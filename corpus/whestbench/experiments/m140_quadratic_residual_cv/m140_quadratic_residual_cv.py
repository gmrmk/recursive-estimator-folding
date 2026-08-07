"""M140: exact quadratic-jet / residual partition for the ``[2,1,1]`` source.

This is a theory-first, generated-array-only module.  It does not load a
challenge model, a scorer, a leaderboard, a submission archive, or a target
outcome.

For distinct standardized bridge labels ``(i,j,k)`` write

``D_ijk = exact connected-minus-tree [2,1,1] coefficient``
``J_ijk = (Q_ij Q_ik + Q_ij Q_jk + Q_ik Q_jk)/(4*pi)``.

The proposed control-variate identity is exact *on the already-owned [2,1,1]
support*:

``D = J + R``, where ``R = D-J``.

The module deliberately distinguishes this identity from a deployable
estimator.  M130 proves that the full masked ``J`` aabb table has a split-pair
Khatri--Rao diagonal contraction.  No cubic deterministic contraction for
that table is installed here.  Consequently the pre-execution cost gate is
closed rather than silently turning the leftover jet into an uncharged
approximation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

import numpy as np


Array = np.ndarray
ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "m126_repeated_output_source_contraction",
    "m130_direct_aabc_collision",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m130_direct_aabc_collision import (  # noqa: E402
    QUADRATIC_JET_COEFFICIENT,
    aabb_quadratic_jet_reference,
    aabb_quadratic_jet_split,
    aaab_quadratic_jet_exact,
    defect211_quadratic_jet,
)


def _bridge(value: Array) -> Array:
    value = np.asarray(value, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("bridge must be square")
    if not np.all(np.isfinite(value)) or not np.allclose(value, value.T, rtol=0.0, atol=2e-12):
        raise ValueError("bridge must be finite and symmetric")
    if not np.allclose(np.diag(value), 1.0, rtol=0.0, atol=2e-12):
        raise ValueError("bridge must have unit diagonal")
    return value


def _hollow_symmetric(value: Array, name: str) -> Array:
    value = np.asarray(value, dtype=np.float64)
    if value.ndim != 3 or len(set(value.shape)) != 1:
        raise ValueError(f"{name} must have shape (n,n,n)")
    if not np.all(np.isfinite(value)) or not np.allclose(value, value.swapaxes(1, 2), rtol=0.0, atol=2e-12):
        raise ValueError(f"{name} must be finite and symmetric in singleton labels")
    n = value.shape[0]
    for i in range(n):
        if np.any(value[i, i, :] != 0.0) or np.any(value[i, :, i] != 0.0) or np.any(np.diag(value[i]) != 0.0):
            raise ValueError(f"{name} must be hollow on every label collision")
    return value


def quadratic_211_coefficient(bridge: Array, repeated: int, left: int, right: int) -> float:
    """Owned M118/M130 quadratic jet, zero outside distinct ``[2,1,1]`` support."""

    bridge = _bridge(bridge)
    n = bridge.shape[0]
    if not all(0 <= item < n for item in (repeated, left, right)):
        raise IndexError("label out of range")
    if len({repeated, left, right}) != 3:
        return 0.0
    a = float(bridge[repeated, left])
    b = float(bridge[repeated, right])
    c = float(bridge[left, right])
    return QUADRATIC_JET_COEFFICIENT * (a * b + a * c + b * c)


def quadratic_211_coefficient_dot(
    bridge: Array,
    bridge_dot: Array,
    repeated: int,
    left: int,
    right: int,
) -> tuple[float, float]:
    """Quadratic jet and its exact Fréchet directional derivative."""

    bridge = _bridge(bridge)
    bridge_dot = np.asarray(bridge_dot, dtype=np.float64)
    if bridge_dot.shape != bridge.shape or not np.all(np.isfinite(bridge_dot)):
        raise ValueError("bridge_dot shape mismatch")
    if not np.allclose(bridge_dot, bridge_dot.T, rtol=0.0, atol=2e-12) or not np.allclose(np.diag(bridge_dot), 0.0, rtol=0.0, atol=2e-12):
        raise ValueError("bridge_dot must be symmetric with zero diagonal")
    if len({repeated, left, right}) != 3:
        return 0.0, 0.0
    a = float(bridge[repeated, left])
    b = float(bridge[repeated, right])
    c = float(bridge[left, right])
    da = float(bridge_dot[repeated, left])
    db = float(bridge_dot[repeated, right])
    dc = float(bridge_dot[left, right])
    value = QUADRATIC_JET_COEFFICIENT * (a * b + a * c + b * c)
    tangent = QUADRATIC_JET_COEFFICIENT * (da * (b + c) + db * (a + c) + dc * (a + b))
    return value, tangent


def quadratic_211_tensor(bridge: Array) -> Array:
    """Dense generated-only reference tensor for the owned quadratic support."""

    return defect211_quadratic_jet(_bridge(bridge))


@dataclass(frozen=True)
class QuadraticResidualPartition:
    """Exact source-level partition, with no fitted or outcome-derived scalar."""

    jet: Array
    residual: Array
    jet_tangent: Array | None = None
    residual_tangent: Array | None = None


def standardize_211_tensor(physical_defect: Array, relu_scale: Array) -> Array:
    """Remove the physical ``s_i^2 s_j s_k`` factor on `[2,1,1]` support.

    M131's conditional oracle returns a physical ReLU cumulant.  The M118
    quadratic jet is dimensionless in the normalized bridge.  Comparing them
    without this conversion is a units error.  In deployment the same factors
    are restored by transporting the standardized source with
    ``effective_weight = diag(relu_scale) @ downstream_weight``.
    """

    physical_defect = _hollow_symmetric(physical_defect, "physical_defect")
    scale = np.asarray(relu_scale, dtype=np.float64)
    n = physical_defect.shape[0]
    if scale.shape != (n,) or not np.all(np.isfinite(scale)) or np.any(scale <= 0.0):
        raise ValueError("relu_scale must be finite and strictly positive")
    standardized = np.zeros_like(physical_defect)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    standardized[i, j, k] = physical_defect[i, j, k] / (scale[i] * scale[i] * scale[j] * scale[k])
    return standardized


def standardize_211_tensor_dot(
    physical_defect: Array,
    physical_defect_dot: Array,
    relu_scale: Array,
    relu_scale_dot: Array,
) -> tuple[Array, Array]:
    """Standardize a physical source and its exact directional derivative."""

    physical_defect = _hollow_symmetric(physical_defect, "physical_defect")
    physical_defect_dot = _hollow_symmetric(physical_defect_dot, "physical_defect_dot")
    scale = np.asarray(relu_scale, dtype=np.float64)
    scale_dot = np.asarray(relu_scale_dot, dtype=np.float64)
    n = physical_defect.shape[0]
    if scale.shape != (n,) or scale_dot.shape != (n,) or not np.all(np.isfinite(scale)) or not np.all(np.isfinite(scale_dot)) or np.any(scale <= 0.0):
        raise ValueError("scale derivative shape/value mismatch")
    value = np.zeros_like(physical_defect)
    tangent = np.zeros_like(physical_defect)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) != 3:
                    continue
                denominator = scale[i] * scale[i] * scale[j] * scale[k]
                value[i, j, k] = physical_defect[i, j, k] / denominator
                log_dot = 2.0 * scale_dot[i] / scale[i] + scale_dot[j] / scale[j] + scale_dot[k] / scale[k]
                tangent[i, j, k] = physical_defect_dot[i, j, k] / denominator - value[i, j, k] * log_dot
    return value, tangent


def split_exact_211(
    exact_defect: Array,
    bridge: Array,
    *,
    exact_defect_dot: Array | None = None,
    bridge_dot: Array | None = None,
) -> QuadraticResidualPartition:
    """Return ``exact_defect = jet + residual`` on exactly the ``[2,1,1]`` slots.

    If derivatives are supplied, the same equality holds for their directional
    derivatives.  The function does not extend the jet to `[4]`, `[3,1]`, or
    `[2,2]`; doing so would transfer source ownership and would need a new
    complete residual population.
    """

    exact_defect = _hollow_symmetric(exact_defect, "exact_defect")
    bridge = _bridge(bridge)
    if exact_defect.shape[0] != bridge.shape[0]:
        raise ValueError("defect and bridge widths disagree")
    jet = quadratic_211_tensor(bridge)
    residual = exact_defect - jet

    if (exact_defect_dot is None) != (bridge_dot is None):
        raise ValueError("supply both derivative objects or neither")
    if exact_defect_dot is None:
        return QuadraticResidualPartition(jet, residual)

    exact_defect_dot = _hollow_symmetric(exact_defect_dot, "exact_defect_dot")
    bridge_dot = np.asarray(bridge_dot, dtype=np.float64)
    n = bridge.shape[0]
    jet_dot = np.zeros((n, n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    _, jet_dot[i, j, k] = quadratic_211_coefficient_dot(bridge, bridge_dot, i, j, k)
    return QuadraticResidualPartition(jet, residual, jet_dot, exact_defect_dot - jet_dot)


def deterministic_jet_partial_tables(bridge: Array, effective_weight: Array) -> dict[str, Array]:
    """The deterministic portion of the quadratic jet's M121 repeated tables.

    ``k4_aaaa`` is exactly the diagonal of the symmetric ``k4_aaab`` table.
    The returned ``k4_aabb_repeated_pair`` is exact, but does **not** include
    the split-pair term.  Keeping the distinction in the interface prevents
    an accidental incomplete M121 source.
    """

    bridge = _bridge(bridge)
    weight = np.asarray(effective_weight, dtype=np.float64)
    if weight.ndim != 2 or weight.shape[0] != bridge.shape[0] or not np.all(np.isfinite(weight)):
        raise ValueError("effective_weight shape mismatch")
    aaab = aaab_quadratic_jet_exact(bridge, weight)
    repeated_pair = aabb_quadratic_jet_split(bridge, weight)["repeated_pair_exact"]
    return {
        "k4_aaaa": np.diag(aaab).copy(),
        "k4_aaab": aaab,
        "k4_aabb_repeated_pair": repeated_pair,
    }


def quadratic_aabb_split_pair_remainder(bridge: Array, effective_weight: Array) -> Array:
    """Generated-only exact small-width reference for the unresolved aabb term."""

    full = aabb_quadratic_jet_reference(bridge, effective_weight)
    repeated = aabb_quadratic_jet_split(bridge, effective_weight)["repeated_pair_exact"]
    return full - repeated


def physical_effective_weight(scales: Array, downstream_weight: Array) -> Array:
    """Return the gauge-invariant transport rows ``diag(scales) @ W``."""

    scales = np.asarray(scales, dtype=np.float64)
    downstream_weight = np.asarray(downstream_weight, dtype=np.float64)
    if downstream_weight.ndim != 2 or scales.shape != (downstream_weight.shape[0],):
        raise ValueError("physical scale/weight shape mismatch")
    if not np.all(np.isfinite(scales)) or np.any(scales <= 0.0) or not np.all(np.isfinite(downstream_weight)):
        raise ValueError("physical scale/weight must be finite with positive scales")
    return scales[:, None] * downstream_weight


def ordered_hh_identity(residual: Array, effective_weight: Array) -> dict[str, Array]:
    """Exact ordered-population expectation for a frozen full-support HH law.

    This is not a sampler.  It evaluates
    ``(1/2) sum_{i,j!=k} R_ijk F_ijk`` directly, showing the slot factor that a
    fixed-count Hansen--Hurwitz average estimates when singleton order is
    random.  It equals the canonical ``j<k`` transport exactly.
    """

    residual = _hollow_symmetric(residual, "residual")
    weight = np.asarray(effective_weight, dtype=np.float64)
    if weight.ndim != 2 or weight.shape[0] != residual.shape[0]:
        raise ValueError("residual/weight width mismatch")
    outputs = weight.shape[1]
    aaab = np.zeros((outputs, outputs), dtype=np.float64)
    aabb = np.zeros((outputs, outputs), dtype=np.float64)
    for i in range(residual.shape[0]):
        for j in range(residual.shape[0]):
            for k in range(residual.shape[0]):
                if len({i, j, k}) != 3:
                    continue
                x, y, z = weight[i], weight[j], weight[k]
                coefficient = 0.5 * float(residual[i, j, k])
                aaab += coefficient * (
                    6.0 * np.outer(x * y * z, x)
                    + 3.0 * np.outer(x * x * z, y)
                    + 3.0 * np.outer(x * x * y, z)
                )
                aabb += coefficient * (
                    2.0 * np.outer(x * x, y * z)
                    + 2.0 * np.outer(y * z, x * x)
                    + 4.0 * np.outer(x * y, x * z)
                    + 4.0 * np.outer(x * z, x * y)
                )
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def residual_hh_tangent_identity() -> str:
    """Machine-readable statement of the exact frozen-proposal tangent rule."""

    return (
        "For fixed q0(e)>0 and R_e=D_e-J_e, d E_q0[R_e F_e/q0(e)] "
        "= E_q0[(Rdot_e F_e + R_e Fdot_e)/q0(e)].  The deterministic jet "
        "uses the same product rule; their sum is d of the exact D source."
    )


def m140_preexecution_cost_gate(
    *, width: int = 256, layers: int = 31, dtype: str = "float32", safety_factor: float = 1.25,
) -> dict[str, int | float | bool | str]:
    """Fail-closed protected worksheet for the requested deterministic control.

    Even granting reuse of ``Q@W`` and every M133/M126 pre-existing product,
    the verified M130 aaab/repeated-pair identity needs these four new dense
    products: ``(S*S)@W``, ``(S*S)@(W*W)``, ``S@(W*(Q@W))``, and
    ``S@((W*W)*(Q@W))``.  This deliberately omits further products, scalar
    work, allocations, the aabb split-pair contraction, and the residual HH
    work.  It is therefore an optimistic lower worksheet, not an end-to-end
    bill.
    """

    if width <= 0 or layers <= 0 or dtype not in {"float32", "float64"} or safety_factor < 1.0:
        raise ValueError("invalid target cost dimensions")
    square32 = 2 * width**3 - width**2
    square_bill = square32 if dtype == "float32" else 2 * square32
    unavoidable_calls = 4
    raw = unavoidable_calls * layers * square_bill
    protected = int(math.ceil(raw * safety_factor))
    cap = 5_000_000_000
    return {
        "dtype": dtype,
        "width": width,
        "layers": layers,
        "square_gemm_bill": square_bill,
        "optimistic_new_square_calls_per_layer": unavoidable_calls,
        "raw_lower_worksheet": raw,
        "protected_lower_worksheet": protected,
        "protected_billions": protected / 1e9,
        "incremental_cap": cap,
        "under_incremental_cap": protected <= cap,
        "full_aabb_split_pair_deterministic_verified": False,
        "full_quadratic_control_deployable": False,
        "decision": "KILLED_PREEXECUTION_COST_AND_COMPLETENESS",
    }
