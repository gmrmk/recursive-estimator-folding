"""Generated-only M227 row-HT collision source algebra.

The complete-domain objects ``p``, ``B``, and ``rho`` are exact.  One shared
uniform-without-replacement row subset estimates only ``t``, ``A``, ``E``,
and ``D``.  This module has no response, scorer, truth, or challenge access.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
M205 = HERE.parent / "m205_rankone_complete_physical_owner"
if str(M205) not in sys.path:
    sys.path.insert(0, str(M205))

from m205_rankone_complete_physical_owner import Source211  # noqa: E402


Array = np.ndarray


@dataclass(frozen=True)
class PriorityReceipt:
    """A pathwise hidden-label-bound SRSWOR priority receipt."""

    priorities: Array
    selected: Array
    subset_rows: int
    producer_epoch: int
    layer_ids: tuple[int, ...]


def _checked_weight_factor(weight: Array, factor: Array) -> tuple[Array, Array]:
    w = np.asarray(weight, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] < 3 or not np.all(np.isfinite(w)):
        raise ValueError("weight must be a finite labelled matrix of width at least three")
    if u.ndim != 1 or u.shape[0] != w.shape[0] or not np.all(np.isfinite(u)):
        raise ValueError("factor must be a finite vector matching the labelled width")
    return w, u


def _checked_selected(selected: Array, width: int) -> Array:
    raw = np.asarray(selected)
    if raw.ndim != 1 or raw.size < 1 or raw.size >= width:
        raise ValueError("selected rows must be a nonempty strict subset")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise ValueError("selected rows must be integer labels")
    labels = np.asarray(raw, dtype=np.int64)
    if np.any(labels < 0) or np.any(labels >= width):
        raise ValueError("selected row is outside the labelled width")
    if np.unique(labels).size != labels.size:
        raise ValueError("selected rows must be without replacement")
    return labels


def issue_priority_receipt(
    priorities: Array, *, subset_rows: int, producer_epoch: int
) -> PriorityReceipt:
    """Bind distinct continuous-priority ranks to labelled hidden rows."""

    values = np.asarray(priorities, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] < 3:
        raise ValueError("priorities must have shape (layers,width>=3)")
    if not np.all(np.isfinite(values)):
        raise ValueError("priorities must be finite")
    layers, width = map(int, values.shape)
    k = int(subset_rows)
    if k < 1 or k >= width:
        raise ValueError("subset_rows must be a nonempty strict subset")
    for row in values:
        if np.unique(row).size != width:
            raise ValueError("priority ties are forbidden")
    owned = values.copy()
    selected = np.argsort(owned, axis=1, kind="stable")[:, :k].copy()
    owned.setflags(write=False)
    selected.setflags(write=False)
    return PriorityReceipt(
        priorities=owned,
        selected=selected,
        subset_rows=k,
        producer_epoch=int(producer_epoch),
        layer_ids=tuple(range(1, layers + 1)),
    )


def permute_receipt(receipt: PriorityReceipt, permutation: Array) -> PriorityReceipt:
    """Co-permute one hidden-label permutation with every layer receipt."""

    order = np.asarray(permutation, dtype=np.int64)
    width = int(receipt.priorities.shape[1])
    if order.shape != (width,) or not np.array_equal(np.sort(order), np.arange(width)):
        raise ValueError("permutation must contain every hidden label exactly once")
    return issue_priority_receipt(
        receipt.priorities[:, order],
        subset_rows=receipt.subset_rows,
        producer_epoch=receipt.producer_epoch,
    )


def compile_row_sketch_collision_source_numpy(
    weight: Array, factor: Array, selected: Array
) -> Source211:
    """Compile the M227 collision estimator for one fixed row subset."""

    w, u = _checked_weight_factor(weight, factor)
    labels = _checked_selected(selected, int(w.shape[0]))
    s = u[:, None] * w
    p = np.sum(s, axis=0)
    b = s.T @ s
    rho = np.diag(b).copy()

    chosen = s[labels]
    chosen2 = chosen * chosen
    chosen3 = chosen2 * chosen
    scale = float(s.shape[0]) / float(labels.size)
    t = scale * np.sum(chosen3, axis=0)
    a = scale * (chosen2.T @ chosen)
    e = scale * (chosen3.T @ chosen)
    d = scale * (chosen2.T @ chosen2)

    aaab = (
        -18.0 * (p[:, None] * a)
        - 6.0 * np.outer(t, p)
        - 12.0 * (rho[:, None] * b)
        + 24.0 * e
    )
    aabb = (
        -12.0 * (a * p[None, :] + p[:, None] * a.T)
        - 4.0 * np.outer(rho, rho)
        - 8.0 * (b * b)
        + 24.0 * d
    )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


__all__ = [
    "PriorityReceipt",
    "compile_row_sketch_collision_source_numpy",
    "issue_priority_receipt",
    "permute_receipt",
]
