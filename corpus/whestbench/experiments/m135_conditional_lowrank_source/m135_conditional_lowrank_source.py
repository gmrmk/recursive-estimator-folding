"""Generated-only M135 conditional factor-source experiment.

This module tests a precise Rao--Blackwellization, rather than a heuristic
low-rank approximation.  When a local Gaussian covariance has the *exact*
factor-analysis form

    C = diag(d) + U U.T, d_i > 0,

we condition on h~N(0,I_r).  The remaining preactivations are independent
normals, so every coordinate's ReLU moments through order four is analytic.
The code forms the complete projected repeated k3/k4 tables and their
directional derivative.  The only Monte Carlo variables are the r common
factors.  Thus it is unbiased for every fixed sample count and integrates the
n independent residual Gaussian variables exactly.

The module deliberately keeps an unvectorized per-factor reference.  It is an
exact-small oracle and exposes the actual allocation problem: two fourth-order
diagonal contractions require dense output-pair matrices for each common
factor.  A low-rank approximation to a generic covariance is never silently
substituted for C.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for relative in ("m129_source_frechet_tangent", "m131_trivariate_boundary_stream"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m129_source_frechet import BridgeStateFrechet, Dual  # noqa: E402
from m131_trivariate_boundary_stream import relu_covariance_dual  # noqa: E402


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


@dataclass(frozen=True)
class DiagonalFactorFrechet:
    """Exact diagonal-residual Gaussian factorization and one direction.

    ``loadings`` has shape ``(width, factors)``.  A zero-column loading matrix
    is valid.  This class is exact only if its reconstructed covariance and
    tangent agree with the state passed to the source routine.
    """

    residual_variance: np.ndarray
    loadings: np.ndarray
    residual_variance_dot: np.ndarray
    loadings_dot: np.ndarray

    def covariance(self) -> np.ndarray:
        return np.diag(self.residual_variance) + self.loadings @ self.loadings.T

    def covariance_dot(self) -> np.ndarray:
        return (
            np.diag(self.residual_variance_dot)
            + self.loadings_dot @ self.loadings.T
            + self.loadings @ self.loadings_dot.T
        )

    def validate(self) -> None:
        d = np.asarray(self.residual_variance, dtype=np.float64)
        u = np.asarray(self.loadings, dtype=np.float64)
        dd = np.asarray(self.residual_variance_dot, dtype=np.float64)
        du = np.asarray(self.loadings_dot, dtype=np.float64)
        if d.ndim != 1 or dd.shape != d.shape or u.ndim != 2 or u.shape[0] != d.size or du.shape != u.shape:
            raise ValueError("diagonal-factor shape mismatch")
        if not np.all(np.isfinite(d)) or not np.all(np.isfinite(u)):
            raise ValueError("nonfinite diagonal-factor state")
        if np.any(d <= 1.0e-12):
            raise ValueError("conditional independent residual must be strictly positive")


@dataclass(frozen=True)
class ConditionalRepeatedSource:
    repeated: dict[str, Dual]
    output_covariance: Dual
    common_factor_count: int
    sample_count: int


@dataclass(frozen=True)
class IsotropicDiagonalEigenApproximation:
    """PSD low-rank-plus-isotropic approximation; never an exact replacement."""

    base: DiagonalFactorFrechet
    residual: np.ndarray
    retained_rank: int
    residual_trace_fraction: float
    residual_frobenius_fraction: float


def normal_cdf(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float64)
    return 0.5 * np.vectorize(math.erfc)(-value / math.sqrt(2.0))


def _raw_relu_moments_dot(
    mean: np.ndarray,
    variance: np.ndarray,
    mean_dot: np.ndarray,
    variance_dot: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Raw positive-part moments E[X_+^p], p=0..4, and Frechet derivative.

    Integration by parts gives d_mu M_p=p M_{p-1}; Price's identity gives
    d_v M_p=p(p-1)M_{p-2}/2 for p>=2.  The p=1 variance derivative is the
    ReLU boundary term phi(mu/sqrt(v))/(2 sqrt(v)).
    """

    mean = np.asarray(mean, dtype=np.float64)
    variance = np.asarray(variance, dtype=np.float64)
    mean_dot = np.asarray(mean_dot, dtype=np.float64)
    variance_dot = np.asarray(variance_dot, dtype=np.float64)
    if np.any(variance <= 1.0e-14):
        raise ValueError("nonpositive conditional residual variance")
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    phi = _INV_SQRT_2PI * np.exp(-0.5 * alpha * alpha)
    # I_k(a)=int_a^infty z^k phi(z) dz, a=-alpha.
    truncated = np.empty((5, mean.size), dtype=np.float64)
    truncated[0] = normal_cdf(alpha)
    truncated[1] = phi
    lower = -alpha
    for order in range(2, 5):
        truncated[order] = lower ** (order - 1) * phi + (order - 1) * truncated[order - 2]
    raw = np.empty_like(truncated)
    # ``raw[0]`` is used only as the distributional derivative of ReLU:
    # E[d/dx x_+] = P[X>0], not the ordinary convention x_+^0=1.
    raw[0] = truncated[0]
    for order in range(1, 5):
        value = np.zeros_like(mean)
        for power in range(order + 1):
            value += math.comb(order, power) * mean ** (order - power) * sigma ** power * truncated[power]
        raw[order] = value
    dot = np.zeros_like(raw)
    dot[1] = raw[0] * mean_dot + 0.5 * phi / sigma * variance_dot
    for order in range(2, 5):
        dot[order] = (
            order * raw[order - 1] * mean_dot
            + 0.5 * order * (order - 1) * raw[order - 2] * variance_dot
        )
    return raw, dot


def _conditional_cumulants(
    raw: np.ndarray, raw_dot: np.ndarray
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    """Conditional ReLU mean, variance, k3, k4 and their derivatives."""

    m1, m2, m3, m4 = raw[1], raw[2], raw[3], raw[4]
    d1, d2, d3, d4 = raw_dot[1], raw_dot[2], raw_dot[3], raw_dot[4]
    variance = m2 - m1 * m1
    variance_dot = d2 - 2.0 * m1 * d1
    k3 = m3 - 3.0 * m2 * m1 + 2.0 * m1**3
    k3_dot = d3 - 3.0 * (d2 * m1 + m2 * d1) + 6.0 * m1 * m1 * d1
    k4 = m4 - 4.0 * m3 * m1 - 3.0 * m2 * m2 + 12.0 * m2 * m1 * m1 - 6.0 * m1**4
    k4_dot = (
        d4
        - 4.0 * (d3 * m1 + m3 * d1)
        - 6.0 * m2 * d2
        + 12.0 * (d2 * m1 * m1 + 2.0 * m2 * m1 * d1)
        - 24.0 * m1**3 * d1
    )
    return (m1, variance, k3, k4), (d1, variance_dot, k3_dot, k4_dot)


def _weighted_accumulate(
    accumulator: np.ndarray, value: np.ndarray, weight: float
) -> None:
    accumulator += weight * value


def _factor_matches_state(
    tangent: BridgeStateFrechet, factor: DiagonalFactorFrechet
) -> None:
    factor.validate()
    covariance_error = np.max(np.abs(factor.covariance() - tangent.state.covariance))
    covariance_dot_error = np.max(np.abs(factor.covariance_dot() - tangent.covariance_dot))
    scale = max(1.0, float(np.max(np.abs(tangent.state.covariance))))
    dot_scale = max(1.0, float(np.max(np.abs(tangent.covariance_dot))))
    if covariance_error > 3.0e-10 * scale or covariance_dot_error > 3.0e-10 * dot_scale:
        raise ValueError("factorization is not an exact value/tangent representation of the state")


def conditional_lowrank_repeated_source(
    tangent: BridgeStateFrechet,
    downstream_weight: np.ndarray,
    common_factor_samples: np.ndarray,
    factor: DiagonalFactorFrechet,
    *,
    sample_weights: np.ndarray | None = None,
) -> ConditionalRepeatedSource:
    """Exact conditional k3/k4 repeated source for an exact D+UU.T state.

    The returned estimator is unbiased for iid common-factor rows.  Nonnegative
    deterministic weights are supported solely for generated quadrature
    references; they are not called unbiased Monte Carlo estimators.
    """

    _factor_matches_state(tangent, factor)
    weight = np.asarray(downstream_weight, dtype=np.float64)
    h = np.asarray(common_factor_samples, dtype=np.float64)
    n = tangent.state.mean.size
    if weight.shape != (n, n) or h.ndim != 2 or h.shape[1] != factor.loadings.shape[1]:
        raise ValueError("conditional source shape mismatch")
    count = h.shape[0]
    if count <= 0:
        raise ValueError("at least one common-factor sample is required")
    if sample_weights is None:
        q = np.full(count, 1.0 / count)
    else:
        q = np.asarray(sample_weights, dtype=np.float64)
        if q.shape != (count,) or np.any(q < 0.0) or not math.isclose(float(q.sum()), 1.0, abs_tol=2.0e-14):
            raise ValueError("invalid common-factor quadrature weights")

    global_mean = tangent.state.relu_mean
    global_mean_dot = tangent.relu_mean_dot
    global_covariance = relu_covariance_dual(tangent)
    output_covariance = Dual(
        weight.T @ global_covariance.value @ weight,
        weight.T @ global_covariance.tangent @ weight,
    )
    sigma = output_covariance.value
    sigma_dot = output_covariance.tangent
    diag_sigma = np.diag(sigma)
    diag_sigma_dot = np.diag(sigma_dot)
    w2, w3, w4 = weight * weight, weight**3, weight**4

    raw3 = np.zeros((n, n), dtype=np.float64)
    raw3_dot = np.zeros_like(raw3)
    raw31 = np.zeros_like(raw3)
    raw31_dot = np.zeros_like(raw3)
    raw22 = np.zeros_like(raw3)
    raw22_dot = np.zeros_like(raw3)
    d = factor.residual_variance
    ddot = factor.residual_variance_dot

    # Each iteration exactly integrates all n independent residual normals.
    # It is intentionally explicit: this is the reference against which any
    # future hidden-edge/HT fusion must be checked.
    for row, row_weight in zip(h, q):
        local_mean = tangent.state.mean + factor.loadings @ row
        local_mean_dot = tangent.mean_dot + factor.loadings_dot @ row
        moments, moments_dot = _raw_relu_moments_dot(local_mean, d, local_mean_dot, ddot)
        (m, v, c3, c4), (m_dot, v_dot, c3_dot, c4_dot) = _conditional_cumulants(moments, moments_dot)
        z = (m - global_mean) @ weight
        z_dot = (m_dot - global_mean_dot) @ weight
        qmat = weight.T @ (v[:, None] * weight)
        qmat_dot = weight.T @ (v_dot[:, None] * weight)
        qdiag = np.diag(qmat)
        qdiag_dot = np.diag(qmat_dot)
        r3aab = (w2 * c3[:, None]).T @ weight
        r3aab_dot = (w2 * c3_dot[:, None]).T @ weight
        r3aaa = np.diag(r3aab)
        r3aaa_dot = np.diag(r3aab_dot)
        r3abb = r3aab.T
        r3abb_dot = r3aab_dot.T
        k4aaab = (w3 * c4[:, None]).T @ weight
        k4aaab_dot = (w3 * c4_dot[:, None]).T @ weight
        k4aabb = (w2 * c4[:, None]).T @ w2
        k4aabb_dot = (w2 * c4_dot[:, None]).T @ w2

        local3 = z[:, None] ** 2 * z[None, :]
        local3_dot = (
            2.0 * (z * z_dot)[:, None] * z[None, :]
            + z[:, None] ** 2 * z_dot[None, :]
        )
        local3 += qdiag[:, None] * z[None, :] + 2.0 * z[:, None] * qmat + r3aab
        local3_dot += (
            qdiag_dot[:, None] * z[None, :]
            + qdiag[:, None] * z_dot[None, :]
            + 2.0 * (z_dot[:, None] * qmat + z[:, None] * qmat_dot)
            + r3aab_dot
        )

        local31 = z[:, None] ** 3 * z[None, :]
        local31_dot = 3.0 * (z * z * z_dot)[:, None] * z[None, :] + z[:, None] ** 3 * z_dot[None, :]
        local31 += (
            3.0 * z[:, None] ** 2 * qmat
            + 3.0 * (z * qdiag)[:, None] * z[None, :]
            + 3.0 * z[:, None] * r3aab
            + r3aaa[:, None] * z[None, :]
            + k4aaab
            + 3.0 * qdiag[:, None] * qmat
        )
        local31_dot += (
            6.0 * (z * z_dot)[:, None] * qmat + 3.0 * z[:, None] ** 2 * qmat_dot
            + 3.0 * ((z_dot * qdiag + z * qdiag_dot)[:, None] * z[None, :] + (z * qdiag)[:, None] * z_dot[None, :])
            + 3.0 * (z_dot[:, None] * r3aab + z[:, None] * r3aab_dot)
            + r3aaa_dot[:, None] * z[None, :] + r3aaa[:, None] * z_dot[None, :]
            + k4aaab_dot
            + 3.0 * (qdiag_dot[:, None] * qmat + qdiag[:, None] * qmat_dot)
        )

        local22 = z[:, None] ** 2 * z[None, :] ** 2
        local22_dot = (
            2.0 * (z * z_dot)[:, None] * z[None, :] ** 2
            + 2.0 * z[:, None] ** 2 * (z * z_dot)[None, :]
        )
        local22 += (
            z[:, None] ** 2 * qdiag[None, :]
            + qdiag[:, None] * z[None, :] ** 2
            + 4.0 * z[:, None] * z[None, :] * qmat
            + 2.0 * z[:, None] * r3abb
            + 2.0 * r3aab * z[None, :]
            + k4aabb
            + qdiag[:, None] * qdiag[None, :]
            + 2.0 * qmat * qmat
        )
        local22_dot += (
            2.0 * (z * z_dot)[:, None] * qdiag[None, :] + z[:, None] ** 2 * qdiag_dot[None, :]
            + qdiag_dot[:, None] * z[None, :] ** 2 + 2.0 * qdiag[:, None] * (z * z_dot)[None, :]
            + 4.0 * (z_dot[:, None] * z[None, :] * qmat + z[:, None] * z_dot[None, :] * qmat + z[:, None] * z[None, :] * qmat_dot)
            + 2.0 * (z_dot[:, None] * r3abb + z[:, None] * r3abb_dot)
            + 2.0 * (r3aab_dot * z[None, :] + r3aab * z_dot[None, :])
            + k4aabb_dot
            + qdiag_dot[:, None] * qdiag[None, :] + qdiag[:, None] * qdiag_dot[None, :]
            + 4.0 * qmat * qmat_dot
        )
        _weighted_accumulate(raw3, local3, float(row_weight))
        _weighted_accumulate(raw3_dot, local3_dot, float(row_weight))
        _weighted_accumulate(raw31, local31, float(row_weight))
        _weighted_accumulate(raw31_dot, local31_dot, float(row_weight))
        _weighted_accumulate(raw22, local22, float(row_weight))
        _weighted_accumulate(raw22_dot, local22_dot, float(row_weight))

    k4aaab = raw31 - 3.0 * diag_sigma[:, None] * sigma
    k4aaab_dot = raw31_dot - 3.0 * (diag_sigma_dot[:, None] * sigma + diag_sigma[:, None] * sigma_dot)
    k4aabb = raw22 - diag_sigma[:, None] * diag_sigma[None, :] - 2.0 * sigma * sigma
    k4aabb_dot = raw22_dot - (
        diag_sigma_dot[:, None] * diag_sigma[None, :]
        + diag_sigma[:, None] * diag_sigma_dot[None, :]
        + 4.0 * sigma * sigma_dot
    )
    repeated = {
        "k3_aaa": Dual(np.diag(raw3).copy(), np.diag(raw3_dot).copy()),
        "k3_aab": Dual(raw3, raw3_dot),
        "k4_aaaa": Dual(np.diag(k4aaab).copy(), np.diag(k4aaab_dot).copy()),
        "k4_aaab": Dual(k4aaab, k4aaab_dot),
        "k4_aabb": Dual(k4aabb, k4aabb_dot),
    }
    return ConditionalRepeatedSource(repeated, output_covariance, factor.loadings.shape[1], count)


def exact_diagonal_factor_state(
    residual_variance: np.ndarray,
    loadings: np.ndarray,
    residual_variance_dot: np.ndarray | None = None,
    loadings_dot: np.ndarray | None = None,
) -> DiagonalFactorFrechet:
    """Convenience constructor for generated exact factor states."""

    d = np.asarray(residual_variance, dtype=np.float64)
    u = np.asarray(loadings, dtype=np.float64)
    dd = np.zeros_like(d) if residual_variance_dot is None else np.asarray(residual_variance_dot, dtype=np.float64)
    du = np.zeros_like(u) if loadings_dot is None else np.asarray(loadings_dot, dtype=np.float64)
    answer = DiagonalFactorFrechet(d, u, dd, du)
    answer.validate()
    return answer


def isotropic_diagonal_eigen_approximation(
    covariance: np.ndarray, rank: int
) -> IsotropicDiagonalEigenApproximation:
    """Safe PSD approximation C0=lambda_min I+U_r U_r.T and residual C-C0.

    It is diagnostic-only.  For a generic covariance the residual is nonzero,
    so passing C0 to ``conditional_lowrank_repeated_source`` correctly raises.
    """

    covariance = np.asarray(covariance, dtype=np.float64)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1] or not np.array_equal(covariance, covariance.T):
        raise ValueError("covariance must be symmetric square")
    n = covariance.shape[0]
    if not 0 <= rank < n:
        raise ValueError("rank must be in [0,n)")
    values, vectors = np.linalg.eigh(covariance)
    if values[0] <= 1.0e-12:
        raise ValueError("covariance is not comfortably positive definite")
    order = np.argsort(values)[::-1]
    retained = order[:rank]
    lambda_floor = float(values[0])
    strengths = np.maximum(values[retained] - lambda_floor, 0.0)
    loadings = vectors[:, retained] * np.sqrt(strengths)[None, :]
    base = exact_diagonal_factor_state(np.full(n, lambda_floor), loadings)
    residual = covariance - base.covariance()
    residual = 0.5 * (residual + residual.T)
    return IsotropicDiagonalEigenApproximation(
        base,
        residual,
        rank,
        float(np.trace(residual) / np.trace(covariance)),
        float(np.linalg.norm(residual, "fro") / np.linalg.norm(covariance, "fro")),
    )


def gaussian_factor_samples(count: int, factors: int, seed: int) -> np.ndarray:
    if count <= 0 or factors < 0:
        raise ValueError("invalid Gaussian factor sample shape")
    return np.random.default_rng(seed).standard_normal((count, factors))


def generic_factor_rank_dimension_lower_bound(width: int) -> int:
    """Necessary factor rank for D+UU.T to cover a generic SPD covariance.

    After quotienting U by r-dimensional orthogonal rotations, the model has
    at most n+nr-r(r-1)/2 dimensions.  Comparing it with n(n+1)/2 gives the
    necessary condition (n-r)(n-r+1)<=2n.  This is a dimension obstruction,
    not a claim that every rank at or above the bound is feasible with d>0.
    """

    if width <= 0:
        raise ValueError("width must be positive")
    missing = 0
    while (missing + 1) * (missing + 2) <= 2 * width:
        missing += 1
    return width - missing


def conditional_reference_cost_envelope(
    common_samples_per_bank: int,
    *,
    bank_count: int = 2,
    width: int = 256,
    layers: int = 31,
    safety_factor: float = 1.25,
    include_tangent: bool = True,
    dense_dtype: str = "float64",
) -> dict[str, int | float | bool]:
    """Conservative all-in bill for the exact per-common-factor reference.

    Each factor row needs four dense pair contractions (Q, k3 aab, k4 aaab,
    k4 aabb).  A Frechet direction needs their four derivative contractions.
    This intentionally does not pretend that a batch dimension removes the
    pair-matrix work: each row has a different diagonal operator.
    """

    if common_samples_per_bank <= 0 or bank_count < 2 or width <= 0 or layers <= 0:
        raise ValueError("invalid conditional cost inputs")
    if dense_dtype not in {"float32", "float64"}:
        raise ValueError("dense dtype must be float32 or float64")
    # The executable exact-small reference is float64.  A float32 number is
    # shown only as a hypothetical port and is never treated as a validated
    # replacement until its own tangent/numerics audit exists.
    dtype_rate = 2 if dense_dtype == "float64" else 1
    square_bill = dtype_rate * (2 * width**3 - width**2)
    contractions_per_sample = 4 * (2 if include_tangent else 1)
    total_common_samples = common_samples_per_bank * bank_count
    dense_pairs = layers * total_common_samples * contractions_per_sample * square_bill
    # scalar ReLU moments, factor transforms, output products/copies, and an
    # f64 state-factor validation envelope.  It is deliberately below neither
    # the carrier nor response reserve, both added separately.
    scalar_and_factor = layers * (320 * total_common_samples * width + 24 * width**3)
    source_raw = dense_pairs + scalar_and_factor
    source_protected = int(math.ceil(safety_factor * source_raw))
    protected_carrier = 16_971_970_384
    response_reserve = 1_600_000_000
    total = source_protected + protected_carrier + response_reserve
    return {
        "common_samples_per_bank": common_samples_per_bank,
        "dense_dtype": dense_dtype,
        "bank_count": bank_count,
        "total_common_samples": total_common_samples,
        "square_bill": square_bill,
        "pair_contractions_per_common_sample": contractions_per_sample,
        "dense_pair_contractions": dense_pairs,
        "scalar_and_factor_upper": scalar_and_factor,
        "source_raw": source_raw,
        "source_protected": source_protected,
        "protected_carrier": protected_carrier,
        "response_reserve": response_reserve,
        "complete_protected_total": total,
        "strictly_below_100b": total < 100_000_000_000,
        "exact_only_if_factor_model_matches": True,
    }


def covariance_likelihood_ratio(
    x: np.ndarray, base_covariance: np.ndarray, target_covariance: np.ndarray
) -> np.ndarray:
    """Exact Gaussian bridge density ratio E_base[F L]=E_target[F].

    This is the explicit unbiased correction for an approximate D+UU.T base.
    It is provided as a diagnostic, not a promoted estimator: it requires full
    residual sampling and its log-weight variance can be catastrophic.
    """

    x = np.asarray(x, dtype=np.float64)
    base_covariance = np.asarray(base_covariance, dtype=np.float64)
    target_covariance = np.asarray(target_covariance, dtype=np.float64)
    if x.ndim != 2 or base_covariance.shape != target_covariance.shape or base_covariance.shape != (x.shape[1], x.shape[1]):
        raise ValueError("likelihood-ratio shape mismatch")
    sign0, logdet0 = np.linalg.slogdet(base_covariance)
    sign1, logdet1 = np.linalg.slogdet(target_covariance)
    if sign0 <= 0 or sign1 <= 0:
        raise ValueError("Gaussian bridge covariance must be positive definite")
    inverse_difference = np.linalg.inv(target_covariance) - np.linalg.inv(base_covariance)
    log_ratio = 0.5 * (logdet0 - logdet1) - 0.5 * np.einsum("bi,ij,bj->b", x, inverse_difference, x)
    return np.exp(log_ratio)


def gaussian_bridge_log_second_moment(
    base_covariance: np.ndarray, target_covariance: np.ndarray
) -> float:
    """log E_base[(p_target/p_base)^2], or +inf when it does not exist.

    This is the hard variance gate for the exact density-ratio correction of a
    low-rank approximation.  The moment exists iff
    ``2 target^{-1}-base^{-1}`` is positive definite.
    """

    base = np.asarray(base_covariance, dtype=np.float64)
    target = np.asarray(target_covariance, dtype=np.float64)
    if base.shape != target.shape or base.ndim != 2 or base.shape[0] != base.shape[1]:
        raise ValueError("Gaussian bridge second-moment shape mismatch")
    sign0, logdet0 = np.linalg.slogdet(base)
    sign1, logdet1 = np.linalg.slogdet(target)
    if sign0 <= 0 or sign1 <= 0:
        raise ValueError("Gaussian bridge covariance must be positive definite")
    precision = 2.0 * np.linalg.inv(target) - np.linalg.inv(base)
    sign_precision, logdet_precision = np.linalg.slogdet(precision)
    if sign_precision <= 0:
        return math.inf
    return float(-logdet1 + 0.5 * logdet0 - 0.5 * logdet_precision)
