"""M167 response-free collision-owner unification for the M156 [2,1,1] table.

M156 represents the hidden fourth-order multiset ``{i,i,j,k}`` through an
ordered singleton-symmetric cubic coefficient table.  It deliberately set
collision triples to zero because those entries had separate physical owners.
M167 asks a narrower algebraic question: can those real owners be put into the
same *complete* cubic table, with their previous source contribution retired,
without a double count?

The answer is yes at the source-algebra level.  If ``K4``, ``K31``, and
``K22`` denote physical connected fourth cumulants, the exact table mapping is

    T[i,i,i] = K4[i] / 6,
    T[i,i,j] = T[i,j,i] = K31[i,j] / 3,      i != j,
    T[i,j,j] = K22[i,j] / 2,                 i != j.

The factors are forced by hidden-index orbit multiplicities, not fitted.  The
two ``[2,2]`` representatives ``(i,j,j)`` and ``(j,i,i)`` together carry one
physical unordered-pair source.  This module also localizes the important
limit: M163's surviving coefficient ``-2 A_ij^2`` has the same ``[2,2]``
*support*, but is not the physical ``K22`` coefficient in general.  It may be
an add/subtract control within that owner, not reclassified as that owner.

All code is generated-array source algebra.  It has no network response,
truth, scorer, contest, leaderboard, submission, or champion dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for _relative in (
    "m156_extended_domain_star_control",
    "m163_exterior_collision_null",
):
    _path = str(ROOT / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m156_extended_domain_star_control import (  # noqa: E402
    Source211,
    compiled_extended_star_control,
    dense_extended_source,
    distinct_target_extension,
    extended_star_table,
    source_add,
    source_max_abs_difference,
    zero_source,
)
from m163_exterior_collision_null import (  # noqa: E402
    compile_exterior_star_control,
    exterior_edge_matrix,
    exterior_star_table,
)


@dataclass(frozen=True)
class PhysicalFourthOwners:
    """Canonical physical collision values before their M167 reassignment.

    ``k31[i,j]`` names the physical multiset ``{i,i,i,j}``, so it is directed
    by its majority label.  ``k22[i,j]`` names ``{i,i,j,j}`` and is symmetric.
    All diagonal entries of the two mixed classes must be zero: their fully
    collapsed value belongs solely to ``k4``.
    """

    k4: np.ndarray
    k31: np.ndarray
    k22: np.ndarray


ORBIT_MAPPING = {
    "iii->[4]": {"complete_triples_per_physical_unit": 1, "coefficient_scale": 1.0 / 6.0},
    "iik/iji->[3,1]": {"complete_triples_per_physical_unit": 2, "coefficient_scale": 1.0 / 3.0},
    "ijj->[2,2]": {"complete_triples_per_physical_unit": 2, "coefficient_scale": 1.0 / 2.0},
}


def _owners(owners: PhysicalFourthOwners) -> PhysicalFourthOwners:
    k4 = np.asarray(owners.k4, dtype=np.float64)
    k31 = np.asarray(owners.k31, dtype=np.float64)
    k22 = np.asarray(owners.k22, dtype=np.float64)
    n = k4.size
    if (
        k4.ndim != 1
        or k31.shape != (n, n)
        or k22.shape != (n, n)
        or n < 2
        or not all(np.all(np.isfinite(value)) for value in (k4, k31, k22))
        or not np.array_equal(np.diag(k31), np.zeros(n))
        or not np.array_equal(np.diag(k22), np.zeros(n))
        or not np.allclose(k22, k22.T, rtol=0.0, atol=2.0e-13)
    ):
        raise ValueError("invalid physical [4]/[3,1]/[2,2] ownership tables")
    return PhysicalFourthOwners(k4.copy(), k31.copy(), 0.5 * (k22 + k22.T))


def _distinct_table(value: np.ndarray, width: int) -> np.ndarray:
    table = np.asarray(value, dtype=np.float64)
    if (
        table.shape != (width, width, width)
        or not np.all(np.isfinite(table))
        or not np.allclose(table, table.swapaxes(1, 2), rtol=0.0, atol=2.0e-13)
    ):
        raise ValueError("distinct [2,1,1] table must be finite and singleton-symmetric")
    return table


def complete_owner_table(distinct_211: np.ndarray, owners: PhysicalFourthOwners) -> np.ndarray:
    """Move every physical repeated-index owner into M156's complete table.

    The input may contain arbitrary collision values, which are discarded.
    Only its pairwise-distinct values are retained.  Thus this is not another
    zero extension: every collision entry is immediately replaced by the
    physical fourth-cumulant class to which it belongs.
    """

    checked = _owners(owners)
    n = checked.k4.size
    table = distinct_target_extension(_distinct_table(distinct_211, n))
    for i in range(n):
        table[i, i, i] = checked.k4[i] / 6.0
        for j in range(n):
            if i == j:
                continue
            table[i, i, j] = checked.k31[i, j] / 3.0
            table[i, j, i] = checked.k31[i, j] / 3.0
            table[i, j, j] = checked.k22[i, j] / 2.0
    return table


def retired_owners(owners: PhysicalFourthOwners) -> PhysicalFourthOwners:
    """The prior separate owners after M167 transfers their entire source."""

    checked = _owners(owners)
    n = checked.k4.size
    return PhysicalFourthOwners(np.zeros(n), np.zeros((n, n)), np.zeros((n, n)))


def physical_collision_tensor(owners: PhysicalFourthOwners) -> np.ndarray:
    """Independent dense fourth-tensor oracle for the three physical classes."""

    checked = _owners(owners)
    n = checked.k4.size
    tensor = np.zeros((n, n, n, n), dtype=np.float64)
    for i in range(n):
        tensor[i, i, i, i] = checked.k4[i]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for unit in set(itertools.permutations((i, i, i, j))):
                tensor[unit] = checked.k31[i, j]
    for i in range(n):
        for j in range(i + 1, n):
            for unit in set(itertools.permutations((i, i, j, j))):
                tensor[unit] = checked.k22[i, j]
    return tensor


def source_from_physical_tensor(weight: np.ndarray, tensor: np.ndarray) -> Source211:
    """Direct fourth-tensor contraction reference for tiny generated widths."""

    w = np.asarray(weight, dtype=np.float64)
    value = np.asarray(tensor, dtype=np.float64)
    if w.ndim != 2 or value.shape != (w.shape[0],) * 4 or not np.all(np.isfinite(w)):
        raise ValueError("invalid tensor/weight reference inputs")
    full = np.einsum("ijkl,ia,jb,kc,ld->abcd", value, w, w, w, w, optimize=True)
    outputs = w.shape[1]
    aaab = np.empty((outputs, outputs), dtype=np.float64)
    aabb = np.empty((outputs, outputs), dtype=np.float64)
    for a in range(outputs):
        for b in range(outputs):
            aaab[a, b] = full[a, a, a, b]
            aabb[a, b] = full[a, a, b, b]
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def complete_source_reference(weight: np.ndarray, coefficient: np.ndarray) -> Source211:
    """Unrestricted direct M156 feature sum, including the width-two oracle.

    M156's production reference intentionally refuses widths below three.  This
    tiny direct expansion is used only to test the requested width ``2..6``
    orbit identity; for width at least three it agrees with M156 exactly.
    """

    w = np.asarray(weight, dtype=np.float64)
    table = np.asarray(coefficient, dtype=np.float64)
    if w.ndim != 2 or table.shape != (w.shape[0],) * 3 or not np.all(np.isfinite(table)):
        raise ValueError("invalid complete source reference input")
    if not np.allclose(table, table.swapaxes(1, 2), rtol=0.0, atol=2.0e-13):
        raise ValueError("complete coefficient must be singleton-symmetric")
    answer = zero_source(w.shape[1])
    for i, j, k in itertools.product(range(w.shape[0]), repeat=3):
        x, y, z = w[i], w[j], w[k]
        aaab = 3.0 * (np.outer(x * y * z, x) + np.outer(x * x * z, y))
        first = np.outer(x * x, y * z)
        split = 2.0 * np.outer(x * y, x * z)
        aabb = first + first.T + split + split.T
        feature = Source211(np.diag(aaab).copy(), aaab, aabb)
        answer = Source211(
            answer.aaaa + table[i, j, k] * feature.aaaa,
            answer.aaab + table[i, j, k] * feature.aaab,
            answer.aabb + table[i, j, k] * feature.aabb,
        )
    return answer


def direct_physical_owner_source(weight: np.ndarray, owners: PhysicalFourthOwners) -> Source211:
    """Closed-form source from the original separate physical owners."""

    checked = _owners(owners)
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] != checked.k4.size or not np.all(np.isfinite(w)):
        raise ValueError("weight shape differs from physical owner width")
    aaab = np.zeros((w.shape[1], w.shape[1]), dtype=np.float64)
    aabb = np.zeros_like(aaab)
    for i in range(w.shape[0]):
        x = w[i]
        aaab += checked.k4[i] * np.outer(x**3, x)
        aabb += checked.k4[i] * np.outer(x * x, x * x)
        for j in range(w.shape[0]):
            if i == j:
                continue
            y = w[j]
            aaab += checked.k31[i, j] * (
                3.0 * np.outer(x * x * y, x) + np.outer(x**3, y)
            )
            mixed = np.outer(x * x, x * y)
            aabb += 2.0 * checked.k31[i, j] * (mixed + mixed.T)
    for i in range(w.shape[0]):
        for j in range(i + 1, w.shape[0]):
            x, y = w[i], w[j]
            aaab += 3.0 * checked.k22[i, j] * (
                np.outer(x * y * y, x) + np.outer(x * x * y, y)
            )
            aabb += checked.k22[i, j] * (
                np.outer(x * x, y * y)
                + np.outer(y * y, x * x)
                + 4.0 * np.outer(x * y, x * y)
            )
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def complete_residual_table(complete_target: np.ndarray, control: np.ndarray) -> np.ndarray:
    """Subtract an all-domain control without re-zeroing physical collisions.

    M156's public ``residual_table`` intentionally applies
    ``distinct_target_extension`` because its original target had no physical
    collision owner.  M167 must not call that helper: doing so would silently
    erase the newly transferred `[4]`, `[3,1]`, and `[2,2]` classes.
    """

    target = np.asarray(complete_target, dtype=np.float64)
    value = np.asarray(control, dtype=np.float64)
    if (
        target.ndim != 3
        or target.shape[0] != target.shape[1]
        or target.shape != value.shape
        or not all(np.all(np.isfinite(item)) for item in (target, value))
        or not np.allclose(target, target.swapaxes(1, 2), rtol=0.0, atol=2.0e-13)
        or not np.allclose(value, value.swapaxes(1, 2), rtol=0.0, atol=2.0e-13)
    ):
        raise ValueError("complete target/control tables must be finite, matched, and singleton-symmetric")
    return target - value


def m156_conservation_error(weight: np.ndarray, complete_target: np.ndarray, covariance: np.ndarray) -> float:
    """Full-domain conservation after physical collision-owner reassignment."""

    control = extended_star_table(covariance)
    reconstructed = source_add(
        compiled_extended_star_control(weight, covariance),
        dense_extended_source(weight, complete_residual_table(complete_target, control)),
    )
    return source_max_abs_difference(dense_extended_source(weight, complete_target), reconstructed)


def m163_conservation_error(weight: np.ndarray, complete_target: np.ndarray, covariance: np.ndarray) -> float:
    """Same conservation law with M163's support-aware exterior control."""

    control = exterior_star_table(covariance)
    reconstructed = source_add(
        compile_exterior_star_control(weight, covariance),
        dense_extended_source(weight, complete_residual_table(complete_target, control)),
    )
    return source_max_abs_difference(dense_extended_source(weight, complete_target), reconstructed)


def gauge_owners(owners: PhysicalFourthOwners, gauge: np.ndarray) -> PhysicalFourthOwners:
    """Exact positive-hidden-gauge action on the three physical classes."""

    checked = _owners(owners)
    d = np.asarray(gauge, dtype=np.float64)
    if d.shape != checked.k4.shape or np.any(~np.isfinite(d)) or np.any(d <= 0.0):
        raise ValueError("gauge must be finite positive and match owner width")
    return PhysicalFourthOwners(
        checked.k4 * d**4,
        checked.k31 * (d[:, None] ** 3) * d[None, :],
        checked.k22 * (d[:, None] ** 2) * (d[None, :] ** 2),
    )


def permute_owners(owners: PhysicalFourthOwners, permutation: np.ndarray) -> PhysicalFourthOwners:
    """Relabel physical owners under the same row permutation as the weights."""

    checked = _owners(owners)
    p = np.asarray(permutation, dtype=int)
    if p.shape != checked.k4.shape or set(p.tolist()) != set(range(p.size)):
        raise ValueError("invalid owner permutation")
    return PhysicalFourthOwners(checked.k4[p], checked.k31[np.ix_(p, p)], checked.k22[np.ix_(p, p)])


def m163_required_k22_for_absorption(covariance: np.ndarray) -> np.ndarray:
    """Physical K22 that would be required to relabel M163's ijj control.

    M167 maps a physical pair coefficient to two table entries of ``K22/2``.
    M163 puts ``-2 A_ij^2`` in each such entry.  Equality would force
    ``K22_ij=-4 A_ij^2``.  This is a necessary identity, not an approximation.
    """

    edge = exterior_edge_matrix(covariance)[2]
    required = -4.0 * edge * edge
    np.fill_diagonal(required, 0.0)
    return required


def static_owner_ledger(width: int = 256, layers: int = 31) -> dict[str, object]:
    """Static disposition: ownership changes, compiler does not gain credit."""

    n = int(width)
    if n < 2 or int(layers) <= 0:
        raise ValueError("invalid static dimensions")
    return {
        "candidate": "M167 complete-domain physical collision-owner unification",
        "width": n,
        "layers": int(layers),
        "physical_units": {
            "[4]": n,
            "[3,1]": n * (n - 1),
            "[2,2]": n * (n - 1) // 2,
        },
        "complete_table_collision_triples": {
            "iii": n,
            "iik_and_iji": 2 * n * (n - 1),
            "ijj": n * (n - 1),
        },
        "mapping": ORBIT_MAPPING,
        "m156_dense_products_per_layer_unchanged": 5,
        "m163_dense_products_per_layer_unchanged": 5,
        "m167_added_dense_products_per_layer": 0,
        "m167_added_deployment_calls_claimed": 0,
        "existing_physical_owner_source": "retired exactly when its mapped complete-table entries are used",
        "m163_ijj": "same [2,2] support only; coefficient equality would require K22=-4A^2 and is not a generic identity",
        "static_disposition": "ALGEBRAIC_OWNER_REPAIR_ONLY",
        "implementation_blocker": "generic physical [2,2] formation/residual transport remains the existing Khatri--Rao-class obstruction; no cost credit or target implementation is claimed",
    }
