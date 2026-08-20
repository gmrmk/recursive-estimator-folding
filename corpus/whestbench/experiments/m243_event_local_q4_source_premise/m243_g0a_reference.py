"""Independent pure-mpmath reference for the frozen M243 G0A gate.

This module never imports the candidate, M147, M178, NumPy, or SciPy.  Every
fixture number arrives through ``mp.mpf(repr(float(x)))`` and the bivariate
positive-part moment, Hermite projections, Wick terms, and M122/M126 tree are
assembled here independently.  It is reference support for the one-shot G0A
runner only; importing it performs no quadrature and creates no artifact.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import itertools
import math
from typing import Callable, Sequence

from mpmath import mp


QUAD_RELATIVE_ERROR_LIMIT = mp.mpf("1e-11")
OUTER_PANEL_TEXT = (
    "-inf", "-16", "-10", "-8", "-5", "-2.5", "-1", "-.25",
    "0", ".25", "1", "2.5", "5", "8", "10", "16", "+inf",
)


class M243ReferenceFailure(RuntimeError):
    """Fail-closed independent-oracle error."""


def binary_mpf(value: object):
    """Ingest exactly one generated binary64 fixture scalar."""

    return mp.mpf(repr(float(value)))


def normal_pdf(value):
    return mp.exp(-(value * value) / 2) / mp.sqrt(2 * mp.pi)


def normal_cdf(value):
    return mp.erfc(-value / mp.sqrt(2)) / 2


def relu_mean(mean, variance):
    if variance <= 0:
        raise M243ReferenceFailure("nonpositive unary variance")
    sigma = mp.sqrt(variance)
    alpha = mean / sigma
    return sigma * (alpha * normal_cdf(alpha) + normal_pdf(alpha))


def relu_second(mean, variance):
    if variance <= 0:
        raise M243ReferenceFailure("nonpositive unary variance")
    sigma = mp.sqrt(variance)
    alpha = mean / sigma
    return sigma**2 * (
        (alpha**2 + 1) * normal_cdf(alpha) + alpha * normal_pdf(alpha)
    )


def hermites(value):
    square = value * value
    return (
        mp.one,
        value,
        square - 1,
        value * square - 3 * value,
        square * square - 6 * square + 3,
    )


def outer_panel_points(alpha):
    points = []
    for text in OUTER_PANEL_TEXT:
        if text == "-inf":
            points.append(mp.ninf)
        elif text == "+inf":
            points.append(mp.inf)
        else:
            points.append(mp.mpf(text))
    points.append(-alpha)
    points.sort()
    deduplicated = []
    for point in points:
        if not deduplicated or point != deduplicated[-1]:
            deduplicated.append(point)
    return tuple(deduplicated)


@dataclass
class QuadAudit:
    """Observable maxdegree-12 composite-quadrature ledger."""

    dps: int
    checkpoint: Callable[[], None] | None = None

    def __post_init__(self):
        self.composite_count = 0
        self.panel_call_count = 0
        self.max_error_ratio = mp.zero
        self.worst_label = None
        self.family_counts = Counter()

    def integrate(self, function, points: Sequence, label: str):
        values = []
        errors = []
        for panel_index, (left, right) in enumerate(zip(points[:-1], points[1:])):
            if self.checkpoint is not None:
                self.checkpoint()
            if left == right:
                values.append(mp.zero)
                errors.append(mp.zero)
                continue
            observed = mp.quad(
                function,
                [left, right],
                method="tanh-sinh",
                maxdegree=12,
                error=True,
            )
            if not isinstance(observed, tuple) or len(observed) != 2:
                raise M243ReferenceFailure(
                    f"mp.quad did not return value/error for {label} panel {panel_index}"
                )
            value, error = observed
            if not mp.isfinite(value) or not mp.isfinite(error) or error < 0:
                raise M243ReferenceFailure(
                    f"nonfinite quadrature receipt for {label} panel {panel_index}"
                )
            values.append(value)
            errors.append(abs(error))
            self.panel_call_count += 1
        total = mp.fsum(values)
        error_sum = mp.fsum(errors)
        ratio = error_sum / (1 + abs(total))
        self.composite_count += 1
        family = label.split(":", 1)[0]
        self.family_counts[family] += 1
        if ratio > self.max_error_ratio:
            self.max_error_ratio = ratio
            self.worst_label = label
        if ratio > QUAD_RELATIVE_ERROR_LIMIT:
            raise M243ReferenceFailure(
                f"maxdegree=12 composite error cap failed for {label}: {ratio}"
            )
        if self.checkpoint is not None:
            self.checkpoint()
        return total, error_sum

    def receipt(self):
        return {
            "dps": self.dps,
            "composite_count": self.composite_count,
            "panel_call_count": self.panel_call_count,
            "max_error_ratio": self.max_error_ratio,
            "worst_label": self.worst_label,
            "family_counts": dict(sorted(self.family_counts.items())),
            "limit": QUAD_RELATIVE_ERROR_LIMIT,
        }


def phi2(a, b, rho, audit: QuadAudit, label: str):
    """Independent Phi2 using exactly sixteen directed rho panels."""

    points = tuple(rho * index / 16 for index in range(17))

    def density(correlation):
        delta = (1 - correlation) * (1 + correlation)
        if delta <= 0:
            raise M243ReferenceFailure("Phi2 rho panel left strict SPD")
        return mp.exp(
            -(a * a - 2 * correlation * a * b + b * b) / (2 * delta)
        ) / (2 * mp.pi * mp.sqrt(delta))

    correction, _ = audit.integrate(density, points, f"phi2:{label}")
    return normal_cdf(a) * normal_cdf(b) + correction


def positive_part_raw(
    mean_left,
    variance_left,
    mean_right,
    variance_right,
    covariance,
    audit: QuadAudit,
    label: str,
):
    if variance_left <= 0 or variance_right <= 0:
        raise M243ReferenceFailure("pair has nonpositive marginal variance")
    scale_left = mp.sqrt(variance_left)
    scale_right = mp.sqrt(variance_right)
    a = mean_left / scale_left
    b = mean_right / scale_right
    rho = covariance / (scale_left * scale_right)
    delta = (1 - rho) * (1 + rho)
    if delta <= 0:
        raise M243ReferenceFailure("pair is outside strict SPD")
    probability = phi2(a, b, rho, audit, label)
    derivative_a = normal_pdf(a) * normal_cdf((b - rho * a) / mp.sqrt(delta))
    derivative_b = normal_pdf(b) * normal_cdf((a - rho * b) / mp.sqrt(delta))
    derivative_rho = mp.exp(
        -(a * a - 2 * rho * a * b + b * b) / (2 * delta)
    ) / (2 * mp.pi * mp.sqrt(delta))
    raw = scale_left * scale_right * (
        (a * b + rho) * probability
        + b * derivative_a
        + a * derivative_b
        + delta * derivative_rho
    )
    return {
        "raw": raw,
        "a": a,
        "b": b,
        "rho": rho,
        "P": probability,
        "A": derivative_a,
        "B": derivative_b,
        "D": derivative_rho,
    }


@dataclass
class MPBridgeState:
    mean: tuple
    covariance: tuple
    sigma: tuple
    alpha: tuple
    relu_mean: tuple
    relu_variance: tuple
    relu_scale: tuple
    post_covariance: tuple
    bridge: tuple
    gamma2: tuple
    gamma3: tuple


def build_bridge_state(mean_values, covariance_values, audit: QuadAudit, label: str):
    mean = tuple(binary_mpf(value) for value in mean_values)
    covariance = tuple(
        tuple(binary_mpf(value) for value in row) for row in covariance_values
    )
    width = len(mean)
    if width == 0 or len(covariance) != width or any(len(row) != width for row in covariance):
        raise M243ReferenceFailure("invalid bridge fixture shape")
    for left in range(width):
        for right in range(width):
            if covariance[left][right] != covariance[right][left]:
                raise M243ReferenceFailure("bridge fixture is not exactly symmetric")
    matrix = mp.matrix(covariance)
    for order in range(1, width + 1):
        principal = mp.matrix([[covariance[i][j] for j in range(order)] for i in range(order)])
        if mp.det(principal) <= 0:
            raise M243ReferenceFailure("bridge fixture is not strict SPD")
    if mp.det(matrix) <= 0:
        raise M243ReferenceFailure("bridge fixture determinant is nonpositive")

    sigma = tuple(mp.sqrt(covariance[index][index]) for index in range(width))
    alpha = tuple(mean[index] / sigma[index] for index in range(width))
    unary_mean = tuple(
        relu_mean(mean[index], covariance[index][index]) for index in range(width)
    )
    second = tuple(
        relu_second(mean[index], covariance[index][index]) for index in range(width)
    )
    variance = tuple(second[index] - unary_mean[index] ** 2 for index in range(width))
    if any(value <= 0 for value in variance):
        raise M243ReferenceFailure("rectified marginal variance is nonpositive")
    relu_scale = tuple(mp.sqrt(value) for value in variance)
    post = [[mp.zero for _ in range(width)] for _ in range(width)]
    bridge = [[mp.zero for _ in range(width)] for _ in range(width)]
    for index in range(width):
        post[index][index] = variance[index]
        bridge[index][index] = mp.one
    for left in range(width):
        for right in range(left + 1, width):
            pair = positive_part_raw(
                mean[left], covariance[left][left],
                mean[right], covariance[right][right],
                covariance[left][right], audit,
                f"{label}:bridge:{left}:{right}",
            )
            centered = pair["raw"] - unary_mean[left] * unary_mean[right]
            post[left][right] = post[right][left] = centered
            normalized = centered / (relu_scale[left] * relu_scale[right])
            if abs(normalized) > 1 + mp.mpf("2e-10"):
                raise M243ReferenceFailure("invalid normalized ReLU bridge")
            bridge[left][right] = bridge[right][left] = normalized

    h1 = tuple(sigma[index] * normal_cdf(alpha[index]) for index in range(width))
    h2 = tuple(sigma[index] * normal_pdf(alpha[index]) for index in range(width))
    h3 = tuple(
        -sigma[index] * alpha[index] * normal_pdf(alpha[index])
        for index in range(width)
    )
    if any(value == 0 for value in h1):
        raise M243ReferenceFailure("zero degree-one bridge coefficient")
    gamma2 = tuple(
        h2[index] * relu_scale[index] / h1[index] ** 2
        for index in range(width)
    )
    gamma3 = tuple(
        h3[index] * relu_scale[index] ** 2 / h1[index] ** 3
        for index in range(width)
    )
    return MPBridgeState(
        mean,
        covariance,
        sigma,
        alpha,
        unary_mean,
        variance,
        relu_scale,
        tuple(tuple(row) for row in post),
        tuple(tuple(row) for row in bridge),
        gamma2,
        gamma3,
    )


def tree_211(state: MPBridgeState, repeated: int, left: int, right: int):
    labels = (repeated, repeated, left, right)
    scale_product = mp.fprod(state.relu_scale[label] for label in labels)
    stars = []
    for centre in range(4):
        root = labels[centre]
        value = state.gamma3[root]
        for position in range(4):
            if position != centre:
                value *= state.bridge[root][labels[position]]
        stars.append(value)
    paths = []
    for permutation in itertools.permutations(range(4)):
        a, b, c, d = (labels[position] for position in permutation)
        paths.append(
            state.gamma2[b]
            * state.gamma2[c]
            * state.bridge[a][b]
            * state.bridge[b][c]
            * state.bridge[c][d]
        )
    return scale_product * (mp.fsum(stars) + mp.fsum(paths) / 2)


class ReferenceEvent:
    """One independent strict-[2,1,1] event at one mpmath precision."""

    def __init__(
        self,
        mean_values,
        covariance_values,
        audit: QuadAudit,
        label: str,
    ):
        self.audit = audit
        self.label = label
        self.state = build_bridge_state(mean_values, covariance_values, audit, label)
        if len(self.state.mean) != 3:
            raise M243ReferenceFailure("ReferenceEvent requires an ordered three-label slice")
        self.i, self.j, self.k = 0, 1, 2
        self._pair_cache = {}
        self._R = None
        self._beta_direct = None
        self._beta_analytic = None
        self._jet = None
        self.tree = tree_211(self.state, self.i, self.j, self.k)
        post = self.state.post_covariance
        self.wick_vii_vjk = post[self.i][self.i] * post[self.j][self.k]
        self.wick_cross = 2 * post[self.i][self.j] * post[self.i][self.k]
        self.constants = self.wick_vii_vjk + self.wick_cross + self.tree

    @property
    def alpha_i(self):
        return self.state.alpha[self.i]

    @property
    def panels(self):
        return outer_panel_points(self.alpha_i)

    def repeated_factor(self, g):
        output = max(mp.zero, self.state.mean[self.i] + self.state.sigma[self.i] * g)
        return (output - self.state.relu_mean[self.i]) ** 2

    def conditional_centered_pair(self, g):
        key = mp.nstr(g, n=mp.dps + 10, strip_zeros=False)
        cached = self._pair_cache.get(key)
        if cached is not None:
            return cached
        state = self.state
        i, j, k = self.i, self.j, self.k
        variance_i = state.covariance[i][i]
        spoke_j = state.covariance[j][i]
        spoke_k = state.covariance[k][i]
        mean_j = state.mean[j] + spoke_j * g / state.sigma[i]
        mean_k = state.mean[k] + spoke_k * g / state.sigma[i]
        variance_j = state.covariance[j][j] - spoke_j**2 / variance_i
        variance_k = state.covariance[k][k] - spoke_k**2 / variance_i
        covariance_jk = state.covariance[j][k] - spoke_j * spoke_k / variance_i
        pair = positive_part_raw(
            mean_j,
            variance_j,
            mean_k,
            variance_k,
            covariance_jk,
            self.audit,
            f"{self.label}:conditional:{key}",
        )
        conditional_j = relu_mean(mean_j, variance_j)
        conditional_k = relu_mean(mean_k, variance_k)
        centered = (
            pair["raw"]
            - state.relu_mean[j] * conditional_k
            - state.relu_mean[k] * conditional_j
            + state.relu_mean[j] * state.relu_mean[k]
        )
        self._pair_cache[key] = centered
        return centered

    def _outer(self, function, suffix: str):
        return self.audit.integrate(
            lambda g: function(g) * normal_pdf(g),
            self.panels,
            f"outer:{self.label}:{suffix}",
        )[0]

    def repeated_R(self):
        if self._R is None:
            values = []
            for degree in range(5):
                values.append(
                    self._outer(
                        lambda g, q=degree: self.repeated_factor(g) * hermites(g)[q],
                        f"R{degree}",
                    )
                )
            self._R = tuple(values)
        return self._R

    def beta_direct(self):
        if self._beta_direct is None:
            values = []
            for degree in range(5):
                numerator = self._outer(
                    lambda g, q=degree: self.conditional_centered_pair(g) * hermites(g)[q],
                    f"beta_direct_{degree}",
                )
                values.append(numerator / math.factorial(degree))
            self._beta_direct = tuple(values)
        return self._beta_direct

    def beta_analytic(self):
        if self._beta_analytic is not None:
            return self._beta_analytic
        state = self.state
        i, j, k = self.i, self.j, self.k
        sj, sk = state.sigma[j], state.sigma[k]
        a, b = state.alpha[j], state.alpha[k]
        rho = state.covariance[j][k] / (sj * sk)
        p = state.covariance[i][j] / (state.sigma[i] * sj)
        q = state.covariance[i][k] / (state.sigma[i] * sk)
        delta = (1 - rho) * (1 + rho)
        P = phi2(a, b, rho, self.audit, f"{self.label}:analytic_beta")
        A = normal_pdf(a) * normal_cdf((b - rho * a) / mp.sqrt(delta))
        B = normal_pdf(b) * normal_cdf((a - rho * b) / mp.sqrt(delta))
        D = mp.exp(-(a * a - 2 * rho * a * b + b * b) / (2 * delta)) / (
            2 * mp.pi * mp.sqrt(delta)
        )
        la = a * normal_cdf(a) + normal_pdf(a)
        lb = b * normal_cdf(b) + normal_pdf(b)
        phi_a, phi_b = normal_pdf(a), normal_pdf(b)
        Phi_a, Phi_b = normal_cdf(a), normal_cdf(b)

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
            (a**2 * (b - rho * a) - b + 3 * rho * a) * A
            + (delta * a**2 + 2 * rho**2 - 1) * D
            + (1 - a**2) * lb * phi_a
        )
        Haaab = -a * A - rho * D
        Haabb = D
        Habbb = -b * B - rho * D
        Hbbbb = (
            (b**2 * (a - rho * b) - a + 3 * rho * b) * B
            + (delta * b**2 + 2 * rho**2 - 1) * D
            + (1 - b**2) * la * phi_b
        )
        derivatives = (
            H,
            p * Ha + q * Hb,
            p**2 * Haa + 2 * p * q * Hab + q**2 * Hbb,
            p**3 * Haaa + 3 * p**2 * q * Haab + 3 * p * q**2 * Habb + q**3 * Hbbb,
            p**4 * Haaaa
            + 4 * p**3 * q * Haaab
            + 6 * p**2 * q**2 * Haabb
            + 4 * p * q**3 * Habbb
            + q**4 * Hbbbb,
        )
        self._beta_analytic = tuple(
            sj * sk * derivatives[degree] / math.factorial(degree)
            for degree in range(5)
        )
        self._jet = {"P": P, "A": A, "B": B, "D": D, "a": a, "b": b, "rho": rho, "p": p, "q": q}
        return self._beta_analytic

    def raw(self, g):
        return self.repeated_factor(g) * self.conditional_centered_pair(g) - self.constants

    def raw_antithetic(self, g):
        return (self.raw(g) + self.raw(-g)) / 2

    def folded(self, g, degree: int):
        if degree not in (2, 4):
            raise M243ReferenceFailure("ideal fold degree must be two or four")
        beta = self.beta_analytic()
        repeated = self.repeated_R()
        count = degree + 1
        plus_h = hermites(g)
        minus_h = hermites(-g)
        plus_poly = mp.fsum(beta[index] * plus_h[index] for index in range(count))
        minus_poly = mp.fsum(beta[index] * minus_h[index] for index in range(count))
        residual = (
            self.repeated_factor(g) * (self.conditional_centered_pair(g) - plus_poly)
            + self.repeated_factor(-g) * (self.conditional_centered_pair(-g) - minus_poly)
        ) / 2
        addback = mp.fsum(beta[index] * repeated[index] for index in range(count))
        return residual + addback - self.constants

    def evaluate(self, tail_values: Sequence[float]):
        repeated = self.repeated_R()
        beta_direct = self.beta_direct()
        beta_analytic = self.beta_analytic()
        fourth_central = self._outer(
            lambda g: self.repeated_factor(g) * self.conditional_centered_pair(g),
            "central_fourth",
        )
        delta = fourth_central - self.constants
        means = {
            "raw_antithetic": self._outer(self.raw_antithetic, "mean_raw_antithetic"),
            "q2": self._outer(lambda g: self.folded(g, 2), "mean_q2"),
            "q4": self._outer(lambda g: self.folded(g, 4), "mean_q4"),
        }
        tails = []
        for value in tail_values:
            g = binary_mpf(value)
            tails.append(
                {
                    "g_hex": float(value).hex(),
                    "g": g,
                    "b": self.conditional_centered_pair(g),
                    "r": self.repeated_factor(g),
                    "raw": self.raw(g),
                    "q2": self.folded(g, 2),
                    "q4": self.folded(g, 4),
                }
            )
        return {
            "R_direct": repeated,
            "beta_direct": beta_direct,
            "beta_analytic": beta_analytic,
            "analytic_jet": self._jet,
            "central_fourth": fourth_central,
            "delta": delta,
            "means": means,
            "tree": self.tree,
            "wick_vii_vjk": self.wick_vii_vjk,
            "wick_cross": self.wick_cross,
            "tree_star_count": 4,
            "tree_positional_path_count": 24,
            "tails": tails,
        }


__all__ = [
    "M243ReferenceFailure",
    "QuadAudit",
    "ReferenceEvent",
    "binary_mpf",
    "normal_pdf",
    "outer_panel_points",
]
