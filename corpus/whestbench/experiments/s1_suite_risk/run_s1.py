"""S1 (ledger id s1_suite_risk_bootstrap): Monte-Carlo bootstrap of 50-net suite
scores under R-rotation budget splitting.

Model: per-net MSE = S * D_i * mean(F_i1..F_iR)
  D_i : net difficulty factor, log-uniform with max/min ratio 1.1 (the tail
        theorem's ~1.1x MC-difficulty spread), normalized to mean 1.
  F_ij: rotation-draw factor, drawn iid from the pooled empirical within-net
        distribution of the P2 rotation grid (3 nets x 16 rotations, each net's
        mse_per_rotation normalized by its own mean), pool mean forced to 1.
  S   : anchor scale = 1.83e-7 (hosted champion level); with E[D]=E[F]=1 the
        R=1 suite mean is anchored at S by construction.
  Budget split: R rotations at B/R each => per-draw MSE x R; equal-weight
  average of R independent estimates => MSE = S*D*mean(F_1..F_R): mean
  preserved, rotation-variance component / R.

Gates (predeclared, ledger s1_suite_risk_bootstrap):
  PASS: P5-P95 width shrink >= 25% at R=6 vs R=1 AND |mean shift| < 2%.
  KILL: width shrink < 25%, OR mean inflates >= 2%, OR rotation-draw variance
        is not the dominant across-suite component.

Cross-checks (two-signal rule):
  1. Analytic SD per R: S*sqrt((vD + (1+vD)*vF/R)/50) vs bootstrap SD.
  2. Bitwise repeat of the first R=1 chunk with the same seed.
  3. M185 validation: distribution of 80-net max/min spread of single-draw
     D*F vs the observed hosted spread 15.53x (m185 stage1, mse_raw).
"""
import json
import hashlib
import time
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
P2_PATH = ROOT + r"\corpus\whestbench\experiments\pb1_premise_battery\p2_results.json"
M185_PATH = ROOT + r"\corpus\whestbench\experiments\a_series_granular_adversarial\m185_g0_stage1_checkpoint.json"
A1B_PATH = ROOT + r"\corpus\whestbench\experiments\a_series_granular_adversarial\a1b_tail_diagnostics.json"
OUT_JSON = ROOT + r"\corpus\whestbench\experiments\s1_suite_risk\s1_results.json"

ANCHOR = 1.83e-7
N_SUITES = 100_000
N_NETS = 50
R_LIST = [1, 2, 4, 6]
N_CHUNKS = 10          # for batch-based CIs and memory bounding
DIFF_RATIO = 1.1       # max/min spread of the difficulty factor
THRESH = [1.6e-7, 1.0e-7]
MASTER_SEED = 20260809

t0 = time.time()

# ---------------- calibration: rotation factor pool from P2 ----------------
p2 = json.load(open(P2_PATH))
per_net = p2["q1_oracle_headroom"]["per_net"]
pool_parts, p2_summary = [], {}
for seed, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    p2_summary[seed] = {"n": len(m), "mean": m.mean(), "min": m.min(),
                        "max": m.max(), "within_net_spread": m.max() / m.min()}
    pool_parts.append(m / m.mean())
pool = np.concatenate(pool_parts)
pool = pool / pool.mean()           # force mean exactly 1
vF = float(pool.var())              # population variance of rotation factor
pool_spread = float(pool.max() / pool.min())

# ---------------- difficulty factor ----------------
# log-uniform on [-log(r)/2, +log(r)/2], r = DIFF_RATIO; normalize to mean 1.
half = np.log(DIFF_RATIO) / 2.0
# E[e^U], U~Unif(-half, half) = sinh(half)/half
d_mean = np.sinh(half) / half
vD = float((np.sinh(2 * half) / (2 * half)) / d_mean**2 - 1.0)  # Var(D)/E[D]^2 with mean-1 normalization

# ---------------- M185 observed reference ----------------
m185 = json.load(open(M185_PATH))
m185_raw = np.array([v["mse_raw"] for v in m185["nets"].values()], dtype=np.float64)
m185_spread_obs = float(m185_raw.max() / m185_raw.min())
a1b = json.load(open(A1B_PATH))

# ---------------- bootstrap ----------------
rng_root = np.random.SeedSequence(MASTER_SEED)
r_seeds = {R: s for R, s in zip(R_LIST, rng_root.spawn(len(R_LIST)))}
val_seed, rep_seed = rng_root.spawn(2)

def draw_D(rng, n):
    return np.exp(rng.uniform(-half, half, size=n)) / d_mean

def run_arm(R, seedseq):
    """Returns (all_scores, per-chunk means, per-chunk widths, chunk0_hash)."""
    chunk = N_SUITES // N_CHUNKS
    scores = np.empty(N_SUITES)
    chunk_means, chunk_widths = [], []
    chunk0_hash = None
    for c, ss in enumerate(seedseq.spawn(N_CHUNKS)):
        rng = np.random.default_rng(ss)
        idx = rng.integers(0, pool.size, size=(chunk, N_NETS, R))
        Fbar = pool[idx].mean(axis=2)
        D = draw_D(rng, (chunk, N_NETS))
        sc = ANCHOR * (D * Fbar).mean(axis=1)
        scores[c * chunk:(c + 1) * chunk] = sc
        chunk_means.append(sc.mean())
        p5c, p95c = np.percentile(sc, [5, 95])
        chunk_widths.append(p95c - p5c)
        if c == 0:
            chunk0_hash = hashlib.sha256(sc.tobytes()).hexdigest()
    return scores, np.array(chunk_means), np.array(chunk_widths), chunk0_hash

arms = {}
for R in R_LIST:
    sc, cmeans, cwidths, h0 = run_arm(R, r_seeds[R])
    p5, p95 = np.percentile(sc, [5, 95])
    arms[R] = {
        "R": R,
        "mean": float(sc.mean()),
        "mean_se": float(cmeans.std(ddof=1) / np.sqrt(N_CHUNKS)),
        "sd": float(sc.std(ddof=1)),
        "p5": float(p5),
        "p95": float(p95),
        "p5_p95_width": float(p95 - p5),
        "width_se_batch": float(cwidths.std(ddof=1) / np.sqrt(N_CHUNKS)),
        "p_below_1p6em7": float((sc < THRESH[0]).mean()),
        "p_below_1p0em7": float((sc < THRESH[1]).mean()),
        "sd_analytic": float(ANCHOR * np.sqrt((vD + (1 + vD) * vF / R) / N_NETS)),
        "chunk0_sha256": h0,
    }
    print(f"R={R}: mean={arms[R]['mean']:.4e} sd={arms[R]['sd']:.3e} "
          f"(analytic {arms[R]['sd_analytic']:.3e}) width={arms[R]['p5_p95_width']:.3e} "
          f"P(<1.6e-7)={arms[R]['p_below_1p6em7']:.4f} [{time.time()-t0:.1f}s]",
          flush=True)

# ---------------- cross-check 2: bitwise repeat of R=1 chunk 0 ----------------
_, _, _, h0_rep = run_arm(1, np.random.SeedSequence(MASTER_SEED).spawn(len(R_LIST))[0])
bitwise_repeat_ok = (h0_rep == arms[1]["chunk0_sha256"])

# ---------------- cross-check 3: M185 80-net spread validation ----------------
rng = np.random.default_rng(val_seed)
NREP = 10_000
idx = rng.integers(0, pool.size, size=(NREP, 80))
sim = pool[idx] * draw_D(rng, (NREP, 80))
spread_sim = sim.max(axis=1) / sim.min(axis=1)
m185_val = {
    "observed_spread_80net_mse_raw": m185_spread_obs,
    "a1b_recorded_spread": a1b["spread"],
    "model_sim_spread_p5": float(np.percentile(spread_sim, 5)),
    "model_sim_spread_p50": float(np.percentile(spread_sim, 50)),
    "model_sim_spread_p95": float(np.percentile(spread_sim, 95)),
    "model_pool_max_spread_bound": pool_spread,
    "p_sim_ge_observed": float((spread_sim >= m185_spread_obs).mean()),
}

# ---------------- variance decomposition ----------------
# Var(D*Fbar) = vD + (1+vD)*vF/R ; rotation component = (1+vD)*vF/R.
decomp = {}
for R in R_LIST:
    rot = (1 + vD) * vF / R
    decomp[R] = {"rotation_component": rot, "difficulty_component": vD,
                 "rotation_share": rot / (rot + vD)}

# ---------------- gates ----------------
width_shrink = 1.0 - arms[6]["p5_p95_width"] / arms[1]["p5_p95_width"]
mean_shift = arms[6]["mean"] / arms[1]["mean"] - 1.0
rot_dominant = decomp[1]["rotation_share"] > 0.5
gates = {
    "width_shrink_R6_vs_R1": {"value": float(width_shrink), "threshold": 0.25,
                              "pass": bool(width_shrink >= 0.25)},
    "abs_mean_shift_R6_vs_R1": {"value": float(mean_shift), "threshold": 0.02,
                                "pass": bool(abs(mean_shift) < 0.02)},
    "rotation_variance_dominant": {"rotation_share_R1": decomp[1]["rotation_share"],
                                   "pass": bool(rot_dominant)},
}
verdict = "PASS" if all(g["pass"] for g in gates.values()) else "KILL"

results = {
    "experiment": "s1_suite_risk_bootstrap",
    "date": "2026-08-09",
    "verdict": verdict,
    "gates": gates,
    "design": {
        "n_suites": N_SUITES, "n_nets_per_suite": N_NETS, "R_list": R_LIST,
        "anchor_suite_mean": ANCHOR, "difficulty_spread_ratio": DIFF_RATIO,
        "difficulty_model": "log-uniform max/min=1.1, normalized to mean 1",
        "rotation_pool": "P2 grid, 3 nets x 16 rotations, per-net mean-normalized, pooled (48 values), mean forced to 1",
        "budget_model": "R rotations at B/R each; per-draw MSE x R; equal-weight average => MSE = S*D*mean(F_1..F_R)",
        "master_seed": MASTER_SEED,
    },
    "calibration": {
        "pool_n": int(pool.size), "vF_rotation_factor_variance": vF,
        "pool_max_over_min": pool_spread, "vD_difficulty_variance": vD,
        "p2_per_net": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in p2_summary.items()},
    },
    "arms": {str(R): arms[R] for R in R_LIST},
    "variance_decomposition": {str(R): decomp[R] for R in R_LIST},
    "crosschecks": {
        "analytic_vs_bootstrap_sd_ratio": {str(R): arms[R]["sd"] / arms[R]["sd_analytic"] for R in R_LIST},
        "bitwise_repeat_R1_chunk0": bitwise_repeat_ok,
        "m185_spread_validation": m185_val,
    },
    "data_files": [P2_PATH, M185_PATH, A1B_PATH],
    "runtime_seconds": round(time.time() - t0, 1),
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=1)
print("verdict:", verdict, "| width_shrink:", round(width_shrink, 4),
      "| mean_shift:", round(mean_shift, 6), "| rot_share_R1:",
      round(decomp[1]["rotation_share"], 5), "| bitwise_repeat:", bitwise_repeat_ok)
print("wrote", OUT_JSON, f"[{time.time()-t0:.1f}s]")
