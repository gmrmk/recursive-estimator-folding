"""Fresh-process generated-only native trace for frozen M215."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

import flopscope as flops
import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m209_batched_recursive_gram_control",
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m209_flopscope_sidecar import LayerInput  # noqa: E402
from run_m210_native_trace import digest_arrays, process_memory  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
from m215_flopscope_sidecar import (  # noqa: E402
    allocate_collision_workspace,
    allocation_ledger,
    issue_full_domain_receipt,
    subtract_collisions_inplace,
)


WIDTH = 256
LAYERS = 31
DEPTH = 3
EXPECTED_BILL = 5_446_508_544
EXPECTED_MATMUL_BILL = 5_320_548_352
EXPECTED_RESHAPE_BILL = 16_252_928
INCREMENTAL_EFFECTIVE_CAP = 6_824_272_176


def generated_records(seed: int) -> list[LayerInput]:
    rng = np.random.Generator(np.random.Philox(int(seed)))
    he = math.sqrt(2.0 / WIDTH)
    return [
        LayerInput(
            layer=layer + 1,
            weight=rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he,
            factor=rng.standard_normal(WIDTH, dtype=np.float64) / math.sqrt(WIDTH),
            producer_epoch=215,
        )
        for layer in range(LAYERS)
    ]


def run_trace(records: list[LayerInput]) -> dict[str, object]:
    setup_budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    failure = None
    outputs = None
    allocation = None
    started = time.perf_counter()
    try:
        with setup_budget:
            staged = m212.allocate_staged_inputs()
            base_workspace = m212.allocate_workspace(depth=DEPTH)
            m212.stage_inputs(records, staged, expected_epoch=215)
            full_outputs = m212.compile_staged_stack(staged, base_workspace, depth=DEPTH)
        receipt = issue_full_domain_receipt(staged, base_workspace, full_outputs)

        budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        correction_started = time.perf_counter()
        with budget:
            collision_workspace = allocate_collision_workspace()
            allocation = allocation_ledger(staged, base_workspace, collision_workspace)
            outputs = subtract_collisions_inplace(
                staged,
                base_workspace,
                collision_workspace,
                receipt,
                depth=DEPTH,
            )
        correction_wall = time.perf_counter() - correction_started
        arrays = tuple(np.asarray(value) for value in outputs)
        if not all(np.all(np.isfinite(value)) for value in arrays):
            raise ArithmeticError("nonfinite M215 strict-distinct output")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        if "budget" not in locals():
            budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        correction_wall = float("nan")

    operations = budget.summary_dict().get("operations", {})
    matmul = operations.get("matmul", {})
    reshape = operations.get("reshape", {})
    bill = int(budget.flops_used)
    residual = float(budget.residual_wall_time_s or 0.0)
    hostile = bill + 5.0e11 * residual
    arrays = tuple(np.asarray(value) for value in outputs) if outputs is not None else ()
    asymmetry = (
        float(np.max(np.abs(arrays[2] - np.swapaxes(arrays[2], 1, 2))))
        if arrays
        else None
    )
    return {
        "failure": failure,
        "finite": failure is None,
        "billed_flops": bill,
        "residual_s": residual,
        "correction_wall_s": correction_wall,
        "whole_process_wall_s": time.perf_counter() - started,
        "setup_m212_bill": int(setup_budget.flops_used),
        "combined_arithmetic_bill": int(setup_budget.flops_used) + bill,
        "matmul_calls": int(matmul.get("calls", -1)),
        "matmul_bill": int(matmul.get("flop_cost", -1)),
        "reshape_calls": int(reshape.get("calls", -1)),
        "reshape_bill": int(reshape.get("flop_cost", -1)),
        "operations": operations,
        "allocation": allocation,
        "aabb_max_asymmetry": asymmetry,
        "output_sha256": digest_arrays(outputs) if outputs is not None else None,
        "prediction_match": {
            "inclusive_bill": bill == EXPECTED_BILL,
            "matmul_calls": int(matmul.get("calls", -1)) == 5,
            "matmul_bill": int(matmul.get("flop_cost", -1)) == EXPECTED_MATMUL_BILL,
            "reshape_calls": int(reshape.get("calls", -1)) == 4,
            "reshape_bill": int(reshape.get("flop_cost", -1)) == EXPECTED_RESHAPE_BILL,
            "hostile_five_x_fits": hostile <= INCREMENTAL_EFFECTIVE_CAP,
        },
        "incremental_effective_cap": INCREMENTAL_EFFECTIVE_CAP,
        "raw_margin_after_correction": INCREMENTAL_EFFECTIVE_CAP - bill,
        "hostile_five_x_effective_component": hostile,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = run_trace(generated_records(args.seed))
    payload = {
        "status": "M215_GENERATED_COLLISION_CORRECTION_RESOURCE_TRACE_ONLY",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "runtime": {"flopscope": flops.__version__, "numpy": np.__version__},
        "seed": int(args.seed),
        "width": WIDTH,
        "layers": LAYERS,
        "depth": DEPTH,
        "trace": trace,
        "rss": process_memory(),
    }
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "failure": trace["failure"],
                "billed_flops": trace["billed_flops"],
                "residual_s": trace["residual_s"],
                "hostile": trace["hostile_five_x_effective_component"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
