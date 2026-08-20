"""One measured memory case, run in a FRESH subprocess. Prints JSON on stdout.

Cases
  baseline                 : imports only (numpy + flopscope) -> interpreter floor
  rbw                      : instantiate the FROZEN RowBlockedBatchedWinograd(64512,256,4096)
  stacks:<d>               : allocate+fill every level stack of a batched row-blocked
                             Strassen-Winograd to depth d (BLOCK_ROWS=4096, W=256)
  batched:<d>              : execute the fused level-d batched leaf matmul under
                             flopscope (7^d, 4096/2^d, 256/2^d) @ (7^d, 256/2^d, 256/2^d)
  swprod:<d>:<M>           : run U-F1's own metered sw_product at (M,256)@(256,256)

Read-only w.r.t. every frozen source: sw_product and RowBlockedBatchedWinograd are
IMPORTED from their committed locations, never copied or edited.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPS = HERE.parent
UF1 = EXPS / "uf1_strassen_flop_accounting"
PKG = EXPS / "v31_guards" / "package_source"

import memprobe  # noqa: E402  (local, no third-party deps)

BLOCK_ROWS = 4096
W = 256


def _fill(arr):
    # flopscope arrays are immutable; copyto is the supported whole-array write
    # and is exactly what the frozen RowBlockedBatchedWinograd itself uses.
    import flopscope.numpy as _fnp
    _fnp.copyto(arr, 1.0)
    return arr


def main() -> None:
    case = sys.argv[1]
    out = {"case": case}
    t0 = time.perf_counter()

    import numpy as np  # noqa: F401
    import flopscope as fl
    import flopscope.numpy as fnp

    out["after_import"] = memprobe.snapshot()

    if case == "baseline":
        pass

    elif case == "rbw":
        sys.path.insert(0, str(PKG))
        from row_blocked_winograd import RowBlockedBatchedWinograd  # noqa: E402
        ws = RowBlockedBatchedWinograd(64512, 256, BLOCK_ROWS)
        for name in ("direct_scratch", "tail_output", "left_children",
                     "right_children", "products"):
            _fill(getattr(ws, name))
        out["buffer_bytes"] = int(ws.buffer_bytes)
        out["full_output_bytes"] = int(ws.full_output_bytes)
        out["per_array_bytes"] = {
            name: int(getattr(ws, name).nbytes)
            for name in ("direct_scratch", "tail_output", "left_children",
                         "right_children", "products")}

    elif case.startswith("stacks:"):
        d = int(case.split(":")[1])
        held = []
        total = 0
        per_level = {}
        for lvl in range(1, d + 1):
            b = 7 ** lvl
            r = BLOCK_ROWS >> lvl
            w = W >> lvl
            left = _fill(fnp.empty((b, r, w), dtype=fnp.float32))
            right = _fill(fnp.empty((b, w, w), dtype=fnp.float32))
            prod = _fill(fnp.empty((b, r, w), dtype=fnp.float32))
            held.extend((left, right, prod))
            lb = int(left.nbytes + right.nbytes + prod.nbytes)
            per_level[f"level{lvl}"] = {
                "batch": b, "rows": r, "width": w, "bytes": lb}
            total += lb
        out["level_stack_bytes_total"] = total
        out["per_level"] = per_level
        out["peak_at_hold"] = memprobe.snapshot()
        del held

    elif case.startswith("batched:"):
        d = int(case.split(":")[1])
        b = 7 ** d
        r = BLOCK_ROWS >> d
        w = W >> d
        left = _fill(fnp.empty((b, r, w), dtype=fnp.float32))
        right = _fill(fnp.empty((b, w, w), dtype=fnp.float32))
        prod = fnp.empty((b, r, w), dtype=fnp.float32)
        t1 = time.perf_counter()
        with fl.BudgetContext(flop_budget=10 ** 18, quiet=True) as bud:
            fnp.matmul(left, right, out=prod)
            used = int(bud.summary_dict()["flops_used"])
        out["batch"] = b
        out["leaf_shape"] = [r, w, w]
        out["billed_flops"] = used
        out["formula_flops"] = b * (2 * r * w * w - r * w)
        out["exact_match"] = used == b * (2 * r * w * w - r * w)
        out["matmul_wall_s"] = time.perf_counter() - t1
        out["peak_at_hold"] = memprobe.snapshot()

    elif case.startswith("swprod:"):
        _, ds, Ms = case.split(":")
        d, M = int(ds), int(Ms)
        sys.path.insert(0, str(UF1))
        from uf1_derive_and_verify import sw_product, strassen_charge  # noqa: E402
        rng = np.random.default_rng(20260810 + d)
        a = np.asarray(rng.standard_normal((M, W)), dtype="float32")
        bmat = np.asarray(rng.standard_normal((W, W)), dtype="float32")
        fa, fb = fnp.asarray(a), fnp.asarray(bmat)
        out["after_operands"] = memprobe.snapshot()
        t1 = time.perf_counter()
        with fl.BudgetContext(flop_budget=10 ** 18, quiet=True) as bud:
            C = fnp.empty((M, W), dtype=fnp.float32)
            sw_product(fa, fb, C, d)
            used = int(bud.summary_dict()["flops_used"])
        out["run_wall_s"] = time.perf_counter() - t1
        pred = strassen_charge(M, W, W, d, "V1_winograd15_floor")["total"]
        out["billed_flops"] = used
        out["analytic_flops"] = int(pred)
        out["exact_match"] = used == pred
        out["peak_at_hold"] = memprobe.snapshot()
        del C, fa, fb, a, bmat

    else:
        raise SystemExit(f"unknown case {case!r}")

    out["final"] = memprobe.snapshot()
    out["wall_s"] = time.perf_counter() - t0
    print(json.dumps(out))


if __name__ == "__main__":
    main()
