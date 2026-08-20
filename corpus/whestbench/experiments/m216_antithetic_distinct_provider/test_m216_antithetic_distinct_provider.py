"""TDD contract for M216's strict-distinct antithetic child."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m216_antithetic_distinct_provider.py"
    spec = importlib.util.spec_from_file_location("m216_provider", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M216 provider")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M216AntitheticDistinctTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m216 = _load()

    def test_frozen_manifest_precedes_code_and_variance_is_firewalled(self):
        manifest = json.loads((HERE / "M216_FROZEN_MANIFEST_20260809.json").read_text())
        self.assertEqual(manifest["widths"], [3, 4, 5, 6, 7])
        self.assertEqual(manifest["m178_calls_per_coupled_event"], 2)
        self.assertFalse(manifest["variance_gate_authorized_initially"])
        self.assertFalse((HERE / "run_m216_source_variance.py").exists())
        self.assertFalse((HERE / "M216_SOURCE_VARIANCE_RESULTS_20260809.json").exists())

    def test_antithetic_kernel_is_exact_pair_average_and_refuses_every_other_stratum(self):
        local = self.m216.frozen_local_state(5, 216700005)
        coupled = self.m216.antithetic_distinct_event(local, (0, 0, 1, 2), 0.73)
        plus = self.m216.parent_distinct_event(local, 0, 1, 2, 0.73)
        minus = self.m216.parent_distinct_event(local, 0, 1, 2, -0.73)
        self.assertAlmostEqual(coupled.value, 0.5 * (plus.value + minus.value), places=14)
        self.assertEqual(coupled.m178_calls, 2)
        swapped = self.m216.antithetic_distinct_event(local, (0, 0, 2, 1), 0.73)
        self.assertLess(abs(swapped.value - coupled.value), 2e-12)
        for labels in ((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 1, 2, 3)):
            with self.assertRaises(self.m216.M216DomainRefusal):
                self.m216.antithetic_distinct_event(local, labels, 0.73)

    def test_positive_gauge_and_permutation_covariance(self):
        local = self.m216.frozen_local_state(5, 216700005)
        gauge = np.exp(np.asarray((-0.4, -0.1, 0.0, 0.2, 0.5)))
        permutation = np.asarray((3, 0, 4, 1, 2), dtype=int)
        gauged = self.m216.build_local_state(
            local.mean * gauge,
            local.covariance * gauge[:, None] * gauge[None, :],
        )
        permuted = self.m216.build_local_state(
            local.mean[permutation],
            local.covariance[np.ix_(permutation, permutation)],
        )
        inverse = np.argsort(permutation)
        labels = (0, 0, 1, 2)
        g = -0.5
        baseline = self.m216.antithetic_distinct_event(local, labels, g).value
        observed_gauge = self.m216.antithetic_distinct_event(gauged, labels, g).value
        expected_gauge = baseline * gauge[0] ** 2 * gauge[1] * gauge[2]
        self.assertLess(abs(observed_gauge - expected_gauge), 5e-8 * (1.0 + abs(expected_gauge)))
        permuted_labels = tuple(int(inverse[index]) for index in labels)
        observed_permutation = self.m216.antithetic_distinct_event(permuted, permuted_labels, g).value
        self.assertLess(abs(observed_permutation - baseline), 5e-8 * (1.0 + abs(baseline)))

    def test_independent_adaptive_oracle_agrees_on_one_frozen_cell(self):
        local = self.m216.frozen_local_state(3, 216700003)
        result = self.m216.identity_oracle_check(local, 0, 1, 2, primary_dps=60, crosscheck_dps=80)
        self.assertTrue(result.oracle_self_pass, result)
        self.assertTrue(result.identity_pass, result)
        self.assertTrue(math.isfinite(result.reference))
        self.assertNotEqual(result.oracle_method, "gauss-hermite")

    def test_numerical_census_and_static_count_are_bounded(self):
        report = self.m216.run_numerical_and_static_gates()
        # This is a falsifier, not a test that forces promotion.  The frozen
        # threshold must decide the boolean without being relaxed after the
        # census is observed.
        self.assertEqual(
            report["numerical_gate_pass"],
            report["max_radius_ratio"] <= 2e-7,
        )
        self.assertIsNotNone(report["worst_radius_record"])
        self.assertEqual(report["m178_calls_per_event"], 2)
        self.assertLessEqual(report["local_counted_worst"], 4096)
        self.assertLessEqual(report["static_per_event_worst"], 12192)
        self.assertEqual(report["target_static_worst"], 48377856)

    def test_native_rss_probe_returns_a_real_process_measurement(self):
        self.assertGreater(self.m216._rss_bytes(), 0)


if __name__ == "__main__":
    unittest.main()
