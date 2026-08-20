"""Output-slice contractions for the quadratic aabc ReLU collision jet.

This module deliberately contains only generated-array algebra.  It neither
loads a network nor estimates a contest target.  The source is the symmetric
four-tensor with, for distinct i,j,k,

    K[i,i,j,k] = (q[i,j]*q[i,k] + q[i,j]*q[j,k] + q[i,k]*q[j,k])/(4*pi),

scattered over its twelve slots.  The functions below exploit the fact that
only (aaab,aabb) output slices are requested after one affine transport.
"""

from __future__ import annotations

import math
from typing import Final

import numpy as np

QUADRATIC_JET_COEFFICIENT: Final[float] = 1.0 / (4.0 * math.pi)


def _check(q: np.ndarray, weight: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q = np.asarray(q, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("q must be square")
    if weight.ndim != 2 or weight.shape[0] != q.shape[0]:
        raise ValueError("weight must have q.shape[0] rows")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(weight)):
        raise ValueError("inputs must be finite")
    if not np.allclose(q, q.T, rtol=0.0, atol=2e-12):
        raise ValueError("q must be symmetric")
    if not np.allclose(np.diag(q), 1.0, rtol=0.0, atol=2e-12):
        raise ValueError("q must have unit diagonal")
    return q, weight


def defect211_quadratic_jet(q: np.ndarray) -> np.ndarray:
    """The exact [2,1,1] tensor for the M118 quadratic jet, on its support."""
    q = np.asarray(q, dtype=np.float64)
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("q must be square")
    n = q.shape[0]
    out = np.zeros((n, n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    out[i, j, k] = QUADRATIC_JET_COEFFICIENT * (
                        q[i, j] * q[i, k]
                        + q[i, j] * q[j, k]
                        + q[i, k] * q[j, k]
                    )
    return out


def aaab_quadratic_jet_exact(q: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """Exact O(n^3) aaab table of the twelve-slot quadratic collision source.

    Let S=q-I, P=qW, and D=S* S (Hadamard square).  For each repeated source
    label i, the ordered singleton-pair aggregate is

      V_i = sum_(j,k distinct from i,j!=k) F_ijk W_j*W_k,

    and, for each distinguished singleton j,

      U_j = sum_(i,k distinct) F_ijk W_i^2*W_k.

    The twelve output slot placements then reduce exactly to

      3 (W*V)^T W + 3 U^T W.

    All products in the displayed identities are entrywise except @.  This
    is an output-aligned identity, not a low-rank approximation.
    """
    q, w = _check(q, weight)
    n = q.shape[0]
    s = q - np.eye(n, dtype=np.float64)
    s2 = s * s
    w2 = w * w
    w3 = w2 * w
    p = q @ w
    a = s @ w
    d = s @ w2
    s2w = s2 @ w
    s2w2 = s2 @ w2

    # V_i: xy plus the two equal xz/yz contributions.  B<->C symmetry doubles
    # only the latter, not the xy term.
    v_xy = a * a - s2 @ w2
    v_xz = s @ (w * p) - s2w * w - s @ w2
    v = QUADRATIC_JET_COEFFICIENT * (v_xy + 2.0 * v_xz)

    # U_j: all three monomials with j as the output-side singleton.
    u_xy = s @ (w2 * p) - s @ w3 - s2w2 * w
    u_xz = d * p - s2 @ w3 - d * w
    u_yz = s @ (w * d) - s2w * w2
    u = QUADRATIC_JET_COEFFICIENT * (u_xy + u_xz + u_yz)

    return 3.0 * ((w * v).T @ w + u.T @ w)


def aaab_quadratic_jet_physical(
    q: np.ndarray, scales: np.ndarray, downstream_weight: np.ndarray
) -> np.ndarray:
    """Physical-scale wrapper for the standardized quadratic source.

    If ``z_i=scales_i*y_i``, every collision tensor slot supplies one scale,
    so affine transport uses ``effective_weight_i=scales_i*downstream_weight_i``.
    This makes the positive diagonal ReLU gauge explicit rather than assuming
    unit variances in a place where it would silently break covariance.
    """
    q, downstream_weight = _check(q, downstream_weight)
    scales = np.asarray(scales, dtype=np.float64)
    if scales.shape != (q.shape[0],) or not np.all(np.isfinite(scales)) or np.any(scales <= 0):
        raise ValueError("scales must be finite and strictly positive")
    return aaab_quadratic_jet_exact(q, scales[:, None] * downstream_weight)


def aabb_quadratic_jet_split(q: np.ndarray, weight: np.ndarray) -> dict[str, np.ndarray]:
    """Expose the exact easy term and the unresolved hard aabb contraction.

    The repeated-pair placements are exactly ``W^2.T@V + V.T@W^2``.  The
    split-pair placements are an exact sum of three matrix-valued contractions
    C_xy+C_xz+C_yz.  They are returned only by the small-width reference in
    :func:`aabb_quadratic_jet_reference`; forming all of them generically is
    the same fourth-order obstruction that M126 estimates with Rademacher
    probes or a certified low-rank bridge residual.  This explicit split keeps
    the repair honest: no source mass is silently dropped.
    """
    q, w = _check(q, weight)
    n = q.shape[0]
    s = q - np.eye(n, dtype=np.float64)
    s2 = s * s
    w2 = w * w
    p = q @ w
    a = s @ w
    v_xy = a * a - s2 @ w2
    v_xz = s @ (w * p) - (s2 @ w) * w - s @ w2
    v = QUADRATIC_JET_COEFFICIENT * (v_xy + 2.0 * v_xz)
    repeated_pair = w2.T @ v + v.T @ w2
    return {"repeated_pair_exact": repeated_pair, "v": v}


def aabb_quadratic_jet_reference(q: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """Dense small-width oracle for the full aabb slice; O(n^5) by design."""
    q, w = _check(q, weight)
    n, outputs = w.shape
    answer = np.zeros((outputs, outputs), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                # every choice of repeated label and unordered singleton pair
                for repeated, left, right in ((i, j, k), (j, i, k), (k, i, j)):
                    f = QUADRATIC_JET_COEFFICIENT * (
                        q[repeated, left] * q[repeated, right]
                        + q[repeated, left] * q[left, right]
                        + q[repeated, right] * q[left, right]
                    )
                    wi, wj, wk = w[repeated], w[left], w[right]
                    answer += f * (
                        2.0 * (np.outer(wi * wi, wj * wk) + np.outer(wj * wk, wi * wi))
                        + 4.0 * (np.outer(wi * wj, wi * wk) + np.outer(wi * wk, wi * wj))
                    )
    return answer


def aabb_quadratic_jet_probe_sample(
    q: np.ndarray, weight: np.ndarray, probe: np.ndarray
) -> np.ndarray:
    """One unbiased full-aabb sample for the quadratic aabc source.

    This is a direct Rademacher contraction, not an assertion that the aabb
    table is low rank.  The three split-pair monomials need eight square-GEMM
    equivalents after sharing ``S@(z*W)``: six for their products and two to
    remove the illegal j=k diagonal in the xy term.  The i=k and i=j illegal
    diagonals in xz and yz are removed exactly by two deterministic GEMMs.
    Averaging all 2^n signs gives :func:`aabb_quadratic_jet_reference`.
    """
    q, w = _check(q, weight)
    z = np.asarray(probe, dtype=np.float64)
    if z.shape != (q.shape[0],) or not np.all(np.isfinite(z)):
        raise ValueError("probe must be a finite source-width vector")
    n = q.shape[0]
    s = q - np.eye(n, dtype=np.float64)
    h = s * s
    a = s @ w
    t = s @ (z[:, None] * w)
    sz = s @ z

    # xy, including a separate probe estimate of its forbidden j=k diagonal.
    xy = ((w * a).T @ (z[:, None] * w)) * ((s @ z) @ w)[None, :]
    collision_xy = (w.T @ (z[:, None] * w)) * (w.T @ ((h @ z)[:, None] * w))

    # xz: the common singleton j is sketched; remove k=i exactly.
    xz = ((w * t).T @ w) * ((s @ z) @ w)[None, :]
    correction_xz = (w * (h @ w)).T @ (w * w)

    # yz: the common singleton k is sketched; remove i=j exactly.
    yz = (w.T @ (sz[:, None] * w)) * (w.T @ t)
    correction_yz = (w * w).T @ (w * (h @ w))

    return (
        aabb_quadratic_jet_split(q, w)["repeated_pair_exact"]
        + 4.0
        * QUADRATIC_JET_COEFFICIENT
        * (xy - collision_xy + xz - correction_xz + yz - correction_yz)
    )


def flopscope_aabc_ledger(
    *, width: int = 256, layers: int = 31, dtype: str = "float64", probes: int = 0,
    safety_factor: float = 1.25,
) -> dict[str, int | float | str]:
    """Conservative declared bill for the new exact aaab and probe aabb arm.

    Eleven square GEMM-equivalents construct V/U and contract aaab per source
    layer.  The aabb repeated-pair term reuses V and costs two more, and the
    two deterministic forbidden-diagonal corrections cost two more.  Each
    Rademacher aabb sample is charged eight square calls, including the
    collision-removal sample.  A retained-factor implementation has not been
    derived and must not borrow this stochastic bill.
    Scalar Hadamard/copy work is reserved separately rather than called free.
    """
    if dtype not in {"float32", "float64"}:
        raise ValueError("dtype must be float32 or float64")
    if width <= 0 or layers <= 0 or probes < 0 or safety_factor < 1:
        raise ValueError("invalid ledger parameters")
    square32 = 2 * width**3 - width**2
    square = square32 if dtype == "float32" else 2 * square32
    exact_calls = 15
    probe_calls = 8 * probes
    scalar_reserve_per_layer = 30 * width * width
    raw = layers * ((exact_calls + probe_calls) * square + scalar_reserve_per_layer)
    return {
        "dtype": dtype,
        "square_call_bill": square,
        "exact_square_calls_per_layer": exact_calls,
        "aabb_hard_square_calls_per_probe": 8,
        "probes_or_modes": probes,
        "layers": layers,
        "raw_flops": raw,
        "effective_flops": int(math.ceil(raw * safety_factor)),
        "aabb_hard_is_exact": False,
        "status": "exact_aaab_and_repeated_aabb_only" if probes == 0 else "unbiased_full_aabb_quadratic_jet_probe",
    }
