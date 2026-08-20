"""Generated-only identities for the M125/M125b forward tangent carriers."""

from __future__ import annotations

import unittest

import numpy as np

from m125_forward_tangent import (
    LocalReluJacobian,
    TangentState,
    explicit_source_superposition,
    inhomogeneous_source_recurrence,
    tangent_stage,
)


class M125ForwardTangentTests(unittest.TestCase):
    def test_inhomogeneous_recurrence_equals_explicit_source_superposition(self) -> None:
        rng = np.random.Generator(np.random.Philox(125_002))
        width = 5
        source_count = 6

        sources: list[TangentState] = []
        for _ in range(source_count):
            mean = rng.normal(size=width)
            raw = rng.normal(size=(width, width))
            covariance = 0.5 * (raw + raw.T)
            sources.append(TangentState(mean, covariance))

        weights: list[np.ndarray] = []
        jacobians: list[LocalReluJacobian] = []
        for _ in range(source_count - 1):
            weights.append(rng.normal(scale=0.2, size=(width, width)))
            probability = rng.uniform(0.1, 0.9, size=width)
            mean_variance = rng.normal(scale=0.1, size=width)
            price_raw = rng.normal(scale=0.1, size=(width, width))
            price = 0.5 * (price_raw + price_raw.T)
            h_mu = rng.normal(scale=0.1, size=(width, width))
            h_variance = rng.normal(scale=0.1, size=(width, width))
            jacobians.append(
                LocalReluJacobian(
                    probability,
                    mean_variance,
                    price,
                    h_mu,
                    h_variance,
                )
            )

        explicit = explicit_source_superposition(sources, weights, jacobians)
        coalesced = inhomogeneous_source_recurrence(sources, weights, jacobians)

        np.testing.assert_allclose(coalesced.mean, explicit.mean, rtol=2e-13, atol=2e-13)
        np.testing.assert_allclose(
            coalesced.covariance,
            explicit.covariance,
            rtol=3e-13,
            atol=3e-13,
        )
        np.testing.assert_allclose(coalesced.covariance, coalesced.covariance.T, rtol=0.0, atol=0.0)

    def test_row_oriented_affine_and_complete_relu_blocks(self) -> None:
        weight = np.asarray([[0.4, -0.2], [0.7, 0.3]], dtype=np.float64)
        state = TangentState(
            np.asarray([0.2, -0.5]),
            np.asarray([[0.6, -0.1], [-0.1, -0.4]]),
        )
        jacobian = LocalReluJacobian(
            probability=np.asarray([0.3, 0.8]),
            mean_variance_derivative=np.asarray([0.1, -0.2]),
            price_kernel=np.asarray([[0.3, 0.17], [0.17, 0.8]]),
            h_mu=np.asarray([[0.4, -0.3], [0.2, 0.5]]),
            h_variance=np.asarray([[0.6, 0.1], [-0.2, -0.7]]),
        )

        actual = tangent_stage(state, weight, jacobian)
        affine_mean = state.mean @ weight
        affine_covariance = weight.T @ state.covariance @ weight
        diagonal = np.diag(affine_covariance)
        expected_mean = (
            jacobian.probability * affine_mean
            + jacobian.mean_variance_derivative * diagonal
        )
        expected_covariance = np.empty((2, 2), dtype=np.float64)
        expected_covariance[0, 0] = (
            jacobian.h_mu[0, 0] * affine_mean[0]
            + jacobian.h_variance[0, 0] * diagonal[0]
        )
        expected_covariance[1, 1] = (
            jacobian.h_mu[1, 1] * affine_mean[1]
            + jacobian.h_variance[1, 1] * diagonal[1]
        )
        expected_covariance[0, 1] = expected_covariance[1, 0] = (
            jacobian.price_kernel[0, 1] * affine_covariance[0, 1]
            + jacobian.h_mu[0, 1] * affine_mean[0]
            + jacobian.h_mu[1, 0] * affine_mean[1]
            + jacobian.h_variance[0, 1] * diagonal[0]
            + jacobian.h_variance[1, 0] * diagonal[1]
        )

        np.testing.assert_allclose(actual.mean, expected_mean, rtol=1e-15, atol=1e-15)
        np.testing.assert_allclose(actual.covariance, expected_covariance, rtol=1e-15, atol=1e-15)


if __name__ == "__main__":
    unittest.main()
