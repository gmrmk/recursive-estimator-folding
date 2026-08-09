"""Fail-closed feasibility check for M196's M151 B=1 premise.

This script intentionally does not create a surrogate canonical state or a
fake native trace.  It records whether the four concrete artifacts frozen in
M196's predeclaration exist with the minimum API markers required to open the
generated source-variance runner.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent


def _definitions(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def _entry(path: Path, symbols: set[str]) -> dict:
    found = _definitions(path)
    return {
        "path": str(path),
        "exists": path.is_file(),
        "required_symbols": sorted(symbols),
        "symbols_present": sorted(symbols & found),
        "ready": path.is_file() and symbols <= found,
    }


def main() -> None:
    # These are intentionally separate artifacts.  M151's exhaustive oracle,
    # M147's reference rule, and M179's (mu,V) recurrence cannot be silently
    # reinterpreted as any one of them.
    checks = {
        "b1_state_provider": _entry(
            HERE / "m196_b1_state_provider.py", {"build_b1_state"}
        ),
        "native_b1_compiler": _entry(
            HERE / "m196_native_b1_compiler.py", {"compile_b1_control"}
        ),
        "m147_bound_provider": _entry(
            HERE / "m196_m147_provider.py", {"delta211"}
        ),
        "native_trace": {
            "path": str(HERE / "m196_native_trace.json"),
            "exists": (HERE / "m196_native_trace.json").is_file(),
            "ready": False,
        },
    }
    trace = HERE / "m196_native_trace.json"
    if trace.is_file():
        try:
            payload = json.loads(trace.read_text(encoding="utf-8"))
            checks["native_trace"].update({
                "blocks": payload.get("blocks"),
                "nodes": payload.get("nodes"),
                "inclusive_new_cost_billions": payload.get("inclusive_new_cost_billions"),
                "peak_mib": payload.get("peak_mib"),
                "ready": (
                    payload.get("blocks") == 1
                    and payload.get("nodes") == 49
                    and payload.get("inclusive_new_cost_billions", float("inf")) <= 10.291363760
                    and payload.get("peak_mib", float("inf")) <= 512.0
                    and payload.get("flopscope_target_trace") is True
                    and payload.get("prohibited_operations") == []
                ),
            })
        except (OSError, ValueError, TypeError) as exc:
            checks["native_trace"]["parse_error"] = type(exc).__name__

    # Static evidence for the blocker: M179 can emit only a Gaussian-closure
    # (mu,V) state, M151 has only the small-width exhaustive oracle, and M147
    # is an explicitly cost-killed per-triple reference kernel.
    existing = {
        "m151_oracle": _entry(
            EXPERIMENTS / "m151_b1_forward_control" / "m151_b1_forward_control.py",
            {"B1CanonicalState", "forward_b1_control_source"},
        ),
        "m179_background": _entry(
            EXPERIMENTS / "m179_background_archive_producer" / "m179_background_producer.py",
            {"BackgroundState", "zero_order_recurrence"},
        ),
        "m147_reference": _entry(
            EXPERIMENTS / "m147_endpoint_safe_bridge" / "m147_endpoint_safe_bridge.py",
            {"collision211_local_state_dot"},
        ),
    }
    ready = all(item["ready"] for item in checks.values())
    payload = {
        "candidate": "M196 M151 B=1 generated source-variance gate",
        "status": "READY_TO_OPEN_GENERATED_VARIANCE" if ready else "BLOCKED_MISSING_NATIVE_PROVIDER_OR_TRACE",
        "generated_variance_authorized": ready,
        "checks": checks,
        "existing_components": existing,
        "blocker": None if ready else (
            "No deterministic B=1 state-provider, non-cubic native source compiler, "
            "M147 binding, and inclusive target FlopScope trace exist together. "
            "Do not execute the 24-cell variance screen with a substitute state."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
