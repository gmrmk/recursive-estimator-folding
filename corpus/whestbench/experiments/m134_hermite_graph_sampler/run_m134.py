"""Reproduce the generated-only M134 audit and write results.json."""

from __future__ import annotations

import json

import numpy as np

from m134_hermite_graph_sampler import (
    cost_envelope,
    equicorrelation_partial_sums,
    exact_joint_response_variance,
    hermite_factors,
    importance_probabilities,
    negative_tree_factors,
)
from m122_nonzero_bridge import build_state


def generated_state(n: int, seed: int, correlation_scale: float):
    rng = np.random.default_rng(seed)
    mean = rng.normal(0.2, 0.12, size=n)
    sigma = rng.uniform(0.7, 1.2, size=n)
    raw = rng.normal(size=(n, n))
    raw = 0.5 * (raw + raw.T)
    np.fill_diagonal(raw, 0.0)
    raw /= max(1.0, np.linalg.norm(raw, 2))
    correlation = np.eye(n) + correlation_scale * raw
    covariance = sigma[:, None] * correlation * sigma[None, :]
    covariance = 0.5 * (covariance + covariance.T)
    return build_state(mean, covariance, pair_terms=64)


def variance_case(seed: int, scale: float) -> dict[str, float | int]:
    state = generated_state(4, seed, scale)
    factors = hermite_factors(state.alpha, state.sigma, state.correlation, 24)
    factors += negative_tree_factors(state)
    probabilities = importance_probabilities(factors)
    rng = np.random.default_rng(seed + 1000)
    weight = rng.normal(scale=0.4, size=(4, 4))
    response31 = rng.normal(size=(4, 4))
    response22 = rng.normal(size=(4, 4))
    response22 = 0.5 * (response22 + response22.T)
    result = exact_joint_response_variance(
        factors, weight, response31, response22, probabilities
    )
    result.update(
        {
            "seed": seed,
            "correlation_scale": scale,
            "factors": len(factors),
        }
    )
    return result


def main() -> None:
    horizons = (12, 16, 20, 24, 28, 32)
    result = {
        "scope": "generated-only; no contest/public/private outcome access",
        "variance_cases": [
            variance_case(13411, 0.12),
            variance_case(13412, 0.30),
            variance_case(13413, 0.50),
        ],
        "equicorrelation_horizons": horizons,
        "equicorrelation_low_rho_0_2": equicorrelation_partial_sums(
            (0.3, 0.4, 0.5), (1.0, 1.0, 1.0), 0.2, horizons
        ),
        "equicorrelation_high_rho_0_975": equicorrelation_partial_sums(
            (0.3, 0.4, 0.5), (1.0, 1.0, 1.0), 0.975, horizons
        ),
        "costs": {
            "first_order_k1": cost_envelope(1, second_order=False),
            "first_order_k2": cost_envelope(2, second_order=False),
            "second_order_k1": cost_envelope(1, second_order=True),
            "second_order_k2": cost_envelope(2, second_order=True),
        },
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(payload, end="")


if __name__ == "__main__":
    main()
