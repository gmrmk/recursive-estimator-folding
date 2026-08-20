"""ARM A -- 126 Haar-random orthonormal frames (the shipped row_blocked carrier).

Identical to corpus row_blocked_production/candidate_source/estimator.py except
for the per-network Haar rotation, which is lifted verbatim from the deployed
kerdock_v3 champion and applied in ALL THREE arms so the arms differ in exactly
one thing: the frame set.  For Haar frames the rotation is distributionally
vacuous (Haar x Haar = Haar); it is present only to hold the billed structure
identical to arms B and C, where it is mathematically required.
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench.domain import MLP

from orthogonal_fold3 import Estimator as _RandomFrameEstimator
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd


class Estimator(_RandomFrameEstimator):
    n_base = 126 * 256

    def setup(self, ctx) -> None:
        super().setup(ctx)
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
