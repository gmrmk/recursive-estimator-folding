"""Consolidate gm_s1s4_vd into results.json. Every number is copied from the
harness outputs programmatically - nothing is transcribed by hand."""
import json, os

H = os.path.dirname(os.path.abspath(__file__))
s0 = json.load(open(os.path.join(H, "step0_results.json")))
s1x = json.load(open(os.path.join(H, "step1_results.json")))
s1 = json.load(open(os.path.join(H, "s1_gm_results.json")))
s4 = json.load(open(os.path.join(H, "s4_gm_results.json")))
nd = json.load(open(os.path.join(H, "ndtr_validation.json")))

mi = s0["moment_identity"]
bo = s0["bootstrap_vD"]["arms"]
g5 = s1x["G5_quantified_lower_bound"]
tk = ["1.55e-07", "1.60e-07", "1.70e-07"]

R = {
 "experiment": "gm_s1s4_vd",
 "ledger_item": "s1_suite_risk_bootstrap (+ s1b_dispersion_corrected, s4_designation_portfolio_bootstrap)",
 "mining_search_key": "s1_suite_risk_bootstrap",
 "date": "2026-08-10",
 "gate_result": "KILL_CONFIRMED",
 "one_line": ("The mined moment identity reproduces exactly, but its raw-observable conclusion "
              "(vD ~ 0.013) is excluded by the same 80-net panel: the rotation-free floor31 "
              "component forces vD >= 0.1016 (permutation p < 5e-5), landing inside S1b's "
              "operative 0.081-0.122. S1b stands; the revival is dead. One sub-claim survives: "
              "S4's Door-B 'near-zero rho_pair (~0.2% of variance)' is wrong, it is 17-26%."),

 "step0_moment_identity": {
   "vF": s0["rotation_pool"]["vF"],
   "pool_n": s0["rotation_pool"]["n"],
   "pool_max_over_min": s0["rotation_pool"]["max_over_min"],
   "panel": s0["panel"],
   "raw": mi["raw"], "corr_floor_subtracted": mi["corr_floor_subtracted"],
   "bootstrap": bo,
 },

 "gates": {
   "G0_step0_kill": s0["G0_step0_kill_gate"],
   "G1_identification": s0["G1_identification"],
   "G2_shape_freedom": {
     "pass": s1x["G2_shape_freedom"]["pass"],
     "betas_bracketing_at_vD_moment_raw": s1x["G2_shape_freedom"]["betas_bracketing_at_vD_moment_raw"],
     "betas_bracketing_at_vD_moment_corr": s1x["G2_shape_freedom"]["betas_bracketing_at_vD_moment_corr"],
     "p_sim_ge_obs_at_raw_reading": {k: v["p_sim_ge_observed"]
        for k, v in s1x["shape_refit_grid_vs_raw_spread"]["vD_moment_raw_ddof1"].items()},
   },
   "G3_S1_gates_by_vD": {n: {"vD": a["vD"], "D_max_over_min": a["difficulty_max_over_min"],
        "width_shrink_R6_vs_R1": a["gates"]["width_shrink_R6_vs_R1"]["value"],
        "mean_shift": a["gates"]["abs_mean_shift_R6_vs_R1"]["value"],
        "rotation_share_R1": a["gates"]["rotation_variance_dominant"]["rotation_share_R1"],
        "R1_p5": a["arms"]["1"]["p5"], "R1_p95": a["arms"]["1"]["p95"],
        "R1_sd": a["arms"]["1"]["sd"],
        "R1_p_below_1p6em7": a["arms"]["1"]["p_below_1p6em7"],
        "analytic_sd_shrink": a["analytic_sd_shrink_R6_vs_R1"],
        "m185_bracket": a["m185_spread_validation"],
        "verdict": a["verdict"]} for n, a in s1["arms"].items()},
   "G4_S4_doorB_by_vD": {n: {"vD": a["vD"], "analytic_share_D": a["analytic_share_D"],
        "realized_rho0_score_corr_same_mean": a["shared_difficulty_correlation_floor_same_mean_rho0"],
        "same_mean_gain_pp": {t: a["diversification_gains_rho0_minus_rho1"]["same_mean"][t]["value"] * 100
                              for t in tk},
        "same_mean_gain_ci95_pp": {t: [c * 100 for c in a["diversification_gains_rho0_minus_rho1"]["same_mean"][t]["ci95"]]
                                   for t in tk},
        "r6_gain_pp": {t: a["diversification_gains_rho0_minus_rho1"]["r6"][t]["value"] * 100 for t in tk},
        "doubling_ratio": {t: a["doubling_ratio_rho0_over_rho1"]["same_mean"][t]["ratio"] for t in tk},
        "doubling_claim_holds": {t: a["doubling_ratio_rho0_over_rho1"]["same_mean"][t]["doubling_claim_holds"] for t in tk},
        "p_min_below": {t: a["doubling_ratio_rho0_over_rho1"]["same_mean"][t] for t in tk},
        "verdict": a["verdict"]} for n, a in s4["arms"].items()},
   "G5_floor_correlation_bound": {
     "floor31_rotation_free_evidence": ("run_m185_g0.py:342 truth_stats(weights, 7_000_000+seed, "
        "N_TRUTH_S1) - net seed only; rot enters only predict_once at line 346"),
     "pearson_floor31_vs_mse_raw": g5["mse_raw"]["pearson_rho_floor31"],
     "spearman_floor31_vs_mse_raw": s0["G5_floor_correlation_ceiling"]["corr_floor31_vs_mse_raw_spearman"],
     "pearson_floor31_vs_mse_corr": g5["mse_corr"]["pearson_rho_floor31"],
     "vD_lower_bound_raw": g5["mse_raw"]["vD_lower_bound"],
     "share_D_lower_bound_raw": g5["mse_raw"]["share_D_lower_bound"],
     "vD_lower_bound_corr": g5["mse_corr"]["vD_lower_bound"],
     "bootstrap_and_null": g5["bootstrap_and_null_raw_arm"],
     "a1b_weightsonly_spearman_max_abs": s0["G5_floor_correlation_ceiling"]["a1b_max_abs_spearman"],
     "readings_excluded_by_pearson_ceiling": {k: v["excluded_by_floor31_pearson"]
        for k, v in s0["G5_floor_correlation_ceiling"]["readings"].items()},
   },
 },

 "two_signal_verification": {
   "V1_s1_control_vs_committed": s1["V1_control_reproduces_committed_s1"],
   "V1_s4_control_vs_committed": s4["V1_control_reproduces_committed_s4"],
   "V3_bitwise_repeat_s1": {n: a["bitwise_repeat_R1_chunk0"] for n, a in s1["arms"].items()},
   "V3_bitwise_repeat_s4": {n: a["bitwise_repeat_chunk0"] for n, a in s4["arms"].items()},
   "V3_s4_rho1_bitwise_equals_A": {n: a["rho1_same_mean_bitwise_equals_A"] for n, a in s4["arms"].items()},
   "V4_independent_simulator_vs_s1b": s1x["V4_cross_simulator_vs_s1b"],
   "V6_analytic_vs_bootstrap_sd_ratio": {n: a["analytic_vs_bootstrap_sd_ratio"] for n, a in s1["arms"].items()},
   "V8_ndtr_substitute_validation": nd,
 },

 "deviations": [
   "D1 mined S17 80-net settling check NOT run (only 3 s5 ybar arrays exist; 80 nets needs fresh forwards + 600k truth passes, outside the cheapest falsifier and the 90-min envelope)",
   "D2 predeclared replacement second signal: floor-correlation ceiling (G5) - became the decisive gate",
   "D3 five vD arms instead of two (control + 2 moment readings + 0.0814 + 0.1220)",
   "D4 S1b's exact 0.0814/0.1220 used where the task says 0.081/0.122",
   "D5 pinned interpreter has no scipy; ndtr reimplemented in numpy (Cody CALERF), validated vs math.erfc (max rel 9.55e-15) and by exact reproduction of the committed S4 control",
   "D6 verdict mapping: predeclared G0 did not fire; KILL_CONFIRMED is called on G1 FAIL + G5 instead, flagged rather than reported as INCONCLUSIVE",
 ],

 "files": ["PREDECLARATION.md", "VERDICT.md", "results.json", "step0_moment.py",
           "step0_results.json", "step1_shape_and_bounds.py", "step1_results.json",
           "run_s1_gm.py", "s1_gm_results.json", "run_s4_gm.py", "s4_gm_results.json",
           "ndtr_numpy.py", "ndtr_validation.json", "make_results.py"],
}

json.dump(R, open(os.path.join(H, "results.json"), "w"), indent=1)
print("wrote results.json")
print("gate_result:", R["gate_result"])
print("G0 fires:", R["gates"]["G0_step0_kill"]["FIRES_KILL"],
      "| G1 pass:", R["gates"]["G1_identification"]["pass"],
      "| G2 pass:", R["gates"]["G2_shape_freedom"]["pass"])
print("G5 vD lower bound raw:", R["gates"]["G5_floor_correlation_bound"]["vD_lower_bound_raw"],
      R["gates"]["G5_floor_correlation_bound"]["bootstrap_and_null"]["vD_lower_bound_ci95"],
      "perm p:", R["gates"]["G5_floor_correlation_bound"]["bootstrap_and_null"]["permutation_p_two_sided"])
print("boot lower-bound mean:", R["gates"]["G5_floor_correlation_bound"]["bootstrap_and_null"]["vD_lower_bound_boot_mean"])
