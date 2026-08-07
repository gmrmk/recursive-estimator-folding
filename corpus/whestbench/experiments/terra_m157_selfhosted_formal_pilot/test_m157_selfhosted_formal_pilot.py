"""Truth-free structural contract for M157 self-hosted Formal-pilot reuse."""

from __future__ import annotations

import math
from pathlib import Path
import sys

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


def _generated_he_mlp(seed: int) -> MLP:
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


def test_self_hosted_formal_pilot_freezes_q1_before_main_and_reuses_q0_state() -> None:
    """The Formal q0 state replaces dense pilot work; no truth is constructed."""

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
    initial_bank = np.asarray(estimator.frame_bank).copy()
    mlp = _generated_he_mlp(STRUCTURAL_MLP_SEED)
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0)
    with budget:
        prediction = np.asarray(estimator.predict(mlp, 10**15)).copy()

    assert prediction.shape == (32, 256)
    assert np.isfinite(prediction).all()
    assert np.array_equal(initial_bank, np.asarray(estimator.frame_bank))
    assert estimator.event_log == [
        "formal_q0_pilot_materialized",
        "proposal_frozen_from_formal_q0_only",
        "main_transport_applied_after_proposal",
        "formal_main_with_cached_q0_entered",
        "formal_main_with_cached_q0_complete",
        "main_transport_restored_and_canonicalized",
    ]
    assert estimator.last_transport["proposal_source"] == "formal_kink_even_q0"
    assert estimator.last_transport["bad_weight_count"] == 0
    assert 0.0 < estimator.last_transport["weight_min"] <= estimator.last_transport["weight_max"] <= 1.25
    assert estimator.reuse_summary["dense_proposal_pilot_dispatches"] == 0
    assert estimator.reuse_summary["cached_q0_reused_after_proposal"] is True
    assert estimator.reuse_summary["formal_q0_dispatches"] > 0
    assert all(
        not row["stage"].startswith("pilot_surrogate:")
        for row in estimator.dispatch_trace
    )


if __name__ == "__main__":
    test_self_hosted_formal_pilot_freezes_q1_before_main_and_reuses_q0_state()
