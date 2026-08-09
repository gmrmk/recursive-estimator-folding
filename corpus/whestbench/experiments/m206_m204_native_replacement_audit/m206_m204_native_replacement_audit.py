"""M206's response-free adversarial audit of an M204 replacement claim.

This module is deliberately small-width and generated-only.  It tests a
specific accounting assertion: whether M204's rank-one complete-domain source
can be treated as the arithmetic-identical M151 distinct-label source call.
It cannot evaluate an estimator, a proposal, a response, variance, MSE, or a
contest instance.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


Array = np.ndarray
WIDTH = 256
SOURCE_LAYERS = 31
# M199's composed strict gate is a 100B-FLOP budget.  Do not substitute the
# separate challenge-level number quoted in older campaign material here.
BUDGET = 100_000_000_000
M151_M179_NO_CREDIT_PARTIAL = 98_013_128_528
STRICT_HEADROOM = BUDGET - M151_M179_NO_CREDIT_PARTIAL
F64_RATE = 2
M151_PROTECTION_NUMERATOR = 5
M151_PROTECTION_DENOMINATOR = 4


@dataclass(frozen=True)
class Source211:
    """The three source slots, represented only for response-free checks."""

    aaaa: Array
    aaab: Array
    aabb: Array


def rank_one_control_table(factor: Array, *, distinct_only: bool) -> Array:
    """Return ``-2 u_i^2 u_j u_k`` on the requested ordered-triple domain."""

    u = np.asarray(factor, dtype=np.float64)
    if u.ndim != 1 or u.size < 3 or not np.all(np.isfinite(u)):
        raise ValueError("factor must be a finite one-dimensional vector of width >= 3")
    answer = -2.0 * np.einsum("i,j,k->ijk", u * u, u, u)
    if distinct_only:
        for i in range(u.size):
            answer[i, i, :] = 0.0
            answer[i, :, i] = 0.0
            answer[:, i, i] = 0.0
    return answer


def compile_complete_rank_one_lift(weight: Array, factor: Array) -> Source211:
    """Compile M204's complete-domain rank-one source slots.

    This is the one-square-contraction algebra.  It intentionally emits the
    complete-domain lift, not M151's collision-zeroed owner.
    """

    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] < 3 or w.shape[0] != u.size:
        raise ValueError("weight/factor shapes are incompatible")
    if not (np.all(np.isfinite(w)) and np.all(np.isfinite(u))):
        raise ValueError("weight and factor must be finite")
    a = u @ w
    b = w.T @ ((u * u)[:, None] * w)
    diagonal = np.diag(b)
    aaab = -6.0 * ((a * a)[:, None] * b + np.outer(diagonal * a, a))
    aabb = -2.0 * (
        np.outer(diagonal, a * a)
        + np.outer(a * a, diagonal)
        + 4.0 * b * np.outer(a, a)
    )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def source_max_abs_difference(left: Source211, right: Source211) -> float:
    """Return a shared max norm without conflating the two source owners."""

    return float(
        max(
            np.max(np.abs(left.aaaa - right.aaaa)),
            np.max(np.abs(left.aaab - right.aaab)),
            np.max(np.abs(left.aabb - right.aabb)),
        )
    )


def collision_statistic(weight: Array) -> Array:
    """Return ``D=(W^2)^T(W^2)``, one statistic exposed by collisions."""

    w = np.asarray(weight, dtype=np.float64)
    if w.ndim != 2 or not np.all(np.isfinite(w)):
        raise ValueError("weight must be finite and two-dimensional")
    return (w * w).T @ (w * w)


def gram_statistic(weight: Array, factor: Array | None = None) -> Array:
    """Return ``B=W^T diag(u^2) W``; Rademacher factors give ``W^T W``."""

    w = np.asarray(weight, dtype=np.float64)
    if w.ndim != 2 or not np.all(np.isfinite(w)):
        raise ValueError("weight must be finite and two-dimensional")
    if factor is None:
        return w.T @ w
    u = np.asarray(factor, dtype=np.float64)
    if u.shape != (w.shape[0],) or not np.all(np.isfinite(u)):
        raise ValueError("factor must match the weight-label dimension")
    return w.T @ ((u * u)[:, None] * w)


def b_equal_d_different_witness() -> tuple[Array, Array, Array, Array]:
    """Return two width-two matrices with equal B but different D.

    This is a non-identifiability witness for a *one-B-only* strict-collision
    reconstruction.  It is not asserted as a universal arithmetic lower bound:
    a new circuit may use W directly, but it must trace and pay that work.
    """

    identity = np.eye(2, dtype=np.float64)
    rotation = np.array([[1.0, -1.0], [1.0, 1.0]], dtype=np.float64) / np.sqrt(2.0)
    return (
        gram_statistic(identity),
        gram_statistic(rotation),
        collision_statistic(identity),
        collision_statistic(rotation),
    )


def matmul_flops(m: int, k: int, n: int, *, dtype_rate: int) -> int:
    """Pinned FlopScope 0.10.0 2D matmul arithmetic: rate*(2mkn-mn)."""

    if min(m, k, n, dtype_rate) <= 0:
        raise ValueError("dimensions and dtype rate must be positive")
    return int(dtype_rate) * (2 * int(m) * int(k) * int(n) - int(m) * int(n))


def raw_and_protected_cost_ledger() -> dict[str, int | bool | str]:
    """Static cost arithmetic only; no source call is credited as shared."""

    square_f64_per_layer = matmul_flops(WIDTH, WIDTH, WIDTH, dtype_rate=F64_RATE)
    row_f64_per_layer = matmul_flops(1, WIDTH, WIDTH, dtype_rate=F64_RATE)
    square_all = SOURCE_LAYERS * square_f64_per_layer
    row_all = SOURCE_LAYERS * row_f64_per_layer
    raw_minimum = square_all + row_all
    protected_square = square_all * M151_PROTECTION_NUMERATOR // M151_PROTECTION_DENOMINATOR
    protected_row = row_all * M151_PROTECTION_NUMERATOR // M151_PROTECTION_DENOMINATOR
    terminal_covariance_minimum = 2 * square_f64_per_layer
    terminal_mean_minimum = row_f64_per_layer
    return {
        "budget": BUDGET,
        "m151_m179_no_credit_partial": M151_M179_NO_CREDIT_PARTIAL,
        "strict_headroom": STRICT_HEADROOM,
        "f64_square_per_source_layer": square_f64_per_layer,
        "f64_row_per_source_layer": row_f64_per_layer,
        "rankone_B_raw_31_layers": square_all,
        "rankone_a_raw_31_layers": row_all,
        "rankone_raw_minimum": raw_minimum,
        "rankone_raw_excess_over_headroom": raw_minimum - STRICT_HEADROOM,
        "rankone_B_protected_31_layers": protected_square,
        "rankone_a_protected_31_layers": protected_row,
        "rankone_protected_minimum": protected_square + protected_row,
        "rankone_protected_excess_over_headroom": protected_square + protected_row - STRICT_HEADROOM,
        "M151_booked_protected_source_emission": 2_595_389_440,
        "terminal_background_matmul_floor": terminal_covariance_minimum + terminal_mean_minimum,
        "rankone_plus_terminal_raw_excess": raw_minimum
        + terminal_covariance_minimum
        + terminal_mean_minimum
        - STRICT_HEADROOM,
        "one_B_is_additive_without_proved_replacement": True,
        "native_replacement_proved": False,
        "disposition": "KILLED_M204_ARITHMETIC_IDENTICAL_M151_REPLACEMENT_CLAIM",
    }
