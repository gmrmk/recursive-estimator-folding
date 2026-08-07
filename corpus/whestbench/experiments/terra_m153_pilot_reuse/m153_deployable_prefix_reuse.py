"""M153 guarded pilot-prefix reuse on the repaired sign-Haar M145 branch.

This isolated descendant changes no proposal response or estimator formula. It
only returns already computed float32 pilot states while the Formal active set
is exactly the complete ordered width.  No truth or efficacy interface exists.
"""

from __future__ import annotations

import flopscope.numpy as fnp

from m145_deployable_estimator import (
    DIMENSION,
    PILOT_LINES,
    PILOT_PATHS,
    Estimator as _DeployableM145,
)


class PrefixReuseEstimator(_DeployableM145):
    def __init__(self) -> None:
        super().__init__()
        self._m153_first_pre = None
        self._m153_dense_x2 = None
        self._m153_dense_x3 = None
        self.pilot_reuse_trace: list[str] = []

    def _exact_pilot_surrogate(self, mlp):
        self._m153_first_pre = None
        self._m153_dense_x2 = None
        self._m153_dense_x3 = None
        self.pilot_reuse_trace = []

        first_pre = _DeployableM145._pilot_mm(
            self, "pilot_surrogate:first", self._pilot_gaussian, mlp.weights[0]
        )
        first_cache = fnp.empty((PILOT_LINES, DIMENSION), dtype=fnp.float32)
        fnp.copyto(first_cache, first_pre)
        self._m153_first_pre = first_cache
        x1 = fnp.concatenate(
            (
                fnp.maximum(first_pre, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(first_pre), fnp.float32(0.0)),
            ),
            axis=0,
        )

        pre2 = _DeployableM145._pilot_mm(
            self, "pilot_surrogate:layer2", x1, mlp.weights[1]
        )
        x2 = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        fnp.maximum(pre2, fnp.float32(0.0), out=x2)
        self._m153_dense_x2 = x2
        del x1, pre2

        pre3 = _DeployableM145._pilot_mm(
            self, "pilot_surrogate:layer3", x2, mlp.weights[2]
        )
        x3 = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        fnp.maximum(pre3, fnp.float32(0.0), out=x3)
        self._m153_dense_x3 = x3
        del pre3

        x = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        for layer in range(3, mlp.depth):
            pre = _DeployableM145._pilot_mm(
                self,
                f"pilot_surrogate:layer{layer + 1}",
                x3 if layer == 3 else x,
                mlp.weights[layer],
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

    @staticmethod
    def _is_full_width_pilot_product(left, right) -> bool:
        return tuple(left.shape) == (PILOT_PATHS, DIMENSION) and tuple(
            right.shape
        ) == (DIMENSION, DIMENSION)

    def _pilot_mm(self, stage: str, left, right):
        if stage == "formal:first:pilot":
            if self._m153_first_pre is None:
                raise RuntimeError("M153 cache missing mandatory first pilot state")
            if tuple(left.shape) != (PILOT_LINES, DIMENSION) or tuple(
                right.shape
            ) != (DIMENSION, DIMENSION):
                raise RuntimeError("M153 first pilot geometry changed")
            cached = self._m153_first_pre
            self._m153_first_pre = None
            self.pilot_reuse_trace.append(stage)
            return cached

        if stage == "formal:layer2:pilot" and self._m153_dense_x2 is not None:
            if self._is_full_width_pilot_product(left, right):
                cached = self._m153_dense_x2
                self._m153_dense_x2 = None
                self.pilot_reuse_trace.append(stage)
                return cached
            self._m153_dense_x2 = None
            self._m153_dense_x3 = None

        if stage == "formal:layer3:pilot" and self._m153_dense_x3 is not None:
            if self._is_full_width_pilot_product(left, right):
                cached = self._m153_dense_x3
                self._m153_dense_x3 = None
                self.pilot_reuse_trace.append(stage)
                return cached
            self._m153_dense_x3 = None

        return _DeployableM145._pilot_mm(self, stage, left, right)

