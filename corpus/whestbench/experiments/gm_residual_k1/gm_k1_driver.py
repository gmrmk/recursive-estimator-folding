"""gm_residual_k1 driver: re-run the frozen five-worker M160 harness under the
1-physical-core participant pin and charge residual ONCE at lambda=1e11.

Checkpoint/resume: each worker's raw JSON is written as it completes and is
skipped on a later invocation, so the run can be driven by repeated sequential
foreground calls without losing work.

Gate constants copied verbatim from the frozen run_m160_hostile_audit.py.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAUNCHER = HERE / "pin_launch.py"
PYTHON311 = Path(r"C:\Users\strid\.local\bin\python3.11.exe")
CACHED_RAW = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\scorefloor_generation\terra_m160_hostile_deploy\raw_workers"
)

HISTORICAL_EFFECTIVE_LIMIT = 258.4e9
HISTORICAL_RSS_LIMIT_MIB = 512.0
HISTORICAL_SETUP_LIMIT_S = 4.0
HISTORICAL_PREDICT_LIMIT_S = 20.0
LAMBDA = 1e11

TARGET_JOBS = [(160_310_001 + i, 160_320_001 + i) for i in range(5)]
EARLY_JOB = (160_410_001, 160_420_001)


def charge(billed: int, residual_s: float, k: float) -> float:
    return float(billed) + LAMBDA * float(k) * float(residual_s)


def run_worker(mask: int, output: Path, case: str, setup: int, mlp: int, timeout: int) -> dict:
    if output.is_file():
        record = json.loads(output.read_text(encoding="utf-8"))
        record["_resumed_from_disk"] = True
        return record
    command = [
        str(PYTHON311),
        str(LAUNCHER),
        "--mask",
        hex(mask),
        "--",
        "--output",
        str(output),
        "--case",
        case,
        "--setup-seed",
        str(setup),
        "--mlp-seed",
        str(mlp),
    ]
    started = time.perf_counter()
    completed = subprocess.run(
        command, check=False, capture_output=True, text=True, timeout=timeout
    )
    elapsed = time.perf_counter() - started
    if not output.is_file():
        return {
            "status": "GM_K1_MISSING_WORKER_OUTPUT",
            "case": case,
            "seeds": {"setup": setup, "generated_mlp": mlp},
            "subprocess_returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    record = json.loads(output.read_text(encoding="utf-8"))
    record["subprocess_returncode"] = completed.returncode
    record["subprocess_stderr"] = completed.stderr.strip()
    record["driver_wall_s"] = elapsed
    record["affinity_mask"] = hex(mask)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def cached_reference(name: str) -> dict:
    path = CACHED_RAW / f"{name}.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(record: dict, reference: dict) -> dict:
    first = record.get("first_predict", {})
    second = record.get("second_predict", {})
    memory = record.get("memory_after_second_predict", {})
    billed = int(first.get("billed_flops", 0))
    residual = float(first.get("residual_s", 0.0))
    k1 = charge(billed, residual, 1)
    k5 = charge(billed, residual, 5)
    ref_first = reference.get("first_predict", {})
    row = {
        "case": record.get("case"),
        "seeds": record.get("seeds"),
        "status": record.get("status"),
        "affinity_mask": record.get("affinity_mask"),
        "billed_flops": billed,
        "residual_s": residual,
        "wall_s": first.get("wall_s"),
        "backend_s": first.get("backend_s"),
        "overhead_s": first.get("overhead_s"),
        "setup_s": record.get("setup_s"),
        "C_k1": k1,
        "C_k5": k5,
        "worker_effective_compute_field": first.get("effective_compute"),
        "worker_hostile_5x_field": first.get("hostile_effective_compute_5x_residual"),
        "recompute_matches_field_k1": abs(k1 - float(first.get("effective_compute", 0.0)))
        <= 1e-6 * max(k1, 1.0),
        "k1_margin_to_gate": HISTORICAL_EFFECTIVE_LIMIT - k1,
        "k1_margin_pct": 100.0 * (HISTORICAL_EFFECTIVE_LIMIT - k1) / HISTORICAL_EFFECTIVE_LIMIT,
        "break_even_k": (HISTORICAL_EFFECTIVE_LIMIT - billed) / (LAMBDA * residual)
        if residual > 0
        else None,
        "residual_ceiling_s_at_k1": (HISTORICAL_EFFECTIVE_LIMIT - billed) / LAMBDA,
        "passes_k1": k1 < HISTORICAL_EFFECTIVE_LIMIT,
        "passes_k5": k5 < HISTORICAL_EFFECTIVE_LIMIT,
        "peak_rss_mib": memory.get("peak_rss_mib"),
        "peak_private_mib": memory.get("peak_private_mib"),
        "all_assertions_pass": bool(record.get("assertions"))
        and all(record.get("assertions", {}).values()),
        "failed_assertions": [
            name for name, value in record.get("assertions", {}).items() if not value
        ],
        "prediction_sha256": first.get("prediction_sha256"),
        "replay_bitwise_equal": first.get("prediction_sha256")
        == second.get("prediction_sha256"),
        "second_predict_residual_s": second.get("residual_s"),
        "second_predict_C_k1": charge(
            int(second.get("billed_flops", 0)), float(second.get("residual_s", 0.0)), 1
        ),
        "second_predict_passes_k1": charge(
            int(second.get("billed_flops", 0)), float(second.get("residual_s", 0.0)), 1
        )
        < HISTORICAL_EFFECTIVE_LIMIT,
        "residual_inflation_vs_20260807": (
            residual / float(ref_first["residual_s"])
            if ref_first.get("residual_s")
            else None
        ),
        "cached_20260807_billed_flops": ref_first.get("billed_flops"),
        "cached_20260807_residual_s": ref_first.get("residual_s"),
        "cached_20260807_prediction_sha256": ref_first.get("prediction_sha256"),
        "billed_matches_20260807": ref_first.get("billed_flops") == billed
        if ref_first
        else None,
        "prediction_sha256_matches_20260807": (
            ref_first.get("prediction_sha256") == first.get("prediction_sha256")
        )
        if ref_first
        else None,
    }
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True, choices=("A", "B"))
    parser.add_argument("--mask", required=True)
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    mask = int(args.mask, 0)
    raw = HERE / f"raw_arm_{args.arm}"
    raw.mkdir(parents=True, exist_ok=True)

    targets = []
    for index, (setup, mlp) in enumerate(TARGET_JOBS, start=1):
        record = run_worker(mask, raw / f"target_{index}.json", "target", setup, mlp, args.timeout)
        row = summarize(record, cached_reference(f"target_{index}"))
        row["worker"] = index
        targets.append(row)
        print(
            f"[arm {args.arm}] w{index} billed={row['billed_flops']/1e9:.9f}B "
            f"resid={row['residual_s']:.6f}s C_k1={row['C_k1']/1e9:.9f}B "
            f"C_k5={row['C_k5']/1e9:.9f}B k1="
            f"{'PASS' if row['passes_k1'] else 'FAIL'} "
            f"assert={'PASS' if row['all_assertions_pass'] else row['failed_assertions']} "
            f"resid_x={row['residual_inflation_vs_20260807']}",
            flush=True,
        )
    early_record = run_worker(
        mask, raw / "adversarial_early_pruning.json", "early", *EARLY_JOB, args.timeout
    )
    early = summarize(early_record, cached_reference("adversarial_early_pruning"))
    early["worker"] = "early"
    print(
        f"[arm {args.arm}] early billed={early['billed_flops']/1e9:.9f}B "
        f"resid={early['residual_s']:.6f}s C_k1={early['C_k1']/1e9:.9f}B "
        f"assert={'PASS' if early['all_assertions_pass'] else early['failed_assertions']}",
        flush=True,
    )

    worst_k1 = max(row["C_k1"] for row in targets)
    worst_k5 = max(row["C_k5"] for row in targets)
    worst_rss = max(row["peak_rss_mib"] or 0.0 for row in targets)
    worst_setup = max(row["setup_s"] or 0.0 for row in targets)
    worst_predict = max(row["wall_s"] or 0.0 for row in targets)
    worst_residual = max(row["residual_s"] for row in targets)

    gates = {
        "five_fresh_target_processes_completed": len(targets) == 5
        and all(row["status"] == "M160_CPYTHON311_HOSTILE_WORKER_PASS_NO_EFFICACY" for row in targets),
        "all_target_structural_invariants": all(row["all_assertions_pass"] for row in targets),
        "adversarial_early_pruning_structural_invariants": early["all_assertions_pass"],
        "k1_258_4B_effective_compute": worst_k1 < HISTORICAL_EFFECTIVE_LIMIT,
        "legacy_k5_258_4B_effective_compute": worst_k5 < HISTORICAL_EFFECTIVE_LIMIT,
        "historical_512MiB_peak_rss": worst_rss < HISTORICAL_RSS_LIMIT_MIB,
        "historical_setup_under_4s": worst_setup < HISTORICAL_SETUP_LIMIT_S,
        "historical_predict_under_20s": worst_predict < HISTORICAL_PREDICT_LIMIT_S,
        "second_predict_k1_all_pass": all(row["second_predict_passes_k1"] for row in targets),
        "replay_bitwise_equal_all": all(row["replay_bitwise_equal"] for row in targets),
        "billed_flops_reproduce_20260807": all(
            row["billed_matches_20260807"] for row in targets
        ),
        "prediction_sha256_reproduce_20260807": all(
            row["prediction_sha256_matches_20260807"] for row in targets
        ),
        "independent_recompute_matches_worker_field": all(
            row["recompute_matches_field_k1"] for row in targets
        ),
    }
    binding_kill = not gates["k1_258_4B_effective_compute"]
    structural_fail = not (
        gates["five_fresh_target_processes_completed"]
        and gates["all_target_structural_invariants"]
        and gates["adversarial_early_pruning_structural_invariants"]
        and gates["historical_512MiB_peak_rss"]
    )
    result = {
        "arm": args.arm,
        "affinity_mask": hex(mask),
        "arm_description": (
            "1 physical core (SMT pair 0,1) participant pin -- BINDING falsifier"
            if args.arm == "A"
            else "1 logical CPU pin -- declared NON-BINDING hostility probe"
        ),
        "firewall": (
            "generated 256x32 He weights only; no truth, labels, reference, MSE, "
            "scorer, leaderboard, submission, network, or champion mutation"
        ),
        "gate": HISTORICAL_EFFECTIVE_LIMIT,
        "lambda": LAMBDA,
        "targets": targets,
        "adversarial_early_pruning": early,
        "max_target_C_k1": worst_k1,
        "max_target_C_k5": worst_k5,
        "max_target_residual_s": worst_residual,
        "max_target_peak_rss_mib": worst_rss,
        "max_target_setup_s": worst_setup,
        "max_target_predict_s": worst_predict,
        "k1_pass_count": sum(row["passes_k1"] for row in targets),
        "k5_pass_count": sum(row["passes_k5"] for row in targets),
        "gates": gates,
        "verdict": (
            "KILLED_STRUCTURAL"
            if structural_fail
            else ("KILLED_K1_OVER_GATE" if binding_kill else "K1_GATE_PASS")
        ),
    }
    out = HERE / f"arm_{args.arm}_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "arm": args.arm,
                "max_target_C_k1": worst_k1,
                "max_target_C_k5": worst_k5,
                "max_target_residual_s": worst_residual,
                "k1_pass_count": result["k1_pass_count"],
                "k5_pass_count": result["k5_pass_count"],
                "gates": gates,
                "verdict": result["verdict"],
                "output": str(out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
