"""Production random32,256 estimator with 8192-row Winograd products."""

from orthogonal_fold3 import Estimator as _RandomFrameEstimator
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd


class Estimator(_RandomFrameEstimator):
    """Frozen parent with only its exact sample-product hooks changed."""

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

