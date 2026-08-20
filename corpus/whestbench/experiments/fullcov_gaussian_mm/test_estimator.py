"""Estimator-level contract tests, written before the scored implementation."""

from __future__ import annotations

import math
import unittest

import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP

from estimator import Estimator


class FullCovEstimatorTests(unittest.TestCase):
    @staticmethod
    def context(width, depth):
        return SetupContext(
            width=width,
            depth=depth,
            flop_budget=1_000_000_000,
            api_version="0.14",
            submission_dir=None,
            seed=0,
        )

    def test_first_layer_mean_is_exact(self):
        weight = np.array(
            [[1.0, -0.5, 0.2], [0.4, 1.1, -0.7], [-0.3, 0.8, 0.9]],
            dtype=np.float32,
        )
        mlp = MLP(
            width=3,
            depth=1,
            weights=[fnp.asarray(weight)],
            seed=1,
            name="one-layer",
        )
        estimator = Estimator()
        estimator.setup(self.context(3, 1))
        got = np.asarray(estimator.predict(mlp, 1_000_000_000))[0]
        expected = np.sqrt(np.sum(weight.astype(np.float64) ** 2, axis=0))
        expected /= math.sqrt(2.0 * math.pi)
        np.testing.assert_allclose(got, expected, rtol=2e-7, atol=2e-8)

    def test_multilayer_prediction_is_finite_and_has_contract_shape(self):
        rng = np.random.default_rng(17)
        weights = [
            fnp.asarray(rng.normal(scale=0.4, size=(4, 4)), dtype=fnp.float32)
            for _ in range(3)
        ]
        mlp = MLP(width=4, depth=3, weights=weights, seed=2, name="tiny")
        estimator = Estimator()
        estimator.setup(self.context(4, 3))
        got = np.asarray(estimator.predict(mlp, 1_000_000_000))
        self.assertEqual(got.shape, (3, 4))
        self.assertTrue(np.all(np.isfinite(got)))
        self.assertTrue(np.all(got >= 0.0))


if __name__ == "__main__":
    unittest.main()
