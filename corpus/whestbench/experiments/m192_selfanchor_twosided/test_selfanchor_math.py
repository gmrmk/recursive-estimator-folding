"""Standalone checks of the STEP 0 algebra, independent of any cached data.

Each test re-derives a claim in PREDECLARATION.md section 0 a second way.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Set before importing the frozen M192/M194 modules: the import machinery
# writes __pycache__ next to the source it loads, and the frozen directory
# must stay write-free.  run_m192_g0 sets this flag too, but only while its
# own body executes -- by then its own .pyc has already been written.
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
M192 = HERE.parent / "m192_cross_output_gls"
sys.path.insert(0, str(M192))
sys.path.insert(0, str(HERE))

import run_m192_g0 as m192  # noqa: E402
import run_m194_g0 as m194  # noqa: E402
import run_selfanchor_g0 as sa  # noqa: E402

P = 126
U = np.ones(P) / np.sqrt(P)
PROJ = np.eye(P) - np.outer(U, U)


class Step0Algebra(unittest.TestCase):
    def test_sum_one_gls_needs_the_cross_block_not_only_PCP(self) -> None:
        """w* = 1/p - (1/sqrt p) (PCP)^+ P C u, and it moves with b alone."""
        rng = np.random.default_rng(1920001)
        f = rng.normal(size=(P, 400))
        c = f @ f.T / 400 + 0.5 * np.eye(P)
        w_solver, _ = m192._weights(c, 0.0)  # alpha=0 -> unshrunk C^{-1}1 rule

        a = PROJ @ c @ PROJ
        b = PROJ @ c @ U
        v = -np.linalg.pinv(a) @ b / np.sqrt(P)
        w_block = np.full(P, 1.0 / P) + v
        np.testing.assert_allclose(w_solver, w_block, rtol=1e-8, atol=1e-10)

        # Same A, different b -> different solution. So A alone cannot decide w.
        d = rng.normal(size=P)
        d -= d.mean()
        c2 = c + np.outer(d, np.ones(P)) + np.outer(np.ones(P), d)
        np.testing.assert_allclose(PROJ @ c2 @ PROJ, a, rtol=1e-10, atol=1e-12)
        w2, _ = m192._weights(c2, 0.0)
        self.assertGreater(float(np.linalg.norm(w2 - w_solver)), 1e-6)

    def test_b_zero_forces_uniform_for_every_positive_alpha(self) -> None:
        rng = np.random.default_rng(1920002)
        f = rng.normal(size=(P, 400))
        c = PROJ @ (f @ f.T / 400) @ PROJ  # b = 0 by construction
        for alpha in (0.25, 0.5, 0.75, 0.9, 0.99):
            w, _ = m192._weights(c, alpha)
            np.testing.assert_allclose(w, np.full(P, 1.0 / P),
                                       rtol=0, atol=1e-12)

    def test_selfanchor_makes_Pq_exactly_cancel_the_signal(self) -> None:
        """q = -(1/p) C_e 1 and hence P C_a 1 = P C_e 1 + p P q = 0."""
        rng = np.random.default_rng(1920003)
        n = 512
        mu = rng.normal(size=n)
        factor = rng.normal(size=(P, 9))
        e = factor @ rng.normal(size=(9, n)) + 0.3 * rng.normal(size=(P, n))
        x = np.outer(np.ones(P), mu) + e

        ce = e @ e.T / n
        anchor = x.mean(axis=0)
        delta = mu - anchor
        q = e @ delta / n
        np.testing.assert_allclose(q, -(ce @ np.ones(P)) / P,
                                   rtol=1e-10, atol=1e-14)

        r = x - anchor[None, :]
        ca = r @ r.T / n
        np.testing.assert_allclose(PROJ @ ca @ PROJ, PROJ @ ce @ PROJ,
                                   rtol=1e-9, atol=1e-16)
        one = np.ones(P)
        lhs = PROJ @ ca @ one
        rhs = PROJ @ ce @ one + P * (PROJ @ q)
        scale = float(np.linalg.norm(PROJ @ ce @ one))
        self.assertGreater(scale, 1e-6)  # the signal the solver needs is real
        # Both sides are zero to double-precision roundoff at this scale.
        np.testing.assert_allclose(lhs, rhs, rtol=1e-6, atol=1e-12 * scale)
        self.assertLess(float(np.linalg.norm(lhs)) / scale, 1e-12)
        self.assertLess(float(np.linalg.norm(rhs)) / scale, 1e-12)

    def test_selfanchor_second_moment_annihilates_ones(self) -> None:
        rng = np.random.default_rng(1920004)
        x = np.outer(np.ones(P), rng.normal(size=256)) + rng.normal(size=(P, 256))
        c = sa.self_second_moment(x, np.arange(256))
        rel = float(np.linalg.norm(c @ np.ones(P)) /
                    (np.linalg.norm(c) * np.sqrt(P)))
        self.assertLess(rel, 1e-14)
        w, _ = m192._weights(c, 0.25)
        self.assertLess(float(np.max(np.abs(w - 1.0 / P))) * P, 1e-10)

    def test_m194_cross_block_is_identically_zero_under_self_anchor(self) -> None:
        rng = np.random.default_rng(1920005)
        x = np.outer(np.ones(P), rng.normal(size=256)) + rng.normal(size=(P, 256))
        train = np.arange(224)
        anchor = x.mean(axis=0)
        w, diag = m194._block_weights(x, anchor, train)
        self.assertLess(diag["cross_norm"], 1e-14)
        np.testing.assert_allclose(w, np.full(P, 1.0 / P), rtol=0, atol=1e-13)
        # A generic anchor keeps a nonzero cross block, so the solver is alive.
        _, gdiag = m194._block_weights(x, anchor + rng.normal(size=256), train)
        self.assertGreater(gdiag["cross_norm"], 1e-3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
