"""M224: gauge-invariant normalized chart for the exact M216/M221 atom.

Only the numerical coordinates and algebraic factorization change.  The
strict-distinct antithetic estimator, generated events, pair kernel, Taylor
recurrence, and 32-panel Plackett/Simpson rule are inherited unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import itertools
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
PARENT_DIR = EXPERIMENTS / "m221_batched_certified_distinct_atom"
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

import m221_batched_certified_distinct_atom as _m221  # noqa: E402


MUTATION = "M224"
PackedBatch = _m221.PackedBatch
M224DomainRefusal = _m221.M221DomainRefusal
WIDTHS = _m221.WIDTHS
STATE_SEEDS = _m221.STATE_SEEDS
FRESH_STATE_SEEDS = (224700003, 224700004, 224700005, 224700006, 224700007)
OUTER_PROBES = _m221.OUTER_PROBES
NATIVE_OUTER_SEEDS = (221720001, 221720002, 221720003, 221720004, 221720005)

ABS_RHO_MAX = 0.08
ABS_STANDARD_MAX = _m221.ABS_STANDARD_MAX
SCALE_RATIO_MIN = _m221.SIGMA_MIN
SCALE_RATIO_MAX = _m221.SIGMA_MAX
STANDARDIZED_REPEATED_MAX = _m221.REPEATED_CENTER_MAX
EVENT_RADIUS_FACTOR = _m221.EVENT_RADIUS_FACTOR
REQUIRED_RADIUS_FACTOR = _m221.REQUIRED_RADIUS_FACTOR
SIMPSON_PANELS = _m221.SIMPSON_PANELS
PHI2_RADIUS = 2.5e-12


@dataclass(frozen=True)
class BatchResult:
    value: np.ndarray
    radius: np.ndarray
    chart_ok: np.ndarray
    fallback: np.ndarray
    max_abs_alpha: np.ndarray
    max_abs_t: np.ndarray
    max_abs_repeated_standardized: np.ndarray
    conditional_scale_ratio_left: np.ndarray
    conditional_scale_ratio_right: np.ndarray
    normalized_bracket: np.ndarray


def single_event_batch(
    *,
    width: int,
    seed: int,
    labels: tuple[int, int, int, int],
    outer_g: Iterable[float],
) -> PackedBatch:
    return _m221.single_event_batch(
        width=width,
        seed=seed,
        labels=labels,
        outer_g=outer_g,
    )


def generated_probe_batch(
    width: int,
    seed: int,
    *,
    outer_g: Iterable[float] = OUTER_PROBES,
) -> PackedBatch:
    return _m221.generated_probe_batch(width, seed, outer_g=outer_g)


def concatenate_batches(batches: Iterable[PackedBatch]) -> PackedBatch:
    return _m221.concatenate_batches(batches)


def generated_native_batch(seed: int) -> PackedBatch:
    """Reproduce an M221 native issuer without importing FlopScope."""

    rng = np.random.default_rng(int(seed))
    batches = []
    for layer in range(1, 32):
        local = _m221._m216.frozen_local_state(7, 221730000 + layer)
        owners = _m221._m216.strict_physical_owners(7)
        g = rng.normal(size=128)
        batches.append(
            _m221._pack_rows(
                local,
                ((owners[slot % len(owners)], float(g[slot])) for slot in range(128)),
            )
        )
    return concatenate_batches(batches)


def _marginal_singleton_sigmas(packed: PackedBatch) -> tuple[np.ndarray, np.ndarray]:
    left = np.empty(packed.size, dtype=np.float64)
    right = np.empty(packed.size, dtype=np.float64)
    for slot, (local, labels) in enumerate(
        zip(packed.local_states, packed.labels, strict=True)
    ):
        left[slot] = float(local.sigma[int(labels[2])])
        right[slot] = float(local.sigma[int(labels[3])])
    return left, right


def evaluate_numpy(packed: PackedBatch) -> BatchResult:
    """Evaluate the unchanged atom in dimensionless normalized coordinates."""

    g = np.stack((packed.g, -packed.g), axis=0)
    mean_left = packed.pair_base_left[None, :] + packed.pair_slope_left[None, :] * g
    mean_right = packed.pair_base_right[None, :] + packed.pair_slope_right[None, :] * g
    alpha_left = mean_left / packed.pair_sigma_left[None, :]
    alpha_right = mean_right / packed.pair_sigma_right[None, :]
    rho = packed.pair_rho
    q_rho = np.sqrt(1.0 - rho * rho)
    t_left = (alpha_right - rho[None, :] * alpha_left) / q_rho[None, :]
    t_right = (alpha_left - rho[None, :] * alpha_right) / q_rho[None, :]

    Phi_left = _m221._Phi16(alpha_left)
    Phi_right = _m221._Phi16(alpha_right)
    phi_left = _m221._phi(alpha_left)
    phi_right = _m221._phi(alpha_right)
    Phi2 = _m221._Phi2_plackett_simpson(alpha_left, alpha_right, rho)
    d_left = phi_left * _m221._Phi16(t_left)
    d_right = phi_right * _m221._Phi16(t_right)
    joint = (
        _m221.INV_TWO_PI
        * np.exp(
            -(
                alpha_left * alpha_left
                - 2.0 * rho[None, :] * alpha_left * alpha_right
                + alpha_right * alpha_right
            )
            / (2.0 * (1.0 - rho[None, :] * rho[None, :]))
        )
        / q_rho[None, :]
    )
    standard_pair = (
        alpha_right * d_left
        + alpha_left * d_right
        + (1.0 - rho[None, :] * rho[None, :]) * joint
        + (alpha_left * alpha_right + rho[None, :]) * Phi2
    )
    standard_unary_left = alpha_left * Phi_left + phi_left
    standard_unary_right = alpha_right * Phi_right + phi_right

    beta_left = packed.activation_mean_left / packed.pair_sigma_left
    beta_right = packed.activation_mean_right / packed.pair_sigma_right
    centered_pair_standard = (
        standard_pair
        - beta_left[None, :] * standard_unary_right
        - beta_right[None, :] * standard_unary_left
        + beta_left[None, :] * beta_right[None, :]
    )
    repeated_standardized = (
        np.maximum(
            packed.repeated_mean[None, :] + packed.repeated_sigma[None, :] * g,
            0.0,
        )
        - packed.repeated_activation_mean[None, :]
    ) / packed.repeated_sigma[None, :]

    covariance_scale = (
        packed.repeated_sigma
        * packed.repeated_sigma
        * packed.pair_sigma_left
        * packed.pair_sigma_right
    )
    physical_offset = (
        packed.activation_vii * packed.activation_vjk
        + 2.0 * packed.activation_vij * packed.activation_vik
        + packed.tree
    )
    normalized_bracket = (
        0.5
        * np.sum(
            repeated_standardized
            * repeated_standardized
            * centered_pair_standard,
            axis=0,
        )
        - physical_offset / covariance_scale
    )
    value = covariance_scale * normalized_bracket

    marginal_left, marginal_right = _marginal_singleton_sigmas(packed)
    scale_ratio_left = packed.pair_sigma_left / marginal_left
    scale_ratio_right = packed.pair_sigma_right / marginal_right
    max_alpha = np.maximum(np.abs(alpha_left), np.abs(alpha_right)).max(axis=0)
    max_t = np.maximum(np.abs(t_left), np.abs(t_right)).max(axis=0)
    max_repeated = np.abs(repeated_standardized).max(axis=0)
    chart_ok = (
        (np.abs(rho) <= ABS_RHO_MAX)
        & (max_alpha <= ABS_STANDARD_MAX)
        & (max_t <= ABS_STANDARD_MAX)
        & (scale_ratio_left >= SCALE_RATIO_MIN)
        & (scale_ratio_left <= SCALE_RATIO_MAX)
        & (scale_ratio_right >= SCALE_RATIO_MIN)
        & (scale_ratio_right <= SCALE_RATIO_MAX)
        & (max_repeated <= STANDARDIZED_REPEATED_MAX)
        & (covariance_scale > 0.0)
        & np.isfinite(value)
    )
    fallback = ~chart_ok
    radius = EVENT_RADIUS_FACTOR * (1.0 + np.abs(value))
    value = np.where(chart_ok, value, np.nan)
    radius = np.where(chart_ok, radius, np.nan)
    normalized_bracket = np.where(chart_ok, normalized_bracket, np.nan)
    return BatchResult(
        value=value,
        radius=radius,
        chart_ok=chart_ok,
        fallback=fallback,
        max_abs_alpha=max_alpha,
        max_abs_t=max_t,
        max_abs_repeated_standardized=max_repeated,
        conditional_scale_ratio_left=scale_ratio_left,
        conditional_scale_ratio_right=scale_ratio_right,
        normalized_bracket=normalized_bracket,
    )


def scalar_m216_midpoints(packed: PackedBatch) -> np.ndarray:
    return _m221.scalar_m216_midpoints(packed)


def scalar_m216_radii(packed: PackedBatch) -> np.ndarray:
    return _m221.scalar_m216_radii(packed)


def high_precision_midpoints(packed: PackedBatch, *, dps: int) -> np.ndarray:
    return _m221.high_precision_midpoints(packed, dps=dps)


def plackett_proof_certificate() -> dict[str, object]:
    """Return the frozen real-axis fourth-derivative/Simpson certificate."""

    R = Fraction(2, 25)
    A2 = Fraction(16, 25)
    D = 1 - R * R
    E = [Fraction(0)] * 5
    E[0] = 1 / D
    E[1] = 2 * R / D**2
    E[2] = 2 / D**2 + 8 * R**2 / D**3
    E[3] = 24 * R / D**3 + 48 * R**3 / D**4
    E[4] = 24 / D**3 + 288 * R**2 / D**4 + 384 * R**4 / D**5
    H = [
        Fraction(0),
        R / D,
        (1 + R**2) / D**2,
        2 * R * (3 + R**2) / D**3,
        6 * (1 + 6 * R**2 + R**4) / D**4,
    ]
    O = [Fraction(0)] + [R * E[k] + k * E[k - 1] for k in range(1, 5)]
    bounds_fraction = [H[k] + A2 * E[k] + A2 * O[k] for k in range(1, 5)]
    bounds = [float(item) for item in bounds_fraction]
    phi2_max = 1.0 / (2.0 * math.pi * math.sqrt(float(D)))
    b1, b2, b3, b4 = bounds
    fourth = phi2_max * (
        b4 + 4.0 * b3 * b1 + 3.0 * b2 * b2 + 6.0 * b2 * b1 * b1 + b1**4
    )
    remainder = fourth * float(R) ** 5 / (180.0 * SIMPSON_PANELS**4)
    return {
        "panels": SIMPSON_PANELS,
        "abs_rho_max": float(R),
        "abs_alpha_max": math.sqrt(float(A2)),
        "log_derivative_bounds_fraction": [str(item) for item in bounds_fraction],
        "log_derivative_bounds": bounds,
        "phi2_bound": phi2_max,
        "fourth_derivative_bound": fourth,
        "simpson_remainder_bound": remainder,
        "phi2_radius": PHI2_RADIUS,
        "pass": remainder < PHI2_RADIUS,
    }


def _census(state_seeds: tuple[int, ...]) -> dict[str, object]:
    fallback_count = 0
    event_count = 0
    max_midpoint_error = 0.0
    max_radius_ratio = 0.0
    parent_interval_pass = True
    returned_interval_pass = True
    extrema = {
        "abs_rho": 0.0,
        "abs_alpha": 0.0,
        "abs_t": 0.0,
        "abs_repeated_standardized": 0.0,
        "scale_ratio_min": math.inf,
        "scale_ratio_max": 0.0,
    }
    for width, seed in zip(WIDTHS, state_seeds, strict=True):
        packed = generated_probe_batch(width, seed)
        observed = evaluate_numpy(packed)
        parent = scalar_m216_midpoints(packed)
        parent_radius = scalar_m216_radii(packed)
        error = np.abs(observed.value - parent)
        ok = observed.chart_ok
        fallback_count += int(np.count_nonzero(observed.fallback))
        event_count += packed.size
        if np.any(ok):
            max_midpoint_error = max(max_midpoint_error, float(np.nanmax(error[ok])))
            max_radius_ratio = max(
                max_radius_ratio,
                float(np.nanmax(observed.radius[ok] / (1.0 + np.abs(observed.value[ok])))),
            )
        parent_interval_pass = parent_interval_pass and bool(
            np.all(error[ok] <= parent_radius[ok])
        )
        returned_interval_pass = returned_interval_pass and bool(
            np.all(error[ok] <= observed.radius[ok])
        )
        extrema["abs_rho"] = max(extrema["abs_rho"], float(np.max(np.abs(packed.pair_rho))))
        extrema["abs_alpha"] = max(extrema["abs_alpha"], float(np.max(observed.max_abs_alpha)))
        extrema["abs_t"] = max(extrema["abs_t"], float(np.max(observed.max_abs_t)))
        extrema["abs_repeated_standardized"] = max(
            extrema["abs_repeated_standardized"],
            float(np.max(observed.max_abs_repeated_standardized)),
        )
        ratios = np.concatenate(
            (observed.conditional_scale_ratio_left, observed.conditional_scale_ratio_right)
        )
        extrema["scale_ratio_min"] = min(extrema["scale_ratio_min"], float(np.min(ratios)))
        extrema["scale_ratio_max"] = max(extrema["scale_ratio_max"], float(np.max(ratios)))
    return {
        "event_count": event_count,
        "fallback_count": fallback_count,
        "max_midpoint_error": max_midpoint_error,
        "max_radius_ratio": max_radius_ratio,
        "parent_interval_pass": parent_interval_pass,
        "returned_interval_pass": returned_interval_pass,
        "parent_containment_pass": parent_interval_pass and returned_interval_pass,
        "chart_extrema": extrema,
    }


def _m221_native_cell_gate() -> dict[str, object]:
    event_count = 0
    fallback_count = 0
    max_abs_rho = 0.0
    max_radius_ratio = 0.0
    per_seed_fallback = []
    for seed in NATIVE_OUTER_SEEDS:
        packed = generated_native_batch(seed)
        observed = evaluate_numpy(packed)
        count = int(np.count_nonzero(observed.fallback))
        per_seed_fallback.append(count)
        fallback_count += count
        event_count += packed.size
        max_abs_rho = max(max_abs_rho, float(np.max(np.abs(packed.pair_rho))))
        if np.any(observed.chart_ok):
            max_radius_ratio = max(
                max_radius_ratio,
                float(
                    np.nanmax(
                        observed.radius[observed.chart_ok]
                        / (1.0 + np.abs(observed.value[observed.chart_ok]))
                    )
                ),
            )
    return {
        "event_count": event_count,
        "fallback_count": fallback_count,
        "per_seed_fallback_count": per_seed_fallback,
        "max_abs_rho": max_abs_rho,
        "max_radius_ratio": max_radius_ratio,
        "pass": fallback_count == 0 and max_abs_rho <= ABS_RHO_MAX,
    }


def _coordinate_arrays(packed: PackedBatch, result: BatchResult) -> tuple[np.ndarray, ...]:
    return (
        packed.pair_rho,
        result.max_abs_alpha,
        result.max_abs_t,
        result.max_abs_repeated_standardized,
        result.conditional_scale_ratio_left,
        result.conditional_scale_ratio_right,
        result.normalized_bracket,
    )


def _invariance_gate() -> dict[str, object]:
    local = _m221._m216.frozen_local_state(5, 221700005)
    owners = _m221._m216.strict_physical_owners(5)
    probes = (-2.0, 0.0, 2.5)
    baseline = _m221._pack_rows(local, ((labels, g) for labels in owners for g in probes))
    baseline_result = evaluate_numpy(baseline)

    gauge = np.exp(np.asarray((-0.4, -0.1, 0.0, 0.2, 0.5)))
    gauged_local = _m221._m216.build_local_state(
        local.mean * gauge,
        local.covariance * gauge[:, None] * gauge[None, :],
    )
    gauged = _m221._pack_rows(
        gauged_local,
        ((labels, g) for labels in owners for g in probes),
    )
    gauged_result = evaluate_numpy(gauged)
    expected_scales = np.asarray(
        [
            gauge[labels[0]] ** 2 * gauge[labels[2]] * gauge[labels[3]]
            for labels in baseline.labels
        ]
    )
    gauge_error = np.abs(gauged_result.value - expected_scales * baseline_result.value) / (
        1.0 + np.abs(expected_scales * baseline_result.value)
    )
    coordinate_errors = []
    for before, after in zip(
        _coordinate_arrays(baseline, baseline_result),
        _coordinate_arrays(gauged, gauged_result),
        strict=True,
    ):
        coordinate_errors.append(np.abs(after - before) / (1.0 + np.abs(before)))

    permutation = np.asarray((3, 0, 4, 1, 2), dtype=int)
    inverse = np.argsort(permutation)
    permuted_local = _m221._m216.build_local_state(
        local.mean[permutation],
        local.covariance[np.ix_(permutation, permutation)],
    )
    permuted_rows = [
        (tuple(int(inverse[item]) for item in labels), float(g))
        for labels, g in zip(baseline.labels, baseline.g, strict=True)
    ]
    permuted = _m221._pack_rows(permuted_local, permuted_rows)
    permuted_result = evaluate_numpy(permuted)
    permutation_error = np.abs(permuted_result.value - baseline_result.value) / (
        1.0 + np.abs(baseline_result.value)
    )

    baseline_fallback = int(np.count_nonzero(baseline_result.fallback))
    gauge_fallback = int(np.count_nonzero(gauged_result.fallback))
    permutation_fallback = int(np.count_nonzero(permuted_result.fallback))
    membership_mismatch = int(
        np.count_nonzero(baseline_result.chart_ok != gauged_result.chart_ok)
    )
    max_coordinate_error = float(max(np.max(item) for item in coordinate_errors))
    max_gauge_error = float(np.max(gauge_error))
    max_permutation_error = float(np.max(permutation_error))
    passed = bool(
        baseline_fallback == 0
        and gauge_fallback == 0
        and permutation_fallback == 0
        and membership_mismatch == 0
        and max_coordinate_error <= 2.0e-14
        and max_gauge_error <= 5.0e-8
        and max_permutation_error <= 5.0e-8
    )
    return {
        "pass": passed,
        "probe_count": baseline.size,
        "baseline_fallback_count": baseline_fallback,
        "gauge_fallback_count": gauge_fallback,
        "permutation_fallback_count": permutation_fallback,
        "chart_membership_mismatch_count": membership_mismatch,
        "max_normalized_coordinate_error": max_coordinate_error,
        "max_gauge_scaled_error": max_gauge_error,
        "max_permutation_scaled_error": max_permutation_error,
    }


def _high_precision_subset() -> PackedBatch:
    inherited = _m221._high_precision_subset()
    fresh = [
        single_event_batch(
            width=width,
            seed=seed,
            labels=(0, 0, 1, 2),
            outer_g=(0.0, 8.0, -8.0),
        )
        for width, seed in zip(WIDTHS, FRESH_STATE_SEEDS, strict=True)
    ]
    return concatenate_batches(itertools.chain((inherited,), fresh))


def _high_precision_gate() -> dict[str, object]:
    packed = _high_precision_subset()
    observed = evaluate_numpy(packed)
    reference80 = high_precision_midpoints(packed, dps=80)
    reference100 = high_precision_midpoints(packed, dps=100)
    oracle_gap = np.abs(reference80 - reference100)
    tolerance = 1.0e-12 * (1.0 + np.abs(reference100))
    midpoint_error = np.abs(observed.value - reference100)
    passed = bool(
        np.all(observed.chart_ok)
        and np.all(oracle_gap <= tolerance)
        and np.all(midpoint_error <= observed.radius)
    )
    return {
        "pass": passed,
        "probe_count": packed.size,
        "fallback_count": int(np.count_nonzero(observed.fallback)),
        "max_oracle_gap": float(np.max(oracle_gap)),
        "oracle_tolerance_max": float(np.max(tolerance)),
        "max_midpoint_error": float(np.max(midpoint_error)),
        "min_radius": float(np.min(observed.radius)),
        "min_radius_margin": float(np.min(observed.radius - midpoint_error)),
    }


@lru_cache(maxsize=1)
def run_frozen_numerical_gate() -> dict[str, object]:
    original = _census(STATE_SEEDS)
    fresh = _census(FRESH_STATE_SEEDS)
    native = _m221_native_cell_gate()
    invariance = _invariance_gate()
    high_precision = _high_precision_gate()
    proof = plackett_proof_certificate()
    max_radius_ratio = max(
        original["max_radius_ratio"],
        fresh["max_radius_ratio"],
        native["max_radius_ratio"],
    )
    passed = bool(
        proof["pass"]
        and original["fallback_count"] == 0
        and original["parent_containment_pass"]
        and fresh["fallback_count"] == 0
        and fresh["parent_containment_pass"]
        and native["pass"]
        and invariance["pass"]
        and high_precision["pass"]
        and max_radius_ratio <= REQUIRED_RADIUS_FACTOR
    )
    return {
        "numerical_gate_pass": passed,
        "max_radius_ratio": max_radius_ratio,
        "original_census": original,
        "fresh_census": fresh,
        "m221_native_cells": native,
        "invariance": invariance,
        "high_precision": high_precision,
        "plackett_proof": proof,
        "native_speed_gate_run": False,
        "variance_gate_run": False,
    }


__all__ = [
    "ABS_RHO_MAX",
    "BatchResult",
    "M224DomainRefusal",
    "PackedBatch",
    "concatenate_batches",
    "evaluate_numpy",
    "generated_native_batch",
    "generated_probe_batch",
    "high_precision_midpoints",
    "plackett_proof_certificate",
    "run_frozen_numerical_gate",
    "scalar_m216_midpoints",
    "single_event_batch",
]
