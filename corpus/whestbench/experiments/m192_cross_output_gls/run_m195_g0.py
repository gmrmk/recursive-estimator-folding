"""M195 cached mechanism test: symmetric two-rotation half attenuation."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
PB1 = HERE.parent / "pb1_premise_battery"
M181 = HERE.parent / "m181_terminal_smoothing"
NETS = (101, 202, 303)
N_PAIRS = 8
K = 63
N_OUTPUTS = 256
N_FOLDS = 8
LAMBDA = 1.0 / 3.0
BOOT_DRAWS = 5000
BOOT_SEED = 20260811


def _contrast_correction(group: np.ndarray, difference: np.ndarray,
                         train: np.ndarray, sign: float) -> tuple[np.ndarray, dict]:
    sample = group[:, train]
    center = sample.mean(axis=0, dtype=np.float64)
    contrast = sample - center[None, :]
    count = float(len(train))
    covariance = (contrast @ contrast.T) / count
    covariance = 0.5 * (covariance + covariance.T)
    cross = sign * (contrast @ difference[train]) / (2.0 * count)
    cross -= cross.mean()
    tau = float(np.trace(covariance) / (K - 1))
    if not np.isfinite(tau) or tau <= 0.0:
        return np.zeros(K), {"fallback": "zero_nonpositive_tau", "tau": tau}
    vals, vecs = np.linalg.eigh(covariance)
    denom = np.maximum(vals, 0.0) + LAMBDA * tau
    correction = -(vecs @ ((vecs.T @ cross) / denom))
    correction -= correction.mean()
    if not np.all(np.isfinite(correction)):
        return np.zeros(K), {"fallback": "zero_nonfinite", "tau": tau}
    sum_error = abs(float(correction.sum()))
    if sum_error > 1e-10:
        return np.zeros(K), {"fallback": "zero_sum_error", "tau": tau,
                             "sum_error": sum_error}
    full_weights = np.full(K, 0.5 / K) + correction
    return correction, {
        "fallback": None,
        "tau": tau,
        "rank": int((vals > 1e-10 * max(float(vals[-1]), tau)).sum()),
        "condition": float(denom.max() / denom.min()),
        "cross_norm": float(np.linalg.norm(cross)),
        "correction_norm": float(np.linalg.norm(correction)),
        "group_weight_l1": float(np.abs(full_weights).sum()),
        "group_max_abs_weight": float(np.abs(full_weights).max()),
        "sum_error": sum_error,
    }


def _one_pair(first: np.ndarray, second: np.ndarray, truth: np.ndarray) -> dict:
    outputs = np.arange(N_OUTPUTS)
    prediction = np.empty(N_OUTPUTS, dtype=np.float64)
    diagnostics = []
    mean_first = first.mean(axis=0, dtype=np.float64)
    mean_second = second.mean(axis=0, dtype=np.float64)
    difference = mean_first - mean_second
    for fold in range(N_FOLDS):
        held = outputs[outputs % N_FOLDS == fold]
        train = outputs[outputs % N_FOLDS != fold]
        v_first, d_first = _contrast_correction(
            first, difference, train, +1.0
        )
        v_second, d_second = _contrast_correction(
            second, difference, train, -1.0
        )
        prediction[held] = (
            0.5 * (mean_first[held] + mean_second[held])
            + v_first @ first[:, held]
            + v_second @ second[:, held]
        )
        diagnostics.append({
            "fold": fold,
            "held": len(held),
            "train": len(train),
            "first": d_first,
            "second": d_second,
        })
    primary_baseline = first  # Caller supplies the full main separately.
    del primary_baseline
    half_uniform = 0.5 * (mean_first + mean_second)
    return {
        "prediction": prediction,
        "half_uniform": half_uniform,
        "candidate_mse": float(np.mean((prediction - truth) ** 2)),
        "half_uniform_mse": float(np.mean((half_uniform - truth) ** 2)),
        "diagnostics": diagnostics,
    }


def _bootstrap(per_net: dict[int, dict]) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    draws = np.empty(BOOT_DRAWS)
    for draw in range(BOOT_DRAWS):
        ratios = []
        for net in NETS:
            base = np.asarray(per_net[net]["primary_base_mse_per_pair"])
            child = np.asarray(per_net[net]["candidate_mse_per_pair"])
            idx = rng.integers(0, len(base), len(base))
            ratios.append(float(child[idx].mean() / base[idx].mean()))
        draws[draw] = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    return [float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975))]


def main() -> None:
    per_net: dict[int, dict] = {}
    all_group_diags = []
    for net in NETS:
        stacks = np.asarray(
            np.load(PB1 / f"p2_partial_net{net}.npz")["frame_means"],
            dtype=np.float64,
        )
        truth_data = np.load(M181 / f"m181_truth_net{net}.npz")
        truth = np.asarray(truth_data["means"], dtype=np.float64)
        primary_base, half_base, child = [], [], []
        base_predictions, child_predictions = [], []
        rows = []
        for pair in range(N_PAIRS):
            full_main = stacks[pair]
            first = full_main[:K]
            second = stacks[pair + N_PAIRS, :K]
            row = _one_pair(first, second, truth)
            primary_prediction = full_main.mean(axis=0, dtype=np.float64)
            base_mse = float(np.mean((primary_prediction - truth) ** 2))
            primary_base.append(base_mse)
            half_base.append(row["half_uniform_mse"])
            child.append(row["candidate_mse"])
            base_predictions.append(primary_prediction)
            child_predictions.append(row["prediction"])
            for fold_diag in row["diagnostics"]:
                all_group_diags.extend((fold_diag["first"], fold_diag["second"]))
            row.pop("prediction")
            row.pop("half_uniform")
            row["primary_base_mse"] = base_mse
            rows.append(row)
        primary_base = np.asarray(primary_base)
        half_base = np.asarray(half_base)
        child = np.asarray(child)
        raw_ratio = float(child.mean() / primary_base.mean())
        half_ratio = float(half_base.mean() / primary_base.mean())
        per_net[net] = {
            "primary_base_mse_per_pair": primary_base.tolist(),
            "half_uniform_mse_per_pair": half_base.tolist(),
            "candidate_mse_per_pair": child.tolist(),
            "candidate_ratio": raw_ratio,
            "half_uniform_ratio": half_ratio,
            "candidate_reduction": 1.0 - raw_ratio,
            "primary_rotation_mean_bias2": float(np.mean(
                (np.mean(base_predictions, axis=0) - truth) ** 2
            )),
            "candidate_rotation_mean_bias2": float(np.mean(
                (np.mean(child_predictions, axis=0) - truth) ** 2
            )),
            "truth_noise_floor": float(truth_data["noise_final"]),
            "pair_rows": rows,
        }
        print(
            f"net {net}: candidate_ratio={raw_ratio:.6f}, "
            f"half_uniform_ratio={half_ratio:.6f}"
        )
    net_ratios = [per_net[n]["candidate_ratio"] for n in NETS]
    panel = math.exp(sum(math.log(x) for x in net_ratios) / len(net_ratios))
    ci = _bootstrap(per_net)
    fallbacks = sum(d["fallback"] is not None for d in all_group_diags)
    any_worse = any(x >= 1.0 for x in net_ratios)
    every_reduction_20 = all(x <= 0.80 for x in net_ratios)
    if 1.0 - panel < 0.10 or any_worse or fallbacks or not math.isfinite(panel):
        verdict = "KILLED"
    elif every_reduction_20 and ci[1] < 0.90:
        verdict = "MECHANISTIC_SURVIVOR"
    else:
        verdict = "UNRESOLVED"

    usable = [d for d in all_group_diags if d["fallback"] is None]
    payload = {
        "candidate": "m195_symmetric_two_rotation_half_design_attenuation",
        "protocol": "M195_SYMMETRIC_HALF_PREDECLARATION.md",
        "status_scope": "same_cache_mechanistic_only_no_promotion",
        "pairing": "rotation r first 63 plus rotation r+8 first 63",
        "total_frames": 2 * K,
        "lambda": LAMBDA,
        "per_net": {str(key): value for key, value in per_net.items()},
        "panel_ratio_geomean": panel,
        "panel_reduction": 1.0 - panel,
        "bootstrap_95_ratio": ci,
        "weight_diagnostics": {
            "fits": len(all_group_diags),
            "fallbacks": fallbacks,
            "group_l1_median": float(np.median(
                [d["group_weight_l1"] for d in usable]
            )),
            "group_l1_max": float(np.max(
                [d["group_weight_l1"] for d in usable]
            )),
            "group_max_abs_median": float(np.median(
                [d["group_max_abs_weight"] for d in usable]
            )),
            "group_max_abs_max": float(np.max(
                [d["group_max_abs_weight"] for d in usable]
            )),
        },
        "gate": {
            "kill_below_reduction": 0.10,
            "survive_each_net_reduction": 0.20,
            "survive_bootstrap_upper": 0.90,
            "any_net_worse": any_worse,
            "every_net_reduction_20": every_reduction_20,
            "fallbacks": fallbacks,
        },
        "verdict": verdict,
    }
    out = HERE / "m195_g0_results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"panel ratio={panel:.6f}, bootstrap={ci}, verdict={verdict}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
