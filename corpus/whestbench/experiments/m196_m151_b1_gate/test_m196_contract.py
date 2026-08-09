"""Static fail-closed contract tests for the M196 M151 successor gate."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _load_checker():
    spec = importlib.util.spec_from_file_location("m196_checker", HERE / "check_m196_feasibility.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M196ContractTest(unittest.TestCase):
    def test_predeclaration_freezes_all_hard_gates(self) -> None:
        text = (HERE / "M196_PREDECLARATION_20260808.md").read_text(encoding="utf-8")
        for token in (
            "24 Philox cells", "V_H/V_Delta", "below `0.25`", "<= 1.25",
            "10.291363760B", "512 MiB", "K=128", "B=1", "nodes=49",
        ):
            self.assertIn(token, text)

    def test_checker_does_not_conflate_existing_components_with_provider(self) -> None:
        checker = _load_checker()
        self.assertIn("build_b1_state", checker._entry(HERE / "missing.py", {"build_b1_state"})["required_symbols"])
        m151 = checker._entry(
            HERE.parent / "m151_b1_forward_control" / "m151_b1_forward_control.py",
            {"B1CanonicalState", "forward_b1_control_source"},
        )
        self.assertTrue(m151["ready"])
        self.assertNotIn("build_b1_state", m151["symbols_present"])

    def test_runner_is_not_present_before_provider_gate(self) -> None:
        self.assertFalse((HERE / "run_m196_generated_variance.py").exists())


if __name__ == "__main__":
    unittest.main()
