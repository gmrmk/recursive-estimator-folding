"""gm_s1s4_vd — COPY of experiments/s4_portfolio/run_s4.py, multi-arm in vD.

ONLY the difficulty variance vD changes (log-uniform half-width solved per arm).
Anchor, pool, copula, rho grid, thresholds, arms, chunking and MASTER_SEED are
byte-identical to the committed harness; each vD arm re-derives the seed layout
from scratch, so all arms share common random numbers.

Door-B (S4 ledger, "CONCRETE LEGAL CONSTRUCTION"): two designations of the SAME
validated estimator differing only in the participant-owned rotation-seed
constant. In this harness that is rho_pair = 0.0 with the net-difficulty factor D
SHARED. The quantity of interest is therefore
    gain(T) = P(min < T | rho=0) - P(min < T | rho=1)
and the "doubling" claim is  P(min<T|rho=0) / P(min<T|rho=1) >= 1.9.
The residual score correlation at rho=0 is the shared-difficulty floor that no
seed choice can remove; it rises with vD, which is what this re-run measures.

The original file is NOT modified.
"""
import json, hashlib, time, os
import numpy as np
from ndtr_numpy import ndtr   # DEVIATION D5: pinned interpreter has no scipy;
# Cody CALERF reimplementation, validated vs math.erfc in ndtr_validation.json
# (max rel diff 9.5e-15). Acceptance test = control arm vs committed s4_results.json.

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
EXP = os.path.join(ROOT, "corpus", "whestbench", "experiments")
P2_PATH = os.path.join(EXP, "pb1_premise_battery", "p2_results.json")
S4_COMMITTED = os.path.join(EXP, "s4_portfolio", "s4_results.json")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "s4_gm_results.json")

ANCHOR = 1.83e-7
N_SUITES = 100_000
N_NETS = 50
N_CHUNKS = 10
RHO_LIST = [0.0, 0.3, 0.6, 0.9, 1.0]
THRESH = [1.55e-7, 1.6e-7, 1.7e-7]
ARMS = {"same_mean": (1.83e-7, "pool"), "l2": (2.10e-7, "pool"),
        "r6": (1.83e-7, "fbar6"), "sens_fold3cap": (1.41e-7, "pool")}
GATE_ARMS = ["same_mean", "r6"]
GATE_PP = 0.02
N_FBAR6_PRESAMPLE = 1 << 20
MASTER_SEED = 202608094
S1_SD_REF = 1.562588338576902e-08
S1_P16_REF = 0.06434

t0 = time.time()

p2 = json.load(open(P2_PATH))
pool_parts = []
for seed, rec in sorted(p2["q1_oracle_headroom"]["per_net"].items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    pool_parts.append(m / m.mean())
pool = np.concatenate(pool_parts)
pool = pool / pool.mean()
pool_sorted = np.sort(pool)
vF = float(pool.var())


def vd_of_half(half):
    d_mean = np.sinh(half) / half
    return float((np.sinh(2 * half) / (2 * half)) / d_mean ** 2 - 1.0)

def half_for_vd(target):
    lo, hi = 1e-9, 0.1
    while vd_of_half(hi) < target:
        hi *= 1.5
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if vd_of_half(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

s0 = json.load(open(os.path.join(HERE, "step0_results.json")))
ARMS_VD = {
    "control_1.1x": ("half", np.log(1.1) / 2.0),
    "vD_moment_raw": ("vd", s0["moment_identity"]["raw"]["ddof1"]["vD_moment"]),
    "vD_moment_corr": ("vd", s0["moment_identity"]["corr_floor_subtracted"]["ddof1"]["vD_moment"]),
    "s1b_s17_low_0.0814": ("vd", 0.0814),
    "s1b_s17_high_0.1220": ("vd", 0.1220),
}

def spawn_all(master):
    root = np.random.SeedSequence(master)
    ss = root.spawn(N_CHUNKS + 1)
    return ss[:N_CHUNKS], ss[N_CHUNKS]

def build_fbar6(seedseq):
    rng = np.random.default_rng(seedseq)
    idx = rng.integers(0, pool.size, size=(N_FBAR6_PRESAMPLE, 6))
    fb = pool[idx].mean(axis=1)
    fb /= fb.mean()
    return np.sort(fb)

def qmap(U, sorted_vals):
    idx = np.minimum((U * sorted_vals.size).astype(np.int64), sorted_vals.size - 1)
    return sorted_vals[idx]

CHUNK = N_SUITES // N_CHUNKS
tkey = lambda T: f"{T:.2e}"


def run_family(half):
    d_mean = np.sinh(half) / half
    vD = vd_of_half(half)
    SD_ANALYTIC = ANCHOR * np.sqrt((vD + (1 + vD) * vF) / N_NETS)

    def draw_D(rng, shape):
        return np.exp(rng.uniform(-half, half, size=shape)) / d_mean

    chunk_seeds, presample_seed = spawn_all(MASTER_SEED)
    fbar6_sorted = build_fbar6(presample_seed)

    def run_chunk(seedseq):
        rng = np.random.default_rng(seedseq)
        Z_A = rng.standard_normal((CHUNK, N_NETS))
        W = rng.standard_normal((CHUNK, N_NETS))
        D = draw_D(rng, (CHUNK, N_NETS))
        F_A = qmap(ndtr(Z_A), pool_sorted)
        scoreA = ANCHOR * (D * F_A).mean(axis=1)
        out = {}
        for rho in RHO_LIST:
            Z_B = rho * Z_A + np.sqrt(1.0 - rho * rho) * W
            U_B = ndtr(Z_B)
            base_pool = (D * qmap(U_B, pool_sorted)).mean(axis=1)
            base_r6 = (D * qmap(U_B, fbar6_sorted)).mean(axis=1)
            for arm, (S_B, marg) in ARMS.items():
                out[(arm, rho)] = S_B * (base_pool if marg == "pool" else base_r6)
        return scoreA, out

    pA_chunks = {T: np.zeros(N_CHUNKS) for T in THRESH}
    pmin_chunks = {(a, r): {T: np.zeros(N_CHUNKS) for T in THRESH}
                   for a in ARMS for r in RHO_LIST}
    scorr_chunks = {(a, r): np.zeros(N_CHUNKS) for a in ARMS for r in RHO_LIST}
    sA_all = np.empty(N_SUITES)
    chunk0_hash_A = None
    chunk0_hash_min = None
    rho1_bitwise_ok = True
    for c, ss in enumerate(chunk_seeds):
        scoreA, out = run_chunk(ss)
        sA_all[c * CHUNK:(c + 1) * CHUNK] = scoreA
        for T in THRESH:
            pA_chunks[T][c] = (scoreA < T).mean()
        for (arm, rho), sB in out.items():
            mn = np.minimum(scoreA, sB)
            for T in THRESH:
                pmin_chunks[(arm, rho)][T][c] = (mn < T).mean()
            scorr_chunks[(arm, rho)][c] = np.corrcoef(scoreA, sB)[0, 1]
        if not np.array_equal(out[("same_mean", 1.0)], scoreA):
            rho1_bitwise_ok = False
        if c == 0:
            chunk0_hash_A = hashlib.sha256(scoreA.tobytes()).hexdigest()
            chunk0_hash_min = hashlib.sha256(
                np.minimum(scoreA, out[("same_mean", 0.3)]).tobytes()).hexdigest()

    # bitwise repeat of chunk 0
    cs_rep, ps_rep = spawn_all(MASTER_SEED)
    assert np.array_equal(build_fbar6(ps_rep), fbar6_sorted)
    sA_rep, out_rep = run_chunk(cs_rep[0])
    rep_ok = (hashlib.sha256(sA_rep.tobytes()).hexdigest() == chunk0_hash_A and
              hashlib.sha256(np.minimum(sA_rep, out_rep[("same_mean", 0.3)]).tobytes()
                             ).hexdigest() == chunk0_hash_min)

    def stat(v):
        m = float(v.mean()); se = float(v.std(ddof=1) / np.sqrt(N_CHUNKS))
        return {"value": m, "se": se, "ci95": [m - 1.96 * se, m + 1.96 * se]}

    gains, ratios, pmin_tab = {}, {}, {}
    for arm in ARMS:
        gains[arm], ratios[arm], pmin_tab[arm] = {}, {}, {}
        for T in THRESH:
            d = pmin_chunks[(arm, 0.0)][T] - pmin_chunks[(arm, 1.0)][T]
            gains[arm][tkey(T)] = stat(d)
            p0 = float(pmin_chunks[(arm, 0.0)][T].mean())
            p1 = float(pmin_chunks[(arm, 1.0)][T].mean())
            ratios[arm][tkey(T)] = {"p_rho0": p0, "p_rho1": p1,
                                    "ratio": (p0 / p1) if p1 > 0 else None,
                                    "doubling_claim_holds": bool(p1 > 0 and p0 / p1 >= 1.9)}
            pmin_tab[arm][tkey(T)] = {f"{r:.1f}": float(pmin_chunks[(arm, r)][T].mean())
                                      for r in RHO_LIST}

    survive = any(gains[a][tkey(T)]["value"] >= GATE_PP for a in GATE_ARMS for T in THRESH)
    return {
        "vD": vD, "difficulty_half_width": half,
        "difficulty_max_over_min": float(np.exp(2 * half)),
        "verdict": "SURVIVES" if survive else "KILL",
        "scoreA_mean": float(sA_all.mean()), "scoreA_sd": float(sA_all.std(ddof=1)),
        "sd_analytic": float(SD_ANALYTIC),
        "sd_ratio_vs_analytic": float(sA_all.std(ddof=1) / SD_ANALYTIC),
        "pA_below": {tkey(T): stat(pA_chunks[T]) for T in THRESH},
        "diversification_gains_rho0_minus_rho1": gains,
        "doubling_ratio_rho0_over_rho1": ratios,
        "p_min_below_by_rho": pmin_tab,
        "score_corr_AB": {a: {f"{r:.1f}": stat(scorr_chunks[(a, r)])["value"]
                              for r in RHO_LIST} for a in ARMS},
        "shared_difficulty_correlation_floor_same_mean_rho0":
            float(scorr_chunks[("same_mean", 0.0)].mean()),
        "analytic_share_D": float(vD / (vD + (1 + vD) * vF)),
        "rho1_same_mean_bitwise_equals_A": bool(rho1_bitwise_ok),
        "bitwise_repeat_chunk0": bool(rep_ok),
        "chunk0_sha256_scoreA": chunk0_hash_A,
    }


results = {"experiment": "gm_s1s4_vd_s4_rerun", "source_harness": "s4_portfolio/run_s4.py",
           "changed": "difficulty variance vD only", "calibration": {"vF": vF, "pool_n": int(pool.size)},
           "design": {"n_suites": N_SUITES, "n_nets": N_NETS, "rho_list": RHO_LIST,
                      "thresholds": THRESH, "master_seed": MASTER_SEED},
           "arms": {}}

for name, (kind, val) in ARMS_VD.items():
    half = val if kind == "half" else half_for_vd(val)
    r = run_family(half)
    results["arms"][name] = r
    g = r["diversification_gains_rho0_minus_rho1"]["same_mean"]
    d = r["doubling_ratio_rho0_over_rho1"]["same_mean"]
    print("%-22s vD=%.6f  share_D=%.4f  rho0_scorecorr=%.4f | gains same_mean "
          "1.55=%.2fpp 1.60=%.2fpp 1.70=%.2fpp | ratio@1.6=%.3f  verdict=%s [%.1fs]"
          % (name, r["vD"], r["analytic_share_D"],
             r["shared_difficulty_correlation_floor_same_mean_rho0"],
             g["1.55e-07"]["value"] * 100, g["1.60e-07"]["value"] * 100,
             g["1.70e-07"]["value"] * 100, d["1.60e-07"]["ratio"], r["verdict"],
             time.time() - t0), flush=True)

# ------------------- V1: control reproduces the committed S4 run -------------
c = json.load(open(S4_COMMITTED))
ctl = results["arms"]["control_1.1x"]
detail, ok = {}, True
for T in ["1.55e-07", "1.60e-07", "1.70e-07"]:
    mine = ctl["diversification_gains_rho0_minus_rho1"]["same_mean"][T]["value"]
    ref = c["diversification_gains_rho0_minus_rho1"]["same_mean"][T]["value"]
    good = abs(mine - ref) < 1e-12
    detail["gain_same_mean_" + T] = {"mine": mine, "committed": ref, "identical_1e-12": good}
    ok = ok and good
mine_sd = ctl["scoreA_sd"]; ref_sd = c["harness_check_s1_reproduction"]["scoreA_sd"]
detail["scoreA_sd"] = {"mine": mine_sd, "committed": ref_sd,
                       "rel_diff": abs(mine_sd / ref_sd - 1)}
ok = ok and abs(mine_sd / ref_sd - 1) < 1e-12
detail["scoreA_sd_vs_s1_bootstrap_ratio"] = mine_sd / S1_SD_REF
results["V1_control_reproduces_committed_s4"] = {"all_pass": bool(ok), "checks": detail}
results["runtime_seconds"] = round(time.time() - t0, 1)
json.dump(results, open(OUT_JSON, "w"), indent=1)
print("V1 control reproduction of committed s4_results.json:", ok)
for k, v in detail.items():
    print("   ", k, v)
print("wrote", OUT_JSON, "[%.1fs]" % (time.time() - t0))
