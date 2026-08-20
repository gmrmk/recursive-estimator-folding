"""Hostile, response-free gates for the frozen M200 streaming fixture."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for directory in (
    HERE,
    EXPERIMENTS / "m125_source_batched_forward_tangent",
    EXPERIMENTS / "m167_collision_owner_unification",
    EXPERIMENTS / "m172_selective_22_owner_fusion",
    EXPERIMENTS / "m178_certified_phi2_owent",
    EXPERIMENTS / "m179_background_archive_producer",
    EXPERIMENTS / "m198_source211_delay_one_adapter",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import m198_source211_delay_one_adapter as m198  # noqa: E402
import m179_jacobian_archive as m179_archive  # noqa: E402
import m200_streaming_overlap as m200  # noqa: E402


def _small_nonfrozen_weights() -> tuple[np.ndarray, ...]:
    """Width eight keeps unit tests outside the frozen 2..7 evaluation grid."""

    return m200.generated_weights(8, 4, 200_888_003)  # H=3 plus terminal


class M200StreamingOverlapTests(unittest.TestCase):
    def _first_two_bound_layers(self):
        weights = _small_nonfrozen_weights()
        trace = m200._weight_trace_digest(weights)
        network = m200._network_digest(trace)
        mu0 = np.zeros(8, dtype=np.float64)
        v0 = np.eye(8, dtype=np.float64)
        entry1 = m200._m179_stream_step(
            mu0, v0, weights[0], layer=1, network_digest=network, weight_trace_digest=trace
        )
        bound1 = m200.bind_archive_layer(entry1, mu0, v0, weights[0], generation=1)
        entry2 = m200._m179_stream_step(
            entry1.mu, entry1.V, weights[1], layer=2,
            network_digest=network, weight_trace_digest=trace,
        )
        bound2 = m200.bind_archive_layer(
            entry2, entry1.mu, entry1.V, weights[1], generation=2
        )
        return weights, bound1, bound2

    def test_stream_forbids_archive_and_carrier_helpers(self):
        weights = _small_nonfrozen_weights()

        def forbidden(*_args, **_kwargs):
            raise AssertionError("forbidden non-streaming helper was called")

        with (
            patch.object(m198, "build_extended_background", forbidden),
            patch.object(m179_archive, "build_archive", forbidden),
            patch.object(m198, "build_labelled_carrier_maps", forbidden),
            patch.object(m198, "labelled_explicit_source_superposition", forbidden),
            patch.object(m198, "labelled_inhomogeneous_source_recurrence", forbidden),
        ):
            result = m200.run_streaming_overlap(weights, network_seed=200_888_003)
        self.assertEqual(result.background_rebuilds_inside_stream, 0)
        self.assertEqual(result.background_steps, 3)
        self.assertEqual(result.transports, 2)
        self.assertEqual(result.terminal_responses, 1)

    def test_packet_rejects_cross_layer_duplicate_and_terminal_reinjection(self):
        _weights, bound1, bound2 = self._first_two_bound_layers()
        packet = m200.fixture_source_bound_to(bound1, m200.FixtureSpec(9182, 1))
        with self.assertRaises(ValueError):
            m200.validate_packet_binding(packet, bound2)
        guard = m200.StreamInjectionGuard()
        guard.consume(packet, bound1)
        with self.assertRaises(ValueError):
            guard.consume(packet, bound1)
        guard.seal_terminal()
        with self.assertRaises(ValueError):
            guard.consume(packet, bound1)

    def test_integrated_issuer_rejects_w_vprev_laundering(self):
        weights, bound1, _bound2 = self._first_two_bound_layers()
        packet = m200.fixture_source_bound_to(bound1, m200.FixtureSpec(9183, 1))
        # This deliberately issues a mathematically valid M172 source under the
        # same M179 context but with different W/Vprev. The integrated M200
        # source-issuance receipt must reject wrapper-level relabelling.
        wrong_weight = weights[0].copy()
        wrong_weight[0, 0] += 0.125
        wrong_vprev = bound1.upstream_covariance.copy()
        wrong_vprev[0, 0] += 0.25
        laundered_source = m200._fixture_source(
            bound1.entry, wrong_weight, wrong_vprev, m200.FixtureSpec(9183, 1)
        )
        with self.assertRaises(ValueError):
            replace(packet, source=laundered_source)

    def test_equal_value_copies_and_wrong_covariance_spaces_are_rejected(self):
        _weights, bound1, _bound2 = self._first_two_bound_layers()
        packet = m200.fixture_source_bound_to(bound1, m200.FixtureSpec(9184, 1))
        copied_weight = bound1.weight.copy()
        copied_vprev = bound1.upstream_covariance.copy()
        copied_bound = m200.bind_archive_layer(
            bound1.entry, bound1.upstream_mu.copy(), copied_vprev, copied_weight, generation=1
        )
        with self.assertRaises(ValueError):
            m200.validate_packet_binding(packet, copied_bound)
        # C_k and V_k are mathematically different covariance spaces; neither
        # can replace upstream V_(k-1) in a causal M172 bound layer.
        with self.assertRaises(ValueError):
            m200.bind_archive_layer(
                bound1.entry, bound1.upstream_mu, bound1.entry.pre_covariance,
                bound1.weight, generation=1,
            )
        with self.assertRaises(ValueError):
            m200.bind_archive_layer(
                bound1.entry, bound1.upstream_mu, bound1.entry.V,
                bound1.weight, generation=1,
            )
        with self.assertRaises(ValueError):
            replace(packet, pre_mean_object=packet.pre_mean_object.copy())
        with self.assertRaises(ValueError):
            replace(packet, pre_covariance_object=packet.pre_covariance_object.copy())
        with self.assertRaises(ValueError):
            replace(packet, post_mean_object=packet.post_mean_object.copy())

    def test_post_issue_weight_mutation_fails_closed(self):
        _weights, bound1, _bound2 = self._first_two_bound_layers()
        packet = m200.fixture_source_bound_to(bound1, m200.FixtureSpec(9185, 1))
        original = float(bound1.weight[0, 0])
        try:
            bound1.weight[0, 0] = original + 0.125
            with self.assertRaises(ValueError):
                m200.validate_packet_binding(packet, bound1)
        finally:
            bound1.weight[0, 0] = original

    def test_post_issue_upstream_covariance_mutation_fails_closed(self):
        _weights, bound1, _bound2 = self._first_two_bound_layers()
        packet = m200.fixture_source_bound_to(bound1, m200.FixtureSpec(9186, 1))
        original = float(bound1.upstream_covariance[0, 0])
        try:
            bound1.upstream_covariance[0, 0] = original + 0.125
            with self.assertRaises(ValueError):
                m200.validate_packet_binding(packet, bound1)
        finally:
            bound1.upstream_covariance[0, 0] = original

    def test_float32_input_rejected_without_implicit_cast(self):
        weights = tuple(value.astype(np.float32) for value in _small_nonfrozen_weights())
        with self.assertRaises(ValueError):
            m200.run_streaming_overlap(weights, network_seed=200_888_003)

    def test_transport_boundary_and_truthful_cross_iteration_liveness(self):
        weights = _small_nonfrozen_weights()
        result = m200.run_streaming_overlap(weights, network_seed=200_888_003)
        self.assertEqual(len(result.transport_call_log), 2)
        transport_events = [
            event for event in result.event_ledger
            if event.operation == "m125b.transport.current_m179_jacobian"
            and event.logical_buffer_id.endswith("transport_mean")
        ]
        self.assertEqual(len(transport_events), 2)
        for (weight_id, jacobian_id, layer), event in zip(result.transport_call_log, transport_events):
            self.assertEqual(layer, event.metadata["emitting_layer"])
            self.assertEqual(weight_id, event.metadata["weight_object_id"])
            self.assertEqual(jacobian_id, event.metadata["jacobian_object_id"])
        by_id = {event.logical_buffer_id: event for event in result.event_ledger}
        # l1 post-state survives until l2 is complete; it is never released in
        # l1 and then silently reused as an untracked previous background.
        self.assertGreater(
            by_id["l1.post_mean"].death_order,
            by_id["l2.pre_mean"].birth_order,
        )
        self.assertGreater(
            by_id["l1.post_covariance"].death_order,
            by_id["l2.pre_covariance"].birth_order,
        )
        self.assertTrue(result.conversion_copy_integrity_pass)
        self.assertTrue(result.transport_jacobian_identity_pass)

    def test_transport_spy_observes_current_weight_and_jacobian_objects(self):
        import m125_forward_tangent as m125

        weights = _small_nonfrozen_weights()
        seen: list[tuple[int, int]] = []

        def spy(state, weight, jacobian):
            seen.append((id(weight), id(jacobian)))
            return m125.tangent_stage(state, weight, jacobian)

        with patch.object(m200, "tangent_stage", spy):
            result = m200.run_streaming_overlap(weights, network_seed=200_888_003)
        self.assertEqual([weight_id for weight_id, _ in seen], [id(w) for w in weights[1:]])
        self.assertEqual(len(seen), 3)  # H-1 internal transports plus terminal
        internal_jacobians = [jacobian_id for _, jacobian_id, _ in result.transport_call_log]
        self.assertEqual([jacobian_id for _, jacobian_id in seen[:-1]], internal_jacobians)
        terminal_event = next(
            event for event in result.event_ledger
            if event.operation == "m200.terminal_w_h_plus_1_response"
            and event.logical_buffer_id == "terminal.response_mean"
        )
        self.assertEqual(seen[-1][1], terminal_event.metadata["jacobian_object_id"])

    def test_nonfrozen_full_archive_manual_suffix_parity(self):
        weights = _small_nonfrozen_weights()
        streamed = m200.run_streaming_overlap(weights, network_seed=200_888_003)
        reference = m200.full_archive_reference(weights, network_seed=200_888_003)
        maximum = max(
            float(np.max(np.abs(streamed.source_terminal_state.mean - reference.source_terminal_state.mean))),
            float(np.max(np.abs(streamed.source_terminal_state.covariance - reference.source_terminal_state.covariance))),
            float(np.max(np.abs(streamed.terminal_state.mean - reference.terminal_state.mean))),
            float(np.max(np.abs(streamed.terminal_state.covariance - reference.terminal_state.covariance))),
        )
        self.assertLessEqual(maximum, m200.PARITY_MAX_ABS)
        self.assertLessEqual(reference.per_layer_impulse_max_abs, m200.PARITY_MAX_ABS)

    def test_frozen_artifacts_match_scope_and_hashed_contract(self):
        manifest = json.loads(
            (HERE / "M200_FROZEN_MANIFEST_20260809.json").read_text(encoding="utf-8")
        )
        for filename_key, digest_key in (
            ("predeclaration", "predeclaration_sha256"),
            ("index_erratum", "index_erratum_sha256"),
        ):
            actual = hashlib.sha256((HERE / manifest[filename_key]).read_bytes()).hexdigest()
            self.assertEqual(actual, manifest[digest_key])

        results = json.loads(
            (HERE / "M200_RESULTS_20260809.json").read_text(encoding="utf-8")
        )
        ledger = json.loads(
            (HERE / "M200_EVENT_LIVENESS_LEDGER_20260809.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            results["status"], "STREAMING_SEMANTIC_PASS_NATIVE_COST_BLOCKED"
        )
        self.assertEqual(results["case_count"], 48)
        self.assertLessEqual(results["max_abs_error"], results["parity_max_abs_threshold"])
        self.assertEqual(results["per_layer_impulse_max_abs"], 0.0)
        self.assertEqual(results["fixture_provider_cost"], "UNKNOWN")
        self.assertEqual(results["native_target_cost"], "NOT_MEASURED")
        self.assertEqual(ledger["case_count"], 48)
        self.assertEqual(ledger["count_ranges"]["terminal_responses"], [1, 1])
        self.assertEqual(
            ledger["count_ranges"]["background_rebuilds_inside_stream"], [0, 0]
        )
        self.assertTrue(ledger["all_final_retained_counts_zero"])


if __name__ == "__main__":
    unittest.main()
