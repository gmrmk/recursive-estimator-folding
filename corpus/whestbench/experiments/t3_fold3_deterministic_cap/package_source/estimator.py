"""T3: deterministic per-network sample cap over the frozen fold3-39936 lineage.

Mechanism (T3_PREDECLARATION.md):
  1. Before the main sampling run, replay the parent's active-set evolution on
     the pilot block only (the first ``fold_pilot_base`` frame rows and their
     antipodal images) -- exactly the rows the parent's own pilot rescues and
     fold refinements consult, so the realized partitions equal the parent
     run's for every n_eff >= fold_pilot_base.
  2. From those realized set sizes, evaluate a billed-FLOP cost model
     C_pred(n) for the whole predict() (cap simulation + analytic pass + main
     run), where the cap simulation and the analytic diagonal pass are
     OBSERVED via live budget-tally reads and only the parent's main run is
     modeled op-by-op.
  3. Choose n_eff = the largest multiple of 256 with n_eff <= 39,936 and
     C_pred(n_eff) <= CAP = 244.8e9 (= 0.9 * 272e9).
  4. Slice the frozen frame tensor to n_eff rows, shadow ``n_base`` on the
     instance, delegate to the UNMODIFIED parent predict(), restore in a
     ``finally`` block.

Legality note: the cap simulation is mlp-dependent arithmetic, so it runs
through ``flopscope.numpy`` and is billed like any other predict work; its
observed cost is part of C_pred's overhead term.  The cost-model evaluation
itself is plain Python integer arithmetic on set SIZES (control flow, not
array math) and bills nothing, matching the precedent of the two-axis
``cost_model.py`` bill functions.

Floor note (documented deviation candidate): n_eff is never taken below
1,024 (= fold_pilot_base).  Below that the parent would shrink its fold
pilot (``pilot_n = min(fold_pilot_base, n_base)``), the realized partitions
would diverge from the pilot-identical simulation, and the cost model's
premise would be void.  The predeclaration's "pilot-identical simulation"
requires n_eff >= fold_pilot_base; for width-256 depth-32 networks the
floor is unreachable anyway (C_pred(1024) is a few percent of CAP).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp

# Package-local imports: all six modules ship flat in the submission folder.
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from base_estimator import _diagonal_gaussian_pass  # noqa: E402
from fold_estimator import _initial_regimes, _refine_dead, _refine_on  # noqa: E402
from estimator_n39936 import Estimator as _FrozenN39936  # noqa: E402


# ---------------------------------------------------------------------------
# Billed-FLOP model of the parent predict(), minus the analytic diagonal pass
# (which is observed, not modeled).  Per-op bills verified empirically against
# flopscope on the pinned v0.14 env (see T3_BUILD_NOTES.md):
#   matmul (m,k)@(k,n) float32:  2mkn - mn
#   pointwise unary/binary:      1 per element (float32 rate 1.0)
#   mean axis=0 of (m,n):        m*n        sum/max/min axis=0: (m-1)*n
#   concatenate:                 1 per output element (x2 for int64)
#   fancy-index gather:          4 per output element (int64 assumed 8)
#   sort / argsort:              8 * n * ceil(log2 n)
#   flatnonzero:                 1 per input element
#   arange:                      4 per element
#   stack:                       1 per output element
#   sqrt: 2/elem   exp: 16/elem   x**2: 16/elem
# ---------------------------------------------------------------------------


def _mm(m: int, k: int, n: int) -> int:
    """Billed FLOPs of a float32 matmul (m,k)@(k,n); (1,...) covers vec@mat."""
    if m <= 0 or k <= 0 or n <= 0:
        return 1
    return 2 * m * k * n - m * n


def _sort_bill(m: int) -> int:
    if m < 2:
        return 8
    return 8 * m * max(1, math.ceil(math.log2(m)))


def _refine_bill(size: int, moved: int, rows: int) -> int:
    """_refine_dead/_refine_on on a (rows, size) pilot preactivation.

    max/min reduction + compare + flatnonzero + int gather of ``moved``
    + invert + flatnonzero + int gather of ``size - moved``.
    """
    return (
        (rows - 1) * size + size + size + 8 * moved + size + size
        + 8 * (size - moved)
    )


def _pre31_bill(a28, o30, k30, cols, rows, w):
    """One call of the parent's pre31(): folded30_to31 + two matmuls + add."""
    if cols <= 0:
        return 0
    return (
        4 * a28 * o30 + 4 * o30 * w + 4 * o30 * cols   # weight30/31 gathers
        + _mm(a28, o30, cols)                          # folded30_to31
        + _mm(rows, a28, cols)                         # left @ folded
        + 4 * k30 * w + 4 * k30 * cols                 # weight31[kink30][:,c]
        + _mm(rows, k30, cols)                         # middle @ ...
        + rows * cols                                  # add
    )


def _pre32_bill(a28, o31, k30, k31, cols, rows, w):
    """One call of the parent's pre32(): three bases, two folded inners."""
    if cols <= 0:
        return 0
    return (
        2 * (4 * o31 * w + 4 * o31 * cols)             # weight32[on31][:,c] x2
        + 4 * k31 * w + 4 * k31 * cols                 # weight32[kink31][:,c]
        + _mm(a28, o31, cols) + _mm(rows, a28, cols)   # term 1
        + _mm(k30, o31, cols) + _mm(rows, k30, cols)   # term 2
        + _mm(rows, k31, cols)                         # term 3
        + 2 * rows * cols                              # two adds
    )


def predict_main_bill(n, width, depth, pilot, fold_pilot, loop_dims, fold):
    """Billed FLOPs of the parent fold3 predict() at sample count ``n``,
    excluding its _diagonal_gaussian_pass call (observed separately).

    ``loop_dims``: per pruning layer (a_prev, cold, rescued, a_next).
    ``fold``: realized fold-layer partition sizes (see _simulate_cap_sets).
    Mirrors fold3_estimator.Estimator.predict with radial_conditioning=True
    (final_weights is None) op by op.
    """
    w = width
    big = 2 * n            # antipodal sample rows
    p2 = 2 * pilot         # loop pilot rows (512)
    P2 = 2 * fold_pilot    # fold pilot rows (2048)
    total = 0

    # first_pre = z @ W0 ; x = concat(relu(first_pre), relu(-first_pre))
    total += _mm(n, w, w)
    total += 3 * n * w             # relu, negate, relu
    total += big * w               # concatenate
    # sigma0, exact_first_mean
    total += w * w + (w - 1) * w + 2 * w      # W0*W0, sum axis=0, sqrt
    total += 3 + w                            # 2*pi, scalar sqrt, divide
    # first moment / variance residuals
    total += big * w + w                      # mean(x), subtract
    total += big * w + big * w + 6 * w        # x*x, mean, scalar chain
    total += 4 * w                            # arange(width)

    # pruning loop, layers 1..depth-4
    for a_prev, cold, rescued, a_next in loop_dims:
        total += 4 * w                        # two compares + two flatnonzero
        if cold > 0:
            total += p2 * a_prev              # pilot_x concatenate
            total += 4 * a_prev * w + 4 * a_prev * cold      # weight gathers
            total += _mm(p2, a_prev, cold)
            total += (p2 - 1) * cold + cold                  # max, > 0
            total += cold + 8 * rescued                      # fnz + gather
            total += 2 * a_next + _sort_bill(a_next)         # concat + sort
        total += 4 * a_prev * w + 4 * a_prev * a_next        # weight gathers
        total += _mm(big, a_prev, a_next)
        total += big * a_next                                # relu

    a28 = fold["a28"]
    total += P2 * a28                          # pilot_x29 concatenate

    # ---- layer30 ----
    total += 8 * w                             # _initial_regimes
    total += 4 * a28 * w                       # weight30 = W[active, :]
    k_run = fold["k30_init"]
    if fold["d30_init"] > 0:
        total += 4 * a28 * fold["d30_init"] + _mm(P2, a28, fold["d30_init"])
        total += _refine_bill(fold["d30_init"], fold["r30"], P2)
        k_run += fold["r30"]
        total += 2 * k_run                     # int concatenate
    if fold["o30_init"] > 0:
        total += 4 * a28 * fold["o30_init"] + _mm(P2, a28, fold["o30_init"])
        total += _refine_bill(fold["o30_init"], fold["dm30"], P2)
        k_run += fold["dm30"]
        total += 2 * k_run
    k30 = fold["k30"]
    o30 = fold["o30"]
    total += _sort_bill(k30)
    total += 4 * a28 * k30 + _mm(big, a28, k30) + big * k30  # x30_kink
    total += P2 * k30                          # pilot_x30_kink concatenate

    # ---- layer31 ----
    total += 8 * w
    k_run = fold["k31_init"]
    if fold["d31_init"] > 0:
        total += _pre31_bill(a28, o30, k30, fold["d31_init"], P2, w)
        total += _refine_bill(fold["d31_init"], fold["r31"], P2)
        k_run += fold["r31"]
        total += 2 * k_run
    if fold["o31_init"] > 0:
        total += _pre31_bill(a28, o30, k30, fold["o31_init"], P2, w)
        total += _refine_bill(fold["o31_init"], fold["dm31"], P2)
        k_run += fold["dm31"]
        total += 2 * k_run
    k31 = fold["k31"]
    o31 = fold["o31"]
    total += _sort_bill(k31)
    total += _pre31_bill(a28, o30, k30, k31, big, w) + big * k31   # x31_kink
    total += P2 * k31                          # pilot_x31_kink concatenate

    # ---- layer32 ----
    total += 8 * w
    total += (4 * a28 * o30 + 4 * o30 * w + 4 * o30 * o31
              + _mm(a28, o30, o31))            # folded29_to31_on
    total += 4 * k30 * w + 4 * k30 * o31       # kink30_to31_on
    k_run = fold["k32_init"]
    if fold["d32_init"] > 0:
        total += _pre32_bill(a28, o31, k30, k31, fold["d32_init"], P2, w)
        total += _refine_bill(fold["d32_init"], fold["r32"], P2)
        k_run += fold["r32"]
        total += 2 * k_run
    if fold["o32_init"] > 0:
        total += _pre32_bill(a28, o31, k30, k31, fold["o32_init"], P2, w)
        total += _refine_bill(fold["o32_init"], fold["dm32"], P2)
        k_run += fold["dm32"]
        total += 2 * k_run
    k32 = fold["k32"]
    o32 = fold["o32"]
    d32 = fold["d32"]
    total += _sort_bill(k32)
    if k32 > 0:
        total += _pre32_bill(a28, o31, k30, k31, k32, big, w)
        total += big * k32                     # relu
        total += big * k32                     # mean
    if o32 > 0:
        total += big * a28 + big * k30 + big * k31           # three means
        total += (4 * o31 * w + 4 * o31 * o32 + _mm(a28, o31, o32)
                  + _mm(1, a28, o32))          # folded path + vec@mat
        total += (4 * o31 * w + 4 * o31 * o32 + _mm(k30, o31, o32)
                  + _mm(1, k30, o32))
        total += 4 * k31 * w + 4 * k31 * o32 + _mm(1, k31, o32)
        total += 2 * o32                       # two adds
    if d32 > 0:
        total += 4 * d32                       # analytic means gather
    # _assemble_vector: int concat + float concat + argsort + gather
    total += 2 * w + w + _sort_bill(w) + 4 * w

    # first-layer tangent recursion, layers 1..depth-1
    per_layer = 2 * _mm(1, w, w) + w * w + 16 * w + w + 16 * w + 3 + w + 12 * w
    total += (depth - 1) * per_layer
    total += 2 * w                             # lambda * delta, subtract
    total += depth * w                         # final stack
    return total


class Estimator(_FrozenN39936):
    """fold3-39936 with a deterministic per-network billed-FLOP cap."""

    cap_billed_flops = 244.8e9        # 0.9 * B, B = 272e9 (predeclared)
    min_n_eff = 1_024                 # = fold_pilot_base; see module docstring

    @staticmethod
    def _tally() -> int:
        # O(1) live read; budget_summary_dict() re-scans the process-global
        # accumulator and its cost grows with suite position (U2 bound:
        # ~11% of B at net 100, C>B breach for near-cap nets past ~92).
        try:
            from flopscope._budget import get_active_budget
            return int(get_active_budget().flops_used)
        except Exception:
            return 0

    def _simulate_cap_sets(self, mlp):
        """Billed pilot-identical replay of the parent's set evolution.

        Propagates only the first fold_pilot_base frame rows (plus antipodal
        images) through the exact selection logic of the parent predict().
        Row-for-row these are the same pilot rows the parent will consult,
        so the recorded partition sizes match the real run.
        Returns (loop_dims, fold, dp_cost, sim_cost) with observed bills.
        """
        t0 = self._tally()
        _, alphas, _, _ = _diagonal_gaussian_pass(mlp)
        dp_cost = self._tally() - t0

        P = self.fold_pilot_base
        p = self.pilot_base
        z = self._gaussian[:P]
        first_pre = z @ mlp.weights[0]
        x = fnp.concatenate(
            (fnp.maximum(first_pre, 0.0), fnp.maximum(-first_pre, 0.0)),
            axis=0,
        )
        loop_dims = []
        active = fnp.arange(mlp.width)
        for layer in range(1, mlp.depth - 3):
            structural = fnp.flatnonzero(alphas[layer] >= self.dead_alpha)
            cold = fnp.flatnonzero(alphas[layer] < self.dead_alpha)
            if cold.shape[0] > 0:
                pilot_x = fnp.concatenate((x[:p], x[P:P + p]), axis=0)
                pilot_pre = pilot_x @ mlp.weights[layer][active, :][:, cold]
                fired = fnp.max(pilot_pre, axis=0) > 0.0
                rescued = cold[fnp.flatnonzero(fired)]
                next_active = fnp.sort(
                    fnp.concatenate((structural, rescued), axis=0)
                )
            else:
                rescued = cold
                next_active = structural
            loop_dims.append((
                int(active.shape[0]), int(cold.shape[0]),
                int(rescued.shape[0]), int(next_active.shape[0]),
            ))
            x = fnp.maximum(
                x @ mlp.weights[layer][active, :][:, next_active], 0.0
            )
            active = next_active

        fold = {"a28": int(active.shape[0])}

        # ---- layer30 (x here IS the parent's pilot_x29, row for row) ----
        layer30 = mlp.depth - 3
        d30, k30, o30 = _initial_regimes(
            alphas[layer30], self.dead_alpha, self.on_alpha
        )
        fold["d30_init"] = int(d30.shape[0])
        fold["k30_init"] = int(k30.shape[0])
        fold["o30_init"] = int(o30.shape[0])
        weight30 = mlp.weights[layer30][active, :]
        if d30.shape[0] > 0:
            d30, r30 = _refine_dead(d30, x @ weight30[:, d30])
            k30 = fnp.concatenate((k30, r30), axis=0)
            fold["r30"] = int(r30.shape[0])
        else:
            fold["r30"] = 0
        if o30.shape[0] > 0:
            o30, dm30 = _refine_on(o30, x @ weight30[:, o30])
            k30 = fnp.concatenate((k30, dm30), axis=0)
            fold["dm30"] = int(dm30.shape[0])
        else:
            fold["dm30"] = 0
        k30 = fnp.sort(k30)
        fold["k30"] = int(k30.shape[0])
        fold["o30"] = int(o30.shape[0])
        x30_kink = fnp.maximum(x @ weight30[:, k30], 0.0)

        # ---- layer31 ----
        layer31 = mlp.depth - 2
        d31, k31, o31 = _initial_regimes(
            alphas[layer31], self.dead_alpha, self.on_alpha
        )
        fold["d31_init"] = int(d31.shape[0])
        fold["k31_init"] = int(k31.shape[0])
        fold["o31_init"] = int(o31.shape[0])
        weight31 = mlp.weights[layer31]

        def folded30_to31(columns):
            return weight30[:, o30] @ weight31[o30, :][:, columns]

        def pre31(columns):
            return (
                x @ folded30_to31(columns)
                + x30_kink @ weight31[k30, :][:, columns]
            )

        if d31.shape[0] > 0:
            d31, r31 = _refine_dead(d31, pre31(d31))
            k31 = fnp.concatenate((k31, r31), axis=0)
            fold["r31"] = int(r31.shape[0])
        else:
            fold["r31"] = 0
        if o31.shape[0] > 0:
            o31, dm31 = _refine_on(o31, pre31(o31))
            k31 = fnp.concatenate((k31, dm31), axis=0)
            fold["dm31"] = int(dm31.shape[0])
        else:
            fold["dm31"] = 0
        k31 = fnp.sort(k31)
        fold["k31"] = int(k31.shape[0])
        fold["o31"] = int(o31.shape[0])
        x31_kink = fnp.maximum(pre31(k31), 0.0)

        # ---- layer32 ----
        layer32 = mlp.depth - 1
        d32, k32, o32 = _initial_regimes(
            alphas[layer32], self.dead_alpha, self.on_alpha
        )
        fold["d32_init"] = int(d32.shape[0])
        fold["k32_init"] = int(k32.shape[0])
        fold["o32_init"] = int(o32.shape[0])
        weight32 = mlp.weights[layer32]
        folded29_to31_on = folded30_to31(o31)
        kink30_to31_on = weight31[k30, :][:, o31]

        def pre32(columns):
            return (
                x @ (folded29_to31_on @ weight32[o31, :][:, columns])
                + x30_kink
                @ (kink30_to31_on @ weight32[o31, :][:, columns])
                + x31_kink @ weight32[k31, :][:, columns]
            )

        if d32.shape[0] > 0:
            d32, r32 = _refine_dead(d32, pre32(d32))
            k32 = fnp.concatenate((k32, r32), axis=0)
            fold["r32"] = int(r32.shape[0])
        else:
            fold["r32"] = 0
        if o32.shape[0] > 0:
            o32, dm32 = _refine_on(o32, pre32(o32))
            k32 = fnp.concatenate((k32, dm32), axis=0)
            fold["dm32"] = int(dm32.shape[0])
        else:
            fold["dm32"] = 0
        k32 = fnp.sort(k32)
        fold["k32"] = int(k32.shape[0])
        fold["o32"] = int(o32.shape[0])
        fold["d32"] = int(d32.shape[0])

        sim_cost = self._tally() - t0
        return loop_dims, fold, int(dp_cost), int(sim_cost)

    def predict(self, mlp, budget):
        z_full = self._gaussian
        if z_full is None:
            raise RuntimeError("setup() did not initialize the Gaussian net")

        loop_dims, fold, dp_cost, sim_cost = self._simulate_cap_sets(mlp)
        # Total predicted bill: observed cap-sim (which already contains one
        # diagonal pass) + the parent's own diagonal pass (identical ops =>
        # identical bill) + modeled main run.
        overhead = sim_cost + dp_cost
        full = int(type(self).n_base)
        cap = float(self.cap_billed_flops)

        def c_pred(n):
            return overhead + predict_main_bill(
                n, mlp.width, mlp.depth, self.pilot_base,
                self.fold_pilot_base, loop_dims, fold,
            )

        n_eff = self.min_n_eff
        for k in range(full // 256, self.min_n_eff // 256 - 1, -1):
            if c_pred(256 * k) <= cap:
                n_eff = 256 * k
                break

        self.last_cap_report = {
            "n_eff": n_eff,
            "cap_billed_flops": cap,
            "c_pred_full": int(c_pred(full)),
            "c_pred_chosen": int(c_pred(n_eff)),
            "sim_cost_observed": sim_cost,
            "dp_cost_observed": dp_cost,
            "loop_dims": loop_dims,
            "fold_dims": dict(fold),
        }

        try:
            if n_eff < full:
                self._gaussian = z_full[:n_eff]
                self.n_base = n_eff          # instance shadow of class attr
            return super().predict(mlp, budget)
        finally:
            self._gaussian = z_full
            self.__dict__.pop("n_base", None)
