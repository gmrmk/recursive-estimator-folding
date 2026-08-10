"""M226 execution-only topology for M224's frozen normalized atom."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
M224_DIR = EXPERIMENTS / "m224_gauge_invariant_rho08_chart"
if str(M224_DIR) not in sys.path:
    sys.path.insert(0, str(M224_DIR))

import m224_gauge_invariant_rho08_chart as core  # noqa: E402


MUTATION = "M226"
M224_CODE_SHA256 = "6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B"
FLOAT64_UNITS_PER_EVENT = 268
BOOL_UNITS_PER_EVENT = 2
BYTES_PER_EVENT = 2146
PREDICTED_BILL_PER_EVENT = 5467


@dataclass(frozen=True)
class BoundInputs:
    columns: dict[str, np.ndarray]
    event_count: int


def prepare_inputs(packed: core.PackedBatch) -> BoundInputs:
    marginal_left, marginal_right = core._marginal_singleton_sigmas(packed)
    names = (
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
    columns = {
        name: np.asarray(getattr(packed, name), dtype=np.float64)
        for name in names
    }
    columns["marginal_sigma_left"] = marginal_left
    columns["marginal_sigma_right"] = marginal_right
    return BoundInputs(columns=columns, event_count=packed.size)


class PersistentKernel:
    """Two-slab persistent workspace; all views are hoisted in setup."""

    def __init__(self, event_count: int):
        self.event_count = int(event_count)
        if self.event_count <= 0:
            raise ValueError("positive event count required")
        n = self.event_count
        self._float_slab = fnp.empty(FLOAT64_UNITS_PER_EVENT * n, dtype=fnp.float64)
        self._bool_slab = fnp.empty(BOOL_UNITS_PER_EVENT * n, dtype=fnp.bool_)
        self._cursor = 0

        self.phi_args = self._take((8, n))
        self.phi_x = self._take((8, n))
        self.phi_y = self._take((8, n))
        self.phi_acc = self._take((8, n))
        self.phi_out = self._take((8, n))
        self.univariate_density = self._take((4, n))
        self.r_grid = self._take((2, n, core._m221.SIMPSON_NODES))
        self.one_grid = self._take((2, n, core._m221.SIMPSON_NODES))
        self.quadratic_grid = self._take((2, n, core._m221.SIMPSON_NODES))
        self.phi2 = self._take((2, n))
        self.joint = self._take((2, n))
        self.standard_pair = self._take((2, n))
        self.unary_left = self._take((2, n))
        self.unary_right = self._take((2, n))
        self.centered_pair = self._take((2, n))
        self.repeated_standardized = self._take((2, n))
        self.temp1 = self._take((2, n))
        self.temp2 = self._take((2, n))
        self.temp3 = self._take((2, n))
        self.scratch0 = self._take((n,))
        self.scratch1 = self._take((n,))
        self.value = self._take((n,))
        self.radius = self._take((n,))
        self.max_metric = self._take((n,))
        self.ratio = self._take((n,))
        if self._cursor != self._float_slab.size:
            raise RuntimeError("M226 float slab ledger mismatch")

        self.chart_ok = self._bool_slab[:n]
        self.bool_temp = self._bool_slab[n:]

        # Setup-only views; no runtime reshape operation exists.
        self.alpha_left = self.phi_args[0:2]
        self.alpha_right = self.phi_args[2:4]
        self.t_left = self.phi_args[4:6]
        self.t_right = self.phi_args[6:8]
        self.phi2_column = self.phi2.reshape((2 * n, 1))
        self.quadratic_grid_flat = self.quadratic_grid.reshape(
            (2 * n, core._m221.SIMPSON_NODES)
        )
        self.simpson_fractions_two_sign = np.broadcast_to(
            core._m221._SIMPSON_FRACTIONS[None, None, :],
            (2, 1, core._m221.SIMPSON_NODES),
        )
        self._columns: dict[str, np.ndarray] | None = None

    def _take(self, shape: tuple[int, ...]) -> np.ndarray:
        size = math.prod(shape)
        start = self._cursor
        stop = start + size
        self._cursor = stop
        return self._float_slab[start:stop].reshape(shape)

    def allocation_ledger(self) -> dict[str, int]:
        return {
            "empty_calls": 2,
            "float64_elements": int(self._float_slab.size),
            "bool_elements": int(self._bool_slab.size),
            "float64_bytes": int(self._float_slab.nbytes),
            "bool_bytes": int(self._bool_slab.nbytes),
            "total_bytes": int(self._float_slab.nbytes + self._bool_slab.nbytes),
            "runtime_user_allocation_bytes": 0,
        }

    def bind(self, bound: BoundInputs) -> None:
        if bound.event_count != self.event_count:
            raise ValueError("bound input size does not match persistent kernel")
        if len(bound.columns) != 20:
            raise ValueError("M226 requires exactly 20 direct-bound columns")
        for name, column in bound.columns.items():
            if np.asarray(column).shape != (self.event_count,):
                raise ValueError(f"M226 column {name} has wrong shape")
        self._columns = bound.columns

    def _phi16_combined(self) -> None:
        coefficients = core._m221._ERF_COEFFICIENTS
        fnp.multiply(
            self.phi_args,
            fnp.float64(core._m221.INV_SQRT_TWO),
            out=self.phi_x,
        )
        fnp.multiply(self.phi_x, self.phi_x, out=self.phi_y)
        fnp.multiply(
            self.phi_y,
            fnp.float64(coefficients[-1]),
            out=self.phi_acc,
        )
        fnp.add(
            self.phi_acc,
            fnp.float64(coefficients[-2]),
            out=self.phi_acc,
        )
        for coefficient in coefficients[-3::-1]:
            fnp.multiply(self.phi_acc, self.phi_y, out=self.phi_acc)
            fnp.add(self.phi_acc, fnp.float64(coefficient), out=self.phi_acc)
        fnp.multiply(self.phi_acc, self.phi_x, out=self.phi_acc)
        fnp.multiply(self.phi_acc, fnp.float64(0.5), out=self.phi_out)
        fnp.add(self.phi_out, fnp.float64(0.5), out=self.phi_out)

    def compile(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self._columns is None:
            raise RuntimeError("M226 kernel is not bound")
        c = self._columns
        a_left = self.alpha_left
        a_right = self.alpha_right
        t_left = self.t_left
        t_right = self.t_right

        # Conditional standardized means for +g and -g, directly in Phi slab.
        fnp.multiply(c["pair_slope_left"], c["g"], out=a_left[0])
        fnp.multiply(a_left[0], fnp.float64(-1.0), out=a_left[1])
        fnp.add(a_left, c["pair_base_left"][None, :], out=a_left)
        fnp.divide(a_left, c["pair_sigma_left"][None, :], out=a_left)
        fnp.multiply(c["pair_slope_right"], c["g"], out=a_right[0])
        fnp.multiply(a_right[0], fnp.float64(-1.0), out=a_right[1])
        fnp.add(a_right, c["pair_base_right"][None, :], out=a_right)
        fnp.divide(a_right, c["pair_sigma_right"][None, :], out=a_right)

        fnp.multiply(c["pair_rho"], c["pair_rho"], out=self.scratch0)
        fnp.multiply(self.scratch0, fnp.float64(-1.0), out=self.scratch0)
        fnp.add(self.scratch0, fnp.float64(1.0), out=self.scratch0)
        fnp.sqrt(self.scratch0, out=self.scratch1)
        fnp.multiply(c["pair_rho"][None, :], a_left, out=t_left)
        fnp.subtract(a_right, t_left, out=t_left)
        fnp.divide(t_left, self.scratch1[None, :], out=t_left)
        fnp.multiply(c["pair_rho"][None, :], a_right, out=t_right)
        fnp.subtract(a_left, t_right, out=t_right)
        fnp.divide(t_right, self.scratch1[None, :], out=t_right)

        self._phi16_combined()
        Phi_left = self.phi_out[0:2]
        Phi_right = self.phi_out[2:4]
        Phi_t_left = self.phi_out[4:6]
        Phi_t_right = self.phi_out[6:8]

        fnp.multiply(self.phi_args[0:4], self.phi_args[0:4], out=self.univariate_density)
        fnp.multiply(
            self.univariate_density,
            fnp.float64(-0.5),
            out=self.univariate_density,
        )
        fnp.exp(self.univariate_density, out=self.univariate_density)
        fnp.multiply(
            self.univariate_density,
            fnp.float64(core._m221.INV_SQRT_TWO_PI),
            out=self.univariate_density,
        )
        phi_left = self.univariate_density[0:2]
        phi_right = self.univariate_density[2:4]

        # Same 33 Simpson nodes; weighted reduction is one billed matmul.
        fnp.multiply(
            c["pair_rho"][None, :, None],
            self.simpson_fractions_two_sign,
            out=self.r_grid,
        )
        fnp.multiply(self.r_grid, self.r_grid, out=self.one_grid)
        fnp.multiply(self.one_grid, fnp.float64(-1.0), out=self.one_grid)
        fnp.add(self.one_grid, fnp.float64(1.0), out=self.one_grid)
        fnp.multiply(a_left, a_left, out=self.temp1)
        fnp.multiply(a_right, a_right, out=self.temp2)
        fnp.multiply(
            self.r_grid,
            a_left[:, :, None],
            out=self.quadratic_grid,
        )
        fnp.multiply(
            self.quadratic_grid,
            a_right[:, :, None],
            out=self.quadratic_grid,
        )
        fnp.multiply(
            self.quadratic_grid,
            fnp.float64(-2.0),
            out=self.quadratic_grid,
        )
        fnp.add(
            self.quadratic_grid,
            self.temp1[:, :, None],
            out=self.quadratic_grid,
        )
        fnp.add(
            self.quadratic_grid,
            self.temp2[:, :, None],
            out=self.quadratic_grid,
        )
        fnp.multiply(self.one_grid, fnp.float64(2.0), out=self.r_grid)
        fnp.divide(self.quadratic_grid, self.r_grid, out=self.quadratic_grid)
        fnp.multiply(
            self.quadratic_grid,
            fnp.float64(-1.0),
            out=self.quadratic_grid,
        )
        fnp.exp(self.quadratic_grid, out=self.quadratic_grid)
        fnp.sqrt(self.one_grid, out=self.one_grid)
        fnp.divide(self.quadratic_grid, self.one_grid, out=self.quadratic_grid)
        fnp.multiply(
            self.quadratic_grid,
            fnp.float64(core._m221.INV_TWO_PI),
            out=self.quadratic_grid,
        )
        fnp.matmul(
            self.quadratic_grid_flat,
            core._m221._SIMPSON_WEIGHTS[:, None],
            out=self.phi2_column,
        )
        fnp.multiply(self.phi2, c["pair_rho"][None, :], out=self.phi2)
        fnp.divide(
            self.phi2,
            fnp.float64(3.0 * core._m221.SIMPSON_PANELS),
            out=self.phi2,
        )
        fnp.multiply(Phi_left, Phi_right, out=self.temp1)
        fnp.add(self.phi2, self.temp1, out=self.phi2)

        # Price derivatives and dimensionless centered pair from frozen M224.
        fnp.multiply(phi_left, Phi_t_left, out=self.temp1)
        fnp.multiply(phi_right, Phi_t_right, out=self.temp2)
        fnp.multiply(a_left, a_left, out=self.joint)
        fnp.multiply(c["pair_rho"][None, :], a_left, out=self.temp3)
        fnp.multiply(self.temp3, a_right, out=self.temp3)
        fnp.multiply(self.temp3, fnp.float64(-2.0), out=self.temp3)
        fnp.add(self.joint, self.temp3, out=self.joint)
        fnp.multiply(a_right, a_right, out=self.temp3)
        fnp.add(self.joint, self.temp3, out=self.joint)
        fnp.multiply(self.scratch0, fnp.float64(2.0), out=self.ratio)
        fnp.divide(self.joint, self.ratio[None, :], out=self.joint)
        fnp.multiply(self.joint, fnp.float64(-1.0), out=self.joint)
        fnp.exp(self.joint, out=self.joint)
        fnp.divide(self.joint, self.scratch1[None, :], out=self.joint)
        fnp.multiply(
            self.joint,
            fnp.float64(core._m221.INV_TWO_PI),
            out=self.joint,
        )

        fnp.multiply(a_right, self.temp1, out=self.standard_pair)
        fnp.multiply(a_left, self.temp2, out=self.temp3)
        fnp.add(self.standard_pair, self.temp3, out=self.standard_pair)
        fnp.multiply(self.scratch0[None, :], self.joint, out=self.temp3)
        fnp.add(self.standard_pair, self.temp3, out=self.standard_pair)
        fnp.multiply(a_left, a_right, out=self.temp3)
        fnp.add(self.temp3, c["pair_rho"][None, :], out=self.temp3)
        fnp.multiply(self.temp3, self.phi2, out=self.temp3)
        fnp.add(self.standard_pair, self.temp3, out=self.standard_pair)

        fnp.multiply(a_left, Phi_left, out=self.unary_left)
        fnp.add(self.unary_left, phi_left, out=self.unary_left)
        fnp.multiply(a_right, Phi_right, out=self.unary_right)
        fnp.add(self.unary_right, phi_right, out=self.unary_right)
        fnp.divide(
            c["activation_mean_left"],
            c["pair_sigma_left"],
            out=self.scratch0,
        )
        fnp.divide(
            c["activation_mean_right"],
            c["pair_sigma_right"],
            out=self.scratch1,
        )
        fnp.multiply(
            self.scratch0[None, :],
            self.unary_right,
            out=self.centered_pair,
        )
        fnp.subtract(
            self.standard_pair,
            self.centered_pair,
            out=self.centered_pair,
        )
        fnp.multiply(
            self.scratch1[None, :],
            self.unary_left,
            out=self.temp1,
        )
        fnp.subtract(self.centered_pair, self.temp1, out=self.centered_pair)
        fnp.multiply(self.scratch0, self.scratch1, out=self.ratio)
        fnp.add(self.centered_pair, self.ratio[None, :], out=self.centered_pair)

        # Gauge-invariant repeated residual, then apply its/rho chart guards.
        fnp.multiply(
            c["repeated_sigma"],
            c["g"],
            out=self.repeated_standardized[0],
        )
        fnp.multiply(
            self.repeated_standardized[0],
            fnp.float64(-1.0),
            out=self.repeated_standardized[1],
        )
        fnp.add(
            self.repeated_standardized,
            c["repeated_mean"][None, :],
            out=self.repeated_standardized,
        )
        fnp.maximum(
            self.repeated_standardized,
            fnp.float64(0.0),
            out=self.repeated_standardized,
        )
        fnp.subtract(
            self.repeated_standardized,
            c["repeated_activation_mean"][None, :],
            out=self.repeated_standardized,
        )
        fnp.divide(
            self.repeated_standardized,
            c["repeated_sigma"][None, :],
            out=self.repeated_standardized,
        )
        fnp.abs(self.repeated_standardized, out=self.temp1)
        fnp.maximum(self.temp1[0], self.temp1[1], out=self.max_metric)
        fnp.less_equal(
            self.max_metric,
            fnp.float64(core.STANDARDIZED_REPEATED_MAX),
            out=self.bool_temp,
        )
        fnp.abs(c["pair_rho"], out=self.ratio)
        fnp.less_equal(
            self.ratio,
            fnp.float64(core.ABS_RHO_MAX),
            out=self.chart_ok,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)

        # Antithetic central term; no reduction call.
        fnp.multiply(
            self.repeated_standardized,
            self.repeated_standardized,
            out=self.repeated_standardized,
        )
        fnp.multiply(
            self.repeated_standardized,
            self.centered_pair,
            out=self.repeated_standardized,
        )
        fnp.add(
            self.repeated_standardized[0],
            self.repeated_standardized[1],
            out=self.value,
        )
        fnp.multiply(self.value, fnp.float64(0.5), out=self.value)
        fnp.multiply(c["repeated_sigma"], c["repeated_sigma"], out=self.scratch0)
        fnp.multiply(self.scratch0, c["pair_sigma_left"], out=self.scratch0)
        fnp.multiply(self.scratch0, c["pair_sigma_right"], out=self.scratch0)
        fnp.multiply(self.value, self.scratch0, out=self.value)
        fnp.multiply(c["activation_vii"], c["activation_vjk"], out=self.scratch1)
        fnp.multiply(c["activation_vij"], c["activation_vik"], out=self.ratio)
        fnp.multiply(self.ratio, fnp.float64(2.0), out=self.ratio)
        fnp.add(self.scratch1, self.ratio, out=self.scratch1)
        fnp.add(self.scratch1, c["tree"], out=self.scratch1)
        fnp.subtract(self.value, self.scratch1, out=self.value)
        fnp.abs(self.value, out=self.radius)
        fnp.add(self.radius, fnp.float64(1.0), out=self.radius)
        fnp.multiply(
            self.radius,
            fnp.float64(core.EVENT_RADIUS_FACTOR),
            out=self.radius,
        )

        # Remaining chart guards; two-sign maxima are elementwise maximum.
        fnp.abs(a_left, out=self.temp1)
        fnp.abs(a_right, out=self.temp2)
        fnp.maximum(self.temp1, self.temp2, out=self.temp1)
        fnp.maximum(self.temp1[0], self.temp1[1], out=self.max_metric)
        fnp.less_equal(
            self.max_metric,
            fnp.float64(core.ABS_STANDARD_MAX),
            out=self.bool_temp,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        fnp.abs(t_left, out=self.temp1)
        fnp.abs(t_right, out=self.temp2)
        fnp.maximum(self.temp1, self.temp2, out=self.temp1)
        fnp.maximum(self.temp1[0], self.temp1[1], out=self.max_metric)
        fnp.less_equal(
            self.max_metric,
            fnp.float64(core.ABS_STANDARD_MAX),
            out=self.bool_temp,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)

        fnp.divide(
            c["pair_sigma_left"],
            c["marginal_sigma_left"],
            out=self.ratio,
        )
        fnp.greater_equal(
            self.ratio,
            fnp.float64(core.SCALE_RATIO_MIN),
            out=self.bool_temp,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        fnp.less_equal(
            self.ratio,
            fnp.float64(core.SCALE_RATIO_MAX),
            out=self.bool_temp,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        fnp.divide(
            c["pair_sigma_right"],
            c["marginal_sigma_right"],
            out=self.ratio,
        )
        fnp.greater_equal(
            self.ratio,
            fnp.float64(core.SCALE_RATIO_MIN),
            out=self.bool_temp,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        fnp.less_equal(
            self.ratio,
            fnp.float64(core.SCALE_RATIO_MAX),
            out=self.bool_temp,
        )
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        fnp.greater(self.scratch0, fnp.float64(0.0), out=self.bool_temp)
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        fnp.isfinite(self.value, out=self.bool_temp)
        fnp.logical_and(self.chart_ok, self.bool_temp, out=self.chart_ok)
        return self.value, self.radius, self.chart_ok


def generated_native_batch(seed: int) -> core.PackedBatch:
    return core.generated_native_batch(seed)


def run_billed_batch(
    packed: core.PackedBatch,
    kernel: PersistentKernel,
) -> dict[str, object]:
    bound = prepare_inputs(packed)
    kernel.bind(bound)
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
    if output is None:
        value = np.full(packed.size, np.nan)
        radius = np.full(packed.size, np.nan)
        chart_ok = np.zeros(packed.size, dtype=bool)
    else:
        value = np.asarray(output[0])
        radius = np.asarray(output[1])
        chart_ok = np.asarray(output[2])
    summary = budget.summary_dict()
    return {
        "failure": failure,
        "event_count": packed.size,
        "billed_flops": int(budget.flops_used),
        "residual_wall_s": float(budget.residual_wall_time_s or 0.0),
        "wall_s": wall,
        "operations": summary.get("operations", {}),
        "allocation": kernel.allocation_ledger(),
        "value": value,
        "radius": radius,
        "chart_ok": chart_ok,
        "fallback_count": int(np.count_nonzero(~chart_ok)),
        "rss_bytes": int(core._m221._m216._rss_bytes()),
    }


__all__ = [
    "BoundInputs",
    "M224_CODE_SHA256",
    "PersistentKernel",
    "core",
    "generated_native_batch",
    "prepare_inputs",
    "run_billed_batch",
]
