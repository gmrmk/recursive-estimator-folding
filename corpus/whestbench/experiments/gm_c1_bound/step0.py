"""gm_c1_bound STEP 0 -- reproduction gate G0 + arithmetic kill gate G0b.

Committed-JSON arithmetic only. Read-only on every path outside this dir.
Predeclared in PREDECLARATION.md; gate constants are copied from it verbatim.
"""
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(
    HERE, "..", "c1_local_mc_calibration", "c1_local_mc25.json"))

# --- predeclared constants -------------------------------------------------
H = 6.470e-7            # hosted MC reference, verbatim from the ledger row
PUB_MEAN22 = 1.0686e-6  # published mean adjusted over 22 completed nets
PUB_R = 1.652           # published ratio
PUB_AGG25 = 0.09778592927244555   # committed results.adjusted_final_layer_score
KERDOCK = 1.619e-7      # Kerdock v3 local adjusted
OABUOD = 9.45e-8        # best honest hosted entry
BAND_LO, BAND_HI = 0.8, 1.25      # C1's own comparability band applied to P(R)
R_BAND_LO = KERDOCK / (BAND_HI * OABUOD)
R_BAND_HI = KERDOCK / (BAND_LO * OABUOD)
CV_KILL = (1.0 - R_BAND_LO / PUB_R) / 1.96   # G0b threshold

with open(SRC, "r", encoding="utf-8-sig") as fh:
    doc = json.load(fh)
res = doc["results"]
rows = res["per_mlp"]

all25 = [r["adjusted_final_layer_score"] for r in rows]
comp = [r for r in rows if not r["combined_budget_exhausted"]]
excl = [r for r in rows if r["combined_budget_exhausted"]]
A = [r["adjusted_final_layer_score"] for r in comp]

mean25 = sum(all25) / len(all25)
meanA = st.fmean(A)
sdA = st.stdev(A)
n = len(A)
cv_mean = sdA / (meanA * math.sqrt(n))
v_rel = (sdA ** 2) / (meanA ** 2)
R = meanA / H

# G0.1 -- does the archived per-row field aggregate to the committed top-level?
g01_rel = abs(mean25 - PUB_AGG25) / PUB_AGG25
g01 = g01_rel <= 1e-9
# G0.2 -- does the 22-net mean reproduce the published constant?
g02_mean_rel = abs(meanA / PUB_MEAN22 - 1.0)
g02_R_abs = abs(R - PUB_R)
g02 = (g02_mean_rel <= 0.005) and (g02_R_abs <= 0.005)

norm_lo = PUB_R * (1 - 1.96 * cv_mean)
norm_hi = PUB_R * (1 + 1.96 * cv_mean)
g0b_kill = (norm_lo >= R_BAND_LO) and (norm_hi <= R_BAND_HI)

ec_comp = [r["effective_compute"] for r in comp]
ec_excl = [r["effective_compute"] for r in excl]

out = {
    "source_file": SRC,
    "n_rows": len(rows), "n_completed": n, "n_excluded": len(excl),
    "excluded_names": [r["mlp_name"] for r in excl],
    "excluded_mlp_index": [r["mlp_index"] for r in excl],
    "excluded_effective_compute": ec_excl,
    "completed_mean_effective_compute": st.fmean(ec_comp),
    "completed_max_effective_compute": max(ec_comp),
    "excluded_are_top3_effective_compute":
        min(ec_excl) > max(ec_comp),
    "mean_all25_recomputed": mean25,
    "published_agg25": PUB_AGG25,
    "G0_1_rel_err": g01_rel, "G0_1_pass": g01,
    "mean22_recomputed": meanA,
    "published_mean22": PUB_MEAN22,
    "G0_2_mean_rel_err": g02_mean_rel,
    "R_point_recomputed": R,
    "published_R": PUB_R,
    "G0_2_R_abs_err": g02_R_abs, "G0_2_pass": g02,
    "sd_A_ddof1": sdA, "n": n, "CV_mean": cv_mean,
    "relative_variance_v_rel": v_rel,
    "spread_max_over_min": max(A) / min(A),
    "min_A": min(A), "max_A": max(A), "median_A": st.median(A),
    "R_band_for_claims_unchanged": [R_BAND_LO, R_BAND_HI],
    "G0b_CV_kill_threshold": CV_KILL,
    "G0b_normal_interval": [norm_lo, norm_hi],
    "G0b_KILL": g0b_kill,
    "A_sorted": sorted(A),
}
with open(os.path.join(HERE, "step0.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)

for k in ("n_completed", "n_excluded", "mean_all25_recomputed",
          "published_agg25", "G0_1_rel_err", "G0_1_pass",
          "mean22_recomputed", "G0_2_mean_rel_err", "R_point_recomputed",
          "G0_2_R_abs_err", "G0_2_pass", "sd_A_ddof1", "CV_mean",
          "relative_variance_v_rel", "spread_max_over_min",
          "excluded_effective_compute", "completed_max_effective_compute",
          "excluded_are_top3_effective_compute",
          "R_band_for_claims_unchanged", "G0b_CV_kill_threshold",
          "G0b_normal_interval", "G0b_KILL"):
    print("%-38s %r" % (k, out[k]))

if not (g01 and g02):
    print("\nG0 FAIL -> STOP. INCONCLUSIVE: archived rows do not reproduce the "
          "published constant; falsifier data premise broken.")
    raise SystemExit(2)
if g0b_kill:
    print("\nG0b KILL -> STOP. KILL_CONFIRMED at step 0: 22-net sampling error "
          "cannot move any downstream claim. C1 stands exactly as written.")
    raise SystemExit(3)
print("\nG0 pass, G0b does not kill -> proceed to G1 bootstrap.")
