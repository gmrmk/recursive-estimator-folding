"""Static M177 ledger verifier: no runtime estimator is introduced."""

from __future__ import annotations

from pathlib import Path
import hashlib


ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "m177_bivariate_relu_primitive.py",
    "test_m177_bivariate_relu_primitive.py",
    "M177_BIVARIATE_RELU_PRIMITIVE_REPORT_20260807.md",
    "M177_FROZEN_MANIFEST_20260807.json",
]


def main() -> None:
    for name in REQUIRED:
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"missing M177 artifact: {name}")
    source = (ROOT / "m177_bivariate_relu_primitive.py").read_text(encoding="utf-8")
    required = ["ZERO_VARIANCE_FACE", "RANK_ONE_PLUS", "RANK_ONE_MINUS", "M177_REFUSE_NO_CERTIFIED"]
    if not all(token in source for token in required):
        raise SystemExit("M177 source is missing an endpoint/fail-closed branch")
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    print({"m177_static": "pass", "source_sha256": digest, "runtime_candidate": False})


if __name__ == "__main__":
    main()
