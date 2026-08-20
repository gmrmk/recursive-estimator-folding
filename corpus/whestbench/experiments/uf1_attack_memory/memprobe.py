"""Windows process memory probe (ctypes; psutil is not installed in whest-v014).

Reports PeakWorkingSetSize and PeakPagefileUsage (private commit) from
K32GetProcessMemoryInfo, which is the same "peak working set" quantity the
corpus quotes for the 512-MiB envelope (e.g. 667.328 MiB for the L2 hybrid).
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

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
_GetProcessMemoryInfo = _k32.K32GetProcessMemoryInfo
_GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
_GetProcessMemoryInfo.restype = wintypes.BOOL


def snapshot() -> dict:
    pmc = _PMC()
    pmc.cb = ctypes.sizeof(_PMC)
    ok = _GetProcessMemoryInfo(_k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
    if not ok:
        raise OSError(ctypes.get_last_error(), "GetProcessMemoryInfo failed")
    return {
        "working_set_bytes": int(pmc.WorkingSetSize),
        "peak_working_set_bytes": int(pmc.PeakWorkingSetSize),
        "commit_bytes": int(pmc.PagefileUsage),
        "peak_commit_bytes": int(pmc.PeakPagefileUsage),
    }
