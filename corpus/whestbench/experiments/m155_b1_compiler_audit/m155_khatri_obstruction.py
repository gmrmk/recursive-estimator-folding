"""Response-free witness for M151's masked aabb split-pair obstruction.

No estimator, network target, response carrier, scorer, or competition data is
used here.  The routines expose the exact Khatri--Rao quadratic form forced by
the covariance-star part of the B=1 [2,1,1] control.
"""

from __future__ import annotations

import numpy as np


Array = np.ndarray


def _arrays(weight: Array, covariance: Array) -> tuple[Array, Array]:
    weight = np.asarray(weight, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if weight.ndim != 2 or weight.shape[0] < 3:
        raise ValueError("weight must have at least three labelled rows")
    if covariance.shape != (weight.shape[0], weight.shape[0]):
        raise ValueError("covariance and labelled weight widths disagree")
    if not np.all(np.isfinite(weight)) or not np.all(np.isfinite(covariance)):
        raise ValueError("inputs must be finite")
    if not np.allclose(covariance, covariance.T, rtol=0.0, atol=2e-13):
        raise ValueError("covariance must be symmetric")
    return weight, covariance


def off_diagonal_square(covariance: Array) -> Array:
    covariance = np.asarray(covariance, dtype=np.float64)
    off = covariance.copy()
    np.fill_diagonal(off, 0.0)
    return off * off


def symmetric_khatri_columns(weight: Array) -> tuple[Array, list[tuple[int, int]]]:
    """Return columns w[:,p]*w[:,q] for p<=q.

    This is a small-width parity representation.  Materializing it at target
    width is precisely the memory/cost exposure audited by this mutation.
    """

    weight = np.asarray(weight, dtype=np.float64)
    pairs = [(p, q) for p in range(weight.shape[1]) for q in range(p, weight.shape[1])]
    columns = np.stack(
        [weight[:, p] * weight[:, q] for p, q in pairs], axis=1
    )
    return columns, pairs


def split_pair_obstruction_khatri(weight: Array, covariance: Array) -> Array:
    """Compute E[p,q]=(w_p*w_q)^T (V_off^2) (w_p*w_q)."""

    weight, covariance = _arrays(weight, covariance)
    gram = off_diagonal_square(covariance)
    columns, pairs = symmetric_khatri_columns(weight)
    values = np.sum(columns * (gram @ columns), axis=0)
    answer = np.zeros((weight.shape[1], weight.shape[1]), dtype=np.float64)
    for value, (p, q) in zip(values, pairs):
        answer[p, q] = value
        answer[q, p] = value
    return answer


def split_pair_obstruction_exhaustive(weight: Array, covariance: Array) -> Array:
    """Independent O(n^2 m^2) reference for the same obstruction."""

    weight, covariance = _arrays(weight, covariance)
    gram = off_diagonal_square(covariance)
    output = np.zeros((weight.shape[1], weight.shape[1]), dtype=np.float64)
    for p in range(weight.shape[1]):
        for q in range(weight.shape[1]):
            for i in range(weight.shape[0]):
                left = weight[i, p] * weight[i, q]
                for j in range(weight.shape[0]):
                    output[p, q] += (
                        gram[i, j]
                        * left
                        * weight[j, p]
                        * weight[j, q]
                    )
    return output


def star_split_aabb_exhaustive(weight: Array, covariance: Array) -> Array:
    """Exact masked split-pair aabb source for d_ijk=-2 V_ij V_ik."""

    weight, covariance = _arrays(weight, covariance)
    n, output_width = weight.shape
    answer = np.zeros((output_width, output_width), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) != 3:
                    continue
                coefficient = -2.0 * covariance[i, j] * covariance[i, k]
                left = weight[i] * weight[j]
                right = weight[i] * weight[k]
                # M151's half-owned ordered feature contributes
                # 2*d*(outer(left,right)+transpose) in this slot.
                block = np.outer(left, right)
                answer += 2.0 * coefficient * (block + block.T)
    return answer


def star_split_aabb_decomposed(weight: Array, covariance: Array) -> Array:
    """Exact decomposition: -8[(W*Z)^T(W*Z)-E]."""

    weight, covariance = _arrays(weight, covariance)
    off = covariance.copy()
    np.fill_diagonal(off, 0.0)
    z = off @ weight
    unrestricted = (weight * z).T @ (weight * z)
    obstruction = split_pair_obstruction_khatri(weight, covariance)
    return -8.0 * (unrestricted - obstruction)


def target_cost_ledger(width: int = 256, source_layers: int = 31) -> dict[str, float | int | str]:
    """Cost of the smallest direct symmetric Khatri action under FlopScope.

    The entry is not a universal arithmetic-circuit lower bound.  It is the
    exact bill of the only currently installed generic dense realization of
    the forced quadratic form: G_(n,n) @ K_(n,n(n+1)/2).  Any proposed cheaper
    compiler must provide a new proved factorization and native trace.
    """

    n = int(width)
    layers = int(source_layers)
    columns = n * (n + 1) // 2
    f32_per_layer = 2 * n * n * columns - n * columns
    f64_per_layer = 2 * f32_per_layer
    one_k_f64_mib = n * columns * 8 / (1024.0 * 1024.0)
    return {
        "width": n,
        "source_layers": layers,
        "symmetric_quadratic_columns": columns,
        "f32_matmul_bill_per_layer": f32_per_layer,
        "f32_matmul_bill_all_layers": f32_per_layer * layers,
        "f64_matmul_bill_per_layer": f64_per_layer,
        "f64_matmul_bill_all_layers": f64_per_layer * layers,
        "f64_matmul_bill_all_layers_billions": f64_per_layer * layers / 1e9,
        "one_symmetric_khatri_buffer_f64_mib": one_k_f64_mib,
        "two_input_output_buffers_f64_mib": 2.0 * one_k_f64_mib,
        "m151_inclusive_untraced_cap_billions": 10.291363760,
        "known_m151_branch_billions": 89.708636240,
        "status": "CURRENT_GENERIC_F64_COMPILER_EXCEEDS_CAP_BEFORE_OTHER_TERMS",
    }
