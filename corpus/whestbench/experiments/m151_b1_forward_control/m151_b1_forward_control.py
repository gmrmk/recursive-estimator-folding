"""Generated-only algebra for the M151 B=1 forward C_211 control.

This is not an estimator and it does not import Formal-L1, a contest model, a
coefficient oracle, or any response/scoring machinery.  It freezes a narrow
alternative to M150: emit the B=1 control in the already-owned *forward*
source slots, then let the existing one-carrier M125b forward transport carry
that source.  It deliberately constructs no all-output response dual.

The dense ordered-triplet loops below are a small-width parity oracle, not a
target implementation.  The target mechanism is permitted only after the
separate source-only gate proves the B=1 compiler/call/wall budget in the
ledger returned by :func:`b1_forward_static_ledger`.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math

import numpy as np


Array = np.ndarray
B1_NODE_COUNT = 49
ORDERED_SINGLETON_OWNER = 0.5


@dataclass(frozen=True)
class B1CanonicalState:
    """One signed 49-node canonical moment-functional state.

    ``omega`` need not be nonnegative: signed Smolyak-style weights define a
    finite moment functional here, not a sampling law.  B=1 is structural;
    accepting a second block would silently change the cost proof.
    """

    omega: Array
    conditional_mean: Array
    conditional_variance: Array

    def __post_init__(self) -> None:
        omega = np.asarray(self.omega, dtype=np.float64)
        mean = np.asarray(self.conditional_mean, dtype=np.float64)
        variance = np.asarray(self.conditional_variance, dtype=np.float64)
        if omega.shape != (B1_NODE_COUNT,):
            raise ValueError("M151 requires exactly one 49-node canonical block")
        if mean.ndim != 2 or mean.shape[0] != B1_NODE_COUNT or variance.shape != mean.shape:
            raise ValueError("canonical conditional moments have incompatible B=1 shapes")
        if mean.shape[1] < 3:
            raise ValueError("C_211 needs at least three labels")
        if not (np.all(np.isfinite(omega)) and np.all(np.isfinite(mean)) and np.all(np.isfinite(variance))):
            raise ValueError("canonical state must be finite")
        if np.any(variance < 0.0):
            raise ValueError("conditional variances must be nonnegative")
        if not math.isclose(float(np.sum(omega)), 1.0, rel_tol=0.0, abs_tol=3e-13):
            raise ValueError("signed cubature weights must sum to one")


@dataclass(frozen=True)
class Source211:
    """The exactly-once M133 [2,1,1] source owner."""

    aaaa: Array
    aaab: Array
    aabb: Array


def _state_arrays(state: B1CanonicalState) -> tuple[Array, Array, Array]:
    # ``__post_init__`` is the public contract; repeat conversion here so
    # callers cannot depend on a mutable input's original dtype.
    return (
        np.asarray(state.omega, dtype=np.float64),
        np.asarray(state.conditional_mean, dtype=np.float64),
        np.asarray(state.conditional_variance, dtype=np.float64),
    )


def covariance_star_b1(state: B1CanonicalState) -> Array:
    """Finite-cubature covariance including the mandatory conditional star."""

    omega, mean, variance = _state_arrays(state)
    mu = omega @ mean
    centered = mean - mu[None, :]
    return centered.T @ (omega[:, None] * centered) + np.diag(omega @ variance)


def canonical_delta_tilde_b1(state: B1CanonicalState) -> Array:
    """Return M148's B=1 connected coefficient on pairwise-distinct labels.

    For distinct ``i,j,k`` this is exactly

    ``sum_s omega_s (a_si^2+v_si)a_sj a_sk
       - V_ii V_jk - 2 V_ij V_ik``.

    Repeated-label entries are zero by ownership: they belong to other source
    collision classes and must never be inserted through this owner.
    """

    omega, mean, variance = _state_arrays(state)
    width = mean.shape[1]
    mu = omega @ mean
    a = mean - mu[None, :]
    t = a * a + variance
    covariance = covariance_star_b1(state)
    answer = np.zeros((width, width, width), dtype=np.float64)
    # Evaluate each singleton-symmetric physical unit once, then copy its
    # value to the two ordered labels.  Apart from guaranteeing the ownership
    # contract, this avoids turning harmless floating multiplication order
    # differences into an accidental broken j/k symmetry.
    for i in range(width):
        for j in range(width):
            for k in range(j + 1, width):
                if i == j or i == k:
                    continue
                raw = float(np.sum(omega * t[:, i] * a[:, j] * a[:, k]))
                value = (
                    raw
                    - covariance[i, i] * covariance[j, k]
                    - 2.0 * covariance[i, j] * covariance[i, k]
                )
                answer[i, j, k] = value
                answer[i, k, j] = value
    return answer


def _weight_array(weight: Array) -> Array:
    value = np.asarray(weight, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] < 3 or not np.all(np.isfinite(value)):
        raise ValueError("weight must be a finite (labels, output-width) matrix with at least three labels")
    return value


def source_feature_211(weight: Array, i: int, j: int, k: int) -> Source211:
    """Coefficient-free M133 [2,1,1] feature for one ordered triple."""

    w = _weight_array(weight)
    n, _ = w.shape
    if not (0 <= i < n and 0 <= j < n and 0 <= k < n and len({i, j, k}) == 3):
        raise ValueError("[2,1,1] source labels must be pairwise distinct")
    x, y, z = w[i], w[j], w[k]
    aaab = (
        6.0 * np.outer(x * y * z, x)
        + 3.0 * np.outer(x * x * z, y)
        + 3.0 * np.outer(x * x * y, z)
    )
    first = 2.0 * np.outer(x * x, y * z)
    second = 4.0 * np.outer(x * y, x * z)
    aabb = first + first.T + second + second.T
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def source_add(left: Source211, right: Source211) -> Source211:
    """Add two same-shaped source contributions without changing ownership."""

    if left.aaaa.shape != right.aaaa.shape or left.aaab.shape != right.aaab.shape or left.aabb.shape != right.aabb.shape:
        raise ValueError("source slots have incompatible shapes")
    return Source211(left.aaaa + right.aaaa, left.aaab + right.aaab, left.aabb + right.aabb)


def source_scale(scale: float, source: Source211) -> Source211:
    if not math.isfinite(scale):
        raise ValueError("source scale must be finite")
    return Source211(scale * source.aaaa, scale * source.aaab, scale * source.aabb)


def dense_ordered_211_source(weight: Array, coefficient: Array) -> Source211:
    """Exact reference ``1/2 sum_ordered_distinct coefficient*F``.

    This reference is intentionally exhaustive for response-free parity only.
    The target B=1 forward compiler has a separate static/native cost gate;
    this routine is not evidence that a cubic label loop is deployable.
    """

    w = _weight_array(weight)
    n, output_width = w.shape
    delta = np.asarray(coefficient, dtype=np.float64)
    if delta.shape != (n, n, n) or not np.all(np.isfinite(delta)):
        raise ValueError("coefficient must be a finite (labels, labels, labels) tensor")
    if not np.allclose(delta, delta.swapaxes(1, 2), rtol=0.0, atol=3e-12):
        raise ValueError("ordered singleton coefficient must be symmetric under j/k exchange")
    for i in range(n):
        if np.any(delta[i, i, :] != 0.0) or np.any(delta[i, :, i] != 0.0) or np.any(delta[:, i, i] != 0.0):
            raise ValueError("repeated-label coefficients are owned outside M151 C_211")
    total = Source211(
        np.zeros(output_width, dtype=np.float64),
        np.zeros((output_width, output_width), dtype=np.float64),
        np.zeros((output_width, output_width), dtype=np.float64),
    )
    for i, j, k in itertools.permutations(range(n), 3):
        total = source_add(total, source_scale(ORDERED_SINGLETON_OWNER * float(delta[i, j, k]), source_feature_211(w, i, j, k)))
    return total


def _forward_owned_ordered_211_source(weight: Array, coefficient: Array) -> Source211:
    """Independent forward-slot form of the ordered M133 sum.

    This establishes the reusable source identity used by the B=1 compiler.
    In the `aaab` slot, singleton symmetry reduces the half-owned feature to

    ``3 sum d_ijk [(x*y*z)x^T + (x^2*z)y^T]``.

    The `aabb` slot retains both orientations explicitly.  This function is
    still a small-width exhaustive oracle; it is intentionally not offered as
    a target-size aggregation implementation.
    """

    w = _weight_array(weight)
    n, output_width = w.shape
    delta = np.asarray(coefficient, dtype=np.float64)
    if delta.shape != (n, n, n) or not np.all(np.isfinite(delta)):
        raise ValueError("coefficient must be a finite (labels, labels, labels) tensor")
    aaab = np.zeros((output_width, output_width), dtype=np.float64)
    aabb = np.zeros((output_width, output_width), dtype=np.float64)
    for i, j, k in itertools.permutations(range(n), 3):
        d = float(delta[i, j, k])
        x, y, z = w[i], w[j], w[k]
        aaab += 3.0 * d * (
            np.outer(x * y * z, x)
            + np.outer(x * x * z, y)
        )
        first = np.outer(x * x, y * z)
        second = 2.0 * np.outer(x * y, x * z)
        aabb += d * (first + first.T + second + second.T)
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def forward_b1_control_source(weight: Array, state: B1CanonicalState) -> Source211:
    """Compile the B=1 deterministic control into M133's forward source slots.

    The only operation performed by the deployed mechanism after this source
    emission is the *existing* single M125b forward carrier.  It does not
    request, build, or propagate an all-output covariance adjoint, so the
    ``O(L n^4)`` M150 obstruction is outside this mechanism.
    """

    w = _weight_array(weight)
    if w.shape[0] != state.conditional_mean.shape[1]:
        raise ValueError("canonical state and source weight label widths disagree")
    return _forward_owned_ordered_211_source(w, canonical_delta_tilde_b1(state))


def source_max_abs_difference(left: Source211, right: Source211) -> float:
    """Maximum source-slot error for small-width exact algebra checks."""

    return float(
        max(
            np.max(np.abs(left.aaaa - right.aaaa)),
            np.max(np.abs(left.aaab - right.aaab)),
            np.max(np.abs(left.aabb - right.aabb)),
        )
    )


def b1_forward_static_ledger() -> dict[str, int | float | bool | str]:
    """Frozen M148-to-M151 static crosswalk, in protected billions of FLOPs.

    The four known terms are M148's B=16 leading floor with node-linear terms
    divided by 16 and its dense forward source emission retained once.  The
    resulting remainder is a hard *inclusive* cap for an audited B=1 state
    provider, fixed tables/canonicalization, allocations, extra calls, and
    residual wall time.  No unknown work receives an implicit zero cost.
    """

    residual_endpoint = 85.98087880  # M148 K=128 endpoint subtotal.
    stacked_forward = 7.948380160 / 16.0
    stacked_reverse = 7.958855680 / 16.0
    dense_source_emission = 2.595389440
    node_pointwise = 2.210652160 / 16.0
    known_forward = stacked_forward + stacked_reverse + dense_source_emission + node_pointwise
    total = residual_endpoint + known_forward
    cap = 100.0 - total
    return {
        "candidate": "M151 B=1 exact forward C_211 control plus fixed-q exact residual HH",
        "blocks": 1,
        "nodes": B1_NODE_COUNT,
        "width": 256,
        "source_layers": 31,
        "residual_draws_per_layer": 128,
        "residual_endpoint_subtotal_billions": residual_endpoint,
        "stacked_node_forward_map_billions": stacked_forward,
        "stacked_node_reverse_map_billions": stacked_reverse,
        "dense_forward_source_emission_billions": dense_source_emission,
        "node_pointwise_allowance_billions": node_pointwise,
        "known_forward_core_billions": known_forward,
        "known_total_endpoint_billions": total,
        "untraced_provider_call_wall_cap_billions": cap,
        "known_core_fits": total < 100.0,
        "premise_gate_requires_native_trace": True,
        "execution_authorized": False,
        "cost_status": "CONDITIONAL_STATIC_SURVIVOR_PENDING_INCLUSIVE_B1_NATIVE_TRACE",
    }
