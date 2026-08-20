"""Structural-only tests for the integrated M145 descendant."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from whestbench import SetupContext

from m145_defensive_acg import (
    EPSILON,
    MAIN_FRAMES,
    PILOT_FRAMES,
    PILOT_LINES,
    RANK,
    conditional_radius_scaled_row_frame,
)
from m145_formal_l1_crosswalk import verify_formal_sources
from m145_integrated_estimator import (
    DIMENSION,
    Estimator,
    MatchedComparator,
    mean_radius,
    raw_qr_radius_bank_numpy,
    setup_child_seeds,
)


HERE = Path(__file__).resolve().parent
_CACHE: dict = {}


def _json(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _target_estimator() -> Estimator:
    if "estimator" not in _CACHE:
        estimator = Estimator()
        estimator.setup(
            SetupContext(
                width=256,
                depth=32,
                flop_budget=10**15,
                api_version="structural-test",
                seed=145_310_001,
            )
        )
        _CACHE["estimator"] = estimator
    return _CACHE["estimator"]


def test_frozen_integrated_cell_unchanged() -> None:
    assert (PILOT_LINES, PILOT_FRAMES, MAIN_FRAMES, RANK) == (1024, 4, 122, 16)
    assert EPSILON == np.float32(0.8)
    assert Estimator.transport_enabled is True
    assert MatchedComparator.transport_enabled is False


def test_reference_generator_uses_raw_formal_qr_signs() -> None:
    width = 8
    pilot_seed, _main_seed = setup_child_seeds(145_310_091)
    rng = np.random.default_rng(pilot_seed)
    raw = rng.standard_normal((2, width, width), dtype=np.float32)
    q, r = np.linalg.qr(raw)
    bank = raw_qr_radius_bank_numpy(
        145_310_091, width=width, pilot_frames=2, main_frames=3
    )
    expected = q.astype(np.float32) * np.float32(mean_radius(width))
    assert np.array_equal(bank[:2], expected)
    signs = np.where(np.diagonal(r, axis1=1, axis2=2) < 0.0, -1.0, 1.0)
    q_sign_normalized = q * signs[:, None, :]
    assert np.any(signs < 0.0)
    assert not np.array_equal(bank[:2], q_sign_normalized.astype(np.float32))


def test_raw_qr_projective_and_conditional_completion_moments() -> None:
    # Direct test of the exact unnormalized np/fnp QR convention.  Only
    # sign-invariant row-line moments are asserted.
    rng = np.random.default_rng(145_310_092)
    d = 8
    raw = rng.standard_normal((4096, d, d), dtype=np.float32)
    q, _r = np.linalg.qr(raw)
    u = q[:, 0, :].astype(np.float64)
    assert np.max(np.abs(np.mean(u * u, axis=0) - 1.0 / d)) < 0.008
    assert abs(float(np.mean(u[:, 0] ** 4)) - 3.0 / (d * (d + 2.0))) < 0.004

    anchor = np.zeros(d, dtype=np.float64)
    anchor[0] = 1.0
    v = u - anchor[None, :]
    beta = 2.0 / np.sum(v * v, axis=1)
    second = q[:, 1, :].astype(np.float64)
    conditional_second = second - (
        np.sum(second * v, axis=1) * beta
    )[:, None] * v
    expected = np.zeros(d)
    expected[1:] = 1.0 / (d - 1.0)
    assert np.max(np.abs(np.mean(conditional_second**2, axis=0) - expected)) < 0.012


def test_actual_target_bank_has_formal_radius_and_bitwise_reference() -> None:
    estimator = _target_estimator()
    observed = np.asarray(estimator.frame_bank)
    reference = raw_qr_radius_bank_numpy(145_310_001)
    assert observed.shape == (126, 256, 256)
    assert observed.dtype == np.float32
    assert np.array_equal(observed, reference)
    norms = np.linalg.norm(observed, axis=2)
    assert np.max(np.abs(norms - mean_radius())) < 3e-6
    assert np.array_equal(
        np.asarray(estimator._provisional_main_copy), observed[PILOT_FRAMES:]
    )


def test_radius_scaled_conditioner_hits_anchor_without_sign_change() -> None:
    rng = np.random.default_rng(145_310_093)
    raw = rng.standard_normal((8, 8), dtype=np.float32)
    q, _r = np.linalg.qr(raw)
    radius = mean_radius(8)
    frame = q.astype(np.float32) * np.float32(radius)
    anchor = rng.standard_normal(8, dtype=np.float32)
    anchor /= np.linalg.norm(anchor)
    conditioned = conditional_radius_scaled_row_frame(frame, anchor, radius)
    direction = conditioned[0] / np.linalg.norm(conditioned[0])
    assert np.max(np.abs(direction - anchor)) < 2e-6
    gram = conditioned @ conditioned.T
    target = np.float32(radius * radius) * np.eye(8, dtype=np.float32)
    assert np.max(np.abs(gram - target)) / (radius * radius) < 2e-6


def test_candidate_and_comparator_share_provisional_bank() -> None:
    candidate = _json("M145_INTEGRATED_STRUCTURAL_TRACE_20260807.json")
    comparator = _json("M145_MATCHED_COMPARATOR_STRUCTURAL_TRACE_20260807.json")
    assert candidate["provisional_reference_bitwise_equal"]
    assert comparator["provisional_reference_bitwise_equal"]
    assert candidate["provisional_bank_sha256"] == comparator["provisional_bank_sha256"]
    assert candidate["seeds"] == comparator["seeds"]


def test_pilot_is_materialized_before_proposal_and_main_transport() -> None:
    trace = _json("M145_INTEGRATED_STRUCTURAL_TRACE_20260807.json")
    first = trace["first_predict"]
    assert first["event_log"] == [
        "pilot_surrogate_materialized",
        "proposal_frozen_from_pilot_only",
        "main_transport_applied_after_proposal",
        "split_formal_path_entered",
        "split_formal_path_complete",
        "main_transport_restored_and_canonicalized",
    ]
    assert first["transport"]["pilot_surrogate_shape"] == [1024, 256]
    assert first["transport"]["rank"] == 16
    stages = [row["stage"] for row in first["dispatch_records"]]
    assert stages[:32] == ["pilot_surrogate:first"] + [
        f"pilot_surrogate:layer{i}" for i in range(2, 33)
    ]
    assert stages[32] == "formal:first:pilot"


def test_target_trace_restores_and_replays_exactly() -> None:
    trace = _json("M145_INTEGRATED_STRUCTURAL_TRACE_20260807.json")
    assert trace["first_predict"]["failure"] is None
    assert trace["second_predict"]["failure"] is None
    assert trace["first_restore_max_abs_defect"] == 0.0
    assert trace["second_restore_max_abs_defect"] == 0.0
    assert trace["repeat_prediction_bitwise_equal"] is True
    assert trace["repeat_prediction_max_abs"] == 0.0
    weights = trace["first_predict"]["transport"]
    assert weights["bad_weight_count"] == 0
    assert 0.0 < weights["weight_min"] <= weights["weight_max"] <= 1.25


def test_target_trace_prices_every_call_and_stays_inside_resources() -> None:
    candidate = _json("M145_INTEGRATED_STRUCTURAL_TRACE_20260807.json")
    comparator = _json("M145_MATCHED_COMPARATOR_STRUCTURAL_TRACE_20260807.json")
    c = candidate["first_predict"]
    b = comparator["first_predict"]
    assert c["flopscope_summary"]["operations"]["matmul"]["calls"] == 1078
    assert b["flopscope_summary"]["operations"]["matmul"]["calls"] == 798
    assert c["billed_flops"] == 184_270_895_262
    assert b["billed_flops"] == 176_455_830_878
    assert candidate["operational_memory_after_first_predict"]["peak_working_set_mib"] < 512.0
    assert comparator["operational_memory_after_first_predict"]["peak_working_set_mib"] < 512.0
    delta = c["effective_compute"] - b["effective_compute"]
    assert 222_405_357_000.0 + delta < 258.4e9


def test_truth_free_formal_parity_binds_all_semantic_hooks() -> None:
    parity = _json("M145_FORMAL_PARITY_20260807.json")
    assert parity["status"] == "TRUTH_FREE_FORMAL_L1_PARITY_ONLY"
    assert parity["both_finite"]
    assert parity["max_abs_difference"] < 2e-5
    assert parity["max_relative_to_output_scale"] < 3e-6
    assert parity["split_event_log"] == [
        "matched_comparator_transport_disabled",
        "split_formal_path_entered",
        "split_formal_path_complete",
    ]
    verification = verify_formal_sources()
    assert verification["hash_pass"] and verification["hook_pass"]


def test_comparator_null_second_predict_is_declared_single_run_not_failure() -> None:
    comparator = _json("M145_MATCHED_COMPARATOR_STRUCTURAL_TRACE_20260807.json")
    assert comparator["kind"] == "comparator"
    assert comparator["first_predict"]["failure"] is None
    assert comparator["second_predict"] is None
    assert comparator["second_restore_max_abs_defect"] is None
    assert comparator["repeat_prediction_bitwise_equal"] is None


def test_sealed_truth_protocol_is_unchanged_and_cross_risk_is_separate() -> None:
    sealed = HERE / "M145_GENERATED_EFFICACY_PROTOCOL_20260807.json"
    assert _sha256(sealed) == (
        "68ea6625322df0870fc5c19f4667597eb883c667d834cdc443f0a924a8977a41"
    )
    cross = _json("M145_CROSS_REFERENCE_RISK_PROTOCOL_20260807.json")
    assert cross["execution_authorized"] is False
    assert cross["outcome_opened"] is False
    assert cross["efficacy_run_count"] == 0
    assert cross["separation_from_existing_protocol"]["sealed_protocol_sha256"] == (
        _sha256(sealed)
    )
    assert cross["reference_replicates"]["pairs_per_network"] == 8
    assert cross["reference_rule"]["antipodal_path_count"] == 64_512


def test_cross_reference_seed_tree_is_exact_unique_and_disjoint() -> None:
    cross = _json("M145_CROSS_REFERENCE_RISK_PROTOCOL_20260807.json")
    canonical = "".join(
        f"{i}|{k}|{145_500_000 + 100*i + k}|{145_600_000 + 100*i + k}\n"
        for i in range(24)
        for k in range(8)
    ).encode("utf-8")
    assert len(canonical) == cross["reference_replicates"]["seed_table_byte_count"]
    assert hashlib.sha256(canonical).hexdigest() == (
        cross["reference_replicates"]["seed_table_sha256"]
    )
    r1 = {145_500_000 + 100 * i + k for i in range(24) for k in range(8)}
    r2 = {145_600_000 + 100 * i + k for i in range(24) for k in range(8)}
    sealed = _json("M145_GENERATED_EFFICACY_PROTOCOL_20260807.json")
    sealed_seeds = {value for row in sealed["seed_table"] for value in row[1:]}
    assert len(r1) == len(r2) == 192
    assert r1.isdisjoint(r2)
    assert (r1 | r2).isdisjoint(sealed_seeds | {145_630_001})


def test_cross_reference_assets_cost_and_unbiasedness_are_bound() -> None:
    cross = _json("M145_CROSS_REFERENCE_RISK_PROTOCOL_20260807.json")
    asset_dir = HERE.parent / "design8_reconstruction"
    for name, expected in cross["reference_assets"].items():
        if not name.endswith((".py", ".npz")):
            continue
        assert _sha256(asset_dir / name) == expected
    compute = cross["compute_feasibility"]
    n, d, depth = 64_512, 256, 32
    dense = depth * (2 * n * d * d - n * d)
    activation = depth * n * d
    assert dense == compute["dense_matmul_bill_per_reference"]
    assert dense + activation == compute["dense_plus_activation_lower_bound_per_reference"]
    assert (dense + activation) * 16 * 24 == (
        compute["dense_plus_activation_lower_bound_all_24_networks"]
    )
    proof = cross["conditional_unbiasedness_proof"]
    assert "e1 dot e2" in proof["expansion"]
    assert "MSE(A|W)-MSE(B|W)" in proof["paired_result"]
    assert "R1 dot R2 term cancels exactly" in (
        cross["variance_identity"]["paired_difference"]
        + cross["cross_risk_statistics"]["algebraic_cancellation"]
    )


def test_cross_reference_zero_outcome_manifest_blocks_execution() -> None:
    manifest = _json("M145_CROSS_REFERENCE_RISK_PREEXECUTION_MANIFEST_20260807.json")
    protocol_path = HERE / "M145_CROSS_REFERENCE_RISK_PROTOCOL_20260807.json"
    derivation_path = HERE / "M145_CROSS_REFERENCE_RISK_DERIVATION_20260807.md"
    assert manifest["execution_authorized"] is False
    assert manifest["reference_evaluator_implemented"] is False
    assert manifest["outcome_opened"] is False
    assert manifest["efficacy_run_count"] == 0
    assert manifest["rank_claim_authorized"] is False
    assert manifest["sealed_inputs"]["cross_reference_protocol"]["sha256"] == (
        _sha256(protocol_path)
    )
    assert manifest["sealed_inputs"]["mathematical_derivation"]["sha256"] == (
        _sha256(derivation_path)
    )
    assert manifest["frozen_experiment"]["negative_estimates"] == (
        "valid finite outcomes; retained without clipping"
    )


def test_integrated_manifest_binds_artifacts_and_remains_zero_outcome() -> None:
    manifest = _json("M145_INTEGRATED_PREEXECUTION_MANIFEST_20260807.json")
    assert manifest["execution_authorized"] is False
    assert manifest["outcome_opened"] is False
    assert manifest["efficacy_run_count"] == 0
    assert manifest["submission_authorized"] is False
    assert manifest["champion_mutation_authorized"] is False
    for name, expected in manifest["bound_integrated_artifacts"].items():
        assert _sha256(HERE / name) == expected
    cross = manifest["recommended_unbiased_cross_reference_protocol"]
    assert cross["sealed_protocol_unchanged"] is True
    assert "reference evaluator not implemented" in cross["status"]
