"""Response-free tests frozen by M208_PREDECLARATION_20260809.md."""

from __future__ import annotations

import inspect
import itertools
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m208_physical_rankone_cumulant_control as m208  # noqa: E402


KAPPA = -2.0


def _half_feature(weight: np.ndarray, i: int, j: int, k: int):
    """Independent half-owned M133 feature, valid on the complete table."""

    x, y, z = weight[i], weight[j], weight[k]
    aaab = 3.0 * (np.outer(x * y * z, x) + np.outer(x * x * z, y))
    aabb_half = np.outer(x * x, y * z)
    aabb_split = 2.0 * np.outer(x * y, x * z)
    aabb = aabb_half + aabb_half.T + aabb_split + aabb_split.T
    return np.diag(aaab).copy(), aaab, aabb


def _brute_source(weight: np.ndarray, table: np.ndarray):
    outputs = weight.shape[1]
    aaaa = np.zeros(outputs, dtype=np.float64)
    aaab = np.zeros((outputs, outputs), dtype=np.float64)
    aabb = np.zeros_like(aaab)
    for i in range(weight.shape[0]):
        for j in range(weight.shape[0]):
            for k in range(weight.shape[0]):
                coefficient = float(table[i, j, k])
                if coefficient == 0.0:
                    continue
                f4, f31, f22 = _half_feature(weight, i, j, k)
                aaaa += coefficient * f4
                aaab += coefficient * f31
                aabb += coefficient * f22
    return aaaa, aaab, aabb


def _physical_rankone_table(u: np.ndarray) -> np.ndarray:
    """Independent M167 table for KAPPA*u^tensor4."""

    width = u.size
    answer = np.zeros((width, width, width), dtype=np.float64)
    for i in range(width):
        for j in range(width):
            for k in range(width):
                if i == j == k:
                    answer[i, j, k] = KAPPA * u[i] ** 4 / 6.0
                elif i == j and k != i:
                    answer[i, j, k] = KAPPA * u[i] ** 3 * u[k] / 3.0
                elif i == k and j != i:
                    answer[i, j, k] = KAPPA * u[i] ** 3 * u[j] / 3.0
                elif j == k and i != j:
                    answer[i, j, k] = KAPPA * u[i] ** 2 * u[j] ** 2 / 2.0
                else:
                    answer[i, j, k] = KAPPA * u[i] ** 2 * u[j] * u[k]
    return answer


def _all_four_distinct_wedge(weight: np.ndarray, u: np.ndarray):
    """Independent `[1,1,1,1]` sector omitted by the current Source211 owner."""

    outputs = weight.shape[1]
    aaab = np.zeros((outputs, outputs), dtype=np.float64)
    aabb = np.zeros_like(aaab)
    for labels in itertools.combinations(range(weight.shape[0]), 4):
        rows = [weight[index] for index in labels]
        coefficient = KAPPA * float(np.prod(u[list(labels)]))
        for singleton in range(4):
            others = [index for index in range(4) if index != singleton]
            aaab += 6.0 * coefficient * np.outer(
                rows[others[0]] * rows[others[1]] * rows[others[2]], rows[singleton]
            )
        for pair in itertools.combinations(range(4), 2):
            complement = [index for index in range(4) if index not in pair]
            aabb += 4.0 * coefficient * np.outer(
                rows[pair[0]] * rows[pair[1]],
                rows[complement[0]] * rows[complement[1]],
            )
    return np.diag(aaab).copy(), aaab, aabb


def _arbitrary_physical_target(width: int, rng: np.random.Generator) -> np.ndarray:
    target = np.zeros((width, width, width), dtype=np.float64)
    k4 = rng.normal(size=width)
    k31 = rng.normal(size=(width, width))
    k22 = rng.normal(size=(width, width))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k31, 0.0)
    np.fill_diagonal(k22, 0.0)
    for i in range(width):
        target[i, i, i] = k4[i] / 6.0
        for j in range(width):
            if i == j:
                continue
            target[i, i, j] = k31[i, j] / 3.0
            target[i, j, i] = k31[i, j] / 3.0
            target[i, j, j] = k22[i, j] / 2.0
        for j in range(width):
            for k in range(j + 1, width):
                if i == j or i == k:
                    continue
                value = float(rng.normal())
                target[i, j, k] = value
                target[i, k, j] = value
    return target


def _max_source_error(observed, expected) -> float:
    return float(
        max(
            np.max(np.abs(observed.aaaa - expected[0])),
            np.max(np.abs(observed.aaab - expected[1])),
            np.max(np.abs(observed.aabb - expected[2])),
        )
    )


class M208PhysicalRankOneCumulantControlTests(unittest.TestCase):
    def test_predeclared_p_only_gate_is_killed_above_width_three(self):
        measured = {}
        for width in (3, 4, 5, 6, 7):
            rng = np.random.Generator(np.random.Philox(208000 + width))
            weight = rng.normal(size=(width, width + 2))
            u = rng.normal(size=width)
            observed = m208.compile_physical_rankone_control(weight, u, KAPPA)
            expected = _brute_source(weight, _physical_rankone_table(u))
            measured[width] = _max_source_error(observed, expected)
            np.testing.assert_array_equal(observed.aaaa, np.diag(observed.aaab))
            np.testing.assert_allclose(observed.aabb, observed.aabb.T, rtol=0.0, atol=2e-13)
        self.assertLessEqual(measured[3], 5e-10)
        for width in (4, 5, 6, 7):
            self.assertGreater(measured[width], 5e-10)

    def test_failure_is_exactly_the_missing_all_four_distinct_wedge(self):
        for width in (4, 5, 6, 7):
            rng = np.random.Generator(np.random.Philox(208000 + width))
            weight = rng.normal(size=(width, width + 2))
            u = rng.normal(size=width)
            full = m208.compile_physical_rankone_control(weight, u, KAPPA)
            owned = _brute_source(weight, _physical_rankone_table(u))
            wedge = _all_four_distinct_wedge(weight, u)
            reconstructed = m208.Source211(
                owned[0] + wedge[0], owned[1] + wedge[1], owned[2] + wedge[2]
            )
            self.assertLessEqual(m208.source_max_abs_difference(full, reconstructed), 8e-10)

    def test_new_control_preserves_distinct_rows_and_changes_collision_normalization(self):
        u = np.asarray([0.7, -1.1, 0.4, 1.3], dtype=np.float64)
        physical = _physical_rankone_table(u)
        old = KAPPA * np.einsum("i,j,k->ijk", u * u, u, u)
        for i in range(u.size):
            for j in range(u.size):
                for k in range(u.size):
                    if len({i, j, k}) == 3:
                        self.assertEqual(float(physical[i, j, k]), float(old[i, j, k]))
        self.assertNotEqual(float(physical[0, 0, 0]), float(old[0, 0, 0]))
        self.assertNotEqual(float(physical[0, 0, 1]), float(old[0, 0, 1]))
        self.assertNotEqual(float(physical[0, 1, 1]), float(old[0, 1, 1]))

    def test_p_only_control_violates_current_owner_conservation_but_table_control_does_not(self):
        for width in (3, 5, 7):
            rng = np.random.Generator(np.random.Philox(208100 + width))
            weight = rng.normal(size=(width, width + 1))
            u = rng.normal(size=width)
            target = _arbitrary_physical_target(width, rng)
            control = _physical_rankone_table(u)
            residual = target - control
            direct = _brute_source(weight, target)
            c = m208.compile_physical_rankone_control(weight, u, KAPPA)
            r = _brute_source(weight, residual)
            reconstructed = (c.aaaa + r[0], c.aaab + r[1], c.aabb + r[2])
            p_only_error = _max_source_error(m208.Source211(*reconstructed), direct)
            if width == 3:
                self.assertLessEqual(p_only_error, 8e-10)
            else:
                self.assertGreater(p_only_error, 8e-10)
            exact_control = _brute_source(weight, control)
            exact_reconstructed = (
                exact_control[0] + r[0],
                exact_control[1] + r[1],
                exact_control[2] + r[2],
            )
            self.assertLessEqual(
                _max_source_error(m208.Source211(*exact_reconstructed), direct), 8e-10
            )

    def test_permutation_positive_gauge_and_zero_factor(self):
        rng = np.random.Generator(np.random.Philox(208200))
        width = 7
        weight = rng.normal(size=(width, width + 3))
        u = rng.normal(size=width)
        baseline = m208.compile_physical_rankone_control(weight, u, KAPPA)
        permutation = rng.permutation(width)
        permuted = m208.compile_physical_rankone_control(weight[permutation], u[permutation], KAPPA)
        self.assertLessEqual(m208.source_max_abs_difference(baseline, permuted), 2e-12)
        gauge = np.exp(rng.uniform(-0.8, 0.8, size=width))
        gauged = m208.compile_physical_rankone_control(weight / gauge[:, None], u * gauge, KAPPA)
        self.assertLessEqual(m208.source_max_abs_difference(baseline, gauged), 2e-12)
        zero = m208.compile_physical_rankone_control(weight, np.zeros(width), KAPPA)
        np.testing.assert_array_equal(zero.aaaa, np.zeros(weight.shape[1]))
        np.testing.assert_array_equal(zero.aaab, np.zeros((weight.shape[1], weight.shape[1])))
        np.testing.assert_array_equal(zero.aabb, np.zeros((weight.shape[1], weight.shape[1])))

    def test_compiler_source_contains_no_dense_gram_or_cubic_table_path(self):
        source = inspect.getsource(m208).lower()
        for forbidden in (
            "einsum",
            "rho",
            "diag(u",
            "u * u)[:, none] * w",
            "range(weight.shape[0])",
            "range(width)",
        ):
            self.assertNotIn(forbidden, source)

    def test_static_bill_is_far_below_strict_composed_headroom(self):
        ledger = m208.static_operation_ledger(width=256, layers=31)
        self.assertEqual(ledger["projection_bill"], 8_110_592)
        self.assertLess(ledger["declared_raw_upper"], 25_000_000)
        self.assertLess(ledger["declared_raw_upper"], 1_986_871_472)
        self.assertEqual(ledger["dense_square_calls"], 0)
        self.assertEqual(ledger["bias_class"], "invalid_for_current_owner_domain_missing_1111")
        self.assertFalse(ledger["candidate_gate_passed"])
        self.assertFalse(ledger["native_cost_certified"])


if __name__ == "__main__":
    unittest.main()
