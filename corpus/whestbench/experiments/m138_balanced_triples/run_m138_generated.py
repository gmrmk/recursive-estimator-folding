"""Frozen generated-only output-functional audit for M138 balancing.

This audit intentionally measures the final *mean-output response* after all
of the following on fresh generated Gaussian/ReLU chains:

1. complete repeated-slot M121 one-delay conversion (mean and covariance);
2. M125b's inhomogeneous all-source suffix recurrence; and
3. the unchanged five-product M133 ``[2,1,1]`` contraction.

It never loads contest inputs, reference values, scores, submissions, or
leaderboard data.  The exact generated target is a vectorized small-width
``[2,1,1]`` contraction, used only to measure the balanced-versus-iid output
MSE of the one changed sampling operator.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m133_ht_hidden_edge",
    "m129_source_frechet_tangent",
    "m120_price_normal_ordered_adjoint",
    "m125_source_batched_forward_tangent",
    "m131_trivariate_boundary_stream",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)
sys.path.insert(0, str(HERE))

from m120c_analytic_dense_reference import analytic_local_kernels, analytic_relu_gaussian_moments  # noqa: E402
from m125_forward_tangent import LocalReluJacobian, TangentState, tangent_stage  # noqa: E402
from m129_source_frechet import Dual  # noqa: E402
from m131_trivariate_boundary_stream import one_delay_edgeworth_source  # noqa: E402
from m133_ht_hidden_edge import collision211_factored_proposal, collision211_hh_batched  # noqa: E402
from m138_balanced_triples import balanced_factored_draws, balanced_sampling_bill  # noqa: E402


CONFIG = {
    "widths": [12, 16, 24, 32],
    "development_seeds": [1338101, 1338102, 1338103, 1338104],
    "confirmation_seeds": [1388101, 1388102, 1388103, 1388104],
    "development_replicates": 128,
    "confirmation_replicates": 64,
    "depth": 4,
    "fixed_triple_samples_per_layer": 512,
    "uniform_rescue": 0.05,
    "bridge_weight_scale": "sqrt(2/width)",
    "quadratic_211_coefficient": "1/(4*pi)",
    "gate": {
        "maximum_balanced_over_iid_mse_ratio": 0.75,
        "upper90_balanced_over_iid": 0.90,
        "no_adverse_width_trend": True,
        "protected_total_billion_lt": 100.0,
    },
}


def _quadratic_defect(bridge: np.ndarray) -> np.ndarray:
    """The inherited M133 quadratic-jet coefficient, with collision ownership."""

    width = bridge.shape[0]
    answer = np.zeros((width, width, width), dtype=np.float64)
    coefficient = 1.0 / (4.0 * math.pi)
    for repeated in range(width):
        for left in range(width):
            for right in range(left + 1, width):
                if len({repeated, left, right}) != 3:
                    continue
                value = coefficient * (
                    bridge[repeated, left] * bridge[repeated, right]
                    + bridge[repeated, left] * bridge[left, right]
                    + bridge[repeated, right] * bridge[left, right]
                )
                answer[repeated, left, right] = value
                answer[repeated, right, left] = value
    return answer


def exact_vectorized_repeated_211(defect: np.ndarray, weight: np.ndarray) -> dict[str, np.ndarray]:
    """Small-width exact oracle; algebraically matches twelve-slot ownership.

    The singleton pair appears twice in the ordered tensor.  The coefficients
    below are therefore 3, 3, 1, and 4 rather than the canonical j<k values
    6, 3+3, 2, and 4+4.  This is an oracle only, never a target-width path.
    """

    aaab = 3.0 * np.einsum("ijk,ia,ja,ka,ib->ab", defect, weight, weight, weight, weight, optimize=True)
    aaab += 3.0 * np.einsum("ijk,ia,ia,ka,jb->ab", defect, weight, weight, weight, weight, optimize=True)
    repeated = np.einsum("ijk,ia,ia,jb,kb->ab", defect, weight, weight, weight, weight, optimize=True)
    split = 4.0 * np.einsum("ijk,ia,ja,ib,kb->ab", defect, weight, weight, weight, weight, optimize=True)
    aabb = repeated + repeated.T + split
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def _dual_table(k4: dict[str, np.ndarray]) -> dict[str, Dual]:
    width = k4["k4_aaaa"].size
    zero_vector = np.zeros(width, dtype=np.float64)
    zero_matrix = np.zeros((width, width), dtype=np.float64)
    return {
        "k3_aaa": Dual(zero_vector, zero_vector),
        "k3_aab": Dual(zero_matrix, zero_matrix),
        "k4_aaaa": Dual(k4["k4_aaaa"], zero_vector),
        "k4_aaab": Dual(k4["k4_aaab"], zero_matrix),
        "k4_aabb": Dual(k4["k4_aabb"], zero_matrix),
    }


def build_generated_chain(width: int, depth: int, seed: int):
    """A well-conditioned fresh chain with complete Gaussian local Jacobians."""

    rng = np.random.default_rng(seed)
    factor = np.eye(width) + 0.025 * rng.normal(size=(width, width))
    covariance = factor @ factor.T + 0.45 * np.eye(width)
    mean = rng.normal(scale=0.16, size=width) * np.sqrt(np.diag(covariance))
    weights = [
        rng.normal(scale=math.sqrt(2.0 / width), size=(width, width))
        for _ in range(depth)
    ]
    states = [(mean, covariance)]
    for weight in weights:
        activation_mean, activation_covariance = analytic_relu_gaussian_moments(
            states[-1][0], states[-1][1]
        )
        next_mean = activation_mean @ weight
        next_covariance = weight.T @ activation_covariance @ weight
        next_covariance = 0.5 * (next_covariance + next_covariance.T)
        states.append((next_mean, next_covariance))
    jacobians = []
    for local_mean, local_covariance in states[1:]:
        kernels = analytic_local_kernels(local_mean, local_covariance)
        jacobians.append(
            LocalReluJacobian(
                kernels.probability,
                kernels.mean_variance_derivative,
                kernels.price_kernel,
                kernels.h_mu,
                kernels.h_variance,
            )
        )
    # The input bridge is the post-ReLU Gaussian correlation in M133's exact
    # proposal.  Construct it directly from the same valid local Gaussian
    # state rather than using a free synthetic bridge matrix.
    bridges = []
    for local_mean, local_covariance in states[:-1]:
        _, activation_covariance = analytic_relu_gaussian_moments(
            local_mean, local_covariance
        )
        scale = np.sqrt(np.diag(activation_covariance))
        bridge = activation_covariance / np.outer(scale, scale)
        bridge = 0.5 * (bridge + bridge.T)
        np.fill_diagonal(bridge, 1.0)
        bridges.append(bridge)
    return states, weights, jacobians, bridges


def _coalesced_response(
    sources: list[TangentState], weights: list[np.ndarray], jacobians: list[LocalReluJacobian]
) -> TangentState:
    """M125b recurrence; every source's covariance influences later means."""

    state = sources[0]
    for index in range(1, len(sources)):
        propagated = tangent_stage(state, weights[index], jacobians[index])
        state = TangentState(
            propagated.mean + sources[index].mean,
            propagated.covariance + sources[index].covariance,
        )
    return state


def _final_response(
    tables: list[dict[str, np.ndarray]], states, weights, jacobians
) -> np.ndarray:
    sources = [
        one_delay_edgeworth_source(_dual_table(table), states[index + 1][0], states[index + 1][1])
        for index, table in enumerate(tables)
    ]
    return _coalesced_response(sources, weights, jacobians).mean


def _sample_tables(
    method: str,
    proposals,
    defects,
    weights,
    rng: np.random.Generator,
    count: int,
) -> list[dict[str, np.ndarray]]:
    tables = []
    for proposal, defect, weight in zip(proposals, defects, weights):
        if method == "iid":
            draws = proposal.sample(rng, count)
        elif method == "balanced":
            draws = balanced_factored_draws(proposal, rng, count)
        else:
            raise ValueError("unknown sampling method")
        tables.append(
            collision211_hh_batched(
                weight, proposal, draws, lambda i, j, k: float(defect[i, j, k])
            )
        )
    return tables


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p90": float(np.quantile(values, 0.90)),
        "maximum": float(np.max(values)),
    }


def evaluate_cell(width: int, seed: int, repetitions: int) -> dict[str, object]:
    states, weights, jacobians, bridges = build_generated_chain(width, CONFIG["depth"], seed)
    defects = [_quadratic_defect(bridge) for bridge in bridges]
    proposals = [
        collision211_factored_proposal(
            bridge, weight, uniform_mixture=CONFIG["uniform_rescue"]
        )
        for bridge, weight in zip(bridges, weights)
    ]
    exact_tables = [
        exact_vectorized_repeated_211(defect, weight)
        for defect, weight in zip(defects, weights)
    ]
    exact_response = _final_response(exact_tables, states, weights, jacobians)
    response_energy = max(float(np.mean(exact_response * exact_response)), 1.0e-30)
    iid_errors, balanced_errors, ratios = [], [], []
    for repetition in range(repetitions):
        # Independent randomisations make this conservative: no favorable
        # common-random cancellation is used in the primary MSE ratio.
        iid_rng = np.random.default_rng(seed + 10_000_003 + 97_409 * repetition)
        balanced_rng = np.random.default_rng(seed + 20_000_003 + 97_409 * repetition)
        iid_response = _final_response(
            _sample_tables("iid", proposals, defects, weights, iid_rng, CONFIG["fixed_triple_samples_per_layer"]),
            states, weights, jacobians,
        )
        balanced_response = _final_response(
            _sample_tables("balanced", proposals, defects, weights, balanced_rng, CONFIG["fixed_triple_samples_per_layer"]),
            states, weights, jacobians,
        )
        iid_error = float(np.mean((iid_response - exact_response) ** 2)) / response_energy
        balanced_error = float(np.mean((balanced_response - exact_response) ** 2)) / response_energy
        iid_errors.append(iid_error)
        balanced_errors.append(balanced_error)
        ratios.append(balanced_error / iid_error if iid_error > 0.0 else math.inf)
    iid = np.asarray(iid_errors)
    balanced = np.asarray(balanced_errors)
    return {
        "width": width,
        "seed": seed,
        "repetitions": repetitions,
        "response_energy": response_energy,
        "iid_output_mse": _summary(iid),
        "balanced_output_mse": _summary(balanced),
        "balanced_over_iid_ratio_of_mean_mse": float(np.mean(balanced) / np.mean(iid)),
        "paired_ratio_distribution": _summary(np.asarray(ratios)),
        "all_sources_complete_m121_m125b": True,
        "source_only_211_component": True,
    }


def evaluate_split(name: str, seeds: list[int], repetitions: int) -> dict[str, object]:
    cells = [evaluate_cell(width, seed, repetitions) for width in CONFIG["widths"] for seed in seeds]
    by_width = {}
    for width in CONFIG["widths"]:
        entries = [item for item in cells if item["width"] == width]
        iid = np.mean([item["iid_output_mse"]["mean"] for item in entries])
        balanced = np.mean([item["balanced_output_mse"]["mean"] for item in entries])
        ratios = np.asarray([item["balanced_over_iid_ratio_of_mean_mse"] for item in entries])
        by_width[str(width)] = {
            "mean_iid_output_mse": float(iid),
            "mean_balanced_output_mse": float(balanced),
            "balanced_over_iid_ratio": float(balanced / iid),
            "seedwise_ratio": _summary(ratios),
        }
    all_iid = np.asarray([item["iid_output_mse"]["mean"] for item in cells])
    all_balanced = np.asarray([item["balanced_output_mse"]["mean"] for item in cells])
    seedwise = np.asarray([item["balanced_over_iid_ratio_of_mean_mse"] for item in cells])
    width_ratio = [by_width[str(width)]["balanced_over_iid_ratio"] for width in CONFIG["widths"]]
    return {
        "split": name,
        "cells": cells,
        "by_width": by_width,
        "pooled": {
            "balanced_over_iid_ratio": float(np.mean(all_balanced) / np.mean(all_iid)),
            "seedwise_ratio": _summary(seedwise),
            "nonincreasing_with_width": bool(
                all(width_ratio[index + 1] <= width_ratio[index] + 1e-12 for index in range(len(width_ratio) - 1))
            ),
        },
    }


def run() -> dict[str, object]:
    development = evaluate_split("development", CONFIG["development_seeds"], CONFIG["development_replicates"])
    confirmation = evaluate_split("confirmation", CONFIG["confirmation_seeds"], CONFIG["confirmation_replicates"])
    bill = balanced_sampling_bill(count=CONFIG["fixed_triple_samples_per_layer"])
    # M133's conservative complete first-order kappa=2 sheet was 94.94094024B
    # (including coefficient/residual reserves).  The new operator changes no
    # five-product contraction and is charged only by this separate bill.
    protected_total_billion = 94.94094024 + bill["protected_increment"] / 1.0e9
    gate = CONFIG["gate"]
    dev = development["pooled"]
    confirmed = confirmation["pooled"]
    passed = (
        dev["balanced_over_iid_ratio"] <= gate["maximum_balanced_over_iid_mse_ratio"]
        and dev["seedwise_ratio"]["p90"] < gate["upper90_balanced_over_iid"]
        and dev["nonincreasing_with_width"]
        and confirmed["balanced_over_iid_ratio"] <= gate["maximum_balanced_over_iid_mse_ratio"]
        and confirmed["seedwise_ratio"]["p90"] < gate["upper90_balanced_over_iid"]
        and confirmed["nonincreasing_with_width"]
        and protected_total_billion < gate["protected_total_billion_lt"]
    )
    return {
        "contract": {
            "generated_only": True,
            "contest_data_accessed": False,
            "complete_m121_one_delay": True,
            "complete_m125b_coalescing": True,
            "same_five_product_211_contraction": True,
            "same_factored_proposal_and_5pct_rescue": True,
            "no_full_triple_catalog": True,
        },
        "config": CONFIG,
        "development": development,
        "confirmation": confirmation,
        "static_cost": {
            "balance_increment": bill,
            "inherited_m133_kappa2_complete_protected_total_billion": 94.94094024,
            "balanced_kappa2_complete_protected_total_billion": protected_total_billion,
        },
        "gate": {"passed": passed, "promotion": "closed unless every prespecified condition passes"},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
