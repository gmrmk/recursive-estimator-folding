"""Response-free M159 scale-normalized ABI falsifier for a [2,1,1] endpoint.

The component does *not* evaluate a trivariate noncentral normal primitive.
It specifies and stress-tests the numerical boundary around such a primitive.
For an ordered coefficient ``(i, i, j, k)``, positive coordinate scales give

    Delta_211(mu, Sigma) = sigma_i**2 sigma_j sigma_k * delta(alpha, R),

where ``alpha_l = mu_l / sigma_l`` and ``R`` is the correlation matrix.  A
uniform dyadic carrier ``r=2**e`` is factored as well, so the reconstructed
value is represented as ``2**(4e) * mantissa``.  This avoids prematurely
rounding a large *physical* coefficient, but cannot make that coefficient
meet a universal absolute-float64 contract once it is materialized.

Zero-variance PSD faces are deliberately dispatched rather than divided by:
they require deterministic reduction or a one-sided tangent treatment.  The
normalizer neither ridges nor clips covariance matrices.

No model, response, truth, scorer, leaderboard, submission, or champion is
read by this component.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from enum import Enum
import math
from typing import Sequence


_PI = Decimal(
    "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
)


class M159ABIError(RuntimeError):
    """Base class for a fail-closed scale-normalized endpoint ABI error."""


class M159ZeroVarianceFace(M159ABIError):
    """A marginal-zero PSD face needs its dedicated deterministic/tangent path."""


class M159DynamicRangeFailure(M159ABIError):
    """A float64 normalizer would erase a nonzero component by underflow."""


class M159PhysicalCertificateFailure(M159ABIError):
    """The requested physical float64 absolute certificate cannot be met."""


class FactorStatus(str, Enum):
    REGULAR = "regular-positive-marginals"
    ZERO_VARIANCE_FACE = "zero-variance-psd-face"


@dataclass(frozen=True)
class DyadicCarrier:
    """Uniform primal scale; its output exponent is exact integer metadata."""

    state_exponent: int

    @property
    def output_exponent(self) -> int:
        return 4 * self.state_exponent


@dataclass(frozen=True)
class ScaleNormalized211:
    """The regular dimensionless state or an explicit marginal-zero dispatch."""

    status: FactorStatus
    carrier: DyadicCarrier
    normalized_mean: tuple[float, float, float]
    normalized_covariance: tuple[tuple[float, float, float], ...]
    sigmas: tuple[float, float, float] | None
    standardized_mean: tuple[float, float, float] | None
    correlation: tuple[tuple[float, float, float], ...] | None
    coefficient_scale_mantissa: float | None
    zero_variance_indices: tuple[int, ...]


@dataclass(frozen=True)
class ScaleNormalized211Tangent:
    """JVP data with the primal dyadic carrier intentionally held constant."""

    normalized_mean_dot: tuple[float, float, float]
    normalized_covariance_dot: tuple[tuple[float, float, float], ...]
    sigma_dot: tuple[float, float, float]
    standardized_mean_dot: tuple[float, float, float]
    correlation_dot: tuple[tuple[float, float, float], ...]
    coefficient_scale_mantissa_dot: float


@dataclass(frozen=True)
class UniformScaleNormalized211Tangent:
    """Tangent for the exact dyadic-only ABI, valid on every PSD stratum."""

    normalized_mean_dot: tuple[float, float, float]
    normalized_covariance_dot: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class ScaledFloat64:
    """A value enclosure ``2**exponent * (mantissa +/- abs_radius)``.

    The carrier is not a physical float64 value.  It is exact exponent
    metadata, so it can travel through an exponent-aware source accumulator
    without triggering the M158 spacing obstruction.
    """

    mantissa: float
    exponent: int
    abs_radius: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.mantissa):
            raise ValueError("mantissa must be finite")
        if not math.isfinite(self.abs_radius) or self.abs_radius < 0.0:
            raise ValueError("abs_radius must be finite and nonnegative")


@dataclass(frozen=True)
class PhysicalMaterialization:
    """A conservative direct-float64 reconstruction certificate."""

    materialized_value: float
    scaled_evaluation_radius: Decimal
    final_rounding_radius: Decimal
    total_radius: Decimal


@dataclass(frozen=True)
class Float64ScaleCounterexample:
    """Ideal normalized evaluation followed by an unavoidable float64 round."""

    gauge: int
    carrier_exponent: int
    exact_value: Decimal
    normalized_exact_mantissa: Decimal
    physical_float64: float
    nearest_float64_error: Decimal
    float64_ulp: Decimal


def _as_vector3(name: str, values: Sequence[float]) -> tuple[float, float, float]:
    if len(values) != 3:
        raise ValueError(f"{name} must have length three")
    result = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must be finite")
    return result  # type: ignore[return-value]


def _as_matrix3(
    name: str, values: Sequence[Sequence[float]]
) -> tuple[tuple[float, float, float], ...]:
    if len(values) != 3 or any(len(row) != 3 for row in values):
        raise ValueError(f"{name} must be 3 by 3")
    result = tuple(tuple(float(value) for value in row) for row in values)
    if not all(math.isfinite(value) for row in result for value in row):
        raise ValueError(f"{name} must be finite")
    for left in range(3):
        for right in range(3):
            if result[left][right] != result[right][left]:
                raise ValueError(f"{name} must be exactly symmetric at float64 ABI")
    return result  # type: ignore[return-value]


def _ceil_half(exponent: int) -> int:
    return -((-exponent) // 2)


def _binary_exponent(value: float) -> int | None:
    """Return ``e`` in ``abs(value)=m*2**e, .5<=m<1``; None for zero."""

    if value == 0.0:
        return None
    return math.frexp(abs(value))[1]


def choose_dyadic_carrier(
    mean: Sequence[float], covariance: Sequence[Sequence[float]]
) -> DyadicCarrier:
    """Choose a uniform power-of-two carrier without changing a PSD state.

    The carrier uses all mean coordinates and covariance diagonals.  It is
    primal metadata, not a differentiable quantity: JVPs must hold it fixed.
    """

    mean3 = _as_vector3("mean", mean)
    covariance3 = _as_matrix3("covariance", covariance)
    diagonal = tuple(covariance3[index][index] for index in range(3))
    if any(value < 0.0 for value in diagonal):
        raise ValueError("covariance diagonal must be nonnegative")
    exponents: list[int] = []
    for value in mean3:
        exponent = _binary_exponent(value)
        if exponent is not None:
            exponents.append(exponent)
    for value in diagonal:
        exponent = _binary_exponent(value)
        if exponent is not None:
            exponents.append(_ceil_half(exponent))
    return DyadicCarrier(max(exponents) if exponents else 0)


def _scale_power_of_two(value: float, exponent: int) -> float:
    try:
        result = math.ldexp(value, exponent)
    except OverflowError as error:
        raise M159DynamicRangeFailure("normalization overflowed a finite ABI input") from error
    if value != 0.0 and result == 0.0:
        raise M159DynamicRangeFailure(
            "normalization would erase a nonzero ABI component by underflow; "
            "use exponent-coded state entries"
        )
    return result


def factor_scale_normalized_211(
    mean: Sequence[float], covariance: Sequence[Sequence[float]]
) -> ScaleNormalized211:
    """Factor a 3-variable [2,1,1] state without ridge, clipping, or retry.

    Labels are fixed as ``(0, 0, 1, 2)``.  A permutation wrapper may permute a
    local state before calling this ABI, but must apply the matching weight
    permutation outside it.
    """

    mean3 = _as_vector3("mean", mean)
    covariance3 = _as_matrix3("covariance", covariance)
    diagonal = tuple(covariance3[index][index] for index in range(3))
    if any(value < 0.0 for value in diagonal):
        raise ValueError("covariance diagonal must be nonnegative")

    carrier = choose_dyadic_carrier(mean3, covariance3)
    normalized_mean = tuple(
        _scale_power_of_two(value, -carrier.state_exponent) for value in mean3
    )
    normalized_covariance = tuple(
        tuple(
            _scale_power_of_two(value, -2 * carrier.state_exponent) for value in row
        )
        for row in covariance3
    )
    zero_indices = tuple(index for index, value in enumerate(diagonal) if value == 0.0)
    if zero_indices:
        return ScaleNormalized211(
            FactorStatus.ZERO_VARIANCE_FACE,
            carrier,
            normalized_mean,  # type: ignore[arg-type]
            normalized_covariance,  # type: ignore[arg-type]
            None,
            None,
            None,
            None,
            zero_indices,
        )

    sigmas = tuple(math.sqrt(normalized_covariance[index][index]) for index in range(3))
    standardized_mean = tuple(
        normalized_mean[index] / sigmas[index] for index in range(3)
    )
    correlation = tuple(
        tuple(
            normalized_covariance[left][right] / (sigmas[left] * sigmas[right])
            for right in range(3)
        )
        for left in range(3)
    )
    # The [2,1,1] label scale is sigma_0^2 sigma_1 sigma_2.
    scale_mantissa = (sigmas[0] * sigmas[0]) * sigmas[1] * sigmas[2]
    return ScaleNormalized211(
        FactorStatus.REGULAR,
        carrier,
        normalized_mean,  # type: ignore[arg-type]
        normalized_covariance,  # type: ignore[arg-type]
        sigmas,  # type: ignore[arg-type]
        standardized_mean,  # type: ignore[arg-type]
        correlation,  # type: ignore[arg-type]
        scale_mantissa,
        (),
    )


def factor_scale_normalized_211_tangent(
    factor: ScaleNormalized211,
    mean_dot: Sequence[float],
    covariance_dot: Sequence[Sequence[float]],
) -> ScaleNormalized211Tangent:
    """Prepare the tangent ABI; the carrier selected on the primal is frozen."""

    if factor.status is FactorStatus.ZERO_VARIANCE_FACE:
        raise M159ZeroVarianceFace(
            "do not differentiate sigma-normalization through a zero-variance PSD face; "
            "use deterministic reduction or an explicitly one-sided conic path"
        )
    assert factor.sigmas is not None
    assert factor.standardized_mean is not None
    assert factor.correlation is not None
    assert factor.coefficient_scale_mantissa is not None

    mean_dot3 = _as_vector3("mean_dot", mean_dot)
    covariance_dot3 = _as_matrix3("covariance_dot", covariance_dot)
    exponent = factor.carrier.state_exponent
    normalized_mean_dot = tuple(
        _scale_power_of_two(value, -exponent) for value in mean_dot3
    )
    normalized_covariance_dot = tuple(
        tuple(_scale_power_of_two(value, -2 * exponent) for value in row)
        for row in covariance_dot3
    )
    sigma_dot = tuple(
        normalized_covariance_dot[index][index] / (2.0 * factor.sigmas[index])
        for index in range(3)
    )
    standardized_mean_dot = tuple(
        normalized_mean_dot[index] / factor.sigmas[index]
        - factor.standardized_mean[index]
        * sigma_dot[index]
        / factor.sigmas[index]
        for index in range(3)
    )
    correlation_dot = tuple(
        tuple(
            normalized_covariance_dot[left][right]
            / (factor.sigmas[left] * factor.sigmas[right])
            - factor.correlation[left][right]
            * (
                sigma_dot[left] / factor.sigmas[left]
                + sigma_dot[right] / factor.sigmas[right]
            )
            for right in range(3)
        )
        for left in range(3)
    )
    log_scale_dot = (
        2.0 * sigma_dot[0] / factor.sigmas[0]
        + sigma_dot[1] / factor.sigmas[1]
        + sigma_dot[2] / factor.sigmas[2]
    )
    return ScaleNormalized211Tangent(
        normalized_mean_dot,  # type: ignore[arg-type]
        normalized_covariance_dot,  # type: ignore[arg-type]
        sigma_dot,  # type: ignore[arg-type]
        standardized_mean_dot,  # type: ignore[arg-type]
        correlation_dot,  # type: ignore[arg-type]
        factor.coefficient_scale_mantissa * log_scale_dot,
    )


def factor_uniform_scale_normalized_211_tangent(
    factor: ScaleNormalized211,
    mean_dot: Sequence[float],
    covariance_dot: Sequence[Sequence[float]],
) -> UniformScaleNormalized211Tangent:
    """Prepare a JVP for the primary, dyadic-only endpoint ABI.

    Unlike the optional correlation chart, this operation never divides by a
    marginal standard deviation.  Hence a rank-deficient or zero-variance PSD
    state remains in its native stratum.  The dyadic carrier chosen on the
    primal is frozen, as required for a reparameterization carrier.
    """

    mean_dot3 = _as_vector3("mean_dot", mean_dot)
    covariance_dot3 = _as_matrix3("covariance_dot", covariance_dot)
    exponent = factor.carrier.state_exponent
    return UniformScaleNormalized211Tangent(
        tuple(_scale_power_of_two(value, -exponent) for value in mean_dot3),
        tuple(
            tuple(_scale_power_of_two(value, -2 * exponent) for value in row)
            for row in covariance_dot3
        ),
    )


def reconstruct_uniform_dyadic_211(
    factor: ScaleNormalized211,
    dimensionless_value: float,
    dimensionless_abs_radius: float,
    *,
    dimensionless_value_dot: float | None = None,
    dimensionless_value_dot_abs_radius: float | None = None,
) -> tuple[ScaledFloat64, ScaledFloat64 | None]:
    """Primary reconstruction using only the exact ``2**(4e)`` carrier.

    This is the recommended generic ABI.  Its dimensionless primitive sees
    ``(mu / 2**e, Sigma / 2**(2e))`` directly, so no marginal division is
    needed and all PSD ranks remain admissible.  A kernel-supplied radius must
    include its own normalized-state and evaluation error.
    """

    if not math.isfinite(dimensionless_value) or dimensionless_abs_radius < 0.0:
        raise ValueError("dimensionless value/radius is invalid")
    value = ScaledFloat64(
        dimensionless_value,
        factor.carrier.output_exponent,
        dimensionless_abs_radius + 0.5 * math.ulp(dimensionless_value),
    )
    if dimensionless_value_dot is None:
        if dimensionless_value_dot_abs_radius is not None:
            raise ValueError("dimensionless tangent radius requires its value")
        return value, None
    if (
        not math.isfinite(dimensionless_value_dot)
        or dimensionless_value_dot_abs_radius is None
        or dimensionless_value_dot_abs_radius < 0.0
    ):
        raise ValueError("dimensionless tangent value/radius is invalid")
    return value, ScaledFloat64(
        dimensionless_value_dot,
        factor.carrier.output_exponent,
        dimensionless_value_dot_abs_radius + 0.5 * math.ulp(dimensionless_value_dot),
    )


def reconstruct_scaled_211(
    factor: ScaleNormalized211,
    dimensionless_value: float,
    dimensionless_abs_radius: float,
    *,
    dimensionless_value_dot: float | None = None,
    dimensionless_value_dot_abs_radius: float | None = None,
    tangent: ScaleNormalized211Tangent | None = None,
) -> tuple[ScaledFloat64, ScaledFloat64 | None]:
    """Reconstruct scale-carried value and optional tangent with product bounds.

    This optional *correlation-chart* reconstruction is useful only when the
    caller has included all chart-conversion error in its input radii.  The
    primary generic ABI is :func:`reconstruct_uniform_dyadic_211`, whose
    carrier is an exact power of two.  Product-rounding half-ulp is added here.
    The returned values are not direct physical float64 outputs.
    """

    if factor.status is FactorStatus.ZERO_VARIANCE_FACE:
        raise M159ZeroVarianceFace("zero-variance faces must use their explicit reduction")
    if not math.isfinite(dimensionless_value) or dimensionless_abs_radius < 0.0:
        raise ValueError("dimensionless value/radius is invalid")
    assert factor.coefficient_scale_mantissa is not None
    scale = factor.coefficient_scale_mantissa
    mantissa = scale * dimensionless_value
    radius = (
        abs(scale) * dimensionless_abs_radius
        + 0.5 * math.ulp(mantissa)
    )
    value = ScaledFloat64(mantissa, factor.carrier.output_exponent, radius)

    if dimensionless_value_dot is None:
        if dimensionless_value_dot_abs_radius is not None or tangent is not None:
            raise ValueError("tangent arguments require dimensionless_value_dot")
        return value, None
    if tangent is None or dimensionless_value_dot_abs_radius is None:
        raise ValueError("tangent reconstruction needs tangent and its radius")
    if not math.isfinite(dimensionless_value_dot) or dimensionless_value_dot_abs_radius < 0.0:
        raise ValueError("dimensionless tangent value/radius is invalid")
    tangent_mantissa = (
        scale * dimensionless_value_dot
        + tangent.coefficient_scale_mantissa_dot * dimensionless_value
    )
    # Interval product propagation.  This is conservative and intentionally
    # leaves an endpoint primitive responsible for its own delta/delta-dot
    # relation and radius.
    tangent_radius = (
        abs(scale) * dimensionless_value_dot_abs_radius
        + abs(tangent.coefficient_scale_mantissa_dot) * dimensionless_abs_radius
        + 0.5 * math.ulp(tangent_mantissa)
    )
    return value, ScaledFloat64(
        tangent_mantissa, factor.carrier.output_exponent, tangent_radius
    )


def _decimal_from_float(value: float) -> Decimal:
    numerator, denominator = value.as_integer_ratio()
    return Decimal(numerator) / Decimal(denominator)


def _decimal_power_of_two(exponent: int) -> Decimal:
    with localcontext() as context:
        context.prec = 120
        return +(Decimal(2) ** exponent)


def materialize_physical_float64(value: ScaledFloat64) -> PhysicalMaterialization:
    """Materialize a carrier and add the irreducible final-rounding bound."""

    try:
        materialized = math.ldexp(value.mantissa, value.exponent)
    except OverflowError as error:
        raise M159PhysicalCertificateFailure("physical value overflows float64") from error
    if not math.isfinite(materialized):
        raise M159PhysicalCertificateFailure("physical value is not finite float64")
    with localcontext() as context:
        context.prec = 120
        scale = _decimal_power_of_two(value.exponent)
        scaled_radius = Decimal.from_float(value.abs_radius) * scale
        rounding_radius = _decimal_from_float(math.ulp(materialized)) / Decimal(2)
        return PhysicalMaterialization(
            materialized,
            +scaled_radius,
            +rounding_radius,
            +(scaled_radius + rounding_radius),
        )


def require_physical_absolute_certificate(
    value: ScaledFloat64, *, tolerance: str = "2e-8"
) -> PhysicalMaterialization:
    """Fail closed unless direct materialization has the requested bound."""

    limit = Decimal(tolerance)
    if not limit.is_finite() or limit <= 0:
        raise ValueError("tolerance must be finite and positive")
    certificate = materialize_physical_float64(value)
    if certificate.total_radius > limit:
        raise M159PhysicalCertificateFailure(
            "physical float64 materialization cannot meet the requested absolute certificate"
        )
    return certificate


def robust_variance_ratio_upper(
    observed_residual_variance: float,
    residual_centered_l2_error: float,
    observed_raw_variance: float,
    raw_centered_l2_error: float,
) -> float:
    """Certified upper bound for a source-level residual/raw variance ratio.

    The errors are RMS envelopes over the same source draw or bootstrap
    replicate.  This is the triangle inequality in centered L2; it is valid
    after multiplying every path in that replicate by one common nonzero
    normalization factor.
    """

    values = (
        observed_residual_variance,
        residual_centered_l2_error,
        observed_raw_variance,
        raw_centered_l2_error,
    )
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("variances and L2 envelopes must be finite nonnegative")
    denominator = math.sqrt(observed_raw_variance) - raw_centered_l2_error
    if denominator <= 0.0:
        return math.inf
    numerator = math.sqrt(observed_residual_variance) + residual_centered_l2_error
    return (numerator / denominator) ** 2


def robust_p99_ratio_upper(
    observed_residual_p99: float,
    residual_linf_error: float,
    observed_raw_p99: float,
    raw_linf_error: float,
) -> float:
    """Certified p99 residual/raw ratio upper bound from pointwise envelopes."""

    values = (
        observed_residual_p99,
        residual_linf_error,
        observed_raw_p99,
        raw_linf_error,
    )
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("p99 values and Linf envelopes must be finite nonnegative")
    denominator = observed_raw_p99 - raw_linf_error
    if denominator <= 0.0:
        return math.inf
    return (observed_residual_p99 + residual_linf_error) / denominator


def common_factor_defect_exact(gauge: int) -> Decimal:
    """Exact M158 rank-one [2,1,1] defect retained as a response-free probe."""

    if type(gauge) is not int or gauge <= 0:
        raise ValueError("gauge must be a positive built-in integer")
    with localcontext() as context:
        context.prec = 110
        pi = +_PI
        cumulant = (3 * pi * pi - 4 * pi - 6) / (4 * pi * pi)
        tree = 12 * (pi - 1) ** 3 / pi**4
        return +(Decimal(gauge) ** 4 * (cumulant - tree))


def scale_normalized_float64_counterexample(gauge: int = 1024) -> Float64ScaleCounterexample:
    """Show that even ideal normalization cannot repair direct output spacing."""

    if type(gauge) is not int or gauge <= 0 or gauge & (gauge - 1):
        raise ValueError("gauge must be a positive power of two")
    covariance = tuple(tuple(float(gauge * gauge) for _ in range(3)) for _ in range(3))
    factor = factor_scale_normalized_211((0.0, 0.0, 0.0), covariance)
    exact = common_factor_defect_exact(gauge)
    carrier_exponent = factor.carrier.output_exponent
    normalized_exact_mantissa = exact / _decimal_power_of_two(carrier_exponent)
    # This grants the endpoint an ideal exact dimensionless calculation before
    # the first binary64 conversion; any real float64 kernel can only add error.
    physical = math.ldexp(float(normalized_exact_mantissa), carrier_exponent)
    with localcontext() as context:
        context.prec = 120
        nearest_error = abs(exact - _decimal_from_float(physical))
        ulp = _decimal_from_float(math.ulp(physical))
    return Float64ScaleCounterexample(
        gauge,
        carrier_exponent,
        exact,
        normalized_exact_mantissa,
        physical,
        +nearest_error,
        +ulp,
    )
