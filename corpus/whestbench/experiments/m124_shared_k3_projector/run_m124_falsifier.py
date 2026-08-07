"""Inert, manifest-ready M124 falsifier.

The draft deliberately refuses execution.  A separate reviewed action must
replace the manifest with a hash-locked FROZEN release and explicitly enable
execution before the generated-only outcome grid can run once.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from m124_protocol import adjudicate, evaluate_case
from m124_shared_projector import M124FailClosed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="DRAFT_MANIFEST.json")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", default="outcome.json")
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        not args.execute
        or manifest.get("status") != "FROZEN_RELEASE"
        or manifest.get("execution_authorized") is not True
        or manifest.get("carrier_prerequisite", {}).get("status") != "PASSED_AND_HASH_LOCKED"
        or not manifest.get("carrier_prerequisite", {}).get("artifact_hash")
        or not isinstance(manifest.get("carrier_prerequisite", {}).get("effective_compute"), int)
        or manifest.get("carrier_prerequisite", {}).get("effective_compute")
        > manifest.get("carrier_prerequisite", {}).get("maximum_nonoverlap_effective_compute")
    ):
        raise SystemExit("M124 INERT: draft/unapproved or carrier-unresolved manifest; no outcome evaluated")
    # This branch is intentionally unreachable in the current draft.  It is
    # complete enough for a later independent pre-execution audit.
    rows = []
    for row in manifest["cases"]:
        try:
            rows.append(evaluate_case(type("CaseRecord", (), row)()))
        except (M124FailClosed, MemoryError) as exc:
            rows.append({"case": row, "failure": type(exc).__name__, "message": str(exc)})
    adjudication = adjudicate(rows, manifest)
    destination = Path(args.output).resolve()
    if destination.exists():
        raise SystemExit("refusing to overwrite an existing outcome")
    destination.write_text(
        json.dumps({"manifest": manifest, "rows": rows, "adjudication": adjudication}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
