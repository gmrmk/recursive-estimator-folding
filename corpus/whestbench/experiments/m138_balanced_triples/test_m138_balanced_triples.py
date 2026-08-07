"""Small/generated tests for the M138 balanced-design mutation."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m133_ht_hidden_edge",
    "m126_repeated_output_source_contraction",
    "m125_source_batched_forward_tangent",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)
sys.path.insert(0, str(HERE))

from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m133_ht_hidden_edge import (  # noqa: E402
    collision211_factored_proposal,
    collision211_hh_batched,
    collision211_hh_batched_tangent,
)
from m125_forward_tangent import TangentState, tangent_stage  # noqa: E402
from m138_balanced_triples import balanced_factored_draws, balanced_sampling_bill  # noqa: E402
from run_m138_generated import (  # noqa: E402
    _coalesced_response,
    _quadratic_defect,
    build_generated_chain,
    exact_vectorized_repeated_211,
    _final_response,
)


def bridge(width: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.13, size=(width, width))
    answer = 0.5 * (raw + raw.T)
    np.fill_diagonal(answer, 1.0)
    return answer


class BalancedTripleTests(unittest.TestCase):
    def test_vectorized_exact_oracle_matches_canonical_small_reference(self) -> None:
        rng = np.random.default_rng(13801)
        q = bridge(7, 13802)
        weight = rng.normal(size=(7, 5))
        defect = _quadratic_defect(q)
        expected = collision211_repeated_exact(defect, weight)
        observed = exact_vectorized_repeated_211(defect, weight)
        for key in expected:
            self.assertLessEqual(
                float(np.max(np.abs(expected[key] - observed[key]))), 3e-10
            )

    def test_balanced_rows_have_parent_q_marginal_and_no_collisions(self) -> None:
        n, count, designs = 6, 17, 8_000
        rng = np.random.default_rng(13811)
        q = bridge(n, 13812)
        weight = rng.normal(size=(n, 4))
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.05)
        observed = np.zeros((n, n, n), dtype=np.float64)
        centre_counts = np.zeros(n, dtype=np.float64)
        for _ in range(designs):
            draws, audit = balanced_factored_draws(proposal, rng, count, return_audit=True)
            self.assertTrue(np.all([len(set(row.tolist())) == 3 for row in draws]))
            for i, j, k in draws:
                observed[i, j, k] += 1.0
            centre_counts += np.bincount(audit.centres[audit.centres >= 0], minlength=n)
        observed /= designs * count
        expected = np.zeros_like(observed)
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    expected[i, j, k] = proposal.probability(i, j, k)
        # Total variation tests the joint (not just centre) marginal.  It is
        # deliberately loose enough for the unchanged 5% rescue tail.
        self.assertLess(float(0.5 * np.sum(np.abs(observed - expected))), 0.035)
        self.assertEqual(float(np.sum(observed)), 1.0)
        self.assertGreater(float(np.sum(centre_counts)), 0.0)

    def test_balanced_hh_keeps_canonical_pair_gauge_and_collision_ownership(self) -> None:
        n = 7
        rng = np.random.default_rng(13821)
        q = bridge(n, 13822)
        weight = rng.normal(size=(n, 5))
        defect = _quadratic_defect(q)
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.05)
        draws = balanced_factored_draws(proposal, rng, 53)
        for i, j, k in draws:
            self.assertNotEqual(int(i), int(j))
            self.assertNotEqual(int(i), int(k))
            self.assertNotEqual(int(j), int(k))
            self.assertAlmostEqual(float(defect[i, j, k]), float(defect[i, k, j]))
        # The same 1/(2Kq) HH estimator accepts the dependent draws exactly;
        # compare it to a direct manual permutation gauge at a finite sample.
        sample = collision211_hh_batched(
            weight, proposal, draws, lambda i, j, k: float(defect[i, j, k])
        )
        swapped = draws.copy()
        swapped[:, [1, 2]] = swapped[:, [2, 1]]
        reflected = collision211_hh_batched(
            weight, proposal, swapped, lambda i, j, k: float(defect[i, j, k])
        )
        for key in sample:
            self.assertLessEqual(float(np.max(np.abs(sample[key] - reflected[key]))), 4e-10)

    def test_frozen_q_frechet_tangent_needs_no_probability_derivative(self) -> None:
        n = 8
        rng = np.random.default_rng(13831)
        q = bridge(n, 13832)
        weight = rng.normal(size=(n, 6))
        defect = _quadratic_defect(q)
        defect_dot = _quadratic_defect(bridge(n, 13833))
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.05)
        draws = balanced_factored_draws(proposal, rng, 61)
        primal, tangent = collision211_hh_batched_tangent(
            weight,
            proposal,
            draws,
            lambda i, j, k: (float(defect[i, j, k]), float(defect_dot[i, j, k])),
        )
        epsilon = 2e-6
        plus = collision211_hh_batched(
            weight, proposal, draws, lambda i, j, k: float(defect[i, j, k] + epsilon * defect_dot[i, j, k])
        )
        minus = collision211_hh_batched(
            weight, proposal, draws, lambda i, j, k: float(defect[i, j, k] - epsilon * defect_dot[i, j, k])
        )
        for key in primal:
            finite_difference = (plus[key] - minus[key]) / (2.0 * epsilon)
            self.assertLessEqual(float(np.max(np.abs(tangent[key] - finite_difference))), 4e-8)

    def test_complete_m121_m125b_response_equals_explicit_source_sum(self) -> None:
        width, depth = 7, 4
        states, weights, jacobians, bridges = build_generated_chain(width, depth, 13841)
        defects = [_quadratic_defect(item) for item in bridges]
        tables = [exact_vectorized_repeated_211(d, w) for d, w in zip(defects, weights)]
        observed = _final_response(tables, states, weights, jacobians)
        # Reconstruct every post-M121 source then propagate it through the
        # complete suffix explicitly.  This is a small correctness oracle for
        # the M125b output-functional recurrence, not a target algorithm.
        from run_m138_generated import _dual_table
        from m131_trivariate_boundary_stream import one_delay_edgeworth_source
        sources = [
            one_delay_edgeworth_source(_dual_table(table), states[index + 1][0], states[index + 1][1])
            for index, table in enumerate(tables)
        ]
        explicit = TangentState(np.zeros(width), np.zeros((width, width)))
        for source_index, source in enumerate(sources):
            state = source
            for map_index in range(source_index + 1, depth):
                state = tangent_stage(state, weights[map_index], jacobians[map_index])
            explicit = TangentState(
                explicit.mean + state.mean, explicit.covariance + state.covariance
            )
        self.assertLessEqual(float(np.max(np.abs(observed - explicit.mean))), 2e-10)
        # Execute the coalesced map too so the test protects its covariance
        # carrying path, not a scalar response surrogate.
        coalesced = _coalesced_response(sources, weights, jacobians)
        self.assertLessEqual(float(np.max(np.abs(coalesced.mean - explicit.mean))), 2e-10)
        self.assertLessEqual(float(np.max(np.abs(coalesced.covariance - explicit.covariance))), 2e-10)

    def test_balancing_bill_has_no_product_or_catalog_and_fits_remaining_budget(self) -> None:
        bill = balanced_sampling_bill(width=256, count=512, layers=31)
        self.assertEqual(bill["additional_rectangular_products"], 0)
        self.assertEqual(bill["full_triple_catalog_entries"], 0)
        self.assertAlmostEqual(bill["unchanged_uniform_rescue"], 0.05)
        self.assertLess(94.94094024 + bill["protected_increment"] / 1.0e9, 100.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
