"""Fresh-process generated-only target trace for frozen M218."""

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
    BASE / "m205_rankone_complete_physical_owner",
    BASE / "m209_batched_recursive_gram_control",
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m205_rankone_complete_physical_owner as m205  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402
from run_m210_native_trace import digest_arrays, process_memory  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
import m215_rankone_collision_correction as m215_numpy  # noqa: E402
from m215_flopscope_sidecar import issue_full_domain_receipt  # noqa: E402
from m218_flopscope_sidecar import (  # noqa: E402
    allocate_strassen_collision_workspace,
    allocation_ledger,
    subtract_collisions_strassen_inplace,
)


WIDTH = 256
LAYERS = 31
D_DEPTH = 3
EXPECTED_BILL = 4_622_180_352
EXPECTED_MATMUL_BILL = 4_328_611_840
EXPECTED_COPY_BILL = 85_089_792
EXPECTED_ADD_BILL = 95_232_000
EXPECTED_SUBTRACT_BILL = 27_934_720
EXPECTED_MULTIPLY_BILL = 65_011_712
EXPECTED_RESHAPE_BILL = 16_252_928
EXPECTED_SUM_BILL = 4_047_360
CAP = 6_824_272_176


def generated_records(seed: int) -> list[LayerInput]:
    rng = np.random.Generator(np.random.Philox(int(seed)))
    he = math.sqrt(2.0 / WIDTH)
    return [
        LayerInput(
            layer=layer + 1,
            weight=rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he,
            factor=rng.standard_normal(WIDTH, dtype=np.float64) / math.sqrt(WIDTH),
            producer_epoch=218,
        )
        for layer in range(LAYERS)
    ]


def _generated_m215_audit(records, outputs) -> dict[str, float | bool]:
    arrays = tuple(np.asarray(value) for value in outputs)
    max_error = 0.0
    max_reference = 0.0
    for layer, record in enumerate(records):
        full = m205.compile_lifted_rank_one_control(record.weight, record.factor)
        collision = m215_numpy.compile_rank_one_collision_source_numpy(
            record.weight, record.factor
        )
        reference = m215_numpy.subtract_source(full, collision)
        actual = m205.Source211(arrays[0][layer], arrays[1][layer], arrays[2][layer])
        max_error = max(max_error, m205.source_max_abs_difference(actual, reference))
        max_reference = max(
            max_reference,
            float(np.max(np.abs(reference.aaaa))),
            float(np.max(np.abs(reference.aaab))),
            float(np.max(np.abs(reference.aabb))),
        )
    threshold = 2e-9 * (1.0 + max_reference)
    return {
        "max_abs_error_vs_m215": max_error,
        "max_abs_m215_reference": max_reference,
        "frozen_threshold": threshold,
        "passes": max_error <= threshold,
    }


def run_trace(records: list[LayerInput]) -> dict[str, object]:
    setup_budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    failure = None
    outputs = None
    allocation = None
    resource_rss = None
    started = time.perf_counter()
    numerical = None
    try:
        with setup_budget:
            staged = m212.allocate_staged_inputs()
            base = m212.allocate_workspace(depth=D_DEPTH)
            m212.stage_inputs(records, staged, expected_epoch=218)
            full_outputs = m212.compile_staged_stack(staged, base, depth=D_DEPTH)
        receipt = issue_full_domain_receipt(staged, base, full_outputs)

        budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        correction_started = time.perf_counter()
        with budget:
            workspace = allocate_strassen_collision_workspace()
            allocation = allocation_ledger(staged, base, workspace)
            outputs = subtract_collisions_strassen_inplace(
                staged, base, workspace, receipt, d_depth=D_DEPTH
            )
        correction_wall = time.perf_counter() - correction_started
        resource_rss = process_memory()
        arrays = tuple(np.asarray(value) for value in outputs)
        if not all(np.all(np.isfinite(value)) for value in arrays):
            raise ArithmeticError("nonfinite M218 output")
        numerical = _generated_m215_audit(records, outputs)
        if not numerical["passes"]:
            raise ArithmeticError("M218 exceeded frozen M215 numerical drift gate")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        if "budget" not in locals():
            budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        correction_wall = float("nan")

    operations = budget.summary_dict().get("operations", {})
    get = lambda name: operations.get(name, {})
    bill = int(budget.flops_used)
    residual = float(budget.residual_wall_time_s or 0.0)
    hostile = bill + 5.0e11 * residual
    arrays = tuple(np.asarray(value) for value in outputs) if outputs is not None else ()
    asymmetry = (
        float(np.max(np.abs(arrays[2] - np.swapaxes(arrays[2], 1, 2))))
        if arrays
        else None
    )
    prediction = {
        "inclusive_bill": bill == EXPECTED_BILL,
        "matmul": int(get("matmul").get("calls", -1)) == 6
        and int(get("matmul").get("flop_cost", -1)) == EXPECTED_MATMUL_BILL,
        "copyto": int(get("copyto").get("calls", -1)) == 81
        and int(get("copyto").get("flop_cost", -1)) == EXPECTED_COPY_BILL,
        "add": int(get("add").get("calls", -1)) == 51
        and int(get("add").get("flop_cost", -1)) == EXPECTED_ADD_BILL,
        "subtract": int(get("subtract").get("calls", -1)) == 20
        and int(get("subtract").get("flop_cost", -1)) == EXPECTED_SUBTRACT_BILL,
        "multiply": int(get("multiply").get("calls", -1)) == 16
        and int(get("multiply").get("flop_cost", -1)) == EXPECTED_MULTIPLY_BILL,
        "reshape": int(get("reshape").get("calls", -1)) == 4
        and int(get("reshape").get("flop_cost", -1)) == EXPECTED_RESHAPE_BILL,
        "sum": int(get("sum").get("calls", -1)) == 1
        and int(get("sum").get("flop_cost", -1)) == EXPECTED_SUM_BILL,
        "hostile_five_x_fits": hostile <= CAP,
    }
    return {
        "failure": failure,
        "finite": failure is None,
        "billed_flops": bill,
        "residual_s": residual,
        "correction_wall_s": correction_wall,
        "whole_process_wall_s": time.perf_counter() - started,
        "setup_m212_bill": int(setup_budget.flops_used),
        "combined_arithmetic_bill": int(setup_budget.flops_used) + bill,
        "operations": operations,
        "allocation": allocation,
        "resource_rss_checkpoint": resource_rss,
        "numerical_audit": numerical,
        "aabb_max_asymmetry": asymmetry,
        "output_sha256": digest_arrays(outputs) if outputs is not None else None,
        "prediction_match": prediction,
        "incremental_effective_cap": CAP,
        "raw_remaining_for_other_unknowns": CAP - bill,
        "hostile_five_x_effective_component": hostile,
        "hostile_remaining_for_other_unknowns": CAP - hostile,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = run_trace(generated_records(args.seed))
    payload = {
        "status": "M218_GENERATED_SELECTIVE_L2_RESOURCE_TRACE_ONLY",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "runtime": {"flopscope": flops.__version__, "numpy": np.__version__},
        "seed": int(args.seed),
        "width": WIDTH,
        "layers": LAYERS,
        "strassen_depth": 2,
        "d_depth": D_DEPTH,
        "trace": trace,
        "rss_after_audit": process_memory(),
    }
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "failure": trace["failure"],
                "bill": trace["billed_flops"],
                "residual_s": trace["residual_s"],
                "hostile": trace["hostile_five_x_effective_component"],
                "max_error": (
                    trace["numerical_audit"]["max_abs_error_vs_m215"]
                    if trace["numerical_audit"] is not None
                    else None
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
