"""K1 (predeclared): the S-lever benchmark -- how fast can the wall-priced
forward run, and how many floor-budget samples does that buy?

The score model is adjusted = v * 8.74e-6 / S with v pinned ~0.0199 and S the
throughput vs the N2 numpy baseline (176.5 GFLOP/s, 23.77 us/sample). #1 needs
S ~ 24x, top-6 ~ 9x. This machine has 16 logical cores (~ the grading box's 16
vCPU), so S is ~all kernel quality, not hardware.

No C compiler / numba / cython in the frozen venv (matches the sandbox), so
this measures the PURE-NUMPY FUSED ceiling (preallocated ping-pong f32 buffers,
in-place ReLU, out= matmuls -- removes N2's per-layer allocation churn) and the
fraction of the 16-core f32 compute peak it reaches. A compiled fused kernel
(bundled per Rules 5.2) is the deployment artifact; its source is written
separately (k1_forward_kernel.c) but cannot be compiled/benchmarked here.

PREDICTION: the numpy-fused forward beats N2's 23.77 us/sample by removing
allocations (modest, ~1.2-2x); the remaining gap to S~24x is the compiled-
kernel headroom (numpy reaches only a small fraction of the AVX f32 peak on
this tall-skinny 256-cube-sequential workload). KILL/DISPOSITION: report the
measured us/sample, GFLOP/s, peak fraction, and the floor-budget sample count +
implied MSE/board-rank -- honestly, whatever it is.

Response-free: generated weights. No challenge data.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WIDTH, DEPTH = 256, 32
FLOPS_PER_SAMPLE = DEPTH * 2 * WIDTH * WIDTH
BUDGET_FLOOR_S = 0.272          # C/B = 0.1 at 1e11 FLOP-eq/s, billed ~ 0
N2_US_PER_SAMPLE = 23.77
V_CHAMPION = 0.0199


def gen(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(np.sqrt(2.0 / WIDTH))
    return [np.ascontiguousarray(rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * g)
            for _ in range(DEPTH)]


def naive_forward(weights, X):
    x = X
    for W in weights:
        x = np.maximum(x @ W, np.float32(0.0))
    return x.mean(axis=0)


def fused_forward(weights, X):
    """Preallocated ping-pong f32 buffers, out= matmul, in-place ReLU."""
    n = X.shape[0]
    a = np.array(X, dtype=np.float32, order="C")
    b = np.empty((n, WIDTH), dtype=np.float32, order="C")
    for W in weights:
        np.dot(a, W, out=b)
        np.maximum(b, np.float32(0.0), out=b)
        a, b = b, a
    return a.mean(axis=0)


def best_us_per_sample(fn, weights, block, runs=5):
    X = np.random.default_rng(0).standard_normal((block, WIDTH)).astype(np.float32)
    fn(weights, X)                      # warm
    best = 1e18
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(weights, X)
        best = min(best, time.perf_counter() - t0)
    return 1e6 * best / block, block * FLOPS_PER_SAMPLE / best / 1e9


def main():
    weights = gen(20260807)

    # correctness: fused == naive to f32 tolerance
    Xc = np.random.default_rng(7).standard_normal((4096, WIDTH)).astype(np.float32)
    err = float(np.max(np.abs(fused_forward(weights, Xc) - naive_forward(weights, Xc))))

    rows = {}
    for name, fn in (("naive_N2style", naive_forward), ("fused_prealloc", fused_forward)):
        rows[name] = {}
        for block in (16384, 65536, 131072, 262144):
            us, gflops = best_us_per_sample(fn, weights, block)
            rows[name][block] = {"us_per_sample": round(us, 3), "gflops": round(gflops, 1)}

    best_fused = min(rows["fused_prealloc"].values(), key=lambda r: r["us_per_sample"])
    us = best_fused["us_per_sample"]
    S = N2_US_PER_SAMPLE / us
    # floor-budget sample count at this us, and implied MSE / board rank
    n_floor = BUDGET_FLOOR_S / (us * 1e-6)
    mse_floor = V_CHAMPION / n_floor
    adjusted_floor = 0.1 * mse_floor      # at the floor multiplier

    out = {
        "cpu_cores": 16,
        "correctness_fused_vs_naive_maxabs": err,
        "throughput_rows": rows,
        "best_fused_us_per_sample": us,
        "best_fused_gflops": best_fused["gflops"],
        "S_vs_N2_baseline": round(S, 2),
        "floor_budget_samples": int(n_floor),
        "implied_raw_mse_at_floor": mse_floor,
        "implied_adjusted_at_floor": adjusted_floor,
        "board_ref": {"top12_cutoff": 4.09e-8, "joewanza": 7.39e-9, "skibidi": 9.2e-9},
        "S_needed_for_ranks_at_v0.0199": {
            "top12_4.09e-8": round(0.0199 * 8.739e-6 / 4.09e-8, 1),
            "skibidi_9.2e-9": round(0.0199 * 8.739e-6 / 9.2e-9, 1),
            "joewanza_7.39e-9": round(0.0199 * 8.739e-6 / 7.39e-9, 1),
        },
        "note": ("numpy-fused ceiling on 16 cores; compiled fused kernel (bundled "
                 "per Rules 5.2) is the deployment artifact, un-benchmarkable here "
                 "(no toolchain). adjusted_at_floor uses this laptop's us/sample; "
                 "grading throughput measurable only by a graded submission."),
    }
    (HERE / "K1_RESULTS.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in (
        "correctness_fused_vs_naive_maxabs", "best_fused_us_per_sample",
        "best_fused_gflops", "S_vs_N2_baseline", "floor_budget_samples",
        "implied_adjusted_at_floor", "S_needed_for_ranks_at_v0.0199")}, indent=1))


if __name__ == "__main__":
    main()
