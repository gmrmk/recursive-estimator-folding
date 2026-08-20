"""Exhaustive generated-only ownership/conservation tests for M172."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m172_selective_22_owner_fusion",
    "m156_extended_domain_star_control",
    "m163_exterior_collision_null",
    "m167_collision_owner_unification",
):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from m156_extended_domain_star_control import source_add, source_max_abs_difference  # noqa: E402
from m167_collision_owner_unification import PhysicalFourthOwners, complete_source_reference  # noqa: E402
from m172_selective_22_owner_fusion import (  # noqa: E402
    COLLISION_MASS,
    CONFIRMATION_CELLS,
    DEVELOPMENT_CELLS,
    complete_selective_source,
    gauged_inputs,
    independent_22_tensor_source,
    intentionally_bad_rezeroed_residual,
    m163_control_source,
    m163_ijj_formula,
    m163_selective_22_conservation_error,
    old_separate_22_source,
    old_separate_source,
    permuted_inputs,
    retired_22_source,
    selective_22_complete_target,
    selective_22_residual,
    static_owner_fusion_ledger,
)


def generated_owners(rng: np.random.Generator, width: int) -> PhysicalFourthOwners:
    k4 = rng.normal(size=width)
    k31 = rng.normal(size=(width, width))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(size=(width, width))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    return PhysicalFourthOwners(k4, k31, k22)


def generated_distinct(rng: np.random.Generator, width: int) -> np.ndarray:
    value = rng.normal(size=(width, width, width))
    return 0.5 * (value + value.swapaxes(1, 2))


def generated_spd(rng: np.random.Generator, width: int) -> np.ndarray:
    root = rng.normal(size=(width, width))
    return root @ root.T + np.eye(width)


class TestM172Selective22OwnerFusion(unittest.TestCase):
    def test_exhaustive_width2_to7_22_complete_rows_match_independent_symmetric_tensor(self) -> None:
        rng = np.random.default_rng(17201)
        for width in range(2, 8):
            owners = generated_owners(rng, width)
            weight = rng.normal(size=(width, width + 1))
            target = selective_22_complete_target(np.zeros((width, width, width)), owners)
            table_source = complete_source_reference(weight, target)
            tensor_source = independent_22_tensor_source(weight, owners)
            separate_source = old_separate_22_source(weight, owners)
            self.assertLess(source_max_abs_difference(table_source, tensor_source), 3e-10)
            self.assertLess(source_max_abs_difference(table_source, separate_source), 3e-10)

    def test_exhaustive_width2_to7_m163_complete_domain_conservation(self) -> None:
        rng = np.random.default_rng(17202)
        for width in range(2, 8):
            owners = generated_owners(rng, width)
            distinct = generated_distinct(rng, width)
            weight = rng.normal(size=(width, width + 2))
            covariance = generated_spd(rng, width)
            self.assertLess(
                m163_selective_22_conservation_error(weight, distinct, owners, covariance),
                3e-10,
            )

    def test_ijj_formula_and_zero_rows_are_exact_for_width2_to7(self) -> None:
        rng = np.random.default_rng(17203)
        for width in range(2, 8):
            owners = generated_owners(rng, width)
            distinct = generated_distinct(rng, width)
            covariance = generated_spd(rng, width)
            target, control, residual = selective_22_residual(distinct, owners, covariance)
            edge, expected_control_ijj = m163_ijj_formula(covariance)
            for i in range(width):
                self.assertEqual(target[i, i, i], 0.0)
                self.assertEqual(control[i, i, i], 0.0)
                self.assertEqual(residual[i, i, i], 0.0)
                for j in range(width):
                    if i == j:
                        continue
                    self.assertEqual(target[i, i, j], 0.0)
                    self.assertEqual(target[i, j, i], 0.0)
                    self.assertEqual(control[i, i, j], 0.0)
                    self.assertEqual(control[i, j, i], 0.0)
                    self.assertEqual(residual[i, i, j], 0.0)
                    self.assertEqual(residual[i, j, i], 0.0)
                    self.assertEqual(target[i, j, j], owners.k22[i, j] / 2.0)
                    self.assertEqual(control[i, j, j], expected_control_ijj[i, j])
                    self.assertEqual(
                        residual[i, j, j], owners.k22[i, j] / 2.0 - expected_control_ijj[i, j]
                    )
                    self.assertEqual(expected_control_ijj[i, j], -2.0 * edge[i, j] ** 2)

    def test_exhaustive_width2_to7_permutation_and_positive_gauge_covariance(self) -> None:
        rng = np.random.default_rng(17204)
        for width in range(2, 8):
            owners = generated_owners(rng, width)
            distinct = generated_distinct(rng, width)
            weight = rng.normal(size=(width, width + 1))
            covariance = generated_spd(rng, width)
            original = complete_selective_source(weight, distinct, owners)
            original_m163 = source_add(
                m163_control_source(weight, covariance),
                complete_source_reference(weight, selective_22_residual(distinct, owners, covariance)[2]),
            )

            permutation = rng.permutation(width)
            p_distinct, p_owners = permuted_inputs(distinct, owners, permutation)
            permuted = complete_selective_source(weight[permutation], p_distinct, p_owners)
            permuted_m163 = source_add(
                m163_control_source(weight[permutation], covariance[np.ix_(permutation, permutation)]),
                complete_source_reference(
                    weight[permutation],
                    selective_22_residual(p_distinct, p_owners, covariance[np.ix_(permutation, permutation)])[2],
                ),
            )
            self.assertLess(source_max_abs_difference(original, permuted), 3e-9)
            self.assertLess(source_max_abs_difference(original_m163, permuted_m163), 3e-9)

            gauge = np.exp(rng.uniform(-0.4, 0.4, size=width))
            g_distinct, g_owners = gauged_inputs(distinct, owners, gauge)
            g_weight = weight / gauge[:, None]
            g_covariance = gauge[:, None] * covariance * gauge[None, :]
            gauged = complete_selective_source(g_weight, g_distinct, g_owners)
            gauged_m163 = source_add(
                m163_control_source(g_weight, g_covariance),
                complete_source_reference(
                    g_weight, selective_22_residual(g_distinct, g_owners, g_covariance)[2]
                ),
            )
            self.assertLess(source_max_abs_difference(original, gauged), 4e-9)
            self.assertLess(source_max_abs_difference(original_m163, gauged_m163), 4e-9)

    def test_exhaustive_width2_to7_exact_22_retirement_and_double_count_detector(self) -> None:
        rng = np.random.default_rng(17205)
        for width in range(2, 8):
            owners = generated_owners(rng, width)
            distinct = generated_distinct(rng, width)
            weight = rng.normal(size=(width, width + 2))
            expected = old_separate_source(weight, distinct, owners)
            transferred = complete_selective_source(weight, distinct, owners)
            self.assertLess(source_max_abs_difference(transferred, expected), 5e-10)
            retired = retired_22_source(weight, owners)
            self.assertLess(np.max(np.abs(retired.aaab)), 1e-15)
            double_counted = source_add(transferred, old_separate_22_source(weight, owners))
            self.assertGreater(source_max_abs_difference(double_counted, expected), 1e-6)

    def test_exhaustive_width2_to7_rezeroing_is_detected_as_a_hard_failure(self) -> None:
        rng = np.random.default_rng(17206)
        for width in range(2, 8):
            owners = generated_owners(rng, width)
            distinct = generated_distinct(rng, width)
            weight = rng.normal(size=(width, width + 1))
            covariance = generated_spd(rng, width)
            target, control, good = selective_22_residual(distinct, owners, covariance)
            bad = intentionally_bad_rezeroed_residual(distinct, owners, covariance)
            for i in range(width):
                for j in range(width):
                    if i != j:
                        self.assertEqual(bad[i, j, j], -control[i, j, j])
                        self.assertNotEqual(good[i, j, j], bad[i, j, j])
            expected = complete_source_reference(weight, target)
            good_source = source_add(m163_control_source(weight, covariance), complete_source_reference(weight, good))
            bad_source = source_add(m163_control_source(weight, covariance), complete_source_reference(weight, bad))
            self.assertLess(source_max_abs_difference(expected, good_source), 3e-10)
            self.assertGreater(source_max_abs_difference(expected, bad_source), 1e-6)
            self.assertTrue(np.any(control != 0.0))

    def test_static_delta_is_inclusive_and_does_not_claim_a_free_k22_transport(self) -> None:
        ledger = static_owner_fusion_ledger()
        self.assertEqual(ledger["collision_mass_eta"], COLLISION_MASS)
        self.assertEqual(ledger["nonzero_ordered_ijj_representatives"], 256 * 255)
        self.assertEqual(ledger["physical_unordered_22_units"], 256 * 255 // 2)
        self.assertEqual(ledger["compiler"]["m163_dense_calls_over_layers_unchanged"], 5 * 31)
        self.assertEqual(ledger["physical_22_provider_per_accepted_event"]["old_separate_owner_probe_dense_calls_retired"], 2)
        self.assertEqual(ledger["physical_22_provider_per_accepted_event"]["new_residual_k22_provider_dense_calls"], 2)
        self.assertEqual(ledger["physical_22_provider_per_accepted_event"]["net_dense_calls"], 0)
        self.assertEqual(ledger["new_eventwise_f64_operations_per_accepted_event"]["total"], 5)
        self.assertEqual(ledger["call_delta"]["net_dense_call_credit_claimed"], 0)

    def test_development_and_confirmation_seeds_are_exactly_frozen(self) -> None:
        self.assertEqual(
            DEVELOPMENT_CELLS,
            (("iso_w5", 5, 1720501, 0.22), ("factor_w5", 5, 1720502, 0.50),
             ("iso_w6", 6, 1720601, 0.22), ("factor_w6", 6, 1720602, 0.50),
             ("iso_w7", 7, 1720701, 0.22), ("factor_w7", 7, 1720702, 0.50)),
        )
        self.assertEqual(
            CONFIRMATION_CELLS,
            (("iso_w5c", 5, 1721501, 0.22), ("factor_w5c", 5, 1721502, 0.50),
             ("iso_w6c", 6, 1721601, 0.22), ("factor_w6c", 6, 1721602, 0.50),
             ("iso_w7c", 7, 1721701, 0.22), ("factor_w7c", 7, 1721702, 0.50)),
        )


if __name__ == "__main__":
    unittest.main()
