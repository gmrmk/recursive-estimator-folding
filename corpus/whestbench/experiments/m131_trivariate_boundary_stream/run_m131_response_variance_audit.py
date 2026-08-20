"""Generated-only M131 complete first-order response variance audit.

The audit builds a fresh Gaussian-input ReLU chain, never opens a benchmark,
and compares:

* iid antithetic normal ordering;
* its exact first-Wiener-chaos common-random control;
* Gaussianized Haar-frame and regular-simplex banks; and
* direct input sampling at matched leading rectangular-matmul work.

Every analytic method constructs all local projected repeated k3/k4 tables,
performs the complete one-delay M121 conversion, and coalesces all sources by
the M125b inhomogeneous recurrence.  The comparison therefore happens at the
final mean response, not at source-table Frobenius norm.
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
    "m122_nonzero_bridge_theory",
    "m125_source_batched_forward_tangent",
    "m129_source_frechet_tangent",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m120c_analytic_dense_reference import (  # noqa: E402
    analytic_local_kernels,
    analytic_relu_gaussian_moments,
)
from m125_forward_tangent import (  # noqa: E402
    LocalReluJacobian,
    TangentState,
    tangent_stage,
)
from m131_trivariate_boundary_stream import (  # noqa: E402
    antithetic_standard_samples,
    build_zero_sampling_frechet,
    gaussianized_frame_samples,
    one_delay_edgeworth_source,
    sampled_first_chaos_controlled_source,
    sampled_normal_ordered_source,
    sampled_source_cost_envelope,
)


def build_generated_chain(width: int, depth: int, seed: int):
    rng = np.random.default_rng(seed)
    factor = np.eye(width) + 0.035 * rng.normal(size=(width, width))
    covariance = factor @ factor.T + 0.30 * np.eye(width)
    sigma = np.sqrt(np.diag(covariance))
    mean = rng.normal(scale=0.22, size=width) * sigma
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
    local_frechet = [
        build_zero_sampling_frechet(state_mean, state_covariance)
        for state_mean, state_covariance in states[:-1]
    ]
    jacobians = []
    for state_mean, state_covariance in states[1:]:
        kernels = analytic_local_kernels(state_mean, state_covariance)
        jacobians.append(
            LocalReluJacobian(
                kernels.probability,
                kernels.mean_variance_derivative,
                kernels.price_kernel,
                kernels.h_mu,
                kernels.h_variance,
            )
        )
    gaussian_final_mean = analytic_relu_gaussian_moments(
        states[-1][0], states[-1][1]
    )[0]
    return states, weights, local_frechet, jacobians, gaussian_final_mean


def _add(left: TangentState, right: TangentState) -> TangentState:
    return TangentState(
        left.mean + right.mean,
        left.covariance + right.covariance,
    )


def coalesced_response(
    local_sources: list[TangentState],
    weights: list[np.ndarray],
    jacobians: list[LocalReluJacobian],
) -> TangentState:
    response = local_sources[0]
    for index in range(1, len(local_sources)):
        response = tangent_stage(response, weights[index], jacobians[index])
        response = _add(response, local_sources[index])
    return response


def _reused_frame_directions(
    width: int, bank_count: int, seed: int, design: str
) -> list[np.ndarray]:
    samples = gaussianized_frame_samples(width, bank_count, seed, design=design)
    rows = width if design == "orthobasis" else width + 1
    answer = []
    for bank in range(bank_count):
        block = samples[bank * rows : (bank + 1) * rows]
        answer.append(block / np.linalg.norm(block, axis=1)[:, None])
    return answer


def _fresh_radii_on_directions(
    directions: list[np.ndarray], width: int, seed: int
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    banks = []
    for bank in directions:
        permutation = rng.permutation(bank.shape[0])
        radii = np.sqrt(rng.chisquare(width, size=bank.shape[0]))
        banks.append(radii[:, None] * bank[permutation])
    return np.concatenate(banks, axis=0)


def evaluate_analytic_method(
    method: str,
    repetition: int,
    states,
    weights,
    local_frechet,
    jacobians,
    width: int,
) -> np.ndarray:
    controlled = method.startswith("controlled")
    local_sources = []
    reused = None
    if "reused_frame" in method:
        design = "simplex" if "simplex" in method else "orthobasis"
        reused = _reused_frame_directions(
            width, 2, 131_900_000 + repetition, design
        )
    for layer in range(len(weights)):
        key = 131_000_000 + 100_003 * repetition + 1009 * layer
        if "iid_s2n" in method:
            samples = antithetic_standard_samples(width, width, 2, key)
        elif "iid" in method:
            samples = antithetic_standard_samples(width // 2, width, 2, key)
        elif "antithetic_frame" in method:
            samples = gaussianized_frame_samples(
                width, 2, key, design="orthobasis", antithetic=True
            )
        elif reused is not None:
            samples = _fresh_radii_on_directions(reused, width, key)
        elif "simplex" in method:
            samples = gaussianized_frame_samples(width, 2, key, design="simplex")
        else:
            samples = gaussianized_frame_samples(width, 2, key, design="orthobasis")
        if controlled:
            source = sampled_first_chaos_controlled_source(
                local_frechet[layer], weights[layer], samples, bank_count=2
            ).controlled
        else:
            source = sampled_normal_ordered_source(
                local_frechet[layer], weights[layer], samples, bank_count=2
            )
        local_sources.append(
            one_delay_edgeworth_source(
                source.repeated,
                states[layer + 1][0],
                states[layer + 1][1],
            )
        )
    return coalesced_response(local_sources, weights, jacobians).mean


def direct_network_samples(
    count: int,
    repetition: int,
    initial_mean: np.ndarray,
    initial_covariance: np.ndarray,
    weights: list[np.ndarray],
) -> np.ndarray:
    width = initial_mean.size
    if count % 2:
        raise ValueError("direct antithetic count must be even")
    standard = antithetic_standard_samples(
        count // 2, width, 1, 132_000_000 + repetition
    )
    factor = np.linalg.cholesky(initial_covariance)
    value = initial_mean[None, :] + standard @ factor.T
    for weight in weights:
        value = np.maximum(value, 0.0) @ weight
    return np.mean(np.maximum(value, 0.0), axis=0)


def direct_truth(
    count: int,
    initial_mean: np.ndarray,
    initial_covariance: np.ndarray,
    weights: list[np.ndarray],
    seed: int,
) -> np.ndarray:
    width = initial_mean.size
    factor = np.linalg.cholesky(initial_covariance)
    rng = np.random.default_rng(seed)
    total = np.zeros(width)
    done = 0
    chunk = 20_000
    while done < count:
        half = min(chunk // 2, (count - done) // 2)
        positive = rng.standard_normal((half, width))
        standard = np.concatenate((positive, -positive), axis=0)
        value = initial_mean[None, :] + standard @ factor.T
        for weight in weights:
            value = np.maximum(value, 0.0) @ weight
        total += np.sum(np.maximum(value, 0.0), axis=0)
        done += 2 * half
    return total / done


def summarize(samples: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    mean = np.mean(samples, axis=0)
    centered = samples - mean[None, :]
    bias = mean - truth
    return {
        "per_output_mse": float(np.mean((samples - truth[None, :]) ** 2)),
        "per_output_variance": float(
            np.sum(centered * centered) / ((samples.shape[0] - 1) * samples.shape[1])
        ),
        "per_output_squared_bias": float(np.mean(bias * bias)),
        "mean_norm": float(np.linalg.norm(mean)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--repetitions", type=int, default=80)
    parser.add_argument("--truth-samples", type=int, default=400_000)
    args = parser.parse_args()
    if args.width % 2 or args.truth_samples % 2:
        raise ValueError("width and truth sample count must be even")
    states, weights, local_frechet, jacobians, gaussian_base = build_generated_chain(
        args.width, args.depth, 131_701
    )
    truth = direct_truth(
        args.truth_samples, states[0][0], states[0][1], weights, 131_702
    )
    methods = (
        "uncontrolled_iid_s1n",
        "controlled_iid_s1n",
        "uncontrolled_iid_s2n",
        "uncontrolled_antithetic_frame_s2n",
        "controlled_fresh_frame_s1n",
        "controlled_reused_frame_s1n",
        "controlled_fresh_simplex",
        "controlled_reused_frame_simplex",
    )
    observed = {
        method: np.asarray(
            [
                gaussian_base
                + evaluate_analytic_method(
                    method,
                    repetition,
                    states,
                    weights,
                    local_frechet,
                    jacobians,
                    args.width,
                )
                for repetition in range(args.repetitions)
            ]
        )
        for method in methods
    }
    # Twenty-six total-row-equivalent rectangular products is the controlled
    # source's leading per-layer work at two banks; direct MC gets that many
    # independent input paths as a deliberately favorable matched-work arm.
    direct_count = 52 * args.width
    direct = np.asarray(
        [
            direct_network_samples(
                direct_count,
                repetition,
                states[0][0],
                states[0][1],
                weights,
            )
            for repetition in range(args.repetitions)
        ]
    )
    result = {
        "contract": {
            "generated_only": True,
            "width": args.width,
            "depth": args.depth,
            "repetitions": args.repetitions,
            "truth_samples": args.truth_samples,
            "complete_linear_k3_k4_one_delay": True,
            "complete_all_source_m125b_coalescing": True,
            "m128_k3_squared_included": False,
        },
        "truth_mc_standard_error_proxy": float(
            np.sqrt(np.mean(np.var(direct, axis=0, ddof=1)) / args.truth_samples * direct_count)
        ),
        "gaussian_base": {
            "per_output_squared_bias": float(np.mean((gaussian_base - truth) ** 2))
        },
        "methods": {method: summarize(values, truth) for method, values in observed.items()},
        "direct_matched_leading_work": {
            "samples": direct_count,
            **summarize(direct, truth),
        },
        "variance_ratios": {
            "control_same_iid_samples": summarize(
                observed["controlled_iid_s1n"], truth
            )["per_output_variance"]
            / summarize(observed["uncontrolled_iid_s1n"], truth)["per_output_variance"],
            "control_half_iid_samples_vs_uncontrolled_equal_work": summarize(
                observed["controlled_iid_s1n"], truth
            )["per_output_variance"]
            / summarize(observed["uncontrolled_iid_s2n"], truth)["per_output_variance"],
            "fresh_frame_vs_controlled_iid": summarize(
                observed["controlled_fresh_frame_s1n"], truth
            )["per_output_variance"]
            / summarize(observed["controlled_iid_s1n"], truth)["per_output_variance"],
            "fresh_simplex_vs_controlled_iid": summarize(
                observed["controlled_fresh_simplex"], truth
            )["per_output_variance"]
            / summarize(observed["controlled_iid_s1n"], truth)["per_output_variance"],
            "antithetic_frame_vs_equal_sample_iid": summarize(
                observed["uncontrolled_antithetic_frame_s2n"], truth
            )["per_output_variance"]
            / summarize(observed["uncontrolled_iid_s2n"], truth)["per_output_variance"],
        },
        "target_width_costs": {
            "controlled_iid_s256": sampled_source_cost_envelope(
                256, first_chaos_control=True
            )["complete_protected_total"],
            "uncontrolled_iid_s512": sampled_source_cost_envelope(512)[
                "complete_protected_total"
            ],
            "uncontrolled_antithetic_frame_s512": sampled_source_cost_envelope(
                512,
                gaussianized_design="antithetic_orthobasis",
            )["complete_protected_total"],
            "controlled_frame_s256_reused_rotation": sampled_source_cost_envelope(
                256,
                first_chaos_control=True,
                gaussianized_design="orthobasis",
            )["complete_protected_total"],
            "controlled_simplex_s257_reused_rotation": sampled_source_cost_envelope(
                257,
                first_chaos_control=True,
                gaussianized_design="simplex",
            )["complete_protected_total"],
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
