"""RED/GREEN setup, provenance, algebra, and bill contract for frozen M235."""

from __future__ import annotations

import hashlib
import inspect
from itertools import combinations
from pathlib import Path
import sys
import unittest

import flopscope as flops
import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[5]
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

import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
import m215_rankone_collision_correction as m215  # noqa: E402
import m227_row_subset_collision_ht as m227  # noqa: E402
from m215_flopscope_sidecar import issue_full_domain_receipt  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402
import m235_setup_shared_philox_row_receipt as m235  # noqa: E402


PINNED_LIFECYCLE_HASHES = {
    "whestbench/sdk.py": "B0FCC52C6B531981E46DA6955365AA786260FAB53FD66DCF3675791ED8C3C105",
    "whestbench/subprocess_worker.py": "F1EA178C94E4F7BA790EC1350D83A078982964D6A0C88F90EF58522A234EC089",
    "whestbench/runner.py": "6176EB3A91233AC6AAB8057141C2E82FEEA02BDF955E9F830EE8F756DE9ABC86",
}


def _records(seed: int, epoch: int = 231) -> list[LayerInput]:
    rng = np.random.Generator(np.random.Philox(seed))
    he = np.sqrt(2.0 / 256.0)
    return [
        LayerInput(
            layer=layer + 1,
            weight=rng.standard_normal((256, 256)) * he,
            factor=rng.standard_normal(256) / 16.0,
            producer_epoch=epoch,
        )
        for layer in range(31)
    ]


def _direct_row_oracle(
    weight: np.ndarray, factor: np.ndarray, selected: np.ndarray
) -> m205.Source211:
    """Independent scalar row loop for the frozen partial HT collision source."""

    scaled = factor[:, None] * weight
    p = np.sum(scaled, axis=0)
    gram = scaled.T @ scaled
    rho = np.diag(gram).copy()
    scale = float(scaled.shape[0]) / float(len(selected))
    t = np.zeros(scaled.shape[1], dtype=np.float64)
    a = np.zeros((scaled.shape[1], scaled.shape[1]), dtype=np.float64)
    e = np.zeros_like(a)
    d = np.zeros_like(a)
    for index in selected:
        row = scaled[int(index)]
        row2 = row * row
        row3 = row2 * row
        t += row3
        a += np.outer(row2, row)
        e += np.outer(row3, row)
        d += np.outer(row2, row2)
    t *= scale
    a *= scale
    e *= scale
    d *= scale
    aaab = (
        -18.0 * (p[:, None] * a)
        - 6.0 * np.outer(t, p)
        - 12.0 * (rho[:, None] * gram)
        + 24.0 * e
    )
    aabb = (
        -12.0 * (a * p[None, :] + p[:, None] * a.T)
        - 4.0 * np.outer(rho, rho)
        - 8.0 * (gram * gram)
        + 24.0 * d
    )
    return m205.Source211(np.diag(aaab).copy(), aaab, aabb)


def _co_permuted_selected(
    rank_order: np.ndarray, permutation: np.ndarray, subset_rows: int
) -> np.ndarray:
    """Host-only label action; production never imports NumPy for this audit."""

    width = int(permutation.size)
    inverse = np.empty(width, dtype=np.int64)
    inverse[permutation] = np.arange(width, dtype=np.int64)
    return inverse[rank_order][:, :subset_rows]


class M235SetupAndAlgebraTests(unittest.TestCase):
    def test_frozen_documents_and_lifecycle_hashes_exist_before_g0(self):
        expected = (
            "M235_PREDECLARATION_20260809.md",
            "M235_FROZEN_MANIFEST_20260809.json",
            "M235_PREIMPLEMENTATION_ERRATUM_20260809.md",
            "M235_PREIMPLEMENTATION_ERRATUM2_20260809.md",
            "M235_PREIMPLEMENTATION_ERRATUM3_20260809.md",
            "M235_PREIMPLEMENTATION_ERRATUM4_20260809.md",
        )
        self.assertTrue(all((HERE / name).exists() for name in expected))
        self.assertFalse((HERE / "M235_G0_RESULTS_20260809.json").exists())
        site = ROOT / "work" / "whest-v014" / "Lib" / "site-packages"
        actual = {
            name: hashlib.sha256((site / name).read_bytes()).hexdigest().upper()
            for name in PINNED_LIFECYCLE_HASHES
        }
        self.assertEqual(actual, PINNED_LIFECYCLE_HASHES)

    def test_setup_owns_exact_philox_receipt_and_eighteen_empty_workspaces(self):
        budget = flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=30.0)
        with budget:
            state = m235.setup_component(
                setup_seed=0,
                layers=31,
                width=256,
                subset_rows=32,
                producer_epoch=231,
                depth=3,
            )
        operations = budget.summary_dict()["operations"]
        self.assertEqual(int(budget.flops_used), 32_768)
        self.assertEqual(operations["empty"]["calls"], 18)
        self.assertEqual(operations["empty"]["flop_cost"], 0)
        self.assertEqual(operations["arange"]["calls"], 1)
        self.assertEqual(operations["arange"]["flop_cost"], 1_024)
        self.assertEqual(operations["broadcast_to"]["calls"], 1)
        self.assertEqual(operations["random.Generator.permuted"]["calls"], 1)
        self.assertEqual(
            operations["random.Generator.permuted"]["flop_cost"], 31_744
        )

        rank = np.asarray(state.receipt.rank_order)
        selected = np.asarray(state.receipt.selected)
        self.assertEqual(rank.shape, (31, 256))
        self.assertEqual(selected.shape, (31, 32))
        self.assertTrue(
            all(np.array_equal(np.sort(row), np.arange(256)) for row in rank)
        )
        self.assertTrue(all(np.unique(row).size == 32 for row in selected))
        self.assertFalse(state.receipt.rank_order.flags.writeable)
        self.assertFalse(state.receipt.selected.flags.writeable)
        self.assertEqual(state.receipt.setup_seed, 0)
        self.assertEqual(state.receipt.layer_ids, tuple(range(1, 32)))

        source = inspect.getsource(m235.issue_setup_receipt)
        self.assertIn("fnp.random.Generator(fnp.random.Philox(int(setup_seed)))", source)
        self.assertNotIn("default_rng", source)
        for forbidden in ("time.time", "os.urandom", "argsort", "choice", "retry"):
            self.assertNotIn(forbidden, source)

    def test_predict_correction_has_no_rng_allocation_or_audit_and_exact_bill(self):
        state = m235.setup_component(
            setup_seed=235700001,
            layers=31,
            width=256,
            subset_rows=32,
            producer_epoch=231,
            depth=3,
        )
        records = _records(227700001)
        setup_budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        with setup_budget:
            m212.stage_inputs(records, state.staged, expected_epoch=231)
            full_outputs = m212.compile_staged_stack(state.staged, state.base, depth=3)
        self.assertEqual(int(setup_budget.flops_used), 1_249_253_376)
        self.assertNotIn("empty", setup_budget.summary_dict()["operations"])
        full_arrays = tuple(np.asarray(value).copy() for value in full_outputs[:3])
        full_receipt = issue_full_domain_receipt(state.staged, state.base, full_outputs)

        correction = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
        with correction:
            strict = m235.subtract_setup_row_sketch_inplace(state, full_receipt)
        self.assertEqual(int(correction.flops_used), 864_960_512)
        operations = correction.summary_dict()["operations"]
        expected_calls = {
            "take_along_axis": 1,
            "matmul": 2,
            "multiply": 16,
            "add": 9,
            "sum": 1,
            "copyto": 1,
        }
        for operation, calls in expected_calls.items():
            self.assertEqual(operations[operation]["calls"], calls)
        for forbidden in (
            "empty",
            "arange",
            "broadcast_to",
            "random.Generator.permuted",
            "reshape",
            "transpose",
            "swapaxes",
            "diagonal",
        ):
            self.assertNotIn(forbidden, operations)

        strict_arrays = tuple(np.asarray(value) for value in strict)
        for layer in range(31):
            expected_collision = m227.compile_row_sketch_collision_source_numpy(
                records[layer].weight,
                records[layer].factor,
                state.receipt.selected[layer],
            )
            actual_collision = m205.Source211(
                full_arrays[0][layer] - strict_arrays[0][layer],
                full_arrays[1][layer] - strict_arrays[1][layer],
                full_arrays[2][layer] - strict_arrays[2][layer],
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(actual_collision, expected_collision),
                2e-9,
            )

        source = inspect.getsource(m235.subtract_setup_row_sketch_inplace)
        for forbidden in (
            "default_rng",
            "Philox",
            "Generator",
            "arange",
            "broadcast_to",
            "permuted",
            "empty",
            "allocation_ledger",
            "hash",
            "isfinite",
            "unique",
            "sort",
            "dtype",
            "shape",
        ):
            self.assertNotIn(forbidden, source)

        module_source = (HERE / "m235_setup_shared_philox_row_receipt.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("import numpy as np", module_source)
        self.assertNotIn("m215_flopscope_sidecar", module_source)

    def test_small_width_row_loop_gauge_zero_and_cubic_oracles(self):
        for width in range(3, 10):
            k = 1 if width < 8 else width // 8
            receipt = m235.issue_setup_receipt(
                setup_seed=2353000 + width,
                layers=31,
                width=width,
                subset_rows=k,
                producer_epoch=231,
            )
            rng = np.random.Generator(np.random.Philox(2354000 + width))
            weight = rng.normal(scale=0.35, size=(width, width + 2))
            factor = rng.normal(scale=0.25, size=width)
            selected = np.asarray(receipt.selected[0])

            actual = m227.compile_row_sketch_collision_source_numpy(
                weight, factor, selected
            )
            row_loop = _direct_row_oracle(weight, factor, selected)
            self.assertLessEqual(
                m205.source_max_abs_difference(actual, row_loop), 2e-10
            )

            gauge = np.exp(rng.uniform(-0.7, 0.7, size=width))
            gauged = m227.compile_row_sketch_collision_source_numpy(
                weight / gauge[:, None], factor * gauge, selected
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(actual, gauged), 2e-10
            )

            zero = m227.compile_row_sketch_collision_source_numpy(
                weight, np.zeros_like(factor), selected
            )
            self.assertTrue(np.array_equal(zero.aaaa, np.zeros_like(zero.aaaa)))
            self.assertTrue(np.array_equal(zero.aaab, np.zeros_like(zero.aaab)))
            self.assertTrue(np.array_equal(zero.aabb, np.zeros_like(zero.aabb)))

            full = m205.compile_lifted_rank_one_control(weight, factor)
            exact = m215.subtract_source(
                full, m215.compile_rank_one_collision_source_numpy(weight, factor)
            )
            table = m205.rank_one_control_table(factor)
            for i in range(width):
                for j in range(width):
                    for ell in range(width):
                        if len({i, j, ell}) < 3:
                            table[i, j, ell] = 0.0
            cubic = m205.brute_complete_source(weight, table)
            self.assertLessEqual(
                m205.source_max_abs_difference(exact, cubic), 2e-10
            )

    def test_receipt_marginal_algebra_and_pathwise_hidden_row_covariance(self):
        for width in range(3, 10):
            k = 1 if width < 8 else max(1, width // 8)
            receipt = m235.issue_setup_receipt(
                setup_seed=2350000 + width,
                layers=31,
                width=width,
                subset_rows=k,
                producer_epoch=231,
            )
            rng = np.random.Generator(np.random.Philox(2351000 + width))
            weight = rng.normal(scale=0.35, size=(width, width + 2))
            factor = rng.normal(scale=0.25, size=width)
            baseline = m227.compile_row_sketch_collision_source_numpy(
                weight, factor, receipt.selected[0]
            )
            permutation = rng.permutation(width)
            transformed_selected = _co_permuted_selected(
                np.asarray(receipt.rank_order), permutation, k
            )
            actual = m227.compile_row_sketch_collision_source_numpy(
                weight[permutation], factor[permutation], transformed_selected[0]
            )
            self.assertLessEqual(
                m205.source_max_abs_difference(baseline, actual), 2e-10
            )

            full = m205.compile_lifted_rank_one_control(weight, factor)
            exact = m215.subtract_source(
                full, m215.compile_rank_one_collision_source_numpy(weight, factor)
            )
            subsets = list(combinations(range(width), k))
            draws = [
                m215.subtract_source(
                    full,
                    m227.compile_row_sketch_collision_source_numpy(
                        weight, factor, np.asarray(indices, dtype=np.int64)
                    ),
                )
                for indices in subsets
            ]
            mean = m205.Source211(
                np.mean([draw.aaaa for draw in draws], axis=0),
                np.mean([draw.aaab for draw in draws], axis=0),
                np.mean([draw.aabb for draw in draws], axis=0),
            )
            self.assertLessEqual(m205.source_max_abs_difference(mean, exact), 2e-10)


if __name__ == "__main__":
    unittest.main()
