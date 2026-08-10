"""gm_s1s4_vd STEP 1 — shape refit (G2), Cauchy-Schwarz lower bound on vD from
the rotation-free floor31 statistic (G5, quantified), and the V4 cross-simulator
check against S1b's committed 80-net spread table.

Difficulty shape family (PREDECLARATION Q5): log D proportional to a standardized
exponential-power (generalized normal) variate with shape beta; density of the
log-factor prop. to exp(-|x|^beta). beta = inf reproduces S1's committed
log-uniform EXACTLY; beta = 2 is lognormal; beta = 1 is log-Laplace. The scale is
solved by bisection so that Var(D)/E[D]^2 equals the target vD on a fixed
presample, so vD is held FIXED while only the tail index moves.
"""
import json, os
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
EXP = os.path.join(ROOT, "corpus", "whestbench", "experiments")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "step1_results.json")

s0 = json.load(open(os.path.join(HERE, "step0_results.json")))
vF = s0["rotation_pool"]["vF"]
OBS_SPREAD = s0["panel"]["spread_raw_max_over_min"]
OBS_SPREAD_CORR = s0["panel"]["spread_corr_max_over_min"]

# rebuild the exact P2 pool (same construction as run_s1.py)
p2 = json.load(open(os.path.join(EXP, "pb1_premise_battery", "p2_results.json")))
parts = []
for seed, rec in sorted(p2["q1_oracle_headroom"]["per_net"].items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    parts.append(m / m.mean())
pool = np.concatenate(parts)
pool = pool / pool.mean()
assert abs(float(pool.var()) - vF) < 1e-15

m185 = json.load(open(os.path.join(EXP, "a_series_granular_adversarial",
                                   "m185_g0_stage1_checkpoint.json")))
keys = sorted(m185["nets"], key=lambda s: int(s))
raw = np.array([m185["nets"][k]["mse_raw"] for k in keys])
corr = np.array([m185["nets"][k]["mse_corr"] for k in keys])
floor = np.array([m185["nets"][k]["floor31"] for k in keys])

SEED = 20260810
NREP = 20_000
NPRE = 1 << 20
BETAS = [1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 10.0, np.inf]

out = {"experiment": "gm_s1s4_vd_step1", "vF": vF,
       "observed_spread_raw": OBS_SPREAD, "observed_spread_corr": OBS_SPREAD_CORR}

# ------------------------------------------------------------------ shapes --
def presample_logfactor(beta, rng):
    """Standardized exponential-power presample of the LOG difficulty factor."""
    if np.isinf(beta):
        g = rng.uniform(-1.0, 1.0, size=NPRE)      # -> log-uniform D (S1's shape)
    else:
        r = rng.gamma(1.0 / beta, 1.0, size=NPRE) ** (1.0 / beta)
        s = rng.integers(0, 2, size=NPRE) * 2 - 1
        g = r * s
    return g - g.mean()

def solve_scale(g, target_vd):
    """Bisect a so that relvar(exp(a*g)) == target_vd on this presample."""
    def rv(a):
        e = np.exp(a * g)
        return float(e.var() / e.mean() ** 2)
    lo, hi = 1e-9, 1.0
    while rv(hi) < target_vd:
        hi *= 1.5
        if hi > 50:
            raise RuntimeError("scale search overflow")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if rv(mid) < target_vd:
            lo = mid
        else:
            hi = mid
    a = 0.5 * (lo + hi)
    e = np.exp(a * g)
    D = e / e.mean()
    return a, D, float(D.var() / D.mean() ** 2)

READINGS = {
    "vD_moment_raw_ddof1": s0["moment_identity"]["raw"]["ddof1"]["vD_moment"],
    "vD_moment_corr_ddof1": s0["moment_identity"]["corr_floor_subtracted"]["ddof1"]["vD_moment"],
    "s1b_s17_low_0.0814": 0.0814,
    "s1b_s17_high_0.1220": 0.1220,
    "old_committed_S1_7.57e-4": 7.57e-4,
}

rng = np.random.default_rng(SEED)
pre = {}
for b in BETAS:
    pre[b] = presample_logfactor(b, rng)

shape_grid = {}
for rname, vd in READINGS.items():
    shape_grid[rname] = {}
    for b in BETAS:
        a, D, vd_ach = solve_scale(pre[b], vd)
        r2 = np.random.default_rng([SEED, int(1e6 * vd), int(b if np.isfinite(b) else 999)])
        di = r2.integers(0, NPRE, size=(NREP, 80))
        fi = r2.integers(0, pool.size, size=(NREP, 80))
        x = D[di] * pool[fi]
        sp = x.max(axis=1) / x.min(axis=1)
        p5, p50, p95 = np.percentile(sp, [5, 50, 95])
        sim_relvar = float(x.var() / x.mean() ** 2)
        shape_grid[rname]["beta=%s" % ("inf" if np.isinf(b) else ("%g" % b))] = {
            "beta": None if np.isinf(b) else b,
            "log_scale_a": a,
            "vD_achieved": vd_ach,
            "D_max_over_min": float(D.max() / D.min()),
            "spread_P5": float(p5), "spread_P50": float(p50), "spread_P95": float(p95),
            "p_sim_ge_observed": float((sp >= OBS_SPREAD).mean()),
            "observed_in_P5_P95": bool(p5 <= OBS_SPREAD <= p95),
            "sim_relvar_forward_check": sim_relvar,
            "model_relvar_identity": vd_ach + (1 + vd_ach) * vF,
        }
out["shape_refit_grid_vs_raw_spread"] = shape_grid

# G2: does SOME beta bracket the observed range at BOTH moment readings?
def any_bracket(rname):
    return [k for k, v in shape_grid[rname].items() if v["observed_in_P5_P95"]]

g2 = {
    "rule": ("PASS iff some beta in the declared grid puts the observed 15.5317 inside "
             "[P5,P95] of the simulated 80-net max/min at BOTH vD_moment(raw) and "
             "vD_moment(corr)"),
    "betas_bracketing_at_vD_moment_raw": any_bracket("vD_moment_raw_ddof1"),
    "betas_bracketing_at_vD_moment_corr": any_bracket("vD_moment_corr_ddof1"),
    "pass": bool(any_bracket("vD_moment_raw_ddof1") and any_bracket("vD_moment_corr_ddof1")),
}
out["G2_shape_freedom"] = g2

# --------------------------------- G5 quantified: Cauchy-Schwarz lower bound -
# For any rotation-free net statistic Z:  Cov(Z, mse) = Cov(Z, E[mse|net]) = S*Cov(Z,D)
#   => Var_between(mse) >= Corr(Z,mse)^2 * Var(mse)
#   => share_D >= rho^2  and  vD >= rho^2 * relvar_obs.
def bound(z, y, ddof=1):
    rho = float(np.corrcoef(z, y)[0, 1])
    rv = float(y.var(ddof=ddof) / y.mean() ** 2)
    return rho, rv, rho * rho * rv

rb = {}
for nm, y in [("mse_raw", raw), ("mse_corr", corr)]:
    rho, rv, vdmin = bound(floor, y)
    rb[nm] = {"pearson_rho_floor31": rho, "relvar_obs_ddof1": rv,
              "share_D_lower_bound": rho * rho, "vD_lower_bound": vdmin,
              "vD_moment_point": (rv - vF) / (1 + vF)}
# bootstrap + permutation on the raw arm (the decisive one)
rngb = np.random.default_rng(SEED + 7)
idx = rngb.integers(0, 80, size=(20000, 80))
fz, yz = floor[idx], raw[idx]
fzc, yzc = fz - fz.mean(axis=1, keepdims=True), yz - yz.mean(axis=1, keepdims=True)
rho_b = (fzc * yzc).sum(axis=1) / np.sqrt((fzc ** 2).sum(axis=1) * (yzc ** 2).sum(axis=1))
rv_b = yz.var(axis=1, ddof=1) / yz.mean(axis=1) ** 2
vdmin_b = rho_b ** 2 * rv_b
perm = np.empty(20000)
rngp = np.random.default_rng(SEED + 13)
for i in range(20000):
    perm[i] = np.corrcoef(rngp.permutation(floor), raw)[0, 1]
rb["bootstrap_and_null_raw_arm"] = {
    "vD_lower_bound_boot_mean": float(vdmin_b.mean()),
    "vD_lower_bound_ci95": [float(np.percentile(vdmin_b, 2.5)),
                            float(np.percentile(vdmin_b, 97.5))],
    "p_vD_lower_bound_ge_0.08": float((vdmin_b >= 0.08).mean()),
    "rho_boot_ci95": [float(np.percentile(rho_b, 2.5)), float(np.percentile(rho_b, 97.5))],
    "permutation_null_rho_sd": float(perm.std(ddof=1)),
    "permutation_p_two_sided": float((np.abs(perm) >= abs(rb["mse_raw"]["pearson_rho_floor31"])).mean()),
    "n_boot": 20000, "n_perm": 20000,
}
out["G5_quantified_lower_bound"] = rb

# ------------------------------------------------------ V4 cross-simulator --
v4 = {
    "s1b_committed_s17_low_row": {"vD": 0.0814, "P5": 11.64, "P50": 18.19,
                                  "P95": 25.51, "p_sim_ge": 0.720},
    "mine_s17_low_beta_inf": shape_grid["s1b_s17_low_0.0814"]["beta=inf"],
    "s1b_committed_s17_high_row": {"vD": 0.1220, "P5": 13.19, "P50": 21.22,
                                   "P95": 31.21, "p_sim_ge": 0.862},
    "mine_s17_high_beta_inf": shape_grid["s1b_s17_high_0.1220"]["beta=inf"],
    "s1_committed_control_row": {"vD": 7.57e-4, "P5": 9.14, "P50": 11.18,
                                 "P95": 11.94, "p_sim_ge": 0.000},
    "mine_control_beta_inf": shape_grid["old_committed_S1_7.57e-4"]["beta=inf"],
}
out["V4_cross_simulator_vs_s1b"] = v4

json.dump(out, open(OUT, "w"), indent=1)

print("=== STEP 1 ===")
for rname in READINGS:
    print("-- %s (vD=%.6f)" % (rname, READINGS[rname]))
    for k, v in shape_grid[rname].items():
        print("   %-10s D_maxmin=%7.2f  P5/P50/P95 = %6.2f /%7.2f /%8.2f  P(sim>=obs)=%.3f  brackets=%s"
              % (k, v["D_max_over_min"], v["spread_P5"], v["spread_P50"], v["spread_P95"],
                 v["p_sim_ge_observed"], v["observed_in_P5_P95"]))
print("G2 pass:", g2["pass"], "| raw brackets:", g2["betas_bracketing_at_vD_moment_raw"],
      "| corr brackets:", g2["betas_bracketing_at_vD_moment_corr"])
print("G5 bound (mse_raw): rho=%.4f relvar=%.4f -> vD >= %.4f  (moment point %.4f)"
      % (rb["mse_raw"]["pearson_rho_floor31"], rb["mse_raw"]["relvar_obs_ddof1"],
         rb["mse_raw"]["vD_lower_bound"], rb["mse_raw"]["vD_moment_point"]))
print("G5 bound (mse_corr): rho=%.4f relvar=%.4f -> vD >= %.4f  (moment point %.4f)"
      % (rb["mse_corr"]["pearson_rho_floor31"], rb["mse_corr"]["relvar_obs_ddof1"],
         rb["mse_corr"]["vD_lower_bound"], rb["mse_corr"]["vD_moment_point"]))
b = rb["bootstrap_and_null_raw_arm"]
print("   boot CI95 on vD lower bound: [%.4f, %.4f]  P(bound>=0.08)=%.3f  perm p=%.5f (null sd %.4f)"
      % (b["vD_lower_bound_ci95"][0], b["vD_lower_bound_ci95"][1],
         b["p_vD_lower_bound_ge_0.08"], b["permutation_p_two_sided"], b["permutation_null_rho_sd"]))
print("wrote", OUT)
