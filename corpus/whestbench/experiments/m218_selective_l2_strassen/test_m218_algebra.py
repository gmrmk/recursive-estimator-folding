"""Generated-only algebra gates for frozen M218."""

from __future__ import annotations

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
import m218_selective_l2_strassen as m218  # noqa: E402


class M218AlgebraTests(unittest.TestCase):
    def test_l2_integer_products_equal_direct_matmul_bit_exactly(self):
        for width in (4, 8, 12):
            rng = np.random.Generator(np.random.Philox(218100 + width))
            left = rng.integers(-3, 4, size=(3, width, width)).astype(np.float64)
            right = rng.integers(-3, 4, size=(3, width, width)).astype(np.float64)
            actual = m218.strassen_l2_numpy(left, right)
            self.assertTrue(np.array_equal(actual, left @ right))

    def test_ae_and_collision_source_match_m215_at_generated_widths(self):
        worst_ae = 0.0
        worst_source = 0.0
        for width in (4, 8, 12):
            rng = np.random.Generator(np.random.Philox(218200 + width))
            weight = rng.normal(scale=0.35, size=(width, width))
            factor = rng.normal(scale=0.2, size=width)
            actual_a, actual_e = m218.compile_ae_numpy(weight, factor)
            s = factor[:, None] * weight
            reference_a = (s * s).T @ s
            reference_e = (s * s * s).T @ s
            worst_ae = max(
                worst_ae,
                float(np.max(np.abs(actual_a - reference_a))),
                float(np.max(np.abs(actual_e - reference_e))),
            )

            actual_source = m218.compile_collision_source_numpy(weight, factor)
            reference_source = m215.compile_rank_one_collision_source_numpy(weight, factor)
            error = m205.source_max_abs_difference(actual_source, reference_source)
            scale = max(
                float(np.max(np.abs(reference_source.aaaa))),
                float(np.max(np.abs(reference_source.aaab))),
                float(np.max(np.abs(reference_source.aabb))),
            )
            self.assertLessEqual(error, 2e-9 * (1.0 + scale))
            worst_source = max(worst_source, error)
        self.assertLessEqual(worst_ae, 2e-9)
        self.assertLessEqual(worst_source, 2e-9)

    def test_permutation_gauge_and_zero_factor_contracts_survive(self):
        width = 8
        rng = np.random.Generator(np.random.Philox(218301))
        weight = rng.normal(scale=0.3, size=(width, width))
        factor = rng.normal(scale=0.2, size=width)
        baseline = m218.compile_collision_source_numpy(weight, factor)

        permutation = rng.permutation(width)
        permuted = m218.compile_collision_source_numpy(
            weight[permutation], factor[permutation]
        )
        self.assertLessEqual(m205.source_max_abs_difference(baseline, permuted), 2e-9)

        gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
        gauged = m218.compile_collision_source_numpy(
            weight / gauge[:, None], factor * gauge
        )
        self.assertLessEqual(m205.source_max_abs_difference(baseline, gauged), 2e-9)

        zero = m218.compile_collision_source_numpy(weight, np.zeros(width))
        self.assertTrue(np.array_equal(zero.aaaa, np.zeros_like(zero.aaaa)))
        self.assertTrue(np.array_equal(zero.aaab, np.zeros_like(zero.aaab)))
        self.assertTrue(np.array_equal(zero.aabb, np.zeros_like(zero.aabb)))

    def test_mutation_is_selective_and_contains_no_cubic_compiler(self):
        source = inspect.getsource(m218.compile_collision_source_numpy)
        self.assertIn("compile_ae_numpy", source)
        self.assertNotIn("for i in range", source)
        self.assertNotIn("(width, width, width)", source)
        self.assertNotIn("levels=3", inspect.getsource(m218.strassen_l2_numpy))

    def test_frozen_documents_exist_and_no_response_runner_exists(self):
        self.assertTrue((HERE / "M218_PREDECLARATION_20260809.md").exists())
        self.assertTrue((HERE / "M218_FROZEN_MANIFEST_20260809.json").exists())
        self.assertFalse((HERE / "run_m218_source_variance.py").exists())


if __name__ == "__main__":
    unittest.main()
