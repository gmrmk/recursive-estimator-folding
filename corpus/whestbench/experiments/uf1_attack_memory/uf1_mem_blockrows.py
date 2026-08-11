"""Is the Strassen workspace objection repairable at zero FLOP cost?

The frozen RowBlockedBatchedWinograd takes block_rows as a CONSTRUCTOR argument.
Its workspace is linear in block_rows; its bill should be exactly block_rows-
invariant (the right-hand stack fill is hoisted outside the row loop, and every
other term is linear in total rows).  Meter both claims on the production shape
(64512 x 256) @ (256 x 256) at several block heights, then solve for the largest
block height that keeps a depth-d recursion inside a given memory envelope.

Frozen source is imported, never modified.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent / "v31_guards" / "package_source"
sys.path.insert(0, str(PKG))

import flopscope as fl          # noqa: E402
import flopscope.numpy as fnp   # noqa: E402
import memprobe                 # noqa: E402
from row_blocked_winograd import RowBlockedBatchedWinograd  # noqa: E402

MIB = 1024 ** 2
M, W = 64_512, 256


def meter(block_rows: int) -> dict:
    rng = np.random.default_rng(20260810)
    a = np.asarray(rng.standard_normal((M, W)), dtype=np.float32)
    b = np.asarray(rng.standard_normal((W, W)), dtype=np.float32)
    fa, fb = fnp.asarray(a), fnp.asarray(b)
    ws = RowBlockedBatchedWinograd(M, W, block_rows)
    out = fnp.empty((M, W), dtype=fnp.float32)
    t0 = time.perf_counter()
    with fl.BudgetContext(flop_budget=10 ** 18, quiet=True) as bud:
        ws.multiply(fa, fb, out=out)
        used = int(bud.summary_dict()["flops_used"])
    wall = time.perf_counter() - t0
    got = np.asarray(out, dtype=np.float64)
    ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
    rel = float(np.linalg.norm(got - ref) / np.linalg.norm(ref))
    stacks = int(ws.left_children.nbytes + ws.right_children.nbytes
                 + ws.products.nbytes)
    return {
        "block_rows": block_rows,
        "billed_flops": used,
        "core_calls": int(ws.last_core_calls),
        "total_matmul_calls": int(ws.last_total_matmul_calls),
        "buffer_bytes": int(ws.buffer_bytes),
        "level_stack_bytes": stacks,
        "level_stack_MiB": stacks / MIB,
        "wall_s": wall,
        "relative_frobenius": rel,
        "checksum": float(got.sum()),
    }


def stack_bytes(depth: int, rows: int, width: int = W) -> int:
    """Batched all-levels-live Strassen level stacks, float32 bytes."""
    total = 0
    for lvl in range(1, depth + 1):
        b = 7 ** lvl
        r, w = rows >> lvl, width >> lvl
        total += (2 * b * r * w + b * w * w) * 4
    return total


def main() -> None:
    out: dict = {}

    rows = []
    for br in (4096, 2048, 512, 240, 128):
        rows.append(meter(br))
        print(json.dumps(rows[-1]), flush=True)
    out["block_rows_sweep"] = rows
    base = rows[0]["billed_flops"]
    out["bill_is_block_rows_invariant"] = all(
        r["billed_flops"] == base for r in rows)
    out["checksum_identical"] = all(
        r["checksum"] == rows[0]["checksum"] for r in rows)
    out["measured_d1_stack_bytes_vs_closed_form"] = {
        r["block_rows"]: {"measured": r["level_stack_bytes"],
                          "closed_form": stack_bytes(1, r["block_rows"]),
                          "agree": r["level_stack_bytes"] == stack_bytes(1, r["block_rows"])}
        for r in rows}

    # ---- largest block height that fits a depth-d recursion in an envelope --
    # Measured champion peak (uf1_mem_champion.py, no ballast) and the level
    # stacks it already contains at depth 1 / BLOCK_ROWS 4096.
    champ_peak_bytes = 474_284_032          # measured, run champion_d1
    champ_d1_stacks = 15_138_816            # measured, est._winograd stacks
    envelope = 512 * MIB
    headroom = envelope - (champ_peak_bytes - champ_d1_stacks)
    fits = {}
    for d in range(1, 6):
        step = 1 << d                       # block height must divide by 2^d
        best = 0
        r = step
        while r <= 4096:
            if stack_bytes(d, r) <= headroom:
                best = r
            r += step
        fits[f"d{d}"] = {
            "max_block_rows_under_512MiB": best,
            "stack_bytes_at_max": stack_bytes(d, best) if best else None,
            "stack_MiB_at_max": stack_bytes(d, best) / MIB if best else None,
            "row_blocks_at_max": (M + best - 1) // best if best else None,
            "stack_MiB_at_4096": stack_bytes(d, 4096) / MIB,
        }
    out["fit_under_512MiB"] = {
        "measured_champion_peak_bytes": champ_peak_bytes,
        "measured_champion_peak_MiB": champ_peak_bytes / MIB,
        "champion_d1_stack_bytes": champ_d1_stacks,
        "headroom_for_stacks_bytes": headroom,
        "headroom_for_stacks_MiB": headroom / MIB,
        "by_depth": fits,
    }
    out["final_memprobe"] = memprobe.snapshot()

    (HERE / "uf1_mem_blockrows.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                      if k != "block_rows_sweep"}, indent=2))


if __name__ == "__main__":
    main()
