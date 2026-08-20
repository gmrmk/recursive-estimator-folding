"""Immutable, stdlib-only aggregation for the M245 diagnostic.

This module deliberately contains no scientific computation.  It verifies a
committed input authorization and its twelve immutable inputs, copies the
eight event records losslessly, applies the one frozen family-label rule, and
publishes canonical JSON with a create-if-absent hard-link transaction.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
from ctypes import wintypes
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from typing import Any


class M245AggregationContractError(RuntimeError):
    """Raised whenever an immutable aggregation contract check fails."""


AUTHORITY_DIRECTORY_REPO_RELATIVE = (
    "corpus/whestbench/experiments/"
    "m245_canonical_unordered_replica_galerkin_spectrum"
)
SHARD_DIRECTORY_REPO_RELATIVE = (
    "corpus/whestbench/experiments/m245_fable_spectrum_shards"
)
ASSIGNMENTS = {
    0: ("E00", "E01"),
    1: ("E02", "E03"),
    2: ("E04", "E05"),
    3: ("E06", "E07"),
}
FINAL_RECEIPT_NAMES = tuple(
    f"M245_S{shard_id}_FINAL_RECEIPT_20260810.json"
    for shard_id in ASSIGNMENTS
)
FAMILIES = ("geometric", "logistic", "Gompertz")
STDLIB_PYTHON = r"C:\Python314\python.exe"
VENV_PYTHON = r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe"
STDLIB_PYTHON_SHA256 = "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"
VENV_PYTHON_SHA256 = "4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262"

_CONTRACT = {
    "owner": "codex",
    "committed_input_authorization_required": True,
    "authorized_only_after_four_pass_receipts": True,
    "authority_directory_repo_relative": AUTHORITY_DIRECTORY_REPO_RELATIVE,
    "shard_directory_repo_relative": SHARD_DIRECTORY_REPO_RELATIVE,
    "final_shard_receipt_names": FINAL_RECEIPT_NAMES,
    "final_shard_receipt_schema": "m245-final-shard-receipt-v2",
    "input_count": 4,
    "terminal_witness_count": 8,
    "aggregation_launch_slots_max": 1,
    "launch_slot_unit": "durable_aggregation_intent",
    "os_process_creations_max": 3,
    "wall_seconds": 120,
    "scientific_worker_count": 1,
    "scientific_worker_children": 0,
    "inert_hash_bound_venv_launcher_redirector_max": 1,
    "network": False,
    "stdlib_only": True,
    "scientific_imports": False,
    "new_quadrature": False,
    "new_solve": False,
    "new_curve_transform_or_fit": False,
    "drop_or_relabel_event": False,
    "retry": False,
    "max_shard_cpu_seconds_total": 43200,
}

_NAMESPACE = {
    "directory_repo_relative": AUTHORITY_DIRECTORY_REPO_RELATIVE,
    "authorization": "M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json",
    "intent_temp": ".M245_AGGREGATION_INTENT_20260810.json.tmp",
    "intent": "M245_AGGREGATION_INTENT_20260810.json",
    "result_temp": ".M245_AGGREGATED_SPECTRUM_20260810.json.tmp",
    "result": "M245_AGGREGATED_SPECTRUM_20260810.json",
    "receipt_temp": ".M245_AGGREGATION_RECEIPT_20260810.json.tmp",
    "receipt": "M245_AGGREGATION_RECEIPT_20260810.json",
}

_FINAL_KEYS = (
    "artifact", "schema", "shard_id", "events_in_order", "event_results",
    "invocation_receipts", "authority_sha256", "resource_union",
    "no_cross_shard_cache", "firewall", "status",
)
_EVENT_KEYS = (
    "event_id", "fixture_array_sha256", "primary_by_precision",
    "replica_by_precision", "cross_precision_gates",
    "primary_replica_gates", "analytic_solve_energy_beta_gates",
    "curve_report", "quad_gateway_ledger_refs", "only_future_bound",
    "gate_verdict", "firewall", "forbidden_credit",
)
_PRIMARY_KEYS = (
    "artifact", "schema", "event_id", "precision_dps",
    "fixture_array_sha256", "degrees", "R", "G", "mu_rb", "K", "d",
    "beta", "leading_blocks", "analytic_direct_checks",
    "quadrature_audit", "firewall",
)
_REPLICA_KEYS = (
    "artifact", "schema", "event_id", "precision_dps",
    "fixture_array_sha256", "fixed_b_nodes", "b_rep_at_nodes", "mu_rep",
    "M_same", "M_cross", "K_rep", "quadrature_audit", "firewall",
)
_WITNESS_KEYS = (
    "artifact", "schema", "shard_id", "invocation_index", "event_id",
    "authority_sha256", "inner_artifacts", "inner_meter",
    "prior_invocation_files", "outer_meter", "process_identities",
    "job_census", "s_exit", "resource_meter", "final_shard_receipt",
    "firewall", "status",
)
_FIREWALL_KEYS = (
    "challenge_network_or_weights", "champion_output", "credentials",
    "hidden_compute", "leaderboard", "m125_response", "m151_source_arrays",
    "m178_code_or_credit", "m196_state", "m243_input_or_import",
    "network_service", "retry_or_clipping", "scorer", "sealed_cells",
    "submission", "truth",
)
_AUTH_KEYS = (
    "artifact", "schema", "shard_trigger_sha256", "final_shard_receipts",
    "terminal_witnesses", "observed_parent_head", "aggregate_argv",
    "aggregate_cwd", "aggregate_source_sha256", "zero_prior_paths",
    "status",
)
_RESULT_KEYS = (
    "artifact", "schema", "authority_sha256", "event_ids", "events",
    "family_curve_labels", "shard_receipt_sha256",
    "global_shard_cpu_seconds", "firewall", "status",
)
_RECEIPT_KEYS = (
    "artifact", "schema", "authorization_binding", "input_shard_receipts",
    "input_terminal_witnesses", "intent_publication", "output_publication",
    "postpublication_verification", "process_tree", "network",
    "no_scientific_imports", "wall_seconds", "status",
)
_AUTH_BINDING_KEYS = {
    "bytes", "device", "inode", "path", "repository_commit", "sha256"
}
_FINAL_BINDING_KEYS = {
    "bytes", "device", "inode", "path", "sha256", "shard_id", "status"
}
_WITNESS_BINDING_KEYS = {
    "bytes", "device", "inode", "invocation_index", "path", "sha256",
    "shard_id", "status",
}
_INVOCATION_RECEIPT_KEYS = {
    "event_id", "invocation_index", "path", "sha256", "status",
}
_INNER_ARTIFACT_KEYS = {
    "bytes", "device", "event_id", "file_kind", "inode",
    "invocation_index", "path", "sha256",
}
_PRIOR_WITNESS_KEYS = _INNER_ARTIFACT_KEYS | {"status"}
_EMBEDDED_WITNESS_KEYS = {
    "bytes", "device", "inode", "path", "sha256", "status",
    "terminal_witness",
}
_INNER_METER_BINDING_KEYS = {
    "bytes", "device", "inode", "path", "raw_meter", "resource_meter",
    "sha256",
}
_FINAL_WITNESS_BINDING_KEYS = {
    "bytes", "device", "inode", "path", "sha256", "status",
}
_DUMMY_PROCESS_IDENTITY_KEYS = {
    "creation_filetime", "image_sha256", "pid", "retained_handle_through_exit",
}
_PRODUCTION_PROCESS_IDENTITY_KEYS = {
    "argv", "creation_filetime", "cwd", "environment_sha256", "exit_code",
    "handle_acquired_filetime", "image_path", "image_sha256", "job_membership",
    "kernel_time_100ns", "parent_pid", "pid", "retained_handle_through_exit",
    "user_time_100ns",
}
_JOB_CENSUS_KEYS = {
    "active_process_limit", "distinct_job_pids", "job_roles",
    "total_processes", "worker_children",
}
_S_EXIT_KEYS = {"exit_code", "handle_retained_through_exit", "identity"}
_PUBLICATION_KEYS = {
    "bytes", "device", "inode", "path", "sha256",
    "source_final_same_device_inode", "temporary_unlinked",
    "reopened_bytes_equal",
}
_PROCESS_TREE_KEYS = {
    "aggregation_launch_slots", "os_process_creations",
    "inert_launcher_redirector_count", "scientific_worker_children",
    "scientific_worker_count",
}
_INNER_METER_KEYS = {
    "artifact", "job_process_events", "milestones", "qpc_clock_id",
    "qpc_frequency", "s_process_creation_filetime", "samples", "schema",
    "scientific_stop_filetime", "terminal_child_exit_filetime",
}
_OUTER_METER_KEYS = {
    "artifact", "invocation_index", "milestones",
    "o_process_creation_filetime", "qpc_clock_id", "qpc_frequency",
    "samples", "schema", "terminal_endpoint_filetime",
}
_METER_SAMPLE_KEYS = {
    "qpc_clock_id", "qpc_frequency", "qpc_tick", "roles", "sample_index",
    "utc_filetime",
}
_METER_ROLE_KEYS = {
    "alive", "creation_filetime", "current_working_set_bytes", "exit_code",
    "image_sha256", "kernel_time_100ns", "peak_working_set_bytes", "pid",
    "state", "user_time_100ns",
}
_TERMINAL_RESOURCE_KEYS = {
    "charged_process_roles", "cpu_100ns_by_role", "cpu_seconds_sum",
    "full_wall_seconds", "inner_sample_count", "lifetime_peak_upper_bytes",
    "max_merged_concurrent_working_set_bytes",
    "max_observed_sampling_gap_seconds", "o_process_creation_filetime",
    "outer_sample_count", "rss_gate_bytes", "scientific_stop_wall_seconds",
    "terminal_endpoint_filetime",
}
_INNER_RESOURCE_KEYS = {
    "charged_process_roles", "cpu_100ns_by_role", "cpu_seconds_sum",
    "endpoint_qpc_tick", "full_wall_seconds", "lifetime_peak_upper_bytes",
    "max_observed_sampling_gap_seconds",
    "max_sampled_concurrent_working_set_bytes", "qpc_frequency",
    "rss_gate_bytes", "sample_count", "s_process_creation_filetime",
    "scientific_stop_qpc_tick", "scientific_stop_wall_seconds",
    "t0_qpc_tick", "terminal_child_exit_filetime",
}
_INNER_MILESTONE_KEYS = {
    "checkpoint_publication_verified_qpc_tick", "done_received_qpc_tick",
    "exit_released_qpc_tick", "launcher_exit_qpc_tick",
    "result_publication_verified_qpc_tick", "stream_closed_qpc_tick",
    "worker_exit_qpc_tick",
}
_OUTER_MILESTONE_KEYS = {
    "final_shard_publication_verified_qpc_tick", "s_exit_qpc_tick",
    "s_spawn_qpc_tick", "stream_closed_qpc_tick",
}
_JOB_EVENT_KEYS = {"creation_filetime", "event", "pid", "qpc_tick", "role"}
_PROCESS_STATE_RANK = {"NOT_CREATED": 0, "ALIVE": 1, "EXITED": 2}
_AUTHORITY_REQUIRED_NAMES = {
    "M245_PREDECLARATION_20260810.md",
    "M245_FROZEN_MANIFEST_V1_20260810.json",
    "M245_SHA256SUMS_V1_20260810.txt",
    "M245_PREMATERIALIZATION_ERRATUM1_20260810.md",
    "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json",
    "M245_SHA256SUMS_V1_OVERLAY1_20260810.txt",
    "supervise_m245_fixture_materialization.py",
    "materialize_m245_fixtures.py",
    "test_m245_fixture_materialization_transport.py",
    "M245_FIXTURE_MATERIALIZATION_TDD_RECEIPT_20260810.md",
    "M245_FIXTURE_MATERIALIZATION_STATIC_VALIDATION_RECEIPT_20260810.json",
    "M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json",
    "M245_FROZEN_MANIFEST_V2_20260810.json",
    "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json",
    "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json",
    "M245_SHA256SUMS_V2_20260810.txt",
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md",
    "M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md",
    "M245_SHA256SUMS_V2_OVERLAY2_20260810.txt",
    "m245_primary_core.py", "m245_replica_core.py",
    "m245_scientific_worker.py", "run_m245_scientific_shard.py",
    "launch_m245_scientific_invocation.py", "aggregate_m245_spectrum.py",
    "test_m245_primary_core.py", "test_m245_replica_core.py",
    "test_m245_scientific_transport.py", "test_m245_aggregation.py",
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md",
    "M245_SCIENTIFIC_STATIC_AUDIT_CONTRACT_20260810.md",
    "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
    "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    "M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json",
}

_GIT_PROCESS_CREATIONS = 0
_OBSERVED_GIT_CHILDREN: list[dict] = []


class _FILETIME(ctypes.Structure):
    _fields_ = (
        ("dwLowDateTime", wintypes.DWORD),
        ("dwHighDateTime", wintypes.DWORD),
    )


def _filetime_integer(value: _FILETIME) -> int:
    return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)


def _process_creation_filetime_from_handle(handle: int) -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    creation, exit_time, kernel, user = (_FILETIME() for _ in range(4))
    _require(
        bool(kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel),
            ctypes.byref(user),
        )),
        "cannot observe child process creation time",
    )
    creation_value = _filetime_integer(creation)
    _require(creation_value > 0, "invalid child process creation time")
    return creation_value


def _observed_windows_command_line_argv() -> list[str]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    kernel32.GetCommandLineW.argtypes = []
    kernel32.GetCommandLineW.restype = wintypes.LPCWSTR
    shell32.CommandLineToArgvW.argtypes = [
        wintypes.LPCWSTR,
        ctypes.POINTER(ctypes.c_int),
    ]
    shell32.CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    command_line = kernel32.GetCommandLineW()
    _require(isinstance(command_line, str) and command_line, "missing OS command line")
    count = ctypes.c_int()
    pointer = shell32.CommandLineToArgvW(command_line, ctypes.byref(count))
    _require(bool(pointer) and count.value > 0, "cannot parse OS command line")
    try:
        return [pointer[index] for index in range(count.value)]
    finally:
        kernel32.LocalFree(ctypes.cast(pointer, ctypes.c_void_p))


def _process_lifetime_seconds_at_terminal_boundary() -> Decimal:
    """Measure from OS process creation through this terminal observation."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.GetSystemTimePreciseAsFileTime.argtypes = [ctypes.POINTER(_FILETIME)]
    kernel32.GetSystemTimePreciseAsFileTime.restype = None
    creation, exit_time, kernel, user = (_FILETIME() for _ in range(4))
    handle = kernel32.GetCurrentProcess()
    _require(bool(handle), "cannot acquire aggregation process handle")
    _require(
        bool(kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel),
            ctypes.byref(user),
        )),
        "cannot observe aggregation process creation time",
    )
    endpoint = _FILETIME()
    kernel32.GetSystemTimePreciseAsFileTime(ctypes.byref(endpoint))
    creation_value = _filetime_integer(creation)
    endpoint_value = _filetime_integer(endpoint)
    _require(
        creation_value > 0 and endpoint_value >= creation_value,
        "invalid aggregation lifetime boundary",
    )
    return Decimal(endpoint_value - creation_value) / Decimal(10_000_000)


def _fail(message: str) -> None:
    raise M245AggregationContractError(message)


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _canonical_json_bytes(payload: object) -> bytes:
    try:
        text = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise M245AggregationContractError("noncanonical JSON value") from exc
    return (text + "\n").encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_commit(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and value != "0" * 40
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _exact_keys(payload: object, keys: tuple[str, ...], context: str) -> dict:
    _require(isinstance(payload, dict), f"{context}: expected object")
    _require(
        set(payload) == set(keys) and len(payload) == len(keys),
        f"{context}: nonexact key schema",
    )
    return payload


def _exact_key_set(payload: object, keys: set[str], context: str) -> dict:
    _require(isinstance(payload, dict), f"{context}: expected object")
    _require(set(payload) == keys and len(payload) == len(keys), f"{context}: nonexact key schema")
    return payload


def _is_reparse(identity: os.stat_result) -> bool:
    attributes = getattr(identity, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _open_regular_handle(path: Path):
    _require(os.path.lexists(path), f"missing file: {path}")
    before = path.lstat()
    _require(not path.is_symlink() and not _is_reparse(before), f"reparse/symlink refused: {path}")
    _require(stat.S_ISREG(before.st_mode), f"nonregular file: {path}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        stream = os.fdopen(descriptor, "rb", closefd=True)
    except BaseException:
        os.close(descriptor)
        raise
    identity = os.fstat(stream.fileno())
    try:
        _require(stat.S_ISREG(identity.st_mode), f"nonregular open handle: {path}")
        _require(
            (before.st_dev, before.st_ino, before.st_size)
            == (identity.st_dev, identity.st_ino, identity.st_size),
            f"file identity drift while opening: {path}",
        )
    except BaseException:
        stream.close()
        raise
    return stream, identity


def _regular_bytes(path: Path) -> tuple[bytes, os.stat_result]:
    stream, before = _open_regular_handle(path)
    try:
        raw = stream.read()
        after = os.fstat(stream.fileno())
    finally:
        stream.close()
    _require(
        (before.st_dev, before.st_ino, before.st_size)
        == (after.st_dev, after.st_ino, after.st_size),
        f"file identity drift: {path}",
    )
    _require(len(raw) == after.st_size, f"short read: {path}")
    return raw, after


def _canonical_payload(path: Path) -> tuple[dict, bytes, os.stat_result]:
    raw, identity = _regular_bytes(path)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise M245AggregationContractError(f"invalid JSON: {path}") from exc
    _require(_canonical_json_bytes(payload) == raw, f"noncanonical JSON bytes: {path}")
    _require(isinstance(payload, dict), f"top-level JSON object required: {path}")
    return payload, raw, identity


def _check_file_binding(path: Path, binding: dict, keys: set[str], context: str) -> bytes:
    _exact_key_set(binding, keys, context)
    raw, identity = _regular_bytes(path)
    _require(str(path.resolve()) == binding["path"], f"{context}: path mismatch")
    _require(identity.st_size == binding["bytes"], f"{context}: byte mismatch")
    _require(identity.st_dev == binding["device"], f"{context}: device mismatch")
    _require(identity.st_ino == binding["inode"], f"{context}: inode mismatch")
    _require(_is_sha256(binding["sha256"]), f"{context}: invalid hash")
    _require(_sha256(raw) == binding["sha256"], f"{context}: hash mismatch")
    return raw


def _retain_bound_file(path: Path, binding: dict, payload: dict, context: str) -> dict:
    stream, identity = _open_regular_handle(path)
    try:
        raw = stream.read()
        _require(str(path.resolve()) == binding["path"], f"{context}: retained path mismatch")
        _require(
            (identity.st_dev, identity.st_ino, identity.st_size)
            == (binding["device"], binding["inode"], binding["bytes"]),
            f"{context}: retained identity mismatch",
        )
        _require(len(raw) == binding["bytes"] and _sha256(raw) == binding["sha256"], f"{context}: retained bytes mismatch")
        _require(raw == _canonical_json_bytes(payload), f"{context}: retained payload mismatch")
        stream.seek(0)
    except BaseException:
        stream.close()
        raise
    return {
        "binding": binding,
        "context": context,
        "identity": identity,
        "path": path,
        "raw": raw,
        "stream": stream,
    }


def _retain_authorized_inputs(
    authorization_path: Path,
    authorization_binding: dict,
    authorization: dict,
    finals: list[dict],
    witnesses: list[dict],
) -> list[dict]:
    specifications = [(authorization_path, authorization_binding, authorization, "authorization")]
    specifications.extend(
        (Path(row["path"]), row, payload, f"final shard {index}")
        for index, (row, payload) in enumerate(zip(authorization["final_shard_receipts"], finals))
    )
    specifications.extend(
        (Path(row["path"]), row, payload, f"terminal witness {index}")
        for index, (row, payload) in enumerate(zip(authorization["terminal_witnesses"], witnesses))
    )
    retained: list[dict] = []
    try:
        for path, binding, payload, context in specifications:
            retained.append(_retain_bound_file(path, binding, payload, context))
    except BaseException:
        for item in retained:
            item["stream"].close()
        raise
    return retained


def _verify_retained_inputs(retained: list[dict]) -> None:
    for item in retained:
        stream = item["stream"]
        stream.seek(0)
        raw = stream.read()
        identity = os.fstat(stream.fileno())
        expected = item["identity"]
        _require(
            raw == item["raw"]
            and (identity.st_dev, identity.st_ino, identity.st_size)
            == (expected.st_dev, expected.st_ino, expected.st_size),
            f"{item['context']}: retained handle drift",
        )
        reopened, reopened_identity = _regular_bytes(item["path"])
        _require(
            reopened == raw
            and (reopened_identity.st_dev, reopened_identity.st_ino, reopened_identity.st_size)
            == (expected.st_dev, expected.st_ino, expected.st_size),
            f"{item['context']}: reopen drift",
        )


def _close_retained_inputs(retained: list[dict]) -> None:
    for item in retained:
        item["stream"].close()


def _run_git(
    root: Path,
    *arguments: str,
    required: bool = True,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    global _GIT_PROCESS_CREATIONS
    command = ["git", "-C", str(root), *arguments]
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        handle = getattr(process, "_handle", None)
        _require(handle is not None, "Git child lacks a retained OS process handle")
        observation = {
            "argv": command,
            "creation_filetime": _process_creation_filetime_from_handle(int(handle)),
            "exit_code": None,
            "pid": process.pid,
        }
        _require(
            _is_nonnegative_int(observation["pid"])
            and observation["pid"] > 0
            and all(
                (row["pid"], row["creation_filetime"])
                != (observation["pid"], observation["creation_filetime"])
                for row in _OBSERVED_GIT_CHILDREN
            ),
            "duplicate or invalid Git child identity",
        )
        _OBSERVED_GIT_CHILDREN.append(observation)
        _GIT_PROCESS_CREATIONS += 1
        try:
            stdout, stderr = process.communicate(input=input_bytes, timeout=30)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.communicate()
            observation["exit_code"] = process.returncode
            raise M245AggregationContractError("Git authority verification timed out") from exc
        observation["exit_code"] = process.returncode
        _require(
            _process_creation_filetime_from_handle(int(handle))
            == observation["creation_filetime"],
            "Git child identity changed through exit",
        )
        completed = subprocess.CompletedProcess(
            command,
            process.returncode,
            stdout,
            stderr,
        )
    except M245AggregationContractError:
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate()
        raise
    except OSError as exc:
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate()
        raise M245AggregationContractError("Git authority verification failed") from exc
    if required and completed.returncode != 0:
        _fail("Git authority verification failed")
    return completed


def _repo_context(path: Path) -> tuple[Path, str]:
    resolved = path.resolve()
    root: Path | None = None
    for candidate in (resolved.parent, *resolved.parents):
        if os.path.lexists(candidate / ".git"):
            root = candidate.resolve()
            break
    _require(root is not None, "authorization is not inside a Git repository")
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise M245AggregationContractError("authorization escapes repository") from exc
    return root, relative


def _git_batch_objects(
    root: Path,
    expressions: list[str],
) -> dict[str, tuple[str, str, bytes] | None]:
    _require(len(expressions) == len(set(expressions)), "duplicate Git batch expression")
    request = b"".join(expression.encode("utf-8") + b"\n" for expression in expressions)
    completed = _run_git(root, "cat-file", "--batch", input_bytes=request)
    raw = completed.stdout
    offset = 0
    objects: dict[str, tuple[str, str, bytes] | None] = {}
    for expression in expressions:
        newline = raw.find(b"\n", offset)
        _require(newline >= 0, "truncated Git batch header")
        header = raw[offset:newline]
        offset = newline + 1
        missing = expression.encode("utf-8") + b" missing"
        if header == missing:
            objects[expression] = None
            continue
        parts = header.rsplit(b" ", 2)
        _require(len(parts) == 3, "malformed Git batch header")
        try:
            object_id = parts[0].decode("ascii")
            object_type = parts[1].decode("ascii")
            size = int(parts[2].decode("ascii"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise M245AggregationContractError("malformed Git batch object") from exc
        _require(_is_sha256(object_id) or _is_commit(object_id), "invalid Git object id")
        _require(size >= 0 and offset + size < len(raw), "truncated Git batch object")
        content = raw[offset:offset + size]
        offset += size
        _require(raw[offset:offset + 1] == b"\n", "malformed Git batch separator")
        offset += 1
        objects[expression] = (object_id, object_type, content)
    _require(offset == len(raw), "unexpected trailing Git batch output")
    return objects


def _is_production_authorization_path(path: Path) -> bool:
    root, relative = _repo_context(path)
    source = Path(__file__).resolve()
    source_root, _source_relative = _repo_context(source)
    expected = (
        Path(AUTHORITY_DIRECTORY_REPO_RELATIVE) / _NAMESPACE["authorization"]
    ).as_posix()
    return (
        relative == expected
        and root.resolve() == source_root.resolve()
        and path.resolve().parent == source.parent
    )


def _authorized_input_root(authorization_path: Path) -> Path:
    repository_root, _relative = _repo_context(authorization_path)
    if _is_production_authorization_path(authorization_path):
        lexical_root = repository_root / SHARD_DIRECTORY_REPO_RELATIVE
        _require(os.path.lexists(lexical_root), "authorized shard root is absent")
        try:
            lexical_identity = os.lstat(lexical_root)
        except OSError as exc:
            raise M245AggregationContractError("cannot inspect authorized shard root") from exc
        _require(stat.S_ISDIR(lexical_identity.st_mode), "authorized shard root is not a directory")
        _require(
            not lexical_root.is_symlink() and not _is_reparse(lexical_identity),
            "authorized shard root is a reparse point",
        )
        resolved_repository = repository_root.resolve()
        resolved_root = lexical_root.resolve(strict=True)
        try:
            resolved_relative = resolved_root.relative_to(resolved_repository)
        except ValueError as exc:
            raise M245AggregationContractError("authorized shard root escapes repository") from exc
        _require(
            resolved_relative.as_posix() == SHARD_DIRECTORY_REPO_RELATIVE,
            "authorized shard root resolves to a different repository path",
        )
        return resolved_root
    return authorization_path.resolve().parent


def aggregation_contract() -> dict:
    return copy.deepcopy(_CONTRACT)


def aggregation_namespace() -> dict:
    return copy.deepcopy(_NAMESPACE)


def _validate_authorization_payload(
    payload: dict,
    path: Path,
    *,
    require_zero_paths_now: bool,
) -> None:
    _exact_keys(payload, _AUTH_KEYS, "aggregation authorization")
    _require(payload["artifact"] == "M245_AGGREGATION_INPUT_AUTHORIZATION", "wrong authorization artifact")
    _require(payload["schema"] == "m245-aggregation-input-authorization-v1", "wrong authorization schema")
    _require(_is_sha256(payload["shard_trigger_sha256"]), "invalid trigger hash")
    _require(_is_commit(payload["observed_parent_head"]), "invalid observed parent")
    _require(_is_sha256(payload["aggregate_source_sha256"]), "invalid aggregate source hash")
    expected_argv = [
        STDLIB_PYTHON,
        "-I", "-B", "-S", "-u",
        str(Path(__file__).resolve()),
        "--authorization",
        str(path.resolve()),
    ]
    _require(payload["aggregate_argv"] == expected_argv, "aggregate argv drift")
    _require(payload["aggregate_cwd"] == str(Path(__file__).resolve().parent), "aggregate cwd drift")
    _require(payload["status"] == "PASS_COMMITTED_INPUT_AUTHORIZATION", "authorization did not pass")
    zero = payload["zero_prior_paths"]
    expected_zero = {
        _NAMESPACE["intent"]: "ABSENT",
        _NAMESPACE["result"]: "ABSENT",
        _NAMESPACE["receipt"]: "ABSENT",
    }
    _require(zero == expected_zero, "nonexact zero-prior-path census")
    if require_zero_paths_now:
        for name in expected_zero:
            _require(not os.path.lexists(path.parent / name), f"prior aggregation path exists: {name}")
    finals = payload["final_shard_receipts"]
    witnesses = payload["terminal_witnesses"]
    _require(isinstance(finals, list) and len(finals) == 4, "four final bindings required")
    _require(isinstance(witnesses, list) and len(witnesses) == 8, "eight witness bindings required")
    for shard_id, row in enumerate(finals):
        _exact_key_set(row, _FINAL_BINDING_KEYS, f"final binding {shard_id}")
        _require(row["shard_id"] == shard_id, "final binding shard order drift")
        _require(Path(row["path"]).name == FINAL_RECEIPT_NAMES[shard_id], "final binding name drift")
        _require(row["status"] == "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS", "wrong provisional final status")
    expected_pairs = [(shard_id, invocation) for shard_id in ASSIGNMENTS for invocation in (1, 2)]
    for row, pair in zip(witnesses, expected_pairs):
        _exact_key_set(row, _WITNESS_BINDING_KEYS, f"witness binding {pair}")
        _require((row["shard_id"], row["invocation_index"]) == pair, "witness order drift")
        expected_status = "PASS_M245_INVOCATION_BOUND" if pair[1] == 1 else "PASS_M245_SHARD_BOUND"
        _require(row["status"] == expected_status, "wrong witness status")
        expected_name = (
            f"M245_S{pair[0]}_I{pair[1]}_{ASSIGNMENTS[pair[0]][pair[1]-1]}_"
            "TERMINAL_WITNESS_20260810.json"
        )
        _require(Path(row["path"]).name == expected_name, "witness name drift")


def _validate_authorization(
    authorization_path: str | os.PathLike[str],
    authorization_binding: dict,
    *,
    require_zero_paths_now: bool,
    first_containing_proof: tuple[Path, str, str] | None = None,
) -> None:
    path = Path(authorization_path)
    _exact_key_set(authorization_binding, _AUTH_BINDING_KEYS, "authorization binding")
    _require(_is_commit(authorization_binding["repository_commit"]), "invalid authorization commit")
    raw = _check_file_binding(path, authorization_binding, _AUTH_BINDING_KEYS, "authorization binding")
    payload, canonical_raw, second_identity = _canonical_payload(path)
    _require(raw == canonical_raw, "authorization changed across reads")
    _require(
        (second_identity.st_dev, second_identity.st_ino, second_identity.st_size)
        == (authorization_binding["device"], authorization_binding["inode"], authorization_binding["bytes"]),
        "authorization identity changed across reads",
    )
    _validate_authorization_payload(
        payload,
        path,
        require_zero_paths_now=require_zero_paths_now,
    )

    root, relative = _repo_context(path)
    commit = authorization_binding["repository_commit"]
    if first_containing_proof is None:
        added = _run_git(
            root,
            "log", "--diff-filter=A", "--format=%H", "--", relative,
        ).stdout.decode("utf-8").splitlines()
        _require(added == [commit], "authorization commit is not the unique first-containing commit")
    else:
        proof_root, proof_relative, proof_commit = first_containing_proof
        _require(
            (proof_root.resolve(), proof_relative, proof_commit)
            == (root, relative, commit),
            "first-containing Git proof scope drift",
        )

    parent = payload["observed_parent_head"]
    relative_parent = Path(relative).parent
    forbidden_paths = [
        (relative_parent / _NAMESPACE[key]).as_posix()
        for key in (
            "intent_temp", "intent", "result_temp", "result",
            "receipt_temp", "receipt",
        )
    ]
    expressions = [commit, f"{commit}:{relative}", f"{parent}:{relative}"]
    expressions.extend(
        f"{revision}:{forbidden}"
        for forbidden in forbidden_paths
        for revision in (parent, commit)
    )
    objects = _git_batch_objects(root, expressions)
    commit_object = objects[commit]
    _require(commit_object is not None and commit_object[1] == "commit", "authorization commit object missing")
    header = commit_object[2].split(b"\n\n", 1)[0]
    parents = [
        line[7:].decode("ascii")
        for line in header.splitlines()
        if line.startswith(b"parent ")
    ]
    _require(parents == [parent], "observed parent mismatch or merge authorization")
    authorization_blob = objects[f"{commit}:{relative}"]
    _require(
        authorization_blob is not None
        and authorization_blob[1] == "blob"
        and authorization_blob[2] == raw,
        "authorization Git blob differs from disk",
    )
    _require(objects[f"{parent}:{relative}"] is None, "authorization existed in its parent")
    for forbidden in forbidden_paths:
        _require(
            objects[f"{parent}:{forbidden}"] is None
            and objects[f"{commit}:{forbidden}"] is None,
            "prior or authorization-commit aggregate namespace exists",
        )


def validate_aggregation_authorization(authorization_path: str | os.PathLike[str], authorization_binding: dict) -> None:
    _validate_authorization(
        authorization_path,
        authorization_binding,
        require_zero_paths_now=True,
    )


def _validate_firewall(payload: object, context: str) -> None:
    _require(isinstance(payload, dict), f"{context}: firewall object required")
    _require(set(payload) == set(_FIREWALL_KEYS), f"{context}: firewall key drift")
    _require(all(value is False for value in payload.values()), f"{context}: firewall violation")


def _validate_small_firewall(payload: object, context: str) -> None:
    _require(isinstance(payload, dict) and payload, f"{context}: firewall object required")
    _require(all(value is False for value in payload.values()), f"{context}: firewall violation")


def _validate_hash_map(payload: object, context: str) -> dict:
    _require(isinstance(payload, dict) and payload, f"{context}: authority map required")
    _require(all(isinstance(name, str) and _is_sha256(value) for name, value in payload.items()), f"{context}: invalid authority map")
    return payload


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_receipt_identity(payload: dict, context: str) -> None:
    _require(_is_nonnegative_int(payload.get("bytes")), f"{context}: invalid byte count")
    _require(_is_nonnegative_int(payload.get("device")), f"{context}: invalid device")
    _require(_is_nonnegative_int(payload.get("inode")), f"{context}: invalid inode")
    _require(isinstance(payload.get("path"), str) and payload["path"], f"{context}: invalid path")
    _require(_is_sha256(payload.get("sha256")), f"{context}: invalid hash")


def _expected_inner_name(shard_id: int, invocation_index: int, event_id: str, kind: str) -> str:
    suffix = {
        "result": "RESULT",
        "checkpoint": "CHECKPOINT",
        "meter": "METER",
        "provisional_receipt": "RECEIPT",
    }[kind]
    return f"M245_S{shard_id}_I{invocation_index}_{event_id}_{suffix}_20260810.json"


def _validate_inner_artifacts(
    payload: object,
    shard_id: int,
    invocation_index: int,
    event_id: str,
) -> list[dict]:
    _require(isinstance(payload, list) and len(payload) == 4, "inner artifact census drift")
    kinds = ("result", "checkpoint", "meter", "provisional_receipt")
    rows: list[dict] = []
    for row, kind in zip(payload, kinds):
        artifact = _exact_key_set(row, _INNER_ARTIFACT_KEYS, f"inner artifact {shard_id}/{invocation_index}/{kind}")
        _validate_receipt_identity(artifact, f"inner artifact {shard_id}/{invocation_index}/{kind}")
        _require(artifact["file_kind"] == kind, "inner artifact kind/order drift")
        _require(artifact["event_id"] == event_id, "inner artifact event drift")
        _require(artifact["invocation_index"] == invocation_index, "inner artifact invocation drift")
        _require(
            Path(artifact["path"]).name
            == _expected_inner_name(shard_id, invocation_index, event_id, kind),
            "inner artifact path drift",
        )
        rows.append(artifact)
    return rows


def _validate_dummy_outer_lifetime_boundary(samples: list[dict]) -> None:
    """Retain only the frozen test's intentionally lossy lifetime labels."""

    _require(
        samples[0]["roles"]["S"]["state"] in {"NOT_CREATED", "ALIVE"}
        and samples[-1]["roles"]["S"]["state"] == "EXITED"
        and all(sample["roles"]["O"]["state"] == "ALIVE" for sample in samples),
        "dummy outer lifetime boundary drift",
    )


def _validate_production_outer_lifetime_boundary(samples: list[dict]) -> None:
    _require(
        samples[0]["roles"]["S"]["state"] == "NOT_CREATED"
        and samples[-1]["roles"]["S"]["state"] == "EXITED"
        and samples[-1]["roles"]["O"]["state"] == "ALIVE"
        and all(sample["roles"]["O"]["state"] == "ALIVE" for sample in samples),
        "production outer pre-spawn/terminal lifetime boundary drift",
    )


def _validate_stream_close(
    samples: list[dict],
    stream_closed_tick: int,
    frequency: int,
    clock_offset_filetime: int,
    context: str,
) -> int:
    last_tick = samples[-1]["qpc_tick"]
    _require(
        last_tick <= stream_closed_tick
        and (stream_closed_tick - last_tick) * 10 <= frequency,
        f"{context}: stream close/sample gap drift",
    )
    close_filetime = (
        clock_offset_filetime
        + stream_closed_tick * 10_000_000 // frequency
    )
    _require(
        samples[-1]["utc_filetime"] <= close_filetime,
        f"{context}: sample occurs after stream close",
    )
    return close_filetime


def _validate_meter_stream(
    payload: object,
    *,
    outer: bool,
    invocation_index: int,
    expected_identities: dict | None = None,
    production: bool = False,
) -> tuple[dict, Decimal, int]:
    context = "outer meter" if outer else "inner meter"
    keys = _OUTER_METER_KEYS if outer else _INNER_METER_KEYS
    meter = _exact_key_set(payload, keys, context)
    expected_artifact = "M245_OUTER_RAW_METER" if outer else "M245_SHARD_RAW_METER"
    expected_schema = "m245-outer-raw-meter-v1" if outer else "m245-shard-raw-meter-v1"
    _require(meter["artifact"] == expected_artifact and meter["schema"] == expected_schema, f"{context}: identity drift")
    if outer:
        _require(meter["invocation_index"] == invocation_index, "outer meter invocation drift")
    frequency = meter["qpc_frequency"]
    clock = meter["qpc_clock_id"]
    _require(_is_nonnegative_int(frequency) and frequency > 0, f"{context}: invalid frequency")
    _require(isinstance(clock, str) and clock, f"{context}: invalid clock")
    samples = meter["samples"]
    _require(isinstance(samples, list) and len(samples) > 1, f"{context}: sample census drift")
    expected_roles = {"O", "S"} if outer else {"S", "L", "W"}
    prior_tick: int | None = None
    prior_filetime: int | None = None
    prior_by_role: dict[str, dict] = {}
    observed_identities: dict[str, tuple[int, int, str] | None] = {
        role: None for role in expected_roles
    }
    maximum_gap = Decimal("0")
    clock_offset_filetime: int | None = None
    for index, row in enumerate(samples):
        sample = _exact_key_set(row, _METER_SAMPLE_KEYS, f"{context} sample {index}")
        _require(sample["sample_index"] == index, f"{context}: sample order drift")
        _require(sample["qpc_clock_id"] == clock and sample["qpc_frequency"] == frequency, f"{context}: clock drift")
        tick = sample["qpc_tick"]
        _require(_is_nonnegative_int(tick) and (prior_tick is None or tick > prior_tick), f"{context}: nonmonotonic ticks")
        filetime = sample["utc_filetime"]
        _require(
            _is_nonnegative_int(filetime)
            and (prior_filetime is None or filetime > prior_filetime),
            f"{context}: invalid or nonmonotonic FILETIME",
        )
        offset_filetime = filetime - (tick * 10_000_000 // frequency)
        if clock_offset_filetime is None:
            clock_offset_filetime = offset_filetime
        else:
            _require(offset_filetime == clock_offset_filetime, f"{context}: QPC/FILETIME clock drift")
        if prior_tick is not None:
            gap = Decimal(tick - prior_tick) / Decimal(frequency)
            _require(gap <= Decimal("0.100000000"), f"{context}: sampling gap cap failed")
            maximum_gap = max(maximum_gap, gap)
        roles = sample["roles"]
        _require(isinstance(roles, dict) and set(roles) == expected_roles, f"{context}: role census drift")
        for role, role_payload in roles.items():
            role_row = _exact_key_set(role_payload, _METER_ROLE_KEYS, f"{context} {role}/{index}")
            for field in (
                "current_working_set_bytes", "kernel_time_100ns",
                "peak_working_set_bytes", "user_time_100ns",
            ):
                _require(_is_nonnegative_int(role_row[field]), f"{context}: invalid {role} {field}")
            state = role_row["state"]
            _require(state in _PROCESS_STATE_RANK, f"{context}: invalid process state")
            _require(role_row["alive"] is (state == "ALIVE"), f"{context}: alive/state disagreement")
            _require(
                role_row["current_working_set_bytes"]
                <= role_row["peak_working_set_bytes"],
                f"{context}: current RSS exceeds peak for {role}",
            )
            if state == "NOT_CREATED":
                _require(
                    all(role_row[field] is None for field in (
                        "creation_filetime", "exit_code", "image_sha256", "pid",
                    )),
                    f"{context}: not-created identity present for {role}",
                )
                _require(
                    all(role_row[field] == 0 for field in (
                        "current_working_set_bytes", "kernel_time_100ns",
                        "peak_working_set_bytes", "user_time_100ns",
                    )),
                    f"{context}: not-created counters present for {role}",
                )
            else:
                _require(
                    _is_nonnegative_int(role_row["pid"])
                    and role_row["pid"] > 0
                    and _is_nonnegative_int(role_row["creation_filetime"])
                    and role_row["creation_filetime"] > 0
                    and _is_sha256(role_row["image_sha256"]),
                    f"{context}: incomplete immutable identity for {role}",
                )
                identity = (
                    role_row["pid"],
                    role_row["creation_filetime"],
                    role_row["image_sha256"],
                )
                prior_identity = observed_identities[role]
                _require(prior_identity in (None, identity), f"{context}: identity drift for {role}")
                observed_identities[role] = identity
                if expected_identities is not None:
                    expected = expected_identities[role]
                    _require(
                        identity
                        == (expected["pid"], expected["creation_filetime"], expected["image_sha256"]),
                        f"{context}: retained identity mismatch for {role}",
                    )
                if state == "ALIVE":
                    _require(role_row["exit_code"] is None, f"{context}: live process has exit code")
                else:
                    _require(
                        _is_nonnegative_int(role_row["exit_code"])
                        and role_row["exit_code"] == 0,
                        f"{context}: unsuccessful process exit",
                    )
                    _require(role_row["current_working_set_bytes"] == 0, f"{context}: exited process has current RSS")
            previous = prior_by_role.get(role)
            if previous is not None:
                _require(
                    _PROCESS_STATE_RANK[state] >= _PROCESS_STATE_RANK[previous["state"]],
                    f"{context}: process state rollback for {role}",
                )
                for field in (
                    "kernel_time_100ns", "peak_working_set_bytes", "user_time_100ns",
                ):
                    _require(role_row[field] >= previous[field], f"{context}: {field} rollback for {role}")
            prior_by_role[role] = role_row
        prior_tick = tick
        prior_filetime = filetime
    _require(clock_offset_filetime is not None, f"{context}: missing clock correlation")
    _require(all(value is not None for value in observed_identities.values()), f"{context}: incomplete role identities")

    first_tick = samples[0]["qpc_tick"]
    last_tick = samples[-1]["qpc_tick"]
    if outer:
        milestones = _exact_key_set(meter["milestones"], _OUTER_MILESTONE_KEYS, "outer milestones")
        for name in ("s_spawn_qpc_tick", "s_exit_qpc_tick", "stream_closed_qpc_tick"):
            _require(_is_nonnegative_int(milestones[name]), f"outer milestones: invalid {name}")
        final_tick = milestones["final_shard_publication_verified_qpc_tick"]
        if production:
            _require(
                first_tick
                < milestones["s_spawn_qpc_tick"]
                < milestones["s_exit_qpc_tick"],
                "production outer pre-spawn chronology drift",
            )
        else:
            _require(
                first_tick <= milestones["s_spawn_qpc_tick"],
                "dummy outer pre-spawn chronology drift",
            )
        _require(
            milestones["s_spawn_qpc_tick"]
            < milestones["s_exit_qpc_tick"]
            < milestones["stream_closed_qpc_tick"],
            "outer milestone order drift",
        )
        close_filetime = _validate_stream_close(
            samples,
            milestones["stream_closed_qpc_tick"],
            frequency,
            clock_offset_filetime,
            context,
        )
        if invocation_index == 1:
            _require(final_tick is None, "invocation one carries a final-shard milestone")
        else:
            _require(
                _is_nonnegative_int(final_tick)
                and milestones["s_exit_qpc_tick"] < final_tick < last_tick,
                "invocation two final-shard milestone drift",
            )
        if production:
            _validate_production_outer_lifetime_boundary(samples)
        else:
            _validate_dummy_outer_lifetime_boundary(samples)
        if expected_identities is not None:
            _require(
                meter["o_process_creation_filetime"]
                == expected_identities["O"]["creation_filetime"],
                "outer O creation identity drift",
            )
        _require(
            meter["terminal_endpoint_filetime"] >= close_filetime,
            "outer endpoint precedes stream close",
        )
    else:
        milestones = _exact_key_set(meter["milestones"], _INNER_MILESTONE_KEYS, "inner milestones")
        _require(all(_is_nonnegative_int(value) for value in milestones.values()), "inner milestone type drift")
        _require(
            first_tick
            <= milestones["result_publication_verified_qpc_tick"]
            < milestones["checkpoint_publication_verified_qpc_tick"]
            < milestones["done_received_qpc_tick"]
            < milestones["exit_released_qpc_tick"]
            <= milestones["worker_exit_qpc_tick"]
            <= milestones["launcher_exit_qpc_tick"]
            <= last_tick
            <= milestones["stream_closed_qpc_tick"],
            "inner milestone order drift",
        )
        close_filetime = _validate_stream_close(
            samples,
            milestones["stream_closed_qpc_tick"],
            frequency,
            clock_offset_filetime,
            context,
        )
        _require(
            samples[0]["roles"]["L"]["state"] == "NOT_CREATED"
            and samples[0]["roles"]["W"]["state"] == "NOT_CREATED"
            and samples[-1]["roles"]["L"]["state"] == "EXITED"
            and samples[-1]["roles"]["W"]["state"] == "EXITED"
            and all(sample["roles"]["S"]["state"] == "ALIVE" for sample in samples),
            "inner child lifetime boundary drift",
        )
        events = meter["job_process_events"]
        _require(isinstance(events, list) and len(events) == 4, "job process event census drift")
        expected_event_pairs = (
            ("L", "NEW_PROCESS"), ("W", "NEW_PROCESS"),
            ("W", "EXIT_PROCESS"), ("L", "EXIT_PROCESS"),
        )
        prior_event_tick: int | None = None
        for event, (role, event_name) in zip(events, expected_event_pairs):
            row = _exact_key_set(event, _JOB_EVENT_KEYS, "job process event")
            _require(row["role"] == role and row["event"] == event_name, "job process event order drift")
            _require(
                _is_nonnegative_int(row["qpc_tick"])
                and first_tick <= row["qpc_tick"] <= last_tick
                and (prior_event_tick is None or row["qpc_tick"] >= prior_event_tick),
                "job process event chronology drift",
            )
            identity = observed_identities[role]
            _require(
                identity is not None
                and (row["pid"], row["creation_filetime"]) == identity[:2],
                "job process event identity drift",
            )
            prior_event_tick = row["qpc_tick"]
        _require(
            events[2]["qpc_tick"] == milestones["worker_exit_qpc_tick"]
            and events[3]["qpc_tick"] == milestones["launcher_exit_qpc_tick"],
            "job exit/milestone disagreement",
        )
        if expected_identities is not None:
            _require(
                meter["s_process_creation_filetime"]
                == expected_identities["S"]["creation_filetime"],
                "inner S creation identity drift",
            )
        _require(
            samples[0]["utc_filetime"]
            <= meter["scientific_stop_filetime"]
            <= meter["terminal_child_exit_filetime"]
            <= samples[-1]["utc_filetime"]
            <= close_filetime,
            "inner FILETIME chronology drift",
        )
    return meter, maximum_gap, clock_offset_filetime


def _as_finite_decimal(value: object, context: str) -> Decimal:
    try:
        observed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise M245AggregationContractError(f"{context}: invalid decimal") from exc
    _require(observed.is_finite(), f"{context}: nonfinite decimal")
    return observed


def _sample_at_or_before(
    samples: list[dict],
    tick: int,
    frequency: int,
) -> dict:
    selected: dict | None = None
    for sample in samples:
        if sample["qpc_tick"] > tick:
            break
        selected = sample
    _require(selected is not None, "missing prior sample at union QPC tick")
    _require(
        (tick - selected["qpc_tick"]) * 10 <= frequency,
        "sample carry exceeds 0.1 seconds",
    )
    return selected


def _validate_inner_resource(resource_payload: object, meter_payload: object) -> None:
    meter, maximum_gap, offset_filetime = _validate_meter_stream(
        meter_payload,
        outer=False,
        invocation_index=2,
    )
    resource = _exact_key_set(resource_payload, _INNER_RESOURCE_KEYS, "inner resource meter")
    samples = meter["samples"]
    terminal = samples[-1]["roles"]
    cpu = {
        role: terminal[role]["kernel_time_100ns"] + terminal[role]["user_time_100ns"]
        for role in ("S", "L", "W")
    }
    _require(resource["charged_process_roles"] == ["S", "L", "W"], "inner charged role order drift")
    _require(resource["cpu_100ns_by_role"] == cpu, "inner CPU role reduction drift")
    cpu_seconds = Decimal(sum(cpu.values())) / Decimal(10_000_000)
    sampled = max(
        sum(row["current_working_set_bytes"] for row in sample["roles"].values())
        for sample in samples
    )
    lifetime_peak = sum(
        max(sample["roles"][role]["peak_working_set_bytes"] for sample in samples)
        for role in ("S", "L", "W")
    )
    full_wall = Decimal(
        meter["terminal_child_exit_filetime"] - meter["s_process_creation_filetime"]
    ) / Decimal(10_000_000)
    science_wall = Decimal(
        meter["scientific_stop_filetime"] - meter["s_process_creation_filetime"]
    ) / Decimal(10_000_000)
    scientific_stop_tick = resource["scientific_stop_qpc_tick"]
    _require(
        _is_nonnegative_int(scientific_stop_tick)
        and samples[0]["qpc_tick"] <= scientific_stop_tick <= samples[-1]["qpc_tick"],
        "inner scientific-stop tick is outside the sampled lifetime",
    )
    _require(
        meter["scientific_stop_filetime"]
        == offset_filetime
        + scientific_stop_tick * 10_000_000 // meter["qpc_frequency"],
        "inner scientific-stop FILETIME/QPC conversion drift",
    )
    exact_values = {
        "cpu_seconds_sum": cpu_seconds,
        "full_wall_seconds": full_wall,
        "max_observed_sampling_gap_seconds": maximum_gap,
        "scientific_stop_wall_seconds": science_wall,
    }
    for field, expected in exact_values.items():
        _require(_as_finite_decimal(resource[field], f"inner {field}") == expected, f"inner {field} drift")
    _require(resource["endpoint_qpc_tick"] == samples[-1]["qpc_tick"], "inner endpoint tick drift")
    _require(resource["lifetime_peak_upper_bytes"] == lifetime_peak, "inner lifetime peak drift")
    _require(resource["max_sampled_concurrent_working_set_bytes"] == sampled, "inner sampled RSS drift")
    _require(resource["qpc_frequency"] == meter["qpc_frequency"], "inner frequency drift")
    _require(resource["rss_gate_bytes"] == max(sampled, lifetime_peak), "inner RSS gate drift")
    _require(resource["rss_gate_bytes"] <= 2_147_483_648, "inner RSS cap failed")
    _require(resource["sample_count"] == len(samples), "inner sample count drift")
    _require(resource["s_process_creation_filetime"] == meter["s_process_creation_filetime"], "inner S creation drift")
    _require(resource["t0_qpc_tick"] == samples[0]["qpc_tick"], "inner t0 drift")
    _require(resource["terminal_child_exit_filetime"] == meter["terminal_child_exit_filetime"], "inner child exit drift")


def _validate_terminal_resource(
    witness: dict,
    invocation_index: int,
    identities: dict | None = None,
    *,
    production: bool = False,
) -> Decimal:
    if identities is None:
        identities = witness["process_identities"]
    inner, inner_gap, inner_offset = _validate_meter_stream(
        witness["inner_meter"],
        outer=False,
        invocation_index=invocation_index,
        expected_identities=identities,
        production=production,
    )
    outer, outer_gap, outer_offset = _validate_meter_stream(
        witness["outer_meter"],
        outer=True,
        invocation_index=invocation_index,
        expected_identities=identities,
        production=production,
    )
    _require(
        inner["qpc_clock_id"] == outer["qpc_clock_id"]
        and inner["qpc_frequency"] == outer["qpc_frequency"]
        and inner_offset == outer_offset,
        "inner/outer meter clock disagreement",
    )
    resource = _exact_key_set(witness["resource_meter"], _TERMINAL_RESOURCE_KEYS, "terminal resource meter")
    _require(resource["charged_process_roles"] == ["O", "S", "L", "W"], "charged role order drift")
    by_role = resource["cpu_100ns_by_role"]
    _require(isinstance(by_role, dict) and set(by_role) == {"O", "S", "L", "W"}, "CPU role census drift")
    terminal_rows = {
        "O": outer["samples"][-1]["roles"]["O"],
        "S": outer["samples"][-1]["roles"]["S"],
        "L": inner["samples"][-1]["roles"]["L"],
        "W": inner["samples"][-1]["roles"]["W"],
    }
    if production:
        samples_by_role = {
            "O": outer["samples"],
            "S": outer["samples"],
            "L": inner["samples"],
            "W": inner["samples"],
        }
        for role, terminal_row in terminal_rows.items():
            identity = identities[role]
            first_observation = next(
                sample
                for sample in samples_by_role[role]
                if sample["roles"][role]["state"] != "NOT_CREATED"
            )
            _require(
                identity["creation_filetime"]
                <= identity["handle_acquired_filetime"]
                <= first_observation["utc_filetime"],
                f"production process identity {role}: handle/meter chronology drift",
            )
            if role == "O":
                _require(
                    identity["kernel_time_100ns"]
                    >= terminal_row["kernel_time_100ns"]
                    and identity["user_time_100ns"]
                    >= terminal_row["user_time_100ns"],
                    "production O retained counters precede its final live sample",
                )
            else:
                _require(
                    identity["kernel_time_100ns"]
                    == terminal_row["kernel_time_100ns"]
                    and identity["user_time_100ns"]
                    == terminal_row["user_time_100ns"]
                    and identity["exit_code"] == terminal_row["exit_code"] == 0,
                    f"production process identity {role}: terminal meter drift",
                )
    expected_cpu: dict[str, int] = {}
    for role, row in terminal_rows.items():
        expected_cpu[role] = row["kernel_time_100ns"] + row["user_time_100ns"]
        _require(by_role[role] == expected_cpu[role], f"terminal CPU mismatch for {role}")
    cpu_seconds = Decimal(sum(expected_cpu.values())) / Decimal(10_000_000)
    _require(_as_finite_decimal(resource["cpu_seconds_sum"], "terminal CPU") == cpu_seconds, "terminal CPU reduction drift")
    _require(resource["inner_sample_count"] == len(inner["samples"]), "inner sample count drift")
    _require(resource["outer_sample_count"] == len(outer["samples"]), "outer sample count drift")
    _require(resource["o_process_creation_filetime"] == outer["o_process_creation_filetime"], "O creation time drift")
    _require(resource["terminal_endpoint_filetime"] == outer["terminal_endpoint_filetime"], "terminal endpoint drift")
    full_wall = Decimal(outer["terminal_endpoint_filetime"] - outer["o_process_creation_filetime"]) / Decimal(10_000_000)
    science_wall = Decimal(inner["scientific_stop_filetime"] - outer["o_process_creation_filetime"]) / Decimal(10_000_000)
    _require(_as_finite_decimal(resource["full_wall_seconds"], "full wall") == full_wall, "full wall reduction drift")
    _require(_as_finite_decimal(resource["scientific_stop_wall_seconds"], "science wall") == science_wall, "science wall reduction drift")
    _require(Decimal("0") <= full_wall <= Decimal("5400"), "full wall cap failed")
    _require(Decimal("0") <= science_wall <= Decimal("5100"), "scientific wall cap failed")
    maximum_gap = max(inner_gap, outer_gap)
    _require(
        _as_finite_decimal(resource["max_observed_sampling_gap_seconds"], "sampling gap")
        == maximum_gap,
        "sampling gap reduction drift",
    )
    _require(maximum_gap <= Decimal("0.100000000"), "sampling gap cap failed")
    peak_by_role = {
        "O": max(row["roles"]["O"]["peak_working_set_bytes"] for row in outer["samples"]),
        "S": max(
            [row["roles"]["S"]["peak_working_set_bytes"] for row in outer["samples"]]
            + [row["roles"]["S"]["peak_working_set_bytes"] for row in inner["samples"]]
        ),
        "L": max(row["roles"]["L"]["peak_working_set_bytes"] for row in inner["samples"]),
        "W": max(row["roles"]["W"]["peak_working_set_bytes"] for row in inner["samples"]),
    }
    lifetime_peak = sum(peak_by_role.values())
    _require(resource["lifetime_peak_upper_bytes"] == lifetime_peak, "lifetime peak reduction drift")
    frequency = inner["qpc_frequency"]
    merged_values: list[int] = []
    union_start = max(
        inner["samples"][0]["qpc_tick"],
        outer["samples"][0]["qpc_tick"],
    )
    union_end = min(
        inner["samples"][-1]["qpc_tick"],
        outer["samples"][-1]["qpc_tick"],
    )
    _require(union_start <= union_end, "meter streams have no common union interval")
    for tick in sorted({
        sample["qpc_tick"]
        for meter in (inner, outer)
        for sample in meter["samples"]
        if union_start <= sample["qpc_tick"] <= union_end
    }):
        inner_sample = _sample_at_or_before(inner["samples"], tick, frequency)
        outer_sample = _sample_at_or_before(outer["samples"], tick, frequency)
        inner_roles = inner_sample["roles"]
        outer_roles = outer_sample["roles"]
        merged_values.append(
            outer_roles["O"]["current_working_set_bytes"]
            + max(
                inner_roles["S"]["current_working_set_bytes"],
                outer_roles["S"]["current_working_set_bytes"],
            )
            + inner_roles["L"]["current_working_set_bytes"]
            + inner_roles["W"]["current_working_set_bytes"]
        )
    merged = max(merged_values)
    _require(resource["max_merged_concurrent_working_set_bytes"] == merged, "merged concurrent RSS drift")
    _require(resource["rss_gate_bytes"] == max(merged, lifetime_peak), "RSS gate reduction drift")
    _require(resource["rss_gate_bytes"] <= 2_147_483_648, "RSS cap failed")
    return cpu_seconds


def _validate_quad_audit(payload: object, context: str) -> None:
    _require(isinstance(payload, dict), f"{context}: quadrature audit required")
    _require(payload.get("all_calls_pass") is True, f"{context}: quadrature call failed")
    _require(
        payload.get("error_semantics")
        == "heuristic_diagnostic_estimate_not_interval_certificate",
        f"{context}: error semantics drift",
    )
    _require(payload.get("interval_certified") is False, f"{context}: false interval claim")
    count = payload.get("observed_call_count")
    _require(isinstance(count, int) and count > 0, f"{context}: missing quadrature calls")


def _validate_primary(payload: object, event_id: str, dps: int, fixture: dict) -> None:
    primary = _exact_keys(payload, _PRIMARY_KEYS, f"primary {event_id}/{dps}")
    _require(primary["artifact"] == "M245_PRIMARY_EVENT_PRECISION", "wrong primary artifact")
    _require(primary["schema"] == "m245-primary-event-v1", "wrong primary schema")
    _require(primary["event_id"] == event_id and primary["precision_dps"] == dps, "primary context drift")
    _require(primary["fixture_array_sha256"] == fixture, "primary fixture binding drift")
    _require(primary["degrees"] == list(range(9)), "primary degree census drift")
    _require(isinstance(primary["R"], list) and len(primary["R"]) == 9, "primary R census drift")
    _require(
        isinstance(primary["G"], list)
        and len(primary["G"]) == 9
        and all(isinstance(row, list) and len(row) == 9 for row in primary["G"]),
        "primary G census drift",
    )
    _require(len(primary["d"]) == 9 and len(primary["beta"]) == 9, "primary vector census drift")
    blocks = primary["leading_blocks"]
    _require(isinstance(blocks, list) and len(blocks) == 9, "primary leading blocks drift")
    for Q, block in enumerate(blocks):
        _require(isinstance(block, dict) and block.get("Q") == Q, "primary leading block order drift")
        _require(block.get("cholesky_pass") is True and block.get("solve_pass") is True, "primary linear gate failed")
        _require(isinstance(block.get("energy_gate"), dict) and block["energy_gate"].get("pass") is True, "primary energy gate failed")
        identity = block.get("ordinary_beta_identity")
        _require(isinstance(identity, dict) and identity.get("pass") is True, "primary beta identity failed")
        if Q in (0, 4, 8):
            _require(isinstance(block.get("direct_residual"), dict) and block["direct_residual"].get("pass") is True, "primary direct residual failed")
            _require(isinstance(block.get("direct_beta_residual"), dict) and block["direct_beta_residual"].get("pass") is True, "primary beta residual failed")
    checks = primary["analytic_direct_checks"]
    _require(isinstance(checks, dict) and checks.get("all_pass") is True, "primary analytic/direct gate failed")
    _require(len(checks.get("R", [])) == 9 and len(checks.get("G_upper", [])) == 45, "primary analytic census drift")
    _require(all(row.get("pass") is True for row in checks["R"] + checks["G_upper"]), "primary analytic comparison failed")
    _validate_quad_audit(primary["quadrature_audit"], f"primary {event_id}/{dps}")
    _validate_small_firewall(primary["firewall"], f"primary {event_id}/{dps}")


def _validate_replica(payload: object, event_id: str, dps: int, fixture: dict) -> None:
    replica = _exact_keys(payload, _REPLICA_KEYS, f"replica {event_id}/{dps}")
    _require(replica["artifact"] == "M245_REPLICA_EVENT_PRECISION", "wrong replica artifact")
    _require(replica["schema"] == "m245-replica-event-v1", "wrong replica schema")
    _require(replica["event_id"] == event_id and replica["precision_dps"] == dps, "replica context drift")
    _require(replica["fixture_array_sha256"] == fixture, "replica fixture binding drift")
    _require(isinstance(replica["fixed_b_nodes"], list) and len(replica["fixed_b_nodes"]) == 17, "replica node census drift")
    _require(isinstance(replica["b_rep_at_nodes"], list) and len(replica["b_rep_at_nodes"]) == 17, "replica value census drift")
    _validate_quad_audit(replica["quadrature_audit"], f"replica {event_id}/{dps}")
    _validate_small_firewall(replica["firewall"], f"replica {event_id}/{dps}")


def _validate_curve_report(
    payload: object,
    event_id: str,
    *,
    require_models: bool,
) -> dict:
    _require(isinstance(payload, dict), "curve report object required")
    expected_keys = {"labels", "models"} if require_models else None
    if expected_keys is None:
        _require(set(payload) in ({"labels"}, {"labels", "models"}), "curve report schema drift")
    else:
        _require(set(payload) == expected_keys, "production curve report schema drift")
    labels = payload["labels"]
    _require(isinstance(labels, dict) and set(labels) == set(FAMILIES), "curve label family drift")
    if event_id == "E00":
        _require(all(labels[family] == "ENDPOINT_CONTROL/NA" for family in FAMILIES), "E00 endpoint label drift")
    else:
        _require(
            all(labels[family] in {"FALSIFIED", "NOT_FALSIFIED_ON_Q0_8"} for family in FAMILIES),
            "invalid noncontrol curve label",
        )
    if "models" not in payload:
        return labels

    models = payload["models"]
    _require(isinstance(models, dict) and set(models) == set(FAMILIES), "curve model family drift")
    base_keys = {
        "event_id", "model", "fit_degrees", "holdout_degrees",
        "second_difference_indices", "only_future_bound", "label", "reason",
    }
    detail_keys = {
        "tau_T", "tau_x", "transformed_80", "transformed_100",
        "second_differences", "fit_intercept", "fit_slope",
        "holdout_predictions", "holdout_errors",
    }
    for family in FAMILIES:
        report = models[family]
        _require(isinstance(report, dict), f"curve model {family}: object required")
        reason = report.get("reason")
        detailed = reason in {
            "ALL_FINITE_LADDER_GATES_PASS",
            "CURVATURE_OR_HOLDOUT_MISS",
        }
        _require(
            set(report) == (base_keys | detail_keys if detailed else base_keys),
            f"curve model {family}: schema drift",
        )
        _require(
            report["event_id"] == event_id
            and report["model"] == family
            and report["fit_degrees"] == list(range(6))
            and report["holdout_degrees"] == [6, 7, 8]
            and report["second_difference_indices"] == list(range(1, 8))
            and report["only_future_bound"] == "0<=additional_explainable_energy_beyond_Q8<=K-P8",
            f"curve model {family}: scope drift",
        )
        _require(report["label"] == labels[family], f"curve model {family}: label drift")
        if event_id == "E00":
            _require(
                report["label"] == "ENDPOINT_CONTROL/NA"
                and reason == "DECLARED_TRANSFORMS_SINGULAR_AT_X1"
                and not detailed,
                f"curve model {family}: endpoint disposition drift",
            )
            continue
        if reason == "MODEL_DOMAIN_REFUSAL":
            _require(report["label"] == "FALSIFIED", f"curve model {family}: domain refusal label drift")
            continue
        _require(detailed, f"curve model {family}: invalid disposition")
        expected_label = (
            "NOT_FALSIFIED_ON_Q0_8"
            if reason == "ALL_FINITE_LADDER_GATES_PASS"
            else "FALSIFIED"
        )
        _require(report["label"] == expected_label, f"curve model {family}: disposition/label drift")
        for field, length in (
            ("transformed_80", 9),
            ("transformed_100", 9),
            ("second_differences", 7),
            ("holdout_predictions", 3),
            ("holdout_errors", 3),
        ):
            values = report[field]
            _require(isinstance(values, list) and len(values) == length, f"curve model {family}: {field} census drift")
            for index, value in enumerate(values):
                _as_finite_decimal(value, f"curve model {family}: {field}[{index}]")
        for field in ("tau_T", "tau_x", "fit_intercept", "fit_slope"):
            _as_finite_decimal(report[field], f"curve model {family}: {field}")
        _require(
            _as_finite_decimal(report["tau_T"], f"curve model {family}: tau_T") >= 0
            and _as_finite_decimal(report["tau_x"], f"curve model {family}: tau_x") >= 0
            and all(
                _as_finite_decimal(value, f"curve model {family}: holdout error") >= 0
                for value in report["holdout_errors"]
            ),
            f"curve model {family}: negative tolerance or error",
        )
    return labels


def _validate_event(
    payload: object,
    event_id: str,
    *,
    require_curve_models: bool = False,
) -> None:
    event = _exact_keys(payload, _EVENT_KEYS, f"event {event_id}")
    _require(event["event_id"] == event_id, "event order/id drift")
    fixture = event["fixture_array_sha256"]
    _require(
        isinstance(fixture, dict)
        and set(fixture) == {"C", "mu"}
        and all(_is_sha256(value) for value in fixture.values()),
        "invalid fixture hash binding",
    )
    for field, validator in (
        ("primary_by_precision", _validate_primary),
        ("replica_by_precision", _validate_replica),
    ):
        by_precision = event[field]
        _require(isinstance(by_precision, dict) and set(by_precision) == {"80", "100"}, f"{field} precision census drift")
        for dps in (80, 100):
            validator(by_precision[str(dps)], event_id, dps, fixture)
    for gate_name in (
        "cross_precision_gates", "primary_replica_gates",
        "analytic_solve_energy_beta_gates",
    ):
        gate = event[gate_name]
        _require(isinstance(gate, dict) and gate.get("pass") is True, f"{gate_name} failed")
    _validate_curve_report(
        event["curve_report"],
        event_id,
        require_models=require_curve_models,
    )
    refs = event["quad_gateway_ledger_refs"]
    _require(isinstance(refs, list) and len(refs) == 4, "quad ledger reference census drift")
    expected = (("primary", 80), ("primary", 100), ("replica", 80), ("replica", 100))
    for row, pair in zip(refs, expected):
        _require(isinstance(row, dict) and row.get("engine") == pair[0] and row.get("precision_dps") == pair[1], "quad ledger scope drift")
        _require(isinstance(row.get("count"), int) and row["count"] > 0 and _is_sha256(row.get("sha256")), "invalid quad ledger binding")
    _require(event["only_future_bound"] == "0<=additional_explainable_energy_beyond_Q8<=K-P8", "future bound drift")
    _require(event["gate_verdict"] == "PASS", "event gate failed")
    _validate_firewall(event["firewall"], f"event {event_id}")
    _require(event["forbidden_credit"] is True, "forbidden credit flag drift")


def _validate_final(
    payload: object,
    shard_id: int,
    *,
    require_curve_models: bool = False,
) -> dict:
    final = _exact_keys(payload, _FINAL_KEYS, f"final shard {shard_id}")
    _require(final["artifact"] == "M245_FINAL_SHARD_RECEIPT", "wrong final artifact")
    _require(final["schema"] == "m245-final-shard-receipt-v2", "wrong final schema")
    _require(final["shard_id"] == shard_id, "duplicate/wrong shard id")
    _require(final["events_in_order"] == list(ASSIGNMENTS[shard_id]), "event assignment/order drift")
    _require(final["status"] == "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS", "wrong provisional final status")
    _require(final["no_cross_shard_cache"] is True, "cross-shard cache forbidden")
    _validate_firewall(final["firewall"], f"final shard {shard_id}")
    authority = _validate_hash_map(final["authority_sha256"], f"final shard {shard_id}")
    _require(set(authority) == _AUTHORITY_REQUIRED_NAMES, "final authority filename census drift")
    events = final["event_results"]
    _require(isinstance(events, list) and len(events) == 2, "two lossless events required")
    for event, event_id in zip(events, ASSIGNMENTS[shard_id]):
        _validate_event(event, event_id, require_curve_models=require_curve_models)
    invocations = final["invocation_receipts"]
    _require(isinstance(invocations, list) and len(invocations) == 3, "invocation receipt census drift")
    for index, event_id in enumerate(ASSIGNMENTS[shard_id], 1):
        row = _exact_key_set(invocations[index - 1], _INVOCATION_RECEIPT_KEYS, f"inner receipt {shard_id}/{index}")
        _require(row["event_id"] == event_id and row["invocation_index"] == index, "inner receipt order drift")
        _require(row["status"] == "PROVISIONAL_INNER_RECEIPT_NO_INVOCATION_PASS" and _is_sha256(row["sha256"]), "invalid inner receipt binding")
        _require(
            Path(row["path"]).name
            == _expected_inner_name(shard_id, index, event_id, "provisional_receipt"),
            "inner receipt path drift",
        )
    first_invocation = _exact_key_set(invocations[2], _INVOCATION_RECEIPT_KEYS, "first terminal receipt binding")
    _require(
        first_invocation["event_id"] == ASSIGNMENTS[shard_id][0]
        and first_invocation["invocation_index"] == 1
        and first_invocation["status"] == "PASS_M245_INVOCATION_BOUND"
        and _is_sha256(first_invocation["sha256"])
        and Path(first_invocation["path"]).name
        == f"M245_S{shard_id}_I1_{ASSIGNMENTS[shard_id][0]}_TERMINAL_WITNESS_20260810.json",
        "first terminal witness binding missing",
    )
    resource = final["resource_union"]
    _require(
        isinstance(resource, dict)
        and set(resource) == {
            "invocation_one_terminal_witness",
            "invocation_two_inner_meter",
            "invocation_two_terminal_witness_required",
        },
        "resource union schema drift",
    )
    _require(resource["invocation_two_terminal_witness_required"] is True, "I2 terminal witness not required")
    first = _exact_key_set(resource["invocation_one_terminal_witness"], _EMBEDDED_WITNESS_KEYS, "embedded first witness")
    second = _exact_key_set(resource["invocation_two_inner_meter"], _INNER_METER_BINDING_KEYS, "embedded second meter")
    _validate_receipt_identity(first, "embedded first witness")
    _validate_receipt_identity(second, "embedded second meter")
    first_raw = _canonical_json_bytes(first["terminal_witness"])
    _require(first["bytes"] == len(first_raw) and first["sha256"] == _sha256(first_raw), "embedded first witness binding drift")
    _require(first["status"] == "PASS_M245_INVOCATION_BOUND", "embedded first witness status drift")
    _require(first_invocation["sha256"] == first["sha256"] and Path(first_invocation["path"]).name == Path(first["path"]).name, "first invocation/resource binding drift")
    meter_raw = _canonical_json_bytes(second["raw_meter"])
    _require(second["bytes"] == len(meter_raw) and second["sha256"] == _sha256(meter_raw), "embedded second meter binding drift")
    _validate_meter_stream(second["raw_meter"], outer=False, invocation_index=2)
    _validate_inner_resource(second["resource_meter"], second["raw_meter"])
    return authority


def _validate_production_identity_sources(authority: dict) -> None:
    authority_directory = Path(__file__).resolve().parent
    for source_name in (
        "launch_m245_scientific_invocation.py",
        "run_m245_scientific_shard.py",
        "m245_scientific_worker.py",
    ):
        _require(
            source_name in authority and _is_sha256(authority[source_name]),
            f"missing trigger-bound source hash: {source_name}",
        )
        source_raw, _source_identity = _regular_bytes(
            authority_directory / source_name
        )
        _require(
            _sha256(source_raw) == authority[source_name],
            f"trigger-bound source drift: {source_name}",
        )


def _validate_production_process_identity(
    row: object,
    role: str,
    shard_id: int,
    invocation_index: int,
) -> dict:
    identity = _exact_key_set(
        row,
        _PRODUCTION_PROCESS_IDENTITY_KEYS,
        f"production process identity {role}",
    )
    authority_directory = Path(__file__).resolve().parent
    launcher = str(
        (authority_directory / "launch_m245_scientific_invocation.py").resolve()
    )
    runner = str(
        (authority_directory / "run_m245_scientific_shard.py").resolve()
    )
    worker = str(
        (authority_directory / "m245_scientific_worker.py").resolve()
    )
    expected_argv = {
        "O": [
            STDLIB_PYTHON, "-I", "-B", "-S", "-u", launcher,
            "--shard-id", str(shard_id),
            "--invocation-index", str(invocation_index),
        ],
        "S": [
            STDLIB_PYTHON, "-I", "-B", "-S", "-u", runner,
            "--shard-id", str(shard_id),
            "--invocation-index", str(invocation_index),
        ],
        "L": [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker],
        "W": [worker],
    }[role]
    expected_image_path = VENV_PYTHON if role == "L" else STDLIB_PYTHON
    expected_image_sha256 = (
        VENV_PYTHON_SHA256 if role == "L" else STDLIB_PYTHON_SHA256
    )
    _require(
        all(_is_nonnegative_int(identity[field]) for field in (
            "creation_filetime", "exit_code", "handle_acquired_filetime",
            "kernel_time_100ns", "parent_pid", "pid", "user_time_100ns",
        )),
        f"production process identity {role}: invalid integer field",
    )
    _require(
        identity["creation_filetime"] > 0
        and identity["handle_acquired_filetime"] >= identity["creation_filetime"]
        and identity["parent_pid"] > 0
        and identity["pid"] > 0,
        f"production process identity {role}: invalid lifetime identity",
    )
    _require(
        identity["argv"] == expected_argv
        and identity["cwd"] == str(authority_directory)
        and _is_sha256(identity["environment_sha256"])
        and identity["exit_code"] == 0
        and identity["image_path"] == expected_image_path
        and identity["image_sha256"] == expected_image_sha256
        and identity["job_membership"] is (role in ("L", "W"))
        and identity["retained_handle_through_exit"] is True,
        f"production process identity {role}: metadata drift",
    )
    return identity


def _validate_witness(
    payload: object,
    shard_id: int,
    invocation_index: int,
    authority: dict,
    *,
    production: bool = False,
) -> Decimal:
    witness = _exact_keys(payload, _WITNESS_KEYS, f"witness {shard_id}/{invocation_index}")
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    _require(witness["artifact"] == "M245_OUTER_TERMINAL_INVOCATION_WITNESS", "wrong witness artifact")
    _require(witness["schema"] == "m245-outer-terminal-invocation-witness-v1", "wrong witness schema")
    _require((witness["shard_id"], witness["invocation_index"], witness["event_id"]) == (shard_id, invocation_index, event_id), "witness scope drift")
    _require(witness["authority_sha256"] == authority, "witness authority drift")
    expected_status = "PASS_M245_INVOCATION_BOUND" if invocation_index == 1 else "PASS_M245_SHARD_BOUND"
    _require(witness["status"] == expected_status, "witness status drift")
    _validate_firewall(witness["firewall"], f"witness {shard_id}/{invocation_index}")
    _validate_inner_artifacts(witness["inner_artifacts"], shard_id, invocation_index, event_id)
    identities = witness["process_identities"]
    _require(isinstance(identities, dict) and set(identities) == {"O", "S", "L", "W"}, "process identity census drift")
    if production:
        _validate_production_identity_sources(authority)
    for role, row in identities.items():
        if production:
            identity = _validate_production_process_identity(
                row,
                role,
                shard_id,
                invocation_index,
            )
        else:
            identity = _exact_key_set(
                row,
                _DUMMY_PROCESS_IDENTITY_KEYS,
                f"dummy process identity {role}",
            )
        _require(identity["retained_handle_through_exit"] is True, "unretained process identity")
        _require(
            _is_nonnegative_int(identity["creation_filetime"])
            and identity["creation_filetime"] > 0,
            "invalid process creation time",
        )
        _require(
            _is_nonnegative_int(identity["pid"])
            and identity["pid"] > 0
            and _is_sha256(identity["image_sha256"]),
            "invalid process identity",
        )
    _require(
        len({row["pid"] for row in identities.values()}) == 4
        and len({
            (row["pid"], row["creation_filetime"])
            for row in identities.values()
        }) == 4,
        "O/S/L/W process identities are not distinct",
    )
    if production:
        _require(
            identities["S"]["parent_pid"] == identities["O"]["pid"]
            and identities["L"]["parent_pid"] == identities["S"]["pid"]
            and identities["W"]["parent_pid"] == identities["L"]["pid"],
            "O/S/L/W retained parent chain drift",
        )
        _require(
            identities["L"]["environment_sha256"]
            == identities["W"]["environment_sha256"],
            "L/W frozen environment hash drift",
        )
    job = witness["job_census"]
    _exact_key_set(job, _JOB_CENSUS_KEYS, "job census")
    _require(
        all(_is_nonnegative_int(job[field]) for field in (
            "active_process_limit", "total_processes", "worker_children",
        )),
        "job census integer field drift",
    )
    _require(job["active_process_limit"] == 2 and job["total_processes"] == 2 and job["worker_children"] == 0, "job census failed")
    _require(job["distinct_job_pids"] == [identities["L"]["pid"], identities["W"]["pid"]], "job PID census drift")
    _require(job["job_roles"] == ["L", "W"], "job role census drift")
    if production:
        _require(
            [
                role for role in ("O", "S", "L", "W")
                if identities[role]["job_membership"]
            ]
            == job["job_roles"],
            "process identity/job membership cross-binding drift",
        )
    s_exit = _exact_key_set(witness["s_exit"], _S_EXIT_KEYS, "S exit")
    _require(s_exit["exit_code"] == 0 and s_exit["handle_retained_through_exit"] is True, "S exit failed")
    if production:
        _require(
            _is_nonnegative_int(s_exit["exit_code"])
            and s_exit["exit_code"] == identities["S"]["exit_code"],
            "S exit/process identity cross-binding drift",
        )
    _require(
        s_exit["identity"]
        == {"creation_filetime": identities["S"]["creation_filetime"], "pid": identities["S"]["pid"]},
        "S exit identity drift",
    )
    cpu = _validate_terminal_resource(
        witness,
        invocation_index,
        identities,
        production=production,
    )
    if invocation_index == 1:
        _require(witness["prior_invocation_files"] is None and witness["final_shard_receipt"] is None, "I1 future binding present")
    else:
        _require(isinstance(witness["prior_invocation_files"], list) and len(witness["prior_invocation_files"]) == 5, "I2 prior binding census drift")
        final_binding = _exact_key_set(witness["final_shard_receipt"], _FINAL_WITNESS_BINDING_KEYS, "I2 final binding")
        _validate_receipt_identity(final_binding, "I2 final binding")
    return cpu


def _load_authorized_inputs(
    authorization_path: Path,
    authorization_binding: dict,
    *,
    first_containing_proof: tuple[Path, str, str] | None = None,
    require_zero_paths_now: bool = True,
) -> tuple[dict, list[dict], list[dict], list[bytes]]:
    _validate_authorization(
        authorization_path,
        authorization_binding,
        require_zero_paths_now=require_zero_paths_now,
        first_containing_proof=first_containing_proof,
    )
    authorization, authorization_raw, authorization_identity = _canonical_payload(authorization_path)
    _require(_sha256(authorization_raw) == authorization_binding["sha256"], "authorization drift after validation")
    _require(
        (authorization_identity.st_dev, authorization_identity.st_ino)
        == (authorization_binding["device"], authorization_binding["inode"]),
        "authorization identity drift after validation",
    )
    finals: list[dict] = []
    final_raws: list[bytes] = []
    witnesses: list[dict] = []
    authority_map: dict | None = None
    production = _is_production_authorization_path(authorization_path)
    input_root = _authorized_input_root(authorization_path)
    for shard_id, row in enumerate(authorization["final_shard_receipts"]):
        path = Path(row["path"])
        expected_path = (input_root / FINAL_RECEIPT_NAMES[shard_id]).resolve()
        _require(path.resolve() == expected_path, "final receipt escapes exact shard namespace")
        raw = _check_file_binding(path, row, _FINAL_BINDING_KEYS, f"final binding {shard_id}")
        payload, canonical_raw, second_identity = _canonical_payload(path)
        _require(raw == canonical_raw, "final receipt drift across reads")
        _require(
            (second_identity.st_dev, second_identity.st_ino, second_identity.st_size)
            == (row["device"], row["inode"], row["bytes"]),
            "final receipt identity drift across reads",
        )
        observed_authority = _validate_final(
            payload,
            shard_id,
            require_curve_models=production,
        )
        if authority_map is None:
            authority_map = copy.deepcopy(observed_authority)
        else:
            _require(observed_authority == authority_map, "cross-shard authority hash drift")
        finals.append(payload)
        final_raws.append(raw)
    _require(authority_map is not None, "empty authority map")
    for ordinal, row in enumerate(authorization["terminal_witnesses"]):
        shard_id, invocation_index = divmod(ordinal, 2)[0], ordinal % 2 + 1
        path = Path(row["path"])
        expected_name = (
            f"M245_S{shard_id}_I{invocation_index}_"
            f"{ASSIGNMENTS[shard_id][invocation_index - 1]}_"
            "TERMINAL_WITNESS_20260810.json"
        )
        _require(
            path.resolve() == (input_root / expected_name).resolve(),
            "witness escapes exact shard namespace",
        )
        raw = _check_file_binding(path, row, _WITNESS_BINDING_KEYS, f"witness binding {shard_id}/{invocation_index}")
        payload, canonical_raw, second_identity = _canonical_payload(path)
        _require(raw == canonical_raw, "witness drift across reads")
        _require(
            (second_identity.st_dev, second_identity.st_ino, second_identity.st_size)
            == (row["device"], row["inode"], row["bytes"]),
            "witness identity drift across reads",
        )
        _validate_witness(
            payload,
            shard_id,
            invocation_index,
            authority_map,
            production=production,
        )
        if production:
            meter_artifact = payload["inner_artifacts"][2]
            meter_raw = _canonical_json_bytes(payload["inner_meter"])
            _require(
                meter_artifact["bytes"] == len(meter_raw)
                and meter_artifact["sha256"] == _sha256(meter_raw),
                f"I{invocation_index} witness inner meter/artifact byte binding drift",
            )
            expected_meter_path = (
                input_root
                / _expected_inner_name(
                    shard_id,
                    invocation_index,
                    ASSIGNMENTS[shard_id][invocation_index - 1],
                    "meter",
                )
            )
            _require(
                meter_artifact["path"] == str(expected_meter_path),
                f"I{invocation_index} witness inner meter artifact escapes exact shard namespace",
            )
        witnesses.append(payload)

    for shard_id, final in enumerate(finals):
        first = witnesses[2 * shard_id]
        second = witnesses[2 * shard_id + 1]
        embedded = final["resource_union"]["invocation_one_terminal_witness"]
        authorized_first = authorization["terminal_witnesses"][2 * shard_id]
        _require(embedded["terminal_witness"] == first, "first witness is not losslessly embedded")
        first_binding_fields = (
            ("bytes", "device", "inode", "path", "sha256", "status")
            if production else ("bytes", "sha256", "status")
        )
        if production:
            _require(
                Path(embedded["path"]).resolve() == Path(authorized_first["path"]).resolve(),
                "first witness exact path binding drift",
            )
        else:
            _require(Path(embedded["path"]).name == Path(authorized_first["path"]).name, "first witness path binding drift")
        for field in first_binding_fields:
            _require(
                (
                    Path(embedded[field]).resolve() == Path(authorized_first[field]).resolve()
                    if field == "path" else embedded.get(field) == authorized_first[field]
                ),
                f"first witness {field} binding drift",
            )
        prior = second["prior_invocation_files"]
        _require(prior[:4] == first["inner_artifacts"], "I2 does not losslessly bind I1 inner artifacts")
        prior_witness = _exact_key_set(prior[4], _PRIOR_WITNESS_KEYS, "I2 prior terminal witness")
        _validate_receipt_identity(prior_witness, "I2 prior terminal witness")
        _require(prior_witness["file_kind"] == "terminal_witness", "I2 prior witness kind drift")
        _require(prior_witness["event_id"] == first["event_id"] and prior_witness["invocation_index"] == 1, "I2 prior witness scope drift")
        for field in ("bytes", "device", "inode", "path", "sha256", "status"):
            _require(prior_witness[field] == embedded[field], f"I1/I2 {field} cross-binding drift")
        second_meter = final["resource_union"]["invocation_two_inner_meter"]
        _require(second_meter["raw_meter"] == second["inner_meter"], "I2 inner meter is not losslessly embedded")
        if production:
            first_receipt_artifact = first["inner_artifacts"][3]
            second_receipt_artifact = second["inner_artifacts"][3]
            for receipt_row, artifact in zip(
                final["invocation_receipts"][:2],
                (first_receipt_artifact, second_receipt_artifact),
            ):
                for field in ("event_id", "invocation_index", "sha256"):
                    _require(receipt_row[field] == artifact[field], f"provisional receipt {field} binding drift")
                _require(
                    Path(receipt_row["path"]).resolve() == Path(artifact["path"]).resolve(),
                    "provisional receipt exact path binding drift",
                )
            first_terminal_row = final["invocation_receipts"][2]
            _require(
                first_terminal_row["event_id"] == first["event_id"]
                and first_terminal_row["invocation_index"] == 1
                and first_terminal_row["sha256"] == authorized_first["sha256"]
                and first_terminal_row["status"] == authorized_first["status"]
                and Path(first_terminal_row["path"]).resolve()
                == Path(authorized_first["path"]).resolve(),
                "first terminal invocation row binding drift",
            )
            meter_artifact = second["inner_artifacts"][2]
            for field in ("bytes", "device", "inode", "sha256"):
                _require(second_meter[field] == meter_artifact[field], f"I2 meter {field} binding drift")
            _require(
                Path(second_meter["path"]).resolve() == Path(meter_artifact["path"]).resolve(),
                "I2 meter exact path binding drift",
            )
        final_binding = second["final_shard_receipt"]
        authorized_final = authorization["final_shard_receipts"][shard_id]
        _require(final_binding["bytes"] == len(final_raws[shard_id]), "I2 final byte binding drift")
        _require(final_binding["sha256"] == _sha256(final_raws[shard_id]), "I2 final hash binding drift")
        if production:
            for field in ("bytes", "device", "inode", "sha256", "status"):
                _require(final_binding[field] == authorized_final[field], f"I2 final {field} binding drift")
            _require(
                Path(final_binding["path"]).resolve() == Path(authorized_final["path"]).resolve(),
                "I2 final exact path binding drift",
            )
        else:
            _require(Path(final_binding["path"]).name == FINAL_RECEIPT_NAMES[shard_id], "I2 final path binding drift")
            _require(final_binding["status"] == final["status"], "I2 final status binding drift")

    reopened, reopened_raw, reopened_identity = _canonical_payload(authorization_path)
    _require(reopened == authorization and reopened_raw == authorization_raw, "authorization changed while inputs were open")
    _require(
        (reopened_identity.st_dev, reopened_identity.st_ino)
        == (authorization_binding["device"], authorization_binding["inode"]),
        "authorization identity changed while inputs were open",
    )
    return authorization, finals, witnesses, final_raws


def load_verified_shard_receipts(authorization_path, authorization_binding):
    _authorization, finals, _witnesses, _raws = _load_authorized_inputs(
        Path(authorization_path), authorization_binding
    )
    return copy.deepcopy(finals)


def _family_labels(events: list[dict]) -> dict:
    e00 = events[0]["curve_report"]["labels"]
    _require(all(e00[family] == "ENDPOINT_CONTROL/NA" for family in FAMILIES), "E00 is not the endpoint control")
    labels: dict[str, str] = {}
    for family in FAMILIES:
        labels[family] = (
            "NOT_FALSIFIED_ON_Q0_8"
            if all(event["curve_report"]["labels"][family] == "NOT_FALSIFIED_ON_Q0_8" for event in events[1:])
            else "FALSIFIED"
        )
    return labels


def _build_aggregate(
    authorization: dict,
    finals: list[dict],
    witnesses: list[dict],
    final_raws: list[bytes],
) -> dict:
    events = [copy.deepcopy(event) for final in finals for event in final["event_results"]]
    _require([event["event_id"] for event in events] == [f"E{index:02d}" for index in range(8)], "global event order drift")
    total_cpu = Decimal("0")
    for witness in witnesses:
        total_cpu += _validate_terminal_resource(witness, witness["invocation_index"])
    _require(total_cpu.is_finite() and total_cpu <= Decimal("43200"), "global shard CPU cap exceeded")
    total_cpu_json = float(total_cpu)
    _require(Decimal(str(total_cpu_json)) == total_cpu, "global CPU is not losslessly JSON-number representable")
    result = {
        "artifact": "M245_AGGREGATED_SPECTRUM",
        "schema": "m245-aggregated-spectrum-v1",
        "authority_sha256": copy.deepcopy(finals[0]["authority_sha256"]),
        "event_ids": [event["event_id"] for event in events],
        "events": events,
        "family_curve_labels": _family_labels(events),
        "shard_receipt_sha256": [_sha256(raw) for raw in final_raws],
        "global_shard_cpu_seconds": total_cpu_json,
        "firewall": {name: False for name in _FIREWALL_KEYS},
        "status": "PASSED_PRESERVED_GENERATED_SPECTRUM_PREMISE_ONLY",
    }
    validate_aggregate_result(result)
    _require(authorization["aggregate_source_sha256"] == finals[0]["authority_sha256"].get("aggregate_m245_spectrum.py"), "aggregate source authorization drift")
    return result


def aggregate_from_authorization(authorization_path, authorization_binding):
    authorization, finals, witnesses, final_raws = _load_authorized_inputs(
        Path(authorization_path), authorization_binding
    )
    return _build_aggregate(authorization, finals, witnesses, final_raws)


def validate_aggregate_result(result: dict) -> None:
    payload = _exact_keys(result, _RESULT_KEYS, "aggregate result")
    _require(payload["artifact"] == "M245_AGGREGATED_SPECTRUM", "wrong aggregate artifact")
    _require(payload["schema"] == "m245-aggregated-spectrum-v1", "wrong aggregate schema")
    _validate_hash_map(payload["authority_sha256"], "aggregate result")
    expected_ids = [f"E{index:02d}" for index in range(8)]
    _require(payload["event_ids"] == expected_ids, "aggregate event id order drift")
    _require(isinstance(payload["events"], list) and len(payload["events"]) == 8, "aggregate event census drift")
    for event, event_id in zip(payload["events"], expected_ids):
        _validate_event(event, event_id)
    _require(payload["family_curve_labels"] == _family_labels(payload["events"]), "aggregate family rule drift")
    hashes = payload["shard_receipt_sha256"]
    _require(isinstance(hashes, list) and len(hashes) == 4 and len(set(hashes)) == 4 and all(_is_sha256(value) for value in hashes), "aggregate shard hash census drift")
    try:
        cpu = Decimal(str(payload["global_shard_cpu_seconds"]))
    except (InvalidOperation, ValueError) as exc:
        raise M245AggregationContractError("invalid aggregate CPU") from exc
    _require(cpu.is_finite() and Decimal("0") <= cpu <= Decimal("43200"), "aggregate CPU cap failed")
    _validate_firewall(payload["firewall"], "aggregate result")
    _require(payload["status"] == "PASSED_PRESERVED_GENERATED_SPECTRUM_PREMISE_ONLY", "aggregate status drift")


def render_summary(result: dict) -> str:
    validate_aggregate_result(result)
    labels = result["family_curve_labels"]
    return (
        "M245 generated-spectrum premise only\n"
        f"events: {result['event_ids'][0]}..{result['event_ids'][-1]}\n"
        f"global shard CPU seconds: {result['global_shard_cpu_seconds']}\n"
        + "\n".join(f"{family}: {labels[family]}" for family in FAMILIES)
        + "\n"
    )


def publish_immutable_json(temp_path: str | os.PathLike[str], final_path: str | os.PathLike[str], payload: object) -> dict:
    temp = Path(temp_path)
    final = Path(final_path)
    _require(temp.parent.resolve() == final.parent.resolve(), "publication roots differ")
    _require(not os.path.lexists(temp) and not os.path.lexists(final), "publication namespace already consumed")
    raw = _canonical_json_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(temp, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise
    temp_payload, temp_raw, temp_identity = _canonical_payload(temp)
    _require(temp_raw == raw and temp_payload == payload, "temporary publication verification failed")
    os.link(temp, final)
    final_payload, final_raw, final_identity = _canonical_payload(final)
    _require(final_raw == raw and final_payload == payload, "final publication verification failed")
    same_identity = (
        temp_identity.st_dev == final_identity.st_dev
        and temp_identity.st_ino == final_identity.st_ino
    )
    _require(same_identity, "hard-link identity mismatch")
    temp.unlink()
    _require(not os.path.lexists(temp), "temporary publication residue")
    reopened, reopened_identity = _regular_bytes(final)
    _require(
        reopened == raw
        and (reopened_identity.st_dev, reopened_identity.st_ino, reopened_identity.st_size)
        == (final_identity.st_dev, final_identity.st_ino, final_identity.st_size),
        "post-unlink final verification failed",
    )
    return {
        "bytes": len(raw),
        "device": final_identity.st_dev,
        "inode": final_identity.st_ino,
        "path": str(final.resolve()),
        "sha256": _sha256(raw),
        "source_final_same_device_inode": True,
        "temporary_unlinked": True,
        "reopened_bytes_equal": True,
    }


def _validate_publication_receipt(
    publication: object,
    name: str,
    *,
    strict: bool,
    root: Path,
) -> dict | None:
    _require(isinstance(publication, dict), f"{name}: publication receipt missing")
    for flag in ("source_final_same_device_inode", "temporary_unlinked", "reopened_bytes_equal"):
        _require(publication.get(flag) is True, f"{name}: publication gate failed")
    _require(_is_sha256(publication.get("sha256")), f"{name}: invalid publication hash")
    if strict:
        _exact_key_set(publication, _PUBLICATION_KEYS, f"{name}: publication receipt")
        _validate_receipt_identity(publication, f"{name}: publication receipt")
        namespace_key = "intent" if name == "intent_publication" else "result"
        expected = root / _NAMESPACE[namespace_key]
        _require(Path(publication["path"]).resolve() == expected.resolve(), f"{name}: namespace drift")
        raw = _check_file_binding(expected, publication, _PUBLICATION_KEYS, name)
        payload, canonical_raw, identity = _canonical_payload(expected)
        _require(raw == canonical_raw, f"{name}: publication bytes drift across reads")
        _require(
            (identity.st_dev, identity.st_ino, identity.st_size)
            == (publication["device"], publication["inode"], publication["bytes"]),
            f"{name}: publication identity drift across reads",
        )
        if name == "intent_publication":
            _exact_key_set(
                payload,
                {"artifact", "authorization_binding", "no_retry", "status"},
                "aggregation intent",
            )
            _require(
                payload["artifact"] == "M245_AGGREGATION_INTENT"
                and payload["no_retry"] is True
                and payload["status"] == "AGGREGATION_INTENT_ONLY",
                "aggregation intent payload drift",
            )
        else:
            validate_aggregate_result(payload)
        return payload
    return None


def _validate_aggregation_receipt(
    receipt: dict,
    *,
    authorization: dict | None,
    verify_git_authority: bool,
    strict_publications: bool,
) -> None:
    payload = _exact_keys(receipt, _RECEIPT_KEYS, "aggregation receipt")
    _require(payload["artifact"] == "M245_AGGREGATION_RECEIPT", "wrong aggregation receipt artifact")
    _require(payload["schema"] == "m245-aggregation-receipt-v1", "wrong aggregation receipt schema")
    authorization_binding = payload["authorization_binding"]
    _exact_key_set(authorization_binding, _AUTH_BINDING_KEYS, "receipt authorization binding")
    verified_finals: list[dict] | None = None
    if verify_git_authority:
        authorization, verified_finals, _verified_witnesses, _verified_raws = _load_authorized_inputs(
            Path(authorization_binding["path"]),
            authorization_binding,
            require_zero_paths_now=False,
        )
    else:
        _require(authorization is not None, "verified authorization payload required")
    _require(payload["input_shard_receipts"] == authorization["final_shard_receipts"], "receipt final input binding drift")
    _require(payload["input_terminal_witnesses"] == authorization["terminal_witnesses"], "receipt witness input binding drift")
    _require(len({row["path"] for row in payload["input_shard_receipts"]}) == 4, "duplicate final input path")
    _require(len({row["sha256"] for row in payload["input_shard_receipts"]}) == 4, "duplicate final input hash")
    _require(len({row["path"] for row in payload["input_terminal_witnesses"]}) == 8, "duplicate witness path")
    _require(len({row["sha256"] for row in payload["input_terminal_witnesses"]}) == 8, "duplicate witness hash")
    root = Path(authorization_binding["path"]).resolve().parent
    publication_payloads: dict[str, dict | None] = {}
    for name in ("intent_publication", "output_publication"):
        publication_payloads[name] = _validate_publication_receipt(
            payload[name], name, strict=strict_publications, root=root
        )
    if strict_publications:
        intent = publication_payloads["intent_publication"]
        output = publication_payloads["output_publication"]
        _require(intent is not None and intent["authorization_binding"] == authorization_binding, "intent authorization binding drift")
        _require(output is not None, "aggregate output payload missing")
        _require(
            output["shard_receipt_sha256"]
            == [row["sha256"] for row in authorization["final_shard_receipts"]],
            "aggregate output/final receipt hash binding drift",
        )
        if verified_finals is not None:
            expected_events = [
                event for final in verified_finals for event in final["event_results"]
            ]
            _require(output["events"] == expected_events, "aggregate output is not a lossless event union")
    verification = payload["postpublication_verification"]
    _require(
        isinstance(verification, dict)
        and set(verification) == {
            "input_bytes_and_identities_unchanged",
            "output_bytes_and_identity_unchanged",
        }
        and verification.get("input_bytes_and_identities_unchanged") is True
        and verification.get("output_bytes_and_identity_unchanged") is True,
        "postpublication verification failed",
    )
    tree = _exact_key_set(payload["process_tree"], _PROCESS_TREE_KEYS, "process tree")
    _require(tree.get("aggregation_launch_slots") == 1, "aggregation launch-slot cap failed")
    _require(_is_nonnegative_int(tree.get("os_process_creations")) and tree["os_process_creations"] <= 3, "OS process creation cap failed")
    _require(_is_nonnegative_int(tree.get("inert_launcher_redirector_count")) and tree["inert_launcher_redirector_count"] <= 1, "launcher redirector cap failed")
    _require(tree.get("scientific_worker_count") == 1, "scientific worker census failed")
    _require(tree.get("scientific_worker_children") == 0, "scientific child prohibition failed")
    _require(payload["network"] is False and payload["no_scientific_imports"] is True, "aggregation firewall failed")
    wall = _as_finite_decimal(payload["wall_seconds"], "aggregation wall")
    _require(Decimal("0") <= wall <= Decimal("120"), "aggregation wall cap failed")
    _require(payload["status"] == "PASS", "aggregation receipt did not pass")


def validate_aggregation_receipt(receipt: dict) -> None:
    _require(isinstance(receipt, dict), "aggregation receipt object required")
    binding = receipt.get("authorization_binding")
    _require(isinstance(binding, dict) and isinstance(binding.get("path"), str), "receipt authorization path missing")
    production = _is_production_authorization_path(Path(binding["path"]))
    _validate_aggregation_receipt(
        receipt,
        authorization=None,
        verify_git_authority=True,
        # Frozen dummy tests deliberately use non-production, nonexistent
        # publication rows.  Only the exact authority-directory entry can
        # confer production PASS, and that path always performs live strict
        # publication verification.
        strict_publications=production,
    )


def _derive_authorization_binding_with_proof(
    path: Path,
) -> tuple[dict, tuple[Path, str, str]]:
    payload, raw, identity = _canonical_payload(path)
    root, relative = _repo_context(path)
    commits = _run_git(root, "log", "--diff-filter=A", "--format=%H", "--", relative).stdout.decode("utf-8").splitlines()
    _require(len(commits) == 1, "authorization lacks unique first-containing commit")
    binding = {
        "bytes": len(raw),
        "device": identity.st_dev,
        "inode": identity.st_ino,
        "path": str(path.resolve()),
        "repository_commit": commits[0],
        "sha256": _sha256(raw),
    }
    return binding, (root, relative, commits[0])


def _derive_authorization_binding(path: Path) -> dict:
    binding, _proof = _derive_authorization_binding_with_proof(path)
    return binding


def _verify_postpublication_state(
    authorization_path: Path,
    binding: dict,
    authorization: dict,
    finals: list[dict],
    witnesses: list[dict],
    output_publication: dict,
) -> None:
    raw = _check_file_binding(
        authorization_path,
        binding,
        _AUTH_BINDING_KEYS,
        "postpublication authorization",
    )
    _require(json.loads(raw.decode("utf-8")) == authorization, "postpublication authorization payload drift")
    for row, payload in zip(authorization["final_shard_receipts"], finals):
        observed = _check_file_binding(
            Path(row["path"]),
            row,
            _FINAL_BINDING_KEYS,
            "postpublication final receipt",
        )
        _require(observed == _canonical_json_bytes(payload), "postpublication final receipt drift")
    for row, payload in zip(authorization["terminal_witnesses"], witnesses):
        observed = _check_file_binding(
            Path(row["path"]),
            row,
            _WITNESS_BINDING_KEYS,
            "postpublication terminal witness",
        )
        _require(observed == _canonical_json_bytes(payload), "postpublication terminal witness drift")
    output = Path(output_publication["path"])
    output_raw, output_identity = _regular_bytes(output)
    _require(len(output_raw) == output_publication["bytes"], "postpublication output byte drift")
    _require(_sha256(output_raw) == output_publication["sha256"], "postpublication output hash drift")
    _require(
        (output_identity.st_dev, output_identity.st_ino)
        == (output_publication["device"], output_publication["inode"]),
        "postpublication output identity drift",
    )


def _validate_production_entry(authorization_path: Path, authorization: dict) -> None:
    _root, relative = _repo_context(authorization_path)
    expected_relative = (
        Path(AUTHORITY_DIRECTORY_REPO_RELATIVE) / _NAMESPACE["authorization"]
    ).as_posix()
    _require(relative == expected_relative, "production authorization namespace drift")
    _require(authorization_path.parent == Path(__file__).resolve().parent, "production authority directory drift")
    _require(Path.cwd().resolve() == Path(__file__).resolve().parent, "production cwd drift")
    expected_python = os.path.normcase(os.path.abspath(STDLIB_PYTHON))
    observed_python = os.path.normcase(os.path.abspath(sys.executable))
    _require(observed_python == expected_python, "production interpreter drift")
    _require(sys.flags.isolated == 1 and sys.flags.no_site == 1, "production isolation flags missing")
    _require(sys.dont_write_bytecode, "production -B flag missing")
    _require(
        _observed_windows_command_line_argv() == authorization["aggregate_argv"],
        "production OS command line is not the exact authorized argv",
    )
    source_path = Path(__file__).resolve()
    source_raw, _source_identity = _regular_bytes(source_path)
    _require(
        _sha256(source_raw) == authorization["aggregate_source_sha256"],
        "running aggregate source hash is not authorized",
    )


def main(argv: list[str] | None = None) -> int:
    main_entry_monotonic = time.monotonic()
    child_process_start = _GIT_PROCESS_CREATIONS
    child_observation_start = len(_OBSERVED_GIT_CHILDREN)
    parser = argparse.ArgumentParser(description="Aggregate immutable M245 shard receipts")
    parser.add_argument("--authorization", required=True)
    arguments = parser.parse_args(argv)
    authorization_path = Path(arguments.authorization).resolve()
    binding, first_containing_proof = _derive_authorization_binding_with_proof(
        authorization_path
    )
    authorization, finals, witnesses, final_raws = _load_authorized_inputs(
        authorization_path,
        binding,
        first_containing_proof=first_containing_proof,
    )
    _validate_production_entry(authorization_path, authorization)
    retained = _retain_authorized_inputs(
        authorization_path,
        binding,
        authorization,
        finals,
        witnesses,
    )
    retained_open = True
    root = authorization_path.parent
    try:
        intent_payload = {
            "artifact": "M245_AGGREGATION_INTENT",
            "authorization_binding": binding,
            "no_retry": True,
            "status": "AGGREGATION_INTENT_ONLY",
        }
        intent_publication = publish_immutable_json(
            root / _NAMESPACE["intent_temp"],
            root / _NAMESPACE["intent"],
            intent_payload,
        )
        result = _build_aggregate(authorization, finals, witnesses, final_raws)
        _verify_retained_inputs(retained)
        output_publication = publish_immutable_json(
            root / _NAMESPACE["result_temp"],
            root / _NAMESPACE["result"],
            result,
        )
        _verify_postpublication_state(
            authorization_path,
            binding,
            authorization,
            finals,
            witnesses,
            output_publication,
        )
        _verify_retained_inputs(retained)
        observed_git_children = _OBSERVED_GIT_CHILDREN[child_observation_start:]
        proof_root, proof_relative, _proof_commit = first_containing_proof
        expected_git_argv = [
            [
                "git", "-C", str(proof_root), "log", "--diff-filter=A",
                "--format=%H", "--", proof_relative,
            ],
            ["git", "-C", str(proof_root), "cat-file", "--batch"],
        ]
        _require(
            _GIT_PROCESS_CREATIONS - child_process_start == 2
            and len(observed_git_children) == 2
            and [row["argv"] for row in observed_git_children] == expected_git_argv
            and all(row["exit_code"] == 0 for row in observed_git_children)
            and len({
                (row["pid"], row["creation_filetime"])
                for row in observed_git_children
            }) == 2,
            "aggregation Git child process census drift",
        )
        observed_process_creations = 1 + len(observed_git_children)
        _require(
            observed_process_creations <= _CONTRACT["os_process_creations_max"],
            "aggregation OS process creation cap failed",
        )
        _close_retained_inputs(retained)
        retained_open = False
        receipt = {
            "artifact": "M245_AGGREGATION_RECEIPT",
            "schema": "m245-aggregation-receipt-v1",
            "authorization_binding": binding,
            "input_shard_receipts": copy.deepcopy(authorization["final_shard_receipts"]),
            "input_terminal_witnesses": copy.deepcopy(authorization["terminal_witnesses"]),
            "intent_publication": intent_publication,
            "output_publication": output_publication,
            "postpublication_verification": {
                "input_bytes_and_identities_unchanged": True,
                "output_bytes_and_identity_unchanged": True,
            },
            "process_tree": {
                "aggregation_launch_slots": 1,
                "os_process_creations": observed_process_creations,
                "inert_launcher_redirector_count": 0,
                "scientific_worker_children": 0,
                "scientific_worker_count": 1,
            },
            "network": False,
            "no_scientific_imports": True,
            # A zero placeholder permits complete receipt-structure and live
            # publication validation before the terminal wall observation.
            "wall_seconds": 0,
            "status": "PASS",
        }
        _validate_aggregation_receipt(
            receipt,
            authorization=authorization,
            verify_git_authority=False,
            strict_publications=True,
        )
        process_lifetime = _process_lifetime_seconds_at_terminal_boundary()
        main_lifetime = Decimal(str(time.monotonic() - main_entry_monotonic))
        measured_wall = max(process_lifetime, main_lifetime)
        _require(
            measured_wall <= Decimal(_CONTRACT["wall_seconds"]),
            "aggregation wall cap failed at terminal receipt boundary",
        )
        # Round upward by one microsecond so the JSON number cannot understate
        # the terminal observation through binary64 conversion.
        reported_wall = float(measured_wall + Decimal("0.000001"))
        _require(
            Decimal(str(reported_wall)) >= measured_wall
            and Decimal(str(reported_wall)) <= Decimal(_CONTRACT["wall_seconds"]),
            "aggregation wall report is not a conservative bounded value",
        )
        receipt["wall_seconds"] = reported_wall
        # This is the sole operation after the finite terminal boundary.  As
        # with Erratum2's terminal witness, an immutable receipt cannot bind
        # its own future publication; it contains no scientific work.
        publish_immutable_json(
            root / _NAMESPACE["receipt_temp"],
            root / _NAMESPACE["receipt"],
            receipt,
        )
    finally:
        if retained_open:
            _close_retained_inputs(retained)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except M245AggregationContractError as exc:
        sys.stderr.write(f"M245 aggregation refused: {exc}\n")
        raise SystemExit(2)
