"""Fresh-process target-shaped structural trace for deployable M145.

The worker generates one He MLP but never generates/opens a truth vector,
never computes an error or score, and never touches a competition instance.
It executes the candidate twice solely to certify call structure and reusable
frame restoration.
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
from whestbench import SetupContext
from whestbench.domain import MLP

from m145_deployable_estimator import (
    Estimator,
    MatchedComparator,
    signed_haar_radius_bank,
)


HERE = Path(__file__).resolve().parent
SETUP_SEED = 145_310_001
STRUCTURAL_MLP_SEED = 145_310_002


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


def process_memory() -> dict:
    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
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


def generated_he_mlp(seed: int) -> MLP:
    rng = np.random.default_rng(int(seed))
    scale = np.float32(math.sqrt(2.0 / 256.0))
    weights = [
        fnp.asarray(
            rng.standard_normal((256, 256), dtype=np.float32) * scale,
            dtype=fnp.float32,
        )
        for _ in range(32)
    ]
    mlp = MLP(
        width=256,
        depth=32,
        weights=weights,
        seed=int(seed),
        name=f"m145-structural-only-{seed}",
    )
    mlp.validate()
    return mlp


def array_sha256(array) -> str:
    contiguous = np.ascontiguousarray(np.asarray(array))
    return hashlib.sha256(memoryview(contiguous).cast("B")).hexdigest()


def one_predict(estimator: Estimator, mlp: MLP) -> tuple[dict, np.ndarray]:
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    failure = None
    prediction = None
    try:
        with budget:
            prediction = estimator.predict(mlp, 10**15)
        prediction = np.asarray(prediction).copy()
    except Exception as exc:  # structural audit records, never hides, a failure
        failure = f"{type(exc).__name__}: {exc}"
    wall = time.perf_counter() - started
    trace = list(estimator.dispatch_trace)
    stage_calls: dict[str, int] = {}
    for row in trace:
        prefix = str(row["stage"]).split(":", 1)[0]
        stage_calls[prefix] = stage_calls.get(prefix, 0) + int(row["matmul_calls"])
    record = {
        "failure": failure,
        "wall_s": wall,
        "billed_flops": int(budget.flops_used),
        "backend_s": float(budget.flopscope_backend_time_s),
        "overhead_s": float(budget.flopscope_overhead_time_s),
        "residual_s": float(budget.residual_wall_time_s or 0.0),
        "effective_compute": int(budget.flops_used)
        + 1e11 * float(budget.residual_wall_time_s or 0.0),
        "flopscope_summary": budget.summary_dict(),
        "prediction_shape": list(prediction.shape) if prediction is not None else None,
        "prediction_finite": bool(
            prediction is not None and np.isfinite(prediction).all()
        ),
        "prediction_sha256": array_sha256(prediction)
        if prediction is not None
        else None,
        "event_log": list(estimator.event_log),
        "transport": estimator.last_transport,
        "dispatch_records": trace,
        "matmul_call_total": int(sum(int(row["matmul_calls"]) for row in trace)),
        "matmul_calls_by_stage_prefix": stage_calls,
    }
    return record, prediction


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("candidate", "comparator"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--setup-seed", type=int, default=SETUP_SEED)
    parser.add_argument("--mlp-seed", type=int, default=STRUCTURAL_MLP_SEED)
    args = parser.parse_args()
    estimator = Estimator() if args.kind == "candidate" else MatchedComparator()
    stage_memory: list[dict] = []
    estimator.stage_observer = lambda stage: stage_memory.append(
        {"stage": stage, **process_memory()}
    )
    context = SetupContext(
        width=256,
        depth=32,
        flop_budget=10**15,
        api_version="synthetic-structural-only",
        seed=int(args.setup_seed),
    )
    setup_started = time.perf_counter()
    estimator.setup(context)
    setup_s = time.perf_counter() - setup_started
    after_setup = process_memory()
    provisional_hash = array_sha256(estimator.frame_bank)
    mlp = generated_he_mlp(int(args.mlp_seed))

    first, _prediction1 = one_predict(estimator, mlp)
    # Capture operational peak before allocating the independent reference
    # bank used only for restoration/coupling verification.
    operational_memory = process_memory()
    reference = signed_haar_radius_bank(int(args.setup_seed))
    first_restore_defect = float(
        np.max(np.abs(np.asarray(estimator.frame_bank) - reference))
    )
    reference_hash = array_sha256(reference)
    del reference

    if args.kind == "candidate":
        second, _prediction2 = one_predict(estimator, mlp)
        reference2 = signed_haar_radius_bank(int(args.setup_seed))
        second_restore_defect = float(
            np.max(np.abs(np.asarray(estimator.frame_bank) - reference2))
        )
        del reference2
        repeat_equal = first["prediction_sha256"] == second["prediction_sha256"]
        repeat_prediction_max_abs = float(
            np.max(np.abs(_prediction1 - _prediction2))
        )
    else:
        second = None
        second_restore_defect = None
        repeat_equal = None
        repeat_prediction_max_abs = None

    result = {
        "status": "DEPLOYABLE_SIGN_CORRECT_HAAR_STRUCTURAL_TRACE_ONLY_NO_EFFICACY",
        "kind": args.kind,
        "firewall": (
            "one generated He MLP; no truth, MSE, scorer, competition row, "
            "API, submission, designation, or champion mutation"
        ),
        "runtime": {
            "flopscope": getattr(flops, "__version__", "unknown"),
            "numpy": np.__version__,
        },
        "seeds": {
            "setup": int(args.setup_seed),
            "structural_mlp": int(args.mlp_seed),
        },
        "setup_s": setup_s,
        "memory_after_setup": after_setup,
        "operational_memory_after_first_predict": operational_memory,
        "workspace_bytes": estimator.workspace_bytes,
        "stage_memory": stage_memory,
        "frame_bank_bytes": int(estimator.frame_bank.nbytes),
        "provisional_bank_sha256": provisional_hash,
        "independent_reference_bank_sha256": reference_hash,
        "provisional_reference_bitwise_equal": provisional_hash == reference_hash,
        "first_restore_max_abs_defect": first_restore_defect,
        "second_restore_max_abs_defect": second_restore_defect,
        "repeat_prediction_bitwise_equal": repeat_equal,
        "repeat_prediction_max_abs": repeat_prediction_max_abs,
        "first_predict": first,
        "second_predict": second,
        "memory_after_all_verification": process_memory(),
    }
    payload = json.dumps(result, indent=2, sort_keys=True)
    args.output.write_text(payload + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "kind": args.kind,
                "output": str(args.output),
                "failure": first["failure"],
                "billed_flops": first["billed_flops"],
                "residual_s": first["residual_s"],
                "effective_compute": first["effective_compute"],
                "operational_peak_mib": operational_memory["peak_working_set_mib"],
                "restore_defect": first_restore_defect,
                "repeat_restore_defect": second_restore_defect,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
