from __future__ import annotations

import sys
from pathlib import Path
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "m151_b1_forward_control"))

from m155_khatri_obstruction import (
    split_pair_obstruction_exhaustive,
    split_pair_obstruction_khatri,
    star_split_aabb_decomposed,
    star_split_aabb_exhaustive,
    target_cost_ledger,
)
from m151_b1_forward_control import B1CanonicalState, canonical_delta_tilde_b1


class TestM155KhatriObstruction(unittest.TestCase):
    def test_khatri_identity(self) -> None:
        for width in (3, 4, 5):
            rng = np.random.default_rng(15500 + width)
            weight = rng.normal(size=(width, width + 1))
            root = rng.normal(size=(width, width))
            covariance = root @ root.T
            self.assertLess(
                np.max(
                    np.abs(
                        split_pair_obstruction_exhaustive(weight, covariance)
                        - split_pair_obstruction_khatri(weight, covariance)
                    )
                ),
                3e-10,
            )

    def test_masked_star_split_decomposition(self) -> None:
        for width in (3, 4, 5):
            rng = np.random.default_rng(15520 + width)
            weight = rng.normal(size=(width, width))
            root = rng.normal(size=(width, width))
            covariance = root @ root.T
            self.assertLess(
                np.max(
                    np.abs(
                        star_split_aabb_exhaustive(weight, covariance)
                        - star_split_aabb_decomposed(weight, covariance)
                    )
                ),
                2e-9,
            )

    def test_label_permutation_invariance(self) -> None:
        rng = np.random.default_rng(15541)
        weight = rng.normal(size=(6, 5))
        root = rng.normal(size=(6, 6))
        covariance = root @ root.T
        permutation = rng.permutation(6)
        expected = split_pair_obstruction_khatri(weight, covariance)
        actual = split_pair_obstruction_khatri(
            weight[permutation], covariance[permutation][:, permutation]
        )
        self.assertLess(np.max(np.abs(expected - actual)), 2e-10)

    def test_admissible_star_only_b1_state_prevents_cp_cancellation(self) -> None:
        rng = np.random.default_rng(15561)
        width = 5
        axis = rng.normal(size=width)
        omega = np.zeros(49, dtype=np.float64)
        omega[:2] = 0.5
        mean = np.zeros((49, width), dtype=np.float64)
        mean[0] = axis
        mean[1] = -axis
        variance = np.zeros_like(mean)
        state = B1CanonicalState(omega, mean, variance)
        coefficient = canonical_delta_tilde_b1(state)
        covariance = np.outer(axis, axis)
        expected = np.zeros_like(coefficient)
        for i in range(width):
            for j in range(width):
                for k in range(width):
                    if len({i, j, k}) == 3:
                        expected[i, j, k] = -2.0 * covariance[i, j] * covariance[i, k]
        self.assertLess(np.max(np.abs(coefficient - expected)), 2e-12)

    def test_target_cost_closes_current_m151_gate(self) -> None:
        ledger = target_cost_ledger()
        self.assertEqual(ledger["symmetric_quadratic_columns"], 32896)
        self.assertAlmostEqual(
            ledger["f64_matmul_bill_all_layers_billions"],
            266.806034432,
            places=12,
        )
        self.assertGreater(
            ledger["f64_matmul_bill_all_layers_billions"],
            ledger["m151_inclusive_untraced_cap_billions"],
        )
        self.assertGreater(ledger["two_input_output_buffers_f64_mib"], 37.141)


if __name__ == "__main__":
    unittest.main()

