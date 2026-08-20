"""S6 (ledger id s6_bloch_design_bragg_spectrum): Bragg spectrum of the Kerdock
design's degree-4 quadrature-error operator.

QUESTION: is the design operator's deviation from I/dim on H_4 LOW-RANK
(failure concentrated on few "Bragg" modes)?

NORMALIZATION (stated once, used everywhere):
  H_ell = spherical harmonics of degree ell on S^{d-1}, d=256, dim m_ell.
  Reproducing kernel  Z_ell(x,y) = m_ell * G_ell(<x,y>),
  G_ell(t) = C_ell^{(alpha)}(t) / C_ell^{(alpha)}(1),  alpha = (d-2)/2 = 127.
  phi(x) = Z_ell(x,.) / sqrt(m_ell)  =>  ||phi(x)|| = 1,
  <phi(x), phi(y)> = G_ell(<x,y>).
  A = (1/N) sum_j phi(x_j) phi(x_j)^T  on H_ell;  tr(A) = 1 exactly.
  Nonzero spectrum of A = spectrum of the N x N Gram  G = K/N,
  K_jk = G_ell(<x_j, x_k>).
  D = A - I/m;  tr(D^2) = tr(A^2) - 1/m;
  tr(A^2) = (1/N^2) sum_{j,k} G_ell(<x_j,x_k>)^2   (exact pairwise sum).
  spec(D) = { lam_i(G) - 1/m  (design span, N values) }
            union { -1/m with multiplicity m - N }.

DESIGN CHOICE (predeclared option): the UNROTATED 32,256-point base set with
even-degree kernels.  For even ell, phi(-x) = phi(x), so the antipodally
doubled 64,512-point set produces the IDENTICAL operator A (each term
duplicated, N doubled): same spectrum, same tr(D^2).  Rotations conjugate A
by an orthogonal map and leave the spectrum invariant, so the unrotated set
is fully general.

GATES (predeclared): PASS if top-100 eigenvalues of D carry >= 50% of
tr(D^2) (sum of eigenvalue^2); KILL if < 5%; else INCONCLUSIVE.

TWO-SIGNAL DESIGN:
  (1) exact rational (Fraction) closed-form spectrum derived from the
      bitwise-exact inner-product fingerprint (unit entries are exactly
      +-1/16, so all pairwise inner products are exact multiples of 1/256 in
      f64), cross-checked against the exact pairwise-sum tr(D^2);
  (2) structure-agnostic dense eigensolve on a uniformly-subsampled 16,000-
      direction Gram (predeclared fallback path for the top spectrum).

FIREWALL: frozen n8a source imported read-only; writes confined to this
directory; no git; synthetic/deterministic inputs only.
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N8A = HERE.parent / "n8a_rqmc_kerdock"
PB1 = HERE.parent / "pb1_premise_battery"
sys.path.insert(0, str(N8A))
from run_n8a_gates import load_kerdock_directions, MEAN_CHI_256  # noqa: E402

D = 256
N = 126 * 256                      # 32,256 base directions (see docstring)
N_DOUBLED = 2 * N                  # M191's antipodal count (for iid scale)
ALPHA = Fraction(D - 2, 2)         # 127
BLOCK = 1024
SUB_N = 16000                      # predeclared 12,000-16,000 window
SUB_SEED = 20260809
M191_NPOLY = 200
M191_SEED = 424242


# ------------------------------------------------------------ exact algebra
def gegenbauer_coeffs(ell: int, a: Fraction) -> list[Fraction]:
    """Coefficients c[k] of t^k in C_ell^{(a)}(t), exact rationals.
    Recurrence: n C_n = 2t(n-1+a) C_{n-1} - (n-2+2a) C_{n-2}."""
    c_prev = [Fraction(1)]
    if ell == 0:
        return c_prev
    c_curr = [Fraction(0), 2 * a]
    for n in range(2, ell + 1):
        c_next = [Fraction(0)] * (n + 1)
        for k, v in enumerate(c_curr):
            c_next[k + 1] += 2 * (n - 1 + a) * v
        for k, v in enumerate(c_prev):
            c_next[k] -= (n - 2 + 2 * a) * v
        c_next = [v / n for v in c_next]
        c_prev, c_curr = c_curr, c_next
    return c_curr


def dim_H(ell: int) -> int:
    """dim H_ell(S^{d-1}) two ways; assert agreement (two-signal on m_ell)."""
    a = Fraction(2 * ell + D - 2, ell) * math.comb(ell + D - 3, ell - 1)
    assert a.denominator == 1
    b = math.comb(D + ell - 1, ell) - math.comb(D + ell - 3, ell - 2)
    assert int(a) == b, (a, b)
    return b


def even_moment(two_k: int) -> Fraction:
    """E[t^{2k}] for t = <e,u>, u uniform on S^{d-1}:
    (2k-1)!! / (d (d+2) ... (d+2k-2)), exact."""
    k = two_k // 2
    num = 1
    for i in range(1, 2 * k, 2):
        num *= i
    den = 1
    for i in range(k):
        den *= D + 2 * i
    return Fraction(num, den)


def zonal_moment(coeffs: list[Fraction], extra_power: int = 0) -> Fraction:
    """E[t^extra_power * sum_k c_k t^k] under the single-coordinate law
    (odd moments vanish)."""
    total = Fraction(0)
    for k, c in enumerate(coeffs):
        p = k + extra_power
        if p % 2 == 0:
            total += c * even_moment(p)
    return total


def g_of(coeffs: list[Fraction], c1: Fraction, t: Fraction) -> Fraction:
    """G_ell(t) = C_ell(t)/C_ell(1), exact."""
    acc = Fraction(0)
    for k in reversed(range(len(coeffs))):
        acc = acc * t + coeffs[k]
    return acc / c1


def exact_constants() -> dict:
    out = {}
    for ell in (4, 6):
        coeffs = gegenbauer_coeffs(ell, ALPHA)
        c1 = sum(coeffs)                       # C_ell(1)
        m = dim_H(ell)
        # exact identity checks: E[G_ell] = 0 and m_ell * E[G_ell^2] = 1
        assert zonal_moment(coeffs) == 0, f"E[G_{ell}] != 0"
        gg = [Fraction(0)] * (2 * ell + 1)     # coefficients of C_ell^2
        for i, a in enumerate(coeffs):
            for j, b in enumerate(coeffs):
                gg[i + j] += a * b
        assert m * zonal_moment(gg) == c1 * c1, f"m_{ell} * E[G^2] != 1"
        g0 = g_of(coeffs, c1, Fraction(0))
        g1 = g_of(coeffs, c1, Fraction(1, 16))   # G_ell(+-1/16), even kernel
        out[ell] = {
            "coeffs": coeffs, "c1": c1, "m": m, "g0": g0, "g1": g1,
        }
    # hand-check anchor for ell=4, alpha=127 (derived independently):
    assert out[4]["coeffs"] == [Fraction(8128), Fraction(0),
                                Fraction(-4194048), Fraction(0),
                                Fraction(181742080)]
    assert out[4]["c1"] == 177556160
    assert out[4]["m"] == 183148480
    return out


# ------------------------------------------------------- exact pairwise pass
def load_unit_directions() -> np.ndarray:
    """Unrotated base design as EXACT dyadic unit vectors (entries +-1/16)."""
    x = load_kerdock_directions().astype(np.float64) / MEAN_CHI_256
    snapped = np.rint(x * 16.0)
    snap_dev = float(np.abs(x * 16.0 - snapped).max())
    assert snap_dev < 1e-5, snap_dev
    assert np.all(np.abs(snapped) == 1.0)      # every entry +-1/16
    u = snapped / 16.0
    norms2 = np.einsum("ij,ij->i", u, u)
    assert np.all(norms2 == 1.0)               # exact in f64 (dyadic)
    return u


def pairwise_pass(u: np.ndarray, consts: dict) -> dict:
    """One chunked pass over all N^2 ordered pairs: exact inner-product
    fingerprint (values are exact multiples of 1/256 -> integer bincount)
    plus f64 accumulation of S1_ell = sum G_ell(t), S2_ell = sum G_ell(t)^2
    for ell = 4, 6."""
    frame = np.arange(N) // 256
    c4 = [float(c / consts[4]["c1"]) for c in consts[4]["coeffs"]]
    c6 = [float(c / consts[6]["c1"]) for c in consts[6]["coeffs"]]
    # even polynomials in v = t^2
    p4 = (c4[0], c4[2], c4[4])                 # c0 + c2 v + c4 v^2
    p6 = (c6[0], c6[2], c6[4], c6[6])
    counts = np.zeros(513, dtype=np.int64)     # k = 256*t + 256 in [0,512]
    counts_within = np.zeros(513, dtype=np.int64)
    s1_4 = s2_4 = s1_6 = s2_6 = 0.0
    max_grid_dev = 0.0
    diag_ok = True
    t0 = time.perf_counter()
    for i0 in range(0, N, BLOCK):
        i1 = min(i0 + BLOCK, N)
        t = u[i0:i1] @ u.T                     # exact dyadic values in f64
        k256 = t * 256.0
        r = np.rint(k256)
        max_grid_dev = max(max_grid_dev, float(np.abs(k256 - r).max()))
        idx = (r + 256.0).astype(np.int64)
        counts += np.bincount(idx.ravel(), minlength=513)
        wf = frame[i0:i1, None] == frame[None, :]
        counts_within += np.bincount(idx[wf], minlength=513)
        rows = np.arange(i0, i1)
        if not np.all(r[rows - i0, rows] == 256.0):
            diag_ok = False
        v = t * t
        g4v = (p4[2] * v + p4[1]) * v + p4[0]
        s1_4 += float(g4v.sum())
        s2_4 += float(np.dot(g4v.ravel(), g4v.ravel()))
        g6v = ((p6[3] * v + p6[2]) * v + p6[1]) * v + p6[0]
        s1_6 += float(g6v.sum())
        s2_6 += float(np.dot(g6v.ravel(), g6v.ravel()))
        if (i0 // BLOCK) % 8 == 0:
            print(f"  pass block {i0:>6}/{N}  ({time.perf_counter()-t0:5.1f}s)",
                  flush=True)
    return {
        "counts": counts, "counts_within": counts_within,
        "S1_4": s1_4, "S2_4": s2_4, "S1_6": s1_6, "S2_6": s2_6,
        "max_grid_dev": max_grid_dev, "diag_ok": diag_ok,
        "wall_s": time.perf_counter() - t0,
    }


# ------------------------------------------------------ closed-form spectrum
def closed_form(ell: int, consts: dict) -> dict:
    """Given the VERIFIED structure (within-frame off-diag t=0, cross-frame
    t=+-1/16), K = (1-g0) I + (g0-g1) F F^T + g1 11^T with F the frame
    indicator matrix, so G=K/N has exactly three eigenvalue shells."""
    g0, g1, m = consts[ell]["g0"], consts[ell]["g1"], consts[ell]["m"]
    lam_bulk = (1 - g0) / N                          # mult N - 126
    lam_mid = (1 - g0 + 256 * (g0 - g1)) / N         # mult 125
    lam_top = (1 - g0 + 256 * (g0 - g1) + N * g1) / N  # mult 1
    inv_m = Fraction(1, m)
    tr_a2 = (N * 1 + N * 255 * g0 * g0 + N * 32000 * g1 * g1) / (N * N)
    tr_d2 = tr_a2 - inv_m
    # independent trace identities (exact rationals)
    assert 125 * lam_mid + (N - 126) * lam_bulk + lam_top == 1
    assert (125 * lam_mid ** 2 + (N - 126) * lam_bulk ** 2
            + lam_top ** 2) == tr_a2
    mu_bulk, mu_mid, mu_top = (lam_bulk - inv_m, lam_mid - inv_m,
                               lam_top - inv_m)
    tr_d2_shells = (125 * mu_mid ** 2 + (N - 126) * mu_bulk ** 2
                    + mu_top ** 2 + (m - N) * inv_m ** 2)
    assert tr_d2_shells == tr_d2
    # shells of D sorted by |eigenvalue| descending (generic: the ordering
    # differs between ell=4 and ell=6)
    shells = sorted(
        [(mu_mid, 125), (mu_bulk, N - 126), (mu_top, 1), (-inv_m, m - N)],
        key=lambda s: abs(s[0]), reverse=True)
    tops = {}
    top20 = []
    for k in (1, 10, 100, 1000):
        s = Fraction(0)
        left = k
        for mu, mult in shells:
            take = min(left, mult)
            s += take * mu ** 2
            left -= take
            if left == 0:
                break
        tops[k] = float(s / tr_d2)
    for mu, mult in shells:
        top20 += [float(mu)] * min(mult, 20 - len(top20))
        if len(top20) >= 20:
            break
    tr_d4 = (125 * mu_mid ** 4 + (N - 126) * mu_bulk ** 4 + mu_top ** 4
             + (m - N) * inv_m ** 4)
    return {
        "lam_bulk": float(lam_bulk), "lam_mid": float(lam_mid),
        "lam_top": float(lam_top),
        "mult": {"bulk": N - 126, "mid": 125, "top": 1,
                 "minus_inv_m": m - N},
        "mu_bulk": float(mu_bulk), "mu_mid": float(mu_mid),
        "mu_top": float(mu_top), "inv_m": float(inv_m),
        "tr_A2": float(tr_a2), "tr_D2": float(tr_d2),
        "topk_frac": tops,
        "top20_eigs_D": top20,
        "participation_rank": float(tr_d2 ** 2 / tr_d4),
        "S1_pred": float((N + N * 255 * g0 + N * 32000 * g1)),  # sum G(t)
    }


# --------------------------------------------------------- subsample eigh arm
def subsample_arm(u: np.ndarray, consts: dict) -> dict:
    rng = np.random.default_rng(SUB_SEED)
    idx = np.sort(rng.choice(N, size=SUB_N, replace=False))
    frame = idx // 256
    n_f = np.bincount(frame, minlength=126)
    us = u[idx].astype(np.float32)             # entries +-1/16 exact in f32
    t0 = time.perf_counter()
    ks = us @ us.T                             # exact multiples of 1/256
    c1 = consts[4]["c1"]
    p = [float(c / c1) for c in consts[4]["coeffs"]]
    # in-place kernel eval (memory budget): ks -> v = t^2; w = (p4 v + p2) v + p0
    np.square(ks, out=ks)                      # ks now holds v = t^2
    w = ks * np.float32(p[4])
    w += np.float32(p[2])
    w *= ks
    w += np.float32(p[0])
    del ks
    ks = w
    ks[np.arange(SUB_N), np.arange(SUB_N)] = 1.0
    # exact-ish trace sums in f64 (chunked upcast)
    s1 = s2 = 0.0
    for i0 in range(0, SUB_N, 2048):
        chunk = ks[i0:i0 + 2048].astype(np.float64)
        s1 += float(chunk.sum())
        s2 += float(np.dot(chunk.ravel(), chunk.ravel()))
    tr_a2_sub = s2 / SUB_N ** 2
    inv_m = 1.0 / consts[4]["m"]
    tr_d2_sub = tr_a2_sub - inv_m
    print(f"  subsample Gram built ({time.perf_counter()-t0:.1f}s); eigvalsh "
          f"on {SUB_N}x{SUB_N} f32 ...", flush=True)
    t1 = time.perf_counter()
    evals = np.linalg.eigvalsh(ks)             # ascending, f32
    eig_wall = time.perf_counter() - t1
    lam = evals.astype(np.float64)[::-1] / SUB_N       # descending
    mu = lam - inv_m
    order = np.argsort(-np.abs(mu))            # top by |mu|
    mu_sorted = mu[order]
    sum_sq = float(np.dot(mu, mu)) + (consts[4]["m"] - SUB_N) * inv_m ** 2
    tops = {k: float(np.sum(mu_sorted[:k] ** 2) / tr_d2_sub)
            for k in (1, 10, 100, 1000)}
    # model prediction for the subsample: 126x126 reduced frame matrix
    # (frame-constant subspace: 125 mid shells ABOVE the bulk plus the
    # constant mode BELOW it) + bulk (1-g0)/n_sub with mult n_sub - 126.
    # Compare full sorted multisets (the constant mode is the SMALLEST
    # eigenvalue, so a naive "top-126" comparison misaligns by one).
    g0f, g1f = float(consts[4]["g0"]), float(consts[4]["g1"])
    present = n_f > 0
    nf = n_f[present].astype(np.float64)
    m_red = g1f * np.sqrt(np.outer(nf, nf))
    np.fill_diagonal(m_red, (1.0 - g0f) + g0f * nf)
    pred_frame = np.linalg.eigvalsh(m_red) / SUB_N   # ascending, 126 values
    pred_full = np.sort(np.concatenate(
        [pred_frame, np.full(SUB_N - len(nf), (1.0 - g0f) / SUB_N)]))
    obs_sorted = np.sort(lam)
    max_multiset_err = float(np.abs(obs_sorted - pred_full).max())
    np.savez_compressed(HERE / "s6_sub_eigs.npz",
                        evals_f32=evals, idx=idx)
    return {
        "n_sub": SUB_N, "seed": SUB_SEED,
        "frame_sizes_min_max_mean": [int(n_f.min()), int(n_f.max()),
                                     float(n_f.mean())],
        "tr_A2_sub": tr_a2_sub, "tr_D2_sub": tr_d2_sub,
        "trace_check_sum_lam": float(lam.sum()),      # should be ~1
        "sum_mu_sq_from_eigs": sum_sq,                # vs tr_D2_sub
        "topk_frac_observed": tops,
        "top20_eigs_D_sub": [float(x) for x in mu_sorted[:20]],
        "pred_vs_obs_full_multiset_max_abs_err": max_multiset_err,
        "constant_mode_obs_vs_pred": [float(obs_sorted[0]),
                                      float(pred_full[0])],
        "mid_cluster_obs_vs_pred_max_err": float(
            np.abs(obs_sorted[-125:] - pred_full[-125:]).max()),
        "bulk_predicted": (1.0 - g0f) / SUB_N,
        "eigh_wall_s": eig_wall,
    }


# ------------------------------------------------------------- M191 anchor
def m191_arm(u: np.ndarray, consts: dict, s1_4: float, s1_6: float) -> dict:
    """(a) direct recompute of M191's deg-4/deg-6 zonal-family quadrature
    ratios on the unrotated design (rotation-invariant in distribution);
    (b) spectral prediction from the design's S1_ell sums via the zonal
    projection  E_a[err_ell^2] = m_ell ghat_ell^2 S1_ell / N^2."""
    rng = np.random.default_rng(M191_SEED)
    a = rng.standard_normal((M191_NPOLY, D))
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    t = u @ a.T                                       # N x npoly
    out = {}
    for deg, const in (("deg4", 3.0 / (D * (D + 2))),
                       ("deg6", 15.0 / (D * (D + 2) * (D + 4)))):
        p = t ** (4 if deg == "deg4" else 6) - const
        errs = np.abs(p.mean(axis=0)) / p.std(axis=0)
        rms = float(np.sqrt(np.mean(errs ** 2)))
        out[deg + "_direct_ratio"] = rms * math.sqrt(N_DOUBLED)
    # spectral predictions (exact-rational constants -> float)
    c4, c6 = consts[4], consts[6]
    ghat4 = float(zonal_moment(c4["coeffs"], 4) / c4["c1"])   # E[t^4 G_4]
    ghat6 = float(zonal_moment(c6["coeffs"], 6) / c6["c1"])   # E[t^6 G_6]
    ghat46 = float(zonal_moment(c4["coeffs"], 6) / c4["c1"])  # E[t^6 G_4]
    var4 = float(even_moment(8) - even_moment(4) ** 2)
    var6 = float(even_moment(12) - even_moment(6) ** 2)
    err2_4 = c4["m"] * ghat4 ** 2 * s1_4 / N ** 2
    err2_6 = (c6["m"] * ghat6 ** 2 * s1_6 / N ** 2
              + c4["m"] * ghat46 ** 2 * s1_4 / N ** 2)
    out["deg4_pred_ratio"] = math.sqrt(err2_4 / var4) * math.sqrt(N_DOUBLED)
    out["deg6_pred_ratio"] = math.sqrt(err2_6 / var6) * math.sqrt(N_DOUBLED)
    # archived M191 numbers (read-only citation)
    archived = json.loads((PB1 / "m191_g0a_results.json").read_text())
    out["m191_archived_deg4_ratios"] = [
        archived[f"rot{i}"]["deg4"]["ratio"] for i in range(3)]
    out["m191_archived_deg6_ratios"] = [
        archived[f"rot{i}"]["deg6"]["ratio"] for i in range(3)]
    out["npoly"] = M191_NPOLY
    out["note"] = (
        "direct = unrotated design, 200 random unit a, sample-std "
        "normalization, iid scale 1/sqrt(64512) as in M191; pred = zonal "
        "projection through the design's exact S1_ell kernel sums "
        "(deg6 pred includes the H_4 leakage term of t^6)")
    return out


# --------------------------------------------------------------------- main
def main() -> None:
    t_start = time.perf_counter()
    consts = exact_constants()
    print("exact constants verified (E[G_ell]=0, m_ell E[G_ell^2]=1, "
          "dim formulas agree)", flush=True)
    u = load_unit_directions()
    print(f"design loaded: {u.shape}, entries exactly +-1/16", flush=True)

    print("pairwise pass (exact fingerprint + kernel sums) ...", flush=True)
    pw = pairwise_pass(u, consts)

    counts, cw = pw["counts"], pw["counts_within"]
    cross = counts - cw
    nz = np.nonzero(counts)[0]
    fingerprint = {
        "grid": "k/256, k = index - 256",
        "max_grid_dev": pw["max_grid_dev"],
        "distinct_values": {str((k - 256) / 256): int(counts[k]) for k in nz},
        "within_frame": {str((k - 256) / 256): int(cw[k])
                         for k in np.nonzero(cw)[0]},
        "cross_frame": {str((k - 256) / 256): int(cross[k])
                        for k in np.nonzero(cross)[0]},
    }
    structure_verified = (
        pw["max_grid_dev"] == 0.0 and pw["diag_ok"]
        and counts[512] == N                       # t=+1 only on diagonal
        and cw[256 + 0] == N * 255                 # within off-diag all 0
        and cw[512] == N and int(cw.sum()) == N * 256
        and cross[256 + 16] + cross[256 - 16] == N * 32000
        and int(counts.sum()) == N * N
        and set(nz.tolist()) == {256 - 16, 256, 256 + 16, 512}
    )
    print(f"fingerprint: {fingerprint['distinct_values']}  "
          f"max_grid_dev={pw['max_grid_dev']:.1e}  "
          f"structure_verified={structure_verified}", flush=True)

    m4, m6 = consts[4]["m"], consts[6]["m"]
    tr_a2_4 = pw["S2_4"] / N ** 2
    tr_d2_4 = tr_a2_4 - 1.0 / m4
    tr_a2_6 = pw["S2_6"] / N ** 2
    tr_d2_6 = tr_a2_6 - 1.0 / m6

    cf4 = closed_form(4, consts)
    cf6 = closed_form(6, consts)
    rel4 = abs(tr_d2_4 - cf4["tr_D2"]) / cf4["tr_D2"]
    rel6 = abs(tr_d2_6 - cf6["tr_D2"]) / cf6["tr_D2"]
    rel_s1 = abs(pw["S1_4"] - cf4["S1_pred"]) / abs(cf4["S1_pred"])
    rel_s1_6 = abs(pw["S1_6"] - cf6["S1_pred"]) / abs(cf6["S1_pred"])
    assert structure_verified, "3-value structure NOT verified; closed form invalid"
    assert rel4 < 1e-9 and rel6 < 1e-9 and rel_s1 < 1e-9 and rel_s1_6 < 1e-9, (
        rel4, rel6, rel_s1, rel_s1_6)
    print(f"tr(D^2) deg4: pairwise {tr_d2_4:.9e} vs closed {cf4['tr_D2']:.9e} "
          f"(rel {rel4:.1e}); deg6 rel {rel6:.1e}", flush=True)

    print("subsample eigh arm ...", flush=True)
    sub = subsample_arm(u, consts)

    print("M191 anchor arm ...", flush=True)
    m191 = m191_arm(u, consts, pw["S1_4"], pw["S1_6"])

    frac100 = cf4["topk_frac"][100]
    if frac100 >= 0.50:
        verdict = "PASS"
    elif frac100 < 0.05:
        verdict = "KILL"
    else:
        verdict = "INCONCLUSIVE"
    haar4 = math.sqrt(N * cf4["lam_top"])
    haar6 = math.sqrt(N * cf6["lam_top"])

    results = {
        "ledger_id": "s6_bloch_design_bragg_spectrum",
        "date": "2026-08-09",
        "design_choice": ("unrotated 32,256 base set + even-degree kernels; "
                          "identical operator to the antipodally doubled "
                          "64,512 set for even ell (phi(-x)=phi(x))"),
        "constants": {
            "d": D, "N": N, "alpha": str(ALPHA),
            "dim_H4": m4, "dim_H6": m6,
            "C4_coeffs_t^[0,2,4]": [str(consts[4]["coeffs"][k])
                                    for k in (0, 2, 4)],
            "C4_at_1": str(consts[4]["c1"]),
            "G4_at_0": float(consts[4]["g0"]),
            "G4_at_1/16": float(consts[4]["g1"]),
            "G6_at_0": float(consts[6]["g0"]),
            "G6_at_1/16": float(consts[6]["g1"]),
            "exact_identity_checks": ("E[G_ell]=0 and m_ell*E[G_ell^2]=1 "
                                      "hold EXACTLY in rational arithmetic "
                                      "for ell=4,6"),
        },
        "fingerprint": fingerprint,
        "structure_verified": bool(structure_verified),
        "deg4": {
            "tr_A2_pairwise": tr_a2_4, "tr_D2_pairwise": tr_d2_4,
            "closed_form": {k: v for k, v in cf4.items() if k != "S1_pred"},
            "tr_D2_rel_diff_pairwise_vs_closed": rel4,
            "S1_sum_G4": pw["S1_4"], "S1_rel_diff_vs_closed": rel_s1,
        },
        "deg6": {
            "tr_A2_pairwise": tr_a2_6, "tr_D2_pairwise": tr_d2_6,
            "closed_form": {k: v for k, v in cf6.items() if k != "S1_pred"},
            "tr_D2_rel_diff_pairwise_vs_closed": rel6,
            "S1_sum_G6": pw["S1_6"], "S1_rel_diff_vs_closed": rel_s1_6,
        },
        "subsample_arm": sub,
        "m191_consistency": m191,
        "haar_H4_design_over_iid_rms": haar4,
        "haar_H6_design_over_iid_rms": haar6,
        "gate": {
            "rule": "PASS >= 50% of tr(D^2) in top-100 eig^2; KILL < 5%",
            "top100_fraction_fullN_closed_form": frac100,
            "top100_fraction_subsample_observed":
                sub["topk_frac_observed"][100],
            "verdict": verdict,
        },
        "wall_s_total": time.perf_counter() - t_start,
        "pairwise_pass_wall_s": pw["wall_s"],
    }
    (HERE / "s6_results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results["gate"], indent=2))
    print(f"\ntop-k fractions (full N, closed form): {cf4['topk_frac']}")
    print(f"top-k fractions (subsample observed):  {sub['topk_frac_observed']}")
    print(f"M191 anchor: direct {m191['deg4_direct_ratio']:.4f}, "
          f"pred {m191['deg4_pred_ratio']:.4f}, "
          f"archived {m191['m191_archived_deg4_ratios']}")
    print(f"\nVERDICT: {verdict}  "
          f"(wall {results['wall_s_total']:.0f}s)")
    print(f"results written to {HERE / 's6_results.json'}")


if __name__ == "__main__":
    main()
