"""Pre-outcome protocol tests; never build a generated response cell."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from run_m143_generated import (  # noqa: E402
    CONFIG,
    FAMILY_CODE,
    MANIFEST,
    authorize,
    canonical_authorization_id,
    canonical_receipt_path,
    child_rng,
    consume_authorization,
    _recompute_development_gates,
    sha256,
    stratified_gate_pass,
    validate_development_result,
)


def _summary(pooled: float, upper: float, trend: bool = True) -> dict:
    return {
        "pooled": pooled,
        "upper90": upper,
        "by_width": {"5": pooled, "6": pooled},
        "no_adverse_width_trend": trend,
    }


def test_primary_and_attribution_thresholds_match_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = manifest["predeclared_gates"]["primary_m143_vs_original_m133"]
    attribution = manifest["predeclared_gates"]["causal_attribution_m143_vs_scale_only"]
    assert CONFIG["gates"]["primary"]["pooled_max"] == primary["pooled_mse_ratio_max"]
    assert CONFIG["gates"]["primary"]["upper90_max"] == primary["one_sided_bootstrap_upper90_strict_max"]
    assert CONFIG["gates"]["attribution"]["pooled_max"] == attribution["pooled_mse_ratio_max"]
    assert CONFIG["gates"]["attribution"]["upper90_max"] == attribution["one_sided_bootstrap_upper90_strict_max"]


def test_stratified_gate_requires_pooled_and_every_family() -> None:
    gate = {"pooled_max": .75, "upper90_max": .90}
    good = _summary(.70, .85)
    by_family = {family: dict(good) for family in FAMILY_CODE}
    assert stratified_gate_pass(good, by_family, gate, protocol_complete=True)
    broken = {family: dict(value) for family, value in by_family.items()}
    broken["iid_he"] = _summary(.76, .85)
    assert not stratified_gate_pass(good, broken, gate, protocol_complete=True)
    assert not stratified_gate_pass(good, by_family, gate, protocol_complete=False)
    assert not stratified_gate_pass(good, {"diagonal": good}, gate, protocol_complete=True)


def test_upper_threshold_is_strict_and_width_trend_binds() -> None:
    gate = {"pooled_max": .90, "upper90_max": 1.00}
    equal_upper = _summary(.80, 1.00)
    family = {name: _summary(.80, .95) for name in FAMILY_CODE}
    assert not stratified_gate_pass(equal_upper, family, gate, protocol_complete=True)
    adverse = _summary(.80, .95, False)
    assert not stratified_gate_pass(adverse, family, gate, protocol_complete=True)


def test_child_streams_are_reproducible_and_method_distinct() -> None:
    first = child_rng(101, 307, 5, 143701, 11, 0, 0, 0xD2A).random(8)
    repeat = child_rng(101, 307, 5, 143701, 11, 0, 0, 0xD2A).random(8)
    different = child_rng(101, 307, 5, 143701, 37, 0, 0, 0xD2A).random(8)
    assert np.array_equal(first, repeat)
    assert not np.array_equal(first, different)


def test_confirmation_is_named_but_manifest_stays_closed() -> None:
    manifest = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
    assert manifest["status"] == "PREDECLARED_NOT_AUTHORIZED_TO_RUN"
    assert manifest["root_reaudit_required_before_any_response_execution"] is True
    assert set(CONFIG["chain"]["families"]) == set(FAMILY_CODE)


def test_manifest_binds_every_execution_artifact() -> None:
    manifest = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
    hashes = manifest["execution_artifact_hashes"]
    assert hashes
    for relative, expected in hashes.items():
        artifact = (HERE / relative).resolve()
        assert artifact.is_file()
        assert sha256(artifact) == expected


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _expect_permission(function) -> None:
    try:
        function()
    except PermissionError:
        return
    raise AssertionError("expected a fail-closed PermissionError")


def _authorization_document(
    *,
    split: str,
    output: Path,
    receipt_root: Path,
    nonce: str,
    extra: dict | None = None,
) -> dict:
    document = {
        "candidate": "M143",
        "split": split,
        f"authorize_{split}": True,
        "manifest_sha256": sha256(MANIFEST),
        "runner_sha256": sha256(HERE / "run_m143_generated.py"),
        "authorized_output_path": str(output.resolve()),
        "authorization_id": canonical_authorization_id(nonce),
        "nonce": nonce,
        "consumption_receipt_path": str(canonical_receipt_path(nonce, receipt_root)),
    }
    if extra:
        document.update(extra)
    return document


def test_authorization_binds_artifacts_split_and_exact_output() -> None:
    with tempfile.TemporaryDirectory(prefix="m143-auth-") as raw:
        root = Path(raw)
        receipt_root = root / "receipts"
        output = (root / "development.json").resolve()
        authorization_path = root / "authorization.json"
        document = _authorization_document(
            split="development",
            output=output,
            receipt_root=receipt_root,
            nonce="nonce-development-0001",
        )
        _write_json(authorization_path, document)
        information = authorize(
            "development", authorization_path, output, receipt_root=receipt_root
        )
        assert information["authorized_output_path"] == str(output)
        _expect_permission(
            lambda: authorize(
                "development", authorization_path, root / "different.json",
                receipt_root=receipt_root,
            )
        )
        for field, replacement in (
            ("manifest_sha256", "0" * 64),
            ("runner_sha256", "1" * 64),
            ("split", "confirmation"),
            ("authorization_id", "authorization-id-not-bound"),
        ):
            stale = dict(document)
            stale[field] = replacement
            _write_json(authorization_path, stale)
            _expect_permission(
                lambda: authorize(
                    "development", authorization_path, output, receipt_root=receipt_root
                )
            )


def test_atomic_nonce_receipt_survives_output_delete_and_path_change() -> None:
    with tempfile.TemporaryDirectory(prefix="m143-once-") as raw:
        root = Path(raw)
        receipt_root = root / "receipts"
        output = (root / "development.json").resolve()
        authorization_path = root / "authorization.json"
        nonce = "nonce-one-shot-000001"
        document = _authorization_document(
            split="development",
            output=output,
            receipt_root=receipt_root,
            nonce=nonce,
        )
        _write_json(authorization_path, document)
        information = authorize(
            "development", authorization_path, output, receipt_root=receipt_root
        )
        receipt_hash = consume_authorization(information, receipt_root=receipt_root)
        receipt = canonical_receipt_path(nonce, receipt_root)
        assert receipt.is_file() and sha256(receipt) == receipt_hash
        output.write_text("temporary", encoding="utf-8")
        output.unlink()
        _expect_permission(lambda: consume_authorization(information, receipt_root=receipt_root))

        changed_output = (root / "changed.json").resolve()
        changed_authorization = root / "changed-authorization.json"
        changed = _authorization_document(
            split="development",
            output=changed_output,
            receipt_root=receipt_root,
            nonce=nonce,
        )
        _write_json(changed_authorization, changed)
        changed_information = authorize(
            "development", changed_authorization, changed_output, receipt_root=receipt_root
        )
        _expect_permission(
            lambda: consume_authorization(changed_information, receipt_root=receipt_root)
        )


def _complete_passing_development_fixture(root: Path, receipt_root: Path):
    output = (root / "development-result.json").resolve()
    authorization_path = root / "development-authorization.json"
    authorization_document = _authorization_document(
        split="development",
        output=output,
        receipt_root=receipt_root,
        nonce="nonce-development-fixture",
    )
    _write_json(authorization_path, authorization_document)
    information = authorize(
        "development", authorization_path, output, receipt_root=receipt_root
    )
    receipt_hash = consume_authorization(information, receipt_root=receipt_root)
    records = []
    cells = []
    widths = []
    families = []
    values = {"m133": [], "scale_only": [], "m143": []}
    specification = CONFIG["splits"]["development"]
    repetitions = CONFIG["sampling"]["repetitions"]
    for family in FAMILY_CODE:
        for width in specification["widths"]:
            for cell_seed in specification["seeds"]:
                cells.append(
                    {
                        "family": family,
                        "width": width,
                        "cell_seed": cell_seed,
                        "q_snapshot_sha256_by_layer": [
                            {method: "a" * 64 for method in ("m133", "scale_only", "m143")}
                            for _ in range(CONFIG["chain"]["depth"])
                        ],
                        "mean_mse": {"m133": 1.0, "scale_only": .8, "m143": .5},
                    }
                )
                for repetition in range(repetitions):
                    records.append(
                        {
                            "family": family,
                            "width": width,
                            "cell_seed": cell_seed,
                            "repetition": repetition,
                            "mse_m133": 1.0,
                            "mse_scale_only": .8,
                            "mse_m143": .5,
                        }
                    )
                    widths.append(width)
                    families.append(family)
                    values["m133"].append(1.0)
                    values["scale_only"].append(.8)
                    values["m143"].append(.5)
    recomputed = _recompute_development_gates(
        {method: np.asarray(value) for method, value in values.items()},
        np.asarray(widths),
        np.asarray(families),
    )
    result = {
        "candidate": "M143",
        "split": "development",
        "manifest_sha256": sha256(MANIFEST),
        "runner_sha256": sha256(HERE / "run_m143_generated.py"),
        "config": CONFIG,
        "authorization_provenance": {
            "authorization_file_path": str(authorization_path.resolve()),
            "authorization_file_sha256": sha256(authorization_path),
            "authorization_id": information["authorization_id"],
            "nonce": information["nonce"],
            "split": "development",
            "authorized_output_path": str(output),
            "consumption_receipt_path": information["consumption_receipt_path"],
            "consumption_receipt_sha256": receipt_hash,
        },
        "protocol_failures": [],
        "cells": cells,
        "records": records,
        **recomputed,
    }
    _write_json(output, result)
    binding = {
        "development_result_path": str(output),
        "development_result_sha256": sha256(output),
        "development_authorization_path": str(authorization_path.resolve()),
        "development_authorization_sha256": sha256(authorization_path),
    }
    return output, authorization_path, result, binding


def test_confirmation_recomputes_complete_records_not_asserted_booleans() -> None:
    with tempfile.TemporaryDirectory(prefix="m143-confirm-") as raw:
        root = Path(raw)
        receipt_root = root / "receipts"
        output, _development_auth, passing, binding = _complete_passing_development_fixture(
            root, receipt_root
        )
        validated = validate_development_result(binding, receipt_root=receipt_root)
        assert validated["recomputed"]["gate"]["confirmation_eligible"] is True

        forged = json.loads(json.dumps(passing))
        for record in forged["records"]:
            record["mse_m143"] = 2.0
        forged["gate"] = {
            "primary_pass": True,
            "attribution_pass": True,
            "confirmation_eligible": True,
        }
        _write_json(output, forged)
        forged_binding = dict(binding)
        forged_binding["development_result_sha256"] = sha256(output)
        _expect_permission(
            lambda: validate_development_result(forged_binding, receipt_root=receipt_root)
        )
        confirmation_output = (root / "forged-confirmation.json").resolve()
        confirmation_authorization = root / "forged-confirmation-authorization.json"
        forged_confirmation = _authorization_document(
            split="confirmation",
            output=confirmation_output,
            receipt_root=receipt_root,
            nonce="nonce-forged-confirmation",
            extra=forged_binding,
        )
        _write_json(confirmation_authorization, forged_confirmation)
        _expect_permission(
            lambda: authorize(
                "confirmation",
                confirmation_authorization,
                confirmation_output,
                receipt_root=receipt_root,
            )
        )

        missing = json.loads(json.dumps(passing))
        missing["records"] = missing["records"][1:]
        _write_json(output, missing)
        missing_binding = dict(binding)
        missing_binding["development_result_sha256"] = sha256(output)
        _expect_permission(
            lambda: validate_development_result(missing_binding, receipt_root=receipt_root)
        )


def test_confirmation_rejects_stale_or_forged_result_identity() -> None:
    with tempfile.TemporaryDirectory(prefix="m143-stale-") as raw:
        root = Path(raw)
        receipt_root = root / "receipts"
        output, _development_auth, passing, binding = _complete_passing_development_fixture(
            root, receipt_root
        )
        mutations = (
            ("candidate", "FORGED"),
            ("manifest_sha256", "0" * 64),
            ("runner_sha256", "1" * 64),
            ("config", {"forged": True}),
            ("protocol_failures", [{"failure": "forged"}]),
        )
        for field, value in mutations:
            stale = json.loads(json.dumps(passing))
            stale[field] = value
            _write_json(output, stale)
            stale_binding = dict(binding)
            stale_binding["development_result_sha256"] = sha256(output)
            _expect_permission(
                lambda: validate_development_result(stale_binding, receipt_root=receipt_root)
            )

        _write_json(output, passing)
        receipt = Path(passing["authorization_provenance"]["consumption_receipt_path"])
        receipt.write_text('{"status":"forged"}', encoding="utf-8")
        forged_receipt_binding = dict(binding)
        forged_receipt_binding["development_result_sha256"] = sha256(output)
        _expect_permission(
            lambda: validate_development_result(
                forged_receipt_binding, receipt_root=receipt_root
            )
        )


def test_confirmation_authorization_binds_exact_development_and_output() -> None:
    with tempfile.TemporaryDirectory(prefix="m143-confirm-auth-") as raw:
        root = Path(raw)
        receipt_root = root / "receipts"
        _output, _development_auth, _passing, binding = _complete_passing_development_fixture(
            root, receipt_root
        )
        confirmation_output = (root / "confirmation-result.json").resolve()
        confirmation_authorization = root / "confirmation-authorization.json"
        document = _authorization_document(
            split="confirmation",
            output=confirmation_output,
            receipt_root=receipt_root,
            nonce="nonce-confirmation-0001",
            extra=binding,
        )
        _write_json(confirmation_authorization, document)
        information = authorize(
            "confirmation",
            confirmation_authorization,
            confirmation_output,
            receipt_root=receipt_root,
        )
        assert information["validated_development"]["recomputed"]["gate"][
            "confirmation_eligible"
        ] is True
        _expect_permission(
            lambda: authorize(
                "confirmation",
                confirmation_authorization,
                root / "different-confirmation.json",
                receipt_root=receipt_root,
            )
        )
