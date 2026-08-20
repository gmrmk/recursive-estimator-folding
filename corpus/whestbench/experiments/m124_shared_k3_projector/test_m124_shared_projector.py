"""Target-free algebra and invariance tests for M124; no frozen grid."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

from m124_protocol import INCREMENTAL_CEILING, adjudicate, draft_manifest, static_cost_ledger
from m124_shared_projector import (
    M124FailClosed,
    _univariate_raw_positive_moment,
    bivariate_positive_moments,
    build_nonzero_bridge_source,
    edgeworth_delay_one,
    local_vertices,
    physical_source,
    project_source,
    projected_core3,
    projected_core4,
    reconstruct,
    repeated_output_k4_relative,
    shared_projector,
    transport_dense,
    transport_projected,
    weighted_tree3,
    weighted_tree3_mode_gram,
)


def generated_state(n: int, seed: int, alpha_scale: float = 0.3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.Generator(np.random.Philox(seed))
    a = rng.normal(size=(n, n)) / math.sqrt(n)
    covariance = a @ a.T + 0.8 * np.eye(n)
    covariance = 0.5 * (covariance + covariance.T)
    mean = alpha_scale * np.sqrt(np.diag(covariance)) * rng.normal(size=n)
    weight = rng.normal(0.0, math.sqrt(2.0 / n), size=(n, n))
    return mean, covariance, weight


def projector_matrix(u: np.ndarray) -> np.ndarray:
    return u @ u.T


class M124SharedProjectorTests(unittest.TestCase):
    def test_analytic_collision_moment_jet_independence_and_swap(self) -> None:
        for alpha, beta in ((-0.7, 0.2), (0.0, 0.0), (0.4, 1.1)):
            independent = bivariate_positive_moments(alpha, beta, 0.0)
            for p in range(5):
                for q in range(5 - p):
                    expected = (
                        _univariate_raw_positive_moment(alpha, p)
                        * _univariate_raw_positive_moment(beta, q)
                    )
                    self.assertLessEqual(abs(float(independent[p, q]) - expected), 2e-12)

        for alpha, beta, rho in ((-0.6, 0.9, -0.45), (0.25, -0.4, 0.7)):
            forward = bivariate_positive_moments(alpha, beta, rho)
            reverse = bivariate_positive_moments(beta, alpha, rho)
            for p in range(5):
                for q in range(5 - p):
                    self.assertLessEqual(abs(float(forward[p, q]) - float(reverse[q, p])), 2e-12)

        # Independent one-dimensional conditional integration checks the MGF
        # chain rule away from rho=0 without reusing its quadrant derivatives.
        alpha, beta, rho = 0.25, -0.4, 0.7
        analytic = bivariate_positive_moments(alpha, beta, rho)
        nodes, weights = np.polynomial.legendre.leggauss(192)
        upper = alpha + 12.0
        x = 0.5 * upper * (nodes + 1.0)
        w = 0.5 * upper * weights
        density_x = np.exp(-0.5 * (x - alpha) ** 2) / math.sqrt(2.0 * math.pi)
        conditional_scale = math.sqrt(1.0 - rho * rho)
        conditional_alpha = (beta + rho * (x - alpha)) / conditional_scale
        for p, q in ((1, 1), (2, 1), (1, 2), (3, 1), (2, 2), (1, 3)):
            conditional = np.asarray(
                [conditional_scale**q * _univariate_raw_positive_moment(float(a), q) for a in conditional_alpha]
            )
            reference = float(np.sum(w * (x**p) * density_x * conditional))
            self.assertLessEqual(abs(float(analytic[p, q]) - reference), 2e-11)

    def test_weighted_k3_mode_gram_formula_n2_to_n8(self) -> None:
        worst = 0.0
        for n in range(2, 9):
            rng = np.random.Generator(np.random.Philox(1_249_000 + n))
            raw = rng.normal(size=(n, n))
            q = raw @ raw.T
            d = np.sqrt(np.diag(q))
            q = q / np.outer(d, d)
            np.fill_diagonal(q, 1.0)
            gamma = rng.uniform(0.3, 2.0, size=n)
            tensor = weighted_tree3(q, gamma)
            flat = tensor.reshape(n, -1)
            dense = flat @ flat.T
            formula = weighted_tree3_mode_gram(q, gamma)
            worst = max(worst, float(np.max(np.abs(dense - formula))))
        self.assertLessEqual(worst, 1e-10)

    def test_zero_mean_vertices_have_no_star(self) -> None:
        vertices = local_vertices(np.zeros(6))
        self.assertLessEqual(float(np.max(np.abs(vertices.gamma3))), 1e-15)
        expected_std = math.sqrt(0.5 - 1.0 / (2.0 * math.pi))
        b1 = 0.5 / expected_std
        b2 = (1.0 / math.sqrt(2.0 * math.pi)) / (2.0 * expected_std)
        expected_gamma2 = 2.0 * b2 / (b1 * b1)
        self.assertLessEqual(float(np.max(np.abs(vertices.gamma2 - expected_gamma2))), 1e-14)

    def test_shared_projector_gram_and_exact_cores(self) -> None:
        for n in (5, 6, 8):
            mean, covariance, _ = generated_state(n, 1_249_100 + n)
            source = build_nonzero_bridge_source(mean, covariance)
            projector = shared_projector(source)
            dense_flat = source.standard_k3.reshape(n, -1)
            dense_gram = dense_flat @ dense_flat.T
            self.assertLessEqual(float(np.max(np.abs(dense_gram - projector.mode_gram))), 1e-10)
            core3 = projected_core3(source, projector.factor_standard)
            core4 = projected_core4(source, projector.factor_standard)
            dense3 = np.einsum(
                "ijk,ip,jq,kr->pqr",
                source.standard_k3,
                projector.factor_standard,
                projector.factor_standard,
                projector.factor_standard,
                optimize=True,
            )
            dense4 = np.einsum(
                "ijkl,ip,jq,kr,ls->pqrs",
                source.standard_k4,
                projector.factor_standard,
                projector.factor_standard,
                projector.factor_standard,
                projector.factor_standard,
                optimize=True,
            )
            self.assertLessEqual(float(np.max(np.abs(core3 - dense3))), 1e-10)
            self.assertLessEqual(float(np.max(np.abs(core4 - dense4))), 1e-10)

    def test_factor_transport_and_delay_one_algebra(self) -> None:
        mean, covariance, weight = generated_state(6, 1_249_200)
        source = build_nonzero_bridge_source(mean, covariance)
        projected = project_source(source, shared_projector(source))
        approx3 = reconstruct(projected.core3, projected.factor_standard)
        approx4 = reconstruct(projected.core4, projected.factor_standard)
        scale = source.activation_scale
        physical3 = approx3 * np.einsum("i,j,k->ijk", scale, scale, scale)
        physical4 = approx4 * np.einsum("i,j,k,l->ijkl", scale, scale, scale, scale)
        dense3 = transport_dense(physical3, weight)
        dense4 = transport_dense(physical4, weight)
        factor3, factor4 = transport_projected(projected, weight)
        denominator = max(float(np.linalg.norm(dense3) + np.linalg.norm(dense4)), 1.0e-300)
        self.assertLessEqual(float(np.linalg.norm(dense3 - factor3) + np.linalg.norm(dense4 - factor4)) / denominator, 1e-10)
        next_mean = weight.T @ source.activation_mean
        next_covariance = weight.T @ source.activation_covariance @ weight
        next_covariance = 0.5 * (next_covariance + next_covariance.T)
        direct = edgeworth_delay_one(next_mean, next_covariance, dense3, dense4)
        factorized = edgeworth_delay_one(next_mean, next_covariance, factor3, factor4)
        self.assertLessEqual(float(np.max(np.abs(direct.mean - factorized.mean))), 1e-10)
        self.assertLessEqual(float(np.max(np.abs(direct.covariance - factorized.covariance))), 1e-10)
        self.assertLessEqual(repeated_output_k4_relative(dense4, factor4), 1e-10)

    def test_repeated_output_k4_metric_uses_ordered_multiplicities(self) -> None:
        reference = np.ones((2, 2, 2, 2), dtype=np.float64)
        approximation = np.array(reference, copy=True)
        approximation[0, 0, 0, 1] += 1.0
        # Every order-four entry has at most two distinct coordinates at n=2,
        # so ||reference||^2=16; the aaab orbit has multiplicity four.
        self.assertLessEqual(abs(repeated_output_k4_relative(reference, approximation) - 0.5), 1e-15)

    def test_permutation_and_positive_gauge_covariance(self) -> None:
        n = 8
        mean, covariance, weight = generated_state(n, 1_249_300)
        source = build_nonzero_bridge_source(mean, covariance)
        projected = project_source(source, shared_projector(source))
        rng = np.random.Generator(np.random.Philox(1_249_301))
        permutation = rng.permutation(n)
        mean_p = mean[permutation]
        covariance_p = covariance[np.ix_(permutation, permutation)]
        source_p = build_nonzero_bridge_source(mean_p, covariance_p)
        projected_p = project_source(source_p, shared_projector(source_p))
        expected_projector = projector_matrix(projected.factor_standard)[np.ix_(permutation, permutation)]
        self.assertLessEqual(
            float(np.max(np.abs(expected_projector - projector_matrix(projected_p.factor_standard)))), 1e-10
        )
        self.assertLessEqual(
            float(np.max(np.abs(source.standard_k3[np.ix_(permutation, permutation, permutation)] - source_p.standard_k3))),
            1e-10,
        )
        gauge = rng.uniform(0.25, 3.0, size=n)
        mean_g = gauge * mean
        covariance_g = gauge[:, None] * covariance * gauge[None, :]
        covariance_g = 0.5 * (covariance_g + covariance_g.T)
        source_g = build_nonzero_bridge_source(mean_g, covariance_g)
        projected_g = project_source(source_g, shared_projector(source_g))
        self.assertLessEqual(float(np.max(np.abs(source.standard_k3 - source_g.standard_k3))), 1e-10)
        self.assertLessEqual(float(np.max(np.abs(source.standard_k4 - source_g.standard_k4))), 1e-10)
        self.assertLessEqual(
            float(np.max(np.abs(projector_matrix(projected.factor_standard) - projector_matrix(projected_g.factor_standard)))),
            1e-10,
        )
        # Physical factor and affine map cancel the positive gauge.
        self.assertLessEqual(
            float(np.max(np.abs(weight.T @ projected.factor_physical - (weight / gauge[:, None]).T @ projected_g.factor_physical))),
            1e-10,
        )

    def test_rank_boundary_tie_fails_closed(self) -> None:
        # A deliberately exchangeable independent state has a broad symmetric
        # boundary; if numerical ordering happens to split it, the relative-gap
        # guard still refuses the unsafe rank-four cutoff.
        n = 8
        mean = np.zeros(n)
        covariance = np.eye(n)
        source = build_nonzero_bridge_source(mean, covariance)
        with self.assertRaises(M124FailClosed):
            shared_projector(source)

    def test_cost_and_manifest_are_inert(self) -> None:
        ledger = static_cost_ledger()
        self.assertLess(ledger["incremental_total"], INCREMENTAL_CEILING)
        self.assertEqual(ledger["source_only_effective"], 98_834_297_600)
        self.assertEqual(ledger["carrier_allowance_below_ceiling"], 53_165_702_400)
        manifest = draft_manifest()
        self.assertEqual(manifest["status"], "DRAFT_NOT_FROZEN")
        self.assertIs(manifest["execution_authorized"], False)
        self.assertEqual(manifest["outcome_state"], "UNOPENED")
        root = Path(__file__).resolve().parent
        draft_path = root / "_test_inert_manifest.json"
        draft_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            process = subprocess.run(
                [sys.executable, str(root / "run_m124_falsifier.py"), "--manifest", str(draft_path), "--execute"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("M124 INERT", process.stderr + process.stdout)
        finally:
            draft_path.unlink(missing_ok=True)

    def test_future_adjudication_is_mechanical(self) -> None:
        manifest = draft_manifest()
        passing = {
            "factor_transport_algebra_relative": 0.0,
            "source_fidelity": 1.0,
            "source_fidelity_k3": 1.0,
            "source_fidelity_k4": 1.0,
            "repeated_output_k4_relative": 0.0,
            "correction_ratio_to_zero": 0.0,
            "finite": True,
            "permutation_projector_relative": 0.0,
            "permutation_correction_relative": 0.0,
            "positive_gauge_projector_relative": 0.0,
            "positive_gauge_correction_relative": 0.0,
        }
        rows = [dict(passing) for _ in manifest["cases"]]
        self.assertEqual(adjudicate(rows, manifest)["verdict"], "SOURCE_PASS")
        rows[4]["correction_ratio_to_zero"] = 0.5000001
        killed = adjudicate(rows, manifest)
        self.assertEqual(killed["verdict"], "SOURCE_KILL")
        self.assertIn("cell_4:correction", killed["failures"])
        rows[4]["correction_ratio_to_zero"] = 0.0
        manifest["carrier_prerequisite"].update(
            status="PASSED_AND_HASH_LOCKED", artifact_hash="sha256:test", effective_compute=53_165_702_400
        )
        cost_killed = adjudicate(rows, manifest)
        self.assertEqual(cost_killed["verdict"], "SOURCE_KILL")
        self.assertIn("combined_cost", cost_killed["failures"])


if __name__ == "__main__":
    unittest.main()
