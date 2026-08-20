from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location(
        "m214_ledger", HERE / "m214_complete_domain_replacement_dag.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M214 ledger")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M214ReplacementLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m214 = _load()

    def test_source_m151_decomposition_is_exact(self):
        ledger = self.m214.build_ledger()
        self.assertEqual(ledger["source_m151_total"], "89.708636240")
        self.assertEqual(ledger["known_replacement_subtotal"], "93.175727824")
        self.assertEqual(ledger["remaining_before_unknowns"], "6.824272176")
        self.assertEqual(ledger["terminal_floor_sensitivity_total"], "93.309945040")
        self.assertEqual(ledger["after_terminal_floor_sensitivity"], "6.690054960")

    def test_no_overlap_or_same_call_credit(self):
        ledger = self.m214.build_ledger()
        rows = {row["id"]: row for row in ledger["rows"]}
        self.assertEqual(rows["m151_b1_core"]["disposition"], "removed_by_new_dag")
        self.assertEqual(rows["m151_endpoint_provider"]["disposition"], "removed_by_new_dag")
        self.assertEqual(rows["m179"]["disposition"], "fully_additive")
        self.assertEqual(rows["m212"]["disposition"], "fully_additive_new_call")
        self.assertNotIn("overlap_credit", ledger)
        self.assertFalse(ledger["legacy_background_replacement_credit"])

    def test_unknowns_keep_candidate_blocked(self):
        ledger = self.m214.build_ledger()
        self.assertEqual(ledger["status"], "BLOCKED_COMPLETE_DOMAIN_REPLACEMENT_DAG")
        self.assertFalse(ledger["cost_coherent"])
        self.assertFalse(ledger["provider_pass_assumed"])
        self.assertFalse(ledger["variance_or_efficacy_authorized"])
        self.assertGreaterEqual(len(ledger["unknowns"]), 5)


if __name__ == "__main__":
    unittest.main()
