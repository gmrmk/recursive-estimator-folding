"""Drive the eight frozen n=64 cases, one separately killable child each.

Pass 1 recomputes the comparator as well (seal 1).  Pass 2 is a bit-repeat of
the candidate in fresh processes (seal 3).  Seal 2 compares the three cases the
original killed run completed against premise_results.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from frozen_paths import (
    CASES,
    FROZEN_CONTRACT,
    FROZEN_IMPL,
    HERE,
    ORIGINAL_PARTIAL,
    TRUTH_BANK,
    sha256,
)

PYTHON = sys.executable
PER_CASE_TIMEOUT_S = 600


def run_pass(tag: str, comparator: bool) -> list[dict]:
    out_dir = HERE / f"cases_{tag}"
    out_dir.mkdir(exist_ok=True)
    records = []
    for width, depth, seed in CASES:
        target = out_dir / f"case_n{width}_l{depth}_s{seed}.json"
        argv = [
            PYTHON,
            str(HERE / "run_case.py"),
            str(width),
            str(depth),
            str(seed),
            str(target),
        ]
        if comparator:
            argv.append("--comparator")
        started = time.perf_counter()
        proc = subprocess.run(
            argv,
            cwd=str(HERE),
            capture_output=True,
            text=True,
            timeout=PER_CASE_TIMEOUT_S,
        )
        wall = time.perf_counter() - started
        if proc.returncode != 0:
            raise RuntimeError(
                f"child failed rc={proc.returncode} for {width}/{depth}/{seed}\n"
                f"stdout={proc.stdout}\nstderr={proc.stderr}"
            )
        record = json.loads(target.read_text(encoding="utf-8"))
        record["child_returncode"] = proc.returncode
        record["child_wall_seconds"] = wall
        records.append(record)
        print(f"[{tag}] {proc.stdout.strip()}  wall={wall:.2f}s")
    return records


def main() -> None:
    started = time.perf_counter()
    pass1 = run_pass("pass1", comparator=True)
    pass2 = run_pass("pass2", comparator=False)

    baseline_sum = sum(r["baseline_mse"] for r in pass1)
    candidate_sum = sum(r["candidate_mse"] for r in pass1)
    ratio = candidate_sum / baseline_sum
    wins = sum(1 for r in pass1 if r["win"])

    # SEAL 1 - weights/bank seal
    seal1_max_pred_delta = max(
        r["comparator_recompute_max_abs_delta"] for r in pass1
    )
    seal1_max_mse_delta = max(r["banked_baseline_mse_abs_delta"] for r in pass1)

    # SEAL 2 - repair neutrality against the original partial run
    original = json.loads(ORIGINAL_PARTIAL.read_text(encoding="utf-8"))
    seal2 = []
    for case in original["cases"]:
        key = (case["width"], case["depth"], case["seed"])
        mine = next(
            r
            for r in pass1
            if (r["width"], r["depth"], r["seed"]) == key
        )
        original_mse = float(
            case["metrics"]["adaptive_tau05_sparse_radial"]["mse"]
        )
        original_ratio = float(
            case["metrics"]["adaptive_tau05_sparse_radial"][
                "ratio_to_corrected_fullcov"
            ]
        )
        seal2.append(
            {
                "seed": case["seed"],
                "original_mse": original_mse,
                "revived_mse": mine["candidate_mse"],
                "relative_mse_delta": abs(mine["candidate_mse"] - original_mse)
                / original_mse,
                "original_ratio": original_ratio,
                "revived_ratio": mine["ratio"],
                "relative_ratio_delta": abs(mine["ratio"] - original_ratio)
                / original_ratio,
            }
        )
    seal2_max = max(s["relative_mse_delta"] for s in seal2)

    # SEAL 3 - bit repeat
    seal3 = [
        {
            "seed": a["seed"],
            "pass1_candidate_mse": a["candidate_mse"],
            "pass2_candidate_mse": b["candidate_mse"],
            "bitwise_identical": a["candidate_mse"] == b["candidate_mse"],
        }
        for a, b in zip(pass1, pass2)
    ]
    seal3_all = all(s["bitwise_identical"] for s in seal3)

    result = {
        "schema": 1,
        "experiment": "gm_latent_cubature",
        "revives": "fold_ledger.json candidate index 11 latent_sparse_radial_cubature",
        "scope": "eight frozen synthetic n=64 cases from the banked truth file; "
        "no truth generation, no WHest data, scorer, holdout, or API",
        "frozen_hashes": {
            "latent_sparse_cubature.py": sha256(FROZEN_IMPL),
            "premise_contract.json": sha256(FROZEN_CONTRACT),
            "fresh_n64_results.json": sha256(TRUTH_BANK),
        },
        "retained_hashes_expected": {
            "candidate": "a31fd01802ff79167efe00c1b3b129c2744853d9ad0a9897c990af5988c4f24c",
            "contract": "df2ef00fff7b77fc365fc80536524dfec388363f6a77993aa81c9c47c97a400a",
        },
        "cases": [
            {
                k: v
                for k, v in r.items()
                if k != "candidate_prediction"
            }
            for r in pass1
        ],
        "aggregate": {
            "baseline_mse_sum": baseline_sum,
            "candidate_mse_sum": candidate_sum,
            "aggregate_ratio": ratio,
            "wins": wins,
            "cases": len(pass1),
        },
        "gates": {
            "gate1_aggregate_ratio_at_most_0_80": {
                "value": ratio,
                "threshold": 0.80,
                "passes": bool(ratio <= 0.80),
            },
            "gate2_wins_at_least_6_of_8": {
                "value": wins,
                "threshold": 6,
                "passes": bool(wins >= 6),
            },
        },
        "seals": {
            "seal1_comparator_recompute_max_abs_prediction_delta": seal1_max_pred_delta,
            "seal1_banked_baseline_mse_max_abs_delta": seal1_max_mse_delta,
            "seal1_tolerance": 1e-12,
            "seal1_passes": bool(seal1_max_pred_delta <= 1e-12),
            "seal2_repair_neutrality": seal2,
            "seal2_max_relative_mse_delta": seal2_max,
            "seal2_tolerance": 1e-12,
            "seal2_passes": bool(seal2_max <= 1e-12),
            "seal3_bit_repeat": seal3,
            "seal3_passes": bool(seal3_all),
        },
        "resources": {
            "max_peak_working_set_bytes": max(
                r["memory"]["peak_working_set_bytes"] for r in pass1 + pass2
            ),
            "rss_limit_bytes": 2_000_000_000,
            "max_case_wall_seconds": max(
                r["child_wall_seconds"] for r in pass1 + pass2
            ),
            "total_wall_seconds": time.perf_counter() - started,
            "all_eight_cases_completed": len(pass1) == 8,
        },
        "guard_counts_pass1": [r["guard_counts"] for r in pass1],
    }
    (HERE / "bank_results.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["aggregate"], indent=2))
    print(json.dumps(result["gates"], indent=2))
    print(
        json.dumps(
            {k: v for k, v in result["seals"].items() if "seal2_repair" not in k},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
