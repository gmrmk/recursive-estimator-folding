"""gm_s17_reuse -- S17 section-A instrument reuse on the committed 80-net m185 panel.

Predeclared in PREDECLARATION.md (this directory). Response-free: no estimator
change, no submission, no held-lane contact, no network.

Per net seed s in the m185 stage-1 panel:
  sigma2_s = Var_u(ybar)  over the 64512-direction antipodally-doubled Kerdock
             v3 design rotated by haar_rotation(900000 + s*1000 + 0),
             ybar = neuron-mean of the layer-31 post-ReLU activation (float64)
  floor_s  = sigma2_s / 64512                       (S17's gated denominator)
  ratio_s  = champ_s / floor_s
with champ_s taken two ways (see PREDECLARATION deviation 1):
  PRIMARY        champ_corr = mse_corr                       (floor-corrected)
  S17-CONVENTION champ_s17  = mse_corr + floor31*600000/3.5e6

Checkpoint/resume: run repeatedly until 'REMAINING: 0'.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
sys.dont_write_bytecode = True
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
N8A_PATH = os.path.join(EXP, "n8a_rqmc_kerdock", "run_n8a_gates.py")
M185_CKPT = os.path.join(EXP, "a_series_granular_adversarial",
                         "m185_g0_stage1_checkpoint.json")
CKPT = os.path.join(HERE, "gm_s17_reuse_checkpoint.json")

_spec = importlib.util.spec_from_file_location("run_n8a_gates", N8A_PATH)
n8a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(n8a)   # main() is __main__-guarded

WIDTH, DEPTH = n8a.WIDTH, n8a.DEPTH
N_BASE = n8a.N_BASE
N_FULL = 2 * N_BASE
N_TRUTH_S1 = 600_000            # m185 stage-1 truth samples
N_TRUTH_S16 = 3_500_000         # cached m181/S16 truth samples S17's numerators used


def rot_seed(net_seed: int) -> int:
    return 900_000 + net_seed * 1_000 + 0


def forward_stats(weights, first_eff, kerdock):
    """Layer-31 post-ReLU field statistics over the doubled design.

    Returns (sigma2_ybar, mean_ybar, meanvar_perneuron, sum-check dict).
    """
    pre1 = kerdock @ first_eff                        # (32256, 256) f32
    act = np.concatenate([np.maximum(pre1, np.float32(0.0)),
                          np.maximum(-pre1, np.float32(0.0))], axis=0)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    a64 = act.astype(np.float64)
    ybar = a64.mean(axis=1)
    mu = ybar.mean()
    sig2 = ybar.var()                                  # signal 1 (ddof=0)
    sig2_b = np.mean((ybar - mu) ** 2)                 # S4: two-way check
    colmean = a64.mean(axis=0)
    colvar = (a64 * a64).mean(axis=0) - colmean * colmean
    return {"mu": float(mu), "sigma2": float(sig2), "sigma2_twoway": float(sig2_b),
            "meanvar_perneuron": float(colvar.mean()),
            "max_act": float(a64.max())}


def forward_sigma2_altpath(weights, first_eff, kerdock, chunk=4096):
    """S3 independent code path: chunked over directions, Welford-free two-pass
    with a different summation order and layout (base and antipode blocks
    processed separately, in chunks)."""
    tot_n = 0
    s1 = 0.0
    vals = []
    for sign in (+1.0, -1.0):
        for lo in range(0, N_BASE, chunk):
            hi = min(lo + chunk, N_BASE)
            p = kerdock[lo:hi] @ first_eff
            a = np.maximum(np.float32(sign) * p, np.float32(0.0))
            for layer in range(1, DEPTH):
                a = np.maximum(a @ weights[layer], np.float32(0.0))
            yb = a.astype(np.float64).mean(axis=1)
            vals.append(yb)
            s1 += yb.sum()
            tot_n += yb.size
    y = np.concatenate(vals)
    mean = s1 / tot_n
    return float(((y - mean) ** 2).sum() / tot_n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1000:1020")
    ap.add_argument("--budget-seconds", type=float, default=3000.0)
    ap.add_argument("--altpath-seeds", default="1000,1001,1002")
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.seeds.split(":"))
    want = list(range(lo, hi))
    alt = {int(x) for x in args.altpath_seeds.split(",") if x}

    m185 = json.load(open(M185_CKPT))["nets"]

    ck = {"nets": {}, "meta": {}}
    if os.path.exists(CKPT):
        ck = json.load(open(CKPT))
    ck["meta"].update({"N_FULL": N_FULL, "N_BASE": N_BASE,
                       "rot_seed_formula": "900000 + net_seed*1000 + 0"})

    kerdock = n8a.load_kerdock_directions()
    t_start = time.perf_counter()
    pending = [s for s in want if str(s) not in ck["nets"]]
    print("PENDING: %d" % len(pending), flush=True)

    for s in pending:
        if time.perf_counter() - t_start > args.budget_seconds:
            break
        t0 = time.perf_counter()
        rec_m = m185[str(s)]
        # S1: independent recomputation of the numerator from stored vectors
        pred = np.asarray(rec_m["pred31"], dtype=np.float64)
        truth = np.asarray(rec_m["truth31"], dtype=np.float64)
        mse_raw_recomp = float(((pred - truth) ** 2).mean())
        mse_raw_stored = float(rec_m["mse_raw"])
        s1_rel = abs(mse_raw_recomp - mse_raw_stored) / mse_raw_stored

        weights = n8a.he_mlp_weights(s)
        rot = n8a.haar_rotation(rot_seed(s))
        first_eff = (rot.T @ weights[0]).astype(np.float32)
        st = forward_stats(weights, first_eff, kerdock)

        sig2 = st["sigma2"]
        floor_full = sig2 / N_FULL
        floor_base = sig2 / N_BASE
        floor_perout = st["meanvar_perneuron"] / N_FULL
        floor31 = float(rec_m["floor31"])
        champ_corr = float(rec_m["mse_corr"])
        champ_s17 = champ_corr + floor31 * N_TRUTH_S1 / N_TRUTH_S16

        rec = {
            "net_seed": s, "rot_seed": rot_seed(s),
            "m185_rot_seed": rec_m["rot_seed"],
            "mse_raw_stored": mse_raw_stored,
            "mse_raw_recomputed": mse_raw_recomp,
            "S1_numerator_rel_err": s1_rel,
            "floor31": floor31,
            "champ_corr": champ_corr,
            "champ_s17conv": champ_s17,
            "mu_ybar": st["mu"],
            "sigma2": sig2,
            "sigma2_twoway": st["sigma2_twoway"],
            "S4_twoway_rel_diff": abs(sig2 - st["sigma2_twoway"]) / sig2,
            "meanvar_perneuron_design": st["meanvar_perneuron"],
            "iid_floor_sigma2_over_64512": floor_full,
            "dir_floor_sigma2_over_32256": floor_base,
            "perout_floor_meanvar_over_64512": floor_perout,
            "ratio_primary_corr_over_costfloor": champ_corr / floor_full,
            "ratio_s17conv_over_costfloor": champ_s17 / floor_full,
            "ratio_primary_over_dirfloor": champ_corr / floor_base,
            "ratio_primary_over_peroutfloor": champ_corr / floor_perout,
            "N_eff_sigma2_over_champ_corr": sig2 / champ_corr,
            "wall_s": None,
        }
        if s in alt:
            sig2_alt = forward_sigma2_altpath(weights, first_eff, kerdock)
            rec["S3_sigma2_altpath"] = sig2_alt
            rec["S3_altpath_rel_err"] = abs(sig2_alt - sig2) / sig2
        rec["wall_s"] = round(time.perf_counter() - t0, 2)
        ck["nets"][str(s)] = rec
        with open(CKPT, "w") as fh:
            json.dump(ck, fh, indent=1)
        print("net %d sigma2=%.6e champ_corr=%.4e ratio=%.4f s17conv=%.4f "
              "perout=%.4f S1rel=%.1e %s (%.1fs)"
              % (s, sig2, champ_corr, rec["ratio_primary_corr_over_costfloor"],
                 rec["ratio_s17conv_over_costfloor"],
                 rec["ratio_primary_over_peroutfloor"], s1_rel,
                 ("alt_rel=%.1e" % rec["S3_altpath_rel_err"]) if s in alt else "",
                 rec["wall_s"]), flush=True)

    remaining = len([s for s in want if str(s) not in ck["nets"]])
    print("REMAINING: %d" % remaining, flush=True)


if __name__ == "__main__":
    main()
