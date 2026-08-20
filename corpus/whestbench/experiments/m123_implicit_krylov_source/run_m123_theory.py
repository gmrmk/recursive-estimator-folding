"""Generated-only identity and static cost runner for M123 pretheory."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

from m123_orbit_fusion import (
    HARD_ORBITS,
    REPRESENTATIVES,
    dense_representative,
    equivariant_start_block,
    full_fused_matrix_small,
    fused_mode1_gram_apply,
    orbit_matrix_formula,
)

M122_DIR = Path(__file__).resolve().parents[1] / "m122_tree_factor_theory"
sys.path.insert(0, str(M122_DIR))
from m122_tree_factor import mode1_gram, tree4_tensor  # noqa: E402


def generated_q(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(n, n)) / math.sqrt(n)
    c = w @ w.T
    d = np.sqrt(np.diag(c))
    rho = c / np.outer(d, d)
    q = np.tanh(0.8 * rho)
    np.fill_diagonal(q, 1.0)
    return q


def mm(m: int, k: int, n: int) -> int:
    return 2 * m * k * n - m * n


def main() -> None:
    worst_orbit = 0.0
    worst_full = 0.0
    worst_mv = 0.0
    for n in range(2, 9):
        q = generated_q(n, 123600 + n)
        for orbit in range(16):
            worst_orbit = max(
                worst_orbit,
                float(np.max(np.abs(dense_representative(q, orbit) - orbit_matrix_formula(q, orbit)))),
            )
        dense = mode1_gram(tree4_tensor(q))
        fused = full_fused_matrix_small(q)
        x = np.random.default_rng(123700 + n).normal(size=n)
        worst_full = max(worst_full, float(np.max(np.abs(dense - fused))))
        worst_mv = max(worst_mv, float(np.max(np.abs(dense @ x - fused_mode1_gram_apply(q, x)))))

    q8 = generated_q(8, 123808)
    rng8 = np.random.default_rng(123809)
    permutation = rng8.permutation(8)
    x8 = rng8.normal(size=8)
    perm_operator_defect = float(
        np.max(
            np.abs(
                fused_mode1_gram_apply(q8[np.ix_(permutation, permutation)], x8[permutation])
                - fused_mode1_gram_apply(q8, x8)[permutation]
            )
        )
    )
    u8 = equivariant_start_block(q8)
    up8 = equivariant_start_block(q8[np.ix_(permutation, permutation)])
    perm_projector_defect = float(
        np.max(np.abs((u8 @ u8.T)[np.ix_(permutation, permutation)] - up8 @ up8.T))
    )
    scale = rng8.uniform(0.2, 2.0, size=8)
    gauge = rng8.uniform(0.2, 3.0, size=8)
    gauge_defect = float(
        np.max(np.abs((gauge * scale)[:, None] * u8 - gauge[:, None] * (scale[:, None] * u8)))
    )
    identity_tie_fails_closed = False
    try:
        equivariant_start_block(np.eye(8))
    except FloatingPointError:
        identity_tie_fails_closed = True

    n = 256
    layers = 31
    block = 4
    easy_setup_gemm = 19
    hard_gemm_per_vector = 8
    f32_square = mm(n, n, n)
    f64_square = 2 * f32_square
    safety = 1.25
    strassen_credit = 0.779
    setup_calls = layers * easy_setup_gemm
    one_apply_calls = layers * block * hard_gemm_per_vector
    one_pass_calls = setup_calls + one_apply_calls
    two_pass_calls = setup_calls + 2 * one_apply_calls

    def charged(calls: int, credit: float = 1.0) -> float:
        return calls * f64_square * safety * credit

    result = {
        "schema": 1,
        "firewall": "generated algebra and static cost only; no contest/public/private weights, scorer, labels, outcomes, champion, or submission",
        "identity_defects": {
            "max_16_representative_orbits_n2_to_n8": worst_orbit,
            "max_full_fused_gram_n2_to_n8": worst_full,
            "max_full_fused_matvec_n2_to_n8": worst_mv,
            "permutation_operator": perm_operator_defect,
            "permutation_start_projector": perm_projector_defect,
            "positive_gauge_restoration": gauge_defect,
            "identity_bridge_rank_tie_fails_closed": identity_tie_fails_closed,
        },
        "orbit_partition": {
            "fused_orbits": len(REPRESENTATIVES),
            "original_ordered_path_pairs": sum(item[2] for item in REPRESENTATIVES),
            "hard_orbits": list(HARD_ORBITS),
        },
        "fixed_schedule": {
            "width": n,
            "source_layers": layers,
            "block_size": block,
            "easy_setup_square_gemms_per_layer": easy_setup_gemm,
            "hard_square_gemms_per_vector_per_apply": hard_gemm_per_vector,
            "square_f32_shape_bill": f32_square,
            "square_float64_shape_bill": f64_square,
            "safety_factor_once": safety,
            "setup_calls_all_layers": setup_calls,
            "one_block_apply_calls_all_layers": one_apply_calls,
            "static_start_plus_one_certificate_apply_charged": charged(one_pass_calls),
            "minimal_nontrivial_krylov_plus_residual_two_apply_charged": charged(two_pass_calls),
            "conditional_strassen_credit": strassen_credit,
            "static_one_apply_best_case_strassen": charged(one_pass_calls, strassen_credit),
            "nontrivial_two_apply_best_case_strassen": charged(two_pass_calls, strassen_credit),
            "incremental_headroom": 152_000_000_000,
        },
        "already_audited_additional_source_lower_bounds": {
            "m121_31_tree_core_queries_charged": 14_018_150_400,
            "m121_31_source_transports_charged": 40_632_320,
            "m121_dense_deltaV_CP_pairing_shape_sum": 16_641_000_000,
            "excluded_positive_costs": [
                "nonzero-mean star-tree orbit actions",
                "exact one/two-coordinate collision cores",
                "bivariate normal response scalar work",
                "buffer operations and CP concatenation",
                "residual wall-time charge",
            ],
        },
        "decision": "KILL_M123_FIXED_BLOCK_KRYLOV: the minimal nontrivial degree-1 block-Lanczos factor plus a fail-closed residual needs two Gram block applications; the zero-mean path subset alone costs 167.810B even granting the uncertified 0.779 Strassen credit, above 152B before every source/core/response cost. Preserve the exact 16-orbit/3-hard-orbit operator for a different static Tucker or reduced-layer mutation.",
    }
    destination = Path(__file__).with_name("results.json")
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    Path(__file__).with_name("RESULTS.sha256").write_text(f"{digest}  results.json\n", encoding="ascii")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
