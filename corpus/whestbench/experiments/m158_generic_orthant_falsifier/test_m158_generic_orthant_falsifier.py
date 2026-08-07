"""Response-free literal-domain falsifier for M158's absolute-error request."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m154_analytic_endpoint_partition", ROOT / "m147_endpoint_safe_bridge", ROOT / "m129_source_frechet_tangent"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m154_analytic_endpoint_partition import analytic_rank1_collision211_local_state_dot  # noqa: E402
from m158_generic_orthant_falsifier import (  # noqa: E402
    M158LiteralDomainFailure,
    common_factor_defect_exact,
    literal_float64_absolute_error_counterexample,
    m158_per_coefficient_allowance,
    require_literal_m158_contract,
)


class GenericOrthantLiteralDomainTests(unittest.TestCase):
    def test_exact_common_factor_formula_matches_the_retained_m154_rank_one_identity(self) -> None:
        observed = analytic_rank1_collision211_local_state_dot(
            np.zeros(3), np.ones((3, 3)), np.zeros(3), np.zeros((3, 3))
        )
        expected = float(common_factor_defect_exact(1))
        self.assertLess(abs(observed.defect - expected), 2e-14)

    def test_positive_gauge_rank_one_psd_state_has_no_float64_value_inside_2e_minus_8(self) -> None:
        counterexample = literal_float64_absolute_error_counterexample(
            gauge=1024,
            value_tolerance="2e-8",
        )
        self.assertTrue(counterexample.covariance_is_psd)
        self.assertTrue(counterexample.positive_marginal_variances)
        self.assertGreater(counterexample.nearest_float64_error, counterexample.value_tolerance)
        self.assertGreater(counterexample.float64_ulp, counterexample.value_tolerance)
        self.assertEqual(counterexample.coefficient_kind, "C_211 defect = cumulant - tree")
        with self.assertRaisesRegex(M158LiteralDomainFailure, "unrepresentable"):
            require_literal_m158_contract(value_tolerance="2e-8")

    def test_counterexample_is_not_a_zero_variance_or_non_psd_loophole(self) -> None:
        gauge = 1024.0
        covariance = gauge * gauge * np.ones((3, 3))
        self.assertGreater(float(np.min(np.diag(covariance))), 0.0)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(covariance))), -1e-8)
        self.assertEqual(np.linalg.matrix_rank(covariance), 1)

    def test_residual_allowance_is_exactly_606720_per_coefficient_but_cannot_repair_the_abi_failure(self) -> None:
        allowance = m158_per_coefficient_allowance()
        self.assertEqual(allowance["residual_allowance_ops"], 2_407_464_960)
        self.assertEqual(allowance["coefficient_calls"], 3968)
        self.assertEqual(allowance["ops_per_coefficient"], 606_720)
        self.assertTrue(allowance["integer_division_exact"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
