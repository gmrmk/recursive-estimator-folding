from __future__ import annotations

from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from aggregate_m215_results import aggregate  # noqa: E402


class M215AggregateTests(unittest.TestCase):
    def test_pinned_flopscope_build_suffix_is_accepted_without_waiving_base_version(self):
        result = aggregate()
        self.assertTrue(result["gates"]["flopscope_0_10_0"])
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(
            result["status"],
            "EXACT_STRICT_DISTINCT_OWNERSHIP_BRIDGE_RESOURCE_COMPONENT_PASS_INTEGRATED_DAG_BLOCKED",
        )


if __name__ == "__main__":
    unittest.main()
