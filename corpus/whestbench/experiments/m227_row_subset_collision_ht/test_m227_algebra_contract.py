"""Generated-only RED/GREEN contracts for frozen M227 row HT subtraction."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import inspect
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m205_rankone_complete_physical_owner",
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m215_rankone_collision_correction as m215  # noqa: E402
import m227_row_subset_collision_ht as m227  # noqa: E402


def _cell(width: int, seed: int):
    rng = np.random.Generator(np.random.Philox(seed))
    weight = rng.normal(scale=0.35, size=(width, width + 2))
    factor = rng.normal(scale=0.25, size=width)
    return weight, factor, rng


def _mean_sources(sources: list[m205.Source211]) -> m205.Source211:
    count = float(len(sources))
    return m205.Source211(
        sum(source.aaaa for source in sources) / count,
        sum(source.aaab for source in sources) / count,
        sum(source.aabb for source in sources) / count,
    )


def _direct_row_oracle(
    weight: np.ndarray, factor: np.ndarray, selected: tuple[int, ...]
) -> m205.Source211:
    """Independent loop oracle: exact B/p/rho plus HT t/A/E/D rows."""

    s = factor[:, None] * weight
    p = np.sum(s, axis=0)
    b = s.T @ s
    rho = np.diag(b).copy()
    scale = float(s.shape[0]) / float(len(selected))
    t = np.zeros(s.shape[1], dtype=np.float64)
    a = np.zeros((s.shape[1], s.shape[1]), dtype=np.float64)
    e = np.zeros_like(a)
    d = np.zeros_like(a)
    for index in selected:
        row = s[index]
        row2 = row * row
        row3 = row2 * row
        t += row3
        a += np.outer(row2, row)
        e += np.outer(row3, row)
        d += np.outer(row2, row2)
    t *= scale
    a *= scale
    e *= scale
    d *= scale
    aaab = (
        -18.0 * (p[:, None] * a)
        - 6.0 * np.outer(t, p)
        - 12.0 * (rho[:, None] * b)
        + 24.0 * e
    )
    aabb = (
        -12.0 * (a * p[None, :] + p[:, None] * a.T)
        - 4.0 * np.outer(rho, rho)
        - 8.0 * (b * b)
        + 24.0 * d
    )
    return m205.Source211(np.diag(aaab).copy(), aaab, aabb)


class M227AlgebraTests(unittest.TestCase):
    def test_exhaustive_subset_mean_matches_m215_strict_and_cubic_oracle(self):
        worst = 0.0
        for width in range(3, 10):
            weight, factor, _rng = _cell(width, 227000 + width)
            full = m205.compile_lifted_rank_one_control(weight, factor)
            exact_collision = m215.compile_rank_one_collision_source_numpy(weight, factor)
            expected_strict = m215.subtract_source(full, exact_collision)
            for subset_size in sorted({1, min(3, width - 1)}):
                strict_draws = []
                for selected in combinations(range(width), subset_size):
                    collision = m227.compile_row_sketch_collision_source_numpy(
                        weight, factor, selected
                    )
                    strict_draws.append(m215.subtract_source(full, collision))
                actual_mean = _mean_sources(strict_draws)
                worst = max(
                    worst,
                    m205.source_max_abs_difference(actual_mean, expected_strict),
                )

            table = m205.rank_one_control_table(factor)
            for i in range(width):
                for j in range(width):
                    for k in range(width):
                        if len({i, j, k}) < 3:
                            table[i, j, k] = 0.0
            cubic_strict = m205.brute_complete_source(weight, table)
            worst = max(
                worst,
                m205.source_max_abs_difference(expected_strict, cubic_strict),
            )
        self.assertLessEqual(worst, 2e-10)

    def test_each_draw_matches_independent_row_loop(self):
        weight, factor, _rng = _cell(9, 227101)
        for selected in ((0,), (0, 3, 8), (1, 2, 4, 7)):
            actual = m227.compile_row_sketch_collision_source_numpy(
                weight, factor, selected
            )
            expected = _direct_row_oracle(weight, factor, selected)
            self.assertLessEqual(
                m205.source_max_abs_difference(actual, expected), 2e-10
            )

    def test_receipt_co_permutation_and_positive_gauge_are_pathwise_covariant(self):
        width = 9
        weight, factor, rng = _cell(width, 227201)
        priorities = rng.random((1, width), dtype=np.float64)
        receipt = m227.issue_priority_receipt(
            priorities, subset_rows=3, producer_epoch=227
        )
        baseline = m227.compile_row_sketch_collision_source_numpy(
            weight, factor, receipt.selected[0]
        )

        permutation = rng.permutation(width)
        permuted_receipt = m227.permute_receipt(receipt, permutation)
        permuted = m227.compile_row_sketch_collision_source_numpy(
            weight[permutation], factor[permutation], permuted_receipt.selected[0]
        )
        self.assertLessEqual(
            m205.source_max_abs_difference(baseline, permuted), 2e-10
        )

        gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
        gauged = m227.compile_row_sketch_collision_source_numpy(
            weight / gauge[:, None], factor * gauge, receipt.selected[0]
        )
        self.assertLessEqual(
            m205.source_max_abs_difference(baseline, gauged), 2e-10
        )

    def test_zero_factor_and_receipt_errors_fail_closed(self):
        weight, factor, _rng = _cell(7, 227301)
        zero = m227.compile_row_sketch_collision_source_numpy(
            weight, np.zeros_like(factor), (0, 2)
        )
        self.assertTrue(np.array_equal(zero.aaaa, np.zeros_like(zero.aaaa)))
        self.assertTrue(np.array_equal(zero.aaab, np.zeros_like(zero.aaab)))
        self.assertTrue(np.array_equal(zero.aabb, np.zeros_like(zero.aabb)))

        with self.assertRaises(ValueError):
            m227.compile_row_sketch_collision_source_numpy(weight, factor, (1, 1))
        with self.assertRaises(ValueError):
            m227.compile_row_sketch_collision_source_numpy(weight, factor, (7,))
        tied = np.arange(14, dtype=np.float64).reshape(2, 7)
        tied[1, 3] = tied[1, 2]
        with self.assertRaises(ValueError):
            m227.issue_priority_receipt(tied, subset_rows=2, producer_epoch=227)
        with self.assertRaises(ValueError):
            m227.issue_priority_receipt(
                np.arange(7, dtype=np.float64)[None, :],
                subset_rows=7,
                producer_epoch=227,
            )

    def test_target_function_contains_no_cubic_tensor_or_triple_loop(self):
        source = inspect.getsource(m227.compile_row_sketch_collision_source_numpy)
        self.assertNotIn("for i in range", source)
        self.assertNotIn("(width, width, width)", source)
        self.assertNotIn("einsum", source)

    def test_predeclaration_is_frozen_and_no_g0_result_exists(self):
        self.assertTrue((HERE / "M227_PREDECLARATION_20260809.md").exists())
        self.assertTrue((HERE / "M227_FROZEN_MANIFEST_20260809.json").exists())
        self.assertFalse((HERE / "M227_G0_RESULTS_20260809.json").exists())


if __name__ == "__main__":
    unittest.main()
