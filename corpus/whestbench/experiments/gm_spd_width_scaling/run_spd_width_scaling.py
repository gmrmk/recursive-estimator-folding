"""Measure ell*(n): the first layer at which the M179 zero-order recurrence's
pre-ReLU covariance leaves the positive-definite cone, as a function of width.

Fills the unmeasured interval (48, 256) left by gm_m179_m199, which measured
only width 48 (reaches layer 32) and width 256 (fails at layers 12 and 10).

The per-cell trace is byte-for-byte the same computation as
gm_m179_m199/diag_spd_depth.py -- same generator, same cell_seed scheme, same
floor and rho_max, same recurrence call -- so width-256 replicates 0 and 1 are
exact reproduction controls against diag256.log.

Parallel over (width, replicate) cells. Each worker pins BLAS to one thread:
the dominant cost is the scalar pair loop inside relu_moments, not the matmul,
so process-level parallelism is the right axis and thread contention only hurts.

Synthetic He-Gaussian weights only. No truth, scorer, holdout, private data,
leaderboard, submission, or champion work.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

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

import m178_certified_phi2_owent as m178      # noqa: E402
import m179_background_producer as producer   # noqa: E402
import m198_source211_delay_one_adapter as m198  # noqa: E402
import m200_streaming_overlap as m200         # noqa: E402

FLOOR = m198.VARIANCE_FLOOR
RHO_MAX = m178.RHO_MAX
TOTAL_WEIGHTS = 32
SOURCE_LAYERS_H = 31

# Reproduction controls from gm_m179_m199/diag256.log.
CONTROLS = {(256, 0): 12, (256, 1): 10}


def cell_seed(width: int, replicate: int) -> int:
    """Identical to gm_m179_m199/diag_spd_depth.py."""
    return 200_000_000 + 10_000 * width + 100 * SOURCE_LAYERS_H + replicate


def trace(width: int, replicate: int) -> dict:
    seed = cell_seed(width, replicate)
    weights = m200.generated_weights(width, TOTAL_WEIGHTS, seed)
    mu = np.zeros(width)
    V = np.eye(width)
    rows = []
    first_spd_fail = None
    first_rho_fail = None
    started = time.perf_counter()
    for layer, W in enumerate(weights, start=1):
        a = mu @ W
        C = W.T @ (V @ W)
        C = 0.5 * (C + C.T)
        eigs = np.linalg.eigvalsh(C)
        eig = float(np.min(eigs))
        eig_max = float(np.max(eigs))
        d = np.diag(C)
        s = np.sqrt(np.maximum(d, 0.0))
        with np.errstate(divide="ignore", invalid="ignore"):
            R = C / np.outer(s, s)
        off = R[~np.eye(width, dtype=bool)] if width > 1 else np.array([0.0])
        rho = float(np.max(np.abs(off))) if off.size else 0.0
        rows.append({
            "layer": layer,
            "min_eig_pre_cov": eig,
            "max_eig_pre_cov": eig_max,
            "max_abs_rho": rho,
            "min_diag_var": float(np.min(d)),
            # eps * n * lambda_max is the entrywise-assembly indefiniteness
            # scale predicted in PREDECLARATION.md; recorded, not gated on.
            "assembly_scale": float(np.finfo(np.float64).eps * width * eig_max),
        })
        if first_spd_fail is None and eig <= FLOOR:
            first_spd_fail = layer
        if first_rho_fail is None and rho > RHO_MAX:
            first_rho_fail = layer
        if first_rho_fail is not None:
            break
        st = producer.relu_moments(a, C)
        mu, V = st.mu, st.V
    return {
        "width": width,
        "replicate": replicate,
        "seed": seed,
        "variance_floor": FLOOR,
        "rho_max": RHO_MAX,
        "first_layer_min_eig_le_floor": first_spd_fail,
        "first_layer_rho_gt_rhomax": first_rho_fail,
        "reaches_layer_32_spd_safe": first_spd_fail is None,
        "layers": rows,
        "seconds": time.perf_counter() - started,
    }


def _cell(args: tuple[int, int]) -> dict:
    return trace(*args)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--widths", default="64,96,128,160,192,224",
                    help="comma-separated widths to sweep")
    ap.add_argument("--reps", type=int, default=4, help="replicates per width")
    ap.add_argument("--controls", action="store_true",
                    help="also run width-256 reps 0,1 as reproduction controls")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(HERE / "spd_width_scaling.json"))
    args = ap.parse_args()

    cells: list[tuple[int, int]] = []
    for w in (int(x) for x in args.widths.split(",") if x.strip()):
        cells.extend((w, r) for r in range(args.reps))
    if args.controls:
        cells.extend(CONTROLS)

    # Longest cells first so the tail does not serialize at the end.
    cells.sort(key=lambda c: -c[0])
    print(f"{len(cells)} cells, {args.workers} workers", flush=True)

    results: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for rec in pool.map(_cell, cells):
            key = (rec["width"], rec["replicate"])
            note = ""
            if key in CONTROLS:
                want = CONTROLS[key]
                got = rec["first_layer_min_eig_le_floor"]
                rec["control_expected"] = want
                rec["control_reproduced"] = (got == want)
                note = f"  CONTROL expected={want} got={got} " + \
                       ("REPRODUCED" if got == want else "MISMATCH")
            results.append(rec)
            print(json.dumps({
                "width": rec["width"],
                "replicate": rec["replicate"],
                "first_layer_min_eig_le_floor": rec["first_layer_min_eig_le_floor"],
                "reaches_layer_32_spd_safe": rec["reaches_layer_32_spd_safe"],
                "seconds": round(rec["seconds"], 1),
            }) + note, flush=True)

    results.sort(key=lambda r: (r["width"], r["replicate"]))
    Path(args.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.out}", flush=True)

    controls = [r for r in results if "control_reproduced" in r]
    if controls:
        ok = all(r["control_reproduced"] for r in controls)
        print(f"KILL_HARNESS check: {'PASS' if ok else 'FAIL'} "
              f"({sum(r['control_reproduced'] for r in controls)}/{len(controls)} reproduced)",
              flush=True)


if __name__ == "__main__":
    main()
