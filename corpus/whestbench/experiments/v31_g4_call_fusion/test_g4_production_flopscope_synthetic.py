"""Production-row FlopScope parity on deterministic hand matrices only.

This fixture exercises the exact 64,512-row partition, the 3,072-row
remainder, the implicit group-prefix RHS broadcast, alias capture, and the
odd-tail chronology.  It constructs no MLP and reads no truth or scorer.
"""

from __future__ import annotations

import gc
import importlib.util
import os
import sys
import unittest
from pathlib import Path

for _name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_name] = "1"

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "candidate_source"
sys.path.insert(0, str(CANDIDATE))

_spec = importlib.util.spec_from_file_location(
    "g4_rbw_production_flopscope_isolated",
    CANDIDATE / "row_blocked_winograd.py",
)
assert _spec is not None and _spec.loader is not None
_rbw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rbw)

GroupedRowBlockedBatchedWinograd = _rbw.GroupedRowBlockedBatchedWinograd
RowBlockedBatchedWinograd = _rbw.RowBlockedBatchedWinograd
owned_batched_candidate_bill = _rbw.owned_batched_candidate_bill


ROWS = 64_512
WIDTH = 256
BLOCK_ROWS = 4_096
GROUP = 4
BUDGET = 20_000_000_000
PLAN = [(4, 4_096), (4, 4_096), (4, 4_096), (3, 4_096), (1, 3_072)]


class ProductionFlopScopeSyntheticContracts(unittest.TestCase):
    def _run_alias_case(self, k: int, n: int) -> None:
        rng = np.random.default_rng(90_000 + 101 * k + n)
        left_np = rng.standard_normal((ROWS, WIDTH), dtype=np.float32)
        right_np = rng.standard_normal((k, n), dtype=np.float32)

        parent_left = fnp.asarray(left_np.copy())
        right_parent = fnp.asarray(right_np.copy())
        parent = RowBlockedBatchedWinograd(ROWS, WIDTH, BLOCK_ROWS)
        with flops.BudgetContext(BUDGET, quiet=True) as parent_ctx:
            expected = parent.multiply(
                parent_left[:, :k], right_parent, out=parent_left[:, :n]
            )
        expected_words = np.asarray(expected).copy().view(np.uint32)
        parent_total_calls = int(parent.last_total_matmul_calls)
        del expected, parent_left, right_parent, parent
        gc.collect()

        child_left = fnp.asarray(left_np.copy())
        right_child = fnp.asarray(right_np.copy())
        child = GroupedRowBlockedBatchedWinograd(
            ROWS, WIDTH, BLOCK_ROWS, group=GROUP
        )
        child.bind(child_left)
        self.assertEqual(child.dispatch_plan(ROWS), PLAN)
        with flops.BudgetContext(BUDGET, quiet=True) as child_ctx:
            actual = child.multiply(
                child_left[:, :k], right_child, out=child_left[:, :n]
            )
        actual_words = np.asarray(actual).view(np.uint32)

        selected = int(owned_batched_candidate_bill(ROWS, k, n).total)
        self.assertTrue(np.array_equal(expected_words, actual_words))
        self.assertEqual(int(parent_ctx.flops_used), selected)
        self.assertEqual(int(child_ctx.flops_used), selected)
        self.assertEqual(parent_total_calls, 16 * (1 + int(n % 2 == 1)))
        self.assertEqual(child.last_core_calls, 5)
        self.assertEqual(child.last_total_matmul_calls, 5 * (1 + int(n % 2 == 1)))
        if n % 2:
            self.assertEqual(
                child.last_event_order,
                ("tail", "core", "fold") * len(PLAN),
            )
        else:
            self.assertEqual(
                child.last_event_order,
                ("core", "fold") * len(PLAN),
            )

        del actual, child_left, right_child, child, left_np, right_np
        gc.collect()

    def test_production_rows_even_and_odd_l1_match_parent_words_and_bill(self):
        for k, n in ((256, 256), (256, 253)):
            with self.subTest(k=k, n=n):
                self._run_alias_case(k, n)


if __name__ == "__main__":
    unittest.main()
