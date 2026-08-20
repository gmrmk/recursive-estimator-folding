"""RED/GREEN preflight contracts for M230's live-M223 gather seam."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m230_m223_live_sigma_gather.py"
    spec = importlib.util.spec_from_file_location("m230_native", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M230 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M230LiveM223SigmaSeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m230 = _load()

    def test_predeclaration_freezes_conditional_inclusive_boundary(self):
        ledger = json.loads((HERE / "M230_STATIC_LEDGER_20260809.json").read_text())
        self.assertEqual(ledger["kernel_parent"]["calls"], 171)
        self.assertEqual(ledger["kernel_parent"]["bill"], "5467*N")
        self.assertTrue(ledger["blocked_if_provider_absent"])
        self.assertFalse(ledger["gates"]["variance_gate_authorized"])

    def test_current_m223_context_is_integration_blocked_without_retained_vector(self):
        context = self.m230.make_generated_m223_context()
        audit = self.m230.audit_live_m223_sigma_provider(context)
        self.assertEqual(audit["status"], "SEAM_PROTOTYPE_INTEGRATION_BLOCKED")
        self.assertEqual(audit["reason"], "M223_RETAINED_MARGINAL_SIGMA_VECTOR_ABSENT")
        self.assertFalse(audit["reuse_credit_authorized"])
        self.assertFalse(audit["inclusive_trace_authorized"])

    def test_absent_vector_refuses_copy_wrong_epoch_and_conditional_substitution(self):
        context = self.m230.make_generated_m223_context()
        vector = np.sqrt(np.diag(context.C))
        with self.assertRaisesRegex(self.m230.M230IntegrationBlocked, "RETAINED_MARGINAL"):
            self.m230.bind_live_sigma_vector(context, vector, context.layer, context.epoch)
        with self.assertRaisesRegex(self.m230.M230IntegrationBlocked, "RETAINED_MARGINAL"):
            self.m230.bind_live_sigma_vector(context, vector.copy(), context.layer, context.epoch + 1)
        with self.assertRaisesRegex(self.m230.M230IntegrationBlocked, "RETAINED_MARGINAL"):
            self.m230.bind_live_sigma_vector(context, vector * 0.9, context.layer, context.epoch)

    def test_no_m230_inclusive_trace_is_exposed_while_provider_is_absent(self):
        self.assertFalse(hasattr(self.m230, "run_inclusive_native_trace"))


if __name__ == "__main__":
    unittest.main()
