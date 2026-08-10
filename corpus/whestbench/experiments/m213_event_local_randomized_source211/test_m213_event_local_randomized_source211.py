"""TDD contract for M213's generated-only event-local Source211 falsifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for sibling in (
    "m131_trivariate_boundary_stream",
    "m167_collision_owner_unification",
):
    path = str(EXPERIMENTS / sibling)
    if path not in sys.path:
        sys.path.insert(0, path)

from m131_trivariate_boundary_stream import bivariate_relu_raw_dot  # noqa: E402
from m167_collision_owner_unification import (  # noqa: E402
    PhysicalFourthOwners,
    complete_owner_table,
)


def _load():
    spec = importlib.util.spec_from_file_location("m213_provider", HERE / "m213_event_local_randomized_source211.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M213 provider")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M213EventLocalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m213 = _load()

    def test_predeclaration_precedes_provider_and_bans_variance_efficacy(self):
        self.assertTrue((HERE / "M213_PREDECLARATION_20260809.md").exists())
        manifest = self.m213.frozen_manifest()
        self.assertEqual(manifest["widths"], (2, 3, 4, 5, 6, 7))
        self.assertFalse(manifest["variance_efficacy_authorized"])
        self.assertFalse(manifest["four_distinct_wedge"])
        self.assertFalse((HERE / "run_m213_source_variance.py").exists())

    def test_one_outer_draw_uses_one_m178_pair_and_m131_pair_crosscheck(self):
        mean, covariance = self.m213.generated_spd_cell(3, 213700003)
        local = self.m213.build_local_state(mean, covariance)
        sample = self.m213.distinct_event_from_outer_g(local, 0, 1, 2, 0.37)
        self.assertEqual(sample.conditional_m178_calls, 1)
        self.assertTrue(sample.m178_contained)
        raw_m131, _ = bivariate_relu_raw_dot(
            sample.conditional_mean,
            sample.conditional_covariance,
            np.zeros(2),
            np.zeros((2, 2)),
        )
        self.assertLess(abs(sample.conditional_pair_raw - raw_m131), 2.0e-8)
        self.assertAlmostEqual(
            sample.value,
            sample.central_fourth_sample - local.activation_covariance[0, 0] * local.activation_covariance[1, 2]
            - 2.0 * local.activation_covariance[0, 1] * local.activation_covariance[0, 2]
            - local.tree_211(0, 1, 2),
            places=12,
        )

    def test_collision_owner_gate_refuses_unsupported_high_moment_boundary(self):
        for width, seed in zip((2, 3, 4, 5, 6, 7), (213700002, 213700003, 213700004, 213700005, 213700006, 213700007), strict=True):
            mean, covariance = self.m213.generated_spd_cell(width, seed)
            local = self.m213.build_local_state(mean, covariance)
            with self.assertRaisesRegex(self.m213.M213Refusal, "boundary-indicator"):
                self.m213.audit_collision_owners(local)
            for i in range(width):
                k4 = self.m213.event_local_coefficient(local, (i, i, i, i))
                self.assertFalse(k4.refused)
                self.assertEqual(k4.source211_denominator, 6)
                for j in range(width):
                    if i != j:
                        self.assertTrue(self.m213.event_local_coefficient(local, (i, i, i, j)).refused)
                        self.assertTrue(self.m213.event_local_coefficient(local, (i, i, j, j)).refused)

    def test_generated_gauge_and_permutation_actions_hold_for_k4_without_masking_collision_refusal(self):
        mean, covariance = self.m213.generated_spd_cell(5, 213700005)
        local = self.m213.build_local_state(mean, covariance)
        gauge = np.exp(np.array((-0.4, -0.1, 0.0, 0.2, 0.5)))
        permutation = np.array((3, 0, 4, 1, 2))
        gauged = self.m213.build_local_state(mean * gauge, covariance * gauge[:, None] * gauge[None, :])
        permuted = self.m213.build_local_state(mean[permutation], covariance[np.ix_(permutation, permutation)])
        baseline_k4 = np.asarray([self.m213.event_local_coefficient(local, (i, i, i, i)).value for i in range(5)])
        gauged_k4 = np.asarray([self.m213.event_local_coefficient(gauged, (i, i, i, i)).value for i in range(5)])
        permuted_k4 = np.asarray([self.m213.event_local_coefficient(permuted, (i, i, i, i)).value for i in range(5)])
        np.testing.assert_allclose(gauged_k4, baseline_k4 * gauge**4, rtol=0.0, atol=1.5e-8)
        np.testing.assert_allclose(permuted_k4, baseline_k4[permutation], rtol=0.0, atol=2.0e-9)
        self.assertTrue(self.m213.event_local_coefficient(local, (0, 0, 0, 1)).refused)
        self.assertTrue(self.m213.event_local_coefficient(local, (0, 0, 1, 1)).refused)

    def test_on_demand_api_covers_three_physical_owner_strata_and_refuses_four_distinct_wedge(self):
        mean, covariance = self.m213.generated_spd_cell(4, 213700004)
        local = self.m213.build_local_state(mean, covariance)
        k4 = self.m213.event_local_coefficient(local, (0, 0, 0, 0))
        k31 = self.m213.event_local_coefficient(local, (0, 0, 0, 1))
        k22 = self.m213.event_local_coefficient(local, (0, 0, 1, 1))
        distinct = self.m213.event_local_coefficient(local, (0, 0, 1, 2), outer_g=-0.23)
        wedge = self.m213.event_local_coefficient(local, (0, 1, 2, 3))
        self.assertEqual((k4.stratum, k31.stratum, k22.stratum, distinct.stratum), ("[4]", "[3,1]", "[2,2]", "[2,1,1]"))
        self.assertEqual((k4.source211_denominator, distinct.source211_denominator), (6, 1))
        self.assertTrue(k31.refused)
        self.assertTrue(k22.refused)
        self.assertIsNone(k31.source211_coefficient)
        self.assertIsNone(k22.source211_coefficient)
        self.assertEqual(distinct.conditional_m178_calls, 1)
        self.assertTrue(all(item.m178_contained for item in (k4, distinct)))
        self.assertEqual(wedge.stratum, "[1,1,1,1]")
        self.assertTrue(wedge.refused)
        self.assertIsNone(wedge.value)
        self.assertIsNone(wedge.source211_coefficient)
        self.assertEqual(wedge.conditional_m178_calls, 0)

    def test_falsifier_records_identity_confidence_and_provider_stop_without_variance(self):
        report = self.m213.run_falsifier()
        self.assertEqual(report["mutation"], "M213")
        self.assertEqual(report["m178_calls_per_distinct_event"], 1)
        # Frozen GH64/96 identity audit is intentionally allowed to falsify
        # the candidate; M149 forbids relaxing this reference after seeing it.
        self.assertFalse(report["identity_gate_pass"])
        self.assertIn(report["confidence_gate_pass"], (True, False))
        self.assertTrue(report["m178_local_numerical_gate_pass"])
        self.assertFalse(report["local_provider_gate_pass"])
        self.assertFalse(report["collision_owner_gate_pass"])
        self.assertFalse(report["whole_source_provider_gate_pass"])
        self.assertIn("next affine", report["whole_source_stop_reason"])
        self.assertFalse(report["source_variance_executed"])


if __name__ == "__main__":
    unittest.main()
