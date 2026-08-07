"""M147 endpoint-safe Gaussian ReLU bridge and [2,1,1] reference.

This is a response-free, generated-state mathematics component.  It replaces
the M122 Hermite ``abs(rho) <= .80`` certification domain by:

* an angular Plackett coordinate ``rho = sin(theta)`` whose integrand remains
  bounded at ``theta = +/-pi/2``;
* exact rank-one endpoint formulae;
* Price-theorem value enclosures that are rigorous independently of the
  paired-order quadrature indicator; and
* a conditional one-dimensional central-moment rule for the connected
  ``[2,1,1]`` coefficient and its directional derivative.

No benchmark, model, response cell, scorer, or submission is read here.
The exact PSD boundary has only a one-sided feasible directional derivative;
it is deliberately not mislabeled as an ambient Frechet derivative.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path
import sys
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for relative in ("m122_nonzero_bridge_theory", "m129_source_frechet_tangent"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m122_nonzero_bridge import (  # noqa: E402
    NonzeroMeanBridgeState,
    power_hermite_coefficient,
)
from m129_source_frechet import (  # noqa: E402
    BridgeStateFrechet,
    _tree_entry_dot,
    power_hermite_coefficient_dot,
)


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_INV_2PI = 1.0 / (2.0 * math.pi)
_EPS = np.finfo(np.float64).eps


class EndpointCertificationFailure(RuntimeError):
    """Raised when a stated domain or numerical certificate does not pass."""


def _require_finite_scalar(value: float, label: str) -> float:
    """Return a finite scalar or convert invalid arithmetic into a refusal."""

    value = float(value)
    if not math.isfinite(value):
        raise EndpointCertificationFailure(f"non-finite {label}")
    return value


def _require_finite_arrays(*arrays: np.ndarray, label: str) -> None:
    if not all(np.all(np.isfinite(array)) for array in arrays):
        raise EndpointCertificationFailure(f"non-finite {label}")


def _cdf(value: float) -> float:
    if not math.isfinite(value):
        if value == math.inf:
            return 1.0
        if value == -math.inf:
            return 0.0
        raise EndpointCertificationFailure("non-finite Gaussian CDF argument")
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def _pdf(value: float) -> float:
    if not math.isfinite(value):
        if abs(value) == math.inf:
            return 0.0
        raise EndpointCertificationFailure("non-finite Gaussian PDF argument")
    return _INV_SQRT_2PI * math.exp(-0.5 * value * value)


@lru_cache(maxsize=None)
def _legendre(order: int) -> tuple[np.ndarray, np.ndarray]:
    if order < 4:
        raise ValueError("Gauss-Legendre order must be at least four")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return nodes.astype(np.float64), weights.astype(np.float64)


def _endpoint_quadrant(alpha: float, beta: float, sign: int) -> float:
    if sign == 1:
        return _cdf(min(alpha, beta))
    if sign == -1:
        return max(0.0, _cdf(alpha) + _cdf(beta) - 1.0)
    raise ValueError("endpoint sign must be +/-1")


def _angle_density(alpha: float, beta: float, theta: np.ndarray) -> np.ndarray:
    """Plackett density after ``rho=sin(theta)``.

    The nonnegative decomposition

      a^2+b^2-2tab = .5(1+t)(a-b)^2 + .5(1-t)(a+b)^2

    removes the cancellation that otherwise occurs near either endpoint.
    Gauss nodes are strictly interior, so both denominators are positive.
    """

    t = np.sin(theta)
    cosine = np.cos(theta)
    # ``1-sin(theta)`` loses all bits next to +pi/2 (and analogously on the
    # negative side).  The conjugate identity keeps a positive denominator.
    denominator_minus = 1.0 - t
    mask_plus = t > 0.5
    denominator_minus[mask_plus] = (
        cosine[mask_plus] ** 2 / (1.0 + t[mask_plus])
    )
    denominator_plus = 1.0 + t
    mask_minus = t < -0.5
    denominator_plus[mask_minus] = (
        cosine[mask_minus] ** 2 / (1.0 - t[mask_minus])
    )
    exponent = -0.25 * (
        (alpha - beta) ** 2 / denominator_minus
        + (alpha + beta) ** 2 / denominator_plus
    )
    return _INV_2PI * np.exp(exponent)


def _gauss_interval(
    function: Callable[[np.ndarray], np.ndarray],
    left: float,
    right: float,
    order: int,
) -> float:
    nodes, weights = _legendre(order)
    half = 0.5 * (right - left)
    middle = 0.5 * (right + left)
    return float(half * np.dot(weights, function(middle + half * nodes)))


def _adaptive_paired_angle_integral(
    function: Callable[[np.ndarray], np.ndarray],
    left: float,
    right: float,
    *,
    tolerance: float,
    coarse_order: int,
    fine_order: int,
    max_subdivisions: int,
) -> tuple[float, float, int, int]:
    if left == right:
        return 0.0, 0.0, 0, 0

    def interval(a: float, b: float) -> tuple[float, float, float, float]:
        coarse = _gauss_interval(function, a, b, coarse_order)
        fine = _gauss_interval(function, a, b, fine_order)
        return a, b, fine, abs(fine - coarse)

    active = [interval(left, right)]
    subdivisions = 0
    while math.fsum(item[3] for item in active) > tolerance:
        if subdivisions >= max_subdivisions:
            raise EndpointCertificationFailure(
                "angular paired-order certificate did not converge"
            )
        index = max(range(len(active)), key=lambda slot: active[slot][3])
        a, b, _value, _error = active.pop(index)
        middle = 0.5 * (a + b)
        active.extend((interval(a, middle), interval(middle, b)))
        subdivisions += 1
    disagreement = math.fsum(item[3] for item in active)
    value = math.fsum(item[2] for item in active)
    if not all(math.isfinite(item) for item in (value, disagreement)):
        raise EndpointCertificationFailure("non-finite angular paired-order result")
    evaluations = (1 + 2 * subdivisions) * (coarse_order + fine_order)
    return value, disagreement, subdivisions, evaluations


@dataclass(frozen=True)
class QuadrantCertificate:
    value: float
    paired_order_disagreement: float
    rigorous_lower: float
    rigorous_upper: float
    subdivisions: int
    integrand_evaluations: int
    method: str


def quadrant_probability_angle(
    alpha: float,
    beta: float,
    rho: float,
    *,
    tolerance: float = 2.0e-13,
    coarse_order: int = 16,
    fine_order: int = 32,
    max_subdivisions: int = 128,
) -> QuadrantCertificate:
    """Endpoint-safe ``P(G1>-alpha,G2>-beta)``.

    The paired-order disagreement is an a-posteriori numerical indicator, not
    a formal interval error bound.  The separately returned endpoint enclosure
    *is* rigorous: Plackett's angular integrand is between zero and ``1/(2pi)``.
    """

    alpha, beta, rho = float(alpha), float(beta), float(rho)
    if not all(math.isfinite(item) for item in (alpha, beta, rho)):
        raise EndpointCertificationFailure("non-finite quadrant request")
    if abs(rho) > 1.0:
        raise EndpointCertificationFailure("correlation lies outside the PSD interval")
    if abs(rho) == 1.0:
        value = _endpoint_quadrant(alpha, beta, 1 if rho > 0.0 else -1)
        return QuadrantCertificate(value, 0.0, value, value, 0, 0, "exact-rank-one")

    theta = math.asin(rho)
    base = _cdf(alpha) * _cdf(beta)
    if theta == 0.0:
        value = base
        subdivisions = 0
        disagreement = 0.0
        evaluations = 0
    else:
        integrand = lambda value: _angle_density(alpha, beta, value)
        integral, disagreement, subdivisions, evaluations = (
            _adaptive_paired_angle_integral(
                integrand,
                0.0,
                theta,
                tolerance=tolerance,
                coarse_order=coarse_order,
                fine_order=fine_order,
                max_subdivisions=max_subdivisions,
            )
        )
        value = base + integral

    sign = 1 if rho >= 0.0 else -1
    endpoint = _endpoint_quadrant(alpha, beta, sign)
    angular_width = math.acos(abs(rho)) * _INV_2PI
    if sign == 1:
        rigorous_lower = max(0.0, endpoint - angular_width)
        rigorous_upper = endpoint
    else:
        rigorous_lower = endpoint
        rigorous_upper = min(1.0, endpoint + angular_width)
    slack = 64.0 * _EPS
    if (
        not math.isfinite(value)
        or value < rigorous_lower - slack
        or value > rigorous_upper + slack
        or value < -slack
        or value > 1.0 + slack
    ):
        raise EndpointCertificationFailure("quadrant value violates its rigorous enclosure")
    return QuadrantCertificate(
        min(1.0, max(0.0, value)),
        disagreement,
        rigorous_lower,
        rigorous_upper,
        subdivisions,
        evaluations,
        "angular-plackett-paired-order",
    )


def _normal_interval_moments(lower: float, upper: float, maximum: int) -> np.ndarray:
    """Return ``int_lower^upper z^k phi(z) dz`` through ``maximum``."""

    if maximum < 0 or lower > upper:
        raise ValueError("invalid interval moment request")
    answer = np.zeros(maximum + 1, dtype=np.float64)
    answer[0] = max(0.0, _cdf(upper) - _cdf(lower))
    if maximum == 0 or answer[0] == 0.0:
        return answer
    density_lower, density_upper = _pdf(lower), _pdf(upper)
    answer[1] = density_lower - density_upper

    def boundary_power(value: float, density: float, power: int) -> float:
        # Test density before the power: otherwise a finite, remote endpoint
        # can form an indeterminate ``inf * 0`` after Gaussian underflow.
        if density == 0.0 or not math.isfinite(value):
            return 0.0
        return value**power * density

    for degree in range(2, maximum + 1):
        answer[degree] = (
            boundary_power(lower, density_lower, degree - 1)
            - boundary_power(upper, density_upper, degree - 1)
            + (degree - 1) * answer[degree - 2]
        )
    return answer


def endpoint_positive_power_raw(
    alpha: float,
    beta: float,
    sign: int,
    power_left: int = 1,
    power_right: int = 1,
) -> float:
    """Exact rank-one standardized positive-part product moment."""

    if power_left < 1 or power_right < 1 or sign not in (-1, 1):
        raise ValueError("invalid endpoint powered-moment request")
    if sign == 1:
        lower, upper = max(-alpha, -beta), math.inf
    else:
        lower, upper = -alpha, beta
        if lower >= upper:
            return 0.0
    try:
        moments = _normal_interval_moments(lower, upper, power_left + power_right)
        terms: list[float] = []
        for left_degree in range(power_left + 1):
            left_coefficient = (
                math.comb(power_left, left_degree)
                * alpha ** (power_left - left_degree)
            )
            for right_degree in range(power_right + 1):
                right_coefficient = (
                    math.comb(power_right, right_degree)
                    * beta ** (power_right - right_degree)
                    * sign**right_degree
                )
                terms.append(
                    left_coefficient
                    * right_coefficient
                    * float(moments[left_degree + right_degree])
                )
        return _require_finite_scalar(
            math.fsum(terms), "rank-one positive-part powered moment"
        )
    except (OverflowError, ValueError) as error:
        raise EndpointCertificationFailure(
            "rank-one positive-part powered moment overflowed"
        ) from error


def _endpoint_standardized_derivatives(
    alpha: float, beta: float, sign: int
) -> tuple[float, float, float]:
    probability = _endpoint_quadrant(alpha, beta, sign)
    if sign == 1:
        threshold = min(alpha, beta)
        density = _pdf(threshold)
        derivative_alpha = beta * probability + density
        derivative_beta = alpha * probability + density
    else:
        if alpha + beta <= 0.0:
            derivative_alpha = derivative_beta = 0.0
        else:
            derivative_alpha = (
                beta * probability - _pdf(alpha) + _pdf(beta)
            )
            derivative_beta = (
                alpha * probability + _pdf(alpha) - _pdf(beta)
            )
    return derivative_alpha, derivative_beta, probability


def _endpoint_remainder_bound(abs_rho: float) -> float:
    """Universal Price remainder after the endpoint linear term.

    ``sin(theta)-theta*cos(theta)`` is evaluated by series near zero to avoid
    destroying the positive ``O(theta^3)`` certificate by cancellation.
    """

    theta = math.acos(abs_rho)
    if theta < 1.0e-3:
        theta2 = theta * theta
        numerator = theta**3 * (
            1.0 / 3.0
            + theta2
            * (-1.0 / 30.0 + theta2 * (1.0 / 840.0 - theta2 / 45360.0))
        )
    else:
        numerator = math.sin(theta) - theta * math.cos(theta)
    return max(0.0, numerator * _INV_2PI)


@dataclass(frozen=True)
class BivariateReluCertificate:
    raw: float
    tangent: float
    standardized_raw: float
    standardized_alpha_derivative: float
    standardized_beta_derivative: float
    standardized_rho_derivative: float
    rho: float
    rho_dot: float
    rigorous_raw_lower: float
    rigorous_raw_upper: float
    quadrant: QuadrantCertificate
    derivative_kind: str
    moment_paired_order_disagreement: float
    moment_integrand_evaluations: int


def _stable_endpoint_remainder(
    alpha: float,
    beta: float,
    rho: float,
    *,
    tolerance: float,
) -> tuple[float, float, int]:
    """Numerically evaluate the nonnegative Price endpoint remainder."""

    sign = 1 if rho >= 0.0 else -1
    theta_rho = math.asin(rho)
    if sign == 1:
        left, right = theta_rho, 0.5 * math.pi

        def integrand(theta: np.ndarray) -> np.ndarray:
            return (np.sin(theta) - rho) * _angle_density(alpha, beta, theta)

    else:
        left, right = -0.5 * math.pi, theta_rho

        def integrand(theta: np.ndarray) -> np.ndarray:
            return (rho - np.sin(theta)) * _angle_density(alpha, beta, theta)

    value, disagreement, _subdivisions, evaluations = (
        _adaptive_paired_angle_integral(
            integrand,
            left,
            right,
            tolerance=tolerance,
            coarse_order=16,
            fine_order=32,
            max_subdivisions=128,
        )
    )
    if value < -64.0 * _EPS:
        raise EndpointCertificationFailure("negative Price endpoint remainder")
    return max(0.0, value), disagreement, evaluations


def bivariate_relu_raw_dot_endpoint(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    *,
    quadrant_tolerance: float = 2.0e-13,
) -> BivariateReluCertificate:
    """Bivariate ReLU product and tangent for every ``|rho|<=1``.

    For ``|rho|<1`` this is the ordinary Frechet derivative.  At a rank-one
    endpoint only the supplied ``t -> 0+`` PSD-feasible directional derivative
    is accepted.  An outward direction is rejected rather than regularized.
    """

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    if (
        mean.shape != (2,)
        or covariance.shape != (2, 2)
        or mean_dot.shape != (2,)
        or covariance_dot.shape != (2, 2)
        or not np.array_equal(covariance, covariance.T)
        or not np.array_equal(covariance_dot, covariance_dot.T)
        or not all(
            np.all(np.isfinite(item))
            for item in (mean, covariance, mean_dot, covariance_dot)
        )
    ):
        raise EndpointCertificationFailure("invalid bivariate value/tangent state")
    variance = np.diag(covariance)
    if np.any(variance <= 0.0):
        raise EndpointCertificationFailure("positive marginal variances are required")
    sigma = np.sqrt(variance)
    sigma_dot = np.diag(covariance_dot) / (2.0 * sigma)
    alpha = mean / sigma
    alpha_dot = mean_dot / sigma - alpha * sigma_dot / sigma
    rho = float(covariance[0, 1] / (sigma[0] * sigma[1]))
    if abs(rho) > 1.0:
        raise EndpointCertificationFailure("bivariate covariance is not PSD")
    rho_dot = float(
        covariance_dot[0, 1] / (sigma[0] * sigma[1])
        - rho * (sigma_dot[0] / sigma[0] + sigma_dot[1] / sigma[1])
    )
    endpoint = abs(rho) == 1.0
    if endpoint:
        sign = 1 if rho > 0.0 else -1
        # det'(0+) >= 0 is equivalent to -sign*rho_dot >= 0.
        if -sign * rho_dot < -256.0 * _EPS * (1.0 + abs(rho_dot)):
            raise EndpointCertificationFailure(
                "rank-one covariance tangent points outside the PSD cone"
            )
        standardized = endpoint_positive_power_raw(
            float(alpha[0]), float(alpha[1]), sign
        )
        derivative_alpha, derivative_beta, derivative_rho = (
            _endpoint_standardized_derivatives(
                float(alpha[0]), float(alpha[1]), sign
            )
        )
        quadrant = quadrant_probability_angle(
            float(alpha[0]), float(alpha[1]), rho
        )
        standardized_lower = standardized_upper = standardized
        derivative_kind = "one-sided-PSD-directional"
        moment_disagreement = 0.0
        moment_evaluations = 0
    else:
        abs_rho = abs(rho)
        one_minus = (1.0 - abs_rho) * (1.0 + abs_rho)
        if one_minus <= 0.0:
            raise EndpointCertificationFailure("nonpositive interior determinant")
        root = math.sqrt(one_minus)
        sign = 1 if rho >= 0.0 else -1
        # Algebraically beta-rho*alpha, rearranged around the nearest endpoint.
        numerator_beta = math.fsum(
            [float(alpha[1]), -sign * float(alpha[0]), (sign - rho) * float(alpha[0])]
        )
        numerator_alpha = math.fsum(
            [float(alpha[0]), -sign * float(alpha[1]), (sign - rho) * float(alpha[1])]
        )
        boundary_alpha = _pdf(float(alpha[0])) * _cdf(numerator_beta / root)
        boundary_beta = _pdf(float(alpha[1])) * _cdf(numerator_alpha / root)
        quadrant = quadrant_probability_angle(
            float(alpha[0]),
            float(alpha[1]),
            rho,
            tolerance=quadrant_tolerance,
        )
        q = quadrant.value
        rotated_quadratic = 0.5 * (
            (1.0 + rho) * (float(alpha[0]) - float(alpha[1])) ** 2
            + (1.0 - rho) * (float(alpha[0]) + float(alpha[1])) ** 2
        )
        root_density = root * _INV_2PI * math.exp(
            -rotated_quadratic / (2.0 * one_minus)
        )
        rosenbaum_terms = (
            float(alpha[1]) * boundary_alpha,
            float(alpha[0]) * boundary_beta,
            root_density,
            (float(alpha[0]) * float(alpha[1]) + rho) * q,
        )
        rosenbaum_standardized = math.fsum(rosenbaum_terms)
        derivative_alpha = (
            float(alpha[1]) * q + rho * boundary_alpha + boundary_beta
        )
        derivative_beta = (
            float(alpha[0]) * q + rho * boundary_beta + boundary_alpha
        )
        derivative_rho = q

        endpoint_standardized = endpoint_positive_power_raw(
            float(alpha[0]), float(alpha[1]), sign
        )
        endpoint_q = _endpoint_quadrant(
            float(alpha[0]), float(alpha[1]), sign
        )
        delta = 1.0 - abs_rho
        if sign == 1:
            linear_endpoint = endpoint_standardized - delta * endpoint_q
        else:
            linear_endpoint = endpoint_standardized + delta * endpoint_q
        standardized_lower = linear_endpoint
        standardized_upper = linear_endpoint + _endpoint_remainder_bound(abs_rho)

        # Rosenbaum's closed form is normally the cheapest exact path, even at
        # high correlation.  Its independent Price enclosure detects the
        # exceptional cancellation regime (most visibly rho -> -1 with
        # coincident zero thresholds); only then do we pay for the short,
        # nonnegative endpoint-remainder integral.
        rosenbaum_roundoff = 128.0 * _EPS * math.fsum(
            abs(item) for item in rosenbaum_terms
        )
        if not (
            standardized_lower - rosenbaum_roundoff
            <= rosenbaum_standardized
            <= standardized_upper + rosenbaum_roundoff
        ):
            remainder, moment_disagreement, moment_evaluations = (
                _stable_endpoint_remainder(
                    float(alpha[0]),
                    float(alpha[1]),
                    rho,
                    tolerance=max(2.0e-16, quadrant_tolerance),
                )
            )
            standardized = linear_endpoint + remainder
        else:
            standardized = rosenbaum_standardized
            moment_disagreement = 0.0
            moment_evaluations = 0
        slack = max(
            128.0 * _EPS * (1.0 + abs(standardized)),
            4.0 * moment_disagreement,
        )
        if not (
            standardized_lower - slack
            <= standardized
            <= standardized_upper + slack
        ):
            raise EndpointCertificationFailure(
                "bivariate raw moment violates the rigorous Price enclosure"
            )
        derivative_kind = "interior-Frechet"

    raw_scale = float(sigma[0] * sigma[1])
    raw = raw_scale * standardized
    tangent = (
        (float(sigma_dot[0]) * float(sigma[1]) + float(sigma[0]) * float(sigma_dot[1]))
        * standardized
        + raw_scale
        * (
            derivative_alpha * float(alpha_dot[0])
            + derivative_beta * float(alpha_dot[1])
            + derivative_rho * rho_dot
        )
    )
    raw_lower = raw_scale * standardized_lower
    raw_upper = raw_scale * standardized_upper
    _require_finite_scalar(raw, "bivariate ReLU raw moment")
    _require_finite_scalar(tangent, "bivariate ReLU raw-moment tangent")
    _require_finite_scalar(standardized, "standardized bivariate ReLU moment")
    _require_finite_scalar(derivative_alpha, "bivariate alpha derivative")
    _require_finite_scalar(derivative_beta, "bivariate beta derivative")
    _require_finite_scalar(derivative_rho, "bivariate rho derivative")
    _require_finite_scalar(raw_lower, "bivariate lower enclosure")
    _require_finite_scalar(raw_upper, "bivariate upper enclosure")
    return BivariateReluCertificate(
        raw,
        tangent,
        standardized,
        derivative_alpha,
        derivative_beta,
        derivative_rho,
        rho,
        rho_dot,
        raw_lower,
        raw_upper,
        quadrant,
        derivative_kind,
        moment_disagreement,
        moment_evaluations,
    )


def univariate_relu_mean_dot(
    mean: float, variance: float, mean_dot: float, variance_dot: float
) -> tuple[float, float]:
    if not all(math.isfinite(item) for item in (mean, variance, mean_dot, variance_dot)) or variance <= 0.0:
        raise EndpointCertificationFailure("invalid univariate ReLU state")
    sigma = math.sqrt(variance)
    alpha = mean / sigma
    density, probability = _pdf(alpha), _cdf(alpha)
    value = sigma * density + mean * probability
    tangent = probability * mean_dot + 0.5 * density / sigma * variance_dot
    return (
        _require_finite_scalar(value, "univariate ReLU mean"),
        _require_finite_scalar(tangent, "univariate ReLU mean tangent"),
    )


def build_endpoint_state_frechet(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    *,
    allow_psd_directional: bool = False,
) -> BridgeStateFrechet:
    """M122/M129-compatible state with no artificial ``abs(rho)<=.80`` cap.

    The full state remains strictly positive definite because its ordinary
    Frechet derivative and the downstream conditional rule live on the open
    SPD cone.  Pairwise correlations may approach either endpoint arbitrarily
    closely.  Exact singular *pairs* are handled by the standalone primitive.
    """

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    n = mean.size
    if (
        mean.ndim != 1
        or covariance.shape != (n, n)
        or mean_dot.shape != (n,)
        or covariance_dot.shape != (n, n)
        or n > 16
        or not np.array_equal(covariance, covariance.T)
        or not np.array_equal(covariance_dot, covariance_dot.T)
        or not all(
            np.all(np.isfinite(item))
            for item in (mean, covariance, mean_dot, covariance_dot)
        )
    ):
        raise EndpointCertificationFailure("invalid endpoint bridge state")
    diagonal = np.diag(covariance)
    if np.any(diagonal <= 0.0):
        raise EndpointCertificationFailure("bridge state has nonpositive variance")
    scale = max(1.0, float(np.max(diagonal)))
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    eigen_minimum = float(eigenvalues[0])
    boundary_tolerance = 64.0 * _EPS * scale
    if not math.isfinite(eigen_minimum) or eigen_minimum < -boundary_tolerance:
        raise EndpointCertificationFailure("full bridge covariance is not PSD")
    if eigen_minimum <= boundary_tolerance:
        if not allow_psd_directional:
            raise EndpointCertificationFailure(
                "full bridge state is outside the certified open SPD cone"
            )
        null_vectors = eigenvectors[:, eigenvalues <= boundary_tolerance]
        null_tangent = null_vectors.T @ covariance_dot @ null_vectors
        null_tangent = 0.5 * (null_tangent + null_tangent.T)
        tangent_scale = max(1.0, float(np.max(np.abs(covariance_dot))))
        if float(np.min(np.linalg.eigvalsh(null_tangent))) < -256.0 * _EPS * tangent_scale:
            raise EndpointCertificationFailure(
                "full rank-deficient state tangent points outside the PSD cone"
            )

    sigma = np.sqrt(diagonal)
    sigma_dot = np.diag(covariance_dot) / (2.0 * sigma)
    alpha = mean / sigma
    alpha_dot = mean_dot / sigma - alpha * sigma_dot / sigma
    correlation = covariance / np.outer(sigma, sigma)
    correlation = 0.5 * (correlation + correlation.T)
    np.fill_diagonal(correlation, 1.0)
    scale_rate = sigma_dot / sigma
    correlation_dot = (
        covariance_dot / np.outer(sigma, sigma)
        - correlation * (scale_rate[:, None] + scale_rate[None, :])
    )
    correlation_dot = 0.5 * (correlation_dot + correlation_dot.T)
    np.fill_diagonal(correlation_dot, 0.0)

    relu_mean = np.empty(n, dtype=np.float64)
    relu_mean_dot = np.empty(n, dtype=np.float64)
    second = np.empty(n, dtype=np.float64)
    second_dot = np.empty(n, dtype=np.float64)
    h1 = np.empty(n, dtype=np.float64)
    h2 = np.empty(n, dtype=np.float64)
    h3 = np.empty(n, dtype=np.float64)
    h1_dot = np.empty(n, dtype=np.float64)
    h2_dot = np.empty(n, dtype=np.float64)
    h3_dot = np.empty(n, dtype=np.float64)
    for index in range(n):
        a, s = float(alpha[index]), float(sigma[index])
        adot, sdot = float(alpha_dot[index]), float(sigma_dot[index])
        relu_mean[index], relu_mean_dot[index] = power_hermite_coefficient_dot(
            a, s, 1, 0, adot, sdot
        )
        second[index], second_dot[index] = power_hermite_coefficient_dot(
            a, s, 2, 0, adot, sdot
        )
        h1[index], h1_dot[index] = power_hermite_coefficient_dot(
            a, s, 1, 1, adot, sdot
        )
        h2[index], h2_dot[index] = power_hermite_coefficient_dot(
            a, s, 1, 2, adot, sdot
        )
        h3[index], h3_dot[index] = power_hermite_coefficient_dot(
            a, s, 1, 3, adot, sdot
        )
    variance = second - relu_mean * relu_mean
    variance_dot = second_dot - 2.0 * relu_mean * relu_mean_dot
    if np.any(variance <= 64.0 * _EPS * np.maximum(1.0, second)):
        raise EndpointCertificationFailure("rectified marginal variance is degenerate")
    relu_scale = np.sqrt(variance)
    relu_scale_dot = variance_dot / (2.0 * relu_scale)

    bridge = np.eye(n, dtype=np.float64)
    bridge_dot = np.zeros((n, n), dtype=np.float64)
    for left in range(n):
        for right in range(left + 1, n):
            selected = np.asarray((left, right), dtype=int)
            pair = bivariate_relu_raw_dot_endpoint(
                mean[selected],
                covariance[np.ix_(selected, selected)],
                mean_dot[selected],
                covariance_dot[np.ix_(selected, selected)],
            )
            centered = pair.raw - relu_mean[left] * relu_mean[right]
            centered_dot = (
                pair.tangent
                - relu_mean_dot[left] * relu_mean[right]
                - relu_mean[left] * relu_mean_dot[right]
            )
            denominator = relu_scale[left] * relu_scale[right]
            value = centered / denominator
            value_dot = centered_dot / denominator - value * (
                relu_scale_dot[left] / relu_scale[left]
                + relu_scale_dot[right] / relu_scale[right]
            )
            if not math.isfinite(value) or abs(value) > 1.0 + 2.0e-10:
                raise EndpointCertificationFailure("invalid normalized ReLU bridge")
            bridge[left, right] = bridge[right, left] = value
            bridge_dot[left, right] = bridge_dot[right, left] = value_dot

    gamma2 = h2 * relu_scale / (h1 * h1)
    gamma3 = h3 * relu_scale * relu_scale / (h1 * h1 * h1)
    gamma2_dot = (
        (h2_dot * relu_scale + h2 * relu_scale_dot) / (h1 * h1)
        - 2.0 * h2 * relu_scale * h1_dot / (h1**3)
    )
    gamma3_dot = (
        (h3_dot * relu_scale**2 + 2.0 * h3 * relu_scale * relu_scale_dot)
        / (h1**3)
        - 3.0 * h3 * relu_scale**2 * h1_dot / (h1**4)
    )
    _require_finite_arrays(
        relu_mean,
        relu_mean_dot,
        relu_scale,
        relu_scale_dot,
        bridge,
        bridge_dot,
        gamma2,
        gamma3,
        gamma2_dot,
        gamma3_dot,
        label="endpoint bridge state",
    )
    state = NonzeroMeanBridgeState(
        mean,
        covariance,
        sigma,
        alpha,
        relu_mean,
        relu_scale,
        correlation,
        bridge,
        gamma2,
        gamma3,
    )
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


def collision211_local_state_dot(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    *,
    repeated_slot: int = 0,
    coarse_order: int = 48,
    fine_order: int = 64,
    value_tolerance: float = 2.0e-8,
    tangent_tolerance: float = 2.0e-7,
) -> "Collision211Certificate":
    """Width-independent per-triple ``[2,1,1]`` coefficient/Frechet API.

    A width-256 caller gathers the three selected mean entries and the 3x3
    covariance/tangent minors, then calls this function.  No ambient tensor or
    width-dependent state is constructed.  Exact conditional ``rho=+/-1`` is
    delegated to the rank-one pair primitive.  A local PSD boundary is
    accepted only when conditioning on the repeated coordinate leaves both
    singleton conditional variances strictly positive.  Zero conditional
    variance is a distinct degenerate truncated-normal problem and is refused
    explicitly rather than silently applying a non-existent Frechet tangent at
    a ReLU kink.
    """

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    if (
        mean.shape != (3,)
        or covariance.shape != (3, 3)
        or mean_dot.shape != (3,)
        or covariance_dot.shape != (3, 3)
        or repeated_slot not in (0, 1, 2)
    ):
        raise ValueError("local [2,1,1] API requires one three-variable state")
    singleton = [index for index in range(3) if index != repeated_slot]
    repeated_variance = float(covariance[repeated_slot, repeated_slot])
    if not math.isfinite(repeated_variance) or repeated_variance <= 0.0:
        raise EndpointCertificationFailure(
            "local [2,1,1] repeated variable needs positive finite variance"
        )
    conditional_diagonal = (
        np.diag(covariance)[singleton]
        - covariance[singleton, repeated_slot] ** 2 / repeated_variance
    )
    variance_scale = max(1.0, float(np.max(np.abs(np.diag(covariance)))))
    conditional_floor = 256.0 * _EPS * variance_scale
    if (
        not np.all(np.isfinite(conditional_diagonal))
        or np.any(conditional_diagonal <= conditional_floor)
    ):
        raise EndpointCertificationFailure(
            "local [2,1,1] degenerate conditional singleton variance is unsupported"
        )
    tangent = build_endpoint_state_frechet(
        mean,
        covariance,
        mean_dot,
        covariance_dot,
        allow_psd_directional=True,
    )
    return conditional_collision211_endpoint_dot(
        tangent,
        repeated_slot,
        singleton[0],
        singleton[1],
        coarse_order=coarse_order,
        fine_order=fine_order,
        value_tolerance=value_tolerance,
        tangent_tolerance=tangent_tolerance,
    )


def _relu_covariance_dot(
    tangent: BridgeStateFrechet, left: int, right: int
) -> tuple[float, float]:
    state = tangent.state
    if left == right:
        value = float(state.relu_scale[left] ** 2)
        dot = float(2.0 * state.relu_scale[left] * tangent.relu_scale_dot[left])
        return value, dot
    value = float(
        state.bridge[left, right]
        * state.relu_scale[left]
        * state.relu_scale[right]
    )
    dot = float(
        tangent.bridge_dot[left, right]
        * state.relu_scale[left]
        * state.relu_scale[right]
        + state.bridge[left, right]
        * tangent.relu_scale_dot[left]
        * state.relu_scale[right]
        + state.bridge[left, right]
        * state.relu_scale[left]
        * tangent.relu_scale_dot[right]
    )
    return value, dot


@dataclass(frozen=True)
class Collision211Certificate:
    central_fourth: float
    central_fourth_tangent: float
    cumulant: float
    cumulant_tangent: float
    tree: float
    tree_tangent: float
    defect: float
    defect_tangent: float
    value_disagreement: float
    tangent_disagreement: float
    coarse_order: int
    fine_order: int
    quadrant_integrand_evaluations: int


def _central211_rule(
    tangent: BridgeStateFrechet,
    repeated: int,
    singleton_left: int,
    singleton_right: int,
    order: int,
) -> tuple[float, float, int]:
    state = tangent.state
    i, j, k = repeated, singleton_left, singleton_right
    sigma_i = float(state.sigma[i])
    sigma_i_dot = float(tangent.sigma_dot[i])
    lower = -float(state.alpha[i])
    lower_dot = -float(tangent.alpha_dot[i])
    beta = state.covariance[(j, k), i] / sigma_i
    beta_dot = (
        tangent.covariance_dot[(j, k), i] / sigma_i
        - beta * sigma_i_dot / sigma_i
    )
    selected = np.asarray((j, k), dtype=int)
    conditional_covariance = state.covariance[np.ix_(selected, selected)].copy()
    conditional_covariance -= np.outer(
        state.covariance[selected, i], state.covariance[selected, i]
    ) / state.covariance[i, i]
    numerator_dot = (
        np.outer(tangent.covariance_dot[selected, i], state.covariance[selected, i])
        + np.outer(state.covariance[selected, i], tangent.covariance_dot[selected, i])
    ) / state.covariance[i, i]
    denominator_dot = (
        np.outer(state.covariance[selected, i], state.covariance[selected, i])
        * tangent.covariance_dot[i, i]
        / state.covariance[i, i] ** 2
    )
    conditional_covariance_dot = (
        tangent.covariance_dot[np.ix_(selected, selected)]
        - numerator_dot
        + denominator_dot
    )
    nodes, weights = _legendre(order)
    t_nodes = 0.5 * (nodes + 1.0)
    t_weights = 0.5 * weights
    values: list[float] = []
    dots: list[float] = []
    evaluations = 0
    for t, weight in zip(t_nodes, t_weights):
        radial = float(t / (1.0 - t))
        jacobian = 1.0 / (1.0 - t) ** 2
        for side in (-1, 1):
            node = lower + side * radial
            node_dot = lower_dot
            density = _pdf(node)
            density_dot = -node * density * node_dot
            conditional_mean = state.mean[selected] + beta * node
            conditional_mean_dot = (
                tangent.mean_dot[selected] + beta_dot * node + beta * node_dot
            )
            pair = bivariate_relu_raw_dot_endpoint(
                conditional_mean,
                conditional_covariance,
                conditional_mean_dot,
                conditional_covariance_dot,
                quadrant_tolerance=5.0e-13,
            )
            evaluations += (
                pair.quadrant.integrand_evaluations
                + pair.moment_integrand_evaluations
            )
            left_mean, left_mean_dot = univariate_relu_mean_dot(
                float(conditional_mean[0]),
                float(conditional_covariance[0, 0]),
                float(conditional_mean_dot[0]),
                float(conditional_covariance_dot[0, 0]),
            )
            right_mean, right_mean_dot = univariate_relu_mean_dot(
                float(conditional_mean[1]),
                float(conditional_covariance[1, 1]),
                float(conditional_mean_dot[1]),
                float(conditional_covariance_dot[1, 1]),
            )
            global_left = float(state.relu_mean[j])
            global_right = float(state.relu_mean[k])
            global_left_dot = float(tangent.relu_mean_dot[j])
            global_right_dot = float(tangent.relu_mean_dot[k])
            conditional_centered = (
                pair.raw
                - global_left * right_mean
                - global_right * left_mean
                + global_left * global_right
            )
            conditional_centered_dot = (
                pair.tangent
                - global_left_dot * right_mean
                - global_left * right_mean_dot
                - global_right_dot * left_mean
                - global_right * left_mean_dot
                + global_left_dot * global_right
                + global_left * global_right_dot
            )
            if side == -1:
                repeated_output = 0.0
                repeated_output_dot = 0.0
            else:
                repeated_output = sigma_i * radial
                repeated_output_dot = sigma_i_dot * radial
            centered_repeated = repeated_output - float(state.relu_mean[i])
            centered_repeated_dot = (
                repeated_output_dot - float(tangent.relu_mean_dot[i])
            )
            common = float(weight) * jacobian
            values.append(
                common
                * density
                * centered_repeated**2
                * conditional_centered
            )
            dots.append(
                common
                * (
                    density_dot
                    * centered_repeated**2
                    * conditional_centered
                    + density
                    * (
                        2.0
                        * centered_repeated
                        * centered_repeated_dot
                        * conditional_centered
                        + centered_repeated**2 * conditional_centered_dot
                    )
                )
            )
    return math.fsum(values), math.fsum(dots), evaluations


def conditional_collision211_endpoint_dot(
    tangent: BridgeStateFrechet,
    repeated: int,
    singleton_left: int,
    singleton_right: int,
    *,
    coarse_order: int = 48,
    fine_order: int = 64,
    value_tolerance: float = 2.0e-8,
    tangent_tolerance: float = 2.0e-7,
) -> Collision211Certificate:
    """Connected ``kappa(Y_i,Y_i,Y_j,Y_k)`` and M129 tree defect.

    The integral is central from the outset:

      E[a_i^2 a_j a_k]
        - Var(Y_i) Cov(Y_j,Y_k)
        - 2 Cov(Y_i,Y_j) Cov(Y_i,Y_k).

    This eliminates the M129 triple Hermite series and all powered bivariate
    partition blocks.  The split tails share the moving ReLU boundary; their
    boundary terms cancel because the centered integrand is continuous there.
    """

    if len({repeated, singleton_left, singleton_right}) != 3:
        raise ValueError("[2,1,1] labels must be distinct")
    n = tangent.state.mean.size
    if not all(0 <= item < n for item in (repeated, singleton_left, singleton_right)):
        raise ValueError("[2,1,1] label outside state")
    coarse = _central211_rule(
        tangent, repeated, singleton_left, singleton_right, coarse_order
    )
    fine = _central211_rule(
        tangent, repeated, singleton_left, singleton_right, fine_order
    )
    value_disagreement = abs(fine[0] - coarse[0])
    tangent_disagreement = abs(fine[1] - coarse[1])
    if value_disagreement > value_tolerance:
        raise EndpointCertificationFailure(
            "central [2,1,1] value paired-order certificate failed"
        )
    if tangent_disagreement > tangent_tolerance:
        raise EndpointCertificationFailure(
            "central [2,1,1] tangent paired-order certificate failed"
        )
    var_i, var_i_dot = _relu_covariance_dot(tangent, repeated, repeated)
    cov_jk, cov_jk_dot = _relu_covariance_dot(
        tangent, singleton_left, singleton_right
    )
    cov_ij, cov_ij_dot = _relu_covariance_dot(
        tangent, repeated, singleton_left
    )
    cov_ik, cov_ik_dot = _relu_covariance_dot(
        tangent, repeated, singleton_right
    )
    cumulant = fine[0] - var_i * cov_jk - 2.0 * cov_ij * cov_ik
    cumulant_dot = (
        fine[1]
        - var_i_dot * cov_jk
        - var_i * cov_jk_dot
        - 2.0 * (cov_ij_dot * cov_ik + cov_ij * cov_ik_dot)
    )
    labels = (repeated, repeated, singleton_left, singleton_right)
    tree, tree_dot = _tree_entry_dot(tangent, labels)
    _require_finite_scalar(fine[0], "central [2,1,1] fourth moment")
    _require_finite_scalar(fine[1], "central [2,1,1] fourth-moment tangent")
    _require_finite_scalar(cumulant, "central [2,1,1] cumulant")
    _require_finite_scalar(cumulant_dot, "central [2,1,1] cumulant tangent")
    _require_finite_scalar(tree, "central [2,1,1] tree")
    _require_finite_scalar(tree_dot, "central [2,1,1] tree tangent")
    return Collision211Certificate(
        fine[0],
        fine[1],
        cumulant,
        cumulant_dot,
        tree,
        tree_dot,
        cumulant - tree,
        cumulant_dot - tree_dot,
        value_disagreement,
        tangent_disagreement,
        coarse_order,
        fine_order,
        coarse[2] + fine[2],
    )
