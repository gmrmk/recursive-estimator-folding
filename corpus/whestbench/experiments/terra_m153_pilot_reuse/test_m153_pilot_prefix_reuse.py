"""Truth-free regression for the M153 all-active pilot-prefix reuse only."""

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

from m145_integrated_estimator import Estimator  # noqa: E402
from m153_pilot_prefix_reuse import PrefixReuseEstimator  # noqa: E402


SETUP_SEED = 145_310_001
STRUCTURAL_MLP_SEED = 145_310_002


def _generated_he_mlp(seed: int) -> MLP:
    """Make the predeclared structural-only MLP; no truth or score exists."""

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


def _run(estimator, mlp: MLP) -> tuple[np.ndarray, int, int]:
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
    with budget:
        prediction = np.asarray(estimator.predict(mlp, 10**15)).copy()
    calls = sum(int(row["matmul_calls"]) for row in estimator.dispatch_trace)
    return prediction, int(budget.flops_used), calls


def test_all_active_prefix_reuse_is_bitwise_and_fails_closed_at_first_pruning() -> None:
    """Only same-shape all-active states may replace Formal pilot products."""

    mlp = _generated_he_mlp(STRUCTURAL_MLP_SEED)
    base = Estimator()
    reused = PrefixReuseEstimator()

    base_prediction, base_bill, base_calls = _run(base, mlp)
    reused_prediction, reused_bill, reused_calls = _run(reused, mlp)

    # Proposal, full output, and restoration stay coupled exactly.  This does
    # not construct a truth vector, an error, or an efficacy statistic.
    assert np.array_equal(base_prediction, reused_prediction)
    assert base.last_transport == reused.last_transport
    assert np.array_equal(np.asarray(base.frame_bank), np.asarray(reused.frame_bank))

    # The target-shaped trace has a full 256-wide prefix through Formal layer
    # 3; layer 4 is 253-wide and must dispatch normally rather than reuse a
    # mathematically similar but differently rounded dense result.
    assert reused.pilot_reuse_trace == [
        "formal:first:pilot",
        "formal:layer2:pilot",
        "formal:layer3:pilot",
    ]
    assert any(
        row["stage"] == "formal:layer4:pilot" for row in reused.dispatch_trace
    )
    assert reused_calls == base_calls - 3
    assert reused_bill < base_bill


def test_reduced_formal_width_releases_unusable_dense_cache_and_dispatches() -> None:
    """A 253-wide Formal product is never replaced by a dense 256-wide one."""

    estimator = PrefixReuseEstimator()
    estimator.setup(
        SetupContext(
            width=256,
            depth=32,
            flop_budget=10**15,
            api_version="m153-reduced-width-structural-only",
            seed=SETUP_SEED,
        )
    )
    estimator._m153_dense_x2 = fnp.ones((2048, 256), dtype=fnp.float32)
    estimator._m153_dense_x3 = fnp.ones((2048, 256), dtype=fnp.float32)
    left = fnp.zeros((2048, 256), dtype=fnp.float32)
    reduced_right = fnp.zeros((256, 253), dtype=fnp.float32)

    with flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=120.0):
        product = estimator._pilot_mm("formal:layer2:pilot", left, reduced_right)

    assert product.shape == (2048, 253)
    assert estimator.pilot_reuse_trace == []
    assert estimator._m153_dense_x2 is None
    assert estimator._m153_dense_x3 is None
    assert estimator.dispatch_trace[-1]["stage"] == "formal:layer2:pilot"


if __name__ == "__main__":
    test_all_active_prefix_reuse_is_bitwise_and_fails_closed_at_first_pruning()
    test_reduced_formal_width_releases_unusable_dense_cache_and_dispatches()
