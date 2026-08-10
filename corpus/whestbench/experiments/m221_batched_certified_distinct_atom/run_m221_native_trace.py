"""Emit one fresh-process M221 native trace as JSON.

The generated packed context and independent NumPy recurrence are prepared
outside the timed FlopScope region.  The billed run itself includes all staged
allocations, copies, guards, recurrence work, output extraction, and measured
wall residual described by the frozen M221 declaration.
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

import m221_batched_certified_distinct_atom as core
import m221_flopscope_sidecar as native


EVENT_COUNT = 3968
PREDICTED_BILL = 21_760_512
PREDICTED_ALLOCATION_BYTES = 11_911_936
M216_BEST_WALL_S = 1.6133916999970097
RAW_WALL_STRICT_MAX_S = 0.016133916999970098
LAMBDA_FLOPS_PER_SECOND = 100_000_000_000.0
HOSTILE_WALL_FACTOR = 5.0
COMPONENT_CEILING = 6_824_272_176
RSS_MAX_BYTES = 536_870_912


def trace(seed: int) -> dict[str, object]:
    packed = native.generated_native_batch(seed)
    expected = core.evaluate_numpy(packed)
    result = native.run_billed_batch(packed)

    value = np.asarray(result.pop("value"), dtype=np.float64)
    radius = np.asarray(result.pop("radius"), dtype=np.float64)
    chart_ok = np.asarray(result.pop("chart_ok"), dtype=bool)
    expected_ok = np.asarray(expected.chart_ok, dtype=bool)
    joint_ok = chart_ok & expected_ok

    if np.any(joint_ok):
        value_error = float(np.max(np.abs(value[joint_ok] - expected.value[joint_ok])))
        radius_error = float(np.max(np.abs(radius[joint_ok] - expected.radius[joint_ok])))
        enclosure_ratio = float(
            np.max(
                np.abs(value[joint_ok] - expected.value[joint_ok])
                / np.maximum(radius[joint_ok], np.finfo(np.float64).tiny)
            )
        )
    else:
        value_error = math.inf
        radius_error = math.inf
        enclosure_ratio = math.inf

    billed = int(result["billed_flops"])
    wall = float(result["wall_s"])
    residual = float(result["residual_wall_s"])
    allocation_detail = result.pop("allocation") or {}
    allocation_bytes = int(allocation_detail.get("total_bytes", -1))
    hostile_component = billed + LAMBDA_FLOPS_PER_SECOND * HOSTILE_WALL_FACTOR * residual
    raw_speedup = M216_BEST_WALL_S / wall if wall > 0.0 else math.inf
    fallback_count = int(result["fallback_count"])
    expected_fallback_count = int(np.count_nonzero(~expected_ok))
    chart_mismatch_count = int(np.count_nonzero(chart_ok != expected_ok))

    checks = {
        "no_exception": result["failure"] is None,
        "event_count_exact": int(result["event_count"]) == EVENT_COUNT,
        "bill_exact": billed == PREDICTED_BILL,
        "allocation_exact": allocation_bytes == PREDICTED_ALLOCATION_BYTES,
        "fallback_zero": fallback_count == 0,
        "chart_matches_numpy": chart_mismatch_count == 0,
        "values_inside_returned_radius": enclosure_ratio <= 1.0,
        "raw_speedup_strictly_over_100x": raw_speedup > 100.0 and wall < RAW_WALL_STRICT_MAX_S,
        "hostile_component_within_ceiling": hostile_component <= COMPONENT_CEILING,
        "rss_within_ceiling": int(result["rss_bytes"]) <= RSS_MAX_BYTES,
    }
    execution_gate_pass = all(checks.values())

    result.update(
        {
            "seed": int(seed),
            "predicted_bill": PREDICTED_BILL,
            "predicted_allocation_bytes": PREDICTED_ALLOCATION_BYTES,
            "allocation_bytes": allocation_bytes,
            "allocation_ledger": {
                "staged_columns": int(allocation_detail.get("staged_columns", -1)),
                "staged_bytes": int(allocation_detail.get("staged_bytes", -1)),
                "workspace_buffers": int(allocation_detail.get("workspace_buffers", -1)),
                "workspace_bytes": int(allocation_detail.get("workspace_bytes", -1)),
                "unlisted_user_temporaries": int(
                    allocation_detail.get("unlisted_user_temporaries", -1)
                ),
                "total_bytes": allocation_bytes,
            },
            "expected_fallback_count": expected_fallback_count,
            "chart_mismatch_count": chart_mismatch_count,
            "value_parity_max_abs": value_error,
            "radius_parity_max_abs": radius_error,
            "value_parity_enclosure_ratio": enclosure_ratio,
            "raw_speedup_vs_m216": raw_speedup,
            "raw_wall_strict_max_s": RAW_WALL_STRICT_MAX_S,
            "hostile_component": hostile_component,
            "component_ceiling": COMPONENT_CEILING,
            "checks": checks,
            "execution_gate_pass": execution_gate_pass,
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    print(json.dumps(trace(args.seed), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
