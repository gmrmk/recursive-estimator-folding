"""M179 zero-order full-covariance BackgroundArchive recurrence (G2).

Exact Gaussian-closure recurrence of the M176 contract, using the G1 pair
assembly (M178 provider) for off-diagonal post-ReLU second moments and the
arc-whitebox-estimator univariate backbone for the diagonal. This is the
exact-bivariate UPGRADE of that repo's off-diagonal gain approximation.

Convention (competition / base_estimator, row-vector): weights is a list of
(n, n) matrices; mu_0 = 0 (n,), V_0 = I (n,n); per layer
    a = mu @ W ;  C = W.T @ V @ W ;  (mu, V) <- post-ReLU moments of N(a, C).
The recurrence computes the EXACT moments UNDER the per-layer Gaussian closure
(the standard moment-propagation model); it is not the true non-Gaussian
network law at depth >= 2.

G2 scope: the SPD stratum (generic generated weights). Exact rank-one /
zero-variance / non-PSD dispatch is G3. A pair whose |rho| exceeds the M178
SPD bound raises (no clip/floor/ridge) so the SPD assumption is verified, never
silently violated. Response-free; runs on GENERATED weights only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m179_relu_pair_assembly as asm  # noqa: E402
import m178_certified_phi2_owent as m178  # noqa: E402


@dataclass(frozen=True)
class BackgroundState:
    """One layer's exact zero-order post-ReLU moments (float64)."""

    mu: np.ndarray          # (n,)
    V: np.ndarray           # (n, n), exactly symmetric
    strata: dict            # count of pairs by stratum (audit)


def relu_moments(a: np.ndarray, C: np.ndarray) -> BackgroundState:
    """Exact post-ReLU (mu, V) of X ~ N(a, C) on the SPD stratum.

    a: (n,) pre-activation means; C: (n, n) pre-activation covariance (PSD,
    symmetric). Returns post-ReLU mean and exactly-symmetric covariance.
    """
    a = np.asarray(a, dtype=np.float64)
    C = np.asarray(C, dtype=np.float64)
    n = a.size
    diagC = np.diag(C)
    if np.any(diagC < 0.0):
        raise ValueError("negative pre-activation variance (non-PSD input)")
    sigma = np.sqrt(diagC)

    mu = np.empty(n, dtype=np.float64)
    V = np.zeros((n, n), dtype=np.float64)
    strata = {"spd": 0, "zero_var_diag": 0}

    # diagonal via the exact univariate backbone (never a near-diagonal rule)
    for i in range(n):
        mu[i] = asm.relu_gaussian_mean(a[i], sigma[i])
        V[i, i] = asm.relu_gaussian_second_moment(a[i], sigma[i]) - mu[i] * mu[i]
        if sigma[i] <= 0.0:
            strata["zero_var_diag"] += 1

    # off-diagonal via the G1 assembly (M178), upper triangle then mirror
    for i in range(n):
        if sigma[i] <= 0.0:
            continue
        for j in range(i + 1, n):
            if sigma[j] <= 0.0:
                continue
            rho = C[i, j] / (sigma[i] * sigma[j])
            if abs(rho) > m178.RHO_MAX:
                raise ValueError(
                    f"pair ({i},{j}) rho={rho!r} exceeds SPD bound; "
                    "rank-one/zero-var dispatch is G3, not G2")
            pm = asm.pair_moments(a[i], a[j], sigma[i], sigma[j], rho)
            V[i, j] = pm.cov
            V[j, i] = pm.cov            # exact symmetry by construction
            strata["spd"] += 1

    return BackgroundState(mu=mu, V=V, strata=strata)


def zero_order_recurrence(weights) -> list[BackgroundState]:
    """Run the M176 zero-order recurrence over a list of (n, n) weights.

    Returns the post-ReLU states [ (mu_1, V_1), ..., (mu_L, V_L) ]. The caller
    scores mu of the terminal state; the archive (G3+) retains l=1..L-1 plus
    the terminal, with the Jacobian bundles.
    """
    weights = [np.asarray(W, dtype=np.float64) for W in weights]
    n = weights[0].shape[0]
    mu = np.zeros(n, dtype=np.float64)
    V = np.eye(n, dtype=np.float64)
    states = []
    for W in weights:
        if W.shape != (n, n):
            raise ValueError("this recurrence assumes square constant-width weights")
        a = mu @ W
        C = W.T @ (V @ W)
        C = 0.5 * (C + C.T)          # canonicalize the two-sided GEMM triangles
        state = relu_moments(a, C)
        mu, V = state.mu, state.V
        states.append(state)
    return states
