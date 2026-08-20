"""Generated-only exact algebra for M218's selective L2 Strassen mutation."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    BASE / "m205_rankone_complete_physical_owner",
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m205_rankone_complete_physical_owner import Source211  # noqa: E402


Array = np.ndarray


def _strassen_recursive(left: Array, right: Array, remaining: int) -> Array:
    if remaining == 0:
        return left @ right
    half = left.shape[-1] // 2
    a11, a12 = left[..., :half, :half], left[..., :half, half:]
    a21, a22 = left[..., half:, :half], left[..., half:, half:]
    b11, b12 = right[..., :half, :half], right[..., :half, half:]
    b21, b22 = right[..., half:, :half], right[..., half:, half:]
    m1 = _strassen_recursive(a11 + a22, b11 + b22, remaining - 1)
    m2 = _strassen_recursive(a21 + a22, b11, remaining - 1)
    m3 = _strassen_recursive(a11, b12 - b22, remaining - 1)
    m4 = _strassen_recursive(a22, b21 - b11, remaining - 1)
    m5 = _strassen_recursive(a11 + a12, b22, remaining - 1)
    m6 = _strassen_recursive(a21 - a11, b11 + b12, remaining - 1)
    m7 = _strassen_recursive(a12 - a22, b21 + b22, remaining - 1)
    output = np.empty_like(left)
    output[..., :half, :half] = m1 + m4 - m5 + m7
    output[..., :half, half:] = m3 + m5
    output[..., half:, :half] = m2 + m4
    output[..., half:, half:] = m1 - m2 + m3 + m6
    return output


def strassen_l2_numpy(left: Array, right: Array) -> Array:
    """Classic exact seven-product identity at exactly two levels."""

    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    if a.shape != b.shape or a.ndim < 2 or a.shape[-2] != a.shape[-1]:
        raise ValueError("M218 requires shape-identical square matrix batches")
    if a.shape[-1] < 4 or a.shape[-1] % 4:
        raise ValueError("M218 L2 requires matrix width divisible by four")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("M218 inputs must be finite")
    return _strassen_recursive(a, b, remaining=2)


def _checked_weight_factor(weight: Array, factor: Array) -> tuple[Array, Array]:
    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] < 4 or w.shape[1] < 4 or not np.all(np.isfinite(w)):
        raise ValueError("weight must be a finite labelled matrix")
    if w.shape[0] % 4 or w.shape[1] % 4:
        raise ValueError("both labelled and output widths must be divisible by four")
    if u.shape != (w.shape[0],) or not np.all(np.isfinite(u)):
        raise ValueError("factor must be a finite vector matching labelled width")
    return w, u


def compile_ae_numpy(weight: Array, factor: Array) -> tuple[Array, Array]:
    """Compute only M215's nonsymmetric A/E products with exact L2 Strassen."""

    w, u = _checked_weight_factor(weight, factor)
    s = u[:, None] * w
    s2 = s * s
    s3 = s2 * s
    return strassen_l2_numpy(s2.T, s), strassen_l2_numpy(s3.T, s)


def compile_collision_source_numpy(weight: Array, factor: Array) -> Source211:
    """M215 collision algebra with only A/E supplied by L2 Strassen."""

    w, u = _checked_weight_factor(weight, factor)
    s = u[:, None] * w
    s2 = s * s
    s3 = s2 * s
    p = np.sum(s, axis=0)
    b = s.T @ s
    rho = np.diag(b).copy()
    a, e = compile_ae_numpy(w, u)
    t = np.sum(s3, axis=0)
    d = s2.T @ s2
    aaab = (
        -18.0 * (p[:, None] * a)
        - 6.0 * np.outer(t, p)
        - 12.0 * (rho[:, None] * b)
        + 24.0 * e
    )
    aabb = (
        -12.0 * (a * p[None, :] + p[:, None] * a.T)
        - 4.0 * np.outer(rho, rho)
        - 8.0 * (b * b)
        + 24.0 * d
    )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


__all__ = ["compile_ae_numpy", "compile_collision_source_numpy", "strassen_l2_numpy"]
