"""Fresh CPython-3.11 worker for the response-free M160 hostile audit.

The worker deliberately constructs only generated 256x32 weights.  It uses a
temporary CPython-3.11 NumPy wheel and appends the read-only, pinned FlopScope
site-packages directory after NumPy has loaded.  It substitutes the two tiny
WhestBench container types required by the structural prototype, preventing
the cached CPython-3.14-only optional WhestBench stack from being imported.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import types


HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]
PINNED_SITE_PACKAGES = WORK / "whest-v014" / "Lib" / "site-packages"
M145 = WORK / "scorefloor_generation" / "m145_defensive_acg"
M157 = WORK / "scorefloor_generation" / "terra_m157_selfhosted_formal_pilot"
FORMAL = WORK / "scorefloor_generation" / "row_blocked_production" / "candidate_source"
DEFAULT_CP311_DEPS = Path(r"C:\tmp\m160-cp311-deps")


def hostile_effective_compute(
    billed_flops: int, residual_s: float, multiplier: int = 5
) -> float:
    """Project a hostile residual penalty without modifying the bill."""

    return float(billed_flops) + 1e11 * float(multiplier) * float(residual_s)


class _ProcessMemoryCountersEx(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def process_memory() -> dict[str, float]:
    """Return process RSS and private-commit counters from Windows PSAPI."""

    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    if not psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    mib = 1024.0 * 1024.0
    return {
        "rss_mib": counters.WorkingSetSize / mib,
        "peak_rss_mib": counters.PeakWorkingSetSize / mib,
        "private_mib": counters.PrivateUsage / mib,
        # Windows exposes peak private commit as PeakPagefileUsage in this API.
        "peak_private_mib": counters.PeakPagefileUsage / mib,
    }


def _bootstrap_cp311():
    """Load CPython-3.11 NumPy first, then the project-pinned FlopScope."""

    if sys.version_info[:2] != (3, 11):
        raise RuntimeError(f"M160 requires CPython 3.11, got {sys.version}")
    dependency_root = Path(os.environ.get("M160_CP311_DEPS", DEFAULT_CP311_DEPS))
    if not dependency_root.is_dir():
        raise RuntimeError(f"missing isolated CPython-3.11 dependencies: {dependency_root}")
    sys.path.insert(0, str(dependency_root))
    import numpy as np

    if not PINNED_SITE_PACKAGES.is_dir():
        raise RuntimeError(f"missing pinned site-packages: {PINNED_SITE_PACKAGES}")
    sys.path.append(str(PINNED_SITE_PACKAGES))

    class MLP:
        def __init__(self, *, width, depth, weights, seed, name):
            self.width = int(width)
            self.depth = int(depth)
            self.weights = list(weights)
            self.seed = int(seed)
            self.name = str(name)

        def validate(self) -> None:
            expected = (self.width, self.width)
            if self.depth != len(self.weights) or any(
                tuple(weight.shape) != expected for weight in self.weights
            ):
                raise ValueError("generated MLP is not a 256x32 dense stack")

    whestbench = types.ModuleType("whestbench")
    whestbench.BaseEstimator = object
    whestbench.SetupContext = lambda **kwargs: types.SimpleNamespace(**kwargs)
    domain = types.ModuleType("whestbench.domain")
    domain.MLP = MLP
    sys.modules["whestbench"] = whestbench
    sys.modules["whestbench.domain"] = domain

    for path in (M157, M145, FORMAL):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)

    import flopscope as flops
    import flopscope.numpy as fnp
    import m157_selfhosted_formal_pilot as m157_core

    return np, fnp, flops, MLP, m157_core


def generated_he_mlp(np, fnp, MLP, seed: int, case: str):
    """Generate only weights; ``early`` forces a safe layer-2 prune to 32."""

    rng = np.random.default_rng(int(seed))
    scale = np.float32(math.sqrt(2.0 / 256.0))
    weights = [
        fnp.asarray(
            rng.standard_normal((256, 256), dtype=np.float32) * scale,
            dtype=fnp.float32,
        )
    ]
    if case == "early":
        # For a nonnegative first ReLU state, columns 0:32 are strongly on;
        # the remaining columns are strictly non-positive on all pilot inputs.
        # This forces a first Formal pruning branch while retaining 32 paths.
        second = np.full((256, 256), -np.float32(1.0 / 256.0), dtype=np.float32)
        second[:, :32] = np.float32(1.0 / 256.0)
        weights.append(fnp.asarray(second, dtype=fnp.float32))
    else:
        weights.append(
            fnp.asarray(
                rng.standard_normal((256, 256), dtype=np.float32) * scale,
                dtype=fnp.float32,
            )
        )
    for _ in range(2, 32):
        weights.append(
            fnp.asarray(
                rng.standard_normal((256, 256), dtype=np.float32) * scale,
                dtype=fnp.float32,
            )
        )
    mlp = MLP(
        width=256,
        depth=32,
        weights=weights,
        seed=int(seed),
        name=f"m160-{case}-generated-only-{seed}",
    )
    mlp.validate()
    return mlp


def array_sha256(np, value) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    return hashlib.sha256(memoryview(array).cast("B")).hexdigest()


def _early_width(dispatch_records: list[dict]) -> int | None:
    for row in dispatch_records:
        if row["stage"] == "selfhost:formal:layer2:pilot":
            return int(row["shape"][2])
    return None


def one_predict(np, flops, m157_core, estimator, mlp) -> tuple[dict, object | None]:
    """Run one prediction while timing every proposal/main ownership boundary."""

    timing: dict[str, float] = {}
    started = time.perf_counter()
    original_materialize = estimator._materialize_formal_q0
    original_split = estimator._split_with_cached_q0
    original_apply = estimator._apply_one_reflector
    original_fit = m157_core.fit_proposal_f32

    def materialize(*args):
        timing["formal_q0_start_s"] = time.perf_counter() - started
        plan = original_materialize(*args)
        timing["formal_q0_complete_s"] = time.perf_counter() - started
        return plan

    def fit(*args):
        timing["proposal_fit_start_s"] = time.perf_counter() - started
        proposal = original_fit(*args)
        timing["proposal_frozen_s"] = time.perf_counter() - started
        return proposal

    def apply(*args):
        timing.setdefault("first_transport_apply_s", time.perf_counter() - started)
        return original_apply(*args)

    def split(*args):
        timing["formal_main_start_s"] = time.perf_counter() - started
        result = original_split(*args)
        timing["formal_main_complete_s"] = time.perf_counter() - started
        return result

    estimator._materialize_formal_q0 = materialize
    estimator._split_with_cached_q0 = split
    estimator._apply_one_reflector = apply
    m157_core.fit_proposal_f32 = fit
    budget = flops.BudgetContext(10**15, quiet=True, wall_time_limit_s=180.0)
    prediction = None
    failure = None
    try:
        with budget:
            prediction = np.asarray(estimator.predict(mlp, 10**15)).copy()
    except Exception as exc:  # audit records a failure without hiding it
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        estimator._materialize_formal_q0 = original_materialize
        estimator._split_with_cached_q0 = original_split
        estimator._apply_one_reflector = original_apply
        m157_core.fit_proposal_f32 = original_fit

    residual = float(budget.residual_wall_time_s or 0.0)
    summary = budget.summary_dict()
    dispatch = list(estimator.dispatch_trace)
    events = list(estimator.event_log)
    proposal_order = (
        events[:3]
        == [
            "formal_q0_pilot_materialized",
            "proposal_frozen_from_formal_q0_only",
            "main_transport_applied_after_proposal",
        ]
    )
    measured_order = (
        timing.get("formal_q0_complete_s", float("inf"))
        <= timing.get("proposal_fit_start_s", float("-inf"))
        <= timing.get("proposal_frozen_s", float("-inf"))
        <= timing.get("first_transport_apply_s", float("-inf"))
        <= timing.get("formal_main_start_s", float("-inf"))
    )
    record = {
        "failure": failure,
        "wall_s": time.perf_counter() - started,
        "billed_flops": int(budget.flops_used),
        "backend_s": float(budget.flopscope_backend_time_s),
        "overhead_s": float(budget.flopscope_overhead_time_s),
        "residual_s": residual,
        "effective_compute": hostile_effective_compute(int(budget.flops_used), residual, 1),
        "hostile_effective_compute_5x_residual": hostile_effective_compute(
            int(budget.flops_used), residual, 5
        ),
        "flopscope_matmul_calls": int(summary["operations"]["matmul"]["calls"]),
        "matmul_dispatch_calls": int(
            sum(int(row["matmul_calls"]) for row in dispatch)
        ),
        "prediction_shape": list(prediction.shape) if prediction is not None else None,
        "prediction_finite": bool(
            prediction is not None and np.isfinite(prediction).all()
        ),
        "prediction_sha256": array_sha256(np, prediction)
        if prediction is not None
        else None,
        "frame_bank_sha256": array_sha256(np, estimator.frame_bank),
        "event_log": events,
        "proposal_timing_s": timing,
        "proposal_order_event_log": proposal_order,
        "proposal_order_measured": measured_order,
        "transport": dict(estimator.last_transport),
        "reuse_summary": dict(estimator.reuse_summary),
        "dispatch_records": dispatch,
        "first_early_pruned_width": _early_width(dispatch),
    }
    return record, prediction


def run_case(args) -> dict:
    np, fnp, flops, MLP, m157_core = _bootstrap_cp311()
    estimator = m157_core.SelfHostedFormalPilotEstimator()
    setup_started = time.perf_counter()
    estimator.setup(
        types.SimpleNamespace(
            width=256,
            depth=32,
            flop_budget=10**15,
            api_version="m160-generated-structural-only",
            seed=int(args.setup_seed),
        )
    )
    setup_s = time.perf_counter() - setup_started
    initial_bank = array_sha256(np, estimator.frame_bank)
    mlp = generated_he_mlp(np, fnp, MLP, int(args.mlp_seed), args.case)
    after_setup = process_memory()
    first, prediction1 = one_predict(np, flops, m157_core, estimator, mlp)
    after_first = process_memory()
    second, prediction2 = one_predict(np, flops, m157_core, estimator, mlp)
    after_second = process_memory()

    assertions = {
        "first_completed": first["failure"] is None,
        "second_completed": second["failure"] is None,
        "first_finite": first["prediction_finite"],
        "second_finite": second["prediction_finite"],
        "proposal_frozen_before_main_first": first["proposal_order_event_log"]
        and first["proposal_order_measured"],
        "proposal_frozen_before_main_second": second["proposal_order_event_log"]
        and second["proposal_order_measured"],
        "no_dense_proposal_pilot": not any(
            row["stage"].startswith("pilot_surrogate:")
            for row in first["dispatch_records"]
        ),
        "cached_q0_reused": first["reuse_summary"].get(
            "cached_q0_reused_after_proposal"
        )
        is True,
        "first_bank_exactly_restored": first["frame_bank_sha256"] == initial_bank,
        "second_bank_exactly_restored": second["frame_bank_sha256"] == initial_bank,
        "replay_prediction_bitwise_equal": first["prediction_sha256"]
        == second["prediction_sha256"],
    }
    if args.case == "early":
        assertions["adversarial_early_pruning_observed"] = (
            first["first_early_pruned_width"] == 32
        )

    return {
        "status": (
            "M160_CPYTHON311_HOSTILE_WORKER_PASS_NO_EFFICACY"
            if all(assertions.values())
            else "M160_CPYTHON311_HOSTILE_WORKER_FAIL_NO_EFFICACY"
        ),
        "firewall": (
            "generated 256x32 weights only; no truth, labels, reference, MSE, "
            "score, leaderboard, submission, or champion mutation"
        ),
        "runtime": {
            "python": sys.version,
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "flopscope": getattr(flops, "__version__", "unknown"),
            "pinned_site_packages": str(PINNED_SITE_PACKAGES),
            "temporary_cp311_numpy": str(
                Path(os.environ.get("M160_CP311_DEPS", DEFAULT_CP311_DEPS))
            ),
        },
        "case": args.case,
        "seeds": {"setup": int(args.setup_seed), "generated_mlp": int(args.mlp_seed)},
        "setup_s": setup_s,
        "memory_after_setup": after_setup,
        "memory_after_first_predict": after_first,
        "memory_after_second_predict": after_second,
        "workspace_bytes": int(estimator.workspace_bytes),
        "initial_bank_sha256": initial_bank,
        "first_predict": first,
        "second_predict": second,
        "assertions": assertions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=("target", "early"), required=True)
    parser.add_argument("--setup-seed", type=int, required=True)
    parser.add_argument("--mlp-seed", type=int, required=True)
    args = parser.parse_args()
    try:
        result = run_case(args)
    except Exception as exc:
        result = {
            "status": "M160_CPYTHON311_HOSTILE_WORKER_INFRASTRUCTURE_FAILURE_NO_EFFICACY",
            "firewall": "no truth/scorer/competition resource is opened by this worker",
            "case": args.case,
            "seeds": {"setup": int(args.setup_seed), "generated_mlp": int(args.mlp_seed)},
            "failure": f"{type(exc).__name__}: {exc}",
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "case": args.case,
                "output": str(args.output),
                "first_bill": result.get("first_predict", {}).get("billed_flops"),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
