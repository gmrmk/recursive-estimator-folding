from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m163_exterior_collision_null import (  # noqa: E402
    TARGET_COMPILER_CAP,
    compile_exterior_star_control,
    exterior_edge_matrix,
    exterior_star_table,
    static_compiler_ledger,
    structural_conservation_check,
)
from m156_extended_domain_star_control import dense_extended_source, source_max_abs_difference  # noqa: E402


class TestM163ExteriorCollisionNull(unittest.TestCase):
    def test_exactly_nulls_iii_iik_and_iji_without_a_label_mask(self) -> None:
        rng = np.random.default_rng(16301)
        width = 6
        base = rng.normal(size=(width, width))
        covariance = base @ base.T + np.eye(width)
        control = exterior_star_table(covariance)
        for i in range(width):
            self.assertTrue(np.all(control[i, i, :] == 0.0))
            self.assertTrue(np.all(control[i, :, i] == 0.0))
            self.assertEqual(control[i, i, i], 0.0)
        self.assertTrue(any(abs(control[i, j, j]) > 0.0 for i in range(width) for j in range(width) if i != j))

    def test_isotropic_and_tied_correlation_case_has_exact_zero_control_fallback(self) -> None:
        covariance = 3.7 * np.eye(5)
        correlation, exterior, edge = exterior_edge_matrix(covariance)
        self.assertTrue(np.array_equal(correlation, np.eye(5)))
        self.assertTrue(np.array_equal(exterior, np.ones((5, 5)) - np.eye(5)))
        self.assertTrue(np.array_equal(edge, np.zeros((5, 5))))
        self.assertTrue(np.array_equal(exterior_star_table(covariance), np.zeros((5, 5, 5))))

    def test_permutation_and_positive_gauge_covariance_of_compiled_source(self) -> None:
        rng = np.random.default_rng(16302)
        width, outputs = 5, 4
        weight = rng.normal(size=(width, outputs))
        factor = rng.normal(size=(width, width))
        covariance = factor @ factor.T + np.eye(width)
        original = compile_exterior_star_control(weight, covariance)
        permutation = rng.permutation(width)
        permuted = compile_exterior_star_control(weight[permutation], covariance[permutation][:, permutation])
        self.assertLess(source_max_abs_difference(original, permuted), 3e-11)
        gauge = np.exp(rng.uniform(-0.4, 0.4, size=width))
        gauged = compile_exterior_star_control(weight / gauge[:, None], gauge[:, None] * covariance * gauge[None, :])
        self.assertLess(source_max_abs_difference(original, gauged), 3e-10)

    def test_full_domain_conservation_against_exhaustive_reference(self) -> None:
        rng = np.random.default_rng(16303)
        width = 5
        weight = rng.normal(size=(width, 4))
        factor = rng.normal(size=(width, width))
        covariance = factor @ factor.T + np.eye(width)
        target = rng.normal(size=(width, width, width))
        target = 0.5 * (target + target.swapaxes(1, 2))
        self.assertLess(structural_conservation_check(weight, target, covariance), 4e-8)

    def test_static_compiler_uses_only_five_products_and_fits_cap(self) -> None:
        ledger = static_compiler_ledger()
        self.assertEqual(ledger["dense_f64_products"], 5)
        self.assertTrue(ledger["no_kronecker_mask_or_khatri_action"])
        self.assertTrue(ledger["fits_cap"])
        self.assertLessEqual(ledger["total_static_compiler_bill"], TARGET_COMPILER_CAP)


if __name__ == "__main__":
    unittest.main()
