"""gm_s1s4_vd STEP 0 — moment identity + bootstrap + floor-correlation ceiling.

Pure arithmetic on committed artifacts. Implements PREDECLARATION.md sections
2 (Q1-Q4, Q8), 4 (gate G0), 5 (G1, G5). No forwards, no network.

Identity under the S1 model (mse_i = S*D_i*F_i, D indep F, E[D]=E[F]=1, one
distinct rotation per net):
    relvar(mse) = (1+vD)(1+vF) - 1  =>  vD = (relvar_obs - vF)/(1+vF)
which is SHAPE-FREE.
"""
import json, os, hashlib
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
EXP = os.path.join(ROOT, "corpus", "whestbench", "experiments")
M185 = os.path.join(EXP, "a_series_granular_adversarial", "m185_g0_stage1_checkpoint.json")
A1B = os.path.join(EXP, "a_series_granular_adversarial", "a1b_tail_diagnostics.json")
P2 = os.path.join(EXP, "pb1_premise_battery", "p2_results.json")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "step0_results.json")

BOOT_SEED = 20260810
N_BOOT = 20_000

out = {"experiment": "gm_s1s4_vd_step0",
       "predeclaration": "PREDECLARATION.md sections 2,4,5 (G0,G1,G5)"}

# ---------------------------------------------------------------- panel ----
m185 = json.load(open(M185))
nets = m185["nets"]
keys = sorted(nets, key=lambda s: int(s))
raw = np.array([nets[k]["mse_raw"] for k in keys], dtype=np.float64)
corr = np.array([nets[k]["mse_corr"] for k in keys], dtype=np.float64)
floor = np.array([nets[k]["floor31"] for k in keys], dtype=np.float64)
net_seeds = [nets[k]["net_seed"] for k in keys]
rot_seeds = [nets[k]["rot_seed"] for k in keys]

assert len(keys) == 80
assert len(set(net_seeds)) == 80 and len(set(rot_seeds)) == 80
id_err = float(np.abs(raw - corr - floor).max())
id_rel = float((np.abs(raw - corr - floor) / raw).max())
out["panel"] = {
    "n_nets": 80,
    "distinct_net_seeds": len(set(net_seeds)),
    "distinct_rot_seeds": len(set(rot_seeds)),
    "identity_raw_minus_corr_minus_floor_max_abs": id_err,
    "identity_max_rel": id_rel,
    "sha256_mse_raw": hashlib.sha256(raw.tobytes()).hexdigest(),
    "spread_raw_max_over_min": float(raw.max() / raw.min()),
    "spread_corr_max_over_min": float(corr.max() / corr.min()),
    "floor_share_of_raw": {"mean": float((floor / raw).mean()),
                           "min": float((floor / raw).min()),
                           "max": float((floor / raw).max())},
    "relvar_floor31_ddof0": float(floor.var(ddof=0) / floor.mean() ** 2),
    "relvar_floor31_ddof1": float(floor.var(ddof=1) / floor.mean() ** 2),
    "E_floor_over_E_raw": float(floor.mean() / raw.mean()),
}

# ------------------------------------------------- rotation pool (vF) ------
p2 = json.load(open(P2))
per_net = p2["q1_oracle_headroom"]["per_net"]
parts = []
for seed, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    parts.append(m / m.mean())
pool = np.concatenate(parts)
pool = pool / pool.mean()
vF = float(pool.var())
out["rotation_pool"] = {
    "n": int(pool.size), "vF": vF,
    "max_over_min": float(pool.max() / pool.min()),
    "construction": "identical to run_s1.py: per-net mean-normalized, pooled, mean forced to 1",
}

# --------------------------------------------- Q1/Q2/Q3 moment identity ----
def relvar(a, ddof):
    return float(a.var(ddof=ddof) / a.mean() ** 2)

def vd_from_relvar(rv):
    return (rv - vF) / (1.0 + vF)

moment = {}
for name, a in [("raw", raw), ("corr_floor_subtracted", corr)]:
    d = {}
    for ddof in (0, 1):
        rv = relvar(a, ddof)
        vd = vd_from_relvar(rv)
        d["ddof%d" % ddof] = {
            "relvar_obs": rv, "vD_moment": vd,
            "share_D": vd / rv,
            "share_rotation": 1.0 - vd / rv,
            "implied_D_max_over_min_loguniform": None,
        }
    moment[name] = d
out["moment_identity"] = moment

# --------------------------------------------------- Q4 bootstrap CI -------
rng = np.random.default_rng(BOOT_SEED)
idx = rng.integers(0, 80, size=(N_BOOT, 80))
boot = {}
for name, a in [("raw", raw), ("corr_floor_subtracted", corr)]:
    s = a[idx]
    for ddof in (0, 1):
        rv = s.var(axis=1, ddof=ddof) / s.mean(axis=1) ** 2
        vd = (rv - vF) / (1.0 + vF)
        lo, hi = np.percentile(vd, [2.5, 97.5])
        boot["%s_ddof%d" % (name, ddof)] = {
            "vD_boot_mean": float(vd.mean()),
            "vD_ci95_lo": float(lo), "vD_ci95_hi": float(hi),
            "p_vD_ge_0.08": float((vd >= 0.08).mean()),
        }
out["bootstrap_vD"] = {"n_boot": N_BOOT, "seed": BOOT_SEED, "arms": boot}

# ---------------------------------------------------- G0 (KILL gate) -------
vd_raw1 = moment["raw"]["ddof1"]["vD_moment"]
vd_corr1 = moment["corr_floor_subtracted"]["ddof1"]["vD_moment"]
g0_fires = bool(vd_raw1 >= 0.08 and vd_corr1 >= 0.08)
out["G0_step0_kill_gate"] = {
    "rule": "KILL (S1b stands, candidate dead) iff vD_moment >= 0.08 under BOTH floor treatments (ddof=1)",
    "vD_raw_ddof1": vd_raw1, "vD_corr_ddof1": vd_corr1,
    "threshold": 0.08,
    "raw_ge_0.08": bool(vd_raw1 >= 0.08),
    "corr_ge_0.08": bool(vd_corr1 >= 0.08),
    "FIRES_KILL": g0_fires,
}

# ---------------------------------------------------- G1 ------------------
g1 = {
    "rule": "PASS iff vD_moment(raw,ddof1) < 0.08 AND bootstrap 95% upper bound < 0.08",
    "vD_raw_ddof1": vd_raw1,
    "boot_ci95_hi": boot["raw_ddof1"]["vD_ci95_hi"],
    "pass": bool(vd_raw1 < 0.08 and boot["raw_ddof1"]["vD_ci95_hi"] < 0.08),
}
out["G1_identification"] = g1

# ------------------------------- G5 floor-correlation ceiling --------------
def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])

pear_fr = float(np.corrcoef(floor, raw)[0, 1])
spear_fr = spearman(floor, raw)
pear_fc = float(np.corrcoef(floor, corr)[0, 1])
spear_fc = spearman(floor, corr)
a1b = json.load(open(A1B))
a1b_max = max(abs(v) for v in a1b["spearman"].values())

readings = {
    "old_committed_S1": 7.57e-4,
    "vD_moment_raw_ddof1": vd_raw1,
    "vD_moment_corr_ddof1": vd_corr1,
    "s1b_s17_low_0.0814": 0.0814,
    "s1b_s17_high_0.1220": 0.1220,
    "s1b_p2_low_0.2335": 0.2335,
    "s1b_p2_high_0.3614": 0.3614,
}
ceil = {}
for nm, vd in readings.items():
    share = vd / (vd + (1 + vd) * vF)
    c = float(np.sqrt(share))
    ceil[nm] = {
        "vD": vd, "share_D": share, "ceiling_sqrt_share_D": c,
        "excluded_by_floor31_pearson": bool(abs(pear_fr) > c),
        "excluded_by_floor31_spearman": bool(abs(spear_fr) > c),
        "excluded_by_a1b_best_spearman": bool(a1b_max > c),
    }
out["G5_floor_correlation_ceiling"] = {
    "why_floor31_is_rotation_free": ("run_m185_g0.py lines 185-191: floor31 = "
        "mean(var31)/n_samples from the 600k-sample TRUTH pass; a function of the "
        "net and the truth sampler only, no rot_seed dependence"),
    "corr_floor31_vs_mse_raw_pearson": pear_fr,
    "corr_floor31_vs_mse_raw_spearman": spear_fr,
    "corr_floor31_vs_mse_corr_pearson": pear_fc,
    "corr_floor31_vs_mse_corr_spearman": spear_fc,
    "a1b_weightsonly_spearman": a1b["spearman"],
    "a1b_max_abs_spearman": a1b_max,
    "a1b_multivariate_spearman": a1b["multi_spearman"],
    "readings": ceil,
    "minimum_vD_implied_by_floor31_pearson_raw": float(
        (pear_fr ** 2) * relvar(raw, 1) / (1 + vF) / (1 - (pear_fr ** 2) * relvar(raw, 1) / (1 + vF))
        if False else (pear_fr ** 2) * relvar(raw, 1) / ((1 + vF) * (1 - (pear_fr ** 2)))),
}

json.dump(out, open(OUT, "w"), indent=1)

print("=== STEP 0 (moment identity) ===")
print("vF = %.6f  (pool n=%d, max/min %.4f)" % (vF, pool.size, pool.max() / pool.min()))
for name in ("raw", "corr_floor_subtracted"):
    for ddof in (0, 1):
        d = moment[name]["ddof%d" % ddof]
        print("  %-22s ddof%d  relvar=%.6f  vD=%.6f  share_D=%.4f"
              % (name, ddof, d["relvar_obs"], d["vD_moment"], d["share_D"]))
for k, v in boot.items():
    print("  boot %-26s mean %.5f  CI95 [%.5f, %.5f]  P(vD>=0.08)=%.4f"
          % (k, v["vD_boot_mean"], v["vD_ci95_lo"], v["vD_ci95_hi"], v["p_vD_ge_0.08"]))
print("G0 FIRES_KILL:", g0_fires, " (raw>=0.08:", vd_raw1 >= 0.08, ", corr>=0.08:", vd_corr1 >= 0.08, ")")
print("G1 pass:", g1["pass"])
print("G5 corr(floor31, mse_raw) pearson=%.4f spearman=%.4f ; a1b max |spearman|=%.4f"
      % (pear_fr, spear_fr, a1b_max))
for nm, v in ceil.items():
    print("   %-26s share_D=%.4f ceiling=%.4f  excl_by_floor(P)=%s excl_by_a1b=%s"
          % (nm, v["share_D"], v["ceiling_sqrt_share_D"],
             v["excluded_by_floor31_pearson"], v["excluded_by_a1b_best_spearman"]))
print("wrote", OUT)
