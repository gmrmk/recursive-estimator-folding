from __future__ import annotations

import unittest

import numpy as np

from m156_extended_domain_star_control import (
    collision_count,
    collision_strata,
    compiled_extended_star_control,
    dense_extended_source,
    distinct_count,
    distinct_target_extension,
    extended_star_table,
    mixture_probability,
    residual_table,
    source_add,
    source_max_abs_difference,
    static_cost_ledger,
)


class TestM156ExtendedDomainControl(unittest.TestCase):
    def test_five_gemm_compiler_equals_complete_ordered_sum(self) -> None:
        for width in (3, 4, 5):
            rng = np.random.default_rng(15600 + width)
            weight = rng.normal(size=(width, width + 1))
            root = rng.normal(size=(width, width))
            covariance = root @ root.T
            dense = dense_extended_source(weight, extended_star_table(covariance))
            compiled = compiled_extended_star_control(weight, covariance)
            self.assertLess(source_max_abs_difference(dense, compiled), 2e-8)

    def test_extended_control_plus_exact_residual_conserves_distinct_target(self) -> None:
        rng = np.random.default_rng(15621)
        width = 5
        weight = rng.normal(size=(width, 4))
        root = rng.normal(size=(width, width))
        covariance = root @ root.T
        target = rng.normal(size=(width, width, width))
        target = 0.5 * (target + target.swapaxes(1, 2))
        target = distinct_target_extension(target)
        control = extended_star_table(covariance)
        residual = residual_table(target, control)
        expected = dense_extended_source(weight, target)
        actual = source_add(
            compiled_extended_star_control(weight, covariance),
            dense_extended_source(weight, residual),
        )
        self.assertLess(source_max_abs_difference(expected, actual), 3e-8)

    def test_collision_partition_is_disjoint_and_complete(self) -> None:
        for width in (3, 4, 7):
            rows = collision_strata(width)
            self.assertEqual(len(rows), collision_count(width))
            self.assertEqual(len(set(rows)), collision_count(width))
            self.assertTrue(all(len(set(row)) < 3 for row in rows))
            self.assertEqual(collision_count(width) + distinct_count(width), width**3)

    def test_two_stratum_probability_has_full_support_and_unit_mass(self) -> None:
        width = 5
        dcount = distinct_count(width)

        def uniform_distinct(_unit):
            return 1.0 / dcount

        total = 0.0
        for i in range(width):
            for j in range(width):
                for k in range(width):
                    probability = mixture_probability(
                        (i, j, k), width, uniform_distinct
                    )
                    self.assertGreater(probability, 0.0)
                    total += probability
        self.assertAlmostEqual(total, 1.0, places=14)

    def test_label_permutation_and_positive_gauge_covariance(self) -> None:
        rng = np.random.default_rng(15641)
        width = 6
        weight = rng.normal(size=(width, 5))
        root = rng.normal(size=(width, width))
        covariance = root @ root.T
        expected = compiled_extended_star_control(weight, covariance)

        permutation = rng.permutation(width)
        permuted = compiled_extended_star_control(
            weight[permutation], covariance[permutation][:, permutation]
        )
        self.assertLess(source_max_abs_difference(expected, permuted), 2e-8)

        gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
        gauged = compiled_extended_star_control(
            weight / gauge[:, None],
            gauge[:, None] * covariance * gauge[None, :],
        )
        self.assertLess(source_max_abs_difference(expected, gauged), 3e-8)

    def test_collision_target_is_zero_and_residual_is_negative_control(self) -> None:
        rng = np.random.default_rng(15661)
        width = 4
        target = rng.normal(size=(width, width, width))
        target = 0.5 * (target + target.swapaxes(1, 2))
        target = distinct_target_extension(target)
        root = rng.normal(size=(width, width))
        control = extended_star_table(root @ root.T)
        residual = residual_table(target, control)
        for i, j, k in collision_strata(width):
            self.assertEqual(target[i, j, k], 0.0)
            self.assertEqual(residual[i, j, k], -control[i, j, k])

    def test_static_floor_is_narrow_but_below_100b(self) -> None:
        ledger = static_cost_ledger()
        self.assertEqual(ledger["protected_five_products_all_layers"], 12_976_947_200)
        self.assertEqual(ledger["known_total_before_pointwise_wall"], 98_957_826_000)
        self.assertEqual(ledger["remaining_to_100b"], 1_042_174_000)
        self.assertTrue(ledger["arithmetic_floor_below_100b"])


if __name__ == "__main__":
    unittest.main()

