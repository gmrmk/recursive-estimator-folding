"""Target-free regression tests for the analytic M120C dense local reference."""

from __future__ import annotations

import math
import unittest
from unittest import mock

import numpy as np

from m120c_analytic_dense_reference import (
    AnalyticReferenceFailClosed,
    FLOOR,
    analytic_dense_pullback,
    analytic_local_kernels,
    analytic_relu_gaussian_moments,
    quadrant_probability,
)
import m120c_analytic_dense_reference as reference


class AnalyticDenseReferenceTests(unittest.TestCase):
    @staticmethod
    def prospective_state() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        rng = np.random.Generator(np.random.Philox(2_026_120_703))
        width, outputs = 4, 3
        factor = rng.normal(size=(width, width))
        covariance = factor @ factor.T + 3.0 * np.eye(width)
        mean = 0.25 * rng.normal(size=width)
        b = rng.normal(size=(width, outputs))
        a = rng.normal(size=(outputs, width, width))
        return mean, covariance, b, 0.5 * (a + a.swapaxes(1, 2))

    def test_quadrant_probability_has_zero_mean_and_independence_identities(self) -> None:
        zero = quadrant_probability(0.0, 0.0, 0.0)
        self.assertEqual(zero.value, 0.25)
        self.assertEqual(zero.paired_order_disagreement, 0.0)
        rho = 0.37
        expected = 0.25 + math.asin(rho) / (2.0 * math.pi)
        observed = quadrant_probability(0.0, 0.0, rho)
        self.assertLess(abs(observed.value - expected), 1e-14)
        independent = quadrant_probability(0.8, -0.3, 0.0)
        product = (0.5 * math.erfc(-0.8 / math.sqrt(2.0))) * (0.5 * math.erfc(0.3 / math.sqrt(2.0)))
        self.assertLess(abs(independent.value - product), 1e-14)

    def test_diagonal_identities_and_symmetric_price_kernel(self) -> None:
        mean, covariance, _, _ = self.prospective_state()
        kernels = analytic_local_kernels(mean, covariance)
        sigma = np.sqrt(np.diag(covariance))
        alpha = mean / sigma
        p = np.asarray([0.5 * math.erfc(-float(x) / math.sqrt(2.0)) for x in alpha])
        phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
        moments = sigma * phi + mean * p
        self.assertLess(np.max(abs(np.diag(kernels.price_kernel) - p)), 1e-15)
        self.assertLess(np.max(abs(np.diag(kernels.h_mu) - 2.0 * moments * (1.0 - p))), 1e-14)
        self.assertLess(np.max(abs(np.diag(kernels.h_variance) - (p - moments * phi / sigma))), 1e-14)
        self.assertLess(np.max(abs(kernels.price_kernel - kernels.price_kernel.T)), 1e-15)
        self.assertLessEqual(kernels.max_quadrature_disagreement, 1e-13)

    def test_analytic_complete_dense_pullback_matches_multiscale_central_difference(self) -> None:
        mean, covariance, b, a = self.prospective_state()
        analytic_b, analytic_a = analytic_dense_pullback(b, a, analytic_local_kernels(mean, covariance))
        identity = np.eye(mean.size)

        def objective(local_mean: np.ndarray, local_covariance: np.ndarray) -> np.ndarray:
            output_mean, output_covariance = analytic_relu_gaussian_moments(local_mean, local_covariance)
            return b.T @ output_mean + np.einsum("oij,ij->o", a, output_covariance, optimize=True)

        def finite(step: float) -> tuple[np.ndarray, np.ndarray]:
            fd_b = np.empty_like(analytic_b)
            fd_a = np.zeros_like(analytic_a)
            for i in range(mean.size):
                fd_b[i] = (objective(mean + step * identity[i], covariance) - objective(mean - step * identity[i], covariance)) / (2.0 * step)
                perturbation = step * np.outer(identity[i], identity[i])
                fd_a[:, i, i] = (objective(mean, covariance + perturbation) - objective(mean, covariance - perturbation)) / (2.0 * step)
            for i in range(mean.size):
                for j in range(i + 1, mean.size):
                    perturbation = step * (np.outer(identity[i], identity[j]) + np.outer(identity[j], identity[i]))
                    derivative = (objective(mean, covariance + perturbation) - objective(mean, covariance - perturbation)) / (2.0 * step)
                    fd_a[:, i, j] = fd_a[:, j, i] = 0.5 * derivative
            return fd_b, fd_a

        coarse_b, coarse_a = finite(1.0e-3)
        fine_b, fine_a = finite(5.0e-4)
        self.assertLess(np.max(abs(fine_b - analytic_b)), 5e-8)
        self.assertLess(np.max(abs(fine_a - analytic_a)), 5e-8)
        self.assertLess(np.max(abs(fine_b - analytic_b)), np.max(abs(coarse_b - analytic_b)))
        self.assertLess(np.max(abs(fine_a - analytic_a)), np.max(abs(coarse_a - analytic_a)))

    def test_zero_near_zero_and_endpoint_inputs_reject_instead_of_clip_or_floor(self) -> None:
        with self.assertRaises(AnalyticReferenceFailClosed):
            analytic_local_kernels(np.zeros(2), np.diag((FLOOR, 1.0)))
        with self.assertRaises(AnalyticReferenceFailClosed):
            analytic_local_kernels(np.zeros(2), np.array(((1.0, 1.0 - 1e-12), (1.0 - 1e-12, 1.0))))
        with self.assertRaises(AnalyticReferenceFailClosed):
            quadrant_probability(0.0, 0.0, 1.0 - 1e-11)

    def test_global_controller_refines_a_mocked_1_48_tolerance_root_indicator(self) -> None:
        """A root discrepancy of 1.48T cannot be locally accepted as a result."""
        tolerance = reference.QUADRATURE_TOLERANCE

        def mocked_interval(_a: float, _b: float, left: float, right: float, nodes: np.ndarray, _weights: np.ndarray) -> float:
            # The 64-node value carries an indicator 1.48T on [0,1] and
            # 0.37T on each half.  A global controller must split the root;
            # it may only return after the aggregate 0.74T is audited.
            if nodes.size == 32:
                return 0.0
            return 1.48 * tolerance * (abs(right - left) / 0.5) ** 2

        with mock.patch.object(reference, "_gauss_interval", side_effect=mocked_interval):
            observed = quadrant_probability(0.0, 0.0, 0.5)
        self.assertEqual(observed.subdivisions, 1)
        self.assertLessEqual(observed.paired_order_disagreement, tolerance)

    def test_nonfinite_paired_estimates_reject_primitive_and_forward_callers_before_ledger(self) -> None:
        mean = np.zeros(2)
        covariance = np.array(((1.0, 0.5), (0.5, 1.0)))

        def assert_rejected(nonfinite: float, operation: object) -> None:
            def mocked_interval(_a: float, _b: float, _left: float, _right: float, nodes: np.ndarray, _weights: np.ndarray) -> float:
                return nonfinite if nodes.size == 32 else 0.0

            with mock.patch.object(reference, "_gauss_interval", side_effect=mocked_interval) as interval:
                with self.assertRaises(AnalyticReferenceFailClosed):
                    operation()
            self.assertEqual(interval.call_count, 2)

        for label, nonfinite in (("nan", float("nan")), ("positive infinity", float("inf")), ("negative infinity", float("-inf"))):
            for caller, operation in (
                ("primitive", lambda: quadrant_probability(0.0, 0.0, 0.5)),
                ("local kernels", lambda: analytic_local_kernels(mean, covariance)),
                ("forward moments", lambda: analytic_relu_gaussian_moments(mean, covariance)),
            ):
                with self.subTest(estimate=label, caller=caller):
                    assert_rejected(nonfinite, operation)

    def test_forward_callers_reject_nonfinite_quadrant_values_and_certificates(self) -> None:
        mean = np.zeros(2)
        covariance = np.array(((1.0, 0.5), (0.5, 1.0)))
        certificates = (
            ("nan value", reference.QuadrantProbability(float("nan"), 0.0, 0)),
            ("nan indicator", reference.QuadrantProbability(0.25, float("nan"), 0)),
            ("positive infinite indicator", reference.QuadrantProbability(0.25, float("inf"), 0)),
            ("negative infinite indicator", reference.QuadrantProbability(0.25, float("-inf"), 0)),
        )
        for label, certificate in certificates:
            for caller, operation in (
                ("local kernels", lambda: analytic_local_kernels(mean, covariance)),
                ("forward moments", lambda: analytic_relu_gaussian_moments(mean, covariance)),
            ):
                with self.subTest(certificate=label, caller=caller):
                    with mock.patch.object(reference, "quadrant_probability", return_value=certificate):
                        with self.assertRaises(AnalyticReferenceFailClosed):
                            operation()

    def test_philox_directional_and_near_endpoint_cases_are_deterministic_or_reject(self) -> None:
        rng = np.random.Generator(np.random.Philox(2_026_120_704))
        alpha_i, alpha_j = rng.normal(size=2)
        rho = float(rng.uniform(-0.8, 0.8))
        first = quadrant_probability(float(alpha_i), float(alpha_j), rho)
        second = quadrant_probability(float(alpha_i), float(alpha_j), rho)
        self.assertEqual(first, second)
        self.assertLessEqual(first.paired_order_disagreement, reference.QUADRATURE_TOLERANCE)
        endpoint = 1.0 - 0.5 * reference.ENDPOINT_MARGIN
        with self.assertRaises(AnalyticReferenceFailClosed):
            quadrant_probability(float(alpha_i), float(alpha_j), endpoint)


if __name__ == "__main__":
    unittest.main()
