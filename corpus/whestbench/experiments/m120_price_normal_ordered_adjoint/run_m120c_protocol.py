"""Non-CLI owner for the M120C operational one-shot protocol.

This module intentionally offers no command-line grid execution.  A future
independent release must supply the exact externally sealed manifest digest to
call the function below.  This turn does not make that call.
"""

from __future__ import annotations

from pathlib import Path

from m120c_protocol_config import CONFIG
from m120c_protocol_harness import (
    AtomicLifecycle,
    CANONICAL_OUTCOME_ROOT,
    ProtocolFailClosed,
    all_generated_metric_records,
    closed_manifest_errors,
    evaluate_predeclared_gates,
    record_as_json,
)


def freeze_ready_description() -> dict[str, object]:
    """Describe the sealed shape without reading, creating, or accepting a manifest."""

    return {
        "protocol_id": CONFIG.protocol_id,
        "execution_mode": CONFIG.execution_mode,
        "jobs": 27,
        "expected_records": 648,
        "fixed_output_path": CONFIG.output_path,
        "canonical_root": str(CANONICAL_OUTCOME_ROOT),
        "atomic_no_retry_claim": True,
        "manifest_required_externally": True,
    }


def run_authorized_m120c_grid(expected_manifest_sha256: str) -> dict[str, object]:
    """Consume the only canonical root and evaluate exactly the frozen grid.

    This is deliberately callable only by an independently sealed release; it
    is never called by tests, import-time code, or this module's CLI.
    """

    errors = closed_manifest_errors(Path(CONFIG.manifest_path), expected_manifest_sha256)
    if errors:
        raise ProtocolFailClosed("manifest/runtime preflight failed: " + "; ".join(errors))
    if CANONICAL_OUTCOME_ROOT.exists():
        raise ProtocolFailClosed("canonical M120C outcome root already exists; no retry is allowed")
    lifecycle = AtomicLifecycle()
    claim = {
        "protocol_id": CONFIG.protocol_id,
        "manifest_sha256": expected_manifest_sha256,
        "state": "claimed",
        "retry_allowed": False,
    }
    lifecycle.claim(claim)
    try:
        records = all_generated_metric_records()
        gate = evaluate_predeclared_gates(records)
        result = {
            "protocol_id": CONFIG.protocol_id,
            "claim_path": str(lifecycle.claim_path),
            "record_count": len(records),
            "records": [record_as_json(record) for record in records],
            "gates": gate,
            "pass": bool(gate["pass"]),
            "retry_allowed": False,
        }
    except Exception as error:
        lifecycle.publish_outcome({
            "protocol_id": CONFIG.protocol_id,
            "claim_path": str(lifecycle.claim_path),
            "failure": f"{type(error).__name__}: {error}",
            "pass": False,
            "retry_allowed": False,
        }, "error")
        raise
    lifecycle.publish_outcome(result, "pass" if result["pass"] else "fail")
    return result


def main() -> None:
    raise SystemExit(
        "M120C has no CLI execution path. An independently sealed manifest hash "
        "and explicit future authorization are required; this module will not run the grid."
    )


if __name__ == "__main__":
    main()
