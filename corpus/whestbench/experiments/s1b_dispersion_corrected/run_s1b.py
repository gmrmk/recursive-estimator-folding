"""S1B (s1b_dispersion_corrected): dispersion-corrected re-run of the S1
suite-risk bootstrap.

A verified red-team finding says the committed S1/U9 suite-risk model
(DIFF_RATIO = 1.1, vD = 7.57e-4) understates per-net difficulty variance.
This harness is a copy of s1_suite_risk/run_s1.py in which ONLY the dispersion
parameter (DIFF_RATIO, equivalently vD) is varied across predeclared arms.
Model shape (log-uniform difficulty, mean 1), rotation pool calibration
(P2 grid, 48 values), anchor (1.83e-7), budget model, and the committed seed
layout are IDENTICAL to run_s1.py. R is fixed at 1 = the champion designation
(U9: slot A = champion, R=1).

Arms (vD derived in-harness from committed evidence, arithmetic recorded):
  old_control : DIFF_RATIO = 1.1 (committed model; must REPRODUCE
                s1_results.json exactly and must FAIL the 15.53x bracket)
  s17_low/high: vD = relative variance of the three s17 per-net
                sigma2_var(ybar) values (ddof=0 / ddof=1); rotation-free
                by construction
  p2_low/high : vD = relative variance of the three P2 per-net 16-rotation
                mean MSEs (ddof=0 / ddof=1), deconvolved for the residual
                rotation noise of a 16-rotation mean under the model
                Var(D*Fbar16)/E^2 = vD + (1+vD)*vF/16
                => vD = (v_obs - vF/16) / (1 + vF/16)

Output extensions required by the dispatch task (model untouched):
  - 100-net suites alongside the committed 50-net suites
  - threshold grid T in {1.55e-7, 1.6e-7, 1.83e-7, 2.0e-7, 2.5e-7}
  - per-arm 80-net max/min spread bracket test vs observed 15.53x
  - 1e6-suite tail refinement for P(<T) and the downside P(>2.5e-7)

Two-signal verification:
  1. control arm reproduces committed s1_results.json (mean, sd, p5, p95,
     P(<1.6e-7), chunk0 sha256, m185 sim spread P5/P50/P95) -- asserted
  2. analytic SD S*sqrt((vD+(1+vD)*vF)/n)/ vs bootstrap SD, every arm
  3. bitwise repeat of chunk 0, every arm
  4. 100k-run P5/P95 vs 1e6-run P5/P95 (disjoint seed streams)
  5. input crosscheck: p2 16-rotation means vs s17 champion_mse fields
"""
import json
import hashlib
import time
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
P2_PATH = ROOT + r"\corpus\whestbench\experiments\pb1_premise_battery\p2_results.json"
M185_PATH = ROOT + r"\corpus\whestbench\experiments\a_series_granular_adversarial\m185_g0_stage1_checkpoint.json"
A1B_PATH = ROOT + r"\corpus\whestbench\experiments\a_series_granular_adversarial\a1b_tail_diagnostics.json"
S17_PATH = ROOT + r"\corpus\whestbench\experiments\s17_ibc_floor\s17_results.json"
S1_PATH = ROOT + r"\corpus\whestbench\experiments\s1_suite_risk\s1_results.json"
OUT_JSON = ROOT + r"\corpus\whestbench\experiments\s1b_dispersion_corrected\s1b_results.json"

ANCHOR = 1.83e-7
N_SUITES = 100_000          # committed size (control must reproduce)
N_CHUNKS = 10
N_TAIL = 1_000_000          # tail refinement
N_TAIL_CHUNKS = 100
THRESH = [1.55e-7, 1.6e-7, 1.83e-7, 2.0e-7, 2.5e-7]
DOWNSIDE_T = 2.5e-7
MASTER_SEED = 20260809      # identical to committed S1
R = 1                       # champion designation (U9 slot A)
NET_KEYS = ("101", "202", "303")
tkey = lambda T: f"{T:.2e}"

t0 = time.time()

# ---------------- calibration: rotation factor pool (identical to S1) ----------------
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

s1_committed = json.load(open(S1_PATH))
assert abs(vF - s1_committed["calibration"]["vF_rotation_factor_variance"]) < 1e-15, vF
assert abs(pool_spread - s1_committed["calibration"]["pool_max_over_min"]) < 1e-12, pool_spread

# ---------------- vD derivation from committed evidence ----------------
def relvar(x, ddof):
    x = np.asarray(x, dtype=np.float64)
    return float(x.var(ddof=ddof) / x.mean() ** 2)

# (a) s17 per-net sigma2_var(ybar): rotation-free net-difficulty proxy
s17 = json.load(open(S17_PATH))
sig2 = np.array([s17["A_per_net"][k]["sigma2_var(ybar)"] for k in NET_KEYS])
vD_s17_low = relvar(sig2, 0)
vD_s17_high = relvar(sig2, 1)

# (b) p2 per-net 16-rotation mean MSEs: direct champion-MSE dispersion
p2_means = np.array([np.mean(per_net[k]["mse_per_rotation"]) for k in NET_KEYS])
# input crosscheck: same quantity recorded independently in p2 mse_mean and s17 champion_mse
p2_mse_mean_field = np.array([per_net[k]["mse_mean"] for k in NET_KEYS])
s17_champ = np.array([s17["A_per_net"][k]["champion_mse"] for k in NET_KEYS])
assert np.allclose(p2_means, p2_mse_mean_field, rtol=1e-12)
assert np.allclose(p2_means, s17_champ, rtol=1e-4)   # independent recomputation in s17
v_obs_low = relvar(p2_means, 0)
v_obs_high = relvar(p2_means, 1)
rot_noise_16 = vF / 16.0
deconv_exact = lambda v: (v - rot_noise_16) / (1.0 + rot_noise_16)
vD_p2_low = deconv_exact(v_obs_low)
vD_p2_high = deconv_exact(v_obs_high)

derivation = {
    "a_s17_sigma2": {
        "values": [float(v) for v in sig2],
        "mean": float(sig2.mean()),
        "max_over_min": float(sig2.max() / sig2.min()),
        "relvar_ddof0": vD_s17_low,
        "relvar_ddof1": vD_s17_high,
        "note": "sigma2_var(ybar) is rotation-free by construction; using it as the "
                "difficulty factor assumes MSE_i ~ sigma_i^2 (equal N_eff). s17 shows "
                "N_eff/N_eval varies 0.42-0.73 across the 3 nets, so this is a LOWER "
                "anchor on champion-MSE dispersion.",
    },
    "b_p2_16rot_means": {
        "values": [float(v) for v in p2_means],
        "mean": float(p2_means.mean()),
        "max_over_min": float(p2_means.max() / p2_means.min()),
        "relvar_observed_ddof0": v_obs_low,
        "relvar_observed_ddof1": v_obs_high,
        "rotation_noise_of_16rot_mean_vF_over_16": rot_noise_16,
        "deconvolution": "vD = (v_obs - vF/16)/(1 + vF/16)  [exact under MSE=S*D*Fbar16, D indep F]",
        "vD_ddof0": vD_p2_low,
        "vD_ddof1": vD_p2_high,
        "subtraction_only_for_reference_ddof0": v_obs_low - rot_noise_16,
        "subtraction_only_for_reference_ddof1": v_obs_high - rot_noise_16,
    },
    "n3_caveat": "both estimates rest on n=3 nets; a chi2(2) CI on the ddof=1 variance "
                 "spans ~[0.27x, 39.5x], so the vD point values are wide. The third, "
                 "independent signal that disciplines the range is the 80-net observed "
                 "spread 15.53x bracket test below.",
}

# ---------------- arm definitions: invert DIFF_RATIO from target vD ----------------
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

ARMS = {
    "old_control": {"ratio": 1.1, "vD_source": "committed S1/U9 model (control)"},
    "s17_low":  {"vD": vD_s17_low,  "vD_source": "s17 sigma2 relvar ddof=0"},
    "s17_high": {"vD": vD_s17_high, "vD_source": "s17 sigma2 relvar ddof=1"},
    "p2_low":   {"vD": vD_p2_low,   "vD_source": "p2 16-rot means relvar ddof=0, rotation-deconvolved"},
    "p2_high":  {"vD": vD_p2_high,  "vD_source": "p2 16-rot means relvar ddof=1, rotation-deconvolved"},
}
for name, arm in ARMS.items():
    if "ratio" in arm:
        arm["vD"] = vD_of_ratio(arm["ratio"])
    else:
        arm["ratio"] = ratio_of_vD(arm["vD"])
        assert abs(vD_of_ratio(arm["ratio"]) - arm["vD"]) < 1e-9 * max(arm["vD"], 1e-12)
    arm["half"] = np.log(arm["ratio"]) / 2.0
    arm["d_mean"] = np.sinh(arm["half"]) / arm["half"]
assert abs(ARMS["old_control"]["vD"] - s1_committed["calibration"]["vD_difficulty_variance"]) < 1e-15

# ---------------- observed reference ----------------
m185 = json.load(open(M185_PATH))
m185_raw = np.array([v["mse_raw"] for v in m185["nets"].values()], dtype=np.float64)
m185_spread_obs = float(m185_raw.max() / m185_raw.min())
a1b = json.load(open(A1B_PATH))
assert abs(m185_spread_obs - a1b["spread"]) < 1e-9

# ---------------- seed layout (identical prefix to committed S1) ----------------
# SeedSequence.spawn mutates spawn state, so every consumer derives the layout
# FRESH from MASTER_SEED: all arms then use the same seed children (common
# random numbers) and the control reproduces the committed run exactly.
def seed_layout():
    root = np.random.SeedSequence(MASTER_SEED)
    r4 = root.spawn(4)                # committed: seeds for R in {1,2,4,6}; we use [0] (R=1)
    v, rep = root.spawn(2)            # committed: m185 validation seed, (unused rep seed)
    n100 = root.spawn(1)[0]           # new: 100-net suites
    t50 = root.spawn(1)[0]            # new: 1e6-suite tail, 50 nets
    t100 = root.spawn(1)[0]           # new: 1e6-suite tail, 100 nets
    return r4[0], v, n100, t50, t100

_, val_seed, _, _, _ = seed_layout()  # default_rng(seedseq) does not mutate spawn state

def draw_D(rng, shape, arm):
    return np.exp(rng.uniform(-arm["half"], arm["half"], size=shape)) / arm["d_mean"]

def run_suites(arm, n_nets, seedseq, n_suites, n_chunks):
    """Identical draw sequence to run_s1.py run_arm (R=1); per-chunk stats."""
    chunk = n_suites // n_chunks
    scores = np.empty(n_suites)
    chunk_means = np.empty(n_chunks)
    chunk_p = {tkey(T): np.empty(n_chunks) for T in THRESH}
    chunk_pdown = np.empty(n_chunks)
    chunk0_hash = None
    for c, ss in enumerate(seedseq.spawn(n_chunks)):
        rng = np.random.default_rng(ss)
        idx = rng.integers(0, pool.size, size=(chunk, n_nets, R))
        Fbar = pool[idx].mean(axis=2)
        D = draw_D(rng, (chunk, n_nets), arm)
        sc = ANCHOR * (D * Fbar).mean(axis=1)
        scores[c * chunk:(c + 1) * chunk] = sc
        chunk_means[c] = sc.mean()
        for T in THRESH:
            chunk_p[tkey(T)][c] = (sc < T).mean()
        chunk_pdown[c] = (sc > DOWNSIDE_T).mean()
        if c == 0:
            chunk0_hash = hashlib.sha256(sc.tobytes()).hexdigest()
    p5, p95 = np.percentile(scores, [5, 95])
    sd_analytic = ANCHOR * np.sqrt((arm["vD"] + (1 + arm["vD"]) * vF / R) / n_nets)
    out = {
        "n_nets": n_nets, "n_suites": n_suites,
        "mean": float(scores.mean()),
        "mean_se": float(chunk_means.std(ddof=1) / np.sqrt(n_chunks)),
        "sd": float(scores.std(ddof=1)),
        "sd_analytic": float(sd_analytic),
        "p5": float(p5), "p95": float(p95),
        "p5_p95_width": float(p95 - p5),
        "normal_approx_p5": float(ANCHOR - 1.6449 * sd_analytic),
        "normal_approx_p95": float(ANCHOR + 1.6449 * sd_analytic),
        "p_below": {}, "chunk0_sha256": chunk0_hash,
    }
    for T in THRESH:
        v = chunk_p[tkey(T)]
        out["p_below"][tkey(T)] = {"value": float(v.mean()),
                                   "se": float(v.std(ddof=1) / np.sqrt(n_chunks))}
    out["p_above_2p5em7"] = {"value": float(chunk_pdown.mean()),
                             "se": float(chunk_pdown.std(ddof=1) / np.sqrt(n_chunks))}
    return out

def run_spread80(arm):
    """Identical to run_s1.py cross-check 3: 80-net single-draw D*F spread."""
    rng = np.random.default_rng(val_seed)
    NREP = 10_000
    idx = rng.integers(0, pool.size, size=(NREP, 80))
    sim = pool[idx] * draw_D(rng, (NREP, 80), arm)
    spread_sim = sim.max(axis=1) / sim.min(axis=1)
    p5, p50, p95 = np.percentile(spread_sim, [5, 50, 95])
    return {
        "sim_spread_p5": float(p5), "sim_spread_p50": float(p50), "sim_spread_p95": float(p95),
        "model_max_spread_bound": float(pool_spread * arm["ratio"]),
        "p_sim_ge_observed": float((spread_sim >= m185_spread_obs).mean()),
        "observed_spread": m185_spread_obs,
        "brackets_observed": bool(p5 <= m185_spread_obs <= p95),
    }

# ---------------- run all arms ----------------
results_arms = {}
for name, arm in ARMS.items():
    seed50, _, n100_seed, tail50_seed, tail100_seed = seed_layout()
    a = {"vD": arm["vD"], "diff_ratio": arm["ratio"], "vD_source": arm["vD_source"]}
    a["suite_50"] = run_suites(arm, 50, seed50, N_SUITES, N_CHUNKS)
    a["suite_100"] = run_suites(arm, 100, n100_seed, N_SUITES, N_CHUNKS)
    a["tail_50"] = run_suites(arm, 50, tail50_seed, N_TAIL, N_TAIL_CHUNKS)
    a["tail_100"] = run_suites(arm, 100, tail100_seed, N_TAIL, N_TAIL_CHUNKS)
    a["spread80"] = run_spread80(arm)
    rot = (1 + arm["vD"]) * vF / R
    a["variance_decomposition_R1"] = {
        "rotation_component": rot, "difficulty_component": arm["vD"],
        "rotation_share": rot / (rot + arm["vD"]),
        "difficulty_share": arm["vD"] / (rot + arm["vD"]),
    }
    # analytic note: what the committed S1 R=6 width-shrink gate would look like
    a["s1_gate_note_analytic_R6_sd_shrink"] = float(
        1.0 - np.sqrt((arm["vD"] + (1 + arm["vD"]) * vF / 6.0)
                      / (arm["vD"] + (1 + arm["vD"]) * vF)))
    # bitwise repeat of chunk 0 (fresh SeedSequence, same derivation path)
    rep = run_suites(arm, 50, seed_layout()[0], N_SUITES, N_CHUNKS)
    a["bitwise_repeat_chunk0_ok"] = bool(rep["chunk0_sha256"] == a["suite_50"]["chunk0_sha256"])
    results_arms[name] = a
    print(f"{name}: vD={arm['vD']:.4g} ratio={arm['ratio']:.4g} | 50-net mean={a['suite_50']['mean']:.4e} "
          f"sd={a['suite_50']['sd']:.3e} P5={a['suite_50']['p5']:.4e} P95={a['suite_50']['p95']:.4e} | "
          f"spread80 P5-P95 [{a['spread80']['sim_spread_p5']:.2f},{a['spread80']['sim_spread_p95']:.2f}] "
          f"brackets15.53={a['spread80']['brackets_observed']} | "
          f"P(>2.5e-7) 50-net={a['tail_50']['p_above_2p5em7']['value']:.5f} "
          f"[{time.time()-t0:.1f}s]", flush=True)

# ---------------- control-arm reproduction asserts (two-signal, committed) ----------------
ctrl = results_arms["old_control"]["suite_50"]
ref = s1_committed["arms"]["1"]
assert ctrl["chunk0_sha256"] == ref["chunk0_sha256"], "control chunk0 hash mismatch"
for k_new, k_old in [("mean", "mean"), ("sd", "sd"), ("p5", "p5"), ("p95", "p95")]:
    assert abs(ctrl[k_new] - ref[k_old]) <= 1e-12 * abs(ref[k_old]), (k_new, ctrl[k_new], ref[k_old])
assert abs(ctrl["p_below"]["1.60e-07"]["value"] - ref["p_below_1p6em7"]) < 1e-12
ctrl_sp = results_arms["old_control"]["spread80"]
ref_sp = s1_committed["crosschecks"]["m185_spread_validation"]
for k_new, k_old in [("sim_spread_p5", "model_sim_spread_p5"),
                     ("sim_spread_p50", "model_sim_spread_p50"),
                     ("sim_spread_p95", "model_sim_spread_p95"),
                     ("p_sim_ge_observed", "p_sim_ge_observed")]:
    assert abs(ctrl_sp[k_new] - ref_sp[k_old]) <= 1e-12 * max(abs(ref_sp[k_old]), 1.0)
print("control reproduction of committed s1_results.json: PASS", flush=True)

# ---------------- bracketing verdict ----------------
bracket = {
    "observed_80net_spread": m185_spread_obs,
    "old_model_fails_bracket": bool(not results_arms["old_control"]["spread80"]["brackets_observed"]),
    "corrected_arms_bracket": {n: results_arms[n]["spread80"]["brackets_observed"]
                               for n in ("s17_low", "s17_high", "p2_low", "p2_high")},
}
bracket["verdict"] = ("PASS" if bracket["old_model_fails_bracket"]
                      and any(bracket["corrected_arms_bracket"].values()) else "FAIL")

# ---------------- headline ----------------
corr_names = [n for n in ("s17_low", "s17_high", "p2_low", "p2_high")
              if results_arms[n]["spread80"]["brackets_observed"]]
env_names = corr_names if corr_names else ["s17_high", "p2_high"]
headline = {
    "corrected_vD_range": [min(ARMS[n]["vD"] for n in ("s17_low", "s17_high", "p2_low", "p2_high")),
                           max(ARMS[n]["vD"] for n in ("s17_low", "s17_high", "p2_low", "p2_high"))],
    "bracketing_arms": corr_names,
    "fresh_seed_band_50net_p5_p95_envelope": [
        min(results_arms[n]["tail_50"]["p5"] for n in env_names),
        max(results_arms[n]["tail_50"]["p95"] for n in env_names)],
    "fresh_seed_band_100net_p5_p95_envelope": [
        min(results_arms[n]["tail_100"]["p5"] for n in env_names),
        max(results_arms[n]["tail_100"]["p95"] for n in env_names)],
    "difficulty_share_range_R1": [
        min(results_arms[n]["variance_decomposition_R1"]["difficulty_share"] for n in env_names),
        max(results_arms[n]["variance_decomposition_R1"]["difficulty_share"] for n in env_names)],
    "rotation_share_range_R1": [
        min(results_arms[n]["variance_decomposition_R1"]["rotation_share"] for n in env_names),
        max(results_arms[n]["variance_decomposition_R1"]["rotation_share"] for n in env_names)],
    "replaces_claim": "S1's '99.79% rotation-draw / 1.1x difficulty' (vD=7.57e-4)",
    "downside_p_above_2p5em7_50net_range": [
        min(results_arms[n]["tail_50"]["p_above_2p5em7"]["value"] for n in env_names),
        max(results_arms[n]["tail_50"]["p_above_2p5em7"]["value"] for n in env_names)],
    "downside_p_above_2p5em7_100net_range": [
        min(results_arms[n]["tail_100"]["p_above_2p5em7"]["value"] for n in env_names),
        max(results_arms[n]["tail_100"]["p_above_2p5em7"]["value"] for n in env_names)],
}

results = {
    "experiment": "s1b_dispersion_corrected",
    "date": "2026-08-10",
    "parent": "s1_suite_risk/run_s1.py (copied; ONLY dispersion parameter varied)",
    "champion_designation": "R=1 (U9 slot A)",
    "anchor": ANCHOR,
    "design": {
        "n_suites_main": N_SUITES, "n_chunks_main": N_CHUNKS,
        "n_suites_tail": N_TAIL, "n_chunks_tail": N_TAIL_CHUNKS,
        "suite_sizes": [50, 100], "thresholds": [tkey(T) for T in THRESH],
        "master_seed": MASTER_SEED,
        "seed_layout": "committed prefix (spawn(4)+spawn(2)) then new children 6/7/8 "
                       "for 100-net and tail streams; common random numbers across arms",
        "difficulty_model": "log-uniform max/min=DIFF_RATIO, normalized to mean 1 (unchanged)",
        "rotation_pool": "P2 grid 48 values, per-net mean-normalized, mean forced to 1 (unchanged)",
    },
    "calibration": {"vF": vF, "pool_spread": pool_spread, "pool_n": int(pool.size)},
    "vD_derivation": derivation,
    "arms": results_arms,
    "bracketing_test": bracket,
    "headline": headline,
    "crosschecks": {
        "control_reproduces_committed_s1": True,
        "analytic_vs_bootstrap_sd_ratio_50net": {
            n: results_arms[n]["suite_50"]["sd"] / results_arms[n]["suite_50"]["sd_analytic"]
            for n in ARMS},
        "analytic_vs_bootstrap_sd_ratio_100net": {
            n: results_arms[n]["suite_100"]["sd"] / results_arms[n]["suite_100"]["sd_analytic"]
            for n in ARMS},
        "bitwise_repeat_chunk0": {n: results_arms[n]["bitwise_repeat_chunk0_ok"] for n in ARMS},
        "p5_p95_100k_vs_1e6_50net": {
            n: {"p5_ratio": results_arms[n]["suite_50"]["p5"] / results_arms[n]["tail_50"]["p5"],
                "p95_ratio": results_arms[n]["suite_50"]["p95"] / results_arms[n]["tail_50"]["p95"]}
            for n in ARMS},
        "input_p2_means_vs_s17_champion_mse_max_rel_diff": float(
            np.max(np.abs(p2_means / s17_champ - 1.0))),
    },
    "data_files": [P2_PATH, M185_PATH, A1B_PATH, S17_PATH, S1_PATH],
    "runtime_seconds": round(time.time() - t0, 1),
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=1)
print("bracketing verdict:", bracket["verdict"],
      "| old fails:", bracket["old_model_fails_bracket"],
      "| corrected bracket:", bracket["corrected_arms_bracket"])
print("wrote", OUT_JSON, f"[{time.time()-t0:.1f}s]")
