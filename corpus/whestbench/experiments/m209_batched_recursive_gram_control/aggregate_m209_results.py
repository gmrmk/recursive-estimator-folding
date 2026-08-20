"""Aggregate the five frozen bound M209 traces without rerunning them."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (209700001, 209700002, 209700003, 209700004, 209700005)
HEADROOM = 1_986_871_472
EXPECTED_BILL = 1_226_651_648
EXPECTED_MATMUL_BILL = 1_167_925_248
EXPECTED_MATMUL_CALLS = 15


def aggregate() -> dict[str, object]:
    records = []
    for seed in SEEDS:
        path = HERE / f"M209_BOUND_NATIVE_TRACE_{seed}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        trace = payload["trace"]
        records.append(
            {
                "seed": seed,
                "failure": trace["failure"],
                "finite": trace["finite"],
                "billed_flops": trace["billed_flops"],
                "matmul_bill": trace["matmul_bill"],
                "matmul_calls": trace["matmul_calls"],
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
                "no_reshape": "reshape" not in trace["operations"],
            }
        )
    residuals = np.asarray([row["residual_s"] for row in records], dtype=np.float64)
    hostile = np.asarray(
        [row["hostile_five_x_effective_component"] for row in records], dtype=np.float64
    )
    hostile_pass = hostile <= HEADROOM
    gates = {
        "five_exact_frozen_seeds": len(records) == len(SEEDS),
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in records),
        "constant_exact_inclusive_bill": all(
            row["billed_flops"] == EXPECTED_BILL for row in records
        ),
        "exact_matmul_bill": all(
            row["matmul_bill"] == EXPECTED_MATMUL_BILL for row in records
        ),
        "exact_matmul_calls": all(
            row["matmul_calls"] == EXPECTED_MATMUL_CALLS for row in records
        ),
        "inclusive_bill_below_headroom": all(
            row["billed_flops"] < HEADROOM for row in records
        ),
        "rss_below_512_mib": all(row["peak_working_set_mib"] < 512.0 for row in records),
        "no_rank3_coefficients": all(
            row["rank3_coefficient_arrays"] == 0 for row in records
        ),
        "no_reshape": all(row["no_reshape"] for row in records),
        "every_hostile_five_x_projection_fits": bool(np.all(hostile_pass)),
    }
    return {
        "candidate": "M209 layer-batched depth-3 recursive Gram control compiler",
        "status": "KILLED_HOSTILE_FIVE_X_WALL_PRESERVE_EXACT_GRAM_RESOURCE_COMPONENT",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "records": records,
        "aggregate": {
            "residual_mean_ms": float(1e3 * np.mean(residuals)),
            "residual_p99_linear_ms": float(
                1e3 * np.quantile(residuals, 0.99, method="linear")
            ),
            "residual_max_ms": float(1e3 * np.max(residuals)),
            "hostile_projection_max": float(np.max(hostile)),
            "hostile_overage_max": float(np.max(hostile) - HEADROOM),
            "hostile_pass_count": int(np.count_nonzero(hostile_pass)),
            "hostile_fail_count": int(np.count_nonzero(~hostile_pass)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in records)),
            "persistent_mib": float(max(row["persistent_mib"] for row in records)),
        },
        "gates": gates,
        "disposition": {
            "schedule": "killed without depth retuning because two of five hostile five-times residual projections exceed the strict component headroom",
            "preserved": "exact symmetric recursive Gram algebra, source parity, 1.226651648B inclusive bill, 15-call layer batch, layer binding, and 760.219824M arithmetic margin",
            "next_mutation": "fuse same-level tree nodes into one batch call under a separately frozen candidate; do not rewrite M209",
            "no_credit": [
                "physical Source211 provider",
                "M198 or terminal cost",
                "source variance or MSE",
                "winner or champion"
            ]
        }
    }


if __name__ == "__main__":
    output = HERE / "M209_RESULTS_20260809.json"
    result = aggregate()
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
