"""Exact tests for the M201 repeated-label rank witness."""

from __future__ import annotations

import unittest

from m201_repeated_label_rank_no_go import (
    EXPECTED_DECODER,
    WITNESS_WEIGHT,
    determinant3,
    exact_result,
    repeated_label_decoder,
)


class M201RepeatedLabelRankTests(unittest.TestCase):
    def test_weight_is_full_rank(self):
        self.assertEqual(determinant3(WITNESS_WEIGHT), 5)

    def test_decoder_matches_exact_m151_feature_expansion(self):
        self.assertEqual(repeated_label_decoder(), EXPECTED_DECODER)

    def test_repeated_label_channel_has_full_rank(self):
        self.assertEqual(determinant3(repeated_label_decoder()), 116_640)

    def test_result_scope_is_fail_closed(self):
        result = exact_result()
        self.assertEqual(
            result["status"],
            "KILLED_EXACT_COMMUTE_THEN_COLLAPSE_REPEATED_LABEL_AXIS",
        )
        self.assertNotIn("score", result)
        self.assertNotIn("MSE", result)
        self.assertEqual(result["decoder_determinant"], 116_640)


if __name__ == "__main__":
    unittest.main()
