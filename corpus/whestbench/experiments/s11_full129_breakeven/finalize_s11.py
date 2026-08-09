"""S11 finalize: read the saved per-rep stacks (s11_stacks.npz), compute the
degree-4-ISOLATED champion-MSE reduction (the quantity the S11 gate is on),
and write the corrected s11_results.json.

Key correction over the raw completion-vs-126 comparison: the direct
measurement showed completing to 129 reduces raw MSE by ~3.4%, but the
random-frame CONTROL (same +1536 points, deg-4 NOT zeroed) reduces it by
~3.25%. Almost all of the raw reduction is the generic more-samples averaging
benefit -- exactly what the +2.381% point-count cost is meant to offset -- and
is NOT attributable to degree-4 exactness. The task's break-even quantity is
"the fractional champion-MSE reduction from setting the degree-4 design error
to 0" = the degree-4 SHARE. That is isolated by holding point count fixed:
completion(66048, deg4=0) vs control(66048, deg4 present). The control's own
deg-4 error is INFLATED (Phi4/Welch 1.554 > 126-set 1.016), so
completion-vs-control is an UPPER bound on the true 126->129 deg-4 benefit.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
M181 = HERE.parent / "m181_terminal_smoothing"
NET_SEEDS = (101, 202, 303)
N126, NADD, N129 = 64512, 1536, 66048
COST_RATIO = N129 / N126
BREAKEVEN = N126 / N129
BOOT_DRAWS = 20000
BOOT_SEED = 20260809

d = np.load(HERE / "s11_stacks.npz")
truths = {net: dict(np.load(M181 / f"m181_truth_net{net}.npz")) for net in NET_SEEDS}

def stacks(net, key):
    return np.concatenate([d[f"prim_{net}_{key}"], d[f"rese_{net}_{key}"]])

REPS = stacks(101, "f126").shape[0]  # 64

def mse_ns(est, tm, noise):
    return float(((est - tm[None]) ** 2).mean()) - noise

def panel_ratio(numkey, denkey):
    logs, rows = [], []
    for net in NET_SEEDS:
        tm = truths[net]["means"]; noise = float(truths[net]["noise_final"])
        mnum = mse_ns(stacks(net, numkey), tm, noise)
        mden = mse_ns(stacks(net, denkey), tm, noise)
        logs.append(math.log(mnum / mden))
        rows.append({"net_seed": net, f"mse_{denkey}": mden,
                     f"mse_{numkey}": mnum, "ratio": mnum / mden,
                     "reduction_pct": 100 * (1 - mnum / mden)})
    return math.exp(float(np.mean(logs))), rows

def boot(numkey, denkey):
    rng = np.random.default_rng(BOOT_SEED)
    cache = {net: (stacks(net, numkey), stacks(net, denkey),
                   truths[net]["means"], float(truths[net]["noise_final"]))
             for net in NET_SEEDS}
    out = []
    for _ in range(BOOT_DRAWS):
        logs = []
        for net in NET_SEEDS:
            num, den, tm, noise = cache[net]
            idx = rng.integers(0, REPS, size=REPS)
            mn = float(((num[idx] - tm[None]) ** 2).mean()) - noise
            md = float(((den[idx] - tm[None]) ** 2).mean()) - noise
            logs.append(math.log(max(mn, 1e-18) / max(md, 1e-18)))
        out.append(math.exp(float(np.mean(logs))))
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)),
            float(np.mean(np.array(out) < 1.0)))  # P(ratio<1)

def family_ratio(fam, key):
    logs = []
    for net in NET_SEEDS:
        tm = truths[net]["means"]; noise = float(truths[net]["noise_final"])
        mn = mse_ns(d[f"{fam}_{net}_{key}"], tm, noise)
        md = mse_ns(d[f"{fam}_{net}_f126"], tm, noise)
        logs.append(math.log(mn / md))
    return math.exp(float(np.mean(logs)))

# --- three comparisons ---
comp126, comp126_rows = panel_ratio("f129", "f126")   # completion vs 126 (raw)
ctrl126, ctrl126_rows = panel_ratio("fctrl", "f126")  # control vs 126 (more-samples)
deg4, deg4_rows = panel_ratio("f129", "fctrl")        # completion vs control (deg-4 ISOLATED)
comp126_ci = boot("f129", "f126")
ctrl126_ci = boot("fctrl", "f126")
deg4_ci = boot("f129", "fctrl")

deg4_reduction = 1.0 - deg4
def gate(red):
    if red < 0.0233: return "RE-KILLED (below 2.33% break-even)"
    if red > 0.03:  return "ADVANCE-TO-M81-GATES (>~3%; flag Sol, do NOT build)"
    return "INCONCLUSIVE (2.33-3%)"

results = {
    "ledger_id": "s11_full129_reopen_measured_breakeven",
    "date": "2026-08-09",
    "reopen_of": "m81_full129_pareto",
    "one_line_verdict": (
        f"RE-KILLED on the M81 break-even (now MEASURED): the degree-4-"
        f"exactness-attributable champion-MSE reduction is <= "
        f"{100*deg4_reduction:.2f}% (completion vs point-count-matched control, "
        f"UPPER bound), an order of magnitude below the 2.326% break-even; "
        f"corroborated by committed m191 cv_deg4 (+0.42%) and R^2_deg4 (~0.2%). "
        f"The raw completion-vs-126 reduction (+{100*(1-comp126):.2f}%) is "
        f"dominated by generic more-samples averaging (control +"
        f"{100*(1-ctrl126):.2f}%), not degree-4."),
    "break_even": {
        "adjusted_score": "S = MSE * max(0.1, C/B); C proportional to point count",
        "cost_ratio_C129_over_C126": COST_RATIO,
        "mse_ratio_breakeven_bar": BREAKEVEN,
        "required_mse_drop_pct": 100.0 * (1.0 - BREAKEVEN),
        "regime_check": {
            "hosted_326094_adjusted": 1.832e-7, "hosted_326094_mse": 2.818e-7,
            "cb_implied": 1.832e-7 / 2.818e-7,
            "conclusion": "C/B = 0.6501 > 0.1 floor => METERED regime => the "
                          "proportional break-even 2.32558% applies (NOT the "
                          "floored 0.1 regime)."}},
    "design_verification": {
        "method": "verify_design.py exact 4th-moment (Welch) identity, unit dirs",
        "frame129_per_line_sum4": 1.5, "welch_target_3_over_d_d2": 3.0/(256*258),
        "frame129_phi4_over_welch": 1.0,
        "frame126_per_line_sum4": 1.48828125, "frame126_phi4_over_welch": 1.0158110,
        "control_union_phi4_over_welch": 1.55362,
        "conclusion": "129-frame completion (phased-Hadamard idx 0,1 + standard "
                      "basis) is an EXACT spherical 5-design: deg-4 error == 0. "
                      "126-frame and the random-control union are NOT 5-designs."},
    "committed_data": {
        "sufficiency": "INSUFFICIENT to pin the deg-4 SHARE from arithmetic alone: "
            "S6 gives the design's per-degree ERROR operator and m191-g0a the "
            "per-degree error LEVELS (deg4 rms/iid=0.107, deg6=0.40), but neither "
            "pins the champion ESTIMAND's per-degree ENERGY E_l required for "
            "share = E_4 D_4 / sum_l E_l D_l. Hence the direct measurement.",
        "proxy_m191_cv_deg4_reduction": 0.0042,
        "proxy_m191_r2_deg4": [0.00180, 0.00232],
        "proxy_note": "m191 cv_deg4 removed 0.42% of champion MSE by a direct "
            "degree-4 control variate on the 126 design (aligned/removable share, "
            "12-dir basis); R^2_deg4 0.18-0.23%. Both independent of S11's direct "
            "measurement and both << 2.33%."},
    "direct_measurement": {
        "config": {"nets": list(NET_SEEDS), "reps_per_net": REPS,
                   "families": ["matched 900000+net*1000+rep",
                                "reseed 314159+net*1000+rep"],
                   "estimator": "champion plain final-layer antipodal ReLU mean",
                   "truth": "m181_truth 3.5M iid MC, noise subtracted",
                   "bootstrap_draws": BOOT_DRAWS},
        "signal1_bitwise_fhat126_vs_m181_arm0": {"note": "all nets max|diff|=0.0 "
            "on the matched-seed reps (from run_s11.py)"},
        "raw_completion_vs_126": {
            "panel_ratio": comp126, "reduction_pct": 100*(1-comp126),
            "bootstrap_ci95_ratio": comp126_ci[:2], "prob_ratio_below_1": comp126_ci[2],
            "adjusted_score_ratio": comp126 * COST_RATIO, "per_net": comp126_rows,
            "caveat": "CONFOUNDED: includes the more-samples averaging benefit; "
                      "CI includes the 2.326% break-even. NOT the degree-4 share."},
        "control_random3frames_vs_126": {
            "panel_ratio": ctrl126, "reduction_pct": 100*(1-ctrl126),
            "bootstrap_ci95_ratio": ctrl126_ci[:2],
            "adjusted_score_ratio": ctrl126 * COST_RATIO, "per_net": ctrl126_rows,
            "interpretation": "pure more-samples benefit of +1536 generic points "
                "(deg-4 NOT zeroed, in fact inflated). ~equals the completion's "
                "raw reduction => the raw reduction is not from degree-4."},
        "degree4_isolated_completion_vs_control": {
            "panel_ratio": deg4, "reduction_pct": 100*deg4_reduction,
            "bootstrap_ci95_ratio": deg4_ci[:2], "prob_ratio_below_1": deg4_ci[2],
            "per_net": deg4_rows,
            "interpretation": "point-count-matched (both 66048): the ONLY "
                "difference is degree-4 exactness. This is the measured degree-4 "
                "share (an UPPER bound, since the control's own deg-4 error is "
                "inflated vs the 126 set). This is the S11 gate quantity."},
        "per_family_completion_ratio": {
            "primary": family_ratio("prim", "f129"),
            "reseed": family_ratio("rese", "f129"),
            "note": "signal-2 independent-reseed agreement on the raw comparison"}},
    "gate_quantity_degree4_isolated_reduction_pct": 100*deg4_reduction,
    "gate": gate(deg4_reduction),
    "two_signal_verification": (
        "Signal A: direct point-count-matched completion-vs-control measurement "
        f"=> degree-4 reduction {100*deg4_reduction:.2f}% (<= this; upper bound). "
        "Signal B (independent, committed): m191 cv_deg4 direct degree-4 control "
        "variate on the 126 design => 0.42%; R^2_deg4 ~0.2%. Both << 2.33%. "
        "Additional: fhat_126 reproduces cached m181 arm0 bitwise; two independent "
        "rotation families agree on the raw comparison."),
    "memory_ground_status": (
        "M81's memory-margin kill STILL APPLIES and is UNTOUCHED by S11. M81 had "
        "two kill edges: (1) unmeasured variance value -- now measured here and it "
        "FAILS the break-even; (2) min persistent increment 1.75195 MiB vs M71 "
        "frozen margin 1.44531 MiB, crossing the 480 MiB safety gate. Even had the "
        "variance value passed, edge (2) remained a separate blocker for Sol."),
    "firewall": ("synthetic He nets only; kerdock_phases.npz + m181 caches "
                 "read-only; frozen sources imported unmodified; writes confined "
                 "to s11_full129_breakeven; plain numpy; no dataset/scorer/"
                 "submission; no git"),
}

outp = HERE / "s11_results.json"
outp.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print("raw completion vs 126:   ratio %.5f  reduction %+.3f%%  CI[%.5f,%.5f]"
      % (comp126, 100*(1-comp126), *comp126_ci[:2]))
print("control(random) vs 126:  ratio %.5f  reduction %+.3f%%  CI[%.5f,%.5f]"
      % (ctrl126, 100*(1-ctrl126), *ctrl126_ci[:2]))
print("DEG-4 ISOLATED (comp/ctrl): ratio %.5f  reduction %+.3f%%  CI[%.5f,%.5f]  P(<1)=%.3f"
      % (deg4, 100*deg4_reduction, *deg4_ci[:2], deg4_ci[2]))
print("per-family completion: primary %.5f reseed %.5f"
      % (family_ratio("prim","f129"), family_ratio("rese","f129")))
print("adjusted-score S129/S126 = %.5f ; S_ctrl/S126 = %.5f"
      % (comp126*COST_RATIO, ctrl126*COST_RATIO))
print("GATE (degree-4 isolated %.2f%% vs 2.33%%): %s"
      % (100*deg4_reduction, gate(deg4_reduction)))
print("results ->", outp)
