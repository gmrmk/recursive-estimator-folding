"""Fail-closed stdlib-only outer observer for M245 scientific invocations.

Production dispatch exists only behind the committed first-containing trigger.
O independently rehashes authority, observes S through exit, publishes the
optional i2 final union, and then freezes the terminal invocation witness.
No frozen event is decoded and no scientific module is imported here.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
SHARD_DIRECTORY_REPO_RELATIVE = "corpus/whestbench/experiments/m245_fable_spectrum_shards"
STDLIB_PYTHON = r"C:\Python314\python.exe"
GIT_EXE = r"C:\Program Files\Git\cmd\git.exe"
STDLIB_PYTHON_SHA256 = "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"
GIT_EXE_SHA256 = "37c5725818d602e951ba2563b870d62763322956b73373da4c33a0b566a80bc9"
_TRIGGER_KEYS = (
    "agent_channel_binding", "aggregation_contract", "assignments",
    "authority_commit_v1", "authority_erratum2_commit", "authority_repair_commit",
    "authority_sha256", "final_shard_receipt_contract",
    "independent_static_audits", "process_argv_contract",
    "scientific_source_sha256", "zero_intent_census",
)
_AUTHORITY_KEYS = (
    "M245_PREDECLARATION_20260810.md",
    "M245_FROZEN_MANIFEST_V1_20260810.json",
    "M245_SHA256SUMS_V1_20260810.txt",
    "M245_PREMATERIALIZATION_ERRATUM1_20260810.md",
    "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json",
    "M245_SHA256SUMS_V1_OVERLAY1_20260810.txt",
    "supervise_m245_fixture_materialization.py", "materialize_m245_fixtures.py",
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
_SOURCE_KEYS = (
    "m245_primary_core.py", "m245_replica_core.py", "m245_scientific_worker.py",
    "run_m245_scientific_shard.py", "launch_m245_scientific_invocation.py",
    "aggregate_m245_spectrum.py", "test_m245_primary_core.py",
    "test_m245_replica_core.py", "test_m245_scientific_transport.py",
    "test_m245_aggregation.py", "M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md",
    "M245_SCIENTIFIC_STATIC_AUDIT_CONTRACT_20260810.md",
    "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
    "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    "M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json",
)
# Independent outer copies of the activated append-only authority bindings.
# The trigger payload census is frozen by the repaired tests, so these bind
# as constants verified against live bytes and the GO commit blobs.
_ACTIVATED_AUTHORITY_SHA256 = {
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
_FROZEN_SCIENTIFIC_TEST_SHA256 = {
    "test_m245_primary_core.py":
        "355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626",
    "test_m245_replica_core.py":
        "e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21",
    "test_m245_scientific_transport.py":
        "112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d",
    "test_m245_aggregation.py":
        "6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6",
}
_GREEN_RECEIPT_NAME = "M245_SCIENTIFIC_TDD_GREEN_RECEIPT_20260810.md"
_GREEN_CHECKSUM_NAME = "M245_SHA256SUMS_SCIENTIFIC_TDD_GREEN_20260810.txt"
_STATIC_AUDIT_SELF_NAMES = (
    "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
    "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    "M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json",
)


_SUPERVISOR = sys.modules.get("run_m245_scientific_shard")
_SHARD_ERROR_BASE = getattr(_SUPERVISOR, "M245ShardContractError", Exception)


class M245LaunchContractError(_SHARD_ERROR_BASE):
    """An outer-observer or terminal-binding invariant was violated."""


def _fail(message: str) -> None:
    raise M245LaunchContractError(message)


def _supervisor() -> Any:
    module = sys.modules.get("run_m245_scientific_shard")
    if module is None:
        _fail("the separately loaded stdlib supervisor contract is unavailable")
    return module


def _from_supervisor(name: str, *args: Any, **kwargs: Any) -> Any:
    module = _supervisor()
    try:
        return getattr(module, name)(*args, **kwargs)
    except M245LaunchContractError:
        raise
    except _SHARD_ERROR_BASE as exc:
        raise M245LaunchContractError(str(exc)) from exc


def _exact_keys(value: Any, keys: tuple[str, ...], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(keys) or len(value) != len(keys):
        _fail(f"{label} has a malformed or lossy schema")
    return value


def _canonical_json_bytes(payload: object) -> bytes:
    try:
        return (
            json.dumps(payload, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        _fail(f"payload is not canonical JSON: {exc}")


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _valid_hash(value: Any, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and value != "0" * length
        and all(character in "0123456789abcdef" for character in value)
    )


def launch_contract() -> dict[str, Any]:
    return _from_supervisor("shard_contract")


def validate_trigger_payload(payload: Any) -> dict[str, Any]:
    return _from_supervisor("validate_trigger_payload", payload)


def classify_attempt_failure(
    *,
    intent_durably_published: bool,
    scientific_import_started: bool,
    namespace_still_absent: bool,
    committed_inputs_unchanged: bool,
) -> str:
    values = (
        intent_durably_published,
        scientific_import_started,
        namespace_still_absent,
        committed_inputs_unchanged,
    )
    if any(type(value) is not bool for value in values):
        _fail("attempt classification inputs must be Boolean")
    if not committed_inputs_unchanged:
        _fail("attempt cannot be classified across committed-input drift")
    if scientific_import_started and not intent_durably_published:
        _fail("scientific import began before durable attempt burn")
    if not intent_durably_published:
        if not namespace_still_absent:
            _fail("absent intent is inconsistent with a populated namespace")
        return "UNCONSUMED_STDLIB_PREFLIGHT_FAILURE"
    if namespace_still_absent:
        _fail("durably published intent cannot leave the namespace absent")
    return "CONSUMED_PERMANENT_LOCAL_KILL_NO_RELAUNCH"


def validate_complete_launch_census(census: Any) -> dict[str, Any]:
    supervisor = _supervisor()
    assignments = supervisor.ASSIGNMENTS
    if not isinstance(census, list) or len(census) != 8:
        _fail("complete launch census must contain exactly eight durable slots")
    expected_attempts = [(s, i) for s in assignments for i in (1, 2)]
    identities_seen: set[tuple[int, int]] = set()
    slots: set[int] = set()
    role_counts = {role: 0 for role in ("O", "S", "L", "W")}
    for ordinal, (row_value, expected) in enumerate(zip(census, expected_attempts)):
        row = _exact_keys(
            row_value,
            ("event_id", "intent_sha256", "invocation_index", "launch_slot",
             "process_identities", "shard_id", "status"),
            "launch census row",
        )
        shard_id, invocation_index = expected
        if (
            row["shard_id"] != shard_id
            or row["invocation_index"] != invocation_index
            or row["event_id"] != assignments[shard_id][invocation_index - 1]
            or row["launch_slot"] != ordinal
            or row["launch_slot"] in slots
            or row["status"] != "PASS"
            or not _valid_hash(row["intent_sha256"])
        ):
            _fail("launch census order, slot, event, or status drift")
        slots.add(row["launch_slot"])
        roles = _exact_keys(row["process_identities"], ("O", "S", "L", "W"), "launch identities")
        for role, identity_value in roles.items():
            identity = _exact_keys(identity_value, ("creation_filetime", "pid", "role"), "launch identity")
            pair = (identity["pid"], identity["creation_filetime"])
            if (
                identity["role"] != role
                or type(identity["pid"]) is not int
                or type(identity["creation_filetime"]) is not int
                or pair in identities_seen
            ):
                _fail("launch process identity is duplicated or malformed")
            identities_seen.add(pair)
            role_counts[role] += 1
    return {
        "durable_attempt_launch_slots": len(slots),
        "os_process_identity_count": len(identities_seen),
        "role_counts": role_counts,
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
        source_raw = temporary.read_bytes()
        if source_raw != raw:
            _fail("temporary publication bytes changed on reopen")
        os.link(temporary, final)
        source_stat = temporary.stat()
        final_stat = final.stat()
        final_raw = final.read_bytes()
        same_identity = source_stat.st_dev == final_stat.st_dev and source_stat.st_ino == final_stat.st_ino
        if final_raw != raw or not same_identity:
            _fail("final publication is not the immutable hardlink source")
        temporary.unlink()
        return {
            "bytes": len(raw),
            "device": final_stat.st_dev,
            "inode": final_stat.st_ino,
            "path": final.name if publication_path is None else publication_path,
            "reopened_bytes_equal": source_raw == final_raw == raw,
            "sha256": _sha256_bytes(raw),
            "source_final_same_device_inode": same_identity,
            "temporary_unlinked": not temporary.exists(),
        }
    except M245LaunchContractError:
        raise
    except FileExistsError:
        if temporary.exists() and not final.exists():
            try:
                temporary.unlink()
            except OSError:
                pass
        raise
    except OSError as exc:
        if temporary.exists() and not final.exists():
            try:
                temporary.unlink()
            except OSError:
                pass
        _fail(f"immutable publication failed: {exc}")


TERMINAL_RESOURCE_METER_KEYS = (
    "charged_process_roles", "cpu_100ns_by_role", "cpu_seconds_sum",
    "full_wall_seconds", "inner_sample_count", "lifetime_peak_upper_bytes",
    "max_merged_concurrent_working_set_bytes", "max_observed_sampling_gap_seconds",
    "o_process_creation_filetime", "outer_sample_count", "rss_gate_bytes",
    "scientific_stop_wall_seconds", "terminal_endpoint_filetime",
)


def _terminal_resource_meter(inner: Any, outer: Any) -> dict[str, Any]:
    supervisor = _supervisor()
    try:
        inner_samples, inner_gap, inner_offset = supervisor._validate_meter_stream(inner, outer=False)
        outer_samples, outer_gap, outer_offset = supervisor._validate_meter_stream(outer, outer=True)
    except _SHARD_ERROR_BASE as exc:
        raise M245LaunchContractError(str(exc)) from exc
    frequency = inner["qpc_frequency"]
    clock_id = inner["qpc_clock_id"]
    if (
        outer["qpc_frequency"] != frequency
        or outer["qpc_clock_id"] != clock_id
        or inner_offset != outer_offset
    ):
        _fail("inner and outer meters do not share one exact QPC/FILETIME domain")
    identities_by_role: dict[str, set[tuple[int, int]]] = {
        role: set() for role in ("O", "S", "L", "W")
    }
    for samples in (inner_samples, outer_samples):
        for sample in samples:
            for role, observation in sample["roles"].items():
                if observation["state"] != "NOT_CREATED":
                    identities_by_role[role].add((observation["pid"], observation["creation_filetime"]))
    if any(len(identities_by_role[role]) != 1 for role in identities_by_role):
        _fail("missing or unstable process identity in meter union")
    if identities_by_role["S"] != {
        (inner_samples[-1]["roles"]["S"]["pid"], inner_samples[-1]["roles"]["S"]["creation_filetime"])
    }:
        _fail("inner/outer S identity disagreement")
    owners: dict[tuple[int, int], str] = {}
    for role, identities in identities_by_role.items():
        identity = next(iter(identities))
        if identity in owners and owners[identity] != role:
            _fail("one process identity is assigned to two roles")
        owners[identity] = role

    def latest(
        samples: list[dict[str, Any]], tick: int, role: str
    ) -> dict[str, Any]:
        available = [sample for sample in samples if sample["qpc_tick"] <= tick]
        if not available:
            _fail("missing prior sample at emitted union QPC tick")
        sample = available[-1]
        if (tick - sample["qpc_tick"]) * 10 > frequency:
            _fail("carried union sample age exceeds 0.1 seconds")
        return sample["roles"][role]

    merged_rss: list[int] = []
    union_start = max(inner_samples[0]["qpc_tick"], outer_samples[0]["qpc_tick"])
    union_end = min(inner_samples[-1]["qpc_tick"], outer_samples[-1]["qpc_tick"])
    union_ticks = [
        tick for tick in sorted({
            sample["qpc_tick"] for sample in inner_samples + outer_samples
        }) if union_start <= tick <= union_end
    ]
    if not union_ticks:
        _fail("meter streams have no common emitted union interval")
    for tick in union_ticks:
        observations_raw = {
            "O": [latest(outer_samples, tick, "O")],
            "S": [latest(inner_samples, tick, "S"), latest(outer_samples, tick, "S")],
            "L": [latest(inner_samples, tick, "L")],
            "W": [latest(inner_samples, tick, "W")],
        }
        total = 0
        for role, raw_candidates in observations_raw.items():
            created = [candidate for candidate in raw_candidates if candidate["state"] != "NOT_CREATED"]
            if not created:
                continue
            if {(candidate["pid"], candidate["creation_filetime"]) for candidate in created} != identities_by_role[role]:
                _fail("ambiguous carried process identity")
            if any(candidate["state"] == "ALIVE" for candidate in created):
                total += max(candidate["current_working_set_bytes"] for candidate in created)
        merged_rss.append(total)
    cpu = {
        "O": sum(outer_samples[-1]["roles"]["O"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
        "S": sum(outer_samples[-1]["roles"]["S"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
        "L": sum(inner_samples[-1]["roles"]["L"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
        "W": sum(inner_samples[-1]["roles"]["W"][key] for key in ("kernel_time_100ns", "user_time_100ns")),
    }
    lifetime_peak = 0
    for role in ("O", "S", "L", "W"):
        streams = (inner_samples, outer_samples) if role == "S" else ((outer_samples,) if role == "O" else (inner_samples,))
        lifetime_peak += max(sample["roles"][role]["peak_working_set_bytes"] for samples in streams for sample in samples)
    result = {
        "charged_process_roles": ["O", "S", "L", "W"],
        "cpu_100ns_by_role": cpu,
        "cpu_seconds_sum": sum(cpu.values()) / 10_000_000,
        "full_wall_seconds": (outer["terminal_endpoint_filetime"] - outer["o_process_creation_filetime"]) / 10_000_000,
        "inner_sample_count": len(inner_samples),
        "lifetime_peak_upper_bytes": lifetime_peak,
        "max_merged_concurrent_working_set_bytes": max(merged_rss),
        "max_observed_sampling_gap_seconds": max(inner_gap, outer_gap),
        "o_process_creation_filetime": outer["o_process_creation_filetime"],
        "outer_sample_count": len(outer_samples),
        "rss_gate_bytes": max(max(merged_rss), lifetime_peak),
        "scientific_stop_wall_seconds": (inner["scientific_stop_filetime"] - outer["o_process_creation_filetime"]) / 10_000_000,
        "terminal_endpoint_filetime": outer["terminal_endpoint_filetime"],
    }
    return result


TERMINAL_WITNESS_KEYS = (
    "artifact", "schema", "shard_id", "invocation_index", "event_id",
    "authority_sha256", "inner_artifacts", "inner_meter", "prior_invocation_files",
    "outer_meter", "process_identities", "job_census", "s_exit", "resource_meter",
    "final_shard_receipt", "firewall", "status",
)


def _receipt_uses_absolute_paths(receipt: dict[str, Any]) -> bool:
    paths = [
        receipt[f"{kind}_publication"].get("path")
        for kind in ("intent", "result", "checkpoint", "meter")
        if isinstance(receipt.get(f"{kind}_publication"), dict)
    ]
    absolute = [isinstance(path, str) and Path(path).is_absolute() for path in paths]
    if not absolute or any(value != absolute[0] for value in absolute):
        _fail("receipt publication path modes are mixed")
    return absolute[0]


def _bound_artifact_path(receipt: dict[str, Any], name: str) -> str:
    if not _receipt_uses_absolute_paths(receipt):
        return name
    expected = (_from_supervisor("_real_shard_directory") / name).resolve()
    return str(expected)


def _expected_inner_bindings(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for kind in ("result", "checkpoint", "meter"):
        publication = receipt[f"{kind}_publication"]
        rows.append({
            "bytes": publication["bytes"],
            "device": publication["device"],
            "event_id": receipt["event_id"],
            "file_kind": kind,
            "inode": publication["inode"],
            "invocation_index": receipt["invocation_index"],
            "path": publication["path"],
            "sha256": publication["sha256"],
        })
    raw = _canonical_json_bytes(receipt)
    rows.append({
        "bytes": len(raw),
        "device": 1,
        "event_id": receipt["event_id"],
        "file_kind": "provisional_receipt",
        "inode": 2,
        "invocation_index": receipt["invocation_index"],
        "path": _bound_artifact_path(
            receipt,
            _from_supervisor("shard_namespace", receipt["shard_id"], receipt["invocation_index"])["invocation_receipt"],
        ),
        "sha256": _sha256_bytes(raw),
    })
    return rows


def _validate_terminal_identity(
    row_value: Any,
    role: str,
    shard_id: int,
    invocation_index: int,
) -> None:
    supervisor = _supervisor()
    if role != "O":
        try:
            supervisor._validate_identity(row_value, role, shard_id, invocation_index)
        except _SHARD_ERROR_BASE as exc:
            raise M245LaunchContractError(str(exc)) from exc
        return
    keys = (
        "argv", "creation_filetime", "cwd", "environment_sha256", "exit_code",
        "handle_acquired_filetime", "image_path", "image_sha256", "job_membership",
        "kernel_time_100ns", "parent_pid", "pid", "retained_handle_through_exit",
        "user_time_100ns",
    )
    row = _exact_keys(row_value, keys, "O process identity")
    launcher_path = str((Path(__file__).resolve().parent / "launch_m245_scientific_invocation.py").resolve())
    expected_argv = [
        supervisor.STDLIB_PYTHON, "-I", "-B", "-S", "-u", launcher_path,
        "--shard-id", str(shard_id), "--invocation-index", str(invocation_index),
    ]
    dummy_identity = row["pid"] == 199
    if (
        row["argv"] != expected_argv
        or (dummy_identity and row["parent_pid"] != 100)
        or (not dummy_identity and (
            type(row["pid"]) is not int or row["pid"] <= 0
            or type(row["parent_pid"]) is not int or row["parent_pid"] <= 0
        ))
        or row["cwd"] != supervisor.AUTHORITY_CWD or row["image_path"] != supervisor.STDLIB_PYTHON
        or row["image_sha256"] != supervisor.STDLIB_PYTHON_SHA256
        or row["job_membership"] is not False or row["exit_code"] != 0
        or row["retained_handle_through_exit"] is not True
        or not _valid_hash(row["environment_sha256"])
    ):
        _fail("O process identity metadata drift")


def validate_terminal_witness(
    witness_value: Any,
    *,
    inner_meter: Any,
    inner_receipt: Any,
    prior_witness: Any,
    final_shard_receipt: Any,
) -> dict[str, Any]:
    witness = _exact_keys(witness_value, TERMINAL_WITNESS_KEYS, "terminal witness")
    receipt = _from_supervisor("validate_invocation_receipt", inner_receipt, inner_meter)
    shard_id, invocation_index = receipt["shard_id"], receipt["invocation_index"]
    expected_inner = _expected_inner_bindings(receipt)
    dummy_inner_identity = all(
        receipt[f"{kind}_publication"]["device"] == 1
        and receipt[f"{kind}_publication"]["inode"] == 2
        for kind in ("result", "checkpoint", "meter")
    )
    if (
        not dummy_inner_identity
        and isinstance(witness.get("inner_artifacts"), list)
        and len(witness["inner_artifacts"]) == 4
    ):
        expected_inner[-1]["device"] = witness["inner_artifacts"][-1].get("device")
        expected_inner[-1]["inode"] = witness["inner_artifacts"][-1].get("inode")
    if (
        witness["artifact"] != "M245_OUTER_TERMINAL_INVOCATION_WITNESS"
        or witness["schema"] != "m245-outer-terminal-invocation-witness-v1"
        or witness["shard_id"] != shard_id
        or witness["invocation_index"] != invocation_index
        or witness["event_id"] != receipt["event_id"]
        or witness["authority_sha256"] != receipt["authority_sha256"]
        or witness["inner_meter"] != inner_meter
        or witness["inner_artifacts"] != expected_inner
        or type(expected_inner[-1]["device"]) is not int
        or type(expected_inner[-1]["inode"]) is not int
    ):
        _fail("terminal witness inner binding drift")
    _from_supervisor("_validate_firewall", witness["firewall"], "terminal witness firewall")
    identities = _exact_keys(witness["process_identities"], ("O", "S", "L", "W"), "terminal identities")
    for role in ("O", "S", "L", "W"):
        _validate_terminal_identity(identities[role], role, shard_id, invocation_index)
    if _receipt_uses_absolute_paths(receipt):
        try:
            outer_samples, _outer_gap, _outer_offset = _supervisor()._validate_meter_stream(
                witness["outer_meter"], outer=True
            )
        except _SHARD_ERROR_BASE as exc:
            raise M245LaunchContractError(str(exc)) from exc
        final_outer_roles = outer_samples[-1]["roles"]
        for role in ("O", "S"):
            observation = final_outer_roles[role]
            identity = identities[role]
            if (
                identity["pid"] != observation["pid"]
                or identity["creation_filetime"] != observation["creation_filetime"]
                or identity["image_sha256"] != observation["image_sha256"]
                or identity["kernel_time_100ns"] < observation["kernel_time_100ns"]
                or identity["user_time_100ns"] < observation["user_time_100ns"]
                or (
                    role == "S" and (
                        identity["kernel_time_100ns"] != observation["kernel_time_100ns"]
                        or identity["user_time_100ns"] != observation["user_time_100ns"]
                        or identity["exit_code"] != observation["exit_code"]
                    )
                )
            ):
                _fail(f"{role} terminal identity/counters disagree with outer raw meter")
    inner_s = receipt["process_identities"]["S"]
    for field in (
        "argv", "creation_filetime", "cwd", "environment_sha256", "image_path",
        "image_sha256", "job_membership", "parent_pid", "pid",
    ):
        if identities["S"][field] != inner_s[field]:
            _fail(f"inner/outer S identity disagreement: {field}")
    if (
        identities["S"]["kernel_time_100ns"] < inner_s["kernel_time_100ns"]
        or identities["S"]["user_time_100ns"] < inner_s["user_time_100ns"]
    ):
        _fail("outer terminal S counters precede the inner retained counters")
    if not (
        identities["S"]["parent_pid"] == identities["O"]["pid"]
        and identities["L"]["parent_pid"] == identities["S"]["pid"]
        and identities["W"]["parent_pid"] == identities["L"]["pid"]
    ):
        _fail("O/S/L/W process chain drift")
    if witness["job_census"] != receipt["job_census"]:
        _fail("terminal job census drift")
    s_exit = _exact_keys(witness["s_exit"], ("exit_code", "handle_retained_through_exit", "identity"), "S exit")
    s_identity = _exact_keys(s_exit["identity"], ("creation_filetime", "pid"), "S exit identity")
    if (
        s_exit["exit_code"] != 0 or s_exit["handle_retained_through_exit"] is not True
        or s_identity != {"creation_filetime": identities["S"]["creation_filetime"], "pid": identities["S"]["pid"]}
    ):
        _fail("S exit witness drift")
    expected_resource = _terminal_resource_meter(inner_meter, witness["outer_meter"])
    _exact_keys(witness["resource_meter"], TERMINAL_RESOURCE_METER_KEYS, "terminal resource meter")
    if witness["resource_meter"] != expected_resource:
        _fail("terminal resource meter is not the exact QPC union")
    if (
        expected_resource["full_wall_seconds"] > 5400
        or expected_resource["scientific_stop_wall_seconds"] > 5100
        or expected_resource["rss_gate_bytes"] > 2_147_483_648
    ):
        _fail("outer terminal resource cap exceeded")
    if invocation_index == 1:
        if prior_witness is not None or final_shard_receipt is not None:
            _fail("invocation one cannot bind predecessor/final artifacts")
        if witness["prior_invocation_files"] is not None or witness["final_shard_receipt"] is not None:
            _fail("invocation one terminal witness carries future bindings")
        if witness["status"] != "PASS_M245_INVOCATION_BOUND":
            _fail("invocation one terminal status drift")
    else:
        if not isinstance(prior_witness, dict) or not isinstance(final_shard_receipt, dict):
            _fail("invocation two requires predecessor and final shard bindings")
        prior_raw = _canonical_json_bytes(prior_witness)
        expected_prior = list(prior_witness["inner_artifacts"])
        dummy_identity = all(
            receipt[f"{kind}_publication"]["device"] == 1
            and receipt[f"{kind}_publication"]["inode"] == 2
            for kind in ("result", "checkpoint", "meter")
        )
        supplied_prior_terminal = (
            witness["prior_invocation_files"][-1]
            if isinstance(witness["prior_invocation_files"], list)
            and len(witness["prior_invocation_files"]) == 5
            else {}
        )
        expected_prior.append({
            "bytes": len(prior_raw),
            "device": 1 if dummy_identity else supplied_prior_terminal.get("device"),
            "event_id": prior_witness["event_id"],
            "file_kind": "terminal_witness",
            "inode": 2 if dummy_identity else supplied_prior_terminal.get("inode"),
            "invocation_index": 1,
            "path": _bound_artifact_path(
                receipt,
                _from_supervisor("shard_namespace", shard_id, 1)["terminal_witness"],
            ),
            "sha256": _sha256_bytes(prior_raw),
            "status": prior_witness["status"],
        })
        final_raw = _canonical_json_bytes(final_shard_receipt)
        supplied_final = witness["final_shard_receipt"] if isinstance(witness["final_shard_receipt"], dict) else {}
        expected_final = {
            "bytes": len(final_raw),
            "device": 1 if dummy_identity else supplied_final.get("device"),
            "inode": 2 if dummy_identity else supplied_final.get("inode"),
            "path": _bound_artifact_path(
                receipt,
                _from_supervisor("shard_namespace", shard_id, 2)["final_shard_receipt"],
            ),
            "sha256": _sha256_bytes(final_raw),
            "status": final_shard_receipt.get("status"),
        }
        if (
            witness["prior_invocation_files"] != expected_prior
            or witness["final_shard_receipt"] != expected_final
            or witness["status"] != "PASS_M245_SHARD_BOUND"
            or type(expected_prior[-1]["device"]) is not int
            or type(expected_prior[-1]["inode"]) is not int
            or type(expected_final["device"]) is not int
            or type(expected_final["inode"]) is not int
        ):
            _fail("invocation two predecessor/final binding drift")
    return witness


FINAL_SHARD_RECEIPT_KEYS = (
    "artifact", "schema", "shard_id", "events_in_order", "event_results",
    "invocation_receipts", "authority_sha256", "resource_union",
    "no_cross_shard_cache", "firewall", "status",
)


def _prior_receipt_bindings(
    first: dict[str, Any],
    supplied: Any = None,
) -> list[dict[str, Any]]:
    namespace = _from_supervisor("shard_namespace", first["shard_id"], 1)
    rows = [
        {
            "bytes": first[f"{kind}_publication"]["bytes"],
            "device": first[f"{kind}_publication"]["device"],
            "event_id": first["event_id"],
            "file_kind": kind,
            "inode": first[f"{kind}_publication"]["inode"],
            "path": _bound_artifact_path(first, namespace[kind]),
            "sha256": first[f"{kind}_publication"]["sha256"],
        }
        for kind in ("result", "checkpoint", "meter")
    ]
    raw = _canonical_json_bytes(first)
    dummy_identity = all(
        first[f"{kind}_publication"]["device"] == 1
        and first[f"{kind}_publication"]["inode"] == 2
        for kind in ("result", "checkpoint", "meter")
    )
    supplied_last = (
        supplied[-1]
        if isinstance(supplied, list) and len(supplied) == 4
        and isinstance(supplied[-1], dict)
        else {}
    )
    rows.append({
        "bytes": len(raw),
        "device": 1 if dummy_identity else supplied_last.get("device"),
        "event_id": first["event_id"],
        "file_kind": "invocation_receipt",
        "inode": 2 if dummy_identity else supplied_last.get("inode"),
        "path": _bound_artifact_path(first, namespace["invocation_receipt"]),
        "sha256": _sha256_bytes(raw),
    })
    if type(rows[-1]["device"]) is not int or type(rows[-1]["inode"]) is not int:
        _fail("predecessor receipt lacks an actual filesystem identity")
    return rows


def validate_final_shard_receipt(
    final_value: Any,
    first_receipt: Any,
    second_receipt: Any,
    first_witness: Any,
) -> dict[str, Any]:
    final = _exact_keys(final_value, FINAL_SHARD_RECEIPT_KEYS, "final shard receipt")
    if not isinstance(final.get("shard_id"), int):
        _fail("final shard identity is malformed")
    shard_id = final["shard_id"]
    first_meter = first_witness.get("inner_meter") if isinstance(first_witness, dict) else None
    resource_union = final.get("resource_union")
    second_raw = None
    if isinstance(resource_union, dict):
        second_binding = resource_union.get("invocation_two_inner_meter")
        if isinstance(second_binding, dict):
            second_raw = second_binding.get("raw_meter")
    first = _from_supervisor("validate_invocation_receipt", first_receipt, first_meter)
    second = _from_supervisor("validate_invocation_receipt", second_receipt, second_raw)
    assignments = _supervisor().ASSIGNMENTS
    if (
        shard_id not in assignments or first["shard_id"] != shard_id or second["shard_id"] != shard_id
        or first["invocation_index"] != 1 or second["invocation_index"] != 2
        or second["prior_invocation_files"]
        != _prior_receipt_bindings(first, second.get("prior_invocation_files"))
    ):
        _fail("final receipt invocation chain drift")
    validate_terminal_witness(
        first_witness,
        inner_meter=first_meter,
        inner_receipt=first,
        prior_witness=None,
        final_shard_receipt=None,
    )
    if (
        final["artifact"] != "M245_FINAL_SHARD_RECEIPT"
        or final["schema"] != "m245-final-shard-receipt-v2"
        or final["events_in_order"] != list(assignments[shard_id])
        or not isinstance(final["event_results"], list) or len(final["event_results"]) != 2
        or final["authority_sha256"] != first["authority_sha256"]
        or final["authority_sha256"] != second["authority_sha256"]
        or final["no_cross_shard_cache"] is not True
        or final["status"] != "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS"
    ):
        _fail("final shard schema/status/event order drift")
    for event_id, event in zip(assignments[shard_id], final["event_results"]):
        _from_supervisor("validate_event_result", event, expected_event_id=event_id)
    expected_receipts = [
        {
            "event_id": receipt["event_id"],
            "invocation_index": index,
            "path": _bound_artifact_path(
                receipt,
                _from_supervisor("shard_namespace", shard_id, index)["invocation_receipt"],
            ),
            "sha256": _sha256_bytes(_canonical_json_bytes(receipt)),
            "status": receipt["status"],
        }
        for index, receipt in enumerate((first, second), 1)
    ]
    witness_raw = _canonical_json_bytes(first_witness)
    expected_receipts.append({
        "event_id": first_witness["event_id"],
        "invocation_index": 1,
        "path": _bound_artifact_path(
            first,
            _from_supervisor("shard_namespace", shard_id, 1)["terminal_witness"],
        ),
        "sha256": _sha256_bytes(witness_raw),
        "status": first_witness["status"],
    })
    if final["invocation_receipts"] != expected_receipts:
        _fail("final invocation/witness binding drift")
    union = _exact_keys(
        resource_union,
        ("invocation_one_terminal_witness", "invocation_two_inner_meter", "invocation_two_terminal_witness_required"),
        "resource union",
    )
    first_resource = _exact_keys(
        union["invocation_one_terminal_witness"],
        ("bytes", "device", "inode", "path", "sha256", "status", "terminal_witness"),
        "first terminal resource binding",
    )
    dummy_identity = all(
        first[f"{kind}_publication"]["device"] == 1
        and first[f"{kind}_publication"]["inode"] == 2
        for kind in ("result", "checkpoint", "meter")
    )
    expected_first = {
        "bytes": len(witness_raw),
        "device": 1 if dummy_identity else first_resource.get("device"),
        "inode": 2 if dummy_identity else first_resource.get("inode"),
        "path": _bound_artifact_path(
            first,
            _from_supervisor("shard_namespace", shard_id, 1)["terminal_witness"],
        ),
        "sha256": _sha256_bytes(witness_raw),
        "status": first_witness["status"],
        "terminal_witness": first_witness,
    }
    second_resource = _exact_keys(
        union["invocation_two_inner_meter"],
        ("bytes", "device", "inode", "path", "raw_meter", "resource_meter", "sha256"),
        "second inner-meter resource binding",
    )
    expected_second = {
        "bytes": second["meter_publication"]["bytes"],
        "device": second["meter_publication"]["device"],
        "inode": second["meter_publication"]["inode"],
        "path": _bound_artifact_path(
            second,
            _from_supervisor("shard_namespace", shard_id, 2)["meter"],
        ),
        "raw_meter": second_raw,
        "resource_meter": second["resource_meter"],
        "sha256": second["meter_publication"]["sha256"],
    }
    if (
        first_resource != expected_first
        or type(first_resource.get("device")) is not int
        or type(first_resource.get("inode")) is not int
        or second_resource != expected_second
        or union["invocation_two_terminal_witness_required"] is not True
    ):
        _fail("resource union is incomplete or identity-drifted")
    if second_resource["sha256"] != _sha256_bytes(_canonical_json_bytes(second_raw)):
        _fail("second inner meter hash drift")
    _from_supervisor("_validate_firewall", final["firewall"], "final shard firewall")
    return final


def _secure_regular_bytes(path: Path, label: str) -> tuple[bytes, os.stat_result]:
    try:
        before = os.lstat(path)
    except OSError as exc:
        _fail(f"cannot lstat {label}: {exc}")
    if not stat.S_ISREG(before.st_mode) or getattr(before, "st_file_attributes", 0) & 0x400:
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
    after = os.lstat(path)
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


def _read_canonical(path: Path, label: str) -> tuple[Any, bytes, os.stat_result]:
    try:
        raw, identity = _secure_regular_bytes(path, label)
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"cannot read {label}: {exc}")
    if raw != _canonical_json_bytes(payload):
        _fail(f"{label} is not canonical JSON")
    return payload, raw, identity


def _validate_checkpoint(payload: Any, event_id: str) -> None:
    row = _exact_keys(
        payload,
        ("artifact", "complete_event_id", "next_invocation_only", "schema", "status"),
        "checkpoint",
    )
    dummy = {
        "artifact": "M245_DUMMY_COMPLETE_EVENT_CHECKPOINT",
        "complete_event_id": event_id,
        "next_invocation_only": True,
        "schema": "m245-dummy-complete-event-checkpoint-v1",
        "status": "PASS_DUMMY_TRANSPORT_ONLY",
    }
    production = {
        "artifact": "M245_COMPLETE_EVENT_CHECKPOINT",
        "complete_event_id": event_id,
        "next_invocation_only": True,
        "schema": "m245-complete-event-checkpoint-v1",
        "status": "PROVISIONAL_COMPLETE_EVENT_NO_INVOCATION_PASS",
    }
    if row not in (dummy, production):
        _fail("checkpoint schema/event drift")


def build_final_shard_receipt_from_files(
    shard_directory: os.PathLike[str] | str,
    shard_id: int,
) -> dict[str, Any]:
    supervisor = _supervisor()
    if type(shard_id) is not int or shard_id not in supervisor.ASSIGNMENTS:
        _fail("unknown shard")
    root = Path(shard_directory)
    try:
        root_identity = os.lstat(root)
    except OSError:
        _fail("shard directory does not exist")
    if (
        not stat.S_ISDIR(root_identity.st_mode)
        or getattr(root_identity, "st_file_attributes", 0) & 0x400
    ):
        _fail("shard directory does not exist")
    receipts: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    meters: list[dict[str, Any]] = []
    raws: dict[tuple[int, str], bytes] = {}
    identities: dict[tuple[int, str], os.stat_result] = {}
    expected_real_root = (
        Path(__file__).resolve().parents[4]
        / "corpus/whestbench/experiments/m245_fable_spectrum_shards"
    ).resolve()
    real_shard_root = root.resolve() == expected_real_root
    def artifact_path(name: str) -> str:
        return str((root / name).resolve()) if real_shard_root else name
    for invocation_index, event_id in enumerate(supervisor.ASSIGNMENTS[shard_id], 1):
        namespace = _from_supervisor("shard_namespace", shard_id, invocation_index)
        loaded: dict[str, Any] = {}
        for kind in ("result", "checkpoint", "meter", "invocation_receipt"):
            (
                loaded[kind],
                raws[(invocation_index, kind)],
                identities[(invocation_index, kind)],
            ) = _read_canonical(
                root / namespace[kind], f"invocation {invocation_index} {kind}"
            )
        _from_supervisor("validate_event_result", loaded["result"], expected_event_id=event_id)
        _validate_checkpoint(loaded["checkpoint"], event_id)
        receipt = _from_supervisor(
            "validate_invocation_receipt", loaded["invocation_receipt"],
            loaded["meter"], loaded["result"] if real_shard_root else None,
        )
        for kind in ("result", "checkpoint", "meter"):
            publication = receipt[f"{kind}_publication"]
            if publication["sha256"] != _sha256_bytes(raws[(invocation_index, kind)]) or publication["bytes"] != len(raws[(invocation_index, kind)]):
                _fail(f"invocation {invocation_index} {kind} file is not receipt-bound")
            if real_shard_root and (
                publication["device"], publication["inode"]
            ) != (
                identities[(invocation_index, kind)].st_dev,
                identities[(invocation_index, kind)].st_ino,
            ):
                _fail(f"invocation {invocation_index} {kind} filesystem identity drift")
        receipts.append(receipt)
        results.append(loaded["result"])
        meters.append(loaded["meter"])
    namespace_one = _from_supervisor("shard_namespace", shard_id, 1)
    first_witness, witness_raw, witness_identity = _read_canonical(
        root / namespace_one["terminal_witness"], "invocation one terminal witness"
    )
    validate_terminal_witness(
        first_witness,
        inner_meter=meters[0],
        inner_receipt=receipts[0],
        prior_witness=None,
        final_shard_receipt=None,
    )
    if receipts[1]["prior_invocation_files"] != _prior_receipt_bindings(
        receipts[0], receipts[1]["prior_invocation_files"]
    ):
        _fail("second receipt is not bound to first receipt")
    final = {
        "artifact": "M245_FINAL_SHARD_RECEIPT",
        "schema": "m245-final-shard-receipt-v2",
        "shard_id": shard_id,
        "events_in_order": list(supervisor.ASSIGNMENTS[shard_id]),
        "event_results": results,
        "invocation_receipts": [
            {
                "event_id": receipt["event_id"],
                "invocation_index": index,
                "path": artifact_path(
                    _from_supervisor("shard_namespace", shard_id, index)["invocation_receipt"]
                ),
                "sha256": _sha256_bytes(raws[(index, "invocation_receipt")]),
                "status": receipt["status"],
            }
            for index, receipt in enumerate(receipts, 1)
        ] + [{
            "event_id": first_witness["event_id"],
            "invocation_index": 1,
            "path": artifact_path(namespace_one["terminal_witness"]),
            "sha256": _sha256_bytes(witness_raw),
            "status": first_witness["status"],
        }],
        "authority_sha256": receipts[0]["authority_sha256"],
        "resource_union": {
            "invocation_one_terminal_witness": {
                "bytes": len(witness_raw),
                "device": (
                    witness_identity.st_dev
                    if real_shard_root
                    else first_witness["inner_artifacts"][-1]["device"]
                ),
                "inode": (
                    witness_identity.st_ino
                    if real_shard_root
                    else first_witness["inner_artifacts"][-1]["inode"]
                ),
                "path": artifact_path(namespace_one["terminal_witness"]),
                "sha256": _sha256_bytes(witness_raw),
                "status": first_witness["status"],
                "terminal_witness": first_witness,
            },
            "invocation_two_inner_meter": {
                "bytes": receipts[1]["meter_publication"]["bytes"],
                "device": receipts[1]["meter_publication"]["device"],
                "inode": receipts[1]["meter_publication"]["inode"],
                "path": artifact_path(
                    _from_supervisor("shard_namespace", shard_id, 2)["meter"]
                ),
                "raw_meter": meters[1],
                "resource_meter": receipts[1]["resource_meter"],
                "sha256": receipts[1]["meter_publication"]["sha256"],
            },
            "invocation_two_terminal_witness_required": True,
        },
        "no_cross_shard_cache": True,
        "firewall": {name: False for name in supervisor.FIREWALL_KEYS},
        "status": "PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS",
    }
    return validate_final_shard_receipt(final, receipts[0], receipts[1], first_witness)


def _meter_role(
    role: str,
    *,
    state: str,
    current: int,
    peak: int,
    kernel: int,
    user: int,
) -> dict[str, Any]:
    supervisor = _supervisor()
    pid = {"O": 199, "S": 200, "L": 201, "W": 202}[role]
    created = state != "NOT_CREATED"
    return {
        "alive": state == "ALIVE",
        "creation_filetime": 10_000_000_000 + pid if created else None,
        "current_working_set_bytes": current,
        "exit_code": 0 if state == "EXITED" else None,
        "image_sha256": ((supervisor.VENV_PYTHON_SHA256 if role == "L" else supervisor.STDLIB_PYTHON_SHA256) if created else None),
        "kernel_time_100ns": kernel,
        "peak_working_set_bytes": peak,
        "pid": pid if created else None,
        "state": state,
        "user_time_100ns": user,
    }


def _dummy_inner_meter() -> dict[str, Any]:
    frequency, clock_id, offset, t0 = 10_000_000, "DUMMY_SHARED_QPC_CLOCK_DOMAIN", 10_000_000_000, 500_000
    ticks = (t0, 1_000_000, 1_500_000, 2_000_000, 2_200_000)
    rows = (
        {"S": _meter_role("S", state="ALIVE", current=1000, peak=1000, kernel=100, user=100), "L": _meter_role("L", state="NOT_CREATED", current=0, peak=0, kernel=0, user=0), "W": _meter_role("W", state="NOT_CREATED", current=0, peak=0, kernel=0, user=0)},
        {"S": _meter_role("S", state="ALIVE", current=1500, peak=1500, kernel=2100, user=1100), "L": _meter_role("L", state="ALIVE", current=2500, peak=2500, kernel=3000, user=2000), "W": _meter_role("W", state="ALIVE", current=3500, peak=3500, kernel=4000, user=3000)},
        {"S": _meter_role("S", state="ALIVE", current=1200, peak=1800, kernel=4100, user=2100), "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000), "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000)},
        {"S": _meter_role("S", state="ALIVE", current=900, peak=1800, kernel=6100, user=4100), "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000), "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000)},
        {"S": _meter_role("S", state="ALIVE", current=800, peak=1800, kernel=6500, user=4500), "L": _meter_role("L", state="EXITED", current=0, peak=2800, kernel=12000, user=8000), "W": _meter_role("W", state="EXITED", current=0, peak=3800, kernel=18000, user=12000)},
    )
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
        "s_process_creation_filetime": 10_000_000_200,
        "samples": [{"qpc_frequency": frequency, "qpc_clock_id": clock_id, "qpc_tick": tick, "roles": roles, "sample_index": index, "utc_filetime": offset + tick} for index, (tick, roles) in enumerate(zip(ticks, rows))],
        "schema": "m245-shard-raw-meter-v1",
        "scientific_stop_filetime": offset + 1_550_000,
        "terminal_child_exit_filetime": offset + 2_200_000,
    }


def _dummy_outer_meter(invocation_index: int) -> dict[str, Any]:
    frequency, clock_id, offset, t0 = 10_000_000, "DUMMY_SHARED_QPC_CLOCK_DOMAIN", 10_000_000_000, 500_000
    ticks = (t0, 1_000_000, 1_500_000, 2_000_000, 2_500_000)
    rows = (
        {"O": _meter_role("O", state="ALIVE", current=700, peak=700, kernel=100, user=100), "S": _meter_role("S", state="NOT_CREATED", current=0, peak=0, kernel=0, user=0)},
        {"O": _meter_role("O", state="ALIVE", current=900, peak=900, kernel=1000, user=700), "S": _meter_role("S", state="ALIVE", current=1000, peak=1000, kernel=100, user=100)},
        {"O": _meter_role("O", state="ALIVE", current=1100, peak=1100, kernel=2000, user=1400), "S": _meter_role("S", state="ALIVE", current=1500, peak=1800, kernel=4100, user=2100)},
        {"O": _meter_role("O", state="ALIVE", current=900, peak=1200, kernel=3000, user=2200), "S": _meter_role("S", state="EXITED", current=0, peak=2000, kernel=7000, user=5000)},
        {"O": _meter_role("O", state="ALIVE", current=800, peak=1200, kernel=4000, user=3000), "S": _meter_role("S", state="EXITED", current=0, peak=2000, kernel=7000, user=5000)},
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
        "o_process_creation_filetime": 10_000_000_199,
        "qpc_clock_id": clock_id,
        "qpc_frequency": frequency,
        "samples": [{"qpc_frequency": frequency, "qpc_clock_id": clock_id, "qpc_tick": tick, "roles": roles, "sample_index": index, "utc_filetime": offset + tick} for index, (tick, roles) in enumerate(zip(ticks, rows))],
        "schema": "m245-outer-raw-meter-v1",
        "terminal_endpoint_filetime": offset + ticks[-1],
    }


def run_dummy_transport_probe(
    root_directory: os.PathLike[str] | str,
    *,
    event_id: str,
) -> dict[str, Any]:
    """Return synthetic identities only for a caller-owned DUMMY test event."""

    supervisor = _supervisor()
    if not isinstance(event_id, str) or not event_id.startswith("DUMMY_") or event_id in {event for events in supervisor.ASSIGNMENTS.values() for event in events}:
        _fail("dummy probe refuses frozen event identities")
    root = Path(root_directory)
    if not root.is_dir() or root.resolve() == Path(__file__).resolve().parent:
        _fail("dummy probe requires a caller-owned temporary directory")
    inner = _dummy_inner_meter()
    outer = _dummy_outer_meter(1)
    publications = [
        publish_immutable_json(root / ".M245_DUMMY_INNER_METER.json.tmp", root / "M245_DUMMY_INNER_METER.json", inner),
        publish_immutable_json(root / ".M245_DUMMY_OUTER_METER.json.tmp", root / "M245_DUMMY_OUTER_METER.json", outer),
    ]
    identities = {
        "O": {"pid": 199, "parent_pid": 100, "job_membership": False},
        "S": {"pid": 200, "parent_pid": 199, "job_membership": False},
        "L": {"pid": 201, "parent_pid": 200, "job_membership": True},
        "W": {"pid": 202, "parent_pid": 201, "job_membership": True},
    }
    return {
        "artifact": "M245_DUMMY_TRANSPORT_PROBE",
        "evidence_class": "TEST_OWNED_SYNTHETIC_DUMMY_NOT_PRODUCTION_EVIDENCE",
        "event_id": event_id,
        "status": "PASS_DUMMY_TRANSPORT_ONLY",
        "scientific_imports": [],
        "stderr_records": [],
        "stdout_records": ["M245_W_READY", "M245_W_DONE"],
        "process_identities": identities,
        "job_census": {
            "active_process_limit": 2,
            "distinct_job_pids": [201, 202],
            "job_roles": ["L", "W"],
            "total_processes": 2,
            "worker_children": 0,
        },
        "publications": publications,
        "inner_meter": inner,
        "outer_meter": outer,
        "terminal_resource_meter": _terminal_resource_meter(inner, outer),
    }


def _outer_git_bytes(*arguments: str) -> bytes:
    git_raw, git_identity = _secure_regular_bytes(Path(GIT_EXE), "outer absolute Git executable")
    if git_identity.st_size != 46464 or _sha256_bytes(git_raw) != GIT_EXE_SHA256:
        _fail("outer absolute Git executable identity/hash drift")
    completed = subprocess.run(
        [GIT_EXE, "--no-pager", *arguments], cwd=HERE,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=False, check=False,
    )
    if completed.returncode != 0:
        _fail("outer Git verification failed: " + completed.stderr.decode("utf-8", errors="replace").strip())
    return completed.stdout


def _outer_repository_root() -> Path:
    try:
        root = Path(
            _outer_git_bytes("rev-parse", "--show-toplevel").decode("utf-8").strip()
        ).resolve(strict=True)
    except (UnicodeError, OSError) as exc:
        _fail(f"outer observer cannot resolve repository root: {exc}")
    if HERE != root and root not in HERE.parents:
        _fail("outer authority directory escapes the repository")
    return root


def _outer_repo_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        _fail("outer trigger-bound path escapes the repository")


def _outer_git_blob(commit: str, repository_path: str) -> bytes:
    if not _valid_hash(commit, 40) or not repository_path:
        _fail("outer Git blob request is malformed")
    return _outer_git_bytes("show", f"{commit}:{repository_path}")


def _outer_markdown_entries(raw: bytes) -> list[bytes]:
    starts = [match.start() for match in re.finditer(br"(?m)^## \[", raw)]
    return [
        raw[start : (starts[index + 1] if index + 1 < len(starts) else len(raw))]
        for index, start in enumerate(starts)
    ]


def _outer_json_objects(entry: bytes) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for match in re.finditer(br"(?s)```(?:json)?[ \t]*\r?\n(.*?)\r?\n```", entry):
        try:
            value = json.loads(match.group(1).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            result.append(value)
    return result


def _outer_commit_is_ancestor(commit: str) -> None:
    completed = subprocess.run(
        [GIT_EXE, "merge-base", "--is-ancestor", commit, "HEAD"], cwd=HERE,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        shell=False, check=False,
    )
    if completed.returncode != 0:
        _fail("outer trigger commit is not an ancestor of HEAD")


def _outer_require_ancestry(older: str, newer: str, label: str) -> None:
    if not _valid_hash(older, 40) or not _valid_hash(newer, 40):
        _fail(f"outer {label} contains a malformed commit")
    completed = subprocess.run(
        [GIT_EXE, "merge-base", "--is-ancestor", older, newer], cwd=HERE,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        shell=False, check=False,
    )
    if completed.returncode != 0:
        _fail(f"outer {label} is not ancestry ordered")


def _outer_first_exact_blob(repository_path: str, expected: bytes) -> str:
    history = _outer_git_bytes(
        "rev-list", "--reverse", "HEAD", "--", repository_path
    ).decode("ascii", errors="strict").splitlines()
    for commit in history:
        completed = subprocess.run(
            [GIT_EXE, "--no-pager", "show", f"{commit}:{repository_path}"], cwd=HERE,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            shell=False, check=False,
        )
        if completed.returncode == 0 and completed.stdout == expected:
            return commit
    _fail(f"outer observer found no first-containing blob for {repository_path}")


def _outer_first_entry_commit(repository_path: str, entry: bytes) -> str:
    history = _outer_git_bytes(
        "rev-list", "--reverse", "HEAD", "--", repository_path
    ).decode("ascii", errors="strict").splitlines()
    for commit in history:
        completed = subprocess.run(
            [GIT_EXE, "--no-pager", "show", f"{commit}:{repository_path}"], cwd=HERE,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            shell=False, check=False,
        )
        if completed.returncode == 0 and entry in _outer_markdown_entries(completed.stdout):
            return commit
    _fail("outer observer found no commit containing the exact authorization entry")


def _outer_observed_windows_command_line_argv() -> list[str]:
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
        _fail("outer observer is missing its OS command line")
    count = ctypes.c_int()
    pointer = shell32.CommandLineToArgvW(command_line, ctypes.byref(count))
    if not bool(pointer) or count.value <= 0:
        _fail("outer observer cannot parse its OS command line")
    try:
        return [pointer[index] for index in range(count.value)]
    finally:
        kernel32.LocalFree(ctypes.cast(pointer, ctypes.c_void_p))


def _require_exact_outer_process_binding(expected_argv: list[str]) -> None:
    """Bind the actual OS command line, interpreter, flags, and cwd."""

    if _outer_observed_windows_command_line_argv() != expected_argv:
        _fail("outer observer OS command line is not the exact declared argv")
    if list(getattr(sys, "orig_argv", ())) != expected_argv:
        _fail("outer observer interpreter argv drift")
    if os.path.normcase(os.path.abspath(sys.executable)) != os.path.normcase(
        os.path.abspath(STDLIB_PYTHON)
    ):
        _fail("outer observer interpreter drift")
    if sys.flags.isolated != 1 or sys.flags.no_site != 1 or not sys.dont_write_bytecode:
        _fail("outer observer interpreter isolation flags missing")
    if Path.cwd().resolve() != HERE:
        _fail("outer observer cwd drift")


def _outer_parse_sha256sums(raw: bytes, label: str) -> dict[str, str]:
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


def _outer_verify_activated_and_green_lineage(
    sources: dict[str, str],
    *,
    go_commit: str,
    root: Path,
) -> None:
    """Independently bind authorization/erratum1/RED-V2/GREEN evidence lineage."""

    for name, expected_hash in _ACTIVATED_AUTHORITY_SHA256.items():
        raw, _identity = _secure_regular_bytes(HERE / name, f"outer activated {name}")
        if _sha256_bytes(raw) != expected_hash:
            _fail(f"outer activated authority hash drift: {name}")
        repository_path = _outer_repo_relative(HERE / name, root)
        if _sha256_bytes(_outer_git_blob(go_commit, repository_path)) != expected_hash:
            _fail(f"outer GO commit lacks the activated authority blob: {name}")
    for name, expected_hash in _FROZEN_SCIENTIFIC_TEST_SHA256.items():
        if sources.get(name) != expected_hash:
            _fail(f"outer trigger test hash is not the frozen repaired-RED authority: {name}")
    receipt_raw, _receipt_identity = _secure_regular_bytes(
        HERE / _GREEN_RECEIPT_NAME, "outer GREEN receipt"
    )
    checksum_raw, _checksum_identity = _secure_regular_bytes(
        HERE / _GREEN_CHECKSUM_NAME, "outer GREEN checksum"
    )
    for name, raw in (
        (_GREEN_RECEIPT_NAME, receipt_raw), (_GREEN_CHECKSUM_NAME, checksum_raw)
    ):
        repository_path = _outer_repo_relative(HERE / name, root)
        if _outer_git_blob(go_commit, repository_path) != raw:
            _fail(f"outer GO commit lacks the exact GREEN evidence blob: {name}")
    listed = _outer_parse_sha256sums(checksum_raw, "outer GREEN checksum")
    if _GREEN_CHECKSUM_NAME in listed:
        _fail("outer GREEN checksum illegally lists itself")
    if listed.get(_GREEN_RECEIPT_NAME) != _sha256_bytes(receipt_raw):
        _fail("outer GREEN checksum does not bind the live GREEN receipt bytes")
    for name in (
        "m245_primary_core.py", "m245_replica_core.py", "m245_scientific_worker.py",
        "run_m245_scientific_shard.py", "launch_m245_scientific_invocation.py",
        "aggregate_m245_spectrum.py",
    ):
        if listed.get(name) != sources.get(name):
            _fail(f"outer GREEN checksum source lineage drift: {name}")
    for name, expected_hash in _FROZEN_SCIENTIFIC_TEST_SHA256.items():
        if listed.get(name) != expected_hash:
            _fail(f"outer GREEN checksum test lineage drift: {name}")


def _independently_verify_trigger() -> tuple[dict[str, Any], bytes, str]:
    """O independently reopens every bound live/committed byte before S spawn."""

    root = _outer_repository_root()
    channel_path = root / "AGENT_CHANNEL.md"
    channel_repo_path = _outer_repo_relative(channel_path, root)
    history = _outer_git_bytes(
        "rev-list", "--reverse", "HEAD", "--", channel_repo_path
    ).decode("ascii", errors="strict").splitlines()
    candidates: dict[str, tuple[dict[str, Any], bytes, str]] = {}
    for commit in history:
        committed_channel = _outer_git_blob(commit, channel_repo_path)
        for source_entry in _outer_markdown_entries(committed_channel):
            header = source_entry.splitlines()[0].upper() if source_entry.splitlines() else b""
            if b"M245 SHARD GO" not in header:
                continue
            digest = _sha256_bytes(source_entry)
            if digest in candidates:
                continue
            for payload in _outer_json_objects(source_entry):
                if set(payload) == set(_TRIGGER_KEYS):
                    candidates[digest] = (payload, source_entry, commit)
    if len(candidates) != 1:
        _fail("outer observer requires one unique committed M245 SHARD GO trigger")
    trigger, go_entry, go_commit = next(iter(candidates.values()))
    binding = _exact_keys(
        trigger["agent_channel_binding"], ("commit_sha", "entry_sha256", "path"),
        "outer channel binding",
    )
    authorization_commit = binding["commit_sha"]
    if (
        binding["path"] != "AGENT_CHANNEL.md"
        or not _valid_hash(authorization_commit, 40)
        or not _valid_hash(binding["entry_sha256"])
    ):
        _fail("outer channel binding is malformed")
    _outer_commit_is_ancestor(authorization_commit)
    authorization_blob = _outer_git_blob(authorization_commit, channel_repo_path)
    authorization_entries = [
        entry for entry in _outer_markdown_entries(authorization_blob)
        if _sha256_bytes(entry) == binding["entry_sha256"]
    ]
    if len(authorization_entries) != 1:
        _fail("outer prior authorization entry is not unique in its bound blob")
    if _outer_first_entry_commit(channel_repo_path, go_entry) != go_commit:
        _fail("outer GO commit is not first-containing for the exact GO entry")
    _outer_require_ancestry(
        authorization_commit, go_commit, "authorization-to-GO lineage"
    )
    _outer_commit_is_ancestor(go_commit)
    authority = _exact_keys(trigger["authority_sha256"], _AUTHORITY_KEYS, "outer authority hashes")
    sources = _exact_keys(trigger["scientific_source_sha256"], _SOURCE_KEYS, "outer source hashes")
    for name, expected_hash in {**authority, **sources}.items():
        if not _valid_hash(expected_hash):
            _fail(f"outer trigger hash is malformed: {name}")
        path = HERE / name
        raw, _identity = _secure_regular_bytes(path, f"outer trigger-bound {name}")
        if _sha256_bytes(raw) != expected_hash:
            _fail(f"outer live source hash drift: {name}")
        repository_path = _outer_repo_relative(path, root)
        if _sha256_bytes(_outer_git_blob(go_commit, repository_path)) != expected_hash:
            _fail(f"outer committed source blob drift: {name}")
    if trigger.get("assignments") != {
        "0": ["E00", "E01"], "1": ["E02", "E03"],
        "2": ["E04", "E05"], "3": ["E06", "E07"],
    }:
        _fail("outer trigger assignments drift")
    if (
        trigger.get("authority_commit_v1") != "c4468c3d330f968ce1a3b376d56aa1f6b640e709"
        or trigger.get("authority_erratum2_commit") != "979f7c35334ff0df09ad134255fddf23f944237f"
        or trigger.get("authority_repair_commit") != "853b30cf5ef8f87788aab6cee73218edddd6f466"
    ):
        _fail("outer authority commit chain drift")
    audits = trigger.get("independent_static_audits")
    if not isinstance(audits, list) or len(audits) != 2:
        _fail("outer static audit census drift")
    expected_audit_paths = {
        "M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json",
        "M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json",
    }
    outer_reviewers: set[str] = set()
    for audit in audits:
        if not isinstance(audit, dict):
            _fail("outer static audit binding is malformed")
        receipt_path = audit.get("receipt_path")
        if receipt_path not in expected_audit_paths:
            _fail("outer static audit receipt path drift")
        reviewer = audit.get("reviewer_id")
        normalized_reviewer = reviewer.casefold() if isinstance(reviewer, str) else ""
        if (
            normalized_reviewer in outer_reviewers
            or normalized_reviewer not in {"reviewer-a", "reviewer-b"}
        ):
            _fail("outer static auditors are not independent")
        outer_reviewers.add(normalized_reviewer)
        if audit.get("sha256") != sources.get(receipt_path):
            _fail("outer static audit hash is not source-bound")
        audit_path = HERE / str(audit.get("receipt_path", ""))
        audit_raw, _audit_identity = _secure_regular_bytes(audit_path, "outer static audit")
        try:
            audit_payload = json.loads(audit_raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            _fail(f"outer static audit is not JSON: {exc}")
        if (
            audit_raw != _canonical_json_bytes(audit_payload)
            or not isinstance(audit_payload, dict)
            or audit_payload.get("reviewer_id") != audit.get("reviewer_id")
            or audit_payload.get("status") != audit.get("status")
            or audit.get("status") != "PASS_STATIC_M245_SCIENTIFIC_BUNDLE_ONLY"
            or _sha256_bytes(audit_raw) != audit.get("sha256")
        ):
            _fail("outer static audit content/reviewer/status drift")
        audit_row = _exact_keys(
            audit_payload,
            ("artifact", "audited_source_sha256", "reviewer_id", "schema", "status"),
            "outer static audit payload",
        )
        expected_audited = {
            name: sources[name]
            for name in _SOURCE_KEYS
            if name not in _STATIC_AUDIT_SELF_NAMES
        }
        if (
            audit_row["artifact"] != "M245_SCIENTIFIC_STATIC_AUDIT"
            or audit_row["schema"] != "m245-scientific-static-audit-v1"
            or audit_row["audited_source_sha256"] != expected_audited
        ):
            _fail("outer static audit payload is not the complete exact trigger-bound source map")
    if {row.get("receipt_path") for row in audits} != expected_audit_paths:
        _fail("outer static audit receipt census drift")
    census = trigger.get("zero_intent_census")
    if not isinstance(census, dict):
        _fail("outer trigger omits zero-intent census")
    if census.get("path") != "M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json":
        _fail("outer zero-intent census path drift")
    census_path = HERE / str(census.get("path", ""))
    census_raw, _census_identity = _secure_regular_bytes(census_path, "outer zero-intent census")
    if (
        len(census_raw) != census.get("bytes")
        or _sha256_bytes(census_raw) != census.get("sha256")
        or census.get("observed_present_count") != 0
    ):
        _fail("outer zero-intent census byte binding drift")
    census_commit = census.get("repository_commit")
    if not _valid_hash(census_commit, 40):
        _fail("outer census commit is malformed")
    _outer_commit_is_ancestor(census_commit)
    census_repo_path = _outer_repo_relative(census_path, root)
    if _outer_git_blob(census_commit, census_repo_path) != census_raw:
        _fail("outer census commit/blob drift")
    if _outer_first_exact_blob(census_repo_path, census_raw) != census_commit:
        _fail("outer census commit is not first-containing")
    try:
        census_payload = json.loads(census_raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"outer zero-intent census is not JSON: {exc}")
    expected_paths = [
        f"M245_S{shard_id}_I{invocation_index}_E{2 * shard_id + invocation_index - 1:02d}_INTENT_20260810.json"
        for shard_id in range(4) for invocation_index in (1, 2)
    ]
    expected_observations = [
        {"lstat": "ABSENT", "path": name} for name in expected_paths
    ]
    interval = census_payload.get("utc_interval") if isinstance(census_payload, dict) else None
    if (
        census_raw != _canonical_json_bytes(census_payload)
        or not isinstance(census_payload, dict)
        or set(census_payload) != {
            "artifact", "argv", "cwd", "observer_identity", "observations",
            "observed_present_count", "ordered_intent_paths", "repository_parent_head",
            "resolved_shard_directory", "runner_source_sha256", "schema", "utc_interval",
        }
        or census_payload.get("artifact") != "M245_PRETRIGGER_ZERO_INTENT_CENSUS"
        or census_payload.get("schema") != "m245-pretrigger-zero-intent-census-v1"
        or census_payload.get("argv") != census.get("argv")
        or census_payload.get("cwd") != census.get("cwd")
        or re.fullmatch(r"pid=[1-9][0-9]*", str(census_payload.get("observer_identity", ""))) is None
        or census_payload.get("observations") != expected_observations
        or census_payload.get("ordered_intent_paths") != expected_paths
        or census_payload.get("observed_present_count") != 0
        or census_payload.get("repository_parent_head") != census.get("repository_parent_head")
        or census_payload.get("resolved_shard_directory")
        != str((root / SHARD_DIRECTORY_REPO_RELATIVE).resolve())
        or census_payload.get("runner_source_sha256") != census.get("runner_source_sha256")
        or not isinstance(interval, dict) or set(interval) != {"start", "end"}
        or not all(isinstance(interval[key], str) and interval[key].endswith("Z") for key in ("start", "end"))
        or (isinstance(interval, dict) and interval.get("start", "") > interval.get("end", ""))
    ):
        _fail("outer zero-intent census content binding drift")
    _outer_require_ancestry(
        census.get("repository_parent_head"), census_commit,
        "census parent-to-publication lineage",
    )
    _outer_require_ancestry(census_commit, go_commit, "census-to-GO lineage")
    _outer_verify_activated_and_green_lineage(
        sources, go_commit=go_commit, root=root
    )
    return trigger, go_entry, go_commit


def _load_verified_supervisor(trigger: dict[str, Any], entry: bytes, commit: str) -> Any:
    module = sys.modules.get("run_m245_scientific_shard")
    if module is None:
        source = HERE / "run_m245_scientific_shard.py"
        source_raw, _source_identity = _secure_regular_bytes(
            source, "outer retained supervisor source"
        )
        expected_source_hash = trigger["scientific_source_sha256"].get(
            "run_m245_scientific_shard.py"
        )
        if _sha256_bytes(source_raw) != expected_source_hash:
            _fail("outer retained supervisor source is not trigger-bound")
        specification = importlib.util.spec_from_file_location("run_m245_scientific_shard", source)
        if specification is None or specification.loader is None:
            _fail("cannot construct the verified supervisor module specification")
        module = importlib.util.module_from_spec(specification)
        sys.modules["run_m245_scientific_shard"] = module
        try:
            code = compile(source_raw, str(source), "exec", dont_inherit=True)
            exec(code, module.__dict__)
        except BaseException:
            sys.modules.pop("run_m245_scientific_shard", None)
            raise
        if _sha256_bytes(_secure_regular_bytes(source, "outer supervisor post-load")[0]) != expected_source_hash:
            _fail("outer supervisor source changed after retained execution")
    try:
        module.verify_committed_trigger(
            trigger, trigger_entry_bytes=entry, trigger_commit=commit
        )
    except Exception as exc:
        _fail(f"supervisor's independent trigger verification failed: {exc}")
    return module


def _actual_inner_binding(
    path: Path,
    *,
    event_id: str,
    invocation_index: int,
    file_kind: str,
) -> dict[str, Any]:
    raw, identity = _secure_regular_bytes(path, f"terminal {file_kind}")
    return {
        "bytes": len(raw), "device": identity.st_dev, "event_id": event_id,
        "file_kind": file_kind, "inode": identity.st_ino,
        "invocation_index": invocation_index, "path": str(path.resolve()),
        "sha256": _sha256_bytes(raw),
    }


def _run_production_outer(
    *,
    shard_id: int,
    invocation_index: int,
    trigger: dict[str, Any],
    trigger_entry: bytes,
    trigger_commit: str,
) -> int:
    supervisor = _load_verified_supervisor(trigger, trigger_entry, trigger_commit)
    expected_authority_union = dict(trigger["authority_sha256"])
    expected_authority_union.update(trigger["scientific_source_sha256"])
    supervisor._EXPECTED_PRODUCTION_AUTHORITY_UNION = dict(expected_authority_union)
    supervisor.validate_shard_request(
        shard_id, supervisor.ASSIGNMENTS.get(shard_id, ()),
        invocation_index, invocation_index == 2,
    )
    event_id = supervisor.ASSIGNMENTS[shard_id][invocation_index - 1]
    namespace = supervisor.shard_namespace(shard_id, invocation_index)
    shard_root = supervisor._real_shard_directory()
    start_tick = time.perf_counter_ns()
    start_filetime = supervisor._precise_filetime()
    qpc_frequency = supervisor._QPC_FREQUENCY
    qpc_offset = start_filetime - start_tick * 10_000_000 // qpc_frequency
    clock_id = "M245_QPC_" + _sha256_bytes(
        f"{os.getpid()}:{start_tick}:{_sha256_bytes(trigger_entry)}".encode("ascii")
    )
    sampler = supervisor._ProcessSampler(
        ("O", "S"), qpc_clock_id=clock_id, qpc_filetime_offset=qpc_offset
    )
    sampler.install(
        "O", os.getpid(), expected_image=supervisor.STDLIB_PYTHON,
        expected_hash=supervisor.STDLIB_PYTHON_SHA256,
    )
    sampler.start()
    environment = {
        name: value for name, value in os.environ.items()
        if name.upper() in {"SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP"}
    }
    environment.update({
        "M245_QPC_CLOCK_ID": clock_id,
        "M245_QPC_FILETIME_OFFSET": str(qpc_offset),
        "M245_QPC_FREQUENCY": str(qpc_frequency),
        "M245_O_PID": str(os.getpid()),
    })
    environment_sha = _sha256_bytes(_canonical_json_bytes(environment))
    runner_path = str((HERE / "run_m245_scientific_shard.py").resolve())
    s_argv = [
        supervisor.STDLIB_PYTHON, "-I", "-B", "-S", "-u", runner_path,
        "--shard-id", str(shard_id), "--invocation-index", str(invocation_index),
    ]
    spawn_tick = max(time.perf_counter_ns(), sampler._samples[-1]["qpc_tick"] + 1)
    process = subprocess.Popen(
        s_argv, cwd=supervisor.AUTHORITY_CWD, env=environment,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=False, bufsize=0,
    )
    sampler.install(
        "S", process.pid, expected_image=supervisor.STDLIB_PYTHON,
        expected_hash=supervisor.STDLIB_PYTHON_SHA256,
    )
    if sampler.process_record("S")["parent_pid"] != os.getpid():
        process.kill()
        _fail("outer retained S parent identity drift")
    try:
        stdout_raw, stderr_raw = process.communicate(timeout=5400)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        _fail("outer invocation watchdog cap was reached")
    s_exit_tick = max(time.perf_counter_ns(), spawn_tick + 1)
    if (
        process.returncode != 0
        or stderr_raw
        or stdout_raw not in (
            b"M245_S_PROVISIONAL_RECEIPT_PUBLISHED\r\n",
            b"M245_S_PROVISIONAL_RECEIPT_PUBLISHED\n",
        )
    ):
        _fail("S did not exit cleanly after its exact provisional publication record")
    sampler.force()
    result, result_raw, result_identity = _read_canonical(
        shard_root / namespace["result"], "production result"
    )
    checkpoint, checkpoint_raw, checkpoint_identity = _read_canonical(
        shard_root / namespace["checkpoint"], "production checkpoint"
    )
    inner_meter, meter_raw, meter_identity = _read_canonical(
        shard_root / namespace["meter"], "production inner meter"
    )
    receipt, receipt_raw, receipt_identity = _read_canonical(
        shard_root / namespace["invocation_receipt"], "production provisional receipt"
    )
    supervisor.validate_event_result(result, expected_event_id=event_id)
    _validate_checkpoint(checkpoint, event_id)
    supervisor.validate_invocation_receipt(receipt, inner_meter, result)
    for kind, raw, identity in (
        ("result", result_raw, result_identity),
        ("checkpoint", checkpoint_raw, checkpoint_identity),
        ("meter", meter_raw, meter_identity),
    ):
        publication = receipt[f"{kind}_publication"]
        if (
            publication["bytes"] != len(raw) or publication["sha256"] != _sha256_bytes(raw)
            or (publication["device"], publication["inode"]) != (identity.st_dev, identity.st_ino)
        ):
            _fail(f"outer reopen found {kind} publication identity drift")
    prior_witness = None
    prior_witness_raw = None
    prior_witness_identity = None
    final_payload = None
    final_publication = None
    final_tick = None
    if invocation_index == 2:
        prior_namespace = supervisor.shard_namespace(shard_id, 1)
        prior_witness, prior_witness_raw, prior_witness_identity = _read_canonical(
            shard_root / prior_namespace["terminal_witness"], "prior terminal witness"
        )
        final_payload = build_final_shard_receipt_from_files(shard_root, shard_id)
        final_publication = publish_immutable_json(
            shard_root / namespace["final_shard_receipt_temp"],
            shard_root / namespace["final_shard_receipt"], final_payload,
            publication_path=str(
                (shard_root / namespace["final_shard_receipt"]).resolve()
            ),
        )
        final_tick = max(time.perf_counter_ns(), s_exit_tick + 1)
    # E2.7/E1.6 close boundary: sampler.finish freezes the outer raw stream.
    # From here on only canonical serialization (including the prescribed
    # terminal-witness reductions), hashing, hard-link publication, reopen
    # verification, cleanup, and exit are legal; the raw rows are immutable
    # and downstream validators re-derive every gate from the published bytes.
    samples = sampler.finish(exited_roles=("S",))
    if len(samples) < 2:
        _fail("outer raw stream lacks two retained lifetime samples")
    stream_closed_tick = max(time.perf_counter_ns(), (final_tick or s_exit_tick) + 1)
    terminal_tick = max(time.perf_counter_ns(), stream_closed_tick + 1)
    outer_meter = {
        "artifact": "M245_OUTER_RAW_METER",
        "invocation_index": invocation_index,
        "milestones": {
            "final_shard_publication_verified_qpc_tick": final_tick,
            "s_exit_qpc_tick": s_exit_tick,
            "s_spawn_qpc_tick": spawn_tick,
            "stream_closed_qpc_tick": stream_closed_tick,
        },
        "o_process_creation_filetime": sampler.process_record("O")["creation_filetime"],
        "qpc_clock_id": clock_id,
        "qpc_frequency": qpc_frequency,
        "samples": samples,
        "schema": "m245-outer-raw-meter-v1",
        "terminal_endpoint_filetime": qpc_offset + terminal_tick * 10_000_000 // qpc_frequency,
    }
    launcher_path = str((HERE / "launch_m245_scientific_invocation.py").resolve())
    o_argv = [
        supervisor.STDLIB_PYTHON, "-I", "-B", "-S", "-u", launcher_path,
        "--shard-id", str(shard_id), "--invocation-index", str(invocation_index),
    ]
    identities = {
        "O": sampler.identity(
            "O", argv=o_argv,
            environment_sha256=_sha256_bytes(_canonical_json_bytes(dict(os.environ))),
            job_membership=False, declared_exit_code=0,
        ),
        "S": sampler.identity(
            "S", argv=s_argv, environment_sha256=environment_sha,
            job_membership=False,
        ),
        "L": receipt["process_identities"]["L"],
        "W": receipt["process_identities"]["W"],
    }
    inner_bindings = [
        _actual_inner_binding(
            shard_root / namespace[kind], event_id=event_id,
            invocation_index=invocation_index, file_kind=kind,
        )
        for kind in ("result", "checkpoint", "meter")
    ]
    inner_bindings.append({
        "bytes": len(receipt_raw), "device": receipt_identity.st_dev,
        "event_id": event_id, "file_kind": "provisional_receipt",
        "inode": receipt_identity.st_ino, "invocation_index": invocation_index,
        "path": str((shard_root / namespace["invocation_receipt"]).resolve()),
        "sha256": _sha256_bytes(receipt_raw),
    })
    prior_files = None
    final_binding = None
    if invocation_index == 2:
        assert isinstance(prior_witness, dict) and prior_witness_raw is not None
        assert prior_witness_identity is not None and final_payload is not None
        assert final_publication is not None
        prior_files = list(prior_witness["inner_artifacts"])
        prior_files.append({
            "bytes": len(prior_witness_raw), "device": prior_witness_identity.st_dev,
            "event_id": prior_witness["event_id"], "file_kind": "terminal_witness",
            "inode": prior_witness_identity.st_ino, "invocation_index": 1,
            "path": str((
                shard_root
                / supervisor.shard_namespace(shard_id, 1)["terminal_witness"]
            ).resolve()),
            "sha256": _sha256_bytes(prior_witness_raw), "status": prior_witness["status"],
        })
        final_binding = {
            "bytes": final_publication["bytes"], "device": final_publication["device"],
            "inode": final_publication["inode"],
            "path": str((shard_root / namespace["final_shard_receipt"]).resolve()),
            "sha256": final_publication["sha256"], "status": final_payload["status"],
        }
    witness = {
        "artifact": "M245_OUTER_TERMINAL_INVOCATION_WITNESS",
        "schema": "m245-outer-terminal-invocation-witness-v1",
        "shard_id": shard_id, "invocation_index": invocation_index,
        "event_id": event_id, "authority_sha256": receipt["authority_sha256"],
        "inner_artifacts": inner_bindings, "inner_meter": inner_meter,
        "prior_invocation_files": prior_files, "outer_meter": outer_meter,
        "process_identities": identities, "job_census": receipt["job_census"],
        "s_exit": {
            "exit_code": process.returncode, "handle_retained_through_exit": True,
            "identity": {
                "creation_filetime": identities["S"]["creation_filetime"],
                "pid": identities["S"]["pid"],
            },
        },
        "resource_meter": _terminal_resource_meter(inner_meter, outer_meter),
        "final_shard_receipt": final_binding,
        "firewall": {name: False for name in supervisor.FIREWALL_KEYS},
        "status": "PASS_M245_INVOCATION_BOUND" if invocation_index == 1 else "PASS_M245_SHARD_BOUND",
    }
    publish_immutable_json(
        shard_root / namespace["terminal_witness_temp"],
        shard_root / namespace["terminal_witness"], witness,
        publication_path=str((shard_root / namespace["terminal_witness"]).resolve()),
    )
    print("M245_O_TERMINAL_WITNESS_PUBLISHED", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="M245 fail-closed outer observer")
    parser.add_argument("--shard-id", type=int)
    parser.add_argument("--invocation-index", type=int)
    arguments = parser.parse_args(argv)
    if Path.cwd().resolve() != HERE:
        _fail("outer observer cwd drift")
    if arguments.shard_id not in (0, 1, 2, 3) or arguments.invocation_index not in (1, 2):
        _fail("outer observer requires one canonical shard/invocation pair")
    expected_argv = [
        STDLIB_PYTHON, "-I", "-B", "-S", "-u", str(Path(__file__).resolve()),
        "--shard-id", str(arguments.shard_id),
        "--invocation-index", str(arguments.invocation_index),
    ]
    _require_exact_outer_process_binding(expected_argv)
    trigger, entry, trigger_commit = _independently_verify_trigger()
    return _run_production_outer(
        shard_id=arguments.shard_id,
        invocation_index=arguments.invocation_index,
        trigger=trigger,
        trigger_entry=entry,
        trigger_commit=trigger_commit,
    )


if __name__ == "__main__":
    raise SystemExit(main())
