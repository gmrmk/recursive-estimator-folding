"""U-F1 step 1: empirically establish the flopscope v0.10.0 price table.

Meters tiny synthetic float32/float64 arrays through flopscope and reports the
exact charged cost of each primitive Strassen-Winograd needs:
  matmul (batched and 2D), add/subtract, copyto, empty/zeros, slicing views.

No estimator source is imported. No champion / m245 module is touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import flopscope as fl
import flopscope.numpy as fnp

HERE = Path(__file__).resolve().parent
BUDGET = 10**18


def meter(fn):
    """Run `fn` inside a fresh budget; return (total_flops, per-op dict)."""
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as b:
        fn()
        d = b.summary_dict()
    ops = {k: (v["flop_cost"], v["calls"]) for k, v in d["operations"].items()}
    return int(d["flops_used"]), ops


def _rand(shape, dtype, seed):
    # numpy directly for the *setup* array, then wrap: setup must not be billed
    # inside the measured window, so we build outside and only meter the op.
    import numpy as np

    rng = np.random.default_rng(seed)
    return np.asarray(rng.standard_normal(shape), dtype=dtype)


def main() -> None:
    fl.configure(symmetry_warnings=False)
    results: dict[str, object] = {}

    # ---- 1. matmul, 2D, distinct operands, float32 --------------------------
    mm = {}
    for (m, k, n) in [(4, 4, 4), (8, 4, 4), (4, 8, 4), (4, 4, 8), (16, 16, 16),
                      (32, 8, 16), (64, 64, 64), (128, 256, 256)]:
        A = fnp.asarray(_rand((m, k), "float32", 1))
        B = fnp.asarray(_rand((k, n), "float32", 2))
        tot, ops = meter(lambda A=A, B=B: fnp.matmul(A, B))
        mm[f"{m}x{k}@{k}x{n}"] = {
            "charged": tot,
            "2mkn_minus_mn": 2 * m * k * n - m * n,
            "mn_2k_minus_1": m * n * (2 * k - 1),
        }
    results["matmul_f32_2d"] = mm

    # ---- 1b. matmul, batched --------------------------------------------
    bm = {}
    for (bs, m, k, n) in [(3, 4, 4, 4), (7, 8, 8, 8), (2, 5, 16, 16, )]:
        A = fnp.asarray(_rand((bs, m, k), "float32", 3))
        B = fnp.asarray(_rand((bs, k, n), "float32", 4))
        tot, ops = meter(lambda A=A, B=B: fnp.matmul(A, B))
        bm[f"b{bs}:{m}x{k}@{k}x{n}"] = {
            "charged": tot,
            "batch_x_2mkn_minus_mn": bs * (2 * m * k * n - m * n),
        }
    # broadcast form: (7, b, q, q) @ (7, b, q, q)
    A = fnp.asarray(_rand((7, 3, 8, 8), "float32", 5))
    B = fnp.asarray(_rand((7, 3, 8, 8), "float32", 6))
    tot, _ = meter(lambda: fnp.matmul(A, B))
    bm["7x3:8x8@8x8"] = {"charged": tot,
                         "batch_x_2mkn_minus_mn": 21 * (2 * 8 * 8 * 8 - 64)}
    # rectangular batched, the production motif: (b, M, K) @ (K, N) broadcast
    A = fnp.asarray(_rand((4, 32, 16), "float32", 7))
    B = fnp.asarray(_rand((16, 16), "float32", 8))
    tot, _ = meter(lambda: fnp.matmul(A, B))
    bm["bcast4:32x16@16x16"] = {"charged": tot,
                                "batch_x_2mkn_minus_mn": 4 * (2 * 32 * 16 * 16 - 32 * 16)}
    results["matmul_f32_batched"] = bm

    # ---- 1c. matmul dtype scaling ----------------------------------------
    dt = {}
    for name in ("float32", "float64"):
        A = fnp.asarray(_rand((16, 16), name, 9))
        B = fnp.asarray(_rand((16, 16), name, 10))
        tot, _ = meter(lambda A=A, B=B: fnp.matmul(A, B))
        dt[f"matmul16_{name}"] = tot
    results["matmul_dtype"] = dt

    # ---- 2. elementwise add / subtract / multiply -------------------------
    ew = {}
    for shape in [(4, 4), (16, 16), (7, 3, 8, 8), (64, 64)]:
        A = fnp.asarray(_rand(shape, "float32", 11))
        B = fnp.asarray(_rand(shape, "float32", 12))
        nel = 1
        for s in shape:
            nel *= s
        for op in ("add", "subtract", "multiply"):
            f = getattr(fnp, op)
            tot, _ = meter(lambda f=f, A=A, B=B: f(A, B))
            ew[f"{op}_{shape}_f32"] = {"charged": tot, "elements": nel}
            # with out= (in-place accumulate, the Winograd idiom)
            O = fnp.empty(shape, dtype=fnp.float32)
            tot2, _ = meter(lambda f=f, A=A, B=B, O=O: f(A, B, out=O))
            ew[f"{op}_out_{shape}_f32"] = {"charged": tot2, "elements": nel}
    # dtype scaling on add
    for name in ("float32", "float64"):
        A = fnp.asarray(_rand((16, 16), name, 13))
        B = fnp.asarray(_rand((16, 16), name, 14))
        tot, _ = meter(lambda A=A, B=B: fnp.add(A, B))
        ew[f"add_16x16_{name}"] = {"charged": tot, "elements": 256}
    results["elementwise"] = ew

    # ---- 3. copies / fills / allocation ------------------------------------
    mv = {}
    for shape in [(16, 16), (7, 3, 8, 8)]:
        nel = 1
        for s in shape:
            nel *= s
        A = fnp.asarray(_rand(shape, "float32", 15))
        O = fnp.empty(shape, dtype=fnp.float32)
        tot, _ = meter(lambda A=A, O=O: fnp.copyto(O, A))
        mv[f"copyto_{shape}_f32"] = {"charged": tot, "elements": nel}
        tot, _ = meter(lambda A=A: fnp.empty(A.shape, dtype=fnp.float32))
        mv[f"empty_{shape}_f32"] = {"charged": tot, "elements": nel}
        tot, _ = meter(lambda A=A: fnp.zeros(A.shape, dtype=fnp.float32))
        mv[f"zeros_{shape}_f32"] = {"charged": tot, "elements": nel}
        tot, _ = meter(lambda A=A: A.copy())
        mv[f"ndarray_copy_{shape}_f32"] = {"charged": tot, "elements": nel}
    # copyto dtype scaling
    for name in ("float32", "float64"):
        A = fnp.asarray(_rand((16, 16), name, 16))
        O = fnp.empty((16, 16), dtype=getattr(fnp, name))
        tot, _ = meter(lambda A=A, O=O: fnp.copyto(O, A))
        mv[f"copyto_16x16_{name}"] = {"charged": tot, "elements": 256}
    # slicing: is a view free?
    A = fnp.asarray(_rand((16, 16), "float32", 17))
    tot, _ = meter(lambda: A[:8, :8])
    mv["slice_view_16x16_to_8x8"] = {"charged": tot, "elements": 64}
    # in-place add into a slice destination (quadrant accumulate)
    A = fnp.asarray(_rand((16, 16), "float32", 18))
    B = fnp.asarray(_rand((8, 8), "float32", 19))
    tot, _ = meter(lambda: fnp.add(A[:8, :8], B, out=A[:8, :8]))
    mv["add_into_slice_8x8"] = {"charged": tot, "elements": 64}
    # swapaxes / transpose
    A = fnp.asarray(_rand((3, 16, 16), "float32", 20))
    tot, _ = meter(lambda: fnp.swapaxes(A, 1, 2))
    mv["swapaxes_3x16x16"] = {"charged": tot, "elements": 768}
    # concatenate / stack
    A = fnp.asarray(_rand((8, 8), "float32", 21))
    B = fnp.asarray(_rand((8, 8), "float32", 22))
    tot, _ = meter(lambda: fnp.concatenate([A, B], axis=0))
    mv["concatenate_2x_8x8"] = {"charged": tot, "elements": 128}
    tot, _ = meter(lambda: fnp.stack([A, B]))
    mv["stack_2x_8x8"] = {"charged": tot, "elements": 128}
    results["data_movement"] = mv

    # ---- 4. aliasing check: matmul(A, A) gets a repeated-operand discount --
    A = fnp.asarray(_rand((4, 4), "float32", 23))
    B = fnp.asarray(_rand((4, 4), "float32", 24))
    same, _ = meter(lambda: fnp.matmul(A, A))
    diff, _ = meter(lambda: fnp.matmul(A, B))
    results["alias_discount"] = {"A@A": same, "A@B": diff,
                                 "note": "A@A is discounted; Strassen must be "
                                         "priced with DISTINCT operands"}

    out = HERE / "uf1_price_table.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
