"""Response-free M178 unit tests: dispatch, symmetry, scale gauge,
determinism, static-count data-independence, contract widths, and reference
containment on a deterministic sub-grid (the full grid is exercised by
run_m178_static_audit.py, which writes the frozen results JSON)."""

from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import math
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m178_certified_phi2_owent as m178  # noqa: E402
import run_m178_static_audit as audit  # noqa: E402


class M178DispatchTests(unittest.TestCase):
    def test_refusals_are_fail_closed(self):
        for bad in [(0.5, 0.25, 1.0), (0.5, 0.25, -1.0),
                    (0.5, 0.25, 1.0000001), (0.5, 0.25, math.nan),
                    (math.inf, 0.0, 0.5), (0.0, -math.inf, 0.5),
                    (0.5, 0.25, math.nextafter(m178.RHO_MAX, 2.0))]:
            r = m178.evaluate(*bad)
            self.assertTrue(r.refused, bad)
            self.assertIn(r.reason,
                          ("NONFINITE_INPUT", "NON_SPD_OR_RANK_ONE_CHART"))

    def test_near_endpoint_spd_is_accepted_not_clipped(self):
        r = m178.evaluate(0.5, 0.5, m178.RHO_MAX)
        self.assertFalse(r.refused)
        r = m178.evaluate(0.5, 0.5, -m178.RHO_MAX)
        self.assertFalse(r.refused)

    def test_symmetry_is_bitwise(self):
        for (a, b, rho) in [(0.5, 0.25, 0.3), (-1.0, 2.0, -0.9),
                            (3.0, -3.0, 0.999999), (7.0, 2.0, 0.5),
                            (0.0, 1.0, 0.5), (-4.0, 0.0, -0.5)]:
            r1 = m178.evaluate(a, b, rho)
            r2 = m178.evaluate(b, a, rho)
            self.assertEqual(r1.value, r2.value)
            self.assertEqual(r1.d_a, r2.d_b)
            self.assertEqual(r1.d_b, r2.d_a)
            self.assertEqual(r1.d_rho, r2.d_rho)

    def test_dyadic_scale_gauge_invariance(self):
        # M159 caller path: (mu, C) and (lam*mu, lam^2*C) with dyadic lam
        # normalize to bitwise-identical (a, b, rho); evaluator output is
        # therefore bitwise scale-invariant.
        mu = (0.375, -1.25)
        C = ((4.0, 1.5), (1.5, 9.0))
        for k in (-8, -1, 1, 12):
            lam = 2.0 ** k
            s0, s1 = math.sqrt(C[0][0]), math.sqrt(C[1][1])
            a0 = (mu[0] / s0, mu[1] / s1, C[0][1] / (s0 * s1))
            t0, t1 = math.sqrt(lam * lam * C[0][0]), math.sqrt(lam * lam * C[1][1])
            a1 = (lam * mu[0] / t0, lam * mu[1] / t1,
                  (lam * lam * C[0][1]) / (t0 * t1))
            self.assertEqual(a0, a1)
            r0, r1 = m178.evaluate(*a0), m178.evaluate(*a1)
            self.assertEqual((r0.value, r0.d_a, r0.d_b, r0.d_rho),
                             (r1.value, r1.d_a, r1.d_b, r1.d_rho))

    def test_determinism_in_process(self):
        for (a, b, rho) in [(0.5, 0.25, 0.3), (3.0, -3.0, 0.999999)]:
            r1 = m178.evaluate(a, b, rho)
            r2 = m178.evaluate(a, b, rho)
            self.assertEqual((r1.value, r1.d_a, r1.d_b, r1.d_rho),
                             (r2.value, r2.d_a, r2.d_b, r2.d_rho))


class M178CostTests(unittest.TestCase):
    def test_static_count_census_ceiling_and_billed_agreement(self):
        census = audit.static_leaf_census(audit.build_grid()[::7],
                                          random_points=1500)
        worst = max(r["charged_flops"] for r in census.values())
        self.assertLessEqual(worst + m178.F_EPILOGUE, 20000)
        for row in audit.flopscope_billed_sample(census, sample=6):
            self.assertTrue(row["match"], row)

    def test_no_opaque_special_function_in_source(self):
        src = (HERE / "m178_certified_phi2_owent.py").read_text()
        for banned in ("stats.norm", "math.erf", "scipy", "ncdf("):
            self.assertNotIn(banned, src)


class M178ConstantTests(unittest.TestCase):
    def test_gl20_monomial_exactness_in_decimal(self):
        getcontext().prec = 60
        nodes = [Decimal(s) for s in m178.GL20_NODES_DEC]
        weights = [Decimal(s) for s in m178.GL20_WEIGHTS_DEC]
        for k in range(40):
            q = sum(w * u ** k for u, w in zip(nodes, weights))
            exact = Decimal(1) / Decimal(k + 1)
            self.assertLess(abs(q - exact), Decimal("1e-28"), k)

    def test_frozen_bound_arithmetic(self):
        # deep-tail bracket: exp(-18)/(2*pi) = 2.4240e-9 < 2.43e-9
        # (the protocol's prose said 2.4e-9 — an arithmetic slip disclosed
        # in the report; the 2e-8 contract is unaffected)
        self.assertLess(math.exp(-18.0) / (2 * math.pi), 2.43e-9)
        # erf tail enclosure width at x = 3.5 is below 8e-10
        x = 3.5
        width = (15 / (8 * x ** 6)) * math.exp(-x * x) / (x * math.sqrt(math.pi))
        self.assertLess(width, 8e-10)


class M178ContainmentSubsetTests(unittest.TestCase):
    """Deterministic sub-grid containment against dps=50 references."""

    POINTS = [
        (0.5, 0.25, 0.3), (0.0, 0.0, 0.7), (0.0, 1.0, -0.5),
        (-1.0, 2.0, -0.9), (2.0, 2.0, 0.99), (3.0, -3.0, 0.999999),
        (0.5, 0.5, 1 - 2 ** -52), (-0.5, 0.5, -(1 - 2 ** -52)),
        (7.0, 7.0, 0.9), (-7.0, 3.0, -0.99), (10.0, -10.0, 0.5),
        (2.0 ** -30, 1.0, 0.5), (-2.0, -2.0, 0.5), (4.95, 1.0, 0.9),
        (37.5, 37.5, 0.9), (-37.5, 2.0, 0.0), (1.0, 1.0, 2 ** -52),
        (0.25, 8.0, 0.999999), (3.4999, -3.5000001, -0.999999),
        (1.0, 1.0 - 2.0 ** -45 + 1.0, 1.0 - 2.0 ** -45),
    ]

    def test_subset_containment_and_contract(self):
        rows = audit.audit_chunk(self.POINTS)
        for row in rows:
            self.assertTrue(row["value_contained"], row)
            self.assertTrue(row["da_contained"], row)
            self.assertTrue(row["db_contained"], row)
            self.assertTrue(row["drho_contained"], row)
            self.assertLessEqual(row["value_w"], 2e-8, row["point"])


class M178AdversarialRegressionTests(unittest.TestCase):
    """Counterexamples found by the pre-freeze adversarial verification;
    each fired a kill gate against the draft and must stay fixed."""

    def test_delta_sign_never_uses_underflowable_product(self):
        # all four sign combinations at |mean| ~ 1e-200 and the deepest
        # subnormal must equal the a,b -> 0 limit 1/4 + asin(-1/2)/(2 pi)
        limit = 1.0 / 6.0
        for pt in [(1e-200, -1e-200, -0.5), (-1e-200, -1e-200, -0.5),
                   (1e-200, 1e-200, -0.5), (-1e-200, 1e-200, -0.5),
                   (5e-324, -5e-324, -0.5), (-5e-324, 5e-324, -0.5)]:
            r = m178.evaluate(*pt)
            self.assertFalse(r.refused, pt)
            self.assertLessEqual(abs(r.value - limit), r.w_value + 1e-14, pt)

    def test_overflow_channels_return_exact_limits_not_nan(self):
        for pt, expect in [((-1.5e308, 1.5e308, 0.9), 0.0),
                           ((1.5e308, -1.5e308, 0.9), 0.0),
                           ((1e-320, 1e301, -(1 - 2 ** -52)), 0.5),
                           ((1.7976931348623157e308,
                             1.7976931348623157e308, -0.9), 1.0)]:
            r = m178.evaluate(*pt)
            self.assertFalse(r.refused, pt)
            self.assertTrue(math.isfinite(r.value), pt)
            self.assertLessEqual(abs(r.value - expect), r.w_value + 1e-12, pt)

    def test_enclosure_never_fakes_an_interval_for_nan(self):
        e = m178.evaluate(math.nan, 0.0, 0.0).enclosure()
        self.assertTrue(all(math.isnan(x) for x in e))

    def test_tiny_mean_at_rank_face_carries_qarg_width(self):
        # audit-v2 counterexamples: maximal cancellation in b - rho*a at
        # the face makes Delta_q ~ u|rho|/s; the value width must carry
        # the W_QARG term.  True value = 1/4 + asin(rho)/(2 pi) + O(1e-200).
        for sa in (1.0, -1.0):
            for sb in (1.0, -1.0):
                for srho in (1.0, -1.0):
                    rho = srho * m178.RHO_MAX
                    r = m178.evaluate(sa * 1e-200, sb * 1e-200, rho)
                    truth = 0.25 + math.asin(rho) / (2 * math.pi)
                    self.assertFalse(r.refused)
                    self.assertLessEqual(abs(r.value - truth),
                                         r.w_value + 1e-14,
                                         (sa, sb, rho))


if __name__ == "__main__":
    unittest.main()
