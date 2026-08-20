"""Measure the CHAMPION's own peak working set on a synthetic He net, and the
projected peak once the depth-1 Winograd stacks are replaced by depth-d ones.

Net construction is copied from v31_guards/run_v31_gates.py::he_weights
(seeded He 256x256, depth 32) -- synthetic, no dataset, no truth, no scorer.
The frozen package_source is IMPORTED, never modified.

argv: <extra_bytes> [<label>]
  extra_bytes: a live float32 block held across setup+predict, standing in for
  the additional Strassen level stacks of a deeper recursion.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent / "v31_guards" / "package_source"

import memprobe  # noqa: E402

WIDTH = 256
DEPTH = 32
GAIN = math.sqrt(2.0 / WIDTH)  # verbatim v31_guards/run_v31_gates.py:51
BUDGET = int(2.72e11)


def main() -> None:
    extra_bytes = int(sys.argv[1])
    label = sys.argv[2] if len(sys.argv) > 2 else f"extra{extra_bytes}"

    import numpy as np
    import flopscope as flops
    import flopscope.numpy as fnp
    from whestbench import SetupContext
    from whestbench.domain import MLP

    sys.path.insert(0, str(PKG))
    flops.configure(symmetry_warnings=False)
    from kerdock_v3_estimator import Estimator

    out = {"label": label, "extra_bytes": extra_bytes,
           "after_import": memprobe.snapshot()}

    ballast = None
    if extra_bytes > 0:
        n = extra_bytes // 4
        ballast = fnp.empty((n,), dtype=fnp.float32)
        fnp.copyto(ballast, 1.0)
        out["ballast_bytes"] = int(ballast.nbytes)
    out["after_ballast"] = memprobe.snapshot()

    rng = np.random.default_rng(101)
    gain = np.float32(GAIN)
    weights_np = [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
                  for _ in range(DEPTH)]
    weights_f = [fnp.asarray(w) for w in weights_np]

    est = Estimator()
    est.setup(SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET,
                           api_version="2.0", seed=0, submission_dir=str(PKG)))
    out["after_setup"] = memprobe.snapshot()
    out["winograd_buffer_bytes"] = int(est._winograd.buffer_bytes)
    out["winograd_full_output_bytes"] = int(est._winograd.full_output_bytes)
    out["winograd_level_stack_bytes"] = int(
        est._winograd.left_children.nbytes
        + est._winograd.right_children.nbytes
        + est._winograd.products.nbytes)

    mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights_f,
              seed=901_101, name="uf1-mem-a4det")
    mlp.validate()

    ctx = flops.BudgetContext(BUDGET, quiet=True)
    t0 = time.perf_counter()
    with ctx:
        res = est.predict(mlp, BUDGET)
    out["predict_wall_s"] = time.perf_counter() - t0
    out["billed_flops"] = int(ctx.flops_used)
    arr = np.asarray(res)
    out["output_shape"] = list(arr.shape)
    out["output_finite"] = bool(np.isfinite(arr).all())
    out["output_checksum"] = float(np.asarray(arr, dtype=np.float64).sum())
    out["after_predict"] = memprobe.snapshot()
    if ballast is not None:
        out["ballast_alive_checksum"] = float(np.asarray(ballast[:4]).sum())
    out["final"] = memprobe.snapshot()
    print(json.dumps(out))


if __name__ == "__main__":
    main()
