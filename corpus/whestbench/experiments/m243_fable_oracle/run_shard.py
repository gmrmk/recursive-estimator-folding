"""G0B shard runner for Fable's independent M243 oracle.

    python run_shard.py --shard {0,1,2,3} --authorize-g0b

Shard map (task directive; the predeclaration defines two 128-draw cells,
the shards split each cell's occurrence indices in half):

    shard 0: cell P0, occurrence indices 0..63
    shard 1: cell P0, occurrence indices 64..127
    shard 2: cell P1, occurrence indices 0..63
    shard 3: cell P1, occurrence indices 64..127

Discipline: 5400 s wall clock and 2048 MiB RSS, checked in-loop before
every event.  On a cap the runner checkpoints and exits (code 3 = wall
clock, code 4 = memory); rerunning the same command resumes from the
JSONL checkpoint, skipping completed occurrence indices.  Without
--authorize-g0b the runner only prints the plan and exits: G0B may run
only after Sol's G0A PASS trigger (predeclaration section 11, step 6).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_g0a_oracle as oracle


def shard_events(shard: int):
    """Deterministic event stream for one shard: full-cell regeneration,
    q0 proposal, the frozen 128-draw stream, then this shard's slice."""
    cell_name, lo, hi = oracle.SHARDS[shard]
    mu, C, W = oracle.regenerate_g0b_cell(cell_name)
    proposal = oracle.build_proposal(mu, C, W)
    draws = oracle.draw_events(cell_name, proposal)
    if draws.shape != (oracle.EVENT_DRAWS_PER_CELL, 3):
        raise oracle.OracleHardFail("event draw shape mismatch")
    return cell_name, mu, C, W, proposal, draws, lo, hi


def per_event(mu, C, W, proposal, i, j, k):
    q_e = oracle.q_e_check(proposal, i, j, k)
    rec = oracle.oracle_event(mu, C, i, j, k,
                              dps_pair=oracle.MPMATH_DPS,
                              tol=oracle.REFERENCE_SELF_TOL)
    if "refusal" in rec:
        raise oracle.OracleHardFail(f"oracle refusal on drawn event: {rec}")
    rec["q_e"] = q_e
    rec["weight_sq"] = oracle.feature_weight_sq(W, i, j, k, q_e)
    # two-signal cross-check: frozen M122 Hermite-series re-derivation
    xc = oracle.delta_series_cross_check(mu, C, i, j, k)
    rec["delta_series_cross_check"] = xc
    if abs(xc - rec["delta_reference"]) > oracle.EXPECTATION_TOL * (
            1 + abs(rec["delta_reference"])):
        raise oracle.OracleHardFail(
            f"Delta cross-check disagreement: {xc} vs "
            f"{rec['delta_reference']}")
    return rec


def run_shard_core(work, per_event_fn, out_path,
                   wall_cap_s=oracle.WALL_CLOCK_CAP_S,
                   mem_cap_mib=oracle.MEMORY_CAP_MIB,
                   log=print):
    """Cap-disciplined checkpointed loop.  `work` is a list of
    (occurrence_index, (i, j, k)).  Returns 'DONE' | 'WALL' | 'MEM'."""
    done = set()
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    done.add(json.loads(line)["occurrence"])
        log(f"resume: {len(done)} occurrences already checkpointed")
    start = time.monotonic()
    with open(out_path, "a", encoding="utf-8") as out:
        for occ, (i, j, k) in work:
            if occ in done:
                continue
            elapsed = time.monotonic() - start
            if elapsed > wall_cap_s:
                log(f"wall-clock cap {wall_cap_s}s reached at occurrence "
                    f"{occ}; checkpoint is complete, rerun to resume")
                return "WALL"
            rss = oracle.rss_mib()
            if math.isnan(rss):
                log("WARNING: RSS probe unavailable on this platform; "
                    "memory cap check reported as UNAVAILABLE")
            elif rss > mem_cap_mib:
                log(f"memory cap {mem_cap_mib} MiB exceeded (rss={rss:.0f}); "
                    "checkpoint is complete, rerun to resume")
                return "MEM"
            rec = per_event_fn(int(i), int(j), int(k))
            rec["occurrence"] = int(occ)
            out.write(json.dumps(rec) + "\n")
            out.flush()
            log(f"occurrence {occ} event ({i},{j},{k}) done "
                f"[{time.monotonic() - start:.1f}s]")
    return "DONE"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True, choices=[0, 1, 2, 3])
    ap.add_argument("--out-dir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "g0b_results"))
    ap.add_argument("--authorize-g0b", action="store_true",
                    help="required to actually run; G0B is gated on Sol's "
                         "G0A PASS trigger")
    args = ap.parse_args(argv)

    # hash-verification hooks: frozen inputs, manifest fields, and every
    # shared module hash are checked before any computation
    oracle.verify_frozen_inputs()
    oracle.validate_manifest()
    for name in oracle.PARENT_SHA256:
        oracle.import_frozen(name)

    cell_name, lo, hi = oracle.SHARDS[args.shard]
    print(f"shard {args.shard}: cell {cell_name}, occurrences {lo}..{hi - 1}, "
          f"caps {oracle.WALL_CLOCK_CAP_S:.0f}s / "
          f"{oracle.MEMORY_CAP_MIB:.0f} MiB, dps {oracle.MPMATH_DPS}")
    if not args.authorize_g0b:
        print("DRY: --authorize-g0b not given; not running (G0B awaits "
              "Sol's G0A PASS trigger). Exiting 0.")
        return 0

    cell_name, mu, C, W, proposal, draws, lo, hi = shard_events(args.shard)
    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"shard{args.shard}_{cell_name}.jsonl")
    work = [(occ, tuple(draws[occ])) for occ in range(lo, hi)]
    state = run_shard_core(
        work, lambda i, j, k: per_event(mu, C, W, proposal, i, j, k),
        out_path)
    print(f"shard {args.shard} state: {state}; checkpoint: {out_path}")
    return {"DONE": 0, "WALL": 3, "MEM": 4}[state]


if __name__ == "__main__":
    sys.exit(main())
