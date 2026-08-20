"""M143 diagonal path-energy proposal for exact M133 ``[2,1,1]`` sampling.

This is a *proposal-only* child of M133.  It changes neither the five-product
Hansen--Hurwitz estimator nor M131's exact conditional-boundary coefficient.
The new node strength is output aware:

    tau_i^2 = s_i^2 sum_a W[i,a]^2 h_next[a],

where ``h_next`` is the exact diagonal second moment of a Rademacher probe
transported through the *mean-only* Gaussian/ReLU tangent suffix.  Thus it is
not a fitted output model and is not the previously killed full covariance
goal-adjoint.  Its role is only to select a positive proposal distribution;
the uniform-rescue HH estimator remains unbiased for any finite value of
``tau``.

No contest model, scorer, truth, leaderboard, or submission interface is
present here.  The module is intentionally limited to algebra and static cost
accounting.  A generated response experiment has a separate frozen manifest
and must not be run before independent audit.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from typing import Sequence

import numpy as np


Array = np.ndarray
GENERATED_REFERENCE_DTYPE = np.float64
TARGET_PROPOSAL_DTYPE = np.float32

ROOT = Path(__file__).resolve().parents[1]
M133 = ROOT / "m133_ht_hidden_edge"
if str(M133) not in sys.path:
    sys.path.insert(0, str(M133))

from m133_ht_hidden_edge import Factored211Proposal  # noqa: E402


def _finite_vector(name: str, value: Array, length: int, *, nonnegative: bool = False) -> Array:
    answer = np.asarray(value, dtype=np.float64)
    if answer.shape != (length,) or not np.all(np.isfinite(answer)):
        raise ValueError(f"{name} must be one finite length-{length} vector")
    if nonnegative and np.any(answer < 0.0):
        raise ValueError(f"{name} must be nonnegative")
    return answer


def _weight(value: Array, rows: int | None = None) -> Array:
    answer = np.asarray(value, dtype=np.float64)
    if answer.ndim != 2 or not np.all(np.isfinite(answer)):
        raise ValueError("weight must be one finite matrix")
    if rows is not None and answer.shape[0] != rows:
        raise ValueError("weight row count mismatch")
    return answer


def _bridge(value: Array) -> Array:
    answer = np.asarray(value, dtype=np.float64)
    if answer.ndim != 2 or answer.shape[0] != answer.shape[1] or not np.all(np.isfinite(answer)):
        raise ValueError("bridge must be one finite square matrix")
    if not np.allclose(answer, answer.T, rtol=0.0, atol=2e-12):
        raise ValueError("bridge must be symmetric")
    if not np.allclose(np.diag(answer), 1.0, rtol=0.0, atol=2e-12):
        raise ValueError("bridge must have a unit diagonal")
    return answer


def diagonal_path_energies(
    weights: Sequence[Array],
    relu_probability: Sequence[Array],
    *,
    terminal_energy: Array | None = None,
) -> tuple[Array, ...]:
    """Return exact mean-only Rademacher-probe path energies by layer.

    In row notation, a source activation first crosses ``W_l`` and then the
    next ReLU: the local mean tangent is ``W_l diag(p_l)``.  If a terminal
    Rademacher probe and one independent Rademacher diagonal at every hidden
    interface have independent unit-variance coordinates, then

    ``E[(J_l(s) g)_i^2] = sum_a W_l[i,a]^2 p_l[a]^2 h[l+1,a]``.

    A terminal probe alone leaves coherent cross-path terms, so it cannot
    justify this diagonal recursion.  The recursion instead gives the exact
    diagonal second moment of a *sign-scrambled mean-channel path sketch*.
    The signs are analytically integrated, not used by the returned
    estimator.  It costs O(L n^2), stores only vectors, and is
    permutation-covariant.  It is deliberately not asserted to equal either
    the coherent mean response or the complete M121/M125 covariance response.
    """

    if len(weights) == 0 or len(weights) != len(relu_probability):
        raise ValueError("weights and ReLU probabilities must be nonempty and matched")
    parsed = tuple(_weight(value) for value in weights)
    width = parsed[-1].shape[1]
    if any(value.shape != (width, width) for value in parsed):
        raise ValueError("this fixed-width branch requires square matched weights")
    probabilities = tuple(
        _finite_vector("relu_probability", value, width, nonnegative=True)
        for value in relu_probability
    )
    if any(np.any(value > 1.0 + 2e-12) for value in probabilities):
        raise ValueError("ReLU probabilities must lie in [0,1]")
    if terminal_energy is None:
        energy = np.ones(width, dtype=np.float64)
    else:
        energy = _finite_vector("terminal_energy", terminal_energy, width, nonnegative=True).copy()
    if not np.any(energy > 0.0):
        raise ValueError("terminal energy must have positive mass")

    answer: list[Array] = [np.empty(width, dtype=np.float64) for _ in parsed]
    for layer in range(len(parsed) - 1, -1, -1):
        # ``gated`` lives after W_l.  The row energy is exactly the strength
        # needed for the M143 proposal at W_l and becomes the suffix energy
        # for the preceding source activation.
        gated = probabilities[layer] ** 2 * energy
        energy = (parsed[layer] ** 2) @ gated
        if not np.all(np.isfinite(energy)) or np.any(energy < 0.0):
            raise ArithmeticError("non-finite path-energy recursion")
        answer[layer] = energy.copy()
    return tuple(answer)


def output_aware_node_strength_from_gated_downstream_energy(
    weight: Array,
    source_scale: Array,
    gated_downstream_energy: Array,
) -> Array:
    """Return the positive-gauge-invariant M143 node strength ``tau``.

    ``gated_downstream_energy`` means ``p[r]^2 * E[r+1]`` and therefore
    refers to the already-gated energy *after*
    ``weight``.  Passing the result of :func:`diagonal_path_energies` through
    :func:`output_aware_node_strength_from_row_energy` at the same layer is
    valid because that recurrence computes this weighted row energy exactly.
    The direct form is exposed to make the gauge identity independently
    testable.
    """

    weight = _weight(weight)
    n, outputs = weight.shape
    scale = _finite_vector("source_scale", source_scale, n)
    if np.any(scale <= 0.0):
        raise ValueError("source_scale must be strictly positive")
    energy = _finite_vector(
        "gated_downstream_energy", gated_downstream_energy, outputs, nonnegative=True
    )
    weighted = (weight * weight) @ energy
    if not np.all(np.isfinite(weighted)) or np.any(weighted < 0.0):
        raise ArithmeticError("weighted row energy is invalid")
    return scale * np.sqrt(weighted)


def output_aware_node_strength_from_row_energy(source_scale: Array, row_energy: Array) -> Array:
    """Apply source scales to cached path energy for one proposal layer."""

    source_scale = np.asarray(source_scale, dtype=np.float64)
    row_energy = _finite_vector("row_energy", row_energy, source_scale.size, nonnegative=True)
    if not np.all(np.isfinite(source_scale)) or np.any(source_scale <= 0.0):
        raise ValueError("source_scale must be one strictly positive finite vector")
    return source_scale * np.sqrt(row_energy)


def scale_only_node_strength(weight: Array, source_scale: Array) -> Array:
    """Frozen attribution arm ``s_i ||W_i||`` inherited from M139.

    This is not M133 unless every physical ReLU scale equals one.  It exists
    so the response protocol can causally separate the preserved source-scale
    component from M143's new downstream path-energy component.
    """

    weight = _weight(weight)
    source_scale = _finite_vector("source_scale", source_scale, weight.shape[0])
    if np.any(source_scale <= 0.0):
        raise ValueError("source_scale must be strictly positive")
    return source_scale * np.linalg.norm(weight, axis=1)


def physical_relu_scale(mean: Array, variance: Array) -> Array:
    """Return ``sqrt(Var(ReLU(Z_i)))`` for independent Gaussian marginals.

    This is the precise physical statistic used by both M143 and its
    scale-only attribution arm.  It is strictly positive for finite mean and
    positive finite variance; invalid or numerically collapsed states fail
    closed instead of receiving a floor.
    """

    mean = np.asarray(mean, dtype=np.float64)
    if mean.ndim != 1 or not np.all(np.isfinite(mean)):
        raise ValueError("mean must be one finite vector")
    variance = _finite_vector("variance", variance, mean.size)
    if np.any(variance <= 0.0):
        raise ValueError("variance must be strictly positive")
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    cdf = np.fromiter(
        (0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in alpha),
        dtype=np.float64,
        count=mean.size,
    )
    density = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
    first = sigma * density + mean * cdf
    second = (mean * mean + variance) * cdf + mean * sigma * density
    relu_variance = second - first * first
    if not np.all(np.isfinite(relu_variance)) or np.any(relu_variance <= 0.0):
        raise ArithmeticError("physical ReLU variance collapsed or became non-finite")
    return np.sqrt(relu_variance)


def freeze_factored_proposal(proposal: Factored211Proposal) -> Factored211Proposal:
    """Deep-copy an immutable proposal snapshot before any coefficient/draw."""

    def frozen(value: Array) -> Array:
        answer = np.array(value, dtype=np.float64, copy=True)
        answer.setflags(write=False)
        return answer

    return Factored211Proposal(
        absolute_residual=frozen(proposal.absolute_residual),
        node_norm=frozen(proposal.node_norm),
        z_a=float(proposal.z_a),
        z_b=float(proposal.z_b),
        z_c=float(proposal.z_c),
        center_a=frozen(proposal.center_a),
        center_b=frozen(proposal.center_b),
        center_c=frozen(proposal.center_c),
        uniform_mixture=float(proposal.uniform_mixture),
    )


def make_output_aware_proposal(
    bridge: Array,
    node_strength: Array,
    *,
    uniform_mixture: float = 0.05,
) -> Factored211Proposal:
    """Construct M133's three-tree HH law with M143 output-aware strengths.

    The normalizer and sampling construction are exactly the M133 law after
    the substitution ``||W_i|| -> tau_i``.  Thus all sampled terms keep the
    same five rectangular products and use exactly the same coefficient / q
    HH correction.  A nonzero uniform component owns any zero-strength node.
    """

    bridge = _bridge(bridge)
    n = bridge.shape[0]
    strength = _finite_vector("node_strength", node_strength, n, nonnegative=True).copy()
    if n < 3:
        raise ValueError("the [2,1,1] proposal needs width at least three")
    if not math.isfinite(uniform_mixture) or not (0.0 < uniform_mixture <= 1.0):
        raise ValueError("uniform_mixture must lie in (0,1]")
    residual = np.abs(bridge.copy())
    np.fill_diagonal(residual, 0.0)

    a = residual * strength[None, :]
    a_sum = np.sum(a, axis=1)
    a_distinct = np.maximum(a_sum * a_sum - np.sum(a * a, axis=1), 0.0)
    center_a = strength**2 * a_distinct

    center_b = np.zeros(n, dtype=np.float64)
    center_c = np.zeros(n, dtype=np.float64)
    for centre in range(n):
        edge = residual[:, centre]
        left = strength**2 * edge
        right = strength * edge
        distinct = float(np.sum(left) * np.sum(right) - left @ right)
        center_b[centre] = strength[centre] * max(0.0, distinct)
        center_c[centre] = center_b[centre]
    return Factored211Proposal(
        absolute_residual=residual,
        node_norm=strength,
        z_a=float(np.sum(center_a)),
        z_b=float(np.sum(center_b)),
        z_c=float(np.sum(center_c)),
        center_a=center_a,
        center_b=center_b,
        center_c=center_c,
        uniform_mixture=float(uniform_mixture),
    )


def m143_incremental_cost_envelope(
    *, width: int = 256, layers: int = 31, safety_factor: float = 1.25
) -> dict[str, int | float | bool]:
    """Float32 planning worksheet for the *incremental path-energy* piece.

    It includes separate square, weighted matvec, probability-square/scale,
    vector storage, and proposal-strength operations.  It does *not* rebill
    M133's existing O(n^2) three-bank tables, exact coefficient quadrature, or
    five rectangular products.  It is not the full replacement proposal
    bill.  The default target shape now has a separate native structural trace
    and non-overlap crosswalk; this helper remains an independently checkable
    formula for the new recurrence alone.
    """

    if type(width) is not int or type(layers) is not int or width <= 0 or layers <= 0:
        raise ValueError("width and layers must be positive integers")
    if not math.isfinite(safety_factor) or safety_factor < 1.0:
        raise ValueError("safety_factor must be finite and at least one")
    entries = width * width * layers
    # Every term is deliberately charged as an ordinary scalar/copy/fill-rate
    # operation.  This dominates the actual vector-only recursion.
    square = entries
    weighted_matvec_multiply_add = 2 * entries
    relu_and_source_scale = 5 * width * layers
    cached_vectors_and_strength = 5 * width * layers
    proposal_integration = 6 * width * layers
    raw = square + weighted_matvec_multiply_add + relu_and_source_scale + cached_vectors_and_strength + proposal_integration
    protected = int(math.ceil(safety_factor * raw))
    return {
        "width": width,
        "layers": layers,
        "raw_incremental": int(raw),
        "protected_incremental": protected,
        "protected_billions": protected / 1.0e9,
        "scope": "incremental path-energy and strength only",
        "target_dtype": "float32",
        "under_five_billion": protected <= 5_000_000_000,
        "uses_full_covariance_goal_adjoint": False,
        "uses_added_rectangular_products": False,
        "requires_independent_hh_draws": True,
        "native_full_proposal_trace_completed_at_default_shape": (
            width == 256 and layers == 31 and safety_factor == 1.25
        ),
        "default_native_full_proposal_billed": (
            67_900_646 if width == 256 and layers == 31 and safety_factor == 1.25 else None
        ),
        "default_complete_nonoverlap_protected": (
            94_903_919_088 if width == 256 and layers == 31 and safety_factor == 1.25 else None
        ),
    }
