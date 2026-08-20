"""Response-free algebra and static-ledger tests for M151.

All arrays are Philox-generated local fixtures.  These tests intentionally do
not import an estimator, contest model, scorer, response, or coefficient
provider.
"""

from __future__ import annotations

import unittest

import numpy as np

from m151_b1_forward_control import (
    B1_NODE_COUNT,
    B1CanonicalState,
    b1_forward_static_ledger,
    canonical_delta_tilde_b1,
    dense_ordered_211_source,
    forward_b1_control_source,
    source_add,
    source_max_abs_difference,
    source_scale,
)


def _state(seed: int, width: int) -> B1CanonicalState:
    rng = np.random.Generator(np.random.Philox(seed))
    # Signed weights exercise finite-moment-functional semantics: this is not
    # a probability-mixture test.
    # Keep the normalizer well-conditioned while retaining negative weights;
    # an accidental near-zero signed sum would test cancellation magnitude,
    # not the finite-moment identity.
    omega = 1.0 / B1_NODE_COUNT + rng.normal(scale=0.04, size=B1_NODE_COUNT)
    omega /= np.sum(omega)
    return B1CanonicalState(
        omega=omega,
        conditional_mean=rng.normal(scale=0.3, size=(B1_NODE_COUNT, width)),
        conditional_variance=0.02 + rng.random((B1_NODE_COUNT, width)),
    )


def _symmetric_distinct_delta(seed: int, width: int) -> np.ndarray:
    rng = np.random.Generator(np.random.Philox(seed))
    answer = np.zeros((width, width, width), dtype=np.float64)
    for i in range(width):
        for j in range(width):
            for k in range(j + 1, width):
                if i == j or i == k:
                    continue
                value = float(rng.normal())
                answer[i, j, k] = value
                answer[i, k, j] = value
    return answer


class B1ForwardControlTest(unittest.TestCase):
    def test_b1_state_has_signed_49_node_moment_contract(self) -> None:
        state = _state(15101, width=5)
        delta = canonical_delta_tilde_b1(state)
        self.assertEqual(state.omega.shape, (49,))
        self.assertLess(abs(float(np.sum(state.omega)) - 1.0), 3e-13)
        self.assertLess(np.max(np.abs(delta - delta.swapaxes(1, 2))), 3e-12)
        for i in range(5):
            self.assertTrue(np.all(delta[i, i, :] == 0.0))
            self.assertTrue(np.all(delta[i, :, i] == 0.0))
            self.assertTrue(np.all(delta[:, i, i] == 0.0))

    def test_control_plus_exact_residual_mean_is_the_full_owned_source(self) -> None:
        width, output_width = 5, 4
        rng = np.random.Generator(np.random.Philox(15102))
        weight = rng.normal(size=(width, output_width))
        control_delta = canonical_delta_tilde_b1(_state(15103, width))
        reference_delta = _symmetric_distinct_delta(15104, width)

        control = forward_b1_control_source(weight, _state(15103, width))
        residual = dense_ordered_211_source(weight, reference_delta - control_delta)
        target = dense_ordered_211_source(weight, reference_delta)
        self.assertLess(
            source_max_abs_difference(source_add(control, residual), target),
            4e-11,
        )

    def test_forward_control_has_mandatory_ordered_singleton_half_owner(self) -> None:
        width, output_width = 5, 3
        rng = np.random.Generator(np.random.Philox(15105))
        state = _state(15106, width)
        weight = rng.normal(size=(width, output_width))
        delta = canonical_delta_tilde_b1(state)
        reference = dense_ordered_211_source(weight, delta)
        actual = forward_b1_control_source(weight, state)
        doubled = source_scale(2.0, actual)
        self.assertLess(source_max_abs_difference(actual, reference), 4e-11)
        self.assertGreater(source_max_abs_difference(doubled, reference), 1e-8)

    def test_b1_forward_core_and_k128_endpoint_residual_stay_below_100b(self) -> None:
        ledger = b1_forward_static_ledger()
        self.assertEqual(ledger["blocks"], 1)
        self.assertEqual(ledger["nodes"], 49)
        self.assertEqual(ledger["residual_draws_per_layer"], 128)
        self.assertAlmostEqual(ledger["known_forward_core_billions"], 3.72775744)
        self.assertAlmostEqual(ledger["known_total_endpoint_billions"], 89.70863624)
        self.assertAlmostEqual(ledger["untraced_provider_call_wall_cap_billions"], 10.29136376)
        self.assertTrue(ledger["known_core_fits"])
        self.assertTrue(ledger["premise_gate_requires_native_trace"])

    def test_b1_rejects_any_other_node_count(self) -> None:
        state = _state(15107, width=4)
        with self.assertRaises(ValueError):
            B1CanonicalState(
                omega=state.omega[:-1],
                conditional_mean=state.conditional_mean[:-1],
                conditional_variance=state.conditional_variance[:-1],
            )


if __name__ == "__main__":
    unittest.main()
