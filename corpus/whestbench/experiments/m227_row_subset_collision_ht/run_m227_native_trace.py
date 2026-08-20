"""Fresh-process generated-only native trace for frozen M227."""

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
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m209_flopscope_sidecar import LayerInput  # noqa: E402
from run_m210_native_trace import digest_arrays, process_memory  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
from m227_flopscope_sidecar import (  # noqa: E402
    allocate_row_workspace,
    allocation_ledger,
    issue_full_domain_receipt,
    subtract_row_sketch_inplace,
)


WIDTH = 256
LAYERS = 31
DEPTH = 3
SUBSET_ROWS = 32
EPOCH = 227
EXPECTED_M212_BILL = 1_249_253_376
EXPECTED_M227_BILL = 865_484_288
EXPECTED_COMBINED_BILL = 2_114_737_664
EXPECTED_MATMUL_BILL = 767_950_848
COMBINED_EFFECTIVE_CAP = 3_727_757_440
M227_WALL_CAP_S = 0.002024139684262334


def generated_records(seed: int) -> list[LayerInput]:
    rng = np.random.Generator(np.random.Philox(int(seed)))
    he = math.sqrt(2.0 / WIDTH)
    return [
        LayerInput(
            layer=layer + 1,
            weight=rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he,
            factor=rng.standard_normal(WIDTH, dtype=np.float64) / math.sqrt(WIDTH),
            producer_epoch=EPOCH,
        )
        for layer in range(LAYERS)
    ]


def run_trace(records: list[LayerInput], *, seed: int) -> dict[str, object]:
    setup_budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    correction_budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    failure = None
    outputs = None
    allocation = None
    started = time.perf_counter()
    correction_wall = float("nan")
    row_receipt = None
    try:
        with setup_budget:
            staged = m212.allocate_staged_inputs()
            base = m212.allocate_workspace(depth=DEPTH)
            m212.stage_inputs(records, staged, expected_epoch=EPOCH)
            full_outputs = m212.compile_staged_stack(staged, base, depth=DEPTH)
        full_receipt = issue_full_domain_receipt(staged, base, full_outputs)

        correction_started = time.perf_counter()
        with correction_budget:
            row_workspace = allocate_row_workspace()
            allocation = allocation_ledger(staged, base, row_workspace)
            outputs, row_receipt = subtract_row_sketch_inplace(
                staged,
                base,
                row_workspace,
                full_receipt,
                seed=int(seed) ^ 0x227A011,
                subset_rows=SUBSET_ROWS,
            )
        correction_wall = time.perf_counter() - correction_started
        arrays = tuple(np.asarray(value) for value in outputs)
        if not all(np.all(np.isfinite(value)) for value in arrays):
            raise ArithmeticError("nonfinite M227 strict source")
        asymmetry = float(np.max(np.abs(arrays[2] - np.swapaxes(arrays[2], 1, 2))))
        if asymmetry > 2.0e-10:
            raise ArithmeticError("M227 aabb exceeded the frozen symmetry tolerance")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"

    operations = correction_budget.summary_dict().get("operations", {})
    matmul = operations.get("matmul", {})
    setup_bill = int(setup_budget.flops_used)
    m227_bill = int(correction_budget.flops_used)
    setup_residual = float(setup_budget.residual_wall_time_s or 0.0)
    m227_residual = float(correction_budget.residual_wall_time_s or 0.0)
    combined_bill = setup_bill + m227_bill
    combined_residual = setup_residual + m227_residual
    hostile = combined_bill + 5.0e11 * combined_residual
    arrays = tuple(np.asarray(value) for value in outputs) if outputs is not None else ()
    return {
        "failure": failure,
        "finite": failure is None,
        "seed": int(seed),
        "m212_bill": setup_bill,
        "m227_bill": m227_bill,
        "combined_arithmetic_bill": combined_bill,
        "m212_residual_s": setup_residual,
        "m227_residual_s": m227_residual,
        "combined_residual_s": combined_residual,
        "correction_wall_s": correction_wall,
        "whole_process_wall_s": time.perf_counter() - started,
        "hostile_five_x_effective_component": hostile,
        "combined_effective_cap": COMBINED_EFFECTIVE_CAP,
        "operations": operations,
        "matmul_calls": int(matmul.get("calls", -1)),
        "matmul_bill": int(matmul.get("flop_cost", -1)),
        "allocation": allocation,
        "aabb_max_asymmetry": (
            float(np.max(np.abs(arrays[2] - np.swapaxes(arrays[2], 1, 2))))
            if arrays
            else None
        ),
        "selected_row_count": (
            int(np.asarray(row_receipt.selected).shape[1])
            if row_receipt is not None
            else None
        ),
        "output_sha256": digest_arrays(outputs) if outputs is not None else None,
        "prediction_match": {
            "m212_bill": setup_bill == EXPECTED_M212_BILL,
            "m227_bill": m227_bill == EXPECTED_M227_BILL,
            "combined_bill": combined_bill == EXPECTED_COMBINED_BILL,
            "matmul_calls": int(matmul.get("calls", -1)) == 2,
            "matmul_bill": int(matmul.get("flop_cost", -1)) == EXPECTED_MATMUL_BILL,
            "reshape_calls": int(operations.get("reshape", {}).get("calls", 0)) == 0,
            "m227_wall_fits": m227_residual <= M227_WALL_CAP_S,
            "combined_hostile_five_x_fits": hostile <= COMBINED_EFFECTIVE_CAP,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = run_trace(generated_records(args.seed), seed=args.seed)
    payload = {
        "status": "M227_GENERATED_ROW_HT_NATIVE_TRACE_ONLY",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "runtime": {"flopscope": flops.__version__, "numpy": np.__version__},
        "seed": int(args.seed),
        "width": WIDTH,
        "layers": LAYERS,
        "subset_rows": SUBSET_ROWS,
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
                "m227_bill": trace["m227_bill"],
                "combined_residual_s": trace["combined_residual_s"],
                "hostile": trace["hostile_five_x_effective_component"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
