"""Response-free checks for the M168 transverse rank-two reference."""

from __future__ import annotations

from itertools import permutations
from pathlib import Path
import sys
import unittest

import mpmath as mp
import numpy as np

mp.mp.dps = 70


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (HERE, ROOT / "m147_endpoint_safe_bridge"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m147_endpoint_safe_bridge import (  # noqa: E402
    build_endpoint_state_frechet,
    conditional_collision211_endpoint_dot,
)
from m168_rank2_anchor import (  # noqa: E402
    Rank2AnchorDomainError,
    rank2_anchor_cost_envelope,
    rank2_transverse_anchor_dot,
)


def _state():
    """A fixed generated rank-two state with all three pair minors positive."""

    mean = (mp.mpf("0.3"), mp.mpf("-0.45"), mp.mpf("0.65"))
    factor = (
        (mp.mpf("1.2"), mp.mpf("0.4")),
        (mp.mpf("-0.35"), mp.mpf("1.1")),
        (mp.mpf("0.8"), mp.mpf("-0.9")),
    )
    mean_dot = (mp.mpf("0.07"), mp.mpf("-0.03"), mp.mpf("0.05"))
    factor_dot = (
        (mp.mpf("0.11"), mp.mpf("-0.04")),
        (mp.mpf("0.02"), mp.mpf("0.06")),
        (mp.mpf("-0.05"), mp.mpf("0.08")),
    )
    covariance_dot = tuple(
        tuple(
            mp.fsum(
                factor_dot[left][axis] * factor[right][axis]
                + factor[left][axis] * factor_dot[right][axis]
                for axis in range(2)
            )
            for right in range(3)
        )
        for left in range(3)
    )
    return mean, factor, mean_dot, factor_dot, covariance_dot


def _null_opening(factor):
    column0, column1 = tuple(row[0] for row in factor), tuple(row[1] for row in factor)
    normal = (
        column0[1] * column1[2] - column0[2] * column1[1],
        column0[2] * column1[0] - column0[0] * column1[2],
        column0[0] * column1[1] - column0[1] * column1[0],
    )
    length = mp.sqrt(mp.fsum(value * value for value in normal))
    normal = tuple(value / length for value in normal)
    return tuple(tuple(left * right for right in normal) for left in normal)


def _zeros():
    return ((mp.mpf(0),) * 3,) * 3


class M168Rank2AnchorTests(unittest.TestCase):
    def test_rank_two_price_tangent_matches_a_rank_preserving_high_precision_difference(self) -> None:
        mean, factor, mean_dot, factor_dot, covariance_dot = _state()
        certificate = rank2_transverse_anchor_dot(
            mean, factor, mean_dot, covariance_dot, dps=45
        )
        step = mp.mpf("1e-4")
        plus = rank2_transverse_anchor_dot(
            tuple(mean[index] + step * mean_dot[index] for index in range(3)),
            tuple(
                tuple(factor[row][column] + step * factor_dot[row][column] for column in range(2))
                for row in range(3)
            ),
            (mp.mpf(0),) * 3,
            _zeros(),
            dps=45,
        ).defect
        minus = rank2_transverse_anchor_dot(
            tuple(mean[index] - step * mean_dot[index] for index in range(3)),
            tuple(
                tuple(factor[row][column] - step * factor_dot[row][column] for column in range(2))
                for row in range(3)
            ),
            (mp.mpf(0),) * 3,
            _zeros(),
            dps=45,
        ).defect
        self.assertLess(abs(certificate.tangent - (plus - minus) / (2 * step)), mp.mpf("1e-9"))

    def test_one_sided_rank_three_opening_matches_the_independent_m147_reference(self) -> None:
        mean, factor, _, _, _ = _state()
        opening = _null_opening(factor)
        certificate = rank2_transverse_anchor_dot(
            mean, factor, (mp.mpf(0),) * 3, opening, dps=45
        )
        covariance = np.asarray(
            [[float(mp.fsum(factor[left][axis] * factor[right][axis] for axis in range(2))) for right in range(3)] for left in range(3)],
            dtype=np.float64,
        )
        step = 2.0e-5
        interior = conditional_collision211_endpoint_dot(
            build_endpoint_state_frechet(
                np.asarray(mean, dtype=np.float64),
                covariance + step * np.asarray(opening, dtype=np.float64),
                np.zeros(3),
                np.zeros((3, 3)),
                allow_psd_directional=True,
            ),
            0,
            1,
            2,
        )
        finite_difference = (mp.mpf(str(interior.defect)) - certificate.defect) / step
        self.assertEqual(certificate.cone_mode, "one-sided-rank-three-opening")
        self.assertLess(abs(certificate.tangent - finite_difference), mp.mpf("5e-6"))

    def test_permutation_and_positive_gauge_covariance_on_the_generated_state(self) -> None:
        mean, factor, mean_dot, _, covariance_dot = _state()
        base = rank2_transverse_anchor_dot(mean, factor, mean_dot, covariance_dot, dps=40)
        for ordering in permutations(range(3)):
            inverse = [0, 0, 0]
            for new, old in enumerate(ordering):
                inverse[old] = new
            labels = tuple(inverse[index] for index in (0, 0, 1, 2))
            observed = rank2_transverse_anchor_dot(
                tuple(mean[old] for old in ordering),
                tuple(factor[old] for old in ordering),
                tuple(mean_dot[old] for old in ordering),
                tuple(tuple(covariance_dot[left][right] for right in ordering) for left in ordering),
                labels=labels,
                dps=40,
            )
            self.assertLess(abs(observed.defect - base.defect), mp.mpf("1e-24"))
            self.assertLess(abs(observed.tangent - base.tangent), mp.mpf("1e-24"))

        gauge = (mp.mpf(2), mp.mpf("0.5"), mp.mpf("1.75"))
        weight = gauge[0] ** 2 * gauge[1] * gauge[2]
        observed = rank2_transverse_anchor_dot(
            tuple(gauge[index] * mean[index] for index in range(3)),
            tuple(tuple(gauge[row] * factor[row][column] for column in range(2)) for row in range(3)),
            tuple(gauge[index] * mean_dot[index] for index in range(3)),
            tuple(
                tuple(gauge[left] * gauge[right] * covariance_dot[left][right] for right in range(3))
                for left in range(3)
            ),
            dps=40,
        )
        self.assertLess(abs(observed.defect - weight * base.defect), mp.mpf("1e-23"))
        self.assertLess(abs(observed.tangent - weight * base.tangent), mp.mpf("1e-23"))

    def test_nontransverse_zero_and_outward_faces_refuse_and_cost_has_no_credit(self) -> None:
        mean, factor, _, _, _ = _state()
        with self.assertRaisesRegex(Rank2AnchorDomainError, "nontransverse"):
            rank2_transverse_anchor_dot(
                mean,
                ((1, 0), (2, 0), (0, 1)),
                (0, 0, 0),
                _zeros(),
                dps=40,
            )
        with self.assertRaisesRegex(Rank2AnchorDomainError, "zero marginal"):
            rank2_transverse_anchor_dot(
                mean,
                ((1, 0), (0, 0), (0, 1)),
                (0, 0, 0),
                _zeros(),
                dps=40,
            )
        opening = _null_opening(factor)
        with self.assertRaisesRegex(Rank2AnchorDomainError, "outside the PSD tangent cone"):
            rank2_transverse_anchor_dot(
                mean,
                factor,
                (0, 0, 0),
                tuple(tuple(-entry for entry in row) for row in opening),
                dps=40,
            )
        ten = rank2_anchor_cost_envelope(angular_nodes=10)
        eleven = rank2_anchor_cost_envelope(angular_nodes=11)
        self.assertTrue(ten["fits_bookkeeping_ceiling"])
        self.assertFalse(eleven["fits_bookkeeping_ceiling"])
        self.assertFalse(ten["native_bill_proved"])
        self.assertFalse(ten["uniform_error_certificate_proved"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
