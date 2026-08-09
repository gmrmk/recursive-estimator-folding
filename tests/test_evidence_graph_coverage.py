import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "corpus" / "whestbench" / "graph" / "build_evidence_graph.py"
LEDGER = ROOT / "corpus" / "whestbench" / "headroom" / "fold_ledger.json"

SPEC = importlib.util.spec_from_file_location("build_evidence_graph", BUILDER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class EvidenceGraphCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = MODULE.build()
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_every_ledger_candidate_has_one_exhaustive_node(self):
        expected = {candidate["id"] for candidate in self.ledger["candidates"]}
        observed = {
            node.removeprefix("candidate::")
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("type") == "ledger_candidate"
        }
        self.assertEqual(expected, observed)
        self.assertEqual(len(expected), len(self.ledger["candidates"]))

    def test_every_candidate_has_typed_navigation_edges(self):
        for node, attrs in self.graph.nodes(data=True):
            if attrs.get("type") != "ledger_candidate":
                continue
            neighbor_types = {
                self.graph.nodes[neighbor].get("type")
                for neighbor in self.graph.neighbors(node)
            }
            self.assertIn("ledger_disposition", neighbor_types, node)
            self.assertIn("ledger_family", neighbor_types, node)
            self.assertIn("ledger_information", neighbor_types, node)
            self.assertIn("ledger_boundary", neighbor_types, node)

    def test_graph_marks_exhaustive_layer_as_non_evidentiary(self):
        self.assertEqual(
            self.graph.graph["exhaustive_ledger_count"],
            len(self.ledger["candidates"]),
        )
        self.assertEqual(
            self.graph.graph["exhaustive_layer_evidence"],
            "DESCRIPTIVE_INDEX_NOT_PROOF",
        )


if __name__ == "__main__":
    unittest.main()
