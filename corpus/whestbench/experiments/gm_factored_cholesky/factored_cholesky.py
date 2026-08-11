"""Factored (Cholesky Gram) propagation of the M179 second-order state.

Two entry points, deliberately separate:

* `diagnose(...)` -- records the full per-layer trajectory of the dense path,
  the factored path, and the post-ReLU state, without raising. This is what
  answers the predeclared question of *where* the indefiniteness is born.
* `factored_recurrence(...)` -- the producer form. Fails closed at the first
  non-factorable state. No clip, no floor, no ridge, no eigenvalue truncation.

Mechanism, one change only: carry `L` with `V = L @ L.T`, form `M = L.T @ W`,
and take `C = M.T @ M`. `C` is then a Gram of a real matrix and is PSD by
construction, where the dense path forms the same object entrywise with
independent `O(eps)` error per entry and no structural guarantee.

`relu_moments` is injected rather than imported so this module and its tests run
on a checkout without PR #1.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

VARIANCE_FLOOR = 1e-12


class NotFactorable(RuntimeError):
    """The carried second-order state is not positive definite."""


def _sym(A: np.ndarray) -> np.ndarray:
    return 0.5 * (A + A.T)


def min_eig(A: np.ndarray) -> float:
    return float(np.linalg.eigvalsh(_sym(A))[0])


def max_eig(A: np.ndarray) -> float:
    return float(np.linalg.eigvalsh(_sym(A))[-1])


def factor(V: np.ndarray) -> np.ndarray:
    """Cholesky factor of the carried state. Raises rather than repairing."""
    try:
        return np.linalg.cholesky(_sym(np.asarray(V, dtype=np.float64)))
    except np.linalg.LinAlgError as exc:
        raise NotFactorable(
            f"state is not positive definite: min eig {min_eig(V):.6e}"
        ) from exc


def gram_pre_covariance(L: np.ndarray, W: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (M, C) with M = L.T @ W and C = M.T @ M -- PSD by construction."""
    M = L.T @ W
    return M, M.T @ M


def dense_pre_covariance(V: np.ndarray, W: np.ndarray) -> np.ndarray:
    """The frozen path: C = W.T @ (V @ W), assembled entrywise."""
    return W.T @ (V @ W)


@dataclass
class LayerRecord:
    layer: int
    min_eig_V_post: float = 0.0        # post-ReLU state out of relu_moments
    min_eig_C_dense: float = 0.0       # frozen path
    min_eig_C_gram: float = 0.0        # factored path
    max_eig_C_dense: float = 0.0
    rel_gap: float = 0.0               # ||C_gram - C_dense||_max / ||C_dense||_max
    state_factorable: bool = True


@dataclass
class Trajectory:
    width: int
    replicate: int
    layers: list[LayerRecord] = field(default_factory=list)
    first_dense_trip: int | None = None
    first_gram_trip: int | None = None
    first_state_nonpsd: int | None = None
    first_unfactorable: int | None = None


def diagnose(weights, relu_moments, *, width: int = 0, replicate: int = 0,
             floor: float = VARIANCE_FLOOR) -> Trajectory:
    """Run both paths side by side and record where definiteness is lost.

    The dense path drives the recurrence, so the trajectory is directly
    comparable with the gm_spd_width_scaling record for the same cell. The
    factored path is computed alongside at each layer from the *same* state.
    Nothing raises; refusals are recorded.
    """
    W0 = np.asarray(weights[0], dtype=np.float64)
    n = W0.shape[0]
    traj = Trajectory(width=n if not width else width, replicate=replicate)
    mu = np.zeros(n, dtype=np.float64)
    V = np.eye(n, dtype=np.float64)

    for layer, Wk in enumerate(weights, start=1):
        W = np.asarray(Wk, dtype=np.float64)
        rec = LayerRecord(layer=layer)

        rec.min_eig_V_post = min_eig(V)
        if rec.min_eig_V_post <= 0.0 and traj.first_state_nonpsd is None:
            traj.first_state_nonpsd = layer

        C_dense = dense_pre_covariance(V, W)
        rec.min_eig_C_dense = min_eig(C_dense)
        rec.max_eig_C_dense = max_eig(C_dense)

        try:
            L = factor(V)
            _, C_gram = gram_pre_covariance(L, W)
            rec.min_eig_C_gram = min_eig(C_gram)
            denom = float(np.max(np.abs(C_dense))) or 1.0
            rec.rel_gap = float(np.max(np.abs(C_gram - C_dense))) / denom
        except NotFactorable:
            rec.state_factorable = False
            rec.min_eig_C_gram = float("nan")
            rec.rel_gap = float("nan")
            if traj.first_unfactorable is None:
                traj.first_unfactorable = layer

        if traj.first_dense_trip is None and rec.min_eig_C_dense <= floor:
            traj.first_dense_trip = layer
        if (traj.first_gram_trip is None and rec.state_factorable
                and rec.min_eig_C_gram <= floor):
            traj.first_gram_trip = layer

        traj.layers.append(rec)

        step = relu_moments(mu @ W, _sym(C_dense))
        mu, V = step.mu, step.V

    return traj


def factored_recurrence(weights, relu_moments, *, floor: float = VARIANCE_FLOOR):
    """Producer form: propagate through the Gram, fail closed on refusal."""
    W0 = np.asarray(weights[0], dtype=np.float64)
    n = W0.shape[0]
    mu = np.zeros(n, dtype=np.float64)
    V = np.eye(n, dtype=np.float64)
    out = []
    for layer, Wk in enumerate(weights, start=1):
        W = np.asarray(Wk, dtype=np.float64)
        try:
            L = factor(V)
        except NotFactorable as exc:
            raise NotFactorable(f"layer {layer}: {exc}") from exc
        _, C = gram_pre_covariance(L, W)
        lo = min_eig(C)
        if lo <= floor:
            raise NotFactorable(
                f"layer {layer}: Gram pre-covariance below floor "
                f"(min eig {lo:.6e} <= {floor:.1e})"
            )
        step = relu_moments(mu @ W, _sym(C))
        mu, V = step.mu, step.V
        out.append((layer, lo))
    return out
