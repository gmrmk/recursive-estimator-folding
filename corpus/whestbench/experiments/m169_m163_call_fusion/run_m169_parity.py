"""Algebra and bitwise parity checks against the frozen M164/M163 schedule."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

HERE = Path(__file__).resolve().parent
M164 = HERE.parent / "m164_staged_audit"
if str(M164) not in sys.path:
    sys.path.insert(0, str(M164))

from m164_flopscope_sidecar import allocate_workspace as allocate_m164_workspace  # noqa: E402
from m164_flopscope_sidecar import compile_layer as compile_m164_layer  # noqa: E402
from m169_fused_compiler import (  # noqa: E402
    COLLISION_MASS,
    allocate_staged_inputs,
    allocate_workspace,
    compile_staged_stack,
    initialize_target_q0,
    stage_inputs,
)
from run_m169_native_trace import generated_inputs  # noqa: E402


def _generated_inputs(width: int, layers: int, seed: int):
    if (width, layers) == (256, 31):
        return generated_inputs(seed)
    rng = np.random.default_rng(int(seed))
    weights, covariances = [], []
    for _ in range(layers):
        weight = rng.standard_normal((width, width), dtype=np.float64) * np.sqrt(2.0 / width)
        root = rng.standard_normal((width, width), dtype=np.float64) / np.sqrt(width)
        covariance = root @ root.T + 0.25 * np.eye(width)
        weights.append(weight)
        covariances.append(0.5 * (covariance + covariance.T))
    return weights, covariances


def parity(width: int, layers: int, seed: int) -> dict[str, object]:
    """Compare every layer output, not merely the final staged source."""

    weights_np, covariances_np = _generated_inputs(width, layers, seed)
    weights = [fnp.asarray(value, dtype=fnp.float64) for value in weights_np]
    covariances = [fnp.asarray(value, dtype=fnp.float64) for value in covariances_np]

    baseline = []
    baseline_budget = flops.BudgetContext(10**15, quiet=True)
    with baseline_budget:
        workspace = allocate_m164_workspace(width)
        for weight, covariance in zip(weights, covariances):
            outputs = compile_m164_layer(weight, covariance, workspace)[:3]
            baseline.append(tuple(np.asarray(value).copy() for value in outputs))

    fused_budget = flops.BudgetContext(10**15, quiet=True)
    with fused_budget:
        staged = allocate_staged_inputs(layers, width)
        workspace = allocate_workspace(layers, width)
        masses = fnp.asarray(np.array([COLLISION_MASS, 1.0 - COLLISION_MASS], dtype=np.float64), dtype=fnp.float64)
        initialize_target_q0(workspace, masses)
        stage_inputs(weights, covariances, staged)
        fused = compile_staged_stack(staged, workspace)[:3]
    fused_np = tuple(np.asarray(value) for value in fused)

    exact = True
    max_abs = 0.0
    mismatch_count = 0
    for layer, reference in enumerate(baseline):
        for component, expected in enumerate(reference):
            actual = fused_np[component][layer]
            equal = np.array_equal(expected, actual)
            exact = exact and equal
            mismatch_count += int(np.size(expected) - np.count_nonzero(expected == actual))
            max_abs = max(max_abs, float(np.max(np.abs(expected - actual))))
    return {
        "width": width,
        "layers": layers,
        "seed": seed,
        "reference": "frozen M164 sidecar / frozen M163 coefficients",
        "bitwise_equal": exact,
        "mismatch_elements": mismatch_count,
        "max_abs_difference": max_abs,
        "locked_tolerance": 0.0,
        "baseline_billed_flops": int(baseline_budget.flops_used),
        "fused_billed_flops": int(fused_budget.flops_used),
        "baseline_matmul_calls": int(baseline_budget.summary_dict()["operations"]["matmul"]["calls"]),
        "fused_matmul_calls": int(fused_budget.summary_dict()["operations"]["matmul"]["calls"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = parity(args.width, args.layers, args.seed)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
