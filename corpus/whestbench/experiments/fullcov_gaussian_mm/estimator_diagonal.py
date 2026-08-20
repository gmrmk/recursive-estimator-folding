"""Existing diagonal Gaussian moment pass as a standalone scored baseline."""

from __future__ import annotations

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP


class Estimator(BaseEstimator):
    def setup(self, ctx: SetupContext) -> None:
        _ = ctx

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        mu = fnp.zeros(mlp.width, dtype=fnp.float32)
        variance = fnp.ones(mlp.width, dtype=fnp.float32)
        means = []
        for weight in mlp.weights:
            mu_pre = mu @ weight
            variance_pre = variance @ (weight * weight)
            sigma = fnp.sqrt(fnp.maximum(variance_pre, 1e-12))
            alpha = mu_pre / sigma
            phi = flops.stats.norm.pdf(alpha)
            cdf = flops.stats.norm.cdf(alpha)
            mu = mu_pre * cdf + sigma * phi
            second = (
                (variance_pre + mu_pre * mu_pre) * cdf
                + mu_pre * sigma * phi
            )
            variance = fnp.maximum(second - mu * mu, 0.0)
            means.append(mu)
        return fnp.stack(means, axis=0)

