"""Generated-array premise tests for M166; no response or score is used."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in ("m166_oriented_collision_null", "m156_extended_domain_star_control"):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from m156_extended_domain_star_control import (  # noqa: E402
    dense_extended_source,
    distinct_target_extension,
    source_add,
    source_max_abs_difference,
)
from m166_oriented_collision_null import (  # noqa: E402
    TARGET_COMPILER_CAP,
    compile_oriented_star_control,
    f32_shared_control_report,
    orient_covariance_edges,
    oriented_star_table,
    residual_table_from_control,
    static_cost_ledger,
)


def positive_covariance(rng: np.random.Generator, width: int) -> np.ndarray:
    factor = rng.normal(size=(width, width))
    return factor @ factor.T + np.eye(width)


class TestM166OrientedCollisionNull(unittest.TestCase):
    def test_all_four_collision_patterns_are_exact_zero_without_collision_mask(self) -> None:
        rng = np.random.default_rng(16601)
        control = orient_covariance_edges(positive_covariance(rng, 6))
        table = oriented_star_table(control)
        for i in range(6):
            self.assertTrue(np.all(table[i, i, :] == 0.0))  # iii and iik
            self.assertTrue(np.all(table[i, :, i] == 0.0))  # iji
            self.assertTrue(np.all(table[:, i, i] == 0.0))  # ijj

    def test_score_ties_are_certified_to_zero_not_oriented_by_index(self) -> None:
        width = 6
        covariance = 0.2 * np.ones((width, width)) + 0.8 * np.eye(width)
        control = orient_covariance_edges(covariance)
        self.assertTrue(np.array_equal(control.a, np.zeros((width, width))))
        self.assertTrue(np.array_equal(control.b, np.zeros((width, width))))
        self.assertEqual(control.tied_pair_count, width * (width - 1) // 2)

    def test_exact_seven_product_compiler_matches_exhaustive_full_domain_source(self) -> None:
        rng = np.random.default_rng(16602)
        weight = rng.normal(size=(5, 4))
        control = orient_covariance_edges(positive_covariance(rng, 5))
        direct = dense_extended_source(weight, oriented_star_table(control))
        compiled = compile_oriented_star_control(weight, control)
        self.assertLess(source_max_abs_difference(direct, compiled), 4e-10)

    def test_permutation_and_positive_gauge_covariance_hold_in_f64_reference(self) -> None:
        rng = np.random.default_rng(16603)
        width, outputs = 6, 4
        weight = rng.normal(size=(width, outputs))
        covariance = positive_covariance(rng, width)
        original = compile_oriented_star_control(weight, orient_covariance_edges(covariance))

        permutation = rng.permutation(width)
        permuted = compile_oriented_star_control(
            weight[permutation],
            orient_covariance_edges(covariance[permutation][:, permutation]),
        )
        self.assertLess(source_max_abs_difference(original, permuted), 5e-10)

        gauge = np.exp(rng.uniform(-0.3, 0.3, size=width))
        gauged = compile_oriented_star_control(
            weight / gauge[:, None],
            orient_covariance_edges(gauge[:, None] * covariance * gauge[None, :]),
        )
        self.assertLess(source_max_abs_difference(original, gauged), 2e-9)

    def test_same_control_object_reconstructs_full_domain_target(self) -> None:
        rng = np.random.default_rng(16604)
        width = 5
        weight = rng.normal(size=(width, 4))
        covariance = positive_covariance(rng, width)
        target = rng.normal(size=(width, width, width))
        target = 0.5 * (target + target.swapaxes(1, 2))
        control = orient_covariance_edges(covariance)
        residual = residual_table_from_control(distinct_target_extension(target), control)
        reconstructed = source_add(
            compile_oriented_star_control(weight, control),
            dense_extended_source(weight, residual),
        )
        direct = dense_extended_source(weight, distinct_target_extension(target))
        self.assertLess(source_max_abs_difference(reconstructed, direct), 5e-10)

    def test_f32_report_uses_one_stored_control_for_both_arms_and_reports_roundoff(self) -> None:
        rng = np.random.default_rng(16605)
        width = 5
        covariance = positive_covariance(rng, width).astype(np.float32)
        target = rng.normal(size=(width, width, width)).astype(np.float32)
        target = np.float32(0.5) * (target + target.swapaxes(1, 2))
        report = f32_shared_control_report(target, covariance)
        self.assertTrue(report["same_control_object_used_by_both_arms"])
        self.assertLess(report["coefficient_reconstruction_max_abs"], 3e-6)
        self.assertFalse(report["bitwise_coefficient_reconstruction"])

    def test_cost_ledger_counts_orientation_correlation_and_copies(self) -> None:
        ledger = static_cost_ledger()
        self.assertEqual(ledger["exact_f64_dense_products"], 7)
        self.assertFalse(ledger["exact_f64_fits_cap"])
        self.assertEqual(ledger["f32_dense_products"], 7)
        self.assertGreater(ledger["f32_orientation_correlation_copy_allowance"], 0)
        self.assertTrue(ledger["f32_static_fits_cap"])
        self.assertLessEqual(ledger["f32_static_total"], TARGET_COMPILER_CAP)


if __name__ == "__main__":
    unittest.main()
