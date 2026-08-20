#!/usr/bin/env python3
"""Verify the private WHestBench handoff without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "corpus" / "whestbench"
HANDOFF = CORPUS / "handoff"
MANIFEST = HANDOFF / "BUNDLE_SHA256SUMS.txt"
PROMPT = HANDOFF / "FABLE5_ASCII_RESUME_PROMPT_20260807.txt"
PROMPT_COPY = CORPUS / "headroom" / PROMPT.name
LEDGER = CORPUS / "headroom" / "fold_ledger.json"
GRAPH = CORPUS / "graph" / "graph.json"
EXPECTED_LEDGER_COUNT = 213
EXPECTED_GRAPH_NODES = 291
EXPECTED_GRAPH_EDGES = 593
EXPECTED_CHAMPION_HASH = (
    "bc2ec39558c76a67b12b587ca4ee70bb1e8921489643d83707e052d086e8ae36"
)
V31_ARCHIVE = (
    CORPUS
    / "experiments"
    / "v31_guards"
    / "submission_kerdock_v31_guards_20260808.tar.gz"
)
EXPECTED_V31_HASH = (
    "8382e269c9b32e0935492734ddf8182560120f7e9331621aa18839d5d1f4ea06"
)
FORBIDDEN_SUFFIXES = {
    ".dll",
    ".dylib",
    ".env",
    ".exe",
    ".gz",
    ".key",
    ".npy",
    ".npz",
    ".onnx",
    ".pem",
    ".pt",
    ".pth",
    ".pyc",
    ".so",
    ".tar",
    ".zip",
}
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".venv", "node_modules"}
ALLOWED_BINARY_PATHS = {
    "corpus/whestbench/experiments/a_series_granular_adversarial/a4_det_run1.npz",
    "corpus/whestbench/experiments/a_series_granular_adversarial/a4_det_run2.npz",
    "corpus/whestbench/experiments/m180_design_strength/m180_g0_partial_net101.npz",
    "corpus/whestbench/experiments/m180_design_strength/m180_g0_partial_net202.npz",
    "corpus/whestbench/experiments/m180_design_strength/m180_g0_partial_net303.npz",
    "corpus/whestbench/experiments/m181_terminal_smoothing/m181_g0_partial_net101.npz",
    "corpus/whestbench/experiments/m181_terminal_smoothing/m181_g0_partial_net202.npz",
    "corpus/whestbench/experiments/m181_terminal_smoothing/m181_g0_partial_net303.npz",
    "corpus/whestbench/experiments/m181_terminal_smoothing/m181_truth_net101.npz",
    "corpus/whestbench/experiments/m181_terminal_smoothing/m181_truth_net202.npz",
    "corpus/whestbench/experiments/m181_terminal_smoothing/m181_truth_net303.npz",
    "corpus/whestbench/experiments/pb1_premise_battery/m191_g0b_partial_net101.npz",
    "corpus/whestbench/experiments/pb1_premise_battery/m191_g0b_partial_net202.npz",
    "corpus/whestbench/experiments/pb1_premise_battery/m191_g0b_partial_net303.npz",
    "corpus/whestbench/experiments/pb1_premise_battery/p2_partial_net101.npz",
    "corpus/whestbench/experiments/pb1_premise_battery/p2_partial_net202.npz",
    "corpus/whestbench/experiments/pb1_premise_battery/p2_partial_net303.npz",
    "corpus/whestbench/experiments/t3_fold3_deterministic_cap/submission_fold3cap_n39936_20260808.tar.gz",
    "corpus/whestbench/experiments/v31_guards/package_source/kerdock_phases.npz",
    "corpus/whestbench/experiments/v31_guards/package_source/sobol_owen_u32.npz",
    "corpus/whestbench/experiments/v31_guards/submission_kerdock_v31_guards_20260808.tar.gz",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def parse_manifest() -> dict[str, str]:
    if not MANIFEST.is_file():
        fail(f"missing manifest: {MANIFEST.relative_to(REPO)}")
    entries: dict[str, str] = {}
    line_re = re.compile(r"^([0-9a-f]{64})  (.+)$")
    for number, raw in enumerate(MANIFEST.read_text(encoding="ascii").splitlines(), 1):
        if not raw or raw.startswith("#"):
            continue
        match = line_re.fullmatch(raw)
        if not match:
            fail(f"invalid manifest line {number}: {raw!r}")
        value, relative = match.groups()
        if relative in entries:
            fail(f"duplicate manifest path: {relative}")
        entries[relative] = value
    return entries


def verify_manifest(entries: dict[str, str]) -> None:
    expected_paths = {
        path.relative_to(REPO).as_posix()
        for path in CORPUS.rglob("*")
        if path.is_file() and path != MANIFEST
    }
    listed_paths = set(entries)
    missing = sorted(expected_paths - listed_paths)
    extra = sorted(listed_paths - expected_paths)
    if missing:
        fail(f"manifest omits {len(missing)} file(s), first={missing[0]}")
    if extra:
        fail(f"manifest lists {len(extra)} absent file(s), first={extra[0]}")
    bad: list[str] = []
    for relative, expected in sorted(entries.items()):
        actual = digest(REPO / relative)
        if actual != expected:
            bad.append(relative)
    if bad:
        fail(f"SHA256 mismatch in {len(bad)} file(s), first={bad[0]}")


def verify_firewall() -> None:
    offenders: list[str] = []
    for path in CORPUS.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(REPO).as_posix()
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            if relative not in ALLOWED_BINARY_PATHS:
                offenders.append(relative)
        elif FORBIDDEN_PARTS.intersection(path.parts):
            offenders.append(relative)
    if offenders:
        fail(f"forbidden cache/binary artifact(s), first={sorted(offenders)[0]}")


def verify_prompt() -> None:
    data = PROMPT.read_bytes()
    non_ascii = [index for index, value in enumerate(data) if value > 0x7F]
    if non_ascii:
        fail(f"Fable prompt is not 7-bit ASCII at byte {non_ascii[0]}")
    if PROMPT_COPY.read_bytes() != data:
        fail("headroom and handoff Fable prompt copies differ")
    required = [
        b"Standing goal:",
        b"M178 is exactly one mutation",
        b"BUNDLE_SHA256SUMS.txt",
        b"immutable champion",
        b"291 nodes, 593 edges",
    ]
    for marker in required:
        if marker not in data:
            fail(f"Fable prompt missing marker: {marker.decode('ascii')}")


def verify_ledger() -> None:
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != EXPECTED_LEDGER_COUNT:
        fail(f"ledger candidate count != {EXPECTED_LEDGER_COUNT}")
    ids = [item.get("id") for item in candidates]
    if len(ids) != len(set(ids)):
        fail("ledger has duplicate candidate IDs")
    champion = payload.get("invariants", {}).get("champion_hash", "")
    if EXPECTED_CHAMPION_HASH not in champion:
        fail("ledger champion hash changed or disappeared")


def verify_graph() -> None:
    payload = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = payload.get("nodes", [])
    links = payload.get("links", [])
    if len(nodes) != EXPECTED_GRAPH_NODES or len(links) != EXPECTED_GRAPH_EDGES:
        fail(
            "graph dimensions changed: "
            f"nodes={len(nodes)} links={len(links)}, expected "
            f"{EXPECTED_GRAPH_NODES}/{EXPECTED_GRAPH_EDGES}"
        )
    node_ids = [node.get("id") for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        fail("graph has duplicate node IDs")


def verify_guard_archive() -> None:
    if not V31_ARCHIVE.is_file():
        fail("missing v3.1 guard archive")
    if digest(V31_ARCHIVE) != EXPECTED_V31_HASH:
        fail("v3.1 guard archive hash changed")


def main() -> int:
    try:
        entries = parse_manifest()
        verify_manifest(entries)
        verify_firewall()
        verify_prompt()
        verify_ledger()
        verify_graph()
        verify_guard_archive()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"HANDOFF VERIFY: FAIL: {exc}", file=sys.stderr)
        return 1
    tests = sum(1 for path in CORPUS.rglob("test_*.py") if path.is_file())
    files = sum(1 for path in CORPUS.rglob("*") if path.is_file())
    print("HANDOFF VERIFY: PASS")
    print(f"manifest_entries={len(entries)} corpus_files={files} test_files={tests}")
    print(f"ledger_candidates={EXPECTED_LEDGER_COUNT}")
    print(f"graph_nodes={EXPECTED_GRAPH_NODES} graph_edges={EXPECTED_GRAPH_EDGES}")
    print(f"fable_prompt_bytes={PROMPT.stat().st_size} ascii_only=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
