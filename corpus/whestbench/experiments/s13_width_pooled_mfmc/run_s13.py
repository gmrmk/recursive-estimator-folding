"""S13 -- ledger id s13_width_pooled_mfmc_premise.

QUESTION: does a WIDTH-POOLED surrogate net give a real MFMC/control-variate
gain for the champion target E[final-layer neuron-mean]?  (Depth-fidelity died
at 0.056x in S10 -- layers re-mix.  Width is the untested axis.)

Firewall: synthetic self-generated He nets + own MC only.  We IMPORT (never
edit) the frozen constructor + Kerdock directions from the sibling n8a runner
(he_mlp_weights, load_kerdock_directions, haar_rotation, WIDTH, DEPTH).  The
only external read is n8a's own shipped sampling asset (read-only, via its
loader).  sys.dont_write_bytecode is set so importing n8a leaves no .pyc
outside this directory.  Writes confined to this directory.  No git.

---------------------------------------------------------------- SURROGATE
Deterministic, training-free width pooling of the SAME weight draw:

Hidden layers l=2..32 (stored (in, out) = (256, 256); forward is act @ W):
  pool disjoint k x k blocks in BOTH dims -> (256/k, 256/k), then rescale.
  Rescale derivation: each pooled entry is the average of k^2 iid
  N(0, 2/256) entries -> variance (2/256)/k^2 = 2/(256 k^2).  He for
  fan_in = 256/k wants variance 2/(256/k) = 2k/256.  Rescale factor
  sqrt[(2k/256) / (2/(256 k^2))] = sqrt(k^3) = k^{3/2}.
    k=4 (width 64):  sqrt(64)  = 8
    k=2 (width 128): sqrt(8)   = 2*sqrt(2)

Input layer W_1 (the probe direction u stays 256-d so the SAME rotated u
feeds both nets): pool the OUTPUT dim only -> (256, 256/k).  Each pooled
entry is the average of k iid N(0, 2/256) entries (k adjacent columns)
-> variance 2/(256 k).  He with fan_in = 256 (input dim unchanged) wants
2/256.  Rescale factor sqrt[(2/256) / (2/(256 k))] = sqrt(k).
    k=4: 2      k=2: sqrt(2)

Both rescales are verified empirically below (pooled-entry variance vs the
He target for the pooled width).

Surrogate target: h(u) = mean over ITS 256/k final post-ReLU neurons.
Full-net target: g(u) = mean over 256 final post-ReLU neurons.

-------------------------------------------------------------- MEASUREMENT
Fixed 8,192-direction subsample (seeded permutation, no replacement) of the
antipodally-doubled rotated Kerdock design (2 * 126 * 256 = 64,512 points).
The per-net Haar rotation (seed 900000 + net*1000 + 0) is folded into the
first matmul exactly as the champion does (first_eff = rotation.T @ W1);
because the subsample is drawn from the already-doubled set, forwarding each
subsampled point directly reproduces the champion's antipodal branches.

rho = Pearson corr_u(g, h) on the subsample.  (Pearson IS the correlation of
the mean-removed fields, and is the quantity the MFMC formula consumes; the
uncentered cosine of the raw positive fields is reported separately for
context -- it is trivially near 1 for post-ReLU means and carries no CV
information.)

------------------------------------------------------- MFMC CLOSED FORM
Peherstorfer / Willcox / Gunzburger 2016, two models, derived:
Estimator  s = mean_{n1} g  +  alpha * ( mean_{n2} h - mean_{n1} h ),
n2 >= n1 (h is evaluated on a superset of g's samples).
  Var(s) = sig_g^2/n1 + (alpha^2 sig_h^2 - 2 alpha rho sig_g sig_h)
                        * (1/n1 - 1/n2)
Optimal alpha* = rho * sig_g / sig_h  gives
  Var(s) = sig_g^2 [ (1 - rho^2)/n1 + rho^2/n2 ].
Minimize under budget n1 * 1 + n2 * w = p (cost(g) = 1, cost(h) = w):
  n1 propto sqrt(1 - rho^2),  n2 propto |rho| / sqrt(w)  ==>
  Var(s) = sig_g^2 ( sqrt(1 - rho^2) + sqrt(w) |rho| )^2 / p.
Plain MC at the same budget: Var = sig_g^2 / p.  Hence at matched billed
FLOPs
  ratio = ( sqrt(1 - rho^2) + sqrt(w) * |rho| )^2 ,   GAIN = 1 / ratio.
Feasibility n2 >= n1 requires rho^2 >= w/(1+w); any gain (>1) requires
|rho| > 2 sqrt(w)/(1+w).  Both are checked and reported.

-------------------------------------------------------------- FLOP MODEL
MACs per direction (ReLU + neuron-mean are O(width), negligible):
  full     : 32 layers * 256*256                  = 2,097,152
  pooled-64: 256*64 (input) + 31 * 64*64          =   143,360
  pooled-128: 256*128 (input) + 31 * 128*128      =   540,672
  w64  = 143,360 / 2,097,152 = 35/512  = 0.068359375   (~1/14.6)
  w128 = 540,672 / 2,097,152 = 33/128  = 0.2578125     (~1/3.9)

------------------------------------------------------------------- GATES
Predeclared, on the aggregate (geomean over nets 101/202/303) closed-form
MFMC gain of the width-64 pooled surrogate at matched billed FLOPs:
  >= 1.3x  -> arm proposal for Sol
  <  1.1x  -> width-fidelity CLOSED (joins depth; fidelity family fully dead)
  1.1-1.3x -> INCONCLUSIVE

------------------------------------------------------------- TWO-SIGNAL
1. rho recomputed on an independent, disjoint 8,192-direction resample.
2. width-128 (k=2) pooled variant as the width-trend check (its MFMC gain at
   w128 reported if rho rises strongly with surrogate width).
3. Internal: Pearson rho recomputed from raw sums (float64) and required to
   match np.corrcoef to 1e-12.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True  # keep .pyc out of the frozen n8a directory

HERE = Path(__file__).resolve().parent
N8A_DIR = HERE.parent / "n8a_rqmc_kerdock"
sys.path.insert(0, str(N8A_DIR))

import run_n8a_gates as n8a  # noqa: E402  (frozen, imported, never edited)

WIDTH = n8a.WIDTH    # 256
DEPTH = n8a.DEPTH    # 32
NET_SEEDS = (101, 202, 303)
N_SUB = 8192
SUBSAMPLE_SEED = 13_2026_0809   # fixed permutation seed for the direction subsets
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 2026_08_09
POOL_KS = (4, 2)                # k=4 -> width 64 (primary); k=2 -> width 128 (trend)

MACS_FULL = DEPTH * WIDTH * WIDTH


def pooled_width(k: int) -> int:
    return WIDTH // k


def cost_ratio(k: int) -> float:
    m = pooled_width(k)
    return (WIDTH * m + (DEPTH - 1) * m * m) / MACS_FULL


# ------------------------------------------------------------ construction
def pool_hidden(w: np.ndarray, k: int) -> np.ndarray:
    """Disjoint k x k block average in both dims, rescaled by k^{3/2}."""
    m = WIDTH // k
    pooled = w.astype(np.float64).reshape(m, k, m, k).mean(axis=(1, 3))
    return (pooled * k ** 1.5).astype(np.float32)


def pool_input(w: np.ndarray, k: int) -> np.ndarray:
    """Average k adjacent OUTPUT columns only (input dim stays 256),
    rescaled by sqrt(k)."""
    m = WIDTH // k
    pooled = w.astype(np.float64).reshape(WIDTH, m, k).mean(axis=2)
    return (pooled * math.sqrt(k)).astype(np.float32)


def build_surrogate(weights: list[np.ndarray], k: int) -> list[np.ndarray]:
    return [pool_input(weights[0], k)] + [
        pool_hidden(weights[layer], k) for layer in range(1, DEPTH)
    ]


def variance_check(weights: list[np.ndarray], surrogate: list[np.ndarray],
                   k: int) -> dict:
    """Empirical pooled-entry variance vs the He target, pre-rescale target
    algebra folded in: we check the RESCALED matrices against He for the
    pooled width directly."""
    m = pooled_width(k)
    hidden_vars = [float(np.var(s)) for s in surrogate[1:]]
    return {
        "k": k,
        "pooled_width": m,
        "hidden_var_mean_empirical": float(np.mean(hidden_vars)),
        "hidden_var_he_target": 2.0 / m,
        "hidden_var_ratio": float(np.mean(hidden_vars) / (2.0 / m)),
        "input_var_empirical": float(np.var(surrogate[0])),
        "input_var_he_target": 2.0 / WIDTH,
        "input_var_ratio": float(np.var(surrogate[0]) / (2.0 / WIDTH)),
    }


# --------------------------------------------------------------- forward
def forward_neuron_mean(weights: list[np.ndarray], first_eff: np.ndarray,
                        points: np.ndarray) -> np.ndarray:
    """Per-direction mean over the final layer's post-ReLU neurons.
    Mirrors the champion forward (f32 matmuls, rotated first matmul); the
    antipodal branches are supplied by the subsample itself (drawn from the
    doubled design)."""
    act = np.maximum(points @ first_eff, np.float32(0.0))
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    return act.mean(axis=1, dtype=np.float64)


# ------------------------------------------------------------- statistics
def pearson(a: np.ndarray, b: np.ndarray) -> float:
    r = float(np.corrcoef(a, b)[0, 1])
    # Second-way recompute from raw float64 sums (internal consistency).
    n = a.size
    sa, sb = a.sum(), b.sum()
    saa, sbb, sab = (a * a).sum(), (b * b).sum(), (a * b).sum()
    cov = sab / n - (sa / n) * (sb / n)
    r2 = cov / math.sqrt((saa / n - (sa / n) ** 2) * (sbb / n - (sb / n) ** 2))
    if abs(r - r2) > 1e-12:
        raise RuntimeError(f"pearson cross-check failed: {r} vs {r2}")
    return r


def cosine_raw(a: np.ndarray, b: np.ndarray) -> float:
    return float((a * b).sum()
                 / math.sqrt((a * a).sum() * (b * b).sum()))


def mfmc_gain(rho: float, w: float) -> float:
    ratio = (math.sqrt(max(1.0 - rho * rho, 0.0))
             + math.sqrt(w) * abs(rho)) ** 2
    return 1.0 / ratio


def rho_threshold_for_gain(gain: float, w: float) -> float:
    """Smallest |rho| with mfmc_gain(rho, w) >= gain (closed form from the
    quadratic in the docstring derivation)."""
    s = 1.0 / math.sqrt(gain)
    disc = s * s * w - (1.0 + w) * (s * s - 1.0)
    return (s * math.sqrt(w) + math.sqrt(disc)) / (1.0 + w)


# ------------------------------------------------------------------ main
def main() -> None:
    t_start = time.perf_counter()
    kerdock = n8a.load_kerdock_directions()               # (32256, 256)
    doubled = np.concatenate((kerdock, -kerdock), axis=0)  # (64512, 256)
    perm = np.random.default_rng(SUBSAMPLE_SEED).permutation(doubled.shape[0])
    idx_primary = perm[:N_SUB]
    idx_resample = perm[N_SUB:2 * N_SUB]                  # disjoint
    subsets = {
        "primary": doubled[idx_primary].astype(np.float32),
        "resample": doubled[idx_resample].astype(np.float32),
    }

    w_by_k = {k: cost_ratio(k) for k in POOL_KS}
    results: dict = {
        "ledger_id": "s13_width_pooled_mfmc_premise",
        "date": "2026-08-09",
        "firewall": (
            "synthetic He nets only; frozen n8a sources imported read-only "
            "(sys.dont_write_bytecode set); only n8a's shipped sampling asset "
            "read; no dataset/truth/scorer/submission; no git; writes "
            "confined to s13_width_pooled_mfmc/"
        ),
        "design": {
            "n_directions_doubled": int(doubled.shape[0]),
            "n_sub": N_SUB,
            "subsample_seed": SUBSAMPLE_SEED,
            "resample_disjoint": True,
            "rotation_seed_formula": "900000 + net*1000 + 0",
        },
        "cost_model": {
            "macs_per_direction_full": MACS_FULL,
            "macs_per_direction_pooled64": WIDTH * 64 + (DEPTH - 1) * 64 * 64,
            "macs_per_direction_pooled128": WIDTH * 128 + (DEPTH - 1) * 128 * 128,
            "w64": w_by_k[4], "w64_exact": "35/512",
            "w128": w_by_k[2], "w128_exact": "33/128",
        },
        "mfmc_formula": (
            "two-model Peherstorfer, optimal alpha=rho*sig_g/sig_h and "
            "optimal allocation: variance ratio vs single-model MC at "
            "matched budget = (sqrt(1-rho^2) + sqrt(w)*|rho|)^2; "
            "gain = 1/ratio; feasibility n2>=n1 iff rho^2 >= w/(1+w); "
            "gain>1 iff |rho| > 2*sqrt(w)/(1+w)"
        ),
        "rho_thresholds": {
            f"k{k}": {
                "any_gain": 2.0 * math.sqrt(w) / (1.0 + w),
                "gain_1.1": rho_threshold_for_gain(1.1, w),
                "gain_1.3": rho_threshold_for_gain(1.3, w),
            }
            for k, w in w_by_k.items()
        },
        "construction_checks": {},
        "per_net": {},
    }

    boot_rng = np.random.default_rng(BOOTSTRAP_SEED)
    # gain bootstrap draws per net/variant (primary subset), kept for aggregate
    boot_gains: dict[int, dict[int, np.ndarray]] = {}

    for seed in NET_SEEDS:
        weights = n8a.he_mlp_weights(seed)
        rotation = n8a.haar_rotation(900_000 + seed * 1_000 + 0)
        first_eff_full = (rotation.T @ weights[0]).astype(np.float32)

        g = {name: forward_neuron_mean(weights, first_eff_full, pts)
             for name, pts in subsets.items()}

        net_row: dict = {
            "sigma_g_primary": float(np.std(g["primary"], ddof=1)),
            "mean_g_primary": float(np.mean(g["primary"])),
            "variants": {},
        }
        results["construction_checks"][str(seed)] = []
        boot_gains[seed] = {}

        for k in POOL_KS:
            surrogate = build_surrogate(weights, k)
            results["construction_checks"][str(seed)].append(
                variance_check(weights, surrogate, k)
            )
            first_eff_p = (rotation.T @ surrogate[0]).astype(np.float32)
            h = {name: forward_neuron_mean(surrogate, first_eff_p, pts)
                 for name, pts in subsets.items()}

            w = w_by_k[k]
            rho_p = pearson(g["primary"], h["primary"])
            rho_r = pearson(g["resample"], h["resample"])

            # bootstrap over directions (primary subset)
            draws_rho = np.empty(BOOTSTRAP_DRAWS)
            for b in range(BOOTSTRAP_DRAWS):
                idx = boot_rng.integers(0, N_SUB, size=N_SUB)
                gg, hh = g["primary"][idx], h["primary"][idx]
                c = np.corrcoef(gg, hh)[0, 1]
                draws_rho[b] = c
            draws_gain = np.array([mfmc_gain(r, w) for r in draws_rho])
            boot_gains[seed][k] = draws_gain

            net_row["variants"][f"pooled{pooled_width(k)}"] = {
                "k": k,
                "w": w,
                "sigma_h_primary": float(np.std(h["primary"], ddof=1)),
                "mean_h_primary": float(np.mean(h["primary"])),
                "rho_pearson_primary": rho_p,
                "rho_pearson_resample": rho_r,
                "rho_bootstrap_ci95": [
                    float(np.percentile(draws_rho, 2.5)),
                    float(np.percentile(draws_rho, 97.5)),
                ],
                "cosine_raw_primary": cosine_raw(g["primary"], h["primary"]),
                "feasible_n2_ge_n1": bool(rho_p * rho_p >= w / (1.0 + w)),
                "mfmc_gain_primary": mfmc_gain(rho_p, w),
                "mfmc_gain_resample": mfmc_gain(rho_r, w),
                "mfmc_gain_bootstrap_ci95": [
                    float(np.percentile(draws_gain, 2.5)),
                    float(np.percentile(draws_gain, 97.5)),
                ],
            }
            print(
                f"net {seed} pooled-{pooled_width(k)}: "
                f"rho={rho_p:+.4f} (resample {rho_r:+.4f})  "
                f"gain={mfmc_gain(rho_p, w):.4f}x  "
                f"cos_raw={cosine_raw(g['primary'], h['primary']):.4f}",
                flush=True,
            )
        results["per_net"][str(seed)] = net_row

    # ------------------------------------------------------------ aggregate
    agg = {}
    for k in POOL_KS:
        wname = f"pooled{pooled_width(k)}"
        gains_p = [results["per_net"][str(s)]["variants"][wname]
                   ["mfmc_gain_primary"] for s in NET_SEEDS]
        gains_r = [results["per_net"][str(s)]["variants"][wname]
                   ["mfmc_gain_resample"] for s in NET_SEEDS]
        stacked = np.stack([boot_gains[s][k] for s in NET_SEEDS])
        geo_draws = np.exp(np.log(stacked).mean(axis=0))
        agg[wname] = {
            "geomean_gain_primary": float(np.exp(np.mean(np.log(gains_p)))),
            "geomean_gain_resample": float(np.exp(np.mean(np.log(gains_r)))),
            "geomean_gain_bootstrap_ci95": [
                float(np.percentile(geo_draws, 2.5)),
                float(np.percentile(geo_draws, 97.5)),
            ],
            "per_net_gains_primary": gains_p,
        }
    results["aggregate"] = agg

    gate_gain = agg["pooled64"]["geomean_gain_primary"]
    if gate_gain >= 1.3:
        outcome = "ARM_PROPOSAL"
    elif gate_gain < 1.1:
        outcome = "WIDTH_FIDELITY_CLOSED"
    else:
        outcome = "INCONCLUSIVE"
    results["gate"] = {
        "thresholds": {"arm": 1.3, "closed_below": 1.1},
        "metric": "geomean over nets of closed-form MFMC gain, width-64 "
                  "pooled surrogate, matched billed FLOPs",
        "value": gate_gain,
        "outcome": outcome,
    }
    results["wall_s"] = round(time.perf_counter() - t_start, 1)

    out = HERE / "s13_results.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nGATE: geomean width-64 MFMC gain = {gate_gain:.4f}x "
          f"-> {outcome}")
    print(f"results written to {out}  ({results['wall_s']}s)")


if __name__ == "__main__":
    main()
