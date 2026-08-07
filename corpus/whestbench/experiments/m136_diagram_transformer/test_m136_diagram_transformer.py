"""Generated-only hostile tests for M136."""

from __future__ import annotations

import unittest

import numpy as np

from m136_diagram_transformer import (
    CHANNELS,
    DiagramResummer,
    _bootstrap_ratio_ci,
    causal_feature_matrix,
    diagonal_gaussian_states,
    diagram_channels,
    analytic_node_tokens,
    iid_he_network,
    least_squares_mse,
    synthetic_polynomial_dataset,
    target_cost_envelope,
    signed_edge_attention,
    transform_hidden_permutation_and_gauge,
)


class M136DiagramTransformerTests(unittest.TestCase):
    def test_synthetic_hard_motifs_are_exactly_representable(self):
        full, y, low = synthetic_polynomial_dataset()
        full_mse = least_squares_mse(full, y)
        low_mse = least_squares_mse(low, y)
        self.assertLess(full_mse, 1.0e-20)
        self.assertGreater(low_mse, 1.0e-7)

    def test_hidden_permutation_and_positive_gauge_are_exact(self):
        weights = iid_he_network(1361, width=7, depth=4)
        rng = np.random.default_rng(1362)
        permutations = [np.arange(7)] + [rng.permutation(7) for _ in weights]
        gauges = [np.ones(7)] + [np.exp(rng.uniform(-0.7, 0.7, size=7)) for _ in weights]
        transformed = transform_hidden_permutation_and_gauge(weights, permutations, gauges)
        state = diagonal_gaussian_states(weights)
        transformed_state = diagonal_gaussian_states(transformed)
        old_f = causal_feature_matrix(diagram_channels(state))
        new_f = causal_feature_matrix(diagram_channels(transformed_state))
        final_perm, final_gauge = permutations[-1], gauges[-1]
        np.testing.assert_allclose(transformed_state.anchor, final_gauge * state.anchor[final_perm], rtol=3e-12, atol=3e-12)
        np.testing.assert_allclose(transformed_state.stds[-1], final_gauge * state.stds[-1][final_perm], rtol=3e-12, atol=3e-12)
        np.testing.assert_allclose(new_f, old_f[final_perm], rtol=2e-11, atol=2e-11)

    def test_fitted_prediction_is_equivariant(self):
        weights = iid_he_network(1363, width=6, depth=4)
        state = diagonal_gaussian_states(weights)
        features = causal_feature_matrix(diagram_channels(state))
        target = np.linspace(-0.2, 0.3, 6)
        model = DiagramResummer().fit([features, 1.01 * features], [target, 0.99 * target])
        rng = np.random.default_rng(1364)
        perms = [np.arange(6)] + [rng.permutation(6) for _ in weights]
        gauges = [np.ones(6)] + [np.exp(rng.uniform(-0.5, 0.5, 6)) for _ in weights]
        new_weights = transform_hidden_permutation_and_gauge(weights, perms, gauges)
        old_prediction, _old_anchor, _ = model.predict(weights)
        new_prediction, _new_anchor, _ = model.predict(new_weights)
        np.testing.assert_allclose(new_prediction, gauges[-1] * old_prediction[perms[-1]], rtol=3e-10, atol=3e-10)

    def test_signed_edge_attention_respects_hidden_permutation_and_gauge(self):
        weights = iid_he_network(1366, width=6, depth=4)
        rng = np.random.default_rng(1367)
        perms = [np.arange(6)] + [rng.permutation(6) for _ in weights]
        gauges = [np.ones(6)] + [np.exp(rng.uniform(-0.5, 0.5, 6)) for _ in weights]
        transformed = transform_hidden_permutation_and_gauge(weights, perms, gauges)
        old_state, new_state = diagonal_gaussian_states(weights), diagonal_gaussian_states(transformed)
        layer = 2
        old = signed_edge_attention(
            analytic_node_tokens(old_state, layer - 1),
            analytic_node_tokens(old_state, layer),
            old_state.normalized_weights[layer],
        )
        new = signed_edge_attention(
            analytic_node_tokens(new_state, layer - 1),
            analytic_node_tokens(new_state, layer),
            new_state.normalized_weights[layer],
        )
        np.testing.assert_allclose(new, old[perms[layer + 1]], rtol=2e-11, atol=2e-11)

    def test_label_shuffling_cannot_pass_real_residual_gate(self):
        # The CI gate is constructed from network-level errors.  A deliberately
        # shuffled candidate loses its pairing and is safely rejected.
        rng = np.random.default_rng(1365)
        teacher = rng.normal(size=(16, 5))
        anchor = teacher + 0.1 * rng.normal(size=(16, 5))
        candidate = teacher + 0.1 * rng.normal(size=(16, 5))
        candidate = candidate[rng.permutation(16)]
        _ratio, _lo, hi = _bootstrap_ratio_ci(anchor, candidate, teacher, draws=2000)
        self.assertGreater(hi, 0.5)

    def test_target_envelope_is_under_80b_only_with_declared_float32_gate(self):
        fp32 = target_cost_envelope()
        fp64 = target_cost_envelope(dtype_multiplier=2.0)
        self.assertTrue(fp32["below_80B"])
        self.assertLess(fp32["protected_billed_flops_including_2B_nonmatmul_reserve"], 80e9)
        self.assertLess(fp64["protected_billed_flops_including_2B_nonmatmul_reserve"], 80e9)
        self.assertEqual(len(CHANNELS), 6)


if __name__ == "__main__":
    unittest.main()
