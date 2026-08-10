"""Assemble the gm_residual_k1 verdict artifact from the three measured pieces."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\scorefloor_generation\terra_m160_hostile_deploy"
    r"\M160_HOSTILE_AUDIT_20260807.json"
)
GATE = 258.4e9


def main() -> None:
    step0 = json.loads((HERE / "step0_results.json").read_text(encoding="utf-8"))
    arm_a = json.loads((HERE / "arm_A_results.json").read_text(encoding="utf-8"))
    old = json.loads(OLD.read_text(encoding="utf-8"))
    diag = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(HERE.glob("diag_threadpool_mask*_pool*.json"))
    }

    def gflops(mask: str, pool: str) -> float:
        return float(diag[f"diag_threadpool_mask{mask}_pool{pool}.json"]["sgemm_gflops"])
    timing = []
    for index, (o, n) in enumerate(zip(old["targets"], arm_a["targets"]), start=1):
        of = o["first_predict"]
        timing.append(
            {
                "worker": index,
                "setup_s_20260807": o["setup_s"],
                "setup_s_arm_a": n["setup_s"],
                "setup_inflation_x": n["setup_s"] / o["setup_s"],
                "backend_s_20260807": of["backend_s"],
                "backend_s_arm_a": n["backend_s"],
                "backend_inflation_x": n["backend_s"] / of["backend_s"],
                "overhead_s_20260807": of["overhead_s"],
                "overhead_s_arm_a": n["overhead_s"],
                "overhead_inflation_x": n["overhead_s"] / of["overhead_s"],
                "residual_s_20260807": of["residual_s"],
                "residual_s_arm_a": n["residual_s"],
                "residual_inflation_x": n["residual_s"] / of["residual_s"],
            }
        )
    result = {
        "id": "gm_residual_k1",
        "mining_search_key": "m157_selfhosted_formal_pilot",
        "ledger_ids_addressed": [
            "m157_selfhosted_formal_pilot",
            "m160_hostile_selfhosted_pilot_audit",
            "m145_defensive_acg_transport",
            "m153_exact_formal_prefix_reuse",
        ],
        "gate": GATE,
        "lambda": 1e11,
        "step0_cached_arithmetic_k1": {
            "verdict": step0["step0_verdict"],
            "max_C_k1": step0["max_C_k1"],
            "max_C_k5": step0["max_C_k5"],
            "k1_pass_count": step0["k1_pass_count"],
            "k5_pass_count": step0["k5_pass_count"],
            "per_worker": [
                {
                    "worker": row["worker"],
                    "billed_flops": row["billed_flops"],
                    "residual_s": row["residual_s"],
                    "C_k1": row["C_k1"],
                    "C_k5": row["C_k5"],
                    "break_even_k": row["break_even_k"],
                    "k1_margin_to_gate": row["k1_margin_to_gate"],
                    "k1_margin_pct": row["k1_margin_pct"],
                    "passes_k1": row["passes_k1"],
                    "passes_k5": row["passes_k5"],
                }
                for row in step0["rows"]
            ],
            "reproduces_ledger_k5_verdict": step0["k5_pass_count"] == 3,
            "independent_recompute_matches_cached_fields": step0["recompute_all_match"],
        },
        "arm_a_1_physical_core_pin": {
            "verdict": arm_a["verdict"],
            "affinity_mask": arm_a["affinity_mask"],
            "max_target_C_k1": arm_a["max_target_C_k1"],
            "max_target_C_k5": arm_a["max_target_C_k5"],
            "max_target_residual_s": arm_a["max_target_residual_s"],
            "k1_pass_count": arm_a["k1_pass_count"],
            "k5_pass_count": arm_a["k5_pass_count"],
            "per_worker": [
                {
                    "worker": row["worker"],
                    "billed_flops": row["billed_flops"],
                    "residual_s": row["residual_s"],
                    "C_k1": row["C_k1"],
                    "C_k5": row["C_k5"],
                    "break_even_k": row["break_even_k"],
                    "k1_margin_to_gate": row["k1_margin_to_gate"],
                    "passes_k1": row["passes_k1"],
                    "second_predict_residual_s": row["second_predict_residual_s"],
                    "second_predict_C_k1": row["second_predict_C_k1"],
                    "second_predict_passes_k1": row["second_predict_passes_k1"],
                    "peak_rss_mib": row["peak_rss_mib"],
                    "setup_s": row["setup_s"],
                }
                for row in arm_a["targets"]
            ],
            "gates": arm_a["gates"],
        },
        "two_signal_verification": {
            "signal_1_independent_recompute": arm_a["gates"][
                "independent_recompute_matches_worker_field"
            ],
            "signal_2_billed_flops_bitwise_reproduce_20260807": arm_a["gates"][
                "billed_flops_reproduce_20260807"
            ],
            "signal_2b_prediction_sha256_reproduce_20260807": arm_a["gates"][
                "prediction_sha256_reproduce_20260807"
            ],
            "signal_3_replay_bitwise_equal_within_worker": arm_a["gates"][
                "replay_bitwise_equal_all"
            ],
            "signal_4_second_predict_independent_residual_draw_all_pass_k1": arm_a[
                "gates"
            ]["second_predict_k1_all_pass"],
            "note": (
                "The arithmetic half of the estimator reproduced BITWISE against "
                "2026-08-07 for all five seeds; only the wall-clock residual moved."
            ),
        },
        "confound_diagnostic": {
            "claim": (
                "ARM A's residual inflation is dominated by BLAS thread-pool "
                "oversubscription introduced by the whole-process pin, not by the "
                "grader's participant-only 1-physical-core pin."
            ),
            "sgemm_1024_f32_gflops_unpinned_default_pool": gflops("0x0", "default"),
            "sgemm_1024_f32_gflops_pinned_0x3_default_pool": gflops("0x3", "default"),
            "sgemm_1024_f32_gflops_pinned_0x3_openblas_num_threads_1": gflops("0x3", "1"),
            "sgemm_1024_f32_gflops_pinned_0x3_openblas_num_threads_2": gflops("0x3", "2"),
            "sgemm_1024_f32_gflops_unpinned_openblas_num_threads_1": gflops("0x0", "1"),
            "pin_cost_actually_inflicted_by_arm_a_x": gflops("0x0", "default")
            / gflops("0x3", "default"),
            "throughput_recovery_from_sizing_pool_to_affinity_x": gflops("0x3", "1")
            / gflops("0x3", "default"),
            "true_cost_of_one_physical_core_x": gflops("0x0", "default")
            / gflops("0x3", "1"),
            "replicate_run_1_console_gflops": {
                "unpinned_default_pool": 195.7818064714739,
                "pinned_0x3_default_pool": 1.4278340722496523,
                "pinned_0x3_pool_1": 69.15984235364357,
                "pinned_0x3_pool_2": 78.24888940393427,
                "unpinned_pool_1": 71.91347037685813,
                "note": "first diagnostic pass; filenames collided, values verbatim from console",
            },
            "raw_diagnostic_files": diag,
            "os_cpu_count_seen_by_openblas_under_pin": 16,
            "worker_level_timing_inflation_vs_20260807": timing,
        },
        "verdict": "PREDECLARED_ARM_A_GATE_FAILED_BUT_INSTRUMENT_PROVEN_CONFOUNDED",
        "gate_result": "INCONCLUSIVE",
        "disposition": (
            "No revival gate opens. The original M157/M160 kill stands unchanged. "
            "The k=1 re-derivation on the FROZEN 2026-08-07 measurements is exact "
            "and passes 5/5, but the fresh pinned re-measurement that the mined "
            "falsifier demanded could not discriminate the mechanism because the "
            "local pin also throttled the FlopScope backend, which the grader gives "
            "7 cores."
        ),
    }
    (HERE / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: result[k] for k in ("verdict", "gate_result")}, sort_keys=True))


if __name__ == "__main__":
    main()
