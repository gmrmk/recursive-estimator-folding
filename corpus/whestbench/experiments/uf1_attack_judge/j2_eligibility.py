"""Judge check J2: independent re-measurement of deep-hook shape raggedness and
depth-d lane eligibility on the FROZEN v3.1 GUARDS predict path.

Written from scratch (not a copy of the eligibility falsifier's script) so the
(k,n) sequence and the eligibility fractions are a second signal.

Synthetic He nets only.  No frozen file modified.
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

import flopscope as fl
import flopscope.numpy as fnp
from whestbench import SetupContext, sample_mlp

from cost_model import direct_cost, owned_batched_candidate_bill
from kerdock_v3_estimator import Estimator as Frozen

WIDTH, DEPTH = 256, 32
BUDGET = 10**14
SEEDS = [21, 22, 23, 24, 25]


class Tapped(Frozen):
    def __init__(self):
        super().__init__()
        self.shapes = []

    def _sample_matmul(self, values, weight, firing_rates, *, out):
        self.shapes.append(
            (int(values.shape[0]), int(values.shape[1]), int(weight.shape[1]))
        )
        return super()._sample_matmul(values, weight, firing_rates, out=out)


def strict_depth(m, k, n, cap=8):
    d = 0
    while d < cap and all(v % (1 << (d + 1)) == 0 for v in (m, k, n)):
        d += 1
    return d


rows = []
for seed in SEEDS:
    rng = fnp.random.default_rng(seed)
    mlp = sample_mlp(WIDTH, DEPTH, rng=rng, seed=seed)
    est = Tapped()
    ctx = SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET,
                       api_version="1.0", submission_dir=str(PKG), seed=seed)
    est.setup(ctx)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        est.predict(mlp, BUDGET)
        total = int(bud.summary_dict()["flops_used"])
        matmul_lane = sum(int(r.flop_cost) for r in bud.op_log
                          if r.op_name == "matmul")

    sh = est.shapes
    direct_bill = sum(direct_cost(m, k, n) for (m, k, n) in sh)
    # depth-1 dispatcher rule actually shipped: owned_batched_candidate_bill
    elig_d1 = sum(direct_cost(m, k, n) for (m, k, n) in sh
                  if owned_batched_candidate_bill(m, k, n).strategy
                  == "winograd_batched_owned")
    shipped_bill = sum(owned_batched_candidate_bill(m, k, n).total
                       for (m, k, n) in sh)
    elig = {}
    for d in range(1, 6):
        step = 1 << d
        elig[d] = sum(direct_cost(m, k, n) for (m, k, n) in sh
                      if all(v % step == 0 for v in (m, k, n)))
    rows.append({
        "seed": seed,
        "n_deep_hooks": len(sh),
        "k_sequence": [k for (_m, k, _n) in sh],
        "n_sequence": [n for (_m, _k, n) in sh],
        "odd_k_hooks": sum(1 for (_m, k, _n) in sh if k % 2),
        "k_mod16_zero_hooks": sum(1 for (_m, k, _n) in sh if k % 16 == 0),
        "total_charged": total,
        "matmul_lane_charged": matmul_lane,
        "deep_hook_direct_equivalent": direct_bill,
        "deep_hook_shipped_bill": shipped_bill,
        "shipped_over_direct": shipped_bill / direct_bill,
        "eligible_share_shipped_dispatcher_rule": elig_d1 / direct_bill,
        "strict_eligible_share_by_depth": {
            str(d): elig[d] / direct_bill for d in elig},
        "deepest_strict_depth_per_hook": [strict_depth(m, k, n) for (m, k, n) in sh],
    })
    print(f"seed {seed}: hooks={len(sh)} oddk={rows[-1]['odd_k_hooks']} "
          f"d1_rule={rows[-1]['eligible_share_shipped_dispatcher_rule']:.4f} "
          f"d4_strict={rows[-1]['strict_eligible_share_by_depth']['4']:.4f}",
          flush=True)

summary = {
    "mean_eligible_share_shipped_dispatcher_rule":
        float(np.mean([r["eligible_share_shipped_dispatcher_rule"] for r in rows])),
    "mean_strict_by_depth": {
        str(d): float(np.mean([r["strict_eligible_share_by_depth"][str(d)]
                               for r in rows])) for d in range(1, 6)},
    "mean_shipped_over_direct":
        float(np.mean([r["shipped_over_direct"] for r in rows])),
    "per_seed_d1_rule": [r["eligible_share_shipped_dispatcher_rule"] for r in rows],
    "per_seed_d4_strict": [r["strict_eligible_share_by_depth"]["4"] for r in rows],
}
out = {"rows": rows, "summary": summary}
print(json.dumps(summary, indent=2))
(HERE / "j2_eligibility.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
