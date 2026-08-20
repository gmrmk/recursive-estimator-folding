"""U-F1 signal-2 closing run: meter a real Strassen-Winograd at the FULL
production width (K = N = 256) and depths 0..5, on a row-count reduced by 8x
(M = 8064 instead of 64512) purely for wall/memory tractability.

r(d) is shown to be M-independent to <2e-4 across M in {8064, 32256, 64512},
so the metered ratios at M = 8064 bind the production shape.

Also emits the supplementary depth 6..8 range (BEYOND the predeclared
d = 0..5 window -- reported separately, not used for the verdict) and a
bitwise determinism repeat.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import flopscope as fl
import flopscope.numpy as fnp

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from uf1_derive_and_verify import (  # noqa: E402
    VARIANTS, matmul_charge, strassen_charge, sw_product,
)

BUDGET = 10**18


def meter(M, K, N, depth, dtype="float32", seed=20260810):
    rng = np.random.default_rng(seed + depth)
    a = np.asarray(rng.standard_normal((M, K)), dtype=dtype)
    b = np.asarray(rng.standard_normal((K, N)), dtype=dtype)
    fa, fb = fnp.asarray(a), fnp.asarray(b)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        C = fnp.empty((M, N), dtype=getattr(fnp, dtype))
        sw_product(fa, fb, C, depth)
        used = int(bud.summary_dict()["flops_used"])
    ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
    got = np.asarray(C, dtype=np.float64)
    rel = float(np.linalg.norm(got - ref) / np.linalg.norm(ref))
    return used, rel


def main() -> None:
    out: dict[str, object] = {}
    M, K, N = 8064, 256, 256
    base = matmul_charge(M, K, N)

    rows = []
    for d in range(0, 6):
        used, rel = meter(M, K, N, d)
        pred = strassen_charge(M, K, N, d, "V1_winograd15_floor")
        rows.append({
            "depth": d,
            "metered_charged_flops": used,
            "analytic_charged_flops": pred["total"],
            "exact_match": used == pred["total"],
            "metered_r": used / base,
            "analytic_r": pred["total"] / base,
            "relative_frobenius_vs_float64_classical": rel,
        })
        print(f"d={d} metered={used} analytic={pred['total']} "
              f"match={used == pred['total']} r={used / base:.6f} rel={rel:.3e}",
              flush=True)
    out["metered_production_width"] = {
        "M": M, "K": K, "N": N, "classical_charged_flops": base, "rows": rows}

    # bitwise determinism repeat of the decisive depth
    rep = [meter(M, K, N, 5)[0] for _ in range(2)]
    out["determinism_repeat_d5"] = {"runs": rep, "identical": rep[0] == rep[1]}
    print("repeat d5:", rep, flush=True)

    # M-independence of r(d)
    mi = {}
    for MM in (8064, 32256, 64512):
        b2 = matmul_charge(MM, K, N)
        mi[f"M{MM}"] = {f"d{d}": strassen_charge(MM, K, N, d,
                                                 "V1_winograd15_floor")["total"] / b2
                        for d in range(0, 6)}
    mi["max_abs_spread_over_M"] = max(
        max(abs(mi[f"M{a}"][f"d{d}"] - mi[f"M{b}"][f"d{d}"])
            for a in (8064, 32256, 64512) for b in (8064, 32256, 64512))
        for d in range(0, 6))
    out["M_independence"] = mi

    # supplementary depths beyond the predeclared window
    supp = {}
    for MM in (64512,):
        b2 = matmul_charge(MM, K, N)
        for d in range(0, 9):
            supp[f"d{d}"] = {v: strassen_charge(MM, K, N, d, v)["total"] / b2
                             for v in VARIANTS}
    out["supplementary_depth_0_to_8_m64512"] = supp
    best = min(supp, key=lambda k: supp[k]["V1_winograd15_floor"])
    out["supplementary_optimal_depth_floor_variant"] = best

    # optimal depth per active width (folded widths the champion actually hits)
    opt = {}
    for W in (256, 128, 64, 32):
        b2 = matmul_charge(32256, W, W)
        rr = {}
        d = 0
        while (W >> d) % 2 == 0 or d == 0:
            try:
                rr[d] = strassen_charge(32256, W, W, d,
                                        "V1_winograd15_floor")["total"] / b2
            except ValueError:
                break
            d += 1
            if d > 8:
                break
        opt[f"W{W}"] = {"r_by_depth": rr,
                        "argmin_depth": min(rr, key=rr.get),
                        "min_r": min(rr.values())}
    out["optimal_depth_by_width"] = opt

    (HERE / "uf1_production_width_metering.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("determinism_repeat_d5", "M_independence",
                       "supplementary_optimal_depth_floor_variant",
                       "optimal_depth_by_width")}, indent=2))


if __name__ == "__main__":
    main()
