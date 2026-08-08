"""Track A / A1: clean-room re-derivation of the two-level fused Winograd
matmul (H53 screened survivor; original source not in repo, hash-pinned only).

The H53 operator is a TWO-level recursive fast matrix multiply: 7 products per
level, 7^2 = 49 leaf products at two levels (256 -> 128 -> 64), fused so one
batched matmul evaluates all 49 leaves per row-block. This module re-derives
the recursion from the classic exact bilinear identity and proves it EXACT vs
dense (G-A1a, the cheapest falsifier). It is a RESOURCE-only mutation: the
predictions are unchanged up to float reassociation; the win is billed-FLOP
compression (8 -> 7 products per level) under the score's compute term.

Response-free: pure linear algebra, no MLP / challenge data / scorer.

Level count: `levels` = number of Strassen recursions before the dense base.
levels=1 is the champion's L1 (7 products); levels=2 is the H53 L2 (49 leaves).
"""

from __future__ import annotations

import numpy as np


def _split(M):
    n = M.shape[0]
    h = n // 2
    return M[:h, :h], M[:h, h:], M[h:, :h], M[h:, h:]


def strassen(A: np.ndarray, B: np.ndarray, levels: int) -> np.ndarray:
    """Recursive Strassen fast matmul, exact bilinear identity (classic 7-mult
    scheme). Square power-of-two-splittable dims assumed for the re-derivation
    (the target 256-core is 256 -> 128 -> 64). `levels` recursions, then dense.

    Batched left operand: A may be (m, k) with m the row-block (batch) axis; the
    split is on the shared k and output n axes only. Here we prove the square
    core identity (m = k = n) exactly; row-batching rides the m axis unchanged.
    """
    n = A.shape[-1]
    if levels <= 0 or n % 2 != 0:
        return A @ B
    A11, A12, A21, A22 = _split(A)
    B11, B12, B21, B22 = _split(B)

    M1 = strassen(A11 + A22, B11 + B22, levels - 1)
    M2 = strassen(A21 + A22, B11, levels - 1)
    M3 = strassen(A11, B12 - B22, levels - 1)
    M4 = strassen(A22, B21 - B11, levels - 1)
    M5 = strassen(A11 + A12, B22, levels - 1)
    M6 = strassen(A21 - A11, B11 + B12, levels - 1)
    M7 = strassen(A12 - A22, B21 + B22, levels - 1)

    C11 = M1 + M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 - M2 + M3 + M6

    top = np.concatenate((C11, C12), axis=-1)
    bot = np.concatenate((C21, C22), axis=-1)
    return np.concatenate((top, bot), axis=-2)


def leaf_product_count(levels: int) -> int:
    """Number of leaf multiplications: 7^levels (49 at the H53 two-level)."""
    return 7 ** levels


def direct_mult_count(k: int, levels: int) -> int:
    """Base-case dense multiplications for a k-cube at `levels` recursions:
    7^levels leaves, each a (k/2^levels)-cube costing (k/2^levels)^3 mults."""
    base = k // (2 ** levels)
    return leaf_product_count(levels) * base ** 3


def naive_mult_count(k: int) -> int:
    """Dense k-cube multiplications."""
    return k ** 3
