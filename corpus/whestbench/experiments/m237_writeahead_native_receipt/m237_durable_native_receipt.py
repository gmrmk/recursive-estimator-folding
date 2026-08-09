"""M237 durable no-overwrite publication primitives.

These helpers own host-side evidence transport only.  Importing this module
does not create a path, issue an intent, or start a worker.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Mapping


INTENT_NAME = "M237_LAUNCH_INTENT_20260809.json"
RESULT_NAME = "M237_NATIVE_ONE_PROCESS_RESULT_20260809.json"
RESULT_TEMP_NAME = ".M237_NATIVE_ONE_PROCESS_RESULT_20260809.json.tmp"
PROBE_TEMP_NAME = ".m237_hardlink_probe.tmp"
PROBE_FINAL_NAME = ".m237_hardlink_probe.final"
PROBE_BYTES = b"M237_NTFS_NO_OVERWRITE_PROBE_V1\n"


def canonical_json_bytes(payload: Mapping[str, object]) -> bytes:
    """Return the sole M237 JSON representation."""

    text = json.dumps(
        dict(payload),
        allow_nan=False,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    )
    return (text + "\n").encode("utf-8")


def execution_paths(directory: Path) -> dict[str, Path]:
    root = Path(directory)
    return {
        "intent": root / INTENT_NAME,
        "result": root / RESULT_NAME,
        "result_temp": root / RESULT_TEMP_NAME,
        "probe_temp": root / PROBE_TEMP_NAME,
        "probe_final": root / PROBE_FINAL_NAME,
    }


def assert_execution_paths_absent(directory: Path) -> dict[str, Path]:
    paths = execution_paths(Path(directory))
    existing = [str(path) for path in paths.values() if path.exists()]
    if existing:
        raise FileExistsError("M237 durable path already exists: " + ", ".join(existing))
    return paths


def _write_fsync_exclusive(path: Path, payload: bytes) -> None:
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _verified_json_receipt(path: Path, expected: bytes) -> dict[str, object]:
    observed = Path(path).read_bytes()
    if observed != expected:
        raise IOError(f"durable byte mismatch for {path}")
    parsed = json.loads(observed.decode("utf-8"))
    return {
        "path": str(path),
        "bytes": len(observed),
        "sha256": hashlib.sha256(observed).hexdigest(),
        "parsed": parsed,
    }


def hardlink_preflight(directory: Path) -> dict[str, object]:
    """Prove same-directory create-if-absent hard links, then clean the probe."""

    root = Path(directory)
    probe_temp = root / PROBE_TEMP_NAME
    probe_final = root / PROBE_FINAL_NAME
    if probe_temp.exists() or probe_final.exists():
        raise FileExistsError("M237 hard-link probe path already exists")
    temp_created = False
    linked = False
    try:
        stream = probe_temp.open("xb")
        temp_created = True
        with stream:
            stream.write(PROBE_BYTES)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(probe_temp, probe_final)
        linked = True
        if probe_temp.read_bytes() != PROBE_BYTES:
            raise IOError("M237 probe temporary bytes changed")
        if probe_final.read_bytes() != PROBE_BYTES:
            raise IOError("M237 probe final bytes changed")
        temp_stat = probe_temp.stat()
        final_stat = probe_final.stat()
        if temp_stat.st_dev != final_stat.st_dev:
            raise IOError("M237 probe crossed devices")
        if hasattr(temp_stat, "st_ino") and temp_stat.st_ino != final_stat.st_ino:
            raise IOError("M237 probe names are not one hard-linked file")
        receipt = {
            "supported": True,
            "bytes": len(PROBE_BYTES),
            "sha256": hashlib.sha256(PROBE_BYTES).hexdigest(),
            "device": int(temp_stat.st_dev),
        }
    finally:
        if linked and probe_final.exists():
            probe_final.unlink()
        if temp_created and probe_temp.exists():
            probe_temp.unlink()
    if probe_temp.exists() or probe_final.exists():
        raise IOError("M237 probe cleanup failed")
    return receipt


def write_launch_intent_exclusive(
    path: Path, payload: Mapping[str, object]
) -> dict[str, object]:
    """Exclusive-create, fsync, reopen, and parse one launch intent."""

    target = Path(path)
    encoded = canonical_json_bytes(payload)
    _write_fsync_exclusive(target, encoded)
    return _verified_json_receipt(target, encoded)


def publish_native_result(
    *,
    temp_path: Path,
    final_path: Path,
    payload: Mapping[str, object],
) -> dict[str, object]:
    """Install one complete pass-or-fail JSON with no-overwrite hard linking."""

    temporary = Path(temp_path)
    final = Path(final_path)
    if temporary.parent.resolve() != final.parent.resolve():
        raise ValueError("M237 result paths must share one directory")
    if temporary.exists():
        raise FileExistsError(str(temporary))
    if final.exists():
        raise FileExistsError(str(final))
    encoded = canonical_json_bytes(payload)
    with temporary.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    temp_stat = temporary.stat()
    os.link(temporary, final)
    final_stat = final.stat()
    if temp_stat.st_dev != final_stat.st_dev:
        raise IOError("M237 result hard link crossed devices")
    if hasattr(temp_stat, "st_ino") and temp_stat.st_ino != final_stat.st_ino:
        raise IOError("M237 result names are not one hard-linked file")
    if temporary.read_bytes() != encoded:
        raise IOError("M237 result temporary bytes changed")
    receipt = _verified_json_receipt(final, encoded)
    temporary.unlink()
    if temporary.exists() or not final.exists():
        raise IOError("M237 result finalization state mismatch")
    receipt["temporary_removed"] = True
    return receipt


__all__ = [
    "INTENT_NAME",
    "PROBE_BYTES",
    "PROBE_FINAL_NAME",
    "PROBE_TEMP_NAME",
    "RESULT_NAME",
    "RESULT_TEMP_NAME",
    "assert_execution_paths_absent",
    "canonical_json_bytes",
    "execution_paths",
    "hardlink_preflight",
    "publish_native_result",
    "write_launch_intent_exclusive",
]
