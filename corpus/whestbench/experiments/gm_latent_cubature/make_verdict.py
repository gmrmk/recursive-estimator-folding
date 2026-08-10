"""Assemble results.json: gates, seals, and uncertainty on the eight cases.

No new arms and no new runs -- this only summarises the already-collected
case records with a case-level bootstrap and a paired sign-flip permutation
null on the log ratio.
"""

from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from frozen_paths import HERE

bank = json.loads((HERE / "bank_results.json").read_text(encoding="utf-8"))
step0 = json.loads((HERE / "step0_arithmetic.json").read_text(encoding="utf-8"))
cross = json.loads((HERE / "step0_crosscheck.json").read_text(encoding="utf-8"))
inv = json.loads((HERE / "invariance_results.json").read_text(encoding="utf-8"))

cases = bank["cases"]
base = np.array([c["baseline_mse"] for c in cases])
cand = np.array([c["candidate_mse"] for c in cases])
ratio = float(cand.sum() / base.sum())
wins = int(sum(1 for c in cases if c["win"]))

rng = np.random.default_rng(20260810)
B = 200_000
idx = rng.integers(0, len(cases), size=(B, len(cases)))
boot = cand[idx].sum(axis=1) / base[idx].sum(axis=1)
ci_lo, ci_hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
p_boot_below_gate = float(np.mean(boot <= 0.80))

# paired sign-flip permutation null: H0 = candidate and comparator exchangeable
log_ratio = np.log(cand / base)
signs = rng.choice([-1.0, 1.0], size=(B, len(cases)))
null_mean = (signs * log_ratio).mean(axis=1)
observed_mean = float(log_ratio.mean())
p_perm_two_sided = float(np.mean(np.abs(null_mean) >= abs(observed_mean)))

# exact binomial for wins under a fair-coin null
n = len(cases)
p_wins_ge_6 = sum(math.comb(n, k) for k in range(6, n + 1)) / 2**n

gate1 = ratio <= 0.80
gate2 = wins >= 6
gate3 = bool(inv["passes"])
gate4_f64 = not step0["gate4_kill_under_float64"]
gate4_f32 = not step0["gate4_kill_under_float32"]

result = {
    "schema": 1,
    "experiment": "gm_latent_cubature",
    "mining_key": "latent_sparse_radial_cubature",
    "ledger_record": "corpus/whestbench/headroom/fold_ledger.json candidate index 11",
    "verdict": "KILL_CONFIRMED",
    "verdict_basis": "gate1 and gate2 both fail on the full eight-case frozen bank",
    "predeclared_prediction": {
        "gate1_aggregate_ratio": "FAIL, point prediction R in [1.0,3.0] centred ~1.3",
        "gate2_wins": "FAIL, point prediction W <= 3 of 8",
        "gate3_invariance": "PASS",
        "gate4_step0_arithmetic": "PASS, both dtype readings well below 80e9",
        "overall": "KILL_CONFIRMED",
    },
    "gates": {
        "gate1_aggregate_ratio_at_most_0_80": {
            "value": ratio,
            "threshold": 0.80,
            "passes": bool(gate1),
        },
        "gate2_wins_at_least_6_of_8": {
            "value": wins,
            "threshold": 6,
            "passes": bool(gate2),
        },
        "gate3_permutation_and_scale_equivariance": {
            "permutation_relative_max_error": inv["revived"]["permutation"][
                "relative_max_error"
            ],
            "positive_scale_relative_max_error": max(
                c["relative_max_error"]
                for c in inv["revived"]["positive_scale"]["network_cells"]
            ),
            "ranks_equal": inv["revived"]["permutation"]["ranks_equal"],
            "tolerance": 1e-10,
            "passes": gate3,
        },
        "gate4_conservative_target_arithmetic_below_80e9": {
            "float64_billed": step0["billed"]["float64_no_contingency"],
            "float32_billed_with_25pct_contingency": step0["billed"][
                "float32_with_25pct_contingency"
            ],
            "threshold": 80_000_000_000,
            "passes_under_float64": bool(gate4_f64),
            "passes_under_float32": bool(gate4_f32),
            "note": "dtype-conditional; the frozen candidate is float64 and "
            "FlopScope 0.10.0 bills float64 at rate 2.0",
        },
    },
    "uncertainty": {
        "method": "case-level nonparametric bootstrap, B=200000, seed 20260810",
        "aggregate_ratio": ratio,
        "aggregate_ratio_ci95": [ci_lo, ci_hi],
        "bootstrap_probability_ratio_at_most_0_80": p_boot_below_gate,
        "paired_sign_flip_permutation_p_two_sided_on_mean_log_ratio": p_perm_two_sided,
        "observed_mean_log_ratio": observed_mean,
        "exact_binomial_p_wins_ge_6_under_fair_coin": p_wins_ge_6,
    },
    "per_case": [
        {
            "depth": c["depth"],
            "seed": c["seed"],
            "baseline_mse": c["baseline_mse"],
            "candidate_mse": c["candidate_mse"],
            "ratio": c["ratio"],
            "win": c["win"],
            "rank_min": c["trace_summary"]["rank_min"],
            "rank_max": c["trace_summary"]["rank_max"],
            "children_max_per_layer": c["trace_summary"]["children_max_per_layer"],
        }
        for c in cases
    ],
    "aggregate": bank["aggregate"],
    "seals": {
        "seal1_comparator_independent_recompute_max_abs_delta": bank["seals"][
            "seal1_comparator_recompute_max_abs_prediction_delta"
        ],
        "seal1_banked_baseline_mse_max_abs_delta": bank["seals"][
            "seal1_banked_baseline_mse_max_abs_delta"
        ],
        "seal1_passes": bank["seals"]["seal1_passes"],
        "seal2_repair_neutrality_max_relative_mse_delta": bank["seals"][
            "seal2_max_relative_mse_delta"
        ],
        "seal2_detail": bank["seals"]["seal2_repair_neutrality"],
        "seal2_passes": bank["seals"]["seal2_passes"],
        "seal3_bit_repeat_all_identical": bank["seals"]["seal3_passes"],
        "step0_two_signal_agreement": cross["same_side_of_threshold_as_static"],
    },
    "refreeze_against_retained_hashes": {
        "candidate_sha256_measured": bank["frozen_hashes"][
            "latent_sparse_cubature.py"
        ],
        "candidate_sha256_retained": bank["retained_hashes_expected"]["candidate"],
        "contract_sha256_measured": bank["frozen_hashes"]["premise_contract.json"],
        "contract_sha256_retained": bank["retained_hashes_expected"]["contract"],
        "match": bool(
            bank["frozen_hashes"]["latent_sparse_cubature.py"]
            == bank["retained_hashes_expected"]["candidate"]
            and bank["frozen_hashes"]["premise_contract.json"]
            == bank["retained_hashes_expected"]["contract"]
        ),
        "truth_bank_sha256": bank["frozen_hashes"]["fresh_n64_results.json"],
    },
    "resource_containment": bank["resources"],
    "resource_contrast_with_killed_harness": {
        "original_peak_working_set": "24.6 GB and 13.8 GB, externally stopped",
        "original_cases_completed": 3,
        "revived_max_peak_working_set_bytes": bank["resources"][
            "max_peak_working_set_bytes"
        ],
        "revived_cases_completed": 8,
        "nonreturning_case_seed_18563_now_completes": True,
    },
    "step0_detail": {
        "static": {
            k: step0[k]
            for k in (
                "installed_weights",
                "installed_dtype_rates",
                "measured_unit_cost_derivations",
                "arithmetic_raw_ops_total",
                "data_movement_raw_ops_total",
                "raw_ops_total",
                "billed",
                "verdict",
            )
        },
        "crosscheck": {
            k: cross[k]
            for k in (
                "observations",
                "extrapolation",
                "data_movement_share_of_raw_worst_case",
                "data_movement_share_of_raw_observed",
                "billed_float64_observed",
                "billed_float32_observed_with_25pct",
                "gather_heavy_hypothesis",
            )
        },
    },
    "firewall": {
        "truth_generation": "none; banked truth vectors only",
        "whest_data_scorer_holdout_api_network": "not accessed",
        "frozen_sources_edited": "none; loaded by path, reducer replaced by "
        "in-process monkeypatch only",
        "git": "no git commands run",
        "writes": "confined to corpus/whestbench/experiments/gm_latent_cubature/",
    },
}

(HERE / "results.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result["gates"], indent=2))
print(json.dumps(result["uncertainty"], indent=2))
print("refreeze match:", result["refreeze_against_retained_hashes"]["match"])
