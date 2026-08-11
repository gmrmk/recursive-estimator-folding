"""Measure G7 as depth degeneracy: spectrum, angles, and rank vs depth/width.

Records per layer, for both a He-Gaussian arm (the competition's ensemble, via
the frozen m200 generator) and a Haar-orthogonal arm at matched scale:

    lambda_min, lambda_max, kappa, mean|rho|, max|rho|, effective rank

so the four predeclared predictions in PREDECLARATION.md can be tested directly.

Synthetic weights only. No truth, scorer, holdout, private data, leaderboard,
submission, or champion access. The orthogonal arm is a mechanism diagnostic and
is not a competition claim.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _d in ("m178_certified_phi2_owent", "m179_background_archive_producer",
           "m198_source211_delay_one_adapter", "m200_streaming_overlap_fixture",
           "m125_source_batched_forward_tangent", "m167_collision_owner_unification",
           "m172_selective_22_owner_fusion"):
    _p = str(EXPERIMENTS / _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import m179_background_producer as producer   # noqa: E402
import m200_streaming_overlap as m200         # noqa: E402

FLOOR = 1e-12
TOTAL_WEIGHTS = 32
SOURCE_LAYERS_H = 31
KNOWN_HE = {(256, 0): 12, (256, 1): 10}


def cell_seed(width: int, replicate: int) -> int:
    return 200_000_000 + 10_000 * width + 100 * SOURCE_LAYERS_H + replicate


def orthogonal_weights(width: int, depth: int, seed: int):
    """Haar-orthogonal at matched scale.

    He-Gaussian here is N(0, 2/width) entrywise, so each column has expected
    squared norm width * 2/width = 2. sqrt(2) * Q with Q orthogonal has columns
    of norm exactly sqrt(2), matching that scale.
    """
    rng = np.random.Generator(np.random.Philox(seed))
    out = []
    for _ in range(depth):
        A = rng.normal(size=(width, width))
        Q, R = np.linalg.qr(A)
        Q = Q * np.sign(np.diag(R))          # Haar-correct sign fix
        out.append(np.sqrt(2.0) * Q)
    return tuple(out)


def effective_rank(eigs: np.ndarray) -> float:
    lam = np.clip(eigs, 0.0, None)
    total = float(lam.sum())
    if total <= 0:
        return 0.0
    p = lam / total
    p = p[p > 0]
    return float(np.exp(-np.sum(p * np.log(p))))


def trace_cell(args) -> dict:
    width, rep, arm = args
    seed = cell_seed(width, rep)
    weights = (m200.generated_weights(width, TOTAL_WEIGHTS, seed) if arm == "he"
               else orthogonal_weights(width, TOTAL_WEIGHTS, seed))
    mu = np.zeros(width)
    V = np.eye(width)
    rows = []
    trip = None
    for layer, W in enumerate(weights, start=1):
        a = mu @ W
        C = W.T @ (V @ W)
        C = 0.5 * (C + C.T)
        eigs = np.linalg.eigvalsh(C)
        lo, hi = float(eigs[0]), float(eigs[-1])
        d = np.sqrt(np.maximum(np.diag(C), 0.0))
        with np.errstate(divide="ignore", invalid="ignore"):
            R = C / np.outer(d, d)
        off = R[~np.eye(width, dtype=bool)]
        off = off[np.isfinite(off)]
        rows.append({
            "layer": layer,
            "lambda_min": lo,
            "lambda_max": hi,
            "kappa": (hi / lo) if lo > 0 else float("inf"),
            "mean_abs_rho": float(np.mean(np.abs(off))) if off.size else 0.0,
            "max_abs_rho": float(np.max(np.abs(off))) if off.size else 0.0,
            "effective_rank": effective_rank(eigs),
        })
        if trip is None and lo <= FLOOR:
            trip = layer
        if trip is not None:
            break
        step = producer.relu_moments(a, C)
        mu, V = step.mu, step.V

    healthy = [r for r in rows if r["lambda_min"] > FLOOR]
    ratios = [healthy[i + 1]["lambda_min"] / healthy[i]["lambda_min"]
              for i in range(len(healthy) - 1) if healthy[i]["lambda_min"] > 0]
    return {
        "width": width, "replicate": rep, "arm": arm, "seed": seed,
        "first_trip": trip,
        "n_healthy": len(healthy),
        "decay_rate": statistics.median(ratios) if ratios else None,
        "layers": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--widths", default="32,64,128,256")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(HERE / "degeneracy.json"))
    args = ap.parse_args()

    cells = [(w, r, arm)
             for w in (int(x) for x in args.widths.split(","))
             for r in range(args.reps)
             for arm in ("he", "orth")]
    cells.sort(key=lambda c: -c[0])
    print(f"{len(cells)} cells, {args.workers} workers\n", flush=True)

    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for rec in pool.map(trace_cell, cells):
            key = (rec["width"], rec["replicate"])
            sig = ""
            if rec["arm"] == "he" and key in KNOWN_HE:
                want = KNOWN_HE[key]
                sig = ("  SECOND SIGNAL REPRODUCED" if rec["first_trip"] == want
                       else f"  MISMATCH expected {want}")
            dr = rec["decay_rate"]
            print(f"  w={rec['width']:>4} rep={rec['replicate']} {rec['arm']:>5}  "
                  f"trip={str(rec['first_trip']):>5}  "
                  f"decay={('%.4f' % dr) if dr else '-':>7}{sig}", flush=True)
            results.append(rec)

    results.sort(key=lambda r: (r["arm"], r["width"], r["replicate"]))
    Path(args.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
