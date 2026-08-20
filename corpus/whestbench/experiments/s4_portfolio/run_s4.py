"""S4 (ledger id s4_designation_portfolio_bootstrap): does designating TWO
DECORRELATED entries materially improve P(at least one beats threshold T)
vs designating two highly-correlated same-family entries?

Foundation: S1's per-net MSE model (corpus/whestbench/experiments/s1_suite_risk):
  per-net MSE = S * D_i * F_i
  D_i : net-difficulty factor, log-uniform max/min = 1.1, normalized to mean 1.
  F_i : rotation-draw factor from the pooled P2 empirical distribution
        (3 nets x 16 rotations, per-net mean-normalized, 48 values, mean forced
        to 1). Suite score = mean over 50 nets.
  Anchor S = 1.83e-7 => R=1 suite mean = 1.83e-7 by construction.

S4 extension — JOINT pairs (A, B) on the SAME 50-net suite:
  - D_i is SHARED between A and B (same nets by construction).
  - Rotation-draw factors are coupled through a Gaussian copula with latent
    correlation rho_pair: Z_A, W ~ iid N(0,1); Z_B = rho*Z_A + sqrt(1-rho^2)*W;
    F = Q(Phi(Z)) where Q is the empirical inverse CDF of the marginal pool.
    Marginals are therefore preserved exactly; ranks are correlated.
  - Candidate A: mean 1.83e-7, R=1 (v3.1 profile). Sampling A via the
    inverse-CDF path is distribution-identical to S1's integer-index path;
    reproducing S1's R=1 suite SD (1.563e-8) is the harness check.
  - Candidate B arms (predeclared):
      same_mean    : mean 1.83e-7, R=1 marginal (pure correlation effect)
      l2           : mean 2.10e-7, R=1 marginal (decision support only)
      r6           : mean 1.83e-7, rotation-factor variance / 6. Marginal =
                     empirical distribution of the mean of 6 iid pool draws
                     (2^20 presampled values, sorted, renormalized to mean
                     exactly 1 to keep the anchor exact); coupled to A's
                     single draw through the same copula rank.
      sens_fold3cap: mean 1.41e-7, R=1 marginal. WEAK EVIDENCE (5-net number);
                     decision support only.
  - rho_pair in {0.0, 0.3, 0.6, 0.9, 1.0}. Common random numbers (same Z_A,
    W, D) across all rhos and arms => paired gain estimates, and at rho=1.0
    the same_mean arm is bitwise identical to A (internal consistency check).

Per (arm, rho): N_SUITES joint suites; report P(min(scoreA,scoreB) < T) for
T in {1.55e-7, 1.6e-7, 1.7e-7}; P(scoreA < T) is the single-designation
baseline.

PREDECLARED GATES (gate inputs: same_mean and r6 arms ONLY):
  SURVIVE: diversification gain = P(min<T | rho=0.0) - P(min<T | rho=1.0),
           same arm, >= 2 percentage points absolute at ANY threshold in the
           same_mean or r6 arms.
  KILL   : gain < 2 points everywhere in those arms.

Cross-checks (two-signal rule):
  1. Harness check: A's R=1 suite SD vs S1 bootstrap (1.5626e-8) and analytic
     S*sqrt((vD+(1+vD)*vF)/50); P(A<1.6e-7) vs S1's 0.06434.
  2. rho=1.0 same_mean: scoreB bitwise == scoreA.
  3. rho=0.0: simulated P(min<T) vs independence product 1-(1-pA)(1-pB)
     from the same simulation's marginals (shared D leaves ~0.002 residual
     score correlation, so a small gap is expected).
  4. Bitwise repeat of chunk 0 (scoreA and one (arm,rho) min-score hash).
"""
import json
import hashlib
import time
import numpy as np
from scipy.special import ndtr

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
P2_PATH = ROOT + r"\corpus\whestbench\experiments\pb1_premise_battery\p2_results.json"
OUT_JSON = ROOT + r"\corpus\whestbench\experiments\s4_portfolio\s4_results.json"

ANCHOR = 1.83e-7
N_SUITES = 100_000
N_NETS = 50
N_CHUNKS = 10
DIFF_RATIO = 1.1
RHO_LIST = [0.0, 0.3, 0.6, 0.9, 1.0]
THRESH = [1.55e-7, 1.6e-7, 1.7e-7]
ARMS = {  # arm -> (scale S_B, marginal: "pool" or "fbar6")
    "same_mean": (1.83e-7, "pool"),
    "l2": (2.10e-7, "pool"),
    "r6": (1.83e-7, "fbar6"),
    "sens_fold3cap": (1.41e-7, "pool"),
}
GATE_ARMS = ["same_mean", "r6"]
GATE_PP = 0.02
N_FBAR6_PRESAMPLE = 1 << 20
MASTER_SEED = 202608094          # distinct from S1's 20260809
S1_SD_REF = 1.562588338576902e-08
S1_P16_REF = 0.06434

t0 = time.time()

# ---------------- calibration: rotation factor pool from P2 (same as S1) ----
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
SD_ANALYTIC = ANCHOR * np.sqrt((vD + (1 + vD) * vF) / N_NETS)

# ---------------- seeds ----------------
def spawn_all(master):
    root = np.random.SeedSequence(master)
    ss = root.spawn(N_CHUNKS + 1)
    return ss[:N_CHUNKS], ss[N_CHUNKS]

chunk_seeds, presample_seed = spawn_all(MASTER_SEED)

# ---------------- fbar6 marginal presample (R=6 variant) ----------------
def build_fbar6(seedseq):
    rng = np.random.default_rng(seedseq)
    idx = rng.integers(0, pool.size, size=(N_FBAR6_PRESAMPLE, 6))
    fb = pool[idx].mean(axis=1)
    fb /= fb.mean()              # force mean exactly 1 (keeps anchor exact)
    return np.sort(fb)

fbar6_sorted = build_fbar6(presample_seed)
vF6 = float(fbar6_sorted.var())

def qmap(U, sorted_vals):
    """Empirical inverse CDF: U in [0,1) -> sorted_vals[floor(U*n)]."""
    idx = np.minimum((U * sorted_vals.size).astype(np.int64), sorted_vals.size - 1)
    return sorted_vals[idx]

def draw_D(rng, shape):
    return np.exp(rng.uniform(-half, half, size=shape)) / d_mean

# ---------------- main loop (CRN across arms and rhos) ----------------
CHUNK = N_SUITES // N_CHUNKS

def run_chunk(seedseq):
    """One chunk: returns scoreA and {(arm, rho): scoreB} dicts."""
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
        for arm, (S_B, marg) in ARMS.items():
            out[(arm, rho)] = S_B * (base_pool if marg == "pool" else base_r6)
        fcorr[rho] = (
            float(np.corrcoef(F_A.ravel(), F_B_pool.ravel())[0, 1]),
            float(np.corrcoef(F_A.ravel(), F_B_r6.ravel())[0, 1]),
        )
    return scoreA, out, fcorr

# accumulators: per-chunk P values
pA_chunks = {T: np.zeros(N_CHUNKS) for T in THRESH}
pB_chunks = {(a, r): {T: np.zeros(N_CHUNKS) for T in THRESH}
             for a in ARMS for r in RHO_LIST}
pmin_chunks = {(a, r): {T: np.zeros(N_CHUNKS) for T in THRESH}
               for a in ARMS for r in RHO_LIST}
scorr_chunks = {(a, r): np.zeros(N_CHUNKS) for a in ARMS for r in RHO_LIST}
fcorr_pool_chunks = {r: np.zeros(N_CHUNKS) for r in RHO_LIST}
fcorr_r6_chunks = {r: np.zeros(N_CHUNKS) for r in RHO_LIST}
sA_all = np.empty(N_SUITES)
chunk0_hash_A = None
chunk0_hash_min = None          # (same_mean, rho=0.3) min-score hash
rho1_bitwise_ok = True

for c, ss in enumerate(chunk_seeds):
    scoreA, out, fcorr = run_chunk(ss)
    sA_all[c * CHUNK:(c + 1) * CHUNK] = scoreA
    for T in THRESH:
        pA_chunks[T][c] = (scoreA < T).mean()
    for (arm, rho), sB in out.items():
        mn = np.minimum(scoreA, sB)
        for T in THRESH:
            pB_chunks[(arm, rho)][T][c] = (sB < T).mean()
            pmin_chunks[(arm, rho)][T][c] = (mn < T).mean()
        scorr_chunks[(arm, rho)][c] = np.corrcoef(scoreA, sB)[0, 1]
    for rho in RHO_LIST:
        fcorr_pool_chunks[rho][c] = fcorr[rho][0]
        fcorr_r6_chunks[rho][c] = fcorr[rho][1]
    if not np.array_equal(out[("same_mean", 1.0)], scoreA):
        rho1_bitwise_ok = False
    if c == 0:
        chunk0_hash_A = hashlib.sha256(scoreA.tobytes()).hexdigest()
        mn03 = np.minimum(scoreA, out[("same_mean", 0.3)])
        chunk0_hash_min = hashlib.sha256(mn03.tobytes()).hexdigest()
    print(f"chunk {c}: done [{time.time()-t0:.1f}s]", flush=True)

# ---------------- harness check: reproduce S1 R=1 suite SD ----------------
sd_A = float(sA_all.std(ddof=1))
harness = {
    "scoreA_mean": float(sA_all.mean()),
    "scoreA_sd": sd_A,
    "s1_sd_ref": S1_SD_REF,
    "sd_ratio_vs_s1": sd_A / S1_SD_REF,
    "sd_analytic": float(SD_ANALYTIC),
    "sd_ratio_vs_analytic": sd_A / float(SD_ANALYTIC),
    "pA_below_1p6em7": float(pA_chunks[1.6e-7].mean()),
    "s1_pA_below_1p6em7_ref": S1_P16_REF,
    "pass": bool(abs(sd_A / S1_SD_REF - 1.0) < 0.02),
}

# ---------------- bitwise repeat of chunk 0 ----------------
chunk_seeds_rep, presample_seed_rep = spawn_all(MASTER_SEED)
fbar6_rep = build_fbar6(presample_seed_rep)
assert np.array_equal(fbar6_rep, fbar6_sorted)
scoreA_rep, out_rep, _ = run_chunk(chunk_seeds_rep[0])
rep_ok = (hashlib.sha256(scoreA_rep.tobytes()).hexdigest() == chunk0_hash_A and
          hashlib.sha256(np.minimum(scoreA_rep, out_rep[("same_mean", 0.3)])
                         .tobytes()).hexdigest() == chunk0_hash_min)

# ---------------- assemble grid, gains, gates ----------------
def stat(chunk_vals):
    m = float(chunk_vals.mean())
    se = float(chunk_vals.std(ddof=1) / np.sqrt(N_CHUNKS))
    return {"value": m, "se": se, "ci95": [m - 1.96 * se, m + 1.96 * se]}

tkey = lambda T: f"{T:.2e}"
grid = {}
for arm in ARMS:
    grid[arm] = {}
    for rho in RHO_LIST:
        cell = {"rho_pair": rho,
                "p_min_below": {tkey(T): stat(pmin_chunks[(arm, rho)][T]) for T in THRESH},
                "p_B_below": {tkey(T): stat(pB_chunks[(arm, rho)][T]) for T in THRESH},
                "score_corr_AB": stat(scorr_chunks[(arm, rho)])}
        grid[arm][f"{rho:.1f}"] = cell

baseline = {tkey(T): stat(pA_chunks[T]) for T in THRESH}

gains = {}
for arm in ARMS:
    gains[arm] = {}
    for T in THRESH:
        d = pmin_chunks[(arm, 0.0)][T] - pmin_chunks[(arm, 1.0)][T]  # paired (CRN)
        gains[arm][tkey(T)] = stat(d)

gate_details = {}
survive = False
for arm in GATE_ARMS:
    for T in THRESH:
        g = gains[arm][tkey(T)]["value"]
        ok = g >= GATE_PP
        gate_details[f"{arm}@{tkey(T)}"] = {"gain": g, "threshold": GATE_PP, "meets": bool(ok)}
        survive = survive or ok
verdict = "SURVIVES" if survive else "KILL"

# rho=0 independence cross-check (same simulation marginals)
indep_check = {}
for arm in ARMS:
    indep_check[arm] = {}
    for T in THRESH:
        pA = float(pA_chunks[T].mean())
        pB = float(pB_chunks[(arm, 0.0)][T].mean())
        prod = 1.0 - (1.0 - pA) * (1.0 - pB)
        sim = float(pmin_chunks[(arm, 0.0)][T].mean())
        indep_check[arm][tkey(T)] = {"independence_product": prod, "simulated": sim,
                                     "gap": sim - prod}

results = {
    "experiment": "s4_designation_portfolio_bootstrap",
    "date": "2026-08-09",
    "verdict": verdict,
    "gates": {
        "rule": "SURVIVE if P(min<T|rho=0)-P(min<T|rho=1) >= 0.02 at ANY threshold in same_mean or r6 arms; else KILL",
        "gate_arms": GATE_ARMS,
        "details": gate_details,
    },
    "design": {
        "n_suites": N_SUITES, "n_nets_per_suite": N_NETS, "n_chunks": N_CHUNKS,
        "anchor_suite_mean_A": ANCHOR, "rho_list": RHO_LIST, "thresholds": THRESH,
        "arms": {a: {"scale": s, "marginal": m} for a, (s, m) in ARMS.items()},
        "copula": "Gaussian latent: Z_B = rho*Z_A + sqrt(1-rho^2)*W; F = Q_emp(Phi(Z)); marginals exact",
        "shared_net_difficulty": True,
        "fbar6_presample_n": N_FBAR6_PRESAMPLE,
        "fbar6_presample_note": "mean of 6 iid pool draws, renormalized to mean exactly 1",
        "crn": "Z_A, W, D shared across all arms and rhos (paired gain estimates)",
        "master_seed": MASTER_SEED,
    },
    "calibration": {"pool_n": int(pool.size), "vF": vF, "vD": vD,
                    "vF6_presample": vF6, "vF_over_6": vF / 6.0},
    "harness_check_s1_reproduction": harness,
    "single_designation_baseline_pA_below": baseline,
    "grid": grid,
    "diversification_gains_rho0_minus_rho1": gains,
    "crosschecks": {
        "rho1_same_mean_bitwise_equals_A": bool(rho1_bitwise_ok),
        "bitwise_repeat_chunk0": bool(rep_ok),
        "rho0_independence_product_vs_sim": indep_check,
        "factor_corr_pool_marginal": {f"{r:.1f}": float(fcorr_pool_chunks[r].mean()) for r in RHO_LIST},
        "factor_corr_r6_marginal": {f"{r:.1f}": float(fcorr_r6_chunks[r].mean()) for r in RHO_LIST},
    },
    "data_files": [P2_PATH],
    "runtime_seconds": round(time.time() - t0, 1),
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=1)

print("verdict:", verdict)
print("harness SD check:", harness["pass"], f"(sd={sd_A:.4e}, s1={S1_SD_REF:.4e}, ratio={harness['sd_ratio_vs_s1']:.4f})")
print("rho1 bitwise:", rho1_bitwise_ok, "| chunk0 repeat:", rep_ok)
for arm in ARMS:
    for T in THRESH:
        g = gains[arm][tkey(T)]
        print(f"gain {arm}@{tkey(T)}: {g['value']*100:.2f}pp (se {g['se']*100:.3f})")
print("wrote", OUT_JSON, f"[{time.time()-t0:.1f}s]")
