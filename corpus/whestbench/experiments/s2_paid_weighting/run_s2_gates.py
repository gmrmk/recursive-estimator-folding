"""S2 -- paid-information rotation weighting (ledger id
s2_paid_information_rotation_weighting), predeclared in the dispatch task of
2026-08-09.

MECHANISM UNDER TEST: split the budget across K rotations and estimate each
rotation's quality from the PAID samples themselves.  The antipodal-pair
structure gives within-rotation half-sample estimates whose disagreement is
(under the iid premise) an unbiased variance proxy; combine rotations with
inverse-variance weights under a SPLIT-SAMPLE guard (weights estimated on one
half of the antipodal pairs, applied to the mean computed from the other
half).

PREDECLARED GATES (task text governs)
-------------------------------------
G0-CORRELATION: fresh simulation, 3 cached-truth nets x 16 rotations at
  reduced direction count.  Per rotation: (a) half-sample disagreement
  variance proxy over balanced random splits of the antipodal pairs, (b)
  realized MSE vs cached m181 truth.  GATE: pooled |spearman rho| < 0.4 ->
  KILL, stop (this is where gen3_p2 [-0.089 pilot] and p2b [best 0.166]
  died).
G0-EFFECT (only if the rho gate passes): split-sample inverse-variance
  combination across K=4 rotations at matched total sample count vs the
  equal-weight baseline.  PASS requires MSE ratio (weighted/equal) <= 0.98
  AND no detectable bias (paired test across nets/neurons).

INTERPRETATION DECISIONS (recorded loudly, none silent -- see S2_VERDICT.md)
---------------------------------------------------------------------------
1. Nets = all three cached-truth nets (101/202/303); rotations = 16/net,
   seed formula 900000+net*1000+r (P2 lineage).
2. Reduced direction count = Kerdock frames 0..31 (deterministic prefix,
   matching the P2 pilot convention) -> 8192 antipodal pairs = 16384
   evaluations per rotation.  32 ~= 126/4 is exactly the per-rotation budget
   a K=4 budget split would pay, so the correlation is measured in the
   operating regime of the mechanism.
3. Proxy = mean over S=64 seeded balanced pair-splits and 256 neurons of
   (mean_halfA - mean_halfB)^2 / 4.  Closed form E[proxy] = s^2/P (ddof-1
   pair variance / n_pairs) is computed as the second derivation of the gate
   quantity; a single-split version is reported as a practical diagnostic.
   Split index sets are shared across (net, rotation) to reduce comparison
   noise (pairs are indexed by the same pre-rotation base directions).
4. "Pooled rho" = Pearson on WITHIN-NET ranks pooled over the 48
   (net, rotation) points -- the P2 lineage convention (weighting happens
   within a net; raw pooling manufactured a sign flip in P2).  The raw
   pooled spearman is reported as a diagnostic.  The 0.4 gate applies to the
   within-net-ranked pooled value.
5. G0-EFFECT: K=4 = rotations 0..3 (deterministic prefix), same 32-frame
   data as G0-CORR; R=20 seeded half-split replicates; per half, the weight
   variance estimate is the disagreement over 16 balanced sub-splits of that
   half; the combined estimator is symmetrized: 0.5*(sum w(A)~ * meanB +
   sum w(B)~ * meanA).  Equal baseline = plain mean of the 4 full-sample
   rotation means (identical samples; only the weights differ).  Bias check:
   paired test on signed per-neuron errors (weighted - equal) across
   3 nets x 256 neurons, averaged over replicates (within-net neuron
   correlation acknowledged as a limitation).
6. Archive diagnostic (non-gating): the same disagreement construction at
   FRAME level on the archived full-budget P2 frame means (p2_partial_*.npz,
   read-only) vs the archived per-rotation MSEs.  Frame-level splits are
   monotone-equivalent in expectation to the P2 frame-variance proxy, so
   this locates the fresh pair-level result against the killed P2 signal.
   The archive alone could NOT carry G0 because it stores only frame means;
   pair-level splits (within-frame dispersion) need the fresh forward.

FIREWALL: synthetic He nets only; kerdock_phases.npz, m181 truths and P2
archives read-only; plain numpy; no submissions; no git; writes only inside
s2_paid_weighting/.  Checkpoint per net so an interrupted run resumes.

TWO-SIGNAL CROSS-CHECKS (all asserted or reported):
  * bitwise repeat: full-budget forward net101/r0 == archived P2 frame
    means row (np.array_equal);
  * reduced-forward frame means vs archived frame_means[:, :32, :] (max
    abs diff reported; validates the whole construction chain);
  * pair-mean bookkeeping == direct overall mean, every forward (atol 1e-12);
  * spearman via Pearson-on-ranks == 6*sum d^2/(n(n^2-1)) formula, every rho;
  * split-average proxy vs closed-form s^2/P (max rel dev + gate rho
    recomputed from the closed form).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PB1 = EXP / "pb1_premise_battery"
M181 = EXP / "m181_terminal_smoothing"
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)

WIDTH, DEPTH = 256, 32
N_FRAMES_FULL = 126
FRAMES_RED = 32                     # frames 0..31, deterministic prefix
N_PAIRS = FRAMES_RED * WIDTH        # 8192 antipodal pairs
NET_SEEDS = (101, 202, 303)
N_ROT = 16
K_EFFECT = 4                        # rotations 0..3
S_SPLITS = 64
S_WEIGHT = 16
R_REPS = 20
SEED = 20260809
BOOT_DRAWS = 4000
MEAN_CHI_256 = 15.98438266660852747

GATE_RHO = 0.40
GATE_RATIO = 0.98
GATE_BIAS_P = 0.05


# ------------------------------------------------- construction (P2 verbatim)
def he_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def load_kerdock_directions() -> np.ndarray:
    """Verbatim rebuild from run_p2_rotation_selection.py (asset read-only)."""
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (N_FRAMES_FULL, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    h_norm = (hadamard / 16.0).astype(np.float32)
    directions = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).reshape(N_FRAMES_FULL * WIDTH, WIDTH).astype(np.float32)
    radii = np.linalg.norm(directions, axis=1)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return directions


def haar_rotation(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


def forward_pair_means(weights, first_eff, kerdock_rows) -> np.ndarray:
    """Plain-antipodal forward; returns per-PAIR final-layer means (P, 256).

    Row order matches P2: [relu(+x); relu(-x)] stacked, so pair p is rows
    (p, p+P).
    """
    first = kerdock_rows @ first_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    p = kerdock_rows.shape[0]
    pm = 0.5 * (act[:p].astype(np.float64) + act[p:].astype(np.float64))
    direct = act.mean(axis=0, dtype=np.float64)
    if not np.allclose(pm.mean(axis=0), direct, rtol=0, atol=1e-12):
        raise RuntimeError("pair-mean bookkeeping does not reproduce the "
                           "overall mean")
    return pm


def forward_frame_means_full(weights, first_eff, kerdock) -> np.ndarray:
    """P2's forward_frame_means, verbatim, for the bitwise archive repeat."""
    first = kerdock @ first_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    fm = act.reshape(2, N_FRAMES_FULL, WIDTH, WIDTH).mean(axis=(0, 2),
                                                          dtype=np.float64)
    direct = act.mean(axis=0, dtype=np.float64)
    if not np.allclose(fm.mean(axis=0), direct, rtol=0, atol=1e-12):
        raise RuntimeError("frame-mean decomposition failed")
    return fm


# ------------------------------------------------------------------ statistics
def rankdata_avg(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    sx = x[order]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        r[i:j + 1] = 0.5 * (i + j) + 1.0
        i = j + 1
    ranks = np.empty(len(x))
    ranks[order] = r
    return ranks


def pearson(a, b) -> float:
    a = np.asarray(a, dtype=np.float64) - np.mean(a)
    b = np.asarray(b, dtype=np.float64) - np.mean(b)
    den = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


def spearman(a, b) -> float:
    r1 = pearson(rankdata_avg(a), rankdata_avg(b))
    ra, rb = rankdata_avg(a), rankdata_avg(b)
    n = len(ra)
    r2 = 1.0 - 6.0 * float(((ra - rb) ** 2).sum()) / (n * (n * n - 1.0))
    if abs(r1 - r2) > 1e-10:
        raise RuntimeError("spearman cross-check failed")
    return r1


def pooled_within_net_rho(va: dict, vb: dict) -> float:
    ra, rb = [], []
    for n in va:
        ra.append(rankdata_avg(va[n]))
        rb.append(rankdata_avg(vb[n]))
    return pearson(np.concatenate(ra), np.concatenate(rb))


def rho_block(pa: dict, pb: dict) -> dict:
    return {
        "per_net": {str(n): spearman(pa[n], pb[n]) for n in pa},
        "pooled_within_net_ranked": pooled_within_net_rho(pa, pb),
        "pooled_raw_diag": spearman(
            np.concatenate([pa[n] for n in pa]),
            np.concatenate([pb[n] for n in pa])),
    }


def sign_matrix(rng: np.random.Generator, n_splits: int, n_items: int
                ) -> np.ndarray:
    """(n_splits, n_items) of +-1, each row balanced (sum 0)."""
    e = np.empty((n_splits, n_items), dtype=np.float64)
    half = n_items // 2
    base = np.concatenate([np.ones(half), -np.ones(n_items - half)])
    for s in range(n_splits):
        e[s] = base[rng.permutation(n_items)]
    return e


def norm_p_two_sided(t: float) -> float:
    return float(math.erfc(abs(t) / math.sqrt(2.0)))


# ------------------------------------------------------------------------ main
def main() -> None:
    t_start = time.perf_counter()
    print("== S2 paid-information rotation weighting ==", flush=True)
    kerdock = load_kerdock_directions()
    kerdock_red = kerdock[:N_PAIRS]              # frames 0..31, frame-major

    truths, noises = {}, {}
    for n in NET_SEEDS:
        d = np.load(M181 / f"m181_truth_net{n}.npz")
        truths[n] = np.asarray(d["means"], dtype=np.float64)
        noises[n] = float(d["noise_final"])
        d.close()
    print("cached m181 truths loaded (read-only)", flush=True)

    arch = {}
    for n in NET_SEEDS:
        d = np.load(PB1 / f"p2_partial_net{n}.npz")
        arch[n] = np.asarray(d["frame_means"], dtype=np.float64)
        d.close()
    print("P2 archive frame means loaded (read-only)", flush=True)

    # shared balanced splits (pairs indexed by pre-rotation base directions)
    rng_splits = np.random.default_rng(SEED)
    E = sign_matrix(rng_splits, S_SPLITS, N_PAIRS)        # (64, 8192)

    # ---- fresh reduced-budget forwards (checkpointed per net) -------------
    full_means, pair_var, disagree, fresh_fm, pm03 = {}, {}, {}, {}, {}
    for n in NET_SEEDS:
        ck = HERE / f"s2_partial_net{n}.npz"
        if ck.exists():
            d = np.load(ck)
            full_means[n] = d["full_means"]
            pair_var[n] = d["pair_var"]
            disagree[n] = d["disagree"]
            fresh_fm[n] = d["fresh_frame_means"]
            pm03[n] = np.asarray(d["pm03"], dtype=np.float64)
            d.close()
            print(f"net {n}: checkpoint reused", flush=True)
            continue
        weights = he_weights(n)
        fm_ = np.empty((N_ROT, WIDTH))
        pv_ = np.empty((N_ROT, WIDTH))
        dg_ = np.empty((N_ROT, S_SPLITS))
        ff_ = np.empty((N_ROT, FRAMES_RED, WIDTH))
        pm_keep = np.empty((K_EFFECT, N_PAIRS, WIDTH), dtype=np.float32)
        t0 = time.perf_counter()
        for r in range(N_ROT):
            rot = haar_rotation(900_000 + n * 1_000 + r)
            first_eff = (rot.T @ weights[0]).astype(np.float32)
            pm = forward_pair_means(weights, first_eff, kerdock_red)
            fm_[r] = pm.mean(axis=0)
            pv_[r] = pm.var(axis=0, ddof=1)
            diff = (E @ pm) * (2.0 / N_PAIRS)             # (64, 256) mA-mB
            dg_[r] = (diff * diff).mean(axis=1) / 4.0
            ff_[r] = pm.reshape(FRAMES_RED, WIDTH, WIDTH).mean(axis=1)
            if r < K_EFFECT:
                pm_keep[r] = pm.astype(np.float32)
        np.savez_compressed(ck, full_means=fm_, pair_var=pv_, disagree=dg_,
                            fresh_frame_means=ff_, pm03=pm_keep)
        full_means[n], pair_var[n], disagree[n] = fm_, pv_, dg_
        fresh_fm[n], pm03[n] = ff_, pm_keep.astype(np.float64)
        print(f"net {n}: 16 reduced forwards in "
              f"{time.perf_counter() - t0:.1f}s, checkpointed", flush=True)

    # ---- cross-check 1: bitwise full-budget repeat vs P2 archive ----------
    w101 = he_weights(101)
    rot0 = haar_rotation(900_000 + 101 * 1_000 + 0)
    fm_repeat = forward_frame_means_full(
        w101, (rot0.T @ w101[0]).astype(np.float32), kerdock)
    bitwise_ok = bool(np.array_equal(fm_repeat, arch[101][0]))
    print(f"bitwise full-budget repeat net101/r0 vs archive: "
          f"{'OK' if bitwise_ok else 'MISMATCH'}", flush=True)
    if not bitwise_ok:
        raise RuntimeError("bitwise archive repeat failed -- construction "
                           "drift; stop")

    # ---- cross-check 2: reduced frame means vs archive prefix -------------
    max_abs, max_rel = 0.0, 0.0
    for n in NET_SEEDS:
        diff = np.abs(fresh_fm[n] - arch[n][:, :FRAMES_RED, :])
        max_abs = max(max_abs, float(diff.max()))
        max_rel = max(max_rel, float(
            (diff / np.maximum(np.abs(arch[n][:, :FRAMES_RED, :]), 1e-3)
             ).max()))
    print(f"reduced-forward vs archive prefix: max abs diff {max_abs:.3e}, "
          f"max rel diff {max_rel:.3e}", flush=True)
    if max_abs > 1e-3:
        raise RuntimeError("reduced forward diverges from archived frame "
                           "means beyond float32 tolerance -- stop")

    # ---- G0-CORRELATION ---------------------------------------------------
    mse, proxy, proxy_cf, proxy_1 = {}, {}, {}, {}
    for n in NET_SEEDS:
        mse[n] = ((full_means[n] - truths[n][None]) ** 2).mean(axis=1)
        proxy[n] = disagree[n].mean(axis=1)               # S=64 split average
        proxy_cf[n] = pair_var[n].mean(axis=1) / N_PAIRS  # closed form s^2/P
        proxy_1[n] = disagree[n][:, 0]                    # single split diag

    # cross-check 3: split average vs closed form
    all_p = np.concatenate([proxy[n] for n in NET_SEEDS])
    all_cf = np.concatenate([proxy_cf[n] for n in NET_SEEDS])
    cf_max_rel_dev = float(np.max(np.abs(all_p / all_cf - 1.0)))
    print(f"split-average vs closed-form s^2/P: max rel dev "
          f"{cf_max_rel_dev:.4f}", flush=True)

    corr = rho_block(proxy, mse)
    corr_cf = rho_block(proxy_cf, mse)
    corr_1 = rho_block(proxy_1, mse)

    # bootstrap CI on the gate quantity (resample rotations within net)
    rng_b = np.random.default_rng(SEED + 1)
    b_rho = []
    for _ in range(BOOT_DRAWS):
        idx = {n: rng_b.integers(0, N_ROT, size=N_ROT) for n in NET_SEEDS}
        b_rho.append(pooled_within_net_rho(
            {n: proxy[n][idx[n]] for n in NET_SEEDS},
            {n: mse[n][idx[n]] for n in NET_SEEDS}))
    rho_ci = [float(np.percentile(b_rho, 2.5)),
              float(np.percentile(b_rho, 97.5))]

    # archive full-budget frame-level diagnostic (non-gating)
    rng_a = np.random.default_rng(SEED + 2)
    Ef = sign_matrix(rng_a, S_SPLITS, N_FRAMES_FULL)
    arch_proxy, arch_mse = {}, {}
    for n in NET_SEEDS:
        fmn = arch[n]                                     # (16, 126, 256)
        d = np.einsum("sf,rfj->rsj", Ef, fmn) * (2.0 / N_FRAMES_FULL)
        arch_proxy[n] = (d * d).mean(axis=2).mean(axis=1) / 4.0
        arch_mse[n] = ((fmn.mean(axis=1) - truths[n][None]) ** 2).mean(axis=1)
    arch_corr = rho_block(arch_proxy, arch_mse)

    rho_gate_val = corr["pooled_within_net_ranked"]
    gate_corr_pass = bool(abs(rho_gate_val) >= GATE_RHO)
    print(f"\nG0-CORRELATION pooled within-net rho = {rho_gate_val:+.4f} "
          f"(CI95 [{rho_ci[0]:+.3f}, {rho_ci[1]:+.3f}]) "
          f"gate |rho|>={GATE_RHO} -> {'PASS' if gate_corr_pass else 'KILL'}",
          flush=True)

    results = {
        "date": "2026-08-09",
        "experiment": "S2 paid-information rotation weighting",
        "ledger_id": "s2_paid_information_rotation_weighting",
        "predeclaration": "dispatch task 2026-08-09 (S2)",
        "firewall": ("synthetic He nets; kerdock_phases.npz + m181 truths + "
                     "P2 archives read-only; plain numpy; no submission; no "
                     "git; writes only in s2_paid_weighting/"),
        "design": {
            "nets": list(NET_SEEDS), "rotations": N_ROT,
            "rotation_seed_formula": "900000+net*1000+r",
            "frames_reduced": FRAMES_RED, "n_pairs": N_PAIRS,
            "n_evals_per_rotation": 2 * N_PAIRS,
            "proxy_splits": S_SPLITS, "split_seed": SEED,
            "proxy_def": ("mean over 64 balanced pair-splits and 256 neurons "
                          "of (meanA-meanB)^2/4; closed form s^2/P as second "
                          "derivation"),
            "pooled_rho_def": ("Pearson on within-net ranks pooled over 48 "
                               "(net,rotation) points; raw pooled spearman "
                               "diagnostic"),
        },
        "g0_correlation": {
            "mse_per_rotation": {str(n): [float(v) for v in mse[n]]
                                 for n in NET_SEEDS},
            "proxy_per_rotation": {str(n): [float(v) for v in proxy[n]]
                                   for n in NET_SEEDS},
            "rho_proxy_vs_mse": corr,
            "rho_closedform_vs_mse": corr_cf,
            "rho_singlesplit_vs_mse": corr_1,
            "rho_pooled_ci95_bootstrap": rho_ci,
            "bootstrap": {"draws": BOOT_DRAWS, "seed": SEED + 1},
            "archive_full_budget_frame_level_diag": {
                "note": ("frame-level disagreement on archived 126-frame P2 "
                         "means; monotone-equivalent in expectation to the "
                         "killed P2 frame-variance proxy; NON-GATING"),
                "rho": arch_corr,
            },
            "gate": {"value": rho_gate_val, "threshold": GATE_RHO,
                     "pass": gate_corr_pass},
        },
        "crosschecks": {
            "bitwise_full_budget_repeat_net101_r0_vs_archive": bitwise_ok,
            "reduced_forward_vs_archive_prefix_max_abs_diff": max_abs,
            "reduced_forward_vs_archive_prefix_max_rel_diff": max_rel,
            "pair_mean_vs_direct_mean": "asserted every forward (atol 1e-12)",
            "spearman_pearson_ranks_vs_d2_formula": "asserted every rho",
            "split_avg_vs_closed_form_max_rel_dev": cf_max_rel_dev,
        },
        "truth_noise_floors": {str(n): noises[n] for n in NET_SEEDS},
    }

    # ---- G0-EFFECT (only if the correlation gate passes) ------------------
    if not gate_corr_pass:
        results["g0_effect"] = ("NOT RUN -- predeclared stop: correlation "
                                "gate failed")
        results["verdict"] = (
            f"KILL: G0-CORRELATION pooled |rho| = {abs(rho_gate_val):.4f} "
            f"< {GATE_RHO}; the paid-sample half-disagreement proxy dies "
            f"where the P2/P2b truth-free proxies died")
    else:
        rng_e = np.random.default_rng(SEED + 3)
        equal_err = {n: np.mean([pm03[n][k].mean(axis=0)
                                 for k in range(K_EFFECT)], axis=0)
                     - truths[n] for n in NET_SEEDS}
        panel_ratios, per_net_ratios = [], {n: [] for n in NET_SEEDS}
        bias_diff_accum = {n: np.zeros(WIDTH) for n in NET_SEEDS}
        weight_spread = []
        for rep in range(R_REPS):
            mse_w_net, mse_e_net = [], []
            for n in NET_SEEDS:
                perm = rng_e.permutation(N_PAIRS)
                ia, ib = perm[:N_PAIRS // 2], perm[N_PAIRS // 2:]
                ew_a = sign_matrix(rng_e, S_WEIGHT, len(ia))
                ew_b = sign_matrix(rng_e, S_WEIGHT, len(ib))
                m_a = np.empty((K_EFFECT, WIDTH))
                m_b = np.empty((K_EFFECT, WIDTH))
                v_a = np.empty(K_EFFECT)
                v_b = np.empty(K_EFFECT)
                for k in range(K_EFFECT):
                    pa, pb = pm03[n][k][ia], pm03[n][k][ib]
                    m_a[k], m_b[k] = pa.mean(axis=0), pb.mean(axis=0)
                    da = (ew_a @ pa) * (2.0 / len(ia))
                    db = (ew_b @ pb) * (2.0 / len(ib))
                    v_a[k] = (da * da).mean() / 4.0
                    v_b[k] = (db * db).mean() / 4.0
                wa = (1.0 / np.maximum(v_a, 1e-300))
                wb = (1.0 / np.maximum(v_b, 1e-300))
                wa, wb = wa / wa.sum(), wb / wb.sum()
                weight_spread.append(float(wa.max() / wa.min()))
                comb = 0.5 * ((wa[:, None] * m_b).sum(axis=0)
                              + (wb[:, None] * m_a).sum(axis=0))
                e_w = comb - truths[n]
                mse_w_net.append(float((e_w ** 2).mean()))
                mse_e_net.append(float((equal_err[n] ** 2).mean()))
                per_net_ratios[n].append(mse_w_net[-1] / mse_e_net[-1])
                bias_diff_accum[n] += (e_w - equal_err[n]) / R_REPS
            panel_ratios.append(float(np.mean(mse_w_net))
                                / float(np.mean(mse_e_net)))
        panel_ratios = np.asarray(panel_ratios)
        ratio_mean = float(panel_ratios.mean())
        ratio_sd = float(panel_ratios.std(ddof=1))
        ratio_ci = [ratio_mean - 1.96 * ratio_sd / math.sqrt(R_REPS),
                    ratio_mean + 1.96 * ratio_sd / math.sqrt(R_REPS)]

        # bias: paired test on signed error diffs across nets x neurons
        d_all = np.concatenate([bias_diff_accum[n] for n in NET_SEEDS])
        t_stat = float(d_all.mean() / (d_all.std(ddof=1)
                                       / math.sqrt(len(d_all))))
        p_bias = norm_p_two_sided(t_stat)
        bias_pass = bool(p_bias >= GATE_BIAS_P)
        ratio_pass = bool(ratio_mean <= GATE_RATIO)

        results["g0_effect"] = {
            "k": K_EFFECT, "replicates": R_REPS, "seed": SEED + 3,
            "weight_subsplits_per_half": S_WEIGHT,
            "mse_ratio_panel_mean": ratio_mean,
            "mse_ratio_panel_sd": ratio_sd,
            "mse_ratio_panel_ci95": ratio_ci,
            "mse_ratio_per_net_mean": {
                str(n): float(np.mean(per_net_ratios[n])) for n in NET_SEEDS},
            "weight_spread_max_over_min": {
                "mean": float(np.mean(weight_spread)),
                "max": float(np.max(weight_spread))},
            "bias_paired_t": t_stat, "bias_p_normal_approx": p_bias,
            "bias_mean_signed_diff_per_net": {
                str(n): float(bias_diff_accum[n].mean()) for n in NET_SEEDS},
            "bias_limitation": ("768 (net,neuron) errors are correlated "
                                "within a net; p-value is anti-conservative"),
            "gate_ratio": {"value": ratio_mean, "threshold": GATE_RATIO,
                           "pass": ratio_pass},
            "gate_bias": {"p": p_bias, "threshold": GATE_BIAS_P,
                          "pass": bias_pass},
        }
        if ratio_pass and bias_pass:
            results["verdict"] = (
                f"PASS: rho {rho_gate_val:+.3f}, MSE ratio "
                f"{ratio_mean:.4f} <= {GATE_RATIO}, no detectable bias "
                f"(p={p_bias:.3f})")
        else:
            broken = []
            if not ratio_pass:
                broken.append(f"MSE ratio {ratio_mean:.4f} > {GATE_RATIO}")
            if not bias_pass:
                broken.append(f"bias detected (p={p_bias:.4g})")
            results["verdict"] = "KILL: " + "; ".join(broken)

    results["wall_s"] = round(time.perf_counter() - t_start, 1)
    out = HERE / "s2_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"\nVERDICT: {results['verdict']}")
    print(f"results -> {out}", flush=True)


if __name__ == "__main__":
    main()
