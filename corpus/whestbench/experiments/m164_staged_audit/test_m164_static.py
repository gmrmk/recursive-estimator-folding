from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
M163 = HERE.parent / "m163_exterior_collision_null"
if str(M163) not in sys.path:
    sys.path.insert(0, str(M163))

from m163_exterior_collision_null import static_compiler_ledger  # noqa: E402


class TestM164StaticAudit(unittest.TestCase):
    def test_trace_has_no_outcome_or_network_imports(self) -> None:
        for name in ("m164_flopscope_sidecar.py", "run_m164_native_trace.py"):
            tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
            imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
            self.assertFalse(any(name.startswith(("whestbench", "aicrowd", "requests")) for name in imports))

    def test_m163_static_slot_is_prerequisite_not_a_sharing_credit(self) -> None:
        ledger = static_compiler_ledger()
        self.assertTrue(ledger["fits_cap"])
        self.assertTrue(ledger["native_trace_still_required"])
        self.assertEqual(ledger["dense_f64_products"], 5)


if __name__ == "__main__":
    unittest.main()
