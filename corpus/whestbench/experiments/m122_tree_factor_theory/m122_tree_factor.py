"""Generated-only algebra probes for M122's bridge-tree factor question.

This module deliberately operates only on caller-supplied small matrices.  It
contains no challenge loader, scorer, labels, submission code, or learned
parameter.  Its purpose is narrow: verify the tensor-network identities needed
to decide whether M85's *zero-mean* k3/k4 tree source can acquire a legal,
non-materialising Tucker factor.

The tensors here are the all-index tree polynomials.  M85's special one- and
two-coordinate source entries are a sparse replacement of those polynomials;
they are treated in the report as a separate O(n^3) correction to a mode Gram.
"""

from __future__ import annotations

import itertools
from typing import Iterable

import numpy as np


def undirected_paths4() -> tuple[tuple[int, int, int, int], ...]:
    """The 12 labelled undirected paths on four positions.

    The reverse orientation represents the same product and is retained only
    once.  Lexicographic canonicalisation makes this independent of set order.
    """
    answer = []
    for path in itertools.permutations(range(4)):
        if path <= path[::-1]:
            answer.append(path)
    assert len(answer) == 12
    return tuple(answer)


PATHS4 = undirected_paths4()


def _require_symmetric(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64)
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("q must be square")
    if not np.allclose(q, q.T, rtol=0.0, atol=2e-12):
        raise ValueError("q must be symmetric")
    return q


def tree3_tensor(q: np.ndarray) -> np.ndarray:
    """All-index unscaled k3 bridge-tree polynomial.

    This is the displayed M85 tree expression before the special repeated-index
    replacement and its common gamma_2 factor.
    """
    q = _require_symmetric(q)
    return (
        np.einsum("ij,ik->ijk", q, q, optimize=True)
        + np.einsum("ij,jk->ijk", q, q, optimize=True)
        + np.einsum("ik,jk->ijk", q, q, optimize=True)
    )


def path4_tensor(q: np.ndarray, path: tuple[int, int, int, int]) -> np.ndarray:
    """One labelled length-three path written in canonical tensor axes."""
    q = _require_symmetric(q)
    raw = np.einsum("ab,bc,cd->abcd", q, q, q, optimize=True)
    return np.transpose(raw, np.argsort(path))


def tree4_tensor(q: np.ndarray) -> np.ndarray:
    """All-index unscaled k4 labelled-path sum (12 unoriented paths)."""
    q = _require_symmetric(q)
    return sum((path4_tensor(q, path) for path in PATHS4), start=np.zeros((q.shape[0],) * 4))


def mode1_gram(tensor: np.ndarray) -> np.ndarray:
    """Dense small-width reference for a symmetric tensor's mode-1 Gram."""
    t = np.asarray(tensor, dtype=np.float64)
    return t.reshape(t.shape[0], -1) @ t.reshape(t.shape[0], -1).T


def tree3_mode1_gram_formula(q: np.ndarray) -> np.ndarray:
    """Exact O(n^3) mode-1 Gram for ``tree3_tensor(q)``.

    With R=Q^2, H=Q circ Q, r=H 1, F=(Q circ R)Q, K=QHQ,

      G3 = R circ R + 2 Q diag(r) Q + 2 K + 2(F + F^T).

    The conventional M85 gamma_2^2 multiplier is intentionally excluded.
    """
    q = _require_symmetric(q)
    r2 = q @ q
    had = q * q
    row_sq = had.sum(axis=1)
    f = (q * r2) @ q
    k = (q @ had) @ q
    qdiagq = (q * row_sq[None, :]) @ q
    return r2 * r2 + 2.0 * qdiagq + 2.0 * k + 2.0 * (f + f.T)


def crossed_middle_paths() -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    """A path pair whose mode Gram exposes the Khatri--Rao obstruction.

    First:  j-a-k-l; second: k-b-j-l, where a/b are mode-1 row indices.
    """
    return (1, 0, 2, 3), (2, 0, 1, 3)


def crossed_middle_gram_dense(q: np.ndarray) -> np.ndarray:
    """Dense small-width contraction of the selected path-pair mode Gram."""
    first, second = crossed_middle_paths()
    left = path4_tensor(q, first)
    right = path4_tensor(q, second)
    return np.einsum("ajkl,bjkl->ab", left, right, optimize=True)


def crossed_middle_gram_formula(q: np.ndarray) -> np.ndarray:
    """The same contraction as a Khatri--Rao quadratic Gram.

      H_ab = sum_jk Q_aj Q_bj (Q^2)_jk Q_ak Q_bk.

    Materialising all H_ab by this formula is a generic n^4 operation.
    """
    q = _require_symmetric(q)
    r2 = q @ q
    return np.einsum("aj,bj,jk,ak,bk->ab", q, q, r2, q, q, optimize=True)


def crossed_middle_matvec_formula(q: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Exact O(n^3) matvec for the crossed-middle Gram.

    C = Q diag(x) Q and Hx = diag(Q[(Q^2) circ C]Q).  The final diagonal is
    formed as a rowwise product, so it needs no second dense matmul.
    """
    q = _require_symmetric(q)
    x = np.asarray(x, dtype=np.float64)
    if x.shape != (q.shape[0],):
        raise ValueError("x has wrong shape")
    r2 = q @ q
    c = (q * x[None, :]) @ q
    qb = q @ (r2 * c)
    return np.sum(qb * q, axis=1)


def crossed_middle_khatri_rao(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Explicit n^2-by-n factors B,C such that H=B^T diag(vec Q) C.

    This is only a small-width reference; it makes the n^4 shaped matmul
    visible to the cost audit.
    """
    q = _require_symmetric(q)
    n = q.shape[0]
    # B_(j,k),a = Q_aj Q_ak.  The other factor is the same here because Q is
    # symmetric; keeping two objects makes the general contraction explicit.
    b = np.einsum("aj,ak->jka", q, q, optimize=True).reshape(n * n, n)
    return b, b.copy()


def path_pair_post_b_elimination_width(
    first: tuple[int, int, int, int], second: tuple[int, int, int, int]
) -> int:
    """Minimum induced width after contracting b (mode-1 of the right term).

    ``a`` is position 0 of the left tensor and is retained; the three remaining
    tensor labels are 1,2,3.  A width <=2 means every individual path-pair
    *matvec* admits a matrix/Hadamard contraction of O(n^3), even though the
    explicit n-by-n Gram can be O(n^4).
    """
    # Vertices: A is the retained left root.  Labels 1..3 are shared internal
    # variables; B is the summed right root.  In both tensors position 0 is
    # their root, hence first/second use that same positional convention.
    root_a, root_b = "a", "b"
    def relabel(path: tuple[int, int, int, int], root: str) -> tuple[object, ...]:
        return tuple(root if item == 0 else item for item in path)

    graph: dict[object, set[object]] = {root_a: set(), root_b: set(), 1: set(), 2: set(), 3: set()}
    for path, root in ((first, root_a), (second, root_b)):
        named = relabel(path, root)
        for u, v in zip(named[:-1], named[1:]):
            graph[u].add(v)
            graph[v].add(u)

    # Sum b with x.  If b was a degree-two middle vertex, the weighted
    # contraction produces a rank-two factor on its neighbours.
    neigh = tuple(graph[root_b])
    for u in neigh:
        graph[u].discard(root_b)
    del graph[root_b]
    if len(neigh) == 2:
        u, v = neigh
        graph[u].add(v)
        graph[v].add(u)

    def width_for_order(order: Iterable[int]) -> int:
        work = {u: set(v) for u, v in graph.items()}
        width = 0
        for victim in order:
            ns = tuple(work[victim])
            width = max(width, len(ns))
            for u, v in itertools.combinations(ns, 2):
                work[u].add(v)
                work[v].add(u)
            for u in ns:
                work[u].discard(victim)
            del work[victim]
        return width

    return min(width_for_order(order) for order in itertools.permutations((1, 2, 3)))


def all_path_pair_widths() -> dict[str, int]:
    """A proof-by-finite-enumeration of the 12x12 path-pair matvec width."""
    widths = [path_pair_post_b_elimination_width(p, q) for p in PATHS4 for q in PATHS4]
    return {"count": len(widths), "max": max(widths), "min": min(widths)}


def four_core_from_paths(q: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Projected all-index tree4 core, without forming the order-four tensor.

    This is a small-width verifier.  At target rank r, each ordered core entry
    is the path contraction a^T Q diag(b) Q diag(c) Q d, summed over the 12
    labelled paths.  Symmetric-core charging can therefore use 36 Q matvecs
    per unordered r^4 entry, exactly as M85's source ledger stated.
    """
    q = _require_symmetric(q)
    u = np.asarray(u, dtype=np.float64)
    if u.ndim != 2 or u.shape[0] != q.shape[0]:
        raise ValueError("u has wrong shape")
    r = u.shape[1]
    core = np.zeros((r, r, r, r), dtype=np.float64)
    for output in itertools.product(range(r), repeat=4):
        vectors = [u[:, item] for item in output]
        value = 0.0
        for path in PATHS4:
            a, b, c, d = (vectors[pos] for pos in path)
            scratch = q @ d
            scratch *= c
            scratch = q @ scratch
            scratch *= b
            scratch = q @ scratch
            value += float(a @ scratch)
        core[output] = value
    return core


def standardized_physical_factor(u_standard: np.ndarray, scale: np.ndarray) -> np.ndarray:
    """Gauge-covariant physical Tucker factor V=D_scale U_standard."""
    u_standard = np.asarray(u_standard, dtype=np.float64)
    scale = np.asarray(scale, dtype=np.float64)
    if scale.shape != (u_standard.shape[0],) or np.any(scale <= 0.0):
        raise ValueError("scale must be positive and match u_standard")
    return scale[:, None] * u_standard
