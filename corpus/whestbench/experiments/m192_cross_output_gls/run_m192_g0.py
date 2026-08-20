"""M192 cached oracle falsifier: cross-output frame-covariance GLS.

The governing protocol is M192_PREDECLARATION.md.  This script performs no
network forward and writes only m192_g0_results.json beside itself.
"""
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

HERE = Path(__file__).resolve().parent
PB1 = HERE.parent / "pb1_premise_battery"
M181 = HERE.parent / "m181_terminal_smoothing"
NETS = (101, 202, 303)
N_OUTER = 8
N_INNER = 4
ALPHAS = (0.0, 0.25, 0.5, 0.75, 0.9, 0.99)
BOOT_DRAWS = 5000
BOOT_SEED = 20260808


def _weights(second_moment: np.ndarray, alpha: float) -> tuple[np.ndarray, dict]:
    """Sum-one GLS weights from a shrunk symmetric second moment."""
    c = np.asarray(second_moment, dtype=np.float64)
    c = 0.5 * (c + c.T)
    p = c.shape[0]
    vals, vecs = np.linalg.eigh(c)
    tau = float(np.trace(c) / p)
    if not np.isfinite(tau) or tau <= 0.0:
        return np.full(p, 1.0 / p), {
            "tau": tau, "rank": 0, "condition": 1.0, "fallback": "uniform"
        }
    denom = (1.0 - alpha) * vals + alpha * tau
    if alpha == 0.0:
        cutoff = 1e-10 * max(float(vals[-1]), tau)
        inv = np.where(denom > cutoff, 1.0 / denom, 0.0)
    else:
        inv = 1.0 / denom
    one_coords = vecs.T @ np.ones(p, dtype=np.float64)
    x = vecs @ (inv * one_coords)
    normalizer = float(x.sum())
    if not np.isfinite(normalizer) or abs(normalizer) < 1e-14:
        raise RuntimeError("GLS normalization is singular")
    w = x / normalizer
    if not np.all(np.isfinite(w)):
        raise RuntimeError("nonfinite GLS weight")
    if abs(float(w.sum()) - 1.0) > 1e-10:
        raise RuntimeError("GLS weights do not sum to one")
    positive = denom[denom > max(1e-14 * tau, 0.0)]
    condition = float(positive.max() / positive.min()) if positive.size else math.inf
    return w, {
        "tau": tau,
        "rank": int((vals > 1e-10 * max(float(vals[-1]), tau)).sum()),
        "condition": condition,
        "fallback": None,
    }


def _second_moment(frame_means: np.ndarray, truth: np.ndarray,
                   outputs: np.ndarray) -> np.ndarray:
    err = frame_means[:, outputs] - truth[outputs][None, :]
    return (err @ err.T) / float(len(outputs))


def _choose_alpha(frame_means: np.ndarray, truth: np.ndarray,
                  outer_train: np.ndarray) -> tuple[float, dict]:
    """Four-fold inner truth oracle, confined to the outer training outputs."""
    losses = {a: 0.0 for a in ALPHAS}
    counts = {a: 0 for a in ALPHAS}
    for inner in range(N_INNER):
        held = outer_train[np.arange(len(outer_train)) % N_INNER == inner]
        train = outer_train[np.arange(len(outer_train)) % N_INNER != inner]
        c = _second_moment(frame_means, truth, train)
        for alpha in ALPHAS:
            w, _ = _weights(c, alpha)
            pred = w @ frame_means[:, held]
            diff = pred - truth[held]
            losses[alpha] += float(diff @ diff)
            counts[alpha] += len(held)
    means = {a: losses[a] / counts[a] for a in ALPHAS}
    # Exact protocol tie break: larger alpha wins a numerical tie.
    chosen = min(ALPHAS, key=lambda a: (means[a], -a))
    return float(chosen), {str(a): float(means[a]) for a in ALPHAS}


def _one_rotation(frame_means: np.ndarray, truth: np.ndarray) -> dict:
    p, q = frame_means.shape
    if (p, q) != (126, 256):
        raise RuntimeError(f"unexpected frame matrix shape {(p, q)}")
    uniform = frame_means.mean(axis=0, dtype=np.float64)
    corrected = np.empty(q, dtype=np.float64)
    selected: list[float] = []
    diagnostics = []
    all_outputs = np.arange(q)
    for fold in range(N_OUTER):
        held = all_outputs[all_outputs % N_OUTER == fold]
        train = all_outputs[all_outputs % N_OUTER != fold]
        alpha, inner_losses = _choose_alpha(frame_means, truth, train)
        c = _second_moment(frame_means, truth, train)
        w, diag = _weights(c, alpha)
        corrected[held] = w @ frame_means[:, held]
        selected.append(alpha)
        diagnostics.append({
            "fold": fold,
            "alpha": alpha,
            "inner_losses": inner_losses,
            "l1_weight": float(np.abs(w).sum()),
            "max_abs_weight": float(np.abs(w).max()),
            **diag,
        })
    base_mse = float(np.mean((uniform - truth) ** 2))
    gls_mse = float(np.mean((corrected - truth) ** 2))
    return {
        "base_mse": base_mse,
        "gls_mse": gls_mse,
        "ratio": gls_mse / base_mse,
        "selected_alpha": selected,
        "diagnostics": diagnostics,
    }


def _bootstrap(per_net: dict[int, dict]) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    ratios = np.empty(BOOT_DRAWS, dtype=np.float64)
    for b in range(BOOT_DRAWS):
        net_ratios = []
        for net in NETS:
            base = np.asarray(per_net[net]["base_mse_per_rotation"])
            gls = np.asarray(per_net[net]["gls_mse_per_rotation"])
            idx = rng.integers(0, len(base), len(base))
            net_ratios.append(float(gls[idx].mean() / base[idx].mean()))
        ratios[b] = math.exp(sum(math.log(x) for x in net_ratios) / len(net_ratios))
    return [float(np.quantile(ratios, 0.025)), float(np.quantile(ratios, 0.975))]


def main() -> None:
    p2 = json.loads((PB1 / "p2_results.json").read_text(encoding="utf-8"))
    per_net: dict[int, dict] = {}
    alpha_counter: Counter[str] = Counter()
    all_l1, all_maxw, all_rank, all_condition = [], [], [], []
    for net in NETS:
        cache = np.load(PB1 / f"p2_partial_net{net}.npz")
        stacks = np.asarray(cache["frame_means"], dtype=np.float64)
        truth_file = np.load(M181 / f"m181_truth_net{net}.npz")
        truth = np.asarray(truth_file["means"], dtype=np.float64)
        rows = []
        for rotation in range(stacks.shape[0]):
            result = _one_rotation(stacks[rotation], truth)
            rows.append(result)
            for alpha in result["selected_alpha"]:
                alpha_counter[str(alpha)] += 1
            for diag in result["diagnostics"]:
                all_l1.append(diag["l1_weight"])
                all_maxw.append(diag["max_abs_weight"])
                all_rank.append(diag["rank"])
                all_condition.append(diag["condition"])
        base = np.array([r["base_mse"] for r in rows])
        gls = np.array([r["gls_mse"] for r in rows])
        archived = np.asarray(
            p2["q1_oracle_headroom"]["per_net"][str(net)]["mse_per_rotation"],
            dtype=np.float64,
        )
        max_crosscheck = float(np.max(np.abs(base - archived)))
        if max_crosscheck > 1e-18:
            raise RuntimeError(
                f"net {net} baseline does not reproduce P2 archive: {max_crosscheck}"
            )
        ratio = float(gls.mean() / base.mean())
        per_net[net] = {
            "base_mse_per_rotation": base.tolist(),
            "gls_mse_per_rotation": gls.tolist(),
            "ratio_of_rotation_means": ratio,
            "reduction": 1.0 - ratio,
            "max_p2_baseline_crosscheck": max_crosscheck,
            "rotation_rows": rows,
        }
        print(f"net {net}: ratio={ratio:.6f}, reduction={100*(1-ratio):+.2f}%")

    net_ratios = [per_net[n]["ratio_of_rotation_means"] for n in NETS]
    panel_ratio = math.exp(sum(math.log(x) for x in net_ratios) / len(net_ratios))
    reduction = 1.0 - panel_ratio
    any_worse_5 = any(x > 1.05 for x in net_ratios)
    if reduction < 0.10 or any_worse_5:
        verdict = "KILLED"
    elif reduction >= 0.15 and all(x < 1.0 for x in net_ratios):
        verdict = "SCREEN_SURVIVOR"
    else:
        verdict = "UNRESOLVED"
    payload = {
        "candidate": "m192_cross_output_frame_covariance_gls",
        "protocol": "M192_PREDECLARATION.md",
        "firewall": "cached synthetic-only P2 frame matrices and M181 truths; no forward or submission",
        "alphas": list(ALPHAS),
        "outer_folds": N_OUTER,
        "inner_folds": N_INNER,
        "per_net": {str(k): v for k, v in per_net.items()},
        "panel_ratio_geomean": panel_ratio,
        "panel_reduction": reduction,
        "bootstrap_95_ratio": _bootstrap(per_net),
        "selected_alpha_counts": dict(alpha_counter),
        "weight_diagnostics": {
            "l1_median": float(np.median(all_l1)),
            "l1_max": float(np.max(all_l1)),
            "max_abs_weight_median": float(np.median(all_maxw)),
            "max_abs_weight_max": float(np.max(all_maxw)),
            "rank_median": float(np.median(all_rank)),
            "condition_median": float(np.median(all_condition)),
            "condition_max": float(np.max(all_condition)),
        },
        "gate": {
            "kill_below_reduction": 0.10,
            "survive_at_reduction": 0.15,
            "any_net_worse_5_percent": any_worse_5,
        },
        "verdict": verdict,
    }
    out = HERE / "m192_g0_results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"panel ratio={panel_ratio:.6f}, reduction={100*reduction:+.2f}%")
    print(f"bootstrap 95% ratio={payload['bootstrap_95_ratio']}")
    print(f"verdict={verdict}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
