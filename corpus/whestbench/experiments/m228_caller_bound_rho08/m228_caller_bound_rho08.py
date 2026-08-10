"""M228: caller-bound accounting boundary around M226's frozen kernel."""

from __future__ import annotations

from pathlib import Path
import sys
import time
import tracemalloc

import flopscope as flops
import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
M226_DIR = EXPERIMENTS / "m226_preallocated_fused_rho08"
if str(M226_DIR) not in sys.path:
    sys.path.insert(0, str(M226_DIR))

import m226_preallocated_fused_rho08 as m226  # noqa: E402


MUTATION = "M228"
M224_CODE_SHA256 = "6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B"
RAW_WALL_STRICT_MAX_S = 0.016133916999970098
M216_BEST_WALL_S = 1.6133916999970097
COMPONENT_CEILING = 6_824_272_176
PREDICTED_BILL_PER_EVENT = 5467
FORBIDDEN_OPERATIONS = ("empty", "copyto", "sum", "max", "reshape")

BoundInputs = m226.BoundInputs
PersistentKernel = m226.PersistentKernel
core = m226.core

_RAW_NAMES = (
    "g",
    "repeated_mean",
    "repeated_sigma",
    "repeated_activation_mean",
    "pair_base_left",
    "pair_base_right",
    "pair_slope_left",
    "pair_slope_right",
    "pair_sigma_left",
    "pair_sigma_right",
    "pair_rho",
    "activation_mean_left",
    "activation_mean_right",
    "activation_vii",
    "activation_vjk",
    "activation_vij",
    "activation_vik",
    "tree",
)
_SOURCE_FILENAMES = {
    str((HERE / "m228_caller_bound_rho08.py").resolve()),
    str((M226_DIR / "m226_preallocated_fused_rho08.py").resolve()),
}


def caller_owned_inputs(packed: core.PackedBatch) -> tuple[BoundInputs, dict[str, object]]:
    """Construct the full ABI in caller setup, before kernel bind/timing."""
    started = time.perf_counter()
    marginal_left, marginal_right = core._marginal_singleton_sigmas(packed)
    columns = {name: np.asarray(getattr(packed, name), dtype=np.float64) for name in _RAW_NAMES}
    columns["marginal_sigma_left"] = marginal_left
    columns["marginal_sigma_right"] = marginal_right
    raw_aliases = [np.shares_memory(columns[name], getattr(packed, name)) for name in _RAW_NAMES]
    setup = {
        "raw_columns_alias_caller": bool(all(raw_aliases)),
        "marginal_left_owns_data": bool(marginal_left.flags.owndata),
        "marginal_right_owns_data": bool(marginal_right.flags.owndata),
        "marginal_bytes": int(marginal_left.nbytes + marginal_right.nbytes),
        "column_count": len(columns),
        "caller_setup_wall_s": time.perf_counter() - started,
        "event_dependent_preprocessing": True,
        "integrated_cost_credit": 0,
    }
    if not setup["raw_columns_alias_caller"]:
        raise RuntimeError("M228 caller setup copied a raw input column")
    if not setup["marginal_left_owns_data"] or not setup["marginal_right_owns_data"]:
        raise RuntimeError("M228 singleton-sigma inputs are not caller-owned")
    return BoundInputs(columns=columns, event_count=packed.size), setup


def _slab_fingerprint(kernel: PersistentKernel) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (int(kernel._float_slab.__array_interface__["data"][0]), int(kernel._float_slab.nbytes)),
        (int(kernel._bool_slab.__array_interface__["data"][0]), int(kernel._bool_slab.nbytes)),
    )


def _source_attributed_growth(before: tracemalloc.Snapshot, after: tracemalloc.Snapshot) -> int:
    growth = 0
    for stat in after.compare_to(before, "traceback"):
        if stat.size_diff <= 0:
            continue
        if any(frame.filename in _SOURCE_FILENAMES for frame in stat.traceback):
            growth += stat.size_diff
    return int(growth)


def measure_bound_kernel_allocation(kernel: PersistentKernel) -> dict[str, object]:
    """Run the explicit, separately reported allocation audit for a bound kernel."""
    tracing_was_active = tracemalloc.is_tracing()
    if not tracing_was_active:
        tracemalloc.start()
    before_snapshot = tracemalloc.take_snapshot()
    before_slabs = _slab_fingerprint(kernel)
    budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=120.0)
    with budget:
        kernel.compile()
    after_snapshot = tracemalloc.take_snapshot()
    after_slabs = _slab_fingerprint(kernel)
    result = {
        "persistent_slab_fingerprint_stable": before_slabs == after_slabs,
        "persistent_total_bytes": int(kernel._float_slab.nbytes + kernel._bool_slab.nbytes),
        "source_attributed_python_bytes": _source_attributed_growth(before_snapshot, after_snapshot),
        "billed_flops": int(budget.flops_used),
        "runtime_allocation_measured": True,
        "tracing_was_active": tracing_was_active,
    }
    if not tracing_was_active:
        tracemalloc.stop()
    return result


def run_billed_bound_kernel(kernel: PersistentKernel) -> dict[str, object]:
    """Time only an already-bound kernel; allocation auditing is a separate phase."""
    before_slabs = _slab_fingerprint(kernel)
    budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=120.0)
    failure = None
    output = None
    started = time.perf_counter()
    try:
        with budget:
            output = kernel.compile()
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    wall = time.perf_counter() - started
    after_slabs = _slab_fingerprint(kernel)
    if before_slabs != after_slabs:
        failure = failure or "RuntimeError: persistent slab pointer/size drift"

    if output is None:
        value = np.full(kernel.event_count, np.nan)
        radius = np.full(kernel.event_count, np.nan)
        chart_ok = np.zeros(kernel.event_count, dtype=bool)
    else:
        value = np.asarray(output[0])
        radius = np.asarray(output[1])
        chart_ok = np.asarray(output[2])
    summary = budget.summary_dict()
    operations = summary.get("operations", {})
    allocation = {
        "persistent_float64_bytes": int(kernel._float_slab.nbytes),
        "persistent_bool_bytes": int(kernel._bool_slab.nbytes),
        "persistent_total_bytes": int(kernel._float_slab.nbytes + kernel._bool_slab.nbytes),
        "persistent_slab_fingerprint_stable": before_slabs == after_slabs,
        "runtime_allocation_measured": False,
        "separate_allocation_audit_required": True,
    }
    return {
        "failure": failure,
        "event_count": kernel.event_count,
        "billed_flops": int(budget.flops_used),
        "residual_wall_s": float(budget.residual_wall_time_s or 0.0),
        "wall_s": wall,
        "operations": operations,
        "allocation": allocation,
        "value": value,
        "radius": radius,
        "chart_ok": chart_ok,
        "fallback_count": int(np.count_nonzero(~chart_ok)),
        "rss_bytes": int(core._m221._m216._rss_bytes()),
    }


def generated_native_batch(seed: int) -> core.PackedBatch:
    return core.generated_native_batch(seed)


__all__ = [
    "BoundInputs",
    "COMPONENT_CEILING",
    "FORBIDDEN_OPERATIONS",
    "M216_BEST_WALL_S",
    "M224_CODE_SHA256",
    "PersistentKernel",
    "PREDICTED_BILL_PER_EVENT",
    "RAW_WALL_STRICT_MAX_S",
    "caller_owned_inputs",
    "core",
    "generated_native_batch",
    "measure_bound_kernel_allocation",
    "run_billed_bound_kernel",
]
