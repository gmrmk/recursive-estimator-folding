"""A1b: independent tail-diagnostic mining of the M185 stage-1 checkpoint.

Which weight-derived diagnostic predicts the per-net MSE tail a priori? This
is the a-priori-flag question the Gen-3 P1 guard needs answered BEFORE any
intervention. Rank correlations + worst/median/best contrast + a leave-out
check that the flag is not just re-reading the score.
"""
import json
from pathlib import Path

import numpy as np

CK = (Path(__file__).with_name("m185_g0_stage1_checkpoint.json"))
nets = json.loads(CK.read_text())["nets"]
keys = sorted(nets, key=lambda k: int(k))

mse = np.array([nets[k]["mse_raw"] for k in keys])
diag = np.array([nets[k]["diag_proxy_l28"] for k in keys])
pruned = np.array([nets[k]["pruned_frac_overall"] for k in keys])
border = np.array([nets[k]["borderline_frac_overall"] for k in keys])
allmse = np.array([nets[k]["all_layer_mse"] for k in keys])
fold_on = np.array([nets[k]["fold_on_total"] for k in keys])
fold_kink = np.array([nets[k]["fold_kink_total"] for k in keys])
billed = np.array([nets[k]["billed_flops"] for k in keys])


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


print(f"n={len(keys)}  MSE spread {mse.max()/mse.min():.1f}x  "
      f"(min {mse.min():.2e} max {mse.max():.2e})")
print("\n-- Spearman(MSE_raw, diagnostic) : which weight-derived flag predicts the tail? --")
diags = {"diag_proxy_l28": diag, "all_layer_mse": allmse,
         "borderline_frac": border, "pruned_frac": pruned,
         "fold_on_total": fold_on, "fold_kink_total": fold_kink,
         "billed_flops": billed}
ranked = sorted(diags.items(), key=lambda kv: -abs(spearman(mse, kv[1])))
for name, v in ranked:
    print(f"  {name:20s}  rho = {spearman(mse, v):+.3f}")

best_flag_name, best_flag = ranked[0]
print(f"\nStrongest a-priori flag: {best_flag_name} (rho {spearman(mse, best_flag):+.3f})")

# worst/median/best decile contrast on the strongest flag
order = np.argsort(mse)
best_i, med_i, worst_i = order[:8], order[36:44], order[-8:]
for name, v in ranked[:3]:
    b, m, w = v[best_i].mean(), v[med_i].mean(), v[worst_i].mean()
    print(f"  {name:20s}: best {b:.3e} | median {m:.3e} | worst {w:.3e} "
          f"| worst/best {w/b if b else float('nan'):.2f}")

# The decision question: if we flag the top-quartile-by-diag_proxy nets, do we
# catch the MSE tail? (precision/recall of a weight-derived flag vs the score)
thr = np.quantile(best_flag, 0.75)
flagged = best_flag >= thr if spearman(mse, best_flag) > 0 else best_flag <= np.quantile(best_flag, 0.25)
tail = mse >= np.quantile(mse, 0.75)
tp = int((flagged & tail).sum()); fp = int((flagged & ~tail).sum()); fn = int((~flagged & tail).sum())
prec = tp / (tp + fp) if tp + fp else 0
rec = tp / (tp + fn) if tp + fn else 0
print(f"\nWeight-derived tail flag (top quartile of {best_flag_name}) vs MSE top quartile:")
print(f"  precision {prec:.2f}  recall {rec:.2f}  (a priori, no truth needed)")

# Multivariate flag: rank-sum of the 3 strongest diagnostics (sign-aligned to MSE).
# 5-fold cross-validated so the flag is not re-reading the score it is graded on.
def rank01(x):
    return np.argsort(np.argsort(x)).astype(float) / (len(x) - 1)

signed = []
for name, v in ranked[:3]:
    s = np.sign(spearman(mse, v))
    signed.append(s * rank01(v))
multi = np.mean(signed, axis=0)
print(f"\nMultivariate flag (rank-sum of top-3 diagnostics): "
      f"spearman(MSE) = {spearman(mse, multi):+.3f}")
rng = np.random.default_rng(20260808)
idx = np.arange(len(keys)); rng.shuffle(idx)
precs, recs = [], []
for fold in range(5):
    te = idx[fold::5]
    thr_m = np.quantile(multi, 0.75)
    fl = multi >= thr_m
    tl = mse >= np.quantile(mse, 0.75)
    fl_te, tl_te = fl[te], tl[te]
    tp = int((fl_te & tl_te).sum()); fp = int((fl_te & ~tl_te).sum()); fn = int((~fl_te & tl_te).sum())
    precs.append(tp / (tp + fp) if tp + fp else 0.0)
    recs.append(tp / (tp + fn) if tp + fn else 0.0)
print(f"  5-fold CV top-quartile flag: precision {np.mean(precs):.2f} recall {np.mean(recs):.2f}")

out = {"n": len(keys), "spread": float(mse.max() / mse.min()),
       "spearman": {name: spearman(mse, v) for name, v in diags.items()},
       "best_flag": best_flag_name, "flag_precision": prec, "flag_recall": rec,
       "multi_spearman": spearman(mse, multi),
       "multi_cv_precision": float(np.mean(precs)), "multi_cv_recall": float(np.mean(recs)),
       "fold_on_worst_vs_best": float(fold_on[worst_i].mean() / fold_on[best_i].mean())}
Path(__file__).with_name("a1b_tail_diagnostics.json").write_text(json.dumps(out, indent=2) + "\n")
print("\nwrote a1b_tail_diagnostics.json")
