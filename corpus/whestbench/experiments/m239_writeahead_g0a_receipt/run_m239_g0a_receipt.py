"""One-shot durable transport for the frozen M238 six-test G0A replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
M238 = EXPERIMENTS / "m238_live_m179_event_packer"
M237 = EXPERIMENTS / "m237_writeahead_native_receipt"
if str(M237) not in sys.path:
    sys.path.insert(0, str(M237))

import m237_durable_native_receipt as durable  # noqa: E402


INTERPRETER = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\whest-starterkit\.venv\Scripts\python.exe"
)
INTENT = HERE / "M239_G0A_LAUNCH_INTENT_20260809.json"
RESULT = HERE / "M239_G0A_RESULT_20260809.json"
TEMP = HERE / ".M239_G0A_RESULT_20260809.json.tmp"
TIMEOUT_S = 120

PARENTS = {
    M238 / "m238_live_m179_event_packer.py":
        "25A44983642BAD7136C3486DF71BE9A3476EB76A28D2F9BA656EAB446241C603",
    M238 / "test_m238_live_m179_event_packer.py":
        "618D1EF92917166325458FA2D51CC7B2402DB0261589D013A601F1D4A6617C7A",
    M238 / "M238_DISPOSITION_20260809.md":
        "842EE3E6AB58D1622CC8AD2D4F6CA4159C40609D9162A51D9E9A06A69BC959F0",
    M237 / "m237_durable_native_receipt.py":
        "774CEF483C33B149524121144A4C5EDE9141F094AA6FE5037414E31BDDAC873C",
}

METHODS = (
    "test_production_source_has_no_generated_oracle_import",
    "test_dependency_free_nine_monomial_census",
    "test_all_twenty_columns_tree_and_m224_parity_on_frozen_grid",
    "test_positive_gauge_action_matches_every_frozen_column_degree",
    "test_co_permutation_changes_only_coordinate_names",
    "test_hostile_binders_domain_zero_write_and_one_use_lifetime",
)
PREFIX = "test_m238_live_m179_event_packer.M238AlgebraAndInterfaceTests."
COMMAND = tuple(
    [str(INTERPRETER), "-m", "unittest"]
    + [PREFIX + method for method in METHODS]
    + ["-v"]
)
FORBIDDEN_METHOD = (
    "test_m238_live_m179_event_packer.M238AlgebraAndInterfaceTests."
    "test_target_digests_non_degeneracy_and_static_flopscope_contract"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def verify_parents() -> dict[str, str]:
    observed = {str(path): sha256(path) for path in PARENTS}
    bad = {
        str(path): {"expected": expected, "observed": observed[str(path)]}
        for path, expected in PARENTS.items()
        if observed[str(path)] != expected
    }
    if bad:
        raise RuntimeError("M239 frozen parent mismatch: " + json.dumps(bad, sort_keys=True))
    return observed


def observe_parents() -> tuple[dict[str, str | None], dict[str, object]]:
    """Best-effort postflight observation that never suppresses publication."""

    observed: dict[str, str | None] = {}
    errors: dict[str, object] = {}
    for path, expected in PARENTS.items():
        try:
            value = sha256(path)
            observed[str(path)] = value
            if value != expected:
                errors[str(path)] = {"expected": expected, "observed": value}
        except Exception as exc:  # evidence transport must survive postflight errors
            observed[str(path)] = None
            errors[str(path)] = {
                "expected": expected,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }
    return observed, errors


_OUTCOME = re.compile(
    r"^(test_[^ ]+) \(([^)]+)\) \.\.\. (ok|ERROR|FAIL|skipped.*)$",
    re.MULTILINE,
)


def parse_outcomes(stdout: str, stderr: str) -> list[dict[str, str]]:
    combined = stdout + ("\n" if stdout and stderr else "") + stderr
    return [
        {"method": match.group(1), "case": match.group(2), "outcome": match.group(3)}
        for match in _OUTCOME.finditer(combined)
    ]


def main() -> int:
    if INTENT.exists() or RESULT.exists() or TEMP.exists():
        raise FileExistsError("M239 launch/result path already exists")
    if FORBIDDEN_METHOD in COMMAND:
        raise RuntimeError("M239 command contains forbidden G0B method")
    if len(METHODS) != 6 or len(COMMAND) != 10:
        raise RuntimeError("M239 exact six-test command mismatch")
    if not INTERPRETER.is_file():
        raise FileNotFoundError(str(INTERPRETER))

    before = verify_parents()
    preflight = durable.hardlink_preflight(HERE)
    intent_payload = {
        "mutation": "m239_writeahead_g0a_receipt",
        "cwd": str(M238),
        "command": list(COMMAND),
        "timeout_s": TIMEOUT_S,
        "expected_test_count": 6,
        "forbidden_method": FORBIDDEN_METHOD,
        "parent_hashes_before": before,
        "hardlink_preflight": preflight,
    }
    intent_receipt = durable.write_launch_intent_exclusive(INTENT, intent_payload)

    started = time.perf_counter()
    timed_out = False
    returncode = None
    stdout = ""
    stderr = ""
    phase = "subprocess_launch"
    execution_exception = None
    outcomes: list[dict[str, str]] = []
    after: dict[str, str | None] = {}
    postflight_errors: dict[str, object] = {}
    try:
        completed = subprocess.run(
            COMMAND,
            cwd=M238,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_S,
            check=False,
        )
        returncode = int(completed.returncode)
        stdout = completed.stdout
        stderr = completed.stderr
        phase = "postflight_hashes"
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        phase = "postflight_hashes"
    except Exception as exc:
        execution_exception = {
            "phase": phase,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }
        phase = "postflight_hashes"
    try:
        after, postflight_errors = observe_parents()
        phase = "outcome_parse"
        outcomes = parse_outcomes(stdout, stderr)
        phase = "result_publication"
    except Exception as exc:
        execution_exception = execution_exception or {
            "phase": phase,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }
    duration = time.perf_counter() - started

    observed_methods = [item["method"] for item in outcomes]
    parents_stable = not postflight_errors and all(
        after.get(str(path)) == expected for path, expected in PARENTS.items()
    )
    result_payload = {
        "mutation": "m239_writeahead_g0a_receipt",
        "transport_status": "DURABLE_RESULT_CAPTURED_FOR_PUBLICATION",
        "timed_out": timed_out,
        "returncode": returncode,
        "duration_s": duration,
        "cwd": str(M238),
        "command": list(COMMAND),
        "expected_methods": list(METHODS),
        "outcomes": outcomes,
        "outcome_count": len(outcomes),
        "outcome_name_set_exact": sorted(observed_methods) == sorted(METHODS),
        "stdout": stdout,
        "stderr": stderr,
        "execution_exception": execution_exception,
        "postflight_errors": postflight_errors,
        "parent_hashes_before": before,
        "parent_hashes_after": after,
        "parents_stable": parents_stable,
        "intent_sha256": intent_receipt["sha256"],
        "g0b_run": False,
        "g0c_run": False,
        "variance_run": False,
    }
    try:
        result_receipt = durable.publish_native_result(
            temp_path=TEMP,
            final_path=RESULT,
            payload=result_payload,
        )
    except Exception as exc:
        print(json.dumps({
            "publication_failure": True,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "temporary_exists": TEMP.exists(),
            "final_exists": RESULT.exists(),
            "relaunch_authorized": False,
        }, sort_keys=True))
        return 2
    print(json.dumps({
        "result": str(RESULT),
        "result_sha256": result_receipt["sha256"],
        "returncode": returncode,
        "outcome_count": len(outcomes),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
