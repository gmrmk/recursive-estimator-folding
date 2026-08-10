"""Small generated FlopScope contract for M215's frozen native circuit."""

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
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import flopscope as flops  # noqa: E402
import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
import m215_flopscope_sidecar as native  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402


class M215NativeContractTests(unittest.TestCase):
    def _records(self):
        rng = np.random.Generator(np.random.Philox(215401))
        return [
            LayerInput(
                layer=layer + 1,
                weight=rng.normal(scale=0.2, size=(8, 8)),
                factor=rng.normal(scale=0.15, size=8),
                producer_epoch=215,
            )
            for layer in range(3)
        ]

    def test_native_delta_is_collision_and_output_is_strict_distinct(self):
        records = self._records()
        setup_budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with setup_budget:
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            base_workspace = m212.allocate_workspace(layers=3, width=8, depth=3)
            m212.stage_inputs(records, staged, expected_epoch=215)
            full_outputs = m212.compile_staged_stack(staged, base_workspace, depth=3)
        full = tuple(np.asarray(value).copy() for value in full_outputs[:3])
        receipt = native.issue_full_domain_receipt(staged, base_workspace, full_outputs)

        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            collision_workspace = native.allocate_collision_workspace(layers=3, width=8)
            strict = native.subtract_collisions_inplace(
                staged,
                base_workspace,
                collision_workspace,
                receipt,
                depth=3,
            )
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 5)
        self.assertEqual(operations["reshape"]["calls"], 4)

        strict_arrays = tuple(np.asarray(value) for value in strict)
        for layer, record in enumerate(records):
            expected_collision = native.numpy_collision_oracle(record.weight, record.factor)
            delta = m205.Source211(
                full[0][layer] - strict_arrays[0][layer],
                full[1][layer] - strict_arrays[1][layer],
                full[2][layer] - strict_arrays[2][layer],
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(delta, expected_collision), 2e-9
            )

            table = m205.rank_one_control_table(record.factor)
            for i in range(table.shape[0]):
                for j in range(table.shape[1]):
                    for k in range(table.shape[2]):
                        if len({i, j, k}) < 3:
                            table[i, j, k] = 0.0
            expected_strict = m205.brute_complete_source(record.weight, table)
            actual_strict = m205.Source211(
                strict_arrays[0][layer], strict_arrays[1][layer], strict_arrays[2][layer]
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(actual_strict, expected_strict), 2e-9
            )

    def test_binding_and_receipt_fail_closed(self):
        records = self._records()
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            base_workspace = m212.allocate_workspace(layers=3, width=8, depth=3)
            collision_workspace = native.allocate_collision_workspace(layers=3, width=8)
            m212.stage_inputs(records, staged, expected_epoch=215)
            outputs = m212.compile_staged_stack(staged, base_workspace, depth=3)
        receipt = native.issue_full_domain_receipt(staged, base_workspace, outputs)
        object.__setattr__(receipt, "producer_epoch", 999)
        with self.assertRaises(ValueError):
            native.subtract_collisions_inplace(
                staged, base_workspace, collision_workspace, receipt, depth=3
            )

    def test_allocation_ledger_includes_every_still_live_m212_array(self):
        with flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0):
            staged = m212.allocate_staged_inputs(layers=31, width=256)
            base_workspace = m212.allocate_workspace(layers=31, width=256, depth=3)
            collision_workspace = native.allocate_collision_workspace(layers=31, width=256)
            ledger = native.allocation_ledger(staged, base_workspace, collision_workspace)
        self.assertIn("p2", ledger["arrays"])
        self.assertIn("rho_p", ledger["arrays"])
        self.assertEqual(ledger["incremental_collision_mib"], 62.0)
        self.assertEqual(ledger["persistent_mib_visible_to_m215"], 164.08203125)


if __name__ == "__main__":
    unittest.main()
