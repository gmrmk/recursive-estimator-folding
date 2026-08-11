"""V31-G4: inherited GUARDS logic over the grouped-call Kerdock child.

The parent M186/M187 evidence is ``a4_results.json`` plus ``A3_A4_NOTES.md``
under ``experiments/a_series_granular_adversarial``.  The executable wrapper
logic below is inherited from v3.1, but this child deliberately changes
``kerdock_v3_estimator.py``, ``fold3_estimator.py``, and
``row_blocked_winograd.py``.  The preexecution manifest binds those child
bytes; full-wrapper and guard-path parity remain unearned gates.

M186 - empty-regime guard.  A net whose pruning layer goes fully dead (every
neuron analytically dead under ``dead_alpha`` and no pilot rescue fires)
drives ``next_active`` empty; the frozen bill chain then rejects the
zero-width product with ``ValueError: matrix dimensions must be positive``
(fold3_estimator.py:143 -> row_blocked_winograd.py:88 -> cost_model.py:133;
observed on A4 input (f), the all-negative -3/16 shift net).  That message is
raised only by ``cost_model.direct_cost``; in the frozen predict path the row
count (2*n_base) and contracted width (previous active count, nonzero or the
previous layer would already have raised) are always positive, so the message
uniquely identifies the empty-active-set condition.  v3.1 catches exactly it
and degrades gracefully: the analytic diagonal-pass means for all layers (the
same fallback the frozen estimator already uses for dead neurons).

M187 - finite-output guard.  On f32-overflow-scale nets (A4 input (b), He x
1e3) the frozen chain silently returns NaN/inf.  v3.1 scans the final stacked
prediction with ``isfinite``; non-finite entries are replaced with the
analytic diagonal-pass means for those neurons (never zeros while any
information exists); entries whose analytic mean is itself non-finite are
clamped to the nearest finite float32 (inf -> +/-float32 max; NaN -> 0.0 only
as the information-free last resort).

Healthy-net target (future gate G1): the grouped child must reproduce the
parent GUARDS output word-for-word and return the guard-quiet output object
untouched.  The wrapper itself adds one ``isfinite`` scan plus its reduction
over the ``(depth, width)`` output stack, billed through FlopScope like every
other op.  Synthetic kernel parity does not establish this full-wrapper target.
Guard activations are reported in ``self.last_guard_report``.
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench.domain import MLP

from base_estimator import _diagonal_gaussian_pass
from kerdock_v3_estimator import Estimator as _FrozenKerdockV3

_EMPTY_REGIME_MESSAGE = "matrix dimensions must be positive"


class Estimator(_FrozenKerdockV3):
    """G4 Kerdock child with inherited M186 and M187 guard logic."""

    last_guard_report = None

    def _guard_reference_mlp(self, mlp: MLP) -> MLP:
        """Rebuild the net whose analytic pass the frozen predict used.

        At width 256 the frozen predict absorbs a Haar rotation (seeded
        deterministically by ``mlp.seed``) into the first weight before its
        analytic pass; the guard fallback mirrors that so its analytic means
        are the ones the crashed/overflowed run had computed.
        """
        if mlp.width != 256:
            return mlp
        rotation = self._haar_rotation(int(mlp.seed), mlp.width)
        first_weight = rotation.T @ mlp.weights[0]
        return MLP(
            width=mlp.width,
            depth=mlp.depth,
            weights=[first_weight, *mlp.weights[1:]],
            seed=mlp.seed,
            name=mlp.name,
        )

    def _analytic_fallback_stack(self, mlp: MLP):
        """Analytic diagonal-pass means for all layers, (depth, width)."""
        means, _, _, _ = _diagonal_gaussian_pass(self._guard_reference_mlp(mlp))
        return fnp.stack(means, axis=0)

    def predict(self, mlp: MLP, budget):
        report = {
            "m186_empty_regime_fired": False,
            "m187_finite_output_fired": False,
            "m187_entries_nonfinite": 0,
            "m187_entries_replaced_analytic": 0,
            "m187_entries_clamped": 0,
        }
        self.last_guard_report = report
        fallback = None
        try:
            out = super().predict(mlp, budget)
        except ValueError as exc:
            if _EMPTY_REGIME_MESSAGE not in str(exc):
                raise
            # M186: a fully-dead layer emptied the active set and the frozen
            # bill chain rejected the zero-width product.  Graceful
            # degradation per the A4 finding: analytic means, all layers.
            report["m186_empty_regime_fired"] = True
            fallback = self._analytic_fallback_stack(mlp)
            out = fallback

        finite = fnp.isfinite(out)
        if bool(fnp.all(finite)):
            return out

        # M187: never return a non-finite prediction.
        report["m187_finite_output_fired"] = True
        n_bad = int(out.size) - int(fnp.sum(finite))
        report["m187_entries_nonfinite"] = n_bad
        if fallback is None:
            fallback = self._analytic_fallback_stack(mlp)
        repaired = fnp.where(finite, out, fallback)
        still_bad = fnp.logical_not(fnp.isfinite(repaired))
        n_still = int(fnp.sum(still_bad))
        report["m187_entries_replaced_analytic"] = n_bad - n_still
        report["m187_entries_clamped"] = n_still
        if n_still:
            # The analytic mean itself overflowed/NaNed at these entries:
            # clamp to the nearest finite float32 (numpy defaults: inf ->
            # +/-float32 max, NaN -> 0.0 -- the information-free last resort).
            repaired = fnp.nan_to_num(repaired)
        return repaired
