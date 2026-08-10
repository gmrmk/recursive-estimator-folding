"""M209 response-free layer-batched recursive Gram compiler.

This NumPy module is the algebra/reference half of the frozen M209 packet.  A
separate FlopScope sidecar owns target-shape billing; this file neither reads a
challenge object nor claims provider, variance, response, or score credit.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


WIDTH = 256
LAYERS = 31
DEPTH = 3
F64_RATE = 2
STRICT_COMPOSED_HEADROOM = 1_986_871_472


@dataclass(frozen=True)
class Source211:
    aaaa: np.ndarray
    aaab: np.ndarray
    aabb: np.ndarray


def _validate_depth(width: int, depth: int) -> None:
    if depth < 0 or width <= 0 or width % (2**depth):
        raise ValueError("width must be positive and divisible by 2**depth")


def recursive_batched_gram(value: np.ndarray, depth: int = DEPTH) -> np.ndarray:
    """Return ``value.swapaxes(-2,-1) @ value`` using one triangle only.

    Leading axes are independent batch axes.  Recursion splits only the final
    column axis; every cross block is computed once and mirrored exactly.
    """

    array = np.asarray(value)
    if array.ndim < 2 or array.shape[-2] != array.shape[-1]:
        raise ValueError("a square final two-axis matrix is required")
    width = array.shape[-1]
    _validate_depth(width, depth)
    if not np.all(np.isfinite(array)):
        raise ValueError("input must be finite")

    output = np.empty(array.shape[:-2] + (width, width), dtype=array.dtype)

    def visit(start: int, stop: int, remaining: int) -> None:
        if remaining == 0:
            block = array[..., :, start:stop]
            output[..., start:stop, start:stop] = np.swapaxes(block, -2, -1) @ block
            return
        middle = (start + stop) // 2
        left = array[..., :, start:middle]
        right = array[..., :, middle:stop]
        cross = np.swapaxes(left, -2, -1) @ right
        output[..., start:middle, middle:stop] = cross
        output[..., middle:stop, start:middle] = np.swapaxes(cross, -2, -1)
        visit(start, middle, remaining - 1)
        visit(middle, stop, remaining - 1)

    visit(0, width, depth)
    return output


def compile_recursive_rank_one_control(
    weight: np.ndarray, factor: np.ndarray, depth: int = DEPTH
) -> Source211:
    """Compile the unchanged M205 full-domain rank-one control via M209."""

    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] != w.shape[1] or w.shape[0] < 3:
        raise ValueError("weight must be a square matrix of width at least three")
    if u.shape != (w.shape[0],):
        raise ValueError("factor must match the weight row-label axis")
    if not (np.all(np.isfinite(w)) and np.all(np.isfinite(u))):
        raise ValueError("weight and factor must be finite")
    _validate_depth(w.shape[0], depth)

    scaled = u[:, None] * w
    p = np.sum(scaled, axis=0)
    gram = recursive_batched_gram(scaled[None, ...], depth=depth)[0]
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
    """Return the frozen f64 matmul/copy ledger for the recursive tree."""

    _validate_depth(width, depth)
    arithmetic_per_layer = 0
    mirror_elements_per_layer = 0
    calls = 0
    for level in range(depth):
        nodes = 2**level
        half = width // (2 ** (level + 1))
        arithmetic_per_layer += nodes * _matmul_bill(half, width, half)
        mirror_elements_per_layer += nodes * half * half
        calls += nodes
    leaf_width = width // (2**depth)
    leaves = 2**depth
    arithmetic_per_layer += leaves * _matmul_bill(leaf_width, width, leaf_width)
    calls += leaves
    return {
        "matmul_calls": calls,
        "matmul_bill": F64_RATE * layers * arithmetic_per_layer,
        "mirror_copy_elements": layers * mirror_elements_per_layer,
        "mirror_copy_bill": F64_RATE * layers * mirror_elements_per_layer,
        "strict_composed_headroom": STRICT_COMPOSED_HEADROOM,
        "raw_matmul_margin": STRICT_COMPOSED_HEADROOM
        - F64_RATE * layers * arithmetic_per_layer,
    }


if static_prediction()["matmul_bill"] != 1_167_925_248:
    raise AssertionError("frozen M209 target-shape arithmetic drifted")

