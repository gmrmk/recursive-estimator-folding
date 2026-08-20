"""Frozen dummy-only contract for M245 shard transport and metering.

No frozen fixture is evaluated here.  The missing supervisor/runner import is
an independent RED; after it exists, this suite also binds the separate worker
module, exact two-invocation namespaces, immutable publication, full resource
scope, and the lossless ordered receipt for every ``mp.quad`` call.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import inspect
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import run_m245_scientific_shard as runner
import launch_m245_scientific_invocation as launcher


HERE = Path(__file__).resolve().parent
SHARD_DIRECTORY_REPO_RELATIVE = "corpus/whestbench/experiments/m245_fable_spectrum_shards"
V2_SHA256 = "0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b"
V2_CHECKSUM_SHA256 = "2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e"
SCIENTIFIC_ERRATUM2_NAME = "M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md"
SCIENTIFIC_ERRATUM2_SHA256 = "8641de9ec301ba402b87e50dd8c5e3322a6532313f1d603c54356a4137e21587"
SCIENTIFIC_OVERLAY2_SHA256 = "401629468b5ec1f2eb5447b650b10f27fb47ba7ce3af74c740a230feeefcceaf"
AUTHORITY_CWD = str(HERE)
STDLIB_PYTHON = r"C:\Python314\python.exe"
VENV_PYTHON = r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe"
STDLIB_PYTHON_SHA256 = "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"
VENV_PYTHON_SHA256 = "4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262"
ASSIGNMENTS = {
    0: ("E00", "E01"),
    1: ("E02", "E03"),
    2: ("E04", "E05"),
    3: ("E06", "E07"),
}

SHARD_CONTRACT = {
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
    SCIENTIFIC_ERRATUM2_NAME,
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
    "M245_FROZEN_MANIFEST_V2_20260810.json": V2_SHA256,
    "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json": "4d9adc56a9f1a02a7fa1f066be3a6fd626b67a0656e5d86577271b4bb4a097fe",
    "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json": "15a69748afc5e7109f61ce41ccfe32d17b8af573caf2b5d8e99f5be80be17985",
    "M245_SHA256SUMS_V2_20260810.txt": V2_CHECKSUM_SHA256,
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md": "5497b1397a62bbfb4f3be73a02f2b63872e01f2bd4795b77232e7c6c287beb85",
    SCIENTIFIC_ERRATUM2_NAME: SCIENTIFIC_ERRATUM2_SHA256,
    "M245_SHA256SUMS_V2_OVERLAY2_20260810.txt": SCIENTIFIC_OVERLAY2_SHA256,
}

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

NAMESPACE_KEYS = (
    "directory_repo_relative",
    "intent_temp",
    "intent",
    "result_temp",
    "result",
    "checkpoint_temp",
    "checkpoint",
    "meter_temp",
    "meter",
    "invocation_receipt_temp",
    "invocation_receipt",
    "terminal_witness_temp",
    "terminal_witness",
    "final_shard_receipt_temp",
    "final_shard_receipt",
)

QUAD_CALL_RECEIPT_KEYS = (
    "shard_id",
    "invocation_index",
    "event_id",
    "engine",
    "precision_dps",
    "cache_scope_id",
    "request_index",
    "completion_index",
    "parent_request_index",
    "nesting_depth",
    "quantity",
    "call_role",
    "panel_path",
    "interval_left",
    "interval_right",
    "method",
    "maxdegree",
    "error_api",
    "error_semantics",
    "interval_certified",
    "saved_mp_eps_mpf",
    "mp_quad_invoked",
    "cache_disposition",
    "returned_value_mpf",
    "returned_error_mpf",
    "value_finite",
    "error_finite",
    "error_le_saved_mp_eps_over_8",
    "exception_type",
    "exception_message_sha256",
    "pass",
)

MPF_TUPLE_KEYS = ("bitcount", "exponent", "mantissa", "sign")
ENDPOINT_KEYS = ("kind", "mpf")
QUAD_ROLES = (
    "outer_top_level",
    "nested_plackett",
    "nested_unary",
    "direct_analytic_gate",
    "direct_residual_gate",
    "direct_beta_residual_gate",
)

INVOCATION_RECEIPT_KEYS = (
    "artifact",
    "authority_sha256",
    "checkpoint_publication",
    "child_environment",
    "child_environment_sha256",
    "event_id",
    "firewall",
    "intent_publication",
    "invocation_index",
    "job_census",
    "meter_publication",
    "no_retry",
    "path_state",
    "prior_invocation_files",
    "process_identities",
    "quad_call_ledger",
    "quad_call_ledger_sha256",
    "quad_gateway",
    "resource_meter",
    "result_publication",
    "schema",
    "shard_id",
    "status",
    "stderr_empty",
    "stdout_records",
)

RESOURCE_METER_KEYS = (
    "charged_process_roles",
    "cpu_100ns_by_role",
    "cpu_seconds_sum",
    "endpoint_qpc_tick",
    "full_wall_seconds",
    "lifetime_peak_upper_bytes",
    "max_observed_sampling_gap_seconds",
    "max_sampled_concurrent_working_set_bytes",
    "qpc_frequency",
    "rss_gate_bytes",
    "sample_count",
    "s_process_creation_filetime",
    "scientific_stop_qpc_tick",
    "scientific_stop_wall_seconds",
    "t0_qpc_tick",
    "terminal_child_exit_filetime",
)

TERMINAL_RESOURCE_METER_KEYS = (
    "charged_process_roles",
    "cpu_100ns_by_role",
    "cpu_seconds_sum",
    "full_wall_seconds",
    "inner_sample_count",
    "lifetime_peak_upper_bytes",
    "max_merged_concurrent_working_set_bytes",
    "max_observed_sampling_gap_seconds",
    "o_process_creation_filetime",
    "outer_sample_count",
    "rss_gate_bytes",
    "scientific_stop_wall_seconds",
    "terminal_endpoint_filetime",
)

TERMINAL_WITNESS_KEYS = (
    "artifact",
    "schema",
    "shard_id",
    "invocation_index",
    "event_id",
    "authority_sha256",
    "inner_artifacts",
    "inner_meter",
    "prior_invocation_files",
    "outer_meter",
    "process_identities",
    "job_census",
    "s_exit",
    "resource_meter",
    "final_shard_receipt",
    "firewall",
    "status",
)

FINAL_SHARD_RECEIPT_KEYS = (
    "artifact",
    "schema",
    "shard_id",
    "events_in_order",
    "event_results",
    "invocation_receipts",
    "authority_sha256",
    "resource_union",
    "no_cross_shard_cache",
    "firewall",
    "status",
)

EVENT_RESULT_KEYS = (
    "event_id",
    "fixture_array_sha256",
    "primary_by_precision",
    "replica_by_precision",
    "cross_precision_gates",
    "primary_replica_gates",
    "analytic_solve_energy_beta_gates",
    "curve_report",
    "quad_gateway_ledger_refs",
    "only_future_bound",
    "gate_verdict",
    "firewall",
    "forbidden_credit",
)

PRIMARY_EVENT_KEYS = (
    "artifact",
    "schema",
    "event_id",
    "precision_dps",
    "fixture_array_sha256",
    "degrees",
    "R",
    "G",
    "mu_rb",
    "K",
    "d",
    "beta",
    "leading_blocks",
    "analytic_direct_checks",
    "quadrature_audit",
    "firewall",
)

REPLICA_EVENT_KEYS = (
    "artifact",
    "schema",
    "event_id",
    "precision_dps",
    "fixture_array_sha256",
    "fixed_b_nodes",
    "b_rep_at_nodes",
    "mu_rep",
    "M_same",
    "M_cross",
    "K_rep",
    "quadrature_audit",
    "firewall",
)

TRIGGER_KEYS = (
    "agent_channel_binding",
    "aggregation_contract",
    "assignments",
    "authority_commit_v1",
    "authority_erratum2_commit",
    "authority_repair_commit",
    "authority_sha256",
    "final_shard_receipt_contract",
    "independent_static_audits",
    "process_argv_contract",
    "scientific_source_sha256",
    "zero_intent_census",
)

FIREWALL_KEYS = (
    "challenge_network_or_weights",
    "champion_output",
    "credentials",
    "hidden_compute",
    "leaderboard",
    "m125_response",
    "m151_source_arrays",
    "m178_code_or_credit",
    "m196_state",
    "m243_input_or_import",
    "network_service",
    "retry_or_clipping",
    "scorer",
    "sealed_cells",
    "submission",
    "truth",
)

RUNNER_PUBLIC_CALLABLES = (
    "shard_contract",
    "shard_namespace",
    "validate_shard_request",
    "validate_trigger_payload",
    "validate_quad_call_ledger",
    "validate_event_result",
    "validate_invocation_receipt",
    "preflight_invocation_paths",
    "publish_immutable_json",
    "main",
)

LAUNCHER_PUBLIC_CALLABLES = (
    "launch_contract",
    "classify_attempt_failure",
    "validate_complete_launch_census",
    "validate_trigger_payload",
    "validate_terminal_witness",
    "validate_final_shard_receipt",
    "build_final_shard_receipt_from_files",
    "publish_immutable_json",
    "run_dummy_transport_probe",
    "main",
)


def _canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _mpf(sign: int, mantissa: int, exponent: int, bitcount: int) -> dict:
    return {
        "bitcount": bitcount,
        "exponent": exponent,
        "mantissa": str(mantissa),
        "sign": sign,
    }


def _decode_mpf_tuple(payload: dict) -> float:
    magnitude = int(payload["mantissa"]) * (2.0 ** int(payload["exponent"]))
    return -magnitude if payload["sign"] else magnitude


def _endpoint(value: int | str) -> dict:
    if value == "+inf":
        return {"kind": "+inf", "mpf": None}
    if value == "-inf":
        return {"kind": "-inf", "mpf": None}
    return {"kind": "finite", "mpf": _mpf(0 if value >= 0 else 1, abs(int(value)), 0, abs(int(value)).bit_length())}


def _quad_call(
    index: int,
    *,
    shard_id: int = 0,
    invocation_index: int = 1,
    event_id: str = "DUMMY_EVENT_NOT_E00_E07",
    engine: str = "primary",
    precision_dps: int = 80,
    role: str = "outer_top_level",
    parent_request_index: int | None = None,
    nesting_depth: int = 0,
    completion_index: int | None = None,
) -> dict:
    return {
        "shard_id": shard_id,
        "invocation_index": invocation_index,
        "event_id": event_id,
        "engine": engine,
        "precision_dps": precision_dps,
        "cache_scope_id": (
            f"S{shard_id}:I{invocation_index}:{event_id}:"
            f"{engine}:{precision_dps}:fresh"
        ),
        "request_index": index,
        "completion_index": index if completion_index is None else completion_index,
        "parent_request_index": parent_request_index,
        "nesting_depth": nesting_depth,
        "quantity": "dummy_scalar",
        "call_role": role,
        "panel_path": [index],
        "interval_left": _endpoint(0),
        "interval_right": _endpoint(1),
        "method": "tanh-sinh",
        "maxdegree": 14,
        "error_api": True,
        "error_semantics": "heuristic_diagnostic_estimate_not_interval_certificate",
        "interval_certified": False,
        "saved_mp_eps_mpf": _mpf(0, 1, -296, 1),
        "mp_quad_invoked": True,
        "cache_disposition": "miss",
        "returned_value_mpf": _mpf(0, 1, 0, 1),
        "returned_error_mpf": _mpf(0, 1, -300, 1),
        "value_finite": True,
        "error_finite": True,
        "error_le_saved_mp_eps_over_8": True,
        "exception_type": None,
        "exception_message_sha256": None,
        "pass": True,
    }


def _publication(name: str, byte: str = "0", raw: bytes | None = None) -> dict:
    payload = b"x" * 64 if raw is None else raw
    return {
        "bytes": len(payload),
        "device": 1,
        "inode": 2,
        "path": name,
        "reopened_bytes_equal": True,
        "sha256": byte * 64 if raw is None else _sha256_bytes(raw),
        "source_final_same_device_inode": True,
        "temporary_unlinked": True,
    }


def _firewall() -> dict:
    return {name: False for name in FIREWALL_KEYS}


def _identity(
    role: str,
    pid: int,
    parent_pid: int,
    *,
    shard_id: int,
    invocation_index: int,
) -> dict:
    runner_path = str((HERE / "run_m245_scientific_shard.py").resolve())
    launcher_path = str((HERE / "launch_m245_scientific_invocation.py").resolve())
    worker_path = str((HERE / "m245_scientific_worker.py").resolve())
    argv = {
        "O": [
            STDLIB_PYTHON,
            "-I",
            "-B",
            "-S",
            "-u",
            launcher_path,
            "--shard-id",
            str(shard_id),
            "--invocation-index",
            str(invocation_index),
        ],
        "S": [
            STDLIB_PYTHON,
            "-I",
            "-B",
            "-S",
            "-u",
            runner_path,
            "--shard-id",
            str(shard_id),
            "--invocation-index",
            str(invocation_index),
        ],
        "L": [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker_path],
        "W": [worker_path],
    }[role]
    return {
        "argv": argv,
        "creation_filetime": 10_000_000_000 + pid,
        "cwd": AUTHORITY_CWD,
        "environment_sha256": "e" * 64,
        "exit_code": 0,
        "handle_acquired_filetime": 10_000_000_500 + pid,
        "image_path": VENV_PYTHON if role == "L" else STDLIB_PYTHON,
        "image_sha256": VENV_PYTHON_SHA256 if role == "L" else STDLIB_PYTHON_SHA256,
        "job_membership": role in ("L", "W"),
        "kernel_time_100ns": 10_000,
        "parent_pid": parent_pid,
        "pid": pid,
        "retained_handle_through_exit": True,
        "user_time_100ns": 20_000,
    }


def _authority_sha256() -> dict[str, str]:
    authority = dict(FROZEN_AUTHORITY_SHA256)
    authority.update(
        {
            name: format(index + 1, "x")[-1] * 64
            for index, name in enumerate(SCIENTIFIC_SOURCE_HASH_KEYS)
        }
    )
    return authority


def _meter_role(
    role: str,
    *,
    state: str,
    current: int,
    peak: int,
    kernel: int,
    user: int,
) -> dict:
    pid = {"O": 199, "S": 200, "L": 201, "W": 202}[role]
    created = state != "NOT_CREATED"
    return {
        "alive": state == "ALIVE",
        "creation_filetime": 10_000_000_000 + pid if created else None,
        "current_working_set_bytes": current,
        "exit_code": 0 if state == "EXITED" else None,
        "image_sha256": (
            (VENV_PYTHON_SHA256 if role == "L" else STDLIB_PYTHON_SHA256)
            if created
            else None
        ),
        "kernel_time_100ns": kernel,
        "peak_working_set_bytes": peak,
        "pid": pid if created else None,
        "state": state,
        "user_time_100ns": user,
    }


def _meter_payload() -> dict:
    frequency = 10_000_000
    clock_id = "DUMMY_SHARED_QPC_CLOCK_DOMAIN"
    filetime_offset = 10_000_000_000
    t0 = 500_000
    ticks = (t0, 1_000_000, 1_500_000, 2_000_000, 2_200_000)
    rows = (
        {
            "S": _meter_role("S", state="ALIVE", current=1000, peak=1000, kernel=100, user=100),
            "L": _meter_role("L", state="NOT_CREATED", current=0, peak=0, kernel=0, user=0),
            "W": _meter_role("W", state="NOT_CREATED", current=0, peak=0, kernel=0, user=0),
        },
        {
            "S": _meter_role("S", state="ALIVE", current=1500, peak=1500, kernel=2100, user=1100),
            "L": _meter_role("L", state="ALIVE", current=2500, peak=2500, kernel=3000, user=2000),
            "W": _meter_role("W", state="ALIVE", current=3500, peak=3500, kernel=4000, user=3000),
        },
        {
            "S": _meter_role("S", state="ALIVE", current=1200, peak=1800, kernel=4100, user=2100),
            "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000),
            "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000),
        },
        {
            "S": _meter_role("S", state="ALIVE", current=900, peak=1800, kernel=6100, user=4100),
            "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000),
            "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000),
        },
        {
            "S": _meter_role("S", state="ALIVE", current=800, peak=1800, kernel=6500, user=4500),
            "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000),
            "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000),
        },
    )
    s_creation = 10_000_000_200
    return {
        "artifact": "M245_SHARD_RAW_METER",
        "job_process_events": [
            {"creation_filetime": 10_000_000_201, "event": "NEW_PROCESS", "pid": 201, "qpc_tick": 1_100_000, "role": "L"},
            {"creation_filetime": 10_000_000_202, "event": "NEW_PROCESS", "pid": 202, "qpc_tick": 1_200_000, "role": "W"},
            {"creation_filetime": 10_000_000_202, "event": "EXIT_PROCESS", "pid": 202, "qpc_tick": 1_900_000, "role": "W"},
            {"creation_filetime": 10_000_000_201, "event": "EXIT_PROCESS", "pid": 201, "qpc_tick": 2_000_000, "role": "L"},
        ],
        "milestones": {
            "checkpoint_publication_verified_qpc_tick": 1_400_000,
            "done_received_qpc_tick": 1_450_000,
            "exit_released_qpc_tick": 1_500_000,
            "launcher_exit_qpc_tick": 2_000_000,
            "result_publication_verified_qpc_tick": 1_350_000,
            "stream_closed_qpc_tick": 2_200_000,
            "worker_exit_qpc_tick": 1_900_000,
        },
        "qpc_clock_id": clock_id,
        "qpc_frequency": frequency,
        "s_process_creation_filetime": s_creation,
        "samples": [
            {
                "qpc_frequency": frequency,
                "qpc_clock_id": clock_id,
                "qpc_tick": tick,
                "roles": roles,
                "sample_index": index,
                "utc_filetime": filetime_offset + tick,
            }
            for index, (tick, roles) in enumerate(zip(ticks, rows))
        ],
        "schema": "m245-shard-raw-meter-v1",
        "scientific_stop_filetime": filetime_offset + 1_550_000,
        "terminal_child_exit_filetime": filetime_offset + 2_200_000,
    }


def _resource_meter(meter: dict | None = None) -> dict:
    meter = _meter_payload() if meter is None else meter
    samples = meter["samples"]
    frequency = meter["qpc_frequency"]
    t0 = samples[0]["qpc_tick"]
    endpoint = samples[-1]["qpc_tick"]
    final_roles = samples[-1]["roles"]
    cpu = {
        role: final_roles[role]["kernel_time_100ns"] + final_roles[role]["user_time_100ns"]
        for role in ("S", "L", "W")
    }
    sampled = max(
        sum(
            role["current_working_set_bytes"]
            for role in sample["roles"].values()
            if role["state"] == "ALIVE"
        )
        for sample in samples
    )
    lifetime_peak = sum(
        max(sample["roles"][role]["peak_working_set_bytes"] for sample in samples)
        for role in ("S", "L", "W")
    )
    gaps = [
        (right["qpc_tick"] - left["qpc_tick"]) / frequency
        for left, right in zip(samples, samples[1:])
    ]
    return {
        "charged_process_roles": ["S", "L", "W"],
        "cpu_100ns_by_role": cpu,
        "cpu_seconds_sum": sum(cpu.values()) / 10_000_000,
        "endpoint_qpc_tick": endpoint,
        "full_wall_seconds": (
            meter["terminal_child_exit_filetime"] - meter["s_process_creation_filetime"]
        ) / 10_000_000,
        "lifetime_peak_upper_bytes": lifetime_peak,
        "max_observed_sampling_gap_seconds": max(gaps),
        "max_sampled_concurrent_working_set_bytes": sampled,
        "qpc_frequency": frequency,
        "rss_gate_bytes": max(sampled, lifetime_peak),
        "sample_count": len(samples),
        "s_process_creation_filetime": meter["s_process_creation_filetime"],
        "scientific_stop_qpc_tick": 1_300_000,
        "scientific_stop_wall_seconds": (
            meter["scientific_stop_filetime"] - meter["s_process_creation_filetime"]
        ) / 10_000_000,
        "t0_qpc_tick": t0,
        "terminal_child_exit_filetime": meter["terminal_child_exit_filetime"],
    }


def _outer_meter_payload(invocation_index: int) -> dict:
    frequency = 10_000_000
    clock_id = "DUMMY_SHARED_QPC_CLOCK_DOMAIN"
    filetime_offset = 10_000_000_000
    t0 = 500_000
    ticks = (t0, 1_000_000, 1_500_000, 2_000_000, 2_500_000)
    o_creation = 10_000_000_199
    rows = (
        {
            "O": _meter_role("O", state="ALIVE", current=700, peak=700, kernel=100, user=100),
            "S": _meter_role("S", state="NOT_CREATED", current=0, peak=0, kernel=0, user=0),
        },
        {
            "O": _meter_role("O", state="ALIVE", current=900, peak=900, kernel=1000, user=700),
            "S": _meter_role("S", state="ALIVE", current=1000, peak=1000, kernel=100, user=100),
        },
        {
            "O": _meter_role("O", state="ALIVE", current=1100, peak=1100, kernel=2000, user=1400),
            "S": _meter_role("S", state="ALIVE", current=1500, peak=1800, kernel=4100, user=2100),
        },
        {
            "O": _meter_role("O", state="ALIVE", current=900, peak=1200, kernel=3000, user=2200),
            "S": _meter_role("S", state="EXITED", current=0, peak=2000, kernel=7000, user=5000),
        },
        {
            "O": _meter_role("O", state="ALIVE", current=800, peak=1200, kernel=4000, user=3000),
            "S": _meter_role("S", state="EXITED", current=0, peak=2000, kernel=7000, user=5000),
        },
    )
    return {
        "artifact": "M245_OUTER_RAW_METER",
        "invocation_index": invocation_index,
        "milestones": {
            "final_shard_publication_verified_qpc_tick": 2_200_000 if invocation_index == 2 else None,
            "s_exit_qpc_tick": 2_000_000,
            "s_spawn_qpc_tick": 1_000_000,
            "stream_closed_qpc_tick": 2_500_000,
        },
        "o_process_creation_filetime": o_creation,
        "qpc_clock_id": clock_id,
        "qpc_frequency": frequency,
        "samples": [
            {
                "qpc_frequency": frequency,
                "qpc_clock_id": clock_id,
                "qpc_tick": tick,
                "roles": roles,
                "sample_index": index,
                "utc_filetime": filetime_offset + tick,
            }
            for index, (tick, roles) in enumerate(zip(ticks, rows))
        ],
        "schema": "m245-outer-raw-meter-v1",
        "terminal_endpoint_filetime": filetime_offset + ticks[-1],
    }


def _terminal_resource_meter(inner: dict, outer: dict) -> dict:
    inner_samples = inner["samples"]
    outer_samples = outer["samples"]
    frequency = inner["qpc_frequency"]
    clock_id = inner["qpc_clock_id"]
    if outer["qpc_frequency"] != frequency or outer["qpc_clock_id"] != clock_id:
        raise AssertionError("inner and outer meters must share one QPC domain")

    clock_offsets: set[int] = set()
    identities_by_role: dict[str, set[tuple[int, int]]] = {
        role: set() for role in ("O", "S", "L", "W")
    }
    max_gap = 0.0
    for stream, expected_roles in (
        (inner, {"S", "L", "W"}),
        (outer, {"O", "S"}),
    ):
        previous_tick = None
        previous_counters: dict[tuple[str, int, int], tuple[int, int, int]] = {}
        for expected_index, sample in enumerate(stream["samples"]):
            if sample["sample_index"] != expected_index:
                raise AssertionError("sample indices must be contiguous")
            if sample["qpc_frequency"] != frequency or sample["qpc_clock_id"] != clock_id:
                raise AssertionError("sample QPC domain drift")
            if set(sample["roles"]) != expected_roles:
                raise AssertionError("meter role census drift")
            tick = sample["qpc_tick"]
            if previous_tick is not None:
                if tick <= previous_tick:
                    raise AssertionError("QPC ticks must strictly increase")
                gap = (tick - previous_tick) / frequency
                if gap > 0.100000000:
                    raise AssertionError("meter sampling gap exceeds 0.1 seconds")
                max_gap = max(max_gap, gap)
            previous_tick = tick
            clock_offsets.add(sample["utc_filetime"] - tick * 10_000_000 // frequency)
            for role, observation in sample["roles"].items():
                if observation["state"] == "NOT_CREATED":
                    if any(
                        observation[key] is not None
                        for key in ("pid", "creation_filetime", "image_sha256")
                    ):
                        raise AssertionError("not-created role carries an identity")
                    continue
                identity = (observation["pid"], observation["creation_filetime"])
                identities_by_role[role].add(identity)
                counters = (
                    observation["kernel_time_100ns"],
                    observation["user_time_100ns"],
                    observation["peak_working_set_bytes"],
                )
                prior = previous_counters.get((role, *identity))
                if prior is not None and any(now < old for now, old in zip(counters, prior)):
                    raise AssertionError("resource counter rollback")
                previous_counters[(role, *identity)] = counters
                if observation["current_working_set_bytes"] > observation["peak_working_set_bytes"]:
                    raise AssertionError("current RSS exceeds lifetime peak")
    if len(clock_offsets) != 1:
        raise AssertionError("inner and outer FILETIME/QPC clocks disagree")
    if any(len(identities_by_role[role]) != 1 for role in ("O", "S", "L", "W")):
        raise AssertionError("missing or unstable process identity")
    if identities_by_role["S"] != {
        (
            inner_samples[-1]["roles"]["S"]["pid"],
            inner_samples[-1]["roles"]["S"]["creation_filetime"],
        )
    }:
        raise AssertionError("inner/outer S identity disagreement")
    identity_owners: dict[tuple[int, int], str] = {}
    for role, identities in identities_by_role.items():
        identity = next(iter(identities))
        prior_role = identity_owners.setdefault(identity, role)
        if prior_role != role:
            raise AssertionError("one process identity assigned to two roles")

    cpu = {
        "O": sum(
            outer_samples[-1]["roles"]["O"][key]
            for key in ("kernel_time_100ns", "user_time_100ns")
        ),
        "S": sum(
            outer_samples[-1]["roles"]["S"][key]
            for key in ("kernel_time_100ns", "user_time_100ns")
        ),
        "L": sum(
            inner_samples[-1]["roles"]["L"][key]
            for key in ("kernel_time_100ns", "user_time_100ns")
        ),
        "W": sum(
            inner_samples[-1]["roles"]["W"][key]
            for key in ("kernel_time_100ns", "user_time_100ns")
        ),
    }

    def latest(samples: list[dict], when_tick: int, role: str) -> dict:
        available = [sample for sample in samples if sample["qpc_tick"] <= when_tick]
        if not available:
            raise AssertionError("missing prior sample at union QPC tick")
        sample = available[-1]
        if (when_tick - sample["qpc_tick"]) / frequency > 0.100000000:
            raise AssertionError("carry-forward age exceeds 0.1 seconds")
        return sample["roles"][role]

    merged_rss = []
    for when_tick in sorted(
        {sample["qpc_tick"] for sample in inner_samples + outer_samples}
    ):
        observations = {
            "O": [latest(outer_samples, when_tick, "O")],
            "S": [
                latest(inner_samples, when_tick, "S"),
                latest(outer_samples, when_tick, "S"),
            ],
            "L": [latest(inner_samples, when_tick, "L")],
            "W": [latest(inner_samples, when_tick, "W")],
        }
        total = 0
        for role, candidates in observations.items():
            created = [row for row in candidates if row["state"] != "NOT_CREATED"]
            if not created:
                continue
            observed_identities = {
                (row["pid"], row["creation_filetime"]) for row in created
            }
            if observed_identities != identities_by_role[role]:
                raise AssertionError("ambiguous carried process identity")
            if any(row["state"] == "ALIVE" for row in created):
                # S is deliberately sampled by both streams and is counted once,
                # at the conservative maximum of the two carried observations.
                total += max(row["current_working_set_bytes"] for row in created)
        merged_rss.append(total)
    lifetime_peak = sum(
        max(
            sample["roles"][role]["peak_working_set_bytes"]
            for samples in (
                (inner_samples, outer_samples) if role == "S" else
                ((outer_samples,) if role == "O" else (inner_samples,))
            )
            for sample in samples
        )
        for role in ("O", "S", "L", "W")
    )
    return {
        "charged_process_roles": ["O", "S", "L", "W"],
        "cpu_100ns_by_role": cpu,
        "cpu_seconds_sum": sum(cpu.values()) / 10_000_000,
        "full_wall_seconds": (
            outer["terminal_endpoint_filetime"] - outer["o_process_creation_filetime"]
        ) / 10_000_000,
        "inner_sample_count": len(inner_samples),
        "lifetime_peak_upper_bytes": lifetime_peak,
        "max_merged_concurrent_working_set_bytes": max(merged_rss),
        "max_observed_sampling_gap_seconds": max_gap,
        "o_process_creation_filetime": outer["o_process_creation_filetime"],
        "outer_sample_count": len(outer_samples),
        "rss_gate_bytes": max(max(merged_rss), lifetime_peak),
        "scientific_stop_wall_seconds": (
            inner["scientific_stop_filetime"] - outer["o_process_creation_filetime"]
        ) / 10_000_000,
        "terminal_endpoint_filetime": outer["terminal_endpoint_filetime"],
    }


def _checkpoint(event_id: str) -> dict:
    return {
        "artifact": "M245_DUMMY_COMPLETE_EVENT_CHECKPOINT",
        "complete_event_id": event_id,
        "next_invocation_only": True,
        "schema": "m245-dummy-complete-event-checkpoint-v1",
        "status": "PASS_DUMMY_TRANSPORT_ONLY",
    }


def _valid_receipt(
    shard_id: int = 0,
    invocation_index: int = 1,
    *,
    prior_receipt: dict | None = None,
) -> dict:
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    namespace = _expected_namespace(shard_id, invocation_index)
    ledger = []
    request_index = 0
    for engine, role in (("primary", "nested_plackett"), ("replica", "nested_unary")):
        for precision_dps in (80, 100):
            context = {
                "shard_id": shard_id,
                "invocation_index": invocation_index,
                "event_id": event_id,
                "engine": engine,
                "precision_dps": precision_dps,
            }
            ledger.extend(
                [
                    _quad_call(request_index, completion_index=request_index + 1, **context),
                    _quad_call(
                        request_index + 1,
                        role=role,
                        parent_request_index=request_index,
                        nesting_depth=1,
                        completion_index=request_index,
                        **context,
                    ),
                ]
            )
            request_index += 2
    ledger_hash = _sha256_bytes(_canonical_json_bytes(ledger))
    meter_payload = _meter_payload()
    event_payload = _event_result(
        event_id,
        shard_id=shard_id,
        invocation_index=invocation_index,
    )
    checkpoint_payload = _checkpoint(event_id)
    if invocation_index == 1:
        if prior_receipt is not None:
            raise AssertionError("invocation one has no predecessor")
        prior_binding = None
    else:
        if prior_receipt is None:
            prior_receipt = _valid_receipt(shard_id, 1)
        prior_namespace = _expected_namespace(shard_id, 1)
        prior_receipt_bytes = _canonical_json_bytes(prior_receipt)
        prior_binding = [
            {
                "bytes": prior_receipt[f"{kind}_publication"]["bytes"],
                "device": prior_receipt[f"{kind}_publication"]["device"],
                "event_id": prior_receipt["event_id"],
                "file_kind": kind,
                "inode": prior_receipt[f"{kind}_publication"]["inode"],
                "path": prior_namespace[kind],
                "sha256": prior_receipt[f"{kind}_publication"]["sha256"],
            }
            for kind in ("result", "checkpoint", "meter")
        ]
        prior_binding.append(
            {
                "bytes": len(prior_receipt_bytes),
                "device": 1,
                "event_id": prior_receipt["event_id"],
                "file_kind": "invocation_receipt",
                "inode": 2,
                "path": prior_namespace["invocation_receipt"],
                "sha256": _sha256_bytes(prior_receipt_bytes),
            }
        )
    return {
        "artifact": "M245_SHARD_INVOCATION_RECEIPT",
        "authority_sha256": _authority_sha256(),
        "checkpoint_publication": _publication(
            namespace["checkpoint"], raw=_canonical_json_bytes(checkpoint_payload)
        ),
        "child_environment": {
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        },
        "child_environment_sha256": "8" * 64,
        "event_id": event_id,
        "firewall": _firewall(),
        "intent_publication": _publication(namespace["intent"], "a"),
        "invocation_index": invocation_index,
        "job_census": {
            "active_process_limit": 2,
            "distinct_job_pids": [201, 202],
            "job_roles": ["L", "W"],
            "total_processes": 2,
            "worker_children": 0,
        },
        "meter_publication": _publication(
            namespace["meter"], raw=_canonical_json_bytes(meter_payload)
        ),
        "no_retry": True,
        "path_state": {
            "all_current_paths_initially_absent": True,
            "all_prior_paths_exact": invocation_index == 2,
            "no_unlisted_write": True,
            "temporary_paths_absent_after_publication": True,
        },
        "prior_invocation_files": prior_binding,
        "process_identities": {
            "S": _identity("S", 200, 199, shard_id=shard_id, invocation_index=invocation_index),
            "L": _identity("L", 201, 200, shard_id=shard_id, invocation_index=invocation_index),
            "W": _identity("W", 202, 201, shard_id=shard_id, invocation_index=invocation_index),
        },
        "quad_call_ledger": ledger,
        "quad_call_ledger_sha256": ledger_hash,
        "quad_gateway": {
            "actual_mp_quad_call_count": len(ledger),
            "all_calls_pass": True,
            "cache_hit_count": 0,
            "completion_request_order": [1, 0, 3, 2, 5, 4, 7, 6],
            "gateway_source_sha256": "d" * 64,
            "nested_call_count": 4,
            "outer_call_count": 4,
            "outer_panel_error_sums_mpf": {
                f"{engine}:{dps}:dummy_scalar": _mpf(0, 1, -300, 1)
                for engine in ("primary", "replica")
                for dps in (80, 100)
            },
            "request_count": len(ledger),
        },
        "resource_meter": _resource_meter(meter_payload),
        "result_publication": _publication(
            namespace["result"], raw=_canonical_json_bytes(event_payload)
        ),
        "schema": "m245-shard-invocation-receipt-v1",
        "shard_id": shard_id,
        "status": "PROVISIONAL_INNER_RECEIPT_NO_INVOCATION_PASS",
        "stderr_empty": True,
        "stdout_records": ["M245_W_READY", "M245_W_DONE"],
    }


def _inner_artifact_bindings(receipt: dict) -> list[dict]:
    rows = []
    for kind in ("result", "checkpoint", "meter"):
        publication = receipt[f"{kind}_publication"]
        rows.append(
            {
                "bytes": publication["bytes"],
                "device": publication["device"],
                "event_id": receipt["event_id"],
                "file_kind": kind,
                "inode": publication["inode"],
                "invocation_index": receipt["invocation_index"],
                "path": publication["path"],
                "sha256": publication["sha256"],
            }
        )
    raw = _canonical_json_bytes(receipt)
    rows.append(
        {
            "bytes": len(raw),
            "device": 1,
            "event_id": receipt["event_id"],
            "file_kind": "provisional_receipt",
            "inode": 2,
            "invocation_index": receipt["invocation_index"],
            "path": _expected_namespace(
                receipt["shard_id"], receipt["invocation_index"]
            )["invocation_receipt"],
            "sha256": _sha256_bytes(raw),
        }
    )
    return rows


def _valid_terminal_witness(
    receipt: dict,
    *,
    prior_witness: dict | None = None,
    final_shard_receipt: dict | None = None,
) -> dict:
    shard_id = receipt["shard_id"]
    invocation_index = receipt["invocation_index"]
    namespace = _expected_namespace(shard_id, invocation_index)
    inner_meter = _meter_payload()
    outer_meter = _outer_meter_payload(invocation_index)
    if invocation_index == 1:
        if prior_witness is not None or final_shard_receipt is not None:
            raise AssertionError("invocation one cannot bind a predecessor or final shard")
        prior_files = None
        final_binding = None
        status = "PASS_M245_INVOCATION_BOUND"
    else:
        if prior_witness is None or final_shard_receipt is None:
            raise AssertionError("invocation two witness requires predecessor and final shard")
        prior_raw = _canonical_json_bytes(prior_witness)
        prior_files = copy.deepcopy(prior_witness["inner_artifacts"])
        prior_files.append(
            {
                "bytes": len(prior_raw),
                "device": 1,
                "event_id": prior_witness["event_id"],
                "file_kind": "terminal_witness",
                "inode": 2,
                "invocation_index": 1,
                "path": _expected_namespace(shard_id, 1)["terminal_witness"],
                "sha256": _sha256_bytes(prior_raw),
                "status": prior_witness["status"],
            }
        )
        final_raw = _canonical_json_bytes(final_shard_receipt)
        final_binding = {
            "bytes": len(final_raw),
            "device": 1,
            "inode": 2,
            "path": namespace["final_shard_receipt"],
            "sha256": _sha256_bytes(final_raw),
            "status": final_shard_receipt["status"],
        }
        status = "PASS_M245_SHARD_BOUND"
    return {
        "artifact": "M245_OUTER_TERMINAL_INVOCATION_WITNESS",
        "schema": "m245-outer-terminal-invocation-witness-v1",
        "shard_id": shard_id,
        "invocation_index": invocation_index,
        "event_id": receipt["event_id"],
        "authority_sha256": _authority_sha256(),
        "inner_artifacts": _inner_artifact_bindings(receipt),
        "inner_meter": copy.deepcopy(inner_meter),
        "prior_invocation_files": prior_files,
        "outer_meter": outer_meter,
        "process_identities": {
            "O": _identity("O", 199, 100, shard_id=shard_id, invocation_index=invocation_index),
            "S": _identity("S", 200, 199, shard_id=shard_id, invocation_index=invocation_index),
            "L": _identity("L", 201, 200, shard_id=shard_id, invocation_index=invocation_index),
            "W": _identity("W", 202, 201, shard_id=shard_id, invocation_index=invocation_index),
        },
        "job_census": copy.deepcopy(receipt["job_census"]),
        "s_exit": {
            "exit_code": 0,
            "handle_retained_through_exit": True,
            "identity": {"creation_filetime": 10_000_000_200, "pid": 200},
        },
        "resource_meter": _terminal_resource_meter(inner_meter, outer_meter),
        "final_shard_receipt": final_binding,
        "firewall": _firewall(),
        "status": status,
    }


def _expected_namespace(shard_id: int, invocation_index: int) -> dict:
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


def _ordered_intent_paths() -> list[str]:
    paths: list[str] = []
    for shard_id in ASSIGNMENTS:
        for invocation_index in (1, 2):
            namespace = _expected_namespace(shard_id, invocation_index)
            paths.append(namespace["intent"])
    return paths


def _external_zero_intent_census(root: Path) -> tuple[dict, bytes]:
    expected = _ordered_intent_paths()
    observations = []
    for path in expected:
        try:
            os.lstat(root / path)
        except FileNotFoundError:
            observations.append({"lstat": "ABSENT", "path": path})
        else:
            observations.append({"lstat": "PRESENT", "path": path})
    present_count = sum(row["lstat"] == "PRESENT" for row in observations)
    payload = {
        "artifact": "M245_PRETRIGGER_ZERO_INTENT_CENSUS",
        "argv": [
            STDLIB_PYTHON,
            "-I",
            "-B",
            "-S",
            "-u",
            str((HERE / "run_m245_scientific_shard.py").resolve()),
            "--emit-pretrigger-zero-intent-census",
        ],
        "cwd": AUTHORITY_CWD,
        "observer_identity": "dummy-codex-test-observer",
        "observations": observations,
        "observed_present_count": present_count,
        "ordered_intent_paths": expected,
        "repository_parent_head": "e" * 40,
        "resolved_shard_directory": str(root.resolve()),
        "runner_source_sha256": _authority_sha256()["run_m245_scientific_shard.py"],
        "schema": "m245-pretrigger-zero-intent-census-v1",
        "utc_interval": {
            "end": "2026-08-10T00:00:01Z",
            "start": "2026-08-10T00:00:00Z",
        },
    }
    raw = _canonical_json_bytes(payload)
    if present_count:
        raise AssertionError("dummy external observer found a preexisting intent")
    return payload, raw


def _zero_intent_binding(root: Path | None = None) -> dict:
    if root is None:
        observations = [{"lstat": "ABSENT", "path": path} for path in _ordered_intent_paths()]
        payload = {
            "artifact": "M245_PRETRIGGER_ZERO_INTENT_CENSUS",
            "argv": [
                STDLIB_PYTHON,
                "-I",
                "-B",
                "-S",
                "-u",
                str((HERE / "run_m245_scientific_shard.py").resolve()),
                "--emit-pretrigger-zero-intent-census",
            ],
            "cwd": AUTHORITY_CWD,
            "observer_identity": "dummy-codex-test-observer",
            "observations": observations,
            "observed_present_count": 0,
            "ordered_intent_paths": _ordered_intent_paths(),
            "repository_parent_head": "e" * 40,
            "resolved_shard_directory": "DUMMY_RESOLVED_SHARD_DIRECTORY",
            "runner_source_sha256": _authority_sha256()["run_m245_scientific_shard.py"],
            "schema": "m245-pretrigger-zero-intent-census-v1",
            "utc_interval": {"end": "2026-08-10T00:00:01Z", "start": "2026-08-10T00:00:00Z"},
        }
        raw = _canonical_json_bytes(payload)
    else:
        payload, raw = _external_zero_intent_census(root)
    return {
        "argv": payload["argv"],
        "bytes": len(raw),
        "cwd": payload["cwd"],
        "observed_present_count": payload["observed_present_count"],
        "ordered_intent_paths": payload["ordered_intent_paths"],
        "path": "M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json",
        "repository_commit": "f" * 40,
        "repository_parent_head": payload["repository_parent_head"],
        "runner_source_sha256": payload["runner_source_sha256"],
        "sha256": _sha256_bytes(raw),
    }


def _process_argv_contract() -> dict:
    runner_path = str((HERE / "run_m245_scientific_shard.py").resolve())
    launcher_path = str((HERE / "launch_m245_scientific_invocation.py").resolve())
    worker_path = str((HERE / "m245_scientific_worker.py").resolve())
    return {
        "L": {
            "argv": [VENV_PYTHON, "-B", "-P", "-s", "-S", "-u", worker_path],
            "cwd": AUTHORITY_CWD,
            "image_sha256": VENV_PYTHON_SHA256,
            "source_sha256": _authority_sha256()["m245_scientific_worker.py"],
        },
        "O_by_attempt": [
            {
                "argv": [
                    STDLIB_PYTHON,
                    "-I",
                    "-B",
                    "-S",
                    "-u",
                    launcher_path,
                    "--shard-id",
                    str(shard_id),
                    "--invocation-index",
                    str(invocation_index),
                ],
                "cwd": AUTHORITY_CWD,
                "event_id": ASSIGNMENTS[shard_id][invocation_index - 1],
                "invocation_index": invocation_index,
                "shard_id": shard_id,
            }
            for shard_id in ASSIGNMENTS
            for invocation_index in (1, 2)
        ],
        "O_image_sha256": STDLIB_PYTHON_SHA256,
        "O_source_sha256": _authority_sha256()["launch_m245_scientific_invocation.py"],
        "S_by_attempt": [
            {
                "argv": [
                    STDLIB_PYTHON,
                    "-I",
                    "-B",
                    "-S",
                    "-u",
                    runner_path,
                    "--shard-id",
                    str(shard_id),
                    "--invocation-index",
                    str(invocation_index),
                ],
                "cwd": AUTHORITY_CWD,
                "event_id": ASSIGNMENTS[shard_id][invocation_index - 1],
                "invocation_index": invocation_index,
                "shard_id": shard_id,
            }
            for shard_id in ASSIGNMENTS
            for invocation_index in (1, 2)
        ],
        "S_image_sha256": STDLIB_PYTHON_SHA256,
        "S_source_sha256": _authority_sha256()["run_m245_scientific_shard.py"],
        "W": {
            "cwd": AUTHORITY_CWD,
            "image_sha256": STDLIB_PYTHON_SHA256,
            "source_sha256": _authority_sha256()["m245_scientific_worker.py"],
            "sys_argv": [worker_path],
            "sys_executable": VENV_PYTHON,
        },
        "process_tree": "O->S->L->W",
    }


def _valid_trigger(zero_intent_census: dict | None = None) -> dict:
    audits = [
        {
            "receipt_path": f"M245_SCIENTIFIC_STATIC_AUDIT_{label}_20260810.json",
            "reviewer_id": f"reviewer-{label.lower()}",
            "sha256": _authority_sha256()[f"M245_SCIENTIFIC_STATIC_AUDIT_{label}_20260810.json"],
            "status": "PASS_STATIC_M245_SCIENTIFIC_BUNDLE_ONLY",
        }
        for label in ("A", "B")
    ]
    return {
        "agent_channel_binding": {
            "commit_sha": "c" * 40,
            "entry_sha256": "d" * 64,
            "path": "AGENT_CHANNEL.md",
        },
        "aggregation_contract": {
            "authorization_path": "M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json",
            "authorization_schema": "m245-aggregation-input-authorization-v1",
            "result_schema": "m245-aggregated-spectrum-v1",
            "receipt_schema": "m245-aggregation-receipt-v1",
            "source_sha256": _authority_sha256()["aggregate_m245_spectrum.py"],
        },
        "assignments": {str(key): list(value) for key, value in ASSIGNMENTS.items()},
        "authority_commit_v1": "c4468c3d330f968ce1a3b376d56aa1f6b640e709",
        "authority_erratum2_commit": "979f7c35334ff0df09ad134255fddf23f944237f",
        "authority_repair_commit": "853b30cf5ef8f87788aab6cee73218edddd6f466",
        "authority_sha256": {name: _authority_sha256()[name] for name in AUTHORITY_HASH_KEYS},
        "final_shard_receipt_contract": {
            "paths": [
                f"M245_S{shard_id}_FINAL_RECEIPT_20260810.json"
                for shard_id in ASSIGNMENTS
            ],
            "schema": "m245-final-shard-receipt-v2",
        },
        "independent_static_audits": audits,
        "process_argv_contract": _process_argv_contract(),
        "scientific_source_sha256": {
            name: _authority_sha256()[name] for name in SCIENTIFIC_SOURCE_HASH_KEYS
        },
        "zero_intent_census": _zero_intent_binding() if zero_intent_census is None else zero_intent_census,
    }


def _complete_launch_census() -> list[dict]:
    rows = []
    for ordinal, (shard_id, invocation_index) in enumerate(
        (pair for shard_id in ASSIGNMENTS for pair in ((shard_id, 1), (shard_id, 2)))
    ):
        roles = {}
        for offset, role in enumerate(("O", "S", "L", "W")):
            pid = 1000 + ordinal * 10 + offset
            roles[role] = {
                "creation_filetime": 40_000_000_000 + ordinal * 100 + offset,
                "pid": pid,
                "role": role,
            }
        rows.append(
            {
                "event_id": ASSIGNMENTS[shard_id][invocation_index - 1],
                "intent_sha256": format(ordinal + 1, "x") * 64,
                "invocation_index": invocation_index,
                "launch_slot": ordinal,
                "process_identities": roles,
                "shard_id": shard_id,
                "status": "PASS",
            }
        )
    return rows


def _dummy_primary_result(event_id: str, precision_dps: int) -> dict:
    degrees = list(range(9))
    R = [f"{0.125 + 0.01 * q:.17g}" for q in degrees]
    G = [
        [
            f"{(1.0 + 0.05 * q) if m == q else 0.001 / (1 + abs(m - q)):.17g}"
            for q in degrees
        ]
        for m in degrees
    ]
    d = [f"{0.2 / (q + 1):.17g}" for q in degrees]
    beta = [f"{0.1 / (q + 1):.17g}" for q in degrees]
    leading_blocks = []
    for Q in degrees:
        P = 0.2 + 0.05 * Q
        V = 2.0 - P
        V_beta = V + 0.025
        direct = {
            "observed": f"{V:.17g}",
            "reference": f"{V:.17g}",
            "pass": True,
        }
        direct_beta = {
            "observed": f"{V_beta:.17g}",
            "reference": f"{V_beta:.17g}",
            "pass": True,
        }
        leading_blocks.append(
            {
                "Q": Q,
                "c": [f"{0.1 / (q + 1):.17g}" for q in range(Q + 1)],
                "P": f"{P:.17g}",
                "V": f"{V:.17g}",
                "lambda_min": f"{0.5 + 0.01 * Q:.17g}",
                "lambda_max": f"{1.5 + 0.01 * Q:.17g}",
                "lambda_ratio": f"{(0.5 + 0.01 * Q) / (1.5 + 0.01 * Q):.17g}",
                "condition_2": f"{(1.5 + 0.01 * Q) / (0.5 + 0.01 * Q):.17g}",
                "cholesky_pass": True,
                "solve_relative_inf_residual": "1e-30",
                "solve_pass": True,
                "energy_gate": {"pass": True, "tau_K": "4e-10"},
                "V_beta": f"{V_beta:.17g}",
                "ordinary_beta_identity": {
                    "lhs": f"{V_beta - V:.17g}",
                    "rhs": f"{V_beta - V:.17g}",
                    "gap": f"{V_beta - V:.17g}",
                    "pass": True,
                },
                "direct_residual": copy.deepcopy(direct) if Q in (0, 4, 8) else None,
                "direct_beta_residual": (
                    copy.deepcopy(direct_beta) if Q in (0, 4, 8) else None
                ),
            }
        )
    return {
        "artifact": "M245_PRIMARY_EVENT_PRECISION",
        "schema": "m245-primary-event-v1",
        "event_id": event_id,
        "precision_dps": precision_dps,
        "fixture_array_sha256": {"C": "c" * 64, "mu": "d" * 64},
        "degrees": degrees,
        "R": R,
        "G": G,
        "mu_rb": "0.375",
        "K": "2",
        "d": d,
        "beta": beta,
        "leading_blocks": leading_blocks,
        "analytic_direct_checks": {
            "R": [
                {"q": q, "analytic": R[q], "direct": R[q], "pass": True}
                for q in degrees
            ],
            "G_upper": [
                {
                    "m": m,
                    "q": q,
                    "analytic": G[m][q],
                    "direct": G[m][q],
                    "pass": True,
                }
                for q in degrees
                for m in range(q + 1)
            ],
            "all_pass": True,
        },
        "quadrature_audit": {
            "all_calls_pass": True,
            "error_semantics": "heuristic_diagnostic_estimate_not_interval_certificate",
            "interval_certified": False,
            "observed_call_count": 2,
        },
        "firewall": {"network": False},
    }


def _dummy_replica_result(event_id: str, precision_dps: int) -> dict:
    nodes = [
        "0", "0.00390625", "-0.00390625", "0.25", "-0.25", "1", "-1",
        "2.5", "-2.5", "5", "-5", "8", "-8", "10", "-10", "16", "-16",
    ]
    return {
        "artifact": "M245_REPLICA_EVENT_PRECISION",
        "schema": "m245-replica-event-v1",
        "event_id": event_id,
        "precision_dps": precision_dps,
        "fixture_array_sha256": {"C": "c" * 64, "mu": "d" * 64},
        "fixed_b_nodes": nodes,
        "b_rep_at_nodes": [f"{0.25 + index / 100:.17g}" for index in range(17)],
        "mu_rep": "0.375",
        "M_same": "3.25",
        "M_cross": "0.75",
        "K_rep": "1.859375",
        "quadrature_audit": {
            "all_calls_pass": True,
            "error_semantics": "heuristic_diagnostic_estimate_not_interval_certificate",
            "interval_certified": False,
            "observed_call_count": 2,
        },
        "firewall": {"network": False, "primary_import": False},
    }


def _event_result(
    event_id: str,
    *,
    shard_id: int = 0,
    invocation_index: int = 1,
) -> dict:

    curve_labels = {
        "Gompertz": "ENDPOINT_CONTROL/NA" if event_id == "E00" else "FALSIFIED",
        "geometric": "ENDPOINT_CONTROL/NA" if event_id == "E00" else "FALSIFIED",
        "logistic": "ENDPOINT_CONTROL/NA" if event_id == "E00" else "FALSIFIED",
    }
    return {
        "event_id": event_id,
        "fixture_array_sha256": {"C": "c" * 64, "mu": "d" * 64},
        "primary_by_precision": {
            "80": _dummy_primary_result(event_id, 80),
            "100": _dummy_primary_result(event_id, 100),
        },
        "replica_by_precision": {
            "80": _dummy_replica_result(event_id, 80),
            "100": _dummy_replica_result(event_id, 100),
        },
        "cross_precision_gates": {"pass": True},
        "primary_replica_gates": {"pass": True},
        "analytic_solve_energy_beta_gates": {"pass": True},
        "curve_report": {"labels": curve_labels},
        "quad_gateway_ledger_refs": [
            {
                "count": 2,
                "engine": engine,
                "precision_dps": dps,
                "sha256": _sha256_bytes(
                    _canonical_json_bytes(
                        [
                            _quad_call(
                                (
                                    (0 if engine == "primary" else 4)
                                    + (0 if dps == 80 else 2)
                                ),
                                shard_id=shard_id,
                                invocation_index=invocation_index,
                                event_id=event_id,
                                engine=engine,
                                precision_dps=dps,
                                completion_index=(
                                    (1 if engine == "primary" else 5)
                                    + (0 if dps == 80 else 2)
                                ),
                            ),
                            _quad_call(
                                (
                                    (1 if engine == "primary" else 5)
                                    + (0 if dps == 80 else 2)
                                ),
                                shard_id=shard_id,
                                invocation_index=invocation_index,
                                event_id=event_id,
                                engine=engine,
                                precision_dps=dps,
                                role=(
                                    "nested_plackett"
                                    if engine == "primary"
                                    else "nested_unary"
                                ),
                                parent_request_index=(
                                    (0 if engine == "primary" else 4)
                                    + (0 if dps == 80 else 2)
                                ),
                                nesting_depth=1,
                                completion_index=(
                                    (0 if engine == "primary" else 4)
                                    + (0 if dps == 80 else 2)
                                ),
                            ),
                        ]
                    )
                ),
            }
            for engine in ("primary", "replica")
            for dps in (80, 100)
        ],
        "only_future_bound": "0<=additional_explainable_energy_beyond_Q8<=K-P8",
        "gate_verdict": "PASS",
        "firewall": _firewall(),
        "forbidden_credit": True,
    }


def _valid_final_receipt(
    shard_id: int,
    first: dict | None = None,
    second: dict | None = None,
    first_witness: dict | None = None,
) -> tuple[dict, dict, dict, dict, dict]:
    first = _valid_receipt(shard_id, 1) if first is None else first
    second = _valid_receipt(shard_id, 2, prior_receipt=first) if second is None else second
    first_witness = (
        _valid_terminal_witness(first) if first_witness is None else first_witness
    )
    receipts = (first, second)
    first_witness_raw = _canonical_json_bytes(first_witness)
    final = {
        "artifact": "M245_FINAL_SHARD_RECEIPT",
        "schema": "m245-final-shard-receipt-v2",
        "shard_id": shard_id,
        "events_in_order": list(ASSIGNMENTS[shard_id]),
        "event_results": [
            _event_result(
                event_id,
                shard_id=shard_id,
                invocation_index=invocation_index,
            )
            for invocation_index, event_id in enumerate(ASSIGNMENTS[shard_id], 1)
        ],
        "invocation_receipts": [
            {
                "event_id": receipt["event_id"],
                "invocation_index": index,
                "path": _expected_namespace(shard_id, index)["invocation_receipt"],
                "sha256": _sha256_bytes(_canonical_json_bytes(receipt)),
                "status": receipt["status"],
            }
            for index, receipt in enumerate(receipts, 1)
        ]
        + [
            {
                "event_id": first_witness["event_id"],
                "invocation_index": 1,
                "path": _expected_namespace(shard_id, 1)["terminal_witness"],
                "sha256": _sha256_bytes(first_witness_raw),
                "status": first_witness["status"],
            }
        ],
        "authority_sha256": _authority_sha256(),
        "resource_union": {
            "invocation_one_terminal_witness": {
                "bytes": len(first_witness_raw),
                "device": 1,
                "inode": 2,
                "path": _expected_namespace(shard_id, 1)["terminal_witness"],
                "sha256": _sha256_bytes(first_witness_raw),
                "status": first_witness["status"],
                "terminal_witness": copy.deepcopy(first_witness),
            },
            "invocation_two_inner_meter": {
                "bytes": second["meter_publication"]["bytes"],
                "device": second["meter_publication"]["device"],
                "inode": second["meter_publication"]["inode"],
                "path": _expected_namespace(shard_id, 2)["meter"],
                "raw_meter": _meter_payload(),
                "resource_meter": copy.deepcopy(second["resource_meter"]),
                "sha256": second["meter_publication"]["sha256"],
            },
            "invocation_two_terminal_witness_required": True,
        },
        "no_cross_shard_cache": True,
        "firewall": _firewall(),
        "status": "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS",
    }
    second_witness = _valid_terminal_witness(
        second,
        prior_witness=first_witness,
        final_shard_receipt=final,
    )
    return final, first, second, first_witness, second_witness


def _dummy_intent(
    shard_id: int,
    invocation_index: int,
    *,
    trigger_sha256: str = "d" * 64,
) -> dict:
    return {
        "artifact": "M245_SHARD_INVOCATION_INTENT",
        "schema": "m245-shard-invocation-intent-v1",
        "shard_id": shard_id,
        "invocation_index": invocation_index,
        "event_id": ASSIGNMENTS[shard_id][invocation_index - 1],
        "trigger_entry_sha256": trigger_sha256,
        "trigger_commit": "c" * 40,
        "namespace": _expected_namespace(shard_id, invocation_index),
        "status": "DURABLE_ATTEMPT_BURNED",
    }


def _write_dummy_completed_attempt(
    root: Path,
    shard_id: int,
    invocation_index: int,
    *,
    trigger_sha256: str = "d" * 64,
    terminal_status: str | None = None,
) -> None:
    namespace = _expected_namespace(shard_id, invocation_index)
    intent = _dummy_intent(
        shard_id,
        invocation_index,
        trigger_sha256=trigger_sha256,
    )
    (root / namespace["intent"]).write_bytes(_canonical_json_bytes(intent))
    if invocation_index == 1:
        receipt = _valid_receipt(shard_id, 1)
        witness = _valid_terminal_witness(receipt)
        final = None
    else:
        final, _first, receipt, _first_witness, witness = _valid_final_receipt(shard_id)
    payloads = {
        "result": _event_result(
            receipt["event_id"],
            shard_id=shard_id,
            invocation_index=invocation_index,
        ),
        "checkpoint": _checkpoint(receipt["event_id"]),
        "meter": _meter_payload(),
        "invocation_receipt": receipt,
        "terminal_witness": witness,
    }
    if terminal_status is not None:
        payloads["terminal_witness"] = copy.deepcopy(witness)
        payloads["terminal_witness"]["status"] = terminal_status
    for kind, payload in payloads.items():
        (root / namespace[kind]).write_bytes(_canonical_json_bytes(payload))
    if final is not None:
        (root / namespace["final_shard_receipt"]).write_bytes(
            _canonical_json_bytes(final)
        )


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    return imported


def _mp_quad_call_owners(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    owners: list[str] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute) and node.func.attr == "quad":
                owners.append(self.stack[-1] if self.stack else "<module>")
            self.generic_visit(node)

    Visitor().visit(tree)
    return owners


class TestM245ShardNamespaceAndAPI(unittest.TestCase):
    def test_public_surface_and_complete_contract_are_exact(self) -> None:
        self.assertTrue(issubclass(runner.M245ShardContractError, Exception))
        self.assertTrue(issubclass(launcher.M245LaunchContractError, Exception))
        for name in RUNNER_PUBLIC_CALLABLES:
            self.assertTrue(callable(getattr(runner, name, None)), name)
        for name in LAUNCHER_PUBLIC_CALLABLES:
            self.assertTrue(callable(getattr(launcher, name, None)), name)
        self.assertEqual(runner.shard_contract(), SHARD_CONTRACT)
        self.assertEqual(launcher.launch_contract(), SHARD_CONTRACT)

    def test_every_shard_has_exactly_two_one_event_invocation_namespaces(self) -> None:
        all_final_paths: set[str] = set()
        all_paths: set[str] = set()
        for shard_id, events in ASSIGNMENTS.items():
            for invocation_index, event_id in enumerate(events, 1):
                observed = runner.shard_namespace(shard_id, invocation_index)
                expected = _expected_namespace(shard_id, invocation_index)
                self.assertEqual(observed, expected)
                self.assertEqual(tuple(observed), NAMESPACE_KEYS)
                self.assertIn(event_id, observed["result"])
                for key, path in observed.items():
                    if key == "directory_repo_relative":
                        continue
                    if key in {"final_shard_receipt_temp", "final_shard_receipt"}:
                        all_final_paths.add(path)
                    else:
                        self.assertNotIn(path, all_paths)
                        all_paths.add(path)
            self.assertEqual(len({
                runner.shard_namespace(shard_id, 1)["final_shard_receipt"],
                runner.shard_namespace(shard_id, 2)["final_shard_receipt"],
            }), 1)
        self.assertEqual(len(all_final_paths), 8)
        self.assertEqual(len(all_paths), 4 * 2 * 12)

    def test_attempt_burn_is_durable_intent_not_os_process_count(self) -> None:
        self.assertEqual(
            launcher.classify_attempt_failure(
                intent_durably_published=False,
                scientific_import_started=False,
                namespace_still_absent=True,
                committed_inputs_unchanged=True,
            ),
            "UNCONSUMED_STDLIB_PREFLIGHT_FAILURE",
        )
        for scientific_started in (False, True):
            self.assertEqual(
                launcher.classify_attempt_failure(
                    intent_durably_published=True,
                    scientific_import_started=scientific_started,
                    namespace_still_absent=False,
                    committed_inputs_unchanged=True,
                ),
                "CONSUMED_PERMANENT_LOCAL_KILL_NO_RELAUNCH",
            )
        with self.assertRaises(launcher.M245LaunchContractError):
            launcher.classify_attempt_failure(
                intent_durably_published=False,
                scientific_import_started=True,
                namespace_still_absent=True,
                committed_inputs_unchanged=True,
            )

    def test_complete_launch_census_is_eight_slots_and_thirty_two_os_identities(self) -> None:
        census = _complete_launch_census()
        summary = launcher.validate_complete_launch_census(census)
        self.assertEqual(summary["durable_attempt_launch_slots"], 8)
        self.assertEqual(summary["os_process_identity_count"], 32)
        self.assertEqual(summary["role_counts"], {"O": 8, "S": 8, "L": 8, "W": 8})
        mutations = [census[:-1]]
        changed = copy.deepcopy(census)
        changed[7]["process_identities"]["W"] = copy.deepcopy(
            changed[6]["process_identities"]["W"]
        )
        mutations.append(changed)
        changed = copy.deepcopy(census)
        changed[7]["launch_slot"] = 6
        mutations.append(changed)
        changed = copy.deepcopy(census)
        changed[7]["invocation_index"] = 3
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(runner.M245ShardContractError):
                launcher.validate_complete_launch_census(changed)

    def test_shard_request_is_ordered_two_invocation_fail_closed(self) -> None:
        for shard_id, events in ASSIGNMENTS.items():
            runner.validate_shard_request(shard_id, events, 1, False)
            runner.validate_shard_request(shard_id, events, 2, True)
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_shard_request(shard_id, tuple(reversed(events)), 1, False)
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_shard_request(shard_id, events, 2, False)
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_shard_request(shard_id, events, 3, True)
        with self.assertRaises(runner.M245ShardContractError):
            runner.validate_shard_request(4, ("E00", "E01"), 1, False)

    def test_trigger_binds_every_authority_source_audit_and_committed_channel_hash(self) -> None:
        trigger = _valid_trigger()
        runner.validate_trigger_payload(trigger)
        launcher.validate_trigger_payload(trigger)
        self.assertEqual(tuple(trigger), TRIGGER_KEYS)
        self.assertEqual(tuple(trigger["authority_sha256"]), AUTHORITY_HASH_KEYS)
        self.assertEqual(tuple(trigger["scientific_source_sha256"]), SCIENTIFIC_SOURCE_HASH_KEYS)
        self.assertEqual(len(trigger["independent_static_audits"]), 2)
        self.assertEqual(
            {row["reviewer_id"].casefold() for row in trigger["independent_static_audits"]},
            {"reviewer-a", "reviewer-b"},
        )
        mutations = []
        changed = copy.deepcopy(trigger)
        changed["zero_intent_census"]["observed_present_count"] = 1
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["independent_static_audits"][1]["reviewer_id"] = "REVIEWER-A"
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["independent_static_audits"][0]["status"] = "PENDING"
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["agent_channel_binding"]["entry_sha256"] = "0" * 64
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["authority_sha256"]["M245_FROZEN_MANIFEST_V2_20260810.json"] = "0" * 64
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        del changed["scientific_source_sha256"]["aggregate_m245_spectrum.py"]
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["process_argv_contract"]["S_by_attempt"][7]["argv"].append("--extra")
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["process_argv_contract"]["O_by_attempt"][0]["argv"][0] = VENV_PYTHON
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["process_argv_contract"]["L"]["cwd"] = "DUMMY_OTHER_CWD"
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["final_shard_receipt_contract"]["schema"] = "m245-final-shard-receipt-v1"
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["aggregation_contract"]["source_sha256"] = "0" * 64
        mutations.append(changed)
        changed = copy.deepcopy(trigger)
        changed["zero_intent_census"]["sha256"] = "0" * 64
        mutations.append(changed)
        for changed in mutations:
            with self.subTest(changed=changed):
                for validator, error in (
                    (runner.validate_trigger_payload, runner.M245ShardContractError),
                    (launcher.validate_trigger_payload, launcher.M245LaunchContractError),
                ):
                    with self.assertRaises(error):
                        validator(changed)

    def test_external_zero_intent_census_is_exact_and_each_S_rechecks_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload, raw = _external_zero_intent_census(root)
            binding = _zero_intent_binding(root)
            self.assertEqual(payload["ordered_intent_paths"], _ordered_intent_paths())
            self.assertEqual(payload["observed_present_count"], 0)
            self.assertEqual(binding["sha256"], _sha256_bytes(raw))
            runner.validate_trigger_payload(_valid_trigger(binding))
            runner.preflight_invocation_paths(root, shard_id=0, invocation_index=1)
            collision = root / _expected_namespace(0, 1)["intent"]
            collision.write_bytes(b"preexisting-intent\n")
            with self.assertRaises(AssertionError):
                _external_zero_intent_census(root)
            with self.assertRaises(runner.M245ShardContractError):
                runner.preflight_invocation_paths(root, shard_id=0, invocation_index=1)

    def test_present_intents_obey_exact_down_closed_partial_order_and_lexical_census(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_dummy_completed_attempt(root, 0, 1)
            runner.preflight_invocation_paths(root, shard_id=1, invocation_index=1)
            _write_dummy_completed_attempt(root, 3, 1)
            _write_dummy_completed_attempt(root, 3, 2)
            runner.preflight_invocation_paths(root, shard_id=2, invocation_index=1)

        cases = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_dummy_completed_attempt(root, 0, 1)
            (root / _expected_namespace(1, 1)["result_temp"]).write_bytes(b"collision\n")
            cases.append((root, 1, 1, "target temporary collision"))
            self._assert_preflight_refused(*cases[-1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / _expected_namespace(0, 1)["intent"]
            malformed.write_bytes(b"{}\n")
            self._assert_preflight_refused(root, 1, 1, "malformed present intent")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_dummy_completed_attempt(root, 0, 1)
            outside = root / "M245_S9_I1_E99_INTENT_20260810.json"
            outside.write_bytes(_canonical_json_bytes({"artifact": "OUTSIDE_CENSUS"}))
            self._assert_preflight_refused(root, 1, 1, "outside-census intent")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_dummy_completed_attempt(root, 0, 1)
            _write_dummy_completed_attempt(root, 1, 2)
            self._assert_preflight_refused(root, 2, 1, "invocation two without one")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_dummy_completed_attempt(
                root,
                0,
                1,
                terminal_status="FAILED_PERMANENT_LOCAL_KILL",
            )
            self._assert_preflight_refused(root, 1, 1, "failed root predecessor")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_dummy_completed_attempt(root, 0, 1)
            _write_dummy_completed_attempt(root, 3, 1, trigger_sha256="e" * 64)
            self._assert_preflight_refused(root, 2, 1, "mixed trigger lineage")

    def _assert_preflight_refused(
        self,
        root: Path,
        shard_id: int,
        invocation_index: int,
        reason: str,
    ) -> None:
        with self.subTest(reason=reason):
            with self.assertRaises(runner.M245ShardContractError):
                runner.preflight_invocation_paths(
                    root,
                    shard_id=shard_id,
                    invocation_index=invocation_index,
                )


class TestM245QuadLedgerContract(unittest.TestCase):
    def test_lossless_mpf_and_endpoint_schemas_are_exact(self) -> None:
        entry = _quad_call(0)
        self.assertEqual(tuple(entry), QUAD_CALL_RECEIPT_KEYS)
        for key in ("saved_mp_eps_mpf", "returned_value_mpf", "returned_error_mpf"):
            self.assertEqual(tuple(entry[key]), MPF_TUPLE_KEYS)
            self.assertIsInstance(entry[key]["mantissa"], str)
        for key in ("interval_left", "interval_right"):
            self.assertEqual(tuple(entry[key]), ENDPOINT_KEYS)
        self.assertEqual(_endpoint("+inf"), {"kind": "+inf", "mpf": None})
        self.assertEqual(_decode_mpf_tuple(entry["returned_value_mpf"]), 1.0)
        self.assertEqual(
            entry["error_semantics"],
            "heuristic_diagnostic_estimate_not_interval_certificate",
        )
        self.assertFalse(entry["interval_certified"])
        self.assertLessEqual(
            _decode_mpf_tuple(entry["returned_error_mpf"]),
            _decode_mpf_tuple(entry["saved_mp_eps_mpf"]) / 8.0,
        )

    def test_ledger_is_complete_ordered_per_call_and_cache_scoped(self) -> None:
        receipt = _valid_receipt()
        ledger = receipt["quad_call_ledger"]
        summary = runner.validate_quad_call_ledger(
            ledger,
            shard_id=receipt["shard_id"],
            invocation_index=receipt["invocation_index"],
            event_id=receipt["event_id"],
        )
        self.assertEqual(summary["request_count"], 8)
        self.assertEqual(summary["actual_mp_quad_call_count"], 8)
        self.assertEqual(summary["cache_hit_count"], 0)
        self.assertEqual(summary["outer_call_count"], 4)
        self.assertEqual(summary["nested_call_count"], 4)
        self.assertEqual(summary["completion_request_order"], [1, 0, 3, 2, 5, 4, 7, 6])
        self.assertEqual(summary["nested_raw_error_sum_is_diagnostic_only"], True)
        self.assertTrue(summary["pass"])

    def test_cache_hit_is_a_logged_request_but_not_an_mp_quad_call(self) -> None:
        ledger = copy.deepcopy(_valid_receipt()["quad_call_ledger"])
        hit = copy.deepcopy(ledger[0])
        hit["request_index"] = 8
        hit["completion_index"] = 8
        hit["mp_quad_invoked"] = False
        hit["cache_disposition"] = "hit"
        ledger.append(hit)
        summary = runner.validate_quad_call_ledger(
            ledger,
            shard_id=0,
            invocation_index=1,
            event_id="E00",
        )
        self.assertEqual(summary["request_count"], 9)
        self.assertEqual(summary["actual_mp_quad_call_count"], 8)
        self.assertEqual(summary["cache_hit_count"], 1)

    def test_ledger_refuses_dropped_reordered_duplicate_or_failed_calls(self) -> None:
        base = _valid_receipt()["quad_call_ledger"]
        mutations = [
            base[:-1],
            list(reversed(base)),
            [base[0], copy.deepcopy(base[0]), *base[2:]],
        ]
        failed = copy.deepcopy(base)
        failed[1]["error_le_saved_mp_eps_over_8"] = False
        failed[1]["pass"] = False
        mutations.append(failed)
        wrong_policy = copy.deepcopy(base)
        wrong_policy[1]["maxdegree"] = 15
        mutations.append(wrong_policy)
        missing = copy.deepcopy(base)
        del missing[1]["returned_error_mpf"]
        mutations.append(missing)
        wrong_event = copy.deepcopy(base)
        wrong_event[1]["event_id"] = "DUMMY_OTHER"
        mutations.append(wrong_event)
        wrong_precision = copy.deepcopy(base)
        wrong_precision[1]["precision_dps"] = 100
        mutations.append(wrong_precision)
        wrong_role = copy.deepcopy(base)
        wrong_role[1]["call_role"] = "invented_role"
        mutations.append(wrong_role)
        wrong_method = copy.deepcopy(base)
        wrong_method[1]["method"] = "gauss-legendre"
        mutations.append(wrong_method)
        false_certificate = copy.deepcopy(base)
        false_certificate[1]["interval_certified"] = True
        mutations.append(false_certificate)
        inconsistent_error = copy.deepcopy(base)
        inconsistent_error[1]["returned_error_mpf"] = _mpf(0, 1, -295, 1)
        inconsistent_error[1]["error_le_saved_mp_eps_over_8"] = True
        mutations.append(inconsistent_error)
        inconsistent_bitcount = copy.deepcopy(base)
        inconsistent_bitcount[1]["returned_value_mpf"]["bitcount"] = 9
        mutations.append(inconsistent_bitcount)
        bad_endpoint = copy.deepcopy(base)
        bad_endpoint[1]["interval_left"] = {"kind": "+inf", "mpf": _mpf(0, 1, 0, 1)}
        mutations.append(bad_endpoint)
        unparented = copy.deepcopy(base)
        unparented[1]["parent_request_index"] = None
        mutations.append(unparented)
        uncompleted = copy.deepcopy(base)
        uncompleted[1]["completion_index"] = None
        mutations.append(uncompleted)
        direct_bypass = copy.deepcopy(base)
        direct_bypass[1]["mp_quad_invoked"] = False
        direct_bypass[1]["cache_disposition"] = "miss"
        mutations.append(direct_bypass)
        scope_cross = copy.deepcopy(base)
        scope_cross[1]["cache_scope_id"] = "primary:OTHER_EVENT:80:fresh"
        mutations.append(scope_cross)
        for ledger in mutations:
            receipt = _valid_receipt()
            receipt["quad_call_ledger"] = ledger
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_invocation_receipt(receipt, _meter_payload())

    def test_gateway_summary_must_be_reconstructed_from_the_ledger(self) -> None:
        receipt = _valid_receipt()
        runner.validate_invocation_receipt(receipt, _meter_payload())
        for key, value in (
            ("request_count", 7),
            ("actual_mp_quad_call_count", 7),
            ("cache_hit_count", 1),
            ("completion_request_order", list(range(8))),
        ):
            changed = copy.deepcopy(receipt)
            changed["quad_gateway"][key] = value
            with self.subTest(key=key):
                with self.assertRaises(runner.M245ShardContractError):
                    runner.validate_invocation_receipt(changed, _meter_payload())


class TestM245ShardPublicationMeterAndReceipt(unittest.TestCase):
    def test_dummy_immutable_publication_is_hardlink_create_if_absent(self) -> None:
        for owner, error in (
            (runner, runner.M245ShardContractError),
            (launcher, launcher.M245LaunchContractError),
        ):
            payload = {"artifact": "DUMMY_NOT_M245_SCIENCE", "owner": owner.__name__}
            with self.subTest(owner=owner.__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                temp = root / ".dummy.json.tmp"
                final = root / "dummy.json"
                receipt = owner.publish_immutable_json(temp, final, payload)
                self.assertFalse(temp.exists())
                self.assertTrue(final.is_file())
                self.assertEqual(final.read_bytes(), _canonical_json_bytes(payload))
                self.assertTrue(receipt["source_final_same_device_inode"])
                self.assertTrue(receipt["temporary_unlinked"])
                self.assertTrue(receipt["reopened_bytes_equal"])
                self.assertEqual(receipt["sha256"], _sha256_bytes(final.read_bytes()))
                with self.assertRaises((error, FileExistsError)):
                    owner.publish_immutable_json(temp, final, payload)

    def test_dummy_end_to_end_outer_supervisor_redirector_worker_probe_is_observable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            probe = launcher.run_dummy_transport_probe(
                root,
                event_id="DUMMY_TRANSPORT_PROBE_NOT_IN_FROZEN_CENSUS",
            )
            self.assertEqual(probe["artifact"], "M245_DUMMY_TRANSPORT_PROBE")
            self.assertEqual(probe["event_id"], "DUMMY_TRANSPORT_PROBE_NOT_IN_FROZEN_CENSUS")
            self.assertEqual(probe["status"], "PASS_DUMMY_TRANSPORT_ONLY")
            self.assertEqual(probe["scientific_imports"], [])
            self.assertEqual(probe["stderr_records"], [])
            self.assertEqual(probe["stdout_records"], ["M245_W_READY", "M245_W_DONE"])
            identities = probe["process_identities"]
            self.assertEqual(set(identities), {"O", "S", "L", "W"})
            self.assertEqual(len({row["pid"] for row in identities.values()}), 4)
            self.assertEqual(identities["S"]["parent_pid"], identities["O"]["pid"])
            self.assertEqual(identities["L"]["parent_pid"], identities["S"]["pid"])
            self.assertEqual(identities["W"]["parent_pid"], identities["L"]["pid"])
            self.assertFalse(identities["S"]["job_membership"])
            self.assertTrue(identities["L"]["job_membership"])
            self.assertTrue(identities["W"]["job_membership"])
            self.assertEqual(probe["job_census"]["total_processes"], 2)
            self.assertEqual(probe["job_census"]["worker_children"], 0)
            for publication in probe["publications"]:
                path = root / publication["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(_sha256_bytes(path.read_bytes()), publication["sha256"])
                self.assertTrue(publication["reopened_bytes_equal"])
                self.assertTrue(publication["source_final_same_device_inode"])
                self.assertTrue(publication["temporary_unlinked"])
            inner_meter = probe["inner_meter"]
            outer_meter = probe["outer_meter"]
            meter = probe["terminal_resource_meter"]
            self.assertEqual(meter, _terminal_resource_meter(inner_meter, outer_meter))
            self.assertEqual(tuple(meter), TERMINAL_RESOURCE_METER_KEYS)
            self.assertLessEqual(meter["rss_gate_bytes"], 2_147_483_648)
            self.assertLessEqual(meter["full_wall_seconds"], 5400)

    def test_invocation_receipt_schema_topology_firewall_and_caps_are_exact(self) -> None:
        for invocation_index in (1, 2):
            receipt = _valid_receipt(0, invocation_index)
            self.assertEqual(tuple(receipt), INVOCATION_RECEIPT_KEYS)
            self.assertEqual(tuple(receipt["resource_meter"]), RESOURCE_METER_KEYS)
            self.assertEqual(tuple(receipt["firewall"]), FIREWALL_KEYS)
            runner.validate_invocation_receipt(receipt, _meter_payload())
            self.assertEqual(
                receipt["status"],
                "PROVISIONAL_INNER_RECEIPT_NO_INVOCATION_PASS",
            )
            self.assertEqual(set(receipt["process_identities"]), {"S", "L", "W"})
            self.assertEqual(receipt["job_census"]["job_roles"], ["L", "W"])
            self.assertEqual(receipt["job_census"]["worker_children"], 0)
            expected_identities = {
                role: _identity(
                    role,
                    {"S": 200, "L": 201, "W": 202}[role],
                    {"S": 199, "L": 200, "W": 201}[role],
                    shard_id=0,
                    invocation_index=invocation_index,
                )
                for role in ("S", "L", "W")
            }
            self.assertEqual(receipt["process_identities"], expected_identities)
            raw_meter = _meter_payload()
            meter = receipt["resource_meter"]
            sampled = max(
                sum(
                    role["current_working_set_bytes"]
                    for role in sample["roles"].values()
                    if role["state"] == "ALIVE"
                )
                for sample in raw_meter["samples"]
            )
            lifetime_peak = sum(
                max(
                    sample["roles"][role]["peak_working_set_bytes"]
                    for sample in raw_meter["samples"]
                )
                for role in ("S", "L", "W")
            )
            expected_cpu_100ns = {
                role: raw_meter["samples"][-1]["roles"][role]["kernel_time_100ns"]
                + raw_meter["samples"][-1]["roles"][role]["user_time_100ns"]
                for role in ("S", "L", "W")
            }
            cpu_seconds = sum(expected_cpu_100ns.values()) / 10_000_000
            gaps = [
                (right["qpc_tick"] - left["qpc_tick"]) / raw_meter["qpc_frequency"]
                for left, right in zip(raw_meter["samples"], raw_meter["samples"][1:])
            ]
            self.assertEqual(meter["max_sampled_concurrent_working_set_bytes"], sampled)
            self.assertEqual(meter["lifetime_peak_upper_bytes"], lifetime_peak)
            self.assertEqual(meter["rss_gate_bytes"], max(sampled, lifetime_peak))
            self.assertEqual(meter["cpu_100ns_by_role"], expected_cpu_100ns)
            self.assertEqual(meter["cpu_seconds_sum"], cpu_seconds)
            self.assertEqual(meter["max_observed_sampling_gap_seconds"], max(gaps))
            self.assertEqual(
                meter["full_wall_seconds"],
                (
                    meter["terminal_child_exit_filetime"]
                    - meter["s_process_creation_filetime"]
                )
                / 10_000_000,
            )
            self.assertEqual(raw_meter["samples"][0]["roles"]["L"]["state"], "NOT_CREATED")
            self.assertEqual(raw_meter["samples"][0]["roles"]["W"]["state"], "NOT_CREATED")
            milestones = raw_meter["milestones"]
            self.assertLess(
                milestones["result_publication_verified_qpc_tick"],
                milestones["checkpoint_publication_verified_qpc_tick"],
            )
            self.assertLess(
                milestones["checkpoint_publication_verified_qpc_tick"],
                milestones["done_received_qpc_tick"],
            )
            self.assertLess(
                milestones["done_received_qpc_tick"],
                milestones["exit_released_qpc_tick"],
            )
            self.assertLess(
                milestones["launcher_exit_qpc_tick"],
                milestones["stream_closed_qpc_tick"],
            )
            self.assertEqual(
                receipt["meter_publication"]["sha256"],
                _sha256_bytes(_canonical_json_bytes(raw_meter)),
            )

    def test_receipt_refuses_resource_topology_publication_or_firewall_failure(self) -> None:
        mutations = []
        for path, value in (
            (("resource_meter", "full_wall_seconds"), 5400.0001),
            (("resource_meter", "scientific_stop_wall_seconds"), 5100.0001),
            (("resource_meter", "rss_gate_bytes"), 2147483649),
            (("resource_meter", "max_observed_sampling_gap_seconds"), 0.1000001),
            (("resource_meter", "cpu_seconds_sum"), 999.0),
            (("resource_meter", "max_sampled_concurrent_working_set_bytes"), 1),
            (("resource_meter", "lifetime_peak_upper_bytes"), 1),
            (("resource_meter", "endpoint_qpc_tick"), 10_000_000_001),
            (("job_census", "worker_children"), 1),
            (("path_state", "temporary_paths_absent_after_publication"), False),
            (("result_publication", "source_final_same_device_inode"), False),
            (("firewall", "network_service"), True),
        ):
            changed = _valid_receipt()
            changed[path[0]][path[1]] = value
            mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_invocation_receipt(changed, _meter_payload())
        raw_mutations = []
        changed_meter = _meter_payload()
        changed_meter["samples"][2]["sample_index"] = 99
        raw_mutations.append(changed_meter)
        changed_meter = _meter_payload()
        changed_meter["samples"][2]["roles"]["W"]["kernel_time_100ns"] = -1
        raw_mutations.append(changed_meter)
        changed_meter = _meter_payload()
        changed_meter["samples"][2]["qpc_tick"] += 2_000_000
        raw_mutations.append(changed_meter)
        changed_meter = _meter_payload()
        changed_meter["milestones"]["checkpoint_publication_verified_qpc_tick"] = 1_300_000
        raw_mutations.append(changed_meter)
        changed_meter = _meter_payload()
        changed_meter["samples"][0]["roles"]["L"] = _meter_role(
            "L", state="ALIVE", current=1, peak=1, kernel=1, user=1
        )
        raw_mutations.append(changed_meter)
        changed_meter = _meter_payload()
        changed_meter["samples"][-1]["roles"]["W"]["state"] = "ALIVE"
        changed_meter["samples"][-1]["roles"]["W"]["alive"] = True
        raw_mutations.append(changed_meter)
        for raw_meter in raw_mutations:
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_invocation_receipt(_valid_receipt(), raw_meter)

    def test_outer_terminal_witness_is_the_only_invocation_and_shard_pass(self) -> None:
        final, first, second, first_witness, second_witness = _valid_final_receipt(2)
        self.assertEqual(tuple(first_witness), TERMINAL_WITNESS_KEYS)
        self.assertEqual(tuple(second_witness), TERMINAL_WITNESS_KEYS)
        self.assertEqual(
            first_witness["status"],
            "PASS_M245_INVOCATION_BOUND",
        )
        self.assertEqual(second_witness["status"], "PASS_M245_SHARD_BOUND")
        self.assertEqual(set(first_witness["process_identities"]), {"O", "S", "L", "W"})
        self.assertEqual(
            tuple(first_witness["resource_meter"]),
            TERMINAL_RESOURCE_METER_KEYS,
        )
        self.assertEqual(
            first_witness["resource_meter"],
            _terminal_resource_meter(_meter_payload(), first_witness["outer_meter"]),
        )
        self.assertEqual(first_witness["inner_meter"], _meter_payload())
        self.assertEqual(
            first_witness["inner_artifacts"][2]["sha256"],
            _sha256_bytes(_canonical_json_bytes(first_witness["inner_meter"])),
        )
        launcher.validate_terminal_witness(
            first_witness,
            inner_meter=_meter_payload(),
            inner_receipt=first,
            prior_witness=None,
            final_shard_receipt=None,
        )
        launcher.validate_terminal_witness(
            second_witness,
            inner_meter=_meter_payload(),
            inner_receipt=second,
            prior_witness=first_witness,
            final_shard_receipt=final,
        )
        self.assertEqual(
            second_witness["final_shard_receipt"]["sha256"],
            _sha256_bytes(_canonical_json_bytes(final)),
        )
        self.assertEqual(
            [row["file_kind"] for row in second_witness["prior_invocation_files"]],
            ["result", "checkpoint", "meter", "provisional_receipt", "terminal_witness"],
        )
        mutations = []
        changed = copy.deepcopy(second_witness)
        changed["outer_meter"]["samples"][3]["roles"]["O"]["kernel_time_100ns"] = -1
        mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["outer_meter"]["samples"][-1]["roles"]["S"]["state"] = "ALIVE"
        changed["outer_meter"]["samples"][-1]["roles"]["S"]["alive"] = True
        mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["outer_meter"]["milestones"]["final_shard_publication_verified_qpc_tick"] = 1_900_000
        mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["resource_meter"]["cpu_seconds_sum"] = 0.0
        mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["resource_meter"]["full_wall_seconds"] = 5400.0001
        mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["resource_meter"]["rss_gate_bytes"] = 2_147_483_649
        mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["final_shard_receipt"]["sha256"] = "0" * 64
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(launcher.M245LaunchContractError):
                launcher.validate_terminal_witness(
                    changed,
                    inner_meter=_meter_payload(),
                    inner_receipt=second,
                    prior_witness=first_witness,
                    final_shard_receipt=final,
                )

    def test_qpc_union_merge_carry_dedup_and_domain_refusals_are_exact(self) -> None:
        inner = _meter_payload()
        outer = _outer_meter_payload(1)
        expected = _terminal_resource_meter(inner, outer)
        union_ticks = sorted(
            {row["qpc_tick"] for row in inner["samples"] + outer["samples"]}
        )
        self.assertEqual(union_ticks, [500_000, 1_000_000, 1_500_000, 2_000_000, 2_200_000, 2_500_000])
        # At every union tick duplicated S contributes the max, never the sum.
        self.assertEqual(expected["max_merged_concurrent_working_set_bytes"], 8_400)
        self.assertEqual(expected["lifetime_peak_upper_bytes"], 9_800)
        self.assertEqual(expected["rss_gate_bytes"], 9_800)
        self.assertLessEqual(expected["max_observed_sampling_gap_seconds"], 0.1)

        mutations: list[tuple[dict, dict]] = []
        changed_inner, changed_outer = copy.deepcopy(inner), copy.deepcopy(outer)
        changed_outer["qpc_frequency"] += 1
        mutations.append((changed_inner, changed_outer))
        changed_inner, changed_outer = copy.deepcopy(inner), copy.deepcopy(outer)
        changed_outer["qpc_clock_id"] = "OTHER_CLOCK"
        mutations.append((changed_inner, changed_outer))
        changed_inner, changed_outer = copy.deepcopy(inner), copy.deepcopy(outer)
        changed_outer["samples"][2]["utc_filetime"] += 1
        mutations.append((changed_inner, changed_outer))
        changed_inner, changed_outer = copy.deepcopy(inner), copy.deepcopy(outer)
        changed_outer["samples"][2]["roles"]["S"]["creation_filetime"] += 1
        mutations.append((changed_inner, changed_outer))
        changed_inner, changed_outer = copy.deepcopy(inner), copy.deepcopy(outer)
        changed_outer["samples"].pop(0)
        for index, sample in enumerate(changed_outer["samples"]):
            sample["sample_index"] = index
        mutations.append((changed_inner, changed_outer))
        changed_inner, changed_outer = copy.deepcopy(inner), copy.deepcopy(outer)
        changed_inner["samples"] = [changed_inner["samples"][0], changed_inner["samples"][-1]]
        changed_inner["samples"][1]["sample_index"] = 1
        mutations.append((changed_inner, changed_outer))
        for changed_inner, changed_outer in mutations:
            with self.assertRaises(AssertionError):
                _terminal_resource_meter(changed_inner, changed_outer)

        final, _first, second, first_witness, second_witness = _valid_final_receipt(2)
        witness_mutations = []
        changed = copy.deepcopy(second_witness)
        changed["inner_meter"]["qpc_clock_id"] = "OTHER_CLOCK"
        witness_mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["outer_meter"]["samples"][2]["roles"]["S"]["pid"] += 1
        witness_mutations.append(changed)
        changed = copy.deepcopy(second_witness)
        changed["resource_meter"]["max_merged_concurrent_working_set_bytes"] += 1
        witness_mutations.append(changed)
        for changed in witness_mutations:
            with self.assertRaises(launcher.M245LaunchContractError):
                launcher.validate_terminal_witness(
                    changed,
                    inner_meter=changed["inner_meter"],
                    inner_receipt=second,
                    prior_witness=first_witness,
                    final_shard_receipt=final,
                )

    def test_second_invocation_and_final_receipt_bind_both_complete_events(self) -> None:
        final, first, second, first_witness, second_witness = _valid_final_receipt(2)
        self.assertEqual(tuple(final), FINAL_SHARD_RECEIPT_KEYS)
        expected_prior = _sha256_bytes(_canonical_json_bytes(first))
        prior_receipt = second["prior_invocation_files"][-1]
        self.assertEqual(
            [row["file_kind"] for row in second["prior_invocation_files"]],
            ["result", "checkpoint", "meter", "invocation_receipt"],
        )
        for kind, row in zip(
            ("result", "checkpoint", "meter"),
            second["prior_invocation_files"][:3],
        ):
            self.assertEqual(row["sha256"], first[f"{kind}_publication"]["sha256"])
            self.assertEqual(row["bytes"], first[f"{kind}_publication"]["bytes"])
        self.assertEqual(prior_receipt["file_kind"], "invocation_receipt")
        self.assertEqual(prior_receipt["sha256"], expected_prior)
        self.assertEqual(
            prior_receipt["bytes"],
            len(_canonical_json_bytes(first)),
        )
        self.assertEqual(
            [row["event_id"] for row in final["event_results"]],
            ["E04", "E05"],
        )
        self.assertTrue(all(tuple(row) == EVENT_RESULT_KEYS for row in final["event_results"]))
        self.assertEqual(
            final["status"],
            "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS",
        )
        self.assertEqual(len(final["invocation_receipts"]), 3)
        self.assertEqual(
            final["invocation_receipts"][-1]["sha256"],
            _sha256_bytes(_canonical_json_bytes(first_witness)),
        )
        self.assertTrue(final["resource_union"]["invocation_two_terminal_witness_required"])
        self.assertNotIn("cpu_seconds_sum", final["resource_union"])
        first_resource = final["resource_union"]["invocation_one_terminal_witness"]
        second_resource = final["resource_union"]["invocation_two_inner_meter"]
        self.assertEqual(
            first_resource["terminal_witness"],
            first_witness,
        )
        self.assertEqual(first_resource["bytes"], len(_canonical_json_bytes(first_witness)))
        self.assertEqual((first_resource["device"], first_resource["inode"]), (1, 2))
        self.assertEqual(second_resource["raw_meter"], _meter_payload())
        self.assertEqual(
            second_resource["sha256"],
            _sha256_bytes(_canonical_json_bytes(second_resource["raw_meter"])),
        )
        self.assertEqual((second_resource["device"], second_resource["inode"]), (1, 2))
        launcher.validate_final_shard_receipt(final, first, second, first_witness)
        launcher.validate_terminal_witness(
            second_witness,
            inner_meter=_meter_payload(),
            inner_receipt=second,
            prior_witness=first_witness,
            final_shard_receipt=final,
        )
        bad = copy.deepcopy(final)
        bad["events_in_order"].reverse()
        with self.assertRaises(launcher.M245LaunchContractError):
            launcher.validate_final_shard_receipt(bad, first, second, first_witness)
        bad_second = copy.deepcopy(second)
        bad_second["prior_invocation_files"][-1]["sha256"] = "0" * 64
        with self.assertRaises(launcher.M245LaunchContractError):
            launcher.validate_final_shard_receipt(final, first, bad_second, first_witness)
        bad_event = copy.deepcopy(final)
        bad_event["event_results"][1]["quad_gateway_ledger_refs"][0]["sha256"] = "0" * 64
        with self.assertRaises(launcher.M245LaunchContractError):
            launcher.validate_final_shard_receipt(bad_event, first, second, first_witness)
        bad_resource = copy.deepcopy(final)
        del bad_resource["resource_union"]["invocation_two_inner_meter"]["raw_meter"]
        with self.assertRaises(launcher.M245LaunchContractError):
            launcher.validate_final_shard_receipt(bad_resource, first, second, first_witness)
        bad_identity = copy.deepcopy(final)
        bad_identity["resource_union"]["invocation_one_terminal_witness"]["inode"] += 1
        with self.assertRaises(launcher.M245LaunchContractError):
            launcher.validate_final_shard_receipt(bad_identity, first, second, first_witness)

    def test_event_union_schema_is_exact_complete_and_not_a_lossy_summary(self) -> None:
        dummy_event_id = "DUMMY_UNION_EVENT_NOT_IN_FROZEN_CENSUS"
        event = _event_result(dummy_event_id)
        runner.validate_event_result(event, expected_event_id=dummy_event_id)
        self.assertEqual(tuple(event), EVENT_RESULT_KEYS)
        self.assertEqual(tuple(event["primary_by_precision"]), ("80", "100"))
        self.assertEqual(tuple(event["replica_by_precision"]), ("80", "100"))
        for dps in ("80", "100"):
            primary = event["primary_by_precision"][dps]
            replica = event["replica_by_precision"][dps]
            self.assertEqual(tuple(primary), PRIMARY_EVENT_KEYS)
            self.assertEqual(tuple(replica), REPLICA_EVENT_KEYS)
            self.assertEqual(len(primary["R"]), 9)
            self.assertEqual(len(primary["G"]), 9)
            self.assertTrue(all(len(row) == 9 for row in primary["G"]))
            self.assertEqual(len(primary["leading_blocks"]), 9)
            self.assertEqual(len(primary["analytic_direct_checks"]["R"]), 9)
            self.assertEqual(len(primary["analytic_direct_checks"]["G_upper"]), 45)
            self.assertEqual(len(replica["fixed_b_nodes"]), 17)
            self.assertEqual(len(replica["b_rep_at_nodes"]), 17)
            self.assertNotEqual(primary["K"], "0")
            self.assertNotEqual(replica["K_rep"], "0")
        mutations = []
        changed = copy.deepcopy(event)
        del changed["primary_by_precision"]["100"]
        mutations.append(changed)
        changed = copy.deepcopy(event)
        del changed["primary_by_precision"]["80"]["G"]
        mutations.append(changed)
        changed = copy.deepcopy(event)
        changed["replica_by_precision"]["100"]["b_rep_at_nodes"].pop()
        mutations.append(changed)
        changed = copy.deepcopy(event)
        changed["lossy_summary"] = {"K": 1}
        mutations.append(changed)
        changed = copy.deepcopy(event)
        changed["curve_report"]["labels"]["Gompertz"] = "gompertz"
        mutations.append(changed)
        changed = copy.deepcopy(event)
        changed["only_future_bound"] = "unbounded extrapolation"
        mutations.append(changed)
        changed = copy.deepcopy(event)
        changed["forbidden_credit"] = False
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(runner.M245ShardContractError):
                runner.validate_event_result(changed, expected_event_id=dummy_event_id)

    def test_final_union_is_built_only_from_nine_immutable_input_files(self) -> None:
        final, first, second, first_witness, _ = _valid_final_receipt(1)
        self.assertEqual(
            tuple(inspect.signature(launcher.build_final_shard_receipt_from_files).parameters),
            ("shard_directory", "shard_id"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exact_paths: list[Path] = []
            for index, receipt in enumerate((first, second), 1):
                event_id = ASSIGNMENTS[1][index - 1]
                namespace = _expected_namespace(1, index)
                payloads = {
                    "result": _event_result(
                        event_id,
                        shard_id=1,
                        invocation_index=index,
                    ),
                    "checkpoint": _checkpoint(event_id),
                    "meter": _meter_payload(),
                    "invocation_receipt": receipt,
                }
                for kind, payload in payloads.items():
                    path = root / namespace[kind]
                    path.write_bytes(_canonical_json_bytes(payload))
                    exact_paths.append(path)
            first_witness_path = root / _expected_namespace(1, 1)["terminal_witness"]
            first_witness_path.write_bytes(_canonical_json_bytes(first_witness))
            exact_paths.append(first_witness_path)
            observed = launcher.build_final_shard_receipt_from_files(
                root,
                shard_id=1,
            )
            self.assertEqual(observed, final)
            self.assertEqual(len(exact_paths), 9)
            for path in exact_paths:
                original = path.read_bytes()
                path.write_bytes(b"{}\n")
                with self.subTest(path=path.name):
                    with self.assertRaises(launcher.M245LaunchContractError):
                        launcher.build_final_shard_receipt_from_files(root, shard_id=1)
                path.write_bytes(original)


class TestM245ShardProcessFirewalls(unittest.TestCase):
    def test_outer_and_supervisor_are_stdlib_only_and_worker_is_the_only_scientific_importer(self) -> None:
        supervisor_forbidden = (
            "mpmath",
            "numpy",
            "scipy",
            "m245_primary_core",
            "m245_replica_core",
            "m243",
            "m178",
            "requests",
            "urllib",
            "http",
            "socket",
        )
        for module in (launcher, runner):
            observed_imports = _imports(Path(module.__file__).resolve())
            self.assertFalse(
                any(name.lower().startswith(supervisor_forbidden) for name in observed_imports),
                observed_imports,
            )

        worker = importlib.import_module("m245_scientific_worker")
        worker_path = Path(worker.__file__).resolve()
        worker_imports = _imports(worker_path)
        self.assertIn("m245_primary_core", worker_imports)
        self.assertIn("m245_replica_core", worker_imports)
        worker_forbidden = ("m243", "m178", "m151", "m196", "m125", "requests", "urllib", "http", "socket", "subprocess")
        self.assertFalse(
            any(name.lower().startswith(worker_forbidden) for name in worker_imports),
            worker_imports,
        )

        primary_module = importlib.import_module("m245_primary_core")
        replica_module = importlib.import_module("m245_replica_core")
        source_paths = {
            "primary": Path(primary_module.__file__).resolve(),
            "replica": Path(replica_module.__file__).resolve(),
            "worker": worker_path,
        }
        self.assertEqual(_mp_quad_call_owners(source_paths["primary"]), [])
        self.assertEqual(_mp_quad_call_owners(source_paths["replica"]), [])
        self.assertEqual(_mp_quad_call_owners(source_paths["worker"]), ["_instrumented_quad"])
        for path in source_paths.values():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == "mpmath":
                    self.assertNotIn("quad", {alias.name for alias in node.names})

        worker_tree = ast.parse(worker_path.read_text(encoding="utf-8"), filename=str(worker_path))
        injected_calls = [
            node
            for node in ast.walk(worker_tree)
            if isinstance(node, ast.Call)
            and (
                (isinstance(node.func, ast.Attribute) and node.func.attr in {"run_primary_event", "run_replica_event"})
                or (isinstance(node.func, ast.Name) and node.func.id in {"run_primary_event", "run_replica_event"})
            )
        ]
        self.assertGreaterEqual(len(injected_calls), 2)
        for call in injected_calls:
            self.assertIn("quad_gateway", {keyword.arg for keyword in call.keywords})


if __name__ == "__main__":
    unittest.main()
