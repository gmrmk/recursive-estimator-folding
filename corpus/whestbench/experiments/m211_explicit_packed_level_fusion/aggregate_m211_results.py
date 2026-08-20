"""Aggregate the five frozen M211 traces without rerunning them."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (211700001, 211700002, 211700003, 211700004, 211700005)
HEADROOM = 1_986_871_472


def aggregate() -> dict[str, object]:
    records = []
    for seed in SEEDS:
        payload = json.loads(
            (HERE / f"M211_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")
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
            "untracked_full_plane_temporaries": trace["allocation"]["untracked_full_plane_temporaries"],
        })
    bills = {row["billed_flops"] for row in records}
    hostile = np.asarray([row["hostile"] for row in records])
    residual = np.asarray([row["residual_s"] for row in records])
    gates = {
        "five_frozen_seeds": len(records) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in records),
        "constant_bill": len(bills) == 1,
        "bill_below_1_35b": all(row["billed_flops"] < 1_350_000_000 for row in records),
        "exact_four_matmul_calls": all(row["matmul_calls"] == 4 for row in records),
        "exact_matmul_bill": all(row["matmul_bill"] == 1_167_925_248 for row in records),
        "exact_four_reshape_calls": all(row["reshape_calls"] == 4 for row in records),
        "exact_reshape_bill": all(row["reshape_bill"] == 16_252_928 for row in records),
        "persistent_below_300_mib": all(row["persistent_mib"] < 300.0 for row in records),
        "rss_below_512_mib": all(row["peak_working_set_mib"] < 512.0 for row in records),
        "no_untracked_full_plane_temporary": all(row["untracked_full_plane_temporaries"] == 0 for row in records),
        "every_hostile_five_x_projection_fits": bool(np.all(hostile <= HEADROOM)),
    }
    passed = all(gates.values())
    bill = next(iter(bills)) if len(bills) == 1 else None
    return {
        "candidate": "M211 explicit packed level fusion",
        "status": "EXPLICIT_MEMORY_RESOURCE_COMPONENT_PASS_PROVIDER_AND_STREAM_BINDING_BLOCKED" if passed else "KILLED_FROZEN_RESOURCE_GATE",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "records": records,
        "aggregate": {
            "inclusive_bill": bill,
            "strict_component_arithmetic_margin": HEADROOM - bill if bill is not None else None,
            "residual_mean_ms": float(1e3 * np.mean(residual)),
            "residual_max_ms": float(1e3 * np.max(residual)),
            "hostile_projection_max": float(np.max(hostile)),
            "hostile_margin_min": float(HEADROOM - np.max(hostile)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in records)),
            "persistent_mib": float(max(row["persistent_mib"] for row in records)),
        },
        "gates": gates,
        "disposition": {
            "promoted": "explicitly packed four-call exact-real Gram/source resource component" if passed else None,
            "still_blocked": [
                "M179-bound all-layer factor lifecycle and immediate M198 consumption",
                "physical K4/K31/K22/C211 provider and residual proposal",
                "full integrated replacement and terminal native trace",
                "source variance, MSE, score, and winner evidence"
            ]
        }
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M211_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
