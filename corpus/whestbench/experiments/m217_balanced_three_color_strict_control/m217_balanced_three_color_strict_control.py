"""M217 response-free balanced-color strict-support control algebra.

This module contains only generated/source identities.  The cubic table
helpers are parity oracles and are prohibited at target width.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class Source211:
    aaaa: Array
    aaab: Array
    aabb: Array


def balanced_sizes(width: int) -> tuple[int, int, int]:
    if width < 3:
        raise ValueError("balanced three-coloring requires width at least three")
    quotient, remainder = divmod(int(width), 3)
    return tuple(quotient + int(color < remainder) for color in range(3))


def distinct_probability(width: int) -> float:
    n0, n1, n2 = balanced_sizes(width)
    return float(6 * n0 * n1 * n2) / float(width * (width - 1) * (width - 2))


def random_balanced_colors(width: int, seed: int) -> Array:
    sizes = balanced_sizes(width)
    base = np.concatenate(
        [np.full(count, color, dtype=np.int64) for color, count in enumerate(sizes)]
    )
    return base[np.random.default_rng(int(seed)).permutation(width)]


def _factor(value: Array) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 1 or result.size < 3 or not np.all(np.isfinite(result)):
        raise ValueError("factor must be a finite vector of width at least three")
    return result


def _colors(value: Array, width: int) -> Array:
    result = np.asarray(value, dtype=np.int64)
    if result.shape != (width,) or not np.all((0 <= result) & (result < 3)):
        raise ValueError("colors must be a width-vector over {0,1,2}")
    if tuple(int(np.count_nonzero(result == color)) for color in range(3)) != balanced_sizes(width):
        raise ValueError("color class sizes do not match the frozen balanced partition")
    return result


def strict_control_table(factor: Array) -> Array:
    """Small-width parity oracle for the M151 pairwise-distinct table."""

    u = _factor(factor)
    answer = np.zeros((u.size, u.size, u.size), dtype=np.float64)
    full = -2.0 * np.einsum("i,j,k->ijk", u * u, u, u)
    for i in range(u.size):
        for j in range(u.size):
            for k in range(u.size):
                if len({i, j, k}) == 3:
                    answer[i, j, k] = full[i, j, k]
    return answer


def masked_control_table(factor: Array, colors: Array) -> Array:
    """Small-width colored table, zero on every repeated-label row."""

    u = _factor(factor)
    h = _colors(colors, u.size)
    scale = 1.0 / distinct_probability(u.size)
    full = -2.0 * scale * np.einsum("i,j,k->ijk", u * u, u, u)
    answer = np.zeros_like(full)
    for i in range(u.size):
        for j in range(u.size):
            for k in range(u.size):
                if len({int(h[i]), int(h[j]), int(h[k])}) == 3:
                    answer[i, j, k] = full[i, j, k]
    return answer


def compile_colored_control(weight: Array, factor: Array, colors: Array) -> Source211:
    """Compile the strict colored source from three local Grams and moments.

    For a fixed ordered color-role assignment (a,b,c), the repeated role i is
    in class a and the singleton roles j,k are in b,c.  The six assignments
    are disjoint, so no inclusion/exclusion or collision statistic is needed.
    """

    w = np.asarray(weight, dtype=np.float64)
    u = _factor(factor)
    if w.ndim != 2 or w.shape[0] != u.size or not np.all(np.isfinite(w)):
        raise ValueError("weight must be finite and share the factor label width")
    h = _colors(colors, u.size)
    scale = 1.0 / distinct_probability(u.size)
    output = int(w.shape[1])
    first = []
    grams = []
    for color in range(3):
        indices = np.flatnonzero(h == color)
        scaled = u[indices, None] * w[indices]
        first.append(np.sum(scaled, axis=0))
        grams.append(scaled.T @ scaled)

    aaab = np.zeros((output, output), dtype=np.float64)
    aabb = np.zeros((output, output), dtype=np.float64)
    for a, b, c in itertools.permutations(range(3)):
        gram = grams[a]
        rho = np.diag(gram)
        pb = first[b]
        pc = first[c]
        singleton_product = pb * pc
        aaab += -6.0 * scale * (
            singleton_product[:, None] * gram
            + np.outer(rho * pc, pb)
        )
        cross_bc = (pb[:, None] * gram) * pc[None, :]
        cross_cb = (pc[:, None] * gram) * pb[None, :]
        aabb += -2.0 * scale * (
            np.outer(rho, singleton_product)
            + np.outer(singleton_product, rho)
            + 2.0 * cross_bc
            + 2.0 * cross_cb
        )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


__all__ = [
    "Source211",
    "balanced_sizes",
    "distinct_probability",
    "random_balanced_colors",
    "strict_control_table",
    "masked_control_table",
    "compile_colored_control",
]
