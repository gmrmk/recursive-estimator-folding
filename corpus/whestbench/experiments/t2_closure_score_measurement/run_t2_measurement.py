"""T2: full-covariance closure depth-32 raw MSE + wall -> floor-conditional verdict.

Predeclared in T2_PREDECLARATION.md (written before this file). Response-free:
self-generated He-init f32 networks + own Monte-Carlo truth. Consumes the
certified M179 zero-order recurrence unmodified.

Usage: python run_t2_measurement.py [--probe]   (--probe: time one layer, exit)
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
M179 = HERE.parent / "m179_background_archive_producer"
sys.path.insert(0, str(M179))

from m179_background_producer import zero_order_recurrence  # noqa: E402

WIDTH = 256
DEPTH = 32
BILLED_FLOPS = 8.30e9          # M179 G4 inclusive ledger (reported-level carry)
B = 2.72e11
L2_ADJ = 2.101976249e-7        # slot-1 candidate to beat
SEEDS = [101, 202, 303]        # same nets as the diagonal calibration run
N_MC = 400_000


def gen_net(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(math.sqrt(2.0 / WIDTH))
    return [(rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * g)
            for _ in range(DEPTH)]


def true_mc_final(weights, n_total, seed, chunk=50_000):
    rng = np.random.default_rng(seed)
    s1 = np.zeros(WIDTH)
    s2 = np.zeros(WIDTH)
    done = 0
    while done < n_total:
        m = min(chunk, n_total - done)
        a = rng.standard_normal((m, WIDTH)).astype(np.float32)
        for W in weights:
            a = np.maximum(a @ W, np.float32(0.0))
        a64 = a.astype(np.float64)
        s1 += a64.sum(axis=0)
        s2 += (a64 * a64).sum(axis=0)
        done += m
    mean = s1 / n_total
    var = np.maximum(s2 / n_total - mean * mean, 0.0)
    return mean, var / n_total


def main():
    if "--probe" in sys.argv:
        w = gen_net(SEEDS[0])
        t0 = time.perf_counter()
        from m179_background_producer import relu_moments
        a = np.zeros(WIDTH)
        C = np.eye(WIDTH)
        a1 = a @ np.asarray(w[0], dtype=np.float64)
        C1 = np.asarray(w[0], dtype=np.float64).T @ C @ np.asarray(w[0], dtype=np.float64)
        relu_moments(a1, C1)
        print(f"one-layer relu_moments wall: {time.perf_counter() - t0:.3f} s "
              f"(x{DEPTH - 1} layers ~ full-net closure estimate)", flush=True)
        return

    rows = []
    for seed in SEEDS:
        w = gen_net(seed)
        t0 = time.perf_counter()
        states = zero_order_recurrence(w)
        wall = time.perf_counter() - t0
        mu_pred = states[-1].mu
        mc, se2 = true_mc_final(w, N_MC, seed=1000 + seed)
        raw = float(np.mean((mu_pred - mc) ** 2))
        floor_mc = float(np.mean(se2))
        bias = max(raw - floor_mc, 0.0)
        rows.append({"seed": seed, "raw_mse": raw, "mc_floor": floor_mc,
                     "bias_mse": bias, "closure_wall_s": wall})
        print(f"seed {seed}: closure_MSE={raw:.4e}  MC_floor={floor_mc:.3e}  "
              f"bias~={bias:.4e}  closure_wall={wall:.2f}s", flush=True)

    bias_mean = float(np.mean([r["bias_mse"] for r in rows]))
    wall_mean = float(np.mean([r["closure_wall_s"] for r in rows]))
    C_eff = BILLED_FLOPS + 1e11 * wall_mean
    out = {"rows": rows, "bias_mse_mean": bias_mean, "wall_mean_s": wall_mean,
           "billed_flops_carry": BILLED_FLOPS, "C_eff": C_eff,
           "l2_adjusted_to_beat": L2_ADJ, "verdicts": {}}
    print(f"\n=== T2 VERDICT (bias_MSE mean {bias_mean:.4e}, "
          f"closure wall mean {wall_mean:.2f}s, C_eff {C_eff:.3e}) ===", flush=True)
    for floor in (0.1, 0.5):
        mult = max(floor, C_eff / B)
        adj = bias_mean * mult
        win = adj < L2_ADJ
        out["verdicts"][str(floor)] = {"multiplier": mult, "adjusted": adj, "beats_l2": win}
        print(f"floor {floor}: multiplier={mult:.4f}  adjusted={adj:.4e}  "
              f"beats L2 ({L2_ADJ:.4e})? {'YES' if win else 'NO'}", flush=True)
    k1 = bias_mean >= 2.102e-6
    k3 = not all(r["bias_mse"] >= 5 * r["mc_floor"] for r in rows)
    print(f"kill gates: K1 (bias>=2.102e-6): {'FIRED' if k1 else 'clear'};  "
          f"K3 (MC floor not 5x below): {'FIRED' if k3 else 'clear'}", flush=True)
    (HERE / "t2_results.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote t2_results.json", flush=True)


if __name__ == "__main__":
    main()
