"""Static restricted-import audit for the M145 deployment closure.

This audit intentionally distinguishes an application importing ordinary
``numpy`` from FlopScope internally depending on its own backend.  It rejects
every direct import of numpy in the code shipped by this candidate and its
sealed Formal-L1 closure.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent / "row_blocked_production" / "candidate_source"
DEPLOYED = (
    HERE / "m145_deployable_core.py",
    HERE / "m145_deployable_sidecar.py",
    HERE / "m145_deployable_estimator.py",
)
FORMAL_FILES = tuple(sorted(FORMAL.glob("*.py")))


def direct_numpy_imports(path: Path) -> list[dict]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "numpy" or alias.name.startswith("numpy."):
                    bad.append({"line": node.lineno, "import": alias.name})
        elif isinstance(node, ast.ImportFrom) and node.module and (
            node.module == "numpy" or node.module.startswith("numpy.")
        ):
            bad.append({"line": node.lineno, "import": node.module})
    return bad


def main() -> None:
    files = DEPLOYED + FORMAL_FILES
    violations = {
        str(path.relative_to(HERE.parent)): direct_numpy_imports(path)
        for path in files
        if direct_numpy_imports(path)
    }
    payload = {
        "status": "PASS" if not violations else "FAIL",
        "scope": "candidate deployment closure + sealed Formal-L1 sources",
        "direct_numpy_imports": violations,
        "files": {
            str(path.relative_to(HERE.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
        },
        "note": (
            "This rejects direct ordinary NumPy imports in shipped candidate code. "
            "It does not reject FlopScope's own private backend dependencies."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
