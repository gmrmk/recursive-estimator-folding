"""Additive spectral PSD guard for the M179 zero-order recurrence.

## Why this exists

`gm_m179_m199` recorded, and `gm_spd_width_scaling` measured as a width law,
that the pre-ReLU covariance of the exact full-covariance recurrence leaves the
positive-definite cone before layer 32 at production width. The verdict states
the gap in the producer's own words:

    `relu_moments` checks diagonal variance and pairwise rho, never the
    spectrum, so it silently ACCEPTS a numerically non-PSD covariance from
    layer 12-13 onward at width 256. ... The 31-layer archive was never
    validated for spectral PSD at depth, and that is a gap in our own record.

Measured blast radius over the 74 cells on record:

  * the shipping per-pair guard (`|rho| <= RHO_MAX`) fired **0 / 74** times;
  * a spectral guard fires in 45 / 74, and in **18 / 18** cells at width >= 96;
  * at width 256 the median first-loss layer is 11, so layers 11-32 --
    **69% of the archived layers** -- are downstream of the loss (75% at 224).

## What this module is, and is not

It is **additive**. It does not modify `m179_background_producer.py`, which is
frozen under `M179_SHA256SUMS_20260807.txt`; editing a frozen artifact would
break the manifest and the fold discipline. This is a separate mechanism that
can be composed in front of the frozen producer, and its own predeclaration and
report stand beside it.

It is a **detector**, not a repair. It makes the silent acceptance loud. It does
not make the closure reach layer 32 -- nothing here changes the mathematics, and
the honest repair (propagating a factored Cholesky/eigendecomposition state
rather than re-assembling the covariance entrywise) remains untested.

Style follows the producer's existing stratum discipline: **fail closed, raise,
no clip, no floor, no ridge, no eigenvalue truncation.**
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# M198 DelayOneContext's floor, restated here so this module stands alone.
DEFAULT_VARIANCE_FLOOR = 1e-12


class SpectralPSDRefusal(RuntimeError):
    """Raised when the propagated covariance is not safely SPD.

    Carries the diagnostic the per-pair guard cannot produce: which layer, the
    minimum eigenvalue, and how that eigenvalue compares with the entrywise
    assembly scale eps * n * lambda_max -- the scale below which an
    entrywise-assembled Gram matrix is indefinite from float64 round-off alone.
    """


@dataclass(frozen=True)
class SpectralState:
    layer: int
    width: int
    min_eigenvalue: float
    max_eigenvalue: float
    assembly_scale: float
    safe: bool

    @property
    def roundoff_dominated(self) -> bool:
        """True when |min eig| sits at or below the entrywise assembly noise.

        Distinguishes the two regimes measured in gm_spd_width_scaling: below
        width ~64 the floor is reached by genuine ill-conditioning, one to three
        orders above round-off; from ~80 up the eigenvalue is at or beneath the
        assembly scale and the indefiniteness is representational.
        """
        return abs(self.min_eigenvalue) <= self.assembly_scale


def inspect(covariance: np.ndarray, *, layer: int = -1,
            floor: float = DEFAULT_VARIANCE_FLOOR) -> SpectralState:
    """Symmetrize and spectrally inspect a pre-ReLU covariance. Never mutates."""
    C = np.asarray(covariance, dtype=np.float64)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError("covariance must be a square matrix")
    n = C.shape[0]
    sym = 0.5 * (C + C.T)
    eigs = np.linalg.eigvalsh(sym)
    lo, hi = float(eigs[0]), float(eigs[-1])
    return SpectralState(
        layer=layer,
        width=n,
        min_eigenvalue=lo,
        max_eigenvalue=hi,
        assembly_scale=float(np.finfo(np.float64).eps * n * max(hi, 0.0)),
        safe=lo > floor,
    )


def require_spd(covariance: np.ndarray, *, layer: int = -1,
                floor: float = DEFAULT_VARIANCE_FLOOR) -> SpectralState:
    """Fail closed unless the covariance is safely SPD. Returns the state."""
    state = inspect(covariance, layer=layer, floor=floor)
    if not state.safe:
        raise SpectralPSDRefusal(
            f"pre-ReLU covariance is not safely SPD at layer {state.layer} "
            f"(width {state.width}): min eig {state.min_eigenvalue:.6e} "
            f"<= floor {floor:.1e}; lambda_max {state.max_eigenvalue:.6e}; "
            f"assembly scale eps*n*lambda_max {state.assembly_scale:.6e}; "
            f"round-off dominated: {state.roundoff_dominated}"
        )
    return state


def guarded_zero_order_recurrence(weights, relu_moments, *,
                                  floor: float = DEFAULT_VARIANCE_FLOOR):
    """Run the frozen recurrence with a spectral check at every layer.

    `relu_moments` is passed in rather than imported so this module has no
    dependency on the frozen producer and is testable on its own. Compose it as:

        from m179_background_producer import relu_moments
        states = guarded_zero_order_recurrence(weights, relu_moments)

    Yields one SpectralState per layer and raises SpectralPSDRefusal at the
    first unsafe layer, instead of silently archiving it.
    """
    W0 = np.asarray(weights[0], dtype=np.float64)
    width = W0.shape[0]
    mu = np.zeros(width, dtype=np.float64)
    V = np.eye(width, dtype=np.float64)
    states: list[SpectralState] = []
    for layer, W in enumerate(weights, start=1):
        W = np.asarray(W, dtype=np.float64)
        a = mu @ W
        C = W.T @ (V @ W)
        states.append(require_spd(C, layer=layer, floor=floor))
        step = relu_moments(a, 0.5 * (C + C.T))
        mu, V = step.mu, step.V
    return states
