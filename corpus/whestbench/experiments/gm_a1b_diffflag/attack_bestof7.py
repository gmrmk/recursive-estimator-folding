"""Self-attack on the gm_a1b_diffflag verdict.

Strongest counter-hypothesis to "a1b's 0.50 sits at the perfect-oracle ceiling":
a1b picked the BEST of 7 diagnostics by |rho|. A best-of-7 selection over
ZERO-SIGNAL diagnostics might reach precision 0.50 on its own, in which case
a1b's 0.50 is selection noise and says nothing about the ceiling.

Null arm : 7 diagnostics independent of MSE (conservative: independence maximises
           the multiplicity bonus vs a1b's mutually correlated diagnostics).
Also reported: P(perfect oracle |rho| >= a1b's measured 0.5627) at each vD, and
the base rate a "coin flip" would actually give (0.25, not 0.50).
"""
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
            r"\publish\recursive-estimator-folding")
EXP = ROOT / "corpus" / "whestbench" / "experiments"
OUT = EXP / "gm_a1b_diffflag" / "attack_bestof7.json"
RES = EXP / "gm_a1b_diffflag" / "results.json"

r = json.load(open(RES, encoding="utf-8"))
POOLSRC = json.load(open(EXP / "pb1_premise_battery" / "p2_results.json"))
pn = POOLSRC["q1_oracle_headroom"]["per_net"]
POOL = np.concatenate([np.asarray(pn[k]["mse_per_rotation"], float)
                       / np.mean(pn[k]["mse_per_rotation"]) for k in sorted(pn)])
POOL = POOL / POOL.mean()

N = 80
CUT = 60
K = 7
REPS = 200_000
BLOCK = 5_000
t0 = time.time()


def ranks_rows(a):
    order = np.argsort(a, axis=-1, kind="stable")
    out = np.empty_like(order)
    np.put_along_axis(out, order, np.arange(a.shape[-1]), axis=-1)
    return out


def spear_rows(ra, rb):
    ra = ra.astype(np.float64) - (N - 1) / 2.0
    rb = rb.astype(np.float64) - (N - 1) / 2.0
    return (ra * rb).sum(-1) / np.sqrt((ra ** 2).sum(-1) * (rb ** 2).sum(-1))


# ---- null arm: 7 zero-signal diagnostics, best-of-7 by |rho|, then its precision
rng = np.random.default_rng(20260810 + 991)
precs, rhos = [], []
done = 0
while done < REPS:
    b = min(BLOCK, REPS - done)
    M = rng.random((b, N))                       # target ranks only -> any law works
    X = rng.random((b, K, N))                    # 7 independent zero-signal flags
    rM = ranks_rows(M)
    rX = ranks_rows(X)
    sp = spear_rows(rX, rM[:, None, :])          # (b, K)
    j = np.argmax(np.abs(sp), axis=1)
    best_rho = sp[np.arange(b), j]
    rbest = rX[np.arange(b), j, :]
    fl = np.where(best_rho[:, None] > 0, rbest >= CUT, rbest < N - CUT)
    tl = rM >= CUT
    tp = (fl & tl).sum(1).astype(float)
    precs.append(tp / fl.sum(1))
    rhos.append(np.abs(best_rho))
    done += b
pn_ = np.concatenate(precs)
rn_ = np.concatenate(rhos)

out = {
    "null_best_of_7_zero_signal": {
        "reps": int(pn_.size),
        "precision_mean": float(pn_.mean()),
        "precision_se": float(pn_.std(ddof=1) / np.sqrt(pn_.size)),
        "precision_p5": float(np.percentile(pn_, 5)),
        "precision_p50": float(np.percentile(pn_, 50)),
        "precision_p95": float(np.percentile(pn_, 95)),
        "p_precision_ge_0p50": float((pn_ >= 0.50 - 1e-12).mean()),
        "abs_rho_mean": float(rn_.mean()),
        "abs_rho_p95": float(np.percentile(rn_, 95)),
        "p_abs_rho_ge_0p5627": float((rn_ >= 0.5627285513361463).mean()),
    },
    "single_flag_zero_signal_precision_expectation": 0.25,
    "a1b_measured": {"best_abs_rho": 0.5627285513361463, "precision": 0.5, "recall": 0.5},
}

# ---- P(perfect oracle |rho| >= a1b's 0.5627) at each vD, from the committed run
for name, arm in r["arms"].items():
    out.setdefault("oracle_vs_a1b_rho", {})[name] = {
        "vD": arm["vD"],
        "oracle_rho_mean": arm["oracle_spearman"]["mean"],
        "oracle_rho_p95": arm["oracle_spearman"]["p95"],
        "a1b_0p5627_below_oracle_p95": bool(0.5627285513361463
                                            <= arm["oracle_spearman"]["p95"]),
    }
out["measured_chance_precision_from_results_json"] = {
    k: v["null_oracle_precision_mean"] for k, v in r["arms"].items()}
out["attack_verdict"] = (
    "LANDS PARTIALLY" if out["null_best_of_7_zero_signal"]["precision_mean"] >= 0.40
    else "DOES NOT LAND")
out["wall_s"] = time.time() - t0
OUT.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
