"""Late-layer dead/on/kink folding experiment.

The first thirty layers use the frozen Sobol-antipodal sampler.  At layer 31,
pilot-confirmed always-on units are composed through the final weight matrix
without materializing their sampled activation columns.  Pilot-confirmed
always-on final units are integrated linearly; only kink outputs receive a
sampled final ReLU.  This is an independently implemented, rules-compliant
test of the structure-aware family disclosed by Team SOX.
"""

from __future__ import annotations

import flopscope.numpy as fnp

from base_estimator import (
    Estimator as _BaseEstimator,
    _assemble_vector,
    _diagonal_gaussian_pass,
)


def _initial_regimes(alpha, dead_alpha: float, on_alpha: float):
    dead = fnp.flatnonzero(alpha < dead_alpha)
    on = fnp.flatnonzero(alpha > on_alpha)
    kink = fnp.flatnonzero(
        fnp.logical_and(alpha >= dead_alpha, alpha <= on_alpha)
    )
    return dead, kink, on


def _refine_dead(dead, pilot_pre):
    if dead.shape[0] == 0:
        return dead, dead
    fired = fnp.max(pilot_pre, axis=0) > 0.0
    rescued = dead[fnp.flatnonzero(fired)]
    confirmed = dead[fnp.flatnonzero(~fired)]
    return confirmed, rescued


def _refine_on(on, pilot_pre):
    if on.shape[0] == 0:
        return on, on
    crossed = fnp.min(pilot_pre, axis=0) <= 0.0
    demoted = on[fnp.flatnonzero(crossed)]
    confirmed = on[fnp.flatnonzero(~crossed)]
    return confirmed, demoted


class Estimator(_BaseEstimator):
    """Frozen tangent sampler with pilot-verified final-two-layer folding."""

    n_base = 14_000
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
        sigma0 = fnp.sqrt(fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0))
        exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
        first_moment_residual = fnp.mean(x, axis=0) - exact_first_mean
        first_variance_residual = (
            fnp.mean(x * x, axis=0)
            - 0.5 * self._radial_covariance * sigma0 * sigma0
        ) - 2.0 * exact_first_mean * first_moment_residual

        # Ordinary pruned propagation through layer 30 (weight index 29).
        active = fnp.arange(mlp.width)
        for layer in range(1, mlp.depth - 2):
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

        # Layer 31: verify the analytical regimes on a reused Sobol prefix.
        layer31 = mlp.depth - 2
        dead31, kink31, on31 = _initial_regimes(
            analytic_alphas[layer31], self.dead_alpha, self.on_alpha
        )
        pilot_n = min(self.fold_pilot_base, self.n_base)
        pilot_x30 = fnp.concatenate(
            (x[:pilot_n], x[self.n_base : self.n_base + pilot_n]), axis=0
        )
        weight31 = mlp.weights[layer31][active, :]
        if dead31.shape[0] > 0:
            dead31, rescued31 = _refine_dead(
                dead31, pilot_x30 @ weight31[:, dead31]
            )
            kink31 = fnp.concatenate((kink31, rescued31), axis=0)
        if on31.shape[0] > 0:
            on31, demoted31 = _refine_on(
                on31, pilot_x30 @ weight31[:, on31]
            )
            kink31 = fnp.concatenate((kink31, demoted31), axis=0)
        kink31 = fnp.sort(kink31)
        x31_kink = fnp.maximum(x @ weight31[:, kink31], 0.0)
        pilot_x31_kink = fnp.concatenate(
            (
                x31_kink[:pilot_n],
                x31_kink[self.n_base : self.n_base + pilot_n],
            ),
            axis=0,
        )

        # Layer 32: refine output regimes using the folded pilot preactivation.
        layer32 = mlp.depth - 1
        dead32, kink32, on32 = _initial_regimes(
            analytic_alphas[layer32], self.dead_alpha, self.on_alpha
        )
        weight32 = mlp.weights[layer32]

        def pilot_final_pre(columns):
            folded = weight31[:, on31] @ weight32[on31, :][:, columns]
            return (
                pilot_x30 @ folded
                + pilot_x31_kink @ weight32[kink31, :][:, columns]
            )

        if dead32.shape[0] > 0:
            dead32, rescued32 = _refine_dead(
                dead32, pilot_final_pre(dead32)
            )
            kink32 = fnp.concatenate((kink32, rescued32), axis=0)
        if on32.shape[0] > 0:
            on32, demoted32 = _refine_on(on32, pilot_final_pre(on32))
            kink32 = fnp.concatenate((kink32, demoted32), axis=0)
        kink32 = fnp.sort(kink32)

        index_parts = []
        value_parts = []
        if kink32.shape[0] > 0:
            folded_kink = weight31[:, on31] @ weight32[on31, :][:, kink32]
            pre32_kink = (
                x @ folded_kink
                + x31_kink @ weight32[kink31, :][:, kink32]
            )
            sampled_kink = self._weighted_mean(
                fnp.maximum(pre32_kink, 0.0), final_weights
            )
            index_parts.append(kink32)
            value_parts.append(sampled_kink)
        if on32.shape[0] > 0:
            folded_on = weight31[:, on31] @ weight32[on31, :][:, on32]
            mean_on = (
                self._weighted_mean(x, final_weights) @ folded_on
                + self._weighted_mean(x31_kink, final_weights)
                @ weight32[kink31, :][:, on32]
            )
            index_parts.append(on32)
            value_parts.append(mean_on)
        if dead32.shape[0] > 0:
            index_parts.append(dead32)
            value_parts.append(analytic_means[layer32][dead32])
        final_mean = _assemble_vector(index_parts, value_parts)

        # Preserve the development-frozen first-layer tangent control.
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
