from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m146_pilot_adaptive_hh import (  # noqa: E402
    CertifiedCoefficient,
    Defensive211Mixture,
    EndpointProviderUnavailable,
    FadingFields,
    M146ContractError,
    PremiseRecord,
    RoleAware211Proposal,
    UnresolvedBaselineVariance,
    complete_phase_tail_population,
    concatenate_phase_batch,
    evaluate_all_family_gates,
    exact_rmain,
    exact_trace_variance,
    feature_norm_211_gram,
    feature_norm_211_gram_batch,
    fit_defensive_mixture,
    fit_fading_fields,
    heterogeneous_collision211_batched,
    heterogeneous_collision211_direct,
    make_adapted_proposal,
    make_base_proposal,
    pilot_scores,
    pooled_complete_phase_p99_ratio,
    proposal_probabilities,
    proposal_snapshot_digest,
    require_endpoint_provider,
    validate_protocol_completeness,
    weighted_quantile_lower_cdf,
)


def ordered_units(width: int) -> np.ndarray:
    return np.asarray(
        [
            (i, j, k)
            for i in range(width)
            for j in range(width)
            for k in range(width)
            if len({i, j, k}) == 3
        ],
        dtype=np.int64,
    )


def dense_feature(weight: np.ndarray, i: int, j: int, k: int) -> tuple[np.ndarray, np.ndarray]:
    x, y, z = weight[i], weight[j], weight[k]
    f31 = (
        6.0 * np.outer(x * y * z, x)
        + 3.0 * np.outer(x * x * z, y)
        + 3.0 * np.outer(x * x * y, z)
    )
    f22 = (
        2.0 * np.outer(x * x, y * z)
        + 2.0 * np.outer(y * z, x * x)
        + 4.0 * np.outer(x * y, x * z)
        + 4.0 * np.outer(x * z, x * y)
    )
    return f31, f22


def random_base(width: int, outputs: int, seed: int = 1) -> tuple[RoleAware211Proposal, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.12, size=(width, width))
    bridge = 0.5 * (raw + raw.T)
    np.fill_diagonal(bridge, 1.0)
    source_scale = rng.uniform(0.2, 1.3, size=width)
    weight = rng.normal(scale=0.4, size=(width, outputs))
    return make_base_proposal(bridge, source_scale, weight), bridge, source_scale, weight


class TestRoleAwareProposal(unittest.TestCase):
    def test_exhaustive_normalizers_probabilities_and_singleton_exchange(self) -> None:
        base, _, _, _ = random_base(5, 4, 10)
        units = ordered_units(5)
        masses = np.asarray([base.structured_mass(*map(int, row)) for row in units])
        probabilities = proposal_probabilities(base, units)
        self.assertAlmostEqual(float(np.sum(masses)), base.structured_normalizer, places=11)
        self.assertAlmostEqual(float(np.sum(probabilities)), 1.0, places=13)
        self.assertGreaterEqual(float(np.min(probabilities)), 0.05 / base.ordered_population)
        for i, j, k in units:
            self.assertAlmostEqual(base.structured_mass(int(i), int(j), int(k)), base.structured_mass(int(i), int(k), int(j)), places=15)
            self.assertAlmostEqual(base.probability(int(i), int(j), int(k)), base.probability(int(i), int(k), int(j)), places=15)

    def test_uniform_and_partial_degenerate_semantics(self) -> None:
        width = 4
        zero = np.zeros(width)
        edge = np.zeros((width, width))
        degenerate = RoleAware211Proposal(zero, zero, edge, edge)
        units = ordered_units(width)
        probabilities = proposal_probabilities(degenerate, units)
        self.assertTrue(np.all(probabilities == 1.0 / units.shape[0]))
        self.assertEqual(degenerate.effective_uniform_weight, 1.0)
        draws = degenerate.sample(np.random.default_rng(22), 1000)
        self.assertTrue(np.all([len(set(map(int, row))) == 3 for row in draws]))

        live, _, _, _ = random_base(width, 3, 11)
        mixture = Defensive211Mixture(degenerate, live, 0.25)
        self.assertAlmostEqual(mixture.effective_uniform_weight, 0.25 + 0.75 * 0.05)
        self.assertEqual(mixture.guaranteed_uniform_weight, 0.05)
        self.assertAlmostEqual(float(np.sum(proposal_probabilities(mixture, units))), 1.0, places=13)

    def test_empirical_sampler_frequency_and_zero_bank(self) -> None:
        base, _, _, _ = random_base(4, 3, 12)
        units = ordered_units(4)
        expected = proposal_probabilities(base, units)
        lookup = {tuple(map(int, row)): pos for pos, row in enumerate(units)}
        draws = base.sample(np.random.default_rng(1201), 80_000)
        counts = np.zeros(units.shape[0], dtype=np.int64)
        for row in draws:
            counts[lookup[tuple(map(int, row))]] += 1
        observed = counts / counts.sum()
        self.assertLess(float(np.max(np.abs(observed - expected))), 0.006)

        # Only repeated-centre stars are live; the sampler must never attempt a
        # zero B/C bank.
        star = np.ones((4, 4)) - np.eye(4)
        no_singleton_edge = np.zeros((4, 4))
        proposal = RoleAware211Proposal(np.ones(4), np.ones(4), star, no_singleton_edge)
        self.assertGreater(proposal.z_a, 0.0)
        self.assertEqual(proposal.z_b, 0.0)
        self.assertEqual(proposal.z_c, 0.0)
        sampled = proposal.sample(np.random.default_rng(99), 500)
        self.assertTrue(np.all([len(set(map(int, row))) == 3 for row in sampled]))

    def test_nonfinite_collision_and_bad_inputs_fail_closed(self) -> None:
        base, bridge, scale, weight = random_base(4, 3, 13)
        with self.assertRaises(M146ContractError):
            make_base_proposal(bridge, np.array([1.0, np.nan, 1.0, 1.0]), weight)
        bad_edge = base.repeated_singleton_edge.copy()
        bad_edge[0, 1] = np.nan
        with self.assertRaises(M146ContractError):
            RoleAware211Proposal(base.repeated_strength, base.singleton_strength, bad_edge, base.singleton_singleton_edge)
        self.assertEqual(base.probability(0, 0, 1), 0.0)
        with self.assertRaises(IndexError):
            base.probability(-1, 1, 2)


class TestPilotAndFeatures(unittest.TestCase):
    def test_exact_t_index_all_zero_duplicates_and_shuffle(self) -> None:
        rho = 0.75
        probabilities = np.full(4, 0.1)
        zero = pilot_scores(np.zeros(4), probabilities, rho=rho)
        np.testing.assert_allclose(zero.age_weights, [rho**3, rho**2, rho, 1.0], rtol=0.0, atol=0.0)
        self.assertTrue(zero.all_zero)
        self.assertTrue(np.all(zero.centered_scores == 0.0))

        draws = np.asarray([(0, 1, 2), (0, 1, 2), (2, 3, 1), (3, 0, 2)])
        fields = fit_fading_fields(draws, zero, width=4)
        self.assertTrue(np.all(fields.repeated_node == 0.0))
        self.assertTrue(np.all(fields.repeated_singleton_edge == 0.0))

        scores = pilot_scores(np.asarray([1.0, 2.0, 4.0, 8.0]), probabilities, rho=rho)
        identity = fit_fading_fields(draws, scores, width=4, score_permutation=np.arange(4))
        direct = fit_fading_fields(draws, scores, width=4)
        np.testing.assert_array_equal(identity.repeated_node, direct.repeated_node)
        shuffled = fit_fading_fields(draws, scores, width=4, score_permutation=np.asarray([3, 2, 1, 0]))
        self.assertFalse(np.array_equal(shuffled.repeated_node, direct.repeated_node))
        with self.assertRaises(M146ContractError):
            pilot_scores(np.asarray([1.0, np.nan]), np.asarray([0.2, 0.2]))
        with self.assertRaises(M146ContractError):
            fit_fading_fields(draws, scores, width=4, score_permutation=np.asarray([0, 0, 2, 3]))

    def test_gram_norm_matches_dense_and_extreme_finite_scales(self) -> None:
        rng = np.random.default_rng(21)
        weight = rng.normal(size=(6, 7))
        draws = np.asarray([(0, 1, 2), (3, 5, 1), (4, 2, 0), (1, 0, 5)])
        actual64 = feature_norm_211_gram_batch(weight, draws, arithmetic_dtype=np.float64)
        expected = []
        for i, j, k in draws:
            f31, f22 = dense_feature(weight, int(i), int(j), int(k))
            expected.append(math.sqrt(float(np.sum(f31 * f31) + np.sum(f22 * f22))))
        np.testing.assert_allclose(actual64, expected, rtol=3e-14, atol=3e-13)
        actual32 = feature_norm_211_gram_batch(weight.astype(np.float32), draws, arithmetic_dtype=np.float32)
        np.testing.assert_allclose(actual32, expected, rtol=4e-6, atol=4e-5)
        self.assertAlmostEqual(feature_norm_211_gram(weight, 0, 1, 2), expected[0], places=11)

        gauges = np.asarray([1e-3, 1e3, 0.2, 5.0, 2.0, 0.5])
        transformed = weight / gauges[:, None]
        for row, original in zip(draws, actual64, strict=True):
            i, j, k = map(int, row)
            factor = gauges[i] ** 2 * gauges[j] * gauges[k]
            transformed_norm = feature_norm_211_gram(transformed, i, j, k)
            self.assertAlmostEqual(transformed_norm * factor / original, 1.0, places=10)

    def test_neutral_fit_and_factor_bounds(self) -> None:
        base, _, _, _ = random_base(6, 4, 22)
        pilot = base.sample(np.random.default_rng(2201), 8)
        neutral, scores, fields = fit_defensive_mixture(base, pilot, np.zeros(8))
        self.assertTrue(scores.all_zero)
        units = ordered_units(6)
        np.testing.assert_array_equal(
            proposal_probabilities(neutral.adaptive, units), proposal_probabilities(base, units)
        )
        self.assertEqual(neutral.effective_uniform_weight, 0.05)

        magnitudes = np.geomspace(1e-9, 1e9, 8)
        learned, _, learned_fields = fit_defensive_mixture(base, pilot, magnitudes)
        for field in (
            learned_fields.repeated_node,
            learned_fields.singleton_node,
            learned_fields.repeated_singleton_edge,
            learned_fields.singleton_singleton_edge,
        ):
            self.assertLessEqual(float(np.max(np.abs(field))), 1.0 + 1e-15)
        ratio = learned.adaptive.repeated_strength / base.repeated_strength
        self.assertGreaterEqual(float(np.min(ratio)), 0.5)
        self.assertLessEqual(float(np.max(ratio)), 2.0)


class TestBatchingAndSymmetry(unittest.TestCase):
    def test_heterogeneous_five_product_dense_parity(self) -> None:
        rng = np.random.default_rng(31)
        base, _, _, weight = random_base(7, 5, 31)
        pilot = base.sample(rng, 4)
        magnitudes = np.asarray([0.2, 1.1, 0.7, 2.4])
        mixture, _, _ = fit_defensive_mixture(base, pilot, magnitudes)
        main = mixture.sample(rng, 10)
        pilot_coefficient = rng.normal(size=4)
        main_coefficient = rng.normal(size=10)
        draws, scales = concatenate_phase_batch(
            base, mixture, pilot, pilot_coefficient, main, main_coefficient
        )
        batched = heterogeneous_collision211_batched(weight, draws, scales)
        direct = heterogeneous_collision211_direct(weight, draws, scales)
        for key in batched:
            np.testing.assert_allclose(batched[key], direct[key], rtol=2e-13, atol=3e-13)

    def test_exhaustive_conditional_expectation_and_variance_identity(self) -> None:
        base, _, _, weight = random_base(4, 3, 32)
        units = ordered_units(4)
        rng = np.random.default_rng(3201)
        raw = rng.normal(size=(4, 4, 4))
        coefficient = np.empty(units.shape[0])
        for position, (i, j, k) in enumerate(units):
            coefficient[position] = 0.5 * (raw[i, j, k] + raw[i, k, j])
        pilot = units[[0, 4, 9]]
        pilot_magnitude = np.abs(coefficient[[0, 4, 9]]) * feature_norm_211_gram_batch(weight, pilot)
        mixture, _, _ = fit_defensive_mixture(base, pilot, pilot_magnitude)
        q0 = proposal_probabilities(base, units)
        q1 = proposal_probabilities(mixture, units)

        target = {key: np.zeros_like(value) for key, value in heterogeneous_collision211_direct(weight, units[:1], np.ones(1)).items()}
        for row, value in zip(units, coefficient, strict=True):
            feature = heterogeneous_collision211_direct(weight, row[None, :], np.asarray([0.5 * value]))
            for key in target:
                target[key] += feature[key]
        for probability in (q0, q1):
            expected = heterogeneous_collision211_direct(
                weight, units, coefficient / (2.0 * probability) * probability
            )
            for key in target:
                np.testing.assert_allclose(expected[key], target[key], rtol=2e-13, atol=4e-13)

        norm_sq = []
        for row, value in zip(units, coefficient, strict=True):
            f31, f22 = dense_feature(weight, *map(int, row))
            norm_sq.append(value * value * float(np.sum(f31 * f31) + np.sum(f22 * f22)))
        target_norm = float(np.sum(target["k4_aaab"] ** 2) + np.sum(target["k4_aabb"] ** 2))
        exact = exact_rmain(np.asarray(norm_sq), target_norm, q0, q1)
        self.assertAlmostEqual(exact["ratio"], exact["adaptive_variance"] / exact["base_variance"])
        f = 0.125
        total_ratio = f + (1.0 - f) * exact["ratio"]
        self.assertAlmostEqual(total_ratio, (f * exact["base_variance"] + (1.0 - f) * exact["adaptive_variance"]) / exact["base_variance"])

    def test_gauge_permutation_and_singleton_invariance(self) -> None:
        base, bridge, scale, weight = random_base(6, 5, 33)
        draws = base.sample(np.random.default_rng(3301), 12)
        coefficient = np.linspace(-1.0, 2.0, draws.shape[0])
        magnitude = np.abs(coefficient) * feature_norm_211_gram_batch(weight, draws)
        mixture, _, _ = fit_defensive_mixture(base, draws, magnitude)

        gauge = np.asarray([0.2, 2.0, 0.5, 4.0, 1.5, 0.8])
        base_g = make_base_proposal(bridge, gauge * scale, weight / gauge[:, None])
        factor = gauge[draws[:, 0]] ** 2 * gauge[draws[:, 1]] * gauge[draws[:, 2]]
        coefficient_g = coefficient * factor
        magnitude_g = np.abs(coefficient_g) * feature_norm_211_gram_batch(weight / gauge[:, None], draws)
        mix_g, _, _ = fit_defensive_mixture(base_g, draws, magnitude_g)
        for row in ordered_units(6):
            np.testing.assert_allclose(
                [base.probability(*map(int, row)), mixture.probability(*map(int, row))],
                [base_g.probability(*map(int, row)), mix_g.probability(*map(int, row))],
                rtol=3e-13,
                atol=3e-15,
            )
        q = np.asarray([mixture.probability(*map(int, row)) for row in draws])
        qg = np.asarray([mix_g.probability(*map(int, row)) for row in draws])
        original = heterogeneous_collision211_batched(weight, draws, coefficient / (2 * len(draws) * q))
        gauged = heterogeneous_collision211_batched(weight / gauge[:, None], draws, coefficient_g / (2 * len(draws) * qg))
        for key in original:
            np.testing.assert_allclose(original[key], gauged[key], rtol=2e-12, atol=2e-12)

        permutation = np.asarray([3, 0, 5, 1, 4, 2])
        inverse = np.empty_like(permutation)
        inverse[permutation] = np.arange(permutation.size)
        permuted_draws = inverse[draws]
        base_p = make_base_proposal(
            bridge[np.ix_(permutation, permutation)], scale[permutation], weight[permutation]
        )
        mix_p, _, _ = fit_defensive_mixture(base_p, permuted_draws, magnitude)
        for row in ordered_units(6):
            mapped = inverse[row]
            self.assertAlmostEqual(
                mixture.probability(*map(int, row)),
                mix_p.probability(*map(int, mapped)),
                places=13,
            )
            self.assertAlmostEqual(
                mixture.probability(*map(int, row)),
                mixture.probability(int(row[0]), int(row[2]), int(row[1])),
                places=15,
            )


class TestMetricsProtocolAndEndpoint(unittest.TestCase):
    def test_exact_rmain_zero_resolution_and_tail_convention(self) -> None:
        q0 = np.asarray([0.2, 0.3, 0.5])
        q1 = np.asarray([0.3, 0.3, 0.4])
        norm_sq = np.asarray([1.0, 4.0, 2.0])
        target = 0.7
        same = exact_rmain(norm_sq, target, q0, q0)
        self.assertAlmostEqual(same["ratio"], 1.0)
        candidate, baseline = complete_phase_tail_population(norm_sq, q0, q1)
        ratio = pooled_complete_phase_p99_ratio([candidate], [baseline])
        self.assertGreater(ratio, 0.0)
        self.assertEqual(weighted_quantile_lower_cdf([1, 2, 3], [0.2, 0.3, 0.5], 0.5), 2.0)

        second = float(np.sum(norm_sq / (4.0 * q0)))
        variance, _ = exact_trace_variance(norm_sq, second, q0)
        self.assertEqual(variance, 0.0)
        with self.assertRaises(UnresolvedBaselineVariance):
            exact_rmain(norm_sq, second, q0, q1)

    def test_complete_family_gate_recomputation_and_fail_closed_cases(self) -> None:
        families = ("diagonal", "iid_he")
        widths = (12, 16)
        seeds = (146701,)
        records = []
        for family in families:
            for width in widths:
                for repetition in range(2):
                    records.append(
                        PremiseRecord(
                            family,
                            width,
                            seeds[0],
                            repetition,
                            2.0,
                            2.2,
                            1.0,
                            1.6,
                            4.0,
                            2.0,
                        )
                    )
        result = evaluate_all_family_gates(
            records,
            families=families,
            widths=widths,
            cell_seeds=seeds,
            repetitions=2,
            p99_ratios={"pooled": 1.0, "diagonal": 1.0, "iid_he": 1.0},
        )
        self.assertTrue(result["all_pass"])
        self.assertAlmostEqual(result["pooled"]["primary_ratio"], 0.5)
        self.assertAlmostEqual(result["pooled"]["attribution_ratio"], 0.625)
        self.assertAlmostEqual(result["pooled"]["rmain_ratio_of_summed_exact_variances"], 0.5)

        with self.assertRaises(M146ContractError):
            validate_protocol_completeness(
                records[:-1], families=families, widths=widths, cell_seeds=seeds, repetitions=2
            )
        with self.assertRaises(M146ContractError):
            validate_protocol_completeness(
                records + [records[0]], families=families, widths=widths, cell_seeds=seeds, repetitions=2
            )
        killed = evaluate_all_family_gates(
            records,
            families=families,
            widths=widths,
            cell_seeds=seeds,
            repetitions=2,
            p99_ratios={"pooled": 1.26, "diagonal": 1.0, "iid_he": 1.0},
        )
        self.assertFalse(killed["all_pass"])

    def test_endpoint_interface_is_locked_and_certificate_validation(self) -> None:
        with self.assertRaises(EndpointProviderUnavailable):
            require_endpoint_provider(None)

        class Unsafe:
            provider_id = "unsafe"
            endpoint_safe = False
            arithmetic_dtype = "float64"

            def build_cell(self, **kwargs):  # pragma: no cover - never called
                raise AssertionError

            def coefficient(self, *args):  # pragma: no cover - never called
                raise AssertionError

        with self.assertRaises(EndpointProviderUnavailable):
            require_endpoint_provider(Unsafe())
        digest = "a" * 64
        value = CertifiedCoefficient(1.0, 1.0, 1.0, digest)
        self.assertEqual(value.certificate_digest, digest)
        with self.assertRaises(M146ContractError):
            CertifiedCoefficient(1.0, 1.0, np.nan, digest)

    def test_snapshot_digest_changes_with_adaptation(self) -> None:
        base, _, _, weight = random_base(5, 4, 41)
        pilot = base.sample(np.random.default_rng(4101), 5)
        magnitude = feature_norm_211_gram_batch(weight, pilot)
        mixture, _, _ = fit_defensive_mixture(base, pilot, magnitude)
        self.assertEqual(len(proposal_snapshot_digest(base)), 64)
        self.assertNotEqual(proposal_snapshot_digest(base), proposal_snapshot_digest(mixture))


if __name__ == "__main__":
    unittest.main()
