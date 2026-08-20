"""U-F1 hostile attack, surface = LANE ELIGIBILITY.

Independently derive, from the FROZEN v3.1 GUARDS predict path, how much of the
champion's charged matmul lane can actually carry a Strassen-Winograd recursion
to depth d, and re-translate the adjusted score.

Method
------
1. Import the frozen estimator from experiments/v31_guards/package_source/ with
   a THIN logging subclass (no behaviour change: every override records the
   logical shape and delegates to super()).
2. Run one full predict per synthetic He net (width 256, depth 32) inside a
   flopscope BudgetContext; read `budget.op_log` for the exact per-op charge.
3. Partition the charged bill into: matmul lane vs elementwise lane; and inside
   the matmul lane, deep-layer hook products vs everything else.
4. For every LOGICAL product (m,k,n) compute the deepest lawful Strassen
   recursion (2^d | m, k, n) and the depth-d eligible direct-equivalent volume.
5. Emit the bill-weighted eligible fraction at every depth under three
   denominators and re-run the published score translation with it.

Read-only outside this directory. No scorer, truth, holdout or network access.
Synthetic He nets only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PKG = REPO / "corpus" / "whestbench" / "experiments" / "v31_guards" / "package_source"
UF1 = REPO / "corpus" / "whestbench" / "experiments" / "uf1_strassen_flop_accounting"
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(UF1))

import flopscope as fl  # noqa: E402
import flopscope.numpy as fnp  # noqa: E402
from whestbench import SetupContext, sample_mlp  # noqa: E402

from kerdock_v3_estimator import Estimator as FrozenEstimator  # noqa: E402
from uf1_derive_and_verify import matmul_charge, strassen_charge  # noqa: E402

BUDGET = 10**14
VARIANT = "V1_winograd15_floor"
WIDTH, DEPTH = 256, 32
SEEDS = [11, 12, 13, 14, 15]


def live_flops() -> int:
    return int(fl.budget_summary_dict()["flops_used"])


class TracedEstimator(FrozenEstimator):
    """Frozen behaviour + a shape/charge tape.  Every hook calls super()."""

    def __init__(self) -> None:
        super().__init__()
        self.tape: list[dict] = []

    def _first_sample_matmul(self, phases, weight, *, out=None):
        before = live_flops()
        result = super()._first_sample_matmul(phases, weight, out=out)
        self.tape.append({
            "kind": "first_product_WHT",
            "m": int(self.n_base), "k": int(weight.shape[0]),
            "n": int(weight.shape[1]),
            "charged": live_flops() - before,
        })
        return result

    def _sample_matmul(self, values, weight, firing_rates, *, out):
        m, k = int(values.shape[0]), int(values.shape[1])
        n = int(weight.shape[1])
        before = live_flops()
        result = super()._sample_matmul(values, weight, firing_rates, out=out)
        self.tape.append({
            "kind": "deep_hook", "m": m, "k": k, "n": n,
            "charged": live_flops() - before,
        })
        return result


def deepest_depth(m: int, k: int, n: int, cap: int = 8) -> int:
    d = 0
    while d < cap and all(v % (1 << (d + 1)) == 0 for v in (m, k, n)):
        d += 1
    return d


def run_one(seed: int) -> dict:
    rng = fnp.random.default_rng(seed)
    mlp = sample_mlp(WIDTH, DEPTH, rng=rng, seed=seed)
    est = TracedEstimator()
    ctx = SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET,
                       api_version="1.0", submission_dir=str(PKG), seed=seed)
    est.setup(ctx)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        out = est.predict(mlp, BUDGET)
        _ = float(np.asarray(out[-1][:1], dtype=np.float64)[0])
        log = list(bud.op_log)
        total = int(bud.summary_dict()["flops_used"])
    tape = est.tape

    by_op: dict[str, list[int]] = {}
    for rec in log:
        by_op.setdefault(rec.op_name, [0, 0])
        by_op[rec.op_name][0] += 1
        by_op[rec.op_name][1] += int(rec.flop_cost)
    matmul_lane = by_op.get("matmul", [0, 0])[1]

    hook_charged = sum(t["charged"] for t in tape if t["kind"] == "deep_hook")
    first_charged = sum(t["charged"] for t in tape
                        if t["kind"] == "first_product_WHT")
    return {
        "seed": seed,
        "total_charged": total,
        "matmul_lane_charged": matmul_lane,
        "op_totals": {k: {"calls": v[0], "flops": v[1]}
                      for k, v in sorted(by_op.items(),
                                         key=lambda kv: -kv[1][1])},
        "n_deep_hooks": sum(1 for t in tape if t["kind"] == "deep_hook"),
        "deep_hook_charged": hook_charged,
        "first_product_charged": first_charged,
        "tape": tape,
    }


def eligibility(runs: list[dict]) -> dict:
    out: dict[str, object] = {}
    per_seed = []
    for run in runs:
        deep = [t for t in run["tape"] if t["kind"] == "deep_hook"]
        direct_hook = sum(matmul_charge(t["m"], t["k"], t["n"]) for t in deep)
        rows = {}
        for d in range(0, 9):
            step = 1 << d
            strict = [t for t in deep
                      if t["m"] % step == 0 and t["k"] % step == 0
                      and t["n"] % step == 0]
            strict_vol = sum(matmul_charge(t["m"], t["k"], t["n"])
                             for t in strict)
            # generous: split off the ragged k-slab and n-tail, charge them
            # direct, recurse only on the 2^d-divisible core.
            gen_vol = 0
            for t in deep:
                if t["m"] % step:
                    continue
                kc = t["k"] - (t["k"] % step)
                nc = t["n"] - (t["n"] % step)
                if kc == 0 or nc == 0:
                    continue
                gen_vol += matmul_charge(t["m"], kc, nc)
            rows[d] = {
                "strict_calls": len(strict),
                "strict_direct_volume": strict_vol,
                "strict_frac_of_deep_hook_direct":
                    strict_vol / direct_hook if direct_hook else 0.0,
                "generous_core_volume": gen_vol,
                "generous_frac_of_deep_hook_direct":
                    gen_vol / direct_hook if direct_hook else 0.0,
            }
        per_seed.append({
            "seed": run["seed"],
            "n_deep_hooks": len(deep),
            "deep_hook_direct_volume": direct_hook,
            "deep_hook_charged_actual": run["deep_hook_charged"],
            "matmul_lane_charged": run["matmul_lane_charged"],
            "total_charged": run["total_charged"],
            "deep_hook_share_of_matmul_lane":
                run["deep_hook_charged"] / run["matmul_lane_charged"],
            "matmul_share_of_total":
                run["matmul_lane_charged"] / run["total_charged"],
            "widths_k": [t["k"] for t in deep],
            "widths_n": [t["n"] for t in deep],
            "max_depth_per_hook": [deepest_depth(t["m"], t["k"], t["n"])
                                   for t in deep],
            "by_depth": rows,
        })
    out["per_seed"] = per_seed
    return out


def main() -> None:
    fl.configure(symmetry_warnings=False)
    runs = []
    for seed in SEEDS:
        run = run_one(seed)
        runs.append(run)
        print(f"seed={seed} total={run['total_charged']/1e9:.6f}B "
              f"matmul={run['matmul_lane_charged']/1e9:.6f}B "
              f"hooks={run['n_deep_hooks']} "
              f"hook_charged={run['deep_hook_charged']/1e9:.6f}B", flush=True)
    result = {"runs": [{k: v for k, v in r.items() if k != "tape"}
                       for r in runs],
              "tapes": {str(r["seed"]): r["tape"] for r in runs}}
    result["eligibility"] = eligibility(runs)
    (HERE / "attack_eligibility_raw.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    print("wrote attack_eligibility_raw.json", flush=True)


if __name__ == "__main__":
    main()
