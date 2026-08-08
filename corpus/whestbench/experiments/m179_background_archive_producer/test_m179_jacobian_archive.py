"""M179 G3: the Jacobian bundle constructs a valid m125 LocalReluJacobian, its
diagonal entries match direct dps-30 references, the zero-variance limit matches
its definition, non-PSD and rank-one fail closed, and the labelled archive runs
end-to-end on generated MLPs. Response-free.
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
import m179_jacobian_archive as ja  # noqa: E402
import m179_background_producer as prod  # noqa: E402
from m125_forward_tangent import LocalReluJacobian, relu_tangent, TangentState  # noqa: E402

mp.mp.dps = 30


def _gen_weights(n, depth, seed):
    rng = np.random.default_rng(seed)
    gain = np.sqrt(2.0 / n)
    return [rng.standard_normal((n, n)).astype(np.float64) * gain
            for _ in range(depth)]


def _spd_state(n, seed):
    """A generic SPD (a, C): random mean and C = M M^T + small ridge for
    strict PD (the ridge is a TEST-input construction, not an estimator clip)."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal(n)
    M = rng.standard_normal((n, n))
    C = M @ M.T + 0.5 * np.eye(n)
    return a, C


class M179JacobianTests(unittest.TestCase):
    def test_constructs_valid_local_relu_jacobian(self):
        a, C = _spd_state(6, 1)
        jac, m, strata = ja.build_jacobian(a, C)
        self.assertIsInstance(jac, LocalReluJacobian)          # __post_init__ validated
        self.assertTrue(np.array_equal(jac.price_kernel, jac.price_kernel.T))
        for arr in (jac.probability, jac.mean_variance_derivative,
                    jac.price_kernel, jac.h_mu, jac.h_variance):
            self.assertTrue(np.all(np.isfinite(arr)))
        self.assertEqual(strata["spd"], 6 * 5 // 2)

    def test_diagonal_entries_match_direct_references(self):
        a, C = _spd_state(6, 2)
        jac, m, _ = ja.build_jacobian(a, C)
        sigma = np.sqrt(np.diag(C))
        for i in range(6):
            A, S = mp.mpf(a[i]), mp.mpf(sigma[i])
            alpha = A / S
            p_ref = mp.ncdf(alpha)
            r_ref = mp.npdf(alpha) / (2 * S)
            m_ref = A * mp.ncdf(alpha) + S * mp.npdf(alpha)
            self.assertLess(abs(mp.mpf(jac.probability[i]) - p_ref), 1e-12, i)
            self.assertLess(abs(mp.mpf(jac.mean_variance_derivative[i]) - r_ref), 1e-12, i)
            self.assertLess(abs(mp.mpf(jac.price_kernel[i, i]) - p_ref), 1e-12, i)
            self.assertLess(abs(mp.mpf(jac.h_mu[i, i]) - 2 * m_ref * (1 - p_ref)), 1e-11, i)
            self.assertLess(abs(mp.mpf(jac.h_variance[i, i]) - (p_ref - 2 * m_ref * r_ref)), 1e-11, i)

    def test_offdiagonal_K_matches_orthant_probability(self):
        # K_ij = P(X_i>0, X_j>0), checked by 1D-reduced dps-30 integration.
        a, C = _spd_state(5, 3)
        jac, _, _ = ja.build_jacobian(a, C)
        sigma = np.sqrt(np.diag(C))
        for i in range(5):
            for j in range(i + 1, 5):
                A_i, A_j = mp.mpf(a[i]), mp.mpf(a[j])
                S_i, S_j = mp.mpf(sigma[i]), mp.mpf(sigma[j])
                rho = mp.mpf(C[i, j]) / (S_i * S_j)
                s = mp.sqrt((1 - rho) * (1 + rho))
                cond_sd = S_j * s

                def prob(x):
                    dens = mp.npdf((x - A_i) / S_i) / S_i
                    cm = A_j + rho * (S_j / S_i) * (x - A_i)
                    return dens * mp.ncdf(cm / cond_sd)

                K_ref = mp.quad(prob, [max(mp.mpf(0), A_i - 12 * S_i), A_i + 12 * S_i])
                self.assertLess(abs(mp.mpf(jac.price_kernel[i, j]) - K_ref), 1e-7, (i, j))

    def test_zero_variance_marginal_limit(self):
        # sigma_i == 0 => X_i = a_i a.s.; K_ij = 1{a_i>0} p_j, Hmu=Hv=0 cross.
        a = np.array([2.0, 0.5, -1.0])
        C = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.3], [0.0, 0.3, 1.0]])
        jac, m, strata = ja.build_jacobian(a, C)
        self.assertGreater(strata["zero_var"], 0)
        p1 = jac.probability[1]
        self.assertAlmostEqual(jac.price_kernel[0, 1], 1.0 * p1, places=12)  # a_0>0 -> 1
        self.assertEqual(jac.h_mu[0, 1], 0.0)
        self.assertEqual(jac.h_mu[1, 0], 0.0)
        self.assertEqual(jac.h_variance[0, 1], 0.0)

    def test_non_psd_fails_closed(self):
        a = np.zeros(2)
        C = np.array([[1.0, 0.0], [0.0, -1.0]])   # negative variance
        with self.assertRaises(ValueError):
            ja.build_jacobian(a, C)

    def test_rank_one_face_fails_closed(self):
        a = np.array([0.3, -0.2])
        s = 1.0
        rho = 1.0 - 2.0 ** -60                     # beyond RHO_MAX
        C = np.array([[s, rho * s], [rho * s, s]])
        with self.assertRaises(ValueError):
            ja.build_jacobian(a, C)

    def test_archive_runs_and_is_abi_consumable(self):
        # end-to-end: the archive entries drive the m125 carrier without raising
        weights = _gen_weights(n=6, depth=3, seed=20260807)
        entries = ja.build_archive(weights)
        self.assertEqual(len(entries), 3)
        state = TangentState(np.zeros(6), np.eye(6) * 1e-6)
        for e in entries:
            self.assertTrue(np.array_equal(e.V, e.V.T))
            self.assertEqual(e.jacobian.probability.shape, (6,))
            # the carrier consumes the bundle (proves ABI compatibility)
            state = relu_tangent(state, e.jacobian)
            self.assertTrue(np.all(np.isfinite(state.mean)))

    def test_archive_matches_g2_recurrence_state(self):
        # the archived (mu, V) must equal the standalone G2 producer states
        weights = _gen_weights(n=5, depth=4, seed=7)
        entries = ja.build_archive(weights)
        states = prod.zero_order_recurrence(weights)
        for e, st in zip(entries, states):
            self.assertTrue(np.array_equal(e.mu, st.mu))
            self.assertTrue(np.array_equal(e.V, st.V))


if __name__ == "__main__":
    unittest.main()
