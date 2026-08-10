"""Read-only locators for the frozen sources. Nothing here is edited."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(
    r"C:/Users/strid/Documents/Codex/2026-08-02/"
    r"https-chatgpt-com-share-6a5556ed-2e1c"
)
SPARSE_DIR = ROOT / "work" / "scorefloor_generation" / "latent_sparse_cubature"
FULLSIGMA_DIR = ROOT / "work" / "scorefloor_generation" / "latent_full_sigma"
RADIAL_DIR = ROOT / "work" / "scorefloor_generation" / "latent_randomized_radial"

FROZEN_IMPL = SPARSE_DIR / "latent_sparse_cubature.py"
FROZEN_CONTRACT = SPARSE_DIR / "premise_contract.json"
FROZEN_FULLCOV = SPARSE_DIR / "corrected_fullcov.py"
ORIGINAL_PARTIAL = SPARSE_DIR / "premise_results.json"
TRUTH_BANK = FULLSIGMA_DIR / "fresh_n64_results.json"

HERE = Path(__file__).resolve().parent

CASES = (
    (64, 16, 18560),
    (64, 16, 18561),
    (64, 16, 18562),
    (64, 16, 18563),
    (64, 32, 18720),
    (64, 32, 18721),
    (64, 32, 18722),
    (64, 32, 18723),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
