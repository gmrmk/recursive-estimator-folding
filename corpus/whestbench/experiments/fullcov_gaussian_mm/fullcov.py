"""Full-covariance Gaussian moment matching for ReLU.

This unscored NumPy reference follows Kuang & Lin (2026), Appendix E.  The
bivariate Normal CDF uses their Appendix B implementation prescription:
ten-point Gauss-Legendre quadrature of Plackett's derivative from correlation
zero to ``rho``.
"""

from __future__ import annotations

import math

import numpy as np


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_INV_2PI = 1.0 / (2.0 * math.pi)
_GL10_X, _GL10_W = np.polynomial.legendre.leggauss(10)


def _normal_pdf(x):
    x = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * x * x) * _INV_SQRT_2PI


def _normal_cdf(x):
    x = np.asarray(x, dtype=np.float64)
    flat = x.reshape(-1)
    values = np.fromiter(
        (0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return values.reshape(x.shape)


def phi2_gauss10(h, k, rho):
    """Approximate ``Phi_2(h, k; rho)`` with the paper's 10-point rule."""
    h, k, rho = np.broadcast_arrays(
        np.asarray(h, dtype=np.float64),
        np.asarray(k, dtype=np.float64),
        np.asarray(rho, dtype=np.float64),
    )
    # The proper integral becomes singular only at |rho|=1.  ReLU covariance
    # diagonals are replaced by exact univariate moments by the caller.
    safe_rho = np.clip(rho, -1.0 + 1e-12, 1.0 - 1e-12)
    r = 0.5 * safe_rho[..., None] * (_GL10_X + 1.0)
    one_minus_r2 = np.maximum(1.0 - r * r, 1e-300)
    exponent = -(
        h[..., None] ** 2
        + k[..., None] ** 2
        - 2.0 * r * h[..., None] * k[..., None]
    ) / (2.0 * one_minus_r2)
    density = _INV_2PI * np.exp(exponent) / np.sqrt(one_minus_r2)
    integral = 0.5 * safe_rho * np.sum(density * _GL10_W, axis=-1)
    return _normal_cdf(h) * _normal_cdf(k) + integral


def relu_gaussian_moments(mu, covariance):
    """Return mean and full covariance of elementwise ReLU of a Gaussian."""
    mu = np.asarray(mu, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if covariance.shape != (mu.size, mu.size):
        raise ValueError("covariance shape must be (len(mu), len(mu))")

    variance = np.maximum(np.diag(covariance), 1e-24)
    sigma = np.sqrt(variance)
    alpha = mu / sigma
    phi = _normal_pdf(alpha)
    cdf = _normal_cdf(alpha)
    mean = sigma * phi + mu * cdf

    sigma_outer = np.outer(sigma, sigma)
    rho = np.clip(covariance / sigma_outer, -1.0 + 1e-12, 1.0 - 1e-12)
    one_minus_r2 = np.maximum(1.0 - rho * rho, 1e-24)
    root = np.sqrt(one_minus_r2)
    a = alpha[:, None]
    b = alpha[None, :]
    phi_a = phi[:, None]
    phi_b = phi[None, :]

    joint_cdf = phi2_gauss10(a, b, rho)
    partial_a = phi_a * _normal_cdf((b - rho * a) / root)
    partial_b = phi_b * _normal_cdf((a - rho * b) / root)
    joint_pdf = _INV_2PI * np.exp(
        -(a * a + b * b - 2.0 * rho * a * b) /
        (2.0 * one_minus_r2)
    ) / root

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
    output_covariance = raw_second - np.outer(mean, mean)

    # The bivariate representation is singular on i=j; use the exact
    # univariate truncated-Normal second moment there.
    second = (variance + mu * mu) * cdf + mu * sigma * phi
    np.fill_diagonal(output_covariance, second - mean * mean)
    output_covariance = 0.5 * (output_covariance + output_covariance.T)
    return mean, output_covariance

