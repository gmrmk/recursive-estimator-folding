from __future__ import annotations

import itertools
import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m122_nonzero_bridge_theory",
    "m126_repeated_output_source_contraction",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m122_nonzero_bridge import build_state, small_source_tensor
from m126_repeated_output_contractions import (
    collision22_probe_sample,
    path_residual_probe_sample,
    tree_repeated_exact,
)
from m129_source_frechet import (
    BridgeStateFrechet,
    CollisionDefects,
    Dual,
    build_collision_defects,
    build_state_frechet,
    collision211_dense_dual,
    collision211_probe_dual,
    collision22_probe_dual,
    collision_repeated_dual,
    exact_collision_cumulant_dot,
    flopscope_cost_envelope,
    path_probe_dual,
    power_hermite_coefficient_dot,
    tree_repeated_dual,
)


def generated_state(n: int, seed: int):
    rng = np.random.default_rng(seed)
    factor = np.eye(n) + 0.10 * rng.normal(size=(n, n))
    covariance = factor @ factor.T + 0.35 * np.eye(n)
    mean = rng.normal(scale=0.30, size=n)
    covariance_dot = rng.normal(scale=0.08, size=(n, n))
    covariance_dot = 0.5 * (covariance_dot + covariance_dot.T)
    mean_dot = rng.normal(scale=0.12, size=n)
    return mean, covariance, mean_dot, covariance_dot


def generated_bridge(n: int, seed: int):
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.12, size=(n, n))
    q = 0.5 * (raw + raw.T)
    np.fill_diagonal(q, 1.0)
    qdot = rng.normal(scale=0.07, size=(n, n))
    qdot = 0.5 * (qdot + qdot.T)
    np.fill_diagonal(qdot, 0.0)
    return q, qdot


def generated_a211(n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    value = np.zeros((n, n, n), dtype=np.float64)
    tangent = np.zeros_like(value)
    for i in range(n):
        other = [j for j in range(n) if j != i]
        for left, j in enumerate(other):
            for k in other[left + 1 :]:
                v, d = rng.normal(size=2)
                value[i, j, k] = value[i, k, j] = v
                tangent[i, j, k] = tangent[i, k, j] = d
    return value, tangent


def repeated_from_dense(
    tensor3: np.ndarray, tensor4: np.ndarray, weight: np.ndarray
) -> dict[str, np.ndarray]:
    transported3 = np.einsum(
        "ijk,ia,jb,kc->abc", tensor3, weight, weight, weight, optimize=True
    )
    transported4 = np.einsum(
        "ijkl,ia,jb,kc,ld->abcd",
        tensor4,
        weight,
        weight,
        weight,
        weight,
        optimize=True,
    )
    outputs = weight.shape[1]
    return {
        "k3_aaa": np.asarray([transported3[a, a, a] for a in range(outputs)]),
        "k3_aab": np.asarray(
            [[transported3[a, a, b] for b in range(outputs)] for a in range(outputs)]
        ),
        "k4_aaaa": np.asarray([transported4[a, a, a, a] for a in range(outputs)]),
        "k4_aaab": np.asarray(
            [[transported4[a, a, a, b] for b in range(outputs)] for a in range(outputs)]
        ),
        "k4_aabb": np.asarray(
            [[transported4[a, a, b, b] for b in range(outputs)] for a in range(outputs)]
        ),
    }


def sparse_with_values(template: CollisionDefects, slot: str, value: np.ndarray) -> CollisionDefects:
    fields = {
        name: getattr(template, name)
        for name in (
            "diagonal3",
            "majority3",
            "diagonal4",
            "majority4",
            "paired4",
            "collision211",
        )
    }
    fields[slot] = Dual(value, np.zeros_like(value))
    return CollisionDefects(**fields)


class M129SourceFrechetTests(unittest.TestCase):
    def assert_close(self, left, right, tolerance=2.0e-7):
        error = float(np.max(np.abs(np.asarray(left) - np.asarray(right))))
        self.assertLessEqual(error, tolerance)

    def test_local_hermite_coefficient_derivative(self):
        rng = np.random.default_rng(129001)
        epsilon = 2.0e-6
        worst = 0.0
        for power in range(1, 5):
            for degree in range(9):
                alpha = float(rng.normal(scale=0.7))
                sigma = float(np.exp(rng.normal(scale=0.2)))
                alpha_dot, sigma_dot = rng.normal(scale=0.3, size=2)
                value, derivative = power_hermite_coefficient_dot(
                    alpha, sigma, power, degree, alpha_dot, sigma_dot
                )
                plus = power_hermite_coefficient_dot(
                    alpha + epsilon * alpha_dot,
                    sigma + epsilon * sigma_dot,
                    power,
                    degree,
                    0.0,
                    0.0,
                )[0]
                minus = power_hermite_coefficient_dot(
                    alpha - epsilon * alpha_dot,
                    sigma - epsilon * sigma_dot,
                    power,
                    degree,
                    0.0,
                    0.0,
                )[0]
                finite_difference = (plus - minus) / (2.0 * epsilon)
                worst = max(worst, abs(derivative - finite_difference))
                self.assertTrue(math.isfinite(value))
        self.assertLessEqual(worst, 2.0e-8)

    def test_complete_bridge_state_frechet_matches_dense_finite_difference(self):
        mean, covariance, mean_dot, covariance_dot = generated_state(4, 129101)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        epsilon = 1.0e-6
        plus = build_state(mean + epsilon * mean_dot, covariance + epsilon * covariance_dot)
        minus = build_state(mean - epsilon * mean_dot, covariance - epsilon * covariance_dot)
        checks = (
            (tangent.sigma_dot, (plus.sigma - minus.sigma) / (2 * epsilon)),
            (tangent.alpha_dot, (plus.alpha - minus.alpha) / (2 * epsilon)),
            (
                tangent.relu_mean_dot,
                (plus.relu_mean - minus.relu_mean) / (2 * epsilon),
            ),
            (
                tangent.relu_scale_dot,
                (plus.relu_scale - minus.relu_scale) / (2 * epsilon),
            ),
            (
                tangent.correlation_dot,
                (plus.correlation - minus.correlation) / (2 * epsilon),
            ),
            (
                tangent.bridge_dot,
                (plus.bridge - minus.bridge) / (2 * epsilon),
            ),
            (
                tangent.gamma2_dot,
                (plus.gamma2 - minus.gamma2) / (2 * epsilon),
            ),
            (
                tangent.gamma3_dot,
                (plus.gamma3 - minus.gamma3) / (2 * epsilon),
            ),
        )
        for exact, observed in checks:
            self.assert_close(exact, observed, 2.0e-7)

    def test_collision_cumulant_dot_includes_211(self):
        mean, covariance, mean_dot, covariance_dot = generated_state(3, 129201)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        epsilon = 2.0e-6
        plus_tangent = build_state_frechet(
            mean + epsilon * mean_dot,
            covariance + epsilon * covariance_dot,
            np.zeros_like(mean),
            np.zeros_like(covariance),
        )
        minus_tangent = build_state_frechet(
            mean - epsilon * mean_dot,
            covariance - epsilon * covariance_dot,
            np.zeros_like(mean),
            np.zeros_like(covariance),
        )
        for labels in ((0, 0, 0), (0, 0, 1), (0, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2)):
            value, derivative = exact_collision_cumulant_dot(tangent, labels, terms=24)
            plus = exact_collision_cumulant_dot(plus_tangent, labels, terms=24)[0]
            minus = exact_collision_cumulant_dot(minus_tangent, labels, terms=24)[0]
            self.assertTrue(math.isfinite(value))
            self.assertAlmostEqual(derivative, (plus - minus) / (2 * epsilon), places=6)

    def test_tree_dual_matches_formula_finite_difference(self):
        n = 4
        rng = np.random.default_rng(129301)
        q, qdot = generated_bridge(n, 129302)
        g2, g3 = rng.normal(size=(2, n))
        g2dot, g3dot = rng.normal(scale=0.1, size=(2, n))
        weight = rng.normal(size=(n, n))
        weight_dot = rng.normal(scale=0.08, size=(n, n))
        actual = tree_repeated_dual(
            q, g2, g3, weight, qdot, g2dot, g3dot, weight_dot
        )
        epsilon = 1.0e-6
        plus = tree_repeated_exact(
            q + epsilon * qdot,
            g2 + epsilon * g2dot,
            g3 + epsilon * g3dot,
            weight + epsilon * weight_dot,
        )
        minus = tree_repeated_exact(
            q - epsilon * qdot,
            g2 - epsilon * g2dot,
            g3 - epsilon * g3dot,
            weight - epsilon * weight_dot,
        )
        base = tree_repeated_exact(q, g2, g3, weight)
        for key in base:
            self.assert_close(actual[key].value, base[key], 2.0e-10)
            self.assert_close(
                actual[key].tangent, (plus[key] - minus[key]) / (2 * epsilon), 2.0e-7
            )

    def test_path_and_22_probe_tangents_use_common_random_numbers(self):
        n = 5
        rng = np.random.default_rng(129401)
        q, qdot = generated_bridge(n, 129402)
        g2 = rng.normal(size=n)
        g2dot = rng.normal(scale=0.1, size=n)
        weight = rng.normal(size=(n, n))
        weight_dot = rng.normal(scale=0.1, size=(n, n))
        z = rng.choice((-1.0, 1.0), size=n)
        actual = path_probe_dual(q, g2, weight, z, qdot, g2dot, weight_dot)
        epsilon = 1.0e-6
        plus = path_residual_probe_sample(
            q + epsilon * qdot,
            g2 + epsilon * g2dot,
            weight + epsilon * weight_dot,
            z,
        )
        minus = path_residual_probe_sample(
            q - epsilon * qdot,
            g2 - epsilon * g2dot,
            weight - epsilon * weight_dot,
            z,
        )
        for key in ("residual_self", "residual_cross"):
            self.assert_close(actual[key].tangent, (plus[key] - minus[key]) / (2 * epsilon), 4e-7)

        paired = rng.normal(size=(n, n))
        paired = 0.5 * (paired + paired.T)
        np.fill_diagonal(paired, 0.0)
        paired_dot = rng.normal(scale=0.1, size=(n, n))
        paired_dot = 0.5 * (paired_dot + paired_dot.T)
        np.fill_diagonal(paired_dot, 0.0)
        observed = collision22_probe_dual(paired, weight, z, paired_dot)
        plus22 = collision22_probe_sample(paired + epsilon * paired_dot, weight, z)
        minus22 = collision22_probe_sample(paired - epsilon * paired_dot, weight, z)
        self.assert_close(observed.tangent, (plus22 - minus22) / (2 * epsilon), 2e-7)

    def test_hollow_quadratic_211_probe_is_exact_in_complete_average(self):
        n = 4
        rng = np.random.default_rng(129501)
        collision, collision_dot = generated_a211(n, 129502)
        weight = rng.normal(size=(n, n))
        dense = collision211_dense_dual(collision, weight, collision_dot)
        accumulated = {
            key: Dual(np.zeros_like(item.value), np.zeros_like(item.tangent))
            for key, item in dense.items()
        }
        signs = tuple(itertools.product((-1.0, 1.0), repeat=n))
        for sign in signs:
            sample = collision211_probe_dual(
                collision, weight, np.asarray(sign), collision_dot
            )
            self.assert_close(sample["k4_aabb"].value, sample["k4_aabb"].value.T, 1e-12)
            self.assert_close(
                np.diag(sample["k4_aaab"].value), sample["k4_aaaa"].value, 1e-12
            )
            self.assert_close(
                np.diag(sample["k4_aabb"].value), sample["k4_aaaa"].value, 1e-12
            )
            for key in dense:
                accumulated[key] = Dual(
                    accumulated[key].value + sample[key].value,
                    accumulated[key].tangent + sample[key].tangent,
                )
        for key in dense:
            self.assert_close(accumulated[key].value / len(signs), dense[key].value, 2e-11)
            self.assert_close(accumulated[key].tangent / len(signs), dense[key].tangent, 2e-11)

        leaked = collision.copy()
        leaked[0, 1, 1] = 1.0
        with self.assertRaisesRegex(ValueError, "diagonal leakage"):
            collision211_probe_dual(leaked, weight, np.ones(n), collision_dot)

    def test_full_source_and_tangent_decompose_exactly_including_211(self):
        n = 3
        rng = np.random.default_rng(129601)
        mean, covariance, mean_dot, covariance_dot = generated_state(n, 129602)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        defects = build_collision_defects(tangent, terms=24)
        weight = rng.normal(size=(n, n))
        effective_weight = tangent.state.relu_scale[:, None] * weight
        effective_weight_dot = tangent.relu_scale_dot[:, None] * weight
        tree = tree_repeated_dual(
            tangent.state.bridge,
            tangent.state.gamma2,
            tangent.state.gamma3,
            effective_weight,
            tangent.bridge_dot,
            tangent.gamma2_dot,
            tangent.gamma3_dot,
            effective_weight_dot,
        )
        sparse = collision_repeated_dual(defects, weight)
        collision211 = collision211_dense_dual(
            defects.collision211.value, weight, defects.collision211.tangent
        )
        total = {
            key: Dual(
                tree[key].value
                + sparse[key].value
                + (collision211[key].value if key.startswith("k4") else 0.0),
                tree[key].tangent
                + sparse[key].tangent
                + (collision211[key].tangent if key.startswith("k4") else 0.0),
            )
            for key in tree
        }
        base3 = small_source_tensor(tangent.state, 3, terms=24)
        base4 = small_source_tensor(tangent.state, 4, terms=24)
        base = repeated_from_dense(base3, base4, weight)
        epsilon = 1.0e-6
        plus_state = build_state(
            mean + epsilon * mean_dot, covariance + epsilon * covariance_dot
        )
        minus_state = build_state(
            mean - epsilon * mean_dot, covariance - epsilon * covariance_dot
        )
        plus = repeated_from_dense(
            small_source_tensor(plus_state, 3, terms=24),
            small_source_tensor(plus_state, 4, terms=24),
            weight,
        )
        minus = repeated_from_dense(
            small_source_tensor(minus_state, 3, terms=24),
            small_source_tensor(minus_state, 4, terms=24),
            weight,
        )
        for key in total:
            self.assert_close(total[key].value, base[key], 2e-8)
            self.assert_close(
                total[key].tangent,
                (plus[key] - minus[key]) / (2 * epsilon),
                2e-5,
            )

    def test_cost_envelope_has_precise_repair_kill_boundary(self):
        grid = (2, 4, 8, 16, 22)
        mixed = {p: flopscope_cost_envelope(p, dense_dtype="float32") for p in grid}
        full64 = {p: flopscope_cost_envelope(p, dense_dtype="float64") for p in grid}
        self.assertTrue(mixed[2]["strictly_below_100b_even_at_lower_bound"])
        self.assertGreater(mixed[2]["total_upper"], 100_000_000_000)
        for p in grid[1:]:
            self.assertFalse(mixed[p]["strictly_below_100b_even_at_lower_bound"])
        for p in grid:
            self.assertFalse(full64[p]["strictly_below_100b_even_at_lower_bound"])
            self.assertTrue(mixed[p]["co_propagates_without_n4"])
            self.assertFalse(mixed[p]["collision211_dense_tensor_required"])


if __name__ == "__main__":
    unittest.main()

