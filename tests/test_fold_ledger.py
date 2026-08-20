import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fold_ledger", ROOT / "scripts" / "fold_ledger.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FoldLedgerTests(unittest.TestCase):
    def test_canonical_and_explicit_legacy_status_namespaces(self):
        self.assertTrue(MODULE.status_is_allowed("screened"))
        self.assertTrue(MODULE.status_is_allowed("blocked"))
        self.assertTrue(MODULE.status_is_allowed(
            "repair_source_interface_carrier_blocked"
        ))
        self.assertTrue(MODULE.status_is_allowed(
            "killed_preexecution_static_cost"
        ))
        self.assertFalse(MODULE.status_is_allowed("totally_made_up_status"))
        self.assertFalse(MODULE.status_is_allowed("validated somehow"))

    def valid_payload(self):
        return {
            "schema_version": 1,
            "invariants": {key: "set" for key in MODULE.REQUIRED_INVARIANTS},
            "candidates": [
                {
                    "id": "candidate-a",
                    "status": "promoted",
                    "mechanism": "one causal operator",
                    "bias_class": "unbiased",
                    "prediction": "lower paired score",
                    "kill_condition": "confidence interval reaches zero",
                    "artifact_hash": "abc",
                    "matched_units": 20,
                    "primary_effect": -0.1,
                    "ci_upper": -0.01,
                    "failures": 0,
                    "holdout_used_for_generation": False,
                }
            ],
        }

    def test_valid_promoted_ledger(self):
        self.assertEqual(MODULE.audit(self.valid_payload()), [])

    def test_rejects_failed_promotion(self):
        payload = self.valid_payload()
        payload["candidates"][0]["failures"] = 1
        self.assertTrue(any("resource failures" in item for item in MODULE.audit(payload)))

    def test_rejects_holdout_leakage(self):
        payload = self.valid_payload()
        payload["candidates"][0]["holdout_used_for_generation"] = True
        self.assertTrue(any("holdout firewall" in item for item in MODULE.audit(payload)))

    def test_round_trip(self):
        payload = self.valid_payload()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            MODULE.write(path, payload)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), payload)


if __name__ == "__main__":
    unittest.main()
