"""Frozen-shape, not-yet-frozen M124 generated-only protocol definition."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np

from m124_shared_projector import (
    BOUNDARY_GAP_RELATIVE,
    RANK,
    build_nonzero_bridge_source,
    combined_source_fidelity,
    correction_ratio,
    edgeworth_delay_one,
    physical_source,
    project_source,
    reconstruct,
    repeated_output_k4_relative,
    shared_projector,
    source_fidelity,
    transport_dense,
    transport_projected,
)


ALGEBRA_TOLERANCE = 1.0e-10
SOURCE_FIDELITY_GATE = 0.80
CORRECTION_RATIO_GATE = 0.50
REPEATED_OUTPUT_K4_GATE = 0.50
INCREMENTAL_CEILING = 152_000_000_000
SOURCE_ONLY_CEILING = 99_000_000_000


@dataclass(frozen=True)
class Case:
    width: int
    alpha_scale: float
    seed: int


CASES = (
    Case(8, 0.15, 1_240_801),
    Case(8, 0.35, 1_240_802),
    Case(8, 0.65, 1_240_803),
    Case(12, 0.15, 1_241_201),
    Case(12, 0.35, 1_241_202),
    Case(12, 0.65, 1_241_203),
    Case(16, 0.15, 1_241_601),
    Case(16, 0.35, 1_241_602),
    Case(16, 0.65, 1_241_603),
)


def generated_background(case: Case) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.Generator(np.random.Philox(case.seed))
    n = case.width
    factor = rng.normal(size=(n, n)) / math.sqrt(n)
    covariance = factor @ factor.T + 0.75 * np.eye(n)
    covariance = 0.5 * (covariance + covariance.T)
    mean = case.alpha_scale * np.sqrt(np.diag(covariance)) * rng.normal(size=n)
    weight = rng.normal(0.0, math.sqrt(2.0 / n), size=(n, n))
    return mean, covariance, weight


def _combined_relative(left: tuple[np.ndarray, ...], right: tuple[np.ndarray, ...]) -> float:
    numerator = sum(float(np.sum((a - b) ** 2)) for a, b in zip(left, right))
    denominator = sum(float(np.sum(a * a)) for a in left)
    return math.sqrt(numerator / max(denominator, 1.0e-300))


def _projector_relative(left: np.ndarray, right: np.ndarray) -> float:
    numerator = float(np.linalg.norm(left @ left.T - right @ right.T))
    denominator = max(float(np.linalg.norm(left @ left.T)), 1.0e-300)
    return numerator / denominator


def _projected_defect(source, projected, weight: np.ndarray):
    t3_factor, t4_factor = transport_projected(projected, weight)
    next_mean = weight.T @ source.activation_mean
    next_covariance = weight.T @ source.activation_covariance @ weight
    next_covariance = 0.5 * (next_covariance + next_covariance.T)
    return edgeworth_delay_one(next_mean, next_covariance, t3_factor, t4_factor)


def evaluate_case(case: Case) -> dict[str, object]:
    """Future frozen outcome evaluator.  The current CLI cannot call it."""
    mean, covariance, weight = generated_background(case)
    source = build_nonzero_bridge_source(mean, covariance)
    projector = shared_projector(source)
    projected = project_source(source, projector)

    reconstructed3 = reconstruct(projected.core3, projected.factor_standard)
    reconstructed4 = reconstruct(projected.core4, projected.factor_standard)
    physical_reconstructed3 = reconstructed3 * np.einsum(
        "i,j,k->ijk", source.activation_scale, source.activation_scale, source.activation_scale
    )
    physical_reconstructed4 = reconstructed4 * np.einsum(
        "i,j,k,l->ijkl",
        source.activation_scale,
        source.activation_scale,
        source.activation_scale,
        source.activation_scale,
    )
    t3_factor, t4_factor = transport_projected(projected, weight)
    t3_reconstructed = transport_dense(physical_reconstructed3, weight)
    t4_reconstructed = transport_dense(physical_reconstructed4, weight)
    algebra_transport = _combined_relative((t3_reconstructed, t4_reconstructed), (t3_factor, t4_factor))

    dense_t3 = transport_dense(physical_source(source, 3), weight)
    dense_t4 = transport_dense(physical_source(source, 4), weight)
    next_mean = weight.T @ source.activation_mean
    next_covariance = weight.T @ source.activation_covariance @ weight
    next_covariance = 0.5 * (next_covariance + next_covariance.T)
    reference = edgeworth_delay_one(next_mean, next_covariance, dense_t3, dense_t4)
    approximation = edgeworth_delay_one(next_mean, next_covariance, t3_factor, t4_factor)

    # A fixed Philox transformation per cell makes both equivariance gates
    # outcome-bearing without choosing a favourable relabelling or gauge.
    invariance_rng = np.random.Generator(np.random.Philox(case.seed + 124_000_000))
    permutation = invariance_rng.permutation(case.width)
    source_p = build_nonzero_bridge_source(
        mean[permutation], covariance[np.ix_(permutation, permutation)]
    )
    projector_p = shared_projector(source_p)
    projected_p = project_source(source_p, projector_p)
    approximation_p = _projected_defect(source_p, projected_p, weight[permutation, :])
    permutation_projector = _projector_relative(
        projector.factor_standard[permutation, :], projector_p.factor_standard
    )
    permutation_correction = _combined_relative(
        (approximation.mean, approximation.covariance),
        (approximation_p.mean, approximation_p.covariance),
    )

    gauge = invariance_rng.uniform(0.25, 3.0, size=case.width)
    source_g = build_nonzero_bridge_source(
        gauge * mean, gauge[:, None] * covariance * gauge[None, :]
    )
    projector_g = shared_projector(source_g)
    projected_g = project_source(source_g, projector_g)
    approximation_g = _projected_defect(source_g, projected_g, weight / gauge[:, None])
    gauge_projector = _projector_relative(projector.factor_standard, projector_g.factor_standard)
    gauge_correction = _combined_relative(
        (approximation.mean, approximation.covariance),
        (approximation_g.mean, approximation_g.covariance),
    )

    return {
        "case": asdict(case),
        "rank": RANK,
        "boundary_gap": projector.boundary_gap,
        "boundary_gap_relative": projector.boundary_gap / max(float(projector.eigenvalues[0]), 1.0),
        "source_fidelity": combined_source_fidelity(source, projected),
        "source_fidelity_k3": source_fidelity(source, projected, 3),
        "source_fidelity_k4": source_fidelity(source, projected, 4),
        "repeated_output_k4_relative": repeated_output_k4_relative(dense_t4, t4_factor),
        "correction_ratio_to_zero": correction_ratio(reference, approximation),
        "factor_transport_algebra_relative": algebra_transport,
        "permutation_projector_relative": permutation_projector,
        "permutation_correction_relative": permutation_correction,
        "positive_gauge_projector_relative": gauge_projector,
        "positive_gauge_correction_relative": gauge_correction,
        "finite": bool(
            np.all(np.isfinite(reference.mean))
            and np.all(np.isfinite(reference.covariance))
            and np.all(np.isfinite(approximation.mean))
            and np.all(np.isfinite(approximation.covariance))
        ),
    }


def static_cost_ledger() -> dict[str, int | float]:
    """Conservative non-overlap target ledger with one global safety factor."""
    n, layers = 256, 31
    square_f32 = 2 * n**3 - n**2
    square_float64 = 2 * square_f32
    safety = 1.25
    # Five weighted-tree Gram products, twelve dense-equivalent collision
    # products, and ten n^3 equivalents for a symmetric eigensolve.
    factor_equivalent_calls = layers * (5 + 12 + 10)
    raw_components = {
        "g3_factor_and_eigensolve": factor_equivalent_calls * square_float64,
        "tree_path_cores": 11_214_520_320,
        "nonzero_star_cores": 160_000_000,
        "collision_cores": 6_000_000_000,
        "source_transports": 32_505_856,
        "dense_defect_cp_pairing": 16_641_000_000,
        "analytic_collision_source_scalars": 4_000_000_000,
        "response_scalar_reserve": 1_600_000_000,
        "copies_allocation_reserve": 1_600_000_000,
    }
    raw_total = sum(raw_components.values())
    effective_components = {
        name: int(math.ceil(value * safety)) for name, value in raw_components.items()
    }
    total = int(math.ceil(raw_total * safety))
    source_component_names = (
        "g3_factor_and_eigensolve",
        "tree_path_cores",
        "nonzero_star_cores",
        "collision_cores",
        "source_transports",
        "analytic_collision_source_scalars",
        "copies_allocation_reserve",
    )
    source_only_raw = sum(raw_components[name] for name in source_component_names)
    source_only_effective = int(math.ceil(source_only_raw * safety))
    return {
        "square_f32_bill": square_f32,
        "square_float64_bill": square_float64,
        "safety_factor_once": safety,
        "raw_components": raw_components,
        "raw_total": raw_total,
        "effective_components": effective_components,
        "source_component_names": source_component_names,
        "source_only_raw": source_only_raw,
        "source_only_effective": source_only_effective,
        "carrier_allowance_below_ceiling": INCREMENTAL_CEILING - source_only_effective,
        "incremental_total": total,
        "incremental_ceiling": INCREMENTAL_CEILING,
        "headroom": INCREMENTAL_CEILING - total,
    }


def adjudicate(rows: list[dict[str, object]], manifest: dict[str, object]) -> dict[str, object]:
    """Apply every declared gate mechanically; no discretionary promotion."""
    gates = manifest["gates"]
    failures: list[str] = []
    if len(rows) != len(manifest["cases"]):
        failures.append("row_count")
    for index, row in enumerate(rows):
        label = f"cell_{index}"
        if "failure" in row:
            failures.append(f"{label}:resource_or_domain_failure")
            continue
        checks = (
            (float(row["factor_transport_algebra_relative"]) <= float(gates["algebra_relative_max"]), "algebra"),
            (float(row["source_fidelity"]) >= float(gates["combined_source_fidelity_min_every_cell"]), "source_fidelity"),
            (
                min(float(row["source_fidelity_k3"]), float(row["source_fidelity_k4"]))
                >= float(gates["source_fidelity_min_each_order_every_cell"]),
                "source_fidelity_by_order",
            ),
            (
                float(row["repeated_output_k4_relative"])
                <= float(gates["repeated_output_k4_relative_max_every_cell"]),
                "repeated_output_k4",
            ),
            (float(row["correction_ratio_to_zero"]) <= float(gates["correction_ratio_to_zero_max_every_cell"]), "correction"),
            (bool(row["finite"]) is bool(gates["finite_every_cell"]), "finite"),
            (
                max(float(row["permutation_projector_relative"]), float(row["permutation_correction_relative"]))
                <= float(gates["permutation_projector_and_correction_relative_max"]),
                "permutation",
            ),
            (
                max(float(row["positive_gauge_projector_relative"]), float(row["positive_gauge_correction_relative"]))
                <= float(gates["positive_gauge_projector_and_correction_relative_max"]),
                "positive_gauge",
            ),
        )
        failures.extend(f"{label}:{name}" for passed, name in checks if not passed)
    if int(manifest["cost_ledger"]["source_only_effective"]) >= int(gates["source_only_effective_compute_max"]):
        failures.append("source_only_cost")
    carrier = manifest.get("carrier_prerequisite", {})
    if carrier.get("status") == "PASSED_AND_HASH_LOCKED":
        carrier_cost = carrier.get("effective_compute")
        carrier_hash = carrier.get("artifact_hash")
        if not isinstance(carrier_cost, int) or carrier_cost < 0 or not isinstance(carrier_hash, str) or not carrier_hash:
            failures.append("carrier_certificate")
        elif int(manifest["cost_ledger"]["source_only_effective"]) + carrier_cost >= int(
            gates["combined_source_plus_carrier_compute_max"]
        ):
            failures.append("combined_cost")
    return {
        "verdict": "SOURCE_PASS" if not failures else "SOURCE_KILL",
        "failures": failures,
        "cells_evaluated": len(rows),
        "no_retry": bool(manifest.get("no_retry")),
    }
def draft_manifest() -> dict[str, object]:
    return {
        "schema": 1,
        "candidate": "M124_SHARED_K3_PROJECTOR",
        "status": "DRAFT_NOT_FROZEN",
        "execution_authorized": False,
        "carrier_prerequisite": {
            "candidate": "M125_FORWARD_DENSE_TANGENT",
            "status": "UNRESOLVED",
            "artifact_hash": None,
            "effective_compute": None,
            "required_status_before_source_grid": "PASSED_AND_HASH_LOCKED",
            "maximum_nonoverlap_effective_compute": static_cost_ledger()["carrier_allowance_below_ceiling"],
        },
        "firewall": "generated Philox Gaussian backgrounds only; no contest/public/private data, scorer, champion, or submission",
        "rank": RANK,
        "rank_provenance": "frozen from M85 before M124",
        "boundary_gap_relative": BOUNDARY_GAP_RELATIVE,
        "cases": [asdict(case) for case in CASES],
        "gates": {
            "algebra_relative_max": ALGEBRA_TOLERANCE,
            "combined_source_fidelity_min_every_cell": SOURCE_FIDELITY_GATE,
            "source_fidelity_min_each_order_every_cell": SOURCE_FIDELITY_GATE,
            "repeated_output_k4_relative_max_every_cell": REPEATED_OUTPUT_K4_GATE,
            "correction_ratio_to_zero_max_every_cell": CORRECTION_RATIO_GATE,
            "finite_every_cell": True,
            "permutation_projector_and_correction_relative_max": ALGEBRA_TOLERANCE,
            "positive_gauge_projector_and_correction_relative_max": ALGEBRA_TOLERANCE,
            "zero_resource_failures": True,
            "source_only_effective_compute_max": SOURCE_ONLY_CEILING,
            "combined_source_plus_carrier_compute_max": INCREMENTAL_CEILING,
        },
        "cost_ledger": static_cost_ledger(),
        "outcome_state": "UNOPENED",
        "no_retry": True,
    }
