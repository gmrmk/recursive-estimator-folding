"""One fresh-process resource trace for the frozen M169 compiler schedule.

Generated Gaussian matrices are the only inputs.  This executable has no
model response, truth, scorer, contest row, leaderboard, submission, or
champion access.
"""

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

from m169_fused_compiler import (
    COMBINED_CAP,
    COLLISION_MASS,
    COMPILER_SLOT,
    INHERITED_K128_ENDPOINT_SUBTOTAL,
    LAYERS,
    WIDTH,
    allocate_staged_inputs,
    allocate_workspace,
    compile_staged_stack,
    initialize_target_q0,
    stage_inputs,
    static_prediction,
    workspace_allocation_ledger,
)


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
    if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    mib = 1024.0 * 1024.0
    return {
        "peak_working_set_mib": counters.PeakWorkingSetSize / mib,
        "working_set_mib": counters.WorkingSetSize / mib,
        "private_mib": counters.PrivateUsage / mib,
        "peak_pagefile_mib": counters.PeakPagefileUsage / mib,
    }


def generated_inputs(seed: int):
    """Match M164's response-free generated target-shape input contract."""

    rng = np.random.default_rng(int(seed))
    he = math.sqrt(2.0 / WIDTH)
    weights, covariances = [], []
    for _ in range(LAYERS):
        weights.append(rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he)
        root = rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) / math.sqrt(WIDTH)
        covariance = root @ root.T + 0.25 * np.eye(WIDTH)
        covariances.append(0.5 * (covariance + covariance.T))
    return weights, covariances


def digest_arrays(arrays) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        digest.update(memoryview(np.ascontiguousarray(np.asarray(value))).cast("B"))
    return digest.hexdigest()


def validate_state(correlation, exterior, edge, outputs) -> tuple[bool, str | None]:
    arrays = tuple(np.asarray(value) for value in (*outputs, correlation, exterior, edge))
    if not all(np.all(np.isfinite(value)) for value in arrays):
        return False, "nonfinite fused compiler output"
    corr, ext, edge_np = arrays[-3:]
    if not np.array_equal(np.diag(corr), np.ones(WIDTH)):
        return False, "correlation diagonal is not exactly one"
    if not np.array_equal(np.diag(ext), np.zeros(WIDTH)):
        return False, "exterior diagonal is not exactly zero"
    if not np.array_equal(np.diagonal(edge_np, axis1=1, axis2=2), np.zeros((LAYERS, WIDTH))):
        return False, "edge diagonal is not exactly zero"
    if np.any(ext < 0.0) or np.any(np.abs(corr) > 1.0):
        return False, "correlation/exterior domain violation"
    return True, None


def run_stack(weights_np, covariances_np) -> dict[str, object]:
    """Trace every materialization and compiler op in a single budget scope."""

    weights = [fnp.asarray(value, dtype=fnp.float64) for value in weights_np]
    covariances = [fnp.asarray(value, dtype=fnp.float64) for value in covariances_np]
    frozen_masses = fnp.asarray(np.array([COLLISION_MASS, 1.0 - COLLISION_MASS], dtype=np.float64), dtype=fnp.float64)
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    finite, reason = False, None
    outputs = None
    allocation = None
    try:
        with budget:
            staged = allocate_staged_inputs(LAYERS, WIDTH)
            workspace = allocate_workspace(LAYERS, WIDTH)
            allocation = workspace_allocation_ledger(workspace, staged)
            initialize_target_q0(workspace, frozen_masses)
            stage_inputs(weights, covariances, staged)
            aaaa, aaab, aabb, correlation, exterior, edge = compile_staged_stack(staged, workspace)
            outputs = (aaaa, aaab, aabb)
        finite, reason = validate_state(correlation, exterior, edge, outputs)
        if not finite:
            raise ArithmeticError(reason)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    summary = budget.summary_dict()
    operations = summary.get("operations", {})
    matmul = operations.get("matmul", {})
    prediction = static_prediction()
    residual = float(budget.residual_wall_time_s or 0.0)
    bill = int(budget.flops_used)
    residual_5x = 5.0 * residual
    combined = INHERITED_K128_ENDPOINT_SUBTOTAL + bill + 1.0e11 * residual_5x
    return {
        "failure": failure,
        "finite": bool(failure is None and finite),
        "billed_flops": bill,
        "residual_s": residual,
        "wall_s": time.perf_counter() - started,
        "matmul_calls": int(matmul.get("calls", -1)),
        "post_z_fused_matmul_calls": 1 if int(matmul.get("calls", -1)) == 2 else 0,
        "output_sha256": digest_arrays(outputs) if outputs is not None else None,
        "allocation": allocation,
        "operations": operations,
        "prediction_match": {
            "matmul_calls": int(matmul.get("calls", -1)) == prediction["predicted_total_matmul_calls"],
            "bill": bill == prediction["predicted_total_bill"],
            "no_reshape": "reshape" not in operations,
        },
        "combined": {
            "inherited_k128_endpoint_subtotal": INHERITED_K128_ENDPOINT_SUBTOTAL,
            "compiler_slot": COMPILER_SLOT,
            "combined_cap": COMBINED_CAP,
            "compiler_bill_fits_slot": bill <= COMPILER_SLOT,
            "five_x_residual_s": residual_5x,
            "combined_five_x_effective": combined,
            "combined_five_x_fits": combined <= COMBINED_CAP,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    weights, covariances = generated_inputs(args.seed)
    trace = run_stack(weights, covariances)
    output = {
        "status": "M169_NATIVE_RESOURCE_TRACE_ONLY_NO_EFFICACY",
        "firewall": "generated matrices only; no target truth, scorer, contest row, response, leaderboard, submission, or champion mutation",
        "runtime": {"flopscope": flops.__version__, "numpy": np.__version__},
        "seed": int(args.seed),
        "width": WIDTH,
        "layers": LAYERS,
        "static_prediction": static_prediction(),
        "trace": trace,
        "rss": process_memory(),
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "failure": trace["failure"],
        "matmul_calls": trace["matmul_calls"],
        "billed_flops": trace["billed_flops"],
        "residual_s": trace["residual_s"],
        "combined_five_x_effective": trace["combined"]["combined_five_x_effective"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
