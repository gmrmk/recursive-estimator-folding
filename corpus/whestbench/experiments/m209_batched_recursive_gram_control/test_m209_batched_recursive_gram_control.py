"""Frozen response-free gates for M209.

The test is intentionally written before the implementation.  It uses only
generated matrices and the already-frozen M205 dense algebra as an independent
source oracle.
"""

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
import m209_batched_recursive_gram_control as m209  # noqa: E402


class M209RecursiveGramTests(unittest.TestCase):
    def test_integer_gram_is_exact(self) -> None:
        rng = np.random.default_rng(209001)
        for width in (8, 16):
            for layers in (1, 3):
                value = rng.integers(-5, 6, size=(layers, width, width), dtype=np.int64)
                got = m209.recursive_batched_gram(value, depth=3)
                expected = np.swapaxes(value, -2, -1) @ value
                self.assertTrue(np.array_equal(got, expected), (width, layers))

    def test_float_gram_matches_dense(self) -> None:
        rng = np.random.default_rng(209002)
        for width in (8, 16, 32):
            value = rng.normal(size=(4, width, width))
            got = m209.recursive_batched_gram(value, depth=3)
            expected = np.swapaxes(value, -2, -1) @ value
            self.assertLessEqual(float(np.max(np.abs(got - expected))), 2e-12)
            self.assertTrue(np.array_equal(got, np.swapaxes(got, -2, -1)))

    def test_source_parity_with_m205_dense_compiler(self) -> None:
        rng = np.random.default_rng(209003)
        for width in (8, 16, 32):
            for _ in range(3):
                weight = rng.normal(scale=0.3, size=(width, width))
                factor = rng.normal(scale=0.2, size=width)
                got = m209.compile_recursive_rank_one_control(weight, factor, depth=3)
                expected = m205.compile_lifted_rank_one_control(weight, factor)
                self.assertLessEqual(m205.source_max_abs_difference(got, expected), 2e-10)

    def test_permutation_and_positive_gauge(self) -> None:
        rng = np.random.default_rng(209004)
        width = 16
        weight = rng.normal(scale=0.2, size=(width, width))
        factor = rng.normal(scale=0.15, size=width)
        base = m209.compile_recursive_rank_one_control(weight, factor, depth=3)

        permutation = rng.permutation(width)
        moved = m209.compile_recursive_rank_one_control(
            weight[permutation], factor[permutation], depth=3
        )
        self.assertLessEqual(m205.source_max_abs_difference(base, moved), 3e-10)

        gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
        gauged = m209.compile_recursive_rank_one_control(
            weight / gauge[:, None], factor * gauge, depth=3
        )
        self.assertLessEqual(m205.source_max_abs_difference(base, gauged), 3e-10)

    def test_zero_factor_is_exact_zero(self) -> None:
        rng = np.random.default_rng(209005)
        weight = rng.normal(size=(16, 16))
        got = m209.compile_recursive_rank_one_control(weight, np.zeros(16), depth=3)
        self.assertTrue(np.array_equal(got.aaaa, np.zeros(16)))
        self.assertTrue(np.array_equal(got.aaab, np.zeros((16, 16))))
        self.assertTrue(np.array_equal(got.aabb, np.zeros((16, 16))))

    def test_frozen_static_prediction(self) -> None:
        prediction = m209.static_prediction(width=256, layers=31, depth=3)
        self.assertEqual(prediction["matmul_calls"], 15)
        self.assertEqual(prediction["matmul_bill"], 1_167_925_248)
        self.assertEqual(prediction["mirror_copy_bill"], 1_777_664)
        self.assertLess(prediction["matmul_bill"], 1_986_871_472)

    def test_invalid_partition_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            m209.recursive_batched_gram(np.ones((2, 12, 12)), depth=3)
        with self.assertRaises(ValueError):
            m209.recursive_batched_gram(np.ones((2, 8, 7)), depth=3)
        with self.assertRaises(ValueError):
            m209.recursive_batched_gram(np.ones((2, 8, 8)), depth=-1)


if __name__ == "__main__":
    unittest.main()
