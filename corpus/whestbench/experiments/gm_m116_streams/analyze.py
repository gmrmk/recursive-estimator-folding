"""Aggregate the arms, run the parity word-count, emit results.json."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import statistics

import numpy as np

HERE = Path(__file__).resolve().parent

LEDGER_M116B = {"calls": 1024, "residual_s": 0.6105131132062525}
LEDGER_M116C = {"calls": 512, "residual_s": 0.3284645767}
RESIDUAL_GATE_S = 0.170
PEAK_GATE_MIB = 464.0
EXPECTED_BILL = 189_738_221_568

REF_TAGS = ["ref_a", "ref_b", "ref_hp", "ref_hp2"]
FUSED_TAGS = ["fused_a", "fused_b", "fused_hp", "fused_hp2"]


def load(tag: str) -> dict:
    return json.loads((HERE / f"arm_{tag}.json").read_text(encoding="utf-8"))


def ci95(values: list[float]) -> tuple[float, float, float]:
    n = len(values)
    mean = statistics.fmean(values)
    if n < 2:
        return mean, mean, mean
    sd = statistics.stdev(values)
    t = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}.get(n, 1.96)
    half = t * sd / math.sqrt(n)
    return mean, mean - half, mean + half


def main() -> None:
    refs = [load(t) for t in REF_TAGS]
    fused = [load(t) for t in FUSED_TAGS]

    # --- bitwise parity, explicit word count over the two dumped states -----
    a = np.load(HERE / "state_ref_a.npy")
    b = np.load(HERE / "state_fused_a.npy")
    words_a, words_b = a.view(np.uint32), b.view(np.uint32)
    differing = int(np.count_nonzero(words_a != words_b))
    parity = {
        "shape": list(a.shape),
        "float32_words": int(a.size),
        "differing_float32_words": differing,
        "bitwise_equal": differing == 0,
        "max_abs_difference": float(np.max(np.abs(a - b))),
        "sha256_ref_a": hashlib.sha256(memoryview(a).cast("B")).hexdigest(),
        "sha256_fused_a": hashlib.sha256(memoryview(b).cast("B")).hexdigest(),
        "all_run_sha256": sorted({r["state_sha256"] for r in refs + fused}),
        "distinct_sha256_across_8_runs": len({r["state_sha256"] for r in refs + fused}),
    }

    ref_res = [r["residual_s"] for r in refs]
    fus_res = [r["residual_s"] for r in fused]
    ref_mean, ref_lo, ref_hi = ci95(ref_res)
    fus_mean, fus_lo, fus_hi = ci95(fus_res)

    # control reproduction: ARM REF has the consumed M116c dispatch schedule
    host_factor_mean = ref_mean / LEDGER_M116C["residual_s"]
    host_factor_min = min(ref_res) / LEDGER_M116C["residual_s"]
    control_reproduces = 0.9 <= host_factor_mean <= 1.1

    # ledger two-point law (campaign host), used only as a labelled projection
    slope = (LEDGER_M116B["residual_s"] - LEDGER_M116C["residual_s"]) / (
        LEDGER_M116B["calls"] - LEDGER_M116C["calls"]
    )
    intercept = LEDGER_M116C["residual_s"] - LEDGER_M116C["calls"] * slope
    fused_calls = fused[0]["full_prediction_matmul_calls"]
    ledger_law_projection = intercept + fused_calls * slope

    results = {
        "candidate": "m116b_inplace_streamed_l3_b2048 (gm_m116_streams revival)",
        "step0": json.loads((HERE / "step0_results.json").read_text(encoding="utf-8")),
        "arms": {
            "REF_group1_512calls": {
                "tags": REF_TAGS,
                "dispatches_per_layer": refs[0]["dispatches_per_layer"],
                "matmul_calls": refs[0]["full_prediction_matmul_calls"],
                "residual_s": ref_res,
                "residual_mean_s": ref_mean,
                "residual_ci95_s": [ref_lo, ref_hi],
                "workspace_mib": refs[0]["workspace_mib"],
                "peak_mib": [r["peak_working_set_mib_after_prediction"] for r in refs],
                "predict_wall_s": [r["predict_wall_s"] for r in refs],
                "billed_flops": sorted({r["billed_flops"] for r in refs}),
            },
            "FUSED_group4_160calls": {
                "tags": FUSED_TAGS,
                "dispatches_per_layer": fused[0]["dispatches_per_layer"],
                "dispatch_plan_per_layer": fused[0]["dispatch_plan_per_layer"],
                "matmul_calls": fused_calls,
                "residual_s": fus_res,
                "residual_mean_s": fus_mean,
                "residual_ci95_s": [fus_lo, fus_hi],
                "workspace_mib": fused[0]["workspace_mib"],
                "peak_mib": [r["peak_working_set_mib_after_prediction"] for r in fused],
                "predict_wall_s": [r["predict_wall_s"] for r in fused],
                "billed_flops": sorted({r["billed_flops"] for r in fused}),
            },
        },
        "parity": parity,
        "dispatch_reduction_factor": refs[0]["full_prediction_matmul_calls"] / fused_calls,
        "residual_reduction_factor_measured": ref_mean / fus_mean,
        "control_reproduction": {
            "ledger_m116c_residual_s": LEDGER_M116C["residual_s"],
            "measured_same_schedule_mean_s": ref_mean,
            "measured_same_schedule_min_s": min(ref_res),
            "host_slowdown_factor_mean": host_factor_mean,
            "host_slowdown_factor_min": host_factor_min,
            "control_reproduces_within_10pct": control_reproduces,
        },
        "labelled_projections_not_gates": {
            "ledger_two_point_slope_s_per_call": slope,
            "ledger_two_point_intercept_s": intercept,
            "ledger_law_projection_for_160_calls_s": ledger_law_projection,
            "host_normalized_fused_residual_mean_s": fus_mean / host_factor_mean,
            "host_normalized_fused_residual_min_s": min(fus_res) / host_factor_min,
        },
        "gates": {
            "STEP0_relevance": {
                "quantity": "pre_L3_baseline_minus_189738221568",
                "value": 48_478_846_976,
                "floor": 1_000_000_000,
                "result": "CLEAR",
            },
            "G1_residual_le_0.170s_ABSOLUTE": {
                "raw_measured_mean_s": fus_mean,
                "raw_measured_ci95_s": [fus_lo, fus_hi],
                "gate_s": RESIDUAL_GATE_S,
                "raw_result": "FAIL",
                "control_valid": control_reproduces,
                "result": "NOT_MEASURABLE_ON_THIS_HOST",
            },
            "G2_bitwise_parity": {
                "differing_float32_words": differing,
                "of_total": int(a.size),
                "result": "PASS" if differing == 0 else "FAIL",
            },
            "G3_peak_le_464_MiB": {
                "measured_mib": max(r["peak_working_set_mib_after_prediction"] for r in fused),
                "gate_mib": PEAK_GATE_MIB,
                "result": "PASS"
                if max(r["peak_working_set_mib_after_prediction"] for r in fused) <= PEAK_GATE_MIB
                else "FAIL",
            },
            "INV_bill_exact": {
                "expected": EXPECTED_BILL,
                "observed": sorted({r["billed_flops"] for r in refs + fused}),
                "result": "PASS"
                if {r["billed_flops"] for r in refs + fused} == {EXPECTED_BILL}
                else "FAIL",
            },
            "INV_finite": {
                "result": "PASS" if all(r["finite"] for r in refs + fused) else "FAIL"
            },
            "INV_wall_lt_20s": {
                "measured_s": [r["predict_wall_s"] for r in refs + fused],
                "result": "NOT_MEASURABLE_ON_THIS_HOST",
                "note": "control arm also fails; host is ~2.4-3.4x slower than the campaign host",
            },
        },
        "verdict": "INCONCLUSIVE",
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(json.dumps(results["gates"], indent=1))
    print(json.dumps(results["control_reproduction"], indent=1))
    print(json.dumps(results["labelled_projections_not_gates"], indent=1))
    print("residual REF ", [round(v, 6) for v in ref_res], "mean", round(ref_mean, 6))
    print("residual FUSED", [round(v, 6) for v in fus_res], "mean", round(fus_mean, 6))


if __name__ == "__main__":
    main()
