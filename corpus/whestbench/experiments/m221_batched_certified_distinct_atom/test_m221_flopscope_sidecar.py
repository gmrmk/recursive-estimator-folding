"""TDD/native contract for M221's charged vector sidecar."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m221_batched_certified_distinct_atom as core


def _load_sidecar():
    path = HERE / "m221_flopscope_sidecar.py"
    spec = importlib.util.spec_from_file_location("m221_sidecar", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M221 sidecar")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M221FlopscopeSidecarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sidecar = _load_sidecar()

    def test_small_billed_batch_exposes_copies_allocations_and_matches_core(self):
        packed = core.generated_probe_batch(3, 221700003, outer_g=(0.0, 0.25, -2.5))
        expected = core.evaluate_numpy(packed)
        report = self.sidecar.run_billed_batch(packed)
        self.assertIsNone(report["failure"], report)
        self.assertGreater(report["billed_flops"], 0)
        self.assertGreater(report["allocation"]["total_bytes"], 0)
        self.assertGreater(report["operations"].get("copyto", {}).get("calls", 0), 0)
        self.assertGreater(report["operations"].get("exp", {}).get("calls", 0), 0)
        self.assertEqual(report["event_count"], packed.size)
        np.testing.assert_array_less(
            np.abs(report["value"] - expected.value),
            expected.radius,
        )
        np.testing.assert_array_equal(report["chart_ok"], expected.chart_ok)

    def test_target_batch_has_exact_frozen_shape_and_issuer_rule(self):
        packed = self.sidecar.generated_native_batch(221720001)
        self.assertEqual(packed.size, 3968)
        self.assertEqual(packed.labels.shape, (3968, 4))
        self.assertEqual(len(packed.local_states), 3968)


if __name__ == "__main__":
    unittest.main()
