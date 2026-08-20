from __future__ import annotations

import itertools
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from m130_direct_aabc_collision import (
    QUADRATIC_JET_COEFFICIENT,
    aabb_quadratic_jet_reference,
    aabb_quadratic_jet_probe_sample,
    aabb_quadratic_jet_split,
    aaab_quadratic_jet_exact,
    aaab_quadratic_jet_physical,
    defect211_quadratic_jet,
    flopscope_aabc_ledger,
)

M126 = HERE.parent / "m126_repeated_output_source_contraction"
sys.path.insert(0, str(M126))
from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402


def bridge(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = rng.normal(scale=0.11, size=(n, n))
    q = (x + x.T) / 2.0
    np.fill_diagonal(q, 1.0)
    return q


class M130DirectAabcTests(unittest.TestCase):
    def test_aaab_formula_matches_twelve_slot_oracle(self) -> None:
        worst = 0.0
        for n in range(3, 8):
            q = bridge(n, 130100 + n)
            w = np.random.default_rng(130200 + n).normal(size=(n, n - 1))
            expected = collision211_repeated_exact(defect211_quadratic_jet(q), w)["k4_aaab"]
            observed = aaab_quadratic_jet_exact(q, w)
            worst = max(worst, float(np.max(np.abs(expected - observed))))
        self.assertLessEqual(worst, 3e-11)

    def test_repeated_pair_split_matches_its_explicit_slots(self) -> None:
        n = 6
        q = bridge(n, 130301)
        w = np.random.default_rng(130302).normal(size=(n, 4))
        defect = defect211_quadratic_jet(q)
        expected = np.zeros((4, 4))
        for i in range(n):
            for j, k in itertools.combinations([z for z in range(n) if z != i], 2):
                f = defect[i, j, k]
                expected += 2.0 * (
                    np.outer(w[i] ** 2, w[j] * w[k])
                    + np.outer(w[j] * w[k], w[i] ** 2)
                ) * f
        observed = aabb_quadratic_jet_split(q, w)["repeated_pair_exact"]
        self.assertLessEqual(float(np.max(np.abs(expected - observed))), 3e-11)

    def test_full_aabb_reference_equals_twelve_slot_oracle(self) -> None:
        n, outputs = 5, 3
        q = bridge(n, 130401)
        w = np.random.default_rng(130402).normal(size=(n, outputs))
        expected = collision211_repeated_exact(defect211_quadratic_jet(q), w)["k4_aabb"]
        observed = aabb_quadratic_jet_reference(q, w)
        self.assertLessEqual(float(np.max(np.abs(expected - observed))), 3e-11)

    def test_complete_rademacher_average_recovers_full_aabb(self) -> None:
        n, outputs = 4, 3
        q = bridge(n, 130451)
        w = np.random.default_rng(130452).normal(size=(n, outputs))
        expected = aabb_quadratic_jet_reference(q, w)
        observed = sum(
            aabb_quadratic_jet_probe_sample(q, w, np.asarray(signs))
            for signs in itertools.product((-1.0, 1.0), repeat=n)
        ) / (2**n)
        self.assertLessEqual(float(np.max(np.abs(expected - observed))), 4e-11)

    def test_permutation_and_positive_gauge_covariance(self) -> None:
        n = 6
        q = bridge(n, 130501)
        w = np.random.default_rng(130502).normal(size=(n, 4))
        base = aaab_quadratic_jet_exact(q, w)
        p = np.random.default_rng(130503).permutation(n)
        self.assertLessEqual(
            float(np.max(np.abs(base - aaab_quadratic_jet_exact(q[np.ix_(p, p)], w[p])))),
            3e-11,
        )
        scale = np.exp(np.random.default_rng(130504).normal(size=n))
        physical = aaab_quadratic_jet_physical(q, scale, w)
        gauge = np.exp(np.random.default_rng(130505).normal(size=n))
        gauged = aaab_quadratic_jet_physical(q, scale * gauge, w / gauge[:, None])
        self.assertLessEqual(float(np.max(np.abs(physical - gauged))), 3e-11)

    def test_jet_and_cost_constants(self) -> None:
        self.assertAlmostEqual(QUADRATIC_JET_COEFFICIENT, 1.0 / (4.0 * np.pi))
        f64 = flopscope_aabc_ledger(probes=2)
        f32 = flopscope_aabc_ledger(dtype="float32", probes=2)
        self.assertEqual(f64["square_call_bill"], 66_977_792)
        self.assertEqual(f32["square_call_bill"], 33_488_896)
        self.assertEqual(f64["exact_square_calls_per_layer"], 15)
        self.assertEqual(f64["aabb_hard_square_calls_per_probe"], 8)
        self.assertGreater(f64["effective_flops"], f32["effective_flops"])


if __name__ == "__main__":
    unittest.main()
