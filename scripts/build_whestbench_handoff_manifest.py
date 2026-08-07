#!/usr/bin/env python3
"""Deterministically rebuild the private WHestBench corpus SHA-256 manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "corpus" / "whestbench"
MANIFEST = CORPUS / "handoff" / "BUNDLE_SHA256SUMS.txt"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    paths = sorted(
        (
            path
            for path in CORPUS.rglob("*")
            if path.is_file() and path != MANIFEST
        ),
        key=lambda path: path.relative_to(REPO).as_posix(),
    )
    lines = [
        "# Recursive Estimator Folding private WHestBench handoff",
        "# SHA-256; paths are relative to repository root; this file excludes itself.",
    ]
    lines.extend(
        f"{digest(path)}  {path.relative_to(REPO).as_posix()}" for path in paths
    )
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(f"wrote {MANIFEST.relative_to(REPO)} with {len(paths)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
