"""Response-free tests for M165's centered rank-face subtraction prototype."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import mpmath as mp
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m154_analytic_endpoint_partition", ROOT / "m147_endpoint_safe_bridge"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m147_endpoint_safe_bridge import build_endpoint_state_frechet, conditional_collision211_endpoint_dot  # noqa: E402
from m154_analytic_endpoint_partition import analytic_rank1_collision211_local_state_dot  # noqa: E402
from m165_rank_face_subtraction import (  # noqa: E402
    M165PrototypeDomainError,
    centered_equicorrelation_defect_mp,
    common_factor_rank_one_defect_mp,
    dispatch_m165_prototype_stratum,
    rank_face_subtracted_residual_mp,
)


M154_EQUICORRELATED_OPENING_DERIVATIVE = mp.mpf("3.983346315428913")


class M165RankFaceSubtractionTests(unittest.TestCase):
    def test_common_factor_limit_matches_the_retained_m154_rank_one_provider(self) -> None:
        observed = analytic_rank1_collision211_local_state_dot(
            np.zeros(3), np.ones((3, 3)), np.zeros(3), np.eye(3) - np.ones((3, 3))
        )
        self.assertLess(
            abs(common_factor_rank_one_defect_mp() - mp.mpf(str(observed.defect))),
            mp.mpf("3e-14"),
        )

    def test_centered_high_precision_interior_probe_matches_independent_m147_reference(self) -> None:
        epsilon = mp.mpf("1e-3")
        high_precision = centered_equicorrelation_defect_mp(epsilon, dps=60)
        covariance = float(epsilon) * np.eye(3) + (1.0 - float(epsilon)) * np.ones((3, 3))
        reference = conditional_collision211_endpoint_dot(
            build_endpoint_state_frechet(
                np.zeros(3), covariance, np.zeros(3), np.zeros((3, 3)),
                allow_psd_directional=True,
            ),
            0,
            1,
            2,
        )
        self.assertLess(abs(high_precision - mp.mpf(str(reference.defect))), mp.mpf("4e-9"))

    def test_rank_one_and_linear_m154_terms_leave_a_nonzero_epsilon_to_three_halves_remainder(self) -> None:
        epsilon = mp.mpf("1e-6")
        residual = rank_face_subtracted_residual_mp(
            epsilon, M154_EQUICORRELATED_OPENING_DERIVATIVE, dps=70
        )
        coefficient = residual / epsilon ** mp.mpf("1.5")
        self.assertGreater(coefficient, mp.mpf("-1.49"))
        self.assertLess(coefficient, mp.mpf("-1.46"))

    def test_prototype_refuses_to_claim_a_rank_two_or_zero_face_anchor(self) -> None:
        with self.assertRaisesRegex(M165PrototypeDomainError, "rank-one common-factor"):
            centered_equicorrelation_defect_mp(mp.mpf("0"), dps=50)
        with self.assertRaisesRegex(M165PrototypeDomainError, "strictly between"):
            centered_equicorrelation_defect_mp(mp.mpf("1"), dps=50)
        self.assertEqual(
            dispatch_m165_prototype_stratum(
                rank=1, positive_marginals=True, centered_common_factor=True
            ),
            "rank1-common-factor-subtraction",
        )
        with self.assertRaisesRegex(M165PrototypeDomainError, "rank-two anchor"):
            dispatch_m165_prototype_stratum(
                rank=2, positive_marginals=True, centered_common_factor=False
            )
        with self.assertRaisesRegex(M165PrototypeDomainError, "zero-marginal"):
            dispatch_m165_prototype_stratum(
                rank=1, positive_marginals=False, centered_common_factor=True
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
