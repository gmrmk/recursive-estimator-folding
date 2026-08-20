from __future__ import annotations

import inspect
from pathlib import Path
import sys
import tracemalloc
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
M205 = HERE.parent / "m205_rankone_complete_physical_owner"
M209 = HERE.parent / "m209_batched_recursive_gram_control"
M210 = HERE.parent / "m210_level_fused_recursive_gram"
for path in (HERE, M205, M209, M210):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:
    import flopscope as flops
    HAVE_FLOPSCOPE = True
except ModuleNotFoundError:
    HAVE_FLOPSCOPE = False

if HAVE_FLOPSCOPE:
    import m205_rankone_complete_physical_owner as m205
    import m212_flopscope_sidecar as m212
    from m209_flopscope_sidecar import LayerInput


@unittest.skipUnless(HAVE_FLOPSCOPE, "pinned FlopScope runtime is required")
class M212ContractTests(unittest.TestCase):
    def _records(self):
        rng = np.random.default_rng(212101)
        return [
            LayerInput(
                layer=i + 1,
                weight=rng.normal(scale=0.2, size=(8, 8)),
                factor=rng.normal(scale=0.1, size=8),
                producer_epoch=212,
            )
            for i in range(3)
        ]

    def test_explicit_symmetry_and_source_parity(self):
        records = self._records()
        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            staged = m212.allocate_staged_inputs(layers=3, width=8)
            workspace = m212.allocate_workspace(layers=3, width=8, depth=3)
            m212.stage_inputs(records, staged, expected_epoch=212)
            outputs = m212.compile_staged_stack(staged, workspace, depth=3)
        operations = budget.summary_dict()["operations"]
        self.assertEqual(operations["matmul"]["calls"], 4)
        self.assertEqual(operations["reshape"]["calls"], 4)
        aaaa, aaab, aabb, gram, _p = map(np.asarray, outputs)
        self.assertTrue(np.array_equal(gram, np.swapaxes(gram, 1, 2)))
        self.assertTrue(np.array_equal(aabb, np.swapaxes(aabb, 1, 2)))
        for layer, record in enumerate(records):
            expected = m205.compile_lifted_rank_one_control(record.weight, record.factor)
            self.assertLessEqual(float(np.max(np.abs(aaaa[layer] - expected.aaaa))), 2e-10)
            self.assertLessEqual(float(np.max(np.abs(aaab[layer] - expected.aaab))), 2e-10)
            self.assertLessEqual(float(np.max(np.abs(aabb[layer] - expected.aabb))), 2e-10)

    def test_source_contains_no_overlapping_transpose_add(self):
        source = inspect.getsource(m212.compile_staged_stack)
        self.assertIn("fnp.copyto(x.scratch, fnp.swapaxes(x.aabb, 1, 2))", source)
        self.assertNotIn("fnp.add(x.aabb, fnp.swapaxes(x.aabb", source)

    def test_target_symmetry_operation_has_no_plane_temporary(self):
        import flopscope.numpy as fnp

        rng = np.random.default_rng(212102)
        value = rng.normal(size=(31, 256, 256))
        scratch = np.empty_like(value)
        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        tracemalloc.start()
        tracemalloc.reset_peak()
        with budget:
            fnp.copyto(scratch, fnp.swapaxes(value, 1, 2))
            fnp.add(value, scratch, out=value)
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(int(budget.flops_used), 8_126_464)
        self.assertLess(peak, 1024 * 1024)
        self.assertTrue(np.array_equal(value, np.swapaxes(value, 1, 2)))

    def test_binding_remains_fail_closed(self):
        records = self._records()
        staged = m212.allocate_staged_inputs(layers=3, width=8)
        with self.assertRaises(ValueError):
            m212.stage_inputs(list(reversed(records)), staged, expected_epoch=212)
        workspace = m212.allocate_workspace(layers=3, width=8, depth=3)
        with self.assertRaises(ValueError):
            m212.compile_staged_stack(staged, workspace, depth=3)


if __name__ == "__main__":
    unittest.main()
