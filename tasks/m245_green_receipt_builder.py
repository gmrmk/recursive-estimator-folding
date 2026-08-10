"""Build the M245 GREEN receipt + non-self-hashing checksum per I1.8.

Stdlib-only; reads the driver logs and authority files, writes the two GREEN
evidence files into the authority directory. Run only after all four commands
exited zero and the post-run census is clean.
"""
import hashlib
import json
from pathlib import Path

REPO = Path(r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding")
AUTH = REPO / "corpus/whestbench/experiments/m245_canonical_unordered_replica_galerkin_spectrum"
LOGS = REPO / "tasks/m245-green-logs"
PY = r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe"

SOURCES = [
    "m245_primary_core.py", "m245_replica_core.py", "m245_scientific_worker.py",
    "run_m245_scientific_shard.py", "launch_m245_scientific_invocation.py",
    "aggregate_m245_spectrum.py",
]
TESTS = [
    "test_m245_primary_core.py", "test_m245_replica_core.py",
    "test_m245_scientific_transport.py", "test_m245_aggregation.py",
]
EXPECTED_SOURCE = {
    "m245_primary_core.py": "4087adad00ede51734f7368738267be05b34c85662572883f14dd96ca6752062",
    "m245_replica_core.py": "6ab33386ae985942b48b395eba7f78c724a3ad0805744b1ea42f3d31d8ab1326",
    "m245_scientific_worker.py": "3cce3474d1173c0252a8f2c98fc29a4404275cad0d988ace728a6639207e4047",
    "run_m245_scientific_shard.py": "983e598ce97a56848103efb249b3a249e738a3b32c56c124392de15b17dfe2bf",
    "launch_m245_scientific_invocation.py": "71abeebac9968d519d9dc2ea14cd760256a86f384fe4d5e6f3f4e7b06f4141bf",
    "aggregate_m245_spectrum.py": "fc04e9258bb52e5171c54948c5451449e9c96a07a39c9bbab942982371d47c01",
}
EXPECTED_TEST = {
    "test_m245_primary_core.py": "355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626",
    "test_m245_replica_core.py": "e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21",
    "test_m245_scientific_transport.py": "112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d",
    "test_m245_aggregation.py": "6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6",
}
CHECKSUM_EXTRAS = [
    "M245_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.md",
    "M245_SHA256SUMS_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.txt",
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md",
    "M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md",
    "M245_SHA256SUMS_SCIENTIFIC_TDD_RED_V2_20260810.txt",
    "M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md",
    "M245_SHA256SUMS_V2_OVERLAY2_20260810.txt",
    "M245_FROZEN_MANIFEST_V2_20260810.json",
    "M245_SHA256SUMS_V2_20260810.txt",
]
RECEIPT_NAME = "M245_SCIENTIFIC_TDD_GREEN_RECEIPT_20260810.md"
CHECKSUM_NAME = "M245_SHA256SUMS_SCIENTIFIC_TDD_GREEN_20260810.txt"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    done = (LOGS / "DONE").read_text().strip()
    if done != "GREEN_ALL_ZERO":
        raise SystemExit(f"refusing: DONE marker is {done!r}")
    rows = []
    for line in (LOGS / "progress.log").read_text().splitlines():
        n, name, start, end, exit_code = line.split("|")
        rows.append((int(n), name, start, end, int(exit_code)))
    if [r[0] for r in rows] != [1, 2, 3, 4] or [r[1] for r in rows] != TESTS:
        raise SystemExit("refusing: progress log is not the exact serial four-command record")
    if any(r[4] != 0 for r in rows):
        raise SystemExit("refusing: a command exited nonzero")
    for name, expected in {**EXPECTED_SOURCE, **EXPECTED_TEST}.items():
        observed = sha256(AUTH / name)
        if observed != expected:
            raise SystemExit(f"refusing: post-run hash drift {name} {observed}")
    if (AUTH / RECEIPT_NAME).exists() or (AUTH / CHECKSUM_NAME).exists():
        raise SystemExit("refusing: GREEN evidence already exists")

    lines = []
    lines.append("# M245 scientific dummy-only GREEN receipt")
    lines.append("")
    lines.append("Date: 2026-08-10 UTC")
    lines.append("Status: `GREEN_ALL_FOUR_COMMANDS_EXIT_ZERO_DUMMY_ONLY_NO_SCIENTIFIC_AUTHORITY`")
    lines.append("")
    lines.append("Issued under `M245_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.md`")
    lines.append("(committed dummy-only implementation authority commit")
    lines.append("`9886acd7d1eb9f7e887bed70c516e6b0de22b58b`) as activated by")
    lines.append("`M245_SCIENTIFIC_IMPLEMENTATION_ERRATUM1_20260810.md` (docs-only activation")
    lines.append("commit `76b446c075343b6b9633156f0d0617af5a417666`). This receipt confers no")
    lines.append("scientific authority, census, trigger, shard, aggregation, score, FLOP,")
    lines.append("estimator, or credit claim of any kind (I1.8/I1.9). It contains no")
    lines.append("self-hash, no hash of its own checksum, and no future commit hash.")
    lines.append("")
    lines.append("Static gate before GREEN 1: the complete I1.6 inspection passed twice via")
    lines.append("independent read-only, non-executing reviews (reviewer A authority-first,")
    lines.append("reviewer B test-first), each binding the exact ten SHA-256 values below;")
    lines.append("both returned STATIC VERDICT: PASS before any command ran.")
    lines.append("")
    lines.append("## Frozen implementation candidate (six sources)")
    lines.append("")
    lines.append("```text")
    for name in SOURCES:
        raw = (AUTH / name).read_bytes()
        lines.append(f"{hashlib.sha256(raw).hexdigest()}  {len(raw):>7d} bytes  {name}")
    lines.append("```")
    lines.append("")
    lines.append("## Frozen test authority (four tests, byte-identical to I1.1)")
    lines.append("")
    lines.append("```text")
    for name in TESTS:
        raw = (AUTH / name).read_bytes()
        lines.append(f"{hashlib.sha256(raw).hexdigest()}  {len(raw):>7d} bytes  {name}")
    lines.append("```")
    lines.append("")
    lines.append("## The four exact serial one-shot commands (I1.7)")
    lines.append("")
    lines.append("Interpreter (sha256 verified before command one):")
    lines.append("```text")
    lines.append(PY)
    lines.append("4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262")
    lines.append("```")
    lines.append("Working directory for every command:")
    lines.append("```text")
    lines.append(str(AUTH))
    lines.append("```")
    lines.append("")
    for n, name, start, end, exit_code in rows:
        out = LOGS / f"cmd{n}.out"
        err = LOGS / f"cmd{n}.err"
        out_raw = out.read_bytes()
        err_raw = err.read_bytes()
        lines.append(f"### Command {n}")
        lines.append("")
        lines.append("```text")
        lines.append(f"argv       : [{PY}, -B, -m, unittest, -v, {name}]")
        lines.append(f"utc_start  : {start}")
        lines.append(f"utc_end    : {end}")
        lines.append(f"exit_code  : {exit_code}")
        lines.append(f"stdout     : {len(out_raw)} bytes  sha256={hashlib.sha256(out_raw).hexdigest()}")
        lines.append(f"stderr     : {len(err_raw)} bytes  sha256={hashlib.sha256(err_raw).hexdigest()}")
        tail = err_raw.decode("utf-8", errors="replace").strip().splitlines()
        summary = [t for t in tail if t.startswith("Ran ") or t == "OK"]
        for t in summary:
            lines.append(f"unittest   : {t}")
        lines.append("```")
        lines.append("")
    lines.append("Executed exactly once each, serially, in the frozen order, with no")
    lines.append("combined discovery, no parallel runner, no coverage wrapper, no pytest,")
    lines.append("no alternate interpreter or cwd, no environment injection, no test")
    lines.append("selection or skip conversion, and no second attempt. The six source and")
    lines.append("four test hashes above were re-verified byte-identical immediately before")
    lines.append("command one and immediately after command four.")
    lines.append("")
    lines.append("## Post-command census")
    lines.append("")
    lines.append("```text")
    lines.append("E00:E07 decoded_or_evaluated=0")
    lines.append("real_fixture_values_used=0")
    lines.append("production_dispatches=0")
    lines.append("real_shard_directories_or_files_created=0")
    lines.append("pretrigger_censuses_created=0")
    lines.append("scientific_triggers_created=0")
    lines.append("aggregation_authorities_or_outputs_created=0")
    lines.append("responses_or_providers_created=0")
    lines.append("network_or_submission_actions=0")
    lines.append("```")
    lines.append("")
    lines.append("Evidence: the four suites exercise only their frozen dummy events outside")
    lines.append("E00:E07, dummy meters, test-owned temporary directories, and temporary Git")
    lines.append("repositories; after command four the authority directory holds no shard,")
    lines.append("census, trigger, static-audit, or aggregation artifact, the real shard")
    lines.append("directory `corpus/whestbench/experiments/m245_fable_spectrum_shards` is")
    lines.append("absent, and the only authority-directory additions across the run set are")
    lines.append("this receipt and its checksum, both created after command four.")
    lines.append("")
    lines.append("Per I1.9 this run set stops here: no static-audit artifact, pretrigger")
    lines.append("census, trigger, shard, or aggregation step is authorized by this receipt.")
    lines.append("")
    receipt_text = "\n".join(lines)
    (AUTH / RECEIPT_NAME).write_bytes(receipt_text.encode("utf-8"))

    checksum_lines = []
    checksum_lines.append(f"{sha256(AUTH / RECEIPT_NAME)}  {RECEIPT_NAME}")
    for name in CHECKSUM_EXTRAS[:2]:
        checksum_lines.append(f"{sha256(AUTH / name)}  {name}")
    for name in SOURCES:
        checksum_lines.append(f"{sha256(AUTH / name)}  {name}")
    for name in TESTS:
        checksum_lines.append(f"{sha256(AUTH / name)}  {name}")
    for name in CHECKSUM_EXTRAS[2:]:
        checksum_lines.append(f"{sha256(AUTH / name)}  {name}")
    (AUTH / CHECKSUM_NAME).write_bytes(("\n".join(checksum_lines) + "\n").encode("ascii"))
    print(json.dumps({
        "receipt": sha256(AUTH / RECEIPT_NAME),
        "checksum": sha256(AUTH / CHECKSUM_NAME),
        "lines": len(checksum_lines),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
