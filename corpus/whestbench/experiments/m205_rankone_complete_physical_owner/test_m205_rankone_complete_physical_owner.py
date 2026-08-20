"""Generated-only, response-free algebra and strict-cost tests for M205."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
M151 = HERE.parent / "m151_b1_forward_control"
if str(M151) not in sys.path:
    sys.path.insert(0, str(M151))

from m205_rankone_complete_physical_owner import (  # noqa: E402
    B1_NODE_COUNT,
    STRICT_COMPOSED_HEADROOM,
    PhysicalFourthOwners,
    Source211,
    brute_complete_source,
    build_rank_one_b1_state,
    canonical_covariance,
    canonical_delta_tilde_distinct,
    compile_lifted_rank_one_control,
    complete_physical_owner_table,
    complete_residual_table,
    rank_one_control_table,
    source_add,
    source_cost_and_blockers,
    source_max_abs_difference,
)
from m151_b1_forward_control import B1CanonicalState  # noqa: E402


def _cell(width: int, seed: int):
    rng = np.random.Generator(np.random.Philox(seed))
    root = rng.normal(size=(width, width))
    covariance = root @ root.T + np.eye(width)
    mean = rng.normal(scale=0.25, size=width)
    weight = rng.normal(size=(width, width + 1))
    return mean, covariance, weight, rng


def _distinct_211(width: int, rng: np.random.Generator) -> np.ndarray:
    """A finite [2,1,1] table with its required singleton-pair symmetry."""

    answer = np.zeros((width, width, width), dtype=np.float64)
    for i in range(width):
        for j in range(width):
            for k in range(j + 1, width):
                if i == j or i == k:
                    continue
                value = float(rng.normal())
                answer[i, j, k] = value
                answer[i, k, j] = value
    return answer


def _owners(width: int, rng: np.random.Generator) -> PhysicalFourthOwners:
    """Physical owner fixtures: K31 is intentionally directed."""

    k4 = rng.normal(size=width)
    k31 = rng.normal(size=(width, width))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(size=(width, width))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    return PhysicalFourthOwners(k4=k4, k31=k31, k22=k22)


def _gauge_table(table: np.ndarray, gauge: np.ndarray) -> np.ndarray:
    return table * (gauge * gauge)[:, None, None] * gauge[None, :, None] * gauge[None, None, :]


def _m151_contract(state) -> None:
    """Use M151's actual public constructor, not a local imitation of it."""

    B1CanonicalState(
        omega=state.omega,
        conditional_mean=state.conditional_mean,
        conditional_variance=state.conditional_variance,
    )


def _independent_physical_collision_source(weight: np.ndarray, owners: PhysicalFourthOwners) -> Source211:
    """Direct [4]/[3,1]/[2,2] source, independent of the cubic table oracle."""

    width, outputs = weight.shape
    aaab = np.zeros((outputs, outputs), dtype=np.float64)
    aabb = np.zeros_like(aaab)
    for i in range(width):
        x = weight[i]
        aaab += owners.k4[i] * np.outer(x**3, x)
        aabb += owners.k4[i] * np.outer(x * x, x * x)
        for j in range(width):
            if i == j:
                continue
            y = weight[j]
            aaab += owners.k31[i, j] * (
                3.0 * np.outer(x * x * y, x) + np.outer(x**3, y)
            )
            mixed = np.outer(x * x, x * y)
            aabb += 2.0 * owners.k31[i, j] * (mixed + mixed.T)
    for i in range(width):
        for j in range(i + 1, width):
            x, y = weight[i], weight[j]
            aaab += 3.0 * owners.k22[i, j] * (
                np.outer(x * y * y, x) + np.outer(x * x * y, y)
            )
            aabb += owners.k22[i, j] * (
                np.outer(x * x, y * y)
                + np.outer(y * y, x * x)
                + 4.0 * np.outer(x * y, x * y)
            )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


class M205RankOneCompletePhysicalOwnerTests(unittest.TestCase):
    def test_b1_contract_distinct_identity_and_zero_variance_totality(self):
        for width in (3, 4, 5):
            mean, covariance, _, _ = _cell(width, 205100 + width)
            # This exact zero mean checks that the signed pair is valid when
            # M179's post-ReLU mean is zero, rather than relying on positivity.
            mean[0] = 0.0
            state = build_rank_one_b1_state(mean, covariance)
            _m151_contract(state)
            self.assertEqual(state.omega.shape, (B1_NODE_COUNT,))
            self.assertEqual(state.conditional_mean.shape, (B1_NODE_COUNT, width))
            self.assertTrue(np.all(np.isfinite(state.conditional_mean)))
            self.assertTrue(np.all(state.conditional_variance >= 0.0))
            self.assertAlmostEqual(float(np.sum(state.omega)), 1.0, places=13)
            self.assertEqual(int(np.count_nonzero(state.omega)), 2)
            np.testing.assert_allclose(
                np.diag(canonical_covariance(state)), np.diag(covariance), rtol=0.0, atol=3e-12
            )
            direct = canonical_delta_tilde_distinct(state)
            expected = rank_one_control_table(state.factor)
            for i in range(width):
                for j in range(width):
                    for k in range(width):
                        if len({i, j, k}) == 3:
                            self.assertAlmostEqual(float(direct[i, j, k]), float(expected[i, j, k]), places=10)

        zero = build_rank_one_b1_state(np.zeros(3), np.zeros((3, 3)))
        _m151_contract(zero)
        np.testing.assert_array_equal(zero.factor, np.zeros(3))
        np.testing.assert_array_equal(zero.diagonal_residual, np.zeros(3))
        np.testing.assert_array_equal(canonical_delta_tilde_distinct(zero), np.zeros((3, 3, 3)))

    def test_compiler_matches_brute_complete_rank_one_source_slots_n3_to_n5(self):
        for width in (3, 4, 5):
            mean, covariance, weight, _ = _cell(width, 205200 + width)
            state = build_rank_one_b1_state(mean, covariance)
            control = rank_one_control_table(state.factor)
            compiled = compile_lifted_rank_one_control(weight, state.factor)
            brute = brute_complete_source(weight, control)
            self.assertLess(source_max_abs_difference(compiled, brute), 4e-10)
            np.testing.assert_array_equal(compiled.aaaa, np.diag(compiled.aaab))

    def test_complete_physical_owner_slots_and_source_reconstruction_n3_to_n5(self):
        for width in (3, 4, 5):
            mean, covariance, weight, rng = _cell(width, 205300 + width)
            state = build_rank_one_b1_state(mean, covariance)
            owners = _owners(width, rng)
            distinct = _distinct_211(width, rng)
            target = complete_physical_owner_table(distinct, owners)
            control = rank_one_control_table(state.factor)
            residual = complete_residual_table(target, control)

            for i in range(width):
                self.assertAlmostEqual(float(target[i, i, i]), float(owners.k4[i] / 6.0), places=13)
                for j in range(width):
                    if i == j:
                        continue
                    self.assertAlmostEqual(float(target[i, i, j]), float(owners.k31[i, j] / 3.0), places=13)
                    self.assertAlmostEqual(float(target[i, j, i]), float(owners.k31[i, j] / 3.0), places=13)
                    self.assertAlmostEqual(float(target[i, j, j]), float(owners.k22[i, j] / 2.0), places=13)
                    for k in range(width):
                        if len({i, j, k}) == 3:
                            self.assertAlmostEqual(float(target[i, j, k]), float(distinct[i, j, k]), places=13)

            # Collision rows are physically owned rather than M156-zeroed.
            collision_mass = sum(
                abs(float(target[i, j, k]))
                for i in range(width)
                for j in range(width)
                for k in range(width)
                if len({i, j, k}) < 3
            )
            self.assertGreater(collision_mass, 0.0)

            physical_only = complete_physical_owner_table(np.zeros_like(distinct), owners)
            direct_physical = _independent_physical_collision_source(weight, owners)
            self.assertLess(
                source_max_abs_difference(brute_complete_source(weight, physical_only), direct_physical),
                4e-10,
            )

            direct = brute_complete_source(weight, target)
            reconstructed = source_add(
                compile_lifted_rank_one_control(weight, state.factor),
                brute_complete_source(weight, residual),
            )
            self.assertLess(source_max_abs_difference(direct, reconstructed), 5e-10)

    def test_permutation_and_positive_gauge_covariance_of_complete_owners(self):
        width = 5
        mean, covariance, weight, rng = _cell(width, 205400)
        owners = _owners(width, rng)
        target = complete_physical_owner_table(_distinct_211(width, rng), owners)
        baseline_state = build_rank_one_b1_state(mean, covariance)
        _m151_contract(baseline_state)
        baseline_control = rank_one_control_table(baseline_state.factor)
        baseline = source_add(
            compile_lifted_rank_one_control(weight, baseline_state.factor),
            brute_complete_source(weight, complete_residual_table(target, baseline_control)),
        )

        permutation = rng.permutation(width)
        permuted_state = build_rank_one_b1_state(
            mean[permutation], covariance[permutation][:, permutation]
        )
        _m151_contract(permuted_state)
        permuted_target = target[permutation][:, permutation][:, :, permutation]
        permuted_control = rank_one_control_table(permuted_state.factor)
        permuted = source_add(
            compile_lifted_rank_one_control(weight[permutation], permuted_state.factor),
            brute_complete_source(weight[permutation], complete_residual_table(permuted_target, permuted_control)),
        )
        self.assertLess(source_max_abs_difference(baseline, permuted), 8e-10)

        gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
        gauged_state = build_rank_one_b1_state(
            mean * gauge, gauge[:, None] * covariance * gauge[None, :]
        )
        _m151_contract(gauged_state)
        gauged_target = _gauge_table(target, gauge)
        gauged_control = rank_one_control_table(gauged_state.factor)
        gauged = source_add(
            compile_lifted_rank_one_control(weight / gauge[:, None], gauged_state.factor),
            brute_complete_source(weight / gauge[:, None], complete_residual_table(gauged_target, gauged_control)),
        )
        self.assertLess(source_max_abs_difference(baseline, gauged), 1e-9)

    def test_strict_cost_and_provider_blockers_are_not_waived(self):
        cost = source_cost_and_blockers()
        self.assertEqual(cost["one_f64_square_raw"], 2_076_311_552)
        self.assertEqual(cost["one_f64_square_protected"], 2_595_389_440)
        self.assertEqual(cost["strict_composed_headroom"], STRICT_COMPOSED_HEADROOM)
        self.assertGreater(cost["one_f64_square_protected"], STRICT_COMPOSED_HEADROOM)
        self.assertIn("not an identical shared", str(cost["m151_booking"]))
        self.assertEqual(
            cost["disposition"], "BLOCKED_PHYSICAL_COLLISION_PROVIDER_AND_NATIVE_COST"
        )
        self.assertGreaterEqual(len(cost["physical_provider_blockers"]), 4)

    def test_predeclaration_and_no_response_runner(self):
        self.assertTrue((HERE / "M205_PREDECLARATION_20260809.md").exists())
        self.assertFalse((HERE / "run_m205_source_variance.py").exists())


if __name__ == "__main__":
    unittest.main()
