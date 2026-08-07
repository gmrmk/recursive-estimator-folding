"""M153 truth-free prototype: exact all-active pilot-prefix memoization.

This is an isolated descendant of the frozen M145 integrated estimator.  It
does not alter M145, the Formal-L1 source, the proposal, frame bank, weights,
or comparator.  It caches only the dense pilot state that is a byte-for-byte
replacement for a same-shape Formal pilot product.  At the first non-full
Formal active set the cache is deliberately not consulted.
"""

from __future__ import annotations

import flopscope.numpy as fnp

from m145_integrated_estimator import (
    DIMENSION,
    PILOT_LINES,
    PILOT_PATHS,
    Estimator as _M145Estimator,
)


class PrefixReuseEstimator(_M145Estimator):
    """Reuse the maximal observed all-active prefix and fail closed otherwise.

    ``formal:first:pilot`` is always exact because both paths start from the
    same immutable 1024 pilot rows.  Later states are reusable only while the
    Formal path's right operand remains 256 by 256: sorted unique active sets
    of cardinality 256 are necessarily the full ordered width, so the dense
    and Formal operators have identical float32 operands and geometry.
    """

    def __init__(self) -> None:
        super().__init__()
        self._m153_first_pre = None
        self._m153_dense_x2 = None
        self._m153_dense_x3 = None
        self.pilot_reuse_trace: list[str] = []

    def _exact_pilot_surrogate(self, mlp):
        """Run M145's same 32-layer dense pilot while retaining its prefix.

        The independent buffers are necessary: M145's original dense forward
        overwrites its activation buffer at each layer, while the later Formal
        pass needs first-preactivation and activated layers two and three.
        No response is transformed, reordered, or otherwise changed.
        """

        self._m153_first_pre = None
        self._m153_dense_x2 = None
        self._m153_dense_x3 = None
        self.pilot_reuse_trace = []

        first_pre = super()._pilot_mm(
            "pilot_surrogate:first", self._pilot_gaussian, mlp.weights[0]
        )
        first_pre_cache = fnp.empty(
            (PILOT_LINES, DIMENSION), dtype=fnp.float32
        )
        fnp.copyto(first_pre_cache, first_pre)
        self._m153_first_pre = first_pre_cache

        x1 = fnp.concatenate(
            (
                fnp.maximum(first_pre, fnp.float32(0.0)),
                fnp.maximum(fnp.negative(first_pre), fnp.float32(0.0)),
            ),
            axis=0,
        )

        pre2 = super()._pilot_mm(
            "pilot_surrogate:layer2", x1, mlp.weights[1]
        )
        x2 = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        fnp.maximum(pre2, fnp.float32(0.0), out=x2)
        self._m153_dense_x2 = x2
        # The x1 cache has served its only dense-pilot consumer.  Keeping it
        # live would turn an intentional bounded cache into an avoidable peak.
        del x1, pre2

        pre3 = super()._pilot_mm(
            "pilot_surrogate:layer3", x2, mlp.weights[2]
        )
        x3 = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        fnp.maximum(pre3, fnp.float32(0.0), out=x3)
        self._m153_dense_x3 = x3
        del pre3

        # x3 must remain immutable until Formal consumes it, so complete the
        # dense proposal pilot in a fourth buffer.  Thereafter in-place ReLU
        # writes are identical to M145's original schedule.
        x = fnp.empty((PILOT_PATHS, DIMENSION), dtype=fnp.float32)
        for layer in range(3, mlp.depth):
            pre = super()._pilot_mm(
                f"pilot_surrogate:layer{layer + 1}", x3 if layer == 3 else x,
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
        """Return a cached state only for an identical Formal product.

        The caller immediately applies ReLU.  Layers two and three are stored
        after that same ReLU, so their reapplication is idempotent, including
        IEEE NaNs and signed zero.  Any reduced active width follows M145's
        normal product path; no column-slice algebra is accepted as a rounding
        substitute.
        """

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
            # A reduced first active set invalidates every later dense state
            # as a Formal substitute, so release both rather than carrying
            # an unusable cache through the main stream.
            self._m153_dense_x2 = None
            self._m153_dense_x3 = None

        if stage == "formal:layer3:pilot" and self._m153_dense_x3 is not None:
            if self._is_full_width_pilot_product(left, right):
                cached = self._m153_dense_x3
                self._m153_dense_x3 = None
                self.pilot_reuse_trace.append(stage)
                return cached
            self._m153_dense_x3 = None

        return super()._pilot_mm(stage, left, right)
