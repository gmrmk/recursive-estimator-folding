"""gm_c1_bound -- assemble results.json from the gate outputs. No new stats."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(n):
    with open(os.path.join(HERE, n), "r", encoding="utf-8") as fh:
        return json.load(fh)


s0, g1, at, ed = (load("step0.json"), load("g1_bootstrap.json"),
                  load("attack.json"), load("exclusion_direction.json"))
tp = load("tail_probs.json")
lo, hi = g1["CI95_percentile_bootstrap"]
cands = {"kerdock_v3": 1.619e-7, "two_axis_L2": 2.102e-7, "L1_champion": 2.122e-7}
prop = {k: {"local_adjusted": v,
            "hosted_at_R_point": v / g1["R_point"],
            "hosted_band_from_CI": [v / hi, v / lo],
            "hosted_at_R_max_imputed": v / g1["R_max_imputed"],
            "hosted_at_R_median_imputed": v / g1["R_median_imputed"]}
        for k, v in cands.items()}

out = {
 "ledger_id": "c1_local_vs_hosted_calibration",
 "worker": "gm_c1_bound",
 "date_utc": "2026-08-10",
 "source_of_truth": s0["source_file"],
 "compute": "committed-JSON arithmetic + numpy RNG only; zero estimator compute",
 "G0_reproduction": {
   "mean_all25_recomputed": s0["mean_all25_recomputed"],
   "committed_results_adjusted_final_layer_score": s0["published_agg25"],
   "relative_error": s0["G0_1_rel_err"],
   "mean22_recomputed": s0["mean22_recomputed"],
   "published_mean22": s0["published_mean22"],
   "R_point_recomputed": s0["R_point_recomputed"],
   "published_R": s0["published_R"],
   "pass": s0["G0_1_pass"] and s0["G0_2_pass"]},
 "dispersion_of_the_22": {
   "sd_ddof1": s0["sd_A_ddof1"], "CV_of_mean": s0["CV_mean"],
   "relative_variance": s0["relative_variance_v_rel"],
   "max_over_min": s0["spread_max_over_min"],
   "min": s0["min_A"], "median": s0["median_A"], "max": s0["max_A"]},
 "G0b_step0_kill_gate": {
   "CV_kill_threshold": s0["G0b_CV_kill_threshold"],
   "CV_observed": s0["CV_mean"],
   "normal_interval": s0["G0b_normal_interval"],
   "killed": s0["G0b_KILL"]},
 "G1_main_gate": {
   "R_point": g1["R_point"],
   "CI95_percentile_bootstrap_B200k": [lo, hi],
   "one_sigma_bootstrap": g1["one_sigma_R_bootstrap"],
   "SE_analytic_local_only": g1["se_R_local_only"],
   "CI95_normal_analytic": g1["CI95_normal_analytic"],
   "CI95_student_t21_analytic": g1["CI95_student_t21_analytic"],
   "jackknife_SE_R_no_RNG": at["full_22"]["jackknife_se_R"],
   "two_RNG_streams_agree_within_0.01": g1[
       "two_stream_endpoint_agreement_within_0.01"],
   "R_band_claims_unchanged": g1["R_band_claims_unchanged"],
   "bootstrap_prob_R_inside_band": g1["bootstrap_prob_R_inside_band"],
   "CI_inside_band": g1["G1_kill"],
   "CI_width_over_band_width":
       (hi - lo) / (g1["R_band_claims_unchanged"][1]
                    - g1["R_band_claims_unchanged"][0]),
   "bootstrap_tail_probabilities_two_streams": tp,
   "verdict": g1["G1_verdict"]},
 "exclusion_bias": {
   "n_excluded": s0["n_excluded"],
   "excluded_names": s0["excluded_names"],
   "excluded_effective_compute": s0["excluded_effective_compute"],
   "completed_max_effective_compute": s0["completed_max_effective_compute"],
   "completed_mean_effective_compute": s0["completed_mean_effective_compute"],
   "excluded_are_top3_effective_compute":
       s0["excluded_are_top3_effective_compute"],
   "R_median_imputed": g1["R_median_imputed"],
   "R_max_imputed": g1["R_max_imputed"],
   "predeclared_bias_up_test_R_max_imp_gt_R": g1["exclusion_bias_is_upward"],
   "DIRECTION_NOT_SUPPORTED_BY_DATA": {
     "spearman_effcompute_vs_adjusted_within_22":
         ed["spearman_effcompute_vs_adjusted"],
     "permutation_p_two_sided_runA": ed["permutation_null_run_A"][
         "p_two_sided"],
     "permutation_p_two_sided_runB": ed["permutation_null_run_B"][
         "p_two_sided"],
     "pearson": ed["pearson_effcompute_vs_adjusted"],
     "spearman_flops_vs_adjusted": ed["spearman_flopsused_vs_adjusted"],
     "note": "median-imputed R = %.4f is BELOW the point R = %.4f; the mined "
             "'1.652 is a lower bound' reading is an assumption, not a "
             "measurement" % (g1["R_median_imputed"], g1["R_point"])}},
 "attack_outlier_robustness": {
   "attack_lands": at["attack_lands"],
   "drop_top1_n21": {"R": at["drop_top1_21"]["R"],
                     "ci95": at["drop_top1_21"]["ci95"]},
   "drop_top2_n20": {"R": at["drop_top2_20"]["R"],
                     "ci95": at["drop_top2_20"]["ci95"]},
   "trim_min_max_n20": {"R": at["trim_min_and_max_20"]["R"],
                        "ci95": at["trim_min_and_max_20"]["ci95"]}},
 "downstream_propagation": prop,
 "parity_claim": {
   "oabuod_adjusted": 9.45e-8,
   "parity_band_from_C1_own_predeclaration": [0.8, 1.25],
   "P_at_R_point": g1["parity_ratio_at_R_point"],
   "P_at_CI_lo": g1["parity_ratio_at_CI_lo"],
   "P_at_CI_hi": g1["parity_ratio_at_CI_hi"],
   "claim_holds_across_CI": g1["G1_kill"]},
 "G2_mined_reproduction": g1["G2_mined_reproduction"],
 "mined_expectations": {"CI": [1.04, 2.42], "one_sigma": 0.36,
                        "R_max_imputed": 2.36, "relative_variance": 1.07,
                        "max_over_min": 22.4},
 "GATE_RESULT": "REVIVED_PASS" if g1["G1_verdict"] == "REVIVED_PASS"
                else g1["G1_verdict"],
}
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out["downstream_propagation"], indent=1))
print("GATE_RESULT", out["GATE_RESULT"])
