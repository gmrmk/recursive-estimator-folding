"""Hostile layer-binding and small-shape FlopScope gates for M209."""

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

try:
    import flopscope as flops
    import m205_rankone_complete_physical_owner as m205
    from m209_flopscope_sidecar import (
        LayerInput,
        allocate_staged_inputs,
        allocate_workspace,
        compile_staged_stack,
        stage_inputs,
    )

    HAVE_FLOPSCOPE = True
except ModuleNotFoundError:
    HAVE_FLOPSCOPE = False


@unittest.skipUnless(HAVE_FLOPSCOPE, "pinned FlopScope runtime is required")
class M209NativeContractTests(unittest.TestCase):
    def _records(self, *, layers: int = 3, width: int = 8, seed: int = 209101):
        rng = np.random.default_rng(seed)
        weights = [rng.normal(scale=0.2, size=(width, width)) for _ in range(layers)]
        factors = [rng.normal(scale=0.1, size=width) for _ in range(layers)]
        return [
            LayerInput(layer=i + 1, weight=w, factor=u, producer_epoch=17)
            for i, (w, u) in enumerate(zip(weights, factors, strict=True))
        ]

    def test_small_native_stack_matches_dense_sources(self) -> None:
        records = self._records()
        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            staged = allocate_staged_inputs(layers=3, width=8)
            workspace = allocate_workspace(layers=3, width=8)
            stage_inputs(records, staged, expected_epoch=17)
            aaaa, aaab, aabb, gram, _p = compile_staged_stack(staged, workspace, depth=3)
        self.assertEqual(budget.summary_dict()["operations"]["matmul"]["calls"], 15)
        for layer, record in enumerate(records):
            expected = m205.compile_lifted_rank_one_control(record.weight, record.factor)
            self.assertLessEqual(
                float(np.max(np.abs(np.asarray(aaaa[layer]) - expected.aaaa))), 2e-10
            )
            self.assertLessEqual(
                float(np.max(np.abs(np.asarray(aaab[layer]) - expected.aaab))), 2e-10
            )
            self.assertLessEqual(
                float(np.max(np.abs(np.asarray(aabb[layer]) - expected.aabb))), 2e-10
            )
        self.assertTrue(np.array_equal(np.asarray(gram), np.swapaxes(np.asarray(gram), 1, 2)))

    def test_reorder_duplicate_epoch_and_float32_are_rejected(self) -> None:
        records = self._records()
        staged = allocate_staged_inputs(layers=3, width=8)
        with self.assertRaises(ValueError):
            stage_inputs(list(reversed(records)), staged, expected_epoch=17)
        duplicate = list(records)
        duplicate[1] = LayerInput(
            layer=2,
            weight=duplicate[0].weight,
            factor=duplicate[0].factor,
            producer_epoch=17,
        )
        with self.assertRaises(ValueError):
            stage_inputs(duplicate, staged, expected_epoch=17)
        wrong_epoch = list(records)
        wrong_epoch[1] = LayerInput(
            layer=2,
            weight=wrong_epoch[1].weight,
            factor=wrong_epoch[1].factor,
            producer_epoch=99,
        )
        with self.assertRaises(ValueError):
            stage_inputs(wrong_epoch, staged, expected_epoch=17)
        low_precision = list(records)
        low_precision[2] = LayerInput(
            layer=3,
            weight=low_precision[2].weight.astype(np.float32),
            factor=low_precision[2].factor,
            producer_epoch=17,
        )
        with self.assertRaises(ValueError):
            stage_inputs(low_precision, staged, expected_epoch=17)

    def test_unstaged_compile_is_rejected(self) -> None:
        staged = allocate_staged_inputs(layers=3, width=8)
        workspace = allocate_workspace(layers=3, width=8)
        with self.assertRaises(ValueError):
            compile_staged_stack(staged, workspace, depth=3)


if __name__ == "__main__":
    unittest.main()
