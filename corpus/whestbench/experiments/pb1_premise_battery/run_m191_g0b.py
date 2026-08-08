"""M191 G0-b: harmonic control-variate battery arm.

Governed by M191_HARMONIC_PREDECLARATION.md (section G0-b).  G0-a found the
Kerdock antipodal design is an exact 2-design (odd degrees + degree 2
annihilated); residual quadrature error is ~11% of iid at degree 4 and ~40%
at degree 6.  This arm asks whether a WEIGHT-DERIVED degree-4/6 harmonic
control variate recovers a measurable share of the remaining panel MSE.

Estimators per (net, rotation seed), scored vs the cached m181 3.5M-truth
(noise floor subtracted):

  baseline      fhat_j = mean_s ReLU-net final activation f_j(u_s)
                (identical construction to m181 Arm 0 -- cross-checked
                bitwise-ish against the cached m181_g0_partial stacks).
  cv_*          fhat_j - sum_k beta_jk * mean_s p_k(u_s), beta fitted
                SPLIT-SAMPLE: beta^A from cov/var on a random half A,
                correction applied with mean of p_k over half B only,
                then symmetrized (swap halves, average).
                  cv_both  : all 24 basis functions (12 dirs x {deg4, deg6})
                  cv_deg4  : the 12 degree-4 functions only
                  cv_deg6  : the 12 degree-6 functions only
  cv_both_nosplit  diagnostic: beta from ALL samples, correction from the
                full-sample mean (reports the bias the no-split shortcut
                introduces).

Basis (weight-derived, never truth-derived): directions a_k = top 8
input-space singular directions of the first-layer weight matrix (computed
once per net in f64) + 4 fixed He-random control directions (seed 191042,
shared across nets).  Basis functions with n = 256:
  p4_a(u) = (a.u)^4 - 3/(n(n+2))
  p6_a(u) = (a.u)^6 - 15/(n(n+2)(n+4))
each normalized to unit sample-std (scale-invariant for the estimator:
beta ~ cov/var absorbs any column scaling exactly).

Convention note (documented deviation ledger in M191_G0B_NOTES.md): the code
stores the first layer as weights[0] with shape (in, out), i.e. the
transpose of the math-convention W_1.  "Top right singular vectors of W_1"
therefore = the top LEFT singular vectors (columns of U) of weights[0]
= the input-space directions of largest first-layer gain.

Gates (predeclared): KILL if panel-MSE reduction < 10% (ratio > 0.90);
PROMOTE if >= 15% with bootstrap 95% CI excluding 10% (upper < 0.90).
Gate arm: cv_both (split-sample).  deg-4/deg-6 split reported regardless.

Firewall: synthetic He nets only; kerdock_phases.npz + m181 truth/partial
caches loaded READ-ONLY; frozen sources imported, never edited; writes
confined to pb1_premise_battery; plain numpy (sanctioned G0 deviation);
no dataset/scorer/submission access; no git.

Usage:
  python run_m191_g0b.py probe    # timing probe, writes nothing
  python run_m191_g0b.py 101      # run/resume one net (checkpoint per rep)
  python run_m191_g0b.py          # run everything remaining + aggregate
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
N8A = HERE.parent / "n8a_rqmc_kerdock"
M181 = HERE.parent / "m181_terminal_smoothing"
sys.path.insert(0, str(N8A))
from run_n8a_gates import (  # noqa: E402  (read-only import)
    load_kerdock_directions, haar_rotation, he_mlp_weights,
    WIDTH, MEAN_CHI_256,
)

N = WIDTH                       # ambient dimension 256
DEPTH = 32
N_BASE = 126 * WIDTH            # 32,256 base directions
N_TOTAL = 2 * N_BASE            # 64,512 antipodal samples
NET_SEEDS = (101, 202, 303)
REPLICATES = 16                 # >= predeclared 12; matches m181 stacks
K_SVD = 8                       # top singular directions of W_1
K_CTRL = 4                      # fixed He-random control directions
CTRL_SEED = 191_042             # documented control-direction seed
SPLIT_SEED_BASE = 777_000       # half-split seed = base + net*1000 + rep
BOOTSTRAP_DRAWS = 4000
BOOT_SEED = 2026_08_08
KILL_REDUCTION = 0.10
PROMOTE_REDUCTION = 0.15

C4 = 3.0 / (N * (N + 2.0))                    # E[(a.u)^4], |a|=1, uniform
C6 = 15.0 / (N * (N + 2.0) * (N + 4.0))       # E[(a.u)^6]

VARIANTS = ("cv_both", "cv_deg4", "cv_deg6", "cv_both_nosplit")
DEG4_COLS = slice(0, K_SVD + K_CTRL)          # columns 0..11
DEG6_COLS = slice(K_SVD + K_CTRL, 2 * (K_SVD + K_CTRL))  # columns 12..23
SUBSETS = {"cv_both": slice(None), "cv_deg4": DEG4_COLS, "cv_deg6": DEG6_COLS}


def rot_seed(net_seed: int, rep: int) -> int:
    """Rotation-seed formula shared with n8a/m180/m181 (pairs the baseline
    bitwise with the cached m181 arm0 stacks)."""
    return 900_000 + net_seed * 1_000 + rep


# ------------------------------------------------------------------ basis
def basis_directions(w0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """12 unit basis directions: top-8 input-space singular directions of the
    first layer (f64 SVD, once per net) + 4 fixed He-random controls."""
    u, s, _ = np.linalg.svd(w0.astype(np.float64), full_matrices=False)
    a_svd = u[:, :K_SVD].T                       # (8, 256), unit rows
    rng = np.random.default_rng(CTRL_SEED)
    a_ctrl = rng.standard_normal((K_CTRL, N))
    a_ctrl /= np.linalg.norm(a_ctrl, axis=1, keepdims=True)
    return np.concatenate([a_svd, a_ctrl], axis=0), s[:K_SVD]


def basis_matrix(u_all: np.ndarray, dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """P: (N_TOTAL, 24) basis values, columns [12 x deg4 | 12 x deg6], each
    normalized to unit sample-std.  Also returns the pre-normalization
    column means (the design's raw quadrature error on each p, for the
    G0-a consistency check)."""
    t = u_all @ dirs.T                           # (M, 12) f64
    p4 = t ** 4 - C4
    p6 = t ** 6 - C6
    P = np.concatenate([p4, p6], axis=1)
    sd = P.std(axis=0, ddof=0)
    if np.any(sd <= 0.0):
        raise RuntimeError("degenerate basis column (zero sample-std)")
    P /= sd
    return P, P.mean(axis=0)


# ---------------------------------------------------------------- forward
def forward_final(weights: list[np.ndarray], points: np.ndarray) -> np.ndarray:
    """Antipodal ReLU forward, final-layer activations kept per-sample.
    Identical op order to m181 forward_terminal + arm0 (rows [0,N_BASE) are
    +points, rows [N_BASE, 2N_BASE) the antipodal partners)."""
    first = points @ weights[0]
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    return act                                    # (N_TOTAL, 256) f32


# ------------------------------------------------------------------- CV
def univariate_betas(F: np.ndarray, P: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """beta_kj = cov(f_j, p_k) / var(p_k) on the rows in idx (exactly the
    predeclared per-k univariate form, NOT a joint fit)."""
    Fh = F[idx]
    Ph = P[idx]
    Fc = Fh - Fh.mean(axis=0)
    Pc = Ph - Ph.mean(axis=0)
    m = len(idx) - 1
    cov = Pc.T @ Fc / m                          # (24, 256)
    var = np.einsum("sk,sk->k", Pc, Pc) / m      # (24,)
    return cov / var[:, None]


def joint_r2(F: np.ndarray, P: np.ndarray, cols: slice) -> np.ndarray:
    """Per-neuron R^2 of f_j on the selected p_k's (joint least squares over
    all samples) -- the predeclared mechanism diagnostic."""
    Pc = P[:, cols] - P[:, cols].mean(axis=0)
    Fc = F - F.mean(axis=0)
    coef, *_ = np.linalg.lstsq(Pc, Fc, rcond=None)
    C = Pc.T @ Fc
    explained = np.einsum("kj,kj->j", C, coef)
    total = np.einsum("sj,sj->j", Fc, Fc)
    # dead final neurons (all-zero activations, total variance 0) explain
    # nothing and get R^2 = 0 rather than 0/0 = NaN
    return np.divide(explained, total,
                     out=np.zeros_like(total), where=total > 0.0)  # (256,)


# ---------------------------------------------------------------- per net
def run_net(net_seed: int, kerdock: np.ndarray) -> None:
    weights = he_mlp_weights(net_seed)
    dirs, top_sv = basis_directions(weights[0])
    path = HERE / f"m191_g0b_partial_net{net_seed}.npz"
    keys = ("baseline",) + VARIANTS
    if path.exists():
        d = np.load(path)
        stacks = {k: list(d[k]) for k in keys}
        r2 = {k: list(d[f"r2_{k}"]) for k in ("both", "deg4", "deg6")}
        pmeans = list(d["pmeans_raw"])
        done = len(stacks["baseline"])
        if done >= REPLICATES:
            print(f"net {net_seed}: already complete ({done} reps)", flush=True)
            return
        print(f"net {net_seed}: resuming at rep {done}/{REPLICATES}", flush=True)
    else:
        stacks = {k: [] for k in keys}
        r2 = {k: [] for k in ("both", "deg4", "deg6")}
        pmeans = []
        done = 0

    for rep in range(done, REPLICATES):
        t0 = time.perf_counter()
        rot = haar_rotation(rot_seed(net_seed, rep))
        points = (kerdock @ rot.T).astype(np.float32)     # (32256, 256)
        F = forward_final(weights, points).astype(np.float64)
        fhat = F.mean(axis=0)
        t1 = time.perf_counter()

        u_all = np.concatenate([points, -points]).astype(np.float64)
        u_all /= np.linalg.norm(u_all, axis=1, keepdims=True)  # exact unit
        P, pmean_raw = basis_matrix(u_all, dirs)
        pmeans.append(pmean_raw)

        perm = np.random.default_rng(
            SPLIT_SEED_BASE + net_seed * 1_000 + rep
        ).permutation(N_TOTAL)
        half_a, half_b = perm[: N_TOTAL // 2], perm[N_TOTAL // 2:]
        beta_a = univariate_betas(F, P, half_a)
        beta_b = univariate_betas(F, P, half_b)
        beta_full = univariate_betas(F, P, np.arange(N_TOTAL))
        mean_a = P[half_a].mean(axis=0)
        mean_b = P[half_b].mean(axis=0)
        mean_all = P.mean(axis=0)

        stacks["baseline"].append(fhat)
        for v in ("cv_both", "cv_deg4", "cv_deg6"):
            s = SUBSETS[v]
            corr = 0.5 * (beta_a[s].T @ mean_b[s] + beta_b[s].T @ mean_a[s])
            stacks[v].append(fhat - corr)
        stacks["cv_both_nosplit"].append(
            fhat - beta_full.T @ mean_all
        )
        for name, cols in (("both", slice(None)), ("deg4", DEG4_COLS),
                           ("deg6", DEG6_COLS)):
            r2[name].append(joint_r2(F, P, cols))
        t2 = time.perf_counter()

        np.savez(
            path,
            **{k: np.stack(stacks[k]) for k in keys},
            **{f"r2_{k}": np.stack(r2[k]) for k in ("both", "deg4", "deg6")},
            pmeans_raw=np.stack(pmeans),
            top_singular_values=top_sv,
        )
        print(f"  net {net_seed} rep {rep + 1}/{REPLICATES}: forward "
              f"{t1 - t0:.1f}s cv+r2 {t2 - t1:.1f}s "
              f"r2_both={float(np.mean(r2['both'][-1])):.2e}", flush=True)
    print(f"net {net_seed}: complete ({REPLICATES} reps)", flush=True)


# -------------------------------------------------------------- aggregate
def decompose(est: np.ndarray, truth: np.ndarray, noise: float) -> dict:
    """N8c decomposition verbatim (m181): bias^2 = MSE - var(ddof=1) - noise."""
    sq = (est - truth[None]) ** 2
    mse = float(sq.mean())
    var1 = float(np.var(est, axis=0, ddof=1).mean())
    return {
        "mse_raw": mse,
        "mse_noise_subtracted": mse - noise,
        "variance_ddof1": var1,
        "bias2": mse - var1 - noise,
        "bias_share_of_raw_mse": (mse - var1 - noise) / mse,
    }


def aggregate(partials: dict, truths: dict) -> dict:
    out: dict = {"net_rows": [], "variant_summary": {}, "floored_draws": 0,
                 "m181_arm0_crosscheck": {}, "r2_summary": {},
                 "quadrature_check_vs_g0a": {}}

    lognets: dict[str, list[float]] = {v: [] for v in VARIANTS}
    for net_seed in NET_SEEDS:
        arrs, truth = partials[net_seed], truths[net_seed]
        noise = float(truth["noise_final"])
        tmeans = truth["means"]
        row: dict = {"net_seed": net_seed, "truth_noise_final": noise}
        dec0 = decompose(arrs["baseline"], tmeans, noise)
        row["baseline"] = dec0
        base = dec0["mse_noise_subtracted"]
        for v in VARIANTS:
            dec = decompose(arrs[v], tmeans, noise)
            dec["ratio_vs_baseline_noise_subtracted"] = (
                dec["mse_noise_subtracted"] / base
            )
            row[v] = dec
            lognets[v].append(math.log(dec["mse_noise_subtracted"] / base))
        out["net_rows"].append(row)

        # cached-reference cross-check: baseline must reproduce m181 arm0
        ref = np.load(M181 / f"m181_g0_partial_net{net_seed}.npz")["arm0_baseline"]
        diff = float(np.max(np.abs(arrs["baseline"] - ref)))
        out["m181_arm0_crosscheck"][str(net_seed)] = diff

        out["r2_summary"][str(net_seed)] = {
            k: float(np.mean(arrs[f"r2_{k}"])) for k in ("both", "deg4", "deg6")
        }
        pm = arrs["pmeans_raw"]                   # (reps, 24) unit-std columns
        iid_rms = 1.0 / math.sqrt(N_TOTAL)
        out["quadrature_check_vs_g0a"][str(net_seed)] = {
            "deg4_rms_over_iid": float(
                np.sqrt(np.mean(pm[:, DEG4_COLS] ** 2)) / iid_rms),
            "deg6_rms_over_iid": float(
                np.sqrt(np.mean(pm[:, DEG6_COLS] ** 2)) / iid_rms),
        }

    # paired bootstrap over rotation-seed indices, shared per draw (m181 form)
    boot_rng = np.random.default_rng(BOOT_SEED)
    boots: dict[str, list[float]] = {v: [] for v in VARIANTS}
    floor_hits = 0
    for _ in range(BOOTSTRAP_DRAWS):
        logs: dict[str, list[float]] = {v: [] for v in VARIANTS}
        for net_seed in NET_SEEDS:
            arrs, truth = partials[net_seed], truths[net_seed]
            noise = float(truth["noise_final"])
            tmeans = truth["means"]
            idx = boot_rng.integers(0, REPLICATES, size=REPLICATES)
            mses = {}
            for v in ("baseline",) + VARIANTS:
                m = float(((arrs[v][idx] - tmeans[None]) ** 2).mean()) - noise
                if m <= 0.0:
                    m = 1e-18
                    floor_hits += 1
                mses[v] = m
            for v in VARIANTS:
                logs[v].append(math.log(mses[v] / mses["baseline"]))
        for v in VARIANTS:
            boots[v].append(math.exp(float(np.mean(logs[v]))))
    out["floored_draws"] = floor_hits

    for v in VARIANTS:
        agg = math.exp(float(np.mean(lognets[v])))
        ci = (float(np.percentile(boots[v], 2.5)),
              float(np.percentile(boots[v], 97.5)))
        reduction = 1.0 - agg
        out["variant_summary"][v] = {
            "aggregate_ratio_geomean": agg,
            "reduction_vs_baseline": reduction,
            "bootstrap_ci_95_ratio": ci,
        }
        print(f"{v}: ratio {agg:.5f} (reduction {100 * reduction:+.2f}%), "
              f"95% CI [{ci[0]:.5f}, {ci[1]:.5f}]", flush=True)

    # gate on the predeclared primary arm: cv_both (split-sample)
    s = out["variant_summary"]["cv_both"]
    red, ci = s["reduction_vs_baseline"], s["bootstrap_ci_95_ratio"]
    if red < KILL_REDUCTION:
        gate = "KILL"
    elif red >= PROMOTE_REDUCTION and ci[1] < 1.0 - KILL_REDUCTION:
        gate = "PROMOTE"
    else:
        gate = "SURVIVES-KILL-NOT-PROMOTABLE"
    out["gate_arm"] = "cv_both"
    out["gate"] = gate
    return out


# ------------------------------------------------------------------ probe
def probe() -> None:
    kerdock = load_kerdock_directions()
    weights = he_mlp_weights(101)
    dirs, sv = basis_directions(weights[0])
    print(f"probe: top-8 singular values of W_1: {np.round(sv, 4)}", flush=True)
    t0 = time.perf_counter()
    rot = haar_rotation(rot_seed(101, 0))
    points = (kerdock @ rot.T).astype(np.float32)
    F = forward_final(weights, points).astype(np.float64)
    fwd_s = time.perf_counter() - t0
    ref = np.load(M181 / "m181_g0_partial_net101.npz")["arm0_baseline"][0]
    diff = float(np.max(np.abs(F.mean(axis=0) - ref)))
    print(f"probe: forward {fwd_s:.1f}s; baseline vs m181 arm0 rep0 "
          f"max|diff| = {diff:.2e}", flush=True)
    t0 = time.perf_counter()
    u_all = np.concatenate([points, -points]).astype(np.float64)
    u_all /= np.linalg.norm(u_all, axis=1, keepdims=True)
    P, pmean = basis_matrix(u_all, dirs)
    iid = 1.0 / math.sqrt(N_TOTAL)
    print(f"probe: basis {time.perf_counter() - t0:.1f}s; "
          f"deg4 |mean|/iid rms {np.sqrt(np.mean(pmean[DEG4_COLS]**2))/iid:.3f}, "
          f"deg6 {np.sqrt(np.mean(pmean[DEG6_COLS]**2))/iid:.3f} "
          f"(G0-a: ~0.10-0.11, ~0.35-0.43)", flush=True)
    t0 = time.perf_counter()
    r2 = joint_r2(F, P, slice(None))
    print(f"probe: joint R^2 {time.perf_counter() - t0:.1f}s; "
          f"mean R^2(both) = {float(np.mean(r2)):.3e}", flush=True)
    per_net = (fwd_s + 3.0) * REPLICATES
    print(f"probe: projected ~{per_net:.0f}s per net at {REPLICATES} reps",
          flush=True)


# ------------------------------------------------------------------- main
def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "probe":
        probe()
        return
    only = {int(x) for x in sys.argv[1].split(",")} if len(sys.argv) > 1 else None

    kerdock = load_kerdock_directions()
    partials: dict[int, dict] = {}
    truths: dict[int, dict] = {}
    for net_seed in NET_SEEDS:
        path = HERE / f"m191_g0b_partial_net{net_seed}.npz"
        if path.exists() and len(np.load(path)["baseline"]) >= REPLICATES:
            pass
        elif only is not None and net_seed not in only:
            continue
        else:
            run_net(net_seed, kerdock)
        partials[net_seed] = dict(np.load(path))
        truths[net_seed] = dict(np.load(M181 / f"m181_truth_net{net_seed}.npz"))

    if set(partials) != set(NET_SEEDS):
        print(f"nets remaining: {sorted(set(NET_SEEDS) - set(partials))} "
              "-- rerun to continue", flush=True)
        return

    g0b = aggregate(partials, truths)
    results = {
        "date": "2026-08-08",
        "predeclaration": "M191_HARMONIC_PREDECLARATION.md (G0-b)",
        "config": {
            "width": N, "depth": DEPTH, "n_total_antipodal": N_TOTAL,
            "net_seeds": list(NET_SEEDS), "replicates": REPLICATES,
            "rotation_seed_formula": "900000 + net_seed*1000 + rep",
            "basis": f"top-{K_SVD} input-space singular directions of W_1 "
                     f"(f64 SVD of weights[0], columns of U) + {K_CTRL} fixed "
                     f"He-random controls (seed {CTRL_SEED}); "
                     "p4 = (a.u)^4 - 3/(n(n+2)), "
                     "p6 = (a.u)^6 - 15/(n(n+2)(n+4)), unit sample-std",
            "split": "uniform random permutation of all 64512 samples, "
                     f"halves 32256/32256, seed {SPLIT_SEED_BASE}+net*1000+rep; "
                     "beta = cov/var per k (univariate, predeclared form); "
                     "symmetrized swap-halves average",
            "truth": "m181_truth_net*.npz (3.5M iid MC, cached, read-only), "
                     "measured noise floor subtracted",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "kill_reduction": KILL_REDUCTION,
            "promote_reduction": PROMOTE_REDUCTION,
        },
        "firewall": (
            "synthetic He nets only; kerdock_phases.npz + m181 caches read-"
            "only; frozen sources imported unmodified; writes confined to "
            "pb1_premise_battery; plain numpy (sanctioned G0 deviation); "
            "no dataset/scorer/submission; no git"
        ),
        "g0b": g0b,
    }
    s = g0b["variant_summary"]["cv_both"]
    results["verdict"] = (
        f"{g0b['gate']} at G0-b: cv_both panel ratio "
        f"{s['aggregate_ratio_geomean']:.5f} "
        f"(reduction {100 * s['reduction_vs_baseline']:+.2f}%, "
        f"CI [{s['bootstrap_ci_95_ratio'][0]:.5f}, "
        f"{s['bootstrap_ci_95_ratio'][1]:.5f}]) vs kill bar 10% / promote "
        f"bar 15%"
    )
    out_path = HERE / "m191_g0b_results.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"\nVERDICT: {results['verdict']}")
    print(f"results written to {out_path}")


if __name__ == "__main__":
    main()
