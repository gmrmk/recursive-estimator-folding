"""S3 G0b -- coupled cross-net rotation ensembles vs independent Haar.

Ledger id: s3_cross_net_coupled_rotations.  Generated-only and response-free:
no dataset, no hosted truth, no scorer, no leaderboard artifact is read.
Synthetic He nets with cached MC truth computed here.

Reduced simulation blessed by the predeclaration: width 64, depth 8, K=12
nets, one fixed orthonormal frame (64 directions) at the champion's
radial-conditioning radius (mean chi_64), rotated per net.  Per-net estimate
is the mean over directions and neurons of the final post-ReLU activations;
per-net error is estimate minus cached MC truth.  Arms differ ONLY in the
JOINT law of the per-net rotations; every arm's marginal is exactly Haar on
O(64) by construction.

Arms (predeclared):
  indep      : K iid Haar rotations (sign-fixed QR of iid Gaussian).
  block_orth : one Haar Stiefel frame Q in V_64(R^(K*64)) (sign-fixed reduced
               QR of a (K*64)x64 Gaussian), sliced row-wise into K 64x64
               blocks; each block's orthogonal polar factor is the net's
               rotation.  Two-sided orthogonal invariance of the block law
               makes each polar factor exactly Haar; jointly the blocks are
               repulsive (sum of B_k^T B_k = I).
  antithetic : K/2 iid Haar draws; pairs (R, -R).  -R is the maximally
               distant rotation (trace inner product -64); negation preserves
               Haar measure, so marginals are exact.

Primary metric: Var over replicate ensembles of the across-net mean error,
per arm.  PASS gate: >=10% suite-mean variance reduction in a coupled arm
with per-net marginal variances unchanged (95% bootstrap CIs of per-net
variance ratios covering 1 for >=11/12 nets in the passing arm).

Cross-checks (two-signal discipline):
  1. cov-decomposition: Var(mean) recomputed as (1/K^2) 1' Cov 1.
  2. split-half ratios on reps [0:1000] and [1000:2000].
  3. bitwise repeat of the first 50 replicates of every arm.
  4. truth recomputed from a second independent MC stream.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

WIDTH = 64
DEPTH = 8
K_NETS = 12
N_DIRECTIONS = WIDTH          # one frame = one 64x64 orthogonal matrix
N_REP = 2000
BLOCK = 250                   # replicates per forward-pass batch
N_TRUTH = 200_000
TRUTH_CHUNK = 50_000
BOOT = 4000
BOOT_SEED = 20260809
NET_SEED_BASE = 3_000_001
TRUTH_SEED_BASE = 4_000_000
TRUTH2_SEED_BASE = 5_000_000
FRAME_SEED = 777

MEAN_CHI_64 = math.exp(
    0.5 * math.log(2.0) + math.lgamma((WIDTH + 1.0) / 2.0) - math.lgamma(WIDTH / 2.0)
)

ARMS = ("indep", "block_orth", "antithetic")


def he_net(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


def forward_mean_per_rep(x: np.ndarray, weights: list[np.ndarray], reps: int) -> np.ndarray:
    """x: (reps*N_DIRECTIONS, WIDTH) inputs -> per-rep scalar mean of final ReLU."""
    h = x
    for w in weights:
        h = np.maximum(h @ w, 0.0)
    return h.reshape(reps, N_DIRECTIONS, WIDTH).mean(axis=(1, 2)).astype(np.float64)


def truth_mc(weights: list[np.ndarray], seed: int) -> float:
    rng = np.random.default_rng(seed)
    total = 0.0
    n_done = 0
    while n_done < N_TRUTH:
        n = min(TRUTH_CHUNK, N_TRUTH - n_done)
        h = rng.standard_normal((n, WIDTH), dtype=np.float32)
        for w in weights:
            h = np.maximum(h @ w, 0.0)
        total += float(h.mean(dtype=np.float64)) * n
        n_done += n
    return total / N_TRUTH


def sign_fixed_qr(g: np.ndarray) -> np.ndarray:
    """Reduced QR with the R-diagonal sign fix (Haar for iid Gaussian input)."""
    q, r = np.linalg.qr(g)
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    return q * signs[None, :]


def haar64(rng: np.random.Generator) -> np.ndarray:
    return sign_fixed_qr(rng.standard_normal((WIDTH, WIDTH)))


def polar_orthogonal(b: np.ndarray) -> np.ndarray:
    u, _, vt = np.linalg.svd(b)
    return u @ vt


def rotations_for_rep(arm: str, rep: int) -> np.ndarray:
    """(K_NETS, WIDTH, WIDTH) rotations for one replicate ensemble."""
    rng = np.random.default_rng([rep, ARMS.index(arm), 424242])
    if arm == "indep":
        return np.stack([haar64(rng) for _ in range(K_NETS)])
    if arm == "block_orth":
        g = rng.standard_normal((K_NETS * WIDTH, WIDTH))
        q = sign_fixed_qr(g)                      # Haar Stiefel frame
        blocks = q.reshape(K_NETS, WIDTH, WIDTH)
        return np.stack([polar_orthogonal(b) for b in blocks])
    if arm == "antithetic":
        halves = [haar64(rng) for _ in range(K_NETS // 2)]
        out = []
        for r in halves:
            out.append(r)
            out.append(-r)
        return np.stack(out)
    raise ValueError(arm)


def run_arm(arm: str, nets: list[list[np.ndarray]], truths: np.ndarray,
            frame: np.ndarray, n_rep: int, rep_offset: int = 0) -> np.ndarray:
    """Return err matrix (n_rep, K_NETS)."""
    err = np.empty((n_rep, K_NETS), dtype=np.float64)
    scaled_frame = (MEAN_CHI_64 * frame).astype(np.float64)
    done = 0
    t0 = time.perf_counter()
    while done < n_rep:
        nb = min(BLOCK, n_rep - done)
        rots = np.stack(
            [rotations_for_rep(arm, rep_offset + done + j) for j in range(nb)]
        )  # (nb, K, W, W)
        for m in range(K_NETS):
            # X per rep: MEAN_CHI * U0 @ R_m^T  -> stack reps
            x = np.einsum("ij,rkj->rik", scaled_frame, rots[:, m, :, :])
            x = x.reshape(nb * N_DIRECTIONS, WIDTH).astype(np.float32)
            err[done:done + nb, m] = (
                forward_mean_per_rep(x, nets[m], nb) - truths[m]
            )
        done += nb
        print(f"  [{arm}] reps {done}/{n_rep}  ({time.perf_counter() - t0:.1f}s)",
              flush=True)
    return err


def var_mean_two_ways(err: np.ndarray) -> tuple[float, float]:
    suite = err.mean(axis=1)
    direct = float(np.var(suite, ddof=1))
    cov = np.cov(err, rowvar=False)
    quad = float(np.ones(K_NETS) @ cov @ np.ones(K_NETS) / K_NETS**2)
    return direct, quad


def bootstrap_ratio_ci(num_series: np.ndarray, den_series: np.ndarray,
                       rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    """95% CI for Var(num)/Var(den); independent resampling (arms independent)."""
    n = num_series.shape[0]
    ratios = np.empty(n_boot)
    for b in range(n_boot):
        i = rng.integers(0, n, n)
        j = rng.integers(0, n, n)
        ratios[b] = np.var(num_series[i], ddof=1) / np.var(den_series[j], ddof=1)
    return float(np.quantile(ratios, 0.025)), float(np.quantile(ratios, 0.975))


def main() -> None:
    t_start = time.perf_counter()
    print("Building nets and cached truth...", flush=True)
    nets = [he_net(NET_SEED_BASE + m) for m in range(K_NETS)]
    truths = np.array(
        [truth_mc(nets[m], TRUTH_SEED_BASE + m) for m in range(K_NETS)]
    )
    truths2 = np.array(
        [truth_mc(nets[m], TRUTH2_SEED_BASE + m) for m in range(K_NETS)]
    )
    truth_gap = np.abs(truths - truths2)
    print(f"truth cross-check max |t1-t2| = {truth_gap.max():.3e}", flush=True)

    frame = sign_fixed_qr(
        np.random.default_rng(FRAME_SEED).standard_normal((WIDTH, WIDTH))
    )

    errs: dict[str, np.ndarray] = {}
    for arm in ARMS:
        print(f"Running arm {arm}...", flush=True)
        errs[arm] = run_arm(arm, nets, truths, frame, N_REP)

    # Bitwise repeat: first full block of every arm, regenerated from seeds
    # with the SAME batch size (float32 matmul rounding depends on batching,
    # so the repeat must follow the identical execution path).
    bitwise_ok = {}
    for arm in ARMS:
        repeat = run_arm(arm, nets, truths, frame, BLOCK)
        bitwise_ok[arm] = bool(np.array_equal(repeat, errs[arm][:BLOCK]))
    print(f"bitwise repeat identical: {bitwise_ok}", flush=True)

    np.savez_compressed(
        HERE / "s3_errors.npz",
        **{f"err_{arm}": errs[arm] for arm in ARMS},
        truths=truths,
    )

    rng_boot = np.random.default_rng(BOOT_SEED)
    results: dict = {
        "ledger_id": "s3_cross_net_coupled_rotations",
        "config": {
            "width": WIDTH, "depth": DEPTH, "k_nets": K_NETS,
            "n_directions": N_DIRECTIONS, "n_rep": N_REP,
            "n_truth": N_TRUTH, "mean_chi_64": MEAN_CHI_64,
            "net_seed_base": NET_SEED_BASE, "frame_seed": FRAME_SEED,
            "boot": BOOT, "boot_seed": BOOT_SEED,
        },
        "truth": {
            "values": truths.tolist(),
            "recheck_max_abs_gap": float(truth_gap.max()),
        },
        "arms": {},
        "cross_checks": {"bitwise_repeat_identical": bitwise_ok},
    }

    suite_var = {}
    for arm in ARMS:
        direct, quad = var_mean_two_ways(errs[arm])
        suite_var[arm] = direct
        per_net_var = np.var(errs[arm], axis=0, ddof=1)
        per_net_mean = errs[arm].mean(axis=0)
        h1, h2 = errs[arm][:N_REP // 2], errs[arm][N_REP // 2:]
        results["arms"][arm] = {
            "suite_mean_error_var": direct,
            "suite_mean_error_var_cov_decomposition": quad,
            "cov_decomposition_abs_gap": abs(direct - quad),
            "suite_mean_error_mean": float(errs[arm].mean(axis=1).mean()),
            "per_net_error_var": per_net_var.tolist(),
            "per_net_error_mean": per_net_mean.tolist(),
            "split_half_suite_var": [
                float(np.var(h1.mean(axis=1), ddof=1)),
                float(np.var(h2.mean(axis=1), ddof=1)),
            ],
        }

    indep_suite = errs["indep"].mean(axis=1)
    gate_effect = {}
    for arm in ("block_orth", "antithetic"):
        coupled_suite = errs[arm].mean(axis=1)
        ratio = suite_var[arm] / suite_var["indep"]
        lo, hi = bootstrap_ratio_ci(coupled_suite, indep_suite, rng_boot, BOOT)
        # per-net marginal ratios with CIs
        per_net = []
        n_cover = 0
        for m in range(K_NETS):
            r_m = float(np.var(errs[arm][:, m], ddof=1)
                        / np.var(errs["indep"][:, m], ddof=1))
            lo_m, hi_m = bootstrap_ratio_ci(
                errs[arm][:, m], errs["indep"][:, m], rng_boot, 2000
            )
            covers = bool(lo_m <= 1.0 <= hi_m)
            n_cover += covers
            per_net.append({"net": m, "var_ratio": r_m,
                            "ci95": [lo_m, hi_m], "covers_1": covers})
        h1r = (np.var(errs[arm][:N_REP // 2].mean(axis=1), ddof=1)
               / np.var(errs["indep"][:N_REP // 2].mean(axis=1), ddof=1))
        h2r = (np.var(errs[arm][N_REP // 2:].mean(axis=1), ddof=1)
               / np.var(errs["indep"][N_REP // 2:].mean(axis=1), ddof=1))
        gate_effect[arm] = {
            "suite_var_ratio": ratio,
            "suite_var_ratio_ci95": [lo, hi],
            "variance_reduction": 1.0 - ratio,
            "split_half_ratios": [float(h1r), float(h2r)],
            "per_net_marginal_ratios": per_net,
            "marginals_unchanged_11_of_12": bool(n_cover >= 11),
            "n_marginal_cis_covering_1": n_cover,
            "meets_10pct_reduction": bool(1.0 - ratio >= 0.10),
        }

    passing = [a for a, g in gate_effect.items()
               if g["meets_10pct_reduction"] and g["marginals_unchanged_11_of_12"]]
    results["gate_g0b"] = {
        "effect": gate_effect,
        "passing_arms": passing,
        "verdict": "PASS" if passing else "KILL",
    }
    results["runtime_seconds"] = time.perf_counter() - t_start

    out = HERE / "s3_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out}")
    print(f"G0b verdict: {results['gate_g0b']['verdict']}")
    for arm, g in gate_effect.items():
        print(f"  {arm}: ratio={g['suite_var_ratio']:.4f} "
              f"CI95=[{g['suite_var_ratio_ci95'][0]:.4f},"
              f"{g['suite_var_ratio_ci95'][1]:.4f}] "
              f"reduction={g['variance_reduction']*100:.2f}% "
              f"marginal_CIs_cover_1={g['n_marginal_cis_covering_1']}/12")


if __name__ == "__main__":
    main()
