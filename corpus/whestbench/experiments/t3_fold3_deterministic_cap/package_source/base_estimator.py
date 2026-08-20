"""Self-contained WHestBench Phase-II estimator.

The scored final layer combines an LMS+shift-scrambled Sobol sequence prefix,
antithetic Gaussianized inputs, an exact spectral radial control,
empirically pilot-rescued sparsification, and a development-frozen
moment-tangent control.  The pruning heuristic is deliberately biased; the
tangent control is centered only under the ideal continuous-Gaussian
randomization.  Intermediate rows are ordinary analytic mean-propagation
estimates and never carry research telemetry.
"""

from __future__ import annotations

import math
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP


def _diagonal_gaussian_pass(mlp: MLP):
    """Propagate diagonal Gaussian moments and ReLU firing probabilities."""
    mu = fnp.zeros(mlp.width, dtype=fnp.float32)
    var = fnp.ones(mlp.width, dtype=fnp.float32)
    means = []
    alphas = []
    firing = []
    sigmas = []
    for weight in mlp.weights:
        mu_pre = mu @ weight
        var_pre = var @ (weight * weight)
        sigma = fnp.sqrt(fnp.maximum(var_pre, 1e-12))
        alpha = mu_pre / sigma
        phi = flops.stats.norm.pdf(alpha)
        cdf = flops.stats.norm.cdf(alpha)
        mu = mu_pre * cdf + sigma * phi
        second = (
            (var_pre + mu_pre * mu_pre) * cdf
            + mu_pre * sigma * phi
        )
        var = fnp.maximum(second - mu * mu, 0.0)
        means.append(mu)
        alphas.append(alpha)
        firing.append(cdf)
        sigmas.append(sigma)
    return means, alphas, firing, sigmas


def _assemble_vector(index_parts, value_parts):
    """Assemble disjoint vector slices without mutating a tracked array."""
    packed_indices = fnp.concatenate(index_parts, axis=0)
    packed_values = fnp.concatenate(value_parts, axis=0)
    return packed_values[fnp.argsort(packed_indices)]


class Estimator(BaseEstimator):
    """Randomized Sobol-antipodal pilot rescue with tangent correction."""

    n_base = 14_000
    pilot_base = 256
    dead_alpha = -2.0
    moment_tangent_lambda = 0.9807112198896164
    # Full800 development testing rejected spherical-radial conditioning.
    radial_conditioning = False

    def __init__(self) -> None:
        self._gaussian = None
        self._radial_covariance = 1.0

    def setup(self, ctx: SetupContext) -> None:
        if ctx.submission_dir is None:
            raise RuntimeError("submission_dir is required to load Sobol points")
        archive_path = Path(ctx.submission_dir) / "sobol_owen_u32.npz"
        raw = fnp.load(str(archive_path))["points"][: self.n_base, : ctx.width]
        if raw.shape != (self.n_base, ctx.width):
            raise ValueError(
                f"Sobol asset shape {raw.shape}, expected "
                f"({self.n_base}, {ctx.width})"
            )

        rng = fnp.random.default_rng(ctx.seed)
        shift = rng.integers(
            0, 2**32, size=(ctx.width,), dtype=fnp.uint32
        )
        shifted = fnp.bitwise_xor(raw, shift)
        uniform = (shifted.astype(fnp.float64) + 0.5) / float(2**32)
        u_radius = uniform[:, 0::2]
        u_angle = uniform[:, 1::2]
        radius = fnp.sqrt(-2.0 * fnp.log(u_radius))
        angle = (2.0 * fnp.pi) * u_angle
        pairs = fnp.stack(
            (radius * fnp.cos(angle), radius * fnp.sin(angle)), axis=2
        )
        gaussian = pairs.reshape(uniform.shape).astype(fnp.float32)

        if self.radial_conditioning:
            mean_radius = math.exp(
                0.5 * math.log(2.0)
                + math.lgamma((ctx.width + 1.0) / 2.0)
                - math.lgamma(ctx.width / 2.0)
            )
            radii = fnp.sqrt(fnp.sum(gaussian * gaussian, axis=1))
            gaussian = gaussian * (
                mean_radius / fnp.maximum(radii, 1e-12)
            )[:, None]
            self._radial_covariance = mean_radius * mean_radius / ctx.width
        self._gaussian = gaussian

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        z = self._gaussian
        if z is None:
            raise RuntimeError("setup() did not initialize the Gaussian net")

        analytic_means, analytic_alphas, firing, analytic_sigmas = (
            _diagonal_gaussian_pass(mlp)
        )
        if self.radial_conditioning:
            final_weights = None
        else:
            radius_sq = fnp.sum(z * z, axis=1)
            q1 = radius_sq - 257.0
            q2 = radius_sq * radius_sq - 66563.0
            base_weights = (
                1.0
                - (2600.0 / 537689.0) * q1
                + (3.0 / 537689.0) * q2
            )
            final_weights = fnp.concatenate(
                (base_weights, base_weights), axis=0
            )

        first_pre = z @ mlp.weights[0]
        x = fnp.concatenate(
            (fnp.maximum(first_pre, 0.0), fnp.maximum(-first_pre, 0.0)),
            axis=0,
        )
        sigma0 = fnp.sqrt(
            fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0)
        )
        exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
        first_moment_residual = fnp.mean(x, axis=0) - exact_first_mean
        first_variance_residual = (
            fnp.mean(x * x, axis=0)
            - 0.5 * self._radial_covariance * sigma0 * sigma0
        ) - 2.0 * exact_first_mean * first_moment_residual

        active = fnp.arange(mlp.width)
        final_mean = None
        for layer in range(1, mlp.depth):
            structural_active = fnp.flatnonzero(
                analytic_alphas[layer] >= self.dead_alpha
            )
            cold = fnp.flatnonzero(
                analytic_alphas[layer] < self.dead_alpha
            )
            if cold.shape[0] > 0:
                pilot_x = fnp.concatenate(
                    (
                        x[: self.pilot_base],
                        x[self.n_base : self.n_base + self.pilot_base],
                    ),
                    axis=0,
                )
                pilot_pre = (
                    pilot_x @ mlp.weights[layer][active, :][:, cold]
                )
                fired = fnp.max(pilot_pre, axis=0) > 0.0
                rescued = cold[fnp.flatnonzero(fired)]
                next_dead = cold[fnp.flatnonzero(~fired)]
                next_active = fnp.sort(
                    fnp.concatenate(
                        (structural_active, rescued), axis=0
                    )
                )
            else:
                next_active = structural_active
                next_dead = cold

            x = fnp.maximum(
                x @ mlp.weights[layer][active, :][:, next_active],
                0.0,
            )
            active = next_active
            if layer == mlp.depth - 1:
                if final_weights is None:
                    sampled = fnp.mean(x, axis=0)
                else:
                    sampled = fnp.mean(
                        x * final_weights[:, None], axis=0
                    )
                index_parts = [active]
                value_parts = [sampled]
                if next_dead.shape[0] > 0:
                    index_parts.append(next_dead)
                    value_parts.append(analytic_means[layer][next_dead])
                final_mean = _assemble_vector(index_parts, value_parts)

        if final_mean is None:
            raise RuntimeError("final layer was not evaluated")

        delta_mean = first_moment_residual
        delta_var = first_variance_residual
        for layer in range(1, mlp.depth):
            weight = mlp.weights[layer]
            delta_pre_mean = delta_mean @ weight
            delta_pre_var = delta_var @ (weight * weight)
            phi = fnp.exp(
                -0.5 * analytic_alphas[layer] ** 2
            ) / fnp.sqrt(2.0 * fnp.pi)
            next_delta_mean = (
                firing[layer] * delta_pre_mean
                + (phi / (2.0 * analytic_sigmas[layer])) * delta_pre_var
            )
            layer_mean = analytic_means[layer]
            next_delta_var = (
                2.0 * layer_mean * delta_pre_mean
                + firing[layer] * delta_pre_var
                - 2.0 * layer_mean * next_delta_mean
            )
            delta_mean = next_delta_mean
            delta_var = next_delta_var
        final_mean = (
            final_mean - self.moment_tangent_lambda * delta_mean
        )

        return fnp.stack((*analytic_means[:-1], final_mean), axis=0)
