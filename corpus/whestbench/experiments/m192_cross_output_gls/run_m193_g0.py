"""M193 cached truth-free falsifier: analytic-anchor frame attenuation."""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")
sys.dont_write_bytecode = True

import numpy as np
from scipy.special import ndtr

from run_m192_g0 import _weights

HERE = Path(__file__).resolve().parent
PB1 = HERE.parent / "pb1_premise_battery"
M181 = HERE.parent / "m181_terminal_smoothing"
NETS = (101, 202, 303)
WIDTH = 256
DEPTH = 32
N_FOLDS = 8
ALPHA = 0.25
BOOT_DRAWS = 5000
BOOT_SEED = 20260809


def he_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def diagonal_anchor(weights: list[np.ndarray]) -> np.ndarray:
    """Plain-numpy mirror of the champion's paid diagonal Gaussian pass."""
    mu = np.zeros(WIDTH, dtype=np.float32)
    var = np.ones(WIDTH, dtype=np.float32)
    for weight in weights:
        mu_pre = mu @ weight
        var_pre = var @ (weight * weight)
        sigma = np.sqrt(np.maximum(var_pre, np.float32(1e-12)))
        alpha = mu_pre / sigma
        phi = np.exp(np.float32(-0.5) * alpha * alpha) / np.float32(
            math.sqrt(2.0 * math.pi)
        )
        cdf = ndtr(alpha).astype(np.float32)
        mu = mu_pre * cdf + sigma * phi
        second = ((var_pre + mu_pre * mu_pre) * cdf
                  + mu_pre * sigma * phi)
        var = np.maximum(second - mu * mu, np.float32(0.0))
    if not np.all(np.isfinite(mu)):
        raise RuntimeError("analytic anchor is nonfinite")
    return mu.astype(np.float64)


def output_folds(final_weight: np.ndarray) -> np.ndarray:
    """Permutation/gauge-invariant fold label from each final output column."""
    labels = np.count_nonzero(final_weight > 0.0, axis=0) % N_FOLDS
    counts = np.bincount(labels, minlength=N_FOLDS)
    if np.any(counts == 0) or np.any(WIDTH - counts < 16):
        raise RuntimeError(f"invalid sign-count fold sizes {counts.tolist()}")
    return labels.astype(np.int64)


def one_rotation(frame_means: np.ndarray, anchor: np.ndarray,
                 labels: np.ndarray) -> tuple[np.ndarray, list[dict]]:
    pred = np.empty(WIDTH, dtype=np.float64)
    diagnostics = []
    outputs = np.arange(WIDTH)
    for fold in range(N_FOLDS):
        held = outputs[labels == fold]
        train = outputs[labels != fold]
        residual = frame_means[:, train] - anchor[train][None, :]
        second_moment = (residual @ residual.T) / len(train)
        w, diag = _weights(second_moment, ALPHA)
        pred[held] = w @ frame_means[:, held]
        diagnostics.append({
            "fold": fold,
            "held": int(len(held)),
            "train": int(len(train)),
            "l1_weight": float(np.abs(w).sum()),
            "max_abs_weight": float(np.abs(w).max()),
            **diag,
        })
    if not np.all(np.isfinite(pred)):
        raise RuntimeError("M193 prediction is nonfinite")
    return pred, diagnostics


def bootstrap(per_net: dict[int, dict]) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    draws = np.empty(BOOT_DRAWS)
    for b in range(BOOT_DRAWS):
        rs = []
        for net in NETS:
            base = np.asarray(per_net[net]["base_mse_per_rotation"])
            child = np.asarray(per_net[net]["m193_mse_per_rotation"])
            idx = rng.integers(0, len(base), len(base))
            rs.append(float(child[idx].mean() / base[idx].mean()))
        draws[b] = math.exp(sum(math.log(x) for x in rs) / len(rs))
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def main() -> None:
    p2 = json.loads((PB1 / "p2_results.json").read_text(encoding="utf-8"))
    per_net: dict[int, dict] = {}
    all_l1, all_maxw, all_rank, all_cond = [], [], [], []
    for net in NETS:
        weights = he_weights(net)
        anchor = diagonal_anchor(weights)
        labels = output_folds(weights[-1])
        stacks = np.asarray(
            np.load(PB1 / f"p2_partial_net{net}.npz")["frame_means"],
            dtype=np.float64,
        )
        truth_data = np.load(M181 / f"m181_truth_net{net}.npz")
        truth = np.asarray(truth_data["means"], dtype=np.float64)
        # Truth is first touched for scoring after anchor, labels, and all
        # truth-free operator definitions have been frozen above.
        preds, base_preds, rotation_diags = [], [], []
        for frame_means in stacks:
            child, diags = one_rotation(frame_means, anchor, labels)
            preds.append(child)
            base_preds.append(frame_means.mean(axis=0, dtype=np.float64))
            rotation_diags.append(diags)
            for d in diags:
                all_l1.append(d["l1_weight"])
                all_maxw.append(d["max_abs_weight"])
                all_rank.append(d["rank"])
                all_cond.append(d["condition"])
        preds = np.asarray(preds)
        base_preds = np.asarray(base_preds)
        base_mse = np.mean((base_preds - truth[None, :]) ** 2, axis=1)
        child_mse = np.mean((preds - truth[None, :]) ** 2, axis=1)
        archived = np.asarray(
            p2["q1_oracle_headroom"]["per_net"][str(net)]["mse_per_rotation"]
        )
        max_crosscheck = float(np.max(np.abs(base_mse - archived)))
        if max_crosscheck > 1e-18:
            raise RuntimeError(f"net {net} P2 baseline mismatch {max_crosscheck}")
        ratio = float(child_mse.mean() / base_mse.mean())
        base_bias2 = float(np.mean((base_preds.mean(axis=0) - truth) ** 2))
        child_bias2 = float(np.mean((preds.mean(axis=0) - truth) ** 2))
        per_net[net] = {
            "fold_sizes": np.bincount(labels, minlength=N_FOLDS).tolist(),
            "anchor_mse": float(np.mean((anchor - truth) ** 2)),
            "base_mse_per_rotation": base_mse.tolist(),
            "m193_mse_per_rotation": child_mse.tolist(),
            "ratio_of_rotation_means": ratio,
            "reduction": 1.0 - ratio,
            "base_rotation_mean_bias2": base_bias2,
            "m193_rotation_mean_bias2": child_bias2,
            "max_p2_baseline_crosscheck": max_crosscheck,
            "rotation_diagnostics": rotation_diags,
        }
        print(
            f"net {net}: anchor_mse={per_net[net]['anchor_mse']:.3e}, "
            f"ratio={ratio:.6f}, reduction={100*(1-ratio):+.2f}%"
        )

    ratios = [per_net[n]["ratio_of_rotation_means"] for n in NETS]
    panel = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    reduction = 1.0 - panel
    ci = bootstrap(per_net)
    any_worse = any(x >= 1.0 for x in ratios)
    if reduction < 0.10 or any_worse:
        verdict = "KILLED"
    elif reduction >= 0.20 and ci[1] < 0.90:
        verdict = "SCREEN_SURVIVOR"
    else:
        verdict = "UNRESOLVED"
    payload = {
        "candidate": "m193_truth_free_analytic_anchor_frame_attenuation",
        "protocol": "M193_ANCHOR_PREDECLARATION.md",
        "parent": "m192_cross_output_frame_covariance_gls",
        "alpha_frozen_from_parent": ALPHA,
        "fold_rule": "count_positive_final_column mod 8",
        "firewall": "cached synthetic P2 frames; truth read only for final scoring; no forward/submission",
        "per_net": {str(k): v for k, v in per_net.items()},
        "panel_ratio_geomean": panel,
        "panel_reduction": reduction,
        "bootstrap_95_ratio": ci,
        "weight_diagnostics": {
            "l1_median": float(np.median(all_l1)),
            "l1_max": float(np.max(all_l1)),
            "max_abs_weight_median": float(np.median(all_maxw)),
            "max_abs_weight_max": float(np.max(all_maxw)),
            "rank_median": float(np.median(all_rank)),
            "condition_median": float(np.median(all_cond)),
            "condition_max": float(np.max(all_cond)),
        },
        "gate": {
            "kill_below_reduction": 0.10,
            "survive_at_reduction": 0.20,
            "any_net_worse": any_worse,
            "bootstrap_upper_below": 0.90,
        },
        "verdict": verdict,
    }
    out = HERE / "m193_g0_results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"panel ratio={panel:.6f}, reduction={100*reduction:+.2f}%")
    print(f"bootstrap 95% ratio={ci}")
    print(f"verdict={verdict}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
