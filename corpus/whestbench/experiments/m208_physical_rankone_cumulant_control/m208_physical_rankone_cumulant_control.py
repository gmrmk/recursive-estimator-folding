"""M208 response-free physical rank-one fourth-cumulant control.

The production identity projects one rank-one factor through the current
weight and emits the three repeated-output fourth-source slots. It does not
construct a label-cubic coefficient table or a label-square Gram. Independent
small-width owner enumeration lives only in the test module.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray
DEFAULT_KAPPA = -2.0
STRICT_COMPOSED_HEADROOM = 1_986_871_472


@dataclass(frozen=True)
class Source211:
    """Repeated-output fourth-source slots consumed by the forward carrier."""

    aaaa: Array
    aaab: Array
    aabb: Array


def _checked_inputs(weight: Array, factor: Array, kappa: float) -> tuple[Array, Array, float]:
    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    scale = float(kappa)
    if w.ndim != 2 or w.shape[0] < 3 or w.shape[1] < 1:
        raise ValueError("weight must be a finite labelled matrix")
    if u.ndim != 1 or u.shape[0] != w.shape[0]:
        raise ValueError("factor must match the weight's labelled axis")
    if not np.all(np.isfinite(w)) or not np.all(np.isfinite(u)) or not math.isfinite(scale):
        raise ValueError("weight, factor, and kappa must be finite")
    return w, u, scale


def compile_physical_rankone_control(
    weight: Array, factor: Array, kappa: float = DEFAULT_KAPPA
) -> Source211:
    """Compile the physical owner table of ``kappa*u^tensor4`` via ``p=W^T u``.

    Physical `[4]`, `[3,1]`, `[2,2]`, and `[2,1,1]` multiplicities make the
    complete source exactly multilinear. Consequently the output needs only
    the projected vector and two outer products.
    """

    w, u, scale = _checked_inputs(weight, factor, kappa)
    p = w.T @ u
    p2 = p * p
    p3 = p2 * p
    aaab = scale * np.outer(p3, p)
    aabb = scale * np.outer(p2, p2)
    aaaa = np.diag(aaab).copy()
    return Source211(aaaa=aaaa, aaab=aaab, aabb=aabb)


def source_max_abs_difference(left: Source211, right: Source211) -> float:
    """Maximum slotwise absolute difference for response-free parity tests."""

    return float(
        max(
            np.max(np.abs(np.asarray(left.aaaa) - np.asarray(right.aaaa))),
            np.max(np.abs(np.asarray(left.aaab) - np.asarray(right.aaab))),
            np.max(np.abs(np.asarray(left.aabb) - np.asarray(right.aabb))),
        )
    )


def static_operation_ledger(width: int = 256, layers: int = 31) -> dict[str, object]:
    """Conservative response-free arithmetic envelope, not a native trace."""

    if width < 3 or layers < 1:
        raise ValueError("width and layers must be positive target-like integers")
    projection_per_layer_f32 = 2 * width * width - width
    projection_bill = 2 * layers * projection_per_layer_f32
    pointwise_upper_per_layer = 4 * width * width + 4 * width
    pointwise_upper = layers * pointwise_upper_per_layer
    declared_raw_upper = projection_bill + pointwise_upper
    return {
        "width": width,
        "layers": layers,
        "projection_bill": projection_bill,
        "pointwise_upper": pointwise_upper,
        "declared_raw_upper": declared_raw_upper,
        "strict_composed_headroom": STRICT_COMPOSED_HEADROOM,
        "dense_square_calls": 0,
        "bias_class": "invalid_for_current_owner_domain_missing_1111",
        "candidate_gate_passed": False,
        "native_cost_certified": False,
        "fits_static_necessary_gate": declared_raw_upper < STRICT_COMPOSED_HEADROOM,
        "unpaid_terms": [
            "physical residual coefficient provider",
            "M198 conversion",
            "terminal response",
            "copies and allocations",
            "residual wall time",
        ],
    }
