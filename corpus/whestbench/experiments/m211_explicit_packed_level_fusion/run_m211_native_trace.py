"""Fresh-process generated-only native resource trace for frozen M211."""

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
M210 = HERE.parent / "m210_level_fused_recursive_gram"
if str(M210) not in sys.path:
    sys.path.insert(0, str(M210))

from run_m210_native_trace import digest_arrays, process_memory  # noqa: E402
from m211_flopscope_sidecar import (  # noqa: E402
    LayerInput,
    allocate_staged_inputs,
    allocate_workspace,
    allocation_ledger,
    compile_staged_stack,
    stage_inputs,
)


WIDTH = 256
LAYERS = 31
DEPTH = 3
HEADROOM = 1_986_871_472


def generated_records(seed: int) -> list[LayerInput]:
    rng = np.random.default_rng(int(seed))
    he = math.sqrt(2.0 / WIDTH)
    return [
        LayerInput(
            layer=layer + 1,
            weight=rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he,
            factor=rng.standard_normal(WIDTH, dtype=np.float64) / math.sqrt(WIDTH),
            producer_epoch=211,
        )
        for layer in range(LAYERS)
    ]


def run_trace(records: list[LayerInput]) -> dict[str, object]:
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    outputs = None
    allocation = None
    try:
        with budget:
            staged = allocate_staged_inputs()
            workspace = allocate_workspace(depth=DEPTH)
            allocation = allocation_ledger(staged, workspace)
            stage_inputs(records, staged, expected_epoch=211)
            outputs = compile_staged_stack(staged, workspace, depth=DEPTH)
        arrays = tuple(np.asarray(value) for value in outputs)
        if not all(np.all(np.isfinite(value)) for value in arrays):
            raise ArithmeticError("nonfinite M211 output")
        if not np.array_equal(arrays[3], np.swapaxes(arrays[3], 1, 2)):
            raise ArithmeticError("M211 Gram lost exact mirrored symmetry")
        if not np.array_equal(arrays[2], np.swapaxes(arrays[2], 1, 2)):
            raise ArithmeticError("M211 aabb lost exact symmetry")
        if not all(
            item["c_contiguous"]
            for name, item in allocation["arrays"].items()
            if name.startswith("left_pack_") or name.startswith("right_pack_")
        ):
            raise ArithmeticError("M211 pack is not C-contiguous")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    summary = budget.summary_dict()
    operations = summary.get("operations", {})
    matmul = operations.get("matmul", {})
    reshape = operations.get("reshape", {})
    bill = int(budget.flops_used)
    residual = float(budget.residual_wall_time_s or 0.0)
    hostile = bill + 5.0e11 * residual
    return {
        "failure": failure,
        "finite": failure is None,
        "billed_flops": bill,
        "residual_s": residual,
        "wall_s": time.perf_counter() - started,
        "matmul_calls": int(matmul.get("calls", -1)),
        "matmul_bill": int(matmul.get("flop_cost", -1)),
        "reshape_calls": int(reshape.get("calls", -1)),
        "reshape_bill": int(reshape.get("flop_cost", -1)),
        "operations": operations,
        "allocation": allocation,
        "output_sha256": digest_arrays(outputs[:3]) if outputs is not None else None,
        "inclusive_below_frozen_upper_bound": bill < 1_350_000_000,
        "hostile_five_x_fits": hostile <= HEADROOM,
        "remaining_after_compiler": HEADROOM - bill,
        "hostile_five_x_effective_component": hostile,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = run_trace(generated_records(args.seed))
    payload = {
        "status": "M211_GENERATED_EXPLICIT_MEMORY_RESOURCE_TRACE_ONLY",
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
    print(json.dumps({
        "output": str(args.output),
        "failure": trace["failure"],
        "billed_flops": trace["billed_flops"],
        "residual_s": trace["residual_s"],
        "hostile": trace["hostile_five_x_effective_component"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
