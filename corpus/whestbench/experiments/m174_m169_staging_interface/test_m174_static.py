"""Unit entry point for the response-free M174 static verifier."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from verify_m174_static import assert_static_contract


class TestM174StaticContract(unittest.TestCase):
    def test_frozen_interface_and_liveness_claims(self) -> None:
        result = assert_static_contract()
        self.assertEqual(result["status"], "STATIC_PASS_VERDICT_REPAIR")
        self.assertEqual(result["m169_explicit_packing_bill"], 32_505_856)
        self.assertEqual(result["b8_blocks"], [8, 8, 8, 7])


if __name__ == "__main__":
    unittest.main()
