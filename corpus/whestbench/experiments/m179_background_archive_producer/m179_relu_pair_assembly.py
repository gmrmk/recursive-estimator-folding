"""M179 assembly premise: exact bivariate ReLU pair moments and the complete
M125b local Jacobian bundle, assembled ENTIRELY from the M178 certified
provider's four outputs (value + three derivatives) plus the univariate ReLU
backbone.

This is the cheapest M179 falsifier (fold ladder G1-premise): if these
closed forms cannot reconstruct E[ReLU_i ReLU_j] and {K, Hmu, Hv} to reference
accuracy, the whole producer is dead at the assembly link and M178 is
preserved for a different M180 decomposition.

Mathematics (predeclared in M179_PREDECLARED_PROTOCOL_20260807.md):
  standardize alpha_i = a_i/sigma_i, rho = C_ij/(sigma_i sigma_j), s^2=1-rho^2.
  M178.evaluate(alpha_i, alpha_j, rho) -> K=value, Da=dV/da, Db=dV/db, Dr=dV/drho.
  Truncated moments over R = {X_i>0, X_j>0} (Tallis):
    E[Z_i 1_R]     = Da + rho*Db
    E[Z_j 1_R]     = Db + rho*Da
    E[Z_i Z_j 1_R] = rho*K - rho*(alpha_i*Da + alpha_j*Db) + s^2*Dr
  E[ReLU_i ReLU_j] = a_i a_j K + a_i sigma_j E[Z_j 1_R]
                   + a_j sigma_i E[Z_i 1_R] + sigma_i sigma_j E[Z_i Z_j 1_R].
Provider outputs are the exact cone first-moment pieces (m86 coarea identity
m_s = mu p_s + Sigma grad_mu p_s); the univariate backbone is the
arc-whitebox-estimator identity re-expressed through M178's certified kernels.

Response-free: no challenge instance, target, scorer, or model loop. This
module runs on plain scalars/small arrays; the FlopScope-metered target-width
producer is a later sub-gate (G4).
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
M178 = HERE.parent / "m178_certified_phi2_owent"
if str(M178) not in sys.path:
    sys.path.insert(0, str(M178))

import m178_certified_phi2_owent as m178  # noqa: E402

_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _phi(x: float) -> float:
    return _INV_SQRT_2PI * math.exp(-0.5 * x * x)


def _Phi(x: float) -> float:
    # certified univariate normal CDF via the M178 erf kernel (no scipy/opaque
    # CDF): reuse the provider's own erf chart through a degenerate call is
    # unnecessary here — the standalone premise may use math.erf for the
    # REFERENCE-adjacent marginal backbone; the metered producer (G2+) will use
    # the M178 kernel exclusively.  math.erf is correctly rounded to ~1 ulp.
    return 0.5 * (1.0 + math.erf(x * m178.INV_SQRT_TWO))


def relu_gaussian_mean(a: float, sigma: float) -> float:
    """E[ReLU(z)], z ~ N(a, sigma^2). arc-whitebox-estimator backbone identity."""
    if sigma <= 0.0:
        return max(a, 0.0)
    alpha = a / sigma
    return a * _Phi(alpha) + sigma * _phi(alpha)


def relu_gaussian_second_moment(a: float, sigma: float) -> float:
    """E[ReLU(z)^2], z ~ N(a, sigma^2). Backbone identity."""
    if sigma <= 0.0:
        return max(a, 0.0) ** 2
    alpha = a / sigma
    return (a * a + sigma * sigma) * _Phi(alpha) + a * sigma * _phi(alpha)


@dataclass(frozen=True)
class PairMoments:
    """Exact pair moments and Jacobian-bundle entries for one (i, j) pair."""

    e_relu_relu: float          # E[ReLU(X_i) ReLU(X_j)]
    cov: float                  # V_l[i,j] = E[ReLU_i ReLU_j] - m_i m_j
    K: float                    # P(X_i>0, X_j>0)
    Hmu_ij: float               # E[1{X_i>0} ReLU(X_j)] - p_i m_j
    Hmu_ji: float               # E[1{X_j>0} ReLU(X_i)] - p_j m_i
    Hv_ij: float
    Hv_ji: float


def pair_moments(a_i, a_j, sigma_i, sigma_j, rho):
    """Assemble the exact pair moments from the M178 provider (SPD stratum).

    a_i, a_j: pre-ReLU means; sigma_i, sigma_j > 0: std devs; rho in (-1, 1).
    Returns PairMoments. Diagonal (i == j) is handled by the caller with the
    exact direct limits, never through this bivariate path.
    """
    alpha_i = a_i / sigma_i
    alpha_j = a_j / sigma_j
    s2 = (1.0 - rho) * (1.0 + rho)
    s = math.sqrt(s2)

    res = m178.evaluate(alpha_i, alpha_j, rho)
    if res.refused:
        raise ValueError(f"M178 refused SPD pair: {res.reason}")
    K = res.value
    Da = res.d_a
    Db = res.d_b
    Dr = res.d_rho

    # Tallis truncated moments over {X_i>0, X_j>0}, all from M178 outputs.
    ez_i = Da + rho * Db
    ez_j = Db + rho * Da
    ez_ij = rho * K - rho * (alpha_i * Da + alpha_j * Db) + s2 * Dr

    e_relu_relu = (
        a_i * a_j * K
        + a_i * sigma_j * ez_j
        + a_j * sigma_i * ez_i
        + sigma_i * sigma_j * ez_ij
    )

    m_i = relu_gaussian_mean(a_i, sigma_i)
    m_j = relu_gaussian_mean(a_j, sigma_j)
    p_i = _Phi(alpha_i)
    p_j = _Phi(alpha_j)
    r_i = _phi(alpha_i) / (2.0 * sigma_i)
    r_j = _phi(alpha_j) / (2.0 * sigma_j)

    # E[1{X_i>0} ReLU(X_j)] = a_j K + sigma_j E[Z_j 1_R]
    hmu_ij = a_j * K + sigma_j * ez_j - p_i * m_j
    hmu_ji = a_i * K + sigma_i * ez_i - p_j * m_i

    # Hv_ij = 0.5 f_{X_i}(0) E[ReLU(X_j)|X_i=0] - r_i m_j, conditional law
    #   X_j | X_i = 0 ~ N(a_j - rho alpha_i sigma_j, sigma_j^2 s^2)
    f_i0 = _phi(alpha_i) / sigma_i
    f_j0 = _phi(alpha_j) / sigma_j
    cond_mean_j = a_j - rho * alpha_i * sigma_j
    cond_mean_i = a_i - rho * alpha_j * sigma_i
    cond_sd = s  # sqrt(s^2); sigma_j * s for the actual sd below
    hv_ij = 0.5 * f_i0 * relu_gaussian_mean(cond_mean_j, sigma_j * cond_sd) - r_i * m_j
    hv_ji = 0.5 * f_j0 * relu_gaussian_mean(cond_mean_i, sigma_i * cond_sd) - r_j * m_i

    return PairMoments(
        e_relu_relu=e_relu_relu,
        cov=e_relu_relu - m_i * m_j,
        K=K,
        Hmu_ij=hmu_ij,
        Hmu_ji=hmu_ji,
        Hv_ij=hv_ij,
        Hv_ji=hv_ji,
    )
