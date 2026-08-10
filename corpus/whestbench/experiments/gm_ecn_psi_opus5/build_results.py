"""Consolidate the gm_ecn_psi verdict record from the three step artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(name: str) -> str:
    h = hashlib.sha256()
    h.update((HERE / name).read_bytes())
    return h.hexdigest()


s1 = json.loads((HERE / "step1_results.json").read_text(encoding="utf-8"))
s2 = json.loads((HERE / "step2_results.json").read_text(encoding="utf-8"))
s3 = json.loads((HERE / "step3_crosscheck.json").read_text(encoding="utf-8"))

out = {
    "schema": "gm-ecn-psi-verdict-v1",
    "graveyard_item": "gm_ecn_psi",
    "mining_search_key": "ecn_exact_jspace_psi_streaming",
    "ledger_record": {
        "file": "corpus/whestbench/headroom/fold_ledger.json",
        "index": 35,
        "id": "ecn_exact_jspace_psi_streaming",
        "status_before": "proposed",
        "status_after_this_run": "measured_and_killed",
        "parent_index": 34,
        "parent_id": "ecn_jacobian_maxent_compressor",
        "parent_status": "killed",
    },
    "gate_result": "KILL_CONFIRMED",
    "predicted_on_record": {
        "step1": "PASS, max relative error below 1e-8",
        "step2": "FAIL both gates; exact-psi ratio in [0.85, 1.05], above 0.8942 and far above 0.80",
        "expected_gain_for_score": "ZERO",
    },
    "observed": {
        "step1": "PASS",
        "step2": "FAIL both gates; exact-psi ratio 1.0064508507414671, worse than generic and worse than the surrogate on 32/32 units",
    },
    "step1_jacobian_central_difference": s1,
    "step2_exact_psi_swap": s2,
    "step3_crosscheck": s3,
    "decisive_numbers": {
        "step1_max_rel_err_alpha_block": s1["max_rel_err"]["G1A_alpha_block_h1e-5"],
        "step1_max_rel_err_ell_block": s1["max_rel_err"]["G1B_ell_block_h1e-5"],
        "step1_gauss_legendre_vs_frozen_observable": s1["max_rel_err"][
            "G1C_gl_vs_frozen_observable"
        ],
        "frozen_surrogate_noladder_ratio": s2["aggregate_ratio_vs_generic"][
            "jacobian_maxent"
        ],
        "exact_psi_ratio": s2["aggregate_ratio_vs_generic"]["jacobian_exact_psi"],
        "exact_psi_ratio_ci95": s2["bootstrap"]["exact_psi_ratio_ci95"],
        "exact_psi_wins_vs_generic": s2["wins"]["exact_psi_vs_generic"],
        "exact_psi_wins_vs_surrogate_noladder": s2["wins"][
            "exact_psi_vs_surrogate_noladder"
        ],
        "paired_ratio_difference_point": s2["bootstrap"][
            "paired_ratio_difference_point"
        ],
        "paired_ratio_difference_ci95": s2["bootstrap"]["paired_ratio_difference_ci95"],
        "paired_sign_test_two_sided_p": s2["paired_sign_test_exact_vs_surrogate"][
            "two_sided_p"
        ],
        "explicit_matrix_crosscheck_max_rel_diff": s3[
            "explicit_matrix_vs_vectorised_distance"
        ]["max_rel_diff_offdiag"],
        "cached_reference_reproduction_rel_diff": s2["reproduction_of_frozen_cache"][
            "noladder_ratio_rel_diff"
        ],
    },
    "two_signal_verification": {
        "signal_1_cached_reference_bit_exact": True,
        "signal_2_independent_explicit_matrix_recomputation": True,
        "signal_3_bit_repeat_identical_sha256": "cde475ceba8ad3a2511ba76aa6d49d9e5766dbbfc4d27c9c514268faf743b784",
        "signal_4_judge_bootstrap_agreement": s3[
            "judge_bootstrap_independent_agreement"
        ],
    },
    "deployment": {
        "status": "closed, untouched",
        "target_geometry_flops_4Ksq_p_at_K3072_p512": 19327352832,
        "judge_projected_total_flops": 89924567040,
        "ceiling_flops": 80000000000,
        "cost_mutation_attempted": False,
    },
    "deviations": [
        "Frozen implementation imported read-only from work/scorefloor_generation/ecn_jacobian_maxent_compressor/experiment.py (outside the publish repo); never copied or edited. Declared in PREDECLARATION.md section 0 before any code.",
        "No other deviation: no added arm, no retuned gate, no data-selected constant, no scale-down.",
    ],
    "firewall": {
        "synthetic_frozen_generator_only": True,
        "competition_or_truth_or_scorer_read": False,
        "network_or_submission": False,
        "git_commands": False,
        "m245_M243_M244_touched": False,
    },
    "artifact_sha256": {
        name: sha(name)
        for name in (
            "PREDECLARATION.md",
            "step1_jacobian_cd.py",
            "step1_results.json",
            "step2_psi_swap.py",
            "step2_results.json",
            "step3_crosscheck.py",
            "step3_crosscheck.json",
            "VERDICT.md",
        )
    },
}

(HERE / "results.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(out["decisive_numbers"], indent=2, sort_keys=True))
print(out["gate_result"])
