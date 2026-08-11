"""
R0/R1 — harmonic energy spectrum of the residual, from COMMITTED artifacts only.

LADDER-R RUNGS R0 (re-read) and R1 (arithmetic on committed numbers).
NO new measurement, NO nets generated, NO estimator/m245 code executed.

Inputs, all read-only, all committed:
  experiments/s6_bragg_spectrum/s6_results.json      (exact inner-product census, dims, lam_top)
  experiments/s7_speckle/s7_results.json             (c_32 table, C_pred table, per-net C_r)
  experiments/s15_stratification/s15_results.json    (deg<=2 R^2, pure-deg4 single-mode R^2)
  experiments/s17_ibc_floor/s17_results.json         (sigma^2, champion MSE, N_eff)
  experiments/pb1_premise_battery/m191_g0a_results.json  (per-degree design/iid RMS)

Everything below is either (i) exact rational combinatorics on d=256, (ii) linear
algebra on numbers quoted from those files, or (iii) [DECLARED BOUNDARY CALL, see
R0_HARMONIC_SPECTRUM.md deviation D1] re-derivation of the mean-field scalar
recurrence whose closed form and 37-point tabulation are both committed in
S7_VERDICT.md / s7_results.json, validated against that committed tabulation.
"""

import json
import os
from fractions import Fraction as Fr
from math import comb, pi, acos, sqrt, log

import numpy as np
from scipy.optimize import nnls

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, ".."))

D = 256
ALPHA2 = D - 2          # 2*alpha = 254
N_BASE = 32256
OUT = {}


def load(rel):
    with open(os.path.join(EXP, rel), "r", encoding="utf-8") as fh:
        return json.load(fh)


s6 = load("s6_bragg_spectrum/s6_results.json")
s7 = load("s7_speckle/s7_results.json")
s15 = load("s15_stratification/s15_results.json")
s17 = load("s17_ibc_floor/s17_results.json")
m191 = load("pb1_premise_battery/m191_g0a_results.json")

# ----------------------------------------------------------------------------
# 1. dim H_l, exact, two formulas; cross-checked against S6 constants
# ----------------------------------------------------------------------------
def dim_H(l, d=D):
    if l == 0:
        return 1
    if l == 1:
        return d
    return comb(d + l - 1, l) - comb(d + l - 3, l - 2)


def dim_H_alt(l, d=D):
    # (2l+d-2)/l * C(l+d-3, l-1)
    num = (2 * l + d - 2) * comb(l + d - 3, l - 1)
    assert num % l == 0
    return num // l


LMAX = 24
dims = {l: dim_H(l) for l in range(0, LMAX + 1)}
for l in range(1, LMAX + 1):
    assert dims[l] == dim_H_alt(l), l
CHECK = {}
CHECK["dim_H4_matches_s6"] = (dims[4] == s6["constants"]["dim_H4"], dims[4], s6["constants"]["dim_H4"])
CHECK["dim_H6_matches_s6"] = (dims[6] == s6["constants"]["dim_H6"], dims[6], s6["constants"]["dim_H6"])

# ----------------------------------------------------------------------------
# 2. Normalized Gegenbauer G_l = C_l^(alpha)(t)/C_l^(alpha)(1); stable recurrence
#      G_n = 2t (n+alpha-1)/(n+2alpha-1) G_{n-1} - (n-1)/(n+2alpha-1) G_{n-2}
#    (alpha = (d-2)/2 = 127).  Exact-rational and float64 versions.
# ----------------------------------------------------------------------------
def G_values(t_arr, lmax=LMAX):
    """float64 G_l(t) for l=0..lmax; t_arr array-like."""
    t = np.asarray(t_arr, dtype=np.float64)
    out = np.zeros((lmax + 1,) + t.shape)
    out[0] = 1.0
    if lmax >= 1:
        out[1] = t
    for n in range(2, lmax + 1):
        A = 2.0 * (n + ALPHA2 / 2.0 - 1.0) / (n + ALPHA2 - 1.0)
        B = (n - 1.0) / (n + ALPHA2 - 1.0)
        out[n] = A * t * out[n - 1] - B * out[n - 2]
    return out


def G_poly_exact(lmax=LMAX):
    """Exact monomial coefficient lists g[l] with G_l(t) = sum_j g[l][j] t^j."""
    g = [[Fr(1)], [Fr(0), Fr(1)]]
    for n in range(2, lmax + 1):
        A = Fr(2 * (2 * n + ALPHA2 - 2), 2 * (n + ALPHA2 - 1))   # 2(n+alpha-1)/(n+2alpha-1)
        B = Fr(n - 1, n + ALPHA2 - 1)
        prev, prev2 = g[n - 1], g[n - 2]
        new = [Fr(0)] * (n + 1)
        for j, c in enumerate(prev):
            new[j + 1] += A * c
        for j, c in enumerate(prev2):
            new[j] -= B * c
        g.append(new)
    return g


gpoly = G_poly_exact()

# exact-value cross-check against S6's committed kernel constants
def G_exact_at(l, t):
    return sum(c * t ** j for j, c in enumerate(gpoly[l]))


g4_0 = G_exact_at(4, Fr(0))
g4_16 = G_exact_at(4, Fr(1, 16))
g6_0 = G_exact_at(6, Fr(0))
g6_16 = G_exact_at(6, Fr(1, 16))
CHECK["G4_at_0"] = (float(g4_0), s6["constants"]["G4_at_0"])
CHECK["G4_at_1_16"] = (float(g4_16), s6["constants"]["G4_at_1/16"])
CHECK["G6_at_0"] = (float(g6_0), s6["constants"]["G6_at_0"])
CHECK["G6_at_1_16"] = (float(g6_16), s6["constants"]["G6_at_1/16"])

# C_4^(127) coefficient cross-check: C_l = G_l * C_l(1), C_l(1) = comb(l+2a-1, l)
C4_1 = comb(4 + ALPHA2 - 1, 4)
c4_coeffs = [c * C4_1 for c in gpoly[4]]
CHECK["C4_at_1"] = (C4_1, int(s6["constants"]["C4_at_1"]))
CHECK["C4_coeffs_t024"] = ([int(c4_coeffs[0]), int(c4_coeffs[2]), int(c4_coeffs[4])],
                           [int(x) for x in s6["constants"]["C4_coeffs_t^[0,2,4]"]])

# ----------------------------------------------------------------------------
# 3. DESIGN SUPPRESSION lambda_top(l) from the EXACT committed inner-product
#    census.  This is a property of the DESIGN, never of the residual field.
#      lambda_l = (1/N^2) * sum_{j,k} G_l(<x_j,x_k>)
#    = (1/N^2)[ N*1 + n0*G_l(0) + n+*G_l(1/16) + n-*G_l(-1/16) ]
#    Cross-checked at l=4 and l=6 against s6 closed-form lam_top.
# ----------------------------------------------------------------------------
fp = s6["fingerprint"]["distinct_values"]
n_diag = int(fp["1.0"])
n_zero = int(fp["0.0"])
n_pos = int(fp["0.0625"])
n_neg = int(fp["-0.0625"])
assert n_diag + n_zero + n_pos + n_neg == N_BASE ** 2
assert n_diag == N_BASE

lam_top = {}
for l in range(1, LMAX + 1):
    val = (Fr(n_diag) * Fr(1)
           + Fr(n_zero) * G_exact_at(l, Fr(0))
           + Fr(n_pos) * G_exact_at(l, Fr(1, 16))
           + Fr(n_neg) * G_exact_at(l, Fr(-1, 16))) / Fr(N_BASE ** 2)
    lam_top[l] = float(val)

CHECK["lam_top4_vs_s6"] = (lam_top[4], s6["deg4"]["closed_form"]["lam_top"])
CHECK["lam_top6_vs_s6"] = (lam_top[6], s6["deg6"]["closed_form"]["lam_top"])
# and the design/iid RMS ratios sqrt(N*lambda) vs S6's Haar numbers
CHECK["haarH4_rms_ratio"] = (sqrt(N_BASE * lam_top[4]), s6["haar_H4_design_over_iid_rms"])
CHECK["haarH6_rms_ratio"] = (sqrt(N_BASE * lam_top[6]), s6["haar_H6_design_over_iid_rms"])

design_supp = {l: N_BASE * lam_top[l] for l in range(1, LMAX + 1)}   # 1.0 == iid-level

# ----------------------------------------------------------------------------
# 4. Exact monomial -> Gegenbauer transfer:  a_l = sum_k b_k * kappa[k][l]
#    kappa[k][l] = m_l * E_t[ t^k G_l(t) ],  t = <u,v> Haar on S^{d-1}
# ----------------------------------------------------------------------------
KMAX = 40


def moment_t(k, d=D):
    """E[t^k], t = <u,v> Haar on S^{d-1}; exact Fraction."""
    if k % 2:
        return Fr(0)
    p = k // 2
    v = Fr(1)
    for i in range(p):
        v *= Fr(2 * i + 1, d + 2 * i)
    return v


MOM = [moment_t(k) for k in range(KMAX + 2 * LMAX + 2)]
kappa = np.zeros((KMAX + 1, LMAX + 1))
kappa_exact = {}
for l in range(0, LMAX + 1):
    ml = Fr(dims[l])
    for k in range(0, KMAX + 1):
        s = Fr(0)
        for j, c in enumerate(gpoly[l]):
            s += c * MOM[k + j]
        kappa_exact[(k, l)] = ml * s
        kappa[k, l] = float(ml * s)

CHECK["kappa_1_1_is_one"] = kappa[1, 1]
CHECK["kappa_4_4_is_inv_leading"] = kappa[4, 4]

# ----------------------------------------------------------------------------
# 5. Mean-field kernel  [DECLARED BOUNDARY CALL D1]
#    f(c) = (sqrt(1-c^2) + c(pi - arccos c))/pi, iterated 32x, exactly as
#    committed in S7_VERDICT.md; validated against the committed 37-point
#    table_c32 and the committed 8-point c32_probe.
# ----------------------------------------------------------------------------
DEPTH = 32


def f_relu(c):
    c = np.clip(np.asarray(c, dtype=np.float64), -1.0, 1.0)
    return (np.sqrt(1.0 - c * c) + c * (np.pi - np.arccos(c))) / np.pi


def c32(t):
    c = np.asarray(t, dtype=np.float64).copy()
    for _ in range(DEPTH):
        c = f_relu(c)
    return c


grid_deg = np.array(s7["meanfield"]["table_grid_deg"], dtype=np.float64)
table_c32 = np.array(s7["meanfield"]["table_c32"], dtype=np.float64)
table_cpred = np.array(s7["meanfield"]["table_c_pred"], dtype=np.float64)
t_grid = np.cos(np.deg2rad(grid_deg))
m2 = s7["meanfield"]["m2_plateau_c32_at_90deg"]

repro = c32(t_grid)
VALID_C32_MAXABS = float(np.max(np.abs(repro - table_c32)))
probe_t = np.cos(np.deg2rad(np.array(s7["meanfield"]["probe_thetas_deg"])))
VALID_PROBE_MAXABS = float(np.max(np.abs(c32(probe_t) - np.array(s7["meanfield"]["c32_probe"]))))
VALID_M2 = float(abs(c32(np.array([0.0]))[0] - m2))

# Chebyshev fit of c_32 on [-R, R] -> monomial Taylor coefficients b_k
R_FIT = 0.60
KFIT = 30
_x = np.cos(np.pi * (np.arange(2 * KFIT + 1) + 0.5) / (2 * KFIT + 1))     # Cheb nodes on [-1,1]
_t = R_FIT * _x
_y = c32(_t)
cheb = np.polynomial.chebyshev.Chebyshev.fit(_x, _y, KFIT)
mono_in_x = np.polynomial.chebyshev.cheb2poly(cheb.convert(kind=np.polynomial.chebyshev.Chebyshev).coef)
b = np.array([mono_in_x[k] / (R_FIT ** k) for k in range(len(mono_in_x))])
FIT_RESID = float(np.max(np.abs(cheb(_x) - _y)))
# independent check of the fit away from the nodes
_tt = np.linspace(-R_FIT, R_FIT, 401)
FIT_RESID_DENSE = float(np.max(np.abs(np.polyval(b[::-1], _tt) - c32(_tt))))

nb = min(len(b), KMAX + 1)
a_mf_raw = np.array([float(np.dot(b[:nb], kappa[:nb, l])) for l in range(0, LMAX + 1)])
a0_mf = a_mf_raw[0]
a_mf = a_mf_raw / (1.0 - a0_mf)      # mean-removed energy share per degree
a_mf[0] = 0.0

MF_SUM_ALL = float(np.sum(a_mf_raw))            # should approach c_32(1) = 1
MF_A0_VS_M2 = (float(a0_mf), m2)
MF_TAIL = float(1.0 - MF_SUM_ALL)

# reconstruction check: sum_l a_l G_l(t) vs committed c_pred table
Gt = G_values(t_grid)
recon = (Gt[: LMAX + 1] * a_mf[:, None]).sum(axis=0)
RECON_MAXABS = float(np.max(np.abs(recon - table_cpred)))
RECON_AT_SMALL_T = float(np.max(np.abs(recon[grid_deg >= 60.0] - table_cpred[grid_deg >= 60.0])))

# ----------------------------------------------------------------------------
# 6. Model-free arm: NNLS in the G_l basis on the COMMITTED c_pred table only
# ----------------------------------------------------------------------------
def nnls_spectrum(t_pts, y_pts, lmax, w_sum1=50.0):
    Gm = G_values(t_pts, lmax)[1:]                       # (lmax, npts)
    A = Gm.T.copy()
    y = np.asarray(y_pts, dtype=np.float64).copy()
    A = np.vstack([A, w_sum1 * np.ones((1, lmax))])      # soft sum_l a_l = 1
    y = np.concatenate([y, [w_sum1 * 1.0]])
    sol, _ = nnls(A, y)
    pred = G_values(t_pts, lmax)[1:].T @ sol
    return sol, float(np.max(np.abs(pred - np.asarray(y_pts))))


mf_free = {}
for L in (8, 12, 16, 20):
    sol, res = nnls_spectrum(t_grid, table_cpred, L)
    mf_free[L] = {"a": sol.tolist(), "max_resid": res, "sum": float(sol.sum())}

# ----------------------------------------------------------------------------
# 7. Measured arm: NNLS on the 3 nets' committed 8-point C_r
# ----------------------------------------------------------------------------
probe_deg = np.array(s7["meanfield"]["probe_thetas_deg"], dtype=np.float64)
probe_tm = np.cos(np.deg2rad(probe_deg))
meas = {}
for net in s7["nets"]:
    y = np.array(net["c_meas"], dtype=np.float64)
    row = {"se_per_theta": net["se_per_theta"], "xi_half_deg": net["xi_measured_deg_raw"]}
    for L in (6, 8, 12):
        sol, res = nnls_spectrum(probe_tm, y, L)
        row["L%d" % L] = {"a": sol.tolist(), "max_resid": res, "sum": float(sol.sum()),
                          "cum_le3": float(sol[:3].sum()), "cum_le6": float(sol[:6].sum())}
    meas[str(net["net_seed"])] = row

# ----------------------------------------------------------------------------
# 8. Independent S15 anchors on the low-degree share (regression, not correlation)
# ----------------------------------------------------------------------------
s15_anchor = {}
for k, v in s15["nets"].items():
    deg1_lb = v["covariate_sets_baseA"]["C4_control_linear"]["incremental_oos"]
    deg1_ub = v["covariate_sets_baseA"]["C4_control_linear"]["r2_full_oos"]
    s15_anchor[k] = {
        "deg1_share_lower_bound": deg1_lb,        # increment of the single optimal deg-1 mode over Base-A
        "deg1_plus_deg2top8_share": deg1_ub,      # Base-A + C4 total R^2 (upper bound on a_1)
        "deg_le2_partial_share_baseB": v["base_B"]["r2_base_oos"],
        "pure_deg4_single_mode_R2_mean": v["positive_control"]["pure_deg4_R2_mean"],
        "pure_deg4_single_mode_R2_range": v["positive_control"]["pure_deg4_R2_range"],
        "raw_t4_R2_singular0": v["positive_control"]["raw_t4_R2_singular0"],
    }

# ----------------------------------------------------------------------------
# 9. THE TWO PREDICTIONS
# ----------------------------------------------------------------------------
# (a) equipartition:  a_l / dim H_l = const   <=>   a_l proportional to dim H_l
# (b) cascade:        a_l / dim H_l ~ l^-p    (power law, finite p)
per_mode_mf = {l: (a_mf[l] / dims[l] if a_mf[l] > 0 else 0.0) for l in range(1, LMAX + 1)}

# equipartition test statistic: a_4/a_1 measured vs dim H_4/dim H_1
equi_pred_a4_over_a1 = dims[4] / dims[1]
equi_obs_a4_over_a1_mf = a_mf[4] / a_mf[1]
equi_violation_mf = equi_pred_a4_over_a1 / equi_obs_a4_over_a1_mf

# S15 single-mode anchor: a_4/dim H_4 estimated directly from the pure-deg4 R^2
#   a single zonal H_4 mode's R^2 == that mode's energy share == a_4/dim H_4
#   IF the deg-4 content is isotropic in H_4.
s15_permode4 = [v["positive_control"]["pure_deg4_R2_mean"] for v in s15["nets"].values()]
s15_permode1_lb = [v["covariate_sets_baseA"]["C4_control_linear"]["incremental_oos"] / dims[1]
                   for v in s15["nets"].values()]

# cascade exponent from the mean-field per-mode spectrum, l = 1..12
ls = np.array([l for l in range(1, 13) if per_mode_mf[l] > 0], dtype=float)
es = np.array([per_mode_mf[int(l)] for l in ls])
slope, intercept = np.polyfit(np.log(ls), np.log(es), 1)
pred = np.polyval([slope, intercept], np.log(ls))
ss_res = float(np.sum((np.log(es) - pred) ** 2))
ss_tot = float(np.sum((np.log(es) - np.mean(np.log(es))) ** 2))
cascade_R2 = 1.0 - ss_res / ss_tot
# geometric (exponential) alternative: log e_l ~ linear in l
sl2, ic2 = np.polyfit(ls, np.log(es), 1)
pred2 = np.polyval([sl2, ic2], ls)
exp_R2 = 1.0 - float(np.sum((np.log(es) - pred2) ** 2)) / ss_tot
# factorial/dimension alternative: e_l = a_l/dim H_l with a_l nearly flat
per_degree_flat_ratio = {l: float(a_mf[l] / a_mf[1]) for l in range(1, 13)}

# ----------------------------------------------------------------------------
# 10. Where the estimator error actually lives, per degree
#     err_var/sigma^2 = sum_{l even >= 4} a_l * lambda_l   (odd killed by antipodes,
#     deg 0,2 killed by the exact 2-design)
# ----------------------------------------------------------------------------
err_share = {}
tot = 0.0
for l in range(4, LMAX + 1, 2):
    v = a_mf[l] * lam_top[l]
    err_share[l] = v
    tot += v
err_frac = {l: (v / tot if tot > 0 else 0.0) for l, v in err_share.items()}
implied_mse_over_sigma2 = tot
implied_N_eff = 1.0 / tot if tot > 0 else float("inf")
s17_N_eff = [s17["A_per_net"][k]["N_eff"] if "A_per_net" in s17 else None for k in ()]

# ----------------------------------------------------------------------------
OUT = {
    "ledger_id": "r0_harmonic_energy_spectrum",
    "rung": "R0/R1 only — committed artifacts + arithmetic; no new measurement",
    "d": D, "N_base": N_BASE, "depth": DEPTH,
    "dim_H": {str(l): dims[l] for l in range(0, 17)},
    "cross_checks": {k: (list(v) if isinstance(v, tuple) else v) for k, v in CHECK.items()},
    "design_suppression_N_lambda_top": {str(l): design_supp[l] for l in range(2, 17)},
    "lam_top": {str(l): lam_top[l] for l in range(2, 17)},
    "meanfield_validation": {
        "c32_table_37pt_max_abs_dev": VALID_C32_MAXABS,
        "c32_probe_8pt_max_abs_dev": VALID_PROBE_MAXABS,
        "c32_at_90deg_abs_dev": VALID_M2,
        "cheb_fit_R": R_FIT, "cheb_fit_K": KFIT,
        "cheb_node_resid": FIT_RESID, "cheb_dense_resid": FIT_RESID_DENSE,
        "sum_a_l_all_degrees_should_be_1": MF_SUM_ALL,
        "a0_vs_committed_plateau": MF_A0_VS_M2,
        "tail_beyond_L%d" % LMAX: MF_TAIL,
        "recon_vs_committed_cpred_maxabs": RECON_MAXABS,
        "recon_vs_committed_cpred_maxabs_theta_ge60": RECON_AT_SMALL_T,
    },
    "spectrum_meanfield_a_l": {str(l): float(a_mf[l]) for l in range(1, LMAX + 1)},
    "spectrum_meanfield_per_mode": {str(l): per_mode_mf[l] for l in range(1, LMAX + 1)},
    "spectrum_meanfield_cumulative": {str(l): float(np.sum(a_mf[1:l + 1])) for l in range(1, LMAX + 1)},
    "spectrum_modelfree_nnls_on_committed_table": mf_free,
    "spectrum_measured_nets_nnls": meas,
    "s15_anchors": s15_anchor,
    "m191_design_over_iid_rms_by_degree": {
        rot: {deg: m191[rot][deg]["ratio"] for deg in m191[rot] if deg.startswith("deg")}
        for rot in ("rot0", "rot1", "rot2")
    },
    "tests": {
        "equipartition_predicted_a4_over_a1": equi_pred_a4_over_a1,
        "equipartition_observed_a4_over_a1_meanfield": float(equi_obs_a4_over_a1_mf),
        "equipartition_violation_factor_meanfield": float(equi_violation_mf),
        "per_mode_ratio_l1_over_l4_meanfield": float(per_mode_mf[1] / per_mode_mf[4]),
        "s15_per_mode_l4_direct": s15_permode4,
        "s15_per_mode_l1_lower_bound": s15_permode1_lb,
        "s15_per_mode_l1_over_l4": [lb / p4 for lb, p4 in zip(s15_permode1_lb, s15_permode4)],
        "cascade_powerlaw_exponent_p": float(-slope),
        "cascade_powerlaw_logR2": float(cascade_R2),
        "exponential_alt_log_slope_per_degree": float(sl2),
        "exponential_alt_logR2": float(exp_R2),
        "per_degree_a_l_over_a_1": per_degree_flat_ratio,
    },
    "estimator_error_by_degree": {
        "share_of_MSE_by_degree": {str(l): err_frac[l] for l in err_frac},
        "implied_MSE_over_sigma2": implied_mse_over_sigma2,
        "implied_N_eff": implied_N_eff,
        "s17_measured_N_eff": [39557.85, 27251.21, 46955.11],
        "s17_measured_MSE_over_sigma2": [1.997e-7 / 7.900e-3, 5.872e-7 / 1.600e-2, 2.369e-7 / 1.112e-2],
    },
}

with open(os.path.join(HERE, "r0_results.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, indent=2)

# ---------------------------------- report ----------------------------------
def p(*a):
    print(*a)


p("=== CROSS-CHECKS (committed vs recomputed) ===")
for k, v in CHECK.items():
    p(" ", k, "->", v)
p()
p("=== MEAN-FIELD VALIDATION ===")
for k, v in OUT["meanfield_validation"].items():
    p(" ", k, "=", v)
p()
p("=== SPECTRUM (mean-field, committed closed form) ===")
p(" l | dim H_l        | a_l (deg share) | cum   | per-mode a_l/dimH | N*lam_top (design)")
for l in range(1, 17):
    p("%2d | %14d | %.6e | %.4f | %.6e | %.6e"
      % (l, dims[l], a_mf[l], float(np.sum(a_mf[1:l + 1])), per_mode_mf[l], design_supp[l]))
p()
p("=== MODEL-FREE NNLS ON THE COMMITTED c_pred TABLE ===")
for L, r in mf_free.items():
    p(" L=%2d sum=%.4f maxresid=%.2e a_1..a_8=%s" % (L, r["sum"], r["max_resid"],
      np.array2string(np.array(r["a"][:8]), precision=4)))
p()
p("=== MEASURED NETS (8 committed C_r points each) ===")
for k, v in meas.items():
    p(" net", k, "xi=%.1f" % v["xi_half_deg"], "L8 a_1..a_6 =",
      np.array2string(np.array(v["L8"]["a"][:6]), precision=4),
      "cum<=3=%.3f cum<=6=%.3f resid=%.3f" % (v["L8"]["cum_le3"], v["L8"]["cum_le6"], v["L8"]["max_resid"]))
p()
p("=== S15 ANCHORS ===")
for k, v in s15_anchor.items():
    p(" net", k, v)
p()
p("=== TESTS ===")
for k, v in OUT["tests"].items():
    p(" ", k, "=", v)
p()
p("=== ESTIMATOR ERROR BY DEGREE ===")
for k, v in OUT["estimator_error_by_degree"].items():
    p(" ", k, "=", v)
p()
p("wrote r0_results.json")
