"""Response-free exact/cost tests for M203."""

from __future__ import annotations

import unittest

import numpy as np

from m203_terminal_contraction_circuit_no_go import (
    CONDITIONAL_REPLACEMENT_HEADROOM,
    M151_SLOT,
    STRICT_COMPOSED_HEADROOM,
    cost_table,
    expanded_terminal_contractions,
    packed_terminal_contractions,
)


class M203TerminalCircuitTests(unittest.TestCase):
    def test_two_rectangle_identity_matches_five_channel_expansion(self):
        rng = np.random.Generator(np.random.Philox(203001))
        for width in (3, 4, 8):
            weight = rng.integers(-3, 4, size=(width, width), dtype=np.int64)
            orientation = rng.integers(-2, 3, size=(width, width), dtype=np.int64)
            packed = packed_terminal_contractions(weight, orientation)
            expanded = expanded_terminal_contractions(weight, orientation)
            for left, right in zip(packed, expanded):
                np.testing.assert_array_equal(left, right)

    def test_recorded_cost_table_is_reproduced_exactly(self):
        observed = [
            (row["depth"], row["terminal"], row["combined"], row["m151_overage"])
            for row in cost_table()
        ]
        self.assertEqual(
            observed,
            [
                (3, 9_069_419_520, 11_649_611_520, 1_358_247_760),
                (4, 8_320_856_320, 10_901_048_320, 609_684_560),
                (5, 7_963_587_520, 10_543_779_520, 252_415_760),
                (6, 8_171_994_320, 10_752_186_320, 460_822_560),
            ],
        )

    def test_best_standard_fusion_misses_every_current_headroom(self):
        best = min(row["combined"] for row in cost_table())
        self.assertGreater(best, M151_SLOT)
        self.assertGreater(best, STRICT_COMPOSED_HEADROOM)
        self.assertGreater(best, CONDITIONAL_REPLACEMENT_HEADROOM)

    def test_generic_channel_minors_are_nonsingular(self):
        self.assertEqual(round(np.linalg.det(np.diag([2, 1, 1]))), 2)
        self.assertEqual(round(np.linalg.det(np.diag([1, 2]))), 2)


if __name__ == "__main__":
    unittest.main()
