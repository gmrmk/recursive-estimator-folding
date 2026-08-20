"""Aggregate the five predeclared M169 native resource traces without reruns."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from m169_fused_compiler import LAYERS, WIDTH, static_prediction


SEEDS = (169700001, 169700002, 169700003, 169700004, 169700005)


def linear_p99(values: list[float]) -> float:
    return float(np.quantile(np.asarray(values, dtype=np.float64), 0.99, method="linear"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prediction = static_prediction()
    records = []
    for seed in SEEDS:
        path = args.directory / f"M169_NATIVE_TRACE_{seed}.json"
        records.append(json.loads(path.read_text(encoding="utf-8")))

    traces = [record["trace"] for record in records]
    residuals = [float(trace["residual_s"]) for trace in traces]
    p99 = linear_p99(residuals)
    summary = {
        "candidate": "M169 frozen M163 two-axis batched call fusion",
        "status": "RESOURCE_CLOSED_NO_SOURCE_EFFICACY_RUN",
        "firewall": "only generated matrices were used; no response, source efficacy, network, truth, scorer, leaderboard, submission, or champion artifact was read or changed",
        "runtime": records[0]["runtime"],
        "width": WIDTH,
        "layers": LAYERS,
        "predeclared_prediction": prediction,
        "native_resource_runs": [
            {
                "seed": int(record["seed"]),
                "finite": bool(trace["finite"]),
                "matmul_calls": int(trace["matmul_calls"]),
                "billed_flops": int(trace["billed_flops"]),
                "residual_s": float(trace["residual_s"]),
                "five_x_combined_effective": float(trace["combined"]["combined_five_x_effective"]),
                "peak_working_set_mib": float(record["rss"]["peak_working_set_mib"]),
                "private_mib": float(record["rss"]["private_mib"]),
                "persistent_allocation": trace["allocation"],
                "prediction_match": trace["prediction_match"],
            }
            for record, trace in zip(records, traces, strict=True)
        ],
        "aggregate": {
            "bill_constant": len({int(trace["billed_flops"]) for trace in traces}) == 1,
            "residual_mean_ms": float(np.mean(residuals) * 1.0e3),
            "residual_p99_ms_linear": p99 * 1.0e3,
            "residual_max_ms": max(residuals) * 1.0e3,
            "peak_rss_mib": max(float(record["rss"]["peak_working_set_mib"]) for record in records),
            "peak_private_mib": max(float(record["rss"]["private_mib"]) for record in records),
            "resource_gate": {
                "five_fresh_expected_seeds": [int(record["seed"]) for record in records] == list(SEEDS),
                "finite": all(bool(trace["finite"]) for trace in traces),
                "exact_two_matmuls": all(int(trace["matmul_calls"]) == 2 for trace in traces),
                "exact_predeclared_bill": all(int(trace["billed_flops"]) == int(prediction["predicted_total_bill"]) for trace in traces),
                "all_pack_copy_and_no_reshape_match": all(all(bool(value) for value in trace["prediction_match"].values()) for trace in traces),
                "compiler_slot": all(bool(trace["combined"]["compiler_bill_fits_slot"]) for trace in traces),
                "rss_within_512_mib": all(float(record["rss"]["peak_working_set_mib"]) <= 512.0 for record in records),
                "every_hostile_5x_projection_within_100b": all(bool(trace["combined"]["combined_five_x_fits"]) for trace in traces),
                "p99_residual_within_predeclared_ms": p99 <= float(prediction["max_residual_s_each_for_hostile_5x"]),
            },
        },
        "exactness": {
            "small": json.loads((args.directory / "M169_PARITY_SMALL_20260807.json").read_text(encoding="utf-8")),
            "target": json.loads((args.directory / "M169_PARITY_TARGET_20260807.json").read_text(encoding="utf-8")),
        },
        "staging_disposition": "The fused compiler is valid only at an interface that already owns all 31 W/V arrays. It does not authorize a sequential covariance/source provider to reorder its state transitions. No external provider was inspected in this response-free pass.",
        "development_screen": {
            "executed": False,
            "reason": "This was a compiler/resource mutation only. No source efficacy, variance, p99, response, truth, or contest evaluation was opened."
        }
    }
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
