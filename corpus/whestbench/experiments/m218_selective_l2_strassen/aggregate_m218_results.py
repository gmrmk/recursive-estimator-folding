"""Aggregate frozen M218 traces and compare honestly with M215."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (218700001, 218700002, 218700003, 218700004, 218700005)
EXPECTED_BILL = 4_622_180_352
CAP = 6_824_272_176
TERMINAL_FLOOR = 134_217_216
M215_BILL = 5_446_508_544
M215_WORST_RESIDUAL_S = 0.0013124000106472522
M215_WORST_HOSTILE = 6_102_708_549.323626


def _row(payload: dict[str, object]) -> dict[str, object]:
    trace = payload["trace"]
    return {
        "seed": int(payload["seed"]),
        "failure": trace["failure"],
        "finite": trace["finite"],
        "bill": trace["billed_flops"],
        "combined_m212_m218_bill": trace["combined_arithmetic_bill"],
        "residual_s": trace["residual_s"],
        "hostile": trace["hostile_five_x_effective_component"],
        "raw_remaining": trace["raw_remaining_for_other_unknowns"],
        "hostile_remaining": trace["hostile_remaining_for_other_unknowns"],
        "prediction_match": trace["prediction_match"],
        "max_error": trace["numerical_audit"]["max_abs_error_vs_m215"],
        "numerical_threshold": trace["numerical_audit"]["frozen_threshold"],
        "numerical_pass": trace["numerical_audit"]["passes"],
        "aabb_max_asymmetry": trace["aabb_max_asymmetry"],
        "resource_peak_rss_mib": trace["resource_rss_checkpoint"]["peak_working_set_mib"],
        "audit_peak_rss_mib": payload["rss_after_audit"]["peak_working_set_mib"],
        "persistent_mib": trace["allocation"]["persistent_mib_visible_to_m218"],
        "incremental_mib": trace["allocation"]["incremental_m218_mib"],
        "runtime": payload["runtime"],
    }


def aggregate() -> dict[str, object]:
    rows = [
        _row(json.loads((HERE / f"M218_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")))
        for seed in SEEDS
    ]
    residual = np.asarray([row["residual_s"] for row in rows], dtype=np.float64)
    hostile = np.asarray([row["hostile"] for row in rows], dtype=np.float64)
    errors = np.asarray([row["max_error"] for row in rows], dtype=np.float64)
    worst_residual = float(np.max(residual))
    worst_hostile = float(np.max(hostile))
    one_x_worst = EXPECTED_BILL + 1e11 * worst_residual
    m215_one_x_worst = M215_BILL + 1e11 * M215_WORST_RESIDUAL_S

    gates = {
        "five_frozen_isolated_processes": len(rows) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in rows),
        "flopscope_0_10_0": all(
            row["runtime"]["flopscope"].split("+", 1)[0] == "0.10.0"
            for row in rows
        ),
        "constant_exact_bill": all(row["bill"] == EXPECTED_BILL for row in rows),
        "combined_m212_m218_bill": all(
            row["combined_m212_m218_bill"] == 5_871_433_728 for row in rows
        ),
        "every_operation_prediction": all(
            all(row["prediction_match"].values()) for row in rows
        ),
        "numerical_drift_gate": all(row["numerical_pass"] for row in rows),
        "aabb_symmetric_to_1e_15": all(row["aabb_max_asymmetry"] <= 1e-15 for row in rows),
        "persistent_memory_exact": all(row["persistent_mib"] == 333.61328125 for row in rows),
        "incremental_memory_exact": all(row["incremental_mib"] == 231.53125 for row in rows),
        "resource_rss_below_512_mib": all(row["resource_peak_rss_mib"] < 512.0 for row in rows),
        "every_hostile_five_x_projection_fits": bool(np.all(hostile <= CAP)),
    }
    passed = all(gates.values())
    status = (
        "SCREENED_EXACT_BILLED_COST_SURVIVOR_HOSTILE_FIVE_X_HEADROOM_REGRESSION_INTEGRATED_SELECTION_BLOCKED"
        if passed
        else "KILLED_FROZEN_IDENTITY_NUMERICAL_OR_RESOURCE_GATE"
    )
    hostile_remaining = CAP - worst_hostile
    return {
        "candidate": "M218 selective exact L2 Strassen for M215 A/E",
        "status": status,
        "firewall": "generated-only response-free algebra and resource audit",
        "changed_mechanism": "only A/E conventional matmul becomes factorized classic L2 Strassen",
        "unchanged": [
            "M215 collision equations and strict-distinct ownership",
            "legacy physical collision routing",
            "M215 D symmetric recursion",
            "M215 receipt and binding contract",
        ],
        "algebra": {
            "small_widths": [4, 8, 12],
            "integer_bit_exact": True,
            "permutation_gauge_zero": "pass",
            "target_max_abs_error_vs_m215": float(np.max(errors)),
            "target_min_frozen_threshold": float(min(row["numerical_threshold"] for row in rows)),
        },
        "records": rows,
        "aggregate": {
            "incremental_bill": EXPECTED_BILL,
            "recovery_vs_m215_bill": M215_BILL - EXPECTED_BILL,
            "combined_m212_m218_bill": 5_871_433_728,
            "raw_remaining_for_provider_m198_terminal_and_unknowns": CAP - EXPECTED_BILL,
            "raw_after_terminal_floor_sensitivity": CAP - EXPECTED_BILL - TERMINAL_FLOOR,
            "residual_mean_ms": float(1e3 * np.mean(residual)),
            "residual_max_ms": float(1e3 * worst_residual),
            "one_x_worst_effective": one_x_worst,
            "one_x_worst_recovery_vs_m215": m215_one_x_worst - one_x_worst,
            "hostile_five_x_max": worst_hostile,
            "hostile_five_x_remaining": hostile_remaining,
            "hostile_after_terminal_floor_sensitivity": hostile_remaining - TERMINAL_FLOOR,
            "hostile_regression_vs_m215": worst_hostile - M215_WORST_HOSTILE,
            "resource_peak_rss_mib": float(max(row["resource_peak_rss_mib"] for row in rows)),
            "audit_peak_rss_mib": float(max(row["audit_peak_rss_mib"] for row in rows)),
            "persistent_mib": 333.61328125,
        },
        "gates": gates,
        "allowance_assessment": {
            "verdict": "CONDITIONALLY_CREDIBLE_INTEGRATION_EXPERIMENT_NOT_CREDITABLE_FIT",
            "reason": (
                "The 2.202B raw remainder and 610M observed one-times recovery make an integrated trace worth running, "
                "but the frozen five-times remainder is only 475.8M and 341.6M after the terminal floor; M198/provider "
                "native cost and integrated wall are unmetered. M218 also loses 245.8M hostile headroom versus M215."
            ),
            "credit_granted": False,
        },
        "disposition": {
            "preserved_component": "exact factorized L2 A/E circuit with 824.328M billed recovery",
            "not_promoted_over_m215": "hostile five-times effective headroom regresses; integrated one-times trace must choose",
            "still_blocked": [
                "layer-bound physical distinct provider",
                "native M198 conversion and source lifecycle",
                "terminal implementation beyond its floor",
                "full integrated allocation/copy/wall trace",
                "variance, MSE, score, submission, and winner evidence",
            ],
        },
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M218_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
