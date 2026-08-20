"""Run a script in this process and report the process-wide peak memory.

Method B of the memory reconciliation: the whole-harness peak the hostile
verifier read, which holds the direct arbiter, the incumbent package and every
fork route at once.  Method A -- the incumbent's own declared method, one
isolated process per estimator -- is ``peak_probe.py``.

The target is executed with ``runpy`` rather than as a child process on
purpose.  ``PeakWorkingSetSize`` is a live kernel counter: once a process
exits its working set is torn down and a post-mortem
``GetProcessMemoryInfo`` on a handle to it reports a few MiB, which is how an
earlier version of this file credited a 600-MiB run with 4.48 MiB.  Reading
the counter from inside the same process avoids that entirely; the wrapper's
own overhead is a few hundred KiB of interpreter state that is already
resident before the target starts.

    python -B peak_of.py <peak.json> <script.py> [script args...]

Pass ``-B`` (or set ``PYTHONDONTWRITEBYTECODE=1``) unless the point of the run
is to observe whether the target protects the incumbent tree itself.
"""

from __future__ import annotations

import ctypes
import json
import runpy
import sys
import time
from ctypes import wintypes
from pathlib import Path

MIB = 1024.0 * 1024.0


class _PMC(ctypes.Structure):
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
    ]


_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_info = _k32.K32GetProcessMemoryInfo
_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
_info.restype = wintypes.BOOL


def snapshot() -> dict:
    pmc = _PMC()
    pmc.cb = ctypes.sizeof(_PMC)
    if not _info(_k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
        raise OSError(ctypes.get_last_error(), "GetProcessMemoryInfo failed")
    return {
        "working_set_mib": round(pmc.WorkingSetSize / MIB, 4),
        "peak_working_set_mib": round(pmc.PeakWorkingSetSize / MIB, 4),
        "commit_mib": round(pmc.PagefileUsage / MIB, 4),
        "peak_commit_mib": round(pmc.PeakPagefileUsage / MIB, 4),
    }


def main() -> None:
    peak_path = Path(sys.argv[1]).resolve()
    script = Path(sys.argv[2]).resolve()
    script_args = sys.argv[3:]

    baseline = snapshot()
    saved_argv = sys.argv
    sys.argv = [str(script)] + script_args
    sys.path.insert(0, str(script.parent))
    start = time.perf_counter()
    status = "ok"
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exit_code:            # a target that calls sys.exit
        status = f"SystemExit({exit_code.code})"
    finally:
        wall = time.perf_counter() - start
        sys.argv = saved_argv
    final = snapshot()

    peak_path.write_text(json.dumps({
        "method": "B: whole-harness process peak (target run in-process)",
        "script": str(script),
        "args": script_args,
        "status": status,
        "wall_s": round(wall, 3),
        "dont_write_bytecode": bool(sys.dont_write_bytecode),
        "wrapper_baseline": baseline,
        "final": final,
        "peak_working_set_mib": final["peak_working_set_mib"],
        "peak_commit_mib": final["peak_commit_mib"],
    }, indent=1), encoding="utf-8")
    print("\n" + json.dumps({
        "peak_json": str(peak_path),
        "status": status,
        "wall_s": round(wall, 3),
        "peak_working_set_mib": final["peak_working_set_mib"],
        "peak_commit_mib": final["peak_commit_mib"],
    }, indent=1), file=sys.stderr)


if __name__ == "__main__":
    main()
