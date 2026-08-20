"""TDD contract for M221's algebra-preserving vector chart."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m221_batched_certified_distinct_atom.py"
    spec = importlib.util.spec_from_file_location("m221_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M221 core")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M221VectorChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m221 = _load()

    def test_manifest_freezes_algebra_chart_and_variance_firewall(self):
        manifest = json.loads((HERE / "M221_FROZEN_MANIFEST_20260809.json").read_text())
        self.assertFalse(manifest["algebra_change"])
        self.assertEqual(manifest["chart"]["phi_erf_taylor_terms"], 16)
        self.assertEqual(manifest["chart"]["plackett_composite_simpson_panels"], 32)
        self.assertFalse(manifest["variance_gate_authorized_initially"])
        self.assertFalse((HERE / "run_m221_source_variance.py").exists())

    def test_vector_batch_preserves_the_m216_antithetic_midpoint(self):
        packed = self.m221.generated_probe_batch(5, 221700005, outer_g=(0.0, 0.25, -2.5, 8.0))
        observed = self.m221.evaluate_numpy(packed)
        expected = self.m221.scalar_m216_midpoints(packed)
        self.assertTrue(np.all(observed.chart_ok))
        self.assertEqual(int(np.count_nonzero(observed.fallback)), 0)
        np.testing.assert_array_less(np.abs(observed.value - expected), observed.radius)
        np.testing.assert_array_less(
            observed.radius / (1.0 + np.abs(observed.value)),
            np.full(observed.value.shape, 2.0e-7),
        )

    def test_inherited_m216_tail_failure_is_inside_the_new_certified_interval(self):
        packed = self.m221.single_event_batch(
            width=6,
            seed=216700006,
            labels=(1, 1, 0, 2),
            outer_g=(8.0, -8.0),
        )
        observed = self.m221.evaluate_numpy(packed)
        references = self.m221.high_precision_midpoints(packed, dps=100)
        self.assertTrue(np.all(observed.chart_ok))
        np.testing.assert_array_less(np.abs(observed.value - references), observed.radius)
        self.assertLessEqual(float(np.max(observed.radius / (1.0 + np.abs(observed.value)))), 2e-7)

    def test_chart_refuses_instead_of_clipping_or_zeroing(self):
        packed = self.m221.single_event_batch(
            width=3,
            seed=221700003,
            labels=(0, 0, 1, 2),
            outer_g=(64.0,),
        )
        observed = self.m221.evaluate_numpy(packed)
        self.assertFalse(bool(observed.chart_ok[0]))
        self.assertTrue(bool(observed.fallback[0]))
        self.assertTrue(np.isnan(observed.value[0]))
        self.assertTrue(np.isnan(observed.radius[0]))

    def test_frozen_full_numerical_census_and_high_precision_subset(self):
        report = self.m221.run_frozen_numerical_gate()
        # M221 is a frozen falsifier.  Its tight midpoint certificate may pass
        # even when the predeclared chart covariance gate kills deployment.
        self.assertFalse(report["numerical_gate_pass"], report)
        self.assertEqual(report["fallback_count"], 0)
        self.assertLessEqual(report["max_radius_ratio"], 2e-7)
        self.assertTrue(report["high_precision_gate_pass"])
        self.assertTrue(report["scalar_parent_containment_pass"])
        self.assertTrue(report["inherited_worst_pass"])
        self.assertFalse(report["invariance"]["pass"])
        self.assertGreater(report["invariance"]["gauge_fallback_count"], 0)


if __name__ == "__main__":
    unittest.main()
