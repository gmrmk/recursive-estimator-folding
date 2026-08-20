"""Target-free regression tests for the corrected M120 CP Jacobian recurrence."""

from __future__ import annotations

import math
import unittest

import numpy as np

from corrected_cp_jacobian import (
    cost_ledger,
    cp_local_pullback,
    dense_local_pullback,
    factors_to_dense,
    finite_difference_dense_pullback,
    he_weights,
    local_kernels,
    reverse_generated_network,
    zero_mean_variance_derivative,
)


def _symmetric_random(rng: np.random.Generator, outputs: int, width: int) -> np.ndarray:
    value = rng.normal(size=(outputs, width, width))
    return 0.5 * (value + value.swapaxes(1, 2))


def _gauge_weights(
    weights: tuple[np.ndarray, ...], scales: tuple[np.ndarray, ...]
) -> tuple[np.ndarray, ...]:
    width = weights[0].shape[0]
    diagonal = tuple(np.diag(scale) for scale in scales)
    transformed = []
    for layer, weight in enumerate(weights):
        left = np.eye(width) if layer == 0 else np.linalg.inv(diagonal[layer - 1])
        right = np.eye(width) if layer == len(weights) - 1 else diagonal[layer]
        transformed.append(left @ weight @ right)
    return tuple(transformed)


def _permuted_weights(
    weights: tuple[np.ndarray, ...], permutations: tuple[np.ndarray, ...]
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    width = weights[0].shape[0]
    matrices = tuple(np.eye(width)[:, permutation] for permutation in permutations)
    transformed = []
    for layer, weight in enumerate(weights):
        left = np.eye(width) if layer == 0 else matrices[layer - 1].T
        right = np.eye(width) if layer == len(weights) - 1 else matrices[layer]
        transformed.append(left @ weight @ right)
    return tuple(transformed), matrices


class CorrectedCPJacobianTests(unittest.TestCase):
    def test_zero_mean_central_variance_derivative_is_not_raw_second_moment_half(self) -> None:
        expected = 0.5 - 1.0 / (2.0 * math.pi)
        actual = zero_mean_variance_derivative()

        self.assertLess(abs(actual - expected), 1e-15)
        self.assertGreater(abs(actual - 0.5), 0.1)

        kernel = local_kernels(np.zeros(1), np.ones((1, 1)))
        self.assertLess(abs(kernel.h_variance[0, 0] - expected), 1e-9)

    def test_complete_dense_pullback_matches_independent_finite_differences(self) -> None:
        rng = np.random.default_rng(120401)
        width, outputs = 3, 4
        factor = rng.normal(size=(width, width))
        covariance = factor @ factor.T + np.eye(width)
        mean = rng.normal(size=width)
        mean_adjoint = rng.normal(size=(width, outputs))
        covariance_adjoint = _symmetric_random(rng, outputs, width)

        kernels = local_kernels(mean, covariance)
        analytic_mean, analytic_covariance = dense_local_pullback(
            mean_adjoint,
            covariance_adjoint,
            kernels,
            include_connected_price=True,
        )
        finite_mean, finite_covariance = finite_difference_dense_pullback(
            mean,
            covariance,
            mean_adjoint,
            covariance_adjoint,
        )
        self.assertLess(
            np.linalg.norm(analytic_mean - finite_mean) / np.linalg.norm(finite_mean),
            1e-7,
        )
        self.assertLess(
            np.linalg.norm(analytic_covariance - finite_covariance)
            / np.linalg.norm(finite_covariance),
            1e-7,
        )

    def test_e_zero_cp_matches_full_dense_oracle_and_signed_diagonal_reset(self) -> None:
        rng = np.random.default_rng(120402)
        width, outputs, rank = 4, 5, 7
        mean = np.array((-0.35, -0.1, 0.2, 0.45))
        covariance = np.diag((0.7, 0.9, 1.2, 1.4))
        mean_adjoint = rng.normal(size=(width, outputs))
        u = rng.normal(size=(width, rank))
        g = rng.normal(size=(outputs, rank))
        covariance_adjoint = factors_to_dense(u, g)
        kernels = local_kernels(mean, covariance)

        exact_mean, exact_covariance = dense_local_pullback(
            mean_adjoint,
            covariance_adjoint,
            kernels,
            include_connected_price=True,
        )
        finite_mean, finite_covariance = finite_difference_dense_pullback(
            mean,
            covariance,
            mean_adjoint,
            covariance_adjoint,
        )
        cp = cp_local_pullback(mean_adjoint, u, g, kernels)
        u_here, g_here = cp.factors_here()
        cp_covariance = factors_to_dense(u_here, g_here)

        self.assertLess(np.linalg.norm(exact_mean - finite_mean), 2e-8)
        self.assertLess(np.linalg.norm(exact_covariance - finite_covariance), 2e-8)
        self.assertLess(np.linalg.norm(cp.mean_adjoint - exact_mean), 2e-12)
        self.assertLess(np.linalg.norm(cp_covariance - exact_covariance), 2e-12)
        self.assertLess(
            np.linalg.norm(np.diagonal(cp_covariance, axis1=1, axis2=2).T - np.diagonal(exact_covariance, axis1=1, axis2=2).T),
            2e-12,
        )

    def test_generated_small_width_all_output_cp_matches_dense_base_and_tracks_rank(self) -> None:
        for width in (3, 4, 5):
            for depth in (3, 4):
                for replica in (0, 1):
                    result = reverse_generated_network(
                        he_weights(120500 + 100 * width + 10 * depth + replica, width, depth)
                    )
                    self.assertEqual(
                        result["incoming_rank_ledger"],
                        [width * multiple for multiple in range(1, depth)],
                    )
                    self.assertEqual(
                        result["rank_ledger"],
                        [width * multiple for multiple in range(1, depth + 1)],
                    )
                    self.assertLess(
                        np.linalg.norm(result["cp_mean"] - result["base_mean"]), 1e-10
                    )
                    self.assertLess(
                        np.linalg.norm(result["cp_covariance"] - result["base_covariance"]), 1e-10
                    )
                    for record in result["layer_metrics"]:
                        self.assertLess(record["cp_base_mean_relative"], 1e-10)
                        self.assertLess(record["cp_base_covariance_relative"], 1e-10)
                        self.assertTrue(np.isfinite(record["base_exact_covariance_relative"]))

    def test_permutation_and_positive_gauge_covariance_rules(self) -> None:
        width, depth = 4, 4
        weights = he_weights(120601, width, depth)
        reference = reverse_generated_network(weights)
        scales = (
            np.array((0.85, 1.12, 0.93, 1.08)),
            np.array((1.10, 0.90, 1.07, 0.88)),
            np.array((0.95, 1.08, 0.91, 1.13)),
        )
        gauged = reverse_generated_network(_gauge_weights(weights, scales))
        d_inverse = np.diag(1.0 / scales[0])
        expected_gauge_mean = d_inverse @ reference["cp_mean"]
        expected_gauge_covariance = np.einsum(
            "ia,oab,bj->oij", d_inverse, reference["cp_covariance"], d_inverse
        )
        self.assertLess(np.linalg.norm(gauged["terminal_mean"] - reference["terminal_mean"]), 1e-12)
        self.assertLess(np.linalg.norm(gauged["cp_mean"] - expected_gauge_mean), 1e-9)
        self.assertLess(
            np.linalg.norm(gauged["cp_covariance"] - expected_gauge_covariance), 1e-9
        )

        permuted_weights, permutation_matrices = _permuted_weights(
            weights,
            (
                np.array((2, 0, 3, 1)),
                np.array((1, 3, 0, 2)),
                np.array((3, 2, 1, 0)),
            ),
        )
        permuted = reverse_generated_network(permuted_weights)
        first_permutation = permutation_matrices[0]
        expected_permutation_mean = first_permutation.T @ reference["cp_mean"]
        expected_permutation_covariance = np.einsum(
            "ia,oab,bj->oij",
            first_permutation.T,
            reference["cp_covariance"],
            first_permutation,
        )
        self.assertLess(np.linalg.norm(permuted["terminal_mean"] - reference["terminal_mean"]), 1e-12)
        self.assertLess(
            np.linalg.norm(permuted["cp_mean"] - expected_permutation_mean), 1e-9
        )
        self.assertLess(
            np.linalg.norm(permuted["cp_covariance"] - expected_permutation_covariance), 1e-9
        )

    def test_cost_formula_reproduces_reported_independent_ledger(self) -> None:
        ledger = cost_ledger()
        self.assertEqual(ledger["variable_gemm_calls"], 215)
        self.assertEqual(ledger["reverse_flops"], 99_720_888_320)
        self.assertEqual(ledger["with_background_flops"], 105_909_888_320)
        self.assertAlmostEqual(ledger["reverse_billions"], 99.72088832)
        self.assertAlmostEqual(ledger["with_background_billions"], 105.90988832)


if __name__ == "__main__":
    unittest.main()
