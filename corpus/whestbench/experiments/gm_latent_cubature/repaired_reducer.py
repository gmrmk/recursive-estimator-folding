"""Load the frozen sparse-radial candidate and install the repaired reducer.

The frozen module is imported from its own path and is never edited.  The only
change is the revival mechanism itself: ``reduce_components`` is replaced, in
this process only, by the zero-progress-guarded equal-mass compressor whose
control structure is copied from the index-13 sibling
``latent_randomized_radial/randomized_radial.py``.  Every other routine
(adaptive rank, signed spherical-radial nodes, ReLU moments, moment matching)
is the frozen one.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from types import ModuleType

import numpy as np

from frozen_paths import FROZEN_FULLCOV, FROZEN_IMPL

GUARD_COUNTS = {"last_bin_absorb": 0, "zero_capacity_advance": 0, "loops": 0}


def _load(path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


frozen = _load(FROZEN_IMPL, "latent_sparse_cubature")
fullcov = _load(FROZEN_FULLCOV, "corrected_fullcov")

GaussianComponent = frozen.GaussianComponent
_original_reduce = frozen.reduce_components


def repaired_reduce_components(
    components,
    maximum_components: int,
    *,
    relative_gap_tolerance: float,
):
    """Frozen equal-mass reduction plus a zero-progress last-bin guard."""
    total = math.fsum(component.weight for component in components)
    if len(components) <= maximum_components:
        return [
            GaussianComponent(
                component.weight / total, component.mean, component.covariance
            )
            for component in components
        ]

    global_mean, global_covariance = frozen.mixture_moments(components)
    direction = frozen.leading_direction(
        global_covariance, relative_gap_tolerance=relative_gap_tolerance
    )
    if direction is None:
        matched = frozen.moment_match(components)
        return [GaussianComponent(1.0, matched.mean, matched.covariance)]
    scores = np.asarray(
        [
            float(direction @ (component.mean - global_mean))
            for component in components
        ]
    )
    score_scale = float(np.max(np.abs(scores)))
    if score_scale <= 0.0:
        matched = frozen.moment_match(components)
        return [GaussianComponent(1.0, matched.mean, matched.covariance)]
    order = np.argsort(scores, kind="mergesort")
    if np.any(np.diff(scores[order]) <= relative_gap_tolerance * score_scale):
        matched = frozen.moment_match(components)
        return [GaussianComponent(1.0, matched.mean, matched.covariance)]

    target_mass = total / maximum_components
    bins = [[] for _ in range(maximum_components)]
    bin_index = 0
    bin_mass = 0.0
    eps = float(np.finfo(np.float64).eps)
    tolerance = eps * total
    advance_tolerance = 32.0 * eps * target_mass
    for component_index in order:
        component = components[int(component_index)]
        remaining = component.weight
        while remaining > tolerance:
            GUARD_COUNTS["loops"] += 1
            if bin_index == maximum_components - 1:
                # REPAIR: no next bin exists, so the last bin absorbs the rest
                # instead of appending zero-weight components forever.
                take = remaining
                GUARD_COUNTS["last_bin_absorb"] += 1
            else:
                capacity = max(target_mass - bin_mass, 0.0)
                if capacity <= tolerance:
                    # REPAIR: advance rather than append a zero-mass child.
                    bin_index += 1
                    bin_mass = 0.0
                    GUARD_COUNTS["zero_capacity_advance"] += 1
                    continue
                take = min(remaining, capacity)
            if take <= 0.0:
                raise ArithmeticError("equal-mass compressor made no progress")
            bins[bin_index].append(
                GaussianComponent(take, component.mean, component.covariance)
            )
            remaining -= take
            bin_mass += take
            if (
                bin_index + 1 < maximum_components
                and bin_mass >= target_mass - advance_tolerance
            ):
                bin_index += 1
                bin_mass = 0.0
    reduced = [frozen.moment_match(group) for group in bins if group]
    reduced_total = math.fsum(component.weight for component in reduced)
    return [
        GaussianComponent(
            component.weight / reduced_total,
            component.mean,
            component.covariance,
        )
        for component in reduced
    ]


frozen.reduce_components = repaired_reduce_components


def make_weights(width: int, depth: int, seed: int) -> list[np.ndarray]:
    """Frozen weight law, copied verbatim from the index-13 runner."""
    rng = np.random.default_rng(seed)
    return [
        rng.normal(0.0, math.sqrt(2.0 / width), size=(width, width)).astype(
            np.float64
        )
        for _ in range(depth)
    ]


def candidate(weights, trace=None) -> np.ndarray:
    return frozen.latent_sparse_cubature(
        weights,
        mixture_components=3,
        trace_fraction=0.5,
        relative_gap_tolerance=1e-10,
        trace=trace,
    )


def comparator(weights) -> np.ndarray:
    return fullcov.corrected_fullcov_closure(weights, order=256)
