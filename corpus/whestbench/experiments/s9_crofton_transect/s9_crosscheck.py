"""
S9 INDEPENDENT CROSS-CHECK (second signal for the predeclared run_s9.py).

Reproduces E[f] on the SAME nets/seeds the predeclared harness uses, but with a
DIFFERENT unbiased transect estimator:
   predeclared:  Ef = (1/kappa_d) E[ sum_k phi(t_k) c_k ||a_k|| ]     (Crofton norm)
   here (mine):  Ef = d * E[ sum_k phi(t_k) c_k (a_k . u) ]           (slope-jump/d)
The neuron-averaged output f = A . wbar equals a scalar-output net with W_L = wbar,
so my s9_core (scalar output, exact mask-product gradients) applies directly.

Writes s9_crosscheck.json.  No reads of the predeclared results; no clobbering.
"""
import json
import time
import numpy as np
from math import sqrt

from s9_core import forward_grad, forward_only, transect_line, sample_line


def make_net_predeclared(d, width, L, out_w, seed):
    """Identical to run_s9.make_net (bias-free, He init, RNG=default_rng(seed))."""
    rng = np.random.default_rng(seed)
    widths = [d] + [width] * (L - 1) + [out_w]
    return [rng.normal(0.0, sqrt(2.0 / widths[i]), size=(widths[i + 1], widths[i]))
            for i in range(L)]


def equiv_scalar_net(Ws):
    """Neuron-averaged readout f = A @ wbar  <=>  scalar net with W_L = wbar row."""
    wbar = Ws[-1].mean(axis=0)          # (h,)
    return Ws[:-1] + [wbar[None, :]]


def mc_ef(Ws, d, n, rng, chunk=500000):
    s = ss = 0.0
    tot = 0
    while tot < n:
        m = min(chunk, n - tot)
        X = rng.standard_normal((m, d))
        f = forward_only(Ws, X)
        s += f.sum(); ss += (f * f).sum(); tot += m
    mean = s / tot
    return mean, sqrt(max(ss / tot - mean * mean, 0) / tot)


def transect_ef(Ws, d, n_lines, rng, hidden):
    vals = np.empty(n_lines)
    per_layer = np.zeros((n_lines, hidden))
    events = np.empty(n_lines)
    for k in range(n_lines):
        base, v = sample_line(d, rng)
        tot, pl, ne = transect_line(Ws, base, v)
        vals[k] = d * tot
        per_layer[k] = d * pl
        events[k] = ne
    return vals, per_layer, events


def fwd_flops(d, width, depth, out_w):
    ins = [d] + [width] * (depth - 1)
    outs = [width] * (depth - 1) + [out_w]
    return sum(2 * i * o for i, o in zip(ins, outs))


def main():
    t0 = time.time()
    out = {"role": "independent_cross_check_of_predeclared_run_s9"}
    rng = np.random.default_rng(777)

    # ---- Stage A: predeclared seeds/geometry ----
    d, width, L, out_w = 16, 16, 4, 16
    hidden = L - 1
    A_LINES = 8000
    A_MC = 2_000_000
    seedsA = [101, 202, 303]
    A = []
    euler_max = 0.0
    for seed in seedsA:
        Ws = equiv_scalar_net(make_net_predeclared(d, width, L, out_w, seed))
        mc, mc_se = mc_ef(Ws, d, A_MC, rng)
        Xg = rng.standard_normal((300000, d))
        f, g = forward_grad(Ws, Xg)
        emax = float(np.max(np.abs((Xg * g).sum(1) - f)))
        euler_max = max(euler_max, emax)
        vals, per_layer, events = transect_ef(Ws, d, A_LINES, rng, hidden)
        tm, tse = float(vals.mean()), float(vals.std() / sqrt(A_LINES))
        z = (tm - mc) / sqrt(tse ** 2 + mc_se ** 2)
        fr = (per_layer.mean(0) / tm).tolist()
        A.append(dict(seed=seed, mc=mc, mc_se=mc_se, euler_max=emax,
                      transect=tm, transect_se=tse, z_vs_mc=float(z),
                      layer_fractions=[float(x) for x in fr],
                      mean_events=float(events.mean())))
        print("[xA seed %d] MC=%+.5f transect=%+.5f z=%+.2f Lfrac=[%s] ev=%.0f" % (
            seed, mc, tm, z, ",".join("%.2f" % x for x in fr), events.mean()),
            flush=True)
    out["stageA"] = A
    out["stageA_euler_max_persample_err"] = euler_max
    frac0 = float(np.mean([a["layer_fractions"][0] for a in A]))
    out["stageA_first_layer_only_fraction"] = frac0
    out["stageA_first_layer_only_closes"] = bool(abs(frac0 - 1.0) < 0.05)

    # ---- Stage B: predeclared seeds/geometry, my variance-per-FLOP ----
    d, width, L, out_w = 64, 64, 8, 64
    hidden = L - 1
    F = fwd_flops(d, width, L, out_w)
    from scipy.special import gammaln
    ER = float(np.sqrt(2.0) * np.exp(gammaln((d + 1) / 2) - gammaln(d / 2)))
    B_LINES = 500
    B_MC = 300000
    seedsB = [404, 505, 606]
    B = []
    for seed in seedsB:
        Ws = equiv_scalar_net(make_net_predeclared(d, width, L, out_w, seed))
        vals, _, events = transect_ef(Ws, d, B_LINES, rng, hidden)
        var_T = float(vals.var(ddof=1)); mev = float(events.mean())
        flop_T = (3.0 * mev + 1.0) * F
        V_T = var_T * flop_T
        X = rng.standard_normal((B_MC, d)); f = forward_only(Ws, X)
        var_mc = float(f.var(ddof=1)); V_mc = var_mc * F
        G = rng.standard_normal((B_MC // 2, d))
        U = G / np.linalg.norm(G, axis=1, keepdims=True)
        est = ER * 0.5 * (forward_only(Ws, U) + forward_only(Ws, -U))
        var_ra = float(est.var(ddof=1)); V_ra = var_ra * 2.0 * F
        B.append(dict(seed=seed, mean_events=mev, var_T=var_T, var_mc=var_mc,
                      var_ra=var_ra, ratio_vs_plain=V_T / V_mc,
                      ratio_vs_radial=V_T / V_ra,
                      transect_mean=float(vals.mean()), mc_mean=float(f.mean()),
                      ra_mean=float(est.mean())))
        print("[xB seed %d] ev=%.0f ratio(T/plain)=%.0fx ratio(T/radial)=%.0fx" % (
            seed, mev, V_T / V_mc, V_T / V_ra), flush=True)
    out["stageB"] = B
    out["stageB_ratio_vs_plainMC_mean"] = float(np.mean([b["ratio_vs_plain"] for b in B]))
    out["stageB_ratio_vs_radialMC_mean"] = float(np.mean([b["ratio_vs_radial"] for b in B]))
    out["runtime_sec"] = time.time() - t0
    with open("s9_crosscheck.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print("WROTE s9_crosscheck.json (%.0fs)" % out["runtime_sec"], flush=True)


if __name__ == "__main__":
    main()
