"""GATE 3: rerun the frozen permutation / positive-scale equivariance checks
against the revived (repaired-reducer) build, and compare with the values the
original killed run recorded.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import repaired_reducer as rr  # noqa: E402  (installs the repaired reducer)
from frozen_paths import HERE, ORIGINAL_PARTIAL, SPARSE_DIR  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "invariance_checks", str(SPARSE_DIR / "invariance_checks.py")
)
checks = importlib.util.module_from_spec(spec)
sys.modules["invariance_checks"] = checks
spec.loader.exec_module(checks)

revived = checks.run_checks()
original = json.loads(ORIGINAL_PARTIAL.read_text(encoding="utf-8"))["invariance"]

out = {
    "gate": "gate3_permutation_and_positive_scale_equivariance",
    "tolerance": 1e-10,
    "revived": revived,
    "original_killed_run": original,
    "agreement": {
        "permutation_relative_max_error_revived": revived["permutation"][
            "relative_max_error"
        ],
        "permutation_relative_max_error_original": original["permutation"][
            "relative_max_error"
        ],
        "both_pass": bool(revived["pass"] and original["permutation"]["pass"]),
    },
    "passes": bool(revived["pass"]),
}
(HERE / "invariance_results.json").write_text(
    json.dumps(out, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(out, indent=2))
