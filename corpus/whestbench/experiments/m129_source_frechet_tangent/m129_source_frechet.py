"""Generated-only Frechet tangent reference for the M122/M126 source.

The module differentiates the nonzero-mean Hermite bridge, its tree source,
all repeated-index collision strata through order four, and the linear
Hutchinson contractions used by M126.  It is deliberately a small-width
algebra oracle.  It contains no model, scorer, benchmark, target, or outcome
access.

The new fourth-order ``[2,1,1]`` defect is represented as ``A[i,j,k]``, where
``i`` is the repeated source label and the singleton slots ``j,k`` are
symmetric.  Its dense transport is only a reference; its probe transport is
``O(n^3)`` per probe and never materializes an ``n^4`` tensor.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import numpy as np


_ROOT = Path(__file__).resolve().parents[1]
for _relative in (
    "m122_nonzero_bridge_theory",
    "m126_repeated_output_source_contraction",
):
    _path = str(_ROOT / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m122_nonzero_bridge import (  # noqa: E402
    NonzeroMeanBridgeState,
    build_state,
    power_hermite_coefficient,
    probabilists_hermite,
    rectified_power_moment,
)


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _pdf(value: float) -> float:
    return _INV_SQRT_2PI * math.exp(-0.5 * value * value)


def power_hermite_coefficient_dot(
    alpha: float,
    sigma: float,
    power: int,
    degree: int,
    alpha_dot: float,
    sigma_dot: float,
) -> tuple[float, float]:
    """Exact directional derivative of ``E[Y^p He_q(G)]``.

    Here ``Y=sigma*(alpha+G)_+``.  The alpha derivative is evaluated from the
    truncated-power identity, including the distributional branch above the
    polynomial degree; no numerical derivative is used.
    """

    value = power_hermite_coefficient(alpha, sigma, power, degree)
    if degree <= power:
        remaining = power - degree
        falling = math.factorial(power) / math.factorial(remaining)
        if remaining == 0:
            alpha_derivative = sigma**power * falling * _pdf(alpha)
        else:
            alpha_derivative = (
                sigma**power
                * falling
                * remaining
                * rectified_power_moment(alpha, remaining - 1)
            )
    else:
        kink_order = degree - power - 1
        alpha_derivative = (
            sigma**power
            * math.factorial(power)
            * ((-1.0) ** (kink_order + 1))
            * probabilists_hermite(kink_order + 1, alpha)
            * _pdf(alpha)
        )
    sigma_derivative = power * value / sigma
    return value, alpha_derivative * alpha_dot + sigma_derivative * sigma_dot


def _pair_sum_dot(
    alpha_i: float,
    sigma_i: float,
    power_i: int,
    alpha_j: float,
    sigma_j: float,
    power_j: int,
    rho: float,
    alpha_i_dot: float,
    sigma_i_dot: float,
    alpha_j_dot: float,
    sigma_j_dot: float,
    rho_dot: float,
    terms: int,
) -> tuple[float, float]:
    value_terms: list[float] = []
    dot_terms: list[float] = []
    for degree in range(terms):
        hi, dhi = power_hermite_coefficient_dot(
            alpha_i, sigma_i, power_i, degree, alpha_i_dot, sigma_i_dot
        )
        hj, dhj = power_hermite_coefficient_dot(
            alpha_j, sigma_j, power_j, degree, alpha_j_dot, sigma_j_dot
        )
        factorial = math.factorial(degree)
        rho_power = rho**degree
        rho_power_dot = (
            0.0 if degree == 0 else degree * rho ** (degree - 1) * rho_dot
        )
        value_terms.append(hi * hj * rho_power / factorial)
        dot_terms.append(
            ((dhi * hj + hi * dhj) * rho_power + hi * hj * rho_power_dot)
            / factorial
        )
    return math.fsum(value_terms), math.fsum(dot_terms)


def pair_raw_moment_series_dot(
    alpha_i: float,
    sigma_i: float,
    power_i: int,
    alpha_j: float,
    sigma_j: float,
    power_j: int,
    rho: float,
    alpha_i_dot: float,
    sigma_i_dot: float,
    alpha_j_dot: float,
    sigma_j_dot: float,
    rho_dot: float,
    *,
    terms: int = 64,
    tolerance: float = 5.0e-9,
) -> tuple[float, float]:
    """Certified pair Hermite series and its exact directional derivative."""

    if terms < 24 or abs(rho) > 0.80 or not math.isfinite(rho):
        raise ValueError("uncertified pair-series request")
    fine = _pair_sum_dot(
        alpha_i,
        sigma_i,
        power_i,
        alpha_j,
        sigma_j,
        power_j,
        rho,
        alpha_i_dot,
        sigma_i_dot,
        alpha_j_dot,
        sigma_j_dot,
        rho_dot,
        terms,
    )
    coarse = _pair_sum_dot(
        alpha_i,
        sigma_i,
        power_i,
        alpha_j,
        sigma_j,
        power_j,
        rho,
        alpha_i_dot,
        sigma_i_dot,
        alpha_j_dot,
        sigma_j_dot,
        rho_dot,
        terms - 12,
    )
    for exact, truncated in zip(fine, coarse):
        if not math.isfinite(exact) or abs(exact - truncated) > tolerance * (
            1.0 + abs(exact)
        ):
            raise ValueError("pair Hermite value/tangent tail did not certify")
    return fine


def _power_and_dot(base: float, exponent: int, base_dot: float) -> tuple[float, float]:
    value = base**exponent
    derivative = 0.0 if exponent == 0 else exponent * base ** (exponent - 1) * base_dot
    return value, derivative


def _triple_sum_dot(
    alpha: np.ndarray,
    sigma: np.ndarray,
    powers: tuple[int, int, int],
    correlation: np.ndarray,
    alpha_dot: np.ndarray,
    sigma_dot: np.ndarray,
    correlation_dot: np.ndarray,
    terms: int,
) -> tuple[float, float]:
    coefficients: list[list[tuple[float, float]]] = []
    for node in range(3):
        coefficients.append(
            [
                power_hermite_coefficient_dot(
                    float(alpha[node]),
                    float(sigma[node]),
                    powers[node],
                    degree,
                    float(alpha_dot[node]),
                    float(sigma_dot[node]),
                )
                for degree in range(terms)
            ]
        )
    rho01, rho02, rho12 = (
        float(correlation[0, 1]),
        float(correlation[0, 2]),
        float(correlation[1, 2]),
    )
    drho01, drho02, drho12 = (
        float(correlation_dot[0, 1]),
        float(correlation_dot[0, 2]),
        float(correlation_dot[1, 2]),
    )
    values: list[float] = []
    dots: list[float] = []
    for degree0 in range(terms):
        h0, dh0 = coefficients[0][degree0]
        for degree1 in range(terms):
            h1, dh1 = coefficients[1][degree1]
            numerator = degree0 + degree1
            for degree2 in range(terms):
                if (numerator + degree2) % 2:
                    continue
                r01 = (degree0 + degree1 - degree2) // 2
                r02 = (degree0 + degree2 - degree1) // 2
                r12 = (degree1 + degree2 - degree0) // 2
                if min(r01, r02, r12) < 0:
                    continue
                h2, dh2 = coefficients[2][degree2]
                p01, dp01 = _power_and_dot(rho01, r01, drho01)
                p02, dp02 = _power_and_dot(rho02, r02, drho02)
                p12, dp12 = _power_and_dot(rho12, r12, drho12)
                denominator = (
                    math.factorial(r01)
                    * math.factorial(r02)
                    * math.factorial(r12)
                )
                hproduct = h0 * h1 * h2
                pproduct = p01 * p02 * p12
                values.append(hproduct * pproduct / denominator)
                hproduct_dot = dh0 * h1 * h2 + h0 * dh1 * h2 + h0 * h1 * dh2
                pproduct_dot = (
                    dp01 * p02 * p12 + p01 * dp02 * p12 + p01 * p02 * dp12
                )
                dots.append(
                    (hproduct_dot * pproduct + hproduct * pproduct_dot) / denominator
                )
    return math.fsum(values), math.fsum(dots)


def triple_raw_moment_series_dot(
    alpha: np.ndarray,
    sigma: np.ndarray,
    powers: tuple[int, int, int],
    correlation: np.ndarray,
    alpha_dot: np.ndarray,
    sigma_dot: np.ndarray,
    correlation_dot: np.ndarray,
    *,
    terms: int = 24,
    tolerance: float = 2.0e-8,
) -> tuple[float, float]:
    """Certified three-node ``[2,1,1]`` series and Frechet tangent."""

    arrays = tuple(
        np.asarray(item, dtype=np.float64)
        for item in (alpha, sigma, correlation, alpha_dot, sigma_dot, correlation_dot)
    )
    alpha, sigma, correlation, alpha_dot, sigma_dot, correlation_dot = arrays
    if (
        alpha.shape != (3,)
        or sigma.shape != (3,)
        or correlation.shape != (3, 3)
        or alpha_dot.shape != (3,)
        or sigma_dot.shape != (3,)
        or correlation_dot.shape != (3, 3)
        or terms < 12
    ):
        raise ValueError("triple value/tangent shape mismatch")
    if np.any(np.abs(correlation[np.triu_indices(3, 1)]) > 0.80):
        raise ValueError("uncertified triple-series request")
    fine = _triple_sum_dot(
        alpha,
        sigma,
        powers,
        correlation,
        alpha_dot,
        sigma_dot,
        correlation_dot,
        terms,
    )
    coarse = _triple_sum_dot(
        alpha,
        sigma,
        powers,
        correlation,
        alpha_dot,
        sigma_dot,
        correlation_dot,
        terms - 6,
    )
    for exact, truncated in zip(fine, coarse):
        if not math.isfinite(exact) or abs(exact - truncated) > tolerance * (
            1.0 + abs(exact)
        ):
            raise ValueError("triple Hermite value/tangent tail did not certify")
    return fine


@dataclass(frozen=True)
class BridgeStateFrechet:
    state: NonzeroMeanBridgeState
    mean_dot: np.ndarray
    covariance_dot: np.ndarray
    sigma_dot: np.ndarray
    alpha_dot: np.ndarray
    relu_mean_dot: np.ndarray
    relu_scale_dot: np.ndarray
    correlation_dot: np.ndarray
    bridge_dot: np.ndarray
    gamma2_dot: np.ndarray
    gamma3_dot: np.ndarray


def build_state_frechet(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    *,
    pair_terms: int = 64,
) -> BridgeStateFrechet:
    """Build the exact forward directional derivative of the M122 state."""

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    if mean_dot.shape != mean.shape or covariance_dot.shape != covariance.shape:
        raise ValueError("state tangent shape mismatch")
    if not np.array_equal(covariance_dot, covariance_dot.T):
        raise ValueError("covariance tangent must be exactly symmetric")
    state = build_state(mean, covariance, pair_terms=pair_terms)
    sigma_dot = np.diag(covariance_dot) / (2.0 * state.sigma)
    alpha_dot = mean_dot / state.sigma - state.alpha * sigma_dot / state.sigma
    scale_rate = sigma_dot / state.sigma
    correlation_dot = (
        covariance_dot / np.outer(state.sigma, state.sigma)
        - state.correlation * (scale_rate[:, None] + scale_rate[None, :])
    )
    correlation_dot = 0.5 * (correlation_dot + correlation_dot.T)
    np.fill_diagonal(correlation_dot, 0.0)

    n = mean.size
    relu_mean_dot = np.empty(n, dtype=np.float64)
    second_dot = np.empty(n, dtype=np.float64)
    h1 = np.empty(n, dtype=np.float64)
    h2 = np.empty(n, dtype=np.float64)
    h3 = np.empty(n, dtype=np.float64)
    h1_dot = np.empty(n, dtype=np.float64)
    h2_dot = np.empty(n, dtype=np.float64)
    h3_dot = np.empty(n, dtype=np.float64)
    for index in range(n):
        arguments = (
            float(state.alpha[index]),
            float(state.sigma[index]),
            float(alpha_dot[index]),
            float(sigma_dot[index]),
        )
        _, relu_mean_dot[index] = power_hermite_coefficient_dot(
            arguments[0], arguments[1], 1, 0, arguments[2], arguments[3]
        )
        _, second_dot[index] = power_hermite_coefficient_dot(
            arguments[0], arguments[1], 2, 0, arguments[2], arguments[3]
        )
        h1[index], h1_dot[index] = power_hermite_coefficient_dot(
            arguments[0], arguments[1], 1, 1, arguments[2], arguments[3]
        )
        h2[index], h2_dot[index] = power_hermite_coefficient_dot(
            arguments[0], arguments[1], 1, 2, arguments[2], arguments[3]
        )
        h3[index], h3_dot[index] = power_hermite_coefficient_dot(
            arguments[0], arguments[1], 1, 3, arguments[2], arguments[3]
        )
    variance_dot = second_dot - 2.0 * state.relu_mean * relu_mean_dot
    relu_scale_dot = variance_dot / (2.0 * state.relu_scale)

    bridge_dot = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            raw, raw_dot = pair_raw_moment_series_dot(
                float(state.alpha[i]),
                float(state.sigma[i]),
                1,
                float(state.alpha[j]),
                float(state.sigma[j]),
                1,
                float(state.correlation[i, j]),
                float(alpha_dot[i]),
                float(sigma_dot[i]),
                float(alpha_dot[j]),
                float(sigma_dot[j]),
                float(correlation_dot[i, j]),
                terms=pair_terms,
            )
            centered = raw - state.relu_mean[i] * state.relu_mean[j]
            centered_dot = (
                raw_dot
                - relu_mean_dot[i] * state.relu_mean[j]
                - state.relu_mean[i] * relu_mean_dot[j]
            )
            denominator = state.relu_scale[i] * state.relu_scale[j]
            value_dot = centered_dot / denominator - state.bridge[i, j] * (
                relu_scale_dot[i] / state.relu_scale[i]
                + relu_scale_dot[j] / state.relu_scale[j]
            )
            bridge_dot[i, j] = bridge_dot[j, i] = value_dot

    gamma2_dot = (
        h2_dot * state.relu_scale + h2 * relu_scale_dot
    ) / (h1 * h1) - 2.0 * h2 * state.relu_scale * h1_dot / (h1**3)
    gamma3_dot = (
        h3_dot * state.relu_scale**2
        + 2.0 * h3 * state.relu_scale * relu_scale_dot
    ) / (h1**3) - 3.0 * h3 * state.relu_scale**2 * h1_dot / (h1**4)
    return BridgeStateFrechet(
        state,
        mean_dot,
        covariance_dot,
        sigma_dot,
        alpha_dot,
        relu_mean_dot,
        relu_scale_dot,
        correlation_dot,
        bridge_dot,
        gamma2_dot,
        gamma3_dot,
    )


def _set_partitions(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, ...], ...]]:
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in _set_partitions(rest):
        yield ((first,),) + partition
        for position in range(len(partition)):
            yield (
                partition[:position]
                + (partition[position] + (first,),)
                + partition[position + 1 :]
            )


def _raw_for_labels_dot(
    tangent: BridgeStateFrechet, labels: tuple[int, ...], *, terms: int
) -> tuple[float, float]:
    if not labels:
        return 1.0, 0.0
    state = tangent.state
    unique = tuple(sorted(set(labels)))
    counts = tuple(labels.count(index) for index in unique)
    if len(unique) == 1:
        index = unique[0]
        return power_hermite_coefficient_dot(
            float(state.alpha[index]),
            float(state.sigma[index]),
            len(labels),
            0,
            float(tangent.alpha_dot[index]),
            float(tangent.sigma_dot[index]),
        )
    if len(unique) == 2:
        i, j = unique
        return pair_raw_moment_series_dot(
            float(state.alpha[i]),
            float(state.sigma[i]),
            counts[0],
            float(state.alpha[j]),
            float(state.sigma[j]),
            counts[1],
            float(state.correlation[i, j]),
            float(tangent.alpha_dot[i]),
            float(tangent.sigma_dot[i]),
            float(tangent.alpha_dot[j]),
            float(tangent.sigma_dot[j]),
            float(tangent.correlation_dot[i, j]),
            terms=max(terms, 32),
        )
    if len(unique) == 3:
        selected = np.asarray(unique, dtype=int)
        return triple_raw_moment_series_dot(
            state.alpha[selected],
            state.sigma[selected],
            counts,
            state.correlation[np.ix_(selected, selected)],
            tangent.alpha_dot[selected],
            tangent.sigma_dot[selected],
            tangent.correlation_dot[np.ix_(selected, selected)],
            terms=terms,
        )
    raise ValueError("collision reference needs at most three distinct labels")


def exact_collision_cumulant_dot(
    tangent: BridgeStateFrechet, labels: tuple[int, ...], *, terms: int = 24
) -> tuple[float, float]:
    """Exact connected collision cumulant and directional derivative."""

    if len(labels) not in (3, 4) or len(set(labels)) == len(labels):
        raise ValueError("labels must be a repeated order-three/four tuple")
    value = 0.0
    derivative = 0.0
    slots = tuple(range(len(labels)))
    for partition in _set_partitions(slots):
        coefficient = math.factorial(len(partition) - 1) * (
            (-1.0) ** (len(partition) - 1)
        )
        factors = [
            _raw_for_labels_dot(
                tangent, tuple(labels[position] for position in block), terms=terms
            )
            for block in partition
        ]
        primal_product = math.prod(item[0] for item in factors)
        tangent_product = 0.0
        for chosen, (_, factor_dot) in enumerate(factors):
            tangent_product += factor_dot * math.prod(
                factor[0]
                for position, factor in enumerate(factors)
                if position != chosen
            )
        value += coefficient * primal_product
        derivative += coefficient * tangent_product
    return value, derivative


@dataclass(frozen=True)
class Dual:
    value: Any
    tangent: Any

    __array_priority__ = 1000

    def __add__(self, other: Any) -> "Dual":
        other = as_dual(other)
        return Dual(self.value + other.value, self.tangent + other.tangent)

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.value, -self.tangent)

    def __sub__(self, other: Any) -> "Dual":
        return self + (-as_dual(other))

    def __rsub__(self, other: Any) -> "Dual":
        return as_dual(other) - self

    def __mul__(self, other: Any) -> "Dual":
        other = as_dual(other)
        return Dual(
            self.value * other.value,
            self.tangent * other.value + self.value * other.tangent,
        )

    __rmul__ = __mul__

    def __matmul__(self, other: Any) -> "Dual":
        other = as_dual(other)
        return Dual(
            self.value @ other.value,
            self.tangent @ other.value + self.value @ other.tangent,
        )

    def __rmatmul__(self, other: Any) -> "Dual":
        return as_dual(other) @ self

    def __pow__(self, power: int) -> "Dual":
        if type(power) is not int or power < 1:
            raise ValueError("Dual supports positive integer powers")
        return Dual(
            self.value**power,
            power * self.value ** (power - 1) * self.tangent,
        )

    def __getitem__(self, key: Any) -> "Dual":
        return Dual(self.value[key], self.tangent[key])

    @property
    def T(self) -> "Dual":
        return Dual(np.asarray(self.value).T, np.asarray(self.tangent).T)

    def reshape(self, *shape: int) -> "Dual":
        return Dual(np.asarray(self.value).reshape(*shape), np.asarray(self.tangent).reshape(*shape))


def as_dual(value: Any, tangent: Any | None = None) -> Dual:
    if isinstance(value, Dual):
        return value
    if tangent is None:
        tangent = np.zeros_like(value, dtype=np.float64) if isinstance(value, np.ndarray) else 0.0
    return Dual(value, tangent)


def dual_einsum(subscripts: str, *operands: Dual) -> Dual:
    values = [operand.value for operand in operands]
    primal = np.einsum(subscripts, *values, optimize=True)
    pieces = []
    for chosen, operand in enumerate(operands):
        replaced = list(values)
        replaced[chosen] = operand.tangent
        pieces.append(np.einsum(subscripts, *replaced, optimize=True))
    return Dual(primal, sum(pieces))


def dual_diag(value: Dual) -> Dual:
    return Dual(np.diag(value.value).copy(), np.diag(value.tangent).copy())


def _tree_entry_dot(
    tangent: BridgeStateFrechet, labels: tuple[int, ...]
) -> tuple[float, float]:
    state = tangent.state
    scale = as_dual(state.relu_scale, tangent.relu_scale_dot)
    q = as_dual(state.bridge, tangent.bridge_dot)
    g2 = as_dual(state.gamma2, tangent.gamma2_dot)
    g3 = as_dual(state.gamma3, tangent.gamma3_dot)
    scale_product = as_dual(1.0)
    for label in labels:
        scale_product *= scale[label]
    if len(labels) == 3:
        total = as_dual(0.0)
        for centre in range(3):
            root = labels[centre]
            leaves = [labels[position] for position in range(3) if position != centre]
            total += g2[root] * q[root, leaves[0]] * q[root, leaves[1]]
    elif len(labels) == 4:
        total = as_dual(0.0)
        for centre in range(4):
            root = labels[centre]
            star = g3[root]
            for position in range(4):
                if position != centre:
                    star *= q[root, labels[position]]
            total += star
        path = as_dual(0.0)
        for permutation in itertools.permutations(range(4)):
            a, b, c, d = (labels[position] for position in permutation)
            path += g2[b] * g2[c] * q[a, b] * q[b, c] * q[c, d]
        total += 0.5 * path
    else:
        raise ValueError("tree entry requires order three or four")
    answer = scale_product * total
    return float(answer.value), float(answer.tangent)


@dataclass(frozen=True)
class CollisionDefects:
    diagonal3: Dual
    majority3: Dual
    diagonal4: Dual
    majority4: Dual
    paired4: Dual
    collision211: Dual


def build_collision_defects(
    tangent: BridgeStateFrechet, *, terms: int = 24
) -> CollisionDefects:
    """Build every exact repeated-index defect, including ``[2,1,1]``.

    This is a width-at-most-eight oracle.  The ``collision211`` tensor has
    shape ``(n,n,n)``, is symmetric in its last two slots, and is zero unless
    all three represented labels are distinct.
    """

    n = tangent.state.mean.size
    arrays = {
        "d3": [np.zeros(n), np.zeros(n)],
        "e3": [np.zeros((n, n)), np.zeros((n, n))],
        "d4": [np.zeros(n), np.zeros(n)],
        "e31": [np.zeros((n, n)), np.zeros((n, n))],
        "e22": [np.zeros((n, n)), np.zeros((n, n))],
        "a211": [np.zeros((n, n, n)), np.zeros((n, n, n))],
    }

    def defect(labels: tuple[int, ...]) -> tuple[float, float]:
        exact = exact_collision_cumulant_dot(tangent, labels, terms=terms)
        tree = _tree_entry_dot(tangent, labels)
        return exact[0] - tree[0], exact[1] - tree[1]

    for i in range(n):
        for slot, value in enumerate(defect((i, i, i))):
            arrays["d3"][slot][i] = value
        for slot, value in enumerate(defect((i, i, i, i))):
            arrays["d4"][slot][i] = value
        for j in range(n):
            if i == j:
                continue
            for slot, value in enumerate(defect((i, i, j))):
                arrays["e3"][slot][i, j] = value
            for slot, value in enumerate(defect((i, i, i, j))):
                arrays["e31"][slot][i, j] = value
        for j in range(i + 1, n):
            for slot, value in enumerate(defect((i, i, j, j))):
                arrays["e22"][slot][i, j] = arrays["e22"][slot][j, i] = value
        others = [index for index in range(n) if index != i]
        for j_position, j in enumerate(others):
            for k in others[j_position + 1 :]:
                for slot, value in enumerate(defect((i, i, j, k))):
                    arrays["a211"][slot][i, j, k] = value
                    arrays["a211"][slot][i, k, j] = value

    return CollisionDefects(
        Dual(*arrays["d3"]),
        Dual(*arrays["e3"]),
        Dual(*arrays["d4"]),
        Dual(*arrays["e31"]),
        Dual(*arrays["e22"]),
        Dual(*arrays["a211"]),
    )


def _repeated_dual(k3_aab: Dual, k4_aaab: Dual, k4_aabb: Dual) -> dict[str, Dual]:
    return {
        "k3_aaa": dual_diag(k3_aab),
        "k3_aab": k3_aab,
        "k4_aaaa": dual_diag(k4_aaab),
        "k4_aaab": k4_aaab,
        "k4_aabb": k4_aabb,
    }


def _path_hard_dual(q: Dual, gamma2: Dual, weight: Dual) -> dict[str, Dual]:
    propagated = q @ weight
    weighted = gamma2[:, None] * propagated
    identity_self = (weighted * weighted).T @ (weight * weight)
    pair_feature = weighted * weight
    identity_cross = pair_feature.T @ pair_feature
    full_self = dual_einsum(
        "ia,ib,ij,ja,jb->ab", weighted, weight, q, weighted, weight
    )
    full_cross = dual_einsum(
        "ia,ib,ij,jb,ja->ab", weighted, weight, q, weighted, weight
    )
    return {
        "identity_self": identity_self,
        "identity_cross": identity_cross,
        "residual_self": full_self - identity_self,
        "residual_cross": full_cross - identity_cross,
        "full_self": full_self,
        "full_cross": full_cross,
    }


def tree_repeated_dual(
    q: np.ndarray,
    gamma2: np.ndarray,
    gamma3: np.ndarray,
    weight: np.ndarray,
    q_dot: np.ndarray,
    gamma2_dot: np.ndarray,
    gamma3_dot: np.ndarray,
    weight_dot: np.ndarray | None = None,
) -> dict[str, Dual]:
    """Exact product-rule derivative of every M126 tree table."""

    if weight_dot is None:
        weight_dot = np.zeros_like(weight)
    qd = Dual(np.asarray(q), np.asarray(q_dot))
    g2 = Dual(np.asarray(gamma2), np.asarray(gamma2_dot))
    g3 = Dual(np.asarray(gamma3), np.asarray(gamma3_dot))
    w = Dual(np.asarray(weight), np.asarray(weight_dot))
    propagated = qd @ w

    k3_aab = (
        2.0 * (g2[:, None] * w * propagated).T @ propagated
        + (g2[:, None] * propagated * propagated).T @ w
    )
    star_aaab = (
        3.0 * (g3[:, None] * w * propagated * propagated).T @ propagated
        + (g3[:, None] * propagated**3).T @ w
    )
    star_half = (g3[:, None] * w * propagated).T @ (propagated * propagated)
    star_aabb = 2.0 * (star_half + star_half.T)

    pair_diagonal = g2[:, None] * propagated * w
    central_pull = qd @ pair_diagonal
    endpoint = (propagated.T @ (g2[:, None] * w * central_pull)).T
    internal = (w.T @ (g2[:, None] * propagated * central_pull)).T
    path_aaab = 6.0 * (endpoint + internal)
    block = pair_diagonal.T @ central_pull
    hard = _path_hard_dual(qd, g2, w)
    path_aabb = (
        4.0 * block
        + 2.0 * (hard["full_self"] + hard["full_self"].T)
        + 4.0 * hard["full_cross"]
    )
    return _repeated_dual(k3_aab, star_aaab + path_aaab, star_aabb + path_aabb)


def path_probe_dual(
    q: np.ndarray,
    gamma2: np.ndarray,
    weight: np.ndarray,
    probe: np.ndarray,
    q_dot: np.ndarray,
    gamma2_dot: np.ndarray,
    weight_dot: np.ndarray | None = None,
) -> dict[str, Dual]:
    """M126 hard-path probe and derivative with common-random ownership."""

    if weight_dot is None:
        weight_dot = np.zeros_like(weight)
    qd = Dual(np.asarray(q), np.asarray(q_dot))
    g2 = Dual(np.asarray(gamma2), np.asarray(gamma2_dot))
    w = Dual(np.asarray(weight), np.asarray(weight_dot))
    z = as_dual(np.asarray(probe))
    propagated = qd @ w
    residual_probe = (qd - np.eye(q.shape[0])) @ z
    m_probe = propagated.T @ ((g2 * z)[:, None] * w)
    m_residual = propagated.T @ ((g2 * residual_probe)[:, None] * w)
    residual_self = m_probe * m_residual
    residual_cross = m_probe * m_residual.T
    assembled = 2.0 * (residual_self + residual_self.T) + 2.0 * (
        residual_cross + residual_cross.T
    )
    return {
        "residual_self": residual_self,
        "residual_cross": residual_cross,
        "aabb_assembled": assembled,
    }


def collision22_probe_dual(
    paired4: np.ndarray,
    weight: np.ndarray,
    probe: np.ndarray,
    paired4_dot: np.ndarray,
) -> Dual:
    """Linear hard ``[2,2]`` probe and its same-probe tangent."""

    defect = Dual(np.asarray(paired4), np.asarray(paired4_dot))
    w = as_dual(np.asarray(weight))
    z = as_dual(np.asarray(probe))
    m_probe = w.T @ (z[:, None] * w)
    m_defect = w.T @ ((defect @ z)[:, None] * w)
    return 2.0 * m_probe * m_defect


def _collision22_hard_dual(paired4: Dual, weight: Dual) -> Dual:
    return 2.0 * dual_einsum(
        "ia,ib,ij,ja,jb->ab", weight, weight, paired4, weight, weight
    )


def collision_repeated_dual(
    defects: CollisionDefects, weight: np.ndarray
) -> dict[str, Dual]:
    """Product-rule sparse collision tables excluding ``[2,1,1]``."""

    w = as_dual(np.asarray(weight))
    square = w * w
    cube = square * w
    majority3_weight = defects.majority3 @ w
    k3_aab = (
        (defects.diagonal3[:, None] * square).T @ w
        + square.T @ majority3_weight
        + 2.0 * (w * majority3_weight).T @ w
    )
    majority4_weight = defects.majority4 @ w
    paired_square = defects.paired4 @ square
    k4_aaab = (
        (defects.diagonal4[:, None] * cube).T @ w
        + cube.T @ majority4_weight
        + 3.0 * (square * majority4_weight).T @ w
        + 3.0 * (w * paired_square).T @ w
    )
    majority_aabb = (w * majority4_weight).T @ square
    k4_aabb = (
        (defects.diagonal4[:, None] * square).T @ square
        + 2.0 * (majority_aabb + majority_aabb.T)
        + square.T @ paired_square
        + _collision22_hard_dual(defects.paired4, w)
    )
    return _repeated_dual(k3_aab, k4_aaab, k4_aabb)


def collision211_probe_dual(
    collision211: np.ndarray,
    weight: np.ndarray,
    probe: np.ndarray,
    collision211_dot: np.ndarray,
) -> dict[str, Dual]:
    """Unbiased hollow-quadratic probe for the full ``[2,1,1]`` defect.

    ``A[i,j,k]`` is symmetric in ``j,k`` and hollow whenever any represented
    labels coincide.  With ``u=W.T@z`` and ``t_i=sum_jk A_ijk z_j z_k``, the
    identity ``E[t_i u_a u_b]/2=S_i(a,b)`` contracts both singleton legs at
    once.  The same probe is used for ``A`` and ``A_dot`` so differentiation
    commutes with expectation.  There is one packed tensor quadratic and one
    square product for each of primal and tangent -- no ``n^4`` object.
    """

    a = np.asarray(collision211, dtype=np.float64)
    adot = np.asarray(collision211_dot, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)
    z = np.asarray(probe, dtype=np.float64)
    n, outputs = w.shape
    if a.shape != (n, n, n) or adot.shape != a.shape or z.shape != (n,):
        raise ValueError("[2,1,1] probe shape mismatch")
    if not np.allclose(a, a.swapaxes(1, 2), rtol=0.0, atol=2.0e-12):
        raise ValueError("[2,1,1] singleton slots must be symmetric")
    if not np.allclose(adot, adot.swapaxes(1, 2), rtol=0.0, atol=2.0e-12):
        raise ValueError("[2,1,1] tangent singleton slots must be symmetric")
    forbidden = np.zeros_like(a, dtype=bool)
    for i in range(n):
        forbidden[i, i, :] = True
        forbidden[i, :, i] = True
        forbidden[i, np.arange(n), np.arange(n)] = True
    if np.any(a[forbidden] != 0.0) or np.any(adot[forbidden] != 0.0):
        raise ValueError("[2,1,1] diagonal leakage biases the quadratic probe")

    collision = Dual(a, adot)
    zd = as_dual(z)
    t = dual_einsum("ijk,j,k->i", collision, zd, zd)
    projection = z @ w
    wd = as_dual(w)
    gram = wd.T @ (t[:, None] * wd)
    diagonal = dual_diag(gram)
    uaub = projection[:, None] * projection[None, :]
    aaab = 1.5 * (
        gram * projection[:, None] ** 2
        + diagonal[:, None] * uaub
    )
    aabb = (
        0.5
        * (
            diagonal[:, None] * projection[None, :] ** 2
            + diagonal[None, :] * projection[:, None] ** 2
        )
        + 2.0 * gram * uaub
    )
    return {
        "k4_aaaa": dual_diag(aaab),
        "k4_aaab": aaab,
        "k4_aabb": aabb,
    }


def collision211_dense_dual(
    collision211: np.ndarray,
    weight: np.ndarray,
    collision211_dot: np.ndarray,
) -> dict[str, Dual]:
    """Small-width ``n^4`` oracle for the ``[2,1,1]`` transport."""

    a = np.asarray(collision211, dtype=np.float64)
    adot = np.asarray(collision211_dot, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)
    n, outputs = w.shape
    if a.shape != (n, n, n) or adot.shape != a.shape:
        raise ValueError("[2,1,1] dense shape mismatch")
    tensor = np.zeros((n, n, n, n), dtype=np.float64)
    tensor_dot = np.zeros_like(tensor)
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                if len({i, j, k}) != 3:
                    continue
                for permutation in set(itertools.permutations((i, i, j, k))):
                    tensor[permutation] = a[i, j, k]
                    tensor_dot[permutation] = adot[i, j, k]
    transported = dual_einsum(
        "ijkl,ia,jb,kc,ld->abcd",
        Dual(tensor, tensor_dot),
        as_dual(w),
        as_dual(w),
        as_dual(w),
        as_dual(w),
    )
    return {
        "k4_aaaa": Dual(
            np.asarray([transported.value[a_, a_, a_, a_] for a_ in range(outputs)]),
            np.asarray([transported.tangent[a_, a_, a_, a_] for a_ in range(outputs)]),
        ),
        "k4_aaab": Dual(
            np.asarray(
                [
                    [transported.value[a_, a_, a_, b_] for b_ in range(outputs)]
                    for a_ in range(outputs)
                ]
            ),
            np.asarray(
                [
                    [transported.tangent[a_, a_, a_, b_] for b_ in range(outputs)]
                    for a_ in range(outputs)
                ]
            ),
        ),
        "k4_aabb": Dual(
            np.asarray(
                [
                    [transported.value[a_, a_, b_, b_] for b_ in range(outputs)]
                    for a_ in range(outputs)
                ]
            ),
            np.asarray(
                [
                    [transported.tangent[a_, a_, b_, b_] for b_ in range(outputs)]
                    for a_ in range(outputs)
                ]
            ),
        ),
    }


def flopscope_cost_envelope(
    probes: int,
    *,
    width: int = 256,
    layers: int = 31,
    dense_dtype: str = "float32",
    safety_factor: float = 1.25,
) -> dict[str, int | float | bool | str]:
    """Complete declared lower/upper envelope for M126+M128 ``D source``.

    Lower bound charges only dense calls plus the already protected M125b
    carrier and M128 second affine tangent.  The conservative upper bound adds
    all declared f64 scalar/copy reserves and applies the source safety factor
    once.  Mixed mode means dense GEMMs are f32 while Hermite/state arithmetic
    and reserves remain f64.
    """

    if probes < 0 or type(probes) is not int:
        raise ValueError("probes must be a nonnegative integer")
    if dense_dtype not in {"float32", "float64"}:
        raise ValueError("dense_dtype must be float32 or float64")
    square_f32 = 2 * width**3 - width**2
    square = square_f32 if dense_dtype == "float32" else 2 * square_f32

    # Exact M126 primal: 12 tree + 12 sparse collision calls.  Every output
    # depending on state requires at least one tangent call.  A product with
    # two moving matrix operands requires two; the enumerated tree/sparse
    # schedule caps the tangent at 36 calls.
    exact_primal_calls = 24
    exact_tangent_calls_lower = 24
    exact_tangent_calls_upper = 36

    # Per probe: existing path is 2 primal + 4 tangent calls; [2,2] is
    # 2 primal + 1 tangent.  The hollow [2,1,1] estimator uses two packed
    # tensor reductions, two square calls, and one shared GEMV.
    existing_probe_calls = 9 * probes
    calls_lower = (
        exact_primal_calls
        + exact_tangent_calls_lower
        + existing_probe_calls
    )
    calls_upper = (
        exact_primal_calls
        + exact_tangent_calls_upper
        + existing_probe_calls
    )
    packed_pairs = math.comb(width, 2)
    packed_tall_matvec_f32 = 2 * width * packed_pairs - width
    gemv_f32 = 2 * width**2 - width
    collision211_lower_f32 = (
        2 * packed_tall_matvec_f32 + 2 * square_f32 + gemv_f32
    )
    collision211_allowance_f32 = 10 * packed_pairs + 66 * width**2
    collision211_upper_f32 = collision211_lower_f32 + collision211_allowance_f32
    dtype_rate = 1 if dense_dtype == "float32" else 2
    collision211_lower = dtype_rate * collision211_lower_f32
    collision211_upper = dtype_rate * collision211_upper_f32
    contraction_lower = (
        calls_lower * layers * square
        + probes * layers * collision211_lower
    )
    contraction_upper = (
        calls_upper * layers * square
        + probes * layers * collision211_upper
    )

    m125b_protected_carrier = 12_819_347_280
    second_affine_tangent = layers * 2 * (2 * square_f32)
    protected_carrier = m125b_protected_carrier + second_affine_tangent
    reserves = {
        "analytic_collision_primal_f64": 4_000_000_000,
        "state_and_collision_tangent_f64": 8_000_000_000,
        "second_response_scalars_f64": 1_600_000_000,
        "dual_copies_and_allocations": 3_200_000_000,
    }
    reserve_total = sum(reserves.values())
    lower_total = contraction_lower + protected_carrier
    upper_total = (
        int(math.ceil((contraction_upper + reserve_total) * safety_factor))
        + protected_carrier
    )
    return {
        "probes": probes,
        "width": width,
        "layers": layers,
        "dense_dtype": dense_dtype,
        "square_bill": square,
        "exact_primal_calls_per_layer": exact_primal_calls,
        "exact_tangent_calls_lower_per_layer": exact_tangent_calls_lower,
        "exact_tangent_calls_upper_per_layer": exact_tangent_calls_upper,
        "existing_probe_primal_plus_tangent_calls_per_layer": existing_probe_calls,
        "collision211_lower_bill_per_probe_layer": collision211_lower,
        "collision211_upper_bill_per_probe_layer": collision211_upper,
        "total_calls_lower_per_layer": calls_lower,
        "total_calls_upper_per_layer": calls_upper,
        "dense_contraction_lower": contraction_lower,
        "dense_contraction_upper": contraction_upper,
        "protected_carrier": protected_carrier,
        "declared_upper_reserves": reserve_total,
        "safety_factor": safety_factor,
        "total_lower": lower_total,
        "total_upper": upper_total,
        "strictly_below_100b_even_at_lower_bound": lower_total < 100_000_000_000,
        "co_propagates_without_n4": True,
        "collision211_dense_tensor_required": False,
    }
