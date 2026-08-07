from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
M164 = HERE.parent / "m164_staged_audit"
if str(M164) not in sys.path:
    sys.path.insert(0, str(M164))

from m164_flopscope_sidecar import allocate_workspace as allocate_m164_workspace  # noqa: E402
from m164_flopscope_sidecar import compile_layer as compile_m164_layer  # noqa: E402
from m169_fused_compiler import (  # noqa: E402
    COLLISION_MASS,
    LAYERS,
    WIDTH,
    allocate_staged_inputs,
    allocate_workspace,
    compile_staged_stack,
    initialize_target_q0,
    stage_inputs,
    static_prediction,
)


def generated(width: int, layers: int, seed: int):
    rng = np.random.default_rng(seed)
    weights, covariances = [], []
    for _ in range(layers):
        weights.append(rng.normal(size=(width, width)) * np.sqrt(2.0 / width))
        root = rng.normal(size=(width, width)) / np.sqrt(width)
        covariance = root @ root.T + 0.25 * np.eye(width)
        covariances.append(0.5 * (covariance + covariance.T))
    return weights, covariances


def compare(width: int, layers: int, seed: int):
    weights_np, covariances_np = generated(width, layers, seed)
    weights = [fnp.asarray(value, dtype=fnp.float64) for value in weights_np]
    covariances = [fnp.asarray(value, dtype=fnp.float64) for value in covariances_np]
    expected = []
    with flops.BudgetContext(10**12, quiet=True):
        reference_workspace = allocate_m164_workspace(width)
        for weight, covariance in zip(weights, covariances):
            values = compile_m164_layer(weight, covariance, reference_workspace)[:3]
            expected.append(tuple(np.asarray(value).copy() for value in values))
    with flops.BudgetContext(10**12, quiet=True) as budget:
        staged = allocate_staged_inputs(layers, width)
        workspace = allocate_workspace(layers, width)
        masses = fnp.asarray(np.array([COLLISION_MASS, 1.0 - COLLISION_MASS], dtype=np.float64), dtype=fnp.float64)
        initialize_target_q0(workspace, masses)
        stage_inputs(weights, covariances, staged)
        actual = compile_staged_stack(staged, workspace)[:3]
    return expected, tuple(np.asarray(value) for value in actual), budget


class TestM169CallFusion(unittest.TestCase):
    def test_small_shape_is_bitwise_m163_parity(self) -> None:
        expected, actual, _ = compare(width=7, layers=3, seed=169_001)
        for layer, reference in enumerate(expected):
            for component, value in enumerate(reference):
                self.assertTrue(np.array_equal(value, actual[component][layer]))

    def test_target_shape_is_bitwise_m163_parity(self) -> None:
        expected, actual, _ = compare(width=WIDTH, layers=LAYERS, seed=169_002)
        for layer, reference in enumerate(expected):
            for component, value in enumerate(reference):
                self.assertTrue(np.array_equal(value, actual[component][layer]))

    def test_target_trace_has_two_matmuls_and_all_packing_is_counted(self) -> None:
        _, _, budget = compare(width=WIDTH, layers=LAYERS, seed=169_003)
        operations = budget.summary_dict()["operations"]
        prediction = static_prediction()
        self.assertEqual(operations["matmul"]["calls"], prediction["predicted_total_matmul_calls"])
        self.assertIn("stack", operations)
        self.assertIn("copyto", operations)
        self.assertNotIn("reshape", operations)
        self.assertEqual(budget.flops_used, prediction["predicted_total_bill"])

    def test_static_prediction_has_no_block_cross_terms(self) -> None:
        prediction = static_prediction()
        self.assertTrue(prediction["no_block_cross_terms"])
        self.assertTrue(prediction["predicted_bill_fits_slot"])
        self.assertEqual(prediction["predicted_post_z_matmul_calls"], 1)
        self.assertEqual(prediction["predicted_total_matmul_calls"], 2)

    def test_no_response_or_network_imports(self) -> None:
        for name in ("m169_fused_compiler.py", "run_m169_native_trace.py", "run_m169_parity.py"):
            tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
            imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
            self.assertFalse(any(item.startswith(("requests", "whestbench", "aicrowd")) for item in imports))


if __name__ == "__main__":
    unittest.main()
