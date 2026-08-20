"""STEP 2 -- does depth-d Strassen COMPOSE with the production row-blocking?

Builds RowBlockedDepthStrassen: the frozen RowBlockedBatchedWinograd design
generalised to depth d, keeping every production structural commitment:
  * fixed-height streaming over M at BLOCK_ROWS = 4096
  * ONE batched matmul per row block (contiguous 7^d operand stack)
  * right-hand packing hoisted outside the row loop
  * every reshape hoisted into construction (flopscope bills reshape at
    1/element; the frozen kernel pays none because its stacks are allocated
    with a leading 7 axis -- we hold both views for the same reason)
  * the ownership-transfer invariant: the whole row block is captured in the
    level-1 left stack before any output row is written, so ``out`` may alias
    ``left``

Then meters it under a real BudgetContext at d = 0..5 and checks the bill
against the exact-integer (7,7,7) closed form and against a float64 reference.

Nothing in the frozen package is modified; it is imported read-only.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

import flopscope as fl
import flopscope.numpy as fnp

FROZEN = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
    r"\corpus\whestbench\experiments\v31_guards\package_source"
)
sys.path.insert(0, str(FROZEN))
from cost_model import direct_cost  # noqa: E402
from row_blocked_winograd import BLOCK_ROWS  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from step1_production_baseline import VARIANTS, strassen_charge  # noqa: E402

BUDGET = 10**18


def _expand_left_2d(a, dst):
    """2-D block -> (7, m/2, k/2).  Identical op list to frozen lines 137-143."""
    m, k = a.shape
    hm, hk = m // 2, k // 2
    a11, a12 = a[:hm, :hk], a[:hm, hk:]
    a21, a22 = a[hm:, :hk], a[hm:, hk:]
    fnp.copyto(dst[0], a11)
    fnp.copyto(dst[1], a12)
    fnp.copyto(dst[3], a22)
    fnp.add(a21, a22, out=dst[4])
    fnp.subtract(dst[4], a11, out=dst[5])
    fnp.subtract(a11, a21, out=dst[6])
    fnp.subtract(a12, dst[5], out=dst[2])


def _expand_left(src, dst):
    """(B, m, k) -> (B, 7, m/2, k/2): 3 copies + 4 arithmetic = 7 writes/node."""
    _, m, k = src.shape
    hm, hk = m // 2, k // 2
    a11, a12 = src[:, :hm, :hk], src[:, :hm, hk:]
    a21, a22 = src[:, hm:, :hk], src[:, hm:, hk:]
    fnp.copyto(dst[:, 0], a11)
    fnp.copyto(dst[:, 1], a12)
    fnp.copyto(dst[:, 3], a22)
    fnp.add(a21, a22, out=dst[:, 4])
    fnp.subtract(dst[:, 4], a11, out=dst[:, 5])
    fnp.subtract(a11, a21, out=dst[:, 6])
    fnp.subtract(a12, dst[:, 5], out=dst[:, 2])


def _expand_right_2d(b, dst):
    """2-D block -> (7, k/2, n/2).  Frozen lines 110-116."""
    k, n = b.shape
    hk, hn = k // 2, n // 2
    b11, b12 = b[:hk, :hn], b[:hk, hn:]
    b21, b22 = b[hk:, :hn], b[hk:, hn:]
    fnp.copyto(dst[0], b11)
    fnp.copyto(dst[1], b21)
    fnp.copyto(dst[2], b22)
    fnp.subtract(b12, b11, out=dst[4])
    fnp.subtract(b22, dst[4], out=dst[5])
    fnp.subtract(b22, b12, out=dst[6])
    fnp.subtract(dst[5], b21, out=dst[3])


def _expand_right(src, dst):
    _, k, n = src.shape
    hk, hn = k // 2, n // 2
    b11, b12 = src[:, :hk, :hn], src[:, :hk, hn:]
    b21, b22 = src[:, hk:, :hn], src[:, hk:, hn:]
    fnp.copyto(dst[:, 0], b11)
    fnp.copyto(dst[:, 1], b21)
    fnp.copyto(dst[:, 2], b22)
    fnp.subtract(b12, b11, out=dst[:, 4])
    fnp.subtract(b22, dst[:, 4], out=dst[:, 5])
    fnp.subtract(b22, b12, out=dst[:, 6])
    fnp.subtract(dst[:, 5], b21, out=dst[:, 3])


def _combine_2d(p, dst):
    """(7, m/2, n/2) -> 2-D block.  Frozen lines 157-163: exactly 7 writes."""
    m, n = dst.shape
    hm, hn = m // 2, n // 2
    c11, c12 = dst[:hm, :hn], dst[:hm, hn:]
    c21, c22 = dst[hm:, :hn], dst[hm:, hn:]
    fnp.add(p[0], p[1], out=c11)
    fnp.add(p[0], p[5], out=c12)
    fnp.add(c12, p[6], out=c21)
    fnp.add(c21, p[4], out=c22)
    fnp.add(c12, p[4], out=c12)
    fnp.add(c12, p[2], out=c12)
    fnp.subtract(c21, p[3], out=c21)


def _combine(p, dst):
    """(B, 7, m/2, n/2) -> (B, m, n)."""
    _, m, n = dst.shape
    hm, hn = m // 2, n // 2
    c11, c12 = dst[:, :hm, :hn], dst[:, :hm, hn:]
    c21, c22 = dst[:, hm:, :hn], dst[:, hm:, hn:]
    fnp.add(p[:, 0], p[:, 1], out=c11)
    fnp.add(p[:, 0], p[:, 5], out=c12)
    fnp.add(c12, p[:, 6], out=c21)
    fnp.add(c21, p[:, 4], out=c22)
    fnp.add(c12, p[:, 4], out=c12)
    fnp.add(c12, p[:, 2], out=c12)
    fnp.subtract(c21, p[:, 3], out=c21)


class RowBlockedDepthStrassen:
    """Production row-blocked batched Winograd, generalised to depth d."""

    def __init__(self, max_m, width, depth, block_rows=BLOCK_ROWS):
        self.max_m, self.width = int(max_m), int(width)
        self.depth, self.block_rows = int(depth), int(block_rows)
        d, w = self.depth, self.width
        if d and w % (1 << d):
            raise ValueError("width not 2^depth divisible")
        self.row_sizes = sorted({min(self.block_rows, self.max_m - s)
                                 for s in range(0, self.max_m, self.block_rows)})
        for rows in self.row_sizes:
            if d and rows % (1 << d):
                raise ValueError(f"row block {rows} not 2^{d} divisible")
        # right stacks: flat (7^j, ., .) plus a grouped view for the next level
        self.r_flat, self.r_group = [], []
        for j in range(1, d + 1):
            g = fnp.empty((7 ** (j - 1), 7, w >> j, w >> j), dtype=fnp.float32)
            self.r_group.append(g)
            self.r_flat.append(g.reshape(7 ** j, w >> j, w >> j))
        self.l_flat, self.l_group, self.p_flat, self.p_group = {}, {}, {}, {}
        for rows in self.row_sizes:
            lf, lg, pf, pg = [], [], [], []
            for j in range(1, d + 1):
                g = fnp.empty((7 ** (j - 1), 7, rows >> j, w >> j),
                              dtype=fnp.float32)
                lg.append(g)
                lf.append(g.reshape(7 ** j, rows >> j, w >> j))
                q = fnp.empty((7 ** (j - 1), 7, rows >> j, w >> j),
                              dtype=fnp.float32)
                pg.append(q)
                pf.append(q.reshape(7 ** j, rows >> j, w >> j))
            self.l_flat[rows], self.l_group[rows] = lf, lg
            self.p_flat[rows], self.p_group[rows] = pf, pg
        self.direct_scratch = fnp.empty(
            (min(self.block_rows, self.max_m), w), dtype=fnp.float32)
        self.last_core_calls = 0

    @property
    def buffer_bytes(self):
        seen, total = set(), 0
        for a in ([self.direct_scratch] + list(self.r_group)
                  + [x for v in self.l_group.values() for x in v]
                  + [x for v in self.p_group.values() for x in v]):
            base = a.base if a.base is not None else a
            if id(base) not in seen:
                seen.add(id(base))
                total += int(a.nbytes)
        return total

    def multiply(self, left, right, *, out):
        m, k = (int(v) for v in left.shape)
        n = int(right.shape[1])
        d = self.depth
        if d == 0:
            for start in range(0, m, self.block_rows):
                stop = min(start + self.block_rows, m)
                src = self.direct_scratch[: stop - start, :k]
                fnp.copyto(src, left[start:stop, :k])
                fnp.matmul(src, right, out=out[start:stop, :n])
            self.last_core_calls = math.ceil(m / self.block_rows)
            return out[:m, :n]

        # Right stack built once, outside the row loop (frozen commitment).
        _expand_right_2d(right, self.r_flat[0])
        for j in range(1, d):
            _expand_right(self.r_flat[j - 1], self.r_group[j])
        rstack = self.r_flat[d - 1]

        calls = 0
        for start in range(0, m, self.block_rows):
            stop = min(start + self.block_rows, m)
            rows = stop - start
            lf, lg = self.l_flat[rows], self.l_group[rows]
            pf, pg = self.p_flat[rows], self.p_group[rows]
            # ---- capture: the whole row block enters the level-1 stack ----
            _expand_left_2d(left[start:stop, :k], lf[0])
            for j in range(1, d):
                _expand_left(lf[j - 1], lg[j])
            # ---- ONE batched matmul over the 7^d contiguous stack ----
            fnp.matmul(lf[d - 1], rstack, out=pf[d - 1])
            calls += 1
            # ---- reconstruction: only now are output rows written ----
            for j in range(d - 1, 0, -1):
                _combine(pg[j], pf[j - 1])
            _combine_2d(pf[0], out[start:stop, :n])
        self.last_core_calls = calls
        return out[:m, :n]


def meter(M, K, N, depth, seed=20260810, alias_out=False, ref=None, ab=None):
    if ab is None:
        rng = np.random.default_rng(seed + depth)
        a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
        b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
    else:
        a, b = ab
    if ref is None:
        ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
    fa, fb = fnp.asarray(a.copy()), fnp.asarray(b)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        op = RowBlockedDepthStrassen(M, max(K, N), depth)
        setup = int(bud.summary_dict()["flops_used"])
        out = fa if alias_out else fnp.empty((M, N), dtype=fnp.float32)
        op.multiply(fa, fb, out=out)
        used = int(bud.summary_dict()["flops_used"])
    got = np.asarray(out, dtype=np.float64)[:M, :N]
    rel = float(np.linalg.norm(got - ref) / np.linalg.norm(ref))
    res = {"depth": depth, "setup_flops": setup,
           "multiply_flops": used - setup, "total_flops": used,
           "core_calls": op.last_core_calls,
           "workspace_bytes": op.buffer_bytes,
           "relative_frobenius_vs_float64_classical": rel}
    del op
    return res


def main():
    K = N = 256
    out = {"note": "d=0 arm is the frozen direct_owned branch "
                   "(one bounded copy in + direct matmul)."}
    for M in (8064, 64512):
        classical = direct_cost(M, K, N)
        rng = np.random.default_rng(20260810)
        a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
        b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
        ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
        rows = []
        for d in range(0, 6):
            r = meter(M, K, N, d, ref=ref, ab=(a, b))
            pred = (classical + M * K) if d == 0 else strassen_charge(
                M, K, N, d, VARIANTS["V5_production_batched_ACTUAL"])
            r["closed_form_777"] = pred
            r["exact_match"] = r["multiply_flops"] == pred
            r["r_vs_classical"] = r["multiply_flops"] / classical
            rows.append(r)
            print(f"M={M} d={d} metered={r['multiply_flops']} pred={pred} "
                  f"match={r['exact_match']} r={r['r_vs_classical']:.6f} "
                  f"rel={r['relative_frobenius_vs_float64_classical']:.3e} "
                  f"ws={r['workspace_bytes']/1e6:.1f}MB "
                  f"setup={r['setup_flops']}", flush=True)
        out[f"M{M}"] = {"classical": classical, "rows": rows}

    alias = {}
    rng = np.random.default_rng(7)
    M = 64512
    a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
    b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
    ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
    for d in (1, 2, 3, 4):
        base = meter(M, K, N, d, ref=ref, ab=(a, b))
        al = meter(M, K, N, d, alias_out=True, ref=ref, ab=(a, b))
        alias[f"d{d}"] = {
            "disjoint_flops": base["multiply_flops"],
            "aliased_flops": al["multiply_flops"],
            "same_bill": base["multiply_flops"] == al["multiply_flops"],
            "disjoint_rel": base["relative_frobenius_vs_float64_classical"],
            "aliased_rel": al["relative_frobenius_vs_float64_classical"],
            "aliased_result_correct":
                al["relative_frobenius_vs_float64_classical"] < 1e-4,
        }
        print("alias d=%d" % d, alias[f"d{d}"], flush=True)
    out["ownership_transfer_out_aliases_left"] = alias

    (HERE / "step2_composed_depth_kernel.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
