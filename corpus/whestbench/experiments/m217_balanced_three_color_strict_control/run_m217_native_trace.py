"""Fresh-process generated-only native trace for M217's frozen component."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
M210 = HERE.parent / "m210_level_fused_recursive_gram"
if str(M210) not in sys.path:
    sys.path.insert(0, str(M210))

from run_m210_native_trace import digest_arrays, process_memory  # noqa: E402
from m217_flopscope_sidecar import (  # noqa: E402
    ColoredLayerInput,
    allocate_staged_inputs,
    allocate_workspace,
    allocation_ledger,
    compile_staged_stack,
    stage_inputs,
)


WIDTH = 256
LAYERS = 31
DEPTH = 3
ARITHMETIC_CAP = 1_600_000_000
HOSTILE_CAP = 2_250_000_000
MEMORY_CAP = 512 * 1024 * 1024
EPOCH = 217


@dataclass(frozen=True)
class RawLayer:
    layer: int
    weight: np.ndarray
    factor: np.ndarray


def generated_layers(seed: int) -> list[RawLayer]:
    rng = np.random.default_rng(int(seed))
    he = math.sqrt(2.0 / WIDTH)
    return [
        RawLayer(
            layer=layer + 1,
            weight=rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he,
            factor=rng.uniform(0.01, 0.15, size=WIDTH).astype(np.float64),
        )
        for layer in range(LAYERS)
    ]


def run_trace(raw_layers: list[RawLayer], seed: int) -> dict[str, object]:
    sizes = (86, 85, 85)
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    outputs = None
    allocation = None
    try:
        with budget:
            generator = fnp.random.default_rng(int(seed) ^ 0x217C010)
            records = []
            for raw in raw_layers:
                permutation = generator.permutation(WIDTH)
                colors = [0] * WIDTH
                cut0, cut1 = sizes[0], sizes[0] + sizes[1]
                for position, label in enumerate(np.asarray(permutation)):
                    colors[int(label)] = 0 if position < cut0 else (1 if position < cut1 else 2)
                records.append(
                    ColoredLayerInput(
                        layer=raw.layer,
                        weight=raw.weight,
                        factor=raw.factor,
                        colors=colors,
                        producer_epoch=EPOCH,
                    )
                )
            staged = allocate_staged_inputs()
            workspace = allocate_workspace(depth=DEPTH)
            stage_inputs(records, staged, expected_epoch=EPOCH)
            allocation = allocation_ledger(staged, workspace)
            outputs = compile_staged_stack(staged, workspace, depth=DEPTH)
        arrays = tuple(np.asarray(value) for value in outputs)
        if not all(np.all(np.isfinite(value)) for value in arrays):
            raise ArithmeticError("nonfinite M217 output")
        if not np.array_equal(arrays[3], np.swapaxes(arrays[3], 2, 3)):
            raise ArithmeticError("class-local Gram lost mirrored symmetry")
        if not np.array_equal(arrays[2], np.swapaxes(arrays[2], 1, 2)):
            raise ArithmeticError("M217 aabb lost symmetry")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    operations = budget.summary_dict().get("operations", {})
    matmul = operations.get("matmul", {})
    reshape = operations.get("reshape", {})
    take = operations.get("take", {})
    permutation = operations.get("random.permutation", operations.get("permutation", {}))
    bill = int(budget.flops_used)
    residual = float(budget.residual_wall_time_s or 0.0)
    hostile = bill + 5.0e11 * residual
    peak = 0 if allocation is None else int(allocation["persistent_bytes"])
    return {
        "failure": failure,
        "finite": failure is None,
        "billed_flops": bill,
        "residual_s": residual,
        "wall_s": time.perf_counter() - started,
        "hostile_five_x_effective_component": hostile,
        "matmul_calls": int(matmul.get("calls", -1)),
        "matmul_bill": int(matmul.get("flop_cost", -1)),
        "reshape_calls": int(reshape.get("calls", -1)),
        "reshape_bill": int(reshape.get("flop_cost", -1)),
        "take_calls": int(take.get("calls", -1)),
        "take_bill": int(take.get("flop_cost", -1)),
        "permutation_calls": int(permutation.get("calls", -1)),
        "operations": operations,
        "allocation": allocation,
        "output_sha256": digest_arrays(outputs[:3]) if outputs is not None else None,
        "gates": {
            "finite": failure is None,
            "arithmetic": bill <= ARITHMETIC_CAP,
            "hostile_five_x": hostile <= HOSTILE_CAP,
            "memory": peak <= MEMORY_CAP,
            "matmul_calls": int(matmul.get("calls", -1)) == 4,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = run_trace(generated_layers(args.seed), args.seed)
    payload = {
        "status": "M217_GENERATED_RESOURCE_COMPONENT_TRACE_ONLY",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weights, leaderboard, submission, or champion access",
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
                "gates": trace["gates"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
