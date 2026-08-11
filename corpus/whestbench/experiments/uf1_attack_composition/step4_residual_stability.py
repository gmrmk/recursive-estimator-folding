"""STEP 4 -- interleaved residual measurement with a bootstrap CI.

The scorer charges residual wall, not backend wall
(COMPRESSION_SCORE_CALCULUS_20260806.md).  The conversion rate is DERIVED
from two committed rows of INTEGRATED_BATCHED_WINOGRAD_REPORT.md and equals
1.0e11 effective FLOPs per residual second to 5.0e-6 relative.

Arms are interleaved round-robin so machine drift hits every arm equally.
Reports median delta and a 95% percentile bootstrap CI on the paired delta.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import flopscope as fl
import flopscope.numpy as fnp

FROZEN = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
    r"\corpus\whestbench\experiments\v31_guards\package_source"
)
sys.path.insert(0, str(FROZEN))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd  # noqa
from step2_composed_depth_kernel import RowBlockedDepthStrassen  # noqa

BUDGET = 10**18
M = K = N = None
RATE = 1.0e11
ROUNDS = 9


def workspace_single_row_size(depth, blk, width=256):
    """Frozen-style single-block-height workspace, in MiB (no direct scratch).

    Matches the DERIVED column of core/CODEX_HANDOFF_20260810.md so the two
    are directly comparable.
    """
    total = 0
    for j in range(1, depth + 1):
        total += 7 ** j * (blk >> j) * (width >> j) * 4      # left
        total += 7 ** j * (blk >> j) * (width >> j) * 4      # products
        total += 7 ** j * (width >> j) * (width >> j) * 4    # right
    return total / 1048576


def main():
    M, K, N = 64512, 256, 256
    rng = np.random.default_rng(20260810)
    a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
    b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
    fa, fb = fnp.asarray(a), fnp.asarray(b)
    out_buf = fnp.empty((M, N), dtype=fnp.float32)

    arms = {"production_d1_frozen": lambda: RowBlockedBatchedWinograd(M, N, BLOCK_ROWS)}
    for d, blk in [(2, 4096), (3, 4096), (4, 4096), (5, 4096), (4, 1024)]:
        arms[f"d{d}_block{blk}"] = (
            lambda d=d, blk=blk: RowBlockedDepthStrassen(M, N, d, blk))

    ops = {}
    for name, ctor in arms.items():
        with fl.BudgetContext(flop_budget=BUDGET, quiet=True):
            ops[name] = ctor()

    samples = {name: [] for name in arms}
    flops = {}
    for rnd in range(ROUNDS):
        for name in arms:
            with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
                ops[name].multiply(fa, fb, out=out_buf)
                s = bud.summary_dict()
            samples[name].append(float(s["residual_wall_time_s"]))
            flops[name] = int(s["flops_used"])
        print("round", rnd, {k: round(v[-1] * 1e3, 3) for k, v in samples.items()},
              flush=True)

    base = np.asarray(samples["production_d1_frozen"])
    result = {"rounds": ROUNDS, "residual_rate_flops_per_s": RATE,
              "production_flops": flops["production_d1_frozen"],
              "production_residual_ms_median": float(np.median(base) * 1e3),
              "production_residual_ms_all": [round(x * 1e3, 4) for x in base],
              "arms": {}}
    boot = np.random.default_rng(11)
    for name in arms:
        if name == "production_d1_frozen":
            continue
        arm = np.asarray(samples[name])
        delta = arm - base                    # paired, same round
        idx = boot.integers(0, len(delta), size=(20000, len(delta)))
        means = delta[idx].mean(axis=1)
        lo, hi = np.percentile(means, [2.5, 97.5])
        saved = flops["production_d1_frozen"] - flops[name]
        d, blk = int(name[1]), int(name.split("block")[1])
        result["arms"][name] = {
            "flops": flops[name],
            "billed_flops_saved_vs_production": saved,
            "residual_ms_median": float(np.median(arm) * 1e3),
            "paired_delta_residual_ms_mean": float(delta.mean() * 1e3),
            "paired_delta_residual_ms_ci95": [float(lo * 1e3), float(hi * 1e3)],
            "residual_charged_effective_flops_mean": float(delta.mean() * RATE),
            "residual_charged_effective_flops_ci95":
                [float(lo * RATE), float(hi * RATE)],
            "NET_effective_saving_mean": float(saved - delta.mean() * RATE),
            "NET_effective_saving_ci95":
                [float(saved - hi * RATE), float(saved - lo * RATE)],
            "net_is_positive_at_95ci_low": bool(saved - hi * RATE > 0),
            "workspace_MiB_single_block_height":
                workspace_single_row_size(d, blk),
        }
    result["production_workspace_MiB_single_block_height"] = (
        (7 * 2048 * 128 * 4 * 2 + 7 * 128 * 128 * 4) / 1048576)
    (HERE / "step4_residual_stability.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["arms"], indent=2))
    print("production workspace MiB",
          result["production_workspace_MiB_single_block_height"])


if __name__ == "__main__":
    main()
