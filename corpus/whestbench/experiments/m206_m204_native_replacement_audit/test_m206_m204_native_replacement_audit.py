"""Response-free falsifiers for the claimed M204-to-M151 call replacement."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for directory in (
    HERE,
    EXPERIMENTS / "m151_b1_forward_control",
    EXPERIMENTS / "m156_extended_domain_star_control",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from m151_b1_forward_control import (  # noqa: E402
    B1CanonicalState,
    forward_b1_control_source,
)
from m156_extended_domain_star_control import (  # noqa: E402
    compiled_extended_star_control,
)
from m206_m204_native_replacement_audit import (  # noqa: E402
    b_equal_d_different_witness,
    compile_complete_rank_one_lift,
    rank_one_control_table,
    raw_and_protected_cost_ledger,
    source_max_abs_difference,
)


def _m151_rademacher_state(factor: np.ndarray) -> B1CanonicalState:
    """Embed one rank-one Rademacher pair in M151's 49-node ABI."""

    width = factor.size
    omega = np.zeros(49, dtype=np.float64)
    omega[:2] = 0.5
    mean = np.zeros((49, width), dtype=np.float64)
    mean[0] = factor
    mean[1] = -factor
    variance = np.zeros_like(mean)
    return B1CanonicalState(omega, mean, variance)


class M206NativeReplacementAuditTests(unittest.TestCase):
    def test_lift_matches_m156_complete_domain_not_m151_strict_domain(self):
        """The exact equality is with M156's lift; M151 diverges on collisions."""

        rng = np.random.Generator(np.random.Philox(206_151_156))
        weight = rng.normal(size=(5, 4))
        factor = np.array([1.0, -1.0, 1.0, 1.0, -1.0], dtype=np.float64)

        table_all = rank_one_control_table(factor, distinct_only=False)
        table_strict = rank_one_control_table(factor, distinct_only=True)
        distinct_mask = np.fromfunction(
            lambda i, j, k: (i != j) & (i != k) & (j != k), table_all.shape, dtype=int
        )
        self.assertTrue(np.all(table_strict[~distinct_mask] == 0.0))
        np.testing.assert_allclose(table_all[distinct_mask], table_strict[distinct_mask])
        self.assertGreater(float(np.max(np.abs(table_all[~distinct_mask]))), 0.0)

        full_lift = compile_complete_rank_one_lift(weight, factor)
        m156_full = compiled_extended_star_control(weight, np.outer(factor, factor))
        self.assertLess(source_max_abs_difference(full_lift, m156_full), 2e-10)

        m151_strict = forward_b1_control_source(weight, _m151_rademacher_state(factor))
        # The source slots carry the collision difference.  This is the first
        # mismatch; it is not a numerical tolerance or a dtype conversion.
        self.assertGreater(source_max_abs_difference(full_lift, m151_strict), 1e-6)

    def test_B_equal_D_different_witness(self):
        """One Gram does not determine the collision statistic D."""

        b_identity, b_rotation, d_identity, d_rotation = b_equal_d_different_witness()
        np.testing.assert_allclose(b_identity, b_rotation, rtol=0.0, atol=3e-16)
        np.testing.assert_allclose(d_identity, np.eye(2), rtol=0.0, atol=3e-16)
        np.testing.assert_allclose(
            d_rotation,
            0.5 * np.ones((2, 2), dtype=np.float64),
            rtol=0.0,
            atol=3e-16,
        )
        self.assertGreater(float(np.max(np.abs(d_identity - d_rotation))), 0.0)

    def test_raw_and_protected_static_costs_fail_without_a_replacement_trace(self):
        """Even the raw B+a minimum exhausts the strict composed headroom."""

        ledger = raw_and_protected_cost_ledger()
        self.assertEqual(ledger["strict_headroom"], 1_986_871_472)
        self.assertEqual(ledger["rankone_B_raw_31_layers"], 2_076_311_552)
        self.assertEqual(ledger["rankone_a_raw_31_layers"], 8_110_592)
        self.assertEqual(ledger["rankone_raw_minimum"], 2_084_422_144)
        self.assertEqual(ledger["rankone_raw_excess_over_headroom"], 97_550_672)
        self.assertEqual(ledger["rankone_B_protected_31_layers"], 2_595_389_440)
        self.assertEqual(ledger["rankone_protected_minimum"], 2_605_527_680)
        self.assertEqual(ledger["rankone_protected_excess_over_headroom"], 618_656_208)
        self.assertEqual(ledger["terminal_background_matmul_floor"], 134_217_216)
        self.assertEqual(ledger["rankone_plus_terminal_raw_excess"], 231_767_888)
        self.assertTrue(ledger["one_B_is_additive_without_proved_replacement"])
        self.assertFalse(ledger["native_replacement_proved"])


if __name__ == "__main__":
    unittest.main()
