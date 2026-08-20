import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_failure_salvage_atlas", ROOT / "scripts" / "build_failure_salvage_atlas.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FailureSalvageAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = MODULE.build_payload(MODULE.DEFAULT_LEDGER)

    def test_every_ledger_record_is_covered_once(self):
        records = self.payload["records"]
        ledger = MODULE.json.loads(MODULE.DEFAULT_LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(len(records), self.payload["summary"]["total_records"])
        self.assertEqual(len({record["id"] for record in records}), len(records))
        self.assertEqual(len(records), len(ledger["candidates"]))

    def test_every_record_has_typed_salvage_and_reopening_rule(self):
        for record in self.payload["records"]:
            for field in (
                "operator_families", "information_sources", "failure_boundaries",
                "passed_tissue", "failed_link", "reopening_condition",
            ):
                self.assertTrue(record[field], f"{record['id']} missing {field}")

    def test_known_boundaries_are_not_misreported_as_wins(self):
        by_id = {record["id"]: record for record in self.payload["records"]}
        self.assertEqual(by_id["m192_cross_output_frame_gls_oracle"]["canonical_status"], "screened_component")
        self.assertEqual(by_id["m197_crossed_three_rotation_u_statistic"]["canonical_status"], "killed_or_closed")
        self.assertEqual(by_id["m196_m151_b1_native_provider_gate"]["canonical_status"], "blocked")
        self.assertEqual(by_id["m198_source211_delay_one_adapter"]["canonical_status"], "screened_component")
        self.assertEqual(by_id["m204_lowrank_b1_lifted_control"]["canonical_status"], "killed_or_closed")
        self.assertEqual(by_id["m205_rankone_complete_physical_owner"]["canonical_status"], "blocked")
        self.assertEqual(by_id["m206_m204_native_replacement_audit"]["canonical_status"], "killed_or_closed")
        self.assertEqual(by_id["m207_zero_variance_rank_one_guard"]["canonical_status"], "preserved_component")
        self.assertEqual(by_id["v31_guards_m186_m187"]["canonical_status"], "validated")

    def test_render_is_deterministic(self):
        first = MODULE.serialized(self.payload)
        second = MODULE.serialized(MODULE.build_payload(MODULE.DEFAULT_LEDGER))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
