"""gm_u3_grid -- ADVERSARIAL ATTACK on the Gate-A REVIVED_PASS.

NOT predeclared in PREDECLARATION.md; added AFTER the primary run returned
REVIVED_PASS, and recorded as Deviation 2 in VERDICT.md. It cannot make the
gate stricter or looser -- it only tests whether the cell that passed Gate A
is admissible and what inside it does the work.

Attacks:
 A1  Admissibility of `lognorm_ext`. If the lognormal is a bad fit to the 48
     committed pool values, the passing cell is not a model anyone would
     accept and the Gate-A pass is hollow. KS statistic + parametric-bootstrap
     (fit-refit) p-value, 20,000 replicates.
 A2  Which tail does the work? Re-run the decisive cell with the lognormal
     truncated (a) below at the empirical pool minimum and (b) above at the
     empirical pool maximum. U3's wording is about the UPPER tail; if the pass
     is driven entirely by the unbounded LOWER tail that must be said out loud.
 A3  Closed-form consequence: the suite-score SD of the passing alternative
     model, via the committed analytic identity
     SD = S*sqrt((vD + (1+vD)*vF/R)/n) (S1b two-signal item 2, empirically
     validated there to ratio [0.999, 1.002]).
"""
import json, math, hashlib, time
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
EXP = ROOT + r"\corpus\whestbench\experiments"
OUT = EXP + r"\gm_u3_grid\attack_results.json"

p2 = json.load(open(EXP + r"\pb1_premise_battery\p2_results.json"))
per_net = p2["q1_oracle_headroom"]["per_net"]
parts = []
for s, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], float)
    parts.append(m / m.mean())
pool = np.concatenate(parts); pool = pool / pool.mean()
srt = np.sort(pool)
vF_emp = float(pool.var())

m185 = json.load(open(EXP + r"\a_series_granular_adversarial\m185_g0_stage1_checkpoint.json"))
raw = np.array([v["mse_raw"] for v in m185["nets"].values()], float)
OBS = float(raw.max() / raw.min())

s1 = json.load(open(EXP + r"\s1_suite_risk\s1_results.json"))
ANCHOR = 1.83e-7

erf = np.vectorize(math.erf)
Phi = lambda z: 0.5 * (1.0 + erf(z / math.sqrt(2.0)))

# ---------------------------------------------------------------- A1
lg = np.log(srt)
mu, sd = float(lg.mean()), float(lg.std(ddof=0))


def ks_stat(x, mu, sd):
    xs = np.sort(x)
    n = xs.size
    F = Phi((np.log(xs) - mu) / sd)
    return float(np.max(np.maximum(np.arange(1, n + 1) / n - F, F - np.arange(n) / n)))


D_obs = ks_stat(srt, mu, sd)
rng = np.random.default_rng(11223344)
NB = 20_000
cnt = 0
Db = np.empty(NB)
for b in range(NB):
    z = rng.normal(mu, sd, size=48)
    m2, s2 = z.mean(), z.std(ddof=0)
    Db[b] = ks_stat(np.exp(z), m2, s2)
p_ks = float((Db >= D_obs).mean())
A1 = {"mu_log_mle": mu, "sd_log_mle": sd, "ks_stat_observed": D_obs,
      "parametric_bootstrap_p_value": p_ks, "n_bootstrap": NB,
      "ks_boot_p95": float(np.percentile(Db, 95)),
      "lognormal_admissible_at_0p05": bool(p_ks > 0.05),
      "caveat": "the 48 values are 3 nets x 16 rotations, each block normalised "
                "to its own mean, so they are not strictly iid; the same caveat "
                "applies to the committed empirical-48 pool itself."}
print("A1 KS:", json.dumps(A1, indent=1))

# ---------------------------------------------------------------- A2
MASTER_SEED = 20260809


def seed_layout():
    root = np.random.SeedSequence(MASTER_SEED)
    r4 = root.spawn(4); v, rep = root.spawn(2)
    return r4[0], v


_, VAL_SEED = seed_layout()
RATIO = 1.1
HALF = math.log(RATIO) / 2.0
DMEAN = math.sinh(HALF) / HALF


def ndtri(p):
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p = np.asarray(p, float); out = np.empty_like(p)
    pl, ph = 0.02425, 1 - 0.02425
    lo, hi = p < pl, p > ph; mid = ~(lo | hi)
    q = np.sqrt(-2 * np.log(np.where(lo, p, 0.5)))
    out[lo] = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])[lo] / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)[lo]
    q = np.sqrt(-2 * np.log(np.where(hi, 1 - p, 0.5)))
    out[hi] = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])[hi] / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)[hi]
    q = np.where(mid, p, 0.5) - 0.5; r = q * q
    out[mid] = ((((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q)[mid] / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)[mid]
    return out


def run_cell(ginv, nrep=10_000, seed=None):
    rg = np.random.default_rng(VAL_SEED if seed is None else seed)
    F = ginv(rg.random((nrep, 80)))
    D = np.exp(rg.uniform(-HALF, HALF, size=(nrep, 80))) / DMEAN
    sim = F * D
    sp = sim.max(axis=1) / sim.min(axis=1)
    p5, p50, p95 = np.percentile(sp, [5, 50, 95])
    return {"p5": float(p5), "p50": float(p50), "p95": float(p95),
            "p_ge_obs": float((sp >= OBS).mean()),
            "brackets": bool(p5 <= OBS <= p95)}


ln = lambda u: np.exp(mu + sd * ndtri(u))
ln_lo_trunc = lambda u: np.maximum(ln(u), srt[0])      # lower tail clipped to empirical min
ln_hi_trunc = lambda u: np.minimum(ln(u), srt[-1])     # upper tail clipped to empirical max
ln_both = lambda u: np.clip(ln(u), srt[0], srt[-1])

A2 = {"full_lognormal": run_cell(ln),
      "lognormal_lower_clipped_at_empirical_min": run_cell(ln_lo_trunc),
      "lognormal_upper_clipped_at_empirical_max": run_cell(ln_hi_trunc),
      "lognormal_clipped_both_ends": run_cell(ln_both),
      "empirical_min": float(srt[0]), "empirical_max": float(srt[-1]),
      "gate_interval": [0.20, 0.90]}
print("A2:", json.dumps(A2, indent=1))

# ---------------------------------------------------------------- A3
u = (np.arange(400_000) + 0.5) / 400_000
fl = ln(u); fl = fl / fl.mean()
vF_ln = float(fl.var())
vD_old = float(s1["calibration"]["vD_difficulty_variance"])
s1b = json.load(open(EXP + r"\s1b_dispersion_corrected\s1b_results.json"))


def sd_suite(vD, vF, n, R=1):
    return ANCHOR * math.sqrt((vD + (1 + vD) * vF / R) / n)


A3 = {
    "vF_empirical48": vF_emp, "vF_lognormal_ext": vF_ln,
    "vD_old_committed": vD_old,
    "sd_50net": {
        "committed_old_model (vD 7.57e-4, empirical F)": sd_suite(vD_old, vF_emp, 50),
        "PASSING ALTERNATIVE (vD 7.57e-4, lognormal F)": sd_suite(vD_old, vF_ln, 50),
        "s1b headline s17_low (vD 0.0814, empirical F)":
            sd_suite(s1b["arms"]["s17_low"]["vD"], vF_emp, 50),
        "s1b headline s17_high (vD 0.1220, empirical F)":
            sd_suite(s1b["arms"]["s17_high"]["vD"], vF_emp, 50),
    },
    "committed_bootstrap_sd_50net_old_control": s1b["arms"]["old_control"]["suite_50"]["sd"],
    "committed_bootstrap_sd_50net_s17_low": s1b["arms"]["s17_low"]["suite_50"]["sd"],
    "committed_bootstrap_sd_50net_s17_high": s1b["arms"]["s17_high"]["suite_50"]["sd"],
    "difficulty_share_R1": {
        "PASSING ALTERNATIVE (vD 7.57e-4, lognormal F)":
            vD_old / (vD_old + (1 + vD_old) * vF_ln),
        "s1b headline s17_low": s1b["arms"]["s17_low"]["variance_decomposition_R1"]["difficulty_share"],
        "s1b headline s17_high": s1b["arms"]["s17_high"]["variance_decomposition_R1"]["difficulty_share"],
    },
    "note": "closed form only; the identity was empirically validated against the "
            "bootstrap in S1b two-signal item 2 to ratio [0.999, 1.002].",
}
print("A3:", json.dumps(A3, indent=1))

json.dump({"attack": "post-hoc, not predeclared; see VERDICT.md Deviation 2",
           "A1_lognormal_admissibility": A1,
           "A2_which_tail_does_the_work": A2,
           "A3_closed_form_suite_sd_consequence": A3,
           "observed_spread": OBS},
          open(OUT, "w"), indent=1)
print("wrote", OUT)
