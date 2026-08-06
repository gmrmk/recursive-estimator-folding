#!/usr/bin/env python3
"""Create and audit a recursive estimator-folding JSON ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_INVARIANTS = {
    "objective",
    "score_formula",
    "legality_boundary",
    "resource_ceiling",
    "development_split",
    "holdout_split",
    "champion_hash",
}
ALLOWED_STATUS = {"proposed", "killed", "screened", "validated", "promoted"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def init(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path}")
    write(path, {"schema_version": 1, "invariants": {}, "candidates": []})
    print(path)


def audit(payload: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_INVARIANTS - set(payload.get("invariants", {}))
    if missing:
        errors.append("missing invariants: " + ", ".join(sorted(missing)))

    seen: set[str] = set()
    for index, candidate in enumerate(payload.get("candidates", [])):
        label = f"candidate[{index}]"
        cid = candidate.get("id")
        if not cid or cid in seen:
            errors.append(f"{label}: id is missing or duplicated")
        seen.add(cid)
        if candidate.get("status") not in ALLOWED_STATUS:
            errors.append(f"{label}: invalid status")
        for key in ("mechanism", "bias_class", "prediction", "kill_condition"):
            if not candidate.get(key):
                errors.append(f"{label}: missing {key}")
        if candidate.get("status") in {"validated", "promoted"}:
            for key in ("artifact_hash", "matched_units", "primary_effect", "ci_upper", "failures"):
                if key not in candidate:
                    errors.append(f"{label}: {candidate['status']} entry missing {key}")
        if candidate.get("status") == "promoted":
            if candidate.get("failures") != 0:
                errors.append(f"{label}: promoted with resource failures")
            if candidate.get("ci_upper", float("inf")) >= 0:
                errors.append(f"{label}: promoted without paired CI below parity")
            if candidate.get("holdout_used_for_generation", True):
                errors.append(f"{label}: holdout firewall not affirmed")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", help="create an empty ledger")
    p_init.add_argument("path", type=Path)
    p_audit = sub.add_parser("audit", help="validate invariants and promotion records")
    p_audit.add_argument("path", type=Path)
    args = parser.parse_args()

    if args.command == "init":
        init(args.path)
        return

    problems = audit(load(args.path))
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("ledger is valid")


if __name__ == "__main__":
    main()
