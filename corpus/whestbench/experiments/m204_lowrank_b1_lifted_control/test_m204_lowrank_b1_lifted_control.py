"""Generated-only algebra and static-cost tests for M204."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m204_lowrank_b1_lifted_control import (  # noqa: E402
    STRICT_COMPOSED_HEADROOM,
    brute_complete_source,
    build_rank_one_b1_state,
    canonical_covariance,
    canonical_delta_tilde,
    complete_domain_conservation_source,
    complete_domain_mixture,
    compile_lifted_rank_one_control,
    distinct_only_table,
    m204_cost_ledger,
    rank_factor_schur_identity,
    rank_one_control_table,
    source_add,
    source_max_abs_difference,
)


def _generated_cell(width: int, seed: int):
    rng = np.random.Generator(np.random.Philox(seed))
    root = rng.normal(size=(width, width))
    covariance = root @ root.T + np.eye(width)
    mean = rng.normal(scale=0.25, size=width)
    weight = rng.normal(size=(width, width + 1))
    return mean, covariance, weight, rng


def _distinct_symmetric_target(width: int, rng: np.random.Generator) -> np.ndarray:
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


def _uniform_distinct_q0(width: int) -> np.ndarray:
    answer = np.zeros((width, width, width), dtype=np.float64)
    mass = 1.0 / (width * (width - 1) * (width - 2))
    for i in range(width):
        for j in range(width):
            for k in range(width):
                if len({i, j, k}) == 3:
                    answer[i, j, k] = mass
    return answer


class M204LowRankLiftedControlTests(unittest.TestCase):
    def test_rank_factor_schur_identity(self):
        for width in (3, 4, 8):
            mean, covariance, _, _ = _generated_cell(width, 204100 + width)
            state = build_rank_one_b1_state(mean, covariance)
            direct, factorized = rank_factor_schur_identity(state.rank_factor)
            np.testing.assert_allclose(direct, factorized, rtol=0.0, atol=3e-12)
            canonical = canonical_covariance(state)
            self.assertTrue(np.all(state.diagonal_residual >= 0.0))
            np.testing.assert_allclose(
                np.diag(canonical), np.diag(covariance), rtol=0.0, atol=3e-12
            )

    def test_rademacher_delta_tilde_identity(self):
        for width in (3, 4, 5, 8):
            mean, covariance, _, _ = _generated_cell(width, 204200 + width)
            state = build_rank_one_b1_state(mean, covariance)
            direct = canonical_delta_tilde(state)
            expected = rank_one_control_table(state.rank_factor, distinct_only=True)
            np.testing.assert_allclose(direct, expected, rtol=0.0, atol=4e-11)

    def test_lifted_source_slots_match_complete_ordered_oracle(self):
        for width in (3, 4, 5, 8):
            mean, covariance, weight, _ = _generated_cell(width, 204300 + width)
            state = build_rank_one_b1_state(mean, covariance)
            control = rank_one_control_table(state.rank_factor, distinct_only=False)
            compiled = compile_lifted_rank_one_control(weight, state.rank_factor)
            oracle = brute_complete_source(weight, control)
            self.assertLess(source_max_abs_difference(compiled, oracle), 4e-10)
            np.testing.assert_array_equal(compiled.aaaa, np.diag(compiled.aaab))

    def test_hidden_permutation_and_positive_gauge_covariance(self):
        for width in (4, 8):
            mean, covariance, weight, rng = _generated_cell(width, 204400 + width)
            baseline_state = build_rank_one_b1_state(mean, covariance)
            baseline = compile_lifted_rank_one_control(weight, baseline_state.rank_factor)

            permutation = rng.permutation(width)
            permuted_state = build_rank_one_b1_state(
                mean[permutation], covariance[permutation][:, permutation]
            )
            permuted = compile_lifted_rank_one_control(
                weight[permutation], permuted_state.rank_factor
            )
            self.assertLess(source_max_abs_difference(baseline, permuted), 6e-10)

            gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
            gauged_state = build_rank_one_b1_state(
                mean * gauge,
                gauge[:, None] * covariance * gauge[None, :],
            )
            gauged = compile_lifted_rank_one_control(
                weight / gauge[:, None], gauged_state.rank_factor
            )
            self.assertLess(source_max_abs_difference(baseline, gauged), 8e-10)

    def test_complete_domain_conservation_and_full_support(self):
        width = 5
        mean, covariance, weight, rng = _generated_cell(width, 204500)
        state = build_rank_one_b1_state(mean, covariance)
        target = _distinct_symmetric_target(width, rng)
        control = rank_one_control_table(state.rank_factor, distinct_only=False)
        q = complete_domain_mixture(_uniform_distinct_q0(width))
        target_source, control_source, residual_expectation = complete_domain_conservation_source(
            weight, target, control, q
        )
        reconstructed = source_add(control_source, residual_expectation)
        self.assertLess(source_max_abs_difference(target_source, reconstructed), 6e-10)
        self.assertTrue(np.all(q > 0.0))
        self.assertAlmostEqual(float(np.sum(q)), 1.0, places=13)
        residual = distinct_only_table(target) - control
        for i in range(width):
            self.assertTrue(np.allclose(residual[i, i, :], -control[i, i, :]))
            self.assertTrue(np.allclose(residual[i, :, i], -control[i, :, i]))
            self.assertTrue(np.allclose(residual[:, i, i], -control[:, i, i]))

    def test_cost_records_the_strict_blocker_without_granting_credit(self):
        ledger = m204_cost_ledger()
        self.assertEqual(ledger["dense_output_products_per_layer"], 1)
        self.assertEqual(ledger["f64_square_product_all_layers"], 2_076_311_552)
        self.assertEqual(ledger["protected_dense_source_emission"], 2_595_389_440)
        self.assertEqual(ledger["additional_if_same_call_proved"], 0)
        self.assertEqual(ledger["additional_if_uncredited"], 2_595_389_440)
        self.assertTrue(ledger["uncredited_product_exceeds_strict_headroom"])
        self.assertFalse(ledger["native_replacement_proved"])
        self.assertEqual(ledger["strict_composed_headroom"], STRICT_COMPOSED_HEADROOM)
        self.assertEqual(ledger["status"], "BLOCKED_COST_PREMISE")

    def test_predeclaration_forbids_a_variance_runner(self):
        self.assertFalse((HERE / "run_m204_source_variance.py").exists())


if __name__ == "__main__":
    unittest.main()
