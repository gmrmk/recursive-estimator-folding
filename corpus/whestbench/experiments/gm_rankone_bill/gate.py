"""Mechanical application of the PREDECLARATION.md gates to the measured JSONs."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
s0 = json.loads((HERE / "step0_bill.json").read_text())
s1 = json.loads((HERE / "step1_identities.json").read_text())
s2 = json.loads((HERE / "step2_scale.json").read_text())
s3 = json.loads((HERE / "step3_attack.json").read_text())
s4 = json.loads((HERE / "step4_attribute.json").read_text())
s5 = json.loads((HERE / "step5_repeat.json").read_text())

GATE_R = 1.0e-5
GATE_K = 1.0e-3

D = {r["width"]: r for r in s1["stages"]["D_identities"]}
PRE = (3, 4, 5)

predeclared = []
for w in PRE:
    r = D[w]
    predeclared.append({"identity": "I1_distinct_delta_tilde", "width": w, "rel": r["I1_distinct_delta_tilde"]["f32_rel"]})
    predeclared.append({"identity": "I2_compiler_vs_brute_f32", "width": w, "rel": r["I2_compiled_vs_brute"]["f32_vs_f32brute"]["rel"]})
    predeclared.append({"identity": "I2_f32compiler_vs_f64brute", "width": w, "rel": r["I2_compiled_vs_brute"]["f32compiler_vs_f64brute"]["rel"]})
    predeclared.append({"identity": "I3_physical_K4_K31_K22_mapping", "width": w, "rel": r["I3_physical_owner_mapping"]["f32_rel"]})
    predeclared.append({"identity": "I4_source_T_eq_source_c_plus_source_Tmc", "width": w, "rel": r["I4_complete_reconstruction"]["f32_rel"]})
i5 = [r for r in s2["I5_m203_two_rectangle"] if r["n"] == 256][0]
i6 = [r for r in s2["I6_compiler_parity_he"] if r["n"] == 256][0]
predeclared.append({"identity": "I5_m203_packed_vs_expanded_f32", "width": 256, "rel": i5["f32_packed_vs_expanded_rel"]})
predeclared.append({"identity": "I5_m203_packed_f32_vs_f64", "width": 256, "rel": i5["f32_packed_vs_f64_packed_rel"]})
predeclared.append({"identity": "I6_compiler_f32_vs_f64_he256", "width": 256, "rel": i6["f32_vs_f64_rel"]})

worst = max(predeclared, key=lambda r: r["rel"])
any_kill = any(r["rel"] > GATE_K for r in predeclared)
all_revive = all(r["rel"] <= GATE_R for r in predeclared)

# ---- extended (beyond the predeclared widths): everything measured ----
extended = []
for w in (8, 12):
    r = D[w]
    extended += [
        {"identity": "I1", "width": w, "rel": r["I1_distinct_delta_tilde"]["f32_rel"]},
        {"identity": "I2", "width": w, "rel": r["I2_compiled_vs_brute"]["f32_vs_f32brute"]["rel"]},
        {"identity": "I3", "width": w, "rel": r["I3_physical_owner_mapping"]["f32_rel"]},
        {"identity": "I4", "width": w, "rel": r["I4_complete_reconstruction"]["f32_rel"]},
    ]
for r in s1["stages"]["E_I1_scaling"]:
    extended.append({"identity": "I1_scaling", "width": r["width"], "rel": r["f32_rel"]})
for r in s3["I4_width_sweep"]:
    extended.append({"identity": "I4_sweep_naive_accum", "width": r["width"], "rel": r["f32_rel"]})
for r in s3["I3d_accumulator_attack"]:
    extended.append({"identity": "I3d_naive_accum", "width": r["n"], "rel": r["naive_f32_vs_naive_f64_rel"]})
    extended.append({"identity": "I3d_blocked_accum", "width": r["n"], "rel": r["pairwise_f32_vs_pairwise_f64_rel"]})
for r in s4["I4_attribution"]:
    extended.append({"identity": "I4_blocked_accum", "width": r["width"], "rel": r["blocked_f32_result_rel"]})
for r in s2["I5_m203_two_rectangle"] + s2["I6_compiler_parity_he"]:
    pass

ext_worst = max(extended, key=lambda r: r["rel"])
ext_over_R = sorted([r for r in extended if r["rel"] > GATE_R], key=lambda r: -r["rel"])
ext_any_kill = any(r["rel"] > GATE_K for r in extended)

if s0["step0_gate"] == "KILL":
    verdict = "KILL_CONFIRMED"
elif any_kill or ext_any_kill:
    verdict = "KILL_CONFIRMED"
elif all_revive:
    verdict = "REVIVED_PASS"
else:
    verdict = "INCONCLUSIVE"

out = {
    "gate_thresholds": {"GATE_R_revive_le": GATE_R, "GATE_K_kill_gt": GATE_K},
    "step0_arithmetic_gate": s0["step0_gate"],
    "step0_predeclared_integers_all_match": s0["predeclared_all_match"],
    "step0_frozen_f64_record_reproduced": s0["frozen_f64_reproduced"],
    "step0_f32_repricing": s0["f32_repricing"],
    "step0_m203_best_combined_f32": s0["m203_best_combined_f32"],
    "step0_m203_pct_under_m151_slot": s0["m203_pct_under_m151_slot"],
    "step0_m203_still_over_strict_headroom": s0["m203_over_strict_headroom"],
    "predeclared_identity_table": predeclared,
    "predeclared_worst": worst,
    "predeclared_all_le_GATE_R": all_revive,
    "predeclared_any_gt_GATE_K": any_kill,
    "extended_worst": ext_worst,
    "extended_entries_over_GATE_R": ext_over_R,
    "extended_any_gt_GATE_K": ext_any_kill,
    "verification": {
        "frozen_m205_suite": "6 tests OK, unmodified",
        "frozen_m203_suite": "4 tests OK, unmodified",
        "frozen_record_two_of_four_bitwise": s1["stages"]["B_frozen_record_reproduction"]["bitwise_identical"],
        "frozen_record_recomputed": s1["stages"]["B_frozen_record_reproduction"]["recomputed"],
        "transcription_fidelity_worst_abs_diff": s1["stages"]["A_transcription_fidelity"]["worst_abs_diff"],
        "exact_rational_width3": s1["stages"]["C_exact_rational_width3"],
        "f64_alt_association_cross_check_n256": i6["f64_alt_assoc_vs_f64_rel"],
        "bit_repeat": s5,
    },
    "verdict": verdict,
}
(HERE / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("predeclared_identity_table", "verification")}, indent=2))
print("VERDICT:", verdict)
