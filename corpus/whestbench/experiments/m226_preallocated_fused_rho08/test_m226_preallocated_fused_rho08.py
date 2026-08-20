"""TDD/static contract for M226's execution-only topology mutation."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m226_preallocated_fused_rho08.py"
    spec = importlib.util.spec_from_file_location("m226_native", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M226 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M226PreallocatedTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m226 = _load()

    def test_manifest_freezes_m224_math_and_keeps_variance_closed(self):
        manifest = json.loads((HERE / "M226_FROZEN_MANIFEST_20260809.json").read_text())
        self.assertEqual(manifest["parent_code_sha256"], self.m226.M224_CODE_SHA256)
        self.assertFalse(manifest["frozen_math"]["estimator_algebra_change"])
        self.assertEqual(manifest["frozen_math"]["abs_rho_max"], 0.08)
        self.assertEqual(manifest["frozen_math"]["plackett_composite_simpson_panels"], 32)
        self.assertEqual(manifest["frozen_math"]["event_radius"], "1e-8*(1+abs(midpoint))")
        self.assertFalse(manifest["variance_gate_authorized"])
        self.assertFalse((HERE / "run_m226_source_variance.py").exists())

    def test_persistent_setup_matches_frozen_two_slab_allocation_ledger(self):
        kernel = self.m226.PersistentKernel(9)
        ledger = kernel.allocation_ledger()
        self.assertEqual(ledger["empty_calls"], 2)
        self.assertEqual(ledger["float64_elements"], 268 * 9)
        self.assertEqual(ledger["bool_elements"], 2 * 9)
        self.assertEqual(ledger["total_bytes"], 2146 * 9)
        self.assertEqual(ledger["runtime_user_allocation_bytes"], 0)

    def test_small_billed_probe_matches_frozen_calls_bill_and_m224_parity(self):
        packed = self.m226.core.single_event_batch(
            width=3,
            seed=221700003,
            labels=(0, 0, 1, 2),
            outer_g=(0.0, 0.25, -2.5),
        )
        expected = self.m226.core.evaluate_numpy(packed)
        kernel = self.m226.PersistentKernel(packed.size)
        report = self.m226.run_billed_batch(packed, kernel)
        self.assertIsNone(report["failure"], report)
        self.assertEqual(report["billed_flops"], 5467 * packed.size)
        self.assertEqual(sum(row["calls"] for row in report["operations"].values()), 171)
        expected_calls = {
            "abs": 7,
            "add": 37,
            "divide": 14,
            "exp": 3,
            "greater": 1,
            "greater_equal": 2,
            "isfinite": 1,
            "less_equal": 6,
            "logical_and": 9,
            "matmul": 1,
            "maximum": 6,
            "multiply": 76,
            "sqrt": 2,
            "subtract": 6,
        }
        self.assertEqual(
            {name: row["calls"] for name, row in report["operations"].items()},
            expected_calls,
        )
        for forbidden in ("empty", "copyto", "sum", "max", "reshape"):
            self.assertNotIn(forbidden, report["operations"])
        self.assertEqual(report["allocation"]["runtime_user_allocation_bytes"], 0)
        self.assertEqual(report["fallback_count"], 0)
        np.testing.assert_array_equal(report["chart_ok"], expected.chart_ok)
        np.testing.assert_array_less(np.abs(report["value"] - expected.value), expected.radius)
        np.testing.assert_allclose(report["radius"], expected.radius, rtol=0.0, atol=1e-20)

    def test_persistent_kernel_rebinds_without_runtime_allocation_or_state_leak(self):
        first = self.m226.core.single_event_batch(
            width=3,
            seed=221700003,
            labels=(0, 0, 1, 2),
            outer_g=(0.0, 0.25, -2.5),
        )
        second = self.m226.core.single_event_batch(
            width=4,
            seed=221700004,
            labels=(0, 0, 1, 2),
            outer_g=(-0.25, 1.0, 2.5),
        )
        kernel = self.m226.PersistentKernel(3)
        first_report = self.m226.run_billed_batch(first, kernel)
        first_values = np.asarray(first_report["value"]).copy()
        second_report = self.m226.run_billed_batch(second, kernel)
        expected_second = self.m226.core.evaluate_numpy(second)
        self.assertEqual(first_report["allocation"]["total_bytes"], second_report["allocation"]["total_bytes"])
        self.assertEqual(second_report["billed_flops"], 5467 * 3)
        np.testing.assert_array_less(
            np.abs(second_report["value"] - expected_second.value),
            expected_second.radius,
        )
        self.assertTrue(np.all(np.isfinite(first_values)))

    def test_frozen_native_issuer_shape_and_seeds_are_unchanged(self):
        packed = self.m226.generated_native_batch(221720001)
        self.assertEqual(packed.size, 3968)
        self.assertEqual(packed.labels.shape, (3968, 4))
        self.assertEqual(len(packed.local_states), 3968)


if __name__ == "__main__":
    unittest.main()
