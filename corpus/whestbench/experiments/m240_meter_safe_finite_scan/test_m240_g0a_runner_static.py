"""Static-only contract for M240's durable six-method G0A runner.

This module never calls ``main`` and never creates a launch intent.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "run_m240_g0a_receipt.py"

EXPECTED_METHODS = (
    "test_production_source_has_no_generated_oracle_import",
    "test_dependency_free_nine_monomial_census",
    "test_all_twenty_columns_tree_and_m224_parity_on_frozen_grid",
    "test_positive_gauge_action_matches_every_frozen_column_degree",
    "test_co_permutation_changes_only_coordinate_names",
    "test_hostile_binders_domain_zero_write_and_one_use_lifetime",
)
EXPECTED_PARENT_HASHES = {
    "M240_PREDECLARATION_20260809.md":
        "CA52CDB93C60415145917879E8E36C3913382CB03267F9F99CCAFA7310FB0958",
    "M240_FROZEN_MANIFEST_20260809.json":
        "61187920D8D46C7132A212B81EF79DC13DD1CE32BD2EBA2547C0D63447E5E265",
    "M240_PREIMPLEMENTATION_ERRATUM_20260809.md":
        "CBE18DF72F8000071B93907CF9D0797A6DEBE40E9A94A361DB5D3D152B326AD9",
    "m240_meter_safe_finite_scan.py":
        "29B86374FF3A9B7ADC6D2B86F2C03A6F7F676303E5F100C46BEF1AC478B8C89E",
    "test_m240_meter_safe_finite_scan.py":
        "A5AE1A9A2C20B8E67C70E2771B6AEE4674A03315BC3CB1CE88DA40E0CABBF84B",
    "M240_TDD_RED_RECEIPT_20260809.md":
        "90E4D187BE5B308398496D1C95AE0F2CF9DC7C1CED65CAA55E2148767EC4EB4E",
    "M239_G0A_RESULT_20260809.json":
        "9271F2E9426B5FF1AB9882DE6787250EAE61C0D7C16EE4411D0E2FD86C6E6EAE",
    "m237_durable_native_receipt.py":
        "774CEF483C33B149524121144A4C5EDE9141F094AA6FE5037414E31BDDAC873C",
}


def _load_without_launch():
    spec = importlib.util.spec_from_file_location("m240_g0a_runner_static", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M240 G0A runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    with mock.patch.object(
        subprocess, "run", side_effect=AssertionError("import attempted subprocess launch")
    ) as launch:
        spec.loader.exec_module(module)
    if launch.call_count:
        raise AssertionError("runner launched during import")
    return module


class M240G0ARunnerStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = _load_without_launch()
        cls.source = RUNNER_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_frozen_hashes_interpreter_cwd_and_exact_six_method_command(self):
        runner = self.runner
        observed = {path.name: expected for path, expected in runner.PARENTS.items()}
        self.assertEqual(observed, EXPECTED_PARENT_HASHES)
        for path, expected in runner.PARENTS.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest().upper(), expected)
        self.assertEqual(runner.METHODS, EXPECTED_METHODS)
        expected_prefix = (
            "test_m240_meter_safe_finite_scan.M240AlgebraAndInterfaceTests."
        )
        self.assertEqual(runner.PREFIX, expected_prefix)
        self.assertEqual(
            runner.COMMAND,
            tuple(
                [str(runner.INTERPRETER), "-m", "unittest"]
                + [expected_prefix + method for method in EXPECTED_METHODS]
                + ["-v"]
            ),
        )
        self.assertEqual(len(runner.COMMAND), 10)
        self.assertNotIn(runner.FORBIDDEN_METHOD, runner.COMMAND)
        self.assertIn("test_target_digests_non_degeneracy", runner.FORBIDDEN_METHOD)
        self.assertEqual(runner.TIMEOUT_S, 120)
        self.assertEqual(runner.M240, HERE)
        self.assertEqual(
            runner.INTERPRETER,
            Path(
                r"C:\Users\strid\Documents\Codex\2026-08-02"
                r"\https-chatgpt-com-share-6a5556ed-2e1c"
                r"\work\whest-starterkit\.venv\Scripts\python.exe"
            ),
        )

    def test_one_shot_exclusive_durable_protocol_and_no_discovery_launch(self):
        calls = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        ]
        self.assertEqual(len(calls), 1)
        self.assertIn("if __name__ == \"__main__\":", self.source)
        self.assertIn("durable.hardlink_preflight(HERE)", self.source)
        self.assertIn("durable.write_launch_intent_exclusive(INTENT, intent_payload)", self.source)
        self.assertIn("durable.publish_native_result(", self.source)
        self.assertLess(
            self.source.index("write_launch_intent_exclusive"),
            self.source.index("subprocess.run("),
        )
        self.assertLess(
            self.source.index("subprocess.run("),
            self.source.index("publish_native_result("),
        )
        self.assertIn("if INTENT.exists() or RESULT.exists() or TEMP.exists():", self.source)
        self.assertIn("capture_output=True", self.source)
        self.assertIn("timeout=TIMEOUT_S", self.source)
        self.assertIn('"stdout": stdout', self.source)
        self.assertIn('"stderr": stderr', self.source)
        self.assertIn('"outcomes": outcomes', self.source)
        self.assertIn('"parent_hashes_before": before', self.source)
        self.assertIn('"parent_hashes_after": after', self.source)

    def test_authorization_flags_are_explicitly_closed_and_no_artifact_exists(self):
        for literal in (
            '"g0b_run": False',
            '"g0c_run": False',
            '"variance_run": False',
            '"integration_run": False',
        ):
            self.assertIn(literal, self.source)
        self.assertFalse(self.runner.INTENT.exists())
        self.assertFalse(self.runner.RESULT.exists())
        self.assertFalse(self.runner.TEMP.exists())


if __name__ == "__main__":
    unittest.main()
