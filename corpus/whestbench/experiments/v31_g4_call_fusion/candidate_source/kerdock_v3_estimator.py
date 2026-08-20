"""Kerdock126 memory-fold composed with the frozen row-blocked L1 backend.

This implementation is an isolated generated-network audit target.  It does
not access a dataset or competition result.
"""

from __future__ import annotations

from pathlib import Path

import flopscope.numpy as fnp
from whestbench.domain import MLP

from fold3_estimator import Estimator as _Fold3Estimator
from row_blocked_winograd import (
    BLOCK_ROWS,
    GroupedRowBlockedBatchedWinograd,
)


MEAN_CHI_256 = 15.98438266660852747


def _normalized_hadamard_rows(frames):
    """Apply normalized H_256 to each frame's row axis."""
    transformed = frames
    half = 1
    while half < frames.shape[1]:
        blocks = transformed.reshape(
            (frames.shape[0], -1, 2, half, frames.shape[2])
        )
        left = blocks[:, :, 0, :, :]
        right = blocks[:, :, 1, :, :]
        transformed = fnp.stack((left + right, left - right), axis=2).reshape(
            frames.shape
        )
        half *= 2
    return transformed / 16.0


class Estimator(_Fold3Estimator):
    """Frozen Kerdock trim with exact phased-WHT first product.

    The first product uses ``H diag(phase) (Q.T @ W1)`` per frozen frame,
    rather than retaining the equivalent 32,256-by-256 direction matrix.
    It is a predeclared memory/lifetime mutation; later sample products retain
    the same row-blocked Batched-B Winograd arithmetic.
    """

    n_base = 126 * 256
    radial_conditioning = True
    pilot_base = 256
    fold_pilot_base = 1_024
    phase_start = 2
    phase_stop = 128

    def _allocate_grouped_activation(self, width: int) -> None:
        """Own the sole sampled activation and its group views from setup."""
        self._activation = fnp.empty(
            (2 * self.n_base, int(width)), dtype=fnp.float32
        )

    def setup(self, ctx) -> None:
        self._context_width = ctx.width
        if ctx.width != 256:
            # Keep the benchmark's small-width contract while avoiding a
            # false claim that the frozen 256-dimensional construction ports.
            super().setup(ctx)
            self._allocate_grouped_activation(ctx.width)
            self._winograd = GroupedRowBlockedBatchedWinograd(
                2 * self.n_base, ctx.width, BLOCK_ROWS
            )
            self._winograd.bind(self._activation)
            return
        if ctx.submission_dir is None:
            raise RuntimeError("submission_dir is required for the Kerdock asset")
        archive = fnp.load(str(Path(ctx.submission_dir) / "kerdock_phases.npz"))
        packed = archive["negative_bits"]
        negative = fnp.unpackbits(packed, axis=1, bitorder="little")[:, :256]
        phases = 1.0 - 2.0 * negative.astype(fnp.float32)
        phases = phases[self.phase_start : self.phase_stop]
        if phases.shape != (126, 256):
            raise RuntimeError(f"frozen trim has unexpected shape {phases.shape}")
        # Compact, immutable-equivalent state: 126 phase vectors, one normalized
        # Walsh matrix, and one half-frame butterfly scratch.  No full direction
        # array is retained after setup.
        identity = fnp.eye(ctx.width, dtype=fnp.float32)
        self._phase_signs = phases
        self._hadamard = _normalized_hadamard_rows(identity[None])[0]
        self._wht_scratch = fnp.empty(
            (self.phase_stop - self.phase_start, ctx.width // 2, ctx.width),
            dtype=fnp.float32,
        )
        self._radial_covariance = MEAN_CHI_256 * MEAN_CHI_256 / ctx.width
        # BaseEstimator initializes this member for random samplers.  Removing
        # it makes the no-persistent-direction ownership invariant executable.
        del self._gaussian
        self._allocate_grouped_activation(ctx.width)
        self._winograd = GroupedRowBlockedBatchedWinograd(
            2 * self.n_base, ctx.width, BLOCK_ROWS
        )
        self._winograd.bind(self._activation)

    def _initial_sample_state(self):
        # Fold3 passes this state only to the first-product hook.  It is compact
        # and keeps the exact frame sequence s=2,...,127.
        if self._context_width != 256:
            return self._gaussian
        return self._phase_signs

    def _release_initial_sample_state(self) -> None:
        # Phase/Hadamard state is tiny and intentionally retained for static
        # ownership audit; no full direction storage exists to release.
        return None

    def _first_sample_matmul(self, phases, weight, *, out=None):
        """Return the exact Kerdock first preactivation without directions.

        For frame ``s``, this computes
        ``mean_chi * H_256 @ (diag(phase_s) @ weight)`` in phase order.  The
        butterfly is exact algebraically and each multiply/add/subtract stays
        inside FlopScope prediction billing.
        """
        if self._context_width != 256:
            return fnp.matmul(phases, weight, out=out)
        if out is None:
            output = fnp.empty((self.n_base, weight.shape[1]), dtype=fnp.float32)
        else:
            if out.shape != (self.n_base, weight.shape[1]):
                raise ValueError("first-product output has unexpected shape")
            output = out
        frames = output.reshape(self.phase_stop - self.phase_start, 256, weight.shape[1])
        fnp.multiply(phases[:, :, None], weight[None, :, :], out=frames)
        half = 1
        while half < 256:
            pairs = frames.reshape(frames.shape[0], -1, 2, half, frames.shape[2])
            left = pairs[:, :, 0]
            right = pairs[:, :, 1]
            scratch = self._wht_scratch.reshape(-1)[: left.size].reshape(left.shape)
            fnp.copyto(scratch, left)
            fnp.add(scratch, right, out=left)
            fnp.subtract(scratch, right, out=right)
            half *= 2
        fnp.multiply(output, MEAN_CHI_256 / 16.0, out=output)
        return output

    def _sample_matmul(self, values, weight, firing_rates, *, out):
        _ = firing_rates
        return self._winograd.multiply(values, weight, out=out)

    @staticmethod
    def _haar_rotation(seed: int, width: int):
        rng = fnp.random.default_rng(seed)
        raw = rng.standard_normal((width, width), dtype=fnp.float32)
        rotation, triangular = fnp.linalg.qr(raw)
        signs = fnp.where(fnp.diag(triangular) < 0.0, -1.0, 1.0)
        return rotation * signs[None, :]

    def predict(self, mlp: MLP, budget):
        if mlp.width != 256:
            return super().predict(mlp, budget)
        rotation = self._haar_rotation(int(mlp.seed), mlp.width)
        first_weight = rotation.T @ mlp.weights[0]
        self._trace_stage("haar_absorbed")
        rotated = MLP(
            width=mlp.width,
            depth=mlp.depth,
            weights=[first_weight, *mlp.weights[1:]],
            seed=mlp.seed,
            name=mlp.name,
        )
        return super().predict(rotated, budget)
