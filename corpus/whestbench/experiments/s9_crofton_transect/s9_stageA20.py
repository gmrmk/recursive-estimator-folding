"""
Stage-A '20+ random nets' leg (task spec), independent implementation.
20 synthetic bias-free ReLU MLPs (width 16, depth 4, He init), scalar output.
Three ways per net: high-precision MC, Euler-MC (machine-exact per sample), and
my slope-jump transect (surface form) with per-layer decomposition.
Writes s9_stageA20.json.  Synthetic self-generated nets only.
"""
import json, time
import numpy as np
from math import sqrt
from s9_core import make_net, forward_grad, forward_only, transect_line, sample_line

d, width, depth = 16, 16, 4
hidden = depth - 1
N_NETS = 20
MC = 1_500_000
GRAD_N = 300_000
LINES = 3000

rng = np.random.default_rng(424242)
recs = []
euler_max = 0.0
zs = []
fracs = []
t0 = time.time()
for i in range(N_NETS):
    Ws = make_net(d, width, depth, rng)
    # MC ground truth
    X = rng.standard_normal((MC, d)); f = forward_only(Ws, X)
    mc = float(f.mean()); mc_se = float(f.std() / sqrt(MC))
    # Euler-MC (machine exact per sample)
    Xg = rng.standard_normal((GRAD_N, d)); fg, g = forward_grad(Ws, Xg)
    euler_ps = (Xg * g).sum(1)
    emax = float(np.max(np.abs(euler_ps - fg))); euler_max = max(euler_max, emax)
    euler_mc = float(euler_ps.mean())
    # surface/transect form
    vals = np.empty(LINES); pl = np.zeros((LINES, hidden))
    for k in range(LINES):
        base, v = sample_line(d, rng)
        tot, p, _ = transect_line(Ws, base, v)
        vals[k] = d * tot; pl[k] = d * p
    tm = float(vals.mean()); tse = float(vals.std() / sqrt(LINES))
    z = (tm - mc) / sqrt(tse ** 2 + mc_se ** 2); zs.append(z)
    lf = (pl.mean(0) / tm)
    fracs.append(lf)
    recs.append(dict(net=i, mc=mc, mc_se=mc_se, euler_mc=euler_mc,
                     euler_max_persample=emax, transect=tm, transect_se=tse,
                     z_vs_mc=float(z), layer_fractions=[float(x) for x in lf]))
    print("net %2d MC=%+.5f Euler=%+.5f transect=%+.5f z=%+.2f Lfrac=[%s]" % (
        i, mc, euler_mc, tm, z, ",".join("%.2f" % x for x in lf)), flush=True)

zs = np.array(zs)
# layer fractions: use nets whose |E[f]| is not tiny (fraction well-defined)
mask = np.array([abs(r["mc"]) > 0.05 for r in recs])
fr = np.array(fracs)[mask]
out = dict(role="stageA_20net_leg_independent", n_nets=N_NETS,
           euler_max_persample_err=euler_max,
           z_pooled_mean=float(zs.mean()), z_pooled_sd=float(zs.std()),
           z_pooled_max_abs=float(np.max(np.abs(zs))),
           n_within_3sigma=int(np.sum(np.abs(zs) < 3)),
           layer_fractions_mean=[float(x) for x in fr.mean(0)],
           layer_fractions_sd=[float(x) for x in fr.std(0)],
           n_nets_for_fractions=int(mask.sum()),
           runtime_sec=time.time() - t0, nets=recs)
with open("s9_stageA20.json", "w") as fh:
    json.dump(out, fh, indent=2)
print("\nEuler max |x.gradf-f| over 20 nets = %.2e" % euler_max)
print("pooled z: mean=%.2f sd=%.2f max|z|=%.2f  (%d/20 within 3sigma)" % (
    zs.mean(), zs.std(), np.max(np.abs(zs)), np.sum(np.abs(zs) < 3)))
print("layer fractions (mean over %d non-degenerate nets) = [%s]" % (
    mask.sum(), ", ".join("%.3f" % x for x in fr.mean(0))))
print("WROTE s9_stageA20.json (%.0fs)" % out["runtime_sec"])
