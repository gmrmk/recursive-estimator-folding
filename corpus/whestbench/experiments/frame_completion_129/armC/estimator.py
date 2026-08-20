"""ARM C -- the Kerdock-126 design {H diag(phi_s)/16, s = 2..127}.

THE THIRD ARM (amendment H2, AGENT_CHANNEL.md [2026-08-19 ~01:0x UTC], the
A_4 reconciliation pre-registration).  Arm C is the DECOMPOSITION arm and is
REPORTED, never gated.  It carries the same point count as arm A (126 frames,
32,256 base rows) and the same frame family as arm B (phased Hadamard from the
shipped kerdock_phases.npz), which splits the arm A -> arm B contrast into its
two physical causes:

    A -> C   design quality   Haar-random frames -> mutually unbiased frames,
                              at fixed point count; A_4 falls by 42 and 2/3.
    C -> B   completion       126 -> 129 frames, at fixed design family;
                              A_4 falls from its Kerdock value to exactly zero,
                              and the score law charges for three more frames.

The phase trim s = 2..127 is the champion's own frozen Kerdock-126 selection,
lifted verbatim from v31_guards/package_source/kerdock_v3_estimator.py
(phase_start = 2, phase_stop = 128), so arm C is the deployed structured design
rather than a fresh 126-subset chosen by this cell.

Construction, not memory layout, is what is matched here: arm C builds the
explicit direction array exactly as arms A and B do, rather than the champion's
phase/butterfly memory fold, so that all three arms bill the same first-product
arithmetic and the frame set stays the single manipulated variable.  The
champion's memory-fold optimisation is a separate mechanism with its own record
and is deliberately out of scope.

Arms B and C share phased-Hadamard pilot rows, so the C -> B completion
contrast is the one contrast in this cell whose pilot-probe structure is
matched; the pilot-structure confound lives entirely in A -> C.
"""

from __future__ import annotations

import math
from pathlib import Path

import flopscope.numpy as fnp
from whestbench.domain import MLP

from orthogonal_fold3 import Estimator as _RandomFrameEstimator
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd


PHASE_START = 2
PHASE_STOP = 128


def _normalized_hadamard(width: int):
    """Sylvester H_width with entries +-1, divided by sqrt(width)."""
    h = fnp.ones((1, 1), dtype=fnp.float32)
    while h.shape[0] < width:
        top = fnp.concatenate((h, h), axis=1)
        bottom = fnp.concatenate((h, -h), axis=1)
        h = fnp.concatenate((top, bottom), axis=0)
    return h / math.sqrt(width)


class Estimator(_RandomFrameEstimator):
    n_base = 126 * 256

    def setup(self, ctx) -> None:
        if self.n_base % ctx.width:
            raise ValueError("n_base must be an integer number of frames")
        if ctx.width != 256:
            # Preserve the benchmark's small-width contract rather than assert a
            # 256-dimensional Kerdock construction that does not port.
            super().setup(ctx)
            self._winograd = RowBlockedBatchedWinograd(
                2 * self.n_base, ctx.width, BLOCK_ROWS
            )
            return
        if ctx.submission_dir is None:
            raise RuntimeError("submission_dir is required for the Kerdock asset")
        archive = fnp.load(str(Path(ctx.submission_dir) / "kerdock_phases.npz"))
        negative = fnp.unpackbits(
            archive["negative_bits"], axis=1, bitorder="little"
        )[:, : ctx.width]
        phases = 1.0 - 2.0 * negative.astype(fnp.float32)
        if phases.shape != (128, ctx.width):
            raise RuntimeError(f"phase asset has unexpected shape {phases.shape}")
        phases = phases[PHASE_START:PHASE_STOP]
        if phases.shape != (126, ctx.width):
            raise RuntimeError(f"frozen trim has unexpected shape {phases.shape}")

        mean_radius = math.exp(
            0.5 * math.log(2.0)
            + math.lgamma((ctx.width + 1.0) / 2.0)
            - math.lgamma(ctx.width / 2.0)
        )
        hadamard = _normalized_hadamard(ctx.width)
        directions = fnp.empty((self.n_base, ctx.width), dtype=fnp.float32)
        block = directions.reshape(126, ctx.width, ctx.width)
        fnp.multiply(
            hadamard[None, :, :] * mean_radius, phases[:, None, :], out=block
        )
        self._gaussian = directions
        self._radial_covariance = mean_radius * mean_radius / ctx.width
        self._winograd = RowBlockedBatchedWinograd(
            2 * self.n_base, ctx.width, BLOCK_ROWS
        )

    def _first_sample_matmul(self, values, weight):
        return self._winograd.multiply(values, weight)

    def _sample_matmul(self, values, weight, firing_rates):
        _ = firing_rates
        return self._winograd.multiply(values, weight)

    @staticmethod
    def _haar_rotation(seed: int, width: int):
        rng = fnp.random.default_rng(seed)
        raw = rng.standard_normal((width, width), dtype=fnp.float32)
        rotation, triangular = fnp.linalg.qr(raw)
        signs = fnp.where(fnp.diag(triangular) < 0.0, -1.0, 1.0)
        return rotation * signs[None, :]

    def predict(self, mlp: MLP, budget):
        rotation = self._haar_rotation(int(mlp.seed), mlp.width)
        rotated = MLP(
            width=mlp.width,
            depth=mlp.depth,
            weights=[rotation.T @ mlp.weights[0], *mlp.weights[1:]],
            seed=mlp.seed,
            name=mlp.name,
        )
        return super().predict(rotated, budget)
