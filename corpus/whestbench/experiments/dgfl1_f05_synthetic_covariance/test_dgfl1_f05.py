"""Tests for the predeclared DGFL hand-network covariance screen."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


HERE = Path(__file__).resolve().parent
F0 = HERE.parent / "dgfl1_f0_synthetic"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(F0))

from dgfl1_f05 import (  # noqa: E402
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    FIT_ROTATION_SEED,
    HELD_ROTATION_SEED,
    PERMUTATION_REPLICATES,
    PERMUTATION_SEED,
    apply_factorial_arms,
    bootstrap_indices,
    bootstrap_joint_lower,
    classify_screen,
    design_rows,
    evaluate_rotation_record,
    evaluate_rotation_matrix_record,
    fit_joint_coefficients,
    generate_split_records,
    hand_network,
    held_statistics,
    permutation_indices,
    permutation_p_num,
    pilot_geometry,
    rotation_angles,
    rotation_matrices,
    sha256_payload,
    trace_variance,
)
import dgfl1_f05 as f05_module  # noqa: E402
import run_dgfl1_f05 as runner_module  # noqa: E402


EXPECTED_FIXTURE_HASHES = {
    "fit_rotations": "BDDA3E2AAF5ABFCBABE05AAA9CCFC3928CF4406006BADE0CF140C2EE368C52C3",
    "held_rotations": "757DA553306CB1A644BDFD9A0A4F39FBA5800557375F80896017B73090D78D71",
    "permutations": "716CE92671E981918A6D1F2D4EC1C371795721D8B8D0566BD5F882F8D34487F8",
    "bootstrap": "60BFF8CF76A7CEF92731C8B25B7DCF1D8568F9AE73F296EE70E64D61ED758E5C",
}


class PilotAndRecordContracts(unittest.TestCase):
    def test_pilot_geometry_matches_the_frozen_deep_pullbacks(self) -> None:
        geometry = pilot_geometry(hand_network())
        np.testing.assert_allclose(
            geometry["pilot"],
            np.array([math.cos(0.137), math.sin(0.137)]),
            rtol=0.0,
            atol=2e-16,
        )
        np.testing.assert_array_equal(geometry["first_mask"], [True, True, False])
        np.testing.assert_allclose(
            geometry["pullbacks"],
            np.array([[0.52, -0.34], [0.04, 1.0]]),
            rtol=0.0,
            atol=3e-16,
        )
        np.testing.assert_allclose(
            geometry["axes"],
            np.array(
                [
                    [0.8369696139735456, -0.5472493629827029],
                    [0.03996803834887161, 0.9992009587217893],
                ]
            ),
            rtol=0.0,
            atol=2e-15,
        )
        np.testing.assert_allclose(geometry["J"] + geometry["J"].T, 0.0, atol=0.0)

    def test_one_rotation_returns_base_and_six_rungs_from_four_jvps(self) -> None:
        geometry = pilot_geometry(hand_network())
        actual_forward_jvp = f05_module.forward_jvp
        with mock.patch.object(
            f05_module, "forward_jvp", wraps=actual_forward_jvp
        ) as counted:
            y, z, receipt = evaluate_rotation_record(
                theta=0.419, weights=hand_network(), geometry=geometry
            )
        self.assertEqual(counted.call_count, 4)
        self.assertEqual(y.shape, (2,))
        self.assertEqual(z.shape, (6, 2))
        self.assertEqual(receipt["row_order"], ["+e1", "-e1", "+e2", "-e2"])
        self.assertEqual(receipt["jvp_evaluations"], 4)
        self.assertTrue(np.all(np.isfinite(y)))
        self.assertTrue(np.all(np.isfinite(z)))

    def test_materialized_rotation_path_matches_the_angle_wrapper(self) -> None:
        geometry = pilot_geometry(hand_network())
        angle_record = evaluate_rotation_record(
            theta=0.419, weights=hand_network(), geometry=geometry
        )
        matrix_record = evaluate_rotation_matrix_record(
            rotation=rotation_matrices(741, 1)[0],
            weights=hand_network(),
            geometry=geometry,
        )
        direct_record = evaluate_rotation_record(
            theta=rotation_angles(741, 1)[0],
            weights=hand_network(),
            geometry=geometry,
        )
        self.assertEqual(angle_record[2]["jvp_evaluations"], 4)
        np.testing.assert_array_equal(matrix_record[0], direct_record[0])
        np.testing.assert_array_equal(matrix_record[1], direct_record[1])

    def test_rotation_record_rejects_nonrotations_and_nonfinite_angles(self) -> None:
        geometry = pilot_geometry(hand_network())
        with self.assertRaises(ValueError):
            evaluate_rotation_record(
                theta=math.nan, weights=hand_network(), geometry=geometry
            )
        with self.assertRaises(ValueError):
            evaluate_rotation_matrix_record(
                rotation=np.array([[1.0, 1.0], [0.0, 1.0]]),
                weights=hand_network(),
                geometry=geometry,
            )

    def test_all_six_aggregate_rungs_match_rotation_finite_differences(self) -> None:
        weights = hand_network()
        geometry = pilot_geometry(weights)
        theta = 0.419
        _, z, _ = evaluate_rotation_record(
            theta=theta, weights=weights, geometry=geometry
        )

        base = design_rows()

        def modulated_means(angle: float) -> np.ndarray:
            rows = (f05_module.rotation_2d(angle) @ base.T).T
            leaves = []
            for u in rows:
                y, _ = f05_module.forward_jvp(weights, u, np.zeros(2))
                modulators = [float(geometry["m"] @ u), float(geometry["b"] @ u)]
                for axis in geometry["axes"]:
                    for frequency in (math.sqrt(2.0), 2.0 * math.sqrt(2.0)):
                        modulators.append(math.cos(float(frequency * (axis @ u))))
                leaves.append(np.asarray(modulators)[:, None] * y[None, :])
            return np.mean(np.stack(leaves), axis=0)

        step = 2.0**-20
        finite_difference = (
            modulated_means(theta + step) - modulated_means(theta - step)
        ) / (2.0 * step)
        np.testing.assert_allclose(z, finite_difference, rtol=0.0, atol=2e-10)

    def test_split_generation_uses_four_jvps_per_materialized_rotation(self) -> None:
        y, z, receipt = generate_split_records(FIT_ROTATION_SEED, count=8)
        self.assertEqual(y.shape, (8, 2))
        self.assertEqual(z.shape, (8, 6, 2))
        self.assertEqual(receipt["jvp_evaluations"], 32)
        self.assertEqual(
            receipt["rotation_payload_sha256"],
            sha256_payload(rotation_matrices(FIT_ROTATION_SEED, 8)),
        )

    def test_fit_and_held_rotation_streams_are_domain_separated(self) -> None:
        fit = rotation_angles(FIT_ROTATION_SEED, 128)
        held = rotation_angles(HELD_ROTATION_SEED, 128)
        self.assertEqual(fit.shape, (128,))
        self.assertEqual(held.shape, (128,))
        self.assertFalse(np.array_equal(fit, held))
        self.assertTrue(np.all((fit >= 0.0) & (fit < 2.0 * math.pi)))
        self.assertTrue(np.all((held >= 0.0) & (held < 2.0 * math.pi)))


class FitAndFactorialContracts(unittest.TestCase):
    def test_joint_ridge_fit_recovers_a_well_conditioned_synthetic_relation(self) -> None:
        rng = np.random.Generator(np.random.PCG64DXSM(911_731))
        z = rng.standard_normal((96, 6, 2))
        beta_true = np.array([0.4, -0.2, 0.1, 0.3, -0.5, 0.25])
        y = np.einsum("irp,r->ip", z, beta_true)
        beta, receipt = fit_joint_coefficients(y, z)
        self.assertEqual(beta.shape, (6,))
        self.assertGreater(receipt["ridge_lambda"], 0.0)
        self.assertLess(receipt["relative_residual"], 1e-12)
        np.testing.assert_allclose(beta, beta_true, rtol=3e-6, atol=2e-6)

    def test_factorial_arms_use_one_joint_vector_without_refitting(self) -> None:
        rng = np.random.Generator(np.random.PCG64DXSM(88_401))
        y = rng.standard_normal((24, 2))
        z = rng.standard_normal((24, 6, 2))
        beta = np.array([0.2, -0.1, 0.3, 0.4, -0.2, 0.05])
        arms = apply_factorial_arms(y, z, beta)
        np.testing.assert_array_equal(arms["00"], y)
        np.testing.assert_allclose(
            arms["10"], y - np.einsum("irp,r->ip", z[:, :2], beta[:2])
        )
        np.testing.assert_allclose(
            arms["01"], y - np.einsum("irp,r->ip", z[:, 2:], beta[2:])
        )
        np.testing.assert_allclose(
            arms["11"], y - np.einsum("irp,r->ip", z, beta)
        )

    def test_trace_variance_is_sample_centered_whole_rotation_variance(self) -> None:
        values = np.array([[1.0, 2.0], [3.0, 0.0], [2.0, 4.0]])
        centered = values - np.mean(values, axis=0, keepdims=True)
        self.assertEqual(trace_variance(values), float(np.sum(centered**2) / 2.0))

    def test_resampling_constants_are_exactly_frozen(self) -> None:
        self.assertEqual(FIT_ROTATION_SEED, 0xD6F10001)
        self.assertEqual(HELD_ROTATION_SEED, 0xD6F10002)
        self.assertEqual(BOOTSTRAP_SEED, 0xD6F10003)
        self.assertEqual(PERMUTATION_SEED, 0xD6F10004)
        self.assertEqual(BOOTSTRAP_REPLICATES, 4096)
        self.assertEqual(PERMUTATION_REPLICATES, 1024)

    def test_randomization_fixtures_are_byte_deterministic(self) -> None:
        fit_a = rotation_matrices(FIT_ROTATION_SEED, 128)
        fit_b = rotation_matrices(FIT_ROTATION_SEED, 128)
        held = rotation_matrices(HELD_ROTATION_SEED, 128)
        permutations_a = permutation_indices()
        permutations_b = permutation_indices()
        boot_a = bootstrap_indices()
        boot_b = bootstrap_indices()
        self.assertEqual(fit_a.shape, (128, 2, 2))
        self.assertEqual(held.shape, (128, 2, 2))
        self.assertEqual(permutations_a.shape, (1024, 2, 128))
        self.assertEqual(permutations_a.dtype, np.dtype("<u2"))
        self.assertEqual(boot_a.shape, (4096, 128))
        self.assertEqual(boot_a.dtype, np.dtype("<u2"))
        self.assertEqual(sha256_payload(fit_a), sha256_payload(fit_b))
        self.assertNotEqual(sha256_payload(fit_a), sha256_payload(held))
        self.assertEqual(permutations_a.tobytes(), permutations_b.tobytes())
        self.assertEqual(boot_a.tobytes(), boot_b.tobytes())
        self.assertEqual(sha256_payload(fit_a), EXPECTED_FIXTURE_HASHES["fit_rotations"])
        self.assertEqual(sha256_payload(held), EXPECTED_FIXTURE_HASHES["held_rotations"])
        self.assertEqual(
            sha256_payload(permutations_a), EXPECTED_FIXTURE_HASHES["permutations"]
        )
        self.assertEqual(sha256_payload(boot_a), EXPECTED_FIXTURE_HASHES["bootstrap"])
        self.assertEqual(fit_a.dtype.str, "<f8")
        self.assertEqual(held.dtype.str, "<f8")
        self.assertTrue(fit_a.flags.c_contiguous and held.flags.c_contiguous)
        for pair in permutations_a[:4]:
            np.testing.assert_array_equal(np.sort(pair[0]), np.arange(128))
            np.testing.assert_array_equal(np.sort(pair[1]), np.arange(128))

    def test_held_statistics_and_bootstrap_use_common_whole_record_indices(self) -> None:
        rng = np.random.Generator(np.random.PCG64DXSM(713_009))
        base = rng.standard_normal((128, 2))
        arms = {
            "00": base,
            "10": 0.8 * base,
            "01": 0.7 * base,
            "11": 0.5 * base,
        }
        stats = held_statistics(arms)
        self.assertAlmostEqual(stats["R2_joint"], 0.75, places=14)
        self.assertGreater(stats["R2_F_given_D"], 0.0)
        self.assertGreater(stats["R2_D_given_F"], 0.0)
        lower, values = bootstrap_joint_lower(arms, bootstrap_indices())
        self.assertEqual(values.shape, (4096,))
        self.assertGreater(lower, 0.0)
        self.assertEqual(lower, np.sort(values)[40])
        np.testing.assert_allclose(values, np.full(4096, 0.75), rtol=0.0, atol=2e-15)

    def test_permutation_p_value_counts_ties_against_the_candidate(self) -> None:
        rng = np.random.Generator(np.random.PCG64DXSM(99_117))
        z_fit = rng.standard_normal((32, 6, 2))
        z_held = rng.standard_normal((32, 6, 2))
        beta = np.array([0.4, -0.1, 0.25, 0.05, -0.2, 0.3])
        y_fit = np.einsum("irp,r->ip", z_fit, beta)
        y_held = np.einsum("irp,r->ip", z_held, beta)
        perms = np.empty((3, 2, 32), dtype="<u2")
        perms[0, 0] = np.arange(32)
        perms[0, 1] = np.arange(32)
        perms[1, 0] = np.arange(31, -1, -1)
        perms[1, 1] = np.arange(31, -1, -1)
        perms[2, 0] = np.roll(np.arange(32), 1)
        perms[2, 1] = np.roll(np.arange(32), 2)
        observed_beta, _ = fit_joint_coefficients(y_fit, z_fit)
        observed = held_statistics(apply_factorial_arms(y_held, z_held, observed_beta))[
            "R2_joint"
        ]
        p_num, nulls = permutation_p_num(
            y_fit, z_fit, y_held, z_held, perms, observed
        )
        self.assertEqual(nulls.shape, (3,))
        self.assertEqual(nulls[0], observed)
        self.assertEqual(p_num, 1 + int(np.count_nonzero(nulls >= observed)))

    def test_identity_permutation_is_an_exact_tie_across_random_fixtures(self) -> None:
        for seed in range(20):
            rng = np.random.Generator(np.random.PCG64DXSM(31_000 + seed))
            z_fit = rng.standard_normal((32, 6, 2))
            z_held = rng.standard_normal((32, 6, 2))
            y_fit = rng.standard_normal((32, 2))
            y_held = rng.standard_normal((32, 2))
            beta, _ = fit_joint_coefficients(y_fit, z_fit)
            observed = held_statistics(apply_factorial_arms(y_held, z_held, beta))[
                "R2_joint"
            ]
            identity = np.tile(np.arange(32, dtype=np.uint16), (1, 2, 1))
            _, nulls = permutation_p_num(
                y_fit, z_fit, y_held, z_held, identity, observed
            )
            self.assertEqual(nulls[0], observed)

    def test_perfect_joint_correction_with_zero_v11_is_valid(self) -> None:
        base = np.arange(32, dtype=np.float64).reshape(16, 2)
        arms = {
            "00": base,
            "10": 0.8 * base,
            "01": 0.7 * base,
            "11": np.zeros_like(base),
        }
        statistics = held_statistics(arms)
        self.assertEqual(statistics["V11"], 0.0)
        self.assertEqual(statistics["R2_joint"], 1.0)
        lower, values = bootstrap_joint_lower(arms, bootstrap_indices(replicates=41, count=16))
        self.assertEqual(lower, 1.0)
        np.testing.assert_array_equal(values, np.ones(41))
        status, reasons = classify_screen(statistics, lower, p_num=1)
        self.assertEqual(status, "PASS_F05_SYNTHETIC_COVARIANCE_ONLY")
        self.assertEqual(reasons, [])

    def test_fit_is_invariant_to_constant_response_and_control_offsets(self) -> None:
        rng = np.random.Generator(np.random.PCG64DXSM(714_882))
        y = rng.standard_normal((64, 2))
        z = rng.standard_normal((64, 6, 2))
        beta_a, _ = fit_joint_coefficients(y, z)
        beta_b, _ = fit_joint_coefficients(
            y + np.array([7.0, -3.0]), z + np.arange(12).reshape(6, 2)
        )
        np.testing.assert_allclose(beta_a, beta_b, rtol=2e-13, atol=2e-13)

    def test_fit_and_variance_fail_closed_on_degenerate_or_nonfinite_data(self) -> None:
        with self.assertRaises(RuntimeError):
            fit_joint_coefficients(np.ones((8, 2)), np.ones((8, 6, 2)))
        with self.assertRaises(ValueError):
            trace_variance(np.array([[0.0, math.nan], [1.0, 2.0]]))
        self.assertEqual(trace_variance(np.ones((8, 2))), 0.0)
        with self.assertRaises(RuntimeError):
            held_statistics(
                {
                    "00": np.ones((8, 2)),
                    "10": np.arange(16).reshape(8, 2),
                    "01": np.arange(16).reshape(8, 2),
                    "11": np.zeros((8, 2)),
                }
            )

    def test_frozen_screen_classifier_uses_ratio_free_inclusive_joint_gate(self) -> None:
        exactly = {"V00": 10.0, "V10": 9.5, "V01": 9.25, "V11": 9.0}
        status, reasons = classify_screen(exactly, bootstrap_lower=0.01, p_num=10)
        self.assertEqual(status, "PASS_F05_SYNTHETIC_COVARIANCE_ONLY")
        self.assertEqual(reasons, [])
        killed, reasons = classify_screen(
            {"V00": 10.0, "V10": 8.9, "V01": 8.8, "V11": 9.01},
            bootstrap_lower=0.0,
            p_num=11,
        )
        self.assertEqual(killed, "KILLED_F05_SYNTHETIC_COVARIANCE")
        self.assertEqual(
            reasons,
            [
                "JOINT_R2_BELOW_0P10",
                "FOURIER_PARTIAL_R2_NONPOSITIVE",
                "DIPOLE_PARTIAL_R2_NONPOSITIVE",
                "BOOTSTRAP_LOWER_NONPOSITIVE",
                "PERMUTATION_P_EXCEEDS_0P01",
            ],
        )

    def test_resample_and_permutation_fixtures_fail_closed(self) -> None:
        base = np.arange(16, dtype=np.float64).reshape(8, 2)
        arms = {"00": base, "10": 0.9 * base, "01": 0.8 * base, "11": 0.7 * base}
        with self.assertRaises(ValueError):
            bootstrap_joint_lower(arms, np.full((41, 8), 8, dtype=np.uint16))
        constant_base = dict(arms)
        constant_base["00"] = np.ones_like(base)
        with self.assertRaises(RuntimeError):
            bootstrap_joint_lower(
                constant_base, np.tile(np.arange(8, dtype=np.uint16), (41, 1))
            )
        nonfinite = dict(arms)
        nonfinite["10"] = nonfinite["10"].copy()
        nonfinite["10"][0, 0] = math.nan
        with self.assertRaises(ValueError):
            bootstrap_joint_lower(
                nonfinite, np.tile(np.arange(8, dtype=np.uint16), (41, 1))
            )
        y = np.arange(16, dtype=np.float64).reshape(8, 2)
        z = np.arange(96, dtype=np.float64).reshape(8, 6, 2)
        bad = np.tile(np.arange(8, dtype=np.uint16), (1, 2, 1))
        bad[0, 0, 0] = 1
        with self.assertRaises(ValueError):
            permutation_p_num(y, z, y, z, bad, 0.1)
        with self.assertRaises(ValueError):
            permutation_p_num(y, z, y, z, bad.astype(np.float64), 0.1)


class RunnerPreflightContracts(unittest.TestCase):
    def _assert_manifest_rejected_before_import(self, mutate) -> None:
        manifest = json.loads((HERE / "PREEXECUTION_MANIFEST.json").read_text())
        mutate(manifest)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(runner_module, "_load_numeric_modules") as loader:
                with self.assertRaises(RuntimeError):
                    runner_module.validate_manifest(path)
                loader.assert_not_called()

    def test_missing_bound_file_set_fails_before_numeric_import(self) -> None:
        self._assert_manifest_rejected_before_import(
            lambda manifest: manifest.update({"bound_files": []})
        )

    def test_duplicate_bound_file_fails_before_numeric_import(self) -> None:
        def duplicate(manifest) -> None:
            manifest["bound_files"].append(dict(manifest["bound_files"][0]))

        self._assert_manifest_rejected_before_import(duplicate)

    def test_wrong_variance_contract_fails_before_numeric_import(self) -> None:
        def wrong_contract(manifest) -> None:
            manifest["statistical_contract"]["trace_variance"] = "population"

        self._assert_manifest_rejected_before_import(wrong_contract)

    def test_wrong_bound_hash_fails_before_numeric_import(self) -> None:
        def wrong_hash(manifest) -> None:
            manifest["bound_files"][0]["sha256"] = "0" * 64

        self._assert_manifest_rejected_before_import(wrong_hash)


if __name__ == "__main__":
    unittest.main()
