"""Exact and stochastic contractions for the M126 repeated-output source audit.

The exact functions operate only on supplied generated algebra arrays.  They
contain no model, target, scorer, network, file, or submission access.

The declared bridge-tree source uses exact path/star contractions and sparse
one/two-coordinate collision replacements.  The full-width AABB hard tables
are exposed both as small-width exact references and as unbiased Rademacher
probe samples.  A probe estimator is not an exact table and carries no
accuracy guarantee without a separately frozen variance gate.
"""

from __future__ import annotations

import itertools
import math
from typing import Final

import numpy as np


ORBIT_MULTIPLICITIES: Final[dict[str, dict[str, int]]] = {
    "k3_aab": {"centre_a": 2, "centre_b": 1},
    "k4_star_aaab": {"centre_a": 3, "centre_b": 1},
    "k4_star_aabb": {"centre_a": 2, "centre_b": 2},
    "k4_path_aaab": {"singleton_endpoint": 6, "singleton_internal": 6},
    "k4_path_aabb": {
        "block_aabb": 4,
        "self_abba": 2,
        "self_baab": 2,
        "cross_abab": 4,
    },
    "source_collision_partitions": {
        "k3_3": 1,
        "k3_21": 3,
        "k4_4": 1,
        "k4_31": 4,
        "k4_22": 6,
        "k4_211": 12,
    },
}


def _require_matrix(name: str, value: np.ndarray) -> np.ndarray:
    answer = np.asarray(value, dtype=np.float64)
    if answer.ndim != 2 or not np.all(np.isfinite(answer)):
        raise ValueError(f"{name} must be one finite matrix")
    return answer


def _require_bridge(q: np.ndarray) -> np.ndarray:
    q = _require_matrix("q", q)
    if q.shape[0] != q.shape[1]:
        raise ValueError("q must be square")
    if not np.allclose(q, q.T, rtol=0.0, atol=2.0e-12):
        raise ValueError("q must be symmetric")
    if not np.allclose(np.diag(q), 1.0, rtol=0.0, atol=2.0e-12):
        raise ValueError("the bridge diagonal must equal one")
    return q


def _require_vector(name: str, value: np.ndarray, size: int) -> np.ndarray:
    answer = np.asarray(value, dtype=np.float64)
    if answer.shape != (size,) or not np.all(np.isfinite(answer)):
        raise ValueError(f"{name} must be one finite length-{size} vector")
    return answer


def _require_weight(weight: np.ndarray, rows: int) -> np.ndarray:
    weight = _require_matrix("weight", weight)
    if weight.shape[0] != rows:
        raise ValueError("weight row count must match the source width")
    return weight


def _repeated_result(
    k3_aab: np.ndarray, k4_aaab: np.ndarray, k4_aabb: np.ndarray
) -> dict[str, np.ndarray]:
    return {
        "k3_aaa": np.diag(k3_aab).copy(),
        "k3_aab": k3_aab,
        "k4_aaaa": np.diag(k4_aaab).copy(),
        "k4_aaab": k4_aaab,
        "k4_aabb": k4_aabb,
    }


def path_hard_tables_exact(
    q: np.ndarray, gamma2: np.ndarray, weight: np.ndarray
) -> dict[str, np.ndarray]:
    """Return the exact ABBA self and ABAB cross tables.

    This direct contraction is a small-width oracle.  For dense width-m
    inputs it has the generic O(n^2 m^2) cost that M126 is auditing.
    """

    q = _require_bridge(q)
    n = q.shape[0]
    gamma2 = _require_vector("gamma2", gamma2, n)
    weight = _require_weight(weight, n)
    propagated = q @ weight
    weighted_propagated = gamma2[:, None] * propagated
    identity_self = (weighted_propagated * weighted_propagated).T @ (weight * weight)
    pair_feature = weighted_propagated * weight
    identity_cross = pair_feature.T @ pair_feature
    full_self = np.einsum(
        "ia,ib,ij,ja,jb->ab",
        weighted_propagated,
        weight,
        q,
        weighted_propagated,
        weight,
        optimize=True,
    )
    full_cross = np.einsum(
        "ia,ib,ij,jb,ja->ab",
        weighted_propagated,
        weight,
        q,
        weighted_propagated,
        weight,
        optimize=True,
    )
    return {
        "identity_self": identity_self,
        "identity_cross": identity_cross,
        "residual_self": full_self - identity_self,
        "residual_cross": full_cross - identity_cross,
        "full_self": full_self,
        "full_cross": full_cross,
    }


def path_residual_probe_sample(
    q: np.ndarray, gamma2: np.ndarray, weight: np.ndarray, probe: np.ndarray
) -> dict[str, np.ndarray]:
    """One unbiased sample of the Q-I ABBA and ABAB residual tables.

    If E[zz^T]=I, then entrywise M_z*M_Ez and M_z*M_Ez.T have expectations
    B_ab^T(Q-I)B_ab and B_ab^T(Q-I)B_ba respectively.
    """

    q = _require_bridge(q)
    n = q.shape[0]
    gamma2 = _require_vector("gamma2", gamma2, n)
    weight = _require_weight(weight, n)
    probe = _require_vector("probe", probe, n)
    propagated = q @ weight
    residual_probe = (q - np.eye(n, dtype=np.float64)) @ probe
    m_probe = propagated.T @ ((gamma2 * probe)[:, None] * weight)
    m_residual_probe = propagated.T @ (
        (gamma2 * residual_probe)[:, None] * weight
    )
    return {
        "residual_self": m_probe * m_residual_probe,
        "residual_cross": m_probe * m_residual_probe.T,
    }


def path_aabb_residual_probe_sample(
    q: np.ndarray, gamma2: np.ndarray, weight: np.ndarray, probe: np.ndarray
) -> np.ndarray:
    """One symmetric unbiased sample of the complete hard AABB path term.

    The ABBA and BAAB self orbits contribute two copies each, while the
    ABAB/BABA orbit contributes four copies.  Symmetrizing inside each sample
    preserves the exact output-exchange law instead of only recovering it in
    expectation.
    """

    sample = path_residual_probe_sample(q, gamma2, weight, probe)
    self_table = sample["residual_self"]
    cross_table = sample["residual_cross"]
    return (
        2.0 * (self_table + self_table.T)
        + 2.0 * (cross_table + cross_table.T)
    )


def path_residual_from_factorization(
    propagated: np.ndarray,
    weight: np.ndarray,
    gamma2: np.ndarray,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> dict[str, np.ndarray]:
    """Contract a supplied symmetric residual factorization exactly.

    With E=U diag(lambda) U^T, one dense output matrix is formed per retained
    mode.  The schedule is O(r n m^2), hence cubic only for bounded r.
    """

    propagated = _require_matrix("propagated", propagated)
    n, outputs = propagated.shape
    weight = _require_weight(weight, n)
    if weight.shape[1] != outputs:
        raise ValueError("propagated and weight output counts must agree")
    gamma2 = _require_vector("gamma2", gamma2, n)
    eigenvalues = _require_vector("eigenvalues", eigenvalues, np.asarray(eigenvalues).size)
    eigenvectors = _require_matrix("eigenvectors", eigenvectors)
    if eigenvectors.shape != (n, eigenvalues.size):
        raise ValueError("factorization shapes do not agree")
    self_table = np.zeros((outputs, outputs), dtype=np.float64)
    cross_table = np.zeros_like(self_table)
    for index, value in enumerate(eigenvalues):
        mode = propagated.T @ (
            (gamma2 * eigenvectors[:, index])[:, None] * weight
        )
        self_table += value * mode * mode
        cross_table += value * mode * mode.T
    return {"residual_self": self_table, "residual_cross": cross_table}


def _tree_path_repeated_exact(
    q: np.ndarray, gamma2: np.ndarray, weight: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    propagated = q @ weight
    pair_diagonal = gamma2[:, None] * propagated * weight
    central_pull = q @ pair_diagonal

    endpoint_singleton = (
        propagated.T @ (gamma2[:, None] * weight * central_pull)
    ).T
    internal_singleton = (
        weight.T @ (gamma2[:, None] * propagated * central_pull)
    ).T
    aaab = 6.0 * (endpoint_singleton + internal_singleton)

    block = pair_diagonal.T @ central_pull
    hard = path_hard_tables_exact(q, gamma2, weight)
    aabb = (
        4.0 * block
        + 2.0 * (hard["full_self"] + hard["full_self"].T)
        + 4.0 * hard["full_cross"]
    )
    return aaab, aabb


def tree_repeated_exact(
    q: np.ndarray,
    gamma2: np.ndarray,
    gamma3: np.ndarray,
    weight: np.ndarray,
) -> dict[str, np.ndarray]:
    """Exact repeated-output tables for the declared weighted tree source.

    The k3, star, AAAB-path, and block-path formulas are cubic.  This reference
    includes the dense ABBA/ABAB contraction and is therefore not a target
    cubic algorithm for a generic full bridge.
    """

    q = _require_bridge(q)
    n = q.shape[0]
    gamma2 = _require_vector("gamma2", gamma2, n)
    gamma3 = _require_vector("gamma3", gamma3, n)
    weight = _require_weight(weight, n)
    propagated = q @ weight

    k3_aab = (
        2.0
        * (gamma2[:, None] * weight * propagated).T
        @ propagated
        + (gamma2[:, None] * propagated * propagated).T @ weight
    )

    star_aaab = (
        3.0
        * (gamma3[:, None] * weight * propagated * propagated).T
        @ propagated
        + (gamma3[:, None] * propagated**3).T @ weight
    )
    star_half = (
        gamma3[:, None] * weight * propagated
    ).T @ (propagated * propagated)
    star_aabb = 2.0 * (star_half + star_half.T)

    path_aaab, path_aabb = _tree_path_repeated_exact(q, gamma2, weight)
    return _repeated_result(
        k3_aab,
        star_aaab + path_aaab,
        star_aabb + path_aabb,
    )


def collision22_hard_exact(paired4: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """Exact 2:2 alternating collision table, including its slot factor two."""

    paired4 = _require_matrix("paired4", paired4)
    n = paired4.shape[0]
    if paired4.shape[1] != n or not np.allclose(
        paired4, paired4.T, rtol=0.0, atol=2.0e-12
    ):
        raise ValueError("paired4 must be square and symmetric")
    weight = _require_weight(weight, n)
    return 2.0 * np.einsum(
        "ia,ib,ij,ja,jb->ab",
        weight,
        weight,
        paired4,
        weight,
        weight,
        optimize=True,
    )


def collision22_probe_sample(
    paired4: np.ndarray, weight: np.ndarray, probe: np.ndarray
) -> np.ndarray:
    """One unbiased sample of the hard 2:2 collision contribution."""

    paired4 = _require_matrix("paired4", paired4)
    n = paired4.shape[0]
    if paired4.shape[1] != n or not np.allclose(
        paired4, paired4.T, rtol=0.0, atol=2.0e-12
    ):
        raise ValueError("paired4 must be square and symmetric")
    weight = _require_weight(weight, n)
    probe = _require_vector("probe", probe, n)
    m_probe = weight.T @ (probe[:, None] * weight)
    m_paired_probe = weight.T @ ((paired4 @ probe)[:, None] * weight)
    return 2.0 * m_probe * m_paired_probe


def collision22_from_factorization(
    weight: np.ndarray, eigenvalues: np.ndarray, eigenvectors: np.ndarray
) -> np.ndarray:
    """Exact hard 2:2 table for a supplied symmetric factorization."""

    weight = _require_matrix("weight", weight)
    n, outputs = weight.shape
    eigenvalues = _require_vector("eigenvalues", eigenvalues, np.asarray(eigenvalues).size)
    eigenvectors = _require_matrix("eigenvectors", eigenvectors)
    if eigenvectors.shape != (n, eigenvalues.size):
        raise ValueError("factorization shapes do not agree")
    answer = np.zeros((outputs, outputs), dtype=np.float64)
    for index, value in enumerate(eigenvalues):
        mode = weight.T @ (eigenvectors[:, index, None] * weight)
        answer += 2.0 * value * mode * mode
    return answer


def collision211_repeated_exact(
    defect211: np.ndarray, weight: np.ndarray
) -> dict[str, np.ndarray]:
    """Small-width oracle for an exact three-label ``[2,1,1]`` defect.

    ``defect211[i,j,k]`` stores the value on the multiset ``{i,i,j,k}`` and
    must be symmetric in ``j,k`` with zero entries whenever labels collide.
    The implementation scatters the twelve slot placements analytically.  It
    intentionally carries the generic tuple-by-output-pair cost and is not a
    target-width compression algorithm.
    """

    defect211 = np.asarray(defect211, dtype=np.float64)
    if defect211.ndim != 3 or len(set(defect211.shape)) != 1:
        raise ValueError("defect211 must be one cubic tensor")
    if not np.all(np.isfinite(defect211)):
        raise ValueError("defect211 must be finite")
    n = defect211.shape[0]
    if not np.allclose(defect211, defect211.swapaxes(1, 2), rtol=0.0, atol=2e-12):
        raise ValueError("defect211 must be symmetric in its singleton labels")
    for repeated in range(n):
        if np.any(defect211[repeated, repeated, :]) or np.any(
            defect211[repeated, :, repeated]
        ) or np.any(np.diag(defect211[repeated])):
            raise ValueError("defect211 must vanish whenever any labels collide")
    weight = _require_weight(weight, n)
    outputs = weight.shape[1]
    aaab = np.zeros((outputs, outputs), dtype=np.float64)
    aabb = np.zeros_like(aaab)
    for repeated in range(n):
        singletons = [index for index in range(n) if index != repeated]
        wi = weight[repeated]
        wi2 = wi * wi
        for left_index, right_index in itertools.combinations(singletons, 2):
            value = defect211[repeated, left_index, right_index]
            if value == 0.0:
                continue
            wj = weight[left_index]
            wk = weight[right_index]
            aaab += value * (
                6.0 * np.outer(wi * wj * wk, wi)
                + 3.0 * np.outer(wi2 * wk, wj)
                + 3.0 * np.outer(wi2 * wj, wk)
            )
            repeated_block = np.outer(wi2, wj * wk)
            split_block = np.outer(wi * wj, wi * wk)
            aabb += value * (
                2.0 * (repeated_block + repeated_block.T)
                + 4.0 * (split_block + split_block.T)
            )
    return {
        "k4_aaaa": np.diag(aaab).copy(),
        "k4_aaab": aaab,
        "k4_aabb": aabb,
    }


def collision_repeated_exact(
    diagonal3: np.ndarray,
    majority3: np.ndarray,
    diagonal4: np.ndarray,
    majority4: np.ndarray,
    paired4: np.ndarray,
    weight: np.ndarray,
) -> dict[str, np.ndarray]:
    """Exact tables for sparse [3]/[2,1]/[4]/[3,1]/[2,2] defects.

    This is the M124 one/two-coordinate collision convention.  It deliberately
    does not claim to include an exact three-label [2,1,1] defect tensor.
    """

    weight = _require_matrix("weight", weight)
    n = weight.shape[0]
    diagonal3 = _require_vector("diagonal3", diagonal3, n)
    diagonal4 = _require_vector("diagonal4", diagonal4, n)
    majority3 = _require_matrix("majority3", majority3)
    majority4 = _require_matrix("majority4", majority4)
    paired4 = _require_matrix("paired4", paired4)
    if majority3.shape != (n, n) or majority4.shape != (n, n) or paired4.shape != (n, n):
        raise ValueError("collision matrices must match the source width")
    if not np.allclose(paired4, paired4.T, rtol=0.0, atol=2.0e-12):
        raise ValueError("paired4 must be symmetric")

    square = weight * weight
    cube = square * weight

    majority3_weight = majority3 @ weight
    k3_aab = (
        (diagonal3[:, None] * square).T @ weight
        + square.T @ majority3_weight
        + 2.0 * (weight * majority3_weight).T @ weight
    )

    majority4_weight = majority4 @ weight
    paired_square = paired4 @ square
    k4_aaab = (
        (diagonal4[:, None] * cube).T @ weight
        + cube.T @ majority4_weight
        + 3.0 * (square * majority4_weight).T @ weight
        + 3.0 * (weight * paired_square).T @ weight
    )

    majority_aabb = (weight * majority4_weight).T @ square
    k4_aabb = (
        (diagonal4[:, None] * square).T @ square
        + 2.0 * (majority_aabb + majority_aabb.T)
        + square.T @ paired_square
        + collision22_hard_exact(paired4, weight)
    )
    return _repeated_result(k3_aab, k4_aaab, k4_aabb)


def rademacher_product_variance(u: np.ndarray, v: np.ndarray) -> float:
    """Exact one-probe variance of (u^T z)(v^T z) for iid Rademacher z."""

    u = np.asarray(u, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    if u.ndim != 1 or v.shape != u.shape:
        raise ValueError("u and v must be equal-length vectors")
    variance = (
        float(u @ u) * float(v @ v)
        + float(u @ v) ** 2
        - 2.0 * float((u * u) @ (v * v))
    )
    return max(0.0, variance)


def flopscope_ledger(
    *,
    probes: int,
    width: int = 256,
    layers: int = 31,
    safety_factor: float = 1.25,
    dense_gemm_dtype: str = "float64",
) -> dict[str, int | float | bool | str | dict[str, int]]:
    """Static contraction ledger for the declared sparse-collision source.

    Twenty-four square-call equivalents cover all exact cubic terms:
    12 tree calls and 12 one/two-coordinate collision calls.  Each probe adds
    two path-residual and two 2:2-collision calls.  The scalar/copy reserves
    match the existing M124 source accounting.  ``dense_gemm_dtype=float32``
    changes only the dense contraction bill; the analytic, response, and copy
    reserves deliberately remain unchanged.  Exact [2,1,1] collision
    corrections and every downstream carrier remain unresolved and uncharged.
    """

    if type(probes) is not int or probes < 0:
        raise ValueError("probes must be a nonnegative integer")
    if type(width) is not int or width <= 0 or type(layers) is not int or layers <= 0:
        raise ValueError("width and layers must be positive integers")
    if not math.isfinite(safety_factor) or safety_factor < 1.0:
        raise ValueError("safety_factor must be finite and at least one")
    if dense_gemm_dtype not in {"float32", "float64"}:
        raise ValueError("dense_gemm_dtype must be 'float32' or 'float64'")

    exact_breakdown = {
        "bridge_transport": 1,
        "k3_tree": 2,
        "k4_stars": 3,
        "k4_path_aaab_and_block": 4,
        "k4_path_identity_hard": 2,
        "k3_sparse_collisions": 3,
        "k4_diagonal_collisions": 2,
        "k4_31_collisions": 4,
        "k4_22_nonhard_collisions": 3,
    }
    probe_breakdown = {
        "k4_path_residual_per_probe": 2 * probes,
        "k4_22_hard_collision_per_probe": 2 * probes,
    }
    exact_calls = sum(exact_breakdown.values())
    probe_calls = sum(probe_breakdown.values())
    square_f32 = 2 * width**3 - width**2
    square_float64 = 2 * square_f32
    square_dense_gemm = (
        square_f32 if dense_gemm_dtype == "float32" else square_float64
    )
    raw_contraction = (exact_calls + probe_calls) * layers * square_dense_gemm
    raw_reserves = {
        "analytic_collision_source_scalars": 4_000_000_000,
        "response_scalar_reserve": 1_600_000_000,
        "copies_allocation_reserve": 1_600_000_000,
    }
    raw_total = raw_contraction + sum(raw_reserves.values())
    return {
        "width": width,
        "layers": layers,
        "probes": probes,
        "square_f32_bill": square_f32,
        "square_float64_bill": square_float64,
        "dense_gemm_dtype": dense_gemm_dtype,
        "square_dense_gemm_bill": square_dense_gemm,
        "safety_factor_once": safety_factor,
        "exact_call_breakdown": exact_breakdown,
        "probe_call_breakdown": probe_breakdown,
        "exact_base_square_calls_per_layer": exact_calls,
        "probe_square_calls_per_layer": probe_calls,
        "raw_contraction_flops": raw_contraction,
        "raw_reserves": raw_reserves,
        "source_raw_flops": raw_total,
        "source_effective_flops": int(math.ceil(raw_total * safety_factor)),
        "exact_three_label_211_collision_charged": False,
        "downstream_carrier_charged": False,
    }
