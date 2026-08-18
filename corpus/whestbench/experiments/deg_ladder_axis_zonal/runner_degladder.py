"""deg_ladder_own_axis_capture -- does own-axis zonal concentration RISE with harmonic degree?

deg6_own_axis_zonal_capture_v1 measured ONE degree and killed on materiality: own-axis
capture of the depth-32 readout was 0.001872 of the degree-3-and-above residual, 10.2x the
random floor but a tenth of the 2 percent bar.  The owner's follow-on premise is a DEGREE
BAND, not a degree: ReLU's kink gives each entry-layer neuron a polynomially-decaying
harmonic tail that is EXACTLY zonal about its own axis, while the cross-axis mixing
background is built from products of smoother low-degree factors and should decay faster,
so the own-axis SHARE ought to grow with degree and the CUMULATIVE capture over the
measured band is what a multi-degree theorem-fixed control could remove.

This cell measures the full (degree x depth) capture surface on ONE set of forward passes:
degrees 6, 8, 12, 16, 24, 48 harvested from a single Gegenbauer recurrence, against the
same six matched-count random axis pools, on the identical samples, with the identical
deg-3-and-above denominator so the per-degree captures ADD (distinct harmonic degrees are
exactly orthogonal).  Degree 6 replicates v1 as the anchor rung.

Two exact positive controls ride every rung: relu(w.u) has a closed-form own-axis
coefficient lambda_n at every degree (exact rational absolute moments), and the
second-layer preactivation lies EXACTLY in the entry-layer zonal span, so its captured
degree-n energy has a closed form too.  The second control is the power gate: a rung whose
known in-span energy the instrument cannot recover is reported, not gated.

Diagnostic only; synthetic seeded He nets; no truth, holdout, scorer or submission artifact
is read; zero charge against H.
"""
from __future__ import annotations

import json
import math
import os
import time
from fractions import Fraction

import numpy as np

D = 256
WIDTH = 256
DEPTH = 32
LADDER_DEG = (6, 8, 12, 16, 24, 48)     # 6 = v1 replication anchor
NMAX = LADDER_DEG[-1]
N_PULLBACK = 8
N_RANDOM_POOLS = 6
LADDER = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
NEURONS_PER_LAYER = 2
R2_BAR = 0.02                       # predeclared materiality bar, R^2-of-deg>=3 units
DEN_FLOOR = 0.02                    # below this share the deg-2 subtraction is untrusted
GATE_NOISE_BAR = R2_BAR / len(LADDER_DEG)     # per-rung noise admission bar
GATE_SPAN_LO, GATE_SPAN_HI = 0.5, 2.0         # exact-span recovery band for the power gate
GATE_REACH = 0.5                              # share of E[e^2] = 1 the sample must reach
AXIS_BLOCK = 264
SAMP_TILE = 1024
METRIC_NAME = "deg_ladder_own_axis_capture_shortfall"

SMOKE = os.environ.get("DEGLADDER_SMOKE") == "1"
SEEDS = (778001312,) if SMOKE else (20260904, 20260905, 20260906)
M_PILOT = 2048 if SMOKE else 16384
M_HALF = 8192 if SMOKE else 327680
M_GRAD = 512 if SMOKE else 4096
CHUNK = 4096 if SMOKE else 16384


def r6(x) -> float:
    return float(np.round(float(x), 6))


def g6(x) -> float:
    return float("%.6g" % float(x))


def sph_dim(n: int, d: int) -> int:
    """dim H_n(S^{d-1}) = C(n+d-1, n) - C(n+d-3, n-2)."""
    return math.comb(n + d - 1, n) - (math.comb(n + d - 3, n - 2) if n >= 2 else 0)


# ---- normalized Gegenbauer machinery -------------------------------------------------
# P_n(1) = 1 from (n+d-3) P_n = (2n+d-4) t P_{n-1} - (n-1) P_{n-2}, P_0 = 1, P_1 = t.
# Addition theorem under unit-mass surface measure: sum_k Y_nk(u) Y_nk(v) = N(d,n) P_n(<u,v>),
# so the unit-L2-norm zonal about a is e_a = sqrt(N(d,n)) P_n(<.,a>) and <e_a,e_b> = P_n(<a,b>).
ALPHA = np.zeros(NMAX + 1)
BETA = np.zeros(NMAX + 1)
for _k in range(2, NMAX + 1):
    ALPHA[_k] = (2 * _k + D - 4) / (_k + D - 3)
    BETA[_k] = (_k - 1) / (_k + D - 3)

RUNG_IDX = {n: i for i, n in enumerate(LADDER_DEG)}
NR = len(LADDER_DEG)
DIMS = [sph_dim(n, D) for n in LADDER_DEG]
LOG_DIM = [math.log(x) for x in DIMS]
SQRT_N = [math.exp(0.5 * v) for v in LOG_DIM]
N2 = sph_dim(2, D)


def zonal_values(TT):
    """[P_n(TT) for n in LADDER_DEG], UNSCALED, by the forward three-term recurrence."""
    out = [None] * NR
    p0 = np.ones_like(TT)
    p1 = TT.astype(np.float64, copy=True)
    scr = np.empty_like(TT)
    for k in range(2, NMAX + 1):
        np.multiply(TT, p1, out=scr)
        scr *= ALPHA[k]
        p0 *= BETA[k]
        scr -= p0
        p0, p1, scr = p1, scr, p0
        r = RUNG_IDX.get(k)
        if r is not None:
            out[r] = p1.copy()
    return out


def zonal_accumulate(TT, Rt, C, s0, s1, E2):
    """One recurrence pass; at each rung accumulate C[r][s0:s1] += sqrt(N_r) P_n(TT)^T @ Rt
    and E2[r] += sum P_n(TT)^2 (the REACH statistic: E[e^2] = 1 exactly, so the measured
    mean is the share of the feature's own known variance this sample count reaches).

    The sqrt(N_r) scaling is applied AFTER the (axes x targets) contraction, so the large
    factor never multiplies the (tile x axes) array: at degree 48, sqrt(N) is about 1e28
    while P_48 is about 1e-28, and both stay far from float64 overflow either way.
    """
    p0 = np.ones_like(TT)
    p1 = TT.astype(np.float64, copy=True)
    scr = np.empty_like(TT)
    for k in range(2, NMAX + 1):
        np.multiply(TT, p1, out=scr)
        scr *= ALPHA[k]
        p0 *= BETA[k]
        scr -= p0
        p0, p1, scr = p1, scr, p0
        r = RUNG_IDX.get(k)
        if r is not None:
            C[r][s0:s1] += (p1.T @ Rt) * SQRT_N[r]
            E2[r] += float(np.vdot(p1, p1))


# ---- exact rational reference (independent of every float path above) ----------------
def exact_coeffs():
    """Ascending monomial coefficients of P_n for each rung, as exact Fractions."""
    got = {}
    p0 = [Fraction(1)] + [Fraction(0)] * NMAX
    p1 = [Fraction(0), Fraction(1)] + [Fraction(0)] * (NMAX - 1)
    for k in range(2, NMAX + 1):
        a = Fraction(2 * k + D - 4, k + D - 3)
        b = Fraction(k - 1, k + D - 3)
        p2 = [Fraction(0)] * (NMAX + 1)
        for i in range(k):
            p2[i + 1] += a * p1[i]
        for i in range(k - 1):
            p2[i] -= b * p0[i]
        p0, p1 = p1, p2
        if k in RUNG_IDX:
            got[k] = list(p1)
    return got


EXACT_COEF = exact_coeffs()


def exact_abs_moment(m: int) -> Fraction:
    """pi * E|<u,a>|^m for u uniform on S^{D-1}, m ODD, D even -- exactly rational.

    E|t|^m = G((m+1)/2) G(D/2) / (G(1/2) G((m+D)/2)); with m odd and D even the two
    half-integer Gammas contribute (2q)! sqrt(pi) / (4^q q!) and sqrt(pi), leaving 1/pi.
    """
    assert m % 2 == 1 and D % 2 == 0
    p = (m + 1) // 2
    q = (m + D - 1) // 2
    return Fraction(math.factorial(p - 1) * math.factorial(D // 2 - 1)
                    * (4 ** q) * math.factorial(q), math.factorial(2 * q))


def exact_lambda(n: int) -> float:
    """<relu(<.,a>), e_a> at degree n, exactly: relu(t) = (t+|t|)/2 and <t, P_n> = 0 for n>1,
    so lambda_n = sqrt(N(d,n)) * 0.5 * sum_j c_j E|t|^{j+1} with EXACT rational c_j and
    E|t|^{odd}.  Evaluated in log space, so the degree-48 alternating sum never cancels in
    floating point."""
    coef = EXACT_COEF[n]
    s = Fraction(0)
    for j, c in enumerate(coef):
        if c:
            s += c * exact_abs_moment(j + 1)
    if s == 0:
        return 0.0
    sign = 1.0 if s > 0 else -1.0
    s = abs(s)
    log_mag = (0.5 * LOG_DIM[RUNG_IDX[n]] + math.log(s.numerator) - math.log(s.denominator)
               - math.log(2.0) - math.log(math.pi))
    return sign * math.exp(log_mag)


LAMBDA = [exact_lambda(n) for n in LADDER_DEG]


def recurrence_exactness():
    """Relative error of the SHIPPED float64 recurrence against exact rational evaluation,
    at cosines spanning the sampled range (|t| ~ 1/16 typically) up to the axis-pool worst
    case, plus the P_n(1) = 1 fixed point.  This is the degree-48 stability check."""
    ts = [Fraction(k, 64) for k in (0, 1, 2, 4, 8, 16, 32, 48, 56, 64)]
    tf = np.array([float(t) for t in ts])
    vals = zonal_values(tf)
    worst = {}
    for n in LADDER_DEG:
        coef = EXACT_COEF[n]
        rel = 0.0
        for i, t in enumerate(ts):
            acc = Fraction(0)
            tp = Fraction(1)
            for c in coef:
                acc += c * tp
                tp *= t
            ex = float(acc)
            got = float(vals[RUNG_IDX[n]][i])
            if ex != 0.0:
                rel = max(rel, abs(got - ex) / abs(ex))
            else:
                rel = max(rel, abs(got))
        worst[n] = rel
    p_at_one = {n: float(vals[RUNG_IDX[n]][-1]) for n in LADDER_DEG}
    return worst, p_at_one


REC_ERR, P_AT_ONE = recurrence_exactness()
assert max(REC_ERR.values()) < 1e-9, "float64 Gegenbauer recurrence lost the exact value"
assert max(abs(v - 1.0) for v in P_AT_ONE.values()) < 1e-12, "P_n(1) != 1"
# lambda_6 must reproduce the v1 authenticated constant 0.00277366 (independent code path).
assert abs(LAMBDA[0] / 0.00277366 - 1.0) < 1e-5, "lambda_6 disagrees with the v1 closed form"
for _n in LADDER_DEG:
    _m = 2 * _n - 1
    _e = float(exact_abs_moment(_m)) / math.pi
    _l = math.exp(math.lgamma((_m + 1) / 2) + math.lgamma(D / 2)
                  - math.lgamma(0.5) - math.lgamma((_m + D) / 2))
    assert abs(_e / _l - 1.0) < 1e-12, "exact absolute moment disagrees with lgamma"


def hermite_limit_kurtosis(n: int) -> float:
    """E[h_n^4] for the Hermite limit h_n = He_n/sqrt(n!) of the normalized zonal:
    sum_k [C(n,k)^2 k!/n!]^2 (2n-2k)!.  Reference scale for the measured fourth moment;
    at n = 48, d = 256 the sphere is not in the fixed-n limit, so this is a SCALE, not an
    identity."""
    lf = math.lgamma
    tot = 0.0
    for k in range(n + 1):
        lg = 2.0 * (2 * (lf(n + 1) - lf(k + 1) - lf(n - k + 1)) + lf(k + 1) - lf(n + 1)) \
            + lf(2 * n - 2 * k + 1)
        tot += math.exp(lg)
    return tot


KURT_REF = [hermite_limit_kurtosis(n) for n in LADDER_DEG]


def target_names() -> list:
    names = []
    for l in LADDER:
        for j in range(NEURONS_PER_LAYER):
            names.append("L%d_%s_n%d" % (l, "act" if l == 1 else "pre", j))
    names.append("OUT")
    return names


NAMES = target_names()
T = len(NAMES)
OUT_IDX = T - 1
L2_IDX = [NAMES.index("L2_pre_n%d" % j) for j in range(NEURONS_PER_LAYER)]


def make_net(rng):
    Ws = [rng.standard_normal((WIDTH, D)) * math.sqrt(2.0 / D)]
    for _ in range(DEPTH - 1):
        Ws.append(rng.standard_normal((WIDTH, WIDTH)) * math.sqrt(2.0 / WIDTH))
    w_out = rng.standard_normal(WIDTH) * math.sqrt(2.0 / WIDTH)
    return Ws, w_out


def sample_sphere(rng, m):
    U = rng.standard_normal((m, D))
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    return U


def forward_targets(U, Ws, w_out):
    """(len(U), T) target values in NAMES order: layer-1 ACTIVATIONS (exactly zonal),
    layer-l PREACTIVATIONS for l >= 2, and the depth-32 scalar readout."""
    out = np.empty((len(U), T))
    col = 0
    H = U
    for l in range(1, DEPTH + 1):
        Z = H @ Ws[l - 1].T
        H = np.maximum(Z, 0.0)
        if l in LADDER:
            src = H if l == 1 else Z
            out[:, col:col + NEURONS_PER_LAYER] = src[:, :NEURONS_PER_LAYER]
            col += NEURONS_PER_LAYER
    out[:, OUT_IDX] = H @ w_out
    return out


def spec(ev):
    ev = np.maximum(ev, 0.0)
    s = ev.sum()
    return {"top1_share": r6(ev[0] / s),
            "top8_share": r6(ev[:N_PULLBACK].sum() / s),
            "participation_ratio": r6(float(s ** 2 / (ev ** 2).sum()))}


def spec_of(G):
    ev = np.linalg.eigvalsh(G.T @ G / len(G))[::-1]
    return spec(ev)


def ridge_and_pullback(U, Ws, w_out):
    """RAW input-gradient second-moment spectra for every target (the ridge-collinearity
    instrument: a function exactly zonal about one axis has a gradient collinear with that
    axis everywhere, so top1_share = 1 EXACTLY at layer 1 -- a hard anchor), plus v1's
    TANGENTIAL readout gradient used for the pullback axis pool."""
    masks, H = [], U
    for W in Ws:
        Z = H @ W.T
        m = Z > 0
        masks.append(m)
        H = np.where(m, Z, 0.0)
    f = H @ w_out
    ridge, col = {}, 0
    for l in LADDER:
        for j in range(NEURONS_PER_LAYER):
            if l == 1:
                G = masks[0][:, j:j + 1] * Ws[0][j][None, :]
            else:
                G = np.repeat(Ws[l - 1][j][None, :], len(U), axis=0)
                for k in range(l - 2, -1, -1):
                    G = np.where(masks[k], G, 0.0) @ Ws[k]
            ridge[NAMES[col]] = spec_of(G)
            col += 1
    G = np.repeat(w_out[None, :], len(U), axis=0)
    for k in range(DEPTH - 1, -1, -1):
        G = np.where(masks[k], G, 0.0) @ Ws[k]
    ridge["OUT"] = spec_of(G)
    return ridge, G - f[:, None] * U


def half_pass(rng, Ws, w_out, A, mu, B, n):
    """One independent half.  Returns (per-rung zonal coefficients [NR](n_axes, T),
    mean r^2 (T,), degree-1 accumulator b (D, T), degree-2 accumulator Q (T, D, D))."""
    n_ax = len(A)
    C = [np.zeros((n_ax, T)) for _ in range(NR)]
    E2 = [0.0] * NR
    S2 = np.zeros(T)
    b = np.zeros((D, T))
    Q = np.zeros((T, D, D))
    done = 0
    while done < n:
        m = min(CHUNK, n - done)
        U = sample_sphere(rng, m)
        R = forward_targets(U, Ws, w_out)
        R -= mu                       # exact-zero degree-0 control variate (pilot-fitted)
        R -= D * (U @ B)              # exact-zero degree-1 control variate (pilot-fitted)
        S2 += np.einsum("ij,ij->j", R, R)
        b += U.T @ R
        for s0 in range(0, n_ax, AXIS_BLOCK):
            s1 = min(s0 + AXIS_BLOCK, n_ax)
            Ab = A[s0:s1]
            for t0 in range(0, m, SAMP_TILE):
                t1 = min(t0 + SAMP_TILE, m)
                zonal_accumulate(U[t0:t1] @ Ab.T, R[t0:t1], C, s0, s1, E2)
        for t in range(T):
            Q[t] += U.T @ (R[:, t][:, None] * U)
        done += m
    for r in range(NR):
        C[r] /= n
        E2[r] = E2[r] * math.exp(LOG_DIM[r]) / (n * n_ax)
    S2 /= n
    b /= n
    Q /= n
    return C, S2, b, Q, E2


def psi(cB, cC, G):
    """Split-half cross product: exactly unbiased for the captured degree-n energy."""
    try:
        x = np.linalg.solve(G, cC)
        bad = False
    except np.linalg.LinAlgError:
        x = np.linalg.pinv(G, rcond=1e-10) @ cC
        bad = True
    return float(cB @ x), bad


def run_seed(seed):
    ss = np.random.SeedSequence(seed)
    s_net, s_pool, s_pilot, s_b, s_c = ss.spawn(5)
    gen = lambda s: np.random.Generator(np.random.PCG64DXSM(s))
    rng_net, rng_pool, rng_pilot, rng_b, rng_c = (gen(s_net), gen(s_pool), gen(s_pilot),
                                                  gen(s_b), gen(s_c))
    Ws, w_out = make_net(rng_net)

    # ---- pilot (independent): degree-0/1 control variates + pullback axes -------------
    Up = sample_sphere(rng_pilot, M_PILOT)
    Rp = forward_targets(Up, Ws, w_out)
    mu = Rp.mean(axis=0)
    B = Up.T @ (Rp - mu) / M_PILOT                # (D, T); degree-1 part = D * <B_t, u>
    ridge, Gt = ridge_and_pullback(Up[:M_GRAD], Ws, w_out)
    Ghat = Gt.T @ Gt / M_GRAD
    evals, evecs = np.linalg.eigh(Ghat)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    pull = evecs[:, :N_PULLBACK].T.copy()
    pull /= np.linalg.norm(pull, axis=1, keepdims=True)
    Gn = rng_pilot.standard_normal((M_GRAD, D))
    en = np.linalg.eigvalsh(Gn.T @ Gn / M_GRAD)[::-1]

    # ---- axis pools: own (W1 rows + pullback) vs matched-count random -----------------
    w1norm = np.linalg.norm(Ws[0], axis=1)
    W1n = Ws[0] / w1norm[:, None]
    A_own = np.vstack([W1n, pull])
    m_pool = len(A_own)
    pools = [A_own] + [sample_sphere(rng_pool, m_pool) for _ in range(N_RANDOM_POOLS)]
    A = np.vstack(pools)
    slices = [slice(i * m_pool, (i + 1) * m_pool) for i in range(len(pools))]
    Grams = [zonal_values(P @ P.T) for P in pools]        # Grams[pool][rung]
    gram_diag_err = max(float(np.abs(np.diag(G[r]) - 1.0).max())
                        for G in Grams for r in range(NR))
    gram_cond = {LADDER_DEG[r]: g6(max(float(np.linalg.cond(G[r])) for G in Grams))
                 for r in range(NR)}
    off = np.abs(A_own @ A_own.T - np.eye(m_pool))
    max_own_cos = float(off.max())

    # feature moments on the pilot sample (E[e^2] = 1 exactly; E[e^4] is the power tell)
    fv = zonal_values(Up[:min(M_PILOT, 4096)] @ A_own[:64].T)
    moments = {}
    for r, n in enumerate(LADDER_DEG):
        v2 = float(np.mean(fv[r] ** 2)) * math.exp(LOG_DIM[r])
        v4 = float(np.mean(fv[r] ** 4)) * math.exp(2.0 * LOG_DIM[r])
        moments[n] = {"mean_e2": g6(v2), "mean_e4": g6(v4),
                      "hermite_limit_e4_reference": g6(KURT_REF[r]),
                      "e4_reach": g6(v4 / KURT_REF[r])}

    cB, S2b, bB, Qb, E2b = half_pass(rng_b, Ws, w_out, A, mu, B, M_HALF)
    cC, S2c, bC, Qc, E2c = half_pass(rng_c, Ws, w_out, A, mu, B, M_HALF)
    reach = {LADDER_DEG[r]: g6(0.5 * (E2b[r] + E2c[r])) for r in range(NR)}

    r01 = 0.5 * (S2b + S2c)
    g1 = D * np.einsum("it,it->t", bB, bC)     # unbiased leftover degree-1 energy
    g2 = np.array([N2 * D * float((Qb[t] * Qc[t]).sum()) / (D - 1) for t in range(T)])
    den_raw = r01 - g1 - g2
    trust = den_raw >= DEN_FLOOR * r01
    den = np.where(trust, den_raw, r01)      # untrusted deg-2 subtraction -> conservative
    untrusted = [NAMES[i] for i in range(T) if not trust[i]]

    psis = np.zeros((NR, len(pools), T))
    any_bad = False
    for r in range(NR):
        for p, (sl, G) in enumerate(zip(slices, Grams)):
            for t in range(T):
                v, bad = psi(cB[r][sl, t], cC[r][sl, t], G[r])
                any_bad |= bad
                psis[r, p, t] = v

    surface = {}
    for t in range(T):
        surface[NAMES[t]] = {LADDER_DEG[r]: {
            "rho_own": r6(psis[r, 0, t] / den[t]),
            "rho_rand_floor": r6(psis[r, 1:, t].max() / den[t]),
        } for r in range(NR)}
    readout = {LADDER_DEG[r]: {
        "rho_own": r6(psis[r, 0, OUT_IDX] / den[OUT_IDX]),
        "psi_own_over_r01": r6(psis[r, 0, OUT_IDX] / r01[OUT_IDX]),
        "rho_rand": [r6(v / den[OUT_IDX]) for v in psis[r, 1:, OUT_IDX]],
        "rho_rand_floor": r6(psis[r, 1:, OUT_IDX].max() / den[OUT_IDX]),
    } for r in range(NR)}

    # ---- exact positive controls, per rung -------------------------------------------
    l1_check, l2_check = {}, {}
    for r, n in enumerate(LADDER_DEG):
        rows = []
        for j in range(NEURONS_PER_LAYER):
            ti = NAMES.index("L1_act_n%d" % j)
            pred = float(w1norm[j]) * LAMBDA[r]
            obs = 0.5 * (cB[r][j, ti] + cC[r][j, ti])
            rows.append({"neuron": j, "predicted": g6(pred), "observed": g6(obs),
                         "ratio": r6(obs / pred)})
        l1_check[n] = rows
        rows = []
        for j, ti in enumerate(L2_IDX):
            a = Ws[1][j] * w1norm * LAMBDA[r]
            pred = float(a @ (Grams[0][r][:WIDTH, :WIDTH] @ a))
            obs = float(psis[r, 0, ti])
            rows.append({"neuron": j, "predicted_psi": g6(pred), "observed_psi": g6(obs),
                         "ratio": r6(obs / pred)})
        l2_check[n] = rows

    return {
        "seed": int(seed),
        "readout_by_degree": readout,
        "surface": surface,
        "den_over_r01": {NAMES[t]: r6(den[t] / r01[t]) for t in range(T)},
        "r01_energy": {NAMES[t]: g6(r01[t]) for t in range(T)},
        "instrument": {
            "L1_own_axis_coefficient_check": l1_check,
            "L2_exact_span_energy_check": l2_check,
            "feature_moments": moments,
            "feature_reach_mean_e2_on_halves": reach,
            "gram_diagonal_max_error": g6(gram_diag_err),
            "gram_max_condition_by_degree": gram_cond,
            "gram_solve_fell_back_to_pinv": any_bad,
            "own_pool_max_offdiagonal_cosine": r6(max_own_cos),
            "deg2_subtraction_untrusted_targets": untrusted,
        },
        "ridge_collinearity": ridge,
        "pullback_spectrum": spec(evals),
        "pullback_spectrum_isotropic_null": spec(en),
        "axes_per_pool": int(m_pool),
    }


def main() -> None:
    started = time.perf_counter()
    per_seed = [run_seed(s) for s in SEEDS]
    cap = lambda x: min(2.0, max(0.0, x))

    per_degree, gating = {}, {}
    for n in LADDER_DEG:
        own = [s["readout_by_degree"][n]["rho_own"] for s in per_seed]
        flo = [s["readout_by_degree"][n]["rho_rand_floor"] for s in per_seed]
        rand = [v for s in per_seed for v in s["readout_by_degree"][n]["rho_rand"]]
        sd = float(np.std(rand, ddof=1)) if len(rand) > 1 else 0.0
        span = [x["ratio"] for s in per_seed for x in s["instrument"]
                ["L2_exact_span_energy_check"][n]]
        span_mean = float(np.mean(span))
        reach = float(np.mean([s["instrument"]["feature_reach_mean_e2_on_halves"][n]
                               for s in per_seed]))
        noise_ok = max(3.0 * sd, float(np.max(np.abs(rand)))) <= GATE_NOISE_BAR
        power_ok = GATE_SPAN_LO <= span_mean <= GATE_SPAN_HI
        reach_ok = reach >= GATE_REACH
        per_degree[n] = {
            "rho_own_mean": r6(float(np.mean(own))),
            "rho_own_per_seed": [r6(v) for v in own],
            "rho_rand_floor_mean": r6(float(np.mean(flo))),
            "rand_pool_values_all_seeds": [r6(v) for v in rand],
            "rand_pool_sd": r6(sd),
            "resolvable_rho_at_3sd": r6(3.0 * sd),
            "rand_pool_max_abs": r6(float(np.max(np.abs(rand)))),
            "own_over_floor": r6(float(np.mean(own)) / float(np.mean(flo)))
                              if float(np.mean(flo)) > 0 else None,
            "L2_span_ratio_mean": r6(span_mean),
            "feature_reach_mean_e2": r6(reach),
            "lambda_closed_form": g6(LAMBDA[RUNG_IDX[n]]),
            "dim_H_n": g6(float(DIMS[RUNG_IDX[n]])),
        }
        gating[n] = {"gated": bool(noise_ok and power_ok and reach_ok),
                     "noise_ok": bool(noise_ok), "power_ok": bool(power_ok),
                     "reach_ok": bool(reach_ok), "feature_reach": r6(reach),
                     "reach_bar": GATE_REACH,
                     "noise_statistic": r6(max(3.0 * sd, float(np.max(np.abs(rand))))),
                     "noise_bar": r6(GATE_NOISE_BAR),
                     "span_recovery": r6(span_mean)}

    gated = [n for n in LADDER_DEG if gating[n]["gated"]]
    not_gated = [n for n in LADDER_DEG if not gating[n]["gated"]]
    own_sum = sum(per_degree[n]["rho_own_mean"] for n in gated)
    floor_sum = sum(per_degree[n]["rho_rand_floor_mean"] for n in gated)
    own_sum_all = sum(per_degree[n]["rho_own_mean"] for n in LADDER_DEG)
    binding = max(floor_sum, R2_BAR)
    metric = 2.0 if own_sum <= 0.0 else cap(binding / own_sum)
    leg_structural = 2.0 if own_sum <= 0.0 else cap(floor_sum / own_sum)
    leg_material = 2.0 if own_sum <= 0.0 else cap(R2_BAR / own_sum)
    anchor_gated = 6 in gated

    surface = {nm: {n: {
        "rho_own_mean": r6(float(np.mean([s["surface"][nm][n]["rho_own"] for s in per_seed]))),
        "rho_own_per_seed": [r6(s["surface"][nm][n]["rho_own"]) for s in per_seed],
        "rho_rand_floor_mean": r6(float(np.mean([s["surface"][nm][n]["rho_rand_floor"]
                                                 for s in per_seed]))),
    } for n in LADDER_DEG} for nm in NAMES}

    ridge = {nm: {k: r6(float(np.mean([s["ridge_collinearity"][nm][k] for s in per_seed])))
                  for k in ("top1_share", "top8_share", "participation_ratio")}
             for nm in NAMES}
    l1r = {n: r6(float(np.mean([x["ratio"] for s in per_seed
                                for x in s["instrument"]["L1_own_axis_coefficient_check"][n]])))
           for n in LADDER_DEG}
    fm = {n: {k: g6(float(np.mean([s["instrument"]["feature_moments"][n][k]
                                   for s in per_seed])))
              for k in ("mean_e2", "mean_e4", "hermite_limit_e4_reference", "e4_reach")}
          for n in LADDER_DEG}

    print(json.dumps({
        "cell": "deg_ladder_own_axis_capture",
        "smoke": SMOKE,
        METRIC_NAME: r6(metric),
        "instrument_failure_not_a_kill": (not anchor_gated),
        "metric_semantics": (
            "max(summed matched-count random-axis floor over the GATED rungs, predeclared "
            "materiality bar R2_BAR) divided by the summed own-axis captured energy over the "
            "same gated rungs, every capture expressed as a fraction of the SAME "
            "degree-3-and-above residual energy of the depth-32 readout so that distinct "
            "harmonic degrees, being exactly orthogonal, add; LOW means the own-axis zonal "
            "family across the measured degree band both beats the random floor and clears "
            "the materiality bar, HIGH means it does neither"),
        "leg_structural_floor_over_own": r6(leg_structural),
        "leg_material_bar_over_own": r6(leg_material),
        "cumulative": {
            "gated_rungs": gated,
            "reported_not_gated_rungs": not_gated,
            "own_sum_gated": r6(own_sum),
            "floor_sum_gated": r6(floor_sum),
            "own_sum_all_rungs": r6(own_sum_all),
            "binding_requirement": r6(binding),
            "r2_bar": R2_BAR,
            "own_over_floor_cumulative": r6(own_sum / floor_sum) if floor_sum > 0 else None,
            "v1_anchor_rho_own_deg6": per_degree[6]["rho_own_mean"],
            "v1_reported_rho_own_deg6": 0.001872,
        },
        "gating": {
            "rule": ("a rung enters the metric only if ALL THREE hold: (a) its measured "
                     "readout noise max(3 sd, max abs) over the 6 x seeds random-pool draws "
                     "is at most R2_BAR / n_rungs; (b) the instrument recovers the EXACT "
                     "in-span degree-n energy of the second-layer preactivation to within a "
                     "factor of two; (c) the sampled mean of the zonal feature square, whose "
                     "true value is EXACTLY 1, reaches at least half of it, so the rung is "
                     "not being read through an unsampled tail. The own-axis readout capture "
                     "is never consulted, so the gate cannot select on the answer"),
            "noise_bar": r6(GATE_NOISE_BAR),
            "span_band": [GATE_SPAN_LO, GATE_SPAN_HI],
            "reach_bar": GATE_REACH,
            "per_rung": gating,
            "anchor_rung_6_gated": anchor_gated,
            "anchor_note": ("v1 resolved degree 6 at 10.2x its floor with the same sample "
                            "count; if anchor_rung_6_gated is false the run is an INSTRUMENT "
                            "FAILURE and must not be recorded as a KILL"),
        },
        "per_degree_readout": per_degree,
        "degree_by_depth_surface": surface,
        "ridge_collinearity": ridge,
        "ridge_collinearity_note": (
            "raw input-gradient second-moment spectra; a function exactly zonal about one "
            "axis has a gradient collinear with that axis everywhere, so top1_share is "
            "EXACTLY 1 at layer 1 and its decay with depth measures, independently of all "
            "harmonic machinery, how far the deep kink surfaces have bent away from great "
            "spheres about any fixed input-space axis"),
        "instrument_pooled": {
            "L1_own_axis_ratio_by_degree": l1r,
            "L2_exact_span_ratio_by_degree": {n: per_degree[n]["L2_span_ratio_mean"]
                                              for n in LADDER_DEG},
            "feature_moments_by_degree": fm,
            "feature_reach_by_degree": {n: per_degree[n]["feature_reach_mean_e2"]
                                        for n in LADDER_DEG},
            "L1_ratio_note": ("heavy-tailed: the degree-n zonal fourth moment grows steeply "
                              "with n, so per-neuron ratios are noise dominated and only the "
                              "pooled mean is a usable check"),
        },
        "pullback_spectrum": {k: r6(float(np.mean([s["pullback_spectrum"][k]
                                                   for s in per_seed])))
                              for k in ("top1_share", "top8_share", "participation_ratio")},
        "pullback_spectrum_isotropic_null": {
            k: r6(float(np.mean([s["pullback_spectrum_isotropic_null"][k]
                                 for s in per_seed])))
            for k in ("top1_share", "top8_share", "participation_ratio")},
        "per_seed": per_seed,
        "geometry": {
            "degrees": list(LADDER_DEG),
            "dim_H_n": {n: g6(float(DIMS[RUNG_IDX[n]])) for n in LADDER_DEG},
            "dim_H_2": N2,
            "lambda_closed_form": {n: g6(LAMBDA[RUNG_IDX[n]]) for n in LADDER_DEG},
            "P_n_at_one": {n: float("%.17g" % P_AT_ONE[n]) for n in LADDER_DEG},
            "recurrence_vs_exact_rational_max_rel_error": {n: g6(REC_ERR[n])
                                                           for n in LADDER_DEG},
        },
        "config": {"d": D, "width": WIDTH, "depth": DEPTH, "m_pilot": M_PILOT,
                   "m_half": M_HALF, "m_grad": M_GRAD, "n_random_pools": N_RANDOM_POOLS,
                   "n_pullback": N_PULLBACK, "n_targets": T, "degrees": list(LADDER_DEG),
                   "axis_block": AXIS_BLOCK, "samp_tile": SAMP_TILE,
                   "seeds": list(SEEDS)},
        "wall_seconds": r6(time.perf_counter() - started),
    }))


if __name__ == "__main__":
    main()
