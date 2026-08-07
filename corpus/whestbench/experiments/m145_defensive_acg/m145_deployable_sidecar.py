"""FlopScope-compatible M145 sidecar for the frozen P1024/r16/M122 cell.

This is a structural trace kernel, not an efficacy runner.  Its inputs are a
stored Formal-L1 row-frame bank and already-computed pilot surrogate outputs.
It fits the proposal, draws main anchors, applies/restores the Householder
frames in place, and emits the exact per-path coefficients used by the Formal
L1 crosswalk.
"""

from __future__ import annotations

import math

import flopscope.numpy as fnp

from m145_deployable_core import (
    DIMENSION,
    EPSILON,
    LAMBDA_LOWER,
    LAMBDA_UPPER,
    MAIN_FRAMES,
    PILOT_FRAMES,
    PILOT_LINES,
    RANK,
    TIE_ULPS,
)


def _normalize_rows(x):
    norms = fnp.sqrt(fnp.sum(fnp.multiply(x, x), axis=1))
    return fnp.divide(x, norms[:, None])


def fit_proposal_f32(pilot_u, y_plus, y_minus):
    """Billed full-scatter/full-eigh version of the repaired proposal."""

    u = _normalize_rows(pilot_u.astype(fnp.float32))
    even = fnp.multiply(
        fnp.float32(0.5),
        fnp.add(y_plus.astype(fnp.float32), y_minus.astype(fnp.float32)),
    )
    energy = fnp.mean(fnp.multiply(even, even), axis=1).astype(fnp.float32)
    total = fnp.sum(energy).astype(fnp.float32)
    if float(total) <= 0.0 or not math.isfinite(float(total)):
        return (
            fnp.empty((DIMENSION, 0), dtype=fnp.float32),
            fnp.empty((0,), dtype=fnp.float32),
            "zero_pilot_energy",
        )
    probability = fnp.divide(energy, total)
    weighted = fnp.multiply(u, probability[:, None])
    scatter = fnp.multiply(fnp.float32(DIMENSION), fnp.matmul(u.T, weighted))
    scatter = fnp.multiply(fnp.float32(0.5), fnp.add(scatter, scatter.T))
    evals, evecs = fnp.linalg.eigh(scatter)
    lower = float(evals[DIMENSION - RANK - 1])
    upper = float(evals[DIMENSION - RANK])
    tolerance = (
        TIE_ULPS
        # IEEE-754 binary32 machine epsilon, written explicitly to avoid an
        # unsupported host-array/introspection call in the sandbox.
        * 1.1920928955078125e-7
        * max(1.0, abs(lower), abs(upper))
    )
    if upper - lower <= tolerance:
        return (
            fnp.empty((DIMENSION, 0), dtype=fnp.float32),
            fnp.empty((0,), dtype=fnp.float32),
            "rank_boundary_tie",
        )
    v = evecs[:, DIMENSION - RANK :].astype(fnp.float32)
    mu = evals[DIMENSION - RANK :].astype(fnp.float32)
    shrink = fnp.float32(PILOT_LINES / (PILOT_LINES + DIMENSION))
    lam = fnp.clip(
        fnp.add(
            fnp.float32(1.0),
            fnp.multiply(shrink, fnp.subtract(mu, fnp.float32(1.0))),
        ),
        fnp.float32(LAMBDA_LOWER),
        fnp.float32(LAMBDA_UPPER),
    ).astype(fnp.float32)
    return v, lam, None


def _draw_main_anchors(v, lam, seeds: dict[str, int]):
    component_rng = fnp.random.default_rng(int(seeds["mixture_labels"]))
    uniform_rng = fnp.random.default_rng(int(seeds["uniform_anchors"]))
    acg_rng = fnp.random.default_rng(int(seeds["acg_latents"]))
    labels = component_rng.random(MAIN_FRAMES, dtype=fnp.float32) >= fnp.float32(
        EPSILON
    )
    uniform = _normalize_rows(
        uniform_rng.standard_normal(
            (MAIN_FRAMES, DIMENSION), dtype=fnp.float32
        )
    )
    z = acg_rng.standard_normal((MAIN_FRAMES, DIMENSION), dtype=fnp.float32)
    if int(lam.shape[0]):
        coeff = fnp.subtract(fnp.sqrt(lam), fnp.float32(1.0))
        projected = fnp.multiply(fnp.matmul(z, v), coeff[None, :])
        z = fnp.add(z, fnp.matmul(projected, v.T))
    acg = _normalize_rows(z)
    anchors = fnp.where(labels[:, None], acg, uniform).astype(fnp.float32)
    return anchors, labels


def _full_mixture_weights(anchors, v, lam):
    if int(lam.shape[0]) == 0:
        loga = fnp.zeros((MAIN_FRAMES,), dtype=fnp.float32)
    else:
        projected = fnp.matmul(anchors, v)
        coeff = fnp.subtract(
            fnp.float32(1.0), fnp.divide(fnp.float32(1.0), lam)
        )
        projected_sq = fnp.multiply(projected, projected)
        invquad = fnp.subtract(
            fnp.float32(1.0),
            fnp.sum(fnp.multiply(projected_sq, coeff[None, :]), axis=1),
        )
        if bool(fnp.any(~fnp.isfinite(invquad))) or bool(
            fnp.any(invquad <= fnp.float32(0.0))
        ):
            raise FloatingPointError("nonpositive/nonfinite ACG quadratic")
        logdet = fnp.sum(fnp.log(lam))
        loga = fnp.subtract(
            fnp.multiply(fnp.float32(-0.5), logdet),
            fnp.multiply(fnp.float32(0.5 * DIMENSION), fnp.log(invquad)),
        )
    log_eps = fnp.log(fnp.float32(EPSILON))
    log_tail = fnp.log(fnp.float32(1.0) - fnp.float32(EPSILON))
    logq = fnp.logaddexp(log_eps, fnp.add(log_tail, loga))
    logq = fnp.maximum(logq, log_eps)
    weights = fnp.exp(fnp.negative(logq)).astype(fnp.float32)
    weights = fnp.minimum(
        weights, fnp.float32(1.0) / fnp.float32(EPSILON)
    )
    cap = fnp.float32(1.0) / fnp.float32(EPSILON)
    if (
        bool(fnp.any(~fnp.isfinite(weights)))
        or bool(fnp.any(weights <= fnp.float32(0.0)))
        or bool(fnp.any(weights > cap))
    ):
        raise FloatingPointError("defensive weight lost its float32 envelope")
    return weights


def prepare_reflectors(frame_bank, anchors, radius):
    """Freeze radius-scaled setup-frame-to-anchor reflectors.

    Formal L1 stores ``rho_d * Q`` rather than ``Q``.  Right multiplication
    by the Householder built from ``rho_d * (q_0-a)`` maps the stored first
    row to ``rho_d * a`` and is self-inverse.  Passing a unit target here is
    the radial mismatch rejected by the second hostile audit.
    """

    radius32 = fnp.float32(radius)
    if not math.isfinite(float(radius32)) or float(radius32) <= 0.0:
        raise ValueError("radius must be finite and positive")
    targets = fnp.multiply(radius32, anchors)
    vectors = fnp.subtract(frame_bank[PILOT_FRAMES:, 0, :], targets)
    vv = fnp.sum(fnp.multiply(vectors, vectors), axis=1)
    beta = fnp.where(
        vv > fnp.float32(1e-12),
        fnp.divide(fnp.float32(2.0), vv),
        fnp.float32(0.0),
    )
    return vectors.astype(fnp.float32), beta.astype(fnp.float32)


def _householder_in_place(frame, v, beta, qv, outer):
    """Right-reflect one stored Formal-L1 row frame using fixed scratch."""

    if float(beta) != 0.0:
        fnp.matmul(frame, v, out=qv)
        fnp.multiply(qv[:, None], fnp.multiply(beta, v[None, :]), out=outer)
        fnp.subtract(frame, outer, out=frame)


def apply_or_restore_main_frames_in_place(frame_bank, vectors, beta, qv, outer):
    """Householder is self-inverse; calling twice restores the setup bank."""

    for index in range(MAIN_FRAMES):
        _householder_in_place(
            frame_bank[PILOT_FRAMES + index], vectors[index], beta[index], qv, outer
        )


def frame_and_path_coefficients(weights):
    wbar = fnp.mean(weights)
    pilot_fill = float(
        fnp.multiply(
            fnp.float32(126.0 / PILOT_FRAMES),
            fnp.subtract(fnp.float32(1.0), wbar),
        )
    )
    pilot = fnp.full(
        (PILOT_FRAMES,),
        pilot_fill,
        dtype=fnp.float32,
    )
    main = fnp.multiply(fnp.float32(126.0 / MAIN_FRAMES), weights)
    frame = fnp.concatenate((pilot, main), axis=0)
    line = fnp.repeat(frame, DIMENSION)
    path = fnp.concatenate((line, line), axis=0).astype(fnp.float32)
    return frame, path


def structural_sidecar(
    frame_bank,
    y_plus,
    y_minus,
    predict_child_seeds: dict[str, int],
):
    """Run the entire billed sidecar and restore the stored frame bank."""

    pilot_u = frame_bank[:PILOT_FRAMES].reshape((PILOT_LINES, DIMENSION))
    v, lam, fallback = fit_proposal_f32(pilot_u, y_plus, y_minus)
    anchors, labels = _draw_main_anchors(v, lam, predict_child_seeds)
    weights = _full_mixture_weights(anchors, v, lam)
    frame_coeff, path_coeff = frame_and_path_coefficients(weights)
    qv = fnp.empty((DIMENSION,), dtype=fnp.float32)
    outer = fnp.empty((DIMENSION, DIMENSION), dtype=fnp.float32)
    radius = fnp.sqrt(
        fnp.sum(fnp.multiply(frame_bank[0, 0, :], frame_bank[0, 0, :]))
    )
    vectors, beta = prepare_reflectors(frame_bank, anchors, radius)
    apply_or_restore_main_frames_in_place(frame_bank, vectors, beta, qv, outer)
    # A production adapter runs Formal L1 between these calls.  The structural
    # trace restores immediately because it is forbidden to open efficacy.
    apply_or_restore_main_frames_in_place(frame_bank, vectors, beta, qv, outer)
    return {
        "v": v,
        "lambdas": lam,
        "fallback": fallback,
        "anchors": anchors,
        "weights": weights,
        "labels": labels,
        "frame_coefficients": frame_coeff,
        "path_coefficients": path_coeff,
    }
