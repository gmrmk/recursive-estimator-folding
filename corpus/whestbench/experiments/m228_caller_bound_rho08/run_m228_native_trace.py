"""Emit one isolated fresh-process trace for M228's bound-only kernel."""

from __future__ import annotations

import argparse
import gc
import json
import math

import numpy as np

import m228_caller_bound_rho08 as m228


EVENT_COUNT = 3968
PREDICTED_BILL = 21_693_056
PREDICTED_SETUP_BYTES = 8_515_328
PREDICTED_CALLS = 171
RSS_MAX_BYTES = 536_870_912


def trace(seed: int) -> dict[str, object]:
    packed = m228.generated_native_batch(seed)
    expected = m228.core.evaluate_numpy(packed)
    bound, caller_setup = m228.caller_owned_inputs(packed)
    audit_kernel = m228.PersistentKernel(packed.size)
    audit_kernel.bind(bound)
    allocation_audit = m228.measure_bound_kernel_allocation(audit_kernel)
    del audit_kernel
    gc.collect()
    kernel = m228.PersistentKernel(packed.size)
    kernel.bind(bound)
    report = m228.run_billed_bound_kernel(kernel)

    value = report.pop("value")
    radius = report.pop("radius")
    chart_ok = report.pop("chart_ok")
    joint_ok = chart_ok & expected.chart_ok
    if np.any(joint_ok):
        value_error = float(np.max(np.abs(value[joint_ok] - expected.value[joint_ok])))
        radius_error = float(np.max(np.abs(radius[joint_ok] - expected.radius[joint_ok])))
        enclosure_ratio = float(np.max(np.abs(value[joint_ok] - expected.value[joint_ok]) / np.maximum(expected.radius[joint_ok], np.finfo(np.float64).tiny)))
    else:
        value_error = radius_error = enclosure_ratio = math.inf
    operation_calls = {name: int(row["calls"]) for name, row in report["operations"].items()}
    wall = float(report["wall_s"])
    billed = int(report["billed_flops"])
    hostile_component = billed + 500_000_000_000.0 * float(report["residual_wall_s"])
    chart_mismatch = int(np.count_nonzero(chart_ok != expected.chart_ok))
    forbidden_seen = sorted(name for name in m228.FORBIDDEN_OPERATIONS if name in operation_calls)
    checks = {
        "no_exception": report["failure"] is None,
        "event_count_exact": int(report["event_count"]) == EVENT_COUNT,
        "bill_exact": billed == PREDICTED_BILL,
        "persistent_setup_exact": int(report["allocation"]["persistent_total_bytes"]) == PREDICTED_SETUP_BYTES,
        "runtime_calls_exact": sum(operation_calls.values()) == PREDICTED_CALLS,
        "forbidden_operations_absent": not forbidden_seen,
        "allocation_audit_completed": bool(allocation_audit["runtime_allocation_measured"]),
        "persistent_slab_stable": bool(report["allocation"]["persistent_slab_fingerprint_stable"]),
        "fallback_zero": int(report["fallback_count"]) == 0,
        "chart_matches_m224": chart_mismatch == 0,
        "values_inside_m224_radius": enclosure_ratio <= 1.0,
        "radius_parity": radius_error <= 1.0e-20,
        "raw_speedup_strictly_over_100x": m228.M216_BEST_WALL_S / wall > 100.0 and wall < m228.RAW_WALL_STRICT_MAX_S,
        "hostile_component_within_ceiling": hostile_component <= m228.COMPONENT_CEILING,
        "rss_within_ceiling": int(report["rss_bytes"]) <= RSS_MAX_BYTES,
    }
    report.update({
        "seed": int(seed), "caller_setup": caller_setup, "allocation_audit": allocation_audit, "predicted_bill": PREDICTED_BILL,
        "runtime_calls": sum(operation_calls.values()),
        "operation_calls": operation_calls, "forbidden_operations_seen": forbidden_seen,
        "chart_mismatch_count": chart_mismatch, "value_parity_max_abs": value_error,
        "radius_parity_max_abs": radius_error, "value_parity_enclosure_ratio": enclosure_ratio,
        "raw_speedup_vs_m216": m228.M216_BEST_WALL_S / wall if wall > 0.0 else math.inf,
        "raw_wall_strict_max_s": m228.RAW_WALL_STRICT_MAX_S,
        "hostile_component": hostile_component, "component_ceiling": m228.COMPONENT_CEILING,
        "checks": checks, "execution_gate_pass": all(checks.values()),
    })
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, type=int)
    print(json.dumps(trace(parser.parse_args().seed), sort_keys=True, separators=(",", ":")))
