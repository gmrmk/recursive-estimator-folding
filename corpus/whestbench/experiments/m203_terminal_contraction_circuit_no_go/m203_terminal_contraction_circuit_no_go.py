"""Exact packing identity and static bill for the M203 terminal audit."""

from __future__ import annotations

import numpy as np


N = 256
LAYERS = 31
F64_RATE = 2
PROTECTION_NUMERATOR = 5
PROTECTION_DENOMINATOR = 4
M151_SLOT = 10_291_363_760
STRICT_COMPOSED_HEADROOM = 1_986_871_472
CONDITIONAL_REPLACEMENT_HEADROOM = 9_723_621_632


def dense_bill(m: int, k: int, n: int) -> int:
    return 2 * m * k * n - m * n


def recursive_winograd_bill(m: int, k: int, n: int, depth: int) -> int:
    if min(m, k, n) <= 0 or depth < 0:
        raise ValueError("positive shapes and nonnegative depth required")
    if depth == 0:
        return dense_bill(m, k, n)
    if any(value % 2 for value in (m, k, n)):
        raise ValueError("all dimensions must be divisible at every recursion level")
    return (
        7 * recursive_winograd_bill(m // 2, k // 2, n // 2, depth - 1)
        + m * k
        + k * n
        + 2 * m * n
    )


def protected_terminal_bill(depth: int, n: int = N, layers: int = LAYERS) -> int:
    raw = recursive_winograd_bill(n, 3 * n, n, depth)
    raw += recursive_winograd_bill(n, 2 * n, n, depth)
    return raw * layers * F64_RATE * PROTECTION_NUMERATOR // PROTECTION_DENOMINATOR


def protected_ideal_projection_bill(n: int = N, layers: int = LAYERS) -> int:
    raw = 2 * n * (n - 1) ** 2
    return raw * layers * F64_RATE * PROTECTION_NUMERATOR // PROTECTION_DENOMINATOR


def packed_terminal_contractions(weight: np.ndarray, orientation: np.ndarray):
    """Two-rectangle exact identity on generated small integer/float matrices."""

    x = np.asarray(weight)
    a = np.asarray(orientation)
    if x.ndim != 2 or a.shape != (x.shape[0], x.shape[0]):
        raise ValueError("weight/orientation shapes are incompatible")
    p = a @ x
    q = a.T @ x
    u3 = np.vstack((2 * x * p * q, x * x * p, x * x * q))
    v3 = np.vstack((x, q, p))
    aaab = -3 * (u3.T @ v3)
    u2 = np.vstack((x * x, 2 * x * p))
    v2 = np.vstack((p * q, x * q))
    raw = u2.T @ v2
    aabb = -2 * (raw + raw.T)
    return np.diag(aaab).copy(), aaab, aabb


def expanded_terminal_contractions(weight: np.ndarray, orientation: np.ndarray):
    """Independent block-by-block expansion of the same five channels."""

    x = np.asarray(weight)
    a = np.asarray(orientation)
    p = a @ x
    q = a.T @ x
    aaab = -3 * (
        (2 * x * p * q).T @ x
        + (x * x * p).T @ q
        + (x * x * q).T @ p
    )
    raw = (x * x).T @ (p * q) + (2 * x * p).T @ (x * q)
    aabb = -2 * (raw + raw.T)
    return np.diag(aaab).copy(), aaab, aabb


def cost_table() -> list[dict[str, int]]:
    projection = protected_ideal_projection_bill()
    rows = []
    for depth in range(3, 7):
        terminal = protected_terminal_bill(depth)
        combined = terminal + projection
        rows.append(
            {
                "depth": depth,
                "terminal": terminal,
                "combined": combined,
                "m151_overage": combined - M151_SLOT,
            }
        )
    return rows
