"""Aggregate frozen isolated traces and preserve the parallel stress result."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (215700001, 215700002, 215700003, 215700004, 215700005)
EXPECTED_BILL = 5_446_508_544
EXPECTED_MATMUL_BILL = 5_320_548_352
EXPECTED_RESHAPE_BILL = 16_252_928
CAP = 6_824_272_176


def _row(payload: dict[str, object]) -> dict[str, object]:
    trace = payload["trace"]
    return {
        "seed": int(payload["seed"]),
        "failure": trace["failure"],
        "finite": trace["finite"],
        "billed_flops": trace["billed_flops"],
        "combined_arithmetic_bill": trace["combined_arithmetic_bill"],
        "matmul_calls": trace["matmul_calls"],
        "matmul_bill": trace["matmul_bill"],
        "reshape_calls": trace["reshape_calls"],
        "reshape_bill": trace["reshape_bill"],
        "residual_s": trace["residual_s"],
        "hostile": trace["hostile_five_x_effective_component"],
        "aabb_max_asymmetry": trace["aabb_max_asymmetry"],
        "peak_working_set_mib": payload["rss"]["peak_working_set_mib"],
        "persistent_mib": trace["allocation"]["persistent_mib_visible_to_m215"],
        "incremental_collision_mib": trace["allocation"]["incremental_collision_mib"],
        "runtime": payload["runtime"],
    }


def aggregate() -> dict[str, object]:
    rows = [
        _row(json.loads((HERE / f"M215_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")))
        for seed in SEEDS
    ]
    stress_rows = []
    stress_dir = HERE / "parallel_stress"
    for path in sorted(stress_dir.glob("M215_PARALLEL_STRESS_*.json")):
        stress_rows.append(_row(json.loads(path.read_text(encoding="utf-8"))))

    hostile = np.asarray([row["hostile"] for row in rows], dtype=np.float64)
    residual = np.asarray([row["residual_s"] for row in rows], dtype=np.float64)
    gates = {
        "five_frozen_isolated_processes": len(rows) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in rows),
        "flopscope_0_10_0": all(
            row["runtime"]["flopscope"].split("+", 1)[0] == "0.10.0"
            for row in rows
        ),
        "constant_exact_incremental_bill": all(row["billed_flops"] == EXPECTED_BILL for row in rows),
        "combined_m212_m215_arithmetic_bill": all(row["combined_arithmetic_bill"] == 6_695_761_920 for row in rows),
        "exact_five_matmul_calls": all(row["matmul_calls"] == 5 for row in rows),
        "exact_matmul_bill": all(row["matmul_bill"] == EXPECTED_MATMUL_BILL for row in rows),
        "exact_four_reshape_calls": all(row["reshape_calls"] == 4 for row in rows),
        "exact_reshape_bill": all(row["reshape_bill"] == EXPECTED_RESHAPE_BILL for row in rows),
        "persistent_memory_ledger_complete": all(row["persistent_mib"] == 164.08203125 for row in rows),
        "incremental_planes_exactly_62_mib": all(row["incremental_collision_mib"] == 62.0 for row in rows),
        "rss_below_512_mib": all(row["peak_working_set_mib"] < 512.0 for row in rows),
        "aabb_symmetric_to_1e_15": all(row["aabb_max_asymmetry"] <= 1e-15 for row in rows),
        "every_isolated_hostile_five_x_projection_fits": bool(np.all(hostile <= CAP)),
    }
    passed = all(gates.values())
    stress_failures = sum(row["hostile"] > CAP for row in stress_rows)
    return {
        "candidate": "M215 exact noncubic rank-one collision correction",
        "status": (
            "EXACT_STRICT_DISTINCT_OWNERSHIP_BRIDGE_RESOURCE_COMPONENT_PASS_INTEGRATED_DAG_BLOCKED"
            if passed
            else "KILLED_FROZEN_IDENTITY_OR_RESOURCE_GATE"
        ),
        "firewall": "generated-only response-free algebra and resource audit",
        "equations": {
            "A": "(S^2)^T S",
            "t": "(S^3)^T 1",
            "E": "(S^3)^T S",
            "D": "(S^2)^T S^2 = (W^2)^T diag(u^4) (W^2)",
            "Ccol_aaab": "-18 diag(p)A -6 t p^T -12 diag(rho)B +24E",
            "Ccol_aabb": "-12[A diag(p)+diag(p)A^T] -4 rho rho^T -8(B hadamard B)+24D",
            "strict": "M212 complete-domain source minus Ccol",
        },
        "algebra_gate": {
            "widths": [3, 4, 5, 6, 7],
            "collision_max_abs_error": 6.661338147750939e-16,
            "strict_distinct_max_abs_error": 1.3877787807814457e-15,
            "hidden_permutation": "pass",
            "positive_relu_gauge": "pass",
            "zero_factor_exact_zero": "pass",
        },
        "records": rows,
        "aggregate": {
            "incremental_bill": EXPECTED_BILL,
            "combined_m212_m215_arithmetic_bill": 6_695_761_920,
            "raw_incremental_cap": CAP,
            "raw_margin": CAP - EXPECTED_BILL,
            "residual_mean_ms": float(1e3 * np.mean(residual)),
            "residual_max_ms": float(1e3 * np.max(residual)),
            "hostile_projection_max": float(np.max(hostile)),
            "hostile_margin_min": float(CAP - np.max(hostile)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in rows)),
            "persistent_mib": 164.08203125,
            "incremental_collision_mib": 62.0,
        },
        "gates": gates,
        "parallel_stress": {
            "protocol_status": "preserved_noncanonical_concurrent_launch_stress_not_used_as_single_process_gate",
            "records": stress_rows,
            "failures_over_cap": stress_failures,
            "constraint": "do not co-launch independent M215 compilers; integrated official trace remains mandatory",
        },
        "disposition": {
            "promoted_component": (
                "exact M212-complete to M151-strict collision subtraction using A/t/E/D"
                if passed
                else None
            ),
            "legacy_collision_consequence": (
                "already-paid physical K4/K31/K22 owners can remain injected; M215 does not recreate them"
            ),
            "still_blocked": [
                "physical distinct C211 residual provider and proposal binding",
                "M179-to-M212 factor lifecycle in the actual two-phase caller",
                "M198 next-context conversion and terminal response",
                "full replacement-DAG allocation/copy and integrated wall trace",
                "source variance, MSE, score, submission, and winner evidence",
            ],
        },
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M215_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
