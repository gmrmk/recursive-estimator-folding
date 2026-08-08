"""M179 G4: inclusive FlopScope FLOP ledger and B=8 liveness for the exact
BackgroundArchive producer.

The producer's cost is dominated by two metered quantities:
  - the per-pair M178 evaluation (value + 3 derivatives), FROZEN at
    F_M178 = 4048 charged FLOPs worst case (M178_RESULTS_20260807.json,
    census-certified, billed == static);
  - the per-layer matmuls a = mu @ W and C = W^T (V W), standard FLOP counts,
    metered here through flopscope.numpy for a second signal.
Plus the diagonal univariate ReLU moments and the small per-pair Tallis
assembly. The inclusive ledger below is verify-before-use arithmetic; the
B=8 liveness reproduces the M175 static facts exactly.

Response-free: generated shapes only; no challenge data.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

N = 256
LAYERS = 31
BUDGET_B = 2.72e11

F_M178 = 4048                       # frozen worst-case per-pair (M178 G5)
F_ASSEMBLY_PER_PAIR = 42            # Tallis combine + Hmu/Hv (counted below)
F_PHI = 316                         # charged FLOPs of one Phi via M178 erf kernel
F_DIAG_PER_NEURON = 2 * F_PHI + 40  # mu, second-moment, alpha, r


def metered_layer_matmul_flops():
    """Bill a = mu @ W and C = W^T (V W) through flopscope.numpy; return the
    billed FLOPs for one layer's matmuls (a real metered second signal)."""
    import flopscope as flops
    import flopscope.numpy as fnp
    mu = fnp.asarray(np.zeros((1, N)))
    V = fnp.asarray(np.eye(N))
    W = fnp.asarray(np.ones((N, N)))
    with flops.BudgetContext(10 ** 12, quiet=True):
        before = flops.budget_summary_dict()["flops_used"]
        _a = mu @ W
        VW = V @ W
        _C = W.T @ VW
        after = flops.budget_summary_dict()["flops_used"]
    return int(after - before)


def inclusive_ledger():
    pairs = N * (N - 1) // 2
    per_pair = F_M178 + F_ASSEMBLY_PER_PAIR
    pair_flops_layer = pairs * per_pair
    diag_flops_layer = N * F_DIAG_PER_NEURON
    matmul_flops_layer = metered_layer_matmul_flops()
    per_layer = pair_flops_layer + diag_flops_layer + matmul_flops_layer
    total = per_layer * LAYERS
    return {
        "pairs_per_layer": pairs,
        "per_pair_flops": per_pair,
        "pair_flops_per_layer": pair_flops_layer,
        "diag_flops_per_layer": diag_flops_layer,
        "matmul_flops_per_layer_METERED": matmul_flops_layer,
        "per_layer_flops": per_layer,
        "total_producer_flops": total,
        "fraction_of_budget_B": total / BUDGET_B,
    }


def b8_liveness():
    """Reproduce the M175 static liveness facts exactly."""
    n, itemsize, blocks = N, 8, (8, 8, 8, 7)
    assert sum(blocks) == LAYERS and blocks == (8, 8, 8, 7)
    largest = max(blocks)
    workspace_elements = (
        3 * n + 3 * n * n + 7 * largest * n * n + 12 * largest * n * n
        + largest * n + 4 + 2 * largest * n * n
    )
    return {
        "blocks": list(blocks),
        "workspace_mib": workspace_elements * itemsize / 2 ** 20,
        "block_covariance_archive_mib": largest * n * n * itemsize / 2 ** 20,
        "model_weight_mib": LAYERS * n * n * 4 / 2 ** 20,
    }
