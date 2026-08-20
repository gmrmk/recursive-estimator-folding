"""M163: a collision-null exterior-star control, response-free only.

M156's control ``-2 V_ij V_ik`` was algebraically cheap but nonzero on every
collision pattern.  M163 changes exactly that coefficient mechanism.  Let R
be the correlation of the already-present positive-diagonal Gaussian
covariance V and let

    G_ij = det([[1, R_ij], [R_ij, 1]]) = 1 - R_ij**2,
    A_ij = V_ij G_ij,
    c^E_ijk = -2 A_ij A_ik.

G is the squared exterior area of two normalized covariance directions.  It
is canonical under hidden permutations and positive ReLU gauge, has no chosen
axis or tie-break, and makes c^E exactly zero when i=j or i=k.  Thus it kills
the iii, iik, and iji collision strata by construction without a Kronecker
mask or a Khatri--Rao action.  The ijj stratum is intentionally retained and
must be measured separately by a fresh future premise.

The all-domain control retains the exact M156 add/subtract identity.  This
module contains no estimator, neural-network output, truth, scorer, or
competition-facing code.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for _relative in (
    "m156_extended_domain_star_control",
    "m161_response_free_source_variance",
):
    _path = str(ROOT / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m156_extended_domain_star_control import (  # noqa: E402
    Source211,
    collision_count,
    collision_strata,
    compiled_extended_star_control,
    dense_extended_source,
    distinct_target_extension,
    extended_feature,
    residual_table,
    source_add,
    source_max_abs_difference,
)
from m161_response_free_variance import (  # noqa: E402
    ORDERED_OWNER,
    TARGET_COLLISION_MASS,
    frozen_cells,
    frozen_probability,
)


TARGET_COMPILER_CAP = 14_019_121_200
PROTECTED_F64_SQUARE_PRODUCT_ALL_LAYERS = 2_595_389_440
SOURCE_LAYERS = 31
WIDTH = 256


@dataclass(frozen=True)
class CollisionDiagnostic:
    pattern: str
    second_moment: float
    second_fraction: float
    conditional_p99_squared: float
    global_p99_ratio: float
    units: int


def _covariance(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float64)
    if (
        value.ndim != 2
        or value.shape[0] != value.shape[1]
        or not np.all(np.isfinite(value))
        or not np.allclose(value, value.T, rtol=0.0, atol=2.0e-13)
    ):
        raise ValueError("V must be a finite exactly symmetric matrix")
    # Finite multiplication under a legal positive gauge can differ only in
    # operation order above/below the diagonal.  Exact re-symmetrization is a
    # representation repair, not a ridge, projection, or statistical change.
    value = 0.5 * (value + value.T)
    if np.any(np.diag(value) <= 0.0):
        raise ValueError("V must have strictly positive diagonal")
    return value


def exterior_edge_matrix(covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return R, its two-vector Gram determinant G, and A=V o G.

    No clipping/ridge is applied.  A covariance whose normalized off-diagonal
    magnitudes materially leave [-1,1] is rejected.  A diagonal/isotropic V
    gives A=0 exactly: this is the specified tied/isotropic zero-control
    fallback, not an adaptive substitute.
    """

    value = _covariance(covariance)
    sigma = np.sqrt(np.diag(value))
    correlation = value / np.outer(sigma, sigma)
    correlation = 0.5 * (correlation + correlation.T)
    np.fill_diagonal(correlation, 1.0)
    if np.any(np.abs(correlation) > 1.0):
        raise ValueError("normalized covariance violates the correlation domain")
    # The diagonal is set exactly above; close exterior factors are permitted
    # to be small but never rounded/clipped to an arbitrary threshold.
    exterior = 1.0 - correlation * correlation
    if np.any(exterior < 0.0) or not np.all(np.isfinite(exterior)):
        raise ValueError("exterior Gram determinant is invalid")
    np.fill_diagonal(exterior, 0.0)
    edge = value * exterior
    edge = 0.5 * (edge + edge.T)
    np.fill_diagonal(edge, 0.0)
    return correlation, exterior, edge


def exterior_star_table(covariance: np.ndarray) -> np.ndarray:
    """M163 full-domain coefficient, zero whenever i=j or i=k."""

    _, _, edge = exterior_edge_matrix(covariance)
    return -2.0 * edge[:, :, None] * edge[:, None, :]


def compile_exterior_star_control(weight: np.ndarray, covariance: np.ndarray) -> Source211:
    """Exact five-product compiler: reuse M156 with edge matrix A, not V."""

    _, _, edge = exterior_edge_matrix(covariance)
    return compiled_extended_star_control(weight, edge)


def _source_vector(source: Source211) -> np.ndarray:
    return np.concatenate((source.aaaa.ravel(), source.aaab.ravel(), source.aabb.ravel()))


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    order = np.argsort(values, kind="mergesort")
    threshold = quantile * float(np.sum(weights))
    slot = int(np.searchsorted(np.cumsum(weights[order]), threshold, side="left"))
    return float(values[order[min(slot, values.size - 1)]])


def _pattern(unit: tuple[int, int, int]) -> str:
    i, j, k = unit
    if i == j == k:
        return "iii"
    if i == j:
        return "iik"
    if i == k:
        return "iji"
    if j == k:
        return "ijj"
    return "distinct"


def collision_diagnostics(
    coefficient: np.ndarray,
    weight: np.ndarray,
    *,
    probability=frozen_probability,
) -> tuple[CollisionDiagnostic, ...]:
    """Exact HH second-moment/p99 decomposition by four disjoint patterns."""

    value = np.asarray(coefficient, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)
    width = value.shape[0]
    if value.shape != (width, width, width) or w.shape[0] != width:
        raise ValueError("coefficient/weight dimensions disagree")
    units = [(i, j, k) for i in range(width) for j in range(width) for k in range(width)]
    q = np.asarray([probability(width, unit) for unit in units], dtype=np.float64)
    vectors = np.asarray(
        [ORDERED_OWNER * value[unit] * _source_vector(extended_feature(w, *unit)) / mass for unit, mass in zip(units, q)],
        dtype=np.float64,
    )
    squared = np.einsum("ij,ij->i", vectors, vectors)
    total = float(np.dot(q, squared))
    global_p99 = _weighted_quantile(squared, q, 0.99)
    answer: list[CollisionDiagnostic] = []
    for name in ("iii", "iik", "iji", "ijj"):
        mask = np.asarray([_pattern(unit) == name for unit in units], dtype=bool)
        second = float(np.dot(q[mask], squared[mask]))
        local_p99 = _weighted_quantile(squared[mask], q[mask], 0.99)
        answer.append(CollisionDiagnostic(
            pattern=name,
            second_moment=second,
            second_fraction=(second / total if total > 0.0 else 0.0),
            conditional_p99_squared=local_p99,
            global_p99_ratio=(local_p99 / global_p99 if global_p99 > 0.0 else math.inf),
            units=int(np.sum(mask)),
        ))
    return tuple(answer)


def decompose_open_m161_collision_tail() -> list[dict[str, object]]:
    """Diagnostic only: use already-open M161 cells, never a promotion set."""

    records: list[dict[str, object]] = []
    for cell in frozen_cells():
        # M161 collision target is zero, therefore its collision residual is
        # exactly -c.  No M147 target call is needed or reopened here.
        old_control = -2.0 * cell.covariance[:, :, None] * cell.covariance[:, None, :]
        old_collision_residual = -old_control
        records.append({
            "name": cell.name,
            "width": cell.width,
            "diagnostic_only_not_promotion": True,
            "patterns": [diagnostic.__dict__ for diagnostic in collision_diagnostics(old_collision_residual, cell.weight)],
        })
    return records


def static_compiler_ledger() -> dict[str, int | float | bool | str]:
    """Conservative static accounting for a target-width M163 compiler.

    The five dense products are exactly M156's five-product source compiler.
    The explicit 0.100B allowance covers all 31 covariance normalizations,
    exterior edge arithmetic, finite checks, source-vector bookkeeping, and
    copies.  It is a static arithmetic allowance, not a native wall-time
    certificate or sharing credit.
    """

    five_products = 5 * PROTECTED_F64_SQUARE_PRODUCT_ALL_LAYERS
    conservative_pointwise = 100_000_000
    total = five_products + conservative_pointwise
    return {
        "candidate": "M163 exterior collision-null star control compiler only",
        "width": WIDTH,
        "layers": SOURCE_LAYERS,
        "dense_f64_products": 5,
        "protected_five_product_bill": five_products,
        "conservative_normalization_exterior_copy_allowance": conservative_pointwise,
        "total_static_compiler_bill": total,
        "cap": TARGET_COMPILER_CAP,
        "margin": TARGET_COMPILER_CAP - total,
        "no_kronecker_mask_or_khatri_action": True,
        "fits_cap": total <= TARGET_COMPILER_CAP,
        "native_trace_still_required": True,
    }


def structural_conservation_check(weight: np.ndarray, target: np.ndarray, covariance: np.ndarray) -> float:
    """Exhaustive small-width proof of the M163 full-domain add/subtract law."""

    target = distinct_target_extension(target)
    control = exterior_star_table(covariance)
    residual = residual_table(target, control)
    direct = dense_extended_source(weight, target)
    reconstructed = source_add(
        compile_exterior_star_control(weight, covariance),
        dense_extended_source(weight, residual),
    )
    return source_max_abs_difference(direct, reconstructed)
