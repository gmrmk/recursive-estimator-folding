"""Exact orbit fusion for the zero-mean M85 fourth-order path Gram.

Generated algebra only.  This module has no challenge/scorer/submission access.
It separates thirteen explicit O(n^3)-constructible orbit matrices from three
Khatri--Rao orbit actions that are applied in O(n^3) per vector.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np


M122_DIR = Path(__file__).resolve().parents[1] / "m122_tree_factor_theory"
if str(M122_DIR) not in sys.path:
    sys.path.insert(0, str(M122_DIR))
from m122_tree_factor import PATHS4, path4_tensor  # noqa: E402


REPRESENTATIVES = (
    ((0, 1, 2, 3), (0, 1, 2, 3), 6),
    ((0, 1, 2, 3), (0, 1, 3, 2), 6),
    ((0, 1, 2, 3), (0, 2, 1, 3), 6),
    ((0, 1, 2, 3), (0, 2, 3, 1), 12),
    ((0, 1, 2, 3), (0, 3, 2, 1), 6),
    ((0, 1, 2, 3), (1, 0, 2, 3), 12),
    ((0, 1, 2, 3), (1, 0, 3, 2), 12),
    ((0, 1, 2, 3), (1, 2, 0, 3), 12),
    ((0, 1, 2, 3), (1, 3, 0, 2), 12),
    ((0, 1, 2, 3), (2, 0, 1, 3), 12),
    ((0, 1, 2, 3), (2, 1, 0, 3), 12),
    ((1, 0, 2, 3), (1, 0, 2, 3), 6),
    ((1, 0, 2, 3), (1, 0, 3, 2), 6),
    ((1, 0, 2, 3), (1, 2, 0, 3), 6),
    ((1, 0, 2, 3), (1, 3, 0, 2), 12),
    ((1, 0, 2, 3), (2, 0, 1, 3), 6),
)

HARD_ORBITS = (8, 14, 15)


def _require_q(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64)
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("q must be square")
    if not np.allclose(q, q.T, rtol=0.0, atol=2e-12):
        raise ValueError("q must be symmetric")
    return q


def dense_representative(q: np.ndarray, orbit: int) -> np.ndarray:
    """Small-width reference matrix for one representative path pair."""
    q = _require_q(q)
    left, right, _ = REPRESENTATIVES[orbit]
    a = path4_tensor(q, left)
    b = path4_tensor(q, right)
    return np.einsum("ajkl,bjkl->ab", a, b, optimize=True)


def orbit_matrix_formula(q: np.ndarray, orbit: int) -> np.ndarray:
    """Exact representative matrix K_o for all sixteen fused orbits.

    Orbits 8, 14, and 15 are included only as small-width dense formulas for
    validation.  A target operator must use ``hard_orbit_apply`` instead.
    """
    q = _require_q(q)
    h = q * q
    r = q @ q
    s = h.sum(axis=1)
    if orbit == 0:
        return (q * (h @ s)[None, :]) @ q
    if orbit == 1:
        d = np.sum((q @ h) * q, axis=1)
        return (q * d[None, :]) @ q
    if orbit == 2:
        return (q @ (h * r)) @ q
    if orbit == 3:
        return (q @ (q * (q @ h))) @ q
    if orbit == 4:
        return ((q @ h) @ h) @ q
    if orbit == 5:
        a = (q * s[None, :]) @ q
        return q @ (q * a)
    if orbit == 6:
        a = (q @ h) @ q
        return q @ (q * a)
    if orbit == 7:
        return (q @ h) @ (q * r)
    if orbit == 8:
        # D_bj=(q_b circ q_j)^T Q (q_b circ q_j), K=Q D^T.
        d = np.einsum("bk,jk,kl,bl,jl->bj", q, q, q, q, q, optimize=True)
        return q @ d.T
    if orbit == 9:
        m = q * r
        a = q @ m
        return q @ (q * a).T
    if orbit == 10:
        a = r @ h
        return q @ (q * a).T
    if orbit == 11:
        a = (q * s[None, :]) @ q
        return r * a
    if orbit == 12:
        return r * ((q @ h) @ q)
    if orbit == 13:
        b = q * r
        return b @ b
    if orbit == 14:
        return np.einsum("aj,ak,kl,jl,bl,bk->ab", q, q, q, q, q, q, optimize=True)
    if orbit == 15:
        return np.einsum("aj,bj,jk,ak,bk->ab", q, q, r, q, q, optimize=True)
    raise ValueError("orbit must be in 0..15")


def easy_fused_matrix(q: np.ndarray) -> np.ndarray:
    """Sum the thirteen O(n^3)-constructible orbit matrices with multiplicity."""
    q = _require_q(q)
    answer = np.zeros_like(q)
    for orbit, (_, _, size) in enumerate(REPRESENTATIVES):
        if orbit in HARD_ORBITS:
            continue
        k = orbit_matrix_formula(q, orbit)
        answer += 6.0 * k if size == 6 else 6.0 * (k + k.T)
    return answer


def _c(q: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Q diag(x) Q: one target n-by-n matmul after column scaling."""
    return (q * x[None, :]) @ q


def _diag_q_b_q(q: np.ndarray, b: np.ndarray) -> np.ndarray:
    """diag(Q B Q), with the second product replaced by a rowwise dot."""
    return np.sum((q @ b) * q, axis=1)


def hard_orbit_apply(q: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Apply the exactly fused contributions of orbits 8,14,15.

    The shared C=Q diag(x) Q leaves eight n-by-n products per vector:

    - C itself;
    - orbit 8 forward and transpose: three further products;
    - orbit 14 forward and transpose: three further products; and
    - orbit 15: one further product.

    All scalar multipliers below are exact orbit sizes, not fitted weights.
    """
    q = _require_q(q)
    x = np.asarray(x, dtype=np.float64)
    if x.shape != (q.shape[0],):
        raise ValueError("x has wrong shape")
    r = q @ q  # target implementation precomputes this outside the action
    c = _c(q, x)  # shared product 1

    # Orbit 8: Kx = Q z, z=diag(Q[(Q circ C)]Q).
    e = q * c
    k8x = q @ _diag_q_b_q(q, e)  # product 2; final q-vector is n^2 work
    v = q @ x
    cv = _c(q, v)  # product 3
    k8tx = _diag_q_b_q(q, q * cv)  # product 4

    # Orbit 14 forward: diag(Q [Q(Q circ C)] Q) = rowsum((R E) circ Q).
    k14x = np.sum((r @ e) * q, axis=1)  # product 5
    qc = q @ c  # product 6
    f = q * qc
    k14tx = np.sum((q @ f.T) * q, axis=1)  # product 7

    # Orbit 15 is symmetric.
    k15x = _diag_q_b_q(q, r * c)  # product 8
    return 6.0 * (k8x + k8tx) + 6.0 * (k14x + k14tx) + 6.0 * k15x


def fused_mode1_gram_apply(q: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Apply the complete all-index tree4 mode-1 Gram without n^4 storage."""
    q = _require_q(q)
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        return easy_fused_matrix(q) @ x + hard_orbit_apply(q, x)
    if x.ndim != 2 or x.shape[0] != q.shape[0]:
        raise ValueError("x must have shape (n,) or (n,b)")
    easy = easy_fused_matrix(q)
    return easy @ x + np.column_stack([hard_orbit_apply(q, x[:, column]) for column in range(x.shape[1])])


def equivariant_start_block(q: np.ndarray, rank_tolerance: float = 2.0**-40) -> np.ndarray:
    """Fixed rank-four standardised start, with symmetry degeneracy fail-closed."""
    q = _require_q(q)
    if q.shape[0] < 4:
        raise ValueError("rank-four start requires n>=4")
    one = np.ones(q.shape[0], dtype=np.float64)
    hdegree = (q * q) @ one
    raw = np.column_stack((one, q @ one, hdegree, q @ hdegree))
    singular = np.linalg.svd(raw, compute_uv=False)
    if singular[-1] <= rank_tolerance * max(1.0, singular[0]):
        raise FloatingPointError("equivariant start is rank deficient")
    u, _ = np.linalg.qr(raw, mode="reduced")
    return u


def full_fused_matrix_small(q: np.ndarray) -> np.ndarray:
    """Small-width exact fused matrix, including explicit hard orbit formulas."""
    q = _require_q(q)
    answer = np.zeros_like(q)
    for orbit, (_, _, size) in enumerate(REPRESENTATIVES):
        k = orbit_matrix_formula(q, orbit)
        answer += 6.0 * k if size == 6 else 6.0 * (k + k.T)
    return answer
