"""Fail-closed analytic local dense reference for M120C.

This module deliberately has no binding-grid entry point.  It supplies the
analytic mean/variance cross blocks of the central Gaussian ReLU covariance
map and a bounded-disagreement Plackett evaluation of the bivariate quadrant
probability.  Inputs near a singular Gaussian endpoint are rejected; no
correlation clipping, variance floor, or denominator replacement is used.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


FLOOR = 1.0e-10
ENDPOINT_MARGIN = 1.0e-10
QUADRATURE_TOLERANCE = 1.0e-13
MAX_SUBDIVISIONS = 4096
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_INV_2PI = 1.0 / (2.0 * math.pi)
_GL32_X, _GL32_W = np.polynomial.legendre.leggauss(32)
_GL64_X, _GL64_W = np.polynomial.legendre.leggauss(64)


class AnalyticReferenceFailClosed(RuntimeError):
    """The analytic reference domain or its numerical certificate failed."""


@dataclass(frozen=True)
class QuadrantProbability:
    value: float
    paired_order_disagreement: float
    subdivisions: int


@dataclass(frozen=True)
class AnalyticLocalKernels:
    probability: np.ndarray
    mean_variance_derivative: np.ndarray
    price_kernel: np.ndarray
    h_mu: np.ndarray
    h_variance: np.ndarray
    max_quadrature_disagreement: float


def _cdf(x: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(x, dtype=np.float64)
    if not np.all(np.isfinite(values)):
        raise AnalyticReferenceFailClosed("non-finite normal CDF argument")
    answer = np.fromiter(
        (0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in values.ravel()),
        dtype=np.float64,
        count=values.size,
    ).reshape(values.shape)
    return float(answer) if answer.ndim == 0 else answer


def _pdf(x: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(x, dtype=np.float64)
    if not np.all(np.isfinite(values)):
        raise AnalyticReferenceFailClosed("non-finite normal PDF argument")
    answer = np.exp(-0.5 * values * values) * _INV_SQRT_2PI
    return float(answer) if answer.ndim == 0 else answer


def _integrand(alpha_i: float, alpha_j: float, rho: np.ndarray) -> np.ndarray:
    one_minus = 1.0 - rho * rho
    if np.any(one_minus <= 0.0) or not np.all(np.isfinite(one_minus)):
        raise AnalyticReferenceFailClosed("Plackett integration reached singular correlation")
    exponent = -(alpha_i * alpha_i + alpha_j * alpha_j - 2.0 * rho * alpha_i * alpha_j) / (2.0 * one_minus)
    return _INV_2PI * np.exp(exponent) / np.sqrt(one_minus)


def _gauss_interval(alpha_i: float, alpha_j: float, left: float, right: float, nodes: np.ndarray, weights: np.ndarray) -> float:
    mapped = 0.5 * (right - left) * nodes + 0.5 * (left + right)
    return float(0.5 * (right - left) * np.sum(weights * _integrand(alpha_i, alpha_j, mapped)))


def quadrant_probability(alpha_i: float, alpha_j: float, rho: float) -> QuadrantProbability:
    """Return ``P(X_i>0,X_j>0)`` with adaptive paired-order disagreement.

    Plackett's identity gives ``Phi2(a,b;rho)=Phi(a)Phi(b)+int_0^rho phi2(a,b;t)dt``.
    A 32/64 Gauss-Legendre pair is recursively bisected until the sum of the
    local paired-order disagreements is below ``QUADRATURE_TOLERANCE``.  The
    disagreement is an explicit a-posteriori numerical indicator, not a
    hidden replacement for endpoint regularization.
    """
    alpha_i, alpha_j, rho = float(alpha_i), float(alpha_j), float(rho)
    if not all(math.isfinite(value) for value in (alpha_i, alpha_j, rho)):
        raise AnalyticReferenceFailClosed("non-finite Plackett argument")
    if abs(rho) >= 1.0 - ENDPOINT_MARGIN:
        raise AnalyticReferenceFailClosed("correlation too close to singular endpoint")
    base = float(_cdf(alpha_i)) * float(_cdf(alpha_j))
    if rho == 0.0:
        return QuadrantProbability(base, 0.0, 0)

    def interval(left: float, right: float) -> tuple[float, float, float, float]:
        coarse = _gauss_interval(alpha_i, alpha_j, left, right, _GL32_X, _GL32_W)
        fine = _gauss_interval(alpha_i, alpha_j, left, right, _GL64_X, _GL64_W)
        indicator = abs(fine - coarse)
        if not all(math.isfinite(value) for value in (coarse, fine, indicator)):
            raise AnalyticReferenceFailClosed("non-finite Plackett paired-order estimate")
        return left, right, fine, indicator

    def aggregate_disagreement(active: list[tuple[float, float, float, float]]) -> float:
        indicators = [item[3] for item in active]
        if not all(math.isfinite(indicator) for indicator in indicators):
            raise AnalyticReferenceFailClosed("non-finite active Plackett paired-order disagreement")
        aggregate = math.fsum(indicators)
        if not math.isfinite(aggregate):
            raise AnalyticReferenceFailClosed("non-finite aggregate Plackett paired-order disagreement")
        return aggregate

    # This is intentionally a *global* adaptive controller.  Every current
    # interval remains in the ledger, so the termination criterion is the sum
    # of all 32/64 indicators rather than a moving local budget that could
    # accept individually small intervals whose aggregate exceeds tolerance.
    intervals = [interval(0.0, rho)]
    subdivisions = 0
    disagreement = aggregate_disagreement(intervals)
    while True:
        if not math.isfinite(disagreement):
            raise AnalyticReferenceFailClosed("non-finite Plackett paired-order disagreement")
        if disagreement <= QUADRATURE_TOLERANCE:
            break
        index = max(range(len(intervals)), key=lambda item: intervals[item][3])
        left, right, _fine, _indicator = intervals.pop(index)
        subdivisions += 1
        if subdivisions > MAX_SUBDIVISIONS:
            raise AnalyticReferenceFailClosed("Plackett paired-order global convergence failed")
        middle = 0.5 * (left + right)
        intervals.extend((interval(left, middle), interval(middle, right)))
        disagreement = aggregate_disagreement(intervals)
    if not math.isfinite(disagreement) or disagreement > QUADRATURE_TOLERANCE:
        raise AnalyticReferenceFailClosed("Plackett paired-order aggregate disagreement exceeds tolerance")
    value = base + math.fsum(item[2] for item in intervals)
    if not math.isfinite(value) or value < -QUADRATURE_TOLERANCE or value > 1.0 + QUADRATURE_TOLERANCE:
        raise AnalyticReferenceFailClosed("invalid quadrant probability")
    return QuadrantProbability(value, disagreement, subdivisions)


def _validate_state(mean: np.ndarray, covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if mean.ndim != 1 or covariance.shape != (mean.size, mean.size):
        raise ValueError("mean/covariance shape mismatch")
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(covariance)):
        raise AnalyticReferenceFailClosed("non-finite Gaussian state")
    if not np.array_equal(covariance, covariance.T):
        raise AnalyticReferenceFailClosed("covariance must be exactly symmetric before reference evaluation")
    variance = np.diag(covariance)
    if np.any(variance <= FLOOR):
        raise AnalyticReferenceFailClosed("variance at or below fail-closed floor")
    eigen_minimum = float(np.min(np.linalg.eigvalsh(covariance)))
    if not math.isfinite(eigen_minimum) or eigen_minimum <= FLOOR:
        raise AnalyticReferenceFailClosed("covariance is not comfortably positive definite")
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    return mean, covariance, sigma, alpha


def relu_mean(mean: float, variance: float) -> float:
    if not math.isfinite(mean) or not math.isfinite(variance) or variance <= FLOOR:
        raise AnalyticReferenceFailClosed("invalid univariate ReLU Gaussian")
    sigma = math.sqrt(variance)
    alpha = mean / sigma
    return sigma * float(_pdf(alpha)) + mean * float(_cdf(alpha))


def analytic_local_kernels(mean: np.ndarray, covariance: np.ndarray) -> AnalyticLocalKernels:
    """Analytic central-covariance ReLU Jacobian blocks required by M120C.

    For ``i != j``, differentiating ``Cov(ReLU(X_i),ReLU(X_j))`` gives
    ``Hmu = E[1_i ReLU(X_j)] - p_i m_j`` and
    ``Hv = .5 f_i(0) E[ReLU(X_j)|X_i=0] - phi(alpha_i)m_j/(2 sigma_i)``.
    The diagonal limits are evaluated directly, never by a near-diagonal rule.
    """
    mean, covariance, sigma, alpha = _validate_state(mean, covariance)
    n = mean.size
    probability = np.asarray(_cdf(alpha), dtype=np.float64)
    density = np.asarray(_pdf(alpha), dtype=np.float64)
    moments = sigma * density + mean * probability
    r = density / (2.0 * sigma)
    price = np.empty((n, n), dtype=np.float64)
    h_mu = np.empty((n, n), dtype=np.float64)
    h_variance = np.empty((n, n), dtype=np.float64)
    max_disagreement = 0.0

    for i in range(n):
        price[i, i] = probability[i]
        h_mu[i, i] = 2.0 * moments[i] * (1.0 - probability[i])
        h_variance[i, i] = probability[i] - 2.0 * moments[i] * r[i]
        for j in range(i + 1, n):
            rho = covariance[i, j] / (sigma[i] * sigma[j])
            quadrant = quadrant_probability(alpha[i], alpha[j], rho)
            if not math.isfinite(quadrant.value) or not math.isfinite(quadrant.paired_order_disagreement):
                raise AnalyticReferenceFailClosed("non-finite Plackett quadrant certificate")
            q = math.sqrt(1.0 - rho * rho)
            d_i = density[i] * float(_cdf((alpha[j] - rho * alpha[i]) / q)) / sigma[i]
            d_j = density[j] * float(_cdf((alpha[i] - rho * alpha[j]) / q)) / sigma[j]
            event_xj = mean[j] * quadrant.value + covariance[j, i] * d_i + covariance[j, j] * d_j
            event_xi = mean[i] * quadrant.value + covariance[i, j] * d_j + covariance[i, i] * d_i
            conditional_mean_j = mean[j] - covariance[j, i] * mean[i] / covariance[i, i]
            conditional_variance_j = covariance[j, j] - covariance[j, i] * covariance[j, i] / covariance[i, i]
            conditional_mean_i = mean[i] - covariance[i, j] * mean[j] / covariance[j, j]
            conditional_variance_i = covariance[i, i] - covariance[i, j] * covariance[i, j] / covariance[j, j]
            h_mu[i, j] = event_xj - probability[i] * moments[j]
            h_mu[j, i] = event_xi - probability[j] * moments[i]
            h_variance[i, j] = 0.5 * density[i] / sigma[i] * relu_mean(conditional_mean_j, conditional_variance_j) - r[i] * moments[j]
            h_variance[j, i] = 0.5 * density[j] / sigma[j] * relu_mean(conditional_mean_i, conditional_variance_i) - r[j] * moments[i]
            price[i, j] = price[j, i] = quadrant.value
            max_disagreement = max(max_disagreement, quadrant.paired_order_disagreement)

    if not math.isfinite(max_disagreement) or max_disagreement > QUADRATURE_TOLERANCE:
        raise AnalyticReferenceFailClosed("quadrature disagreement exceeds frozen tolerance")
    return AnalyticLocalKernels(probability, r, price, h_mu, h_variance, max_disagreement)


def analytic_relu_gaussian_moments(mean: np.ndarray, covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fail-closed full Gaussian ReLU moments using the same Plackett primitive."""
    mean, covariance, sigma, alpha = _validate_state(mean, covariance)
    n = mean.size
    probability = np.asarray(_cdf(alpha), dtype=np.float64)
    density = np.asarray(_pdf(alpha), dtype=np.float64)
    output_mean = sigma * density + mean * probability
    raw_second = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        second = (covariance[i, i] + mean[i] * mean[i]) * probability[i] + mean[i] * sigma[i] * density[i]
        raw_second[i, i] = second
        for j in range(i + 1, n):
            rho = covariance[i, j] / (sigma[i] * sigma[j])
            quadrant_certificate = quadrant_probability(alpha[i], alpha[j], rho)
            if (
                not math.isfinite(quadrant_certificate.value)
                or not math.isfinite(quadrant_certificate.paired_order_disagreement)
            ):
                raise AnalyticReferenceFailClosed("non-finite Plackett quadrant certificate")
            quadrant = quadrant_certificate.value
            q = math.sqrt(1.0 - rho * rho)
            pa = density[i] * float(_cdf((alpha[j] - rho * alpha[i]) / q))
            pb = density[j] * float(_cdf((alpha[i] - rho * alpha[j]) / q))
            joint_density = float(_integrand(alpha[i], alpha[j], np.asarray(rho)))
            value = (
                mean[j] * sigma[i] * pa
                + mean[i] * sigma[j] * pb
                + sigma[i] * sigma[j] * (1.0 - rho * rho) * joint_density
                + (mean[i] * mean[j] + covariance[i, j]) * quadrant
            )
            raw_second[i, j] = raw_second[j, i] = value
    output_covariance = raw_second - np.outer(output_mean, output_mean)
    return output_mean, 0.5 * (output_covariance + output_covariance.T)


def analytic_dense_pullback(mean_adjoint: np.ndarray, covariance_adjoint: np.ndarray, kernels: AnalyticLocalKernels) -> tuple[np.ndarray, np.ndarray]:
    """Complete dense central-covariance pullback with analytic local blocks."""
    mean_adjoint = np.asarray(mean_adjoint, dtype=np.float64)
    covariance_adjoint = np.asarray(covariance_adjoint, dtype=np.float64)
    if mean_adjoint.ndim != 2 or covariance_adjoint.shape != (mean_adjoint.shape[1], mean_adjoint.shape[0], mean_adjoint.shape[0]):
        raise ValueError("adjoint shape mismatch")
    covariance_adjoint = 0.5 * (covariance_adjoint + covariance_adjoint.swapaxes(1, 2))
    diagonal_a = np.diagonal(covariance_adjoint, axis1=1, axis2=2).T

    def contract(block: np.ndarray) -> np.ndarray:
        paired = np.einsum("oij,ij->oi", covariance_adjoint, block, optimize=True).T
        return 2.0 * paired - diagonal_a * np.diag(block)[:, None]

    c_mu = contract(kernels.h_mu)
    c_variance = contract(kernels.h_variance)
    mean_before = kernels.probability[:, None] * mean_adjoint + c_mu
    covariance_before = covariance_adjoint * kernels.price_kernel[None, :, :]
    diagonal = kernels.mean_variance_derivative[:, None] * mean_adjoint + c_variance
    indices = np.arange(mean_adjoint.shape[0])
    covariance_before[:, indices, indices] = diagonal.T
    return mean_before, covariance_before
