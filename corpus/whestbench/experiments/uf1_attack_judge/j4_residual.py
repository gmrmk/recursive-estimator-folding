"""Judge check J4: does the depth-d recursion's residual wall-time charge
swamp its FLOP saving on the production shape?

Cost law (re-read from the integrated falsifier's a_cost_law.json, itself
verified at 0.0 error against 100 cached MLPs):
    effective_compute = flops_used + residual_wall_time_s * 1e11
so every un-instrumented Python second is billed 1e11 FLOPs.

Independent re-measurement with my own Winograd-15 recursion, production shape
64512x256 @ 256x256:
  champ_d1_frozen : the frozen RowBlockedBatchedWinograd (the REAL baseline)
  d0_direct       : one fnp.matmul
  sw_d1..sw_d4    : recursion, preallocated per-level scratch, out=, views only
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "v31_guards", "package_source"))
sys.path.insert(0, PKG)

import numpy as np
import flopscope as fl
import flopscope.numpy as fnp
import row_blocked_winograd as rbw

LAMBDA = 1e11
M, K, N = 64512, 256, 256
REPEATS = 3


class WS:
    def __init__(self, m, k, n, depth):
        self.levels = []
        for lvl in range(1, depth + 1):
            hm, hk, hn = m >> lvl, k >> lvl, n >> lvl
            self.levels.append((
                fnp.empty((4, hm, hk), dtype=fnp.float32),
                fnp.empty((4, hk, hn), dtype=fnp.float32),
                fnp.empty((7, hm, hn), dtype=fnp.float32),
            ))


def sw(a, b, c, d, ws, lvl):
    """Winograd-15: 4 A-adds + 4 B-adds + 7 output adds + 7 sub-products."""
    if d == 0:
        fnp.matmul(a, b, out=c)
        return
    m, k = a.shape
    n = b.shape[1]
    hm, hk, hn = m >> 1, k >> 1, n >> 1
    a11, a12, a21, a22 = a[:hm, :hk], a[:hm, hk:], a[hm:, :hk], a[hm:, hk:]
    b11, b12, b21, b22 = b[:hk, :hn], b[:hk, hn:], b[hk:, :hn], b[hk:, hn:]
    S, T, P = ws.levels[lvl]
    fnp.add(a21, a22, out=S[0])            # S1
    fnp.subtract(S[0], a11, out=S[1])      # S2
    fnp.subtract(a11, a21, out=S[2])       # S3
    fnp.subtract(a12, S[1], out=S[3])      # S4
    fnp.subtract(b12, b11, out=T[0])       # T1
    fnp.subtract(b22, T[0], out=T[1])      # T2
    fnp.subtract(b22, b12, out=T[2])       # T3
    fnp.subtract(T[1], b21, out=T[3])      # T4
    nd, nl = d - 1, lvl + 1
    sw(a11, b11, P[0], nd, ws, nl)         # P1
    sw(a12, b21, P[1], nd, ws, nl)         # P2
    sw(S[3], b22, P[2], nd, ws, nl)        # P3
    sw(a22, T[3], P[3], nd, ws, nl)        # P4
    sw(S[0], T[0], P[4], nd, ws, nl)       # P5
    sw(S[1], T[1], P[5], nd, ws, nl)       # P6
    sw(S[2], T[2], P[6], nd, ws, nl)       # P7
    c11, c12, c21, c22 = c[:hm, :hn], c[:hm, hn:], c[hm:, :hn], c[hm:, hn:]
    fnp.add(P[0], P[1], out=c11)           # C11 = P1 + P2
    fnp.add(P[0], P[5], out=c22)           # U2  = P1 + P6
    fnp.add(c22, P[6], out=c21)            # U3  = U2 + P7
    fnp.add(c22, P[4], out=c12)            # U4  = U2 + P5
    fnp.add(c12, P[2], out=c12)            # C12 = U4 + P3
    fnp.add(c21, P[4], out=c22)            # C22 = U3 + P5
    fnp.subtract(c21, P[3], out=c21)       # C21 = U3 - P4


rng = np.random.default_rng(20260810)
a = np.asarray(rng.standard_normal((M, K)), dtype=np.float32)
b = np.asarray(rng.standard_normal((K, N)), dtype=np.float32)
ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
nrm = np.linalg.norm(ref)
fa, fb = fnp.asarray(a), fnp.asarray(b)

results: dict[str, dict] = {}


def run(tag, fn):
    recs = []
    last = None
    for _ in range(REPEATS):
        with fl.BudgetContext(flop_budget=10**18, quiet=True) as bud:
            c = fnp.empty((M, N), dtype=fnp.float32)
            fn(c)
            s = bud.summary_dict()
        recs.append((int(s["flops_used"]), float(s["residual_wall_time_s"]),
                     float(s["wall_time_s"]), int(sum(v["count"] if isinstance(v,dict) and "count" in v else 0 for v in s["operations"].values())) if isinstance(s["operations"],dict) else 0))
        last = np.asarray(c, dtype=np.float64)
    flops = recs[0][0]
    res_sorted = sorted(r[1] for r in recs)
    res = res_sorted[len(recs) // 2]
    results[tag] = {
        "flops": flops,
        "flops_bitwise_stable": all(r[0] == flops for r in recs),
        "operations": recs[0][3],
        "residual_s_median": res,
        "residual_s_min": res_sorted[0],
        "residual_s_all": [r[1] for r in recs],
        "wall_s_median": sorted(r[2] for r in recs)[len(recs) // 2],
        "effective_compute_median": flops + res * LAMBDA,
        "effective_compute_at_min_residual": flops + res_sorted[0] * LAMBDA,
        "rel_fro_vs_f64": float(np.linalg.norm(last - ref) / nrm),
    }
    r = results[tag]
    print(f"{tag:18s} flops={flops:>13,} ops={r['operations']:>5} "
          f"resid={res:.6f}s eff={r['effective_compute_median']:.4e} "
          f"rel={r['rel_fro_vs_f64']:.2e}", flush=True)


op = rbw.RowBlockedBatchedWinograd(M, K, rbw.BLOCK_ROWS)
run("champ_d1_frozen", lambda c: op.multiply(fa, fb, out=c))
run("d0_direct", lambda c: fnp.matmul(fa, fb, out=c))
for d in (1, 2, 3, 4):
    ws = WS(M, K, N, d)
    run(f"sw_d{d}", (lambda ws, d: (lambda c: sw(fa, fb, c, d, ws, 0)))(ws, d))

champ = results["champ_d1_frozen"]
delta = {}
for d in (1, 2, 3, 4):
    r = results[f"sw_d{d}"]
    delta[f"d{d}"] = {
        "flop_delta_vs_champion": r["flops"] - champ["flops"],
        "residual_charge_delta": (r["residual_s_median"]
                                  - champ["residual_s_median"]) * LAMBDA,
        "net_effective_delta": (r["effective_compute_median"]
                                - champ["effective_compute_median"]),
        "net_effective_delta_at_min_residual": (
            r["effective_compute_at_min_residual"]
            - champ["effective_compute_at_min_residual"]),
    }
out = {"lambda": LAMBDA, "shape": [M, K, N], "repeats": REPEATS,
       "flopscope": "0.10.0+np2.4.6", "arms": results,
       "delta_vs_champion": delta}
print(json.dumps(delta, indent=2))
open(os.path.join(HERE, "j4_residual.json"), "w", encoding="utf-8").write(
    json.dumps(out, indent=2))
