"""Aggregate M231's five frozen fresh-process traces without retuning."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (227700001, 227700002, 227700003, 227700004, 227700005)
EXPECTED_M231_BILL = 864_993_280
EXPECTED_COMBINED_BILL = 2_114_246_656
EXPECTED_MATMUL_BILL = 767_950_848
CAP = 3_727_757_440


def _row(payload: dict[str, object]) -> dict[str, object]:
    trace = payload["trace"]
    operations = trace["operations"]
    return {
        "seed": int(payload["seed"]),
        "failure": trace["failure"],
        "finite": trace["finite"],
        "runtime_hashes_match": trace["runtime_hashes_match"],
        "m212_bill": trace["m212_bill"],
        "m231_bill": trace["m231_bill"],
        "combined_arithmetic_bill": trace["combined_arithmetic_bill"],
        "m212_residual_s": trace["m212_residual_s"],
        "m231_residual_s": trace["m231_residual_s"],
        "combined_residual_s": trace["combined_residual_s"],
        "hostile": trace["hostile_five_x_effective_component"],
        "matmul_calls": trace["matmul_calls"],
        "matmul_bill": trace["matmul_bill"],
        "arange_calls": operations.get("arange", {}).get("calls", -1),
        "broadcast_calls": operations.get("broadcast_to", {}).get("calls", -1),
        "permuted_calls": operations.get("random.Generator.permuted", {}).get("calls", -1),
        "gather_calls": operations.get("take_along_axis", {}).get("calls", -1),
        "multiply_calls": operations.get("multiply", {}).get("calls", -1),
        "add_calls": operations.get("add", {}).get("calls", -1),
        "sum_calls": operations.get("sum", {}).get("calls", -1),
        "copy_calls": operations.get("copyto", {}).get("calls", -1),
        "argsort_calls": operations.get("argsort", {}).get("calls", 0),
        "reshape_calls": operations.get("reshape", {}).get("calls", 0),
        "peak_working_set_mib": payload["rss"]["peak_working_set_mib"],
        "incremental_persistent_mib": trace["allocation"]["incremental_persistent_mib"],
        "incremental_nominal_peak_mib": trace["allocation"]["incremental_nominal_peak_mib"],
        "combined_persistent_mib": trace["allocation"]["m212_m231_persistent_mib"],
        "aabb_max_asymmetry": trace["aabb_max_asymmetry"],
        "runtime": payload["runtime"],
    }


def aggregate() -> dict[str, object]:
    rows = [
        _row(
            json.loads(
                (HERE / f"M231_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")
            )
        )
        for seed in SEEDS
    ]
    hostile = np.asarray([row["hostile"] for row in rows], dtype=np.float64)
    combined_residual = np.asarray(
        [row["combined_residual_s"] for row in rows], dtype=np.float64
    )
    m231_residual = np.asarray(
        [row["m231_residual_s"] for row in rows], dtype=np.float64
    )
    gates = {
        "five_frozen_fresh_processes": len(rows) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in rows),
        "pinned_runtime_hashes": all(row["runtime_hashes_match"] for row in rows),
        "flopscope_0_10_0": all(
            row["runtime"]["flopscope"].split("+", 1)[0] == "0.10.0" for row in rows
        ),
        "constant_exact_m231_bill": all(row["m231_bill"] == EXPECTED_M231_BILL for row in rows),
        "constant_exact_combined_bill": all(
            row["combined_arithmetic_bill"] == EXPECTED_COMBINED_BILL for row in rows
        ),
        "exact_selector_calls": all(
            row["arange_calls"] == 1
            and row["broadcast_calls"] == 1
            and row["permuted_calls"] == 1
            and row["gather_calls"] == 1
            and row["argsort_calls"] == 0
            for row in rows
        ),
        "exact_two_matmul_calls": all(row["matmul_calls"] == 2 for row in rows),
        "exact_matmul_bill": all(row["matmul_bill"] == EXPECTED_MATMUL_BILL for row in rows),
        "exact_pointwise_calls": all(
            row["multiply_calls"] == 16
            and row["add_calls"] == 9
            and row["sum_calls"] == 1
            and row["copy_calls"] == 1
            for row in rows
        ),
        "zero_reshape_calls": all(row["reshape_calls"] == 0 for row in rows),
        "persistent_memory_ledger": all(
            row["incremental_persistent_mib"] == 36.873046875
            and row["incremental_nominal_peak_mib"] == 36.875
            and row["combined_persistent_mib"] == 138.955078125
            for row in rows
        ),
        "rss_below_512_mib": all(row["peak_working_set_mib"] <= 512.0 for row in rows),
        "aabb_symmetry": all(row["aabb_max_asymmetry"] <= 2e-10 for row in rows),
        "m231_wall_cap": bool(np.all(m231_residual <= 0.002025121700262334)),
        "combined_hostile_five_x_fits": bool(np.all(hostile <= CAP)),
    }
    passed = all(gates.values())
    return {
        "candidate": "M231 exact permuted row receipt for M227 algebra",
        "status": (
            "NATIVE_COMPONENT_PASS_G0_AUTHORIZED_NO_REPLACEMENT_CREDIT"
            if passed
            else "KILLED_FROZEN_NATIVE_RESOURCE_OR_LEDGER_GATE"
        ),
        "firewall": "generated-only response-free native audit",
        "mechanism": "one exact per-layer permuted integer receipt; exact live B/p/rho; k32 HT t/A/E/D",
        "replacement_credit": "denied; no integrated ABI retirement trace exists",
        "records": rows,
        "aggregate": {
            "m231_bill": EXPECTED_M231_BILL,
            "combined_arithmetic_bill": EXPECTED_COMBINED_BILL,
            "combined_residual_mean_ms": float(1e3 * np.mean(combined_residual)),
            "combined_residual_max_ms": float(1e3 * np.max(combined_residual)),
            "m231_residual_max_ms": float(1e3 * np.max(m231_residual)),
            "hostile_max": float(np.max(hostile)),
            "hostile_margin_min": float(CAP - np.max(hostile)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in rows)),
        },
        "gates": gates,
        "g0_authorized": passed,
        "credit": "native component only; no compiler retirement, source result, MSE, score, submission, or winner",
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M231_NATIVE_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
