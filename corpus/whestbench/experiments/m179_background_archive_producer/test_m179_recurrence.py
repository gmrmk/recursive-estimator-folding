"""M179 G2: the full-covariance zero-order recurrence must reproduce an
INDEPENDENT dps-30 mpmath computation of the same Gaussian closure on generated
small MLPs, and must be exact at layer 1 (where the closure is the true law).

Two references:
 (i)  an mpmath closure that recomputes (mu_l, V_l) with 1D-reduced pair
      integrals, wholly independent of the M178 provider;
 (ii) a large Monte-Carlo of the TRUE network at layer 1 only (there the
      Gaussian closure is exact, so producer == truth up to MC noise).

Response-free: GENERATED He-Gaussian weights only; no challenge weights,
target, scorer, or model loop.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mpmath as mp  # noqa: E402
import m179_background_producer as prod  # noqa: E402

mp.mp.dps = 30


def _gen_weights(n, depth, seed):
    """He-Gaussian square weights (competition family), row-vector convention."""
    rng = np.random.default_rng(seed)
    gain = np.sqrt(2.0 / n)
    return [rng.standard_normal((n, n)).astype(np.float64) * gain
            for _ in range(depth)]


# ---- independent mpmath closure reference -------------------------------

def _relu_mean_mp(a, s):
    if s <= 0:
        return max(mp.mpf(0), a)
    r = a / s
    return a * mp.ncdf(r) + s * mp.npdf(r)


def _relu_second_mp(a, s):
    if s <= 0:
        return max(mp.mpf(0), a) ** 2
    r = a / s
    return (a * a + s * s) * mp.ncdf(r) + a * s * mp.npdf(r)


def _pair_e_relu_relu_mp(a_i, a_j, si, sj, rho):
    s = mp.sqrt((1 - rho) * (1 + rho))
    cond_sd = sj * s
    hi = a_i + 12 * si
    lo = max(mp.mpf(0), a_i - 12 * si)

    def integrand(x):
        dens = mp.npdf((x - a_i) / si) / si
        cond_mean = a_j + rho * (sj / si) * (x - a_i)
        return x * dens * _relu_mean_mp(cond_mean, cond_sd)

    return mp.quad(integrand, [lo, hi])


def _closure_recurrence_mp(weights):
    n = weights[0].shape[0]
    mu = mp.matrix(n, 1)
    V = mp.eye(n)
    out = []
    for W in weights:
        Wm = mp.matrix(W.tolist())
        a = Wm.T * mu
        C = Wm.T * V * Wm
        sigma = [mp.sqrt(C[i, i]) for i in range(n)]
        mu_new = mp.matrix(n, 1)
        V_new = mp.matrix(n, n)
        for i in range(n):
            mu_new[i] = _relu_mean_mp(a[i], sigma[i])
            V_new[i, i] = _relu_second_mp(a[i], sigma[i]) - mu_new[i] ** 2
        for i in range(n):
            for j in range(i + 1, n):
                rho = C[i, j] / (sigma[i] * sigma[j])
                e_rr = _pair_e_relu_relu_mp(a[i], a[j], sigma[i], sigma[j], rho)
                cov = e_rr - mu_new[i] * mu_new[j]
                V_new[i, j] = cov
                V_new[j, i] = cov
        mu, V = mu_new, V_new
        out.append((mu, V))
    return out


class M179RecurrenceTests(unittest.TestCase):
    def test_recurrence_matches_independent_mpmath_closure(self):
        weights = _gen_weights(n=5, depth=3, seed=20260807)
        states = prod.zero_order_recurrence(weights)
        ref = _closure_recurrence_mp(weights)
        worst_mu = worst_V = 0.0
        for l, (state, (mu_ref, V_ref)) in enumerate(zip(states, ref)):
            n = state.mu.size
            for i in range(n):
                worst_mu = max(worst_mu, float(abs(mp.mpf(state.mu[i]) - mu_ref[i])))
                for j in range(n):
                    worst_V = max(worst_V,
                                  float(abs(mp.mpf(state.V[i, j]) - V_ref[i, j])))
        self.assertLess(worst_mu, 5e-7, f"worst mu err {worst_mu}")
        self.assertLess(worst_V, 5e-7, f"worst V err {worst_V}")

    def test_layer1_matches_true_network_monte_carlo(self):
        # At layer 1 the Gaussian closure is EXACT (inputs jointly Gaussian).
        weights = _gen_weights(n=6, depth=1, seed=11)
        state = prod.zero_order_recurrence(weights)[0]
        W = weights[0]
        rng = np.random.default_rng(3)
        N = 4_000_000
        x = rng.standard_normal((N, W.shape[0]))
        z = x @ W
        a = np.maximum(z, 0.0)
        mu_mc = a.mean(axis=0)
        V_mc = np.cov(a, rowvar=False, bias=True)
        # MC std error ~ 1/sqrt(N) ~ 5e-4; comfortable tolerance
        self.assertLess(np.max(np.abs(state.mu - mu_mc)), 3e-3)
        self.assertLess(np.max(np.abs(state.V - V_mc)), 3e-3)

    def test_V_is_bitwise_symmetric_and_finite(self):
        weights = _gen_weights(n=7, depth=4, seed=99)
        for state in prod.zero_order_recurrence(weights):
            self.assertTrue(np.array_equal(state.V, state.V.T))
            self.assertTrue(np.all(np.isfinite(state.V)))
            self.assertTrue(np.all(np.isfinite(state.mu)))
            self.assertGreater(state.strata["spd"], 0)

    def test_no_banned_markers_in_source(self):
        src = (HERE / "m179_background_producer.py").read_text()
        for banned in ("_phi2_gauss10", "1e-24", "clip(", "np.clip", "ndtr", "scipy"):
            self.assertNotIn(banned, src)


if __name__ == "__main__":
    unittest.main()
