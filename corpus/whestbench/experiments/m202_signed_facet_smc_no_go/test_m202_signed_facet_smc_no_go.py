"""Exact tests for the M202 sign-collapse witness."""

from __future__ import annotations

from fractions import Fraction
import unittest

from m202_signed_facet_smc_no_go import (
    absolute_mass,
    exact_result,
    generic_first_layer_candidate_facets,
    optimal_relative_variance,
    raw_gate_to_owned_mass_factor,
    sign_ratio,
    signed_mass,
)


class M202SignedFacetTests(unittest.TestCase):
    def test_exact_owned_masses(self):
        epsilon = Fraction(1, 10)
        self.assertEqual(signed_mass(epsilon), Fraction(1, 5))
        self.assertEqual(absolute_mass(epsilon), Fraction(19, 5))
        self.assertEqual(sign_ratio(epsilon), Fraction(1, 19))

    def test_sign_ratio_has_no_positive_uniform_floor(self):
        ratios = [sign_ratio(Fraction(1, 2**power)) for power in range(2, 12)]
        self.assertTrue(all(right < left for left, right in zip(ratios, ratios[1:])))
        self.assertLess(ratios[-1], Fraction(1, 1000))
        self.assertGreater(
            optimal_relative_variance(Fraction(1, 2048)),
            1_000_000,
        )

    def test_raw_nested_gate_labels_double_count_owned_boundary(self):
        self.assertEqual(raw_gate_to_owned_mass_factor(), 2)

    def test_target_first_layer_facet_envelope_is_exponential(self):
        self.assertEqual(generic_first_layer_candidate_facets(256), 2**263)

    def test_result_is_a_scoped_no_go(self):
        result = exact_result()
        self.assertTrue(result["status"].startswith("KILLED_"))
        self.assertNotIn("score", result)
        self.assertNotIn("rank", result)


if __name__ == "__main__":
    unittest.main()
