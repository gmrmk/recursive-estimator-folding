"""M144 algebraic kernel: binary gate-aligned split and exact moment merge.

This module is deliberately structural.  It neither imports the contest MLP
loader nor contains an accuracy experiment.  Its role is to make the claimed
conditional-Gaussian algebra, symmetry, and non-collapse properties testable.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np


RIDGE = 1e-6
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_HALF_NORMAL_MEAN = math.sqrt(2.0 / math.pi)
_HALF_NORMAL_VARIANCE = 1.0 - 2.0 / math.pi


@dataclass(frozen=True)
class GaussianComponent:
    """A Gaussian surrogate component with a normalized external weight."""

    weight: float
    mean: np.ndarray
    covariance: np.ndarray


def normal_pdf(x: np.ndarray) -> np.ndarray:
    return _INV_SQRT_2PI * np.exp(-0.5 * np.asarray(x, dtype=np.float64) ** 2)


def binary_truncated_standard_moments() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact masses, means, and variances of N(0,1) conditioned on T<0/T>0."""
    return (
        np.array([0.5, 0.5]),
        np.array([-_HALF_NORMAL_MEAN, _HALF_NORMAL_MEAN]),
        np.array([_HALF_NORMAL_VARIANCE, _HALF_NORMAL_VARIANCE]),
    )


def gate_direction(mean: np.ndarray, covariance: np.ndarray, ridge: float = RIDGE) -> np.ndarray:
    """Return the scale-covariant gate direction a=S^-1(R+ridge I)^-1 phi(mu/s).

    The fixed ridge is dimensionless because R has diagonal one.  This avoids
    a non-covariant absolute jitter and does not require an eigendecomposition.
    """
    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    covariance = 0.5 * (covariance + covariance.T)
    variance = np.diag(covariance)
    if np.any(variance <= 0.0):
        raise ValueError("M144 structural kernel requires positive component variances")
    sigma = np.sqrt(variance)
    correlation = covariance / np.outer(sigma, sigma)
    correlation = 0.5 * (correlation + correlation.T)
    y = np.linalg.solve(correlation + ridge * np.eye(mean.size), normal_pdf(mean / sigma))
    return y / sigma


def split_binary(component: GaussianComponent, ridge: float = RIDGE) -> tuple[GaussianComponent, GaussianComponent]:
    """Moment-match the exact T<0/T>0 conditional laws by two Gaussian children.

    The first two conditional moments are exact.  The conditional distribution
    itself is truncated Gaussian rather than Gaussian, which is the controlled
    approximation that makes subsequent analytic propagation finite.
    """
    a = gate_direction(component.mean, component.covariance, ridge)
    covariance_direction = component.covariance @ a
    direction_variance = float(a @ covariance_direction)
    if not math.isfinite(direction_variance) or direction_variance <= 0.0:
        raise ValueError("nonpositive standardized gate direction variance")
    c = covariance_direction / math.sqrt(direction_variance)
    masses, conditional_means, conditional_variances = binary_truncated_standard_moments()
    children: list[GaussianComponent] = []
    for mass, scalar_mean, scalar_variance in zip(masses, conditional_means, conditional_variances, strict=True):
        mean = component.mean + c * scalar_mean
        covariance = component.covariance + (scalar_variance - 1.0) * np.outer(c, c)
        covariance = 0.5 * (covariance + covariance.T)
        children.append(GaussianComponent(component.weight * float(mass), mean, covariance))
    return children[0], children[1]


def mixture_moments(components: Iterable[GaussianComponent]) -> tuple[float, np.ndarray, np.ndarray]:
    """Return total mass, exact mixture mean, and exact mixture covariance."""
    items = list(components)
    if not items:
        raise ValueError("need at least one component")
    mass = float(sum(item.weight for item in items))
    if mass <= 0.0:
        raise ValueError("positive mixture mass required")
    mean = sum(item.weight * item.mean for item in items) / mass
    covariance = sum(
        item.weight
        * (item.covariance + np.outer(item.mean - mean, item.mean - mean))
        for item in items
    ) / mass
    return mass, mean, 0.5 * (covariance + covariance.T)


def merge_moment_preserving(components: Iterable[GaussianComponent]) -> GaussianComponent:
    """Replace a component sub-mixture by its unique first-two-moment Gaussian.

    This preservation claim applies to the Gaussian *surrogate mixture* being
    merged, not to the underlying exact truncated law before Gaussianization.
    """
    items = list(components)
    mass, mean, covariance = mixture_moments(items)
    return GaussianComponent(mass, mean, covariance)


def sibling_merge(first: GaussianComponent, second: GaussianComponent) -> GaussianComponent:
    """The deterministic provenance merge used once the K cap is saturated."""
    return merge_moment_preserving((first, second))


def split_surrogate_fourth_moment() -> float:
    """Fourth moment along T after binary split then Gaussian moment matching."""
    mean_square = _HALF_NORMAL_MEAN**2
    variance = _HALF_NORMAL_VARIANCE
    return mean_square**2 + 6.0 * mean_square * variance + 3.0 * variance**2


def retained_component_history_bound(depth: int, cap: int, branches: int = 2) -> dict[str, int]:
    """Combinatorial branch-capacity witness; not an accuracy lower bound."""
    if depth < 0 or cap < 1 or branches < 2:
        raise ValueError("invalid branch-capacity arguments")
    exact_histories = branches**depth
    return {
        "unmerged_histories": exact_histories,
        "cap": cap,
        "minimum_histories_per_retained_label": math.ceil(exact_histories / cap),
    }
