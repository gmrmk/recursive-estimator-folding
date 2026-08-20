"""Isolated, truth-free Formal-L1 descendant for M145 integration audits.

This module deliberately does not replace the frozen Formal-L1 champion.  It
imports that champion's hash-bound analytic/folding primitives, generates the
same provisional radius-scaled QR bank for a matched comparator and candidate,
materializes an exact all-output pilot surrogate, freezes the ACG proposal,
then evaluates the Formal fold3 path as separate pilot/main streams.

No efficacy decision is encoded here.  ``MatchedComparator`` disables the
transport and consumes the exact same provisional bank law.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
FORMAL_SOURCE = HERE.parent / "row_blocked_production" / "candidate_source"
if str(FORMAL_SOURCE) not in sys.path:
    sys.path.insert(0, str(FORMAL_SOURCE))

from base_estimator import _assemble_vector, _diagonal_gaussian_pass  # noqa: E402
from fold3_estimator import Estimator as _FormalFold3Estimator  # noqa: E402
from fold_estimator import _initial_regimes, _refine_dead, _refine_on  # noqa: E402
from row_blocked_winograd import (  # noqa: E402
    BLOCK_ROWS,
    RowBlockedBatchedWinograd,
    row_blocked_bill_identity,
)

from m145_defensive_acg import (  # noqa: E402
    DIMENSION,
    MAIN_FRAMES,
    PILOT_FRAMES,
    PILOT_LINES,
    RANK,
    TOTAL_FRAMES,
    explicit_seed_tree,
)
from m145_flopscope_sidecar import (  # noqa: E402
    _draw_main_anchors,
    _full_mixture_weights,
    _householder_in_place,
    fit_proposal_f32,
    frame_and_path_coefficients,
    prepare_reflectors,
)


PILOT_PATHS = 2 * PILOT_LINES
MAIN_LINES = MAIN_FRAMES * DIMENSION
MAIN_PATHS = 2 * MAIN_LINES
TOTAL_PATHS = 2 * TOTAL_FRAMES * DIMENSION
INTEGRATED_BLOCK_ROWS = 4096


def mean_radius(width: int = DIMENSION) -> float:
    return math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((int(width) + 1.0) / 2.0)
        - math.lgamma(int(width) / 2.0)
    )


def setup_child_seeds(setup_seed: int) -> tuple[int, int]:
    tree = explicit_seed_tree(int(setup_seed), 0)
    return (
        int(tree["children"]["pilot_qr"]["seed"]),
        int(tree["children"]["main_qr"]["seed"]),
    )


def raw_qr_radius_bank_numpy(
    setup_seed: int,
    *,
    width: int = DIMENSION,
    pilot_frames: int = PILOT_FRAMES,
    main_frames: int = MAIN_FRAMES,
) -> np.ndarray:
    """Reference generator using the exact Formal QR/sign convention.

    There is intentionally no diagonal-``R`` sign normalization.  This helper
    exists for coupling and law tests; deployed setup repeats the same calls
    with ``flopscope.numpy`` so they are visible to the sandbox.
    """

    pilot_seed, main_seed = setup_child_seeds(setup_seed)
    radius = np.float32(mean_radius(width))
    pilot_rng = np.random.default_rng(pilot_seed)
    main_rng = np.random.default_rng(main_seed)
    pilot_raw = pilot_rng.standard_normal(
        (int(pilot_frames), int(width), int(width)), dtype=np.float32
    )
    main_raw = main_rng.standard_normal(
        (int(main_frames), int(width), int(width)), dtype=np.float32
    )
    pilot_q, _pilot_r = np.linalg.qr(pilot_raw)
    main_q, _main_r = np.linalg.qr(main_raw)
    return np.concatenate((pilot_q, main_q), axis=0).astype(np.float32) * radius


class Estimator(_FormalFold3Estimator):
    """Integrated M145 candidate; execution remains protocol-locked."""

    n_base = TOTAL_FRAMES * DIMENSION
    pilot_base = DIMENSION
    fold_pilot_base = PILOT_LINES
    radial_conditioning = True
    transport_enabled = True

    def __init__(self) -> None:
        super().__init__()
        self._setup_seed = 0
        self._mean_radius = np.float32(mean_radius(DIMENSION))
        self._frame_bank = None
        self._pilot_gaussian = None
        self._main_gaussian = None
        self._provisional_main_copy = None
        self._main_winograd = None
        self._hh_qv = None
        self._hh_outer = None
        self.dispatch_trace: list[dict] = []
        self.event_log: list[str] = []
        self.last_transport: dict = {}
        self.stage_observer = None

    def setup(self, ctx) -> None:
        if int(ctx.width) != DIMENSION or int(ctx.depth) != 32:
            raise ValueError("M145 integrated descendant is frozen at 256x32")
        self._setup_seed = int(ctx.seed)
        pilot_seed, main_seed = setup_child_seeds(self._setup_seed)
        pilot_rng = fnp.random.default_rng(pilot_seed)
        main_rng = fnp.random.default_rng(main_seed)
        pilot_raw = pilot_rng.standard_normal(
            (PILOT_FRAMES, DIMENSION, DIMENSION), dtype=fnp.float32
        )
        main_raw = main_rng.standard_normal(
            (MAIN_FRAMES, DIMENSION, DIMENSION), dtype=fnp.float32
        )
        # Exact Formal-L1 convention: raw q, with no sign normalization.
        pilot_q, _pilot_r = fnp.linalg.qr(pilot_raw)
        main_q, _main_r = fnp.linalg.qr(main_raw)
        bank = fnp.concatenate((pilot_q, main_q), axis=0).astype(fnp.float32)
        bank = bank * self._mean_radius
        self._frame_bank = bank
        # Hoist both tracked reshapes to setup; Formal billing charges reshapes.
        self._pilot_gaussian = bank[:PILOT_FRAMES].reshape(
            (PILOT_LINES, DIMENSION)
        )
        self._main_gaussian = bank[PILOT_FRAMES:].reshape(
            (MAIN_LINES, DIMENSION)
        )
        if self.transport_enabled:
            self._provisional_main_copy = fnp.empty(
                (MAIN_FRAMES, DIMENSION, DIMENSION), dtype=fnp.float32
            )
            fnp.copyto(
                self._provisional_main_copy, bank[PILOT_FRAMES:]
            )
        self._radial_covariance = (
            self._mean_radius * self._mean_radius / fnp.float32(DIMENSION)
        )
        # QR temporaries must die before the hot buffers are allocated; keeping
        # both lifetime classes live would violate the 512 MiB setup gate.
        del pilot_raw, main_raw, pilot_q, main_q, _pilot_r, _main_r
        # One sequential workspace owns both passes.  The 4096-row scratch
        # freezes a memory-safe exact schedule; the 8192-row parent schedule
        # exceeded the integrated 512 MiB peak once pilot/main lifetimes met.
        self._main_winograd = RowBlockedBatchedWinograd(
            MAIN_PATHS, DIMENSION, INTEGRATED_BLOCK_ROWS
        )
        self._hh_qv = fnp.empty((DIMENSION,), dtype=fnp.float32)
        self._hh_outer = fnp.empty((DIMENSION, DIMENSION), dtype=fnp.float32)

    @property
    def frame_bank(self):
        if self._frame_bank is None:
            raise RuntimeError("setup() has not initialized the frame bank")
        return self._frame_bank

    @property
    def workspace_bytes(self) -> int:
        return int(self._main_winograd.buffer_bytes)

    def _record_rowblocked(self, stage: str, left, right, workspace) -> None:
        m, k = int(left.shape[0]), int(left.shape[1])
        n = int(right.shape[1])
        identity = row_blocked_bill_identity(m, k, n)
        self.dispatch_trace.append(
            {
                "stage": stage,
                "shape": [m, k, n],
                "kind": identity["strategy"],
                "matmul_calls": int(workspace.last_total_matmul_calls),
                "shape_bill": int(identity["selected_bill"]),
            }
        )

    def _observe(self, stage: str) -> None:
        if self.stage_observer is not None:
            self.stage_observer(stage)

    def _pilot_mm(self, stage: str, left, right):
        return self._workspace_mm(stage, left, right)

    def _main_mm(self, stage: str, left, right):
        return self._workspace_mm(stage, left, right)

    def _workspace_mm(self, stage: str, left, right):
        """Use the owned output even when the parent dispatches direct."""

        identity = row_blocked_bill_identity(
            int(left.shape[0]), int(left.shape[1]), int(right.shape[1])
        )
        if identity["strategy"] == "direct":
            rows = int(left.shape[0])
            columns = int(right.shape[1])
            out = self._main_winograd.output[:rows, :columns]
            calls = 0
            for start in range(0, rows, INTEGRATED_BLOCK_ROWS):
                stop = min(start + INTEGRATED_BLOCK_ROWS, rows)
                fnp.matmul(left[start:stop], right, out=out[start:stop])
                calls += 1
            self._main_winograd.last_core_calls = 0
            self._main_winograd.last_total_matmul_calls = calls
        else:
            out = self._main_winograd.multiply(left, right)
        self._record_rowblocked(stage, left, right, self._main_winograd)
        return out

    def _direct_mm(self, stage: str, left, right):
        out = left @ right
        self.dispatch_trace.append(
            {
                "stage": stage,
                "shape": [int(left.shape[0]), int(left.shape[1]), int(right.shape[1])],
                "kind": "direct",
                "matmul_calls": 1,
            }
        )
        return out

    def _exact_pilot_surrogate(self, mlp):
        """Materialize exact even final activations for all 1024 pilot lines."""

        first_pre = self._pilot_mm(
            "pilot_surrogate:first", self._pilot_gaussian, mlp.weights[0]
        )
        x = fnp.concatenate(
            (
                fnp.maximum(first_pre, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(first_pre), fnp.float32(0.0)),
            ),
            axis=0,
        )
        for layer in range(1, mlp.depth):
            pre = self._pilot_mm(
                f"pilot_surrogate:layer{layer + 1}", x, mlp.weights[layer]
            )
            fnp.maximum(pre, fnp.float32(0.0), out=x)
        surrogate = fnp.multiply(
            fnp.float32(0.5),
            fnp.add(x[:PILOT_LINES], x[PILOT_LINES:PILOT_PATHS]),
        )
        if surrogate.shape != (PILOT_LINES, DIMENSION):
            raise AssertionError("pilot surrogate shape changed")
        if bool(fnp.any(~fnp.isfinite(surrogate))):
            raise FloatingPointError("pilot surrogate is nonfinite")
        self.event_log.append("pilot_surrogate_materialized")
        return surrogate.astype(fnp.float32)

    def _split_path_coefficients(self, frame_coefficients):
        pilot_line = fnp.repeat(frame_coefficients[:PILOT_FRAMES], DIMENSION)
        main_line = fnp.repeat(frame_coefficients[PILOT_FRAMES:], DIMENSION)
        pilot_path = fnp.concatenate((pilot_line, pilot_line), axis=0).astype(
            fnp.float32
        )
        main_path = fnp.concatenate((main_line, main_line), axis=0).astype(
            fnp.float32
        )
        return pilot_path, main_path

    def _split_weighted_mean(
        self,
        pilot_values,
        main_values,
        pilot_path_coeff,
        main_path_coeff,
        stage="weighted_mean",
    ):
        if int(pilot_values.shape[0]) != PILOT_PATHS:
            raise ValueError("pilot value path count changed")
        if int(main_values.shape[0]) != MAIN_PATHS:
            raise ValueError("main value path count changed")
        # A 1xN by NxK product avoids materializing an NxK weighted copy.
        pilot_sum = self._direct_mm(
            f"formal:{stage}:pilot", pilot_path_coeff[None, :], pilot_values
        )[0]
        main_sum = self._direct_mm(
            f"formal:{stage}:main", main_path_coeff[None, :], main_values
        )[0]
        return (pilot_sum + main_sum) / fnp.float32(TOTAL_PATHS)

    def _split_weighted_second_mean(
        self, pilot_values, main_values, pilot_path_coeff, main_path_coeff
    ):
        """Weighted second moment with bounded 8192-row temporaries."""

        out = fnp.zeros((int(pilot_values.shape[1]),), dtype=fnp.float32)
        for values, coefficients in (
            (pilot_values, pilot_path_coeff),
            (main_values, main_path_coeff),
        ):
            rows = int(values.shape[0])
            for start in range(0, rows, INTEGRATED_BLOCK_ROWS):
                stop = min(start + INTEGRATED_BLOCK_ROWS, rows)
                block = values[start:stop]
                square = fnp.multiply(block, block)
                weighted = fnp.multiply(square, coefficients[start:stop, None])
                out = fnp.add(out, fnp.sum(weighted, axis=0))
        return fnp.divide(out, fnp.float32(TOTAL_PATHS))

    def _apply_one_reflector(self, main_index, vectors, beta) -> None:
        _householder_in_place(
            self._frame_bank[PILOT_FRAMES + main_index],
            vectors[main_index],
            beta[main_index],
            self._hh_qv,
            self._hh_outer,
        )

    def _split_formal_path(
        self,
        mlp,
        analytic_means,
        analytic_alphas,
        firing,
        analytic_sigmas,
        pilot_path_coeff,
        main_path_coeff,
    ):
        """Formal fold3 with identical regimes and separate pilot/main paths."""

        p_first = self._pilot_mm(
            "formal:first:pilot", self._pilot_gaussian, mlp.weights[0]
        )
        # Materialize pilot activations before the shared workspace is reused
        # by the main pass.
        p_x = fnp.concatenate(
            (
                fnp.maximum(p_first, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(p_first), fnp.float32(0.0)),
            ),
            axis=0,
        )
        m_first = self._main_mm(
            "formal:first:main", self._main_gaussian, mlp.weights[0]
        )
        m_x = fnp.concatenate(
            (
                fnp.maximum(m_first, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(m_first), fnp.float32(0.0)),
            ),
            axis=0,
        )
        p_activation_storage = p_x
        m_activation_storage = m_x
        sigma0 = fnp.sqrt(fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0))
        exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
        first_mean = self._split_weighted_mean(
            p_x,
            m_x,
            pilot_path_coeff,
            main_path_coeff,
            "first_mean",
        )
        first_second = self._split_weighted_second_mean(
            p_x, m_x, pilot_path_coeff, main_path_coeff
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
        self._observe("formal_first_complete")

        active = fnp.arange(mlp.width)
        for layer in range(1, mlp.depth - 3):
            structural_active = fnp.flatnonzero(
                analytic_alphas[layer] >= self.dead_alpha
            )
            cold = fnp.flatnonzero(analytic_alphas[layer] < self.dead_alpha)
            if cold.shape[0] > 0:
                # Exact Formal ownership: first 256 positive pilot lines and
                # their antipodes.  No main value can influence this branch.
                rescue_x = fnp.concatenate(
                    (
                        p_x[: self.pilot_base],
                        p_x[PILOT_LINES : PILOT_LINES + self.pilot_base],
                    ),
                    axis=0,
                )
                pilot_pre = self._direct_mm(
                    f"formal:rescue:layer{layer + 1}",
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
                f"formal:layer{layer + 1}:pilot", p_x, selected
            )
            p_next = p_activation_storage[:, : int(next_active.shape[0])]
            fnp.maximum(p_pre, fnp.float32(0.0), out=p_next)
            p_x = p_next
            m_pre = self._main_mm(
                f"formal:layer{layer + 1}:main", m_x, selected
            )
            m_next = m_activation_storage[:, : int(next_active.shape[0])]
            fnp.maximum(m_pre, fnp.float32(0.0), out=m_next)
            m_x = m_next
            active = next_active
            self._observe(f"formal_layer_{layer + 1}_complete")

        # The pilot stream is exactly four frames / 1024 lines, so its whole
        # antipodal state is Formal's fold_pilot_base slice.
        pilot_x29 = p_x
        layer30 = mlp.depth - 3
        dead30, kink30, on30 = _initial_regimes(
            analytic_alphas[layer30], self.dead_alpha, self.on_alpha
        )
        weight30 = mlp.weights[layer30][active, :]
        if dead30.shape[0] > 0:
            dead30, rescued30 = _refine_dead(
                dead30,
                self._direct_mm(
                    "formal:fold30:refine_dead", pilot_x29, weight30[:, dead30]
                ),
            )
            kink30 = fnp.concatenate((kink30, rescued30), axis=0)
        if on30.shape[0] > 0:
            on30, demoted30 = _refine_on(
                on30,
                self._direct_mm(
                    "formal:fold30:refine_on", pilot_x29, weight30[:, on30]
                ),
            )
            kink30 = fnp.concatenate((kink30, demoted30), axis=0)
        kink30 = fnp.sort(kink30)
        p_x30 = fnp.maximum(
            self._direct_mm("formal:fold30:pilot", p_x, weight30[:, kink30]), 0.0
        )
        m_x30 = fnp.maximum(
            self._direct_mm("formal:fold30:main", m_x, weight30[:, kink30]), 0.0
        )
        self._observe("fold30_states_complete")

        layer31 = mlp.depth - 2
        dead31, kink31, on31 = _initial_regimes(
            analytic_alphas[layer31], self.dead_alpha, self.on_alpha
        )
        weight31 = mlp.weights[layer31]
        folded30_to31 = self._direct_mm(
            "formal:fold30_to31", weight30[:, on30], weight31[on30, :]
        )

        def pre31(columns, p_left, p_middle, label):
            left = self._direct_mm(
                f"formal:pre31:{label}:left", p_left, folded30_to31[:, columns]
            )
            middle = self._direct_mm(
                f"formal:pre31:{label}:middle",
                p_middle,
                weight31[kink30, :][:, columns],
            )
            fnp.add(left, middle, out=left)
            return left

        if dead31.shape[0] > 0:
            dead31, rescued31 = _refine_dead(
                dead31, pre31(dead31, p_x, p_x30, "refine_dead")
            )
            kink31 = fnp.concatenate((kink31, rescued31), axis=0)
        if on31.shape[0] > 0:
            on31, demoted31 = _refine_on(
                on31, pre31(on31, p_x, p_x30, "refine_on")
            )
            kink31 = fnp.concatenate((kink31, demoted31), axis=0)
        kink31 = fnp.sort(kink31)
        p_x31 = fnp.maximum(pre31(kink31, p_x, p_x30, "pilot"), 0.0)
        self._observe("fold31_pilot_complete")

        layer32 = mlp.depth - 1
        dead32, kink32, on32 = _initial_regimes(
            analytic_alphas[layer32], self.dead_alpha, self.on_alpha
        )
        weight32 = mlp.weights[layer32]
        folded29_to31_on = folded30_to31[:, on31]
        kink30_to31_on = weight31[kink30, :][:, on31]
        left32 = self._direct_mm(
            "formal:fold29_to32", folded29_to31_on, weight32[on31, :]
        )
        middle32 = self._direct_mm(
            "formal:fold30_to32", kink30_to31_on, weight32[on31, :]
        )

        def pre32(columns, left, middle, right, label):
            a = self._direct_mm(
                f"formal:pre32:{label}:left", left, left32[:, columns]
            )
            b = self._direct_mm(
                f"formal:pre32:{label}:middle", middle, middle32[:, columns]
            )
            fnp.add(a, b, out=a)
            del b
            c = self._direct_mm(
                f"formal:pre32:{label}:right",
                right,
                weight32[kink31, :][:, columns],
            )
            fnp.add(a, c, out=a)
            return a

        if dead32.shape[0] > 0:
            dead32, rescued32 = _refine_dead(
                dead32, pre32(dead32, p_x, p_x30, p_x31, "refine_dead")
            )
            kink32 = fnp.concatenate((kink32, rescued32), axis=0)
        if on32.shape[0] > 0:
            on32, demoted32 = _refine_on(
                on32, pre32(on32, p_x, p_x30, p_x31, "refine_on")
            )
            kink32 = fnp.concatenate((kink32, demoted32), axis=0)
        kink32 = fnp.sort(kink32)

        index_parts = []
        value_parts = []
        pilot_kink_sum = None
        main_kink_sum = None
        if kink32.shape[0] > 0:
            p_final = fnp.maximum(
                pre32(kink32, p_x, p_x30, p_x31, "kink_pilot"), 0.0
            )
            pilot_kink_sum = self._direct_mm(
                "formal:terminal_kink_mean:pilot",
                pilot_path_coeff[None, :],
                p_final,
            )[0]
            # The full 62,464x|kink| terminal output was the last avoidable
            # peak buffer.  Stream it in frozen 4096-row blocks and reduce
            # immediately; the matrix-product and reduction bills remain
            # explicit and the change of measure is unchanged.
            main_kink_sum = fnp.zeros(
                (int(kink32.shape[0]),), dtype=fnp.float32
            )
        pilot_x31_sum = None
        main_x31_sum = None
        if on32.shape[0] > 0:
            pilot_x31_sum = self._direct_mm(
                "formal:terminal_x31_mean:pilot",
                pilot_path_coeff[None, :],
                p_x31,
            )[0]
            main_x31_sum = fnp.zeros(
                (int(kink31.shape[0]),), dtype=fnp.float32
            )

        # Stream the layer-31 main state and every consumer together.  This
        # removes the 62,464x|kink31| resident buffer while retaining exactly
        # the same pilot-frozen regimes and per-frame coefficients.
        if kink32.shape[0] > 0 or on32.shape[0] > 0:
            for start in range(0, MAIN_PATHS, INTEGRATED_BLOCK_ROWS):
                stop = min(start + INTEGRATED_BLOCK_ROWS, MAIN_PATHS)
                x31_block = pre31(
                    kink31,
                    m_x[start:stop],
                    m_x30[start:stop],
                    f"main_block_{start}_{stop}",
                )
                fnp.maximum(x31_block, fnp.float32(0.0), out=x31_block)
                if kink32.shape[0] > 0:
                    block = pre32(
                        kink32,
                        m_x[start:stop],
                        m_x30[start:stop],
                        x31_block,
                        f"kink_main_{start}_{stop}",
                    )
                    fnp.maximum(block, fnp.float32(0.0), out=block)
                    block_sum = self._direct_mm(
                        f"formal:terminal_kink_mean:main_{start}_{stop}",
                        main_path_coeff[None, start:stop],
                        block,
                    )[0]
                    main_kink_sum = fnp.add(main_kink_sum, block_sum)
                if on32.shape[0] > 0:
                    block_x31_sum = self._direct_mm(
                        f"formal:terminal_x31_mean:main_{start}_{stop}",
                        main_path_coeff[None, start:stop],
                        x31_block,
                    )[0]
                    main_x31_sum = fnp.add(main_x31_sum, block_x31_sum)
                self._observe(f"terminal_stream_block_{start}_{stop}")

        if kink32.shape[0] > 0:
            sampled_kink = fnp.divide(
                fnp.add(pilot_kink_sum, main_kink_sum),
                fnp.float32(TOTAL_PATHS),
            )
            index_parts.append(kink32)
            value_parts.append(sampled_kink)
        if on32.shape[0] > 0:
            mean_x = self._split_weighted_mean(
                p_x, m_x, pilot_path_coeff, main_path_coeff, "terminal_x_mean"
            )
            mean_x30 = self._split_weighted_mean(
                p_x30,
                m_x30,
                pilot_path_coeff,
                main_path_coeff,
                "terminal_x30_mean",
            )
            mean_x31 = fnp.divide(
                fnp.add(pilot_x31_sum, main_x31_sum),
                fnp.float32(TOTAL_PATHS),
            )
            mean_on = (
                mean_x @ left32[:, on32]
                + mean_x30 @ middle32[:, on32]
                + mean_x31 @ weight32[kink31, :][:, on32]
            )
            index_parts.append(on32)
            value_parts.append(mean_on)
        if dead32.shape[0] > 0:
            index_parts.append(dead32)
            value_parts.append(analytic_means[layer32][dead32])
        final_mean = _assemble_vector(index_parts, value_parts)

        # Formal's moment tangent is linear in the two first-layer residuals;
        # only their complete-frame coefficient surface changed.
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
            raise RuntimeError("setup() did not initialize M145")
        self.dispatch_trace = []
        self.event_log = []
        self.last_transport = {}
        analytic_means, analytic_alphas, firing, analytic_sigmas = (
            _diagonal_gaussian_pass(mlp)
        )
        self._observe("analytic_pass_complete")

        vectors = None
        beta = None
        applied = 0
        if self.transport_enabled:
            surrogate = self._exact_pilot_surrogate(mlp)
            self._observe("pilot_surrogate_complete")
            # Passing the materialized even surrogate twice is algebraically
            # identical to the sidecar's .5*(y_plus+y_minus) interface.
            v, lam, fallback = fit_proposal_f32(
                self._pilot_gaussian, surrogate, surrogate
            )
            tree = explicit_seed_tree(self._setup_seed, int(mlp.seed))
            child_seeds = {
                name: int(tree["children"][name]["seed"])
                for name in ("mixture_labels", "uniform_anchors", "acg_latents")
            }
            anchors, labels = _draw_main_anchors(v, lam, child_seeds)
            weights = _full_mixture_weights(anchors, v, lam)
            frame_coeff, _combined_path = frame_and_path_coefficients(weights)
            pilot_path_coeff, main_path_coeff = self._split_path_coefficients(
                frame_coeff
            )
            vectors, beta = prepare_reflectors(
                self._frame_bank, anchors, self._mean_radius
            )
            self.last_transport = {
                "rank": int(lam.shape[0]),
                "fallback": fallback,
                "lambda_min": float(fnp.min(lam)) if int(lam.shape[0]) else 1.0,
                "lambda_max": float(fnp.max(lam)) if int(lam.shape[0]) else 1.0,
                "weight_min": float(fnp.min(weights)),
                "weight_max": float(fnp.max(weights)),
                "bad_weight_count": int(
                    fnp.sum((~fnp.isfinite(weights)) | (weights <= fnp.float32(0.0)))
                ),
                "label_acg_count": int(fnp.sum(labels)),
                "pilot_surrogate_shape": list(surrogate.shape),
                "seed_tree": tree,
            }
            self.event_log.append("proposal_frozen_from_pilot_only")
            self._observe("proposal_and_reflectors_frozen")
        else:
            frame_coeff = fnp.ones((TOTAL_FRAMES,), dtype=fnp.float32)
            pilot_path_coeff, main_path_coeff = self._split_path_coefficients(
                frame_coeff
            )
            self.last_transport = {
                "rank": 0,
                "fallback": "transport_disabled",
                "weight_min": 1.0,
                "weight_max": 1.0,
                "bad_weight_count": 0,
                "pilot_surrogate_shape": None,
            }
            self.event_log.append("matched_comparator_transport_disabled")

        try:
            if self.transport_enabled:
                for index in range(MAIN_FRAMES):
                    self._apply_one_reflector(index, vectors, beta)
                    applied += 1
                self.event_log.append("main_transport_applied_after_proposal")
                self._observe("main_transport_applied")
            self.event_log.append("split_formal_path_entered")
            prediction = self._split_formal_path(
                mlp,
                analytic_means,
                analytic_alphas,
                firing,
                analytic_sigmas,
                pilot_path_coeff,
                main_path_coeff,
            )
            self.event_log.append("split_formal_path_complete")
            return prediction
        finally:
            if self.transport_enabled:
                for index in range(applied - 1, -1, -1):
                    self._apply_one_reflector(index, vectors, beta)
                # Float32 H(H(Q)) drifts by a few ulps per prediction.  The
                # charged canonical copy makes multi-network reuse exact.
                fnp.copyto(
                    self._frame_bank[PILOT_FRAMES:],
                    self._provisional_main_copy,
                )
                self.event_log.append("main_transport_restored_and_canonicalized")


class MatchedComparator(Estimator):
    """Same provisional radius-scaled frames, transport disabled."""

    transport_enabled = False
