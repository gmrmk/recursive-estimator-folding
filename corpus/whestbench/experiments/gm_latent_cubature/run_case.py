"""One frozen n=64 case, in its own separately killable process.

Usage: run_case.py <width> <depth> <seed> <out.json> [--comparator]

An RSS watchdog thread hard-exits this process at 2 GB working set; the parent
also imposes a wall-clock limit.  This is the containment the resource
postmortem demanded.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
import threading
import time

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

from frozen_paths import TRUTH_BANK  # noqa: E402
import repaired_reducer as rr  # noqa: E402

RSS_LIMIT = 2_000_000_000
WATCHDOG_PERIOD_S = 0.25


class _MEM(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
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


def memory() -> dict[str, int]:
    counters = _MEM()
    counters.cb = ctypes.sizeof(counters)
    get_current = ctypes.windll.kernel32.GetCurrentProcess
    get_current.restype = ctypes.c_void_p
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)
    get_info.restype = ctypes.c_bool
    if not get_info(get_current(), ctypes.byref(counters), counters.cb):
        raise OSError("GetProcessMemoryInfo failed")
    return {
        "working_set_bytes": int(counters.WorkingSetSize),
        "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
        "private_bytes": int(counters.PrivateUsage),
    }


def _watchdog() -> None:
    while True:
        try:
            if memory()["working_set_bytes"] >= RSS_LIMIT:
                sys.stderr.write("RSS_WATCHDOG_KILL\n")
                sys.stderr.flush()
                os._exit(9)
        except Exception:
            pass
        time.sleep(WATCHDOG_PERIOD_S)


def main() -> None:
    width, depth, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out_path = sys.argv[4]
    want_comparator = "--comparator" in sys.argv

    thread = threading.Thread(target=_watchdog, daemon=True)
    thread.start()

    bank = json.loads(TRUTH_BANK.read_text(encoding="utf-8"))
    source = next(
        c
        for c in bank["cases"]
        if (c["width"], c["depth"], c["seed"]) == (width, depth, seed)
    )
    truth = np.asarray(source["truth"], dtype=np.float64)
    banked_baseline_prediction = np.asarray(
        source["corrected_fullcov_prediction"], dtype=np.float64
    )

    weights = rr.make_weights(width, depth, seed)

    record: dict[str, object] = {
        "width": width,
        "depth": depth,
        "seed": seed,
        "rss_limit_bytes": RSS_LIMIT,
    }

    # comparator MSE from the banked prediction (this is the gate denominator)
    err = banked_baseline_prediction - truth
    baseline_mse = float(np.mean(err * err))
    record["baseline_mse"] = baseline_mse
    record["banked_baseline_mse"] = float(source["baseline_mse"])
    record["banked_baseline_mse_abs_delta"] = abs(
        baseline_mse - float(source["baseline_mse"])
    )

    # SEAL 1: independently recompute the comparator from my regenerated
    # weights with the frozen corrected_fullcov module.
    if want_comparator:
        t0 = time.perf_counter()
        recomputed = rr.comparator(weights)
        record["comparator_seconds"] = time.perf_counter() - t0
        record["comparator_recompute_max_abs_delta"] = float(
            np.max(np.abs(recomputed - banked_baseline_prediction))
        )
        rerr = recomputed - truth
        record["comparator_recomputed_mse"] = float(np.mean(rerr * rerr))

    # the frozen candidate, repaired reducer, own process
    trace: list[dict[str, object]] = []
    t0 = time.perf_counter()
    prediction = rr.candidate(weights, trace=trace)
    record["candidate_seconds"] = time.perf_counter() - t0

    cerr = prediction - truth
    candidate_mse = float(np.mean(cerr * cerr))
    record["candidate_mse"] = candidate_mse
    record["candidate_max_abs_error"] = float(np.max(np.abs(cerr)))
    record["ratio"] = candidate_mse / baseline_mse
    record["win"] = bool(candidate_mse < baseline_mse)
    record["candidate_prediction"] = prediction.tolist()
    record["finite"] = bool(np.all(np.isfinite(prediction)))

    ranks = [int(r) for layer in trace for r in layer["ranks"]]
    record["trace_summary"] = {
        "layers": len(trace),
        "component_splits": len(ranks),
        "rank_min": min(ranks),
        "rank_max": max(ranks),
        "rank_mean": float(np.mean(ranks)),
        "children_max_per_layer": max(int(l["children"]) for l in trace),
        "output_component_counts": [int(l["output_components"]) for l in trace],
    }
    record["guard_counts"] = dict(rr.GUARD_COUNTS)
    record["memory"] = memory()
    record["status"] = "ok"

    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
    print(
        f"case n{width} L{depth} seed{seed}: ratio={record['ratio']!r} "
        f"win={record['win']} peakWS={record['memory']['peak_working_set_bytes']}"
    )


if __name__ == "__main__":
    main()
