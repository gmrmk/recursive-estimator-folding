"""Deterministic F0 primitives for the DGFL dipole–Fourier proposal.

This module is deliberately small and source-only.  It uses column-vector
coordinates, float64 arithmetic, a strict-positive ReLU JVP convention, and no
generated networks, challenge truth, scorer, or provider code.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np


Array = np.ndarray


def _finite_vector(name: str, value: Array) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 1:
        raise ValueError(f"{name} must be a vector")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    return result


def _unit_vector(name: str, value: Array) -> Array:
    result = _finite_vector(name, value)
    if not math.isclose(float(result @ result), 1.0, rel_tol=0.0, abs_tol=1e-13):
        raise ValueError(f"{name} must have unit norm")
    return result


def _skew_matrix(name: str, value: Array, dimension: int) -> Array:
    result = np.asarray(value, dtype=np.float64)
    if result.shape != (dimension, dimension):
        raise ValueError(f"{name} has incompatible shape")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    if not np.allclose(result + result.T, 0.0, rtol=0.0, atol=1e-13):
        raise ValueError(f"{name} must be skew-symmetric")
    return (result - result.T) / 2.0


def rotation_generator(m: Array, b: Array) -> Array:
    """Return J = b m^T - m b^T for an orthonormal ordered pair."""

    m64 = _finite_vector("m", m)
    b64 = _finite_vector("b", b)
    if m64.shape != b64.shape:
        raise ValueError("m and b must have the same shape")
    if not math.isclose(float(m64 @ m64), 1.0, rel_tol=0.0, abs_tol=1e-13):
        raise ValueError("m must have unit norm")
    if not math.isclose(float(b64 @ b64), 1.0, rel_tol=0.0, abs_tol=1e-13):
        raise ValueError("b must have unit norm")
    if not math.isclose(float(m64 @ b64), 0.0, rel_tol=0.0, abs_tol=1e-13):
        raise ValueError("m and b must be orthogonal")
    return np.outer(b64, m64) - np.outer(m64, b64)


def rotation_2d(theta: float) -> Array:
    """Return exp(theta J) for m=e1, b=e2 and J=[[0,-1],[1,0]]."""

    if not math.isfinite(theta):
        raise ValueError("theta must be finite")
    cosine = math.cos(theta)
    sine = math.sin(theta)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=np.float64)


def forward_jvp(weights: Sequence[Array], x: Array, dx: Array) -> tuple[Array, Array]:
    """Propagate one primal and one tangent through a bias-free ReLU MLP.

    Each weight has shape ``(out_features, in_features)``.  At exactly zero
    preactivation, the frozen convention is the strict-positive derivative 0.
    """

    if not weights:
        raise ValueError("weights must be nonempty")
    primal = _finite_vector("x", x).copy()
    tangent = _finite_vector("dx", dx).copy()
    if primal.shape != tangent.shape:
        raise ValueError("x and dx must have the same shape")

    for layer_index, weight in enumerate(weights):
        matrix = np.asarray(weight, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] != primal.shape[0]:
            raise ValueError(f"weight {layer_index} has incompatible shape")
        if not np.all(np.isfinite(matrix)):
            raise ValueError(f"weight {layer_index} must be finite")
        preactivation = matrix @ primal
        tangent_preactivation = matrix @ tangent
        active = preactivation > 0.0
        primal = np.where(active, preactivation, 0.0)
        tangent = np.where(active, tangent_preactivation, 0.0)

    return primal, tangent


def forward_jvp_row_weights(
    weights: Sequence[Array], x: Array, dx: Array
) -> tuple[Array, Array]:
    """Apply WHest-style ``(in,out)`` weights through the column kernel.

    The explicit seam is ``W_col = W_row.T``.  It keeps the mathematical JVP
    implementation single-sourced while making the deployed row convention
    testable on nonsquare, nonsymmetric matrices.
    """

    column_weights: list[Array] = []
    for layer_index, weight in enumerate(weights):
        matrix = np.asarray(weight, dtype=np.float64)
        if matrix.ndim != 2:
            raise ValueError(f"weight {layer_index} must be a matrix")
        column_weights.append(matrix.T)
    return forward_jvp(column_weights, x, dx)


def dipole_rungs(u: Array, y: Array, dy: Array, m: Array, b: Array) -> Array:
    """Return the ordered ``(m,b)`` dipole control vectors."""

    u64 = _finite_vector("u", u)
    y64 = _finite_vector("y", y)
    dy64 = _finite_vector("dy", dy)
    m64 = _finite_vector("m", m)
    b64 = _finite_vector("b", b)
    if y64.shape != dy64.shape:
        raise ValueError("y and dy must have the same shape")
    if not (u64.shape == m64.shape == b64.shape):
        raise ValueError("u, m, and b must have the same shape")
    J = rotation_generator(m64, b64)

    h_m = float(m64 @ u64)
    h_b = float(b64 @ u64)
    Ju = J @ u64
    lie_m = float(m64 @ Ju)
    lie_b = float(b64 @ Ju)
    return np.stack((h_m * dy64 + lie_m * y64, h_b * dy64 + lie_b * y64))


def fourier_rung(
    u: Array,
    y: Array,
    dy: Array,
    J: Array,
    axis: Array,
    frequency: float,
) -> Array:
    """Return the complete cosine product-rule control for one axis/frequency."""

    u64 = _finite_vector("u", u)
    y64 = _finite_vector("y", y)
    dy64 = _finite_vector("dy", dy)
    axis64 = _unit_vector("axis", axis)
    if y64.shape != dy64.shape:
        raise ValueError("y and dy must have the same shape")
    if u64.shape != axis64.shape:
        raise ValueError("u and axis have incompatible shapes")
    matrix = _skew_matrix("J", J, u64.size)
    if not math.isfinite(frequency):
        raise ValueError("frequency must be finite")

    phase = frequency * float(axis64 @ u64)
    h = math.cos(phase)
    lie_h = -frequency * math.sin(phase) * float(axis64 @ (matrix @ u64))
    return h * dy64 + lie_h * y64


def fused_rung(
    u: Array,
    y: Array,
    dy: Array,
    m: Array,
    b: Array,
    J: Array,
    axes: Sequence[Array],
    frequencies: Sequence[float],
    betas: Array,
) -> Array:
    """Fuse the complete scalar bank before forming one vector correction."""

    u64 = _finite_vector("u", u)
    y64 = _finite_vector("y", y)
    dy64 = _finite_vector("dy", dy)
    m64 = _finite_vector("m", m)
    b64 = _finite_vector("b", b)
    beta64 = _finite_vector("betas", betas)
    if y64.shape != dy64.shape:
        raise ValueError("y and dy must have the same shape")
    if not (u64.shape == m64.shape == b64.shape):
        raise ValueError("u, m, and b must have the same shape")
    expected_J = rotation_generator(m64, b64)
    matrix = _skew_matrix("J", J, u64.size)
    if not np.allclose(matrix, expected_J, rtol=0.0, atol=1e-13):
        raise ValueError("J must equal the frozen generator for m and b")
    matrix = expected_J
    expected = 2 + len(axes) * len(frequencies)
    if beta64.size != expected:
        raise ValueError(f"betas must have length {expected}")

    h_total = beta64[0] * float(m64 @ u64) + beta64[1] * float(b64 @ u64)
    Ju = matrix @ u64
    lie_total = beta64[0] * float(m64 @ Ju) + beta64[1] * float(b64 @ Ju)
    beta_index = 2
    for axis in axes:
        axis64 = _unit_vector("axis", axis)
        if axis64.shape != u64.shape:
            raise ValueError("axis has incompatible shape")
        for frequency in frequencies:
            if not math.isfinite(frequency):
                raise ValueError("frequency must be finite")
            phase = frequency * float(axis64 @ u64)
            coefficient = beta64[beta_index]
            h_total += coefficient * math.cos(phase)
            lie_total += (
                coefficient
                * -frequency
                * math.sin(phase)
                * float(axis64 @ (matrix @ u64))
            )
            beta_index += 1

    return h_total * dy64 + lie_total * y64


def canonical_pairwise_mean(leaves: Iterable[Array]) -> Array:
    """Reduce finite, equal-shaped leaves through one deterministic binary tree."""

    work = [np.asarray(leaf, dtype=np.float64).copy() for leaf in leaves]
    if not work:
        raise ValueError("leaves must be nonempty")
    shape = work[0].shape
    if any(leaf.shape != shape for leaf in work):
        raise ValueError("all leaves must have the same shape")
    if any(not np.all(np.isfinite(leaf)) for leaf in work):
        raise ValueError("all leaves must be finite")
    count = len(work)

    while len(work) > 1:
        merged: list[Array] = []
        index = 0
        while index + 1 < len(work):
            merged.append(work[index] + work[index + 1])
            index += 2
        if index < len(work):
            merged.append(work[index])
        work = merged

    return work[0] / float(count)


def evaluate_bank(
    rows: Array,
    weights: Sequence[Array],
    m: Array,
    b: Array,
    axes: Sequence[Array],
    frequencies: Sequence[float],
    betas: Array,
    *,
    radius: float,
    shard_count: int,
    shard_emission_order: Sequence[int] | None = None,
) -> tuple[Array, dict[str, Any]]:
    """Evaluate fixed row shards, then merge identical global leaves canonically.

    ``shard_count`` changes only ownership.  This F0 function does not spawn
    processes and makes no speed claim.
    """

    row_matrix = np.asarray(rows, dtype=np.float64)
    if row_matrix.ndim != 2 or row_matrix.shape[0] == 0:
        raise ValueError("rows must be a nonempty matrix")
    if not np.all(np.isfinite(row_matrix)):
        raise ValueError("rows must be finite")
    norms = np.linalg.norm(row_matrix, axis=1)
    if not np.allclose(norms, 1.0, rtol=0.0, atol=2e-13):
        raise ValueError("rows must have unit norm")
    if shard_count < 1 or shard_count > row_matrix.shape[0]:
        raise ValueError("shard_count is out of range")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be finite and positive")

    m64 = _finite_vector("m", m)
    b64 = _finite_vector("b", b)
    J = rotation_generator(m64, b64)
    partitions = np.array_split(np.arange(row_matrix.shape[0]), shard_count)
    if shard_emission_order is None:
        emission_order = list(range(shard_count))
    else:
        emission_order = [int(index) for index in shard_emission_order]
        if sorted(emission_order) != list(range(shard_count)):
            raise ValueError("shard_emission_order must be a permutation of shard ids")
    indexed_leaves: list[tuple[int, Array]] = []
    jvp_evaluations = 0

    for shard_index in emission_order:
        partition = partitions[shard_index]
        for raw_index in partition:
            index = int(raw_index)
            u = row_matrix[index]
            x = radius * u
            y, dy = forward_jvp(weights, x, J @ x)
            leaf = fused_rung(u, y, dy, m64, b64, J, axes, frequencies, betas)
            indexed_leaves.append((index, leaf))
            jvp_evaluations += 1

    indexed_leaves.sort(key=lambda item: item[0])
    leaf_order = [index for index, _ in indexed_leaves]
    result = canonical_pairwise_mean([leaf for _, leaf in indexed_leaves])
    receipt: dict[str, Any] = {
        "leaf_order": leaf_order,
        "jvp_evaluations": jvp_evaluations,
        "shard_count": shard_count,
        "radius": radius,
        "emission_order": emission_order,
        "execution": "deterministic shard simulation; no processes spawned",
    }
    return result, receipt
