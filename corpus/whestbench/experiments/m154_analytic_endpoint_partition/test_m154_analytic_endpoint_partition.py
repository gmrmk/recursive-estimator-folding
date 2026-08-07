"""Response-free small-dimensional tests for M154's analytic rank-one branch."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m147_endpoint_safe_bridge", ROOT / "m129_source_frechet_tangent"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m154_analytic_endpoint_partition import (  # noqa: E402
    Analytic211Failure,
    analytic_rank1_collision211_local_state_dot,
    analytic_rank1_cost_bound,
)
from m147_endpoint_safe_bridge import (  # noqa: E402
    build_endpoint_state_frechet,
    conditional_collision211_endpoint_dot,
)


def rank_one_state(
    latent: np.ndarray,
    latent_dot: np.ndarray,
    mean: np.ndarray,
    mean_dot: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    covariance = np.outer(latent, latent)
    covariance_dot = (
        np.outer(latent_dot, latent) + np.outer(latent, latent_dot)
    )
    return mean, covariance, mean_dot, covariance_dot


class AnalyticEndpointPartitionTests(unittest.TestCase):
    def assert_close(self, left: float, right: float, tolerance: float = 2e-10) -> None:
        self.assertLessEqual(abs(left - right), tolerance * (1.0 + abs(right)))

    def test_rank_one_zero_mean_common_factor_has_exact_central_and_cumulant(self) -> None:
        mean, covariance, mean_dot, covariance_dot = rank_one_state(
            np.ones(3), np.zeros(3), np.zeros(3), np.zeros(3)
        )
        observed = analytic_rank1_collision211_local_state_dot(
            mean, covariance, mean_dot, covariance_dot
        )
        mu = 1.0 / math.sqrt(2.0 * math.pi)
        central = 1.5 - 5.0 / (2.0 * math.pi) - 3.0 / (4.0 * math.pi**2)
        variance = 0.5 - mu * mu
        self.assert_close(observed.central_fourth, central, 3e-13)
        self.assert_close(observed.cumulant, central - 3.0 * variance * variance, 3e-13)
        self.assertEqual(observed.rank, 1)
        self.assertEqual(observed.method, "analytic-rank1-moving-kink-partition-price")
        self.assertGreater(observed.analytic_intervals, 0)
        self.assertEqual(observed.special_function_calls, 0)

    def test_rank_one_frechet_matches_a_rank_preserving_centered_difference(self) -> None:
        latent = np.array([1.2, -0.7, 0.9])
        latent_dot = np.array([-0.03, 0.05, 0.02])
        mean = np.array([0.15, -0.21, 0.34])
        mean_dot = np.array([0.04, -0.02, 0.01])
        args = rank_one_state(latent, latent_dot, mean, mean_dot)
        observed = analytic_rank1_collision211_local_state_dot(*args)
        epsilon = 2.0e-6
        plus = analytic_rank1_collision211_local_state_dot(
            *(rank_one_state(
                latent + epsilon * latent_dot,
                np.zeros(3),
                mean + epsilon * mean_dot,
                np.zeros(3),
            ))
        )
        minus = analytic_rank1_collision211_local_state_dot(
            *(rank_one_state(
                latent - epsilon * latent_dot,
                np.zeros(3),
                mean - epsilon * mean_dot,
                np.zeros(3),
            ))
        )
        self.assert_close(
            observed.cumulant_tangent,
            (plus.cumulant - minus.cumulant) / (2.0 * epsilon),
            4e-7,
        )

    def test_rank_one_opening_direction_matches_m147_one_sided_response_free_oracle(self) -> None:
        # This M147 call is an independent small-dimensional test oracle only;
        # M154 itself makes no angular or outer quadrature call.  J+tI opens
        # both rank-one null directions and exercises Price's delta boundary.
        mean = np.zeros(3)
        covariance = np.ones((3, 3))
        opening = np.eye(3)
        observed = analytic_rank1_collision211_local_state_dot(
            mean, covariance, np.zeros(3), opening
        )
        epsilon = 2.0e-6
        oracle_state = build_endpoint_state_frechet(
            mean, covariance + epsilon * opening, np.zeros(3), np.zeros((3, 3))
        )
        oracle = conditional_collision211_endpoint_dot(oracle_state, 0, 1, 2)
        forward = (oracle.cumulant - observed.cumulant) / epsilon
        self.assert_close(observed.cumulant_tangent, forward, 3e-3)
        self.assertGreater(oracle.quadrant_integrand_evaluations, 0)
        self.assertEqual(observed.special_function_calls, 0)

    def test_singleton_permutation_and_positive_gauge_are_covariant(self) -> None:
        args = rank_one_state(
            np.array([1.1, -0.8, 0.6]),
            np.array([0.02, 0.03, -0.01]),
            np.array([0.2, -0.3, 0.1]),
            np.array([0.01, -0.02, 0.03]),
        )
        observed = analytic_rank1_collision211_local_state_dot(*args)
        permutation = np.array([0, 2, 1])
        swapped = analytic_rank1_collision211_local_state_dot(
            args[0][permutation],
            args[1][np.ix_(permutation, permutation)],
            args[2][permutation],
            args[3][np.ix_(permutation, permutation)],
        )
        self.assert_close(swapped.cumulant, observed.cumulant, 5e-12)
        self.assert_close(swapped.cumulant_tangent, observed.cumulant_tangent, 5e-11)
        gauge = np.diag([1.7, 0.8, 1.3])
        gauged_covariance = gauge @ args[1] @ gauge
        gauged_covariance = 0.5 * (gauged_covariance + gauged_covariance.T)
        gauged_covariance_dot = gauge @ args[3] @ gauge
        gauged_covariance_dot = 0.5 * (gauged_covariance_dot + gauged_covariance_dot.T)
        gauged = analytic_rank1_collision211_local_state_dot(
            gauge @ args[0],
            gauged_covariance,
            gauge @ args[2],
            gauged_covariance_dot,
        )
        scale = gauge[0, 0] ** 2 * gauge[1, 1] * gauge[2, 2]
        self.assert_close(gauged.cumulant, scale * observed.cumulant, 1e-10)
        self.assert_close(gauged.cumulant_tangent, scale * observed.cumulant_tangent, 1e-9)

    def test_rank_two_and_generic_spd_refuse_instead_of_using_a_grid_or_ridge(self) -> None:
        mean = np.array([0.1, -0.2, 0.3])
        tangent = np.zeros(3)
        factors = np.array([[1.0, 0.0], [0.2, 1.0], [-0.3, 0.5]])
        rank_two = factors @ factors.T
        with self.assertRaisesRegex(Analytic211Failure, "rank-2"):
            analytic_rank1_collision211_local_state_dot(mean, rank_two, tangent, np.zeros((3, 3)))
        generic = np.array([[1.0, 0.2, -0.1], [0.2, 1.1, 0.15], [-0.1, 0.15, 0.9]])
        with self.assertRaisesRegex(Analytic211Failure, "rank-3"):
            analytic_rank1_collision211_local_state_dot(mean, generic, tangent, np.zeros((3, 3)))

    def test_outward_rank_one_tangent_and_nonfinite_inputs_fail_closed(self) -> None:
        mean, covariance, _mean_dot, _covariance_dot = rank_one_state(
            np.array([1.0, 0.8, -0.6]), np.zeros(3), np.zeros(3), np.zeros(3)
        )
        # A negative null-space quadratic form points outside the PSD cone.
        outward = -np.diag([0.0, 1.0, 1.0])
        with self.assertRaisesRegex(Analytic211Failure, "PSD tangent"):
            analytic_rank1_collision211_local_state_dot(mean, covariance, np.zeros(3), outward)
        with self.assertRaises(Analytic211Failure):
            analytic_rank1_collision211_local_state_dot(
                np.array([math.inf, 0.0, 0.0]), covariance, np.zeros(3), np.zeros((3, 3))
            )

    def test_rank_one_cost_is_bounded_far_below_the_m151_inclusive_allowance(self) -> None:
        bound = analytic_rank1_cost_bound(coefficient_calls=3968)
        self.assertEqual(bound["coefficient_calls"], 3968)
        self.assertEqual(bound["special_function_calls_per_coefficient"], 0)
        self.assertLess(bound["total_billed_ops"], 10_291_363_760)
        self.assertTrue(bound["fits_m151_inclusive_allowance"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
