"""Enumerate physical cores via Windows GetLogicalProcessorInformation so the
1-physical-core affinity mask is MEASURED, not assumed."""

from __future__ import annotations

import ctypes
import json
from ctypes import wintypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELATION_PROCESSOR_CORE = 0


class _SLPI(ctypes.Structure):
    _fields_ = [
        ("ProcessorMask", ctypes.c_size_t),
        ("Relationship", ctypes.c_int),
        ("Reserved", ctypes.c_ulonglong * 2),
    ]


def physical_core_masks() -> list[int]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetLogicalProcessorInformation.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.GetLogicalProcessorInformation.restype = wintypes.BOOL
    length = wintypes.DWORD(0)
    kernel32.GetLogicalProcessorInformation(None, ctypes.byref(length))
    count = length.value // ctypes.sizeof(_SLPI)
    buffer = (_SLPI * count)()
    if not kernel32.GetLogicalProcessorInformation(
        ctypes.byref(buffer), ctypes.byref(length)
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return [
        int(entry.ProcessorMask)
        for entry in buffer
        if entry.Relationship == RELATION_PROCESSOR_CORE
    ]


def main() -> None:
    masks = physical_core_masks()
    first = masks[0] if masks else 1
    result = {
        "physical_core_count": len(masks),
        "physical_core_masks_hex": [hex(mask) for mask in masks],
        "physical_core_logical_ids": [
            [bit for bit in range(64) if mask >> bit & 1] for mask in masks
        ],
        "arm_a_mask_one_physical_core_hex": hex(first),
        "arm_a_mask_one_physical_core": first,
        "arm_b_mask_one_logical_cpu_hex": hex(first & -first),
        "arm_b_mask_one_logical_cpu": first & -first,
    }
    (HERE / "topology.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
