"""One-shot stdlib control plane for M245 fixture materialization.

Importing this module is inert.  The executable entry point implements the
authority-frozen S -> L -> W topology and owns only I, provisional R, and
terminal witness T.  Scientific work remains exclusively in W after GO.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import threading
import time
from typing import Any, Mapping, Sequence


AUTHORITY_DIRECTORY = Path(__file__).resolve().parent
REPOSITORY_ROOT = AUTHORITY_DIRECTORY.parents[3]
RUNTIME_ROOT = Path(r"C:\Users\strid\.venvs\whestbench-frozen-m178")
BASE_RUNTIME_ROOT = Path(r"C:\Python314")
SUPERVISOR_SOURCE = Path(__file__).resolve()
WORKER_SOURCE = AUTHORITY_DIRECTORY / "materialize_m245_fixtures.py"
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
EXECUTION_BASENAMES = tuple(path.name for path in EXECUTION_PATHS)

SUPERVISOR_INTERPRETER = BASE_RUNTIME_ROOT / "python.exe"
WORKER_LOGICAL_INTERPRETER = RUNTIME_ROOT / "Scripts" / "python.exe"
WORKER_OS_IMAGE = SUPERVISOR_INTERPRETER
SUPERVISOR_FLAGS = ("-I", "-B", "-S", "-u")
WORKER_FLAGS = ("-B", "-P", "-s", "-S", "-u")
SUPERVISOR_IMAGE_SHA256 = (
    "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"
)
WORKER_IMAGE_SHA256 = SUPERVISOR_IMAGE_SHA256
LAUNCHER_IMAGE_SHA256 = (
    "4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262"
)
V1_COMMIT = "c4468c3d330f968ce1a3b376d56aa1f6b640e709"
REPAIR_COMMIT = "853b30cf5ef8f87788aab6cee73218edddd6f466"
PASS_STATIC_VERDICT = "PASS_STATIC_M245_FIXTURE_MATERIALIZER_ONLY"

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

EXPECTED_TRACE = (
    "PREINTENT",
    "INTENT_VERIFIED",
    "LAUNCHER_SUSPENDED",
    "JOB_ASSIGNED",
    "LAUNCHER_RESUMED",
    "WORKER_READY",
    "GO_RELEASED",
    "V2_PUBLISHED",
    "DONE_BARRIER",
    "CHILDREN_LIVE_AT_R",
    "R_PUBLISHED",
    "ENDPOINT_CAPTURED",
    "LIVE_PEAK_CPU_CAPTURED",
    "EXIT_RELEASED",
    "WORKER_OS_EXIT",
    "CHILDREN_EXITED",
    "CHILD_EXIT_CLOCK_CAPTURED",
    "JOB_ACTIVE_ZERO",
    "T_PUBLISHED_PENDING_INDEPENDENT_AUDIT",
)

CONTROL_EVENT_MANUAL_RESET = True
CONTROL_EVENT_INITIAL_STATE = False
RSS_CAP_BYTES = 268_435_456
WALL_CAP_SECONDS = 30.0
CHILD_EXIT_WALL_CAP_SECONDS = 30.0
MAXIMUM_GAP_SECONDS = 0.100
NOMINAL_SAMPLE_SECONDS = 0.010

CREATE_SUSPENDED = 0x00000004
CREATE_UNICODE_ENVIRONMENT = 0x00000400
STARTF_USESTDHANDLES = 0x00000100
HANDLE_FLAG_INHERIT = 0x00000001
STD_INPUT_HANDLE = -10
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
STILL_ACTIVE = 259
INFINITE = 0xFFFFFFFF
ERROR_ALREADY_EXISTS = 183
ERROR_BROKEN_PIPE = 109
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SYNCHRONIZE = 0x00100000
PROCESS_HANDLE_ACCESS_MASK = PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400

JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectBasicAccountingInformation = 1
JobObjectAssociateCompletionPortInformation = 7
JobObjectExtendedLimitInformation = 9
JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO = 4
JOB_OBJECT_MSG_NEW_PROCESS = 6
JOB_OBJECT_MSG_EXIT_PROCESS = 7


class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", wintypes.DWORD),
        ("dwHighDateTime", wintypes.DWORD),
    ]


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL),
    ]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


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


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class JOBOBJECT_ASSOCIATE_COMPLETION_PORT(ctypes.Structure):
    _fields_ = [
        ("CompletionKey", wintypes.LPVOID),
        ("CompletionPort", wintypes.HANDLE),
    ]


class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
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


def _normalized(path: Path | str) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def _environment_digest(environment: Mapping[str, str]) -> str:
    return sha256_bytes(_canonical_compact_bytes(dict(sorted(environment.items()))))


def sanitized_child_environment() -> dict[str, str]:
    return dict(CHILD_ENVIRONMENT)


def supervisor_argv() -> list[str]:
    return [str(SUPERVISOR_INTERPRETER), *SUPERVISOR_FLAGS, str(SUPERVISOR_SOURCE)]


def worker_argv() -> list[str]:
    return [str(WORKER_LOGICAL_INTERPRETER), *WORKER_FLAGS, str(WORKER_SOURCE)]


def assert_paths_absent(paths: Sequence[Path]) -> None:
    bound = tuple(Path(path) for path in paths)
    if len(bound) != 5 or tuple(path.name for path in bound) != EXECUTION_BASENAMES:
        raise ValueError("the exact frozen five-path namespace is required")
    parents = {_normalized(path.parent.resolve(strict=False)) for path in bound}
    if len(parents) != 1:
        raise ValueError("all five execution paths must share one resolved parent")
    present = [
        os.path.lexists(str(path))
        for path in bound
    ]
    if any(present):
        occupied = [str(path) for path, exists in zip(bound, present, strict=True) if exists]
        raise FileExistsError("execution namespace is not absent: " + ",".join(occupied))


def validate_state_trace(trace: Sequence[str]) -> bool:
    if tuple(trace) != EXPECTED_TRACE:
        raise ValueError("M245 supervisor state trace differs from frozen order")
    return True


def _require_hex_digest(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"{label} is not a lowercase SHA-256")
    return value


def validate_topology_evidence(evidence: Mapping[str, Any]) -> bool:
    if not isinstance(evidence, Mapping):
        raise ValueError("topology evidence must be an object")
    for role in ("S", "L", "W"):
        row = evidence.get(role)
        if not isinstance(row, Mapping):
            raise ValueError(f"missing {role} identity")
        required = {
            "role", "pid", "parent_pid", "creation_filetime", "image_path",
            "image_sha256", "argv", "cwd", "environment_sha256", "job_member",
            "process_handle_access_mask", "handle_acquisition_filetime",
            "handle_retained_at_r", "live_at_r",
        }
        if not required <= set(row):
            raise ValueError(f"incomplete {role} identity")
        if row["role"] != role:
            raise ValueError(f"{role} role mismatch")
        for key in ("pid", "parent_pid", "creation_filetime", "handle_acquisition_filetime"):
            if not isinstance(row[key], int) or isinstance(row[key], bool) or row[key] < 0:
                raise ValueError(f"invalid {role} {key}")
        if not isinstance(row["image_path"], str) or not row["image_path"]:
            raise ValueError(f"invalid {role} image path")
        _require_hex_digest(row["image_sha256"], f"{role}.image_sha256")
        _require_hex_digest(row["environment_sha256"], f"{role}.environment_sha256")
        if not isinstance(row["argv"], list) or not all(
            isinstance(item, str) for item in row["argv"]
        ):
            raise ValueError(f"invalid {role} argv")
        if not isinstance(row["cwd"], str) or not row["cwd"]:
            raise ValueError(f"invalid {role} cwd")
        if row["process_handle_access_mask"] != PROCESS_HANDLE_ACCESS_MASK:
            raise ValueError(f"invalid {role} process access mask")
        if row["handle_retained_at_r"] is not True or row["live_at_r"] is not True:
            raise ValueError(f"{role} was not retained and live at R")
    s_row = evidence["S"]
    l_row = evidence["L"]
    w_row = evidence["W"]
    if len({s_row["pid"], l_row["pid"], w_row["pid"]}) != 3:
        raise ValueError("S/L/W PIDs must be distinct")
    if s_row["job_member"] is not False:
        raise ValueError("S must be outside the child job")
    if l_row["job_member"] is not True or w_row["job_member"] is not True:
        raise ValueError("L and W must be job members")
    if l_row["parent_pid"] != s_row["pid"] or w_row["parent_pid"] != l_row["pid"]:
        raise ValueError("S -> L -> W parent chain mismatch")
    if l_row.get("child_pids") != [w_row["pid"]]:
        raise ValueError("L must have exactly W as child")
    if w_row.get("child_count") != 0 or w_row.get("used_os_exit_zero") is not True:
        raise ValueError("W child/exit contract mismatch")
    job = evidence.get("job")
    exits = evidence.get("exits")
    if not isinstance(job, Mapping) or not isinstance(exits, Mapping):
        raise ValueError("job/exits evidence absent")
    expected_census = sorted([l_row["pid"], w_row["pid"]])
    if (
        job.get("total_processes") != 2
        or job.get("active_at_r") != 2
        or sorted(job.get("pid_census", [])) != expected_census
        or job.get("active_after_exit") != 0
        or job.get("kill_on_close") is not True
        or job.get("active_process_limit") != 2
        or exits.get("launcher") != 0
        or exits.get("worker") != 0
    ):
        raise ValueError("job census or exit evidence mismatch")
    return True


def _pre_r_topology(topology: Mapping[str, Any]) -> dict[str, Any]:
    for role in ("S", "L", "W"):
        row = topology.get(role)
        if not isinstance(row, Mapping):
            raise ValueError(f"missing pre-R {role} identity")
        if row.get("role") != role or row.get("live_at_r") is not True:
            raise ValueError(f"invalid pre-R {role} identity")
        if row.get("handle_retained_at_r") is not True:
            raise ValueError(f"pre-R {role} handle not retained")
    if len({topology[role].get("pid") for role in ("S", "L", "W")}) != 3:
        raise ValueError("pre-R S/L/W PIDs must be distinct")
    if topology["S"].get("job_member") is not False:
        raise ValueError("S must be outside the child job")
    if topology["L"].get("job_member") is not True or topology["W"].get("job_member") is not True:
        raise ValueError("L/W must be in the child job")
    if topology["L"].get("parent_pid") != topology["S"].get("pid"):
        raise ValueError("S/L parent mismatch")
    if topology["W"].get("parent_pid") != topology["L"].get("pid"):
        raise ValueError("L/W parent mismatch")
    if topology["L"].get("child_pids") != [topology["W"].get("pid")]:
        raise ValueError("L child census mismatch")
    if topology["W"].get("child_count") != 0:
        raise ValueError("W must be childless")
    job = topology.get("job")
    if not isinstance(job, Mapping):
        raise ValueError("pre-R job census missing")
    if (
        job.get("total_processes") != 2
        or job.get("active_at_r") != 2
        or sorted(job.get("pid_census", []))
        != sorted([topology["L"]["pid"], topology["W"]["pid"]])
        or job.get("kill_on_close") is not True
        or job.get("active_process_limit") != 2
    ):
        raise ValueError("pre-R job census mismatch")
    projected_job = {
        key: job[key]
        for key in (
            "total_processes", "active_at_r", "pid_census",
            "kill_on_close", "active_process_limit",
        )
    }
    identity_keys = {
        "role", "pid", "parent_pid", "creation_filetime", "image_path",
        "image_sha256", "argv", "cwd", "environment_sha256", "job_member",
        "process_handle_access_mask", "handle_acquisition_filetime",
        "handle_retained_at_r", "live_at_r",
    }
    projected = {
        role: {
            key: topology[role][key]
            for key in identity_keys
        }
        for role in ("S", "L", "W")
    }
    projected["L"]["child_pids"] = list(topology["L"]["child_pids"])
    projected["W"]["child_count"] = topology["W"]["child_count"]
    return {**projected, "job": projected_job}


def control_event_names(intent_sha256: str) -> dict[str, str]:
    _require_hex_digest(intent_sha256, "intent_sha256")
    prefix = intent_sha256[:32]
    return {
        label: rf"Local\M245_{prefix}_{label}"
        for label in ("READY", "GO", "DONE", "EXIT")
    }


def validate_control_event_creation(*, created_new: bool, last_error: int) -> bool:
    if created_new is True and last_error == 0:
        return True
    if created_new is False and last_error == ERROR_ALREADY_EXISTS:
        raise FileExistsError("M245 control event already exists")
    raise OSError(last_error, "M245 control event creation was not exclusive")


def _parse_canonical_documents(encoded: bytes) -> list[dict[str, Any]]:
    try:
        text = encoded.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("worker stdout is not UTF-8") from exc
    decoder = json.JSONDecoder()
    documents: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(text):
        if text[cursor].isspace():
            cursor += 1
            continue
        try:
            payload, end = decoder.raw_decode(text, cursor)
        except json.JSONDecodeError as exc:
            raise ValueError("worker transcript is truncated or invalid") from exc
        if not isinstance(payload, dict):
            raise ValueError("worker transcript record is not an object")
        documents.append(payload)
        cursor = end
    if b"".join(canonical_json_bytes(row) for row in documents) != encoded:
        raise ValueError("worker transcript is not exact concatenated canonical JSON")
    return documents


def validate_worker_transcript(
    *,
    stdout_bytes: bytes,
    stderr_bytes: bytes,
    intent_sha256: str,
    v2_sha256: str,
    worker_pid: int,
) -> bool:
    _require_hex_digest(intent_sha256, "intent_sha256")
    _require_hex_digest(v2_sha256, "v2_sha256")
    if stderr_bytes != b"":
        raise ValueError("worker stderr must be empty")
    documents = _parse_canonical_documents(stdout_bytes)
    if len(documents) != 2:
        raise ValueError("worker must emit exactly READY and DONE")
    ready, done = documents
    if (
        ready.get("artifact") != "M245_W_READY"
        or ready.get("status") != "READY_PRE_NUMPY"
        or ready.get("pid") != worker_pid
        or ready.get("intent_sha256") != intent_sha256
        or ready.get("numpy_modules") != []
        or ready.get("job_member") is not True
    ):
        raise ValueError("worker READY record mismatch")
    v2 = done.get("v2")
    if (
        done.get("artifact") != "M245_W_DONE"
        or done.get("status") != "V2_PUBLISHED_WAITING_EXIT"
        or done.get("pid") != worker_pid
        or done.get("intent_sha256") != intent_sha256
        or not isinstance(v2, Mapping)
        or v2.get("sha256") != v2_sha256
    ):
        raise ValueError("worker DONE record mismatch")
    return True


def _nonnegative_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    observed = float(value)
    if not math.isfinite(observed) or observed < 0.0:
        raise ValueError(f"{label} must be finite and nonnegative")
    return observed


def evaluate_resource_gate(
    *,
    processes: Mapping[str, Mapping[str, Any]],
    working_set_samples: Sequence[Mapping[str, Any]],
    wall_r_seconds: float,
    wall_child_exit_seconds: float,
) -> dict[str, Any]:
    wall_r = _nonnegative_number(wall_r_seconds, "wall_r_seconds")
    wall_exit = _nonnegative_number(
        wall_child_exit_seconds, "wall_child_exit_seconds"
    )
    chronology_pass = wall_exit >= wall_r
    if set(processes) != {"S", "L", "W"}:
        raise ValueError("resource process census must be exactly S/L/W")
    normalized_processes: dict[str, dict[str, int]] = {}
    lifetime_sum = 0
    cpu_sum = 0
    required = {
        "peak_working_set_lifetime_to_endpoint",
        "kernel_endpoint_100ns",
        "kernel_final_100ns",
        "user_endpoint_100ns",
        "user_final_100ns",
    }
    for role in ("S", "L", "W"):
        row = processes[role]
        if not isinstance(row, Mapping) or not required <= set(row):
            raise ValueError(f"incomplete {role} resource evidence")
        clean: dict[str, int] = {}
        for key in required:
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"invalid {role}.{key}")
            clean[key] = value
        if (
            clean["kernel_final_100ns"] < clean["kernel_endpoint_100ns"]
            or clean["user_final_100ns"] < clean["user_endpoint_100ns"]
        ):
            raise ValueError(f"{role} CPU counter rollback")
        lifetime_sum += clean["peak_working_set_lifetime_to_endpoint"]
        cpu_sum += max(clean["kernel_endpoint_100ns"], clean["kernel_final_100ns"])
        cpu_sum += max(clean["user_endpoint_100ns"], clean["user_final_100ns"])
        normalized_processes[role] = clean
    if not working_set_samples:
        raise ValueError("working-set sample series is empty")
    clean_samples: list[dict[str, Any]] = []
    prior: float | None = None
    gaps: list[float] = []
    sampled_peak = 0
    for index, sample in enumerate(working_set_samples):
        if not isinstance(sample, Mapping) or not {"seconds", "S", "L", "W"} <= set(sample):
            raise ValueError("incomplete working-set sample")
        seconds = _nonnegative_number(sample["seconds"], "sample.seconds")
        if prior is not None and seconds < prior:
            raise ValueError("working-set timestamps moved backward")
        if prior is not None:
            gaps.append(seconds - prior)
        prior = seconds
        clean = {"seconds": seconds}
        concurrent = 0
        for role in ("S", "L", "W"):
            raw = sample[role]
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                raise ValueError(f"invalid sampled {role} working set")
            clean[role] = raw
            concurrent += raw
        if "retained_handle_roles" in sample:
            present_roles = sample["retained_handle_roles"]
            if (
                not isinstance(present_roles, list)
                or any(role not in {"S", "L", "W"} for role in present_roles)
                or len(present_roles) != len(set(present_roles))
            ):
                raise ValueError("invalid sample retained-handle census")
            clean["retained_handle_roles"] = list(present_roles)
        sampled_peak = max(sampled_peak, concurrent)
        clean_samples.append(clean)
    if prior is None:
        raise ValueError("working-set sample series is empty")
    if prior > wall_exit:
        if prior - wall_exit > 1e-9:
            raise ValueError("sample timestamp occurs after frozen child-exit wall")
    if not gaps:
        raise ValueError("at least two working-set samples are required")
    maximum_gap = max(gaps)
    rss_gate = max(sampled_peak, lifetime_sum)
    passed = (
        chronology_pass
        and rss_gate <= RSS_CAP_BYTES
        and wall_r <= WALL_CAP_SECONDS
        and wall_exit <= CHILD_EXIT_WALL_CAP_SECONDS
        and maximum_gap <= MAXIMUM_GAP_SECONDS
    )
    return {
        "pass": passed,
        "rss_sampled_bytes": sampled_peak,
        "rss_lifetime_to_endpoint_sum_bytes": lifetime_sum,
        "rss_gate_bytes": rss_gate,
        "cpu_sum_100ns": cpu_sum,
        "cpu_sum_seconds": cpu_sum / 10_000_000.0,
        "wall_r_seconds": wall_r,
        "wall_child_exit_seconds": wall_exit,
        "maximum_gap_seconds": maximum_gap,
        "first_sample_seconds": clean_samples[0]["seconds"],
        "caps": {
            "rss_bytes": RSS_CAP_BYTES,
            "wall_seconds": WALL_CAP_SECONDS,
            "child_exit_wall_seconds": CHILD_EXIT_WALL_CAP_SECONDS,
            "maximum_gap_seconds": MAXIMUM_GAP_SECONDS,
        },
        "processes": normalized_processes,
        "working_set_samples": clean_samples,
    }


def build_provisional_receipt(
    *,
    intent_sha256: str,
    v2_sha256: str,
    authority_sha256: Mapping[str, str],
    v2_receipt: Mapping[str, Any],
    topology: Mapping[str, Any],
) -> dict[str, Any]:
    _require_hex_digest(intent_sha256, "intent_sha256")
    _require_hex_digest(v2_sha256, "v2_sha256")
    pre_r_topology = _pre_r_topology(topology)
    if v2_receipt.get("sha256") != v2_sha256:
        raise ValueError("V2 receipt hash mismatch")
    return {
        "artifact": "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT",
        "status": "PROVISIONAL_REQUIRES_T",
        "intent_sha256": intent_sha256,
        "v2_sha256": v2_sha256,
        "authority_sha256": dict(sorted(authority_sha256.items())),
        "v2": dict(v2_receipt),
        "topology": pre_r_topology,
        "terminal_witness_required": WITNESS_T.name,
    }


def build_terminal_witness(
    *,
    intent_sha256: str,
    v2_sha256: str,
    r_sha256: str,
    r_bytes: int,
    resources: Mapping[str, Any],
    exits: Mapping[str, Any],
    identities: Mapping[str, Any],
    sampling: Mapping[str, Any],
    pre_t_state: Mapping[str, Any],
    job_census: Mapping[str, Any],
    expected_t_path: str,
) -> dict[str, Any]:
    for label, digest in (
        ("intent_sha256", intent_sha256),
        ("v2_sha256", v2_sha256),
        ("r_sha256", r_sha256),
    ):
        _require_hex_digest(digest, label)
    if isinstance(r_bytes, bool) or not isinstance(r_bytes, int) or r_bytes <= 0:
        raise ValueError("R byte length must be positive")
    if resources.get("pass") is not True:
        raise ValueError("terminal witness cannot carry a failing resource gate")
    if expected_t_path != WITNESS_T.name:
        raise ValueError("terminal witness path mismatch")
    if dict(pre_t_state) != {
        "intent": True, "v2": True, "r": True, "temp": False, "t": False
    }:
        raise ValueError("pre-T namespace state mismatch")
    return {
        "artifact": "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS",
        "status": "PASS_M245_FIXTURE_AUTHORITY_BOUND",
        "intent_sha256": intent_sha256,
        "v2_sha256": v2_sha256,
        "r_sha256": r_sha256,
        "r_bytes": r_bytes,
        "resources": dict(resources),
        "exits": dict(exits),
        "identities": dict(identities),
        "sampling": dict(sampling),
        "pre_t_state": {
            **dict(pre_t_state),
            "paths": {
                "intent": str(INTENT),
                "v2": str(V2_FINAL),
                "r": str(RECEIPT_R),
                "temp": str(V2_TEMP),
                "t": str(WITNESS_T),
            },
        },
        "job_census": dict(job_census),
        "expected_t_path": expected_t_path,
        "publication_verification_pending_independent_audit": True,
    }


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


def _has_reparse_attribute(path: Path) -> bool:
    if os.name != "nt":
        return Path(path).is_symlink()
    kernel32 = _kernel32()
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
    cursor = Path(boundary.anchor)
    for part in boundary.parts[1:]:
        cursor = cursor / part
        if not cursor.is_dir() or cursor.is_symlink() or _has_reparse_attribute(cursor):
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: reparse root component: {cursor}")
    return resolved


def _require_plain_contained_file(path: Path, root: Path) -> None:
    target = Path(path)
    resolved_root = _require_plain_root(Path(root))
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


def _publish_owned_json(
    path: Path, payload: Mapping[str, Any]
) -> tuple[dict[str, Any], bytes, str]:
    encoded = canonical_json_bytes(payload)
    _write_exclusive_fsync(path, encoded)
    observed = Path(path).read_bytes()
    if observed != encoded:
        raise IOError(f"durable byte mismatch: {path}")
    parsed = json.loads(observed.decode("utf-8"))
    if parsed != dict(payload) or canonical_json_bytes(parsed) != observed:
        raise IOError(f"durable canonical parse mismatch: {path}")
    digest = sha256_bytes(observed)
    return (
        {
            "path": str(Path(path)),
            "bytes": len(observed),
            "sha256": digest,
            "reopened_bytes_equal": True,
            "reopened_parse_equal": True,
        },
        observed,
        digest,
    )


def _publish_r_and_capture_endpoint(
    payload: Mapping[str, Any]
) -> tuple[dict[str, Any], bytes, str, int]:
    encoded = canonical_json_bytes(payload)
    _write_exclusive_fsync(RECEIPT_R, encoded)
    observed = RECEIPT_R.read_bytes()
    if observed != encoded:
        raise IOError("R durable byte mismatch")
    parsed = json.loads(observed.decode("utf-8"))
    if parsed != dict(payload) or canonical_json_bytes(parsed) != observed:
        raise IOError("R durable canonical parse mismatch")
    digest = sha256_bytes(observed)
    endpoint_filetime = _precise_filetime()
    return (
        {
            "path": str(RECEIPT_R),
            "bytes": len(observed),
            "sha256": digest,
            "reopened_bytes_equal": True,
            "reopened_parse_equal": True,
        },
        observed,
        digest,
        endpoint_filetime,
    )


def _verify_static_validation(actual_hashes: Mapping[str, str]) -> dict[str, Any]:
    _require_plain_contained_file(STATIC_VALIDATION_RECEIPT, AUTHORITY_DIRECTORY)
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
        if (
            not isinstance(identity, str)
            or identity != identity.strip().casefold()
            or not identity
            or not all(
                char.isascii() and (char.isalnum() or char in "-_")
                for char in identity
            )
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


def _verify_authority_and_sources() -> tuple[
    dict[str, str], dict[str, Any], dict[str, Any]
]:
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
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: hash mismatch: {name}")
        observed[name] = digest
        frozen_authority_bytes[name] = encoded
    manifest = json.loads(
        frozen_authority_bytes["M245_FROZEN_MANIFEST_V1_20260810.json"].decode("utf-8")
    )
    for relative, expected in manifest["parent_hashes_repo_relative"].items():
        path = REPOSITORY_ROOT / Path(relative)
        _require_plain_contained_file(path, REPOSITORY_ROOT)
        digest = sha256_file(path)
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: parent hash mismatch: {relative}")
        observed[f"repository::{relative}"] = digest
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
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: runtime hash mismatch: {relative}")
        observed[f"runtime::{relative}"] = digest
    base_files = {
        runtime["base_interpreter_base_relative"]: runtime["base_interpreter_sha256"],
        runtime["base_python_dll_base_relative"]: runtime["base_python_dll_sha256"],
    }
    for relative, expected in base_files.items():
        path = BASE_RUNTIME_ROOT / Path(relative)
        _require_plain_contained_file(path, BASE_RUNTIME_ROOT)
        digest = sha256_file(path)
        if digest != expected:
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: base hash mismatch: {relative}")
        observed[f"base::{relative}"] = digest
    for path in (SUPERVISOR_SOURCE, WORKER_SOURCE, TRANSPORT_TEST, TDD_RECEIPT):
        _require_plain_contained_file(path, AUTHORITY_DIRECTORY)
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


def _intent_payload(
    authority_sha256: Mapping[str, str],
    static_validation: Mapping[str, Any],
) -> dict[str, Any]:
    child_environment = sanitized_child_environment()
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
        "source_sha256": dict(sorted(static_validation["audited_sha256"].items())),
        "static_validation_receipt_sha256": static_validation["sha256"],
        "supervisor_argv": supervisor_argv(),
        "worker_argv": worker_argv(),
        "cwd": str(AUTHORITY_DIRECTORY),
        "child_environment": dict(sorted(child_environment.items())),
        "child_environment_sha256": _environment_digest(child_environment),
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


def _validate_intent_payload(
    payload: Mapping[str, Any],
    *,
    authority_sha256: Mapping[str, str],
    static_validation: Mapping[str, Any],
) -> bool:
    expected = _intent_payload(authority_sha256, static_validation)
    if dict(payload) != expected:
        raise RuntimeError("intent schema or value mismatch")
    return True


def _filetime_value(value: FILETIME) -> int:
    return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)


def _precise_filetime() -> int:
    kernel32 = _kernel32()
    kernel32.GetSystemTimePreciseAsFileTime.argtypes = [ctypes.POINTER(FILETIME)]
    kernel32.GetSystemTimePreciseAsFileTime.restype = None
    value = FILETIME()
    ctypes.set_last_error(0)
    kernel32.GetSystemTimePreciseAsFileTime(ctypes.byref(value))
    observed = _filetime_value(value)
    if observed <= 0:
        raise OSError(ctypes.get_last_error(), "GetSystemTimePreciseAsFileTime failed")
    return observed


def _open_process(pid: int) -> tuple[int, int]:
    kernel32 = _kernel32()
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    handle = kernel32.OpenProcess(PROCESS_HANDLE_ACCESS_MASK, False, pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), f"OpenProcess failed: {pid}")
    acquired = _precise_filetime()
    return int(handle), acquired


def _process_times(handle: int) -> dict[str, int]:
    kernel32 = _kernel32()
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    creation = FILETIME()
    exit_time = FILETIME()
    kernel = FILETIME()
    user = FILETIME()
    if not kernel32.GetProcessTimes(
        handle,
        ctypes.byref(creation), ctypes.byref(exit_time),
        ctypes.byref(kernel), ctypes.byref(user),
    ):
        raise OSError(ctypes.get_last_error(), "GetProcessTimes failed")
    return {
        "creation_filetime": _filetime_value(creation),
        "exit_filetime": _filetime_value(exit_time),
        "kernel_100ns": _filetime_value(kernel),
        "user_100ns": _filetime_value(user),
    }


def _process_memory(handle: int) -> dict[str, int]:
    kernel32 = _kernel32()
    if _exit_code(handle) != STILL_ACTIVE:
        return {"working_set": 0, "peak_working_set": 0}
    kernel32.K32GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD
    ]
    kernel32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    if not kernel32.K32GetProcessMemoryInfo(
        handle, ctypes.byref(counters), ctypes.sizeof(counters)
    ):
        if _exit_code(handle) != STILL_ACTIVE:
            return {"working_set": 0, "peak_working_set": 0}
        raise OSError(ctypes.get_last_error(), "K32GetProcessMemoryInfo failed")
    return {
        "working_set": int(counters.WorkingSetSize),
        "peak_working_set": int(counters.PeakWorkingSetSize),
    }


def _exit_code(handle: int) -> int:
    kernel32 = _kernel32()
    kernel32.GetExitCodeProcess.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    value = wintypes.DWORD()
    if not kernel32.GetExitCodeProcess(handle, ctypes.byref(value)):
        raise OSError(ctypes.get_last_error(), "GetExitCodeProcess failed")
    return int(value.value)


def _wait_process(handle: int, milliseconds: int = 30_000) -> int:
    kernel32 = _kernel32()
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    result = int(kernel32.WaitForSingleObject(handle, milliseconds))
    if result == WAIT_TIMEOUT:
        raise TimeoutError("process exit timed out")
    if result != WAIT_OBJECT_0:
        raise OSError(ctypes.get_last_error(), "process wait failed")
    code = _exit_code(handle)
    if code == STILL_ACTIVE:
        raise RuntimeError("signaled process remains active")
    return code


def _actual_image_path(handle: int) -> str:
    kernel32 = _kernel32()
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    capacity = wintypes.DWORD(32768)
    buffer = ctypes.create_unicode_buffer(capacity.value)
    if not kernel32.QueryFullProcessImageNameW(
        handle, 0, buffer, ctypes.byref(capacity)
    ):
        raise OSError(ctypes.get_last_error(), "QueryFullProcessImageNameW failed")
    return buffer.value


def _process_snapshot() -> dict[int, int]:
    kernel32 = _kernel32()
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Process32FirstW.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)
    ]
    kernel32.Process32FirstW.restype = wintypes.BOOL
    kernel32.Process32NextW.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)
    ]
    kernel32.Process32NextW.restype = wintypes.BOOL
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")
    result: dict[int, int] = {}
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            result[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        _close_handle(snapshot)
    return result


def _is_process_in_job(handle: int, job: int | None) -> bool:
    kernel32 = _kernel32()
    kernel32.IsProcessInJob.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)
    ]
    kernel32.IsProcessInJob.restype = wintypes.BOOL
    answer = wintypes.BOOL()
    if not kernel32.IsProcessInJob(handle, job, ctypes.byref(answer)):
        raise OSError(ctypes.get_last_error(), "IsProcessInJob failed")
    return bool(answer.value)


def _identity(
    *,
    role: str,
    handle: int,
    pid: int,
    parent_pid: int,
    expected_image: Path,
    expected_image_sha256: str,
    argv: Sequence[str],
    environment_sha256: str,
    job: int | None,
    handle_acquisition_filetime: int,
) -> dict[str, Any]:
    image = _actual_image_path(handle)
    if _normalized(image) != _normalized(expected_image):
        raise RuntimeError(f"{role} OS image path mismatch")
    _require_plain_contained_file(
        Path(image), BASE_RUNTIME_ROOT if role in {"S", "W"} else RUNTIME_ROOT
    )
    image_sha256 = sha256_file(Path(image))
    if image_sha256 != expected_image_sha256:
        raise RuntimeError(f"{role} OS image hash mismatch")
    creation = _process_times(handle)["creation_filetime"]
    return {
        "role": role,
        "pid": pid,
        "parent_pid": parent_pid,
        "creation_filetime": creation,
        "image_path": image,
        "image_sha256": image_sha256,
        "argv": list(argv),
        "cwd": str(AUTHORITY_DIRECTORY),
        "environment_sha256": environment_sha256,
        "job_member": _is_process_in_job(handle, job),
        "process_handle_access_mask": PROCESS_HANDLE_ACCESS_MASK,
        "handle_acquisition_filetime": handle_acquisition_filetime,
        "handle_retained_at_r": True,
        "live_at_r": True,
    }


def _quote_windows_argument(argument: str) -> str:
    if argument and not any(char in ' \t\n\v"' for char in argument):
        return argument
    output = ['"']
    slashes = 0
    for char in argument:
        if char == "\\":
            slashes += 1
            continue
        if char == '"':
            output.append("\\" * (slashes * 2 + 1))
            output.append('"')
        else:
            output.append("\\" * slashes)
            output.append(char)
        slashes = 0
    output.append("\\" * (slashes * 2))
    output.append('"')
    return "".join(output)


def _command_line(argv: Sequence[str]) -> str:
    return " ".join(_quote_windows_argument(item) for item in argv)


def _environment_block(environment: Mapping[str, str]) -> str:
    ordered = sorted(environment.items(), key=lambda row: row[0].casefold())
    return "\0".join(f"{key}={value}" for key, value in ordered) + "\0\0"


def _create_pipe() -> tuple[int, int]:
    kernel32 = _kernel32()
    kernel32.CreatePipe.argtypes = [
        ctypes.POINTER(wintypes.HANDLE), ctypes.POINTER(wintypes.HANDLE),
        ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.DWORD,
    ]
    kernel32.CreatePipe.restype = wintypes.BOOL
    kernel32.SetHandleInformation.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD
    ]
    kernel32.SetHandleInformation.restype = wintypes.BOOL
    attributes = SECURITY_ATTRIBUTES(
        ctypes.sizeof(SECURITY_ATTRIBUTES), None, True
    )
    read_handle = wintypes.HANDLE()
    write_handle = wintypes.HANDLE()
    if not kernel32.CreatePipe(
        ctypes.byref(read_handle), ctypes.byref(write_handle),
        ctypes.byref(attributes), 0,
    ):
        raise OSError(ctypes.get_last_error(), "CreatePipe failed")
    if not kernel32.SetHandleInformation(read_handle, HANDLE_FLAG_INHERIT, 0):
        _close_handle(read_handle.value)
        _close_handle(write_handle.value)
        raise OSError(ctypes.get_last_error(), "SetHandleInformation failed")
    return int(read_handle.value), int(write_handle.value)


def _read_available(handle: int) -> bytes:
    kernel32 = _kernel32()
    kernel32.PeekNamedPipe.argtypes = [
        wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.PeekNamedPipe.restype = wintypes.BOOL
    kernel32.ReadFile.argtypes = [
        wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID,
    ]
    kernel32.ReadFile.restype = wintypes.BOOL
    output = bytearray()
    while True:
        available = wintypes.DWORD()
        if not kernel32.PeekNamedPipe(
            handle, None, 0, None, ctypes.byref(available), None
        ):
            error = ctypes.get_last_error()
            if error == ERROR_BROKEN_PIPE:
                break
            raise OSError(error, "PeekNamedPipe failed")
        if available.value == 0:
            break
        size = min(int(available.value), 65536)
        buffer = ctypes.create_string_buffer(size)
        read = wintypes.DWORD()
        if not kernel32.ReadFile(
            handle, buffer, size, ctypes.byref(read), None
        ):
            error = ctypes.get_last_error()
            if error == ERROR_BROKEN_PIPE:
                break
            raise OSError(error, "ReadFile failed")
        output.extend(buffer.raw[: read.value])
    return bytes(output)


def _create_control_events(names: Mapping[str, str]) -> dict[str, int]:
    kernel32 = _kernel32()
    kernel32.CreateEventW.argtypes = [
        ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.BOOL,
        wintypes.BOOL, wintypes.LPCWSTR,
    ]
    kernel32.CreateEventW.restype = wintypes.HANDLE
    handles: dict[str, int] = {}
    try:
        for label in ("READY", "GO", "DONE", "EXIT"):
            ctypes.set_last_error(0)
            handle = kernel32.CreateEventW(
                None, CONTROL_EVENT_MANUAL_RESET,
                CONTROL_EVENT_INITIAL_STATE, names[label],
            )
            error = ctypes.get_last_error()
            created_new = bool(handle) and error != ERROR_ALREADY_EXISTS
            if handle and not created_new:
                _close_handle(int(handle))
            validate_control_event_creation(
                created_new=created_new, last_error=error
            )
            handles[label] = int(handle)
        return handles
    except BaseException:
        for handle in handles.values():
            _close_handle(handle)
        raise


def _set_event(handle: int) -> None:
    kernel32 = _kernel32()
    kernel32.SetEvent.argtypes = [wintypes.HANDLE]
    kernel32.SetEvent.restype = wintypes.BOOL
    if not kernel32.SetEvent(handle):
        raise OSError(ctypes.get_last_error(), "SetEvent failed")


def _wait_event(handle: int, milliseconds: int = 30_000) -> None:
    kernel32 = _kernel32()
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    result = int(kernel32.WaitForSingleObject(handle, milliseconds))
    if result == WAIT_TIMEOUT:
        raise TimeoutError("M245 control-event wait timed out")
    if result != WAIT_OBJECT_0:
        raise OSError(ctypes.get_last_error(), "WaitForSingleObject failed")


def _create_job() -> tuple[int, int]:
    kernel32 = _kernel32()
    kernel32.CreateJobObjectW.argtypes = [
        ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.LPCWSTR
    ]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.CreateIoCompletionPort.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, ctypes.c_size_t, wintypes.DWORD
    ]
    kernel32.CreateIoCompletionPort.restype = wintypes.HANDLE
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise OSError(ctypes.get_last_error(), "CreateJobObjectW failed")
    port: int | None = None
    try:
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS
        )
        limits.BasicLimitInformation.ActiveProcessLimit = 2
        if not kernel32.SetInformationJobObject(
            job, JobObjectExtendedLimitInformation,
            ctypes.byref(limits), ctypes.sizeof(limits),
        ):
            raise OSError(ctypes.get_last_error(), "job limit configuration failed")
        raw_port = kernel32.CreateIoCompletionPort(
            INVALID_HANDLE_VALUE, None, 0, 1
        )
        if not raw_port:
            raise OSError(ctypes.get_last_error(), "CreateIoCompletionPort failed")
        port = int(raw_port)
        association = JOBOBJECT_ASSOCIATE_COMPLETION_PORT(
            ctypes.c_void_p(1), raw_port
        )
        if not kernel32.SetInformationJobObject(
            job, JobObjectAssociateCompletionPortInformation,
            ctypes.byref(association), ctypes.sizeof(association),
        ):
            raise OSError(ctypes.get_last_error(), "job completion-port association failed")
        return int(job), port
    except BaseException:
        if port:
            _close_handle(port)
        _close_handle(job)
        raise


def _job_accounting(job: int) -> dict[str, int]:
    kernel32 = _kernel32()
    kernel32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryInformationJobObject.restype = wintypes.BOOL
    accounting = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
    returned = wintypes.DWORD()
    if not kernel32.QueryInformationJobObject(
        job, JobObjectBasicAccountingInformation,
        ctypes.byref(accounting), ctypes.sizeof(accounting),
        ctypes.byref(returned),
    ):
        raise OSError(ctypes.get_last_error(), "QueryInformationJobObject failed")
    return {
        "total_processes": int(accounting.TotalProcesses),
        "active_processes": int(accounting.ActiveProcesses),
        "total_terminated_processes": int(accounting.TotalTerminatedProcesses),
    }


def _drain_job_notifications(port: int, timeout_ms: int = 0) -> list[dict[str, int]]:
    kernel32 = _kernel32()
    kernel32.GetQueuedCompletionStatus.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(wintypes.LPVOID),
        wintypes.DWORD,
    ]
    kernel32.GetQueuedCompletionStatus.restype = wintypes.BOOL
    records: list[dict[str, int]] = []
    wait = timeout_ms
    while True:
        message = wintypes.DWORD()
        key = ctypes.c_size_t()
        overlapped = wintypes.LPVOID()
        ctypes.set_last_error(0)
        ok = kernel32.GetQueuedCompletionStatus(
            port, ctypes.byref(message), ctypes.byref(key),
            ctypes.byref(overlapped), wait,
        )
        if not ok:
            error = ctypes.get_last_error()
            if error == WAIT_TIMEOUT:
                break
            raise OSError(error, "GetQueuedCompletionStatus failed")
        records.append({
            "message": int(message.value),
            "pid": int(ctypes.cast(overlapped, ctypes.c_void_p).value or 0),
            "completion_key": int(key.value),
            "filetime": _precise_filetime(),
        })
        wait = 0
    return records


def _create_suspended_launcher(
    *, stdout_write: int, stderr_write: int
) -> PROCESS_INFORMATION:
    kernel32 = _kernel32()
    kernel32.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR,
        ctypes.POINTER(SECURITY_ATTRIBUTES), ctypes.POINTER(SECURITY_ATTRIBUTES),
        wintypes.BOOL, wintypes.DWORD, wintypes.LPVOID, wintypes.LPCWSTR,
        ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION),
    ]
    kernel32.CreateProcessW.restype = wintypes.BOOL
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.DWORD,
        wintypes.DWORD, wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    attributes = SECURITY_ATTRIBUTES(
        ctypes.sizeof(SECURITY_ATTRIBUTES), None, True
    )
    stdin_handle = kernel32.CreateFileW(
        "NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
        ctypes.byref(attributes), OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None,
    )
    if stdin_handle == INVALID_HANDLE_VALUE:
        raise OSError(ctypes.get_last_error(), "opening inheritable NUL stdin failed")
    startup = STARTUPINFOW()
    startup.cb = ctypes.sizeof(startup)
    startup.dwFlags = STARTF_USESTDHANDLES
    startup.hStdInput = stdin_handle
    startup.hStdOutput = stdout_write
    startup.hStdError = stderr_write
    process = PROCESS_INFORMATION()
    command = ctypes.create_unicode_buffer(_command_line(worker_argv()))
    environment = ctypes.create_unicode_buffer(
        _environment_block(sanitized_child_environment())
    )
    try:
        created = bool(kernel32.CreateProcessW(
            str(WORKER_LOGICAL_INTERPRETER), command,
            None, None, True,
            CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT,
            environment, str(AUTHORITY_DIRECTORY),
            ctypes.byref(startup), ctypes.byref(process),
        ))
        creation_error = ctypes.get_last_error() if not created else 0
    finally:
        _close_handle(int(stdin_handle))
    if not created:
        raise OSError(creation_error, "CreateProcessW launcher failed")
    return process


def _assign_to_job(job: int, process: PROCESS_INFORMATION) -> None:
    kernel32 = _kernel32()
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    if not kernel32.AssignProcessToJobObject(job, process.hProcess):
        assignment_error = ctypes.get_last_error()
        kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel32.TerminateProcess.restype = wintypes.BOOL
        terminated = bool(kernel32.TerminateProcess(process.hProcess, 0xE2450001))
        termination_error = ctypes.get_last_error() if not terminated else 0
        try:
            _wait_process(int(process.hProcess), 5_000)
        except BaseException as exc:
            raise RuntimeError(
                "unassigned suspended launcher could not be reaped; "
                f"assignment_error={assignment_error}, "
                f"termination_error={termination_error}"
            ) from exc
        raise OSError(assignment_error, "AssignProcessToJobObject failed")


def _resume_launcher(process: PROCESS_INFORMATION) -> None:
    kernel32 = _kernel32()
    kernel32.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel32.ResumeThread.restype = wintypes.DWORD
    previous_suspend_count = int(kernel32.ResumeThread(process.hThread))
    if previous_suspend_count != 1:
        if previous_suspend_count == 0xFFFFFFFF:
            raise OSError(ctypes.get_last_error(), "ResumeThread failed")
        raise RuntimeError(
            f"launcher suspend-count drift: {previous_suspend_count}"
        )


class _ResourceSampler:
    def __init__(self, s_handle: int, s_creation_filetime: int) -> None:
        self._handles: dict[str, int | None] = {
            "S": s_handle, "L": None, "W": None
        }
        self._t0 = s_creation_filetime
        self._samples: list[dict[str, Any]] = []
        self._last_sample_filetime = s_creation_filetime
        self._lock = threading.Lock()
        self._sample_gate = threading.Lock()
        self._enabled = threading.Event()
        self._enabled.set()
        self._stop = threading.Event()
        self._error: BaseException | None = None
        self._thread = threading.Thread(
            target=self._run, name="m245-resource-sampler", daemon=True
        )

    def set_handle(self, role: str, handle: int) -> None:
        if role not in {"L", "W"}:
            raise ValueError("only child handles may be installed")
        with self._lock:
            if self._handles[role] is not None:
                raise RuntimeError(f"{role} sampler handle already installed")
            self._handles[role] = handle

    def _sample_once(self, *, periodic: bool = False) -> dict[str, Any] | None:
        with self._sample_gate:
            if periodic and not self._enabled.is_set():
                return None
            now = _precise_filetime()
            if now < self._t0:
                raise RuntimeError("resource sample clock precedes S creation")
            if now < self._last_sample_filetime:
                raise RuntimeError("resource sample clock moved backward")
            self._last_sample_filetime = now
            with self._lock:
                handles = dict(self._handles)
            row: dict[str, Any] = {
                "seconds": (now - self._t0) / 10_000_000.0,
                "retained_handle_roles": [
                    role for role in ("S", "L", "W")
                    if handles[role] is not None
                ],
            }
            for role in ("S", "L", "W"):
                handle = handles[role]
                row[role] = (
                    0 if handle is None else _process_memory(handle)["working_set"]
                )
            with self._lock:
                self._samples.append(row)
            return dict(row)

    def _run(self) -> None:
        try:
            while not self._stop.is_set():
                if self._enabled.is_set():
                    self._sample_once(periodic=True)
                    self._stop.wait(NOMINAL_SAMPLE_SECONDS)
                else:
                    self._stop.wait(0.001)
        except BaseException as exc:
            self._error = exc
            self._stop.set()

    def start(self) -> None:
        self._thread.start()

    def force(self) -> dict[str, Any]:
        if self._error is not None:
            raise RuntimeError("resource sampler failed") from self._error
        observed = self._sample_once()
        if observed is None:
            raise RuntimeError("forced resource sample was suppressed")
        return observed

    def pause(self) -> None:
        self._enabled.clear()
        with self._sample_gate:
            pass

    def resume(self) -> None:
        self._enabled.set()

    def finish(self) -> list[dict[str, Any]]:
        self._stop.set()
        self._thread.join(timeout=1.0)
        if self._thread.is_alive():
            raise RuntimeError("resource sampler did not stop")
        if self._error is not None:
            raise RuntimeError("resource sampler failed") from self._error
        with self._lock:
            rows = list(self._samples)
        if any(
            later["seconds"] < earlier["seconds"]
            for earlier, later in zip(rows, rows[1:])
        ):
            raise RuntimeError("resource samples are not append-order monotonic")
        return rows


def _validate_ready_record(
    *,
    record: Mapping[str, Any],
    intent_sha256: str,
    launcher_pid: int,
    static_validation_sha256: str,
    worker_source_sha256: str,
    child_environment_sha256: str,
) -> int:
    worker_pid = record.get("pid")
    if (
        record.get("artifact") != "M245_W_READY"
        or record.get("status") != "READY_PRE_NUMPY"
        or not isinstance(worker_pid, int)
        or worker_pid <= 0
        or record.get("parent_pid") != launcher_pid
        or record.get("intent_sha256") != intent_sha256
        or record.get("numpy_modules") != []
        or record.get("job_member") is not True
        or _normalized(record.get("actual_image", "")) != _normalized(WORKER_OS_IMAGE)
        or record.get("actual_image_sha256") != WORKER_IMAGE_SHA256
        or _normalized(record.get("logical_sys_executable", ""))
        != _normalized(WORKER_LOGICAL_INTERPRETER)
        or _normalized(record.get("base_executable", ""))
        != _normalized(WORKER_OS_IMAGE)
        or record.get("argv") != [str(WORKER_SOURCE)]
        or record.get("orig_argv") != worker_argv()
        or _normalized(record.get("cwd", "")) != _normalized(AUTHORITY_DIRECTORY)
        or record.get("environment_sha256") != child_environment_sha256
        or record.get("worker_source_sha256") != worker_source_sha256
        or record.get("static_validation_receipt_sha256")
        != static_validation_sha256
    ):
        raise RuntimeError("worker READY identity mismatch")
    return worker_pid


def _array_receipt_from_raw(receipt: Mapping[str, Any]) -> None:
    if set(receipt) != {
        "dtype", "shape", "bytes", "sha256", "raw_c_order_sha256",
        "raw_c_hex", "repr_rows", "hex_rows", "hash_preimage",
    }:
        raise RuntimeError("V2 array receipt schema mismatch")
    if receipt.get("dtype") != "<f8":
        raise RuntimeError("V2 array dtype mismatch")
    shape = receipt.get("shape")
    if (
        not isinstance(shape, list)
        or len(shape) not in (1, 2)
        or not all(isinstance(item, int) and item > 0 for item in shape)
    ):
        raise RuntimeError("V2 array shape mismatch")
    raw_hex = receipt.get("raw_c_hex")
    if not isinstance(raw_hex, str):
        raise RuntimeError("V2 raw array hex absent")
    try:
        raw = bytes.fromhex(raw_hex)
    except ValueError as exc:
        raise RuntimeError("V2 raw array hex invalid") from exc
    count = math.prod(shape)
    if len(raw) != count * 8 or receipt.get("bytes") != len(raw):
        raise RuntimeError("V2 raw array byte length mismatch")
    if receipt.get("raw_c_order_sha256") != sha256_bytes(raw):
        raise RuntimeError("V2 raw C-order hash mismatch")
    shape_json = json.dumps(
        shape, ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8")
    preimage = b"<f8\0" + shape_json + b"\0" + raw
    if receipt.get("sha256") != sha256_bytes(preimage):
        raise RuntimeError("V2 frozen array preimage hash mismatch")
    repr_rows = receipt.get("repr_rows")
    hex_rows = receipt.get("hex_rows")
    expected_rows = [shape[0]] if len(shape) == 1 else [shape[1]] * shape[0]
    if (
        not isinstance(repr_rows, list)
        or not isinstance(hex_rows, list)
        or [len(row) for row in repr_rows] != expected_rows
        or [len(row) for row in hex_rows] != expected_rows
    ):
        raise RuntimeError("V2 exact representation row shape mismatch")
    values = struct.unpack("<" + "d" * count, raw)
    decimal = [item for row in repr_rows for item in row]
    hexadecimal = [item for row in hex_rows for item in row]
    for value, decimal_text, hex_text in zip(
        values, decimal, hexadecimal, strict=True
    ):
        if (
            not math.isfinite(value)
            or not isinstance(decimal_text, str)
            or decimal_text != repr(value)
            or not isinstance(hex_text, str)
            or hex_text != value.hex()
        ):
            raise RuntimeError("V2 repr/hex differs from raw float")


def _validate_v2_payload(
    payload: Mapping[str, Any],
    *,
    intent_sha256: str,
    authority_sha256: Mapping[str, str],
    source_sha256: Mapping[str, str],
    static_validation_sha256: str,
    manifest_v1: Mapping[str, Any],
) -> None:
    if set(payload) != {
        "schema", "artifact", "date", "status", "authority_commit_v1",
        "authority_repair_commit", "authority_precedence", "authority_sha256",
        "source_sha256", "static_validation_receipt_sha256", "intent_sha256",
        "numpy_version", "platform", "canonical_event_policy",
        "generated_fixture_algorithm", "array_receipt_policy", "fixtures",
        "shards", "fixture_census", "scientific_quantities_evaluated",
        "retry_or_redraw", "receipt_R_required", "terminal_witness_T_required",
    }:
        raise RuntimeError("V2 top-level schema mismatch")
    if (
        payload.get("schema") != "m245-authority-manifest-v2"
        or payload.get("artifact") != "M245_FROZEN_FIXTURE_AUTHORITY_V2"
        or payload.get("status")
        != "PROVISIONAL_REQUIRES_PASSING_R_AND_T_AND_COMMITTED_AUDIT"
        or payload.get("authority_commit_v1") != V1_COMMIT
        or payload.get("authority_repair_commit") != REPAIR_COMMIT
        or payload.get("date") != "2026-08-10"
        or payload.get("authority_precedence") != [
            "M245_PREMATERIALIZATION_ERRATUM1_20260810.md",
            "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json",
            "M245_PREDECLARATION_20260810.md",
            "M245_FROZEN_MANIFEST_V1_20260810.json",
        ]
        or payload.get("intent_sha256") != intent_sha256
        or payload.get("authority_sha256") != dict(sorted(authority_sha256.items()))
        or payload.get("source_sha256") != dict(sorted(source_sha256.items()))
        or payload.get("static_validation_receipt_sha256")
        != static_validation_sha256
        or payload.get("numpy_version") != "2.4.6"
        or payload.get("platform") != {
            "byteorder": "little",
            "implementation": "CPython",
            "python_version": manifest_v1["runtime"]["python"],
        }
        or payload.get("generated_fixture_algorithm")
        != manifest_v1["generated_fixture_algorithm"]
        or payload.get("canonical_event_policy")
        != manifest_v1["canonical_event_policy"]
        or payload.get("array_receipt_policy") != manifest_v1["array_receipt_v2"]
        or payload.get("shards") != manifest_v1["shards"]
        or payload.get("scientific_quantities_evaluated") != []
        or payload.get("retry_or_redraw") is not False
        or payload.get("receipt_R_required") != RECEIPT_R.name
        or payload.get("terminal_witness_T_required") != WITNESS_T.name
    ):
        raise RuntimeError("V2 authority binding mismatch")
    fixtures = payload.get("fixtures")
    expected_ids = [f"E{index:02d}" for index in range(8)]
    if (
        not isinstance(fixtures, list)
        or [row.get("event_id") for row in fixtures] != expected_ids
    ):
        raise RuntimeError("V2 fixture census/order mismatch")
    literal_by_id = {
        row["event_id"]: row for row in manifest_v1["literal_fixtures"]
    }
    generated_by_id = {
        row["event_id"]: row for row in manifest_v1["generated_fixtures"]
    }
    for row in fixtures:
        event_id = row["event_id"]
        frozen = literal_by_id.get(event_id) or generated_by_id.get(event_id)
        if frozen is None or row.get("event") != frozen["event"]:
            raise RuntimeError("V2 fixture event mismatch")
        if event_id in literal_by_id:
            if (
                set(row) != {
                    "event_id", "event", "role", "origin", "no_redraw",
                    "mu", "C", "diagnostics",
                }
                or row.get("role") != frozen["role"]
                or row.get("origin") != "literal_v1"
                or row.get("no_redraw") is not True
            ):
                raise RuntimeError("V2 literal provenance mismatch")
        else:
            if (
                set(row) != {
                    "event_id", "event", "origin", "seed", "no_redraw",
                    "mu", "C", "diagnostics",
                }
                or row.get("origin") != "numpy_2_4_6_philox_v1"
                or row.get("seed") != frozen["seed"]
                or row.get("no_redraw") is not True
            ):
                raise RuntimeError("V2 generated provenance mismatch")
        mu_receipt = row.get("mu", {})
        covariance_receipt = row.get("C", {})
        _array_receipt_from_raw(mu_receipt)
        _array_receipt_from_raw(covariance_receipt)
        if mu_receipt.get("shape") != [3] or covariance_receipt.get("shape") != [3, 3]:
            raise RuntimeError("V2 mu/C dimension mismatch")
        if event_id in literal_by_id:
            literal_mu = b"".join(
                struct.pack("<d", float(value)) for value in frozen["mu"]
            )
            literal_c = b"".join(
                struct.pack("<d", float(value))
                for matrix_row in frozen["C"] for value in matrix_row
            )
            if (
                mu_receipt.get("raw_c_hex") != literal_mu.hex()
                or covariance_receipt.get("raw_c_hex") != literal_c.hex()
            ):
                raise RuntimeError("V2 literal raw binary64 differs from V1")
        diagnostics = row.get("diagnostics")
        if (
            not isinstance(diagnostics, Mapping)
            or set(diagnostics) != {
                "all_finite", "C_bytewise_equal_to_transpose",
                "numpy_linalg_cholesky_pass", "eigvalsh_min_strictly_positive",
                "conditional_variances_strictly_positive",
                "absolute_conditional_correlation_strictly_less_than_one",
                "eigvalsh_min", "eigvalsh_max", "determinant",
                "conditional_variance_j", "conditional_variance_k",
                "conditional_covariance_jk", "conditional_correlation",
            }
        ):
            raise RuntimeError("V2 diagnostics absent")
        for key in (
            "all_finite", "C_bytewise_equal_to_transpose",
            "numpy_linalg_cholesky_pass", "eigvalsh_min_strictly_positive",
            "conditional_variances_strictly_positive",
            "absolute_conditional_correlation_strictly_less_than_one",
        ):
            if diagnostics.get(key) is not True:
                raise RuntimeError(f"V2 diagnostic failed: {key}")
        for key in (
            "eigvalsh_min", "eigvalsh_max", "determinant",
            "conditional_variance_j", "conditional_variance_k",
            "conditional_covariance_jk", "conditional_correlation",
        ):
            scalar = diagnostics.get(key)
            if (
                not isinstance(scalar, Mapping)
                or set(scalar) != {"repr", "hex"}
                or not isinstance(scalar.get("repr"), str)
                or not isinstance(scalar.get("hex"), str)
            ):
                raise RuntimeError("V2 scalar diagnostic receipt absent")
            value = float.fromhex(scalar["hex"])
            if not math.isfinite(value) or scalar["repr"] != repr(value):
                raise RuntimeError("V2 scalar diagnostic repr/hex mismatch")
    census = payload.get("fixture_census")
    if census != {
        "event_ids": expected_ids,
        "event_count": 8,
        "literal_count": len(literal_by_id),
        "generated_count": len(generated_by_id),
        "array_count": 16,
        "shard_count": len(manifest_v1["shards"]),
    }:
        raise RuntimeError("V2 declared fixture census mismatch")


def _reopen_and_validate_v2(
    *,
    intent_sha256: str,
    authority_sha256: Mapping[str, str],
    source_sha256: Mapping[str, str],
    static_validation_sha256: str,
    manifest_v1: Mapping[str, Any],
    done_v2: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bytes, str]:
    _require_plain_root(AUTHORITY_DIRECTORY)
    if os.path.lexists(str(V2_TEMP)):
        raise RuntimeError("V2 temporary path remains after publication")
    _require_plain_contained_file(V2_FINAL, AUTHORITY_DIRECTORY)
    encoded = V2_FINAL.read_bytes()
    payload = json.loads(encoded.decode("utf-8"))
    if canonical_json_bytes(payload) != encoded:
        raise RuntimeError("V2 is not canonical JSON")
    digest = sha256_bytes(encoded)
    final_stat = V2_FINAL.stat()
    if (
        set(done_v2) != {
            "path", "bytes", "sha256", "reopened_bytes_equal",
            "reopened_parse_equal", "temporary_path", "temporary_sha256",
            "temporary_removed", "same_device", "same_inode",
            "source_device", "source_inode", "final_device", "final_inode",
        }
        or done_v2.get("path") != str(V2_FINAL)
        or done_v2.get("temporary_path") != str(V2_TEMP)
        or done_v2.get("sha256") != digest
        or done_v2.get("temporary_sha256") != digest
        or done_v2.get("bytes") != len(encoded)
        or done_v2.get("temporary_removed") is not True
        or done_v2.get("same_device") is not True
        or done_v2.get("same_inode") is not True
        or done_v2.get("reopened_bytes_equal") is not True
        or done_v2.get("reopened_parse_equal") is not True
        or done_v2.get("source_device") != int(final_stat.st_dev)
        or done_v2.get("final_device") != int(final_stat.st_dev)
        or done_v2.get("source_inode") != int(final_stat.st_ino)
        or done_v2.get("final_inode") != int(final_stat.st_ino)
        or int(final_stat.st_size) != len(encoded)
    ):
        raise RuntimeError("worker V2 hard-link receipt mismatch")
    _validate_v2_payload(
        payload,
        intent_sha256=intent_sha256,
        authority_sha256=authority_sha256,
        source_sha256=source_sha256,
        static_validation_sha256=static_validation_sha256,
        manifest_v1=manifest_v1,
    )
    receipt = {
        **dict(done_v2),
        "supervisor_reopened_bytes_equal": True,
        "supervisor_reopened_parse_equal": True,
        "supervisor_sha256": digest,
    }
    return payload, receipt, encoded, digest


def _remaining_milliseconds(
    deadline_filetime: int, cap_milliseconds: int | None = None
) -> int:
    remaining_100ns = deadline_filetime - _precise_filetime()
    if remaining_100ns <= 0:
        raise TimeoutError("shared M245 30-second deadline expired")
    observed = max(1, int(math.ceil(remaining_100ns / 10_000.0)))
    return observed if cap_milliseconds is None else min(cap_milliseconds, observed)


def _initial_job_census(
    port: int,
    launcher_pid: int,
    sampler: _ResourceSampler,
    deadline_filetime: int,
) -> tuple[list[dict[str, int]], set[int], int, int]:
    records: list[dict[str, int]] = []
    pids: set[int] = set()
    worker_handle: int | None = None
    worker_acquired = 0
    while launcher_pid not in pids or len(pids) < 2:
        batch = _drain_job_notifications(
            port, _remaining_milliseconds(deadline_filetime, 10)
        )
        if not batch:
            continue
        if any(
            row["completion_key"] != 1
            or row["message"] not in {
                JOB_OBJECT_MSG_NEW_PROCESS,
                JOB_OBJECT_MSG_EXIT_PROCESS,
                JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO,
            }
            for row in batch
        ):
            raise RuntimeError("unexpected keyed Job notification")
        batch_pids = {
            row["pid"] for row in batch
            if row["message"] == JOB_OBJECT_MSG_NEW_PROCESS
        }
        pids.update(batch_pids)
        if len(pids) > 2:
            raise RuntimeError("third process entered M245 job")
        worker_candidates = pids - {launcher_pid}
        if worker_candidates and worker_handle is None:
            worker_pid = next(iter(worker_candidates))
            worker_handle, worker_acquired = _open_process(worker_pid)
            sampler.set_handle("W", worker_handle)
        records.extend(batch)
    if worker_handle is None:
        raise RuntimeError("W handle was not acquired from NEW_PROCESS")
    for _notification in records:
        _sample = sampler.force()
        _notification["sample_seconds"] = _sample["seconds"]
    return records, pids, worker_handle, worker_acquired


def _collect_terminal_job_census(
    *,
    port: int,
    records: list[dict[str, int]],
    expected_pids: set[int],
    sampler: _ResourceSampler,
    deadline_filetime: int,
) -> list[dict[str, int]]:
    while True:
        new_counts = {
            pid: sum(
                row["message"] == JOB_OBJECT_MSG_NEW_PROCESS and row["pid"] == pid
                for row in records
            )
            for pid in expected_pids
        }
        exit_counts = {
            pid: sum(
                row["message"] == JOB_OBJECT_MSG_EXIT_PROCESS and row["pid"] == pid
                for row in records
            )
            for pid in expected_pids
        }
        zero_count = sum(
            row["message"] == JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO
            for row in records
        )
        if (
            all(value == 1 for value in new_counts.values())
            and all(value == 1 for value in exit_counts.values())
            and zero_count == 1
        ):
            extra = _drain_job_notifications(port, 0)
            if extra:
                if any(
                    row["completion_key"] != 1
                    or row["message"] not in {
                        JOB_OBJECT_MSG_NEW_PROCESS,
                        JOB_OBJECT_MSG_EXIT_PROCESS,
                        JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO,
                    }
                    for row in extra
                ):
                    raise RuntimeError("unexpected keyed Job notification")
                for _row in extra:
                    _sample = sampler.force()
                    _row["sample_seconds"] = _sample["seconds"]
                records.extend(extra)
                continue
            break
        batch = _drain_job_notifications(
            port, _remaining_milliseconds(deadline_filetime, 100)
        )
        if any(
            row["completion_key"] != 1
            or row["message"] not in {
                JOB_OBJECT_MSG_NEW_PROCESS,
                JOB_OBJECT_MSG_EXIT_PROCESS,
                JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO,
            }
            for row in batch
        ):
            raise RuntimeError("unexpected keyed Job notification")
        for _row in batch:
            _sample = sampler.force()
            _row["sample_seconds"] = _sample["seconds"]
        records.extend(batch)
    process_messages = [
        row for row in records
        if row["message"] in {JOB_OBJECT_MSG_NEW_PROCESS, JOB_OBJECT_MSG_EXIT_PROCESS}
    ]
    if any(row["pid"] not in expected_pids for row in process_messages):
        raise RuntimeError("unexpected PID in job process-event census")
    for pid in expected_pids:
        if sum(
            row["message"] == JOB_OBJECT_MSG_NEW_PROCESS and row["pid"] == pid
            for row in records
        ) != 1:
            raise RuntimeError("NEW_PROCESS census is not exact")
        if sum(
            row["message"] == JOB_OBJECT_MSG_EXIT_PROCESS and row["pid"] == pid
            for row in records
        ) != 1:
            raise RuntimeError("EXIT_PROCESS census is not exact")
    if sum(
        row["message"] == JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO for row in records
    ) != 1:
        raise RuntimeError("ACTIVE_PROCESS_ZERO census is not exact")
    return records


def _supervisor_main() -> int:
    trace: list[str] = ["PREINTENT"]
    if sys.argv != [str(SUPERVISOR_SOURCE)]:
        raise RuntimeError("supervisor accepts no arguments")
    if _normalized(Path.cwd()) != _normalized(AUTHORITY_DIRECTORY):
        raise RuntimeError("supervisor cwd mismatch")
    if (
        int(sys.flags.isolated) != 1
        or int(sys.flags.no_site) != 1
        or int(sys.flags.safe_path) != 1
        or not bool(sys.dont_write_bytecode)
        or list(getattr(sys, "orig_argv", [])) != supervisor_argv()
    ):
        raise RuntimeError("supervisor startup flags or argv mismatch")

    s_handle: int | None = None
    l_handle: int | None = None
    w_handle: int | None = None
    job: int | None = None
    completion_port: int | None = None
    stdout_read: int | None = None
    stdout_write: int | None = None
    stderr_read: int | None = None
    stderr_write: int | None = None
    process: PROCESS_INFORMATION | None = None
    events: dict[str, int] = {}
    sampler: _ResourceSampler | None = None
    sampler_finished = False
    completed = False
    job_assigned = False
    stdout_bytes = b""
    try:
        _require_plain_root(AUTHORITY_DIRECTORY)
        _require_plain_contained_file(SUPERVISOR_SOURCE, AUTHORITY_DIRECTORY)
        _require_plain_contained_file(SUPERVISOR_INTERPRETER, BASE_RUNTIME_ROOT)
        if _normalized(sys.executable) != _normalized(SUPERVISOR_INTERPRETER):
            raise RuntimeError("supervisor logical interpreter mismatch")
        s_pid = os.getpid()
        s_handle, s_acquired = _open_process(s_pid)
        if _actual_image_path(s_handle) != str(SUPERVISOR_INTERPRETER):
            if _normalized(_actual_image_path(s_handle)) != _normalized(SUPERVISOR_INTERPRETER):
                raise RuntimeError("supervisor OS image mismatch")
        s_times_initial = _process_times(s_handle)
        shared_deadline_filetime = (
            s_times_initial["creation_filetime"]
            + int(WALL_CAP_SECONDS * 10_000_000)
        )
        _remaining_milliseconds(shared_deadline_filetime)
        sampler = _ResourceSampler(s_handle, s_times_initial["creation_filetime"])
        sampler.start()

        assert_paths_absent(EXECUTION_PATHS)
        authority_sha256, static_validation, manifest_v1 = (
            _verify_authority_and_sources()
        )
        _remaining_milliseconds(shared_deadline_filetime)
        assert_paths_absent(EXECUTION_PATHS)
        intent_payload = _intent_payload(authority_sha256, static_validation)
        _validate_intent_payload(
            intent_payload,
            authority_sha256=authority_sha256,
            static_validation=static_validation,
        )
        intent_receipt, intent_bytes, intent_sha256 = _publish_owned_json(
            INTENT, intent_payload
        )
        _require_plain_contained_file(INTENT, AUTHORITY_DIRECTORY)
        if (
            INTENT.read_bytes() != intent_bytes
            or sha256_file(INTENT) != intent_sha256
            or intent_receipt["sha256"] != intent_sha256
        ):
            raise RuntimeError("intent durable verification mismatch")
        trace.append("INTENT_VERIFIED")

        _remaining_milliseconds(shared_deadline_filetime)
        names = control_event_names(intent_sha256)
        events = _create_control_events(names)
        job, completion_port = _create_job()
        stdout_read, stdout_write = _create_pipe()
        stderr_read, stderr_write = _create_pipe()
        sampler.force()
        sampler.pause()
        process = _create_suspended_launcher(
            stdout_write=stdout_write, stderr_write=stderr_write
        )
        trace.append("LAUNCHER_SUSPENDED")
        launcher_pid = int(process.dwProcessId)
        _assign_to_job(job, process)
        job_assigned = True
        trace.append("JOB_ASSIGNED")
        l_handle, l_acquired = _open_process(launcher_pid)
        sampler.set_handle("L", l_handle)
        sampler.force()
        _resume_launcher(process)
        trace.append("LAUNCHER_RESUMED")
        _close_handle(int(process.hThread))
        process.hThread = None
        _close_handle(int(process.hProcess))
        process.hProcess = None
        _close_handle(stdout_write)
        stdout_write = None
        _close_handle(stderr_write)
        stderr_write = None

        notifications, job_pids, w_handle, w_acquired = _initial_job_census(
            completion_port, launcher_pid, sampler, shared_deadline_filetime
        )
        if launcher_pid not in job_pids or len(job_pids) != 2:
            raise RuntimeError("initial Job process census mismatch")
        sampler.resume()
        worker_pid = next(pid for pid in job_pids if pid != launcher_pid)
        sampler.force()
        snapshot = _process_snapshot()
        if (
            snapshot.get(launcher_pid) != s_pid
            or snapshot.get(worker_pid) != launcher_pid
        ):
            raise RuntimeError("S -> L -> W live parent chain mismatch")
        if not _is_process_in_job(l_handle, job) or not _is_process_in_job(w_handle, job):
            raise RuntimeError("L/W job membership mismatch")
        if _is_process_in_job(s_handle, job):
            raise RuntimeError("S entered child job")
        child_environment_sha256 = _environment_digest(
            sanitized_child_environment()
        )
        s_parent = snapshot.get(s_pid)
        if s_parent is None:
            raise RuntimeError("S parent identity unavailable")
        s_identity = _identity(
            role="S", handle=s_handle, pid=s_pid, parent_pid=s_parent,
            expected_image=SUPERVISOR_INTERPRETER,
            expected_image_sha256=SUPERVISOR_IMAGE_SHA256,
            argv=supervisor_argv(),
            environment_sha256=_environment_digest(dict(os.environ)),
            job=job,
            handle_acquisition_filetime=s_acquired,
        )
        l_identity = _identity(
            role="L", handle=l_handle, pid=launcher_pid, parent_pid=s_pid,
            expected_image=WORKER_LOGICAL_INTERPRETER,
            expected_image_sha256=LAUNCHER_IMAGE_SHA256,
            argv=worker_argv(),
            environment_sha256=child_environment_sha256,
            job=job,
            handle_acquisition_filetime=l_acquired,
        )
        w_identity = _identity(
            role="W", handle=w_handle, pid=worker_pid, parent_pid=launcher_pid,
            expected_image=WORKER_OS_IMAGE,
            expected_image_sha256=WORKER_IMAGE_SHA256,
            argv=worker_argv(),
            environment_sha256=child_environment_sha256,
            job=job,
            handle_acquisition_filetime=w_acquired,
        )
        l_identity["child_pids"] = [worker_pid]
        w_identity["child_count"] = 0

        _wait_event(
            events["READY"], _remaining_milliseconds(shared_deadline_filetime)
        )
        sampler.force()
        stdout_bytes += _read_available(stdout_read)
        stderr_bytes = _read_available(stderr_read)
        ready_documents = _parse_canonical_documents(stdout_bytes)
        if len(ready_documents) != 1 or stderr_bytes != b"":
            raise RuntimeError("READY transcript or stderr mismatch")
        ready_worker_pid = _validate_ready_record(
            record=ready_documents[0],
            intent_sha256=intent_sha256,
            launcher_pid=launcher_pid,
            static_validation_sha256=static_validation["sha256"],
            worker_source_sha256=static_validation["audited_sha256"][
                WORKER_SOURCE.name
            ],
            child_environment_sha256=child_environment_sha256,
        )
        if ready_worker_pid != worker_pid:
            raise RuntimeError("READY PID differs from retained Job W handle")
        trace.append("WORKER_READY")

        _remaining_milliseconds(shared_deadline_filetime)
        _set_event(events["GO"])
        trace.append("GO_RELEASED")
        _wait_event(
            events["DONE"], _remaining_milliseconds(shared_deadline_filetime)
        )
        sampler.force()
        stdout_bytes += _read_available(stdout_read)
        stderr_bytes += _read_available(stderr_read)
        documents = _parse_canonical_documents(stdout_bytes)
        if len(documents) != 2:
            raise RuntimeError("DONE transcript record count mismatch")
        done = documents[1]
        if (
            done.get("artifact") != "M245_W_DONE"
            or done.get("status") != "V2_PUBLISHED_WAITING_EXIT"
            or done.get("pid") != worker_pid
            or done.get("intent_sha256") != intent_sha256
            or done.get("worker_source_sha256")
            != static_validation["audited_sha256"][WORKER_SOURCE.name]
            or done.get("fixture_count") != 8
            or not isinstance(done.get("retained_object_count"), int)
            or done["retained_object_count"] <= 0
            or not isinstance(done.get("v2"), Mapping)
        ):
            raise RuntimeError("worker DONE record mismatch")
        (
            _v2_payload,
            v2_receipt,
            _v2_bytes,
            v2_sha256,
        ) = _reopen_and_validate_v2(
            intent_sha256=intent_sha256,
            authority_sha256=authority_sha256,
            source_sha256=static_validation["audited_sha256"],
            static_validation_sha256=static_validation["sha256"],
            manifest_v1=manifest_v1,
            done_v2=done["v2"],
        )
        validate_worker_transcript(
            stdout_bytes=stdout_bytes,
            stderr_bytes=stderr_bytes,
            intent_sha256=intent_sha256,
            v2_sha256=v2_sha256,
            worker_pid=worker_pid,
        )
        trace.append("V2_PUBLISHED")
        trace.append("DONE_BARRIER")

        sampler.force()
        snapshot = _process_snapshot()
        l_children = sorted(
            pid for pid, parent in snapshot.items() if parent == launcher_pid
        )
        w_children = sorted(
            pid for pid, parent in snapshot.items() if parent == worker_pid
        )
        if l_children != [worker_pid] or w_children:
            raise RuntimeError("L/W child census mismatch")
        if _exit_code(l_handle) != STILL_ACTIVE or _exit_code(w_handle) != STILL_ACTIVE:
            raise RuntimeError("L/W not live at R barrier")
        accounting_at_r = _job_accounting(job)
        later_notifications = _drain_job_notifications(completion_port, 0)
        if later_notifications:
            if any(
                row["completion_key"] != 1
                or row["message"] not in {
                    JOB_OBJECT_MSG_NEW_PROCESS,
                    JOB_OBJECT_MSG_EXIT_PROCESS,
                    JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO,
                }
                for row in later_notifications
            ):
                raise RuntimeError("unexpected keyed Job notification")
            for _notification in later_notifications:
                _sample = sampler.force()
                _notification["sample_seconds"] = _sample["seconds"]
            notifications.extend(later_notifications)
            job_pids.update(
                row["pid"] for row in later_notifications
                if row["message"] == JOB_OBJECT_MSG_NEW_PROCESS
            )
        if (
            job_pids != {launcher_pid, worker_pid}
            or accounting_at_r["total_processes"] != 2
            or accounting_at_r["active_processes"] != 2
        ):
            raise RuntimeError("live Job census mismatch at R")

        pre_r_topology = {
            "S": s_identity,
            "L": l_identity,
            "W": w_identity,
            "job": {
                "total_processes": 2,
                "active_at_r": 2,
                "pid_census": sorted(job_pids),
                "kill_on_close": True,
                "active_process_limit": 2,
            },
        }
        _pre_r_topology(pre_r_topology)
        post_v2_authority, post_v2_static, post_v2_manifest = (
            _verify_authority_and_sources()
        )
        if (
            post_v2_authority != authority_sha256
            or post_v2_static != static_validation
            or post_v2_manifest != manifest_v1
        ):
            raise RuntimeError("authority/runtime/source drift before R")
        _remaining_milliseconds(shared_deadline_filetime)
        trace.append("CHILDREN_LIVE_AT_R")

        r_binding_hashes = {
            **authority_sha256,
            **{
                f"source::{name}": digest
                for name, digest in static_validation["audited_sha256"].items()
            },
        }
        r_payload = build_provisional_receipt(
            intent_sha256=intent_sha256,
            v2_sha256=v2_sha256,
            authority_sha256=r_binding_hashes,
            v2_receipt=v2_receipt,
            topology=pre_r_topology,
        )
        (
            r_receipt,
            r_bytes_value,
            r_sha256,
            endpoint_filetime,
        ) = _publish_r_and_capture_endpoint(
            r_payload
        )
        trace.append("R_PUBLISHED")
        if endpoint_filetime < s_times_initial["creation_filetime"]:
            raise RuntimeError("R endpoint precedes S creation")
        trace.append("ENDPOINT_CAPTURED")
        sampler.force()
        if _exit_code(l_handle) != STILL_ACTIVE or _exit_code(w_handle) != STILL_ACTIVE:
            raise RuntimeError("L/W left EXIT barrier at the R endpoint")

        process_handles = {"S": s_handle, "L": l_handle, "W": w_handle}
        resources_raw: dict[str, dict[str, int]] = {}
        for role, handle in process_handles.items():
            memory = _process_memory(handle)
            times = _process_times(handle)
            resources_raw[role] = {
                "peak_working_set_lifetime_to_endpoint":
                    memory["peak_working_set"],
                "kernel_endpoint_100ns": times["kernel_100ns"],
                "kernel_final_100ns": times["kernel_100ns"],
                "user_endpoint_100ns": times["user_100ns"],
                "user_final_100ns": times["user_100ns"],
            }
        trace.append("LIVE_PEAK_CPU_CAPTURED")

        _remaining_milliseconds(shared_deadline_filetime)
        sampler.force()
        _set_event(events["EXIT"])
        trace.append("EXIT_RELEASED")
        notifications = _collect_terminal_job_census(
            port=completion_port,
            records=notifications,
            expected_pids={launcher_pid, worker_pid},
            sampler=sampler,
            deadline_filetime=shared_deadline_filetime,
        )
        sampler.force()
        sampler.pause()
        worker_exit = _wait_process(w_handle, 0)
        trace.append("WORKER_OS_EXIT")
        launcher_exit = _wait_process(l_handle, 0)
        child_exit_filetime = _precise_filetime()
        samples = sampler.finish()
        sampler_finished = True
        trace.append("CHILDREN_EXITED")
        if child_exit_filetime < endpoint_filetime:
            raise RuntimeError("child-exit clock precedes R endpoint")
        trace.append("CHILD_EXIT_CLOCK_CAPTURED")
        accounting_after = _job_accounting(job)
        if (
            accounting_after["active_processes"] != 0
            or accounting_after["total_processes"] != 2
            or accounting_after["total_terminated_processes"] != 0
            or job_pids != {launcher_pid, worker_pid}
            or worker_exit != 0
            or launcher_exit != 0
        ):
            raise RuntimeError("post-exit job or exit-code mismatch")
        trace.append("JOB_ACTIVE_ZERO")
        w_identity["used_os_exit_zero"] = True

        stdout_bytes += _read_available(stdout_read)
        stderr_bytes += _read_available(stderr_read)
        validate_worker_transcript(
            stdout_bytes=stdout_bytes,
            stderr_bytes=stderr_bytes,
            intent_sha256=intent_sha256,
            v2_sha256=v2_sha256,
            worker_pid=worker_pid,
        )

        for role, handle in process_handles.items():
            final_times = _process_times(handle)
            resources_raw[role]["kernel_final_100ns"] = final_times["kernel_100ns"]
            resources_raw[role]["user_final_100ns"] = final_times["user_100ns"]
            identity = {"S": s_identity, "L": l_identity, "W": w_identity}[role]
            identity["kernel_time_100ns"] = final_times["kernel_100ns"]
            identity["user_time_100ns"] = final_times["user_100ns"]
            identity["exit_code"] = (
                _exit_code(handle) if role == "S"
                else {"L": launcher_exit, "W": worker_exit}[role]
            )
        if s_identity["exit_code"] != STILL_ACTIVE:
            raise RuntimeError("S was not live while constructing T evidence")
        wall_r_seconds = (
            endpoint_filetime - s_times_initial["creation_filetime"]
        ) / 10_000_000.0
        wall_child_exit_seconds = (
            child_exit_filetime - s_times_initial["creation_filetime"]
        ) / 10_000_000.0
        resources = evaluate_resource_gate(
            processes=resources_raw,
            working_set_samples=samples,
            wall_r_seconds=wall_r_seconds,
            wall_child_exit_seconds=wall_child_exit_seconds,
        )
        if resources["pass"] is not True:
            raise RuntimeError("M245 resource gate failed")
        resources["clock_filetimes"] = {
            "s_creation": s_times_initial["creation_filetime"],
            "r_endpoint": endpoint_filetime,
            "child_exit": child_exit_filetime,
        }
        resources["wall_r_100ns"] = (
            endpoint_filetime - s_times_initial["creation_filetime"]
        )
        resources["wall_child_exit_100ns"] = (
            child_exit_filetime - s_times_initial["creation_filetime"]
        )

        full_job = {
            "total_processes": accounting_at_r["total_processes"],
            "active_at_r": accounting_at_r["active_processes"],
            "pid_census": sorted(job_pids),
            "active_after_exit": accounting_after["active_processes"],
            "total_processes_final": accounting_after["total_processes"],
            "total_terminated_processes":
                accounting_after["total_terminated_processes"],
            "kill_on_close": True,
            "active_process_limit": 2,
            "notifications": notifications,
        }
        exits = {
            "launcher": launcher_exit,
            "worker": worker_exit,
            "active_processes": accounting_after["active_processes"],
            "child_exit_filetime": child_exit_filetime,
        }
        full_topology = {
            "S": s_identity,
            "L": l_identity,
            "W": w_identity,
            "job": full_job,
            "exits": {
                "launcher": launcher_exit,
                "worker": worker_exit,
            },
        }
        validate_topology_evidence(full_topology)
        pre_t_state = {
            "intent": os.path.lexists(str(INTENT)),
            "v2": os.path.lexists(str(V2_FINAL)),
            "r": os.path.lexists(str(RECEIPT_R)),
            "temp": os.path.lexists(str(V2_TEMP)),
            "t": os.path.lexists(str(WITNESS_T)),
        }
        pre_t_authority, pre_t_static, pre_t_manifest = (
            _verify_authority_and_sources()
        )
        if (
            pre_t_authority != authority_sha256
            or pre_t_static != static_validation
            or pre_t_manifest != manifest_v1
        ):
            raise RuntimeError("authority/runtime/source drift before T")
        for path in (INTENT, V2_FINAL, RECEIPT_R):
            _require_plain_contained_file(path, AUTHORITY_DIRECTORY)
        if INTENT.read_bytes() != intent_bytes or sha256_file(INTENT) != intent_sha256:
            raise RuntimeError("intent changed before T")
        if RECEIPT_R.read_bytes() != r_bytes_value or sha256_file(RECEIPT_R) != r_sha256:
            raise RuntimeError("R changed before T")
        if V2_FINAL.read_bytes() != _v2_bytes or sha256_file(V2_FINAL) != v2_sha256:
            raise RuntimeError("V2 changed before T")
        pre_t_state = {
            "intent": os.path.lexists(str(INTENT)),
            "v2": os.path.lexists(str(V2_FINAL)),
            "r": os.path.lexists(str(RECEIPT_R)),
            "temp": os.path.lexists(str(V2_TEMP)),
            "t": os.path.lexists(str(WITNESS_T)),
        }
        sampling = {
            "nominal_interval_seconds": NOMINAL_SAMPLE_SECONDS,
            "maximum_gap_seconds": resources["maximum_gap_seconds"],
            "sample_count": len(samples),
            "timestamps_seconds": [row["seconds"] for row in samples],
            "clock": "GetSystemTimePreciseAsFileTime_since_S_creation_FILETIME",
            "state_trace_before_t": list(trace),
        }
        t_payload = build_terminal_witness(
            intent_sha256=intent_sha256,
            v2_sha256=v2_sha256,
            r_sha256=r_sha256,
            r_bytes=r_receipt["bytes"],
            resources=resources,
            exits=exits,
            identities={role: full_topology[role] for role in ("S", "L", "W")},
            sampling=sampling,
            pre_t_state=pre_t_state,
            job_census=full_job,
            expected_t_path=WITNESS_T.name,
        )
        prospective_trace = [
            *trace, "T_PUBLISHED_PENDING_INDEPENDENT_AUDIT"
        ]
        validate_state_trace(prospective_trace)
        canonical_json_bytes(t_payload)
        _publish_owned_json(WITNESS_T, t_payload)
        trace = prospective_trace
        completed = True
        return 0
    finally:
        if (
            not completed
            and not job_assigned
            and process is not None
            and process.hProcess
        ):
            try:
                if _exit_code(int(process.hProcess)) == STILL_ACTIVE:
                    kernel32 = _kernel32()
                    kernel32.TerminateProcess.argtypes = [
                        wintypes.HANDLE, wintypes.UINT
                    ]
                    kernel32.TerminateProcess.restype = wintypes.BOOL
                    kernel32.TerminateProcess(process.hProcess, 0xE2450002)
                    _wait_process(int(process.hProcess), 5_000)
            except BaseException:
                pass
        if not completed and job is not None:
            _close_handle(job)
            job = None
        if sampler is not None and not sampler_finished:
            try:
                sampler.finish()
            except BaseException:
                pass
        if process is not None:
            _close_handle(int(process.hThread) if process.hThread else None)
            _close_handle(int(process.hProcess) if process.hProcess else None)
        for handle in events.values():
            _close_handle(handle)
        for handle in (
            stdout_read, stdout_write, stderr_read, stderr_write,
            w_handle, l_handle, s_handle, completion_port, job,
        ):
            _close_handle(handle)


if __name__ == "__main__":
    raise SystemExit(_supervisor_main())
