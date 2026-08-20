"""M154 analytic moving-kink endpoint partition for the rank-one [2,1,1] stratum.

The M149 failure was caused by a fixed outer quadrature over the conditioning
normal.  This component takes the only part of the proposed replacement that
can be made finite without introducing a new trivariate-normal numerical
primitive: an exact rank-one factor branch.

For ``X = mean + a Z`` every ReLU gate changes only at one scalar endpoint.
The real line is partitioned at those moving endpoints, and each active cell
is a polynomial times the standard-normal density.  Its value uses finite
normal interval moments.  Its Frechet/directional derivative uses Price's
identity, including the delta boundary produced by the second derivative of
``x_+``.  There is no grid, quadrature order, ridge, clipping, retry, or
fallback computation in this provider.

The rank-two and rank-three strata are intentionally refused.  A rank-two
three-ReLU product has a Gaussian integral over a generic three-line planar
cell; a rank-three product contains a noncentral trivariate orthant
probability.  Tallis/Rosenbaum reduce their *moments* to derivatives of that
truncation probability, but do not remove the probability itself.  Owen's T
is a bivariate primitive, so admitting those strata here would silently
reintroduce the unresolved one-dimensional numerical integral that M149 was
asked to replace.  The refusal preserves this useful rank-one identity
without presenting it as a generic M151 provider.

This file is generated-state mathematics only.  It has no model, response,
truth, scorer, leaderboard, submission, or champion dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from pathlib import Path
import sys
from typing import Literal

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for relative in ("m147_endpoint_safe_bridge", "m129_source_frechet_tangent"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m147_endpoint_safe_bridge import (  # noqa: E402
    EndpointCertificationFailure,
)
from m129_source_frechet import power_hermite_coefficient_dot  # noqa: E402


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_EPS = np.finfo(np.float64).eps
_RANK_TOL_FACTOR = 2048.0
_TANGENT_TOL_FACTOR = 4096.0


class Analytic211Failure(EndpointCertificationFailure):
    """The analytic rank-one contract cannot certify the supplied request."""


@dataclass(frozen=True)
class RawMoment:
    """One rank-one ReLU monomial and its Price directional derivative."""

    value: float
    tangent: float
    analytic_intervals: int
    boundary_evaluations: int


@dataclass(frozen=True)
class Analytic211Certificate:
    """Exact rank-one local [2,1,1] moment/cumulant/tree certificate."""

    central_fourth: float
    central_fourth_tangent: float
    cumulant: float
    cumulant_tangent: float
    tree: float
    tree_tangent: float
    defect: float
    defect_tangent: float
    rank: int
    analytic_intervals: int
    boundary_evaluations: int
    special_function_calls: int
    conservative_billed_ops: int
    derivative_kind: str
    method: str


# A factor is ``(kind, ReLU power, scalar multiplier, coordinate)``.  The
# ``step`` and ``delta`` kinds arise only in Price derivatives; the production
# value path itself consists solely of ReLU powers.
FactorKind = Literal["relu", "step", "delta"]
Factor = tuple[FactorKind, int, float, int]


def _require_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise Analytic211Failure(f"non-finite {label}")
    return value


def _cdf(value: float) -> float:
    if value == math.inf:
        return 1.0
    if value == -math.inf:
        return 0.0
    if not math.isfinite(value):
        raise Analytic211Failure("non-finite Gaussian CDF argument")
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def _pdf(value: float) -> float:
    if abs(value) == math.inf:
        return 0.0
    if not math.isfinite(value):
        raise Analytic211Failure("non-finite Gaussian PDF argument")
    return _INV_SQRT_2PI * math.exp(-0.5 * value * value)


def _boundary_power(value: float, density: float, power: int) -> float:
    if density == 0.0 or not math.isfinite(value):
        return 0.0
    try:
        result = value**power * density
    except OverflowError as error:
        raise Analytic211Failure("normal interval boundary moment overflow") from error
    return _require_finite(result, "normal interval boundary moment")


def _normal_interval_moments(lower: float, upper: float, maximum: int) -> np.ndarray:
    """Exact ``int_lower^upper z^q phi(z) dz`` through ``maximum``."""

    if maximum < 0 or lower > upper:
        raise Analytic211Failure("invalid analytic interval request")
    moments = np.zeros(maximum + 1, dtype=np.float64)
    probability = _cdf(upper) - _cdf(lower)
    if probability < -64.0 * _EPS:
        raise Analytic211Failure("negative normal interval probability")
    moments[0] = probability
    if maximum == 0 or probability == 0.0:
        return moments
    density_lower, density_upper = _pdf(lower), _pdf(upper)
    moments[1] = density_lower - density_upper
    for power in range(2, maximum + 1):
        moments[power] = (
            _boundary_power(lower, density_lower, power - 1)
            - _boundary_power(upper, density_upper, power - 1)
            + (power - 1) * moments[power - 2]
        )
    if not np.all(np.isfinite(moments)):
        raise Analytic211Failure("non-finite normal interval moments")
    return moments


def _multiply_affine_power(
    polynomial: np.ndarray, intercept: float, slope: float, power: int
) -> np.ndarray:
    """Multiply a coefficient vector by ``(intercept + slope*z)**power``."""

    if power < 0:
        raise Analytic211Failure("negative ReLU power")
    result = polynomial.copy()
    for _ in range(power):
        next_result = np.zeros(result.size + 1, dtype=np.float64)
        next_result[:-1] += intercept * result
        next_result[1:] += slope * result
        result = next_result
    if not np.all(np.isfinite(result)):
        raise Analytic211Failure("analytic polynomial overflow")
    return result


def _strictly_positive_on_interval(
    intercept: float, slope: float, lower: float, upper: float
) -> bool:
    """Decide an affine gate's sign without unsafe midpoint arithmetic."""

    if slope == 0.0:
        return intercept > 0.0
    root = -intercept / slope
    if not math.isfinite(root):
        raise Analytic211Failure("non-finite moving ReLU endpoint")
    # Every cell endpoint is a gate root.  Open cells beginning at root are
    # positive for positive slope; cells ending at root are positive for
    # negative slope.  Equality is therefore the correct side convention.
    return lower >= root if slope > 0.0 else upper <= root


def _analytic_factor_expectation(
    mean: np.ndarray, latent: np.ndarray, factors: tuple[Factor, ...]
) -> tuple[float, int, int]:
    """Evaluate products of ReLU/step/delta factors on a rank-one line."""

    if not factors:
        return 1.0, 0, 0
    delta_factors = [factor for factor in factors if factor[0] == "delta"]
    if len(delta_factors) > 1:
        # No term used by the second-order Price derivative can contain two
        # deltas.  Treating a delta product as a number would be invalid.
        raise Analytic211Failure("unsupported coincident delta boundary")
    multiplier = math.prod(factor[2] for factor in factors)
    _require_finite(multiplier, "analytic factor multiplier")
    if multiplier == 0.0:
        return 0.0, 0, 0

    if delta_factors:
        _kind, _power, _scale, coordinate = delta_factors[0]
        slope = float(latent[coordinate])
        intercept = float(mean[coordinate])
        if slope == 0.0:
            if intercept == 0.0:
                raise Analytic211Failure("ReLU kink has positive mass under rank-one law")
            return 0.0, 0, 0
        endpoint = -intercept / slope
        density = _pdf(endpoint) / abs(slope)
        value = multiplier * density
        for kind, power, _scale, index in factors:
            if kind == "delta":
                continue
            affine = float(mean[index] + latent[index] * endpoint)
            if affine <= 0.0:
                return 0.0, 0, 1
            if kind == "relu":
                try:
                    value *= affine**power
                except OverflowError as error:
                    raise Analytic211Failure("delta-boundary ReLU moment overflow") from error
        return _require_finite(value, "delta-boundary moment"), 0, 1

    endpoints: list[float] = []
    for kind, _power, _scale, index in factors:
        if kind not in {"relu", "step"}:
            raise Analytic211Failure("unknown analytic factor kind")
        slope = float(latent[index])
        if slope != 0.0:
            endpoint = -float(mean[index]) / slope
            if not math.isfinite(endpoint):
                raise Analytic211Failure("non-finite moving ReLU endpoint")
            endpoints.append(endpoint)
    endpoints = sorted(set(endpoints))
    boundaries = [-math.inf, *endpoints, math.inf]
    total: list[float] = []
    active_cells = 0
    for lower, upper in zip(boundaries[:-1], boundaries[1:]):
        polynomial = np.array([multiplier], dtype=np.float64)
        active = True
        for kind, power, _scale, index in factors:
            intercept, slope = float(mean[index]), float(latent[index])
            if not _strictly_positive_on_interval(intercept, slope, lower, upper):
                active = False
                break
            if kind == "relu":
                polynomial = _multiply_affine_power(polynomial, intercept, slope, power)
        if not active:
            continue
        moments = _normal_interval_moments(lower, upper, polynomial.size - 1)
        total.append(math.fsum(float(coefficient) * float(moment) for coefficient, moment in zip(polynomial, moments, strict=True)))
        active_cells += 1
    return _require_finite(math.fsum(total), "analytic interval expectation"), active_cells, 0


def _base_factors(powers: tuple[int, int, int]) -> tuple[Factor, ...]:
    return tuple(("relu", power, 1.0, index) for index, power in enumerate(powers) if power)


def _first_derivative_factor(power: int, index: int) -> Factor:
    if power == 1:
        return "step", 0, 1.0, index
    if power == 2:
        return "relu", 1, 2.0, index
    raise Analytic211Failure("unsupported first ReLU derivative")


def _second_derivative_factor(power: int, index: int) -> Factor:
    if power == 1:
        return "delta", 0, 1.0, index
    if power == 2:
        return "step", 0, 2.0, index
    raise Analytic211Failure("unsupported second ReLU derivative")


def _replace_factor(
    powers: tuple[int, int, int], coordinate: int, replacement: Factor
) -> tuple[Factor, ...]:
    factors: list[Factor] = []
    for index, power in enumerate(powers):
        if not power:
            continue
        factors.append(replacement if index == coordinate else ("relu", power, 1.0, index))
    return tuple(factors)


def _replace_two_factors(
    powers: tuple[int, int, int], left: int, right: int
) -> tuple[Factor, ...]:
    factors: list[Factor] = []
    for index, power in enumerate(powers):
        if not power:
            continue
        if index == left or index == right:
            factors.append(_first_derivative_factor(power, index))
        else:
            factors.append(("relu", power, 1.0, index))
    return tuple(factors)


def _raw_rank_one_moment_dot(
    mean: np.ndarray,
    latent: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    powers: tuple[int, int, int],
) -> RawMoment:
    """Raw rank-one ReLU monomial and directional derivative by Price."""

    value, intervals, boundaries = _analytic_factor_expectation(
        mean, latent, _base_factors(powers)
    )
    tangent = 0.0
    for coordinate, power in enumerate(powers):
        if not power or mean_dot[coordinate] == 0.0:
            continue
        derivative, cells, boundary_count = _analytic_factor_expectation(
            mean, latent, _replace_factor(powers, coordinate, _first_derivative_factor(power, coordinate))
        )
        tangent += float(mean_dot[coordinate]) * derivative
        intervals += cells
        boundaries += boundary_count
    for coordinate, power in enumerate(powers):
        if not power or covariance_dot[coordinate, coordinate] == 0.0:
            continue
        derivative, cells, boundary_count = _analytic_factor_expectation(
            mean, latent, _replace_factor(powers, coordinate, _second_derivative_factor(power, coordinate))
        )
        tangent += 0.5 * float(covariance_dot[coordinate, coordinate]) * derivative
        intervals += cells
        boundaries += boundary_count
    for left in range(3):
        for right in range(left + 1, 3):
            if (
                not powers[left]
                or not powers[right]
                or covariance_dot[left, right] == 0.0
            ):
                continue
            derivative, cells, boundary_count = _analytic_factor_expectation(
                mean, latent, _replace_two_factors(powers, left, right)
            )
            tangent += float(covariance_dot[left, right]) * derivative
            intervals += cells
            boundaries += boundary_count
    return RawMoment(
        _require_finite(value, "raw rank-one moment"),
        _require_finite(tangent, "raw rank-one moment tangent"),
        intervals,
        boundaries,
    )


def _rank_one_factor(covariance: np.ndarray) -> tuple[np.ndarray, int]:
    """Classify PSD rank without modifying the supplied covariance."""

    scale = max(1.0, float(np.max(np.abs(covariance))))
    rank_tolerance = _RANK_TOL_FACTOR * _EPS * scale
    eigenvalues = np.linalg.eigvalsh(covariance)
    if not np.all(np.isfinite(eigenvalues)) or float(np.min(eigenvalues)) < -rank_tolerance:
        raise Analytic211Failure("local covariance is not PSD")
    rank = int(np.count_nonzero(eigenvalues > rank_tolerance))
    if rank == 2:
        raise Analytic211Failure(
            "rank-2 moving-three-line stratum requires a Gaussian triangle primitive; refused"
        )
    if rank != 1:
        raise Analytic211Failure(
            "rank-3 noncentral trivariate-orthant stratum requires an unpriced primitive; refused"
        )
    pivot = int(np.argmax(np.diag(covariance)))
    if covariance[pivot, pivot] <= 0.0:
        raise Analytic211Failure("rank-one covariance has no positive pivot")
    latent = covariance[:, pivot] / math.sqrt(float(covariance[pivot, pivot]))
    reconstruction = np.outer(latent, latent)
    residual = float(np.max(np.abs(covariance - reconstruction)))
    if residual > rank_tolerance:
        raise Analytic211Failure("rank-one covariance factorization does not certify")
    return latent, rank


def _require_rank_one_tangent_feasible(latent: np.ndarray, covariance_dot: np.ndarray) -> None:
    """Check the exact first-order PSD tangent-cone conditions at rank one."""

    direction_norm = float(np.linalg.norm(latent))
    if direction_norm <= 0.0 or not math.isfinite(direction_norm):
        raise Analytic211Failure("invalid rank-one direction")
    unit = latent / direction_norm
    # The null-space basis is used only for an invariant cone test; no factor
    # or covariance entry is modified by this computation.
    _, _, vectors = np.linalg.svd(unit.reshape(1, 3), full_matrices=True)
    null = vectors[1:].T
    null_tangent = null.T @ covariance_dot @ null
    null_tangent = 0.5 * (null_tangent + null_tangent.T)
    eigenvalues, eigenvectors = np.linalg.eigh(null_tangent)
    scale = max(1.0, float(np.max(np.abs(covariance_dot))))
    tolerance = _TANGENT_TOL_FACTOR * _EPS * scale
    if float(np.min(eigenvalues)) < -tolerance:
        raise Analytic211Failure("rank-one PSD tangent points outside the cone")
    # Cross terms between the rank-one line and its null space are allowed:
    # ``(a+t a_dot)(a+t a_dot)^T`` has such a first derivative and is PSD
    # after its necessary second-order completion.  The tangent-cone test is
    # therefore precisely the nonnegative null-space quadratic form above.


def _multiply_polynomials(
    left: dict[tuple[int, int, int], tuple[float, float]],
    right: dict[tuple[int, int, int], tuple[float, float]],
) -> dict[tuple[int, int, int], tuple[float, float]]:
    result: dict[tuple[int, int, int], tuple[float, float]] = {}
    for left_power, (left_value, left_dot) in left.items():
        for right_power, (right_value, right_dot) in right.items():
            power = tuple(a + b for a, b in zip(left_power, right_power, strict=True))
            previous_value, previous_dot = result.get(power, (0.0, 0.0))
            result[power] = (
                previous_value + left_value * right_value,
                previous_dot + left_dot * right_value + left_value * right_dot,
            )
    return result


def _central_211_rank_one(
    mean: np.ndarray,
    latent: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
) -> tuple[float, float, dict[tuple[int, int, int], RawMoment]]:
    cache: dict[tuple[int, int, int], RawMoment] = {}

    def raw(powers: tuple[int, int, int]) -> RawMoment:
        if powers not in cache:
            cache[powers] = _raw_rank_one_moment_dot(
                mean, latent, mean_dot, covariance_dot, powers
            )
        return cache[powers]

    marginal = [raw(tuple(1 if slot == index else 0 for slot in range(3))) for index in range(3)]
    # Preserve every one/two-point raw moment explicitly.  Some central
    # polynomial coefficients vanish at symmetric means, but the M129 tree
    # continuation still requires the corresponding covariance entries.
    for left in range(3):
        for right in range(left, 3):
            raw(tuple((1 if slot == left else 0) + (1 if slot == right else 0) for slot in range(3)))
    first = {(2, 0, 0): (1.0, 0.0), (1, 0, 0): (-2.0 * marginal[0].value, -2.0 * marginal[0].tangent), (0, 0, 0): (marginal[0].value**2, 2.0 * marginal[0].value * marginal[0].tangent)}
    second = {(0, 1, 0): (1.0, 0.0), (0, 0, 0): (-marginal[1].value, -marginal[1].tangent)}
    third = {(0, 0, 1): (1.0, 0.0), (0, 0, 0): (-marginal[2].value, -marginal[2].tangent)}
    expansion = _multiply_polynomials(_multiply_polynomials(first, second), third)
    central = 0.0
    central_dot = 0.0
    for powers, (coefficient, coefficient_dot) in expansion.items():
        moment = raw(powers)
        central += coefficient * moment.value
        central_dot += coefficient_dot * moment.value + coefficient * moment.tangent
    return (
        _require_finite(central, "rank-one central [2,1,1] moment"),
        _require_finite(central_dot, "rank-one central [2,1,1] tangent"),
        cache,
    )


def _covariance_from_raw(
    cache: dict[tuple[int, int, int], RawMoment], left: int, right: int
) -> tuple[float, float]:
    one_left = tuple(1 if slot == left else 0 for slot in range(3))
    one_right = tuple(1 if slot == right else 0 for slot in range(3))
    pair = tuple(a + b for a, b in zip(one_left, one_right, strict=True))
    raw_pair = cache.get(pair)
    if raw_pair is None:
        raise Analytic211Failure("central expansion did not retain a covariance raw moment")
    first_left, first_right = cache[one_left], cache[one_right]
    value = raw_pair.value - first_left.value * first_right.value
    tangent = (
        raw_pair.tangent
        - first_left.tangent * first_right.value
        - first_left.value * first_right.tangent
    )
    return _require_finite(value, "rank-one ReLU covariance"), _require_finite(tangent, "rank-one ReLU covariance tangent")


def _dual_product(items: tuple[tuple[float, float], ...]) -> tuple[float, float]:
    value, tangent = 1.0, 0.0
    for item_value, item_tangent in items:
        tangent = tangent * item_value + value * item_tangent
        value *= item_value
    return _require_finite(value, "tree product"), _require_finite(tangent, "tree product tangent")


def _rank_one_tree_continuation(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    cache: dict[tuple[int, int, int], RawMoment],
) -> tuple[float, float]:
    """M129's repeated tree algebra, evaluated from exact rank-one moments.

    Avoiding a round-tripped correlation is important here: after a positive
    gauge, an exactly rank-one pair can round just outside ``[-1,1]`` despite
    the supplied factor certifying rank one.  This direct form has no clip.
    """

    sigma = np.sqrt(np.diag(covariance))
    sigma_dot = np.diag(covariance_dot) / (2.0 * sigma)
    alpha = mean / sigma
    alpha_dot = mean_dot / sigma - alpha * sigma_dot / sigma
    h1 = np.empty(3, dtype=np.float64)
    h2 = np.empty(3, dtype=np.float64)
    h3 = np.empty(3, dtype=np.float64)
    h1_dot = np.empty(3, dtype=np.float64)
    h2_dot = np.empty(3, dtype=np.float64)
    h3_dot = np.empty(3, dtype=np.float64)
    for index in range(3):
        arguments = (
            float(alpha[index]),
            float(sigma[index]),
            1,
        )
        direction = (float(alpha_dot[index]), float(sigma_dot[index]))
        h1[index], h1_dot[index] = power_hermite_coefficient_dot(*arguments, 1, *direction)
        h2[index], h2_dot[index] = power_hermite_coefficient_dot(*arguments, 2, *direction)
        h3[index], h3_dot[index] = power_hermite_coefficient_dot(*arguments, 3, *direction)
    scale = np.empty(3, dtype=np.float64)
    scale_dot = np.empty(3, dtype=np.float64)
    q = np.eye(3, dtype=np.float64)
    q_dot = np.zeros((3, 3), dtype=np.float64)
    for left in range(3):
        variance, variance_dot = _covariance_from_raw(cache, left, left)
        if variance <= 0.0:
            raise Analytic211Failure("rank-one ReLU scale is degenerate")
        scale[left] = math.sqrt(variance)
        scale_dot[left] = variance_dot / (2.0 * scale[left])
    for left in range(3):
        for right in range(left + 1, 3):
            covariance_value, covariance_tangent = _covariance_from_raw(cache, left, right)
            denominator = scale[left] * scale[right]
            q[left, right] = q[right, left] = covariance_value / denominator
            q_dot[left, right] = q_dot[right, left] = (
                covariance_tangent / denominator
                - q[left, right] * (scale_dot[left] / scale[left] + scale_dot[right] / scale[right])
            )
    gamma2 = h2 * scale / (h1 * h1)
    gamma3 = h3 * scale * scale / (h1 * h1 * h1)
    gamma2_dot = (
        (h2_dot * scale + h2 * scale_dot) / (h1 * h1)
        - 2.0 * h2 * scale * h1_dot / (h1**3)
    )
    gamma3_dot = (
        (h3_dot * scale * scale + 2.0 * h3 * scale * scale_dot) / (h1**3)
        - 3.0 * h3 * scale * scale * h1_dot / (h1**4)
    )
    if not all(np.all(np.isfinite(item)) for item in (scale, scale_dot, q, q_dot, gamma2, gamma2_dot, gamma3, gamma3_dot)):
        raise Analytic211Failure("non-finite rank-one tree continuation")
    labels = (0, 0, 1, 2)
    scale_product = _dual_product(tuple((float(scale[index]), float(scale_dot[index])) for index in labels))
    star_value = star_dot = 0.0
    for centre_position, centre in enumerate(labels):
        factors = [(float(gamma3[centre]), float(gamma3_dot[centre]))]
        for position, leaf in enumerate(labels):
            if position != centre_position:
                factors.append((float(q[centre, leaf]), float(q_dot[centre, leaf])))
        value, tangent = _dual_product(tuple(factors))
        star_value += value
        star_dot += tangent
    path_value = path_dot = 0.0
    for permutation in itertools.permutations(range(4)):
        a, b, c, d = (labels[position] for position in permutation)
        value, tangent = _dual_product(
            (
                (float(gamma2[b]), float(gamma2_dot[b])),
                (float(gamma2[c]), float(gamma2_dot[c])),
                (float(q[a, b]), float(q_dot[a, b])),
                (float(q[b, c]), float(q_dot[b, c])),
                (float(q[c, d]), float(q_dot[c, d])),
            )
        )
        path_value += value
        path_dot += tangent
    total = (star_value + 0.5 * path_value, star_dot + 0.5 * path_dot)
    return _dual_product((scale_product, total))


def analytic_rank1_collision211_local_state_dot(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    *,
    repeated_slot: int = 0,
) -> Analytic211Certificate:
    """Exact rank-one nonzero-mean ``[2,1,1]`` coefficient and tangent.

    This is intentionally a stratum provider, not a generic replacement for
    M149.  ``repeated_slot`` is accepted only at zero because the source
    owner has already canonicalized the repeated label before its 3x3 gather.
    The singleton pair is intrinsically symmetric.
    """

    arrays = tuple(np.asarray(value, dtype=np.float64) for value in (mean, covariance, mean_dot, covariance_dot))
    local_mean, local_covariance, local_mean_dot, local_covariance_dot = arrays
    if (
        local_mean.shape != (3,)
        or local_mean_dot.shape != (3,)
        or local_covariance.shape != (3, 3)
        or local_covariance_dot.shape != (3, 3)
        or repeated_slot != 0
        or not np.array_equal(local_covariance, local_covariance.T)
        or not np.array_equal(local_covariance_dot, local_covariance_dot.T)
        or not all(np.all(np.isfinite(value)) for value in arrays)
    ):
        raise Analytic211Failure("invalid analytic local [2,1,1] state")
    if np.any(np.diag(local_covariance) <= 0.0):
        raise Analytic211Failure("analytic rank-one branch requires positive marginal variances")
    latent, rank = _rank_one_factor(local_covariance)
    _require_rank_one_tangent_feasible(latent, local_covariance_dot)
    central, central_dot, cache = _central_211_rank_one(
        local_mean, latent, local_mean_dot, local_covariance_dot
    )
    variance, variance_dot = _covariance_from_raw(cache, 0, 0)
    covariance_12, covariance_12_dot = _covariance_from_raw(cache, 1, 2)
    covariance_01, covariance_01_dot = _covariance_from_raw(cache, 0, 1)
    covariance_02, covariance_02_dot = _covariance_from_raw(cache, 0, 2)
    cumulant = central - variance * covariance_12 - 2.0 * covariance_01 * covariance_02
    cumulant_dot = (
        central_dot
        - variance_dot * covariance_12
        - variance * covariance_12_dot
        - 2.0 * (covariance_01_dot * covariance_02 + covariance_01 * covariance_02_dot)
    )
    tree, tree_dot = _rank_one_tree_continuation(
        local_mean,
        local_covariance,
        local_mean_dot,
        local_covariance_dot,
        cache,
    )
    analytic_intervals = sum(moment.analytic_intervals for moment in cache.values())
    boundary_evaluations = sum(moment.boundary_evaluations for moment in cache.values())
    # The fixed structural cap below dominates this particular cache's at-most
    # twelve raw monomials, Price first/second derivatives, three exact
    # rank-one pair trees, and scalar allocations.  It is a source-only cost
    # bound; it does not claim a generic M151 provider is available.
    conservative_billed_ops = 250_000
    return Analytic211Certificate(
        central,
        central_dot,
        _require_finite(cumulant, "rank-one [2,1,1] cumulant"),
        _require_finite(cumulant_dot, "rank-one [2,1,1] cumulant tangent"),
        _require_finite(float(tree), "rank-one tree"),
        _require_finite(float(tree_dot), "rank-one tree tangent"),
        _require_finite(cumulant - float(tree), "rank-one [2,1,1] defect"),
        _require_finite(cumulant_dot - float(tree_dot), "rank-one [2,1,1] defect tangent"),
        rank,
        analytic_intervals,
        boundary_evaluations,
        0,
        conservative_billed_ops,
        "one-sided-PSD-directional-at-rank-one",
        "analytic-rank1-moving-kink-partition-price",
    )


def analytic_rank1_cost_bound(*, coefficient_calls: int) -> dict[str, int | bool | str]:
    """Hard arithmetic-only bound for the retained rank-one stratum kernel."""

    if type(coefficient_calls) is not int or coefficient_calls <= 0:
        raise ValueError("coefficient_calls must be a positive built-in integer")
    per_coefficient = 250_000
    total = coefficient_calls * per_coefficient
    allowance = 10_291_363_760
    return {
        "coefficient_calls": coefficient_calls,
        "analytic_intervals_per_coefficient_upper": 480,
        "boundary_evaluations_per_coefficient_upper": 36,
        "special_function_calls_per_coefficient": 0,
        "conservative_billed_ops_per_coefficient": per_coefficient,
        "total_billed_ops": total,
        "m151_inclusive_allowance_ops": allowance,
        "fits_m151_inclusive_allowance": total <= allowance,
        "scope": "rank-one stratum only; not a generic provider credit",
    }
