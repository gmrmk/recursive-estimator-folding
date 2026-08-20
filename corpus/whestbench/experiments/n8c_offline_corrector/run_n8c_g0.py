"""N8c G0 premise gate. Predeclared in N8C_PREDECLARATION.md (governs).

Decompose the Kerdock v3 estimator's per-net final-layer error on synthetic
He nets into sampling variance (across the estimator's own Haar-rotation
randomization) and bias^2 (vs a high-precision MC truth, truth noise
subtracted).  A corrector can only remove the predictable (bias-like) part;
the predeclared kill fires if the bias^2 share of total MSE < 25% (mean
across nets), because the corrector's ceiling would then be < 1.33x raw.

Two measurement arms, one verdict:

- arm_full_estimator (GOVERNING): the actual frozen v3 fold3 pipeline
  (pilot rescue + tangent correction + folding), replicated over rotation
  seeds via ``mlp.seed`` (the estimator seeds its Haar rotation from it;
  same-seed repeat verified bitwise identical).  The predeclaration says
  "replicate the estimator" -- this arm is the genuine falsifier, because
  the deliberate bias the corrector targets lives in this pipeline.
- arm_plain_downstream (cross-check, coordinator-sanctioned, same deviation
  as N8a): the Kerdock phased-Hadamard antipodal spherical estimate with a
  plain antipodal ReLU forward mean.  NOTE: a no-bias ReLU net is
  positively homogeneous, so this fixed-radius spherical estimate is
  EXACTLY unbiased in expectation over the Haar rotation -- its bias share
  is ~0 by construction and it cannot by itself falsify the premise.  It is
  reported to anchor the variance scale against n8a_results.json.

Scope: the final-layer row (the benchmark's primary score is
final_layer_mse; whestbench/scoring.py).  The all-layers secondary metric
is decomposed as a diagnostic.

Firewall: synthetic He nets only; frozen v3 sources imported read-only
(bytecode writing disabled); only the estimator's own shipped sampling
asset (kerdock_phases.npz, via the estimator's setup) is touched; no
dataset/truth/scorer/submission access; single process.
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
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)
sys.path.insert(0, str(V3_DIR))

import flopscope as flops           # noqa: E402
import flopscope.numpy as fnp       # noqa: E402
from whestbench import SetupContext  # noqa: E402
from whestbench.domain import MLP    # noqa: E402

flops.configure(symmetry_warnings=False)

from estimator import Estimator as KerdockV3  # noqa: E402  (frozen v3)

WIDTH, DEPTH = 256, 32
N_BASE = 126 * 256
NET_SEEDS = (101, 202, 303)          # same He nets as N8a
REPLICATES = 16                      # >= 12 required; 16 matches N8a
N_TRUTH = 3_500_000
TRUTH_CHUNK = 65_536
KILL_BIAS_SHARE = 0.25               # predeclared
MEAN_CHI_256 = 15.98438266660852747
BUDGET_B = 272e9
METER_BUDGET = 10**15
BOOTSTRAP_DRAWS = 4000


def rot_seed(net_seed: int, r: int) -> int:
    """Same rotation-seed formula as N8a arm (a)."""
    return 900_000 + net_seed * 1_000 + r


# ----------------------------------------------------------------- nets
def he_weights_np(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


# ---------------------------------------------------------------- truth
def truth_stats(weights: list[np.ndarray], seed: int) -> dict:
    """Chunked iid MC truth: per-layer means + measured per-layer noise.

    Accumulates per-neuron sum and sum-of-squares at every layer, so the
    truth noise floor is measured, not assumed.
    """
    rng = np.random.default_rng(seed)
    sums = np.zeros((DEPTH, WIDTH))
    sumsq = np.zeros((DEPTH, WIDTH))
    done = 0
    t0 = time.perf_counter()
    while done < N_TRUTH:
        m = min(TRUTH_CHUNK, N_TRUTH - done)
        act = rng.standard_normal((m, WIDTH)).astype(np.float32)
        for layer in range(DEPTH):
            act = np.maximum(act @ weights[layer], np.float32(0.0))
            a64 = act.astype(np.float64)
            sums[layer] += a64.sum(axis=0)
            sumsq[layer] += (a64 * a64).sum(axis=0)
        done += m
    means = sums / N_TRUTH
    per_sample_var = sumsq / N_TRUTH - means * means
    noise_per_layer = per_sample_var.mean(axis=1) / N_TRUTH
    return {
        "means": means,                       # (DEPTH, WIDTH)
        "noise_final": float(noise_per_layer[-1]),
        "noise_all_layers_mean": float(noise_per_layer.mean()),
        "wall_s": round(time.perf_counter() - t0, 1),
    }


# -------------------------------------------- arm: plain downstream (N8a)
def load_kerdock_directions() -> np.ndarray:
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (126, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    h_norm = (hadamard / 16.0).astype(np.float32)
    return (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).reshape(N_BASE, WIDTH).astype(np.float32)


def haar_rotation(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


def plain_final_mean(
    weights: list[np.ndarray], first_eff: np.ndarray, points: np.ndarray
) -> np.ndarray:
    first = points @ first_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    return act.astype(np.float64).mean(axis=0)


# --------------------------------------------------- arm: full estimator
def full_estimator_stacks(
    weights_np: list[np.ndarray], net_seed: int
) -> tuple[np.ndarray, list[int], float]:
    """Predict stacks over REPLICATES rotation seeds with the frozen v3."""
    weights_f = [fnp.asarray(w) for w in weights_np]
    est = KerdockV3()
    est.setup(SetupContext(
        width=WIDTH, depth=DEPTH, flop_budget=int(BUDGET_B),
        api_version="synthetic", seed=0, submission_dir=str(V3_DIR),
    ))
    stacks = []
    billed = []
    t0 = time.perf_counter()
    for r in range(REPLICATES):
        mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights_f,
                  seed=rot_seed(net_seed, r), name=f"n8c-{net_seed}-{r}")
        mlp.validate()
        with flops.BudgetContext(METER_BUDGET, quiet=True) as ctx:
            out = est.predict(mlp, METER_BUDGET)
        stacks.append(np.asarray(out).astype(np.float64).copy())
        billed.append(int(ctx.flops_used))
    wall = time.perf_counter() - t0
    return np.stack(stacks), billed, wall


# -------------------------------------------------------- decomposition
def decompose(estimates: np.ndarray, truth: np.ndarray, noise: float) -> dict:
    """Predeclared decomposition: bias^2 = MSE - variance - truth noise.

    ``estimates``: (R, ...) ; ``truth``: (...).  Variance uses ddof=1 so the
    bias^2 estimator is unbiased (E[per-seed sq err] = var + bias^2 + noise).
    The ddof=0 variant (exact algebraic identity MSE = var0 + mean-est sq
    err) is reported for transparency.
    """
    sq_err = (estimates - truth[None]) ** 2
    mse = float(sq_err.mean())
    var1 = float(np.var(estimates, axis=0, ddof=1).mean())
    var0 = float(np.var(estimates, axis=0, ddof=0).mean())
    bias2 = mse - var1 - noise
    return {
        "mse": mse,
        "variance_ddof1": var1,
        "variance_ddof0": var0,
        "truth_noise": noise,
        "bias2": bias2,
        "bias_share": bias2 / mse,
        "bias2_ddof0_variant": mse - var0 - noise,
        "variance_of_seed_mean": var1 / estimates.shape[0],
    }


def main() -> None:
    results = {
        "date": "2026-08-08",
        "predeclaration": "N8C_PREDECLARATION.md",
        "firewall": (
            "synthetic He nets only; frozen v3 imported read-only; only its "
            "shipped sampling asset touched; no dataset/truth/scorer/"
            "submission; single process"
        ),
        "constants": {
            "net_seeds": list(NET_SEEDS),
            "replicates": REPLICATES,
            "n_truth": N_TRUTH,
            "kill_bias_share": KILL_BIAS_SHARE,
            "rotation_seed_formula": "900000 + net_seed*1000 + r (ties to N8a)",
            "scope": "final-layer row (benchmark primary score)",
        },
        "gates": {},
        "verdict": None,
    }
    out_path = HERE / "n8c_g0_results.json"

    def finish(verdict: str) -> None:
        results["verdict"] = verdict
        out_path.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nVERDICT: {verdict}")
        print(f"results written to {out_path}")

    kerdock = load_kerdock_directions()
    g0 = {"nets": [], "arm_notes": {
        "full_estimator": (
            "GOVERNING arm: frozen v3 fold3 pipeline replicated over its own "
            "Haar-rotation randomization (mlp.seed); deliberate pilot-rescue/"
            "tangent bias included -- the corrector's actual target."
        ),
        "plain_downstream": (
            "Cross-check only (same deviation as N8a): positively homogeneous "
            "no-bias ReLU net + fixed-radius Haar-rotated spherical set is "
            "exactly unbiased in expectation, so this arm's bias share is ~0 "
            "by construction and cannot falsify the premise alone."
        ),
    }}

    shares_full = []
    shares_plain = []
    per_net_estimates_full = {}
    for net_seed in NET_SEEDS:
        weights = he_weights_np(net_seed)
        truth = truth_stats(weights, 9_000 + net_seed)
        print(
            f"net {net_seed}: truth done ({truth['wall_s']}s), "
            f"noise_final={truth['noise_final']:.3e}",
            flush=True,
        )

        # Governing arm: full frozen v3 estimator.
        stacks, billed, wall_full = full_estimator_stacks(weights, net_seed)
        finals = stacks[:, -1, :]
        dec_full = decompose(finals, truth["means"][-1], truth["noise_final"])
        per_net_estimates_full[net_seed] = (finals, truth)

        # Diagnostic: all-layers secondary metric decomposition.
        dec_all = decompose(
            stacks, truth["means"], truth["noise_all_layers_mean"]
        )

        # Cross-check arm: plain antipodal downstream (N8a arm (a)).
        t0 = time.perf_counter()
        plain = np.stack([
            plain_final_mean(
                weights,
                (haar_rotation(rot_seed(net_seed, r)).T @ weights[0]).astype(
                    np.float32
                ),
                kerdock,
            )
            for r in range(REPLICATES)
        ])
        wall_plain = time.perf_counter() - t0
        dec_plain = decompose(plain, truth["means"][-1], truth["noise_final"])

        shares_full.append(dec_full["bias_share"])
        shares_plain.append(dec_plain["bias_share"])
        g0["nets"].append({
            "net_seed": net_seed,
            "truth_noise_final": truth["noise_final"],
            "truth_wall_s": truth["wall_s"],
            "full_estimator": {
                **dec_full,
                "billed_flops_mean": float(np.mean(billed)),
                "wall_s": round(wall_full, 1),
            },
            "all_layers_diagnostic": dec_all,
            "plain_downstream": {**dec_plain, "wall_s": round(wall_plain, 1)},
        })
        print(
            f"net {net_seed} FULL: MSE={dec_full['mse']:.4e} "
            f"var={dec_full['variance_ddof1']:.4e} "
            f"bias2={dec_full['bias2']:.4e} "
            f"share={dec_full['bias_share']:.3f}",
            flush=True,
        )
        print(
            f"net {net_seed} PLAIN: MSE={dec_plain['mse']:.4e} "
            f"var={dec_plain['variance_ddof1']:.4e} "
            f"bias2={dec_plain['bias2']:.4e} "
            f"share={dec_plain['bias_share']:.3f}",
            flush=True,
        )

    mean_share_full = float(np.mean(shares_full))
    mean_share_plain = float(np.mean(shares_plain))

    # Diagnostic bootstrap CI on the governing mean bias share (resample
    # rotation seeds within each net).
    boot_rng = np.random.default_rng(2026_08_08)
    boots = []
    for _ in range(BOOTSTRAP_DRAWS):
        draw = []
        for net_seed in NET_SEEDS:
            finals, truth = per_net_estimates_full[net_seed]
            idx = boot_rng.integers(0, REPLICATES, size=REPLICATES)
            dec = decompose(
                finals[idx], truth["means"][-1], truth["noise_final"]
            )
            draw.append(dec["bias_share"])
        boots.append(float(np.mean(draw)))
    ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))

    g0["mean_bias_share_full_estimator"] = mean_share_full
    g0["mean_bias_share_plain_downstream"] = mean_share_plain
    g0["bootstrap_ci_95_mean_share_full"] = ci
    g0["kill_threshold"] = KILL_BIAS_SHARE
    g0["pass"] = mean_share_full >= KILL_BIAS_SHARE
    results["gates"]["g0"] = g0
    print(
        f"\nG0 mean bias share: full estimator = {mean_share_full:.3f} "
        f"(bootstrap 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]), "
        f"plain downstream = {mean_share_plain:.3f}; "
        f"kill if < {KILL_BIAS_SHARE}",
        flush=True,
    )

    if not g0["pass"]:
        finish(
            "KILL at G0: sampling variance dominates the Kerdock v3 "
            "estimator's final-layer error on synthetic He nets "
            f"(mean bias^2 share {mean_share_full:.3f} < {KILL_BIAS_SHARE} "
            "across nets); an offline corrector's ceiling is below the "
            "predeclared 1.33x bar. First broken link: the N8c premise."
        )
        return
    finish(
        "G0 SURVIVES: mean bias^2 share "
        f"{mean_share_full:.3f} >= {KILL_BIAS_SHARE} -- the predictable "
        "error component is large enough that an offline corrector clears "
        "the predeclared ceiling bar. Build gates G1-G3 may proceed."
    )


if __name__ == "__main__":
    main()
