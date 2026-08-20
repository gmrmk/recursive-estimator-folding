"""Fresh-process, generated-only structural trace for M157."""

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

from m157_selfhosted_formal_pilot import SelfHostedFormalPilotEstimator  # noqa: E402


SETUP_SEED = 145_310_001
STRUCTURAL_MLP_SEED = 145_310_002


def generated_he_mlp(seed: int) -> MLP:
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
        name="m157-structural-only",
    )
    mlp.validate()
    return mlp


def digest(value) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    return hashlib.sha256(memoryview(array).cast("B")).hexdigest()


def one_predict(estimator, mlp) -> dict:
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    started = time.perf_counter()
    with budget:
        prediction = np.asarray(estimator.predict(mlp, 10**15)).copy()
    return {
        "billed_flops": int(budget.flops_used),
        "backend_s": float(budget.flopscope_backend_time_s),
        "overhead_s": float(budget.flopscope_overhead_time_s),
        "residual_s": float(budget.residual_wall_time_s or 0.0),
        "wall_s": float(time.perf_counter() - started),
        "effective_compute": int(budget.flops_used)
        + 1e11 * float(budget.residual_wall_time_s or 0.0),
        "prediction_sha256": digest(prediction),
        "prediction_finite": bool(np.isfinite(prediction).all()),
        "frame_bank_sha256": digest(estimator.frame_bank),
        "dispatch_records": list(estimator.dispatch_trace),
        "matmul_dispatch_calls": int(
            sum(int(row["matmul_calls"]) for row in estimator.dispatch_trace)
        ),
        "flopscope_matmul_calls": int(
            budget.summary_dict()["operations"]["matmul"]["calls"]
        ),
        "event_log": list(estimator.event_log),
        "transport": estimator.last_transport,
        "reuse_summary": estimator.reuse_summary,
    }


def main() -> None:
    estimator = SelfHostedFormalPilotEstimator()
    estimator.setup(
        SetupContext(
            width=256,
            depth=32,
            flop_budget=10**15,
            api_version="m157-structural-only",
            seed=SETUP_SEED,
        )
    )
    initial_bank = digest(estimator.frame_bank)
    mlp = generated_he_mlp(STRUCTURAL_MLP_SEED)
    first = one_predict(estimator, mlp)
    second = one_predict(estimator, mlp)
    assertions = {
        "first_finite": first["prediction_finite"],
        "second_finite": second["prediction_finite"],
        "q0_pilot_precedes_q1_transport": first["event_log"][:3]
        == [
            "formal_q0_pilot_materialized",
            "proposal_frozen_from_formal_q0_only",
            "main_transport_applied_after_proposal",
        ],
        "no_dense_proposal_pilot": not any(
            row["stage"].startswith("pilot_surrogate:")
            for row in first["dispatch_records"]
        ),
        "cached_q0_reused": first["reuse_summary"].get(
            "cached_q0_reused_after_proposal"
        ) is True,
        "restored_after_first": first["frame_bank_sha256"] == initial_bank,
        "restored_after_second": second["frame_bank_sha256"] == initial_bank,
        "repeat_prediction_bitwise_equal": (
            first["prediction_sha256"] == second["prediction_sha256"]
        ),
        "exact_weight_envelope": (
            first["transport"]["bad_weight_count"] == 0
            and 0.0 < first["transport"]["weight_min"]
            <= first["transport"]["weight_max"]
            <= 1.25
        ),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)
    result = {
        "status": "M157_SELF_HOSTED_FORMAL_Q0_STRUCTURAL_PASS_NO_EFFICACY",
        "firewall": (
            "one generated weights-only MLP; no truth, labels, reference, MSE, "
            "score, leaderboard, submission, or champion mutation"
        ),
        "runtime": {
            "flopscope": getattr(flops, "__version__", "unknown"),
            "numpy": np.__version__,
        },
        "seeds": {"setup": SETUP_SEED, "structural_mlp": STRUCTURAL_MLP_SEED},
        "initial_bank_sha256": initial_bank,
        "first_predict": first,
        "second_predict": second,
        "assertions": assertions,
        "dense_pilot_calls_removed_against_m145_trace": 32,
        "dense_pilot_shape_bill_removed_against_m145_trace": 7431323648,
        "disposition": (
            "new pilot-only Formal-kink proposal statistic; structural only, "
            "requires independent causal, memory, and numerical audit"
        ),
    }
    output = HERE / "M157_SELF_HOSTED_FORMAL_STRUCTURAL_TRACE_20260807.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output": str(output),
        "billed_flops": first["billed_flops"],
        "dispatch_calls": first["matmul_dispatch_calls"],
        "removed_dense_pilot_calls": 32,
        "restored": assertions["restored_after_second"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
