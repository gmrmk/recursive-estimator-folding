"""RED/GREEN static native contract for frozen M236.

This test module does not invoke an official worker.  The explicit one-process
falsifier remains a separately authorized command.
"""

from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m236_official_setup_estimator as entry  # noqa: E402
import run_m236_native_process as runner  # noqa: E402


class M236NativeStaticContractTests(unittest.TestCase):
    def test_prenative_erratum2_is_frozen(self):
        path = HERE / "M236_PRENATIVE_ERRATUM2_20260809.md"
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest().upper(),
            "6F01A9EE4CF99F73F4FB318A3FBB1244A1DEB09AA4C9DEFD76E8E1E17C29D5EB",
        )

    def test_frozen_single_process_constants_and_no_split_lifecycle(self):
        self.assertEqual(runner.RSS_CAP_MIB, 496.0)
        self.assertEqual(runner.SETUP_SEED, 0)
        self.assertEqual(runner.SOURCE_SEEDS, {"A": 227700001, "B": 227710001})
        self.assertEqual(runner.SEQUENCE, ("A", "B", "A"))
        self.assertEqual(runner.EXPECTED_M212_BILL, 1_249_253_376)
        self.assertEqual(runner.EXPECTED_M235_BILL, 864_960_512)
        self.assertEqual(runner.EXPECTED_COMBINED_BILL, 2_114_213_888)
        source = inspect.getsource(runner.run_one_process)
        transport_source = inspect.getsource(runner._prediction_receipt)
        self.assertIn("official.start", source)
        self.assertIn("official.predict", transport_source)
        self.assertIn("_prediction_receipt", source)
        self.assertLess(source.index("_prediction_receipt"), source.index("official.close"))
        self.assertNotIn("setup_component", source)
        self.assertNotIn("_run_prediction", source)

    def test_entrypoint_executes_real_block_compiler_and_releases_slots(self):
        record_source = inspect.getsource(entry.Estimator._records)
        self.assertIn("carrier = mlp.weights[LAYERS]", record_source)
        self.assertIn("weight=mlp.weights[layer]", record_source)
        self.assertIn("factor=carrier[layer]", record_source)
        for forbidden in ("copy", "asarray", "stack"):
            self.assertNotIn(forbidden, record_source)
        self.assertNotIn("self._", record_source)

        source = inspect.getsource(entry.Estimator.predict)
        self.assertIn('flops.namespace("m212")', source)
        self.assertIn('flops.namespace("m235")', source)
        self.assertIn("compile_block_m212", source)
        self.assertIn("subtract_block_m235", source)
        self.assertIn("staging_slots_clear", source)
        self.assertIn("del records", source)
        self.assertIn("return mlp.weights[LAYERS][:32]", source)
        self.assertNotIn("fnp.zeros", source)

        identity_source = inspect.getsource(entry.Estimator._identity_values)
        alias_source = inspect.getsource(entry._current_aliases)
        for forbidden in ("mlp", "carrier", "weight_slots", "factor_slots"):
            self.assertNotIn(forbidden, identity_source)
            self.assertNotIn(forbidden, alias_source)

    def test_g0_and_aggregate_remain_closed(self):
        self.assertFalse((HERE / "M236_G0_RESULTS_20260809.json").exists())
        self.assertFalse((HERE / "M236_NATIVE_TEN_PROCESS_RESULT_20260809.json").exists())


if __name__ == "__main__":
    unittest.main()
