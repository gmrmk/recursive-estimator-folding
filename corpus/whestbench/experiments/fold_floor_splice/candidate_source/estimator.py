"""Fold-floor candidate: the champion routed through the depth-swept floor.

The incumbent is `random32256_rowwinograd8192`: the same geometry, frames,
antipodes, pilot rescue, fold3, moment tangent, seeds and float32 path, with
its two sample products on a one-level row-blocked Batched-B Winograd.  This
fork changes the operator and nothing else about the sampler.

``USE_FLOOR``
    ``True`` selects ``depth6_winograd.DepthWinograd``.  ``False`` restores the
    frozen ``RowBlockedBatchedWinograd`` byte for byte, which is the fallback
    the whole splice is gated against.

``FLOOR_MAX_LEVELS``
    The depth the sweep is allowed to reach.  The sweep minimizes *analytical*
    FLOPs and therefore picks 6, but effective compute is
    ``analytical + 100e9 * residual_seconds``, and residual grows with depth.
    Measured end to end by ``verify_fold_floor.py --full``: two synthetic
    width-256 depth-32 He nets, median of three predicts each, one
    BudgetContext per predict so the residual is the scorer's own
    ``residual_wall_time_s`` (incumbent: 186.4B / 186.2B analytical,
    0.1503 s / 0.1459 s residual, C 201.43B / 200.82B):

        route        FLOPs/inc   residual s   wall/inc   C ratio    dev/inc
        ---------    ---------   ----------   --------   --------   -------
        fold3 only    .993/.997   .1522/.1469  1.10/1.04  .994/.997  1.1/1.0
        floor L3      .772/.776   .2696/.2701  3.96/3.74  .848/.854  2.7/2.4
        floor L4      .712/.725   .2955/.3297  6.13/6.10  .806/.837  2.8/3.7
        floor L5      .696/.714   .3525/.3522  9.68/8.48  .819/.838  4.7/5.0
        floor L6      .695/.713   .3629/.3396 11.09/9.07  .823/.831  5.3/5.4

    ``dev/inc`` is the fork's float32 deviation from the plain-product route
    divided by the incumbent's own, so the incumbent's published raw-MSE shift
    of 0.001704% scales to a projected 4.7e-5 / 6.3e-5 at depth 4 and
    9.1e-5 / 9.3e-5 at depth 6, against a 5e-4 per-net parity ceiling.

    Depth 4 is the shipped cap: it has the best measured C on both nets, the
    widest parity margin of the winning depths, and roughly half the wall time
    of depth 6.  Set the constant to 6 to run the floor route at its
    minimum-FLOP depth; the depth-6 schedule is realized and self-checked
    either way.

``FLOOR_WORKSPACE_MIB``
    Bounds the three pooled scratch buffers, and therefore the row block.  At
    depth 4 the traced peak of one predict is 631 MiB against the incumbent's
    334 MiB (1.89x).  256 MiB of workspace measured slightly better C and
    689 MiB of peak; 96 MiB measured 553 MiB of peak and clearly worse C.  192
    is the shipped compromise, chosen because this lineage has already lost one
    candidate to memory (the 667 MiB full-height operator).

THE TWO RISKS, STATED BEFORE THE WIN
    Wall time per predict goes 2.5 s -> 15.4 s at depth 4 (6.1x), because the
    depth-L leaf products are small enough that BLAS dispatch dominates.  The C
    law excludes backend time, so effective compute still improves, but a
    graded run of 100 nets goes from roughly 4 minutes to roughly 26, and any
    per-net wall limit fails first.  Peak memory is 1.89x the incumbent's.
    Neither risk is visible in the score; both are visible in a runner.
"""

from orthogonal_fold3 import Estimator as _RandomFrameEstimator
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd
from depth6_winograd import DepthWinograd


USE_FLOOR = True
FLOOR_MAX_LEVELS = 4
FLOOR_WORKSPACE_MIB = 192.0


class Estimator(_RandomFrameEstimator):
    """Frozen parent with only its exact sample-product hooks changed."""

    n_base = 126 * 256

    def setup(self, ctx) -> None:
        super().setup(ctx)
        if USE_FLOOR:
            self._winograd = DepthWinograd(
                2 * self.n_base,
                ctx.width,
                workspace_mib=FLOOR_WORKSPACE_MIB,
                max_levels=FLOOR_MAX_LEVELS,
            )
        else:
            self._winograd = RowBlockedBatchedWinograd(
                2 * self.n_base, ctx.width, BLOCK_ROWS
            )

    def _first_sample_matmul(self, values, weight):
        return self._winograd.multiply(values, weight)

    def _sample_matmul(self, values, weight, firing_rates):
        _ = firing_rates
        return self._winograd.multiply(values, weight)
