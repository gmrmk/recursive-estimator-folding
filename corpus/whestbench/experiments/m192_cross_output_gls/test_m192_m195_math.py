"""Unit checks for the M192--M195 covariance algebra and frozen results."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_m192_g0 as m192  # noqa: E402
import run_m194_g0 as m194  # noqa: E402
import run_m195_g0 as m195  # noqa: E402


class CovarianceAttenuationMathTests(unittest.TestCase):
    def test_m192_gls_weights_satisfy_kkt_and_sum_one(self) -> None:
        rng = np.random.default_rng(192001)
        factor = rng.normal(size=(126, 40))
        covariance = factor @ factor.T + 0.2 * np.eye(126)
        weights, diagnostics = m192._weights(covariance, 0.25)
        tau = np.trace(covariance) / 126
        shrunk = 0.75 * covariance + 0.25 * tau * np.eye(126)
        gradient = shrunk @ weights
        self.assertAlmostEqual(float(weights.sum()), 1.0, places=12)
        self.assertLess(np.std(gradient), 1e-10)
        self.assertIsNone(diagnostics["fallback"])

    def test_m194_solver_equals_direct_contrast_subspace_solution(self) -> None:
        rng = np.random.default_rng(194001)
        frames = rng.normal(size=(126, 224))
        anchor = rng.normal(size=224)
        train = np.arange(224)
        weights, diagnostics = m194._block_weights(frames, anchor, train)

        residual = frames - anchor[None, :]
        common = residual.mean(axis=0)
        contrast = residual - common[None, :]
        block = contrast @ contrast.T / len(train)
        cross = contrast @ common / len(train)
        cross -= cross.mean()
        tau = np.trace(block) / 125
        projector = np.eye(126) - np.ones((126, 126)) / 126
        values, vectors = np.linalg.eigh(projector)
        helmert = vectors[:, values > 0.5]
        reduced = helmert.T @ block @ helmert
        rhs = helmert.T @ cross
        correction = -helmert @ np.linalg.solve(
            reduced + (tau / 3.0) * np.eye(125), rhs
        )
        reference = np.full(126, 1.0 / 126) + correction
        np.testing.assert_allclose(weights, reference, rtol=2e-11, atol=2e-11)
        self.assertIsNone(diagnostics["fallback"])

    def test_m194_common_pilot_noise_cancels_only_when_cross_is_zero(self) -> None:
        rng = np.random.default_rng(194002)
        frames = rng.normal(size=(126, 256))
        truth = rng.normal(size=256)
        train = np.arange(224)
        base, _ = m194._block_weights(frames, truth, train)

        residual = frames[:, train] - truth[train][None, :]
        contrast = residual - residual.mean(axis=0, keepdims=True)
        # A right-null vector makes the empirical z*eta cross exactly zero.
        _, _, right = np.linalg.svd(contrast, full_matrices=True)
        eta_null = right[-1]
        anchor_null = truth.copy()
        anchor_null[train] += eta_null
        null_weight, _ = m194._block_weights(frames, anchor_null, train)
        np.testing.assert_allclose(base, null_weight, rtol=2e-10, atol=2e-10)

        anchor_generic = truth.copy()
        anchor_generic[train] += rng.normal(size=len(train))
        generic_weight, _ = m194._block_weights(frames, anchor_generic, train)
        self.assertGreater(float(np.linalg.norm(base - generic_weight)), 1e-3)

    def test_m195_each_group_correction_has_zero_sum(self) -> None:
        rng = np.random.default_rng(195001)
        group = rng.normal(size=(63, 256))
        difference = rng.normal(size=256)
        correction, diagnostics = m195._contrast_correction(
            group, difference, np.arange(224), +1.0
        )
        self.assertAlmostEqual(float(correction.sum()), 0.0, places=12)
        self.assertIsNone(diagnostics["fallback"])

    def test_frozen_dispositions_match_written_results(self) -> None:
        expected = {
            "m192_g0_results.json": ("SCREEN_SURVIVOR", 0.126193, "panel_ratio_geomean"),
            "m193_g0_results.json": ("KILLED", 1057.899, "panel_ratio_geomean"),
            "m194_g0_results.json": ("KILLED", 15.8306, "panel_raw_ratio_geomean"),
            "m195_g0_results.json": ("KILLED", 1.15748, "panel_ratio_geomean"),
        }
        for filename, (verdict, approximate, key) in expected.items():
            payload = json.loads((HERE / filename).read_text(encoding="utf-8"))
            self.assertEqual(payload["verdict"], verdict)
            self.assertAlmostEqual(float(payload[key]), approximate, places=3)


if __name__ == "__main__":
    unittest.main()
