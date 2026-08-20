"""RED/GREEN static contracts for M232's retained M205 sigma seam."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def _load():
    path = HERE / "m232_m205_retained_sigma_seam.py"
    spec = importlib.util.spec_from_file_location("m232_native", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M232 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M232RetainedM205SigmaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m232 = _load()

    def test_predeclaration_freezes_inclusive_charges_and_parent_kernel(self):
        ledger = json.loads((HERE / "M232_STATIC_LEDGER_20260809.json").read_text())
        self.assertEqual(ledger["frozen_kernel"]["calls"], 171)
        self.assertEqual(ledger["frozen_kernel"]["bill"], "5467*N")
        self.assertTrue(ledger["blocked_if_current_m205_m212_abi_absent"])
        self.assertFalse(ledger["gates"]["variance_gate_authorized"])

    def test_m205_retention_is_exact_including_zero_diagonals(self):
        mean = np.zeros(3, dtype=np.float64)
        covariance = np.diag(np.asarray((0.0, 0.64, 1.69), dtype=np.float64))
        retained = self.m232.retain_m205_marginal_sigma(mean, covariance, layer=7, epoch=19)
        np.testing.assert_array_equal(retained.marginal_sigma, np.asarray((0.0, 0.8, 1.3)))
        np.testing.assert_array_equal(retained.factor, np.asarray((0.0, 0.8 / np.sqrt(2.0), 1.3 / np.sqrt(2.0))))
        self.assertIs(retained.marginal_sigma, retained.vector)

    def test_generated_m224_grid_gather_has_exact_values_gauge_and_permutation(self):
        proof = self.m232.generated_m224_semantic_proof()
        self.assertTrue(proof["m224_marginals_exact"])
        self.assertTrue(proof["m224_value_parity"])
        self.assertTrue(proof["gauge_exact"])
        self.assertTrue(proof["permutation_exact"])

    def test_binding_rejects_copy_wrong_epoch_and_conditional_substitution(self):
        retained = self.m232.retain_m205_marginal_sigma(np.zeros(3), np.eye(3), layer=7, epoch=19)
        with self.assertRaisesRegex(self.m232.M232Refusal, "COPY"):
            self.m232.bind_retained_sigma(retained, retained.vector.copy(), 7, 19)
        with self.assertRaisesRegex(self.m232.M232Refusal, "EPOCH"):
            self.m232.bind_retained_sigma(retained, retained.vector, 7, 20)
        with self.assertRaisesRegex(self.m232.M232Refusal, "COPY"):
            self.m232.bind_retained_sigma(retained, retained.vector * 0.9, 7, 19)

    def test_current_m205_m212_abi_is_blocked_without_reuse_claim(self):
        audit = self.m232.current_parent_seam_audit()
        self.assertEqual(audit["status"], "SEAM_PROTOTYPE_INTEGRATION_BLOCKED")
        self.assertFalse(audit["inclusive_trace_authorized"])
        self.assertEqual(audit["integrated_cost_credit"], 0)
        self.assertFalse(hasattr(self.m232, "run_inclusive_native_trace"))


if __name__ == "__main__":
    unittest.main()
