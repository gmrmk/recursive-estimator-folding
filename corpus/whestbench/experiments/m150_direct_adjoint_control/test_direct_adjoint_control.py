"""Generated-only parity tests for M150 direct-adjoint algebra."""

from __future__ import annotations

import unittest

import numpy as np

from direct_adjoint_control import (
    CanonicalState,
    ResponseDual,
    canonical_delta_tilde,
    contract_source,
    covariance_star,
    dense_c211,
    direct_aaab_simplified,
    direct_c211_dual_contract,
    feature_211,
    full_dual_static_lower_bound,
    generic_cp_rank_dimension_lower_bound,
    local_feature_dual_formula,
)


def _state(seed: int, cells: int, width: int) -> CanonicalState:
    rng = np.random.Generator(np.random.Philox(seed))
    # The cells are deliberately signed: this tests the moment-functional
    # semantics rather than silently turning Smolyak cubature into a mixture.
    omega = rng.normal(size=cells)
    omega /= np.sum(omega)
    return CanonicalState(
        omega=omega,
        conditional_mean=rng.normal(scale=0.4, size=(cells, width)),
        conditional_variance=0.05 + rng.random((cells, width)),
    )


class DirectAdjointParityTest(unittest.TestCase):
    def test_covariance_star_and_ordered_singleton_exclusions(self) -> None:
        state = _state(15001, cells=7, width=5)
        delta = canonical_delta_tilde(state)
        v = covariance_star(state)
        self.assertTrue(np.all(np.isfinite(v)))
        for i in range(5):
            for j in range(5):
                self.assertEqual(delta[i, i, j], 0.0)
                self.assertEqual(delta[i, j, i], 0.0)
                self.assertEqual(delta[j, i, i], 0.0)
        self.assertLess(np.max(np.abs(delta - delta.swapaxes(1, 2))), 2e-13)

    def test_dense_source_equals_direct_dual_for_b_1_2_4(self) -> None:
        # B labels independently formed canonical blocks.  Every block gets
        # three signed nodes, enough to exercise the covariance-star term.
        for blocks in (1, 2, 4):
            rng = np.random.Generator(np.random.Philox(15010 + blocks))
            width, output_width = 5, 4
            state = _state(15100 + blocks, cells=3 * blocks, width=width)
            delta = canonical_delta_tilde(state)
            weight = rng.normal(size=(width, output_width))
            dual = ResponseDual(
                aaaa=rng.normal(size=(3, output_width)),
                aaab=rng.normal(size=(3, output_width, output_width)),
                aabb=rng.normal(size=(3, output_width, output_width)),
            )
            dense = dense_c211(weight, delta)
            reference = contract_source(dense, dual)
            direct = direct_c211_dual_contract(weight, delta, dual)
            self.assertLess(np.max(np.abs(reference - direct)), 3e-11)
            self.assertLess(
                np.max(np.abs(dense.aaab - direct_aaab_simplified(weight, delta))),
                3e-11,
            )
            self.assertLess(np.max(np.abs(dense.aaaa - np.diag(dense.aaab))), 3e-12)

    def test_closed_local_formula_includes_all_three_slots(self) -> None:
        rng = np.random.Generator(np.random.Philox(15029))
        weight = rng.normal(size=(5, 4))
        dual = ResponseDual(
            aaaa=rng.normal(size=(3, 4)),
            aaab=rng.normal(size=(3, 4, 4)),
            aabb=rng.normal(size=(3, 4, 4)),
        )
        feature = feature_211(weight, 0, 2, 4)
        direct = (
            dual.aaaa @ feature.aaaa
            + np.einsum("oab,ab->o", dual.aaab, feature.aaab)
            + np.einsum("oab,ab->o", dual.aabb, feature.aabb)
        )
        closed = local_feature_dual_formula(weight, 0, 2, 4, dual)
        self.assertLess(np.max(np.abs(direct - closed)), 5e-12)

    def test_generic_all_output_dual_is_not_a_small_shared_cp_object(self) -> None:
        # Dimension counting, not numerical rank truncation: a generic n^3
        # response tensor cannot be parameterized by O(n) shared components.
        n = 256
        lower = generic_cp_rank_dimension_lower_bound(n)
        self.assertGreaterEqual(lower, 21846)
        ledger = full_dual_static_lower_bound(n, layers=30)
        self.assertEqual(ledger["full_dual_entries"], n**3)
        self.assertEqual(ledger["full_dual_bytes_float64"], 134217728)
        self.assertGreater(ledger["all_output_affine_pullback_total"], 1_000_000_000_000)


if __name__ == "__main__":
    unittest.main()
