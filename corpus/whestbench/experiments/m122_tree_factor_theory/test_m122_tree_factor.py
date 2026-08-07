"""Algebraic checks for M122.  All inputs are generated inside this file."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

from m122_tree_factor import (
    PATHS4,
    all_path_pair_widths,
    crossed_middle_gram_dense,
    crossed_middle_gram_formula,
    crossed_middle_matvec_formula,
    four_core_from_paths,
    mode1_gram,
    standardized_physical_factor,
    tree3_mode1_gram_formula,
    tree3_tensor,
    tree4_tensor,
)

M85_DIR = Path(__file__).resolve().parents[1] / "m85_deterministic_signed_source"
sys.path.insert(0, str(M85_DIR))
from m85_source import GAMMA2, bridge_source, rectified_covariance  # noqa: E402


def generated_bridge(n: int, seed: int) -> np.ndarray:
    """A nondegenerate symmetric generated bridge-like matrix, no contest data."""
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(n, n)) / math.sqrt(n)
    raw = w @ w.T
    scale = np.sqrt(np.diag(raw))
    rho = raw / np.outer(scale, scale)
    # A smooth signed function with Q_ii=1.  This is only a generated algebra
    # probe; it intentionally does not import M85 or a scorer.
    q = np.tanh(0.8 * rho)
    np.fill_diagonal(q, 1.0)
    return q


class M122TreeFactorAlgebraTests(unittest.TestCase):
    def test_path_count(self) -> None:
        self.assertEqual(len(PATHS4), 12)
        self.assertEqual(len(set(PATHS4)), 12)

    def test_tree3_mode_gram_formula_n2_to_n8(self) -> None:
        worst = 0.0
        for n in range(2, 9):
            q = generated_bridge(n, 122000 + n)
            expected = mode1_gram(tree3_tensor(q))
            actual = tree3_mode1_gram_formula(q)
            worst = max(worst, float(np.max(np.abs(expected - actual))))
        self.assertLessEqual(worst, 1e-10)

    def test_crossed_middle_formula_and_matvec_n2_to_n8(self) -> None:
        worst_gram = 0.0
        worst_mv = 0.0
        for n in range(2, 9):
            q = generated_bridge(n, 122100 + n)
            dense = crossed_middle_gram_dense(q)
            formula = crossed_middle_gram_formula(q)
            x = np.random.default_rng(122200 + n).normal(size=n)
            worst_gram = max(worst_gram, float(np.max(np.abs(dense - formula))))
            worst_mv = max(worst_mv, float(np.max(np.abs(dense @ x - crossed_middle_matvec_formula(q, x)))))
        self.assertLessEqual(worst_gram, 1e-10)
        self.assertLessEqual(worst_mv, 1e-10)

    def test_all_path_pair_matvec_graphs_have_width_two(self) -> None:
        widths = all_path_pair_widths()
        self.assertEqual(widths["count"], 144)
        self.assertLessEqual(widths["max"], 2)
        self.assertGreaterEqual(widths["min"], 1)

    def test_path_core_equals_dense_projection_n2_to_n8(self) -> None:
        worst = 0.0
        for n in range(2, 9):
            q = generated_bridge(n, 122300 + n)
            r = min(3, n)
            u = np.random.default_rng(122400 + n).normal(size=(n, r))
            dense = np.einsum("ijkl,ip,jq,kr,ls->pqrs", tree4_tensor(q), u, u, u, u, optimize=True)
            path = four_core_from_paths(q, u)
            worst = max(worst, float(np.max(np.abs(dense - path))))
        self.assertLessEqual(worst, 1e-10)

    def test_standardized_factor_positive_gauge_identity(self) -> None:
        rng = np.random.default_rng(122500)
        u = rng.normal(size=(8, 4))
        scale = rng.uniform(0.1, 2.0, size=8)
        gauge = rng.uniform(0.2, 3.0, size=8)
        left = standardized_physical_factor(u, gauge * scale)
        right = gauge[:, None] * standardized_physical_factor(u, scale)
        self.assertLessEqual(float(np.max(np.abs(left - right))), 1e-12)

    def test_m85_repeated_index_correction_is_sparse_and_exact_for_k3(self) -> None:
        """M85's special one/two-coordinate entries do not change O(n^3) status."""
        worst = 0.0
        for n in range(2, 7):
            rng = np.random.default_rng(122900 + n)
            w = rng.normal(size=(n, n)) / math.sqrt(n)
            covariance = w @ w.T
            _, rect_cov, q = rectified_covariance(covariance)
            scale = np.sqrt(np.diag(rect_cov))
            actual = bridge_source(covariance, 3)
            normalizer = np.einsum("i,j,k->ijk", scale, scale, scale)
            standard = actual / normalizer
            base = GAMMA2 * tree3_tensor(q)
            delta = standard - base
            # The source differs only for <=2 distinct coordinate labels.
            for index in np.ndindex((n,) * 3):
                if len(set(index)) >= 3:
                    self.assertLessEqual(abs(delta[index]), 2e-12)
            b = base.reshape(n, -1)
            d = delta.reshape(n, -1)
            reconstructed = GAMMA2 * GAMMA2 * tree3_mode1_gram_formula(q) + b @ d.T + d @ b.T + d @ d.T
            worst = max(worst, float(np.max(np.abs(reconstructed - mode1_gram(standard)))))
        self.assertLessEqual(worst, 1e-10)

    def test_m85_repeated_index_correction_is_sparse_and_exact_for_k4_core(self) -> None:
        """The rank-r core needs only a sparse two-coordinate addendum."""
        worst = 0.0
        for n in range(2, 7):
            rng = np.random.default_rng(123000 + n)
            w = rng.normal(size=(n, n)) / math.sqrt(n)
            covariance = w @ w.T
            _, rect_cov, q = rectified_covariance(covariance)
            scale = np.sqrt(np.diag(rect_cov))
            actual = bridge_source(covariance, 4)
            normalizer = np.einsum("i,j,k,l->ijkl", scale, scale, scale, scale)
            standard = actual / normalizer
            base = GAMMA2 * GAMMA2 * tree4_tensor(q)
            delta = standard - base
            for index in np.ndindex((n,) * 4):
                if len(set(index)) >= 3:
                    self.assertLessEqual(abs(delta[index]), 2e-12)
            r = min(3, n)
            u = np.random.default_rng(123100 + n).normal(size=(n, r))
            full_core = np.einsum("ijkl,ip,jq,kr,ls->pqrs", standard, u, u, u, u, optimize=True)
            repaired_core = (
                GAMMA2 * GAMMA2 * four_core_from_paths(q, u)
                + np.einsum("ijkl,ip,jq,kr,ls->pqrs", delta, u, u, u, u, optimize=True)
            )
            worst = max(worst, float(np.max(np.abs(full_core - repaired_core))))
        self.assertLessEqual(worst, 1e-10)


if __name__ == "__main__":
    unittest.main()
