"""E - attack on my own kill: is the residual rate machine-specific?

Counter-hypothesis: "your box is slow; on the grading host residual per
flopscope call is far lower and depth 4 wins."

Test: express the whole result as a BREAK-EVEN residual rate (microseconds of
residual per flopscope call) and compare it against every independently
measured rate available, including the single most Strassen-favourable number
our corpus has ever recorded -- the full-entry batched-Winograd audit
(INTEGRATED_BATCHED_WINOGRAD_REPORT.md), which measured the residual penalty
of converting 16 real hooks to depth-1 Winograd on a real 29-hook predict.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LAMBDA = 1e11
load = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
Bm = load("b_meter_residual.json")["shapes"]["64512x256@256x256"]
Cf = load("c_residual_floor.json")

# --- call counts, exactly ------------------------------------------------
# champion frozen kernel at M=64512, BLOCK_ROWS=4096 -> 16 row blocks:
#   right pack 7 ops (once) + per block (3 copyto + 4 subtract + 1 matmul + 7 add)
CHAMP_CALLS = 7 + 16 * 15
def sw_calls(d):
    nodes = (7 ** d - 1) // 6
    return 15 * nodes + 7 ** d

# --- independently measured residual rates -------------------------------
# 1. corpus full-entry audit: parent 29 direct hooks residual 0.159546 s;
#    child 16 depth-1 batched Winograd + 13 direct, residual 0.160284 s.
#    Extra flopscope calls in the child = 16 * (15 + 1 - 1) = 240.
AUDIT_DELTA_S = 0.160284 - 0.159546
AUDIT_EXTRA_CALLS = 16 * 15
audit_us = AUDIT_DELTA_S / AUDIT_EXTRA_CALLS * 1e6

# 2. this session, bare-loop floor (no Python structure at all)
ew_us = Cf["cheapest_elementwise_us_per_call"]
mm_us = Cf["cheapest_matmul_us_per_call"]

# 3. this session, my real recursive kernel
mine = {}
for d in (1, 2, 3, 4):
    mine[d] = Bm[f"sw_d{d}"]["residual_s_median"] / sw_calls(d) * 1e6
champ_us = Bm["champ_d1_rowblocked"]["residual_s_median"] / CHAMP_CALLS * 1e6

out = {
    "call_counts": {"champion_d1_rowblocked": CHAMP_CALLS,
                    **{f"sw_d{d}": sw_calls(d) for d in (1, 2, 3, 4, 5)}},
    "measured_residual_rates_us_per_call": {
        "corpus_full_entry_audit_2026_08_06": audit_us,
        "bare_loop_floor_elementwise": ew_us,
        "bare_loop_floor_matmul": mm_us,
        "this_session_champion_frozen_kernel": champ_us,
        **{f"this_session_sw_d{d}": v for d, v in mine.items()},
    },
    "audit_inputs": {"delta_residual_s": AUDIT_DELTA_S,
                     "extra_calls": AUDIT_EXTRA_CALLS},
}

# --- break-even rate per depth ------------------------------------------
base_flops = Bm["champ_d1_rowblocked"]["flops"]
be = {}
for d in (1, 2, 3, 4, 5):
    fl = Bm[f"sw_d{d}"]["flops"] if d <= 4 else 5000639744  # closed form d5
    d_flops = fl - base_flops                      # negative = saving
    d_calls = sw_calls(d) - CHAMP_CALLS
    budget_s = -d_flops / LAMBDA                   # residual seconds affordable
    be[f"d{d}"] = {
        "flop_saving_vs_champion_d1": -d_flops,
        "extra_flopscope_calls": d_calls,
        "residual_seconds_affordable": budget_s,
        "breakeven_us_per_extra_call": (budget_s / d_calls * 1e6)
        if d_calls > 0 else None,
        "verdict_at_corpus_audit_rate": None,
    }

# --- net effect per hook at each independently measured rate -------------
rates = {
    "corpus_audit_rate": audit_us,
    "bare_loop_floor_blend": None,   # filled per depth (ew/mm mix)
    "this_session_measured": None,   # filled per depth (actual measurement)
}
per_hook = {}
for d in (1, 2, 3, 4, 5):
    fl = Bm[f"sw_d{d}"]["flops"] if d <= 4 else 5000639744
    d_flops = fl - base_flops
    d_calls = sw_calls(d) - CHAMP_CALLS
    nodes = (7 ** d - 1) // 6
    floor_s = (15 * nodes * ew_us + 7 ** d * mm_us) * 1e-6
    champ_floor_s = CHAMP_CALLS * ew_us * 1e-6      # generous: cheapest rate
    entry = {
        "d_flops": d_flops,
        "corpus_audit_rate": {
            "d_residual_s": d_calls * audit_us * 1e-6,
            "net_d_effective": d_flops + d_calls * audit_us * 1e-6 * LAMBDA,
        },
        "bare_loop_floor": {
            "d_residual_s": floor_s - champ_floor_s,
            "net_d_effective": d_flops + (floor_s - champ_floor_s) * LAMBDA,
        },
    }
    if d <= 4:
        drs = (Bm[f"sw_d{d}"]["residual_s_median"]
               - Bm["champ_d1_rowblocked"]["residual_s_median"])
        entry["this_session_measured"] = {
            "d_residual_s": drs, "net_d_effective": d_flops + drs * LAMBDA,
        }
    per_hook[f"d{d}"] = entry
    be[f"d{d}"]["verdict_at_corpus_audit_rate"] = (
        "LOSS" if entry["corpus_audit_rate"]["net_d_effective"] > 0 else "win"
    )

out["breakeven"] = be
out["net_per_hook_at_each_rate"] = per_hook

# --- wall-time consequence ----------------------------------------------
H = 12.264357788050148  # from d_integrated_score.json (champion headline)
out["wall_time_consequence"] = {
    "champion_measured_predict_wall_s_mlp0": 2.752767900001345,
    "eligible_full_width_equivalent_hooks": H,
    **{
        f"d{d}_added_wall_s_per_mlp": H * (
            Bm[f"sw_d{d}"]["wall_s_median"]
            - Bm["champ_d1_rowblocked"]["wall_s_median"])
        for d in (1, 2, 3, 4)
    },
    "d4_projected_predict_wall_s": 2.752767900001345 + H * (
        Bm["sw_d4"]["wall_s_median"] - Bm["champ_d1_rowblocked"]["wall_s_median"]),
    "frozen_campaign_gate_s": 20.0,
    "harness_wall_time_limit_s": 60.0,
}

with open(os.path.join(HERE, "e_breakeven.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
print(json.dumps(out, indent=2))
