"""Frozen generated-only M121/M125b response audit for M139.

The exact M131 conditional-boundary oracle constructs every small-width
``[2,1,1]`` coefficient once.  M133 and M139 then estimate precisely that same
component at equal fixed K.  All other source families are zero in this
experiment, so the final M125b response error is exactly the contribution of
the proposal mutation rather than an entrywise proxy.

No challenge, scorer, target, leaderboard, submission, or champion artifact
is accessed by this script.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m120_price_normal_ordered_adjoint",
    "m125_source_batched_forward_tangent",
    "m126_repeated_output_source_contraction",
    "m129_source_frechet_tangent",
    "m131_trivariate_boundary_stream",
    "m133_ht_hidden_edge",
    "m139_trivariate_proposal",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m120c_analytic_dense_reference import analytic_local_kernels, analytic_relu_gaussian_moments  # noqa: E402
from m125_forward_tangent import LocalReluJacobian, TangentState, tangent_stage  # noqa: E402
from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m129_source_frechet import Dual, build_state_frechet  # noqa: E402
from m131_trivariate_boundary_stream import conditional_collision211_defect_dot, one_delay_edgeworth_source  # noqa: E402
from m133_ht_hidden_edge import collision211_factored_proposal, collision211_hh_batched  # noqa: E402
from m139_trivariate_proposal import make_positive_partial_proposal  # noqa: E402


# This is frozen before any result is read.  The confirmation seeds share no
# generated state, coefficient table, or sampling stream with development.
CONFIG = {
    "contract": "generated-only exact-[211]-component M121/M125b response variance",
    "depth": 3,
    "k_rule": "2*width (the M133 kappa=2 analogue)",
    "repetitions": 48,
    "development": {"widths": [5, 6], "seeds": [139701, 139702]},
    "confirmation": {"widths": [7, 8], "seeds": [139811]},
    "m139": {
        "rank": 4,
        "uniform_mixture": 0.05,
        "partial_ridge": 2.0**-12,
        "partial_cap": 8.0,
        "latent_strength": 0.70,
    },
    "promotion": {
        "pooled_output_mse_ratio_max": 0.75,
        "bootstrap_upper90_max": 0.90,
        "no_adverse_width_trend": "largest-width mean ratio <= smallest-width mean ratio",
    },
}


def build_generated_chain(width: int, depth: int, seed: int):
    """A small, comfortably nonsingular Gaussian/ReLU chain."""

    rng = np.random.default_rng(seed)
    factor = np.eye(width) + 0.020 * rng.normal(size=(width, width))
    covariance = factor @ factor.T + 0.45 * np.eye(width)
    sigma = np.sqrt(np.diag(covariance))
    mean = rng.normal(scale=0.16, size=width) * sigma
    # Dense iid affine maps can drive the small Hermite certification oracle
    # through its deliberately fail-closed correlation endpoint.  This audit
    # uses a nontrivial but diagonally dominant generated chain, retaining
    # nonzero bridge paths while keeping every independently certified source
    # comfortably inside that oracle's declared domain.
    weights = [
        0.82 * np.eye(width) + rng.normal(scale=0.035, size=(width, width))
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
    for next_mean, next_covariance in states[1:]:
        kernel = analytic_local_kernels(next_mean, next_covariance)
        jacobians.append(
            LocalReluJacobian(
                kernel.probability,
                kernel.mean_variance_derivative,
                kernel.price_kernel,
                kernel.h_mu,
                kernel.h_variance,
            )
        )
    return states, weights, jacobians


def _add(left: TangentState, right: TangentState) -> TangentState:
    return TangentState(left.mean + right.mean, left.covariance + right.covariance)


def coalesced_response(sources: list[TangentState], weights: list[np.ndarray], jacobians: list[LocalReluJacobian]) -> TangentState:
    response = sources[0]
    for index in range(1, len(sources)):
        response = tangent_stage(response, weights[index], jacobians[index])
        response = _add(response, sources[index])
    return response


def zero_repeated(k4: dict[str, np.ndarray]) -> dict[str, Dual]:
    n = k4["k4_aaaa"].size
    zero_vector = np.zeros(n)
    zero_matrix = np.zeros((n, n))
    return {
        "k3_aaa": Dual(zero_vector.copy(), zero_vector.copy()),
        "k3_aab": Dual(zero_matrix.copy(), zero_matrix.copy()),
        "k4_aaaa": Dual(k4["k4_aaaa"], zero_vector.copy()),
        "k4_aaab": Dual(k4["k4_aaab"], zero_matrix.copy()),
        "k4_aabb": Dual(k4["k4_aabb"], zero_matrix.copy()),
    }


def exact_defect_table(tangent) -> np.ndarray:
    n = tangent.state.mean.size
    answer = np.zeros((n, n, n), dtype=np.float64)
    for repeated in range(n):
        for left in range(n):
            for right in range(left + 1, n):
                if len({repeated, left, right}) != 3:
                    continue
                value, _, certificate = conditional_collision211_defect_dot(
                    tangent, repeated, left, right, coarse_order=32, fine_order=48, series_terms=24
                )
                if certificate.value_disagreement > 4e-5:
                    raise ArithmeticError("M131 paired quadrature did not certify this generated coefficient")
                answer[repeated, left, right] = value
                answer[repeated, right, left] = value
    return answer


def build_cell(width: int, seed: int):
    states, weights, jacobians = build_generated_chain(width, CONFIG["depth"], seed)
    local: list[dict[str, object]] = []
    exact_sources: list[TangentState] = []
    for layer, weight in enumerate(weights):
        mean, covariance = states[layer]
        tangent = build_state_frechet(mean, covariance, np.zeros(width), np.zeros((width, width)))
        defect = exact_defect_table(tangent)
        exact_k4 = collision211_repeated_exact(defect, weight)
        exact_sources.append(one_delay_edgeworth_source(zero_repeated(exact_k4), states[layer + 1][0], states[layer + 1][1]))
        old = collision211_factored_proposal(tangent.state.bridge, weight, uniform_mixture=0.05)
        new = make_positive_partial_proposal(
            tangent.state.bridge,
            weight,
            tangent.state.alpha,
            tangent.state.relu_scale,
            **CONFIG["m139"],
        )
        local.append({"weight": weight, "defect": defect, "old": old, "new": new, "rank_used": new.rank_used})
    exact = coalesced_response(exact_sources, weights, jacobians).mean
    return states, weights, jacobians, local, exact


def sample_cell(cell, repetition: int, method: str) -> np.ndarray:
    _states, weights, jacobians, local, _exact = cell
    n = weights[0].shape[0]
    k = 2 * n
    source_list: list[TangentState] = []
    for layer, item in enumerate(local):
        # Streams are paired by layer/repetition but each sampler applies its
        # own inverse probability.  No result-dependent adaptation occurs.
        rng = np.random.default_rng(139900000 + 10007 * repetition + 101 * layer)
        proposal = item[method]
        draws = proposal.sample(rng, k)
        defect = item["defect"]
        estimated = collision211_hh_batched(
            item["weight"], proposal, draws, lambda i, j, k_: float(defect[i, j, k_])
        )
        source_list.append(one_delay_edgeworth_source(zero_repeated(estimated), _states[layer + 1][0], _states[layer + 1][1]))
    return coalesced_response(source_list, weights, jacobians).mean


def _bootstrap_upper90(old_error: np.ndarray, new_error: np.ndarray, seed: int) -> float:
    """One-sided 90% bootstrap for a fixed equal-K output-MSE ratio."""

    rng = np.random.default_rng(seed)
    ratios = []
    count = old_error.size
    for _ in range(4000):
        choice = rng.integers(0, count, size=count)
        denominator = float(np.mean(old_error[choice]))
        ratios.append(float(np.mean(new_error[choice])) / denominator)
    return float(np.quantile(ratios, 0.90))


def run_split(name: str, widths: list[int], seeds: list[int], repetitions: int) -> dict[str, object]:
    cells: list[dict[str, object]] = []
    all_old: list[float] = []
    all_new: list[float] = []
    for width in widths:
        for seed in seeds:
            cell = build_cell(width, seed)
            exact = cell[-1]
            old = np.asarray([sample_cell(cell, repetition, "old") for repetition in range(repetitions)])
            new = np.asarray([sample_cell(cell, repetition, "new") for repetition in range(repetitions)])
            old_error = np.mean((old - exact[None, :]) ** 2, axis=1)
            new_error = np.mean((new - exact[None, :]) ** 2, axis=1)
            all_old.extend(old_error.tolist())
            all_new.extend(new_error.tolist())
            cells.append(
                {
                    "width": width,
                    "seed": seed,
                    "k_per_layer": 2 * width,
                    "output_mse_m133": float(np.mean(old_error)),
                    "output_mse_m139": float(np.mean(new_error)),
                    "ratio": float(np.mean(new_error) / np.mean(old_error)),
                    "upper90_ratio": _bootstrap_upper90(old_error, new_error, seed + 77),
                    "rank_used_by_layer": [int(item["rank_used"]) for item in cell[3]],
                    "exact_oracle": "M131 conditional 32/48 paired rule; all triples at each local source",
                    "complete_m121_one_delay": True,
                    "complete_m125b_coalescing": True,
                }
            )
    old_array = np.asarray(all_old)
    new_array = np.asarray(all_new)
    by_width = {
        width: float(np.mean([cell["ratio"] for cell in cells if cell["width"] == width]))
        for width in widths
    }
    upper90 = _bootstrap_upper90(old_array, new_array, 139990000 + len(widths))
    return {
        "name": name,
        "cells": cells,
        "pooled_output_mse_ratio": float(np.mean(new_array) / np.mean(old_array)),
        "bootstrap_upper90_ratio": upper90,
        "ratio_by_width": by_width,
        "no_adverse_width_trend": by_width[max(widths)] <= by_width[min(widths)],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=CONFIG["repetitions"])
    parser.add_argument("--split", choices=("development", "confirmation", "both"), default="both")
    args = parser.parse_args()
    result: dict[str, object] = {"config": CONFIG, "contest_data_accessed": False}
    if args.split in ("development", "both"):
        spec = CONFIG["development"]
        result["development"] = run_split("development", spec["widths"], spec["seeds"], args.repetitions)
    if args.split in ("confirmation", "both"):
        spec = CONFIG["confirmation"]
        result["confirmation"] = run_split("confirmation", spec["widths"], spec["seeds"], args.repetitions)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
