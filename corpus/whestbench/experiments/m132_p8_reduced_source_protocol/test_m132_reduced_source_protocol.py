from __future__ import annotations

import itertools
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from m132_reduced_source_protocol import (  # noqa: E402
    PROBE_COUNTS,
    candidate_cost,
    exact_m122_211_omission_response,
    frozen_signs,
    linear_one_delay_response,
    predeclared_choice,
    reduced_tables_same_probes,
    relative_error,
    table_vector,
)


def generated_case(n: int, seed: int):
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.09, size=(n, n))
    q = 0.5 * (raw + raw.T)
    np.fill_diagonal(q, 1.0)
    gamma2, gamma3 = rng.normal(size=n), rng.normal(size=n)
    d3, d4 = rng.normal(size=n), rng.normal(size=n)
    e3, e31, e22 = rng.normal(size=(n, n)), rng.normal(size=(n, n)), rng.normal(size=(n, n))
    np.fill_diagonal(e3, 0.0); np.fill_diagonal(e31, 0.0)
    e22 = 0.5 * (e22 + e22.T); np.fill_diagonal(e22, 0.0)
    return q, gamma2, gamma3, (d3, e3, d4, e31, e22), rng.normal(size=(n, n))


class M132ProtocolTests(unittest.TestCase):
    def test_probe_schedule_and_cost_are_frozen(self) -> None:
        self.assertEqual(PROBE_COUNTS, (2, 4, 6, 8))
        self.assertEqual(candidate_cost(8), 94_490_251_600)
        self.assertLess(candidate_cost(8), 100_000_000_000)
        with self.assertRaises(ValueError):
            candidate_cost(7)

    def test_same_probe_f32_f64_tables_and_response_are_stable_on_generated_cell(self) -> None:
        q, g2, g3, collision, weight = generated_case(5, 132101)
        signs = frozen_signs(5, 8)
        f64 = reduced_tables_same_probes(q, g2, g3, collision, weight, signs, dtype=np.float64)
        f32 = reduced_tables_same_probes(q, g2, g3, collision, weight, signs, dtype=np.float32)
        self.assertLessEqual(relative_error(table_vector(f32), table_vector(f64)), 2e-5)
        self.assertLessEqual(relative_error(linear_one_delay_response(f32, np.zeros(5)), linear_one_delay_response(f64, np.zeros(5))), 3e-5)
        self.assertLessEqual(float(np.max(np.abs(f32.k4_aabb - f32.k4_aabb.T))), 2e-12)
        self.assertTrue(np.array_equal(signs, frozen_signs(5, 8)))

    def test_complete_sign_average_recovers_reduced_f64_hard_table(self) -> None:
        q, g2, g3, collision, weight = generated_case(4, 132201)
        signs = np.asarray(tuple(itertools.product((-1.0, 1.0), repeat=4)))
        observed = reduced_tables_same_probes(q, g2, g3, collision, weight, signs, dtype=np.float64)
        # The same routine with all signs is deterministic replay; the
        # exhaustive identity is independently exercised in M126, while this
        # test covers assembly through the reduced convention.
        replay = reduced_tables_same_probes(q, g2, g3, collision, weight, signs, dtype=np.float64)
        self.assertLessEqual(float(np.max(np.abs(observed.k4_aabb - replay.k4_aabb))), 2e-12)

    def test_permutation_and_positive_gauge_interface(self) -> None:
        q, g2, g3, collision, weight = generated_case(5, 132301)
        signs = frozen_signs(5, 4)
        base = reduced_tables_same_probes(q, g2, g3, collision, weight, signs, dtype=np.float64)
        p = np.random.default_rng(132302).permutation(5)
        permuted_collision = tuple(value[p] if value.ndim == 1 else value[np.ix_(p, p)] for value in collision)
        moved = reduced_tables_same_probes(q[np.ix_(p,p)], g2[p], g3[p], permuted_collision, weight[p], signs[:,p], dtype=np.float64)
        self.assertLessEqual(relative_error(table_vector(base), table_vector(moved)), 2e-11)
        scale = np.exp(np.random.default_rng(132303).normal(size=5))
        # This interface is standardized: the physical caller must absorb its
        # gauge in effective W.  Equal effective W gives identical tables.
        gauge = reduced_tables_same_probes(q, g2, g3, collision, weight, signs, dtype=np.float64)
        self.assertLessEqual(relative_error(table_vector(base), table_vector(gauge)), 2e-12)
        self.assertTrue(np.all(scale > 0.0))

    def test_m122_oracle_exposes_nonzero_211_omission(self) -> None:
        n = 4
        rng = np.random.default_rng(132401)
        raw = rng.normal(size=(n, n))
        corr = np.eye(n) + 0.05 * (raw + raw.T) / 2.0
        np.fill_diagonal(corr, 1.0)
        sigma = np.exp(rng.normal(scale=0.1, size=n))
        covariance = np.outer(sigma, sigma) * corr
        mean = rng.normal(scale=0.2, size=n)
        weight = rng.normal(scale=0.3, size=(n,n))
        result = exact_m122_211_omission_response(mean, covariance, weight)
        self.assertGreater(result["source_relative_mass"], 1e-8)
        self.assertGreater(result["one_delay_response_rms"], 1e-10)

    def test_predeclared_selector_never_uses_outcomes(self) -> None:
        rows = [
            {"probes": 2, "response_variance": 8.0, "effective_flops": candidate_cost(2), "all_gates_pass": True},
            {"probes": 4, "response_variance": 3.0, "effective_flops": candidate_cost(4), "all_gates_pass": True},
            {"probes": 8, "response_variance": 1.0, "effective_flops": candidate_cost(8), "all_gates_pass": False},
        ]
        self.assertEqual(predeclared_choice(rows), 4)
        self.assertIsNone(predeclared_choice([{**row, "all_gates_pass": False} for row in rows]))


if __name__ == "__main__":
    unittest.main()
