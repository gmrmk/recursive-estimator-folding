"""G3-P2 premise test -- per-net rotation SELECTION (kill-respecting).

Predeclared in GEN3_RECURSION_PACKET_20260808.md (proposal G3-P2) and the
dispatch task of 2026-08-08.  M180 killed rotation FRAGMENTATION at fixed
budget; this tests SELECTION: choose among k candidate rotations per net,
spend the full n on the chosen one.  M185 measured within-net across-rotation
MSE spread 2.3-8.7x; selection could capture some of it IF a truth-free proxy
tracks per-rotation error.

DESIGN (all predeclared)
------------------------
3 He nets (101/202/303, t3-style), 16 candidate rotations per net (r=0..15,
rotation seed 900_000+net*1_000+r, the PB1/N8a formula), plain-antipodal
Kerdock forward at FULL n = 2*126*256 = 64,512 per rotation (the N8a
sampling-stage-isolating downstream), MSE vs the cached m181 3.5M truths.

Q1 ORACLE HEADROOM: per net, oracle = expected best-of-k over the 16
  measured rotation MSEs, k in {2,4,8,16} (exact subset expectation via the
  order-statistic identity, cross-checked by full enumeration).  Report
  oracle-mean MSE vs single-rotation-mean MSE.
  GATE: oracle-of-8 panel gain < 20% -> family dies regardless of proxy.
Q2 TRUTH-FREE PROXY: per rotation, proxy = variance across the 126 per-frame
  means (each frame's 512-direction antipodal-averaged final-layer mean),
  averaged over the 256 output neurons.  Pure sample statistics, no truth.
  GATE: pooled |spearman(proxy, measured MSE)| < 0.3 -> proxy dies.
PILOT REALITY CHECK: pilot proxy from an 8-frame subset (frames 0..7,
  deterministic; random-subset sensitivity reported as diagnostic).  Report
  spearman(pilot proxy, full proxy) and (pilot proxy, MSE), plus the billed
  cost of a k-candidate pilot stage as a fraction of B = 2.72e11.
VERDICT: PROMOTE only if oracle-of-8 >= 20% AND full-proxy pooled |rho| >=
  0.3 AND pilot-proxy pooled |rho vs MSE| >= 0.25 AND pilot cost (k=8) < 5%
  of B.  Otherwise KILL naming every broken link.

INTERPRETATION DECISIONS (recorded loudly, see P2_NOTES.md):
  * "pooled rho" = Pearson on WITHIN-NET ranks pooled over the 48
    (net,rotation) points -- selection happens within a net, so the pooled
    statistic must not be inflated/deflated by across-net scale differences.
    The naive raw-pooled spearman is also reported as a diagnostic.
  * Pilot cost is computed two ways and both reported: (a) dense
    plain-antipodal forward FLOPs (2*W^2 per sample-layer, first layer
    shared across the antipodal pair), (b) pruned-pipeline scaling from the
    hosted champion's mean effective compute 1.79e11 * (8/126) per
    candidate.  The gate is applied to the CHEAPER estimate (b) -- a real
    hosted pilot would run the real (pruned) pipeline -- so a cost KILL is
    conservative.

FIREWALL: synthetic He nets only; kerdock_phases.npz and m181 truths read
read-only; no frozen source edited or imported; plain numpy (sanctioned);
no dataset/scorer/submission; no git; writes only in this directory.
Checkpoint per net (p2_partial_net{n}.npz) so an interrupted run resumes.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")

import itertools
import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
M181 = HERE.parent / "m181_terminal_smoothing"
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)

WIDTH, DEPTH = 256, 32
N_FRAMES = 126
N_BASE = N_FRAMES * WIDTH          # 32,256 (antipodally doubled -> 64,512)
NET_SEEDS = (101, 202, 303)
N_ROT = 16
K_LIST = (2, 4, 8, 16)
PILOT_FRAMES = 8                   # frames 0..7, deterministic
N_PILOT_SENS = 20                  # random 8-frame subsets, diagnostic only
B = 2.72e11
MEAN_CHI_256 = 15.98438266660852747
BOOT_DRAWS = 4000
BOOT_SEED = 20260808

GATE_ORACLE8 = 0.20
GATE_RHO_FULL = 0.30
GATE_RHO_PILOT = 0.25
GATE_COST_FRAC = 0.05
HOSTED_MEAN_EFFECTIVE = 1.79e11    # champion mean effective compute (packet s1)


# ---------------------------------------------------------------- construction
def he_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def load_kerdock_directions() -> np.ndarray:
    """Verbatim rebuild from run_n8a_gates.py (asset read-only)."""
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (N_FRAMES, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    h_norm = (hadamard / 16.0).astype(np.float32)
    directions = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).reshape(N_BASE, WIDTH).astype(np.float32)
    radii = np.linalg.norm(directions, axis=1)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return directions


def haar_rotation(seed: int) -> np.ndarray:
    """Mirror of estimator.py _haar_rotation (float32 QR, sign-fixed)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


def forward_frame_means(weights, first_eff, kerdock) -> np.ndarray:
    """Plain-antipodal forward; returns per-frame final-layer means (126,256).

    Row order is frame-major, antipodal halves stacked, so the reshape
    (2, 126, 256rows, 256neurons) recovers frames exactly.
    """
    first = kerdock @ first_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    fm = act.reshape(2, N_FRAMES, WIDTH, WIDTH).mean(axis=(0, 2),
                                                     dtype=np.float64)
    # two-signal cross-check: overall mean via frames == direct overall mean
    direct = act.mean(axis=0, dtype=np.float64)
    if not np.allclose(fm.mean(axis=0), direct, rtol=0, atol=1e-12):
        raise RuntimeError("frame-mean decomposition does not reproduce the "
                           "overall mean (bookkeeping bug)")
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
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a - a.mean()
    b = b - b.mean()
    den = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


def spearman(a, b) -> float:
    return pearson(rankdata_avg(a), rankdata_avg(b))


def spearman_formula_check(a, b) -> float:
    """Second derivation (no-ties classic formula) for the cross-check."""
    ra, rb = rankdata_avg(a), rankdata_avg(b)
    n = len(ra)
    d2 = float(((ra - rb) ** 2).sum())
    return 1.0 - 6.0 * d2 / (n * (n * n - 1.0))


def pooled_within_net_rho(vals_a: dict, vals_b: dict) -> float:
    """Pearson on within-net ranks pooled over all (net, rotation) points."""
    ra, rb = [], []
    for n in vals_a:
        ra.append(rankdata_avg(vals_a[n]))
        rb.append(rankdata_avg(vals_b[n]))
    return pearson(np.concatenate(ra), np.concatenate(rb))


def oracle_of_k(mse: np.ndarray, k: int) -> float:
    """E[min over a uniformly random k-subset of the 16] -- exact.

    Order-statistic identity: sorted ascending m_(0..15),
    P(m_(i) is the subset min) = C(15-i, k-1)/C(16, k).
    """
    m = np.sort(np.asarray(mse, dtype=np.float64))
    n = len(m)
    tot = math.comb(n, k)
    return float(sum(m[i] * math.comb(n - 1 - i, k - 1) for i in range(n))
                 / tot)


def oracle_of_k_enum(mse: np.ndarray, k: int) -> float:
    """Second derivation: full enumeration of all C(16,k) subsets."""
    m = np.asarray(mse, dtype=np.float64)
    return float(np.mean([min(m[list(c)])
                          for c in itertools.combinations(range(len(m)), k)]))


# ------------------------------------------------------------------ pilot cost
def pilot_cost() -> dict:
    n_half = PILOT_FRAMES * WIDTH                    # 2048 antipodal-base pts
    layer1 = 2 * n_half * WIDTH * WIDTH              # shared antipodal matmul
    rest = 2 * (2 * n_half) * WIDTH * WIDTH * (DEPTH - 1)
    dense_per_cand = float(layer1 + rest)
    pruned_per_cand = HOSTED_MEAN_EFFECTIVE * (PILOT_FRAMES / N_FRAMES)
    out = {
        "dense_flops_per_candidate": dense_per_cand,
        "dense_frac_B_per_candidate": dense_per_cand / B,
        "pruned_scaled_flops_per_candidate": pruned_per_cand,
        "pruned_scaled_frac_B_per_candidate": pruned_per_cand / B,
        "note": ("dense = plain-antipodal forward, first layer shared; "
                 "pruned-scaled = hosted champion mean effective compute "
                 "1.79e11 x (8/126) frames; gate uses the cheaper "
                 "(pruned-scaled) estimate at k=8"),
    }
    for k in K_LIST:
        out[f"k{k}_dense_frac_B"] = k * dense_per_cand / B
        out[f"k{k}_pruned_scaled_frac_B"] = k * pruned_per_cand / B
    return out


# ------------------------------------------------------------------------ main
def main() -> None:
    t_start = time.perf_counter()
    print("== G3-P2 rotation-SELECTION premise ==", flush=True)
    kerdock = load_kerdock_directions()
    truths, noises = {}, {}
    for n in NET_SEEDS:
        d = np.load(M181 / f"m181_truth_net{n}.npz")
        truths[n] = np.asarray(d["means"], dtype=np.float64)
        noises[n] = float(d["noise_final"])
        d.close()
    print(f"cached truths loaded; noise floors "
          f"{[f'{noises[n]:.2e}' for n in NET_SEEDS]}", flush=True)

    # ---- per-net forward passes (checkpointed) -----------------------------
    frame_means = {}      # net -> (16, 126, 256) float64
    for n in NET_SEEDS:
        ck = HERE / f"p2_partial_net{n}.npz"
        if ck.exists():
            d = np.load(ck)
            frame_means[n] = np.asarray(d["frame_means"], dtype=np.float64)
            d.close()
            print(f"net {n}: checkpoint reused", flush=True)
            continue
        weights = he_weights(n)
        fms = np.empty((N_ROT, N_FRAMES, WIDTH))
        t0 = time.perf_counter()
        for r in range(N_ROT):
            rot = haar_rotation(900_000 + n * 1_000 + r)
            first_eff = (rot.T @ weights[0]).astype(np.float32)
            fms[r] = forward_frame_means(weights, first_eff, kerdock)
        np.savez_compressed(ck, frame_means=fms)
        frame_means[n] = fms
        print(f"net {n}: 16 rotations done in "
              f"{time.perf_counter() - t0:.1f}s, checkpointed", flush=True)

    # determinism spot-check (bitwise repeat of net 101 / r 0)
    w101 = he_weights(101)
    rot0 = haar_rotation(900_000 + 101 * 1_000 + 0)
    fm_repeat = forward_frame_means(
        w101, (rot0.T @ w101[0]).astype(np.float32), kerdock)
    bitwise_ok = bool(np.array_equal(fm_repeat, frame_means[101][0]))
    print(f"bitwise repeat net101/r0: {'OK' if bitwise_ok else 'MISMATCH'}",
          flush=True)
    if not bitwise_ok:
        raise RuntimeError("bitwise repeat failed -- nondeterministic forward "
                           "or stale checkpoint; delete p2_partial_net101.npz")

    # ---- per-rotation statistics -------------------------------------------
    mse, proxy_full, proxy_pilot = {}, {}, {}
    pilot_sens_rng = np.random.default_rng(BOOT_SEED + 77)
    sens_subsets = [np.sort(pilot_sens_rng.choice(N_FRAMES, PILOT_FRAMES,
                                                  replace=False))
                    for _ in range(N_PILOT_SENS)]
    proxy_pilot_sens = {}  # net -> (N_PILOT_SENS, 16)
    for n in NET_SEEDS:
        fms = frame_means[n]                        # (16, 126, 256)
        preds = fms.mean(axis=1)                    # (16, 256)
        mse[n] = ((preds - truths[n][None]) ** 2).mean(axis=1)
        proxy_full[n] = fms.var(axis=1, ddof=1).mean(axis=1)
        proxy_pilot[n] = fms[:, :PILOT_FRAMES].var(axis=1, ddof=1).mean(axis=1)
        proxy_pilot_sens[n] = np.stack([
            fms[:, s].var(axis=1, ddof=1).mean(axis=1) for s in sens_subsets])

    # ---- Q1 oracle headroom -------------------------------------------------
    q1 = {"per_net": {}, "panel": {}}
    panel_single = float(np.mean([mse[n].mean() for n in NET_SEEDS]))
    for n in NET_SEEDS:
        row = {
            "mse_per_rotation": [float(v) for v in mse[n]],
            "mse_mean": float(mse[n].mean()),
            "mse_min": float(mse[n].min()),
            "mse_max": float(mse[n].max()),
            "spread_max_over_min": float(mse[n].max() / mse[n].min()),
            "truth_noise_floor": noises[n],
            "oracle": {}, "gain": {}, "gain_noise_subtracted_diag": {},
        }
        for k in K_LIST:
            o = oracle_of_k(mse[n], k)
            o2 = oracle_of_k_enum(mse[n], k)
            if abs(o - o2) > 1e-12 * max(o, 1e-30):
                raise RuntimeError(f"oracle cross-check failed net {n} k={k}: "
                                   f"{o!r} vs {o2!r}")
            row["oracle"][str(k)] = o
            row["gain"][str(k)] = 1.0 - o / row["mse_mean"]
            row["gain_noise_subtracted_diag"][str(k)] = (
                1.0 - (o - noises[n]) / max(row["mse_mean"] - noises[n], 1e-30))
        q1["per_net"][str(n)] = row
    for k in K_LIST:
        po = float(np.mean([q1["per_net"][str(n)]["oracle"][str(k)]
                            for n in NET_SEEDS]))
        q1["panel"][str(k)] = {"oracle_mse": po,
                               "single_mean_mse": panel_single,
                               "gain": 1.0 - po / panel_single}
    q1["oracle_crosscheck"] = "order-statistic identity == full enumeration"

    # ---- Q2 proxy correlations ---------------------------------------------
    def rho_block(pa: dict, pb: dict) -> dict:
        per_net = {}
        for n in NET_SEEDS:
            r1 = spearman(pa[n], pb[n])
            r2 = spearman_formula_check(pa[n], pb[n])
            if abs(r1 - r2) > 1e-10:
                raise RuntimeError("spearman cross-check failed")
            per_net[str(n)] = r1
        return {
            "per_net": per_net,
            "pooled_within_net_ranked": pooled_within_net_rho(pa, pb),
            "pooled_raw_diag": spearman(
                np.concatenate([pa[n] for n in NET_SEEDS]),
                np.concatenate([pb[n] for n in NET_SEEDS])),
        }

    q2 = {
        "proxy_def": ("var over 126 per-frame means (each frame = 512 "
                      "antipodal directions, final layer), ddof=1, "
                      "averaged over 256 neurons; no truth used"),
        "full_proxy_vs_mse": rho_block(proxy_full, mse),
        "proxy_full_values": {str(n): [float(v) for v in proxy_full[n]]
                              for n in NET_SEEDS},
    }

    pilot = {
        "pilot_def": f"frames 0..{PILOT_FRAMES - 1} (deterministic subset)",
        "pilot_vs_full_proxy": rho_block(proxy_pilot, proxy_full),
        "pilot_vs_mse": rho_block(proxy_pilot, mse),
        "pilot_values": {str(n): [float(v) for v in proxy_pilot[n]]
                         for n in NET_SEEDS},
        "cost": pilot_cost(),
    }
    # sensitivity: pooled rho(pilot, mse) over 20 random 8-frame subsets
    sens = []
    for i in range(N_PILOT_SENS):
        pa = {n: proxy_pilot_sens[n][i] for n in NET_SEEDS}
        sens.append(pooled_within_net_rho(pa, mse))
    pilot["pilot_vs_mse_sensitivity_random_subsets"] = {
        "n_subsets": N_PILOT_SENS,
        "pooled_rho_mean": float(np.mean(sens)),
        "pooled_rho_std": float(np.std(sens, ddof=1)),
        "pooled_rho_min": float(np.min(sens)),
        "pooled_rho_max": float(np.max(sens)),
    }

    # ---- bootstrap CIs on the gate quantities ------------------------------
    rng = np.random.default_rng(BOOT_SEED)
    b_gain8, b_rho_full, b_rho_pilot = [], [], []
    for _ in range(BOOT_DRAWS):
        idx = {n: rng.integers(0, N_ROT, size=N_ROT) for n in NET_SEEDS}
        m_b = {n: mse[n][idx[n]] for n in NET_SEEDS}
        pf_b = {n: proxy_full[n][idx[n]] for n in NET_SEEDS}
        pp_b = {n: proxy_pilot[n][idx[n]] for n in NET_SEEDS}
        po = np.mean([oracle_of_k(m_b[n], 8) for n in NET_SEEDS])
        ps = np.mean([m_b[n].mean() for n in NET_SEEDS])
        b_gain8.append(1.0 - po / ps)
        b_rho_full.append(pooled_within_net_rho(pf_b, m_b))
        b_rho_pilot.append(pooled_within_net_rho(pp_b, m_b))

    def ci(v):
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

    boots = {
        "draws": BOOT_DRAWS, "seed": BOOT_SEED,
        "oracle8_panel_gain_ci95": ci(b_gain8),
        "rho_full_pooled_ci95": ci(b_rho_full),
        "rho_pilot_pooled_ci95": ci(b_rho_pilot),
        "caveat": ("resampling rotations with replacement biases a min-type "
                   "statistic; the oracle-gain CI is diagnostic, the point "
                   "estimate on the real 16 governs"),
    }

    # ---- gates and verdict --------------------------------------------------
    gain8 = q1["panel"]["8"]["gain"]
    rho_full = q2["full_proxy_vs_mse"]["pooled_within_net_ranked"]
    rho_pilot = pilot["pilot_vs_mse"]["pooled_within_net_ranked"]
    cost8 = pilot["cost"]["k8_pruned_scaled_frac_B"]
    gates = {
        "q1_oracle8_gain": {"value": gain8, "threshold": GATE_ORACLE8,
                            "pass": bool(gain8 >= GATE_ORACLE8)},
        "q2_full_proxy_rho": {"value": rho_full, "threshold": GATE_RHO_FULL,
                              "pass": bool(abs(rho_full) >= GATE_RHO_FULL)},
        "pilot_proxy_rho": {"value": rho_pilot, "threshold": GATE_RHO_PILOT,
                            "pass": bool(abs(rho_pilot) >= GATE_RHO_PILOT)},
        "pilot_cost_k8": {"value": cost8, "threshold": GATE_COST_FRAC,
                          "pass": bool(cost8 < GATE_COST_FRAC)},
    }
    broken = [k for k, g in gates.items() if not g["pass"]]
    verdict = "PROMOTE" if not broken else (
        "KILL: broken links = " + ", ".join(broken))

    results = {
        "date": "2026-08-08",
        "experiment": "G3-P2 rotation-selection premise",
        "predeclaration": ("GEN3_RECURSION_PACKET_20260808.md G3-P2 + "
                           "dispatch task 2026-08-08"),
        "firewall": ("synthetic He nets; kerdock_phases.npz + m181 truths "
                     "read-only; plain numpy; no submission; no git; writes "
                     "in pb1 dir only"),
        "design": {
            "nets": list(NET_SEEDS), "rotations": N_ROT,
            "rotation_seed_formula": "900000+net*1000+r",
            "n_full": 2 * N_BASE, "frames": N_FRAMES,
            "pilot_frames": PILOT_FRAMES, "B": B,
            "downstream": "plain-antipodal Kerdock forward (N8a)",
        },
        "q1_oracle_headroom": q1,
        "q2_truth_free_proxy": q2,
        "pilot_reality_check": pilot,
        "bootstrap": boots,
        "crosschecks": {
            "frame_mean_vs_direct_mean": "asserted every forward (atol 1e-12)",
            "oracle_formula_vs_enumeration": "asserted every net/k (rtol 1e-12)",
            "spearman_pearson_ranks_vs_d2_formula": "asserted every rho (1e-10)",
            "bitwise_repeat_net101_r0": bitwise_ok,
        },
        "gates": gates,
        "verdict": verdict,
        "wall_s": round(time.perf_counter() - t_start, 1),
    }
    out = HERE / "p2_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"\nVERDICT: {verdict}")
    for k, g in gates.items():
        print(f"  {k}: value={g['value']:.4f} thr={g['threshold']} "
              f"pass={g['pass']}")
    print(f"results -> {out}", flush=True)


if __name__ == "__main__":
    main()
