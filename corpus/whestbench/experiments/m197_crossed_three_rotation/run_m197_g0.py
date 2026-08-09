"""M197 cached mechanism falsifier: three-rotation crossed covariance U-stat.

The governing protocol is M197_PREDECLARATION.md.  This runner performs no
network forward and writes only m197_g0_results.json beside itself.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")
sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
PB1 = HERE.parent / "pb1_premise_battery"
M181 = HERE.parent / "m181_terminal_smoothing"
NETS = (101, 202, 303)
TRIPLES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14))
R = 3
K = 42
N_OUTPUTS = 256
N_FOLDS = 8
LAMBDA = 1.0 / 3.0
BOOT_DRAWS = 5000
BOOT_SEED = 20260812


def _crossed_block(
    group: np.ndarray,
    other_mean: np.ndarray,
    train: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return one group's contrast correction and its crossed U-statistic."""
    sample = group[:, train]
    mean = sample.mean(axis=0, dtype=np.float64)
    contrast = sample - mean[None, :]
    count = float(len(train))
    covariance = (contrast @ contrast.T) / count
    covariance = 0.5 * (covariance + covariance.T)
    # h estimates c/R.  The common target mean cancels in mean-other_mean.
    h = (contrast @ (mean - other_mean[train])) / (R * count)
    h -= h.mean()
    tau = float(np.trace(covariance) / (K - 1))
    uniform = np.full(K, 1.0 / (R * K), dtype=np.float64)
    if not np.isfinite(tau) or tau <= 0.0:
        return uniform, h, {"fallback": "uniform_nonpositive_tau", "tau": tau}
    vals, vecs = np.linalg.eigh(covariance)
    denom = np.maximum(vals, 0.0) + LAMBDA * tau
    correction = -(vecs @ ((vecs.T @ h) / denom))
    correction -= correction.mean()
    weights = uniform + correction
    if not np.all(np.isfinite(weights)):
        return uniform, h, {"fallback": "uniform_nonfinite", "tau": tau}
    sum_error = abs(float(correction.sum()))
    if sum_error > 1e-10:
        return uniform, h, {
            "fallback": "uniform_sum_error", "tau": tau,
            "sum_error_before_fallback": sum_error,
        }
    positive = denom[denom > 1e-14 * tau]
    return weights, h, {
        "fallback": None,
        "tau": tau,
        "rank": int((vals > 1e-10 * max(float(vals[-1]), tau)).sum()),
        "condition": float(positive.max() / positive.min()),
        "h_norm": float(np.linalg.norm(h)),
        "correction_norm": float(np.linalg.norm(correction)),
        "group_weight_l1": float(np.abs(weights).sum()),
        "group_max_abs_weight": float(np.abs(weights).max()),
        "sum_error": sum_error,
    }


def _mu_cancellation_check(groups: tuple[np.ndarray, ...], train: np.ndarray) -> float:
    """Check h is invariant when arbitrary unknown means are added to all frames."""
    delta = np.linspace(-0.37, 0.41, N_OUTPUTS, dtype=np.float64)
    shifted = tuple(g + delta[None, :] for g in groups)
    maximum = 0.0
    for r in range(R):
        others = (groups[(r + 1) % R].mean(axis=0, dtype=np.float64)
                  + groups[(r + 2) % R].mean(axis=0, dtype=np.float64)) / 2.0
        shifted_others = (
            shifted[(r + 1) % R].mean(axis=0, dtype=np.float64)
            + shifted[(r + 2) % R].mean(axis=0, dtype=np.float64)
        ) / 2.0
        _, h, _ = _crossed_block(groups[r], others, train)
        _, shifted_h, _ = _crossed_block(shifted[r], shifted_others, train)
        maximum = max(maximum, float(np.max(np.abs(h - shifted_h))))
    return maximum


def _one_triple(groups: tuple[np.ndarray, ...]) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """Construct candidate and equal-three-group predictions without truth."""
    if len(groups) != R or any(g.shape != (K, N_OUTPUTS) for g in groups):
        raise RuntimeError("unexpected M197 group shape")
    output = np.arange(N_OUTPUTS)
    candidate = np.empty(N_OUTPUTS, dtype=np.float64)
    uniform = sum(g.mean(axis=0, dtype=np.float64) for g in groups) / R
    diagnostics = []
    for fold in range(N_FOLDS):
        held = output[output % N_FOLDS == fold]
        train = output[output % N_FOLDS != fold]
        cancellation = _mu_cancellation_check(groups, train)
        if cancellation > 1e-11:
            raise RuntimeError(f"unknown-mu cancellation check failed: {cancellation}")
        weights, group_diags = [], []
        for r in range(R):
            other_mean = (
                groups[(r + 1) % R].mean(axis=0, dtype=np.float64)
                + groups[(r + 2) % R].mean(axis=0, dtype=np.float64)
            ) / 2.0
            weight, _, diag = _crossed_block(groups[r], other_mean, train)
            if diag["fallback"] is not None:
                raise RuntimeError(f"M197 numerical fallback: {diag['fallback']}")
            weights.append(weight)
            group_diags.append(diag)
        combined_sum_error = abs(float(sum(weight.sum() for weight in weights)) - 1.0)
        if combined_sum_error > 1e-10:
            raise RuntimeError(f"combined weights fail sum-one: {combined_sum_error}")
        candidate[held] = sum(
            weights[r] @ groups[r][:, held] for r in range(R)
        )
        diagnostics.append({
            "fold": fold,
            "held": int(len(held)),
            "train": int(len(train)),
            "mu_cancellation_max_abs": cancellation,
            "combined_sum_error": combined_sum_error,
            "groups": group_diags,
        })
    if not np.all(np.isfinite(candidate)):
        raise RuntimeError("nonfinite M197 prediction")
    return candidate, uniform, diagnostics


def _bootstrap(per_net: dict[int, dict]) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    draws = np.empty(BOOT_DRAWS, dtype=np.float64)
    for draw in range(BOOT_DRAWS):
        ratios = []
        for net in NETS:
            base = np.asarray(per_net[net]["base_mse_per_triple"])
            child = np.asarray(per_net[net]["candidate_mse_per_triple"])
            index = rng.integers(0, len(base), len(base))
            ratios.append(float(child[index].mean() / base[index].mean()))
        draws[draw] = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def main() -> None:
    per_net: dict[int, dict] = {}
    all_diags: list[dict] = []
    for net in NETS:
        stacks = np.asarray(
            np.load(PB1 / f"p2_partial_net{net}.npz")["frame_means"],
            dtype=np.float64,
        )
        if stacks.shape != (16, 126, N_OUTPUTS):
            raise RuntimeError(f"net {net}: unexpected cache shape {stacks.shape}")
        rows = []
        candidate_predictions, uniform_predictions, baseline_predictions = [], [], []
        for triple in TRIPLES:
            groups = tuple(stacks[r, :K] for r in triple)
            candidate, uniform, diagnostics = _one_triple(groups)
            candidate_predictions.append(candidate)
            uniform_predictions.append(uniform)
            baseline_predictions.append(stacks[triple[0]].mean(axis=0, dtype=np.float64))
            rows.append({"triple": list(triple), "diagnostics": diagnostics})
            all_diags.extend(d for f in diagnostics for d in f["groups"])

        # Predictions and all truth-free checks above are complete before truth is read.
        truth = np.asarray(np.load(M181 / f"m181_truth_net{net}.npz")["means"], dtype=np.float64)
        candidate_predictions = np.asarray(candidate_predictions)
        uniform_predictions = np.asarray(uniform_predictions)
        baseline_predictions = np.asarray(baseline_predictions)
        base = np.mean((baseline_predictions - truth[None, :]) ** 2, axis=1)
        child = np.mean((candidate_predictions - truth[None, :]) ** 2, axis=1)
        uniform = np.mean((uniform_predictions - truth[None, :]) ** 2, axis=1)
        ratio = float(child.mean() / base.mean())
        uniform_ratio = float(uniform.mean() / base.mean())
        for row, b, c, u in zip(rows, base, child, uniform, strict=True):
            row.update({"primary_base_mse": float(b), "candidate_mse": float(c),
                        "three_group_uniform_mse": float(u)})
        per_net[net] = {
            "base_mse_per_triple": base.tolist(),
            "candidate_mse_per_triple": child.tolist(),
            "three_group_uniform_mse_per_triple": uniform.tolist(),
            "candidate_ratio": ratio,
            "candidate_reduction": 1.0 - ratio,
            "three_group_uniform_ratio": uniform_ratio,
            "primary_rotation_mean_bias2": float(np.mean(
                (baseline_predictions.mean(axis=0) - truth) ** 2
            )),
            "candidate_triple_mean_bias2": float(np.mean(
                (candidate_predictions.mean(axis=0) - truth) ** 2
            )),
            "triple_rows": rows,
        }
        print(f"net {net}: candidate_ratio={ratio:.6f}, three_group_ratio={uniform_ratio:.6f}")

    ratios = [per_net[net]["candidate_ratio"] for net in NETS]
    panel = math.exp(sum(math.log(value) for value in ratios) / len(ratios))
    ci = _bootstrap(per_net)
    any_worse = any(value >= 1.0 for value in ratios)
    every_reduction_20 = all(value <= 0.80 for value in ratios)
    if 1.0 - panel < 0.10 or any_worse or not math.isfinite(panel):
        verdict = "KILLED"
    elif every_reduction_20 and ci[1] < 0.90:
        verdict = "MECHANISTIC_SURVIVOR"
    else:
        verdict = "UNRESOLVED"
    payload = {
        "candidate": "m197_crossed_three_rotation_u_statistic",
        "protocol": "M197_PREDECLARATION.md",
        "status_scope": "same_cache_mechanism_only_no_promotion",
        "triples": [list(triple) for triple in TRIPLES],
        "groups_per_triple": R,
        "frames_per_group": K,
        "total_frames": R * K,
        "lambda": LAMBDA,
        "per_net": {str(key): value for key, value in per_net.items()},
        "panel_ratio_geomean": panel,
        "panel_reduction": 1.0 - panel,
        "bootstrap_95_ratio": ci,
        "weight_diagnostics": {
            "fits": len(all_diags),
            "fallbacks": sum(d["fallback"] is not None for d in all_diags),
            "group_l1_median": float(np.median([d["group_weight_l1"] for d in all_diags])),
            "group_l1_max": float(np.max([d["group_weight_l1"] for d in all_diags])),
            "group_max_abs_median": float(np.median([d["group_max_abs_weight"] for d in all_diags])),
            "group_max_abs_max": float(np.max([d["group_max_abs_weight"] for d in all_diags])),
        },
        "gate": {
            "kill_below_reduction": 0.10,
            "survive_each_net_reduction": 0.20,
            "survive_bootstrap_upper": 0.90,
            "any_net_worse": any_worse,
            "every_net_reduction_20": every_reduction_20,
        },
        "verdict": verdict,
    }
    output = HERE / "m197_g0_results.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"panel ratio={panel:.6f}, bootstrap={ci}, verdict={verdict}")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
