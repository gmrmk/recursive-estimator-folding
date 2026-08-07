"""Replicated randomized-QMC version of the late-fold estimator."""

from __future__ import annotations

import math
from pathlib import Path

import flopscope.numpy as fnp

from fold_estimator import Estimator as _FoldEstimator


class Estimator(_FoldEstimator):
    """Use several digital shifts of a shorter Sobol prefix at fixed cost."""

    n_base = 14_000
    n_replicates = 2

    def setup(self, ctx) -> None:
        if ctx.submission_dir is None:
            raise RuntimeError("submission_dir is required to load Sobol points")
        if self.n_base % self.n_replicates != 0:
            raise ValueError("n_base must be divisible by n_replicates")
        per_replicate = self.n_base // self.n_replicates
        archive_path = Path(ctx.submission_dir) / "sobol_owen_u32.npz"
        raw = fnp.load(str(archive_path))["points"][:per_replicate, : ctx.width]
        if raw.shape != (per_replicate, ctx.width):
            raise ValueError(
                f"Sobol asset shape {raw.shape}, expected "
                f"({per_replicate}, {ctx.width})"
            )

        rng = fnp.random.default_rng(ctx.seed)
        replicate_gaussians = []
        for _ in range(self.n_replicates):
            shift = rng.integers(0, 2**32, size=(ctx.width,), dtype=fnp.uint32)
            shifted = fnp.bitwise_xor(raw, shift)
            uniform = (shifted.astype(fnp.float64) + 0.5) / float(2**32)
            u_radius = uniform[:, 0::2]
            u_angle = uniform[:, 1::2]
            radius = fnp.sqrt(-2.0 * fnp.log(u_radius))
            angle = (2.0 * fnp.pi) * u_angle
            pairs = fnp.stack(
                (radius * fnp.cos(angle), radius * fnp.sin(angle)), axis=2
            )
            gaussian = pairs.reshape(uniform.shape).astype(fnp.float32)
            replicate_gaussians.append(gaussian)

        gaussian = fnp.concatenate(replicate_gaussians, axis=0)
        if self.radial_conditioning:
            mean_radius = math.exp(
                0.5 * math.log(2.0)
                + math.lgamma((ctx.width + 1.0) / 2.0)
                - math.lgamma(ctx.width / 2.0)
            )
            radii = fnp.sqrt(fnp.sum(gaussian * gaussian, axis=1))
            gaussian = gaussian * (
                mean_radius / fnp.maximum(radii, 1e-12)
            )[:, None]
            self._radial_covariance = mean_radius * mean_radius / ctx.width
        self._gaussian = gaussian
