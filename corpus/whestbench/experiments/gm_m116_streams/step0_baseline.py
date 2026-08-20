"""STEP 0: recover the pre-L3 baseline bill and print baseline - 189.738221568B.

Kill if delta < 1e9.  Pure arithmetic, no build, no data.

Every input number is quoted from a committed artifact:
  * per-hook schedule bills  -> M116_STREAMED_FUSED_L3_THEORY_20260807.md table
  * frozen geometry          -> m116b campaign_contract.json (64,512 rows, 256, depth 32)
  * L3 depth-32 trace        -> M116B_INDEPENDENT_RESULT_JUDGE_20260807.md
  * champion identity        -> fold_ledger.json row row_blocked_winograd_production
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- frozen geometry (m116b campaign contract) -----------------------------
FULL_ROWS = 64_512
TILE = 256
DEPTH = 32

# --- committed per-hook schedule bills at m = 64,512 (theory doc table) ----
HOOK_DIRECT = 8_439_201_792          # "direct"
HOOK_L1 = 7_427_768_320              # "fused L1 Winograd"  == champion arithmetic
HOOK_L2 = 6_582_603_776              # "fused L2 Winograd"
HOOK_L3 = 5_912_804_352              # "proposed fused L3 Winograd"

# --- the killed row's metered depth-32 trace -------------------------------
L3_FULL_TRACE = 189_738_221_568

RELU_BILL = DEPTH * FULL_ROWS * TILE  # 528,482,304


def independent_direct_hook() -> int:
    """D(m,k,n) = m*n*(2k-1) re-derived, not quoted."""
    return FULL_ROWS * TILE * (2 * TILE - 1)


def independent_l3_hook() -> int:
    """W3 = 343*D(m/8,k/8,n/8) + 651*(mk+kn+mn)/64 re-derived, not quoted."""
    leaf = 343 * (FULL_ROWS // 8) * (TILE // 8) * (2 * (TILE // 8) - 1)
    transforms = 651 * (FULL_ROWS * TILE + TILE * TILE + FULL_ROWS * TILE) // 64
    return leaf + transforms


def full_trace(hook_bill: int) -> int:
    return DEPTH * hook_bill + RELU_BILL


def main() -> None:
    # cross-check 1: the quoted per-hook numbers reproduce from the formulas
    assert independent_direct_hook() == HOOK_DIRECT, independent_direct_hook()
    assert independent_l3_hook() == HOOK_L3, independent_l3_hook()
    # cross-check 2: the killed row's trace reproduces from the hook bill
    assert full_trace(HOOK_L3) == L3_FULL_TRACE, full_trace(HOOK_L3)

    baseline_champion = full_trace(HOOK_L1)   # promoted row_blocked_winograd_production
    baseline_direct = full_trace(HOOK_DIRECT)
    baseline_l2 = full_trace(HOOK_L2)

    delta_champion = baseline_champion - L3_FULL_TRACE
    delta_direct = baseline_direct - L3_FULL_TRACE
    delta_l2 = baseline_l2 - L3_FULL_TRACE

    floor = 1_000_000_000
    verdict = "STEP0_KILL" if delta_champion < floor else "STEP0_CLEAR"

    out = {
        "step": 0,
        "relu_bill": RELU_BILL,
        "l3_full_trace": L3_FULL_TRACE,
        "baseline_pre_l3_champion_L1": baseline_champion,
        "baseline_pre_l3_direct": baseline_direct,
        "baseline_pre_l3_L2": baseline_l2,
        "delta_vs_champion_L1": delta_champion,
        "delta_vs_direct": delta_direct,
        "delta_vs_L2": delta_l2,
        "delta_vs_champion_L1_B": delta_champion / 1e9,
        "relevance_floor": floor,
        "verdict": verdict,
        "residual_excess_charge_of_killed_run_flopeq": int(
            1e11 * (0.6105131132062525 - 0.170)
        ),
        "net_gain_if_residual_unrepaired_flopeq": delta_champion
        - int(1e11 * (0.6105131132062525 - 0.170)),
    }
    print(json.dumps(out, indent=1))
    (HERE / "step0_results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
