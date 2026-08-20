from __future__ import annotations

import itertools
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "m122_nonzero_bridge_theory"))
sys.path.insert(0, str(ROOT / "m126_repeated_output_source_contraction"))

from m122_nonzero_bridge import build_state, exact_collision_cumulant
from m126_repeated_output_contractions import collision211_repeated_exact
from m134_hermite_graph_sampler import (
    admissible_configurations,
    all_rademacher_signs,
    cost_envelope,
    equicorrelation_partial_sums,
    exact_joint_response_variance,
    factor_probe_t,
    factor_probe_t_dual,
    factor_tensor,
    hermite_factors,
    hermite_factors_dual,
    importance_probabilities,
    negative_tree_factors,
    negative_tree_factors_dual,
    repeated_output_probe,
    sum_factor_tensor,
    tree_211_tensor_oracle,
)
from m129_source_frechet import build_state_frechet


def generated_state(n: int, seed: int, correlation_scale: float = 0.12):
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


def test_configuration_count_and_central_ownership():
    assert len(admissible_configurations(24)) == 3654
    state = generated_state(4, 13401)
    factors = hermite_factors(state.alpha, state.sigma, state.correlation, 18)
    tensor = sum_factor_tensor(factors)
    for i in range(4):
        for j in range(4):
            for k in range(j + 1, 4):
                if len({i, j, k}) != 3:
                    continue
                reference = exact_collision_cumulant(state, (i, i, j, k), terms=32)
                np.testing.assert_allclose(tensor[i, j, k], reference, rtol=0, atol=2e-11)
    for i in range(4):
        assert not np.any(tensor[i, i, :])
        assert not np.any(tensor[i, :, i])
        assert not np.any(np.diag(tensor[i]))


def test_nine_negative_tree_factors_equal_exact_tree_continuation():
    state = generated_state(5, 13402)
    negative = sum_factor_tensor(negative_tree_factors(state))
    reference = tree_211_tensor_oracle(state)
    np.testing.assert_allclose(negative, -reference, rtol=0, atol=2e-13)


def test_one_gemm_triangle_identity_and_rademacher_transport():
    state = generated_state(5, 13403)
    factors = hermite_factors(state.alpha, state.sigma, state.correlation, 10)
    factors += negative_tree_factors(state)
    dense = sum_factor_tensor(factors)
    rng = np.random.default_rng(134030)
    sign = rng.choice((-1.0, 1.0), size=5)
    direct_t = np.einsum("ijk,j,k->i", dense, sign, sign, optimize=True)
    factored_t = sum(factor_probe_t(factor, sign) for factor in factors)
    np.testing.assert_allclose(factored_t, direct_t, rtol=0, atol=2e-12)

    weight = rng.normal(size=(5, 4))
    average = None
    for z in all_rademacher_signs(5):
        tables = repeated_output_probe(
            np.einsum("ijk,j,k->i", dense, z, z, optimize=True), z, weight
        )
        if average is None:
            average = {key: np.zeros_like(value) for key, value in tables.items()}
        for key, value in tables.items():
            average[key] += value / 32.0
    reference_tables = collision211_repeated_exact(dense, weight)
    for key in average:
        np.testing.assert_allclose(average[key], reference_tables[key], rtol=0, atol=3e-11)


def test_fixed_configuration_frechet_tangent():
    state = generated_state(5, 13404)
    rng = np.random.default_rng(134040)
    alpha_dot = rng.normal(scale=0.08, size=5)
    sigma_dot = rng.normal(scale=0.05, size=5)
    correlation_dot = rng.normal(scale=0.03, size=(5, 5))
    correlation_dot = 0.5 * (correlation_dot + correlation_dot.T)
    np.fill_diagonal(correlation_dot, 0.0)
    dual = hermite_factors_dual(
        state.alpha,
        state.sigma,
        state.correlation,
        alpha_dot,
        sigma_dot,
        correlation_dot,
        9,
    )[17]
    sign = rng.choice((-1.0, 1.0), size=5)
    value, tangent = factor_probe_t_dual(dual, sign)
    epsilon = 2e-6
    plus = hermite_factors(
        state.alpha + epsilon * alpha_dot,
        state.sigma + epsilon * sigma_dot,
        state.correlation + epsilon * correlation_dot,
        9,
    )[17]
    minus = hermite_factors(
        state.alpha - epsilon * alpha_dot,
        state.sigma - epsilon * sigma_dot,
        state.correlation - epsilon * correlation_dot,
        9,
    )[17]
    finite = (factor_probe_t(plus, sign) - factor_probe_t(minus, sign)) / (2 * epsilon)
    np.testing.assert_allclose(value, factor_probe_t(dual.value, sign), rtol=0, atol=2e-13)
    np.testing.assert_allclose(tangent, finite, rtol=2e-7, atol=2e-8)


def test_negative_tree_control_frechet_tangent():
    state = generated_state(5, 134041)
    rng = np.random.default_rng(1340410)
    mean_dot = rng.normal(scale=0.03, size=5)
    covariance_dot = rng.normal(scale=0.02, size=(5, 5))
    covariance_dot = 0.5 * (covariance_dot + covariance_dot.T)
    tangent_state = build_state_frechet(
        state.mean, state.covariance, mean_dot, covariance_dot, pair_terms=64
    )
    factor = negative_tree_factors_dual(tangent_state)[7]
    sign = rng.choice((-1.0, 1.0), size=5)
    _, tangent = factor_probe_t_dual(factor, sign)
    epsilon = 2e-6
    plus = build_state(
        state.mean + epsilon * mean_dot,
        state.covariance + epsilon * covariance_dot,
        pair_terms=64,
    )
    minus = build_state(
        state.mean - epsilon * mean_dot,
        state.covariance - epsilon * covariance_dot,
        pair_terms=64,
    )
    finite = (
        factor_probe_t(negative_tree_factors(plus)[7], sign)
        - factor_probe_t(negative_tree_factors(minus)[7], sign)
    ) / (2 * epsilon)
    np.testing.assert_allclose(tangent, finite, rtol=4e-7, atol=3e-8)


def test_importance_sampler_has_exact_generated_response_moments():
    state = generated_state(4, 13405)
    factors = hermite_factors(state.alpha, state.sigma, state.correlation, 10)
    factors += negative_tree_factors(state)
    probabilities = importance_probabilities(factors)
    rng = np.random.default_rng(134050)
    weight = rng.normal(scale=0.4, size=(4, 4))
    response31 = rng.normal(size=(4, 4))
    response22 = rng.normal(size=(4, 4))
    response22 = 0.5 * (response22 + response22.T)
    audit = exact_joint_response_variance(
        factors, weight, response31, response22, probabilities
    )
    assert np.isfinite(audit["joint_variance_one_probe"])
    assert audit["joint_variance_one_probe"] >= audit["hidden_variance_one_probe"]
    assert audit["joint_over_m129_p2"] >= 2.0


def test_high_correlation_series_fails_convergence_gate():
    horizons = (12, 16, 20, 24, 28, 32)
    low = equicorrelation_partial_sums((0.3, 0.4, 0.5), (1, 1, 1), 0.2, horizons)
    high = equicorrelation_partial_sums((0.3, 0.4, 0.5), (1, 1, 1), 0.975, horizons)
    assert abs(low[-1] - low[-2]) < 1e-12
    assert abs(high[-1]) > 1000.0
    assert abs(high[-1] - high[-2]) > 1000.0


def test_static_cost_boundary_is_fail_closed():
    first1 = cost_envelope(1, second_order=False)
    first2 = cost_envelope(2, second_order=False)
    second1 = cost_envelope(1, second_order=True)
    second2 = cost_envelope(2, second_order=True)
    assert first1["protected_total_before_builder"] == 97_085_641_040
    assert first2["protected_total_before_builder"] == 99_681_030_480
    assert second1["lower_total"] == 90_681_030_480
    assert second2["lower_total"] == 95_871_809_360
    assert second1["protected_upper"] > 100_000_000_000
