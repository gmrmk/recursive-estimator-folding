"""Generated-only boundary tests for M207."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
M204 = HERE.parent / "m204_lowrank_b1_lifted_control"
for path in (str(HERE), str(M204)):
    if path not in sys.path:
        sys.path.insert(0, path)

import m204_lowrank_b1_lifted_control as m204  # noqa: E402
from m207_zero_variance_rank_one_guard import rank_one_state_from_background  # noqa: E402


def _positive_cell(width: int, seed: int):
    rng = np.random.Generator(np.random.Philox(seed))
    root = rng.normal(size=(width, width))
    return rng.normal(size=width), root @ root.T + np.eye(width), rng.normal(size=(width, width + 1)), rng


def _source_error(left, right) -> float:
    return m204.source_max_abs_difference(left, right)


class M207ZeroVarianceRankOneGuardTests(unittest.TestCase):
    def test_unwrapped_m204_rejects_then_guard_accepts_all_zero_covariance(self):
        mu = np.array([1.5, -2.0, 0.25])
        zero = np.zeros((3, 3))
        with self.assertRaisesRegex(ValueError, "no positive-variance"):
            m204.build_rank_one_b1_state(mu, zero)

        state = rank_one_state_from_background(mu, zero)
        self.assertEqual(state.omega.shape, (m204.B1_NODE_COUNT,))
        self.assertAlmostEqual(float(np.sum(state.omega)), 1.0, places=14)
        np.testing.assert_array_equal(state.rank_factor, np.zeros_like(mu))
        np.testing.assert_array_equal(state.diagonal_residual, np.zeros_like(mu))
        np.testing.assert_array_equal(state.conditional_mean, np.broadcast_to(mu, state.conditional_mean.shape))
        np.testing.assert_array_equal(m204.canonical_covariance(state), zero)

    def test_all_zero_branch_is_exact_zero_control_and_source(self):
        mu = np.array([2.0, -1.0, 0.0, 3.0])
        state = rank_one_state_from_background(mu, np.zeros((4, 4)))
        table = m204.rank_one_control_table(state.rank_factor, distinct_only=False)
        np.testing.assert_array_equal(table, np.zeros_like(table))
        direct = m204.canonical_delta_tilde(state)
        np.testing.assert_array_equal(direct, np.zeros_like(direct))
        weight = np.arange(20, dtype=np.float64).reshape(4, 5) / 7.0
        compiled = m204.compile_lifted_rank_one_control(weight, state.rank_factor)
        oracle = m204.brute_complete_source(weight, table)
        self.assertEqual(_source_error(compiled, oracle), 0.0)

    def test_mixed_zero_rows_delegate_exactly_to_m204(self):
        mu = np.array([0.25, -1.0, 0.5, 2.0])
        covariance = np.diag(np.array([0.0, 2.0, 0.0, 5.0]))
        guarded = rank_one_state_from_background(mu, covariance)
        original = m204.build_rank_one_b1_state(mu, covariance)
        for name in ("omega", "conditional_mean", "conditional_variance", "rank_factor", "diagonal_residual"):
            np.testing.assert_array_equal(getattr(guarded, name), getattr(original, name))
        self.assertEqual(guarded.rank_factor[0], 0.0)
        self.assertEqual(guarded.rank_factor[2], 0.0)
        self.assertEqual(guarded.diagonal_residual[0], 0.0)
        self.assertEqual(guarded.diagonal_residual[2], 0.0)

    def test_positive_diagonal_nonregression_is_bitwise_m204(self):
        for width in (3, 5, 8):
            mu, covariance, _, _ = _positive_cell(width, 207100 + width)
            guarded = rank_one_state_from_background(mu, covariance)
            original = m204.build_rank_one_b1_state(mu, covariance)
            for name in ("omega", "conditional_mean", "conditional_variance", "rank_factor", "diagonal_residual"):
                np.testing.assert_array_equal(getattr(guarded, name), getattr(original, name))

    def test_permutation_and_positive_gauge_covariance_for_all_zero_and_mixed_states(self):
        rng = np.random.Generator(np.random.Philox(207200))
        for covariance in (np.zeros((4, 4)), np.diag(np.array([0.0, 1.5, 0.0, 4.0]))):
            mu = rng.normal(size=4)
            weight = rng.normal(size=(4, 6))
            baseline = rank_one_state_from_background(mu, covariance)
            baseline_source = m204.compile_lifted_rank_one_control(weight, baseline.rank_factor)

            permutation = rng.permutation(4)
            permuted = rank_one_state_from_background(mu[permutation], covariance[permutation][:, permutation])
            permuted_source = m204.compile_lifted_rank_one_control(weight[permutation], permuted.rank_factor)
            self.assertLess(_source_error(baseline_source, permuted_source), 7e-10)

            gauge = np.exp(rng.uniform(-0.7, 0.7, size=4))
            gauged = rank_one_state_from_background(mu * gauge, gauge[:, None] * covariance * gauge[None, :])
            gauged_source = m204.compile_lifted_rank_one_control(weight / gauge[:, None], gauged.rank_factor)
            self.assertLess(_source_error(baseline_source, gauged_source), 8e-10)

    def test_complete_source_parity_for_mixed_and_positive_states(self):
        for width, covariance in (
            (3, np.diag(np.array([0.0, 1.0, 3.0]))),
            (5, _positive_cell(5, 207301)[1]),
        ):
            mu, _, weight, _ = _positive_cell(width, 207400 + width)
            state = rank_one_state_from_background(mu, covariance)
            table = m204.rank_one_control_table(state.rank_factor, distinct_only=False)
            compiled = m204.compile_lifted_rank_one_control(weight, state.rank_factor)
            oracle = m204.brute_complete_source(weight, table)
            self.assertLess(_source_error(compiled, oracle), 6e-10)

    def test_zero_diagonal_nonzero_offdiagonal_is_rejected(self):
        mu = np.zeros(3)
        invalid = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        with self.assertRaisesRegex(ValueError, "all-zero covariance diagonal"):
            rank_one_state_from_background(mu, invalid)


if __name__ == "__main__":
    unittest.main()
