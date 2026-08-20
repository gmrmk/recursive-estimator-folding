"""C - is the depth-4 residual an artefact of MY kernel, or an irreducible
per-flopscope-call floor?

Counter-hypothesis under test: "a better-engineered recursive Winograd would
not pay 0.106 s of residual; the harness in b_meter_residual.py is sloppy."

Probe: the minimum possible residual of N flopscope calls, in a bare loop with
preallocated `out=` and NO Python structure at all (no recursion, no slicing,
no function calls, no branching). That is a hard lower bound on the residual
any implementation must pay for the same number of billed ops.

Then compare against the call counts a depth-d Winograd-15 REQUIRES:
    elementwise calls = 15 * (7^d - 1) / 6
    matmul calls      = 7^d
"""
from __future__ import annotations

import json
import os

import flopscope
import flopscope.numpy as fnp
import numpy as _np

HERE = os.path.dirname(os.path.abspath(__file__))
LAMBDA = 1e11
REPS = 5


def bare_loop_residual(op, shapes, n_calls):
    """Residual of n_calls back-to-back flopscope calls, nothing else."""
    rng = _np.random.default_rng(7)
    if op == "add":
        x = fnp.asarray(rng.standard_normal(shapes, dtype=_np.float32))
        y = fnp.asarray(rng.standard_normal(shapes, dtype=_np.float32))
        z = fnp.empty(shapes, dtype=fnp.float32)
        call = lambda: fnp.add(x, y, out=z)
    elif op == "matmul":
        m, k, n = shapes
        x = fnp.asarray(rng.standard_normal((m, k), dtype=_np.float32))
        y = fnp.asarray(rng.standard_normal((k, n), dtype=_np.float32))
        z = fnp.empty((m, n), dtype=fnp.float32)
        call = lambda: fnp.matmul(x, y, out=z)
    else:
        raise ValueError(op)
    call()  # warm / first-touch
    best = None
    for _ in range(REPS):
        with flopscope.BudgetContext(1e16) as ctx:
            for _i in range(n_calls):
                call()
        s = ctx.summary_dict()
        r = float(s["residual_wall_time_s"])
        if best is None or r < best[0]:
            best = (r, float(s["flopscope_overhead_time_s"]),
                    float(s["flopscope_backend_time_s"]), int(s["flops_used"]))
    return dict(
        op=op, shape=list(shapes) if isinstance(shapes, tuple) else shapes,
        n_calls=n_calls,
        residual_s_min=best[0],
        residual_us_per_call=best[0] / n_calls * 1e6,
        overhead_s=best[1], backend_s=best[2], flops=best[3],
    )


if __name__ == "__main__":
    out = {"flopscope": flopscope.__version__, "reps": REPS, "probes": []}

    # elementwise shapes matching Winograd levels 1..4 at M=64512, K=N=256
    for lvl in (1, 2, 3, 4):
        hm, hk = 64512 >> lvl, 256 >> lvl
        out["probes"].append(bare_loop_residual("add", (hm, hk), 2000))
    # leaf matmul shapes at depth 1..4
    for lvl in (1, 2, 3, 4):
        hm, hk = 64512 >> lvl, 256 >> lvl
        out["probes"].append(bare_loop_residual("matmul", (hm, hk, hk), 500))

    # --- derive the irreducible floor for a depth-d Winograd-15 ----------
    ew_us = min(
        p["residual_us_per_call"] for p in out["probes"] if p["op"] == "add"
    )
    mm_us = min(
        p["residual_us_per_call"] for p in out["probes"] if p["op"] == "matmul"
    )
    floor = {}
    for d in range(1, 6):
        nodes = (7 ** d - 1) // 6
        ew_calls = 15 * nodes
        mm_calls = 7 ** d
        r = (ew_calls * ew_us + mm_calls * mm_us) * 1e-6
        floor[f"d{d}"] = {
            "internal_nodes": nodes,
            "elementwise_calls": ew_calls,
            "matmul_calls": mm_calls,
            "min_residual_s_floor": r,
            "min_residual_charge_flops": r * LAMBDA,
        }
    out["cheapest_elementwise_us_per_call"] = ew_us
    out["cheapest_matmul_us_per_call"] = mm_us
    out["irreducible_floor_per_product"] = floor

    with open(os.path.join(HERE, "c_residual_floor.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))
