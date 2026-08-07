"""Tests for the response-free M175 static ABI no-go certificate."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from verify_m175_static import assert_static_contract


class M175StaticAuditTest(unittest.TestCase):
    def test_frozen_contract(self) -> None:
        result = assert_static_contract()
        self.assertEqual(result["status"], "NO_GO_CURRENT_CODE_EXACT_LABELLED_PRODUCER_ABSENT")
        self.assertEqual(result["fixed_blocks"], [8, 8, 8, 7])
        self.assertFalse(result["resource_certificate"])
        self.assertFalse(result["integration_runner_created"])


if __name__ == "__main__":
    unittest.main()
