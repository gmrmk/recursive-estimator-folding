"""Run generated-only M122 algebra checks and record arithmetic quantities."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from m122_tree_factor import (
    all_path_pair_widths,
    crossed_middle_gram_dense,
    crossed_middle_gram_formula,
    crossed_middle_matvec_formula,
    four_core_from_paths,
    mode1_gram,
    tree3_mode1_gram_formula,
    tree3_tensor,
    tree4_tensor,
)


def generated_bridge(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(n, n)) / math.sqrt(n)
    raw = w @ w.T
    scale = np.sqrt(np.diag(raw))
    rho = raw / np.outer(scale, scale)
    q = np.tanh(0.8 * rho)
    np.fill_diagonal(q, 1.0)
    return q


def matmul_bill(m: int, k: int, n: int) -> int:
    return 2 * m * k * n - m * n


def main() -> None:
    worst_g3 = 0.0
    worst_hard_gram = 0.0
    worst_hard_mv = 0.0
    worst_core = 0.0
    for n in range(2, 9):
        q = generated_bridge(n, 122600 + n)
        g3_dense = mode1_gram(tree3_tensor(q))
        worst_g3 = max(worst_g3, float(np.max(np.abs(g3_dense - tree3_mode1_gram_formula(q)))))

        hard_dense = crossed_middle_gram_dense(q)
        hard_formula = crossed_middle_gram_formula(q)
        x = np.random.default_rng(122700 + n).normal(size=n)
        worst_hard_gram = max(worst_hard_gram, float(np.max(np.abs(hard_dense - hard_formula))))
        worst_hard_mv = max(
            worst_hard_mv,
            float(np.max(np.abs(hard_dense @ x - crossed_middle_matvec_formula(q, x)))),
        )

        r = min(3, n)
        u = np.random.default_rng(122800 + n).normal(size=(n, r))
        dense_core = np.einsum("ijkl,ip,jq,kr,ls->pqrs", tree4_tensor(q), u, u, u, u, optimize=True)
        worst_core = max(worst_core, float(np.max(np.abs(dense_core - four_core_from_paths(q, u)))))

    n = 256
    nn = n * n
    n3 = n**3
    n4 = n**4
    n5 = n**5
    hard_direct = matmul_bill(n, nn, n)
    full_gram_direct = matmul_bill(n, n**3, n)
    qmv = matmul_bill(n, n, 1)
    core_paths = math.comb(4 + 3, 4) * 12 * 3
    tree_core_raw = core_paths * qmv
    report = {
        "schema": 1,
        "firewall": "generated algebra only; no contest weights, scorer, labels, submissions, or outcome grid",
        "small_width_max_abs_defects": {
            "tree3_mode1_gram_formula": worst_g3,
            "crossed_middle_explicit_gram": worst_hard_gram,
            "crossed_middle_implicit_matvec": worst_hard_mv,
            "tree4_path_core": worst_core,
        },
        "all_144_path_pair_matvec_post_b_treewidth": all_path_pair_widths(),
        "target_n256_ledger": {
            "n3": n3,
            "n4": n4,
            "n5": n5,
            "float64_tensor4_bytes": n4 * 8,
            "float64_tensor4_gib": n4 * 8 / 2**30,
            "direct_mode1_gram_shape": [[n, n**3], [n**3, n]],
            "direct_mode1_gram_f32_bill": full_gram_direct,
            "direct_mode1_gram_float64_x2_contingency": int(math.ceil(full_gram_direct * 2.0 * 1.25)),
            "crossed_middle_kr_shape": [[n, nn], [nn, n]],
            "crossed_middle_kr_factor_bytes_each_float64": nn * n * 8,
            "crossed_middle_kr_two_factors_mib": 2 * nn * n * 8 / 2**20,
            "crossed_middle_direct_f32_bill": hard_direct,
            "crossed_middle_direct_float64_x2_contingency": int(math.ceil(hard_direct * 2.0 * 1.25)),
            "rank4_symmetric_tree_core_entries": math.comb(4 + 3, 4),
            "rank4_tree_core_q_matvecs": core_paths,
            "rank4_tree_core_f32_bill_exact_shape": tree_core_raw,
            "rank4_tree_core_float64_x2_contingency": int(math.ceil(tree_core_raw * 2.0 * 1.25)),
            "k3_closed_form_dense_nxn_matmul_upper_count": 5,
            "k3_closed_form_float64_x2_contingency_upper": int(math.ceil(5 * matmul_bill(n, n, n) * 2.0 * 1.25)),
        },
        "decision": "REPAIR_ONLY: exact k3 Gram and exact k4 projected core are validated; k4 mode-Gram factor construction is not yet a target-valid fixed-cost rank-4 HOSVD because full Gram has a generic Khatri-Rao n^4 obstruction and an implicit Krylov implementation has not been fused, fixed, or costed.",
    }
    destination = Path(__file__).with_name("results.json")
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    Path(__file__).with_name("RESULTS.sha256").write_text(f"{digest}  results.json\n", encoding="ascii")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
