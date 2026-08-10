"""gm_s17_reuse addendum.

(A) NET-IDENTITY second signal: my reconstructed He net must be the SAME net
    m185 measured. Independent 60k-sample iid-Gaussian MC of the layer-31 mean
    vector, compared against the committed truth31 (600k samples). If the
    weights differed at all, mean_j (mine - truth31)^2 would be O(Var)~1e-1;
    if identical it must sit at the sum of the two MC floors ~2e-6.

(B) Downstream propagation of the n=80 pooled ratio into S17's own gate class
    rule and into the ednacob bracket (deterministic, no new data).
"""
from __future__ import annotations
import importlib.util, json, os, sys
sys.dont_write_bytecode = True
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
N8A_PATH = os.path.join(EXP, "n8a_rqmc_kerdock", "run_n8a_gates.py")
M185_CKPT = os.path.join(EXP, "a_series_granular_adversarial",
                         "m185_g0_stage1_checkpoint.json")
_spec = importlib.util.spec_from_file_location("run_n8a_gates", N8A_PATH)
n8a = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(n8a)
WIDTH, DEPTH = n8a.WIDTH, n8a.DEPTH

res = json.load(open(os.path.join(HERE, "results.json")))
m185 = json.load(open(M185_CKPT))["nets"]

# ------------------------------------------------------------------ (A)
N_MC = 60_000
CHUNK = 20_000
ident = {}
for s in (1000, 1040, 1079):
    w = n8a.he_mlp_weights(s)
    rng = np.random.default_rng(7_000_000 + s)      # seed unrelated to m185's
    sums = np.zeros(WIDTH)
    done = 0
    while done < N_MC:
        m = min(CHUNK, N_MC - done)
        act = rng.standard_normal((m, WIDTH)).astype(np.float32)
        for layer in range(DEPTH):
            act = np.maximum(act @ w[layer], np.float32(0.0))
        sums += act.sum(axis=0, dtype=np.float64)
        done += m
    mine = sums / N_MC
    truth = np.asarray(m185[str(s)]["truth31"], dtype=np.float64)
    d2 = float(((mine - truth) ** 2).mean())
    scale = float((truth * truth).mean())
    floor31 = float(m185[str(s)]["floor31"])
    expected = floor31 + floor31 * 600_000 / N_MC   # both MC floors, same var
    ident[str(s)] = {"mean_sq_diff": d2, "expected_sum_of_mc_floors": expected,
                     "ratio_obs_over_expected": d2 / expected,
                     "mean_sq_truth_scale": scale,
                     "relative_to_field_scale": d2 / scale,
                     "n_mc": N_MC}
    print("net %d  mean_sq_diff=%.4e  expected(2 MC floors)=%.4e  ratio=%.3f  "
          "(field scale %.4e -> %.2e of it)"
          % (s, d2, expected, d2 / expected, scale, d2 / scale), flush=True)

# ------------------------------------------------------------------ (B)
p = res["pooled"]["primary_mse_corr_over_costfloor"]
q = res["pooled"]["s17conv_over_costfloor"]
VPF = 3.9657744377832187          # S17 C_ednacob: I_champ / I_ednacob
S17_POOLED = 1.7906808367797993


def bracket(pooled):
    return VPF / pooled


def s17_class(pooled):
    return "i" if pooled < 2.0 else ("ii" if pooled < 4.0 else "iii")


prop = {
    "s17_own_class_rule": "pooled<2.0 -> class i; 2.0-4.0 -> class ii; >4 -> iii",
    "s17_n3_pooled": S17_POOLED, "s17_n3_class": s17_class(S17_POOLED),
    "n80_primary_pooled": p["mean"], "n80_primary_class": s17_class(p["mean"]),
    "n80_primary_ci": p["ci95"],
    "n80_primary_ci_classes": [s17_class(p["ci95"][0]), s17_class(p["ci95"][1])],
    "n80_s17conv_pooled": q["mean"], "n80_s17conv_class": s17_class(q["mean"]),
    "n80_s17conv_ci": q["ci95"],
    "n80_s17conv_ci_classes": [s17_class(q["ci95"][0]), s17_class(q["ci95"][1])],
    "class_boundary_2x_resolved_at_n80": bool(
        (p["ci95"][1] < 2.0) or (p["ci95"][0] > 2.0)),
    "ednacob_below_pointfloor_generous_x": {
        "s17_n3": bracket(S17_POOLED),
        "n80_primary": bracket(p["mean"]),
        "n80_primary_from_ci": [bracket(p["ci95"][1]), bracket(p["ci95"][0])],
        "n80_s17conv": bracket(q["mean"]),
        "n80_s17conv_from_ci": [bracket(q["ci95"][1]), bracket(q["ci95"][0])],
    },
    "ednacob_below_pointfloor_tight_x": VPF,
    "s17_headline_ge_2.2x_still_holds": bool(bracket(p["ci95"][1]) >= 2.2),
    "dirfloor_accounting": {
        "s17_n3_pooled_0.90": 0.8953404183898996,
        "n80_primary_pooled": res["pooled"]["primary_over_dirfloor"]["mean"],
        "n80_primary_ci": res["pooled"]["primary_over_dirfloor"]["ci95"],
        "includes_1.0": bool(res["pooled"]["primary_over_dirfloor"]["ci95"][0] <= 1.0
                             <= res["pooled"]["primary_over_dirfloor"]["ci95"][1]),
    },
}

res["A_net_identity_check"] = ident
res["B_propagation"] = prop
with open(os.path.join(HERE, "results.json"), "w") as fh:
    json.dump(res, fh, indent=2)

print()
print("S17 class rule: n=3 pooled %.4f -> class %s | n=80 primary %.4f -> class %s "
      "(CI classes %s) | n=80 s17conv %.4f -> class %s (CI classes %s)"
      % (S17_POOLED, prop["s17_n3_class"], p["mean"], prop["n80_primary_class"],
         prop["n80_primary_ci_classes"], q["mean"], prop["n80_s17conv_class"],
         prop["n80_s17conv_ci_classes"]))
print("ednacob generous bracket: S17 %.4fx -> n80 primary %.4fx (CI %.4f-%.4f), "
      "s17conv %.4fx; tight stays %.4fx; S17's '>=2.2x in every accounting' holds: %s"
      % (bracket(S17_POOLED), bracket(p["mean"]),
         *prop["ednacob_below_pointfloor_generous_x"]["n80_primary_from_ci"],
         bracket(q["mean"]), VPF, prop["s17_headline_ge_2.2x_still_holds"]))
d = prop["dirfloor_accounting"]
print("dir-floor accounting: S17 0.8953 -> n=80 %.4f CI [%.4f, %.4f] includes 1.0: %s"
      % (d["n80_primary_pooled"], *d["n80_primary_ci"], d["includes_1.0"]))
