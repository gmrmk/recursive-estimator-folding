"""Cheap pre-flight: bill identity, reshape billing, and small-scale bitwise parity.

Not a gate.  It exists so the expensive depth-32 arms are not spent on a
mechanical defect.  Geometry here is small and synthetic.
"""

from __future__ import annotations

import json
import os

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np  # noqa: E402
import flopscope as flops  # noqa: E402
import flopscope.numpy as fnp  # noqa: E402

from fused_l3 import GroupedInplaceL3, BLOCK_ROWS, TILE  # noqa: E402
from cost_model import independently_expanded_l3, dispatch  # noqa: E402
from inplace_l3 import InplaceL3Winograd  # noqa: E402

ROWS = 4 * BLOCK_ROWS + 3_072  # 19,456: three+ full blocks and a short tail
SEED = 116_250


def operands(rows: int, seed: int):
    rng = np.random.default_rng(seed)
    left = rng.standard_normal((rows, TILE), dtype=np.float32)
    right = (rng.standard_normal((TILE, TILE), dtype=np.float32) / 16.0).astype(np.float32)
    return left, right


def run(group: int, traced: bool):
    left, right = operands(ROWS, SEED)
    if traced:
        op = GroupedInplaceL3(group=group, backend=fnp)
        lt, rt = fnp.asarray(left), fnp.asarray(right)
        op.bind(lt)  # setup: grouped views built once, outside the metered region
        with flops.BudgetContext(10**13, quiet=True) as ctx:
            op.multiply_inplace(lt, rt)
        return np.asarray(lt).copy(), int(ctx.flops_used), op.last_total_matmul_calls
    op = GroupedInplaceL3(group=group, backend=np)
    op.multiply_inplace(left, right)
    return left, None, op.last_total_matmul_calls


def run_frozen():
    """The unmodified frozen operator, untouched, as the arithmetic anchor."""
    left, right = operands(ROWS, SEED)
    op = InplaceL3Winograd(max_m=ROWS, backend=np)
    op.multiply_inplace(left, right)
    return left, op.last_total_matmul_calls


def main() -> None:
    frozen_out, frozen_calls = run_frozen()
    ref_out, ref_bill, ref_calls = run(1, traced=True)
    fused_out, fused_bill, fused_calls = run(4, traced=True)

    expected = independently_expanded_l3(ROWS)
    d = dispatch(ROWS, TILE, TILE)

    out = {
        "rows": ROWS,
        "block_rows": BLOCK_ROWS,
        "frozen_calls": frozen_calls,
        "ref_group1_calls": ref_calls,
        "fused_group4_calls": fused_calls,
        "fused_plan": GroupedInplaceL3(group=4, backend=np).dispatch_plan(ROWS),
        "expected_bill": expected,
        "dispatch_total": d.total,
        "ref_billed": ref_bill,
        "fused_billed": fused_bill,
        "bill_ref_ok": ref_bill == expected == d.total,
        "bill_fused_ok": fused_bill == expected == d.total,
        "bitwise_frozen_vs_ref_group1": bool(
            np.array_equal(frozen_out.view(np.uint32), ref_out.view(np.uint32))
        ),
        "bitwise_frozen_vs_fused_group4": bool(
            np.array_equal(frozen_out.view(np.uint32), fused_out.view(np.uint32))
        ),
        "differing_words_frozen_vs_fused": int(
            np.count_nonzero(frozen_out.view(np.uint32) != fused_out.view(np.uint32))
        ),
        "max_abs_frozen_vs_fused": float(np.max(np.abs(frozen_out - fused_out))),
    }
    print(json.dumps(out, indent=1))
    with open("probe_cheap_results.json", "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=1)


if __name__ == "__main__":
    main()
