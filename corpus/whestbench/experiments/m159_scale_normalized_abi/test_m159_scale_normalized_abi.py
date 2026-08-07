"""Response-free falsification tests for the M159 scale-normalized ABI."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import math
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m159_scale_normalized_abi import (  # noqa: E402
    FactorStatus,
    M159PhysicalCertificateFailure,
    M159ZeroVarianceFace,
    ScaledFloat64,
    common_factor_defect_exact,
    factor_scale_normalized_211,
    factor_scale_normalized_211_tangent,
    factor_uniform_scale_normalized_211_tangent,
    materialize_physical_float64,
    reconstruct_scaled_211,
    reconstruct_uniform_dyadic_211,
    require_physical_absolute_certificate,
    robust_p99_ratio_upper,
    robust_variance_ratio_upper,
    scale_normalized_float64_counterexample,
)


class ScaleNormalizedABI211Tests(unittest.TestCase):
    def test_coordinate_gauge_is_factored_and_rank_one_positive_marginal_stratum_survives(self) -> None:
        mean = (0.25, -0.5, 1.25)
        covariance = ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0), (1.0, 1.0, 1.0))
        baseline = factor_scale_normalized_211(mean, covariance)
        self.assertEqual(baseline.status, FactorStatus.REGULAR)
        self.assertTrue(
            all(value == 1.0 for row in baseline.correlation for value in row)
        )

        diagonal_gauge = (2.0, 4.0, 0.5)
        gauged = factor_scale_normalized_211(
            tuple(diagonal_gauge[index] * mean[index] for index in range(3)),
            tuple(
                tuple(
                    diagonal_gauge[left] * covariance[left][right] * diagonal_gauge[right]
                    for right in range(3)
                )
                for left in range(3)
            ),
        )
        self.assertEqual(gauged.status, FactorStatus.REGULAR)
        self.assertEqual(gauged.standardized_mean, baseline.standardized_mean)
        self.assertEqual(gauged.correlation, baseline.correlation)

        baseline_scale = math.ldexp(
            baseline.coefficient_scale_mantissa, baseline.carrier.output_exponent
        )
        gauged_scale = math.ldexp(
            gauged.coefficient_scale_mantissa, gauged.carrier.output_exponent
        )
        # Labels are (0,0,1,2): D_0^2 D_1 D_2 = 2^2 * 4 * .5 = 8.
        self.assertEqual(gauged_scale / baseline_scale, 8.0)

    def test_tangent_freezes_primal_dyadic_carrier_and_reconstructs_homogeneous_derivative(self) -> None:
        mean = (0.25, -0.5, 1.25)
        covariance = (
            (1.0, 0.2, 0.1),
            (0.2, 4.0, 0.3),
            (0.1, 0.3, 9.0),
        )
        factor = factor_scale_normalized_211(mean, covariance)
        tangent = factor_scale_normalized_211_tangent(
            factor,
            mean,  # derivative of lambda * mean at lambda=1
            tuple(tuple(2.0 * value for value in row) for row in covariance),
            # derivative of lambda^2 * covariance
        )
        self.assertLess(max(abs(value) for value in tangent.standardized_mean_dot), 2e-16)
        self.assertLess(
            max(abs(value) for row in tangent.correlation_dot for value in row),
            2e-16,
        )

        value, value_dot = reconstruct_scaled_211(
            factor,
            dimensionless_value=0.375,
            dimensionless_abs_radius=0.0,
            dimensionless_value_dot=0.0,
            dimensionless_value_dot_abs_radius=0.0,
            tangent=tangent,
        )
        assert value_dot is not None
        self.assertAlmostEqual(value_dot.mantissa, 4.0 * value.mantissa, places=14)
        self.assertEqual(value_dot.exponent, value.exponent)

        uniform_tangent = factor_uniform_scale_normalized_211_tangent(
            factor,
            mean,
            tuple(tuple(2.0 * value for value in row) for row in covariance),
        )
        self.assertEqual(uniform_tangent.normalized_mean_dot, factor.normalized_mean)
        self.assertEqual(
            uniform_tangent.normalized_covariance_dot,
            tuple(
                tuple(2.0 * value for value in row)
                for row in factor.normalized_covariance
            ),
        )
        uniform_value, uniform_value_dot = reconstruct_uniform_dyadic_211(
            factor,
            dimensionless_value=0.375,
            dimensionless_abs_radius=0.0,
            dimensionless_value_dot=4.0 * 0.375,
            dimensionless_value_dot_abs_radius=0.0,
        )
        assert uniform_value_dot is not None
        self.assertEqual(uniform_value_dot.mantissa, 4.0 * uniform_value.mantissa)

    def test_zero_variance_psd_face_is_not_silently_normalized_or_given_a_two_sided_tangent(self) -> None:
        factor = factor_scale_normalized_211(
            (1.0, -2.0, 3.0),
            ((0.0, 0.0, 0.0), (0.0, 4.0, 1.0), (0.0, 1.0, 9.0)),
        )
        self.assertEqual(factor.status, FactorStatus.ZERO_VARIANCE_FACE)
        self.assertEqual(factor.zero_variance_indices, (0,))
        # The primary dyadic ABI itself still preserves this exact face.
        uniform_value, _ = reconstruct_uniform_dyadic_211(factor, 0.125, 0.0)
        self.assertEqual(uniform_value.exponent, factor.carrier.output_exponent)
        with self.assertRaisesRegex(M159ZeroVarianceFace, "zero-variance PSD face"):
            factor_scale_normalized_211_tangent(
                factor,
                (0.0, 0.0, 0.0),
                ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
            )

    def test_ideal_scale_normalization_still_cannot_restore_the_literal_physical_float64_contract(self) -> None:
        counterexample = scale_normalized_float64_counterexample(1024)
        self.assertEqual(counterexample.carrier_exponent, 44)
        self.assertEqual(counterexample.exact_value, common_factor_defect_exact(1024))
        self.assertGreater(counterexample.nearest_float64_error, Decimal("2e-8"))
        self.assertGreater(counterexample.float64_ulp / 2, Decimal("2e-8"))

        # Even an unrealistically perfect dimensionless kernel has a final
        # physical-rounding radius above the literal tolerance after export.
        ideal_carrier = ScaledFloat64(
            float(counterexample.normalized_exact_mantissa),
            counterexample.carrier_exponent,
            0.0,
        )
        certificate = materialize_physical_float64(ideal_carrier)
        self.assertGreater(certificate.final_rounding_radius, Decimal("2e-8"))
        with self.assertRaises(M159PhysicalCertificateFailure):
            require_physical_absolute_certificate(ideal_carrier, tolerance="2e-8")

    def test_robust_source_gate_is_invariant_to_a_common_power_of_two_normalization(self) -> None:
        raw_variance = 16.0
        residual_variance = 16.0 * 0.45**2
        raw_l2_error = 0.08
        residual_l2_error = 0.04
        base_variance_ratio = robust_variance_ratio_upper(
            residual_variance,
            residual_l2_error,
            raw_variance,
            raw_l2_error,
        )
        self.assertLess(base_variance_ratio, 0.25)

        # Common source scaling L=2^10 leaves both the actual ratio and the
        # certified perturbation ratio unchanged.  Per-event scaling would not.
        normalizer = 2.0**10
        scaled_variance_ratio = robust_variance_ratio_upper(
            residual_variance * normalizer**2,
            residual_l2_error * normalizer,
            raw_variance * normalizer**2,
            raw_l2_error * normalizer,
        )
        self.assertEqual(scaled_variance_ratio, base_variance_ratio)

        base_p99_ratio = robust_p99_ratio_upper(0.45, 0.002, 1.0, 0.004)
        scaled_p99_ratio = robust_p99_ratio_upper(
            0.45 * normalizer,
            0.002 * normalizer,
            normalizer,
            0.004 * normalizer,
        )
        self.assertLess(base_p99_ratio, 1.25)
        self.assertEqual(scaled_p99_ratio, base_p99_ratio)


if __name__ == "__main__":
    unittest.main(verbosity=2)
