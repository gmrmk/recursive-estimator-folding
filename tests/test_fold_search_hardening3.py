"""Hardening round 3 — the seed-agreement check.

Demonstrated live by k32_base_sensitivity_v2: the spec declared fresh seeds
while the frozen runner still hardcoded the v1 seeds, producing a bit-identical
rerun of already-observed data presented as a replication. The harness never
injects spec.seeds — runners own their seeds — so the only structural defense
is verdict-time contradiction detection against the seeds the runner reports.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fold_search  # noqa: E402


def seeded_runner(value, seeds):
    payload = {"ratio": value, "config": {"seeds": seeds}}
    return [sys.executable, "-c",
            f"import json; print(json.dumps({payload!r}))"]


def bare_runner(value):
    return [sys.executable, "-c",
            f"import json; print(json.dumps({{'ratio': {value}}}))"]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harden3_"))
        self.cells = self.tmp / "cells"
        self.ledger = self.tmp / "fold_ledger.json"
        self.ledger.write_text(json.dumps(
            {"schema_version": 1, "invariants": {}, "candidates": []}),
            encoding="utf-8")
        self.inp = self.tmp / "in.txt"
        self.inp.write_text("x", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def spec(self, cid, argv, seeds):
        return {
            "id": cid, "hypothesis": "h", "causal_mechanism": f"{cid} mech",
            "cheapest_falsifier": "one metric",
            "frozen_inputs": [str(self.inp)], "seeds": seeds,
            "equal_budget_baseline": "direct",
            "thresholds": {"metric": "ratio", "pass_when_lte": 0.95,
                           "kill_when_gte": 1.0},
            "budgets": {"wall_seconds": 30, "memory_mib_declared": 32,
                        "billed_flops_declared": 0},
            "runner": {"argv": argv, "cwd": str(self.tmp),
                       "readable_roots": [str(self.tmp)]},
            "predicted_signature": "s", "second_signal": "rerun",
            "evidence_role": "development",
            "confidence": {"implementation": 0.9, "mechanism": 0.5,
                           "generalization": 0.3, "compliance": 0.9},
        }

    def run_cell(self, cid, argv, seeds):
        cell = fold_search.predeclare(self.spec(cid, argv, seeds), self.cells,
                                      ledger_path=self.ledger)
        fold_search.run(cell)
        return cell


class SeedAgreement(Base):
    def test_seed_contradiction_is_protocol_kill(self):
        cell = self.run_cell("s1", seeded_runner(0.5, [11, 12]), seeds=[1, 2])
        out = fold_search.verdict(cell, self.ledger)
        self.assertEqual(out["verdict"], "KILL")
        self.assertEqual(out["status_written"], "killed_protocol")

    def test_matching_seeds_verdict_normally(self):
        cell = self.run_cell("s2", seeded_runner(0.5, [1, 2]), seeds=[1, 2])
        out = fold_search.verdict(cell, self.ledger)
        self.assertEqual(out["verdict"], "PASS_SCREEN")

    def test_runner_reporting_no_seeds_is_not_bound(self):
        cell = self.run_cell("s3", bare_runner(0.5), seeds=[1, 2])
        out = fold_search.verdict(cell, self.ledger)
        self.assertEqual(out["verdict"], "PASS_SCREEN")


if __name__ == "__main__":
    unittest.main()
