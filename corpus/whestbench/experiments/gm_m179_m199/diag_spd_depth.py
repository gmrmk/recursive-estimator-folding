"""Diagnostic: where does the M198 delay-one SPD guard trip as the M179
zero-order recurrence is extended toward 32 layers?

Records, per width, the per-layer minimum eigenvalue of the pre-ReLU covariance
and the maximum |rho|, and the first layer at which
  min eig(C) <= VARIANCE_FLOOR   (M198 DelayOneContext.__post_init__)
or
  max |rho|  >  RHO_MAX          (M179 relu_moments SPD stratum)
would fail closed.  Uses only the M179 producer recurrence; no fixture algebra.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _d in ("m178_certified_phi2_owent", "m179_background_archive_producer",
           "m198_source211_delay_one_adapter", "m200_streaming_overlap_fixture",
           "m125_source_batched_forward_tangent", "m167_collision_owner_unification",
           "m172_selective_22_owner_fusion"):
    p = str(EXPERIMENTS / _d)
    if p not in sys.path:
        sys.path.insert(0, p)

import m178_certified_phi2_owent as m178      # noqa: E402
import m179_background_producer as producer   # noqa: E402
import m198_source211_delay_one_adapter as m198  # noqa: E402
import m200_streaming_overlap as m200         # noqa: E402

FLOOR = m198.VARIANCE_FLOOR
RHO_MAX = m178.RHO_MAX
TOTAL_WEIGHTS = 32
SOURCE_LAYERS_H = 31


def cell_seed(width: int, replicate: int) -> int:
    return 200_000_000 + 10_000 * width + 100 * SOURCE_LAYERS_H + replicate


def trace(width: int, replicate: int) -> dict:
    seed = cell_seed(width, replicate)
    weights = m200.generated_weights(width, TOTAL_WEIGHTS, seed)
    mu = np.zeros(width)
    V = np.eye(width)
    rows = []
    first_spd_fail = None
    first_rho_fail = None
    for layer, W in enumerate(weights, start=1):
        a = mu @ W
        C = W.T @ (V @ W)
        C = 0.5 * (C + C.T)
        eig = float(np.min(np.linalg.eigvalsh(C)))
        d = np.diag(C)
        s = np.sqrt(np.maximum(d, 0.0))
        with np.errstate(divide="ignore", invalid="ignore"):
            R = C / np.outer(s, s)
        off = R[~np.eye(width, dtype=bool)] if width > 1 else np.array([0.0])
        rho = float(np.max(np.abs(off))) if off.size else 0.0
        rows.append({"layer": layer, "min_eig_pre_cov": eig, "max_abs_rho": rho,
                     "min_diag_var": float(np.min(d))})
        if first_spd_fail is None and eig <= FLOOR:
            first_spd_fail = layer
        if first_rho_fail is None and rho > RHO_MAX:
            first_rho_fail = layer
        if first_rho_fail is not None:
            break
        st = producer.relu_moments(a, C)
        mu, V = st.mu, st.V
    return {
        "width": width, "replicate": replicate, "seed": seed,
        "variance_floor": FLOOR, "rho_max": RHO_MAX,
        "first_layer_min_eig_le_floor": first_spd_fail,
        "first_layer_rho_gt_rhomax": first_rho_fail,
        "reaches_layer_32_spd_safe": first_spd_fail is None,
        "layers": rows,
    }


def main() -> None:
    widths = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [2, 3, 4, 5, 6, 7]
    out = []
    for w in widths:
        for rep in (0, 1):
            t = time.perf_counter()
            rec = trace(w, rep)
            rec["seconds"] = time.perf_counter() - t
            out.append(rec)
            print(json.dumps({k: rec[k] for k in (
                "width", "replicate", "first_layer_min_eig_le_floor",
                "first_layer_rho_gt_rhomax", "reaches_layer_32_spd_safe", "seconds")}),
                flush=True)
    path = HERE / "diag_spd_depth.json"
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    path.write_text(json.dumps(existing + out, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
