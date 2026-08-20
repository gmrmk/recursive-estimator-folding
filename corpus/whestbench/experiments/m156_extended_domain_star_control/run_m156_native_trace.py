"""Fresh-process, response-free native trace for the M156 compiler."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from m156_flopscope_sidecar import allocate_workspace, compile_layer


WIDTH = 256
LAYERS = 31
INHERITED_ENDPOINT = 85_980_878_800
STATIC_PROTECTED_COMPILER = 12_976_947_200


def generated_inputs(seed: int):
    rng = np.random.default_rng(int(seed))
    scale = math.sqrt(2.0 / WIDTH)
    weights = []
    covariances = []
    for _ in range(LAYERS):
        w = rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * scale
        root = rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) / math.sqrt(WIDTH)
        v = root @ root.T
        weights.append(fnp.asarray(w, dtype=fnp.float64))
        covariances.append(fnp.asarray(v, dtype=fnp.float64))
    return weights, covariances


def digest_arrays(arrays) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        digest.update(memoryview(np.ascontiguousarray(np.asarray(value))).cast("B"))
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=156_700_001)
    args = parser.parse_args()

    weights, covariances = generated_inputs(args.seed)
    workspace = allocate_workspace(WIDTH)
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    outputs = None
    try:
        with budget:
            for weight, covariance in zip(weights, covariances):
                outputs = compile_layer(weight, covariance, workspace)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    wall = time.perf_counter() - started

    summary = budget.summary_dict()
    matmul = summary.get("operations", {}).get("matmul", {})
    residual = float(budget.residual_wall_time_s or 0.0)
    bill = int(budget.flops_used)
    effective = bill + 1e11 * residual
    result = {
        "status": "M156_NATIVE_COMPILER_TRACE_ONLY_NO_EFFICACY",
        "firewall": "generated matrices only; no truth, scorer, contest row, response, submission, or champion mutation",
        "seed": int(args.seed),
        "runtime": {"flopscope": getattr(flops, "__version__", "unknown"), "numpy": np.__version__},
        "failure": failure,
        "width": WIDTH,
        "layers": LAYERS,
        "expected_matmul_calls": 5 * LAYERS,
        "measured_matmul_calls": int(matmul.get("calls", -1)),
        "billed_flops": bill,
        "residual_s": residual,
        "effective_compute": effective,
        "wall_s": wall,
        "output_finite": bool(outputs is not None and all(np.isfinite(np.asarray(x)).all() for x in outputs)),
        "output_sha256": digest_arrays(outputs) if outputs is not None else None,
        "inherited_endpoint_subtotal": INHERITED_ENDPOINT,
        "combined_actual_bill": INHERITED_ENDPOINT + bill,
        "combined_actual_effective_compute": INHERITED_ENDPOINT + effective,
        "static_protected_compiler": STATIC_PROTECTED_COMPILER,
        "combined_static_protected_bill": INHERITED_ENDPOINT + STATIC_PROTECTED_COMPILER,
        "remaining_to_100b_actual_bill": 100_000_000_000 - (INHERITED_ENDPOINT + bill),
        "remaining_to_100b_actual_effective": 100_000_000_000 - (INHERITED_ENDPOINT + effective),
        "flopscope_summary": summary,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "failure": failure,
        "matmul_calls": result["measured_matmul_calls"],
        "billed_flops": bill,
        "residual_s": residual,
        "combined_actual_effective_compute": result["combined_actual_effective_compute"],
        "remaining_to_100b_actual_effective": result["remaining_to_100b_actual_effective"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

