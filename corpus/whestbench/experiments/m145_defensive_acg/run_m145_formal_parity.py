"""Truth-free parity between immutable Formal L1 and the split comparator."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP


HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent / "row_blocked_production" / "candidate_source"
if str(FORMAL) not in sys.path:
    sys.path.insert(0, str(FORMAL))

from estimator import Estimator as FormalL1  # noqa: E402
from m145_integrated_estimator import (  # noqa: E402
    MatchedComparator,
    raw_qr_radius_bank_numpy,
)


SETUP_SEED = 145_310_001
MLP_SEED = 145_310_002


def generated_he_mlp(seed: int) -> MLP:
    rng = np.random.default_rng(seed)
    scale = np.float32(math.sqrt(2.0 / 256.0))
    weights = [
        fnp.asarray(
            rng.standard_normal((256, 256), dtype=np.float32) * scale,
            dtype=fnp.float32,
        )
        for _ in range(32)
    ]
    return MLP(256, 32, weights, seed=seed, name="m145-parity-no-truth")


def digest(x: np.ndarray) -> str:
    a = np.ascontiguousarray(x)
    return hashlib.sha256(memoryview(a).cast("B")).hexdigest()


def run(estimator, mlp) -> tuple[np.ndarray, dict]:
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    with budget:
        prediction = estimator.predict(mlp, 10**15)
    return np.asarray(prediction).copy(), {
        "billed_flops": int(budget.flops_used),
        "residual_s": float(budget.residual_wall_time_s or 0.0),
        "matmul_calls": int(
            budget.summary_dict()["operations"]["matmul"]["calls"]
        ),
    }


def main() -> None:
    context = SetupContext(
        width=256,
        depth=32,
        flop_budget=10**15,
        api_version="synthetic-structural-only",
        seed=SETUP_SEED,
    )
    bank = raw_qr_radius_bank_numpy(SETUP_SEED)
    mlp = generated_he_mlp(MLP_SEED)

    formal = FormalL1()
    formal.setup(context)
    # Only geometry is replaced; every immutable pruning/fold/tangent hook is
    # executed unchanged.  This is a parity test, never a score comparison.
    formal._gaussian = fnp.asarray(
        bank.reshape((126 * 256, 256)), dtype=fnp.float32
    )
    formal_prediction, formal_trace = run(formal, mlp)

    comparator = MatchedComparator()
    comparator.setup(context)
    comparator_prediction, comparator_trace = run(comparator, mlp)
    difference = comparator_prediction - formal_prediction
    scale = max(float(np.max(np.abs(formal_prediction))), 1e-12)
    result = {
        "status": "TRUTH_FREE_FORMAL_L1_PARITY_ONLY",
        "firewall": (
            "same generated MLP and provisional bank; no truth, MSE, score, "
            "competition row, API, submission, or champion mutation"
        ),
        "setup_seed": SETUP_SEED,
        "mlp_seed": MLP_SEED,
        "provisional_bank_sha256": digest(bank),
        "formal_prediction_sha256": digest(formal_prediction),
        "split_prediction_sha256": digest(comparator_prediction),
        "max_abs_difference": float(np.max(np.abs(difference))),
        "rms_difference": float(np.sqrt(np.mean(difference * difference))),
        "max_relative_to_output_scale": float(
            np.max(np.abs(difference)) / scale
        ),
        "both_finite": bool(
            np.isfinite(formal_prediction).all()
            and np.isfinite(comparator_prediction).all()
        ),
        "formal_trace": formal_trace,
        "split_trace": comparator_trace,
        "split_event_log": comparator.event_log,
    }
    (HERE / "M145_FORMAL_PARITY_20260807.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

