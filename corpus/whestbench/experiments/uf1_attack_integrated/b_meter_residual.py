"""B - meter the FULL v0.10.0 cost (flops AND residual wall time) of a real
recursive Strassen-Winograd at the production deep-layer shape.

Synthetic data only. No estimator, no scorer, no dataset, no network, no git.
The frozen champion kernel `row_blocked_winograd.py` is IMPORTED READ-ONLY as
the honest depth-1 baseline; it is not modified.

Arms (all V1-floor-favourable: preallocated buffers, strided views, out=):
  d0_direct     : one fnp.matmul                (depth 0)
  champ_d1      : frozen RowBlockedBatchedWinograd.multiply  (the ACTUAL baseline)
  swN d=1..4    : recursive Winograd-15, 7 separate sub-multiplies (V1 floor)

Reported per arm: flops_used, backend_s, overhead_s, residual_s, wall_s,
and effective compute flops + residual*1e11.
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.abspath(os.path.join(HERE, "..", "v31_guards", "package_source"))
sys.path.insert(0, FROZEN)

import flopscope
import flopscope.numpy as fnp
import numpy as _np

LAMBDA = 1e11
REPEATS = int(os.environ.get("UF1_REPEATS", "3"))


# ----------------------------------------------------------------- workspace
class WS:
    """Per-level preallocated Winograd scratch. `empty` is billed 0."""

    def __init__(self, m, k, n, depth):
        self.levels = []
        for lvl in range(1, depth + 1):
            hm, hk, hn = m >> lvl, k >> lvl, n >> lvl
            self.levels.append(
                (
                    fnp.empty((4, hm, hk), dtype=fnp.float32),
                    fnp.empty((4, hk, hn), dtype=fnp.float32),
                    fnp.empty((7, hm, hn), dtype=fnp.float32),
                )
            )

    def at(self, remaining_depth_index):
        return self.levels[remaining_depth_index]


def sw(a, b, c, d, ws, lvl):
    """Winograd-15 recursion. c must not alias a or b."""
    if d == 0:
        fnp.matmul(a, b, out=c)
        return
    m, k = a.shape
    n = b.shape[1]
    hm, hk, hn = m >> 1, k >> 1, n >> 1
    a11 = a[:hm, :hk]
    a12 = a[:hm, hk:]
    a21 = a[hm:, :hk]
    a22 = a[hm:, hk:]
    b11 = b[:hk, :hn]
    b12 = b[:hk, hn:]
    b21 = b[hk:, :hn]
    b22 = b[hk:, hn:]
    S, T, M = ws.at(lvl)
    fnp.add(a21, a22, out=S[0])          # S1
    fnp.subtract(S[0], a11, out=S[1])    # S2
    fnp.subtract(a11, a21, out=S[2])     # S3
    fnp.subtract(a12, S[1], out=S[3])    # S4
    fnp.subtract(b12, b11, out=T[0])     # T1
    fnp.subtract(b22, T[0], out=T[1])    # T2
    fnp.subtract(b22, b12, out=T[2])     # T3
    fnp.subtract(T[1], b21, out=T[3])    # T4
    nd = d - 1
    nl = lvl + 1
    sw(a11, b11, M[0], nd, ws, nl)
    sw(a12, b21, M[1], nd, ws, nl)
    sw(S[3], b22, M[2], nd, ws, nl)
    sw(a22, T[3], M[3], nd, ws, nl)
    sw(S[0], T[0], M[4], nd, ws, nl)
    sw(S[1], T[1], M[5], nd, ws, nl)
    sw(S[2], T[2], M[6], nd, ws, nl)
    c11 = c[:hm, :hn]
    c12 = c[:hm, hn:]
    c21 = c[hm:, :hn]
    c22 = c[hm:, hn:]
    fnp.add(M[0], M[1], out=c11)         # U1 -> C11
    fnp.add(M[0], M[5], out=c12)         # U2
    fnp.add(c12, M[6], out=c21)          # U3
    fnp.add(c12, M[4], out=c22)          # U4
    fnp.add(c22, M[2], out=c12)          # U5 -> C12
    fnp.add(c21, M[4], out=c22)          # U7 -> C22
    fnp.subtract(c21, M[3], out=c21)     # U6 -> C21


def timed(fn, budget=1e15):
    with flopscope.BudgetContext(budget) as ctx:
        fn()
    s = ctx.summary_dict()
    return dict(
        flops=int(s["flops_used"]),
        wall=float(s["wall_time_s"]),
        backend=float(s["flopscope_backend_time_s"]),
        overhead=float(s["flopscope_overhead_time_s"]),
        residual=float(s["residual_wall_time_s"]),
    )


def run_shape(M, K, N, depths, seed):
    rng = _np.random.default_rng(seed)
    A_np = rng.standard_normal((M, K), dtype=_np.float32)
    B_np = rng.standard_normal((K, N), dtype=_np.float32)
    ref = A_np.astype(_np.float64) @ B_np.astype(_np.float64)
    refn = _np.linalg.norm(ref)

    results = {}

    # --- arm: direct -----------------------------------------------------
    A = fnp.asarray(A_np)
    Bm = fnp.asarray(B_np)
    C = fnp.empty((M, N), dtype=fnp.float32)
    reps = []
    for _ in range(REPEATS):
        reps.append(timed(lambda: fnp.matmul(A, Bm, out=C)))
    err = float(_np.linalg.norm(_np.asarray(C).astype(_np.float64) - ref) / refn)
    results["d0_direct"] = {"reps": reps, "rel_fro": err, "matmul_calls": 1}

    # --- arm: frozen champion kernel (true depth-1 baseline) -------------
    from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd

    wg = RowBlockedBatchedWinograd(M, N, BLOCK_ROWS)
    reps = []
    for _ in range(REPEATS):
        reps.append(timed(lambda: wg.multiply(A, Bm, out=C)))
    err = float(_np.linalg.norm(_np.asarray(C).astype(_np.float64) - ref) / refn)
    results["champ_d1_rowblocked"] = {
        "reps": reps,
        "rel_fro": err,
        "matmul_calls": int(wg.last_total_matmul_calls),
        "block_rows": BLOCK_ROWS,
    }
    del wg

    # --- arms: recursive Winograd d=1..dmax ------------------------------
    for d in depths:
        ws = WS(M, K, N, d)
        reps = []
        for _ in range(REPEATS):
            reps.append(timed(lambda: sw(A, Bm, C, d, ws, 0)))
        err = float(_np.linalg.norm(_np.asarray(C).astype(_np.float64) - ref) / refn)
        results[f"sw_d{d}"] = {
            "reps": reps,
            "rel_fro": err,
            "matmul_calls": 7 ** d,
            "internal_nodes": (7 ** d - 1) // 6,
        }
        del ws

    return results


def summarize(res):
    out = {}
    for arm, r in res.items():
        reps = r["reps"]
        fl = {x["flops"] for x in reps}
        med = lambda k: sorted(x[k] for x in reps)[len(reps) // 2]
        mn = lambda k: min(x[k] for x in reps)
        out[arm] = {
            "flops": reps[0]["flops"],
            "flops_bitwise_stable": len(fl) == 1,
            "residual_s_median": med("residual"),
            "residual_s_min": mn("residual"),
            "residual_s_all": [x["residual"] for x in reps],
            "overhead_s_median": med("overhead"),
            "backend_s_median": med("backend"),
            "wall_s_median": med("wall"),
            "eff_median": reps[0]["flops"] + med("residual") * LAMBDA,
            "eff_min_resid": reps[0]["flops"] + mn("residual") * LAMBDA,
            "rel_fro": r["rel_fro"],
            "matmul_calls": r["matmul_calls"],
            "internal_nodes": r.get("internal_nodes", 0),
        }
    return out


if __name__ == "__main__":
    depths = [1, 2, 3, 4]
    payload = {
        "flopscope": flopscope.__version__,
        "numpy": _np.__version__,
        "lambda": LAMBDA,
        "repeats": REPEATS,
        "shapes": {},
    }
    for M in (32256, 64512):
        t0 = time.perf_counter()
        res = run_shape(M, 256, 256, depths, seed=20260810 + M)
        payload["shapes"][f"{M}x256@256x256"] = summarize(res)
        print(f"shape M={M} done in {time.perf_counter()-t0:.1f}s", flush=True)
        print(json.dumps(payload["shapes"][f"{M}x256@256x256"], indent=2), flush=True)
    with open(os.path.join(HERE, "b_meter_residual.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print("WROTE b_meter_residual.json")
