"""Generated-only invariant tests for M139's proposal-only mutation."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m126_repeated_output_source_contraction",
    "m133_ht_hidden_edge",
    "m129_source_frechet_tangent",
    "m139_trivariate_proposal",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m133_ht_hidden_edge import (  # noqa: E402
    collision211_hh_batched,
    collision211_hh_batched_tangent,
    collision211_factored_proposal,
)
from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m129_source_frechet import build_state_frechet  # noqa: E402
from m139_trivariate_proposal import (  # noqa: E402
    make_positive_partial_proposal,
    m139_incremental_cost_envelope,
    partial_correlation,
    singularity_subtracted_defect,
)


def bridge(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.10, size=(n, n))
    answer = 0.5 * (raw + raw.T)
    np.fill_diagonal(answer, 1.0)
    return answer


def defect(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    answer = np.zeros((n, n, n))
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                if len({i, j, k}) == 3:
                    value = float(rng.normal())
                    answer[i, j, k] = answer[i, k, j] = value
    return answer


class M139ProposalTests(unittest.TestCase):
    def test_rank_zero_is_exactly_the_m133_three_bank_law(self) -> None:
        n = 7
        q = bridge(n, 139001)
        weight = np.random.default_rng(139002).normal(size=(n, n))
        old = collision211_factored_proposal(q, weight, uniform_mixture=0.05)
        new = make_positive_partial_proposal(
            q, weight, np.zeros(n), np.ones(n), rank=0, uniform_mixture=0.05
        )
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    self.assertAlmostEqual(new.probability(i, j, k), old.probability(i, j, k), places=13)

    def test_normalization_and_empirical_law(self) -> None:
        n = 6
        q = bridge(n, 139011)
        rng = np.random.default_rng(139012)
        weight = rng.normal(size=(n, n))
        proposal = make_positive_partial_proposal(
            q, weight, rng.normal(size=n), np.exp(rng.normal(scale=0.2, size=n)), rank=2
        )
        total = math.fsum(
            proposal.probability(i, j, k)
            for i in range(n)
            for j in range(n)
            for k in range(n)
        )
        self.assertAlmostEqual(total, 1.0, places=12)
        draws = proposal.sample(np.random.default_rng(139013), 80_000)
        for triple in ((0, 1, 2), (4, 0, 3), (2, 5, 1)):
            empirical = float(np.mean(np.all(draws == np.asarray(triple), axis=1)))
            target = proposal.probability(*triple)
            # Ten standard deviations plus a conservative finite-count slack.
            self.assertLess(abs(empirical - target), 0.004 + 10.0 * math.sqrt(target / draws.shape[0]))

    def test_exact_hh_ownership_with_nonzero_latent_bank(self) -> None:
        n = 6
        q = bridge(n, 139021)
        rng = np.random.default_rng(139022)
        weight = rng.normal(size=(n, n))
        source = defect(n, 139023)
        proposal = make_positive_partial_proposal(q, weight, rng.normal(size=n), np.ones(n), rank=2)
        exact = collision211_repeated_exact(source, weight)
        observed = {key: np.zeros_like(value) for key, value in exact.items()}
        # Exhaustion of the declared one-draw law is a deterministic HH proof.
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if len({i, j, k}) != 3:
                        continue
                    p = proposal.probability(i, j, k)
                    draw = np.asarray(((i, j, k),), dtype=np.int64)
                    sample = collision211_hh_batched(weight, proposal, draw, lambda a, b, c: float(source[a, b, c]))
                    for key in observed:
                        observed[key] += p * sample[key]
        for key in exact:
            self.assertLess(float(np.max(np.abs(observed[key] - exact[key]))), 2e-9)

    def test_permutation_and_positive_gauge_covariance(self) -> None:
        n = 7
        q = bridge(n, 139031)
        rng = np.random.default_rng(139032)
        weight = rng.normal(size=(n, n))
        alpha = rng.normal(size=n)
        scale = np.exp(rng.normal(scale=0.25, size=n))
        proposal = make_positive_partial_proposal(q, weight, alpha, scale, rank=3)
        permutation = rng.permutation(n)
        permuted = make_positive_partial_proposal(
            q[np.ix_(permutation, permutation)], weight[permutation], alpha[permutation], scale[permutation], rank=3
        )
        for triple in ((0, 1, 2), (3, 0, 4), (6, 2, 1)):
            mapped = tuple(int(permutation[item]) for item in triple)
            self.assertAlmostEqual(permuted.probability(*triple), proposal.probability(*mapped), places=12)

        gauge = np.exp(rng.normal(scale=0.35, size=n))
        gauged = make_positive_partial_proposal(q, weight / gauge[:, None], alpha, scale * gauge, rank=3)
        for triple in ((0, 1, 2), (3, 0, 4), (6, 2, 1)):
            self.assertAlmostEqual(gauged.probability(*triple), proposal.probability(*triple), places=12)

    def test_partial_boundary_is_finite_and_tied_pivot_selection_falls_back(self) -> None:
        n = 6
        rho = 0.999999
        q = np.full((n, n), rho)
        np.fill_diagonal(q, 1.0)
        # Equicorrelation has a tied degree boundary, so no coordinate-selected
        # latent pivot is allowed; the covariant tree fallback remains valid.
        proposal = make_positive_partial_proposal(q, np.eye(n), np.zeros(n), np.ones(n), rank=3)
        self.assertEqual(proposal.rank_used, 0)
        self.assertTrue(math.isfinite(partial_correlation(q, 0, 1, 2)))
        self.assertTrue(math.isfinite(proposal.probability(0, 1, 2)))
        total = math.fsum(proposal.probability(i, j, k) for i in range(n) for j in range(n) for k in range(n))
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_frozen_proposal_tangent_has_no_probability_derivative(self) -> None:
        n = 6
        q = bridge(n, 139051)
        rng = np.random.default_rng(139052)
        weight = rng.normal(size=(n, n))
        source = defect(n, 139053)
        source_dot = defect(n, 139054)
        proposal = make_positive_partial_proposal(q, weight, rng.normal(size=n), np.ones(n), rank=2)
        draws = proposal.sample(rng, 31)
        primal, tangent = collision211_hh_batched_tangent(
            weight,
            proposal,
            draws,
            lambda i, j, k: (float(source[i, j, k]), float(source_dot[i, j, k])),
        )
        epsilon = 2e-6
        plus = collision211_hh_batched(weight, proposal, draws, lambda i, j, k: float(source[i, j, k] + epsilon * source_dot[i, j, k]))
        minus = collision211_hh_batched(weight, proposal, draws, lambda i, j, k: float(source[i, j, k] - epsilon * source_dot[i, j, k]))
        for key in primal:
            finite = (plus[key] - minus[key]) / (2.0 * epsilon)
            self.assertLess(float(np.max(np.abs(finite - tangent[key]))), 1e-7)

    def test_conditional_oracle_subtracts_owned_quadratic_diagnostic(self) -> None:
        mean = np.asarray((0.17, -0.22, 0.11))
        factor = np.asarray(((1.0, 0.0, 0.0), (0.24, 0.95, 0.0), (-0.12, 0.16, 0.91)))
        covariance = factor @ factor.T
        tangent = build_state_frechet(mean, covariance, np.zeros(3), np.zeros((3, 3)))
        exact, quadratic, residual = singularity_subtracted_defect(tangent, 0, 1, 2)
        self.assertTrue(all(math.isfinite(item) for item in (exact, quadratic, residual)))
        self.assertAlmostEqual(exact, quadratic + residual, places=13)

    def test_target_incremental_cost_stays_under_cap(self) -> None:
        ledger = m139_incremental_cost_envelope()
        self.assertEqual(ledger["component_count"], 15)
        self.assertTrue(ledger["under_five_billion"])
        self.assertLess(float(ledger["protected_billions"]), 5.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
