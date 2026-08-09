"""Exact response-free algebra for M204's lifted rank-one B=1 control.

This module implements only the predeclared algebraic component.  It does not
import a contest model, coefficient endpoint, response carrier, scorer, or
source-variance runner.  In particular, its cost ledger records the strict
premise but is not a native replacement trace.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray
B1_NODE_COUNT = 49
WIDTH = 256
SOURCE_LAYERS = 31
STRICT_COMPOSED_HEADROOM = 1_986_871_472
CONDITIONAL_REPLACEMENT_HEADROOM = 9_723_621_632
PROTECTION_NUMERATOR = 5
PROTECTION_DENOMINATOR = 4


@dataclass(frozen=True)
class Source211:
    """The three M133/M151 source slots, with the half owner already applied."""

    aaaa: Array
    aaab: Array
    aabb: Array


@dataclass(frozen=True)
class RankOneB1State:
    """A padded 49-node product-Rademacher conditional-moment state."""

    omega: Array
    conditional_mean: Array
    conditional_variance: Array
    rank_factor: Array
    diagonal_residual: Array


def _finite_vector(value: Array, name: str) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 1 or result.size < 3 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite vector with at least three entries")
    return result


def _finite_square(value: Array, name: str) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 2 or result.shape[0] != result.shape[1] or result.shape[0] < 3:
        raise ValueError(f"{name} must be a square matrix with width at least three")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    if not np.allclose(result, result.T, rtol=0.0, atol=2e-13):
        raise ValueError(f"{name} must be symmetric")
    return result


def build_rank_one_b1_state(mean: Array, covariance: Array) -> RankOneB1State:
    """Build the frozen rank-one state from a labelled M179-style ``(mu,V)``.

    The factor is ``u_i=sqrt(V_ii)/sqrt(n_active)`` on positive-variance
    coordinates.  It is therefore permutation-covariant and positive-gauge
    covariant without an eigenvector sign convention, row ranking, or target
    input.  Zero-variance rows are retained with zero factor and variance.
    """

    mu = _finite_vector(mean, "mean")
    v = _finite_square(covariance, "covariance")
    if v.shape[0] != mu.size:
        raise ValueError("mean/covariance widths disagree")
    diagonal = np.diag(v).copy()
    if np.any(diagonal < 0.0):
        raise ValueError("negative covariance diagonal")
    active = diagonal > 0.0
    count = int(np.count_nonzero(active))
    if count == 0:
        raise ValueError("rank-one state has no positive-variance coordinate")

    q = np.zeros(mu.size, dtype=np.float64)
    q[active] = 1.0 / math.sqrt(count)
    factor = np.sqrt(diagonal) * q
    residual = diagonal - factor * factor
    if np.any(residual < 0.0):
        raise ValueError("rank-one diagonal residual is negative")

    omega = np.zeros(B1_NODE_COUNT, dtype=np.float64)
    omega[:2] = 0.5
    conditional_mean = np.broadcast_to(mu, (B1_NODE_COUNT, mu.size)).copy()
    conditional_mean[0] += factor
    conditional_mean[1] -= factor
    conditional_variance = np.broadcast_to(residual, conditional_mean.shape).copy()
    return RankOneB1State(
        omega=omega,
        conditional_mean=conditional_mean,
        conditional_variance=conditional_variance,
        rank_factor=factor,
        diagonal_residual=residual,
    )


def canonical_covariance(state: RankOneB1State) -> Array:
    """Return the B=1 covariance star, including conditional variance."""

    omega = np.asarray(state.omega, dtype=np.float64)
    mean = np.asarray(state.conditional_mean, dtype=np.float64)
    variance = np.asarray(state.conditional_variance, dtype=np.float64)
    if omega.shape != (B1_NODE_COUNT,) or mean.shape != variance.shape:
        raise ValueError("invalid B=1 state shapes")
    if not math.isclose(float(np.sum(omega)), 1.0, rel_tol=0.0, abs_tol=3e-13):
        raise ValueError("B=1 weights must sum to one")
    mu = omega @ mean
    centered = mean - mu[None, :]
    answer = centered.T @ (omega[:, None] * centered)
    answer += np.diag(omega @ variance)
    return answer


def rank_factor_schur_identity(factor: Array) -> tuple[Array, Array]:
    """Return direct and factorized ``V_off o V_off`` for one rank factor."""

    u = _finite_vector(factor, "factor")
    covariance = np.outer(u, u)
    off = covariance.copy()
    np.fill_diagonal(off, 0.0)
    direct = off * off
    h = u * u
    factorized = np.outer(h, h) - np.diag(h * h)
    return direct, factorized


def canonical_delta_tilde(state: RankOneB1State) -> Array:
    """Evaluate the M151 distinct-label coefficient directly from 49 nodes."""

    omega = np.asarray(state.omega, dtype=np.float64)
    mean = np.asarray(state.conditional_mean, dtype=np.float64)
    variance = np.asarray(state.conditional_variance, dtype=np.float64)
    covariance = canonical_covariance(state)
    mu = omega @ mean
    centered = mean - mu[None, :]
    width = mean.shape[1]
    answer = np.zeros((width, width, width), dtype=np.float64)
    for i in range(width):
        for j in range(width):
            for k in range(width):
                if len({i, j, k}) != 3:
                    continue
                raw = np.sum(
                    omega
                    * (centered[:, i] * centered[:, i] + variance[:, i])
                    * centered[:, j]
                    * centered[:, k]
                )
                answer[i, j, k] = (
                    raw
                    - covariance[i, i] * covariance[j, k]
                    - 2.0 * covariance[i, j] * covariance[i, k]
                )
    return answer


def rank_one_control_table(factor: Array, *, distinct_only: bool) -> Array:
    """Return ``-2 u_i^2 u_j u_k`` on all or only pairwise-distinct triples."""

    u = _finite_vector(factor, "factor")
    answer = -2.0 * np.einsum("i,j,k->ijk", u * u, u, u)
    if distinct_only:
        for i in range(u.size):
            answer[i, i, :] = 0.0
            answer[i, :, i] = 0.0
            answer[:, i, i] = 0.0
    return answer


def _weight_array(weight: Array) -> Array:
    value = np.asarray(weight, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] < 3 or not np.all(np.isfinite(value)):
        raise ValueError("weight must be a finite labelled matrix")
    return value


def zero_source(output_width: int) -> Source211:
    return Source211(
        np.zeros(output_width, dtype=np.float64),
        np.zeros((output_width, output_width), dtype=np.float64),
        np.zeros((output_width, output_width), dtype=np.float64),
    )


def source_add(left: Source211, right: Source211) -> Source211:
    return Source211(
        left.aaaa + right.aaaa,
        left.aaab + right.aaab,
        left.aabb + right.aabb,
    )


def half_owned_feature(weight: Array, i: int, j: int, k: int) -> Source211:
    """M151's half-owned source feature, deliberately extended to collisions."""

    w = _weight_array(weight)
    if not all(0 <= index < w.shape[0] for index in (i, j, k)):
        raise ValueError("label outside source width")
    x, y, z = w[i], w[j], w[k]
    aaab = 3.0 * (
        np.outer(x * y * z, x)
        + np.outer(x * x * z, y)
    )
    first = np.outer(x * x, y * z)
    split = 2.0 * np.outer(x * y, x * z)
    aabb = first + first.T + split + split.T
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def brute_complete_source(weight: Array, coefficient: Array) -> Source211:
    """Complete ordered-triple parity oracle; prohibited at target width."""

    w = _weight_array(weight)
    coefficient = np.asarray(coefficient, dtype=np.float64)
    n = w.shape[0]
    if coefficient.shape != (n, n, n) or not np.all(np.isfinite(coefficient)):
        raise ValueError("coefficient must be a finite cubic table")
    answer = zero_source(w.shape[1])
    for i in range(n):
        for j in range(n):
            for k in range(n):
                scale = float(coefficient[i, j, k])
                if scale == 0.0:
                    continue
                feature = half_owned_feature(w, i, j, k)
                answer = source_add(
                    answer,
                    Source211(scale * feature.aaaa, scale * feature.aaab, scale * feature.aabb),
                )
    return answer


def compile_lifted_rank_one_control(weight: Array, factor: Array) -> Source211:
    """Exact one-GEMM-per-layer compiler for the complete-domain rank-one control."""

    w = _weight_array(weight)
    u = _finite_vector(factor, "factor")
    if w.shape[0] != u.size:
        raise ValueError("weight/factor label widths disagree")
    p = w.T @ u
    rho = (w * w).T @ (u * u)
    b = w.T @ ((u * u)[:, None] * w)
    aaab = -6.0 * (
        (p * p)[:, None] * b
        + np.outer(rho * p, p)
    )
    aabb = -2.0 * (
        np.outer(rho, p * p)
        + np.outer(p * p, rho)
        + 4.0 * (b * np.outer(p, p))
    )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def source_max_abs_difference(left: Source211, right: Source211) -> float:
    return float(
        max(
            np.max(np.abs(left.aaaa - right.aaaa)),
            np.max(np.abs(left.aaab - right.aaab)),
            np.max(np.abs(left.aabb - right.aabb)),
        )
    )


def distinct_only_table(value: Array) -> Array:
    """Zero collision entries while preserving the distinct-label target."""

    table = np.asarray(value, dtype=np.float64).copy()
    if table.ndim != 3 or len(set(table.shape)) != 1 or table.shape[0] < 3:
        raise ValueError("target must be a cubic table with width at least three")
    for i in range(table.shape[0]):
        table[i, i, :] = 0.0
        table[i, :, i] = 0.0
        table[:, i, i] = 0.0
    return table


def collision_count(width: int) -> int:
    n = int(width)
    if n < 3:
        raise ValueError("width must be at least three")
    return n * (3 * n - 2)


def complete_domain_mixture(distinct_q0: Array) -> Array:
    """M156's full-support complete-domain mixture from a distinct-only law."""

    q0 = np.asarray(distinct_q0, dtype=np.float64)
    if q0.ndim != 3 or len(set(q0.shape)) != 1 or q0.shape[0] < 3:
        raise ValueError("q0 must be a cubic table with width at least three")
    n = q0.shape[0]
    total = 0.0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    if not math.isfinite(float(q0[i, j, k])) or q0[i, j, k] <= 0.0:
                        raise ValueError("q0 must have positive finite distinct support")
                    total += float(q0[i, j, k])
                elif q0[i, j, k] != 0.0:
                    raise ValueError("q0 collision mass must be zero")
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=3e-13):
        raise ValueError("q0 distinct mass must be one")
    eta = collision_count(n) / float(n**3)
    answer = np.zeros_like(q0)
    collision_mass = eta / collision_count(n)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                answer[i, j, k] = (
                    (1.0 - eta) * q0[i, j, k]
                    if len({i, j, k}) == 3
                    else collision_mass
                )
    if np.any(answer <= 0.0) or not math.isclose(float(np.sum(answer)), 1.0, rel_tol=0.0, abs_tol=3e-13):
        raise AssertionError("complete-domain mixture lost full support or mass")
    return answer


def complete_domain_conservation_source(
    weight: Array,
    distinct_target: Array,
    lifted_control: Array,
    proposal: Array,
) -> tuple[Source211, Source211, Source211]:
    """Return target, deterministic control, and exact residual expectation.

    The proposal is checked because the residual identity requires full support,
    but no random sampling occurs here.
    """

    target = distinct_only_table(distinct_target)
    control = np.asarray(lifted_control, dtype=np.float64)
    proposal = np.asarray(proposal, dtype=np.float64)
    if control.shape != target.shape or proposal.shape != target.shape:
        raise ValueError("target/control/proposal shapes disagree")
    if np.any(proposal <= 0.0) or not math.isclose(float(np.sum(proposal)), 1.0, rel_tol=0.0, abs_tol=3e-13):
        raise ValueError("proposal must have full support and unit mass")
    return (
        brute_complete_source(weight, target),
        brute_complete_source(weight, control),
        brute_complete_source(weight, target - control),
    )


def m204_cost_ledger(width: int = WIDTH, layers: int = SOURCE_LAYERS) -> dict[str, int | str | bool]:
    """Static arithmetic only; a true source-emission replacement is unproved."""

    n = int(width)
    layer_count = int(layers)
    if n <= 0 or layer_count <= 0:
        raise ValueError("width and layers must be positive")
    f32_per_layer = 2 * n**3 - n**2
    f64_per_layer = 2 * f32_per_layer
    f64_all_layers = f64_per_layer * layer_count
    protected = f64_all_layers * PROTECTION_NUMERATOR // PROTECTION_DENOMINATOR
    return {
        "rank": 1,
        "width": n,
        "layers": layer_count,
        "dense_output_products_per_layer": 1,
        "f64_square_product_all_layers": f64_all_layers,
        "protected_dense_source_emission": protected,
        "known_m151_booked_dense_source_emission": protected,
        "additional_if_same_call_proved": 0,
        "additional_if_uncredited": protected,
        "strict_composed_headroom": STRICT_COMPOSED_HEADROOM,
        "conditional_replacement_headroom": CONDITIONAL_REPLACEMENT_HEADROOM,
        "uncredited_product_exceeds_strict_headroom": protected > STRICT_COMPOSED_HEADROOM,
        "strict_trace_required": True,
        "native_replacement_proved": False,
        "status": "BLOCKED_COST_PREMISE",
    }
