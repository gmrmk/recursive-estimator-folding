"""Fresh-process generated-only resource trace for frozen M209."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from m209_batched_recursive_gram_control import static_prediction
from m209_flopscope_sidecar import (
    DEPTH,
    LAYERS,
    WIDTH,
    LayerInput,
    allocate_staged_inputs,
    allocate_workspace,
    allocation_ledger,
    compile_staged_stack,
    stage_inputs,
)


STRICT_HEADROOM = 1_986_871_472


class _ProcessMemoryCountersEx(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def process_memory() -> dict[str, float]:
    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    if not psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    mib = 1024.0 * 1024.0
    return {
        "peak_working_set_mib": counters.PeakWorkingSetSize / mib,
        "working_set_mib": counters.WorkingSetSize / mib,
        "private_mib": counters.PrivateUsage / mib,
        "peak_pagefile_mib": counters.PeakPagefileUsage / mib,
    }


def generated_inputs(seed: int):
    rng = np.random.default_rng(int(seed))
    he = math.sqrt(2.0 / WIDTH)
    weights = [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he
        for _ in range(LAYERS)
    ]
    factors = [
        rng.standard_normal(WIDTH, dtype=np.float64) / math.sqrt(WIDTH)
        for _ in range(LAYERS)
    ]
    return weights, factors


def digest_arrays(arrays) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        digest.update(memoryview(np.ascontiguousarray(np.asarray(value))).cast("B"))
    return digest.hexdigest()


def run_trace(weights_np, factors_np) -> dict[str, object]:
    records = [
        LayerInput(layer=i + 1, weight=weight, factor=factor, producer_epoch=209)
        for i, (weight, factor) in enumerate(zip(weights_np, factors_np, strict=True))
    ]
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    outputs = None
    allocation = None
    try:
        with budget:
            staged = allocate_staged_inputs()
            workspace = allocate_workspace()
            allocation = allocation_ledger(staged, workspace)
            stage_inputs(records, staged, expected_epoch=209)
            outputs = compile_staged_stack(staged, workspace)
        arrays = tuple(np.asarray(value) for value in outputs)
        if not all(np.all(np.isfinite(value)) for value in arrays):
            raise ArithmeticError("nonfinite M209 output")
        if not np.array_equal(arrays[3], np.swapaxes(arrays[3], 1, 2)):
            raise ArithmeticError("Gram output lost exact mirrored symmetry")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    summary = budget.summary_dict()
    operations = summary.get("operations", {})
    matmul = operations.get("matmul", {})
    prediction = static_prediction()
    bill = int(budget.flops_used)
    residual = float(budget.residual_wall_time_s or 0.0)
    matmul_bill = int(matmul.get("flop_cost", -1))
    return {
        "failure": failure,
        "finite": bool(failure is None),
        "billed_flops": bill,
        "residual_s": residual,
        "wall_s": time.perf_counter() - started,
        "matmul_calls": int(matmul.get("calls", -1)),
        "matmul_bill": matmul_bill,
        "output_sha256": digest_arrays(outputs[:3]) if outputs is not None else None,
        "allocation": allocation,
        "operations": operations,
        "prediction_match": {
            "matmul_calls": int(matmul.get("calls", -1)) == prediction["matmul_calls"],
            "matmul_bill": matmul_bill == prediction["matmul_bill"],
            "no_reshape": "reshape" not in operations,
            "inclusive_below_strict_headroom": bill < STRICT_HEADROOM,
        },
        "remaining_after_compiler": STRICT_HEADROOM - bill,
        "hostile_five_x_effective_component": bill + 5.0e11 * residual,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    weights, factors = generated_inputs(args.seed)
    trace = run_trace(weights, factors)
    payload = {
        "status": "M209_GENERATED_NATIVE_RESOURCE_TRACE_ONLY",
        "firewall": "generated matrices only; no response, truth, scorer, challenge weight, leaderboard, submission, or champion access",
        "runtime": {"flopscope": flops.__version__, "numpy": np.__version__},
        "seed": int(args.seed),
        "width": WIDTH,
        "layers": LAYERS,
        "depth": DEPTH,
        "static_prediction": static_prediction(),
        "trace": trace,
        "rss": process_memory(),
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "failure": trace["failure"],
        "matmul_calls": trace["matmul_calls"],
        "matmul_bill": trace["matmul_bill"],
        "billed_flops": trace["billed_flops"],
        "residual_s": trace["residual_s"],
        "remaining_after_compiler": trace["remaining_after_compiler"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
