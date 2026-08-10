"""Frozen generated-only algebra gates for M210, written before code."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
M205 = HERE.parent / "m205_rankone_complete_physical_owner"
for path in (HERE, M205):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m210_level_fused_recursive_gram as m210  # noqa: E402


class M210LevelFusedAlgebraTests(unittest.TestCase):
    def test_integer_and_float_gram_parity(self) -> None:
        rng = np.random.default_rng(210001)
        for width in (8, 16):
            integer = rng.integers(-5, 6, size=(3, width, width), dtype=np.int64)
            got = m210.level_fused_batched_gram(integer, depth=3)
            expected = np.swapaxes(integer, -2, -1) @ integer
            self.assertTrue(np.array_equal(got, expected))
        for width in (8, 16, 32):
            value = rng.normal(size=(4, width, width))
            got = m210.level_fused_batched_gram(value, depth=3)
            expected = np.swapaxes(value, -2, -1) @ value
            self.assertLessEqual(float(np.max(np.abs(got - expected))), 2e-12)
            self.assertTrue(np.array_equal(got, np.swapaxes(got, -2, -1)))

    def test_source_parity_with_dense_m205(self) -> None:
        rng = np.random.default_rng(210002)
        for width in (8, 16, 32):
            weight = rng.normal(scale=0.25, size=(width, width))
            factor = rng.normal(scale=0.15, size=width)
            got = m210.compile_level_fused_rank_one_control(weight, factor, depth=3)
            expected = m205.compile_lifted_rank_one_control(weight, factor)
            self.assertLessEqual(m205.source_max_abs_difference(got, expected), 2e-10)

    def test_zero_permutation_and_gauge(self) -> None:
        rng = np.random.default_rng(210003)
        width = 16
        weight = rng.normal(scale=0.2, size=(width, width))
        factor = rng.normal(scale=0.1, size=width)
        base = m210.compile_level_fused_rank_one_control(weight, factor)
        permutation = rng.permutation(width)
        moved = m210.compile_level_fused_rank_one_control(
            weight[permutation], factor[permutation]
        )
        self.assertLessEqual(m205.source_max_abs_difference(base, moved), 3e-10)
        gauge = np.exp(rng.uniform(-0.5, 0.5, size=width))
        gauged = m210.compile_level_fused_rank_one_control(
            weight / gauge[:, None], factor * gauge
        )
        self.assertLessEqual(m205.source_max_abs_difference(base, gauged), 3e-10)
        zero = m210.compile_level_fused_rank_one_control(weight, np.zeros(width))
        self.assertTrue(np.array_equal(zero.aaab, np.zeros((width, width))))
        self.assertTrue(np.array_equal(zero.aabb, np.zeros((width, width))))

    def test_frozen_static_prediction(self) -> None:
        prediction = m210.static_prediction()
        self.assertEqual(prediction["matmul_calls"], 4)
        self.assertEqual(prediction["matmul_bill"], 1_167_925_248)
        self.assertEqual(prediction["reshape_calls"], 4)
        self.assertEqual(prediction["reshape_bill"], 16_252_928)

    def test_invalid_shapes_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            m210.level_fused_batched_gram(np.ones((2, 12, 12)), depth=3)
        with self.assertRaises(ValueError):
            m210.level_fused_batched_gram(np.ones((2, 8, 7)), depth=3)


if __name__ == "__main__":
    unittest.main()
