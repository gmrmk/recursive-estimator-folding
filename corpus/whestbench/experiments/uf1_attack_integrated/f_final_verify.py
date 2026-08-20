"""F - final verification and the shape-correct irreducible floor.

1. Shape-correct floor: the depth-d tree's elementwise ops live at four
   different block sizes; c_residual_floor.py blended them with the CHEAPEST
   rate. Rebuild the floor using each level's own measured rate.
2. Fresh-process bitwise repeat of the decisive d4 arm (5 reps).
3. The final integrated headline, all arithmetic shown.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "v31_guards",
                                                "package_source")))
LAMBDA = 1e11
load = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
Cf = load("c_residual_floor.json")
Bm = load("b_meter_residual.json")["shapes"]["64512x256@256x256"]

rate = {}
for p in Cf["probes"]:
    rate[(p["op"], tuple(p["shape"])[:2])] = p["residual_us_per_call"]

M, K, N = 64512, 256, 256
out = {}

# ---- 1. shape-correct floor -------------------------------------------
def shape_floor(d):
    ew = 0.0
    for lvl in range(1, d + 1):
        nodes = 7 ** (lvl - 1)
        hm, hk = M >> lvl, K >> lvl
        ew += nodes * 15 * rate[("add", (hm, hk))]
    mm = 7 ** d * rate[("matmul", (M >> d, K >> d))]
    return (ew + mm) * 1e-6

# champion baseline: 247 calls at block (2048,128) / (2048,128)@(128,128).
# Use the cheapest measured elementwise rate as a generous stand-in.
champ_floor_s = 247 * Cf["cheapest_elementwise_us_per_call"] * 1e-6
base_flops = Bm["champ_d1_rowblocked"]["flops"]

tbl = {}
for d in (1, 2, 3, 4):
    f_s = shape_floor(d)
    dfl = Bm[f"sw_d{d}"]["flops"] - base_flops
    dres = f_s - champ_floor_s
    tbl[f"d{d}"] = {
        "shape_correct_floor_residual_s": f_s,
        "champion_floor_residual_s": champ_floor_s,
        "d_residual_s": dres,
        "d_residual_charge": dres * LAMBDA,
        "d_flops": dfl,
        "net_d_effective_per_hook": dfl + dres * LAMBDA,
        "measured_residual_s": Bm[f"sw_d{d}"]["residual_s_median"],
        "measured_over_floor": Bm[f"sw_d{d}"]["residual_s_median"] / f_s,
    }
out["shape_correct_floor"] = tbl

# ---- 2. fresh repeat of the decisive d4 arm ---------------------------
import flopscope
import flopscope.numpy as fnp
import numpy as _np
from b_meter_residual import WS, sw, timed

rng = _np.random.default_rng(424242)
A = fnp.asarray(rng.standard_normal((M, K), dtype=_np.float32))
Bmat = fnp.asarray(rng.standard_normal((K, N), dtype=_np.float32))
C = fnp.empty((M, N), dtype=fnp.float32)
ws = WS(M, K, N, 4)
reps = [timed(lambda: sw(A, Bmat, C, 4, ws, 0)) for _ in range(5)]
fl = {r["flops"] for r in reps}
res = sorted(r["residual"] for r in reps)
out["fresh_repeat_d4"] = {
    "flops": sorted(fl),
    "bitwise_identical_flops": len(fl) == 1,
    "matches_session1": (len(fl) == 1 and fl.pop() == Bm["sw_d4"]["flops"]),
    "residual_s_sorted": res,
    "residual_s_median": res[2],
    "residual_s_min": res[0],
    "session1_residual_s_median": Bm["sw_d4"]["residual_s_median"],
    "eff_at_min_residual": Bm["sw_d4"]["flops"] + res[0] * LAMBDA,
    "direct_product_eff": Bm["d0_direct"]["eff_median"],
    "champion_d1_eff": Bm["champ_d1_rowblocked"]["eff_median"],
}

# ---- 3. final headline -------------------------------------------------
D = load("d_integrated_score.json")
H = D["champion_headline_translation"]["eligible_full_width_hooks_H"]
C_CH, ADJ_CH = 1.7683e11, 1.832e-7
B_CH = C_CH / 0.650
rawmse = ADJ_CH / 0.650

def headline(dkey, dres_s, dflops):
    dC = H * (dflops + dres_s * LAMBDA)
    Cn = C_CH + dC
    s = rawmse * max(0.1, Cn / B_CH)
    return {"delta_C": dC, "C_new": Cn, "C_over_B": Cn / B_CH,
            "score": s, "gain": ADJ_CH / s}

fin = {}
for d in (1, 2, 3, 4):
    dfl = Bm[f"sw_d{d}"]["flops"] - base_flops
    fin[f"d{d}_measured"] = headline(
        d, Bm[f"sw_d{d}"]["residual_s_median"]
        - Bm["champ_d1_rowblocked"]["residual_s_median"], dfl)
    fin[f"d{d}_shape_correct_floor"] = headline(
        d, tbl[f"d{d}"]["d_residual_s"], dfl)
    fin[f"d{d}_flop_only_no_residual"] = headline(d, 0.0, dfl)
out["final_headline"] = {
    "champion_score": ADJ_CH, "B": B_CH, "raw_mse": rawmse,
    "eligible_full_width_hooks_H": H,
    "uf1_claimed_d4_gain": 1.2118,
    "arms": fin,
}

with open(os.path.join(HERE, "f_final_verify.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
print(json.dumps(out, indent=2))
