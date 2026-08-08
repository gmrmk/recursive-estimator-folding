"""M179 G3: the complete local Jacobian bundle {p, r, K, Hmu, Hv} and the
labelled archive entry, consumable by the m125 LocalReluJacobian ABI.

At each pre-ReLU state (a, C) the bundle is built via the G1 assembly on the
SPD stratum, exact direct limits on the diagonal, and the exact zero-variance
limit on degenerate marginals; rank-one (|rho| > 1 - 2^-52) and non-PSD inputs
FAIL CLOSED (raise) rather than approximate. Generic generated weights are
SPD-interior, so the fail-closed strata are guards, not the working path (a
verified exact rank-one limit is a separately-gated follow-up, per the M177
rank-one policy; approximating it here would violate kill gate 2/3).

Diagonals use the direct limits, never a near-diagonal rule; K is canonicalized
to exact symmetry for the ABI.

Response-free: GENERATED weights only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
M125 = HERE.parent / "m125_source_batched_forward_tangent"
for p in (str(HERE), str(M125)):
    if p not in sys.path:
        sys.path.insert(0, p)

import m179_relu_pair_assembly as asm  # noqa: E402
import m178_certified_phi2_owent as m178  # noqa: E402
import m179_background_producer as prod  # noqa: E402
from m125_forward_tangent import LocalReluJacobian  # noqa: E402


@dataclass(frozen=True)
class BackgroundEntry:
    """Immutable labelled archive entry (M176 ABI). layer is 1-based."""

    layer: int
    mu: np.ndarray                  # (n,) post-ReLU mean
    V: np.ndarray                   # (n, n) post-ReLU covariance, exactly symmetric
    jacobian: LocalReluJacobian     # {p, r, K, Hmu, Hv} at this layer's (a, C)
    cast_provenance: str
    producer_epoch: int
    strata: dict


def build_jacobian(a: np.ndarray, C: np.ndarray):
    """Complete {p, r, K, Hmu, Hv} for X ~ N(a, C) -> LocalReluJacobian.

    Fail-closed on non-PSD and on the rank-one face; the SPD interior and
    zero-variance marginals are exact. Returns (jacobian, m, strata)."""
    a = np.asarray(a, dtype=np.float64)
    C = np.asarray(C, dtype=np.float64)
    n = a.size
    diagC = np.diag(C)
    if np.any(diagC < 0.0):
        raise ValueError("non-PSD input: negative marginal variance")
    sigma = np.sqrt(diagC)

    p = np.zeros(n)
    r = np.zeros(n)
    m = np.zeros(n)
    K = np.zeros((n, n))
    Hmu = np.zeros((n, n))
    Hv = np.zeros((n, n))
    strata = {"spd": 0, "zero_var": 0}

    for i in range(n):
        if sigma[i] <= 0.0:
            p[i] = 1.0 if a[i] > 0.0 else 0.0
            r[i] = 0.0
            m[i] = max(a[i], 0.0)
        else:
            alpha = a[i] / sigma[i]
            p[i] = asm._Phi(alpha)
            r[i] = asm._phi(alpha) / (2.0 * sigma[i])
            m[i] = asm.relu_gaussian_mean(a[i], sigma[i])
        K[i, i] = p[i]
        Hmu[i, i] = 2.0 * m[i] * (1.0 - p[i])
        Hv[i, i] = p[i] - 2.0 * m[i] * r[i]

    for i in range(n):
        for j in range(i + 1, n):
            if sigma[i] <= 0.0 or sigma[j] <= 0.0:
                # a degenerate marginal is a.s. constant: the cross entries
                # collapse to K_ij = 1{a_i>0} * p_j and Hmu = Hv = 0 (derivation
                # in test_m179_jacobian_archive; each verified by the direct
                # definition).
                K[i, j] = K[j, i] = p[i] * p[j]
                strata["zero_var"] += 1
                continue
            rho = C[i, j] / (sigma[i] * sigma[j])
            if abs(rho) > m178.RHO_MAX:
                raise ValueError(
                    f"rank-one face rho={rho!r} at ({i},{j}): exact limit is a "
                    "separately-gated follow-up; refusing rather than clipping")
            pm = asm.pair_moments(a[i], a[j], sigma[i], sigma[j], rho)
            K[i, j] = K[j, i] = pm.K
            Hmu[i, j], Hmu[j, i] = pm.Hmu_ij, pm.Hmu_ji
            Hv[i, j], Hv[j, i] = pm.Hv_ij, pm.Hv_ji
            strata["spd"] += 1

    K = 0.5 * (K + K.T)             # enforce bitwise symmetry for the ABI
    jac = LocalReluJacobian(
        probability=p,
        mean_variance_derivative=r,
        price_kernel=K,
        h_mu=Hmu,
        h_variance=Hv,
    )
    return jac, m, strata


def build_archive(weights, epoch: int = 0):
    """Run the M176 recurrence and emit labelled BackgroundEntry objects l=1..L.

    Each entry carries this layer's post-ReLU (mu, V) and the Jacobian of this
    layer's pre-ReLU state (a, C). The zero-order state advances via the exact
    G2 producer; the archive never feeds a signed tangent back into it."""
    weights = [np.asarray(W, dtype=np.float64) for W in weights]
    n = weights[0].shape[0]
    mu = np.zeros(n)
    V = np.eye(n)
    entries = []
    for layer, W in enumerate(weights, start=1):
        if W.shape != (n, n):
            raise ValueError("constant-width square weights assumed")
        a = mu @ W
        C = W.T @ (V @ W)
        C = 0.5 * (C + C.T)
        jac, _m, strata = build_jacobian(a, C)
        state = prod.relu_moments(a, C)     # exact zero-order advance (G2)
        mu, V = state.mu, state.V
        entries.append(BackgroundEntry(
            layer=layer, mu=mu.copy(), V=V.copy(), jacobian=jac,
            cast_provenance="generated-f64 (no f32 source in this trace)",
            producer_epoch=epoch, strata=strata))
    return entries
