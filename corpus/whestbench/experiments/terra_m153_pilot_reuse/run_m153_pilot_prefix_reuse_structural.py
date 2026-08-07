"""Emit a truth-free structural trace for the isolated M153 prototype."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP


HERE = Path(__file__).resolve().parent
M145 = HERE.parent / "m145_defensive_acg"
if str(M145) not in sys.path:
    sys.path.insert(0, str(M145))

from m145_integrated_estimator import Estimator  # noqa: E402
from m153_pilot_prefix_reuse import PrefixReuseEstimator  # noqa: E402


SETUP_SEED = 145_310_001
STRUCTURAL_MLP_SEED = 145_310_002


def generated_he_mlp(seed: int) -> MLP:
    """Create one weights-only structural MLP; deliberately no truth exists."""

    rng = np.random.default_rng(int(seed))
    scale = np.float32(math.sqrt(2.0 / 256.0))
    weights = [
        fnp.asarray(
            rng.standard_normal((256, 256), dtype=np.float32) * scale,
            dtype=fnp.float32,
        )
        for _ in range(32)
    ]
    mlp = MLP(
        width=256,
        depth=32,
        weights=weights,
        seed=int(seed),
        name="m153-structural-only",
    )
    mlp.validate()
    return mlp


def sha256_array(value) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    return hashlib.sha256(memoryview(array).cast("B")).hexdigest()


def trace_one(estimator, mlp: MLP) -> dict:
    estimator.setup(
        SetupContext(
            width=256,
            depth=32,
            flop_budget=10**15,
            api_version="m153-structural-only",
            seed=SETUP_SEED,
        )
    )
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    with budget:
        prediction = np.asarray(estimator.predict(mlp, 10**15)).copy()
    wall = time.perf_counter() - started
    dispatch = list(estimator.dispatch_trace)
    return {
        "billed_flops": int(budget.flops_used),
        "backend_s": float(budget.flopscope_backend_time_s),
        "overhead_s": float(budget.flopscope_overhead_time_s),
        "residual_s": float(budget.residual_wall_time_s or 0.0),
        "wall_s": float(wall),
        "effective_compute": int(budget.flops_used)
        + 1e11 * float(budget.residual_wall_time_s or 0.0),
        "prediction_sha256": sha256_array(prediction),
        "prediction_finite": bool(np.isfinite(prediction).all()),
        "frame_bank_sha256": sha256_array(estimator.frame_bank),
        "dispatch_records": dispatch,
        "matmul_dispatch_calls": int(
            sum(int(row["matmul_calls"]) for row in dispatch)
        ),
        "flopscope_matmul_calls": int(
            budget.summary_dict()["operations"]["matmul"]["calls"]
        ),
        "transport": estimator.last_transport,
        "event_log": estimator.event_log,
        "pilot_reuse_trace": list(
            getattr(estimator, "pilot_reuse_trace", [])
        ),
    }


def main() -> None:
    mlp = generated_he_mlp(STRUCTURAL_MLP_SEED)
    baseline = trace_one(Estimator(), mlp)
    reused = trace_one(PrefixReuseEstimator(), mlp)

    baseline_rows = {row["stage"]: row for row in baseline["dispatch_records"]}
    reused_stages = {row["stage"] for row in reused["dispatch_records"]}
    removed = [
        baseline_rows[stage]
        for stage in reused["pilot_reuse_trace"]
        if stage in baseline_rows and stage not in reused_stages
    ]
    assertions = {
        "prediction_bitwise_equal": (
            baseline["prediction_sha256"] == reused["prediction_sha256"]
        ),
        "proposal_bitwise_equal": baseline["transport"] == reused["transport"],
        "restored_bank_bitwise_equal": (
            baseline["frame_bank_sha256"] == reused["frame_bank_sha256"]
        ),
        "full_pilot_stage_list_equal": [
            row["stage"]
            for row in baseline["dispatch_records"]
            if row["stage"].startswith("pilot_surrogate:")
        ]
        == [
            row["stage"]
            for row in reused["dispatch_records"]
            if row["stage"].startswith("pilot_surrogate:")
        ],
        "formal_layer4_dispatched_normally": "formal:layer4:pilot" in reused_stages,
        "only_three_formal_dispatches_removed": (
            baseline["matmul_dispatch_calls"]
            - reused["matmul_dispatch_calls"]
            == 3
        ),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    result = {
        "status": "M153_STRUCTURAL_PREFIX_REUSE_PASS_NO_EFFICACY",
        "firewall": (
            "one generated weights-only MLP; no truth, labels, reference, MSE, "
            "score, leaderboard, submission, or champion source was opened"
        ),
        "runtime": {
            "flopscope": getattr(flops, "__version__", "unknown"),
            "numpy": np.__version__,
        },
        "seeds": {"setup": SETUP_SEED, "structural_mlp": STRUCTURAL_MLP_SEED},
        "baseline": baseline,
        "prefix_reuse": reused,
        "assertions": assertions,
        "removed_formal_dispatches": removed,
        "removed_shape_bill": int(sum(int(row["shape_bill"]) for row in removed)),
        "billed_flop_delta": int(
            baseline["billed_flops"] - reused["billed_flops"]
        ),
        "dispatch_call_delta": int(
            baseline["matmul_dispatch_calls"]
            - reused["matmul_dispatch_calls"]
        ),
        "cache_bytes": {
            "first_preactivation": 1024 * 256 * 4,
            "dense_activation_layer2": 2048 * 256 * 4,
            "dense_activation_layer3": 2048 * 256 * 4,
            "total_retained_before_formal_entry": 5 * 1024 * 1024,
            "dense_activation_peak": 3 * 2048 * 256 * 4,
            "baseline_dense_activation_peak": 2048 * 256 * 4,
            "additional_activation_bytes_vs_m145": 2 * 2048 * 256 * 4,
            "maximum_additional_bytes_vs_m145": 5 * 1024 * 1024,
        },
        "disposition": (
            "conditional all-active prefix only; no generic dense-column "
            "reuse after the first reduced Formal active set"
        ),
    }
    output = HERE / "M153_PILOT_PREFIX_REUSE_STRUCTURAL_TRACE_20260807.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output": str(output),
        "billed_flop_delta": result["billed_flop_delta"],
        "dispatch_call_delta": result["dispatch_call_delta"],
        "removed_shape_bill": result["removed_shape_bill"],
        "residual_delta_s": baseline["residual_s"] - reused["residual_s"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
