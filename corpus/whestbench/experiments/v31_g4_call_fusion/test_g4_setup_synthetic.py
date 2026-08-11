"""Isolated no-predict setup contracts for both supported width paths."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "candidate_source"


class SetupSyntheticContracts(unittest.TestCase):
    def test_width_256_and_validator_width_4_bind_declared_storage(self):
        program = r'''
import json
import flopscope.numpy as fnp
from pathlib import Path
from whestbench import SetupContext
from kerdock_v3_estimator import Estimator

root = Path(r"__CANDIDATE__").resolve()
rows = []
for width, depth, budget in ((256, 32, 272_000_000_000), (4, 3, 100_000_000)):
    estimator = Estimator()
    estimator.setup(SetupContext(
        width=width,
        depth=depth,
        flop_budget=budget,
        api_version="0.14.0",
        submission_dir=str(root),
        seed=0,
    ))
    plan = estimator._winograd.dispatch_plan(64_512)
    group_checks = []
    start = 0
    for group, (blocks, block_rows) in zip(
        estimator._winograd._bound_left_groups, plan
    ):
        span = blocks * block_rows
        storage = estimator._activation
        group_checks.append({
            "row_start": start,
            "row_stop": start + span,
            "shape": list(group.shape),
            "strides": list(group.strides),
            "expected_strides": [
                block_rows * storage.strides[0],
                storage.strides[0],
                storage.strides[1],
            ],
            "shares_exact_source": bool(fnp.shares_memory(
                group, storage[start:start + span, :]
            )),
            "shares_before": bool(
                start and fnp.shares_memory(group, storage[:start, :])
            ),
            "shares_after": bool(
                start + span < storage.shape[0]
                and fnp.shares_memory(group, storage[start + span:, :])
            ),
        })
        start += span
    rows.append({
        "width": width,
        "activation_shape": list(estimator._activation.shape),
        "dispatch_plan": [list(item) for item in plan],
        "workspace_bytes": estimator._winograd.buffer_bytes,
        "group_checks": group_checks,
        "complete_row_coverage": start,
        "inplace_group_list_alias": bool(
            estimator._winograd._bound_out_groups
            is estimator._winograd._bound_left_groups
        ),
    })
print("G4_SETUP_JSON=" + json.dumps(rows, sort_keys=True))
'''.replace("__CANDIDATE__", str(CANDIDATE).replace("\\", "\\\\"))
        env = os.environ.copy()
        env["PYTHONPATH"] = str(CANDIDATE)
        for name in (
            "OPENBLAS_NUM_THREADS",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ):
            env[name] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", "-c", program],
            cwd=HERE.parents[3],
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        line = next(
            item for item in completed.stdout.splitlines()
            if item.startswith("G4_SETUP_JSON=")
        )
        payload = json.loads(line.split("=", 1)[1])
        plan = [[4, 4_096], [4, 4_096], [4, 4_096], [3, 4_096], [1, 3_072]]
        for item, width, workspace in zip(
            payload, (256, 4), (63_438_848, 1_048_688)
        ):
            with self.subTest(width=width):
                self.assertEqual(item["width"], width)
                self.assertEqual(item["activation_shape"], [64_512, width])
                self.assertEqual(item["dispatch_plan"], plan)
                self.assertEqual(item["workspace_bytes"], workspace)
                self.assertEqual(item["complete_row_coverage"], 64_512)
                self.assertTrue(item["inplace_group_list_alias"])
                start = 0
                for check, (blocks, block_rows) in zip(
                    item["group_checks"], plan
                ):
                    span = blocks * block_rows
                    self.assertEqual(check["row_start"], start)
                    self.assertEqual(check["row_stop"], start + span)
                    self.assertEqual(check["shape"], [blocks, block_rows, width])
                    self.assertEqual(check["strides"], check["expected_strides"])
                    self.assertTrue(check["shares_exact_source"])
                    self.assertFalse(check["shares_before"])
                    self.assertFalse(check["shares_after"])
                    start += span


if __name__ == "__main__":
    unittest.main()
