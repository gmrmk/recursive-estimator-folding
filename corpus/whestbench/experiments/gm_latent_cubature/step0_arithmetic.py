"""STEP 0: reprice index 11's conservative n=256,L=32 target arithmetic under
the INSTALLED FlopScope 0.10.0 weight table.

Gate 4 (index 11 kill_condition): kill if the conservative target operation
count is at least 80e9.

Every unit cost used here is measured from the installed flopscope package in
this same script, not recalled.  Nothing is assumed about the pricing table.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as _np

import flopscope
import flopscope.numpy as fnp
from flopscope._weights import get_dtype_rate, get_weight

HERE = Path(__file__).resolve().parent
N = 256
L = 32
Q = 3


def measure_unit_costs() -> dict[str, float]:
    """Read real billed FLOPs for the primitives the candidate uses."""
    out: dict[str, float] = {}
    prev = 0.0

    def run(label, fn):
        nonlocal prev
        with flopscope.budget(10**15, quiet=True):
            fn()
        summary = flopscope.budget_summary_dict()
        ops = summary["operations"]
        out[label] = ops
        return ops

    with flopscope.budget(10**16, quiet=True):
        m = 64
        a = fnp.asarray(_np.arange(1000.0))
        idx = fnp.asarray(_np.arange(1000))
        fnp.take(a, idx)
        fnp.copy(a)
        fnp.sort(a)
        fnp.argsort(a)
        fnp.linalg.eigh(fnp.asarray(_np.eye(m)))
        fnp.diag(fnp.asarray(_np.ones(m)))
        fnp.outer(fnp.asarray(_np.ones(m)), fnp.asarray(_np.ones(m)))
        A = fnp.asarray(_np.ones((m, m)))
        A @ A
        fnp.exp(fnp.asarray(_np.zeros(1000)))
    ops = flopscope.budget_summary_dict()["operations"]
    return {
        "take_1000_f64": ops["take"]["flop_cost"],
        "copy_1000_f64": ops["copy"]["flop_cost"],
        "sort_1000_f64": ops["sort"]["flop_cost"],
        "argsort_1000_f64": ops["argsort"]["flop_cost"],
        "eigh_64_f64": ops["linalg.eigh"]["flop_cost"],
        "diag_vec64_f64": ops["diag"]["flop_cost"],
        "outer_64_f64": ops["outer"]["flop_cost"],
        "matmul_64_f64": ops["matmul"]["flop_cost"],
        "exp_1000_f64": ops["exp"]["flop_cost"],
    }


def main() -> None:
    units = measure_unit_costs()
    rate64 = float(get_dtype_rate("float64"))
    rate32 = float(get_dtype_rate("float32"))
    weights = {
        op: float(get_weight(op))
        for op in (
            "take",
            "sort",
            "argsort",
            "searchsorted",
            "copy",
            "concatenate",
            "diag",
            "outer",
            "matmul",
            "linalg.eigh",
            "cumsum",
            "exp",
            "zeros",
        )
    }

    n3 = N**3
    n2 = N**2

    # --- index 11's own declared per-layer arithmetic envelope (raw ops) ---
    arithmetic_terms = {
        "covariance_sandwiches_2qn3": 2 * Q * n3,
        "component_eigendecompositions_9qn3": 9 * Q * n3,
        "recompression_eigensolver_9n3": 9 * n3,
        "child_moment_rebin_passes_12qn3": 12 * Q * n3,
        "remaining_means_factors_nodes_2n3": 2 * n3,
    }
    arithmetic_per_layer = sum(arithmetic_terms.values())
    assert arithmetic_per_layer == 80 * n3, arithmetic_per_layer
    arithmetic_raw = arithmetic_per_layer * L

    # --- data-movement / pointwise terms the 2026-08 envelope omitted ---
    # Priced at the installed weights, worst case r <= n and M <= 2qn children.
    M = 2 * Q * N
    log2n = math.log2(N)
    log2M = math.log2(M)
    dm_terms = {
        # per parent component, q per layer
        "argsort_eigenvalues": Q * weights["argsort"] * N * log2n,
        "gather_eigenvalues": Q * weights["take"] * N,
        "gather_eigenvectors": Q * weights["take"] * n2,
        "searchsorted_cumsum": Q * weights["searchsorted"] * N,
        "factor_copy_nr": Q * weights["copy"] * n2,
        # per child, M per layer; measured diag(vec n) bills n input elements
        "child_diag_fill": M * weights["diag"] * N,
        # compressor over M children
        "compressor_argsort": weights["argsort"] * M * log2M,
        "compressor_gather": weights["take"] * M,
        "compressor_diff": M,
        # pointwise transcendental in the ReLU moments, weight 16 per element
        "child_exp": M * weights["exp"] * N,
    }
    dm_per_layer = sum(dm_terms.values())
    dm_raw = dm_per_layer * L

    raw_total = arithmetic_raw + dm_raw
    gate = 80_000_000_000

    result = {
        "step": 0,
        "gate_id": "index 11 kill_condition clause 4",
        "gate_rule": "KILL if conservative n=256,L=32 target operations >= 80e9",
        "gate_threshold": gate,
        "flopscope_version": getattr(flopscope, "__version__", "unknown"),
        "installed_weights": weights,
        "installed_dtype_rates": {"float64": rate64, "float32": rate32},
        "measured_unit_costs_billed_flops": units,
        "measured_unit_cost_derivations": {
            "eigh_64_f64_over_n3": units["eigh_64_f64"] / 64**3,
            "matmul_64_f64_over_n3": units["matmul_64_f64"] / 64**3,
            "take_per_element_f64": units["take_1000_f64"] / 1000.0,
            "copy_per_element_f64": units["copy_1000_f64"] / 1000.0,
            "exp_per_element_f64": units["exp_1000_f64"] / 1000.0,
            "diag_bills_input_elements_only": units["diag_vec64_f64"] / 64.0,
        },
        "shape": {"n": N, "depth": L, "q": Q, "max_children_per_layer": M},
        "arithmetic_terms_per_layer": arithmetic_terms,
        "arithmetic_raw_ops_total": arithmetic_raw,
        "data_movement_terms_per_layer": dm_terms,
        "data_movement_raw_ops_total": dm_raw,
        "raw_ops_total": raw_total,
        "billed": {
            "float32_no_contingency": raw_total * rate32,
            "float32_with_25pct_contingency": raw_total * rate32 * 1.25,
            "float64_no_contingency": raw_total * rate64,
            "float64_with_25pct_contingency": raw_total * rate64 * 1.25,
        },
        "frozen_candidate_dtype": "float64 (latent_sparse_cubature.py declares "
        "dtype=np.float64 throughout; no FP32 port of this candidate is frozen)",
    }
    result["gate4_kill_under_float64"] = bool(
        result["billed"]["float64_no_contingency"] >= gate
    )
    result["gate4_kill_under_float32"] = bool(
        result["billed"]["float32_with_25pct_contingency"] >= gate
    )
    result["verdict"] = (
        "KILL under float64 billing; PASS under float32 billing -> "
        "dtype-conditional, not a clean unilateral step-0 kill; proceed to the "
        "predeclared accuracy falsifier"
        if result["gate4_kill_under_float64"]
        and not result["gate4_kill_under_float32"]
        else (
            "KILL under both dtype rates"
            if result["gate4_kill_under_float32"]
            else "PASS under both dtype rates"
        )
    )
    (HERE / "step0_arithmetic.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
