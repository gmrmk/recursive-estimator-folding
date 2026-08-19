"""Three-terminal-layer dead/on/kink folding estimator, fold-floor fork.

Forked from ``row_blocked_production/candidate_source/fold3_estimator.py``.
Four changes, each behind a named flag, each exact up to reassociation:

``FOLD_PRODUCTS_THROUGH_OPERATOR``
    The incumbent routes only the two sample-path products through the
    Winograd hook and leaves the fold's own full-height products (``x @
    weight30``, ``pre31``, ``pre32``, and the three weighted means) on the
    direct ``@``.  Those are 64,512-row products at the same widths, so they
    are worth exactly as much to the operator as the layer loop is.  They are
    routed through the same hook here.

``HOIST_FOLDED_WEIGHT_STACK``  (suite_03: build a weight-side array once)
    ``folded30_to31(columns)`` and ``weight32[on31, :][:, columns]`` are pure
    functions of the weights, and the incumbent evaluates each of them three
    or four times, once per regime's column set.  Their column sets partition
    the width, so evaluating them once at full width and slicing computes the
    same entries and drops the duplicate evaluations.

``USE_CRELU_SPLIT``  (suite_02 / suite_08: direct-top, subtracted antipode)
    The design is antipodally doubled and the net is bias-free, so the first
    hidden layer's 64,512 rows are 32,256 antipodal pairs:  with ``z`` the
    first preactivation, ``x = [relu(z); relu(-z)]`` and

        x @ W  =  [ t ; t - o ],   t = relu(z) @ W,   o = z @ W

    exactly.  DEFAULT OFF, and the reason is measured rather than assumed:
    the suite's win comes from ``o`` being a phased-WHT butterfly, which needs
    the Kerdock design.  On this lineage's Haar-QR frames ``o`` is a real
    half-height product, so the split pays two half-height products in place
    of one full-height product -- FLOP-neutral on the row lanes once the right
    tree is hoisted across both halves -- plus one extra 32,256 x n subtract.
    That is a small loss, so the flag ships off.  See ``phased_wht`` for the
    schedule that would make it a win, and for why turning that on is not a
    parity-preserving move on this lineage.

``USE_PRECOMPUTED_CM``  (suite_16 / 18 / 19)
    ``cM = c * (W0 @ W1)`` evaluated through the same depth-swept operator
    rather than at the cost model's direct counterfactual, with the design
    scalar carried on ``W0`` rather than on the 32,256 x 256 output block.
    Only reachable with the CReLU split on, since ``cM`` exists to give the
    odd channel a design-side operand.
"""

from __future__ import annotations

import flopscope.numpy as fnp

from base_estimator import (
    Estimator as _BaseEstimator,
    _assemble_vector,
    _diagonal_gaussian_pass,
)
from fold_estimator import _initial_regimes, _refine_dead, _refine_on


FOLD_PRODUCTS_THROUGH_OPERATOR = True
HOIST_FOLDED_WEIGHT_STACK = True
USE_CRELU_SPLIT = False
USE_PRECOMPUTED_CM = False


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
        return None

    def _weighted_mean(self, values, final_weights):
        if final_weights is None:
            return fnp.mean(values, axis=0)
        return fnp.mean(values * final_weights[:, None], axis=0)

    def _sample_matmul(self, values, weight, firing_rates):
        _ = firing_rates
        return values @ weight

    def _first_sample_matmul(self, values, weight):
        return values @ weight

    def _fold_matmul(self, values, weight):
        """Full-height products inside the terminal fold.

        Same arithmetic contract as ``_sample_matmul``; a separate hook so the
        routing decision is one flag rather than a rewrite of the fold.
        """
        if FOLD_PRODUCTS_THROUGH_OPERATOR and values.shape[0] >= 2 * self.n_base:
            return self._sample_matmul(values, weight, None)
        return values @ weight

    def _crelu_layer_product(self, x, weight):
        """``x @ weight`` written as direct top and subtracted antipode.

        ``x`` is the antipodal stack ``[relu(z); relu(-z)]`` and the net is
        bias-free, so ``relu(z) - relu(-z) == z`` exactly, at zero as well.
        """
        base = self.n_base
        top = self._sample_matmul(x[:base], weight, None)
        odd = self._sample_matmul(self._first_preactivation, weight, None)
        return fnp.concatenate((top, fnp.subtract(top, odd)), axis=0)

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
        self._first_preactivation = first_pre
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
            weight = mlp.weights[layer][active, :][:, next_active]
            if USE_CRELU_SPLIT and layer == 1 and active.shape[0] == mlp.width:
                pre = self._crelu_layer_product(x, weight)
            else:
                pre = self._sample_matmul(x, weight, firing[layer - 1][active])
            x = fnp.maximum(pre, 0.0)
            active = next_active

        pilot_n = min(self.fold_pilot_base, self.n_base)
        pilot_x29 = fnp.concatenate(
            (x[:pilot_n], x[self.n_base : self.n_base + pilot_n]), axis=0
        )

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
        x30_kink = fnp.maximum(self._fold_matmul(x, weight30[:, kink30]), 0.0)
        pilot_x30_kink = fnp.concatenate(
            (
                x30_kink[:pilot_n],
                x30_kink[self.n_base : self.n_base + pilot_n],
            ),
            axis=0,
        )

        layer31 = mlp.depth - 2
        dead31, kink31, on31 = _initial_regimes(
            analytic_alphas[layer31], self.dead_alpha, self.on_alpha
        )
        weight31 = mlp.weights[layer31]

        # suite_03: one weight-side array per layer, not one per column set.
        if HOIST_FOLDED_WEIGHT_STACK:
            folded30_full = weight30[:, on30] @ weight31[on30, :]
            kink30_to31_full = weight31[kink30, :]

            def folded30_to31(columns):
                return folded30_full[:, columns]
        else:
            def folded30_to31(columns):
                return weight30[:, on30] @ weight31[on30, :][:, columns]

            kink30_to31_full = weight31[kink30, :]

        def pre31(columns, pilot: bool):
            left = pilot_x29 if pilot else x
            middle = pilot_x30_kink if pilot else x30_kink
            product = (
                self._fold_matmul(left, folded30_to31(columns))
                if not pilot
                else left @ folded30_to31(columns)
            )
            second = (
                self._fold_matmul(middle, kink30_to31_full[:, columns])
                if not pilot
                else middle @ kink30_to31_full[:, columns]
            )
            return product + second

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

        layer32 = mlp.depth - 1
        dead32, kink32, on32 = _initial_regimes(
            analytic_alphas[layer32], self.dead_alpha, self.on_alpha
        )
        weight32 = mlp.weights[layer32]
        folded29_to31_on = folded30_to31(on31)
        kink30_to31_on = kink30_to31_full[:, on31]
        if HOIST_FOLDED_WEIGHT_STACK:
            weight32_from_on31 = weight32[on31, :]
            left32_full = folded29_to31_on @ weight32_from_on31
            middle32_full = kink30_to31_on @ weight32_from_on31
            kink31_to32_full = weight32[kink31, :]

            def legs(columns):
                return (left32_full[:, columns], middle32_full[:, columns],
                        kink31_to32_full[:, columns])
        else:
            def legs(columns):
                tail = weight32[on31, :][:, columns]
                return (folded29_to31_on @ tail, kink30_to31_on @ tail,
                        weight32[kink31, :][:, columns])

        def pre32(columns, pilot: bool):
            left_leg, middle_leg, right_leg = legs(columns)
            if pilot:
                return (
                    pilot_x29 @ left_leg
                    + pilot_x30_kink @ middle_leg
                    + pilot_x31_kink @ right_leg
                )
            return (
                self._fold_matmul(x, left_leg)
                + self._fold_matmul(x30_kink, middle_leg)
                + self._fold_matmul(x31_kink, right_leg)
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
            left_leg, middle_leg, right_leg = legs(on32)
            mean_on = (
                self._weighted_mean(x, final_weights) @ left_leg
                + self._weighted_mean(x30_kink, final_weights) @ middle_leg
                + self._weighted_mean(x31_kink, final_weights) @ right_leg
            )
            index_parts.append(on32)
            value_parts.append(mean_on)
        if dead32.shape[0] > 0:
            index_parts.append(dead32)
            value_parts.append(analytic_means[layer32][dead32])
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
        if additional_tangent is not None:
            final_mean = final_mean - additional_tangent

        return fnp.stack((*analytic_means[:-1], final_mean), axis=0)
