"""Write the non-executable M124 draft manifest and source hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from m124_protocol import draft_manifest


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parent
    manifest = draft_manifest()
    sources = (
        root / "m124_shared_projector.py",
        root / "m124_protocol.py",
        root / "run_m124_falsifier.py",
        root / "test_m124_shared_projector.py",
    )
    manifest["source_hashes"] = {path.name: sha(path) for path in sources}
    destination = root / "DRAFT_MANIFEST.json"
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
