"""M161 response-free variance falsifier for the M156 complete-domain star.

This module deliberately measures no neural-network output, truth, scorer, or
competition row.  Each frozen cell is a small Gaussian background.  Its
preactivation covariance is the already-present ``V`` in
``c[i,j,k] = -2 V[i,j] V[i,k]``.  The exact target is M147's certified
noncentral connected [2,1,1] defect on pairwise-distinct labels and zero on
collisions.

The variance functional is an exhaustive finite-population Hansen--Hurwitz
calculation under one frozen, target-mass two-stratum proposal.  We report two
separate quantities: a scalar coefficient proxy and the full pre-transport
M133 source-slot vector.  There is intentionally no claimed final-output
carrier: an independently traceable M125b forward background is not part of
this small-width source-only premise.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for _relative in (
    "m147_endpoint_safe_bridge",
    "m156_extended_domain_star_control",
):
    _path = str(ROOT / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m147_endpoint_safe_bridge import (  # noqa: E402
    EndpointCertificationFailure,
    build_endpoint_state_frechet,
    conditional_collision211_endpoint_dot,
)
from m156_extended_domain_star_control import (  # noqa: E402
    Source211,
    collision_count,
    collision_strata,
    compiled_extended_star_control,
    dense_extended_source,
    distinct_count,
    distinct_target_extension,
    extended_feature,
    extended_star_table,
    residual_table,
    source_add,
    source_max_abs_difference,
)


ORDERED_OWNER = 0.5
TARGET_WIDTH = 256
TARGET_COLLISION_MASS = collision_count(TARGET_WIDTH) / float(TARGET_WIDTH**3)
CELL_SPECS = (
    ("isotropic_w4", 4, 1610401, 0.20),
    ("factor_w4", 4, 1610402, 0.52),
    ("isotropic_w5", 5, 1610501, 0.20),
    ("factor_w5", 5, 1610502, 0.52),
    ("isotropic_w6", 6, 1610601, 0.20),
    ("factor_w6", 6, 1610602, 0.52),
)
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED = 1619001


@dataclass(frozen=True)
class Cell:
    name: str
    width: int
    seed: int
    correlation_mix: float
    mean: np.ndarray
    covariance: np.ndarray
    weight: np.ndarray


@dataclass(frozen=True)
class ProxyMetrics:
    raw_variance: float
    residual_variance: float
    residual_to_raw: float
    raw_p99_squared: float
    residual_p99_squared: float
    residual_to_raw_p99: float
    collision_residual_second_fraction: float
    collision_residual_p99_squared: float
    collision_to_raw_p99: float


def _correlation_from_seed(rng: np.random.Generator, width: int, mix: float) -> np.ndarray:
    """Well-conditioned SPD correlation with a frozen endpoint exclusion."""

    factor = rng.normal(size=(width, width))
    raw = factor @ factor.T
    diagonal = np.sqrt(np.diag(raw))
    normalized = raw / np.outer(diagonal, diagonal)
    correlation = (1.0 - mix) * np.eye(width) + mix * normalized
    correlation = 0.5 * (correlation + correlation.T)
    np.fill_diagonal(correlation, 1.0)
    if float(np.max(np.abs(correlation - np.eye(width)))) >= 0.60:
        raise AssertionError("frozen M161 cell left the endpoint-excluded domain")
    if float(np.min(np.linalg.eigvalsh(correlation))) <= 0.35:
        raise AssertionError("frozen M161 cell is not comfortably SPD")
    return correlation


def frozen_cells() -> tuple[Cell, ...]:
    """Create the six predeclared generated cells without inspecting targets."""

    answer: list[Cell] = []
    for name, width, seed, mix in CELL_SPECS:
        rng = np.random.default_rng(seed)
        correlation = _correlation_from_seed(rng, width, mix)
        scale = np.exp(rng.uniform(-0.35, 0.35, size=width))
        covariance = scale[:, None] * correlation * scale[None, :]
        # M147's certified endpoint ABI requires exact bitwise symmetry, not
        # merely an allclose SPD matrix.
        covariance = 0.5 * (covariance + covariance.T)
        mean = rng.normal(scale=0.30, size=width)
        # One additional output coordinate makes the complete source-slot
        # proxy nontrivial without pretending it is a final response carrier.
        weight = rng.normal(scale=1.0 / math.sqrt(width + 1), size=(width, width + 1))
        answer.append(Cell(name, width, seed, mix, mean, covariance, weight))
    return tuple(answer)


def frozen_probability(width: int, unit: tuple[int, int, int]) -> float:
    """M161's target-mass, full-support, nonadaptive q0.

    The collision mass is frozen to its width-256 M156 value so that the
    small-width test does not artificially make collisions a 40--60 percent
    event.  Each stratum is uniform; this is intentionally a source-only
    baseline, not a claim about M133's factored production proposal.
    """

    if len(set(unit)) == 3:
        return (1.0 - TARGET_COLLISION_MASS) / float(distinct_count(width))
    return TARGET_COLLISION_MASS / float(collision_count(width))


def _source_vector(source: Source211) -> np.ndarray:
    return np.concatenate((source.aaaa.ravel(), source.aaab.ravel(), source.aabb.ravel()))


def _feature_vector(weight: np.ndarray, unit: tuple[int, int, int]) -> np.ndarray:
    return _source_vector(extended_feature(weight, *unit))


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    if values.ndim != 1 or weights.shape != values.shape:
        raise ValueError("weighted quantile expects matching vectors")
    if not (0.0 < quantile <= 1.0) or np.any(weights <= 0.0):
        raise ValueError("invalid quantile or probability weights")
    order = np.argsort(values, kind="mergesort")
    total = float(np.sum(weights))
    threshold = quantile * total
    slot = int(np.searchsorted(np.cumsum(weights[order]), threshold, side="left"))
    return float(values[order[min(slot, values.size - 1)]])


def _finite_population_metrics(
    coefficient: np.ndarray,
    weight: np.ndarray,
    width: int,
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return HH trace variance and p99 ingredients for one coefficient table."""

    units = [(i, j, k) for i in range(width) for j in range(width) for k in range(width)]
    q = np.asarray([frozen_probability(width, unit) for unit in units], dtype=np.float64)
    if not math.isclose(float(np.sum(q)), 1.0, rel_tol=0.0, abs_tol=3e-14):
        raise AssertionError("M161 q0 lost probability mass")
    vectors = np.asarray(
        [
            ORDERED_OWNER * coefficient[unit] * _feature_vector(weight, unit) / probability
            for unit, probability in zip(units, q)
        ],
        dtype=np.float64,
    )
    mean = q @ vectors
    squared = np.einsum("ij,ij->i", vectors, vectors)
    variance = float(np.dot(q, squared) - np.dot(mean, mean))
    scale = max(1.0, float(np.dot(q, squared)))
    if variance < -2e-12 * scale:
        raise ArithmeticError("finite-population variance is materially negative")
    return max(variance, 0.0), _weighted_quantile(squared, q, 0.99), q, squared, np.asarray(units), vectors


def certified_target_table(cell: Cell) -> tuple[np.ndarray, dict[str, float | int]]:
    """Certify every distinct target coefficient before any variance readout."""

    zero = np.zeros(cell.width, dtype=np.float64)
    tangent = build_endpoint_state_frechet(cell.mean, cell.covariance, zero, np.zeros_like(cell.covariance))
    target = np.zeros((cell.width, cell.width, cell.width), dtype=np.float64)
    max_value_disagreement = 0.0
    max_tangent_disagreement = 0.0
    angular_evaluations = 0
    calls = 0
    for repeated in range(cell.width):
        for left in range(cell.width):
            for right in range(left + 1, cell.width):
                if repeated in (left, right):
                    continue
                certificate = conditional_collision211_endpoint_dot(
                    tangent, repeated, left, right,
                    coarse_order=48,
                    fine_order=64,
                    value_tolerance=2.0e-8,
                    tangent_tolerance=2.0e-7,
                )
                target[repeated, left, right] = certificate.defect
                target[repeated, right, left] = certificate.defect
                max_value_disagreement = max(max_value_disagreement, certificate.value_disagreement)
                max_tangent_disagreement = max(max_tangent_disagreement, certificate.tangent_disagreement)
                angular_evaluations += certificate.quadrant_integrand_evaluations
                calls += 1
    return distinct_target_extension(target), {
        "provider_calls": calls,
        "provider_max_value_disagreement": max_value_disagreement,
        "provider_max_tangent_disagreement": max_tangent_disagreement,
        "provider_angular_integrand_evaluations": angular_evaluations,
    }


def proxy_metrics(target: np.ndarray, control: np.ndarray, cell: Cell) -> tuple[ProxyMetrics, ProxyMetrics]:
    """Coefficient and complete pre-transport-source finite-population metrics."""

    residual = residual_table(target, control)
    raw_variance, raw_p99, q, raw_squared, units, _ = _finite_population_metrics(target, cell.weight, cell.width)
    residual_variance, residual_p99, q2, residual_squared, units2, _ = _finite_population_metrics(residual, cell.weight, cell.width)
    if not (np.array_equal(units, units2) and np.allclose(q, q2, rtol=0.0, atol=0.0)):
        raise AssertionError("raw/residual q0 mismatch")
    collision = np.asarray([len(set(tuple(unit))) < 3 for unit in units], dtype=bool)
    collision_second = float(np.dot(q[collision], residual_squared[collision]))
    residual_second = float(np.dot(q, residual_squared))
    source = ProxyMetrics(
        raw_variance=raw_variance,
        residual_variance=residual_variance,
        residual_to_raw=(residual_variance / raw_variance if raw_variance > 0.0 else math.inf),
        raw_p99_squared=raw_p99,
        residual_p99_squared=residual_p99,
        residual_to_raw_p99=(residual_p99 / raw_p99 if raw_p99 > 0.0 else math.inf),
        collision_residual_second_fraction=(collision_second / residual_second if residual_second > 0.0 else 0.0),
        collision_residual_p99_squared=_weighted_quantile(residual_squared[collision], q[collision], 0.99),
        collision_to_raw_p99=(_weighted_quantile(residual_squared[collision], q[collision], 0.99) / raw_p99 if raw_p99 > 0.0 else math.inf),
    )

    # Scalar coefficient proxy is kept separate from the source proxy.  It
    # cannot imply a final-output improvement, but detects whether an apparent
    # source gain is merely feature-norm weighting.
    def coefficient_scalar(table: np.ndarray) -> ProxyMetrics:
        values = np.asarray([ORDERED_OWNER * table[tuple(unit)] / probability for unit, probability in zip(units, q)])
        second = values * values
        average = float(np.dot(q, values))
        variance = max(float(np.dot(q, second) - average * average), 0.0)
        return ProxyMetrics(variance, 0.0, 0.0, _weighted_quantile(second, q, 0.99), 0.0, 0.0, 0.0, 0.0, 0.0)

    raw_scalar = coefficient_scalar(target)
    residual_scalar = coefficient_scalar(residual)
    residual_scalar_values = np.asarray(
        [
            ORDERED_OWNER * residual[tuple(unit)] / probability
            for unit, probability in zip(units, q)
        ],
        dtype=np.float64,
    )
    residual_scalar_squared = residual_scalar_values * residual_scalar_values
    scalar_collision = float(np.dot(q[collision], residual_scalar_squared[collision]))
    scalar_second = float(np.dot(q, residual_scalar_squared))
    # Reconstruct the scalar reporting record without conflating it with the
    # source-vector trace variance.
    coefficient = ProxyMetrics(
        raw_variance=raw_scalar.raw_variance,
        residual_variance=residual_scalar.raw_variance,
        residual_to_raw=(residual_scalar.raw_variance / raw_scalar.raw_variance if raw_scalar.raw_variance > 0.0 else math.inf),
        raw_p99_squared=raw_scalar.raw_p99_squared,
        residual_p99_squared=residual_scalar.raw_p99_squared,
        residual_to_raw_p99=(residual_scalar.raw_p99_squared / raw_scalar.raw_p99_squared if raw_scalar.raw_p99_squared > 0.0 else math.inf),
        collision_residual_second_fraction=(scalar_collision / scalar_second if scalar_second > 0.0 else 0.0),
        collision_residual_p99_squared=_weighted_quantile(residual_scalar_squared[collision], q[collision], 0.99),
        collision_to_raw_p99=(_weighted_quantile(residual_scalar_squared[collision], q[collision], 0.99) / raw_scalar.raw_p99_squared if raw_scalar.raw_p99_squared > 0.0 else math.inf),
    )
    return coefficient, source


def symmetry_audit(cell: Cell) -> dict[str, float]:
    """Independent finite-precision permutation/gauge audit of M161's ABI.

    This does not alter the frozen six-cell variance result.  It checks the
    actual certified target provider, the already-owned covariance-star
    control, complete-domain ownership, and the source proxy under two legal
    reparameterizations.
    """

    target, _ = certified_target_table(cell)
    control = extended_star_table(cell.covariance)
    coefficient, source = proxy_metrics(target, control, cell)
    rng = np.random.default_rng(1617001)

    permutation = rng.permutation(cell.width)
    permuted = Cell(
        "permuted",
        cell.width,
        cell.seed,
        cell.correlation_mix,
        cell.mean[permutation],
        cell.covariance[permutation][:, permutation],
        cell.weight[permutation],
    )
    target_p, _ = certified_target_table(permuted)
    control_p = extended_star_table(permuted.covariance)
    coefficient_p, source_p = proxy_metrics(target_p, control_p, permuted)
    expected_target_p = target[np.ix_(permutation, permutation, permutation)]
    expected_control_p = control[np.ix_(permutation, permutation, permutation)]

    gauge = np.exp(rng.uniform(-0.45, 0.45, size=cell.width))
    gauged = Cell(
        "gauged",
        cell.width,
        cell.seed,
        cell.correlation_mix,
        gauge * cell.mean,
        0.5 * (
            gauge[:, None] * cell.covariance * gauge[None, :]
            + (gauge[:, None] * cell.covariance * gauge[None, :]).T
        ),
        cell.weight / gauge[:, None],
    )
    target_g, _ = certified_target_table(gauged)
    control_g = extended_star_table(gauged.covariance)
    coefficient_g, source_g = proxy_metrics(target_g, control_g, gauged)
    scale = gauge[:, None, None] ** 2 * gauge[None, :, None] * gauge[None, None, :]

    def difference(left: float, right: float) -> float:
        return abs(left - right) / max(1.0, abs(left), abs(right))

    return {
        "permutation_target_max_abs": float(np.max(np.abs(target_p - expected_target_p))),
        "permutation_control_max_abs": float(np.max(np.abs(control_p - expected_control_p))),
        "permutation_source_variance_relative": difference(source_p.raw_variance, source.raw_variance),
        "permutation_residual_variance_relative": difference(source_p.residual_variance, source.residual_variance),
        "permutation_coefficient_variance_relative": difference(coefficient_p.raw_variance, coefficient.raw_variance),
        "gauge_target_relative": float(np.max(np.abs(target_g - scale * target)) / max(1.0, float(np.max(np.abs(scale * target))))),
        "gauge_control_relative": float(np.max(np.abs(control_g - scale * control)) / max(1.0, float(np.max(np.abs(scale * control))))),
        "gauge_source_variance_relative": difference(source_g.raw_variance, source.raw_variance),
        "gauge_residual_variance_relative": difference(source_g.residual_variance, source.residual_variance),
        "gauge_coefficient_variance_relative": difference(coefficient_g.raw_variance, coefficient.raw_variance),
    }


def _bootstrap_upper90(raw: np.ndarray, residual: np.ndarray) -> float:
    if raw.shape != residual.shape or raw.ndim != 1 or np.any(raw <= 0.0):
        raise ValueError("invalid paired variance vectors")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    ratios = np.empty(BOOTSTRAP_REPLICATES, dtype=np.float64)
    for slot in range(BOOTSTRAP_REPLICATES):
        selected = rng.integers(0, raw.size, size=raw.size)
        ratios[slot] = float(np.mean(residual[selected]) / np.mean(raw[selected]))
    return float(np.quantile(ratios, 0.90, method="higher"))


def _width_slope(cells: Iterable[dict[str, object]], key: str) -> float:
    grouped: dict[int, list[float]] = {}
    for record in cells:
        grouped.setdefault(int(record["width"]), []).append(float(record[key]))
    x = np.asarray(sorted(grouped), dtype=np.float64)
    y = np.asarray([np.mean(grouped[int(width)]) for width in x], dtype=np.float64)
    return float(np.polyfit(x, y, 1)[0])


def run_frozen_premise() -> dict[str, object]:
    """Execute the predeclared response-free source variance screen once."""

    records: list[dict[str, object]] = []
    for cell in frozen_cells():
        try:
            target, certificate = certified_target_table(cell)
        except EndpointCertificationFailure as error:
            return {
                "status": "PROVIDER_BLOCKED_NO_FABRICATION",
                "failed_cell": cell.name,
                "failure": str(error),
                "cells_completed": len(records),
            }
        control = extended_star_table(cell.covariance)
        residual = residual_table(target, control)
        # Algebra/ownership check against the compiler survives independently
        # of the variance result.
        direct_target = dense_extended_source(cell.weight, target)
        reconstructed = source_add(
            compiled_extended_star_control(cell.weight, cell.covariance),
            dense_extended_source(cell.weight, residual),
        )
        conservation_error = source_max_abs_difference(direct_target, reconstructed)
        if conservation_error > 4.0e-8:
            raise ArithmeticError("complete-domain control/residual source conservation failed")
        coefficient, source = proxy_metrics(target, control, cell)
        maximum_correlation = float(np.max(np.abs(cell.covariance / np.outer(np.sqrt(np.diag(cell.covariance)), np.sqrt(np.diag(cell.covariance))) - np.eye(cell.width))))
        records.append({
            "name": cell.name,
            "width": cell.width,
            "seed": cell.seed,
            "correlation_mix": cell.correlation_mix,
            "max_abs_offdiagonal_correlation": maximum_correlation,
            "minimum_covariance_eigenvalue": float(np.min(np.linalg.eigvalsh(cell.covariance))),
            "provider": certificate,
            "source_conservation_max_abs": conservation_error,
            "coefficient_proxy": asdict(coefficient),
            "source_slot_proxy": asdict(source),
        })

    source_raw = np.asarray([record["source_slot_proxy"]["raw_variance"] for record in records], dtype=np.float64)
    source_residual = np.asarray([record["source_slot_proxy"]["residual_variance"] for record in records], dtype=np.float64)
    coefficient_raw = np.asarray([record["coefficient_proxy"]["raw_variance"] for record in records], dtype=np.float64)
    coefficient_residual = np.asarray([record["coefficient_proxy"]["residual_variance"] for record in records], dtype=np.float64)
    source_upper90 = _bootstrap_upper90(source_raw, source_residual)
    coefficient_upper90 = _bootstrap_upper90(coefficient_raw, coefficient_residual)
    source_p99_max = max(float(record["source_slot_proxy"]["residual_to_raw_p99"]) for record in records)
    collision_p99_max = max(float(record["source_slot_proxy"]["collision_to_raw_p99"]) for record in records)
    source_slope = _width_slope(
        [{"width": record["width"], "ratio": record["source_slot_proxy"]["residual_to_raw"]} for record in records],
        "ratio",
    )
    gate = {
        "source_upper90_ratio_lt_0_25": source_upper90 < 0.25,
        "source_p99_ratio_lte_1_25": source_p99_max <= 1.25,
        "collision_p99_ratio_lte_1_25": collision_p99_max <= 1.25,
        "source_width_slope_nonpositive": source_slope <= 0.0,
    }
    return {
        "status": "SOURCE_PROXY_PASS" if all(gate.values()) else "SOURCE_PROXY_KILLED",
        "scope": "response-free generated Gaussian cells; no final-output carrier, truth, scorer, contest model, or score",
        "proposal": {
            "name": "M161 fixed target-mass two-stratum uniform q0",
            "target_width": TARGET_WIDTH,
            "collision_mass": TARGET_COLLISION_MASS,
            "distinct_mass": 1.0 - TARGET_COLLISION_MASS,
            "adaptive": False,
        },
        "primary_gate": {
            "source_residual_raw_upper90_lt": 0.25,
            "source_and_collision_p99_ratio_lte": 1.25,
            "source_width_slope_lte": 0.0,
        },
        "gate": gate,
        "aggregate": {
            "source_ratio": float(np.mean(source_residual) / np.mean(source_raw)),
            "source_upper90_ratio": source_upper90,
            "source_max_p99_ratio": source_p99_max,
            "source_max_collision_p99_ratio": collision_p99_max,
            "source_width_ratio_slope": source_slope,
            "coefficient_ratio": float(np.mean(coefficient_residual) / np.mean(coefficient_raw)),
            "coefficient_upper90_ratio": coefficient_upper90,
        },
        "cells": records,
    }


def main() -> None:
    print(json.dumps(run_frozen_premise(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
