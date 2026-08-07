"""Algebra-only tests for M143; no generated response outcome is run here."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from m143_output_aware_proposal import (  # noqa: E402
    diagonal_path_energies,
    freeze_factored_proposal,
    make_output_aware_proposal,
    m143_incremental_cost_envelope,
    output_aware_node_strength_from_gated_downstream_energy,
    output_aware_node_strength_from_row_energy,
    physical_relu_scale,
    scale_only_node_strength,
)


def _bridge(n: int, seed: int = 14) -> np.ndarray:
    rng = np.random.default_rng(seed)
    factor = rng.normal(size=(n, n))
    gram = factor @ factor.T
    scale = np.sqrt(np.diag(gram))
    return gram / np.outer(scale, scale)


def test_path_energy_equals_exhaustive_rademacher_second_moment() -> None:
    weight0 = np.asarray([[.8, -.2, .3], [.1, .7, -.4], [.2, .5, .6]])
    weight1 = np.asarray([[.9, .1, -.2], [-.3, .8, .2], [.4, -.1, .7]])
    p0 = np.asarray([.4, .8, .6])
    p1 = np.asarray([.7, .5, .9])
    observed = diagonal_path_energies((weight0, weight1), (p0, p1))[0]
    all_signs = np.asarray(
        [[1.0 if (mask >> bit) & 1 else -1.0 for bit in range(3)] for mask in range(8)]
    )
    values = []
    for hidden_sign in all_signs:
        for terminal_sign in all_signs:
            jacobian = weight0 @ np.diag(hidden_sign * p0) @ weight1 @ np.diag(p1)
            values.append((jacobian @ terminal_sign) ** 2)
    expected = np.mean(np.asarray(values), axis=0)
    assert np.allclose(observed, expected, rtol=0.0, atol=2e-12)


def test_source_positive_gauge_invariance() -> None:
    rng = np.random.default_rng(1432)
    weight = rng.normal(size=(5, 5))
    scale = np.exp(rng.normal(size=5))
    energy = np.exp(rng.normal(size=5))
    base = output_aware_node_strength_from_gated_downstream_energy(weight, scale, energy)
    gauge = np.exp(rng.normal(size=5))
    transformed = output_aware_node_strength_from_gated_downstream_energy(
        weight / gauge[:, None], scale * gauge, energy
    )
    assert np.allclose(base, transformed, rtol=0.0, atol=2e-12)


def test_downstream_positive_gauge_invariance() -> None:
    rng = np.random.default_rng(1433)
    weight = rng.normal(size=(5, 5))
    scale = np.exp(rng.normal(size=5))
    energy = np.exp(rng.normal(size=5))
    gauge = np.exp(rng.normal(size=5))
    base = output_aware_node_strength_from_gated_downstream_energy(weight, scale, energy)
    transformed = output_aware_node_strength_from_gated_downstream_energy(
        weight * gauge[None, :], scale, energy / gauge**2
    )
    assert np.allclose(base, transformed, rtol=0.0, atol=2e-12)


def test_proposal_is_permutation_covariant() -> None:
    n = 6
    bridge = _bridge(n)
    strength = np.asarray([.4, .9, 1.5, .7, .3, 1.2])
    proposal = make_output_aware_proposal(bridge, strength)
    perm = np.asarray([3, 1, 5, 0, 4, 2])
    inverse = np.argsort(perm)
    permuted = make_output_aware_proposal(bridge[np.ix_(perm, perm)], strength[perm])
    for i in range(n):
        for j in range(n):
            for k in range(n):
                assert np.isclose(
                    proposal.probability(i, j, k),
                    permuted.probability(inverse[i], inverse[j], inverse[k]),
                    rtol=0.0,
                    atol=2e-12,
                )


def test_uniform_rescue_and_cost_contract() -> None:
    bridge = _bridge(4)
    proposal = make_output_aware_proposal(bridge, np.asarray([0.0, 0.0, 1.0, 0.0]))
    assert proposal.probability(0, 1, 2) > 0.0
    ledger = m143_incremental_cost_envelope()
    assert ledger["under_five_billion"]
    assert not ledger["uses_full_covariance_goal_adjoint"]


def test_direct_gated_and_cached_row_energy_agree() -> None:
    rng = np.random.default_rng(1434)
    weight = rng.normal(size=(7, 7))
    probability = rng.uniform(.1, .9, size=7)
    suffix = rng.uniform(.2, 2.0, size=7)
    scale = rng.uniform(.3, 1.6, size=7)
    cached = diagonal_path_energies(
        (weight,), (probability,), terminal_energy=suffix
    )[0]
    direct = output_aware_node_strength_from_gated_downstream_energy(
        weight, scale, probability**2 * suffix
    )
    from_cached = output_aware_node_strength_from_row_energy(scale, cached)
    assert np.allclose(direct, from_cached, rtol=0.0, atol=2e-12)


def test_exact_zero_strength_law_and_immutable_snapshot() -> None:
    bridge = _bridge(5, 1435)
    strength = np.asarray([0.0, .7, 0.0, 1.1, .4])
    proposal = make_output_aware_proposal(bridge, strength)
    residual = np.abs(bridge.copy())
    np.fill_diagonal(residual, 0.0)
    raw = {}
    for i in range(5):
        for j in range(5):
            for k in range(5):
                if len({i, j, k}) != 3:
                    continue
                raw[(i, j, k)] = strength[i] ** 2 * strength[j] * strength[k] * (
                    residual[i, j] * residual[i, k]
                    + residual[i, j] * residual[j, k]
                    + residual[i, k] * residual[j, k]
                )
    normalizer = sum(raw.values())
    population = 5 * 4 * 3
    for unit, mass in raw.items():
        expected = .05 / population + .95 * mass / normalizer
        assert np.isclose(proposal.probability(*unit), expected, rtol=0.0, atol=2e-12)
    # A zero-strength unit receives exactly rescue mass, not a tiny structured
    # perturbation.
    assert proposal.probability(0, 1, 3) == .05 / population
    frozen = freeze_factored_proposal(proposal)
    try:
        frozen.node_norm[0] = 1.0
    except ValueError:
        pass
    else:
        raise AssertionError("proposal snapshot remained mutable")


def test_all_zero_strength_is_exact_uniform() -> None:
    proposal = make_output_aware_proposal(_bridge(5, 1436), np.zeros(5))
    expected = 1.0 / (5 * 4 * 3)
    for i in range(5):
        for j in range(5):
            for k in range(5):
                if len({i, j, k}) == 3:
                    assert proposal.probability(i, j, k) == expected
    draws = proposal.sample(np.random.default_rng(1436), 25)
    assert draws.shape == (25, 3)
    assert all(len(set(row.tolist())) == 3 for row in draws)


def test_physical_scale_and_scale_only_definition() -> None:
    mean = np.asarray([0.0, .2, -.4])
    variance = np.asarray([1.0, .7, 1.3])
    scale = physical_relu_scale(mean, variance)
    assert np.all(scale > 0.0)
    weight = np.asarray([[.2, -.1, .4], [.3, .5, -.2], [-.7, .1, .2]])
    expected = scale * np.linalg.norm(weight, axis=1)
    assert np.allclose(scale_only_node_strength(weight, scale), expected, rtol=0.0, atol=2e-12)


def test_simultaneous_chain_gauge_and_permutation_covariance() -> None:
    rng = np.random.default_rng(1437)
    n = 5
    weights = tuple(rng.normal(size=(n, n)) for _ in range(3))
    probabilities = tuple(rng.uniform(.15, .85, size=n) for _ in range(3))
    scales = tuple(rng.uniform(.3, 1.5, size=n) for _ in range(3))
    bridges = tuple(_bridge(n, 1500 + layer) for layer in range(3))
    terminal = rng.uniform(.2, 1.7, size=n)
    energies = diagonal_path_energies(weights, probabilities, terminal_energy=terminal)
    strengths = tuple(
        output_aware_node_strength_from_row_energy(scales[layer], energies[layer])
        for layer in range(3)
    )

    gauges = tuple(np.exp(rng.normal(scale=.3, size=n)) for _ in range(4))
    gauged_weights = tuple(
        weights[layer] / gauges[layer][:, None] * gauges[layer + 1][None, :]
        for layer in range(3)
    )
    gauged_scales = tuple(scales[layer] * gauges[layer] for layer in range(3))
    gauged_terminal = terminal / gauges[3] ** 2
    gauged_energies = diagonal_path_energies(
        gauged_weights, probabilities, terminal_energy=gauged_terminal
    )
    gauged_strengths = tuple(
        output_aware_node_strength_from_row_energy(gauged_scales[layer], gauged_energies[layer])
        for layer in range(3)
    )
    for base, transformed in zip(strengths, gauged_strengths):
        assert np.allclose(base, transformed, rtol=0.0, atol=4e-12)

    perms = tuple(rng.permutation(n) for _ in range(4))
    permuted_weights = tuple(
        weights[layer][np.ix_(perms[layer], perms[layer + 1])]
        for layer in range(3)
    )
    permuted_probabilities = tuple(
        probabilities[layer][perms[layer + 1]] for layer in range(3)
    )
    permuted_scales = tuple(scales[layer][perms[layer]] for layer in range(3))
    permuted_energies = diagonal_path_energies(
        permuted_weights,
        permuted_probabilities,
        terminal_energy=terminal[perms[3]],
    )
    for layer in range(3):
        permuted_strength = output_aware_node_strength_from_row_energy(
            permuted_scales[layer], permuted_energies[layer]
        )
        assert np.allclose(
            permuted_strength, strengths[layer][perms[layer]], rtol=0.0, atol=4e-12
        )
        base = make_output_aware_proposal(bridges[layer], strengths[layer])
        permuted_bridge = bridges[layer][np.ix_(perms[layer], perms[layer])]
        moved = make_output_aware_proposal(permuted_bridge, permuted_strength)
        inverse = np.argsort(perms[layer])
        for unit in ((0, 1, 2), (2, 4, 1), (3, 0, 4)):
            mapped = tuple(int(inverse[index]) for index in unit)
            assert np.isclose(
                base.probability(*unit), moved.probability(*mapped), rtol=0.0, atol=3e-12
            )
