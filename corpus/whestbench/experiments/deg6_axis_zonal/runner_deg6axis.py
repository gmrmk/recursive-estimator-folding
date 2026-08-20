"""deg6_own_axis_zonal_capture -- does a deep network's degree-6 energy live on its OWN axes?

Splices two recorded kills.  m191/S15 measured the harmonic ceiling along a FIXED tractable
basis and found the residual dispersed; m107 built exact-zero Gegenbauer controls over W1
axes and died of FITTED-coefficient transport, not of absent energy.  Neither measured the
network-ADAPTIVE zonal basis at degree six.  This cell measures it.

Entry-layer neuron functions relu(w_i . u) are EXACTLY zonal about w_i-hat, and every
second-layer preactivation, being a linear combination of entry-layer ridge functions, lies
exactly inside the span of those zonal functions -- two exact positive controls the run must
reproduce.  The question is how much of that concentration survives thirty-two layers of
composition, measured against matched-count random axis pools on the identical samples.

Diagnostic only; synthetic seeded He nets; no truth, holdout, scorer or submission artifact
is read; zero charge against H.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

D = 256
WIDTH = 256
DEPTH = 32
DEG = 6
N_PULLBACK = 8
N_RANDOM_POOLS = 6
LADDER = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
NEURONS_PER_LAYER = 2
R2_BAR = 0.02                       # predeclared materiality bar, in R^2-of-deg>=3 units
DEN_FLOOR = 0.02                    # below this share the deg-2 subtraction is untrusted
AXIS_BLOCK = 512
METRIC_NAME = "deg6_own_axis_capture_shortfall"

SMOKE = os.environ.get("DEG6AXIS_SMOKE") == "1"
SEEDS = (778001311,) if SMOKE else (20260901, 20260902, 20260903)
M_PILOT = 2048 if SMOKE else 16384
M_HALF = 8192 if SMOKE else 131072
M_GRAD = 512 if SMOKE else 4096
CHUNK = 4096 if SMOKE else 16384


def r6(x) -> float:
    return float(np.round(float(x), 6))


def sph_dim(n: int, d: int) -> int:
    """dim H_n(S^{d-1}) = C(n+d-1, n) - C(n+d-3, n-2)."""
    return math.comb(n + d - 1, n) - (math.comb(n + d - 3, n - 2) if n >= 2 else 0)


def gegenbauer_coeffs(n: int, d: int) -> np.ndarray:
    """Ascending-power coefficients of the NORMALIZED Gegenbauer P_n with P_n(1) = 1, from
    the exact three-term recurrence

        (n+d-3) P_n(t) = (2n+d-4) t P_{n-1}(t) - (n-1) P_{n-2}(t),  P_0 = 1, P_1 = t.

    Addition theorem under unit-mass surface measure: sum_k Y_{n,k}(u) Y_{n,k}(v) =
    N(d,n) P_n(<u,v>), hence <P_n(<.,a>), P_n(<.,b>)> = P_n(<a,b>) / N(d,n).  The unit-norm
    zonal is therefore e_a = sqrt(N(d,n)) P_n(<.,a>), with <e_a, e_b> = P_n(<a,b>).
    """
    p0 = np.zeros(n + 1)
    p0[0] = 1.0
    if n == 0:
        return p0
    p1 = np.zeros(n + 1)
    p1[1] = 1.0
    for k in range(2, n + 1):
        p2 = np.zeros(n + 1)
        p2[1:] += (2 * k + d - 4) * p1[:-1]
        p2 -= (k - 1) * p0
        p2 /= (k + d - 3)
        p0, p1 = p1, p2
    return p1


N6 = sph_dim(DEG, D)
N2 = sph_dim(2, D)
COEF = gegenbauer_coeffs(DEG, D)
SQRT_N6 = math.sqrt(N6)
EVEN = COEF[::2].copy()             # DEG even: powers 0,2,4,6 in s = t^2


def p_deg(t: np.ndarray) -> np.ndarray:
    """P_DEG(t) by Horner in s = t^2 (equal to the recurrence to 1e-15 on [-1,1])."""
    s = t * t
    out = np.full_like(s, EVEN[-1])
    for c in EVEN[-2::-1]:
        out *= s
        out += c
    return out


def abs_moment(m: int, d: int) -> float:
    """E|<u,a>|^m for u uniform on S^{d-1} (t^2 ~ Beta(1/2, (d-1)/2))."""
    return math.exp(math.lgamma((m + 1) / 2) + math.lgamma(d / 2)
                    - math.lgamma(0.5) - math.lgamma((m + d) / 2))


def relu_lambda(d: int) -> float:
    """<relu(<.,a>), e_a> in closed form: relu(t) = (t+|t|)/2 and <t, P_DEG> = 0."""
    return SQRT_N6 * 0.5 * sum(COEF[j] * abs_moment(j + 1, d) for j in range(DEG + 1))


LAMBDA6 = relu_lambda(D)


def _horner_vs_recurrence() -> float:
    t = np.linspace(-1.0, 1.0, 20001)
    p0, p1 = np.ones_like(t), t.copy()
    for k in range(2, DEG + 1):
        p0, p1 = p1, ((2 * k + D - 4) * t * p1 - (k - 1) * p0) / (k + D - 3)
    return float(np.abs(p_deg(t) - p1).max())


HORNER_ERR = _horner_vs_recurrence()
assert HORNER_ERR < 1e-12, "Gegenbauer Horner form disagrees with the recurrence"
assert abs(float(COEF.sum()) - 1.0) < 1e-12, "P_DEG(1) != 1"


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


def out_tangential_grad(U, Ws, w_out):
    """d f_out/du with the radial part removed (f is 1-homogeneous, so u.grad f = f)."""
    masks, H = [], U
    for W in Ws:
        Z = H @ W.T
        m = Z > 0
        masks.append(m)
        H = np.where(m, Z, 0.0)
    f = H @ w_out
    G = np.repeat(w_out[None, :], len(U), axis=0)
    for l in range(DEPTH - 1, -1, -1):
        G = np.where(masks[l], G, 0.0) @ Ws[l]
    return G - f[:, None] * U


def zonal_block(U, A):
    """Unit-L2-norm zonal features e_a(u) = sqrt(N(d,DEG)) P_DEG(<u,a>)."""
    return SQRT_N6 * p_deg(U @ A.T)


def half_pass(rng, Ws, w_out, A, mu, B, n):
    """One independent half.  Returns (zonal coefficients (n_axes, T), mean r^2 (T,),
    degree-1 accumulator b (D, T), degree-2 accumulator Q (T, D, D))."""
    n_ax = len(A)
    C = np.zeros((n_ax, T))
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
        for s in range(0, n_ax, AXIS_BLOCK):
            E = zonal_block(U, A[s:s + AXIS_BLOCK])
            C[s:s + AXIS_BLOCK] += E.T @ R
        for t in range(T):
            Q[t] += U.T @ (R[:, t][:, None] * U)
        done += m
    C /= n
    S2 /= n
    b /= n
    Q /= n
    return C, S2, b, Q


def psi(cB, cC, G):
    """Split-half cross product: exactly unbiased for the captured degree-DEG energy."""
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
    Gt = out_tangential_grad(Up[:M_GRAD], Ws, w_out)
    Ghat = Gt.T @ Gt / M_GRAD
    evals, evecs = np.linalg.eigh(Ghat)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    pull = evecs[:, :N_PULLBACK].T.copy()
    pull /= np.linalg.norm(pull, axis=1, keepdims=True)
    Gn = rng_pilot.standard_normal((M_GRAD, D))
    en = np.linalg.eigvalsh(Gn.T @ Gn / M_GRAD)[::-1]

    def spec(ev):
        return {"top1_share": r6(ev[0] / ev.sum()),
                "top8_share": r6(ev[:N_PULLBACK].sum() / ev.sum()),
                "participation_ratio": r6(float(ev.sum() ** 2 / (ev ** 2).sum()))}

    # ---- axis pools: own (W1 rows + pullback) vs matched-count random -----------------
    W1n = Ws[0] / np.linalg.norm(Ws[0], axis=1, keepdims=True)
    A_own = np.vstack([W1n, pull])
    m_pool = len(A_own)
    pools = [A_own] + [sample_sphere(rng_pool, m_pool) for _ in range(N_RANDOM_POOLS)]
    A = np.vstack(pools)
    slices = [slice(i * m_pool, (i + 1) * m_pool) for i in range(len(pools))]
    Grams = [p_deg(P @ P.T) for P in pools]
    gram_diag_err = max(float(np.abs(np.diag(G) - 1.0).max()) for G in Grams)
    gram_cond = max(float(np.linalg.cond(G)) for G in Grams)

    cB, S2b, bB, Qb = half_pass(rng_b, Ws, w_out, A, mu, B, M_HALF)
    cC, S2c, bC, Qc = half_pass(rng_c, Ws, w_out, A, mu, B, M_HALF)

    r01 = 0.5 * (S2b + S2c)
    g1 = D * np.einsum("it,it->t", bB, bC)     # unbiased leftover degree-1 energy
    g2 = np.array([N2 * D * float((Qb[t] * Qc[t]).sum()) / (D - 1) for t in range(T)])
    den_raw = r01 - g1 - g2
    trust = den_raw >= DEN_FLOOR * r01
    den = np.where(trust, den_raw, r01)      # untrusted deg-2 subtraction -> conservative
    untrusted = [NAMES[i] for i in range(T) if not trust[i]]

    rows, any_bad = {}, False
    for t in range(T):
        vals = []
        for sl, G in zip(slices, Grams):
            v, bad = psi(cB[sl, t], cC[sl, t], G)
            any_bad |= bad
            vals.append(v)
        rows[NAMES[t]] = {
            "rho_own": r6(vals[0] / den[t]),
            "psi_own_over_r01": r6(vals[0] / r01[t]),
            "rho_rand": [r6(v / den[t]) for v in vals[1:]],
            "rho_rand_floor": r6(max(vals[1:]) / den[t]),
            "r01_energy": float("%.6g" % r01[t]),
            "deg1_leftover_share_of_r01": r6(g1[t] / r01[t]),
            "deg2_share_of_r01": r6(g2[t] / r01[t]),
        }

    lam_obs = []
    for j in range(NEURONS_PER_LAYER):
        ti = NAMES.index("L1_act_n%d" % j)
        pred = float(np.linalg.norm(Ws[0][j])) * LAMBDA6
        obs = 0.5 * (cB[j, ti] + cC[j, ti])
        lam_obs.append({"neuron": j, "predicted": float("%.6g" % pred),
                        "observed": float("%.6g" % obs), "ratio": r6(obs / pred)})
    lam_ratio_mean = r6(float(np.mean([x["ratio"] for x in lam_obs])))

    return {
        "seed": int(seed),
        "targets": rows,
        "instrument": {
            "lambda6_closed_form": float("%.6g" % LAMBDA6),
            "L1_own_axis_coefficient_check": lam_obs,
            "L1_ratio_mean_this_seed": lam_ratio_mean,
            "gram_diagonal_max_error": float("%.3g" % gram_diag_err),
            "gram_max_condition": float("%.6g" % gram_cond),
            "gram_solve_fell_back_to_pinv": any_bad,
            "deg2_subtraction_untrusted_targets": untrusted,
        },
        "pullback_spectrum": spec(evals),
        "pullback_spectrum_isotropic_null": spec(en),
        "feature_norm_check_mean_e2": r6(float((zonal_block(Up, A_own[:64]) ** 2).mean())),
        "axes_per_pool": int(m_pool),
    }


def main() -> None:
    started = time.perf_counter()
    per_seed = [run_seed(s) for s in SEEDS]

    own = [s["targets"]["OUT"]["rho_own"] for s in per_seed]
    flo = [s["targets"]["OUT"]["rho_rand_floor"] for s in per_seed]
    rho_own = float(np.mean(own))
    floor = float(np.mean(flo))
    binding = max(floor, R2_BAR)
    cap = lambda x: min(2.0, max(0.0, x))
    metric = 2.0 if rho_own <= 0.0 else cap(binding / rho_own)
    leg_structural = 2.0 if rho_own <= 0.0 else cap(floor / rho_own)
    leg_material = 2.0 if rho_own <= 0.0 else cap(R2_BAR / rho_own)

    all_rand = [v for s in per_seed for v in s["targets"]["OUT"]["rho_rand"]]
    l1r = [x["ratio"] for s in per_seed for x in s["instrument"]["L1_own_axis_coefficient_check"]]
    sd = float(np.std(all_rand, ddof=1)) if len(all_rand) > 1 else 0.0
    ladder = {nm: {
        "rho_own_mean": r6(float(np.mean([s["targets"][nm]["rho_own"] for s in per_seed]))),
        "psi_own_over_r01_mean": r6(float(np.mean([s["targets"][nm]["psi_own_over_r01"]
                                                   for s in per_seed]))),
        "rho_rand_floor_mean": r6(float(np.mean([s["targets"][nm]["rho_rand_floor"]
                                                 for s in per_seed]))),
    } for nm in NAMES}

    print(json.dumps({
        "cell": "deg6_own_axis_zonal_capture",
        "smoke": SMOKE,
        METRIC_NAME: r6(metric),
        "metric_semantics": (
            "max(measured matched-count random-axis floor, predeclared materiality bar "
            "R2_BAR) divided by the own-axis captured degree-6 energy, both expressed as a "
            "fraction of the degree-3-and-above residual energy of the depth-32 readout; LOW "
            "means the own-axis zonal family both beats the random floor and clears the "
            "materiality bar, HIGH means it does neither"),
        "leg_structural_floor_over_own": r6(leg_structural),
        "leg_material_bar_over_own": r6(leg_material),
        "own_over_floor": r6(rho_own / floor) if floor > 0 else None,
        "rho_own_pooled": r6(rho_own),
        "rho_rand_floor_pooled": r6(floor),
        "binding_requirement": r6(binding),
        "r2_bar": R2_BAR,
        "mc_noise_floor": {
            "rand_pool_values_all_seeds": [r6(v) for v in all_rand],
            "rand_pool_mean": r6(float(np.mean(all_rand))),
            "rand_pool_sd": r6(sd),
            "rand_pool_max": r6(float(np.max(all_rand))),
            "per_seed_own": [r6(v) for v in own],
            "per_seed_floor": [r6(v) for v in flo],
            "resolvable_rho_at_3sd": r6(3.0 * sd),
        },
        "instrument_pooled": {
            "L1_own_axis_ratio_mean": r6(float(np.mean(l1r))),
            "L1_own_axis_ratio_sd": r6(float(np.std(l1r, ddof=1))) if len(l1r) > 1 else 0.0,
            "L1_own_axis_ratio_note": ("heavy-tailed: the degree-6 zonal has kurtosis of order "
                                       "two ten-thousands, so the per-neuron ratio is noise "
                                       "dominated; only the pooled mean is a usable check"),
        },
        "depth_ladder": ladder,
        "per_seed": per_seed,
        "geometry": {"deg": DEG, "dim_H_deg": N6, "dim_H_2": N2,
                     "gegenbauer_coeffs_ascending": [float("%.10g" % c) for c in COEF],
                     "P_deg_at_one": float("%.17g" % float(COEF.sum())),
                     "horner_vs_recurrence_max_error": float("%.3g" % HORNER_ERR)},
        "config": {"d": D, "width": WIDTH, "depth": DEPTH, "m_pilot": M_PILOT,
                   "m_half": M_HALF, "m_grad": M_GRAD, "n_random_pools": N_RANDOM_POOLS,
                   "n_pullback": N_PULLBACK, "n_targets": T, "seeds": list(SEEDS)},
        "wall_seconds": r6(time.perf_counter() - started),
    }))


if __name__ == "__main__":
    main()
