"""U-F1 memory attack: peak simultaneous footprint of Strassen-Winograd
recursion at depth d on (M x 256) @ (256 x 256), float32.

Two independent derivations for every quantity (explicit per-level enumeration
vs closed form), and a cross-check of the depth-1 figure against the FROZEN
production workspace RowBlockedBatchedWinograd.buffer_bytes.

No frozen source is modified; nothing is imported from the champion estimator.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
F32 = 4
MIB = 1024 ** 2
BLOCK_ROWS = 4_096
W = 256
M_PROD = 64_512


# --------------------------------------------------------------------------
# A. BATCHED (breadth-first) row-blocked Strassen: every level's operand stack
#    is live simultaneously, because a level's batched matmul consumes the
#    whole 7^l stack in one call.  This is the formulation the champion's
#    RowBlockedBatchedWinograd implements at d = 1 and the one CODEX_HANDOFF
#    section 7 costs.
# --------------------------------------------------------------------------

def batched_stack_bytes_enumerated(depth: int, rows: int = BLOCK_ROWS,
                                   width: int = W) -> dict:
    """Explicit per-level enumeration (derivation 1)."""
    per_level = {}
    total = 0
    for lvl in range(1, depth + 1):
        b = 7 ** lvl
        r = rows >> lvl
        w = width >> lvl
        if r < 1 or w < 1:
            raise ValueError(f"depth {depth} does not fit rows={rows} width={width}")
        left = b * r * w * F32
        right = b * w * w * F32
        prod = b * r * w * F32
        per_level[f"level{lvl}"] = {
            "batch": b, "rows": r, "width": w,
            "left_bytes": left, "right_bytes": right, "product_bytes": prod,
            "level_bytes": left + right + prod,
        }
        total += left + right + prod
    return {"total_bytes": total, "per_level": per_level}


def batched_stack_bytes_closed_form(depth: int, rows: int = BLOCK_ROWS,
                                    width: int = W) -> int:
    """Closed form (derivation 2), exact rationals.

    level l holds 7^l * (rows/2^l)*(width/2^l) elements in each of the left and
    product stacks and 7^l * (width/2^l)^2 in the right stack, i.e.
        (7/4)^l * (2*rows*width + width^2) elements.
    Summing the geometric series l = 1..d:
        (2*rows*width + width^2) * ((7/4)^(d+1) - 7/4) / (7/4 - 1)
    """
    unit = Fraction(2 * rows * width + width * width)
    q = Fraction(7, 4)
    geo = (q ** (depth + 1) - q) / (q - 1) if depth >= 1 else Fraction(0)
    total = unit * geo * F32
    assert total.denominator == 1, total
    return int(total)


# --------------------------------------------------------------------------
# B. DEPTH-FIRST recursion (U-F1's own metered sw_product), no row blocking.
#    Live set while descending into the last child M7 of a node at level l:
#       4 * (m/2)(k/2)  [S1..S4]  + 4 * (k/2)(n/2)  [T1..T4]
#     + 7 * (m/2)(n/2)  [M1..M7 already allocated]
#    and, in the recombination phase of the deepest node, a further
#       3 * (m/2)(n/2)  [U2,U3,U4]
#    Every one of those names is still bound to a Python local for the whole
#    body of sw_product, so none can be freed early.
# --------------------------------------------------------------------------

def depth_first_bytes_enumerated(M: int, K: int, N: int, depth: int) -> dict:
    per_level = {}
    live = 0
    for lvl in range(depth):
        m, k, n = M >> lvl, K >> lvl, N >> lvl
        s = 4 * (m // 2) * (k // 2)
        t = 4 * (k // 2) * (n // 2)
        mm = 7 * (m // 2) * (n // 2)
        node = (s + t + mm) * F32
        per_level[f"level{lvl}"] = {
            "m": m, "k": k, "n": n,
            "S_bytes": s * F32, "T_bytes": t * F32, "M_bytes": mm * F32,
            "node_bytes": node,
        }
        live += node
    # recombination extra at the deepest recursing node (U2,U3,U4)
    if depth >= 1:
        m, n = M >> (depth - 1), N >> (depth - 1)
        recomb = 3 * (m // 2) * (n // 2) * F32
    else:
        recomb = 0
    operands = (M * K + K * N + M * N) * F32
    return {
        "temporaries_bytes": live,
        "recombination_extra_bytes": recomb,
        "temporaries_peak_bytes": live + recomb,
        "operands_ABC_bytes": operands,
        "peak_total_bytes": operands + live + recomb,
        "per_level": per_level,
    }


def depth_first_bytes_closed_form(M: int, K: int, N: int, depth: int) -> int:
    """(4MK + 4KN + 7MN)/4 * sum_{l=0}^{d-1} 4^-l, exact rationals."""
    unit = Fraction(4 * M * K + 4 * K * N + 7 * M * N, 4)
    geo = sum(Fraction(1, 4 ** l) for l in range(depth))
    total = unit * geo * F32
    assert total.denominator == 1, total
    return int(total)


def main() -> None:
    out: dict = {"constants": {
        "float32_bytes": F32, "BLOCK_ROWS": BLOCK_ROWS, "width": W,
        "M_production": M_PROD}}

    # ---- A. batched row-blocked -------------------------------------------
    batched = {}
    for d in range(1, 6):
        enum = batched_stack_bytes_enumerated(d)
        cf = batched_stack_bytes_closed_form(d)
        batched[f"d{d}"] = {
            "enumerated_bytes": enum["total_bytes"],
            "closed_form_bytes": cf,
            "agree": enum["total_bytes"] == cf,
            "MiB": enum["total_bytes"] / MIB,
            "per_level": enum["per_level"],
        }
    out["batched_row_blocked_stacks"] = batched

    # ---- B. depth-first (U-F1's metered sw_product) ------------------------
    df = {}
    for M in (8_064, 64_512):
        rows = {}
        for d in range(0, 6):
            enum = depth_first_bytes_enumerated(M, W, W, d)
            cf = depth_first_bytes_closed_form(M, W, W, d)
            rows[f"d{d}"] = {
                "temporaries_enumerated_bytes": enum["temporaries_bytes"],
                "temporaries_closed_form_bytes": cf,
                "agree": enum["temporaries_bytes"] == cf,
                "recombination_extra_bytes": enum["recombination_extra_bytes"],
                "operands_ABC_bytes": enum["operands_ABC_bytes"],
                "peak_total_bytes": enum["peak_total_bytes"],
                "peak_total_MiB": enum["peak_total_bytes"] / MIB,
            }
        df[f"M{M}"] = rows
    out["depth_first_sw_product"] = df

    # ---- C. ceilings -------------------------------------------------------
    out["ceilings"] = {
        "harness_memory_limit_mb": 65_536,
        "harness_memory_limit_bytes": 65_536 * 1024 * 1024,
        "harness_source": [
            "whestbench/cli.py:393 _default_resource_limits memory_limit_mb=65_536",
            "whestbench/scoring.py:64 ContestSpec.memory_limit_mb: int = 65_536",
            "whestbench/subprocess_worker.py:162 setrlimit(RLIMIT_AS, limit)",
            "whestbench/runner.py:138 local runner: advisory only",
        ],
        "campaign_self_imposed_gate_bytes": 512 * MIB,
        "campaign_gate_source": [
            "COMPRESSION_SCORE_CALCULUS_20260806.md:160 (667.328 MiB vs <512 MiB)",
            "GEN5_MUTANT_RECURSION_20260808.md:133 (peak <= 512 MiB)",
            "HOSTED_INTEL_20260808.md:53 (the 512-MiB gate was self-imposed)",
        ],
        "champion_recorded_peak_bytes": int(round((512 - 1.445) * MIB)),
        "champion_peak_source": [
            "SUBMISSION_DOSSIER_20260808.md:15,113 (1.445 MiB margin under 512)",
            "AGENT_CHANNEL.md:1373 (M81 killed: needed 1.75 MiB, had 1.44 MiB)",
        ],
    }

    # ---- D. champion swap arithmetic --------------------------------------
    d1 = batched_stack_bytes_closed_form(1)
    champ_peak = out["ceilings"]["champion_recorded_peak_bytes"]
    swap = {}
    for d in range(1, 6):
        dd = batched_stack_bytes_closed_form(d)
        delta = dd - d1
        new_peak = champ_peak + delta
        swap[f"d{d}"] = {
            "stack_bytes": dd,
            "stack_MiB": dd / MIB,
            "delta_vs_d1_bytes": delta,
            "delta_vs_d1_MiB": delta / MIB,
            "projected_champion_peak_MiB": new_peak / MIB,
            "over_512MiB_gate": new_peak > 512 * MIB,
            "over_512_by_MiB": (new_peak - 512 * MIB) / MIB,
            "fraction_of_harness_64GiB": new_peak / (65_536 * MIB),
        }
    out["champion_depth_swap"] = swap

    (HERE / "uf1_mem_derive.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
