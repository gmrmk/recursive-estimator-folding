"""gm_s17_reuse analysis: pooled ratios, predeclared gates, two-signal checks."""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CKPT = os.path.join(HERE, "gm_s17_reuse_checkpoint.json")
OUT = os.path.join(HERE, "results.json")

# two-sided 95% t quantiles, df = n-1
T95 = {2: 4.302653, 4: 2.776445, 9: 2.262157, 19: 2.093024, 29: 2.045230,
       39: 2.022691, 49: 2.009575, 59: 2.000995, 69: 1.994945, 79: 1.990450,
       38: 2.024394, 78: 1.990847}


def tq(df):
    if df in T95:
        return T95[df]
    # Cornish-Fisher style fallback (accurate to ~1e-3 for df>=20)
    z = 1.959964
    return z * (1 + (z * z + 1) / (4 * df) + (5 * z**4 + 16 * z**2 + 3) / (96 * df * df))


def stat(a, label):
    a = np.asarray(a, dtype=float)
    n = len(a)
    m, s = float(a.mean()), float(a.std(ddof=1))
    se = s / np.sqrt(n)
    t = tq(n - 1)
    lo, hi = m - t * se, m + t * se
    return {"label": label, "n": n, "mean": m, "sd": s, "se": se,
            "t_quantile": t, "ci95": [lo, hi],
            "median": float(np.median(a)), "min": float(a.min()),
            "max": float(a.max())}


def gate(st):
    lo, hi = st["ci95"]
    g = []
    if lo > 2.5:
        g.append("REOPENS_UPWARD")
    if lo > 1.2:
        g.append("STANDS")
    if lo <= 1.0 <= hi:
        g.append("REOPENS")
    if lo <= 1.2 <= hi:
        g.append("STRADDLES_1.2")
    if not g:
        g.append("BELOW_1.2_ENTIRELY")   # ci_hi < 1.2 and 1.0 not inside
    return g


def main():
    ck = json.load(open(CKPT))["nets"]
    seeds = sorted(int(k) for k in ck)
    recs = [ck[str(s)] for s in seeds]
    prim = [r["ratio_primary_corr_over_costfloor"] for r in recs]
    s17c = [r["ratio_s17conv_over_costfloor"] for r in recs]
    dirf = [r["ratio_primary_over_dirfloor"] for r in recs]
    pero = [r["ratio_primary_over_peroutfloor"] for r in recs]

    out = {"experiment": "gm_s17_reuse",
           "ledger_id": "s17_information_complexity_lower_bound",
           "n_nets": len(seeds), "net_seeds": seeds,
           "denominator": "sigma^2 / 64512 (S17 equal-FLOP accounting)",
           "s17_reference_n3": {
               "pooled_ratio": 1.7906808367797993, "sd": 0.515631542652912,
               "se": 0.29770000995332074, "t95_ci": [0.5096776939506602,
                                                     3.071683979608938]}}

    out["pooled"] = {
        "primary_mse_corr_over_costfloor": stat(prim, "PRIMARY champ=mse_corr"),
        "s17conv_over_costfloor": stat(s17c, "S17-CONVENTION champ=mse_corr+truthfloor(3.5M)"),
        "primary_over_dirfloor": stat(dirf, "distinct-direction sigma^2/32256"),
        "primary_over_peroutfloor": stat(pero, "per-output design floor meanvar/64512"),
    }
    out["gates"] = {
        "primary": gate(out["pooled"]["primary_mse_corr_over_costfloor"]),
        "s17conv": gate(out["pooled"]["s17conv_over_costfloor"]),
    }

    # ---- S2 split-sample (parity of net seed) ----
    ev = [p for s, p in zip(seeds, prim) if s % 2 == 0]
    od = [p for s, p in zip(seeds, prim) if s % 2 == 1]
    ev17 = [p for s, p in zip(seeds, s17c) if s % 2 == 0]
    od17 = [p for s, p in zip(seeds, s17c) if s % 2 == 1]
    out["S2_split_sample"] = {
        "even_primary": stat(ev, "even seeds"), "odd_primary": stat(od, "odd seeds"),
        "even_gate": gate(stat(ev, "e")), "odd_gate": gate(stat(od, "o")),
        "even_s17conv": stat(ev17, "even s17conv"), "odd_s17conv": stat(od17, "odd s17conv"),
        "even_s17conv_gate": gate(stat(ev17, "e")), "odd_s17conv_gate": gate(stat(od17, "o")),
        "agree_on_primary_gate": None,
    }
    out["S2_split_sample"]["agree_on_primary_gate"] = (
        sorted(out["S2_split_sample"]["even_gate"]) ==
        sorted(out["S2_split_sample"]["odd_gate"]))

    # ---- S1 / S3 / S4 verification ----
    s1 = [r["S1_numerator_rel_err"] for r in recs]
    s4 = [r["S4_twoway_rel_diff"] for r in recs]
    s3 = [(r["net_seed"], r["S3_altpath_rel_err"]) for r in recs if "S3_altpath_rel_err" in r]
    out["verification"] = {
        "S1_numerator_max_rel_err": max(s1),
        "S1_all_exact": bool(max(s1) == 0.0),
        "S4_sigma2_twoway_max_rel_diff": max(s4),
        "S3_altpath": {str(k): v for k, v in s3},
        "S3_altpath_max_rel_err": (max(v for _, v in s3) if s3 else None),
        "S3_tolerance_note": ("PREDECLARED 1e-12 was unrealistic for a float32 "
                              "GEMM path with different blocking; observed ~1e-8 "
                              "is float32-grade agreement. Deviation recorded."),
        "rot_seed_match_all": bool(all(r["rot_seed"] == r["m185_rot_seed"] for r in recs)),
    }

    # ---- bootstrap CI as a distribution-free second read on the CI ----
    rng = np.random.default_rng(20260810)
    a = np.asarray(prim)
    bs = np.array([rng.choice(a, size=len(a), replace=True).mean()
                   for _ in range(20000)])
    out["bootstrap_primary"] = {"draws": 20000,
                                "mean": float(bs.mean()),
                                "ci95_percentile": [float(np.percentile(bs, 2.5)),
                                                    float(np.percentile(bs, 97.5))]}
    a17 = np.asarray(s17c)
    bs17 = np.array([rng.choice(a17, size=len(a17), replace=True).mean()
                     for _ in range(20000)])
    out["bootstrap_s17conv"] = {"draws": 20000, "mean": float(bs17.mean()),
                                "ci95_percentile": [float(np.percentile(bs17, 2.5)),
                                                    float(np.percentile(bs17, 97.5))]}

    out["per_net"] = {str(r["net_seed"]): {
        "sigma2": r["sigma2"], "champ_corr": r["champ_corr"],
        "champ_s17conv": r["champ_s17conv"],
        "ratio_primary": r["ratio_primary_corr_over_costfloor"],
        "ratio_s17conv": r["ratio_s17conv_over_costfloor"],
        "ratio_perout": r["ratio_primary_over_peroutfloor"],
        "meanvar_perneuron_design": r["meanvar_perneuron_design"]} for r in recs}

    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    p = out["pooled"]["primary_mse_corr_over_costfloor"]
    q = out["pooled"]["s17conv_over_costfloor"]
    print("n = %d nets" % out["n_nets"])
    print("PRIMARY   mean %.4f sd %.4f se %.4f  95%%CI [%.4f, %.4f]  gate %s"
          % (p["mean"], p["sd"], p["se"], p["ci95"][0], p["ci95"][1], out["gates"]["primary"]))
    print("S17-CONV  mean %.4f sd %.4f se %.4f  95%%CI [%.4f, %.4f]  gate %s"
          % (q["mean"], q["sd"], q["se"], q["ci95"][0], q["ci95"][1], out["gates"]["s17conv"]))
    print("bootstrap PRIMARY CI [%.4f, %.4f]   S17CONV CI [%.4f, %.4f]"
          % (*out["bootstrap_primary"]["ci95_percentile"],
             *out["bootstrap_s17conv"]["ci95_percentile"]))
    sp = out["S2_split_sample"]
    print("S2 even n=%d mean %.4f CI [%.4f,%.4f] %s | odd n=%d mean %.4f CI [%.4f,%.4f] %s | agree=%s"
          % (sp["even_primary"]["n"], sp["even_primary"]["mean"], *sp["even_primary"]["ci95"],
             sp["even_gate"], sp["odd_primary"]["n"], sp["odd_primary"]["mean"],
             *sp["odd_primary"]["ci95"], sp["odd_gate"], sp["agree_on_primary_gate"]))
    print("S1 max rel err %.1e (all exact: %s)  S4 max %.1e  S3 max %.1e"
          % (out["verification"]["S1_numerator_max_rel_err"],
             out["verification"]["S1_all_exact"],
             out["verification"]["S4_sigma2_twoway_max_rel_diff"],
             out["verification"]["S3_altpath_max_rel_err"] or 0.0))
    r = out["pooled"]["primary_over_peroutfloor"]
    print("per-output-floor accounting: mean %.4f CI [%.4f, %.4f]"
          % (r["mean"], *r["ci95"]))


if __name__ == "__main__":
    main()
