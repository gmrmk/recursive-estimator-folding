"""Structural FlopScope probe for M144; no target data or accuracy comparison."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fullcov_gaussian_mm"))

import flopscope as flops  # noqa: E402
import flopscope.numpy as fnp  # noqa: E402
from estimator import _relu_fullcov  # noqa: E402


def main() -> None:
    """Measure exactly one K=1 baseline trace on synthetic, target-shaped arrays."""
    width, depth = 256, 32
    rng = fnp.random.default_rng(144)
    weights = [
        fnp.asarray(rng.standard_normal((width, width)), dtype=fnp.float64)
        for _ in range(depth)
    ]
    off_diagonal = 1.0 - fnp.eye(width, dtype=fnp.float64)
    mean = fnp.zeros(width, dtype=fnp.float64)
    covariance = fnp.eye(width, dtype=fnp.float64)
    flops.budget_reset()
    with flops.budget(272_000_000_000, quiet=True):
        for weight in weights:
            pre_mean = mean @ weight
            pre_covariance = flops.as_symmetric(
                weight.T @ (covariance @ weight), symmetry=(0, 1)
            )
            mean, covariance = _relu_fullcov(
                pre_mean, pre_covariance, off_diagonal
            )
    summary = flops.budget_summary_dict()
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
