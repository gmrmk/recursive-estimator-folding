"""RED/GREEN ownership, algebra, and bill contract for frozen M236."""

from __future__ import annotations

import gc
import hashlib
import inspect
from itertools import combinations
from pathlib import Path
import sys
import unittest

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m205_rankone_complete_physical_owner",
    BASE / "m209_batched_recursive_gram_control",
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m215_rankone_collision_correction",
    BASE / "m227_row_subset_collision_ht",
    BASE / "m235_setup_shared_philox_row_receipt",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m205_rankone_complete_physical_owner as m205  # noqa: E402
from m209_flopscope_sidecar import LayerInput  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402
import m215_rankone_collision_correction as m215  # noqa: E402
from m215_flopscope_sidecar import issue_full_domain_receipt  # noqa: E402
import m227_row_subset_collision_ht as m227  # noqa: E402
import m235_setup_shared_philox_row_receipt as m235  # noqa: E402
import m236_layer_batched_m212_m235 as m236  # noqa: E402


PREDECL_SHA = "793786132F08CE71ABACE2BDA29ADE347ED2800B9615799F85BA7F71836E3CC1"
MANIFEST_SHA = "3B9D3B43D7995FED5D1CA331B465F4DD71C236F0BA5F6D7497E392364D844CF2"
ERRATUM_SHA = "54A63B652A7288EBE06C526C1B0300356DA7B3D8F79D9E9C0D0BA505127E56E1"
EXPECTED_M212_CALLS = {
    "stack": 8,
    "matmul": 16,
    "reshape": 16,
    "add": 12,
    "copyto": 100,
    "diagonal": 8,
    "multiply": 44,
    "sum": 4,
    "swapaxes": 32,
    "transpose": 32,
}
EXPECTED_M235_CALLS = {
    "take_along_axis": 4,
    "matmul": 8,
    "add": 36,
    "copyto": 4,
    "multiply": 64,
    "sum": 4,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _records(
    *, width: int, layers: int, seed: int, epoch: int = 231, f32: bool = False
) -> list[LayerInput]:
    rng = np.random.Generator(np.random.Philox(seed))
    dtype = np.float32 if f32 else np.float64
    he = np.sqrt(2.0 / float(width))
    return [
        LayerInput(
            layer=layer + 1,
            weight=(rng.standard_normal((width, width)) * he).astype(dtype),
            factor=(rng.standard_normal(width) / np.sqrt(width)).astype(dtype),
            producer_epoch=epoch,
        )
        for layer in range(layers)
    ]


def _full_m235_bytes(
    records: list[LayerInput], *, setup_seed: int, width: int, k: int, depth: int
) -> tuple[bytes, bytes, bytes]:
    layers = len(records)
    state = m235.setup_component(
        setup_seed=setup_seed,
        layers=layers,
        width=width,
        subset_rows=k,
        producer_epoch=231,
        depth=depth,
    )
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    with budget:
        fnp.stack([record.weight for record in records], axis=0, out=state.staged.weight)
        fnp.stack([record.factor for record in records], axis=0, out=state.staged.factor)
        state.staged.layer_ids = tuple(range(1, layers + 1))
        state.staged.producer_epoch = 231
        full_outputs = m212.compile_staged_stack(state.staged, state.base, depth=depth)
        full = issue_full_domain_receipt(state.staged, state.base, full_outputs)
        strict = m235.subtract_setup_row_sketch_inplace(state, full)
    return tuple(np.asarray(value).tobytes(order="C") for value in strict)


def _direct_row_oracle(
    weight: np.ndarray, factor: np.ndarray, selected: np.ndarray
) -> m205.Source211:
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


class M236Block8ContractTests(unittest.TestCase):
    def test_frozen_documents_identity_and_initial_red_receipt(self):
        self.assertEqual(_sha(HERE / "M236_PREDECLARATION_20260809.md"), PREDECL_SHA)
        self.assertEqual(_sha(HERE / "M236_FROZEN_MANIFEST_20260809.json"), MANIFEST_SHA)
        self.assertEqual(
            _sha(HERE / "M236_PREIMPLEMENTATION_ERRATUM1_20260809.md"),
            ERRATUM_SHA,
        )
        self.assertTrue((HERE / "M236_TDD_RECEIPT_20260809.md").exists())
        self.assertFalse((HERE / "M236_G0_RESULTS_20260809.json").exists())
        self.assertEqual(m236.BLOCK_SIZE, 8)
        self.assertEqual(
            m236.BLOCK_SPANS,
            ((0, 8), (8, 16), (16, 24), (24, 31)),
        )

    def test_setup_owns_exact_arrays_aliases_and_global_local_bridge(self):
        budget = flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=30.0)
        with budget:
            state = m236.setup_component(setup_seed=0)
        operations = budget.summary_dict()["operations"]
        self.assertEqual(int(budget.flops_used), 32_768)
        self.assertEqual(operations["empty"]["calls"], 18)
        self.assertEqual(operations["empty"]["flop_cost"], 0)
        self.assertEqual(operations["arange"]["calls"], 1)
        self.assertEqual(operations["random.Generator.permuted"]["calls"], 1)

        ledger = m236.allocation_ledger(state)
        self.assertEqual(ledger["setup_empty_owner_count"], 18)
        self.assertEqual(ledger["numeric_peak_bytes"], 61_812_736)
        self.assertEqual(ledger["numeric_peak_mib"], 58.94921875)
        self.assertEqual(ledger["selected_gather_max_bytes"], 524_288)
        self.assertEqual(ledger["global_source_bytes"], 32_569_344)
        self.assertEqual(ledger["rank_receipt_bytes"], 63_488)
        self.assertEqual(ledger["m212_block_bytes"], 19_218_432)
        self.assertEqual(ledger["m235_block_bytes"], 9_437_184)

        self.assertEqual(len(state.block_plans), 4)
        spans = tuple((plan.start, plan.stop) for plan in state.block_plans)
        self.assertEqual(spans, m236.BLOCK_SPANS)
        covered = []
        for index, plan in enumerate(state.block_plans):
            count = plan.stop - plan.start
            covered.extend(plan.global_ids)
            self.assertEqual(plan.block_index, index)
            self.assertEqual(plan.global_ids, tuple(range(plan.start + 1, plan.stop + 1)))
            self.assertEqual(plan.local_ids, tuple(range(1, count + 1)))
            self.assertEqual(plan.receipt.selected.shape, (count, 32))
            self.assertTrue(
                np.shares_memory(plan.receipt.selected, state.receipt.selected)
            )
            self.assertTrue(np.shares_memory(plan.base.aaaa, state.outputs.aaaa))
            self.assertTrue(np.shares_memory(plan.base.aaab, state.outputs.aaab))
            self.assertTrue(np.shares_memory(plan.base.aabb, state.outputs.aabb))
            self.assertIs(plan.full.aaaa, plan.base.aaaa)
            self.assertIs(plan.full.aaab, plan.base.aaab)
            self.assertIs(plan.full.aabb, plan.base.aabb)
            self.assertEqual(len(plan.weight_slots), count)
            self.assertEqual(len(plan.factor_slots), count)
        self.assertEqual(covered, list(range(1, 32)))
        self.assertEqual(state.block_plans[-1].base.aaaa.shape, (7, 256))
        self.assertEqual(state.block_plans[-1].base.aaab.shape, (7, 256, 256))
        self.assertEqual(state.block_plans[-1].base.aabb.shape, (7, 256, 256))

        owners = m236.setup_owner_arrays(state)
        self.assertEqual(len(owners), 20)  # 18 empty owners + rank + selected alias
        empty_owners = owners[:18]
        self.assertEqual(len({id(value) for value in empty_owners}), 18)
        for value in empty_owners:
            if value.ndim >= 1 and value.shape[0] == 31:
                self.assertTrue(
                    any(
                        value is candidate
                        for candidate in (
                            state.outputs.aaaa,
                            state.outputs.aaab,
                            state.outputs.aabb,
                        )
                    )
                )

    def test_bridge_rejects_reorder_duplicate_epoch_and_cross_block_before_charge(self):
        state = m236.setup_component(setup_seed=0, layers=9, width=8, subset_rows=1)
        records = _records(width=8, layers=9, seed=23601001)
        bad_cases = []
        reordered = records.copy()
        reordered[0], reordered[1] = reordered[1], reordered[0]
        bad_cases.append(reordered)
        duplicated = records.copy()
        duplicated[1] = LayerInput(
            layer=2,
            weight=records[0].weight,
            factor=records[0].factor,
            producer_epoch=231,
        )
        bad_cases.append(duplicated)
        wrong_epoch = records.copy()
        wrong_epoch[8] = LayerInput(
            layer=9,
            weight=records[8].weight,
            factor=records[8].factor,
            producer_epoch=999,
        )
        bad_cases.append(wrong_epoch)
        for bad in bad_cases:
            budget = flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=30.0)
            with self.assertRaises(ValueError), budget:
                m236.compile_records_inplace(state, bad)
            self.assertEqual(int(budget.flops_used), 0)
        self.assertTrue(m236.staging_slots_clear(state))

    def test_small_width_algebra_oracles_and_candidate_reference_parity(self):
        for width in range(3, 10):
            k = 1 if width < 8 else width // 8
            receipt = m235.issue_setup_receipt(
                setup_seed=23602000 + width,
                layers=3,
                width=width,
                subset_rows=k,
                producer_epoch=231,
            )
            rng = np.random.Generator(np.random.Philox(23603000 + width))
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

            subsets = list(combinations(range(width), k))
            draws = [
                m227.compile_row_sketch_collision_source_numpy(
                    weight, factor, np.asarray(indices, dtype=np.int64)
                )
                for indices in subsets
            ]
            mean = m205.Source211(
                np.mean([draw.aaaa for draw in draws], axis=0),
                np.mean([draw.aaab for draw in draws], axis=0),
                np.mean([draw.aabb for draw in draws], axis=0),
            )
            exact_collision = m215.compile_rank_one_collision_source_numpy(weight, factor)
            self.assertLessEqual(
                m205.source_max_abs_difference(mean, exact_collision), 2e-10
            )

            records = _records(
                width=width, layers=3, seed=23604000 + width, f32=False
            )
            reference = _full_m235_bytes(
                records,
                setup_seed=23605000 + width,
                width=width,
                k=k,
                depth=0,
            )
            state = m236.setup_component(
                setup_seed=23605000 + width,
                layers=3,
                width=width,
                subset_rows=k,
                depth=0,
            )
            actual_source = m236.compile_records_inplace(state, records)
            self.assertEqual(
                tuple(np.asarray(value).tobytes(order="C") for value in actual_source),
                reference,
            )
            self.assertTrue(m236.staging_slots_clear(state))

    def test_target_f32_raw_byte_parity_exact_calls_bills_and_slot_release(self):
        state = m236.setup_component(setup_seed=0)
        for seed in (227700001, 227710001):
            records = _records(width=256, layers=31, seed=seed, f32=True)
            reference = _full_m235_bytes(
                records, setup_seed=0, width=256, k=32, depth=3
            )
            gc.collect()
            budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
            with budget:
                actual = m236.compile_records_inplace(state, records)
            self.assertEqual(int(budget.flops_used), 2_114_213_888)
            operations = budget.summary_dict()["operations"]
            expected_total = dict(EXPECTED_M212_CALLS)
            for name, calls in EXPECTED_M235_CALLS.items():
                expected_total[name] = expected_total.get(name, 0) + calls
            for name, calls in expected_total.items():
                self.assertEqual(operations[name]["calls"], calls, name)
            self.assertNotIn("empty", operations)
            self.assertNotIn("random.Generator.permuted", operations)
            self.assertEqual(
                tuple(np.asarray(value).tobytes(order="C") for value in actual),
                reference,
            )
            self.assertTrue(m236.staging_slots_clear(state))
            for plan in state.block_plans:
                self.assertTrue(all(value is None for value in plan.weight_slots))
                self.assertTrue(all(value is None for value in plan.factor_slots))

        source = inspect.getsource(m236.compile_records_inplace)
        for forbidden in (
            "fnp.empty",
            "fnp.arange",
            "permuted",
            "Philox",
            "default_rng",
            "concatenate",
            "copy(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
