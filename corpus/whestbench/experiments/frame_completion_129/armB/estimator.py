"""ARM B -- the 129-frame real-MUB completion {I} u {H diag(phi_s)/16}.

The ONLY difference from arm A is setup(): the 126 Haar-random orthonormal
frames are replaced by the complete real mutually-unbiased-basis set in R^256,
which makes the antipodally doubled design's degree-4 defect exactly zero.
Everything downstream -- radial conditioning, the exact first-moment and
second-moment controls, the three-terminal-layer fold, the pilots, the tangent
correction, the row-blocked Winograd path -- is byte-identical to arm A.

Frame ORDER is load-bearing and predeclared: the identity basis is placed LAST
(index 128).  The estimator's pilots read rows [0:256] and [0:1024], i.e. frames
0..3; putting the coordinate basis there would make the regime-classification
pilot a deterministic, maximally structured probe and would confound the frame
set with the fold's dead/kink/on split.
"""

from __future__ import annotations

import math
from pathlib import Path

import flopscope.numpy as fnp
from whestbench.domain import MLP

from orthogonal_fold3 import Estimator as _RandomFrameEstimator
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd


def _normalized_hadamard(width: int):
    """Sylvester H_width with entries +-1, divided by sqrt(width)."""
    h = fnp.ones((1, 1), dtype=fnp.float32)
    while h.shape[0] < width:
        top = fnp.concatenate((h, h), axis=1)
        bottom = fnp.concatenate((h, -h), axis=1)
        h = fnp.concatenate((top, bottom), axis=0)
    return h / math.sqrt(width)


class Estimator(_RandomFrameEstimator):
    n_base = 129 * 256

    def setup(self, ctx) -> None:
        if self.n_base % ctx.width:
            raise ValueError("n_base must be an integer number of frames")
        if ctx.width != 256:
            # Preserve the benchmark's small-width contract rather than assert a
            # 256-dimensional MUB construction that does not port.
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

        mean_radius = math.exp(
            0.5 * math.log(2.0)
            + math.lgamma((ctx.width + 1.0) / 2.0)
            - math.lgamma(ctx.width / 2.0)
        )
        hadamard = _normalized_hadamard(ctx.width)
        directions = fnp.empty((self.n_base, ctx.width), dtype=fnp.float32)
        block = directions.reshape(129, ctx.width, ctx.width)
        # frames 0..127: H diag(phi_s) / sqrt(width); frame 128: the identity.
        fnp.multiply(
            hadamard[None, :, :] * mean_radius, phases[:, None, :], out=block[:128]
        )
        fnp.copyto(
            block[128], fnp.eye(ctx.width, dtype=fnp.float32) * mean_radius
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
