"""Generated-only nonzero-mean normal-ordered ReLU bridge reference.

This module is intentionally restricted to small algebra/reference work.  It
defines exact Hermite-series collision strata and a pair-resummed tree source;
it is not a target-width cumulant propagation or a competition entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import itertools
import math

import numpy as np
from numpy.polynomial.hermite import hermgauss


_SQRT_2PI = math.sqrt(2.0 * math.pi)
_INV_SQRT_2PI = 1.0 / _SQRT_2PI
_SERIES_RHO_LIMIT = 0.80
_SCALE_FLOOR = 1.0e-12


class NonzeroBridgeFailClosed(RuntimeError):
    """Raised when a small reference would require an uncertified shortcut."""


def _cdf(value: float) -> float:
    if not math.isfinite(value):
        raise NonzeroBridgeFailClosed("non-finite normal CDF argument")
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def _pdf(value: float) -> float:
    if not math.isfinite(value):
        raise NonzeroBridgeFailClosed("non-finite normal PDF argument")
    return _INV_SQRT_2PI * math.exp(-0.5 * value * value)


def probabilists_hermite(order: int, value: float) -> float:
    """Probabilists' ``He_order`` with no external special-function backend."""
    if order < 0:
        raise ValueError("Hermite order must be nonnegative")
    if order == 0:
        return 1.0
    if order == 1:
        return value
    previous, current = 1.0, value
    for degree in range(1, order):
        previous, current = current, value * current - degree * previous
    return current


def _truncated_normal_moments(alpha: float, maximum: int) -> np.ndarray:
    """Return ``I_k(-alpha)=int_-alpha^inf g^k phi(g) dg`` for ``k<=maximum``."""
    if maximum < 0 or not math.isfinite(alpha):
        raise ValueError("invalid truncated-moment request")
    lower = -alpha
    density = _pdf(alpha)
    values = np.empty(maximum + 1, dtype=np.float64)
    values[0] = _cdf(alpha)
    if maximum:
        values[1] = density
    for degree in range(2, maximum + 1):
        values[degree] = lower ** (degree - 1) * density + (degree - 1) * values[degree - 2]
    return values


def rectified_power_moment(alpha: float, power: int) -> float:
    """Exact ``E[(alpha+G)_+**power]`` for integer ``0<=power<=4``."""
    if power < 0:
        raise ValueError("power must be nonnegative")
    moments = _truncated_normal_moments(alpha, power)
    return math.fsum(math.comb(power, degree) * alpha ** (power - degree) * float(moments[degree]) for degree in range(power + 1))


def power_hermite_coefficient(alpha: float, sigma: float, power: int, degree: int) -> float:
    """Return ``E[Y**power He_degree(G)]`` for ``Y=sigma*(alpha+G)_+``.

    The derivative identity ``E[f He_q]=E[f^(q)]`` makes this exact even for
    the distributional derivatives beyond the ReLU kink.
    """
    if power < 1 or degree < 0 or not math.isfinite(alpha) or not math.isfinite(sigma) or sigma <= 0.0:
        raise ValueError("invalid local Hermite coefficient request")
    factor = sigma ** power
    if degree <= power:
        falling = math.factorial(power) / math.factorial(power - degree)
        return factor * falling * rectified_power_moment(alpha, power - degree)
    derivative_order = degree - power - 1
    return factor * math.factorial(power) * ((-1.0) ** derivative_order) * probabilists_hermite(derivative_order, alpha) * _pdf(alpha)


def local_relu_coefficients(alpha: float, sigma: float) -> tuple[float, float, float]:
    """Return the exact degree-one through degree-three coefficients of ReLU."""
    return tuple(power_hermite_coefficient(alpha, sigma, 1, degree) for degree in (1, 2, 3))  # type: ignore[return-value]


def _checked_correlation(rho: float) -> float:
    rho = float(rho)
    if not math.isfinite(rho) or abs(rho) >= 1.0:
        raise NonzeroBridgeFailClosed("singular or non-finite Gaussian correlation")
    if abs(rho) > _SERIES_RHO_LIMIT:
        raise NonzeroBridgeFailClosed("small Hermite reference refuses a slow near-endpoint pair series")
    return rho


def _series_sum_pair(alpha_i: float, sigma_i: float, power_i: int, alpha_j: float, sigma_j: float, power_j: int, rho: float, terms: int) -> float:
    return math.fsum(
        power_hermite_coefficient(alpha_i, sigma_i, power_i, degree)
        * power_hermite_coefficient(alpha_j, sigma_j, power_j, degree)
        * rho ** degree
        / math.factorial(degree)
        for degree in range(terms)
    )


def pair_raw_moment_series(
    alpha_i: float,
    sigma_i: float,
    power_i: int,
    alpha_j: float,
    sigma_j: float,
    power_j: int,
    rho: float,
    *,
    terms: int = 64,
    tolerance: float = 2.0e-10,
) -> float:
    """Exact signed pair series, evaluated only when its tail check passes."""
    if terms < 24:
        raise ValueError("at least 24 Hermite terms are required for the reference")
    rho = _checked_correlation(rho)
    fine = _series_sum_pair(alpha_i, sigma_i, power_i, alpha_j, sigma_j, power_j, rho, terms)
    coarse = _series_sum_pair(alpha_i, sigma_i, power_i, alpha_j, sigma_j, power_j, rho, terms - 12)
    if not math.isfinite(fine) or abs(fine - coarse) > tolerance * (1.0 + abs(fine)):
        raise NonzeroBridgeFailClosed("bivariate Hermite series tail did not certify")
    return fine


def _triple_raw_sum(alphas: np.ndarray, sigmas: np.ndarray, powers: tuple[int, int, int], correlations: np.ndarray, terms: int) -> float:
    coefficients = [
        [power_hermite_coefficient(float(alphas[node]), float(sigmas[node]), powers[node], degree) for degree in range(terms)]
        for node in range(3)
    ]
    rho01, rho02, rho12 = float(correlations[0, 1]), float(correlations[0, 2]), float(correlations[1, 2])
    total = 0.0
    for degree0 in range(terms):
        h0 = coefficients[0][degree0]
        for degree1 in range(terms):
            numerator = degree0 + degree1
            h01 = h0 * coefficients[1][degree1]
            for degree2 in range(terms):
                if (numerator + degree2) % 2:
                    continue
                r01 = (degree0 + degree1 - degree2) // 2
                r02 = (degree0 + degree2 - degree1) // 2
                r12 = (degree1 + degree2 - degree0) // 2
                if min(r01, r02, r12) < 0:
                    continue
                total += (
                    h01
                    * coefficients[2][degree2]
                    * rho01 ** r01
                    * rho02 ** r02
                    * rho12 ** r12
                    / (math.factorial(r01) * math.factorial(r02) * math.factorial(r12))
                )
    return total


def triple_raw_moment_series(
    alpha: np.ndarray,
    sigma: np.ndarray,
    powers: tuple[int, int, int],
    correlation: np.ndarray,
    *,
    terms: int = 32,
    tolerance: float = 2.0e-9,
) -> float:
    """Exact three-node normal-ordered series for the `(2,1,1)` collision stratum."""
    alpha, sigma, correlation = np.asarray(alpha, dtype=np.float64), np.asarray(sigma, dtype=np.float64), np.asarray(correlation, dtype=np.float64)
    if alpha.shape != (3,) or sigma.shape != (3,) or correlation.shape != (3, 3):
        raise ValueError("triple series shape mismatch")
    if np.any(sigma <= 0.0) or not np.all(np.isfinite(alpha)) or not np.all(np.isfinite(correlation)):
        raise NonzeroBridgeFailClosed("invalid triple Gaussian state")
    if not np.array_equal(correlation, correlation.T) or not np.allclose(np.diag(correlation), 1.0, rtol=0.0, atol=0.0):
        raise NonzeroBridgeFailClosed("triple correlation must be exactly symmetric with unit diagonal")
    if np.any(np.abs(correlation[np.triu_indices(3, 1)]) > _SERIES_RHO_LIMIT):
        raise NonzeroBridgeFailClosed("small triple reference refuses a slow near-endpoint series")
    fine = _triple_raw_sum(alpha, sigma, powers, correlation, terms)
    coarse = _triple_raw_sum(alpha, sigma, powers, correlation, terms - 6)
    if not math.isfinite(fine) or abs(fine - coarse) > tolerance * (1.0 + abs(fine)):
        raise NonzeroBridgeFailClosed("triple Hermite series tail did not certify")
    return fine


def _set_partitions(items: tuple[int, ...]):
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in _set_partitions(rest):
        yield ((first,),) + partition
        for position in range(len(partition)):
            yield partition[:position] + (partition[position] + (first,),) + partition[position + 1 :]


@dataclass(frozen=True)
class NonzeroMeanBridgeState:
    mean: np.ndarray
    covariance: np.ndarray
    sigma: np.ndarray
    alpha: np.ndarray
    relu_mean: np.ndarray
    relu_scale: np.ndarray
    correlation: np.ndarray
    bridge: np.ndarray
    gamma2: np.ndarray
    gamma3: np.ndarray


def build_state(mean: np.ndarray, covariance: np.ndarray, *, pair_terms: int = 64) -> NonzeroMeanBridgeState:
    """Build a fail-closed small state and exact signed pair bridge by series."""
    mean, covariance = np.asarray(mean, dtype=np.float64), np.asarray(covariance, dtype=np.float64)
    if mean.ndim != 1 or covariance.shape != (mean.size, mean.size) or mean.size > 8:
        raise ValueError("the M122 reference accepts only a generated state of width at most eight")
    if not np.array_equal(covariance, covariance.T) or not np.all(np.isfinite(mean)) or not np.all(np.isfinite(covariance)):
        raise NonzeroBridgeFailClosed("state must be finite and exactly symmetric")
    eigen_minimum = float(np.min(np.linalg.eigvalsh(covariance)))
    if not math.isfinite(eigen_minimum) or eigen_minimum <= _SCALE_FLOOR:
        raise NonzeroBridgeFailClosed("Gaussian covariance is not comfortably positive definite")
    sigma = np.sqrt(np.diag(covariance))
    alpha = mean / sigma
    # The diagonal is the defining unit variance of `G`, not an inferred
    # floating-point quantity.  Restoring it exactly prevents an innocuous
    # positive gauge rescaling from tripping the reference's structural check.
    correlation = covariance / np.outer(sigma, sigma)
    correlation = 0.5 * (correlation + correlation.T)
    np.fill_diagonal(correlation, 1.0)
    if np.any(np.abs(correlation[np.triu_indices(mean.size, 1)]) > _SERIES_RHO_LIMIT):
        raise NonzeroBridgeFailClosed("small state has a pair too close to a Gaussian endpoint")
    relu_mean = np.asarray([power_hermite_coefficient(float(a), float(s), 1, 0) for a, s in zip(alpha, sigma)])
    second = np.asarray([power_hermite_coefficient(float(a), float(s), 2, 0) for a, s in zip(alpha, sigma)])
    variance = second - relu_mean * relu_mean
    if np.any(~np.isfinite(variance)) or np.any(variance <= _SCALE_FLOOR):
        raise NonzeroBridgeFailClosed("rectified variance is degenerate")
    relu_scale = np.sqrt(variance)
    bridge = np.eye(mean.size, dtype=np.float64)
    for i in range(mean.size):
        for j in range(i + 1, mean.size):
            raw = pair_raw_moment_series(float(alpha[i]), float(sigma[i]), 1, float(alpha[j]), float(sigma[j]), 1, float(correlation[i, j]), terms=pair_terms)
            value = (raw - relu_mean[i] * relu_mean[j]) / (relu_scale[i] * relu_scale[j])
            if not math.isfinite(value) or abs(value) > 1.0 + 2.0e-10:
                raise NonzeroBridgeFailClosed("invalid signed pair bridge")
            bridge[i, j] = bridge[j, i] = value
    h1 = np.asarray([power_hermite_coefficient(float(a), float(s), 1, 1) for a, s in zip(alpha, sigma)])
    h2 = np.asarray([power_hermite_coefficient(float(a), float(s), 1, 2) for a, s in zip(alpha, sigma)])
    h3 = np.asarray([power_hermite_coefficient(float(a), float(s), 1, 3) for a, s in zip(alpha, sigma)])
    if np.any(np.abs(h1) <= _SCALE_FLOOR):
        raise NonzeroBridgeFailClosed("normal-ordered degree-one coefficient is too small for bridge normalization")
    gamma2 = h2 * relu_scale / (h1 * h1)
    gamma3 = h3 * relu_scale * relu_scale / (h1 * h1 * h1)
    return NonzeroMeanBridgeState(mean, covariance, sigma, alpha, relu_mean, relu_scale, correlation, bridge, gamma2, gamma3)


def _raw_moment_for_labels(state: NonzeroMeanBridgeState, labels: tuple[int, ...], *, terms: int = 32) -> float:
    unique = tuple(sorted(set(labels)))
    if not labels:
        return 1.0
    if len(unique) == 1:
        index = unique[0]
        return power_hermite_coefficient(float(state.alpha[index]), float(state.sigma[index]), len(labels), 0)
    counts = tuple(labels.count(index) for index in unique)
    if len(unique) == 2:
        left, right = unique
        return pair_raw_moment_series(
            float(state.alpha[left]), float(state.sigma[left]), counts[0],
            float(state.alpha[right]), float(state.sigma[right]), counts[1],
            float(state.correlation[left, right]), terms=max(terms, 32),
        )
    if len(unique) == 3:
        selected = np.asarray(unique, dtype=int)
        return triple_raw_moment_series(
            state.alpha[selected], state.sigma[selected], counts, state.correlation[np.ix_(selected, selected)], terms=terms,
        )
    raise ValueError("exact collision reference only needs at most three distinct labels")


def exact_collision_cumulant(state: NonzeroMeanBridgeState, labels: tuple[int, ...], *, terms: int = 32) -> float:
    """Central connected cumulant for any order-3/4 tuple with a repeated index."""
    if len(labels) not in (3, 4) or len(set(labels)) == len(labels):
        raise ValueError("this exact helper is defined for repeated order-three/four strata")
    answer = 0.0
    slots = tuple(range(len(labels)))
    for partition in _set_partitions(slots):
        coefficient = math.factorial(len(partition) - 1) * ((-1.0) ** (len(partition) - 1))
        product = 1.0
        for block in partition:
            product *= _raw_moment_for_labels(state, tuple(labels[index] for index in block), terms=terms)
        answer += coefficient * product
    return answer


def tree3_distinct(state: NonzeroMeanBridgeState, i: int, j: int, k: int) -> float:
    if len({i, j, k}) != 3:
        raise ValueError("tree formula is only for distinct source nodes")
    scale = state.relu_scale[i] * state.relu_scale[j] * state.relu_scale[k]
    q = state.bridge
    return scale * (
        state.gamma2[i] * q[i, j] * q[i, k]
        + state.gamma2[j] * q[i, j] * q[j, k]
        + state.gamma2[k] * q[i, k] * q[j, k]
    )


def tree4_distinct(state: NonzeroMeanBridgeState, i: int, j: int, k: int, ell: int) -> float:
    labels = (i, j, k, ell)
    if len(set(labels)) != 4:
        raise ValueError("tree formula is only for distinct source nodes")
    q = state.bridge
    star = math.fsum(state.gamma3[center] * math.prod(q[center, leaf] for leaf in labels if leaf != center) for center in labels)
    path = 0.5 * math.fsum(
        state.gamma2[permutation[1]]
        * state.gamma2[permutation[2]]
        * q[permutation[0], permutation[1]]
        * q[permutation[1], permutation[2]]
        * q[permutation[2], permutation[3]]
        for permutation in itertools.permutations(labels)
    )
    return math.prod(state.relu_scale[list(labels)]) * (star + path)


def small_source_tensor(state: NonzeroMeanBridgeState, order: int, *, terms: int = 32) -> np.ndarray:
    """Dense `n<=8` inspection tensor: exact collisions, tree distinct strata."""
    if order not in (3, 4):
        raise ValueError("source order must be three or four")
    n = state.mean.size
    result = np.empty((n,) * order, dtype=np.float64)
    for labels in np.ndindex(*((n,) * order)):
        if len(set(labels)) < order:
            result[labels] = exact_collision_cumulant(state, labels, terms=terms)
        elif order == 3:
            result[labels] = tree3_distinct(state, *labels)
        else:
            result[labels] = tree4_distinct(state, *labels)
    return result


def tree_tensor_continuation(state: NonzeroMeanBridgeState, order: int) -> np.ndarray:
    """Tree formula continued onto collisions, used only to verify projection algebra."""
    n = state.mean.size
    scale, q, g2, g3 = state.relu_scale, state.bridge, state.gamma2, state.gamma3
    result = np.empty((n,) * order, dtype=np.float64)
    for labels in np.ndindex(*((n,) * order)):
        if order == 3:
            i, j, k = labels
            value = g2[i] * q[i, j] * q[i, k] + g2[j] * q[i, j] * q[j, k] + g2[k] * q[i, k] * q[j, k]
        elif order == 4:
            star = math.fsum(g3[center] * math.prod(q[center, leaf] for position, leaf in enumerate(labels) if position != center_position) for center_position, center in enumerate(labels))
            path = 0.5 * math.fsum(
                g2[labels[permutation[1]]]
                * g2[labels[permutation[2]]]
                * q[labels[permutation[0]], labels[permutation[1]]]
                * q[labels[permutation[1]], labels[permutation[2]]]
                * q[labels[permutation[2]], labels[permutation[3]]]
                for permutation in itertools.permutations(range(4))
            )
            value = star + path
        else:
            raise ValueError("source order must be three or four")
        result[labels] = math.prod(scale[list(labels)]) * value
    return result


def projected_tree_tensors(state: NonzeroMeanBridgeState, probe: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project the bridge trees with `O(n^2 r^2+n r^4)` state, never `n^4`."""
    probe = np.asarray(probe, dtype=np.float64)
    if probe.ndim != 2 or probe.shape[0] != state.mean.size or not np.all(np.isfinite(probe)):
        raise ValueError("probe shape mismatch")
    a = state.relu_scale[:, None] * probe
    h = state.bridge @ a
    g2, g3, q = state.gamma2, state.gamma3, state.bridge
    t3 = (
        np.einsum("i,ia,ib,ic->abc", g2, a, h, h, optimize=True)
        + np.einsum("i,ia,ib,ic->abc", g2, h, a, h, optimize=True)
        + np.einsum("i,ia,ib,ic->abc", g2, h, h, a, optimize=True)
    )
    t4_star = np.zeros((probe.shape[1],) * 4, dtype=np.float64)
    for central in range(4):
        operands = [h, h, h, h]
        operands[central] = a
        t4_star += np.einsum("i,ia,ib,ic,id->abcd", g3, *operands, optimize=True)
    oriented_path = np.einsum("i,ia,ib,ij,jc,jd,j->abcd", g2, h, a, q, a, h, g2, optimize=True)
    t4_path = 0.5 * sum(oriented_path.transpose(permutation) for permutation in itertools.permutations(range(4)))
    return t3, t4_star + t4_path


@lru_cache(maxsize=None)
def _gh_rule(order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = hermgauss(order)
    return math.sqrt(2.0) * nodes, weights / math.sqrt(math.pi)


def direct_gh_raw_moment(mean: np.ndarray, covariance: np.ndarray, powers: tuple[int, ...], *, order: int = 42) -> float:
    """Deterministic Gauss--Hermite check for at most three generated variables."""
    mean, covariance = np.asarray(mean, dtype=np.float64), np.asarray(covariance, dtype=np.float64)
    dimension = mean.size
    if dimension > 3 or covariance.shape != (dimension, dimension) or len(powers) != dimension:
        raise ValueError("direct check supports only up to three variables")
    nodes, weights = _gh_rule(order)
    mesh = np.meshgrid(*([nodes] * dimension), indexing="ij")
    mass = np.prod(np.meshgrid(*([weights] * dimension), indexing="ij"), axis=0)
    normal = np.stack([entry.reshape(-1) for entry in mesh], axis=1)
    transformed = normal @ np.linalg.cholesky(covariance).T + mean
    rectified = np.maximum(transformed, 0.0)
    value = np.prod(rectified ** np.asarray(powers), axis=1)
    return float(mass.reshape(-1) @ value)
