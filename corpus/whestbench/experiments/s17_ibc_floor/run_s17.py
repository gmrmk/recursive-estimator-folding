#!/usr/bin/env python
"""
S17 -- ledger id s17_information_complexity_lower_bound.
Budget-indexed achievable-MSE envelope S(B) + sampling-floor location for the
champion (antipodally-doubled Kerdock design) and an ednacob adjudication.

LOWER-BOUND ATTEMPT with its own gates.  Every claim carries its earned level.
  - an achievable-envelope point (a method that runs) is an UPPER BOUND on S(B).
  - a fooling-pair / floor-invariant gap is a LOWER BOUND (impossibility).
  These are NOT conflated.

Firewall: reads only committed synthetic-He-net-derived artifacts (S5 ybar
arrays, S6/S7/S16 json) + own derivations.  No truth/scorer/sealed reads
(S16 already validated champion==cached-m181 to 6 digits; that number is quoted,
not re-read here).  Writes confined to s17_ibc_floor/.

The design fingerprint decomposition is EXACT (4-term base / 5-term doubled);
no 64512^2 brute sum is taken.
"""
import json, os, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP  = os.path.dirname(HERE)
S5   = os.path.join(EXP, "s5_kink_concentration")

# ---------------------------------------------------------------------------
# 0.  Committed constants (stated, not silently trusted)
# ---------------------------------------------------------------------------
# S6 exact inner-product census over the 32,256 base-set pairs (s6_results.json
# ->fingerprint; S6_VERDICT.md table).  Values in {1, 0, +1/16, -1/16}.
N_BASE = 32256
N_FULL = 64512                     # antipodally-doubled design (S15/S16 config)
FP_BASE = {                        # multiplicity of each off-diagonal shell (base)
    "t=0"     : 8225280,           # N*255, all within-frame off-diagonal pairs
    "t=+1/16" : 548352000,         # cross-frame, +1/16
    "t=-1/16" : 483840000,         # cross-frame, -1/16
}
# S7 mean-field depth-32 kernel and probe values (s7_results.json).
M2 = 0.9747204751243136            # c_32(0) plateau (t=0 -> 90 deg)
# S16 per-net champion MSE (16 rotation replicates; ==cached-m181 arm0 to 6 dig)
CHAMP = {"101": 1.9971942916463923e-07,
         "202": 5.872086598611009e-07,
         "303": 2.3692484273379475e-07}
CHAMP_M181 = {"101": 1.9971998400629498e-07,     # S16 crosscheck (2nd signal)
              "202": 5.872094245418941e-07,
              "303": 2.369255085030329e-07}
# Leaderboard (RAYAN53_FORENSICS_20260810.md; score law S=MSE*max(0.1,C/B))
B_TOTAL = 2.72e11
LB = {  # entry: (raw_mse, adjusted_mse, C_over_B)
    "champion":  (2.818e-7, 1.832e-7, 0.650),
    "ednacob":   (9.11e-8,  4.62e-8,  0.507),
    "joe_wanza2":(4.0e-9,   2.11e-8,  5.27),
}
CLOSURE_FULLCOV = 9.6e-5           # T2/M181 full-cov Gaussian closure, depth 32
COVARIATE_R2    = 0.01564795242809819  # S15 best pooled OOS incremental R^2

out = {"ledger_id": "s17_information_complexity_lower_bound",
       "framing": ("LOWER-BOUND ATTEMPT: achievable-envelope points are UPPER "
                   "bounds on S(B); the point-floor invariant gap is a LOWER "
                   "bound (impossibility). Not a minimax proof, not a closure "
                   "certificate."),
       "labels": {"observed": "ran/read this session",
                  "derived":  "follows from observations by shown steps",
                  "reported": "committed doc/result says so"}}

# ---------------------------------------------------------------------------
# 1.  S7 mean-field kernel -> residual correlation at the design inner products
#     c_r(t) = (c_32(t) - m2) / (1 - m2)   (mean-removed; c_r(0)=0, c_r(1)=1)
# ---------------------------------------------------------------------------
def f_kernel(c):
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(1.0 - c*c) + c*(np.pi - np.arccos(c))) / np.pi

def c32(t, layers=32):
    c = float(t)
    for _ in range(layers):
        c = f_kernel(c)
    return c

def c_resid(t):
    return (c32(t) - M2) / (1.0 - M2)

t_vals = {"+1/16": 1.0/16, "-1/16": -1.0/16, "0": 0.0, "-1": -1.0}
c_mf = {k: c_resid(v) for k, v in t_vals.items()}
c_mf_even_1_16 = 0.5*(c_mf["+1/16"] + c_mf["-1/16"])   # antipodal doubling keeps
out["A_meanfield_residual_correlation"] = {
    "note": ("derived from S7 depth-32 kernel; mean-removed so c_r(0)=0 exactly, "
             "c_r(1)=1. Antipodal doubling of the design cancels the ODD part, "
             "so only the even combination survives in the quadrature sum."),
    "c_r(+1/16)_86.42deg": c_mf["+1/16"],
    "c_r(-1/16)_93.58deg": c_mf["-1/16"],
    "c_r(0)_90deg": c_mf["0"],
    "c_r(-1)_antipode": c_mf["-1"],
    "c_r_even(1/16)": c_mf_even_1_16,
    "level": "derived"}

# ---------------------------------------------------------------------------
# 2.  EXACT fingerprint of the 64,512 antipodally-doubled design, derived from
#     the S6 base census by the doubling map {x_i,-x_i}.  For a cross-frame base
#     pair at +/-1/16 the 4 sign combinations give 2 at +1/16 and 2 at -1/16, so
#     the doubled census is sign-BALANCED (the Kerdock +1/16 excess vanishes).
# ---------------------------------------------------------------------------
n0p  = 4 * FP_BASE["t=0"]                                   # within-frame off-diag
npp  = 2 * (FP_BASE["t=+1/16"] + FP_BASE["t=-1/16"])        # doubled +1/16
nmp  = 2 * (FP_BASE["t=+1/16"] + FP_BASE["t=-1/16"])        # doubled -1/16
n_anti = N_FULL                                             # x with its antipode
fp_doubled = {"diag_t=1": N_FULL, "antipode_t=-1": n_anti,
              "within_t=0": n0p, "cross_t=+1/16": npp, "cross_t=-1/16": nmp}
census_sum = sum(fp_doubled.values())
assert census_sum == N_FULL*N_FULL, (census_sum, N_FULL*N_FULL)      # bitwise close
# coefficients of c_r(t) in var*N_full^2/sigma^2  =  N + N*c(-1) + n0'c(0)+...:
coef_anti  = n_anti / N_FULL      # =1
coef_zero  = n0p    / N_FULL      # =510
coef_cross = (npp+nmp)/N_FULL     # =64000 (multiplies c_even(1/16))
out["A_fingerprint"] = {
    "base_multiplicities_from_S6": {"N_base": N_BASE, **FP_BASE},
    "base_census_check": N_BASE*N_BASE == N_BASE + sum(FP_BASE.values()),
    "doubled_multiplicities_derived": fp_doubled,
    "doubled_census_sum": census_sum, "N_full_sq": N_FULL*N_FULL,
    "doubled_census_exact": census_sum == N_FULL*N_FULL,
    "sign_balanced": npp == nmp,
    "inflation_coefficients_over_iid": {
        "antipode c_r(-1)": coef_anti, "within c_r(0)": coef_zero,
        "cross c_r_even(1/16)": coef_cross},
    "level": "derived (exact from the S6 census by the doubling map)"}

# Plugging the mean-field kernel into the exact fingerprint is UNSTABLE: the
# cross-shell coefficient is 64,000, so a sub-1e-3 error in c_even(1/16) moves the
# predicted inflation by O(10).  It is reported as a SENSITIVITY DIAGNOSTIC, not a
# floor -- it shows the floor CANNOT be pinned from the correlation kernel at the
# design's inner products, so the robust anchor is sigma^2/N (Section 3).
mf_inflation = 1.0 + coef_anti*c_mf["-1"] + coef_zero*c_mf["0"] + coef_cross*c_mf_even_1_16
out["A_fingerprint"]["meanfield_plugin_inflation_UNSTABLE_diagnostic"] = {
    "value": mf_inflation,
    "why_unstable": ("64,000 * c_even(1/16): mean-field c_even(1/16)=%.3e is a "
        "second-order Taylor tail the depth-32 iteration does not resolve to the "
        "~1e-5 precision the coefficient demands; empirical c_even(1/16)=~-5e-6 "
        "(Section 3) is ~%.0fx smaller. Do NOT read this as the floor."
        % (c_mf_even_1_16, abs(c_mf_even_1_16/5e-6))),
    "level": "derived (documented artifact)"}

# ---------------------------------------------------------------------------
# 3.  Field variance sigma^2 (two ways) + exact empirical shell correlations,
#     per net, from the committed S5 ybar arrays over the 64,512 design (r=0).
# ---------------------------------------------------------------------------
pernet = {}
for net in ("101", "202", "303"):
    d = np.load(os.path.join(S5, "s5_net%s_arrays.npz" % net))
    yb = d["ybar"].astype(np.float64); fr = d["frames"]
    mu = yb.mean()
    sig2_a = yb.var()                       # signal 1: mean(f^2)-mean(f)^2
    sig2_b = np.mean(d["r_global"]**2)      # signal 2: mean(residual^2), indep path
    # exact per-frame group sums -> shell products (no N^2 loop)
    order = np.argsort(fr, kind="stable"); ybs = yb[order]; frs = fr[order]
    uq, idx, cnt = np.unique(frs, return_index=True, return_counts=True)
    S = yb.sum(); Ssq = (yb*yb).sum(); fsum = np.add.reduceat(ybs, idx)
    sum_fsq = (fsum*fsum).sum()
    cross_prod = S*S - sum_fsq;      n_cross = N_FULL*N_FULL - (cnt*cnt).sum()
    within_prod = sum_fsq - Ssq;     n_within = (cnt*cnt).sum() - N_FULL
    G1 = Ssq / N_FULL
    G0 = within_prod / n_within                       # t~0 (0.2% antipode contam)
    Gx = cross_prod / n_cross                         # t=+/-1/16 even (balanced)
    c0_emp   = (G0 - mu*mu)/sig2_a
    cx_emp   = (Gx - mu*mu)/sig2_a
    floor_full = sig2_a / N_FULL                       # equal-cost iid floor
    floor_base = sig2_a / N_BASE                       # distinct-direction floor
    ch = CHAMP[net]
    pernet[net] = {
        "mu": mu, "sigma2_var(ybar)": sig2_a, "sigma2_mean(r_global^2)": sig2_b,
        "sigma2_two_way_rel_diff": abs(sig2_a-sig2_b)/sig2_a,
        "emp_c(0)_within": c0_emp, "emp_c_even(1/16)_cross": cx_emp,
        "champion_mse": ch, "champion_mse_m181_crosscheck": CHAMP_M181[net],
        "champion_vs_m181_ratio": ch/CHAMP_M181[net],
        "iid_floor_sigma2_over_64512": floor_full,
        "dir_floor_sigma2_over_32256": floor_base,
        "ratio_champ_over_costfloor": ch/floor_full,     # equal-FLOP
        "ratio_champ_over_dirfloor":  ch/floor_base,      # distinct-direction
        "N_eff_sigma2_over_champ": sig2_a/ch,
        "N_eff_over_N_eval": (sig2_a/ch)/N_FULL}
out["A_per_net"] = pernet

r_cost = np.array([pernet[n]["ratio_champ_over_costfloor"] for n in pernet])
r_dir  = np.array([pernet[n]["ratio_champ_over_dirfloor"]  for n in pernet])
def stat(a):
    m = float(a.mean()); s = float(a.std(ddof=1)); se = s/np.sqrt(len(a))
    return {"mean": m, "sd": s, "se": se, "t95_ci": [m-4.303*se, m+4.303*se],
            "per_net": a.tolist()}
out["A_pooled"] = {
    "ratio_champ_over_costfloor(sigma2/64512)": stat(r_cost),
    "ratio_champ_over_dirfloor(sigma2/32256)":  stat(r_dir),
    "meanfield_plugin_UNSTABLE_not_a_floor": mf_inflation,
    "s7_finite_width_band": [1.7, 2.2],
    "note": ("equal-FLOP floor sigma^2/N_eval counts every one of the 64,512 "
             "forwards as a draw; distinct-direction floor sigma^2/N_base "
             "counts the 32,256 base directions (antipode pair = 2 forwards).")}

# ---------------------------------------------------------------------------
# 4.  Sampling-floor GATE (predeclared).  Use the equal-FLOP ratio (conservative,
#     the larger of the two accountings) as the gated quantity.
# ---------------------------------------------------------------------------
pooled = float(r_cost.mean())
if pooled < 2.0:      gate = ("i", "champion within 2x of the sampling floor -> floor located")
elif pooled < 4.0:    gate = ("ii", "2-4x -> modest headroom")
else:                 gate = ("iii", ">4x -> a better SAMPLING scheme exists (would contradict S6/S7)")
out["A_gate"] = {"gated_quantity": "pooled champ/(sigma^2/64512)",
                 "value": pooled, "per_net": r_cost.tolist(),
                 "n_nets_in_gate_i(<2x)": int((r_cost < 2).sum()),
                 "class": gate[0], "verdict": gate[1],
                 "dir_matched_pooled": float(r_dir.mean())}

# ---------------------------------------------------------------------------
# 5.  PART B -- S(B) envelope (each point labelled).  MSE vs FLOP budget (C).
# ---------------------------------------------------------------------------
C_champ = LB["champion"][2]*B_TOTAL
C_ed    = LB["ednacob"][2]*B_TOTAL
scale_5p27_mse = LB["champion"][0]/5.27          # task's stated 5.27x scaling
envelope = [
 {"regime":"(i) B~0 cheap observables","flops":0.0,
  "achievable_mse": None, "note":
  "S15 covariates explain %.2f%% of residual -> essentially unreduced"
  % (COVARIATE_R2*100), "bound":"UPPER (no reduction)","level":"observed(S15)"},
 {"regime":"(ii) analytic closure (deg<=2 exact plateau)","flops":0.0,
  "achievable_mse": CLOSURE_FULLCOV, "note":"T2/M181 full-cov Gaussian closure",
  "bound":"UPPER/achievable","level":"reported(T2/M181)"},
 {"regime":"(iii) our sampling budget (champion)","flops":C_champ,
  "achievable_mse": LB["champion"][0], "note":"C/B 0.650, antipodal Kerdock MC",
  "bound":"UPPER/achievable","level":"reported(leaderboard)"},
 {"regime":"(iv) 5.27x-budget sampling scaling","flops":LB["champion"][2]*B_TOTAL*5.27,
  "achievable_mse": scale_5p27_mse, "note":"joe_wanza-class honest reference (1/N)",
  "bound":"UPPER/achievable","level":"derived(1/N from champion)"},
 {"regime":"(v) B=inf","flops":float("inf"),"achievable_mse":0.0,
  "note":"limit","bound":"limit","level":"derived"}]
gap_raw = CLOSURE_FULLCOV / LB["champion"][0]
gap_adj = CLOSURE_FULLCOV / LB["champion"][1]
out["B_envelope"] = {
    "points": envelope,
    "plateau_to_line": ("closure plateau 9.6e-5 is budget-independent (analytic, "
        "deg<=2 exact); sampling line MSE ~ 1/B anchored at champion 2.818e-7."),
    "gap_closure_over_champion_raw": gap_raw,
    "gap_closure_over_champion_adjusted": gap_adj,
    "gap_note": ("width of the region between the closure plateau and the sampling "
        "line, reachable AMONG TESTED CLASSES ONLY by seed-side methods. This is a "
        "MAP of tested classes, NOT a proof no untested output-side method enters it."),
    "level":"reported points; derived gap"}

# ---------------------------------------------------------------------------
# 6.  PART C -- ednacob adjudication.  Point-evaluation floor is the FLOP
#     invariant I = MSE * C (variance-per-FLOP).  A pure point sampler cannot
#     have I below sigma^2 * flops_per_independent_sample.  The champion sits at
#     most `ratio` above that floor, so the floor invariant I_floor <= I_champ/ratio.
# ---------------------------------------------------------------------------
I_champ = LB["champion"][0]*C_champ
I_ed    = LB["ednacob"][0]*C_ed
vpf_ed_vs_champ = I_champ / I_ed                      # ~3.96x better (leaderboard)
# generous (champion 1.79x above floor) and tight (champion AT floor) brackets
I_floor_generous = I_champ / pooled                  # champion 1.79x above floor
I_floor_tight    = I_champ                            # champion at the floor
ed_below_generous = I_floor_generous / I_ed
ed_below_tight    = I_floor_tight    / I_ed
# equivalent per-budget statement: forwards ednacob could afford, best-case floor
flops_per_forward = C_champ / N_FULL
ed_forwards = C_ed / flops_per_forward
sig2_suite  = LB["champion"][0]*N_FULL/pooled        # back-out suite field variance
ed_best_point_mse = sig2_suite / ed_forwards         # every forward independent
out["C_ednacob"] = {
    "ednacob_raw_mse": LB["ednacob"][0], "ednacob_C_over_B": LB["ednacob"][2],
    "ednacob_flops": C_ed, "champion_flops": C_champ,
    "variance_per_flop_ednacob_vs_champion": vpf_ed_vs_champ,
    "champion_above_pointfloor_x": pooled,
    "ednacob_below_pointfloor_generous_x": ed_below_generous,
    "ednacob_below_pointfloor_tight_x": ed_below_tight,
    "budget_form": {
        "flops_per_forward": flops_per_forward,
        "ednacob_affordable_forwards": ed_forwards,
        "suite_sigma2_backed_out": sig2_suite,
        "ednacob_best_point_mse_floor": ed_best_point_mse,
        "ednacob_actual_mse": LB["ednacob"][0],
        "ednacob_beats_best_point_floor_x": ed_best_point_mse/LB["ednacob"][0]},
    "verdict": ("ednacob-honest is IMPOSSIBLE within point-evaluation: it sits "
        "%.2fx-%.2fx below the best point-sampling floor invariant. It therefore "
        "REQUIRES seed-side extraction (exact-control class, weight access) "
        "[strengthens M245], OR is over-budget/suspect [consistent with forensics]."
        % (ed_below_generous, ed_below_tight)),
    "confidence": ("high on the arithmetic (>=2.2x below the point floor in every "
        "accounting); moderate on assumptions: ednacob in the point-eval class at "
        "comparable per-forward cost, and sigma^2/N as the point lower bound "
        "(valid absent seed-side control variates)."),
    "level": "derived"}

# ---------------------------------------------------------------------------
with open(os.path.join(HERE, "s17_results.json"), "w") as fh:
    json.dump(out, fh, indent=2, default=lambda o: None if o==float("inf") else o)

# console summary
print("== S17 sampling-floor ==")
for n in pernet:
    p = pernet[n]
    print("net %s  sigma2=%.4e (2-way rel %.1e)  champ=%.4e  champ/(s2/64512)=%.3f  "
          "champ/(s2/32256)=%.3f  N_eff=%.0f"
          % (n, p["sigma2_var(ybar)"], p["sigma2_two_way_rel_diff"], p["champion_mse"],
             p["ratio_champ_over_costfloor"], p["ratio_champ_over_dirfloor"],
             p["N_eff_sigma2_over_champ"]))
print("pooled cost-floor ratio = %.3f (gate %s)   dir-floor ratio = %.3f   "
      "[mean-field plug-in %.1f = UNSTABLE artifact, not the floor]"
      % (pooled, gate[0], float(r_dir.mean()), mf_inflation))
print("doubled census exact:", out["A_fingerprint"]["doubled_census_exact"],
      " sign-balanced:", out["A_fingerprint"]["sign_balanced"])
print("emp shell corr: c(0)=%.2e  c_even(1/16)=%.2e  (both ~0 -> pseudo-random)"
      % (pernet['101']['emp_c(0)_within'], pernet['101']['emp_c_even(1/16)_cross']))
print("== S(B) gap == closure/champ raw=%.1fx  adjusted=%.1fx" % (gap_raw, gap_adj))
print("== ednacob == vpf %.2fx better than champ; below point floor %.2fx-%.2fx "
      "(best-point floor at its budget=%.3e vs actual %.3e => %.2fx)"
      % (vpf_ed_vs_champ, ed_below_generous, ed_below_tight,
         ed_best_point_mse, LB["ednacob"][0], ed_best_point_mse/LB["ednacob"][0]))
