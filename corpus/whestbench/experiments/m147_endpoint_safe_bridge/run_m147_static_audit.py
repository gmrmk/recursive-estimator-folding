"""Print the frozen response-free M147 static audit as JSON."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import time

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m122_nonzero_bridge_theory", ROOT / "m129_source_frechet_tangent"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m129_source_frechet import (  # noqa: E402
    build_state_frechet,
    exact_collision_cumulant_dot,
    pair_raw_moment_series_dot,
)
from m147_endpoint_safe_bridge import (  # noqa: E402
    EndpointCertificationFailure,
    bivariate_relu_raw_dot_endpoint,
    build_endpoint_state_frechet,
    collision211_local_state_dot,
    conditional_collision211_endpoint_dot,
)


def pair_state(alpha, sigma, rho, alpha_dot, sigma_dot, rho_dot):
    mean = alpha * sigma
    mean_dot = alpha_dot * sigma + alpha * sigma_dot
    covariance = np.array(
        [[sigma[0] ** 2, rho * np.prod(sigma)], [rho * np.prod(sigma), sigma[1] ** 2]]
    )
    covariance_dot = np.diag(2.0 * sigma * sigma_dot)
    covariance_dot[0, 1] = covariance_dot[1, 0] = (
        rho_dot * np.prod(sigma)
        + rho * (sigma_dot[0] * sigma[1] + sigma[0] * sigma_dot[1])
    )
    return mean, covariance, mean_dot, covariance_dot


def main() -> None:
    alpha = np.array([-0.37, 0.62])
    sigma = np.array([0.9, 1.3])
    alpha_dot = np.array([0.04, -0.03])
    sigma_dot = np.array([0.02, -0.01])
    maximum_pair_value_defect = 0.0
    maximum_pair_tangent_defect = 0.0
    for rho in (-0.75, -0.35, 0.0, 0.35, 0.75):
        state = pair_state(alpha, sigma, rho, alpha_dot, sigma_dot, 0.015)
        observed = bivariate_relu_raw_dot_endpoint(*state)
        expected = pair_raw_moment_series_dot(
            float(alpha[0]), float(sigma[0]), 1,
            float(alpha[1]), float(sigma[1]), 1,
            rho,
            float(alpha_dot[0]), float(sigma_dot[0]),
            float(alpha_dot[1]), float(sigma_dot[1]),
            0.015,
            terms=96,
        )
        maximum_pair_value_defect = max(maximum_pair_value_defect, abs(observed.raw - expected[0]))
        maximum_pair_tangent_defect = max(maximum_pair_tangent_defect, abs(observed.tangent - expected[1]))

    mean = np.array([0.2, -0.1, 0.35])
    moderate_correlation = np.array(
        [[1.0, 0.35, -0.2], [0.35, 1.0, 0.25], [-0.2, 0.25, 1.0]]
    )
    scales = np.array([1.1, 0.8, 1.3])
    moderate_covariance = moderate_correlation * np.outer(scales, scales)
    mean_dot = np.array([0.03, -0.02, 0.01])
    covariance_dot = np.array(
        [[0.02, 0.003, -0.002], [0.003, -0.01, 0.004], [-0.002, 0.004, 0.015]]
    )
    new_state = build_endpoint_state_frechet(mean, moderate_covariance, mean_dot, covariance_dot)
    old_state = build_state_frechet(mean, moderate_covariance, mean_dot, covariance_dot)
    moderate = conditional_collision211_endpoint_dot(new_state, 0, 1, 2)
    old_cumulant = exact_collision_cumulant_dot(old_state, (0, 0, 1, 2), terms=32)

    high_correlation = np.array(
        [[1.0, 0.93, 0.89], [0.93, 1.0, 0.91], [0.89, 0.91, 1.0]]
    )
    high_covariance = high_correlation * np.outer(scales, scales)
    high_state = build_endpoint_state_frechet(mean, high_covariance, mean_dot, covariance_dot)
    start = time.perf_counter()
    high = conditional_collision211_endpoint_dot(high_state, 0, 1, 2)
    high_wall = time.perf_counter() - start

    endpoint_covariance = np.array(
        [[1.0, 0.5, 0.5], [0.5, 1.0, 0.99925], [0.5, 0.99925, 1.0]]
    )
    endpoint_mean = np.array([0.1, -0.2, 0.3])
    endpoint_mean_dot = np.array([0.01, -0.02, 0.015])
    endpoint_covariance_dot = np.array(
        [[0.01, 0.002, -0.001], [0.002, -0.005, 0.001], [-0.001, 0.001, 0.008]]
    )
    endpoint_state = build_endpoint_state_frechet(
        endpoint_mean, endpoint_covariance, endpoint_mean_dot, endpoint_covariance_dot
    )
    start = time.perf_counter()
    endpoint = conditional_collision211_endpoint_dot(endpoint_state, 0, 1, 2)
    endpoint_wall = time.perf_counter() - start

    degenerate_conditional_refusals = 0
    for local_covariance in (
        np.ones((3, 3)),
        np.array([[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    ):
        try:
            collision211_local_state_dot(
                np.array([0.1, 0.2, 0.3]),
                local_covariance,
                np.zeros(3),
                np.zeros((3, 3)),
            )
        except EndpointCertificationFailure as error:
            if "degenerate conditional singleton" not in str(error):
                raise
            degenerate_conditional_refusals += 1
    if degenerate_conditional_refusals != 2:
        raise RuntimeError("M147 degenerate conditional preflight did not fail closed")

    extreme_finite_refusals = 0
    for extreme_mean, extreme_rho in (
        (np.array([1.0e308, 1.0e308]), 1.0),
        (np.array([1.0e200, 1.0e200]), -1.0),
    ):
        try:
            bivariate_relu_raw_dot_endpoint(
                extreme_mean,
                np.array([[1.0, extreme_rho], [extreme_rho, 1.0]]),
                np.zeros(2),
                np.zeros((2, 2)),
            )
        except EndpointCertificationFailure:
            extreme_finite_refusals += 1
    if extreme_finite_refusals != 2:
        raise RuntimeError("M147 extreme finite arithmetic did not fail closed")

    coefficients = 31 * 512
    reserve = 1_625_292_800
    per_coefficient_reserve = reserve // coefficients
    # A deliberately favorable lower bound: sin/cos geometry is assumed
    # precomputed, leaving only two products, one add, exp, and final product.
    # Float64 doubles all five operations under the stated scorer.
    minimum_billed_per_angle_evaluation = 10

    result = {
        "scope": "response-free generated mathematics only",
        "legacy_pair_grid": {
            "rho": [-0.75, -0.35, 0.0, 0.35, 0.75],
            "max_absolute_value_defect": maximum_pair_value_defect,
            "max_absolute_tangent_defect": maximum_pair_tangent_defect,
        },
        "moderate_211_partition_agreement": {
            "absolute_cumulant_defect": abs(moderate.cumulant - old_cumulant[0]),
            "absolute_tangent_defect": abs(moderate.cumulant_tangent - old_cumulant[1]),
            "paired_value_disagreement": moderate.value_disagreement,
            "paired_tangent_disagreement": moderate.tangent_disagreement,
        },
        "high_correlation_static": {
            "maximum_input_correlation": float(np.max(np.abs(high_correlation - np.eye(3)))),
            "angular_integrand_evaluations": high.quadrant_integrand_evaluations,
            "local_scalar_wall_seconds_nonportable": high_wall,
        },
        "conditional_endpoint_adversary": {
            "conditional_singleton_correlation": 0.999,
            "angular_integrand_evaluations": endpoint.quadrant_integrand_evaluations,
            "paired_value_disagreement": endpoint.value_disagreement,
            "paired_tangent_disagreement": endpoint.tangent_disagreement,
            "local_scalar_wall_seconds_nonportable": endpoint_wall,
        },
        "repair_guards": {
            "degenerate_conditional_refusals": degenerate_conditional_refusals,
            "extreme_finite_refusals": extreme_finite_refusals,
            "conditional_support": "strictly positive Schur diagonal for both singleton variables",
            "nonfinite_output_refused": True,
        },
        "frozen_target_cost_boundary": {
            "layers": 31,
            "sampled_coefficients_per_layer": 512,
            "coefficient_count": coefficients,
            "exact_coefficient_reserve": reserve,
            "reserve_per_coefficient": per_coefficient_reserve,
            "favorable_minimum_billed_ops_per_angle_evaluation": minimum_billed_per_angle_evaluation,
            "high_correlation_lower_bound_per_coefficient": high.quadrant_integrand_evaluations * minimum_billed_per_angle_evaluation,
            "conditional_endpoint_lower_bound_per_coefficient": endpoint.quadrant_integrand_evaluations * minimum_billed_per_angle_evaluation,
            "literal_48_64_x_16_32_rule_passes_reserve": False,
        },
        "disposition": {
            "pair_bridge": "static survivor",
            "central_211_oracle": "correctness survivor; literal target implementation cost-killed",
            "generated_response_authorized": False,
            "target_or_contest_execution_authorized": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
