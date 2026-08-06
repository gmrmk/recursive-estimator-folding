"""Deterministic, API-free adapter for recursive-estimator-folding packets.

Headroom is used here only as orchestration/memory.  This adapter never proposes
evidence or promotes a candidate: it extracts the frozen champion, constraints,
kills, and exactly one requested mechanism from the audited fold ledger.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()

    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    candidates = {item["id"]: item for item in ledger["candidates"]}
    if args.candidate not in candidates:
        raise SystemExit(f"unknown candidate: {args.candidate}")
    chosen = candidates[args.candidate]
    if chosen["status"] != "proposed":
        raise SystemExit(f"candidate must be proposed, got {chosen['status']}")

    promoted = [item for item in ledger["candidates"] if item["status"] == "promoted"]
    if len(promoted) != 1:
        raise SystemExit(f"expected exactly one champion, got {len(promoted)}")

    packet = {
        "schema_version": 1,
        "mode": "offline_deterministic_no_api",
        "champion": promoted[0],
        "invariants": ledger["invariants"],
        "killed_mechanisms": [
            {
                "id": item["id"],
                "mechanism": item["mechanism"],
                "kill_condition": item["kill_condition"],
                "result": item.get("result"),
            }
            for item in ledger["candidates"]
            if item["status"] == "killed"
        ],
        "next_mutation_request": {
            "id": chosen["id"],
            "one_mechanism_only": True,
            "mechanism": chosen["mechanism"],
            "bias_class": chosen["bias_class"],
            "predicted_signature": chosen["prediction"],
            "kill_condition": chosen["kill_condition"],
        },
        "survivor_error_covariance": {
            "available": False,
            "reason": "Only one promoted champion exists; proposed children must pass separately before an interaction or covariance test.",
        },
        "holdout_firewall": {
            "development": "0..599",
            "locked": "600..799",
            "prohibited": "800..999",
            "private": "untouched",
            "holdout_outcomes_in_packet": False,
        },
        "authority": "Proposals are non-evidentiary. The external premise/screen/validation ladder is authoritative.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

