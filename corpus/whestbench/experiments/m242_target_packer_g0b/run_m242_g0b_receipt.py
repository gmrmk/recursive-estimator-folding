"""One-shot durable transport for M242's sole target-size G0B method."""

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
M242 = EXPERIMENTS / "m242_target_packer_g0b"
M241 = EXPERIMENTS / "m241_isolated_g0a_fixtures"
M240 = EXPERIMENTS / "m240_meter_safe_finite_scan"
M237 = EXPERIMENTS / "m237_writeahead_native_receipt"
if str(M237) not in sys.path:
    sys.path.insert(0, str(M237))

import m237_durable_native_receipt as durable  # noqa: E402


INTERPRETER = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\whest-starterkit\.venv\Scripts\python.exe"
)
INTENT = HERE / "M242_G0B_LAUNCH_INTENT_20260809.json"
RESULT = HERE / "M242_G0B_RESULT_20260809.json"
TEMP = HERE / ".M242_G0B_RESULT_20260809.json.tmp"
TIMEOUT_S = 120

PARENTS = {
    M242 / "M242_PREDECLARATION_20260809.md":
        "4EB8DD9F8E402BEC7393E91FE939EF40095D26623858BFF891C671711EA4629D",
    M242 / "M242_FROZEN_MANIFEST_20260809.json":
        "7F8CE625E5193988352934D38E195A0D7EC13624DFB3237EB8B37561D1FB9E83",
    M242 / "M242_PREIMPLEMENTATION_ERRATUM_20260809.md":
        "25B0B6EE625F63BB197820E91F742E81591C3D60D23CF1EB9D11BA8607B9230A",
    M240 / "m240_meter_safe_finite_scan.py":
        "29B86374FF3A9B7ADC6D2B86F2C03A6F7F676303E5F100C46BEF1AC478B8C89E",
    M241 / "test_m241_isolated_g0a_fixtures.py":
        "BAFCAB1CD2FA1FAE368160490FD1B6639119386ADA3F3F9B13197E09E71ECFD4",
    M241 / "M241_G0A_LAUNCH_INTENT_20260809.json":
        "960CB2B9C43E0AED791777F6037858323CFA4860B5C5B6DBC02DC7B5E41CF869",
    M241 / "M241_G0A_RESULT_20260809.json":
        "8E26F1AAD37A339B15AE5D9B933BD6177325168BA57B0CF07B716E1202C953CD",
    M241 / "M241_DISPOSITION_20260809.md":
        "FED9F52B8C1FB7C3208A178511AC733009F7D2131318A46396784432F9F8EEDB",
    M241 / "M241_PREDECLARATION_20260809.md":
        "BF5F2DB29324B15392C5C095211DBA3A8B711990AB34D6D1142E0A4821C1AD32",
    M241 / "M241_FROZEN_MANIFEST_20260809.json":
        "81ABECEE6F08D5A9CE431DBA76C7C62825B00A0FDF0EECCC7B2DE633FA5B558A",
    M241 / "M241_PREIMPLEMENTATION_ERRATUM_20260809.md":
        "173565B8DA06DFDF29DE2B789DC391C7F7ADD4B48A2B9235ED4B39BE92D07C2D",
    M241 / "run_m241_g0a_receipt.py":
        "7719BDBC57DFC95C6E731DDD5A3318FE88783AE324F2DE23644F3D2625A7E792",
    M237 / "m237_durable_native_receipt.py":
        "774CEF483C33B149524121144A4C5EDE9141F094AA6FE5037414E31BDDAC873C",
}

METHODS = (
    "test_target_digests_non_degeneracy_and_static_flopscope_contract",
)
PREFIX = "test_m241_isolated_g0a_fixtures.M241AlgebraAndInterfaceTests."
COMMAND = tuple(
    [str(INTERPRETER), "-m", "unittest"]
    + [PREFIX + method for method in METHODS]
    + ["-v"]
)
FORBIDDEN_METHODS = tuple(
    PREFIX + method
    for method in (
        "test_production_source_has_no_generated_oracle_import",
        "test_dependency_free_nine_monomial_census",
        "test_all_twenty_columns_tree_and_m224_parity_on_frozen_grid",
        "test_positive_gauge_action_matches_every_frozen_column_degree",
        "test_co_permutation_changes_only_coordinate_names",
        "test_hostile_binders_domain_zero_write_and_one_use_lifetime",
    )
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
        raise RuntimeError("M242 frozen parent mismatch: " + json.dumps(bad, sort_keys=True))
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
        raise FileExistsError("M242 launch/result path already exists")
    if any(method in COMMAND for method in FORBIDDEN_METHODS):
        raise RuntimeError("M242 command contains forbidden G0A method")
    if len(METHODS) != 1 or len(COMMAND) != 5:
        raise RuntimeError("M242 exact one-test command mismatch")
    if not INTERPRETER.is_file():
        raise FileNotFoundError(str(INTERPRETER))

    before = verify_parents()
    preflight = durable.hardlink_preflight(HERE)
    intent_payload = {
        "mutation": "m242_target_packer_g0b",
        "cwd": str(M241),
        "command": list(COMMAND),
        "timeout_s": TIMEOUT_S,
        "expected_test_count": 1,
        "forbidden_methods": list(FORBIDDEN_METHODS),
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
            cwd=M241,
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
    outcome_order_exact = observed_methods == list(METHODS)
    outcomes_all_ok = (
        len(outcomes) == len(METHODS)
        and all(item["outcome"] == "ok" for item in outcomes)
    )
    combined_output = stdout + ("\n" if stdout and stderr else "") + stderr
    warning_free = re.search(r"(?i)\bwarning\b", combined_output) is None
    parents_stable = not postflight_errors and all(
        after.get(str(path)) == expected for path, expected in PARENTS.items()
    )
    result_payload = {
        "mutation": "m242_target_packer_g0b",
        "transport_status": "DURABLE_RESULT_CAPTURED_FOR_PUBLICATION",
        "timed_out": timed_out,
        "returncode": returncode,
        "duration_s": duration,
        "cwd": str(M241),
        "command": list(COMMAND),
        "expected_methods": list(METHODS),
        "outcomes": outcomes,
        "outcome_count": len(outcomes),
        "outcome_name_set_exact": sorted(observed_methods) == sorted(METHODS),
        "outcome_order_exact": outcome_order_exact,
        "outcomes_all_ok": outcomes_all_ok,
        "warning_free": warning_free,
        "g0b_pass": bool(
            returncode == 0
            and not timed_out
            and execution_exception is None
            and outcome_order_exact
            and outcomes_all_ok
            and warning_free
            and parents_stable
        ),
        "stdout": stdout,
        "stderr": stderr,
        "execution_exception": execution_exception,
        "postflight_errors": postflight_errors,
        "parent_hashes_before": before,
        "parent_hashes_after": after,
        "parents_stable": parents_stable,
        "intent_sha256": intent_receipt["sha256"],
        "g0a_rerun": False,
        "g0b_run": True,
        "g0c_run": False,
        "variance_run": False,
        "response_run": False,
        "truth_accessed": False,
        "scorer_run": False,
        "challenge_weights_accessed": False,
        "integration_run": False,
        "submission_run": False,
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
