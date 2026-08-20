"""gm_c1_bound -- POST-HOC ATTACK on the G1 PASS. NOT a predeclared gate.

Counter-hypothesis: the CI is wide only because one outlier net (max adjusted
4.865e-6) dominates the n=22 mean; drop it and the interval collapses inside
the claims-unchanged band, so C1 would stand after all.

Also computes a jackknife SE (no RNG at all) as a third independent derivation
of the sampling error. Whatever this prints goes into VERDICT.md verbatim.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(
    HERE, "..", "c1_local_mc_calibration", "c1_local_mc25.json"))
H = 6.470e-7
KERDOCK, OABUOD = 1.619e-7, 9.45e-8
R_BAND = (KERDOCK / (1.25 * OABUOD), KERDOCK / (0.8 * OABUOD))
B = 200_000

with open(SRC, "r", encoding="utf-8-sig") as fh:
    rows = json.load(fh)["results"]["per_mlp"]
A = np.array([r["adjusted_final_layer_score"] for r in rows
              if not r["combined_budget_exhausted"]], dtype=float)


def ci(a, seed=4242):
    rng = np.random.Generator(np.random.SFC64(seed))
    m = a[rng.integers(0, a.size, size=(B, a.size))].mean(axis=1) / H
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def jack_se(a):
    n = a.size
    loo = np.array([np.delete(a, i).mean() for i in range(n)]) / H
    return float(math.sqrt((n - 1) / n * ((loo - loo.mean()) ** 2).sum()))


full = {"n": int(A.size), "R": float(A.mean()) / H, "ci95": ci(A),
        "jackknife_se_R": jack_se(A)}
drop1 = np.sort(A)[:-1]
d1 = {"n": int(drop1.size), "R": float(drop1.mean()) / H, "ci95": ci(drop1, 99),
      "jackknife_se_R": jack_se(drop1)}
drop2 = np.sort(A)[:-2]
d2 = {"n": int(drop2.size), "R": float(drop2.mean()) / H, "ci95": ci(drop2, 7),
      "jackknife_se_R": jack_se(drop2)}
trim = np.sort(A)[1:-1]
tr = {"n": int(trim.size), "R": float(trim.mean()) / H, "ci95": ci(trim, 13),
      "jackknife_se_R": jack_se(trim)}

for d in (full, d1, d2, tr):
    d["ci_inside_claims_band"] = (d["ci95"][0] >= R_BAND[0]
                                  and d["ci95"][1] <= R_BAND[1])
    d["parity_at_ci_lo"] = KERDOCK / d["ci95"][0] / OABUOD
    d["parity_at_ci_hi"] = KERDOCK / d["ci95"][1] / OABUOD

out = {"R_band_claims_unchanged": list(R_BAND),
       "full_22": full, "drop_top1_21": d1, "drop_top2_20": d2,
       "trim_min_and_max_20": tr,
       "attack_lands": any(d["ci_inside_claims_band"]
                           for d in (d1, d2, tr))}
with open(os.path.join(HERE, "attack.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
