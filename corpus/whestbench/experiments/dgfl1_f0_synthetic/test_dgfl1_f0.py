from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dgfl1_f0 import (  # noqa: E402
    canonical_pairwise_mean,
    dipole_rungs,
    evaluate_bank,
    forward_jvp,
    forward_jvp_row_weights,
    fourier_rung,
    fused_rung,
    rotation_2d,
    rotation_generator,
)


def hand_network() -> tuple[np.ndarray, ...]:
    """A deterministic bias-free two-layer CPWL network."""

    return (
        np.array(
            [
                [1.0, -0.3],
                [0.4, 0.8],
                [-0.7, 0.5],
            ],
            dtype=np.float64,
        ),
        np.array(
            [
                [0.6, -0.2, 0.9],
                [-0.4, 1.1, 0.3],
            ],
            dtype=np.float64,
        ),
    )


class RotationGeneratorTests(unittest.TestCase):
    def test_rank_two_generator_has_the_frozen_dipole_orientation(self) -> None:
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])

        J = rotation_generator(m, b)

        np.testing.assert_array_equal(J.T, -J)
        np.testing.assert_array_equal(J @ m, b)
        np.testing.assert_array_equal(J @ b, -m)
        np.testing.assert_array_equal(J @ J, -np.eye(2))

    def test_nontrivial_four_dimensional_generator_matches_projector_reference(self) -> None:
        m = np.array([1.0, 2.0, 3.0, 4.0]) / math.sqrt(30.0)
        b = np.array([2.0, -1.0, 0.0, 0.0]) / math.sqrt(5.0)
        projector = np.outer(m, m) + np.outer(b, b)

        J = rotation_generator(m, b)

        np.testing.assert_allclose(np.diag(J), 0.0, rtol=0.0, atol=0.0)
        np.testing.assert_allclose(J.T, -J, rtol=0.0, atol=0.0)
        np.testing.assert_allclose(J @ m, b, rtol=0.0, atol=3e-16)
        np.testing.assert_allclose(J @ b, -m, rtol=0.0, atol=3e-16)
        np.testing.assert_allclose(J @ J, -projector, rtol=0.0, atol=3e-16)

    def test_generator_rejects_nonunit_or_nonorthogonal_pairs(self) -> None:
        with self.assertRaisesRegex(ValueError, "unit norm"):
            rotation_generator(np.array([2.0, 0.0]), np.array([0.0, 1.0]))
        with self.assertRaisesRegex(ValueError, "orthogonal"):
            rotation_generator(np.array([1.0, 0.0]), np.array([1.0, 0.0]))


class SharedJVPTests(unittest.TestCase):
    def test_whest_row_weights_and_absorbed_q_transport_match_physical_coordinates(self) -> None:
        angle = 0.47
        Q = np.array(
            [
                [math.cos(angle), -math.sin(angle), 0.0],
                [math.sin(angle), math.cos(angle), 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        weights_row = (
            np.array(
                [
                    [0.8, -0.1, 0.4, 0.6],
                    [0.3, 0.9, -0.7, 0.2],
                    [-0.5, 0.2, 1.1, -0.4],
                ],
                dtype=np.float64,
            ),
            np.array(
                [
                    [0.7, -0.3],
                    [-0.2, 0.6],
                    [0.5, 0.8],
                    [0.1, -0.9],
                ],
                dtype=np.float64,
            ),
        )
        v = np.array([0.36, -0.48, 0.8])
        radius = 2.75
        J_physical = rotation_generator(
            np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])
        )
        x_physical = radius * (Q @ v)
        dx_physical = J_physical @ x_physical

        direct = forward_jvp_row_weights(weights_row, x_physical, dx_physical)
        absorbed_weights = (Q.T @ weights_row[0], weights_row[1])
        J_base = Q.T @ J_physical @ Q
        absorbed = forward_jvp_row_weights(
            absorbed_weights, radius * v, radius * (J_base @ v)
        )

        np.testing.assert_allclose(direct[0], absorbed[0], rtol=0.0, atol=3e-16)
        np.testing.assert_allclose(direct[1], absorbed[1], rtol=0.0, atol=3e-16)

    def test_deep_jvp_matches_centered_directional_difference_away_from_gates(self) -> None:
        weights = hand_network()
        theta = 0.371
        x = rotation_2d(theta) @ np.array([1.0, 0.0])
        J = rotation_generator(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
        dx = J @ x

        y, dy = forward_jvp(weights, x, dx)
        eps = 2.0**-20
        y_plus, _ = forward_jvp(weights, x + eps * dx, np.zeros_like(dx))
        y_minus, _ = forward_jvp(weights, x - eps * dx, np.zeros_like(dx))
        reference = (y_plus - y_minus) / (2.0 * eps)

        self.assertTrue(np.all(np.isfinite(y)))
        np.testing.assert_allclose(dy, reference, rtol=2e-9, atol=2e-10)

    def test_deep_jvp_matches_independently_constructed_full_jacobian(self) -> None:
        weights = hand_network()
        theta = 0.371
        x = rotation_2d(theta) @ np.array([1.0, 0.0])
        J = rotation_generator(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
        dx = J @ x

        _, dy = forward_jvp(weights, x, dx)
        state = x.copy()
        full_jacobian = np.eye(2)
        for weight in weights:
            preactivation = weight @ state
            active = np.diag((preactivation > 0.0).astype(np.float64))
            full_jacobian = active @ weight @ full_jacobian
            state = np.maximum(preactivation, 0.0)
        reference = full_jacobian @ dx

        np.testing.assert_allclose(dy, reference, rtol=0.0, atol=2e-16)

    def test_physical_orbit_tangent_includes_the_input_radius(self) -> None:
        weights = hand_network()
        radius = 2.75
        theta = 0.371
        u = rotation_2d(theta) @ np.array([1.0, 0.0])
        x = radius * u
        J = rotation_generator(np.array([1.0, 0.0]), np.array([0.0, 1.0]))

        _, dy = forward_jvp(weights, x, J @ x)
        eps = 2.0**-20
        y_plus, _ = forward_jvp(
            weights, radius * (rotation_2d(theta + eps) @ np.array([1.0, 0.0])), np.zeros(2)
        )
        y_minus, _ = forward_jvp(
            weights, radius * (rotation_2d(theta - eps) @ np.array([1.0, 0.0])), np.zeros(2)
        )
        reference = (y_plus - y_minus) / (2.0 * eps)
        _, wrong_scale = forward_jvp(weights, x, J @ u)

        np.testing.assert_allclose(dy, reference, rtol=2e-9, atol=2e-10)
        self.assertGreater(float(np.max(np.abs(dy - wrong_scale))), 0.1)

    def test_relu_at_zero_uses_strict_positive_jvp_and_exposes_both_one_sided_derivatives(self) -> None:
        weights = (np.array([[1.0, 0.0]], dtype=np.float64),)
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        J = rotation_generator(m, b)
        u = b.copy()

        y, dy = forward_jvp(weights, u, J @ u)
        self.assertEqual(float(y[0]), 0.0)
        self.assertEqual(float(dy[0]), 0.0)

        eps = 2.0**-24
        y_right, _ = forward_jvp(weights, rotation_2d(eps) @ u, np.zeros(2))
        y_left, _ = forward_jvp(weights, rotation_2d(-eps) @ u, np.zeros(2))
        right = (y_right[0] - y[0]) / eps
        left = (y[0] - y_left[0]) / eps

        self.assertAlmostEqual(float(right), 0.0, places=12)
        self.assertAlmostEqual(float(left), -1.0, places=9)


class ProductRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.weights = hand_network()
        self.m = np.array([1.0, 0.0])
        self.b = np.array([0.0, 1.0])
        self.J = rotation_generator(self.m, self.b)
        self.theta = 0.413
        self.u = rotation_2d(self.theta) @ self.m
        self.y, self.dy = forward_jvp(self.weights, self.u, self.J @ self.u)

    def _orbit_product_derivative(self, modulator, eps: float = 2.0**-19) -> np.ndarray:
        def product(theta: float) -> np.ndarray:
            u = rotation_2d(theta) @ self.m
            y, _ = forward_jvp(self.weights, u, np.zeros(2))
            return modulator(u) * y

        return (product(self.theta + eps) - product(self.theta - eps)) / (2.0 * eps)

    def test_both_dipole_signs_match_orbit_product_derivatives(self) -> None:
        controls = dipole_rungs(self.u, self.y, self.dy, self.m, self.b)

        reference_m = self._orbit_product_derivative(lambda u: float(self.m @ u))
        reference_b = self._orbit_product_derivative(lambda u: float(self.b @ u))

        np.testing.assert_allclose(controls[0], reference_m, rtol=3e-9, atol=3e-10)
        np.testing.assert_allclose(controls[1], reference_b, rtol=3e-9, atol=3e-10)

    def test_fourier_rung_includes_the_signed_product_rule_term(self) -> None:
        a = np.array([0.6, 0.8])
        k = 2.75

        control = fourier_rung(self.u, self.y, self.dy, self.J, a, k)
        reference = self._orbit_product_derivative(lambda u: math.cos(k * float(a @ u)))

        np.testing.assert_allclose(control, reference, rtol=4e-9, atol=4e-10)

    def test_fourier_rung_rejects_a_nonunit_pilot_axis(self) -> None:
        with self.assertRaisesRegex(ValueError, "unit norm"):
            fourier_rung(
                self.u,
                self.y,
                self.dy,
                self.J,
                np.array([1.2, 0.0]),
                2.75,
            )

    def test_fourier_lie_term_vanishes_when_axis_is_in_kernel_of_J(self) -> None:
        m = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        axis = np.array([0.0, 0.0, 1.0])
        J = rotation_generator(m, b)
        u = np.array([0.4, 0.5, math.sqrt(0.59)])
        y = np.array([0.7, -0.2])
        dy = np.array([0.3, 0.9])
        frequency = 2.75

        actual = fourier_rung(u, y, dy, J, axis, frequency)
        expected = math.cos(frequency * float(axis @ u)) * dy

        self.assertEqual(float(axis @ (J @ u)), 0.0)
        np.testing.assert_allclose(actual, expected, rtol=0.0, atol=2e-16)

    def test_controls_reject_malformed_geometry(self) -> None:
        with self.assertRaisesRegex(ValueError, "orthogonal"):
            dipole_rungs(self.u, self.y, self.dy, self.m, self.m)
        with self.assertRaisesRegex(ValueError, "skew"):
            fourier_rung(
                self.u,
                self.y,
                self.dy,
                np.eye(2),
                np.array([0.6, 0.8]),
                2.75,
            )
        with self.assertRaisesRegex(ValueError, "same shape"):
            fused_rung(
                self.u,
                self.y,
                np.array([1.0]),
                self.m,
                self.b,
                self.J,
                (np.array([0.6, 0.8]),),
                (2.75,),
                np.array([0.1, 0.2, 0.3]),
            )

    def test_fused_control_equals_weighted_sum_of_separate_rungs(self) -> None:
        axes = (np.array([0.6, 0.8]), np.array([-0.8, 0.6]))
        frequencies = (1.5, 3.0)
        betas = np.array([0.25, -0.4, 0.7, -0.1, 0.05, 0.3])

        separate = list(dipole_rungs(self.u, self.y, self.dy, self.m, self.b))
        for a in axes:
            for k in frequencies:
                separate.append(fourier_rung(self.u, self.y, self.dy, self.J, a, k))
        expected = np.tensordot(betas, np.stack(separate), axes=(0, 0))

        actual = fused_rung(
            self.u,
            self.y,
            self.dy,
            self.m,
            self.b,
            self.J,
            axes,
            frequencies,
            betas,
        )

        np.testing.assert_allclose(actual, expected, rtol=2e-15, atol=2e-15)


class WeakCenteringAndScheduleTests(unittest.TestCase):
    def test_antipodal_average_selects_even_and_odd_network_parts(self) -> None:
        weights = hand_network()
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        J = rotation_generator(m, b)
        u = rotation_2d(0.413) @ m
        y_plus, dy_plus = forward_jvp(weights, u, J @ u)
        y_minus, dy_minus = forward_jvp(weights, -u, -(J @ u))

        dipole_plus = dipole_rungs(u, y_plus, dy_plus, m, b)[0]
        dipole_minus = dipole_rungs(-u, y_minus, dy_minus, m, b)[0]
        y_odd = (y_plus - y_minus) / 2.0
        dy_odd = (dy_plus - dy_minus) / 2.0
        odd_reference = dipole_rungs(u, y_odd, dy_odd, m, b)[0]

        axis = np.array([0.6, 0.8])
        frequency = 3.0
        fourier_plus = fourier_rung(u, y_plus, dy_plus, J, axis, frequency)
        fourier_minus = fourier_rung(-u, y_minus, dy_minus, J, axis, frequency)
        y_even = (y_plus + y_minus) / 2.0
        dy_even = (dy_plus + dy_minus) / 2.0
        even_reference = fourier_rung(u, y_even, dy_even, J, axis, frequency)

        np.testing.assert_allclose(
            (dipole_plus + dipole_minus) / 2.0, odd_reference, rtol=0.0, atol=3e-16
        )
        np.testing.assert_allclose(
            (fourier_plus + fourier_minus) / 2.0,
            even_reference,
            rtol=0.0,
            atol=3e-16,
        )

    def test_each_control_has_near_zero_full_orbit_mean_on_a_cpwl_network(self) -> None:
        # The two outputs are ReLU(+x_1) and ReLU(-x_1).  Splitting at their
        # exact gate angles lets Gauss-Legendre integrate the a.e. control on
        # smooth cells without sampling an arbitrary ReLU subgradient.
        weights = (np.array([[1.0, 0.0], [-1.0, 0.0]], dtype=np.float64),)
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        J = rotation_generator(m, b)
        a = np.array([0.6, 0.8])
        k = 3.0
        nodes, quadrature_weights = np.polynomial.legendre.leggauss(64)
        integral = np.zeros((3, 2), dtype=np.float64)
        cells = (
            (0.0, math.pi / 2.0),
            (math.pi / 2.0, 3.0 * math.pi / 2.0),
            (3.0 * math.pi / 2.0, 2.0 * math.pi),
        )

        for lower, upper in cells:
            midpoint = (lower + upper) / 2.0
            half_width = (upper - lower) / 2.0
            for node, weight in zip(nodes, quadrature_weights, strict=True):
                theta = midpoint + half_width * node
                u = rotation_2d(theta) @ m
                y, dy = forward_jvp(weights, u, J @ u)
                integral[:2] += half_width * weight * dipole_rungs(u, y, dy, m, b)
                integral[2] += half_width * weight * fourier_rung(u, y, dy, J, a, k)

        means = integral / (2.0 * math.pi)
        np.testing.assert_allclose(means, 0.0, rtol=0.0, atol=2e-14)

    def test_two_shards_preserve_canonical_leaves_mean_and_one_jvp_per_row(self) -> None:
        weights = hand_network()
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        axes = (np.array([0.6, 0.8]), np.array([-0.8, 0.6]))
        frequencies = (1.5, 3.0)
        betas = np.array([0.25, -0.4, 0.7, -0.1, 0.05, 0.3])
        rows = np.stack(
            [rotation_2d(0.17 + 2.0 * math.pi * i / 64) @ m for i in range(64)]
        )

        serial, serial_receipt = evaluate_bank(
            rows, weights, m, b, axes, frequencies, betas, radius=1.0, shard_count=1
        )
        split, split_receipt = evaluate_bank(
            rows, weights, m, b, axes, frequencies, betas, radius=1.0, shard_count=2
        )

        self.assertEqual(serial.tobytes(), split.tobytes())
        self.assertEqual(serial_receipt["leaf_order"], list(range(64)))
        self.assertEqual(split_receipt["leaf_order"], list(range(64)))
        self.assertEqual(serial_receipt["jvp_evaluations"], 64)
        self.assertEqual(split_receipt["jvp_evaluations"], 64)

    def test_uneven_shards_are_bitwise_invariant_to_adversarial_completion_order(self) -> None:
        weights = hand_network()
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        axes = (np.array([0.6, 0.8]), np.array([-0.8, 0.6]))
        frequencies = (1.5, 3.0)
        betas = np.array([0.25, -0.4, 0.7, -0.1, 0.05, 0.3])
        rows = np.stack(
            [rotation_2d(0.17 + 2.0 * math.pi * i / 65) @ m for i in range(65)]
        )

        serial, _ = evaluate_bank(
            rows, weights, m, b, axes, frequencies, betas, radius=1.0, shard_count=1
        )
        reordered, receipt = evaluate_bank(
            rows,
            weights,
            m,
            b,
            axes,
            frequencies,
            betas,
            radius=1.0,
            shard_count=3,
            shard_emission_order=(2, 0, 1),
        )

        self.assertEqual(serial.tobytes(), reordered.tobytes())
        self.assertEqual(receipt["emission_order"], [2, 0, 1])
        self.assertEqual(receipt["leaf_order"], list(range(65)))
        self.assertEqual(receipt["jvp_evaluations"], 65)

    def test_bank_path_scales_the_physical_input_and_tangent_by_radius(self) -> None:
        weights = hand_network()
        m = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        axes = (np.array([0.6, 0.8]),)
        frequencies = (2.75,)
        betas = np.array([0.25, -0.4, 0.7])
        rows = np.stack(
            [rotation_2d(0.11 + 2.0 * math.pi * i / 33) @ m for i in range(33)]
        )
        radius = 2.75

        unit, _ = evaluate_bank(
            rows, weights, m, b, axes, frequencies, betas, radius=1.0, shard_count=1
        )
        physical, receipt = evaluate_bank(
            rows, weights, m, b, axes, frequencies, betas, radius=radius, shard_count=2
        )

        np.testing.assert_allclose(physical, radius * unit, rtol=2e-15, atol=2e-15)
        self.assertEqual(receipt["radius"], radius)

    def test_canonical_pairwise_mean_rejects_empty_or_nonfinite_leaves(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonempty"):
            canonical_pairwise_mean([])
        with self.assertRaisesRegex(ValueError, "finite"):
            canonical_pairwise_mean([np.array([np.nan])])


if __name__ == "__main__":
    unittest.main()
