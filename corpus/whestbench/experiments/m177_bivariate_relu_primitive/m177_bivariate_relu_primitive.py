"""M177 contract probe: endpoint-complete bivariate Gaussian ReLU primitive.

This is deliberately a *fail-closed contract classifier*, not an estimator.
It establishes which Gaussian strata have elementary value formulas and where
the frozen BackgroundArchive recurrence needs a certified Phi / Phi2 service.
No response, source carrier, model loop, or score is touched.

The important distinction is between an exact symbolic identity and an
installed, metered evaluator carrying a numerical remainder.  FlopScope 0.8
exports a charged scalar normal CDF but no public interval/error API, no Owen
T/S, and no bivariate normal CDF.  Consequently this module returns formulas
or a deterministic refusal; it never treats an unverified library CDF as an
exact primitive.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Optional

import numpy as np


class PrimitiveRefusal(RuntimeError):
    """A value or JVP cannot be certified under the frozen M177 contract."""


class Stratum(str, Enum):
    NON_PSD = "non_psd"
    DETERMINISTIC = "deterministic"
    ZERO_VARIANCE_FACE = "zero_variance_face"
    RANK_ONE_PLUS = "rank_one_plus"
    RANK_ONE_MINUS = "rank_one_minus"
    SPD = "spd"


@dataclass(frozen=True)
class PairClassification:
    stratum: Stratum
    sigma0: float
    sigma1: float
    rho: Optional[float]
    determinant: float
    value_identity: str
    tangent_policy: str


@dataclass(frozen=True)
class RuntimeCapability:
    normal_cdf: bool
    normal_cdf_cost_per_element: int
    normal_cdf_certified_error: bool
    owen_t: bool
    bivariate_normal_cdf: bool
    exact_elementary_evaluator: bool


def _finite_symmetric(mean: np.ndarray, covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if (
        mean.shape != (2,)
        or covariance.shape != (2, 2)
        or not np.array_equal(covariance, covariance.T)
        or not np.all(np.isfinite(mean))
        or not np.all(np.isfinite(covariance))
    ):
        raise PrimitiveRefusal("M177_INVALID_FINITE_SYMMETRIC_PAIR")
    return mean, covariance


def classify_pair(mean: np.ndarray, covariance: np.ndarray) -> PairClassification:
    """Classify every finite symmetric bivariate input without clipping/ridges.

    PSD is tested in its exact 2x2 conditions, so an invalid covariance is not
    made valid by a numerical eigensolver, covariance floor, or correlation
    clamp.  At a zero-variance face a correlation coordinate is intentionally
    absent rather than fabricated by division.
    """

    _mean, covariance = _finite_symmetric(mean, covariance)
    v0, v1 = float(covariance[0, 0]), float(covariance[1, 1])
    c01 = float(covariance[0, 1])
    determinant = v0 * v1 - c01 * c01
    if v0 < 0.0 or v1 < 0.0 or determinant < 0.0:
        return PairClassification(Stratum.NON_PSD, math.nan, math.nan, None, determinant,
                                  "REFUSE", "REFUSE")
    if v0 == 0.0 and v1 == 0.0:
        if c01 != 0.0:
            return PairClassification(Stratum.NON_PSD, 0.0, 0.0, None, determinant,
                                      "REFUSE", "REFUSE")
        return PairClassification(Stratum.DETERMINISTIC, 0.0, 0.0, None, determinant,
                                  "ReLU(mu0)*ReLU(mu1)", "one-sided kink policy required at mu=0")
    if v0 == 0.0 or v1 == 0.0:
        # For a PSD 2x2 matrix a zero diagonal forces the whole row/column to
        # zero.  This explicit condition catches arithmetic that would try to
        # pass a nonzero covariance through a zero standard deviation.
        if c01 != 0.0:
            return PairClassification(Stratum.NON_PSD, math.sqrt(max(v0, 0.0)), math.sqrt(max(v1, 0.0)), None, determinant,
                                      "REFUSE", "REFUSE")
        return PairClassification(Stratum.ZERO_VARIANCE_FACE, math.sqrt(v0), math.sqrt(v1), None, determinant,
                                  "ReLU(deterministic coordinate) times univariate ReLU mean",
                                  "only declared one-sided conic paths; generic covariance JVP is underdetermined")
    sigma0, sigma1 = math.sqrt(v0), math.sqrt(v1)
    rho = c01 / (sigma0 * sigma1)
    # The determinant was tested before division.  Exact endpoint tests are
    # semantic: no near-endpoint replacement is allowed.
    if determinant == 0.0:
        if rho == 1.0:
            return PairClassification(Stratum.RANK_ONE_PLUS, sigma0, sigma1, rho, determinant,
                                      "E[(alpha0+Z)_+(alpha1+Z)_+]", "feasible one-sided PSD JVP only")
        if rho == -1.0:
            return PairClassification(Stratum.RANK_ONE_MINUS, sigma0, sigma1, rho, determinant,
                                      "E[(alpha0+Z)_+(alpha1-Z)_+]", "feasible one-sided PSD JVP only")
        # This is not repaired by clipping.  It means binary64 multiplication
        # has produced an inconsistent claimed exact rank face.
        return PairClassification(Stratum.NON_PSD, sigma0, sigma1, rho, determinant,
                                  "REFUSE_INCONSISTENT_RANK_FACE", "REFUSE")
    if not (-1.0 < rho < 1.0):
        return PairClassification(Stratum.NON_PSD, sigma0, sigma1, rho, determinant,
                                  "REFUSE", "REFUSE")
    return PairClassification(Stratum.SPD, sigma0, sigma1, rho, determinant,
                              "Rosenbaum value using Phi, phi, Phi2(alpha0,alpha1;rho)",
                              "ordinary Frechet JVP if Phi/Phi2 have certified values")


def exact_univariate_relu_mean(mu: float, sigma: float) -> str:
    """Return the exact symbolic branch, including the zero-sigma face."""
    if not math.isfinite(mu) or not math.isfinite(sigma) or sigma < 0.0:
        raise PrimitiveRefusal("M177_INVALID_UNIVARIATE")
    if sigma == 0.0:
        return "max(mu,0)"
    return "sigma*phi(mu/sigma)+mu*Phi(mu/sigma)"


def endpoint_reduction_identity(classification: PairClassification) -> str:
    """Expose the required special-function reduction without evaluating it."""
    if classification.stratum is Stratum.DETERMINISTIC:
        return "elementary deterministic product"
    if classification.stratum is Stratum.ZERO_VARIANCE_FACE:
        return "elementary factor times " + exact_univariate_relu_mean(0.0, 1.0)
    if classification.stratum in (Stratum.RANK_ONE_PLUS, Stratum.RANK_ONE_MINUS):
        return "finite polynomial of truncated N(0,1) moments; requires Phi and phi at moving endpoints"
    if classification.stratum is Stratum.SPD:
        return "Rosenbaum: algebra + Phi + phi + Phi2 (equivalently Owen-T representation)"
    raise PrimitiveRefusal("M177_NON_PSD_PAIR")


def probe_flopscope_capability() -> RuntimeCapability:
    """Inspect the pinned runtime surface only; no claim about hidden accuracy."""
    try:
        import flopscope as flops  # type: ignore
        import flopscope.numpy as fnp  # type: ignore
    except Exception:
        return RuntimeCapability(False, 0, False, False, False, False)
    norm = getattr(getattr(flops, "stats", None), "norm", None)
    cdf = getattr(norm, "cdf", None)
    # The pinned public contract documents a fixed 48-FLOP CDF charge but does
    # not expose a remainder/correct-rounding certificate.  Feature absence is
    # checked on public namespaces, not inferred from private implementation.
    return RuntimeCapability(
        normal_cdf=callable(cdf),
        normal_cdf_cost_per_element=48 if callable(cdf) else 0,
        normal_cdf_certified_error=False,
        owen_t=hasattr(fnp, "owens_t") or hasattr(getattr(flops, "stats", None), "owens_t"),
        bivariate_normal_cdf=hasattr(getattr(flops, "stats", None), "multivariate_normal_cdf"),
        exact_elementary_evaluator=False,
    )


def required_pair_cost_lower_bound() -> dict[str, int]:
    """Inclusive *known* scalar-operation floor before an unknown Phi2 service.

    Per unordered positive-variance pair the M176 kernel needs two marginal
    Phi calls, two boundary Phi calls, two conditional-mean Phi calls, two
    marginal phi calls, two conditional phi calls, and ordinary algebra.
    The 48/27 charges are the pinned FlopScope public costs.  The Phi2/Owen-T
    service and its certificate are intentionally left as ``UNAVAILABLE``:
    assigning it zero FLOPs would be an accounting bypass.
    """
    cdf_calls, pdf_calls = 6, 4
    return {
        "cdf_calls": cdf_calls,
        "pdf_calls": pdf_calls,
        "charged_cdf_flops": 48 * cdf_calls,
        "charged_pdf_flops": 27 * pdf_calls,
        "pointwise_algebra_conservative": 160,
        "known_pre_phi2_total": 48 * cdf_calls + 27 * pdf_calls + 160,
        "phi2_or_owen_t_certificate": -1,
    }


def fail_closed_runtime_reason(mean: np.ndarray, covariance: np.ndarray) -> str:
    """The only lawful M177 runtime result under the installed contract."""
    classification = classify_pair(mean, covariance)
    if classification.stratum is Stratum.NON_PSD:
        return "M177_REFUSE_NON_PSD"
    if classification.stratum in (Stratum.DETERMINISTIC, Stratum.ZERO_VARIANCE_FACE):
        return "M177_REFUSE_TANGENT_PATH_NOT_FULLY_DECLARED"
    return "M177_REFUSE_NO_CERTIFIED_PHI_PHI2_OWEN_T_PROVIDER"
