"""Hardening tests — one per confirmed review finding (C1,C3,C4,H1,H2,H3,M1,M2,M5).

Each asserts the guarantee the review defeated with a live repro. Red before
the fix, green after.
"""

import concurrent.futures as cf
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fold_search  # noqa: E402
import fold_waves  # noqa: E402


def ok_runner(value="0.90"):
    return [sys.executable, "-c",
            f"import json; print(json.dumps({{'ratio': {value}}}))"]


class HardenBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harden_"))
        self.cells = self.tmp / "cells"
        self.ledger = self.tmp / "fold_ledger.json"
        self.ledger.write_text(json.dumps(
            {"schema_version": 1, "invariants": {},
             "candidates": [{"id": "dead", "status": "killed",
                             "mechanism": "overlap tap at 0.7731",
                             "prediction": "x", "kill_condition": "y"}]}),
            encoding="utf-8")
        self.inp = self.tmp / "in.txt"
        self.inp.write_text("x", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def spec(self, cid, value="0.90", metric="ratio",
             pass_lte=0.95, kill_gte=1.0, roots=None, mech=None):
        return {
            "id": cid, "hypothesis": f"{cid} h",
            "causal_mechanism": mech or f"{cid} mechanism",
            "cheapest_falsifier": "one metric",
            "frozen_inputs": [str(self.inp)], "seeds": [1],
            "equal_budget_baseline": "direct",
            "thresholds": {"metric": metric, "pass_when_lte": pass_lte,
                           "kill_when_gte": kill_gte},
            "budgets": {"wall_seconds": 30, "memory_mib_declared": 32,
                        "billed_flops_declared": 0},
            "runner": {"argv": ok_runner(value), "cwd": str(self.tmp),
                       "readable_roots": roots or [str(self.tmp)]},
            "predicted_signature": "s", "second_signal": "rerun",
            "evidence_role": "development",
            "confidence": {"implementation": 0.9, "mechanism": 0.5,
                           "generalization": 0.3, "compliance": 0.9},
        }

    def declare(self, spec):
        return fold_search.predeclare(spec, self.cells, ledger_path=self.ledger)


class C1_Concurrency(HardenBase):
    def test_concurrent_verdicts_all_land(self):
        cells = []
        for i in range(24):
            c = self.declare(self.spec(f"c{i:02d}", value="0.90"))
            fold_search.run(c)
            cells.append(c)
        with cf.ThreadPoolExecutor(max_workers=12) as pool:
            list(pool.map(lambda c: fold_search.verdict(c, self.ledger), cells))
        led = json.loads(self.ledger.read_text("utf-8"))["candidates"]
        got = {r["id"] for r in led if r["id"].startswith("c")}
        self.assertEqual(got, {f"c{i:02d}" for i in range(24)})

    def test_concurrent_predeclare_all_registered(self):
        specs = [self.spec(f"p{i:02d}") for i in range(24)]
        with cf.ThreadPoolExecutor(max_workers=12) as pool:
            list(pool.map(self.declare, specs))
        reg = json.loads((self.cells / ".spec_hashes.json").read_text("utf-8"))
        self.assertEqual(len(reg), 24)


class C3_Firewall(HardenBase):
    def test_alt_spelled_holdout_refused(self):
        for name in ("heldout", "val", "eval", "gold", "answers"):
            d = self.tmp / name
            d.mkdir(exist_ok=True)
            spec = self.spec(f"fw_{name}", roots=[str(self.tmp), str(d)])
            with self.assertRaises(fold_search.FirewallError, msg=name):
                self.declare(spec)

    @unittest.skipUnless(os.name == "nt", "junction is Windows-specific")
    def test_junction_aliased_holdout_refused(self):
        real = self.tmp / "holdout"; real.mkdir()
        (real / "labels.json").write_text('{"secret": true}', encoding="utf-8")
        alias = self.tmp / "dev_view"
        subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(real)],
                       capture_output=True)
        spec = self.spec("fw_junc", roots=[str(alias)])
        with self.assertRaises(fold_search.FirewallError):
            self.declare(spec)


class C4_CrashPaths(HardenBase):
    def test_bad_executable_yields_report_not_exception(self):
        spec = self.spec("crash1")
        spec["runner"]["argv"] = ["this_executable_does_not_exist_xyz"]
        cell = self.declare(spec)
        report = fold_search.run(cell)  # must not raise
        rep = json.loads(report.read_text("utf-8"))
        self.assertTrue(rep["outcome"].startswith("PROTOCOL_KILL"))

    def test_crashed_cell_status_is_not_predeclared(self):
        spec = self.spec("crash2")
        spec["runner"]["argv"] = ["this_executable_does_not_exist_xyz"]
        cell = self.declare(spec)
        fold_search.run(cell)
        self.assertNotEqual(fold_waves._cell_status(cell), "predeclared")


class H2_MetricShape(HardenBase):
    def test_scalar_metrics_is_protocol_kill(self):
        spec = self.spec("h2a")
        spec["runner"]["argv"] = [sys.executable, "-c", "print('0.5')"]
        cell = self.declare(spec)
        rep = json.loads(fold_search.run(cell).read_text("utf-8"))
        self.assertEqual(rep["outcome"], "PROTOCOL_KILL_MALFORMED_METRICS")
        v = fold_search.verdict(cell, self.ledger)  # must not raise
        self.assertEqual(v["verdict"], "KILL")

    def test_missing_key_metrics_is_protocol_kill(self):
        spec = self.spec("h2b")
        spec["runner"]["argv"] = [sys.executable, "-c",
                                  "import json; print(json.dumps({'other': 1}))"]
        cell = self.declare(spec)
        rep = json.loads(fold_search.run(cell).read_text("utf-8"))
        self.assertEqual(rep["outcome"], "PROTOCOL_KILL_MALFORMED_METRICS")


class M1_NaN(HardenBase):
    def test_nan_metric_is_protocol_kill(self):
        spec = self.spec("m1")
        spec["runner"]["argv"] = [sys.executable, "-c", "print('{\"ratio\": NaN}')"]
        cell = self.declare(spec)
        rep = json.loads(fold_search.run(cell).read_text("utf-8"))
        self.assertEqual(rep["outcome"], "PROTOCOL_KILL_MALFORMED_METRICS")


class M2_ThresholdOrder(HardenBase):
    def test_inverted_thresholds_refused(self):
        with self.assertRaises(fold_search.SpecError):
            self.declare(self.spec("m2", pass_lte=1.0, kill_gte=0.9))


class H3_NumericCollision(HardenBase):
    def test_reformatted_killed_number_collides(self):
        # ledger 'dead' killed with 0.7731; these are the same value reworded.
        for reword in ("7.731e-1", "0.77310"):
            spec = self.spec(f"h3_{reword.replace('.','_').replace('-','_')}",
                             mech=f"retap the {reword} overlap")
            with self.assertRaises(fold_search.KillFinalityError, msg=reword):
                self.declare(spec)


class M5_TokenRace(HardenBase):
    def test_preexisting_consumed_token_gives_oneshot(self):
        cell = self.declare(self.spec("m5"))
        # simulate a stray leftover consumed marker beside a live token
        (cell / "GATE_TOKEN.consumed").write_text("stale", encoding="utf-8")
        with self.assertRaises(fold_search.OneShotError):
            fold_search.run(cell)


class H1_WavePartial(HardenBase):
    def test_sibling_crash_does_not_drop_clean_verdict(self):
        good = self.declare(self.spec("good", value="0.90"))
        spent = self.declare(self.spec("spent", value="0.90"))
        fold_search.run(spent)  # consume its token so run() raises OneShotError
        results = fold_waves.run_wave(self.cells, ["good", "spent"],
                                      ledger_path=self.ledger, workers=2)
        by = {r.get("cell_id"): r for r in results}
        self.assertEqual(by["good"]["verdict"], "PASS_SCREEN")
        led = {r["id"] for r in
               json.loads(self.ledger.read_text("utf-8"))["candidates"]}
        self.assertIn("good", led)


if __name__ == "__main__":
    unittest.main()
