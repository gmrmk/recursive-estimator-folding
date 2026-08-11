"""STEP 1 -- meter the ACTUAL frozen production deep-layer kernel.

U-F1 computes r(d) = charged(d) / classical, where classical is a dense
direct matmul.  Our production deep-layer path is NOT classical: it is
RowBlockedBatchedWinograd (frozen, v3.1 GUARDS package_source), which is
already a one-level Winograd.  This step measures what we actually run.

Read-only import of the frozen source.  No modification, no estimator, no
scorer, no network, synthetic data only.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

import flopscope as fl
import flopscope.numpy as fnp

FROZEN = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
    r"\corpus\whestbench\experiments\v31_guards\package_source"
)
sys.path.insert(0, str(FROZEN))

from cost_model import direct_cost, owned_batched_candidate_bill  # noqa: E402
from row_blocked_winograd import (  # noqa: E402
    BLOCK_ROWS, RowBlockedBatchedWinograd, independently_expanded_bill,
    row_blocked_bill_identity,
)

HERE = Path(__file__).resolve().parent
BUDGET = 10**18

# (a, b, c) = writes per level on the (m/2 x k/2), (k/2 x n/2), (m/2 x n/2)
# block families, in units of one block each.
VARIANTS = {
    "V1_winograd15_floor": (4, 4, 7),
    "V2_winograd15_batched_UF1": (6, 6, 7),
    "V5_production_batched_ACTUAL": (7, 7, 7),
    "V3_strassen18_floor": (5, 5, 8),
    "V4_m218_copy_idiom": (11, 11, 12),
}


def matmul_charge(m, k, n, batch=1):
    return batch * (2 * m * k * n - m * n)


def strassen_charge(M, K, N, d, abc):
    """Exact integer charged FLOPs for a depth-d <2,2,2> recursion."""
    a_ops, b_ops, c_ops = abc
    if d == 0:
        return matmul_charge(M, K, N)
    for lvl in range(d):
        if (M >> lvl) % 2 or (K >> lvl) % 2 or (N >> lvl) % 2:
            raise ValueError("shape not 2-divisible to depth %d" % d)
    movement = 0
    for lvl in range(d):
        m, k, n = M >> lvl, K >> lvl, N >> lvl
        movement += 7**lvl * (
            a_ops * (m // 2) * (k // 2)
            + b_ops * (k // 2) * (n // 2)
            + c_ops * (m // 2) * (n // 2)
        )
    return matmul_charge(M >> d, K >> d, N >> d, batch=7**d) + movement


def closed_form(M, K, N, d, abc):
    """Independent Fraction re-derivation of the same quantity."""
    a_ops, b_ops, c_ops = abc
    mm = Fraction(7, 8) ** d * 2 * M * K * N - Fraction(7, 4) ** d * M * N
    mv = (Fraction(a_ops * M * K + b_ops * K * N + c_ops * M * N, 3)
          * (Fraction(7, 4) ** d - 1))
    return mm + mv


def meter_production(M, K, N, seed=20260810, alias_out=False):
    rng = np.random.default_rng(seed)
    a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
    b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
    ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
    fa, fb = fnp.asarray(a), fnp.asarray(b)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        op = RowBlockedBatchedWinograd(M, max(K, N), BLOCK_ROWS)
        setup = int(bud.summary_dict()["flops_used"])
        if alias_out:
            out = fa           # ownership-transfer path: hand the input back
        else:
            out = fnp.empty((M, N), dtype=fnp.float32)
        op.multiply(fa, fb, out=out)
        used = int(bud.summary_dict()["flops_used"])
    got = np.asarray(out, dtype=np.float64)[:M, :N]
    rel = float(np.linalg.norm(got - ref) / np.linalg.norm(ref))
    return {
        "workspace_setup_flops": setup,
        "total_flops": used,
        "multiply_flops": used - setup,
        "core_calls": op.last_core_calls,
        "total_matmul_calls": op.last_total_matmul_calls,
        "relative_frobenius_vs_float64_classical": rel,
    }


def main():
    out = {}
    M, K, N = 64512, 256, 256
    classical = direct_cost(M, K, N)

    m1 = meter_production(M, K, N)
    m2 = meter_production(M, K, N)                       # bitwise repeat
    m3 = meter_production(M, K, N, alias_out=True)       # ownership transfer

    predicted = owned_batched_candidate_bill(M, K, N)
    expanded = independently_expanded_bill(M, K, N)
    v5_closed = strassen_charge(M, K, N, 1, VARIANTS["V5_production_batched_ACTUAL"])
    v2_closed = strassen_charge(M, K, N, 1, VARIANTS["V2_winograd15_batched_UF1"])
    v1_closed = strassen_charge(M, K, N, 1, VARIANTS["V1_winograd15_floor"])

    out["production_shape"] = {"M": M, "K": K, "N": N,
                               "classical_direct_bill": classical,
                               "BLOCK_ROWS": BLOCK_ROWS}
    out["metered_production"] = m1
    out["metered_production_repeat"] = m2
    out["metered_production_out_aliases_left"] = m3
    out["bitwise_repeat_identical"] = m1["total_flops"] == m2["total_flops"]
    out["alias_identical_bill"] = m1["multiply_flops"] == m3["multiply_flops"]
    out["frozen_closed_form_bill"] = row_blocked_bill_identity(M, K, N)
    out["frozen_independently_expanded_bill"] = expanded
    out["depth1_closed_forms"] = {
        "V1_winograd15_floor(4,4,7)": v1_closed,
        "V2_winograd15_batched_UF1(6,6,7)": v2_closed,
        "V5_production_batched_ACTUAL(7,7,7)": v5_closed,
    }
    p = m1["multiply_flops"]
    out["identification"] = {
        "metered_multiply_flops": p,
        "matches_frozen_closed_form": p == predicted.total,
        "matches_independently_expanded": p == expanded,
        "matches_V5_777": p == v5_closed,
        "matches_V2_667_as_UF1_assumed": p == v2_closed,
        "V2_undercount_flops": v5_closed - v2_closed,
    }
    out["r_production_vs_classical"] = p / classical
    out["UF1_reported_r1_V1"] = 0.878677
    out["UF1_reported_r1_V2"] = 0.879659

    # Fraction cross-check of the depth-1 closed forms
    out["fraction_crosscheck_d1"] = {
        name: (strassen_charge(M, K, N, 1, abc)
               == closed_form(M, K, N, 1, abc))
        for name, abc in VARIANTS.items()
    }

    (HERE / "step1_production_baseline.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
