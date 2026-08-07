"""Write M172's generated-only static result; never execute source variance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m172_selective_22_owner_fusion",
    "m156_extended_domain_star_control",
    "m167_collision_owner_unification",
):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from m156_extended_domain_star_control import source_max_abs_difference
from m167_collision_owner_unification import PhysicalFourthOwners, complete_source_reference
from m172_selective_22_owner_fusion import (
    CONFIRMATION_CELLS,
    DEVELOPMENT_CELLS,
    complete_selective_source,
    independent_22_tensor_source,
    m163_selective_22_conservation_error,
    old_separate_22_source,
    static_owner_fusion_ledger,
    selective_22_complete_target,
)


OUT = HERE / "M172_STATIC_RESULTS_20260807.json"


def owners(rng: np.random.Generator, width: int) -> PhysicalFourthOwners:
    k31 = rng.normal(size=(width, width))
    k22 = rng.normal(size=(width, width))
    np.fill_diagonal(k31, 0.0)
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    return PhysicalFourthOwners(rng.normal(size=width), k31, k22)


def distinct(rng: np.random.Generator, width: int) -> np.ndarray:
    value = rng.normal(size=(width, width, width))
    return 0.5 * (value + value.swapaxes(1, 2))


def spd(rng: np.random.Generator, width: int) -> np.ndarray:
    factor = rng.normal(size=(width, width))
    return factor @ factor.T + np.eye(width)


def file_sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    rng = np.random.default_rng(1729001)
    tensor_errors: dict[str, float] = {}
    conservation_errors: dict[str, float] = {}
    retirement_errors: dict[str, float] = {}
    for width in range(2, 8):
        value = owners(rng, width)
        weight = rng.normal(size=(width, width + 1))
        target = selective_22_complete_target(np.zeros((width, width, width)), value)
        tensor_errors[str(width)] = source_max_abs_difference(
            complete_source_reference(weight, target), independent_22_tensor_source(weight, value)
        )
        retirement_errors[str(width)] = source_max_abs_difference(
            complete_source_reference(weight, target), old_separate_22_source(weight, value)
        )
        conservation_errors[str(width)] = m163_selective_22_conservation_error(
            weight, distinct(rng, width), value, spd(rng, width)
        )
    result = {
        "candidate": "M172 selective physical [2,2] owner fusion into M163 ijj rows",
        "status": "STATIC_OWNER_ALGEBRA_PASS__DEVELOPMENT_BLOCKED_M174_UNLAWFUL_CALLER_ABI",
        "firewall": "generated source algebra/static accounting only; no variance run, response, truth, scorer, leaderboard, submission, or champion access",
        "one_changed_mechanism": "transfer physical K22 only into ordered M163 ijj complete-domain rows; retain [4] and [3,1] separate owners; residual is K22/2-cE",
        "static_checks": {
            "independent_symmetric_tensor_max_abs_by_width": tensor_errors,
            "old_separate_22_source_max_abs_by_width": retirement_errors,
            "m163_complete_domain_conservation_max_abs_by_width": conservation_errors,
            "tolerance": 3e-10,
            "widths": list(range(2, 8)),
        },
        "ledger": static_owner_fusion_ledger(),
        "frozen_development_cells": DEVELOPMENT_CELLS,
        "sealed_confirmation_cells": CONFIRMATION_CELLS,
        "development": {
            "executed": False,
            "reason": "M174 established that the actual caller has no lawful labelled all-31 W,V/source-carrier ABI; M169's conditional generated-stack resource pass cannot open development.",
        },
        "confirmation": {"executed": False, "reason": "sealed until every development gate passes"},
        "dependency_sha256": {
            "m122_nonzero_bridge.py": file_sha256("m122_nonzero_bridge_theory/m122_nonzero_bridge.py"),
            "m129_source_frechet.py": file_sha256("m129_source_frechet_tangent/m129_source_frechet.py"),
            "m163_exterior_collision_null.py": file_sha256("m163_exterior_collision_null/m163_exterior_collision_null.py"),
            "m167_collision_owner_unification.py": file_sha256("m167_collision_owner_unification/m167_collision_owner_unification.py"),
            "m169_closeout_manifest": file_sha256("m169_m163_call_fusion/M169_FROZEN_CLOSEOUT_MANIFEST_20260807.json"),
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "status": result["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
