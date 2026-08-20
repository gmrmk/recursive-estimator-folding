"""RED/GREEN native process contract for frozen M235."""

from __future__ import annotations

from array import array
import inspect
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_m235_native_process as runner  # noqa: E402
import m235_official_setup_estimator as entry  # noqa: E402


class M235NativeContractTests(unittest.TestCase):
    def test_identity_audit_detects_live_field_rebinding(self):
        probe = entry.Estimator()
        probe._state = entry.m235.setup_component(setup_seed=235799999)
        probe._workspace_objects = tuple(entry.m235.workspace_arrays(probe._state))
        probe._identity_audit = array("Q", [0] * 41)
        expected = probe._identity_values()
        probe._state.base.p = probe._state.base.rho
        probe._write_identity_audit()
        self.assertNotEqual(list(probe._identity_audit), expected)

    def test_primary_process_uses_official_start_and_three_exact_predictions(self):
        self.assertEqual(runner.WIDTH, 256)
        self.assertEqual(runner.LAYERS, 31)
        self.assertEqual(runner.SUBSET_ROWS, 32)
        self.assertEqual(runner.EXPECTED_SETUP_RECEIPT_BILL, 32_768)
        self.assertEqual(runner.EXPECTED_M212_BILL, 1_249_253_376)
        self.assertEqual(runner.EXPECTED_M235_BILL, 864_960_512)
        self.assertEqual(runner.EXPECTED_COMBINED_BILL, 2_114_213_888)
        self.assertEqual(runner.CONSERVATIVE_COMBINED_BILL, 2_114_246_656)
        self.assertEqual(runner.OFFICIAL_START_CAP_S, 4.0)
        self.assertEqual(runner.SETUP_SEEDS[0], 0)
        self.assertEqual(runner.FIRST_SOURCE_SEEDS[0], 227700001)
        self.assertEqual(runner.SECOND_SOURCE_SEEDS[0], 227710001)

        run_source = inspect.getsource(runner.run_process)
        transport_source = inspect.getsource(runner._prediction_receipt)
        self.assertNotIn("m235.setup_component", run_source)
        self.assertNotIn("_run_prediction", run_source)
        self.assertIn("official.predict", transport_source)
        self.assertIn("_read_process_memory", run_source)
        self.assertLess(
            run_source.index("_prediction_receipt"), run_source.index("official.close")
        )
        stage_source = inspect.getsource(entry.Estimator._stage_f32_fixture)
        for forbidden in ("list(", ".shape", "str(", ".dtype"):
            self.assertNotIn(forbidden, stage_source)
        predict_source = inspect.getsource(entry.Estimator.predict)
        self.assertIn('flops.namespace("m212")', predict_source)
        self.assertIn('flops.namespace("m235")', predict_source)
        self.assertNotIn("fnp.zeros", predict_source)

        result = runner.run_process(pair_index=0, order="primary")
        self.assertIsNone(result["failure"])
        self.assertTrue(result["same_worker_transport"])
        self.assertEqual(result["transport"], "Win32 ReadProcessMemory")
        self.assertTrue(result["official_worker_pid"] > 0)
        self.assertLess(result["official_start_response_s"], 4.0)
        self.assertLess(result["component_setup_pre_manifest_s"], 4.0)
        self.assertLess(result["receipt_issue_s"], 0.05)
        self.assertEqual(result["setup_bill"], 32_768)
        self.assertEqual(result["setup_empty_calls"], 18)
        self.assertTrue(result["receipt_stable"])
        self.assertTrue(result["workspace_stable"])
        self.assertEqual(result["sequence"], ["A", "B", "A"])
        self.assertEqual(result["outputs"][0]["sha256"], result["outputs"][2]["sha256"])
        self.assertTrue(result["endpoint_bitwise_equal"])
        for prediction in result["predictions"]:
            self.assertEqual(
                prediction["worker_pid"], result["official_worker_pid"]
            )
            self.assertTrue(prediction["identity_stable"])
            self.assertIsNone(prediction["failure"])
            self.assertEqual(prediction["m212_bill"], 1_249_253_376)
            self.assertEqual(prediction["m235_bill"], 864_960_512)
            self.assertEqual(prediction["combined_bill"], 2_114_213_888)
            self.assertTrue(prediction["exact_calls"])
            self.assertTrue(prediction["m235_wall_fits"])
            self.assertTrue(prediction["lawful_combined_fits"])
            self.assertTrue(prediction["conservative_combined_fits"])
            self.assertTrue(prediction["finite"])
            self.assertTrue(prediction["symmetric"])
            self.assertLess(prediction["rss_mib"], 512.0)

    def test_g0_remains_closed(self):
        self.assertFalse((HERE / "M235_G0_RESULTS_20260809.json").exists())


if __name__ == "__main__":
    unittest.main()
