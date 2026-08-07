"""Minimal deployment-only constants and deterministic seed derivation for M145.

This module intentionally has no dependency on the development-only NumPy
implementation.  The import closure of ``m145_deployable_estimator`` is
limited to the standard library, flopscope/whestbench, and the sealed
Formal-L1 source files.
"""

from __future__ import annotations

import hashlib


DIMENSION = 256
TOTAL_FRAMES = 126
PILOT_FRAMES = 4
MAIN_FRAMES = TOTAL_FRAMES - PILOT_FRAMES
PILOT_LINES = PILOT_FRAMES * DIMENSION
RANK = 16
EPSILON = 0.80
LAMBDA_LOWER = 0.25
LAMBDA_UPPER = 1.75
TIE_ULPS = 64.0
PROTOCOL_TAG = 145


def _child_seed(setup_seed: int, label: str) -> int:
    """Stable domain-separated seed without a host RNG dependency.

    This descendant deliberately changes the frozen raw-QR setup law: pilot
    and main matrices receive independent SHA-256-derived seeds, and every
    prediction child is separately domain-separated.  No legacy evidence is
    reused as a result for this descendant.
    """

    payload = f"m145-deployable-v1|{PROTOCOL_TAG}|{int(setup_seed)}|{label}".encode(
        "ascii"
    )
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def setup_child_seeds(setup_seed: int) -> tuple[int, int]:
    return _child_seed(setup_seed, "pilot-qr"), _child_seed(setup_seed, "main-qr")


def predict_child_seeds(setup_seed: int, mlp_seed: int) -> dict[str, int]:
    prefix = f"predict-{int(mlp_seed)}"
    return {
        "mixture_labels": _child_seed(setup_seed, prefix + "-mixture"),
        "uniform_anchors": _child_seed(setup_seed, prefix + "-uniform"),
        "acg_latents": _child_seed(setup_seed, prefix + "-acg"),
    }
