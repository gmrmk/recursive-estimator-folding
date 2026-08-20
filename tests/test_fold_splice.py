"""Contract tests for scripts/fold_splice.py — the mutation-chamber enumerator.

Splicing composes PASSED TISSUE from two atlas records whose failures lie on
different boundaries.  It proposes; it never revives: both parents' reopening
constraints ride along on every stub, and records without real passed tissue
(the "No passed component is asserted" sentinel) can never be parents.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fold_splice  # noqa: E402


def rec(rid, tissue, boundaries, families, status="killed"):
    return {
        "id": rid, "canonical_status": status, "index": 0,
        "passed_tissue": tissue, "failed_link": [f"{rid} broke here"],
        "failure_boundaries": boundaries, "operator_families": families,
        "information_sources": [], "kill_condition": "kc",
        "prediction": "p", "raw_status": status, "result_present": True,
        "reopening_condition": [f"{rid} reopening constraint"],
    }


SENTINEL = ["No passed component is asserted; preserve the exact "
            "predeclaration, evidence, and falsifier as negative knowledge."]


class SpliceBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fold_splice_test_"))
        self.atlas = self.tmp / "atlas.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_atlas(self, records):
        self.atlas.write_text(json.dumps(
            {"schema_version": 1, "ledger_sha256": "x", "invariants": {},
             "purpose": "test", "summary": {}, "records": records}),
            encoding="utf-8")


class ProposeContract(SpliceBase):
    def test_sentinel_records_are_never_parents(self):
        self.write_atlas([
            rec("a", SENTINEL, ["arithmetic_cost"], ["sampling_and_design"]),
            rec("b", ["real component"], ["variance_or_signal_to_noise"],
                ["sampling_and_design"]),
        ])
        props = fold_splice.propose(self.atlas)
        self.assertEqual(props, [])

    def test_pair_requires_shared_family_and_disjoint_primary_boundary(self):
        self.write_atlas([
            rec("a", ["tissue A"], ["arithmetic_cost"], ["sampling_and_design"]),
            rec("b", ["tissue B"], ["variance_or_signal_to_noise"],
                ["sampling_and_design"]),
            rec("c", ["tissue C"], ["arithmetic_cost"], ["sampling_and_design"]),
            rec("d", ["tissue D"], ["variance_or_signal_to_noise"],
                ["analytic_moment_closure"]),
        ])
        props = fold_splice.propose(self.atlas)
        pairs = {tuple(sorted(p["parents"])) for p in props}
        self.assertIn(("a", "b"), pairs)      # shared family, disjoint primary
        self.assertNotIn(("a", "c"), pairs)   # same primary boundary
        self.assertNotIn(("b", "d"), pairs)   # no shared family
        self.assertNotIn(("a", "a"), pairs)   # no self-pairs

    def test_stub_carries_tissue_and_reopening_constraints(self):
        self.write_atlas([
            rec("a", ["tissue A"], ["arithmetic_cost"], ["sampling_and_design"]),
            rec("b", ["tissue B"], ["variance_or_signal_to_noise"],
                ["sampling_and_design"]),
        ])
        p = fold_splice.propose(self.atlas)[0]
        self.assertEqual(p["tissue"], {"a": ["tissue A"], "b": ["tissue B"]})
        self.assertIn("a reopening constraint", p["reopening_constraints"])
        self.assertIn("b reopening constraint", p["reopening_constraints"])
        self.assertIn("never revives", p["note"])
        self.assertTrue(p["splice_id"].startswith("splice_"))

    def test_deterministic_and_capped(self):
        records = []
        fams = ["sampling_and_design", "control_and_multifidelity"]
        for i in range(12):
            records.append(rec(
                f"r{i:02d}", [f"tissue {i}"],
                ["arithmetic_cost" if i % 2 else "variance_or_signal_to_noise"],
                fams))
        self.write_atlas(records)
        p1 = fold_splice.propose(self.atlas, top=5)
        p2 = fold_splice.propose(self.atlas, top=5)
        self.assertEqual(p1, p2)
        self.assertEqual(len(p1), 5)

    def test_write_output_file(self):
        self.write_atlas([
            rec("a", ["tissue A"], ["arithmetic_cost"], ["sampling_and_design"]),
            rec("b", ["tissue B"], ["variance_or_signal_to_noise"],
                ["sampling_and_design"]),
        ])
        out = self.tmp / "splices.json"
        fold_splice.propose(self.atlas, out_path=out)
        data = json.loads(out.read_text("utf-8"))
        self.assertEqual(len(data["proposals"]), 1)
        self.assertEqual(data["atlas_sha256"],
                         fold_splice.sha256_file(self.atlas))


class RealAtlasSmoke(unittest.TestCase):
    def test_runs_on_the_real_atlas(self):
        real = ROOT / "corpus/whestbench/headroom/GEN6_FAILURE_SALVAGE_ATLAS_20260809.json"
        props = fold_splice.propose(real, top=10)
        self.assertEqual(len(props), 10)
        for p in props:
            self.assertNotIn("No passed component", json.dumps(p["tissue"]))
            self.assertTrue(p["reopening_constraints"])


if __name__ == "__main__":
    unittest.main()
