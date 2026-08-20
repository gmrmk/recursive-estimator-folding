"""Emit one isolated fresh-process M226 target trace as compact JSON."""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

import m226_preallocated_fused_rho08 as m226


EVENT_COUNT = 3968
PREDICTED_BILL = 21_693_056
PREDICTED_SETUP_BYTES = 8_515_328
PREDICTED_CALLS = 171
M216_BEST_WALL_S = 1.6133916999970097
RAW_WALL_STRICT_MAX_S = 0.016133916999970098
COMPONENT_CEILING = 6_824_272_176
RSS_MAX_BYTES = 536_870_912
FORBIDDEN_OPERATIONS = ("empty", "copyto", "sum", "max", "reshape")


def trace(seed: int) -> dict[str, object]:
    packed = m226.generated_native_batch(seed)
    expected = m226.core.evaluate_numpy(packed)
    kernel = m226.PersistentKernel(packed.size)
    report = m226.run_billed_batch(packed, kernel)

    value = np.asarray(report.pop("value"), dtype=np.float64)
    radius = np.asarray(report.pop("radius"), dtype=np.float64)
    chart_ok = np.asarray(report.pop("chart_ok"), dtype=bool)
    joint_ok = chart_ok & expected.chart_ok
    if np.any(joint_ok):
        value_error = float(np.max(np.abs(value[joint_ok] - expected.value[joint_ok])))
        radius_error = float(np.max(np.abs(radius[joint_ok] - expected.radius[joint_ok])))
        enclosure_ratio = float(
            np.max(
                np.abs(value[joint_ok] - expected.value[joint_ok])
                / np.maximum(expected.radius[joint_ok], np.finfo(np.float64).tiny)
            )
        )
    else:
        value_error = math.inf
        radius_error = math.inf
        enclosure_ratio = math.inf

    operations = report["operations"]
    operation_calls = {name: int(row["calls"]) for name, row in operations.items()}
    total_calls = sum(operation_calls.values())
    forbidden_seen = sorted(name for name in FORBIDDEN_OPERATIONS if name in operations)
    billed = int(report["billed_flops"])
    wall = float(report["wall_s"])
    residual = float(report["residual_wall_s"])
    raw_speedup = M216_BEST_WALL_S / wall if wall > 0.0 else math.inf
    hostile_component = billed + 500_000_000_000.0 * residual
    allocation_bytes = int(report["allocation"]["total_bytes"])
    chart_mismatch = int(np.count_nonzero(chart_ok != expected.chart_ok))

    checks = {
        "no_exception": report["failure"] is None,
        "event_count_exact": int(report["event_count"]) == EVENT_COUNT,
        "bill_exact": billed == PREDICTED_BILL,
        "setup_allocation_exact": allocation_bytes == PREDICTED_SETUP_BYTES,
        "runtime_calls_exact": total_calls == PREDICTED_CALLS,
        "forbidden_operations_absent": not forbidden_seen,
        "runtime_allocation_zero": int(report["allocation"]["runtime_user_allocation_bytes"]) == 0,
        "fallback_zero": int(report["fallback_count"]) == 0,
        "chart_matches_m224": chart_mismatch == 0,
        "values_inside_m224_radius": enclosure_ratio <= 1.0,
        "radius_parity": radius_error <= 1.0e-20,
        "raw_speedup_strictly_over_100x": raw_speedup > 100.0 and wall < RAW_WALL_STRICT_MAX_S,
        "hostile_component_within_ceiling": hostile_component <= COMPONENT_CEILING,
        "rss_within_ceiling": int(report["rss_bytes"]) <= RSS_MAX_BYTES,
    }
    report.update(
        {
            "seed": int(seed),
            "predicted_bill": PREDICTED_BILL,
            "predicted_setup_bytes": PREDICTED_SETUP_BYTES,
            "allocation_bytes": allocation_bytes,
            "runtime_calls": total_calls,
            "operation_calls": operation_calls,
            "forbidden_operations_seen": forbidden_seen,
            "chart_mismatch_count": chart_mismatch,
            "value_parity_max_abs": value_error,
            "radius_parity_max_abs": radius_error,
            "value_parity_enclosure_ratio": enclosure_ratio,
            "raw_speedup_vs_m216": raw_speedup,
            "raw_wall_strict_max_s": RAW_WALL_STRICT_MAX_S,
            "hostile_component": hostile_component,
            "component_ceiling": COMPONENT_CEILING,
            "checks": checks,
            "execution_gate_pass": all(checks.values()),
        }
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    print(json.dumps(trace(args.seed), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
