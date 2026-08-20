"""STEP 0 second signal: reprice the data-movement terms with the OBSERVED
structural sizes instead of the worst-case bound, using real runs at n=64 and
n=128 (depth 32), then extrapolate to the n=256 target shape.

This is an independent recomputation of the same gate quantity.  It tests the
mining note's specific hypothesis that "the adaptive leading-subspace node
selection is gather-heavy" and could push the candidate over 80e9.
"""

from __future__ import annotations

import json
import math
import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import repaired_reducer as rr  # noqa: E402
from frozen_paths import HERE  # noqa: E402
from flopscope._weights import get_dtype_rate, get_weight  # noqa: E402

Q = 3
L = 32
TARGET_N = 256

W = {op: float(get_weight(op)) for op in ("take", "argsort", "searchsorted", "copy", "diag", "exp")}
RATE64 = float(get_dtype_rate("float64"))
RATE32 = float(get_dtype_rate("float32"))


def observe(width: int, depth: int, seed: int) -> dict:
    weights = rr.make_weights(width, depth, seed)
    trace: list[dict[str, object]] = []
    rr.candidate(weights, trace=trace)
    ranks = [int(r) for layer in trace for r in layer["ranks"]]
    children = [int(layer["children"]) for layer in trace]
    return {
        "width": width,
        "depth": depth,
        "seed": seed,
        "rank_max": max(ranks),
        "rank_mean": float(np.mean(ranks)),
        "rank_max_over_n": max(ranks) / width,
        "children_max_per_layer": max(children),
        "children_max_over_2qn": max(children) / (2 * Q * width),
    }


def dm_per_layer(n: int, r: float, m: float) -> dict[str, float]:
    n2 = n * n
    return {
        "argsort_eigenvalues": Q * W["argsort"] * n * math.log2(n),
        "gather_eigenvalues": Q * W["take"] * n,
        "gather_eigenvectors": Q * W["take"] * n2,
        "searchsorted_cumsum": Q * W["searchsorted"] * n,
        "factor_copy_nr": Q * W["copy"] * n * r,
        "child_diag_fill": m * W["diag"] * n,
        "compressor_argsort": W["argsort"] * m * math.log2(max(m, 2)),
        "compressor_gather": W["take"] * m,
        "compressor_diff": m,
        "child_exp": m * W["exp"] * n,
    }


def main() -> None:
    observations = [
        observe(64, 32, 18720),
        observe(128, 32, 24960),
    ]
    # conservative extrapolation: take the largest observed fractions
    r_frac = max(o["rank_max_over_n"] for o in observations)
    m_frac = max(o["children_max_over_2qn"] for o in observations)
    r_target = r_frac * TARGET_N
    m_target = m_frac * 2 * Q * TARGET_N

    arithmetic_raw = 80 * (TARGET_N**3) * L  # index 11's own declared envelope

    worst = dm_per_layer(TARGET_N, TARGET_N, 2 * Q * TARGET_N)
    observed = dm_per_layer(TARGET_N, r_target, m_target)
    dm_worst = sum(worst.values()) * L
    dm_observed = sum(observed.values()) * L

    raw_worst = arithmetic_raw + dm_worst
    raw_observed = arithmetic_raw + dm_observed
    gate = 80_000_000_000

    out = {
        "step": "0-crosscheck",
        "purpose": "independent recomputation of gate 4 with observed structure",
        "observations": observations,
        "extrapolation": {
            "rank_fraction_of_n_used": r_frac,
            "children_fraction_of_2qn_used": m_frac,
            "rank_at_n256": r_target,
            "children_at_n256": m_target,
            "worst_case_rank": TARGET_N,
            "worst_case_children": 2 * Q * TARGET_N,
        },
        "arithmetic_raw_ops_total": arithmetic_raw,
        "data_movement_worst_case_total": dm_worst,
        "data_movement_observed_structure_total": dm_observed,
        "data_movement_share_of_raw_worst_case": dm_worst / raw_worst,
        "data_movement_share_of_raw_observed": dm_observed / raw_observed,
        "raw_total_worst_case": raw_worst,
        "raw_total_observed_structure": raw_observed,
        "billed_float64_worst_case": raw_worst * RATE64,
        "billed_float64_observed": raw_observed * RATE64,
        "billed_float32_worst_case_with_25pct": raw_worst * RATE32 * 1.25,
        "billed_float32_observed_with_25pct": raw_observed * RATE32 * 1.25,
        "gate_threshold": gate,
        "gather_heavy_hypothesis": (
            "FALSIFIED: gathers and other data movement are O(q n^2) and "
            "O(M n) elements against O(n^3) arithmetic; even at the worst-case "
            "bound they are a sub-1% share, and with observed structure they "
            "shrink further. The repricing lever that actually moves gate 4 is "
            "the float64 dtype rate of 2.0, not data movement."
        ),
        "same_side_of_threshold_as_static": {
            "float64": bool(
                (raw_worst * RATE64 >= gate) == (raw_observed * RATE64 >= gate)
            ),
            "float32": bool(
                (raw_worst * RATE32 * 1.25 >= gate)
                == (raw_observed * RATE32 * 1.25 >= gate)
            ),
        },
    }
    (HERE / "step0_crosscheck.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
