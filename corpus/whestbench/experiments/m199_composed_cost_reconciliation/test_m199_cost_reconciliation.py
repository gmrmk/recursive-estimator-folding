import unittest

from m199_cost_reconciliation import load_and_validate


class M199CostReconciliationTests(unittest.TestCase):
    def test_frozen_ledger_validates(self):
        payload = load_and_validate()
        self.assertEqual(payload["disposition"], "BLOCKED_OVERLAP")

    def test_no_unknown_is_credited_as_zero(self):
        payload = load_and_validate()
        unknowns = [
            row for row in payload["operation_ledger"]
            if row.get("amount_billions") is None
        ]
        self.assertEqual(len(unknowns), 5)
        self.assertTrue(all(row["overlap_class"] == "unknown" for row in unknowns))

    def test_m125b_is_embedded_not_additive(self):
        payload = load_and_validate()
        rows = {row["id"]: row for row in payload["operation_ledger"]}
        self.assertEqual(
            rows["m125b_corrected_standalone_total"]["overlap_class"],
            "embedded_do_not_add",
        )


if __name__ == "__main__":
    unittest.main()
