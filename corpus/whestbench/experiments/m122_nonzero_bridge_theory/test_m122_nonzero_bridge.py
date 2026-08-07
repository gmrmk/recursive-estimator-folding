"""Generated-only identity tests for the M122 nonzero-mean bridge algebra."""

from __future__ import annotations

import itertools
import math
from pathlib import Path
import sys

import numpy as np

from m122_nonzero_bridge import (
    _set_partitions,
    build_state,
    direct_gh_raw_moment,
    exact_collision_cumulant,
    local_relu_coefficients,
    pair_raw_moment_series,
    power_hermite_coefficient,
    projected_tree_tensors,
    small_source_tensor,
    tree_tensor_continuation,
    triple_raw_moment_series,
)


def _reference_state() -> tuple[np.ndarray, np.ndarray]:
    mean = np.array([-0.35, 0.20, 0.55, -0.10], dtype=np.float64)
    correlation = np.array(
        [[1.0, 0.16, -0.11, 0.06], [0.16, 1.0, 0.12, -0.09], [-0.11, 0.12, 1.0, 0.14], [0.06, -0.09, 0.14, 1.0]],
        dtype=np.float64,
    )
    sigma = np.array([0.85, 1.10, 0.92, 1.25], dtype=np.float64)
    return mean, np.outer(sigma, sigma) * correlation


def _gh_coefficient(alpha: float, sigma: float, degree: int, *, order: int = 110) -> float:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    normal = math.sqrt(2.0) * nodes
    values = np.maximum(sigma * (alpha + normal), 0.0)
    hermite = np.polynomial.hermite_e.hermeval(normal, [0.0] * degree + [1.0])
    return float(weights @ (values * hermite) / math.sqrt(math.pi))


def _direct_cumulant(mean: np.ndarray, covariance: np.ndarray, labels: tuple[int, ...]) -> float:
    answer = 0.0
    for partition in _set_partitions(tuple(range(len(labels)))):
        coefficient = math.factorial(len(partition) - 1) * ((-1.0) ** (len(partition) - 1))
        product = 1.0
        for block in partition:
            grouped = tuple(labels[position] for position in block)
            unique = tuple(sorted(set(grouped)))
            local_mean = mean[list(unique)]
            local_covariance = covariance[np.ix_(unique, unique)]
            powers = tuple(grouped.count(index) for index in unique)
            product *= direct_gh_raw_moment(local_mean, local_covariance, powers, order=46)
        answer += coefficient * product
    return answer


def test_local_normal_ordered_coefficients_match_deterministic_quadrature() -> None:
    alpha, sigma = 0.35, 1.20
    expected = local_relu_coefficients(alpha, sigma)
    actual = tuple(_gh_coefficient(alpha, sigma, degree) for degree in (1, 2, 3))
    # A ReLU kink makes finite Gauss--Hermite rules algebraically inexact;
    # the high-order deterministic check is deliberately only a coarse
    # independent reference.  The exact identity is the derivative formula.
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=1.5e-3)
    assert expected[2] < 0.0  # The nonzero-mean cubic/LLLC vertex is retained.


def test_signed_pair_series_matches_deterministic_quadrature_and_m120_plackett() -> None:
    alpha_i, sigma_i, alpha_j, sigma_j, rho = -0.25, 0.9, 0.40, 1.25, -0.31
    series = pair_raw_moment_series(alpha_i, sigma_i, 2, alpha_j, sigma_j, 1, rho, terms=64)
    mean = np.array([alpha_i * sigma_i, alpha_j * sigma_j])
    covariance = np.array([[sigma_i * sigma_i, rho * sigma_i * sigma_j], [rho * sigma_i * sigma_j, sigma_j * sigma_j]])
    quadrature = direct_gh_raw_moment(mean, covariance, (2, 1), order=72)
    np.testing.assert_allclose(series, quadrature, rtol=0.0, atol=1.0e-3)

    # The independent M120 Plackett path evaluates the same signed E[ReLU_i ReLU_j].
    m120_root = Path(__file__).resolve().parents[1] / "m120_price_normal_ordered_adjoint"
    sys.path.insert(0, str(m120_root))
    try:
        from m120c_analytic_dense_reference import analytic_relu_gaussian_moments

        state = build_state(mean, covariance)
        _, m120_covariance = analytic_relu_gaussian_moments(mean, covariance)
        np.testing.assert_allclose(
            state.bridge[0, 1],
            m120_covariance[0, 1] / math.sqrt(m120_covariance[0, 0] * m120_covariance[1, 1]),
            rtol=0.0,
            atol=2.0e-9,
        )
        assert state.bridge[0, 1] < 0.0
    finally:
        sys.path.remove(str(m120_root))


def test_exact_collision_strata_match_generated_gauss_hermite_reference() -> None:
    mean, covariance = _reference_state()
    state = build_state(mean, covariance)
    for labels in ((0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2)):
        exact_series = exact_collision_cumulant(state, labels, terms=24)
        direct = _direct_cumulant(mean, covariance, labels)
        np.testing.assert_allclose(exact_series, direct, rtol=0.0, atol=2.0e-3)


def test_three_node_normal_ordered_series_matches_generated_quadrature() -> None:
    mean, covariance = _reference_state()
    selected = np.array([0, 1, 2])
    sigma = np.sqrt(np.diag(covariance))[selected]
    alpha = mean[selected] / sigma
    correlation = covariance[np.ix_(selected, selected)] / np.outer(sigma, sigma)
    series = triple_raw_moment_series(alpha, sigma, (2, 1, 1), correlation, terms=26)
    direct = direct_gh_raw_moment(mean[selected], covariance[np.ix_(selected, selected)], (2, 1, 1), order=48)
    np.testing.assert_allclose(series, direct, rtol=0.0, atol=3.0e-3)


def test_permutation_and_positive_gauge_covariance_of_small_source() -> None:
    mean, covariance = _reference_state()
    state = build_state(mean, covariance)
    source3 = small_source_tensor(state, 3, terms=20)
    source4 = small_source_tensor(state, 4, terms=20)
    diagonal = np.array([1.35, 0.72, 1.16, 0.88])
    gauged = build_state(diagonal * mean, covariance * np.outer(diagonal, diagonal))
    gauge3 = small_source_tensor(gauged, 3, terms=20)
    gauge4 = small_source_tensor(gauged, 4, terms=20)
    np.testing.assert_allclose(gauge3, source3 * np.einsum("i,j,k->ijk", diagonal, diagonal, diagonal), rtol=0.0, atol=3.0e-8)
    np.testing.assert_allclose(gauge4, source4 * np.einsum("i,j,k,l->ijkl", diagonal, diagonal, diagonal, diagonal), rtol=0.0, atol=5.0e-8)

    permutation = np.array([2, 0, 3, 1])
    permuted = build_state(mean[permutation], covariance[np.ix_(permutation, permutation)])
    np.testing.assert_allclose(small_source_tensor(permuted, 3, terms=20), source3[np.ix_(permutation, permutation, permutation)], rtol=0.0, atol=3.0e-8)
    np.testing.assert_allclose(small_source_tensor(permuted, 4, terms=20), source4[np.ix_(permutation, permutation, permutation, permutation)], rtol=0.0, atol=5.0e-8)


def test_low_rank_projection_matches_direct_tree_contraction() -> None:
    mean, covariance = _reference_state()
    state = build_state(mean, covariance)
    probe = np.random.default_rng(77).normal(size=(4, 3))
    direct3 = np.einsum("ijk,ia,jb,kc->abc", tree_tensor_continuation(state, 3), probe, probe, probe, optimize=True)
    direct4 = np.einsum("ijkl,ia,jb,kc,ld->abcd", tree_tensor_continuation(state, 4), probe, probe, probe, probe, optimize=True)
    projected3, projected4 = projected_tree_tensors(state, probe)
    np.testing.assert_allclose(projected3, direct3, rtol=0.0, atol=2.0e-11)
    np.testing.assert_allclose(projected4, direct4, rtol=0.0, atol=4.0e-11)
