"""STEP 3 -- the honest MARGINAL gain, and the two composition costs.

U-F1 divides by a CLASSICAL dense matmul.  Production runs
RowBlockedBatchedWinograd, metered in step 1 at 7,427,768,320 FLOPs =
0.88015058 of classical for the production deep-layer shape.  Every U-F1
score number therefore re-banks a saving the champion has already banked.

This step:
  (A) recomputes r(d) against what we actually run,
  (B) redoes the adjusted-score translation two independent ways,
  (C) measures the workspace and residual-wall composition costs.

Residual rate is DERIVED from the committed integrated audit:
  parent 170.530655499e9 billed + 0.159546 s residual -> 186.485295448e9
  child  159.492745546e9 billed + 0.160284 s residual -> 175.521105660e9
  both give exactly 1.0e11 effective FLOPs per residual second.
"""

from __future__ import annotations

import json
import sys
import time
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
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cost_model import direct_cost  # noqa: E402
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd  # noqa: E402
from step1_production_baseline import VARIANTS, strassen_charge  # noqa: E402
from step2_composed_depth_kernel import RowBlockedDepthStrassen  # noqa: E402

BUDGET = 10**18
M, K, N = 64512, 256, 256

# --- committed champion / trace figures, quoted with their sources ---
CHAMPION_C = 176.830e9          # graded mean effective compute
CHAMPION_CB = 0.650
CHAMPION_ADJ = 1.832e-7
MATMUL_LANE = 145.138e9         # prose figure U-F1 uses (flagged untraceable
                                # in core/CODEX_HANDOFF_20260810.md:333)
ELIGIBLE_FRACTION = 0.574164    # INTEGRATED_BATCHED_WINOGRAD_REPORT.md:57
TRACE_DIRECT_HOOK_BILL = 161.964214272e9
TRACE_SELECTED_HOOK_BILL = 150.926304319e9
TRACE_SAVED = 11.037909953e9
TRACE_PARENT_TOTAL = 170.530655499e9
TRACE_CHILD_TOTAL = 159.492745546e9
RESIDUAL_RATE = 1.0e11          # effective FLOPs per residual second


def residual_rate_crosscheck():
    p = (186.485295448e9 - 170.530655499e9) / 0.159546
    c = (175.521105660e9 - 159.492745546e9) / 0.160284
    return {"from_parent": p, "from_child": c,
            "agree_to_rel": abs(p - c) / p}


def score(cost):
    raw_mse = CHAMPION_ADJ / max(0.1, CHAMPION_CB)
    return raw_mse * max(0.1, cost / (CHAMPION_C / CHAMPION_CB))


def timed(build, repeats=3):
    """min over repeats of (wall, residual, backend, overhead) for multiply."""
    best = None
    for _ in range(repeats):
        op, fa, fb, out = build()
        with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
            t0 = time.perf_counter()
            op.multiply(fa, fb, out=out)
            wall = time.perf_counter() - t0
            s = bud.summary_dict()
            rec = (wall, float(s["residual_wall_time_s"]),
                   float(s["flopscope_backend_time_s"]),
                   float(s["flopscope_overhead_time_s"]),
                   int(s["flops_used"]))
        if best is None or rec[1] < best[1]:
            best = rec
        del op
    return {"wall_s": best[0], "residual_wall_s": best[1],
            "backend_s": best[2], "overhead_s": best[3], "flops": best[4]}


def main():
    out = {"residual_rate_crosscheck": residual_rate_crosscheck()}
    classical = direct_cost(M, K, N)
    prod_bill = 7_427_768_320                       # metered in step 1
    r_prod = prod_bill / classical

    # ---------------- (A) marginal r(d) -----------------------------------
    depths = {}
    for d in range(1, 6):
        b777 = strassen_charge(M, K, N, d,
                               VARIANTS["V5_production_batched_ACTUAL"])
        b_v1 = strassen_charge(M, K, N, d, VARIANTS["V1_winograd15_floor"])
        depths[d] = {
            "bill_777_production_style": b777,
            "r_vs_classical_777": b777 / classical,
            "r_vs_classical_V1_floor_UF1_headline": b_v1 / classical,
            "MARGINAL_factor_vs_production": b777 / prod_bill,
            "UF1_implied_factor": b_v1 / classical,
            "UF1_overstatement_of_saving":
                None if b777 == prod_bill else
                (1 - b_v1 / classical) / (1 - b777 / prod_bill),
            "separate_matmul_calls_if_V1_floor_schedule": 7 ** d,
        }
    out["production_baseline"] = {
        "metered_bill": prod_bill, "classical": classical,
        "r_vs_classical": r_prod,
        "matches_recorded_mutation_B_L1_ratio_0_880151": abs(r_prod - 0.880151) < 5e-7,
    }
    out["depths"] = depths

    # ---------------- (B) score translation, two routes -------------------
    raw_mse = CHAMPION_ADJ / max(0.1, CHAMPION_CB)
    B = CHAMPION_C / CHAMPION_CB
    routes = {}
    for label, elig in (("whole_lane", 1.0),
                        ("measured_57.4164pct", ELIGIBLE_FRACTION)):
        rows = []
        E = MATMUL_LANE * elig       # already-Winograd eligible mass inside C
        for d in range(1, 6):
            f = depths[d]["MARGINAL_factor_vs_production"]
            r_uf1 = depths[d]["r_vs_classical_V1_floor_UF1_headline"]
            c_hon = CHAMPION_C - E * (1 - f)
            c_uf1 = CHAMPION_C - E * (1 - r_uf1)
            rows.append({
                "d": d,
                "UF1_C": c_uf1, "UF1_C_over_B": c_uf1 / B,
                "UF1_score": score(c_uf1),
                "UF1_gain": CHAMPION_ADJ / score(c_uf1),
                "HONEST_C": c_hon, "HONEST_C_over_B": c_hon / B,
                "HONEST_score": score(c_hon),
                "HONEST_gain": CHAMPION_ADJ / score(c_hon),
            })
        routes[label] = rows
    out["route1_lane_arithmetic"] = {
        "raw_mse": raw_mse, "B": B, "rows": routes}

    # Route 2: use the MEASURED full-trace hook bills instead of the
    # untraceable 145.138e9 prose lane.
    E_direct = TRACE_DIRECT_HOOK_BILL * ELIGIBLE_FRACTION
    implied_saving_d1 = E_direct * (1 - r_prod)
    r2 = []
    for d in range(1, 6):
        r_cl = depths[d]["r_vs_classical_777"]
        saving = E_direct * (1 - r_cl)
        total_d = TRACE_PARENT_TOTAL - saving
        r_c_vs_champion = total_d / TRACE_CHILD_TOTAL
        c_d = CHAMPION_C * r_c_vs_champion
        r2.append({
            "d": d, "eligible_direct_mass": E_direct,
            "saving_vs_all_direct": saving,
            "full_trace_analytic_total": total_d,
            "ratio_to_measured_champion_trace": r_c_vs_champion,
            "scaled_champion_C": c_d,
            "score": score(c_d), "gain": CHAMPION_ADJ / score(c_d),
        })
    out["route2_measured_trace"] = {
        "eligible_direct_mass": E_direct,
        "model_implied_d1_saving": implied_saving_d1,
        "recorded_d1_saving": TRACE_SAVED,
        "agreement_rel": abs(implied_saving_d1 - TRACE_SAVED) / TRACE_SAVED,
        "rows": r2,
    }

    # ---------------- (C) composition costs -------------------------------
    rng = np.random.default_rng(20260810)
    a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
    b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
    fa, fb = fnp.asarray(a), fnp.asarray(b)

    def build_prod():
        op = RowBlockedBatchedWinograd(M, N, BLOCK_ROWS)
        return op, fa, fb, fnp.empty((M, N), dtype=fnp.float32)

    def build_depth(d, blk):
        def f():
            op = RowBlockedDepthStrassen(M, N, d, blk)
            return op, fa, fb, fnp.empty((M, N), dtype=fnp.float32)
        return f

    prod_ws = RowBlockedBatchedWinograd(M, N, BLOCK_ROWS)
    timings = {"production_d1_frozen": timed(build_prod)}
    timings["production_d1_frozen"]["workspace_MiB"] = (
        prod_ws.buffer_bytes / 1048576)
    del prod_ws
    configs = [(2, 4096), (3, 4096), (4, 4096), (5, 4096),
               (4, 1024), (4, 256), (3, 1024)]
    for d, blk in configs:
        op = RowBlockedDepthStrassen(M, N, d, blk)
        ws = op.buffer_bytes / 1048576
        blocks = len(range(0, M, blk))
        del op
        t = timed(build_depth(d, blk))
        t["workspace_MiB"] = ws
        t["row_blocks"] = blocks
        t["numpy_calls_per_product"] = blocks * (7 * (2 * d - 1) + 1) + 7 * d
        timings[f"d{d}_block{blk}"] = t
        print(f"d={d} blk={blk} flops={t['flops']} ws={ws:.2f}MiB "
              f"wall={t['wall_s']:.3f}s resid={t['residual_wall_s']:.4f}s",
              flush=True)

    base_res = timings["production_d1_frozen"]["residual_wall_s"]
    base_flops = timings["production_d1_frozen"]["flops"]
    for key, t in timings.items():
        if key == "production_d1_frozen":
            continue
        d_res = t["residual_wall_s"] - base_res
        t["delta_residual_s_vs_production"] = d_res
        t["residual_charged_effective_flops"] = d_res * RESIDUAL_RATE
        t["billed_flops_saved_vs_production"] = base_flops - t["flops"]
        t["net_effective_saving"] = (base_flops - t["flops"]
                                     - d_res * RESIDUAL_RATE)
    out["composition_costs_one_deep_layer_product"] = timings
    out["memory_envelope"] = {
        "gate": "<512 MiB peak working set (GEN5_MUTANT_RECURSION:133; "
                "INTEGRATED_BATCHED_WINOGRAD_REPORT decision)",
        "measured_champion_peak_MiB_at_block8192": 474.301,
        "note": "COMPRESSION_SCORE_CALCULUS_20260806.md:167",
    }
    (HERE / "step3_marginal_and_score.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("residual_rate_crosscheck", "production_baseline",
                       "depths", "route2_measured_trace")}, indent=2))


if __name__ == "__main__":
    main()
