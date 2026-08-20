"""Structural tests for M144 only; no MLP outcome comparison."""

from __future__ import annotations

import math

import numpy as np

from m144_gate_split_merge import (
    GaussianComponent,
    binary_truncated_standard_moments,
    gate_direction,
    merge_moment_preserving,
    mixture_moments,
    retained_component_history_bound,
    split_binary,
    split_surrogate_fourth_moment,
)


def _component() -> GaussianComponent:
    covariance = np.array(
        [[1.7, 0.3, -0.1], [0.3, 0.9, 0.2], [-0.1, 0.2, 1.3]], dtype=np.float64
    )
    return GaussianComponent(1.0, np.array([0.2, -0.4, 0.7]), covariance)


def test_binary_truncation_recombines_standard_first_two_moments() -> None:
    mass, mean, variance = binary_truncated_standard_moments()
    assert np.isclose(np.sum(mass), 1.0)
    assert np.isclose(mass @ mean, 0.0)
    assert np.isclose(mass @ (variance + mean * mean), 1.0)


def test_split_recombines_parent_first_two_moments() -> None:
    parent = _component()
    children = split_binary(parent)
    mass, mean, covariance = mixture_moments(children)
    assert np.isclose(mass, parent.weight)
    np.testing.assert_allclose(mean, parent.mean, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(covariance, parent.covariance, rtol=1e-12, atol=1e-12)


def test_direction_is_permutation_covariant() -> None:
    parent = _component()
    permutation = np.array([2, 0, 1])
    matrix = np.eye(3)[permutation]
    got = gate_direction(matrix @ parent.mean, matrix @ parent.covariance @ matrix.T)
    expected = matrix @ gate_direction(parent.mean, parent.covariance)
    np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)


def test_direction_is_positive_diagonal_gauge_covariant() -> None:
    parent = _component()
    diagonal = np.diag([0.4, 2.5, 1.7])
    got = gate_direction(diagonal @ parent.mean, diagonal @ parent.covariance @ diagonal)
    expected = np.linalg.inv(diagonal) @ gate_direction(parent.mean, parent.covariance)
    np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)


def test_split_is_positive_diagonal_gauge_covariant() -> None:
    parent = _component()
    diagonal = np.diag([0.4, 2.5, 1.7])
    transformed = GaussianComponent(
        parent.weight, diagonal @ parent.mean, diagonal @ parent.covariance @ diagonal
    )
    for original, got in zip(split_binary(parent), split_binary(transformed), strict=True):
        np.testing.assert_allclose(got.mean, diagonal @ original.mean, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(got.covariance, diagonal @ original.covariance @ diagonal, rtol=1e-12, atol=1e-12)


def test_merge_preserves_its_surrogate_mixture_moments() -> None:
    parent = _component()
    children = split_binary(parent)
    before = mixture_moments(children)
    after = merge_moment_preserving(children)
    assert np.isclose(before[0], after.weight)
    np.testing.assert_allclose(before[1], after.mean, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(before[2], after.covariance, rtol=1e-12, atol=1e-12)


def test_split_surrogate_is_not_a_moment_inferred_single_gaussian() -> None:
    fourth = split_surrogate_fourth_moment()
    assert np.isclose(fourth, 3.0 - 8.0 / math.pi**2)
    assert fourth < 3.0 - 0.8


def test_branch_capacity_witness() -> None:
    witness = retained_component_history_bound(depth=10, cap=4)
    assert witness == {
        "unmerged_histories": 1024,
        "cap": 4,
        "minimum_histories_per_retained_label": 256,
    }
