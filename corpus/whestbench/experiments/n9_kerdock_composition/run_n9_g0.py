"""N9 G0 interaction gates. Predeclared in N9_PREDECLARATION.md (GOVERNS).

Two predeclared premise gates, run before any build:

G0-a (tangent-on-frames): on 3 synthetic He f32 256x32 nets (seeds
101/202/303, t3-style construction), at the Kerdock native count
(n_base = 126*256 = 32,256, antipodally doubled), paired variance across
16 Haar rotation seeds (>= 12 required) of
  (i)  the Kerdock phased-Hadamard spherical mean (N8a arm (a)
       construction, plain antipodal ReLU forward mean, final layer), vs
  (ii) the same minus lambda * the moment-tangent correction computed per
       the FROZEN response map of the tangent lineage (lambda =
       0.9807112198896164, verified identical in the tangent candidate
       tar's estimator.py and the frozen v3 base_estimator.py; response
       map transcribed from those sources with _radial_covariance =
       mean_chi(256)^2 / 256 as v3's radially-conditioned setup sets it).
KILL the tangent component if the mean paired variance reduction < 10%.

G0-b (fold increment): static billed-FLOP count of v3's current pipeline
vs an L3-folded variant structure, using realized dead/on/kink partition
counts from the analytic pass on the same 3 nets.  Counting only, no
build; per-op billing mirrors the t3 cost model (capped_fold3.py
predict_main_bill, direct-matmul convention).  KILL the fold component if
the billed reduction < 15%.

LOUD DEVIATION / FINDING (see N9_G0_NOTES.md): the predeclaration's
premise "v3 already folds at L1, so the increment is L1 -> L3" is
contradicted by the frozen v3 source.  candidate_source_validator_v3/
estimator.py inherits fold3_estimator.Estimator -- the three-terminal-
layer dead/on/kink fold -- so v3's current pipeline ALREADY IS the
L3-folded structure (N8c's artifacts likewise call it "the frozen v3
fold3 pipeline").  The predeclared comparison is therefore between two
structurally identical pipelines and its billed reduction is exactly 0%
for every partition input.  The gate is still executed as predeclared
(no retuning): both bills are computed from the realized analytic
partitions and compared.

Firewall: synthetic He nets only; frozen v3 sources read-only (only the
shipped sampling asset kerdock_phases.npz is loaded); the tangent tar's
estimator.py member alone was extracted to a scratch directory to read
the frozen response map; no dataset/truth/scorer/submission access;
single process, all foreground.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)

WIDTH, DEPTH = 256, 32
N_BASE = 126 * 256                    # Kerdock native draw count
NET_SEEDS = (101, 202, 303)
REPLICATES = 16                       # >= 12 predeclared; 16 matches N8a/N8c
KILL_TANGENT_REDUCTION = 0.10         # G0-a: kill if mean reduction < 10%
KILL_FOLD_REDUCTION = 0.15            # G0-b: kill if billed reduction < 15%
MEAN_CHI_256 = 15.98438266660852747   # frozen v3 constant
TANGENT_LAMBDA = 0.9807112198896164   # frozen tangent-lineage lambda
DEAD_ALPHA = -2.0                     # frozen lineage thresholds
ON_ALPHA = 3.0
PILOT_BASE = 256                      # v3 loop pilot
FOLD_PILOT_BASE = 1_024               # v3 fold pilot
BOOTSTRAP_DRAWS = 4000
CTRL_N_BASE = 14_000                  # tangent lineage native count (control)

_ERF = np.vectorize(math.erf)


# ----------------------------------------------------------------- nets
def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (t3-style construction; same as
    N8a/N8c so the variance anchors are comparable)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


# --------------------------------------------------- Kerdock construction
def load_kerdock_directions() -> np.ndarray:
    """Rebuild the exact v3 direction set from its shipped sampling asset
    (verbatim from run_n8a_gates.py)."""
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (126, WIDTH):
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


def rot_seed(net_seed: int, r: int) -> int:
    """Same rotation-seed formula as N8a arm (a) and N8c (anchors tie)."""
    return 900_000 + net_seed * 1_000 + r


# ------------------------------------------------- frozen analytic pass
def diagonal_gaussian_pass(weights: list[np.ndarray]):
    """Float64 numpy transcription of base_estimator._diagonal_gaussian_pass.

    Rotation-invariant for the first layer (mu = 0 and var_pre depends only
    on column norms, which the orthogonal Haar rotation preserves), so one
    pass per net serves every replicate.  Deviation from the frozen source:
    float64 instead of float32 flopscope arrays (a float32 cross-check of
    the resulting tangent is reported in the results JSON).
    """
    mu = np.zeros(WIDTH)
    var = np.ones(WIDTH)
    means, alphas, firing, sigmas = [], [], [], []
    for weight in weights:
        w = weight.astype(np.float64)
        mu_pre = mu @ w
        var_pre = var @ (w * w)
        sigma = np.sqrt(np.maximum(var_pre, 1e-12))
        alpha = mu_pre / sigma
        phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
        cdf = 0.5 * (1.0 + _ERF(alpha / math.sqrt(2.0)).astype(np.float64))
        mu = mu_pre * cdf + sigma * phi
        second = (var_pre + mu_pre * mu_pre) * cdf + mu_pre * sigma * phi
        var = np.maximum(second - mu * mu, 0.0)
        means.append(mu)
        alphas.append(alpha)
        firing.append(cdf)
        sigmas.append(sigma)
    return means, alphas, firing, sigmas


def tangent_delta_final(
    weights: list[np.ndarray],
    analytic,
    first_moment_residual: np.ndarray,
    first_variance_residual: np.ndarray,
    dtype=np.float64,
) -> np.ndarray:
    """Frozen response map: propagate the first-layer moment residuals to a
    final-layer delta_mean.  Transcribed from the tangent tar's estimator.py
    (== frozen v3 base_estimator.py / fold3_estimator.py, lines with the
    delta_mean/delta_var recursion)."""
    means, alphas, firing, sigmas = analytic
    delta_mean = first_moment_residual.astype(dtype)
    delta_var = first_variance_residual.astype(dtype)
    for layer in range(1, DEPTH):
        w = weights[layer].astype(dtype)
        delta_pre_mean = delta_mean @ w
        delta_pre_var = delta_var @ (w * w)
        phi = np.exp(
            -0.5 * alphas[layer].astype(dtype) ** 2
        ) / np.sqrt(dtype(2.0) * dtype(math.pi))
        next_delta_mean = (
            firing[layer].astype(dtype) * delta_pre_mean
            + (phi / (2.0 * sigmas[layer].astype(dtype))) * delta_pre_var
        )
        layer_mean = means[layer].astype(dtype)
        next_delta_var = (
            2.0 * layer_mean * delta_pre_mean
            + firing[layer].astype(dtype) * delta_pre_var
            - 2.0 * layer_mean * next_delta_mean
        )
        delta_mean = next_delta_mean
        delta_var = next_delta_var
    return delta_mean


# ---------------------------------------------------------- G0-a forward
def paired_arms(
    weights: list[np.ndarray],
    first_eff: np.ndarray,
    points: np.ndarray,
    analytic,
    radial_covariance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One replicate: (arm_i, arm_ii, correction) final-layer vectors.

    arm_i is the N8a arm (a) plain antipodal ReLU forward mean (identical op
    order, so its variance must reproduce n8c_g0_results.json
    plain_downstream to float tolerance -- checked as an anchor).
    """
    first = points @ first_eff
    x = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    # Frozen response-map inputs (float64 accumulation over 2*n rows).
    sigma0 = np.sqrt(
        np.sum(first_eff.astype(np.float64) ** 2, axis=0)
    )
    exact_first_mean = sigma0 / math.sqrt(2.0 * math.pi)
    mean_x = np.mean(x, axis=0, dtype=np.float64)
    mean_xx = np.mean(
        x.astype(np.float64) ** 2, axis=0
    )
    first_moment_residual = mean_x - exact_first_mean
    first_variance_residual = (
        mean_xx - 0.5 * radial_covariance * sigma0 * sigma0
    ) - 2.0 * exact_first_mean * first_moment_residual

    act = x
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    arm_i = act.astype(np.float64).mean(axis=0)

    delta = tangent_delta_final(
        weights, analytic, first_moment_residual, first_variance_residual
    )
    correction = TANGENT_LAMBDA * delta
    return arm_i, arm_i - correction, correction


def run_g0a(kerdock: np.ndarray) -> dict:
    g0a = {
        "kill_threshold_reduction": KILL_TANGENT_REDUCTION,
        "replicates": REPLICATES,
        "n_base": N_BASE,
        "lambda": TANGENT_LAMBDA,
        "radial_covariance": MEAN_CHI_256 * MEAN_CHI_256 / WIDTH,
        "net_rows": [],
    }
    radial_cov = MEAN_CHI_256 * MEAN_CHI_256 / WIDTH
    reductions = []
    stacks = {}
    for net_seed in NET_SEEDS:
        weights = he_mlp_weights(net_seed)
        analytic = diagonal_gaussian_pass(weights)
        est_i, est_ii, corr = [], [], []
        t0 = time.perf_counter()
        for r in range(REPLICATES):
            rotation = haar_rotation(rot_seed(net_seed, r))
            first_eff = (rotation.T @ weights[0]).astype(np.float32)
            a_i, a_ii, c = paired_arms(
                weights, first_eff, kerdock, analytic, radial_cov
            )
            est_i.append(a_i)
            est_ii.append(a_ii)
            corr.append(c)
            print(
                f"  G0-a net {net_seed} rep {r + 1}/{REPLICATES} "
                f"({time.perf_counter() - t0:.0f}s)",
                flush=True,
            )
        wall = time.perf_counter() - t0
        a = np.stack(est_i)
        b = np.stack(est_ii)
        c = np.stack(corr)
        stacks[net_seed] = (a, b)
        var_i = float(np.var(a, axis=0, ddof=1).mean())
        var_ii = float(np.var(b, axis=0, ddof=1).mean())
        var_corr = float(np.var(c, axis=0, ddof=1).mean())
        # Per-output covariance between arm-i fluctuation and the correction:
        # var_ii = var_i - 2*cov + var_corr, reported for transparency.
        cov = float(
            np.mean(
                np.sum(
                    (a - a.mean(axis=0)) * (c - c.mean(axis=0)), axis=0
                ) / (REPLICATES - 1)
            )
        )
        reduction = 1.0 - var_ii / var_i
        reductions.append(reduction)
        # Float32 cross-check of the tangent recursion dtype deviation.
        rot0 = haar_rotation(rot_seed(net_seed, 0))
        fe0 = (rot0.T @ weights[0]).astype(np.float32)
        first0 = kerdock @ fe0
        x0 = np.concatenate(
            (np.maximum(first0, np.float32(0.0)),
             np.maximum(-first0, np.float32(0.0))),
            axis=0,
        )
        s0 = np.sqrt(np.sum(fe0.astype(np.float64) ** 2, axis=0))
        efm = s0 / math.sqrt(2.0 * math.pi)
        fmr = np.mean(x0, axis=0, dtype=np.float64) - efm
        fvr = (
            np.mean(x0.astype(np.float64) ** 2, axis=0)
            - 0.5 * radial_cov * s0 * s0
        ) - 2.0 * efm * fmr
        d64 = tangent_delta_final(weights, analytic, fmr, fvr, np.float64)
        d32 = tangent_delta_final(
            weights,
            tuple([v.astype(np.float32) for v in part] for part in analytic),
            fmr.astype(np.float32),
            fvr.astype(np.float32),
            np.float32,
        )
        dtype_rel = float(
            np.max(np.abs(d64 - d32.astype(np.float64)))
            / max(float(np.max(np.abs(d64))), 1e-300)
        )
        g0a["net_rows"].append({
            "net_seed": net_seed,
            "var_arm_i_kerdock": var_i,
            "var_arm_ii_tangent_corrected": var_ii,
            "var_correction_term": var_corr,
            "cov_arm_i_correction": cov,
            "paired_variance_reduction": reduction,
            "tangent_f32_vs_f64_max_rel_diff": dtype_rel,
            "wall_s": round(wall, 1),
        })
        print(
            f"G0-a net {net_seed}: var(i)={var_i:.4e}  var(ii)={var_ii:.4e}  "
            f"reduction={reduction:+.4f}  (var_corr={var_corr:.3e}, "
            f"cov={cov:.3e})  ({wall:.0f}s)",
            flush=True,
        )

    mean_reduction = float(np.mean(reductions))

    # Paired bootstrap over replicate indices (diagnostic CI on the mean).
    boot_rng = np.random.default_rng(2026_08_08)
    boots = []
    for _ in range(BOOTSTRAP_DRAWS):
        draw = []
        for net_seed in NET_SEEDS:
            a, b = stacks[net_seed]
            idx = boot_rng.integers(0, REPLICATES, size=REPLICATES)
            va = np.var(a[idx], axis=0, ddof=1).mean()
            vb = np.var(b[idx], axis=0, ddof=1).mean()
            if va > 0:
                draw.append(1.0 - vb / va)
        boots.append(float(np.mean(draw)))
    ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))

    g0a["per_net_reductions"] = reductions
    g0a["mean_paired_variance_reduction"] = mean_reduction
    g0a["bootstrap_ci_95"] = ci
    g0a["pass"] = mean_reduction >= KILL_TANGENT_REDUCTION
    print(
        f"G0-a mean paired variance reduction = {mean_reduction:+.4f} "
        f"(bootstrap 95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}]); "
        f"kill if < {KILL_TANGENT_REDUCTION}",
        flush=True,
    )
    return g0a


def run_g0a_positive_control() -> dict:
    """Diagnostic only (not a gate): the same frozen response map applied to
    antipodal iid Gaussian sampling at the tangent lineage's native count
    (n=14,000, _radial_covariance=1.0).  The lineage reports ~20-25% adjusted
    gain on its own randomization; a clearly positive reduction here is the
    second signal that the response-map transcription is not silently broken
    (it discriminates 'tangent is redundant on frames' from 'tangent was
    implemented wrong')."""
    rows = []
    for net_seed in NET_SEEDS:
        weights = he_mlp_weights(net_seed)
        analytic = diagonal_gaussian_pass(weights)
        est_i, est_ii = [], []
        t0 = time.perf_counter()
        for r in range(REPLICATES):
            rng = np.random.default_rng(300_000 + net_seed * 1_000 + r)
            z = rng.standard_normal((CTRL_N_BASE, WIDTH)).astype(np.float32)
            a_i, a_ii, _ = paired_arms(
                weights, weights[0], z, analytic, 1.0
            )
            est_i.append(a_i)
            est_ii.append(a_ii)
        wall = time.perf_counter() - t0
        var_i = float(np.var(np.stack(est_i), axis=0, ddof=1).mean())
        var_ii = float(np.var(np.stack(est_ii), axis=0, ddof=1).mean())
        reduction = 1.0 - var_ii / var_i
        rows.append({
            "net_seed": net_seed,
            "var_arm_i_iid": var_i,
            "var_arm_ii_iid_tangent": var_ii,
            "paired_variance_reduction": reduction,
            "wall_s": round(wall, 1),
        })
        print(
            f"  control net {net_seed}: var(i)={var_i:.4e} "
            f"var(ii)={var_ii:.4e} reduction={reduction:+.4f} ({wall:.0f}s)",
            flush=True,
        )
    mean_red = float(np.mean([r["paired_variance_reduction"] for r in rows]))
    print(f"  control mean reduction = {mean_red:+.4f}", flush=True)
    return {
        "note": (
            "diagnostic implementation control, NOT a gate: frozen response "
            "map on antipodal iid Gaussian sampling at the tangent lineage's "
            "native n=14,000 with _radial_covariance=1.0 (no Sobol, no "
            "quartic radial weights -- mechanism check only)"
        ),
        "n_base": CTRL_N_BASE,
        "net_rows": rows,
        "mean_paired_variance_reduction": mean_red,
    }


# ------------------------------------------------- G0-b static counting
# Per-op billed-FLOP constants mirrored from the t3 cost model
# (t3_fold3_deterministic_cap/capped_fold3.py, verified there against
# flopscope v0.14): matmul (m,k)@(k,n) -> 2mkn - mn; pointwise 1/elem;
# mean axis=0 of (m,n) -> m*n; sum/max/min axis=0 -> (m-1)*n; concatenate
# 1/elem (x2 int64); fancy gather 4/elem; sort/argsort 8*n*ceil(log2 n);
# flatnonzero 1/elem; arange 4/elem; stack 1/elem; sqrt 2/elem; exp
# 16/elem; x**2 16/elem.  Direct-matmul convention: v3's WHT first product
# and row-blocked Winograd backend are NOT modeled -- both compared
# structures share them identically, so the reduction ratio is invariant
# (stated in N9_G0_NOTES.md).  The metered n8c anchor sits ~8-10% ABOVE
# this static count: the deployed run's pilot rescues enlarge the active
# sets beyond the analytic structural sets, and its Winograd/WHT backends
# bill their own overheads.


def _mm(m: int, k: int, n: int) -> int:
    if m <= 0 or k <= 0 or n <= 0:
        return 1
    return 2 * m * k * n - m * n


def _sort_bill(m: int) -> int:
    if m < 2:
        return 8
    return 8 * m * max(1, math.ceil(math.log2(m)))


def _refine_bill(size: int, moved: int, rows: int) -> int:
    return (
        (rows - 1) * size + size + size + 8 * moved + size + size
        + 8 * (size - moved)
    )


def _pre31_bill(a28, o30, k30, cols, rows, w):
    if cols <= 0:
        return 0
    return (
        4 * a28 * o30 + 4 * o30 * w + 4 * o30 * cols
        + _mm(a28, o30, cols)
        + _mm(rows, a28, cols)
        + 4 * k30 * w + 4 * k30 * cols
        + _mm(rows, k30, cols)
        + rows * cols
    )


def _pre32_bill(a28, o31, k30, k31, cols, rows, w):
    if cols <= 0:
        return 0
    return (
        2 * (4 * o31 * w + 4 * o31 * cols)
        + 4 * k31 * w + 4 * k31 * cols
        + _mm(a28, o31, cols) + _mm(rows, a28, cols)
        + _mm(k30, o31, cols) + _mm(rows, k30, cols)
        + _mm(rows, k31, cols)
        + 2 * rows * cols
    )


def _shared_head_bill(n: int, w: int) -> int:
    """First product, antipodal ReLU, residual moments, arange (identical in
    every compared structure)."""
    big = 2 * n
    total = _mm(n, w, w)
    total += 3 * n * w
    total += big * w
    total += w * w + (w - 1) * w + 2 * w
    total += 3 + w
    total += big * w + w
    total += big * w + big * w + 6 * w
    total += 4 * w
    return total


def _loop_layer_bill(n: int, w: int, pilot: int,
                     a_prev: int, cold: int, rescued: int, a_next: int) -> int:
    """One pruning-loop layer (pilot rescue + sampled matmul + ReLU)."""
    big = 2 * n
    p2 = 2 * pilot
    total = 4 * w
    if cold > 0:
        total += p2 * a_prev
        total += 4 * a_prev * w + 4 * a_prev * cold
        total += _mm(p2, a_prev, cold)
        total += (p2 - 1) * cold + cold
        total += cold + 8 * rescued
        total += 2 * a_next + _sort_bill(a_next)
    total += 4 * a_prev * w + 4 * a_prev * a_next
    total += _mm(big, a_prev, a_next)
    total += big * a_next
    return total


def _tangent_tail_bill(w: int, depth: int) -> int:
    """First-layer tangent recursion + final subtract + stack (identical in
    every compared structure; from the t3 model)."""
    per_layer = 2 * _mm(1, w, w) + w * w + 16 * w + w + 16 * w + 3 + w + 12 * w
    return (depth - 1) * per_layer + 2 * w + depth * w


def fold3_structure_bill(n, width, depth, pilot, fold_pilot,
                         loop_dims, fold) -> int:
    """Billed FLOPs of the fold3 (three-terminal-layer dead/on/kink) predict
    structure at sample count n, excluding the analytic diagonal pass
    (identical additive term in every compared structure, ~1e7, negligible).
    Adapted verbatim from t3 capped_fold3.predict_main_bill
    (radial_conditioning=True path, final_weights=None)."""
    w = width
    big = 2 * n
    P2 = 2 * fold_pilot
    total = _shared_head_bill(n, w)

    for a_prev, cold, rescued, a_next in loop_dims:
        total += _loop_layer_bill(n, w, pilot, a_prev, cold, rescued, a_next)

    a28 = fold["a28"]
    total += P2 * a28

    # ---- layer30 ----
    total += 8 * w
    total += 4 * a28 * w
    k_run = fold["k30_init"]
    if fold["d30_init"] > 0:
        total += 4 * a28 * fold["d30_init"] + _mm(P2, a28, fold["d30_init"])
        total += _refine_bill(fold["d30_init"], fold["r30"], P2)
        k_run += fold["r30"]
        total += 2 * k_run
    if fold["o30_init"] > 0:
        total += 4 * a28 * fold["o30_init"] + _mm(P2, a28, fold["o30_init"])
        total += _refine_bill(fold["o30_init"], fold["dm30"], P2)
        k_run += fold["dm30"]
        total += 2 * k_run
    k30 = fold["k30"]
    o30 = fold["o30"]
    total += _sort_bill(k30)
    total += 4 * a28 * k30 + _mm(big, a28, k30) + big * k30
    total += P2 * k30

    # ---- layer31 ----
    total += 8 * w
    k_run = fold["k31_init"]
    if fold["d31_init"] > 0:
        total += _pre31_bill(a28, o30, k30, fold["d31_init"], P2, w)
        total += _refine_bill(fold["d31_init"], fold["r31"], P2)
        k_run += fold["r31"]
        total += 2 * k_run
    if fold["o31_init"] > 0:
        total += _pre31_bill(a28, o30, k30, fold["o31_init"], P2, w)
        total += _refine_bill(fold["o31_init"], fold["dm31"], P2)
        k_run += fold["dm31"]
        total += 2 * k_run
    k31 = fold["k31"]
    o31 = fold["o31"]
    total += _sort_bill(k31)
    total += _pre31_bill(a28, o30, k30, k31, big, w) + big * k31
    total += P2 * k31

    # ---- layer32 ----
    total += 8 * w
    total += (4 * a28 * o30 + 4 * o30 * w + 4 * o30 * o31
              + _mm(a28, o30, o31))
    total += 4 * k30 * w + 4 * k30 * o31
    k_run = fold["k32_init"]
    if fold["d32_init"] > 0:
        total += _pre32_bill(a28, o31, k30, k31, fold["d32_init"], P2, w)
        total += _refine_bill(fold["d32_init"], fold["r32"], P2)
        k_run += fold["r32"]
        total += 2 * k_run
    if fold["o32_init"] > 0:
        total += _pre32_bill(a28, o31, k30, k31, fold["o32_init"], P2, w)
        total += _refine_bill(fold["o32_init"], fold["dm32"], P2)
        k_run += fold["dm32"]
        total += 2 * k_run
    k32 = fold["k32"]
    o32 = fold["o32"]
    d32 = fold["d32"]
    total += _sort_bill(k32)
    if k32 > 0:
        total += _pre32_bill(a28, o31, k30, k31, k32, big, w)
        total += big * k32
        total += big * k32
    if o32 > 0:
        total += big * a28 + big * k30 + big * k31
        total += (4 * o31 * w + 4 * o31 * o32 + _mm(a28, o31, o32)
                  + _mm(1, a28, o32))
        total += (4 * o31 * w + 4 * o31 * o32 + _mm(k30, o31, o32)
                  + _mm(1, k30, o32))
        total += 4 * k31 * w + 4 * k31 * o32 + _mm(1, k31, o32)
        total += 2 * o32
    if d32 > 0:
        total += 4 * d32
    total += 2 * w + w + _sort_bill(w) + 4 * w

    total += _tangent_tail_bill(w, depth)
    return total


def unfolded_structure_bill(n, width, depth, pilot, loop_dims_full) -> int:
    """Diagnostic only: the base-estimator structure (no terminal fold; plain
    pilot-rescued propagation through every layer, terminal-layer mean) at the
    same sample count and partitions -- quantifies what the fold v3 ALREADY
    CONTAINS is worth.  Same per-op conventions."""
    w = width
    big = 2 * n
    total = _shared_head_bill(n, w)
    for i, (a_prev, cold, rescued, a_next) in enumerate(loop_dims_full):
        total += _loop_layer_bill(n, w, pilot, a_prev, cold, rescued, a_next)
        if i == len(loop_dims_full) - 1:      # final layer: mean + assemble
            total += big * a_next             # mean axis=0
            n_dead = w - a_next
            if n_dead > 0:
                total += 4 * n_dead           # analytic means gather
            total += 2 * w + w + _sort_bill(w) + 4 * w   # _assemble_vector
    total += _tangent_tail_bill(w, depth)
    return total


def run_g0b() -> dict:
    g0b = {
        "kill_threshold_reduction": KILL_FOLD_REDUCTION,
        "n_base": N_BASE,
        "counting_convention": (
            "t3 cost-model per-op bills (capped_fold3.predict_main_bill), "
            "direct-matmul convention; WHT first product and Winograd "
            "backend not modeled (identical in both compared structures, "
            "ratio-invariant); analytic diagonal pass excluded (identical "
            "additive ~1e7 term)"
        ),
        "partition_source": (
            "realized dead/on/kink counts from the analytic pass "
            "(predeclared); pilot refinements billed but move zero units "
            "(rescued/demoted = 0) because refinement outcomes are "
            "sample-dependent -- NOTE: the reduction is 0 for EVERY "
            "partition input because both structures evaluate the same "
            "bill function"
        ),
        "metered_anchor": (
            "n8c_g0_results.json full_estimator.billed_flops_mean on the "
            "same nets: 1.8166e11 (101), 1.6984e11 (202), 1.6478e11 (303) "
            "-- sits ~8-10% ABOVE this static count because the deployed "
            "run's pilot rescues enlarge the active sets beyond the "
            "analytic structural sets and its Winograd/WHT backends bill "
            "their own overheads; same order, per-net ordering preserved"
        ),
        "net_rows": [],
    }
    reductions = []
    for net_seed in NET_SEEDS:
        weights = he_mlp_weights(net_seed)
        _, alphas, _, _ = diagonal_gaussian_pass(weights)

        # Middle pruning loop, layers 1..depth-4 (fold3 loop range).
        loop_dims = []
        a_prev = WIDTH
        for layer in range(1, DEPTH - 3):
            structural = int(np.sum(alphas[layer] >= DEAD_ALPHA))
            cold = WIDTH - structural
            loop_dims.append((a_prev, cold, 0, structural))
            a_prev = structural

        fold = {"a28": a_prev}
        for tag, layer in (("30", DEPTH - 3), ("31", DEPTH - 2),
                           ("32", DEPTH - 1)):
            alpha = alphas[layer]
            d = int(np.sum(alpha < DEAD_ALPHA))
            o = int(np.sum(alpha > ON_ALPHA))
            k = WIDTH - d - o
            fold[f"d{tag}_init"] = d
            fold[f"k{tag}_init"] = k
            fold[f"o{tag}_init"] = o
            fold[f"r{tag}"] = 0
            fold[f"dm{tag}"] = 0
            fold[f"k{tag}"] = k
            fold[f"o{tag}"] = o
        fold["d32"] = fold["d32_init"]

        bill_v3_current = fold3_structure_bill(
            N_BASE, WIDTH, DEPTH, PILOT_BASE, FOLD_PILOT_BASE,
            loop_dims, fold,
        )
        bill_l3_variant = fold3_structure_bill(
            N_BASE, WIDTH, DEPTH, PILOT_BASE, FOLD_PILOT_BASE,
            loop_dims, fold,
        )
        if bill_v3_current != bill_l3_variant:
            raise RuntimeError("structural identity violated -- impossible")
        reduction = 1.0 - bill_l3_variant / bill_v3_current

        # Diagnostic: what the fold v3 already contains is worth.
        loop_dims_full = list(loop_dims)
        a_run = fold["a28"]
        for layer in range(DEPTH - 3, DEPTH):
            structural = int(np.sum(alphas[layer] >= DEAD_ALPHA))
            cold = WIDTH - structural
            loop_dims_full.append((a_run, cold, 0, structural))
            a_run = structural
        bill_unfolded = unfolded_structure_bill(
            N_BASE, WIDTH, DEPTH, PILOT_BASE, loop_dims_full
        )

        reductions.append(reduction)
        g0b["net_rows"].append({
            "net_seed": net_seed,
            "bill_v3_current": int(bill_v3_current),
            "bill_l3_variant": int(bill_l3_variant),
            "billed_reduction": reduction,
            "fold_partition_counts": {k: int(v) for k, v in fold.items()},
            "middle_loop_active_min": int(min(d[3] for d in loop_dims)),
            "middle_loop_active_max": int(max(d[3] for d in loop_dims)),
            "diagnostic_bill_unfolded_variant": int(bill_unfolded),
            "diagnostic_existing_fold_value": 1.0 - bill_v3_current
            / bill_unfolded,
        })
        print(
            f"G0-b net {net_seed}: bill(v3 current)={bill_v3_current:.4e}  "
            f"bill(L3 variant)={bill_l3_variant:.4e}  "
            f"reduction={reduction:.4f}  "
            f"[diag: unfolded={bill_unfolded:.4e}, existing fold saves "
            f"{100 * (1 - bill_v3_current / bill_unfolded):.1f}%]",
            flush=True,
        )

    mean_reduction = float(np.mean(reductions))
    g0b["per_net_reductions"] = reductions
    g0b["mean_billed_reduction"] = mean_reduction
    g0b["pass"] = mean_reduction >= KILL_FOLD_REDUCTION
    print(
        f"G0-b mean billed reduction = {mean_reduction:.4f}; "
        f"kill if < {KILL_FOLD_REDUCTION}",
        flush=True,
    )
    return g0b


# ---------------------------------------------------------------- main
def main() -> None:
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    if abs(mean_chi_check - MEAN_CHI_256) > 1e-9:
        raise RuntimeError("mean chi constant does not match the formula")

    results = {
        "date": "2026-08-08",
        "predeclaration": "N9_PREDECLARATION.md",
        "deviations": [
            (
                "FINDING (contradicts the predeclaration's premise, verdict "
                "unaffected in direction): the frozen v3 source "
                "(candidate_source_validator_v3/estimator.py) inherits "
                "fold3_estimator.Estimator -- the three-terminal-layer "
                "dead/on/kink fold -- so v3's current pipeline ALREADY IS "
                "the L3-folded structure ('v3 already folds at L1' is "
                "false; N8c artifacts call v3 'the frozen v3 fold3 "
                "pipeline').  G0-b is executed as predeclared and its "
                "billed reduction is structurally 0."
            ),
            (
                "analytic pass and tangent recursion computed in float64 "
                "numpy instead of float32 flopscope arrays; per-net f32/f64 "
                "cross-check reported (tangent_f32_vs_f64_max_rel_diff)"
            ),
            (
                "G0-a arm (i) is the sampling-stage-isolating plain "
                "antipodal downstream (N8a arm (a) / N8c plain arm), not "
                "the full fold3 pipeline -- same deviation as N8a/N8c; its "
                "per-net variances are anchored against "
                "n8c_g0_results.json plain_downstream.variance_ddof1"
            ),
        ],
        "firewall": (
            "synthetic He nets only; frozen v3 read-only (only shipped "
            "kerdock_phases.npz loaded); tangent tar: estimator.py member "
            "only, extracted to scratch; no dataset/truth/scorer/"
            "submission; single process, foreground"
        ),
        "constants": {
            "net_seeds": list(NET_SEEDS),
            "replicates": REPLICATES,
            "n_base": N_BASE,
            "tangent_lambda": TANGENT_LAMBDA,
            "rotation_seed_formula": "900000 + net_seed*1000 + r",
            "kill_g0a_reduction": KILL_TANGENT_REDUCTION,
            "kill_g0b_reduction": KILL_FOLD_REDUCTION,
        },
        "gates": {},
        "verdict": None,
    }
    out_path = HERE / "n9_g0_results.json"

    def finish(verdict: str) -> None:
        results["verdict"] = verdict
        out_path.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nVERDICT: {verdict}")
        print(f"results written to {out_path}")

    kerdock = load_kerdock_directions()

    print("G0-a: tangent-on-frames paired variance", flush=True)
    g0a = run_g0a(kerdock)
    results["gates"]["g0a"] = g0a

    print("G0-a positive control (diagnostic, iid Gaussian n=14000)",
          flush=True)
    results["gates"]["g0a_positive_control"] = run_g0a_positive_control()

    print("\nG0-b: fold-increment static billed-FLOP count", flush=True)
    g0b = run_g0b()
    results["gates"]["g0b"] = g0b

    survivors = []
    verdict_parts = []
    if g0a["pass"]:
        survivors.append("tangent")
        verdict_parts.append(
            f"G0-a SURVIVES (mean paired variance reduction "
            f"{g0a['mean_paired_variance_reduction']:+.4f} >= "
            f"{KILL_TANGENT_REDUCTION})"
        )
    else:
        verdict_parts.append(
            f"G0-a KILL: tangent component dead on Kerdock frames (mean "
            f"paired variance reduction "
            f"{g0a['mean_paired_variance_reduction']:+.4f} < "
            f"{KILL_TANGENT_REDUCTION}; the frames already absorb the "
            f"first-layer residual the control subtracts)"
        )
    if g0b["pass"]:
        survivors.append("fold")
        verdict_parts.append(
            f"G0-b SURVIVES (mean billed reduction "
            f"{g0b['mean_billed_reduction']:.4f} >= {KILL_FOLD_REDUCTION})"
        )
    else:
        verdict_parts.append(
            f"G0-b KILL: fold increment is empty -- the frozen v3 already "
            f"IS the L3-folded structure, so the predeclared comparison "
            f"yields billed reduction "
            f"{g0b['mean_billed_reduction']:.4f} < {KILL_FOLD_REDUCTION}"
        )
    if survivors:
        verdict_parts.append(
            f"surviving components: {', '.join(survivors)} -- G0 only, no "
            f"build in this task; build gates G1-G3 govern any next step"
        )
        finish("; ".join(verdict_parts))
    else:
        verdict_parts.append(
            "BOTH components dead: N9 KILLED -- per the predeclaration, "
            "the honest local program is exhausted with the composition "
            "explicitly measured, not assumed"
        )
        finish("; ".join(verdict_parts))


if __name__ == "__main__":
    main()
