"""gm_c1_bound -- supplementary (NOT a gate): is the exclusion-bias direction
supported by data, or only by the max-imputation assumption?

The 3 excluded nets are the 3 highest effective_compute nets (verified in
step0.json). Within the 22 COMPLETED nets, does higher effective_compute go
with a higher adjusted score? A positive association makes max-imputation the
data-supported direction; a null/negative association makes the mined
"R = 1.652 is a lower bound" reading an assumption, not a measurement.

Spearman rho by rank correlation + an exact permutation p-value (100k perms,
two RNG streams). Archived JSON arithmetic only.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(
    HERE, "..", "c1_local_mc_calibration", "c1_local_mc25.json"))
with open(SRC, "r", encoding="utf-8-sig") as fh:
    rows = json.load(fh)["results"]["per_mlp"]
comp = [r for r in rows if not r["combined_budget_exhausted"]]
ec = np.array([r["effective_compute"] for r in comp], float)
ad = np.array([r["adjusted_final_layer_score"] for r in comp], float)
fl = np.array([r["flops_used"] for r in comp], float)


def rank(x):
    o = x.argsort()
    r = np.empty_like(o, dtype=float)
    r[o] = np.arange(1, x.size + 1)
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    return float((ra @ rb) / np.sqrt((ra @ ra) * (rb @ rb)))


rho = spearman(ec, ad)
rho_pearson = float(np.corrcoef(ec, ad)[0, 1])
rho_flops = spearman(fl, ad)


def perm_p(seed, bitgen):
    rng = np.random.Generator(bitgen(seed))
    ra = rank(ec)
    rb = rank(ad)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    den = np.sqrt((ra @ ra) * (rb @ rb))
    null = np.empty(100_000)
    for i in range(100_000):
        null[i] = (ra @ rng.permutation(rb)) / den
    return {"p_two_sided": float(np.mean(np.abs(null) >= abs(rho))),
            "p_one_sided_positive": float(np.mean(null >= rho)),
            "null_sd": float(null.std(ddof=1))}


p1 = perm_p(20260810, np.random.PCG64)
p2 = perm_p(31337, np.random.Philox)

out = {
    "n": len(comp),
    "spearman_effcompute_vs_adjusted": rho,
    "pearson_effcompute_vs_adjusted": rho_pearson,
    "spearman_flopsused_vs_adjusted": rho_flops,
    "permutation_null_run_A": p1,
    "permutation_null_run_B": p2,
    "direction_supported_by_data_at_p05":
        (rho > 0 and p1["p_one_sided_positive"] < 0.05
         and p2["p_one_sided_positive"] < 0.05),
}
with open(os.path.join(HERE, "exclusion_direction.json"), "w",
          encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
