"""STEP-0 ARITHMETIC KILL GATE for gm_s17_reuse.

Re-derive S17's section-A per-net sigma^2 / floor / ratio numbers from the
committed S5 arrays + the committed S16/m181 champion MSEs, and compare
bitwise-ish (rel err < 1e-12) against the committed s17_results.json.

KILL: any of the three ratio_champ_over_costfloor fails to reproduce ->
the mined instrument is not the object in the record -> stop.

Read-only everywhere except this directory.
"""
from __future__ import annotations
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
S5 = os.path.join(EXP, "s5_kink_concentration")
S17 = os.path.join(EXP, "s17_ibc_floor")

N_BASE, N_FULL = 32256, 64512
CHAMP = {"101": 1.9971942916463923e-07,
         "202": 5.872086598611009e-07,
         "303": 2.3692484273379475e-07}

ref = json.load(open(os.path.join(S17, "s17_results.json")))

out = {"gate": "step0_reproduce_s17_sectionA", "per_net": {}, "checks": {}}
ratios = []
for net in ("101", "202", "303"):
    d = np.load(os.path.join(S5, "s5_net%s_arrays.npz" % net))
    yb = d["ybar"].astype(np.float64)
    assert yb.shape == (N_FULL,), yb.shape
    sig2_a = yb.var()                      # S17 signal 1
    sig2_b = np.mean(d["r_global"] ** 2)   # S17 signal 2 (independent array)
    ch = CHAMP[net]
    floor_full = sig2_a / N_FULL
    floor_base = sig2_a / N_BASE
    r_cost = ch / floor_full
    r_dir = ch / floor_base
    rn = ref["A_per_net"][net]
    rec = {
        "sigma2_var(ybar)": sig2_a,
        "sigma2_mean(r_global^2)": sig2_b,
        "sigma2_two_way_rel_diff": abs(sig2_a - sig2_b) / sig2_a,
        "iid_floor_sigma2_over_64512": floor_full,
        "dir_floor_sigma2_over_32256": floor_base,
        "ratio_champ_over_costfloor": r_cost,
        "ratio_champ_over_dirfloor": r_dir,
        "N_eff_sigma2_over_champ": sig2_a / ch,
        "ref_ratio_champ_over_costfloor": rn["ratio_champ_over_costfloor"],
        "rel_err_ratio_costfloor": abs(r_cost - rn["ratio_champ_over_costfloor"])
                                   / rn["ratio_champ_over_costfloor"],
        "rel_err_sigma2": abs(sig2_a - rn["sigma2_var(ybar)"]) / rn["sigma2_var(ybar)"],
        "bitwise_sigma2": bool(sig2_a == rn["sigma2_var(ybar)"]),
        "bitwise_ratio": bool(r_cost == rn["ratio_champ_over_costfloor"]),
    }
    out["per_net"][net] = rec
    ratios.append(r_cost)

a = np.array(ratios)
m, s = float(a.mean()), float(a.std(ddof=1))
se = s / np.sqrt(len(a))
out["pooled_reproduced"] = {"mean": m, "sd": s, "se": se,
                            "t95_ci": [m - 4.303 * se, m + 4.303 * se]}
out["pooled_reference"] = ref["A_pooled"]["ratio_champ_over_costfloor(sigma2/64512)"]
out["rel_err_pooled"] = abs(m - out["pooled_reference"]["mean"]) / out["pooled_reference"]["mean"]

worst = max(v["rel_err_ratio_costfloor"] for v in out["per_net"].values())
out["checks"]["worst_rel_err_ratio"] = worst
out["checks"]["all_bitwise"] = bool(all(v["bitwise_ratio"] for v in out["per_net"].values()))
out["verdict"] = "STEP0_PASS" if worst < 1e-12 else "STEP0_KILL"

with open(os.path.join(HERE, "step0_results.json"), "w") as fh:
    json.dump(out, fh, indent=2)

for n, v in out["per_net"].items():
    print("net %s sigma2=%.16e ratio=%.16f ref=%.16f relerr=%.2e bitwise=%s"
          % (n, v["sigma2_var(ybar)"], v["ratio_champ_over_costfloor"],
             v["ref_ratio_champ_over_costfloor"], v["rel_err_ratio_costfloor"],
             v["bitwise_ratio"]))
print("pooled reproduced %.16f  reference %.16f  relerr %.2e"
      % (m, out["pooled_reference"]["mean"], out["rel_err_pooled"]))
print("VERDICT:", out["verdict"], " worst rel err %.2e" % worst,
      " all bitwise:", out["checks"]["all_bitwise"])
