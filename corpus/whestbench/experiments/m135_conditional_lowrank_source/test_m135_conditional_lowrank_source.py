from __future__ import annotations

import itertools
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in ("m129_source_frechet_tangent", "m131_trivariate_boundary_stream"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)
sys.path.insert(0, str(HERE))

from m129_source_frechet import build_state_frechet
from m131_trivariate_boundary_stream import sampled_normal_ordered_source
from m135_conditional_lowrank_source import (
    conditional_lowrank_repeated_source,
    conditional_reference_cost_envelope,
    covariance_likelihood_ratio,
    exact_diagonal_factor_state,
    gaussian_factor_samples,
    gaussian_bridge_log_second_moment,
    generic_factor_rank_dimension_lower_bound,
    isotropic_diagonal_eigen_approximation,
)


def tensor_hermite(dimension: int, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = np.sqrt(2.0) * nodes
    weights = weights / np.sqrt(np.pi)
    grid = np.asarray(list(itertools.product(range(order), repeat=dimension)), dtype=int)
    return nodes[grid], np.prod(weights[grid], axis=1)


def generated_factor_state(n: int, r: int, seed: int):
    rng = np.random.default_rng(seed)
    d = 0.55 + rng.random(n)
    u = rng.normal(scale=0.18, size=(n, r))
    dd = rng.normal(scale=0.025, size=n)
    ud = rng.normal(scale=0.025, size=(n, r))
    mean = rng.normal(scale=0.16, size=n)
    mean_dot = rng.normal(scale=0.04, size=n)
    factor = exact_diagonal_factor_state(d, u, dd, ud)
    tangent = build_state_frechet(mean, factor.covariance(), mean_dot, factor.covariance_dot())
    weight = rng.normal(scale=0.38, size=(n, n))
    return mean, mean_dot, factor, tangent, weight


class M135ConditionalLowrankSourceTests(unittest.TestCase):
    def assert_tables_close(self, left, right, tolerance: float):
        for key in left:
            self.assertIn(key, right)
            error = float(np.max(np.abs(left[key].value - right[key].value)))
            self.assertLessEqual(error, tolerance, msg=key)

    def test_conditional_factor_quadrature_matches_full_gaussian_quadrature(self):
        _, _, factor, tangent, weight = generated_factor_state(3, 2, 135101)
        h, hweight = tensor_hermite(2, 24)
        conditional = conditional_lowrank_repeated_source(
            tangent, weight, h, factor, sample_weights=hweight
        )
        standard, standard_weight = tensor_hermite(3, 22)
        full = sampled_normal_ordered_source(
            tangent, weight, standard, sample_weights=standard_weight, bank_count=1
        )
        # Full tensor Hermite crosses ReLU kinks in all dimensions; the two
        # deterministic rules converge from different coordinate systems.
        self.assert_tables_close(conditional.repeated, full.repeated, 7.5e-3)

    def test_conditional_frechet_matches_fixed_factor_finite_difference(self):
        mean, mean_dot, factor, tangent, weight = generated_factor_state(4, 2, 135201)
        h = gaussian_factor_samples(37, 2, 135202)
        observed = conditional_lowrank_repeated_source(tangent, weight, h, factor)
        epsilon = 2.0e-6

        def value(sign: float):
            local_factor = exact_diagonal_factor_state(
                factor.residual_variance + sign * epsilon * factor.residual_variance_dot,
                factor.loadings + sign * epsilon * factor.loadings_dot,
            )
            local_tangent = build_state_frechet(
                mean + sign * epsilon * mean_dot,
                local_factor.covariance(),
                np.zeros_like(mean),
                np.zeros_like(local_factor.covariance()),
            )
            return conditional_lowrank_repeated_source(local_tangent, weight, h, local_factor)

        plus, minus = value(1.0), value(-1.0)
        for key, dual in observed.repeated.items():
            finite = (plus.repeated[key].value - minus.repeated[key].value) / (2.0 * epsilon)
            error = float(np.max(np.abs(dual.tangent - finite)))
            self.assertLessEqual(error, 2.0e-5, msg=key)

    def test_lowrank_approximation_cannot_be_silently_used_as_exact_state(self):
        rng = np.random.default_rng(135301)
        matrix = np.eye(7) + 0.035 * rng.normal(size=(7, 7))
        covariance = matrix @ matrix.T + 0.4 * np.eye(7)
        tangent = build_state_frechet(np.zeros(7), covariance, np.zeros(7), np.zeros((7, 7)))
        approximation = isotropic_diagonal_eigen_approximation(covariance, 2)
        self.assertGreater(approximation.residual_frobenius_fraction, 1.0e-4)
        with self.assertRaises(ValueError):
            conditional_lowrank_repeated_source(
                tangent,
                np.eye(7),
                np.zeros((1, 2)),
                approximation.base,
            )

    def test_likelihood_ratio_is_an_unbiased_gaussian_covariance_bridge(self):
        # A generated-only Monte Carlo premise check.  It verifies the exact
        # density identity that remains available when D+UU.T is approximate.
        rng = np.random.default_rng(135401)
        base = np.asarray([[1.1, 0.12], [0.12, 0.9]])
        target = np.asarray([[1.4, -0.18], [-0.18, 0.75]])
        x = rng.multivariate_normal(np.zeros(2), base, size=140_000)
        ratio = covariance_likelihood_ratio(x, base, target)
        self.assertAlmostEqual(float(np.mean(ratio)), 1.0, delta=0.025)
        weighted_second = (x.T * ratio) @ x / x.shape[0]
        self.assertLess(float(np.max(np.abs(weighted_second - target))), 0.055)

    def test_complete_cost_is_fail_closed_for_the_float64_reference(self):
        one = conditional_reference_cost_envelope(1)
        two = conditional_reference_cost_envelope(2)
        hypothetical_f32_three = conditional_reference_cost_envelope(3, dense_dtype="float32")
        self.assertTrue(one["strictly_below_100b"])
        self.assertFalse(two["strictly_below_100b"])
        self.assertTrue(hypothetical_f32_three["strictly_below_100b"])
        self.assertGreater(two["pair_contractions_per_common_sample"], 4)

    def test_generic_factor_model_has_no_low_rank_open_set_at_target_width(self):
        self.assertEqual(generic_factor_rank_dimension_lower_bound(256), 234)
        self.assertEqual(generic_factor_rank_dimension_lower_bound(8), 5)

    def test_likelihood_ratio_second_moment_gate_is_exact_for_diagonal_variances(self):
        finite = gaussian_bridge_log_second_moment(np.eye(2), np.diag([1.4, 1.6]))
        infinite = gaussian_bridge_log_second_moment(np.eye(2), np.diag([1.4, 2.1]))
        self.assertTrue(np.isfinite(finite))
        self.assertTrue(np.isinf(infinite))


if __name__ == "__main__":
    unittest.main()
