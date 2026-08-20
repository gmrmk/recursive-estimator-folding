"""Batch-axis fused L3 leaf bank (M169 lever) over the FROZEN M116 partition.

The frozen operator `inplace_l3.InplaceL3Winograd` is imported read-only and
SUBCLASSED.  `_pack_left`, `_pack_right`, `_fold` are inherited verbatim; they
are shape-generic over leading batch axes, so the fused arm's arithmetic is the
frozen arithmetic by construction.

ARM REF   : group=1  -> 16 dispatches/layer (the consumed M116c 512-call shape)
ARM FUSED : group=4  -> 5 dispatches/layer (160 calls total)

Both arms use the identical 4,096-row block partition, so the float32
association per row is identical and bitwise parity is the correct gate.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

FROZEN_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\scorefloor_generation\m116c_inplace_l3_b4096_draft"
)
if str(FROZEN_DIR) not in sys.path:
    sys.path.insert(0, str(FROZEN_DIR))

from cost_model import BLOCK_ROWS, TILE, dispatch  # noqa: E402  (frozen, read-only)
from inplace_l3 import InplaceL3Winograd, UnsupportedInplaceShape  # noqa: E402

LEAF = 32


class GroupedInplaceL3(InplaceL3Winograd):
    """Frozen L3 arithmetic with the row-block index as a leading batch axis."""

    def __init__(self, *, group: int, block_rows: int = BLOCK_ROWS, backend: Any = np) -> None:
        if group <= 0 or block_rows <= 0 or block_rows % 8:
            raise ValueError("group must be positive and block_rows divisible by eight")
        self.group = int(group)
        self.block_rows = int(block_rows)
        self.max_m = 1 << 62
        self.xp = backend
        g, b = self.group, self.block_rows
        self.outer_scratch = backend.empty((g, 7, b // 2, 128), dtype=np.float32)
        self.middle_scratch = backend.empty((g, 7, 7, b // 4, 64), dtype=np.float32)
        self.leaf_left = backend.empty((g, 7, 7, 7, b // 8, LEAF), dtype=np.float32)
        self.leaf_products = backend.empty((g, 7, 7, 7, b // 8, LEAF), dtype=np.float32)
        self.outer_right = backend.empty((7, 128, 128), dtype=np.float32)
        self.middle_right = backend.empty((7, 7, 64, 64), dtype=np.float32)
        self.leaf_right = backend.empty((7, 7, 7, LEAF, LEAF), dtype=np.float32)
        self.last_strategy = "unrun"
        self.last_core_calls = 0
        self.last_total_matmul_calls = 0

    def expected_workspace_bytes(self) -> int:  # type: ignore[override]
        return 4 * (3_976 * self.group * self.block_rows + 666_624)

    def _process_group(self, block: Any, leaf_right: Any, g: int, rows: int) -> None:
        """`block` has shape (g, rows, 256); rows must be divisible by eight."""
        hm, qm, em = rows // 2, rows // 4, rows // 8
        outer_left = self.outer_scratch[:g, :, :hm, :]
        middle_left = self.middle_scratch[:g, :, :, :qm, :]
        leaf_left = self.leaf_left[:g, :, :, :, :em, :]
        products = self.leaf_products[:g, :, :, :, :em, :]

        # capture every affine function of the group before any output write
        self._pack_left(self.xp, block, outer_left)
        self._pack_left(self.xp, outer_left, middle_left)
        self._pack_left(self.xp, middle_left, leaf_left)
        self.xp.matmul(leaf_left, leaf_right, out=products)

        # the source rows are now dead: reuse the dead hierarchy, then overwrite
        middle_products = self.middle_scratch[:g, :, :, :qm, :]
        self._fold(self.xp, products, middle_products)
        outer_products = self.outer_scratch[:g, :, :hm, :]
        self._fold(self.xp, middle_products, outer_products)
        self._fold(self.xp, outer_products, block)

    def multiply_inplace(self, left: Any, right: Any, **_: Any) -> Any:  # type: ignore[override]
        self.last_core_calls = 0
        self.last_total_matmul_calls = 0
        if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
            self.last_strategy = "unsupported"
            raise UnsupportedInplaceShape("incompatible 2-D product")
        m, k = (int(v) for v in left.shape)
        n = int(right.shape[1])
        if left.dtype != np.float32 or right.dtype != np.float32:
            self.last_strategy = "unsupported"
            raise UnsupportedInplaceShape("in-place draft requires float32 operands")
        flags = getattr(left, "flags", None)
        if flags is None or not flags.c_contiguous or not flags.writeable:
            self.last_strategy = "unsupported"
            raise UnsupportedInplaceShape("left must be writable C-contiguous storage")
        if not self.ownership_ok(left, right):
            self.last_strategy = "unsupported"
            raise ValueError("left, right, and every owned buffer must be disjoint")
        decision = dispatch(m, k, n)
        if not decision.executable:
            self.last_strategy = "unsupported"
            raise UnsupportedInplaceShape(decision.reason)

        self.last_strategy = decision.strategy
        leaf_right = self._pack_right_hierarchy(right)
        calls = 0
        for view, g, rows in self.bind(left):
            self._process_group(view, leaf_right, g, rows)
            calls += 1
        self.last_core_calls = calls
        self.last_total_matmul_calls = calls
        return left

    def bind(self, left: Any) -> list[tuple[Any, int, int]]:
        """Cache the (g, rows, 256) grouped views of `left`, built ONCE.

        `reshape` is billed by FlopScope as a full elementwise pass, and the
        frozen design forbids reshape in the hot path, so the view plan is
        constructed at setup and reused for every layer (the caller-owned state
        array is the same object at every depth).
        """
        bound = getattr(self, "_bound", None)
        if bound is not None and bound[0] is left:
            return bound[1]
        plan: list[tuple[Any, int, int]] = []
        m, b, start = int(left.shape[0]), self.block_rows, 0
        while start < m:
            remaining = m - start
            if remaining >= b:
                g, rows = min(self.group, remaining // b), b
            else:  # final short tail keeps the frozen partition's tail block
                g, rows = 1, remaining
            span = g * rows
            plan.append((left[start:start + span, :].reshape(g, rows, TILE), g, rows))
            start += span
        self._bound = (left, plan)
        return plan

    def dispatch_plan(self, m: int) -> list[tuple[int, int]]:
        """(group, rows) per dispatch, for predeclaration/audit without running."""
        plan: list[tuple[int, int]] = []
        b, start = self.block_rows, 0
        while start < m:
            remaining = m - start
            if remaining >= b:
                g, rows = min(self.group, remaining // b), b
            else:
                g, rows = 1, remaining
            plan.append((g, rows))
            start += g * rows
        return plan
