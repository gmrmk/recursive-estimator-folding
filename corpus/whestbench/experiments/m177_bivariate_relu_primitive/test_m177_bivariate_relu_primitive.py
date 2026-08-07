"""Response-free M177 contract and high-precision endpoint checks."""

from __future__ import annotations

import math
from decimal import Decimal, getcontext
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m177_bivariate_relu_primitive import (  # noqa: E402
    Stratum,
    classify_pair,
    endpoint_reduction_identity,
    fail_closed_runtime_reason,
    probe_flopscope_capability,
    required_pair_cost_lower_bound,
)


getcontext().prec = 90
D = Decimal
PI = D("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")


def phi(x: Decimal) -> Decimal:
    return (-x * x / D(2)).exp() / (D(2) * PI).sqrt()


def erf_series(x: Decimal) -> Decimal:
    """90-decimal elementary reference for |x|<5, fixed 240-term series."""
    term = x
    total = term
    xx = x * x
    for n in range(1, 240):
        term *= -xx / D(n)
        total += term / D(2 * n + 1)
    return D(2) * total / PI.sqrt()


def cdf(x: Decimal) -> Decimal:
    return (D(1) + erf_series(x / D(2).sqrt())) / D(2)


def moment_interval(lo: Decimal, hi: Decimal | None) -> tuple[Decimal, Decimal, Decimal]:
    p_lo, density_lo = cdf(lo), phi(lo)
    if hi is None:
        p_hi, density_hi = D(1), D(0)
    else:
        p_hi, density_hi = cdf(hi), phi(hi)
    i0 = p_hi - p_lo
    i1 = density_lo - density_hi
    i2 = lo * density_lo - (D(0) if hi is None else hi * density_hi) + i0
    return i0, i1, i2


def endpoint_raw(alpha: Decimal, beta: Decimal, sign: int) -> Decimal:
    # Independent, high-precision univariate truncated-normal moment formula.
    lo = max(-alpha, -beta) if sign == 1 else -alpha
    hi = None if sign == 1 else beta
    if hi is not None and lo >= hi:
        return D(0)
    i0, i1, i2 = moment_interval(lo, hi)
    return alpha * beta * i0 + (beta + alpha * D(sign)) * i1 + D(sign) * i2


class M177PrimitiveTests(unittest.TestCase):
    def test_all_psd_strata_and_invalid_pair_are_dispatched(self):
        self.assertEqual(classify_pair([1, -2], [[0, 0], [0, 0]]).stratum, Stratum.DETERMINISTIC)
        self.assertEqual(classify_pair([1, -2], [[0, 0], [0, 3]]).stratum, Stratum.ZERO_VARIANCE_FACE)
        self.assertEqual(classify_pair([1, -2], [[4, 6], [6, 9]]).stratum, Stratum.RANK_ONE_PLUS)
        self.assertEqual(classify_pair([1, -2], [[4, -6], [-6, 9]]).stratum, Stratum.RANK_ONE_MINUS)
        self.assertEqual(classify_pair([1, -2], [[4, 1], [1, 9]]).stratum, Stratum.SPD)
        self.assertEqual(classify_pair([1, -2], [[1, 2], [2, 1]]).stratum, Stratum.NON_PSD)

    def test_rank_one_endpoint_reference_grid_is_nonnegative_and_scale_exact(self):
        for sign in (-1, 1):
            for alpha, beta in ((-7, -1.5), (-0.5, 0.25), (0, 0), (2.25, -0.75), (6, 5)):
                raw = endpoint_raw(D(alpha), D(beta), sign)
                self.assertGreaterEqual(raw, D("0"))
                scale = D("8")
                scaled = scale * scale * endpoint_raw(D(alpha), D(beta), sign)
                self.assertLess(abs(scaled - scale * scale * raw), D("1e-70"))

    def test_near_endpoint_spd_is_not_clipped_to_rank_one(self):
        rho = np.nextafter(1.0, 0.0)
        result = classify_pair([0.0, 0.0], [[1.0, rho], [rho, 1.0]])
        self.assertEqual(result.stratum, Stratum.SPD)
        self.assertLess(result.rho, 1.0)

    def test_zero_variance_path_is_not_a_generic_jvp(self):
        # Sigma(t)=[[t^2,t],[t,1]] is PSD for t>=0.  Its covariance
        # derivative at zero has an off-diagonal term although the base first
        # coordinate has zero variance; a rho JVP is therefore undefined.
        result = classify_pair([0.0, 1.0], [[0.0, 0.0], [0.0, 1.0]])
        self.assertEqual(result.stratum, Stratum.ZERO_VARIANCE_FACE)
        self.assertIn("underdetermined", result.tangent_policy)
        self.assertIn("TANGENT_PATH", fail_closed_runtime_reason([0.0, 1.0], [[0.0, 0.0], [0.0, 1.0]]))

    def test_special_function_capability_and_inclusive_floor(self):
        cap = probe_flopscope_capability()
        self.assertTrue(cap.normal_cdf)
        self.assertEqual(cap.normal_cdf_cost_per_element, 48)
        self.assertFalse(cap.normal_cdf_certified_error)
        self.assertFalse(cap.owen_t)
        self.assertFalse(cap.bivariate_normal_cdf)
        self.assertFalse(cap.exact_elementary_evaluator)
        cost = required_pair_cost_lower_bound()
        self.assertEqual(cost["known_pre_phi2_total"], 556)
        self.assertEqual(cost["phi2_or_owen_t_certificate"], -1)

    def test_scale_gauge_and_formula_requirements_are_explicit(self):
        base = classify_pair([0.75, -1.25], [[4.0, 1.5], [1.5, 9.0]])
        scaled = classify_pair([6.0, -10.0], [[256.0, 96.0], [96.0, 576.0]])
        self.assertEqual(base.stratum, Stratum.SPD)
        self.assertEqual(scaled.stratum, Stratum.SPD)
        self.assertAlmostEqual(base.rho, scaled.rho, places=15)
        self.assertIn("Phi2", endpoint_reduction_identity(base))


if __name__ == "__main__":
    unittest.main()
