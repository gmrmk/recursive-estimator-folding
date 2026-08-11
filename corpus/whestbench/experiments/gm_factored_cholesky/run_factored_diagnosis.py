"""Run the predeclared factored-Cholesky diagnosis against the frozen producer.

Uses the same generator and cell_seed scheme as gm_m179_m199/diag_spd_depth.py,
so the dense column reproduces the gm_spd_width_scaling value of ell* for each
(width, replicate) cell -- the predeclared second signal.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
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

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "factored_cholesky", HERE / "factored_cholesky.py")
FC = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = FC
_spec.loader.exec_module(FC)

try:
    import m179_background_producer as producer     # noqa: E402
    import m200_streaming_overlap as m200           # noqa: E402
except Exception as exc:                            # pragma: no cover
    raise SystemExit(
        f"frozen M179/M200 modules not importable ({exc}). They arrive with "
        "PR #1 (agent/compression-survivor-corpus); this script reads them "
        "read-only and does not vendor them."
    )

TOTAL_WEIGHTS = 32
SOURCE_LAYERS_H = 31
# Second signal: gm_spd_width_scaling / diag256.log values for the dense path.
KNOWN_DENSE = {(256, 0): 12, (256, 1): 10, (224, 0): 11, (192, 0): 12, (128, 0): 18}


def cell_seed(width: int, replicate: int) -> int:
    return 200_000_000 + 10_000 * width + 100 * SOURCE_LAYERS_H + replicate


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--widths", default="128,192,256")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--out", default=str(HERE / "factored_diagnosis.json"))
    args = ap.parse_args()

    results = []
    print(f"{'width':>6} {'rep':>4} {'dense l*':>9} {'gram l*':>8} "
          f"{'V_post<=0':>10} {'unfactorable':>13} {'max rel gap':>12}  signal")
    print("-" * 82)
    for w in (int(x) for x in args.widths.split(",")):
        for rep in range(args.reps):
            weights = m200.generated_weights(w, TOTAL_WEIGHTS, cell_seed(w, rep))
            traj = FC.diagnose(weights, producer.relu_moments,
                               width=w, replicate=rep)
            gaps = [r.rel_gap for r in traj.layers
                    if r.state_factorable and np.isfinite(r.rel_gap)]
            worst_gap = max(gaps) if gaps else float("nan")
            known = KNOWN_DENSE.get((w, rep))
            sig = ("-" if known is None else
                   ("REPRODUCED" if traj.first_dense_trip == known
                    else f"MISMATCH exp={known}"))
            print(f"{w:>6} {rep:>4} {str(traj.first_dense_trip):>9} "
                  f"{str(traj.first_gram_trip):>8} "
                  f"{str(traj.first_state_nonpsd):>10} "
                  f"{str(traj.first_unfactorable):>13} "
                  f"{worst_gap:>12.3e}  {sig}", flush=True)
            results.append({
                "width": w, "replicate": rep,
                "first_dense_trip": traj.first_dense_trip,
                "first_gram_trip": traj.first_gram_trip,
                "first_state_nonpsd": traj.first_state_nonpsd,
                "first_unfactorable": traj.first_unfactorable,
                "worst_rel_gap": None if not gaps else worst_gap,
                "known_dense_trip": known,
                "layers": [vars(r) for r in traj.layers],
            })

    Path(args.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out}")

    # --- predeclared kill conditions ---
    print("\nPREDECLARED GATES")
    upstream = [r for r in results
                if r["first_state_nonpsd"] is not None
                and r["first_dense_trip"] is not None
                and r["first_state_nonpsd"] <= r["first_dense_trip"]]
    unfact = [r for r in results if r["first_unfactorable"] is not None]
    print(f"  KILL_UPSTREAM  : {'FIRED' if upstream else 'not fired'} "
          f"({len(upstream)}/{len(results)} cells with V' non-PSD at or before "
          f"the dense trip)")
    print(f"    (cells where Cholesky refused at all: {len(unfact)}/{len(results)})")

    at256 = [r for r in results if r["width"] == 256]
    same = [r for r in at256
            if r["first_gram_trip"] == r["first_dense_trip"]]
    print(f"  KILL_NO_GAIN   : {'FIRED' if at256 and len(same) > len(at256)/2 else 'not fired'} "
          f"({len(same)}/{len(at256)} width-256 cells trip at the same layer)")

    gaps = [r["worst_rel_gap"] for r in results if r["worst_rel_gap"] is not None]
    worst = max(gaps) if gaps else 0.0
    print(f"  KILL_DIVERGENCE: {'FIRED' if worst > 1e-9 else 'not fired'} "
          f"(worst relative gap {worst:.3e} vs 1e-9)")


if __name__ == "__main__":
    main()
