from __future__ import annotations

import importlib.util
import itertools
from pathlib import Path
import sys
import unittest

import numpy as np

try:
    import flopscope as flops
    HAVE_FLOPSCOPE = True
except ModuleNotFoundError:
    HAVE_FLOPSCOPE = False


HERE = Path(__file__).resolve().parent
M205_DIR = HERE.parent / "m205_rankone_complete_physical_owner"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class M217BalancedThreeColorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m217 = _load(
            "m217_balanced_three_color_strict_control",
            HERE / "m217_balanced_three_color_strict_control.py",
        )
        cls.m205 = _load(
            "m205_for_m217",
            M205_DIR / "m205_rankone_complete_physical_owner.py",
        )

    def test_balanced_coloring_expectation_is_strict_indicator(self):
        for width in range(3, 7):
            sizes = self.m217.balanced_sizes(width)
            base = tuple(color for color, count in enumerate(sizes) for _ in range(count))
            colorings = sorted(set(itertools.permutations(base)))
            factor = np.linspace(0.3, 1.1, width)
            average = np.mean(
                [self.m217.masked_control_table(factor, np.array(h)) for h in colorings],
                axis=0,
            )
            strict = self.m217.strict_control_table(factor)
            self.assertLessEqual(float(np.max(np.abs(average - strict))), 2e-13)

    def test_non_cubic_compiler_matches_colored_cubic_oracle(self):
        for width in range(3, 10):
            for seed in (217001, 217002, 217003, 217004, 217005, 217006):
                rng = np.random.default_rng(seed + 1000 * width)
                weight = rng.normal(size=(width, width + 2))
                factor = rng.uniform(0.05, 1.2, size=width)
                colors = self.m217.random_balanced_colors(width, seed)
                table = self.m217.masked_control_table(factor, colors)
                expected = self.m205.brute_complete_source(weight, table)
                actual = self.m217.compile_colored_control(weight, factor, colors)
                error = self.m205.source_max_abs_difference(expected, actual)
                self.assertLessEqual(error, 4e-11)

    def test_support_conservation_gauge_and_joint_permutation(self):
        rng = np.random.default_rng(217991)
        width = 7
        weight = rng.normal(size=(width, 9))
        factor = rng.uniform(0.1, 1.0, size=width)
        colors = self.m217.random_balanced_colors(width, 217005)
        table = self.m217.masked_control_table(factor, colors)
        for i in range(width):
            self.assertTrue(np.array_equal(table[i, i, :], np.zeros((width,))))
            self.assertTrue(np.array_equal(table[i, :, i], np.zeros((width,))))
            self.assertTrue(np.array_equal(table[:, i, i], np.zeros((width,))))

        target = rng.normal(size=(width, width, width))
        target = 0.5 * (target + target.swapaxes(1, 2))
        full = self.m205.brute_complete_source(weight, target)
        control = self.m217.compile_colored_control(weight, factor, colors)
        residual = self.m205.brute_complete_source(weight, target - table)
        reconstructed = self.m205.source_add(control, residual)
        self.assertLessEqual(self.m205.source_max_abs_difference(full, reconstructed), 4e-11)

        gauge = rng.uniform(0.4, 2.0, size=width)
        gauged = self.m217.compile_colored_control(
            weight / gauge[:, None], factor * gauge, colors
        )
        self.assertLessEqual(self.m205.source_max_abs_difference(control, gauged), 4e-11)

        permutation = rng.permutation(width)
        permuted = self.m217.compile_colored_control(
            weight[permutation], factor[permutation], colors[permutation]
        )
        self.assertLessEqual(self.m205.source_max_abs_difference(control, permuted), 4e-11)

    def test_firewall_keeps_variance_closed(self):
        manifest = (HERE / "M217_FROZEN_MANIFEST_20260809.json").read_text(encoding="utf-8")
        self.assertIn('"variance_authorized": false', manifest)
        self.assertIn('"efficacy_authorized": false', manifest)

    @unittest.skipUnless(HAVE_FLOPSCOPE, "pinned FlopScope runtime is required")
    def test_native_colored_stack_matches_algebra_without_rank3_storage(self):
        sidecar = _load("m217_flopscope_sidecar", HERE / "m217_flopscope_sidecar.py")
        rng = np.random.default_rng(217812)
        records = []
        for layer in range(1, 4):
            records.append(
                sidecar.ColoredLayerInput(
                    layer=layer,
                    weight=rng.normal(size=(8, 8)),
                    factor=rng.uniform(0.1, 1.0, size=8),
                    colors=self.m217.random_balanced_colors(8, 217800 + layer),
                    producer_epoch=217,
                )
            )
        budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with budget:
            staged = sidecar.allocate_staged_inputs(layers=3, width=8)
            workspace = sidecar.allocate_workspace(layers=3, width=8, depth=3)
            sidecar.stage_inputs(records, staged, expected_epoch=217)
            outputs = sidecar.compile_staged_stack(staged, workspace, depth=3)
        operations = budget.summary_dict()["operations"]
        self.assertLessEqual(int(operations.get("take", {}).get("calls", 0)), 2)
        self.assertLessEqual(
            int(operations.get("take_along_axis", {}).get("calls", 0)), 2
        )
        self.assertLessEqual(int(operations.get("multiply", {}).get("calls", 0)), 25)
        self.assertLessEqual(int(operations.get("add", {}).get("calls", 0)), 8)
        aaaa, aaab, aabb = map(np.asarray, outputs[:3])
        self.assertTrue(np.array_equal(aabb, np.swapaxes(aabb, 1, 2)))
        for index, record in enumerate(records):
            expected = self.m217.compile_colored_control(
                record.weight, record.factor, record.colors
            )
            actual = self.m217.Source211(aaaa[index], aaab[index], aabb[index])
            self.assertLessEqual(
                self.m205.source_max_abs_difference(expected, actual), 2e-10
            )
        ledger = sidecar.allocation_ledger(staged, workspace)
        self.assertEqual(ledger["rank3_coefficient_arrays"], 0)
        self.assertLessEqual(ledger["persistent_bytes"], 512 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
