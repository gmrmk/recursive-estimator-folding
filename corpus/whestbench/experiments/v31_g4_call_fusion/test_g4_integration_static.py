"""Static integration contracts for the isolated V31-G4 package source."""

from __future__ import annotations

import ast
import hashlib
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "candidate_source"
PARENT = HERE.parent / "v31_guards" / "package_source"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def executable_ast(path: Path) -> str:
    """Return an AST census with all documentation strings removed."""
    tree = ast.parse(path.read_text("utf-8"))
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body = node.body[1:]
    return ast.dump(tree, include_attributes=False)


class IntegrationStaticContracts(unittest.TestCase):
    def test_untouched_parent_members_are_byte_identical(self):
        expected = {
            "base_estimator.py": "B64376E09279E520465D63C4C0B2933A8EDB0EC8EAE9D6086C16C1830E7ECE4E",
            "cost_model.py": "2A42E0D9CA3A80ECB4FF2BE302CCFAAACFA34BF6FE920B1EEA27FEB7AE798D68",
            "fold_estimator.py": "0C6187E19CF567D7F7B5658902DC00A123F6219C815E2EA6711589E0A4E9159D",
            "kerdock_phases.npz": "A5E747F95423F5A45972D1A0735F223044A8A998407EB0C6DB51AEFDF47F4906",
            "sobol_owen_u32.npz": "050339EC9966BD046B4FCF53C85240F89D2CD1F7D60C30421922203045EED0CA"
        }
        for name, digest in expected.items():
            with self.subTest(name=name):
                self.assertEqual(sha256(PARENT / name), digest)
                self.assertEqual((PARENT / name).read_bytes(), (CANDIDATE / name).read_bytes())

    def test_guards_wrapper_changes_documentation_not_executable_ast(self):
        parent = PARENT / "estimator.py"
        child = CANDIDATE / "estimator.py"
        self.assertEqual(
            sha256(parent),
            "5E7D52156B330BF63AC4FF0E0F38D864B32677F82BC8ED4D1382787A27D3E0C9",
        )
        self.assertNotEqual(parent.read_bytes(), child.read_bytes())
        self.assertEqual(executable_ast(parent), executable_ast(child))
        child_text = child.read_text("utf-8")
        self.assertIn("V31-G4", child_text)
        self.assertIn("full-wrapper and guard-path parity remain unearned", child_text)

    def test_fold3_reuses_setup_owned_activation(self):
        source = (CANDIDATE / "fold3_estimator.py").read_text("utf-8")
        self.assertIn('activation = getattr(self, "_activation", None)', source)
        self.assertIn("setup() did not bind the sampled activation", source)
        self.assertNotIn(
            "activation = fnp.empty((2 * self.n_base, mlp.width)",
            source,
        )

    def test_kerdock_setup_allocates_then_binds_both_width_paths(self):
        source = (CANDIDATE / "kerdock_v3_estimator.py").read_text("utf-8")
        tree = ast.parse(source)
        setup = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "setup"
        )
        setup_source = ast.get_source_segment(source, setup)
        self.assertIsNotNone(setup_source)
        self.assertIn("GroupedRowBlockedBatchedWinograd", source)
        self.assertEqual(setup_source.count("self._allocate_grouped_activation(ctx.width)"), 2)
        self.assertEqual(setup_source.count("self._winograd.bind(self._activation)"), 2)

    def test_package_surface_has_only_expected_members(self):
        members = sorted(
            path.relative_to(CANDIDATE).as_posix()
            for path in CANDIDATE.rglob("*")
        )
        self.assertEqual(
            members,
            [
                "base_estimator.py",
                "cost_model.py",
                "estimator.py",
                "fold3_estimator.py",
                "fold_estimator.py",
                "kerdock_phases.npz",
                "kerdock_v3_estimator.py",
                "row_blocked_winograd.py",
                "sobol_owen_u32.npz",
            ],
        )


if __name__ == "__main__":
    unittest.main()
