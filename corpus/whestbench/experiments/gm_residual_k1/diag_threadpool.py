"""DIAGNOSTIC (not an arm, cannot change the ARM A verdict).

Counter-hypothesis under test: ARM A's residual inflation is not the
participant pin per se but BLAS thread-pool oversubscription -- the pool is
sized from the machine's 16 logical processors while the process is confined
to 2, so spin-wait contention lands in wall time (and hence in
residual = wall - backend - overhead).

Run pinned to 0x3 exactly like an ARM A worker and report the pool size that
OpenBLAS actually chose, plus a matmul throughput comparison.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
import time
from ctypes import wintypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPS = Path(os.environ.get("M160_CP311_DEPS", r"C:\tmp\m160-cp311-deps"))


def set_affinity(mask: int) -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
    kernel32.GetProcessAffinityMask.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
    ]
    handle = kernel32.GetCurrentProcess()
    if mask:
        kernel32.SetProcessAffinityMask(handle, ctypes.c_size_t(mask))
    process_mask = ctypes.c_size_t(0)
    system_mask = ctypes.c_size_t(0)
    kernel32.GetProcessAffinityMask(
        handle, ctypes.byref(process_mask), ctypes.byref(system_mask)
    )
    return int(process_mask.value)


def main() -> None:
    mask = int(sys.argv[1], 0)
    effective = set_affinity(mask)
    sys.path.insert(0, str(DEPS))
    import numpy as np

    info = []
    try:
        from threadpoolctl import threadpool_info

        info = threadpool_info()
    except Exception as exc:  # threadpoolctl may be absent in the cp311 deps
        info = [{"unavailable": f"{type(exc).__name__}: {exc}"}]

    rng = np.random.default_rng(7)
    a = rng.standard_normal((1024, 1024), dtype=np.float32)
    b = rng.standard_normal((1024, 1024), dtype=np.float32)
    a @ b  # warm
    started = time.perf_counter()
    for _ in range(10):
        a @ b
    elapsed = time.perf_counter() - started

    result = {
        "requested_mask": hex(mask),
        "effective_mask": hex(effective),
        "os_cpu_count": os.cpu_count(),
        "openblas_num_threads_env": os.environ.get("OPENBLAS_NUM_THREADS"),
        "threadpool_info": info,
        "sgemm_1024_x10_s": elapsed,
        "sgemm_gflops": 10 * 2 * 1024**3 / elapsed / 1e9,
    }
    print(json.dumps(result, sort_keys=True))
    pool = os.environ.get("OPENBLAS_NUM_THREADS", "default")
    out = HERE / f"diag_threadpool_mask{hex(mask)}_pool{pool}.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
