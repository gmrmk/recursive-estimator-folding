"""Generated-only dense forward tangents for the M125/M125b theory audit.

This module consumes already-owned post-ReLU source defects.  It does not
construct M122 cumulants, load a benchmark, score a model, or expose a runner.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TangentState:
    """A row-oriented mean tangent and signed central-covariance tangent."""

    mean: np.ndarray
    covariance: np.ndarray

    def __post_init__(self) -> None:
        mean = np.asarray(self.mean, dtype=np.float64)
        covariance = np.asarray(self.covariance, dtype=np.float64)
        if mean.ndim != 1 or covariance.shape != (mean.size, mean.size):
            raise ValueError("tangent mean/covariance shape mismatch")
        if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(covariance)):
            raise ValueError("non-finite tangent state")
        if not np.array_equal(covariance, covariance.T):
            raise ValueError("tangent covariance must be exactly symmetric")
        object.__setattr__(self, "mean", mean)
        object.__setattr__(self, "covariance", covariance)


@dataclass(frozen=True)
class LocalReluJacobian:
    """Complete local Jacobian blocks of the central Gaussian ReLU map."""

    probability: np.ndarray
    mean_variance_derivative: np.ndarray
    price_kernel: np.ndarray
    h_mu: np.ndarray
    h_variance: np.ndarray

    def __post_init__(self) -> None:
        probability = np.asarray(self.probability, dtype=np.float64)
        mean_variance = np.asarray(self.mean_variance_derivative, dtype=np.float64)
        price = np.asarray(self.price_kernel, dtype=np.float64)
        h_mu = np.asarray(self.h_mu, dtype=np.float64)
        h_variance = np.asarray(self.h_variance, dtype=np.float64)
        n = probability.size
        if probability.shape != (n,) or mean_variance.shape != (n,):
            raise ValueError("ReLU vector-kernel shape mismatch")
        if price.shape != (n, n) or h_mu.shape != (n, n) or h_variance.shape != (n, n):
            raise ValueError("ReLU matrix-kernel shape mismatch")
        if not np.array_equal(price, price.T):
            raise ValueError("Price kernel must be exactly symmetric")
        if not all(np.all(np.isfinite(value)) for value in (probability, mean_variance, price, h_mu, h_variance)):
            raise ValueError("non-finite ReLU Jacobian")
        object.__setattr__(self, "probability", probability)
        object.__setattr__(self, "mean_variance_derivative", mean_variance)
        object.__setattr__(self, "price_kernel", price)
        object.__setattr__(self, "h_mu", h_mu)
        object.__setattr__(self, "h_variance", h_variance)


def relu_tangent(state: TangentState, jacobian: LocalReluJacobian) -> TangentState:
    """Apply all Price, diagonal, and mean/covariance cross blocks."""

    mean = state.mean
    covariance = state.covariance
    diagonal = np.diag(covariance)
    next_mean = (
        jacobian.probability * mean
        + jacobian.mean_variance_derivative * diagonal
    )

    mean_term = jacobian.h_mu * mean[:, None]
    variance_term = jacobian.h_variance * diagonal[:, None]
    mean_symmetric = mean_term + mean_term.T
    variance_symmetric = variance_term + variance_term.T
    next_covariance = (
        jacobian.price_kernel * covariance
        + mean_symmetric
        + variance_symmetric
    )
    indices = np.arange(mean.size)
    next_covariance[indices, indices] = (
        np.diag(jacobian.h_mu) * mean
        + np.diag(jacobian.h_variance) * diagonal
    )
    return TangentState(next_mean, next_covariance)


def tangent_stage(
    state: TangentState,
    weight: np.ndarray,
    jacobian: LocalReluJacobian,
) -> TangentState:
    """Apply row-oriented affine transport and the following ReLU tangent."""

    weight = np.asarray(weight, dtype=np.float64)
    n = state.mean.size
    if weight.shape != (n, n):
        raise ValueError("weight shape mismatch")
    affine_covariance = weight.T @ (state.covariance @ weight)
    # The two-sided product is symmetric algebraically but its two triangles
    # need not be bit-identical after floating-point GEMMs.  Canonicalize it;
    # a target ledger must charge this add and scale explicitly.
    affine_covariance = 0.5 * (affine_covariance + affine_covariance.T)
    affine = TangentState(state.mean @ weight, affine_covariance)
    return relu_tangent(affine, jacobian)


def _validate_chain(
    sources: list[TangentState],
    weights: list[np.ndarray],
    jacobians: list[LocalReluJacobian],
) -> None:
    if not sources:
        raise ValueError("at least one source is required")
    if len(weights) != len(jacobians) or len(sources) != len(weights) + 1:
        raise ValueError("post-conversion source/map indexing mismatch")


def explicit_source_superposition(
    sources: list[TangentState],
    weights: list[np.ndarray],
    jacobians: list[LocalReluJacobian],
) -> TangentState:
    """Reference M125: propagate every source through its complete suffix."""

    _validate_chain(sources, weights, jacobians)
    final_mean = np.zeros_like(sources[0].mean)
    final_covariance = np.zeros_like(sources[0].covariance)
    for source_index, source in enumerate(sources):
        state = source
        for weight, jacobian in zip(weights[source_index:], jacobians[source_index:]):
            state = tangent_stage(state, weight, jacobian)
        final_mean += state.mean
        final_covariance += state.covariance
    return TangentState(final_mean, final_covariance)


def inhomogeneous_source_recurrence(
    sources: list[TangentState],
    weights: list[np.ndarray],
    jacobians: list[LocalReluJacobian],
) -> TangentState:
    """M125b: propagate one accumulated tangent and inject the next source."""

    _validate_chain(sources, weights, jacobians)
    state = sources[0]
    for next_source, weight, jacobian in zip(sources[1:], weights, jacobians):
        propagated = tangent_stage(state, weight, jacobian)
        state = TangentState(
            propagated.mean + next_source.mean,
            propagated.covariance + next_source.covariance,
        )
    return state
