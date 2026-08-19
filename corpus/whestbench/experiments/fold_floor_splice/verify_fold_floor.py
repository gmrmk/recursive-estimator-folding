"""One command that re-runs every claim made for the fold-floor splice.

    python verify_fold_floor.py            # checks (a) and (b), ~30 s
    python verify_fold_floor.py --full     # adds the 2-net end-to-end, ~6 min

(a) every ported tier's integer selfcheck constant, by running the modules'
    own ``_selfcheck``;
(b) small-shape parity: the depth route against the frozen owned_batched
    fallback on random (256,256)x(256,256) and (4096,256,256), reported as max
    absolute and max relative deviation with the f64 product as arbiter;
(c) a 2-net end-to-end against a READ-ONLY import of the incumbent package.

Nothing here writes to ``row_blocked_production``; the incumbent is imported
from its own directory and never opened for writing.
"""

from __future__ import annotations

import importlib
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as _np

HERE = Path(__file__).resolve().parent
FORK = HERE / "candidate_source"
INCUMBENT = HERE.parent / "row_blocked_production" / "candidate_source"

MODULES = [
    "estimator", "orthogonal_fold3", "fold3_estimator", "base_estimator",
    "fold_estimator", "row_blocked_winograd", "cost_model",
    "depth6_winograd", "phased_wht",
]


def _load(root: Path):
    """Import a candidate package in isolation and hand back its modules."""
    saved = {name: sys.modules.pop(name, None) for name in MODULES}
    sys.path.insert(0, str(root))
    try:
        loaded = {}
        for name in MODULES:
            try:
                loaded[name] = importlib.import_module(name)
            except ModuleNotFoundError:
                pass
    finally:
        sys.path.remove(str(root))
        for name in MODULES:
            sys.modules.pop(name, None)
            if saved[name] is not None:
                sys.modules[name] = saved[name]
    return loaded


def check_selfchecks(fork) -> dict:
    fork["cost_model"]  # imported for its constants below
    fork["depth6_winograd"]._selfcheck()
    fork["phased_wht"]._selfcheck()
    cm = fork["cost_model"]
    dw = fork["depth6_winograd"]
    pw = fork["phased_wht"]
    return {
        "tier07_floor_4096_256_256": cm.floor_candidate_bill(4096, 256, 256).total,
        "tier07_strategy": cm.floor_candidate_bill(4096, 256, 256).strategy,
        "owned_batched_4096_256_256": cm.owned_batched_candidate_bill(
            4096, 256, 256).total,
        "direct_4096_256_256": cm.direct_cost(4096, 256, 256),
        "tier07_depth_table": {
            level: cm.inplace_depth_core_cost(4096, 256, 256, level)
            for level in range(1, 9)
        },
        "realized_4096_256_256": {
            level: dw.realized_depth_bill(4096, 256, 256, level).total
            for level in range(2, 7)
        },
        "butterfly_ops_126_256_256": {
            "deployed_transcription": pw.butterfly_ops(
                126, 256, 256, pingpong=False, final_scale=True),
            "pingpong": pw.butterfly_ops(126, 256, 256, pingpong=True),
            "shared_stage_1": pw.butterfly_ops(
                126, 256, 256, pingpong=True, shared_stages=1),
            "shared_stage_2": pw.butterfly_ops(
                126, 256, 256, pingpong=True, shared_stages=2),
        },
    }


def check_small_shape_parity(fork) -> dict:
    import flopscope as flops
    import flopscope.numpy as fnp

    dw = fork["depth6_winograd"]
    rbw = fork["row_blocked_winograd"]
    report = {}
    for m, k, n in ((256, 256, 256), (4096, 256, 256)):
        rng = _np.random.default_rng(20260818)
        a32 = rng.standard_normal((m, k)).astype(_np.float32)
        b32 = rng.standard_normal((k, n)).astype(_np.float32)
        exact = a32.astype(_np.float64) @ b32.astype(_np.float64)
        with flops.BudgetContext(flop_budget=10 ** 15) as budget:
            left, right = fnp.array(a32), fnp.array(b32)
            entry = {}
            for label, op in (
                ("depth_route", dw.DepthWinograd(m, max(k, n),
                                                 workspace_mib=192.0,
                                                 max_levels=6)),
                ("owned_batched_fallback",
                 rbw.RowBlockedBatchedWinograd(m, max(k, n), rbw.BLOCK_ROWS)),
            ):
                op.multiply(left, right)                     # warm the plans
                fresh = fnp.array(b32)   # a distinct object: no weight hoist
                before = budget.flops_used
                got = _np.asarray(op.multiply(left, fresh), dtype=_np.float64)
                fresh_bill = int(budget.flops_used - before)
                before = budget.flops_used
                op.multiply(left, fresh)                  # same object: hoisted
                hoisted_bill = int(budget.flops_used - before)
                entry[label] = {
                    "flops": fresh_bill,
                    "flops_with_weight_hoist": hoisted_bill,
                    "strategy": getattr(op, "last_strategy",
                                        "winograd_batched_preallocated"),
                    "max_abs_vs_f64": float(_np.abs(got - exact).max()),
                    "frobenius_rel_vs_f64": float(
                        _np.linalg.norm(got - exact) / _np.linalg.norm(exact)),
                    "_values": got,
                }
        depth = entry["depth_route"].pop("_values")
        base = entry["owned_batched_fallback"].pop("_values")
        scale = _np.maximum(_np.abs(depth), _np.abs(base))
        entry["depth_vs_fallback"] = {
            "max_abs": float(_np.abs(depth - base).max()),
            "max_rel_elementwise": float(
                (_np.abs(depth - base) / _np.maximum(scale, 1e-30)).max()),
            "frobenius_rel": float(
                _np.linalg.norm(depth - base) / _np.linalg.norm(base)),
            "bit_identical": bool(_np.array_equal(depth, base)),
        }
        entry["flops_ratio"] = (entry["depth_route"]["flops"]
                                / entry["owned_batched_fallback"]["flops"])
        report[f"{m}x{k}x{n}"] = entry
    return report


def check_end_to_end(fork, incumbent, reps: int = 3) -> dict:
    import flopscope as flops
    import flopscope.numpy as fnp
    from whestbench import SetupContext
    from whestbench.domain import MLP

    width, depth, count = 256, 32, 2
    budget_flops = 272_000_000_000
    nets = []
    for index in range(count):
        rng = _np.random.default_rng(1000 + index)
        weights = [
            (rng.standard_normal((width, width))
             * _np.sqrt(2.0 / width)).astype(_np.float32)
            for _ in range(depth)
        ]
        nets.append(MLP(width=width, depth=depth,
                        weights=[fnp.array(w) for w in weights],
                        seed=1000 + index, name=f"mini{index}"))

    def measure(cls, sub_dir):
        residuals = {i: [] for i in range(count)}
        billed, predictions = {}, {}
        for rep in range(reps):
            est = cls()
            with flops.BudgetContext(flop_budget=10 ** 13):
                est.setup(SetupContext(
                    width=width, depth=depth, flop_budget=budget_flops,
                    api_version="0.14", submission_dir=str(sub_dir), seed=0))
            for i, net in enumerate(nets):
                start = time.perf_counter()
                with flops.BudgetContext(flop_budget=10 ** 13) as ctx:
                    out = est.predict(net, budget_flops)
                    billed[i] = int(ctx.flops_used)
                residuals[i].append(float(ctx.residual_wall_time_s))
                if rep == 0:
                    predictions[i] = _np.asarray(out, dtype=_np.float64)
                    billed[(i, "wall")] = time.perf_counter() - start
        return ({i: {"flops": billed[i],
                     "residual": statistics.median(residuals[i]),
                     "residual_samples": [round(x, 4) for x in residuals[i]],
                     "wall": round(billed[(i, "wall")], 3)}
                 for i in range(count)}, predictions)

    class Direct(incumbent["estimator"].Estimator):
        """Incumbent geometry on the plain product: the float32 arbiter."""

        def _first_sample_matmul(self, values, weight):
            return values @ weight

        def _sample_matmul(self, values, weight, firing_rates):
            _ = firing_rates
            return values @ weight

    _, direct = measure(Direct, INCUMBENT)
    inc_meta, inc_pred = measure(incumbent["estimator"].Estimator, INCUMBENT)
    norm = _np.linalg.norm
    inc_dev = [float(norm(inc_pred[i] - direct[i])) for i in range(count)]

    published_shift = 1.7038e-5      # the incumbent's own raw-MSE shift
    routes = {}
    for label, use_floor, levels in (("fold3_only", False, 4),
                                     ("floor_L3", True, 3),
                                     ("floor_L4", True, 4),
                                     ("floor_L5", True, 5),
                                     ("floor_L6", True, 6)):
        fork["estimator"].USE_FLOOR = use_floor
        fork["estimator"].FLOOR_MAX_LEVELS = levels
        meta, pred = measure(fork["estimator"].Estimator, FORK)
        rows = []
        for i in range(count):
            dev = float(norm(pred[i] - direct[i]))
            ratio = dev / inc_dev[i]
            c_inc = inc_meta[i]["flops"] + 100e9 * inc_meta[i]["residual"]
            c_new = meta[i]["flops"] + 100e9 * meta[i]["residual"]
            rows.append({
                "flops": meta[i]["flops"],
                "flops_ratio": meta[i]["flops"] / inc_meta[i]["flops"],
                "residual": round(meta[i]["residual"], 4),
                "residual_samples": meta[i]["residual_samples"],
                "residual_ratio": meta[i]["residual"] / inc_meta[i]["residual"],
                "wall": meta[i]["wall"],
                "wall_ratio": meta[i]["wall"] / inc_meta[i]["wall"],
                "output_ratio_vs_incumbent": float(
                    norm(pred[i]) / norm(inc_pred[i])),
                "rel_dev_vs_incumbent": float(
                    norm(pred[i] - inc_pred[i]) / norm(inc_pred[i])),
                "dev_ratio_vs_incumbent_reassociation": ratio,
                "projected_mse_shift": published_shift * ratio,
                "effective_C": c_new,
                "effective_C_ratio": c_new / c_inc,
            })
        routes[label] = rows
    fork["estimator"].USE_FLOOR = True
    fork["estimator"].FLOOR_MAX_LEVELS = 4
    return {
        "incumbent": {
            str(i): dict(inc_meta[i],
                         effective_C=inc_meta[i]["flops"]
                         + 100e9 * inc_meta[i]["residual"])
            for i in range(count)
        },
        "incumbent_deviation_vs_direct": inc_dev,
        "routes": routes,
    }


def main() -> None:
    fork = _load(FORK)
    report = {
        "selfchecks": check_selfchecks(fork),
        "small_shape_parity": check_small_shape_parity(fork),
    }
    if "--full" in sys.argv:
        report["end_to_end"] = check_end_to_end(fork, _load(INCUMBENT))
    print(json.dumps(report, indent=1, default=float))


if __name__ == "__main__":
    main()
