"""Response-free falsifier for fixed Plackett-line quadrature in M162.

For a centered trivariate normal lower orthant with correlation matrix ``R``,
Plackett's identity along ``R(t)=I+t(R-I)`` gives

    P(R) = 1/8 + integral_0^1 sum_{i<j}
        rho_ij/(4*pi*sqrt(1-t^2 rho_ij^2)) dt.

The conditional third-coordinate CDF is exactly 1/2 in this centered probe.
The integral has the closed form

    1/8 + [asin(rho_01)+asin(rho_02)+asin(rho_12)]/(4*pi).

This module deliberately tests fixed quadrature only.  It neither computes a
general endpoint coefficient nor claims that a parameter-aware certified
Plackett transform is impossible.  It establishes that two natural fixed
rules already miss the stated high-correlation absolute target on an analytic,
response-free subfamily.
"""

from __future__ import annotations

from functools import lru_cache
import math


def _validate_correlation_triplet(rho01: float, rho02: float, rho12: float) -> None:
    values = (float(rho01), float(rho02), float(rho12))
    if not all(math.isfinite(value) and -1.0 <= value <= 1.0 for value in values):
        raise ValueError("correlations must be finite values in [-1, 1]")
    determinant = 1.0 + 2.0 * rho01 * rho02 * rho12 - rho01**2 - rho02**2 - rho12**2
    if determinant < -128.0 * math.ulp(1.0):
        raise ValueError("correlation triplet is not PSD")


@lru_cache(maxsize=None)
def _gauss_legendre_unit_interval(nodes: int) -> tuple[tuple[float, float], ...]:
    """Deterministic Gauss-Legendre nodes on [0,1], used only by the probe."""

    if type(nodes) is not int or nodes <= 0:
        raise ValueError("nodes must be a positive built-in integer")
    pairs: list[tuple[float, float]] = []
    half = (nodes + 1) // 2
    for ordinal in range(1, half + 1):
        root = math.cos(math.pi * (ordinal - 0.25) / (nodes + 0.5))
        for _ in range(100):
            current, previous = 1.0, 0.0
            for degree in range(1, nodes + 1):
                before_previous = previous
                previous = current
                current = (
                    (2 * degree - 1) * root * previous
                    - (degree - 1) * before_previous
                ) / degree
            derivative = nodes * (root * current - previous) / (root * root - 1.0)
            update = current / derivative
            root -= update
            if abs(update) <= 2.0e-16:
                break
        else:
            raise RuntimeError("Legendre root did not converge")
        weight = 2.0 / ((1.0 - root * root) * derivative * derivative)
        pairs.append(((1.0 - root) / 2.0, weight / 2.0))
        if not (nodes % 2 and ordinal == half):
            pairs.append(((1.0 + root) / 2.0, weight / 2.0))
    pairs.sort(key=lambda pair: pair[0])
    return tuple(pairs)


def central_trivariate_orthant_closed_form(
    rho01: float, rho02: float, rho12: float
) -> float:
    """Exact centered three-normal lower-orthant probability for PSD ``R``."""

    _validate_correlation_triplet(rho01, rho02, rho12)
    return 0.125 + (
        math.asin(rho01) + math.asin(rho02) + math.asin(rho12)
    ) / (4.0 * math.pi)


def fixed_plackett_zero_threshold_probability(
    rho01: float,
    rho02: float,
    rho12: float,
    *,
    nodes: int,
    endpoint_square_map: bool,
) -> float:
    """Apply a fixed GL rule to the centered Plackett homotopy integral.

    ``endpoint_square_map`` makes ``t=1-u**2`` before fixed quadrature.  It is
    a plausible endpoint repair, included so the falsifier does not rest on
    the straight-coordinate singularity alone.
    """

    _validate_correlation_triplet(rho01, rho02, rho12)
    total = 0.125
    correlations = (rho01, rho02, rho12)
    for unit_node, weight in _gauss_legendre_unit_interval(nodes):
        if endpoint_square_map:
            t = 1.0 - unit_node * unit_node
            jacobian = 2.0 * unit_node
        else:
            t = unit_node
            jacobian = 1.0
        integrand = 0.0
        for correlation in correlations:
            # Product form avoids cancellation in 1-(t*rho)^2 near a rank face.
            denominator_squared = (1.0 - t * correlation) * (1.0 + t * correlation)
            integrand += correlation / (4.0 * math.pi * math.sqrt(denominator_squared))
        total += weight * jacobian * integrand
    return total


def central_bivariate_orthant_correlation_derivative(rho: float) -> float:
    """Exact d/drho Phi_2(0,0;rho), exposing the rank-face singularity."""

    rho = float(rho)
    if not math.isfinite(rho) or not -1.0 <= rho <= 1.0:
        raise ValueError("rho must be finite in [-1, 1]")
    if abs(rho) == 1.0:
        return math.inf
    return 1.0 / (2.0 * math.pi * math.sqrt((1.0 - rho) * (1.0 + rho)))
