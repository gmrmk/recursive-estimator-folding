"""One-shot M245 fixture worker.

Importing this module is inert.  The executable path is owned by the external
stdlib supervisor frozen in M245 prematerialization erratum 1.  The worker
performs no scientific import until the supervisor has validated its READY
record and released the intent-bound GO event.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys
from typing import Any, Mapping, Sequence


AUTHORITY_DIRECTORY = Path(__file__).resolve().parent
REPOSITORY_ROOT = AUTHORITY_DIRECTORY.parents[3]
RUNTIME_ROOT = Path(r"C:\Users\strid\.venvs\whestbench-frozen-m178")
BASE_RUNTIME_ROOT = Path(r"C:\Python314")
WORKER_SOURCE = Path(__file__).resolve()
SUPERVISOR_SOURCE = AUTHORITY_DIRECTORY / "supervise_m245_fixture_materialization.py"
TRANSPORT_TEST = AUTHORITY_DIRECTORY / "test_m245_fixture_materialization_transport.py"
TDD_RECEIPT = AUTHORITY_DIRECTORY / "M245_FIXTURE_MATERIALIZATION_TDD_RECEIPT_20260810.md"
STATIC_VALIDATION_RECEIPT = (
    AUTHORITY_DIRECTORY
    / "M245_FIXTURE_MATERIALIZATION_STATIC_VALIDATION_RECEIPT_20260810.json"
)

INTENT = AUTHORITY_DIRECTORY / "M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json"
V2_TEMP = AUTHORITY_DIRECTORY / ".M245_FROZEN_MANIFEST_V2_20260810.json.tmp"
V2_FINAL = AUTHORITY_DIRECTORY / "M245_FROZEN_MANIFEST_V2_20260810.json"
RECEIPT_R = (
    AUTHORITY_DIRECTORY
    / "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json"
)
WITNESS_T = (
    AUTHORITY_DIRECTORY
    / "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json"
)

EXECUTION_PATHS = (INTENT, V2_TEMP, V2_FINAL, RECEIPT_R, WITNESS_T)
V1_COMMIT = "c4468c3d330f968ce1a3b376d56aa1f6b640e709"
REPAIR_COMMIT = "853b30cf5ef8f87788aab6cee73218edddd6f466"
EXPECTED_NUMPY_VERSION = "2.4.6"
SUPERVISOR_FLAGS = ("-I", "-B", "-S", "-u")
WORKER_FLAGS = ("-B", "-P", "-s", "-S", "-u")
SUPERVISOR_INTERPRETER = BASE_RUNTIME_ROOT / "python.exe"
WORKER_LOGICAL_INTERPRETER = RUNTIME_ROOT / "Scripts" / "python.exe"
WORKER_OS_IMAGE = BASE_RUNTIME_ROOT / "python.exe"
VENV_SITE_PACKAGES = RUNTIME_ROOT / "Lib" / "site-packages"
PASS_STATIC_VERDICT = "PASS_STATIC_M245_FIXTURE_MATERIALIZER_ONLY"
RSS_CAP_BYTES = 268_435_456
WALL_CAP_SECONDS = 30.0
CHILD_EXIT_WALL_CAP_SECONDS = 30.0
MAXIMUM_GAP_SECONDS = 0.100
NOMINAL_SAMPLE_SECONDS = 0.010

TDD_SHA256 = {
    "test_m245_fixture_materialization_transport.py":
        "f3a0835eaddc55ab54726c1366a04148c238d3c9fc10388e3c8c976c5eb8c97f",
    "M245_FIXTURE_MATERIALIZATION_TDD_RECEIPT_20260810.md":
        "b5f473f7a2c983f50842a7f8d6912245a158761a4057d564359af1399f7b6c9b",
}

AUTHORITY_SHA256 = {
    "M245_PREDECLARATION_20260810.md":
        "aa9ca84d48e840435d350fbab3be3f1c98356b541d54a018968cfa16b97f2512",
    "M245_FROZEN_MANIFEST_V1_20260810.json":
        "17a9df68304c7b06dd29957cc6fd4180242a9cc1bafb79e30c35f2426825b6b4",
    "M245_SHA256SUMS_V1_20260810.txt":
        "0fbc35bfa2e77993e19d50d03ebfdda8851b137cdde18e6ef6613172c8c565c9",
    "M245_PREMATERIALIZATION_ERRATUM1_20260810.md":
        "18f743c6bda98dc2c9c926db31ec93188a9670f1f2da3fcc761de14766e366b1",
    "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json":
        "b7aa2176b19571537e3313d8b2e4c8c1daad32b73fde42ce61b7522e4f3f1072",
    "M245_SHA256SUMS_V1_OVERLAY1_20260810.txt":
        "0dc4a2fe475a05db1db1f9cf9c15e13c66f95f16ae7b44b6fee1f0cb9592236a",
}

CHILD_ENVIRONMENT = {
    "BLIS_NUM_THREADS": "1",
    "COMSPEC": r"C:\Windows\System32\cmd.exe",
    "MKL_DYNAMIC": "FALSE",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_DYNAMIC": "FALSE",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PATH": (
        r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts;"
        r"C:\Python314;C:\Windows\System32;C:\Windows"
    ),
    "PATHEXT": ".COM;.EXE;.BAT;.CMD",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONNOUSERSITE": "1",
    "SYSTEMROOT": r"C:\Windows",
    "TEMP": r"C:\Users\strid\AppData\Local\Temp",
    "TMP": r"C:\Users\strid\AppData\Local\Temp",
    "VECLIB_MAXIMUM_THREADS": "1",
    "WINDIR": r"C:\Windows",
}

SYNCHRONIZE = 0x00100000
EVENT_MODIFY_STATE = 0x0002
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
INFINITE = 0xFFFFFFFF
ERROR_ALREADY_EXISTS = 183
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    rendered = json.dumps(
        dict(payload), allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True
    )
    return (rendered + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _canonical_compact_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(payload), allow_nan=False, ensure_ascii=True,
        separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _lexists(path: Path) -> bool:
    return os.path.lexists(str(path))


def _has_reparse_attribute(path: Path) -> bool:
    if os.name != "nt":
        return Path(path).is_symlink()
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetFileAttributesW.restype = wintypes.DWORD
    attributes = int(kernel32.GetFileAttributesW(str(Path(path))))
    if attributes == INVALID_FILE_ATTRIBUTES:
        raise OSError(ctypes.get_last_error(), f"GetFileAttributesW failed: {path}")
    return bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def _require_plain_root(root: Path) -> Path:
    boundary = Path(root)
    if not boundary.is_absolute():
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: root is not absolute: {boundary}")
    if not boundary.is_dir() or boundary.is_symlink() or _has_reparse_attribute(boundary):
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: non-plain root: {boundary}")
    resolved = boundary.resolve(strict=True)
    if _normalized(resolved) != _normalized(boundary):
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: resolved root drift: {boundary}")
    anchor = Path(boundary.anchor)
    cursor = anchor
    for part in boundary.parts[1:]:
        cursor = cursor / part
        if not cursor.is_dir() or cursor.is_symlink() or _has_reparse_attribute(cursor):
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: reparse root component: {cursor}")
    return resolved


def _require_plain_contained_file(path: Path, root: Path) -> None:
    target = Path(path)
    boundary = Path(root)
    resolved_root = _require_plain_root(boundary)
    if not target.is_absolute():
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: file is not absolute: {target}")
    if not target.is_file() or target.is_symlink() or _has_reparse_attribute(target):
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: non-plain file: {target}")
    resolved_target = target.resolve(strict=True)
    if _normalized(resolved_target) != _normalized(target):
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: resolved file drift: {target}")
    try:
        relative = resolved_target.relative_to(resolved_root)
    except ValueError as exc:
        raise RuntimeError(f"BLOCKED_PARENT_DRIFT: root escape: {target}") from exc
    cursor = resolved_root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink() or _has_reparse_attribute(cursor):
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: reparse component: {cursor}")


def _write_exclusive_fsync(path: Path, encoded: bytes) -> None:
    with Path(path).open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _verify_json_bytes(path: Path, expected: bytes) -> dict[str, Any]:
    observed = Path(path).read_bytes()
    if observed != expected:
        raise IOError(f"durable byte mismatch: {path}")
    parsed = json.loads(observed.decode("utf-8"))
    if canonical_json_bytes(parsed) != observed:
        raise IOError(f"noncanonical durable JSON: {path}")
    return {
        "path": str(Path(path)),
        "bytes": len(observed),
        "sha256": sha256_bytes(observed),
        "reopened_bytes_equal": True,
        "reopened_parse_equal": parsed == json.loads(expected.decode("utf-8")),
    }


def publish_canonical_hardlink(
    *, temp_path: Path, final_path: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    """Publish canonical JSON with the frozen create-if-absent hard-link path."""

    temporary = Path(temp_path)
    final = Path(final_path)
    if temporary.parent.resolve() != final.parent.resolve():
        raise ValueError("temporary and final paths must share a directory")
    if _lexists(temporary) or _lexists(final):
        raise FileExistsError("temporary or final path already exists")
    encoded = canonical_json_bytes(payload)
    _write_exclusive_fsync(temporary, encoded)
    temporary_receipt = _verify_json_bytes(temporary, encoded)
    source_stat = temporary.stat()
    os.link(temporary, final)
    final_stat = final.stat()
    same_device = source_stat.st_dev == final_stat.st_dev
    same_inode = source_stat.st_ino == final_stat.st_ino
    if not same_device or not same_inode:
        raise IOError("published names are not one same-device hard-linked file")
    final_receipt = _verify_json_bytes(final, encoded)
    if temporary.read_bytes() != final.read_bytes():
        raise IOError("temporary and final bytes differ")
    if source_stat.st_size != final_stat.st_size or source_stat.st_size != len(encoded):
        raise IOError("published byte length mismatch")
    temporary.unlink()
    if _lexists(temporary) or not final.is_file():
        raise IOError("hard-link finalization state mismatch")
    return {
        **final_receipt,
        "temporary_path": str(temporary),
        "temporary_sha256": temporary_receipt["sha256"],
        "temporary_removed": True,
        "same_device": same_device,
        "same_inode": same_inode,
        "source_device": int(source_stat.st_dev),
        "source_inode": int(source_stat.st_ino),
        "final_device": int(final_stat.st_dev),
        "final_inode": int(final_stat.st_ino),
    }


def raw_array_receipt(
    *,
    dtype_str: str,
    shape: Sequence[int],
    raw_c_bytes: bytes,
    repr_rows: list[list[str]],
    hex_rows: list[list[str]],
) -> dict[str, Any]:
    normalized_shape = [int(item) for item in shape]
    if dtype_str != "<f8":
        raise ValueError("M245 arrays must use little-endian float64")
    element_count = math.prod(normalized_shape)
    if element_count * 8 != len(raw_c_bytes):
        raise ValueError("shape and float64 byte length differ")
    if len(normalized_shape) == 1:
        expected_row_lengths = [normalized_shape[0]]
    elif len(normalized_shape) == 2:
        expected_row_lengths = [normalized_shape[1]] * normalized_shape[0]
    else:
        raise ValueError("M245 receipt shape must be rank one or two")
    if [len(row) for row in repr_rows] != expected_row_lengths:
        raise ValueError("repr row shape differs from array shape")
    if [len(row) for row in hex_rows] != expected_row_lengths:
        raise ValueError("hex row shape differs from array shape")
    values = struct.unpack("<" + "d" * element_count, raw_c_bytes)
    repr_flat = [item for row in repr_rows for item in row]
    hex_flat = [item for row in hex_rows for item in row]
    for value, decimal_text, hex_text in zip(values, repr_flat, hex_flat, strict=True):
        if not math.isfinite(value):
            raise ValueError("array receipt contains a nonfinite float")
        if not isinstance(decimal_text, str) or decimal_text != repr(value):
            raise ValueError("repr row is not the exact raw-float repr")
        if not isinstance(hex_text, str) or hex_text != value.hex():
            raise ValueError("hex row is not the exact raw-float hex")
    shape_json = json.dumps(
        normalized_shape, ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8")
    preimage = dtype_str.encode("utf-8") + b"\0" + shape_json + b"\0" + raw_c_bytes
    return {
        "dtype": dtype_str,
        "shape": normalized_shape,
        "bytes": len(raw_c_bytes),
        "sha256": sha256_bytes(preimage),
        "raw_c_order_sha256": sha256_bytes(raw_c_bytes),
        "raw_c_hex": raw_c_bytes.hex(),
        "repr_rows": repr_rows,
        "hex_rows": hex_rows,
        "hash_preimage": "dtype_utf8_NUL_canonical_shape_json_NUL_C_order_bytes",
    }


def validate_pre_go_runtime(
    *,
    no_site: int,
    no_user_site: int,
    safe_path: int,
    dont_write_bytecode: bool,
    venv_site_packages_present: bool,
    numpy_module_names: Sequence[str],
    intent_verified: bool,
    job_member: bool,
    owned_paths_absent: bool,
) -> bool:
    checks = {
        "no_site": no_site == 1,
        "no_user_site": no_user_site == 1,
        "safe_path": safe_path == 1,
        "dont_write_bytecode": dont_write_bytecode is True,
        "venv_site_packages_absent": venv_site_packages_present is False,
        "numpy_modules_absent": len(tuple(numpy_module_names)) == 0,
        "intent_verified": intent_verified is True,
        "job_member": job_member is True,
        "owned_paths_absent": owned_paths_absent is True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("BLOCKED_PRE_GO_RUNTIME: " + ",".join(failed))
    return True


def _normalized(path: Path | str) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def _environment_digest(environment: Mapping[str, str]) -> str:
    return sha256_bytes(_canonical_compact_bytes(dict(sorted(environment.items()))))


def _kernel32() -> Any:
    if os.name != "nt":
        raise OSError("M245 fixture materialization is Windows-only")
    return ctypes.WinDLL("kernel32", use_last_error=True)


def _close_handle(handle: int | None) -> None:
    if handle:
        kernel32 = _kernel32()
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        kernel32.CloseHandle(handle)


def _parent_pid(pid: int) -> int:
    kernel32 = _kernel32()
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    kernel32.Process32FirstW.restype = wintypes.BOOL
    kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    kernel32.Process32NextW.restype = wintypes.BOOL
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            if int(entry.th32ProcessID) == int(pid):
                return int(entry.th32ParentProcessID)
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        _close_handle(snapshot)
    raise RuntimeError("worker PID missing from process snapshot")


def _actual_image_path(pid: int) -> str:
    kernel32 = _kernel32()
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), "OpenProcess failed")
    try:
        capacity = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(capacity.value)
        if not kernel32.QueryFullProcessImageNameW(
            handle, 0, buffer, ctypes.byref(capacity)
        ):
            raise OSError(ctypes.get_last_error(), "QueryFullProcessImageNameW failed")
        return buffer.value
    finally:
        _close_handle(handle)


def _is_current_process_in_job() -> bool:
    kernel32 = _kernel32()
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.IsProcessInJob.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)
    ]
    kernel32.IsProcessInJob.restype = wintypes.BOOL
    answer = wintypes.BOOL()
    if not kernel32.IsProcessInJob(
        kernel32.GetCurrentProcess(), None, ctypes.byref(answer)
    ):
        raise OSError(ctypes.get_last_error(), "IsProcessInJob failed")
    return bool(answer.value)


def _open_event(name: str) -> int:
    kernel32 = _kernel32()
    kernel32.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.OpenEventW.restype = wintypes.HANDLE
    handle = kernel32.OpenEventW(SYNCHRONIZE | EVENT_MODIFY_STATE, False, name)
    if not handle:
        raise OSError(ctypes.get_last_error(), f"OpenEventW failed: {name}")
    return int(handle)


def _set_event(handle: int) -> None:
    kernel32 = _kernel32()
    kernel32.SetEvent.argtypes = [wintypes.HANDLE]
    kernel32.SetEvent.restype = wintypes.BOOL
    if not kernel32.SetEvent(handle):
        raise OSError(ctypes.get_last_error(), "SetEvent failed")


def _wait_event(handle: int, milliseconds: int) -> None:
    kernel32 = _kernel32()
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    result = kernel32.WaitForSingleObject(handle, milliseconds)
    if result == WAIT_TIMEOUT:
        raise TimeoutError("M245 control-event wait timed out")
    if result != WAIT_OBJECT_0:
        raise OSError(ctypes.get_last_error(), "WaitForSingleObject failed")


def _emit_record(payload: Mapping[str, Any]) -> None:
    encoded = canonical_json_bytes(payload)
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def _verify_static_validation(actual_hashes: Mapping[str, str]) -> dict[str, Any]:
    encoded = STATIC_VALIDATION_RECEIPT.read_bytes()
    payload = json.loads(encoded.decode("utf-8"))
    expected_keys = {
        "artifact", "audited_sha256", "authority_commit_v1",
        "authority_repair_commit", "committed_before_launch", "freeze_status",
        "independent_reviewer_count", "no_scientific_execution_performed",
        "reviewers",
    }
    if set(payload) != expected_keys:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: top-level schema mismatch")
    if canonical_json_bytes(payload) != encoded:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: receipt is not canonical JSON")
    if payload.get("artifact") != "M245_FIXTURE_MATERIALIZATION_STATIC_VALIDATION_RECEIPT":
        raise RuntimeError("BLOCKED_STATIC_AUDIT: artifact mismatch")
    if payload.get("authority_commit_v1") != V1_COMMIT:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: V1 commit mismatch")
    if payload.get("authority_repair_commit") != REPAIR_COMMIT:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: repair commit mismatch")
    if payload.get("freeze_status") != PASS_STATIC_VERDICT:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: non-PASS freeze status")
    if payload.get("committed_before_launch") is not True:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: commit declaration absent")
    if payload.get("no_scientific_execution_performed") is not True:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: execution firewall absent")
    audited = payload.get("audited_sha256")
    if not isinstance(audited, dict) or audited != dict(actual_hashes):
        raise RuntimeError("BLOCKED_STATIC_AUDIT: audited hash census mismatch")
    reviewers = payload.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) < 2:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: fewer than two reviewers")
    identities: list[str] = []
    for row in reviewers:
        if (
            not isinstance(row, dict)
            or set(row) != {"audited_sha256", "reviewer_id", "verdict"}
            or row.get("verdict") != PASS_STATIC_VERDICT
        ):
            raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer verdict mismatch")
        identity = row.get("reviewer_id")
        if not isinstance(identity, str) or identity != identity.strip().casefold():
            raise RuntimeError("BLOCKED_STATIC_AUDIT: noncanonical reviewer identity")
        if not identity or not all(
            char.isascii() and (char.isalnum() or char in "-_") for char in identity
        ):
            raise RuntimeError("BLOCKED_STATIC_AUDIT: invalid reviewer identity")
        if row.get("audited_sha256") != audited:
            raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer hash map mismatch")
        identities.append(identity)
    if len(set(identities)) < 2:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewers are not distinct")
    if payload.get("independent_reviewer_count") != len(set(identities)):
        raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer count mismatch")
    return {
        "path": str(STATIC_VALIDATION_RECEIPT),
        "sha256": sha256_bytes(encoded),
        "reviewers": sorted(set(identities)),
        "audited_sha256": dict(sorted(audited.items())),
    }


def _verify_authority_and_sources() -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    expected_root = Path(
        r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
        r"\publish\recursive-estimator-folding"
    )
    if _normalized(REPOSITORY_ROOT) != _normalized(expected_root):
        raise RuntimeError("BLOCKED_PARENT_DRIFT: repository root mismatch")
    for root in (REPOSITORY_ROOT, RUNTIME_ROOT, BASE_RUNTIME_ROOT, AUTHORITY_DIRECTORY):
        _require_plain_root(root)
    observed: dict[str, str] = {}
    frozen_authority_bytes: dict[str, bytes] = {}
    for name, expected in {**AUTHORITY_SHA256, **TDD_SHA256}.items():
        path = AUTHORITY_DIRECTORY / name
        _require_plain_contained_file(path, AUTHORITY_DIRECTORY)
        encoded = path.read_bytes()
        digest = sha256_bytes(encoded)
        observed[name] = digest
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: hash mismatch: {name}")
        frozen_authority_bytes[name] = encoded
    manifest = json.loads(
        frozen_authority_bytes["M245_FROZEN_MANIFEST_V1_20260810.json"].decode("utf-8")
    )
    for relative, expected in manifest["parent_hashes_repo_relative"].items():
        path = REPOSITORY_ROOT / Path(relative)
        _require_plain_contained_file(path, REPOSITORY_ROOT)
        digest = sha256_file(path)
        observed[f"repository::{relative}"] = digest
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: parent hash mismatch: {relative}")
    runtime = manifest["runtime"]
    runtime_files = {
        runtime["interpreter_runtime_relative"]: runtime["interpreter_sha256"],
        runtime["pyvenv_cfg_runtime_relative"]: runtime["pyvenv_cfg_sha256"],
        **runtime["files_runtime_relative_sha256"],
    }
    for relative, expected in runtime_files.items():
        path = RUNTIME_ROOT / Path(relative)
        _require_plain_contained_file(path, RUNTIME_ROOT)
        digest = sha256_file(path)
        observed[f"runtime::{relative}"] = digest
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: runtime hash mismatch: {relative}")
    base_files = {
        runtime["base_interpreter_base_relative"]: runtime["base_interpreter_sha256"],
        runtime["base_python_dll_base_relative"]: runtime["base_python_dll_sha256"],
    }
    for relative, expected in base_files.items():
        path = BASE_RUNTIME_ROOT / Path(relative)
        _require_plain_contained_file(path, BASE_RUNTIME_ROOT)
        digest = sha256_file(path)
        observed[f"base::{relative}"] = digest
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: base hash mismatch: {relative}")
    for path in (SUPERVISOR_SOURCE, WORKER_SOURCE, TRANSPORT_TEST, TDD_RECEIPT):
        _require_plain_contained_file(path, AUTHORITY_DIRECTORY)
    _require_plain_contained_file(STATIC_VALIDATION_RECEIPT, AUTHORITY_DIRECTORY)
    source_hashes = {
        SUPERVISOR_SOURCE.name: sha256_file(SUPERVISOR_SOURCE),
        WORKER_SOURCE.name: sha256_file(WORKER_SOURCE),
        TRANSPORT_TEST.name: sha256_file(TRANSPORT_TEST),
        TDD_RECEIPT.name: sha256_file(TDD_RECEIPT),
        **{name: observed[name] for name in AUTHORITY_SHA256},
    }
    static_validation = _verify_static_validation(source_hashes)
    observed[STATIC_VALIDATION_RECEIPT.name] = static_validation["sha256"]
    return dict(sorted(observed.items())), static_validation, manifest


def _load_intent() -> tuple[dict[str, Any], bytes, str]:
    _require_plain_contained_file(INTENT, AUTHORITY_DIRECTORY)
    encoded = INTENT.read_bytes()
    payload = json.loads(encoded.decode("utf-8"))
    if canonical_json_bytes(payload) != encoded:
        raise RuntimeError("intent is not canonical immutable JSON")
    digest = sha256_bytes(encoded)
    if payload.get("artifact") != "M245_FIXTURE_MATERIALIZATION_INTENT":
        raise RuntimeError("intent artifact mismatch")
    if payload.get("authority_commit_v1") != V1_COMMIT:
        raise RuntimeError("intent V1 commit mismatch")
    if payload.get("authority_repair_commit") != REPAIR_COMMIT:
        raise RuntimeError("intent repair commit mismatch")
    if payload.get("no_retry") is not True:
        raise RuntimeError("intent no-retry rule absent")
    return payload, encoded, digest


def _expected_intent_payload(
    authority_sha256: Mapping[str, str], static_validation: Mapping[str, Any]
) -> dict[str, Any]:
    source_sha256 = dict(sorted(static_validation["audited_sha256"].items()))
    child_environment = dict(sorted(CHILD_ENVIRONMENT.items()))
    return {
        "artifact": "M245_FIXTURE_MATERIALIZATION_INTENT",
        "schema": "m245-fixture-materialization-intent-v1-erratum1",
        "status": "ONE_SHOT_AUTHORIZED_PENDING_GO",
        "authority_commit_v1": V1_COMMIT,
        "authority_repair_commit": REPAIR_COMMIT,
        "execution_paths": [str(path) for path in EXECUTION_PATHS],
        "authority_directory": str(AUTHORITY_DIRECTORY),
        "repository_root": str(REPOSITORY_ROOT),
        "runtime_root": str(RUNTIME_ROOT),
        "base_runtime_root": str(BASE_RUNTIME_ROOT),
        "authority_sha256": dict(sorted(authority_sha256.items())),
        "source_sha256": source_sha256,
        "static_validation_receipt_sha256": static_validation["sha256"],
        "supervisor_argv": [
            str(SUPERVISOR_INTERPRETER), *SUPERVISOR_FLAGS, str(SUPERVISOR_SOURCE)
        ],
        "worker_argv": [
            str(WORKER_LOGICAL_INTERPRETER), *WORKER_FLAGS, str(WORKER_SOURCE)
        ],
        "cwd": str(AUTHORITY_DIRECTORY),
        "child_environment": child_environment,
        "child_environment_sha256": _environment_digest(CHILD_ENVIRONMENT),
        "job_policy": {
            "fresh_job": True,
            "launcher_created_suspended": True,
            "assign_before_resume": True,
            "kill_on_close": True,
            "active_process_limit": 2,
            "completion_port_required": True,
            "total_processes_at_r": 2,
            "active_processes_at_r": 2,
            "active_processes_after_exit": 0,
            "only_processes": ["L", "W"],
        },
        "control_events": {
            "labels": ["READY", "GO", "DONE", "EXIT"],
            "namespace": "Local",
            "name_derivation": "M245_<first32-lowercase-intent-sha256>_<label>",
            "manual_reset": True,
            "initial_state": False,
            "collision_is_permanent_failure": True,
            "ready_is_pre_numpy": True,
            "done_waits_for_exit": True,
        },
        "resource_caps": {
            "rss_bytes": RSS_CAP_BYTES,
            "wall_seconds": WALL_CAP_SECONDS,
            "child_exit_wall_seconds": CHILD_EXIT_WALL_CAP_SECONDS,
            "maximum_gap_seconds": MAXIMUM_GAP_SECONDS,
            "nominal_sample_seconds": NOMINAL_SAMPLE_SECONDS,
            "processes": ["S", "L", "W"],
            "cpu_cap": None,
            "cpu_reporting_required": True,
        },
        "ownership": {
            "S": [str(INTENT), str(RECEIPT_R), str(WITNESS_T)],
            "L": [],
            "W": [str(V2_TEMP), str(V2_FINAL)],
        },
        "no_retry": True,
        "post_intent_failure_permanent": True,
    }


def _validate_exact_intent(
    payload: Mapping[str, Any],
    authority_sha256: Mapping[str, str],
    static_validation: Mapping[str, Any],
) -> None:
    if dict(payload) != _expected_intent_payload(authority_sha256, static_validation):
        raise RuntimeError("intent exact schema or value mismatch")


def _revalidate_intent_snapshot(expected_bytes: bytes, expected_sha256: str) -> None:
    _require_plain_contained_file(INTENT, AUTHORITY_DIRECTORY)
    observed = INTENT.read_bytes()
    if observed != expected_bytes or sha256_bytes(observed) != expected_sha256:
        raise RuntimeError("BLOCKED_PARENT_DRIFT: intent changed before NumPy import")
    if canonical_json_bytes(json.loads(observed.decode("utf-8"))) != observed:
        raise RuntimeError("BLOCKED_PARENT_DRIFT: intent is no longer canonical")


def _validate_publication_boundary(
    expected_intent_bytes: bytes, expected_intent_sha256: str
) -> None:
    _require_plain_root(AUTHORITY_DIRECTORY)
    if tuple(path.name for path in EXECUTION_PATHS) != (
        "M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json",
        ".M245_FROZEN_MANIFEST_V2_20260810.json.tmp",
        "M245_FROZEN_MANIFEST_V2_20260810.json",
        "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json",
        "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json",
    ):
        raise RuntimeError("execution-path basename drift")
    if any(
        _normalized(path.parent) != _normalized(AUTHORITY_DIRECTORY)
        for path in EXECUTION_PATHS
    ):
        raise RuntimeError("execution-path parent drift")
    _revalidate_intent_snapshot(expected_intent_bytes, expected_intent_sha256)
    present = [
        os.path.lexists(str(path))
        for path in (V2_TEMP, V2_FINAL, RECEIPT_R, WITNESS_T)
    ]
    if any(present):
        raise FileExistsError("worker-owned publication boundary is not absent")


def _event_names(intent_sha256: str) -> dict[str, str]:
    prefix = intent_sha256[:32]
    return {
        label: rf"Local\M245_{prefix}_{label}"
        for label in ("READY", "GO", "DONE", "EXIT")
    }


def _wait_for_go(handle: int) -> None:
    _wait_event(handle, 30_000)


def _load_numpy_after_go(manifest_v1: Mapping[str, Any]) -> Any:
    before = list(sys.path)
    site_path = str(VENV_SITE_PACKAGES)
    if any(_normalized(item) == _normalized(site_path) for item in sys.path):
        raise RuntimeError("venv site-packages appeared before controlled insertion")
    sys.path.insert(0, site_path)
    if _normalized(sys.path[0]) != _normalized(site_path):
        raise RuntimeError("controlled site-packages insertion failed")
    import numpy as np
    if str(np.__version__) != EXPECTED_NUMPY_VERSION:
        raise RuntimeError("BLOCKED_PARENT_DRIFT: NumPy version mismatch")
    if sys.path != [site_path, *before]:
        raise RuntimeError("controlled site-packages path list drift")
    runtime = manifest_v1["runtime"]
    relative = "Lib/site-packages/numpy/__init__.py"
    expected_init = RUNTIME_ROOT / Path(relative)
    numpy_init = Path(str(np.__file__))
    _require_plain_contained_file(numpy_init, RUNTIME_ROOT)
    if _normalized(numpy_init) != _normalized(expected_init):
        raise RuntimeError("BLOCKED_PARENT_DRIFT: NumPy package origin mismatch")
    expected_hash = runtime["files_runtime_relative_sha256"].get(relative)
    if not isinstance(expected_hash, str) or sha256_file(numpy_init) != expected_hash:
        raise RuntimeError("BLOCKED_PARENT_DRIFT: NumPy init hash mismatch")
    expected_package = expected_init.parent
    package_paths = tuple(Path(item) for item in getattr(np, "__path__", ()))
    if len(package_paths) != 1 or _normalized(package_paths[0]) != _normalized(expected_package):
        raise RuntimeError("BLOCKED_PARENT_DRIFT: NumPy package path mismatch")
    return np


def _scalar_receipt(value: Any) -> dict[str, str]:
    scalar = float(value)
    if not math.isfinite(scalar):
        raise RuntimeError("nonfinite fixture diagnostic")
    return {"repr": repr(scalar), "hex": scalar.hex()}


def _rows(value: Any) -> tuple[list[list[str]], list[list[str]]]:
    array = value
    if array.ndim == 1:
        values = [array]
    elif array.ndim == 2:
        values = array
    else:
        raise ValueError("M245 arrays must be vectors or matrices")
    repr_rows = [[repr(float(item)) for item in row] for row in values]
    hex_rows = [[float(item).hex() for item in row] for row in values]
    return repr_rows, hex_rows


def _array_receipt(np: Any, value: Any) -> dict[str, Any]:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    if array.dtype.str != "<f8":
        raise RuntimeError("fixture array dtype drift")
    repr_rows, hex_rows = _rows(array)
    return raw_array_receipt(
        dtype_str=array.dtype.str,
        shape=array.shape,
        raw_c_bytes=array.tobytes(order="C"),
        repr_rows=repr_rows,
        hex_rows=hex_rows,
    )


def _fixture_diagnostics(np: Any, mu: Any, covariance: Any) -> dict[str, Any]:
    mu = np.ascontiguousarray(np.asarray(mu, dtype=np.float64))
    covariance = np.ascontiguousarray(np.asarray(covariance, dtype=np.float64))
    all_finite = bool(np.all(np.isfinite(mu))) and bool(np.all(np.isfinite(covariance)))
    transpose_bytes = np.ascontiguousarray(covariance.T).tobytes(order="C")
    covariance_bytes = covariance.tobytes(order="C")
    symmetric = covariance_bytes == transpose_bytes
    try:
        np.linalg.cholesky(covariance)
        cholesky_pass = True
    except np.linalg.LinAlgError:
        cholesky_pass = False
    eigenvalues = np.linalg.eigvalsh(covariance)
    eigen_min = float(eigenvalues[0])
    eigen_max = float(eigenvalues[-1])
    determinant = float(np.linalg.det(covariance))
    repeated_variance = float(covariance[0, 0])
    conditional_j = float(covariance[1, 1] - covariance[0, 1] ** 2 / repeated_variance)
    conditional_k = float(covariance[2, 2] - covariance[0, 2] ** 2 / repeated_variance)
    conditional_jk = float(
        covariance[1, 2]
        - covariance[0, 1] * covariance[0, 2] / repeated_variance
    )
    conditional_rho = float(
        conditional_jk / np.sqrt(np.float64(conditional_j * conditional_k))
    )
    checks = {
        "all_finite": all_finite,
        "C_bytewise_equal_to_transpose": symmetric,
        "numpy_linalg_cholesky_pass": cholesky_pass,
        "eigvalsh_min_strictly_positive": eigen_min > 0.0,
        "conditional_variances_strictly_positive": conditional_j > 0.0 and conditional_k > 0.0,
        "absolute_conditional_correlation_strictly_less_than_one": abs(conditional_rho) < 1.0,
    }
    if not all(checks.values()):
        raise RuntimeError("frozen fixture failed required SPD diagnostics")
    return {
        **checks,
        "eigvalsh_min": _scalar_receipt(eigen_min),
        "eigvalsh_max": _scalar_receipt(eigen_max),
        "determinant": _scalar_receipt(determinant),
        "conditional_variance_j": _scalar_receipt(conditional_j),
        "conditional_variance_k": _scalar_receipt(conditional_k),
        "conditional_covariance_jk": _scalar_receipt(conditional_jk),
        "conditional_correlation": _scalar_receipt(conditional_rho),
    }


def _materialize_fixture_manifest(
    np: Any,
    *,
    manifest_v1: Mapping[str, Any],
    intent_sha256: str,
    authority_sha256: Mapping[str, str],
    source_sha256: Mapping[str, str],
    static_validation_sha256: str,
) -> tuple[dict[str, Any], list[Any]]:
    generated_by_id = {
        row["event_id"]: row for row in manifest_v1["generated_fixtures"]
    }
    fixtures: list[dict[str, Any]] = []
    retained: list[Any] = []
    for literal in manifest_v1["literal_fixtures"]:
        mu = np.ascontiguousarray(np.asarray(literal["mu"], dtype=np.float64))
        covariance = np.ascontiguousarray(np.asarray(literal["C"], dtype=np.float64))
        retained.extend((mu, covariance))
        fixtures.append({
            "event_id": literal["event_id"],
            "event": list(literal["event"]),
            "role": literal["role"],
            "origin": "literal_v1",
            "no_redraw": True,
            "mu": _array_receipt(np, mu),
            "C": _array_receipt(np, covariance),
            "diagnostics": _fixture_diagnostics(np, mu, covariance),
        })
    algorithm = manifest_v1["generated_fixture_algorithm"]
    for event_id in algorithm["applies_to"]:
        frozen = generated_by_id[event_id]
        seed = int(frozen["seed"])
        rng = np.random.Generator(np.random.Philox(seed))
        A = np.float64(0.30) * rng.standard_normal((3, 3))
        d = rng.uniform(np.float64(0.45), np.float64(1.10), size=3)
        covariance = A @ A.T + np.diag(d)
        alpha = rng.uniform(np.float64(-1.75), np.float64(1.75), size=3)
        mu = alpha * np.sqrt(np.diag(covariance))
        mu = np.ascontiguousarray(mu, dtype=np.float64)
        covariance = np.ascontiguousarray(covariance, dtype=np.float64)
        retained.extend((rng, A, d, alpha, mu, covariance))
        fixtures.append({
            "event_id": event_id,
            "event": list(frozen["event"]),
            "origin": "numpy_2_4_6_philox_v1",
            "seed": seed,
            "no_redraw": True,
            "mu": _array_receipt(np, mu),
            "C": _array_receipt(np, covariance),
            "diagnostics": _fixture_diagnostics(np, mu, covariance),
        })
    expected_ids = [f"E{index:02d}" for index in range(8)]
    if [row["event_id"] for row in fixtures] != expected_ids:
        raise RuntimeError("fixture census or order drift")
    payload = {
        "schema": "m245-authority-manifest-v2",
        "artifact": "M245_FROZEN_FIXTURE_AUTHORITY_V2",
        "date": "2026-08-10",
        "status": "PROVISIONAL_REQUIRES_PASSING_R_AND_T_AND_COMMITTED_AUDIT",
        "authority_commit_v1": V1_COMMIT,
        "authority_repair_commit": REPAIR_COMMIT,
        "authority_precedence": [
            "M245_PREMATERIALIZATION_ERRATUM1_20260810.md",
            "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json",
            "M245_PREDECLARATION_20260810.md",
            "M245_FROZEN_MANIFEST_V1_20260810.json",
        ],
        "authority_sha256": dict(sorted(authority_sha256.items())),
        "source_sha256": dict(sorted(source_sha256.items())),
        "static_validation_receipt_sha256": static_validation_sha256,
        "intent_sha256": intent_sha256,
        "numpy_version": str(np.__version__),
        "platform": {
            "byteorder": sys.byteorder,
            "implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "canonical_event_policy": manifest_v1["canonical_event_policy"],
        "generated_fixture_algorithm": algorithm,
        "array_receipt_policy": manifest_v1["array_receipt_v2"],
        "fixtures": fixtures,
        "shards": manifest_v1["shards"],
        "fixture_census": {
            "event_ids": expected_ids,
            "event_count": len(fixtures),
            "literal_count": len(manifest_v1["literal_fixtures"]),
            "generated_count": len(generated_by_id),
            "array_count": 2 * len(fixtures),
            "shard_count": len(manifest_v1["shards"]),
        },
        "scientific_quantities_evaluated": [],
        "retry_or_redraw": False,
        "receipt_R_required": RECEIPT_R.name,
        "terminal_witness_T_required": WITNESS_T.name,
    }
    return payload, retained


def _worker_main() -> int:
    if sys.argv != [str(WORKER_SOURCE)]:
        raise RuntimeError("worker accepts no arguments and requires absolute source argv")
    if _normalized(Path.cwd()) != _normalized(AUTHORITY_DIRECTORY):
        raise RuntimeError("worker cwd mismatch")
    if _normalized(sys.executable) != _normalized(WORKER_LOGICAL_INTERPRETER):
        raise RuntimeError("worker logical interpreter mismatch")
    if _normalized(getattr(sys, "_base_executable", "")) != _normalized(WORKER_OS_IMAGE):
        raise RuntimeError("worker base interpreter mismatch")
    actual_image = _actual_image_path(os.getpid())
    if _normalized(actual_image) != _normalized(WORKER_OS_IMAGE):
        raise RuntimeError("worker OS image mismatch")
    if sha256_file(Path(actual_image)) != (
        "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"
    ):
        raise RuntimeError("worker OS image hash mismatch")
    intent, _intent_bytes, intent_sha256 = _load_intent()
    authority_sha256, static_validation, manifest_v1 = _verify_authority_and_sources()
    _validate_exact_intent(intent, authority_sha256, static_validation)
    source_sha256 = static_validation["audited_sha256"]
    expected_env = dict(sorted(CHILD_ENVIRONMENT.items()))
    observed_env = dict(sorted(os.environ.items()))
    if observed_env != expected_env:
        raise RuntimeError("worker sanitized environment mismatch")
    environment_sha256 = _environment_digest(observed_env)
    if intent.get("child_environment") != expected_env:
        raise RuntimeError("intent child environment mismatch")
    if intent.get("child_environment_sha256") != environment_sha256:
        raise RuntimeError("intent child environment digest mismatch")
    if intent.get("worker_argv") != [
        str(WORKER_LOGICAL_INTERPRETER), *WORKER_FLAGS, str(WORKER_SOURCE)
    ]:
        raise RuntimeError("intent worker argv mismatch")
    if list(getattr(sys, "orig_argv", [])) != [
        str(WORKER_LOGICAL_INTERPRETER), *WORKER_FLAGS, str(WORKER_SOURCE)
    ]:
        raise RuntimeError("worker orig_argv mismatch")
    if int(sys.flags.hash_randomization) != 0:
        raise RuntimeError("worker PYTHONHASHSEED did not take effect")
    owned_absent = (
        all(not _lexists(path) for path in (V2_TEMP, V2_FINAL, RECEIPT_R, WITNESS_T))
        and INTENT.is_file()
    )
    numpy_names = tuple(
        sorted(name for name in sys.modules if name == "numpy" or name.startswith("numpy."))
    )
    venv_present = any(
        _normalized(item) == _normalized(VENV_SITE_PACKAGES) for item in sys.path
    )
    job_member = _is_current_process_in_job()
    validate_pre_go_runtime(
        no_site=int(sys.flags.no_site),
        no_user_site=int(sys.flags.no_user_site),
        safe_path=int(sys.flags.safe_path),
        dont_write_bytecode=bool(sys.dont_write_bytecode),
        venv_site_packages_present=venv_present,
        numpy_module_names=numpy_names,
        intent_verified=True,
        job_member=job_member,
        owned_paths_absent=owned_absent,
    )
    names = _event_names(intent_sha256)
    handles = {label: _open_event(name) for label, name in names.items()}
    try:
        ready = {
            "artifact": "M245_W_READY",
            "status": "READY_PRE_NUMPY",
            "pid": os.getpid(),
            "parent_pid": _parent_pid(os.getpid()),
            "actual_image": actual_image,
            "actual_image_sha256": sha256_file(Path(actual_image)),
            "logical_sys_executable": sys.executable,
            "base_executable": getattr(sys, "_base_executable", None),
            "argv": list(sys.argv),
            "orig_argv": list(getattr(sys, "orig_argv", [])),
            "cwd": str(Path.cwd()),
            "environment_sha256": environment_sha256,
            "intent_sha256": intent_sha256,
            "worker_source_sha256": sha256_file(WORKER_SOURCE),
            "static_validation_receipt_sha256": static_validation["sha256"],
            "job_member": job_member,
            "numpy_modules": list(numpy_names),
        }
        _emit_record(ready)
        _set_event(handles["READY"])
        _wait_for_go(handles["GO"])
        _revalidate_intent_snapshot(_intent_bytes, intent_sha256)
        np = _load_numpy_after_go(manifest_v1)
        v2_payload, retained_arrays = _materialize_fixture_manifest(
            np,
            manifest_v1=manifest_v1,
            intent_sha256=intent_sha256,
            authority_sha256=authority_sha256,
            source_sha256=source_sha256,
            static_validation_sha256=static_validation["sha256"],
        )
        _validate_publication_boundary(_intent_bytes, intent_sha256)
        v2_receipt = publish_canonical_hardlink(
            temp_path=V2_TEMP, final_path=V2_FINAL, payload=v2_payload
        )
        done = {
            "artifact": "M245_W_DONE",
            "status": "V2_PUBLISHED_WAITING_EXIT",
            "pid": os.getpid(),
            "intent_sha256": intent_sha256,
            "v2": v2_receipt,
            "fixture_count": len(v2_payload["fixtures"]),
            "retained_object_count": len(retained_arrays),
            "worker_source_sha256": sha256_file(WORKER_SOURCE),
        }
        _emit_record(done)
        _set_event(handles["DONE"])
        _wait_event(handles["EXIT"], INFINITE)
        os._exit(0)
    finally:
        for handle in handles.values():
            _close_handle(handle)


if __name__ == "__main__":
    try:
        _worker_main()
    except BaseException:
        os._exit(97)
