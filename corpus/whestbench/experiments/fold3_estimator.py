"""Three-terminal-layer dead/on/kink folding experiment.

This extends the independently verified two-layer fold by one layer.  Sampled
paths are still evaluated exactly within the pilot-refined regime assignment:
dead columns vanish, always-on columns remain linear and are algebraically
composed into the next weight matrix, and kink columns retain their ReLU.
"""

from __future__ import annotations

import flopscope.numpy as fnp

from base_estimator import (
    Estimator as _BaseEstimator,
    _assemble_vector,
    _diagonal_gaussian_pass,
)
from fold_estimator import _initial_regimes, _refine_dead, _refine_on


class Estimator(_BaseEstimator):
    """Frozen tangent sampler with pilot-refined final-three-layer folding."""

    n_base = 14_000
    on_alpha = 3.0
    fold_pilot_base = 1_024

    def _additional_tangent(
        self,
        mlp,
        analytic_means,
        analytic_alphas,
        firing,
        analytic_sigmas,
        first_x,
        exact_first_mean,
        first_moment_residual,
        first_variance_residual,
    ):
        """Optional centered response supplied by an experimental subclass."""
        return None

    def _weighted_mean(self, values, final_weights):
        if final_weights is None:
            return fnp.mean(values, axis=0)
        return fnp.mean(values * final_weights[:, None], axis=0)

    def _sample_matmul(self, values, weight, firing_rates):
        """Hook for an exactly equivalent structured sample product."""
        _ = firing_rates
        return values @ weight

    def _first_sample_matmul(self, values, weight):
        return values @ weight

    def predict(self, mlp, budget):
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
            final_weights = fnp.concatenate((base_weights, base_weights), axis=0)

        first_pre = self._first_sample_matmul(z, mlp.weights[0])
        x = fnp.concatenate(
            (fnp.maximum(first_pre, 0.0), fnp.maximum(-first_pre, 0.0)), axis=0
        )
        sigma0 = fnp.sqrt(fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0))
        exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
        first_moment_residual = fnp.mean(x, axis=0) - exact_first_mean
        first_variance_residual = (
            fnp.mean(x * x, axis=0)
            - 0.5 * self._radial_covariance * sigma0 * sigma0
        ) - 2.0 * exact_first_mean * first_moment_residual
        additional_tangent = self._additional_tangent(
            mlp,
            analytic_means,
            analytic_alphas,
            firing,
            analytic_sigmas,
            x,
            exact_first_mean,
            first_moment_residual,
            first_variance_residual,
        )

        # Ordinary pilot-rescued pruning through layer 29 (weight index 28).
        active = fnp.arange(mlp.width)
        for layer in range(1, mlp.depth - 3):
            structural_active = fnp.flatnonzero(
                analytic_alphas[layer] >= self.dead_alpha
            )
            cold = fnp.flatnonzero(analytic_alphas[layer] < self.dead_alpha)
            if cold.shape[0] > 0:
                pilot_x = fnp.concatenate(
                    (
                        x[: self.pilot_base],
                        x[self.n_base : self.n_base + self.pilot_base],
                    ),
                    axis=0,
                )
                pilot_pre = pilot_x @ mlp.weights[layer][active, :][:, cold]
                fired = fnp.max(pilot_pre, axis=0) > 0.0
                rescued = cold[fnp.flatnonzero(fired)]
                next_active = fnp.sort(
                    fnp.concatenate((structural_active, rescued), axis=0)
                )
            else:
                next_active = structural_active
            x = fnp.maximum(
                self._sample_matmul(
                    x,
                    mlp.weights[layer][active, :][:, next_active],
                    firing[layer - 1][active],
                ),
                0.0,
            )
            active = next_active

        pilot_n = min(self.fold_pilot_base, self.n_base)
        pilot_x29 = fnp.concatenate(
            (x[:pilot_n], x[self.n_base : self.n_base + pilot_n]), axis=0
        )

        # Layer 30: materialize only kink activations.
        layer30 = mlp.depth - 3
        dead30, kink30, on30 = _initial_regimes(
            analytic_alphas[layer30], self.dead_alpha, self.on_alpha
        )
        weight30 = mlp.weights[layer30][active, :]
        if dead30.shape[0] > 0:
            dead30, rescued30 = _refine_dead(
                dead30, pilot_x29 @ weight30[:, dead30]
            )
            kink30 = fnp.concatenate((kink30, rescued30), axis=0)
        if on30.shape[0] > 0:
            on30, demoted30 = _refine_on(
                on30, pilot_x29 @ weight30[:, on30]
            )
            kink30 = fnp.concatenate((kink30, demoted30), axis=0)
        kink30 = fnp.sort(kink30)
        x30_kink = fnp.maximum(x @ weight30[:, kink30], 0.0)
        pilot_x30_kink = fnp.concatenate(
            (
                x30_kink[:pilot_n],
                x30_kink[self.n_base : self.n_base + pilot_n],
            ),
            axis=0,
        )

        # Layer 31: on30 paths are composed through weight31.
        layer31 = mlp.depth - 2
        dead31, kink31, on31 = _initial_regimes(
            analytic_alphas[layer31], self.dead_alpha, self.on_alpha
        )
        weight31 = mlp.weights[layer31]

        def folded30_to31(columns):
            return weight30[:, on30] @ weight31[on30, :][:, columns]

        def pre31(columns, pilot: bool):
            left = pilot_x29 if pilot else x
            middle = pilot_x30_kink if pilot else x30_kink
            return (
                left @ folded30_to31(columns)
                + middle @ weight31[kink30, :][:, columns]
            )

        if dead31.shape[0] > 0:
            dead31, rescued31 = _refine_dead(dead31, pre31(dead31, True))
            kink31 = fnp.concatenate((kink31, rescued31), axis=0)
        if on31.shape[0] > 0:
            on31, demoted31 = _refine_on(on31, pre31(on31, True))
            kink31 = fnp.concatenate((kink31, demoted31), axis=0)
        kink31 = fnp.sort(kink31)
        x31_kink = fnp.maximum(pre31(kink31, False), 0.0)
        pilot_x31_kink = fnp.concatenate(
            (
                x31_kink[:pilot_n],
                x31_kink[self.n_base : self.n_base + pilot_n],
            ),
            axis=0,
        )

        # Layer 32: fold on31 paths, preserving the three live bases.
        layer32 = mlp.depth - 1
        dead32, kink32, on32 = _initial_regimes(
            analytic_alphas[layer32], self.dead_alpha, self.on_alpha
        )
        weight32 = mlp.weights[layer32]
        folded29_to31_on = folded30_to31(on31)
        kink30_to31_on = weight31[kink30, :][:, on31]

        def pre32(columns, pilot: bool):
            left = pilot_x29 if pilot else x
            middle = pilot_x30_kink if pilot else x30_kink
            right = pilot_x31_kink if pilot else x31_kink
            return (
                left
                @ (folded29_to31_on @ weight32[on31, :][:, columns])
                + middle
                @ (kink30_to31_on @ weight32[on31, :][:, columns])
                + right @ weight32[kink31, :][:, columns]
            )

        if dead32.shape[0] > 0:
            dead32, rescued32 = _refine_dead(dead32, pre32(dead32, True))
            kink32 = fnp.concatenate((kink32, rescued32), axis=0)
        if on32.shape[0] > 0:
            on32, demoted32 = _refine_on(on32, pre32(on32, True))
            kink32 = fnp.concatenate((kink32, demoted32), axis=0)
        kink32 = fnp.sort(kink32)

        index_parts = []
        value_parts = []
        if kink32.shape[0] > 0:
            sampled_kink = self._weighted_mean(
                fnp.maximum(pre32(kink32, False), 0.0), final_weights
            )
            index_parts.append(kink32)
            value_parts.append(sampled_kink)
        if on32.shape[0] > 0:
            mean_on = (
                self._weighted_mean(x, final_weights)
                @ (folded29_to31_on @ weight32[on31, :][:, on32])
                + self._weighted_mean(x30_kink, final_weights)
                @ (kink30_to31_on @ weight32[on31, :][:, on32])
                + self._weighted_mean(x31_kink, final_weights)
                @ weight32[kink31, :][:, on32]
            )
            index_parts.append(on32)
            value_parts.append(mean_on)
        if dead32.shape[0] > 0:
            index_parts.append(dead32)
            value_parts.append(analytic_means[layer32][dead32])
        final_mean = _assemble_vector(index_parts, value_parts)

        # Preserve the development-frozen first-layer diagonal tangent.
        delta_mean = first_moment_residual
        delta_var = first_variance_residual
        for layer in range(1, mlp.depth):
            weight = mlp.weights[layer]
            delta_pre_mean = delta_mean @ weight
            delta_pre_var = delta_var @ (weight * weight)
            phi = fnp.exp(-0.5 * analytic_alphas[layer] ** 2) / fnp.sqrt(
                2.0 * fnp.pi
            )
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
        final_mean = final_mean - self.moment_tangent_lambda * delta_mean
        if additional_tangent is not None:
            final_mean = final_mean - additional_tangent

        return fnp.stack((*analytic_means[:-1], final_mean), axis=0)
