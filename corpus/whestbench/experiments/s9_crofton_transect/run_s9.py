"""S9 (ledger id s9_crofton_kink_transect_identity)
Crofton kink-transect identity for bias-free ReLU MLP Gaussian means.

Identity (derived in S9_VERDICT.md):
  For a bias-free ReLU MLP with linear readout, neuron-averaged scalar
  f(x) = wbar . z^{(L-1)}(x), X ~ N(0, I_d):

    E[f(X)] = int_K J(x) phi_d(x) dH^{d-1}(x)          (master, Euler + Stein/BV)

  where K = kink set (union of conical facets where one hidden preactivation
  crosses 0), J = jump of the normal derivative = c * ||a||, with
    a = grad_x h^{(l)}_j (upstream chain),  c = d f / d z^{(l)}_j (downstream chain).

  Crofton/transect estimator (line = x_perp + t u, u ~ Unif(S^{d-1}),
  x_perp = P_{u_perp} z, z ~ N(0,I_d)):

    PRIMARY  (kappa-averaged, finite variance):
        Ef_hat = (1/kappa_d) * sum_k phi_1(t_k) c_k ||a_k||
        kappa_d = Gamma(d/2) / (sqrt(pi) Gamma((d+1)/2)) = E|<nu,u>|
    SECONDARY (per-u exact, heavy-tailed; cross-check only):
        Ef_hat = sum_k phi_1(t_k) c_k ||a_k||^2 / |a_k . u|

  Machine-precision structural checks per line:
    (i)  F(t) = f(x_perp + t u) is affine between consecutive enumerated knots
    (ii) slope jump at each knot equals c_k |a_k . u|

Stage A gate: |transect - MC| <= 4 * SE(difference) on 3/3 width-16 depth-4 nets.
              (Literal 4*SE_MC also reported; see deviation note in verdict.)
Stage B gate: variance-per-FLOP ratio (transect/MC) <= 10 PASS, > 100 KILL,
              else INCONCLUSIVE, on width-64 depth-8 nets at matched FLOPs.
"""

import json
import os
import time
from math import exp, lgamma, pi, sqrt

import numpy as np

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
T_WINDOW = 13.6  # phi_1(13.6) ~ 3e-41: truncation bias bound reported in verdict
SQRT2PI = sqrt(2.0 * pi)

# ----------------------------------------------------------------------------
# FLOP meter (multiply-adds inside matmul-like kernels of the estimator path)
# ----------------------------------------------------------------------------
class Meter:
    def __init__(self):
        self.madds = 0

M = Meter()

def mm(A, B):
    """Metered matmul A @ B, counts rows*inner*cols multiply-adds."""
    M.madds += A.shape[0] * A.shape[1] * B.shape[1]
    return A @ B

def kappa_d(d):
    return exp(lgamma(d / 2.0) - lgamma((d + 1) / 2.0)) / sqrt(pi)

def mean_norm(d):
    """E||X|| for X ~ N(0, I_d)."""
    return sqrt(2.0) * exp(lgamma((d + 1) / 2.0) - lgamma(d / 2.0))

# ----------------------------------------------------------------------------
# Nets: L weight matrices, bias-free, He init N(0, 2/fan_in); hidden ReLU,
# linear readout; scalar of interest = mean over output neurons.
# ----------------------------------------------------------------------------
def make_net(d, width, L, out_w, seed):
    rng = np.random.default_rng(seed)
    widths = [d] + [width] * (L - 1) + [out_w]
    return [rng.normal(0.0, sqrt(2.0 / widths[i]), size=(widths[i + 1], widths[i]))
            for i in range(L)]

def wbar_of(Ws):
    return Ws[-1].mean(axis=0)

def f_batch(Ws, X, meter=False):
    A = X
    for W in Ws[:-1]:
        A = mm(A, W.T) if meter else A @ W.T
        A = np.maximum(A, 0.0)
    wb = wbar_of(Ws)
    if meter:
        M.madds += A.shape[0] * wb.size
    return A @ wb

def mc_cost_per_sample(Ws):
    c = 0
    for W in Ws[:-1]:
        c += W.shape[0] * W.shape[1]
    c += Ws[-1].shape[1]  # wbar readout
    return c

# ----------------------------------------------------------------------------
# Transect engine: exact breakpoint enumeration by layerwise interval tracking
# ----------------------------------------------------------------------------
def enumerate_knots(Ws, Xp, U, T=T_WINDOW, meter=False):
    """All zeros of hidden preactivations along lines x_perp + t u, |t| < T.

    Xp: (B, d) points on u^perp;  U: (B, d) unit directions.
    Returns flat arrays (line, t, layer[1-based], neuron).
    Exact within the window: at stage l, intervals are refined by all knots of
    layers < l, so every layer-l preactivation is affine on each interval and
    all of its zeros are roots of that affine function.
    """
    hidden = Ws[:-1]
    Lh = len(hidden)
    B = Xp.shape[0]
    MMf = mm if meter else (lambda A, Bm: A @ Bm)

    kt_line = np.zeros(0, np.int64)
    kt_t = np.zeros(0, np.float64)
    kt_layer = np.zeros(0, np.int64)
    kt_neu = np.zeros(0, np.int64)

    for l in range(1, Lh + 1):
        nk = kt_t.size
        if nk:
            order = np.lexsort((kt_t, kt_line))
            st = kt_t[order]
            cnt = np.bincount(kt_line, minlength=B)
        else:
            st = kt_t
            cnt = np.zeros(B, np.int64)
        niv = cnt + 1
        tot = int(niv.sum())
        iv_line = np.repeat(np.arange(B), niv)
        starts = np.zeros(B, np.int64)
        starts[1:] = np.cumsum(niv)[:-1]
        pos = np.arange(tot) - np.repeat(starts, niv)
        kstart = np.zeros(B, np.int64)
        kstart[1:] = np.cumsum(cnt)[:-1]
        gk = np.repeat(kstart, niv) + pos
        if nk:
            lefts = np.where(pos == 0, -T, st[np.clip(gk - 1, 0, nk - 1)])
            rights = np.where(pos == cnt[iv_line], T, st[np.clip(gk, 0, nk - 1)])
        else:
            lefts = np.full(tot, -T)
            rights = np.full(tot, T)
        reps = 0.5 * (lefts + rights)

        A0 = Xp[iv_line] + reps[:, None] * U[iv_line]
        A1 = U[iv_line]
        for m in range(l - 1):
            H0 = MMf(A0, hidden[m].T)
            H1 = MMf(A1, hidden[m].T)
            g = H0 > 0
            A0 = np.where(g, H0, 0.0)
            A1 = np.where(g, H1, 0.0)
        P0 = MMf(A0, hidden[l - 1].T)
        P1 = MMf(A1, hidden[l - 1].T)
        with np.errstate(divide="ignore", invalid="ignore"):
            tz = reps[:, None] - P0 / P1
        ok = np.isfinite(tz) & (tz > lefts[:, None]) & (tz < rights[:, None])
        r, ccol = np.nonzero(ok)
        kt_line = np.concatenate([kt_line, iv_line[r]])
        kt_t = np.concatenate([kt_t, tz[r, ccol]])
        kt_layer = np.concatenate([kt_layer, np.full(r.size, l, np.int64)])
        kt_neu = np.concatenate([kt_neu, ccol.astype(np.int64)])
    return kt_line, kt_t, kt_layer, kt_neu


def knot_contribs(Ws, Xp, U, kt_line, kt_t, kt_layer, kt_neu, meter=False):
    """Per-knot phi_1(t), c, ||a||, a.u -> primary and secondary weights."""
    hidden = Ws[:-1]
    Lh = len(hidden)
    K = kt_t.size
    d = Xp.shape[1]
    MMf = mm if meter else (lambda A, Bm: A @ Bm)

    if K == 0:
        z = np.zeros(0)
        return z, z, z, z, z, z

    Xk = Xp[kt_line] + kt_t[:, None] * U[kt_line]
    gates = []
    A = Xk
    for m in range(Lh):
        H = MMf(A, hidden[m].T)
        g = H > 0
        gates.append(g)
        A = np.where(g, H, 0.0)
    wb = wbar_of(Ws)

    anorm = np.zeros(K)
    adotu = np.zeros(K)
    cval = np.zeros(K)
    for l in range(1, Lh + 1):
        idx = np.nonzero(kt_layer == l)[0]
        if idx.size == 0:
            continue
        # upstream: a^T = W_l[j,:] D_{l-1} W_{l-1} ... D_1 W_1
        V = hidden[l - 1][kt_neu[idx]].copy()
        for m in range(l - 1, 0, -1):
            V = MMf(V * gates[m - 1][idx], hidden[m - 1])
        anorm[idx] = np.sqrt((V * V).sum(axis=1))
        adotu[idx] = (V * U[kt_line[idx]]).sum(axis=1)
        if meter:
            M.madds += 2 * idx.size * d
        # downstream: c = [wbar^T D_{Lh} W_{Lh} ... D_{l+1} W_{l+1}]_j
        R = np.repeat(wb[None, :], idx.size, axis=0)
        for m in range(Lh, l, -1):
            R = MMf(R * gates[m - 1][idx], hidden[m - 1])
        cval[idx] = R[np.arange(idx.size), kt_neu[idx]]

    phi = np.exp(-0.5 * kt_t ** 2) / SQRT2PI
    prim = phi * cval * anorm
    sec = phi * cval * anorm ** 2 / np.maximum(np.abs(adotu), 1e-300)
    return prim, sec, anorm, adotu, cval, phi


def transect_lines(Ws, d, n_lines, rng, meter=False, antithetic=True):
    """Run n_lines transect lines; returns per-line primary/secondary sums,
    knot counts, and (if metered) madds consumed."""
    kap = kappa_d(d)
    Z = rng.standard_normal((n_lines if not antithetic else n_lines // 2, d))
    Udir = rng.standard_normal(Z.shape)
    Udir /= np.linalg.norm(Udir, axis=1, keepdims=True)
    Xp = Z - (np.einsum("ij,ij->i", Z, Udir))[:, None] * Udir
    if antithetic:
        Xp = np.vstack([Xp, -Xp])
        Udir = np.vstack([Udir, Udir])
    m0 = M.madds
    kl, ktv, klay, kne = enumerate_knots(Ws, Xp, Udir, meter=meter)
    prim, sec, _, _, _, _ = knot_contribs(Ws, Xp, Udir, kl, ktv, klay, kne, meter=meter)
    madds = M.madds - m0
    B = Xp.shape[0]
    line_prim = np.bincount(kl, weights=prim, minlength=B) / kap
    line_sec = np.bincount(kl, weights=sec, minlength=B)
    line_knots = np.bincount(kl, minlength=B)
    return line_prim, line_sec, line_knots, madds


# ----------------------------------------------------------------------------
# Machine-precision structural checks (enumeration exactness + jump algebra)
# ----------------------------------------------------------------------------
def structural_checks(Ws, d, rng, n_lines=30, T=T_WINDOW):
    max_aff = 0.0
    max_jump = 0.0
    for _ in range(n_lines):
        z = rng.standard_normal(d)
        u = rng.standard_normal(d)
        u /= np.linalg.norm(u)
        xp = z - (z @ u) * u
        kl, ktv, klay, kne = enumerate_knots(Ws, xp[None, :], u[None, :], T=T)
        _, _, anorm, adotu, cval, _ = knot_contribs(
            Ws, xp[None, :], u[None, :], kl, ktv, klay, kne)
        o = np.argsort(ktv)
        ts = ktv[o]
        grid = np.concatenate([[-T], ts, [T]])
        Fv = f_batch(Ws, xp[None, :] + grid[:, None] * u[None, :])
        scale = 1.0 + np.abs(Fv).max()
        # (i) affineness between consecutive knots at 1/3 and 2/3 points
        dt = np.diff(grid)
        keep = dt > 1e-9
        for frac in (1.0 / 3.0, 2.0 / 3.0):
            pts = grid[:-1] + frac * dt
            Fp = f_batch(Ws, xp[None, :] + pts[:, None] * u[None, :])
            lin = Fv[:-1] + frac * (Fv[1:] - Fv[:-1])
            if keep.any():
                max_aff = max(max_aff, float(np.abs((Fp - lin)[keep]).max() / scale))
        # (ii) slope jumps vs c |a.u|
        slopes = np.diff(Fv) / dt
        ds = slopes[1:] - slopes[:-1]           # jump at each interior knot
        pred = (cval * np.abs(adotu))[o]
        keep2 = keep[:-1] & keep[1:]
        if keep2.any():
            rel = np.abs(ds - pred)[keep2] / (1.0 + np.abs(pred)[keep2])
            max_jump = max(max_jump, float(rel.max()))
    return max_aff, max_jump


# ----------------------------------------------------------------------------
# Closed-form unit tests
# ----------------------------------------------------------------------------
def unit_tests(rng):
    out = {}
    # kappa_d formula vs MC of E|u_1| in d=16
    d = 16
    U = rng.standard_normal((400000, d))
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    emp = np.abs(U[:, 0]).mean()
    se = np.abs(U[:, 0]).std(ddof=1) / sqrt(U.shape[0])
    out["kappa16_formula"] = kappa_d(16)
    out["kappa16_mc"] = float(emp)
    out["kappa16_z"] = float((emp - kappa_d(16)) / se)

    # single ReLU neuron, d=4: E = ||w||/sqrt(2 pi)
    d = 4
    rw = np.random.default_rng(7)
    w = rw.normal(0, 1, (1, d))
    Ws = [w, np.array([[1.0]])]
    exact = np.linalg.norm(w) / SQRT2PI
    lp, ls, lk, _ = transect_lines(Ws, d, 200000, rng)
    est, sev = lp.mean(), lp.std(ddof=1) / sqrt(lp.size)
    out["single_neuron"] = dict(exact=float(exact), transect=float(est),
                                se=float(sev), z=float((est - exact) / sev))

    # |x1| via two neurons, d=3: E = sqrt(2/pi)
    d = 3
    W1 = np.zeros((2, d)); W1[0, 0] = 1.0; W1[1, 0] = -1.0
    Ws = [W1, np.array([[1.0, 1.0]])]
    exact = sqrt(2.0 / pi)
    lp, ls, lk, _ = transect_lines(Ws, d, 200000, rng)
    est, sev = lp.mean(), lp.std(ddof=1) / sqrt(lp.size)
    out["abs_x1"] = dict(exact=float(exact), transect=float(est),
                         se=float(sev), z=float((est - exact) / sev))

    # depth-2 (one hidden layer) width-16, d=8: E = sum_k wbar_k ||W1_k|| / sqrt(2pi)
    d = 8
    Ws = make_net(d, 16, 2, 16, seed=42)
    exact = float((wbar_of(Ws) * np.linalg.norm(Ws[0], axis=1)).sum() / SQRT2PI)
    lp, ls, lk, _ = transect_lines(Ws, d, 200000, rng)
    est, sev = lp.mean(), lp.std(ddof=1) / sqrt(lp.size)
    out["depth2_closed_form"] = dict(exact=exact, transect=float(est),
                                     se=float(sev), z=float((est - exact) / sev))
    return out


# ----------------------------------------------------------------------------
# Stage A
# ----------------------------------------------------------------------------
def mc_antithetic(Ws, d, n_pairs, rng, chunk=250000):
    """Brute-force MC with antithetic pairing: pair value (f(x)+f(-x))/2."""
    s = 0.0
    s2 = 0.0
    n = 0
    left = n_pairs
    while left > 0:
        c = min(chunk, left)
        X = rng.standard_normal((c, d))
        v = 0.5 * (f_batch(Ws, X) + f_batch(Ws, -X))
        s += v.sum()
        s2 += (v * v).sum()
        n += c
        left -= c
    mean = s / n
    var = s2 / n - mean * mean
    return mean, sqrt(var / n), var

def mc_sphere(Ws, d, n_pairs, rng, chunk=250000):
    """Radially-conditioned MC: E[f] = E||X|| * E[f(theta)], antipodal pairs."""
    En = mean_norm(d)
    s = 0.0
    s2 = 0.0
    n = 0
    left = n_pairs
    while left > 0:
        c = min(chunk, left)
        Z = rng.standard_normal((c, d))
        Th = Z / np.linalg.norm(Z, axis=1, keepdims=True)
        v = En * 0.5 * (f_batch(Ws, Th) + f_batch(Ws, -Th))
        s += v.sum()
        s2 += (v * v).sum()
        n += c
        left -= c
    mean = s / n
    var = s2 / n - mean * mean
    return mean, sqrt(var / n), var


def stage_A(seeds, n_mc_pairs=5_000_000, time_budget_per_seed=150.0):
    d, width, L, out_w = 16, 16, 4, 16
    results = []
    for seed in seeds:
        t0 = time.time()
        Ws = make_net(d, width, L, out_w, seed)
        rng = np.random.default_rng(10_000 + seed)

        # 1) brute-force MC (>= 1e7 Gaussian samples via 5e6 antithetic pairs)
        mc_mean, mc_se, mc_var = mc_antithetic(Ws, d, n_mc_pairs, rng)
        # cross-check MC a second way (radial conditioning; exact E||X||)
        sph_mean, sph_se, _ = mc_sphere(Ws, d, 1_000_000, rng)

        # 2) transect: pilot to size the run, then main run in batches
        pilot_n = 8192
        tp0 = time.time()
        lp, lsec, lkn, _ = transect_lines(Ws, d, pilot_n, rng)
        pilot_dt = time.time() - tp0
        rate = pilot_n / max(pilot_dt, 1e-9)
        elapsed = time.time() - t0
        n_target = int(min(1_000_000, max(100_000,
                        rate * max(time_budget_per_seed - elapsed, 30.0))))
        n_target = (n_target // 8192) * 8192
        prim_all = [lp]
        sec_all = [lsec]
        kn_all = [lkn]
        done = pilot_n
        while done < n_target:
            b = min(32768, n_target - done)
            b = (b // 2) * 2
            lp, lsec, lkn, _ = transect_lines(Ws, d, b, rng)
            prim_all.append(lp)
            sec_all.append(lsec)
            kn_all.append(lkn)
            done += b
        prim = np.concatenate(prim_all)
        secv = np.concatenate(sec_all)
        kn = np.concatenate(kn_all)
        tr_mean = float(prim.mean())
        tr_se = float(prim.std(ddof=1) / sqrt(prim.size))
        # secondary weighting (per-u exact form; heavy-tailed -> also MoM)
        sec_mean = float(secv.mean())
        sec_se = float(secv.std(ddof=1) / sqrt(secv.size))
        blocks = np.array_split(secv, 64)
        sec_mom = float(np.median([b.mean() for b in blocks]))

        # 3) machine-precision structural checks
        max_aff, max_jump = structural_checks(Ws, d, rng, n_lines=30)

        diff = tr_mean - mc_mean
        se_comb = sqrt(tr_se ** 2 + mc_se ** 2)
        z_comb = abs(diff) / se_comb
        z_lit = abs(diff) / mc_se
        res = dict(
            seed=seed, d=d, width=width, depth=L,
            mc_mean=float(mc_mean), mc_se=float(mc_se),
            mc_n_samples=int(2 * n_mc_pairs),
            mc_sphere_mean=float(sph_mean), mc_sphere_se=float(sph_se),
            mc_crosscheck_z=float(abs(sph_mean - mc_mean) /
                                  sqrt(sph_se ** 2 + mc_se ** 2)),
            transect_mean=tr_mean, transect_se=tr_se,
            transect_n_lines=int(prim.size),
            transect_secondary_mean=sec_mean, transect_secondary_se=sec_se,
            transect_secondary_mom=sec_mom,
            mean_knots_per_line=float(kn.mean()),
            max_knots_per_line=int(kn.max()),
            diff=float(diff), se_combined=float(se_comb),
            z_combined=float(z_comb), z_literal_vs_mc_se=float(z_lit),
            gate_pass_combined=bool(z_comb <= 4.0),
            gate_pass_literal=bool(z_lit <= 4.0),
            structural_max_affine_violation=float(max_aff),
            structural_max_jump_violation=float(max_jump),
            runtime_s=float(time.time() - t0),
        )
        results.append(res)
        print(f"[A seed {seed}] MC={mc_mean:.6f}+-{mc_se:.2e} "
              f"T={tr_mean:.6f}+-{tr_se:.2e} z_comb={z_comb:.2f} "
              f"lines={prim.size} knots/line={kn.mean():.1f} "
              f"aff={max_aff:.2e} jump={max_jump:.2e} "
              f"({res['runtime_s']:.0f}s)", flush=True)
    return results


# ----------------------------------------------------------------------------
# Stage B
# ----------------------------------------------------------------------------
def stage_B(seeds, n_rep=16, lines_per_rep=12, truth_pairs=1_000_000):
    d, width, L, out_w = 64, 64, 8, 64
    results = []
    pooled_T_err = []
    pooled_M_err = []
    for seed in seeds:
        t0 = time.time()
        Ws = make_net(d, width, L, out_w, seed)
        rng = np.random.default_rng(20_000 + seed)

        # ground truth (much tighter than replicate errors)
        truth, truth_se, _ = mc_antithetic(Ws, d, truth_pairs, rng)

        # transect replicates, metered
        T_est = np.zeros(n_rep)
        T_madds = np.zeros(n_rep)
        all_line_sums = []
        all_knots = []
        for r in range(n_rep):
            lp, _, lkn, madds = transect_lines(Ws, d, lines_per_rep, rng,
                                               meter=True)
            T_est[r] = lp.mean()
            T_madds[r] = madds
            all_line_sums.append(lp)
            all_knots.append(lkn)
        line_sums = np.concatenate(all_line_sums)
        knots = np.concatenate(all_knots)
        C_line = float(T_madds.sum() / line_sums.size)

        # matched-FLOP radially-conditioned MC replicates
        c_samp = mc_cost_per_sample(Ws)
        n_pairs_rep = max(1, int(round(T_madds.mean() / (2.0 * c_samp))))
        M_est = np.zeros(n_rep)
        for r in range(n_rep):
            m, _, _ = mc_sphere(Ws, d, n_pairs_rep, rng)
            M_est[r] = m
        mc_pair_madds = 2.0 * c_samp

        # per-draw variances (route 2) with a dedicated large MC sample
        big_m, big_se, big_pair_var = mc_sphere(Ws, d, 200_000, rng)
        var_line = float(line_sums.var(ddof=1))
        var_pair = float(big_pair_var)
        ratio_perdraw = (var_line * C_line) / (var_pair * mc_pair_madds)

        # replicate-route variance ratio (equal budgets by construction)
        vT = float(T_est.var(ddof=1))
        vM = float(M_est.var(ddof=1))
        ratio_rep = vT / vM

        # bootstrap CI on per-draw ratio (line-sum resampling dominates)
        brng = np.random.default_rng(999 + seed)
        n_ls = line_sums.size
        boot = np.empty(4000)
        for b in range(4000):
            idx = brng.integers(0, n_ls, n_ls)
            boot[b] = (line_sums[idx].var(ddof=1) * C_line) / (var_pair * mc_pair_madds)
        ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))

        # error correlation (independent randomness by construction)
        eT = T_est - truth
        eM = M_est - truth
        corr = float(np.corrcoef(eT, eM)[0, 1])
        pooled_T_err.extend((eT / eT.std(ddof=1)).tolist())
        pooled_M_err.extend((eM / eM.std(ddof=1)).tolist())

        res = dict(
            seed=seed, d=d, width=width, depth=L,
            truth=float(truth), truth_se=float(truth_se),
            n_rep=n_rep, lines_per_rep=lines_per_rep,
            C_line_madds=C_line, mc_pair_madds=float(mc_pair_madds),
            matched_mc_pairs_per_rep=int(n_pairs_rep),
            var_line=var_line, var_mc_pair=var_pair,
            ratio_perdraw=float(ratio_perdraw), ratio_perdraw_ci=ci,
            ratio_replicate=float(ratio_rep),
            var_T_rep=vT, var_M_rep=vM,
            err_corr=corr,
            mean_knots_per_line=float(knots.mean()),
            max_abs_line_sum=float(np.abs(line_sums).max()),
            transect_grand_mean=float(T_est.mean()),
            transect_grand_z=float((T_est.mean() - truth) /
                                   (T_est.std(ddof=1) / sqrt(n_rep))),
            runtime_s=float(time.time() - t0),
        )
        results.append(res)
        print(f"[B seed {seed}] ratio_perdraw={ratio_perdraw:.1f} "
              f"CI=({ci[0]:.1f},{ci[1]:.1f}) ratio_rep={ratio_rep:.1f} "
              f"corr={corr:+.2f} C_line={C_line:.3e} knots/line={knots.mean():.0f} "
              f"({res['runtime_s']:.0f}s)", flush=True)

    pooled_corr = float(np.corrcoef(pooled_T_err, pooled_M_err)[0, 1])
    return results, pooled_corr


# ----------------------------------------------------------------------------
def main():
    t_start = time.time()
    rng = np.random.default_rng(123456)
    print("=== unit tests ===", flush=True)
    ut = unit_tests(rng)
    print(json.dumps(ut, indent=1), flush=True)

    print("=== Stage A ===", flush=True)
    seeds_A = [101, 202, 303]
    resA = stage_A(seeds_A, time_budget_per_seed=110.0)
    a_pass = all(r["gate_pass_combined"] for r in resA)
    verdict_A = "VERIFIED" if a_pass else "KILL"
    print(f"Stage A verdict: {verdict_A}", flush=True)

    resB = None
    pooled_corr = None
    verdict_B = "NOT RUN"
    if a_pass:
        print("=== Stage B ===", flush=True)
        seeds_B = [404, 505, 606]
        resB, pooled_corr = stage_B(seeds_B)
        ratios = [r["ratio_perdraw"] for r in resB]
        geo = float(np.exp(np.mean(np.log(ratios))))
        if geo <= 10.0:
            verdict_B = "PASS"
        elif geo > 100.0:
            verdict_B = "KILL"
        else:
            verdict_B = "INCONCLUSIVE"
        print(f"Stage B ratios={ratios} geomean={geo:.1f} -> {verdict_B}",
              flush=True)

    out = dict(
        experiment="s9_crofton_kink_transect_identity",
        date="2026-08-09",
        window_T=T_WINDOW,
        kappa_16=kappa_d(16), kappa_64=kappa_d(64),
        unit_tests=ut,
        stage_A=resA, stage_A_verdict=verdict_A,
        stage_B=resB, stage_B_verdict=verdict_B,
        stage_B_geomean_ratio=(None if resB is None else
                               float(np.exp(np.mean(np.log(
                                   [r["ratio_perdraw"] for r in resB]))))),
        stage_B_pooled_err_corr=pooled_corr,
        total_runtime_s=float(time.time() - t_start),
    )
    with open(os.path.join(OUT_DIR, "s9_results.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"total {out['total_runtime_s']:.0f}s -> s9_results.json", flush=True)


if __name__ == "__main__":
    main()
