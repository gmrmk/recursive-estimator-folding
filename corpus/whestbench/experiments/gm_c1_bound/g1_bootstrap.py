"""gm_c1_bound G1 -- bootstrap CI on R + exclusion-bias bounds.

Run only after step0.py exits 0 (G0 pass, G0b no-kill). Committed-JSON
arithmetic + numpy RNG. No new estimator compute, no network, no writes
outside this directory.
"""
import json
import math
import os
import statistics as st

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(
    HERE, "..", "c1_local_mc_calibration", "c1_local_mc25.json"))

H = 6.470e-7
KERDOCK = 1.619e-7
OABUOD = 9.45e-8
BAND_LO, BAND_HI = 0.8, 1.25
R_BAND_LO = KERDOCK / (BAND_HI * OABUOD)
R_BAND_HI = KERDOCK / (BAND_LO * OABUOD)
B = 200_000
MINED_CI = (1.04, 2.42)
MINED_MAXIMP = 2.36
TOL_G2 = 0.05

with open(SRC, "r", encoding="utf-8-sig") as fh:
    doc = json.load(fh)
rows = doc["results"]["per_mlp"]
comp = [r for r in rows if not r["combined_budget_exhausted"]]
excl = [r for r in rows if r["combined_budget_exhausted"]]
A = np.array([r["adjusted_final_layer_score"] for r in comp], dtype=float)
n = A.size
meanA = float(A.mean())
sdA = float(A.std(ddof=1))
R = meanA / H


def boot(bitgen, seed):
    rng = np.random.Generator(bitgen(seed))
    idx = rng.integers(0, n, size=(B, n))
    means = A[idx].mean(axis=1)
    Rs = means / H
    lo, hi = np.percentile(Rs, [2.5, 97.5])
    return {
        "seed": seed, "bitgen": bitgen.__name__, "B": B,
        "ci95": [float(lo), float(hi)],
        "boot_mean_R": float(Rs.mean()),
        "boot_sd_R": float(Rs.std(ddof=1)),
        "p16": float(np.percentile(Rs, 15.865)),
        "p84": float(np.percentile(Rs, 84.135)),
        "frac_inside_band": float(
            np.mean((Rs >= R_BAND_LO) & (Rs <= R_BAND_HI))),
    }


bA = boot(np.random.PCG64, 20260810)
bB = boot(np.random.Philox, 77)
ci_lo = 0.5 * (bA["ci95"][0] + bB["ci95"][0])
ci_hi = 0.5 * (bA["ci95"][1] + bB["ci95"][1])
stream_agree = (abs(bA["ci95"][0] - bB["ci95"][0]) <= 0.01
                and abs(bA["ci95"][1] - bB["ci95"][1]) <= 0.01)

# analytic cross-derivations (no resampling at all)
se_R = sdA / (math.sqrt(n) * H)
norm_ci = [R - 1.96 * se_R, R + 1.96 * se_R]
T21 = 2.079613844727680  # t_{0.975, df=21}
t_ci = [R - T21 * se_R, R + T21 * se_R]

# exclusion-bias bounds
med = float(np.median(A))
mx = float(A.max())
R_med_imp = float(np.concatenate([A, np.full(3, med)]).mean()) / H
R_max_imp = float(np.concatenate([A, np.full(3, mx)]).mean()) / H
R_min_imp = float(np.concatenate([A, np.full(3, float(A.min()))]).mean()) / H


def K(r):
    return KERDOCK / r


def P(r):
    return K(r) / OABUOD


# gates
kill = (ci_lo >= R_BAND_LO) and (ci_hi <= R_BAND_HI)
bias_up = R_max_imp > R
if kill:
    verdict = "KILL_CONFIRMED"
elif bias_up:
    verdict = "REVIVED_PASS"
else:
    verdict = "INCONCLUSIVE"

g2 = {
    "ci_lo_vs_mined": abs(ci_lo - MINED_CI[0]),
    "ci_hi_vs_mined": abs(ci_hi - MINED_CI[1]),
    "maximp_vs_mined": abs(R_max_imp - MINED_MAXIMP),
}
g2["pass"] = all(v <= TOL_G2 for v in g2.values())

out = {
    "n_completed": n, "n_excluded": len(excl),
    "mean22": meanA, "sd22_ddof1": sdA, "H_hosted_ref": H,
    "R_point": R,
    "se_R_local_only": se_R,
    "boot_run_A": bA, "boot_run_B": bB,
    "two_stream_endpoint_agreement_within_0.01": stream_agree,
    "CI95_percentile_bootstrap": [ci_lo, ci_hi],
    "one_sigma_R_bootstrap": bA["boot_sd_R"],
    "CI95_normal_analytic": norm_ci,
    "CI95_student_t21_analytic": t_ci,
    "median_A": med, "max_A": mx, "min_A": float(A.min()),
    "R_median_imputed": R_med_imp,
    "R_max_imputed": R_max_imp,
    "R_min_imputed_reference_only": R_min_imp,
    "exclusion_bias_is_upward": bias_up,
    "R_band_claims_unchanged": [R_BAND_LO, R_BAND_HI],
    "bootstrap_prob_R_inside_band": bA["frac_inside_band"],
    "Kerdock_hosted_at_R_point": K(R),
    "Kerdock_hosted_at_CI_lo": K(ci_lo),
    "Kerdock_hosted_at_CI_hi": K(ci_hi),
    "parity_ratio_at_R_point": P(R),
    "parity_ratio_at_CI_lo": P(ci_lo),
    "parity_ratio_at_CI_hi": P(ci_hi),
    "parity_ratio_at_R_max_imputed": P(R_max_imp),
    "Kerdock_hosted_at_R_max_imputed": K(R_max_imp),
    "G1_kill": kill, "G1_verdict": verdict,
    "G2_mined_reproduction": g2,
}
with open(os.path.join(HERE, "g1_bootstrap.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)

for k, v in out.items():
    print("%-42s %r" % (k, v))
