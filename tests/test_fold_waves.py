"""Contract tests for scripts/fold_waves.py — DAG-parallel wave scheduling.

The wave layer sits above fold_search: cells may declare `depends_on` (other
cell ids) and `writes` (paths).  The scheduler computes topological waves,
refuses cycles and same-wave write overlap (the parallel-write guard the
clone's agent-graph validator taught us), runs independent ready cells in
parallel, and exports the whole cell DAG as graphify-ready node-link JSON.
"""

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fold_search  # noqa: E402
import fold_waves  # noqa: E402


def runner(value="0.90", sleep="0"):
    code = (f"import json, time; time.sleep({sleep}); "
            f"print(json.dumps({{'ratio': {value}}}))")
    return [sys.executable, "-c", code]


class WaveBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fold_waves_test_"))
        self.cells = self.tmp / "cells"
        self.ledger = self.tmp / "fold_ledger.json"
        self.ledger.write_text(json.dumps(
            {"schema_version": 1, "invariants": {}, "candidates": []}),
            encoding="utf-8")
        self.inp = self.tmp / "in.txt"
        self.inp.write_text("x", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def spec(self, cid, deps=(), writes=(), value="0.90"):
        return {
            "id": cid,
            "hypothesis": f"{cid} hypothesis",
            "causal_mechanism": f"{cid} mechanism",
            "cheapest_falsifier": "one dev metric",
            "frozen_inputs": [str(self.inp)],
            "seeds": [1],
            "equal_budget_baseline": "direct",
            "thresholds": {"metric": "ratio", "pass_when_lte": 0.95,
                           "kill_when_gte": 1.0},
            "budgets": {"wall_seconds": 30, "memory_mib_declared": 32,
                        "billed_flops_declared": 0},
            "runner": {"argv": runner(value), "cwd": str(self.tmp),
                       "readable_roots": [str(self.tmp)]},
            "predicted_signature": "ratio ~0.9",
            "second_signal": "rerun byte-identical",
            "evidence_role": "development",
            "confidence": {"implementation": 0.9, "mechanism": 0.5,
                           "generalization": 0.3, "compliance": 0.9},
            "depends_on": list(deps),
            "writes": [str(w) for w in writes],
        }

    def declare(self, *specs):
        for s in specs:
            fold_search.predeclare(s, self.cells, ledger_path=self.ledger)


class PlanContract(WaveBase):
    def test_waves_follow_dependencies(self):
        self.declare(self.spec("a"), self.spec("b", deps=["a"]),
                     self.spec("c", deps=["a"]), self.spec("d", deps=["b", "c"]))
        waves = fold_waves.plan(self.cells)
        self.assertEqual(waves, [["a"], ["b", "c"], ["d"]])

    def test_cycle_refused(self):
        self.declare(self.spec("a", deps=["b"]), self.spec("b", deps=["a"]))
        with self.assertRaises(fold_waves.DagError):
            fold_waves.plan(self.cells)

    def test_unknown_dependency_refused(self):
        self.declare(self.spec("a", deps=["ghost"]))
        with self.assertRaises(fold_waves.DagError):
            fold_waves.plan(self.cells)

    def test_same_wave_write_overlap_refused(self):
        shared = self.tmp / "out" / "shared.json"
        self.declare(self.spec("a", writes=[shared]),
                     self.spec("b", writes=[shared]))
        with self.assertRaises(fold_waves.WriteOverlapError):
            fold_waves.plan(self.cells)

    def test_ancestor_write_overlap_allowed(self):
        shared = self.tmp / "out" / "shared.json"
        self.declare(self.spec("a", writes=[shared]),
                     self.spec("b", deps=["a"], writes=[shared]))
        self.assertEqual(fold_waves.plan(self.cells), [["a"], ["b"]])


class RunContract(WaveBase):
    def test_wave_runs_parallel_and_verdicts(self):
        self.declare(self.spec("a", value="0.90"),
                     self.spec("b", value="1.30"))
        results = fold_waves.run_wave(self.cells, ["a", "b"],
                                      ledger_path=self.ledger, workers=2)
        by_id = {r["cell_id"]: r for r in results}
        self.assertEqual(by_id["a"]["verdict"], "PASS_SCREEN")
        self.assertEqual(by_id["b"]["verdict"], "KILL")
        led = json.loads(self.ledger.read_text("utf-8"))["candidates"]
        self.assertEqual({r["id"] for r in led}, {"a", "b"})

    def test_dependent_blocked_until_parent_passes(self):
        self.declare(self.spec("a", value="1.30"),
                     self.spec("b", deps=["a"]))
        fold_waves.run_wave(self.cells, ["a"], ledger_path=self.ledger)
        ready = fold_waves.ready_cells(self.cells)
        self.assertEqual(ready, [])  # parent KILLED -> child never ready

    def test_ready_after_parent_pass(self):
        self.declare(self.spec("a", value="0.90"),
                     self.spec("b", deps=["a"]))
        fold_waves.run_wave(self.cells, ["a"], ledger_path=self.ledger)
        self.assertEqual(fold_waves.ready_cells(self.cells), ["b"])


class ExportContract(WaveBase):
    def test_export_graph_is_node_link_with_status(self):
        self.declare(self.spec("a", value="0.90"),
                     self.spec("b", deps=["a"]))
        fold_waves.run_wave(self.cells, ["a"], ledger_path=self.ledger)
        out = self.tmp / "cells-graph.json"
        data = fold_waves.export_graph(self.cells, out)
        self.assertTrue(out.exists())
        ids = {n["id"] for n in data["nodes"]}
        self.assertEqual(ids, {"a", "b"})
        a = next(n for n in data["nodes"] if n["id"] == "a")
        self.assertEqual(a["status"], "PASS_SCREEN")
        self.assertEqual(a["type"], "search_cell")
        links = [(l["source"], l["target"]) for l in data["links"]]
        self.assertIn(("a", "b"), links)


if __name__ == "__main__":
    unittest.main()
