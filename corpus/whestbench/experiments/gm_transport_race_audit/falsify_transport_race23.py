"""Falsifier: M245 audit Races 2 and 3, executed against the frozen supervisor.

    Race 2: PID/Stale Handle Reuse. If an invocation-1 attempt fails, leaving an
    unclosed temporary file or reparse point, a subsequent invocation-2 attempt
    on the same S-node might inherit the descriptor. It could overwrite or bind
    to the malformed payload, generating a cryptographically valid terminal
    witness containing partial invocation-1 data.

    Race 3: Intent Burn Atomicity. If the durable intent commitment (the
    attempt-burn point) is not transactionally atomic with the provisional
    receipt generation, a crash between receipt creation and burn allows an
    illegal third attempt masked as a retry, breaking the strict 8-attempt limit.

An earlier note in this session said these need a Windows host. That was wrong:
the namespace guard and the burn primitive are ordinary POSIX file operations
(`open("xb")` = O_CREAT|O_EXCL, plus `os.fsync`) and run unchanged here. Only
the process/handle/job census is Windows-specific, and it is not what either
race turns on.

Run against `supervise_m245_fixture_materialization.py`, unmodified, with
`ctypes.wintypes` stubbed so the module imports. All filesystem effects are
confined to a temporary directory; the real authority namespace is never
touched.
"""

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import sys
import tempfile
import types
from pathlib import Path

if not hasattr(ctypes, "wintypes"):
    stub = types.ModuleType("ctypes.wintypes")
    for name in ("DWORD", "BOOL", "HANDLE", "LPWSTR", "WORD", "BYTE",
                 "LARGE_INTEGER", "ULARGE_INTEGER", "LPVOID", "UINT", "LONG",
                 "WCHAR", "HMODULE"):
        setattr(stub, name, ctypes.c_uint32)
    stub.MAX_PATH = 260
    sys.modules["ctypes.wintypes"] = stub
    ctypes.wintypes = stub

_NAME = "supervise_m245_fixture_materialization.py"
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE.parent / "m245_canonical_unordered_replica_galerkin_spectrum" / _NAME,
    _HERE / _NAME,
]
SUP = next((p for p in _CANDIDATES if p.is_file()), None)
if SUP is None:
    raise SystemExit(
        "supervisor not found. This falsifier reads the frozen M245 supervisor "
        "read-only; it is deliberately NOT vendored here. Checked:\n  "
        + "\n  ".join(str(p) for p in _CANDIDATES)
        + "\nThe file arrives with PR #1 (agent/compression-survivor-corpus)."
    )
spec = importlib.util.spec_from_file_location("sup", SUP)
sup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sup)

PASS, FAIL = "PASS", "*** FALSIFIED ***"


def local_namespace(root: Path):
    """The five frozen basenames, rehomed into a temp directory."""
    return [root / name for name in sup.EXECUTION_BASENAMES]


def main() -> None:
    print(f"EXECUTION_BASENAMES ({len(sup.EXECUTION_BASENAMES)}):")
    for n in sup.EXECUTION_BASENAMES:
        print(f"   {n}")
    print()

    results: list[tuple[str, str, str]] = []

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        paths = local_namespace(root)

        # ---------------- Race 2 ----------------
        print("=" * 72)
        print("RACE 2 -- stale artifact from a failed invocation-1")

        # R2a: a clean namespace is accepted.
        try:
            sup.assert_paths_absent(paths)
            r = (PASS, "clean namespace accepted")
        except Exception as exc:
            r = (FAIL, f"clean namespace rejected: {exc}")
        results.append(("R2a clean namespace", *r))
        print(f"  R2a {r[0]}: {r[1]}")

        # R2b: invocation-1 dies leaving a malformed INTENT behind.
        stale = paths[0]
        stale.write_bytes(b'{"partial":"invocation-1 wreckage"')   # truncated JSON
        try:
            sup.assert_paths_absent(paths)
            r = (FAIL, "stale artifact NOT detected; invocation-2 would proceed")
        except FileExistsError as exc:
            r = (PASS, f"refused: {str(exc)[:60]}...")
        except Exception as exc:
            r = (PASS, f"refused ({type(exc).__name__})")
        results.append(("R2b stale artifact blocks invocation-2", *r))
        print(f"  R2b {r[0]}: {r[1]}")

        # R2c: can invocation-2 overwrite or bind to the malformed payload?
        before = stale.read_bytes()
        try:
            sup._write_exclusive_fsync(stale, b'{"invocation":2}')
            r = (FAIL, "exclusive write OVERWROTE invocation-1 data")
        except FileExistsError:
            after = stale.read_bytes()
            r = ((PASS, "exclusive create refused; invocation-1 bytes intact")
                 if after == before else
                 (FAIL, "refused but bytes changed"))
        results.append(("R2c no overwrite of stale payload", *r))
        print(f"  R2c {r[0]}: {r[1]}")

        # R2d: is the namespace PID-derived at all? (the race requires it)
        pidlike = [n for n in sup.EXECUTION_BASENAMES
                   if str(os.getpid()) in n or "pid" in n.lower()]
        r = ((PASS, "namespace is a fixed five-path set; no PID component")
             if not pidlike else (FAIL, f"PID-derived names: {pidlike}"))
        results.append(("R2d namespace not PID-derived", *r))
        print(f"  R2d {r[0]}: {r[1]}")

        # ---------------- Race 3 ----------------
        print()
        print("=" * 72)
        print("RACE 3 -- intent-burn atomicity")

        # R3a: is the burn primitive atomic and durable?
        fresh = root / "burn_probe.json"
        sup._write_exclusive_fsync(fresh, b'{"a":1}')
        try:
            sup._write_exclusive_fsync(fresh, b'{"a":2}')
            r = (FAIL, "second burn on the same path succeeded")
        except FileExistsError:
            r = (PASS, "O_EXCL: a burned path can never be re-burned")
        results.append(("R3a burn is once-only", *r))
        print(f"  R3a {r[0]}: {r[1]}")

        # R3b: ordering -- is INTENT durable BEFORE the receipt exists?
        # Checked two independent ways. The frozen state trace is authoritative;
        # call-site line numbers corroborate it. (An earlier version of this
        # probe compared `str.find` offsets and matched the *definition* of
        # _publish_r_and_capture_endpoint rather than its call site, reporting a
        # false FALSIFIED. Definitions are declared above the flow that calls
        # them, so source offsets of defs say nothing about execution order.)
        src = SUP.read_text(encoding="utf-8")
        trace = list(sup.EXPECTED_TRACE)
        by_trace = trace.index("INTENT_VERIFIED") < trace.index("R_PUBLISHED")

        lines = src.splitlines()
        def call_line(needle: str, skip_defs: bool = True) -> int:
            for i, ln in enumerate(lines, start=1):
                if needle in ln and not (skip_defs and ln.lstrip().startswith("def ")):
                    return i
            return -1
        l_intent = call_line("_publish_owned_json(")
        l_verified = call_line('trace.append("INTENT_VERIFIED")')
        l_receipt = call_line("_publish_r_and_capture_endpoint(")
        by_source = 0 < l_intent < l_verified < l_receipt

        r = ((PASS, f"INTENT verified before R: trace {by_trace} "
                    f"(idx {trace.index('INTENT_VERIFIED')} < "
                    f"{trace.index('R_PUBLISHED')}); source lines "
                    f"{l_intent} < {l_verified} < {l_receipt}")
             if (by_trace and by_source) else
             (FAIL, f"ordering not established: trace={by_trace}, "
                    f"source={by_source} ({l_intent},{l_verified},{l_receipt})"))
        results.append(("R3b burn precedes receipt", *r))
        print(f"  R3b {r[0]}: {r[1]}")

        # R3c: crash after intent -- does the next attempt get blocked?
        crash_root = root / "crash"
        crash_root.mkdir()
        crash_paths = local_namespace(crash_root)
        sup._write_exclusive_fsync(crash_paths[0], b'{"intent":"durable"}')
        # ... process dies here, before any receipt exists ...
        try:
            sup.assert_paths_absent(crash_paths)
            r = (FAIL, "post-crash retry ALLOWED -- the burn did not hold")
        except FileExistsError:
            r = (PASS, "post-crash retry refused; the intent file IS the burn")
        results.append(("R3c crash-after-intent blocks retry", *r))
        print(f"  R3c {r[0]}: {r[1]}")

        # R3d: what does the frozen policy actually say about retries?
        policy = {k: v for k, v in
                  (("no_retry", '"no_retry": True' in src),
                   ("post_intent_failure_permanent",
                    '"post_intent_failure_permanent": True' in src))}
        r = ((PASS, f"policy flags present: {policy}")
             if all(policy.values()) else (FAIL, f"policy flags: {policy}"))
        results.append(("R3d no-retry policy declared", *r))
        print(f"  R3d {r[0]}: {r[1]}")

        # R3e: the audit's premise -- is there an 8-attempt limit to break?
        has_eight = any(tok in src for tok in
                        ("8-attempt", "max_attempts", "MAX_ATTEMPTS",
                         "attempt_limit", "ATTEMPT_LIMIT", "attempts_remaining"))
        r = (PASS, ("no attempt counter exists; the policy is no_retry, so there "
                    "is no 8-attempt limit to break")
             if not has_eight else
             (FAIL, "an attempt counter exists and needs separate audit"))
        results.append(("R3e 8-attempt-limit premise", *r))
        print(f"  R3e {r[0]}: {r[1]}")

        # Deterministic control-event names: a conditional note, not a failure.
        print()
        print("=" * 72)
        print("CONDITIONAL NOTE -- control-event naming")
        a = sup.control_event_names("a" * 64)
        b = sup.control_event_names("b" * 64)
        same = sup.control_event_names("a" * 64)
        print(f"  distinct intents -> distinct names: {a != b}")
        print(f"  same intent      -> identical names: {a == same}")
        print("  Event names derive from the intent hash, so they are")
        print("  DETERMINISTIC across invocations, not unique per invocation.")
        print("  Safe under no_retry + namespace-absent. If no_retry were ever")
        print("  relaxed, these names become a collision surface.")

    print()
    print("=" * 72)
    print("SUMMARY")
    worst = PASS
    for name, status, detail in results:
        print(f"  {status:>18}  {name}")
        if status == FAIL:
            worst = FAIL
    print()
    if worst == PASS:
        print("Races 2 and 3 as predeclared: NOT REPRODUCED.")
    else:
        print("At least one predeclared race REPRODUCED -- see FALSIFIED rows.")


if __name__ == "__main__":
    main()
