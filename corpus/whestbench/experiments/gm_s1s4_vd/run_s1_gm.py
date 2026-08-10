"""gm_s1s4_vd — COPY of experiments/s1_suite_risk/run_s1.py, multi-arm in vD.

The ONLY change to the model is the difficulty variance vD: the log-uniform
half-width is solved so Var(D)/E[D]^2 hits each target. Anchor, rotation pool,
suite sizes, R list, chunking, MASTER_SEED and the seed layout are byte-identical
to the committed harness; every arm gets the SAME seed children (fresh
SeedSequence per arm, so no spawn-state mutation across arms -- the defect S1b
reported).

Arms (PREDECLARATION Q6): control 7.57e-4 (DIFF_RATIO 1.1 exactly),
vD_moment(raw,ddof1), vD_moment(corr,ddof1), 0.0814, 0.1220.
The original file is NOT modified.
"""
import json, hashlib, time, os
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
EXP = os.path.join(ROOT, "corpus", "whestbench", "experiments")
P2_PATH = os.path.join(EXP, "pb1_premise_battery", "p2_results.json")
M185_PATH = os.path.join(EXP, "a_series_granular_adversarial", "m185_g0_stage1_checkpoint.json")
A1B_PATH = os.path.join(EXP, "a_series_granular_adversarial", "a1b_tail_diagnostics.json")
S1_COMMITTED = os.path.join(EXP, "s1_suite_risk", "s1_results.json")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "s1_gm_results.json")

ANCHOR = 1.83e-7
N_SUITES = 100_000
N_NETS = 50
R_LIST = [1, 2, 4, 6]
N_CHUNKS = 10
THRESH = [1.6e-7, 1.0e-7]
MASTER_SEED = 20260809          # identical to the committed harness

t0 = time.time()

# ---------------- calibration: rotation factor pool from P2 (unchanged) ------
p2 = json.load(open(P2_PATH))
per_net = p2["q1_oracle_headroom"]["per_net"]
pool_parts = []
for seed, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    pool_parts.append(m / m.mean())
pool = np.concatenate(pool_parts)
pool = pool / pool.mean()
vF = float(pool.var())
pool_spread = float(pool.max() / pool.min())

# ---------------- difficulty: log-uniform, half-width solved for target vD ---
def vd_of_half(half):
    d_mean = np.sinh(half) / half
    return float((np.sinh(2 * half) / (2 * half)) / d_mean ** 2 - 1.0)

def half_for_vd(target):
    lo, hi = 1e-9, 0.1
    while vd_of_half(hi) < target:
        hi *= 1.5
        if hi > 20:
            raise RuntimeError("no bracket")
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if vd_of_half(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

s0 = json.load(open(os.path.join(HERE, "step0_results.json")))
HALF_CONTROL = np.log(1.1) / 2.0
ARMS_VD = {
    "control_1.1x": ("half", HALF_CONTROL),
    "vD_moment_raw": ("vd", s0["moment_identity"]["raw"]["ddof1"]["vD_moment"]),
    "vD_moment_corr": ("vd", s0["moment_identity"]["corr_floor_subtracted"]["ddof1"]["vD_moment"]),
    "s1b_s17_low_0.0814": ("vd", 0.0814),
    "s1b_s17_high_0.1220": ("vd", 0.1220),
}

# ---------------- M185 observed reference ----------------
m185 = json.load(open(M185_PATH))
m185_raw = np.array([v["mse_raw"] for v in m185["nets"].values()], dtype=np.float64)
m185_spread_obs = float(m185_raw.max() / m185_raw.min())
a1b = json.load(open(A1B_PATH))


def run_arm_family(half):
    """Full S1 run at one difficulty half-width. Returns dict of results."""
    d_mean = np.sinh(half) / half
    vD = vd_of_half(half)

    def draw_D(rng, n):
        return np.exp(rng.uniform(-half, half, size=n)) / d_mean

    # fresh seed layout, identical for every arm (true CRN across arms)
    ss_root = np.random.SeedSequence(MASTER_SEED)
    r_seeds = {R: s for R, s in zip(R_LIST, ss_root.spawn(len(R_LIST)))}
    val_seed, rep_seed = ss_root.spawn(2)

    def run_arm(R, seedseq):
        chunk = N_SUITES // N_CHUNKS
        scores = np.empty(N_SUITES)
        chunk_means, chunk_widths = [], []
        chunk0_hash = None
        for c, sq in enumerate(seedseq.spawn(N_CHUNKS)):
            rng = np.random.default_rng(sq)
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
            "R": R, "mean": float(sc.mean()),
            "mean_se": float(cmeans.std(ddof=1) / np.sqrt(N_CHUNKS)),
            "sd": float(sc.std(ddof=1)), "p5": float(p5), "p95": float(p95),
            "p5_p95_width": float(p95 - p5),
            "width_se_batch": float(cwidths.std(ddof=1) / np.sqrt(N_CHUNKS)),
            "p_below_1p6em7": float((sc < THRESH[0]).mean()),
            "p_below_1p0em7": float((sc < THRESH[1]).mean()),
            "sd_analytic": float(ANCHOR * np.sqrt((vD + (1 + vD) * vF / R) / N_NETS)),
            "chunk0_sha256": h0,
        }

    # bitwise repeat of R=1 chunk 0 (fresh spawn, same seed)
    ss2 = np.random.SeedSequence(MASTER_SEED)
    r2 = ss2.spawn(len(R_LIST))[0]
    _, _, _, h0_rep = run_arm(1, r2)
    bitwise_ok = (h0_rep == arms[1]["chunk0_sha256"])

    # m185 80-net spread validation (identical code path & seed to committed S1)
    rng = np.random.default_rng(val_seed)
    NREP = 10_000
    idx = rng.integers(0, pool.size, size=(NREP, 80))
    sim = pool[idx] * draw_D(rng, (NREP, 80))
    spread_sim = sim.max(axis=1) / sim.min(axis=1)
    m185_val = {
        "observed_spread_80net_mse_raw": m185_spread_obs,
        "model_sim_spread_p5": float(np.percentile(spread_sim, 5)),
        "model_sim_spread_p50": float(np.percentile(spread_sim, 50)),
        "model_sim_spread_p95": float(np.percentile(spread_sim, 95)),
        "p_sim_ge_observed": float((spread_sim >= m185_spread_obs).mean()),
    }

    decomp = {}
    for R in R_LIST:
        rot = (1 + vD) * vF / R
        decomp[R] = {"rotation_component": rot, "difficulty_component": vD,
                     "rotation_share": rot / (rot + vD)}

    width_shrink = 1.0 - arms[6]["p5_p95_width"] / arms[1]["p5_p95_width"]
    mean_shift = arms[6]["mean"] / arms[1]["mean"] - 1.0
    # closed-form limit on the SD shrink, for the analytic cross-check
    sd_shrink = 1.0 - arms[6]["sd_analytic"] / arms[1]["sd_analytic"]
    gates = {
        "width_shrink_R6_vs_R1": {"value": float(width_shrink), "threshold": 0.25,
                                  "pass": bool(width_shrink >= 0.25)},
        "abs_mean_shift_R6_vs_R1": {"value": float(mean_shift), "threshold": 0.02,
                                    "pass": bool(abs(mean_shift) < 0.02)},
        "rotation_variance_dominant": {"rotation_share_R1": decomp[1]["rotation_share"],
                                       "pass": bool(decomp[1]["rotation_share"] > 0.5)},
    }
    return {
        "vD": vD, "difficulty_half_width": half,
        "difficulty_max_over_min": float(np.exp(2 * half)),
        "arms": {str(R): arms[R] for R in R_LIST},
        "variance_decomposition": {str(R): decomp[R] for R in R_LIST},
        "gates": gates,
        "verdict": "PASS" if all(g["pass"] for g in gates.values()) else "KILL",
        "analytic_sd_shrink_R6_vs_R1": float(sd_shrink),
        "analytic_vs_bootstrap_sd_ratio": {str(R): arms[R]["sd"] / arms[R]["sd_analytic"] for R in R_LIST},
        "bitwise_repeat_R1_chunk0": bool(bitwise_ok),
        "m185_spread_validation": m185_val,
    }


results = {"experiment": "gm_s1s4_vd_s1_rerun", "source_harness": "s1_suite_risk/run_s1.py",
           "changed": "difficulty variance vD only (log-uniform half-width solved per arm)",
           "calibration": {"pool_n": int(pool.size), "vF": vF, "pool_max_over_min": pool_spread},
           "design": {"n_suites": N_SUITES, "n_nets": N_NETS, "R_list": R_LIST,
                      "anchor": ANCHOR, "master_seed": MASTER_SEED, "n_chunks": N_CHUNKS},
           "arms": {}}

for name, (kind, val) in ARMS_VD.items():
    half = val if kind == "half" else half_for_vd(val)
    res = run_arm_family(half)
    results["arms"][name] = res
    g = res["gates"]
    print("%-22s vD=%.6f (D max/min %.3f)  shrink=%.4f  meanshift=%+.6f  rotshare=%.5f  "
          "P(<1.6e-7)=%.5f  verdict=%s  [%.1fs]"
          % (name, res["vD"], res["difficulty_max_over_min"],
             g["width_shrink_R6_vs_R1"]["value"], g["abs_mean_shift_R6_vs_R1"]["value"],
             g["rotation_variance_dominant"]["rotation_share_R1"],
             res["arms"]["1"]["p_below_1p6em7"], res["verdict"], time.time() - t0), flush=True)

# ---------------- V1: control arm reproduces the committed run ---------------
c = json.load(open(S1_COMMITTED))
ctl = results["arms"]["control_1.1x"]
checks = {}
checks["R1_sd"] = [ctl["arms"]["1"]["sd"], c["arms"]["1"]["sd"]]
checks["R1_p_below_1p6em7"] = [ctl["arms"]["1"]["p_below_1p6em7"], c["arms"]["1"]["p_below_1p6em7"]]
checks["R1_chunk0_sha256"] = [ctl["arms"]["1"]["chunk0_sha256"], c["arms"]["1"]["chunk0_sha256"]]
checks["width_shrink"] = [ctl["gates"]["width_shrink_R6_vs_R1"]["value"],
                          c["gates"]["width_shrink_R6_vs_R1"]["value"]]
checks["rot_share_R1"] = [ctl["gates"]["rotation_variance_dominant"]["rotation_share_R1"],
                          c["gates"]["rotation_variance_dominant"]["rotation_share_R1"]]
checks["vD"] = [ctl["vD"], c["calibration"]["vD_difficulty_variance"]]
checks["m185_p50"] = [ctl["m185_spread_validation"]["model_sim_spread_p50"],
                      c["crosschecks"]["m185_spread_validation"]["model_sim_spread_p50"]]
ok = True
detail = {}
for k, (mine, ref) in checks.items():
    if isinstance(mine, str):
        good = (mine == ref)
        detail[k] = {"mine": mine, "committed": ref, "identical": good}
    else:
        rel = abs(mine / ref - 1.0) if ref else abs(mine - ref)
        good = rel < 1e-12
        detail[k] = {"mine": mine, "committed": ref, "rel_diff": rel, "within_1e-12": good}
    ok = ok and good
results["V1_control_reproduces_committed_s1"] = {"all_pass": bool(ok), "checks": detail}

results["runtime_seconds"] = round(time.time() - t0, 1)
json.dump(results, open(OUT_JSON, "w"), indent=1)
print("V1 control reproduction of committed s1_results.json:", ok)
for k, v in detail.items():
    print("   ", k, v)
print("wrote", OUT_JSON, "[%.1fs]" % (time.time() - t0))
