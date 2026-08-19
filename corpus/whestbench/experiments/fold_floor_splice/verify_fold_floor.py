"""One command that re-runs every claim made for the fold-floor splice.

    python -B verify_fold_floor.py         # checks (a) and (b), ~30 s
    python -B verify_fold_floor.py --full  # adds (c) and (d), ~7 min

(a) every ported tier's integer selfcheck constant, by running the modules'
    own ``_selfcheck`` -- including ``phased_wht``, which is priced but not
    deployed and therefore lives in ``priced_artifacts/`` rather than in the
    shipped package;
(b) small-shape parity: the depth route against the frozen owned_batched
    fallback on random (256,256)x(256,256) and (4096,256,256), reported as max
    absolute and max relative deviation with the f64 product as arbiter;
(c) a 2-net end-to-end against a READ-ONLY import of the incumbent package;
(d) the production gate's ReLU clause: the fraction of post-ReLU sign flips
    between the fold route and the incumbent operator, propagated through the
    same synthetic depth-32 battery, against the frozen ceiling of ``2e-4``.

CUSTODY.  Nothing here writes to ``row_blocked_production``.  The incumbent is
imported from its own directory, and ``sys.dont_write_bytecode`` is set below
before the first import so the import cannot drop ``__pycache__/*.pyc`` into
that tree -- which is exactly what an earlier run of this harness did.  Running
the file by any other route (``runpy``, an IDE, a wrapper) should set
``PYTHONDONTWRITEBYTECODE=1`` in the environment or pass ``-B``, so the
protection does not depend on this module being the entry point.

PACKAGE HYGIENE.  Gate A.7 forbids undeclared binary payload in the archive, so
``main`` fails if any ``__pycache__/*.pyc`` exists in the experiment directory
or in the three package trees by the end of the run.  Git already ignores
``__pycache__/`` and ``*.py[cod]`` repo-wide; this assertion is what stops a
stale ``.pyc`` -- one dropped by running a module directly without ``-B``,
including a compiled copy of a module since removed -- from riding along in a
tarred package that Git never sees.  It is deliberately loud: this repo is
worked on by concurrent processes, and one of them dropped a ``.pyc`` into
``candidate_source`` during a verify run on 2026-08-19.
"""

from __future__ import annotations

import sys

# Must precede every import of a candidate package: the incumbent tree is
# read-only custody, and a stray .pyc there is a write to it.
sys.dont_write_bytecode = True

import importlib                                                 # noqa: E402
import json                                                      # noqa: E402
import statistics                                                # noqa: E402
import time                                                      # noqa: E402
from pathlib import Path                                         # noqa: E402

import numpy as _np                                              # noqa: E402

HERE = Path(__file__).resolve().parent
FORK = HERE / "candidate_source"
PRICED = HERE / "priced_artifacts"
INCUMBENT = HERE.parent / "row_blocked_production" / "candidate_source"

#: the frozen ceiling of production-gate clause A.5
RELU_MISMATCH_GATE = 2e-4

MODULES = [
    "estimator", "orthogonal_fold3", "fold3_estimator", "base_estimator",
    "fold_estimator", "row_blocked_winograd", "cost_model",
    "depth6_winograd",
]

PRICED_MODULES = ["phased_wht"]


def _load(root: Path, names=None):
    """Import a candidate package in isolation and hand back its modules."""
    names = MODULES if names is None else names
    saved = {name: sys.modules.pop(name, None) for name in names}
    sys.path.insert(0, str(root))
    try:
        loaded = {}
        for name in names:
            try:
                loaded[name] = importlib.import_module(name)
            except ModuleNotFoundError:
                pass
    finally:
        sys.path.remove(str(root))
        for name in names:
            sys.modules.pop(name, None)
            if saved[name] is not None:
                sys.modules[name] = saved[name]
    return loaded


def check_selfchecks(fork, priced) -> dict:
    fork["cost_model"]  # imported for its constants below
    fork["depth6_winograd"]._selfcheck()
    priced["phased_wht"]._selfcheck()
    cm = fork["cost_model"]
    dw = fork["depth6_winograd"]
    pw = priced["phased_wht"]
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


def check_relu_mismatch(fork, incumbent, rows: int = 16384,
                        count: int = 2) -> dict:
    """Production-gate clause A.5: post-ReLU sign flips, fold vs incumbent.

    The gate asks for a *fraction of ReLU gate mismatches* on the synthetic
    parent/child battery, ``<= 2e-4``; the incumbent's own receipt reported
    ``1 / 4,194,304 = 2.38419e-7`` for its depth-32 propagation, and the fold
    splice had never measured the clause at all.

    The battery is the same synthetic width-256 depth-32 He nets the end-to-end
    check uses (seeds 1000..), entered the way the estimator enters them: a
    Gaussian half-stack through ``weights[0]``, antipodally doubled by
    ``[relu(z); relu(-z)]``, then propagated ``x = max(x @ W, 0)`` through
    every remaining layer.  One propagation uses the shipped depth route at the
    shipped depth cap and workspace; the other uses the incumbent's own
    ``RowBlockedBatchedWinograd``, imported from the incumbent tree.  A gate
    mismatch is a position where the two disagree on ``x > 0`` after the same
    layer, counted over every hidden layer rather than only the last, so the
    denominator is ``count * (depth - 1) * rows * width``.
    """
    import flopscope as flops
    import flopscope.numpy as fnp

    est = fork["estimator"]
    dw = fork["depth6_winograd"]
    rbw = incumbent["row_blocked_winograd"]

    width, depth = 256, 32
    mismatches = 0
    gates = 0
    per_net = []
    worst_rel = 0.0
    with flops.BudgetContext(flop_budget=10 ** 15):
        for index in range(count):
            rng = _np.random.default_rng(1000 + index)
            weights = [
                (rng.standard_normal((width, width))
                 * _np.sqrt(2.0 / width)).astype(_np.float32)
                for _ in range(depth)
            ]
            seed = _np.random.default_rng(20260818 + index).standard_normal(
                (rows // 2, width)).astype(_np.float32)
            first = fnp.array(seed) @ fnp.array(weights[0])
            start = fnp.concatenate(
                (fnp.maximum(first, 0.0), fnp.maximum(-first, 0.0)), axis=0)

            floor_op = dw.DepthWinograd(
                rows, width,
                workspace_mib=est.FLOOR_WORKSPACE_MIB,
                max_levels=est.FLOOR_MAX_LEVELS)
            base_op = rbw.RowBlockedBatchedWinograd(rows, width, rbw.BLOCK_ROWS)

            x_floor = start
            x_base = start
            net_flips = 0
            for layer in range(1, depth):
                weight = fnp.array(weights[layer])
                x_floor = fnp.maximum(floor_op.multiply(x_floor, weight), 0.0)
                x_base = fnp.maximum(base_op.multiply(x_base, weight), 0.0)
                left = _np.asarray(x_floor) > 0.0
                right = _np.asarray(x_base) > 0.0
                net_flips += int(_np.count_nonzero(left != right))
                gates += left.size
            final_floor = _np.asarray(x_floor, dtype=_np.float64)
            final_base = _np.asarray(x_base, dtype=_np.float64)
            denominator = _np.linalg.norm(final_base)
            relative = float(_np.linalg.norm(final_floor - final_base)
                             / denominator) if denominator else 0.0
            worst_rel = max(worst_rel, relative)
            mismatches += net_flips
            per_net.append({
                "net": index,
                "flips": net_flips,
                "gates": (depth - 1) * rows * width,
                "fraction": net_flips / ((depth - 1) * rows * width),
                "final_relative_frobenius": relative,
                "final_finite": bool(_np.isfinite(final_floor).all()),
            })
            del floor_op, base_op, x_floor, x_base, start, weights

    fraction = mismatches / gates
    return {
        "rows": rows,
        "nets": count,
        "depth": depth,
        "levels": int(est.FLOOR_MAX_LEVELS),
        "workspace_mib": float(est.FLOOR_WORKSPACE_MIB),
        "gate_mismatches": mismatches,
        "gates_compared": gates,
        "mismatch_fraction": fraction,
        "gate_ceiling": RELU_MISMATCH_GATE,
        "pass": bool(fraction <= RELU_MISMATCH_GATE),
        "worst_final_relative_frobenius": worst_rel,
        "per_net": per_net,
    }


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
    priced = _load(PRICED, PRICED_MODULES)
    report = {
        "bytecode_hygiene": None,        # filled in last: see below
        "selfchecks": check_selfchecks(fork, priced),
        "small_shape_parity": check_small_shape_parity(fork),
    }
    if "--full" in sys.argv:
        incumbent = _load(INCUMBENT)
        report["relu_mismatch"] = check_relu_mismatch(fork, incumbent)
        report["end_to_end"] = check_end_to_end(fork, incumbent)
    # Measured after every import this run performs, so it catches a .pyc this
    # harness drops as well as one that shipped with the tree.
    def _compiled(root: Path):
        return sorted(f"{root.name}/__pycache__/{item.name}"
                      for item in (root / "__pycache__").glob("*.pyc"))

    # The payload the clause forbids is the compiled file, not the directory:
    # an emptied ``__pycache__`` left behind by another process carries none.
    stray = [name for root in (HERE, FORK, PRICED, INCUMBENT)
             for name in _compiled(root)]
    report["bytecode_hygiene"] = {
        "sys_dont_write_bytecode": bool(sys.dont_write_bytecode),
        "incumbent_pyc": _compiled(INCUMBENT),
        "fork_pyc": _compiled(FORK),
        "priced_pyc": _compiled(PRICED),
        "harness_pyc": _compiled(HERE),
        "stray_pyc_count": len(stray),
    }
    print(json.dumps(report, indent=1, default=float))
    assert not stray, (
        f"compiled bytecode present: {stray}.  Gate A.7 forbids undeclared "
        f"binary payload in the archive.  Delete it and re-run with -B.")
    if "--full" in sys.argv:
        clause = report["relu_mismatch"]
        assert clause["pass"], (
            f"ReLU mismatch fraction {clause['mismatch_fraction']:.6e} exceeds "
            f"the frozen gate {RELU_MISMATCH_GATE:.1e}")


if __name__ == "__main__":
    main()
