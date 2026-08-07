"""Formula-first tests for full-covariance Gaussian ReLU moments.

SciPy is deliberately confined to this unscored validation suite.  The
estimator implementation must use only FlopScope-compatible operations.
"""

from __future__ import annotations

import math
import unittest

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr
from scipy.stats import multivariate_normal

from fullcov import phi2_gauss10, relu_gaussian_moments


INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def normal_pdf(x):
    return np.exp(-0.5 * np.asarray(x) ** 2) * INV_SQRT_2PI


def relu_mean(mu, sigma):
    alpha = mu / sigma
    return sigma * normal_pdf(alpha) + mu * ndtr(alpha)


def conditional_relu_product(mu1, mu2, sigma1, sigma2, rho):
    """Independent 1-D quadrature reference for E[X_+ Y_+]."""
    conditional_sigma = sigma2 * math.sqrt(1.0 - rho * rho)

    def integrand(x):
        z = (x - mu1) / sigma1
        density = normal_pdf(z) / sigma1
        conditional_mu = mu2 + rho * sigma2 * z
        return x * density * relu_mean(conditional_mu, conditional_sigma)

    value, error = quad(integrand, 0.0, np.inf, epsabs=2e-12, epsrel=2e-12)
    if error > 1e-9:
        raise AssertionError(f"reference quadrature error too large: {error}")
    return value


class Phi2Tests(unittest.TestCase):
    def test_independence_is_exact(self):
        h = np.array([-2.0, -0.4, 0.0, 0.7, 2.5])
        k = np.array([1.1, -1.5, 0.0, 0.2, -0.3])
        got = phi2_gauss10(h, k, np.zeros_like(h))
        np.testing.assert_allclose(got, ndtr(h) * ndtr(k), rtol=0.0, atol=2e-15)

    def test_against_scipy_on_controlled_grid(self):
        cases = [
            (-2.0, -1.0, -0.75),
            (-1.5, 0.4, 0.65),
            (-0.2, 1.7, -0.5),
            (0.0, 0.0, 0.9),
            (0.8, -0.7, 0.25),
            (2.0, 1.0, -0.8),
        ]
        for h, k, rho in cases:
            expected = multivariate_normal.cdf(
                [h, k], mean=[0.0, 0.0], cov=[[1.0, rho], [rho, 1.0]]
            )
            got = float(phi2_gauss10(h, k, rho))
            # This is the authors' deliberately fixed 10-node rule, not an
            # adaptive SciPy integral.  The worst controlled-grid error is
            # about 5.2e-8 at rho=0.9.
            self.assertAlmostEqual(got, expected, delta=6e-8)


class ReluMomentTests(unittest.TestCase):
    def test_diagonal_is_exact_univariate_formula(self):
        mu = np.array([-1.3, -0.2, 0.0, 0.8, 2.2])
        variance = np.array([0.3, 1.7, 0.5, 2.0, 0.9])
        covariance = np.diag(variance)
        mean, cov = relu_gaussian_moments(mu, covariance)

        sigma = np.sqrt(variance)
        alpha = mu / sigma
        expected_mean = sigma * normal_pdf(alpha) + mu * ndtr(alpha)
        expected_second = (
            (variance + mu * mu) * ndtr(alpha)
            + mu * sigma * normal_pdf(alpha)
        )
        np.testing.assert_allclose(mean, expected_mean, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(
            np.diag(cov), expected_second - expected_mean**2,
            rtol=1e-12, atol=1e-12,
        )

    def test_independent_coordinates_have_zero_covariance(self):
        mu = np.array([-0.7, 0.3, 1.2])
        covariance = np.diag([0.5, 1.7, 0.9])
        _, cov = relu_gaussian_moments(mu, covariance)
        offdiag = cov - np.diag(np.diag(cov))
        np.testing.assert_allclose(offdiag, 0.0, rtol=0.0, atol=2e-14)

    def test_zero_mean_matches_arccosine_kernel(self):
        rho = np.array(
            [[1.0, -0.8, 0.2], [-0.8, 1.0, 0.65], [0.2, 0.65, 1.0]]
        )
        sigma = np.array([0.7, 1.4, 2.1])
        covariance = rho * np.outer(sigma, sigma)
        mean, cov = relu_gaussian_moments(np.zeros(3), covariance)
        raw = cov + np.outer(mean, mean)
        expected = np.outer(sigma, sigma) * (
            np.sqrt(np.maximum(1.0 - rho * rho, 0.0))
            + (math.pi - np.arccos(rho)) * rho
        ) / (2.0 * math.pi)
        np.testing.assert_allclose(raw, expected, rtol=2e-10, atol=2e-10)

    def test_general_noncentral_cross_moments_against_quad(self):
        cases = [
            (-0.8, 0.4, 0.7, 1.3, -0.6),
            (0.5, -1.1, 1.5, 0.8, 0.45),
            (1.2, 0.9, 0.6, 1.8, 0.8),
            (-1.4, -0.3, 1.1, 0.5, 0.2),
        ]
        for mu1, mu2, sigma1, sigma2, rho in cases:
            mu = np.array([mu1, mu2])
            covariance = np.array(
                [
                    [sigma1 * sigma1, rho * sigma1 * sigma2],
                    [rho * sigma1 * sigma2, sigma2 * sigma2],
                ]
            )
            mean, cov = relu_gaussian_moments(mu, covariance)
            got = cov[0, 1] + mean[0] * mean[1]
            expected = conditional_relu_product(
                mu1, mu2, sigma1, sigma2, rho
            )
            self.assertAlmostEqual(float(got), expected, delta=4e-8)

    def test_covariance_is_symmetric(self):
        mu = np.array([0.4, -0.8, 1.1])
        covariance = np.array(
            [[1.3, 0.4, -0.2], [0.4, 0.9, 0.1], [-0.2, 0.1, 1.7]]
        )
        _, cov = relu_gaussian_moments(mu, covariance)
        np.testing.assert_allclose(cov, cov.T, rtol=0.0, atol=2e-14)


if __name__ == "__main__":
    unittest.main()
