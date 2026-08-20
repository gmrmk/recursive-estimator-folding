"""Adversarial unit contract for the frozen M243 G0A component."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest
from unittest import mock

import numpy as np

import m243_event_local_q4_source_premise as candidate

from m243_event_local_q4_source_premise import (
    M243DomainRefusal,
    Q4Packet,
    conditional_centered_pair,
    folded_distinct_event,
    q4_packet,
)

from m147_endpoint_safe_bridge import (  # type: ignore  # imported through candidate path binding
    build_endpoint_state_frechet,
    conditional_collision211_endpoint_dot,
)


def _state(mean: np.ndarray, covariance: np.ndarray):
    return build_endpoint_state_frechet(
        np.asarray(mean, dtype=np.float64),
        np.asarray(covariance, dtype=np.float64),
        np.zeros_like(mean, dtype=np.float64),
        np.zeros_like(covariance, dtype=np.float64),
    )


def _a1_state():
    mean = np.asarray((-0.2, 0.45, -0.35), dtype=np.float64)
    scale = np.asarray((0.7, 1.3, 1.8), dtype=np.float64)
    corr = np.asarray(
        ((1.0, 0.75, -0.55), (0.75, 1.0, -0.10), (-0.55, -0.10, 1.0)),
        dtype=np.float64,
    )
    covariance = np.outer(scale, scale) * corr
    covariance = 0.5 * (covariance + covariance.T)
    return _state(mean, covariance)


def _binary_projection_reference(tangent, i: int, j: int, k: int):
    nodes, weights = np.polynomial.legendre.leggauss(48)
    alpha = float(tangent.state.alpha[i])
    panels = sorted(set((-16.0, -10.0, -8.0, -5.0, -2.5, -1.0, -0.25, 0.0, 0.25, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0, -alpha)))
    beta = np.zeros(5, dtype=np.float64)
    repeated = np.zeros(5, dtype=np.float64)
    inverse_root_two_pi = 1.0 / np.sqrt(2.0 * np.pi)
    for left, right in zip(panels[:-1], panels[1:]):
        midpoint = 0.5 * (left + right)
        half = 0.5 * (right - left)
        for node, weight in zip(nodes, weights):
            g = midpoint + half * float(node)
            density = inverse_root_two_pi * np.exp(-0.5 * g * g)
            h = np.asarray((1.0, g, g * g - 1.0, g**3 - 3.0 * g, g**4 - 6.0 * g * g + 3.0))
            pair = conditional_centered_pair(tangent, i, j, k, g).value
            rectified = max(0.0, tangent.state.mean[i] + tangent.state.sigma[i] * g)
            r = (rectified - tangent.state.relu_mean[i]) ** 2
            factor = half * float(weight) * density
            beta += factor * pair * h
            repeated += factor * r * h
    beta /= np.asarray((1.0, 1.0, 2.0, 6.0, 24.0))
    return beta, repeated


class TestM243InitialContract(unittest.TestCase):
    def test_public_surface(self) -> None:
        self.assertTrue(callable(q4_packet))
        self.assertTrue(callable(conditional_centered_pair))
        self.assertTrue(callable(folded_distinct_event))
        self.assertIsNotNone(Q4Packet)

    def test_q4_packet_refuses_collisions_before_state_access(self) -> None:
        for labels in ((0, 0, 0), (0, 0, 1), (0, 1, 1)):
            with self.subTest(labels=labels):
                with self.assertRaises(M243DomainRefusal):
                    q4_packet(object(), *labels)

    def test_folded_event_refuses_every_non_211_stratum(self) -> None:
        for labels in (
            (0, 0, 0, 0),
            (0, 0, 0, 1),
            (0, 0, 1, 1),
            (0, 1, 2, 3),
        ):
            with self.subTest(labels=labels):
                with self.assertRaises(M243DomainRefusal):
                    folded_distinct_event(object(), labels, 0.0, degree=None)

    def test_packet_matches_degree_zero_identities_and_singleton_swap(self) -> None:
        tangent = _a1_state()
        packet = q4_packet(tangent, 0, 1, 2)
        swapped = q4_packet(tangent, 0, 2, 1)
        post_covariance = (
            np.outer(tangent.state.relu_scale, tangent.state.relu_scale)
            * tangent.state.bridge
        )
        self.assertEqual(len(packet.beta), 5)
        self.assertEqual(len(packet.repeated_R), 5)
        self.assertEqual(len(packet.beta_radius), 5)
        self.assertTrue(packet.base_jet_contained)
        self.assertLessEqual(
            abs(packet.beta[0] - post_covariance[1, 2]),
            packet.beta_radius[0] + 5.0e-13,
        )
        self.assertAlmostEqual(packet.repeated_R[0], post_covariance[0, 0], places=13)
        np.testing.assert_allclose(packet.beta, swapped.beta, rtol=0.0, atol=3.0e-13)
        np.testing.assert_allclose(packet.repeated_R, swapped.repeated_R, rtol=0.0, atol=0.0)

    def test_packet_matches_direct_binary_projection_before_high_precision_gate(self) -> None:
        tangent = _a1_state()
        packet = q4_packet(tangent, 0, 1, 2)
        beta_reference, repeated_reference = _binary_projection_reference(tangent, 0, 1, 2)
        np.testing.assert_allclose(packet.beta, beta_reference, rtol=2.0e-10, atol=2.0e-10)
        np.testing.assert_allclose(packet.repeated_R, repeated_reference, rtol=2.0e-10, atol=2.0e-10)

    def test_independent_coordinates_contain_the_exact_zero_pair_and_event(self) -> None:
        tangent = _state(np.asarray((-0.4, 0.1, 0.7)), np.eye(3, dtype=np.float64))
        packet = q4_packet(tangent, 0, 1, 2)
        for center, radius in zip(packet.beta, packet.beta_radius):
            self.assertLessEqual(abs(center), radius)
        for g in (-8.0, -1.0, 0.0, 1.0, 8.0):
            pair = conditional_centered_pair(tangent, 0, 1, 2, g)
            self.assertLessEqual(abs(pair.value), pair.radius)
            for degree in (None, 2, 4):
                event = folded_distinct_event(tangent, (0, 0, 1, 2), g, degree=degree)
                self.assertLessEqual(abs(event.value), event.radius)

    def test_conditional_pair_and_folded_values_are_finite_on_frozen_tail_grid(self) -> None:
        tangent = _a1_state()
        for g in (
            0.0, 2.0**-8, -2.0**-8, 0.25, -0.25, 1.0, -1.0,
            2.5, -2.5, 5.0, -5.0, 8.0, -8.0, 10.0, -10.0, 16.0, -16.0,
        ):
            with self.subTest(g=g):
                pair = conditional_centered_pair(tangent, 0, 1, 2, g)
                self.assertTrue(np.isfinite(pair.value))
                self.assertTrue(np.isfinite(pair.radius))
                self.assertGreaterEqual(pair.radius, 0.0)
                for degree in (None, 2, 4):
                    event = folded_distinct_event(tangent, (0, 0, 1, 2), g, degree=degree)
                    self.assertTrue(np.isfinite(event.value))
                    self.assertTrue(np.isfinite(event.radius))
                    self.assertEqual(event.labels, (0, 1, 2))
                    self.assertEqual(event.owner_factor, 0.5)

    def test_tree_is_exactly_the_m147_m122_m126_convention(self) -> None:
        tangent = _a1_state()
        reference = conditional_collision211_endpoint_dot(tangent, 0, 1, 2)
        event = folded_distinct_event(tangent, (2, 0, 1, 0), 0.375, degree=4)
        self.assertEqual(event.labels, (0, 1, 2))
        self.assertEqual(event.tree, reference.tree)

    def test_universal_addback_is_pointwise_exact_for_arbitrary_coefficients(self) -> None:
        tangent = _a1_state()
        real = q4_packet(tangent, 0, 1, 2)
        coefficients = (0.375, -0.625, 0.875, -1.125, 1.375)
        zero = candidate.Q4Packet((0.0,) * 5, real.repeated_R, (0.0,) * 5, True, "TEST", real.labels)
        chosen = candidate.Q4Packet(coefficients, real.repeated_R, (0.0,) * 5, True, "TEST", real.labels)
        g = 0.625
        h_plus = (1.0, g, g * g - 1.0, g**3 - 3.0 * g, g**4 - 6.0 * g * g + 3.0)
        h_minus = (1.0, -g, g * g - 1.0, -g**3 + 3.0 * g, g**4 - 6.0 * g * g + 3.0)
        base = tangent.state
        r_plus = (max(0.0, base.mean[0] + base.sigma[0] * g) - base.relu_mean[0]) ** 2
        r_minus = (max(0.0, base.mean[0] - base.sigma[0] * g) - base.relu_mean[0]) ** 2
        for degree in (2, 4):
            count = degree + 1
            with mock.patch.object(candidate, "q4_packet", return_value=zero):
                z0 = folded_distinct_event(tangent, (0, 0, 1, 2), g, degree=degree).value
            with mock.patch.object(candidate, "q4_packet", return_value=chosen):
                zc = folded_distinct_event(tangent, (0, 0, 1, 2), g, degree=degree).value
            expected = (
                -0.5
                * (
                    r_plus * sum(coefficients[index] * h_plus[index] for index in range(count))
                    + r_minus * sum(coefficients[index] * h_minus[index] for index in range(count))
                )
                + sum(coefficients[index] * real.repeated_R[index] for index in range(count))
            )
            self.assertAlmostEqual(zc - z0, expected, places=14)

    def test_cyclic_co_permutation_and_positive_gauge_have_the_frozen_degree(self) -> None:
        tangent = _a1_state()
        base_packet = q4_packet(tangent, 0, 1, 2)
        base_event = folded_distinct_event(tangent, (0, 0, 1, 2), 0.625, degree=4)

        permutation = np.asarray((1, 2, 0), dtype=np.int64)
        mean_p = np.empty(3, dtype=np.float64)
        covariance_p = np.empty((3, 3), dtype=np.float64)
        mean_p[permutation] = tangent.state.mean
        covariance_p[np.ix_(permutation, permutation)] = tangent.state.covariance
        permuted = _state(mean_p, covariance_p)
        perm_packet = q4_packet(permuted, 1, 2, 0)
        perm_event = folded_distinct_event(permuted, (1, 1, 2, 0), 0.625, degree=4)
        np.testing.assert_allclose(base_packet.beta, perm_packet.beta, rtol=0.0, atol=4.0e-13)
        np.testing.assert_allclose(base_packet.repeated_R, perm_packet.repeated_R, rtol=0.0, atol=4.0e-13)
        self.assertAlmostEqual(base_event.value, perm_event.value, places=12)

        lam = np.asarray([2.0 ** (((a % 5) - 2) / 4.0) for a in range(3)])
        gauged = _state(lam * tangent.state.mean, np.outer(lam, lam) * tangent.state.covariance)
        gauge_packet = q4_packet(gauged, 0, 1, 2)
        gauge_event = folded_distinct_event(gauged, (0, 0, 1, 2), 0.625, degree=4)
        beta_degree = lam[1] * lam[2]
        repeated_degree = lam[0] ** 2
        event_degree = repeated_degree * beta_degree
        np.testing.assert_allclose(
            gauge_packet.beta,
            beta_degree * np.asarray(base_packet.beta),
            rtol=0.0,
            atol=2.0e-10,
        )
        np.testing.assert_allclose(
            gauge_packet.repeated_R,
            repeated_degree * np.asarray(base_packet.repeated_R),
            rtol=0.0,
            atol=2.0e-10,
        )
        self.assertLessEqual(
            abs(gauge_event.value - event_degree * base_event.value)
            / (1.0 + abs(event_degree * base_event.value)),
            2.0e-10,
        )

    def test_parser_canonicalizes_every_owner_permutation_bitwise(self) -> None:
        tangent = _a1_state()
        baseline = {}
        for degree in (None, 2, 4):
            baseline[degree] = folded_distinct_event(
                tangent, (0, 0, 1, 2), 0.625, degree=degree
            )
        for labels in set(__import__("itertools").permutations((0, 0, 1, 2))):
            for degree in (None, 2, 4):
                observed = folded_distinct_event(tangent, labels, 0.625, degree=degree)
                self.assertEqual(observed.value.hex(), baseline[degree].value.hex())
                self.assertEqual(observed.radius.hex(), baseline[degree].radius.hex())

    def test_candidate_import_firewall(self) -> None:
        tree = ast.parse(Path(candidate.__file__).read_text(encoding="utf-8"))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        forbidden = ("mpmath", "scipy", "m213", "m216")
        self.assertFalse(any(name.lower().startswith(forbidden) for name in imported), imported)

    def test_nonintegral_labels_and_invalid_degrees_refuse(self) -> None:
        tangent = _a1_state()
        with self.assertRaises(M243DomainRefusal):
            q4_packet(tangent, 0.0, 1, 2)
        with self.assertRaises(M243DomainRefusal):
            folded_distinct_event(tangent, (0.2, 0.8, 1.2, 2.2), 0.0, degree=4)
        for degree in (0, 1, 3, 5, True, "4"):
            with self.subTest(degree=degree):
                with self.assertRaises(M243DomainRefusal):
                    folded_distinct_event(tangent, (0, 0, 1, 2), 0.0, degree=degree)


if __name__ == "__main__":
    unittest.main()
