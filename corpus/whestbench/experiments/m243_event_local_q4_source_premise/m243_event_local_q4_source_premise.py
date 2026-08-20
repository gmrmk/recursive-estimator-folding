"""Response-free M243 event-local Q=4 Hermite premise.

This module deliberately implements only the frozen G0A algebraic surface.
It does not construct a B1 state, sample a source proposal, or touch response,
score, challenge-weight, or submission data.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import itertools
import math
import operator
from pathlib import Path
import sys
from typing import Optional, Sequence

import numpy as np


EXPERIMENTS = Path(__file__).resolve().parents[1]
for _relative in ("m178_certified_phi2_owent", "m147_endpoint_safe_bridge"):
    _path = str(EXPERIMENTS / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m178_certified_phi2_owent import evaluate as evaluate_phi2  # noqa: E402
from m147_endpoint_safe_bridge import _tree_entry_dot  # noqa: E402
_EPS = np.finfo(np.float64).eps
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_SQRT_TWO = math.sqrt(2.0)


class M243DomainRefusal(RuntimeError):
    """Typed fail-closed refusal for a request outside the frozen G0A domain."""


@dataclass(frozen=True)
class CertifiedScalar:
    value: float
    radius: float
    lower: float
    upper: float
    contained: bool
    chart: str


@dataclass(frozen=True)
class Q4Packet:
    beta: tuple[float, float, float, float, float]
    repeated_R: tuple[float, float, float, float, float]
    beta_radius: tuple[float, float, float, float, float]
    base_jet_contained: bool
    base_jet_chart: str
    labels: tuple[int, int, int]


@dataclass(frozen=True)
class FoldedEvent:
    value: float
    radius: float
    lower: float
    upper: float
    degree: Optional[int]
    labels: tuple[int, int, int]
    tree: float
    wick_vii_vjk: float
    wick_cross: float
    owner_factor: float
    contained: bool
    pair_charts: tuple[str, ...]


def _cdf(x: float) -> float:
    if not math.isfinite(x):
        if x == math.inf:
            return 1.0
        if x == -math.inf:
            return 0.0
        raise M243DomainRefusal("non-finite normal-CDF input")
    return 0.5 * math.erfc(-x / _SQRT_TWO)


def _pdf(x: float) -> float:
    if not math.isfinite(x):
        if abs(x) == math.inf:
            return 0.0
        raise M243DomainRefusal("non-finite normal-PDF input")
    return _INV_SQRT_2PI * math.exp(-0.5 * x * x)


def _relu_mean(mean: float, variance: float) -> float:
    if not math.isfinite(mean) or not math.isfinite(variance) or variance <= 0.0:
        raise M243DomainRefusal("conditional unary state is not strictly non-degenerate")
    sigma = math.sqrt(variance)
    alpha = mean / sigma
    return sigma * (alpha * _cdf(alpha) + _pdf(alpha))


def _base_state(state):
    base = getattr(state, "state", state)
    required = (
        "mean",
        "covariance",
        "sigma",
        "alpha",
        "relu_mean",
        "relu_scale",
        "bridge",
        "gamma2",
        "gamma3",
    )
    if not all(hasattr(base, name) for name in required):
        raise M243DomainRefusal("state is not an M147/M122 bridge state")
    return base


def _validate_distinct_labels_before_state(i: int, j: int, k: int) -> tuple[int, int, int]:
    try:
        labels = (operator.index(i), operator.index(j), operator.index(k))
    except (TypeError, ValueError, OverflowError) as exc:
        raise M243DomainRefusal("[2,1,1] labels must be integral") from exc
    if len(set(labels)) != 3:
        raise M243DomainRefusal("M243 accepts only three distinct represented labels")
    return labels


def _validate_bounds(base, labels: tuple[int, int, int]) -> None:
    mean = np.asarray(base.mean)
    covariance = np.asarray(base.covariance)
    n = mean.size
    if mean.ndim != 1 or covariance.shape != (n, n):
        raise M243DomainRefusal("invalid bridge-state shape")
    if not all(0 <= label < n for label in labels):
        raise M243DomainRefusal("[2,1,1] label outside state")
    if not np.array_equal(covariance, covariance.T):
        raise M243DomainRefusal("pre-ReLU covariance is not bitwise symmetric")
    selected = np.asarray(labels, dtype=np.int64)
    if not np.all(np.isfinite(mean[selected])) or not np.all(
        np.isfinite(covariance[np.ix_(selected, selected)])
    ):
        raise M243DomainRefusal("selected bridge state is non-finite")


def _canonical_labels4(labels4: Sequence[int]) -> tuple[int, int, int]:
    try:
        labels = tuple(operator.index(value) for value in labels4)
    except (TypeError, ValueError, OverflowError) as exc:
        raise M243DomainRefusal("four-slot owner labels must be integral") from exc
    if len(labels) != 4:
        raise M243DomainRefusal("four-slot owner must contain exactly four labels")
    counts = Counter(labels)
    repeated = [label for label, count in counts.items() if count == 2]
    singletons = sorted(label for label, count in counts.items() if count == 1)
    if len(counts) != 3 or len(repeated) != 1 or len(singletons) != 2:
        raise M243DomainRefusal("M243 emits only the strict [2,1,1] stratum")
    return repeated[0], singletons[0], singletons[1]


def _outward(center: float, radius: float) -> tuple[float, float, float]:
    if not math.isfinite(center) or not math.isfinite(radius) or radius < 0.0:
        raise M243DomainRefusal("non-finite certified interval")
    lower = math.nextafter(center - radius, -math.inf)
    upper = math.nextafter(center + radius, math.inf)
    widened = max(center - lower, upper - center)
    if not all(math.isfinite(value) for value in (lower, upper, widened)):
        raise M243DomainRefusal("certified interval overflow")
    return lower, upper, widened


def _beta_centers(
    *,
    a: float,
    b: float,
    rho: float,
    la: float,
    lb: float,
    p: float,
    q: float,
    sj: float,
    sk: float,
    P: float,
    A: float,
    B: float,
    D: float,
) -> tuple[float, float, float, float, float]:
    delta = (1.0 - rho) * (1.0 + rho)
    phi_a, phi_b = _pdf(a), _pdf(b)
    Phi_a, Phi_b = _cdf(a), _cdf(b)

    H = (a * b + rho) * P + b * A + a * B + delta * D - la * lb
    Ha = b * P + rho * A + B - lb * Phi_a
    Hb = a * P + A + rho * B - la * Phi_b
    Haa = (b - rho * a) * A + delta * D - lb * phi_a
    Hab = P
    Hbb = (a - rho * b) * B + delta * D - la * phi_b

    Haaa = -(rho + a * (b - rho * a)) * A - a * delta * D + a * lb * phi_a
    Haab = A
    Habb = B
    Hbbb = -(rho + b * (a - rho * b)) * B - b * delta * D + b * la * phi_b

    Haaaa = (
        (a * a * (b - rho * a) - b + 3.0 * rho * a) * A
        + (delta * a * a + 2.0 * rho * rho - 1.0) * D
        + (1.0 - a * a) * lb * phi_a
    )
    Haaab = -a * A - rho * D
    Haabb = D
    Habbb = -b * B - rho * D
    Hbbbb = (
        (b * b * (a - rho * b) - a + 3.0 * rho * b) * B
        + (delta * b * b + 2.0 * rho * rho - 1.0) * D
        + (1.0 - b * b) * la * phi_b
    )

    C0 = H
    C1 = p * Ha + q * Hb
    C2 = p * p * Haa + 2.0 * p * q * Hab + q * q * Hbb
    C3 = p**3 * Haaa + 3.0 * p * p * q * Haab + 3.0 * p * q * q * Habb + q**3 * Hbbb
    C4 = (
        p**4 * Haaaa
        + 4.0 * p**3 * q * Haaab
        + 6.0 * p * p * q * q * Haabb
        + 4.0 * p * q**3 * Habbb
        + q**4 * Hbbbb
    )
    physical = sj * sk
    values = (
        physical * C0,
        physical * C1,
        physical * C2 / 2.0,
        physical * C3 / 6.0,
        physical * C4 / 24.0,
    )
    if not all(math.isfinite(value) for value in values):
        raise M243DomainRefusal("non-finite Hermite coefficient")
    return values


def _repeated_addbacks(base, i: int) -> tuple[float, float, float, float, float]:
    sigma = float(base.sigma[i])
    alpha = float(base.alpha[i])
    if not math.isfinite(sigma) or sigma <= 0.0 or not math.isfinite(alpha):
        raise M243DomainRefusal("invalid repeated-coordinate state")
    probability, density = _cdf(alpha), _pdf(alpha)
    mean = sigma * (alpha * probability + density)
    values = (
        sigma * sigma * ((alpha * alpha + 1.0) * probability + alpha * density) - mean * mean,
        2.0 * sigma * mean * (1.0 - probability),
        2.0 * sigma * sigma * probability - 2.0 * sigma * mean * density,
        2.0 * sigma * sigma * density + 2.0 * sigma * mean * alpha * density,
        -2.0 * sigma * sigma * alpha * density
        - 2.0 * sigma * mean * (alpha * alpha - 1.0) * density,
    )
    if not all(math.isfinite(value) for value in values):
        raise M243DomainRefusal("non-finite repeated Hermite add-back")
    return values


def q4_packet(state, i: int, j: int, k: int) -> Q4Packet:
    """Return the frozen Q=4 coefficients from one unconditional M178 jet."""

    labels = _validate_distinct_labels_before_state(i, j, k)
    base = _base_state(state)
    _validate_bounds(base, labels)
    i, j, k = labels
    covariance = np.asarray(base.covariance)
    sigma_i, sj, sk = (float(base.sigma[index]) for index in labels)
    if min(sigma_i, sj, sk) <= 0.0:
        raise M243DomainRefusal("nonpositive marginal scale")
    a = float(base.mean[j]) / sj
    b = float(base.mean[k]) / sk
    rho = float(covariance[j, k]) / (sj * sk)
    p = float(covariance[i, j]) / (sigma_i * sj)
    q = float(covariance[i, k]) / (sigma_i * sk)
    if not all(math.isfinite(value) for value in (a, b, rho, p, q)):
        raise M243DomainRefusal("non-finite standardized singleton state")
    if not -1.0 < rho < 1.0:
        raise M243DomainRefusal("unconditional singleton pair is outside strict SPD")

    jet = evaluate_phi2(a, b, rho)
    if jet.refused:
        raise M243DomainRefusal(f"M178 refused unconditional pair: {jet.reason}")
    la = a * _cdf(a) + _pdf(a)
    lb = b * _cdf(b) + _pdf(b)
    arguments = dict(a=a, b=b, rho=rho, la=la, lb=lb, p=p, q=q, sj=sj, sk=sk)
    beta = _beta_centers(P=jet.value, A=jet.d_a, B=jet.d_b, D=jet.d_rho, **arguments)

    zero = _beta_centers(P=0.0, A=0.0, B=0.0, D=0.0, **arguments)
    widths = (jet.w_value, jet.w_da, jet.w_db, jet.w_drho)
    slopes = []
    for component in range(4):
        basis = [0.0, 0.0, 0.0, 0.0]
        basis[component] = 1.0
        image = _beta_centers(P=basis[0], A=basis[1], B=basis[2], D=basis[3], **arguments)
        slopes.append(tuple(image[index] - zero[index] for index in range(5)))
    beta_radius = []
    for index, center in enumerate(beta):
        radius = math.fsum(abs(slopes[component][index]) * widths[component] for component in range(4))
        radius += 64.0 * _EPS * (1.0 + abs(center))
        _, _, widened = _outward(center, radius)
        beta_radius.append(widened)

    contained = all(
        math.isfinite(value) and value >= 0.0
        for value in (jet.w_value, jet.w_da, jet.w_db, jet.w_drho)
    )
    return Q4Packet(
        tuple(float(value) for value in beta),
        _repeated_addbacks(base, i),
        tuple(float(value) for value in beta_radius),
        contained,
        str(jet.chart),
        labels,
    )


def conditional_centered_pair(state, i: int, j: int, k: int, g: float) -> CertifiedScalar:
    """Return b(g), before any Wick or tree subtraction, with an M178 radius."""

    labels = _validate_distinct_labels_before_state(i, j, k)
    if not math.isfinite(float(g)):
        raise M243DomainRefusal("outer normal coordinate must be finite")
    g = float(g)
    base = _base_state(state)
    _validate_bounds(base, labels)
    i, j, k = labels
    covariance = np.asarray(base.covariance)
    sigma_i = float(base.sigma[i])
    variance_i = sigma_i * sigma_i
    if variance_i <= 0.0:
        raise M243DomainRefusal("repeated coordinate has nonpositive variance")

    spoke_j = float(covariance[j, i])
    spoke_k = float(covariance[k, i])
    mean_j = float(base.mean[j]) + spoke_j * g / sigma_i
    mean_k = float(base.mean[k]) + spoke_k * g / sigma_i
    variance_j = float(covariance[j, j]) - spoke_j * spoke_j / variance_i
    variance_k = float(covariance[k, k]) - spoke_k * spoke_k / variance_i
    covariance_jk = float(covariance[j, k]) - spoke_j * spoke_k / variance_i
    determinant = variance_j * variance_k - covariance_jk * covariance_jk
    if (
        not all(math.isfinite(value) for value in (mean_j, mean_k, variance_j, variance_k, covariance_jk, determinant))
        or variance_j <= 0.0
        or variance_k <= 0.0
        or determinant <= 0.0
    ):
        raise M243DomainRefusal("conditional singleton pair is outside strict SPD")

    sjc, skc = math.sqrt(variance_j), math.sqrt(variance_k)
    a, b = mean_j / sjc, mean_k / skc
    rho = covariance_jk / (sjc * skc)
    if not -1.0 < rho < 1.0:
        raise M243DomainRefusal("conditional singleton correlation is outside strict SPD")
    jet = evaluate_phi2(a, b, rho)
    if jet.refused:
        raise M243DomainRefusal(f"M178 refused conditional pair: {jet.reason}")

    delta = (1.0 - rho) * (1.0 + rho)
    raw_dimensionless = (
        (a * b + rho) * jet.value
        + b * jet.d_a
        + a * jet.d_b
        + delta * jet.d_rho
    )
    raw_pair = sjc * skc * raw_dimensionless
    conditional_relu_j = _relu_mean(mean_j, variance_j)
    conditional_relu_k = _relu_mean(mean_k, variance_k)
    global_j, global_k = float(base.relu_mean[j]), float(base.relu_mean[k])
    centered = (
        raw_pair
        - global_j * conditional_relu_k
        - global_k * conditional_relu_j
        + global_j * global_k
    )
    radius = abs(sjc * skc) * (
        abs(a * b + rho) * jet.w_value
        + abs(b) * jet.w_da
        + abs(a) * jet.w_db
        + abs(delta) * jet.w_drho
    )
    radius += 64.0 * _EPS * (1.0 + abs(raw_pair))
    radius += 64.0 * _EPS * (1.0 + abs(centered))
    lower, upper, radius = _outward(centered, radius)
    return CertifiedScalar(centered, radius, lower, upper, True, str(jet.chart))


def _post_covariance(base, left: int, right: int) -> float:
    return float(base.relu_scale[left]) * float(base.relu_scale[right]) * float(base.bridge[left, right])


def _tree_primal(base, labels: tuple[int, int, int]) -> float:
    i, j, k = labels
    expanded = (i, i, j, k)
    scale_product = math.prod(float(base.relu_scale[label]) for label in expanded)
    stars = []
    for centre in range(4):
        root = expanded[centre]
        star = float(base.gamma3[root])
        for position in range(4):
            if position != centre:
                star *= float(base.bridge[root, expanded[position]])
        stars.append(star)
    paths = []
    for permutation in itertools.permutations(range(4)):
        a, b, c, d = (expanded[position] for position in permutation)
        paths.append(
            float(base.gamma2[b])
            * float(base.gamma2[c])
            * float(base.bridge[a, b])
            * float(base.bridge[b, c])
            * float(base.bridge[c, d])
        )
    answer = scale_product * (math.fsum(stars) + 0.5 * math.fsum(paths))
    if not math.isfinite(answer):
        raise M243DomainRefusal("non-finite M122/M126 tree")
    return answer


def _tree(state, base, labels: tuple[int, int, int]) -> float:
    if getattr(state, "state", None) is base:
        try:
            value, _ = _tree_entry_dot(
                state, (labels[0], labels[0], labels[1], labels[2])
            )
            if math.isfinite(value):
                return float(value)
        except (AttributeError, TypeError, ValueError):
            pass
    return _tree_primal(base, labels)


def _hermites(g: float) -> tuple[float, float, float, float, float]:
    g2 = g * g
    return (1.0, g, g2 - 1.0, g * g2 - 3.0 * g, g2 * g2 - 6.0 * g2 + 3.0)


def _repeated_value(base, i: int, g: float) -> float:
    rectified = max(0.0, float(base.mean[i]) + float(base.sigma[i]) * g)
    centered = rectified - float(base.relu_mean[i])
    value = centered * centered
    if not math.isfinite(value):
        raise M243DomainRefusal("non-finite repeated-coordinate factor")
    return value


def _round_guard(center: float) -> float:
    return 64.0 * _EPS * (1.0 + abs(center))


def folded_distinct_event(
    state,
    labels4: Sequence[int],
    g: float,
    *,
    degree: Optional[int],
) -> FoldedEvent:
    """Evaluate the raw, Q2, or Q4 event under the frozen ownership rules."""

    labels = _canonical_labels4(labels4)
    if degree not in (None, 2, 4):
        raise M243DomainRefusal("degree must be None, 2, or 4")
    if not math.isfinite(float(g)):
        raise M243DomainRefusal("outer normal coordinate must be finite")
    g = float(g)
    base = _base_state(state)
    _validate_bounds(base, labels)
    i, j, k = labels
    tree = _tree(state, base, labels)
    vii = _post_covariance(base, i, i)
    vjk = _post_covariance(base, j, k)
    vij = _post_covariance(base, i, j)
    vik = _post_covariance(base, i, k)
    wick_vii_vjk = vii * vjk
    wick_cross = 2.0 * vij * vik
    constants = wick_vii_vjk + wick_cross + tree

    plus = conditional_centered_pair(state, i, j, k, g)
    r_plus = _repeated_value(base, i, g)
    charts = (plus.chart,)
    if degree is None:
        product = r_plus * plus.value
        r_plus_radius = _round_guard(r_plus)
        radius = (
            abs(r_plus) * plus.radius
            + abs(plus.value) * r_plus_radius
            + r_plus_radius * plus.radius
            + _round_guard(product)
        )
        center = product - constants
        radius += _round_guard(center)
    else:
        packet = q4_packet(state, i, j, k)
        minus = conditional_centered_pair(state, i, j, k, -g)
        r_minus = _repeated_value(base, i, -g)
        charts = (plus.chart, minus.chart, packet.base_jet_chart)
        count = degree + 1
        h_plus = _hermites(g)
        h_minus = _hermites(-g)
        polynomial_plus = math.fsum(packet.beta[index] * h_plus[index] for index in range(count))
        polynomial_minus = math.fsum(packet.beta[index] * h_minus[index] for index in range(count))
        polynomial_plus_radius = math.fsum(
            abs(h_plus[index]) * packet.beta_radius[index] for index in range(count)
        )
        polynomial_minus_radius = math.fsum(
            abs(h_minus[index]) * packet.beta_radius[index] for index in range(count)
        )
        polynomial_plus_radius += _round_guard(polynomial_plus)
        polynomial_minus_radius += _round_guard(polynomial_minus)
        residual_plus = plus.value - polynomial_plus
        residual_minus = minus.value - polynomial_minus
        residual_plus_radius = plus.radius + polynomial_plus_radius + _round_guard(residual_plus)
        residual_minus_radius = minus.radius + polynomial_minus_radius + _round_guard(residual_minus)
        term_plus = r_plus * residual_plus
        term_minus = r_minus * residual_minus
        r_plus_radius = _round_guard(r_plus)
        r_minus_radius = _round_guard(r_minus)
        term_plus_radius = (
            abs(r_plus) * residual_plus_radius
            + abs(residual_plus) * r_plus_radius
            + r_plus_radius * residual_plus_radius
            + _round_guard(term_plus)
        )
        term_minus_radius = (
            abs(r_minus) * residual_minus_radius
            + abs(residual_minus) * r_minus_radius
            + r_minus_radius * residual_minus_radius
            + _round_guard(term_minus)
        )
        addback = math.fsum(packet.beta[index] * packet.repeated_R[index] for index in range(count))
        addback_radius = math.fsum(
            abs(packet.repeated_R[index]) * packet.beta_radius[index] for index in range(count)
        )
        addback_radius += _round_guard(addback)
        antithetic = 0.5 * (term_plus + term_minus)
        antithetic_radius = 0.5 * (term_plus_radius + term_minus_radius) + _round_guard(antithetic)
        center = antithetic + addback - constants
        radius = antithetic_radius + addback_radius + _round_guard(center)

    lower, upper, radius = _outward(center, radius)
    return FoldedEvent(
        center,
        radius,
        lower,
        upper,
        degree,
        labels,
        tree,
        wick_vii_vjk,
        wick_cross,
        0.5,
        True,
        charts,
    )


__all__ = [
    "CertifiedScalar",
    "FoldedEvent",
    "M243DomainRefusal",
    "Q4Packet",
    "conditional_centered_pair",
    "folded_distinct_event",
    "q4_packet",
]
