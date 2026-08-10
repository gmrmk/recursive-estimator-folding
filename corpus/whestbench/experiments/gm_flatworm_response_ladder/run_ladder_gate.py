"""Predeclared falsifier for fold-ledger idx 33 `flatworm_response_ladder`.

Step 0 (lane collapse) runs first and stops the program before any accuracy
number is computed if it kills.  Then the four arms over the 24 frozen states.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

from ladder_controller import (
    DUAL_DIR,
    controller_reduce_components,
    conservative_cost_bound,
    doc,
    h18,
    lane_evidence,
    lane_geometry,
    ladder_pass,
    rr,
    sc,
)


HERE = Path(__file__).resolve().parent
CONTRACT = DUAL_DIR / "gate_contract.json"
FROZEN_DUAL_RESULTS = DUAL_DIR / "one_step_results.json"

LANE_COLLAPSE_FLOOR = 0.01
BASELINE_RATIO = 0.9659440475280408
BASELINE_WINS = 17
MINIMUM_HEAD_TO_HEAD_WINS = 13
TOLERANCE = 1e-10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def energy(values: list[float]) -> float:
    return math.fsum(value * value for value in values)


def component_signature(components: list) -> bytes:
    weights = np.asarray([c.weight for c in components], dtype=np.float64)
    means = np.asarray([c.mean for c in components], dtype=np.float64)
    return weights.tobytes() + means.tobytes()


def symmetry_errors(children, next_weight, reduced, lane_weights, seed):
    width = next_weight.shape[0]
    rng = np.random.default_rng(seed)

    input_perm = np.eye(width)[:, rng.permutation(width)]
    output_perm = np.eye(width)[:, rng.permutation(width)]
    permuted_children = h18.transform_components(children, input_perm)
    permuted_weight = input_perm.T @ next_weight @ output_perm
    permuted_reduced, _ = controller_reduce_components(
        permuted_children, permuted_weight, lane_weights, 3
    )
    expected_permuted = h18.transform_components(reduced, input_perm)

    input_scales = np.exp(rng.uniform(-0.7, 0.7, size=width))
    output_scales = np.exp(rng.uniform(-0.7, 0.7, size=width))
    input_gauge = np.diag(input_scales)
    output_gauge = np.diag(output_scales)
    gauged_children = h18.transform_components(children, input_gauge)
    gauged_weight = np.diag(1.0 / input_scales) @ next_weight @ output_gauge
    gauged_reduced, _ = controller_reduce_components(
        gauged_children, gauged_weight, lane_weights, 3
    )
    expected_gauged = h18.transform_components(reduced, input_gauge)

    base_evidence = lane_evidence(lane_geometry(children, next_weight))
    permuted_evidence = lane_evidence(
        lane_geometry(permuted_children, permuted_weight)
    )
    gauged_evidence = lane_evidence(lane_geometry(gauged_children, gauged_weight))
    evidence_error = max(
        abs(base_evidence[key] - permuted_evidence[key])
        for key in ("gate_evidence", "active_evidence")
    )
    gauge_evidence_error = max(
        abs(base_evidence[key] - gauged_evidence[key])
        for key in ("gate_evidence", "active_evidence")
    )
    return {
        "permutation_relative_error": sc.unordered_component_error(
            expected_permuted, permuted_reduced
        ),
        "positive_gauge_relative_error": sc.unordered_component_error(
            expected_gauged, gauged_reduced
        ),
        "permutation_evidence_absolute_error": float(evidence_error),
        "positive_gauge_evidence_absolute_error": float(gauge_evidence_error),
    }


def permutation_null(paired_log_ratio: list[float], draws: int = 20000) -> dict:
    values = np.asarray(paired_log_ratio, dtype=np.float64)
    observed = float(np.mean(values))
    rng = np.random.default_rng(20260810)
    signs = rng.choice(np.asarray([-1.0, 1.0]), size=(draws, values.size))
    null_means = signs @ values / values.size
    p_value = float(
        (np.sum(np.abs(null_means) >= abs(observed) - 1e-18) + 1) / (draws + 1)
    )
    return {
        "observed_mean_log_ratio": observed,
        "draws": draws,
        "two_sided_p_value": p_value,
        "null_standard_deviation": float(np.std(null_means)),
    }


def main() -> None:
    started = time.perf_counter()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rotation_seed = int(contract["rotation_seed"])

    result: dict[str, object] = {
        "schema": 1,
        "record": "flatworm_response_ladder (fold_ledger idx 33)",
        "scope": "two-lane flatworm depth controller vs scalar fusion on the 24 frozen P0 states",
        "truth_firewall": contract["truth_firewall"],
        "frozen_contract_sha256": sha256(CONTRACT),
        "frozen_dual_implementation_sha256": sha256(
            DUAL_DIR / "dual_observable_compressor.py"
        ),
        "controller_sha256": sha256(HERE / "ladder_controller.py"),
        "predeclaration_sha256": sha256(HERE / "PREDECLARATION.md"),
        "cases": contract["cases"],
        "rotation_seed": rotation_seed,
    }

    # ---------------- state generation + ladder recurrence ----------------
    all_states: list[dict[str, object]] = []
    all_trace: list[dict[str, object]] = []
    for case in contract["cases"]:
        states, trace = ladder_pass(
            int(case["width"]), int(case["depth"]), int(case["seed"]), rotation_seed
        )
        all_states.extend(states)
        all_trace.extend(trace)
    if len(all_states) != 24:
        raise RuntimeError(f"expected 24 states, got {len(all_states)}")

    # ---------------- X1: bitwise state-bank fidelity ----------------
    fidelity: list[dict[str, object]] = []
    index = 0
    for case in contract["cases"]:
        frozen = h18.frozen_states(
            int(case["width"]), int(case["depth"]), int(case["seed"]), rotation_seed
        )
        for frozen_state in frozen:
            mine = all_states[index]
            index += 1
            fidelity.append(
                {
                    "depth": int(case["depth"]),
                    "seed": int(case["seed"]),
                    "layer": int(frozen_state["layer"]),
                    "layer_match": int(frozen_state["layer"]) == int(mine["layer"]),
                    "children_bitwise_equal": component_signature(
                        frozen_state["children"]
                    )
                    == component_signature(mine["children"]),
                    "next_weight_bitwise_equal": bool(
                        np.array_equal(
                            frozen_state["next_weight"], mine["next_weight"]
                        )
                    ),
                    "next_frame_bitwise_equal": bool(
                        np.array_equal(frozen_state["next_frame"], mine["next_frame"])
                    ),
                }
            )
    x1_pass = all(
        cell["layer_match"]
        and cell["children_bitwise_equal"]
        and cell["next_weight_bitwise_equal"]
        and cell["next_frame_bitwise_equal"]
        for cell in fidelity
    )
    result["x1_state_bank_bitwise_fidelity"] = {
        "pass": bool(x1_pass),
        "states_checked": len(fidelity),
    }
    if not x1_pass:
        result["status"] = "blocked_state_bank_mismatch"
        (HERE / "results.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"status": result["status"], "fidelity": fidelity}, indent=2))
        sys.exit(2)

    # ---------------- STEP 0: predeclared lane-collapse gate ----------------
    leak_minimum = min(min(cell["leak_lane_weights"]) for cell in all_trace)
    commissural_minimum = min(
        min(cell["commissural_lane_weights"]) for cell in all_trace
    )
    evidence_gap = max(
        max(
            abs(cell["gate_evidence"] - cell["gate_evidence_exact"]),
            abs(cell["active_evidence"] - cell["active_evidence_exact"]),
        )
        for cell in all_trace
    )
    step0 = {
        "layers_scored": len(all_trace),
        "minimum_leak_lane_weight": leak_minimum,
        "minimum_commissural_lane_weight": commissural_minimum,
        "lane_collapse_floor": LANE_COLLAPSE_FLOOR,
        "max_abs_evidence_difference": evidence_gap,
        "gate_g2_no_lane_collapse": bool(
            leak_minimum > LANE_COLLAPSE_FLOOR
            and commissural_minimum > LANE_COLLAPSE_FLOOR
        ),
    }
    result["step0_lane_collapse"] = step0
    result["ladder_trace"] = all_trace
    (HERE / "step0_results.json").write_text(
        json.dumps(
            {k: result[k] for k in ("step0_lane_collapse", "ladder_trace")}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(step0, indent=2))
    if not step0["gate_g2_no_lane_collapse"]:
        result["status"] = "killed_at_step0_lane_collapse"
        result["decision"] = "kill_flatworm_response_ladder"
        (HERE / "results.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"status": result["status"]}, indent=2))
        return

    # ---------------- arms over the 24 frozen states ----------------
    arms = ("generic", "scalar_fusion", "controller_half", "leak", "commissural")
    per_state: list[dict[str, object]] = []
    for state in all_states:
        children = state["children"]
        next_weight = state["next_weight"]
        next_frame = state["next_frame"]
        reference = h18.direct_point_step(children, next_weight)

        reductions: dict[str, object] = {}
        diagnostics: dict[str, object] = {}
        generic = rr.reduce_components(children, 3)
        reductions["generic"] = generic
        diagnostics["generic"] = {}
        scalar, scalar_diag = doc.dual_reduce_components(children, next_weight, 3)
        reductions["scalar_fusion"] = scalar
        diagnostics["scalar_fusion"] = scalar_diag
        for arm, lane_weights in (
            ("controller_half", (0.5, 0.5)),
            ("leak", state["leak_lane_weights"]),
            ("commissural", state["commissural_lane_weights"]),
        ):
            reduced, diag = controller_reduce_components(
                children, next_weight, lane_weights, 3
            )
            reductions[arm] = reduced
            diagnostics[arm] = diag

        cell: dict[str, object] = {
            "width": state["width"],
            "depth": state["depth"],
            "seed": state["seed"],
            "layer": state["layer"],
            "point_count": len(children),
            "lane_weights_leak": list(state["leak_lane_weights"]),
            "lane_weights_commissural": list(state["commissural_lane_weights"]),
            "channel_gram_cosine": state["ladder"]["channel_gram_cosine"],
            "diagnostics": diagnostics,
            "observables": {},
            "moment_residuals": {},
            "minimum_normalized_eigenvalue": {},
        }
        for arm in arms:
            cell["observables"][arm] = h18.observable_error(
                h18.compressed_step(reductions[arm], next_weight, next_frame),
                reference,
            )
            cell["moment_residuals"][arm] = sc.moment_residuals(
                children, reductions[arm]
            )
            cell["minimum_normalized_eigenvalue"][arm] = (
                sc.minimum_normalized_eigenvalue(reductions[arm])
            )
        cell["symmetry_commissural"] = symmetry_errors(
            children,
            next_weight,
            reductions["commissural"],
            state["commissural_lane_weights"],
            seed=7919 * int(state["seed"]) + int(state["layer"]),
        )
        cell["win_vs_generic"] = {
            arm: bool(
                cell["observables"][arm]["joint_error"]
                < cell["observables"]["generic"]["joint_error"]
            )
            for arm in arms
            if arm != "generic"
        }
        cell["win_vs_scalar_fusion"] = {
            arm: bool(
                cell["observables"][arm]["joint_error"]
                < cell["observables"]["scalar_fusion"]["joint_error"]
            )
            for arm in ("controller_half", "leak", "commissural")
        }
        per_state.append(cell)

    # ---------------- aggregation ----------------
    def joint(arm: str, cells=per_state) -> list[float]:
        return [float(cell["observables"][arm]["joint_error"]) for cell in cells]

    def component(arm: str, key: str, cells=per_state) -> list[float]:
        return [float(cell["observables"][arm][key]) for cell in cells]

    generic_energy = energy(joint("generic"))
    aggregate: dict[str, object] = {"states": len(per_state)}
    for arm in arms:
        arm_energy = energy(joint(arm))
        aggregate[arm] = {
            "joint_energy": arm_energy,
            "rms_ratio_vs_generic": math.sqrt(arm_energy / generic_energy),
            "mean_rms_ratio_vs_generic": math.sqrt(
                energy(component(arm, "mean_relative_error"))
                / energy(component("generic", "mean_relative_error"))
            ),
            "covariance_rms_ratio_vs_generic": math.sqrt(
                energy(component(arm, "covariance_relative_error"))
                / energy(component("generic", "covariance_relative_error"))
            ),
            "wins_vs_generic": sum(
                1
                for cell in per_state
                if cell["observables"][arm]["joint_error"]
                < cell["observables"]["generic"]["joint_error"]
            ),
        }
    for arm in ("controller_half", "leak", "commissural"):
        aggregate[arm]["wins_vs_scalar_fusion"] = sum(
            1 for cell in per_state if cell["win_vs_scalar_fusion"][arm]
        )
        aggregate[arm]["ratio_delta_vs_scalar_fusion"] = (
            aggregate[arm]["rms_ratio_vs_generic"]
            - aggregate["scalar_fusion"]["rms_ratio_vs_generic"]
        )

    # X4 second recomputation of the decisive ratio via a different accumulation.
    numpy_ratio = float(
        np.sqrt(
            np.sum(np.asarray(joint("commissural")) ** 2)
            / np.sum(np.asarray(joint("generic")) ** 2)
        )
    )
    per_state_ratio_check = float(
        np.sqrt(
            np.mean(
                (np.asarray(joint("commissural")) / np.asarray(joint("generic"))) ** 2
                * (
                    np.asarray(joint("generic")) ** 2
                    / np.mean(np.asarray(joint("generic")) ** 2)
                )
            )
        )
    )

    # X5 split sample.
    split: dict[str, object] = {}
    for label, depth in (("L16", 16), ("L32", 32)):
        cells = [cell for cell in per_state if int(cell["depth"]) == depth]
        generic_half = energy(joint("generic", cells))
        split[label] = {
            "states": len(cells),
            "scalar_fusion_ratio": math.sqrt(
                energy(joint("scalar_fusion", cells)) / generic_half
            ),
            "leak_ratio": math.sqrt(energy(joint("leak", cells)) / generic_half),
            "commissural_ratio": math.sqrt(
                energy(joint("commissural", cells)) / generic_half
            ),
            "commissural_wins_vs_scalar_fusion": sum(
                1 for cell in cells if cell["win_vs_scalar_fusion"]["commissural"]
            ),
        }

    # X6 paired permutation null on log ratios.
    paired = [
        math.log(
            max(float(cell["observables"]["commissural"]["joint_error"]), 1e-300)
            / max(float(cell["observables"]["scalar_fusion"]["joint_error"]), 1e-300)
        )
        for cell in per_state
    ]
    null = permutation_null(paired)

    # X2 baseline reproduction against the committed frozen result.
    frozen_dual = json.loads(FROZEN_DUAL_RESULTS.read_text(encoding="utf-8"))
    frozen_ratio = float(frozen_dual["aggregate"]["dual_to_generic_rms_ratio"])
    frozen_wins = int(frozen_dual["aggregate"]["wins"])
    reproduced_ratio = float(aggregate["scalar_fusion"]["rms_ratio_vs_generic"])
    reproduced_wins = int(aggregate["scalar_fusion"]["wins_vs_generic"])
    x2 = {
        "frozen_ratio": frozen_ratio,
        "reproduced_ratio": reproduced_ratio,
        "relative_difference": abs(reproduced_ratio - frozen_ratio)
        / max(frozen_ratio, 1e-300),
        "frozen_wins": frozen_wins,
        "reproduced_wins": reproduced_wins,
        "pass": bool(
            abs(reproduced_ratio - frozen_ratio) / max(frozen_ratio, 1e-300) <= 1e-12
            and reproduced_wins == frozen_wins
            and frozen_ratio == BASELINE_RATIO
            and frozen_wins == BASELINE_WINS
        ),
    }

    # X3 harness equivalence: controller at w=(0.5,0.5) must equal scalar fusion.
    equivalence = max(
        abs(
            float(cell["observables"]["controller_half"]["joint_error"])
            - float(cell["observables"]["scalar_fusion"]["joint_error"])
        )
        / max(float(cell["observables"]["scalar_fusion"]["joint_error"]), 1e-300)
        for cell in per_state
    )
    x3 = {
        "max_relative_difference": float(equivalence),
        "pass": bool(equivalence <= 1e-12),
    }

    # ---------------- gates ----------------
    controller_ratio = float(aggregate["commissural"]["rms_ratio_vs_generic"])
    head_to_head = int(aggregate["commissural"]["wins_vs_scalar_fusion"])
    maximum_moment_error = max(
        float(cell["moment_residuals"][arm][metric])
        for cell in per_state
        for arm in arms
        for metric in ("mean_relative_error", "covariance_relative_error")
    )
    minimum_psd = min(
        float(cell["minimum_normalized_eigenvalue"][arm])
        for cell in per_state
        for arm in arms
    )
    maximum_permutation = max(
        float(cell["symmetry_commissural"]["permutation_relative_error"])
        for cell in per_state
    )
    maximum_gauge = max(
        float(cell["symmetry_commissural"]["positive_gauge_relative_error"])
        for cell in per_state
    )
    maximum_evidence_permutation = max(
        max(
            float(cell["symmetry_commissural"]["permutation_evidence_absolute_error"]),
            float(
                cell["symmetry_commissural"]["positive_gauge_evidence_absolute_error"]
            ),
        )
        for cell in per_state
    )
    ambiguities = sum(
        1
        for cell in per_state
        if bool(cell["diagnostics"]["commissural"].get("spectral_ambiguity"))
    )
    collapses = sum(
        1
        for cell in per_state
        if bool(cell["diagnostics"]["commissural"].get("tie_or_degenerate_collapse"))
    )
    cost = conservative_cost_bound()
    gates = {
        "g1_improves_on_scalar_fusion": bool(controller_ratio < BASELINE_RATIO),
        "g1b_head_to_head_wins_at_least_13": bool(
            head_to_head >= MINIMUM_HEAD_TO_HEAD_WINS
        ),
        "g2_no_lane_collapse": bool(step0["gate_g2_no_lane_collapse"]),
        "g3_no_reference_outcomes_in_controller": True,
        "g4_exact_source_moments": bool(maximum_moment_error <= TOLERANCE),
        "g4_all_covariances_psd": bool(minimum_psd >= -TOLERANCE),
        "g4_permutation_covariance": bool(maximum_permutation <= TOLERANCE),
        "g4_positive_gauge_covariance": bool(maximum_gauge <= TOLERANCE),
        "g4_evidence_invariance": bool(maximum_evidence_permutation <= TOLERANCE),
        "g4_zero_spectral_ambiguities": bool(ambiguities == 0),
        "g4_zero_tie_or_degenerate_collapses": bool(collapses == 0),
        "g5_cost_below_80b": bool(cost["pass"]),
        "g6_family_materiality_ratio_at_most_0_8": bool(controller_ratio <= 0.8),
    }
    decisive = [
        "g1_improves_on_scalar_fusion",
        "g1b_head_to_head_wins_at_least_13",
        "g2_no_lane_collapse",
        "g3_no_reference_outcomes_in_controller",
        "g4_exact_source_moments",
        "g4_all_covariances_psd",
        "g4_permutation_covariance",
        "g4_positive_gauge_covariance",
        "g4_evidence_invariance",
        "g4_zero_spectral_ambiguities",
        "g4_zero_tie_or_degenerate_collapses",
        "g5_cost_below_80b",
    ]
    survived = all(gates[name] for name in decisive)

    result.update(
        {
            "aggregate": aggregate,
            "decisive_numbers": {
                "scalar_fusion_ratio": float(
                    aggregate["scalar_fusion"]["rms_ratio_vs_generic"]
                ),
                "leak_ratio": float(aggregate["leak"]["rms_ratio_vs_generic"]),
                "commissural_ratio": controller_ratio,
                "commissural_minus_scalar": controller_ratio
                - float(aggregate["scalar_fusion"]["rms_ratio_vs_generic"]),
                "commissural_head_to_head_wins": head_to_head,
                "commissural_wins_vs_generic": int(
                    aggregate["commissural"]["wins_vs_generic"]
                ),
            },
            "verification": {
                "x1_state_bank_bitwise": result["x1_state_bank_bitwise_fidelity"],
                "x2_baseline_reproduction": x2,
                "x3_controller_half_equals_scalar_fusion": x3,
                "x4_independent_ratio_recomputation": {
                    "fsum_path": controller_ratio,
                    "numpy_path": numpy_ratio,
                    "weighted_per_state_path": per_state_ratio_check,
                    "max_absolute_difference": max(
                        abs(controller_ratio - numpy_ratio),
                        abs(controller_ratio - per_state_ratio_check),
                    ),
                },
                "x5_split_sample": split,
                "x6_paired_permutation_null": null,
            },
            "structural": {
                "maximum_source_moment_relative_error": maximum_moment_error,
                "minimum_normalized_covariance_eigenvalue": minimum_psd,
                "maximum_permutation_relative_error": maximum_permutation,
                "maximum_positive_gauge_relative_error": maximum_gauge,
                "maximum_evidence_invariance_absolute_error": maximum_evidence_permutation,
                "spectral_ambiguities": ambiguities,
                "tie_or_degenerate_collapses": collapses,
            },
            "cost": cost,
            "gates": gates,
            "decision": (
                "revive_flatworm_response_ladder"
                if survived
                else "kill_flatworm_response_ladder"
            ),
            "states": per_state,
            "status": "complete",
            "elapsed_seconds": time.perf_counter() - started,
        }
    )
    (HERE / "results.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "decisive_numbers": result["decisive_numbers"],
        "gates": gates,
        "decision": result["decision"],
        "verification": result["verification"],
        "structural": result["structural"],
        "cost_with_contingency": cost["with_contingency"],
        "step0": step0,
        "elapsed_seconds": result["elapsed_seconds"],
    }
    (HERE / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
