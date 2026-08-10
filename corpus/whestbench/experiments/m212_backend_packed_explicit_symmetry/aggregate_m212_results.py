"""Aggregate the five frozen M212 traces without reruns."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (212700001, 212700002, 212700003, 212700004, 212700005)
HEADROOM = 1_986_871_472
EXPECTED_BILL = 1_249_253_376


def aggregate() -> dict[str, object]:
    records = []
    for seed in SEEDS:
        payload = json.loads(
            (HERE / f"M212_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")
        )
        trace = payload["trace"]
        records.append({
            "seed": seed,
            "failure": trace["failure"],
            "finite": trace["finite"],
            "billed_flops": trace["billed_flops"],
            "matmul_calls": trace["matmul_calls"],
            "matmul_bill": trace["matmul_bill"],
            "reshape_calls": trace["reshape_calls"],
            "reshape_bill": trace["reshape_bill"],
            "residual_s": trace["residual_s"],
            "hostile": trace["hostile_five_x_effective_component"],
            "peak_working_set_mib": payload["rss"]["peak_working_set_mib"],
            "persistent_mib": trace["allocation"]["persistent_mib"],
            "user_full_plane_temporaries": trace["allocation"]["user_full_plane_temporaries"],
        })
    hostile = np.asarray([row["hostile"] for row in records])
    residual = np.asarray([row["residual_s"] for row in records])
    gates = {
        "five_frozen_seeds": len(records) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in records),
        "constant_exact_bill": all(row["billed_flops"] == EXPECTED_BILL for row in records),
        "exact_four_matmul_calls": all(row["matmul_calls"] == 4 for row in records),
        "exact_matmul_bill": all(row["matmul_bill"] == 1_167_925_248 for row in records),
        "exact_four_reshape_calls": all(row["reshape_calls"] == 4 for row in records),
        "exact_reshape_bill": all(row["reshape_bill"] == 16_252_928 for row in records),
        "rss_below_512_mib": all(row["peak_working_set_mib"] < 512.0 for row in records),
        "no_user_full_plane_temporary": all(row["user_full_plane_temporaries"] == 0 for row in records),
        "every_hostile_five_x_projection_fits": bool(np.all(hostile <= HEADROOM)),
    }
    passed = all(gates.values())
    return {
        "candidate": "M212 backend-packed matmul with explicit symmetry scratch",
        "status": "METER_LAWFUL_RESOURCE_COMPONENT_PASS_PROVIDER_AND_STREAM_BLOCKED" if passed else "KILLED_FROZEN_RESOURCE_GATE",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "records": records,
        "aggregate": {
            "inclusive_bill": EXPECTED_BILL,
            "strict_component_arithmetic_margin": HEADROOM - EXPECTED_BILL,
            "residual_mean_ms": float(1e3 * np.mean(residual)),
            "residual_max_ms": float(1e3 * np.max(residual)),
            "hostile_projection_max": float(np.max(hostile)),
            "hostile_margin_min": float(HEADROOM - np.max(hostile)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in records)),
            "persistent_mib": float(max(row["persistent_mib"] for row in records)),
        },
        "gates": gates,
        "disposition": {
            "promoted": "shape-billed four-matmul exact-real resource component with caller-owned symmetry scratch" if passed else None,
            "still_blocked": [
                "M179-bound factor lifecycle and immediate M198 consumption",
                "physical K4/K31/K22/C211 provider and residual proposal",
                "full integrated replacement and terminal trace",
                "source variance, MSE, score, and winner evidence"
            ]
        }
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M212_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
