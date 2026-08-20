"""Response-free hostile premise tests for M147."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m122_nonzero_bridge_theory", ROOT / "m129_source_frechet_tangent"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m122_nonzero_bridge import NonzeroBridgeFailClosed  # noqa: E402
from m129_source_frechet import (  # noqa: E402
    build_state_frechet,
    exact_collision_cumulant_dot,
    pair_raw_moment_series_dot,
)
from m147_endpoint_safe_bridge import (  # noqa: E402
    EndpointCertificationFailure,
    bivariate_relu_raw_dot_endpoint,
    build_endpoint_state_frechet,
    collision211_local_state_dot,
    conditional_collision211_endpoint_dot,
    endpoint_positive_power_raw,
    quadrant_probability_angle,
)


def pair_state(
    alpha: np.ndarray,
    sigma: np.ndarray,
    rho: float,
    alpha_dot: np.ndarray,
    sigma_dot: np.ndarray,
    rho_dot: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = alpha * sigma
    mean_dot = alpha_dot * sigma + alpha * sigma_dot
    covariance = np.array(
        [
            [sigma[0] ** 2, rho * sigma[0] * sigma[1]],
            [rho * sigma[0] * sigma[1], sigma[1] ** 2],
        ],
        dtype=np.float64,
    )
    covariance_dot = np.array(
        [
            [2.0 * sigma[0] * sigma_dot[0], 0.0],
            [0.0, 2.0 * sigma[1] * sigma_dot[1]],
        ],
        dtype=np.float64,
    )
    covariance_dot[0, 1] = covariance_dot[1, 0] = (
        rho_dot * sigma[0] * sigma[1]
        + rho * (sigma_dot[0] * sigma[1] + sigma[0] * sigma_dot[1])
    )
    return mean, covariance, mean_dot, covariance_dot


class M147EndpointSafeTests(unittest.TestCase):
    def assert_close(self, left: float, right: float, tolerance: float = 2.0e-9):
        self.assertLessEqual(abs(left - right), tolerance * (1.0 + abs(right)))

    def test_angular_quadrant_zero_threshold_and_rigorous_endpoint_bounds(self):
        for rho in (-1.0, -1.0 + 1.0e-12, -0.8, 0.0, 0.8, 1.0 - 1.0e-12, 1.0):
            certificate = quadrant_probability_angle(0.0, 0.0, rho)
            exact = 0.25 + math.asin(rho) / (2.0 * math.pi)
            self.assert_close(certificate.value, exact, 3.0e-13)
            self.assertLessEqual(certificate.rigorous_lower - 2e-15, exact)
            self.assertGreaterEqual(certificate.rigorous_upper + 2e-15, exact)

    def test_rank_one_values_and_one_sided_price_derivative(self):
        # Same latent Z: E[Z_+^2]=1/2.  Opposite latent signs have disjoint
        # positive support at zero means.
        for sign, expected in ((1, 0.5), (-1, 0.0)):
            covariance = np.array([[1.0, float(sign)], [float(sign), 1.0]])
            result = bivariate_relu_raw_dot_endpoint(
                np.zeros(2), covariance, np.zeros(2), np.zeros((2, 2))
            )
            self.assertEqual(result.derivative_kind, "one-sided-PSD-directional")
            self.assert_close(result.raw, expected, 1e-15)
            self.assert_close(
                result.standardized_rho_derivative,
                0.5 if sign == 1 else 0.0,
                1e-15,
            )
        self.assert_close(endpoint_positive_power_raw(0.0, 0.0, 1, 2, 1), math.sqrt(2.0 / math.pi), 1e-14)

    def test_near_negative_endpoint_avoids_rosenbaum_cancellation(self):
        rho = -1.0 + 1.0e-12
        result = bivariate_relu_raw_dot_endpoint(
            np.zeros(2),
            np.array([[1.0, rho], [rho, 1.0]]),
            np.zeros(2),
            np.zeros((2, 2)),
        )
        theta = math.acos(abs(rho))
        stable_exact = (math.sin(theta) - theta * math.cos(theta)) / (2.0 * math.pi)
        self.assert_close(result.raw, stable_exact, 2e-14)
        self.assertGreater(result.moment_integrand_evaluations, 0)
        self.assertGreaterEqual(result.raw + 5e-24, result.rigorous_raw_lower)
        self.assertLessEqual(result.raw, result.rigorous_raw_upper + 5e-24)

    def test_matches_m129_hermite_pair_on_its_certified_domain(self):
        alpha = np.array([-0.37, 0.62])
        sigma = np.array([0.9, 1.3])
        alpha_dot = np.array([0.04, -0.03])
        sigma_dot = np.array([0.02, -0.01])
        for rho in (-0.75, -0.35, 0.0, 0.35, 0.75):
            rho_dot = 0.015
            mean, covariance, mean_dot, covariance_dot = pair_state(
                alpha, sigma, rho, alpha_dot, sigma_dot, rho_dot
            )
            observed = bivariate_relu_raw_dot_endpoint(
                mean, covariance, mean_dot, covariance_dot
            )
            expected = pair_raw_moment_series_dot(
                float(alpha[0]),
                float(sigma[0]),
                1,
                float(alpha[1]),
                float(sigma[1]),
                1,
                rho,
                float(alpha_dot[0]),
                float(sigma_dot[0]),
                float(alpha_dot[1]),
                float(sigma_dot[1]),
                rho_dot,
                terms=96,
            )
            self.assert_close(observed.raw, expected[0], 2e-10)
            self.assert_close(observed.tangent, expected[1], 3e-9)

    def test_interior_frechet_near_both_endpoints_and_symmetry(self):
        mean = np.array([-0.3, 0.7])
        sigma = np.array([1.2, 0.8])
        mean_dot = np.array([0.2, -0.1])
        covariance_dot = np.array([[0.1, 0.03], [0.03, -0.05]])
        for rho in (-0.999999, 0.999999):
            covariance = np.array(
                [[sigma[0] ** 2, rho * np.prod(sigma)], [rho * np.prod(sigma), sigma[1] ** 2]]
            )
            observed = bivariate_relu_raw_dot_endpoint(
                mean, covariance, mean_dot, covariance_dot
            )
            epsilon = 2.0e-7
            plus = bivariate_relu_raw_dot_endpoint(
                mean + epsilon * mean_dot,
                covariance + epsilon * covariance_dot,
                np.zeros(2),
                np.zeros((2, 2)),
            ).raw
            minus = bivariate_relu_raw_dot_endpoint(
                mean - epsilon * mean_dot,
                covariance - epsilon * covariance_dot,
                np.zeros(2),
                np.zeros((2, 2)),
            ).raw
            self.assert_close(observed.tangent, (plus - minus) / (2.0 * epsilon), 8e-8)
            permutation = np.array([1, 0])
            swapped = bivariate_relu_raw_dot_endpoint(
                mean[permutation],
                covariance[np.ix_(permutation, permutation)],
                mean_dot[permutation],
                covariance_dot[np.ix_(permutation, permutation)],
            )
            self.assert_close(swapped.raw, observed.raw, 2e-13)
            self.assert_close(swapped.tangent, observed.tangent, 2e-12)

    def test_positive_gauge_covariance_and_endpoint_tangent_cone(self):
        alpha = np.array([0.2, -0.4])
        sigma = np.array([0.8, 1.1])
        mean, covariance, mean_dot, covariance_dot = pair_state(
            alpha, sigma, 0.93, np.array([0.03, -0.02]), np.array([0.01, 0.015]), -0.04
        )
        base = bivariate_relu_raw_dot_endpoint(mean, covariance, mean_dot, covariance_dot)
        gauge = np.diag([2.3, 0.4])
        gauged_covariance = gauge @ covariance @ gauge
        gauged_covariance = 0.5 * (gauged_covariance + gauged_covariance.T)
        gauged_covariance_dot = gauge @ covariance_dot @ gauge
        gauged_covariance_dot = 0.5 * (gauged_covariance_dot + gauged_covariance_dot.T)
        transformed = bivariate_relu_raw_dot_endpoint(
            gauge @ mean,
            gauged_covariance,
            gauge @ mean_dot,
            gauged_covariance_dot,
        )
        scale = gauge[0, 0] * gauge[1, 1]
        self.assert_close(transformed.raw, scale * base.raw, 2e-12)
        self.assert_close(transformed.tangent, scale * base.tangent, 2e-11)

        endpoint_covariance = np.ones((2, 2))
        outward = np.array([[0.0, 1.0], [1.0, 0.0]])
        with self.assertRaises(EndpointCertificationFailure):
            bivariate_relu_raw_dot_endpoint(
                np.zeros(2), endpoint_covariance, np.zeros(2), outward
            )

    def test_high_correlation_state_replaces_pair_cap_but_not_spd_boundary(self):
        mean = np.array([0.2, -0.1, 0.35])
        correlation = np.array(
            [[1.0, 0.93, 0.89], [0.93, 1.0, 0.91], [0.89, 0.91, 1.0]]
        )
        sigma = np.array([1.1, 0.8, 1.3])
        covariance = correlation * np.outer(sigma, sigma)
        mean_dot = np.array([0.03, -0.02, 0.01])
        covariance_dot = np.array(
            [[0.02, 0.003, -0.002], [0.003, -0.01, 0.004], [-0.002, 0.004, 0.015]]
        )
        state = build_endpoint_state_frechet(
            mean, covariance, mean_dot, covariance_dot
        )
        self.assertTrue(np.all(np.isfinite(state.state.bridge)))
        with self.assertRaises(NonzeroBridgeFailClosed):
            build_state_frechet(mean, covariance, mean_dot, covariance_dot)

        # Pair endpoint support does not make a singular full-width Frechet
        # state legitimate: the latter remains explicitly open-SPD only.
        singular = np.array([[1.0, 1.0], [1.0, 1.0]])
        bivariate_relu_raw_dot_endpoint(
            np.zeros(2), singular, np.zeros(2), np.zeros((2, 2))
        )
        with self.assertRaises(EndpointCertificationFailure):
            build_endpoint_state_frechet(
                np.zeros(2), singular, np.zeros(2), np.zeros((2, 2))
            )

    def test_central_211_matches_independent_partition_oracle(self):
        mean = np.array([0.2, -0.1, 0.35])
        correlation = np.array(
            [[1.0, 0.35, -0.2], [0.35, 1.0, 0.25], [-0.2, 0.25, 1.0]]
        )
        sigma = np.array([1.1, 0.8, 1.3])
        covariance = correlation * np.outer(sigma, sigma)
        mean_dot = np.array([0.03, -0.02, 0.01])
        covariance_dot = np.array(
            [[0.02, 0.003, -0.002], [0.003, -0.01, 0.004], [-0.002, 0.004, 0.015]]
        )
        observed_state = build_endpoint_state_frechet(
            mean, covariance, mean_dot, covariance_dot
        )
        expected_state = build_state_frechet(
            mean, covariance, mean_dot, covariance_dot
        )
        observed = conditional_collision211_endpoint_dot(
            observed_state, 0, 1, 2
        )
        expected = exact_collision_cumulant_dot(
            expected_state, (0, 0, 1, 2), terms=32
        )
        self.assert_close(observed.cumulant, expected[0], 3e-10)
        self.assert_close(observed.cumulant_tangent, expected[1], 3e-9)
        swapped = conditional_collision211_endpoint_dot(
            observed_state, 0, 2, 1
        )
        self.assert_close(swapped.defect, observed.defect, 2e-11)
        self.assert_close(swapped.defect_tangent, observed.defect_tangent, 2e-10)

    def test_near_endpoint_conditional_211_finite_difference_and_cost_counter(self):
        # Conditioning on variable zero leaves singleton correlation .999.
        covariance = np.array(
            [[1.0, 0.5, 0.5], [0.5, 1.0, 0.99925], [0.5, 0.99925, 1.0]]
        )
        mean = np.array([0.1, -0.2, 0.3])
        mean_dot = np.array([0.01, -0.02, 0.015])
        covariance_dot = np.array(
            [[0.01, 0.002, -0.001], [0.002, -0.005, 0.001], [-0.001, 0.001, 0.008]]
        )
        tangent = build_endpoint_state_frechet(
            mean, covariance, mean_dot, covariance_dot
        )
        observed = conditional_collision211_endpoint_dot(tangent, 0, 1, 2)
        epsilon = 2.0e-6
        values = []
        for sign in (1.0, -1.0):
            local_mean = mean + sign * epsilon * mean_dot
            local_covariance = covariance + sign * epsilon * covariance_dot
            local = build_endpoint_state_frechet(
                local_mean,
                local_covariance,
                np.zeros(3),
                np.zeros((3, 3)),
            )
            values.append(
                conditional_collision211_endpoint_dot(local, 0, 1, 2).cumulant
            )
        finite_difference = (values[0] - values[1]) / (2.0 * epsilon)
        self.assert_close(observed.cumulant_tangent, finite_difference, 2e-6)
        self.assertLess(observed.value_disagreement, 2e-8)
        # This is evidence, not a target-cost pass: the count is deliberately
        # exposed so the manifest can reject the scalar path against reserve.
        self.assertGreater(observed.quadrant_integrand_evaluations, 10_000)

    def test_width_independent_local_api_accepts_exact_conditional_endpoint(self):
        # A is independent; B=C at background.  The B-C conditional pair is
        # exactly rank one, while the tangent opens its null direction inward.
        covariance = np.array(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 1.0], [0.0, 1.0, 1.0]]
        )
        covariance_dot = np.array(
            [[0.0, 0.0, 0.0], [0.0, 1.0, -1.0], [0.0, -1.0, 1.0]]
        )
        observed = collision211_local_state_dot(
            np.array([0.1, -0.2, 0.3]),
            covariance,
            np.array([0.01, 0.0, 0.0]),
            covariance_dot,
        )
        self.assertTrue(math.isfinite(observed.cumulant))
        self.assertTrue(math.isfinite(observed.cumulant_tangent))
        self.assertLess(observed.value_disagreement, 2e-8)

        outward = -covariance_dot
        with self.assertRaises(EndpointCertificationFailure):
            collision211_local_state_dot(
                np.array([0.1, -0.2, 0.3]),
                covariance,
                np.zeros(3),
                outward,
            )

    def test_degenerate_conditional_singletons_fail_closed_explicitly(self):
        # These are feasible PSD local states with a feasible zero tangent, but
        # conditioning on the repeated coordinate leaves at least one
        # deterministic singleton.  M147 has no certificate for its ReLU-kink
        # tangent, so this distinct stratum must be refused before quadrature.
        cases = (
            np.ones((3, 3)),
            np.array([[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
        )
        for covariance in cases:
            with self.assertRaisesRegex(
                EndpointCertificationFailure, "degenerate conditional singleton"
            ):
                collision211_local_state_dot(
                    np.array([0.1, 0.2, 0.3]),
                    covariance,
                    np.zeros(3),
                    np.zeros((3, 3)),
                )

    def test_extreme_finite_moments_fail_closed_not_nonfinite(self):
        for mean, rho in (
            (np.array([1.0e308, 1.0e308]), 1.0),
            (np.array([1.0e200, 1.0e200]), -1.0),
        ):
            with self.assertRaises(EndpointCertificationFailure):
                bivariate_relu_raw_dot_endpoint(
                    mean,
                    np.array([[1.0, rho], [rho, 1.0]]),
                    np.zeros(2),
                    np.zeros((2, 2)),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
