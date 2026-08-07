from __future__ import annotations

import itertools
import pathlib
import sys
import unittest

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "m126_repeated_output_source_contraction"))

from m126_repeated_output_contractions import (  # noqa: E402
    collision211_repeated_exact,
    collision22_hard_exact,
    path_hard_tables_exact,
)
from m133_ht_hidden_edge import (  # noqa: E402
    collision211_conductance_catalog,
    collision211_exact_from_catalog,
    collision211_feature,
    collision211_factored_proposal,
    collision211_hh_batched,
    collision211_hh_batched_tangent,
    collision211_hh_direct,
    collision211_hollow_probe,
    collision211_ht_sample,
    collision22_conductance_catalog,
    collision22_exact_from_catalog,
    collision22_ht_sample,
    flopscope_ht_ledger,
    path_conductance_catalog,
    path_exact_from_catalog,
    path_feature,
    path_feature_norm_fast,
    path_ht_sample,
    systematic_pps_sample,
    waterfill_inclusion_probabilities,
)


def generated_bridge(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.13, size=(n, n))
    q = 0.5 * (raw + raw.T)
    np.fill_diagonal(q, 1.0)
    return q


def generated_211(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.zeros((n, n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                if len({i, j, k}) == 3:
                    value = float(rng.normal(scale=0.04))
                    out[i, j, k] = value
                    out[i, k, j] = value
    return out


def phase_partition(probabilities: np.ndarray) -> tuple[tuple[float, float], ...]:
    """Intervals on which ordered systematic PPS is constant."""

    cumulative = np.cumsum(probabilities)
    points = {0.0, 1.0}
    for value in cumulative[:-1]:
        fraction = float(value - np.floor(value))
        if 1e-14 < fraction < 1.0 - 1e-14:
            points.add(fraction)
    ordered = sorted(points)
    return tuple(zip(ordered[:-1], ordered[1:]))


class M133HiddenEdgeTests(unittest.TestCase):
    def test_path_edge_partition_matches_m126_hard_residual(self) -> None:
        for n in range(3, 8):
            rng = np.random.default_rng(133100 + n)
            q = generated_bridge(n, 133200 + n)
            gamma2 = rng.normal(size=n)
            weight = rng.normal(size=(n, n))
            catalog = path_conductance_catalog(q, gamma2, weight)
            exact = path_exact_from_catalog(catalog)
            hard = path_hard_tables_exact(q, gamma2, weight)
            expected = (
                2.0 * (hard["residual_self"] + hard["residual_self"].T)
                + 4.0 * hard["residual_cross"]
            )
            self.assertLessEqual(float(np.max(np.abs(exact - expected))), 2e-10)

    def test_fast_path_norm_is_exact(self) -> None:
        n = 7
        rng = np.random.default_rng(133301)
        q = generated_bridge(n, 133302)
        gamma2 = rng.normal(size=n)
        weight = rng.normal(size=(n, n))
        propagated = q @ weight
        for i, j in itertools.combinations(range(n), 2):
            dense = path_feature(propagated, gamma2, weight, i, j)
            fast = path_feature_norm_fast(propagated, gamma2, weight, i, j)
            self.assertAlmostEqual(float(np.linalg.norm(dense)), fast, places=10)

    def test_collision22_edge_partition_matches_m126(self) -> None:
        n = 7
        rng = np.random.default_rng(133401)
        weight = rng.normal(size=(n, n))
        paired = rng.normal(size=(n, n))
        paired = 0.5 * (paired + paired.T)
        np.fill_diagonal(paired, 0.0)
        catalog = collision22_conductance_catalog(paired, weight)
        exact = collision22_exact_from_catalog(catalog)
        expected = collision22_hard_exact(paired, weight)
        self.assertLessEqual(float(np.max(np.abs(exact - expected))), 2e-11)

    def test_collision211_partition_and_norm_bound(self) -> None:
        n, outputs = 7, 5
        rng = np.random.default_rng(133501)
        weight = rng.normal(size=(n, outputs))
        defect = generated_211(n, 133502)
        catalog = collision211_conductance_catalog(defect, weight)
        exact = collision211_exact_from_catalog(catalog)
        expected = collision211_repeated_exact(defect, weight)
        for key in ("k4_aaaa", "k4_aaab", "k4_aabb"):
            self.assertLessEqual(
                float(np.max(np.abs(exact[key] - expected[key]))), 2e-10
            )
        for unit, upper in zip(catalog.units, catalog.feature_norm_upper):
            feature = collision211_feature(weight, *unit)
            true_norm = np.sqrt(
                float(np.sum(feature["k4_aaab"] ** 2))
                + float(np.sum(feature["k4_aabb"] ** 2))
            )
            self.assertLessEqual(true_norm, float(upper) * (1.0 + 2e-12))

    def test_waterfill_and_systematic_pps_have_exact_first_order_inclusion(self) -> None:
        scores = np.asarray([0.2, 3.0, 1.4, 0.7, 2.1, 0.0], dtype=np.float64)
        probabilities = waterfill_inclusion_probabilities(scores, sample_size=3)
        self.assertAlmostEqual(float(np.sum(probabilities)), 3.0, places=13)
        self.assertTrue(np.all(probabilities >= 0.0))
        self.assertTrue(np.all(probabilities <= 1.0))
        observed = np.zeros_like(probabilities)
        for left, right in phase_partition(probabilities):
            phase = 0.5 * (left + right)
            selected = systematic_pps_sample(probabilities, phase=phase)
            self.assertEqual(int(np.sum(selected)), 3)
            observed += (right - left) * selected
        self.assertLessEqual(float(np.max(np.abs(observed - probabilities))), 3e-13)

    def test_systematic_ht_expectation_recovers_each_disjoint_family(self) -> None:
        n = 6
        rng = np.random.default_rng(133601)
        q = generated_bridge(n, 133602)
        gamma2 = rng.normal(size=n)
        weight = rng.normal(size=(n, n))
        paired = rng.normal(size=(n, n))
        paired = 0.5 * (paired + paired.T)
        np.fill_diagonal(paired, 0.0)
        defect = generated_211(n, 133603)

        path_catalog = path_conductance_catalog(q, gamma2, weight)
        collision22_catalog = collision22_conductance_catalog(paired, weight)
        collision211_catalog = collision211_conductance_catalog(defect, weight)

        families = (
            (
                path_catalog,
                4,
                path_exact_from_catalog(path_catalog),
                lambda mask, p: path_ht_sample(path_catalog, p, mask),
            ),
            (
                collision22_catalog,
                5,
                collision22_exact_from_catalog(collision22_catalog),
                lambda mask, p: collision22_ht_sample(collision22_catalog, p, mask),
            ),
        )
        for catalog, size, expected, estimator in families:
            probabilities = waterfill_inclusion_probabilities(catalog.scores, size)
            observed = np.zeros_like(expected)
            for left, right in phase_partition(probabilities):
                mask = systematic_pps_sample(
                    probabilities, phase=0.5 * (left + right)
                )
                observed += (right - left) * estimator(mask, probabilities)
            self.assertLessEqual(float(np.max(np.abs(observed - expected))), 5e-10)

        probabilities = waterfill_inclusion_probabilities(
            collision211_catalog.scores, 8
        )
        expected211 = collision211_exact_from_catalog(collision211_catalog)
        observed211 = {
            key: np.zeros_like(value) for key, value in expected211.items()
        }
        for left, right in phase_partition(probabilities):
            mask = systematic_pps_sample(
                probabilities, phase=0.5 * (left + right)
            )
            sample = collision211_ht_sample(
                collision211_catalog, probabilities, mask
            )
            for key in observed211:
                observed211[key] += (right - left) * sample[key]
        for key in observed211:
            self.assertLessEqual(
                float(np.max(np.abs(observed211[key] - expected211[key]))), 2e-9
            )

    def test_hollow_probe_complete_average_matches_exact_211(self) -> None:
        n = 6
        rng = np.random.default_rng(133701)
        weight = rng.normal(size=(n, n))
        defect = generated_211(n, 133702)
        observed = None
        signs = tuple(itertools.product((-1.0, 1.0), repeat=n))
        for sign in signs:
            sample = collision211_hollow_probe(defect, weight, np.asarray(sign))
            if observed is None:
                observed = {key: np.zeros_like(value) for key, value in sample.items()}
            for key in observed:
                observed[key] += sample[key] / len(signs)
        expected = collision211_repeated_exact(defect, weight)
        assert observed is not None
        for key in observed:
            self.assertLessEqual(
                float(np.max(np.abs(observed[key] - expected[key]))), 3e-10
            )

    def test_factored_three_bank_proposal_is_normalized_and_has_full_support(self) -> None:
        n = 7
        rng = np.random.default_rng(133751)
        q = generated_bridge(n, 133752)
        weight = rng.normal(size=(n, n))
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.05)
        total = 0.0
        for repeated in range(n):
            for left in range(n):
                for right in range(n):
                    if len({repeated, left, right}) == 3:
                        probability = proposal.probability(repeated, left, right)
                        self.assertGreater(probability, 0.0)
                        total += probability
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_factored_sampler_matches_its_declared_distribution(self) -> None:
        n = 6
        rng = np.random.default_rng(133761)
        q = generated_bridge(n, 133762)
        weight = rng.normal(size=(n, n))
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.08)
        draws = proposal.sample(rng, 120_000)
        observed: dict[tuple[int, int, int], int] = {}
        for row in draws:
            unit = tuple(int(item) for item in row)
            observed[unit] = observed.get(unit, 0) + 1
        worst_standardized = 0.0
        for unit, count in observed.items():
            probability = proposal.probability(*unit)
            expected = draws.shape[0] * probability
            worst_standardized = max(
                worst_standardized, abs(count - expected) / np.sqrt(max(expected, 1.0))
            )
        self.assertLess(worst_standardized, 5.5)

    def test_five_batched_products_equal_direct_hh_scatter(self) -> None:
        n, outputs = 8, 6
        rng = np.random.default_rng(133771)
        q = generated_bridge(n, 133772)
        weight = rng.normal(size=(n, outputs))
        defect = generated_211(n, 133773)
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.04)
        draws = proposal.sample(rng, 41)

        def coefficient(i: int, j: int, k: int) -> float:
            return float(defect[i, j, k])

        direct = collision211_hh_direct(weight, proposal, draws, coefficient)
        batched = collision211_hh_batched(weight, proposal, draws, coefficient)
        for key in direct:
            self.assertLessEqual(
                float(np.max(np.abs(direct[key] - batched[key]))), 2e-10
            )

    def test_factored_hh_one_draw_expectation_owns_canonical_211_once(self) -> None:
        n, outputs = 6, 4
        rng = np.random.default_rng(133781)
        q = generated_bridge(n, 133782)
        weight = rng.normal(size=(n, outputs))
        defect = generated_211(n, 133783)
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.07)
        observed = {
            "k4_aaaa": np.zeros(outputs),
            "k4_aaab": np.zeros((outputs, outputs)),
            "k4_aabb": np.zeros((outputs, outputs)),
        }
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if len({i, j, k}) != 3:
                        continue
                    probability = proposal.probability(i, j, k)
                    feature = collision211_feature(weight, i, j, k)
                    scale = float(defect[i, j, k]) / (2.0 * probability)
                    for key in observed:
                        observed[key] += probability * scale * feature[key]
        expected = collision211_repeated_exact(defect, weight)
        for key in observed:
            self.assertLessEqual(
                float(np.max(np.abs(observed[key] - expected[key]))), 3e-10
            )

    def test_frozen_proposal_pathwise_tangent_needs_no_probability_derivative(self) -> None:
        n, outputs = 8, 6
        rng = np.random.default_rng(133791)
        q = generated_bridge(n, 133792)
        weight = rng.normal(size=(n, outputs))
        defect = generated_211(n, 133793)
        defect_dot = generated_211(n, 133794)
        proposal = collision211_factored_proposal(q, weight, uniform_mixture=0.05)
        draws = proposal.sample(rng, 53)

        def dual_coefficient(i: int, j: int, k: int) -> tuple[float, float]:
            return float(defect[i, j, k]), float(defect_dot[i, j, k])

        primal, tangent = collision211_hh_batched_tangent(
            weight, proposal, draws, dual_coefficient
        )
        epsilon = 2e-6
        plus = collision211_hh_batched(
            weight,
            proposal,
            draws,
            lambda i, j, k: float(defect[i, j, k] + epsilon * defect_dot[i, j, k]),
        )
        minus = collision211_hh_batched(
            weight,
            proposal,
            draws,
            lambda i, j, k: float(defect[i, j, k] - epsilon * defect_dot[i, j, k]),
        )
        base = collision211_hh_batched(
            weight, proposal, draws, lambda i, j, k: float(defect[i, j, k])
        )
        for key in primal:
            finite_difference = (plus[key] - minus[key]) / (2.0 * epsilon)
            self.assertLessEqual(float(np.max(np.abs(primal[key] - base[key]))), 2e-11)
            self.assertLessEqual(
                float(np.max(np.abs(tangent[key] - finite_difference))), 3e-8
            )

    def test_target_ledger_hard_caps_work_and_exposes_211_inclusion(self) -> None:
        ledger = flopscope_ht_ledger(
            path_samples=1024,
            collision22_samples=2048,
            collision211_samples=512,
        )
        self.assertTrue(ledger["fixed_size_hard_cap"])
        self.assertTrue(ledger["exact_211_owned"])
        self.assertLess(ledger["collision211_inclusion_fraction"], 1e-4)
        self.assertGreater(ledger["protected_total_with_m125b"], 100_000_000_000)


if __name__ == "__main__":
    unittest.main()
