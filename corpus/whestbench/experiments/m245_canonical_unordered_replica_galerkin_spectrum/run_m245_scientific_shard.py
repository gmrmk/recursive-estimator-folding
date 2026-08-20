"""Fail-closed, trigger-gated M245 shard supervisor and inner meter.

This stdlib-only S process burns the durable intent, creates the suspended
L/W Job topology, verifies W's framed science, and publishes the real inner
meter plus provisional receipt.  No scientific module is imported here.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import threading
import time
from typing import Any


HERE = Path(__file__).resolve().parent
SHARD_DIRECTORY_REPO_RELATIVE = "corpus/whestbench/experiments/m245_fable_spectrum_shards"
AUTHORITY_CWD = str(HERE)
STDLIB_PYTHON = r"C:\Python314\python.exe"
VENV_PYTHON = r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe"
GIT_EXE = r"C:\Program Files\Git\cmd\git.exe"
STDLIB_PYTHON_SHA256 = "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"
VENV_PYTHON_SHA256 = "4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262"
GIT_EXE_SHA256 = "37c5725818d602e951ba2563b870d62763322956b73373da4c33a0b566a80bc9"
_EXPECTED_OUTER_VALIDATOR_SHA256: str | None = None
# Set by the production dispatch only; when set, every validated receipt's
# authority union must equal the current trigger's exact authority+source
# union, not merely carry syntactically valid hashes.
_EXPECTED_PRODUCTION_AUTHORITY_UNION: dict[str, str] | None = None

ASSIGNMENTS = {
    0: ("E00", "E01"),
    1: ("E02", "E03"),
    2: ("E04", "E05"),
    3: ("E06", "E07"),
}

_SHARD_CONTRACT = {
    "assignments": ASSIGNMENTS,
    "owner": "codex_root",
    "directory_repo_relative": SHARD_DIRECTORY_REPO_RELATIVE,
    "process_topology": "outer_stdlib_observer_O_to_stdlib_supervisor_S_to_venv_redirector_L_to_one_scientific_worker_W",
    "charged_process_roles": ("O", "S", "L", "W"),
    "outer_observer_stdlib_only": True,
    "outer_observer_count_per_invocation": 1,
    "supervisor_stdlib_only": True,
    "launcher_role": "inert_hash_bound_venv_redirector",
    "scientific_worker_count_per_invocation": 1,
    "scientific_worker_children_per_invocation": 0,
    "inert_hash_bound_venv_launcher_redirector_count_per_invocation": 1,
    "complete_events_per_invocation": 1,
    "max_invocations_per_shard": 2,
    "max_launches_total": 8,
    "launch_slot_unit": "unique_durable_shard_invocation_attempt_external_S_launch",
    "successful_os_process_identities_per_attempt": ("O", "S", "L", "W"),
    "successful_complete_os_process_census": {"O": 8, "S": 8, "L": 8, "W": 8},
    "max_cpu_seconds_total": 43200,
    "wall_seconds_per_invocation": 5400,
    "scientific_soft_stop_seconds": 5100,
    "durable_publication_reserve_seconds": 300,
    "peak_rss_bytes_per_invocation": 2147483648,
    "blas_threads": 1,
    "network": False,
    "checkpoint_boundary": "after_complete_event_only_before_watchdog_cap",
    "watchdog_cap_is_failure": True,
    "retry": False,
    "reseed": False,
    "redraw": False,
    "cross_shard_cache": False,
    "third_invocation": False,
}

AUTHORITY_HASH_KEYS = (
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
)

FROZEN_AUTHORITY_SHA256 = {
    "M245_PREDECLARATION_20260810.md": "aa9ca84d48e840435d350fbab3be3f1c98356b541d54a018968cfa16b97f2512",
    "M245_FROZEN_MANIFEST_V1_20260810.json": "17a9df68304c7b06dd29957cc6fd4180242a9cc1bafb79e30c35f2426825b6b4",
    "M245_SHA256SUMS_V1_20260810.txt": "0fbc35bfa2e77993e19d50d03ebfdda8851b137cdde18e6ef6613172c8c565c9",
    "M245_PREMATERIALIZATION_ERRATUM1_20260810.md": "18f743c6bda98dc2c9c926db31ec93188a9670f1f2da3fcc761de14766e366b1",
    "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json": "b7aa2176b19571537e3313d8b2e4c8c1daad32b73fde42ce61b7522e4f3f1072",
    "M245_SHA256SUMS_V1_OVERLAY1_20260810.txt": "0dc4a2fe475a05db1db1f9cf9c15e13c66f95f16ae7b44b6fee1f0cb9592236a",
    "supervise_m245_fixture_materialization.py": "270a9f7d8ddd3fb5b68caec6f3d4352b70cf85491bc20771b4a3996f619bfd9b",
    "materialize_m245_fixtures.py": "e993b46f9cc9a2b580bee900f60ca5d3f1d29385e1694850fb9317d9b994163a",
    "test_m245_fixture_materialization_transport.py": "f3a0835eaddc55ab54726c1366a04148c238d3c9fc10388e3c8c976c5eb8c97f",
    "M245_FIXTURE_MATERIALIZATION_TDD_RECEIPT_20260810.md": "b5f473f7a2c983f50842a7f8d6912245a158761a4057d564359af1399f7b6c9b",
    "M245_FIXTURE_MATERIALIZATION_STATIC_VALIDATION_RECEIPT_20260810.json": "137722b7abdc58699e7c3759129f9b12c72793c711f80e45285a373a07196b88",
    "M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json": "742cb1ba7abf944714c55be55ee08007e3496c23a20f21fc44554df02d3a6167",
    "M245_FROZEN_MANIFEST_V2_20260810.json": "0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b",
    "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json": "4d9adc56a9f1a02a7fa1f066be3a6fd626b67a0656e5d86577271b4bb4a097fe",
    "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json": "15a69748afc5e7109f61ce41ccfe32d17b8af573caf2b5d8e99f5be80be17985",
    "M245_SHA256SUMS_V2_20260810.txt": "2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e",
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md": "5497b1397a62bbfb4f3be73a02f2b63872e01f2bd4795b77232e7c6c287beb85",
    "M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md": "8641de9ec301ba402b87e50dd8c5e3322a6532313f1d603c54356a4137e21587",
    "M245_SHA256SUMS_V2_OVERLAY2_20260810.txt": "401629468b5ec1f2eb5447b650b10f27fb47ba7ce3af74c740a230feeefcceaf",
}

# Activated append-only authorities that postdate the frozen trigger schema.
# The trigger payload census is frozen by the repaired tests, so these bind as
# module constants verified against live bytes and the GO commit blobs.
ACTIVATED_AUTHORITY_SHA256 = {
    "M245_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.md":
        "46ba45dcb35fa93fcbe17b399a67e61cb03cfe13b9f2bbca30807b65ca79ee75",
    "M245_SHA256SUMS_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.txt":
        "e0cd1409e45d2397f4a9dbbf849fa9e7e02dc9d76ea6540a0b1475d300f3b514",
    "M245_SCIENTIFIC_IMPLEMENTATION_ERRATUM1_20260810.md":
        "5d089084acb547b4161cf5bf3684033311dfdbc30d3dfdc9349399964923c2c3",
    "M245_SHA256SUMS_SCIENTIFIC_IMPLEMENTATION_ERRATUM1_20260810.txt":
        "7bd73b142e82a5c7d6172c005bf9d586524b854f9277417526dc09f832d4bbc2",
    "M245_SHA256SUMS_SCIENTIFIC_TDD_RED_V2_20260810.txt":
        "669df0111cbda4c0d7a2d4b694254e54ba9b85f69eaf3f6aefb5b16fa296893d",
}

FROZEN_SCIENTIFIC_TEST_SHA256 = {
    "test_m245_primary_core.py":
        "355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626",
    "test_m245_replica_core.py":
        "e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21",
    "test_m245_scientific_transport.py":
        "112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d",
    "test_m245_aggregation.py":
        "6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6",
}

GREEN_RECEIPT_NAME = "M245_SCIENTIFIC_TDD_GREEN_RECEIPT_20260810.md"
GREEN_CHECKSUM_NAME = "M245_SHA256SUMS_SCIENTIFIC_TDD_GREEN_20260810.txt"

# A static audit cannot bind its own hash or its sibling audit's hash; these
# three names are excluded from the audited-source map equality requirement.
STATIC_AUDIT_SELF_NAMES = (
    "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
    "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    "M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json",
)

SCIENTIFIC_SOURCE_HASH_KEYS = (
    "m245_primary_core.py",
    "m245_replica_core.py",
    "m245_scientific_worker.py",
    "run_m245_scientific_shard.py",
    "launch_m245_scientific_invocation.py",
    "aggregate_m245_spectrum.py",
    "test_m245_primary_core.py",
    "test_m245_replica_core.py",
    "test_m245_scientific_transport.py",
    "test_m245_aggregation.py",
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md",
    "M245_SCIENTIFIC_STATIC_AUDIT_CONTRACT_20260810.md",
    "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
    "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    "M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json",
)

QUAD_CALL_RECEIPT_KEYS = (
    "shard_id", "invocation_index", "event_id", "engine", "precision_dps",
    "cache_scope_id", "request_index", "completion_index", "parent_request_index",
    "nesting_depth", "quantity", "call_role", "panel_path", "interval_left",
    "interval_right", "method", "maxdegree", "error_api", "error_semantics",
    "interval_certified", "saved_mp_eps_mpf", "mp_quad_invoked",
    "cache_disposition", "returned_value_mpf", "returned_error_mpf",
    "value_finite", "error_finite", "error_le_saved_mp_eps_over_8",
    "exception_type", "exception_message_sha256", "pass",
)
MPF_TUPLE_KEYS = ("bitcount", "exponent", "mantissa", "sign")
ENDPOINT_KEYS = ("kind", "mpf")
QUAD_ROLES = (
    "outer_top_level", "nested_plackett", "nested_unary", "direct_analytic_gate",
    "direct_residual_gate", "direct_beta_residual_gate",
)
INVOCATION_RECEIPT_KEYS = (
    "artifact", "authority_sha256", "checkpoint_publication", "child_environment",
    "child_environment_sha256", "event_id", "firewall", "intent_publication",
    "invocation_index", "job_census", "meter_publication", "no_retry", "path_state",
    "prior_invocation_files", "process_identities", "quad_call_ledger",
    "quad_call_ledger_sha256", "quad_gateway", "resource_meter", "result_publication",
    "schema", "shard_id", "status", "stderr_empty", "stdout_records",
)
RESOURCE_METER_KEYS = (
    "charged_process_roles", "cpu_100ns_by_role", "cpu_seconds_sum",
    "endpoint_qpc_tick", "full_wall_seconds", "lifetime_peak_upper_bytes",
    "max_observed_sampling_gap_seconds", "max_sampled_concurrent_working_set_bytes",
    "qpc_frequency", "rss_gate_bytes", "sample_count", "s_process_creation_filetime",
    "scientific_stop_qpc_tick", "scientific_stop_wall_seconds", "t0_qpc_tick",
    "terminal_child_exit_filetime",
)
EVENT_RESULT_KEYS = (
    "event_id", "fixture_array_sha256", "primary_by_precision", "replica_by_precision",
    "cross_precision_gates", "primary_replica_gates", "analytic_solve_energy_beta_gates",
    "curve_report", "quad_gateway_ledger_refs", "only_future_bound", "gate_verdict",
    "firewall", "forbidden_credit",
)
PRIMARY_EVENT_KEYS = (
    "artifact", "schema", "event_id", "precision_dps", "fixture_array_sha256",
    "degrees", "R", "G", "mu_rb", "K", "d", "beta", "leading_blocks",
    "analytic_direct_checks", "quadrature_audit", "firewall",
)
REPLICA_EVENT_KEYS = (
    "artifact", "schema", "event_id", "precision_dps", "fixture_array_sha256",
    "fixed_b_nodes", "b_rep_at_nodes", "mu_rep", "M_same", "M_cross", "K_rep",
    "quadrature_audit", "firewall",
)
FIREWALL_KEYS = (
    "challenge_network_or_weights", "champion_output", "credentials", "hidden_compute",
    "leaderboard", "m125_response", "m151_source_arrays", "m178_code_or_credit",
    "m196_state", "m243_input_or_import", "network_service", "retry_or_clipping",
    "scorer", "sealed_cells", "submission", "truth",
)


class M245ShardContractError(Exception):
    """A frozen M245 shard transport invariant was violated."""


def _fail(message: str) -> None:
    raise M245ShardContractError(message)


def _exact_keys(value: Any, keys: tuple[str, ...], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(keys) or len(value) != len(keys):
        _fail(f"{label} has a malformed or lossy schema")
    return value


def _canonical_json_bytes(payload: object) -> bytes:
    try:
        encoded = json.dumps(
            payload, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True
        ) + "\n"
    except (TypeError, ValueError) as exc:
        _fail(f"payload is not canonical JSON: {exc}")
    return encoded.encode("utf-8")


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _valid_hash(value: Any, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and value != "0" * length
        and all(character in "0123456789abcdef" for character in value)
    )


def _finite_number_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _finite_scientific_scalar(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _direct_check_close(observed: Any, reference: Any) -> bool:
    if not _finite_number_string(observed) or not _finite_number_string(reference):
        return False
    observed_float = float(observed)
    reference_float = float(reference)
    return abs(observed_float - reference_float) <= 2.0e-11 * max(
        1.0, abs(reference_float)
    )


def shard_contract() -> dict[str, Any]:
    """Return a fresh copy of the exact frozen shard contract."""

    return {
        key: (
            dict(value) if isinstance(value, dict)
            else tuple(value) if isinstance(value, tuple)
            else value
        )
        for key, value in _SHARD_CONTRACT.items()
    }


def shard_namespace(shard_id: int, invocation_index: int) -> dict[str, str]:
    if type(shard_id) is not int or shard_id not in ASSIGNMENTS:
        _fail("shard_id is outside the four-shard census")
    if type(invocation_index) is not int or invocation_index not in (1, 2):
        _fail("invocation_index must be one or two")
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    stem = f"M245_S{shard_id}_I{invocation_index}_{event_id}"
    return {
        "directory_repo_relative": SHARD_DIRECTORY_REPO_RELATIVE,
        "intent_temp": f".{stem}_INTENT_20260810.json.tmp",
        "intent": f"{stem}_INTENT_20260810.json",
        "result_temp": f".{stem}_RESULT_20260810.json.tmp",
        "result": f"{stem}_RESULT_20260810.json",
        "checkpoint_temp": f".{stem}_CHECKPOINT_20260810.json.tmp",
        "checkpoint": f"{stem}_CHECKPOINT_20260810.json",
        "meter_temp": f".{stem}_METER_20260810.json.tmp",
        "meter": f"{stem}_METER_20260810.json",
        "invocation_receipt_temp": f".{stem}_RECEIPT_20260810.json.tmp",
        "invocation_receipt": f"{stem}_RECEIPT_20260810.json",
        "terminal_witness_temp": f".{stem}_TERMINAL_WITNESS_20260810.json.tmp",
        "terminal_witness": f"{stem}_TERMINAL_WITNESS_20260810.json",
        "final_shard_receipt_temp": f"M245_S{shard_id}_FINAL_RECEIPT_20260810.json.tmp",
        "final_shard_receipt": f"M245_S{shard_id}_FINAL_RECEIPT_20260810.json",
    }


def validate_shard_request(
    shard_id: int,
    events: Any,
    invocation_index: int,
    prior_complete: bool,
) -> None:
    if type(shard_id) is not int or shard_id not in ASSIGNMENTS:
        _fail("unknown shard")
    if not isinstance(events, (tuple, list)) or tuple(events) != ASSIGNMENTS[shard_id]:
        _fail("event assignment is not exact and ordered")
    if type(invocation_index) is not int or invocation_index not in (1, 2):
        _fail("only two invocations are authorized")
    if type(prior_complete) is not bool:
        _fail("prior_complete must be a Boolean")
    if prior_complete != (invocation_index == 2):
        _fail("invocation order is not down-closed")


def _ordered_intent_paths() -> list[str]:
    return [
        shard_namespace(shard_id, invocation_index)["intent"]
        for shard_id in ASSIGNMENTS
        for invocation_index in (1, 2)
    ]


def _expected_process_argv_contract(source_hashes: dict[str, str]) -> dict[str, Any]:
    runner_path = str((HERE / "run_m245_scientific_shard.py").resolve())
    launcher_path = str((HERE / "launch_m245_scientific_invocation.py").resolve())
    worker_path = str((HERE / "m245_scientific_worker.py").resolve())
    attempts = [(s, i) for s in ASSIGNMENTS for i in (1, 2)]
    return {
        "L": {
            "argv": [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker_path],
            "cwd": AUTHORITY_CWD,
            "image_sha256": VENV_PYTHON_SHA256,
            "source_sha256": source_hashes["m245_scientific_worker.py"],
        },
        "O_by_attempt": [
            {
                "argv": [STDLIB_PYTHON, "-I", "-B", "-S", "-u", launcher_path,
                         "--shard-id", str(s), "--invocation-index", str(i)],
                "cwd": AUTHORITY_CWD,
                "event_id": ASSIGNMENTS[s][i - 1],
                "invocation_index": i,
                "shard_id": s,
            }
            for s, i in attempts
        ],
        "O_image_sha256": STDLIB_PYTHON_SHA256,
        "O_source_sha256": source_hashes["launch_m245_scientific_invocation.py"],
        "S_by_attempt": [
            {
                "argv": [STDLIB_PYTHON, "-I", "-B", "-S", "-u", runner_path,
                         "--shard-id", str(s), "--invocation-index", str(i)],
                "cwd": AUTHORITY_CWD,
                "event_id": ASSIGNMENTS[s][i - 1],
                "invocation_index": i,
                "shard_id": s,
            }
            for s, i in attempts
        ],
        "S_image_sha256": STDLIB_PYTHON_SHA256,
        "S_source_sha256": source_hashes["run_m245_scientific_shard.py"],
        "W": {
            "cwd": AUTHORITY_CWD,
            "image_sha256": STDLIB_PYTHON_SHA256,
            "source_sha256": source_hashes["m245_scientific_worker.py"],
            "sys_argv": [worker_path],
            "sys_executable": VENV_PYTHON,
        },
        "process_tree": "O->S->L->W",
    }


def _git_bytes(*arguments: str, check: bool = True) -> bytes:
    git_raw, git_identity = _secure_regular_bytes(Path(GIT_EXE), "absolute Git executable")
    if git_identity.st_size != 46464 or _sha256_bytes(git_raw) != GIT_EXE_SHA256:
        _fail("absolute Git executable identity/hash drift")
    completed = subprocess.run(
        [GIT_EXE, "--no-pager", *arguments],
        cwd=HERE,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
    )
    if check and completed.returncode != 0:
        _fail(
            "Git verification failed: "
            + completed.stderr.decode("utf-8", errors="replace").strip()
        )
    return completed.stdout


def _repository_root() -> Path:
    raw = _git_bytes("rev-parse", "--show-toplevel")
    try:
        root = Path(raw.decode("utf-8").strip()).resolve(strict=True)
    except (UnicodeError, OSError) as exc:
        _fail(f"cannot resolve Git repository root: {exc}")
    if HERE != root and root not in HERE.parents:
        _fail("authority directory is outside its Git repository")
    return root


def _repo_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        _fail("bound path escapes the repository")


def _secure_regular_bytes(path: Path, label: str) -> tuple[bytes, os.stat_result]:
    try:
        before = os.lstat(path)
    except OSError as exc:
        _fail(f"cannot lstat {label}: {exc}")
    attributes = getattr(before, "st_file_attributes", 0)
    if not stat.S_ISREG(before.st_mode) or attributes & 0x400:
        _fail(f"{label} is not a regular non-reparse file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        _fail(f"cannot open {label} without following reparses: {exc}")
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            _fail(f"{label} identity changed between lstat and open")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    try:
        after = os.lstat(path)
    except OSError as exc:
        _fail(f"cannot re-lstat {label}: {exc}")
    if (
        (after.st_dev, after.st_ino, after.st_size)
        != (before.st_dev, before.st_ino, before.st_size)
        or getattr(after, "st_mtime_ns", None) != getattr(before, "st_mtime_ns", None)
    ):
        _fail(f"{label} changed during retained-handle read")
    raw = b"".join(chunks)
    if len(raw) != before.st_size:
        _fail(f"{label} short read")
    return raw, opened


def _git_blob(commit: str, repository_path: str) -> bytes:
    if not _valid_hash(commit, 40) or not repository_path or repository_path.startswith("/"):
        _fail("malformed Git commit/blob request")
    return _git_bytes("show", f"{commit}:{repository_path}")


def _commit_is_ancestor(commit: str) -> None:
    _git_bytes("cat-file", "-e", f"{commit}^{{commit}}")
    completed = subprocess.run(
        [GIT_EXE, "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=HERE,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        _fail("bound Git commit is not an ancestor of HEAD")


def _require_commit_ancestry(older: str, newer: str, label: str) -> None:
    if not _valid_hash(older, 40) or not _valid_hash(newer, 40):
        _fail(f"{label} contains a malformed commit")
    completed = subprocess.run(
        [GIT_EXE, "merge-base", "--is-ancestor", older, newer],
        cwd=HERE,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        _fail(f"{label} is not ancestry ordered")


def _first_commit_with_exact_blob(repository_path: str, expected_raw: bytes) -> str:
    history = _git_bytes(
        "log", "--all", "--reverse", "--format=%H", "--", repository_path
    ).decode("ascii", errors="strict").splitlines()
    for commit in history:
        completed = subprocess.run(
            [GIT_EXE, "--no-pager", "show", f"{commit}:{repository_path}"],
            cwd=HERE,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout == expected_raw:
            return commit
    _fail(f"no Git commit contains the exact blob {repository_path}")


def _markdown_entries(raw: bytes) -> list[bytes]:
    starts = [match.start() for match in re.finditer(br"(?m)^## \[", raw)]
    return [raw[start : (starts[index + 1] if index + 1 < len(starts) else len(raw))]
            for index, start in enumerate(starts)]


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
    if not isinstance(command_line, str) or not command_line:
        _fail("missing OS command line")
    count = ctypes.c_int()
    pointer = shell32.CommandLineToArgvW(command_line, ctypes.byref(count))
    if not bool(pointer) or count.value <= 0:
        _fail("cannot parse OS command line")
    try:
        return [pointer[index] for index in range(count.value)]
    finally:
        kernel32.LocalFree(ctypes.cast(pointer, ctypes.c_void_p))


def _require_exact_supervisor_process_binding(
    expected_argv: list[str], label: str
) -> None:
    """Bind the actual OS command line, interpreter, flags, and cwd."""

    if _observed_windows_command_line_argv() != expected_argv:
        _fail(f"{label} OS command line is not the exact declared argv")
    if list(getattr(sys, "orig_argv", ())) != expected_argv:
        _fail(f"{label} interpreter argv drift")
    if os.path.normcase(os.path.abspath(sys.executable)) != os.path.normcase(
        os.path.abspath(STDLIB_PYTHON)
    ):
        _fail(f"{label} interpreter drift")
    if sys.flags.isolated != 1 or sys.flags.no_site != 1 or not sys.dont_write_bytecode:
        _fail(f"{label} interpreter isolation flags missing")
    if Path.cwd().resolve() != HERE:
        _fail(f"{label} cwd drift")


def _parse_sha256sums(raw: bytes, label: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    try:
        text = raw.decode("ascii")
    except UnicodeError as exc:
        _fail(f"{label} is not ASCII: {exc}")
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (\S.*)", line)
        if match is None:
            _fail(f"{label} contains a malformed checksum line")
        digest, name = match.group(1), match.group(2)
        if name in entries:
            _fail(f"{label} lists {name} twice")
        entries[name] = digest
    if not entries:
        _fail(f"{label} is empty")
    return entries


def _verify_activated_authority_and_green_lineage(
    trigger: dict[str, Any],
    *,
    trigger_commit: str,
    root: Path,
) -> None:
    """Bind implementation authorization, erratum1, RED-V2 checksum, and GREEN evidence."""

    for name, expected_hash in ACTIVATED_AUTHORITY_SHA256.items():
        raw, _identity = _secure_regular_bytes(HERE / name, f"activated authority {name}")
        if _sha256_bytes(raw) != expected_hash:
            _fail(f"activated authority hash drift: {name}")
        repository_path = _repo_relative(HERE / name, root)
        if _sha256_bytes(_git_blob(trigger_commit, repository_path)) != expected_hash:
            _fail(f"GO commit does not contain the activated authority blob: {name}")
    sources = trigger["scientific_source_sha256"]
    for name, expected_hash in FROZEN_SCIENTIFIC_TEST_SHA256.items():
        if sources[name] != expected_hash:
            _fail(f"trigger test hash is not the frozen repaired-RED authority: {name}")
    receipt_raw, _receipt_identity = _secure_regular_bytes(
        HERE / GREEN_RECEIPT_NAME, "GREEN receipt"
    )
    checksum_raw, _checksum_identity = _secure_regular_bytes(
        HERE / GREEN_CHECKSUM_NAME, "GREEN checksum"
    )
    for name, raw in ((GREEN_RECEIPT_NAME, receipt_raw), (GREEN_CHECKSUM_NAME, checksum_raw)):
        repository_path = _repo_relative(HERE / name, root)
        if _git_blob(trigger_commit, repository_path) != raw:
            _fail(f"GO commit does not contain the exact GREEN evidence blob: {name}")
    listed = _parse_sha256sums(checksum_raw, "GREEN checksum")
    if GREEN_CHECKSUM_NAME in listed:
        _fail("GREEN checksum illegally lists itself")
    if listed.get(GREEN_RECEIPT_NAME) != _sha256_bytes(receipt_raw):
        _fail("GREEN checksum does not bind the live GREEN receipt bytes")
    for name in (
        "m245_primary_core.py", "m245_replica_core.py", "m245_scientific_worker.py",
        "run_m245_scientific_shard.py", "launch_m245_scientific_invocation.py",
        "aggregate_m245_spectrum.py",
    ):
        if listed.get(name) != sources[name]:
            _fail(f"GREEN checksum source lineage drift: {name}")
    for name, expected_hash in FROZEN_SCIENTIFIC_TEST_SHA256.items():
        if listed.get(name) != expected_hash:
            _fail(f"GREEN checksum test lineage drift: {name}")


def verify_committed_trigger(
    payload: Any,
    *,
    trigger_entry_bytes: bytes,
    trigger_commit: str | None = None,
) -> dict[str, Any]:
    """Bind a GO entry to a prior authorization entry and immutable Git blobs."""

    trigger = validate_trigger_payload(payload)
    root = _repository_root()
    channel = trigger["agent_channel_binding"]
    authorization_commit = channel["commit_sha"]
    _commit_is_ancestor(authorization_commit)
    channel_path = root / channel["path"]
    repository_channel_path = _repo_relative(channel_path, root)
    authorization_blob = _git_blob(authorization_commit, repository_channel_path)
    authorization_matches = [
        entry for entry in _markdown_entries(authorization_blob)
        if _sha256_bytes(entry) == channel["entry_sha256"]
    ]
    if len(authorization_matches) != 1:
        _fail("prior authorization entry is not unique in its committed channel blob")
    if not trigger_entry_bytes or b"M245 SHARD GO" not in trigger_entry_bytes.splitlines()[0].upper():
        _fail("actual trigger entry is not the exact M245 SHARD GO entry")
    if trigger not in _json_objects_in_channel_entry(trigger_entry_bytes):
        _fail("actual GO entry does not contain the validated trigger payload")
    history = _git_bytes(
        "rev-list", "--reverse", "HEAD", "--", repository_channel_path
    ).decode("ascii", errors="strict").splitlines()
    first_entry_commit: str | None = None
    for candidate in history:
        try:
            candidate_blob = _git_blob(candidate, repository_channel_path)
        except M245ShardContractError:
            continue
        if trigger_entry_bytes in _markdown_entries(candidate_blob):
            first_entry_commit = candidate
            break
    if first_entry_commit is None:
        _fail("actual GO entry is absent from committed channel history")
    if trigger_commit is not None and trigger_commit != first_entry_commit:
        _fail("supplied GO commit is not first-containing")
    trigger_commit = first_entry_commit
    _require_commit_ancestry(
        authorization_commit, trigger_commit, "authorization-to-GO lineage"
    )
    _commit_is_ancestor(trigger_commit)
    all_hashes = dict(trigger["authority_sha256"])
    all_hashes.update(trigger["scientific_source_sha256"])
    for name, expected_hash in all_hashes.items():
        path = HERE / name
        raw, _identity = _secure_regular_bytes(path, f"trigger-bound source {name}")
        if _sha256_bytes(raw) != expected_hash:
            _fail(f"live trigger-bound source hash drift: {name}")
        repository_path = _repo_relative(path, root)
        if _sha256_bytes(_git_blob(trigger_commit, repository_path)) != expected_hash:
            _fail(f"GO commit does not contain the exact source blob: {name}")

    for audit_binding in trigger["independent_static_audits"]:
        audit_path = HERE / audit_binding["receipt_path"]
        audit_raw, _audit_identity = _secure_regular_bytes(
            audit_path, f"static audit {audit_binding['reviewer_id']}"
        )
        try:
            audit_payload = json.loads(audit_raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            _fail(f"static audit is not JSON: {exc}")
        if audit_raw != _canonical_json_bytes(audit_payload):
            _fail("static audit receipt is not canonical JSON")
        if (
            not isinstance(audit_payload, dict)
            or audit_payload.get("reviewer_id") != audit_binding["reviewer_id"]
            or audit_payload.get("status") != audit_binding["status"]
            or audit_binding["status"] != "PASS_STATIC_M245_SCIENTIFIC_BUNDLE_ONLY"
            or len(audit_raw) == 0
            or _sha256_bytes(audit_raw) != audit_binding["sha256"]
        ):
            _fail("static audit content/status/reviewer binding drift")
        audit_row = _exact_keys(
            audit_payload,
            ("artifact", "audited_source_sha256", "reviewer_id", "schema", "status"),
            "static audit payload",
        )
        expected_audited = {
            name: trigger["scientific_source_sha256"][name]
            for name in SCIENTIFIC_SOURCE_HASH_KEYS
            if name not in STATIC_AUDIT_SELF_NAMES
        }
        if (
            audit_row["artifact"] != "M245_SCIENTIFIC_STATIC_AUDIT"
            or audit_row["schema"] != "m245-scientific-static-audit-v1"
            or audit_row["audited_source_sha256"] != expected_audited
        ):
            _fail("static audit payload is not the complete exact trigger-bound source map")

    census = trigger["zero_intent_census"]
    census_path = HERE / census["path"]
    census_raw, _census_identity = _secure_regular_bytes(census_path, "zero-intent census")
    if len(census_raw) != census["bytes"] or _sha256_bytes(census_raw) != census["sha256"]:
        _fail("zero-intent census live byte binding drift")
    census_commit = census["repository_commit"]
    _commit_is_ancestor(census_commit)
    repository_census_path = _repo_relative(census_path, root)
    if _git_blob(census_commit, repository_census_path) != census_raw:
        _fail("zero-intent census commit/blob mismatch")
    if _first_commit_with_exact_blob(repository_census_path, census_raw) != census_commit:
        _fail("zero-intent census commit is not first-containing")
    try:
        census_payload = json.loads(census_raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"zero-intent census is not JSON: {exc}")
    if census_raw != _canonical_json_bytes(census_payload):
        _fail("zero-intent census is not canonical JSON")
    census_row = _exact_keys(
        census_payload,
        ("artifact", "argv", "cwd", "observer_identity", "observations",
         "observed_present_count", "ordered_intent_paths", "repository_parent_head",
         "resolved_shard_directory", "runner_source_sha256", "schema", "utc_interval"),
        "zero-intent census payload",
    )
    expected_observations = [
        {"lstat": "ABSENT", "path": path} for path in _ordered_intent_paths()
    ]
    interval = _exact_keys(census_row["utc_interval"], ("end", "start"), "census UTC interval")
    try:
        start = datetime.fromisoformat(interval["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(interval["end"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        _fail(f"census UTC interval is malformed: {exc}")
    if (
        census_row["artifact"] != "M245_PRETRIGGER_ZERO_INTENT_CENSUS"
        or census_row["schema"] != "m245-pretrigger-zero-intent-census-v1"
        or census_row["argv"] != census["argv"]
        or census_row["cwd"] != census["cwd"]
        or not isinstance(census_row["observer_identity"], str)
        or re.fullmatch(r"pid=[1-9][0-9]*", census_row["observer_identity"]) is None
        or census_row["observations"] != expected_observations
        or census_row["observed_present_count"] != 0
        or census_row["ordered_intent_paths"] != census["ordered_intent_paths"]
        or census_row["repository_parent_head"] != census["repository_parent_head"]
        or census_row["resolved_shard_directory"] != str(_real_shard_directory().resolve())
        or census_row["runner_source_sha256"] != census["runner_source_sha256"]
        or start.tzinfo is None or end.tzinfo is None or end < start
        or not interval["start"].endswith("Z") or not interval["end"].endswith("Z")
    ):
        _fail("zero-intent census content binding drift")
    _require_commit_ancestry(
        census["repository_parent_head"], census_commit, "census parent-to-publication lineage"
    )
    _require_commit_ancestry(census_commit, trigger_commit, "census-to-GO lineage")
    _verify_activated_authority_and_green_lineage(
        trigger, trigger_commit=trigger_commit, root=root
    )
    return trigger


def _json_objects_in_channel_entry(entry: bytes) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for match in re.finditer(br"(?s)```(?:json)?[ \t]*\r?\n(.*?)\r?\n```", entry):
        try:
            value = json.loads(match.group(1).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            objects.append(value)
    return objects


def load_and_verify_committed_trigger() -> tuple[dict[str, Any], bytes, str]:
    """Discover the unique committed M245 SHARD GO channel payload."""

    root = _repository_root()
    repository_channel_path = _repo_relative(root / "AGENT_CHANNEL.md", root)
    history = _git_bytes(
        "rev-list", "--reverse", "HEAD", "--", repository_channel_path
    ).decode("ascii", errors="strict").splitlines()
    candidates: dict[str, tuple[dict[str, Any], bytes, str]] = {}
    for commit in history:
        try:
            committed = _git_blob(commit, repository_channel_path)
        except M245ShardContractError:
            continue
        for entry in _markdown_entries(committed):
            header = entry.splitlines()[0].upper() if entry.splitlines() else b""
            if b"M245 SHARD GO" not in header:
                continue
            digest = _sha256_bytes(entry)
            if digest in candidates:
                continue
            for value in _json_objects_in_channel_entry(entry):
                try:
                    trigger = validate_trigger_payload(value)
                except M245ShardContractError:
                    continue
                candidates[digest] = (trigger, entry, commit)
    if len(candidates) != 1:
        _fail("exactly one unique committed M245 SHARD GO trigger is required")
    trigger, entry_bytes, commit = next(iter(candidates.values()))
    verified = verify_committed_trigger(
        trigger, trigger_entry_bytes=entry_bytes, trigger_commit=commit
    )
    return verified, entry_bytes, commit


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _real_shard_directory() -> Path:
    return _repository_root() / SHARD_DIRECTORY_REPO_RELATIVE


def _ensure_plain_shard_directory() -> Path:
    root = _real_shard_directory()
    parent = root.parent
    try:
        parent_stat = os.lstat(parent)
    except OSError as exc:
        _fail(f"cannot lstat authorized shard parent: {exc}")
    if (
        not stat.S_ISDIR(parent_stat.st_mode)
        or getattr(parent_stat, "st_file_attributes", 0) & 0x400
    ):
        _fail("authorized shard parent is not a plain non-reparse directory")
    try:
        root_stat = os.lstat(root)
    except FileNotFoundError:
        try:
            root.mkdir(mode=0o700)
        except OSError as exc:
            _fail(f"cannot create the exact authorized shard directory: {exc}")
        root_stat = os.lstat(root)
    except OSError as exc:
        _fail(f"cannot lstat authorized shard directory: {exc}")
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or getattr(root_stat, "st_file_attributes", 0) & 0x400
        or root.resolve() != (_repository_root() / SHARD_DIRECTORY_REPO_RELATIVE).resolve()
    ):
        _fail("authorized shard directory is not a plain exact directory")
    return root


def _emit_pretrigger_zero_intent_census() -> int:
    expected_census_argv = [
        STDLIB_PYTHON, "-I", "-B", "-S", "-u", str(Path(__file__).resolve()),
        "--emit-pretrigger-zero-intent-census",
    ]
    _require_exact_supervisor_process_binding(expected_census_argv, "census")
    start = _utc_now()
    root = _ensure_plain_shard_directory()
    observations: list[dict[str, str]] = []
    for name in _ordered_intent_paths():
        try:
            os.lstat(root / name)
        except FileNotFoundError:
            observations.append({"lstat": "ABSENT", "path": name})
        else:
            observations.append({"lstat": "PRESENT", "path": name})
    present_count = sum(row["lstat"] == "PRESENT" for row in observations)
    if present_count:
        _fail("pretrigger census found a preexisting durable intent")
    repository_head = _git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    source_raw, _source_identity = _secure_regular_bytes(Path(__file__).resolve(), "runner source")
    payload = {
        "artifact": "M245_PRETRIGGER_ZERO_INTENT_CENSUS",
        # Verified equal to the declared census argv by the process binding
        # above, so the recorded value is the actual OS-observed command line.
        "argv": list(sys.orig_argv),
        "cwd": AUTHORITY_CWD,
        "observer_identity": f"pid={os.getpid()}",
        "observations": observations,
        "observed_present_count": 0,
        "ordered_intent_paths": _ordered_intent_paths(),
        "repository_parent_head": repository_head,
        "resolved_shard_directory": str(root.resolve()),
        "runner_source_sha256": _sha256_bytes(source_raw),
        "schema": "m245-pretrigger-zero-intent-census-v1",
        "utc_interval": {"end": _utc_now(), "start": start},
    }
    publish_immutable_json(
        HERE / ".M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json.tmp",
        HERE / "M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json",
        payload,
    )
    return 0


def validate_trigger_payload(payload: Any) -> dict[str, Any]:
    keys = (
        "agent_channel_binding", "aggregation_contract", "assignments",
        "authority_commit_v1", "authority_erratum2_commit", "authority_repair_commit",
        "authority_sha256", "final_shard_receipt_contract",
        "independent_static_audits", "process_argv_contract",
        "scientific_source_sha256", "zero_intent_census",
    )
    trigger = _exact_keys(payload, keys, "trigger")
    if trigger["assignments"] != {str(k): list(v) for k, v in ASSIGNMENTS.items()}:
        _fail("trigger assignments drift")
    if (
        trigger["authority_commit_v1"] != "c4468c3d330f968ce1a3b376d56aa1f6b640e709"
        or trigger["authority_erratum2_commit"] != "979f7c35334ff0df09ad134255fddf23f944237f"
        or trigger["authority_repair_commit"] != "853b30cf5ef8f87788aab6cee73218edddd6f466"
    ):
        _fail("authority commit chain drift")
    authority = _exact_keys(trigger["authority_sha256"], AUTHORITY_HASH_KEYS, "authority hashes")
    if authority != FROZEN_AUTHORITY_SHA256:
        _fail("frozen authority hash drift")
    sources = _exact_keys(
        trigger["scientific_source_sha256"],
        SCIENTIFIC_SOURCE_HASH_KEYS,
        "scientific source hashes",
    )
    if any(not _valid_hash(value) for value in sources.values()):
        _fail("missing or zero scientific source hash")
    channel = _exact_keys(
        trigger["agent_channel_binding"],
        ("commit_sha", "entry_sha256", "path"),
        "agent-channel binding",
    )
    if (
        not _valid_hash(channel["commit_sha"], 40)
        or not _valid_hash(channel["entry_sha256"])
        or channel["path"] != "AGENT_CHANNEL.md"
    ):
        _fail("agent-channel binding is not committed and hash-bound")
    audits = trigger["independent_static_audits"]
    if not isinstance(audits, list) or len(audits) != 2:
        _fail("exactly two independent static audits are required")
    reviewers: set[str] = set()
    expected_audit_paths = {
        "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
        "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    }
    for row in audits:
        _exact_keys(row, ("receipt_path", "reviewer_id", "sha256", "status"), "audit")
        reviewer = row["reviewer_id"].casefold() if isinstance(row["reviewer_id"], str) else ""
        if reviewer in reviewers or reviewer not in {"reviewer-a", "reviewer-b"}:
            _fail("static auditors are not independent")
        reviewers.add(reviewer)
        if row["receipt_path"] not in expected_audit_paths:
            _fail("unexpected static audit receipt")
        if row["sha256"] != sources[row["receipt_path"]]:
            _fail("static audit hash is not source-bound")
        if row["status"] != "PASS_STATIC_M245_SCIENTIFIC_BUNDLE_ONLY":
            _fail("static audit did not pass")
    if {row["receipt_path"] for row in audits} != expected_audit_paths:
        _fail("static audit receipt census drift")
    if trigger["process_argv_contract"] != _expected_process_argv_contract(sources):
        _fail("process argv contract drift")
    final_contract = _exact_keys(
        trigger["final_shard_receipt_contract"], ("paths", "schema"), "final receipt contract"
    )
    if final_contract != {
        "paths": [f"M245_S{s}_FINAL_RECEIPT_20260810.json" for s in ASSIGNMENTS],
        "schema": "m245-final-shard-receipt-v2",
    }:
        _fail("final shard receipt contract drift")
    aggregation = _exact_keys(
        trigger["aggregation_contract"],
        ("authorization_path", "authorization_schema", "result_schema", "receipt_schema", "source_sha256"),
        "aggregation contract",
    )
    expected_aggregation = {
        "authorization_path": "M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json",
        "authorization_schema": "m245-aggregation-input-authorization-v1",
        "result_schema": "m245-aggregated-spectrum-v1",
        "receipt_schema": "m245-aggregation-receipt-v1",
        "source_sha256": sources["aggregate_m245_spectrum.py"],
    }
    if aggregation != expected_aggregation or not _valid_hash(aggregation["source_sha256"]):
        _fail("aggregation contract drift")
    census = _exact_keys(
        trigger["zero_intent_census"],
        ("argv", "bytes", "cwd", "observed_present_count", "ordered_intent_paths", "path",
         "repository_commit", "repository_parent_head", "runner_source_sha256", "sha256"),
        "zero-intent census",
    )
    expected_census_argv = [
        STDLIB_PYTHON, "-I", "-B", "-S", "-u",
        str((HERE / "run_m245_scientific_shard.py").resolve()),
        "--emit-pretrigger-zero-intent-census",
    ]
    if (
        census["argv"] != expected_census_argv
        or type(census["bytes"]) is not int or census["bytes"] <= 0
        or census["cwd"] != AUTHORITY_CWD
        or census["observed_present_count"] != 0
        or census["ordered_intent_paths"] != _ordered_intent_paths()
        or census["path"] != "M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json"
        or not _valid_hash(census["repository_commit"], 40)
        or not _valid_hash(census["repository_parent_head"], 40)
        or census["runner_source_sha256"] != sources["run_m245_scientific_shard.py"]
        or not _valid_hash(census["sha256"])
    ):
        _fail("zero-intent census binding drift")
    return trigger


def _validate_mpf_tuple(payload: Any, label: str) -> Fraction:
    row = _exact_keys(payload, MPF_TUPLE_KEYS, label)
    if type(row["sign"]) is not int or row["sign"] not in (0, 1):
        _fail(f"{label} sign is not canonical")
    if type(row["exponent"]) is not int or type(row["bitcount"]) is not int:
        _fail(f"{label} exponent/bitcount is not integral")
    text = row["mantissa"]
    if not isinstance(text, str) or not re.fullmatch(r"0|[1-9][0-9]*", text):
        _fail(f"{label} mantissa is not lossless canonical decimal")
    mantissa = int(text)
    if row["bitcount"] != mantissa.bit_length():
        _fail(f"{label} bitcount drift")
    if mantissa == 0 and row["sign"] != 0:
        _fail(f"{label} has negative zero")
    exponent = row["exponent"]
    magnitude = Fraction(mantissa << exponent, 1) if exponent >= 0 else Fraction(mantissa, 1 << -exponent)
    return -magnitude if row["sign"] else magnitude


def _fraction_to_mpf_tuple(value: Fraction) -> dict[str, Any]:
    """Return the canonical exact mpmath tuple for a dyadic ledger sum."""

    if value == 0:
        return {"bitcount": 0, "exponent": 0, "mantissa": "0", "sign": 0}
    sign = 1 if value < 0 else 0
    numerator = abs(value.numerator)
    denominator = value.denominator
    if denominator & (denominator - 1):
        _fail("quadrature error sum ceased to be dyadic")
    exponent = -(denominator.bit_length() - 1)
    while numerator % 2 == 0:
        numerator //= 2
        exponent += 1
    return {
        "bitcount": numerator.bit_length(),
        "exponent": exponent,
        "mantissa": str(numerator),
        "sign": sign,
    }


def _validate_endpoint(payload: Any, label: str) -> None:
    row = _exact_keys(payload, ENDPOINT_KEYS, label)
    if row["kind"] in ("+inf", "-inf"):
        if row["mpf"] is not None:
            _fail(f"{label} infinite endpoint carries a finite tuple")
    elif row["kind"] == "finite":
        _validate_mpf_tuple(row["mpf"], f"{label}.mpf")
    else:
        _fail(f"{label} endpoint kind is unknown")


def validate_quad_call_ledger(
    ledger: Any,
    *,
    shard_id: int,
    invocation_index: int,
    event_id: str,
    _return_internal_aggregates: bool = False,
) -> dict[str, Any]:
    validate_shard_request(
        shard_id,
        ASSIGNMENTS[shard_id] if shard_id in ASSIGNMENTS else (),
        invocation_index,
        invocation_index == 2,
    )
    if event_id != ASSIGNMENTS[shard_id][invocation_index - 1] and not event_id.startswith("DUMMY_"):
        _fail("ledger event is outside its invocation context")
    if not isinstance(ledger, list) or len(ledger) < 8:
        _fail("quadrature ledger is incomplete")
    request_indices: list[int] = []
    completion_indices: list[int] = []
    by_request: dict[int, dict[str, Any]] = {}
    required_scopes = {(engine, dps) for engine in ("primary", "replica") for dps in (80, 100)}
    actual_by_scope = {scope: [] for scope in required_scopes}
    prior_miss_signatures: set[tuple[Any, ...]] = set()
    outer_value_fractions: dict[tuple[str, int, str], Fraction] = {}
    outer_error_fractions: dict[str, Fraction] = {}
    for position, entry_value in enumerate(ledger):
        entry = _exact_keys(entry_value, QUAD_CALL_RECEIPT_KEYS, "quadrature call")
        if (
            entry["shard_id"] != shard_id
            or entry["invocation_index"] != invocation_index
            or entry["event_id"] != event_id
        ):
            _fail("quadrature call context drift")
        engine = entry["engine"]
        dps = entry["precision_dps"]
        if (engine, dps) not in required_scopes:
            _fail("quadrature engine/precision drift")
        expected_scope = f"S{shard_id}:I{invocation_index}:{event_id}:{engine}:{dps}:fresh"
        if entry["cache_scope_id"] != expected_scope:
            _fail("quadrature cache crossed an event or precision scope")
        request_index = entry["request_index"]
        completion_index = entry["completion_index"]
        if type(request_index) is not int or type(completion_index) is not int:
            _fail("quadrature request was not completed")
        request_indices.append(request_index)
        completion_indices.append(completion_index)
        if request_index in by_request:
            _fail("duplicate quadrature request")
        by_request[request_index] = entry
        if entry["call_role"] not in QUAD_ROLES:
            _fail("unknown quadrature call role")
        if not isinstance(entry["quantity"], str) or not entry["quantity"]:
            _fail("quadrature quantity is empty")
        if not isinstance(entry["panel_path"], list) or not entry["panel_path"]:
            _fail("quadrature panel path is malformed")
        _validate_endpoint(entry["interval_left"], "interval_left")
        _validate_endpoint(entry["interval_right"], "interval_right")
        if (
            entry["method"] != "tanh-sinh"
            or entry["maxdegree"] != 14
            or entry["error_api"] is not True
            or entry["error_semantics"] != "heuristic_diagnostic_estimate_not_interval_certificate"
            or entry["interval_certified"] is not False
        ):
            _fail("frozen quadrature policy drift")
        saved_eps = _validate_mpf_tuple(entry["saved_mp_eps_mpf"], "saved_mp_eps_mpf")
        returned_value = _validate_mpf_tuple(entry["returned_value_mpf"], "returned_value_mpf")
        returned_error = _validate_mpf_tuple(entry["returned_error_mpf"], "returned_error_mpf")
        expected_error_gate = returned_error >= 0 and returned_error <= saved_eps / 8
        if (
            entry["value_finite"] is not True
            or entry["error_finite"] is not True
            or entry["error_le_saved_mp_eps_over_8"] is not expected_error_gate
            or not expected_error_gate
            or entry["exception_type"] is not None
            or entry["exception_message_sha256"] is not None
            or entry["pass"] is not True
        ):
            _fail("quadrature call did not pass its finite diagnostic gate")
        cache_signature = (
            entry["cache_scope_id"],
            engine,
            dps,
            entry["quantity"],
            entry["call_role"],
            entry["nesting_depth"],
            _canonical_json_bytes(entry["panel_path"]),
            _canonical_json_bytes(entry["interval_left"]),
            _canonical_json_bytes(entry["interval_right"]),
            _canonical_json_bytes(entry["returned_value_mpf"]),
            _canonical_json_bytes(entry["returned_error_mpf"]),
        )
        disposition = entry["cache_disposition"]
        if disposition == "miss":
            if entry["mp_quad_invoked"] is not True:
                _fail("cache miss bypassed the sole mp.quad gateway")
            actual_by_scope[(engine, dps)].append(entry)
            prior_miss_signatures.add(cache_signature)
        elif disposition == "hit":
            if entry["mp_quad_invoked"] is not False:
                _fail("cache hit invoked mp.quad")
            if cache_signature not in prior_miss_signatures:
                _fail("cache hit has no prior identical retained miss record")
        else:
            _fail("unknown cache disposition")
        depth = entry["nesting_depth"]
        parent = entry["parent_request_index"]
        if depth == 0:
            if parent is not None or entry["call_role"] not in (
                "outer_top_level",
                "direct_analytic_gate",
                "direct_residual_gate",
                "direct_beta_residual_gate",
            ):
                _fail("outer quadrature nesting drift")
            if engine == "replica" and entry["call_role"] != "outer_top_level":
                _fail("replica outer request used a primary-only direct gate role")
            value_key = (engine, dps, entry["quantity"])
            outer_value_fractions[value_key] = (
                outer_value_fractions.get(value_key, Fraction(0)) + returned_value
            )
            error_key = f"{engine}:{dps}:{entry['quantity']}"
            outer_error_fractions[error_key] = (
                outer_error_fractions.get(error_key, Fraction(0)) + returned_error
            )
        elif depth == 1:
            if type(parent) is not int or parent >= request_index or parent not in by_request:
                _fail("nested quadrature call has no earlier parent")
            parent_entry = by_request[parent]
            if (
                parent_entry["cache_scope_id"] != entry["cache_scope_id"]
                or parent_entry["nesting_depth"] != 0
                or entry["call_role"] not in ("nested_plackett", "nested_unary")
            ):
                _fail("nested quadrature call crossed its parent scope")
            expected_nested_role = (
                "nested_plackett" if engine == "primary" else "nested_unary"
            )
            if entry["call_role"] != expected_nested_role:
                _fail("nested quadrature role disagrees with its engine")
            if completion_index >= parent_entry["completion_index"]:
                _fail("nested call did not complete before its parent")
        else:
            _fail("quadrature nesting depth exceeds the frozen contract")
    if request_indices != list(range(len(ledger))):
        _fail("quadrature request ledger is reordered or non-contiguous")
    if sorted(completion_indices) != list(range(len(ledger))):
        _fail("quadrature completion order is not a permutation")
    for scope, actual in actual_by_scope.items():
        if not actual:
            _fail(f"quadrature scope {scope} has no real mp.quad call")
        if not any(row["nesting_depth"] == 0 for row in actual):
            _fail("quadrature scope lacks an outer request")
    completion_order = [row["request_index"] for row in sorted(ledger, key=lambda row: row["completion_index"])]
    actual_count = sum(row["mp_quad_invoked"] is True for row in ledger)
    cache_count = sum(row["cache_disposition"] == "hit" for row in ledger)
    summary = {
        "request_count": len(ledger),
        "actual_mp_quad_call_count": actual_count,
        "cache_hit_count": cache_count,
        "outer_call_count": sum(row["nesting_depth"] == 0 for row in ledger),
        "nested_call_count": sum(row["nesting_depth"] == 1 for row in ledger),
        "completion_request_order": completion_order,
        "outer_panel_error_sums_mpf": {
            key: _fraction_to_mpf_tuple(value)
            for key, value in sorted(outer_error_fractions.items())
        },
        "nested_raw_error_sum_is_diagnostic_only": True,
        "pass": True,
    }
    if _return_internal_aggregates:
        summary["_outer_value_fractions"] = outer_value_fractions
        summary["_outer_error_fractions"] = {
            (parts[0], int(parts[1]), parts[2]): value
            for key, value in outer_error_fractions.items()
            for parts in (key.split(":", 2),)
        }
    return summary


def _scientific_scalar_fraction(value: Any, label: str) -> Fraction:
    """Parse a reported decimal/JSON scalar without binary64 arithmetic."""

    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        _fail(f"{label} is not a finite scientific scalar")
    spelling = repr(value) if isinstance(value, float) else str(value)
    try:
        parsed = Fraction(spelling)
    except (ValueError, ZeroDivisionError) as exc:
        _fail(f"{label} is not an exact decimal scalar: {exc}")
    if isinstance(value, float) and not math.isfinite(value):
        _fail(f"{label} is nonfinite")
    return parsed


def _fraction_close(
    observed: Fraction,
    reference: Fraction,
    relative_tolerance: Fraction,
) -> bool:
    return abs(observed - reference) <= relative_tolerance * max(
        Fraction(1), abs(reference)
    )


def _serialized_ledger_close(
    exact_value: Fraction,
    reported: Any,
    dps: int,
    label: str,
) -> bool:
    parsed = _scientific_scalar_fraction(reported, label)
    return _fraction_close(
        parsed,
        exact_value,
        Fraction(1, 10 ** (dps - 8)),
    )


def _precision_close(low: Any, high: Any, label: str) -> bool:
    low_value = _scientific_scalar_fraction(low, f"{label} at 80 dps")
    high_value = _scientific_scalar_fraction(high, f"{label} at 100 dps")
    return _fraction_close(low_value, high_value, Fraction(2, 10**12))


def _top_level_error_pass(error: Fraction, value: Fraction) -> bool:
    return error >= 0 and error <= Fraction(2, 10**14) * max(
        Fraction(1), abs(value)
    )


def _require_bound_outer_scalar(
    values: dict[tuple[str, int, str], Fraction],
    errors: dict[tuple[str, int, str], Fraction],
    *,
    engine: str,
    dps: int,
    quantity: str,
    reported: Any,
    label: str,
) -> tuple[Fraction, Fraction]:
    key = (engine, dps, quantity)
    if key not in values or key not in errors:
        _fail(f"{label} has no complete outer quadrature ledger aggregate")
    value, error = values[key], errors[key]
    if not _serialized_ledger_close(value, reported, dps, label):
        _fail(f"{label} is not bound to the exact outer ledger value sum")
    if not _top_level_error_pass(error, value):
        _fail(f"{label} exact outer ledger error sum failed its top-level gate")
    return value, error


def _validate_scientific_ledger_bindings(
    event: dict[str, Any],
    ledger_summary: dict[str, Any],
) -> None:
    """Recompute scientific gates from exact outer-ledger aggregates in S."""

    values = ledger_summary.get("_outer_value_fractions")
    errors = ledger_summary.get("_outer_error_fractions")
    if not isinstance(values, dict) or not isinstance(errors, dict):
        _fail("scientific binding lacks internal exact ledger aggregates")
    primary = event["primary_by_precision"]
    replica = event["replica_by_precision"]
    bound_primary: dict[int, dict[str, Any]] = {}
    bound_replica: dict[int, dict[str, Fraction]] = {}

    for dps in (80, 100):
        text = str(dps)
        p = primary[text]
        p_bound: dict[str, Any] = {}
        for quantity, reported in (("mu_rb", p["mu_rb"]), ("K", p["K"])):
            p_bound[quantity], _ = _require_bound_outer_scalar(
                values, errors, engine="primary", dps=dps, quantity=quantity,
                reported=reported, label=f"primary {quantity} at {dps} dps",
            )
        p_bound["d"] = []
        p_bound["beta"] = []
        for q in range(9):
            for family in ("d", "beta"):
                exact, _ = _require_bound_outer_scalar(
                    values, errors, engine="primary", dps=dps,
                    quantity=f"{family}_{q}", reported=p[family][q],
                    label=f"primary {family}_{q} at {dps} dps",
                )
                p_bound[family].append(exact)

        reported_top = p["quadrature_audit"]["top_level"]
        expected_top_names = ["mu_rb", "K"] + [
            f"{family}_{q}" for q in range(9) for family in ("d", "beta")
        ]
        if (
            not isinstance(reported_top, list)
            or [row.get("quantity") for row in reported_top] != expected_top_names
        ):
            _fail("primary top-level audit quantity order is not exact")
        for row in reported_top:
            quantity = row["quantity"]
            key = ("primary", dps, quantity)
            if (
                row.get("pass") is not True
                or not _serialized_ledger_close(
                    errors[key], row.get("error_sum"), dps,
                    f"primary {quantity} audit error",
                )
            ):
                _fail("primary top-level audit is not exact-ledger-bound")

        direct_r: list[Fraction] = []
        for q, row in enumerate(p["analytic_direct_checks"]["R"]):
            direct, _ = _require_bound_outer_scalar(
                values, errors, engine="primary", dps=dps,
                quantity=f"direct_R_{q}", reported=row["direct"],
                label=f"primary direct_R_{q} at {dps} dps",
            )
            analytic = _scientific_scalar_fraction(row["analytic"], "analytic R")
            recomputed = _fraction_close(analytic, direct, Fraction(2, 10**11))
            if row["pass"] is not recomputed or not recomputed:
                _fail("primary direct R gate disagrees with exact ledger arithmetic")
            direct_r.append(direct)
        p_bound["direct_R"] = direct_r

        direct_g: list[list[Fraction | None]] = [[None] * 9 for _ in range(9)]
        for row in p["analytic_direct_checks"]["G_upper"]:
            m, q = row["m"], row["q"]
            direct, _ = _require_bound_outer_scalar(
                values, errors, engine="primary", dps=dps,
                quantity=f"direct_G_{m}_{q}", reported=row["direct"],
                label=f"primary direct_G_{m}_{q} at {dps} dps",
            )
            analytic = _scientific_scalar_fraction(row["analytic"], "analytic G")
            recomputed = _fraction_close(analytic, direct, Fraction(2, 10**11))
            if row["pass"] is not recomputed or not recomputed:
                _fail("primary direct G gate disagrees with exact ledger arithmetic")
            direct_g[m][q] = direct
            direct_g[q][m] = direct
        if any(value is None for row in direct_g for value in row):
            _fail("primary direct G ledger binding is incomplete")
        p_bound["direct_G"] = direct_g

        residual_observed: dict[int, Fraction] = {}
        beta_residual_observed: dict[int, Fraction] = {}
        for q in (0, 4, 8):
            block = p["leading_blocks"][q]
            direct_row = block["direct_residual"]
            beta_row = block["direct_beta_residual"]
            direct, _ = _require_bound_outer_scalar(
                values, errors, engine="primary", dps=dps,
                quantity=f"direct_residual_Q{q}", reported=direct_row["observed"],
                label=f"primary direct residual Q{q} at {dps} dps",
            )
            direct_reference = _scientific_scalar_fraction(
                direct_row["reference"], "direct residual reference"
            )
            beta_direct, _ = _require_bound_outer_scalar(
                values, errors, engine="primary", dps=dps,
                quantity=f"direct_beta_residual_Q{q}",
                reported=beta_row["observed"],
                label=f"primary direct beta residual Q{q} at {dps} dps",
            )
            beta_reference = _scientific_scalar_fraction(
                beta_row["reference"], "direct beta residual reference"
            )
            gap = _scientific_scalar_fraction(
                block["ordinary_beta_identity"]["gap"], "ordinary beta gap"
            )
            tolerance = Fraction(2, 10**9) * p_bound["K"]
            direct_pass = abs(direct - direct_reference) <= tolerance
            beta_pass = (
                abs(beta_direct - beta_reference) <= tolerance
                and abs((beta_direct - direct) - gap) <= tolerance
            )
            if direct_row["pass"] is not direct_pass or not direct_pass:
                _fail("direct residual gate disagrees with exact ledger arithmetic")
            if beta_row["pass"] is not beta_pass or not beta_pass:
                _fail("direct beta residual gate disagrees with exact ledger arithmetic")
            residual_observed[q] = direct
            beta_residual_observed[q] = beta_direct
        p_bound["direct_residual"] = residual_observed
        p_bound["direct_beta_residual"] = beta_residual_observed
        bound_primary[dps] = p_bound

        r = replica[text]
        r_bound: dict[str, Fraction] = {}
        reported_errors = r["quadrature_audit"]["outer_top_level_error_sums"]
        if set(reported_errors) != {"mu_rep", "M_same", "M_cross"}:
            _fail("replica outer error quantity census drift")
        for quantity in ("mu_rep", "M_same", "M_cross"):
            exact, error = _require_bound_outer_scalar(
                values, errors, engine="replica", dps=dps, quantity=quantity,
                reported=r[quantity], label=f"replica {quantity} at {dps} dps",
            )
            if not _serialized_ledger_close(
                error, reported_errors[quantity], dps,
                f"replica {quantity} audit error",
            ):
                _fail("replica outer error sum is not exact-ledger-bound")
            r_bound[quantity] = exact
        r_bound["K_rep"] = (
            r_bound["M_same"] + r_bound["M_cross"]
        ) / 2 - r_bound["mu_rep"] ** 2
        if not _serialized_ledger_close(
            r_bound["K_rep"], r["K_rep"], dps, f"replica K_rep at {dps} dps"
        ):
            _fail("replica K is not derived from its exact ledger-bound moments")
        bound_replica[dps] = r_bound

    p80, p100 = primary["80"], primary["100"]
    r80, r100 = replica["80"], replica["100"]
    recomputed_cross = {
        "primary_mu_K": all(
            _precision_close(p80[name], p100[name], f"primary {name}")
            for name in ("mu_rb", "K")
        ),
        "primary_R": all(
            _precision_close(a, b, "primary R")
            for a, b in zip(p80["R"], p100["R"])
        ),
        "primary_G": all(
            _precision_close(a, b, "primary G")
            for low_row, high_row in zip(p80["G"], p100["G"])
            for a, b in zip(low_row, high_row)
        ),
        "primary_d": all(
            _precision_close(a, b, "primary d")
            for a, b in zip(p80["d"], p100["d"])
        ),
        "primary_beta": all(
            _precision_close(a, b, "primary beta")
            for a, b in zip(p80["beta"], p100["beta"])
        ),
        "primary_blocks": all(
            low["Q"] == high["Q"]
            and all(
                _precision_close(a, b, "primary block coefficient")
                for a, b in zip(low["c"], high["c"])
            )
            and all(
                _precision_close(low[name], high[name], f"primary block {name}")
                for name in ("P", "V", "V_beta")
            )
            for low, high in zip(p80["leading_blocks"], p100["leading_blocks"])
        ),
        "replica_integrated": all(
            _precision_close(r80[name], r100[name], f"replica {name}")
            for name in ("mu_rep", "M_same", "M_cross", "K_rep")
        ),
        "replica_all_fixed_nodes": all(
            _precision_close(a, b, "replica fixed node")
            for a, b in zip(r80["b_rep_at_nodes"], r100["b_rep_at_nodes"])
        ),
        "primary_all_fixed_nodes": all(
            _precision_close(a["primary"], b["primary"], "primary fixed node")
            for a, b in zip(
                event["primary_replica_gates"]["by_precision"]["80"]["node_gates"],
                event["primary_replica_gates"]["by_precision"]["100"]["node_gates"],
            )
        ),
    }
    cross = event["cross_precision_gates"]
    if cross.get("checks") != recomputed_cross or cross.get("pass") is not all(
        recomputed_cross.values()
    ) or cross.get("pass") is not True:
        _fail("reported cross-precision gates disagree with S recomputation")

    integrated = event["primary_replica_gates"]["by_precision"]
    for dps in (80, 100):
        gate = integrated[str(dps)]
        p_mu = bound_primary[dps]["mu_rb"]
        p_k = bound_primary[dps]["K"]
        r_mu = bound_replica[dps]["mu_rep"]
        r_k = bound_replica[dps]["K_rep"]
        mu_tolerance = Fraction(2, 10**9) * max(Fraction(1), abs(p_mu))
        k_tolerance = Fraction(5, 10**8) * p_k
        mu_pass = abs(p_mu - r_mu) <= mu_tolerance
        k_pass = abs(p_k - r_k) <= k_tolerance
        node_passes: list[bool] = []
        for index, node_gate in enumerate(gate["node_gates"]):
            primary_node = _scientific_scalar_fraction(
                node_gate["primary"], "primary fixed-node value"
            )
            replica_node = _scientific_scalar_fraction(
                node_gate["replica"], "replica fixed-node value"
            )
            node_pass = _fraction_close(
                replica_node, primary_node, Fraction(2, 10**10)
            )
            if (
                node_gate["replica"] != replica[str(dps)]["b_rep_at_nodes"][index]
                or node_gate["pass"] is not node_pass
            ):
                _fail("reported primary/replica node gate disagrees with S recomputation")
            node_passes.append(node_pass)
        all_nodes = all(node_passes)
        combined = mu_pass and k_pass and all_nodes
        if (
            gate["mu_pass"] is not mu_pass
            or gate["K_pass"] is not k_pass
            or gate["nodes_pass"] is not all_nodes
            or gate["pass"] is not combined
            or not _fraction_close(
                _scientific_scalar_fraction(gate["mu_tolerance"], "mu tolerance"),
                mu_tolerance,
                Fraction(5, 10**15),
            )
            or not _fraction_close(
                _scientific_scalar_fraction(gate["K_tolerance"], "K tolerance"),
                k_tolerance,
                Fraction(5, 10**15),
            )
            or not combined
        ):
            _fail("reported integrated primary/replica gate disagrees with S recomputation")
    if event["primary_replica_gates"].get("pass") is not all(
        integrated[str(dps)]["pass"] is True for dps in (80, 100)
    ):
        _fail("primary/replica aggregate gate drift")
    for dps in (80, 100):
        _validate_reported_primary_ladder(primary[str(dps)], dps, event["event_id"])
    _validate_reported_curve_report(event)


def _symmetric_eigenvalue_range(matrix: list[list[float]]) -> tuple[float, float]:
    """Cyclic Jacobi eigenvalue range for a small symmetric float matrix."""

    size = len(matrix)
    work = [list(map(float, row)) for row in matrix]
    if any(not math.isfinite(value) for row in work for value in row):
        _fail("eigen recomputation received a nonfinite Gram entry")
    for _sweep in range(60):
        off_diagonal = math.sqrt(sum(
            work[i][j] * work[i][j]
            for i in range(size) for j in range(size) if i != j
        ))
        diagonal_scale = max(1.0, max(abs(work[i][i]) for i in range(size)))
        if off_diagonal <= 1.0e-13 * diagonal_scale:
            break
        for i in range(size - 1):
            for j in range(i + 1, size):
                if work[i][j] == 0.0:
                    continue
                theta = (work[j][j] - work[i][i]) / (2.0 * work[i][j])
                t = math.copysign(1.0, theta) / (
                    abs(theta) + math.sqrt(theta * theta + 1.0)
                )
                cosine = 1.0 / math.sqrt(t * t + 1.0)
                sine = t * cosine
                for k in range(size):
                    row_i, row_j = work[i][k], work[j][k]
                    work[i][k] = cosine * row_i - sine * row_j
                    work[j][k] = sine * row_i + cosine * row_j
                for k in range(size):
                    column_i, column_j = work[k][i], work[k][j]
                    work[k][i] = cosine * column_i - sine * column_j
                    work[k][j] = sine * column_i + cosine * column_j
    else:
        _fail("eigen recomputation did not converge")
    eigenvalues = [work[i][i] for i in range(size)]
    return min(eigenvalues), max(eigenvalues)


def _validate_reported_primary_ladder(
    p: dict[str, Any], dps: int, event_id: str
) -> None:
    """Recompute c/P/V/V_beta/spectrum/residual/energy/identity from bound G,d,beta,K.

    Rational quantities are re-derived in exact Fraction arithmetic from the
    reported full-precision decimal strings, so a coherent substituted ladder
    cannot satisfy these pins; only the eigenspectrum uses binary64 with a
    Weyl-bounded absolute tolerance.
    """

    rel = Fraction(1, 10 ** (dps - 12))
    K = _scientific_scalar_fraction(p["K"], "ladder K")
    if K <= 0:
        _fail("ladder K is not positive")
    G = [
        [_scientific_scalar_fraction(value, "ladder G") for value in row]
        for row in p["G"]
    ]
    d = [_scientific_scalar_fraction(value, "ladder d") for value in p["d"]]
    beta = [_scientific_scalar_fraction(value, "ladder beta") for value in p["beta"]]
    g_float = [[float(value) for value in row] for row in p["G"]]
    tau = Fraction(2, 10**10) * K
    margin = rel * max(Fraction(1), abs(K))
    reported_projections: list[Fraction] = []
    reported_residuals: list[Fraction] = []
    for q, block in enumerate(p["leading_blocks"]):
        size = q + 1
        c = [_scientific_scalar_fraction(value, "ladder c") for value in block["c"]]
        d_q = d[:size]
        beta_q = beta[:size]
        g_scale = max(abs(G[i][j]) for i in range(size) for j in range(size))
        c_scale = max([Fraction(1)] + [abs(value) for value in c])
        d_denominator = max([Fraction(1)] + [abs(value) for value in d_q])
        equation_errors = [
            sum((G[i][j] * c[j] for j in range(size)), Fraction(0)) - d_q[i]
            for i in range(size)
        ]
        residual_ratio = max(abs(value) for value in equation_errors) / d_denominator
        solve_margin = (
            Fraction(3, 10**20)
            + rel * size * max(Fraction(1), g_scale * c_scale) / d_denominator
        )
        if residual_ratio > solve_margin:
            _fail("reported coefficients do not solve their bound Galerkin system")
        reported_solve = _scientific_scalar_fraction(
            block["solve_relative_inf_residual"], "ladder solve residual"
        )
        if reported_solve < 0 or reported_solve > Fraction(2, 10**20):
            _fail("reported solve residual exceeds its frozen 2e-20 gate")
        projection = sum((x * y for x, y in zip(d_q, c)), Fraction(0))
        projection_scale = max(
            Fraction(1), abs(K),
            sum((abs(x * y) for x, y in zip(d_q, c)), Fraction(0)),
        )
        p_rep = _scientific_scalar_fraction(block["P"], "ladder P")
        if abs(p_rep - projection) > rel * projection_scale:
            _fail("reported projection P is not d.c from the bound system")
        v_rep = _scientific_scalar_fraction(block["V"], "ladder V")
        if abs(v_rep - (K - p_rep)) > rel * projection_scale:
            _fail("reported residual V is not K - P")
        reported_projections.append(p_rep)
        reported_residuals.append(v_rep)
        quad_beta = sum(
            (beta_q[i] * G[i][j] * beta_q[j]
             for i in range(size) for j in range(size)),
            Fraction(0),
        )
        cross = sum((x * y for x, y in zip(beta_q, d_q)), Fraction(0))
        v_beta_scale = max(
            Fraction(1), abs(K), abs(quad_beta),
            2 * sum((abs(x * y) for x, y in zip(beta_q, d_q)), Fraction(0)),
        )
        vb_rep = _scientific_scalar_fraction(block["V_beta"], "ladder V_beta")
        if abs(vb_rep - (K - 2 * cross + quad_beta)) > rel * v_beta_scale:
            _fail("reported V_beta is not the bound ordinary-beta energy")
        identity = block["ordinary_beta_identity"]
        if identity["gap"] != identity["lhs"]:
            _fail("ordinary-beta gap is not the reported lhs")
        lhs_rep = _scientific_scalar_fraction(identity["lhs"], "identity lhs")
        rhs_rep = _scientific_scalar_fraction(identity["rhs"], "identity rhs")
        if abs(lhs_rep - (vb_rep - v_rep)) > rel * v_beta_scale:
            _fail("identity lhs is not V_beta - V")
        difference = [b - a for b, a in zip(beta_q, c)]
        rhs_mine = sum(
            (difference[i] * G[i][j] * difference[j]
             for i in range(size) for j in range(size)),
            Fraction(0),
        )
        rhs_scale = max(
            Fraction(1),
            sum(
                (abs(difference[i]) * abs(G[i][j]) * abs(difference[j])
                 for i in range(size) for j in range(size)),
                Fraction(0),
            ),
        )
        if abs(rhs_rep - rhs_mine) > rel * rhs_scale:
            _fail("identity rhs is not (beta-c)^T G (beta-c) from the bound system")
        if "identity_tolerance" in identity:
            identity_tolerance = _scientific_scalar_fraction(
                identity["identity_tolerance"], "identity tolerance"
            )
            nonnegative_tolerance = _scientific_scalar_fraction(
                identity["nonnegative_tolerance"], "nonnegative tolerance"
            )
            if abs(identity_tolerance - Fraction(2, 10**20) * K) > margin:
                _fail("identity tolerance is not 2e-20 K")
            if abs(nonnegative_tolerance - tau) > margin:
                _fail("nonnegative tolerance is not 2e-10 K")
            if abs(lhs_rep - rhs_rep) > Fraction(2, 10**20) * K + rel * v_beta_scale:
                _fail("ordinary-beta identity violates its 2e-20 K gate")
            if lhs_rep < -(tau + margin) or rhs_rep < -(tau + margin):
                _fail("ordinary-beta identity violates nonnegativity")
        energy = block["energy_gate"]
        tau_rep = _scientific_scalar_fraction(energy["tau_K"], "energy tau_K")
        if abs(tau_rep - tau) > margin:
            _fail("energy tau_K is not 2e-10 K")
        if "bounds_pass" in energy:
            bound = tau + margin
            if any(
                value < -bound or value > K + bound
                for value in reported_projections
            ):
                _fail("reported projection ladder escapes [0, K] within tau_K")
            if any(value < -bound for value in reported_residuals):
                _fail("reported residual ladder is negative beyond tau_K")
            if any(
                reported_projections[index] < reported_projections[index - 1] - bound
                for index in range(1, len(reported_projections))
            ):
                _fail("reported projection ladder is not monotone within tau_K")
            if event_id == "E00" and (
                abs(reported_projections[0] - K) > bound
                or abs(reported_residuals[0]) > bound
            ):
                _fail("endpoint-control ladder violates its P0=K identity")
        lambda_min_rep = _scientific_scalar_fraction(block["lambda_min"], "lambda_min")
        lambda_max_rep = _scientific_scalar_fraction(block["lambda_max"], "lambda_max")
        ratio_rep = _scientific_scalar_fraction(block["lambda_ratio"], "lambda_ratio")
        condition_rep = _scientific_scalar_fraction(block["condition_2"], "condition_2")
        if lambda_min_rep <= 0 or lambda_max_rep <= 0 or lambda_min_rep > lambda_max_rep:
            _fail("reported eigenvalue range is not positive-ordered")
        if abs(ratio_rep * lambda_max_rep - lambda_min_rep) > rel * max(
            Fraction(1), lambda_min_rep
        ):
            _fail("lambda_ratio is not lambda_min/lambda_max")
        if abs(condition_rep * lambda_min_rep - lambda_max_rep) > rel * max(
            Fraction(1), lambda_max_rep
        ):
            _fail("condition_2 is not lambda_max/lambda_min")
        if (
            ratio_rep < Fraction(1, 10**25) * (1 - rel)
            or condition_rep > Fraction(10**25) * (1 + rel)
        ):
            _fail("reported spectrum violates the frozen conditioning gates")
        block_float = [row[:size] for row in g_float[:size]]
        eigen_min, eigen_max = _symmetric_eigenvalue_range(block_float)
        eigen_scale = max(
            1.0, size * max(abs(value) for row in block_float for value in row)
        )
        if (
            abs(float(lambda_min_rep) - eigen_min) > 1.0e-8 * eigen_scale
            or abs(float(lambda_max_rep) - eigen_max) > 1.0e-8 * eigen_scale
        ):
            _fail("reported eigenspectrum disagrees with the recomputed Gram spectrum")


def _float_close(observed: float, expected: float) -> bool:
    return (
        math.isfinite(observed)
        and math.isfinite(expected)
        and abs(observed - expected) <= 1.0e-9 * max(1.0, abs(observed), abs(expected))
    )


def _float_curve_transform(model: str, x: float) -> float:
    if model == "geometric":
        return math.log1p(-x)
    if model == "logistic":
        return math.log(x / (1.0 - x))
    if model == "Gompertz":
        return math.log(-math.log(x))
    _fail("unknown finite-ladder model")


def _float_curve_inverse(model: str, transformed: float) -> float:
    if model == "geometric":
        return 1.0 - math.exp(transformed)
    if model == "logistic":
        return 1.0 / (1.0 + math.exp(-transformed))
    if model == "Gompertz":
        return math.exp(-math.exp(transformed))
    _fail("unknown finite-ladder model")


def _float_classify_curve_ladder(
    event_id: str, model: str, x80: list[float], x100: list[float]
) -> dict[str, Any]:
    """Stdlib binary64 mirror of the frozen primary-core finite-ladder classifier."""

    if event_id == "E00":
        return {"label": "ENDPOINT_CONTROL/NA"}
    if len(x80) != 9 or len(x100) != 9:
        return {"label": "FALSIFIED"}
    low = list(x80)
    high = list(x100)
    domain_pass = all(math.isfinite(value) for value in low + high)
    if model == "geometric":
        domain_pass = domain_pass and all(0.0 <= value < 1.0 for value in low + high)
    else:
        domain_pass = domain_pass and all(0.0 < value < 1.0 for value in low + high)
    if not domain_pass:
        return {"label": "FALSIFIED"}
    try:
        transformed_low = [_float_curve_transform(model, value) for value in low]
        transformed_high = [_float_curve_transform(model, value) for value in high]
    except (ValueError, OverflowError, ZeroDivisionError):
        return {"label": "FALSIFIED"}
    if not all(math.isfinite(value) for value in transformed_low + transformed_high):
        return {"label": "FALSIFIED"}
    tau_t = 1.0e-12 + 100.0 * max(
        abs(a - b) for a, b in zip(transformed_low, transformed_high)
    )
    tau_x = 1.0e-10 + 100.0 * max(abs(a - b) for a, b in zip(low, high))
    second_differences = [
        transformed_high[q + 1] - 2.0 * transformed_high[q] + transformed_high[q - 1]
        for q in range(1, 8)
    ]
    fit_q = list(range(6))
    q_mean = 2.5
    t_mean = sum(transformed_high[:6]) / 6.0
    denominator = sum((q - q_mean) ** 2 for q in fit_q)
    slope = sum(
        (q - q_mean) * (transformed_high[q] - t_mean) for q in fit_q
    ) / denominator
    intercept = t_mean - slope * q_mean
    predictions = [_float_curve_inverse(model, intercept + slope * q) for q in range(6, 9)]
    holdout_errors = [
        abs(predictions[index] - high[q]) for index, q in enumerate(range(6, 9))
    ]
    curvature_pass = all(abs(value) <= tau_t for value in second_differences)
    holdout_pass = all(value <= tau_x for value in holdout_errors)
    return {
        "label": "NOT_FALSIFIED_ON_Q0_8" if curvature_pass and holdout_pass else "FALSIFIED",
        "tau_T": tau_t,
        "tau_x": tau_x,
        "transformed_80": transformed_low,
        "transformed_100": transformed_high,
        "second_differences": second_differences,
        "fit_intercept": intercept,
        "fit_slope": slope,
        "holdout_predictions": predictions,
        "holdout_errors": holdout_errors,
    }


def _validate_reported_curve_report(event: dict[str, Any]) -> None:
    """Re-derive rich finite-ladder labels from the bound projection ladder."""

    report = event["curve_report"]
    if "models" not in report:
        return
    primary = event["primary_by_precision"]
    ratios: dict[str, list[float]] = {}
    for text in ("80", "100"):
        result = primary[text]
        energy = float(result["K"])
        if not math.isfinite(energy) or energy == 0.0:
            _fail("curve energy denominator is not finite and nonzero")
        ratios[text] = [float(block["P"]) / energy for block in result["leading_blocks"]]
    for model in ("Gompertz", "geometric", "logistic"):
        row = report["models"][model]
        if not isinstance(row, dict):
            _fail("curve model report is malformed")
        expected_base = {
            "event_id": event["event_id"],
            "model": model,
            "fit_degrees": [0, 1, 2, 3, 4, 5],
            "holdout_degrees": [6, 7, 8],
            "second_difference_indices": [1, 2, 3, 4, 5, 6, 7],
            "only_future_bound": "0<=additional_explainable_energy_beyond_Q8<=K-P8",
        }
        for key, value in expected_base.items():
            if row.get(key) != value:
                _fail("curve model report base fields drift")
        if event["event_id"] == "E00":
            continue
        mine = _float_classify_curve_ladder(
            event["event_id"], model, ratios["80"], ratios["100"]
        )
        if "second_differences" not in row:
            if row.get("label") != "FALSIFIED" or mine["label"] == "NOT_FALSIFIED_ON_Q0_8":
                _fail("curve refusal label disagrees with recomputation")
            continue
        for name in (
            "tau_T", "tau_x", "second_differences", "holdout_errors",
            "transformed_80", "transformed_100", "fit_intercept",
            "fit_slope", "holdout_predictions",
        ):
            if name not in row or name not in mine:
                _fail("curve model report omits recomputable gate evidence")
        second_differences = row["second_differences"]
        holdout_errors = row["holdout_errors"]
        tau_t = row["tau_T"]
        tau_x = row["tau_x"]
        if (
            not isinstance(second_differences, list) or len(second_differences) != 7
            or not isinstance(holdout_errors, list) or len(holdout_errors) != 3
            or not all(
                isinstance(value, float) and math.isfinite(value)
                for value in second_differences + holdout_errors
            )
            or not isinstance(tau_t, float) or not isinstance(tau_x, float)
        ):
            _fail("curve model gate evidence is malformed")
        rule_label = (
            "NOT_FALSIFIED_ON_Q0_8"
            if all(abs(value) <= tau_t for value in second_differences)
            and all(value <= tau_x for value in holdout_errors)
            else "FALSIFIED"
        )
        if row.get("label") != rule_label:
            _fail("curve label disagrees with its own reported gate evidence")
        for name in ("tau_T", "tau_x", "fit_intercept", "fit_slope"):
            if not isinstance(row[name], float) or not _float_close(row[name], mine[name]):
                _fail(f"curve report field is not recomputable: {name}")
        for name in (
            "second_differences", "holdout_errors", "transformed_80",
            "transformed_100", "holdout_predictions",
        ):
            observed_series = row[name]
            expected_series = mine[name]
            if (
                not isinstance(observed_series, list)
                or len(observed_series) != len(expected_series)
                or not all(
                    isinstance(value, float) and _float_close(value, expected)
                    for value, expected in zip(observed_series, expected_series)
                )
            ):
                _fail(f"curve report series is not recomputable: {name}")


def _validate_firewall(payload: Any, label: str = "firewall") -> None:
    row = _exact_keys(payload, FIREWALL_KEYS, label)
    if any(value is not False for value in row.values()):
        _fail(f"{label} is not closed")


def _validate_quadrature_audit(
    payload: Any,
    *,
    engine: str,
    event_id: str,
    dps: int,
) -> int:
    if not isinstance(payload, dict):
        _fail("quadrature audit is not an object")
    common = {
        "all_calls_pass", "error_semantics", "interval_certified", "observed_call_count"
    }
    if not common.issubset(payload):
        _fail("quadrature audit omits its dynamic count/gates")
    if (
        payload["all_calls_pass"] is not True
        or payload["error_semantics"] != "heuristic_diagnostic_estimate_not_interval_certificate"
        or payload["interval_certified"] is not False
        or type(payload["observed_call_count"]) is not int
        or payload["observed_call_count"] <= 0
    ):
        _fail("quadrature audit failed or is a zero-count stub")
    count = payload["observed_call_count"]
    if set(payload) == common:
        # Frozen dummy transport schema.
        if count != 2:
            _fail("dummy quadrature audit count drift")
        return count
    if engine == "primary":
        allowed = common | {
            "outer_call_count", "nested_plackett_call_count", "top_level"
        }
        if set(payload) != allowed:
            _fail("rich primary quadrature audit schema drift")
        outer = payload["outer_call_count"]
        nested = payload["nested_plackett_call_count"]
        if (
            type(outer) is not int or type(nested) is not int
            or outer <= 0 or nested < 0 or outer + nested != count
            or not isinstance(payload["top_level"], list) or not payload["top_level"]
        ):
            _fail("rich primary quadrature counts do not reconcile")
        for row in payload["top_level"]:
            _exact_keys(row, ("quantity", "error_sum", "pass"), "primary top-level audit")
            if not isinstance(row["quantity"], str) or not row["quantity"] or not _finite_number_string(row["error_sum"]) or row["pass"] is not True:
                _fail("primary top-level quadrature gate failed")
    else:
        allowed = common | {
            "cache_scope_id", "nested_raw_error_sum_diagnostic",
            "outer_top_level_error_sums", "unary_panel_count",
        }
        if set(payload) != allowed:
            _fail("rich replica quadrature audit schema drift")
        expected_scope = None
        # Production W replaces R's logical scope with this authoritative one;
        # dummy audits have already returned through the four-key branch.
        for shard_id, events in ASSIGNMENTS.items():
            if event_id in events:
                invocation_index = events.index(event_id) + 1
                expected_scope = f"S{shard_id}:I{invocation_index}:{event_id}:replica:{dps}:fresh"
                break
        if (
            payload["cache_scope_id"] != expected_scope
            or not _finite_number_string(payload["nested_raw_error_sum_diagnostic"])
            or type(payload["unary_panel_count"]) is not int
            or payload["unary_panel_count"] <= 0
            or not isinstance(payload["outer_top_level_error_sums"], dict)
            or not payload["outer_top_level_error_sums"]
            or any(not isinstance(name, str) or not name or not _finite_number_string(value) for name, value in payload["outer_top_level_error_sums"].items())
        ):
            _fail("rich replica quadrature audit scope/count/error drift")
    return count


def _validate_primary(payload: Any, event_id: str, dps: int, fixture_hashes: dict[str, str]) -> int:
    row = _exact_keys(payload, PRIMARY_EVENT_KEYS, "primary precision result")
    if (
        row["artifact"] != "M245_PRIMARY_EVENT_PRECISION"
        or row["schema"] != "m245-primary-event-v1"
        or row["event_id"] != event_id
        or row["precision_dps"] != dps
        or row["fixture_array_sha256"] != fixture_hashes
        or row["degrees"] != list(range(9))
    ):
        _fail("primary identity/schema drift")
    if not isinstance(row["R"], list) or len(row["R"]) != 9 or not all(map(_finite_number_string, row["R"])):
        _fail("primary R is incomplete")
    matrix = row["G"]
    if (
        not isinstance(matrix, list) or len(matrix) != 9
        or any(not isinstance(values, list) or len(values) != 9 for values in matrix)
        or any(not _finite_number_string(value) for values in matrix for value in values)
    ):
        _fail("primary G is incomplete")
    for m in range(9):
        for q in range(9):
            if matrix[m][q] != matrix[q][m]:
                _fail("primary G is not exactly symmetric")
    for key in ("mu_rb", "K"):
        if not _finite_number_string(row[key]):
            _fail(f"primary {key} is not finite")
    if row["K"] == "0":
        _fail("primary K placeholder is forbidden")
    for key in ("d", "beta"):
        if not isinstance(row[key], list) or len(row[key]) != 9 or not all(map(_finite_number_string, row[key])):
            _fail(f"primary {key} is incomplete")
    blocks = row["leading_blocks"]
    block_keys = (
        "Q", "c", "P", "V", "lambda_min", "lambda_max", "lambda_ratio",
        "condition_2", "cholesky_pass", "solve_relative_inf_residual", "solve_pass",
        "energy_gate", "V_beta", "ordinary_beta_identity", "direct_residual",
        "direct_beta_residual",
    )
    if not isinstance(blocks, list) or len(blocks) != 9:
        _fail("primary leading-block ladder is incomplete")
    for q, block_value in enumerate(blocks):
        block = _exact_keys(block_value, block_keys, "primary leading block")
        if block["Q"] != q or not isinstance(block["c"], list) or len(block["c"]) != q + 1:
            _fail("primary leading block degree drift")
        numeric = block["c"] + [block[name] for name in (
            "P", "V", "lambda_min", "lambda_max", "lambda_ratio", "condition_2",
            "solve_relative_inf_residual", "V_beta",
        )]
        if not all(map(_finite_number_string, numeric)) or block["cholesky_pass"] is not True or block["solve_pass"] is not True:
            _fail("primary leading block failed")
        energy = block["energy_gate"]
        if not isinstance(energy, dict) or set(energy) not in (
            {"pass", "tau_K"},
            {"pass", "tau_K", "bounds_pass", "endpoint_control_pass"},
        ):
            _fail("energy gate schema drift")
        if energy["pass"] is not True or not _finite_number_string(energy["tau_K"]):
            _fail("primary energy gate failed")
        if "bounds_pass" in energy and (energy["bounds_pass"] is not True or energy["endpoint_control_pass"] is not True):
            _fail("primary rich energy gate failed")
        identity = block["ordinary_beta_identity"]
        if not isinstance(identity, dict) or set(identity) not in (
            {"lhs", "rhs", "gap", "pass"},
            {"lhs", "rhs", "gap", "pass", "identity_tolerance", "nonnegative_tolerance"},
        ):
            _fail("beta identity schema drift")
        if identity["pass"] is not True or not all(_finite_number_string(identity[name]) for name in ("lhs", "rhs", "gap")):
            _fail("ordinary beta identity failed")
        if "identity_tolerance" in identity and not all(
            _finite_number_string(identity[name])
            for name in ("identity_tolerance", "nonnegative_tolerance")
        ):
            _fail("ordinary beta tolerance is not finite")
        for name in ("direct_residual", "direct_beta_residual"):
            direct = block[name]
            if q in (0, 4, 8):
                direct = _exact_keys(direct, ("observed", "reference", "pass"), name)
                if direct["pass"] is not True or not _finite_number_string(direct["observed"]) or not _finite_number_string(direct["reference"]):
                    _fail(f"{name} failed")
            elif direct is not None:
                _fail(f"{name} appeared outside its frozen ladder points")
    checks = _exact_keys(row["analytic_direct_checks"], ("R", "G_upper", "all_pass"), "analytic checks")
    if checks["all_pass"] is not True or not isinstance(checks["R"], list) or len(checks["R"]) != 9:
        _fail("analytic R checks incomplete")
    for q, check_value in enumerate(checks["R"]):
        check = _exact_keys(check_value, ("q", "analytic", "direct", "pass"), "analytic R check")
        if (
            check["q"] != q or check["pass"] is not True
            or not _direct_check_close(check["analytic"], row["R"][q])
            or not _direct_check_close(check["direct"], row["R"][q])
        ):
            _fail("analytic R check drift")
    if not isinstance(checks["G_upper"], list) or len(checks["G_upper"]) != 45:
        _fail("analytic G upper triangle incomplete")
    expected_pairs = [(m, q) for q in range(9) for m in range(q + 1)]
    for (m, q), check_value in zip(expected_pairs, checks["G_upper"]):
        check = _exact_keys(check_value, ("m", "q", "analytic", "direct", "pass"), "analytic G check")
        if (
            check["m"] != m or check["q"] != q or check["pass"] is not True
            or not _direct_check_close(check["analytic"], matrix[m][q])
            or not _direct_check_close(check["direct"], matrix[m][q])
        ):
            _fail("analytic G check drift")
    count = _validate_quadrature_audit(
        row["quadrature_audit"], engine="primary", event_id=event_id, dps=dps
    )
    if row["firewall"] not in (
        {"network": False},
        {
            "network": False,
            "subprocess": False,
            "retry_or_redraw": False,
            "provider_or_response": False,
        },
    ):
        _fail("primary firewall drift")
    return count


def _validate_replica(payload: Any, event_id: str, dps: int, fixture_hashes: dict[str, str]) -> int:
    row = _exact_keys(payload, REPLICA_EVENT_KEYS, "replica precision result")
    if (
        row["artifact"] != "M245_REPLICA_EVENT_PRECISION"
        or row["schema"] != "m245-replica-event-v1"
        or row["event_id"] != event_id
        or row["precision_dps"] != dps
        or row["fixture_array_sha256"] != fixture_hashes
        or not isinstance(row["fixed_b_nodes"], list) or len(row["fixed_b_nodes"]) != 17
        or not isinstance(row["b_rep_at_nodes"], list) or len(row["b_rep_at_nodes"]) != 17
    ):
        _fail("replica identity/schema or node census drift")
    if not all(_finite_number_string(value) for value in row["fixed_b_nodes"] + row["b_rep_at_nodes"]):
        _fail("replica node table is not finite")
    for name in ("mu_rep", "M_same", "M_cross", "K_rep"):
        if not _finite_number_string(row[name]):
            _fail(f"replica {name} is not finite")
    if row["K_rep"] == "0":
        _fail("replica K placeholder is forbidden")
    count = _validate_quadrature_audit(
        row["quadrature_audit"], engine="replica", event_id=event_id, dps=dps
    )
    if row["firewall"] != {"network": False, "primary_import": False}:
        _fail("replica firewall drift")
    return count


def validate_event_result(payload: Any, *, expected_event_id: str) -> dict[str, Any]:
    event = _exact_keys(payload, EVENT_RESULT_KEYS, "event result")
    if not isinstance(expected_event_id, str) or not expected_event_id or event["event_id"] != expected_event_id:
        _fail("event result identity drift")
    fixture = _exact_keys(event["fixture_array_sha256"], ("C", "mu"), "fixture hash binding")
    if any(not _valid_hash(value) for value in fixture.values()):
        _fail("fixture arrays are not hash-bound")
    primary = _exact_keys(event["primary_by_precision"], ("80", "100"), "primary precision union")
    replica = _exact_keys(event["replica_by_precision"], ("80", "100"), "replica precision union")
    audit_counts: dict[tuple[str, int], int] = {}
    for text, dps in (("80", 80), ("100", 100)):
        audit_counts[("primary", dps)] = _validate_primary(
            primary[text], expected_event_id, dps, fixture
        )
        audit_counts[("replica", dps)] = _validate_replica(
            replica[text], expected_event_id, dps, fixture
        )
    for name in ("cross_precision_gates", "primary_replica_gates", "analytic_solve_energy_beta_gates"):
        if not isinstance(event[name], dict) or event[name].get("pass") is not True:
            _fail(f"{name} failed")
    cross_gates = event["cross_precision_gates"]
    if set(cross_gates) != {"pass"}:
        cross_gates = _exact_keys(cross_gates, ("checks", "pass"), "rich cross-precision gates")
        expected_cross_checks = {
            "primary_mu_K", "primary_R", "primary_G", "primary_d", "primary_beta",
            "primary_blocks", "replica_integrated", "replica_all_fixed_nodes",
            "primary_all_fixed_nodes",
        }
        if (
            not isinstance(cross_gates["checks"], dict)
            or set(cross_gates["checks"]) != expected_cross_checks
            or any(value is not True for value in cross_gates["checks"].values())
        ):
            _fail("rich cross-precision gate census failed")
    integrated_gates = event["primary_replica_gates"]
    if set(integrated_gates) != {"pass"}:
        integrated_gates = _exact_keys(
            integrated_gates, ("by_precision", "pass"), "rich primary/replica gates"
        )
        by_precision = _exact_keys(
            integrated_gates["by_precision"], ("80", "100"),
            "primary/replica precision gates",
        )
        for text in ("80", "100"):
            gate = _exact_keys(
                by_precision[text],
                ("mu_pass", "K_pass", "pass", "mu_tolerance", "K_tolerance",
                 "node_gates", "nodes_pass"),
                "integrated precision gate",
            )
            replica_row = replica[text]
            if (
                gate["mu_pass"] is not True or gate["K_pass"] is not True
                or gate["nodes_pass"] is not True or gate["pass"] is not True
                or not _finite_scientific_scalar(gate["mu_tolerance"])
                or not _finite_scientific_scalar(gate["K_tolerance"])
                or not isinstance(gate["node_gates"], list)
                or len(gate["node_gates"]) != 17
            ):
                _fail("integrated primary/replica precision gate failed")
            for index, node_gate_value in enumerate(gate["node_gates"]):
                node_gate = _exact_keys(
                    node_gate_value, ("node", "primary", "replica", "pass"),
                    "primary/replica node gate",
                )
                if (
                    node_gate["node"] != replica_row["fixed_b_nodes"][index]
                    or node_gate["replica"] != replica_row["b_rep_at_nodes"][index]
                    or not _finite_number_string(node_gate["primary"])
                    or node_gate["pass"] is not True
                ):
                    _fail("primary/replica fixed-node gate drift")
    report = event["curve_report"]
    if isinstance(report, dict) and set(report) == {"labels", "models"}:
        models = _exact_keys(report["models"], ("Gompertz", "geometric", "logistic"), "curve models")
        if any(not isinstance(value, dict) or value.get("label") not in (
            "ENDPOINT_CONTROL/NA", "FALSIFIED", "NOT_FALSIFIED_ON_Q0_8"
        ) for value in models.values()):
            _fail("rich curve report is malformed")
    elif not isinstance(report, dict) or set(report) != {"labels"}:
        _fail("curve report schema drift")
    labels = _exact_keys(report["labels"], ("Gompertz", "geometric", "logistic"), "curve labels")
    expected_label = "ENDPOINT_CONTROL/NA" if expected_event_id == "E00" else "FALSIFIED"
    if "models" in report:
        if labels != {name: report["models"][name]["label"] for name in ("Gompertz", "geometric", "logistic")}:
            _fail("rich finite-ladder labels do not match their reports")
    elif labels != {"Gompertz": expected_label, "geometric": expected_label, "logistic": expected_label}:
        _fail("finite-ladder labels drift")
    refs = event["quad_gateway_ledger_refs"]
    if not isinstance(refs, list) or len(refs) != 4:
        _fail("quadrature ledger reference census drift")
    expected_pairs = [(engine, dps) for engine in ("primary", "replica") for dps in (80, 100)]
    for (engine, dps), ref_value in zip(expected_pairs, refs):
        ref = _exact_keys(ref_value, ("count", "engine", "precision_dps", "sha256"), "ledger reference")
        if (
            ref["count"] != audit_counts[(engine, dps)]
            or ref["engine"] != engine
            or ref["precision_dps"] != dps
            or not _valid_hash(ref["sha256"])
        ):
            _fail("quadrature ledger reference drift")
    if event["only_future_bound"] != "0<=additional_explainable_energy_beyond_Q8<=K-P8":
        _fail("uncertified future extrapolation")
    if event["gate_verdict"] != "PASS" or event["forbidden_credit"] is not True:
        _fail("event gate or forbidden-credit firewall failed")
    _validate_firewall(event["firewall"], "event firewall")
    return event


_OBSERVATION_KEYS = (
    "alive", "creation_filetime", "current_working_set_bytes", "exit_code",
    "image_sha256", "kernel_time_100ns", "peak_working_set_bytes", "pid",
    "state", "user_time_100ns",
)


def _validate_meter_stream(
    meter: Any,
    *,
    outer: bool,
) -> tuple[list[dict[str, Any]], float, int]:
    if outer:
        top_keys = (
            "artifact", "invocation_index", "milestones", "o_process_creation_filetime",
            "qpc_clock_id", "qpc_frequency", "samples", "schema", "terminal_endpoint_filetime",
        )
        artifact, schema, role_names = "M245_OUTER_RAW_METER", "m245-outer-raw-meter-v1", ("O", "S")
    else:
        top_keys = (
            "artifact", "job_process_events", "milestones", "qpc_clock_id", "qpc_frequency",
            "s_process_creation_filetime", "samples", "schema", "scientific_stop_filetime",
            "terminal_child_exit_filetime",
        )
        artifact, schema, role_names = "M245_SHARD_RAW_METER", "m245-shard-raw-meter-v1", ("S", "L", "W")
    row = _exact_keys(meter, top_keys, "outer meter" if outer else "inner meter")
    if row["artifact"] != artifact or row["schema"] != schema:
        _fail("raw meter artifact/schema drift")
    frequency = row["qpc_frequency"]
    if type(frequency) is not int or frequency <= 0 or not isinstance(row["qpc_clock_id"], str) or not row["qpc_clock_id"]:
        _fail("invalid QPC domain")
    clock_id = row["qpc_clock_id"]
    if clock_id == "DUMMY_SHARED_QPC_CLOCK_DOMAIN":
        if frequency != 10_000_000:
            _fail("dummy QPC frequency drift")
    elif (
        frequency != _QPC_FREQUENCY
        or not clock_id.startswith("M245_QPC_")
        or not _valid_hash(clock_id[len("M245_QPC_"):])
    ):
        _fail("production QPC clock/frequency identity drift")
    samples = row["samples"]
    if not isinstance(samples, list) or len(samples) < 2:
        _fail("raw meter sampling ladder is incomplete")
    previous_tick: int | None = None
    max_gap = 0.0
    offsets: set[int] = set()
    identities: dict[str, tuple[int, int] | None] = {role: None for role in role_names}
    counters: dict[str, tuple[int, int, int]] = {}
    for index, sample_value in enumerate(samples):
        sample = _exact_keys(
            sample_value,
            ("qpc_frequency", "qpc_clock_id", "qpc_tick", "roles", "sample_index", "utc_filetime"),
            "meter sample",
        )
        if sample["sample_index"] != index or sample["qpc_frequency"] != frequency or sample["qpc_clock_id"] != row["qpc_clock_id"]:
            _fail("meter sample index/domain drift")
        tick = sample["qpc_tick"]
        if type(tick) is not int or (previous_tick is not None and tick <= previous_tick):
            _fail("meter QPC ticks are not strictly increasing")
        if previous_tick is not None:
            gap = Fraction(tick - previous_tick, frequency)
            if gap > Fraction(1, 10):
                _fail("meter sampling gap exceeds 0.1 seconds")
            max_gap = max(max_gap, float(gap))
        previous_tick = tick
        if type(sample["utc_filetime"]) is not int:
            _fail("meter FILETIME is not integral")
        offsets.add(sample["utc_filetime"] - tick * 10_000_000 // frequency)
        roles = _exact_keys(sample["roles"], role_names, "meter role census")
        for role, observation_value in roles.items():
            observation = _exact_keys(observation_value, _OBSERVATION_KEYS, "meter observation")
            state = observation["state"]
            if state not in ("NOT_CREATED", "ALIVE", "EXITED") or observation["alive"] is not (state == "ALIVE"):
                _fail("meter process state drift")
            for key in ("current_working_set_bytes", "peak_working_set_bytes", "kernel_time_100ns", "user_time_100ns"):
                if type(observation[key]) is not int or observation[key] < 0:
                    _fail("negative or non-integral process counter")
            if observation["current_working_set_bytes"] > observation["peak_working_set_bytes"]:
                _fail("current RSS exceeds lifetime peak")
            if state == "NOT_CREATED":
                if any(observation[key] is not None for key in ("pid", "creation_filetime", "image_sha256", "exit_code")):
                    _fail("not-created process carries identity")
                if any(observation[key] != 0 for key in ("current_working_set_bytes", "peak_working_set_bytes", "kernel_time_100ns", "user_time_100ns")):
                    _fail("not-created process carries counters")
                continue
            if type(observation["pid"]) is not int or type(observation["creation_filetime"]) is not int or not _valid_hash(observation["image_sha256"]):
                _fail("created process lacks an immutable identity")
            if clock_id != "DUMMY_SHARED_QPC_CLOCK_DOMAIN":
                expected_image_hash = (
                    VENV_PYTHON_SHA256 if role == "L" else STDLIB_PYTHON_SHA256
                )
                if observation["image_sha256"] != expected_image_hash:
                    _fail(f"{role} meter image hash is not role-exact")
            identity = (observation["pid"], observation["creation_filetime"])
            if identities[role] is not None and identities[role] != identity:
                _fail("process identity changed within meter")
            identities[role] = identity
            if state == "ALIVE" and observation["exit_code"] is not None:
                _fail("alive process has an exit code")
            if state == "EXITED" and type(observation["exit_code"]) is not int:
                _fail("exited process lacks an exit code")
            now = (observation["kernel_time_100ns"], observation["user_time_100ns"], observation["peak_working_set_bytes"])
            if role in counters and any(new < old for new, old in zip(now, counters[role])):
                _fail("resource counter rollback")
            counters[role] = now
    if len(offsets) != 1 or any(identity is None for identity in identities.values()):
        _fail("raw meter clock or process identity is incomplete")
    if outer:
        if (
            row["o_process_creation_filetime"] != identities["O"][1]
            or type(row["terminal_endpoint_filetime"]) is not int
            or row["terminal_endpoint_filetime"] < samples[-1]["utc_filetime"]
        ):
            _fail("outer retained creation/terminal FILETIME drift")
        if (
            samples[0]["roles"]["S"]["state"] != "NOT_CREATED"
            or samples[-1]["roles"]["S"]["state"] != "EXITED"
        ):
            _fail("outer S retained pre-spawn/terminal boundary drift")
        milestones = _exact_keys(
            row["milestones"],
            ("final_shard_publication_verified_qpc_tick", "s_exit_qpc_tick", "s_spawn_qpc_tick", "stream_closed_qpc_tick"),
            "outer milestones",
        )
        if row["invocation_index"] not in (1, 2):
            _fail("outer meter invocation drift")
        final_tick = milestones["final_shard_publication_verified_qpc_tick"]
        if row["qpc_clock_id"] == "DUMMY_SHARED_QPC_CLOCK_DOMAIN":
            final_valid = final_tick == (None if row["invocation_index"] == 1 else 2_200_000)
        else:
            final_valid = (
                final_tick is None if row["invocation_index"] == 1
                else type(final_tick) is int
            )
        if (
            not final_valid
            or not milestones["s_spawn_qpc_tick"] < milestones["s_exit_qpc_tick"] < milestones["stream_closed_qpc_tick"]
            or (
                clock_id != "DUMMY_SHARED_QPC_CLOCK_DOMAIN"
                and not samples[0]["qpc_tick"] < milestones["s_spawn_qpc_tick"]
            )
            or (
                row["invocation_index"] == 2
                and not milestones["s_exit_qpc_tick"] < final_tick < milestones["stream_closed_qpc_tick"]
            )
        ):
            _fail("outer milestone order drift")
    else:
        if (
            row["s_process_creation_filetime"] != identities["S"][1]
            or type(row["scientific_stop_filetime"]) is not int
            or type(row["terminal_child_exit_filetime"]) is not int
            or not row["s_process_creation_filetime"]
            <= row["scientific_stop_filetime"]
            <= row["terminal_child_exit_filetime"]
        ):
            _fail("inner retained creation/science/terminal FILETIME drift")
        if samples[0]["roles"]["L"]["state"] != "NOT_CREATED" or samples[0]["roles"]["W"]["state"] != "NOT_CREATED":
            _fail("inner meter did not begin before L/W creation")
        if samples[-1]["roles"]["L"]["state"] != "EXITED" or samples[-1]["roles"]["W"]["state"] != "EXITED":
            _fail("inner meter did not retain L/W through exit")
        milestones = _exact_keys(
            row["milestones"],
            ("checkpoint_publication_verified_qpc_tick", "done_received_qpc_tick", "exit_released_qpc_tick",
             "launcher_exit_qpc_tick", "result_publication_verified_qpc_tick", "stream_closed_qpc_tick", "worker_exit_qpc_tick"),
            "inner milestones",
        )
        if not (
            milestones["result_publication_verified_qpc_tick"]
            < milestones["checkpoint_publication_verified_qpc_tick"]
            < milestones["done_received_qpc_tick"]
            < milestones["exit_released_qpc_tick"]
            <= milestones["worker_exit_qpc_tick"]
            <= milestones["launcher_exit_qpc_tick"]
            < milestones["stream_closed_qpc_tick"]
        ):
            _fail("inner milestone order drift")
        events = row["job_process_events"]
        if not isinstance(events, list) or len(events) != 4:
            _fail("job process event census drift")
        expected_job_events = (
            ("NEW_PROCESS", "L"), ("NEW_PROCESS", "W"),
            ("EXIT_PROCESS", "W"), ("EXIT_PROCESS", "L"),
        )
        prior_event_tick = None
        for event, (expected_event, expected_role) in zip(events, expected_job_events):
            _exact_keys(event, ("creation_filetime", "event", "pid", "qpc_tick", "role"), "job process event")
            identity = identities[expected_role]
            if (
                event["event"] != expected_event or event["role"] != expected_role
                or identity is None
                or (event["pid"], event["creation_filetime"]) != identity
                or type(event["qpc_tick"]) is not int
                or (prior_event_tick is not None and event["qpc_tick"] <= prior_event_tick)
            ):
                _fail("job process event identity/order drift")
            prior_event_tick = event["qpc_tick"]
    return samples, max_gap, next(iter(offsets))


def _resource_meter_from_raw(meter: Any) -> dict[str, Any]:
    samples, max_gap, _offset = _validate_meter_stream(meter, outer=False)
    return _resource_meter_reductions(meter, samples, max_gap)


def _resource_meter_reductions(
    meter: Any,
    samples: list[dict[str, Any]],
    max_gap: float,
) -> dict[str, Any]:
    """Pure arithmetic reduction of an already-frozen raw stream (no gates)."""

    frequency = meter["qpc_frequency"]
    final_roles = samples[-1]["roles"]
    cpu = {
        role: final_roles[role]["kernel_time_100ns"] + final_roles[role]["user_time_100ns"]
        for role in ("S", "L", "W")
    }
    sampled = max(
        sum(observation["current_working_set_bytes"] for observation in sample["roles"].values() if observation["state"] == "ALIVE")
        for sample in samples
    )
    lifetime_peak = sum(
        max(sample["roles"][role]["peak_working_set_bytes"] for sample in samples)
        for role in ("S", "L", "W")
    )
    return {
        "charged_process_roles": ["S", "L", "W"],
        "cpu_100ns_by_role": cpu,
        "cpu_seconds_sum": sum(cpu.values()) / 10_000_000,
        "endpoint_qpc_tick": samples[-1]["qpc_tick"],
        "full_wall_seconds": (meter["terminal_child_exit_filetime"] - meter["s_process_creation_filetime"]) / 10_000_000,
        "lifetime_peak_upper_bytes": lifetime_peak,
        "max_observed_sampling_gap_seconds": max_gap,
        "max_sampled_concurrent_working_set_bytes": sampled,
        "qpc_frequency": frequency,
        "rss_gate_bytes": max(sampled, lifetime_peak),
        "sample_count": len(samples),
        "s_process_creation_filetime": meter["s_process_creation_filetime"],
        "scientific_stop_qpc_tick": (
            1_300_000
            if meter["qpc_clock_id"] == "DUMMY_SHARED_QPC_CLOCK_DOMAIN"
            else (
                samples[0]["qpc_tick"]
                + (meter["scientific_stop_filetime"] - samples[0]["utc_filetime"])
                * frequency
                // 10_000_000
            )
        ),
        "scientific_stop_wall_seconds": (meter["scientific_stop_filetime"] - meter["s_process_creation_filetime"]) / 10_000_000,
        "t0_qpc_tick": samples[0]["qpc_tick"],
        "terminal_child_exit_filetime": meter["terminal_child_exit_filetime"],
    }


def _validate_publication(publication: Any, expected_path: str, label: str) -> None:
    row = _exact_keys(
        publication,
        ("bytes", "device", "inode", "path", "reopened_bytes_equal", "sha256",
         "source_final_same_device_inode", "temporary_unlinked"),
        label,
    )
    if (
        type(row["bytes"]) is not int or row["bytes"] <= 0
        or type(row["device"]) is not int or row["device"] < 0
        or type(row["inode"]) is not int or row["inode"] < 0
        or row["path"] != expected_path or not _valid_hash(row["sha256"])
        or row["reopened_bytes_equal"] is not True
        or row["source_final_same_device_inode"] is not True
        or row["temporary_unlinked"] is not True
    ):
        _fail(f"{label} is not an immutable hardlink publication")


def _artifact_binding_path(name: str, *, production: bool) -> str:
    return str((_real_shard_directory() / name).resolve()) if production else name


def _validate_authority_union(authority: Any) -> None:
    expected_keys = AUTHORITY_HASH_KEYS + SCIENTIFIC_SOURCE_HASH_KEYS
    row = _exact_keys(authority, expected_keys, "authority union")
    if any(row[name] != value for name, value in FROZEN_AUTHORITY_SHA256.items()):
        _fail("authority union changed a frozen hash")
    if any(not _valid_hash(row[name]) for name in SCIENTIFIC_SOURCE_HASH_KEYS):
        _fail("authority union lacks a scientific source hash")
    if (
        _EXPECTED_PRODUCTION_AUTHORITY_UNION is not None
        and row != _EXPECTED_PRODUCTION_AUTHORITY_UNION
    ):
        _fail("authority union does not equal the exact current trigger union")


def _validate_identity(row_value: Any, role: str, shard_id: int, invocation_index: int) -> None:
    keys = (
        "argv", "creation_filetime", "cwd", "environment_sha256", "exit_code",
        "handle_acquired_filetime", "image_path", "image_sha256", "job_membership",
        "kernel_time_100ns", "parent_pid", "pid", "retained_handle_through_exit",
        "user_time_100ns",
    )
    row = _exact_keys(row_value, keys, f"{role} process identity")
    if any(type(row[name]) is not int or row[name] < 0 for name in (
        "creation_filetime", "handle_acquired_filetime", "kernel_time_100ns", "parent_pid", "pid", "user_time_100ns"
    )):
        _fail(f"{role} process identity/counters are invalid")
    expected_parent = {"S": 199, "L": 200, "W": 201}[role]
    expected_pid = {"S": 200, "L": 201, "W": 202}[role]
    dummy_identity = row["pid"] == expected_pid
    if dummy_identity and row["parent_pid"] != expected_parent:
        _fail(f"{role} process tree drift")
    if not dummy_identity and (row["pid"] <= 0 or row["parent_pid"] <= 0):
        _fail(f"{role} production process identity is invalid")
    worker = str((HERE / "m245_scientific_worker.py").resolve())
    runner = str((HERE / "run_m245_scientific_shard.py").resolve())
    expected_argv = {
        "S": [STDLIB_PYTHON, "-I", "-B", "-S", "-u", runner, "--shard-id", str(shard_id), "--invocation-index", str(invocation_index)],
        "L": [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker],
        "W": [worker],
    }[role]
    expected_image = VENV_PYTHON if role == "L" else STDLIB_PYTHON
    expected_image_hash = VENV_PYTHON_SHA256 if role == "L" else STDLIB_PYTHON_SHA256
    if (
        row["argv"] != expected_argv or row["cwd"] != AUTHORITY_CWD
        or not _valid_hash(row["environment_sha256"])
        or row["exit_code"] != 0 or row["image_path"] != expected_image
        or row["image_sha256"] != expected_image_hash
        or row["job_membership"] is not (role in ("L", "W"))
        or row["retained_handle_through_exit"] is not True
    ):
        _fail(f"{role} process identity metadata drift")


def validate_invocation_receipt(
    receipt_value: Any,
    raw_meter: Any,
    event_result: Any | None = None,
) -> dict[str, Any]:
    receipt = _exact_keys(receipt_value, INVOCATION_RECEIPT_KEYS, "invocation receipt")
    shard_id, invocation_index = receipt.get("shard_id"), receipt.get("invocation_index")
    if shard_id not in ASSIGNMENTS or invocation_index not in (1, 2):
        _fail("invocation receipt identity drift")
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    namespace = shard_namespace(shard_id, invocation_index)
    if (
        receipt["artifact"] != "M245_SHARD_INVOCATION_RECEIPT"
        or receipt["schema"] != "m245-shard-invocation-receipt-v1"
        or receipt["event_id"] != event_id
        or receipt["status"] != "PROVISIONAL_INNER_RECEIPT_NO_INVOCATION_PASS"
        or receipt["no_retry"] is not True
        or receipt["stderr_empty"] is not True
        or receipt["stdout_records"] != ["M245_W_READY", "M245_W_DONE"]
    ):
        _fail("invocation receipt schema/status drift")
    _validate_authority_union(receipt["authority_sha256"])
    _validate_firewall(receipt["firewall"])
    child = _exact_keys(
        receipt["child_environment"],
        ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"),
        "child environment",
    )
    if any(value != "1" for value in child.values()) or not _valid_hash(receipt["child_environment_sha256"]):
        _fail("child thread environment drift")
    intent_path_value = (
        receipt["intent_publication"].get("path")
        if isinstance(receipt["intent_publication"], dict) else None
    )
    production_paths = (
        isinstance(intent_path_value, str) and Path(intent_path_value).is_absolute()
    )
    for kind in ("intent", "result", "checkpoint", "meter"):
        _validate_publication(
            receipt[f"{kind}_publication"],
            _artifact_binding_path(namespace[kind], production=production_paths),
            f"{kind} publication",
        )
    if receipt["meter_publication"]["sha256"] != _sha256_bytes(_canonical_json_bytes(raw_meter)):
        _fail("meter publication is not bound to raw meter bytes")
    path_state = _exact_keys(
        receipt["path_state"],
        ("all_current_paths_initially_absent", "all_prior_paths_exact", "no_unlisted_write", "temporary_paths_absent_after_publication"),
        "path state",
    )
    if path_state != {
        "all_current_paths_initially_absent": True,
        "all_prior_paths_exact": invocation_index == 2,
        "no_unlisted_write": True,
        "temporary_paths_absent_after_publication": True,
    }:
        _fail("invocation path-state drift")
    prior = receipt["prior_invocation_files"]
    if invocation_index == 1:
        if prior is not None:
            _fail("first invocation carries predecessor files")
    else:
        if not isinstance(prior, list) or len(prior) != 4:
            _fail("second invocation predecessor census drift")
        expected_kinds = ("result", "checkpoint", "meter", "invocation_receipt")
        prior_namespace = shard_namespace(shard_id, 1)
        for kind, binding_value in zip(expected_kinds, prior):
            binding = _exact_keys(
                binding_value,
                ("bytes", "device", "event_id", "file_kind", "inode", "path", "sha256"),
                "prior invocation binding",
            )
            if (
                binding["file_kind"] != kind or binding["event_id"] != ASSIGNMENTS[shard_id][0]
                or binding["path"] != _artifact_binding_path(
                    prior_namespace[kind], production=production_paths
                ) or type(binding["bytes"]) is not int
                or binding["bytes"] <= 0 or type(binding["device"]) is not int
                or type(binding["inode"]) is not int or not _valid_hash(binding["sha256"])
            ):
                _fail("prior invocation binding drift")
    identities = _exact_keys(receipt["process_identities"], ("S", "L", "W"), "process identities")
    for role in ("S", "L", "W"):
        _validate_identity(identities[role], role, shard_id, invocation_index)
    meter_samples, _meter_gap, _meter_offset = _validate_meter_stream(
        raw_meter, outer=False
    )
    final_meter_roles = meter_samples[-1]["roles"]
    for role in ("S", "L", "W"):
        observation = final_meter_roles[role]
        identity = identities[role]
        if (
            identity["pid"] != observation["pid"]
            or identity["creation_filetime"] != observation["creation_filetime"]
            or identity["image_sha256"] != observation["image_sha256"]
            or (
                role in ("L", "W")
                and (
                    identity["exit_code"] != observation["exit_code"]
                    # Exact CPU-counter equality with the final raw sample is a
                    # production binding (sealed after exit); the frozen dummy
                    # fixtures carry synthetic counters, on the same absolute-
                    # path axis O uses for its outer-meter identity checks.
                    or (
                        production_paths
                        and (
                            identity["kernel_time_100ns"] != observation["kernel_time_100ns"]
                            or identity["user_time_100ns"] != observation["user_time_100ns"]
                        )
                    )
                )
            )
            or (
                role == "S"
                and (
                    identity["kernel_time_100ns"] < observation["kernel_time_100ns"]
                    or identity["user_time_100ns"] < observation["user_time_100ns"]
                )
            )
        ):
            _fail(f"{role} receipt identity disagrees with the retained raw meter")
    if identities["L"]["parent_pid"] != identities["S"]["pid"] or identities["W"]["parent_pid"] != identities["L"]["pid"]:
        _fail("S/L/W process chain drift")
    census = _exact_keys(
        receipt["job_census"],
        ("active_process_limit", "distinct_job_pids", "job_roles", "total_processes", "worker_children"),
        "job census",
    )
    if census != {
        "active_process_limit": 2,
        "distinct_job_pids": [identities["L"]["pid"], identities["W"]["pid"]],
        "job_roles": ["L", "W"],
        "total_processes": 2,
        "worker_children": 0,
    }:
        _fail("job census drift")
    ledger_summary = validate_quad_call_ledger(
        receipt["quad_call_ledger"],
        shard_id=shard_id,
        invocation_index=invocation_index,
        event_id=event_id,
        _return_internal_aggregates=event_result is not None,
    )
    if event_result is not None:
        validated_event = validate_event_result(event_result, expected_event_id=event_id)
        _validate_scientific_ledger_bindings(validated_event, ledger_summary)
    if receipt["quad_call_ledger_sha256"] != _sha256_bytes(_canonical_json_bytes(receipt["quad_call_ledger"])):
        _fail("quadrature ledger hash drift")
    gateway = _exact_keys(
        receipt["quad_gateway"],
        ("actual_mp_quad_call_count", "all_calls_pass", "cache_hit_count", "completion_request_order",
         "gateway_source_sha256", "nested_call_count", "outer_call_count",
         "outer_panel_error_sums_mpf", "request_count"),
        "quad gateway summary",
    )
    expected_gateway = {
        "actual_mp_quad_call_count": ledger_summary["actual_mp_quad_call_count"],
        "all_calls_pass": True,
        "cache_hit_count": ledger_summary["cache_hit_count"],
        "completion_request_order": ledger_summary["completion_request_order"],
        "nested_call_count": ledger_summary["nested_call_count"],
        "outer_call_count": ledger_summary["outer_call_count"],
        "outer_panel_error_sums_mpf": ledger_summary["outer_panel_error_sums_mpf"],
        "request_count": ledger_summary["request_count"],
    }
    if (
        not _valid_hash(gateway["gateway_source_sha256"])
        or (
            production_paths
            and gateway["gateway_source_sha256"]
            != receipt["authority_sha256"]["m245_scientific_worker.py"]
        )
    ):
        _fail("quad gateway source is not exactly trigger-bound")
    for key, value in expected_gateway.items():
        if gateway[key] != value:
            _fail(f"quad gateway summary drift: {key}")
    expected_resource = _resource_meter_from_raw(raw_meter)
    _exact_keys(receipt["resource_meter"], RESOURCE_METER_KEYS, "resource meter")
    if receipt["resource_meter"] != expected_resource:
        _fail("resource meter is not exactly derived from raw samples")
    if (
        expected_resource["full_wall_seconds"] > 5400
        or expected_resource["scientific_stop_wall_seconds"] > 5100
        or expected_resource["rss_gate_bytes"] > 2_147_483_648
        or expected_resource["max_observed_sampling_gap_seconds"] > 0.1
    ):
        _fail("invocation resource cap exceeded")
    return receipt


_INTENT_NAME = re.compile(r"^M245_S\d+_I\d+_E\d+_INTENT_20260810\.json$")


def _read_json_file(path: Path, label: str) -> Any:
    try:
        raw, _identity = _secure_regular_bytes(path, label)
        if not raw or _canonical_json_bytes(json.loads(raw.decode("utf-8"))) != raw:
            _fail(f"{label} is not canonical JSON")
        return json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"cannot read {label}: {exc}")


def _outer_validator_module() -> Any:
    existing = sys.modules.get("launch_m245_scientific_invocation")
    if existing is not None:
        return existing
    runner_existing = sys.modules.get("run_m245_scientific_shard")
    if runner_existing is None:
        sys.modules["run_m245_scientific_shard"] = sys.modules[__name__]
    elif runner_existing is not sys.modules[__name__]:
        _fail("outer validator would bind a different supervisor module")
    source = HERE / "launch_m245_scientific_invocation.py"
    source_raw, _source_identity = _secure_regular_bytes(
        source, "retained outer validator source"
    )
    if (
        _EXPECTED_OUTER_VALIDATOR_SHA256 is not None
        and _sha256_bytes(source_raw) != _EXPECTED_OUTER_VALIDATOR_SHA256
    ):
        _fail("retained outer validator source is not trigger-bound")
    spec = importlib.util.spec_from_file_location(
        "launch_m245_scientific_invocation", source
    )
    if spec is None or spec.loader is None:
        _fail("cannot create outer validator module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules["launch_m245_scientific_invocation"] = module
    try:
        code = compile(source_raw, str(source), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop("launch_m245_scientific_invocation", None)
        raise
    if (
        _EXPECTED_OUTER_VALIDATOR_SHA256 is not None
        and _sha256_bytes(
            _secure_regular_bytes(source, "outer validator post-load")[0]
        ) != _EXPECTED_OUTER_VALIDATOR_SHA256
    ):
        _fail("outer validator source changed after retained execution")
    return module


def preflight_invocation_paths(
    shard_directory: os.PathLike[str] | str,
    *,
    shard_id: int,
    invocation_index: int,
) -> dict[str, Any]:
    validate_shard_request(shard_id, ASSIGNMENTS.get(shard_id, ()), invocation_index, invocation_index == 2)
    root = Path(shard_directory)
    try:
        root_stat = os.lstat(root)
    except OSError:
        _fail("shard directory does not exist")
    if not stat.S_ISDIR(root_stat.st_mode) or getattr(root_stat, "st_file_attributes", 0) & 0x400:
        _fail("shard directory is not a regular non-reparse directory")
    real_shard_root = root.resolve() == (
        HERE.parents[3] / SHARD_DIRECTORY_REPO_RELATIVE
    ).resolve()
    namespace = shard_namespace(shard_id, invocation_index)
    for key, name in namespace.items():
        if key == "directory_repo_relative":
            continue
        try:
            os.lstat(root / name)
        except FileNotFoundError:
            continue
        else:
            _fail("target invocation namespace is not absent")
    expected_names = set(_ordered_intent_paths())
    # E2.5 requires an exact global ownership census: every directory entry
    # must be a durable member of some pair's namespace, temporaries are
    # always refusal, and no non-intent artifact may exist without its
    # burned durable intent.
    owner_by_name: dict[str, tuple[int, int, str]] = {}
    temporary_names: set[str] = set()
    for census_shard in ASSIGNMENTS:
        for census_invocation in (1, 2):
            census_namespace = shard_namespace(census_shard, census_invocation)
            for kind, name in census_namespace.items():
                if kind == "directory_repo_relative":
                    continue
                if kind.endswith("_temp"):
                    temporary_names.add(name)
                elif kind == "final_shard_receipt":
                    owner_by_name[name] = (census_shard, 2, kind)
                else:
                    owner_by_name[name] = (census_shard, census_invocation, kind)
    present: dict[tuple[int, int], dict[str, Any]] = {}
    completed: dict[tuple[int, int], dict[str, Any]] = {}
    trigger_hashes: set[str] = set()
    trigger_commits: set[str] = set()
    try:
        directory_entries = list(os.scandir(root))
    except OSError as exc:
        _fail(f"cannot enumerate shard directory without globbing: {exc}")
    observed_kinds: dict[tuple[int, int], set[str]] = {}
    for directory_entry in directory_entries:
        if not directory_entry.is_file(follow_symlinks=False):
            _fail("shard directory contains a non-regular entry")
        if directory_entry.name in temporary_names:
            _fail("orphan temporary file in the shard namespace")
        owner = owner_by_name.get(directory_entry.name)
        if owner is None:
            _fail("unlisted file lies outside the exact lexical shard census")
        observed_kinds.setdefault((owner[0], owner[1]), set()).add(owner[2])
    for observed_pair_kinds in observed_kinds.values():
        if "intent" not in observed_pair_kinds:
            _fail("shard artifact present without its burned durable intent")
    for directory_entry in directory_entries:
        path = root / directory_entry.name
        if path.name not in expected_names:
            continue
        intent = _read_json_file(path, "present intent")
        intent = _exact_keys(
            intent,
            ("artifact", "schema", "shard_id", "invocation_index", "event_id",
             "trigger_entry_sha256", "trigger_commit", "namespace", "status"),
            "present intent",
        )
        s, i = intent["shard_id"], intent["invocation_index"]
        if s not in ASSIGNMENTS or i not in (1, 2):
            _fail("present intent identity is outside census")
        expected_namespace = shard_namespace(s, i)
        if (
            path.name != expected_namespace["intent"]
            or intent["artifact"] != "M245_SHARD_INVOCATION_INTENT"
            or intent["schema"] != "m245-shard-invocation-intent-v1"
            or intent["event_id"] != ASSIGNMENTS[s][i - 1]
            or intent["namespace"] != expected_namespace
            or intent["status"] != "DURABLE_ATTEMPT_BURNED"
            or not _valid_hash(intent["trigger_entry_sha256"])
            or not _valid_hash(intent["trigger_commit"], 40)
        ):
            _fail("present intent binding drift")
        if (s, i) in present:
            _fail("duplicate present intent")
        present[(s, i)] = intent
        trigger_hashes.add(intent["trigger_entry_sha256"])
        trigger_commits.add(intent["trigger_commit"])
        payloads: dict[str, Any] = {}
        raw_files: dict[str, bytes] = {}
        file_stats: dict[str, os.stat_result] = {}
        for kind in ("result", "checkpoint", "meter", "invocation_receipt", "terminal_witness"):
            artifact_path = root / expected_namespace[kind]
            try:
                raw, identity = _secure_regular_bytes(artifact_path, f"present {kind}")
            except M245ShardContractError:
                _fail("present intent is not a complete immutable attempt")
            try:
                artifact = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                _fail("present attempt contains malformed JSON")
            if raw != _canonical_json_bytes(artifact) or not isinstance(artifact, dict) or not artifact:
                _fail("present attempt contains a placeholder or noncanonical artifact")
            payloads[kind] = artifact
            raw_files[kind] = raw
            file_stats[kind] = identity
        validate_event_result(payloads["result"], expected_event_id=intent["event_id"])
        checkpoint = _exact_keys(
            payloads["checkpoint"],
            ("artifact", "complete_event_id", "next_invocation_only", "schema", "status"),
            "present checkpoint",
        )
        if checkpoint["complete_event_id"] != intent["event_id"] or checkpoint["next_invocation_only"] is not True:
            _fail("present checkpoint event/boundary drift")
        receipt = validate_invocation_receipt(
            payloads["invocation_receipt"], payloads["meter"],
            payloads["result"] if real_shard_root else None,
        )
        if receipt["shard_id"] != s or receipt["invocation_index"] != i or receipt["event_id"] != intent["event_id"]:
            _fail("present receipt identity drift")
        for kind in ("result", "checkpoint", "meter"):
            publication = receipt[f"{kind}_publication"]
            if publication["bytes"] != len(raw_files[kind]) or publication["sha256"] != _sha256_bytes(raw_files[kind]):
                _fail("present inner artifact is not byte-bound by its receipt")
        witness = _exact_keys(payloads["terminal_witness"], (
            "artifact", "schema", "shard_id", "invocation_index", "event_id",
            "authority_sha256", "inner_artifacts", "inner_meter", "prior_invocation_files",
            "outer_meter", "process_identities", "job_census", "s_exit", "resource_meter",
            "final_shard_receipt", "firewall", "status",
        ), "present terminal witness")
        if (
            witness["artifact"] != "M245_OUTER_TERMINAL_INVOCATION_WITNESS"
            or witness["shard_id"] != s or witness["invocation_index"] != i
            or witness["event_id"] != intent["event_id"]
            or witness["authority_sha256"] != receipt["authority_sha256"]
            or witness["inner_meter"] != payloads["meter"]
        ):
            _fail("present terminal witness/inner receipt binding drift")
        inner_bindings = witness["inner_artifacts"]
        if not isinstance(inner_bindings, list) or len(inner_bindings) != 4:
            _fail("terminal witness inner artifact census drift")
        for kind, binding in zip(("result", "checkpoint", "meter"), inner_bindings[:3]):
            publication = receipt[f"{kind}_publication"]
            expected_binding = {
                "bytes": publication["bytes"],
                "device": publication["device"],
                "event_id": receipt["event_id"],
                "file_kind": kind,
                "inode": publication["inode"],
                "invocation_index": i,
                "path": _artifact_binding_path(
                    expected_namespace[kind], production=real_shard_root
                ),
                "sha256": publication["sha256"],
            }
            if binding != expected_binding:
                _fail("terminal witness inner artifact binding drift")
            if real_shard_root and (
                binding["device"], binding["inode"]
            ) != (file_stats[kind].st_dev, file_stats[kind].st_ino):
                _fail("terminal witness inner artifact filesystem identity drift")
        provisional = inner_bindings[3]
        expected_provisional_common = {
            "bytes": len(raw_files["invocation_receipt"]),
            "event_id": receipt["event_id"],
            "file_kind": "provisional_receipt",
            "invocation_index": i,
            "path": _artifact_binding_path(
                expected_namespace["invocation_receipt"], production=real_shard_root
            ),
            "sha256": _sha256_bytes(raw_files["invocation_receipt"]),
        }
        if not isinstance(provisional, dict) or any(
            provisional.get(key) != value for key, value in expected_provisional_common.items()
        ):
            _fail("terminal witness provisional receipt binding drift")
        if real_shard_root and (
            provisional.get("device"), provisional.get("inode")
        ) != (
            file_stats["invocation_receipt"].st_dev,
            file_stats["invocation_receipt"].st_ino,
        ):
            _fail("terminal witness provisional receipt filesystem identity drift")
        expected_status = "PASS_M245_INVOCATION_BOUND" if i == 1 else "PASS_M245_SHARD_BOUND"
        if witness.get("status") != expected_status:
            _fail("present predecessor did not terminate successfully")
        if i == 2:
            try:
                final_raw, final_identity = _secure_regular_bytes(
                    root / expected_namespace["final_shard_receipt"], "present final shard receipt"
                )
                final_payload = json.loads(final_raw.decode("utf-8"))
            except (M245ShardContractError, UnicodeError, json.JSONDecodeError):
                _fail("second invocation lacks its canonical final shard assembly")
            if final_raw != _canonical_json_bytes(final_payload):
                _fail("present final shard receipt is noncanonical")
            completed[(s, i)] = {
                "intent": intent, "payloads": payloads, "raw": raw_files,
                "stats": file_stats, "final": final_payload,
                "final_raw": final_raw, "final_stat": final_identity,
            }
        else:
            completed[(s, i)] = {
                "intent": intent, "payloads": payloads, "raw": raw_files,
                "stats": file_stats,
            }
    if len(trigger_hashes) > 1 or len(trigger_commits) > 1:
        _fail("present intents have mixed trigger lineage")
    if present and (0, 1) not in present:
        _fail("the root predecessor intent is absent")
    for s, i in present:
        if i == 2 and (s, 1) not in present:
            _fail("invocation two exists without invocation one")
        if i == 2:
            first = completed[(s, 1)]
            second = completed[(s, 2)]
            first_receipt = first["payloads"]["invocation_receipt"]
            if second["payloads"]["invocation_receipt"]["prior_invocation_files"] is None:
                _fail("invocation two omits predecessor cross-bindings")
            expected_prior_hash = _sha256_bytes(first["raw"]["invocation_receipt"])
            if second["payloads"]["invocation_receipt"]["prior_invocation_files"][-1].get("sha256") != expected_prior_hash:
                _fail("invocation two predecessor receipt hash drift")
            if first_receipt["event_id"] != ASSIGNMENTS[s][0]:
                _fail("invocation one predecessor event drift")
            first_witness = first["payloads"]["terminal_witness"]
            first_witness_raw = first["raw"]["terminal_witness"]
            expected_prior_terminal_hash = _sha256_bytes(first_witness_raw)
            prior_witness_rows = second["payloads"]["terminal_witness"].get(
                "prior_invocation_files"
            )
            if (
                not isinstance(prior_witness_rows, list)
                or len(prior_witness_rows) != 5
                or prior_witness_rows[:4] != first_witness["inner_artifacts"]
                or prior_witness_rows[-1].get("sha256") != expected_prior_terminal_hash
                or prior_witness_rows[-1].get("status") != "PASS_M245_INVOCATION_BOUND"
            ):
                _fail("invocation two terminal predecessor union drift")
    if invocation_index == 2 and (shard_id, 1) not in present:
        _fail("target invocation two lacks its complete predecessor")
    if completed:
        outer_validator = _outer_validator_module()
        for completed_shard in sorted({key[0] for key in completed}):
            first = completed.get((completed_shard, 1))
            second = completed.get((completed_shard, 2))
            if first is not None:
                outer_validator.validate_terminal_witness(
                    first["payloads"]["terminal_witness"],
                    inner_meter=first["payloads"]["meter"],
                    inner_receipt=first["payloads"]["invocation_receipt"],
                    prior_witness=None,
                    final_shard_receipt=None,
                )
            if second is not None:
                if first is None:
                    _fail("completed second invocation lacks first validator input")
                outer_validator.validate_final_shard_receipt(
                    second["final"],
                    first["payloads"]["invocation_receipt"],
                    second["payloads"]["invocation_receipt"],
                    first["payloads"]["terminal_witness"],
                )
                outer_validator.validate_terminal_witness(
                    second["payloads"]["terminal_witness"],
                    inner_meter=second["payloads"]["meter"],
                    inner_receipt=second["payloads"]["invocation_receipt"],
                    prior_witness=first["payloads"]["terminal_witness"],
                    final_shard_receipt=second["final"],
                )
    return {
        "present_intents": [shard_namespace(s, i)["intent"] for s, i in sorted(present)],
        "target_namespace_absent": True,
        "trigger_entry_sha256": next(iter(trigger_hashes), None),
        "trigger_commit": next(iter(trigger_commits), None),
        "pass": True,
    }


def publish_immutable_json(
    temporary_path: os.PathLike[str] | str,
    final_path: os.PathLike[str] | str,
    payload: object,
    *,
    publication_path: str | None = None,
) -> dict[str, Any]:
    temporary = Path(temporary_path)
    final = Path(final_path)
    if temporary == final or temporary.parent.resolve() != final.parent.resolve():
        _fail("immutable publication requires distinct sibling paths")
    raw = _canonical_json_bytes(payload)
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        reopened_source = temporary.read_bytes()
        if reopened_source != raw:
            _fail("temporary publication bytes changed on reopen")
        os.link(temporary, final)
        source_stat = temporary.stat()
        final_stat = final.stat()
        reopened_final = final.read_bytes()
        if reopened_final != raw:
            _fail("final publication bytes changed on reopen")
        same_identity = (
            source_stat.st_dev == final_stat.st_dev and source_stat.st_ino == final_stat.st_ino
        )
        if not same_identity:
            _fail("publication was not a same-inode hardlink")
        temporary.unlink()
        return {
            "bytes": len(raw),
            "device": final_stat.st_dev,
            "inode": final_stat.st_ino,
            "path": final.name if publication_path is None else publication_path,
            "reopened_bytes_equal": reopened_source == reopened_final == raw,
            "sha256": _sha256_bytes(raw),
            "source_final_same_device_inode": same_identity,
            "temporary_unlinked": not temporary.exists(),
        }
    except M245ShardContractError:
        raise
    except (FileExistsError, OSError) as exc:
        if temporary.exists() and not final.exists():
            try:
                temporary.unlink()
            except OSError:
                pass
        if isinstance(exc, FileExistsError):
            raise
        _fail(f"immutable publication failed: {exc}")


class _FILETIME(ctypes.Structure):
    _fields_ = (("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD))


class _PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = (
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
    )


class _PROCESSENTRY32W(ctypes.Structure):
    _fields_ = (
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
    )


_STILL_ACTIVE = 259
_WAIT_TIMEOUT = 258
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
_PROCESS_ACCESS = 0x00100000 | 0x00001000
_TH32CS_SNAPPROCESS = 0x00000002
_JOB_NEW_PROCESS = 6
_JOB_EXIT_PROCESS = 7
_QPC_FREQUENCY = 1_000_000_000
_SAMPLE_SECONDS = 0.05


def _kernel32() -> Any:
    return ctypes.WinDLL("kernel32", use_last_error=True)


def _filetime_integer(value: _FILETIME) -> int:
    return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)


def _precise_filetime() -> int:
    kernel32 = _kernel32()
    kernel32.GetSystemTimePreciseAsFileTime.argtypes = [ctypes.POINTER(_FILETIME)]
    kernel32.GetSystemTimePreciseAsFileTime.restype = None
    value = _FILETIME()
    kernel32.GetSystemTimePreciseAsFileTime(ctypes.byref(value))
    result = _filetime_integer(value)
    if result <= 0:
        raise OSError(ctypes.get_last_error(), "GetSystemTimePreciseAsFileTime failed")
    return result


def _close_process_handle(handle: int | None) -> None:
    if handle:
        kernel32 = _kernel32()
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        if not kernel32.CloseHandle(handle):
            raise OSError(ctypes.get_last_error(), "CloseHandle failed")


def _open_process_handle(pid: int) -> tuple[int, int]:
    kernel32 = _kernel32()
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    handle = kernel32.OpenProcess(_PROCESS_ACCESS, False, pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), f"OpenProcess failed for pid {pid}")
    return int(handle), _precise_filetime()


def _process_times(handle: int) -> dict[str, int]:
    kernel32 = _kernel32()
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    creation, exit_time, kernel, user = (_FILETIME() for _ in range(4))
    if not kernel32.GetProcessTimes(
        handle, ctypes.byref(creation), ctypes.byref(exit_time),
        ctypes.byref(kernel), ctypes.byref(user),
    ):
        raise OSError(ctypes.get_last_error(), "GetProcessTimes failed")
    return {
        "creation_filetime": _filetime_integer(creation),
        "exit_filetime": _filetime_integer(exit_time),
        "kernel_time_100ns": _filetime_integer(kernel),
        "user_time_100ns": _filetime_integer(user),
    }


def _process_exit_code(handle: int) -> int:
    kernel32 = _kernel32()
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    code = wintypes.DWORD()
    if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
        raise OSError(ctypes.get_last_error(), "GetExitCodeProcess failed")
    return int(code.value)


def _process_memory(handle: int) -> tuple[int, int]:
    if _process_exit_code(handle) != _STILL_ACTIVE:
        return 0, 0
    kernel32 = _kernel32()
    kernel32.K32GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(_PROCESS_MEMORY_COUNTERS), wintypes.DWORD,
    ]
    kernel32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = _PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    if not kernel32.K32GetProcessMemoryInfo(
        handle, ctypes.byref(counters), ctypes.sizeof(counters)
    ):
        if _process_exit_code(handle) != _STILL_ACTIVE:
            return 0, 0
        raise OSError(ctypes.get_last_error(), "K32GetProcessMemoryInfo failed")
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


def _process_image_path(handle: int) -> str:
    kernel32 = _kernel32()
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    size = wintypes.DWORD(32768)
    buffer = ctypes.create_unicode_buffer(size.value)
    if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
        raise OSError(ctypes.get_last_error(), "QueryFullProcessImageNameW failed")
    return buffer.value


def _process_in_job(handle: int, job: int) -> bool:
    kernel32 = _kernel32()
    kernel32.IsProcessInJob.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL),
    ]
    kernel32.IsProcessInJob.restype = wintypes.BOOL
    answer = wintypes.BOOL()
    if not kernel32.IsProcessInJob(handle, job, ctypes.byref(answer)):
        raise OSError(ctypes.get_last_error(), "IsProcessInJob failed")
    return bool(answer.value)


def _process_parents() -> dict[int, int]:
    kernel32 = _kernel32()
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    kernel32.Process32FirstW.restype = wintypes.BOOL
    kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    kernel32.Process32NextW.restype = wintypes.BOOL
    snapshot = kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
    if int(snapshot) == _INVALID_HANDLE_VALUE:
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")
    result: dict[int, int] = {}
    try:
        entry = _PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        present = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while present:
            result[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
            present = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        _close_process_handle(int(snapshot))
    return result


class _ProcessSampler:
    """Retained-handle QPC sampler used by both real S and real O."""

    def __init__(
        self,
        roles: tuple[str, ...],
        *,
        qpc_clock_id: str,
        qpc_filetime_offset: int,
    ) -> None:
        if not roles or any(role not in ("O", "S", "L", "W") for role in roles):
            _fail("sampler role census is malformed")
        self.roles = roles
        self.qpc_clock_id = qpc_clock_id
        self.qpc_frequency = _QPC_FREQUENCY
        self.qpc_filetime_offset = qpc_filetime_offset
        self._records: dict[str, dict[str, Any]] = {}
        self._last_peaks = {role: 0 for role in roles}
        self._samples: list[dict[str, Any]] = []
        self._job_events: list[dict[str, Any]] = []
        self._job_seen: set[tuple[str, int]] = set()
        self._job_port: int | None = None
        self._launcher_pid: int | None = None
        self._lock = threading.RLock()
        self._sample_lock = threading.Lock()
        self._stop = threading.Event()
        self._error: BaseException | None = None
        self._sealed_times: dict[str, dict[str, int]] = {}
        self._sealed_exit_codes: dict[str, int] = {}
        self._thread = threading.Thread(target=self._run, name="m245-qpc-sampler", daemon=True)
        self._last_tick = 0

    def install(self, role: str, pid: int, *, expected_image: str, expected_hash: str) -> None:
        with self._lock:
            if role not in self.roles or role in self._records:
                _fail(f"sampler duplicate/unknown role installation: {role}")
            handle, acquired = _open_process_handle(pid)
            try:
                image = _process_image_path(handle)
                if os.path.normcase(image) != os.path.normcase(expected_image):
                    _fail(f"{role} process image path drift")
                image_raw, _image_identity = _secure_regular_bytes(Path(image), f"{role} process image")
                if _sha256_bytes(image_raw) != expected_hash:
                    _fail(f"{role} process image hash drift")
                times = _process_times(handle)
                parent = _process_parents().get(pid)
                if type(parent) is not int or parent <= 0:
                    _fail(f"{role} parent process is not observable")
                self._records[role] = {
                    "pid": pid,
                    "parent_pid": parent,
                    "handle": handle,
                    "handle_acquired_filetime": acquired,
                    "creation_filetime": times["creation_filetime"],
                    "image_path": expected_image,
                    "image_sha256": expected_hash,
                }
            except BaseException:
                _close_process_handle(handle)
                raise

    def attach_job(self, *, completion_port: int, launcher_pid: int) -> None:
        with self._lock:
            self._job_port = completion_port
            self._launcher_pid = launcher_pid

    def _next_tick(self) -> int:
        observed = time.perf_counter_ns()
        if observed <= self._last_tick:
            observed = self._last_tick + 1
        self._last_tick = observed
        return observed

    def _poll_job(self) -> None:
        if self._job_port is None:
            return
        kernel32 = _kernel32()
        kernel32.GetQueuedCompletionStatus.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(wintypes.LPVOID), wintypes.DWORD,
        ]
        kernel32.GetQueuedCompletionStatus.restype = wintypes.BOOL
        while True:
            message = wintypes.DWORD()
            key = ctypes.c_size_t()
            overlapped = wintypes.LPVOID()
            ctypes.set_last_error(0)
            ok = kernel32.GetQueuedCompletionStatus(
                self._job_port, ctypes.byref(message), ctypes.byref(key),
                ctypes.byref(overlapped), 0,
            )
            if not ok:
                if ctypes.get_last_error() == _WAIT_TIMEOUT:
                    break
                raise OSError(ctypes.get_last_error(), "GetQueuedCompletionStatus failed")
            pid = int(ctypes.cast(overlapped, ctypes.c_void_p).value or 0)
            event_name = (
                "NEW_PROCESS" if message.value == _JOB_NEW_PROCESS
                else "EXIT_PROCESS" if message.value == _JOB_EXIT_PROCESS
                else None
            )
            if event_name is None:
                continue
            role = "L" if pid == self._launcher_pid else "W"
            if role == "W" and role not in self._records and event_name == "NEW_PROCESS":
                self.install(role, pid, expected_image=STDLIB_PYTHON, expected_hash=STDLIB_PYTHON_SHA256)
            if role not in self._records:
                _fail("job event preceded retained process handle acquisition")
            unique = (event_name, pid)
            if unique in self._job_seen:
                _fail("duplicate Job completion-port process event")
            self._job_seen.add(unique)
            record = self._records[role]
            self._job_events.append({
                "creation_filetime": record["creation_filetime"],
                "event": event_name,
                "pid": pid,
                "qpc_tick": self._next_tick(),
                "role": role,
            })

    def _observation(self, role: str) -> dict[str, Any]:
        record = self._records.get(role)
        if record is None:
            return {
                "alive": False, "creation_filetime": None,
                "current_working_set_bytes": 0, "exit_code": None,
                "image_sha256": None, "kernel_time_100ns": 0,
                "peak_working_set_bytes": 0, "pid": None,
                "state": "NOT_CREATED", "user_time_100ns": 0,
            }
        handle = record["handle"]
        exit_code = _process_exit_code(handle)
        alive = exit_code == _STILL_ACTIVE
        current, peak = _process_memory(handle) if alive else (0, 0)
        self._last_peaks[role] = max(self._last_peaks[role], peak)
        times = _process_times(handle)
        return {
            "alive": alive,
            "creation_filetime": record["creation_filetime"],
            "current_working_set_bytes": current,
            "exit_code": None if alive else exit_code,
            "image_sha256": record["image_sha256"],
            "kernel_time_100ns": times["kernel_time_100ns"],
            "peak_working_set_bytes": self._last_peaks[role],
            "pid": record["pid"],
            "state": "ALIVE" if alive else "EXITED",
            "user_time_100ns": times["user_time_100ns"],
        }

    def force(self) -> dict[str, Any]:
        if self._error is not None:
            raise RuntimeError("QPC sampler failed") from self._error
        with self._sample_lock:
            with self._lock:
                self._poll_job()
                tick = self._next_tick()
                sample = {
                    "qpc_frequency": self.qpc_frequency,
                    "qpc_clock_id": self.qpc_clock_id,
                    "qpc_tick": tick,
                    "roles": {role: self._observation(role) for role in self.roles},
                    "sample_index": len(self._samples),
                    "utc_filetime": self.qpc_filetime_offset + tick * 10_000_000 // self.qpc_frequency,
                }
                self._samples.append(sample)
                return sample

    def _run(self) -> None:
        try:
            while not self._stop.wait(_SAMPLE_SECONDS):
                self.force()
        except BaseException as exc:
            self._error = exc
            self._stop.set()

    def start(self) -> None:
        self.force()
        self._thread.start()

    def await_roles(self, roles: tuple[str, ...], timeout: float = 10.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.force()
            with self._lock:
                if all(role in self._records for role in roles):
                    return
            time.sleep(0.01)
        _fail("required process roles were not observed through retained handles")

    def finish(self, *, exited_roles: tuple[str, ...]) -> list[dict[str, Any]]:
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline:
            final = self.force()
            if all(final["roles"][role]["state"] == "EXITED" for role in exited_roles):
                break
            time.sleep(0.01)
        else:
            _fail("sampler did not observe every required process exit")
        self._stop.set()
        self._thread.join(timeout=1.0)
        if self._thread.is_alive() or self._error is not None:
            raise RuntimeError("QPC sampler did not terminate cleanly") from self._error
        self.force()
        with self._lock:
            for role, record in self._records.items():
                self._sealed_times[role] = _process_times(record["handle"])
                self._sealed_exit_codes[role] = _process_exit_code(record["handle"])
        return list(self._samples)

    def identity(
        self,
        role: str,
        *,
        argv: list[str],
        environment_sha256: str,
        job_membership: bool,
        declared_exit_code: int | None = None,
    ) -> dict[str, Any]:
        record = self._records[role]
        if role not in self._sealed_times or role not in self._sealed_exit_codes:
            _fail("process identity requested before its meter was sealed")
        times = self._sealed_times[role]
        actual_exit = self._sealed_exit_codes[role]
        exit_code = declared_exit_code if actual_exit == _STILL_ACTIVE else actual_exit
        if exit_code is None:
            _fail(f"{role} identity has no terminal/declarative exit code")
        return {
            "argv": argv,
            "creation_filetime": record["creation_filetime"],
            "cwd": AUTHORITY_CWD,
            "environment_sha256": environment_sha256,
            "exit_code": exit_code,
            "handle_acquired_filetime": record["handle_acquired_filetime"],
            "image_path": record["image_path"],
            "image_sha256": record["image_sha256"],
            "job_membership": job_membership,
            "kernel_time_100ns": times["kernel_time_100ns"],
            "parent_pid": record["parent_pid"],
            "pid": record["pid"],
            "retained_handle_through_exit": True,
            "user_time_100ns": times["user_time_100ns"],
        }

    def process_record(self, role: str) -> dict[str, Any]:
        return dict(self._records[role])

    def sealed_times(self, role: str) -> dict[str, int]:
        if role not in self._sealed_times:
            _fail("process times requested before meter seal")
        return dict(self._sealed_times[role])

    @property
    def job_events(self) -> list[dict[str, Any]]:
        return list(self._job_events)

    def close(self) -> None:
        with self._lock:
            handles = [record["handle"] for record in self._records.values()]
            self._records.clear()
        for handle in handles:
            _close_process_handle(handle)


def _launch_worker_in_job(
    argv: list[str],
    *,
    environment: dict[str, str],
) -> tuple[subprocess.Popen[bytes], Any, Any]:
    """Create suspended L, bind a two-process Job/completion port, then resume."""

    if os.name != "nt":
        _fail("the frozen O/S/L/W topology is Windows-only")
    import ctypes
    from ctypes import wintypes

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
        )]

    class BASIC_LIMITS(ctypes.Structure):
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

    class EXTENDED_LIMITS(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BASIC_LIMITS),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    class ASSOCIATE_PORT(ctypes.Structure):
        _fields_ = [("CompletionKey", ctypes.c_void_p), ("CompletionPort", wintypes.HANDLE)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.CreateIoCompletionPort.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, ctypes.c_size_t, wintypes.DWORD,
    ]
    kernel32.CreateIoCompletionPort.restype = wintypes.HANDLE
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        _fail("CreateJobObjectW failed")
    limits = EXTENDED_LIMITS()
    limits.BasicLimitInformation.LimitFlags = 0x00000008 | 0x00002000
    limits.BasicLimitInformation.ActiveProcessLimit = 2
    if not kernel32.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
        _fail("SetInformationJobObject(active-process limit) failed")
    invalid_handle = ctypes.c_void_p(-1).value
    completion_port = kernel32.CreateIoCompletionPort(invalid_handle, None, 0, 1)
    if not completion_port:
        _fail("CreateIoCompletionPort failed")
    association = ASSOCIATE_PORT(ctypes.c_void_p(1), completion_port)
    if not kernel32.SetInformationJobObject(job, 7, ctypes.byref(association), ctypes.sizeof(association)):
        _fail("SetInformationJobObject(completion port) failed")
    process = subprocess.Popen(
        argv,
        cwd=AUTHORITY_CWD,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        bufsize=0,
        creationflags=getattr(subprocess, "CREATE_SUSPENDED", 0x00000004),
    )
    if not kernel32.AssignProcessToJobObject(job, int(process._handle)):
        process.kill()
        _fail("AssignProcessToJobObject failed")
    # subprocess closes the initial thread handle after CreateProcess.  Resume
    # the already-assigned suspended process through its retained process
    # handle; no unassigned execution window is introduced.
    ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
    ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
    ntdll.NtResumeProcess.restype = wintypes.LONG
    if int(ntdll.NtResumeProcess(int(process._handle))) != 0:
        process.kill()
        _fail("NtResumeProcess failed")
    return process, job, completion_port


def _read_exact(stream: Any, count: int) -> bytes:
    chunks: list[bytes] = []
    remaining = count
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            _fail("worker stream closed before the framed payload completed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _production_checkpoint(event_id: str) -> dict[str, Any]:
    return {
        "artifact": "M245_COMPLETE_EVENT_CHECKPOINT",
        "complete_event_id": event_id,
        "next_invocation_only": True,
        "schema": "m245-complete-event-checkpoint-v1",
        "status": "PROVISIONAL_COMPLETE_EVENT_NO_INVOCATION_PASS",
    }


def _publication_binding_from_file(path: Path, *, event_id: str, file_kind: str) -> dict[str, Any]:
    raw, identity = _secure_regular_bytes(path, f"prior {file_kind}")
    return {
        "bytes": len(raw),
        "device": identity.st_dev,
        "event_id": event_id,
        "file_kind": file_kind,
        "inode": identity.st_ino,
        "path": str(path.resolve()),
        "sha256": _sha256_bytes(raw),
    }


def _run_production_invocation(
    *,
    shard_id: int,
    invocation_index: int,
    trigger: dict[str, Any],
    trigger_entry_bytes: bytes,
    trigger_commit: str,
) -> int:
    global _EXPECTED_OUTER_VALIDATOR_SHA256, _EXPECTED_PRODUCTION_AUTHORITY_UNION
    _EXPECTED_OUTER_VALIDATOR_SHA256 = trigger["scientific_source_sha256"][
        "launch_m245_scientific_invocation.py"
    ]
    authority_union = dict(trigger["authority_sha256"])
    authority_union.update(trigger["scientific_source_sha256"])
    _EXPECTED_PRODUCTION_AUTHORITY_UNION = dict(authority_union)
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    shard_root = _real_shard_directory()
    preflight = preflight_invocation_paths(
        shard_root, shard_id=shard_id, invocation_index=invocation_index
    )
    namespace = shard_namespace(shard_id, invocation_index)
    trigger_sha = _sha256_bytes(trigger_entry_bytes)
    if (
        preflight["trigger_entry_sha256"] not in (None, trigger_sha)
        or preflight["trigger_commit"] not in (None, trigger_commit)
    ):
        _fail("current trigger lineage disagrees with the down-closed predecessor set")
    intent = {
        "artifact": "M245_SHARD_INVOCATION_INTENT",
        "schema": "m245-shard-invocation-intent-v1",
        "shard_id": shard_id,
        "invocation_index": invocation_index,
        "event_id": event_id,
        "trigger_entry_sha256": trigger_sha,
        "trigger_commit": trigger_commit,
        "namespace": namespace,
        "status": "DURABLE_ATTEMPT_BURNED",
    }
    intent_publication = publish_immutable_json(
        shard_root / namespace["intent_temp"],
        shard_root / namespace["intent"],
        intent,
        publication_path=str((shard_root / namespace["intent"]).resolve()),
    )
    child_environment = {
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() in {"SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP"}
    }
    environment.update(child_environment)
    environment.update({
        "M245_SHARD_ID": str(shard_id),
        "M245_INVOCATION_INDEX": str(invocation_index),
        "M245_EVENT_ID": event_id,
        "M245_INTENT_PATH": str((shard_root / namespace["intent"]).resolve()),
        "M245_TRIGGER_SHA256": trigger_sha,
        "M245_TRIGGER_COMMIT": trigger_commit,
        "M245_PRIMARY_SOURCE_SHA256": trigger["scientific_source_sha256"]["m245_primary_core.py"],
        "M245_REPLICA_SOURCE_SHA256": trigger["scientific_source_sha256"]["m245_replica_core.py"],
        "M245_WORKER_SOURCE_SHA256": trigger["scientific_source_sha256"]["m245_scientific_worker.py"],
    })
    try:
        qpc_clock_id = os.environ["M245_QPC_CLOCK_ID"]
        qpc_offset = int(os.environ["M245_QPC_FILETIME_OFFSET"])
        qpc_frequency = int(os.environ["M245_QPC_FREQUENCY"])
        outer_pid = int(os.environ["M245_O_PID"])
    except (KeyError, ValueError):
        _fail("outer observer did not supply the exact shared QPC/process context")
    if qpc_frequency != _QPC_FREQUENCY or not qpc_clock_id or outer_pid <= 0:
        _fail("shared QPC/process context drift")
    environment.update({
        "M245_QPC_CLOCK_ID": qpc_clock_id,
        "M245_QPC_FILETIME_OFFSET": str(qpc_offset),
        "M245_QPC_FREQUENCY": str(qpc_frequency),
        "M245_O_PID": str(outer_pid),
    })
    full_environment_sha = _sha256_bytes(_canonical_json_bytes(environment))
    s_environment_sha = _sha256_bytes(_canonical_json_bytes(dict(os.environ)))
    child_environment_sha = _sha256_bytes(_canonical_json_bytes(child_environment))
    worker_path = str((HERE / "m245_scientific_worker.py").resolve())
    runner_path = str((HERE / "run_m245_scientific_shard.py").resolve())
    sampler = _ProcessSampler(
        ("S", "L", "W"),
        qpc_clock_id=qpc_clock_id,
        qpc_filetime_offset=qpc_offset,
    )
    sampler.install(
        "S", os.getpid(), expected_image=STDLIB_PYTHON,
        expected_hash=STDLIB_PYTHON_SHA256,
    )
    if sampler.process_record("S")["parent_pid"] != outer_pid:
        _fail("S actual parent does not match the retained outer observer")
    sampler.start()
    process, job, completion_port = _launch_worker_in_job(
        [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker_path],
        environment=environment,
    )
    sampler.install(
        "L", process.pid, expected_image=VENV_PYTHON,
        expected_hash=VENV_PYTHON_SHA256,
    )
    sampler.attach_job(completion_port=int(completion_port), launcher_pid=process.pid)
    sampler.await_roles(("L", "W"))
    if (
        sampler.process_record("L")["parent_pid"] != os.getpid()
        or sampler.process_record("W")["parent_pid"] != process.pid
        or _process_in_job(sampler.process_record("S")["handle"], int(job))
        or not _process_in_job(sampler.process_record("L")["handle"], int(job))
        or not _process_in_job(sampler.process_record("W")["handle"], int(job))
    ):
        process.kill()
        _fail("retained S/L/W process tree drift")
    assert process.stdout is not None and process.stdin is not None and process.stderr is not None
    if process.stdout.readline() != b"M245_W_READY\n":
        process.kill()
        _fail("worker READY barrier drift")
    process.stdin.write(b"M245_W_GO\n")
    process.stdin.flush()
    watchdog_fired = threading.Event()
    def _watchdog_kill() -> None:
        watchdog_fired.set()
        try:
            process.kill()
        except OSError:
            pass
    watchdog = threading.Timer(5100.0, _watchdog_kill)
    watchdog.daemon = True
    watchdog.start()
    header = process.stdout.readline().decode("ascii", errors="strict").strip().split()
    if len(header) != 3 or header[0] != "M245_W_EVENT":
        process.kill()
        _fail("worker event frame header drift")
    try:
        frame_length = int(header[1])
    except ValueError:
        process.kill()
        _fail("worker event frame length is malformed")
    if frame_length <= 0 or not _valid_hash(header[2]):
        process.kill()
        _fail("worker event frame metadata is malformed")
    framed_raw = _read_exact(process.stdout, frame_length)
    if _sha256_bytes(framed_raw) != header[2]:
        process.kill()
        _fail("worker event frame hash drift")
    try:
        framed = json.loads(framed_raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        process.kill()
        _fail("worker event frame is not JSON")
    if framed_raw != _canonical_json_bytes(framed):
        process.kill()
        _fail("worker event frame is not canonical JSON")
    if not isinstance(framed, dict) or set(framed) != {"event_result", "quad_call_ledger", "quad_gateway"}:
        process.kill()
        _fail("worker event frame schema drift")
    event_result = validate_event_result(framed["event_result"], expected_event_id=event_id)
    ledger_summary = validate_quad_call_ledger(
        framed["quad_call_ledger"],
        shard_id=shard_id,
        invocation_index=invocation_index,
        event_id=event_id,
        _return_internal_aggregates=True,
    )
    _validate_scientific_ledger_bindings(event_result, ledger_summary)
    for ref in event_result["quad_gateway_ledger_refs"]:
        rows = [row for row in framed["quad_call_ledger"] if row["engine"] == ref["engine"] and row["precision_dps"] == ref["precision_dps"]]
        if ref["count"] != len(rows) or ref["sha256"] != _sha256_bytes(_canonical_json_bytes(rows)):
            process.kill()
            _fail("event quadrature ledger reference/hash drift")
    scientific_stop_tick = time.perf_counter_ns()
    watchdog.cancel()
    if watchdog_fired.is_set():
        _fail("scientific watchdog cap was reached")
    result_publication = publish_immutable_json(
        shard_root / namespace["result_temp"],
        shard_root / namespace["result"],
        event_result,
        publication_path=str((shard_root / namespace["result"]).resolve()),
    )
    result_publication_tick = time.perf_counter_ns()
    checkpoint_publication = publish_immutable_json(
        shard_root / namespace["checkpoint_temp"],
        shard_root / namespace["checkpoint"],
        _production_checkpoint(event_id),
        publication_path=str((shard_root / namespace["checkpoint"]).resolve()),
    )
    checkpoint_publication_tick = max(time.perf_counter_ns(), result_publication_tick + 1)
    if process.stdout.readline() != b"M245_W_DONE\n":
        process.kill()
        _fail("worker DONE barrier drift")
    done_tick = max(time.perf_counter_ns(), checkpoint_publication_tick + 1)
    process.stdin.write(b"M245_W_EXIT\n")
    process.stdin.flush()
    exit_release_tick = max(time.perf_counter_ns(), done_tick + 1)
    try:
        exit_code = process.wait(timeout=300)
    except subprocess.TimeoutExpired:
        process.kill()
        _fail("worker exceeded the durability reserve")
    stderr_raw = process.stderr.read()
    if exit_code != 0 or stderr_raw:
        _fail("worker/launcher did not exit cleanly with empty stderr")
    # E2.7/E1.6 close boundary: sampler.finish freezes the inner raw stream.
    # From here on only canonical serialization, hashing, hard-link
    # publication, reopen verification, cleanup, and exit are legal; all
    # policy/science/ledger validation already ran above, and O re-validates
    # every published byte from the immutable files.
    samples = sampler.finish(exited_roles=("L", "W"))
    stream_closed_tick = time.perf_counter_ns()
    events = sampler.job_events
    if (
        len(events) != 4
        or [event["event"] for event in events]
        != ["NEW_PROCESS", "NEW_PROCESS", "EXIT_PROCESS", "EXIT_PROCESS"]
    ):
        _fail("completion-port L/W lifetime census is not exact")
    event_ticks = {(event["role"], event["event"]): event["qpc_tick"] for event in events}
    worker_exit_tick = event_ticks.get(("W", "EXIT_PROCESS"))
    launcher_exit_tick = event_ticks.get(("L", "EXIT_PROCESS"))
    if type(worker_exit_tick) is not int or type(launcher_exit_tick) is not int:
        _fail("completion-port exit chronology is incomplete")
    stream_closed_tick = max(stream_closed_tick, launcher_exit_tick + 1)
    l_times = sampler.sealed_times("L")
    w_times = sampler.sealed_times("W")
    s_creation = sampler.process_record("S")["creation_filetime"]
    raw_meter = {
        "artifact": "M245_SHARD_RAW_METER",
        "job_process_events": events,
        "milestones": {
            "checkpoint_publication_verified_qpc_tick": checkpoint_publication_tick,
            "done_received_qpc_tick": done_tick,
            "exit_released_qpc_tick": exit_release_tick,
            "launcher_exit_qpc_tick": launcher_exit_tick,
            "result_publication_verified_qpc_tick": result_publication_tick,
            "stream_closed_qpc_tick": stream_closed_tick,
            "worker_exit_qpc_tick": worker_exit_tick,
        },
        "qpc_clock_id": qpc_clock_id,
        "qpc_frequency": qpc_frequency,
        "s_process_creation_filetime": s_creation,
        "samples": samples,
        "schema": "m245-shard-raw-meter-v1",
        "scientific_stop_filetime": qpc_offset + scientific_stop_tick * 10_000_000 // qpc_frequency,
        "terminal_child_exit_filetime": max(l_times["exit_filetime"], w_times["exit_filetime"]),
    }
    max_gap = 0.0
    for gap_left, gap_right in zip(samples, samples[1:]):
        max_gap = max(
            max_gap,
            float(Fraction(gap_right["qpc_tick"] - gap_left["qpc_tick"], qpc_frequency)),
        )
    meter_publication = publish_immutable_json(
        shard_root / namespace["meter_temp"],
        shard_root / namespace["meter"],
        raw_meter,
        publication_path=str((shard_root / namespace["meter"]).resolve()),
    )
    prior_files = None
    if invocation_index == 2:
        prior_namespace = shard_namespace(shard_id, 1)
        prior_files = [
            _publication_binding_from_file(
                shard_root / prior_namespace[kind],
                event_id=ASSIGNMENTS[shard_id][0], file_kind=kind,
            )
            for kind in ("result", "checkpoint", "meter", "invocation_receipt")
        ]
    s_argv = [
        STDLIB_PYTHON, "-I", "-B", "-S", "-u", runner_path,
        "--shard-id", str(shard_id), "--invocation-index", str(invocation_index),
    ]
    l_argv = [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker_path]
    identities = {
        "S": sampler.identity(
            "S", argv=s_argv, environment_sha256=s_environment_sha,
            job_membership=False, declared_exit_code=0,
        ),
        "L": sampler.identity(
            "L", argv=l_argv, environment_sha256=full_environment_sha,
            job_membership=True,
        ),
        "W": sampler.identity(
            "W", argv=[worker_path], environment_sha256=full_environment_sha,
            job_membership=True,
        ),
    }
    job_census = {
        "active_process_limit": 2,
        "distinct_job_pids": [identities["L"]["pid"], identities["W"]["pid"]],
        "job_roles": ["L", "W"],
        "total_processes": 2,
        "worker_children": 0,
    }
    receipt = {
        "artifact": "M245_SHARD_INVOCATION_RECEIPT",
        "authority_sha256": authority_union,
        "checkpoint_publication": checkpoint_publication,
        "child_environment": child_environment,
        "child_environment_sha256": child_environment_sha,
        "event_id": event_id,
        "firewall": {name: False for name in FIREWALL_KEYS},
        "intent_publication": intent_publication,
        "invocation_index": invocation_index,
        "job_census": job_census,
        "meter_publication": meter_publication,
        "no_retry": True,
        "path_state": {
            "all_current_paths_initially_absent": True,
            "all_prior_paths_exact": invocation_index == 2,
            "no_unlisted_write": True,
            "temporary_paths_absent_after_publication": True,
        },
        "prior_invocation_files": prior_files,
        "process_identities": identities,
        "quad_call_ledger": framed["quad_call_ledger"],
        "quad_call_ledger_sha256": _sha256_bytes(_canonical_json_bytes(framed["quad_call_ledger"])),
        "quad_gateway": framed["quad_gateway"],
        "resource_meter": _resource_meter_reductions(raw_meter, samples, max_gap),
        "result_publication": result_publication,
        "schema": "m245-shard-invocation-receipt-v1",
        "shard_id": shard_id,
        "status": "PROVISIONAL_INNER_RECEIPT_NO_INVOCATION_PASS",
        "stderr_empty": True,
        "stdout_records": ["M245_W_READY", "M245_W_DONE"],
    }
    publish_immutable_json(
        shard_root / namespace["invocation_receipt_temp"],
        shard_root / namespace["invocation_receipt"],
        receipt,
        publication_path=str((shard_root / namespace["invocation_receipt"]).resolve()),
    )
    _close_process_handle(int(completion_port))
    _close_process_handle(int(job))
    print("M245_S_PROVISIONAL_RECEIPT_PUBLISHED", flush=True)
    del ledger_summary
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="M245 fail-closed stdlib shard supervisor")
    parser.add_argument("--shard-id", type=int)
    parser.add_argument("--invocation-index", type=int)
    parser.add_argument("--emit-pretrigger-zero-intent-census", action="store_true")
    arguments = parser.parse_args(argv)
    if Path.cwd().resolve() != HERE:
        _fail("supervisor cwd drift")
    if arguments.emit_pretrigger_zero_intent_census:
        if arguments.shard_id is not None or arguments.invocation_index is not None:
            _fail("census mode accepts no shard arguments")
        return _emit_pretrigger_zero_intent_census()
    if arguments.shard_id is None or arguments.invocation_index is None:
        _fail("production invocation requires exact shard and invocation indices")
    validate_shard_request(
        arguments.shard_id,
        ASSIGNMENTS.get(arguments.shard_id, ()),
        arguments.invocation_index,
        arguments.invocation_index == 2,
    )
    expected_argv = [
        STDLIB_PYTHON, "-I", "-B", "-S", "-u", str(Path(__file__).resolve()),
        "--shard-id", str(arguments.shard_id),
        "--invocation-index", str(arguments.invocation_index),
    ]
    _require_exact_supervisor_process_binding(expected_argv, "supervisor")
    trigger, entry_bytes, trigger_commit = load_and_verify_committed_trigger()
    return _run_production_invocation(
        shard_id=arguments.shard_id,
        invocation_index=arguments.invocation_index,
        trigger=trigger,
        trigger_entry_bytes=entry_bytes,
        trigger_commit=trigger_commit,
    )


if __name__ == "__main__":
    raise SystemExit(main())
