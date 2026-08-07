"""Structural tests for repaired M145.  No efficacy or truth screen."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from m145_defensive_acg import (
    ACGProposal,
    DIMENSION,
    EPSILON,
    LAMBDA_LOWER,
    LAMBDA_UPPER,
    MAIN_FRAMES,
    PILOT_FRAMES,
    PILOT_LINES,
    RANK,
    TOTAL_FRAMES,
    acg_log_density_ratio_float32,
    centered_main_estimate,
    conditional_haar_row_frame,
    defensive_weight_float32,
    even_energy,
    expand_antipodal_line_weights,
    explicit_seed_tree,
    fit_pilot_acg,
    float32_log_density_envelope,
    frame_coefficients_float32,
    normalize_rows_float32,
    proposal_from_scatter,
    rngs_from_seed_tree,
    sample_defensive_directions_float32,
)
from m145_formal_l1_crosswalk import full_crosswalk


HERE = Path(__file__).resolve().parent


def _unit(rng: np.random.Generator, n: int, d: int) -> np.ndarray:
    return normalize_rows_float32(rng.standard_normal((n, d), dtype=np.float32))


def test_frozen_primary_cell_constants() -> None:
    assert (DIMENSION, PILOT_LINES, RANK, PILOT_FRAMES, MAIN_FRAMES) == (
        256,
        1024,
        16,
        4,
        122,
    )
    assert TOTAL_FRAMES == PILOT_FRAMES + MAIN_FRAMES
    assert EPSILON == np.float32(0.8)


def test_float32_woodbury_density_matches_dense_float64_reference() -> None:
    rng = np.random.default_rng(145201)
    v, _ = np.linalg.qr(rng.standard_normal((7, 3)))
    v = v.astype(np.float32)
    lam = np.array([0.4, 1.2, 1.7], dtype=np.float32)
    p = ACGProposal(v, lam)
    u = _unit(rng, 97, 7)
    sigma = np.eye(7) + v.astype(np.float64) @ np.diag(lam.astype(np.float64) - 1.0) @ v.T.astype(np.float64)
    direct = -0.5 * np.linalg.slogdet(sigma)[1] - 3.5 * np.log(
        np.einsum("bi,ij,bj->b", u.astype(np.float64), np.linalg.inv(sigma), u.astype(np.float64))
    )
    got = acg_log_density_ratio_float32(u, p).astype(np.float64)
    assert np.max(np.abs(got - direct)) < 2.5e-5


def test_density_normalizes_on_deterministic_circle() -> None:
    theta = (2.0 * np.pi * np.arange(300_000) / 300_000.0).astype(np.float32)
    u = np.c_[np.cos(theta), np.sin(theta)].astype(np.float32)
    p = ACGProposal(
        np.array([[1.0], [0.0]], dtype=np.float32),
        np.array([1.7], dtype=np.float32),
    )
    q = np.exp(acg_log_density_ratio_float32(u, p).astype(np.float64))
    assert abs(float(np.mean(q)) - 1.0) < 2e-6


def test_float32_extreme_box_has_no_underflow_and_weight_bound() -> None:
    v = np.eye(DIMENSION, RANK, dtype=np.float32)
    lam = np.full(RANK, LAMBDA_LOWER, dtype=np.float32)
    lam[0] = LAMBDA_UPPER
    p = ACGProposal(v, lam)
    aligned = np.zeros((3, DIMENSION), dtype=np.float32)
    aligned[0, 0] = 1.0
    aligned[1, RANK + 1] = 1.0
    aligned[2, 1] = 1.0
    w = defensive_weight_float32(aligned, p)
    certificate = float32_log_density_envelope()
    assert certificate["strictly_normal_float32"]
    assert certificate["minimum_weight_lower_bound_float32"] > np.finfo(np.float32).tiny
    assert np.all(np.isfinite(w)) and np.all(w > 0.0) and np.all(w <= np.float32(1.25))
    assert float(np.min(w)) >= certificate["minimum_weight_lower_bound_float32"] * 0.99


def test_full_mixture_empirical_weights_are_positive_and_bounded() -> None:
    rng = np.random.default_rng(145202)
    v, _ = np.linalg.qr(rng.standard_normal((19, 5)))
    p = ACGProposal(
        v.astype(np.float32),
        np.array([0.25, 0.6, 1.1, 1.4, 1.75], dtype=np.float32),
    )
    u = _unit(rng, 100_000, 19)
    w = defensive_weight_float32(u, p)
    assert w.dtype == np.float32
    assert int(np.count_nonzero(w == 0.0)) == 0
    assert float(np.max(w)) <= 1.25


def test_generic_pilot_fit_is_pathwise_input_permutation_covariant() -> None:
    rng = np.random.default_rng(145203)
    u = _unit(rng, 96, 11)
    yp = rng.random((96, 13), dtype=np.float32)
    ym = rng.random((96, 13), dtype=np.float32)
    perm = rng.permutation(11)
    a = fit_pilot_acg(u, yp, ym, rank=4)
    b = fit_pilot_acg(u[:, perm], yp, ym, rank=4)
    assert a.fallback_reason == b.fallback_reason
    expected = a.covariance()[np.ix_(perm, perm)]
    assert np.max(np.abs(b.covariance() - expected)) < 2.5e-5


def test_rank_boundary_tie_falls_back_uniform_under_permutation() -> None:
    # rank=3 boundary is the tied pair at value 2.0.
    diag = np.array([0.5, 0.7, 1.0, 2.0, 2.0, 3.0, 4.0], dtype=np.float32)
    s = np.diag(diag)
    perm = np.array([6, 2, 4, 0, 5, 1, 3])
    a = proposal_from_scatter(s, pilot_count=1024, rank=3)
    b = proposal_from_scatter(s[np.ix_(perm, perm)], pilot_count=1024, rank=3)
    assert a.rank == b.rank == 0
    assert a.fallback_reason == b.fallback_reason == "rank_boundary_tie"
    assert np.array_equal(a.covariance(), np.eye(7, dtype=np.float32))
    assert np.array_equal(b.covariance(), np.eye(7, dtype=np.float32))


def test_output_permutation_and_hidden_positive_gauge_float32() -> None:
    rng = np.random.default_rng(145204)
    x = _unit(rng, 31, 5)
    w1 = rng.standard_normal((5, 7), dtype=np.float32)
    w2 = rng.standard_normal((7, 9), dtype=np.float32)
    scale = np.exp(rng.normal(0.0, 0.25, 7)).astype(np.float32)
    perm = rng.permutation(7)

    def net(a: np.ndarray, first: np.ndarray, second: np.ndarray) -> np.ndarray:
        return np.maximum(
            np.float32(0.0),
            np.maximum(np.float32(0.0), a @ first) @ second,
        ).astype(np.float32)

    bp, bm = net(x, w1, w2), net(-x, w1, w2)
    gp = net(x, (w1 * scale)[..., perm], (w2 / scale[:, None])[perm, :])
    gm = net(-x, (w1 * scale)[..., perm], (w2 / scale[:, None])[perm, :])
    assert np.max(np.abs(bp - gp)) < 2e-5
    assert np.max(np.abs(even_energy(bp, bm) - even_energy(gp[:, ::-1], gm[:, ::-1]))) < 2e-5


def test_stored_qr_row_frame_conditioner_has_anchor_and_no_rng() -> None:
    rng = np.random.default_rng(145205)
    q, r = np.linalg.qr(rng.standard_normal((17, 17), dtype=np.float32))
    q *= np.where(np.diag(r) < 0.0, -1.0, 1.0)[None, :]
    anchor = _unit(rng, 1, 17)[0]
    out = conditional_haar_row_frame(q.astype(np.float32), anchor)
    assert np.max(np.abs(out[0] - anchor)) < 2e-6
    assert np.max(np.abs(out @ out.T - np.eye(17, dtype=np.float32))) < 8e-5


def test_seed_tree_is_reproducible_disjoint_and_child_owned() -> None:
    a = explicit_seed_tree(0, 998877)
    b = explicit_seed_tree(0, 998877)
    assert a == b
    children = a["children"]
    assert set(children) == {
        "pilot_qr",
        "main_qr",
        "mixture_labels",
        "uniform_anchors",
        "acg_latents",
    }
    seeds = [record["seed"] for record in children.values()]
    assert len(set(seeds)) == len(seeds)
    rngs_a = rngs_from_seed_tree(a)
    rngs_b = rngs_from_seed_tree(b)
    for name in children:
        xa = rngs_a[name].integers(0, 2**63, size=128, dtype=np.int64)
        xb = rngs_b[name].integers(0, 2**63, size=128, dtype=np.int64)
        assert np.array_equal(xa, xb)
    firsts = [int(rngs_from_seed_tree(a)[name].integers(0, 2**63)) for name in children]
    assert len(set(firsts)) == len(firsts)


def test_same_seed_proposal_sampling_replays_exactly() -> None:
    rng = np.random.default_rng(145206)
    v, _ = np.linalg.qr(rng.standard_normal((13, 4)))
    proposal = ACGProposal(
        v.astype(np.float32), np.array([0.4, 0.9, 1.3, 1.7], dtype=np.float32)
    )
    tree = explicit_seed_tree(9, 81)
    streams1 = rngs_from_seed_tree(tree)
    streams2 = rngs_from_seed_tree(tree)
    args1 = (streams1["mixture_labels"], streams1["uniform_anchors"], streams1["acg_latents"])
    args2 = (streams2["mixture_labels"], streams2["uniform_anchors"], streams2["acg_latents"])
    u1, w1, l1 = sample_defensive_directions_float32(*args1, proposal, 37)
    u2, w2, l2 = sample_defensive_directions_float32(*args2, proposal, 37)
    assert np.array_equal(u1, u2) and np.array_equal(w1, w2) and np.array_equal(l1, l2)


def test_frame_coefficients_equal_centered_estimator_and_own_constant() -> None:
    rng = np.random.default_rng(145207)
    pilot_f = rng.normal(size=(PILOT_FRAMES, 6)).astype(np.float32)
    main_f = rng.normal(size=(MAIN_FRAMES, 6)).astype(np.float32)
    w = rng.uniform(0.6, 1.25, size=MAIN_FRAMES).astype(np.float32)
    pc, mc = frame_coefficients_float32(w)
    via_coeff = (
        np.sum(pc[:, None] * pilot_f, axis=0, dtype=np.float32)
        + np.sum(mc[:, None] * main_f, axis=0, dtype=np.float32)
    ) / np.float32(TOTAL_FRAMES)
    via_formula = centered_main_estimate(
        np.mean(pilot_f, axis=0, dtype=np.float32), main_f, w
    )
    assert np.max(np.abs(via_coeff - via_formula)) < 3e-6
    assert abs(float(np.sum(pc, dtype=np.float32) + np.sum(mc, dtype=np.float32)) - TOTAL_FRAMES) < 2e-4
    line = expand_antipodal_line_weights(pc, mc)
    assert line.shape == (2 * TOTAL_FRAMES * DIMENSION,)
    assert np.array_equal(line[: TOTAL_FRAMES * DIMENSION], line[TOTAL_FRAMES * DIMENSION :])


def test_conditional_importance_identity_on_full_frame_toy() -> None:
    # Structural toy only: no target network or efficacy comparison.
    rng = np.random.default_rng(145208)
    d = 5
    v = np.eye(d, 2, dtype=np.float32)
    proposal = ACGProposal(v, np.array([0.5, 1.7], dtype=np.float32))
    centre = np.array([0.11], dtype=np.float32)
    estimates = []
    for _ in range(2500):
        u, w, _ = sample_defensive_directions_float32(rng, rng, rng, proposal, 1)
        q, r = np.linalg.qr(rng.standard_normal((d, d), dtype=np.float32))
        q *= np.where(np.diag(r) < 0.0, -1.0, 1.0)[None, :]
        frame = conditional_haar_row_frame(q.astype(np.float32), u[0])
        f = np.array([[np.mean(frame[:, 0] ** 4, dtype=np.float32)]], dtype=np.float32)
        estimates.append(centered_main_estimate(centre, f, w)[0])
    truth = 3.0 / (d * (d + 2.0))
    assert abs(float(np.mean(estimates)) - truth) < 0.012


def test_manifest_is_one_cell_and_outcome_locked() -> None:
    manifest = json.loads((HERE / "M145_PREEXECUTION_MANIFEST_20260807.json").read_text())
    assert manifest["status"].startswith("REPAIRED_PREEXECUTION")
    assert manifest["execution_authorized"] is False
    assert manifest["primary_cell"] == {
        "pilot_lines": 1024,
        "rank": 16,
        "pilot_frames": 4,
        "main_frames": 122,
        "epsilon": 0.8,
    }
    assert "cells" not in manifest["proposal"]


def test_formal_l1_crosswalk_is_hash_bound_and_resource_safe() -> None:
    crosswalk = full_crosswalk()
    assert crosswalk["source_verification"]["hash_pass"]
    assert crosswalk["source_verification"]["hook_pass"]
    assert crosswalk["split_winograd"]["total_billed_split_delta"] == 3_325_952
    cost = crosswalk["cost"]
    assert cost["projected_max_effective_compute"] < 258.4e9
    assert cost["memory_crosswalk"]["projected_peak_mib"] < 512.0
    assert cost["adjusted_ratio_if_secondary_raw_ratio_0_75"] < 0.8


def test_locked_native_trace_is_structural_and_weight_safe() -> None:
    trace = json.loads((HERE / "M145_STRUCTURAL_TRACE_20260807.json").read_text())
    assert trace["status"] == "STRUCTURAL_NATIVE_TRACE_ONLY_NO_EFFICACY"
    assert trace["dtype"] == "float32"
    assert trace["billed_flops"] == 357_099_678
    assert trace["restored_frame_max_abs_defect"] < 1e-6
    assert trace["weight_zero_count"] == trace["weight_nonfinite_count"] == 0
    assert 0.0 < trace["weight_min"] <= trace["weight_max"] <= 1.25
