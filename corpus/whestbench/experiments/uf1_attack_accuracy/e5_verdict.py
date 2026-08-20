"""E5 -- assemble the verdict arithmetic from E1/E2/E4 artifacts.

Every printed number is either read from a measured artifact or derived here
with the formula shown in the output.  Nothing is asserted that is not computed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

# ---- champion constants, as given in the task / campaign record -------------
ADJ_SCORE = 1.832e-7          # graded adjusted score
C_OVER_B = 0.650              # multiplier
C_CHAMP = 1.7683e11
RAW_MSE = ADJ_SCORE / max(0.1, C_OVER_B)      # = 2.818462e-7
GATE = 2e-5
NETS = (101, 202, 303, 404)
ROTS = (900101001, 900101002, 900101003, 900101004, 900101005, 900101006)
# U-F1's own adjusted-score gains at 57.4164% lane eligibility
UF1_GAIN = {1: 1.0606, 2: 1.1180, 3: 1.1697, 4: 1.2118, 5: 1.2376}


def boot_ci(vals, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    v = np.asarray(vals, dtype=float)
    idx = rng.integers(0, len(v), size=(n, len(v)))
    means = v[idx].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def main() -> None:
    out = {"raw_mse_derivation": f"{ADJ_SCORE} / max(0.1,{C_OVER_B}) = {RAW_MSE:.6e}",
           "raw_mse": RAW_MSE,
           "rms_error_per_neuron": math.sqrt(RAW_MSE)}
    print(f"champion raw MSE  = {ADJ_SCORE:.4e} / {C_OVER_B} = {RAW_MSE:.6e}")
    print(f"per-neuron RMS err= sqrt({RAW_MSE:.6e}) = {math.sqrt(RAW_MSE):.6e}\n")

    # ---------------- E1: the gate's own tail --------------------------------
    e1 = json.loads((HERE / "e1_chain_distribution.json").read_text())
    print("== E1: 33-seed toy-chain parity distribution (U-F1's own harness) ==")
    e1o = {}
    for d in range(6):
        vals = np.array([e1["per_seed"][s][f"d{d}"]["relative_final_error"]
                         for s in e1["seeds"] and map(str, e1["seeds"])])
        lg = np.log(vals)
        mu, sd = lg.mean(), lg.std(ddof=1)
        p_fail = float(1.0 - 0.5 * (1 + math.erf((math.log(GATE) - mu)
                                                 / (sd * math.sqrt(2)))))
        lo, hi = boot_ci(vals)
        e1o[f"d{d}"] = {
            "n": len(vals), "mean": float(vals.mean()),
            "mean_ci95": [lo, hi],
            "median": float(np.median(vals)), "max": float(vals.max()),
            "p95": float(np.quantile(vals, 0.95)),
            "n_pass": int((vals <= GATE).sum()),
            "lognormal_mu": float(mu), "lognormal_sigma": float(sd),
            "P_single_net_exceeds_2e-5": p_fail,
            "P_any_of_50_nets_exceeds": 1 - (1 - p_fail) ** 50,
        }
        print(f" d{d}: mean {vals.mean():.4e} CI95 [{lo:.3e},{hi:.3e}] "
              f"max {vals.max():.4e} pass {int((vals<=GATE).sum())}/{len(vals)} "
              f"| lognormal P(>2e-5)={p_fail:.4f} P(any of 50)={1-(1-p_fail)**50:.4f}")
    out["e1_toy_chain"] = e1o

    # ---------------- E2: the scored quantity --------------------------------
    print("\n== E2: production geometry (64512x256 rows, 28 Strassen layers) ==")
    e2 = {n: json.loads((HERE / f"e2_net{n}.json").read_text()) for n in NETS}
    e2o = {}
    for d in range(6):
        frob = np.array([e2[n][f"d{d}"]["rel_frobenius_per_sample"] for n in NETS])
        cm = np.array([e2[n][f"d{d}"]["rel_colmean"] for n in NETS])
        mse = np.array([e2[n][f"d{d}"]["mse_contribution"] for n in NETS])
        coh = np.array([e2[n][f"d{d}"]["coherence"] for n in NETS])
        lo, hi = boot_ci(mse)
        ratio = mse.mean() / RAW_MSE
        # worst case: injected error perfectly aligned with the existing error
        r_mse_upper = (1 + math.sqrt(mse.max() / RAW_MSE)) ** 2
        r_mse_orth = 1 + mse.mean() / RAW_MSE
        e2o[f"d{d}"] = {
            "rel_frobenius_mean": float(frob.mean()),
            "rel_frobenius_max": float(frob.max()),
            "n_nets_passing_2e-5": int((frob <= GATE).sum()),
            "rel_colmean_mean": float(cm.mean()),
            "coherence_mean": float(coh.mean()),
            "mse_contribution_mean": float(mse.mean()),
            "mse_contribution_ci95": [lo, hi],
            "mse_contribution_max": float(mse.max()),
            "fraction_of_champion_mse": float(ratio),
            "r_mse_if_orthogonal": r_mse_orth,
            "r_mse_worst_case_aligned": r_mse_upper,
        }
        print(f" d{d}: frob {frob.mean():.4e} (max {frob.max():.4e}, "
              f"{int((frob<=GATE).sum())}/4 pass) | colmean_rel {cm.mean():.4e} "
              f"coh {coh.mean():.4f} | dMSE {mse.mean():.4e} "
              f"= {ratio:.3e} x MSE | r_MSE in [{r_mse_orth:.6f}, {r_mse_upper:.6f}]")
    out["e2_production"] = e2o

    allS = json.loads((HERE / "e2_net202_allS.json").read_text())
    out["e2_all31_strassen_net202"] = {
        k: {kk: allS[k][kk] for kk in
            ("rel_frobenius_per_sample", "rel_colmean", "mse_contribution")}
        for k in ("d4", "d5")}
    print(" all-31-layer-Strassen bound (net202): d4 dMSE "
          f"{allS['d4']['mse_contribution']:.4e}, d5 {allS['d5']['mse_contribution']:.4e}")

    # ---------------- bias vs variance of the injected error -----------------
    print("\n== bias/variance split of the injected error over 6 Haar seeds ==")
    bias_o = {}
    for d in (1, 4):
        deltas = []
        for r in ROTS:
            j = json.loads((HERE / f"e2_rot_net101_r{r}.json").read_text())
            deltas.append(np.array(j[f"d{d}"]["colmean"])
                          - np.array(j["colmean_ref"]))
        D = np.stack(deltas)
        bias = D.mean(axis=0)
        total = float(np.mean(D ** 2))
        b2 = float(np.mean(bias ** 2))
        bias_o[f"d{d}"] = {
            "n_rotation_seeds": len(ROTS),
            "mean_squared_delta": total,
            "bias_squared": b2,
            "bias_share": b2 / total,
            "bias_rms": float(np.sqrt(b2)),
            "bias_share_of_champion_mse": b2 / RAW_MSE,
        }
        print(f" d{d}: E[delta^2]={total:.4e}  bias^2={b2:.4e}  "
              f"bias share={b2/total:.4f}  bias^2/MSE={b2/RAW_MSE:.4e}")
    out["bias_decomposition_net101"] = bias_o

    # ---------------- E4: threshold flips -----------------------------------
    flips = {}
    tot_tests = tot_flips = 0
    for n in (101, 202, 303):
        j = json.loads((HERE / f"e4_flips_net{n}.json").read_text())
        flips[str(n)] = j
        for k, v in j.items():
            tot_tests += v["threshold_tests"]
            tot_flips += v["flips_max_predicate"] + v["flips_min_predicate"]
    rule_of_three = 3.0 / tot_tests if tot_flips == 0 else float("nan")
    out["e4_regime_flips"] = {"per_net": flips, "total_tests": tot_tests,
                              "total_flips": tot_flips,
                              "rule_of_three_95pct_upper_rate": rule_of_three}
    print(f"\n== E4: pilot-threshold flips: {tot_flips} over {tot_tests} tests; "
          f"95% upper bound on flip rate = 3/{tot_tests} = {rule_of_three:.3e}")

    # ---------------- score translation --------------------------------------
    print("\n== score translation: cost gain vs MSE penalty ==")
    sc = {}
    for d in (1, 2, 3, 4, 5):
        g = UF1_GAIN[d]
        m = e2o[f"d{d}"]["mse_contribution_mean"]
        r_orth = 1 + m / RAW_MSE
        r_worst = (1 + math.sqrt(e2o[f"d{d}"]["mse_contribution_max"] / RAW_MSE)) ** 2
        sc[f"d{d}"] = {
            "uf1_cost_gain": g,
            "net_gain_if_orthogonal": g / r_orth,
            "net_gain_worst_case": g / r_worst,
            "mse_headroom_ratio": (g - 1) / (r_worst - 1) if r_worst > 1 else float("inf"),
        }
        print(f" d{d}: cost gain {g:.4f} / r_MSE_worst {r_worst:.6f} "
              f"= net {g/r_worst:.4f}  (gain survives by "
              f"{(g-1)/(r_worst-1):.1f}x margin)")
    out["score_translation"] = sc

    # what would have to be true to kill it at d=4
    g4 = UF1_GAIN[4]
    need_r = g4                       # MSE penalty that exactly cancels the gain
    need_rms = (math.sqrt(need_r) - 1) * math.sqrt(RAW_MSE)   # aligned worst case
    have_rms = math.sqrt(e2o["d4"]["mse_contribution_mean"])
    out["kill_condition_d4"] = {
        "required_r_mse_to_cancel_gain": need_r,
        "required_rms_delta_aligned": need_rms,
        "measured_rms_delta": have_rms,
        "amplification_factor_required": need_rms / have_rms,
        "mse_amplification_required": (need_rms / have_rms) ** 2,
    }
    print(f"\n KILL CONDITION at d=4: r_MSE would have to reach {need_r:.4f}, i.e.")
    print(f"   injected RMS per-neuron error >= (sqrt({need_r:.4f})-1)*"
          f"{math.sqrt(RAW_MSE):.4e} = {need_rms:.4e}")
    print(f"   measured injected RMS = {have_rms:.4e}  ->  a factor "
          f"{need_rms/have_rms:.1f}x in RMS ({(need_rms/have_rms)**2:.0f}x in MSE) "
          f"would be required")

    (HERE / "e5_verdict.json").write_text(json.dumps(out, indent=2),
                                          encoding="utf-8")
    print("\nwrote e5_verdict.json")


if __name__ == "__main__":
    main()
