"""Pinned FlopScope contract for M210's level fusion."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
M205 = HERE.parent / "m205_rankone_complete_physical_owner"
M209 = HERE.parent / "m209_batched_recursive_gram_control"
for path in (HERE, M205, M209):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:
    import flopscope as flops
    import m205_rankone_complete_physical_owner as m205
    from m209_flopscope_sidecar import LayerInput
    from m210_flopscope_sidecar import (
        allocate_staged_inputs,
        allocate_workspace,
        compile_staged_stack,
        stage_inputs,
    )

    HAVE_FLOPSCOPE = True
except ModuleNotFoundError:
    HAVE_FLOPSCOPE = False


@unittest.skipUnless(HAVE_FLOPSCOPE, "pinned FlopScope runtime is required")
class M210NativeContractTests(unittest.TestCase):
    def _records(self):
        rng = np.random.default_rng(210101)
        return [
            LayerInput(
                layer=i + 1,
                weight=rng.normal(scale=0.2, size=(8, 8)),
                factor=rng.normal(scale=0.1, size=8),
                producer_epoch=210,
            )
            for i in range(3)
        ]

    def test_small_native_source_and_dispatch_parity(self) -> None:
        records = self._records()
        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            staged = allocate_staged_inputs(layers=3, width=8)
            workspace = allocate_workspace(layers=3, width=8, depth=3)
            stage_inputs(records, staged, expected_epoch=210)
            aaaa, aaab, aabb, gram, _p = compile_staged_stack(
                staged, workspace, depth=3
            )
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 4)
        self.assertEqual(operations["reshape"]["calls"], 4)
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

    def test_parent_layer_binding_remains_fail_closed(self) -> None:
        records = self._records()
        staged = allocate_staged_inputs(layers=3, width=8)
        with self.assertRaises(ValueError):
            stage_inputs(list(reversed(records)), staged, expected_epoch=210)
        records[1] = LayerInput(
            layer=2,
            weight=records[0].weight,
            factor=records[0].factor,
            producer_epoch=210,
        )
        with self.assertRaises(ValueError):
            stage_inputs(records, staged, expected_epoch=210)

    def test_compile_before_stage_is_rejected(self) -> None:
        staged = allocate_staged_inputs(layers=3, width=8)
        workspace = allocate_workspace(layers=3, width=8, depth=3)
        with self.assertRaises(ValueError):
            compile_staged_stack(staged, workspace, depth=3)


if __name__ == "__main__":
    unittest.main()
