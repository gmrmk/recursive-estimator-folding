"""Batched orthogonal frames with three-terminal-layer folding."""

from __future__ import annotations

import math

import flopscope.numpy as fnp

from fold3_estimator import Estimator as _Fold3Estimator


class Estimator(_Fold3Estimator):
    radial_conditioning = True
    pilot_base = 256
    fold_pilot_base = 1_024

    def setup(self, ctx) -> None:
        if self.n_base % ctx.width:
            raise ValueError("n_base must be an integer number of frames")
        n_frames = self.n_base // ctx.width
        rng = fnp.random.default_rng(ctx.seed)
        mean_radius = math.exp(
            0.5 * math.log(2.0)
            + math.lgamma((ctx.width + 1.0) / 2.0)
            - math.lgamma(ctx.width / 2.0)
        )
        raw = rng.standard_normal(
            (n_frames, ctx.width, ctx.width), dtype=fnp.float32
        )
        q, _r = fnp.linalg.qr(raw)
        self._gaussian = (q.reshape((self.n_base, ctx.width)) * mean_radius).astype(
            fnp.float32
        )
        self._radial_covariance = mean_radius * mean_radius / ctx.width

