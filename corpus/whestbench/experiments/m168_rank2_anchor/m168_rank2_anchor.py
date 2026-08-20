"""Response-free rank-two anchor for the connected ``[2,1,1]`` defect.

This module is deliberately a high-precision mathematical *reference*, not a
runtime endpoint provider.  At a positive-marginal, transverse rank-two
Gaussian state, ``X = mu + L Z`` with ``Z ~ N(0, I_2)``, it computes the
anchor and its Price tangent from:

* planar ReLU-wedge integrals for the 12 Tallis raw moments; and
* exact one-dimensional coarea integrals on the three kink boundaries.

The raw planar integrals use an adaptive ``mpmath`` outer integration only to
validate the identity.  There is no interval enclosure, fixed-node rule,
native operation trace, ridge, clipping, retry, or provider registration.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations
from math import factorial
from typing import Iterable

import mpmath as mp


class Rank2AnchorDomainError(RuntimeError):
    """Raised when a state lies outside the transverse positive-marginal face."""


_LABELS = (0, 0, 1, 2)
_SQRT_2PI = mp.sqrt(2 * mp.pi)


@dataclass(frozen=True)
class Rank2AnchorCertificate:
    """Reference value/tangent and transparent primitive inventory.

    ``cone_mode`` describes only first-order PSD feasibility.  It is not a
    numerical error certificate and does not authorize a generic endpoint.
    """

    defect: mp.mpf
    tangent: mp.mpf
    cumulant: mp.mpf
    cumulant_tangent: mp.mpf
    tree: mp.mpf
    tree_tangent: mp.mpf
    raw_moments: int
    planar_wedge_moments: int
    indicator_wedge_moments: int
    exact_boundary_moments: int
    cone_mode: str
    method: str


def _phi(value: mp.mpf) -> mp.mpf:
    return mp.exp(-value * value / 2) / _SQRT_2PI


def _Phi(value: mp.mpf) -> mp.mpf:
    return mp.erfc(-value / mp.sqrt(2)) / 2


def _as_vector(value: Iterable[object], *, length: int, label: str) -> tuple[mp.mpf, ...]:
    answer = tuple(mp.mpf(item) for item in value)
    if len(answer) != length or not all(mp.isfinite(item) for item in answer):
        raise Rank2AnchorDomainError(f"{label} must contain {length} finite entries")
    return answer


def _as_matrix(
    value: Iterable[Iterable[object]], *, rows: int, columns: int, label: str
) -> tuple[tuple[mp.mpf, ...], ...]:
    answer = tuple(tuple(mp.mpf(item) for item in row) for row in value)
    if (
        len(answer) != rows
        or any(len(row) != columns for row in answer)
        or not all(mp.isfinite(item) for row in answer for item in row)
    ):
        raise Rank2AnchorDomainError(f"{label} must be a finite {rows} by {columns} matrix")
    return answer


def _dot(left: tuple[mp.mpf, ...], right: tuple[mp.mpf, ...]) -> mp.mpf:
    return mp.fsum(a * b for a, b in zip(left, right))


def _covariance_from_factor(factor: tuple[tuple[mp.mpf, mp.mpf], ...]) -> tuple[tuple[mp.mpf, ...], ...]:
    return tuple(tuple(_dot(left, right) for right in factor) for left in factor)


def _null_normal(factor: tuple[tuple[mp.mpf, mp.mpf], ...]) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    column0 = tuple(row[0] for row in factor)
    column1 = tuple(row[1] for row in factor)
    normal = (
        column0[1] * column1[2] - column0[2] * column1[1],
        column0[2] * column1[0] - column0[0] * column1[2],
        column0[0] * column1[1] - column0[1] * column1[0],
    )
    length = mp.sqrt(_dot(normal, normal))
    if not length:
        raise Rank2AnchorDomainError("factor does not have rank two")
    return tuple(item / length for item in normal)  # type: ignore[return-value]


def _validate_transverse_factor(
    mean: tuple[mp.mpf, ...], factor: tuple[tuple[mp.mpf, mp.mpf], ...]
) -> None:
    del mean  # Positive marginal variances depend only on the factor.
    _null_normal(factor)
    for index, row in enumerate(factor):
        if not _dot(row, row):
            raise Rank2AnchorDomainError(f"zero marginal variance at coordinate {index}")
    for left in range(3):
        for right in range(left + 1, 3):
            determinant = factor[left][0] * factor[right][1] - factor[left][1] * factor[right][0]
            if not determinant:
                raise Rank2AnchorDomainError(
                    "nontransverse rank-two face: a pair of ReLU kink lines is parallel"
                )


def _validate_labels(labels: tuple[int, int, int, int]) -> None:
    if len(labels) != 4 or any(type(index) is not int or index not in (0, 1, 2) for index in labels):
        raise ValueError("labels must be four built-in coordinate indices in {0,1,2}")
    counts = tuple(labels.count(index) for index in range(3))
    if sorted(counts) != [1, 1, 2]:
        raise ValueError("labels must describe one [2,1,1] collision")


def _rotate_for_slice(
    factor: tuple[tuple[mp.mpf, mp.mpf], ...]
) -> tuple[tuple[mp.mpf, mp.mpf], ...]:
    """Choose a deterministic orthogonal Gaussian gauge with no vertical kink.

    The factor is only a representation of ``LL^T``.  This rotation is used
    for slicing, never as a change to the physical coordinates.
    """

    best: tuple[tuple[mp.mpf, mp.mpf], ...] | None = None
    best_margin = mp.mpf(-1)
    for ordinal in range(1, 48):
        angle = mp.pi * ordinal / 47
        cosine, sine = mp.cos(angle), mp.sin(angle)
        rotated = tuple(
            (row[0] * cosine + row[1] * sine, -row[0] * sine + row[1] * cosine)
            for row in factor
        )
        margin = min(abs(row[1]) for row in rotated)
        if margin > best_margin:
            best, best_margin = rotated, margin
    if best is None or not best_margin:
        raise Rank2AnchorDomainError("could not select a nonvertical planar slice")
    return best


def _normal_interval_moments(lower: mp.mpf, upper: mp.mpf, maximum: int) -> tuple[mp.mpf, ...]:
    """``int_lower^upper t^q phi(t) dt`` through order ``maximum`` exactly."""

    if lower >= upper:
        return tuple(mp.mpf(0) for _ in range(maximum + 1))
    values = [mp.mpf(0)] * (maximum + 1)
    values[0] = _Phi(upper) - _Phi(lower)
    if maximum:
        values[1] = _phi(lower) - _phi(upper)
    for degree in range(2, maximum + 1):
        lower_term = mp.mpf(0) if mp.isinf(lower) else lower ** (degree - 1) * _phi(lower)
        upper_term = mp.mpf(0) if mp.isinf(upper) else upper ** (degree - 1) * _phi(upper)
        values[degree] = lower_term - upper_term + (degree - 1) * values[degree - 2]
    return tuple(values)


def _multiply_linear_power(
    coefficients: list[mp.mpf], intercept: mp.mpf, slope: mp.mpf, power: int
) -> list[mp.mpf]:
    for _ in range(power):
        updated = [mp.mpf(0)] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            updated[degree] += intercept * coefficient
            updated[degree + 1] += slope * coefficient
        coefficients = updated
    return coefficients


def _univariate_positive_product(
    terms: Iterable[tuple[mp.mpf, mp.mpf, int]]
) -> mp.mpf:
    """Exact normal integral of active affine positive-part powers.

    Every supplied term imposes a strict-positive half-line.  A zero power is
    therefore an indicator rather than an absent factor.
    """

    lower, upper = -mp.inf, mp.inf
    polynomial = [mp.mpf(1)]
    for intercept, slope, power in terms:
        if slope == 0:
            if intercept <= 0:
                return mp.mpf(0)
            if power:
                polynomial = _multiply_linear_power(polynomial, intercept, 0, power)
            continue
        root = -intercept / slope
        if slope > 0:
            lower = max(lower, root)
        else:
            upper = min(upper, root)
        if power:
            polynomial = _multiply_linear_power(polynomial, intercept, slope, power)
    moments = _normal_interval_moments(lower, upper, len(polynomial) - 1)
    return mp.fsum(coefficient * moments[degree] for degree, coefficient in enumerate(polynomial))


def _outer_cuts(
    mean: tuple[mp.mpf, ...],
    factor: tuple[tuple[mp.mpf, mp.mpf], ...],
    powers: tuple[int, int, int],
    indicators: frozenset[int],
) -> tuple[mp.mpf, ...]:
    active = [index for index, power in enumerate(powers) if power or index in indicators]
    cuts = {mp.mpf(0)}
    for position, left in enumerate(active):
        a_left, b_left = factor[left]
        slope_left, intercept_left = -a_left / b_left, -mean[left] / b_left
        for right in active[position + 1 :]:
            a_right, b_right = factor[right]
            slope_right, intercept_right = -a_right / b_right, -mean[right] / b_right
            if slope_left != slope_right:
                cuts.add((intercept_right - intercept_left) / (slope_left - slope_right))
    return tuple(sorted(cuts))


def _raw_wedge_moment(
    mean: tuple[mp.mpf, ...],
    factor: tuple[tuple[mp.mpf, mp.mpf], ...],
    powers: tuple[int, int, int],
    indicators: frozenset[int] = frozenset(),
) -> mp.mpf:
    """Planar Gaussian wedge integral for one Tallis raw moment.

    Conditioning on the first canonical-plane coordinate converts each wedge
    section to exact normal interval moments.  Breaks are precisely the
    pairwise kink-line intersections, so the remaining integral has a fixed
    wedge ordering on every interval.
    """

    if powers == (0, 0, 0) and not indicators:
        return mp.mpf(1)
    sliced = _rotate_for_slice(factor)
    cuts = _outer_cuts(mean, sliced, powers, indicators)

    def integrand(first: mp.mpf) -> mp.mpf:
        terms = tuple(
            (mean[index] + sliced[index][0] * first, sliced[index][1], power)
            for index, power in enumerate(powers)
            if power or index in indicators
        )
        return _phi(first) * _univariate_positive_product(terms)

    endpoints = (-mp.inf,) + cuts + (mp.inf,)
    return mp.quad(integrand, endpoints)


def _boundary_moment(
    mean: tuple[mp.mpf, ...],
    factor: tuple[tuple[mp.mpf, mp.mpf], ...],
    index: int,
    powers: tuple[int, int, int],
) -> mp.mpf:
    """Coarea integral ``E[delta(X_i) product X_j+^p_j]`` on one kink line."""

    row = factor[index]
    norm_squared = _dot(row, row)
    norm = mp.sqrt(norm_squared)
    base = tuple(-mean[index] * component / norm_squared for component in row)
    tangent = (-row[1] / norm, row[0] / norm)
    terms = []
    for other, power in enumerate(powers):
        if other == index or not power:
            continue
        intercept = mean[other] + _dot(factor[other], base)
        slope = _dot(factor[other], tangent)
        terms.append((intercept, slope, power))
    return _phi(mean[index] / norm) * _univariate_positive_product(terms) / norm


def _decrement(powers: tuple[int, int, int], index: int, amount: int = 1) -> tuple[int, int, int]:
    answer = list(powers)
    answer[index] -= amount
    if answer[index] < 0:
        raise ValueError("negative raw-moment power")
    return tuple(answer)  # type: ignore[return-value]


def _required_powers(labels: tuple[int, int, int, int]) -> tuple[tuple[int, int, int], ...]:
    """All raw cache entries required by a collision cumulant and M129 tree."""

    needed: set[tuple[int, int, int]] = set()
    for subset_size in range(5):
        for subset in combinations(range(4), subset_size):
            needed.add(tuple(sum(labels[slot] == index for slot in subset) for index in range(3)))
    for index in range(3):
        needed.add(tuple(2 if position == index else 0 for position in range(3)))
    for left in range(3):
        for right in range(left + 1, 3):
            needed.add(tuple(1 if position in (left, right) else 0 for position in range(3)))
    return tuple(sorted(needed))


def _raw_cache_and_price_tangent(
    mean: tuple[mp.mpf, ...],
    factor: tuple[tuple[mp.mpf, mp.mpf], ...],
    mean_dot: tuple[mp.mpf, ...],
    covariance_dot: tuple[tuple[mp.mpf, ...], ...],
    labels: tuple[int, int, int, int],
) -> tuple[dict[tuple[int, int, int], mp.mpf], dict[tuple[int, int, int], mp.mpf], int, int, int]:
    required = _required_powers(labels)

    def raw_value(powers: tuple[int, int, int]) -> mp.mpf:
        active = [index for index, power in enumerate(powers) if power]
        if len(active) <= 1:
            if not active:
                return mp.mpf(1)
            index = active[0]
            sigma = mp.sqrt(_dot(factor[index], factor[index]))
            return _univariate_positive_product(((mean[index], sigma, powers[index]),))
        return _raw_wedge_moment(mean, factor, powers)

    raw = {powers: raw_value(powers) for powers in required}
    boundary: dict[tuple[int, tuple[int, int, int]], mp.mpf] = {}
    indicator_moment: dict[tuple[tuple[int, int, int], frozenset[int]], mp.mpf] = {}

    def moment_value(powers: tuple[int, int, int], indicators: frozenset[int]) -> mp.mpf:
        if not indicators:
            return raw[powers]
        key = (powers, indicators)
        if key not in indicator_moment:
            active = {index for index, power in enumerate(powers) if power} | set(indicators)
            if len(active) <= 1:
                if not active:
                    indicator_moment[key] = mp.mpf(1)
                else:
                    index = next(iter(active))
                    sigma = mp.sqrt(_dot(factor[index], factor[index]))
                    indicator_moment[key] = _univariate_positive_product(
                        ((mean[index], sigma, powers[index]),)
                    )
            else:
                indicator_moment[key] = _raw_wedge_moment(mean, factor, powers, indicators)
        return indicator_moment[key]

    def first_derivative_factor(powers: tuple[int, int, int], index: int) -> mp.mpf:
        lowered = _decrement(powers, index)
        indicators = frozenset((index,)) if powers[index] == 1 else frozenset()
        return powers[index] * moment_value(lowered, indicators)

    def boundary_value(index: int, powers: tuple[int, int, int]) -> mp.mpf:
        key = (index, powers)
        if key not in boundary:
            boundary[key] = _boundary_moment(mean, factor, index, powers)
        return boundary[key]

    raw_dot: dict[tuple[int, int, int], mp.mpf] = {}
    for powers in required:
        derivative = mp.fsum(
            mean_dot[index] * first_derivative_factor(powers, index)
            for index in range(3)
            if powers[index]
        )
        for index in range(3):
            power = powers[index]
            if power == 1:
                derivative += covariance_dot[index][index] * boundary_value(
                    index, _decrement(powers, index)
                ) / 2
            elif power == 2:
                derivative += covariance_dot[index][index] * moment_value(
                    _decrement(powers, index, 2), frozenset((index,))
                )
        for left in range(3):
            for right in range(left + 1, 3):
                if powers[left] and powers[right]:
                    lowered = _decrement(_decrement(powers, left), right)
                    indicators = frozenset(
                        index for index in (left, right) if powers[index] == 1
                    )
                    derivative += (
                        covariance_dot[left][right]
                        * powers[left]
                        * powers[right]
                        * moment_value(lowered, indicators)
                    )
        raw_dot[powers] = derivative
    planar_wedges = sum(1 for powers in required if sum(power > 0 for power in powers) >= 2)
    indicator_wedges = sum(
        1
        for powers, indicators in indicator_moment
        if len({index for index, power in enumerate(powers) if power} | set(indicators)) >= 2
    )
    return raw, raw_dot, len(boundary), planar_wedges, indicator_wedges


def _set_partitions(items: tuple[int, ...]):
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in _set_partitions(rest):
        yield ((first,),) + partition
        for position in range(len(partition)):
            yield partition[:position] + (partition[position] + (first,),) + partition[position + 1 :]


def _raw_for_labels(
    raw: dict[tuple[int, int, int], mp.mpf],
    raw_dot: dict[tuple[int, int, int], mp.mpf],
    labels: tuple[int, ...],
) -> tuple[mp.mpf, mp.mpf]:
    powers = tuple(labels.count(index) for index in range(3))
    return raw[powers], raw_dot[powers]


def _mul_dual(left: tuple[mp.mpf, mp.mpf], right: tuple[mp.mpf, mp.mpf]) -> tuple[mp.mpf, mp.mpf]:
    return left[0] * right[0], left[1] * right[0] + left[0] * right[1]


def _cumulant(
    raw: dict[tuple[int, int, int], mp.mpf],
    raw_dot: dict[tuple[int, int, int], mp.mpf],
    labels: tuple[int, int, int, int],
) -> tuple[mp.mpf, mp.mpf]:
    value = mp.mpf(0)
    tangent = mp.mpf(0)
    for partition in _set_partitions((0, 1, 2, 3)):
        coefficient = factorial(len(partition) - 1) * (-1) ** (len(partition) - 1)
        product = (mp.mpf(1), mp.mpf(0))
        for block in partition:
            product = _mul_dual(product, _raw_for_labels(raw, raw_dot, tuple(labels[slot] for slot in block)))
        value += coefficient * product[0]
        tangent += coefficient * product[1]
    return value, tangent


def _tree(
    mean: tuple[mp.mpf, ...],
    factor: tuple[tuple[mp.mpf, mp.mpf], ...],
    mean_dot: tuple[mp.mpf, ...],
    covariance_dot: tuple[tuple[mp.mpf, ...], ...],
    raw: dict[tuple[int, int, int], mp.mpf],
    raw_dot: dict[tuple[int, int, int], mp.mpf],
    labels: tuple[int, int, int, int],
) -> tuple[mp.mpf, mp.mpf]:
    covariance = _covariance_from_factor(factor)
    sigma = tuple(mp.sqrt(covariance[index][index]) for index in range(3))
    sigma_dot = tuple(covariance_dot[index][index] / (2 * sigma[index]) for index in range(3))
    alpha = tuple(mean[index] / sigma[index] for index in range(3))
    alpha_dot = tuple(
        mean_dot[index] / sigma[index] - alpha[index] * sigma_dot[index] / sigma[index]
        for index in range(3)
    )
    phi = tuple(_phi(value) for value in alpha)
    cdf = tuple(_Phi(value) for value in alpha)
    h1 = tuple(sigma[index] * cdf[index] for index in range(3))
    h2 = tuple(sigma[index] * phi[index] for index in range(3))
    h3 = tuple(-sigma[index] * alpha[index] * phi[index] for index in range(3))
    h1_dot = tuple(
        sigma_dot[index] * cdf[index] + sigma[index] * phi[index] * alpha_dot[index]
        for index in range(3)
    )
    h2_dot = tuple(
        sigma_dot[index] * phi[index] - sigma[index] * alpha[index] * phi[index] * alpha_dot[index]
        for index in range(3)
    )
    h3_dot = tuple(
        -sigma_dot[index] * alpha[index] * phi[index]
        + sigma[index] * (alpha[index] ** 2 - 1) * phi[index] * alpha_dot[index]
        for index in range(3)
    )
    relu_mean = tuple(
        raw[tuple(1 if position == index else 0 for position in range(3))]
        for index in range(3)
    )
    relu_mean_dot = tuple(raw_dot[tuple(1 if position == index else 0 for position in range(3))] for index in range(3))
    second = tuple(raw[tuple(2 if position == index else 0 for position in range(3))] for index in range(3))
    second_dot = tuple(raw_dot[tuple(2 if position == index else 0 for position in range(3))] for index in range(3))
    scale = tuple(mp.sqrt(second[index] - relu_mean[index] ** 2) for index in range(3))
    scale_dot = tuple(
        (second_dot[index] - 2 * relu_mean[index] * relu_mean_dot[index]) / (2 * scale[index])
        for index in range(3)
    )
    q = [[mp.mpf(0) for _ in range(3)] for _ in range(3)]
    q_dot = [[mp.mpf(0) for _ in range(3)] for _ in range(3)]
    for index in range(3):
        q[index][index] = mp.mpf(1)
    for left in range(3):
        for right in range(left + 1, 3):
            powers = tuple((1 if coordinate in (left, right) else 0) for coordinate in range(3))
            centered = raw[powers] - relu_mean[left] * relu_mean[right]
            centered_dot = raw_dot[powers] - relu_mean_dot[left] * relu_mean[right] - relu_mean[left] * relu_mean_dot[right]
            denominator = scale[left] * scale[right]
            q[left][right] = q[right][left] = centered / denominator
            q_dot[left][right] = q_dot[right][left] = centered_dot / denominator - q[left][right] * (
                scale_dot[left] / scale[left] + scale_dot[right] / scale[right]
            )
    gamma2 = tuple(h2[index] * scale[index] / h1[index] ** 2 for index in range(3))
    gamma3 = tuple(h3[index] * scale[index] ** 2 / h1[index] ** 3 for index in range(3))
    gamma2_dot = tuple(
        (h2_dot[index] * scale[index] + h2[index] * scale_dot[index]) / h1[index] ** 2
        - 2 * h2[index] * scale[index] * h1_dot[index] / h1[index] ** 3
        for index in range(3)
    )
    gamma3_dot = tuple(
        (h3_dot[index] * scale[index] ** 2 + 2 * h3[index] * scale[index] * scale_dot[index]) / h1[index] ** 3
        - 3 * h3[index] * scale[index] ** 2 * h1_dot[index] / h1[index] ** 4
        for index in range(3)
    )
    scale_product = (mp.mpf(1), mp.mpf(0))
    for label in labels:
        scale_product = _mul_dual(scale_product, (scale[label], scale_dot[label]))
    star = (mp.mpf(0), mp.mpf(0))
    for centre_position, centre in enumerate(labels):
        item = (gamma3[centre], gamma3_dot[centre])
        for position, leaf in enumerate(labels):
            if position != centre_position:
                item = _mul_dual(item, (q[centre][leaf], q_dot[centre][leaf]))
        star = star[0] + item[0], star[1] + item[1]
    path = (mp.mpf(0), mp.mpf(0))
    for ordering in permutations(range(4)):
        a, b, c, d = (labels[position] for position in ordering)
        item = _mul_dual((gamma2[b], gamma2_dot[b]), (gamma2[c], gamma2_dot[c]))
        item = _mul_dual(item, (q[a][b], q_dot[a][b]))
        item = _mul_dual(item, (q[b][c], q_dot[b][c]))
        item = _mul_dual(item, (q[c][d], q_dot[c][d]))
        path = path[0] + item[0], path[1] + item[1]
    return _mul_dual(scale_product, (star[0] + path[0] / 2, star[1] + path[1] / 2))


def _cone_mode(
    factor: tuple[tuple[mp.mpf, mp.mpf], ...], covariance_dot: tuple[tuple[mp.mpf, ...], ...]
) -> str:
    normal = _null_normal(factor)
    opening = mp.fsum(normal[left] * covariance_dot[left][right] * normal[right] for left in range(3) for right in range(3))
    if opening < 0:
        raise Rank2AnchorDomainError("covariance direction points outside the PSD tangent cone")
    if opening > 0:
        return "one-sided-rank-three-opening"
    cross = tuple(mp.fsum(covariance_dot[index][other] * normal[other] for other in range(3)) for index in range(3))
    tangent_component = tuple(
        cross[index] - normal[index] * opening for index in range(3)
    )
    if any(component != 0 for component in tangent_component):
        return "tangent-cone-second-order-completion-required"
    return "rank-preserving-face-tangent"


def rank2_transverse_anchor_dot(
    mean: Iterable[object],
    factor: Iterable[Iterable[object]],
    mean_dot: Iterable[object],
    covariance_dot: Iterable[Iterable[object]],
    *,
    labels: tuple[int, int, int, int] = _LABELS,
    dps: int = 50,
) -> Rank2AnchorCertificate:
    """Derive the rank-two anchor and Price tangent in a canonical 2D plane.

    Preconditions are rank two, positive marginal variances, and pairwise
    transverse kink lines.  ``covariance_dot`` may open the null normal only
    one-sidedly.  At an opening direction the returned derivative is the
    limit of Price's SPD identity: the only distributional pieces are the
    coarea boundary integrals implemented above.
    """

    if type(dps) is not int or dps < 35:
        raise ValueError("dps must be a built-in integer of at least 35")
    _validate_labels(labels)
    with mp.workdps(dps):
        local_mean = _as_vector(mean, length=3, label="mean")
        local_factor = _as_matrix(factor, rows=3, columns=2, label="factor")
        local_mean_dot = _as_vector(mean_dot, length=3, label="mean_dot")
        local_covariance_dot = _as_matrix(covariance_dot, rows=3, columns=3, label="covariance_dot")
        if any(local_covariance_dot[left][right] != local_covariance_dot[right][left] for left in range(3) for right in range(3)):
            raise Rank2AnchorDomainError("covariance_dot must be exactly symmetric")
        _validate_transverse_factor(local_mean, local_factor)
        cone_mode = _cone_mode(local_factor, local_covariance_dot)
        raw, raw_dot, boundaries, planar_wedges, indicator_wedges = _raw_cache_and_price_tangent(
            local_mean, local_factor, local_mean_dot, local_covariance_dot, labels
        )
        cumulant, cumulant_dot = _cumulant(raw, raw_dot, labels)
        tree, tree_dot = _tree(
            local_mean,
            local_factor,
            local_mean_dot,
            local_covariance_dot,
            raw,
            raw_dot,
            labels,
        )
        return Rank2AnchorCertificate(
            + (cumulant - tree),
            + (cumulant_dot - tree_dot),
            +cumulant,
            +cumulant_dot,
            +tree,
            +tree_dot,
            len(raw),
            planar_wedges,
            indicator_wedges,
            boundaries,
            cone_mode,
            "rank2-planar-wedge-plus-price-coarea-reference-only",
        )


def rank2_anchor_cost_envelope(*, angular_nodes: int) -> dict[str, int | bool | str]:
    """Transparent, non-creditable bookkeeping envelope for a fused rule.

    This does *not* certify that any fixed node count is accurate.  The 256-op
    cell-monomial allowance is a deliberately conservative accounting model,
    not a native bill.  It makes the remaining ``606720`` constraint explicit.
    """

    if type(angular_nodes) is not int or angular_nodes <= 0:
        raise ValueError("angular_nodes must be a positive built-in integer")
    wedge_cells_upper = 7
    raw_monomials = 11
    extra_tree_univariate_moments = 2
    indicator_tangent_moments = 20
    boundary_moments = 16
    radial_intervals_per_boundary_upper = 3
    allowance_per_kernel = 256
    setup_and_tree_ops = 4_096
    lower_structural_primitives = (
        raw_monomials + extra_tree_univariate_moments + indicator_tangent_moments + boundary_moments
    )
    upper = (
        setup_and_tree_ops
        + wedge_cells_upper * (raw_monomials + indicator_tangent_moments) * allowance_per_kernel * angular_nodes
        + boundary_moments * radial_intervals_per_boundary_upper * allowance_per_kernel
    )
    return {
        "per_coefficient_ceiling": 606_720,
        "irreducible_nonconstant_tallis_raw_moments": raw_monomials,
        "additional_univariate_tree_moments": extra_tree_univariate_moments,
        "price_indicator_tangent_moments": indicator_tangent_moments,
        "irreducible_exact_boundary_moments": boundary_moments,
        "structural_primitive_lower_bound": lower_structural_primitives,
        "fused_wedge_cells_upper": wedge_cells_upper,
        "bookkeeping_ops_upper": upper,
        "fits_bookkeeping_ceiling": upper <= 606_720,
        "native_bill_proved": False,
        "uniform_error_certificate_proved": False,
        "credit": "none: reference inventory only, not a provider cost certificate",
    }
