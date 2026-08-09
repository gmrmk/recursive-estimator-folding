"""Fixed-height streaming Batched-B Winograd workspace with owned outputs.

Every kernel product receives disjoint input and output.  A caller may hand
the active buffer back as ``out``: each Winograd block is fully captured in
the left-child stack before its corresponding output rows are reconstructed.
No future block reads those rows, so the ownership transfer is safe without a
persistent full output buffer.
"""

from __future__ import annotations

import math
import flopscope.numpy as fnp

from cost_model import direct_cost, owned_batched_candidate_bill


# Fixed before measurement: a shape-only memory schedule, never selected by
# MLP seed, generated result, active set, or score.
BLOCK_ROWS = 4_096


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
        # Direct-dispatch shapes need one bounded copy.  Winograd captures the
        # whole row block in its seven left-child operands instead.
        self.direct_scratch = fnp.empty(
            (min(self.block_rows, self.max_m), self.width), dtype=fnp.float32
        )
        self.tail_output = fnp.empty(
            (min(self.block_rows, self.max_m), 1), dtype=fnp.float32
        )
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
            self.direct_scratch,
            self.tail_output,
            self.left_children,
            self.right_children,
            self.products,
        ))

    @property
    def full_output_bytes(self) -> int:
        """The operator owns no full sampled activation/output allocation."""
        return 0

    def predicted_core_calls(self, m: int, strategy: str) -> int:
        return math.ceil(int(m) / self.block_rows)

    def multiply(self, left, right, *, out):
        if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
            raise ValueError("incompatible 2-D matrix product")
        m, k = (int(value) for value in left.shape)
        n = int(right.shape[1])
        if m > self.max_m or max(k, n) > self.width:
            raise ValueError("product exceeds preallocated workspace")
        if out.ndim != 2 or out.shape[0] < m or out.shape[1] < n:
            raise ValueError("caller output has insufficient shape")
        if fnp.shares_memory(out, right):
            raise ValueError("output may not alias right operand")
        same_left = fnp.shares_memory(out, left)
        if same_left and (out.shape[0] != left.shape[0] or out.shape[1] < n):
            raise ValueError("in-place output must cover exactly the input rows")
        bill = owned_batched_candidate_bill(m, k, n)
        if bill.strategy.startswith("direct"):
            self.last_core_calls = 0
            self.last_total_matmul_calls = math.ceil(m / self.block_rows)
            for start in range(0, m, self.block_rows):
                stop = min(start + self.block_rows, m)
                rows = stop - start
                source = self.direct_scratch[:rows, :k]
                fnp.copyto(source, left[start:stop, :k])
                fnp.matmul(source, right, out=out[start:stop, :n])
            return out[:m, :n]

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

        c = out[:m, :n]
        core_calls = 0
        for start in range(0, m, self.block_rows):
            stop = min(start + self.block_rows, m)
            rows = stop - start
            if rows % 2:
                raise AssertionError("even input/block geometry gave odd tail")
            hm = rows // 2
            # All input entries needed for the core are captured by ``lc``
            # before a single output row is written.  The odd tail is likewise
            # computed into bounded disjoint scratch before reconstruction.
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

            if nc < n:
                fnp.matmul(a, right[:, nc:n], out=self.tail_output[:rows, :1])

            # ``lc``, ``rc``, and ``products`` are disjoint workspace views.
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
                fnp.copyto(c[start:stop, nc:n], self.tail_output[:rows, :1])

        self.last_core_calls = core_calls
        self.last_total_matmul_calls = core_calls * (1 + int(nc < n))
        return c


def row_blocked_bill_identity(m: int, k: int, n: int) -> dict:
    """Return the frozen algebraic bill/call statement for one shape."""
    bill = owned_batched_candidate_bill(m, k, n)
    core_calls = math.ceil(m / BLOCK_ROWS)
    total_calls = core_calls if bill.strategy.startswith("direct") else (
        core_calls * (1 + int(bool(bill.output_tail)))
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
    bill = owned_batched_candidate_bill(m, k, n)
    if bill.strategy.startswith("direct"):
        return bill.total
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
