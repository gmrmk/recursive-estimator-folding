"""Generated-only, response-free contract tests for frozen M215."""

from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (HERE, BASE / "m205_rankone_complete_physical_owner"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m215_rankone_collision_correction as m215  # noqa: E402


def _cell(width: int, seed: int):
    rng = np.random.Generator(np.random.Philox(seed))
    output_width = width + 2
    weight = rng.normal(scale=0.4, size=(width, output_width))
    factor = rng.normal(scale=0.3, size=width)
    return weight, factor, rng


def _collision_and_distinct_tables(factor: np.ndarray):
    full = m205.rank_one_control_table(factor)
    width = factor.size
    collision = np.zeros_like(full)
    distinct = np.zeros_like(full)
    for i in range(width):
        for j in range(width):
            for k in range(width):
                if len({i, j, k}) < 3:
                    collision[i, j, k] = full[i, j, k]
                else:
                    distinct[i, j, k] = full[i, j, k]
    return full, collision, distinct


class M215AlgebraTests(unittest.TestCase):
    def test_collision_compiler_and_strict_subtraction_match_cubic_oracles(self):
        worst_collision = 0.0
        worst_strict = 0.0
        for width in (3, 4, 5, 6, 7):
            weight, factor, _rng = _cell(width, 215100 + width)
            _full_table, collision_table, distinct_table = _collision_and_distinct_tables(factor)
            expected_collision = m205.brute_complete_source(weight, collision_table)
            expected_strict = m205.brute_complete_source(weight, distinct_table)
            actual_collision = m215.compile_rank_one_collision_source_numpy(weight, factor)
            full = m205.compile_lifted_rank_one_control(weight, factor)
            actual_strict = m215.subtract_source(full, actual_collision)
            collision_error = m205.source_max_abs_difference(actual_collision, expected_collision)
            strict_error = m205.source_max_abs_difference(actual_strict, expected_strict)
            worst_collision = max(worst_collision, collision_error)
            worst_strict = max(worst_strict, strict_error)
        self.assertLessEqual(worst_collision, 2e-9)
        self.assertLessEqual(worst_strict, 2e-9)

    def test_hidden_permutation_and_positive_relu_gauge_are_covariant(self):
        width = 7
        weight, factor, rng = _cell(width, 215201)
        baseline = m215.compile_rank_one_collision_source_numpy(weight, factor)

        permutation = rng.permutation(width)
        permuted = m215.compile_rank_one_collision_source_numpy(
            weight[permutation], factor[permutation]
        )
        self.assertLessEqual(m205.source_max_abs_difference(baseline, permuted), 2e-9)

        gauge = np.exp(rng.uniform(-0.8, 0.8, size=width))
        gauged = m215.compile_rank_one_collision_source_numpy(
            weight / gauge[:, None], factor * gauge
        )
        self.assertLessEqual(m205.source_max_abs_difference(baseline, gauged), 2e-9)

    def test_zero_factor_is_exact_zero_and_input_contract_fails_closed(self):
        weight, factor, _rng = _cell(5, 215301)
        source = m215.compile_rank_one_collision_source_numpy(weight, np.zeros_like(factor))
        self.assertTrue(np.array_equal(source.aaaa, np.zeros_like(source.aaaa)))
        self.assertTrue(np.array_equal(source.aaab, np.zeros_like(source.aaab)))
        self.assertTrue(np.array_equal(source.aabb, np.zeros_like(source.aabb)))
        with self.assertRaises(ValueError):
            m215.compile_rank_one_collision_source_numpy(weight, factor[:-1])
        bad = weight.copy()
        bad[0, 0] = np.nan
        with self.assertRaises(ValueError):
            m215.compile_rank_one_collision_source_numpy(bad, factor)

    def test_target_source_has_no_cubic_table_or_triple_loop(self):
        source = inspect.getsource(m215.compile_rank_one_collision_source_numpy)
        self.assertNotIn("einsum(\"i,j,k", source)
        self.assertNotIn("for i in range", source)
        self.assertNotIn("(width, width, width)", source)

    def test_predeclaration_is_present_and_response_runner_is_absent(self):
        self.assertTrue((HERE / "M215_PREDECLARATION_20260809.md").exists())
        self.assertTrue((HERE / "M215_FROZEN_MANIFEST_20260809.json").exists())
        self.assertFalse((HERE / "run_m215_source_variance.py").exists())


if __name__ == "__main__":
    unittest.main()
