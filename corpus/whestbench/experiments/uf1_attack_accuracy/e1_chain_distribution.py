"""E1 -- reproduce the U-F1 depth-32 float32 Strassen-Winograd chain drift with
>= 30 seeds and report the DISTRIBUTION, not the 5-seed mean.

Protocol is a byte-for-byte re-use of uf1_attack.py::sw_np and
attack_depth32_chain's geometry (rows=512, width=256, layers=32, He init,
float64 classical reference).  The only change is the seed loop.  Seed
20260810 is included first so the committed uf1_attack.json numbers are
reproduced exactly (bitwise cross-check of the harness).

Extra column collected here, because it is the quantity the SCORE depends on:
the relative error of the COLUMN MEAN of the final activation (the estimator
reports a per-neuron mean, not a per-sample activation).  Its ratio to the
per-element Frobenius drift is the "coherence" of the reassociation error --
1/sqrt(rows) if the error is incoherent across samples, ~1 if systematic.

Read-only w.r.t. everything outside this directory.  Synthetic nets only.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

ROWS = 512
WIDTH = 256
LAYERS = 32
DEPTHS = (0, 1, 2, 3, 4, 5)
GATE_REL = 2e-5
GATE_FRAC = 2e-4


def sw_np(A, B, depth):
    """Verbatim copy of uf1_attack.py::sw_np (Winograd-15, DHSS schedule)."""
    m, k = A.shape[-2], A.shape[-1]
    n = B.shape[-1]
    if depth <= 0 or m % 2 or k % 2 or n % 2:
        return A @ B
    hm, hk, hn = m // 2, k // 2, n // 2
    A11, A12 = A[:hm, :hk], A[:hm, hk:]
    A21, A22 = A[hm:, :hk], A[hm:, hk:]
    B11, B12 = B[:hk, :hn], B[:hk, hn:]
    B21, B22 = B[hk:, :hn], B[hk:, hn:]
    S1 = A21 + A22
    S2 = S1 - A11
    S3 = A11 - A21
    S4 = A12 - S2
    T1 = B12 - B11
    T2 = B22 - T1
    T3 = B22 - B12
    T4 = T2 - B21
    M1 = sw_np(A11, B11, depth - 1)
    M2 = sw_np(A12, B21, depth - 1)
    M3 = sw_np(S4, B22, depth - 1)
    M4 = sw_np(A22, T4, depth - 1)
    M5 = sw_np(S1, T1, depth - 1)
    M6 = sw_np(S2, T2, depth - 1)
    M7 = sw_np(S3, T3, depth - 1)
    U2 = M1 + M6
    U3 = U2 + M7
    U4 = U2 + M5
    C = np.empty((m, n), dtype=A.dtype)
    C[:hm, :hn] = M1 + M2
    C[:hm, hn:] = U4 + M3
    C[hm:, :hn] = U3 - M4
    C[hm:, hn:] = U3 + M5
    return C


def one_seed(seed: int) -> dict:
    rng = np.random.default_rng(seed)
    X0 = np.asarray(rng.standard_normal((ROWS, WIDTH)), dtype="float32")
    Ws = [np.asarray(rng.standard_normal((WIDTH, WIDTH)) * np.sqrt(2.0 / WIDTH),
                     dtype="float32") for _ in range(LAYERS)]
    Xr = X0.astype(np.float64)
    ref_gates = []
    for W in Ws:
        Xr = Xr @ W.astype(np.float64)
        ref_gates.append(Xr > 0)
        Xr = np.maximum(Xr, 0.0)
    ref_colmean = Xr.mean(axis=0)
    out = {}
    for d in DEPTHS:
        X = X0.copy()
        mism = 0
        for i, W in enumerate(Ws):
            X = sw_np(X, W, d)
            mism += int(np.count_nonzero((X > 0) != ref_gates[i]))
            X = np.maximum(X, np.float32(0.0))
        Xd = X.astype(np.float64)
        rel = float(np.linalg.norm(Xd - Xr) / np.linalg.norm(Xr))
        cm = Xd.mean(axis=0)
        rel_cm = float(np.linalg.norm(cm - ref_colmean)
                       / np.linalg.norm(ref_colmean))
        out[f"d{d}"] = {
            "relative_final_error": rel,
            "relative_colmean_error": rel_cm,
            "coherence": rel_cm / rel if rel > 0 else 0.0,
            "gate_mismatch_fraction": mism / (ROWS * WIDTH * LAYERS),
            "passes_rel_gate_2e-5": rel <= GATE_REL,
        }
    return out


def main() -> None:
    seeds = [20260810] + list(range(1, 33))  # 33 seeds, first reproduces committed run
    per_seed = {}
    t0 = time.time()
    for s in seeds:
        per_seed[str(s)] = one_seed(s)
        d4 = per_seed[str(s)]["d4"]["relative_final_error"]
        d5 = per_seed[str(s)]["d5"]["relative_final_error"]
        print(f"seed {s:>9}  d4={d4:.4e} {'PASS' if d4<=GATE_REL else 'FAIL'}"
              f"  d5={d5:.4e} {'PASS' if d5<=GATE_REL else 'FAIL'}"
              f"  [{time.time()-t0:.0f}s]", flush=True)
    summary = {}
    for d in DEPTHS:
        vals = np.array([per_seed[str(s)][f"d{d}"]["relative_final_error"]
                         for s in seeds])
        cms = np.array([per_seed[str(s)][f"d{d}"]["relative_colmean_error"]
                        for s in seeds])
        coh = np.array([per_seed[str(s)][f"d{d}"]["coherence"] for s in seeds])
        summary[f"d{d}"] = {
            "n_seeds": len(seeds),
            "rel_mean": float(vals.mean()),
            "rel_median": float(np.median(vals)),
            "rel_min": float(vals.min()),
            "rel_max": float(vals.max()),
            "rel_p90": float(np.quantile(vals, 0.90)),
            "rel_p95": float(np.quantile(vals, 0.95)),
            "rel_std": float(vals.std(ddof=1)),
            "seeds_passing_2e-5": int((vals <= GATE_REL).sum()),
            "pass_fraction": float((vals <= GATE_REL).mean()),
            "colmean_rel_mean": float(cms.mean()),
            "colmean_rel_max": float(cms.max()),
            "coherence_mean": float(coh.mean()),
            "coherence_max": float(coh.max()),
        }
        print(f"d{d}: mean={vals.mean():.4e} med={np.median(vals):.4e} "
              f"max={vals.max():.4e} pass={int((vals<=GATE_REL).sum())}/{len(vals)} "
              f"colmean_rel={cms.mean():.4e} coh={coh.mean():.4f}", flush=True)
    (HERE / "e1_chain_distribution.json").write_text(
        json.dumps({"geometry": {"rows": ROWS, "width": WIDTH,
                                 "layers": LAYERS, "reference": "float64 classical"},
                    "seeds": seeds, "summary": summary, "per_seed": per_seed},
                   indent=2), encoding="utf-8")
    print("wrote e1_chain_distribution.json", flush=True)


if __name__ == "__main__":
    main()
