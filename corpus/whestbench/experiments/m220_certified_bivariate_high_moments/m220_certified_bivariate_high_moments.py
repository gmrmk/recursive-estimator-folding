"""M220: exact bivariate ReLU fourth connected moments on an SPD pair.

This is a narrow generated-only algebra candidate.  It takes one bivariate
Gaussian pair and returns raw (3,1)/(2,2) moments plus their connected fourth
cumulants.  It is not a Source211 provider, collision proposal, tree compiler,
or variance claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
M178_DIR = HERE.parent / "m178_certified_phi2_owent"
if str(M178_DIR) not in sys.path:
    sys.path.insert(0, str(M178_DIR))

import m178_certified_phi2_owent as m178  # noqa: E402


MUTATION = "M220"
M178_CALLS_PER_SPD_EVENT = 1
M178_WORST_INCLUSIVE = 4048
EXTRA_STATIC_ALLOWANCE = 4144
INCLUSIVE_SCALAR_FLOP_CEILING = M178_WORST_INCLUSIVE + EXTRA_STATIC_ALLOWANCE
# This is a numerical-enclosure gate, not a variance-efficacy gate.  Connected
# values can cancel close to zero, so it is normalized by 1+|value|.
RADIUS_RELATIVE_GATE = 3.0e-3
_EPS = 2.0 ** -52


@dataclass(frozen=True)
class M220Result:
    refused: bool
    reason: str
    raw_m31: float
    raw_m22: float
    kappa31: float
    kappa22: float
    w_raw_m31: float
    w_raw_m22: float
    w_kappa31: float
    w_kappa22: float
    m178_calls: int
    chart: str

    def width_gate_passes(self) -> bool:
        if self.refused:
            return False
        return all(
            math.isfinite(width) and width <= RADIUS_RELATIVE_GATE * (1.0 + abs(value))
            for value, width in (
                (self.raw_m31, self.w_raw_m31),
                (self.raw_m22, self.w_raw_m22),
                (self.kappa31, self.w_kappa31),
                (self.kappa22, self.w_kappa22),
            )
        )


def _refuse(reason: str) -> M220Result:
    nan = float("nan")
    return M220Result(True, reason, nan, nan, nan, nan, nan, nan, nan, nan, 0, "REFUSED")


def _univariate_raw(mu: float, sigma: float, backend: m178.Backend) -> tuple[tuple[float, float, float, float], float]:
    """Raw moments E[(mu+sigma Z)_+^p], p=0..3, and a conservative width."""
    alpha = mu / sigma
    phi_cdf, w_cdf = m178._Phi_cert(backend, alpha)
    phi_pdf, rel_pdf = m178._phi_cert(backend, alpha)
    cdf, pdf = float(phi_cdf), float(phi_pdf)
    p0 = 1.0
    p1 = sigma * (alpha * cdf + pdf)
    p2 = sigma * sigma * ((alpha * alpha + 1.0) * cdf + alpha * pdf)
    p3 = sigma ** 3 * ((alpha ** 3 + 3.0 * alpha) * cdf + (alpha * alpha + 2.0) * pdf)
    # The inherited unary certificates have absolute CDF and relative PDF
    # widths.  The multiplier intentionally overbounds the small arithmetic
    # and standardization roundoff; target-path containment remains a gate.
    scale = max(1.0, abs(alpha), abs(sigma))
    width = 64.0 * (w_cdf + abs(pdf) * rel_pdf + _EPS) * scale ** 3
    return (p0, p1, p2, p3), width


def _central31(u10: float, u20: float, u30: float, v01: float, m11: float, m21: float, m31: float) -> float:
    return (
        m31 - v01 * u30 - 3.0 * u10 * m21 + 3.0 * u10 * v01 * u20
        + 3.0 * u10 * u10 * m11 - 3.0 * u10 * u10 * v01 * u10
        - u10 ** 3 * v01 + u10 ** 3 * v01
    )


def _central22(u10: float, u20: float, v01: float, v02: float, m11: float, m12: float, m21: float, m22: float) -> float:
    return (
        m22 - 2.0 * v01 * m21 + v01 * v01 * u20
        - 2.0 * u10 * m12 + 4.0 * u10 * v01 * m11 - 2.0 * u10 * v01 * v01 * u10
        + u10 * u10 * v02 - 2.0 * u10 * u10 * v01 * v01 + u10 * u10 * v01 * v01
    )


def _radius(value: float, seed_width: float, scale: float, degree: int = 4) -> float:
    """Conservative formula-level radius, not a substitute for promotion tests."""
    radius = 128.0 * seed_width * max(1.0, scale) ** degree + 4096.0 * _EPS * (1.0 + abs(value))
    return radius if math.isfinite(radius) else float("nan")


def _degenerate(mu_x: float, mu_y: float, vx: float, vy: float, cov_xy: float, backend: m178.Backend) -> M220Result:
    if cov_xy != 0.0:
        return _refuse("ZERO_VARIANCE_WITH_NONZERO_COVARIANCE")
    if vx == 0.0 and vy == 0.0:
        ux, uy = max(mu_x, 0.0), max(mu_y, 0.0)
        return M220Result(False, "", ux ** 3 * uy, ux * ux * uy * uy, 0.0, 0.0,
                          0.0, 0.0, 0.0, 0.0, 0, "DEGENERATE_BOTH_CONSTANT")
    if vx == 0.0:
        ux = max(mu_x, 0.0)
        (one, m01, m02, _), width = _univariate_raw(mu_y, math.sqrt(vy), backend)
        return M220Result(False, "", ux ** 3 * m01, ux * ux * m02, 0.0, 0.0,
                          _radius(ux ** 3 * m01, width, max(1.0, abs(ux))),
                          _radius(ux * ux * m02, width, max(1.0, abs(ux))),
                          0.0, 0.0, 0, "DEGENERATE_X_CONSTANT")
    uy = max(mu_y, 0.0)
    (one, m10, m20, m30), width = _univariate_raw(mu_x, math.sqrt(vx), backend)
    return M220Result(False, "", m30 * uy, m20 * uy * uy, 0.0, 0.0,
                      _radius(m30 * uy, width, max(1.0, abs(uy))),
                      _radius(m20 * uy * uy, width, max(1.0, abs(uy))),
                      0.0, 0.0, 0, "DEGENERATE_Y_CONSTANT")


def evaluate(mu_x: float, mu_y: float, vx: float, vy: float, cov_xy: float, *, backend: m178.Backend | None = None) -> M220Result:
    """Return exact-formula M31/M22 and fourth connected owners on one pair.

    The SPD path makes exactly one M178 call.  Rank-one / non-SPD charts fail
    closed.  Exact zero-variance endpoints have their deterministic limits.
    """
    values = (mu_x, mu_y, vx, vy, cov_xy)
    if not all(math.isfinite(value) for value in values):
        return _refuse("NONFINITE_INPUT")
    if vx < 0.0 or vy < 0.0:
        return _refuse("NEGATIVE_VARIANCE")
    bk = backend if backend is not None else m178.Backend()
    if vx == 0.0 or vy == 0.0:
        return _degenerate(mu_x, mu_y, vx, vy, cov_xy, bk)

    sx, sy = math.sqrt(vx), math.sqrt(vy)
    rho = cov_xy / (sx * sy)
    if not math.isfinite(rho) or abs(rho) > m178.RHO_MAX:
        return _refuse("NON_SPD_OR_RANK_ONE_CHART")
    a, b = mu_x / sx, mu_y / sy
    jet = m178.evaluate(a, b, rho, backend=bk)
    if jet.refused:
        return _refuse("M178_" + jet.reason)
    try:
        (_, u10, u20, u30), wx = _univariate_raw(mu_x, sx, bk)
        (_, v01, v02, v03), wy = _univariate_raw(mu_y, sy, bk)
        s2 = (1.0 - rho) * (1.0 + rho)
        tx, ty = a - rho * b, b - rho * a
        bx0, by0 = jet.d_a / sx, jet.d_b / sy
        bx1 = (sy / sx) * (ty * jet.d_a + s2 * jet.d_rho)
        bx2 = (sy * sy / sx) * ((ty * ty + s2) * jet.d_a + ty * s2 * jet.d_rho)
        by1 = (sx / sy) * (tx * jet.d_b + s2 * jet.d_rho)
        # All J values below retain both orthant indicators.  Only u/v are
        # marginal ReLU moments for the eventual connected-cumulant algebra.
        j01 = mu_y * jet.value + cov_xy * bx0 + vy * by0
        j02 = mu_y * j01 + cov_xy * bx1 + vy * jet.value
        j10 = mu_x * jet.value + vx * bx0 + cov_xy * by0
        j20 = mu_x * j10 + vx * jet.value + cov_xy * by1
        m11 = mu_x * j01 + vx * bx1 + cov_xy * jet.value
        m21 = mu_x * m11 + vx * j01 + cov_xy * j10
        m31 = mu_x * m21 + 2.0 * vx * m11 + cov_xy * j20
        m12 = mu_x * j02 + vx * bx2 + 2.0 * cov_xy * j01
        m22 = mu_x * m12 + vx * j02 + 2.0 * cov_xy * m11
        central31 = _central31(u10, u20, u30, v01, m11, m21, m31)
        central22 = _central22(u10, u20, v01, v02, m11, m12, m21, m22)
        var_x, var_y = u20 - u10 * u10, v02 - v01 * v01
        covariance = m11 - u10 * v01
        kappa31 = central31 - 3.0 * var_x * covariance
        kappa22 = central22 - var_x * var_y - 2.0 * covariance * covariance
    except (OverflowError, ZeroDivisionError, ValueError):
        return _refuse("NUMERICAL_FAILURE")
    outputs = (m31, m22, kappa31, kappa22)
    if not all(math.isfinite(value) for value in outputs):
        return _refuse("NONFINITE_INTERMEDIATE")
    seed = jet.w_value + jet.w_da + jet.w_db + jet.w_drho + wx + wy
    scale = max(1.0, abs(mu_x), abs(mu_y), sx, sy, abs(a), abs(b))
    widths = tuple(_radius(value, seed, scale) for value in outputs)
    if not all(math.isfinite(width) for width in widths):
        return _refuse("NONFINITE_ENCLOSURE")
    return M220Result(False, "", m31, m22, kappa31, kappa22, *widths, 1, "SPD_BOUNDARY_RECURRENCE")
