"""No-forward static gates for the V31-G4 component child."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import sys
import textwrap
import unittest
from pathlib import Path

for _name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_name] = "1"

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CANDIDATE = HERE / "candidate_source"
PARENT = HERE.parent / "v31_guards" / "package_source"
sys.path.insert(0, str(CANDIDATE))

import row_blocked_winograd as rbw  # noqa: E402


rbw.fnp = np


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class StaticContracts(unittest.TestCase):
    def test_parent_cost_model_is_byte_identical(self):
        self.assertEqual(
            sha256(PARENT / "cost_model.py"),
            "2A42E0D9CA3A80ECB4FF2BE302CCFAAACFA34BF6FE920B1EEA27FEB7AE798D68",
        )
        self.assertEqual(
            (PARENT / "cost_model.py").read_bytes(),
            (CANDIDATE / "cost_model.py").read_bytes(),
        )

    def test_candidate_retains_the_complete_parent_kernel_as_prefix(self):
        parent = (PARENT / "row_blocked_winograd.py").read_bytes()
        child = (CANDIDATE / "row_blocked_winograd.py").read_bytes()
        self.assertEqual(
            hashlib.sha256(parent).hexdigest().upper(),
            "A3BF5C8014198E33037D6AEAFC3F4138A98908754BB82BFCF5ACDD92B1D9FCCA",
        )
        self.assertTrue(child.startswith(parent))

    def test_production_partition_workspace_and_calls(self):
        child = rbw.GroupedRowBlockedBatchedWinograd(64_512, 256)
        self.assertEqual(
            child.dispatch_plan(64_512),
            [(4, 4_096), (4, 4_096), (4, 4_096), (3, 4_096), (1, 3_072)],
        )
        self.assertEqual(child.buffer_bytes, 63_438_848)

        even = rbw.grouped_row_blocked_bill_identity(64_512, 256, 256)
        odd = rbw.grouped_row_blocked_bill_identity(64_512, 256, 255)
        direct = rbw.grouped_row_blocked_bill_identity(64_512, 255, 256)
        self.assertEqual((even["core_calls"], even["total_matmul_calls"]), (5, 5))
        self.assertEqual((odd["core_calls"], odd["total_matmul_calls"]), (5, 10))
        self.assertEqual(
            (
                direct["core_calls"],
                direct["runtime_winograd_core_calls"],
                direct["primary_matmul_calls"],
                direct["total_matmul_calls"],
            ),
            (16, 0, 16, 16),
        )

    def test_all_width_pairs_preserve_bill_and_frozen_call_law(self):
        for k in range(1, 257):
            for n in range(1, 257):
                bill = rbw.owned_batched_candidate_bill(64_512, k, n)
                identity = rbw.grouped_row_blocked_bill_identity(64_512, k, n)
                self.assertEqual(identity["selected_bill"], bill.total)
                if bill.strategy.startswith("direct"):
                    self.assertEqual(identity["core_calls"], 16)
                    self.assertEqual(identity["runtime_winograd_core_calls"], 0)
                    self.assertEqual(identity["primary_matmul_calls"], 16)
                    self.assertEqual(identity["total_matmul_calls"], 16)
                else:
                    self.assertEqual(identity["core_calls"], 5)
                    self.assertEqual(identity["primary_matmul_calls"], 5)
                    self.assertEqual(
                        identity["total_matmul_calls"],
                        5 * (1 + int(bool(bill.output_tail))),
                    )

    def test_hot_grouped_path_has_no_view_materialization_api(self):
        tree = ast.parse(
            textwrap.dedent(
                inspect.getsource(rbw.GroupedRowBlockedBatchedWinograd.multiply)
            )
        )
        forbidden = {
            "reshape",
            "stack",
            "concatenate",
            "broadcast_to",
            "pad",
            "as_strided",
        }
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertFalse(calls & forbidden, calls & forbidden)

    def test_preexecution_manifest_is_explicitly_zero_authority(self):
        manifest = json.loads((HERE / "PREEXECUTION_MANIFEST.json").read_text("utf-8"))
        self.assertEqual(manifest["status"], "synthetic_contracts_only")
        self.assertFalse(manifest["authority"]["generated_network_forward"])
        self.assertFalse(manifest["authority"]["truth_or_scorer"])
        self.assertFalse(manifest["authority"]["hosted_run"])
        self.assertFalse(manifest["authority"]["submission"])
        self.assertEqual(manifest["constants"], {"BLOCK_ROWS": 4096, "GROUP": 4})

    def test_every_manifest_source_and_fixture_hash_matches(self):
        manifest = json.loads((HERE / "PREEXECUTION_MANIFEST.json").read_text("utf-8"))
        for relative, digest in manifest["child_source"].items():
            with self.subTest(source=relative):
                self.assertEqual(sha256(HERE / relative), digest)
        for relative, item in manifest["synthetic_fixtures"].items():
            with self.subTest(fixture=relative):
                self.assertEqual(sha256(HERE / relative), item["sha256"])


if __name__ == "__main__":
    unittest.main()
