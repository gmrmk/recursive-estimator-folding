"""M158 literal-domain falsifier for a generic float64 [2,1,1] provider.

This is not an approximate normal-probability implementation.  It establishes
that the requested *universal* float64 absolute-value certificate is already
inconsistent with positive ReLU gauge covariance on an admissible PSD state.

For ``X=(g Z,g Z,g Z)`` with zero means, every marginal variance is ``g**2``
and the local covariance has rank one.  The M129/M151 owned coefficient
``Delta_211 = kappa(X_0,X_0,X_1,X_2)-tree(0,0,1,2)`` is exactly

    g**4 * [ (3 pi**2 - 4 pi - 6)/(4 pi**2)
             - 12 (pi - 1)**3/pi**4 ].

At ``g=1024`` no IEEE-754 binary64 number lies within ``2e-8`` of this exact
value.  Consequently, no algorithm returning the existing float64 provider
ABI can furnish the requested absolute certificate over *all* PSD strata,
regardless of whether it uses Plackett, Genz, Owen-T, interval arithmetic, or
an exact trivariate primitive.  No ridge or clipping is involved.

No model, response, truth, scorer, leaderboard, submission, or champion is
read by this component.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
import math


_PI = Decimal(
    "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
)


class M158LiteralDomainFailure(RuntimeError):
    """The literal universal float64/error contract is mathematically impossible."""


@dataclass(frozen=True)
class Float64Counterexample:
    coefficient_kind: str
    gauge: int
    exact_value: Decimal
    nearest_float64: float
    nearest_float64_error: Decimal
    float64_ulp: Decimal
    value_tolerance: Decimal
    covariance_is_psd: bool
    positive_marginal_variances: bool


def _decimal_from_float(value: float) -> Decimal:
    numerator, denominator = value.as_integer_ratio()
    return Decimal(numerator) / Decimal(denominator)


def common_factor_defect_exact(gauge: int) -> Decimal:
    """Exact rank-one common-factor ``C_211`` defect at positive gauge ``g``."""

    if type(gauge) is not int or gauge <= 0:
        raise ValueError("gauge must be a positive built-in integer")
    with localcontext() as context:
        context.prec = 100
        pi = +_PI
        cumulant = (3 * pi * pi - 4 * pi - 6) / (4 * pi * pi)
        tree = 12 * (pi - 1) ** 3 / pi**4
        return +(Decimal(gauge) ** 4 * (cumulant - tree))


def _nearest_binary64_error(value: Decimal) -> tuple[float, Decimal, Decimal]:
    """Return a nearest binary64 candidate and the exact smallest neighbor error."""

    if not value.is_finite():
        raise ValueError("counterexample value must be finite")
    candidate = float(value)
    if not math.isfinite(candidate):
        raise ValueError("counterexample lies outside binary64 range")
    candidates = (
        candidate,
        math.nextafter(candidate, -math.inf),
        math.nextafter(candidate, math.inf),
    )
    exact_candidates = tuple(_decimal_from_float(item) for item in candidates)
    errors = tuple(abs(value - item) for item in exact_candidates)
    index = min(range(len(errors)), key=lambda slot: errors[slot])
    return candidates[index], errors[index], _decimal_from_float(math.ulp(candidates[index]))


def literal_float64_absolute_error_counterexample(
    *, gauge: int = 1024, value_tolerance: str = "2e-8"
) -> Float64Counterexample:
    """Exhibit an admissible PSD state outside the requested float64 tolerance."""

    tolerance = Decimal(value_tolerance)
    if not tolerance.is_finite() or tolerance <= 0:
        raise ValueError("value_tolerance must be positive and finite")
    exact = common_factor_defect_exact(gauge)
    nearest, error, ulp = _nearest_binary64_error(exact)
    return Float64Counterexample(
        "C_211 defect = cumulant - tree",
        gauge,
        exact,
        nearest,
        error,
        ulp,
        tolerance,
        True,
        True,
    )


def require_literal_m158_contract(*, value_tolerance: str = "2e-8") -> None:
    """Fail closed because the stated universal value certificate cannot hold."""

    counterexample = literal_float64_absolute_error_counterexample(
        value_tolerance=value_tolerance
    )
    if counterexample.nearest_float64_error > counterexample.value_tolerance:
        raise M158LiteralDomainFailure(
            "unrepresentable: no float64 C_211 defect value satisfies the literal absolute tolerance"
        )


def m158_per_coefficient_allowance() -> dict[str, int | bool]:
    """The residual allowance stated in the M158 request, without a cost credit."""

    total = 2_407_464_960
    calls = 3968
    quotient, remainder = divmod(total, calls)
    return {
        "residual_allowance_ops": total,
        "coefficient_calls": calls,
        "ops_per_coefficient": quotient,
        "integer_division_exact": remainder == 0,
    }
