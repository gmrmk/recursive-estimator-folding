"""Real-FlopScope synthetic parity and analytical-bill contracts for G4.

Only hand-constructed matrices are used.  View binding and workspace
allocation occur before the hot BudgetContext, matching the declared setup
boundary; their eventual complete setup charge remains an unearned package
gate and is not hidden by this component test.
"""

from __future__ import annotations

import os
import importlib.util
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
sys.path.insert(0, str(HERE / "candidate_source"))

from cost_model import owned_batched_candidate_bill  # noqa: E402

# The NumPy-only fixtures deliberately replace the candidate module's ``fnp``
# global.  Load a private module instance here so the complete unittest suite is
# order-independent and this gate always exercises the real pinned backend.
_spec = importlib.util.spec_from_file_location(
    "g4_rbw_flopscope_isolated",
    HERE / "candidate_source" / "row_blocked_winograd.py",
)
assert _spec is not None and _spec.loader is not None
_rbw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rbw)
GroupedRowBlockedBatchedWinograd = _rbw.GroupedRowBlockedBatchedWinograd
RowBlockedBatchedWinograd = _rbw.RowBlockedBatchedWinograd


ROWS = 304
WIDTH = 256  # preserve the production physical row stride
BLOCK_ROWS = 64
GROUP = 4
BUDGET = 10**10


class FlopScopeSyntheticContracts(unittest.TestCase):
    def _run(self, k: int, n: int, *, alias: bool):
        rng = np.random.default_rng(40_000 + 101 * k + n)
        left_np = rng.standard_normal((ROWS, WIDTH), dtype=np.float32)
        right_np = rng.standard_normal((k, n), dtype=np.float32)

        parent_left = fnp.asarray(left_np.copy())
        child_left = fnp.asarray(left_np.copy())
        right_parent = fnp.asarray(right_np.copy())
        right_child = fnp.asarray(right_np.copy())
        if alias:
            parent_out = parent_left
            child_out = child_left
        else:
            sentinel = np.full((ROWS, WIDTH), np.float32(-17.0))
            parent_out = fnp.asarray(sentinel.copy())
            child_out = fnp.asarray(sentinel.copy())

        parent = RowBlockedBatchedWinograd(ROWS, WIDTH, BLOCK_ROWS)
        child = GroupedRowBlockedBatchedWinograd(
            ROWS, WIDTH, BLOCK_ROWS, group=GROUP
        )
        child.bind(child_left, child_out)

        with flops.BudgetContext(BUDGET, quiet=True) as parent_ctx:
            expected = parent.multiply(
                parent_left[:, :k], right_parent, out=parent_out[:, :n]
            )
        with flops.BudgetContext(BUDGET, quiet=True) as child_ctx:
            actual = child.multiply(
                child_left[:, :k], right_child, out=child_out[:, :n]
            )

        expected_words = np.asarray(expected).view(np.uint32)
        actual_words = np.asarray(actual).view(np.uint32)
        self.assertTrue(np.array_equal(expected_words, actual_words))
        selected = owned_batched_candidate_bill(ROWS, k, n).total
        self.assertEqual(int(parent_ctx.flops_used), selected)
        self.assertEqual(int(child_ctx.flops_used), selected)

    def test_real_backend_even_odd_direct_and_nonalias(self):
        for k, n, alias in (
            (16, 16, True),
            (16, 15, True),
            (15, 16, True),
            (16, 12, False),
            (16, 24, True),
        ):
            with self.subTest(k=k, n=n, alias=alias):
                self._run(k, n, alias=alias)


if __name__ == "__main__":
    unittest.main()
