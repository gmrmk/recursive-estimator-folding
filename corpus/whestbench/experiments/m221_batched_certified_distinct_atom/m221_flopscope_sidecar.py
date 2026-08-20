"""Charged one-batch FlopScope implementation of the M221 vector chart."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

import m221_batched_certified_distinct_atom as core


RUNTIME_FIELDS = tuple(
    field.name
    for field in fields(core.PackedBatch)
    if field.name not in ("labels", "local_states")
)


@dataclass
class StagedBatch:
    columns: dict[str, np.ndarray]


@dataclass
class Workspace:
    sign_g: np.ndarray
    mean_left: np.ndarray
    mean_right: np.ndarray
    alpha_left: np.ndarray
    alpha_right: np.ndarray
    t_left: np.ndarray
    t_right: np.ndarray
    phi_args: np.ndarray
    phi_x: np.ndarray
    phi_y: np.ndarray
    phi_acc: np.ndarray
    phi_out: np.ndarray
    univariate_density: np.ndarray
    q: np.ndarray
    r_grid: np.ndarray
    one_grid: np.ndarray
    quadratic_grid: np.ndarray
    temp_grid: np.ndarray
    phi2: np.ndarray
    joint: np.ndarray
    standard_pair: np.ndarray
    raw_pair: np.ndarray
    unary_left: np.ndarray
    unary_right: np.ndarray
    centered_pair: np.ndarray
    repeated_preactivation: np.ndarray
    repeated_centered: np.ndarray
    central: np.ndarray
    signed: np.ndarray
    temp1: np.ndarray
    temp2: np.ndarray
    temp3: np.ndarray
    offset: np.ndarray
    value: np.ndarray
    radius: np.ndarray
    max_alpha: np.ndarray
    max_t: np.ndarray
    max_repeated: np.ndarray
    chart_ok: np.ndarray
    bool_temp: np.ndarray


def allocate_staged(event_count: int) -> StagedBatch:
    return StagedBatch(
        {name: fnp.empty(event_count, dtype=fnp.float64) for name in RUNTIME_FIELDS}
    )


def allocate_workspace(event_count: int) -> Workspace:
    sb = (2, event_count)
    phi = (8, event_count)
    grid = (2, event_count, core.SIMPSON_NODES)
    return Workspace(
        sign_g=fnp.empty(sb, dtype=fnp.float64),
        mean_left=fnp.empty(sb, dtype=fnp.float64),
        mean_right=fnp.empty(sb, dtype=fnp.float64),
        alpha_left=fnp.empty(sb, dtype=fnp.float64),
        alpha_right=fnp.empty(sb, dtype=fnp.float64),
        t_left=fnp.empty(sb, dtype=fnp.float64),
        t_right=fnp.empty(sb, dtype=fnp.float64),
        phi_args=fnp.empty(phi, dtype=fnp.float64),
        phi_x=fnp.empty(phi, dtype=fnp.float64),
        phi_y=fnp.empty(phi, dtype=fnp.float64),
        phi_acc=fnp.empty(phi, dtype=fnp.float64),
        phi_out=fnp.empty(phi, dtype=fnp.float64),
        univariate_density=fnp.empty((4, event_count), dtype=fnp.float64),
        q=fnp.empty(event_count, dtype=fnp.float64),
        r_grid=fnp.empty(grid, dtype=fnp.float64),
        one_grid=fnp.empty(grid, dtype=fnp.float64),
        quadratic_grid=fnp.empty(grid, dtype=fnp.float64),
        temp_grid=fnp.empty(grid, dtype=fnp.float64),
        phi2=fnp.empty(sb, dtype=fnp.float64),
        joint=fnp.empty(sb, dtype=fnp.float64),
        standard_pair=fnp.empty(sb, dtype=fnp.float64),
        raw_pair=fnp.empty(sb, dtype=fnp.float64),
        unary_left=fnp.empty(sb, dtype=fnp.float64),
        unary_right=fnp.empty(sb, dtype=fnp.float64),
        centered_pair=fnp.empty(sb, dtype=fnp.float64),
        repeated_preactivation=fnp.empty(sb, dtype=fnp.float64),
        repeated_centered=fnp.empty(sb, dtype=fnp.float64),
        central=fnp.empty(sb, dtype=fnp.float64),
        signed=fnp.empty(sb, dtype=fnp.float64),
        temp1=fnp.empty(sb, dtype=fnp.float64),
        temp2=fnp.empty(sb, dtype=fnp.float64),
        temp3=fnp.empty(sb, dtype=fnp.float64),
        offset=fnp.empty(event_count, dtype=fnp.float64),
        value=fnp.empty(event_count, dtype=fnp.float64),
        radius=fnp.empty(event_count, dtype=fnp.float64),
        max_alpha=fnp.empty(event_count, dtype=fnp.float64),
        max_t=fnp.empty(event_count, dtype=fnp.float64),
        max_repeated=fnp.empty(event_count, dtype=fnp.float64),
        chart_ok=fnp.empty(event_count, dtype=fnp.bool_),
        bool_temp=fnp.empty(event_count, dtype=fnp.bool_),
    )


def allocation_ledger(staged: StagedBatch, workspace: Workspace) -> dict[str, object]:
    staged_bytes = int(sum(array.nbytes for array in staged.columns.values()))
    workspace_rows = {
        field.name: int(getattr(workspace, field.name).nbytes)
        for field in fields(workspace)
    }
    workspace_bytes = int(sum(workspace_rows.values()))
    return {
        "staged_columns": len(staged.columns),
        "staged_bytes": staged_bytes,
        "workspace_buffers": len(workspace_rows),
        "workspace_bytes": workspace_bytes,
        "workspace": workspace_rows,
        "total_bytes": staged_bytes + workspace_bytes,
        "unlisted_user_temporaries": 0,
    }


def stage_inputs(packed: core.PackedBatch, staged: StagedBatch) -> None:
    if set(staged.columns) != set(RUNTIME_FIELDS):
        raise ValueError("M221 staged ABI mismatch")
    for name in RUNTIME_FIELDS:
        fnp.copyto(staged.columns[name], np.asarray(getattr(packed, name), dtype=np.float64))


def _phi16_combined(arguments: np.ndarray, workspace: Workspace) -> None:
    fnp.multiply(arguments, fnp.float64(core.INV_SQRT_TWO), out=workspace.phi_x)
    fnp.multiply(workspace.phi_x, workspace.phi_x, out=workspace.phi_y)
    fnp.multiply(workspace.phi_y, fnp.float64(0.0), out=workspace.phi_acc)
    fnp.add(workspace.phi_acc, fnp.float64(core._ERF_COEFFICIENTS[-1]), out=workspace.phi_acc)
    for coefficient in core._ERF_COEFFICIENTS[-2::-1]:
        fnp.multiply(workspace.phi_acc, workspace.phi_y, out=workspace.phi_acc)
        fnp.add(workspace.phi_acc, fnp.float64(coefficient), out=workspace.phi_acc)
    fnp.multiply(workspace.phi_acc, workspace.phi_x, out=workspace.phi_acc)
    fnp.multiply(workspace.phi_acc, fnp.float64(0.5), out=workspace.phi_out)
    fnp.add(workspace.phi_out, fnp.float64(0.5), out=workspace.phi_out)


def compile_batch(staged: StagedBatch, x: Workspace) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    c = staged.columns
    count = c["g"].size
    # Antithetic sign plane.
    fnp.copyto(x.sign_g[0], c["g"])
    fnp.multiply(c["g"], fnp.float64(-1.0), out=x.sign_g[1])
    fnp.multiply(c["pair_slope_left"][None, :], x.sign_g, out=x.mean_left)
    fnp.add(x.mean_left, c["pair_base_left"][None, :], out=x.mean_left)
    fnp.multiply(c["pair_slope_right"][None, :], x.sign_g, out=x.mean_right)
    fnp.add(x.mean_right, c["pair_base_right"][None, :], out=x.mean_right)
    fnp.divide(x.mean_left, c["pair_sigma_left"][None, :], out=x.alpha_left)
    fnp.divide(x.mean_right, c["pair_sigma_right"][None, :], out=x.alpha_right)

    fnp.multiply(c["pair_rho"], c["pair_rho"], out=x.offset)
    fnp.multiply(x.offset, fnp.float64(-1.0), out=x.offset)
    fnp.add(x.offset, fnp.float64(1.0), out=x.offset)
    fnp.sqrt(x.offset, out=x.q)
    fnp.multiply(c["pair_rho"][None, :], x.alpha_left, out=x.t_left)
    fnp.subtract(x.alpha_right, x.t_left, out=x.t_left)
    fnp.divide(x.t_left, x.q[None, :], out=x.t_left)
    fnp.multiply(c["pair_rho"][None, :], x.alpha_right, out=x.t_right)
    fnp.subtract(x.alpha_left, x.t_right, out=x.t_right)
    fnp.divide(x.t_right, x.q[None, :], out=x.t_right)

    # One combined Phi recurrence for alpha_left, alpha_right, t_left, t_right.
    fnp.copyto(x.phi_args[0:2], x.alpha_left)
    fnp.copyto(x.phi_args[2:4], x.alpha_right)
    fnp.copyto(x.phi_args[4:6], x.t_left)
    fnp.copyto(x.phi_args[6:8], x.t_right)
    _phi16_combined(x.phi_args, x)
    Phi_left = x.phi_out[0:2]
    Phi_right = x.phi_out[2:4]
    Phi_t_left = x.phi_out[4:6]
    Phi_t_right = x.phi_out[6:8]

    # phi(alpha) in one four-row call.
    fnp.multiply(x.phi_args[0:4], x.phi_args[0:4], out=x.univariate_density)
    fnp.multiply(x.univariate_density, fnp.float64(-0.5), out=x.univariate_density)
    fnp.exp(x.univariate_density, out=x.univariate_density)
    fnp.multiply(x.univariate_density, fnp.float64(core.INV_SQRT_TWO_PI), out=x.univariate_density)
    phi_left = x.univariate_density[0:2]
    phi_right = x.univariate_density[2:4]

    # Plackett composite-Simpson grid.  All 33 runtime nodes are charged.
    fnp.multiply(
        c["pair_rho"][None, :, None],
        core._SIMPSON_FRACTIONS[None, None, :],
        out=x.r_grid,
    )
    fnp.multiply(x.r_grid, x.r_grid, out=x.one_grid)
    fnp.multiply(x.one_grid, fnp.float64(-1.0), out=x.one_grid)
    fnp.add(x.one_grid, fnp.float64(1.0), out=x.one_grid)
    fnp.multiply(x.alpha_left, x.alpha_left, out=x.temp1)
    fnp.multiply(x.alpha_right, x.alpha_right, out=x.temp2)
    fnp.multiply(x.r_grid, x.alpha_left[:, :, None], out=x.quadratic_grid)
    fnp.multiply(x.quadratic_grid, x.alpha_right[:, :, None], out=x.quadratic_grid)
    fnp.multiply(x.quadratic_grid, fnp.float64(-2.0), out=x.quadratic_grid)
    fnp.add(x.quadratic_grid, x.temp1[:, :, None], out=x.quadratic_grid)
    fnp.add(x.quadratic_grid, x.temp2[:, :, None], out=x.quadratic_grid)
    fnp.multiply(x.one_grid, fnp.float64(2.0), out=x.temp_grid)
    fnp.divide(x.quadratic_grid, x.temp_grid, out=x.quadratic_grid)
    fnp.multiply(x.quadratic_grid, fnp.float64(-1.0), out=x.quadratic_grid)
    fnp.exp(x.quadratic_grid, out=x.quadratic_grid)
    fnp.sqrt(x.one_grid, out=x.temp_grid)
    fnp.divide(x.quadratic_grid, x.temp_grid, out=x.quadratic_grid)
    fnp.multiply(x.quadratic_grid, fnp.float64(core.INV_TWO_PI), out=x.quadratic_grid)
    fnp.multiply(
        x.quadratic_grid,
        core._SIMPSON_WEIGHTS[None, None, :],
        out=x.temp_grid,
    )
    fnp.sum(x.temp_grid, axis=2, out=x.phi2)
    fnp.multiply(x.phi2, c["pair_rho"][None, :], out=x.phi2)
    fnp.divide(x.phi2, fnp.float64(3.0 * core.SIMPSON_PANELS), out=x.phi2)
    fnp.multiply(Phi_left, Phi_right, out=x.temp1)
    fnp.add(x.phi2, x.temp1, out=x.phi2)

    # Price derivatives and the same bivariate raw reconstruction as M216.
    fnp.multiply(phi_left, Phi_t_left, out=x.temp1)
    fnp.multiply(phi_right, Phi_t_right, out=x.temp2)
    fnp.multiply(x.alpha_left, x.alpha_left, out=x.joint)
    fnp.multiply(c["pair_rho"][None, :], x.alpha_left, out=x.temp3)
    fnp.multiply(x.temp3, x.alpha_right, out=x.temp3)
    fnp.multiply(x.temp3, fnp.float64(-2.0), out=x.temp3)
    fnp.add(x.joint, x.temp3, out=x.joint)
    fnp.multiply(x.alpha_right, x.alpha_right, out=x.temp3)
    fnp.add(x.joint, x.temp3, out=x.joint)
    fnp.multiply(x.offset, fnp.float64(2.0), out=x.radius)  # B scratch
    fnp.divide(x.joint, x.radius[None, :], out=x.joint)
    fnp.multiply(x.joint, fnp.float64(-1.0), out=x.joint)
    fnp.exp(x.joint, out=x.joint)
    fnp.divide(x.joint, x.q[None, :], out=x.joint)
    fnp.multiply(x.joint, fnp.float64(core.INV_TWO_PI), out=x.joint)

    fnp.multiply(x.alpha_right, x.temp1, out=x.standard_pair)
    fnp.multiply(x.alpha_left, x.temp2, out=x.temp3)
    fnp.add(x.standard_pair, x.temp3, out=x.standard_pair)
    fnp.multiply(x.offset[None, :], x.joint, out=x.temp3)
    fnp.add(x.standard_pair, x.temp3, out=x.standard_pair)
    fnp.multiply(x.alpha_left, x.alpha_right, out=x.temp3)
    fnp.add(x.temp3, c["pair_rho"][None, :], out=x.temp3)
    fnp.multiply(x.temp3, x.phi2, out=x.temp3)
    fnp.add(x.standard_pair, x.temp3, out=x.standard_pair)
    fnp.multiply(x.standard_pair, c["pair_sigma_left"][None, :], out=x.raw_pair)
    fnp.multiply(x.raw_pair, c["pair_sigma_right"][None, :], out=x.raw_pair)

    fnp.multiply(x.alpha_left, Phi_left, out=x.unary_left)
    fnp.add(x.unary_left, phi_left, out=x.unary_left)
    fnp.multiply(x.unary_left, c["pair_sigma_left"][None, :], out=x.unary_left)
    fnp.multiply(x.alpha_right, Phi_right, out=x.unary_right)
    fnp.add(x.unary_right, phi_right, out=x.unary_right)
    fnp.multiply(x.unary_right, c["pair_sigma_right"][None, :], out=x.unary_right)
    fnp.multiply(c["activation_mean_left"][None, :], x.unary_right, out=x.centered_pair)
    fnp.subtract(x.raw_pair, x.centered_pair, out=x.centered_pair)
    fnp.multiply(c["activation_mean_right"][None, :], x.unary_left, out=x.temp1)
    fnp.subtract(x.centered_pair, x.temp1, out=x.centered_pair)
    fnp.multiply(c["activation_mean_left"], c["activation_mean_right"], out=x.offset)
    fnp.add(x.centered_pair, x.offset[None, :], out=x.centered_pair)

    fnp.multiply(c["repeated_sigma"][None, :], x.sign_g, out=x.repeated_preactivation)
    fnp.add(x.repeated_preactivation, c["repeated_mean"][None, :], out=x.repeated_preactivation)
    fnp.maximum(x.repeated_preactivation, fnp.float64(0.0), out=x.repeated_centered)
    fnp.subtract(x.repeated_centered, c["repeated_activation_mean"][None, :], out=x.repeated_centered)
    fnp.multiply(x.repeated_centered, x.repeated_centered, out=x.central)
    fnp.multiply(x.central, x.centered_pair, out=x.central)
    fnp.multiply(c["activation_vii"], c["activation_vjk"], out=x.offset)
    fnp.multiply(c["activation_vij"], c["activation_vik"], out=x.value)
    fnp.multiply(x.value, fnp.float64(2.0), out=x.value)
    fnp.add(x.offset, x.value, out=x.offset)
    fnp.add(x.offset, c["tree"], out=x.offset)
    fnp.subtract(x.central, x.offset[None, :], out=x.signed)
    fnp.sum(x.signed, axis=0, out=x.value)
    fnp.multiply(x.value, fnp.float64(0.5), out=x.value)
    fnp.abs(x.value, out=x.radius)
    fnp.add(x.radius, fnp.float64(1.0), out=x.radius)
    fnp.multiply(x.radius, fnp.float64(core.EVENT_RADIUS_FACTOR), out=x.radius)

    # Charged chart guard, with caller-visible fallback mask.
    fnp.abs(x.alpha_left, out=x.temp1)
    fnp.abs(x.alpha_right, out=x.temp2)
    fnp.maximum(x.temp1, x.temp2, out=x.temp1)
    fnp.max(x.temp1, axis=0, out=x.max_alpha)
    fnp.abs(x.t_left, out=x.temp1)
    fnp.abs(x.t_right, out=x.temp2)
    fnp.maximum(x.temp1, x.temp2, out=x.temp1)
    fnp.max(x.temp1, axis=0, out=x.max_t)
    fnp.abs(x.repeated_centered, out=x.temp1)
    fnp.max(x.temp1, axis=0, out=x.max_repeated)
    fnp.abs(c["pair_rho"], out=x.offset)
    fnp.less_equal(x.offset, fnp.float64(core.ABS_RHO_MAX), out=x.chart_ok)
    for array, bound, relation in (
        (x.max_alpha, core.ABS_STANDARD_MAX, "le"),
        (x.max_t, core.ABS_STANDARD_MAX, "le"),
        (c["pair_sigma_left"], core.SIGMA_MIN, "ge"),
        (c["pair_sigma_left"], core.SIGMA_MAX, "le"),
        (c["pair_sigma_right"], core.SIGMA_MIN, "ge"),
        (c["pair_sigma_right"], core.SIGMA_MAX, "le"),
        (x.max_repeated, core.REPEATED_CENTER_MAX, "le"),
    ):
        if relation == "le":
            fnp.less_equal(array, fnp.float64(bound), out=x.bool_temp)
        else:
            fnp.greater_equal(array, fnp.float64(bound), out=x.bool_temp)
        fnp.logical_and(x.chart_ok, x.bool_temp, out=x.chart_ok)
    fnp.isfinite(x.value, out=x.bool_temp)
    fnp.logical_and(x.chart_ok, x.bool_temp, out=x.chart_ok)
    return x.value, x.radius, x.chart_ok


def generated_native_batch(seed: int) -> core.PackedBatch:
    rng = np.random.default_rng(int(seed))
    batches = []
    for layer in range(1, 32):
        local = core._m216.frozen_local_state(7, 221730000 + layer)
        owners = core._m216.strict_physical_owners(7)
        g = rng.normal(size=128)
        batches.append(
            core._pack_rows(
                local,
                ((owners[slot % len(owners)], float(g[slot])) for slot in range(128)),
            )
        )
    return core.concatenate_batches(batches)


def run_billed_batch(packed: core.PackedBatch) -> dict[str, object]:
    budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=120.0)
    failure = None
    allocation = None
    output = None
    started = time.perf_counter()
    try:
        with budget:
            staged = allocate_staged(packed.size)
            workspace = allocate_workspace(packed.size)
            allocation = allocation_ledger(staged, workspace)
            stage_inputs(packed, staged)
            output = compile_batch(staged, workspace)
        value = np.asarray(output[0]).copy()
        radius = np.asarray(output[1]).copy()
        chart_ok = np.asarray(output[2]).copy()
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        value = np.full(packed.size, np.nan)
        radius = np.full(packed.size, np.nan)
        chart_ok = np.zeros(packed.size, dtype=bool)
    wall = time.perf_counter() - started
    summary = budget.summary_dict()
    return {
        "failure": failure,
        "event_count": packed.size,
        "billed_flops": int(budget.flops_used),
        "residual_wall_s": float(budget.residual_wall_time_s or 0.0),
        "wall_s": wall,
        "operations": summary.get("operations", {}),
        "allocation": allocation,
        "value": value,
        "radius": radius,
        "chart_ok": chart_ok,
        "fallback_count": int(np.count_nonzero(~chart_ok)),
        "rss_bytes": int(core._m216._rss_bytes()),
    }


__all__ = [
    "allocate_staged",
    "allocate_workspace",
    "allocation_ledger",
    "compile_batch",
    "generated_native_batch",
    "run_billed_batch",
    "stage_inputs",
]
