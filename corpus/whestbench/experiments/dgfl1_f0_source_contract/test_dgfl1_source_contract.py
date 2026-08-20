"""Source-only contracts for the DGFL production seam.

These tests construct no generated network and read no truth or scorer.  They
bind the immutable GUARDS sources, the exact production-Q interception seam,
post-Q return semantics, selected-row geometry, and the coordinate transform
needed by the shared rotational JVP.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PARENT = HERE.parent / "v31_guards" / "package_source"
MANIFEST = HERE / "PREEXECUTION_MANIFEST.json"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PARENT))

from dgfl1_source_contract import (  # noqa: E402
    BASE_BRANCHES,
    DGFL_BASE_LABELS,
    ParentSourceContract,
    PostQReturnGate,
    ProductionRotationCapture,
    absorbed_generator,
    build_selected_unit_rows,
    fixed_antipodal_pairs,
    rotation_generator,
    replay_cost_orientation,
    selected_parent_order,
)


PARENT_HASHES = {
    "kerdock_v3_estimator.py": "076D0A5D81891DDCBB4509DC6E2BFF5459D935B5556490A85D98DAC60759AACF",
    "fold3_estimator.py": "68449E3EFE3B82A860B884A2BD05C9260E1EFBD138A343257CDC51AD38A63F6F",
    "row_blocked_winograd.py": "A3BF5C8014198E33037D6AEAFC3F4138A98908754BB82BFCF5ACDD92B1D9FCCA",
    "estimator.py": "5E7D52156B330BF63AC4FF0E0F38D864B32677F82BC8ED4D1382787A27D3E0C9",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class ParentAndRotationContracts(unittest.TestCase):
    def test_preexecution_manifest_binds_current_source_and_closed_scope(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "SOURCE_CONTRACT_SYNTHETIC_ONLY")
        self.assertEqual(
            manifest["files"]["source"]["sha256"],
            sha256(HERE / "dgfl1_source_contract.py"),
        )
        self.assertEqual(
            manifest["files"]["tests"]["sha256"],
            sha256(HERE / "test_dgfl1_source_contract.py"),
        )
        self.assertEqual(tuple(manifest["fixed_base_labels"]), DGFL_BASE_LABELS)
        self.assertFalse(manifest["authority"]["generated_network_execution"])
        self.assertFalse(manifest["authority"]["provider_execution"])

    def test_parent_hashes_and_overridable_q_call_sites(self) -> None:
        contract = ParentSourceContract(PARENT, PARENT_HASHES)
        report = contract.verify()
        self.assertEqual(report["parent_hashes"], PARENT_HASHES)
        self.assertEqual(report["production_q_calls"], 1)
        self.assertEqual(report["guard_q_calls"], 1)
        self.assertTrue(report["calls_through_self"])

        for name, expected in PARENT_HASHES.items():
            self.assertEqual(sha256(PARENT / name), expected)

    def test_rotation_capture_retains_first_object_and_rejects_drift(self) -> None:
        ledger = ProductionRotationCapture()
        ledger.begin("invocation-1")
        q1 = np.eye(4, dtype=np.float64)
        q2 = q1.copy()
        retained = ledger.observe(seed=17, width=4, rotation=q1)
        self.assertIs(retained, q1)
        self.assertIs(ledger.production_q, q1)
        self.assertEqual(ledger.calls, 1)

        ledger.observe(seed=17, width=4, rotation=q2)
        self.assertIs(ledger.production_q, q1)
        self.assertEqual(ledger.calls, 2)

        q_bad = q1.copy()
        q_bad[0, 0] = np.nextafter(q_bad[0, 0], 0.0)
        with self.assertRaisesRegex(RuntimeError, "byte drift"):
            ledger.observe(seed=17, width=4, rotation=q_bad)
        with self.assertRaisesRegex(RuntimeError, "seed or width drift"):
            ledger.observe(seed=18, width=4, rotation=q2)

    def test_rotation_state_is_cleared_between_worker_invocations(self) -> None:
        ledger = ProductionRotationCapture()
        ledger.begin("first")
        first = np.eye(3)
        ledger.observe(seed=1, width=3, rotation=first)
        summary = ledger.end()
        self.assertEqual(summary["calls"], 1)
        self.assertEqual(summary["seed"], 1)
        with self.assertRaisesRegex(RuntimeError, "has not been captured"):
            _ = ledger.production_q

        ledger.begin("second")
        second = np.fliplr(np.eye(3))
        ledger.observe(seed=2, width=3, rotation=second)
        self.assertIs(ledger.production_q, second)

    def test_real_pinned_haar_path_is_byte_repeatable_and_exactly_billed(self) -> None:
        import flopscope as flops
        from kerdock_v3_estimator import Estimator as KerdockV3

        budget = 1_000_000_000
        ledger = ProductionRotationCapture()
        ledger.begin("real-pinned-q")
        with flops.BudgetContext(budget, quiet=True) as first_ctx:
            first = KerdockV3._haar_rotation(190_711, 256)
        with flops.BudgetContext(budget, quiet=True) as second_ctx:
            second = KerdockV3._haar_rotation(190_711, 256)
        ledger.observe(seed=190_711, width=256, rotation=first)
        ledger.observe(seed=190_711, width=256, rotation=second)

        self.assertEqual(first.dtype, np.dtype(np.float64))
        self.assertEqual(int(first_ctx.flops_used), 45_921_196)
        self.assertEqual(int(second_ctx.flops_used), 45_921_196)
        self.assertEqual(first.tobytes(), second.tobytes())
        self.assertIs(ledger.production_q, first)

    def test_parent_sources_use_instance_dispatch_not_static_class_dispatch(self) -> None:
        for filename in ("kerdock_v3_estimator.py", "estimator.py"):
            tree = ast.parse((PARENT / filename).read_text(encoding="utf-8"))
            calls = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "_haar_rotation"
            ]
            self.assertEqual(len(calls), 1)
            self.assertIsInstance(calls[0].func.value, ast.Name)
            self.assertEqual(calls[0].func.value.id, "self")


class PostQStateMachineContracts(unittest.TestCase):
    def test_pre_q_reject_may_return_w0(self) -> None:
        gate = PostQReturnGate()
        gate.begin()
        self.assertEqual(gate.return_pre_q_w0("reserve_reject"), "w0")

    def test_every_complete_post_q_branch_requires_complete_correction(self) -> None:
        self.assertEqual(set(BASE_BRANCHES), {"healthy", "m186", "m187"})
        for branch in BASE_BRANCHES:
            with self.subTest(branch=branch):
                gate = PostQReturnGate()
                gate.begin()
                gate.capture_q()
                gate.accept_base(branch)
                with self.assertRaisesRegex(RuntimeError, "complete correction"):
                    gate.return_complete()
                gate.accept_complete_correction()
                self.assertEqual(gate.return_complete(), branch)

    def test_post_q_failure_cannot_silently_return_w0(self) -> None:
        gate = PostQReturnGate()
        gate.begin()
        gate.capture_q()
        with self.assertRaisesRegex(RuntimeError, "post-Q"):
            gate.return_pre_q_w0("child_failure")
        gate.provider_failure("child_failure")
        with self.assertRaisesRegex(RuntimeError, "provider failure"):
            gate.return_complete()


class SelectedRowAndCoordinateContracts(unittest.TestCase):
    def setUp(self) -> None:
        self.dimension = 8
        rng = np.random.default_rng(190_711)
        raw = rng.standard_normal((self.dimension, self.dimension))
        q, r = np.linalg.qr(raw)
        q = q * np.where(np.diag(r) < 0.0, -1.0, 1.0)[None, :]
        self.q = q
        self.phases = np.where(
            (np.arange(4)[:, None] + np.arange(self.dimension)[None, :]) % 3,
            1.0,
            -1.0,
        )
        hadamard = np.array([[1.0]])
        while hadamard.shape[0] < self.dimension:
            hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
        self.hadamard = hadamard / np.sqrt(self.dimension)

    def test_fixed_pairs_cover_each_selected_base_row_and_antipode_once(self) -> None:
        labels = (0, 3, 9, 17, 23)
        pairs = fixed_antipodal_pairs(labels, total_base_rows=32)
        self.assertEqual(pairs, ((0, 32), (3, 35), (9, 41), (17, 49), (23, 55)))
        flat = [item for pair in pairs for item in pair]
        self.assertEqual(len(flat), len(set(flat)))
        with self.assertRaises(ValueError):
            fixed_antipodal_pairs((0, 0), total_base_rows=32)
        with self.assertRaises(ValueError):
            fixed_antipodal_pairs((32,), total_base_rows=32)

    def test_manifest_subset_uses_32_distinct_mub_frames_and_parent_order(self) -> None:
        self.assertEqual(len(DGFL_BASE_LABELS), 32)
        frames = tuple(label // 256 for label in DGFL_BASE_LABELS)
        self.assertEqual(len(set(frames)), 32)
        self.assertEqual(tuple(sorted(DGFL_BASE_LABELS)), DGFL_BASE_LABELS)
        order = selected_parent_order(DGFL_BASE_LABELS, total_base_rows=126 * 256)
        self.assertEqual(order[:32], DGFL_BASE_LABELS)
        self.assertEqual(
            order[32:], tuple(label + 126 * 256 for label in DGFL_BASE_LABELS)
        )

        archive = np.load(PARENT / "kerdock_phases.npz")
        negative = np.unpackbits(
            archive["negative_bits"], axis=1, bitorder="little"
        )[:, :256]
        phases = (1.0 - 2.0 * negative.astype(np.float64))[2:128]
        hadamard = np.array([[1.0]], dtype=np.float64)
        while hadamard.shape[0] < 256:
            hadamard = np.block(
                [[hadamard, hadamard], [hadamard, -hadamard]]
            )
        hadamard /= 16.0
        unrotated = build_selected_unit_rows(
            hadamard, phases, np.eye(256), DGFL_BASE_LABELS
        )
        gram = unrotated @ unrotated.T
        off_diagonal = ~np.eye(32, dtype=bool)
        np.testing.assert_allclose(np.diag(gram), 1.0, rtol=0.0, atol=0.0)
        np.testing.assert_allclose(
            np.abs(gram[off_diagonal]), 1.0 / 16.0, rtol=0.0, atol=0.0
        )

    def test_selected_rows_match_frame_row_labels_and_are_unit(self) -> None:
        labels = (0, 9, 17, 31)
        rows = build_selected_unit_rows(self.hadamard, self.phases, self.q, labels)
        expected = []
        for label in labels:
            frame, row = divmod(label, self.dimension)
            expected.append((self.hadamard[row] * self.phases[frame]) @ self.q.T)
        np.testing.assert_allclose(rows, np.stack(expected), rtol=0.0, atol=2e-15)
        np.testing.assert_allclose(
            np.sum(rows * rows, axis=1), np.ones(len(labels)), rtol=0.0, atol=3e-15
        )

    def test_absorbed_generator_preserves_physical_primal_and_tangent_products(self) -> None:
        m = np.zeros(self.dimension)
        b = np.zeros(self.dimension)
        m[1] = 1.0
        b[6] = 1.0
        j_physical = rotation_generator(m, b)
        j_absorbed = absorbed_generator(self.q, j_physical)
        rng = np.random.default_rng(91_731)
        v = rng.standard_normal(self.dimension)
        w1 = rng.standard_normal((self.dimension, 5))

        physical_row = v @ self.q.T
        physical_tangent = physical_row @ j_physical.T
        absorbed_weight = self.q.T @ w1
        absorbed_tangent = v @ j_absorbed.T

        np.testing.assert_allclose(physical_row @ w1, v @ absorbed_weight, atol=2e-14)
        np.testing.assert_allclose(
            physical_tangent @ w1, absorbed_tangent @ absorbed_weight, atol=3e-14
        )
        np.testing.assert_allclose(j_absorbed + j_absorbed.T, 0.0, atol=2e-14)


class TypedCostBoundaryContracts(unittest.TestCase):
    def test_closed_component_subtotals_match_the_source_audit(self) -> None:
        mixed = replay_cost_orientation(
            replay_dtype="float32", trigonometry_dtype="float64"
        )
        all_f32 = replay_cost_orientation(
            replay_dtype="float32", trigonometry_dtype="float32"
        )
        all_f64 = replay_cost_orientation(
            replay_dtype="float64", trigonometry_dtype="float64"
        )
        self.assertEqual(mixed["subtotal"], 556_711_296)
        self.assertEqual(all_f32["subtotal"], 556_694_912)
        self.assertEqual(all_f64["subtotal"], 1_096_579_840)

    def test_open_items_fail_closed_for_generated_execution(self) -> None:
        report = replay_cost_orientation(
            replay_dtype="float32", trigonometry_dtype="float64"
        )
        self.assertFalse(report["complete_upper_bound"])
        self.assertFalse(report["authorizes_generated_execution"])
        self.assertIn("pilot_A_source_and_bill", report["unresolved"])
        self.assertIn("official_Phase2_meter_and_resource_rules", report["unresolved"])

    def test_dtype_labels_are_closed_world(self) -> None:
        with self.assertRaises(ValueError):
            replay_cost_orientation(
                replay_dtype="float16", trigonometry_dtype="float32"
            )
        with self.assertRaises(ValueError):
            replay_cost_orientation(
                replay_dtype="float32", trigonometry_dtype="platform_default"
            )


if __name__ == "__main__":
    unittest.main()
