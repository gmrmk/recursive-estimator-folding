"""Response-free tests for M170's M166 tensor-rank obstruction."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m170_oriented_tensor_rank import (  # noqa: E402
    TARGET_COMPILER_CAP,
    admissible_specialization_certificate,
    coefficient_table,
    compile_seven_products,
    exhaustive_source,
    generated_parity_sweep,
    generated_weight,
    orient_covariance_edges,
    positive_covariance,
    source_max_abs_difference,
    static_cost_ledger,
    static_results,
    symbolic_tensor_rank_ledger,
)


class TestM170OrientedTensorRank(unittest.TestCase):
    def test_exhaustive_generated_width_2_through_7_matches_seven_product_compiler(self) -> None:
        sweep = generated_parity_sweep()
        self.assertEqual(set(sweep), set(range(2, 8)))
        self.assertLess(max(sweep.values()), 2e-10)

    def test_collision_null_is_lawful_including_the_forced_width_two_tie(self) -> None:
        for width in range(2, 8):
            covariance = positive_covariance(170_100 + width, width)
            a, b, _ = orient_covariance_edges(covariance)
            table = coefficient_table(a, b)
            for i in range(width):
                for j in range(width):
                    self.assertEqual(table[i][i][j], 0.0)
                    self.assertEqual(table[i][j][i], 0.0)
                    self.assertEqual(table[i][j][j], 0.0)
            if width == 2:
                self.assertTrue(all(a[i][j] == 0.0 for i in range(width) for j in range(width)))

    def test_independent_direct_orbit_sum_matches_the_compiler_on_every_width(self) -> None:
        for width in range(2, 8):
            covariance = positive_covariance(170_500 + width, width)
            a, b, _ = orient_covariance_edges(covariance)
            weight = generated_weight(170_600 + width, width, width + 3)
            self.assertLess(
                source_max_abs_difference(
                    exhaustive_source(weight, coefficient_table(a, b)),
                    compile_seven_products(weight, a),
                ),
                3e-10,
            )

    def test_admissible_tied_score_specialization_has_all_required_nonzero_minors(self) -> None:
        certificate = admissible_specialization_certificate()
        self.assertTrue(certificate["strict_diagonal_dominance"])
        self.assertEqual(certificate["score_tiers"], [2025, 2025, 900, 900, 225, 225])
        self.assertEqual(certificate["projection_minor_numerator"], -114)
        self.assertEqual(certificate["left_31_minor_numerator"], -1_297_824)
        self.assertEqual(certificate["right_31_minor_numerator"], 686)
        self.assertEqual(certificate["left_22_minor_numerator"], 1_505_876)
        self.assertEqual(certificate["projection_rank"], 2)
        self.assertEqual(certificate["left_31_rank"], 3)
        self.assertEqual(certificate["right_31_rank"], 3)
        self.assertEqual(certificate["left_22_rank"], 4)

    def test_symbolic_flattening_requires_two_plus_three_plus_two_families(self) -> None:
        ledger = symbolic_tensor_rank_ledger()
        self.assertEqual(ledger["projection_rank"], 2)
        self.assertEqual(ledger["aaab_ordered_rank"], 3)
        self.assertEqual(ledger["aabb_symmetric_pair_rank"], 2)
        self.assertEqual(ledger["terminal_product_lower_bound"], 5)
        self.assertEqual(ledger["dense_product_lower_bound"], 7)

    def test_six_f64_families_alone_exceed_the_compiler_slot(self) -> None:
        cost = static_cost_ledger()
        self.assertGreater(cost["six_f64_dense_product_bill"], TARGET_COMPILER_CAP)
        self.assertLess(cost["six_product_margin_before_any_pointwise_or_copy"], 0)
        self.assertGreater(cost["seven_f64_total_including_pointwise_copy"], TARGET_COMPILER_CAP)
        self.assertEqual(cost["pointwise_copy_f64_allowance"], 325_058_560)

    def test_triangular_projection_observation_is_recorded_without_rank_or_cost_credit(self) -> None:
        salvage = static_results()["nonmerged_salvage"]
        self.assertEqual(salvage["status"], "UNTESTED_SEPARATE_STRUCTURED_KERNEL_DESCENDANT")
        self.assertIn("does not reduce", salvage["not_a_rank_claim"])
        self.assertIn("factorial", salvage["composition_rule"])


if __name__ == "__main__":
    unittest.main()
