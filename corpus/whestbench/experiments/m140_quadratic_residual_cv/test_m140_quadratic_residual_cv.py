from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "m126_repeated_output_source_contraction"))

from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m140_quadratic_residual_cv import (  # noqa: E402
    deterministic_jet_partial_tables,
    m140_preexecution_cost_gate,
    ordered_hh_identity,
    physical_effective_weight,
    quadratic_211_coefficient_dot,
    quadratic_211_tensor,
    quadratic_aabb_split_pair_remainder,
    residual_hh_tangent_identity,
    split_exact_211,
    standardize_211_tensor,
    standardize_211_tensor_dot,
)


def bridge(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.10, size=(n, n))
    answer = 0.5 * (raw + raw.T)
    np.fill_diagonal(answer, 1.0)
    return answer


class M140QuadraticResidualTests(unittest.TestCase):
    def test_exact_partition_has_no_unowned_slots(self) -> None:
        n = 5
        q = bridge(n, 140001)
        exact = np.zeros((n, n, n))
        rng = np.random.default_rng(140002)
        for i in range(n):
            for j in range(n):
                for k in range(j + 1, n):
                    if len({i, j, k}) == 3:
                        exact[i, j, k] = exact[i, k, j] = rng.normal()
        part = split_exact_211(exact, q)
        self.assertLessEqual(float(np.max(np.abs(exact - (part.jet + part.residual)))), 2e-14)
        self.assertTrue(np.all(part.jet[np.arange(n), np.arange(n), :] == 0.0))

    def test_quadratic_tangent_matches_central_difference(self) -> None:
        q = bridge(5, 140101)
        rng = np.random.default_rng(140102)
        dot = rng.normal(scale=0.04, size=(5, 5))
        dot = 0.5 * (dot + dot.T)
        np.fill_diagonal(dot, 0.0)
        value, derivative = quadratic_211_coefficient_dot(q, dot, 0, 1, 2)
        eps = 1e-6
        observed = (quadratic_211_tensor(q + eps * dot)[0, 1, 2] - quadratic_211_tensor(q - eps * dot)[0, 1, 2]) / (2.0 * eps)
        self.assertGreater(abs(value), 0.0)
        self.assertLessEqual(abs(derivative - observed), 2e-10)

    def test_physical_standardization_and_scale_tangent_are_exact(self) -> None:
        n = 5
        q = bridge(n, 140151)
        standardized = quadratic_211_tensor(q)
        rng = np.random.default_rng(140152)
        scale = np.exp(rng.normal(size=n))
        scale_dot = rng.normal(scale=0.08, size=n)
        physical = np.zeros_like(standardized)
        physical_dot = np.zeros_like(standardized)
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if len({i, j, k}) == 3:
                        factor = scale[i] ** 2 * scale[j] * scale[k]
                        log_dot = 2.0 * scale_dot[i] / scale[i] + scale_dot[j] / scale[j] + scale_dot[k] / scale[k]
                        physical[i, j, k] = factor * standardized[i, j, k]
                        physical_dot[i, j, k] = factor * standardized[i, j, k] * log_dot
        observed, observed_dot = standardize_211_tensor_dot(physical, physical_dot, scale, scale_dot)
        self.assertLessEqual(float(np.max(np.abs(standardize_211_tensor(physical, scale) - standardized))), 3e-14)
        self.assertLessEqual(float(np.max(np.abs(observed - standardized))), 3e-14)
        self.assertLessEqual(float(np.max(np.abs(observed_dot))), 3e-14)

    def test_aaab_and_aaaa_are_exact_but_aabb_has_a_nonzero_split_remainder(self) -> None:
        q = bridge(6, 140201)
        w = np.random.default_rng(140202).normal(size=(6, 4))
        jet = quadratic_211_tensor(q)
        reference = collision211_repeated_exact(jet, w)
        partial = deterministic_jet_partial_tables(q, w)
        self.assertLessEqual(float(np.max(np.abs(reference["k4_aaab"] - partial["k4_aaab"]))), 4e-11)
        self.assertLessEqual(float(np.max(np.abs(reference["k4_aaaa"] - partial["k4_aaaa"]))), 4e-11)
        remainder = quadratic_aabb_split_pair_remainder(q, w)
        self.assertGreater(float(np.linalg.norm(remainder)), 1e-8)
        self.assertLessEqual(
            float(np.max(np.abs(reference["k4_aabb"] - (partial["k4_aabb_repeated_pair"] + remainder)))),
            4e-11,
        )

    def test_ordered_hh_identity_is_the_exact_residual_transport(self) -> None:
        q = bridge(5, 140301)
        jet = quadratic_211_tensor(q)
        rng = np.random.default_rng(140302)
        residual = np.zeros_like(jet)
        for i in range(5):
            for j in range(5):
                for k in range(j + 1, 5):
                    if len({i, j, k}) == 3:
                        residual[i, j, k] = residual[i, k, j] = rng.normal(scale=0.3)
        w = rng.normal(size=(5, 3))
        expected = collision211_repeated_exact(residual, w)
        actual = ordered_hh_identity(residual, w)
        for key in actual:
            self.assertLessEqual(float(np.max(np.abs(actual[key] - expected[key]))), 5e-11)

    def test_permutation_and_positive_gauge_covariance(self) -> None:
        q = bridge(6, 140401)
        rng = np.random.default_rng(140402)
        w = rng.normal(size=(6, 4))
        scales = np.exp(rng.normal(size=6))
        effective = physical_effective_weight(scales, w)
        base = deterministic_jet_partial_tables(q, effective)
        perm = rng.permutation(6)
        permuted = deterministic_jet_partial_tables(q[np.ix_(perm, perm)], effective[perm])
        gauge = np.exp(rng.normal(size=6))
        gauged = deterministic_jet_partial_tables(q, physical_effective_weight(scales * gauge, w / gauge[:, None]))
        for key in base:
            self.assertLessEqual(float(np.max(np.abs(base[key] - permuted[key]))), 5e-11)
            self.assertLessEqual(float(np.max(np.abs(base[key] - gauged[key]))), 5e-11)

    def test_preexecution_cost_gate_is_closed(self) -> None:
        gate = m140_preexecution_cost_gate()
        self.assertEqual(gate["protected_lower_worksheet"], 5_190_778_880)
        self.assertFalse(gate["under_incremental_cap"])
        self.assertFalse(gate["full_aabb_split_pair_deterministic_verified"])
        self.assertIn("fixed q0", residual_hh_tangent_identity())


if __name__ == "__main__":
    unittest.main()
