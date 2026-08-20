"""Small generated FlopScope contract for M218."""

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
import m215_rankone_collision_correction as m215_numpy  # noqa: E402
from m215_flopscope_sidecar import issue_full_domain_receipt  # noqa: E402
import m218_flopscope_sidecar as m218  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402


class M218NativeContractTests(unittest.TestCase):
    def _records(self):
        rng = np.random.Generator(np.random.Philox(218401))
        return [
            LayerInput(
                layer=layer + 1,
                weight=rng.normal(scale=0.2, size=(8, 8)),
                factor=rng.normal(scale=0.15, size=8),
                producer_epoch=218,
            )
            for layer in range(3)
        ]

    def test_selective_native_source_matches_m215_and_frozen_call_schedule(self):
        records = self._records()
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            base = m212.allocate_workspace(layers=3, width=8, depth=3)
            m212.stage_inputs(records, staged, expected_epoch=218)
            full_outputs = m212.compile_staged_stack(staged, base, depth=3)
        receipt = issue_full_domain_receipt(staged, base, full_outputs)

        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            workspace = m218.allocate_strassen_collision_workspace(layers=3, width=8)
            strict = m218.subtract_collisions_strassen_inplace(
                staged, base, workspace, receipt, d_depth=3
            )
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 6)
        self.assertEqual(operations["reshape"]["calls"], 4)
        self.assertEqual(operations["copyto"]["calls"], 81)
        self.assertEqual(operations["add"]["calls"], 51)
        self.assertEqual(operations["subtract"]["calls"], 20)
        self.assertEqual(operations["multiply"]["calls"], 16)
        self.assertEqual(operations["sum"]["calls"], 1)

        arrays = tuple(np.asarray(value) for value in strict)
        for layer, record in enumerate(records):
            full = m205.compile_lifted_rank_one_control(record.weight, record.factor)
            collision = m215_numpy.compile_rank_one_collision_source_numpy(
                record.weight, record.factor
            )
            reference = m215_numpy.subtract_source(full, collision)
            actual = m205.Source211(arrays[0][layer], arrays[1][layer], arrays[2][layer])
            error = m205.source_max_abs_difference(actual, reference)
            scale = max(
                float(np.max(np.abs(reference.aaaa))),
                float(np.max(np.abs(reference.aaab))),
                float(np.max(np.abs(reference.aabb))),
            )
            self.assertLessEqual(error, 2e-9 * (1.0 + scale))

    def test_binding_fails_closed(self):
        records = self._records()
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            base = m212.allocate_workspace(layers=3, width=8, depth=3)
            workspace = m218.allocate_strassen_collision_workspace(layers=3, width=8)
            m212.stage_inputs(records, staged, expected_epoch=218)
            outputs = m212.compile_staged_stack(staged, base, depth=3)
        receipt = issue_full_domain_receipt(staged, base, outputs)
        object.__setattr__(receipt, "producer_epoch", 999)
        with self.assertRaises(ValueError):
            m218.subtract_collisions_strassen_inplace(
                staged, base, workspace, receipt, d_depth=3
            )

    def test_target_allocation_is_complete_and_contains_no_rank3_coefficient(self):
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=31, width=256)
            base = m212.allocate_workspace(layers=31, width=256, depth=3)
            workspace = m218.allocate_strassen_collision_workspace(layers=31, width=256)
            ledger = m218.allocation_ledger(staged, base, workspace)
        self.assertEqual(ledger["incremental_m218_mib"], 231.53125)
        self.assertEqual(ledger["persistent_mib_visible_to_m218"], 333.61328125)
        self.assertEqual(ledger["rank3_coefficient_arrays"], 0)
        self.assertEqual(ledger["strassen_depth"], 2)


if __name__ == "__main__":
    unittest.main()
