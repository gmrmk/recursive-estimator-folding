"""RED/GREEN contract for M227's generated fresh-process trace harness."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m209_batched_recursive_gram_control",
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_m227_native_trace as runner  # noqa: E402


class M227TraceContractTests(unittest.TestCase):
    def test_target_trace_uses_frozen_seed_shape_bill_and_effective_cap(self):
        self.assertEqual(runner.WIDTH, 256)
        self.assertEqual(runner.LAYERS, 31)
        self.assertEqual(runner.SUBSET_ROWS, 32)
        self.assertEqual(runner.EXPECTED_M227_BILL, 865_484_288)
        self.assertEqual(runner.EXPECTED_COMBINED_BILL, 2_114_737_664)
        self.assertEqual(runner.COMBINED_EFFECTIVE_CAP, 3_727_757_440)

        records = runner.generated_records(227700001)
        self.assertEqual(len(records), 31)
        self.assertTrue(all(record.weight.shape == (256, 256) for record in records))
        result = runner.run_trace(records, seed=227700001)
        self.assertIsNone(result["failure"])
        self.assertEqual(result["m227_bill"], 865_484_288)
        self.assertEqual(result["combined_arithmetic_bill"], 2_114_737_664)
        self.assertEqual(result["operations"]["matmul"]["calls"], 2)
        self.assertEqual(result["operations"]["reshape"]["calls"] if "reshape" in result["operations"] else 0, 0)


if __name__ == "__main__":
    unittest.main()
