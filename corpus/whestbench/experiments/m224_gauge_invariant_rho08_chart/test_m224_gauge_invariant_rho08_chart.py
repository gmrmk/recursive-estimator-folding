"""TDD contract for M224's one-mechanism normalized-chart repair."""

from __future__ import annotations

from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m224_gauge_invariant_rho08_chart.py"
    spec = importlib.util.spec_from_file_location("m224_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M224 core")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M224GaugeInvariantChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m224 = _load()

    def test_manifest_freezes_one_mechanism_and_keeps_speed_and_variance_closed(self):
        manifest = json.loads((HERE / "M224_FROZEN_MANIFEST_20260809.json").read_text())
        self.assertFalse(manifest["estimator_algebra_change"])
        self.assertEqual(manifest["normalized_chart"]["abs_rho_max"], 0.08)
        self.assertEqual(manifest["unchanged_numerics"]["plackett_composite_simpson_panels"], 32)
        self.assertEqual(
            manifest["inherited_native_speed_gate"]["status"],
            "FAILED_AND_NOT_RERUN_IN_M224",
        )
        self.assertFalse(manifest["variance_gate_authorized"])
        self.assertFalse((HERE / "run_m224_native_speed.py").exists())
        self.assertFalse((HERE / "run_m224_source_variance.py").exists())

    def test_real_axis_plackett_bound_certifies_same_32_panel_rule_at_rho_point08(self):
        proof = self.m224.plackett_proof_certificate()
        self.assertEqual(proof["panels"], 32)
        self.assertEqual(proof["abs_rho_max"], 0.08)
        self.assertLessEqual(proof["fourth_derivative_bound"], 13.129531)
        self.assertLessEqual(proof["simpson_remainder_bound"], 2.280e-13)
        self.assertLess(proof["simpson_remainder_bound"], proof["phi2_radius"])

    def test_rho_above_frozen_chart_refuses_without_clipping_or_zeroing(self):
        packed = self.m224.single_event_batch(
            width=3,
            seed=221700003,
            labels=(0, 0, 1, 2),
            outer_g=(0.0,),
        )
        outside = replace(packed, pair_rho=np.asarray((0.0800000001,), dtype=np.float64))
        observed = self.m224.evaluate_numpy(outside)
        self.assertFalse(bool(observed.chart_ok[0]))
        self.assertTrue(bool(observed.fallback[0]))
        self.assertTrue(np.isnan(observed.value[0]))
        self.assertTrue(np.isnan(observed.radius[0]))

    def test_original_and_fresh_cells_are_zero_fallback_and_parent_contained(self):
        report = self.m224.run_frozen_numerical_gate()
        self.assertTrue(report["numerical_gate_pass"], report)
        self.assertEqual(report["original_census"]["event_count"], 2730)
        self.assertEqual(report["original_census"]["fallback_count"], 0)
        self.assertTrue(report["original_census"]["parent_containment_pass"])
        self.assertEqual(report["fresh_census"]["event_count"], 2730)
        self.assertEqual(report["fresh_census"]["fallback_count"], 0)
        self.assertTrue(report["fresh_census"]["parent_containment_pass"])
        self.assertLessEqual(report["max_radius_ratio"], 2e-7)

    def test_frozen_m221_native_cells_cover_old_rho_tail_without_fallback(self):
        report = self.m224.run_frozen_numerical_gate()
        native = report["m221_native_cells"]
        self.assertEqual(native["event_count"], 5 * 3968)
        self.assertEqual(native["fallback_count"], 0)
        self.assertGreaterEqual(native["max_abs_rho"], 0.0788)
        self.assertLessEqual(native["max_abs_rho"], 0.08)

    def test_normalized_chart_is_positive_gauge_covariant_and_permutation_safe(self):
        invariance = self.m224.run_frozen_numerical_gate()["invariance"]
        self.assertTrue(invariance["pass"], invariance)
        self.assertEqual(invariance["baseline_fallback_count"], 0)
        self.assertEqual(invariance["gauge_fallback_count"], 0)
        self.assertEqual(invariance["permutation_fallback_count"], 0)
        self.assertEqual(invariance["chart_membership_mismatch_count"], 0)
        self.assertLessEqual(invariance["max_normalized_coordinate_error"], 2e-14)
        self.assertLessEqual(invariance["max_gauge_scaled_error"], 5e-8)
        self.assertLessEqual(invariance["max_permutation_scaled_error"], 5e-8)

    def test_inherited_and_fresh_high_precision_oracles_fit_returned_radius(self):
        high_precision = self.m224.run_frozen_numerical_gate()["high_precision"]
        self.assertTrue(high_precision["pass"], high_precision)
        self.assertEqual(high_precision["probe_count"], 32)
        self.assertLessEqual(high_precision["max_oracle_gap"], high_precision["oracle_tolerance_max"])
        self.assertLessEqual(high_precision["max_midpoint_error"], high_precision["min_radius"])


if __name__ == "__main__":
    unittest.main()
