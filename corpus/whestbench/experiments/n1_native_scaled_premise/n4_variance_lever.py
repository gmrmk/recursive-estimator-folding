"""N4 (predeclared): measure the v-lever end-to-end.

The N3 formula adjusted = v * 8.74e-6 / S makes variance-per-sample v a linear
score lever. This measures the REAL v of successive variance-reduction stages
on a generated d=256/L=32 network, converting the N3 "v ~ 0.004-0.01 assumed"
into a measured number. Each stage that cuts v halves the throughput bar S.

Stages (all UNBIASED so v is a clean variance, no bias floor; the champion's
biased pruning is deliberately excluded here to keep the lever honest):
  0. plain iid Gaussian
  1. + antipodal pairing (x and -x)
  2. + exact radial control (project each row to the chi_256 mean radius; the
     champion's spectral-radial idea, unbiased under isotropic input)
  3. + RQMC: scrambled-Sobol Gaussian instead of iid (variance reduction from
     low-discrepancy points)

v is reported as MSE * N (N = effective samples). LOWER v = better lever.
Kill/skepticism: v estimates are noisy (N2 showed 70% per-rep); use 40 reps
and report the standard error so no stage-ordering claim rests on noise.

Response-free: generated weights, own high-N MC truth. No challenge data.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WIDTH, DEPTH = 256, 32


def gen_mlp(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(np.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * g for _ in range(DEPTH)]


def forward(weights, x):
    for W in weights:
        x = np.maximum(x @ W, np.float32(0.0))
    return x


MEAN_RADIUS = math.exp(0.5 * math.log(2.0)
                       + math.lgamma((WIDTH + 1.0) / 2.0)
                       - math.lgamma(WIDTH / 2.0))


def draw(kind, n_pairs, rng, sobol=None):
    """Return a (2*n_pairs, WIDTH) f32 sample matrix for the given estimator."""
    if kind == "plain":
        z = rng.standard_normal((2 * n_pairs, WIDTH), dtype=np.float32)
        return z
    z = rng.standard_normal((n_pairs, WIDTH), dtype=np.float32)
    if kind in ("radial", "antipodal"):
        pass
    if kind == "rqmc":
        # scrambled-Sobol -> Gaussian via the EXACT inverse normal CDF
        # (scipy.special.ndtri); a crude inverse-CDF would bias the estimate.
        from scipy.stats import qmc      # optional; skipped if absent
        from scipy.special import ndtri
        eng = qmc.Sobol(d=WIDTH, scramble=True, seed=int(rng.integers(1 << 31)))
        u = eng.random(n_pairs).astype(np.float64)
        u = np.clip(u, 1e-12, 1 - 1e-12)
        z = ndtri(u).astype(np.float32)
    if kind == "radial":
        r = np.sqrt(np.sum(z * z, axis=1, keepdims=True))
        z = z * np.float32(MEAN_RADIUS) / np.maximum(r, np.float32(1e-12))
    return np.concatenate((z, -z), axis=0)  # antipodal for all non-plain


def _erfinv(y):
    # rational approx; only used for the RQMC Gaussianization reference
    a = 0.147
    ln = np.log(1 - y * y)
    t = 2 / (math.pi * a) + ln / 2
    return np.sign(y) * np.sqrt(np.sqrt(t * t - ln / a) - t)


def measure_v(weights, kind, truth, n_pairs, reps, seed0):
    n_eff = 2 * n_pairs
    mses = []
    for rep in range(reps):
        rng = np.random.default_rng(seed0 + rep)
        try:
            x = forward(weights, draw(kind, n_pairs, rng))
        except ImportError:
            return None
        est = x.mean(axis=0)
        mses.append(float(np.mean((est - truth) ** 2)))
    mses = np.array(mses)
    v = float(mses.mean()) * n_eff
    v_sem = float(mses.std(ddof=1) / math.sqrt(reps)) * n_eff
    return {"kind": kind, "v": v, "v_sem": v_sem, "n_eff": n_eff, "reps": reps}


def main():
    weights = gen_mlp(20260807)
    t0 = time.perf_counter()
    truth = forward(weights, np.concatenate(
        (np.random.default_rng(999).standard_normal((3_000_000, WIDTH), dtype=np.float32),),
        axis=0)).mean(axis=0)
    truth_wall = time.perf_counter() - t0

    n_pairs, reps, seed0 = 32_256, 40, 5000
    stages = {}
    for kind in ("plain", "antipodal", "radial", "rqmc"):
        r = measure_v(weights, kind, truth, n_pairs, reps, seed0)
        if r is None:
            stages[kind] = {"kind": kind, "skipped": "scipy.qmc unavailable"}
            print(f"{kind:10s} SKIPPED (scipy.qmc unavailable)")
            continue
        stages[kind] = r
        # S bar to reach joe_wanza 7.39e-9 at this v
        s_needed = r["v"] * 8.739e-6 / 7.39e-9
        print(f"{kind:10s} v={r['v']:.4f} +/- {r['v_sem']:.4f}   "
              f"S_needed(joe_wanza)={s_needed:.1f}x")

    out = {
        "truth_samples": 3_000_000, "truth_wall_s": round(truth_wall, 1),
        "n_eff": 2 * n_pairs, "reps": reps,
        "constant_v_per_S": 8.739e-6,
        "stages": stages,
        "note": ("v = MSE*N, unbiased stages so v is a clean variance; lower is "
                 "better. S_needed at joe_wanza = v*8.739e-6/7.39e-9. RQMC needs "
                 "scipy.qmc; if absent the stage is skipped and reported as such."),
    }
    (HERE / "N4_RESULTS.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (v.get("v") if isinstance(v, dict) else v)
                      for k, v in stages.items()}, indent=1))


if __name__ == "__main__":
    main()
