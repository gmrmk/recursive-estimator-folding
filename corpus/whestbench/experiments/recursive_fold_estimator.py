"""Recursive terminal dead/on/kink folding.

At each folded layer, the sampled preactivation is represented as a sum of
``basis @ transform`` terms.  Confirmed-on neurons remain linear and compose
their transforms into the next weight matrix; confirmed-dead neurons vanish;
only kink neurons materialize a new sampled ReLU basis.  This is the generic
recurrence underlying the verified two- and three-layer folds.
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
    """Frozen diagonal tangent with a configurable recursive terminal fold."""

    n_base = 14_000
    fold_depth = 3
    on_alpha = 3.0
    fold_pilot_base = 1_024

    def _weighted_mean(self, values, final_weights):
        if final_weights is None:
            return fnp.mean(values, axis=0)
        return fnp.mean(values * final_weights[:, None], axis=0)

    def predict(self, mlp, budget):
        _ = budget
        z = self._gaussian
        if z is None:
            raise RuntimeError("setup() did not initialize the Gaussian net")
        if not 2 <= self.fold_depth <= mlp.depth - 1:
            raise ValueError("fold_depth must be in [2, depth-1]")

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

        first_pre = z @ mlp.weights[0]
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

        fold_start = mlp.depth - self.fold_depth
        active = fnp.arange(mlp.width)
        for layer in range(1, fold_start):
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
                x @ mlp.weights[layer][active, :][:, next_active], 0.0
            )
            active = next_active

        pilot_n = min(self.fold_pilot_base, self.n_base)
        # Concatenating all live bases into one recurrent state keeps every
        # represented preactivation to a single sample GEMM.  The companion
        # transform is the memristive state: confirmed-on paths update it
        # linearly, while each kink phenotype appends one nonlinear basis.
        state = x
        pilot_state = fnp.concatenate(
            (x[:pilot_n], x[self.n_base : self.n_base + pilot_n]), axis=0
        )
        transform = mlp.weights[fold_start][active, :]

        def represented_pre(columns, pilot: bool):
            source = pilot_state if pilot else state
            return source @ transform[:, columns]

        # Fold all nonlinear hidden layers; the last iteration is assembled
        # separately because final on units can be averaged without samples.
        for layer in range(fold_start, mlp.depth - 1):
            dead, kink, on = _initial_regimes(
                analytic_alphas[layer], self.dead_alpha, self.on_alpha
            )
            if dead.shape[0] > 0:
                dead, rescued = _refine_dead(dead, represented_pre(dead, True))
                kink = fnp.concatenate((kink, rescued), axis=0)
            if on.shape[0] > 0:
                on, demoted = _refine_on(on, represented_pre(on, True))
                kink = fnp.concatenate((kink, demoted), axis=0)
            kink = fnp.sort(kink)

            kink_values = fnp.maximum(represented_pre(kink, False), 0.0)
            kink_pilot = fnp.concatenate(
                (
                    kink_values[:pilot_n],
                    kink_values[self.n_base : self.n_base + pilot_n],
                ),
                axis=0,
            )
            next_weight = mlp.weights[layer + 1]
            transform = fnp.concatenate(
                (
                    transform[:, on] @ next_weight[on, :],
                    next_weight[kink, :],
                ),
                axis=0,
            )
            state = fnp.concatenate((state, kink_values), axis=1)
            pilot_state = fnp.concatenate((pilot_state, kink_pilot), axis=1)

        final_layer = mlp.depth - 1
        dead, kink, on = _initial_regimes(
            analytic_alphas[final_layer], self.dead_alpha, self.on_alpha
        )
        if dead.shape[0] > 0:
            dead, rescued = _refine_dead(dead, represented_pre(dead, True))
            kink = fnp.concatenate((kink, rescued), axis=0)
        if on.shape[0] > 0:
            on, demoted = _refine_on(on, represented_pre(on, True))
            kink = fnp.concatenate((kink, demoted), axis=0)
        kink = fnp.sort(kink)

        index_parts = []
        value_parts = []
        if kink.shape[0] > 0:
            sampled = self._weighted_mean(
                fnp.maximum(represented_pre(kink, False), 0.0), final_weights
            )
            index_parts.append(kink)
            value_parts.append(sampled)
        if on.shape[0] > 0:
            mean_on = self._weighted_mean(state, final_weights) @ transform[:, on]
            index_parts.append(on)
            value_parts.append(mean_on)
        if dead.shape[0] > 0:
            index_parts.append(dead)
            value_parts.append(analytic_means[final_layer][dead])
        final_mean = _assemble_vector(index_parts, value_parts)

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

        return fnp.stack((*analytic_means[:-1], final_mean), axis=0)
