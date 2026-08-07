"""Source-only operational tests for the M120C one-shot harness.

These tests never invoke the 27-job outcome grid or the fixed lifecycle root.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from unittest import mock
from pathlib import Path
import tempfile

import numpy as np
import m120c_protocol_harness as harness
import run_m120c_protocol as runner

from m120c_protocol_config import CONFIG
from m120c_protocol_harness import (
    AtomicLifecycle,
    BindingMetricRecord,
    CANONICAL_OUTCOME_PATH,
    CANONICAL_OUTCOME_ROOT,
    EXPECTED_SOURCE_KEYS,
    ProtocolFailClosed,
    binding_plan,
    closed_manifest_errors,
    evaluate_predeclared_gates,
    generated_weights,
    metric_records_for_generated_network,
    validate_operational_reparameterization,
    validate_permutation_matrix,
)


class M120COperationalHarnessTests(unittest.TestCase):
    @staticmethod
    def _complete_records() -> tuple[BindingMetricRecord, ...]:
        return tuple(
            BindingMetricRecord(
                width, depth, replica, layer, output, 0.04,
                np.array((-0.02, 0.01, -0.03, 0.04)),
            )
            for width in CONFIG.widths
            for depth in CONFIG.depths
            for replica in range(CONFIG.replicas_per_cell)
            for layer in range(depth - 1)
            for output in range(width)
        )

    def test_plan_exposes_exactly_twenty_seven_philox_jobs(self) -> None:
        plan = binding_plan()
        self.assertEqual(len(plan), 27)
        self.assertEqual(len({item["network_seed"] for item in plan}), 27)
        self.assertTrue(all(item["bit_generator"] == "Philox" for item in plan))

    def test_generated_weights_are_deterministic_philox_and_reject_nonplan_job(self) -> None:
        job = binding_plan()[0]
        first = generated_weights(job)
        second = generated_weights(job)
        self.assertEqual(len(first), job["depth"])
        self.assertTrue(all(np.array_equal(a, b) for a, b in zip(first, second)))
        bad = dict(job)
        bad["network_seed"] = int(job["network_seed"]) + 1
        with self.assertRaises(ProtocolFailClosed):
            generated_weights(bad)

    def test_one_network_uses_analytic_dense_reference_and_emits_all_layer_output_rows(self) -> None:
        job = binding_plan()[0]
        records = metric_records_for_generated_network(job)
        self.assertEqual(len(records), (job["depth"] - 1) * job["width"])
        self.assertTrue(all(record.reference_norm > CONFIG.fail_closed_floor for record in records))
        self.assertTrue(all(len(record.signed_directional_errors) == 4 for record in records))

    def test_permutation_validation_rejects_non_permutation(self) -> None:
        self.assertEqual(validate_permutation_matrix(np.eye(3)).shape, (3, 3))
        with self.assertRaises(ProtocolFailClosed):
            validate_permutation_matrix(np.array(((1.0, 1.0), (0.0, 0.0))))

    def test_actual_dense_cp_reverses_preserve_metrics_under_frozen_permutation_and_gauge(self) -> None:
        validate_operational_reparameterization(binding_plan()[0])

    def test_temporary_lifecycle_consumes_claim_and_forbids_retry_without_touching_canonical_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            lifecycle.claim({"state": "claimed"})
            with self.assertRaises(ProtocolFailClosed):
                lifecycle.claim({"state": "claimed-again"})

    def test_gate_payload_has_deterministic_json_safe_cell_keys(self) -> None:
        gates = evaluate_predeclared_gates(self._complete_records())
        serialized = json.dumps(gates, sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads(serialized), gates)
        expected = [f"w{width}_d{depth}" for width in CONFIG.widths for depth in CONFIG.depths]
        self.assertEqual(list(gates["cell_worst_complete_error"]), expected)
        self.assertEqual(list(gates["cell_worst_absolute_directional_error"]), expected)

    def test_config_lifecycle_and_runner_share_one_exact_canonical_outcome_path(self) -> None:
        self.assertEqual(Path(CONFIG.output_path), CANONICAL_OUTCOME_PATH)
        self.assertEqual(CANONICAL_OUTCOME_PATH.parent, CANONICAL_OUTCOME_ROOT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            self.assertEqual(lifecycle.outcome_path.name, CANONICAL_OUTCOME_PATH.name)

    def test_atomic_publication_has_one_outcome_and_hash_bound_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            lifecycle.claim({"state": "claimed"})
            outcome = lifecycle.publish_outcome({"pass": True}, "pass")
            self.assertEqual(outcome.name, CANONICAL_OUTCOME_PATH.name)
            self.assertEqual(sorted(path.name for path in lifecycle.root.iterdir()), [
                "M120C_CLAIM.json", "M120C_TERMINAL.json", CANONICAL_OUTCOME_PATH.name,
            ])
            terminal = json.loads(lifecycle.terminal_path.read_text(encoding="utf-8"))
            self.assertEqual(terminal["status"], "pass")
            self.assertEqual(terminal["outcome_sha256"], hashlib.sha256(outcome.read_bytes()).hexdigest())

    def test_injected_partial_publication_is_permanently_fail_closed_without_second_outcome(self) -> None:
        for stage in ("after_outcome_pending", "after_terminal_pending", "after_outcome_replace"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temporary_directory:
                def inject(observed: str) -> None:
                    if observed == stage:
                        raise RuntimeError("injected interruption")

                lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated", fault_injector=inject)
                lifecycle.claim({"state": "claimed"})
                with self.assertRaisesRegex(RuntimeError, "injected interruption"):
                    lifecycle.publish_outcome({"pass": True}, "pass")
                with self.assertRaises(ProtocolFailClosed):
                    lifecycle.publish_outcome({"pass": False}, "error")
                with self.assertRaises(ProtocolFailClosed):
                    lifecycle.claim({"state": "retry"})
                names = {path.name for path in lifecycle.root.iterdir()}
                self.assertNotIn("M120C_RESULT.json", names)
                self.assertNotIn("M120C_FAILURE.json", names)
                self.assertLessEqual(sum(name == CANONICAL_OUTCOME_PATH.name for name in names), 1)

    def test_runner_publication_interruption_never_attempts_a_failure_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def inject(stage: str) -> None:
                if stage == "after_outcome_replace":
                    raise RuntimeError("injected publication interruption")

            lifecycle = AtomicLifecycle(
                Path(temporary_directory) / "isolated",
                fault_injector=inject,
            )
            with (
                mock.patch.object(runner, "CANONICAL_OUTCOME_ROOT", lifecycle.root),
                mock.patch.object(runner, "AtomicLifecycle", return_value=lifecycle),
                mock.patch.object(runner, "closed_manifest_errors", return_value=()),
                mock.patch.object(runner, "all_generated_metric_records", return_value=()),
                mock.patch.object(runner, "evaluate_predeclared_gates", return_value={"pass": True}),
            ):
                with self.assertRaisesRegex(RuntimeError, "publication interruption"):
                    runner.run_authorized_m120c_grid("0" * 64)
            names = {path.name for path in lifecycle.root.iterdir()}
            self.assertIn(CANONICAL_OUTCOME_PATH.name, names)
            self.assertNotIn("M120C_RESULT.json", names)
            self.assertNotIn("M120C_FAILURE.json", names)

    def test_runner_computation_failure_publishes_one_error_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            with (
                mock.patch.object(runner, "CANONICAL_OUTCOME_ROOT", lifecycle.root),
                mock.patch.object(runner, "AtomicLifecycle", return_value=lifecycle),
                mock.patch.object(runner, "closed_manifest_errors", return_value=()),
                mock.patch.object(runner, "all_generated_metric_records", side_effect=ValueError("injected compute failure")),
            ):
                with self.assertRaisesRegex(ValueError, "compute failure"):
                    runner.run_authorized_m120c_grid("0" * 64)
            outcome = json.loads(lifecycle.outcome_path.read_text(encoding="utf-8"))
            terminal = json.loads(lifecycle.terminal_path.read_text(encoding="utf-8"))
            self.assertFalse(outcome["pass"])
            self.assertEqual(terminal["status"], "error")
            self.assertEqual(
                sorted(path.name for path in lifecycle.root.iterdir()),
                ["M120C_CLAIM.json", "M120C_TERMINAL.json", CANONICAL_OUTCOME_PATH.name],
            )

    def test_short_writes_persist_large_claim_outcome_and_terminal_exactly(self) -> None:
        real_write = harness.os.write
        write_calls = 0

        def short_write(descriptor: int, remaining: memoryview) -> int:
            nonlocal write_calls
            write_calls += 1
            count = min(len(remaining), 8191)
            return real_write(descriptor, remaining[:count])

        claim_payload = {"state": "claimed", "padding": "c" * (1024 * 1024)}
        outcome_payload = {"pass": True, "records": "o" * (2 * 1024 * 1024)}
        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            with mock.patch.object(harness.os, "write", side_effect=short_write):
                lifecycle.claim(claim_payload)
                outcome = lifecycle.publish_outcome(outcome_payload, "pass")
            self.assertGreater(write_calls, 300)
            self.assertEqual(lifecycle.claim_path.read_bytes(), lifecycle._canonical_bytes(claim_payload))
            self.assertEqual(outcome.read_bytes(), lifecycle._canonical_bytes(outcome_payload))
            terminal = json.loads(lifecycle.terminal_path.read_text(encoding="utf-8"))
            self.assertEqual(terminal["outcome_sha256"], hashlib.sha256(outcome.read_bytes()).hexdigest())

    def test_interrupted_writes_retry_without_advancing_for_claim_outcome_and_terminal(self) -> None:
        real_write = harness.os.write
        interrupt_next = True
        interruption_count = 0

        def interrupted_once_per_file(descriptor: int, remaining: memoryview) -> int:
            nonlocal interrupt_next, interruption_count
            if interrupt_next:
                interrupt_next = False
                interruption_count += 1
                raise InterruptedError("injected EINTR")
            interrupt_next = True
            return real_write(descriptor, remaining)

        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            with mock.patch.object(harness.os, "write", side_effect=interrupted_once_per_file):
                lifecycle.claim({"state": "claimed"})
                lifecycle.publish_outcome({"pass": True}, "pass")
            self.assertEqual(interruption_count, 3)
            self.assertEqual(json.loads(lifecycle.claim_path.read_text(encoding="utf-8"))["state"], "claimed")
            self.assertTrue(json.loads(lifecycle.outcome_path.read_text(encoding="utf-8"))["pass"])
            self.assertEqual(json.loads(lifecycle.terminal_path.read_text(encoding="utf-8"))["status"], "pass")

    def test_zero_writes_fail_before_fsync_at_claim_outcome_and_terminal(self) -> None:
        for stage in ("claim", "outcome", "terminal"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temporary_directory:
                lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
                if stage != "claim":
                    lifecycle.claim({"state": "claimed"})
                real_write = harness.os.write
                calls = 0

                def zero_at_stage(descriptor: int, remaining: memoryview) -> int:
                    nonlocal calls
                    calls += 1
                    if stage == "terminal" and calls == 1:
                        return real_write(descriptor, remaining)
                    return 0

                with (
                    mock.patch.object(harness.os, "write", side_effect=zero_at_stage),
                    mock.patch.object(harness.os, "fsync", wraps=harness.os.fsync) as fsync,
                ):
                    with self.assertRaises(ProtocolFailClosed):
                        if stage == "claim":
                            lifecycle.claim({"state": "claimed"})
                        else:
                            lifecycle.publish_outcome({"pass": True}, "pass")
                self.assertEqual(fsync.call_count, 1 if stage == "terminal" else 0)

    def test_oversize_write_count_is_rejected_before_fsync(self) -> None:
        def impossible_count(_descriptor: int, remaining: memoryview) -> int:
            return len(remaining) + 1

        with tempfile.TemporaryDirectory() as temporary_directory:
            lifecycle = AtomicLifecycle(Path(temporary_directory) / "isolated")
            with (
                mock.patch.object(harness.os, "write", side_effect=impossible_count),
                mock.patch.object(harness.os, "fsync", wraps=harness.os.fsync) as fsync,
            ):
                with self.assertRaises(ProtocolFailClosed):
                    lifecycle.claim({"state": "claimed"})
            fsync.assert_not_called()

    def test_closed_manifest_rejects_omitted_binding_and_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text('{"schema": 1, "source_sha256": {}}', encoding="utf-8")
            errors = closed_manifest_errors(manifest, "0" * 64)
        self.assertTrue(errors)
        self.assertTrue(any("source" in error or "runtime" in error for error in errors))

    def test_manifest_hash_and_parse_use_one_identical_byte_read(self) -> None:
        raw = b'{"schema":1,"source_sha256":{}}'

        class OneReadManifest:
            def __init__(self) -> None:
                self.calls = 0

            def read_bytes(self) -> bytes:
                self.calls += 1
                if self.calls > 1:
                    raise AssertionError("manifest was read more than once")
                return raw

        manifest = OneReadManifest()
        errors = closed_manifest_errors(manifest, hashlib.sha256(raw).hexdigest())
        self.assertEqual(manifest.calls, 1)
        self.assertNotIn("external manifest hash mismatch", errors)

    def test_manifest_source_closure_includes_executed_transitive_local_imports(self) -> None:
        self.assertIn("scorefloor_generation/fullcov_gaussian_mm/fullcov.py", EXPECTED_SOURCE_KEYS)
        self.assertIn("scorefloor_generation/adjoint_cumulant/adjoint_born.py", EXPECTED_SOURCE_KEYS)


if __name__ == "__main__":
    unittest.main()
