"""Frozen immutable-file-only contract for final M245 aggregation.

This suite uses complete dummy receipt objects and identifiers outside the
scientific computation.  It never reads fixture-array values or evaluates
E00:E07 science.  The missing aggregation module is its independent RED.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import aggregate_m245_spectrum as aggregation


HERE = Path(__file__).resolve().parent
AUTHORITY_DIRECTORY_REPO_RELATIVE = (
    "corpus/whestbench/experiments/"
    "m245_canonical_unordered_replica_galerkin_spectrum"
)
SHARD_DIRECTORY_REPO_RELATIVE = "corpus/whestbench/experiments/m245_fable_spectrum_shards"
AUTHORITY_CWD = str(HERE)
STDLIB_PYTHON = r"C:\Python314\python.exe"
V2_SHA256 = "0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b"
V2_CHECKSUM_SHA256 = "2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e"
SCIENTIFIC_ERRATUM2_NAME = "M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md"
SCIENTIFIC_ERRATUM2_SHA256 = "8641de9ec301ba402b87e50dd8c5e3322a6532313f1d603c54356a4137e21587"
SCIENTIFIC_OVERLAY2_SHA256 = "401629468b5ec1f2eb5447b650b10f27fb47ba7ce3af74c740a230feeefcceaf"
ASSIGNMENTS = {
    0: ("E00", "E01"),
    1: ("E02", "E03"),
    2: ("E04", "E05"),
    3: ("E06", "E07"),
}

FINAL_RECEIPT_NAMES = tuple(
    f"M245_S{shard_id}_FINAL_RECEIPT_20260810.json" for shard_id in ASSIGNMENTS
)
AGGREGATION_CONTRACT = {
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

AUTHORITY_SHA256 = {
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
    "m245_primary_core.py": "1" * 64,
    "m245_replica_core.py": "2" * 64,
    "m245_scientific_worker.py": "3" * 64,
    "run_m245_scientific_shard.py": "4" * 64,
    "launch_m245_scientific_invocation.py": "5" * 64,
    "aggregate_m245_spectrum.py": "6" * 64,
    "test_m245_primary_core.py": "7" * 64,
    "test_m245_replica_core.py": "8" * 64,
    "test_m245_scientific_transport.py": "9" * 64,
    "test_m245_aggregation.py": "a" * 64,
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md": "b" * 64,
    "M245_SCIENTIFIC_STATIC_AUDIT_CONTRACT_20260810.md": "c" * 64,
    "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json": "d" * 64,
    "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json": "e" * 64,
    "M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json": "f" * 64,
}

AGGREGATION_NAMESPACE = {
    "directory_repo_relative": AUTHORITY_DIRECTORY_REPO_RELATIVE,
    "authorization": "M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json",
    "intent_temp": ".M245_AGGREGATION_INTENT_20260810.json.tmp",
    "intent": "M245_AGGREGATION_INTENT_20260810.json",
    "result_temp": ".M245_AGGREGATED_SPECTRUM_20260810.json.tmp",
    "result": "M245_AGGREGATED_SPECTRUM_20260810.json",
    "receipt_temp": ".M245_AGGREGATION_RECEIPT_20260810.json.tmp",
    "receipt": "M245_AGGREGATION_RECEIPT_20260810.json",
}

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
    "artifact", "schema", "event_id", "precision_dps", "fixture_array_sha256",
    "degrees", "R", "G", "mu_rb", "K", "d", "beta", "leading_blocks",
    "analytic_direct_checks", "quadrature_audit", "firewall",
)
REPLICA_EVENT_KEYS = (
    "artifact", "schema", "event_id", "precision_dps", "fixture_array_sha256",
    "fixed_b_nodes", "b_rep_at_nodes", "mu_rep", "M_same", "M_cross",
    "K_rep", "quadrature_audit", "firewall",
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
AUTHORIZATION_KEYS = (
    "artifact",
    "schema",
    "shard_trigger_sha256",
    "final_shard_receipts",
    "terminal_witnesses",
    "observed_parent_head",
    "aggregate_argv",
    "aggregate_cwd",
    "aggregate_source_sha256",
    "zero_prior_paths",
    "status",
)
AGGREGATE_RESULT_KEYS = (
    "artifact",
    "schema",
    "authority_sha256",
    "event_ids",
    "events",
    "family_curve_labels",
    "shard_receipt_sha256",
    "global_shard_cpu_seconds",
    "firewall",
    "status",
)
AGGREGATION_RECEIPT_KEYS = (
    "artifact",
    "schema",
    "authorization_binding",
    "input_shard_receipts",
    "input_terminal_witnesses",
    "intent_publication",
    "output_publication",
    "postpublication_verification",
    "process_tree",
    "network",
    "no_scientific_imports",
    "wall_seconds",
    "status",
)
PUBLIC_CALLABLES = (
    "aggregation_contract",
    "aggregation_namespace",
    "validate_aggregation_authorization",
    "load_verified_shard_receipts",
    "aggregate_from_authorization",
    "render_summary",
    "validate_aggregate_result",
    "validate_aggregation_receipt",
    "publish_immutable_json",
    "main",
)


def _canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _firewall() -> dict:
    return {name: False for name in FIREWALL_KEYS}


def _engine_result(event_id: str, engine: str, dps: int) -> dict:
    quadrature_audit = {
        "all_calls_pass": True,
        "error_semantics": "heuristic_diagnostic_estimate_not_interval_certificate",
        "interval_certified": False,
        "observed_call_count": 2,
    }
    fixture = {"C": "c" * 64, "mu": "d" * 64}
    if engine == "replica":
        return {
            "artifact": "M245_REPLICA_EVENT_PRECISION",
            "schema": "m245-replica-event-v1",
            "event_id": event_id,
            "precision_dps": dps,
            "fixture_array_sha256": fixture,
            "fixed_b_nodes": [
                "0", "0.00390625", "-0.00390625", "0.25", "-0.25", "1", "-1",
                "2.5", "-2.5", "5", "-5", "8", "-8", "10", "-10", "16", "-16",
            ],
            "b_rep_at_nodes": [f"{0.25 + index / 100:.17g}" for index in range(17)],
            "mu_rep": "0.375",
            "M_same": "3.25",
            "M_cross": "0.75",
            "K_rep": "1.859375",
            "quadrature_audit": quadrature_audit,
            "firewall": {"network": False, "primary_import": False},
        }
    degrees = list(range(9))
    R = [f"{0.125 + 0.01 * q:.17g}" for q in degrees]
    G = [
        [
            f"{(1.0 + 0.05 * q) if m == q else 0.001 / (1 + abs(m - q)):.17g}"
            for q in degrees
        ]
        for m in degrees
    ]
    leading_blocks = []
    for Q in degrees:
        P, V, V_beta = 0.2 + 0.05 * Q, 1.8 - 0.05 * Q, 1.825 - 0.05 * Q
        leading_blocks.append(
            {
                "Q": Q,
                "c": [f"{0.1 / (q + 1):.17g}" for q in range(Q + 1)],
                "P": f"{P:.17g}", "V": f"{V:.17g}",
                "lambda_min": f"{0.5 + 0.01 * Q:.17g}",
                "lambda_max": f"{1.5 + 0.01 * Q:.17g}",
                "lambda_ratio": "0.33333333333333331", "condition_2": "3",
                "cholesky_pass": True, "solve_relative_inf_residual": "1e-30",
                "solve_pass": True, "energy_gate": {"pass": True, "tau_K": "4e-10"},
                "V_beta": f"{V_beta:.17g}",
                "ordinary_beta_identity": {
                    "lhs": "0.025", "rhs": "0.025", "gap": "0.025", "pass": True,
                },
                "direct_residual": (
                    {"observed": f"{V:.17g}", "reference": f"{V:.17g}", "pass": True}
                    if Q in (0, 4, 8) else None
                ),
                "direct_beta_residual": (
                    {"observed": f"{V_beta:.17g}", "reference": f"{V_beta:.17g}", "pass": True}
                    if Q in (0, 4, 8) else None
                ),
            }
        )
    return {
        "artifact": "M245_PRIMARY_EVENT_PRECISION",
        "schema": "m245-primary-event-v1",
        "event_id": event_id,
        "precision_dps": dps,
        "fixture_array_sha256": fixture,
        "degrees": degrees,
        "R": R,
        "G": G,
        "mu_rb": "0.375",
        "K": "2",
        "d": [f"{0.2 / (q + 1):.17g}" for q in degrees],
        "beta": [f"{0.1 / (q + 1):.17g}" for q in degrees],
        "leading_blocks": leading_blocks,
        "analytic_direct_checks": {
            "R": [{"q": q, "analytic": R[q], "direct": R[q], "pass": True} for q in degrees],
            "G_upper": [
                {"m": m, "q": q, "analytic": G[m][q], "direct": G[m][q], "pass": True}
                for q in degrees for m in range(q + 1)
            ],
            "all_pass": True,
        },
        "quadrature_audit": quadrature_audit,
        "firewall": {"network": False},
    }


def _event(
    event_id: str,
    *,
    labels: dict[str, str] | None = None,
) -> dict:
    if labels is None:
        labels = {
            family: "ENDPOINT_CONTROL/NA" if event_id == "E00" else "FALSIFIED"
            for family in ("geometric", "logistic", "Gompertz")
        }
    return {
        "event_id": event_id,
        "fixture_array_sha256": {"C": "c" * 64, "mu": "d" * 64},
        "primary_by_precision": {
            str(dps): _engine_result(event_id, "primary", dps) for dps in (80, 100)
        },
        "replica_by_precision": {
            str(dps): _engine_result(event_id, "replica", dps) for dps in (80, 100)
        },
        "cross_precision_gates": {"pass": True},
        "primary_replica_gates": {"pass": True},
        "analytic_solve_energy_beta_gates": {"pass": True},
        "curve_report": {"labels": copy.deepcopy(labels)},
        "quad_gateway_ledger_refs": [
            {
                "count": 2,
                "engine": engine,
                "precision_dps": dps,
                "sha256": digit * 64,
            }
            for engine, dps, digit in (
                ("primary", 80, "1"),
                ("primary", 100, "2"),
                ("replica", 80, "3"),
                ("replica", 100, "4"),
            )
        ],
        "only_future_bound": "0<=additional_explainable_energy_beyond_Q8<=K-P8",
        "gate_verdict": "PASS",
        "firewall": _firewall(),
        "forbidden_credit": True,
    }


def _witness_name(shard_id: int, invocation_index: int) -> str:
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    return f"M245_S{shard_id}_I{invocation_index}_{event_id}_TERMINAL_WITNESS_20260810.json"


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
        "image_sha256": "7" * 64 if created else None,
        "kernel_time_100ns": kernel,
        "peak_working_set_bytes": peak,
        "pid": pid if created else None,
        "state": state,
        "user_time_100ns": user,
    }


def _inner_meter() -> dict:
    frequency = 10_000_000
    clock = "DUMMY_SHARED_QPC_CLOCK_DOMAIN"
    offset = 10_000_000_000
    ticks = (500_000, 1_000_000, 1_500_000)
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
            "S": _meter_role("S", state="ALIVE", current=1200, peak=1800, kernel=6100, user=4100),
            "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000),
            "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000),
        },
    )
    return {
        "artifact": "M245_SHARD_RAW_METER",
        "job_process_events": [
            {"creation_filetime": 10_000_000_201, "event": "NEW_PROCESS", "pid": 201, "qpc_tick": 600_000, "role": "L"},
            {"creation_filetime": 10_000_000_202, "event": "NEW_PROCESS", "pid": 202, "qpc_tick": 700_000, "role": "W"},
            {"creation_filetime": 10_000_000_202, "event": "EXIT_PROCESS", "pid": 202, "qpc_tick": 1_400_000, "role": "W"},
            {"creation_filetime": 10_000_000_201, "event": "EXIT_PROCESS", "pid": 201, "qpc_tick": 1_450_000, "role": "L"},
        ],
        "milestones": {
            "result_publication_verified_qpc_tick": 1_100_000,
            "checkpoint_publication_verified_qpc_tick": 1_200_000,
            "done_received_qpc_tick": 1_250_000,
            "exit_released_qpc_tick": 1_300_000,
            "worker_exit_qpc_tick": 1_400_000,
            "launcher_exit_qpc_tick": 1_450_000,
            "stream_closed_qpc_tick": 1_500_000,
        },
        "qpc_clock_id": clock,
        "qpc_frequency": frequency,
        "s_process_creation_filetime": 10_000_000_200,
        "samples": [
            {
                "qpc_clock_id": clock,
                "qpc_frequency": frequency,
                "qpc_tick": tick,
                "roles": roles,
                "sample_index": index,
                "utc_filetime": offset + tick,
            }
            for index, (tick, roles) in enumerate(zip(ticks, rows))
        ],
        "schema": "m245-shard-raw-meter-v1",
        "scientific_stop_filetime": offset + 1_250_000,
        "terminal_child_exit_filetime": offset + 1_500_000,
    }


def _outer_meter(invocation_index: int) -> dict:
    frequency = 10_000_000
    clock = "DUMMY_SHARED_QPC_CLOCK_DOMAIN"
    offset = 10_000_000_000
    ticks = (500_000, 1_000_000, 1_500_000, 2_000_000)
    rows = (
        {
            "O": _meter_role("O", state="ALIVE", current=700, peak=700, kernel=100, user=100),
            "S": _meter_role("S", state="ALIVE", current=1000, peak=1000, kernel=100, user=100),
        },
        {
            "O": _meter_role("O", state="ALIVE", current=900, peak=900, kernel=1000, user=700),
            "S": _meter_role("S", state="ALIVE", current=1400, peak=1600, kernel=4100, user=2100),
        },
        {
            "O": _meter_role("O", state="ALIVE", current=1100, peak=1100, kernel=2000, user=1400),
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
            "s_spawn_qpc_tick": 500_000,
            "s_exit_qpc_tick": 1_500_000,
            "final_shard_publication_verified_qpc_tick": 1_800_000 if invocation_index == 2 else None,
            "stream_closed_qpc_tick": 2_000_000,
        },
        "o_process_creation_filetime": 10_000_000_199,
        "qpc_clock_id": clock,
        "qpc_frequency": frequency,
        "samples": [
            {
                "qpc_clock_id": clock,
                "qpc_frequency": frequency,
                "qpc_tick": tick,
                "roles": roles,
                "sample_index": index,
                "utc_filetime": offset + tick,
            }
            for index, (tick, roles) in enumerate(zip(ticks, rows))
        ],
        "schema": "m245-outer-raw-meter-v1",
        "terminal_endpoint_filetime": offset + ticks[-1],
    }


def _charged_meters(invocation_index: int, cpu_seconds: float) -> tuple[dict, dict]:
    inner = _inner_meter()
    outer = _outer_meter(invocation_index)
    cpu_100ns = int(cpu_seconds * 10_000_000)
    totals = {"O": cpu_100ns // 4, "S": cpu_100ns // 4, "L": cpu_100ns // 4}
    totals["W"] = cpu_100ns - sum(totals.values())
    for role, stream in (("O", outer), ("S", outer), ("L", inner), ("W", inner)):
        prior_user = stream["samples"][-2]["roles"][role]["user_time_100ns"]
        stream["samples"][-1]["roles"][role]["kernel_time_100ns"] = totals[role] - prior_user
        stream["samples"][-1]["roles"][role]["user_time_100ns"] = prior_user
    return inner, outer


def _terminal_resource(inner: dict, outer: dict) -> dict:
    by_role = {
        "O": sum(outer["samples"][-1]["roles"]["O"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
        "S": sum(outer["samples"][-1]["roles"]["S"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
        "L": sum(inner["samples"][-1]["roles"]["L"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
        "W": sum(inner["samples"][-1]["roles"]["W"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
    }
    return {
        "charged_process_roles": ["O", "S", "L", "W"],
        "cpu_100ns_by_role": by_role,
        "cpu_seconds_sum": sum(by_role.values()) / 10_000_000,
        "full_wall_seconds": (
            outer["terminal_endpoint_filetime"] - outer["o_process_creation_filetime"]
        ) / 10_000_000,
        "inner_sample_count": 3,
        "lifetime_peak_upper_bytes": 9_800,
        "max_merged_concurrent_working_set_bytes": 8_400,
        "max_observed_sampling_gap_seconds": 0.05,
        "o_process_creation_filetime": 10_000_000_199,
        "outer_sample_count": 4,
        "rss_gate_bytes": 9_800,
        "scientific_stop_wall_seconds": (
            inner["scientific_stop_filetime"] - outer["o_process_creation_filetime"]
        ) / 10_000_000,
        "terminal_endpoint_filetime": outer["terminal_endpoint_filetime"],
    }


def _inner_resource(inner: dict) -> dict:
    by_role = {
        role: sum(inner["samples"][-1]["roles"][role][key] for key in ("kernel_time_100ns", "user_time_100ns"))
        for role in ("S", "L", "W")
    }
    return {
        "charged_process_roles": ["S", "L", "W"],
        "cpu_100ns_by_role": by_role,
        "cpu_seconds_sum": sum(by_role.values()) / 10_000_000,
        "endpoint_qpc_tick": 1_500_000,
        "full_wall_seconds": (
            inner["terminal_child_exit_filetime"] - inner["s_process_creation_filetime"]
        ) / 10_000_000,
        "lifetime_peak_upper_bytes": 8_400,
        "max_observed_sampling_gap_seconds": 0.05,
        "max_sampled_concurrent_working_set_bytes": 7_500,
        "qpc_frequency": 10_000_000,
        "rss_gate_bytes": 8_400,
        "sample_count": 3,
        "s_process_creation_filetime": 10_000_000_200,
        "scientific_stop_qpc_tick": 1_250_000,
        "scientific_stop_wall_seconds": (
            inner["scientific_stop_filetime"] - inner["s_process_creation_filetime"]
        ) / 10_000_000,
        "t0_qpc_tick": 500_000,
        "terminal_child_exit_filetime": 10_001_500_000,
    }


def _terminal_witness(
    shard_id: int,
    invocation_index: int,
    cpu_seconds: float,
    *,
    prior_witness: dict | None = None,
    final_shard_receipt: dict | None = None,
) -> dict:
    event_id = ASSIGNMENTS[shard_id][invocation_index - 1]
    inner_meter, outer_meter = _charged_meters(invocation_index, cpu_seconds)
    inner_artifacts = [
        {
            "bytes": 100 + index,
            "device": 1,
            "event_id": event_id,
            "file_kind": kind,
            "inode": 10 + index,
            "invocation_index": invocation_index,
            "path": (
                f"M245_S{shard_id}_I{invocation_index}_{event_id}_"
                f"{ {'result': 'RESULT', 'checkpoint': 'CHECKPOINT', 'meter': 'METER', 'provisional_receipt': 'RECEIPT'}[kind] }_20260810.json"
            ),
            "sha256": format(shard_id * 8 + invocation_index * 4 + index + 1, "x")[-1] * 64,
        }
        for index, kind in enumerate(("result", "checkpoint", "meter", "provisional_receipt"))
    ]
    if invocation_index == 1:
        prior_files = None
        final_binding = None
        status = "PASS_M245_INVOCATION_BOUND"
    else:
        if prior_witness is None or final_shard_receipt is None:
            raise AssertionError("invocation two requires the first witness and final shard")
        prior_raw = _canonical_json_bytes(prior_witness)
        prior_files = copy.deepcopy(prior_witness["inner_artifacts"])
        prior_files.append(
            {
                "bytes": len(prior_raw),
                "device": 1,
                "event_id": prior_witness["event_id"],
                "file_kind": "terminal_witness",
                "inode": 19,
                "invocation_index": 1,
                "path": _witness_name(shard_id, 1),
                "sha256": _sha256_bytes(prior_raw),
                "status": prior_witness["status"],
            }
        )
        final_raw = _canonical_json_bytes(final_shard_receipt)
        final_binding = {
            "bytes": len(final_raw),
            "device": 1,
            "inode": 29,
            "path": FINAL_RECEIPT_NAMES[shard_id],
            "sha256": _sha256_bytes(final_raw),
            "status": final_shard_receipt["status"],
        }
        status = "PASS_M245_SHARD_BOUND"
    return {
        "artifact": "M245_OUTER_TERMINAL_INVOCATION_WITNESS",
        "schema": "m245-outer-terminal-invocation-witness-v1",
        "shard_id": shard_id,
        "invocation_index": invocation_index,
        "event_id": event_id,
        "authority_sha256": copy.deepcopy(AUTHORITY_SHA256),
        "inner_artifacts": inner_artifacts,
        "inner_meter": inner_meter,
        "prior_invocation_files": prior_files,
        "outer_meter": outer_meter,
        "process_identities": {
            role: {
                "creation_filetime": 10_000_000_000 + 199 + index,
                "image_sha256": "7" * 64,
                "pid": 199 + index,
                "retained_handle_through_exit": True,
            }
            for index, role in enumerate(("O", "S", "L", "W"))
        },
        "job_census": {
            "active_process_limit": 2,
            "distinct_job_pids": [201, 202],
            "job_roles": ["L", "W"],
            "total_processes": 2,
            "worker_children": 0,
        },
        "s_exit": {
            "exit_code": 0,
            "handle_retained_through_exit": True,
            "identity": {"creation_filetime": 10_000_000_200, "pid": 200},
        },
        "resource_meter": _terminal_resource(inner_meter, outer_meter),
        "final_shard_receipt": final_binding,
        "firewall": _firewall(),
        "status": status,
    }


def _shard_bundle(
    shard_id: int,
    *,
    cpu_seconds: float = 2.0,
    event_labels: dict[str, dict[str, str]] | None = None,
) -> tuple[dict, dict, dict]:
    event_labels = {} if event_labels is None else event_labels
    per_invocation_cpu = cpu_seconds / 2.0
    first_witness = _terminal_witness(shard_id, 1, per_invocation_cpu)
    first_witness_raw = _canonical_json_bytes(first_witness)
    second_inner_meter, _second_outer_meter = _charged_meters(2, per_invocation_cpu)
    final = {
        "artifact": "M245_FINAL_SHARD_RECEIPT",
        "schema": "m245-final-shard-receipt-v2",
        "shard_id": shard_id,
        "events_in_order": list(ASSIGNMENTS[shard_id]),
        "event_results": [
            _event(event_id, labels=event_labels.get(event_id))
            for event_id in ASSIGNMENTS[shard_id]
        ],
        "invocation_receipts": [
            {
                "event_id": event_id,
                "invocation_index": index,
                "path": f"M245_S{shard_id}_I{index}_{event_id}_RECEIPT_20260810.json",
                "sha256": format(shard_id * 2 + index, "x") * 64,
                "status": "PROVISIONAL_INNER_RECEIPT_NO_INVOCATION_PASS",
            }
            for index, event_id in enumerate(ASSIGNMENTS[shard_id], 1)
        ]
        + [
            {
                "event_id": first_witness["event_id"],
                "invocation_index": 1,
                "path": _witness_name(shard_id, 1),
                "sha256": _sha256_bytes(first_witness_raw),
                "status": first_witness["status"],
            }
        ],
        "authority_sha256": copy.deepcopy(AUTHORITY_SHA256),
        "resource_union": {
            "invocation_one_terminal_witness": {
                "bytes": len(first_witness_raw),
                "device": 1,
                "inode": 19,
                "path": _witness_name(shard_id, 1),
                "sha256": _sha256_bytes(first_witness_raw),
                "status": first_witness["status"],
                "terminal_witness": copy.deepcopy(first_witness),
            },
            "invocation_two_inner_meter": {
                "bytes": len(_canonical_json_bytes(second_inner_meter)),
                "device": 1,
                "inode": 18,
                "path": f"M245_S{shard_id}_I2_{ASSIGNMENTS[shard_id][1]}_METER_20260810.json",
                "raw_meter": second_inner_meter,
                "resource_meter": _inner_resource(second_inner_meter),
                "sha256": _sha256_bytes(_canonical_json_bytes(second_inner_meter)),
            },
            "invocation_two_terminal_witness_required": True,
        },
        "no_cross_shard_cache": True,
        "firewall": _firewall(),
        "status": "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS",
    }
    second_witness = _terminal_witness(
        shard_id,
        2,
        per_invocation_cpu,
        prior_witness=first_witness,
        final_shard_receipt=final,
    )
    return final, first_witness, second_witness


def _shard_receipt(
    shard_id: int,
    *,
    cpu_seconds: float = 2.0,
    event_labels: dict[str, dict[str, str]] | None = None,
) -> dict:
    return _shard_bundle(
        shard_id,
        cpu_seconds=cpu_seconds,
        event_labels=event_labels,
    )[0]


def _identity(path: Path) -> dict:
    stat = path.stat()
    return {
        "bytes": stat.st_size,
        "device": stat.st_dev,
        "inode": stat.st_ino,
    }


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def _write_authorization(
    root: Path,
    receipts: list[dict],
    *,
    forbidden_output_in_authorization_commit: bool = False,
    witness_mutator: object | None = None,
) -> tuple[Path, dict]:
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "M245 Dummy Test")
    _git(root, "config", "user.email", "m245-dummy@example.invalid")
    bindings = []
    witness_bindings = []
    for shard_id, receipt in enumerate(receipts):
        path = root / FINAL_RECEIPT_NAMES[shard_id]
        raw = _canonical_json_bytes(receipt)
        path.write_bytes(raw)
        bindings.append(
            {
                "bytes": len(raw),
                "device": path.stat().st_dev,
                "inode": path.stat().st_ino,
                "path": str(path.resolve()),
                "sha256": _sha256_bytes(raw),
                "shard_id": shard_id,
                "status": receipt["status"],
            }
        )
        per_invocation_cpu = receipt["resource_union"][
            "invocation_one_terminal_witness"
        ]["terminal_witness"]["resource_meter"]["cpu_seconds_sum"]
        first_witness = _terminal_witness(shard_id, 1, per_invocation_cpu)
        second_witness = _terminal_witness(
            shard_id,
            2,
            per_invocation_cpu,
            prior_witness=first_witness,
            final_shard_receipt=receipt,
        )
        for invocation_index, witness in enumerate((first_witness, second_witness), 1):
            if witness_mutator is not None:
                witness = witness_mutator(
                    copy.deepcopy(witness),
                    shard_id,
                    invocation_index,
                )
            witness_path = root / _witness_name(shard_id, invocation_index)
            witness_raw = _canonical_json_bytes(witness)
            witness_path.write_bytes(witness_raw)
            witness_bindings.append(
                {
                    "bytes": len(witness_raw),
                    "device": witness_path.stat().st_dev,
                    "inode": witness_path.stat().st_ino,
                    "invocation_index": invocation_index,
                    "path": str(witness_path.resolve()),
                    "sha256": _sha256_bytes(witness_raw),
                    "shard_id": shard_id,
                    "status": witness["status"],
                }
            )
    parent_marker = root / "DUMMY_PARENT_INPUT_CENSUS.txt"
    parent_marker.write_text("four provisional finals and eight witnesses\n", encoding="utf-8")
    _git(root, "add", "--", ".")
    _git(root, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "dummy immutable aggregation inputs")
    observed_parent_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    authorization = {
        "artifact": "M245_AGGREGATION_INPUT_AUTHORIZATION",
        "schema": "m245-aggregation-input-authorization-v1",
        "shard_trigger_sha256": "f" * 64,
        "final_shard_receipts": bindings,
        "terminal_witnesses": witness_bindings,
        "observed_parent_head": observed_parent_head,
        "aggregate_argv": [
            STDLIB_PYTHON,
            "-I",
            "-B",
            "-S",
            "-u",
            str((HERE / "aggregate_m245_spectrum.py").resolve()),
            "--authorization",
            str((root / AGGREGATION_NAMESPACE["authorization"]).resolve()),
        ],
        "aggregate_cwd": AUTHORITY_CWD,
        "aggregate_source_sha256": AUTHORITY_SHA256["aggregate_m245_spectrum.py"],
        "zero_prior_paths": {
            AGGREGATION_NAMESPACE["intent"]: "ABSENT",
            AGGREGATION_NAMESPACE["result"]: "ABSENT",
            AGGREGATION_NAMESPACE["receipt"]: "ABSENT",
        },
        "status": "PASS_COMMITTED_INPUT_AUTHORIZATION",
    }
    path = root / AGGREGATION_NAMESPACE["authorization"]
    raw = _canonical_json_bytes(authorization)
    path.write_bytes(raw)
    _git(root, "add", "--", AGGREGATION_NAMESPACE["authorization"])
    if forbidden_output_in_authorization_commit:
        forbidden = root / AGGREGATION_NAMESPACE["result"]
        forbidden.write_bytes(b"forbidden pre-aggregation output\n")
        _git(root, "add", "--", AGGREGATION_NAMESPACE["result"])
    _git(root, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "dummy aggregation input authorization")
    authorization_commit = _git(root, "rev-parse", "HEAD").stdout.strip()
    binding = {
        "bytes": len(raw),
        "device": path.stat().st_dev,
        "inode": path.stat().st_ino,
        "path": str(path.resolve()),
        "repository_commit": authorization_commit,
        "sha256": _sha256_bytes(raw),
    }
    return path, binding


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    return imported


class TestM245AggregationAPIAndFirewall(unittest.TestCase):
    def test_public_surface_contract_namespace_and_file_only_signatures_are_exact(self) -> None:
        self.assertTrue(issubclass(aggregation.M245AggregationContractError, Exception))
        for name in PUBLIC_CALLABLES:
            self.assertTrue(callable(getattr(aggregation, name, None)), name)
        self.assertEqual(aggregation.aggregation_contract(), AGGREGATION_CONTRACT)
        self.assertEqual(aggregation.aggregation_namespace(), AGGREGATION_NAMESPACE)
        for name in ("load_verified_shard_receipts", "aggregate_from_authorization"):
            self.assertEqual(
                tuple(inspect.signature(getattr(aggregation, name)).parameters),
                ("authorization_path", "authorization_binding"),
            )
        self.assertFalse(callable(getattr(aggregation, "aggregate_receipts", None)))

    def test_aggregator_is_stdlib_only_and_cannot_import_or_recompute_science(self) -> None:
        path = Path(aggregation.__file__).resolve()
        imported = _imports(path)
        forbidden = (
            "mpmath",
            "numpy",
            "scipy",
            "m245_primary_core",
            "m245_replica_core",
            "m245_scientific_worker",
            "run_m245_scientific_shard",
            "launch_m245_scientific_invocation",
            "m243",
            "m178",
            "m151",
            "m196",
            "m125",
            "requests",
            "urllib",
            "http",
            "socket",
        )
        self.assertFalse(any(name.lower().startswith(forbidden) for name in imported), imported)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        forbidden_calls = {
            "cholesky",
            "eigvalsh",
            "exp",
            "fit",
            "log",
            "polyfit",
            "quad",
            "solve",
        }
        called = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(called.isdisjoint(forbidden_calls), called)


class TestM245ImmutableInputAuthorization(unittest.TestCase):
    def test_exact_four_regular_files_are_hash_identity_and_census_verified(self) -> None:
        receipts = [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authorization_path, binding = _write_authorization(root, receipts)
            authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
            self.assertEqual(set(authorization), set(AUTHORIZATION_KEYS))
            self.assertEqual(len(authorization), len(AUTHORIZATION_KEYS))
            self.assertEqual(len(authorization["final_shard_receipts"]), 4)
            self.assertEqual(len(authorization["terminal_witnesses"]), 8)
            self.assertEqual(
                [row["status"] for row in authorization["terminal_witnesses"]],
                [
                    status
                    for _ in ASSIGNMENTS
                    for status in ("PASS_M245_INVOCATION_BOUND", "PASS_M245_SHARD_BOUND")
                ],
            )
            commit = binding["repository_commit"]
            first_containing = _git(
                root,
                "log",
                "--diff-filter=A",
                "--format=%H",
                "--",
                AGGREGATION_NAMESPACE["authorization"],
            ).stdout.splitlines()
            self.assertEqual(first_containing, [commit])
            self.assertEqual(
                _git(root, "show", f"{commit}:{AGGREGATION_NAMESPACE['authorization']}").stdout.encode("utf-8"),
                authorization_path.read_bytes(),
            )
            parent = authorization["observed_parent_head"]
            self.assertNotEqual(parent, commit)
            self.assertNotEqual(
                _git(
                    root,
                    "cat-file",
                    "-e",
                    f"{parent}:{AGGREGATION_NAMESPACE['authorization']}",
                    check=False,
                ).returncode,
                0,
            )
            for forbidden in (
                AGGREGATION_NAMESPACE["intent"],
                AGGREGATION_NAMESPACE["result"],
                AGGREGATION_NAMESPACE["receipt"],
            ):
                self.assertNotEqual(
                    _git(root, "cat-file", "-e", f"{commit}:{forbidden}", check=False).returncode,
                    0,
                )
            aggregation.validate_aggregation_authorization(
                authorization_path, binding
            )
            loaded = aggregation.load_verified_shard_receipts(
                authorization_path, binding
            )
            self.assertEqual(len(loaded), 4)
            for observed, expected in zip(loaded, receipts):
                self.assertEqual(_canonical_json_bytes(observed), _canonical_json_bytes(expected))
                self.assertEqual(set(observed), set(FINAL_SHARD_RECEIPT_KEYS))
                self.assertEqual(len(observed), len(FINAL_SHARD_RECEIPT_KEYS))
                self.assertTrue(
                    all(set(event) == set(EVENT_RESULT_KEYS) and len(event) == len(EVENT_RESULT_KEYS) for event in observed["event_results"])
                )
                for event in observed["event_results"]:
                    for dps in ("80", "100"):
                        self.assertEqual(set(event["primary_by_precision"][dps]), set(PRIMARY_EVENT_KEYS))
                        self.assertEqual(set(event["replica_by_precision"][dps]), set(REPLICA_EVENT_KEYS))
                        self.assertEqual(len(event["primary_by_precision"][dps]["G"]), 9)
                        self.assertEqual(len(event["replica_by_precision"][dps]["b_rep_at_nodes"]), 17)

    def test_fake_later_or_output_containing_git_authorization_commit_is_refused(self) -> None:
        receipts = [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, binding = _write_authorization(root, receipts)
            fake = {**binding, "repository_commit": "b" * 40}
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.validate_aggregation_authorization(path, fake)
            later_marker = root / "DUMMY_LATER_COMMIT.txt"
            later_marker.write_text("later\n", encoding="utf-8")
            _git(root, "add", "--", later_marker.name)
            _git(root, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "dummy later commit")
            later = {**binding, "repository_commit": _git(root, "rev-parse", "HEAD").stdout.strip()}
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.validate_aggregation_authorization(path, later)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, binding = _write_authorization(
                root,
                receipts,
                forbidden_output_in_authorization_commit=True,
            )
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.validate_aggregation_authorization(path, binding)

    def test_hash_drift_missing_file_wrong_identity_or_authorization_binding_is_refused(self) -> None:
        receipts = [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authorization_path, binding = _write_authorization(root, receipts)
            target = root / FINAL_RECEIPT_NAMES[2]
            original = target.read_bytes()
            target.write_bytes(b"{}\n")
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.load_verified_shard_receipts(authorization_path, binding)
            target.write_bytes(original)
            missing = root / FINAL_RECEIPT_NAMES[3]
            held = root / "held-final-receipt"
            os.replace(missing, held)
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.load_verified_shard_receipts(authorization_path, binding)
            os.replace(held, missing)
            changed_binding = copy.deepcopy(binding)
            changed_binding["sha256"] = "0" * 64
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.load_verified_shard_receipts(
                    authorization_path, changed_binding
                )
            witness_path = root / _witness_name(0, 2)
            witness_raw = witness_path.read_bytes()
            witness_path.write_bytes(b"{}\n")
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.load_verified_shard_receipts(
                    authorization_path, binding
                )
            witness_path.write_bytes(witness_raw)
            changed_authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
            changed_authorization["final_shard_receipts"][1]["inode"] += 1
            authorization_path.write_bytes(_canonical_json_bytes(changed_authorization))
            changed_binding = {
                **binding,
                "bytes": authorization_path.stat().st_size,
                "sha256": _sha256_bytes(authorization_path.read_bytes()),
            }
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.load_verified_shard_receipts(
                    authorization_path, changed_binding
                )

    def test_schema_census_reorder_extra_lossy_or_failed_receipt_is_refused(self) -> None:
        base = [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]
        mutations: list[list[dict]] = []
        changed = copy.deepcopy(base)
        changed[2]["schema"] = "m245-final-shard-receipt-v1"
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[0]["events_in_order"].reverse()
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[1]["event_results"][0]["lossy_summary"] = {"K": 1}
        mutations.append(changed)
        changed = copy.deepcopy(base)
        del changed[1]["event_results"][0]["primary_by_precision"]["80"]["G"]
        mutations.append(changed)
        changed = copy.deepcopy(base)
        del changed[2]["resource_union"]["invocation_two_inner_meter"]["raw_meter"]
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[0]["resource_union"]["invocation_one_terminal_witness"]["inode"] += 1
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[3]["shard_id"] = 2
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[2]["status"] = "KILLED"
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[1]["authority_sha256"]["m245_primary_core.py"] = "0" * 64
        mutations.append(changed)
        for index, receipts in enumerate(mutations):
            with self.subTest(index=index):
                with tempfile.TemporaryDirectory() as directory:
                    authorization_path, binding = _write_authorization(
                        Path(directory), receipts
                    )
                    with self.assertRaises(aggregation.M245AggregationContractError):
                        aggregation.load_verified_shard_receipts(
                            authorization_path, binding
                        )

    def test_invocation_two_pass_witness_must_cross_bind_its_provisional_final(self) -> None:
        receipts = [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]

        def break_cross_binding(witness: dict, shard_id: int, invocation_index: int) -> dict:
            if (shard_id, invocation_index) == (2, 2):
                witness["final_shard_receipt"]["sha256"] = "0" * 64
            return witness

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authorization_path, binding = _write_authorization(
                root,
                receipts,
                witness_mutator=break_cross_binding,
            )
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.load_verified_shard_receipts(
                    authorization_path, binding
                )


class TestM245LosslessAggregationAndFamilyRule(unittest.TestCase):
    def _aggregate(self, receipts: list[dict]) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            authorization_path, binding = _write_authorization(Path(directory), receipts)
            return aggregation.aggregate_from_authorization(
                authorization_path, binding
            )

    def test_result_is_lossless_ordered_E00_E07_and_global_cpu_is_exact(self) -> None:
        receipts = [
            _shard_receipt(shard_id, cpu_seconds=10_800.0)
            for shard_id in ASSIGNMENTS
        ]
        result = self._aggregate(receipts)
        self.assertEqual(tuple(result), AGGREGATE_RESULT_KEYS)
        self.assertEqual(result["artifact"], "M245_AGGREGATED_SPECTRUM")
        self.assertEqual(result["schema"], "m245-aggregated-spectrum-v1")
        self.assertEqual(
            result["status"],
            "PASSED_PRESERVED_GENERATED_SPECTRUM_PREMISE_ONLY",
        )
        self.assertEqual(result["event_ids"], [f"E{index:02d}" for index in range(8)])
        expected = [
            copy.deepcopy(event)
            for receipt in receipts
            for event in receipt["event_results"]
        ]
        self.assertEqual(result["events"], expected)
        for observed, source in zip(result["events"], expected):
            self.assertEqual(_canonical_json_bytes(observed), _canonical_json_bytes(source))
        self.assertEqual(result["global_shard_cpu_seconds"], 43_200.0)
        aggregation.validate_aggregate_result(result)

    def test_exact_family_rule_is_all_E01_E07_not_majority_or_E00_vote(self) -> None:
        families = ("geometric", "logistic", "Gompertz")
        all_not_falsified = {
            f"E{index:02d}": {
                family: "NOT_FALSIFIED_ON_Q0_8" for family in families
            }
            for index in range(1, 8)
        }
        all_not_falsified["E00"] = {
            family: "ENDPOINT_CONTROL/NA" for family in families
        }
        receipts = [
            _shard_receipt(
                shard_id,
                event_labels={
                    event_id: all_not_falsified[event_id]
                    for event_id in ASSIGNMENTS[shard_id]
                },
            )
            for shard_id in ASSIGNMENTS
        ]
        result = self._aggregate(receipts)
        self.assertEqual(
            result["family_curve_labels"],
            {family: "NOT_FALSIFIED_ON_Q0_8" for family in families},
        )
        majority = copy.deepcopy(receipts)
        majority[3]["event_results"][1]["curve_report"]["labels"]["Gompertz"] = "FALSIFIED"
        result = self._aggregate(majority)
        self.assertEqual(result["family_curve_labels"]["Gompertz"], "FALSIFIED")
        self.assertEqual(
            result["family_curve_labels"]["geometric"],
            "NOT_FALSIFIED_ON_Q0_8",
        )

    def test_family_label_alias_casefold_missing_or_E00_vote_is_refused(self) -> None:
        base = [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]
        mutations = []
        changed = copy.deepcopy(base)
        changed[0]["event_results"][0]["curve_report"]["labels"]["Gompertz"] = "FALSIFIED"
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[1]["event_results"][0]["curve_report"]["labels"]["logistic"] = "falsified"
        mutations.append(changed)
        changed = copy.deepcopy(base)
        del changed[2]["event_results"][0]["curve_report"]["labels"]["geometric"]
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed[3]["event_results"][1]["curve_report"]["labels"]["Gompertz"] = "UNKNOWN"
        mutations.append(changed)
        for receipts in mutations:
            with self.assertRaises(aggregation.M245AggregationContractError):
                self._aggregate(receipts)

    def test_global_cpu_over_43200_is_binding_failure(self) -> None:
        receipts = [
            _shard_receipt(shard_id, cpu_seconds=10_800.0)
            for shard_id in ASSIGNMENTS
        ]
        receipts[3] = _shard_receipt(3, cpu_seconds=10_800.0001)
        with self.assertRaises(aggregation.M245AggregationContractError):
            self._aggregate(receipts)

    def test_render_summary_does_not_mutate_or_recompute_result(self) -> None:
        result = self._aggregate(
            [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS]
        )
        before = _canonical_json_bytes(result)
        rendered = aggregation.render_summary(result)
        self.assertIsInstance(rendered, str)
        self.assertIn("E00", rendered)
        self.assertIn("E07", rendered)
        self.assertEqual(_canonical_json_bytes(result), before)


class TestM245AggregationPublicationReceipt(unittest.TestCase):
    def test_dummy_output_publication_is_create_if_absent_hardlink(self) -> None:
        payload = {"artifact": "DUMMY_AGGREGATION_NOT_SCIENCE", "status": "PASS"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            temp = root / ".dummy.json.tmp"
            final = root / "dummy.json"
            receipt = aggregation.publish_immutable_json(temp, final, payload)
            self.assertFalse(temp.exists())
            self.assertEqual(final.read_bytes(), _canonical_json_bytes(payload))
            self.assertTrue(receipt["source_final_same_device_inode"])
            self.assertTrue(receipt["temporary_unlinked"])
            self.assertTrue(receipt["reopened_bytes_equal"])
            with self.assertRaises(
                (aggregation.M245AggregationContractError, FileExistsError)
            ):
                aggregation.publish_immutable_json(temp, final, payload)

    def test_terminal_receipt_binds_authorization_four_inputs_output_and_caps(self) -> None:
        authorization_directory = tempfile.TemporaryDirectory()
        self.addCleanup(authorization_directory.cleanup)
        authorization_path, authorization_binding = _write_authorization(
            Path(authorization_directory.name),
            [_shard_receipt(shard_id) for shard_id in ASSIGNMENTS],
        )
        authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
        input_rows = copy.deepcopy(authorization["final_shard_receipts"])
        witness_rows = copy.deepcopy(authorization["terminal_witnesses"])
        receipt = {
            "artifact": "M245_AGGREGATION_RECEIPT",
            "schema": "m245-aggregation-receipt-v1",
            "authorization_binding": authorization_binding,
            "input_shard_receipts": input_rows,
            "input_terminal_witnesses": witness_rows,
            "intent_publication": {
                "path": AGGREGATION_NAMESPACE["intent"],
                "sha256": "4" * 64,
                "source_final_same_device_inode": True,
                "temporary_unlinked": True,
                "reopened_bytes_equal": True,
            },
            "output_publication": {
                "bytes": 2000,
                "path": AGGREGATION_NAMESPACE["result"],
                "sha256": "5" * 64,
                "source_final_same_device_inode": True,
                "temporary_unlinked": True,
                "reopened_bytes_equal": True,
            },
            "postpublication_verification": {
                "input_bytes_and_identities_unchanged": True,
                "output_bytes_and_identity_unchanged": True,
            },
            "process_tree": {
                "aggregation_launch_slots": 1,
                "os_process_creations": 3,
                "inert_launcher_redirector_count": 1,
                "scientific_worker_children": 0,
                "scientific_worker_count": 1,
            },
            "network": False,
            "no_scientific_imports": True,
            "wall_seconds": 100.0,
            "status": "PASS",
        }
        self.assertEqual(tuple(receipt), AGGREGATION_RECEIPT_KEYS)
        self.assertEqual(len(receipt["input_shard_receipts"]), 4)
        self.assertEqual(len(receipt["input_terminal_witnesses"]), 8)
        self.assertEqual(
            {row["path"] for row in receipt["input_shard_receipts"]},
            {
                str((Path(authorization_directory.name) / name).resolve())
                for name in FINAL_RECEIPT_NAMES
            },
        )
        self.assertEqual(
            {(row["shard_id"], row["invocation_index"]) for row in receipt["input_terminal_witnesses"]},
            {(shard_id, invocation_index) for shard_id in ASSIGNMENTS for invocation_index in (1, 2)},
        )
        aggregation.validate_aggregation_receipt(receipt)
        mutations = []
        for path, value in (
            (("wall_seconds",), 120.0001),
            (("network",), True),
            (("no_scientific_imports",), False),
            (("process_tree", "aggregation_launch_slots"), 2),
            (("process_tree", "os_process_creations"), 4),
            (("process_tree", "scientific_worker_children"), 1),
            (("output_publication", "source_final_same_device_inode"), False),
            (
                ("postpublication_verification", "input_bytes_and_identities_unchanged"),
                False,
            ),
            (("authorization_binding", "repository_commit"), "0" * 40),
            (("authorization_binding", "inode"), 10),
        ):
            changed = copy.deepcopy(receipt)
            if len(path) == 1:
                changed[path[0]] = value
            else:
                changed[path[0]][path[1]] = value
            mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["input_shard_receipts"].pop()
        mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["input_terminal_witnesses"][7]["status"] = "PASS_M245_INVOCATION_BOUND"
        mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["input_terminal_witnesses"].pop()
        mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["input_terminal_witnesses"][7]["path"] = changed["input_terminal_witnesses"][6]["path"]
        mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["input_shard_receipts"][3]["sha256"] = changed["input_shard_receipts"][2]["sha256"]
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(aggregation.M245AggregationContractError):
                aggregation.validate_aggregation_receipt(changed)


if __name__ == "__main__":
    unittest.main()
