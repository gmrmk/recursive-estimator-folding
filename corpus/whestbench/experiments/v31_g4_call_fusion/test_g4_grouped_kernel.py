"""Synthetic contracts for the zero-evidence V31-G4 grouped L1 kernel.

These tests use only deterministic hand-constructed matrices.  They do not
construct a benchmark MLP, read truth/scorer data, or exercise a submission.
"""

from __future__ import annotations

import sys
import unittest
import os
from pathlib import Path

for _name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_name] = "1"

import numpy as np


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "candidate_source"
sys.path.insert(0, str(CANDIDATE))

import row_blocked_winograd as rbw  # noqa: E402


# Both kernels use the exact same NumPy backend in this synthetic gate.  The
# later FlopScope/backend fixture is a separate, stricter integration gate.
rbw.fnp = np

GroupedRowBlockedBatchedWinograd = rbw.GroupedRowBlockedBatchedWinograd
RowBlockedBatchedWinograd = rbw.RowBlockedBatchedWinograd
grouped_row_blocked_bill_identity = rbw.grouped_row_blocked_bill_identity


ROWS = 304  # four 64-row blocks plus one 48-row frozen remainder
WIDTH = 256  # preserve the production physical row stride
BLOCK_ROWS = 64
GROUP = 4


class GroupedKernelContracts(unittest.TestCase):
    def _operands(self, k: int, n: int, seed: int = 3104):
        rng = np.random.default_rng(seed + 101 * k + n)
        storage = rng.standard_normal((ROWS, WIDTH), dtype=np.float32)
        right = rng.standard_normal((k, n), dtype=np.float32)
        return storage, right

    def _compare(self, k: int, n: int, *, alias: bool) -> tuple[object, object]:
        original, right = self._operands(k, n)
        parent_left = original.copy()
        child_left = original.copy()
        if alias:
            parent_out = parent_left
            child_out = child_left
        else:
            parent_out = np.full((ROWS, WIDTH), np.float32(-13.0))
            child_out = parent_out.copy()

        parent = RowBlockedBatchedWinograd(ROWS, WIDTH, BLOCK_ROWS)
        child = GroupedRowBlockedBatchedWinograd(
            ROWS, WIDTH, BLOCK_ROWS, group=GROUP
        )
        child.bind(child_left, child_out)

        expected = parent.multiply(
            parent_left[:, :k], right, out=parent_out[:, :n]
        )
        actual = child.multiply(
            child_left[:, :k], right, out=child_out[:, :n]
        )

        self.assertTrue(
            np.array_equal(expected.view(np.uint32), actual.view(np.uint32)),
            msg=f"word mismatch for k={k}, n={n}, alias={alias}",
        )
        self.assertEqual(
            rbw.owned_batched_candidate_bill(ROWS, k, n).total,
            child.last_selected_bill,
        )
        return parent, child

    def test_group_plan_preserves_four_full_blocks_and_short_remainder(self):
        child = GroupedRowBlockedBatchedWinograd(
            ROWS, WIDTH, BLOCK_ROWS, group=GROUP
        )
        self.assertEqual(child.dispatch_plan(ROWS), [(4, 64), (1, 48)])

    def test_production_row_partition_includes_exact_3072_remainder(self):
        rows = 64_512
        width = 256
        k, n = 16, 12
        rng = np.random.default_rng(31_3072)
        original = rng.standard_normal((rows, width), dtype=np.float32)
        right = rng.standard_normal((k, n), dtype=np.float32)
        parent_store = original.copy()
        child_store = original.copy()

        parent = RowBlockedBatchedWinograd(rows, width, 4_096)
        child = GroupedRowBlockedBatchedWinograd(
            rows, width, 4_096, group=GROUP
        )
        child.bind(child_store)
        expected = parent.multiply(
            parent_store[:, :k], right, out=parent_store[:, :n]
        )
        actual = child.multiply(
            child_store[:, :k], right, out=child_store[:, :n]
        )
        self.assertTrue(
            np.array_equal(expected.view(np.uint32), actual.view(np.uint32))
        )
        self.assertEqual(parent.last_core_calls, 16)
        self.assertEqual(child.last_core_calls, 5)
        self.assertEqual(
            child.dispatch_plan(rows),
            [(4, 4_096), (4, 4_096), (4, 4_096), (3, 4_096), (1, 3_072)],
        )

    def test_alias_parity_for_less_equal_and_greater_output_width(self):
        # n=8 dispatches direct at this deliberately small geometry; n=12 is
        # the first n<k case selected by the frozen L1 bill.
        for k, n in ((16, 12), (16, 16), (16, 24)):
            with self.subTest(k=k, n=n):
                parent, child = self._compare(k, n, alias=True)
                self.assertEqual(parent.last_core_calls, 5)
                self.assertEqual(child.last_core_calls, 2)
                self.assertEqual(child.last_total_matmul_calls, 2)

    def test_nonalias_parity(self):
        parent, child = self._compare(16, 16, alias=False)
        self.assertEqual(parent.last_total_matmul_calls, 5)
        self.assertEqual(child.last_total_matmul_calls, 2)

    def test_odd_output_tail_runs_before_grouped_core_and_matches_parent(self):
        parent, child = self._compare(16, 15, alias=True)
        self.assertEqual(parent.last_core_calls, 5)
        self.assertEqual(parent.last_total_matmul_calls, 10)
        self.assertEqual(child.last_core_calls, 2)
        self.assertEqual(child.last_total_matmul_calls, 4)
        self.assertEqual(child.last_event_order, ("tail", "core", "fold") * 2)

    def test_direct_fallback_retains_parent_counters_and_words(self):
        parent, child = self._compare(15, 16, alias=True)
        self.assertEqual(parent.last_core_calls, 0)
        self.assertEqual(parent.last_total_matmul_calls, 5)
        self.assertEqual(child.last_core_calls, 0)
        self.assertEqual(child.last_total_matmul_calls, 5)

    def test_zero_and_finite_extreme_operands_match_parent_words(self):
        for label, left_value, right_value in (
            ("zero", np.float32(0.0), np.float32(0.0)),
            (
                "finite_extreme",
                np.float32(np.finfo(np.float32).max / 8.0),
                np.float32(np.finfo(np.float32).tiny),
            ),
        ):
            with self.subTest(label=label):
                parent_store = np.full((ROWS, WIDTH), left_value, dtype=np.float32)
                child_store = parent_store.copy()
                right = np.full((16, 16), right_value, dtype=np.float32)
                parent = RowBlockedBatchedWinograd(ROWS, WIDTH, BLOCK_ROWS)
                child = GroupedRowBlockedBatchedWinograd(
                    ROWS, WIDTH, BLOCK_ROWS, group=GROUP
                )
                child.bind(child_store)
                expected = parent.multiply(
                    parent_store[:, :16], right, out=parent_store[:, :16]
                )
                actual = child.multiply(
                    child_store[:, :16], right, out=child_store[:, :16]
                )
                self.assertTrue(
                    np.array_equal(expected.view(np.uint32), actual.view(np.uint32))
                )

    def test_zero_width_replays_parent_exception_before_grouped_core(self):
        for k, n in ((0, 16), (16, 0)):
            with self.subTest(k=k, n=n):
                left_parent = np.zeros((ROWS, WIDTH), dtype=np.float32)
                left_child = left_parent.copy()
                right = np.zeros((k, n), dtype=np.float32)
                parent = RowBlockedBatchedWinograd(ROWS, WIDTH, BLOCK_ROWS)
                child = GroupedRowBlockedBatchedWinograd(
                    ROWS, WIDTH, BLOCK_ROWS, group=GROUP
                )
                child.bind(left_child)
                with self.assertRaises(ValueError) as parent_error:
                    parent.multiply(
                        left_parent[:, :k], right, out=left_parent[:, :n]
                    )
                with self.assertRaises(ValueError) as child_error:
                    child.multiply(
                        left_child[:, :k], right, out=left_child[:, :n]
                    )
                self.assertEqual(str(child_error.exception), str(parent_error.exception))
                self.assertEqual(child.last_core_calls, 0)
                self.assertEqual(child.last_total_matmul_calls, 0)

    def test_grouped_bill_identity_changes_calls_not_arithmetic(self):
        even = grouped_row_blocked_bill_identity(
            ROWS, 16, 16, block_rows=BLOCK_ROWS, group=GROUP
        )
        odd = grouped_row_blocked_bill_identity(
            ROWS, 16, 15, block_rows=BLOCK_ROWS, group=GROUP
        )
        direct = grouped_row_blocked_bill_identity(
            ROWS, 15, 16, block_rows=BLOCK_ROWS, group=GROUP
        )
        self.assertEqual(even["core_calls"], 2)
        self.assertEqual(even["total_matmul_calls"], 2)
        self.assertEqual(odd["core_calls"], 2)
        self.assertEqual(odd["total_matmul_calls"], 4)
        self.assertEqual(direct["core_calls"], 5)
        self.assertEqual(direct["runtime_winograd_core_calls"], 0)
        self.assertEqual(direct["total_matmul_calls"], 5)
        for item, k, n in ((even, 16, 16), (odd, 16, 15), (direct, 15, 16)):
            self.assertEqual(
                item["selected_bill"],
                rbw.owned_batched_candidate_bill(ROWS, k, n).total,
            )
            self.assertEqual(
                item,
                rbw.row_blocked_bill_identity(
                    ROWS, k, n, block_rows=BLOCK_ROWS, group=GROUP
                ),
            )

    def test_unbound_or_wrong_storage_is_rejected(self):
        left, right = self._operands(16, 16)
        child = GroupedRowBlockedBatchedWinograd(
            ROWS, WIDTH, BLOCK_ROWS, group=GROUP
        )
        with self.assertRaisesRegex(RuntimeError, "bound"):
            child.multiply(left[:, :16], right, out=left[:, :16])

        child.bind(left)
        alien = left.copy()
        with self.assertRaisesRegex(ValueError, "bound storage"):
            child.multiply(alien[:, :16], right, out=alien[:, :16])


if __name__ == "__main__":
    unittest.main()
