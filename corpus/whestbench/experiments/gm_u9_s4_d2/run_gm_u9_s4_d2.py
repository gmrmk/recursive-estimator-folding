"""gm_u9_s4_d2 — graveyard revival falsifier for S4's certified pass D2
("decorrelated 2nd entry ~doubles tail, 2.00x at 1.55e-7") under S1b's
corrected dispersion.

This file is a COPY of corpus/whestbench/experiments/s4_portfolio/run_s4.py.
The frozen original is not edited. Exactly three things differ:

  (1) DIFF_RATIO becomes a per-arm parameter (old_control 1.1, plus the two
      S1b bracket-validated arms vD = 0.0813595 / 0.1220393, with DIFF_RATIO
      inverted from vD by the same bisection run_s1b.py uses). Nothing else in
      the model, seeds, anchor, pool, copula, arms, rhos or thresholds moves.
  (2) `scipy.special.ndtr` is unavailable in the pinned interpreter, so a
      Cephes-shaped ndtr built on libm erf/erfc is supplied (see PREDECLARATION
      section 0.1). The old_control arm reproducing the committed cells is the
      empirical proof that the substitution is immaterial.
  (3) The output path is this directory; s4_results.json is never written.

Added measurement (the mined falsifier's requested reports):
  Door B union factor  U(T) = P(min(A,B) < T | rho_pair=0) / P(A < T)
  and the induced two-entry score correlation, for the same_mean arm (Door B)
  and the sens_fold3cap arm (Door A).

Two-signal verification (PREDECLARATION section 7):
  S1 copula path (this harness) vs an independent S1-style integer-index path
  at 1e6 suites on a different master seed; analytic Eq.1 correlation and Eq.2
  Jensen bound; bitwise chunk-0 repeat; rho=1 identity.
"""
import json
import math
import hashlib
import time
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
P2_PATH = ROOT + r"\corpus\whestbench\experiments\pb1_premise_battery\p2_results.json"
S17_PATH = ROOT + r"\corpus\whestbench\experiments\s17_ibc_floor\s17_results.json"
S1B_PATH = ROOT + r"\corpus\whestbench\experiments\s1b_dispersion_corrected\s1b_results.json"
S4_PATH = ROOT + r"\corpus\whestbench\experiments\s4_portfolio\s4_results.json"
OUT_JSON = ROOT + r"\corpus\whestbench\experiments\gm_u9_s4_d2\gm_u9_s4_d2_results.json"

# ---- committed S4 constants (unchanged) ----
ANCHOR = 1.83e-7
N_SUITES = 100_000
N_NETS = 50
N_CHUNKS = 10
RHO_LIST = [0.0, 0.3, 0.6, 0.9, 1.0]
THRESH = [1.55e-7, 1.6e-7, 1.7e-7]
ARMS = {
    "same_mean": (1.83e-7, "pool"),
    "l2": (2.10e-7, "pool"),
    "r6": (1.83e-7, "fbar6"),
    "sens_fold3cap": (1.41e-7, "pool"),
}
GATE_ARMS = ["same_mean", "r6"]
GATE_PP = 0.02
N_FBAR6_PRESAMPLE = 1 << 20
MASTER_SEED = 202608094
S1_SD_REF = 1.562588338576902e-08
S1_P16_REF = 0.06434

# ---- falsifier constants (predeclared) ----
IND_MASTER_SEED = 20260810     # signal-2 path, disjoint from 202608094
IND_N_SUITES = 1_000_000
IND_N_CHUNKS = 100
PRIMARY_T = 1.55e-7
KILL_FACTOR = 1.95
NET_KEYS = ("101", "202", "303")

t0 = time.time()
tkey = lambda T: f"{T:.2e}"

# ---------------- ndtr replacement (deviation 0.1) ----------------
_erf = np.frompyfunc(math.erf, 1, 1)
_erfc = np.frompyfunc(math.erfc, 1, 1)
SQRTH = 0.7071067811865476           # 1/sqrt(2), Cephes M_SQRT1_2


def ndtr(a):
    """Cephes ndtr branch structure on libm erf/erfc."""
    a = np.asarray(a, dtype=np.float64)
    x = a * SQRTH
    z = np.abs(x)
    out = np.empty(x.shape, dtype=np.float64)
    m = z < SQRTH
    if m.any():
        out[m] = 0.5 + 0.5 * _erf(x[m]).astype(np.float64)
    nm = ~m
    if nm.any():
        y = 0.5 * _erfc(z[nm]).astype(np.float64)
        out[nm] = np.where(x[nm] > 0.0, 1.0 - y, y)
    return out


# ---------------- calibration: rotation factor pool from P2 (unchanged) ----
p2 = json.load(open(P2_PATH))
per_net = p2["q1_oracle_headroom"]["per_net"]
pool_parts = []
for seed, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    pool_parts.append(m / m.mean())
pool = np.concatenate(pool_parts)
pool = pool / pool.mean()
pool_sorted = np.sort(pool)
vF = float(pool.var())

# ---------------- vD arms: re-derived in-harness, as run_s1b.py does --------
def vD_of_ratio(r):
    half = np.log(r) / 2.0
    if half <= 0:
        return 0.0
    d_mean = np.sinh(half) / half
    return float((np.sinh(2 * half) / (2 * half)) / d_mean ** 2 - 1.0)


def ratio_of_vD(target):
    lo, hi = 1.0 + 1e-12, 1e6
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        if vD_of_ratio(mid) < target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def relvar(x, ddof):
    x = np.asarray(x, dtype=np.float64)
    return float(x.var(ddof=ddof) / x.mean() ** 2)


s17 = json.load(open(S17_PATH))
sig2 = np.array([s17["A_per_net"][k]["sigma2_var(ybar)"] for k in NET_KEYS])
vD_s17_low = relvar(sig2, 0)
vD_s17_high = relvar(sig2, 1)

s1b = json.load(open(S1B_PATH))
assert abs(vF - s1b["calibration"]["vF"]) < 1e-15, vF
assert abs(vD_s17_low - s1b["arms"]["s17_low"]["vD"]) < 1e-15
assert abs(vD_s17_high - s1b["arms"]["s17_high"]["vD"]) < 1e-15

ARM_DEFS = {
    "old_control": {"ratio": 1.1, "source": "committed S4/S1/U9 model"},
    "vd_s17_low": {"vD": vD_s17_low, "source": "S1b s17_low (relvar ddof=0), bracket-validated"},
    "vd_s17_high": {"vD": vD_s17_high, "source": "S1b s17_high (relvar ddof=1), bracket-validated"},
}
for name, a in ARM_DEFS.items():
    if "ratio" in a:
        a["vD"] = vD_of_ratio(a["ratio"])
    else:
        a["ratio"] = ratio_of_vD(a["vD"])
        assert abs(vD_of_ratio(a["ratio"]) - a["vD"]) < 1e-9 * a["vD"]
    a["half"] = float(np.log(a["ratio"]) / 2.0)
    a["d_mean"] = float(np.sinh(a["half"]) / a["half"])
    a["sd_analytic"] = float(ANCHOR * np.sqrt((a["vD"] + (1 + a["vD"]) * vF) / N_NETS))
    a["corr_analytic_eq1"] = float(a["vD"] / (a["vD"] + (1 + a["vD"]) * vF))
for n in ("vd_s17_low", "vd_s17_high"):
    assert abs(ARM_DEFS[n]["ratio"] - s1b["arms"][{"vd_s17_low": "s17_low",
                                                   "vd_s17_high": "s17_high"}[n]]["diff_ratio"]) < 1e-9

s4_committed = json.load(open(S4_PATH))
assert abs(ARM_DEFS["old_control"]["vD"] - s4_committed["calibration"]["vD"]) < 1e-18
assert abs(vF - s4_committed["calibration"]["vF"]) < 1e-18


# ---------------- seeds (unchanged) ----------------
def spawn_all(master):
    root = np.random.SeedSequence(master)
    ss = root.spawn(N_CHUNKS + 1)
    return ss[:N_CHUNKS], ss[N_CHUNKS]


chunk_seeds, presample_seed = spawn_all(MASTER_SEED)


def build_fbar6(seedseq):
    rng = np.random.default_rng(seedseq)
    idx = rng.integers(0, pool.size, size=(N_FBAR6_PRESAMPLE, 6))
    fb = pool[idx].mean(axis=1)
    fb /= fb.mean()
    return np.sort(fb)


fbar6_sorted = build_fbar6(presample_seed)
vF6 = float(fbar6_sorted.var())


def qmap(U, sorted_vals):
    idx = np.minimum((U * sorted_vals.size).astype(np.int64), sorted_vals.size - 1)
    return sorted_vals[idx]


CHUNK = N_SUITES // N_CHUNKS


def run_arm(arm):
    half, d_mean = arm["half"], arm["d_mean"]

    def draw_D(rng, shape):
        return np.exp(rng.uniform(-half, half, size=shape)) / d_mean

    def run_chunk(seedseq):
        rng = np.random.default_rng(seedseq)
        Z_A = rng.standard_normal((CHUNK, N_NETS))
        W = rng.standard_normal((CHUNK, N_NETS))
        D = draw_D(rng, (CHUNK, N_NETS))
        F_A = qmap(ndtr(Z_A), pool_sorted)
        scoreA = ANCHOR * (D * F_A).mean(axis=1)
        out = {}
        fcorr = {}
        for rho in RHO_LIST:
            Z_B = rho * Z_A + np.sqrt(1.0 - rho * rho) * W
            U_B = ndtr(Z_B)
            F_B_pool = qmap(U_B, pool_sorted)
            F_B_r6 = qmap(U_B, fbar6_sorted)
            base_pool = (D * F_B_pool).mean(axis=1)
            base_r6 = (D * F_B_r6).mean(axis=1)
            for a_, (S_B, marg) in ARMS.items():
                out[(a_, rho)] = S_B * (base_pool if marg == "pool" else base_r6)
            fcorr[rho] = (
                float(np.corrcoef(F_A.ravel(), F_B_pool.ravel())[0, 1]),
                float(np.corrcoef(F_A.ravel(), F_B_r6.ravel())[0, 1]),
            )
        return scoreA, out, fcorr

    pA_chunks = {T: np.zeros(N_CHUNKS) for T in THRESH}
    pB_chunks = {(a_, r): {T: np.zeros(N_CHUNKS) for T in THRESH}
                 for a_ in ARMS for r in RHO_LIST}
    pmin_chunks = {(a_, r): {T: np.zeros(N_CHUNKS) for T in THRESH}
                   for a_ in ARMS for r in RHO_LIST}
    scorr_chunks = {(a_, r): np.zeros(N_CHUNKS) for a_ in ARMS for r in RHO_LIST}
    fcorr_pool_chunks = {r: np.zeros(N_CHUNKS) for r in RHO_LIST}
    fcorr_r6_chunks = {r: np.zeros(N_CHUNKS) for r in RHO_LIST}
    sA_all = np.empty(N_SUITES)
    chunk0_hash_A = None
    chunk0_hash_min = None
    rho1_bitwise_ok = True

    cs, _ = spawn_all(MASTER_SEED)
    for c, ss in enumerate(cs):
        scoreA, out, fcorr = run_chunk(ss)
        sA_all[c * CHUNK:(c + 1) * CHUNK] = scoreA
        for T in THRESH:
            pA_chunks[T][c] = (scoreA < T).mean()
        for (a_, rho), sB in out.items():
            mn = np.minimum(scoreA, sB)
            for T in THRESH:
                pB_chunks[(a_, rho)][T][c] = (sB < T).mean()
                pmin_chunks[(a_, rho)][T][c] = (mn < T).mean()
            scorr_chunks[(a_, rho)][c] = np.corrcoef(scoreA, sB)[0, 1]
        for rho in RHO_LIST:
            fcorr_pool_chunks[rho][c] = fcorr[rho][0]
            fcorr_r6_chunks[rho][c] = fcorr[rho][1]
        if not np.array_equal(out[("same_mean", 1.0)], scoreA):
            rho1_bitwise_ok = False
        if c == 0:
            chunk0_hash_A = hashlib.sha256(scoreA.tobytes()).hexdigest()
            chunk0_hash_min = hashlib.sha256(
                np.minimum(scoreA, out[("same_mean", 0.3)]).tobytes()).hexdigest()

    # bitwise repeat of chunk 0
    cs_rep, ps_rep = spawn_all(MASTER_SEED)
    assert np.array_equal(build_fbar6(ps_rep), fbar6_sorted)
    scoreA_rep, out_rep, _ = run_chunk(cs_rep[0])
    rep_ok = (hashlib.sha256(scoreA_rep.tobytes()).hexdigest() == chunk0_hash_A and
              hashlib.sha256(np.minimum(scoreA_rep, out_rep[("same_mean", 0.3)])
                             .tobytes()).hexdigest() == chunk0_hash_min)

    def stat(v):
        m = float(v.mean())
        se = float(v.std(ddof=1) / np.sqrt(N_CHUNKS))
        return {"value": m, "se": se, "ci95": [m - 1.96 * se, m + 1.96 * se]}

    sd_A = float(sA_all.std(ddof=1))
    harness = {
        "scoreA_mean": float(sA_all.mean()),
        "scoreA_sd": sd_A,
        "sd_analytic": arm["sd_analytic"],
        "sd_ratio_vs_analytic": sd_A / arm["sd_analytic"],
        "s1_sd_ref": S1_SD_REF,
        "sd_ratio_vs_s1": sd_A / S1_SD_REF,
        "pA_below_1p6em7": float(pA_chunks[1.6e-7].mean()),
        "s1_pA_below_1p6em7_ref": S1_P16_REF,
    }

    grid = {}
    for a_ in ARMS:
        grid[a_] = {}
        for rho in RHO_LIST:
            grid[a_][f"{rho:.1f}"] = {
                "rho_pair": rho,
                "p_min_below": {tkey(T): stat(pmin_chunks[(a_, rho)][T]) for T in THRESH},
                "p_B_below": {tkey(T): stat(pB_chunks[(a_, rho)][T]) for T in THRESH},
                "score_corr_AB": stat(scorr_chunks[(a_, rho)]),
            }

    baseline = {tkey(T): stat(pA_chunks[T]) for T in THRESH}

    gains = {}
    for a_ in ARMS:
        gains[a_] = {tkey(T): stat(pmin_chunks[(a_, 0.0)][T] - pmin_chunks[(a_, 1.0)][T])
                     for T in THRESH}

    gate_details, survive = {}, False
    for a_ in GATE_ARMS:
        for T in THRESH:
            g = gains[a_][tkey(T)]["value"]
            ok = g >= GATE_PP
            gate_details[f"{a_}@{tkey(T)}"] = {"gain": g, "threshold": GATE_PP, "meets": bool(ok)}
            survive = survive or ok

    # ---- Door B / Door A union factors (the mined falsifier's report) ----
    union = {}
    for a_ in ("same_mean", "sens_fold3cap"):
        union[a_] = {}
        for T in THRESH:
            ratio_c = pmin_chunks[(a_, 0.0)][T] / pA_chunks[T]
            u = stat(ratio_c)          # chunk-paired mean-of-ratios (CI source)
            u["estimator"] = "mean of 10 per-chunk ratios pmin_c/pA_c (CI source)"
            u["p_min_rho0"] = float(pmin_chunks[(a_, 0.0)][T].mean())
            u["pA"] = float(pA_chunks[T].mean())
            u["pB"] = float(pB_chunks[(a_, 0.0)][T].mean())
            u["U_pooled"] = u["p_min_rho0"] / u["pA"]   # matches the committed headline
            u["p_both"] = u["pA"] + u["pB"] - u["p_min_rho0"]
            u["pA_times_pB"] = u["pA"] * u["pB"]
            # exact finite-sample bound: P(both) >= pA*pB (Harris/FKG, both tail
            # events decreasing in the SHARED difficulty vector D), hence
            # U = pmin/pA <= 1 + (pB/pA)(1-pA).  The equal-marginal form 2-pA
            # only holds when pB == pA exactly; in a finite sample pA and pB
            # differ by MC noise, so the two-marginal form is the honest bound.
            u["union_bound_two_marginal"] = 1.0 + (u["pB"] / u["pA"]) * (1.0 - u["pA"])
            u["equal_marginal_bound_2_minus_pA"] = 2.0 - u["pA"]
            u["respects_union_bound"] = bool(u["U_pooled"] <= u["union_bound_two_marginal"] + 1e-12)
            union[a_][tkey(T)] = u

    indep_check = {}
    for a_ in ARMS:
        indep_check[a_] = {}
        for T in THRESH:
            pA = float(pA_chunks[T].mean())
            pB = float(pB_chunks[(a_, 0.0)][T].mean())
            prod = 1.0 - (1.0 - pA) * (1.0 - pB)
            sim = float(pmin_chunks[(a_, 0.0)][T].mean())
            indep_check[a_][tkey(T)] = {"independence_product": prod, "simulated": sim,
                                        "gap": sim - prod}

    return {
        "vD": arm["vD"], "diff_ratio": arm["ratio"], "vD_source": arm["source"],
        "corr_analytic_eq1": arm["corr_analytic_eq1"],
        "harness": harness,
        "single_designation_baseline_pA_below": baseline,
        "grid": grid,
        "diversification_gains_rho0_minus_rho1": gains,
        "s4_gate": {"details": gate_details, "verdict": "SURVIVES" if survive else "KILL"},
        "union_factor": union,
        "crosschecks": {
            "rho1_same_mean_bitwise_equals_A": bool(rho1_bitwise_ok),
            "bitwise_repeat_chunk0": bool(rep_ok),
            "rho0_independence_product_vs_sim": indep_check,
            "factor_corr_pool_marginal": {f"{r:.1f}": float(fcorr_pool_chunks[r].mean()) for r in RHO_LIST},
            "factor_corr_r6_marginal": {f"{r:.1f}": float(fcorr_r6_chunks[r].mean()) for r in RHO_LIST},
            "score_corr_rho0_sim_vs_eq1": {
                "sim": float(scorr_chunks[("same_mean", 0.0)].mean()),
                "analytic": arm["corr_analytic_eq1"],
            },
        },
        "chunk0_sha256_scoreA": chunk0_hash_A,
    }


# ---------------- SIGNAL 2: independent S1-style integer-index path ----------
def independent_path(arm):
    half, d_mean = arm["half"], arm["d_mean"]
    root = np.random.SeedSequence(IND_MASTER_SEED)
    seeds = root.spawn(IND_N_CHUNKS)
    ch = IND_N_SUITES // IND_N_CHUNKS
    pA_c = {T: np.zeros(IND_N_CHUNKS) for T in THRESH}
    pmin_c = {T: np.zeros(IND_N_CHUNKS) for T in THRESH}
    pminA_c = {T: np.zeros(IND_N_CHUNKS) for T in THRESH}   # Door A (1.41e-7 B)
    corr_c = np.zeros(IND_N_CHUNKS)
    for c, ss in enumerate(seeds):
        rng = np.random.default_rng(ss)
        iA = rng.integers(0, pool.size, size=(ch, N_NETS))
        iB = rng.integers(0, pool.size, size=(ch, N_NETS))
        D = np.exp(rng.uniform(-half, half, size=(ch, N_NETS))) / d_mean
        sA = ANCHOR * (D * pool[iA]).mean(axis=1)
        base = (D * pool[iB]).mean(axis=1)
        sB = ANCHOR * base
        sB_fold3 = 1.41e-7 * base
        mn = np.minimum(sA, sB)
        mnA = np.minimum(sA, sB_fold3)
        for T in THRESH:
            pA_c[T][c] = (sA < T).mean()
            pmin_c[T][c] = (mn < T).mean()
            pminA_c[T][c] = (mnA < T).mean()
        corr_c[c] = np.corrcoef(sA, sB)[0, 1]

    def stat(v):
        m = float(v.mean())
        se = float(v.std(ddof=1) / np.sqrt(IND_N_CHUNKS))
        return {"value": m, "se": se, "ci95": [m - 1.96 * se, m + 1.96 * se]}

    out = {"n_suites": IND_N_SUITES, "master_seed": IND_MASTER_SEED,
           "path": "S1-style direct integer indexing of the pool (no copula, no ndtr)",
           "score_corr_AB": stat(corr_c), "corr_analytic_eq1": arm["corr_analytic_eq1"],
           "pA_below": {tkey(T): stat(pA_c[T]) for T in THRESH},
           "union_factor_doorB": {}, "union_factor_doorA": {}}
    for T in THRESH:
        u = stat(pmin_c[T] / pA_c[T])
        u["p_min_rho0"] = float(pmin_c[T].mean())
        u["pA"] = float(pA_c[T].mean())
        u["U_pooled"] = u["p_min_rho0"] / u["pA"]
        out["union_factor_doorB"][tkey(T)] = u
        ua = stat(pminA_c[T] / pA_c[T])
        ua["p_min_rho0"] = float(pminA_c[T].mean())
        ua["pA"] = float(pA_c[T].mean())
        ua["U_pooled"] = ua["p_min_rho0"] / ua["pA"]
        out["union_factor_doorA"][tkey(T)] = ua
    return out


# ---------------- STEP 0 (blocking): control arm first ----------------
step0 = {"checks": {}, "pass": True}


def chk(label, got, ref, tol):
    ok = abs(got - ref) <= tol
    step0["checks"][label] = {"got": got, "committed": ref, "abs_diff": abs(got - ref),
                              "tol": tol, "ok": bool(ok)}
    if not ok:
        step0["pass"] = False


def one_arm(name, arm):
    out = run_arm(arm)
    out["independent_path_signal2"] = independent_path(arm)
    u = out["union_factor"]["same_mean"][tkey(PRIMARY_T)]
    u2 = out["independent_path_signal2"]["union_factor_doorB"][tkey(PRIMARY_T)]
    print(f"{name}: vD={arm['vD']:.6g} ratio={arm['ratio']:.6g} | "
          f"pA(1.55e-7)={u['pA']:.5f} pmin={u['p_min_rho0']:.5f} "
          f"U={u['value']:.4f} (se {u['se']:.4f}) | signal2 U={u2['value']:.4f} "
          f"(se {u2['se']:.4f}) | corr sim={out['crosschecks']['score_corr_rho0_sim_vs_eq1']['sim']:.5f} "
          f"eq1={arm['corr_analytic_eq1']:.5f} [{time.time()-t0:.1f}s]", flush=True)
    return out


arms_out = {"old_control": one_arm("old_control", ARM_DEFS["old_control"])}

ctrl = arms_out["old_control"]
cg = s4_committed["grid"]
cb = s4_committed["single_designation_baseline_pA_below"]
for T in THRESH:
    chk(f"baseline_pA@{tkey(T)}", ctrl["single_designation_baseline_pA_below"][tkey(T)]["value"],
        cb[tkey(T)]["value"], 0.0)
for a_ in ARMS:
    for rho in ("0.0", "1.0"):
        for T in THRESH:
            chk(f"pmin_{a_}_rho{rho}@{tkey(T)}",
                ctrl["grid"][a_][rho]["p_min_below"][tkey(T)]["value"],
                cg[a_][rho]["p_min_below"][tkey(T)]["value"], 0.0)
chk("scoreA_sd", ctrl["harness"]["scoreA_sd"],
    s4_committed["harness_check_s1_reproduction"]["scoreA_sd"], 1e-12 * 1.6e-8)
chk("scoreA_mean", ctrl["harness"]["scoreA_mean"],
    s4_committed["harness_check_s1_reproduction"]["scoreA_mean"], 1e-12 * 1.9e-7)
chk("score_corr_same_mean_rho0", ctrl["grid"]["same_mean"]["0.0"]["score_corr_AB"]["value"],
    cg["same_mean"]["0.0"]["score_corr_AB"]["value"], 1e-12)
chk("gain_same_mean@1.55e-07", ctrl["diversification_gains_rho0_minus_rho1"]["same_mean"]["1.55e-07"]["value"],
    s4_committed["diversification_gains_rho0_minus_rho1"]["same_mean"]["1.55e-07"]["value"], 0.0)

print("STEP 0 control reproduction:", "PASS" if step0["pass"] else "FAIL", flush=True)
if not step0["pass"]:
    for k, v in step0["checks"].items():
        if not v["ok"]:
            print("  MISMATCH", k, v, flush=True)
    print("STEP 0 FAILED -> corrected arms are still run for the record, but no "
          "corrected number is quoted as a verdict.", flush=True)

for name in ("vd_s17_low", "vd_s17_high"):
    arms_out[name] = one_arm(name, ARM_DEFS[name])

# ---------------- PRIMARY GATE (PREDECLARATION section 5) ----------------
# "KILL_CONFIRMED iff U(1.55e-7) >= 1.95 at BOTH vD values; REVIVED_PASS iff
#  U < 1.95 at at least one; INCONCLUSIVE if the DECIDING arm's 95% CI on U
#  straddles 1.95."  For a disjunctive REVIVED_PASS the deciding arm is the one
#  with the smallest U (the arm that establishes "< 1.95"); for KILL_CONFIRMED
#  both arms decide.
u_lo = arms_out["vd_s17_low"]["union_factor"]["same_mean"][tkey(PRIMARY_T)]
u_hi = arms_out["vd_s17_high"]["union_factor"]["same_mean"][tkey(PRIMARY_T)]
both_ge = (u_lo["value"] >= KILL_FACTOR) and (u_hi["value"] >= KILL_FACTOR)
deciding = min((u_lo, u_hi), key=lambda c: c["value"])
deciding_name = "vd_s17_low" if deciding is u_lo else "vd_s17_high"


def ci_clean_of(c):
    return (c["ci95"][1] < KILL_FACTOR) or (c["ci95"][0] > KILL_FACTOR)


if not step0["pass"]:
    gate = "INCONCLUSIVE_STEP0_FAILED"
elif both_ge:
    gate = "KILL_CONFIRMED" if all(ci_clean_of(c) for c in (u_lo, u_hi)) else "INCONCLUSIVE"
elif ci_clean_of(deciding):
    gate = "REVIVED_PASS"
else:
    gate = "INCONCLUSIVE"

s2_lo = arms_out["vd_s17_low"]["independent_path_signal2"]["union_factor_doorB"][tkey(PRIMARY_T)]
s2_hi = arms_out["vd_s17_high"]["independent_path_signal2"]["union_factor_doorB"][tkey(PRIMARY_T)]
gate_audit = {
    "deciding_arm": deciding_name,
    "deciding_U": deciding["value"],
    "deciding_ci95": deciding["ci95"],
    "deciding_ci_clean_of_1.95": bool(ci_clean_of(deciding)),
    "both_arms_ge_1.95_pointwise": bool(both_ge),
    "U_pooled_estimator_low": u_lo["U_pooled"],
    "U_pooled_estimator_high": u_hi["U_pooled"],
    "signal2_1e6_U_low": s2_lo["value"], "signal2_1e6_ci95_low": s2_lo["ci95"],
    "signal2_1e6_U_high": s2_hi["value"], "signal2_1e6_ci95_high": s2_hi["ci95"],
    "signal2_ci_clean_both_arms": bool(ci_clean_of(s2_lo) and ci_clean_of(s2_hi)),
    "signal1_vs_signal2_agree_low": bool(
        abs(u_lo["value"] - s2_lo["value"]) <= 1.96 * math.hypot(u_lo["se"], s2_lo["se"])),
    "signal1_vs_signal2_agree_high": bool(
        abs(u_hi["value"] - s2_hi["value"]) <= 1.96 * math.hypot(u_hi["se"], s2_hi["se"])),
}

committed_U = {tkey(T): (s4_committed["grid"]["same_mean"]["0.0"]["p_min_below"][tkey(T)]["value"] /
                         s4_committed["single_designation_baseline_pA_below"][tkey(T)]["value"])
               for T in THRESH}

results = {
    "experiment": "gm_u9_s4_d2",
    "date": "2026-08-10",
    "parent": "s4_portfolio/run_s4.py (copied; ONLY dispersion parameter varied; ndtr substituted)",
    "revival_item": "U9 designation refresh + S4 portfolio pass D2 under S1b corrected dispersion",
    "gate_rule": ("KILL_CONFIRMED (S4 D2 stands) iff Door B union factor "
                  "U(1.55e-7) >= 1.95 at BOTH vD=0.0813595 and vD=0.1220393; "
                  "else REVIVED_PASS if both CIs are clean of 1.95; else INCONCLUSIVE. "
                  "STEP 0 control reproduction is blocking."),
    "gate_result": gate,
    "gate_audit": gate_audit,
    "step0_control_gate": step0,
    "primary_numbers": {
        "committed_union_factor_doorB": committed_U,
        "vd_s17_low_U_1p55em7": u_lo,
        "vd_s17_high_U_1p55em7": u_hi,
        "kill_factor": KILL_FACTOR,
    },
    "design": {
        "n_suites": N_SUITES, "n_nets_per_suite": N_NETS, "n_chunks": N_CHUNKS,
        "anchor_suite_mean_A": ANCHOR, "rho_list": RHO_LIST, "thresholds": THRESH,
        "arms": {a: {"scale": s, "marginal": m} for a, (s, m) in ARMS.items()},
        "master_seed": MASTER_SEED,
        "dispersion_arms": {n: {"vD": a["vD"], "diff_ratio": a["ratio"], "source": a["source"]}
                            for n, a in ARM_DEFS.items()},
        "deviation_ndtr": "scipy absent in pinned interpreter; Cephes-shaped ndtr on libm erf/erfc",
    },
    "calibration": {"pool_n": int(pool.size), "vF": vF, "vF6_presample": vF6,
                    "vF_over_6": vF / 6.0},
    "arms": arms_out,
    "runtime_seconds": round(time.time() - t0, 1),
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=1)

print("GATE:", gate, "| deciding arm:", gate_audit["deciding_arm"],
      "U=%.4f CI %s" % (gate_audit["deciding_U"], gate_audit["deciding_ci95"]))
for n in ARM_DEFS:
    a = arms_out[n]
    print(f"  {n}: vD={a['vD']:.6g} S4gate={a['s4_gate']['verdict']} "
          f"gain@1.55e-7={a['diversification_gains_rho0_minus_rho1']['same_mean']['1.55e-07']['value']*100:.2f}pp "
          f"U_pooled(1.55/1.60/1.70e-7)="
          f"{a['union_factor']['same_mean']['1.55e-07']['U_pooled']:.5f}/"
          f"{a['union_factor']['same_mean']['1.60e-07']['U_pooled']:.5f}/"
          f"{a['union_factor']['same_mean']['1.70e-07']['U_pooled']:.5f} "
          f"bound_ok={a['union_factor']['same_mean']['1.55e-07']['respects_union_bound']}")
print("wrote", OUT_JSON, f"[{time.time()-t0:.1f}s]")
