"""M194 cached falsifier: independent-pilot projected block GLS.

The governing protocol is M194_PILOT_BLOCK_PREDECLARATION.md.  The runner
performs no network forward and writes only m194_g0_results.json beside itself.
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
N_MAIN = 8
N_FRAMES = 126
N_PILOT_FRAMES = 8
N_OUTPUTS = 256
N_FOLDS = 8
LAMBDA = 1.0 / 3.0
COST_FACTOR = (N_FRAMES + N_PILOT_FRAMES) / N_FRAMES
BOOT_DRAWS = 5000
BOOT_SEED = 20260810


def _block_weights(frame_means: np.ndarray, anchor: np.ndarray,
                   train: np.ndarray) -> tuple[np.ndarray, dict]:
    """Projected covariance blocks; common anchor noise is annihilated."""
    residual = frame_means[:, train] - anchor[train][None, :]
    common = residual.mean(axis=0, dtype=np.float64)
    contrast = residual - common[None, :]
    count = float(len(train))
    block = (contrast @ contrast.T) / count
    block = 0.5 * (block + block.T)
    cross = (contrast @ common) / count
    cross -= cross.mean()
    tau_z = float(np.trace(block) / (N_FRAMES - 1))
    uniform = np.full(N_FRAMES, 1.0 / N_FRAMES, dtype=np.float64)
    if not np.isfinite(tau_z) or tau_z <= 0.0:
        return uniform, {
            "tau_z": tau_z,
            "rank": 0,
            "condition": 1.0,
            "fallback": "uniform_nonpositive_tau",
            "cross_norm": float(np.linalg.norm(cross)),
        }
    vals, vecs = np.linalg.eigh(block)
    # On the contrast subspace this is exactly A + lambda*tau_z*P.  The
    # all-ones coordinate of cross is explicitly zero, so adding the same
    # ridge in that unused coordinate changes no mathematical solution.
    denom = np.maximum(vals, 0.0) + LAMBDA * tau_z
    correction = -(vecs @ ((vecs.T @ cross) / denom))
    correction -= correction.mean()
    weights = uniform + correction
    if not np.all(np.isfinite(weights)):
        return uniform, {
            "tau_z": tau_z,
            "rank": 0,
            "condition": math.inf,
            "fallback": "uniform_nonfinite_weight",
            "cross_norm": float(np.linalg.norm(cross)),
        }
    sum_error = abs(float(weights.sum()) - 1.0)
    if sum_error > 1e-10:
        return uniform, {
            "tau_z": tau_z,
            "rank": 0,
            "condition": math.inf,
            "fallback": "uniform_sum_error",
            "cross_norm": float(np.linalg.norm(cross)),
            "sum_error_before_fallback": sum_error,
        }
    positive = denom[denom > 1e-14 * tau_z]
    condition = (float(positive.max() / positive.min())
                 if positive.size else math.inf)
    rank = int((vals > 1e-10 * max(float(vals[-1]), tau_z)).sum())
    return weights, {
        "tau_z": tau_z,
        "rank": rank,
        "condition": condition,
        "fallback": None,
        "cross_norm": float(np.linalg.norm(cross)),
        "l1_weight": float(np.abs(weights).sum()),
        "max_abs_weight": float(np.abs(weights).max()),
        "correction_norm": float(np.linalg.norm(correction)),
        "sum_error": sum_error,
    }


def _one_pair(main: np.ndarray, pilot: np.ndarray,
              truth: np.ndarray) -> dict:
    if main.shape != (N_FRAMES, N_OUTPUTS):
        raise RuntimeError(f"unexpected main shape {main.shape}")
    if pilot.shape != (N_OUTPUTS,):
        raise RuntimeError(f"unexpected pilot shape {pilot.shape}")
    outputs = np.arange(N_OUTPUTS)
    candidate = np.empty(N_OUTPUTS, dtype=np.float64)
    oracle = np.empty(N_OUTPUTS, dtype=np.float64)
    diagnostics = []
    oracle_diagnostics = []
    for fold in range(N_FOLDS):
        held = outputs[outputs % N_FOLDS == fold]
        train = outputs[outputs % N_FOLDS != fold]
        weights, diag = _block_weights(main, pilot, train)
        oracle_weights, oracle_diag = _block_weights(main, truth, train)
        candidate[held] = weights @ main[:, held]
        oracle[held] = oracle_weights @ main[:, held]
        diagnostics.append({"fold": fold, "held": len(held),
                            "train": len(train), **diag})
        oracle_diagnostics.append({"fold": fold, **oracle_diag})
    baseline = main.mean(axis=0, dtype=np.float64)
    base_mse = float(np.mean((baseline - truth) ** 2))
    candidate_mse = float(np.mean((candidate - truth) ** 2))
    oracle_mse = float(np.mean((oracle - truth) ** 2))
    return {
        "base_mse": base_mse,
        "candidate_mse": candidate_mse,
        "oracle_block_mse": oracle_mse,
        "raw_ratio": candidate_mse / base_mse,
        "cost_adjusted_ratio": COST_FACTOR * candidate_mse / base_mse,
        "oracle_block_ratio": oracle_mse / base_mse,
        "baseline_prediction": baseline,
        "candidate_prediction": candidate,
        "diagnostics": diagnostics,
        "oracle_diagnostics": oracle_diagnostics,
    }


def _bootstrap(per_net: dict[int, dict]) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    draws = np.empty(BOOT_DRAWS, dtype=np.float64)
    for draw in range(BOOT_DRAWS):
        net_ratios = []
        for net in NETS:
            base = np.asarray(per_net[net]["base_mse_per_pair"])
            child = np.asarray(per_net[net]["candidate_mse_per_pair"])
            idx = rng.integers(0, len(base), len(base))
            net_ratios.append(float(child[idx].mean() / base[idx].mean()))
        draws[draw] = COST_FACTOR * math.exp(
            sum(math.log(x) for x in net_ratios) / len(net_ratios)
        )
    return [float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975))]


def main() -> None:
    per_net: dict[int, dict] = {}
    all_diags: list[dict] = []
    all_oracle_diags: list[dict] = []
    for net in NETS:
        stacks = np.asarray(
            np.load(PB1 / f"p2_partial_net{net}.npz")["frame_means"],
            dtype=np.float64,
        )
        truth_data = np.load(M181 / f"m181_truth_net{net}.npz")
        truth = np.asarray(truth_data["means"], dtype=np.float64)
        if stacks.shape != (16, N_FRAMES, N_OUTPUTS):
            raise RuntimeError(f"net {net}: unexpected cache {stacks.shape}")
        rows = []
        for rotation in range(N_MAIN):
            pilot = stacks[rotation + N_MAIN, :N_PILOT_FRAMES].mean(
                axis=0, dtype=np.float64
            )
            row = _one_pair(stacks[rotation], pilot, truth)
            rows.append(row)
            all_diags.extend(row["diagnostics"])
            all_oracle_diags.extend(row["oracle_diagnostics"])
        base = np.asarray([row["base_mse"] for row in rows])
        child = np.asarray([row["candidate_mse"] for row in rows])
        oracle = np.asarray([row["oracle_block_mse"] for row in rows])
        base_predictions = np.asarray(
            [row.pop("baseline_prediction") for row in rows]
        )
        child_predictions = np.asarray(
            [row.pop("candidate_prediction") for row in rows]
        )
        raw_ratio = float(child.mean() / base.mean())
        oracle_ratio = float(oracle.mean() / base.mean())
        per_net[net] = {
            "base_mse_per_pair": base.tolist(),
            "candidate_mse_per_pair": child.tolist(),
            "oracle_block_mse_per_pair": oracle.tolist(),
            "raw_ratio_of_pair_means": raw_ratio,
            "cost_adjusted_ratio": COST_FACTOR * raw_ratio,
            "raw_reduction": 1.0 - raw_ratio,
            "oracle_block_ratio": oracle_ratio,
            "baseline_rotation_mean_bias2": float(np.mean(
                (base_predictions.mean(axis=0) - truth) ** 2
            )),
            "candidate_rotation_mean_bias2": float(np.mean(
                (child_predictions.mean(axis=0) - truth) ** 2
            )),
            "truth_noise_floor": float(truth_data["noise_final"]),
            "pair_rows": rows,
        }
        print(
            f"net {net}: raw_ratio={raw_ratio:.6f}, "
            f"cost_ratio={COST_FACTOR * raw_ratio:.6f}, "
            f"oracle_block_ratio={oracle_ratio:.6f}"
        )

    raw_ratios = [per_net[n]["raw_ratio_of_pair_means"] for n in NETS]
    panel_raw = math.exp(sum(math.log(x) for x in raw_ratios) / len(raw_ratios))
    panel_cost = COST_FACTOR * panel_raw
    ci = _bootstrap(per_net)
    fallbacks = sum(d["fallback"] is not None for d in all_diags)
    any_worse = any(x >= 1.0 for x in raw_ratios)
    every_reduction_20 = all(x <= 0.80 for x in raw_ratios)
    if (1.0 - panel_raw < 0.10 or any_worse or fallbacks or
            not math.isfinite(panel_raw)):
        verdict = "KILLED"
    elif (every_reduction_20 and 1.0 - panel_cost >= 0.15 and ci[1] < 0.90):
        verdict = "SCREEN_SURVIVOR"
    else:
        verdict = "UNRESOLVED"

    def aggregate(diags: list[dict]) -> dict:
        usable = [d for d in diags if d["fallback"] is None]
        return {
            "fits": len(diags),
            "fallbacks": len(diags) - len(usable),
            "l1_median": float(np.median([d["l1_weight"] for d in usable])),
            "l1_max": float(np.max([d["l1_weight"] for d in usable])),
            "max_abs_median": float(np.median(
                [d["max_abs_weight"] for d in usable]
            )),
            "max_abs_max": float(np.max(
                [d["max_abs_weight"] for d in usable]
            )),
            "condition_median": float(np.median(
                [d["condition"] for d in usable]
            )),
            "condition_max": float(np.max(
                [d["condition"] for d in usable]
            )),
        }

    payload = {
        "candidate": "m194_independent_pilot_projected_block_gls",
        "protocol": "M194_PILOT_BLOCK_PREDECLARATION.md",
        "parent": "m192_oracle_survivor_x_m193_first_break",
        "firewall": (
            "cached synthetic P2 frames and M181 truth; truth used only for "
            "scoring and frozen oracle diagnostic; no forward/submission"
        ),
        "pairing": "main rotations 0..7; independent pilot r+8",
        "pilot_frames": N_PILOT_FRAMES,
        "lambda": LAMBDA,
        "cost_factor_conservative": COST_FACTOR,
        "per_net": {str(key): value for key, value in per_net.items()},
        "panel_raw_ratio_geomean": panel_raw,
        "panel_raw_reduction": 1.0 - panel_raw,
        "panel_cost_adjusted_ratio": panel_cost,
        "panel_cost_adjusted_reduction": 1.0 - panel_cost,
        "bootstrap_95_cost_adjusted_ratio": ci,
        "weight_diagnostics": aggregate(all_diags),
        "oracle_weight_diagnostics": aggregate(all_oracle_diags),
        "gate": {
            "kill_below_raw_reduction": 0.10,
            "survive_each_net_raw_reduction": 0.20,
            "survive_panel_cost_adjusted_reduction": 0.15,
            "survive_bootstrap_upper": 0.90,
            "any_net_worse": any_worse,
            "every_net_reduction_20": every_reduction_20,
            "fallbacks": fallbacks,
        },
        "verdict": verdict,
    }
    out = HERE / "m194_g0_results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"panel raw ratio={panel_raw:.6f}")
    print(f"panel cost-adjusted ratio={panel_cost:.6f}")
    print(f"bootstrap 95% cost-adjusted ratio={ci}")
    print(f"verdict={verdict}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
