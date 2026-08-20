"""Run a target-shaped M145 sidecar trace without an efficacy outcome."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from m145_defensive_acg import (  # noqa: E402
    DIMENSION,
    PILOT_LINES,
    TOTAL_FRAMES,
    explicit_seed_tree,
)
from m145_flopscope_sidecar import structural_sidecar  # noqa: E402


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
        wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    ok = psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    )
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return {
        "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
        "working_set_bytes": int(counters.WorkingSetSize),
        "private_bytes": int(counters.PrivateUsage),
    }


def _formal_qr(raw: np.ndarray) -> np.ndarray:
    # Exact setup semantics of Formal L1's `q, _r = fnp.linalg.qr(raw)`.
    q, _r = np.linalg.qr(raw)
    return q.astype(np.float32)


def build_setup_frame_bank(tree: dict) -> fnp.ndarray:
    """Build exactly four pilot and 122 main setup QR frames, once."""

    children = tree["children"]
    pilot_rng = np.random.default_rng(children["pilot_qr"]["seed"])
    main_rng = np.random.default_rng(children["main_qr"]["seed"])
    frames = np.empty((TOTAL_FRAMES, DIMENSION, DIMENSION), dtype=np.float32)
    frames[:4] = _formal_qr(
        pilot_rng.standard_normal((4, DIMENSION, DIMENSION), dtype=np.float32)
    )
    frames[4:] = _formal_qr(
        main_rng.standard_normal((122, DIMENSION, DIMENSION), dtype=np.float32)
    )
    return fnp.asarray(frames, dtype=fnp.float32)


def main() -> None:
    # Fixed target-free trace identity; no generated-network error is formed.
    tree = explicit_seed_tree(setup_seed=0, mlp_seed=1450001)
    setup_started = time.perf_counter()
    frame_bank = build_setup_frame_bank(tree)
    setup_seconds = time.perf_counter() - setup_started
    baseline_copy = np.asarray(frame_bank).copy()
    data_rng = np.random.default_rng(1450002)
    y_plus = fnp.asarray(
        data_rng.random((PILOT_LINES, DIMENSION), dtype=np.float32)
    )
    y_minus = fnp.asarray(
        data_rng.random((PILOT_LINES, DIMENSION), dtype=np.float32)
    )
    memory_before = process_memory()
    predict_seeds = {
        name: int(tree["children"][name]["seed"])
        for name in ("mixture_labels", "uniform_anchors", "acg_latents")
    }
    flops.budget_reset()
    started = time.perf_counter()
    with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=60.0) as ctx:
        out = structural_sidecar(frame_bank, y_plus, y_minus, predict_seeds)
    wall = time.perf_counter() - started
    summary = ctx.summary_dict()
    restored_defect = float(
        np.max(np.abs(np.asarray(frame_bank) - baseline_copy))
    )
    weights = np.asarray(out["weights"])
    covariance = np.eye(DIMENSION, dtype=np.float32)
    if int(out["lambdas"].shape[0]):
        v = np.asarray(out["v"])
        lam = np.asarray(out["lambdas"])
        covariance += (v * (lam - 1.0)[None, :]) @ v.T
    result = {
        "status": "STRUCTURAL_NATIVE_TRACE_ONLY_NO_EFFICACY",
        "flopscope_version": getattr(flops, "__version__", "0.10.0+np2.4.6"),
        "dtype": "float32",
        "setup_seconds_qr_bank": setup_seconds,
        "sidecar_wall_seconds": wall,
        "summary": summary,
        "memory_before": memory_before,
        "memory_after": process_memory(),
        "frame_bank_bytes": int(frame_bank.nbytes),
        "restored_frame_max_abs_defect": restored_defect,
        "fallback": out["fallback"],
        "rank_realized": int(out["lambdas"].shape[0]),
        "lambda_min": float(np.min(np.asarray(out["lambdas"]))) if int(out["lambdas"].shape[0]) else 1.0,
        "lambda_max": float(np.max(np.asarray(out["lambdas"]))) if int(out["lambdas"].shape[0]) else 1.0,
        "weight_min": float(np.min(weights)),
        "weight_max": float(np.max(weights)),
        "weight_zero_count": int(np.count_nonzero(weights == 0.0)),
        "weight_nonfinite_count": int(np.count_nonzero(~np.isfinite(weights))),
        "covariance_finite": bool(np.all(np.isfinite(covariance))),
        "path_coefficient_shape": list(out["path_coefficients"].shape),
        "seed_tree": tree,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
