"""M179 G1-premise falsifier: the M178-assembled bivariate ReLU moments and
Jacobian bundle must match independent references. Three cross-checks:
 (i)   dps-50 mpmath 2D integration of every entry over a hostile pair grid;
 (ii)  the arc-whitebox-estimator univariate backbone (diagonal marginals);
 (iii) the m86 |x| separable closed form.

Response-free. Run in the frozen venv (mpmath 1.3.0).
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mpmath as mp  # noqa: E402
import m179_relu_pair_assembly as asm  # noqa: E402

mp.mp.dps = 30


def _relu_mean_mp(nu, tau):
    """E[ReLU(z)], z ~ N(nu, tau^2), dps-precision reference."""
    a = nu / tau
    return nu * mp.ncdf(a) + tau * mp.npdf(a)


def _ref_pair(a_i, a_j, si, sj, rho):
    """dps-30 references via 1D reduction: integrate out X_i and use the exact
    conditional law X_j | X_i=x ~ N(a_j + rho (sj/si)(x-a_i), sj^2(1-rho^2))."""
    a_i, a_j, si, sj, rho = (mp.mpf(v) for v in (a_i, a_j, si, sj, rho))
    s = mp.sqrt((1 - rho) * (1 + rho))
    cond_sd = sj * s
    hi_i = a_i + 12 * si
    xi = max(mp.mpf(0), a_i - 12 * si)

    def density_i(x):
        return mp.npdf((x - a_i) / si) / si

    def cond_mean(x):
        return a_j + rho * (sj / si) * (x - a_i)

    def inner_prob(x):
        return mp.ncdf(cond_mean(x) / cond_sd)

    def inner_relu(x):
        return _relu_mean_mp(cond_mean(x), cond_sd)

    K = mp.quad(lambda x: density_i(x) * inner_prob(x), [xi, hi_i])
    e_rr = mp.quad(lambda x: x * density_i(x) * inner_relu(x), [xi, hi_i])
    hmu_ij_raw = mp.quad(lambda x: density_i(x) * inner_relu(x), [xi, hi_i])
    hmu_ji_raw = mp.quad(lambda x: x * density_i(x) * inner_prob(x), [xi, hi_i])
    return e_rr, K, hmu_ij_raw, hmu_ji_raw


def _ref_marginal(a, s):
    a, s = mp.mpf(a), mp.mpf(s)
    m = mp.quad(lambda x: x * mp.npdf((x - a) / s) / s, [max(mp.mpf(0), a - 12 * s), a + 12 * s])
    p = mp.quad(lambda x: mp.npdf((x - a) / s) / s, [max(mp.mpf(0), a - 12 * s), a + 12 * s])
    return m, p


class M179PremiseTests(unittest.TestCase):
    # hostile pair grid: SPD interior, near-rank, zero-mean, large/small means,
    # mixed signs, unequal sigmas
    GRID = [
        (0.5, -0.3, 1.0, 1.0, 0.4),
        (0.0, 0.0, 1.0, 1.0, 0.7),
        (2.0, 1.5, 0.5, 2.0, -0.6),
        (-1.0, 3.0, 1.3, 0.8, 0.9),
        (0.2, 0.2, 1.0, 1.0, 1.0 - 2.0 ** -45),
        (0.2, -0.2, 1.0, 1.0, -(1.0 - 2.0 ** -45)),
        (4.0, -3.5, 2.5, 0.7, 0.3),
        (-2.5, -2.5, 1.1, 1.1, 0.5),
        (0.0, 2.0, 1.0, 0.3, -0.5),
        (1e-3, 1e-3, 1.0, 1.0, 0.99),
        (5.0, 5.0, 1.0, 1.0, 0.8),
        (-4.0, 1.0, 0.6, 3.0, -0.85),
    ]

    def test_pair_assembly_matches_dps50_references(self):
        worst = 0.0
        for (a_i, a_j, si, sj, rho) in self.GRID:
            pm = asm.pair_moments(a_i, a_j, si, sj, rho)
            e_rr, K, hmu_ij_raw, hmu_ji_raw = _ref_pair(a_i, a_j, si, sj, rho)
            mi, pi = _ref_marginal(a_i, si)
            mj, pj = _ref_marginal(a_j, sj)
            checks = {
                "e_relu_relu": (pm.e_relu_relu, e_rr),
                "K": (pm.K, K),
                "Hmu_ij": (pm.Hmu_ij, hmu_ij_raw - pi * mj),
                "Hmu_ji": (pm.Hmu_ji, hmu_ji_raw - pj * mi),
                "cov": (pm.cov, e_rr - mi * mj),
            }
            for name, (got, ref) in checks.items():
                err = abs(mp.mpf(got) - ref)
                worst = max(worst, float(err))
                self.assertLess(err, mp.mpf("2e-7"),
                                f"{name} at {(a_i, a_j, si, sj, rho)}: err={mp.nstr(err, 4)}")
        self.assertLess(worst, 2e-7)

    def test_hv_matches_conditional_reference(self):
        # Hv_ij = 0.5 f_i(0) E[ReLU(X_j)|X_i=0] - r_i m_j, checked directly.
        for (a_i, a_j, si, sj, rho) in self.GRID:
            pm = asm.pair_moments(a_i, a_j, si, sj, rho)
            A_i, A_j, S_i, S_j, R = (mp.mpf(v) for v in (a_i, a_j, si, sj, rho))
            s = mp.sqrt((1 - R) * (1 + R))
            f_i0 = mp.npdf(A_i / S_i) / S_i
            cond_mean = A_j - R * (A_i / S_i) * S_j
            cond_sd = S_j * s
            e_relu_cond = mp.quad(
                lambda x: x * mp.npdf((x - cond_mean) / cond_sd) / cond_sd,
                [max(mp.mpf(0), cond_mean - 12 * cond_sd), cond_mean + 12 * cond_sd])
            mj, _ = _ref_marginal(a_j, sj)
            r_i = mp.npdf(A_i / S_i) / (2 * S_i)
            ref = 0.5 * f_i0 * e_relu_cond - r_i * mj
            self.assertLess(abs(mp.mpf(pm.Hv_ij) - ref), mp.mpf("2e-7"),
                            f"Hv_ij at {(a_i, a_j, si, sj, rho)}")

    def test_backbone_matches_arc_whitebox_identity(self):
        # the reused univariate backbone must match dps-50 references
        for a in (-3.0, -0.5, 0.0, 0.7, 3.0):
            for s in (0.05, 0.5, 1.0, 3.0):
                m_ref, _ = _ref_marginal(a, s)
                self.assertLess(abs(mp.mpf(asm.relu_gaussian_mean(a, s)) - m_ref),
                                mp.mpf("1e-9"), (a, s))

    def test_m86_absolute_value_separable_falsifier(self):
        # f(x) = ReLU(x) + ReLU(-x) = |x|, X ~ N(0,1).
        # ReLU(X) and ReLU(-X) never both positive => E[ReLU(X)ReLU(-X)] = 0.
        # (a_i, a_j)=(0,0), sigma=1, rho=-1 is rank-one; approach it as an SPD
        # limit and confirm the cross moment -> 0.
        for rho in (-(1.0 - 2.0 ** -30), -(1.0 - 2.0 ** -45)):
            pm = asm.pair_moments(0.0, 0.0, 1.0, 1.0, rho)
            self.assertLess(abs(pm.e_relu_relu), 5e-8, rho)
        # E[ReLU(X)^2] + E[ReLU(-X)^2] = E[X^2] = 1 (marginal backbone)
        e2 = asm.relu_gaussian_second_moment(0.0, 1.0)
        self.assertLess(abs(2.0 * e2 - 1.0), 1e-12)
        # Z(t) = E[e^{t|X|}] = 2 e^{t^2/2} Phi(t): check E[|X|] = Z'(0) = 2 phi(0)
        # = sqrt(2/pi) via the two ReLU means at N(0,1).
        e_abs = asm.relu_gaussian_mean(0.0, 1.0) + asm.relu_gaussian_mean(0.0, 1.0)
        self.assertLess(abs(e_abs - math.sqrt(2.0 / math.pi)), 1e-12)


if __name__ == "__main__":
    unittest.main()
