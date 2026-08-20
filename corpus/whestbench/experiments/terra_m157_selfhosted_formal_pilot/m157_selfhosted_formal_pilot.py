"""M157 isolated self-hosted Formal-q0 proposal prototype.

The pilot proposal statistic is the even kink-only terminal response of the
already-required Formal q0 stream.  It is intentionally a new pilot-only
proposal statistic, not a replacement for the M145 dense statistic.  The
Formal q0 state is materialized before q1 is drawn, then reused verbatim for
the weighted estimator after q1/main transport have been frozen.
"""

from __future__ import annotations

from dataclasses import dataclass

import flopscope.numpy as fnp

from m145_defensive_acg import explicit_seed_tree
from m145_flopscope_sidecar import (
    _draw_main_anchors,
    _full_mixture_weights,
    fit_proposal_f32,
    frame_and_path_coefficients,
    prepare_reflectors,
)
from m145_integrated_estimator import (
    DIMENSION,
    INTEGRATED_BLOCK_ROWS,
    MAIN_FRAMES,
    MAIN_PATHS,
    PILOT_FRAMES,
    PILOT_LINES,
    PILOT_PATHS,
    TOTAL_PATHS,
    Estimator as _M145Estimator,
)
from base_estimator import _assemble_vector, _diagonal_gaussian_pass
from fold_estimator import _initial_regimes, _refine_dead, _refine_on


@dataclass
class _FormalQ0Plan:
    """Pilot-only Formal state retained until q1 coefficients are available."""

    x1: object
    x29: object
    x30: object
    x31: object
    final_kink: object
    active_sequence: tuple
    active29: object
    dead30: object
    kink30: object
    on30: object
    dead31: object
    kink31: object
    on31: object
    dead32: object
    kink32: object
    on32: object
    weight30: object
    weight31: object
    folded30_to31: object
    left32: object
    middle32: object
    proposal_plus: object
    proposal_minus: object


class SelfHostedFormalPilotEstimator(_M145Estimator):
    """Formal-q0 adaptation with q0-state reuse and exact q1 mixture weights."""

    def __init__(self) -> None:
        super().__init__()
        self.reuse_summary: dict = {}

    def _materialize_formal_q0(self, mlp, analytic_alphas) -> _FormalQ0Plan:
        """Evaluate all q0-only Formal state needed later by the estimator.

        No q1 coefficient, main row, or response-derived proposal parameter is
        read here.  The only values used are fixed q0 pilot rows, MLP weights,
        and analytic regimes.  This is exactly the pilot ownership boundary.
        """

        p_first = self._pilot_mm(
            "selfhost:formal:first:pilot", self._pilot_gaussian, mlp.weights[0]
        )
        p_x = fnp.concatenate(
            (
                fnp.maximum(p_first, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(p_first), fnp.float32(0.0)),
            ),
            axis=0,
        )
        # The normal Formal activation workspace is overwritten through layer
        # 29, while q1-dependent first moments need the original x1 later.
        p_x1 = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        fnp.copyto(p_x1, p_x)
        p_activation_storage = p_x

        active = fnp.arange(mlp.width)
        active_sequence = []
        for layer in range(1, mlp.depth - 3):
            structural_active = fnp.flatnonzero(
                analytic_alphas[layer] >= self.dead_alpha
            )
            cold = fnp.flatnonzero(analytic_alphas[layer] < self.dead_alpha)
            if cold.shape[0] > 0:
                rescue_x = fnp.concatenate(
                    (
                        p_x[: self.pilot_base],
                        p_x[PILOT_LINES : PILOT_LINES + self.pilot_base],
                    ),
                    axis=0,
                )
                pilot_pre = self._direct_mm(
                    f"selfhost:formal:rescue:layer{layer + 1}",
                    rescue_x,
                    mlp.weights[layer][active, :][:, cold],
                )
                fired = fnp.max(pilot_pre, axis=0) > 0.0
                rescued = cold[fnp.flatnonzero(fired)]
                next_active = fnp.sort(
                    fnp.concatenate((structural_active, rescued), axis=0)
                )
            else:
                next_active = structural_active
            selected = mlp.weights[layer][active, :][:, next_active]
            p_pre = self._pilot_mm(
                f"selfhost:formal:layer{layer + 1}:pilot", p_x, selected
            )
            p_next = p_activation_storage[:, : int(next_active.shape[0])]
            fnp.maximum(p_pre, fnp.float32(0.0), out=p_next)
            p_x = p_next
            active = next_active
            active_sequence.append(active)

        p_x29 = p_x
        layer30 = mlp.depth - 3
        dead30, kink30, on30 = _initial_regimes(
            analytic_alphas[layer30], self.dead_alpha, self.on_alpha
        )
        weight30 = mlp.weights[layer30][active, :]
        if dead30.shape[0] > 0:
            dead30, rescued30 = _refine_dead(
                dead30,
                self._direct_mm(
                    "selfhost:formal:fold30:refine_dead",
                    p_x29,
                    weight30[:, dead30],
                ),
            )
            kink30 = fnp.concatenate((kink30, rescued30), axis=0)
        if on30.shape[0] > 0:
            on30, demoted30 = _refine_on(
                on30,
                self._direct_mm(
                    "selfhost:formal:fold30:refine_on",
                    p_x29,
                    weight30[:, on30],
                ),
            )
            kink30 = fnp.concatenate((kink30, demoted30), axis=0)
        kink30 = fnp.sort(kink30)
        p_x30 = fnp.maximum(
            self._direct_mm("selfhost:formal:fold30:pilot", p_x29, weight30[:, kink30]),
            fnp.float32(0.0),
        )

        layer31 = mlp.depth - 2
        dead31, kink31, on31 = _initial_regimes(
            analytic_alphas[layer31], self.dead_alpha, self.on_alpha
        )
        weight31 = mlp.weights[layer31]
        folded30_to31 = self._direct_mm(
            "selfhost:formal:fold30_to31", weight30[:, on30], weight31[on30, :]
        )

        def pre31(columns, label):
            left = self._direct_mm(
                f"selfhost:formal:pre31:{label}:left",
                p_x29,
                folded30_to31[:, columns],
            )
            middle = self._direct_mm(
                f"selfhost:formal:pre31:{label}:middle",
                p_x30,
                weight31[kink30, :][:, columns],
            )
            fnp.add(left, middle, out=left)
            return left

        if dead31.shape[0] > 0:
            dead31, rescued31 = _refine_dead(
                dead31, pre31(dead31, "refine_dead")
            )
            kink31 = fnp.concatenate((kink31, rescued31), axis=0)
        if on31.shape[0] > 0:
            on31, demoted31 = _refine_on(on31, pre31(on31, "refine_on"))
            kink31 = fnp.concatenate((kink31, demoted31), axis=0)
        kink31 = fnp.sort(kink31)
        p_x31 = fnp.maximum(pre31(kink31, "pilot"), fnp.float32(0.0))

        layer32 = mlp.depth - 1
        dead32, kink32, on32 = _initial_regimes(
            analytic_alphas[layer32], self.dead_alpha, self.on_alpha
        )
        weight32 = mlp.weights[layer32]
        left32 = self._direct_mm(
            "selfhost:formal:fold29_to32",
            folded30_to31[:, on31],
            weight32[on31, :],
        )
        middle32 = self._direct_mm(
            "selfhost:formal:fold30_to32",
            weight31[kink30, :][:, on31],
            weight32[on31, :],
        )

        def pre32(columns, label):
            left = self._direct_mm(
                f"selfhost:formal:pre32:{label}:left", p_x29, left32[:, columns]
            )
            middle = self._direct_mm(
                f"selfhost:formal:pre32:{label}:middle", p_x30, middle32[:, columns]
            )
            fnp.add(left, middle, out=left)
            right = self._direct_mm(
                f"selfhost:formal:pre32:{label}:right",
                p_x31,
                weight32[kink31, :][:, columns],
            )
            fnp.add(left, right, out=left)
            return left

        if dead32.shape[0] > 0:
            dead32, rescued32 = _refine_dead(
                dead32, pre32(dead32, "refine_dead")
            )
            kink32 = fnp.concatenate((kink32, rescued32), axis=0)
        if on32.shape[0] > 0:
            on32, demoted32 = _refine_on(on32, pre32(on32, "refine_on"))
            kink32 = fnp.concatenate((kink32, demoted32), axis=0)
        kink32 = fnp.sort(kink32)
        if kink32.shape[0] > 0:
            p_final = fnp.maximum(pre32(kink32, "kink_pilot"), fnp.float32(0.0))
        else:
            p_final = fnp.empty((PILOT_PATHS, 0), dtype=fnp.float32)

        # M157's new proposal statistic is only the Formal kink response.  It
        # is a deterministic q0-only response pair. ``fit_proposal_f32``
        # symmetrizes the pair itself; its normalized energy is invariant to
        # the number of zero dead/on coordinates omitted here.
        if kink32.shape[0] > 0:
            proposal_plus = p_final[:PILOT_LINES]
            proposal_minus = p_final[PILOT_LINES:PILOT_PATHS]
        else:
            # A zero response has the sidecar's explicit uniform fallback.
            proposal_plus = fnp.zeros((PILOT_LINES, 1), dtype=fnp.float32)
            proposal_minus = fnp.zeros((PILOT_LINES, 1), dtype=fnp.float32)

        return _FormalQ0Plan(
            x1=p_x1,
            x29=p_x29,
            x30=p_x30,
            x31=p_x31,
            final_kink=p_final,
            active_sequence=tuple(active_sequence),
            active29=active,
            dead30=dead30,
            kink30=kink30,
            on30=on30,
            dead31=dead31,
            kink31=kink31,
            on31=on31,
            dead32=dead32,
            kink32=kink32,
            on32=on32,
            weight30=weight30,
            weight31=weight31,
            folded30_to31=folded30_to31,
            left32=left32,
            middle32=middle32,
            proposal_plus=proposal_plus,
            proposal_minus=proposal_minus,
        )

    def _split_with_cached_q0(
        self,
        mlp,
        analytic_means,
        analytic_alphas,
        firing,
        analytic_sigmas,
        plan: _FormalQ0Plan,
        pilot_path_coeff,
        main_path_coeff,
    ):
        """Run q1 Formal work while consuming, never recomputing, q0 state."""

        m_first = self._main_mm(
            "selfhost:formal:first:main", self._main_gaussian, mlp.weights[0]
        )
        m_x = fnp.concatenate(
            (
                fnp.maximum(m_first, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(m_first), fnp.float32(0.0)),
            ),
            axis=0,
        )
        m_activation_storage = m_x
        sigma0 = fnp.sqrt(fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0))
        exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
        first_mean = self._split_weighted_mean(
            plan.x1, m_x, pilot_path_coeff, main_path_coeff, "selfhost_first_mean"
        )
        first_second = self._split_weighted_second_mean(
            plan.x1, m_x, pilot_path_coeff, main_path_coeff
        )
        first_moment_residual = first_mean - exact_first_mean
        radial_second = fnp.multiply(
            fnp.multiply(fnp.float32(0.5), self._radial_covariance),
            fnp.multiply(sigma0, sigma0),
        )
        first_variance_residual = fnp.subtract(
            fnp.subtract(first_second, radial_second),
            fnp.multiply(
                fnp.multiply(fnp.float32(2.0), exact_first_mean),
                first_moment_residual,
            ),
        )

        active = fnp.arange(mlp.width)
        for layer, next_active in zip(
            range(1, mlp.depth - 3), plan.active_sequence
        ):
            selected = mlp.weights[layer][active, :][:, next_active]
            m_pre = self._main_mm(
                f"selfhost:formal:layer{layer + 1}:main", m_x, selected
            )
            m_next = m_activation_storage[:, : int(next_active.shape[0])]
            fnp.maximum(m_pre, fnp.float32(0.0), out=m_next)
            m_x = m_next
            active = next_active

        weight30 = plan.weight30
        weight31 = plan.weight31
        weight32 = mlp.weights[mlp.depth - 1]
        m_x30 = fnp.maximum(
            self._direct_mm(
                "selfhost:formal:fold30:main", m_x, weight30[:, plan.kink30]
            ),
            fnp.float32(0.0),
        )

        def main_pre31(columns, left, middle, label):
            a = self._direct_mm(
                f"selfhost:formal:pre31:{label}:left",
                left,
                plan.folded30_to31[:, columns],
            )
            b = self._direct_mm(
                f"selfhost:formal:pre31:{label}:middle",
                middle,
                weight31[plan.kink30, :][:, columns],
            )
            fnp.add(a, b, out=a)
            return a

        def main_pre32(columns, left, middle, right, label):
            a = self._direct_mm(
                f"selfhost:formal:pre32:{label}:left", left, plan.left32[:, columns]
            )
            b = self._direct_mm(
                f"selfhost:formal:pre32:{label}:middle", middle, plan.middle32[:, columns]
            )
            fnp.add(a, b, out=a)
            c = self._direct_mm(
                f"selfhost:formal:pre32:{label}:right",
                right,
                weight32[plan.kink31, :][:, columns],
            )
            fnp.add(a, c, out=a)
            return a

        pilot_kink_sum = None
        main_kink_sum = None
        if plan.kink32.shape[0] > 0:
            pilot_kink_sum = self._direct_mm(
                "selfhost:formal:terminal_kink_mean:pilot",
                pilot_path_coeff[None, :],
                plan.final_kink,
            )[0]
            main_kink_sum = fnp.zeros(
                (int(plan.kink32.shape[0]),), dtype=fnp.float32
            )
        pilot_x31_sum = None
        main_x31_sum = None
        if plan.on32.shape[0] > 0:
            pilot_x31_sum = self._direct_mm(
                "selfhost:formal:terminal_x31_mean:pilot",
                pilot_path_coeff[None, :],
                plan.x31,
            )[0]
            main_x31_sum = fnp.zeros(
                (int(plan.kink31.shape[0]),), dtype=fnp.float32
            )

        if plan.kink32.shape[0] > 0 or plan.on32.shape[0] > 0:
            for start in range(0, MAIN_PATHS, INTEGRATED_BLOCK_ROWS):
                stop = min(start + INTEGRATED_BLOCK_ROWS, MAIN_PATHS)
                x31_block = main_pre31(
                    plan.kink31,
                    m_x[start:stop],
                    m_x30[start:stop],
                    f"main_block_{start}_{stop}",
                )
                fnp.maximum(x31_block, fnp.float32(0.0), out=x31_block)
                if plan.kink32.shape[0] > 0:
                    block = main_pre32(
                        plan.kink32,
                        m_x[start:stop],
                        m_x30[start:stop],
                        x31_block,
                        f"kink_main_{start}_{stop}",
                    )
                    fnp.maximum(block, fnp.float32(0.0), out=block)
                    block_sum = self._direct_mm(
                        f"selfhost:formal:terminal_kink_mean:main_{start}_{stop}",
                        main_path_coeff[None, start:stop],
                        block,
                    )[0]
                    main_kink_sum = fnp.add(main_kink_sum, block_sum)
                if plan.on32.shape[0] > 0:
                    x31_sum = self._direct_mm(
                        f"selfhost:formal:terminal_x31_mean:main_{start}_{stop}",
                        main_path_coeff[None, start:stop],
                        x31_block,
                    )[0]
                    main_x31_sum = fnp.add(main_x31_sum, x31_sum)

        index_parts = []
        value_parts = []
        if plan.kink32.shape[0] > 0:
            index_parts.append(plan.kink32)
            value_parts.append(
                fnp.divide(
                    fnp.add(pilot_kink_sum, main_kink_sum), fnp.float32(TOTAL_PATHS)
                )
            )
        if plan.on32.shape[0] > 0:
            mean_x = self._split_weighted_mean(
                plan.x29,
                m_x,
                pilot_path_coeff,
                main_path_coeff,
                "selfhost_terminal_x_mean",
            )
            mean_x30 = self._split_weighted_mean(
                plan.x30,
                m_x30,
                pilot_path_coeff,
                main_path_coeff,
                "selfhost_terminal_x30_mean",
            )
            mean_x31 = fnp.divide(
                fnp.add(pilot_x31_sum, main_x31_sum), fnp.float32(TOTAL_PATHS)
            )
            mean_on = (
                mean_x @ plan.left32[:, plan.on32]
                + mean_x30 @ plan.middle32[:, plan.on32]
                + mean_x31 @ weight32[plan.kink31, :][:, plan.on32]
            )
            index_parts.append(plan.on32)
            value_parts.append(mean_on)
        if plan.dead32.shape[0] > 0:
            index_parts.append(plan.dead32)
            value_parts.append(analytic_means[mlp.depth - 1][plan.dead32])
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

    def predict(self, mlp, budget):
        _ = budget
        if self._frame_bank is None:
            raise RuntimeError("setup() did not initialize M157")
        self.dispatch_trace = []
        self.event_log = []
        self.last_transport = {}
        self.reuse_summary = {}
        analytic_means, analytic_alphas, firing, analytic_sigmas = (
            _diagonal_gaussian_pass(mlp)
        )

        plan = self._materialize_formal_q0(mlp, analytic_alphas)
        self.event_log.append("formal_q0_pilot_materialized")
        v, lam, fallback = fit_proposal_f32(
            self._pilot_gaussian, plan.proposal_plus, plan.proposal_minus
        )
        tree = explicit_seed_tree(self._setup_seed, int(mlp.seed))
        child_seeds = {
            name: int(tree["children"][name]["seed"])
            for name in ("mixture_labels", "uniform_anchors", "acg_latents")
        }
        anchors, labels = _draw_main_anchors(v, lam, child_seeds)
        weights = _full_mixture_weights(anchors, v, lam)
        frame_coeff, _path = frame_and_path_coefficients(weights)
        pilot_path_coeff, main_path_coeff = self._split_path_coefficients(frame_coeff)
        vectors, beta = prepare_reflectors(self._frame_bank, anchors, self._mean_radius)
        self.last_transport = {
            "proposal_source": "formal_kink_even_q0",
            "rank": int(lam.shape[0]),
            "fallback": fallback,
            "weight_min": float(fnp.min(weights)),
            "weight_max": float(fnp.max(weights)),
            "bad_weight_count": int(
                fnp.sum((~fnp.isfinite(weights)) | (weights <= fnp.float32(0.0)))
            ),
            "label_acg_count": int(fnp.sum(labels)),
            "proposal_signature_shape": list(plan.proposal_plus.shape),
            "proposal_kink_count": int(plan.kink32.shape[0]),
            "seed_tree": tree,
        }
        self.event_log.append("proposal_frozen_from_formal_q0_only")

        applied = 0
        try:
            for index in range(MAIN_FRAMES):
                self._apply_one_reflector(index, vectors, beta)
                applied += 1
            self.event_log.append("main_transport_applied_after_proposal")
            self.event_log.append("formal_main_with_cached_q0_entered")
            prediction = self._split_with_cached_q0(
                mlp,
                analytic_means,
                analytic_alphas,
                firing,
                analytic_sigmas,
                plan,
                pilot_path_coeff,
                main_path_coeff,
            )
            self.event_log.append("formal_main_with_cached_q0_complete")
            self.reuse_summary = {
                "dense_proposal_pilot_dispatches": 0,
                "formal_q0_dispatches": int(
                    sum(
                        int(row["matmul_calls"])
                        for row in self.dispatch_trace
                        if row["stage"].startswith("selfhost:formal:")
                        and ":pilot" in row["stage"]
                    )
                ),
                "cached_q0_reused_after_proposal": True,
            }
            return prediction
        finally:
            for index in range(applied - 1, -1, -1):
                self._apply_one_reflector(index, vectors, beta)
            fnp.copyto(self._frame_bank[PILOT_FRAMES:], self._provisional_main_copy)
            self.event_log.append("main_transport_restored_and_canonicalized")
