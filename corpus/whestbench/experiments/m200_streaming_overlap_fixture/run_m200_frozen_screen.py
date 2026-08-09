"""Execute M200's one predeclared generated-only frozen screen.

No network access, contest artifact, response, scorer, or submission is used.
The runner writes only the semantic/liveness fixture result and a compact
event/liveness ledger summary; it intentionally refuses to calculate a target
cost, variance, MSE, score, or provider claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import m200_streaming_overlap as m200


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "M200_FROZEN_MANIFEST_20260809.json"
RESULTS = HERE / "M200_RESULTS_20260809.json"
LEDGER = HERE / "M200_EVENT_LIVENESS_LEDGER_20260809.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _event_liveness_summary(cases: list[m200.ScreenCaseResult]) -> dict[str, object]:
    """Compact protocol ledger. Full per-buffer records stay reproducible in code."""

    count_vectors = [case.stream_counts for case in cases]
    return {
        "candidate": "M200 streaming overlap event/liveness ledger",
        "scope": "generated-only response-free fixture",
        "event_schema": [
            "operation",
            "dtype",
            "shape",
            "logical_buffer_id",
            "digest",
            "birth_order",
            "death_order",
            "alias_class",
            "native_cost_status",
        ],
        "runtime_emitter": "m200_streaming_overlap.EventLedger",
        "per_case_required_operations": {
            "background_steps": "H source/ReLU M179 steps only",
            "fixture_packets_conversions_injections": "H each; Source211 fixture provider marked explicitly unknown",
            "internal_transports": "H-1, W_k/J_k for k=2..H",
            "terminal_response": "one W_(H+1)/J_(H+1) stage with no Source211 injection",
            "background_rebuilds_inside_stream": 0,
        },
        "liveness_contract": {
            "allowed_max_live_named_objects": 5,
            "allowed": ["previous background", "current background", "one tangent", "one fixture packet", "current scratch"],
            "retained_after_stream": 0,
            "forbidden_retained": ["full archive", "dense rank-3 distinct_211", "per-source suffix states"],
        },
        "case_count": len(cases),
        "count_ranges": {
            key: [min(int(vector[key]) for vector in count_vectors), max(int(vector[key]) for vector in count_vectors)]
            for key in count_vectors[0]
        },
        "max_live_named_objects": max(case.liveness.max_live_named_objects for case in cases),
        "all_final_retained_counts_zero": all(
            all(value == 0 for value in (
                case.liveness.retained_previous_background,
                case.liveness.retained_current_background,
                case.liveness.retained_tangent,
                case.liveness.retained_fixture_packet,
                case.liveness.retained_scratch,
                case.liveness.retained_full_archive,
                case.liveness.retained_dense_rank3,
                case.liveness.retained_suffix_states,
            ))
            for case in cases
        ),
        "native_cost_disposition": "UNKNOWN_NOT_TARGET_METERED; fixture provider explicitly unknown",
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    predecl = HERE / manifest["predeclaration"]
    erratum = HERE / manifest["index_erratum"]
    if sha256(predecl) != manifest["predeclaration_sha256"]:
        raise RuntimeError("M200 predeclaration hash mismatch")
    if sha256(erratum) != manifest["index_erratum_sha256"]:
        raise RuntimeError("M200 index erratum hash mismatch")

    cases = m200.run_frozen_screen()
    payload = m200.results_payload(cases)
    payload["frozen_manifest"] = MANIFEST.name
    payload["predeclaration_sha256"] = manifest["predeclaration_sha256"]
    payload["index_erratum_sha256"] = manifest["index_erratum_sha256"]
    payload["strict_source_and_terminal_parity"] = True
    payload["per_layer_impulse_max_abs"] = max(
        case.per_layer_impulse_max_abs for case in cases
    )
    payload["frozen_counts"] = {
        "source_relu_layers_h": list(manifest["source_relu_layers_h"]),
        "total_weight_count": "H+1",
        "background_steps": "H",
        "source_packets_conversions_injections": "H each",
        "internal_transports": "H-1",
        "terminal_responses": 1,
        "background_rebuilds_inside_stream": 0,
    }
    payload["cooperative_integrity_caveat"] = (
        "Layer and source receipts are in-process cooperative integrity checks, "
        "not hostile-code security capabilities."
    )
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    LEDGER.write_text(
        json.dumps(_event_liveness_summary(cases), indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": payload["status"],
        "case_count": payload["case_count"],
        "max_abs_error": payload["max_abs_error"],
        "per_layer_impulse_max_abs": payload["per_layer_impulse_max_abs"],
        "results": RESULTS.name,
        "ledger": LEDGER.name,
    }, indent=2))


if __name__ == "__main__":
    main()
