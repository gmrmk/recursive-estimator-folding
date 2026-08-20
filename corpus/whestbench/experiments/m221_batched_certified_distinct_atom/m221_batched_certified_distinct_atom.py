"""M221 pure-NumPy algebra/reference for a batched certified M216 atom."""

from __future__ import annotations

from dataclasses import dataclass, fields
import itertools
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _sibling in (
    "m216_antithetic_distinct_provider",
    "m213_event_local_randomized_source211",
):
    _path = str(EXPERIMENTS / _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import m216_antithetic_distinct_provider as _m216  # noqa: E402


MUTATION = "M221"
WIDTHS = (3, 4, 5, 6, 7)
STATE_SEEDS = (221700003, 221700004, 221700005, 221700006, 221700007)
OUTER_PROBES = (
    0.0,
    2.0**-8,
    -(2.0**-8),
    0.25,
    -0.25,
    1.0,
    -1.0,
    2.5,
    -2.5,
    5.0,
    -5.0,
    8.0,
    -8.0,
)
ABS_RHO_MAX = 0.04
ABS_STANDARD_MAX = 0.8
SIGMA_MIN = 0.8
SIGMA_MAX = 1.2
REPEATED_CENTER_MAX = 9.0
EVENT_RADIUS_FACTOR = 1.0e-8
REQUIRED_RADIUS_FACTOR = 2.0e-7
SIMPSON_PANELS = 32
SIMPSON_NODES = SIMPSON_PANELS + 1
INV_SQRT_TWO = 1.0 / math.sqrt(2.0)
INV_SQRT_TWO_PI = 1.0 / math.sqrt(2.0 * math.pi)
INV_TWO_PI = 1.0 / (2.0 * math.pi)


_ERF_COEFFICIENTS = np.asarray(
    [
        2.0 / math.sqrt(math.pi) * ((-1.0) ** order)
        / (math.factorial(order) * (2 * order + 1))
        for order in range(16)
    ],
    dtype=np.float64,
)
_SIMPSON_FRACTIONS = np.arange(SIMPSON_NODES, dtype=np.float64) / SIMPSON_PANELS
_SIMPSON_WEIGHTS = np.ones(SIMPSON_NODES, dtype=np.float64)
_SIMPSON_WEIGHTS[1:-1:2] = 4.0
_SIMPSON_WEIGHTS[2:-1:2] = 2.0


class M221DomainRefusal(RuntimeError):
    """A caller attempted a non-strict label or malformed local state."""


@dataclass(frozen=True)
class PackedBatch:
    g: np.ndarray
    repeated_mean: np.ndarray
    repeated_sigma: np.ndarray
    repeated_activation_mean: np.ndarray
    pair_base_left: np.ndarray
    pair_base_right: np.ndarray
    pair_slope_left: np.ndarray
    pair_slope_right: np.ndarray
    pair_sigma_left: np.ndarray
    pair_sigma_right: np.ndarray
    pair_rho: np.ndarray
    activation_mean_left: np.ndarray
    activation_mean_right: np.ndarray
    activation_vii: np.ndarray
    activation_vjk: np.ndarray
    activation_vij: np.ndarray
    activation_vik: np.ndarray
    tree: np.ndarray
    labels: np.ndarray
    local_states: tuple[object, ...]

    def __post_init__(self) -> None:
        count = int(np.asarray(self.g).size)
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name == "local_states":
                if len(value) != count:
                    raise ValueError("local state provenance length mismatch")
            elif field.name == "labels":
                if np.asarray(value).shape != (count, 4):
                    raise ValueError("labels must have shape (events,4)")
            elif np.asarray(value).shape != (count,):
                raise ValueError(f"{field.name} must be one scalar per event")

    @property
    def size(self) -> int:
        return int(self.g.size)


@dataclass(frozen=True)
class BatchResult:
    value: np.ndarray
    radius: np.ndarray
    chart_ok: np.ndarray
    fallback: np.ndarray
    max_abs_alpha: np.ndarray
    max_abs_t: np.ndarray
    max_abs_repeated_center: np.ndarray


def _strict_owner(labels: tuple[int, int, int, int], width: int) -> tuple[int, int, int]:
    labels = tuple(int(item) for item in labels)
    if len(labels) != 4 or any(item < 0 or item >= width for item in labels):
        raise M221DomainRefusal("four in-range labels required")
    counts = {item: labels.count(item) for item in set(labels)}
    if sorted(counts.values(), reverse=True) != [2, 1, 1]:
        raise M221DomainRefusal("M221 accepts strict [2,1,1] only")
    repeated = next(item for item, count in counts.items() if count == 2)
    left, right = sorted(item for item, count in counts.items() if count == 1)
    return repeated, left, right


def _pack_rows(
    local,
    labels_and_g: Iterable[tuple[tuple[int, int, int, int], float]],
) -> PackedBatch:
    rows = list(labels_and_g)
    if not rows:
        raise ValueError("M221 batch cannot be empty")
    records: dict[str, list[float]] = {
        name: []
        for name in (
            "g",
            "repeated_mean",
            "repeated_sigma",
            "repeated_activation_mean",
            "pair_base_left",
            "pair_base_right",
            "pair_slope_left",
            "pair_slope_right",
            "pair_sigma_left",
            "pair_sigma_right",
            "pair_rho",
            "activation_mean_left",
            "activation_mean_right",
            "activation_vii",
            "activation_vjk",
            "activation_vij",
            "activation_vik",
            "tree",
        )
    }
    canonical_labels: list[tuple[int, int, int, int]] = []
    for labels, g in rows:
        repeated, left, right = _strict_owner(labels, local.mean.size)
        vi = float(local.covariance[repeated, repeated])
        cov_li = float(local.covariance[left, repeated])
        cov_ri = float(local.covariance[right, repeated])
        var_left = float(local.covariance[left, left] - cov_li * cov_li / vi)
        var_right = float(local.covariance[right, right] - cov_ri * cov_ri / vi)
        cov_pair = float(local.covariance[left, right] - cov_li * cov_ri / vi)
        sigma_left = math.sqrt(var_left)
        sigma_right = math.sqrt(var_right)
        rho = cov_pair / (sigma_left * sigma_right)
        values = {
            "g": float(g),
            "repeated_mean": float(local.mean[repeated]),
            "repeated_sigma": float(local.sigma[repeated]),
            "repeated_activation_mean": float(local.activation_mean[repeated]),
            "pair_base_left": float(local.mean[left]),
            "pair_base_right": float(local.mean[right]),
            "pair_slope_left": cov_li / float(local.sigma[repeated]),
            "pair_slope_right": cov_ri / float(local.sigma[repeated]),
            "pair_sigma_left": sigma_left,
            "pair_sigma_right": sigma_right,
            "pair_rho": rho,
            "activation_mean_left": float(local.activation_mean[left]),
            "activation_mean_right": float(local.activation_mean[right]),
            "activation_vii": float(local.activation_covariance[repeated, repeated]),
            "activation_vjk": float(local.activation_covariance[left, right]),
            "activation_vij": float(local.activation_covariance[repeated, left]),
            "activation_vik": float(local.activation_covariance[repeated, right]),
            "tree": float(local.tree_211(repeated, left, right)),
        }
        for name, value in values.items():
            records[name].append(value)
        canonical_labels.append((repeated, repeated, left, right))
    return PackedBatch(
        **{name: np.asarray(value, dtype=np.float64) for name, value in records.items()},
        labels=np.asarray(canonical_labels, dtype=np.int64),
        local_states=tuple(local for _ in rows),
    )


def single_event_batch(
    *,
    width: int,
    seed: int,
    labels: tuple[int, int, int, int],
    outer_g: Iterable[float],
) -> PackedBatch:
    local = _m216.frozen_local_state(width, seed)
    return _pack_rows(local, ((labels, float(g)) for g in outer_g))


def generated_probe_batch(
    width: int,
    seed: int,
    *,
    outer_g: Iterable[float] = OUTER_PROBES,
) -> PackedBatch:
    local = _m216.frozen_local_state(width, seed)
    return _pack_rows(
        local,
        (
            (labels, float(g))
            for labels in _m216.strict_physical_owners(width)
            for g in outer_g
        ),
    )


def concatenate_batches(batches: Iterable[PackedBatch]) -> PackedBatch:
    batches = tuple(batches)
    if not batches:
        raise ValueError("at least one batch required")
    numeric = {}
    for field in fields(PackedBatch):
        if field.name == "local_states":
            continue
        numeric[field.name] = np.concatenate(
            [np.asarray(getattr(batch, field.name)) for batch in batches], axis=0
        )
    return PackedBatch(
        **numeric,
        local_states=tuple(
            itertools.chain.from_iterable(batch.local_states for batch in batches)
        ),
    )


def _Phi16(value: np.ndarray) -> np.ndarray:
    x = np.asarray(value, dtype=np.float64) * INV_SQRT_TWO
    y = x * x
    accumulator = np.full_like(x, _ERF_COEFFICIENTS[-1])
    for coefficient in _ERF_COEFFICIENTS[-2::-1]:
        accumulator = accumulator * y + coefficient
    erf = accumulator * x
    return 0.5 + 0.5 * erf


def _phi(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float64)
    return INV_SQRT_TWO_PI * np.exp(-0.5 * value * value)


def _Phi2_plackett_simpson(
    alpha_left: np.ndarray,
    alpha_right: np.ndarray,
    rho: np.ndarray,
) -> np.ndarray:
    # Inputs signs x events.  The one extra axis is the fixed 33-node rho path.
    r = rho[None, :, None] * _SIMPSON_FRACTIONS[None, None, :]
    left = alpha_left[:, :, None]
    right = alpha_right[:, :, None]
    one = 1.0 - r * r
    quadratic = left * left - 2.0 * r * left * right + right * right
    density = INV_TWO_PI * np.exp(-quadratic / (2.0 * one)) / np.sqrt(one)
    integral = (
        rho[None, :]
        / (3.0 * SIMPSON_PANELS)
        * np.sum(density * _SIMPSON_WEIGHTS[None, None, :], axis=2)
    )
    return _Phi16(alpha_left) * _Phi16(alpha_right) + integral


def evaluate_numpy(packed: PackedBatch) -> BatchResult:
    g = np.stack((packed.g, -packed.g), axis=0)
    mean_left = packed.pair_base_left[None, :] + packed.pair_slope_left[None, :] * g
    mean_right = packed.pair_base_right[None, :] + packed.pair_slope_right[None, :] * g
    alpha_left = mean_left / packed.pair_sigma_left[None, :]
    alpha_right = mean_right / packed.pair_sigma_right[None, :]
    rho = packed.pair_rho
    q = np.sqrt(1.0 - rho * rho)
    t_left = (alpha_right - rho[None, :] * alpha_left) / q[None, :]
    t_right = (alpha_left - rho[None, :] * alpha_right) / q[None, :]

    Phi_left = _Phi16(alpha_left)
    Phi_right = _Phi16(alpha_right)
    phi_left = _phi(alpha_left)
    phi_right = _phi(alpha_right)
    Phi2 = _Phi2_plackett_simpson(alpha_left, alpha_right, rho)
    d_left = phi_left * _Phi16(t_left)
    d_right = phi_right * _Phi16(t_right)
    joint = (
        INV_TWO_PI
        * np.exp(
            -(alpha_left * alpha_left - 2.0 * rho[None, :] * alpha_left * alpha_right + alpha_right * alpha_right)
            / (2.0 * (1.0 - rho[None, :] * rho[None, :]))
        )
        / q[None, :]
    )
    standard_pair = (
        alpha_right * d_left
        + alpha_left * d_right
        + (1.0 - rho[None, :] * rho[None, :]) * joint
        + (alpha_left * alpha_right + rho[None, :]) * Phi2
    )
    raw_pair = (
        packed.pair_sigma_left[None, :]
        * packed.pair_sigma_right[None, :]
        * standard_pair
    )
    unary_left = packed.pair_sigma_left[None, :] * (
        alpha_left * Phi_left + phi_left
    )
    unary_right = packed.pair_sigma_right[None, :] * (
        alpha_right * Phi_right + phi_right
    )
    centered_pair = (
        raw_pair
        - packed.activation_mean_left[None, :] * unary_right
        - packed.activation_mean_right[None, :] * unary_left
        + packed.activation_mean_left[None, :] * packed.activation_mean_right[None, :]
    )
    repeated_preactivation = (
        packed.repeated_mean[None, :] + packed.repeated_sigma[None, :] * g
    )
    repeated_centered = (
        np.maximum(repeated_preactivation, 0.0)
        - packed.repeated_activation_mean[None, :]
    )
    central = repeated_centered * repeated_centered * centered_pair
    offset = (
        packed.activation_vii * packed.activation_vjk
        + 2.0 * packed.activation_vij * packed.activation_vik
        + packed.tree
    )
    signed = central - offset[None, :]
    value = 0.5 * np.sum(signed, axis=0)

    max_alpha = np.maximum(np.abs(alpha_left), np.abs(alpha_right)).max(axis=0)
    max_t = np.maximum(np.abs(t_left), np.abs(t_right)).max(axis=0)
    max_repeated = np.abs(repeated_centered).max(axis=0)
    chart_ok = (
        (np.abs(rho) <= ABS_RHO_MAX)
        & (max_alpha <= ABS_STANDARD_MAX)
        & (max_t <= ABS_STANDARD_MAX)
        & (packed.pair_sigma_left >= SIGMA_MIN)
        & (packed.pair_sigma_left <= SIGMA_MAX)
        & (packed.pair_sigma_right >= SIGMA_MIN)
        & (packed.pair_sigma_right <= SIGMA_MAX)
        & (max_repeated <= REPEATED_CENTER_MAX)
        & np.isfinite(value)
    )
    fallback = ~chart_ok
    radius = EVENT_RADIUS_FACTOR * (1.0 + np.abs(value))
    value = np.where(chart_ok, value, np.nan)
    radius = np.where(chart_ok, radius, np.nan)
    return BatchResult(value, radius, chart_ok, fallback, max_alpha, max_t, max_repeated)


def scalar_m216_midpoints(packed: PackedBatch) -> np.ndarray:
    result = np.empty(packed.size, dtype=np.float64)
    for slot, (local, labels, g) in enumerate(
        zip(packed.local_states, packed.labels, packed.g, strict=True)
    ):
        result[slot] = _m216.antithetic_distinct_event(
            local, tuple(int(item) for item in labels), float(g)
        ).value
    return result


def scalar_m216_radii(packed: PackedBatch) -> np.ndarray:
    result = np.empty(packed.size, dtype=np.float64)
    for slot, (local, labels, g) in enumerate(
        zip(packed.local_states, packed.labels, packed.g, strict=True)
    ):
        result[slot] = _m216.antithetic_distinct_event(
            local, tuple(int(item) for item in labels), float(g)
        ).radius
    return result


def high_precision_midpoints(packed: PackedBatch, *, dps: int) -> np.ndarray:
    mp = _m216._load_mpmath()
    answer = np.empty(packed.size, dtype=np.float64)
    with mp.workdps(int(dps)):
        for slot, (local, labels, g_value) in enumerate(
            zip(packed.local_states, packed.labels, packed.g, strict=True)
        ):
            repeated, _, left, right = (int(item) for item in labels)
            g = mp.mpf(repr(float(g_value)))
            plus = _m216._mp_event_atom(mp, local, repeated, left, right, g)
            minus = _m216._mp_event_atom(mp, local, repeated, left, right, -g)
            answer[slot] = float((plus + minus) / 2)
    return answer


def _high_precision_subset() -> PackedBatch:
    batches = [
        single_event_batch(
            width=width,
            seed=seed,
            labels=(0, 0, 1, 2),
            outer_g=(0.0, 8.0, -8.0),
        )
        for width, seed in zip(WIDTHS, STATE_SEEDS, strict=True)
    ]
    batches.append(
        single_event_batch(
            width=6,
            seed=216700006,
            labels=(1, 1, 0, 2),
            outer_g=(8.0, -8.0),
        )
    )
    return concatenate_batches(batches)


def _invariance_gate() -> dict[str, object]:
    local = _m216.frozen_local_state(5, 221700005)
    owners = _m216.strict_physical_owners(5)
    probes = (-2.0, 0.0, 2.5)
    baseline = _pack_rows(local, ((labels, g) for labels in owners for g in probes))
    baseline_result = evaluate_numpy(baseline)
    gauge = np.exp(np.asarray((-0.4, -0.1, 0.0, 0.2, 0.5)))
    gauged_local = _m216.build_local_state(
        local.mean * gauge,
        local.covariance * gauge[:, None] * gauge[None, :],
    )
    gauged = _pack_rows(gauged_local, ((labels, g) for labels in owners for g in probes))
    gauged_result = evaluate_numpy(gauged)
    scales = np.asarray(
        [
            gauge[labels[0]] ** 2 * gauge[labels[2]] * gauge[labels[3]]
            for labels in baseline.labels
        ]
    )
    gauge_error = np.abs(gauged_result.value - scales * baseline_result.value) / (
        1.0 + np.abs(scales * baseline_result.value)
    )
    permutation = np.asarray((3, 0, 4, 1, 2), dtype=int)
    inverse = np.argsort(permutation)
    permuted_local = _m216.build_local_state(
        local.mean[permutation],
        local.covariance[np.ix_(permutation, permutation)],
    )
    permuted_rows = [
        (tuple(int(inverse[item]) for item in labels), float(g))
        for labels, g in zip(baseline.labels, baseline.g, strict=True)
    ]
    permuted = _pack_rows(permuted_local, permuted_rows)
    permuted_result = evaluate_numpy(permuted)
    permutation_error = np.abs(permuted_result.value - baseline_result.value) / (
        1.0 + np.abs(baseline_result.value)
    )
    baseline_fallback = int(np.count_nonzero(baseline_result.fallback))
    gauge_fallback = int(np.count_nonzero(gauged_result.fallback))
    permutation_fallback = int(np.count_nonzero(permuted_result.fallback))
    finite_gauge = gauge_error[np.isfinite(gauge_error)]
    finite_permutation = permutation_error[np.isfinite(permutation_error)]
    return {
        "pass": bool(
            np.all(baseline_result.chart_ok)
            and np.all(gauged_result.chart_ok)
            and np.all(permuted_result.chart_ok)
            and float(np.max(gauge_error)) <= 5.0e-8
            and float(np.max(permutation_error)) <= 5.0e-8
        ),
        "probe_count": baseline.size,
        "baseline_fallback_count": baseline_fallback,
        "gauge_fallback_count": gauge_fallback,
        "permutation_fallback_count": permutation_fallback,
        "gauged_sigma_min": float(min(np.min(gauged.pair_sigma_left), np.min(gauged.pair_sigma_right))),
        "gauged_sigma_max": float(max(np.max(gauged.pair_sigma_left), np.max(gauged.pair_sigma_right))),
        "max_gauge_scaled_error": float(np.max(finite_gauge)) if finite_gauge.size else math.nan,
        "max_permutation_scaled_error": float(np.max(finite_permutation)) if finite_permutation.size else math.nan,
    }


def run_frozen_numerical_gate() -> dict[str, object]:
    fallback_count = 0
    max_radius_ratio = 0.0
    max_parent_error = 0.0
    parent_containment = True
    total = 0
    chart_extrema = {"abs_rho": 0.0, "abs_alpha": 0.0, "abs_t": 0.0, "abs_repeated": 0.0}
    for width, seed in zip(WIDTHS, STATE_SEEDS, strict=True):
        packed = generated_probe_batch(width, seed)
        observed = evaluate_numpy(packed)
        parent = scalar_m216_midpoints(packed)
        parent_radius = scalar_m216_radii(packed)
        errors = np.abs(observed.value - parent)
        fallback_count += int(np.count_nonzero(observed.fallback))
        total += packed.size
        if np.any(observed.chart_ok):
            max_radius_ratio = max(
                max_radius_ratio,
                float(np.nanmax(observed.radius / (1.0 + np.abs(observed.value)))),
            )
            max_parent_error = max(max_parent_error, float(np.nanmax(errors)))
        parent_containment = parent_containment and bool(
            np.all(errors[observed.chart_ok] <= parent_radius[observed.chart_ok])
        )
        chart_extrema["abs_rho"] = max(chart_extrema["abs_rho"], float(np.max(np.abs(packed.pair_rho))))
        chart_extrema["abs_alpha"] = max(chart_extrema["abs_alpha"], float(np.max(observed.max_abs_alpha)))
        chart_extrema["abs_t"] = max(chart_extrema["abs_t"], float(np.max(observed.max_abs_t)))
        chart_extrema["abs_repeated"] = max(chart_extrema["abs_repeated"], float(np.max(observed.max_abs_repeated_center)))

    subset = _high_precision_subset()
    subset_observed = evaluate_numpy(subset)
    reference80 = high_precision_midpoints(subset, dps=80)
    reference100 = high_precision_midpoints(subset, dps=100)
    oracle_gap = np.abs(reference80 - reference100)
    reference_error = np.abs(subset_observed.value - reference100)
    high_precision_pass = bool(
        np.all(subset_observed.chart_ok)
        and np.all(oracle_gap <= 1.0e-12 * (1.0 + np.abs(reference100)))
        and np.all(reference_error <= subset_observed.radius)
    )
    inherited_slice = slice(subset.size - 2, subset.size)
    inherited_pass = bool(
        np.all(subset_observed.chart_ok[inherited_slice])
        and np.all(reference_error[inherited_slice] <= subset_observed.radius[inherited_slice])
    )
    invariance = _invariance_gate()
    numerical_pass = bool(
        fallback_count == 0
        and max_radius_ratio <= REQUIRED_RADIUS_FACTOR
        and parent_containment
        and high_precision_pass
        and inherited_pass
        and invariance["pass"]
    )
    return {
        "numerical_gate_pass": numerical_pass,
        "event_probe_count": total,
        "fallback_count": fallback_count,
        "max_radius_ratio": max_radius_ratio,
        "max_parent_midpoint_error": max_parent_error,
        "scalar_parent_containment_pass": bool(parent_containment),
        "high_precision_gate_pass": high_precision_pass,
        "high_precision_probe_count": subset.size,
        "high_precision_max_oracle_gap": float(np.max(oracle_gap)),
        "high_precision_max_midpoint_error": float(np.max(reference_error)),
        "high_precision_min_radius_margin": float(np.min(subset_observed.radius - reference_error)),
        "inherited_worst_pass": inherited_pass,
        "chart_extrema": chart_extrema,
        "invariance": invariance,
    }


__all__ = [
    "BatchResult",
    "PackedBatch",
    "M221DomainRefusal",
    "concatenate_batches",
    "evaluate_numpy",
    "generated_probe_batch",
    "high_precision_midpoints",
    "run_frozen_numerical_gate",
    "scalar_m216_midpoints",
    "single_event_batch",
]
