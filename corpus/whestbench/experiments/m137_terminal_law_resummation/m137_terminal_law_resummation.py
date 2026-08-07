"""M137: frozen terminal-law closures from exact first four moments.

This is a generated-only research falsifier.  It asks an intentionally
generous question: if a fixed deep ReLU network were given *exact* final
preactivation moments through order four, could a non-Gaussian univariate
closure improve E[max(Z, 0)] enough to matter?

Nothing here reads a contest dataset, scorer, target, package, or leaderboard.
The only truth is an independently sampled mean from iid-He Gaussian ReLU
networks made in this file.

Rules are frozen before the run:
  * Edgeworth is used only as the ordinary Gram--Charlier baseline.
  * Quartic maximum entropy is used only when its normalizable exponential
    density solves the moment constraints.
  * A two-Gaussian mixture is used only when its equal-within-component-
    variance moment equations have a feasible exact solution.
  * The moment-envelope midpoint is the minimax point estimate for the stated
    certified interval; it is not tuned to generated outcomes.

The module also records why a polynomial-cumulant saddlepoint is not a
probability-law closure: by Marcinkiewicz's theorem an everywhere-defined
characteristic function cannot have a finite non-quadratic cumulant polynomial.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import erf
from typing import Iterable

import numpy as np

try:  # Used only by generated-only fitting/bounds, never a target interface.
    from scipy.optimize import least_squares
except ImportError:  # pragma: no cover - target interface remains NumPy-only.
    least_squares = None


Array = np.ndarray
SQRT_2 = float(np.sqrt(2.0))
SQRT_2PI = float(np.sqrt(2.0 * np.pi))


def normal_cdf(x: Array | float) -> Array:
    x = np.asarray(x, dtype=np.float64)
    return np.vectorize(lambda z: 0.5 * (1.0 + erf(float(z) / SQRT_2)), otypes=[float])(x)


def normal_pdf(x: Array | float) -> Array:
    x = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * x * x) / SQRT_2PI


@dataclass(frozen=True)
class Moments4:
    """Raw moments m_1,...,m_4 plus their standardized counterparts."""

    mean: float
    variance: float
    kappa3: float
    kappa4: float

    @property
    def scale(self) -> float:
        return float(np.sqrt(max(self.variance, 1e-300)))

    @property
    def skewness(self) -> float:
        return float(self.kappa3 / self.scale**3)

    @property
    def excess_kurtosis(self) -> float:
        return float(self.kappa4 / self.variance**2)

    @property
    def raw2(self) -> float:
        return float(self.variance + self.mean**2)

    @property
    def raw3(self) -> float:
        return float(self.kappa3 + 3.0 * self.mean * self.variance + self.mean**3)

    @property
    def raw4(self) -> float:
        central4 = self.kappa4 + 3.0 * self.variance**2
        return float(central4 + 4.0 * self.mean * self.kappa3 + 6.0 * self.mean**2 * self.variance + self.mean**4)


def moments4_from_raw(raw: Array | Iterable[float]) -> Moments4:
    """Convert raw E[Z^r], r=1..4, to cumulants through order four."""
    m1, m2, m3, m4 = (float(x) for x in raw)
    # A finite generated network can contain an exactly dead final coordinate.
    # The floor only regularizes division in standardized diagnostics; all of
    # its closures then reduce continuously to max(mean, 0).
    variance = max(m2 - m1 * m1, 1e-30)
    kappa3 = m3 - 3.0 * m1 * m2 + 2.0 * m1**3
    central4 = m4 - 4.0 * m1 * m3 + 6.0 * m1 * m1 * m2 - 3.0 * m1**4
    kappa4 = central4 - 3.0 * variance * variance
    return Moments4(m1, variance, kappa3, kappa4)


def gaussian_relu_mean(m: Moments4) -> float:
    a = m.mean / m.scale
    return float(m.mean * normal_cdf(a) + m.scale * normal_pdf(a))


def edgeworth_relu_mean(m: Moments4) -> float:
    """Order-(k3,k4,k3^2) Gram--Charlier/Edgeworth baseline.

    This is deliberately the familiar baseline, not a newly fitted closure.
    It can be negative-density and is therefore not treated as a probability
    law or a feasibility selector.
    """
    s = m.scale
    a = m.mean / s
    g1, g2 = m.skewness, m.excess_kurtosis
    result = gaussian_relu_mean(m)
    result += s * normal_pdf(a) * (-g1 * a / 6.0)
    result += s * normal_pdf(a) * (g2 * (a * a - 1.0) / 24.0)
    result += s * normal_pdf(a) * (g1 * g1 * (a**4 - 6.0 * a * a + 3.0) / 72.0)
    return float(max(result, 0.0))


def edgeworth_polynomial_minimum(skew: float, excess: float) -> float:
    """Global minimum of the order-4 Edgeworth density multiplier.

    The polynomial is 1 + g1 He3/6 + g2 He4/24 + g1^2 He6/72.
    If it is negative, the Edgeworth expression is not a density.  Checking
    stationary points is exact up to root-finding precision, unlike a sampled
    positivity grid.
    """
    # Ascending powers: He3=x^3-3x; He4=x^4-6x^2+3;
    # He6=x^6-15x^4+45x^2-15.
    coeff = np.zeros(7, dtype=np.float64)
    coeff[0] = 1.0 + excess * 3.0 / 24.0 - skew * skew * 15.0 / 72.0
    coeff[1] = -skew / 2.0
    coeff[2] = -excess / 4.0 + skew * skew * 45.0 / 72.0
    coeff[3] = skew / 6.0
    coeff[4] = excess / 24.0 - skew * skew * 15.0 / 72.0
    coeff[6] = skew * skew / 72.0
    # Remove trailing zeroes before differentiating; a nonconstant odd leading
    # term means -infinity in one direction and is immediately invalid.
    nz = np.flatnonzero(np.abs(coeff) > 1e-14)
    if nz.size == 0:
        return 1.0
    degree = int(nz[-1])
    if degree % 2:
        return float("-inf")
    if coeff[degree] < 0.0:
        return float("-inf")
    deriv = np.arange(1, degree + 1, dtype=np.float64) * coeff[1 : degree + 1]
    roots = np.roots(deriv[::-1]) if deriv.size > 1 else np.empty(0, dtype=np.complex128)
    candidates = [float(r.real) for r in roots if abs(r.imag) < 1e-9]
    if degree == 0:
        candidates.append(0.0)
    values = [float(np.polynomial.polynomial.polyval(x, coeff[: degree + 1])) for x in candidates]
    # An even degree positive-leading polynomial with no real derivative root
    # can only be constant (already handled), but keep a defensive sample.
    if not values:
        values = [float(np.polynomial.polynomial.polyval(0.0, coeff[: degree + 1]))]
    return float(min(values))


def certified_relu_interval(m: Moments4) -> tuple[float, float]:
    """A rigorous fourth-moment interval for E[Z_+].

    E[Z_+] = (E[Z]+E|Z|)/2.  Interpolation of L^p norms gives
    E|Z| >= (E[Z^2])^(3/2) / sqrt(E[Z^4]), while Cauchy gives
    E|Z| <= sqrt(E[Z^2]).  These require no distributional ansatz.
    """
    m2 = max(m.raw2, 0.0)
    m4 = max(m.raw4, 1e-300)
    lower_abs = m2**1.5 / np.sqrt(m4)
    upper_abs = np.sqrt(m2)
    lower = max(0.0, 0.5 * (m.mean + lower_abs))
    upper = max(0.0, 0.5 * (m.mean + upper_abs))
    return float(lower), float(max(lower, upper))


def envelope_midpoint_relu_mean(m: Moments4) -> float:
    lo, hi = certified_relu_interval(m)
    return float(0.5 * (lo + hi))


def symmetric_gaussian_moment_counterexample() -> dict[str, float]:
    """Sharp symmetric subproblem witness at moments (0,1,0,3).

    The three-atom law P(X=0)=2/3 and P(X=+-sqrt(3))=1/6 has exactly the
    first four Gaussian moments and E[X_+]=1/(2sqrt(3)).  Symmetric laws with
    the same second/fourth moments can approach E[X_+]=1/2 by putting an
    asymptotically vanishing mass at a very large radius.  Thus a four-moment
    closure cannot identify even this most favorable moment vector.
    """
    return {
        "normal_relu": float(1.0 / SQRT_2PI),
        "three_atom_relu": float(1.0 / (2.0 * np.sqrt(3.0))),
        "symmetric_lower_sharp": float(1.0 / (2.0 * np.sqrt(3.0))),
        "symmetric_upper_supremum": 0.5,
        "interval_width": float(0.5 - 1.0 / (2.0 * np.sqrt(3.0))),
    }


def _log_quadrature_weights(theta: Array, nodes: Array, weights: Array) -> tuple[Array, float]:
    """Weights for exp(theta_1 y+...+theta_4 y^4) dy via Hermite quadrature."""
    features = np.stack((nodes, nodes**2, nodes**3, nodes**4), axis=1)
    # hermgauss integrates exp(-y^2), so add y^2 back to represent dy.
    logs = np.log(weights) + features @ theta + nodes**2
    shift = float(np.max(logs))
    unnorm = np.exp(logs - shift)
    total = float(np.sum(unnorm))
    return unnorm / total, shift + float(np.log(total))


def maxent_quartic_relu_mean(m: Moments4, nodes_count: int = 96) -> tuple[float, bool, dict[str, float]]:
    """Quartic maximum-entropy closure, or Gaussian fallback if infeasible.

    The invariant selector is feasibility of a normalizable exponential family:
    theta_4 < 0, moment residual <= 1e-7, and a positive covariance Hessian.
    A positive fitted theta_4 is *not* silently clipped: it means the proposed
    density is nonnormalizable on the real line and the candidate is rejected.
    """
    baseline = gaussian_relu_mean(m)
    if least_squares is None:
        return baseline, False, {"reason": -1.0}
    g1, g2 = m.skewness, m.excess_kurtosis
    # A quartic maximum-entropy law with theta4<0 cannot realize the
    # near-Gaussian positive-kurtosis direction continuously at zero.  Let the
    # optimizer establish feasibility instead of hard-coding that observation.
    nodes, quad_weights = np.polynomial.hermite.hermgauss(nodes_count)
    features = np.stack((nodes, nodes**2, nodes**3, nodes**4), axis=1)
    target = np.array([0.0, 1.0, g1, g2 + 3.0], dtype=np.float64)

    def residual(theta: Array) -> Array:
        prob, _ = _log_quadrature_weights(theta, nodes, quad_weights)
        got = prob @ features
        return got - target

    # Multiple fixed starts are a numerical safeguard, not model selection:
    # choose the feasible solution with the smallest moment residual, then
    # lexicographically smallest natural parameter vector.
    starts = (
        np.array([0.0, -0.5, 0.0, -1e-4]),
        np.array([0.0, -0.25, 0.0, -0.02]),
        np.array([0.0, 0.25, 0.0, -0.08]),
        np.array([0.05 * np.sign(g1), -0.5, -0.02 * np.sign(g1), -0.01]),
    )
    candidates: list[tuple[float, Array]] = []
    for start in starts:
        fit = least_squares(residual, start, method="trf", max_nfev=300, xtol=1e-12, ftol=1e-12, gtol=1e-12)
        theta = np.asarray(fit.x, dtype=np.float64)
        err = float(np.max(np.abs(residual(theta))))
        if np.all(np.isfinite(theta)):
            candidates.append((err, theta))
    if not candidates:
        return baseline, False, {"reason": -2.0}
    candidates.sort(key=lambda pair: (pair[0], *pair[1].tolist()))
    error, theta = candidates[0]
    # Strict normalizability: any cubic survives only under a negative quartic
    # leading term.  An arbitrarily small negative value is a numerical rather
    # than mathematical solution, so demand a tangible margin.
    feasible = bool(error <= 1e-7 and theta[3] < -1e-8)
    if not feasible:
        return baseline, False, {
            "residual": error,
            "theta1": float(theta[0]), "theta2": float(theta[1]),
            "theta3": float(theta[2]), "theta4": float(theta[3]),
        }
    prob, _ = _log_quadrature_weights(theta, nodes, quad_weights)
    value = float(prob @ np.maximum(m.mean + m.scale * nodes, 0.0))
    return value, True, {
        "residual": error,
        "theta1": float(theta[0]), "theta2": float(theta[1]),
        "theta3": float(theta[2]), "theta4": float(theta[3]),
    }


def two_gaussian_mixture_relu_mean(m: Moments4) -> tuple[float, bool, dict[str, float]]:
    """Equal-within-component-variance two-Gaussian moment closure.

    With p the positive-mean component mass and r the fraction of variance in
    component separation, the standardized third/fourth cumulants are

      g1 = r^(3/2) (1-2p)/sqrt(p(1-p)),
      g2 = r^2 (1-6p(1-p))/(p(1-p)).

    This is a frozen parametric selector.  Failure to solve these two equations
    exactly returns the Gaussian fallback; it is not patched with a fit.
    """
    baseline = gaussian_relu_mean(m)
    g1, g2 = m.skewness, m.excess_kurtosis
    if abs(g1) < 1e-12 and abs(g2) < 1e-12:
        return baseline, True, {"p": 0.5, "r": 0.0, "residual": 0.0}
    if abs(g1) < 1e-12 and -2.0 < g2 < -1e-12:
        # Symmetric separated mixture: kappa4=-2 r^2.
        p, r = 0.5, float(np.sqrt(-g2 / 2.0))
        within = np.sqrt(1.0 - r)
        a = np.sqrt(r)
        sd = m.scale * within
        def original_component_relu(loc: float) -> float:
            if sd <= 1e-12:
                return float(max(loc, 0.0))
            alpha = loc / sd
            return float(loc * normal_cdf(alpha) + sd * normal_pdf(alpha))
        value = 0.5 * original_component_relu(m.mean + m.scale * a)
        value += 0.5 * original_component_relu(m.mean - m.scale * a)
        return float(value), True, {"p": p, "r": r, "residual": 0.0}

    # The two branches above are closed form and must remain usable in the
    # dependency-minimal runtime.  SciPy is needed only for the generic
    # asymmetric two-parameter fit below.
    if least_squares is None:
        return baseline, False, {"reason": -1.0}

    # Enforce reflection equivariance.  g1>0 implies p<1/2 for the component
    # carrying the positive mean.  The g1=0/g2>0 branch has no such mixture.
    sign = 1.0 if g1 >= 0.0 else -1.0

    def sigmoid(x: float) -> float:
        return float(1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0))))

    def unpack(x: Array) -> tuple[float, float]:
        # p in (0,1/2), r in (0,1).  If g1<0 reflect at the end.
        p_small = 0.5 * sigmoid(float(x[0]))
        r = sigmoid(float(x[1]))
        return p_small, r

    def residual(x: Array) -> Array:
        p, r = unpack(x)
        q = p * (1.0 - p)
        pred1 = r**1.5 * (1.0 - 2.0 * p) / np.sqrt(q)
        pred2 = r**2 * (1.0 - 6.0 * q) / q
        return np.array([pred1 - abs(g1), pred2 - g2], dtype=np.float64)

    starts = [np.array([u, v], dtype=np.float64) for u in (-4.0, -1.0, 1.0, 4.0) for v in (-4.0, -1.0, 1.0, 4.0)]
    fits: list[tuple[float, float, float]] = []
    for start in starts:
        fit = least_squares(residual, start, method="trf", max_nfev=300, xtol=1e-12, ftol=1e-12, gtol=1e-12)
        p, r = unpack(np.asarray(fit.x))
        err = float(np.max(np.abs(residual(fit.x))))
        if err <= 1e-7 and 1e-9 < p < 0.5 - 1e-9 and 1e-9 < r < 1.0 - 1e-9:
            fits.append((err, p, r))
    if not fits:
        return baseline, False, {"reason": -2.0}
    fits.sort(key=lambda row: (row[0], row[1], row[2]))
    err, p, r = fits[0]
    if sign < 0.0:
        # Reflection swaps the sign of the separated component means.
        p = 1.0 - p
    # p is probability of a component with positive standardized mean a.
    a = np.sqrt(r * (1.0 - p) / p)
    b = -np.sqrt(r * p / (1.0 - p))
    within = np.sqrt(max(1.0 - r, 0.0))
    def component_relu(loc: float) -> float:
        if within <= 1e-12:
            return float(max(loc, 0.0))
        alpha = loc / within
        return float(loc * normal_cdf(alpha) + within * normal_pdf(alpha))
    y_plus = p * component_relu(a) + (1.0 - p) * component_relu(b)
    # Affine map back to the original Z law.  The threshold is not generally
    # zero in standardized units, so re-evaluate components in original units.
    loc_a = m.mean + m.scale * a
    loc_b = m.mean + m.scale * b
    sd = m.scale * within
    def original_component_relu(loc: float) -> float:
        if sd <= 1e-12:
            return float(max(loc, 0.0))
        alpha = loc / sd
        return float(loc * normal_cdf(alpha) + sd * normal_pdf(alpha))
    value = p * original_component_relu(loc_a) + (1.0 - p) * original_component_relu(loc_b)
    del y_plus  # Retained derivation variable, not an additional approximation.
    return float(value), True, {"p": float(p), "r": float(r), "residual": float(err)}


def saddlepoint_status(m: Moments4) -> str:
    """Classify the finite-cumulant saddlepoint proposal before any score run."""
    if abs(m.kappa3) <= 1e-14 and abs(m.kappa4) <= 1e-14:
        return "gaussian_only"
    return "invalid_as_global_law_marcinkiewicz"


def closures_from_moments(m: Moments4) -> tuple[dict[str, float], dict[str, object]]:
    """All frozen terminal closures and their feasibility diagnostics."""
    # A width-8 depth-32 generated network can have a genuinely dead final
    # coordinate.  Its four moments identify the point mass exactly; do not
    # manufacture a huge Holder bound from the numerical variance floor.
    if m.variance <= 1e-28 and abs(m.mean) <= 1e-14:
        values = {
            "gaussian": 0.0,
            "edgeworth_k4_second": 0.0,
            "maxent_quartic_or_gaussian": 0.0,
            "two_gaussian_mixture_or_gaussian": 0.0,
            "certified_interval_midpoint": 0.0,
        }
        diagnostics: dict[str, object] = {
            "edgeworth_density_minimum": 1.0,
            "maxent_feasible": True,
            "maxent": {"degenerate_point_mass": 1.0},
            "mixture_feasible": True,
            "mixture": {"degenerate_point_mass": 1.0},
            "saddlepoint_status": "degenerate_point_mass",
            "certified_interval": [0.0, 0.0],
        }
        return values, diagnostics
    maxent, maxent_ok, maxent_info = maxent_quartic_relu_mean(m)
    mixture, mixture_ok, mixture_info = two_gaussian_mixture_relu_mean(m)
    values = {
        "gaussian": gaussian_relu_mean(m),
        "edgeworth_k4_second": edgeworth_relu_mean(m),
        "maxent_quartic_or_gaussian": maxent,
        "two_gaussian_mixture_or_gaussian": mixture,
        "certified_interval_midpoint": envelope_midpoint_relu_mean(m),
    }
    lo, hi = certified_relu_interval(m)
    diagnostics: dict[str, object] = {
        "edgeworth_density_minimum": edgeworth_polynomial_minimum(m.skewness, m.excess_kurtosis),
        "maxent_feasible": maxent_ok,
        "maxent": maxent_info,
        "mixture_feasible": mixture_ok,
        "mixture": mixture_info,
        "saddlepoint_status": saddlepoint_status(m),
        "certified_interval": [lo, hi],
    }
    return values, diagnostics


def target_terminal_cost_interface(
    outputs: int = 256,
    quadrature_nodes: int = 96,
    maxent_newton_steps: int = 300,
) -> dict[str, object]:
    """Closure-only cost interface; intentionally excludes moment acquisition.

    Each rule consumes already supplied (mu, variance, k3, k4) for each output.
    These scalar counts are negligible beside any proposed tensor/source route,
    but they cannot be presented as a whole estimator because deriving those
    four fixed-network moments is exactly the unresolved upstream problem.
    """
    o, q, it = int(outputs), int(quadrature_nodes), int(maxent_newton_steps)
    return {
        "scope": "terminal_closure_only",
        "source_acquisition": "UNSOLVED_AND_EXCLUDED",
        "gaussian_scalar_ops_upper": 40 * o,
        "edgeworth_scalar_ops_upper": 90 * o,
        "two_gaussian_mixture_scalar_ops_upper": 16_000 * o,
        "quartic_maxent_scalar_ops_upper": 80 * q * it * o,
        "not_a_complete_estimator": True,
    }


def make_iid_he_network(width: int, depth: int, seed: int) -> list[Array]:
    rng = np.random.default_rng(seed)
    scale = np.sqrt(2.0 / width)
    return [rng.normal(0.0, scale, size=(width, width)).astype(np.float64) for _ in range(depth)]


def final_preactivations(x: Array, weights: list[Array]) -> Array:
    h = np.asarray(x, dtype=np.float64)
    for weight in weights[:-1]:
        h = np.maximum(h @ weight, 0.0)
    return h @ weights[-1]


def raw_moments_and_relu_reference(
    weights: list[Array], samples: int, chunk: int, seed: int, reference: bool
) -> tuple[Array, Array]:
    """Independent iid-Gaussian bank: raw moments or direct ReLU reference."""
    width = weights[0].shape[0]
    rng = np.random.default_rng(seed)
    raw = np.zeros((4, width), dtype=np.float64)
    relu_sum = np.zeros(width, dtype=np.float64)
    seen = 0
    while seen < samples:
        take = min(chunk, samples - seen)
        z = final_preactivations(rng.standard_normal((take, width)), weights)
        if reference:
            relu_sum += np.sum(np.maximum(z, 0.0), axis=0)
        else:
            z2 = z * z
            raw[0] += np.sum(z, axis=0)
            raw[1] += np.sum(z2, axis=0)
            raw[2] += np.sum(z2 * z, axis=0)
            raw[3] += np.sum(z2 * z2, axis=0)
        seen += take
    if reference:
        return raw, relu_sum / samples
    return raw / samples, relu_sum
