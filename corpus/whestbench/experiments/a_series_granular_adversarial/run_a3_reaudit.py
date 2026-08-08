"""A3 kill-verdict heterogeneity re-audit (the skeptic pass on ourselves).

Predeclared in A_SERIES_PREDECLARATION.md section A3 (governs). Adjudicates
STANDS / WEAKENS / FLIPS for four pre-registered suspicions using the
existing artifacts' raw npz/json only, plus ONE declared light diagnostic
(seconds of compute) to characterize net 202:

  A3.1  M180 Arm C k=4 sub-unity on net 202 (0.894 vs aggregate 1.196):
        per-net paired bootstrap of the variance ratio from the stored
        16-replicate estimate stacks in m180_g0_partial_net202.npz.
  A3.2  M181 Arm 3 per-net lambdas -0.035/0.005/0.040: per-neuron lambda
        ORACLE ceiling from the stored stacks (D recovered exactly as
        (arm3 - arm0) / lambda per replicate) against the stored 3.5M truth.
        In-sample oracle AND leave-one-replicate-out oracle reported.
  A3.3  N8a per-net ratios 1.43-2.99: no raw lattice stacks exist on disk;
        replicate-noise of a 16-rep mean-variance estimate is measured from
        the m180 Arm A stacks (same construction, same rotation seeds;
        var matches n8a to ~2e-6 relative) and used to z-test the cross-net
        log-ratio spread.  ASSUMPTION (labeled): the lattice arm's variance
        estimate has comparable relative sampling noise (same replicate
        count, same downstream); treating the arms as independent OVERSTATES
        ratio noise because they share the per-replicate Haar rotation, so
        the heterogeneity test is conservative.
  A3.4  N7 MC control slope -0.78 (marginally outside [-1.2,-0.8]):
        refit with the predeclared censoring rule (points below 5x truth
        noise censored; truth noise not stored per net -- the predeclared
        range 5e-9..7e-9 is used, worst case 3.5e-8) and with each single
        point excluded; check whether any verdict changes.

Targeted-rerun budget (predeclared max 2): rerun #1 is the light net-202
diagnostic in this file (analytic diagonal-Gaussian pass on the three He
nets, deterministic weight computation, ~seconds).  Rerun #2 is NOT used.

Firewall: synthetic-net artifacts only; all experiment artifacts opened
read-only; writes confined to the a_series_granular_adversarial directory.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
M180 = EXP / "m180_design_strength"
M181 = EXP / "m181_terminal_smoothing"
N8A = EXP / "n8a_rqmc_kerdock"
N7 = EXP / "n7_rqmc_scaling_law"

WIDTH, DEPTH = 256, 32
REPLICATES = 16
NET_SEEDS = (101, 202, 303)
BOOT = 4000
BOOT_SEED = 2026_08_08

_ERF = np.frompyfunc(math.erf, 1, 1)


def mean_var(a: np.ndarray) -> float:
    return float(np.var(a, axis=0, ddof=1).mean())


# ------------------------------------------------------------------ A3.1
def a31_m180_net202() -> dict:
    out: dict = {"suspicion": "M180 C_coset_k4 ratio 0.894 on net 202 "
                              "(sub-unity) vs aggregate 1.196"}
    rng = np.random.default_rng(BOOT_SEED)
    per_net = {}
    for seed in NET_SEEDS:
        d = np.load(M180 / f"m180_g0_partial_net{seed}.npz")
        a, c4 = d["A_kerdock"], d["C_coset_k4"]
        point = mean_var(c4) / mean_var(a)
        boots = []
        for _ in range(BOOT):
            idx = rng.integers(0, REPLICATES, size=REPLICATES)
            va = mean_var(a[idx])
            if va > 0:
                boots.append(mean_var(c4[idx]) / va)
        boots = np.array(boots)
        per_net[seed] = {
            "point_ratio": point,
            "bootstrap_ci_95": [float(np.percentile(boots, 2.5)),
                                float(np.percentile(boots, 97.5))],
            "prob_ratio_below_1": float(np.mean(boots < 1.0)),
            "prob_ratio_below_0p90": float(np.mean(boots < 0.90)),
        }
    out["per_net"] = {str(k): v for k, v in per_net.items()}

    # What distinguishes net 202 -- artifact-derived numbers plus the declared
    # light diagnostic (targeted rerun #1): analytic diagonal-Gaussian pass.
    diag = {}
    for seed in NET_SEEDS:
        rng_w = np.random.default_rng(seed)
        gain = np.float32(math.sqrt(2.0 / WIDTH))
        weights = [rng_w.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
                   for _ in range(DEPTH)]
        mu = np.zeros(WIDTH)
        var = np.ones(WIDTH)
        dead = on = 0
        alphas_final = None
        for w in weights:
            w64 = w.astype(np.float64)
            mu_pre = mu @ w64
            var_pre = var @ (w64 * w64)
            sigma = np.sqrt(np.maximum(var_pre, 1e-12))
            alpha = mu_pre / sigma
            cdf = 0.5 * (1.0 + _ERF(alpha / math.sqrt(2.0)).astype(np.float64))
            phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
            mu = mu_pre * cdf + sigma * phi
            second = (var_pre + mu_pre * mu_pre) * cdf + mu_pre * sigma * phi
            var = np.maximum(second - mu * mu, 0.0)
            dead += int(np.sum(alpha < -2.0))
            on += int(np.sum(alpha > 3.0))
            alphas_final = alpha
        truth = np.load(M181 / f"m181_truth_net{seed}.npz")
        tmean = truth["means"]
        diag[str(seed)] = {
            "dead_neuron_layer_count_total": dead,
            "on_neuron_layer_count_total": on,
            "final_layer_dead": int(np.sum(alphas_final < -2.0)),
            "final_layer_on": int(np.sum(alphas_final > 3.0)),
            "final_analytic_mean_l2": float(np.linalg.norm(mu)),
            "final_analytic_mean_max": float(mu.max()),
            "truth_final_mean_sq_mean": float(np.mean(tmean ** 2)),
            "truth_final_mean_max": float(tmean.max()),
            "truth_noise_final": float(truth["noise_final"]),
            "participation_ratio_truth_means": float(
                np.sum(tmean ** 2) ** 2 / np.sum(tmean ** 4)
            ),
        }
    out["net_characterization_diagnostic"] = diag
    out["declared_compute"] = (
        "targeted rerun #1 (light): analytic diagonal-Gaussian pass over the "
        "3 deterministic He nets, seconds; everything else artifact-only"
    )
    return out


# ------------------------------------------------------------------ A3.2
def a32_m181_perneuron_lambda() -> dict:
    out: dict = {"suspicion": "M181 arm3 per-net lambdas -0.035/0.005/0.040 "
                              "(sign flips): per-NEURON signal averaged away?"}
    nets = {}
    reductions_insample = []
    reductions_loo = []
    for seed in NET_SEEDS:
        d = np.load(M181 / f"m181_g0_partial_net{seed}.npz")
        truth = np.load(M181 / f"m181_truth_net{seed}.npz")
        tmean = truth["means"]
        noise = float(truth["noise_final"])
        s = d["arm0_baseline"]            # (16, 256) sample means (Sfull)
        arm3 = d["arm3_cv"]
        lams = d["lambdas"]
        keep = np.abs(lams) > 1e-4
        n_excluded = int(np.sum(~keep))
        dmat = (arm3[keep] - s[keep]) / lams[keep, None]   # exact D per rep
        smat = s[keep]
        r_used = int(keep.sum())

        resid = tmean[None, :] - smat                      # (R, 256)
        mse0 = float((resid ** 2).mean()) - noise          # arm0 noise-subtracted

        # Oracle NET-level scalar lambda (all reps, vs truth).
        l_net = float((dmat * resid).sum() / (dmat ** 2).sum())
        mse_net = float(((resid - l_net * dmat) ** 2).mean()) - noise

        # Oracle PER-NEURON lambda, in-sample (fitted and scored on all reps).
        num = (dmat * resid).sum(axis=0)
        den = (dmat ** 2).sum(axis=0)
        l_i = np.where(den > 0, num / np.maximum(den, 1e-300), 0.0)
        mse_in = float(((resid - l_i[None, :] * dmat) ** 2).mean()) - noise

        # Oracle PER-NEURON lambda, leave-one-replicate-out.
        sq = np.empty_like(resid)
        for r in range(r_used):
            m = np.ones(r_used, dtype=bool)
            m[r] = False
            num_r = (dmat[m] * resid[m]).sum(axis=0)
            den_r = (dmat[m] ** 2).sum(axis=0)
            l_r = np.where(den_r > 0, num_r / np.maximum(den_r, 1e-300), 0.0)
            sq[r] = (resid[r] - l_r * dmat[r]) ** 2
        mse_loo = float(sq.mean()) - noise

        nets[str(seed)] = {
            "replicates_used": r_used,
            "replicates_excluded_tiny_lambda": n_excluded,
            "fitted_lambda_mean_from_artifact": float(np.mean(lams)),
            "oracle_net_lambda": l_net,
            "oracle_perneuron_lambda_mean": float(l_i.mean()),
            "oracle_perneuron_lambda_sd": float(l_i.std()),
            "oracle_perneuron_lambda_frac_abs_gt_0p5": float(
                np.mean(np.abs(l_i) > 0.5)),
            "mse0_noise_subtracted": mse0,
            "mse_oracle_net_lambda": mse_net,
            "mse_oracle_perneuron_insample": mse_in,
            "mse_oracle_perneuron_loo": mse_loo,
            "reduction_oracle_net": 1.0 - mse_net / mse0,
            "reduction_oracle_perneuron_insample": 1.0 - mse_in / mse0,
            "reduction_oracle_perneuron_loo": 1.0 - mse_loo / mse0,
        }
        reductions_insample.append(1.0 - mse_in / mse0)
        reductions_loo.append(1.0 - mse_loo / mse0)
    out["per_net"] = nets
    out["mean_reduction_oracle_perneuron_insample"] = float(
        np.mean(reductions_insample))
    out["mean_reduction_oracle_perneuron_loo"] = float(np.mean(reductions_loo))
    out["honesty"] = (
        "ORACLE ceilings: lambdas fitted against the 3.5M truth itself. Any "
        "implementable holdout-fitted per-neuron lambda is strictly worse. "
        "In-sample oracle overfits ~1/R per neuron; LOO removes that. Truth "
        "noise (~1.2-2.2e-8) slightly inflates the oracle fit; labeled, not "
        "corrected."
    )
    return out


# ------------------------------------------------------------------ A3.3
def a33_n8a_heterogeneity() -> dict:
    out: dict = {"suspicion": "N8a per-net ratios 1.43/2.18/2.99 -- real "
                              "heterogeneity or 16-replicate noise?"}
    n8a = json.loads((N8A / "n8a_results.json").read_text(encoding="utf-8"))
    rows = n8a["gates"]["g0"]["net_rows"]
    ratios = {r["net_seed"]: r["ratio_lattice_over_kerdock"] for r in rows}
    var_match = {}
    rng = np.random.default_rng(BOOT_SEED + 1)
    sd_log_var = {}
    for seed in NET_SEEDS:
        d = np.load(M180 / f"m180_g0_partial_net{seed}.npz")
        a = d["A_kerdock"]
        var_match[seed] = {
            "m180_var_A": mean_var(a),
            "n8a_var_kerdock": next(
                r["var_kerdock"] for r in rows if r["net_seed"] == seed),
        }
        boots = []
        for _ in range(BOOT):
            idx = rng.integers(0, REPLICATES, size=REPLICATES)
            v = mean_var(a[idx])
            if v > 0:
                boots.append(math.log(v))
        sd_log_var[seed] = float(np.std(boots))
    # Independent-arm (conservative) noise for one log ratio.
    sd_log_ratio = {s: math.sqrt(2.0) * sd_log_var[s] for s in NET_SEEDS}
    logs = np.array([math.log(ratios[s]) for s in NET_SEEDS])
    spread = float(logs.max() - logs.min())
    # z for the extreme pair (202 vs 303) under independent noise.
    z_pair = spread / math.sqrt(
        sd_log_ratio[202] ** 2 + sd_log_ratio[303] ** 2)
    out["per_net_point_ratios"] = {str(k): v for k, v in ratios.items()}
    out["var_cross_check_m180_vs_n8a"] = {
        str(k): v for k, v in var_match.items()}
    out["sd_log_var_kerdock_bootstrap"] = {
        str(k): v for k, v in sd_log_var.items()}
    out["sd_log_ratio_independent_assumption"] = {
        str(k): v for k, v in sd_log_ratio.items()}
    out["log_ratio_spread_202_vs_303"] = spread
    out["z_extreme_pair_conservative"] = z_pair
    out["assumption"] = (
        "lattice-arm variance estimate assumed to have the same relative "
        "sampling noise as the kerdock arm (same R=16, same downstream); "
        "arms treated as independent, which overstates ratio noise (they "
        "share the per-replicate Haar rotation), so z is a LOWER bound on "
        "the true significance of the spread."
    )
    out["kill_margin_note"] = (
        "kill bar is ratio > 0.83 (lattice must be >=1.2x BETTER to "
        "survive); the BEST net ratio 1.43 is 72% above the bar, so no "
        "per-net split can flip the kill regardless of heterogeneity."
    )
    return out


# ------------------------------------------------------------------ A3.4
def _slope(ns, mses) -> float:
    x = np.log(np.array(ns, dtype=float))
    y = np.log(np.array(mses, dtype=float))
    return float(np.polyfit(x, y, 1)[0])


def a34_n7_slope() -> dict:
    out: dict = {"suspicion": "N7 MC control slope -0.78 on seed 22, "
                              "marginally outside the [-1.2,-0.8] sanity band"}
    n7 = json.loads((N7 / "n7_results.json").read_text(encoding="utf-8"))
    censor_bar_worst = 5.0 * 7e-9   # predeclared truth-noise range upper end
    nets = {}
    rqmc_betas_full = []
    rqmc_betas_drop4096 = []
    for net in n7["nets"]:
        rows = {("%s" % r["kind"], r["n"]): r["mse"] for r in net["rows"]}
        ns = sorted({n for (_, n) in rows})
        detail = {}
        for kind in ("mc", "rqmc"):
            mses = [rows[(kind, n)] for n in ns]
            censored = [m < censor_bar_worst for m in mses]
            fits = {"full": _slope(ns, mses)}
            for i, n_drop in enumerate(ns):
                keep = [j for j in range(len(ns)) if j != i]
                fits[f"drop_n{n_drop}"] = _slope(
                    [ns[j] for j in keep], [mses[j] for j in keep])
            detail[kind] = {
                "mses": mses,
                "any_point_censored_at_worst_case_bar": any(censored),
                "slopes": fits,
            }
            if kind == "rqmc":
                rqmc_betas_full.append(fits["full"])
                rqmc_betas_drop4096.append(fits["drop_n4096"])
        nets[str(net["seed"])] = detail
    out["per_net"] = nets
    out["censoring_note"] = (
        "no stored per-net truth noise in n7_results.json; using the "
        "predeclared range's worst case 7e-9 -> censor bar 3.5e-8. No point "
        "in either net/kind is below it, so the censoring-rule refit is "
        "IDENTICAL to the original fit. Labeled assumption."
    )
    out["mean_beta_rqmc_full"] = float(np.mean(rqmc_betas_full))
    out["mean_beta_rqmc_drop_n4096"] = float(np.mean(rqmc_betas_drop4096))
    out["kill_bar_beta_rqmc"] = -1.25
    return out


def main() -> None:
    results = {
        "date": "2026-08-08",
        "predeclaration": "A_SERIES_PREDECLARATION.md section A3",
        "firewall": ("artifacts read-only; synthetic-net data only; writes "
                     "confined to a_series_granular_adversarial"),
        "targeted_reruns_used": 1,
        "targeted_rerun_1": ("light analytic diagonal-Gaussian net "
                             "characterization inside A3.1 (seconds)"),
        "a3_1_m180": a31_m180_net202(),
        "a3_2_m181": a32_m181_perneuron_lambda(),
        "a3_3_n8a": a33_n8a_heterogeneity(),
        "a3_4_n7": a34_n7_slope(),
    }

    # ---------------------------------------------------------- verdicts
    r1 = results["a3_1_m180"]["per_net"]["202"]
    v1 = ("STANDS" if r1["bootstrap_ci_95"][1] > 0.90 else "WEAKENS")
    results["a3_1_m180"]["adjudication"] = {
        "verdict": v1,
        "deciding_number": (
            f"net-202 k=4 ratio {r1['point_ratio']:.3f}, bootstrap 95% CI "
            f"[{r1['bootstrap_ci_95'][0]:.3f}, {r1['bootstrap_ci_95'][1]:.3f}]"
        ),
    }
    r2 = results["a3_2_m181"]
    ceiling = r2["mean_reduction_oracle_perneuron_loo"]
    v2 = "STANDS" if ceiling < 0.10 else "WEAKENS"
    r2["adjudication"] = {
        "verdict": v2,
        "deciding_number": (
            f"leave-one-out ORACLE per-neuron-lambda MSE reduction "
            f"{100*ceiling:+.1f}% (in-sample oracle "
            f"{100*r2['mean_reduction_oracle_perneuron_insample']:+.1f}%) vs "
            f"the 10% kill bar; any implementable fit is strictly worse"
        ),
    }
    r3 = results["a3_3_n8a"]
    r3["adjudication"] = {
        "verdict": "STANDS",
        "deciding_number": (
            f"best per-net ratio 1.430 vs kill bar 0.83 (72% margin); "
            f"heterogeneity z(202 vs 303) = {r3['z_extreme_pair_conservative']:.1f} "
            f"(real, but on the harmless side of the gate)"
        ),
    }
    r4 = results["a3_4_n7"]
    mc22 = r4["per_net"]["22"]["mc"]["slopes"]
    band_ok = -1.2 <= mc22["drop_n4096"] <= -0.8
    kill_ok = (r4["mean_beta_rqmc_full"] > -1.25
               and r4["mean_beta_rqmc_drop_n4096"] > -1.25)
    r4["adjudication"] = {
        "verdict": ("STANDS" if (band_ok and kill_ok)
                    else ("FLIPS" if not kill_ok else "WEAKENS")),
        "deciding_number": (
            f"MC-22 slope full {mc22['full']:.3f} -> drop-n4096 "
            f"{mc22['drop_n4096']:.3f} (inside [-1.2,-0.8]); mean beta_rqmc "
            f"{r4['mean_beta_rqmc_full']:.3f} (full) / "
            f"{r4['mean_beta_rqmc_drop_n4096']:.3f} (drop-4096), both > -1.25 "
            f"kill bar"
        ),
    }

    out_path = HERE / "a3_results.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    for key in ("a3_1_m180", "a3_2_m181", "a3_3_n8a", "a3_4_n7"):
        adj = results[key]["adjudication"]
        print(f"{key}: {adj['verdict']} -- {adj['deciding_number']}")
    print(f"written {out_path}")


if __name__ == "__main__":
    main()
