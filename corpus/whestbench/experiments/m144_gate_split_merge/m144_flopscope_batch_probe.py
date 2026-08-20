"""Literal synthetic-cost probe for the M144 K-component kernel.

This deliberately does *not* load WHest MLPs or compare predictions.  It
executes the exact array-operation skeleton on synthetic finite arrays to make
the FlopScope bill and residual-call count auditable before any accuracy work.
"""

from __future__ import annotations

import json
import math
import sys

import flopscope as flops
import flopscope.numpy as fnp


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_INV_2PI = 1.0 / (2.0 * math.pi)
_GL10_X = (
    -0.9739065285171717, -0.8650633666889845, -0.6794095682990244,
    -0.4333953941292472, -0.1488743389816312, 0.1488743389816312,
    0.4333953941292472, 0.6794095682990244, 0.8650633666889845,
    0.9739065285171717,
)
_GL10_W = (
    0.06667134430868814, 0.1494513491505806, 0.21908636251598204,
    0.26926671930999635, 0.29552422471475287, 0.29552422471475287,
    0.26926671930999635, 0.21908636251598204, 0.1494513491505806,
    0.06667134430868814,
)


def _pdf(x):
    return fnp.exp(-0.5 * x * x) * _INV_SQRT_2PI


def _batch_relu_fullcov(mean, covariance, eye):
    """The existing exact GL10 Gaussian ReLU map, vectorized in batch axis 0."""
    variance = fnp.maximum(fnp.diagonal(covariance, axis1=-2, axis2=-1), 1e-24)
    sigma = fnp.sqrt(variance)
    alpha = mean / sigma
    phi = _pdf(alpha)
    cdf = flops.stats.norm.cdf(alpha)
    output_mean = sigma * phi + mean * cdf
    sigma_outer = sigma[:, :, None] * sigma[:, None, :]
    rho = fnp.clip(covariance / sigma_outer, -1.0 + 1e-12, 1.0 - 1e-12)
    rho = rho * (1.0 - eye)[None, :, :]
    one_minus_r2 = fnp.maximum(1.0 - rho * rho, 1e-24)
    root = fnp.sqrt(one_minus_r2)
    a, b = alpha[:, :, None], alpha[:, None, :]
    cdf_a, cdf_b = cdf[:, :, None], cdf[:, None, :]
    integral = 0.0
    for node, weight in zip(_GL10_X, _GL10_W, strict=True):
        corr = 0.5 * rho * (node + 1.0)
        one_minus_corr2 = fnp.maximum(1.0 - corr * corr, 1e-24)
        exponent = -(a * a + b * b - 2.0 * corr * a * b) / (2.0 * one_minus_corr2)
        integral = integral + weight * _INV_2PI * fnp.exp(exponent) / fnp.sqrt(one_minus_corr2)
    joint_cdf = cdf_a * cdf_b + 0.5 * rho * integral
    partial_a = _pdf(a) * flops.stats.norm.cdf((b - rho * a) / root)
    partial_b = fnp.swapaxes(partial_a, -1, -2)
    joint_pdf = _INV_2PI * fnp.exp(
        -(a * a + b * b - 2.0 * rho * a * b) / (2.0 * one_minus_r2)
    ) / root
    mu1, mu2 = mean[:, :, None], mean[:, None, :]
    sigma1, sigma2 = sigma[:, :, None], sigma[:, None, :]
    raw_second = (
        mu2 * sigma1 * partial_a
        + mu1 * sigma2 * partial_b
        + sigma_outer * one_minus_r2 * joint_pdf
        + (mu1 * mu2 + covariance) * joint_cdf
    )
    base_covariance = raw_second - output_mean[:, :, None] * output_mean[:, None, :]
    output_covariance = 0.5 * (base_covariance + fnp.swapaxes(base_covariance, -1, -2))
    exact_second = (variance + mean * mean) * cdf + mean * sigma * phi
    current_diag = fnp.diagonal(output_covariance, axis1=-2, axis2=-1)
    output_covariance = output_covariance + (
        (exact_second - output_mean * output_mean - current_diag)[:, :, None]
        * eye[None, :, :]
    )
    return output_mean, output_covariance


def _probe(cap: int) -> dict:
    width, depth, children_per_parent = 256, 32, 2
    children = cap * children_per_parent
    rng = fnp.random.default_rng(144)
    weights = [
        fnp.asarray(rng.standard_normal((width, width)), dtype=fnp.float64)
        for _ in range(depth)
    ]
    eye = fnp.eye(width, dtype=fnp.float64)
    means = fnp.zeros((cap, width), dtype=fnp.float64)
    covariances = fnp.broadcast_to(eye, (cap, width, width)).copy()
    # These fixed exact truncated-normal constants supply a two-bin split.
    shift = math.sqrt(2.0 / math.pi)
    conditional_variance_shift = -2.0 / math.pi
    flops.budget_reset()
    with flops.budget(272_000_000_000, quiet=True):
        for weight in weights:
            pre_means = means @ weight
            right = covariances @ weight
            pre_covariances = flops.as_symmetric(
                fnp.matmul(weight.T, right), symmetry=(1, 2)
            )
            variance = fnp.maximum(
                fnp.diagonal(pre_covariances, axis1=-2, axis2=-1), 1e-24
            )
            sigma = fnp.sqrt(variance)
            density = _pdf(pre_means / sigma)
            correlation = pre_covariances / (sigma[:, :, None] * sigma[:, None, :])
            # Fixed gauge-invariant ridge: R has unit diagonal by construction.
            direction_y = fnp.linalg.solve(
                correlation + 1e-6 * eye[None, :, :], density[:, :, None]
            )[:, :, 0]
            direction = direction_y / sigma
            cov_direction = fnp.matmul(pre_covariances, direction[:, :, None])[:, :, 0]
            direction_variance = fnp.sum(direction * cov_direction, axis=-1)
            standardized = cov_direction / fnp.sqrt(direction_variance)[:, None]
            plus_mean = pre_means + shift * standardized
            minus_mean = pre_means - shift * standardized
            child_means = fnp.concatenate((plus_mean, minus_mean), axis=0)
            rank_one = standardized[:, :, None] * standardized[:, None, :]
            child_covariances = fnp.concatenate(
                (
                    pre_covariances + conditional_variance_shift * rank_one,
                    pre_covariances + conditional_variance_shift * rank_one,
                ),
                axis=0,
            )
            rectified_means, rectified_covariances = _batch_relu_fullcov(
                child_means, child_covariances, eye
            )
            # Exact sibling merge of first two moments: each output label gets
            # the two children born from the same input component.
            left_mean, right_mean = rectified_means[:cap], rectified_means[cap:]
            merged_means = 0.5 * (left_mean + right_mean)
            delta_left = left_mean - merged_means
            delta_right = right_mean - merged_means
            covariances = 0.5 * (
                rectified_covariances[:cap]
                + rectified_covariances[cap:]
                + delta_left[:, :, None] * delta_left[:, None, :]
                + delta_right[:, :, None] * delta_right[:, None, :]
            )
            means = merged_means
    answer = flops.budget_summary_dict()
    answer["configuration"] = {
        "cap": cap,
        "children_per_parent": children_per_parent,
        "children": children,
        "width": width,
        "depth": depth,
        "dtype": "float64",
        "synthetic_cost_only": True,
    }
    return answer


if __name__ == "__main__":
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    print(json.dumps(_probe(cap), indent=2, sort_keys=True))
