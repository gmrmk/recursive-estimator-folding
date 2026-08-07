"""Generated-only exhaustive orbit and ownership tests for M167."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m167_collision_owner_unification",
    "m156_extended_domain_star_control",
    "m122_nonzero_bridge_theory",
):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from m122_nonzero_bridge import build_state, exact_collision_cumulant  # noqa: E402
from m156_extended_domain_star_control import (  # noqa: E402
    dense_extended_source,
    distinct_target_extension,
    source_add,
    source_max_abs_difference,
)
from m167_collision_owner_unification import (  # noqa: E402
    PhysicalFourthOwners,
    complete_residual_table,
    complete_owner_table,
    complete_source_reference,
    direct_physical_owner_source,
    gauge_owners,
    m156_conservation_error,
    m163_conservation_error,
    m163_required_k22_for_absorption,
    permute_owners,
    physical_collision_tensor,
    retired_owners,
    source_from_physical_tensor,
    static_owner_ledger,
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


class TestM167CollisionOwnerUnification(unittest.TestCase):
    def test_literal_orbit_coefficients_and_complete_residual_preserve_collisions(self) -> None:
        rng = np.random.default_rng(16700)
        owners = generated_owners(rng, 5)
        distinct = generated_distinct(rng, 5)
        table = complete_owner_table(distinct, owners)
        for i in range(5):
            self.assertEqual(table[i, i, i], owners.k4[i] / 6.0)
            for j in range(5):
                if i == j:
                    continue
                self.assertEqual(table[i, i, j], owners.k31[i, j] / 3.0)
                self.assertEqual(table[i, j, i], owners.k31[i, j] / 3.0)
                self.assertEqual(table[i, j, j], owners.k22[i, j] / 2.0)
        control = np.full_like(table, 0.125)
        residual = complete_residual_table(table, control)
        self.assertEqual(residual[0, 0, 0], owners.k4[0] / 6.0 - 0.125)
        self.assertEqual(residual[0, 1, 1], owners.k22[0, 1] / 2.0 - 0.125)

    def test_exhaustive_width2_to6_complete_table_equals_independent_physical_tensor(self) -> None:
        rng = np.random.default_rng(16701)
        for width in range(2, 7):
            owners = generated_owners(rng, width)
            weight = rng.normal(size=(width, width + 1))
            empty_distinct = np.zeros((width, width, width), dtype=np.float64)
            mapped = complete_owner_table(empty_distinct, owners)
            direct_tensor = source_from_physical_tensor(weight, physical_collision_tensor(owners))
            direct_owner = direct_physical_owner_source(weight, owners)
            complete = complete_source_reference(weight, mapped)
            self.assertLess(source_max_abs_difference(complete, direct_tensor), 3e-10)
            self.assertLess(source_max_abs_difference(complete, direct_owner), 3e-10)
            if width >= 3:
                self.assertLess(
                    source_max_abs_difference(complete, dense_extended_source(weight, mapped)),
                    3e-10,
                )

    def test_complete_target_plus_retired_owners_has_exactly_one_collision_source(self) -> None:
        rng = np.random.default_rng(16702)
        for width in range(2, 7):
            owners = generated_owners(rng, width)
            weight = rng.normal(size=(width, width + 2))
            distinct = generated_distinct(rng, width)
            complete = complete_source_reference(weight, complete_owner_table(distinct, owners))
            expected = source_add(
                complete_source_reference(weight, distinct_target_extension(distinct)),
                direct_physical_owner_source(weight, owners),
            )
            self.assertLess(source_max_abs_difference(complete, expected), 5e-10)
            retired = direct_physical_owner_source(weight, retired_owners(owners))
            self.assertLess(np.max(np.abs(retired.aaab)), 1e-15)
            # Retaining the old owner after table injection doubles a nonzero
            # physical source.  The test makes the retirement requirement live.
            double_counted = source_add(complete, direct_physical_owner_source(weight, owners))
            self.assertGreater(source_max_abs_difference(double_counted, expected), 1e-6)

    def test_complete_owner_table_is_permutation_and_positive_gauge_covariant(self) -> None:
        rng = np.random.default_rng(16703)
        for width in range(2, 7):
            owners = generated_owners(rng, width)
            distinct = generated_distinct(rng, width)
            weight = rng.normal(size=(width, width + 1))
            original = complete_source_reference(weight, complete_owner_table(distinct, owners))

            permutation = rng.permutation(width)
            permuted = complete_source_reference(
                weight[permutation],
                complete_owner_table(distinct[np.ix_(permutation, permutation, permutation)], permute_owners(owners, permutation)),
            )
            self.assertLess(source_max_abs_difference(original, permuted), 2e-9)

            gauge = np.exp(rng.uniform(-0.4, 0.4, size=width))
            gauged_distinct = distinct * (gauge[:, None, None] ** 2) * gauge[None, :, None] * gauge[None, None, :]
            gauged = complete_source_reference(
                weight / gauge[:, None],
                complete_owner_table(gauged_distinct, gauge_owners(owners, gauge)),
            )
            self.assertLess(source_max_abs_difference(original, gauged), 4e-9)

    def test_m156_and_m163_conservation_hold_after_physical_owner_injection(self) -> None:
        rng = np.random.default_rng(16704)
        for width in range(3, 7):
            owners = generated_owners(rng, width)
            target = complete_owner_table(generated_distinct(rng, width), owners)
            weight = rng.normal(size=(width, width + 1))
            covariance = generated_spd(rng, width)
            self.assertLess(m156_conservation_error(weight, target, covariance), 5e-8)
            self.assertLess(m163_conservation_error(weight, target, covariance), 5e-8)

    def test_m163_ijj_control_is_not_generically_the_physical_22_owner(self) -> None:
        rng = np.random.default_rng(16722)
        for width in range(2, 7):
            root = rng.normal(size=(width, width))
            normalized = root @ root.T
            normalized /= np.outer(np.sqrt(np.diag(normalized)), np.sqrt(np.diag(normalized)))
            correlation = 0.65 * np.eye(width) + 0.35 * normalized
            scale = np.exp(rng.uniform(-0.3, 0.3, size=width))
            covariance = np.outer(scale, scale) * correlation
            mean = rng.normal(scale=0.3, size=width)
            state = build_state(mean, covariance)
            actual = np.zeros((width, width), dtype=np.float64)
            for i in range(width):
                for j in range(i + 1, width):
                    actual[i, j] = actual[j, i] = exact_collision_cumulant(state, (i, i, j, j), terms=32)
            required = m163_required_k22_for_absorption(covariance)
            self.assertGreater(float(np.max(np.abs(actual - required))), 1e-3)

    def test_static_ledger_claims_no_unpriced_compiler_or_call_credit(self) -> None:
        ledger = static_owner_ledger()
        self.assertEqual(ledger["physical_units"]["[4]"], 256)
        self.assertEqual(ledger["physical_units"]["[3,1]"], 256 * 255)
        self.assertEqual(ledger["physical_units"]["[2,2]"], 256 * 255 // 2)
        self.assertEqual(ledger["complete_table_collision_triples"]["ijj"], 256 * 255)
        self.assertEqual(ledger["m167_added_dense_products_per_layer"], 0)
        self.assertEqual(ledger["m167_added_deployment_calls_claimed"], 0)
        self.assertEqual(ledger["static_disposition"], "ALGEBRAIC_OWNER_REPAIR_ONLY")


if __name__ == "__main__":
    unittest.main()
