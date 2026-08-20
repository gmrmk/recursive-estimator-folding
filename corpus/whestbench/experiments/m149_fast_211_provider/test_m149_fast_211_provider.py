"""Response-free tests for M149's bounded local provider."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m147_endpoint_safe_bridge", ROOT / "m129_source_frechet_tangent"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m147_endpoint_safe_bridge import (  # noqa: E402
    EndpointCertificationFailure,
    build_endpoint_state_frechet,
    conditional_collision211_endpoint_dot,
)
from m149_fast_211_provider import (  # noqa: E402
    Fast211CertificationFailure,
    fallback_contract_for_zero_schur,
    fast_collision211_local_state_dot,
)


def state(rho_jk: float = 0.25):
    mean = np.array([0.2, -0.1, 0.35])
    # Keep the adversarial singleton correlation PSD for every tested rho.
    correlation = np.array([[1.0, 0.10, -0.05], [0.10, 1.0, rho_jk], [-0.05, rho_jk, 1.0]])
    sigma = np.array([1.1, 0.8, 1.3])
    covariance = correlation * np.outer(sigma, sigma)
    mean_dot = np.array([0.03, -0.02, 0.01])
    covariance_dot = np.array([[0.02, 0.003, -0.002], [0.003, -0.01, 0.004], [-0.002, 0.004, 0.015]])
    return mean, covariance, mean_dot, covariance_dot


class M149FastProviderTests(unittest.TestCase):
    def assert_close(self, a: float, b: float, tol: float):
        self.assertLessEqual(abs(a-b), tol * (1.0 + abs(b)))

    def oracle(self, args):
        return conditional_collision211_endpoint_dot(build_endpoint_state_frechet(*args), 0, 1, 2)

    def _must_reject_against_oracle(self, args):
        """The test records the failed mechanism, not a weakened acceptance."""
        with self.assertRaises(Fast211CertificationFailure):
            fast_collision211_local_state_dot(*args)
        exploratory = fast_collision211_local_state_dot(
            *args, value_tolerance=1.0, tangent_tolerance=1.0,
            max_angular_evaluations=100_000,
        )
        expected = self.oracle(args)
        value_defect = abs(exploratory.cumulant - expected.cumulant)
        tangent_defect = abs(exploratory.cumulant_tangent - expected.cumulant_tangent)
        self.assertTrue(value_defect > 2e-8 or tangent_defect > 2e-7)
        return exploratory, expected, value_defect, tangent_defect

    def test_moderate_falsifies_43_87_against_m147_oracle(self):
        args = state()
        observed, _expected, value_defect, tangent_defect = self._must_reject_against_oracle(args)
        self.assertGreater(value_defect, 2e-8)
        self.assertGreater(tangent_defect, 2e-7)
        self.assertLessEqual(observed.angular_evaluations, 8000)
        self.assertLessEqual(observed.conservative_billed_ops, 102400)
        self.assertEqual(observed.outer_nodes, 87)

    def test_high_correlation_falsifies_43_87_against_m147_oracle(self):
        args = state(0.93)
        observed, _expected, value_defect, tangent_defect = self._must_reject_against_oracle(args)
        self.assertGreater(value_defect, 2e-8)
        self.assertGreater(tangent_defect, 2e-7)
        self.assertLessEqual(observed.angular_evaluations, 8000)

    def test_near_conditional_endpoint_fails_resource_or_accuracy_gate(self):
        covariance = np.array([[1., .5, .5], [.5, 1., .99925], [.5, .99925, 1.]])
        mean = np.array([.1, -.2, .3]); mean_dot = np.array([.01, -.02, .015])
        covariance_dot = np.array([[.01,.002,-.001],[.002,-.005,.001],[-.001,.001,.008]])
        with self.assertRaises(Fast211CertificationFailure):
            fast_collision211_local_state_dot(mean, covariance, mean_dot, covariance_dot)

    def test_finite_difference_and_gauge_permutation(self):
        args = state(.65)
        with self.assertRaises(Fast211CertificationFailure):
            fast_collision211_local_state_dot(*args)
        observed = fast_collision211_local_state_dot(*args, value_tolerance=1., tangent_tolerance=1., max_angular_evaluations=100_000)
        eps = 2e-6
        exploratory_kwargs = dict(value_tolerance=1., tangent_tolerance=1., max_angular_evaluations=100_000)
        plus = fast_collision211_local_state_dot(args[0]+eps*args[2], args[1]+eps*args[3], np.zeros(3), np.zeros((3,3)), **exploratory_kwargs)
        minus = fast_collision211_local_state_dot(args[0]-eps*args[2], args[1]-eps*args[3], np.zeros(3), np.zeros((3,3)), **exploratory_kwargs)
        self.assert_close(observed.cumulant_tangent, (plus.cumulant-minus.cumulant)/(2*eps), 1e-4)
        permutation = np.array([0,2,1])
        permuted = fast_collision211_local_state_dot(args[0][permutation], args[1][np.ix_(permutation,permutation)], args[2][permutation], args[3][np.ix_(permutation,permutation)], **exploratory_kwargs)
        self.assert_close(permuted.cumulant, observed.cumulant, 2e-10)
        self.assert_close(permuted.cumulant_tangent, observed.cumulant_tangent, 3e-9)
        gauge = np.diag([1.7,.8,1.3])
        gauged_covariance = gauge @ args[1] @ gauge
        gauged_covariance = 0.5 * (gauged_covariance + gauged_covariance.T)
        gauged_covariance_dot = gauge @ args[3] @ gauge
        gauged_covariance_dot = 0.5 * (gauged_covariance_dot + gauged_covariance_dot.T)
        gauged = fast_collision211_local_state_dot(gauge@args[0], gauged_covariance, gauge@args[2], gauged_covariance_dot, **exploratory_kwargs)
        scale = gauge[0,0]**2*gauge[1,1]*gauge[2,2]
        self.assert_close(gauged.cumulant, scale*observed.cumulant, 2e-7)

    def test_zero_schur_contract_and_no_ridge(self):
        covariance = np.ones((3,3)); mean = np.array([.1,.2,.3])
        fallback = fallback_contract_for_zero_schur(mean,covariance)
        self.assertIsNotNone(fallback); self.assertGreater(fallback.conservative_billed_ops(2), 0)
        with self.assertRaisesRegex(Fast211CertificationFailure, "zero-Schur-singleton"):
            fast_collision211_local_state_dot(mean,covariance,np.zeros(3),np.zeros((3,3)))

    def test_nonfinite_and_cap_fail_closed(self):
        args = state()
        with self.assertRaises(Fast211CertificationFailure):
            fast_collision211_local_state_dot(np.array([math.inf,0.,0.]), *args[1:])
        with self.assertRaisesRegex(Fast211CertificationFailure, "cap"):
            fast_collision211_local_state_dot(*args, max_angular_evaluations=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
