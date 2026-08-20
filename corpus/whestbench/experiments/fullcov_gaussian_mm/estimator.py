"""WHestBench estimator using full-covariance Gaussian moment matching.

For each affine layer this propagates ``mu @ W`` and ``W.T @ Sigma @ W``.
It then applies the unrestricted noncentral bivariate-Gaussian ReLU moments
of Kuang & Lin (2026, Appendix E) and re-Gaussianizes.  Their prescribed
10-point Plackett/Gauss-Legendre evaluation of Phi2 is implemented entirely
with FlopScope operations; SciPy is not imported by this scored path.
"""

from __future__ import annotations

import math

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_INV_2PI = 1.0 / (2.0 * math.pi)
_GL10_X = (
    -0.9739065285171717,
    -0.8650633666889845,
    -0.6794095682990244,
    -0.4333953941292472,
    -0.1488743389816312,
    0.1488743389816312,
    0.4333953941292472,
    0.6794095682990244,
    0.8650633666889845,
    0.9739065285171717,
)
_GL10_W = (
    0.06667134430868814,
    0.1494513491505806,
    0.21908636251598204,
    0.26926671930999635,
    0.29552422471475287,
    0.29552422471475287,
    0.26926671930999635,
    0.21908636251598204,
    0.1494513491505806,
    0.06667134430868814,
)


def _normal_pdf(x):
    return fnp.exp(-0.5 * x * x) * _INV_SQRT_2PI


def _phi2_gauss10(h, k, rho, cdf_h, cdf_k):
    """Paper-prescribed fixed quadrature for the bivariate Normal CDF."""
    integral = 0.0
    for node, weight in zip(_GL10_X, _GL10_W):
        correlation = 0.5 * rho * (node + 1.0)
        one_minus_r2 = fnp.maximum(
            1.0 - correlation * correlation, 1e-24
        )
        exponent = -(
            h * h + k * k - 2.0 * correlation * h * k
        ) / (2.0 * one_minus_r2)
        density = (
            _INV_2PI * fnp.exp(exponent) / fnp.sqrt(one_minus_r2)
        )
        integral = integral + weight * density
    return cdf_h * cdf_k + 0.5 * rho * integral


def _relu_fullcov(mu, covariance, off_diagonal):
    """Elementwise ReLU mean and full covariance for one Gaussian layer."""
    variance = fnp.maximum(fnp.diag(covariance), 1e-24)
    sigma = fnp.sqrt(variance)
    alpha = mu / sigma
    phi = _normal_pdf(alpha)
    cdf = flops.stats.norm.cdf(alpha)
    mean = sigma * phi + mu * cdf

    sigma_outer = flops.as_symmetric(
        fnp.outer(sigma, sigma), symmetry=(0, 1)
    )
    # Diagonal bivariate moments are singular representations of an ordinary
    # univariate moment.  Zero them during the bivariate calculation and
    # replace them exactly below.
    rho = flops.as_symmetric(
        fnp.clip(covariance / sigma_outer, -1.0 + 1e-12, 1.0 - 1e-12)
        * off_diagonal,
        symmetry=(0, 1),
    )
    one_minus_r2 = flops.as_symmetric(
        fnp.maximum(1.0 - rho * rho, 1e-24), symmetry=(0, 1)
    )
    root = fnp.sqrt(one_minus_r2)
    a = alpha[:, None]
    b = alpha[None, :]
    cdf_a = cdf[:, None]
    cdf_b = cdf[None, :]

    joint_cdf = flops.as_symmetric(
        _phi2_gauss10(a, b, rho, cdf_a, cdf_b), symmetry=(0, 1)
    )
    partial_a = _normal_pdf(a) * flops.stats.norm.cdf(
        (b - rho * a) / root
    )
    # Phi2;1(b,a;rho) at (i,j) is the transpose of Phi2;1(a,b;rho).
    partial_b = partial_a.T
    joint_pdf = flops.as_symmetric(
        _INV_2PI
        * fnp.exp(
            -(a * a + b * b - 2.0 * rho * a * b)
            / (2.0 * one_minus_r2)
        )
        / root,
        symmetry=(0, 1),
    )

    mu1 = mu[:, None]
    mu2 = mu[None, :]
    sigma1 = sigma[:, None]
    sigma2 = sigma[None, :]
    raw_second = (
        mu2 * sigma1 * partial_a
        + mu1 * sigma2 * partial_b
        + sigma_outer * one_minus_r2 * joint_pdf
        + (mu1 * mu2 + covariance) * joint_cdf
    )
    next_covariance = 0.5 * (
        raw_second - fnp.outer(mean, mean)
        + (raw_second - fnp.outer(mean, mean)).T
    )
    exact_second = (
        (variance + mu * mu) * cdf + mu * sigma * phi
    )
    fnp.fill_diagonal(next_covariance, exact_second - mean * mean)
    next_covariance = flops.as_symmetric(
        next_covariance, symmetry=(0, 1)
    )
    return mean, next_covariance


class Estimator(BaseEstimator):
    """Deterministic full-covariance Gaussian closure."""

    def __init__(self) -> None:
        self._off_diagonal = None

    def setup(self, ctx: SetupContext) -> None:
        self._off_diagonal = (
            1.0 - fnp.eye(ctx.width, dtype=fnp.float64)
        )

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        off_diagonal = self._off_diagonal
        if off_diagonal is None:
            raise RuntimeError("setup() must be called before predict()")

        mu = fnp.zeros(mlp.width, dtype=fnp.float64)
        covariance = fnp.eye(mlp.width, dtype=fnp.float64)
        means = []
        for weight in mlp.weights:
            weight64 = weight.astype(fnp.float64)
            mu_pre = mu @ weight64
            covariance_pre = flops.as_symmetric(
                weight64.T @ (covariance @ weight64), symmetry=(0, 1)
            )
            mu, covariance = _relu_fullcov(
                mu_pre, covariance_pre, off_diagonal
            )
            means.append(mu)
        return fnp.stack(means, axis=0)

