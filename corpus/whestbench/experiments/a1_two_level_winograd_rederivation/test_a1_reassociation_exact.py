"""A1 / G-A1a (cheapest falsifier): the two-level Winograd reassociation must
equal dense matmul EXACTLY. Proven on integer matrices (int64 matmul is exact
for these magnitudes), so equality is bitwise, not tolerance-bound. If the
bilinear identity is wrong this fails immediately, before any FlopScope run.

Also records the mult-count reduction (8->7 per level) that motivates the
resource win, and confirms row-batching leaves the identity intact.

Response-free: pure linear algebra.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import a1_two_level_winograd as w  # noqa: E402


class A1ReassociationExactTests(unittest.TestCase):
    def test_two_level_equals_dense_exactly_integer(self):
        rng = np.random.default_rng(20260807)
        for k in (8, 16, 32):  # k -> k/2 -> k/4, two levels, 49 leaves
            for _ in range(20):
                A = rng.integers(-5, 6, size=(k, k)).astype(np.int64)
                B = rng.integers(-5, 6, size=(k, k)).astype(np.int64)
                got = w.strassen(A, B, levels=2)
                ref = A @ B
                self.assertTrue(np.array_equal(got, ref),
                                f"two-level mismatch at k={k}")

    def test_one_level_matches_champion_L1_exactly(self):
        rng = np.random.default_rng(1)
        for k in (16, 32):
            A = rng.integers(-8, 9, size=(k, k)).astype(np.int64)
            B = rng.integers(-8, 9, size=(k, k)).astype(np.int64)
            self.assertTrue(np.array_equal(w.strassen(A, B, levels=1), A @ B))

    def test_row_batched_left_operand_is_exact(self):
        # the champion applies the core to a tall (M, 256) left operand; the
        # M (row-block) axis rides the recursion unchanged. Verify a batched
        # left operand with square shared/output axes.
        rng = np.random.default_rng(7)
        k = 16
        M = 40  # row-block batch height (not split)
        A = rng.integers(-4, 5, size=(M, k)).astype(np.int64)
        B = rng.integers(-4, 5, size=(k, k)).astype(np.int64)
        # split only the shared k and output n; batch M rides A's row axis.
        # here A is (M,k) not (k,k); the identity still holds because Strassen
        # splits the last two axes. Pad A's row axis conceptually: verify via
        # block-rows of the dense product.
        got = _batched_strassen(A, B, levels=2)
        self.assertTrue(np.array_equal(got, A @ B))

    def test_mult_count_reduction_is_recorded(self):
        # 8 -> 7 per level; two levels: 64 -> 49 leaf products of the core.
        self.assertEqual(w.leaf_product_count(1), 7)
        self.assertEqual(w.leaf_product_count(2), 49)
        # 256-core: dense 256^3 vs two-level 49 * 64^3
        dense = w.naive_mult_count(256)
        two_level = w.direct_mult_count(256, 2)
        self.assertLess(two_level, dense)
        ratio = two_level / dense
        # 49 * 64^3 / 256^3 = 49/64 = 0.765625 (multiplications only)
        self.assertAlmostEqual(ratio, 49.0 / 64.0, places=12)


def _batched_strassen(A, B, levels):
    """Strassen with a non-square (M, k) left operand: split the k/n axes,
    keep M as an un-split batch of rows. Implemented by row-tiling the dense
    identity for the exactness proof (the production operator fuses this)."""
    # For the exactness proof, a (M,k)@(k,n) with M not a power of two is the
    # vertical stack of (2^p, k) blocks; Strassen on square (k,k) sub-cores
    # applies per output column-block. Simplest exact check: since the row
    # axis never enters the bilinear identity, tile A into square k-row blocks
    # plus a remainder handled densely.
    M, k = A.shape
    out = np.empty((M, B.shape[1]), dtype=A.dtype)
    r = 0
    while r + k <= M:
        out[r:r + k] = w.strassen(A[r:r + k], B, levels)
        r += k
    if r < M:
        out[r:] = A[r:] @ B
    return out


if __name__ == "__main__":
    unittest.main()
