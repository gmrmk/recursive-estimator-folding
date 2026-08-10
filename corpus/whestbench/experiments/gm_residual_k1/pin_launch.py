"""Thin affinity-setting launcher for the FROZEN M160 worker.

Sets this process's affinity mask (before NumPy/FlopScope are ever imported),
verifies the mask took, then executes the frozen
``m160_cp311_worker.py`` unmodified via runpy.  The frozen file is never
edited, copied, or mutated.
"""

from __future__ import annotations

import ctypes
import runpy
import sys
from ctypes import wintypes
from pathlib import Path

WORKER = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\scorefloor_generation\terra_m160_hostile_deploy\m160_cp311_worker.py"
)


def set_affinity(mask: int) -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
    kernel32.SetProcessAffinityMask.restype = wintypes.BOOL
    kernel32.GetProcessAffinityMask.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
    ]
    kernel32.GetProcessAffinityMask.restype = wintypes.BOOL
    handle = kernel32.GetCurrentProcess()
    if mask and not kernel32.SetProcessAffinityMask(handle, ctypes.c_size_t(mask)):
        raise ctypes.WinError(ctypes.get_last_error())
    process_mask = ctypes.c_size_t(0)
    system_mask = ctypes.c_size_t(0)
    if not kernel32.GetProcessAffinityMask(
        handle, ctypes.byref(process_mask), ctypes.byref(system_mask)
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(process_mask.value)


def main() -> None:
    if sys.argv[1] != "--mask":
        raise SystemExit("usage: pin_launch.py --mask <int> -- <worker args...>")
    mask = int(sys.argv[2], 0)
    rest = sys.argv[3:]
    if rest and rest[0] == "--":
        rest = rest[1:]
    effective = set_affinity(mask)
    if mask and effective != mask:
        raise SystemExit(f"affinity pin failed: requested {mask:#x} got {effective:#x}")
    print(f"[pin_launch] affinity={effective:#x}", file=sys.stderr)
    sys.argv = [str(WORKER), *rest]
    runpy.run_path(str(WORKER), run_name="__main__")


if __name__ == "__main__":
    main()
