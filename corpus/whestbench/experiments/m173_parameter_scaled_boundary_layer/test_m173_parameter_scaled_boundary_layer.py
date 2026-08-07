"""Response-free tests for M173's parameter-scaled boundary-layer certificate."""

from __future__ import annotations

from fractions import Fraction
import unittest

from m173_parameter_scaled_boundary_layer import (
    BILLED_OPS_CEILING,
    ETA_MAX,
    NORMALIZED_TANGENT_TOLERANCE,
    NORMALIZED_VALUE_TOLERANCE,
    StratumAction,
    canonical_near_parallel_factor,
    covariance_from_factor,
    explicit_exclusions,
    layer_enclosure,
    layer_partition,
    minimum_pairwise_transversality,
    phi_eight_upper_is_certified,
    predeclare_boundary_layer,
    predicted_cost,
    rank2_boundary_layer_dispatch,
)


class M173ParameterScaledBoundaryLayerTests(unittest.TestCase):
    def test_predeclaration_locks_eta_partition_tolerances_and_nodes(self) -> None:
        contract = predeclare_boundary_layer()
        self.assertIn("all real 0 < eta <= 1/10", contract.eta_range)
        self.assertIn("X_i=U, X_j=U+eta*V", contract.eta_range)
        self.assertEqual(contract.regular_node_allocation, 10)
        self.assertEqual(contract.layer_node_allocation, 0)
        self.assertEqual(contract.taylor_degree, 9)
        self.assertEqual(contract.normalized_value_tolerance, "2e-8")
        self.assertEqual(contract.normalized_tangent_tolerance, "2e-7 (current locked M147 source certificate)")
        self.assertIn("no adaptive retry", contract.kill_gates[-1])

    def test_exact_coordinate_partition_scales_only_with_eta(self) -> None:
        eta = Fraction(1, 100)
        self.assertEqual(layer_partition(eta), ("-infinity", Fraction(-2, 25), Fraction(0), Fraction(2, 25), "infinity"))
        self.assertEqual(layer_partition(eta, Fraction(3, 7))[1:4], (Fraction(61, 175), Fraction(3, 7), Fraction(89, 175)))

    def test_rational_gaussian_tail_certificate_uses_no_numerical_probe(self) -> None:
        self.assertTrue(phi_eight_upper_is_certified())

    def test_eta_uniform_value_and_tangent_enclosure_close_at_worst_endpoint(self) -> None:
        endpoint = layer_enclosure(ETA_MAX)
        smaller = layer_enclosure(Fraction(1, 100))
        self.assertTrue(endpoint.value_closes)
        self.assertTrue(endpoint.tangent_closes)
        self.assertLessEqual(endpoint.value_total, NORMALIZED_VALUE_TOLERANCE)
        self.assertLessEqual(endpoint.tangent_total, NORMALIZED_TANGENT_TOLERANCE)
        self.assertGreater(endpoint.value_total, smaller.value_total)
        self.assertGreater(endpoint.tangent_total, smaller.tangent_total)
        self.assertEqual(endpoint.eta, Fraction(1, 10))

    def test_hostile_rank_two_family_remains_psd_positive_and_transverse(self) -> None:
        factor = canonical_near_parallel_factor(ETA_MAX)
        covariance = covariance_from_factor(factor)
        self.assertEqual(covariance[0][0], 1)
        self.assertEqual(covariance[1][1], Fraction(101, 100))
        self.assertEqual(covariance[2][2], 1)
        self.assertEqual(minimum_pairwise_transversality(factor), ETA_MAX)
        self.assertEqual(
            rank2_boundary_layer_dispatch(factor, eta=ETA_MAX, envelopes_certified=True).action,
            StratumAction.TRANSVERSE_RANK2_LAYER_CERTIFIED,
        )

    def test_dispatch_refuses_missing_envelope_nontransverse_and_zero_faces(self) -> None:
        factor = canonical_near_parallel_factor(ETA_MAX)
        self.assertEqual(
            rank2_boundary_layer_dispatch(factor, eta=ETA_MAX, envelopes_certified=False).action,
            StratumAction.TRANSVERSE_RANK2_ENVELOPE_REFUSE,
        )
        nontransverse = ((Fraction(1), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
        self.assertEqual(
            rank2_boundary_layer_dispatch(nontransverse, eta=ETA_MAX, envelopes_certified=True).action,
            StratumAction.NONTRANSVERSE_REFUSE,
        )
        zero = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
        self.assertEqual(
            rank2_boundary_layer_dispatch(zero, eta=ETA_MAX, envelopes_certified=True).action,
            StratumAction.ZERO_MARGINAL_REFUSE,
        )
        self.assertEqual(explicit_exclusions()["spd"].action, StratumAction.SPD_REFUSE)

    def test_cost_replaces_one_m171_channel_without_exceeding_ten_nodes_or_cap(self) -> None:
        cost = predicted_cost()
        self.assertEqual(cost.legacy_m171_prediction, 571_904)
        self.assertEqual(cost.predicted_ops, 561_152)
        self.assertEqual(cost.maximum_nodes_per_channel, 10)
        self.assertLessEqual(cost.predicted_ops, BILLED_OPS_CEILING)
        self.assertTrue(cost.under_ceiling)
        self.assertFalse(cost.native_bill_proved)


if __name__ == "__main__":
    unittest.main()
