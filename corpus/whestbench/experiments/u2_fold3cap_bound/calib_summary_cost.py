"""U2 calibration: measure flopscope.budget_summary_dict() wall cost vs history.

STATIC-ANALYSIS SUPPORT ONLY. This does NOT run the fold3 estimator, does not
submit, and touches no truth/scorer. It exercises the FROZEN flopscope v0.14
library function `budget_summary_dict` on SYNTHETIC accumulator records to
calibrate the one cost-model constant needed to bound the T3 cap's residual
inflation: seconds of residual wall time injected per accumulated OpRecord.

The cap's `_tally()` calls `flops.budget_summary_dict()["flops_used"]`; that
call runs `_snapshot_records()` + `BudgetAccumulator.get_data()` which does
`all_ops.extend(rec.op_log)` over every recorded context then
`_summarize_operations(all_ops)` -- a pure-Python O(total ops) aggregation.
We measure the real per-op cost here.
"""
from __future__ import annotations

import time

import flopscope as flops
from flopscope import _budget as B


def make_oprecord(i: int) -> B.OpRecord:
    # Realistic field population matching charged ops (matmul/relu/gather/...).
    names = ("matmul", "maximum", "concatenate", "take", "sort",
             "flatnonzero", "mean", "sum", "sqrt", "multiply")
    return B.OpRecord(
        op_name=names[i % len(names)],
        subscripts=None,
        shapes=((79872, 256), (256, 256)),
        flop_cost=10_000_000 + i,
        cumulative=0,
        namespace=None,
        flopscope_context_start_offset_s=0.0,
        flopscope_backend_duration_s=1.2e-4,
        flopscope_overhead_duration_s=3.0e-6,
        resolved_dtype="float32",
    )


def make_record(ops_per_record: int) -> B.NamespaceRecord:
    op_log = [make_oprecord(i) for i in range(ops_per_record)]
    return B.NamespaceRecord(
        namespace=None,
        flop_budget=0,
        flops_used=sum(o.flop_cost for o in op_log),
        op_log=op_log,
        wall_time_s=3.6,
        total_flopscope_backend_time=3.2,
        total_flopscope_overhead_time=0.1,
    )


def time_summary(total_ops: int, ops_per_record: int, repeats: int = 7) -> float:
    n_records = max(1, total_ops // ops_per_record)
    B._accumulator._records = [make_record(ops_per_record) for _ in range(n_records)]
    # warm
    flops.budget_summary_dict()
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        d = flops.budget_summary_dict()
        dt = time.perf_counter() - t0
        best = min(best, dt)
    assert d["flops_used"] > 0
    B._accumulator._records = []
    return best


def main() -> None:
    ops_per_record = 2000  # realistic OpRecords per full capped predict
    print("total_ops, best_wall_s, ns_per_op")
    rows = []
    for total_ops in (2000, 10000, 20000, 40000, 100000, 200000):
        w = time_summary(total_ops, ops_per_record)
        ns = w / total_ops * 1e9
        rows.append((total_ops, w, ns))
        print(f"{total_ops:>8d}, {w:.6f}, {ns:.1f}")
    # Linear fit seconds-per-op from the two largest points (amortizes fixed cost).
    (n1, w1, _), (n2, w2, _) = rows[-2], rows[-1]
    sec_per_op = (w2 - w1) / (n2 - n1)
    print(f"\nSECONDS_PER_OP (marginal, large-N): {sec_per_op:.3e}")
    print(f"NS_PER_OP (marginal): {sec_per_op*1e9:.2f}")


if __name__ == "__main__":
    main()
