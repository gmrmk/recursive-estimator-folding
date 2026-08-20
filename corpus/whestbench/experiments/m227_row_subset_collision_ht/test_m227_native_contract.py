"""Generated-only FlopScope contract for the frozen M227 native circuit."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m205_rankone_complete_physical_owner",
    BASE / "m209_batched_recursive_gram_control",
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import flopscope as flops  # noqa: E402
import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
import m215_rankone_collision_correction as m215  # noqa: E402
import m227_flopscope_sidecar as native  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402


class M227NativeContractTests(unittest.TestCase):
    def _records(self, layers: int = 3, width: int = 8):
        rng = np.random.Generator(np.random.Philox(227401))
        return [
            LayerInput(
                layer=layer + 1,
                weight=rng.normal(scale=0.2, size=(width, width)),
                factor=rng.normal(scale=0.15, size=width),
                producer_epoch=227,
            )
            for layer in range(layers)
        ]

    def test_native_draw_matches_numpy_row_oracle_and_has_frozen_call_shape(self):
        records = self._records()
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            base = m212.allocate_workspace(layers=3, width=8, depth=3)
            m212.stage_inputs(records, staged, expected_epoch=227)
            full_outputs = m212.compile_staged_stack(staged, base, depth=3)
        full = tuple(np.asarray(value).copy() for value in full_outputs[:3])
        receipt = native.issue_full_domain_receipt(staged, base, full_outputs)

        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            workspace = native.allocate_row_workspace(layers=3, width=8, subset_rows=1)
            strict, row_receipt = native.subtract_row_sketch_inplace(
                staged,
                base,
                workspace,
                receipt,
                seed=227411,
                subset_rows=1,
            )
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 2)
        self.assertEqual(operations["multiply"]["calls"], 16)
        self.assertEqual(operations["add"]["calls"], 9)
        self.assertEqual(operations["sum"]["calls"], 1)
        self.assertEqual(operations["copyto"]["calls"], 1)
        self.assertEqual(operations["argsort"]["calls"], 1)
        self.assertEqual(operations["take_along_axis"]["calls"], 1)
        self.assertNotIn("reshape", operations)

        strict_arrays = tuple(np.asarray(value) for value in strict)
        for layer, record in enumerate(records):
            expected_collision = native.numpy_row_oracle(
                record.weight, record.factor, row_receipt.selected[layer]
            )
            delta = m205.Source211(
                full[0][layer] - strict_arrays[0][layer],
                full[1][layer] - strict_arrays[1][layer],
                full[2][layer] - strict_arrays[2][layer],
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(delta, expected_collision), 2e-9
            )

    def test_target_allocation_and_exact_frozen_bill(self):
        records = self._records(layers=31, width=256)
        with flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0):
            staged = m212.allocate_staged_inputs()
            base = m212.allocate_workspace(depth=3)
            m212.stage_inputs(records, staged, expected_epoch=227)
            outputs = m212.compile_staged_stack(staged, base, depth=3)
        receipt = native.issue_full_domain_receipt(staged, base, outputs)
        budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        with budget:
            workspace = native.allocate_row_workspace()
            ledger = native.allocation_ledger(staged, base, workspace)
            native.subtract_row_sketch_inplace(
                staged, base, workspace, receipt, seed=227700001, subset_rows=32
            )
        self.assertEqual(int(budget.flops_used), 865_484_288)
        self.assertEqual(ledger["incremental_persistent_mib"], 36.873046875)
        self.assertEqual(ledger["m212_m227_persistent_mib"], 138.955078125)

    def test_epoch_and_receipt_binding_fail_closed(self):
        records = self._records()
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            base = m212.allocate_workspace(layers=3, width=8, depth=3)
            workspace = native.allocate_row_workspace(layers=3, width=8, subset_rows=1)
            m212.stage_inputs(records, staged, expected_epoch=227)
            outputs = m212.compile_staged_stack(staged, base, depth=3)
        receipt = native.issue_full_domain_receipt(staged, base, outputs)
        object.__setattr__(receipt, "producer_epoch", 999)
        with self.assertRaises(ValueError):
            native.subtract_row_sketch_inplace(
                staged, base, workspace, receipt, seed=227499, subset_rows=1
            )


if __name__ == "__main__":
    unittest.main()
