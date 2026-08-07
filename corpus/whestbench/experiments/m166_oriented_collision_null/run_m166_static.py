"""Generated-array static trace for M166; deliberately no variance outcome."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in ("m166_oriented_collision_null", "m156_extended_domain_star_control"):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from m156_extended_domain_star_control import (  # noqa: E402
    dense_extended_source,
    source_max_abs_difference,
)
from m166_oriented_collision_null import (  # noqa: E402
    compile_oriented_star_control,
    f32_shared_control_report,
    orient_covariance_edges,
    oriented_star_table,
    static_cost_ledger,
)


def _digest(value: np.ndarray) -> str:
    packed = np.ascontiguousarray(value)
    return hashlib.sha256(memoryview(packed).cast("B")).hexdigest()


def main() -> None:
    rng = np.random.default_rng(166_000_001)
    width, outputs = 6, 4
    weight = rng.normal(size=(width, outputs))
    factor = rng.normal(size=(width, width))
    covariance = factor @ factor.T + np.eye(width)
    control = orient_covariance_edges(covariance)
    table = oriented_star_table(control)
    direct = dense_extended_source(weight, table)
    compiled = compile_oriented_star_control(weight, control)

    permutation = rng.permutation(width)
    permuted = compile_oriented_star_control(
        weight[permutation],
        orient_covariance_edges(covariance[permutation][:, permutation]),
    )
    gauge = np.exp(rng.uniform(-0.25, 0.25, size=width))
    gauged = compile_oriented_star_control(
        weight / gauge[:, None],
        orient_covariance_edges(gauge[:, None] * covariance * gauge[None, :]),
    )
    target32 = rng.normal(size=(width, width, width)).astype(np.float32)
    target32 = np.float32(0.5) * (target32 + target32.swapaxes(1, 2))
    f32 = f32_shared_control_report(target32, covariance.astype(np.float32))
    collision_max = max(
        float(np.max(np.abs(table[np.arange(width), np.arange(width), :]))),
        float(np.max(np.abs(table[np.arange(width), :, np.arange(width)]))),
        float(np.max(np.abs(table[:, np.arange(width), np.arange(width)]))),
    )
    assertions = {
        "all_collision_patterns_exactly_zero_by_equality": collision_max == 0.0,
        "supports_disjoint": bool(np.all(control.a * control.b == 0.0)),
        "compiler_matches_exhaustive_small_width": source_max_abs_difference(direct, compiled) < 4e-10,
        "permutation_covariant_f64_reference": source_max_abs_difference(compiled, permuted) < 5e-10,
        "positive_gauge_covariant_f64_reference": source_max_abs_difference(compiled, gauged) < 2e-9,
        "f32_uses_one_stored_control": bool(f32["same_control_object_used_by_both_arms"]),
        "exact_f64_cost_killed": not static_cost_ledger()["exact_f64_fits_cap"],
        "f32_static_cost_only_fits": bool(static_cost_ledger()["f32_static_fits_cap"]),
    }
    result = {
        "status": "M166_STATIC_ORIENTATION_COMPILER_PASS_F64_COST_KILLED_NO_EFFICACY",
        "firewall": (
            "generated covariance/weights only; no response, source variance, truth, "
            "score, scorer, competition row, leaderboard, submission, or champion mutation"
        ),
        "seed": 166_000_001,
        "shape": {"labels": width, "outputs": outputs},
        "control": {
            "score": control.score.tolist(),
            "tied_pair_count": control.tied_pair_count,
            "support_disjoint": bool(np.all(control.a * control.b == 0.0)),
            "a_sha256": _digest(control.a),
            "b_sha256": _digest(control.b),
            "collision_max_abs": collision_max,
        },
        "compiler": {
            "dense_product_count": 7,
            "exhaustive_max_abs_difference": source_max_abs_difference(direct, compiled),
            "permutation_max_abs_difference": source_max_abs_difference(compiled, permuted),
            "positive_gauge_max_abs_difference": source_max_abs_difference(compiled, gauged),
        },
        "f32_shared_control_numerics": f32,
        "cost": static_cost_ledger(),
        "assertions": assertions,
        "disposition": (
            "preserve f64 orientation/compiler theorem; exact f64 static cost is killed. "
            "The f32 ledger is a numerical, shared-control candidate only and receives no "
            "native or source-variance authorization."
        ),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)
    output = HERE / "M166_STATIC_TRACE_20260807.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output), "cost": result["cost"]}, sort_keys=True))


if __name__ == "__main__":
    main()
