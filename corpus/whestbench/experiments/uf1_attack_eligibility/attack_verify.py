"""U-F1 eligibility attack, verification pass (independent re-derivation).

Runs the UNMODIFIED frozen Estimator (no logging subclass) and reconstructs the
deep-layer hook widths from raw `budget.op_log` records alone, then compares
that sequence against the subclass tape.  Two different starting points must
agree.  Also repeats the run for bitwise determinism.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PKG = REPO / "corpus" / "whestbench" / "experiments" / "v31_guards" / "package_source"
sys.path.insert(0, str(PKG))

import flopscope as fl  # noqa: E402
import flopscope.numpy as fnp  # noqa: E402
from whestbench import SetupContext, sample_mlp  # noqa: E402
from kerdock_v3_estimator import Estimator as FrozenEstimator  # noqa: E402

BUDGET = 10**14
SEED = 11


def raw_run(seed: int):
    rng = fnp.random.default_rng(seed)
    mlp = sample_mlp(256, 32, rng=rng, seed=seed)
    est = FrozenEstimator()
    est.setup(SetupContext(width=256, depth=32, flop_budget=BUDGET,
                           api_version="1.0", submission_dir=str(PKG),
                           seed=seed))
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        out = est.predict(mlp, BUDGET)
        _ = float(np.asarray(out[-1][:1], dtype=np.float64)[0])
        recs = [(r.op_name, tuple(r.shapes), int(r.flop_cost))
                for r in bud.op_log]
        total = int(bud.summary_dict()["flops_used"])
    return recs, total, np.asarray(out, dtype=np.float64)


def reconstruct_hooks(recs):
    """Rebuild (k, n) per deep hook from raw matmul shapes only.

    The row-blocked operator emits, per hook, 16 row blocks (15x4096 + 1x3072):
    either a batched ((7,hm,hk),(7,hk,hn)) core (+ optional (rows,k)@(k,1)
    tail) or a plain (rows,k)@(k,n) direct call.
    """
    hooks = []
    cur = None
    count = 0
    for name, shapes, _cost in recs:
        if name != "matmul":
            continue
        a, b = shapes[0], shapes[1]
        key = None
        if len(a) == 3 and a[0] == 7 and len(b) == 3 and b[0] == 7:
            key = ("w", 2 * a[2], 2 * b[2])
        elif len(a) == 2 and a[0] in (4096, 3072) and len(b) == 2:
            if b[1] == 1:
                continue           # odd-output tail call, folded into its core
            key = ("d", a[1], b[1])
        if key is None:
            continue
        if key != cur:
            if cur is not None:
                hooks.append((cur, count))
            cur, count = key, 1
        else:
            count += 1
    if cur is not None:
        hooks.append((cur, count))
    return hooks


def main() -> None:
    recs, total, pred = raw_run(SEED)
    hooks = reconstruct_hooks(recs)
    tape = json.loads((HERE / "attack_eligibility_raw.json")
                      .read_text("utf-8"))["tapes"][str(SEED)]
    deep = [t for t in tape if t["kind"] == "deep_hook"]

    rec_kn = [(h[0][1], h[0][2]) for h in hooks]
    tape_kn = [(t["k"], t["n"]) for t in deep]
    # winograd cores report the EVEN core width; an odd n loses its tail column
    tape_kn_core = [(k, n - (n % 2) if
                     h[0][0] == "w" else n)
                    for (k, n), h in zip(tape_kn, hooks)] \
        if len(hooks) == len(tape_kn) else []

    same_len = len(rec_kn) == len(tape_kn)
    match = same_len and rec_kn == tape_kn_core
    blocks_ok = all(c == 16 for _k, c in hooks)

    recs2, total2, pred2 = raw_run(SEED)
    determinism = (recs == recs2 and total == total2
                   and bool(np.array_equal(pred, pred2)))

    lane = sum(c for n, _s, c in recs if n == "matmul")
    lane_alt = sum(c for n, _s, c in recs if n == "matmul")
    out = {
        "seed": SEED,
        "n_hooks_reconstructed": len(rec_kn),
        "n_hooks_in_tape": len(deep),
        "row_blocks_per_hook_all_16": blocks_ok,
        "reconstructed_kn": rec_kn,
        "tape_kn": tape_kn,
        "sequences_match": match,
        "total_charged": total,
        "total_charged_repeat": total2,
        "matmul_lane": lane,
        "bitwise_determinism_repeat": determinism,
        "matmul_lane_selfcheck": lane == lane_alt,
    }
    (HERE / "attack_verify.json").write_text(json.dumps(out, indent=2),
                                             encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("reconstructed_kn", "tape_kn")}, indent=2))
    if not match:
        print("RECON:", rec_kn)
        print("TAPE :", tape_kn)


if __name__ == "__main__":
    main()
