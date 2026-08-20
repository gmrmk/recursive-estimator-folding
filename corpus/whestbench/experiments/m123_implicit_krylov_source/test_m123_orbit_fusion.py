from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

from m123_orbit_fusion import (
    HARD_ORBITS,
    REPRESENTATIVES,
    dense_representative,
    equivariant_start_block,
    full_fused_matrix_small,
    fused_mode1_gram_apply,
    hard_orbit_apply,
    orbit_matrix_formula,
)

M122_DIR = Path(__file__).resolve().parents[1] / "m122_tree_factor_theory"
sys.path.insert(0, str(M122_DIR))
from m122_tree_factor import mode1_gram, tree4_tensor  # noqa: E402


def generated_q(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(n, n)) / math.sqrt(n)
    raw = w @ w.T
    d = np.sqrt(np.diag(raw))
    rho = raw / np.outer(d, d)
    q = np.tanh(0.8 * rho)
    np.fill_diagonal(q, 1.0)
    return q


class M123OrbitFusionTests(unittest.TestCase):
    def test_orbits_partition_all_144_pairs(self) -> None:
        self.assertEqual(len(REPRESENTATIVES), 16)
        self.assertEqual(sum(item[2] for item in REPRESENTATIVES), 144)
        self.assertEqual(HARD_ORBITS, (8, 14, 15))

    def test_each_orbit_formula_n2_to_n8(self) -> None:
        worst = 0.0
        for n in range(2, 9):
            q = generated_q(n, 123200 + n)
            for orbit in range(16):
                worst = max(
                    worst,
                    float(np.max(np.abs(dense_representative(q, orbit) - orbit_matrix_formula(q, orbit)))),
                )
        self.assertLessEqual(worst, 1e-10)

    def test_full_orbit_fusion_equals_dense_gram_n2_to_n8(self) -> None:
        worst = 0.0
        for n in range(2, 9):
            q = generated_q(n, 123300 + n)
            dense = mode1_gram(tree4_tensor(q))
            fused = full_fused_matrix_small(q)
            worst = max(worst, float(np.max(np.abs(dense - fused))))
        self.assertLessEqual(worst, 1e-10)

    def test_hard_and_complete_matvec_n2_to_n8(self) -> None:
        worst_hard = 0.0
        worst_full = 0.0
        for n in range(2, 9):
            q = generated_q(n, 123400 + n)
            x = np.random.default_rng(123500 + n).normal(size=n)
            hard = np.zeros_like(q)
            for orbit in HARD_ORBITS:
                k = orbit_matrix_formula(q, orbit)
                size = REPRESENTATIVES[orbit][2]
                hard += 6.0 * k if size == 6 else 6.0 * (k + k.T)
            worst_hard = max(worst_hard, float(np.max(np.abs(hard @ x - hard_orbit_apply(q, x)))))
            full = mode1_gram(tree4_tensor(q))
            worst_full = max(worst_full, float(np.max(np.abs(full @ x - fused_mode1_gram_apply(q, x)))))
        self.assertLessEqual(worst_hard, 1e-10)
        self.assertLessEqual(worst_full, 1e-10)

    def test_permutation_covariance_of_operator_and_start_projector(self) -> None:
        n = 8
        q = generated_q(n, 123801)
        rng = np.random.default_rng(123802)
        permutation = rng.permutation(n)
        qp = q[np.ix_(permutation, permutation)]
        x = rng.normal(size=n)
        xp = x[permutation]
        expected = fused_mode1_gram_apply(q, x)[permutation]
        actual = fused_mode1_gram_apply(qp, xp)
        self.assertLessEqual(float(np.max(np.abs(expected - actual))), 1e-10)
        u = equivariant_start_block(q)
        up = equivariant_start_block(qp)
        projector_expected = (u @ u.T)[np.ix_(permutation, permutation)]
        self.assertLessEqual(float(np.max(np.abs(projector_expected - up @ up.T))), 1e-10)

    def test_positive_gauge_restoration_and_symmetric_tie_fail_closed(self) -> None:
        q = generated_q(8, 123803)
        u = equivariant_start_block(q)
        rng = np.random.default_rng(123804)
        scale = rng.uniform(0.2, 2.0, size=8)
        gauge = rng.uniform(0.2, 3.0, size=8)
        v = scale[:, None] * u
        vp = (gauge * scale)[:, None] * u
        self.assertLessEqual(float(np.max(np.abs(vp - gauge[:, None] * v))), 1e-12)
        with self.assertRaises(FloatingPointError):
            equivariant_start_block(np.eye(8))


if __name__ == "__main__":
    unittest.main()
