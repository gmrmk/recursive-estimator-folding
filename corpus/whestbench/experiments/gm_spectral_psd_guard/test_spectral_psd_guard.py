"""Tests for the additive spectral PSD guard.

Stdlib unittest + numpy only; no dependency on the frozen M179 producer, so this
suite runs on a checkout that does not yet carry PR #1.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

SPEC = importlib.util.spec_from_file_location(
    "spectral_psd_guard", Path(__file__).resolve().parent / "spectral_psd_guard.py"
)
G = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
# Register before exec: @dataclass resolves cls.__module__ through sys.modules,
# and raises AttributeError on a module loaded by path alone.
sys.modules[SPEC.name] = G
SPEC.loader.exec_module(G)


class SpectralGuardTests(unittest.TestCase):
    def test_identity_is_safe(self):
        state = G.require_spd(np.eye(8), layer=1)
        self.assertTrue(state.safe)
        self.assertAlmostEqual(state.min_eigenvalue, 1.0, places=12)
        self.assertEqual(state.width, 8)

    def test_refuses_negative_eigenvalue(self):
        C = np.diag([1.0, 1.0, -1e-9])
        with self.assertRaises(G.SpectralPSDRefusal) as ctx:
            G.require_spd(C, layer=13)
        self.assertIn("layer 13", str(ctx.exception))

    def test_refuses_at_the_floor_not_only_below_zero(self):
        """The floor is 1e-12, so a tiny positive eigenvalue must still fail.

        This is the case the per-pair guard cannot see at all: every pairwise
        correlation can be far inside RHO_MAX while the spectrum is degenerate.
        """
        C = np.diag([1.0, 1.0, 1e-13])
        self.assertFalse(G.inspect(C).safe)
        with self.assertRaises(G.SpectralPSDRefusal):
            G.require_spd(C)

    def test_rank_deficient_gram_is_refused(self):
        rng = np.random.default_rng(20260810)
        A = rng.standard_normal((16, 4))
        C = A @ A.T                       # rank 4 in dimension 16
        with self.assertRaises(G.SpectralPSDRefusal):
            G.require_spd(C)

    def test_pairwise_rho_can_pass_while_spectrum_fails(self):
        """The defect this guard exists for, as an exact witness.

        The equicorrelation matrix (1-r)I + r*11^T has eigenvalues 1+(n-1)r once
        and 1-r with multiplicity n-1. At r = -1/(n-1) the first is exactly 0,
        so the matrix is singular -- while EVERY pairwise correlation is exactly
        -1/(n-1) = -0.2 for n=6, nowhere near RHO_MAX.

        A per-pair guard sees six harmless correlations. The matrix is singular.
        """
        n = 6
        r = -1.0 / (n - 1)
        C = (1.0 - r) * np.eye(n) + r * np.ones((n, n))
        d = np.sqrt(np.diag(C))
        rho = C / np.outer(d, d)
        off = rho[~np.eye(n, dtype=bool)]
        self.assertAlmostEqual(float(np.max(np.abs(off))), 0.2, places=12)
        self.assertLess(np.max(np.abs(off)), 0.9999999999999998)   # per-pair OK
        self.assertLess(abs(float(np.linalg.eigvalsh(C)[0])), 1e-14)  # singular
        self.assertFalse(G.inspect(C).safe)                        # spectrum not
        with self.assertRaises(G.SpectralPSDRefusal):
            G.require_spd(C, layer=1)

    def test_does_not_mutate_input(self):
        C = np.array([[2.0, 0.5], [0.4, 2.0]])          # deliberately asymmetric
        before = C.copy()
        G.inspect(C)
        np.testing.assert_array_equal(C, before)

    def test_symmetrizes_before_inspecting(self):
        C = np.array([[2.0, 0.5], [0.4, 2.0]])
        state = G.inspect(C)
        expected = np.linalg.eigvalsh(0.5 * (C + C.T))
        self.assertAlmostEqual(state.min_eigenvalue, float(expected[0]), places=12)

    def test_roundoff_dominated_classification(self):
        big = np.diag([1e8, 1e8, 1e-9])                 # min eig under eps*n*lmax
        self.assertTrue(G.inspect(big).roundoff_dominated)
        small = np.diag([1.0, 1.0, -0.5])               # far above round-off
        self.assertFalse(G.inspect(small).roundoff_dominated)

    def test_rejects_non_square(self):
        with self.assertRaises(ValueError):
            G.inspect(np.zeros((3, 4)))

    def test_guarded_recurrence_raises_at_first_unsafe_layer(self):
        """A stub producer that deflates V reaches the floor at a known layer."""
        class Step:
            def __init__(self, mu, V):
                self.mu, self.V = mu, V

        def shrinking_relu_moments(a, C):
            return Step(np.zeros_like(a), np.asarray(C) * 1e-4)

        rng = np.random.default_rng(7)
        weights = [rng.standard_normal((5, 5)) / np.sqrt(5) for _ in range(32)]
        with self.assertRaises(G.SpectralPSDRefusal):
            G.guarded_zero_order_recurrence(weights, shrinking_relu_moments)

    def test_guarded_recurrence_passes_when_state_stays_spd(self):
        class Step:
            def __init__(self, mu, V):
                self.mu, self.V = mu, V

        def identity_relu_moments(a, C):
            return Step(np.zeros_like(a), np.eye(C.shape[0]))

        rng = np.random.default_rng(11)
        weights = [rng.standard_normal((6, 6)) / np.sqrt(6) for _ in range(32)]
        states = G.guarded_zero_order_recurrence(weights, identity_relu_moments)
        self.assertEqual(len(states), 32)
        self.assertTrue(all(s.safe for s in states))


if __name__ == "__main__":
    unittest.main()
