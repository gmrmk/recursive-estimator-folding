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
    HAVE_FLOPSCOPE = True
except ModuleNotFoundError:
    HAVE_FLOPSCOPE = False

if HAVE_FLOPSCOPE:
    import m205_rankone_complete_physical_owner as m205
    from m209_flopscope_sidecar import LayerInput
    from m211_flopscope_sidecar import (
        allocate_staged_inputs,
        allocate_workspace,
        allocation_ledger,
        compile_staged_stack,
        stage_inputs,
    )


@unittest.skipUnless(HAVE_FLOPSCOPE, "pinned FlopScope runtime is required")
class M211ExplicitMemoryContractTests(unittest.TestCase):
    def _records(self):
        rng = np.random.default_rng(211101)
        return [
            LayerInput(
                layer=i + 1,
                weight=rng.normal(scale=0.2, size=(8, 8)),
                factor=rng.normal(scale=0.1, size=8),
                producer_epoch=211,
            )
            for i in range(3)
        ]

    def test_explicit_contiguous_operands_and_source_parity(self):
        records = self._records()
        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            staged = allocate_staged_inputs(layers=3, width=8)
            workspace = allocate_workspace(layers=3, width=8, depth=3)
            stage_inputs(records, staged, expected_epoch=211)
            outputs = compile_staged_stack(staged, workspace, depth=3)
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 4)
        self.assertEqual(operations["reshape"]["calls"], 4)
        for pack in workspace.left_packs + workspace.right_packs:
            self.assertTrue(np.asarray(pack).flags.c_contiguous)
        aaaa, aaab, aabb, gram, _p = map(np.asarray, outputs)
        self.assertTrue(np.array_equal(gram, np.swapaxes(gram, 1, 2)))
        self.assertTrue(np.array_equal(aabb, np.swapaxes(aabb, 1, 2)))
        for layer, record in enumerate(records):
            expected = m205.compile_lifted_rank_one_control(record.weight, record.factor)
            self.assertLessEqual(float(np.max(np.abs(aaaa[layer] - expected.aaaa))), 2e-10)
            self.assertLessEqual(float(np.max(np.abs(aaab[layer] - expected.aaab))), 2e-10)
            self.assertLessEqual(float(np.max(np.abs(aabb[layer] - expected.aabb))), 2e-10)

    def test_all_owned_buffers_are_ledgered(self):
        staged = allocate_staged_inputs(layers=3, width=8)
        workspace = allocate_workspace(layers=3, width=8, depth=3)
        ledger = allocation_ledger(staged, workspace)
        names = set(ledger["arrays"])
        self.assertIn("transpose_scratch", names)
        for level in range(4):
            self.assertIn(f"left_pack_{level}", names)
            self.assertIn(f"right_pack_{level}", names)
        self.assertEqual(ledger["untracked_full_plane_temporaries"], 0)

    def test_binding_remains_fail_closed(self):
        records = self._records()
        staged = allocate_staged_inputs(layers=3, width=8)
        with self.assertRaises(ValueError):
            stage_inputs(list(reversed(records)), staged, expected_epoch=211)
        workspace = allocate_workspace(layers=3, width=8, depth=3)
        with self.assertRaises(ValueError):
            compile_staged_stack(staged, workspace, depth=3)


if __name__ == "__main__":
    unittest.main()
