"""Response-free zero-variance totality guard for the M204 B=1 control.

M204 deliberately requires at least one positive covariance diagonal when it
normalizes its rank-one factor.  A legitimate deterministic background has
``V == 0`` instead.  This separate child preserves M204 unchanged and maps
that one valid boundary stratum to its exact zero-control 49-node state.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
M204 = HERE.parent / "m204_lowrank_b1_lifted_control"
if str(M204) not in sys.path:
    sys.path.insert(0, str(M204))

import m204_lowrank_b1_lifted_control as m204  # noqa: E402


def rank_one_state_from_background(mean: np.ndarray, covariance: np.ndarray) -> m204.RankOneB1State:
    """Return M204's state, with an exact all-zero-covariance boundary guard.

    A matrix with zero diagonal but a nonzero off-diagonal cannot be a valid
    covariance.  It is rejected instead of being silently discarded.  Every
    state with at least one positive variance delegates directly to M204, so
    the interior algebra and its exact byte-level operation order are retained.
    """

    mu = m204._finite_vector(mean, "mean")
    v = m204._finite_square(covariance, "covariance")
    if v.shape[0] != mu.size:
        raise ValueError("mean/covariance widths disagree")
    diagonal = np.diag(v).copy()
    if np.any(diagonal < 0.0):
        raise ValueError("negative covariance diagonal")
    if np.any(diagonal > 0.0):
        return m204.build_rank_one_b1_state(mu, v)
    if not np.array_equal(v, np.zeros_like(v)):
        raise ValueError("all-zero covariance diagonal requires an all-zero covariance matrix")

    omega = np.zeros(m204.B1_NODE_COUNT, dtype=np.float64)
    omega[:2] = 0.5
    conditional_mean = np.broadcast_to(mu, (m204.B1_NODE_COUNT, mu.size)).copy()
    conditional_variance = np.zeros_like(conditional_mean)
    return m204.RankOneB1State(
        omega=omega,
        conditional_mean=conditional_mean,
        conditional_variance=conditional_variance,
        rank_factor=np.zeros_like(mu),
        diagonal_residual=np.zeros_like(mu),
    )
