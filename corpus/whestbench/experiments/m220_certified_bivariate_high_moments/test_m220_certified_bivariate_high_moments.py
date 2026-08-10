from __future__ import annotations

import math
from pathlib import Path
import random
import sys
import unittest


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for sibling in ("m220_certified_bivariate_high_moments", "m122_nonzero_bridge_theory"):
    path = str(EXPERIMENTS / sibling)
    if path not in sys.path:
        sys.path.insert(0, path)

import m220_certified_bivariate_high_moments as m220
from m122_nonzero_bridge import pair_raw_moment_series, rectified_power_moment


def _central31(m10, m20, m30, m01, m11, m21, m31):
    return m31 - m01*m30 - 3*m10*m21 + 3*m10*m01*m20 + 3*m10*m10*m11 - 3*m10*m10*m01*m10


def _central22(m10, m20, m01, m02, m11, m12, m21, m22):
    return m22 - 2*m01*m21 + m01*m01*m20 - 2*m10*m12 + 4*m10*m01*m11 - 2*m10*m01*m01*m10 + m10*m10*m02 - m10*m10*m01*m01


def _reference(mu_x, mu_y, sx, sy, rho):
    raw = {(p, q): pair_raw_moment_series(mu_x/sx, sx, p, mu_y/sy, sy, q, rho, terms=96)
           for p, q in ((1, 1), (2, 1), (1, 2), (3, 1), (2, 2))}
    m10, m20, m30 = (sx**p * rectified_power_moment(mu_x/sx, p) for p in (1, 2, 3))
    m01, m02 = (sy**p * rectified_power_moment(mu_y/sy, p) for p in (1, 2))
    m11, m21, m12, m31, m22 = raw[1, 1], raw[2, 1], raw[1, 2], raw[3, 1], raw[2, 2]
    c31 = _central31(m10, m20, m30, m01, m11, m21, m31)
    c22 = _central22(m10, m20, m01, m02, m11, m12, m21, m22)
    vx, vy, cov = m20-m10*m10, m02-m01*m01, m11-m10*m01
    return m31, m22, c31 - 3*vx*cov, c22 - vx*vy - 2*cov*cov


class M220BoundaryRecurrenceTests(unittest.TestCase):
    def test_fixed_spd_cells_match_96_term_hermite_reference(self):
        cells = ((0.37, -0.41, 0.8, 1.3, -0.63), (-0.6, 0.9, 1.1, 0.7, 0.41),
                 (0.0, 0.5, 0.9, 1.4, 0.0), (1.2, -0.2, 0.6, 0.95, 0.72))
        for mu_x, mu_y, sx, sy, rho in cells:
            result = m220.evaluate(mu_x, mu_y, sx*sx, sy*sy, rho*sx*sy)
            self.assertFalse(result.refused, result.reason)
            self.assertEqual(result.m178_calls, 1)
            for got, expected, width in zip(
                (result.raw_m31, result.raw_m22, result.kappa31, result.kappa22),
                _reference(mu_x, mu_y, sx, sy, rho),
                (result.w_raw_m31, result.w_raw_m22, result.w_kappa31, result.w_kappa22),
            ):
                self.assertLessEqual(abs(got-expected), width)
                self.assertLessEqual(width, m220.RADIUS_RELATIVE_GATE*(1.0+abs(got)))

    def test_swap_and_positive_gauge(self):
        mu_x, mu_y, sx, sy, rho = 0.37, -0.41, 0.8, 1.3, -0.63
        first = m220.evaluate(mu_x, mu_y, sx*sx, sy*sy, rho*sx*sy)
        swapped = m220.evaluate(mu_y, mu_x, sy*sy, sx*sx, rho*sx*sy)
        self.assertAlmostEqual(first.raw_m22, swapped.raw_m22, places=10)
        self.assertAlmostEqual(first.kappa22, swapped.kappa22, places=9)
        gx, gy = 1.7, 0.6
        scaled = m220.evaluate(gx*mu_x, gy*mu_y, (gx*sx)**2, (gy*sy)**2, gx*gy*rho*sx*sy)
        self.assertAlmostEqual(scaled.raw_m31, gx**3*gy*first.raw_m31, places=9)
        self.assertAlmostEqual(scaled.raw_m22, gx**2*gy**2*first.raw_m22, places=9)
        self.assertAlmostEqual(scaled.kappa31, gx**3*gy*first.kappa31, places=8)
        self.assertAlmostEqual(scaled.kappa22, gx**2*gy**2*first.kappa22, places=8)

    def test_frozen_random_spd_reference_and_enclosure_gate(self):
        rng = random.Random(22020260809)
        for _ in range(24):
            mu_x, mu_y = (rng.uniform(-1.5, 1.5) for _ in range(2))
            sx, sy = (rng.uniform(0.4, 1.7) for _ in range(2))
            rho = rng.uniform(-0.74, 0.74)
            result = m220.evaluate(mu_x, mu_y, sx*sx, sy*sy, rho*sx*sy)
            self.assertFalse(result.refused, result.reason)
            self.assertTrue(result.width_gate_passes())
            for got, expected, width in zip(
                (result.raw_m31, result.raw_m22, result.kappa31, result.kappa22),
                _reference(mu_x, mu_y, sx, sy, rho),
                (result.w_raw_m31, result.w_raw_m22, result.w_kappa31, result.w_kappa22),
            ):
                self.assertLessEqual(abs(got-expected), width)

    def test_rank_one_refuses_and_exact_deterministic_limit_is_connected_zero(self):
        rank_one = m220.evaluate(0.2, -0.1, 1.0, 4.0, 2.0)
        self.assertTrue(rank_one.refused)
        fixed = m220.evaluate(0.3, -0.2, 0.0, 1.0, 0.0)
        self.assertFalse(fixed.refused)
        self.assertEqual(fixed.kappa31, 0.0)
        self.assertEqual(fixed.kappa22, 0.0)

    def test_cost_contract_is_explicit_and_scalar_only(self):
        self.assertEqual(m220.M178_CALLS_PER_SPD_EVENT, 1)
        self.assertEqual(m220.INCLUSIVE_SCALAR_FLOP_CEILING, 8192)


if __name__ == "__main__":
    unittest.main()
