"""M205 response-free complete-physical-owner rank-one B=1 algebra.

This module deliberately contains no contest-model, truth, scorer, response,
or source-variance code.  It proves only a source identity: a rank-one
complete-domain control can be added to, and subtracted from, M167's physical
fourth-order owner table without a cubic target compiler.
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
NO_REPLACEMENT_PARTIAL = 98_013_128_528
PROTECTION = 1.25


@dataclass(frozen=True)
class Source211:
    """The half-owned fourth-source slots consumed by the forward carrier."""

    aaaa: Array
    aaab: Array
    aabb: Array


@dataclass(frozen=True)
class RankOneB1State:
    """A total, padded 49-node B=1 Rademacher moment-functional state."""

    omega: Array
    conditional_mean: Array
    conditional_variance: Array
    factor: Array
    diagonal_residual: Array


@dataclass(frozen=True)
class PhysicalFourthOwners:
    """M167's physical [4], [3,1], and [2,2] fourth-cumulant owners."""

    k4: Array
    k31: Array
    k22: Array


def _finite_vector(value: Array, name: str) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 1 or result.size < 3 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite vector of width at least three")
    return result


def _finite_square(value: Array, name: str) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 2 or result.shape[0] != result.shape[1] or result.shape[0] < 3:
        raise ValueError(f"{name} must be a finite square matrix of width at least three")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    if not np.allclose(result, result.T, rtol=0.0, atol=2e-13):
        raise ValueError(f"{name} must be symmetric")
    return result


def build_rank_one_b1_state(mean: Array, covariance: Array) -> RankOneB1State:
    """Build M204's fixed diagonal-scale loading, including the all-zero case.

    The all-zero branch emits the exact zero control instead of raising.  It
    is therefore safe for a zero-variance M179 post-ReLU state and cannot turn
    a harmless zero source into an estimator failure.
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
    factor = np.zeros(mu.size, dtype=np.float64)
    if count:
        factor[active] = np.sqrt(diagonal[active]) / math.sqrt(count)
    residual = diagonal - factor * factor
    if np.any(residual < -2e-14):
        raise ValueError("rank-one diagonal residual is negative")
    residual = np.maximum(residual, 0.0)

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
        factor=factor,
        diagonal_residual=residual,
    )


def canonical_covariance(state: RankOneB1State) -> Array:
    """Return the B=1 covariance including the conditional-variance star."""

    omega = np.asarray(state.omega, dtype=np.float64)
    mean = np.asarray(state.conditional_mean, dtype=np.float64)
    variance = np.asarray(state.conditional_variance, dtype=np.float64)
    if omega.shape != (B1_NODE_COUNT,) or mean.shape != variance.shape:
        raise ValueError("invalid B=1 state shapes")
    if not np.all(np.isfinite(omega)) or not np.all(np.isfinite(mean)):
        raise ValueError("B=1 state is nonfinite")
    if np.any(variance < 0.0) or not np.all(np.isfinite(variance)):
        raise ValueError("B=1 conditional variance is invalid")
    if not math.isclose(float(np.sum(omega)), 1.0, rel_tol=0.0, abs_tol=3e-13):
        raise ValueError("B=1 weights must sum to one")
    mu = omega @ mean
    centered = mean - mu[None, :]
    return centered.T @ (omega[:, None] * centered) + np.diag(omega @ variance)


def canonical_delta_tilde_distinct(state: RankOneB1State) -> Array:
    """Direct M151 definition on distinct labels, retained as a parity oracle."""

    omega = np.asarray(state.omega, dtype=np.float64)
    mean = np.asarray(state.conditional_mean, dtype=np.float64)
    variance = np.asarray(state.conditional_variance, dtype=np.float64)
    mu = omega @ mean
    centered = mean - mu[None, :]
    covariance = canonical_covariance(state)
    n = mean.shape[1]
    answer = np.zeros((n, n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
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


def rank_one_control_table(factor: Array) -> Array:
    """Lift ``-2 u_i^2 u_j u_k`` to the full ordered triple domain."""

    u = _finite_vector(factor, "factor")
    return -2.0 * np.einsum("i,j,k->ijk", u * u, u, u)


def _checked_owners(owners: PhysicalFourthOwners, width: int) -> PhysicalFourthOwners:
    k4 = _finite_vector(owners.k4, "k4")
    # [3,1] has an identified triple label followed by a singleton label;
    # it is directed and must *not* be symmetrized.  Only [2,2] is an
    # unordered pair owner.
    k31 = np.asarray(owners.k31, dtype=np.float64)
    if k31.ndim != 2 or k31.shape[0] != k31.shape[1] or k31.shape[0] < 3:
        raise ValueError("k31 must be a finite square matrix of width at least three")
    if not np.all(np.isfinite(k31)):
        raise ValueError("k31 must be finite")
    k22 = _finite_square(owners.k22, "k22")
    if k4.size != width or k31.shape != (width, width) or k22.shape != (width, width):
        raise ValueError("physical-owner widths disagree")
    if not np.array_equal(np.diag(k31), np.zeros(width)):
        raise ValueError("k31 diagonal must be zero")
    if not np.array_equal(np.diag(k22), np.zeros(width)):
        raise ValueError("k22 diagonal must be zero")
    return PhysicalFourthOwners(k4=k4.copy(), k31=k31.copy(), k22=0.5 * (k22 + k22.T))


def complete_physical_owner_table(distinct_211: Array, owners: PhysicalFourthOwners) -> Array:
    """Construct M167's complete table with exactly one physical owner/row."""

    distinct = np.asarray(distinct_211, dtype=np.float64)
    if distinct.ndim != 3 or len(set(distinct.shape)) != 1 or distinct.shape[0] < 3:
        raise ValueError("distinct_211 must be a cubic table of width at least three")
    if not np.all(np.isfinite(distinct)):
        raise ValueError("distinct_211 must be finite")
    n = distinct.shape[0]
    checked = _checked_owners(owners, n)
    answer = np.zeros_like(distinct)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    if not math.isclose(float(distinct[i, j, k]), float(distinct[i, k, j]), rel_tol=0.0, abs_tol=2e-13):
                        raise ValueError("distinct_211 must be singleton-symmetric")
                    answer[i, j, k] = distinct[i, j, k]
    for i in range(n):
        answer[i, i, i] = checked.k4[i] / 6.0
        for j in range(n):
            if i == j:
                continue
            answer[i, i, j] = checked.k31[i, j] / 3.0
            answer[i, j, i] = checked.k31[i, j] / 3.0
            answer[i, j, j] = checked.k22[i, j] / 2.0
    return answer


def complete_residual_table(target: Array, control: Array) -> Array:
    """The physical complete-domain residual; collision rows are never re-zeroed."""

    target = np.asarray(target, dtype=np.float64)
    control = np.asarray(control, dtype=np.float64)
    if (
        target.shape != control.shape
        or target.ndim != 3
        or not np.all(np.isfinite(target))
        or not np.all(np.isfinite(control))
        or not np.allclose(target, target.swapaxes(1, 2), rtol=0.0, atol=2e-13)
        or not np.allclose(control, control.swapaxes(1, 2), rtol=0.0, atol=2e-13)
    ):
        raise ValueError("target/control tables must be finite and shape-identical")
    return target - control


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
    return Source211(left.aaaa + right.aaaa, left.aaab + right.aaab, left.aabb + right.aabb)


def half_owned_feature(weight: Array, i: int, j: int, k: int) -> Source211:
    """M151's feature extended to collisions for an independent test oracle."""

    w = _weight_array(weight)
    x, y, z = w[i], w[j], w[k]
    aaab = 3.0 * (np.outer(x * y * z, x) + np.outer(x * x * z, y))
    first = np.outer(x * x, y * z)
    split = 2.0 * np.outer(x * y, x * z)
    aabb = first + first.T + split + split.T
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def brute_complete_source(weight: Array, coefficient: Array) -> Source211:
    """Cubic complete-table source oracle; prohibited outside small-width tests."""

    w = _weight_array(weight)
    coefficient = np.asarray(coefficient, dtype=np.float64)
    n = w.shape[0]
    if coefficient.shape != (n, n, n) or not np.all(np.isfinite(coefficient)):
        raise ValueError("coefficient must be a finite width-cubic table")
    answer = zero_source(w.shape[1])
    for i in range(n):
        for j in range(n):
            for k in range(n):
                scale = float(coefficient[i, j, k])
                if scale:
                    feature = half_owned_feature(w, i, j, k)
                    answer = source_add(
                        answer,
                        Source211(scale * feature.aaaa, scale * feature.aaab, scale * feature.aabb),
                    )
    return answer


def compile_lifted_rank_one_control(weight: Array, factor: Array) -> Source211:
    """One-square-GEMM exact compiler for the full-domain rank-one control."""

    w = _weight_array(weight)
    u = _finite_vector(factor, "factor")
    if w.shape[0] != u.size:
        raise ValueError("weight/factor label widths disagree")
    p = w.T @ u
    rho = (w * w).T @ (u * u)
    b = w.T @ ((u * u)[:, None] * w)
    aaab = -6.0 * ((p * p)[:, None] * b + np.outer(rho * p, p))
    aabb = -2.0 * (
        np.outer(rho, p * p)
        + np.outer(p * p, rho)
        + 4.0 * ((p[:, None] * b) * p[None, :])
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


def source_cost_and_blockers(width: int = WIDTH, layers: int = SOURCE_LAYERS) -> dict[str, object]:
    """Record the strict cost block without inventing a replacement credit."""

    square_f32 = 2 * width**3 - width**2
    one_f64_square_all_layers = 2 * square_f32 * layers
    protected = int(math.ceil(PROTECTION * one_f64_square_all_layers))
    return {
        "one_f64_square_raw": one_f64_square_all_layers,
        "one_f64_square_protected": protected,
        "strict_no_replacement_partial": NO_REPLACEMENT_PARTIAL,
        "strict_composed_headroom": STRICT_COMPOSED_HEADROOM,
        "m151_booking": "unexecuted source-emission allowance, not an identical shared M179/M125b call",
        "physical_provider_blockers": [
            "M167 physical K4/K31/K22 coefficients are not a layer-bound native provider",
            "complete-domain proposal and residual event accounting are absent",
            "M198 conversion, terminal path, allocations, and residual wall are untraced",
            "M179/M151 overlap remains BLOCKED_OVERLAP until one integrated trace proves every call",
        ],
        "disposition": "BLOCKED_PHYSICAL_COLLISION_PROVIDER_AND_NATIVE_COST",
    }
