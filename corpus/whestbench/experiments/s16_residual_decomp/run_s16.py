"""S16 -- residual/norm decomposition CONFIRMATORY test.

Ledger id: s16_residual_norm_decomposition_confirm.  CONFIRMATORY (predicts an
IDENTITY, not a new lever).  Converts the assertion "the residual/norm
decomposition reduces to already-promoted/killed machinery" into a measurement.

ALGEBRA under test.  For a ReLU, ReLU(z) = z/2 + |z|/2 (odd half + even half).
The odd half z/2 is cancelled EXACTLY by antipodal pairing:
    ReLU(Wu) + ReLU(-Wu) = |Wu|.
So a "residual-split" estimator -- integrate the linear/odd half to its known
zero mean, keep only the even |.|/2 half -- reconstructs the SAME antipodal set
the champion already propagates, and must be numerically identical.

TESTS (predeclared in the task):
  1. LAYER-1 IDENTITY: ReLU(W1 @ (r u)) + ReLU(W1 @ (r(-u))) == |W1 @ (r u)| to
     machine precision (report max abs deviation over the whole design set).
  2. FULL-ESTIMATOR EQUIVALENCE: residual-split final estimator vs the
     antipodal-paired champion, matched billed sample count; per-net MSE vs
     cached m181 truth + per-direction final outputs.  Predicted ratio ~1.000.
  3. DEEP/CLOSURE ARM: the fully-linear net (all ReLU->identity) has output mean
     EXACTLY 0 under E[x]=0 (verify to MC precision); the "analytic linear +
     Gaussian corrections" closure is the M181/T2 family and lands at that wall
     (~1e-6 mean-neuron MSE, per-neuron dev ~1e-3), NOT below sampling ~2.5e-7
     (M181 committed numbers cited, not re-run).

SCOPE ADD (owner) -- FORM-1 EXACT REPARAMETRIZATION: rewrite each layer as
    y_{l+1} = y_l + F_l,  F_l = ReLU(W_{l+1} y_l) - y_l,
and measure R_l = mean_u ||F_l||_2 / mean_u ||y_l||_2 for l=1..31.  R_l<<1 would
mean a residual/skip perturbative truncation could help (SURPRISE); R_l=O(1)
confirms genuine per-layer transformation (Form-1 reduces to the S8 contraction
law).  Predicted O(1) at all depths.

GATES.  CONFIRMED if (1) layer-1 identity < 1e-10 AND (2) residual-split MSE
matches antipodal within 1% AND (3) linear-part mean ~0 + closure at the M181
wall.  SURPRISE (escalate): residual-split beats antipodal by >10% at matched
billed FLOPs, OR any layer has R_l < 0.3.

FIREWALL: synthetic He nets seeds 101/202/303 (n8a constructor); frozen n8a &
m181 sources imported/loaded READ-ONLY; cached m181 3.5M truth read-only; own
MC for the linear-mean check; single process; writes confined to this dir.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
N8A = EXP / "n8a_rqmc_kerdock"
M181 = EXP / "m181_terminal_smoothing"
sys.path.insert(0, str(N8A))

# frozen n8a machinery, read-only import (no writes at import; ALPHA precompute)
from run_n8a_gates import (  # noqa: E402
    he_mlp_weights, load_kerdock_directions, haar_rotation,
    antipodal_forward_mean, WIDTH, DEPTH, MEAN_CHI_256, N_BASE,
)

NET_SEEDS = (101, 202, 303)
REPLICATES = 16
ROT_SEED = lambda net, r: 900_000 + net * 1_000 + r   # noqa: E731  (n8a formula)
F32 = np.float32

# ---- M181 committed closure/wall numbers (cited, from m181_g0_results.json) ---
# arm0 = antipodal Kerdock forward mean (the SAMPLING baseline == our champion).
# arm1 = one terminal Gaussian-closure step; arm2 = two closure steps.
M181_CITED = {
    "arm0_baseline_mse_raw": {"101": 1.9971998400629498e-07,
                              "202": 5.872094245418941e-07,
                              "303": 2.369255085030329e-07},
    "arm1_univariate_closure_mse_raw": {"101": 9.868304549147735e-07,
                                        "202": 1.7918015108268157e-06,
                                        "303": 1.0551223132088915e-06},
    "arm1_univariate_closure_bias2": {"101": 7.720416214841754e-07,
                                      "202": 1.2005122386727836e-06,
                                      "303": 8.229690345727375e-07},
    "arm2_pairprop_closure_mse_raw": {"101": 1.820257167609185e-06,
                                      "202": 3.567773255645584e-06,
                                      "303": 1.734413296725938e-06},
    "closure_per_neuron_dev_rms_from_bias_source_check": [9.66e-04, 8.93e-04],
    "note": ("arm1/arm2 = analytic Gaussian-closure predictors; their raw MSE "
             "is bias(closure-error)-dominated and 3-8x ABOVE arm0 sampling. "
             "M181_G0_NOTES.md: closure per-neuron deviation rms ~9.66e-4 vs "
             "plain-MC per-neuron noise ~2.5e-4."),
}


# ------------------------------------------------------- estimators
def champion_forward(weights, first_eff, points):
    """The antipodal-paired champion (frozen n8a antipodal_forward_mean)."""
    return antipodal_forward_mean(weights, first_eff, points)


def residual_split_forward(weights, first_eff, points):
    """Residual-split estimator: build the layer-1 activation set from the
    even/odd (|z|/2 + z/2) decomposition instead of ReLU(+-z) directly, then
    run the IDENTICAL deep tail.  Algebraically |z|/2 + z/2 = ReLU(z) and
    |z|/2 - z/2 = ReLU(-z), so this reconstructs the same 2N-point antipodal
    set -- the 'integrate the odd half to zero, keep the even half' reading."""
    first = points @ first_eff                       # z = W1 (r u)
    even = np.abs(first) * F32(0.5)                   # |z| / 2   (even half)
    odd = first * F32(0.5)                            #  z  / 2   (odd half)
    act = np.concatenate((even + odd, even - odd), axis=0)   # ReLU(z), ReLU(-z)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], F32(0.0))
    return act.astype(np.float64).mean(axis=0)


# --------------------------------------------------- test 1: layer-1 identity
def test_layer1_identity(kerdock):
    """max | ReLU(W1(r u)) + ReLU(W1(r(-u))) - |W1(r u)| | over the design set,
    computing BOTH matmuls with actual +points and -points (per the task)."""
    worst = 0.0
    worst_neg = 0.0
    rows = []
    for net in NET_SEEDS:
        weights = he_mlp_weights(net)
        rot = haar_rotation(ROT_SEED(net, 0))
        first_eff = (rot.T @ weights[0]).astype(F32)
        z_plus = (kerdock @ first_eff).astype(F32)               # W1 (r u)
        z_minus = ((-kerdock) @ first_eff).astype(F32)           # W1 (r(-u))
        lhs = np.maximum(z_plus, F32(0.0)) + np.maximum(z_minus, F32(0.0))
        rhs = np.abs(z_plus)
        dev = float(np.max(np.abs(lhs.astype(np.float64) - rhs.astype(np.float64))))
        # bonus: fp exactness of the negation W1(r(-u)) == -(W1(r u))
        neg = float(np.max(np.abs(z_minus.astype(np.float64) + z_plus.astype(np.float64))))
        worst = max(worst, dev)
        worst_neg = max(worst_neg, neg)
        rows.append({"net": net, "max_abs_dev": dev, "max_abs_neg_dev": neg,
                     "n_entries": int(z_plus.size)})
        print(f"  T1 net {net}: max|ReLU(z)+ReLU(-z)-|z|| = {dev:.3e}  "
              f"(neg-exactness {neg:.3e}, {z_plus.size} entries)", flush=True)
    return {"max_abs_deviation": worst, "max_abs_neg_deviation": worst_neg,
            "per_net": rows}


# ------------------------------ test 2: full-estimator equivalence + MSE match
def test_full_equivalence(kerdock, truths):
    champ_mse, resid_mse = {}, {}
    max_final_dev = 0.0
    per_net = []
    for net in NET_SEEDS:
        weights = he_mlp_weights(net)
        c_fin = np.empty((REPLICATES, WIDTH))
        r_fin = np.empty((REPLICATES, WIDTH))
        for r in range(REPLICATES):
            rot = haar_rotation(ROT_SEED(net, r))
            first_eff = (rot.T @ weights[0]).astype(F32)
            c_fin[r] = champion_forward(weights, first_eff, kerdock)
            r_fin[r] = residual_split_forward(weights, first_eff, kerdock)
        dev = float(np.max(np.abs(c_fin - r_fin)))
        max_final_dev = max(max_final_dev, dev)
        t = truths[net]
        cm = float(((c_fin - t[None]) ** 2).mean())
        rm = float(((r_fin - t[None]) ** 2).mean())
        champ_mse[net] = cm
        resid_mse[net] = rm
        per_net.append({"net": net, "mse_champion": cm, "mse_residual": rm,
                        "mse_ratio_resid_over_champ": rm / cm,
                        "max_final_abs_dev": dev})
        print(f"  T2 net {net}: mse_champ={cm:.4e} mse_resid={rm:.4e} "
              f"ratio={rm/cm:.6f} max|final dev|={dev:.3e}", flush=True)
    panel_champ = float(np.mean([champ_mse[n] for n in NET_SEEDS]))
    panel_resid = float(np.mean([resid_mse[n] for n in NET_SEEDS]))
    ratio = panel_resid / panel_champ
    return {"panel_mse_champion": panel_champ, "panel_mse_residual": panel_resid,
            "panel_mse_ratio_resid_over_champ": ratio,
            "max_final_abs_dev_all": max_final_dev,
            "per_net": per_net,
            "champion_mse_by_net": {str(n): champ_mse[n] for n in NET_SEEDS}}


# ------------------------------ test 3a: linear-net mean == 0 (own MC)
def _linear_mc(net, n_samples, chunk, seed):
    """MC mean of the all-linear (ReLU->identity) net: y = x @ (first_eff @ W1
    @ ... @ W31), x ~ N(0,I).  Returns (per-neuron rms of the output mean,
    per-neuron rms of the MC standard error, mean |z|)."""
    weights = he_mlp_weights(net)
    rot = haar_rotation(ROT_SEED(net, 0))
    first_eff = (rot.T @ weights[0]).astype(np.float64)
    mats = [first_eff] + [w.astype(np.float64) for w in weights[1:DEPTH]]
    rng = np.random.default_rng(seed)
    acc = np.zeros(WIDTH)
    acc_sq = np.zeros(WIDTH)
    done = 0
    while done < n_samples:
        m = min(chunk, n_samples - done)
        y = rng.standard_normal((m, WIDTH))
        for M in mats:            # linear forward: identity in place of ReLU
            y = y @ M
        acc += y.sum(axis=0)
        acc_sq += (y * y).sum(axis=0)
        done += m
    mean = acc / done
    std = np.sqrt(np.maximum(acc_sq / done - mean ** 2, 0.0))
    mc_noise = std / np.sqrt(done)
    rms_mean = float(np.sqrt((mean ** 2).mean()))
    rms_noise = float(np.sqrt((mc_noise ** 2).mean()))
    z = np.abs(mean) / np.maximum(mc_noise, 1e-300)
    return rms_mean, rms_noise, float(z.mean()), done


def test_linear_mean(n_a=200_000, n_b=800_000, chunk=100_000):
    """All-ReLU->identity net has E[f]=M^T E[x]=0 EXACTLY under E[x]=0.  Confirm
    by MC on all 3 nets and, decisively, show the output-mean magnitude DECAYS
    as 1/sqrt(n) (a real signal would not) between n_a and n_b (4x n)."""
    per_net = []
    for net in NET_SEEDS:
        rms_a, noise_a, z_a, na = _linear_mc(net, n_a, chunk, 7_000_000 + net)
        rms_b, noise_b, z_b, nb = _linear_mc(net, n_b, chunk, 8_000_000 + net)
        decay = rms_a / rms_b                       # expect ~sqrt(n_b/n_a)=2.0
        per_net.append({
            "net": net,
            "n_a": na, "rms_mean_a": rms_a, "rms_mcnoise_a": noise_a,
            "ratio_mean_over_mcnoise_a": rms_a / noise_a, "mean_abs_z_a": z_a,
            "n_b": nb, "rms_mean_b": rms_b, "rms_mcnoise_b": noise_b,
            "decay_a_over_b": decay})
        print(f"  T3 linear-mean net {net}: rms(mean) {rms_a:.3e}(n={na}) -> "
              f"{rms_b:.3e}(n={nb}); decay {decay:.2f} (sqrt(4)=2.0 expected); "
              f"mean|z|_a={z_a:.3f}", flush=True)
    decay_pred = float(np.sqrt(n_b / n_a))
    mean_decay = float(np.mean([r["decay_a_over_b"] for r in per_net]))
    mean_ratio_a = float(np.mean([r["ratio_mean_over_mcnoise_a"] for r in per_net]))
    return {"per_net": per_net,
            "predicted_decay_sqrt_nb_over_na": decay_pred,
            "mean_decay_a_over_b": mean_decay,
            "mean_ratio_mean_over_mcnoise_a": mean_ratio_a,
            "analytic_expectation": 0.0,
            "note": ("E[x]=0 -> E[linear f]=M^T E[x]=0 exactly (M=product of the "
                     "linear layers).  The MC output-mean IS xbar@M (xbar=input "
                     "sample mean); it carries no signal, only 1/sqrt(n) noise, "
                     "and decays ~2x when n grows 4x -- confirming all of E[f] "
                     "lives in the ReLU corrections (the non-Gaussian part).")}


# ------------------------------ Form-1 reparametrization: per-layer R_l
def form1_profile(kerdock):
    """R_l = mean_u ||F_l||_2 / mean_u ||y_l||_2, F_l = ReLU(W_{l+1} y_l) - y_l,
    for the 31 hidden layers (weights[1..31]) on the antipodal design set.
    y_0 = first-hidden activation.  Averaged over the 3 nets (1 rotation seed)."""
    per_net = {}
    for net in NET_SEEDS:
        weights = he_mlp_weights(net)
        rot = haar_rotation(ROT_SEED(net, 0))
        first_eff = (rot.T @ weights[0]).astype(F32)
        first = kerdock @ first_eff
        act = np.concatenate((np.maximum(first, F32(0.0)),
                              np.maximum(-first, F32(0.0))), axis=0)  # y_0
        rs = []
        for layer in range(1, DEPTH):                 # weights[1..31] -> 31 layers
            y_prev = act
            y_new = np.maximum(y_prev @ weights[layer], F32(0.0))
            F = y_new.astype(np.float64) - y_prev.astype(np.float64)
            num = float(np.linalg.norm(F, axis=1).mean())               # mean_u||F_l||
            den = float(np.linalg.norm(y_prev.astype(np.float64), axis=1).mean())  # mean_u||y_l||
            rs.append(num / den)
            act = y_new
        per_net[net] = rs
    R = np.array([per_net[n] for n in NET_SEEDS])     # (3, 31)
    R_mean = R.mean(axis=0)
    profile = {f"R_{l+1}": float(R_mean[l]) for l in range(R_mean.size)}
    any_near_identity = bool((R_mean < 0.3).any())
    print(f"  FORM-1 R_l: min={R_mean.min():.3f} median={float(np.median(R_mean)):.3f} "
          f"max={R_mean.max():.3f}  any R_l<0.3: {any_near_identity}", flush=True)
    return {"n_layers": int(R_mean.size),
            "R_profile_mean_over_nets": profile,
            "R_per_net": {str(n): per_net[n] for n in NET_SEEDS},
            "min": float(R_mean.min()), "median": float(np.median(R_mean)),
            "max": float(R_mean.max()),
            "any_layer_below_0p3": any_near_identity,
            "layers_below_0p3": [l + 1 for l in range(R_mean.size) if R_mean[l] < 0.3]}


# --------------------------------------------------------------------- main
def main():
    t0 = time.perf_counter()
    print("== S16 residual/norm decomposition (CONFIRMATORY) ==", flush=True)

    kerdock = load_kerdock_directions()
    truths = {}
    truth_noise = {}
    for n in NET_SEEDS:
        d = np.load(M181 / f"m181_truth_net{n}.npz")
        truths[n] = np.asarray(d["means"], dtype=np.float64)
        truth_noise[n] = float(d["noise_final"])
        d.close()
    print(f"cached m181 3.5M truth loaded for nets {NET_SEEDS} "
          f"(noise floors {[f'{truth_noise[n]:.2e}' for n in NET_SEEDS]})", flush=True)

    print("\n[Test 1] layer-1 antipodal == even-part identity", flush=True)
    t1 = test_layer1_identity(kerdock)

    print("\n[Test 2] full residual-split vs antipodal champion (16 seeds x 3 nets)",
          flush=True)
    t2 = test_full_equivalence(kerdock, truths)

    print("\n[Test 3a] linear-net mean == 0 (own MC)", flush=True)
    t3 = test_linear_mean()

    print("\n[Form-1] per-layer residual magnitude ratio R_l (l=1..31)", flush=True)
    f1 = form1_profile(kerdock)

    # ---- cross-check: champion panel MSE vs m181 arm0 committed baseline ----
    champ_by_net = t2["champion_mse_by_net"]
    m181_arm0 = M181_CITED["arm0_baseline_mse_raw"]
    xcheck = {str(n): {"champion_mse": champ_by_net[str(n)],
                       "m181_arm0_mse_raw": m181_arm0[str(n)],
                       "ratio": champ_by_net[str(n)] / m181_arm0[str(n)]}
              for n in NET_SEEDS}
    xratio = float(np.mean([xcheck[str(n)]["ratio"] for n in NET_SEEDS]))
    print(f"\n[cross-check] champion panel MSE vs m181 arm0 baseline: "
          f"mean ratio {xratio:.3f} (both = antipodal Kerdock forward mean)",
          flush=True)

    # ---------------------------------------------------------------- gates
    g1 = t1["max_abs_deviation"] < 1e-10
    g2 = abs(t2["panel_mse_ratio_resid_over_champ"] - 1.0) < 0.01
    # linear part carries no signal: mean sits at its MC-noise floor AND decays
    # ~1/sqrt(n) (a real nonzero mean would not shrink when n grows 4x).
    linear_ok = (t3["mean_ratio_mean_over_mcnoise_a"] < 3.0
                 and 1.4 <= t3["mean_decay_a_over_b"] <= 2.8)
    # closure wall: cited arm1 closure MSE (mean over nets) vs arm0 sampling
    closure_mse = float(np.mean(list(M181_CITED["arm1_univariate_closure_mse_raw"].values())))
    sampling_mse = float(np.mean(list(m181_arm0.values())))
    closure_above_sampling = closure_mse > sampling_mse
    g3 = linear_ok and closure_above_sampling
    # surprise conditions
    surprise_beat = t2["panel_mse_ratio_resid_over_champ"] < 0.90   # resid beats by >10%
    surprise_near_identity = f1["any_layer_below_0p3"]

    confirmed = g1 and g2 and g3
    surprise = surprise_beat or surprise_near_identity
    if surprise:
        verdict = "SURPRISE"
    elif confirmed:
        verdict = "CONFIRMED"
    else:
        verdict = "INCONCLUSIVE"

    wall = time.perf_counter() - t0
    results = {
        "ledger_id": "s16_residual_norm_decomposition_confirm",
        "kind": "CONFIRMATORY",
        "date": "2026-08-09",
        "verdict": verdict,
        "wall_s": round(wall, 1),
        "firewall": ("synthetic He nets 101/202/303 via n8a constructor; frozen "
                     "n8a + m181 sources read-only; cached m181 3.5M truth "
                     "read-only; own MC for the linear-mean check; single "
                     "process; writes confined to s16_residual_decomp/"),
        "config": {"net_seeds": list(NET_SEEDS), "replicates": REPLICATES,
                   "n_base_design": N_BASE, "n_antipodal": 2 * N_BASE,
                   "width": WIDTH, "depth": DEPTH,
                   "rotation_seed_formula": "900000 + net*1000 + r",
                   "truth_source": "cached m181 3.5M-sample MC means"},
        "gates": {
            "g1_layer1_identity_lt_1e-10": {"value": t1["max_abs_deviation"],
                                            "pass": bool(g1)},
            "g2_mse_match_within_1pct": {"ratio_resid_over_champ":
                                         t2["panel_mse_ratio_resid_over_champ"],
                                         "pass": bool(g2)},
            "g3_linear_mean0_and_closure_wall": {
                "linear_mean_at_mc_floor": bool(linear_ok),
                "closure_mse_above_sampling": bool(closure_above_sampling),
                "closure_arm1_mse_mean": closure_mse,
                "sampling_arm0_mse_mean": sampling_mse,
                "pass": bool(g3)},
            "surprise_resid_beats_champ_gt10pct": bool(surprise_beat),
            "surprise_any_layer_near_identity_Rl_lt_0p3": bool(surprise_near_identity),
        },
        "test1_layer1_identity": t1,
        "test2_full_equivalence": t2,
        "test3_linear_mean": t3,
        "test3_closure_wall_cited": M181_CITED,
        "form1_reparametrization": f1,
        "crosscheck_champion_vs_m181_arm0": {"per_net": xcheck, "mean_ratio": xratio},
        "clean_statement": (
            "residual decomposition = antipodal symmetrization"
            if confirmed else
            "residual decomposition did NOT reduce to antipodal symmetrization"),
    }
    out = HERE / "s16_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"\nVERDICT: {verdict}  (wall {wall:.1f}s)")
    print(f"  G1 layer-1 identity dev = {t1['max_abs_deviation']:.3e}  (<1e-10: {g1})")
    print(f"  G2 MSE ratio resid/champ = {t2['panel_mse_ratio_resid_over_champ']:.6f}  "
          f"(within 1%: {g2})")
    print(f"  G3 linear-mean floor + closure wall: {g3}")
    print(f"  Form-1 R_l: min {f1['min']:.3f} / median {f1['median']:.3f} / "
          f"max {f1['max']:.3f}  any<0.3: {f1['any_layer_below_0p3']}")
    print(f"results -> {out}")
    return results


if __name__ == "__main__":
    main()
