"""M145 repaired pre-execution core: defensive ACG frame transport.

The primary protocol is frozen at d=256, P=1024 pilot lines (four complete
Haar frames), rank r=16, and M=122 main frames.  This module contains only
generated-array algebra and deterministic protocol helpers.  It does not run
an efficacy experiment or read competition instances.

The proposal construction is a spectral matrix function of the all-output
pilot scatter.  Unlike the superseded coordinate-started block power method,
it is pathwise covariant under input permutations whenever the rank boundary
is separated.  An explicit boundary-tie gate returns the uniform proposal.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Tuple

import numpy as np


DIMENSION = 256
TOTAL_FRAMES = 126
PILOT_LINES = 1024
PILOT_FRAMES = 4
MAIN_FRAMES = 122
RANK = 16
EPSILON = np.float32(0.80)
LAMBDA_LOWER = np.float32(0.25)
# 1.75 is not an efficacy-tuned value.  It is the largest simple cap used by
# the protocol whose worst-case full-mixture weight stays normal in float32
# even when one selected eigenvalue is maximal and the other 15 are minimal.
LAMBDA_UPPER = np.float32(1.75)
TIE_ULPS = 128.0
PROTOCOL_TAG = 0x4D313435  # ASCII-ish "M145", frozen seed-tree namespace.


@dataclass(frozen=True)
class ACGProposal:
    """Low-rank ACG covariance ``I + V diag(lambda-1) V.T``."""

    v: np.ndarray
    lambdas: np.ndarray
    epsilon: np.float32 = EPSILON
    fallback_reason: str | None = None

    def __post_init__(self) -> None:
        v = np.asarray(self.v)
        lam = np.asarray(self.lambdas)
        if v.dtype != np.float32 or lam.dtype != np.float32:
            raise TypeError("deployed proposal arrays must be float32")
        if v.ndim != 2 or lam.ndim != 1 or v.shape[1] != lam.size:
            raise ValueError("incompatible proposal shapes")
        if not (0.0 < float(self.epsilon) <= 1.0):
            raise ValueError("epsilon must lie in (0,1]")
        if np.any(~np.isfinite(lam)) or np.any(lam <= 0.0):
            raise ValueError("ACG eigenvalues must be finite and positive")
        if v.size:
            defect = np.max(np.abs(v.T @ v - np.eye(v.shape[1], dtype=np.float32)))
            if float(defect) > 2.5e-5:
                raise ValueError(f"V is not float32-orthonormal: defect={defect}")

    @property
    def dimension(self) -> int:
        return int(self.v.shape[0])

    @property
    def rank(self) -> int:
        return int(self.lambdas.size)

    def covariance(self) -> np.ndarray:
        eye = np.eye(self.dimension, dtype=np.float32)
        if self.rank == 0:
            return eye
        return eye + (self.v * (self.lambdas - np.float32(1.0))[None, :]) @ self.v.T


def uniform_proposal(dimension: int, reason: str) -> ACGProposal:
    return ACGProposal(
        np.zeros((int(dimension), 0), dtype=np.float32),
        np.zeros(0, dtype=np.float32),
        EPSILON,
        reason,
    )


def normalize_rows_float32(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.ndim != 2:
        raise ValueError("directions must be a matrix")
    norms = np.sqrt(np.sum(x * x, axis=1, dtype=np.float32), dtype=np.float32)
    if np.any(~np.isfinite(norms)) or np.any(norms == 0.0):
        raise ValueError("directions must be finite and nonzero")
    return x / norms[:, None]


def even_energy(y_plus: np.ndarray, y_minus: np.ndarray) -> np.ndarray:
    """All-output even energy, computed end-to-end in float32."""

    yp = np.asarray(y_plus, dtype=np.float32)
    ym = np.asarray(y_minus, dtype=np.float32)
    if yp.shape != ym.shape or yp.ndim != 2 or yp.shape[1] == 0:
        raise ValueError("plus/minus outputs must be matching nonempty matrices")
    e = np.float32(0.5) * (yp + ym)
    return np.mean(e * e, axis=1, dtype=np.float32)


def proposal_from_scatter(
    scatter: np.ndarray,
    *,
    pilot_count: int,
    rank: int = RANK,
    epsilon: np.float32 = EPSILON,
    tie_ulps: float = TIE_ULPS,
) -> ACGProposal:
    """Apply the frozen permutation-covariant spectral proposal law.

    ``scatter`` is symmetrized in float32, then fully diagonalized.  The
    selected covariance is a spectral matrix function, so eigenvector signs
    and rotations within fully retained tied eigenspaces cancel.  If the
    r/(r+1) boundary is tied within ``128*eps32`` relative scale, selecting
    only part of that eigenspace would not be covariant; the protocol therefore
    returns the uniform proposal before any outcome is observed.
    """

    s = np.asarray(scatter, dtype=np.float32)
    if s.ndim != 2 or s.shape[0] != s.shape[1]:
        raise ValueError("scatter must be square")
    d = int(s.shape[0])
    if not (0 < rank < d) or pilot_count <= 0:
        raise ValueError("frozen spectral proposal needs 0 < rank < d and pilot")
    s = np.float32(0.5) * (s + s.T)
    evals, evecs = np.linalg.eigh(s)
    evals = np.asarray(evals, dtype=np.float32)
    evecs = np.asarray(evecs, dtype=np.float32)
    if np.any(~np.isfinite(evals)) or np.any(~np.isfinite(evecs)):
        return uniform_proposal(d, "nonfinite_eigensolve")
    lower = float(evals[d - rank - 1])
    upper = float(evals[d - rank])
    scale = max(1.0, abs(lower), abs(upper))
    tolerance = tie_ulps * float(np.finfo(np.float32).eps) * scale
    if upper - lower <= tolerance:
        return uniform_proposal(d, "rank_boundary_tie")
    v = np.array(evecs[:, d - rank :], dtype=np.float32, copy=True)
    mu = np.array(evals[d - rank :], dtype=np.float32, copy=True)
    shrink = np.float32(pilot_count / float(pilot_count + d))
    lam = np.float32(1.0) + shrink * (mu - np.float32(1.0))
    lam = np.clip(lam, LAMBDA_LOWER, LAMBDA_UPPER).astype(np.float32, copy=False)
    return ACGProposal(v, lam, np.float32(epsilon), None)


def fit_pilot_acg(
    pilot_u: np.ndarray,
    y_plus: np.ndarray,
    y_minus: np.ndarray,
    rank: int = RANK,
    *,
    epsilon: np.float32 = EPSILON,
) -> ACGProposal:
    """Fit the frozen proposal from pilot directions and all-output energy."""

    u = normalize_rows_float32(pilot_u)
    p, d = u.shape
    if p == 0:
        raise ValueError("M145 primary cell requires a nonempty pilot")
    h = even_energy(y_plus, y_minus)
    if h.shape != (p,):
        raise ValueError("one pilot energy is required per line")
    total = np.sum(h, dtype=np.float32)
    if not np.isfinite(total) or float(total) <= 0.0:
        return uniform_proposal(d, "zero_pilot_energy")
    a = h / total
    weighted = u * a[:, None]
    scatter = np.float32(d) * (u.T @ weighted)
    return proposal_from_scatter(
        scatter, pilot_count=p, rank=rank, epsilon=np.float32(epsilon)
    )


def acg_log_density_ratio_float32(
    u: np.ndarray, proposal: ACGProposal
) -> np.ndarray:
    """Stable float32 log ACG density relative to uniform."""

    x = np.asarray(u, dtype=np.float32)
    one = x.ndim == 1
    if one:
        x = x[None, :]
    x = normalize_rows_float32(x)
    if x.shape[1] != proposal.dimension:
        raise ValueError("direction/proposal dimension mismatch")
    if proposal.rank == 0:
        out = np.zeros(x.shape[0], dtype=np.float32)
    else:
        z = x @ proposal.v
        coeff = np.float32(1.0) - np.float32(1.0) / proposal.lambdas
        invquad = np.float32(1.0) - np.sum(
            (z * z) * coeff[None, :], axis=1, dtype=np.float32
        )
        if np.any(~np.isfinite(invquad)) or np.any(invquad <= 0.0):
            raise FloatingPointError("nonpositive ACG quadratic form")
        logdet = np.sum(np.log(proposal.lambdas), dtype=np.float32)
        out = (
            np.float32(-0.5) * logdet
            - np.float32(0.5 * proposal.dimension) * np.log(invquad)
        ).astype(np.float32, copy=False)
    return out[0] if one else out


def defensive_log_weight_float32(
    u: np.ndarray, proposal: ACGProposal
) -> np.ndarray:
    """Return ``log(1/q)`` without ever materializing the ACG density."""

    loga = acg_log_density_ratio_float32(u, proposal)
    eps = np.float32(proposal.epsilon)
    if eps == np.float32(1.0):
        return np.zeros_like(loga, dtype=np.float32)
    log_eps = np.log(eps).astype(np.float32)
    log_tail = np.log(np.float32(1.0) - eps).astype(np.float32)
    logq = np.logaddexp(log_eps, log_tail + loga).astype(np.float32)
    # Rounding cannot be allowed to put q below its defensive component.
    logq = np.maximum(logq, log_eps).astype(np.float32, copy=False)
    return (-logq).astype(np.float32, copy=False)


def defensive_weight_float32(u: np.ndarray, proposal: ACGProposal) -> np.ndarray:
    """Stable positive full-mixture weight, bounded by float32(1.25)."""

    logw = defensive_log_weight_float32(u, proposal)
    w = np.exp(logw).astype(np.float32)
    cap = np.float32(1.0) / np.float32(proposal.epsilon)
    w = np.minimum(w, cap).astype(np.float32, copy=False)
    if np.any(~np.isfinite(w)) or np.any(w <= 0.0) or np.any(w > cap):
        raise FloatingPointError("defensive weight lost its float32 certificate")
    return w


def float32_log_density_envelope(
    dimension: int = DIMENSION,
    rank: int = RANK,
    lambda_lower: float = float(LAMBDA_LOWER),
    lambda_upper: float = float(LAMBDA_UPPER),
    epsilon: float = float(EPSILON),
) -> dict:
    """Closed worst-case no-underflow certificate for the frozen box."""

    # invquad >= 1/lambda_upper.  The determinant is smallest when the
    # direction uses one upper eigenvalue and the other r-1 are lower.
    loga_max = 0.5 * (
        (dimension - 1) * log(lambda_upper)
        - (rank - 1) * log(lambda_lower)
    )
    logq_max = float(np.logaddexp(log(epsilon), log(1.0 - epsilon) + loga_max))
    log_tiny = log(float(np.finfo(np.float32).tiny))
    min_weight_bound = np.exp(np.float32(-logq_max), dtype=np.float32)
    return {
        "log_acg_density_upper": loga_max,
        "log_full_mixture_density_upper": logq_max,
        "float32_log_tiny": log_tiny,
        "minimum_weight_lower_bound_float32": float(min_weight_bound),
        "strictly_normal_float32": bool(-logq_max > log_tiny),
        "maximum_weight": 1.0 / epsilon,
    }


def sample_acg_float32(
    rng: np.random.Generator, proposal: ACGProposal, count: int = 1
) -> np.ndarray:
    z = rng.standard_normal((int(count), proposal.dimension), dtype=np.float32)
    if proposal.rank:
        coeff = np.sqrt(proposal.lambdas, dtype=np.float32) - np.float32(1.0)
        z = z + (z @ proposal.v * coeff[None, :]) @ proposal.v.T
    return normalize_rows_float32(z)


def sample_defensive_directions_float32(
    component_rng: np.random.Generator,
    uniform_rng: np.random.Generator,
    acg_rng: np.random.Generator,
    proposal: ACGProposal,
    count: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    labels = component_rng.random(int(count), dtype=np.float32) >= proposal.epsilon
    uniform = normalize_rows_float32(
        uniform_rng.standard_normal((int(count), proposal.dimension), dtype=np.float32)
    )
    acg = sample_acg_float32(acg_rng, proposal, int(count))
    out = np.where(labels[:, None], acg, uniform).astype(np.float32)
    weights = defensive_weight_float32(out, proposal)
    return out, weights, labels


def conditional_haar_row_frame(
    provisional_q: np.ndarray, anchor: np.ndarray
) -> np.ndarray:
    """Map the first *row* of a stored Haar frame to an ACG anchor.

    Formal L1 flattens QR matrices by rows.  Right multiplication by the
    symmetric Householder reflector maps row zero to ``anchor`` and keeps the
    remaining rows conditionally Haar in its orthogonal complement.  No QR or
    RNG call occurs here; the provisional frame must be built in setup.
    """

    q = np.array(provisional_q, dtype=np.float32, copy=True)
    a = normalize_rows_float32(np.asarray(anchor, dtype=np.float32)[None, :])[0]
    if q.ndim != 2 or q.shape[0] != q.shape[1] or q.shape[1] != a.size:
        raise ValueError("frame and anchor dimensions disagree")
    v = q[0, :] - a
    vv = np.sum(v * v, dtype=np.float32)
    if float(vv) > 1e-12:
        q -= ((q @ v) * (np.float32(2.0) / vv))[:, None] * v[None, :]
    q[0, :] = a
    defect = np.max(np.abs(q @ q.T - np.eye(q.shape[0], dtype=np.float32)))
    if float(defect) > 8e-5:
        raise FloatingPointError(f"conditional row frame defect={defect}")
    return q


def conditional_radius_scaled_row_frame(
    provisional_frame: np.ndarray,
    anchor: np.ndarray,
    radius: float,
) -> np.ndarray:
    """Condition the exact radius-scaled Formal row-frame law.

    ``provisional_frame`` is ``radius * Q`` using the unmodified QR output.
    The right Householder target is therefore ``radius * anchor``.  The
    routine intentionally does not sign-normalize QR columns: the caller's
    provisional law is preserved exactly.
    """

    frame = np.array(provisional_frame, dtype=np.float32, copy=True)
    if frame.ndim != 2 or frame.shape[0] != frame.shape[1]:
        raise ValueError("provisional frame must be square")
    radius32 = np.float32(radius)
    if not np.isfinite(radius32) or float(radius32) <= 0.0:
        raise ValueError("radius must be finite and positive")
    a = normalize_rows_float32(np.asarray(anchor, dtype=np.float32)[None, :])[0]
    if a.size != frame.shape[1]:
        raise ValueError("frame and anchor dimensions disagree")
    v = frame[0, :] - radius32 * a
    vv = np.sum(v * v, dtype=np.float32)
    if float(vv) > 1e-12:
        frame -= ((frame @ v) * (np.float32(2.0) / vv))[:, None] * v[None, :]
    directional = normalize_rows_float32(frame[0:1])[0]
    if float(np.max(np.abs(directional - a))) > 8e-5:
        raise FloatingPointError("radius-scaled reflector missed its anchor")
    gram = frame @ frame.T
    target = np.float32(radius32 * radius32) * np.eye(frame.shape[0], dtype=np.float32)
    relative_defect = np.max(np.abs(gram - target)) / max(float(radius32 * radius32), 1.0)
    if float(relative_defect) > 8e-5:
        raise FloatingPointError(
            f"conditional radius-scaled row frame defect={relative_defect}"
        )
    return frame


def frame_coefficients_float32(
    main_weights: np.ndarray,
    *,
    total_frames: int = TOTAL_FRAMES,
    pilot_frames: int = PILOT_FRAMES,
) -> Tuple[np.ndarray, np.ndarray]:
    """Per-frame coefficients implementing ``C+mean w(F-C)``.

    When a final computation takes the ordinary mean over all 126 frames,
    pilot frames receive ``T/P*(1-mean(w))`` and main frames receive
    ``T/M*w``.  The coefficients sum to T in float32 up to reduction rounding,
    so constant analytic pieces remain exactly owned.
    """

    w = np.asarray(main_weights, dtype=np.float32)
    main_frames = total_frames - pilot_frames
    if w.shape != (main_frames,):
        raise ValueError("one weight per main frame is required")
    wbar = np.mean(w, dtype=np.float32)
    pilot = np.full(
        pilot_frames,
        np.float32(total_frames / pilot_frames) * (np.float32(1.0) - wbar),
        dtype=np.float32,
    )
    main = np.float32(total_frames / main_frames) * w
    return pilot, main.astype(np.float32, copy=False)


def expand_antipodal_line_weights(
    pilot_coefficients: np.ndarray,
    main_coefficients: np.ndarray,
    width: int = DIMENSION,
) -> np.ndarray:
    frame = np.concatenate((pilot_coefficients, main_coefficients)).astype(np.float32)
    line = np.repeat(frame, int(width)).astype(np.float32)
    return np.concatenate((line, line)).astype(np.float32)


def centered_main_estimate(
    pilot_frame_mean: np.ndarray,
    main_frame_means: np.ndarray,
    main_weights: np.ndarray,
) -> np.ndarray:
    c = np.asarray(pilot_frame_mean, dtype=np.float32)
    f = np.asarray(main_frame_means, dtype=np.float32)
    w = np.asarray(main_weights, dtype=np.float32)
    if f.shape[0] != w.size or f.shape[1:] != c.shape or w.size == 0:
        raise ValueError("centre/main/weight shapes disagree")
    shape = (w.size,) + (1,) * c.ndim
    return (c + np.mean(w.reshape(shape) * (f - c), axis=0, dtype=np.float32)).astype(
        np.float32
    )


def _seed_from_child(child: np.random.SeedSequence) -> int:
    return int(child.generate_state(1, dtype=np.uint64)[0])


def explicit_seed_tree(setup_seed: int, mlp_seed: int) -> dict:
    """Return disjoint setup/predict child seeds and their provenance."""

    setup_root = np.random.SeedSequence([PROTOCOL_TAG, int(setup_seed), 0])
    pilot_qr, main_qr = setup_root.spawn(2)
    predict_root = np.random.SeedSequence(
        [PROTOCOL_TAG, int(setup_seed), int(mlp_seed), 1]
    )
    mixture, uniform, acg = predict_root.spawn(3)
    return {
        "protocol_tag": PROTOCOL_TAG,
        "setup_seed": int(setup_seed),
        "mlp_seed": int(mlp_seed),
        "children": {
            "pilot_qr": {"seed": _seed_from_child(pilot_qr), "spawn_key": list(pilot_qr.spawn_key)},
            "main_qr": {"seed": _seed_from_child(main_qr), "spawn_key": list(main_qr.spawn_key)},
            "mixture_labels": {"seed": _seed_from_child(mixture), "spawn_key": list(mixture.spawn_key)},
            "uniform_anchors": {"seed": _seed_from_child(uniform), "spawn_key": list(uniform.spawn_key)},
            "acg_latents": {"seed": _seed_from_child(acg), "spawn_key": list(acg.spawn_key)},
        },
    }


def rngs_from_seed_tree(tree: dict) -> dict[str, np.random.Generator]:
    return {
        name: np.random.default_rng(int(record["seed"]))
        for name, record in tree["children"].items()
    }
