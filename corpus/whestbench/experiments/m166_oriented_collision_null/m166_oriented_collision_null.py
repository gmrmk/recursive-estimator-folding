"""M166 oriented all-collision-null covariance-star control.

This response-free module changes one algebraic mechanism only.  It derives a
permutation/gauge-covariant node score from each correlation row, orients
non-tied covariance edges into disjoint matrices A and B=A.T, and uses

    c[i,j,k] = -(A[i,j] B[i,k] + B[i,j] A[i,k]).

The deterministic compiler consumes A/B directly (seven dense products); a
cubic table exists only as a small-width test oracle.  No response, target
outcome, scorer, or competition resource is accessed.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
M156 = ROOT / "m156_extended_domain_star_control"
if str(M156) not in sys.path:
    sys.path.insert(0, str(M156))

from m156_extended_domain_star_control import Source211  # noqa: E402


TARGET_COMPILER_CAP = 14_019_121_200
WIDTH = 256
SOURCE_LAYERS = 31
PROTECTION = 1.25


@dataclass(frozen=True)
class OrientedEdges:
    """One stored control object shared by deterministic and residual arms."""

    correlation: np.ndarray
    score: np.ndarray
    a: np.ndarray
    b: np.ndarray
    tied_pair_count: int


def _finite_symmetric_positive_diagonal(covariance: np.ndarray, dtype) -> np.ndarray:
    value = np.asarray(covariance, dtype=dtype)
    if value.ndim != 2 or value.shape[0] != value.shape[1] or value.shape[0] < 3:
        raise ValueError("covariance must be a finite square matrix of width at least three")
    if not np.all(np.isfinite(value)):
        raise ValueError("covariance must be finite")
    tolerance = 3e-6 if value.dtype == np.float32 else 2e-13
    if not np.allclose(value, value.T, rtol=0.0, atol=tolerance):
        raise ValueError("covariance must be symmetric")
    value = np.asarray(0.5 * (value + value.T), dtype=dtype)
    if np.any(np.diag(value) <= 0.0):
        raise ValueError("covariance must have a strictly positive diagonal")
    return value


def orient_covariance_edges(covariance: np.ndarray, *, dtype=None) -> OrientedEdges:
    """Orient covariance edges by the off-diagonal max-correlation score.

    ``s_i=max_{ell != i} R[i,ell]^2`` is a scalar function of the correlation
    row.  Max over a multiset is permutation-covariant, and correlation is
    invariant under a positive diagonal gauge in exact arithmetic.  If two
    scores compare equal in the working representation, their edge is assigned
    to neither support: no row index, axis, or unstable secondary tie-breaker
    is used.
    """

    raw = np.asarray(covariance)
    if dtype is None:
        dtype = raw.dtype if raw.dtype in (np.float32, np.float64) else np.float64
    dtype = np.dtype(dtype)
    if dtype not in (np.float32, np.float64):
        raise TypeError("M166 control supports only float32 or float64")
    scalar = dtype.type
    value = _finite_symmetric_positive_diagonal(raw, dtype)
    sigma = np.sqrt(np.diag(value), dtype=dtype)
    correlation = np.asarray(value / np.outer(sigma, sigma), dtype=dtype)
    correlation = np.asarray(0.5 * (correlation + correlation.T), dtype=dtype)
    np.fill_diagonal(correlation, scalar(1.0))
    if not np.all(np.isfinite(correlation)) or np.any(np.abs(correlation) > scalar(1.0) + scalar(5e-6)):
        raise ValueError("normalized covariance leaves the correlation domain")

    squared = np.asarray(correlation * correlation, dtype=dtype)
    # Only the diagonal is removed from the node statistic; no triple/collision
    # label is inspected anywhere in the orientation mechanism.
    np.fill_diagonal(squared, -np.inf)
    score = np.max(squared, axis=1)
    greater = score[:, None] > score[None, :]
    a = np.where(greater, value, scalar(0.0)).astype(dtype, copy=False)
    np.fill_diagonal(a, scalar(0.0))
    # This exact transpose establishes B=A.T and avoids a second possibly
    # divergent comparison.  At every ordered location A*B is exactly zero.
    b = np.ascontiguousarray(a.T)
    tied_pairs = int(np.count_nonzero(np.triu(score[:, None] == score[None, :], 1)))
    if not np.all(a * b == scalar(0.0)):
        raise AssertionError("orientation supports are not disjoint")
    return OrientedEdges(correlation, score, a, b, tied_pairs)


def oriented_star_value(control: OrientedEdges, i: int, j: int, k: int):
    """Return one coefficient from the stored A/B control, with no reorientation."""

    return -(control.a[i, j] * control.b[i, k] + control.b[i, j] * control.a[i, k])


def oriented_star_table(control: OrientedEdges) -> np.ndarray:
    """Small-width oracle only; deployment compiler never materializes this."""

    return -(
        control.a[:, :, None] * control.b[:, None, :]
        + control.b[:, :, None] * control.a[:, None, :]
    )


def _weight(weight: np.ndarray, width: int, dtype) -> np.ndarray:
    value = np.asarray(weight, dtype=dtype)
    if value.ndim != 2 or value.shape[0] != width or not np.all(np.isfinite(value)):
        raise ValueError("weight must be finite and have the control width")
    return value


def compile_oriented_star_control(weight: np.ndarray, control: OrientedEdges) -> Source211:
    """Exact seven-product all-domain source compiler for the stored A/B.

    With ZA=A W, ZB=B W, U=ZA o ZB, P=(W o U)^T W,
    QAB=(W^2 o ZA)^T ZB, QBA=(W^2 o ZB)^T ZA,
    R=(W^2)^T U, and S=(W o ZA)^T(W o ZB), the full ordered source is

      aaab = -3 (2P + QAB + QBA),
      aabb = -2(R+R^T) - 4(S+S^T),  aaaa=diag(aaab).

    The seven dense products are ZA, ZB, P, QAB, QBA, R, and S.  There is no
    cubic coefficient table, collision mask, Kronecker product, or Khatri--Rao
    action in this compiler.
    """

    dtype = np.result_type(weight, control.a, control.b)
    if dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("compiler supports float32/float64 inputs only")
    w = _weight(weight, control.a.shape[0], dtype)
    a = np.asarray(control.a, dtype=dtype)
    b = np.asarray(control.b, dtype=dtype)
    za = a @ w
    zb = b @ w
    w2 = w * w
    product = za * zb
    p = (w * product).T @ w
    qab = (w2 * za).T @ zb
    qba = (w2 * zb).T @ za
    r = w2.T @ product
    s = (w * za).T @ (w * zb)
    aaab = np.asarray(-3.0, dtype=dtype) * (2.0 * p + qab + qba)
    aabb = np.asarray(-2.0, dtype=dtype) * (r + r.T) - np.asarray(4.0, dtype=dtype) * (s + s.T)
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def residual_table_from_control(target: np.ndarray, control: OrientedEdges) -> np.ndarray:
    """Test/proof helper: subtract precisely the already-stored A/B control."""

    value = np.asarray(target)
    table = oriented_star_table(control)
    if value.shape != table.shape:
        raise ValueError("target/control shapes differ")
    return value - table.astype(value.dtype, copy=False)


def f32_shared_control_report(target: np.ndarray, covariance: np.ndarray) -> dict[str, object]:
    """State the finite-precision semantics without pretending bitwise exactness.

    The *same* stored float32 A/B object is given to both the deterministic
    compiler and the residual subtraction API.  ``c+(target-c)`` is therefore
    the intended numerical conservation identity, but IEEE subtraction/addition
    need not reconstruct every target coefficient bit-for-bit.  Positive-gauge
    covariance is likewise a real-arithmetic theorem, not an f32 bitwise claim
    near score ties.
    """

    control = orient_covariance_edges(covariance, dtype=np.float32)
    target32 = np.asarray(target, dtype=np.float32)
    residual = residual_table_from_control(target32, control)
    reconstructed = oriented_star_table(control) + residual
    return {
        "same_control_object_used_by_both_arms": True,
        "control_dtype": str(control.a.dtype),
        "coefficient_reconstruction_max_abs": float(
            np.max(np.abs(reconstructed - target32))
        ),
        "bitwise_coefficient_reconstruction": bool(
            np.array_equal(reconstructed, target32)
        ),
        "f32_gauge_is_bitwise_certified": False,
        "tie_semantics": "equal computed float32 scores assign A_ij=B_ij=0",
    }


def static_cost_ledger(width: int = WIDTH, layers: int = SOURCE_LAYERS) -> dict[str, int | float | bool | str]:
    """Conservative target accounting, including correlation/orientation/copies."""

    n, count = int(width), int(layers)
    f32_square = 2 * n**3 - n**2
    f32_one_protected = int(math.ceil(PROTECTION * count * f32_square))
    f64_one_protected = 2 * f32_one_protected
    # Per layer: correlation/score (10 n^2), orientation (10 n^2), compiler
    # pointwise transforms (28 n^2), and casts/copies/shared-residual state
    # (16 n^2).  It intentionally overcharges 64 n^2 by the same 1.25 factor.
    scalar_copy_allowance = int(math.ceil(PROTECTION * count * 64 * n**2))
    f32_products = 7 * f32_one_protected
    f64_products = 7 * f64_one_protected
    f32_total = f32_products + scalar_copy_allowance
    f64_total = f64_products + 2 * scalar_copy_allowance
    return {
        "candidate": "M166 oriented all-collision-null covariance-star compiler",
        "width": n,
        "layers": count,
        "protection": PROTECTION,
        "f32_dense_products": 7,
        "exact_f64_dense_products": 7,
        "f32_one_square_product_all_layers_protected": f32_one_protected,
        "f64_one_square_product_all_layers_protected": f64_one_protected,
        "f32_seven_product_bill": f32_products,
        "exact_f64_seven_product_bill": f64_products,
        "f32_orientation_correlation_copy_allowance": scalar_copy_allowance,
        "exact_f64_orientation_correlation_copy_allowance": 2 * scalar_copy_allowance,
        "f32_static_total": f32_total,
        "exact_f64_static_total": f64_total,
        "cap": TARGET_COMPILER_CAP,
        "f32_static_margin": TARGET_COMPILER_CAP - f32_total,
        "exact_f64_margin": TARGET_COMPILER_CAP - f64_total,
        "f32_static_fits_cap": f32_total <= TARGET_COMPILER_CAP,
        "exact_f64_fits_cap": f64_total <= TARGET_COMPILER_CAP,
        "no_cubic_table_or_khatri_in_compiler": True,
        "f32_requires_shared_control_and_numerical_conservation_gate": True,
    }
