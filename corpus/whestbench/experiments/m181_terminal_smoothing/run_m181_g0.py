"""M181 G0 gate runner. Predeclared in M181_PREDECLARATION.md (governs).

Terminal rectified-Gaussian smoothing of the final-layer estimate: the same
64,512 Kerdock antipodal samples (exact chi-mean radius, one shared Haar
rotation per rotation seed -- the M180 Arm A machinery verbatim) feed four
estimators of the final-layer mean vector, scored by MSE against a 3.5M-sample
chunked iid MC truth (N8c machinery reduced to the scored final-layer row,
truth noise floor measured and subtracted from every MSE):

  Arm 0 (baseline)   mean_s ReLU(h_s @ W_31): the current estimator's final
                     row -- exactly unbiased for the Gaussian mean by positive
                     homogeneity + Haar rotation + exact-mean-chi radius.
  Arm 1 (univariate) empirical per-neuron (mu_i, sigma_i) of z = h @ W_31
                     across the n samples -> mu_i Phi(mu_i/sigma_i)
                     + sigma_i phi(mu_i/sigma_i).
  Arm 2 (pair-prop)  empirical layer-30 PRE-activation moments (mu, V) ->
                     ONE exact rectified-Gaussian pair-propagation step
                     (M179 relu_moments over the FULL 32,640-pair set, M178
                     certified bivariate provider) -> propagate through W_31
                     -> univariate rectified-Gaussian final means.
  Arm 3 (CV form)    sample mean PLUS lambda * (analytic smoothed estimate
                     - its own sample-consistent estimate), lambda from a
                     20%-holdout of the samples.  Exact construction (the
                     predeclaration's sentence made operational; documented
                     in M181_G0_NOTES.md):
                       split the 126 Kerdock frames 101 train / 25 holdout
                       (frame % 5 == 4 -> holdout; antipodal halves stay with
                       their base direction), giving 51,712 / 12,800 samples;
                       S80/S20 = per-neuron sample means of ReLU(z) on the
                       splits, Sfull on all samples; A80 = Arm-1 analytic
                       from the train-split moments; D = A80 - S80;
                       lambda = argmin_l || (S80 + l D) - S20 ||^2
                              = sum_i D_i (S20_i - S80_i) / sum_i D_i^2
                       (scalar per net x rotation seed);
                       estimate = Sfull + lambda * D.
                     NOTE (honesty): exact unbiasedness holds only for fixed
                     lambda AND E[D] = 0; here E[D] = bias(A80), so the arm is
                     bias-ADAPTIVE (lambda -> 0 when the smoothing bias is
                     material), not exactly unbiased.  This is the closest
                     operational form of the predeclared sentence.

Gates (predeclared, MSE-based): per arm, aggregate noise-subtracted MSE ratio
vs Arm 0 (geomean over the 3 nets, MSEs averaged over rotation seeds).  KILL
the arm if MSE reduction < 10% (ratio > 0.90).  PROMOTE only the best arm and
only if reduction >= 15% (ratio <= 0.85) with a paired bootstrap 95% CI
excluding 10% (CI upper < 0.90).

Firewall: synthetic He nets only (seeds 101/202/303, t3-style); the only .npz
loaded is the estimator's own shipped sampling asset kerdock_phases.npz; M178/
M179 modules imported READ-ONLY (bytecode writing disabled); no dataset,
truth, scorer, or submission access; all writes stay inside this experiment
directory; single process, plain numpy (sanctioned G0 deviation, no flopscope
metering).

Checkpointing (pure resumability, no statistical effect -- one deterministic
seed schedule): truth partials every few chunks, estimate stacks per rep,
per-net npz files; aggregation + verdicts run once all three nets are done.

Usage:
  python run_m181_g0.py probe        # timing probe, writes nothing
  python run_m181_g0.py 101          # run/resume one net
  python run_m181_g0.py              # run everything remaining + aggregate
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
EXP = HERE.parent
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)
M179_DIR = EXP / "m179_background_archive_producer"
sys.path.insert(0, str(M179_DIR))

import m179_background_producer as m179  # noqa: E402  (read-only; pulls M178)
import m179_relu_pair_assembly as asm    # noqa: E402  (read-only)

WIDTH, DEPTH = 256, 32
N_FRAMES = 126
N_BASE = N_FRAMES * WIDTH            # 32,256 base directions
N_TOTAL = 2 * N_BASE                 # 64,512 antipodal directions (matched n)
G0_NET_SEEDS = (101, 202, 303)
REPLICATES = 16                      # >= predeclared 12; confirmed by probe
N_TRUTH = 3_500_000
TRUTH_CHUNK = 65_536
TRUTH_CKPT_EVERY = 6                 # checkpoint truth partial every 6 chunks
MEAN_CHI_256 = 15.98438266660852747  # frozen v3 constant (estimator.py)
BOOTSTRAP_DRAWS = 4000
BOOT_SEED = 2026_08_08
KILL_REDUCTION = 0.10                # reduction < 10%  -> KILL (ratio > 0.90)
PROMOTE_REDUCTION = 0.15             # >= 15% AND CI excludes 10% -> PROMOTE
HOLDOUT_FRAME_MOD = 5                # frame % 5 == 4 -> Arm-3 holdout (25/126)

ARM_NAMES = ("arm0_baseline", "arm1_univariate", "arm2_pairprop", "arm3_cv")

_ERF = np.frompyfunc(math.erf, 1, 1)
_INV_SQRT2 = 1.0 / math.sqrt(2.0)
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


# ----------------------------------------------------------------- nets
def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (t3-style; verbatim from m180)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


# --------------------------------------------------- Kerdock design (m180)
def normalized_hadamard() -> np.ndarray:
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    return (hadamard / 16.0).astype(np.float32)


def load_kerdock_frames() -> np.ndarray:
    """Rebuild the exact v3 direction set (m180 verbatim, frame shape)."""
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (N_FRAMES, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    h_norm = normalized_hadamard()
    frames = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).astype(np.float32)
    radii = np.linalg.norm(frames, axis=2)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return frames


def haar_rotation(seed: int) -> np.ndarray:
    """Mirror of estimator.py _haar_rotation (float32 QR, sign-fixed)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


def rot_seed(net_seed: int, rep: int) -> int:
    """Rotation-seed formula shared with n8a/n8c/m180 Arm A."""
    return 900_000 + net_seed * 1_000 + rep


# -------------------------------------------------------------- forward
def forward_terminal(
    weights: list[np.ndarray], points: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Antipodal ReLU forward (m180 machinery) with the two terminal
    pre-activation matrices exposed.

    Returns (g30, z31): g30 = layer-30 pre-activations (input to ReLU 30),
    z31 = final-layer pre-activations (h30 @ W_31), both (N_TOTAL, WIDTH) f32.
    Row layout: rows [0, N_BASE) are +points in base order, rows
    [N_BASE, 2 N_BASE) are the antipodal partners in the same base order.
    """
    first = points @ weights[0]
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    for layer in range(1, DEPTH - 2):            # layers 1..29
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    g30 = act @ weights[DEPTH - 2]               # layer-30 pre-activations
    h30 = np.maximum(g30, np.float32(0.0))
    z31 = h30 @ weights[DEPTH - 1]               # final pre-activations
    return g30, z31


# ----------------------------------------------------------------- truth
def truth_final(net_seed: int, weights: list[np.ndarray]) -> dict:
    """Chunked iid MC truth, final layer only: per-neuron mean + measured
    truth noise floor (per-sample final variance / N_TRUTH).  N8c machinery
    reduced to the scored row; per-chunk seeding for clean resumability
    (statistically identical: every sample is iid N(0, I))."""
    final_path = HERE / f"m181_truth_net{net_seed}.npz"
    if final_path.exists():
        d = np.load(final_path)
        return {"means": d["means"], "noise_final": float(d["noise_final"]),
                "wall_s": float(d["wall_s"])}
    part_path = HERE / f"m181_truth_partial_net{net_seed}.npz"
    n_chunks = math.ceil(N_TRUTH / TRUTH_CHUNK)
    if part_path.exists():
        d = np.load(part_path)
        sums, sumsq = d["sums"].copy(), d["sumsq"].copy()
        start = int(d["chunks_done"])
        wall_prev = float(d["wall_s"])
        print(f"  truth net {net_seed}: resuming at chunk {start}/{n_chunks}",
              flush=True)
    else:
        sums = np.zeros(WIDTH)
        sumsq = np.zeros(WIDTH)
        start, wall_prev = 0, 0.0
    t0 = time.perf_counter()
    for c in range(start, n_chunks):
        m = min(TRUTH_CHUNK, N_TRUTH - c * TRUTH_CHUNK)
        rng = np.random.default_rng((9_000 + net_seed) * 1_000_000 + c)
        act = rng.standard_normal((m, WIDTH)).astype(np.float32)
        for layer in range(DEPTH):
            act = np.maximum(act @ weights[layer], np.float32(0.0))
        a64 = act.astype(np.float64)
        sums += a64.sum(axis=0)
        sumsq += (a64 * a64).sum(axis=0)
        if (c + 1) % TRUTH_CKPT_EVERY == 0 and c + 1 < n_chunks:
            np.savez(part_path, sums=sums, sumsq=sumsq, chunks_done=c + 1,
                     wall_s=wall_prev + time.perf_counter() - t0)
            print(f"  truth net {net_seed}: chunk {c + 1}/{n_chunks} "
                  f"({wall_prev + time.perf_counter() - t0:.0f}s)", flush=True)
    wall = wall_prev + time.perf_counter() - t0
    means = sums / N_TRUTH
    per_sample_var = sumsq / N_TRUTH - means * means
    noise_final = float(per_sample_var.mean() / N_TRUTH)
    np.savez(final_path, means=means, noise_final=noise_final, wall_s=wall)
    if part_path.exists():
        part_path.unlink()
    print(f"  truth net {net_seed}: done ({wall:.0f}s), "
          f"noise_final={noise_final:.3e}", flush=True)
    return {"means": means, "noise_final": noise_final, "wall_s": wall}


# ------------------------------------------------------------------ arms
def rect_mean(mu: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """Vectorized E[ReLU(N(mu, sigma^2))] = mu Phi(mu/sigma) + sigma
    phi(mu/sigma); math.erf (correctly rounded ~1 ulp) via frompyfunc.
    Cross-checked against asm.relu_gaussian_mean in the probe."""
    mu = np.asarray(mu, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    out = np.maximum(mu, 0.0)
    ok = sigma > 0.0
    if np.any(ok):
        alpha = mu[ok] / sigma[ok]
        big_phi = 0.5 * (1.0 + _ERF(alpha * _INV_SQRT2).astype(np.float64))
        small_phi = _INV_SQRT_2PI * np.exp(-0.5 * alpha * alpha)
        out[ok] = mu[ok] * big_phi + sigma[ok] * small_phi
    return out


def arm0_baseline(z31: np.ndarray) -> np.ndarray:
    return np.maximum(z31, np.float32(0.0)).astype(np.float64).mean(axis=0)


def arm1_univariate(z31: np.ndarray) -> np.ndarray:
    z = z31.astype(np.float64)
    mu = z.mean(axis=0)
    sd = z.std(axis=0, ddof=1)
    return rect_mean(mu, sd)


def arm2_pairprop(g30: np.ndarray, w31: np.ndarray) -> np.ndarray:
    """Empirical layer-30 pre-activation (mu, V) -> M179 exact rectified pair
    propagation (full 32,640-pair set, M178 certified provider) -> W_31 ->
    univariate rectified-Gaussian final means."""
    g = g30.astype(np.float64)
    mu_g = g.mean(axis=0)
    gc = g - mu_g
    v_g = (gc.T @ gc) / (g.shape[0] - 1)
    v_g = 0.5 * (v_g + v_g.T)
    state = m179.relu_moments(mu_g, v_g)         # exact post-ReLU (mu, V)
    w64 = w31.astype(np.float64)
    a31 = state.mu @ w64
    t = state.V @ w64
    var31 = np.einsum("ik,ik->k", w64, t)
    var31 = np.maximum(var31, 0.0)               # fp-rounding guard only
    return rect_mean(a31, np.sqrt(var31))


def arm3_masks() -> tuple[np.ndarray, np.ndarray]:
    """Train/holdout row masks over the N_TOTAL samples (frame-level split;
    antipodal halves stay with their base direction)."""
    frame_of_base = np.arange(N_BASE) // WIDTH
    hold_base = (frame_of_base % HOLDOUT_FRAME_MOD) == (HOLDOUT_FRAME_MOD - 1)
    hold = np.concatenate((hold_base, hold_base))
    return ~hold, hold


_TRAIN_MASK, _HOLD_MASK = arm3_masks()


def arm3_cv(z31: np.ndarray) -> tuple[np.ndarray, float]:
    """Predeclared CV form; exact construction in the module docstring."""
    relu = np.maximum(z31, np.float32(0.0)).astype(np.float64)
    s_full = relu.mean(axis=0)
    s_80 = relu[_TRAIN_MASK].mean(axis=0)
    s_20 = relu[_HOLD_MASK].mean(axis=0)
    z_tr = z31[_TRAIN_MASK].astype(np.float64)
    a_80 = rect_mean(z_tr.mean(axis=0), z_tr.std(axis=0, ddof=1))
    d = a_80 - s_80
    denom = float(d @ d)
    lam = float(d @ (s_20 - s_80)) / denom if denom > 0.0 else 0.0
    return s_full + lam * d, lam


# ------------------------------------------------------------- per net
def run_net(net_seed: int, kerdock_frames: np.ndarray) -> None:
    weights = he_mlp_weights(net_seed)
    truth_final(net_seed, weights)               # ensure truth exists first
    path = HERE / f"m181_g0_partial_net{net_seed}.npz"
    if path.exists():
        d = np.load(path)
        stacks = {a: list(d[a]) for a in ARM_NAMES}
        lambdas = list(d["lambdas"])
        walls = {"forward": float(d["wall_forward"]),
                 "arm2": float(d["wall_arm2"])}
        done = len(lambdas)
        if done >= REPLICATES:
            print(f"net {net_seed}: already complete ({done} reps)", flush=True)
            return
        print(f"net {net_seed}: resuming at rep {done}/{REPLICATES}",
              flush=True)
    else:
        stacks = {a: [] for a in ARM_NAMES}
        lambdas = []
        walls = {"forward": 0.0, "arm2": 0.0}
        done = 0
    for rep in range(done, REPLICATES):
        t0 = time.perf_counter()
        rot = haar_rotation(rot_seed(net_seed, rep))
        points = (kerdock_frames.reshape(-1, WIDTH) @ rot.T).astype(np.float32)
        g30, z31 = forward_terminal(weights, points)
        t1 = time.perf_counter()
        stacks["arm0_baseline"].append(arm0_baseline(z31))
        stacks["arm1_univariate"].append(arm1_univariate(z31))
        est3, lam = arm3_cv(z31)
        stacks["arm3_cv"].append(est3)
        lambdas.append(lam)
        t2 = time.perf_counter()
        stacks["arm2_pairprop"].append(arm2_pairprop(g30, weights[DEPTH - 1]))
        t3 = time.perf_counter()
        walls["forward"] += t1 - t0
        walls["arm2"] += t3 - t2
        np.savez(
            path,
            **{a: np.stack(stacks[a]) for a in ARM_NAMES},
            lambdas=np.array(lambdas),
            wall_forward=walls["forward"],
            wall_arm2=walls["arm2"],
        )
        print(f"  net {net_seed} rep {rep + 1}/{REPLICATES}: forward "
              f"{t1 - t0:.1f}s arms013 {t2 - t1:.1f}s arm2 {t3 - t2:.1f}s "
              f"lambda={lam:.4f}", flush=True)
    print(f"net {net_seed}: complete ({REPLICATES} reps)", flush=True)


# ------------------------------------------------------------ aggregate
def decompose(estimates: np.ndarray, truth: np.ndarray, noise: float) -> dict:
    """N8c decomposition verbatim: bias^2 = MSE - variance(ddof=1) - noise."""
    sq_err = (estimates - truth[None]) ** 2
    mse = float(sq_err.mean())
    var1 = float(np.var(estimates, axis=0, ddof=1).mean())
    bias2 = mse - var1 - noise
    return {
        "mse_raw": mse,
        "mse_noise_subtracted": mse - noise,
        "variance_ddof1": var1,
        "truth_noise": noise,
        "bias2": bias2,
        "bias_share_of_raw_mse": bias2 / mse,
    }


def aggregate(partials: dict, truths: dict) -> dict:
    comp_arms = [a for a in ARM_NAMES if a != "arm0_baseline"]
    out: dict = {"net_rows": [], "arm_summary": {}, "floored_draws": 0}

    per_arm_lognets: dict[str, list[float]] = {a: [] for a in comp_arms}
    for net_seed in G0_NET_SEEDS:
        arrs, truth = partials[net_seed], truths[net_seed]
        noise = truth["noise_final"]
        row: dict = {"net_seed": net_seed, "truth_noise_final": noise,
                     "lambda_mean_arm3": float(np.mean(arrs["lambdas"])),
                     "lambda_std_arm3": float(np.std(arrs["lambdas"]))}
        dec0 = decompose(arrs["arm0_baseline"], truth["means"], noise)
        row["arm0_baseline"] = dec0
        base = dec0["mse_noise_subtracted"]
        for arm in comp_arms:
            dec = decompose(arrs[arm], truth["means"], noise)
            dec["ratio_vs_arm0_noise_subtracted"] = (
                dec["mse_noise_subtracted"] / base
            )
            row[arm] = dec
            per_arm_lognets[arm].append(
                math.log(dec["mse_noise_subtracted"] / base)
            )
        out["net_rows"].append(row)

    # Paired bootstrap over rotation-seed indices, shared across arms per draw.
    boot_rng = np.random.default_rng(BOOT_SEED)
    boots: dict[str, list[float]] = {a: [] for a in comp_arms}
    floor_hits = 0
    for _ in range(BOOTSTRAP_DRAWS):
        logs: dict[str, list[float]] = {a: [] for a in comp_arms}
        for net_seed in G0_NET_SEEDS:
            arrs, truth = partials[net_seed], truths[net_seed]
            noise = truth["noise_final"]
            idx = boot_rng.integers(0, REPLICATES, size=REPLICATES)
            mses = {}
            for arm in ARM_NAMES:
                m = float(((arrs[arm][idx] - truth["means"][None]) ** 2).mean())
                m -= noise
                if m <= 0.0:
                    m = 1e-18
                    floor_hits += 1
                mses[arm] = m
            for arm in comp_arms:
                logs[arm].append(math.log(mses[arm] / mses["arm0_baseline"]))
        for arm in comp_arms:
            boots[arm].append(math.exp(float(np.mean(logs[arm]))))
    out["floored_draws"] = floor_hits

    promote_eligible = []
    for arm in comp_arms:
        agg = math.exp(float(np.mean(per_arm_lognets[arm])))
        ci = (
            float(np.percentile(boots[arm], 2.5)),
            float(np.percentile(boots[arm], 97.5)),
        )
        reduction = 1.0 - agg
        killed = reduction < KILL_REDUCTION
        eligible = (reduction >= PROMOTE_REDUCTION) and (
            ci[1] < 1.0 - KILL_REDUCTION
        )
        out["arm_summary"][arm] = {
            "aggregate_ratio_geomean": agg,
            "reduction_vs_arm0": reduction,
            "bootstrap_ci_95_ratio": ci,
            "killed": killed,
            "promote_eligible": eligible,
        }
        if eligible:
            promote_eligible.append((agg, arm))
        print(
            f"{arm}: ratio {agg:.4f} (reduction {100 * reduction:+.1f}%), "
            f"95% CI [{ci[0]:.4f}, {ci[1]:.4f}] -> "
            f"{'KILL' if killed else ('PROMOTE-ELIGIBLE' if eligible else 'SURVIVES KILL, NOT PROMOTABLE')}",
            flush=True,
        )

    if promote_eligible:
        promote_eligible.sort()
        out["promoted_arm"] = promote_eligible[0][1]
    else:
        out["promoted_arm"] = None
    return out


# ----------------------------------------------------------------- probe
def probe() -> None:
    """Timing probe: one truth chunk, one rep forward, one full-pair-set
    relu_moments, plus a rect_mean vs asm cross-check.  Writes nothing."""
    print("probe: building design + net", flush=True)
    frames = load_kerdock_frames()
    weights = he_mlp_weights(101)

    # rect_mean cross-check against the M179 univariate backbone
    rng = np.random.default_rng(7)
    mus = rng.normal(size=32)
    sds = np.abs(rng.normal(size=32)) + 0.05
    mine = rect_mean(mus, sds)
    ref = np.array([asm.relu_gaussian_mean(m, s) for m, s in zip(mus, sds)])
    err = float(np.max(np.abs(mine - ref)))
    print(f"probe: rect_mean vs asm.relu_gaussian_mean max |diff| = {err:.2e}",
          flush=True)
    if err > 1e-14:
        raise RuntimeError("rect_mean does not match the M179 backbone")

    t0 = time.perf_counter()
    act = np.random.default_rng(1).standard_normal(
        (TRUTH_CHUNK, WIDTH)).astype(np.float32)
    for w in weights:
        act = np.maximum(act @ w, np.float32(0.0))
    chunk_s = time.perf_counter() - t0
    n_chunks = math.ceil(N_TRUTH / TRUTH_CHUNK)
    print(f"probe: one truth chunk {chunk_s:.2f}s -> ~{chunk_s * n_chunks:.0f}s"
          f" per net truth ({n_chunks} chunks)", flush=True)

    t0 = time.perf_counter()
    rot = haar_rotation(rot_seed(101, 0))
    points = (frames.reshape(-1, WIDTH) @ rot.T).astype(np.float32)
    g30, z31 = forward_terminal(weights, points)
    fwd_s = time.perf_counter() - t0
    print(f"probe: one rep forward {fwd_s:.2f}s -> ~{fwd_s * REPLICATES:.0f}s "
          f"per net at {REPLICATES} reps", flush=True)

    t0 = time.perf_counter()
    est2 = arm2_pairprop(g30, weights[DEPTH - 1])
    arm2_s = time.perf_counter() - t0
    print(f"probe: one full-pair-set arm2 step {arm2_s:.1f}s -> "
          f"~{arm2_s * REPLICATES:.0f}s per net at {REPLICATES} reps",
          flush=True)
    est0 = arm0_baseline(z31)
    est1 = arm1_univariate(z31)
    est3, lam = arm3_cv(z31)
    print("probe: sample estimates neuron 0: "
          f"arm0={est0[0]:.6f} arm1={est1[0]:.6f} arm2={est2[0]:.6f} "
          f"arm3={est3[0]:.6f} (lambda={lam:.4f})", flush=True)
    per_net = chunk_s * n_chunks + (fwd_s + arm2_s) * REPLICATES
    print(f"probe: projected per-net wall ~{per_net:.0f}s, total "
          f"~{3 * per_net / 60:.1f} min at {REPLICATES} reps", flush=True)


# ------------------------------------------------------------------ main
def main() -> None:
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    if abs(mean_chi_check - MEAN_CHI_256) > 1e-9:
        raise RuntimeError("mean chi constant does not match the formula")

    if len(sys.argv) > 1 and sys.argv[1] == "probe":
        probe()
        return

    only_nets = None
    if len(sys.argv) > 1:
        only_nets = {int(x) for x in sys.argv[1].split(",")}

    kerdock_frames = load_kerdock_frames()
    partials: dict[int, dict] = {}
    truths: dict[int, dict] = {}
    for net_seed in G0_NET_SEEDS:
        path = HERE / f"m181_g0_partial_net{net_seed}.npz"
        if path.exists():
            d = dict(np.load(path))
            if len(d["lambdas"]) >= REPLICATES:
                partials[net_seed] = d
                truths[net_seed] = truth_final(
                    net_seed, he_mlp_weights(net_seed))
                print(f"net {net_seed}: loaded complete partial", flush=True)
                continue
        if only_nets is not None and net_seed not in only_nets:
            continue
        run_net(net_seed, kerdock_frames)
        partials[net_seed] = dict(np.load(path))
        truths[net_seed] = truth_final(net_seed, he_mlp_weights(net_seed))

    if set(partials) != set(G0_NET_SEEDS):
        missing = sorted(set(G0_NET_SEEDS) - set(partials))
        print(f"nets remaining: {missing} -- rerun to continue", flush=True)
        return

    g0 = aggregate(partials, truths)
    results = {
        "date": "2026-08-08",
        "predeclaration": "M181_PREDECLARATION.md",
        "gate": "G0",
        "config": {
            "width": WIDTH, "depth": DEPTH,
            "n_base": N_BASE, "n_total_antipodal": N_TOTAL,
            "net_seeds": list(G0_NET_SEEDS),
            "replicates": REPLICATES,
            "n_truth": N_TRUTH,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "kill_reduction": KILL_REDUCTION,
            "promote_reduction": PROMOTE_REDUCTION,
            "rotation_seed_formula": "900000 + net_seed*1000 + rep",
            "arm3_split": "126 frames -> 101 train / 25 holdout "
                          "(frame % 5 == 4), 51712/12800 samples "
                          "(80.16%/19.84%)",
            "arm2_pair_set": "FULL 32,640-pair M179 relu_moments at layer 30 "
                             "(no diagonal/top-k fallback needed)",
        },
        "firewall": (
            "synthetic He nets only; only kerdock_phases.npz loaded (the "
            "estimator's own sampling asset); M178/M179 imported read-only, "
            "bytecode writes disabled; no dataset/truth/scorer/submission; "
            "writes confined to the m181 experiment directory; plain numpy "
            "(sanctioned G0 deviation, no flopscope metering)"
        ),
        "g0": g0,
    }
    verdicts = []
    for arm, s in g0["arm_summary"].items():
        tag = ("KILL" if s["killed"]
               else ("PROMOTE-ELIGIBLE" if s["promote_eligible"]
                     else "SURVIVES-KILL-NOT-PROMOTABLE"))
        verdicts.append(f"{arm}={tag}({s['aggregate_ratio_geomean']:.4f})")
    if g0["promoted_arm"]:
        results["verdict"] = (
            f"PROMOTE {g0['promoted_arm']} to G1 (best promote-eligible arm); "
            "all others held to their per-arm verdicts: " + "; ".join(verdicts)
        )
    else:
        results["verdict"] = "NO ARM PROMOTED at G0: " + "; ".join(verdicts)
    out_path = HERE / "m181_g0_results.json"
    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nVERDICT: {results['verdict']}")
    print(f"results written to {out_path}")


if __name__ == "__main__":
    main()
