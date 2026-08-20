"""E6 -- independent second signal: run the SHIPPED kernel, not my twin.

E2's numbers come from a numpy twin (uf1_attack.py's `sw_np`).  This harness
runs the frozen `RowBlockedBatchedWinograd` from
experiments/v31_guards/package_source/ -- the champion's actual deep-layer
operator, a different schedule (batched 7-stack with explicit copies, 4096-row
blocking) that happens to compute the same one-level Winograd product -- over
the same production chain, and compares the injected column-mean error against
the twin's depth-1 number.

The frozen module is IMPORTED, never modified.  Nothing is written outside
this directory.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = Path(
    "C:/Users/strid/Documents/Codex/2026-08-02/https-chatgpt-com-share-6a5556ed-2e1c"
    "/publish/recursive-estimator-folding/corpus/whestbench/experiments/v31_guards"
    "/package_source"
)
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PKG))

import flopscope.numpy as fnp  # noqa: E402
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd  # noqa: E402

from e2_score_translation import (  # noqa: E402
    DEPTH, N_BASE, STRASSEN_LAYERS, kerdock_directions, sample_mlp_weights,
)
from e1_chain_distribution import sw_np  # noqa: E402


def main() -> None:
    net_seed = int(sys.argv[1]) if len(sys.argv) > 1 else 101
    z = kerdock_directions()
    Ws = sample_mlp_weights(net_seed)

    # float64 classical reference (numpy)
    zf = z.astype(np.float64)
    Wf = [w.astype(np.float64) for w in Ws]
    fp = zf @ Wf[0]
    xr = np.concatenate((np.maximum(fp, 0), np.maximum(-fp, 0)), axis=0)
    for layer in range(1, DEPTH):
        xr = np.maximum(xr @ Wf[layer], 0.0)
    cmr = xr.mean(axis=0)
    del xr, zf, Wf, fp

    # frozen kernel arm
    op = RowBlockedBatchedWinograd(2 * N_BASE, 256, BLOCK_ROWS)
    fz = fnp.asarray(z)
    fW = [fnp.asarray(w) for w in Ws]
    fp = fnp.matmul(fz, fW[0])
    x = fnp.concatenate((fnp.maximum(fp, 0.0), fnp.maximum(-fp, 0.0)), axis=0)
    buf = fnp.empty((2 * N_BASE, 256), dtype=fnp.float32)
    for layer in range(1, DEPTH):
        if layer <= STRASSEN_LAYERS:
            pre = op.multiply(x, fW[layer], out=buf)
            x = fnp.maximum(pre, 0.0)
        else:
            x = fnp.maximum(fnp.matmul(x, fW[layer]), 0.0)
    cm = np.asarray(x, dtype=np.float64).mean(axis=0)
    delta = cm - cmr
    res = {
        "net_seed": net_seed,
        "kernel": "frozen RowBlockedBatchedWinograd (one-level, batched 7-stack)",
        "rel_colmean": float(np.linalg.norm(delta) / np.linalg.norm(cmr)),
        "mse_contribution": float(np.mean(delta ** 2)),
        "rms_delta": float(np.sqrt(np.mean(delta ** 2))),
    }
    twin = json.loads((HERE / f"e2_net{net_seed}.json").read_text())["d1"]
    res["twin_sw_np_d1_rel_colmean"] = twin["rel_colmean"]
    res["twin_sw_np_d1_mse_contribution"] = twin["mse_contribution"]
    res["ratio_frozen_over_twin_mse"] = (
        res["mse_contribution"] / twin["mse_contribution"])
    print(json.dumps(res, indent=2))
    (HERE / f"e6_frozen_kernel_net{net_seed}.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
