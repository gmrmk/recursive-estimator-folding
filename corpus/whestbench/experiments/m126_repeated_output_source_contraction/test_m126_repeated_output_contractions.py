from __future__ import annotations

import itertools
import math
import unittest

import numpy as np

from m126_repeated_output_contractions import (
    ORBIT_MULTIPLICITIES,
    collision22_from_factorization,
    collision22_hard_exact,
    collision22_probe_sample,
    collision211_repeated_exact,
    collision_repeated_exact,
    flopscope_ledger,
    path_aabb_residual_probe_sample,
    path_hard_tables_exact,
    path_residual_from_factorization,
    path_residual_probe_sample,
    rademacher_product_variance,
    tree_repeated_exact,
)


def generated_bridge(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=0.18, size=(n, n))
    q = 0.5 * (raw + raw.T)
    np.fill_diagonal(q, 1.0)
    return q


def canonical_paths4() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(path for path in itertools.permutations(range(4)) if path <= path[::-1])


def dense_tree_tensors(
    q: np.ndarray, gamma2: np.ndarray, gamma3: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    n = q.shape[0]
    t3 = np.empty((n, n, n), dtype=np.float64)
    for i, j, k in np.ndindex(n, n, n):
        t3[i, j, k] = (
            gamma2[i] * q[i, j] * q[i, k]
            + gamma2[j] * q[j, i] * q[j, k]
            + gamma2[k] * q[k, i] * q[k, j]
        )
    t4 = np.zeros((n, n, n, n), dtype=np.float64)
    for indices in np.ndindex(n, n, n, n):
        value = 0.0
        for path in canonical_paths4():
            a, b, c, d = (indices[position] for position in path)
            value += (
                q[a, b]
                * q[b, c]
                * q[c, d]
                * gamma2[b]
                * gamma2[c]
            )
        for centre in range(4):
            root = indices[centre]
            value += gamma3[root] * math.prod(
                q[root, indices[position]]
                for position in range(4)
                if position != centre
            )
        t4[indices] = value
    return t3, t4


def dense_collision_tensors(
    diagonal3: np.ndarray,
    majority3: np.ndarray,
    diagonal4: np.ndarray,
    majority4: np.ndarray,
    paired4: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n = diagonal3.size
    t3 = np.zeros((n, n, n), dtype=np.float64)
    t4 = np.zeros((n, n, n, n), dtype=np.float64)
    for i in range(n):
        t3[i, i, i] = diagonal3[i]
        t4[i, i, i, i] = diagonal4[i]
        for j in range(n):
            if i == j:
                continue
            for singleton in range(3):
                indices = [i, i, i]
                indices[singleton] = j
                t3[tuple(indices)] = majority3[i, j]
            for singleton in range(4):
                indices = [i, i, i, i]
                indices[singleton] = j
                t4[tuple(indices)] = majority4[i, j]
        for j in range(i + 1, n):
            for left_slots in itertools.combinations(range(4), 2):
                indices = [j, j, j, j]
                for slot in left_slots:
                    indices[slot] = i
                t4[tuple(indices)] = paired4[i, j]
    return t3, t4


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


class M126RepeatedOutputContractionTests(unittest.TestCase):
    def test_orbit_multiplicities_are_complete(self) -> None:
        self.assertEqual(ORBIT_MULTIPLICITIES["k3_aab"], {"centre_a": 2, "centre_b": 1})
        self.assertEqual(
            ORBIT_MULTIPLICITIES["k4_path_aaab"],
            {"singleton_endpoint": 6, "singleton_internal": 6},
        )
        self.assertEqual(
            ORBIT_MULTIPLICITIES["k4_path_aabb"],
            {"block_aabb": 4, "self_abba": 2, "self_baab": 2, "cross_abab": 4},
        )
        self.assertEqual(sum(ORBIT_MULTIPLICITIES["k4_path_aabb"].values()), 12)
        self.assertEqual(
            ORBIT_MULTIPLICITIES["source_collision_partitions"],
            {"k3_3": 1, "k3_21": 3, "k4_4": 1, "k4_31": 4, "k4_22": 6, "k4_211": 12},
        )

    def test_tree_formulas_match_dense_transport(self) -> None:
        worst = 0.0
        for n in range(2, 6):
            rng = np.random.default_rng(126100 + n)
            q = generated_bridge(n, 126200 + n)
            gamma2 = rng.normal(size=n)
            gamma3 = rng.normal(size=n)
            weight = rng.normal(size=(n, n))
            dense3, dense4 = dense_tree_tensors(q, gamma2, gamma3)
            expected = repeated_from_dense(dense3, dense4, weight)
            actual = tree_repeated_exact(q, gamma2, gamma3, weight)
            for key in expected:
                worst = max(worst, float(np.max(np.abs(expected[key] - actual[key]))))
        self.assertLessEqual(worst, 2e-10)

    def test_sparse_collision_formulas_match_dense_transport(self) -> None:
        worst = 0.0
        for n in range(2, 6):
            rng = np.random.default_rng(126300 + n)
            d3 = rng.normal(size=n)
            e3 = rng.normal(size=(n, n))
            d4 = rng.normal(size=n)
            e31 = rng.normal(size=(n, n))
            e22 = rng.normal(size=(n, n))
            np.fill_diagonal(e3, 0.0)
            np.fill_diagonal(e31, 0.0)
            e22 = 0.5 * (e22 + e22.T)
            np.fill_diagonal(e22, 0.0)
            weight = rng.normal(size=(n, n))
            dense3, dense4 = dense_collision_tensors(d3, e3, d4, e31, e22)
            expected = repeated_from_dense(dense3, dense4, weight)
            actual = collision_repeated_exact(d3, e3, d4, e31, e22, weight)
            for key in expected:
                worst = max(worst, float(np.max(np.abs(expected[key] - actual[key]))))
        self.assertLessEqual(worst, 2e-10)

    def test_three_label_collision_oracle_matches_all_twelve_slots(self) -> None:
        n, outputs = 5, 3
        rng = np.random.default_rng(126351)
        defect211 = np.zeros((n, n, n), dtype=np.float64)
        dense4 = np.zeros((n, n, n, n), dtype=np.float64)
        for repeated in range(n):
            singletons = [index for index in range(n) if index != repeated]
            for left, right in itertools.combinations(singletons, 2):
                value = float(rng.normal())
                defect211[repeated, left, right] = value
                defect211[repeated, right, left] = value
                for slots in set(itertools.permutations((repeated, repeated, left, right))):
                    dense4[slots] = value
        weight = rng.normal(size=(n, outputs))
        dense3 = np.zeros((n, n, n), dtype=np.float64)
        expected = repeated_from_dense(dense3, dense4, weight)
        actual = collision211_repeated_exact(defect211, weight)
        for key in ("k4_aaaa", "k4_aaab", "k4_aabb"):
            self.assertLessEqual(
                float(np.max(np.abs(expected[key] - actual[key]))), 2e-10
            )

    def test_complete_rademacher_average_recovers_hard_tables_exactly(self) -> None:
        n = 4
        rng = np.random.default_rng(126401)
        q = generated_bridge(n, 126402)
        gamma2 = rng.normal(size=n)
        weight = rng.normal(size=(n, n))
        e22 = rng.normal(size=(n, n))
        e22 = 0.5 * (e22 + e22.T)
        np.fill_diagonal(e22, 0.0)
        hard = path_hard_tables_exact(q, gamma2, weight)
        collision_hard = collision22_hard_exact(e22, weight)
        path_self = np.zeros_like(hard["residual_self"])
        path_cross = np.zeros_like(hard["residual_cross"])
        collision = np.zeros_like(collision_hard)
        assembled_path = np.zeros_like(hard["residual_self"])
        signs = tuple(itertools.product((-1.0, 1.0), repeat=n))
        for values in signs:
            probe = np.asarray(values)
            sample = path_residual_probe_sample(q, gamma2, weight, probe)
            path_self += sample["residual_self"]
            path_cross += sample["residual_cross"]
            assembled_sample = path_aabb_residual_probe_sample(
                q, gamma2, weight, probe
            )
            self.assertLessEqual(
                float(np.max(np.abs(assembled_sample - assembled_sample.T))), 2e-12
            )
            assembled_path += assembled_sample
            collision += collision22_probe_sample(e22, weight, probe)
        path_self /= len(signs)
        path_cross /= len(signs)
        collision /= len(signs)
        assembled_path /= len(signs)
        self.assertLessEqual(float(np.max(np.abs(path_self - hard["residual_self"]))), 2e-12)
        self.assertLessEqual(float(np.max(np.abs(path_cross - hard["residual_cross"]))), 2e-12)
        self.assertLessEqual(float(np.max(np.abs(collision - collision_hard))), 2e-12)
        expected_assembled = (
            2.0 * (hard["residual_self"] + hard["residual_self"].T)
            + 4.0 * hard["residual_cross"]
        )
        propagated = q @ weight
        residual = q - np.eye(n)
        direct_aggregate = np.empty_like(expected_assembled)
        for left in range(n):
            for right in range(n):
                symmetric_pair = gamma2 * (
                    propagated[:, left] * weight[:, right]
                    + propagated[:, right] * weight[:, left]
                )
                direct_aggregate[left, right] = (
                    2.0 * symmetric_pair @ residual @ symmetric_pair
                )
        self.assertLessEqual(
            float(np.max(np.abs(direct_aggregate - expected_assembled))), 2e-12
        )
        self.assertLessEqual(
            float(np.max(np.abs(assembled_path - expected_assembled))), 2e-12
        )

    def test_full_rank_symmetric_factorization_recovers_residual_tables(self) -> None:
        n = 5
        rng = np.random.default_rng(126501)
        q = generated_bridge(n, 126502)
        gamma2 = rng.normal(size=n)
        weight = rng.normal(size=(n, n))
        hard = path_hard_tables_exact(q, gamma2, weight)
        residual = q - np.eye(n)
        values, vectors = np.linalg.eigh(residual)
        factorized = path_residual_from_factorization(
            q @ weight, weight, gamma2, values, vectors
        )
        self.assertLessEqual(
            float(np.max(np.abs(factorized["residual_self"] - hard["residual_self"]))),
            2e-11,
        )
        self.assertLessEqual(
            float(np.max(np.abs(factorized["residual_cross"] - hard["residual_cross"]))),
            2e-11,
        )

        e22 = rng.normal(size=(n, n))
        e22 = 0.5 * (e22 + e22.T)
        np.fill_diagonal(e22, 0.0)
        values22, vectors22 = np.linalg.eigh(e22)
        reconstructed22 = collision22_from_factorization(weight, values22, vectors22)
        self.assertLessEqual(
            float(np.max(np.abs(reconstructed22 - collision22_hard_exact(e22, weight)))),
            2e-11,
        )

    def test_rademacher_product_variance_matches_complete_enumeration(self) -> None:
        rng = np.random.default_rng(126601)
        u = rng.normal(size=5)
        v = rng.normal(size=5)
        values = []
        for signs in itertools.product((-1.0, 1.0), repeat=5):
            z = np.asarray(signs)
            values.append(float((u @ z) * (v @ z)))
        observed = float(np.var(values))
        expected = rademacher_product_variance(u, v)
        self.assertAlmostEqual(observed, expected, places=12)

    def test_permutation_covariance_and_flopscope_are_mechanical(self) -> None:
        n = 5
        rng = np.random.default_rng(126701)
        q = generated_bridge(n, 126702)
        gamma2 = rng.normal(size=n)
        gamma3 = rng.normal(size=n)
        weight = rng.normal(size=(n, n))
        reference = tree_repeated_exact(q, gamma2, gamma3, weight)
        permutation = rng.permutation(n)
        observed = tree_repeated_exact(
            q[np.ix_(permutation, permutation)],
            gamma2[permutation],
            gamma3[permutation],
            weight[permutation],
        )
        for key in reference:
            self.assertLessEqual(float(np.max(np.abs(reference[key] - observed[key]))), 2e-10)

        ledger2 = flopscope_ledger(probes=2)
        ledger8 = flopscope_ledger(probes=8)
        ledger8_f32 = flopscope_ledger(probes=8, dense_gemm_dtype="float32")
        self.assertEqual(ledger2["exact_base_square_calls_per_layer"], 24)
        self.assertEqual(ledger2["probe_square_calls_per_layer"], 8)
        self.assertEqual(ledger2["source_effective_flops"], 92_052_462_080)
        self.assertEqual(ledger8["source_effective_flops"], 154_341_808_640)
        self.assertEqual(ledger8_f32["square_dense_gemm_bill"], 33_488_896)
        self.assertEqual(ledger8_f32["source_effective_flops"], 81_670_904_320)
        self.assertEqual(
            ledger8_f32["source_effective_flops"] + 12_819_347_280,
            94_490_251_600,
        )
        self.assertGreater(ledger8["source_effective_flops"], ledger2["source_effective_flops"])


if __name__ == "__main__":
    unittest.main()
