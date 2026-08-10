"""Aggregate the five frozen M227 fresh-process traces without retuning."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEEDS = (227700001, 227700002, 227700003, 227700004, 227700005)
EXPECTED_M227_BILL = 865_484_288
EXPECTED_COMBINED_BILL = 2_114_737_664
EXPECTED_MATMUL_BILL = 767_950_848
CAP = 3_727_757_440


def _row(payload: dict[str, object]) -> dict[str, object]:
    trace = payload["trace"]
    operations = trace["operations"]
    return {
        "seed": int(payload["seed"]),
        "failure": trace["failure"],
        "finite": trace["finite"],
        "m212_bill": trace["m212_bill"],
        "m227_bill": trace["m227_bill"],
        "combined_arithmetic_bill": trace["combined_arithmetic_bill"],
        "m212_residual_s": trace["m212_residual_s"],
        "m227_residual_s": trace["m227_residual_s"],
        "combined_residual_s": trace["combined_residual_s"],
        "hostile": trace["hostile_five_x_effective_component"],
        "matmul_calls": trace["matmul_calls"],
        "matmul_bill": trace["matmul_bill"],
        "multiply_calls": operations.get("multiply", {}).get("calls", -1),
        "add_calls": operations.get("add", {}).get("calls", -1),
        "sum_calls": operations.get("sum", {}).get("calls", -1),
        "copy_calls": operations.get("copyto", {}).get("calls", -1),
        "argsort_calls": operations.get("argsort", {}).get("calls", -1),
        "gather_calls": operations.get("take_along_axis", {}).get("calls", -1),
        "reshape_calls": operations.get("reshape", {}).get("calls", 0),
        "peak_working_set_mib": payload["rss"]["peak_working_set_mib"],
        "incremental_persistent_mib": trace["allocation"]["incremental_persistent_mib"],
        "combined_persistent_mib": trace["allocation"]["m212_m227_persistent_mib"],
        "runtime": payload["runtime"],
    }


def aggregate() -> dict[str, object]:
    rows = [
        _row(
            json.loads(
                (HERE / f"M227_NATIVE_TRACE_{seed}.json").read_text(encoding="utf-8")
            )
        )
        for seed in SEEDS
    ]
    hostile = np.asarray([row["hostile"] for row in rows], dtype=np.float64)
    combined_residual = np.asarray(
        [row["combined_residual_s"] for row in rows], dtype=np.float64
    )
    m227_residual = np.asarray(
        [row["m227_residual_s"] for row in rows], dtype=np.float64
    )
    gates = {
        "five_frozen_fresh_processes": len(rows) == 5,
        "finite_no_failures": all(row["finite"] and row["failure"] is None for row in rows),
        "flopscope_0_10_0": all(
            row["runtime"]["flopscope"].split("+", 1)[0] == "0.10.0" for row in rows
        ),
        "constant_exact_m227_bill": all(row["m227_bill"] == EXPECTED_M227_BILL for row in rows),
        "constant_exact_combined_bill": all(
            row["combined_arithmetic_bill"] == EXPECTED_COMBINED_BILL for row in rows
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
        "exact_selector_calls": all(
            row["argsort_calls"] == 1 and row["gather_calls"] == 1 for row in rows
        ),
        "zero_reshape_calls": all(row["reshape_calls"] == 0 for row in rows),
        "persistent_memory_ledger": all(
            row["incremental_persistent_mib"] == 36.873046875
            and row["combined_persistent_mib"] == 138.955078125
            for row in rows
        ),
        "rss_below_512_mib": all(row["peak_working_set_mib"] <= 512.0 for row in rows),
        "m227_wall_cap": bool(np.all(m227_residual <= 0.002024139684262334)),
        "combined_hostile_five_x_fits": bool(np.all(hostile <= CAP)),
    }
    passed = all(gates.values())
    return {
        "candidate": "M227 exact-integrated row HT collision subtraction",
        "status": (
            "NATIVE_COMPONENT_PASS_G0_AUTHORIZED_NO_REPLACEMENT_CREDIT"
            if passed
            else "KILLED_FROZEN_NATIVE_RESOURCE_OR_LEDGER_GATE"
        ),
        "firewall": "generated-only response-free native audit",
        "mechanism": "exact live B/p/rho plus one shared k=32 HT subset for t/A/E/D",
        "replacement_credit": "denied; no integrated ABI retirement trace exists",
        "records": rows,
        "aggregate": {
            "m227_bill": EXPECTED_M227_BILL,
            "combined_arithmetic_bill": EXPECTED_COMBINED_BILL,
            "combined_residual_mean_ms": float(1e3 * np.mean(combined_residual)),
            "combined_residual_max_ms": float(1e3 * np.max(combined_residual)),
            "m227_residual_max_ms": float(1e3 * np.max(m227_residual)),
            "hostile_max": float(np.max(hostile)),
            "hostile_margin_min": float(CAP - np.max(hostile)),
            "peak_rss_mib": float(max(row["peak_working_set_mib"] for row in rows)),
        },
        "gates": gates,
        "g0_authorized": passed,
        "credit": "native component only; no source variance, MSE, score, submission, or winner",
    }


if __name__ == "__main__":
    result = aggregate()
    output = HERE / "M227_NATIVE_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"], "gates": result["gates"]}, sort_keys=True))
