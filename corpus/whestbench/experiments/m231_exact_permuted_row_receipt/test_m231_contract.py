"""Generated-only RED/GREEN contracts for frozen M231 exact receipts."""

from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m205_rankone_complete_physical_owner",
    BASE / "m209_batched_recursive_gram_control",
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m215_rankone_collision_correction",
    BASE / "m227_row_subset_collision_ht",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import flopscope as flops  # noqa: E402
import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
import m215_rankone_collision_correction as m215  # noqa: E402
import m227_row_subset_collision_ht as m227  # noqa: E402
import m231_flopscope_sidecar as m231  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402


def _records(layers: int, width: int, seed: int = 231401):
    rng = np.random.Generator(np.random.Philox(seed))
    return [
        LayerInput(
            layer=layer + 1,
            weight=rng.normal(scale=0.2, size=(width, width)),
            factor=rng.normal(scale=0.15, size=width),
            producer_epoch=231,
        )
        for layer in range(layers)
    ]


class M231ReceiptAndNativeTests(unittest.TestCase):
    def test_primitive_emits_one_unique_permutation_per_layer_without_tie_path(self):
        budget = flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=30.0)
        with budget:
            receipt = m231.issue_permuted_receipt(
                layers=31,
                width=256,
                subset_rows=32,
                seed=227700001,
                producer_epoch=231,
                domain=m231.DOMAIN,
            )
        rank = np.asarray(receipt.rank_order)
        selected = np.asarray(receipt.selected)
        self.assertEqual(rank.shape, (31, 256))
        self.assertEqual(selected.shape, (31, 32))
        self.assertTrue(
            all(np.array_equal(np.sort(row), np.arange(256)) for row in rank)
        )
        self.assertTrue(all(np.unique(row).size == 32 for row in selected))
        operations = budget.summary_dict()["operations"]
        self.assertEqual(int(budget.flops_used), 32_768)
        self.assertEqual(operations["arange"]["calls"], 1)
        self.assertEqual(operations["arange"]["flop_cost"], 1_024)
        self.assertEqual(operations["broadcast_to"]["calls"], 1)
        self.assertEqual(operations["broadcast_to"]["flop_cost"], 0)
        self.assertEqual(operations["random.Generator.permuted"]["calls"], 1)
        self.assertEqual(
            operations["random.Generator.permuted"]["flop_cost"], 31_744
        )
        self.assertNotIn("argsort", operations)

        source = inspect.getsource(m231.issue_permuted_receipt)
        for forbidden in ("unique", "tolist", "set(", "argsort", "choice"):
            self.assertNotIn(forbidden, source)

    def test_receipt_co_permutation_is_pathwise_and_binding_fails_closed(self):
        with flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=30.0):
            receipt = m231.issue_permuted_receipt(
                layers=1,
                width=9,
                subset_rows=3,
                seed=231501,
                producer_epoch=231,
                domain=m231.DOMAIN,
            )
        rng = np.random.Generator(np.random.Philox(231502))
        weight = rng.normal(size=(9, 11))
        factor = rng.normal(size=9)
        baseline = m227.compile_row_sketch_collision_source_numpy(
            weight, factor, receipt.selected[0]
        )
        permutation = rng.permutation(9)
        transformed = m231.co_permute_receipt(receipt, permutation)
        actual = m227.compile_row_sketch_collision_source_numpy(
            weight[permutation], factor[permutation], transformed.selected[0]
        )
        self.assertLessEqual(
            m205.source_max_abs_difference(baseline, actual), 2e-10
        )
        with self.assertRaises(ValueError):
            m231.validate_receipt(
                transformed,
                layers=1,
                width=9,
                subset_rows=3,
                producer_epoch=999,
                domain=m231.DOMAIN,
            )
        with self.assertRaises(ValueError):
            m231.validate_receipt(
                transformed,
                layers=1,
                width=9,
                subset_rows=3,
                producer_epoch=231,
                domain="wrong-domain",
            )

    def test_native_draw_matches_m227_row_oracle_and_frozen_target_bill(self):
        records = _records(31, 256)
        with flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0):
            staged = m212.allocate_staged_inputs()
            base = m212.allocate_workspace(depth=3)
            m212.stage_inputs(records, staged, expected_epoch=231)
            full_outputs = m212.compile_staged_stack(staged, base, depth=3)
        full = tuple(np.asarray(value).copy() for value in full_outputs[:3])
        full_receipt = m231.issue_full_domain_receipt(staged, base, full_outputs)

        budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        with budget:
            workspace = m231.allocate_row_workspace()
            strict, row_receipt = m231.subtract_permuted_row_sketch_inplace(
                staged,
                base,
                workspace,
                full_receipt,
                seed=227700001,
                subset_rows=32,
                domain=m231.DOMAIN,
            )
        self.assertEqual(int(budget.flops_used), 864_993_280)
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 2)
        self.assertEqual(operations["multiply"]["calls"], 16)
        self.assertEqual(operations["add"]["calls"], 9)
        self.assertEqual(operations["sum"]["calls"], 1)
        self.assertEqual(operations["copyto"]["calls"], 1)
        self.assertNotIn("reshape", operations)
        self.assertNotIn("argsort", operations)

        strict_arrays = tuple(np.asarray(value) for value in strict)
        for layer in (0, 15, 30):
            expected_collision = m227.compile_row_sketch_collision_source_numpy(
                records[layer].weight,
                records[layer].factor,
                row_receipt.selected[layer],
            )
            delta = m205.Source211(
                full[0][layer] - strict_arrays[0][layer],
                full[1][layer] - strict_arrays[1][layer],
                full[2][layer] - strict_arrays[2][layer],
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(delta, expected_collision), 2e-9
            )
        ledger = m231.allocation_ledger(staged, base, workspace)
        self.assertEqual(ledger["incremental_persistent_mib"], 36.873046875)
        self.assertEqual(ledger["incremental_nominal_peak_mib"], 36.875)
        self.assertEqual(ledger["m212_m231_persistent_mib"], 138.955078125)

    def test_small_width_expectation_reuses_unchanged_m227_algebra(self):
        worst = 0.0
        for width in range(3, 10):
            rng = np.random.Generator(np.random.Philox(227000 + width))
            weight = rng.normal(scale=0.35, size=(width, width + 2))
            factor = rng.normal(scale=0.25, size=width)
            full = m205.compile_lifted_rank_one_control(weight, factor)
            exact = m215.subtract_source(
                full, m215.compile_rank_one_collision_source_numpy(weight, factor)
            )
            draws = []
            for seed in range(400):
                with flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=30.0):
                    receipt = m231.issue_permuted_receipt(
                        layers=1,
                        width=width,
                        subset_rows=1,
                        seed=2310000 + width * 1000 + seed,
                        producer_epoch=231,
                        domain=m231.DOMAIN,
                    )
                draws.append(
                    m215.subtract_source(
                        full,
                        m227.compile_row_sketch_collision_source_numpy(
                            weight, factor, receipt.selected[0]
                        ),
                    )
                )
            mean = m205.Source211(
                np.mean([draw.aaaa for draw in draws], axis=0),
                np.mean([draw.aaab for draw in draws], axis=0),
                np.mean([draw.aabb for draw in draws], axis=0),
            )
            # This stochastic smoke check is deliberately loose; exact
            # exhaustive unbiasedness was already proved by M227's frozen test.
            scale = max(
                1.0,
                float(np.max(np.abs(exact.aaab))),
                float(np.max(np.abs(exact.aabb))),
            )
            worst = max(
                worst, m205.source_max_abs_difference(mean, exact) / scale
            )
        self.assertLessEqual(worst, 0.25)

    def test_predeclaration_exists_and_g0_is_closed(self):
        self.assertTrue((HERE / "M231_PREDECLARATION_20260809.md").exists())
        self.assertTrue((HERE / "M231_FROZEN_MANIFEST_20260809.json").exists())
        self.assertFalse((HERE / "M231_G0_RESULTS_20260809.json").exists())


if __name__ == "__main__":
    unittest.main()
