"""Regression tests for v3.1's fail-closed hostile and package gates."""
from __future__ import annotations

import unittest

from run_v31_gates import hostile_gate_pass, tar_members_gate_pass


class V31GatePredicateTests(unittest.TestCase):
    def test_g2_requires_every_anchor_and_child_condition(self) -> None:
        healthy = {
            "v3_reproduced": True,
            "v3_billed_match": True,
            "completes": True,
            "finite_all": True,
            "within_budget": True,
            "fired_expected": True,
        }
        self.assertTrue(hostile_gate_pass(**healthy))
        for key in healthy:
            broken = dict(healthy)
            broken[key] = False
            with self.subTest(key=key):
                self.assertFalse(hostile_gate_pass(**broken))

    def test_g3_rejects_missing_unexpected_and_pycache_members(self) -> None:
        base = {
            "returncode": 0,
            "missing": [],
            "unexpected": [],
            "members": ["estimator.py", "manifest.json"],
        }
        self.assertTrue(tar_members_gate_pass(**base))
        cases = (
            {**base, "returncode": 1},
            {**base, "missing": ["estimator.py"]},
            {**base, "unexpected": ["extra.bin"]},
            {**base, "members": ["__pycache__/estimator.pyc"]},
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertFalse(tar_members_gate_pass(**case))


if __name__ == "__main__":
    unittest.main()
