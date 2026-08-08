"""M183 falsifier: does the frozen Kerdock v3 pipeline bill any float64 lanes?

Predeclared (M182 miner's spec): run v3 on ONE synthetic net inside a
BudgetContext, scan budget.op_log for ops whose dtypes include float64 (or
complex), and report the billed share. KILL M183 (no headroom) if the
float64-lane share of billed FLOPs < 5%. Response-free; synthetic net only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
V3 = (r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
      r"\work\scorefloor_generation\kerdock_l1_owned_buffer\candidate_source_validator_v3")
sys.path.insert(0, V3)

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import SetupContext
from whestbench.domain import MLP

WIDTH, DEPTH = 256, 32


def make_mlp(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(np.sqrt(2.0 / WIDTH))
    w = [fnp.array((rng.standard_normal((WIDTH, WIDTH)).astype(np.float32) * g))
         for _ in range(DEPTH)]
    m = MLP(width=WIDTH, depth=DEPTH, weights=w, seed=seed)
    m.validate()
    return m


def main():
    import estimator as est_mod
    with flops.BudgetContext(flop_budget=int(1e15), quiet=True) as budget:
        est = est_mod.Estimator()
        ctx = SetupContext(width=WIDTH, depth=DEPTH, seed=0,
                           submission_dir=Path(V3),
                           flop_budget=int(2.72e11), api_version="2.0")
        est.setup(ctx)
        mlp = make_mlp(101)
        est.predict(mlp, int(2.72e11))
        ops = list(budget.op_log)

    total = 0.0
    f64 = 0.0
    by_op_f64 = {}
    for op in ops:
        cost = float(getattr(op, "flop_cost", 0) or 0)
        total += cost
        dts = getattr(op, "dtypes", None) or ()
        names = [str(getattr(d, "name", d)) for d in (dts if isinstance(dts, (list, tuple)) else [dts])]
        if any(("float64" in n) or ("complex" in n) for n in names):
            f64 += cost
            key = f"{getattr(op, 'name', '?')}|{','.join(sorted(set(names)))}"
            by_op_f64[key] = by_op_f64.get(key, 0.0) + cost

    share = f64 / total if total else 0.0
    top = sorted(by_op_f64.items(), key=lambda kv: -kv[1])[:15]
    out = {"total_billed": total, "f64_lane_billed": f64, "f64_share": share,
           "top_f64_ops": top,
           "verdict": ("KILL: f64 share < 5% (no headroom)" if share < 0.05
                       else f"HEADROOM: f64 lanes bill {share:.1%} -> recast is worth ~{1/(1-share/2):.2f}x")}
    (HERE / "m183_falsifier_results.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"total billed: {total:.4e}")
    print(f"float64-lane billed: {f64:.4e}  share: {share:.2%}")
    for k, v in top:
        print(f"  {v:.3e}  {k}")
    print(out["verdict"])


if __name__ == "__main__":
    main()
