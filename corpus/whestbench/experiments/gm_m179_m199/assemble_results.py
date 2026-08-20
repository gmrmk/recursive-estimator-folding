"""Assemble gm_m179_m199 results.json verbatim from the run artifacts."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

step0 = json.loads((HERE / "step0_results.json").read_text(encoding="utf-8"))
cells = []
seen = set()
# arm_b_scaled.jsonl carries the scale diagnostic; prefer it, then fill from arm_b.jsonl
for name in ("arm_b_scaled.jsonl", "arm_b.jsonl"):
    path = HERE / name
    if not path.exists():
        continue
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["cell"]["width"], rec["cell"]["replicate"])
        if key in seen:
            continue
        seen.add(key)
        rec["_source_file"] = name
        cells.append(rec)
cells.sort(key=lambda r: (r["cell"]["width"], r["cell"]["replicate"]))

completed = [c for c in cells if "exception_type" not in c]
failclosed = [c for c in cells if "exception_type" in c]

diag = json.loads((HERE / "diag_spd_depth.json").read_text(encoding="utf-8"))
diag_index = {(d["width"], d["replicate"]): d for d in diag}

g3_fail = [c for c in completed if not c["gates"]["G3_parity"]]
g3_pass = [c for c in completed if c["gates"]["G3_parity"]]

out = {
    "revival_id": "gm_m179_m199",
    "mining_key": "m179_exact_background_archive_producer",
    "predeclaration": "PREDECLARATION.md",
    "status": "MEASURED",
    "verdict": "KILL_CONFIRMED",
    "one_line": (
        "The mined cost clause (b) passes decisively and the identity/lifetime "
        "clause (a) is clean in every cell where the trace can be built, but the "
        "trace CANNOT be built at the real composition width 256: the pre-ReLU "
        "covariance loses positive semidefiniteness by layer 12-13 of 32 and "
        "M198's delay-one SPD precondition fail-closes. M199's BLOCKED_OVERLAP "
        "stands."
    ),

    "STEP_0_cost_gate_mined_clause_b": step0,

    "ARM_B_identity_trace_depth32": {
        "definition": "L = 32 weight matrices = 31 archived M179 source layers + terminal mu_32",
        "cells_attempted": len(cells),
        "cells_completed": len(completed),
        "cells_failclosed_before_trace": len(failclosed),
        "failclosed_cells": [
            {"width": c["cell"]["width"], "replicate": c["cell"]["replicate"],
             "exception_type": c["exception_type"], "exception": c["exception"]}
            for c in failclosed
        ],
        "mined_clause_a_result": {
            "legacy_calls_during_measured_stream_all_cells": {
                "build_extended_background": sorted({
                    c["legacy_calls_during_measured_stream"]["build_extended_background"]
                    for c in completed}),
                "build_labelled_carrier_maps": sorted({
                    c["legacy_calls_during_measured_stream"]["build_labelled_carrier_maps"]
                    for c in completed}),
                "labelled_inhomogeneous_source_recurrence": sorted({
                    c["legacy_calls_during_measured_stream"][
                        "labelled_inhomogeneous_source_recurrence"]
                    for c in completed}),
            },
            "unexpected_ledger_operations_any_cell": sorted({
                op for c in completed for op in c["ledger_audit"]["unexpected_operations"]}),
            "legacy_named_ledger_operations_any_cell": sorted({
                op for c in completed for op in c["ledger_audit"]["legacy_named_operations"]}),
            "buffers_with_surviving_lifetime_any_cell": sorted({
                b for c in completed
                for b in c["ledger_audit"]["buffers_with_surviving_lifetime"]}),
            "non_float64_buffers_any_cell": sorted({
                b for c in completed for b in c["ledger_audit"]["non_float64_buffers"]}),
            "m179_exact_step_post_mean_count_per_cell": sorted({
                c["ledger_audit"]["m179_exact_step_post_mean_count"] for c in completed}),
            "mu32_bitwise_identical_all_cells": all(
                c["mu32_bitwise_identical_to_streamed_terminal"] for c in completed),
            "counts_gate_all_cells": all(c["gates"]["G1_counts"] for c in completed),
            "liveness_gate_all_cells": all(c["gates"]["G2_liveness"] for c in completed),
            "impulse_exactly_zero_all_cells": all(
                c["per_layer_impulse_max_abs"] == 0.0 for c in completed),
            "VERDICT": "PASS - no legacy background call survives in any completed cell",
        },
        "G3_absolute_parity_gate_2e-12": {
            "cells_failing": [
                {"width": c["cell"]["width"], "replicate": c["cell"]["replicate"],
                 "parity_max_abs": c["parity_max_abs"],
                 "reference_state_max_abs_scale": c["reference_state_max_abs_scale"],
                 "relative_parity": c["relative_parity_DIAGNOSTIC_NOT_A_GATE"]}
                for c in g3_fail],
            "cells_passing": [
                {"width": c["cell"]["width"], "replicate": c["cell"]["replicate"],
                 "parity_max_abs": c["parity_max_abs"],
                 "reference_state_max_abs_scale": c["reference_state_max_abs_scale"],
                 "relative_parity": c["relative_parity_DIAGNOSTIC_NOT_A_GATE"]}
                for c in g3_pass],
            "relative_parity_range_all_completed_cells": [
                min(c["relative_parity_DIAGNOSTIC_NOT_A_GATE"] for c in completed),
                max(c["relative_parity_DIAGNOSTIC_NOT_A_GATE"] for c in completed)],
            "interpretation": (
                "Relative parity is 8.098e-17..6.383e-16 in EVERY completed cell, i.e. "
                "float64 round-off (eps = 2.220446049250313e-16). The absolute 2e-12 "
                "gate was frozen for M200's depth 3..6 grid where terminal magnitudes "
                "are O(1); at depth 32 those magnitudes reach 1.1e8, so the absolute "
                "gate is no longer scale-appropriate. Reported as a literal predeclared "
                "gate failure, NOT retuned."),
        },
        "cells": completed,
    },

    "ARM_C_real_width_256": {
        "predeclared": "width 256, depth 32, through the M200 fixture harness",
        "executed": "BLOCKED - two independent obstructions, both measured",
        "obstruction_1_computational": {
            "cause": ("m167_collision_owner_unification.complete_source_reference is an "
                      "O(n^3)-iteration Python triple loop with O(n^2) work per iteration, "
                      "called 3x per layer through m198.issue_m172_source inside "
                      "m200._fixture_source. It is the M200 fixture's reference SOURCE "
                      "algebra - exactly the provider M199/M200 already record as "
                      "physically missing/unpriced."),
            "measured_stream_seconds_at_L4": {"6": 0.347, "8": 0.605, "10": 1.290,
                                              "12": 2.162, "16": 4.756, "20": 10.121,
                                              "24": 16.594, "28": 27.160},
            "empirical_exponent_range": [2.71, 3.42],
            "extrapolated_seconds_one_width256_depth32_cell": ">1e5 (lower bound at the "
            "measured exponent; the code's asymptote is O(n^5))",
        },
        "obstruction_2_fail_closed_math": {
            "guard": "m198.DelayOneContext.__post_init__: min eigvalsh(pre_covariance) "
                     "<= VARIANCE_FLOOR => 'pre-ReLU covariance is not safely SPD'",
            "VARIANCE_FLOOR": 1e-12,
            "RHO_MAX": 0.9999999999999998,
            "width_256_replicate_0": {
                "first_layer_min_eig_le_floor": diag_index[(256, 0)]["first_layer_min_eig_le_floor"],
                "first_layer_rho_gt_rhomax": diag_index[(256, 0)]["first_layer_rho_gt_rhomax"],
                "min_eig_layer_12": diag_index[(256, 0)]["layers"][11]["min_eig_pre_cov"],
                "min_eig_layer_13": diag_index[(256, 0)]["layers"][12]["min_eig_pre_cov"],
                "min_eig_layer_32": diag_index[(256, 0)]["layers"][31]["min_eig_pre_cov"],
                "max_abs_rho_layer_32": diag_index[(256, 0)]["layers"][31]["max_abs_rho"],
            },
            "width_256_replicate_1": {
                "first_layer_min_eig_le_floor": diag_index[(256, 1)]["first_layer_min_eig_le_floor"],
                "first_layer_rho_gt_rhomax": diag_index[(256, 1)]["first_layer_rho_gt_rhomax"],
                "min_eig_layer_10": diag_index[(256, 1)]["layers"][9]["min_eig_pre_cov"],
                "min_eig_layer_12": diag_index[(256, 1)]["layers"][11]["min_eig_pre_cov"],
                "min_eig_layer_32": diag_index[(256, 1)]["layers"][31]["min_eig_pre_cov"],
                "max_abs_rho_layer_32": diag_index[(256, 1)]["layers"][31]["max_abs_rho"],
            },
            "m179_producer_reachability": (
                "The 32-layer M179 background recurrence ITSELF completes all 32 layers "
                "at width 256 on both seeds with no RHO_MAX violation (max|rho| reaches "
                "only 0.942027049827 and 0.970721387933). M179.relu_moments checks "
                "per-pair rho and diagonal variance, not the spectrum, so it ACCEPTS a "
                "numerically non-PSD C from layer 13 (rep 0) / layer 12 (rep 1) onward. "
                "The guard that catches it is M198's, in the composed path."),
        },
        "consequence": (
            "The operand/result/dtype/lifetime identity trace that M199 demanded cannot "
            "be produced at the composition width. M199's fourth denial ground - 'no "
            "identical call/result/lifetime trace exists' - therefore STANDS at width 256."),
    },

    "spd_depth_census": [
        {"width": d["width"], "replicate": d["replicate"],
         "first_layer_min_eig_le_floor": d["first_layer_min_eig_le_floor"],
         "first_layer_rho_gt_rhomax": d["first_layer_rho_gt_rhomax"],
         "reaches_layer_32_spd_safe": d["reaches_layer_32_spd_safe"]}
        for d in diag],

    "two_signal_verification": {
        "1_metering_reproduction": "Live flopscope 0.10.0 re-metering reproduces the "
        "frozen 2026-08-07 M179 ledger bit for bit: matmul 134217216, per_layer "
        "267886848, B31 8304492288 == fold_ledger m179_standalone_total 8.304492288B.",
        "2_exact_fraction_identities": "All five M199 ledger identities hold in exact "
        "Fraction arithmetic; the 9.723621632B threshold is derived two independent "
        "ways (7.73675016 + 1.986871472, and 100 - 90.276378368).",
        "3_independent_recomputation": "mu_32 from the M200 streamed terminal buffer is "
        "BITWISE identical (sha256 array digest) to mu_32 from an independent "
        "m179_background_producer.zero_order_recurrence call, in all 10 completed cells.",
        "4_bit_repeat": "Cell (width 5, replicate 0) parity reproduced identically "
        "across two separate process invocations: 1.862645149230957e-09 both times; "
        "mu_32 digest identical.",
        "5_seed_replication": "The width-256 SPD fail-close reproduces on two "
        "independent Philox seeds (layer 12 and layer 10 of 32).",
        "6_code_plus_measurement": "ARM C infeasibility established both by reading "
        "complete_source_reference (O(n^3) iterations x O(n^2) inner) and by measuring "
        "the width-scaling curve from width 6 to width 28.",
    },
}

(HERE / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "verdict": out["verdict"],
    "cells_attempted": out["ARM_B_identity_trace_depth32"]["cells_attempted"],
    "cells_completed": out["ARM_B_identity_trace_depth32"]["cells_completed"],
    "cells_failclosed": out["ARM_B_identity_trace_depth32"]["cells_failclosed_before_trace"],
    "g3_failing": len(g3_fail), "g3_passing": len(g3_pass),
    "rel_parity_range": out["ARM_B_identity_trace_depth32"]["G3_absolute_parity_gate_2e-12"]["relative_parity_range_all_completed_cells"],
}, indent=2))
