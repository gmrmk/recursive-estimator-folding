"""gm_a1b_diffflag: does a PERFECT net-difficulty oracle beat a1b's measured
0.50/0.50 top-quartile flag under the S1b-corrected dispersion model?

Cheapest falsifier as mined (nseries record, ledger id a1b_tail_apriori_flag):
re-run a1b's EXACT test with a simulated perfect net-difficulty oracle under the
S1b generative model, D log-uniform mean-1 at vD in {7.57e-4, 0.0814, 0.1220},
F resampled from the archived 48-value P2 pool, n=80, top-quartile-flag vs
top-quartile-target precision/recall.

Gates: see PREDECLARATION.md (written before this file).
Read-only inputs: p2_results.json, m185_g0_stage1_checkpoint.json,
m185_g0_stage2_checkpoint.json, a1b_tail_diagnostics.json, s1b_results.json.
No truth/scorer/holdout, no network, no submissions.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
            r"\publish\recursive-estimator-folding")
EXP = ROOT / "corpus" / "whestbench" / "experiments"
P2_PATH = EXP / "pb1_premise_battery" / "p2_results.json"
A_DIR = EXP / "a_series_granular_adversarial"
S1B_PATH = EXP / "s1b_dispersion_corrected" / "s1b_results.json"
OUT = EXP / "gm_a1b_diffflag" / "results.json"

N_NETS = 80
REPS_PER_STREAM = 100_000
BLOCK = 10_000
MASTER_SEED = 20260810
NET_KEYS = ("101", "202", "303")

t0 = time.time()
res = {"experiment": "gm_a1b_diffflag", "n_nets": N_NETS,
       "reps_per_stream": REPS_PER_STREAM, "streams": 2, "master_seed": MASTER_SEED}


# ---------------------------------------------------------------- inputs
p2 = json.load(open(P2_PATH))
per_net = p2["q1_oracle_headroom"]["per_net"]
pool_parts = []
for seed, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    pool_parts.append(m / m.mean())
POOL = np.concatenate(pool_parts)
POOL = POOL / POOL.mean()
vF = float(POOL.var())

s1b = json.load(open(S1B_PATH))
assert abs(vF - s1b["calibration"]["vF"]) < 1e-15, (vF, s1b["calibration"]["vF"])
assert POOL.size == s1b["calibration"]["pool_n"] == 48

VD = {
    "old_control": s1b["arms"]["old_control"]["vD"],
    "s17_low": s1b["arms"]["s17_low"]["vD"],
    "s17_high": s1b["arms"]["s17_high"]["vD"],
}
res["inputs"] = {"vF": vF, "pool_n": int(POOL.size),
                 "pool_spread": float(POOL.max() / POOL.min()), "vD": VD}
print("vF =", repr(vF), " vD =", VD, flush=True)


# ------------------------------------------- log-uniform difficulty helpers
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


ARM = {}
for name, vd in VD.items():
    ratio = ratio_of_vD(vd)
    half = np.log(ratio) / 2.0
    ARM[name] = {"vD": vd, "ratio": ratio, "half": half,
                 "d_mean": float(np.sinh(half) / half)}
    assert abs(vD_of_ratio(ratio) - vd) < 1e-9 * max(vd, 1e-12)
    # cross-check against s1b's own committed diff_ratio
    assert abs(ratio - s1b["arms"][name]["diff_ratio"]) < 1e-9 * ratio


# --------------------------------------------------- STEP 0: arithmetic gate
step0 = {"formula_lin": "sqrt(vD/(vD+vF))",
         "formula_log": "sqrt(vlogD/(vlogD+vlogF)), vlogD = half^2/3",
         "vlogF": float(np.log(POOL).var()), "per_arm": {}}
for name, a in ARM.items():
    rho_lin = float(np.sqrt(a["vD"] / (a["vD"] + vF)))
    vlogD = a["half"] ** 2 / 3.0
    rho_log = float(np.sqrt(vlogD / (vlogD + step0["vlogF"])))
    step0["per_arm"][name] = {"vD": a["vD"], "rho_ceiling_lin": rho_lin,
                              "vlogD": float(vlogD), "rho_ceiling_log": rho_log}
    print(f"STEP0 {name:11s} vD={a['vD']:.6g}  rho_lin={rho_lin:.4f}  rho_log={rho_log:.4f}",
          flush=True)
corrected = ("s17_low", "s17_high")
step0["kill_threshold"] = 0.75
step0["kills"] = bool(all(step0["per_arm"][n]["rho_ceiling_lin"] >= 0.75
                          and step0["per_arm"][n]["rho_ceiling_log"] >= 0.75
                          for n in corrected))
res["step0"] = step0
print("STEP0 kill (>=0.75 both formulas, both corrected arms):", step0["kills"], flush=True)
if step0["kills"]:
    res["verdict"] = "KILL_CONFIRMED_AT_STEP0"
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    sys.exit(0)


# ------------------------------- provenance cross-check: reproduce a1b exactly
def spearman_a1b(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


nets = json.loads((A_DIR / "m185_g0_stage1_checkpoint.json").read_text())["nets"]
keys = sorted(nets, key=lambda k: int(k))
mse_raw = np.array([nets[k]["mse_raw"] for k in keys])
diags = {
    "diag_proxy_l28": np.array([nets[k]["diag_proxy_l28"] for k in keys]),
    "all_layer_mse": np.array([nets[k]["all_layer_mse"] for k in keys]),
    "borderline_frac": np.array([nets[k]["borderline_frac_overall"] for k in keys]),
    "pruned_frac": np.array([nets[k]["pruned_frac_overall"] for k in keys]),
    "fold_on_total": np.array([nets[k]["fold_on_total"] for k in keys]),
    "fold_kink_total": np.array([nets[k]["fold_kink_total"] for k in keys]),
    "billed_flops": np.array([nets[k]["billed_flops"] for k in keys]),
}
a1b_ref = json.load(open(A_DIR / "a1b_tail_diagnostics.json"))
repro = {"n": len(keys), "spread": float(mse_raw.max() / mse_raw.min()),
         "spearman": {k: spearman_a1b(mse_raw, v) for k, v in diags.items()}}
best_name = max(repro["spearman"], key=lambda k: abs(repro["spearman"][k]))
best = diags[best_name]
if repro["spearman"][best_name] > 0:
    flagged = best >= np.quantile(best, 0.75)
else:
    flagged = best <= np.quantile(best, 0.25)
tail = mse_raw >= np.quantile(mse_raw, 0.75)
tp = int((flagged & tail).sum()); fp = int((flagged & ~tail).sum())
fn = int((~flagged & tail).sum())
repro["best_flag"] = best_name
repro["flag_precision"] = tp / (tp + fp)
repro["flag_recall"] = tp / (tp + fn)
repro["n_flagged"] = int(flagged.sum())
repro["n_tail"] = int(tail.sum())
assert abs(repro["spread"] - a1b_ref["spread"]) < 1e-12
for k in diags:
    assert abs(repro["spearman"][k] - a1b_ref["spearman"][k]) < 1e-12, k
assert repro["best_flag"] == a1b_ref["best_flag"]
assert repro["flag_precision"] == a1b_ref["flag_precision"]
assert repro["flag_recall"] == a1b_ref["flag_recall"]
repro["reproduces_committed_a1b_json"] = True
res["a1b_reproduction"] = repro
print(f"a1b reproduction: EXACT  (best {best_name} rho "
      f"{repro['spearman'][best_name]:+.4f}, prec {repro['flag_precision']:.2f}, "
      f"rec {repro['flag_recall']:.2f}, flagged {repro['n_flagged']}, tail {repro['n_tail']})",
      flush=True)

# quartile-selection equivalence check: with no ties, "x >= quantile(x,0.75)"
# picks exactly the top 20 of 80. Verified on real random draws below.


# ----------------------------------------------------------- MC machinery
def ranks_rows(a):
    """Row-wise 0-based ranks, identical to argsort(argsort(.)) per row."""
    order = np.argsort(a, axis=1, kind="stable")
    r = np.empty_like(order)
    idx = np.arange(a.shape[1])[None, :].repeat(a.shape[0], axis=0)
    np.put_along_axis(r, order, idx, axis=1)
    return r


def mc_block(rng, arm, n_reps, oracle_mode="perfect"):
    """Returns (spearman, precision, recall) arrays of length n_reps."""
    a = ARM[arm]
    D = np.exp(rng.uniform(-a["half"], a["half"], size=(n_reps, N_NETS))) / a["d_mean"]
    F = POOL[rng.integers(0, POOL.size, size=(n_reps, N_NETS))]
    M = D * F
    if oracle_mode == "perfect":
        O = D
    elif oracle_mode == "null":                     # independent of D: permutation null
        O = np.exp(rng.uniform(-a["half"], a["half"], size=(n_reps, N_NETS))) / a["d_mean"]
    else:
        raise ValueError(oracle_mode)
    rO = ranks_rows(O).astype(np.float64)
    rM = ranks_rows(M).astype(np.float64)
    rO -= rO.mean(axis=1, keepdims=True)
    rM -= rM.mean(axis=1, keepdims=True)
    sp = (rO * rM).sum(axis=1) / np.sqrt((rO ** 2).sum(axis=1) * (rM ** 2).sum(axis=1))
    cut = N_NETS - N_NETS // 4                      # 60 -> top 20 of 80
    fl = ranks_rows(O) >= cut
    tl = ranks_rows(M) >= cut
    tp = (fl & tl).sum(axis=1).astype(np.float64)
    prec = tp / fl.sum(axis=1)
    rec = tp / tl.sum(axis=1)
    return sp, prec, rec


# one-time verification that the rank-based quartile == a1b's np.quantile form
_rng = np.random.default_rng(7)
_a = ARM["s17_high"]
_D = np.exp(_rng.uniform(-_a["half"], _a["half"], size=(200, N_NETS))) / _a["d_mean"]
_F = POOL[_rng.integers(0, POOL.size, size=(200, N_NETS))]
_M = _D * _F
_ok = True
for i in range(200):
    fl_q = _D[i] >= np.quantile(_D[i], 0.75)
    tl_q = _M[i] >= np.quantile(_M[i], 0.75)
    fl_r = ranks_rows(_D[i:i + 1])[0] >= 60
    tl_r = ranks_rows(_M[i:i + 1])[0] >= 60
    _ok &= bool(np.array_equal(fl_q, fl_r) and np.array_equal(tl_q, tl_r))
res["quantile_equivalence_check"] = {"n_checked": 200, "identical": _ok}
assert _ok, "rank-based quartile does not match np.quantile form"
print("quantile-form equivalence (200 random reps): IDENTICAL", flush=True)


def run_stream(arm, seed, n_reps, mode="perfect"):
    rng = np.random.default_rng(seed)
    sps, prs, rcs = [], [], []
    done = 0
    while done < n_reps:
        b = min(BLOCK, n_reps - done)
        sp, pr, rc = mc_block(rng, arm, b, mode)
        sps.append(sp); prs.append(pr); rcs.append(rc)
        done += b
    return np.concatenate(sps), np.concatenate(prs), np.concatenate(rcs)


# ------------------------------------- population-limit analytic (2nd signal)
def pop_limit(arm):
    """n -> infinity oracle precision and Spearman, by exact enumeration over the
    48-point F pool + deterministic quadrature over D. Independent of the MC."""
    a = ARM[arm]
    h, dm = a["half"], a["d_mean"]

    def cdf_D(d):
        d = np.asarray(d, dtype=np.float64)
        u = (np.log(np.maximum(d, 1e-300) * dm) + h) / (2 * h)
        return np.clip(u, 0.0, 1.0)

    def cdf_M(m):
        return np.mean([cdf_D(m / f) for f in POOL], axis=0)

    qD = float(np.exp(0.5 * h) / dm)                       # exact 0.75 quantile of D
    lo, hi = POOL.min() * np.exp(-h) / dm, POOL.max() * np.exp(h) / dm
    for _ in range(300):                                    # bisect for 0.75 quantile of M
        mid = 0.5 * (lo + hi)
        if float(cdf_M(mid)) < 0.75:
            lo = mid
        else:
            hi = mid
    qM = 0.5 * (lo + hi)
    joint = float(np.mean([1.0 - cdf_D(max(qD, qM / f)) for f in POOL]))
    prec = joint / 0.25
    # population Spearman = 12*E[F_D(D) F_M(M)] - 3 ; substitute u = F_D(D) ~ U(0,1)
    u = (np.arange(200_000) + 0.5) / 200_000
    d = np.exp(h * (2 * u - 1)) / dm
    acc = 0.0
    for f in POOL:
        acc += float(np.mean(u * cdf_M(d * f)))
    sp = 12.0 * acc / POOL.size - 3.0
    return {"quantile_D_075": qD, "quantile_M_075": float(qM),
            "joint_prob": joint, "precision_pop": float(prec), "spearman_pop": float(sp)}


# ------------------------------------------------------------------ run arms
res["arms"] = {}
for name in ("old_control", "s17_low", "s17_high"):
    seeds = np.random.SeedSequence(MASTER_SEED).spawn(8)
    i = ("old_control", "s17_low", "s17_high").index(name)
    sA, pA, rA = run_stream(name, seeds[2 * i], REPS_PER_STREAM)
    sB, pB, rB = run_stream(name, seeds[2 * i + 1], REPS_PER_STREAM)
    sp = np.concatenate([sA, sB]); pr = np.concatenate([pA, pB]); rc = np.concatenate([rA, rB])
    _, pN, _ = run_stream(name, seeds[6], 20_000, mode="null")
    pop = pop_limit(name)

    def stat(x):
        return {"mean": float(x.mean()),
                "se": float(x.std(ddof=1) / np.sqrt(x.size)),
                "sd": float(x.std(ddof=1)),
                "p5": float(np.percentile(x, 5)), "p50": float(np.percentile(x, 50)),
                "p95": float(np.percentile(x, 95))}

    arm_res = {
        "vD": ARM[name]["vD"], "diff_ratio": ARM[name]["ratio"],
        "oracle_spearman": stat(sp), "oracle_precision": stat(pr), "oracle_recall": stat(rc),
        "precision_equals_recall_always": bool(np.array_equal(pr, rc)),
        "split_sample": {"streamA_precision_mean": float(pA.mean()),
                         "streamB_precision_mean": float(pB.mean()),
                         "abs_diff": float(abs(pA.mean() - pB.mean())),
                         "pooled_se3": float(3 * np.sqrt(pA.var(ddof=1) / pA.size
                                                         + pB.var(ddof=1) / pB.size)),
                         "streamA_spearman_mean": float(sA.mean()),
                         "streamB_spearman_mean": float(sB.mean())},
        "null_oracle_precision_mean": float(pN.mean()),
        "null_oracle_precision_se": float(pN.std(ddof=1) / np.sqrt(pN.size)),
        "population_limit": pop,
        "p_oracle_precision_le_0p50": float((pr <= 0.50 + 1e-12).mean()),
        "p_oracle_precision_le_a1b_0p50": float((pr <= 0.50 + 1e-12).mean()),
        "analytic_rho_ceiling_lin": step0["per_arm"][name]["rho_ceiling_lin"],
        "analytic_rho_ceiling_log": step0["per_arm"][name]["rho_ceiling_log"],
        "sha256_precision_stream_A": hashlib.sha256(pA.tobytes()).hexdigest(),
        "sha256_precision_stream_B": hashlib.sha256(pB.tobytes()).hexdigest(),
    }
    arm_res["split_sample"]["agree_within_3se"] = bool(
        arm_res["split_sample"]["abs_diff"] <= arm_res["split_sample"]["pooled_se3"])
    res["arms"][name] = arm_res
    print(f"{name:11s} vD={ARM[name]['vD']:.6g} | oracle rho {sp.mean():.4f} "
          f"(pop {pop['spearman_pop']:.4f}) | precision {pr.mean():.4f} "
          f"(pop {pop['precision_pop']:.4f}) [p5 {np.percentile(pr,5):.3f} "
          f"p95 {np.percentile(pr,95):.3f}] | null {pN.mean():.4f} "
          f"[{time.time()-t0:.1f}s]", flush=True)

# bitwise repeat of stream A on the decisive arm
seeds = np.random.SeedSequence(MASTER_SEED).spawn(8)
_, pR, _ = run_stream("s17_high", seeds[5], REPS_PER_STREAM)
_rep_sha = hashlib.sha256(pR.tobytes()).hexdigest()
res["bitwise_repeat_s17_high_streamB"] = {
    "sha256": _rep_sha,
    "original_sha256": res["arms"]["s17_high"]["sha256_precision_stream_B"],
    "matches_original": bool(_rep_sha == res["arms"]["s17_high"]["sha256_precision_stream_B"])}
print("bitwise repeat (s17_high stream B):",
      res["bitwise_repeat_s17_high_streamB"]["matches_original"], flush=True)

# monotonicity control: a huge-vD arm must drive precision -> 1
ARM["huge"] = None
_h_ratio = ratio_of_vD(50.0)
ARM["huge"] = {"vD": 50.0, "ratio": _h_ratio, "half": np.log(_h_ratio) / 2.0,
               "d_mean": float(np.sinh(np.log(_h_ratio) / 2.0) / (np.log(_h_ratio) / 2.0))}
_, pH, _ = run_stream("huge", seeds[7], 20_000)
res["control_huge_vD50_precision_mean"] = float(pH.mean())
print("control vD=50 precision:", res["control_huge_vD50_precision_mean"], flush=True)


# ------------------------------------------- realizable-gain bound (stage 2)
st2 = json.loads((A_DIR / "m185_g0_stage2_checkpoint.json").read_text())
sel = st2["selection"]


def geo_ratio(group, arm_name):
    lr = []
    for nid in group:
        rec = st2["nets"][str(nid)]["arms"]
        s_def = rec["default"]["mse_raw"] * rec["default"]["billed_flops_mean"]
        s_alt = rec[arm_name]["mse_raw"] * rec[arm_name]["billed_flops_mean"]
        lr.append(np.log(s_alt / s_def))
    lr = np.array(lr)
    n = lr.size
    se = lr.std(ddof=1) / np.sqrt(n)
    return {"geomean_ratio": float(np.exp(lr.mean())), "n": int(n),
            "ci95_lo": float(np.exp(lr.mean() - 2.776 * se)),
            "ci95_hi": float(np.exp(lr.mean() + 2.776 * se))}


gain = {"score_definition": "score = mse_raw * billed_flops_mean (adjusted score)",
        "worst_group": sel["worst"], "median_group": sel["median"],
        "relaxed_vs_default": {"worst": geo_ratio(sel["worst"], "relaxed"),
                               "median": geo_ratio(sel["median"], "relaxed")},
        "unpruned_vs_default": {"worst": geo_ratio(sel["worst"], "unpruned"),
                                "median": geo_ratio(sel["median"], "unpruned")}}
g_w = gain["relaxed_vs_default"]["worst"]["geomean_ratio"]
g_m = gain["relaxed_vs_default"]["median"]["geomean_ratio"]
gain["g_worst"] = g_w
gain["g_median"] = g_m
gain["per_net_gain_if_correctly_flagged"] = 1.0 - g_w
gain["per_net_loss_if_wrongly_flagged"] = g_m - 1.0
denom = (g_m - 1.0) + (1.0 - g_w)
gain["breakeven_precision"] = float((g_m - 1.0) / denom) if denom > 0 else None
gain["per_vD"] = {}
for name in ("old_control", "s17_low", "s17_high"):
    p = res["arms"][name]["oracle_precision"]["mean"]
    val = 0.25 * (p * (1.0 - g_w) + (1.0 - p) * (1.0 - g_m))
    gain["per_vD"][name] = {"vD": ARM[name]["vD"], "oracle_precision": p,
                            "suite_gain_fraction": float(val),
                            "suite_gain_pct": float(100 * val),
                            "positive": bool(val > 0)}
gain["perfect_precision_1p0_suite_gain_pct"] = float(100 * 0.25 * (1.0 - g_w))
res["realizable_gain_bound"] = gain
print("gain bound: g_worst", g_w, "g_median", g_m, "breakeven prec",
      gain["breakeven_precision"], flush=True)
for k, v in gain["per_vD"].items():
    print(f"   {k:11s} prec {v['oracle_precision']:.4f} -> suite gain "
          f"{v['suite_gain_pct']:+.4f}%", flush=True)


# --------------------------------------------------------------- gate verdict
pl = res["arms"]["s17_low"]["oracle_precision"]["mean"]
ph = res["arms"]["s17_high"]["oracle_precision"]["mean"]
a1b_measured = res["a1b_reproduction"]["flag_precision"]
inside_low = (res["arms"]["s17_low"]["oracle_precision"]["p5"] <= a1b_measured
              <= res["arms"]["s17_low"]["oracle_precision"]["p95"])
inside_high = (res["arms"]["s17_high"]["oracle_precision"]["p5"] <= a1b_measured
               <= res["arms"]["s17_high"]["oracle_precision"]["p95"])
kill = bool(pl >= 0.65 and ph >= 0.65)
revive = bool(pl <= 0.60 and ph <= 0.60 and (inside_low or inside_high))
res["gate"] = {
    "gate_text": "perfect oracle materially above a1b's 0.50 (>=0.65) => KILL stands",
    "a1b_measured_precision": a1b_measured,
    "oracle_precision_s17_low": pl, "oracle_precision_s17_high": ph,
    "kill_threshold": 0.65, "revive_threshold": 0.60,
    "a1b_0p50_inside_central90_s17_low": bool(inside_low),
    "a1b_0p50_inside_central90_s17_high": bool(inside_high),
    "result": "KILL_CONFIRMED" if kill else ("REVIVED_PASS" if revive else "INCONCLUSIVE"),
}
res["wall_s"] = time.time() - t0
OUT.write_text(json.dumps(res, indent=1) + "\n")
print("\nGATE:", res["gate"]["result"], f"[{res['wall_s']:.1f}s]", flush=True)
print("wrote", OUT, flush=True)
