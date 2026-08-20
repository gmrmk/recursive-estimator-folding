"""Fresh-process native resource and invariance trace for frozen M163.

This script operates only on generated target-shaped Gaussian covariances and
weight matrices.  It neither creates nor reads an MLP response/target truth,
nor accesses a scorer, leaderboard, submission, or champion artifact.
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

from m164_flopscope_sidecar import allocate_workspace, compile_layer, initialize_target_q0


WIDTH = 256
LAYERS = 31
COLLISION_MASS = 0.011688232421875
INHERITED_K128_ENDPOINT_SUBTOTAL = 85_980_878_800
COMPILER_SLOT = 14_019_121_200
COMBINED_CAP = 100_000_000_000


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
    rng = np.random.default_rng(int(seed))
    he = math.sqrt(2.0 / WIDTH)
    weights, covariances = [], []
    for _ in range(LAYERS):
        weights.append(rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) * he)
        root = rng.standard_normal((WIDTH, WIDTH), dtype=np.float64) / math.sqrt(WIDTH)
        covariance = root @ root.T + 0.25 * np.eye(WIDTH)
        covariance = 0.5 * (covariance + covariance.T)
        covariances.append(covariance)
    return weights, covariances


def digest_arrays(arrays) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        digest.update(memoryview(np.ascontiguousarray(np.asarray(value))).cast("B"))
    return digest.hexdigest()


def validate_state(correlation, exterior, edge, outputs) -> tuple[bool, str | None]:
    arrays = tuple(np.asarray(value) for value in (*outputs, correlation, exterior, edge))
    if not all(np.all(np.isfinite(value)) for value in arrays):
        return False, "nonfinite sidecar output"
    correlation_np, exterior_np, edge_np = arrays[-3:]
    if not np.array_equal(np.diag(correlation_np), np.ones(WIDTH)):
        return False, "correlation diagonal is not exact one"
    if not np.array_equal(np.diag(exterior_np), np.zeros(WIDTH)):
        return False, "exterior diagonal is not exact zero"
    if not np.array_equal(np.diag(edge_np), np.zeros(WIDTH)):
        return False, "edge diagonal is not exact zero"
    if np.any(exterior_np < 0.0) or np.any(np.abs(correlation_np) > 1.0):
        return False, "correlation/exterior domain violation"
    return True, None


def run_stack(weights_np, covariances_np, *, audit_only: bool) -> dict[str, object]:
    weights = [fnp.asarray(value, dtype=fnp.float64) for value in weights_np]
    covariances = [fnp.asarray(value, dtype=fnp.float64) for value in covariances_np]
    frozen_masses = fnp.asarray(
        np.array([COLLISION_MASS, 1.0 - COLLISION_MASS], dtype=np.float64),
        dtype=fnp.float64,
    )
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    finite, reason = False, None
    outputs = None
    try:
        with budget:
            workspace = allocate_workspace(WIDTH)
            initialize_target_q0(workspace, frozen_masses)
            for weight, covariance in zip(weights, covariances):
                aaaa, aaab, aabb, correlation, exterior, edge = compile_layer(weight, covariance, workspace)
                outputs = (aaaa, aaab, aabb)
        # Validation is an audit observer, never deployment work.  It must stay
        # outside the budget context so residual wall time measures the complete
        # estimator rather than repeated host-side introspection.
        finite, reason = validate_state(correlation, exterior, edge, outputs)
        if not finite:
            raise ArithmeticError(reason)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    summary = budget.summary_dict()
    matmul = summary.get("operations", {}).get("matmul", {})
    residual = float(budget.residual_wall_time_s or 0.0)
    bill = int(budget.flops_used)
    result = {
        "audit_only": audit_only,
        "failure": failure,
        "billed_flops": bill,
        "residual_s": residual,
        "wall_s": time.perf_counter() - started,
        "matmul_calls": int(matmul.get("calls", -1)),
        "finite": bool(failure is None and finite),
        "digest": digest_arrays(outputs) if outputs is not None else None,
        "last_outputs": tuple(np.asarray(value).copy() for value in outputs) if outputs is not None else None,
        "summary": summary,
    }
    return result


def invariance_audit(weights, covariances) -> dict[str, object]:
    """Generated, target-shaped structural test; not part of deployment cost."""

    baseline = run_stack(weights, covariances, audit_only=True)
    if baseline["failure"] is not None:
        return {"pass": False, "failure": baseline["failure"]}
    rng = np.random.default_rng(164_991_001)
    permutation = rng.permutation(WIDTH)
    permuted_weights = [weight[permutation] for weight in weights]
    permuted_covariances = [covariance[permutation][:, permutation] for covariance in covariances]
    permuted = run_stack(permuted_weights, permuted_covariances, audit_only=True)
    gauge = np.exp(rng.uniform(-0.35, 0.35, size=WIDTH))
    gauged_weights = [weight / gauge[:, None] for weight in weights]
    gauged_covariances = []
    for covariance in covariances:
        transformed = gauge[:, None] * covariance * gauge[None, :]
        gauged_covariances.append(0.5 * (transformed + transformed.T))
    gauged = run_stack(gauged_weights, gauged_covariances, audit_only=True)
    if permuted["failure"] is not None or gauged["failure"] is not None:
        return {"pass": False, "failure": permuted["failure"] or gauged["failure"]}
    baseline_output = baseline["last_outputs"]
    permutation_error = max(float(np.max(np.abs(left - right))) for left, right in zip(baseline_output, permuted["last_outputs"]))
    gauge_error = max(float(np.max(np.abs(left - right))) for left, right in zip(baseline_output, gauged["last_outputs"]))
    return {
        "pass": permutation_error <= 2.0e-8 and gauge_error <= 2.0e-8,
        "permutation_max_abs": permutation_error,
        "gauge_max_abs": gauge_error,
        "tolerance": 2.0e-8,
        "baseline_digest": baseline["digest"],
        "permutation_digest": permuted["digest"],
        "gauge_digest": gauged["digest"],
    }


def json_safe(result: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in result.items() if key not in {"last_outputs", "summary"}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=164_700_001)
    parser.add_argument("--invariance", action="store_true")
    args = parser.parse_args()
    weights, covariances = generated_inputs(args.seed)
    result = run_stack(weights, covariances, audit_only=False)
    residual_5x = 5.0 * float(result["residual_s"])
    combined_5x = INHERITED_K128_ENDPOINT_SUBTOTAL + int(result["billed_flops"]) + 1.0e11 * residual_5x
    output = {
        "status": "M164_NATIVE_RESOURCE_TRACE_ONLY_NO_EFFICACY",
        "firewall": "generated matrices only; no target truth, scorer, contest row, leaderboard, submission, or champion mutation",
        "seed": int(args.seed),
        "width": WIDTH,
        "layers": LAYERS,
        "expected_matmul_calls": 5 * LAYERS,
        "trace": json_safe(result),
        "rss": process_memory(),
        "combined": {
            "inherited_k128_endpoint_subtotal": INHERITED_K128_ENDPOINT_SUBTOTAL,
            "compiler_slot": COMPILER_SLOT,
            "combined_cap": COMBINED_CAP,
            "compiler_bill_fits_slot": int(result["billed_flops"]) <= COMPILER_SLOT,
            "five_x_residual_s": residual_5x,
            "combined_five_x_effective": combined_5x,
            "combined_five_x_fits": combined_5x <= COMBINED_CAP,
        },
        "invariance": invariance_audit(weights, covariances) if args.invariance else None,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
