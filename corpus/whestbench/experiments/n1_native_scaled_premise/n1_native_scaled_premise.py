"""N1 premise (Track A2+, predeclared): the wipe-the-floor mechanism test.

MECHANISM (one causal step): the board leaders' raw-MSE altitude (~5.2e-8) is
reachable by SAMPLE COUNT priced through the wall-time channel (Rules 5.2:
any library/backend is legal, priced by residual wall at 1e11 FLOP-eq/s).
Champion variance v = MSE*N ~= 0.0199; the fixed-frame design floor scales
1/N; the wall budget under C <= B is ~2.7 s/MLP. A raw-numpy (un-instrumented,
wall-priced) threaded forward pass turns those seconds into 300k-1M samples
instead of 64,512.

PREDICTION: on a generated He-Gaussian d=256 L=32 MLP with own-MC truth,
final-layer MSE of a plain antipodal Gaussian-bank sampler scales ~1/N from
64k through 512k samples with no bias plateau above ~1e-8, and the raw-path
forward at 512k samples costs a wall time that projects under the ~2.7 s
budget on 16-vCPU grading hardware (this laptop gives a lower bound).

KILL CONDITIONS: (1) MSE plateaus >2x above the 1/N line by 512k (hidden bias
floor); (2) local wall at 512k exceeds ~20 s (making 16-vCPU projection
implausible); (3) nondeterminism across reruns with fixed seeds.

RESPONSE-FREE + LEGAL: generated weights, own Monte-Carlo truth, no challenge
data, no scorer, no burned rows, no FlopScope tampering (the raw path is the
explicitly-permitted 'any other library' channel; a production candidate would
carry the full disclosure document). Champion unchanged.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WIDTH = 256
DEPTH = 32
BLOCK = 65_536          # row-block: (65536, 256) f32 = 64 MiB, under liveness caps


def gen_mlp(seed: int):
    rng = np.random.default_rng(seed)
    gain = np.sqrt(2.0 / WIDTH).astype(np.float32) if hasattr(np.sqrt(2.0 / WIDTH), "astype") else np.float32(np.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * np.float32(gain))
        for _ in range(DEPTH)
    ]


def forward_final_mean(weights, n_pairs: int, seed: int):
    """Antipodal plain-MC estimate of the final post-ReLU mean using the raw
    numpy path (wall-priced channel). n_pairs antipodal pairs = 2*n_pairs
    effective samples. Row-blocked to bound liveness. Returns (mean, wall_s)."""
    rng = np.random.default_rng(seed)
    total = np.zeros(WIDTH, dtype=np.float64)
    count = 0
    t0 = time.perf_counter()
    done = 0
    while done < n_pairs:
        b = min(BLOCK, n_pairs - done)
        z = rng.standard_normal((b, WIDTH), dtype=np.float32)
        x = np.concatenate((z, -z), axis=0)
        for W in weights:
            x = np.maximum(x @ W, np.float32(0.0), out=None)
        total += x.sum(axis=0, dtype=np.float64)
        count += 2 * b
        done += b
    wall = time.perf_counter() - t0
    return total / count, wall


def main():
    weights = gen_mlp(seed=20260807)

    # ground truth: 4M antipodal pairs = 8M samples; truth MSE ~ v/8e6 ~ 2.5e-9
    truth, truth_wall = forward_final_mean(weights, n_pairs=4_000_000, seed=999)
    print(f"truth: 8.0M samples, wall {truth_wall:.1f}s")

    results = []
    for n_pairs in (32_256, 64_512, 129_024, 258_048):
        mses = []
        walls = []
        for rep, seed in enumerate((1, 2, 3)):
            est, wall = forward_final_mean(weights, n_pairs=n_pairs, seed=seed)
            mses.append(float(np.mean((est - truth) ** 2)))
            walls.append(wall)
        n_eff = 2 * n_pairs
        mse = float(np.mean(mses))
        results.append({
            "n_samples": n_eff,
            "mse_mean_of_3": mse,
            "mse_reps": mses,
            "wall_s_min": min(walls),
            "v_implied": mse * n_eff,
        })
        print(f"N={n_eff:>7,}  MSE={mse:.3e}  v={mse*n_eff:.4f}  wall={min(walls):.2f}s")

    # scaling check: v = MSE*N should be ~constant if 1/N holds
    v = [r["v_implied"] for r in results]
    scaling_flat = max(v) / min(v)
    # determinism check
    e1, _ = forward_final_mean(weights, n_pairs=32_256, seed=42)
    e2, _ = forward_final_mean(weights, n_pairs=32_256, seed=42)
    deterministic = bool(np.array_equal(e1, e2))

    # projection: champion-variance sampler at the same N (v_champ = 0.0199)
    v_champ = 0.0199
    proj = {f"N={n:,}": v_champ / n for n in (64_512, 258_048, 516_096, 1_032_192)}

    out = {
        "premise": "wall-priced sample scaling",
        "truth_samples": 8_000_000,
        "results": results,
        "v_ratio_max_over_min": scaling_flat,
        "scaling_1_over_N_holds": bool(scaling_flat < 1.5),
        "deterministic_fixed_seed": deterministic,
        "champion_variance_projection_raw_mse": proj,
        "note": ("local wall is a LOWER bound on grading throughput (16 vCPU); "
                 "projection to leaders' altitude needs N>=4x champion plus "
                 "existing controls; production candidate carries disclosure"),
    }
    (HERE / "N1_PREMISE_RESULTS.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("v_ratio_max_over_min",
                                          "scaling_1_over_N_holds",
                                          "deterministic_fixed_seed")}, indent=1))
    print("champion-variance projections:", json.dumps(proj, indent=1))


if __name__ == "__main__":
    main()
