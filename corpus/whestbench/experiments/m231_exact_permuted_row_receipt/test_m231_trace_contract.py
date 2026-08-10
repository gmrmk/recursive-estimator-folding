"""RED/GREEN contract for M231's frozen fresh-process trace harness."""

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
    BASE / "m227_row_subset_collision_ht",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_m231_native_trace as runner  # noqa: E402


class M231TraceContractTests(unittest.TestCase):
    def test_target_trace_uses_frozen_dimensions_bill_and_cap(self):
        self.assertEqual(runner.WIDTH, 256)
        self.assertEqual(runner.LAYERS, 31)
        self.assertEqual(runner.SUBSET_ROWS, 32)
        self.assertEqual(runner.EXPECTED_M231_BILL, 864_993_280)
        self.assertEqual(runner.EXPECTED_COMBINED_BILL, 2_114_246_656)
        self.assertEqual(runner.COMBINED_EFFECTIVE_CAP, 3_727_757_440)
        result = runner.run_trace(
            runner.generated_records(227700001), seed=227700001
        )
        self.assertIsNone(result["failure"])
        self.assertEqual(result["m231_bill"], 864_993_280)
        self.assertEqual(result["combined_arithmetic_bill"], 2_114_246_656)
        operations = result["operations"]
        self.assertEqual(operations["random.Generator.permuted"]["calls"], 1)
        self.assertEqual(operations["matmul"]["calls"], 2)
        self.assertNotIn("argsort", operations)
        self.assertNotIn("reshape", operations)


if __name__ == "__main__":
    unittest.main()
