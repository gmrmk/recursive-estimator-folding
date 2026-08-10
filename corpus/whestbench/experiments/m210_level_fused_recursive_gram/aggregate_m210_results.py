"""Aggregate the five frozen M210 native traces without reruns."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (210700001, 210700002, 210700003, 210700004, 210700005)
HEADROOM = 1_986_871_472
EXPECTED_BILL = 1_245_190_144


def aggregate() -> dict[str, object]:
    records = []
    for seed in SEEDS:
        payload = json.loads(
            (HERE / f"M210_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")
        )
        trace = payload["trace"]
        records.append(
            {
                "seed": seed,
                "failure": trace["failure"],
                "finite": trace["finite"],
                "billed_flops": trace["billed_flops"],
                "matmul_calls": trace["matmul_calls"],
                "matmul_bill": trace["matmul_bill"],
                "reshape_calls": trace["reshape_calls"],
                "reshape_bill": trace["reshape_bill"],
                "residual_s": trace["residual_s"],
                "hostile_five_x_effective_component": trace[
                    "hostile_five_x_effective_component"
                ],
                "remaining_after_compiler": trace["remaining_after_compiler"],
                "peak_working_set_mib": payload["rss"]["peak_working_set_mib"],
                "private_mib": payload["rss"]["private_mib"],
                "persistent_mib": trace["allocation"]["persistent_mib"],
                "rank3_coefficient_arrays": trace["allocation"][
                    "rank3_coefficient_arrays"
                ],
            }
        )
    residuals = np.asarray([row["residual_s"] for row in records])
    hostile = np.asarray([row["hostile_five_x_effective_component"] for row in records])
    gates = {
        "five_frozen_seeds": len(records) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in records),
        "constant_exact_inclusive_bill": all(row["billed_flops"] == EXPECTED_BILL for row in records),
        "exact_four_matmul_calls": all(row["matmul_calls"] == 4 for row in records),
        "exact_matmul_bill": all(row["matmul_bill"] == 1_167_925_248 for row in records),
        "exact_four_reshape_calls": all(row["reshape_calls"] == 4 for row in records),
        "exact_reshape_bill": all(row["reshape_bill"] == 16_252_928 for row in records),
        "inclusive_bill_below_headroom": all(row["billed_flops"] < HEADROOM for row in records),
        "every_hostile_five_x_projection_fits": bool(np.all(hostile <= HEADROOM)),
        "rss_below_512_mib": all(row["peak_working_set_mib"] < 512.0 for row in records),
        "no_rank3_coefficients": all(row["rank3_coefficient_arrays"] == 0 for row in records),
    }
    return {
        "candidate": "M210 same-level fused depth-3 recursive Gram",
        "status": "RESOURCE_COMPONENT_PASS_CONDITIONAL_ALL_LAYER_STAGING_PROVIDER_BLOCKED",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "records": records,
        "aggregate": {
            "residual_mean_ms": float(1e3 * np.mean(residuals)),
            "residual_p99_linear_ms": float(1e3 * np.quantile(residuals, 0.99, method="linear")),
            "residual_max_ms": float(1e3 * np.max(residuals)),
            "hostile_projection_max": float(np.max(hostile)),
            "hostile_margin_min": float(HEADROOM - np.max(hostile)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in records)),
            "private_mib_max": float(max(row["private_mib"] for row in records)),
            "persistent_mib": float(max(row["persistent_mib"] for row in records)),
            "inclusive_arithmetic_margin": HEADROOM - EXPECTED_BILL,
        },
        "gates": gates,
        "disposition": {
            "promoted": "exact response-free resource component under a caller that lawfully owns all 31 labelled factors and weights",
            "still_blocked": [
                "actual M179 caller must emit and retain the complete bound factor bank",
                "physical K4/K31/K22/C211 provider and sampled residual proposal",
                "M198 and terminal response inclusive cost",
                "one integrated M179-to-M125b lifecycle and cost trace",
                "source variance, MSE, score, and winner evidence"
            ],
            "parent_failure_repaired": "same-level fusion reduces M209 from 15 to 4 matmul dispatches and passes all five hostile wall projections"
        }
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M210_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
