from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import replay_v5d3 as replay


class V5FormulaTests(unittest.TestCase):
    def test_bound_inputs_match(self) -> None:
        verified = replay.verify_bound_inputs()
        self.assertEqual(set(verified), set(replay.INPUTS))

    def test_exact_hook3_fixture(self) -> None:
        got = replay.v5_components(64_512, 253, 255)
        self.assertEqual(got.depth_three_core, 5_556_520_011)
        self.assertEqual(got.ragged_k_direct, 143_990_784)
        self.assertEqual(got.ragged_k_add, 15_998_976)
        self.assertEqual(got.ragged_n_direct, 228_049_920)
        self.assertEqual(got.ragged_n_copy, 451_584)
        self.assertEqual(got.total, 5_945_011_275)

    def test_invalid_v5_shapes_fail_closed(self) -> None:
        for shape in ((0, 8, 8), (8, 0, 8), (8, 8, 0), (9, 8, 8), (8, 7, 8), (8, 8, 7)):
            with self.subTest(shape=shape), self.assertRaises(ValueError):
                replay.v5_components(*shape)

    def test_production_domain_formula_is_integral(self) -> None:
        for k in range(8, 257):
            for n in range(8, 257):
                with self.subTest(k=k, n=n):
                    value = replay.v5_components(64_512, k, n)
                    self.assertIsInstance(value.total, int)
                    self.assertGreater(value.total, 0)

    def test_call_laws(self) -> None:
        core = replay.v5_components(64_512, 256, 256)
        both = replay.v5_components(64_512, 253, 255)
        self.assertEqual(replay.v5_group_calls(core, 14), 14)
        self.assertEqual(replay.v5_group_calls(both, 14), 42)
        self.assertEqual(replay.v5_group_calls(core, 5), 5)
        self.assertEqual(replay.v5_group_calls(both, 5), 15)
        self.assertEqual(replay.parent_runtime_calls("direct_owned", 255), 16)
        self.assertEqual(replay.parent_runtime_calls("winograd_batched_owned", 256), 16)
        self.assertEqual(replay.parent_runtime_calls("winograd_batched_owned", 255), 32)


class V5ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = replay.replay()

    def test_ten_seed_totals(self) -> None:
        self.assertEqual(len(self.payload["per_seed"]), 10)
        for row in self.payload["per_seed"]:
            seed = row["seed"]
            self.assertEqual(row["hook_count"], 28)
            self.assertEqual(row["current_total"], replay.EXPECTED_CURRENT[seed])
            self.assertEqual(row["v5_selected_total"], replay.EXPECTED_V5[seed])

    def test_aggregate_exact(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["current_sum"], 1_530_887_087_800)
        self.assertEqual(aggregate["v5_sum"], 1_174_219_060_434)
        self.assertEqual(aggregate["saving_sum"], 356_668_027_366)
        self.assertEqual(aggregate["current_mean"], "153088708780.0")
        self.assertEqual(aggregate["v5_mean"], "117421906043.4")
        self.assertEqual(aggregate["saving_mean"], "35666802736.6")
        self.assertEqual(aggregate["minimum_saving_percent"], "21.600599510857")
        self.assertEqual(aggregate["maximum_saving_percent"], "25.128161558319")

    def test_seed11_classes_and_calls(self) -> None:
        row = next(item for item in self.payload["per_seed"] if item["seed"] == 11)
        self.assertEqual(
            row["class_counts"],
            {
                "core_only": 1,
                "ragged_k_only": 1,
                "ragged_n_only": 4,
                "both_ragged": 22,
            },
        )
        self.assertEqual(row["parent_runtime_calls"], 544)
        self.assertEqual(row["b1152_calls"], 1078)
        self.assertEqual(row["b4096_calls"], 385)

    def test_receipt_is_canonical_and_deterministic(self) -> None:
        first = replay.canonical_json(self.payload)
        second = replay.canonical_json(replay.replay())
        self.assertEqual(first, second)
        parsed = json.loads(first)
        self.assertEqual(parsed["schema"], "v31-v5d3-static-replay-v1")

    def test_write_receipt_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "receipt.json"
            path.write_text(replay.canonical_json(self.payload), encoding="utf-8", newline="\n")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.payload)

    def test_no_credit_boundary_is_machine_readable(self) -> None:
        authority = self.payload["authority"]
        self.assertTrue(authority)
        self.assertFalse(any(authority.values()))
        self.assertEqual(len(self.payload["limitations"]), 4)


if __name__ == "__main__":
    unittest.main()
