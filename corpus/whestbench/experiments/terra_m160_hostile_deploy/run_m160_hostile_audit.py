"""Run M160's generated-only CPython-3.11 workers in separate processes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
WORKER = HERE / "m160_cp311_worker.py"
DEFAULT_PYTHON = Path(r"C:\Users\strid\.local\bin\python3.11.exe")
HISTORICAL_EFFECTIVE_LIMIT = 258.4e9
HISTORICAL_RSS_LIMIT_MIB = 512.0
HISTORICAL_SETUP_LIMIT_S = 4.0
HISTORICAL_PREDICT_LIMIT_S = 20.0


def _worker_command(python: Path, output: Path, case: str, setup: int, mlp: int) -> list[str]:
    return [
        str(python),
        str(WORKER),
        "--output",
        str(output),
        "--case",
        case,
        "--setup-seed",
        str(setup),
        "--mlp-seed",
        str(mlp),
    ]


def _run_worker(python: Path, output: Path, case: str, setup: int, mlp: int) -> dict:
    completed = subprocess.run(
        _worker_command(python, output, case, setup, mlp),
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if not output.is_file():
        return {
            "status": "M160_MISSING_WORKER_OUTPUT",
            "case": case,
            "seeds": {"setup": setup, "generated_mlp": mlp},
            "subprocess_returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    result = json.loads(output.read_text(encoding="utf-8"))
    result["subprocess_returncode"] = completed.returncode
    result["subprocess_stdout"] = completed.stdout.strip()
    result["subprocess_stderr"] = completed.stderr.strip()
    return result


def _first(record: dict) -> dict:
    return record.get("first_predict", {})


def _bools(record: dict) -> bool:
    assertions = record.get("assertions", {})
    return bool(assertions) and all(assertions.values())


def _maximum(records: list[dict], getter, default=None):
    values = [getter(record) for record in records]
    values = [value for value in values if value is not None]
    return max(values) if values else default


def _minimum(records: list[dict], getter, default=None):
    values = [getter(record) for record in records]
    values = [value for value in values if value is not None]
    return min(values) if values else default


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "M160_HOSTILE_AUDIT_20260807.json",
    )
    args = parser.parse_args()
    if not args.python.is_file():
        raise FileNotFoundError(f"CPython-3.11 launcher not found: {args.python}")

    raw = HERE / "raw_workers"
    raw.mkdir(parents=True, exist_ok=True)
    target_jobs = [
        (160_310_001 + index, 160_320_001 + index)
        for index in range(5)
    ]
    targets = [
        _run_worker(
            args.python,
            raw / f"target_{index + 1}.json",
            "target",
            setup,
            mlp,
        )
        for index, (setup, mlp) in enumerate(target_jobs)
    ]
    early = _run_worker(
        args.python,
        raw / "adversarial_early_pruning.json",
        "early",
        160_410_001,
        160_420_001,
    )

    worst_rss = _maximum(
        targets,
        lambda item: item.get("memory_after_second_predict", {}).get("peak_rss_mib"),
    )
    worst_private = _maximum(
        targets,
        lambda item: item.get("memory_after_second_predict", {}).get("peak_private_mib"),
    )
    worst_effective = _maximum(
        targets,
        lambda item: _first(item).get("effective_compute"),
    )
    worst_hostile = _maximum(
        targets,
        lambda item: _first(item).get("hostile_effective_compute_5x_residual"),
    )
    worst_setup = _maximum(targets, lambda item: item.get("setup_s"))
    worst_predict = _maximum(targets, lambda item: _first(item).get("wall_s"))
    target_assertions_all_pass = all(_bools(item) for item in targets)
    early_assertions_pass = _bools(early)
    gates = {
        "five_fresh_target_processes_completed": len(targets) == 5
        and all(item.get("subprocess_returncode") == 0 for item in targets),
        "all_target_structural_invariants": target_assertions_all_pass,
        "adversarial_early_pruning_structural_invariants": early_assertions_pass,
        "historical_258_4B_hostile_5x_residual": (
            worst_hostile is not None and worst_hostile < HISTORICAL_EFFECTIVE_LIMIT
        ),
        "historical_512MiB_peak_rss": (
            worst_rss is not None and worst_rss < HISTORICAL_RSS_LIMIT_MIB
        ),
        "historical_setup_under_4s": (
            worst_setup is not None and worst_setup < HISTORICAL_SETUP_LIMIT_S
        ),
        "historical_predict_under_20s": (
            worst_predict is not None and worst_predict < HISTORICAL_PREDICT_LIMIT_S
        ),
    }
    fail_closed = not all(gates.values())
    result = {
        "status": (
            "M160_HOSTILE_DEPLOYMENT_AUDIT_FAIL_CLOSED_NO_EFFICACY"
            if fail_closed
            else "M160_HOSTILE_DEPLOYMENT_AUDIT_PASS_STRUCTURAL_ONLY_NO_EFFICACY"
        ),
        "firewall": (
            "each worker generates weights only; no truth, labels, reference, MSE, "
            "scorer, competition data, leaderboard, submission, or champion mutation"
        ),
        "worker": {
            "path": str(WORKER),
            "python": str(args.python),
            "fresh_process_count_target": len(targets),
            "fresh_process_count_total": len(targets) + 1,
            "raw_worker_directory": str(raw),
        },
        "historical_limits": {
            "hostile_effective_compute_5x_residual": HISTORICAL_EFFECTIVE_LIMIT,
            "peak_rss_mib": HISTORICAL_RSS_LIMIT_MIB,
            "setup_s": HISTORICAL_SETUP_LIMIT_S,
            "predict_s": HISTORICAL_PREDICT_LIMIT_S,
            "private_commit_note": (
                "Peak private commit is reported, but the historic M145 512 MiB "
                "gate was explicitly PeakWorkingSetSize/RSS rather than private commit."
            ),
        },
        "summary": {
            "minimum_target_billed_flops": _minimum(
                targets, lambda item: _first(item).get("billed_flops")
            ),
            "maximum_target_billed_flops": _maximum(
                targets, lambda item: _first(item).get("billed_flops")
            ),
            "maximum_target_effective_compute": worst_effective,
            "maximum_target_hostile_effective_compute_5x_residual": worst_hostile,
            "maximum_target_peak_rss_mib": worst_rss,
            "maximum_target_peak_private_mib": worst_private,
            "maximum_target_setup_s": worst_setup,
            "maximum_target_predict_s": worst_predict,
            "target_dispatch_call_range": [
                _minimum(targets, lambda item: _first(item).get("matmul_dispatch_calls")),
                _maximum(targets, lambda item: _first(item).get("matmul_dispatch_calls")),
            ],
            "target_flopscope_matmul_call_range": [
                _minimum(targets, lambda item: _first(item).get("flopscope_matmul_calls")),
                _maximum(targets, lambda item: _first(item).get("flopscope_matmul_calls")),
            ],
        },
        "gates": gates,
        "targets": targets,
        "adversarial_early_pruning": early,
        "disposition": (
            "fail closed on any listed gate; this is a response-free structural "
            "deployment audit, not an efficacy, ranking, or authorization result"
        ),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(args.output),
                "gates": gates,
                "worst_hostile_compute": worst_hostile,
                "worst_peak_rss_mib": worst_rss,
                "worst_peak_private_mib": worst_private,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
