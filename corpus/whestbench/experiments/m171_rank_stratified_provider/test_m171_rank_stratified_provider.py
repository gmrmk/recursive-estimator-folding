"""Response-free tests for M171's fixed-rule certificate and refusal map."""

from __future__ import annotations

from fractions import Fraction
import unittest

from m171_rank_stratified_provider import (
    BILLED_OPS_CEILING,
    FIXED_INTERIOR_NODES,
    NORMALIZED_VALUE_TOLERANCE,
    StratumAction,
    covariance_from_factor,
    final_disposition,
    gauss_legendre_remainder_coefficient,
    minimum_pairwise_transversality,
    near_parallel_rank2_factor,
    predeclare_provider,
    predicted_cost,
    probabilists_hermite_at_one,
    rank2_positive_marginal_transverse_dispatch,
    rank_face_sqrt_model,
    regularity_obstruction,
    zero_marginal_dispatch,
)


class M171RankStratifiedProviderTests(unittest.TestCase):
    def test_predeclared_tolerances_nodes_and_cost_prediction(self) -> None:
        contract = predeclare_provider()
        cost = predicted_cost()
        self.assertEqual(contract.fixed_interior_nodes, FIXED_INTERIOR_NODES)
        self.assertEqual(contract.normalized_value_tolerance, "2e-8")
        self.assertEqual(contract.normalized_tangent_tolerance, "2e-7 (current locked M147 source certificate)")
        self.assertEqual(cost.predicted_ops, 571_904)
        self.assertLessEqual(cost.predicted_ops, BILLED_OPS_CEILING)
        self.assertFalse(cost.native_bill_proved)
        self.assertIn("no native bill", cost.credit)

    def test_rank_one_subtraction_sqrt_term_is_analytically_recovered(self) -> None:
        # epsilon=(1/10)^2: exact M165 D0+epsilon DB+A epsilon^(3/2) identity.
        value = rank_face_sqrt_model(Fraction(2, 3), Fraction(-5, 7), Fraction(11, 13), Fraction(1, 100))
        expected = Fraction(2, 3) - Fraction(5, 700) + Fraction(11, 13_000)
        self.assertEqual(value, expected)

    def test_transverse_rank_two_family_is_psd_positive_marginal_and_has_eta_angle(self) -> None:
        eta = Fraction(1, 10)
        factor = near_parallel_rank2_factor(eta)
        covariance = covariance_from_factor(factor)
        self.assertEqual(covariance[0][0], 1)
        self.assertEqual(covariance[1][1], Fraction(101, 100))
        self.assertEqual(covariance[2][2], 1)
        self.assertEqual(minimum_pairwise_transversality(factor), eta)
        self.assertEqual(
            rank2_positive_marginal_transverse_dispatch(factor).action,
            StratumAction.RANK_TWO_M168_ANCHOR,
        )

    def test_derivative_enclosure_obstruction_is_exact_and_not_a_probe(self) -> None:
        obstruction = regularity_obstruction(Fraction(1, 10))
        self.assertEqual(probabilists_hermite_at_one(19), 182_135_008)
        self.assertEqual(obstruction.derivative_order, 20)
        self.assertTrue(obstruction.all_marginals_positive)
        self.assertEqual(obstruction.minimum_pairwise_transversality, Fraction(1, 10))
        self.assertGreater(obstruction.gauss_legendre_remainder_floor, NORMALIZED_VALUE_TOLERANCE)
        self.assertFalse(obstruction.closes_derivative_envelope)
        self.assertEqual(
            gauss_legendre_remainder_coefficient(10),
            Fraction(1, 1_743_978_047_317_826_790_650_019_840_000),
        )

    def test_envelope_diverges_as_the_pair_of_kinks_becomes_nontransverse(self) -> None:
        medium = regularity_obstruction(Fraction(1, 10))
        narrow = regularity_obstruction(Fraction(1, 100))
        self.assertEqual(narrow.gauss_legendre_remainder_floor / medium.gauss_legendre_remainder_floor, 10 ** 20)
        self.assertGreater(narrow.gauss_legendre_remainder_floor, medium.gauss_legendre_remainder_floor)

    def test_nontransverse_and_zero_marginal_faces_fail_closed(self) -> None:
        nontransverse = ((Fraction(1), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
        self.assertEqual(
            rank2_positive_marginal_transverse_dispatch(nontransverse).action,
            StratumAction.NONTRANSVERSE_REFUSE,
        )
        zero_face = ((Fraction(0), Fraction(0), Fraction(0)), (Fraction(0), Fraction(1), Fraction(1, 2)), (Fraction(0), Fraction(1, 2), Fraction(1)))
        self.assertEqual(zero_marginal_dispatch(zero_face).action, StratumAction.ZERO_MARGINAL_REFUSE)

    def test_all_psd_provider_is_killed_without_a_native_bill_or_uniform_enclosure(self) -> None:
        disposition = final_disposition()
        self.assertEqual(disposition.action, StratumAction.CERTIFICATE_KILL)
        self.assertIn("uniform GL10 derivative enclosure", disposition.reason)


if __name__ == "__main__":
    unittest.main()
