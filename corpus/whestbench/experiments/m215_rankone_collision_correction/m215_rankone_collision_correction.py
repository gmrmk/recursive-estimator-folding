"""M215 exact noncubic compiler for rank-one repeated-label source rows.

This module is generated-only and response-free.  The dense repeated-label
table exists solely in the independent M205 tests; the implementation below
uses output-width matrices and vectors only.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
M205 = HERE.parent / "m205_rankone_complete_physical_owner"
if str(M205) not in sys.path:
    sys.path.insert(0, str(M205))

from m205_rankone_complete_physical_owner import Source211  # noqa: E402


Array = np.ndarray


def _checked_weight_factor(weight: Array, factor: Array) -> tuple[Array, Array]:
    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] < 3 or not np.all(np.isfinite(w)):
        raise ValueError("weight must be a finite labelled matrix of width at least three")
    if u.ndim != 1 or u.shape[0] != w.shape[0] or not np.all(np.isfinite(u)):
        raise ValueError("factor must be a finite vector matching the labelled width")
    return w, u


def compile_rank_one_collision_source_numpy(weight: Array, factor: Array) -> Source211:
    """Compile all repeated-label rows of ``-2 u_i^2 u_j u_k`` exactly.

    With ``S=diag(u)W``, the complete circuit is built from ``p,rho,B`` and
    the three noncubic contractions ``A,E,D`` frozen in the predeclaration.
    """

    w, u = _checked_weight_factor(weight, factor)
    s = u[:, None] * w
    s2 = s * s
    s3 = s2 * s
    p = np.sum(s, axis=0)
    b = s.T @ s
    rho = np.diag(b).copy()
    a = s2.T @ s
    t = np.sum(s3, axis=0)
    e = s3.T @ s
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


def subtract_source(full: Source211, collision: Source211) -> Source211:
    """Return the M151 strict-distinct source from complete minus collision."""

    shapes = (
        full.aaaa.shape == collision.aaaa.shape,
        full.aaab.shape == collision.aaab.shape,
        full.aabb.shape == collision.aabb.shape,
    )
    arrays = (full.aaaa, full.aaab, full.aabb, collision.aaaa, collision.aaab, collision.aabb)
    if not all(shapes) or not all(np.all(np.isfinite(value)) for value in arrays):
        raise ValueError("full and collision sources must be finite and shape-identical")
    return Source211(
        np.asarray(full.aaaa) - np.asarray(collision.aaaa),
        np.asarray(full.aaab) - np.asarray(collision.aaab),
        np.asarray(full.aabb) - np.asarray(collision.aabb),
    )


__all__ = ["compile_rank_one_collision_source_numpy", "subtract_source"]
