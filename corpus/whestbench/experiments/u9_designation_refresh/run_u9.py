"""U9 designation-threshold refresh (analysis for the Sep 19 slot decision; NOT
a submission). Reuses the COMMITTED S1 suite-risk and S4 portfolio bootstrap
machinery verbatim (same model, same seeds), extending the reported threshold
grid to the CURRENT post-re-grade board:

    T in {5e-8, 7.5e-8, 1.0e-7, 1.3e-7, 1.55e-7, 1.6e-7}

Task 1 (S1 model): P(champion suite-score < T) for R in {1,2,4,6}, anchored at
                   the current hosted champion 1.83e-7 adjusted.
Task 2 (S4 model): P(min(A,B) < T) for
                   Door B = champion + decorrelated same-mean duplicate (rho=0.0,
                            score corr ~0.2%), and
                   Door A = champion + fold3cap (mean 1.41e-7, rho=0.0),
                   vs the single-designation baseline P(A<T). Shows the doubling.

Cross-check (two-signal rule): identical seeds to the committed runs, so at the
OVERLAPPING thresholds the re-run must reproduce the committed numbers:
    S1  P(<1.6e-7) R=1 == 0.06434 ; R=6 == 0.0001 ; P(<1.0e-7) == 0.0 (all R)
    S4  baseline P(A<1.6e-7)      == 0.06373
        Door B  P(min<1.6e-7)    == 0.12373 ; P(min<1.55e-7) == 0.05701
        Door A  P(min<1.6e-7)    == 0.93972 ; P(min<1.55e-7) == 0.87683
Any mismatch aborts (assert), proving the re-run rides the committed machinery.
"""
import json
import time
import numpy as np
from scipy.special import ndtr

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
P2_PATH = ROOT + r"\corpus\whestbench\experiments\pb1_premise_battery\p2_results.json"
OUT_JSON = ROOT + r"\corpus\whestbench\experiments\u9_designation_refresh\u9_tables.json"

ANCHOR = 1.83e-7            # current hosted champion, adjusted
N_SUITES = 100_000
N_NETS = 50
N_CHUNKS = 10
DIFF_RATIO = 1.1
# CURRENT honest-band + near-rival threshold grid (was {1.6e-7,1.0e-7} in S1)
THRESH = [5.0e-8, 7.5e-8, 1.0e-7, 1.3e-7, 1.55e-7, 1.6e-7]
R_LIST = [1, 2, 4, 6]
S1_MASTER_SEED = 20260809          # identical to committed S1
S4_MASTER_SEED = 202608094         # identical to committed S4
FOLD3CAP_MEAN = 1.41e-7            # Door A candidate (canary-pending)

t0 = time.time()

# ================= shared calibration (identical to S1/S4) =================
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

half = np.log(DIFF_RATIO) / 2.0
d_mean = np.sinh(half) / half
vD = float((np.sinh(2 * half) / (2 * half)) / d_mean**2 - 1.0)

def draw_D(rng, shape):
    return np.exp(rng.uniform(-half, half, size=shape)) / d_mean

tkey = lambda T: f"{T:.2e}"

# ================= TASK 1: S1 suite-risk model (R-splitting) =================
# verbatim run_arm from run_s1.py, thresholds swept post-hoc on the score array.
def s1_run_arm(R, seedseq):
    chunk = N_SUITES // N_CHUNKS
    scores = np.empty(N_SUITES)
    for c, ss in enumerate(seedseq.spawn(N_CHUNKS)):
        rng = np.random.default_rng(ss)
        idx = rng.integers(0, pool.size, size=(chunk, N_NETS, R))
        Fbar = pool[idx].mean(axis=2)
        D = draw_D(rng, (chunk, N_NETS))
        sc = ANCHOR * (D * Fbar).mean(axis=1)
        scores[c * chunk:(c + 1) * chunk] = sc
    return scores

rng_root = np.random.SeedSequence(S1_MASTER_SEED)
r_seeds = {R: s for R, s in zip(R_LIST, rng_root.spawn(len(R_LIST)))}

s1_table = {}          # R -> {mean, sd, p5, p95, P(<T) for T}
for R in R_LIST:
    sc = s1_run_arm(R, r_seeds[R])
    p5, p95 = np.percentile(sc, [5, 95])
    s1_table[R] = {
        "R": R,
        "mean": float(sc.mean()),
        "sd": float(sc.std(ddof=1)),
        "p5": float(p5),
        "p95": float(p95),
        "p_below": {tkey(T): float((sc < T).mean()) for T in THRESH},
    }
    print(f"[S1] R={R}: mean={s1_table[R]['mean']:.4e} sd={s1_table[R]['sd']:.3e} "
          f"P(<1.6e-7)={s1_table[R]['p_below']['1.60e-07']:.5f} [{time.time()-t0:.1f}s]",
          flush=True)

# cross-check vs committed S1
assert abs(s1_table[1]["p_below"]["1.60e-07"] - 0.06434) < 1e-9, s1_table[1]["p_below"]["1.60e-07"]
assert abs(s1_table[6]["p_below"]["1.60e-07"] - 0.0001) < 1e-9, s1_table[6]["p_below"]["1.60e-07"]
assert s1_table[1]["p_below"]["1.00e-07"] == 0.0
print("[S1] cross-check vs committed s1_results.json: PASS", flush=True)

# ================= TASK 2: S4 portfolio model (copula pairs) =================
# verbatim run_chunk from run_s4.py, restricted to the two decision arms at rho=0.
def qmap(U, sorted_vals):
    idx = np.minimum((U * sorted_vals.size).astype(np.int64), sorted_vals.size - 1)
    return sorted_vals[idx]

CHUNK = N_SUITES // N_CHUNKS
chunk_seeds = np.random.SeedSequence(S4_MASTER_SEED).spawn(N_CHUNKS + 1)[:N_CHUNKS]

# accumulate scores across chunks
sA_all = np.empty(N_SUITES)
sB_dup_all = np.empty(N_SUITES)      # Door B: same-mean decorrelated duplicate (rho=0)
sB_f3c_all = np.empty(N_SUITES)      # Door A: fold3cap 1.41e-7 (rho=0)
scorr_dup = np.zeros(N_CHUNKS)
scorr_f3c = np.zeros(N_CHUNKS)

for c, ss in enumerate(chunk_seeds):
    rng = np.random.default_rng(ss)
    Z_A = rng.standard_normal((CHUNK, N_NETS))
    W = rng.standard_normal((CHUNK, N_NETS))
    D = draw_D(rng, (CHUNK, N_NETS))
    F_A = qmap(ndtr(Z_A), pool_sorted)
    scoreA = ANCHOR * (D * F_A).mean(axis=1)
    # rho = 0.0  =>  Z_B = W  (independent draw), shared D (same 50 nets)
    U_B = ndtr(W)
    F_B_pool = qmap(U_B, pool_sorted)
    base_pool = (D * F_B_pool).mean(axis=1)
    scoreB_dup = ANCHOR * base_pool
    scoreB_f3c = FOLD3CAP_MEAN * base_pool
    sl = slice(c * CHUNK, (c + 1) * CHUNK)
    sA_all[sl] = scoreA
    sB_dup_all[sl] = scoreB_dup
    sB_f3c_all[sl] = scoreB_f3c
    scorr_dup[c] = np.corrcoef(scoreA, scoreB_dup)[0, 1]
    scorr_f3c[c] = np.corrcoef(scoreA, scoreB_f3c)[0, 1]
    print(f"[S4] chunk {c} done [{time.time()-t0:.1f}s]", flush=True)

def p_stat(mask_all):
    """chunk-batched P with CI (matches S4's stat())."""
    per_chunk = mask_all.reshape(N_CHUNKS, CHUNK).mean(axis=1)
    m = float(per_chunk.mean())
    se = float(per_chunk.std(ddof=1) / np.sqrt(N_CHUNKS))
    return {"value": m, "se": se, "ci95": [m - 1.96 * se, m + 1.96 * se]}

min_dup = np.minimum(sA_all, sB_dup_all)
min_f3c = np.minimum(sA_all, sB_f3c_all)

s4_table = {"thresholds": [tkey(T) for T in THRESH]}
s4_table["baseline_single_designation_pA_below"] = {tkey(T): p_stat(sA_all < T) for T in THRESH}
s4_table["doorB_champion_plus_decorrelated_duplicate"] = {
    "score_corr_AB": float(scorr_dup.mean()),
    "p_B_below": {tkey(T): p_stat(sB_dup_all < T) for T in THRESH},
    "p_atleast_one_below (min)": {tkey(T): p_stat(min_dup < T) for T in THRESH},
}
s4_table["doorA_champion_plus_fold3cap_1p41em7"] = {
    "candidate_mean": FOLD3CAP_MEAN,
    "score_corr_AB": float(scorr_f3c.mean()),
    "p_B_below": {tkey(T): p_stat(sB_f3c_all < T) for T in THRESH},
    "p_atleast_one_below (min)": {tkey(T): p_stat(min_f3c < T) for T in THRESH},
}
# doubling factor (Door B min / baseline)
s4_table["doorB_doubling_factor_min_over_baseline"] = {
    tkey(T): (s4_table["doorB_champion_plus_decorrelated_duplicate"]["p_atleast_one_below (min)"][tkey(T)]["value"]
              / s4_table["baseline_single_designation_pA_below"][tkey(T)]["value"]
              if s4_table["baseline_single_designation_pA_below"][tkey(T)]["value"] > 0 else None)
    for T in THRESH
}

# cross-check vs committed S4
b16 = s4_table["baseline_single_designation_pA_below"]["1.60e-07"]["value"]
db16 = s4_table["doorB_champion_plus_decorrelated_duplicate"]["p_atleast_one_below (min)"]["1.60e-07"]["value"]
db155 = s4_table["doorB_champion_plus_decorrelated_duplicate"]["p_atleast_one_below (min)"]["1.55e-07"]["value"]
da16 = s4_table["doorA_champion_plus_fold3cap_1p41em7"]["p_atleast_one_below (min)"]["1.60e-07"]["value"]
da155 = s4_table["doorA_champion_plus_fold3cap_1p41em7"]["p_atleast_one_below (min)"]["1.55e-07"]["value"]
print(f"[S4] baseline P(A<1.6e-7)={b16:.5f} (committed 0.06373) | "
      f"DoorB min 1.6e-7={db16:.5f} (0.12373) 1.55e-7={db155:.5f} (0.05701) | "
      f"DoorA min 1.6e-7={da16:.5f} (0.93972) 1.55e-7={da155:.5f} (0.87683)", flush=True)
assert abs(b16 - 0.06373) < 5e-4, b16
assert abs(db16 - 0.12373) < 5e-4, db16
assert abs(db155 - 0.05701) < 5e-4, db155
assert abs(da16 - 0.93972) < 5e-3, da16
assert abs(da155 - 0.87683) < 5e-3, da155
print("[S4] cross-check vs committed s4_results.json: PASS", flush=True)

# ================= assemble & write =================
results = {
    "experiment": "u9_designation_refresh",
    "date": "2026-08-10",
    "purpose": "Refresh U9 designation thresholds on the current post-re-grade board (Sep 19 decision analysis; NOT a submission).",
    "reused_machinery": ["s1_suite_risk/run_s1.py (model+seeds)", "s4_portfolio/run_s4.py (model+seeds)"],
    "anchor_champion_adjusted": ANCHOR,
    "fold3cap_candidate_mean": FOLD3CAP_MEAN,
    "current_board_reported": {
        "rayan53_adjusted": 1.5e-9, "note_rayan53": "accounting/compute-multiplier position",
        "joe_wanza_adjusted": 2.11e-8, "note_joe_wanza": "over-budget(5.27x)+overfit",
        "honest_band_adjusted": [2.1e-8, 7.4e-8],
        "honest_band_members": {"ednacob": 4.62e-8, "dpskv5": 3.68e-8, "huang": 4.62e-8,
                                 "dstepanov": 6.0e-8, "ely2sh": 6.26e-8, "oabuod": 7.35e-8},
        "near_rival_band_adjusted": [1.55e-7, 1.6e-7],
        "near_rival_members": ["natasha", "shiv_m", "SOX"],
        "our_champion_adjusted": 1.832e-7, "our_champion_raw": 2.818e-7,
        "source": "corpus/whestbench/core/RAYAN53_FORENSICS_20260810.md + task board (reported level)",
    },
    "s17_floor": {
        "champion_over_cost_floor_x": 1.7906808367797993,
        "ednacob_below_point_floor_x": [2.214674081683319, 3.9657744377832187],
        "implication": "champion sits AT the point-eval sampling floor; the honest band (ednacob et al.) "
                       "sits 2.2-4x BELOW that floor and requires seed-side extraction we do not own. "
                       "No R-variant or portfolio move over the point-eval champion reaches the honest band.",
    },
    "task1_s1_champion_pbelow_by_R": {str(R): s1_table[R] for R in R_LIST},
    "task2_s4_portfolio": s4_table,
    "crosschecks": {
        "s1_reproduces_committed": True,
        "s4_reproduces_committed": True,
        "note": "identical seeds to committed S1/S4; overlapping thresholds match by assert.",
    },
    "runtime_seconds": round(time.time() - t0, 1),
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=1)
print("wrote", OUT_JSON, f"[{time.time()-t0:.1f}s]")
