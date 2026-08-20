"""N2 (predeclared follow-up to N1): resolve the two real questions N1 surfaced
— native THROUGHPUT (the binding constraint) and properly-powered v-scaling.

N1 fired its gate on 3-rep noise; the mechanism (unbiased MC -> flat v -> 1/N)
is sound by construction. N2 (a) measures the best achievable forward
throughput on this machine (all BLAS cores, f32, warm), (b) confirms v is flat
with 20 reps against a saved MC truth, and (c) projects the grading-hardware
speedup required to fit the floor-reaching sample count in the ~2.72 s budget.

Response-free: generated weights, own MC truth. No challenge data, scorer, or
burned rows. Deploy stays organizer- and user-gated.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WIDTH, DEPTH = 256, 32
FLOPS_PER_SAMPLE = DEPTH * 2 * WIDTH * WIDTH   # 2 per MAC, 32 layers
BUDGET_S = 2.72                                 # C <= B at 1e11 FLOP-eq/s, billed~0


def blas_info():
    try:
        cfg = np.__config__.show(mode="dicts")  # numpy >= 2
        return {k: v.get("name") for k, v in cfg.get("Build Dependencies", {}).items()
                if isinstance(v, dict)}
    except Exception:
        return {"threads_env": {k: os.environ.get(k) for k in
                ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}


def gen_mlp(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(np.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * g for _ in range(DEPTH)]


def forward(weights, x):
    for W in weights:
        x = np.maximum(x @ W, np.float32(0.0))
    return x


def measure_throughput(weights, batch=131072, runs=5):
    """Best warm samples/sec and effective GFLOP/s of the f32 forward."""
    z = np.random.default_rng(0).standard_normal((batch, WIDTH), dtype=np.float32)
    forward(weights, z)                          # warm
    best = 1e18
    for _ in range(runs):
        t0 = time.perf_counter()
        forward(weights, z)
        best = min(best, time.perf_counter() - t0)
    sps = batch / best
    gflops = (batch * FLOPS_PER_SAMPLE) / best / 1e9
    return {"batch": batch, "best_wall_s": best, "samples_per_s": sps,
            "gflops": gflops, "us_per_sample": 1e6 * best / batch}


def mc_truth(weights, n_pairs, seed, block=131072):
    rng = np.random.default_rng(seed)
    total = np.zeros(WIDTH, dtype=np.float64)
    done = 0
    while done < n_pairs:
        b = min(block, n_pairs - done)
        z = rng.standard_normal((b, WIDTH), dtype=np.float32)
        x = forward(weights, np.concatenate((z, -z), axis=0))
        total += x.sum(axis=0, dtype=np.float64)
        done += b
    return total / (2 * n_pairs)


def estimate(weights, n_pairs, seed):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n_pairs, WIDTH), dtype=np.float32)
    x = forward(weights, np.concatenate((z, -z), axis=0))
    return x.mean(axis=0)


def main():
    weights = gen_mlp(20260807)

    tput = measure_throughput(weights)

    # properly-powered v: 20 reps at N=64,512 against a 3M-pair truth
    truth = mc_truth(weights, n_pairs=3_000_000, seed=999)
    n_pairs = 32_256                              # 64,512 samples, champion N
    mses = []
    for rep in range(20):
        est = estimate(weights, n_pairs, seed=1000 + rep)
        mses.append(float(np.mean((est - truth) ** 2)))
    mse_mean = float(np.mean(mses))
    mse_sd = float(np.std(mses))
    v = mse_mean * 2 * n_pairs

    # projections at the MEASURED throughput
    sps = tput["samples_per_s"]
    def N_for(target_mse, v_est):
        return v_est / target_mse
    def wall_for(N):
        return N / sps
    targets = {}
    for name, mse_t in (("skibidi_9.24e-8", 9.24e-8), ("joewanza_5.21e-8", 5.21e-8),
                        ("beat_top12_4.09e-8", 4.09e-8), ("stretch_2.0e-8", 2.0e-8)):
        for fam, v_est in (("plain", v), ("champion_0.0199", 0.0199)):
            N = N_for(mse_t, v_est)
            w = wall_for(N)
            targets[f"{name}|{fam}"] = {
                "N": int(N), "wall_local_s": round(w, 2),
                "speedup_needed_vs_budget": round(w / BUDGET_S, 2)}

    out = {
        "blas": blas_info(),
        "throughput": tput,
        "v_plain_20rep": {"mse_mean": mse_mean, "mse_sd": mse_sd,
                          "v": v, "rel_sd": mse_sd / mse_mean},
        "champion_v_ref": 0.0199,
        "budget_s": BUDGET_S,
        "projections": targets,
        "reading": ("wall_local is on THIS machine; speedup_needed is the factor "
                    "the grading hardware + native kernel must beat this numpy "
                    "forward to fit the budget. A graded baseline submission is "
                    "the only measure of grading throughput."),
    }
    (HERE / "N2_RESULTS.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({
        "gflops": round(tput["gflops"], 1),
        "us_per_sample": round(tput["us_per_sample"], 3),
        "v_plain": round(v, 4), "v_rel_sd": round(mse_sd / mse_mean, 3),
        "joewanza_plain": targets["joewanza_5.21e-8|plain"],
        "joewanza_champion": targets["joewanza_5.21e-8|champion_0.0199"],
    }, indent=1))


if __name__ == "__main__":
    main()
