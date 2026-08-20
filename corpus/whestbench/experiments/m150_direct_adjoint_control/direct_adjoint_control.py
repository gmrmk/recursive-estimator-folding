"""Generated-only algebra for M150 direct-adjoint C_211 contraction.

This module is deliberately not an estimator.  It establishes the ownership
and associativity identities needed to ask a narrow question: can the
canonical-copula control be contracted with an *already certified* response
dual without first emitting its dense source matrices?  The answer in this
file is algebraic only.  It never constructs a response dual from a contest
network or evaluates a challenge response.

Conventions match M133/M148.  ``(i,j,k)`` is ordered in the singleton labels;
the physical unit is singleton-symmetric and therefore owns a factor 1/2.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class CanonicalState:
    """Finite signed cubature state used only for the M148 C_211 identity."""

    omega: Array  # (s,); may be signed, must sum to one
    conditional_mean: Array  # (s,n)
    conditional_variance: Array  # (s,n)


@dataclass(frozen=True)
class Source211:
    """The three M133 fourth-order source slots."""

    aaaa: Array  # (m,)
    aaab: Array  # (m,m)
    aabb: Array  # (m,m)


@dataclass(frozen=True)
class ResponseDual:
    """Abstract all-output linear response dual for the three source slots.

    ``aaab[o]`` and ``aabb[o]`` are full source-matrix covectors.  ``aaaa`` is
    a diagonal covector.  This is the exact interface a direct contraction
    would need; no claim is made that an existing response carrier exposes it
    cheaply.
    """

    aaaa: Array  # (outputs,m)
    aaab: Array  # (outputs,m,m)
    aabb: Array  # (outputs,m,m)


def _check_state(state: CanonicalState) -> tuple[Array, Array, Array]:
    omega = np.asarray(state.omega, dtype=np.float64)
    mean = np.asarray(state.conditional_mean, dtype=np.float64)
    variance = np.asarray(state.conditional_variance, dtype=np.float64)
    if omega.ndim != 1 or mean.ndim != 2 or variance.shape != mean.shape:
        raise ValueError("state arrays have incompatible dimensions")
    if omega.size != mean.shape[0] or mean.shape[1] < 3:
        raise ValueError("state needs at least three coordinates")
    if not (np.all(np.isfinite(omega)) and np.all(np.isfinite(mean)) and np.all(np.isfinite(variance))):
        raise ValueError("state must be finite")
    if np.any(variance < 0.0):
        raise ValueError("conditional variances must be nonnegative")
    if not math.isclose(float(np.sum(omega)), 1.0, rel_tol=0.0, abs_tol=3e-13):
        raise ValueError("signed cubature weights must sum to one")
    return omega, mean, variance


def covariance_star(state: CanonicalState) -> Array:
    """Exact finite-cubature covariance including the diagonal conditional star."""

    omega, mean, variance = _check_state(state)
    mu = omega @ mean
    centered = mean - mu[None, :]
    return centered.T @ (omega[:, None] * centered) + np.diag(omega @ variance)


def canonical_delta_tilde(state: CanonicalState) -> Array:
    """Return M148's connected C_211 coefficient on distinct labels only.

    The diagonal/one-singleton collisions are intentionally zero here.  They
    belong to their separate source ownership classes, and zeroing them makes
    that exclusion machine-checkable.
    """

    omega, mean, variance = _check_state(state)
    n = mean.shape[1]
    mu = omega @ mean
    a = mean - mu[None, :]
    t = a * a + variance
    v = covariance_star(state)
    answer = np.zeros((n, n, n), dtype=np.float64)
    for i, j, k in itertools.permutations(range(n), 3):
        raw = float(np.sum(omega * t[:, i] * a[:, j] * a[:, k]))
        answer[i, j, k] = raw - v[i, i] * v[j, k] - 2.0 * v[i, j] * v[i, k]
    return answer


def feature_211(weight: Array, i: int, j: int, k: int) -> Source211:
    """Coefficient-free M133 [2,1,1] source feature for one ordered triple."""

    w = np.asarray(weight, dtype=np.float64)
    if w.ndim != 2 or not np.all(np.isfinite(w)):
        raise ValueError("weight must be a finite matrix")
    n, _ = w.shape
    if not (0 <= i < n and 0 <= j < n and 0 <= k < n and len({i, j, k}) == 3):
        raise ValueError("the [2,1,1] labels must be distinct")
    x, y, z = w[i], w[j], w[k]
    aaab = (
        6.0 * np.outer(x * y * z, x)
        + 3.0 * np.outer(x * x * z, y)
        + 3.0 * np.outer(x * x * y, z)
    )
    first = 2.0 * np.outer(x * x, y * z)
    second = 4.0 * np.outer(x * y, x * z)
    aabb = first + first.T + second + second.T
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def source_add(left: Source211, right: Source211) -> Source211:
    return Source211(left.aaaa + right.aaaa, left.aaab + right.aaab, left.aabb + right.aabb)


def source_scale(value: float, source: Source211) -> Source211:
    return Source211(value * source.aaaa, value * source.aaab, value * source.aabb)


def dense_c211(weight: Array, delta: Array) -> Source211:
    """Exhaustive reference for C_211 = .5 sum_ordered delta F."""

    w = np.asarray(weight, dtype=np.float64)
    n, m = w.shape
    d = np.asarray(delta, dtype=np.float64)
    if d.shape != (n, n, n):
        raise ValueError("delta shape must be (n,n,n)")
    total = Source211(np.zeros(m), np.zeros((m, m)), np.zeros((m, m)))
    for i, j, k in itertools.permutations(range(n), 3):
        total = source_add(total, source_scale(0.5 * d[i, j, k], feature_211(w, i, j, k)))
    return total


def _check_dual(dual: ResponseDual, width: int) -> tuple[Array, Array, Array]:
    aaaa = np.asarray(dual.aaaa, dtype=np.float64)
    aaab = np.asarray(dual.aaab, dtype=np.float64)
    aabb = np.asarray(dual.aabb, dtype=np.float64)
    if aaaa.ndim != 2 or aaaa.shape[1] != width:
        raise ValueError("aaaa dual shape must be (outputs,width)")
    outputs = aaaa.shape[0]
    if aaab.shape != (outputs, width, width) or aabb.shape != (outputs, width, width):
        raise ValueError("matrix duals must have shape (outputs,width,width)")
    if not (np.all(np.isfinite(aaaa)) and np.all(np.isfinite(aaab)) and np.all(np.isfinite(aabb))):
        raise ValueError("dual must be finite")
    return aaaa, aaab, aabb


def contract_source(source: Source211, dual: ResponseDual) -> Array:
    """Dense-source reference response: <dual, source> for every output."""

    width = source.aaaa.size
    aaaa, aaab, aabb = _check_dual(dual, width)
    return (
        aaaa @ source.aaaa
        + np.einsum("oab,ab->o", aaab, source.aaab, optimize=True)
        + np.einsum("oab,ab->o", aabb, source.aabb, optimize=True)
    )


def local_feature_dual_formula(weight: Array, i: int, j: int, k: int, dual: ResponseDual) -> Array:
    """Closed-form all-output contraction of one M133 feature.

    Write ``A_o = dual.aaab[o] + diag(dual.aaaa[o])`` and replace the aabb
    covector by its symmetric part ``B_o``.  For ``x=W_i,y=W_j,z=W_k``,

    ``<dual_o,F_e> = 6(xyz)^T A_o x + 3(x^2z)^T A_o y + 3(x^2y)^T A_o z
                      + 4(x^2)^T B_o(yz) + 8(xy)^T B_o(xz)``.

    This exposes precisely what an alleged rectangular-GEMM implementation
    must supply: all-output bilinear forms against the response matrices.
    """

    w = np.asarray(weight, dtype=np.float64)
    _, m = w.shape
    h, a, b = _check_dual(dual, m)
    x, y, z = w[i], w[j], w[k]
    a = a + np.einsum("oa,ab->oab", h, np.eye(m), optimize=True)
    b = 0.5 * (b + b.swapaxes(1, 2))
    return (
        6.0 * np.einsum("a,oab,b->o", x * y * z, a, x, optimize=True)
        + 3.0 * np.einsum("a,oab,b->o", x * x * z, a, y, optimize=True)
        + 3.0 * np.einsum("a,oab,b->o", x * x * y, a, z, optimize=True)
        + 4.0 * np.einsum("a,oab,b->o", x * x, b, y * z, optimize=True)
        + 8.0 * np.einsum("a,oab,b->o", x * y, b, x * z, optimize=True)
    )


def direct_c211_dual_contract(weight: Array, delta: Array, dual: ResponseDual) -> Array:
    """Exact associative contraction without materialising C_211.

    This is the desired equality, not a cost claim: it has the same ordered
    singleton factor, collision exclusions, covariance-star coefficients, and
    all three source slots as ``dense_c211``.  The routine intentionally uses
    exhaustive triples, making any replacement by rectangular GEMMs a separate
    theorem rather than an accidental benchmark shortcut.
    """

    w = np.asarray(weight, dtype=np.float64)
    n, m = w.shape
    d = np.asarray(delta, dtype=np.float64)
    aaaa, aaab, aabb = _check_dual(dual, m)
    if d.shape != (n, n, n):
        raise ValueError("delta shape must be (n,n,n)")
    total = np.zeros(aaaa.shape[0], dtype=np.float64)
    for i, j, k in itertools.permutations(range(n), 3):
        total += 0.5 * d[i, j, k] * local_feature_dual_formula(w, i, j, k, dual)
    return total


def direct_aaab_simplified(weight: Array, delta: Array) -> Array:
    """Closed ordered-singleton simplification of the aaab source only.

    Since ``delta[i,j,k]=delta[i,k,j]``, the two 3-coefficient terms in M133
    coincide after summation.  The half-owned ordered sum is therefore

    3 sum d_ijk [ (x*y*z)x^T + (x^2*z)y^T ].

    It is a useful guard against losing the mandatory factor 1/2.
    """

    w = np.asarray(weight, dtype=np.float64)
    n, m = w.shape
    d = np.asarray(delta, dtype=np.float64)
    answer = np.zeros((m, m), dtype=np.float64)
    for i, j, k in itertools.permutations(range(n), 3):
        x, y, z = w[i], w[j], w[k]
        answer += 3.0 * d[i, j, k] * (
            np.outer(x * y * z, x) + np.outer(x * x * z, y)
        )
    return answer


def full_dual_static_lower_bound(width: int = 256, layers: int = 30) -> dict[str, int | float]:
    """Unavoidable all-output exact covariance-adjoint affine lower bound.

    A full response dual has one dense width-by-width covariance covector for
    each output.  One affine pullback needs two square matrix products per
    output.  FlopScope bills a float64 product at twice its base rate.
    """

    if width <= 0 or layers <= 0:
        raise ValueError("width and layers must be positive")
    f32_square = 2 * width**3 - width**2
    f64_square = 2 * f32_square
    per_layer = 2 * width * f64_square
    return {
        "width": width,
        "layers": layers,
        "full_dual_entries": width**3,
        "full_dual_bytes_float64": 8 * width**3,
        "one_f64_square_matmul": f64_square,
        "all_output_affine_pullback_per_layer": per_layer,
        "all_output_affine_pullback_total": layers * per_layer,
        "terabytes_decimal": layers * per_layer / 1e12,
    }


def cp_parameter_dimension(rank: int, width: int) -> int:
    """Degrees of freedom in a shared CP tensor with output/source/source modes."""

    if rank < 0 or width <= 0:
        raise ValueError("invalid rank/width")
    return rank * (3 * width - 2)  # remove two per-component scale gauges


def generic_cp_rank_dimension_lower_bound(width: int) -> int:
    """Dimension-count lower bound for a generic (n,n,n) response dual."""

    return math.ceil(width**3 / (3 * width - 2))
