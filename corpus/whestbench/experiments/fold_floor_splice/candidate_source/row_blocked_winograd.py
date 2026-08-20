"""Fixed-height streaming Batched-B Winograd workspace.

The right operand is packed once.  Row-dependent left operands and products
are streamed through an 8192-row buffer and reconstructed directly into one
full output.  All numerical operations use ``flopscope.numpy``.
"""

from __future__ import annotations

import math
import flopscope.numpy as fnp

from cost_model import batched_candidate_bill, direct_cost


BLOCK_ROWS = 8192


class RowBlockedBatchedWinograd:
    """Exact one-level Winograd with bounded row scratch."""

    def __init__(self, max_m: int, width: int, block_rows: int = BLOCK_ROWS):
        if min(max_m, width, block_rows) <= 0:
            raise ValueError("workspace dimensions must be positive")
        if max_m % 2 or width % 2 or block_rows % 2:
            raise ValueError("workspace dimensions and block rows must be even")
        self.max_m = int(max_m)
        self.width = int(width)
        self.block_rows = int(block_rows)
        half_block = min(self.block_rows, self.max_m) // 2
        half_width = self.width // 2
        self.output = fnp.empty((self.max_m, self.width), dtype=fnp.float32)
        self.left_children = fnp.empty(
            (7, half_block, half_width), dtype=fnp.float32
        )
        self.right_children = fnp.empty(
            (7, half_width, half_width), dtype=fnp.float32
        )
        self.products = fnp.empty(
            (7, half_block, half_width), dtype=fnp.float32
        )
        self.last_core_calls = 0
        self.last_total_matmul_calls = 0

    @property
    def buffer_bytes(self) -> int:
        return sum(int(array.nbytes) for array in (
            self.output,
            self.left_children,
            self.right_children,
            self.products,
        ))

    def predicted_core_calls(self, m: int, strategy: str) -> int:
        if strategy == "direct":
            return 0
        return math.ceil(int(m) / self.block_rows)

    def multiply(self, left, right):
        if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
            raise ValueError("incompatible 2-D matrix product")
        m, k = (int(value) for value in left.shape)
        n = int(right.shape[1])
        if m > self.max_m or max(k, n) > self.width:
            raise ValueError("product exceeds preallocated workspace")
        bill = batched_candidate_bill(m, k, n)
        if bill.strategy == "direct":
            self.last_core_calls = 0
            self.last_total_matmul_calls = 1
            return left @ right

        nc = bill.core_n
        hk, hn = k // 2, nc // 2
        b11 = right[:hk, :hn]
        b12 = right[:hk, hn:nc]
        b21 = right[hk:k, :hn]
        b22 = right[hk:k, hn:nc]
        rc = self.right_children[:, :hk, :hn]

        # Right-hand packing is deliberately outside the row loop, so the
        # billed right-stack fill is identical to the unsplit operator.
        fnp.copyto(rc[0], b11)
        fnp.copyto(rc[1], b21)
        fnp.copyto(rc[2], b22)
        fnp.subtract(b12, b11, out=rc[4])
        fnp.subtract(b22, rc[4], out=rc[5])
        fnp.subtract(b22, b12, out=rc[6])
        fnp.subtract(rc[5], b21, out=rc[3])

        c = self.output[:m, :n]
        core_calls = 0
        for start in range(0, m, self.block_rows):
            stop = min(start + self.block_rows, m)
            rows = stop - start
            if rows % 2:
                raise AssertionError("even input/block geometry gave odd tail")
            hm = rows // 2
            a = left[start:stop, :k]
            a11 = a[:hm, :hk]
            a12 = a[:hm, hk:k]
            a21 = a[hm:rows, :hk]
            a22 = a[hm:rows, hk:k]
            lc = self.left_children[:, :hm, :hk]
            products = self.products[:, :hm, :hn]

            fnp.copyto(lc[0], a11)
            fnp.copyto(lc[1], a12)
            fnp.copyto(lc[3], a22)
            fnp.add(a21, a22, out=lc[4])
            fnp.subtract(lc[4], a11, out=lc[5])
            fnp.subtract(a11, a21, out=lc[6])
            fnp.subtract(a12, lc[5], out=lc[2])

            fnp.matmul(lc, rc, out=products)
            core_calls += 1

            cb = c[start:stop, :nc]
            c11 = cb[:hm, :hn]
            c12 = cb[:hm, hn:nc]
            c21 = cb[hm:rows, :hn]
            c22 = cb[hm:rows, hn:nc]
            fnp.add(products[0], products[1], out=c11)
            fnp.add(products[0], products[5], out=c12)
            fnp.add(c12, products[6], out=c21)
            fnp.add(c21, products[4], out=c22)
            fnp.add(c12, products[4], out=c12)
            fnp.add(c12, products[2], out=c12)
            fnp.subtract(c21, products[3], out=c21)

        if nc < n:
            fnp.matmul(left, right[:, nc:n], out=c[:, nc:n])
        self.last_core_calls = core_calls
        self.last_total_matmul_calls = core_calls + int(nc < n)
        return c


def row_blocked_bill_identity(m: int, k: int, n: int) -> dict:
    """Return the frozen algebraic bill/call statement for one shape."""
    bill = batched_candidate_bill(m, k, n)
    core_calls = 0 if bill.strategy == "direct" else math.ceil(m / BLOCK_ROWS)
    total_calls = 1 if bill.strategy == "direct" else (
        core_calls + int(bool(bill.output_tail))
    )
    return {
        "strategy": bill.strategy,
        "selected_bill": int(bill.total),
        "direct_bill": int(bill.direct),
        "core_calls": int(core_calls),
        "total_matmul_calls": int(total_calls),
    }


def independently_expanded_bill(m: int, k: int, n: int) -> int:
    """Expand every streamed term rather than reusing the core formula."""
    bill = batched_candidate_bill(m, k, n)
    if bill.strategy == "direct":
        return direct_cost(m, k, n)
    nc = bill.core_n
    hk, hn = k // 2, nc // 2
    row_sizes = [
        min(BLOCK_ROWS, m - start) for start in range(0, m, BLOCK_ROWS)
    ]
    leaves = sum(7 * direct_cost(rows // 2, hk, hn) for rows in row_sizes)
    left_fills = sum(7 * (rows // 2) * hk for rows in row_sizes)
    right_fill_once = 7 * hk * hn
    output_adds = sum(7 * (rows // 2) * hn for rows in row_sizes)
    return leaves + left_fills + right_fill_once + output_adds + bill.output_tail

