"""Response-free regression tests for the M162 fixed-rule falsifier."""

from __future__ import annotations

from pathlib import Path
import math
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m162_plackett_tallis_falsifier import (  # noqa: E402
    central_bivariate_orthant_correlation_derivative,
    central_trivariate_orthant_closed_form,
    fixed_plackett_zero_threshold_probability,
)


class M162PlackettTallisFalsifierTests(unittest.TestCase):
    def test_closed_form_retains_the_rank_one_common_factor_orthant_limit(self) -> None:
        self.assertEqual(
            central_trivariate_orthant_closed_form(1.0, 1.0, 1.0), 0.5
        )
        self.assertEqual(
            central_trivariate_orthant_closed_form(0.0, 0.0, 0.0), 0.125
        )

    def test_straight_fixed_87_node_plackett_rule_misses_a_high_correlation_reference(self) -> None:
        rho = 0.999
        exact = central_trivariate_orthant_closed_form(rho, 0.0, 0.0)
        observed = fixed_plackett_zero_threshold_probability(
            rho, 0.0, 0.0, nodes=87, endpoint_square_map=False
        )
        self.assertGreater(abs(observed - exact), 2.0e-8)

    def test_fixed_endpoint_square_map_still_misses_a_near_rank_one_reference(self) -> None:
        rho = 0.999999
        exact = central_trivariate_orthant_closed_form(rho, 0.0, 0.0)
        observed = fixed_plackett_zero_threshold_probability(
            rho, 0.0, 0.0, nodes=87, endpoint_square_map=True
        )
        self.assertGreater(abs(observed - exact), 2.0e-8)

    def test_orthant_probability_covariance_derivative_is_unbounded_at_the_rank_face(self) -> None:
        rho = math.nextafter(1.0, 0.0)
        derivative = central_bivariate_orthant_correlation_derivative(rho)
        self.assertGreater(derivative, 1.0e6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
