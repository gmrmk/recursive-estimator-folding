"""NumPy algebra reference for M210's same-level fused Gram tree."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


WIDTH = 256
LAYERS = 31
DEPTH = 3
F64_RATE = 2


@dataclass(frozen=True)
class Source211:
    aaaa: np.ndarray
    aaab: np.ndarray
    aabb: np.ndarray


def _validate(value: np.ndarray, depth: int) -> tuple[np.ndarray, int, int]:
    array = np.asarray(value)
    if array.ndim != 3 or array.shape[-2] != array.shape[-1]:
        raise ValueError("M210 requires (batch,width,width)")
    width = int(array.shape[-1])
    if depth < 0 or width <= 0 or width % (2**depth):
        raise ValueError("width must be divisible by 2**depth")
    if not np.all(np.isfinite(array)):
        raise ValueError("input must be finite")
    return array, int(array.shape[0]), width


def level_fused_batched_gram(value: np.ndarray, depth: int = DEPTH) -> np.ndarray:
    """Compute every node at a given tree depth in one batch matmul."""

    array, batch, width = _validate(value, depth)
    output = np.empty((batch, width, width), dtype=array.dtype)
    for level in range(depth):
        nodes = 2**level
        block_width = width // nodes
        half = block_width // 2
        blocks = np.reshape(array, (batch, width, nodes, block_width))
        left = np.transpose(blocks[:, :, :, :half], (0, 2, 3, 1))
        right = np.transpose(blocks[:, :, :, half:], (0, 2, 1, 3))
        products = left @ right
        for node in range(nodes):
            start = node * block_width
            middle = start + half
            stop = start + block_width
            output[:, start:middle, middle:stop] = products[:, node]
            output[:, middle:stop, start:middle] = np.swapaxes(products[:, node], 1, 2)

    leaves = 2**depth
    leaf_width = width // leaves
    blocks = np.reshape(array, (batch, width, leaves, leaf_width))
    left = np.transpose(blocks, (0, 2, 3, 1))
    right = np.transpose(blocks, (0, 2, 1, 3))
    products = left @ right
    for node in range(leaves):
        start = node * leaf_width
        stop = start + leaf_width
        output[:, start:stop, start:stop] = products[:, node]
    return output


def compile_level_fused_rank_one_control(
    weight: np.ndarray, factor: np.ndarray, depth: int = DEPTH
) -> Source211:
    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] != w.shape[1] or w.shape[0] < 3:
        raise ValueError("weight must be square")
    if u.shape != (w.shape[0],) or not np.all(np.isfinite(w)) or not np.all(np.isfinite(u)):
        raise ValueError("factor/weight mismatch or nonfinite input")
    scaled = u[:, None] * w
    p = np.sum(scaled, axis=0)
    gram = level_fused_batched_gram(scaled[None], depth=depth)[0]
    rho = np.diag(gram)
    p2 = p * p
    aaab = -6.0 * (p2[:, None] * gram + np.outer(rho * p, p))
    aabb = -2.0 * (
        np.outer(rho, p2)
        + np.outer(p2, rho)
        + 4.0 * gram * np.outer(p, p)
    )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def _matmul_bill(m: int, k: int, n: int) -> int:
    return 2 * m * k * n - m * n


def static_prediction(
    width: int = WIDTH, layers: int = LAYERS, depth: int = DEPTH
) -> dict[str, int]:
    if depth < 0 or width % (2**depth):
        raise ValueError("invalid depth")
    arithmetic = 0
    for level in range(depth):
        nodes = 2**level
        half = width // (2 ** (level + 1))
        arithmetic += nodes * _matmul_bill(half, width, half)
    leaf_width = width // (2**depth)
    arithmetic += 2**depth * _matmul_bill(leaf_width, width, leaf_width)
    full_bank = layers * width * width
    return {
        "matmul_calls": depth + 1,
        "matmul_bill": F64_RATE * layers * arithmetic,
        "reshape_calls": depth + 1,
        "reshape_bill": F64_RATE * (depth + 1) * full_bank,
    }


if static_prediction() != {
    "matmul_calls": 4,
    "matmul_bill": 1_167_925_248,
    "reshape_calls": 4,
    "reshape_bill": 16_252_928,
}:
    raise AssertionError("M210 frozen prediction drifted")

