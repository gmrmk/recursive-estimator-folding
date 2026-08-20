"""Contract tests for scripts/fold_search.py — the fold-search harness.

Every test enforces one clause of the operational contract:
predeclare-before-run, frozen inputs, one-shot authorization, evidence
firewall, budget caps, mechanical verdicts, kill finality, append-only
ledger, and the four-way confidence report.  The harness is the spine;
heavier runners (the clone's measurement contract) plug into it.
"""

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


def ok_runner_argv(value="0.90"):
    # Emits a final-line metrics JSON like a real screen runner.
    code = f"import json; print(json.dumps({{'ratio': {value}}}))"
    return [sys.executable, "-c", code]


class HarnessBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fold_search_test_"))
        self.ledger = self.tmp / "fold_ledger.json"
        self.ledger.write_text(json.dumps({
            "schema_version": 1,
            "invariants": {"objective": "test"},
            "candidates": [
                {"id": "dead_mechanism", "status": "killed",
                 "mechanism": "spectral overlap tap at 0.7731",
                 "bias_class": "unbiased", "prediction": "x",
                 "kill_condition": "ratio >= 1.0"},
            ],
        }), encoding="utf-8")
        self.input_file = self.tmp / "frozen_input.txt"
        self.input_file.write_text("frozen bytes", encoding="utf-8")
        self.spec = {
            "id": "t1_identity_probe",
            "hypothesis": "the identity mutation changes nothing",
            "causal_mechanism": "no-op control path",
            "cheapest_falsifier": "single dev evaluation of the ratio",
            "frozen_inputs": [str(self.input_file)],
            "seeds": [11, 13],
            "equal_budget_baseline": "direct estimator at same rows",
            "thresholds": {"metric": "ratio", "pass_when_lte": 0.95,
                           "kill_when_gte": 1.0},
            "budgets": {"wall_seconds": 20, "memory_mib_declared": 64,
                        "billed_flops_declared": 0},
            "runner": {"argv": ok_runner_argv(), "cwd": str(self.tmp),
                       "readable_roots": [str(self.tmp)]},
            "predicted_signature": "ratio ~= 0.90 on both seeds",
            "second_signal": "byte-identical rerun of the dev metric",
            "evidence_role": "development",
            "confidence": {"implementation": 0.9, "mechanism": 0.5,
                           "generalization": 0.3, "compliance": 0.95},
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def predeclare(self, spec=None):
        return fold_search.predeclare(spec or self.spec, self.tmp / "cells",
                                      ledger_path=self.ledger)


class PredeclareContract(HarnessBase):
    def test_missing_required_field_refused(self):
        for field in ("hypothesis", "causal_mechanism", "cheapest_falsifier",
                      "thresholds", "budgets", "second_signal", "confidence"):
            spec = copy.deepcopy(self.spec)
            del spec[field]
            with self.assertRaises(fold_search.SpecError):
                self.predeclare(spec)

    def test_confidence_requires_all_four_axes(self):
        spec = copy.deepcopy(self.spec)
        del spec["confidence"]["generalization"]
        with self.assertRaises(fold_search.SpecError):
            self.predeclare(spec)

    def test_killed_id_refused_kill_finality(self):
        spec = copy.deepcopy(self.spec)
        spec["id"] = "dead_mechanism"
        with self.assertRaises(fold_search.KillFinalityError):
            self.predeclare(spec)

    def test_killed_numeric_token_collision_refused(self):
        # The MUB129 lesson: search the ledger by number, not only by name.
        spec = copy.deepcopy(self.spec)
        spec["causal_mechanism"] = "retap the 0.7731 overlap differently"
        with self.assertRaises(fold_search.KillFinalityError):
            self.predeclare(spec)

    def test_byte_identical_respec_refused(self):
        self.predeclare()
        with self.assertRaises(fold_search.KillFinalityError):
            self.predeclare()

    def test_holdout_path_refused_for_development_role(self):
        spec = copy.deepcopy(self.spec)
        bad = self.tmp / "holdout" ; bad.mkdir()
        spec["runner"]["readable_roots"].append(str(bad))
        with self.assertRaises(fold_search.FirewallError):
            self.predeclare(spec)

    def test_inputs_are_hash_frozen(self):
        cell = self.predeclare()
        pd = json.loads((cell / "predeclaration.json").read_text("utf-8"))
        self.assertEqual(
            pd["frozen_inputs"][0]["sha256"],
            fold_search.sha256_file(self.input_file))


class RunContract(HarnessBase):
    def test_run_produces_content_bound_report(self):
        cell = self.predeclare()
        report = fold_search.run(cell)
        rep = json.loads(report.read_text("utf-8"))
        self.assertEqual(rep["metrics"]["ratio"], 0.90)
        self.assertEqual(rep["evidence_role"], "development")
        pd_sha = fold_search.sha256_file(cell / "predeclaration.json")
        self.assertEqual(rep["predeclaration_sha256"], pd_sha)
        for key in ("python", "platform", "argv", "wall_seconds_used"):
            self.assertIn(key, rep["environment"] | rep, msg=key)

    def test_tampered_predeclaration_refuses_to_run(self):
        cell = self.predeclare()
        pd = json.loads((cell / "predeclaration.json").read_text("utf-8"))
        pd["thresholds"]["pass_when_lte"] = 99.0
        (cell / "predeclaration.json").write_text(json.dumps(pd), "utf-8")
        with self.assertRaises(fold_search.SealError):
            fold_search.run(cell)

    def test_tampered_frozen_input_refuses_to_run(self):
        cell = self.predeclare()
        self.input_file.write_text("mutated bytes", encoding="utf-8")
        with self.assertRaises(fold_search.SealError):
            fold_search.run(cell)

    def test_authorization_is_one_shot(self):
        cell = self.predeclare()
        fold_search.run(cell)
        with self.assertRaises(fold_search.OneShotError):
            fold_search.run(cell)

    def test_wall_budget_enforced_fail_closed(self):
        spec = copy.deepcopy(self.spec)
        spec["id"] = "t2_sleeper"
        spec["budgets"]["wall_seconds"] = 1
        spec["runner"]["argv"] = [sys.executable, "-c",
                                  "import time; time.sleep(30)"]
        cell = self.predeclare(spec)
        report = fold_search.run(cell)
        rep = json.loads(report.read_text("utf-8"))
        self.assertEqual(rep["outcome"], "BUDGET_KILL_WALL")

    def test_malformed_runner_output_is_canonical_kill(self):
        spec = copy.deepcopy(self.spec)
        spec["id"] = "t3_garbage"
        spec["runner"]["argv"] = [sys.executable, "-c", "print('not json')"]
        cell = self.predeclare(spec)
        rep = json.loads(fold_search.run(cell).read_text("utf-8"))
        self.assertEqual(rep["outcome"], "PROTOCOL_KILL_MALFORMED_METRICS")


class VerdictContract(HarnessBase):
    def _run(self, value):
        spec = copy.deepcopy(self.spec)
        spec["id"] = f"t4_val_{str(value).replace('.', '_')}"
        spec["runner"]["argv"] = ok_runner_argv(value)
        cell = self.predeclare(spec)
        fold_search.run(cell)
        return cell

    def test_pass_verdict_is_mechanical(self):
        cell = self._run("0.90")
        v = fold_search.verdict(cell, ledger_path=self.ledger)
        self.assertEqual(v["verdict"], "PASS_SCREEN")
        self.assertEqual(v["status_written"], "screened")

    def test_kill_verdict_is_mechanical(self):
        cell = self._run("1.30")
        v = fold_search.verdict(cell, ledger_path=self.ledger)
        self.assertEqual(v["verdict"], "KILL")
        self.assertEqual(v["status_written"], "killed")

    def test_gray_zone_is_inconclusive_not_pass(self):
        cell = self._run("0.97")
        v = fold_search.verdict(cell, ledger_path=self.ledger)
        self.assertEqual(v["verdict"], "INCONCLUSIVE")

    def test_ledger_append_is_append_only(self):
        before = json.loads(self.ledger.read_text("utf-8"))["candidates"]
        cell = self._run("1.30")
        fold_search.verdict(cell, ledger_path=self.ledger)
        after = json.loads(self.ledger.read_text("utf-8"))["candidates"]
        self.assertEqual(after[:len(before)], before)
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(after[-1]["status"], "killed")

    def test_killed_cell_cannot_be_repredeclared(self):
        cell = self._run("1.30")
        fold_search.verdict(cell, ledger_path=self.ledger)
        spec = copy.deepcopy(self.spec)
        spec["id"] = json.loads(
            (cell / "predeclaration.json").read_text("utf-8"))["id"]
        with self.assertRaises(fold_search.KillFinalityError):
            self.predeclare(spec)

    def test_verdict_reports_four_confidence_axes(self):
        cell = self._run("0.90")
        v = fold_search.verdict(cell, ledger_path=self.ledger)
        self.assertEqual(
            set(v["confidence"]),
            {"implementation", "mechanism", "generalization", "compliance"})


class TerminalIsolation(HarnessBase):
    def test_terminal_role_report_is_marked_no_mutation(self):
        spec = copy.deepcopy(self.spec)
        spec["id"] = "t5_terminal"
        spec["evidence_role"] = "validation"
        cell = fold_search.predeclare(spec, self.tmp / "cells",
                                      ledger_path=self.ledger, terminal=True)
        rep = json.loads(fold_search.run(cell).read_text("utf-8"))
        self.assertTrue(rep["terminal_no_mutation"])

    def test_terminal_role_without_flag_refused(self):
        spec = copy.deepcopy(self.spec)
        spec["id"] = "t6_terminal_noflag"
        spec["evidence_role"] = "validation"
        with self.assertRaises(fold_search.FirewallError):
            self.predeclare(spec)


if __name__ == "__main__":
    unittest.main()
