"""Generated-only M131 trivariate boundary and projected-source reference.

Two mechanisms are kept deliberately separate:

* a conditional one-dimensional quadrature is an independent correctness
  reference for ``E[Y_i^2 Y_j Y_k]`` and its state directional derivative;
* a normal-ordered projected sampler estimates the complete affine-output
  repeated ``k3/k4`` tables directly, avoiding every explicit trivariate
  coefficient and every ambient order-three/four source tensor.

No model, scorer, benchmark, target, or outcome access exists in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "m122_nonzero_bridge_theory",
    "m129_source_frechet_tangent",
    "m120_price_normal_ordered_adjoint",
    "m125_source_batched_forward_tangent",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m129_source_frechet import (  # noqa: E402
    BridgeStateFrechet,
    Dual,
    _tree_entry_dot,
    exact_collision_cumulant_dot,
    power_hermite_coefficient_dot,
    triple_raw_moment_series_dot,
)
from m120c_analytic_dense_reference import (  # noqa: E402
    analytic_local_kernels,
    analytic_relu_gaussian_moments,
    quadrant_probability,
    relu_mean,
)
from m125_forward_tangent import (  # noqa: E402
    LocalReluJacobian,
    TangentState,
    tangent_stage,
)
from m122_nonzero_bridge import (  # noqa: E402
    NonzeroMeanBridgeState,
    power_hermite_coefficient,
)


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _cdf(value: float) -> float:
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def _pdf(value: float) -> float:
    return _INV_SQRT_2PI * math.exp(-0.5 * value * value)


def bivariate_relu_raw_dot(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
) -> tuple[float, float]:
    """Exact bivariate positive-part product and Frechet derivative.

    Bonnet/Price derivatives avoid differentiating a bivariate CDF: mean
    directions are gate--ReLU boundary moments, diagonal covariance directions
    carry the distributional ``1/2 delta`` factor, and the off-diagonal
    covariance derivative is the positive-quadrant probability.
    """

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    if (
        mean.shape != (2,)
        or covariance.shape != (2, 2)
        or mean_dot.shape != (2,)
        or covariance_dot.shape != (2, 2)
        or not np.array_equal(covariance, covariance.T)
        or not np.array_equal(covariance_dot, covariance_dot.T)
    ):
        raise ValueError("invalid bivariate value/tangent shapes")
    variance = np.diag(covariance)
    if np.any(variance <= 1.0e-12) or np.linalg.det(covariance) <= 1.0e-14:
        raise ValueError("bivariate covariance is not comfortably positive definite")
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    rho = float(covariance[0, 1] / (sigma[0] * sigma[1]))
    if abs(rho) >= 1.0 - 1.0e-10:
        raise ValueError("bivariate correlation is too close to singular")
    root = math.sqrt(1.0 - rho * rho)
    quadrant = quadrant_probability(float(alpha[0]), float(alpha[1]), rho).value
    density = np.asarray([_pdf(float(alpha[0])), _pdf(float(alpha[1]))])
    boundary0 = density[0] * _cdf(float((alpha[1] - rho * alpha[0]) / root))
    boundary1 = density[1] * _cdf(float((alpha[0] - rho * alpha[1]) / root))
    joint_density = (
        math.exp(
            -(
                alpha[0] ** 2
                + alpha[1] ** 2
                - 2.0 * rho * alpha[0] * alpha[1]
            )
            / (2.0 * (1.0 - rho * rho))
        )
        / (2.0 * math.pi * root)
    )
    raw = (
        mean[1] * sigma[0] * boundary0
        + mean[0] * sigma[1] * boundary1
        + sigma[0] * sigma[1] * (1.0 - rho * rho) * joint_density
        + (mean[0] * mean[1] + covariance[0, 1]) * quadrant
    )

    d0 = boundary0 / sigma[0]
    d1 = boundary1 / sigma[1]
    derivative_mean0 = (
        mean[1] * quadrant + covariance[1, 0] * d0 + covariance[1, 1] * d1
    )
    derivative_mean1 = (
        mean[0] * quadrant + covariance[0, 1] * d1 + covariance[0, 0] * d0
    )
    conditional_mean1 = mean[1] - covariance[1, 0] * mean[0] / covariance[0, 0]
    conditional_variance1 = (
        covariance[1, 1] - covariance[1, 0] ** 2 / covariance[0, 0]
    )
    conditional_mean0 = mean[0] - covariance[0, 1] * mean[1] / covariance[1, 1]
    conditional_variance0 = (
        covariance[0, 0] - covariance[0, 1] ** 2 / covariance[1, 1]
    )
    derivative_variance0 = (
        0.5
        * density[0]
        / sigma[0]
        * relu_mean(float(conditional_mean1), float(conditional_variance1))
    )
    derivative_variance1 = (
        0.5
        * density[1]
        / sigma[1]
        * relu_mean(float(conditional_mean0), float(conditional_variance0))
    )
    derivative = (
        derivative_mean0 * mean_dot[0]
        + derivative_mean1 * mean_dot[1]
        + derivative_variance0 * covariance_dot[0, 0]
        + derivative_variance1 * covariance_dot[1, 1]
        + quadrant * covariance_dot[0, 1]
    )
    return float(raw), float(derivative)


@dataclass(frozen=True)
class PairedQuadrature:
    value: float
    tangent: float
    value_disagreement: float
    tangent_disagreement: float
    coarse_order: int
    fine_order: int


def _conditional_triple_rule(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    repeated: int,
    singleton_left: int,
    singleton_right: int,
    order: int,
) -> tuple[float, float]:
    # Split exactly at the repeated ReLU boundary and map its positive tail by
    # x = lower + t/(1-t), t in (0,1).  The repeated squared ReLU supplies a
    # double zero at t=0, while the Gaussian density suppresses t->1.  This is
    # markedly more stable than an unsplit Gauss-Hermite rule across the kink.
    legendre_nodes, legendre_weights = np.polynomial.legendre.leggauss(order)
    t_nodes = 0.5 * (legendre_nodes + 1.0)
    t_weights = 0.5 * legendre_weights
    i, j, k = repeated, singleton_left, singleton_right
    sigma_i = math.sqrt(float(covariance[i, i]))
    sigma_i_dot = float(covariance_dot[i, i]) / (2.0 * sigma_i)
    alpha_i = float(mean[i]) / sigma_i
    alpha_i_dot = float(mean_dot[i]) / sigma_i - alpha_i * sigma_i_dot / sigma_i
    lower = -alpha_i
    lower_dot = -alpha_i_dot
    beta_j = float(covariance[j, i]) / sigma_i
    beta_k = float(covariance[k, i]) / sigma_i
    beta_j_dot = (
        float(covariance_dot[j, i]) / sigma_i
        - beta_j * sigma_i_dot / sigma_i
    )
    beta_k_dot = (
        float(covariance_dot[k, i]) / sigma_i
        - beta_k * sigma_i_dot / sigma_i
    )
    conditional_covariance = covariance[np.ix_((j, k), (j, k))].copy()
    conditional_covariance -= np.outer(
        covariance[(j, k), i], covariance[(j, k), i]
    ) / covariance[i, i]
    numerator_dot = (
        np.outer(covariance_dot[(j, k), i], covariance[(j, k), i])
        + np.outer(covariance[(j, k), i], covariance_dot[(j, k), i])
    ) / covariance[i, i]
    denominator_dot = (
        np.outer(covariance[(j, k), i], covariance[(j, k), i])
        * covariance_dot[i, i]
        / covariance[i, i] ** 2
    )
    conditional_covariance_dot = (
        covariance_dot[np.ix_((j, k), (j, k))]
        - numerator_dot
        + denominator_dot
    )
    values: list[float] = []
    tangents: list[float] = []
    for t, weight in zip(t_nodes, t_weights):
        radial = float(t / (1.0 - t))
        jacobian = 1.0 / (1.0 - t) ** 2
        node = lower + radial
        node_dot = lower_dot
        density = _pdf(node)
        density_dot = -node * density * node_dot
        preactivation_i = sigma_i * radial
        preactivation_i_dot = sigma_i_dot * radial
        conditional_mean = np.asarray(
            [mean[j] + beta_j * node, mean[k] + beta_k * node],
            dtype=np.float64,
        )
        conditional_mean_dot = np.asarray(
            [
                mean_dot[j] + beta_j_dot * node + beta_j * node_dot,
                mean_dot[k] + beta_k_dot * node + beta_k * node_dot,
            ],
            dtype=np.float64,
        )
        pair, pair_dot = bivariate_relu_raw_dot(
            conditional_mean,
            conditional_covariance,
            conditional_mean_dot,
            conditional_covariance_dot,
        )
        common = float(weight) * jacobian
        values.append(common * density * preactivation_i**2 * pair)
        tangents.append(
            common
            * (
                density_dot * preactivation_i**2 * pair
                + density
                * (
                    2.0 * preactivation_i * preactivation_i_dot * pair
                    + preactivation_i**2 * pair_dot
                )
            )
        )
    return math.fsum(values), math.fsum(tangents)


def conditional_triple_relu_raw_dot(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    repeated: int,
    singleton_left: int,
    singleton_right: int,
    *,
    coarse_order: int = 32,
    fine_order: int = 48,
) -> PairedQuadrature:
    """Independent conditional-1D reference for ``E[Y_i^2Y_jY_k]``."""

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    if len({repeated, singleton_left, singleton_right}) != 3:
        raise ValueError("the conditional reference is for three distinct labels")
    if covariance.shape != (mean.size, mean.size) or mean_dot.shape != mean.shape or covariance_dot.shape != covariance.shape:
        raise ValueError("trivariate conditional state shape mismatch")
    coarse = _conditional_triple_rule(
        mean,
        covariance,
        mean_dot,
        covariance_dot,
        repeated,
        singleton_left,
        singleton_right,
        coarse_order,
    )
    fine = _conditional_triple_rule(
        mean,
        covariance,
        mean_dot,
        covariance_dot,
        repeated,
        singleton_left,
        singleton_right,
        fine_order,
    )
    return PairedQuadrature(
        fine[0],
        fine[1],
        abs(fine[0] - coarse[0]),
        abs(fine[1] - coarse[1]),
        coarse_order,
        fine_order,
    )


def conditional_collision211_defect_dot(
    tangent: BridgeStateFrechet,
    repeated: int,
    singleton_left: int,
    singleton_right: int,
    *,
    coarse_order: int = 32,
    fine_order: int = 48,
    series_terms: int = 24,
) -> tuple[float, float, PairedQuadrature]:
    """Collision defect using conditional raw moment in the unique 3D block."""

    state = tangent.state
    selected = np.asarray((repeated, singleton_left, singleton_right), dtype=int)
    conditional = conditional_triple_relu_raw_dot(
        state.mean,
        state.covariance,
        tangent.mean_dot,
        tangent.covariance_dot,
        repeated,
        singleton_left,
        singleton_right,
        coarse_order=coarse_order,
        fine_order=fine_order,
    )
    series_raw = triple_raw_moment_series_dot(
        state.alpha[selected],
        state.sigma[selected],
        (2, 1, 1),
        state.correlation[np.ix_(selected, selected)],
        tangent.alpha_dot[selected],
        tangent.sigma_dot[selected],
        tangent.correlation_dot[np.ix_(selected, selected)],
        terms=series_terms,
    )
    labels = (repeated, repeated, singleton_left, singleton_right)
    series_cumulant = exact_collision_cumulant_dot(
        tangent, labels, terms=series_terms
    )
    cumulant = (
        series_cumulant[0] + conditional.value - series_raw[0],
        series_cumulant[1] + conditional.tangent - series_raw[1],
    )
    tree = _tree_entry_dot(tangent, labels)
    return cumulant[0] - tree[0], cumulant[1] - tree[1], conditional


def cholesky_frechet(
    covariance: np.ndarray, covariance_dot: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Lower Cholesky factor and exact forward directional derivative."""

    covariance = np.asarray(covariance, dtype=np.float64)
    covariance_dot = np.asarray(covariance_dot, dtype=np.float64)
    if covariance.shape != covariance_dot.shape or not np.array_equal(covariance, covariance.T) or not np.array_equal(covariance_dot, covariance_dot.T):
        raise ValueError("Cholesky value/tangent shape mismatch")
    factor = np.linalg.cholesky(covariance)
    left_solved = np.linalg.solve(factor, covariance_dot)
    whitened = np.linalg.solve(factor, left_solved.T).T
    whitened = 0.5 * (whitened + whitened.T)
    phi = np.tril(whitened)
    diagonal = np.diag_indices_from(phi)
    phi[diagonal] *= 0.5
    factor_dot = factor @ phi
    return factor, factor_dot


def relu_covariance_dual(tangent: BridgeStateFrechet) -> Dual:
    state = tangent.state
    value = state.bridge * np.outer(state.relu_scale, state.relu_scale)
    derivative = (
        tangent.bridge_dot * np.outer(state.relu_scale, state.relu_scale)
        + state.bridge * np.outer(tangent.relu_scale_dot, state.relu_scale)
        + state.bridge * np.outer(state.relu_scale, tangent.relu_scale_dot)
    )
    return Dual(value, 0.5 * (derivative + derivative.T))


def build_zero_sampling_frechet(
    mean: np.ndarray, covariance: np.ndarray
) -> BridgeStateFrechet:
    """Target-width exact Gaussian/ReLU state with a zero tangent.

    M122 deliberately limits its tensor reference builder to width eight.
    The projected sampler only needs exact first/two-point Gaussian ReLU
    moments and univariate Hermite coefficients, so this wider constructor
    uses the independent analytic bivariate kernel and introduces no tensor
    approximation.
    """

    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if mean.ndim != 1 or covariance.shape != (mean.size, mean.size):
        raise ValueError("sampling state shape mismatch")
    activation_mean, activation_covariance = analytic_relu_gaussian_moments(
        mean, covariance
    )
    sigma = np.sqrt(np.diag(covariance))
    alpha = mean / sigma
    correlation = covariance / np.outer(sigma, sigma)
    correlation = 0.5 * (correlation + correlation.T)
    np.fill_diagonal(correlation, 1.0)
    activation_scale = np.sqrt(np.diag(activation_covariance))
    bridge = activation_covariance / np.outer(activation_scale, activation_scale)
    bridge = 0.5 * (bridge + bridge.T)
    np.fill_diagonal(bridge, 1.0)
    h1 = np.asarray(
        [
            power_hermite_coefficient(float(a), float(s), 1, 1)
            for a, s in zip(alpha, sigma)
        ]
    )
    h2 = np.asarray(
        [
            power_hermite_coefficient(float(a), float(s), 1, 2)
            for a, s in zip(alpha, sigma)
        ]
    )
    h3 = np.asarray(
        [
            power_hermite_coefficient(float(a), float(s), 1, 3)
            for a, s in zip(alpha, sigma)
        ]
    )
    gamma2 = h2 * activation_scale / (h1 * h1)
    gamma3 = h3 * activation_scale * activation_scale / (h1 * h1 * h1)
    state = NonzeroMeanBridgeState(
        mean,
        covariance,
        sigma,
        alpha,
        activation_mean,
        activation_scale,
        correlation,
        bridge,
        gamma2,
        gamma3,
    )
    zeros_vector = np.zeros_like(mean)
    zeros_matrix = np.zeros_like(covariance)
    return BridgeStateFrechet(
        state,
        zeros_vector,
        zeros_matrix,
        zeros_vector.copy(),
        zeros_vector.copy(),
        zeros_vector.copy(),
        zeros_vector.copy(),
        zeros_matrix.copy(),
        zeros_matrix.copy(),
        zeros_vector.copy(),
        zeros_vector.copy(),
    )


@dataclass(frozen=True)
class SampledRepeatedSource:
    repeated: dict[str, Dual]
    k3_banks: tuple[Dual, ...]
    output_samples: Dual
    output_covariance: Dual


@dataclass(frozen=True)
class FirstChaosControlledSource:
    """Common-random full-minus-affine normal-ordered source.

    ``controlled`` is the deployable unbiased difference.  ``uncontrolled``
    and ``affine_control`` are retained only for generated variance audits.
    The affine control has identically zero population cumulants of orders
    three and four, so no analytic add-back is required.
    """

    controlled: SampledRepeatedSource
    uncontrolled: SampledRepeatedSource
    affine_control: SampledRepeatedSource


def independent_k3_pair_convolution(k3_banks: tuple[Dual, ...]) -> Dual:
    """Unbiased cross-bank M128 pair convolution ``A_q``, q=0..6.

    Each bank independently estimates the complete repeated cubic table.
    Averaging products over *ordered distinct* banks is the U-statistic that
    removes the same-bank noise square.  For pair ``(i,j)``, the four slots
    are ``K_p = kappa[i repeated p, j repeated 3-p]``.  The returned shape is
    ``(7,n,n)`` and already includes both binomial slot multiplicities.
    """

    if len(k3_banks) < 2:
        raise ValueError("k3 squared response requires at least two independent banks")
    n = np.asarray(k3_banks[0].value).shape[0]
    if any(
        np.asarray(bank.value).shape != (n, n)
        or np.asarray(bank.tangent).shape != (n, n)
        for bank in k3_banks
    ):
        raise ValueError("k3 bank shape mismatch")

    def slots(bank: Dual) -> tuple[np.ndarray, np.ndarray]:
        value = np.asarray(bank.value, dtype=np.float64)
        tangent = np.asarray(bank.tangent, dtype=np.float64)
        diagonal = np.diag(value)
        diagonal_dot = np.diag(tangent)
        slot_value = np.empty((4, n, n), dtype=np.float64)
        slot_dot = np.empty_like(slot_value)
        slot_value[0] = diagonal[None, :]
        slot_value[1] = value.T
        slot_value[2] = value
        slot_value[3] = diagonal[:, None]
        slot_dot[0] = diagonal_dot[None, :]
        slot_dot[1] = tangent.T
        slot_dot[2] = tangent
        slot_dot[3] = diagonal_dot[:, None]
        return slot_value, slot_dot

    prepared = [slots(bank) for bank in k3_banks]
    value = np.zeros((7, n, n), dtype=np.float64)
    tangent = np.zeros_like(value)
    pairs = 0
    binomial = (1.0, 3.0, 3.0, 1.0)
    for left_index, (left, left_dot) in enumerate(prepared):
        for right_index, (right, right_dot) in enumerate(prepared):
            if left_index == right_index:
                continue
            pairs += 1
            for p in range(4):
                for r in range(4):
                    coefficient = binomial[p] * binomial[r]
                    value[p + r] += coefficient * left[p] * right[r]
                    tangent[p + r] += coefficient * (
                        left_dot[p] * right[r] + left[p] * right_dot[r]
                    )
    return Dual(value / pairs, tangent / pairs)


def _weighted_mean(value: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.tensordot(weights, value, axes=(0, 0))


def _weighted_gram(
    left: np.ndarray, right: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    return left.T @ (weights[:, None] * right)


def _k3_wick(
    output: np.ndarray,
    output_dot: np.ndarray,
    covariance: np.ndarray,
    covariance_dot: np.ndarray,
    weights: np.ndarray,
) -> Dual:
    mean = _weighted_mean(output, weights)
    mean_dot = _weighted_mean(output_dot, weights)
    raw = _weighted_gram(output * output, output, weights)
    raw_dot = _weighted_gram(2.0 * output * output_dot, output, weights) + _weighted_gram(
        output * output, output_dot, weights
    )
    diagonal = np.diag(covariance)
    diagonal_dot = np.diag(covariance_dot)
    value = raw - diagonal[:, None] * mean[None, :] - 2.0 * mean[:, None] * covariance
    derivative = (
        raw_dot
        - diagonal_dot[:, None] * mean[None, :]
        - diagonal[:, None] * mean_dot[None, :]
        - 2.0 * mean_dot[:, None] * covariance
        - 2.0 * mean[:, None] * covariance_dot
    )
    return Dual(value, derivative)


def _normal_ordered_repeated_from_outputs(
    output: np.ndarray,
    output_dot: np.ndarray,
    output_covariance: Dual,
    weights: np.ndarray,
    bank_count: int,
) -> tuple[dict[str, Dual], tuple[Dual, ...]]:
    """Normal-ordered repeated tables for a centered affine output sample."""

    count = output.shape[0]
    covariance = output_covariance.value
    covariance_dot = output_covariance.tangent
    diagonal = np.diag(covariance)
    diagonal_dot = np.diag(covariance_dot)

    bank_size = count // bank_count
    k3_banks: list[Dual] = []
    for bank in range(bank_count):
        section = slice(bank * bank_size, (bank + 1) * bank_size)
        local_weights = weights[section]
        local_weights = local_weights / np.sum(local_weights)
        k3_banks.append(
            _k3_wick(
                output[section],
                output_dot[section],
                covariance,
                covariance_dot,
                local_weights,
            )
        )
    k3 = Dual(
        sum(item.value for item in k3_banks) / bank_count,
        sum(item.tangent for item in k3_banks) / bank_count,
    )

    second_sample = _weighted_gram(output, output, weights)
    second_sample_dot_half = _weighted_gram(output_dot, output, weights)
    second_sample_dot = second_sample_dot_half + second_sample_dot_half.T
    sample_diagonal = np.diag(second_sample)
    sample_diagonal_dot = np.diag(second_sample_dot)

    raw31 = _weighted_gram(output**3, output, weights)
    raw31_dot = _weighted_gram(
        3.0 * output * output * output_dot, output, weights
    ) + _weighted_gram(output**3, output_dot, weights)
    k4_aaab = (
        raw31
        - 3.0 * diagonal[:, None] * second_sample
        - 3.0 * sample_diagonal[:, None] * covariance
        + 3.0 * diagonal[:, None] * covariance
    )
    k4_aaab_dot = (
        raw31_dot
        - 3.0
        * (
            diagonal_dot[:, None] * second_sample
            + diagonal[:, None] * second_sample_dot
        )
        - 3.0
        * (
            sample_diagonal_dot[:, None] * covariance
            + sample_diagonal[:, None] * covariance_dot
        )
        + 3.0
        * (
            diagonal_dot[:, None] * covariance
            + diagonal[:, None] * covariance_dot
        )
    )

    square_output = output * output
    square_output_dot = 2.0 * output * output_dot
    raw22 = _weighted_gram(square_output, square_output, weights)
    raw22_dot_half = _weighted_gram(square_output_dot, square_output, weights)
    raw22_dot = raw22_dot_half + raw22_dot_half.T
    k4_aabb = (
        raw22
        - diagonal[:, None] * sample_diagonal[None, :]
        - sample_diagonal[:, None] * diagonal[None, :]
        - 4.0 * covariance * second_sample
        + np.outer(diagonal, diagonal)
        + 2.0 * covariance * covariance
    )
    k4_aabb_dot = (
        raw22_dot
        - diagonal_dot[:, None] * sample_diagonal[None, :]
        - diagonal[:, None] * sample_diagonal_dot[None, :]
        - sample_diagonal_dot[:, None] * diagonal[None, :]
        - sample_diagonal[:, None] * diagonal_dot[None, :]
        - 4.0 * (covariance_dot * second_sample + covariance * second_sample_dot)
        + np.outer(diagonal_dot, diagonal)
        + np.outer(diagonal, diagonal_dot)
        + 4.0 * covariance * covariance_dot
    )

    repeated = {
        "k3_aaa": Dual(np.diag(k3.value).copy(), np.diag(k3.tangent).copy()),
        "k3_aab": k3,
        "k4_aaaa": Dual(
            np.diag(k4_aaab).copy(), np.diag(k4_aaab_dot).copy()
        ),
        "k4_aaab": Dual(k4_aaab, k4_aaab_dot),
        "k4_aabb": Dual(k4_aabb, k4_aabb_dot),
    }
    return repeated, tuple(k3_banks)


def sampled_normal_ordered_source(
    tangent: BridgeStateFrechet,
    downstream_weight: np.ndarray,
    standard_samples: np.ndarray,
    *,
    sample_weights: np.ndarray | None = None,
    bank_count: int = 2,
) -> SampledRepeatedSource:
    """Direct affine-output ``k3/k4`` source and Frechet tangent.

    Exact local means/covariances normal-order each sample.  The estimator is
    unbiased for iid standard-normal samples.  Antithetic pairs remain
    unbiased.  ``bank_count=2`` exposes independent cubic estimates for the
    M128 ``k3^2`` response; a same-bank square must not be used.
    """

    weight = np.asarray(downstream_weight, dtype=np.float64)
    samples = np.asarray(standard_samples, dtype=np.float64)
    n = tangent.state.mean.size
    if weight.shape[0] != n or samples.ndim != 2 or samples.shape[1] != n:
        raise ValueError("sampled source shape mismatch")
    count = samples.shape[0]
    if bank_count < 1 or count % bank_count:
        raise ValueError("sample count must split evenly across banks")
    if sample_weights is None:
        weights = np.full(count, 1.0 / count, dtype=np.float64)
    else:
        weights = np.asarray(sample_weights, dtype=np.float64)
        if weights.shape != (count,) or np.any(weights < 0.0) or not math.isclose(float(np.sum(weights)), 1.0, rel_tol=0.0, abs_tol=2e-14):
            raise ValueError("sample weights must be finite nonnegative and sum to one")

    factor, factor_dot = cholesky_frechet(
        tangent.state.covariance, tangent.covariance_dot
    )
    preactivation = tangent.state.mean[None, :] + samples @ factor.T
    preactivation_dot = tangent.mean_dot[None, :] + samples @ factor_dot.T
    activation = np.maximum(preactivation, 0.0)
    activation_dot = (preactivation > 0.0) * preactivation_dot
    centered = activation - tangent.state.relu_mean[None, :]
    centered_dot = activation_dot - tangent.relu_mean_dot[None, :]
    output = centered @ weight
    output_dot = centered_dot @ weight

    activation_covariance = relu_covariance_dual(tangent)
    output_covariance = Dual(
        weight.T @ activation_covariance.value @ weight,
        weight.T @ activation_covariance.tangent @ weight,
    )
    repeated, k3_banks = _normal_ordered_repeated_from_outputs(
        output, output_dot, output_covariance, weights, bank_count
    )
    return SampledRepeatedSource(
        repeated,
        k3_banks,
        Dual(output, output_dot),
        output_covariance,
    )


def sampled_first_chaos_controlled_source(
    tangent: BridgeStateFrechet,
    downstream_weight: np.ndarray,
    standard_samples: np.ndarray,
    *,
    sample_weights: np.ndarray | None = None,
    bank_count: int = 2,
) -> FirstChaosControlledSource:
    """Unbiased common-random control using the exact first Wiener chaos.

    For ``X=mu+L g``, write ``G_i=(X_i-mu_i)/sigma_i`` and
    ``P_i=h1_i G_i`` with ``h1_i=E[(X_i)_+ G_i]``.  ``P`` is jointly
    Gaussian and is the orthogonal first-chaos projection of centered ReLU.
    Every population k3/k4 table of ``P @ W`` is exactly zero.  Subtracting
    its *sampled normal-ordered table* from the full table is consequently
    unbiased and couples away the leading affine Gaussian fluctuation.
    """

    uncontrolled = sampled_normal_ordered_source(
        tangent,
        downstream_weight,
        standard_samples,
        sample_weights=sample_weights,
        bank_count=bank_count,
    )
    weight = np.asarray(downstream_weight, dtype=np.float64)
    samples = np.asarray(standard_samples, dtype=np.float64)
    count = samples.shape[0]
    if sample_weights is None:
        weights = np.full(count, 1.0 / count, dtype=np.float64)
    else:
        weights = np.asarray(sample_weights, dtype=np.float64)

    factor, factor_dot = cholesky_frechet(
        tangent.state.covariance, tangent.covariance_dot
    )
    centered_gaussian = samples @ factor.T
    centered_gaussian_dot = samples @ factor_dot.T
    standardized = centered_gaussian / tangent.state.sigma[None, :]
    standardized_dot = (
        centered_gaussian_dot / tangent.state.sigma[None, :]
        - standardized
        * (tangent.sigma_dot / tangent.state.sigma)[None, :]
    )
    n = tangent.state.mean.size
    h1 = np.empty(n, dtype=np.float64)
    h1_dot = np.empty(n, dtype=np.float64)
    for index in range(n):
        h1[index], h1_dot[index] = power_hermite_coefficient_dot(
            float(tangent.state.alpha[index]),
            float(tangent.state.sigma[index]),
            1,
            1,
            float(tangent.alpha_dot[index]),
            float(tangent.sigma_dot[index]),
        )
    projected_activation = standardized * h1[None, :]
    projected_activation_dot = (
        standardized_dot * h1[None, :]
        + standardized * h1_dot[None, :]
    )
    control_output = projected_activation @ weight
    control_output_dot = projected_activation_dot @ weight
    activation_covariance = np.outer(h1, h1) * tangent.state.correlation
    activation_covariance_dot = (
        np.outer(h1_dot, h1) * tangent.state.correlation
        + np.outer(h1, h1_dot) * tangent.state.correlation
        + np.outer(h1, h1) * tangent.correlation_dot
    )
    control_covariance = Dual(
        weight.T @ activation_covariance @ weight,
        weight.T @ activation_covariance_dot @ weight,
    )
    control_repeated, control_banks = _normal_ordered_repeated_from_outputs(
        control_output,
        control_output_dot,
        control_covariance,
        weights,
        bank_count,
    )
    affine_control = SampledRepeatedSource(
        control_repeated,
        control_banks,
        Dual(control_output, control_output_dot),
        control_covariance,
    )
    controlled_repeated = {
        key: Dual(
            uncontrolled.repeated[key].value - control_repeated[key].value,
            uncontrolled.repeated[key].tangent - control_repeated[key].tangent,
        )
        for key in uncontrolled.repeated
    }
    controlled_banks = tuple(
        Dual(full.value - control.value, full.tangent - control.tangent)
        for full, control in zip(uncontrolled.k3_banks, control_banks)
    )
    controlled = SampledRepeatedSource(
        controlled_repeated,
        controlled_banks,
        uncontrolled.output_samples,
        uncontrolled.output_covariance,
    )
    return FirstChaosControlledSource(controlled, uncontrolled, affine_control)


def one_delay_edgeworth_source(
    repeated: dict[str, Dual],
    affine_mean: np.ndarray,
    affine_covariance: np.ndarray,
) -> TangentState:
    """Complete linear k3/k4 one-delay ReLU mean/covariance source.

    This is the M121 repeated-slot interface.  It consumes ``aaa/aab`` and
    ``aaaa/aaab/aabb`` tables after affine projection and includes every
    symmetric tensor-slot multiplicity.  It intentionally excludes the
    quadratic ``k3^2`` M128 diagram, whose unbiased evaluation must use two
    independent banks.
    """

    required = {"k3_aaa", "k3_aab", "k4_aaaa", "k4_aaab", "k4_aabb"}
    if set(repeated) != required:
        raise ValueError("incomplete repeated cumulant table")
    mean = np.asarray(affine_mean, dtype=np.float64)
    covariance = np.asarray(affine_covariance, dtype=np.float64)
    n = mean.size
    if covariance.shape != (n, n) or not np.array_equal(covariance, covariance.T):
        raise ValueError("one-delay Gaussian state shape mismatch")
    k3_aaa = np.asarray(repeated["k3_aaa"].value, dtype=np.float64)
    k3_aab = np.asarray(repeated["k3_aab"].value, dtype=np.float64)
    k4_aaaa = np.asarray(repeated["k4_aaaa"].value, dtype=np.float64)
    k4_aaab = np.asarray(repeated["k4_aaab"].value, dtype=np.float64)
    k4_aabb = np.asarray(repeated["k4_aabb"].value, dtype=np.float64)
    if (
        k3_aaa.shape != (n,)
        or k3_aab.shape != (n, n)
        or k4_aaaa.shape != (n,)
        or k4_aaab.shape != (n, n)
        or k4_aabb.shape != (n, n)
    ):
        raise ValueError("one-delay repeated table shape mismatch")

    variance = np.diag(covariance)
    if np.any(variance <= 1.0e-12):
        raise ValueError("one-delay covariance has nonpositive variance")
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    standard_density = np.asarray([_pdf(float(item)) for item in alpha])
    probability = np.asarray([_cdf(float(item)) for item in alpha])
    gaussian_relu_mean = sigma * standard_density + mean * probability
    boundary_density = standard_density / sigma
    boundary_density_prime = mean / variance * boundary_density
    boundary_density_second = (
        mean * mean / (variance * variance) - 1.0 / variance
    ) * boundary_density

    mean_source = (
        -k3_aaa * boundary_density_prime / 6.0
        + k4_aaaa * boundary_density_second / 24.0
    )
    covariance_source = np.empty((n, n), dtype=np.float64)
    raw_diagonal = (
        k3_aaa * boundary_density / 3.0
        - k4_aaaa * boundary_density_prime / 12.0
    )
    diagonal = raw_diagonal - 2.0 * gaussian_relu_mean * mean_source
    np.fill_diagonal(covariance_source, diagonal)

    def conditional_terms(conditioning: int, target: int) -> tuple[float, ...]:
        vi = variance[conditioning]
        cij = covariance[target, conditioning]
        conditional_variance = variance[target] - cij * cij / vi
        if conditional_variance <= 1.0e-14:
            raise ValueError("one-delay conditional covariance is singular")
        conditional_sigma = math.sqrt(float(conditional_variance))
        conditional_mean = mean[target] - cij * mean[conditioning] / vi
        conditional_alpha = conditional_mean / conditional_sigma
        conditional_probability = _cdf(float(conditional_alpha))
        conditional_density = _pdf(float(conditional_alpha))
        conditional_relu_mean = (
            conditional_sigma * conditional_density
            + conditional_mean * conditional_probability
        )
        beta = cij / vi
        return (
            conditional_sigma,
            conditional_probability,
            conditional_density,
            conditional_relu_mean,
            beta,
        )

    for i in range(n):
        for j in range(i + 1, n):
            sj, pj, phij, rj, beta_j = conditional_terms(i, j)
            si, pi, phii, ri, beta_i = conditional_terms(j, i)
            d30 = -(
                boundary_density_prime[i] * rj
                + boundary_density[i] * beta_j * pj
            )
            d21 = boundary_density[i] * pj
            d12 = boundary_density[j] * pi
            d03 = -(
                boundary_density_prime[j] * ri
                + boundary_density[j] * beta_i * pi
            )
            d40 = (
                boundary_density_second[i] * rj
                + 2.0 * boundary_density_prime[i] * beta_j * pj
                + boundary_density[i] * beta_j * beta_j * phij / sj
            )
            d31 = -(
                boundary_density_prime[i] * pj
                + boundary_density[i] * beta_j * phij / sj
            )
            determinant = variance[i] * variance[j] - covariance[i, j] ** 2
            inverse_quadratic = (
                variance[j] * mean[i] ** 2
                - 2.0 * covariance[i, j] * mean[i] * mean[j]
                + variance[i] * mean[j] ** 2
            ) / determinant
            d22 = math.exp(-0.5 * inverse_quadratic) / (
                2.0 * math.pi * math.sqrt(determinant)
            )
            d13 = -(
                boundary_density_prime[j] * pi
                + boundary_density[j] * beta_i * phii / si
            )
            d04 = (
                boundary_density_second[j] * ri
                + 2.0 * boundary_density_prime[j] * beta_i * pi
                + boundary_density[j] * beta_i * beta_i * phii / si
            )
            raw_source = (
                k3_aaa[i] * d30
                + 3.0 * k3_aab[i, j] * d21
                + 3.0 * k3_aab[j, i] * d12
                + k3_aaa[j] * d03
            ) / 6.0 + (
                k4_aaaa[i] * d40
                + 4.0 * k4_aaab[i, j] * d31
                + 6.0 * k4_aabb[i, j] * d22
                + 4.0 * k4_aaab[j, i] * d13
                + k4_aaaa[j] * d04
            ) / 24.0
            central_source = (
                raw_source
                - gaussian_relu_mean[j] * mean_source[i]
                - gaussian_relu_mean[i] * mean_source[j]
            )
            covariance_source[i, j] = covariance_source[j, i] = central_source
    return TangentState(mean_source, covariance_source)


def propagate_one_delay_source(
    source: TangentState,
    suffix_weights: list[np.ndarray],
    suffix_gaussian_states: list[tuple[np.ndarray, np.ndarray]],
) -> TangentState:
    """Propagate a converted source through a complete M125b Gaussian suffix."""

    if len(suffix_weights) != len(suffix_gaussian_states):
        raise ValueError("suffix map/state length mismatch")
    result = source
    for weight, (mean, covariance) in zip(suffix_weights, suffix_gaussian_states):
        kernels = analytic_local_kernels(mean, covariance)
        jacobian = LocalReluJacobian(
            kernels.probability,
            kernels.mean_variance_derivative,
            kernels.price_kernel,
            kernels.h_mu,
            kernels.h_variance,
        )
        result = tangent_stage(result, weight, jacobian)
    return result


def antithetic_standard_samples(
    half_count_per_bank: int, width: int, bank_count: int, seed: int
) -> np.ndarray:
    """Fresh independent antithetic Gaussian banks with deterministic keys."""

    if min(half_count_per_bank, width, bank_count) <= 0:
        raise ValueError("antithetic sample dimensions must be positive")
    rng = np.random.default_rng(seed)
    banks = []
    for _ in range(bank_count):
        positive = rng.standard_normal((half_count_per_bank, width))
        banks.append(np.concatenate((positive, -positive), axis=0))
    return np.concatenate(banks, axis=0)


def gaussianized_frame_samples(
    width: int,
    bank_count: int,
    seed: int,
    *,
    design: str = "orthobasis",
    antithetic: bool = False,
) -> np.ndarray:
    """Exactly Gaussian-marginal orthogonal/simplex sample banks.

    A Haar rotation makes each structured direction marginally uniform on the
    sphere.  Multiplication by an independent ``chi_width`` radius therefore
    makes every row exactly ``N(0,I)``.  Rows remain dependent, but all source
    estimators above are linear sample averages; marginal exactness is enough
    for unbiasedness.  Separate banks use independent rotations and radii.
    """

    if width <= 1 or bank_count <= 0 or design not in {"orthobasis", "simplex"}:
        raise ValueError("invalid Gaussianized frame request")
    rng = np.random.default_rng(seed)
    if design == "simplex":
        # Helmert columns are an orthonormal basis of 1^perp in R^(n+1).
        helmert = np.zeros((width + 1, width), dtype=np.float64)
        for column in range(width):
            scale = 1.0 / math.sqrt((column + 1) * (column + 2))
            helmert[: column + 1, column] = scale
            helmert[column + 1, column] = -(column + 1) * scale
        canonical = math.sqrt((width + 1) / width) * helmert
    banks: list[np.ndarray] = []
    for _ in range(bank_count):
        gaussian = rng.standard_normal((width, width))
        rotation, upper = np.linalg.qr(gaussian)
        signs = np.where(np.diag(upper) < 0.0, -1.0, 1.0)
        rotation = rotation * signs[None, :]
        directions = rotation.T if design == "orthobasis" else canonical @ rotation
        radii = np.sqrt(rng.chisquare(width, size=directions.shape[0]))
        positive = radii[:, None] * directions
        banks.append(
            np.concatenate((positive, -positive), axis=0)
            if antithetic
            else positive
        )
    return np.concatenate(banks, axis=0)


def sampled_source_cost_envelope(
    samples_per_bank: int,
    *,
    bank_count: int = 2,
    width: int = 256,
    layers: int = 31,
    dense_dtype: str = "float32",
    safety_factor: float = 1.25,
    first_chaos_control: bool = False,
    gaussianized_design: str = "iid",
) -> dict[str, int | float | str | bool]:
    """Protected installed-style bill for the full sampled source replacement."""

    if samples_per_bank <= 0 or bank_count < 2:
        raise ValueError("at least two nonempty independent banks are required")
    if dense_dtype not in {"float32", "float64"}:
        raise ValueError("dense_dtype must be float32 or float64")
    if gaussianized_design not in {
        "iid",
        "orthobasis",
        "simplex",
        "antithetic_orthobasis",
        "antithetic_simplex",
    }:
        raise ValueError("unknown Gaussianized sampling design")
    if gaussianized_design in {"orthobasis", "antithetic_orthobasis"}:
        expected_samples = width
    else:
        expected_samples = width + 1
    if gaussianized_design.startswith("antithetic_"):
        expected_samples *= 2
    if gaussianized_design != "iid" and samples_per_bank != expected_samples:
        raise ValueError("Gaussianized frame sample count is fixed by its geometry")
    rate = 1 if dense_dtype == "float32" else 2
    total_samples = samples_per_bank * bank_count

    def rectangular(rows: int) -> int:
        return rate * (2 * rows * width * width - rows * width)

    # Base: four full-bank transforms (X, Xdot, O, Odot), three products per
    # k3 bank, and seven combined-bank k4 products.  The first-chaos control
    # reuses X/Xdot but adds P@W/Pdot@W and its own 3-bank/7-full products.
    full_bank_calls = 11
    per_bank_calls = 3
    if first_chaos_control:
        full_bank_calls += 9
        per_bank_calls += 3
    rectangular_bill_per_layer = (
        full_bank_calls * rectangular(total_samples)
        + per_bank_calls * bank_count * rectangular(samples_per_bank)
    )
    rectangular_total = layers * rectangular_bill_per_layer

    # Cholesky n^3/3 plus two n-RHS triangular solves and L@Phi, all f64.
    # Ten n^3 billed operations is a conservative shape-independent cap.
    factor_and_frechet = layers * 10 * width**3
    scalar_multiplier = 180 if first_chaos_control else 100
    scalar_and_copy = layers * (
        scalar_multiplier * total_samples * width + 140 * width**2
    )
    # One reusable Haar QR per bank/MLP.  Four n^3 f64-billed operations per
    # bank is deliberately conservative relative to square Householder QR.
    haar_setup_upper = (
        0 if gaussianized_design == "iid" else 4 * bank_count * width**3
    )
    source_raw = (
        rectangular_total
        + factor_and_frechet
        + scalar_and_copy
        + haar_setup_upper
    )
    source_protected = int(math.ceil(source_raw * safety_factor))
    protected_carrier = 16_971_970_384
    response_and_cross_bank_reserve = 1_600_000_000
    total = source_protected + protected_carrier + response_and_cross_bank_reserve
    return {
        "samples_per_bank": samples_per_bank,
        "bank_count": bank_count,
        "total_samples": total_samples,
        "dense_dtype": dense_dtype,
        "rectangular_bill_per_layer": rectangular_bill_per_layer,
        "rectangular_total": rectangular_total,
        "factor_and_frechet_f64_upper": factor_and_frechet,
        "haar_setup_f64_upper": haar_setup_upper,
        "scalar_and_copy_upper": scalar_and_copy,
        "source_raw": source_raw,
        "source_protected": source_protected,
        "protected_carrier": protected_carrier,
        "response_and_cross_bank_reserve": response_and_cross_bank_reserve,
        "complete_protected_total": total,
        "strictly_below_100b": total < 100_000_000_000,
        "replaces_m126_m129_source_calls": True,
        "first_chaos_control": first_chaos_control,
        "full_bank_rectangular_calls_per_layer": full_bank_calls,
        "per_bank_rectangular_calls_per_layer": per_bank_calls,
        "gaussianized_design": gaussianized_design,
    }
