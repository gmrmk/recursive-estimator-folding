"""One arm of the gm_m116_streams falsifier, in its own fresh process.

Geometry, seed, gain, ReLU and wall limit are copied verbatim from the frozen
`m116b_inplace_l3_draft/campaign_worker.py::_full_prediction`.  Only the
dispatch grouping differs between arms.

usage:  run_arm.py --group 1|4 --tag <name>
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import time

import numpy as np
import flopscope as flops
import flopscope.numpy as fnp

from fused_l3 import GroupedInplaceL3, BLOCK_ROWS, TILE
from cost_model import independently_expanded_l3, dispatch

HERE = Path(__file__).resolve().parent

FULL_ROWS = 64_512
DEPTH = 32
SEED_FULL_PREDICTION = 11_664_512
RESIDUAL_GATE_S = 0.170
PEAK_GATE_MIB = 464.0
WALL_GATE_S = 20.0
EXPECTED_BILL = 189_738_221_568

_THREAD_ENV = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
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
    counters = PROCESS_MEMORY_COUNTERS_EX()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    scale = float(2**20)
    return {
        "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
        "peak_working_set_mib": counters.PeakWorkingSetSize / scale,
        "working_set_mib": counters.WorkingSetSize / scale,
        "private_mib": counters.PrivateUsage / scale,
    }


def runtime_identity() -> dict[str, str]:
    import sys
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "numpy": np.__version__,
        "flopscope": getattr(flops, "__version__", "unknown"),
        "threads": {name: os.environ.get(name) for name in _THREAD_ENV},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=int, required=True)
    parser.add_argument("--tag", type=str, required=True)
    parser.add_argument("--wall-limit", type=float, default=WALL_GATE_S)
    parser.add_argument("--no-dump", action="store_true")
    parser.add_argument("--high-priority", action="store_true")
    args = parser.parse_args()

    priority = "NORMAL"
    if args.high_priority:
        # measurement hygiene only: this host is shared with other agent
        # processes at 100% CPU; nothing is killed or preempted destructively.
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        HIGH_PRIORITY_CLASS = 0x00000080
        if kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), HIGH_PRIORITY_CLASS):
            priority = "HIGH"

    missing = [n for n in _THREAD_ENV if os.environ.get(n) != "1"]
    if missing:
        raise RuntimeError(f"one-thread environment required: {missing}")

    rng = np.random.default_rng(SEED_FULL_PREDICTION)
    gain = math.sqrt(2.0 / 256.0)
    setup_started = time.perf_counter()
    state = fnp.asarray(rng.standard_normal((FULL_ROWS, TILE), dtype=np.float32))
    weights = [
        fnp.asarray((rng.standard_normal((TILE, TILE), dtype=np.float32) * gain).astype(np.float32))
        for _ in range(DEPTH)
    ]
    workspace = GroupedInplaceL3(group=args.group, backend=fnp)
    plan = [(int(g), int(rows)) for _, g, rows in workspace.bind(state)]
    setup_s = time.perf_counter() - setup_started

    hook = dispatch(FULL_ROWS, TILE, TILE)
    started = time.perf_counter()
    context = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=args.wall_limit)
    calls = 0
    try:
        with context:
            for weight in weights:
                returned = workspace.multiply_inplace(state, weight)
                if returned is not state:
                    raise RuntimeError("in-place full prediction lost caller-left identity")
                calls += workspace.last_total_matmul_calls
                fnp.maximum(state, 0.0, out=state)
        failure = None
    except Exception as error:  # noqa: BLE001 - recorded, never retried
        failure = f"{type(error).__name__}: {error}"
    predict_wall_s = time.perf_counter() - started
    residual_s = float(context.residual_wall_time_s or 0.0)
    billed = int(context.flops_used)
    memory_after_prediction = process_memory()

    final = np.asarray(state)
    finite = bool(failure is None and np.isfinite(final).all())
    # copy-free digest: memoryview, not tobytes(), so the peak stays operator-only
    digest = hashlib.sha256(memoryview(final).cast("B")).hexdigest()
    dump = HERE / f"state_{args.tag}.npy"
    if not args.no_dump:
        np.save(dump, final)
    memory_at_exit = process_memory()

    expanded = independently_expanded_l3(FULL_ROWS) * DEPTH + DEPTH * FULL_ROWS * TILE

    report = {
        "tag": args.tag,
        "group": args.group,
        "block_rows": BLOCK_ROWS,
        "dispatch_plan_per_layer": plan,
        "dispatches_per_layer": len(plan),
        "full_prediction_matmul_calls": calls,
        "billed_flops": billed,
        "expected_bill_frozen": EXPECTED_BILL,
        "independently_expanded_bill": expanded,
        "bill_matches_frozen": billed == EXPECTED_BILL,
        "bill_matches_independent_expansion": billed == expanded,
        "hook_billed_flops": int(hook.total),
        "hook_core_calls_b4096": int(hook.core_calls),
        "wall_limit_used_s": args.wall_limit,
        "process_priority": priority,
        "setup_s": setup_s,
        "predict_wall_s": predict_wall_s,
        "residual_s": residual_s,
        "flopscope_backend_time_s": float(context.flopscope_backend_time_s),
        "flopscope_overhead_time_s": float(context.flopscope_overhead_time_s),
        "wall_time_s": float(context.wall_time_s or 0.0),
        "workspace_bytes": workspace.expected_workspace_bytes(),
        "workspace_mib": workspace.expected_workspace_bytes() / float(2**20),
        "peak_working_set_mib_after_prediction": memory_after_prediction["peak_working_set_mib"],
        "peak_working_set_mib_at_exit": memory_at_exit["peak_working_set_mib"],
        "finite": finite,
        "failure": failure,
        "state_sha256": digest,
        "state_dump": str(dump),
        "gates": {
            "residual_le_0.170": residual_s <= RESIDUAL_GATE_S,
            "peak_le_464_mib": memory_after_prediction["peak_working_set_mib"] <= PEAK_GATE_MIB,
            "wall_lt_20": predict_wall_s < WALL_GATE_S,
            "bill_exact": billed == EXPECTED_BILL,
            "finite": finite,
        },
        "runtime_identity": runtime_identity(),
    }
    (HERE / f"arm_{args.tag}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
