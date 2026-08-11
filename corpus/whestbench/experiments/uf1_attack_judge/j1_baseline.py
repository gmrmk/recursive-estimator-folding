"""Judge check J1: is the champion's deep-layer lane already depth-1 Winograd,
and what is its metered ratio against classical direct?

Two independent signals:
  (A) frozen cost_model closed form  owned_batched_candidate_bill(m,k,n).total
  (B) live flopscope BudgetContext metering of the frozen
      RowBlockedBatchedWinograd.multiply on the exact claim shape.
No frozen file is modified; this script only imports them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent / "v31_guards" / "package_source"
sys.path.insert(0, str(PKG))

import numpy as np
import flopscope as fl
import flopscope.numpy as fnp

from cost_model import direct_cost, owned_batched_candidate_bill
import row_blocked_winograd as rbw

M, K, N = 64512, 256, 256

out = {}
direct = direct_cost(M, K, N)
bill = owned_batched_candidate_bill(M, K, N)
out["signal_A_closed_form"] = {
    "strategy": bill.strategy,
    "total": bill.total,
    "direct": direct,
    "r_vs_direct": bill.total / direct,
}

rng = np.random.default_rng(20260810)
a = np.asarray(rng.standard_normal((M, K)), dtype=np.float32)
b = np.asarray(rng.standard_normal((K, N)), dtype=np.float32)
fa, fb = fnp.asarray(a), fnp.asarray(b)
op = rbw.RowBlockedBatchedWinograd(M, K, rbw.BLOCK_ROWS)
with fl.BudgetContext(flop_budget=10**18, quiet=True) as bud:
    C = fnp.empty((M, N), dtype=fnp.float32)
    op.multiply(fa, fb, out=C)
    metered = int(bud.summary_dict()["flops_used"])
out["signal_B_metered_frozen_kernel"] = {
    "BLOCK_ROWS": rbw.BLOCK_ROWS,
    "metered_flops": metered,
    "r_vs_direct": metered / direct,
    "matches_closed_form": metered == bill.total,
}

# correctness of the frozen kernel output (so the bill is a bill of a real product)
ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
got = np.asarray(C, dtype=np.float64)
out["frozen_kernel_rel_frobenius_vs_f64"] = float(
    np.linalg.norm(got - ref) / np.linalg.norm(ref)
)

# also meter a plain classical fnp.matmul for the same shape as a third anchor
with fl.BudgetContext(flop_budget=10**18, quiet=True) as bud2:
    D = fnp.empty((M, N), dtype=fnp.float32)
    fnp.matmul(fa, fb, out=D)
    metered_direct = int(bud2.summary_dict()["flops_used"])
out["metered_classical_matmul"] = {
    "metered_flops": metered_direct,
    "closed_form_direct": direct,
    "match": metered_direct == direct,
}

print(json.dumps(out, indent=2))
(HERE / "j1_baseline.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
