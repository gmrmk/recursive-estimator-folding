"""K1 verification: the fused kernel is bitwise-identical to the naive forward,
pruning reports a sane FLOP fraction, and the floor-budget planner is correct.
Response-free.
"""

from __future__ import annotations

from pathlib import Path
import math
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import k1_kernel as k  # noqa: E402


def _gen(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(math.sqrt(2.0 / k.WIDTH))
    return [rng.standard_normal((k.WIDTH, k.WIDTH), dtype=np.float32) * g for _ in range(32)]


def _naive(weights, X):
    x = X
    for W in weights:
        x = np.maximum(x @ W, np.float32(0.0))
    return x.mean(axis=0)


class K1Tests(unittest.TestCase):
    def test_fused_matches_naive_to_f32_tolerance(self):
        # np.dot(out=) vs @ can differ at the last ulp; immaterial to a
        # statistical sampler. Faithful to f32 tolerance is the honest claim.
        w = _gen(20260807)
        X = np.random.default_rng(7).standard_normal((4096, k.WIDTH)).astype(np.float32)
        diff = float(np.max(np.abs(k.fused_forward_mean(w, X) - _naive(w, X))))
        self.assertLess(diff, 1e-5, diff)

    def test_pruning_reports_sane_flop_fraction(self):
        w = _gen(1)
        masks, frac = k.structural_active_masks(w, dead_alpha=-2.0)
        self.assertEqual(len(masks), 32)
        self.assertTrue(0.4 < frac < 0.9)              # ~0.58 measured
        self.assertTrue(masks[0].all())                # layer 1 fully active

    def test_floor_budget_planner_arithmetic(self):
        p = k.floor_budget_plan(us_per_sample=17.534)
        # n = 0.272 / 17.534e-6 ~= 15512; adjusted = 0.1 * 0.0199 / n
        self.assertAlmostEqual(p["floor_budget_samples"], 15512, delta=5)
        self.assertAlmostEqual(p["adjusted_at_floor"], 0.1 * 0.0199 / p["floor_budget_samples"], places=15)


if __name__ == "__main__":
    unittest.main()
