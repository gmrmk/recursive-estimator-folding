"""D - the honest end-to-end adjusted score under deeper Strassen-Winograd.

Inputs, all measured or derived here (nothing assumed):
  * cost law + per-MLP decomposition  -> a_cost_law.json  (cached artifact)
  * per-product flops AND residual    -> b_meter_residual.json (metered)
  * irreducible per-call residual floor -> c_residual_floor.json (metered)

Baseline is the CHAMPION'S ACTUAL KERNEL (frozen RowBlockedBatchedWinograd,
already depth-1), not the direct product. Deeper recursion is an INCREMENT on
depth 1, which is what the deployed entry actually pays today.

Also carries an exact-Fraction closed form as an independent second signal on
the FLOP side.
"""
from __future__ import annotations

import json
import os
import statistics
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
LAMBDA = 1e11
SHAPE = "64512x256@256x256"
M, K, N = 64512, 256, 256
F_ELIG = 0.574164   # measured, INTEGRATED_BATCHED_WINOGRAD_REPORT.md
N_ELIG_HOOKS = 16   # measured, same report (16 of 29 hook shapes dispatched)

load = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
A = load("a_cost_law.json")
Bm = load("b_meter_residual.json")["shapes"][SHAPE]
Cf = load("c_residual_floor.json")

art = os.path.join(HERE, "..", "t4_kerdock_descriptive_rescore",
                   "kerdock_v3_official100.json")
doc = json.load(open(art, encoding="utf-8-sig"))
per = doc["results"]["per_mlp"]
BUD = float(doc["run_config"]["flop_budget"])

out = {}

# ---------------------------------------------------------------- 1. closed form
def closed(d, a, b, c):
    d = int(d)
    mm = Fraction(7, 8) ** d * 2 * M * K * N - Fraction(7, 4) ** d * M * N
    mv = Fraction(a * M * K + b * K * N + c * M * N, 3) * (Fraction(7, 4) ** d - 1)
    return mm + mv

cf = {}
for d in range(0, 6):
    v = closed(d, 4, 4, 7)
    assert v.denominator == 1, (d, v)
    cf[f"d{d}"] = int(v)
out["closed_form_V1_floor"] = cf
out["closed_form_vs_metered"] = {
    f"d{d}": {
        "closed": cf[f"d{d}"],
        "metered": Bm[f"sw_d{d}"]["flops"] if d else Bm["d0_direct"]["flops"],
        "match": cf[f"d{d}"] == (Bm[f"sw_d{d}"]["flops"] if d else Bm["d0_direct"]["flops"]),
    }
    for d in range(0, 5)
}
# champion depth-1 kernel is the (7,7,7) schedule
out["champion_kernel_schedule_check"] = {
    "closed_form_a=b=c=7_d1": int(closed(1, 7, 7, 7)),
    "metered_frozen_kernel": Bm["champ_d1_rowblocked"]["flops"],
    "match": int(closed(1, 7, 7, 7)) == Bm["champ_d1_rowblocked"]["flops"],
}
out["uf1_table_discrepancy"] = {
    "uf1_d3": 5840555008, "ours_closed_and_metered_d3": cf["d3"],
    "delta_d3": 5840555008 - cf["d3"],
    "uf1_d4": 5309760256, "ours_closed_and_metered_d4": cf["d4"],
    "delta_d4": 5309760256 - cf["d4"],
    "note": "immaterial (<=1e-5 relative) but the UF1 absolute d3/d4 cells do "
            "not equal their own closed form; d1/d2 do.",
}

# ------------------------------------------- 2. eligible share of the billed lane
rho = Fraction(7 * (M // 2) * (N // 2) * (2 * (K // 2) - 1),
               M * N * (2 * K - 1))            # depth-1 matmul-only ratio
rho_f = float(rho)
lane_coeff = (1 - F_ELIG) + F_ELIG * rho_f     # billed lane / direct-equiv lane
elig_share_of_lane = F_ELIG * rho_f / lane_coeff
FULL_HOOK_MATMUL = 7 * (M // 2) * (N // 2) * (2 * (K // 2) - 1)
out["eligibility_reconstruction"] = {
    "f_eligible_of_direct_bill": F_ELIG,
    "depth1_matmul_only_ratio_rho": rho_f,
    "billed_lane_over_direct_equiv": lane_coeff,
    "eligible_share_of_BILLED_matmul_lane": elig_share_of_lane,
    "full_width_hook_matmul_flops": FULL_HOOK_MATMUL,
    "cross_check_audit_selected_over_direct": {
        "predicted_matmul_only": lane_coeff,
        "audit_measured_incl_movement": 150.926304319 / 161.964214272,
    },
}

# -------------------------------------------------- 3. per-product deltas, metered
base = Bm["champ_d1_rowblocked"]
arms = {}
for d in (1, 2, 3, 4):
    a = Bm[f"sw_d{d}"]
    dfl = a["flops"] - base["flops"]
    drs = a["residual_s_median"] - base["residual_s_median"]
    # floor variant: perfect implementation at every depth, floor baseline d1
    fl_d = Cf["irreducible_floor_per_product"][f"d{d}"]["min_residual_s_floor"]
    fl_1 = Cf["irreducible_floor_per_product"]["d1"]["min_residual_s_floor"]
    dfl_fl = a["flops"] - Bm["sw_d1"]["flops"]
    arms[f"d{d}"] = {
        "flops": a["flops"],
        "d_flops_vs_champ_d1": dfl,
        "d_residual_s_vs_champ_d1": drs,
        "d_residual_charge": drs * LAMBDA,
        "net_d_effective_per_hook_MEASURED": dfl + drs * LAMBDA,
        "net_d_effective_per_hook_FLOOR": dfl_fl + (fl_d - fl_1) * LAMBDA,
        "matmul_calls": a["matmul_calls"],
        "rel_fro": a["rel_fro"],
        "wall_s": a["wall_s_median"],
    }
out["per_hook_deltas"] = arms

# ------------------------------------ 4. INTEGRATED per-MLP rescore (cached run)
def rescore(dkey, resid_hooks_mode, floor=False):
    rows = []
    for m in per:
        ops = m["breakdowns"]["estimator"]["by_namespace"][
            "estimator.estimator-client"]["operations"]
        L = ops["matmul"]["flop_cost"]
        elig = elig_share_of_lane * L
        H = elig / FULL_HOOK_MATMUL          # full-width-equivalent hooks
        a = arms[dkey]
        dfl = a["net_d_effective_per_hook_FLOOR" if floor else
               "net_d_effective_per_hook_MEASURED"]
        # split back into flop and residual parts for exact per-MLP bookkeeping
        if floor:
            fl_d = Cf["irreducible_floor_per_product"][dkey]["min_residual_s_floor"]
            fl_1 = Cf["irreducible_floor_per_product"]["d1"]["min_residual_s_floor"]
            d_flops = Bm[f"sw_{dkey}"]["flops"] - Bm["sw_d1"]["flops"]
            d_res = fl_d - fl_1
        else:
            d_flops = a["d_flops_vs_champ_d1"]
            d_res = a["d_residual_s_vs_champ_d1"]
        n_res = H if resid_hooks_mode == "equiv" else N_ELIG_HOOKS
        new_flops = m["flops_used"] + H * d_flops
        new_res = m["residual_wall_time_s"] + n_res * d_res
        new_eff = new_flops + new_res * LAMBDA
        rows.append(m["final_layer_mse"] * max(0.1, new_eff / BUD))
    return statistics.fmean(rows)

base_score = doc["results"]["adjusted_final_layer_score"]
integrated = {}
for dkey in ("d1", "d2", "d3", "d4"):
    for mode in ("equiv", "16hooks"):
        for floor in (False, True):
            s = rescore(dkey, mode, floor)
            integrated[f"{dkey}|{mode}|{'floor' if floor else 'measured'}"] = {
                "score": s, "gain_vs_champion": base_score / s,
            }
out["integrated_rescore_cached_100mlp"] = {
    "champion_score": base_score, "arms": integrated,
}

# ------------------------------- 5. translation onto the stated champion headline
C_CH, CB_CH, ADJ_CH = 1.7683e11, 0.650, 1.832e-7
B_CH = C_CH / CB_CH
rawmse = ADJ_CH / max(0.1, CB_CH)
res_share = A["decomposition"]["mean_residual_charge_share_of_mean_eff"]
mm_share = A["decomposition"]["mean_matmul_share_of_flops"]
C_res = res_share * C_CH
C_flops = C_CH - C_res
L_ch = mm_share * C_flops
H_ch = elig_share_of_lane * L_ch / FULL_HOOK_MATMUL
head = {
    "B": B_CH, "raw_mse": rawmse,
    "C_split_residual_charge": C_res, "C_split_residual_s": C_res / LAMBDA,
    "C_split_flops": C_flops, "matmul_lane": L_ch,
    "eligible_full_width_hooks_H": H_ch,
    "uf1_claim_d4": {"r": 0.629184, "elig": 0.574164,
                     "saved": (1 - 0.629184) * 145.138e9 * 0.574164},
}
tbl = {}
for dkey in ("d1", "d2", "d3", "d4"):
    a = arms[dkey]
    for mode, nres in (("equiv", H_ch), ("16hooks", float(N_ELIG_HOOKS))):
        dC = H_ch * a["d_flops_vs_champ_d1"] + nres * a["d_residual_charge"]
        Cn = C_CH + dC
        tbl[f"{dkey}|{mode}"] = {
            "delta_flops": H_ch * a["d_flops_vs_champ_d1"],
            "delta_residual_charge": nres * a["d_residual_charge"],
            "delta_C": dC, "C_new": Cn, "C_over_B": Cn / B_CH,
            "score": rawmse * max(0.1, Cn / B_CH),
            "gain": ADJ_CH / (rawmse * max(0.1, Cn / B_CH)),
        }
    # FLOP-only counterfactual (what U-F1 reports): ignore residual entirely
    dCf_ = H_ch * a["d_flops_vs_champ_d1"]
    tbl[f"{dkey}|FLOPONLY"] = {
        "delta_C": dCf_, "C_new": C_CH + dCf_,
        "gain": ADJ_CH / (rawmse * max(0.1, (C_CH + dCf_) / B_CH)),
    }
head["table"] = tbl
out["champion_headline_translation"] = head

with open(os.path.join(HERE, "d_integrated_score.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
print(json.dumps(out, indent=2))
