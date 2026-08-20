"""Pre-execution contracts for the frozen M120C component falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from m120c_protocol_config import CONFIG, network_seed
from m120c_protocol_harness import (
    BindingMetricRecord,
    ProtocolFailClosed,
    binding_plan,
    closed_manifest_errors,
    evaluate_predeclared_gates,
    manifest_errors,
    predeclared_signed_directions,
    runtime_identity,
    standardized_complete_error,
    standardized_state,
    simultaneous_hidden_reparameterization,
    transport_directions_for_permutation,
)
from run_m120c_protocol import freeze_ready_description


class M120CProtocolTests(unittest.TestCase):
    @staticmethod
    def _complete_metric_records(error: float) -> tuple[BindingMetricRecord, ...]:
        records = []
        for width in CONFIG.widths:
            for depth in CONFIG.depths:
                for replica in range(CONFIG.replicas_per_cell):
                    for layer in range(depth - 1):
                        for output in range(width):
                            records.append(
                                BindingMetricRecord(
                                    width=width,
                                    depth=depth,
                                    replica=replica,
                                    layer=layer,
                                    output=output,
                                    complete_error=error,
                                    signed_directional_errors=np.array(
                                        (-0.5 * error, 0.25 * error, -0.75 * error, error)
                                    ),
                                )
                            )
        return tuple(records)

    def test_frozen_plan_is_exactly_27_philox_networks_with_prospective_numeric_seeds(self) -> None:
        self.assertEqual(CONFIG.widths, (8, 12, 16))
        self.assertEqual(CONFIG.depths, (2, 3, 4))
        self.assertEqual(CONFIG.replicas_per_cell, 3)
        self.assertEqual(CONFIG.network_bit_generator, "Philox")
        self.assertEqual(network_seed(8, 2, 0), 2_026_882_700)
        self.assertEqual(network_seed(16, 4, 2), 2_027_684_702)

        plan = binding_plan()
        self.assertEqual(len(plan), 27)
        self.assertEqual({entry["width"] for entry in plan}, {8, 12, 16})
        self.assertEqual({entry["depth"] for entry in plan}, {2, 3, 4})
        self.assertTrue(all(entry["bit_generator"] == "Philox" for entry in plan))
        self.assertTrue(all(entry["terminal_outputs"] == list(range(entry["width"])) for entry in plan))

    def test_standardized_complete_adjoint_and_directions_are_gauge_permutation_invariant(self) -> None:
        rng = np.random.default_rng(120_601)
        width = 8
        factor = rng.normal(size=(width, width))
        covariance = factor @ factor.T + np.eye(width)
        reference_b = rng.normal(size=width)
        reference_a = rng.normal(size=(width, width))
        reference_a = 0.5 * (reference_a + reference_a.T)
        approximation_b = reference_b + 0.02 * rng.normal(size=width)
        approximation_a = reference_a + 0.02 * rng.normal(size=(width, width))
        approximation_a = 0.5 * (approximation_a + approximation_a.T)
        permutation = np.eye(width)[:, (2, 0, 7, 1, 6, 4, 3, 5)]
        gauge = np.diag((1.7, 0.8, 1.2, 1.05, 0.9, 1.3, 0.75, 1.1))
        transform = permutation @ gauge
        inverse = np.linalg.inv(transform)

        baseline_state = standardized_state(reference_b, reference_a, covariance)
        baseline = standardized_complete_error(
            reference_b, reference_a, approximation_b, approximation_a, covariance
        )
        directions = predeclared_signed_directions(8, 2, 0)
        baseline_directional = baseline.signed_directional_errors(directions)

        transformed_covariance = transform.T @ covariance @ transform
        transformed_reference_b = inverse @ reference_b
        transformed_approximation_b = inverse @ approximation_b
        transformed_reference_a = inverse @ reference_a @ inverse.T
        transformed_approximation_a = inverse @ approximation_a @ inverse.T
        transformed_state = standardized_state(
            transformed_reference_b, transformed_reference_a, transformed_covariance
        )
        transformed = standardized_complete_error(
            transformed_reference_b,
            transformed_reference_a,
            transformed_approximation_b,
            transformed_approximation_a,
            transformed_covariance,
        )
        transformed_directions = transport_directions_for_permutation(directions, permutation)

        self.assertLess(np.linalg.norm(transformed_state.mean - permutation.T @ baseline_state.mean), 1e-12)
        self.assertLess(
            np.linalg.norm(
                transformed_state.covariance
                - permutation.T @ baseline_state.covariance @ permutation
            ),
            1e-12,
        )
        self.assertLess(abs(transformed.relative_error - baseline.relative_error), 1e-12)
        self.assertLess(
            np.linalg.norm(
                transformed.signed_directional_errors(transformed_directions)
                - baseline_directional
            ),
            1e-12,
        )

    def test_zero_and_near_zero_variance_or_reference_norm_fail_closed_at_one_e_minus_ten(self) -> None:
        b = np.array((1.0, -2.0))
        a = np.eye(2)
        for bad_variance in (0.0, 1e-12, 1e-10):
            with self.subTest(bad_variance=bad_variance):
                with self.assertRaises(ProtocolFailClosed):
                    standardized_state(b, a, np.diag((bad_variance, 1.0)))

        with self.assertRaises(ProtocolFailClosed):
            standardized_complete_error(
                np.zeros(2), np.zeros((2, 2)), np.zeros(2), np.zeros((2, 2)), np.eye(2)
            )

    def test_independent_direction_namespace_is_closed_and_old_preexec_manifest_is_not_a_release(self) -> None:
        first = predeclared_signed_directions(12, 3, 1)
        second = predeclared_signed_directions(12, 3, 1)
        self.assertEqual(len(first), CONFIG.direction_count)
        self.assertTrue(all(np.array_equal(x.mean, y.mean) for x, y in zip(first, second)))
        self.assertTrue(all(np.array_equal(x.covariance, y.covariance) for x, y in zip(first, second)))
        self.assertEqual(CONFIG.direction_bit_generator, "Philox")
        self.assertNotEqual(CONFIG.direction_root_seed, CONFIG.network_root_seed)

        sealed_manifest_path = Path(CONFIG.manifest_path)
        preexec_manifest_path = sealed_manifest_path.with_name(
            "m120c_protocol_manifest_preexec_61968d9818b398dd.json"
        )
        preexec_digest = hashlib.sha256(preexec_manifest_path.read_bytes()).hexdigest()
        self.assertTrue(closed_manifest_errors(preexec_manifest_path, preexec_digest))

        sealed_manifest_bytes = sealed_manifest_path.read_bytes()
        sealed_manifest = json.loads(sealed_manifest_bytes.decode("utf-8"))
        sealed_errors = closed_manifest_errors(
            sealed_manifest_path, hashlib.sha256(sealed_manifest_bytes).hexdigest()
        )
        if sealed_manifest["runtime_identity"] == runtime_identity():
            self.assertEqual(sealed_errors, ())
        else:
            self.assertEqual(sealed_errors, ("runtime identity mismatch",))

    def test_named_runner_is_non_cli_and_awaits_an_external_operational_manifest(self) -> None:
        description = freeze_ready_description()
        self.assertEqual(description["execution_mode"], "OPERATIONAL_AWAITING_EXTERNAL_MANIFEST")
        self.assertEqual(description["jobs"], 27)
        self.assertEqual(description["expected_records"], 648)
        self.assertEqual(description["fixed_output_path"], CONFIG.output_path)
        self.assertTrue(description["manifest_required_externally"])

    def test_manifest_rejects_grid_or_gate_drift_from_the_hashed_config(self) -> None:
        payload = json.loads(Path(CONFIG.manifest_path).read_text(encoding="utf-8"))
        payload["binding_grid"]["widths"] = [8]
        with tempfile.TemporaryDirectory() as temporary_directory:
            altered = Path(temporary_directory) / "altered_manifest.json"
            altered.write_text(json.dumps(payload), encoding="utf-8")
            self.assertIn("binding grid mismatch", manifest_errors(altered))

    def test_global_and_every_cell_gates_use_all_predeclared_records_and_signed_directions(self) -> None:
        passing = evaluate_predeclared_gates(self._complete_metric_records(0.04))
        self.assertTrue(passing["pass"])
        self.assertEqual(passing["record_count"], 648)
        self.assertAlmostEqual(passing["global_mean_complete_error"], 0.04)
        self.assertAlmostEqual(passing["global_mean_absolute_directional_error"], 0.025)

        failing_records = list(self._complete_metric_records(0.04))
        failing_records[-1] = BindingMetricRecord(
            **{
                **failing_records[-1].__dict__,
                "complete_error": 0.1000000001,
            }
        )
        failing = evaluate_predeclared_gates(tuple(failing_records))
        self.assertFalse(failing["pass"])
        self.assertGreater(failing["cell_worst_complete_error"]["w16_d4"], 0.10)

    def test_simultaneous_hidden_permutations_and_positive_gauges_preserve_relu_chain(self) -> None:
        rng = np.random.Generator(np.random.Philox(2_026_199_001))
        width, depth = 8, 4
        weights = tuple(rng.normal(size=(width, width)) for _ in range(depth))
        permutations = (
            np.eye(width)[:, (2, 0, 7, 1, 6, 4, 3, 5)],
            np.eye(width)[:, (1, 6, 4, 0, 7, 3, 5, 2)],
            np.eye(width)[:, (5, 2, 6, 1, 0, 7, 4, 3)],
        )
        gauges = (
            np.array((1.2, 0.8, 1.1, 0.9, 1.3, 0.7, 1.05, 1.15)),
            np.array((0.75, 1.25, 0.95, 1.1, 0.85, 1.2, 0.9, 1.05)),
            np.array((1.1, 0.9, 1.3, 0.8, 1.15, 0.7, 1.05, 1.2)),
        )
        transformed = simultaneous_hidden_reparameterization(weights, permutations, gauges)

        inputs = rng.normal(size=(6, width))
        def evaluate(raw_weights: tuple[np.ndarray, ...]) -> np.ndarray:
            state = inputs
            for weight in raw_weights[:-1]:
                state = np.maximum(0.0, state @ weight)
            return state @ raw_weights[-1]

        self.assertLess(np.linalg.norm(evaluate(weights) - evaluate(transformed)), 1e-11)


if __name__ == "__main__":
    unittest.main()
