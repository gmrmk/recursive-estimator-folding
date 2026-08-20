"""Frozen diagnostic autopsy for M194_PILOT_SCALING_AUTOPSY.md."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

from run_m194_g0 import M181, N_FRAMES, N_MAIN, PB1, _one_pair

HERE = Path(__file__).resolve().parent
NETS = (101, 202, 303)
PREFIXES = (1, 2, 4, 8, 16, 32, 64, 126)


def main() -> None:
    results: dict[str, dict] = {}
    for prefix in PREFIXES:
        per_net = {}
        net_ratios = []
        oracle_ratios = []
        for net in NETS:
            stacks = np.asarray(
                np.load(PB1 / f"p2_partial_net{net}.npz")["frame_means"],
                dtype=np.float64,
            )
            truth = np.asarray(
                np.load(M181 / f"m181_truth_net{net}.npz")["means"],
                dtype=np.float64,
            )
            base, child, oracle = [], [], []
            for rotation in range(N_MAIN):
                pilot = stacks[rotation + N_MAIN, :prefix].mean(
                    axis=0, dtype=np.float64
                )
                row = _one_pair(stacks[rotation], pilot, truth)
                base.append(row["base_mse"])
                child.append(row["candidate_mse"])
                oracle.append(row["oracle_block_mse"])
            raw_ratio = float(np.mean(child) / np.mean(base))
            oracle_ratio = float(np.mean(oracle) / np.mean(base))
            net_ratios.append(raw_ratio)
            oracle_ratios.append(oracle_ratio)
            per_net[str(net)] = {
                "raw_ratio": raw_ratio,
                "cost_adjusted_ratio": raw_ratio * (N_FRAMES + prefix) / N_FRAMES,
                "oracle_block_ratio": oracle_ratio,
            }
        panel_raw = math.exp(sum(math.log(x) for x in net_ratios) / len(net_ratios))
        panel_oracle = math.exp(
            sum(math.log(x) for x in oracle_ratios) / len(oracle_ratios)
        )
        cost_factor = (N_FRAMES + prefix) / N_FRAMES
        results[str(prefix)] = {
            "per_net": per_net,
            "panel_raw_ratio": panel_raw,
            "panel_cost_adjusted_ratio": panel_raw * cost_factor,
            "panel_oracle_block_ratio": panel_oracle,
            "panel_excess_above_oracle": panel_raw - panel_oracle,
            "cost_factor": cost_factor,
        }
        print(
            f"k={prefix:3d}: raw={panel_raw:.6f} "
            f"cost={panel_raw * cost_factor:.6f} "
            f"oracle={panel_oracle:.6f}"
        )

    x = np.asarray([1.0 / k for k in PREFIXES], dtype=np.float64)
    excess = np.asarray(
        [results[str(k)]["panel_excess_above_oracle"] for k in PREFIXES],
        dtype=np.float64,
    )
    design = np.column_stack((np.ones_like(x), x))
    coef, *_ = np.linalg.lstsq(design, excess, rcond=None)
    fitted = design @ coef
    ss_res = float(np.sum((excess - fitted) ** 2))
    ss_tot = float(np.sum((excess - excess.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else 1.0
    monotone = all(
        results[str(b)]["panel_raw_ratio"] <= results[str(a)]["panel_raw_ratio"]
        for a, b in zip(PREFIXES, PREFIXES[1:])
    )
    payload = {
        "protocol": "M194_PILOT_SCALING_AUTOPSY.md",
        "status": "diagnostic_only_same_cache_no_promotion",
        "prefixes": list(PREFIXES),
        "results": results,
        "fit_excess_equals_intercept_plus_slope_over_k": {
            "intercept": float(coef[0]),
            "slope": float(coef[1]),
            "r2": r2,
        },
        "raw_ratio_monotone_nonincreasing": monotone,
        "any_raw_parity": any(
            results[str(k)]["panel_raw_ratio"] < 1.0 for k in PREFIXES
        ),
        "any_cost_adjusted_parity": any(
            results[str(k)]["panel_cost_adjusted_ratio"] < 1.0
            for k in PREFIXES
        ),
    }
    out = HERE / "m194_pilot_scaling_results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"1/k excess fit R2={r2:.6f}; monotone={monotone}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
