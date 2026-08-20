from __future__ import annotations

import itertools
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m122_nonzero_bridge_theory",
    "m129_source_frechet_tangent",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m122_nonzero_bridge import (
    build_state,
    direct_gh_raw_moment,
    small_source_tensor,
)
from m129_source_frechet import (
    Dual,
    build_state_frechet,
    triple_raw_moment_series_dot,
)
from m131_trivariate_boundary_stream import (
    antithetic_standard_samples,
    bivariate_relu_raw_dot,
    cholesky_frechet,
    conditional_collision211_defect_dot,
    conditional_triple_relu_raw_dot,
    gaussianized_frame_samples,
    independent_k3_pair_convolution,
    one_delay_edgeworth_source,
    sampled_first_chaos_controlled_source,
    sampled_normal_ordered_source,
    sampled_source_cost_envelope,
)


def generated_state(n: int, seed: int):
    rng = np.random.default_rng(seed)
    factor = np.eye(n) + 0.09 * rng.normal(size=(n, n))
    covariance = factor @ factor.T + 0.45 * np.eye(n)
    mean = rng.normal(scale=0.25, size=n)
    covariance_dot = rng.normal(scale=0.06, size=(n, n))
    covariance_dot = 0.5 * (covariance_dot + covariance_dot.T)
    mean_dot = rng.normal(scale=0.10, size=n)
    return mean, covariance, mean_dot, covariance_dot


def repeated_from_dense(tensor3, tensor4, weight):
    t3 = np.einsum("ijk,ia,jb,kc->abc", tensor3, weight, weight, weight, optimize=True)
    t4 = np.einsum(
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
        "k3_aaa": np.asarray([t3[a, a, a] for a in range(outputs)]),
        "k3_aab": np.asarray([[t3[a, a, b] for b in range(outputs)] for a in range(outputs)]),
        "k4_aaaa": np.asarray([t4[a, a, a, a] for a in range(outputs)]),
        "k4_aaab": np.asarray([[t4[a, a, a, b] for b in range(outputs)] for a in range(outputs)]),
        "k4_aabb": np.asarray([[t4[a, a, b, b] for b in range(outputs)] for a in range(outputs)]),
    }


def tensor_hermite_rule(dimension: int, order: int):
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = np.sqrt(2.0) * nodes
    weights = weights / np.sqrt(np.pi)
    points = []
    point_weights = []
    for indices in itertools.product(range(order), repeat=dimension):
        points.append([nodes[index] for index in indices])
        point_weights.append(np.prod([weights[index] for index in indices]))
    return np.asarray(points), np.asarray(point_weights)


class M131TrivariateBoundaryStreamTests(unittest.TestCase):
    def assert_close(self, left, right, tolerance):
        error = float(np.max(np.abs(np.asarray(left) - np.asarray(right))))
        self.assertLessEqual(error, tolerance)

    def test_bivariate_price_frechet_matches_finite_difference(self):
        mean, covariance, mean_dot, covariance_dot = generated_state(2, 131001)
        value, derivative = bivariate_relu_raw_dot(
            mean, covariance, mean_dot, covariance_dot
        )
        epsilon = 1.0e-6
        plus = bivariate_relu_raw_dot(
            mean + epsilon * mean_dot,
            covariance + epsilon * covariance_dot,
            np.zeros(2),
            np.zeros((2, 2)),
        )[0]
        minus = bivariate_relu_raw_dot(
            mean - epsilon * mean_dot,
            covariance - epsilon * covariance_dot,
            np.zeros(2),
            np.zeros((2, 2)),
        )[0]
        self.assertTrue(np.isfinite(value))
        self.assertAlmostEqual(derivative, (plus - minus) / (2 * epsilon), places=7)

    def test_conditional_triple_value_and_tangent_are_independent_of_series(self):
        mean, covariance, mean_dot, covariance_dot = generated_state(3, 131101)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        conditional = conditional_triple_relu_raw_dot(
            mean,
            covariance,
            mean_dot,
            covariance_dot,
            0,
            1,
            2,
            coarse_order=48,
            fine_order=72,
        )
        selected = np.arange(3)
        series = triple_raw_moment_series_dot(
            tangent.state.alpha[selected],
            tangent.state.sigma[selected],
            (2, 1, 1),
            tangent.state.correlation,
            tangent.alpha_dot[selected],
            tangent.sigma_dot[selected],
            tangent.correlation_dot,
            terms=24,
        )
        # Tensor Gauss-Hermite crosses three ReLU kinks and converges much more
        # slowly than the boundary-split conditional rule.  Order 88 is kept
        # only as an independent, deliberately expensive check.
        independent = direct_gh_raw_moment(mean, covariance, (2, 1, 1), order=88)
        self.assertAlmostEqual(conditional.value, series[0], places=5)
        self.assertLess(abs(conditional.value - independent), 1.0e-4)
        self.assertLess(conditional.value_disagreement, 2e-5)

        epsilon = 8.0e-7
        plus = conditional_triple_relu_raw_dot(
            mean + epsilon * mean_dot,
            covariance + epsilon * covariance_dot,
            np.zeros(3),
            np.zeros((3, 3)),
            0,
            1,
            2,
            coarse_order=48,
            fine_order=72,
        ).value
        minus = conditional_triple_relu_raw_dot(
            mean - epsilon * mean_dot,
            covariance - epsilon * covariance_dot,
            np.zeros(3),
            np.zeros((3, 3)),
            0,
            1,
            2,
            coarse_order=48,
            fine_order=72,
        ).value
        self.assertAlmostEqual(conditional.tangent, (plus - minus) / (2 * epsilon), places=6)
        self.assertAlmostEqual(conditional.tangent, series[1], places=4)

    def test_conditional_defect_agrees_with_hermite_defect(self):
        mean, covariance, mean_dot, covariance_dot = generated_state(3, 131201)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        observed = conditional_collision211_defect_dot(
            tangent, 0, 1, 2, coarse_order=48, fine_order=72
        )
        # The M129 series is independent of the conditional one-dimensional
        # representation and owns the same exact set-partition subtraction.
        from m129_source_frechet import build_collision_defects

        expected = build_collision_defects(tangent, terms=24).collision211
        self.assertAlmostEqual(observed[0], expected.value[0, 1, 2], places=5)
        self.assertAlmostEqual(observed[1], expected.tangent[0, 1, 2], places=4)

    def test_cholesky_frechet_identity_and_finite_difference(self):
        _, covariance, _, covariance_dot = generated_state(5, 131301)
        factor, factor_dot = cholesky_frechet(covariance, covariance_dot)
        self.assert_close(factor @ factor.T, covariance, 3e-13)
        self.assert_close(
            factor_dot @ factor.T + factor @ factor_dot.T,
            covariance_dot,
            3e-13,
        )
        epsilon = 1.0e-6
        finite = (
            np.linalg.cholesky(covariance + epsilon * covariance_dot)
            - np.linalg.cholesky(covariance - epsilon * covariance_dot)
        ) / (2 * epsilon)
        self.assert_close(factor_dot, finite, 2e-9)

    def test_normal_ordered_projected_source_matches_dense_quadrature_oracle(self):
        n = 3
        rng = np.random.default_rng(131401)
        mean, covariance, mean_dot, covariance_dot = generated_state(n, 131402)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        weight = rng.normal(scale=0.45, size=(n, n))
        samples, weights = tensor_hermite_rule(n, 22)
        observed = sampled_normal_ordered_source(
            tangent,
            weight,
            samples,
            sample_weights=weights,
            bank_count=1,
        )
        exact = repeated_from_dense(
            small_source_tensor(tangent.state, 3, terms=24),
            small_source_tensor(tangent.state, 4, terms=24),
            weight,
        )
        # This tensor rule intentionally crosses every activation kink.  Its
        # loose convergence gate is independent of the exact conditional test
        # above; source/tangent algebra is checked at machine precision below.
        for key in exact:
            self.assert_close(observed.repeated[key].value, exact[key], 1.0e-2)
        self.assert_close(
            np.diag(observed.repeated["k4_aaab"].value),
            observed.repeated["k4_aaaa"].value,
            2e-12,
        )
        self.assert_close(
            observed.repeated["k4_aabb"].value,
            observed.repeated["k4_aabb"].value.T,
            2e-12,
        )

    def test_projected_source_pathwise_tangent_matches_fixed_node_difference(self):
        n = 3
        rng = np.random.default_rng(131501)
        mean, covariance, mean_dot, covariance_dot = generated_state(n, 131502)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        weight = rng.normal(scale=0.35, size=(n, n))
        samples, weights = tensor_hermite_rule(n, 12)
        observed = sampled_normal_ordered_source(
            tangent, weight, samples, sample_weights=weights, bank_count=1
        )
        epsilon = 8e-7
        plus_tangent = build_state_frechet(
            mean + epsilon * mean_dot,
            covariance + epsilon * covariance_dot,
            np.zeros(n),
            np.zeros((n, n)),
        )
        minus_tangent = build_state_frechet(
            mean - epsilon * mean_dot,
            covariance - epsilon * covariance_dot,
            np.zeros(n),
            np.zeros((n, n)),
        )
        plus = sampled_normal_ordered_source(
            plus_tangent, weight, samples, sample_weights=weights, bank_count=1
        )
        minus = sampled_normal_ordered_source(
            minus_tangent, weight, samples, sample_weights=weights, bank_count=1
        )
        for key in observed.repeated:
            finite = (plus.repeated[key].value - minus.repeated[key].value) / (2 * epsilon)
            self.assert_close(observed.repeated[key].tangent, finite, 2e-7)

    def test_first_chaos_control_is_zero_mean_and_preserves_tangent(self):
        n = 3
        rng = np.random.default_rng(131551)
        mean, covariance, mean_dot, covariance_dot = generated_state(n, 131552)
        tangent = build_state_frechet(mean, covariance, mean_dot, covariance_dot)
        weight = rng.normal(scale=0.35, size=(n, n))
        # A degree-4 tensor Hermite rule integrates every affine-Gaussian
        # normal-ordered control polynomial exactly, including its tangent.
        samples, weights = tensor_hermite_rule(n, 4)
        observed = sampled_first_chaos_controlled_source(
            tangent,
            weight,
            samples,
            sample_weights=weights,
            bank_count=1,
        )
        for key in observed.affine_control.repeated:
            self.assert_close(observed.affine_control.repeated[key].value, 0.0, 2e-12)
            self.assert_close(observed.affine_control.repeated[key].tangent, 0.0, 3e-12)
            self.assert_close(
                observed.controlled.repeated[key].value,
                observed.uncontrolled.repeated[key].value,
                2e-12,
            )
            self.assert_close(
                observed.controlled.repeated[key].tangent,
                observed.uncontrolled.repeated[key].tangent,
                3e-12,
            )

        epsilon = 8e-7
        plus_tangent = build_state_frechet(
            mean + epsilon * mean_dot,
            covariance + epsilon * covariance_dot,
            np.zeros(n),
            np.zeros((n, n)),
        )
        minus_tangent = build_state_frechet(
            mean - epsilon * mean_dot,
            covariance - epsilon * covariance_dot,
            np.zeros(n),
            np.zeros((n, n)),
        )
        plus = sampled_first_chaos_controlled_source(
            plus_tangent, weight, samples, sample_weights=weights, bank_count=1
        )
        minus = sampled_first_chaos_controlled_source(
            minus_tangent, weight, samples, sample_weights=weights, bank_count=1
        )
        for key in observed.controlled.repeated:
            finite = (
                plus.controlled.repeated[key].value
                - minus.controlled.repeated[key].value
            ) / (2 * epsilon)
            self.assert_close(observed.controlled.repeated[key].tangent, finite, 3e-7)

    def test_one_delay_response_matches_independent_hermite_score(self):
        mean = np.asarray([0.17, -0.23])
        sigma = np.asarray([0.91, 1.14])
        covariance = np.diag(sigma * sigma)
        k3_aaa = np.asarray([0.08, -0.11])
        k3_aab = np.asarray([[k3_aaa[0], 0.047], [-0.036, k3_aaa[1]]])
        k4_aaaa = np.asarray([0.12, -0.07])
        k4_aaab = np.asarray([[k4_aaaa[0], 0.031], [0.043, k4_aaaa[1]]])
        k4_aabb = np.asarray([[k4_aaaa[0], -0.052], [-0.052, k4_aaaa[1]]])
        repeated = {
            "k3_aaa": Dual(k3_aaa, np.zeros_like(k3_aaa)),
            "k3_aab": Dual(k3_aab, np.zeros_like(k3_aab)),
            "k4_aaaa": Dual(k4_aaaa, np.zeros_like(k4_aaaa)),
            "k4_aaab": Dual(k4_aaab, np.zeros_like(k4_aaab)),
            "k4_aabb": Dual(k4_aabb, np.zeros_like(k4_aabb)),
        }
        observed = one_delay_edgeworth_source(repeated, mean, covariance)
        samples, weights = tensor_hermite_rule(2, 96)
        x = mean[None, :] + samples * sigma[None, :]
        activation = np.maximum(x, 0.0)
        g0, g1 = samples[:, 0], samples[:, 1]
        he2_0, he2_1 = g0 * g0 - 1.0, g1 * g1 - 1.0
        he3_0, he3_1 = g0**3 - 3.0 * g0, g1**3 - 3.0 * g1
        he4_0, he4_1 = g0**4 - 6.0 * g0 * g0 + 3.0, g1**4 - 6.0 * g1 * g1 + 3.0
        score3 = (
            k3_aaa[0] * he3_0 / sigma[0] ** 3
            + 3.0 * k3_aab[0, 1] * he2_0 * g1 / (sigma[0] ** 2 * sigma[1])
            + 3.0 * k3_aab[1, 0] * g0 * he2_1 / (sigma[0] * sigma[1] ** 2)
            + k3_aaa[1] * he3_1 / sigma[1] ** 3
        ) / 6.0
        score4 = (
            k4_aaaa[0] * he4_0 / sigma[0] ** 4
            + 4.0 * k4_aaab[0, 1] * he3_0 * g1 / (sigma[0] ** 3 * sigma[1])
            + 6.0 * k4_aabb[0, 1] * he2_0 * he2_1 / (sigma[0] ** 2 * sigma[1] ** 2)
            + 4.0 * k4_aaab[1, 0] * g0 * he3_1 / (sigma[0] * sigma[1] ** 3)
            + k4_aaaa[1] * he4_1 / sigma[1] ** 4
        ) / 24.0
        score = score3 + score4
        mean_response = np.sum(weights[:, None] * activation * score[:, None], axis=0)
        raw_response = activation.T @ (weights[:, None] * activation * score[:, None])
        base_mean = np.sum(weights[:, None] * activation, axis=0)
        central_response = raw_response - np.outer(mean_response, base_mean) - np.outer(base_mean, mean_response)
        # Gauss-Hermite sees a kink; this is deliberately an independent and
        # relatively loose numerical oracle for the analytic boundary jets.
        self.assert_close(observed.mean, mean_response, 6e-5)
        self.assert_close(observed.covariance, central_response, 1.5e-4)

    def test_independent_antithetic_banks_and_cost_are_mechanical(self):
        samples = antithetic_standard_samples(8, 5, 2, 131601)
        self.assertEqual(samples.shape, (32, 5))
        self.assert_close(samples[:8], -samples[8:16], 0.0)
        self.assert_close(samples[16:24], -samples[24:32], 0.0)
        for dtype in ("float32", "float64"):
            previous = 0
            for per_bank in (16, 32, 64, 128, 256):
                ledger = sampled_source_cost_envelope(
                    per_bank, dense_dtype=dtype
                )
                self.assertTrue(ledger["strictly_below_100b"])
                self.assertGreater(ledger["complete_protected_total"], previous)
                previous = ledger["complete_protected_total"]

    def test_gaussianized_frame_geometry_and_cost(self):
        width = 7
        for design, rows, off_diagonal in (
            ("orthobasis", width, 0.0),
            ("simplex", width + 1, -1.0 / width),
        ):
            samples = gaussianized_frame_samples(width, 2, 131651, design=design)
            self.assertEqual(samples.shape, (2 * rows, width))
            for bank in range(2):
                block = samples[bank * rows : (bank + 1) * rows]
                directions = block / np.linalg.norm(block, axis=1)[:, None]
                gram = directions @ directions.T
                self.assert_close(np.diag(gram), 1.0, 5e-15)
                mask = ~np.eye(rows, dtype=bool)
                self.assert_close(gram[mask], off_diagonal, 5e-15)
        for design, samples_per_bank in (("orthobasis", 256), ("simplex", 257)):
            ledger = sampled_source_cost_envelope(
                samples_per_bank,
                dense_dtype="float32",
                first_chaos_control=True,
                gaussianized_design=design,
            )
            self.assertTrue(ledger["strictly_below_100b"])
            self.assertGreater(ledger["haar_setup_f64_upper"], 0)
        antithetic = gaussianized_frame_samples(
            width, 2, 131652, design="orthobasis", antithetic=True
        )
        self.assertEqual(antithetic.shape, (4 * width, width))
        self.assert_close(antithetic[:width], -antithetic[width : 2 * width], 0.0)
        self.assert_close(
            antithetic[2 * width : 3 * width],
            -antithetic[3 * width :],
            0.0,
        )
        ledger = sampled_source_cost_envelope(
            512,
            dense_dtype="float32",
            gaussianized_design="antithetic_orthobasis",
        )
        self.assertTrue(ledger["strictly_below_100b"])

    def test_independent_bank_k3_convolution_has_exact_slot_ownership(self):
        value = np.asarray([[0.7, -0.2], [0.4, -0.5]])
        tangent = np.asarray([[0.03, -0.07], [0.09, 0.02]])
        # Equal deterministic banks reduce the U-statistic to the exact M128
        # binomial convolution; stochastic callers must supply independent
        # banks, which sampled_normal_ordered_source exposes separately.
        observed = independent_k3_pair_convolution(
            (Dual(value, tangent), Dual(value, tangent))
        )
        slots = np.asarray([value[1, 1], value[1, 0], value[0, 1], value[0, 0]])
        slots_dot = np.asarray(
            [tangent[1, 1], tangent[1, 0], tangent[0, 1], tangent[0, 0]]
        )
        binomial = np.asarray([1.0, 3.0, 3.0, 1.0])
        expected = np.zeros(7)
        expected_dot = np.zeros(7)
        for p in range(4):
            for r in range(4):
                factor = binomial[p] * binomial[r]
                expected[p + r] += factor * slots[p] * slots[r]
                expected_dot[p + r] += factor * (
                    slots_dot[p] * slots[r] + slots[p] * slots_dot[r]
                )
        self.assert_close(observed.value[:, 0, 1], expected, 2e-15)
        self.assert_close(observed.tangent[:, 0, 1], expected_dot, 2e-15)


if __name__ == "__main__":
    unittest.main()
