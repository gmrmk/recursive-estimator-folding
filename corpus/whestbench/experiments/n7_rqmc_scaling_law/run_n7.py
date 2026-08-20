"""N7: RQMC (Kronecker lattice + Cranley-Patterson) MSE-vs-N slope at depth 32.

Predeclared in N7_PREDECLARATION.md. Response-free.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

WIDTH, DEPTH = 256, 32
SEEDS = [11, 22]
NS = [4096, 16384, 65536, 262144]
R = 6
N_TRUTH = 3_500_000
HERE = Path(__file__).resolve().parent


def gen_net(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(math.sqrt(2.0 / WIDTH))
    return [(rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * g) for _ in range(DEPTH)]


def forward_mean(w, X):
    a = X
    for W in w:
        a = np.maximum(a @ W, np.float32(0.0))
    return a.astype(np.float64).mean(axis=0)


def forward_mean_chunked(w, n, rng, chunk=65536):
    s = np.zeros(WIDTH)
    done = 0
    while done < n:
        m = min(chunk, n - done)
        s += forward_mean(w, rng.standard_normal((m, WIDTH)).astype(np.float32)) * m
        done += m
    return s / n


# Acklam's inverse normal CDF (vectorized, ~1.15e-9 rel err) — no scipy needed.
_A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
      1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
_B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
      6.680131188771972e+01, -1.328068155288572e+01]
_C = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
      -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
_D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
      3.754408661907416e+00]


def ndtri(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    out = np.empty_like(p)
    lo = p < 0.02425
    hi = p > 1 - 0.02425
    mid = ~(lo | hi)
    q = np.sqrt(-2 * np.log(p[lo]))
    out[lo] = ((((( _C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]) / \
              (((( _D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1)
    q = np.sqrt(-2 * np.log(1 - p[hi]))
    out[hi] = -((((( _C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]) / \
               (((( _D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1)
    q = p[mid] - 0.5
    r = q * q
    out[mid] = ((((( _A[0]*r + _A[1])*r + _A[2])*r + _A[3])*r + _A[4])*r + _A[5]) * q / \
               ((((( _B[0]*r + _B[1])*r + _B[2])*r + _B[3])*r + _B[4])*r + 1)
    return out


def kronecker_alpha(d, seed=7):
    # Golden-ratio-family irrationals: alpha_j = frac(sqrt(prime_j))
    primes = []
    x = 2
    while len(primes) < d:
        if all(x % p for p in primes):
            primes.append(x)
        x += 1
    return np.array([math.sqrt(p) % 1.0 for p in primes])


ALPHA = kronecker_alpha(WIDTH)


def rqmc_mean(w, n, rep_rng):
    """Antithetic Kronecker lattice with a Cranley-Patterson shift."""
    half = n // 2
    shift = rep_rng.random(WIDTH)
    i = np.arange(half)[:, None]
    u = (i * ALPHA[None, :] + shift[None, :]) % 1.0
    z = ndtri(u).astype(np.float32)
    m1 = forward_mean(w, z)
    m2 = forward_mean(w, -z)
    return 0.5 * (m1 + m2)


def mc_mean(w, n, rep_rng):
    half = n // 2
    z = rep_rng.standard_normal((half, WIDTH)).astype(np.float32)
    return 0.5 * (forward_mean(w, z) + forward_mean(w, -z))


def main():
    out = {"predeclaration": "N7_PREDECLARATION.md", "nets": []}
    for seed in SEEDS:
        w = gen_net(seed)
        t0 = time.perf_counter()
        truth = forward_mean_chunked(w, N_TRUTH, np.random.default_rng(9000 + seed))
        t_truth = time.perf_counter() - t0
        truth_noise = 0.02 / N_TRUTH  # ~5.7e-9, refined below
        rows = []
        for n in NS:
            for label, fn in (("mc", mc_mean), ("rqmc", rqmc_mean)):
                errs = []
                for r in range(R):
                    rep = np.random.default_rng(seed * 1000 + n + r * 17 + (0 if label == "mc" else 500))
                    m = fn(w, n, rep)
                    errs.append(float(np.mean((m - truth) ** 2)))
                mse = float(np.mean(errs))
                rows.append({"n": n, "kind": label, "mse": mse})
                print(f"seed {seed} {label:>4} N={n:>6}: MSE={mse:.4e}", flush=True)
        # slopes over uncensored points (mse > 5x truth noise)
        fits = {}
        for label in ("mc", "rqmc"):
            pts = [(math.log(r["n"]), math.log(r["mse"])) for r in rows
                   if r["kind"] == label and r["mse"] > 5 * truth_noise]
            if len(pts) >= 3:
                x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
                beta = float(np.polyfit(x, y, 1)[0])
            else:
                beta = None
            fits[label] = beta
            print(f"seed {seed} slope beta_{label} = {beta}", flush=True)
        out["nets"].append({"seed": seed, "truth_n": N_TRUTH, "truth_wall_s": t_truth,
                            "rows": rows, "beta": fits})
    (HERE / "n7_results.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote n7_results.json", flush=True)


if __name__ == "__main__":
    main()
