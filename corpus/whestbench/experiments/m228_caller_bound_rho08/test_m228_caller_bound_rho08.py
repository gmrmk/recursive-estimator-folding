"""RED/GREEN contracts for M228's caller-owned measurement boundary."""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m228_caller_bound_rho08.py"
    spec = importlib.util.spec_from_file_location("m228_native", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M228 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M228CallerBoundBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m228 = _load()

    def test_predeclaration_preserves_m224_math_and_native_gate(self):
        manifest = json.loads((HERE / "M228_STATIC_LEDGER_20260809.json").read_text())
        self.assertEqual(self.m228.M224_CODE_SHA256, "6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B")
        self.assertEqual(manifest["runtime"]["calls"], 171)
        self.assertEqual(manifest["runtime"]["bill"], "5467*N")
        self.assertEqual(manifest["gates"]["raw_wall_strict_max_s"], self.m228.RAW_WALL_STRICT_MAX_S)
        self.assertFalse(manifest["gates"]["variance_gate_authorized"])

    def test_caller_owned_inputs_have_exact_provenance_and_setup_bytes(self):
        packed = self.m228.core.single_event_batch(width=3, seed=221700003, labels=(0, 0, 1, 2), outer_g=(0.0, 0.25, -2.5))
        bound, setup = self.m228.caller_owned_inputs(packed)
        self.assertEqual(len(bound.columns), 20)
        self.assertTrue(setup["raw_columns_alias_caller"])
        self.assertTrue(setup["marginal_left_owns_data"])
        self.assertTrue(setup["marginal_right_owns_data"])
        self.assertEqual(setup["marginal_bytes"], 16 * packed.size)
        self.assertTrue(setup["event_dependent_preprocessing"])
        self.assertEqual(setup["integrated_cost_credit"], 0)

    def test_bound_entrypoint_has_no_pre_timer_or_pre_budget_preparation(self):
        source = (HERE / "m228_caller_bound_rho08.py").read_text()
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_billed_bound_kernel")
        calls = [node for node in ast.walk(function) if isinstance(node, ast.Call)]
        called_names = {getattr(node.func, "id", None) for node in calls}
        called_attrs = {getattr(node.func, "attr", None) for node in calls}
        self.assertNotIn("caller_owned_inputs", called_names)
        self.assertNotIn("bind", called_attrs)
        self.assertNotIn("prepare_inputs", called_names)
        self.assertIn("BudgetContext", called_attrs)

    def test_measured_runtime_ledger_is_separate_from_wall_timing_and_returns_slab_views(self):
        packed = self.m228.core.single_event_batch(width=3, seed=221700003, labels=(0, 0, 1, 2), outer_g=(0.0, 0.25, -2.5))
        bound, _ = self.m228.caller_owned_inputs(packed)
        kernel = self.m228.PersistentKernel(packed.size)
        kernel.bind(bound)
        audit = self.m228.measure_bound_kernel_allocation(kernel)
        report = self.m228.run_billed_bound_kernel(kernel)
        allocation = report["allocation"]
        self.assertEqual(allocation["persistent_total_bytes"], kernel._float_slab.nbytes + kernel._bool_slab.nbytes)
        self.assertTrue(audit["runtime_allocation_measured"])
        self.assertGreaterEqual(audit["source_attributed_python_bytes"], 0)
        self.assertEqual(audit["billed_flops"], 5467 * packed.size)
        self.assertTrue(audit["persistent_slab_fingerprint_stable"])
        self.assertFalse(allocation["runtime_allocation_measured"])
        self.assertTrue(allocation["separate_allocation_audit_required"])
        self.assertTrue(np.shares_memory(report["value"], kernel._float_slab))
        self.assertTrue(np.shares_memory(report["radius"], kernel._float_slab))
        self.assertTrue(np.shares_memory(report["chart_ok"], kernel._bool_slab))

    def test_m228_matches_m224_and_preserves_171_call_topology(self):
        packed = self.m228.core.single_event_batch(width=3, seed=221700003, labels=(0, 0, 1, 2), outer_g=(0.0, 0.25, -2.5))
        expected = self.m228.core.evaluate_numpy(packed)
        bound, _ = self.m228.caller_owned_inputs(packed)
        kernel = self.m228.PersistentKernel(packed.size)
        kernel.bind(bound)
        report = self.m228.run_billed_bound_kernel(kernel)
        self.assertIsNone(report["failure"], report)
        self.assertEqual(report["billed_flops"], 5467 * packed.size)
        self.assertEqual(sum(row["calls"] for row in report["operations"].values()), 171)
        self.assertEqual(report["fallback_count"], 0)
        np.testing.assert_array_equal(report["chart_ok"], expected.chart_ok)
        np.testing.assert_array_less(np.abs(report["value"] - expected.value), expected.radius)
        np.testing.assert_allclose(report["radius"], expected.radius, rtol=0.0, atol=1e-20)


if __name__ == "__main__":
    unittest.main()
