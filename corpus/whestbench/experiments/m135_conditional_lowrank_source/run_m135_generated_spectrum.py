"""Generated-only covariance-structure audit for M135.

The chain is freshly sampled and exists only to test whether deep dense
Gaussian-closure states actually exhibit an exact or nearly exact low-rank
factor-analysis structure.  No benchmark architecture, weights, or outcomes
are read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in ("m120_price_normal_ordered_adjoint",):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)
sys.path.insert(0, str(HERE))

from m120c_analytic_dense_reference import analytic_relu_gaussian_moments  # noqa: E402
from m135_conditional_lowrank_source import (  # noqa: E402
    generic_factor_rank_dimension_lower_bound,
    gaussian_bridge_log_second_moment,
    isotropic_diagonal_eigen_approximation,
)


def generated_chain_covariance(width: int, depth: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    seed_factor = np.eye(width) + 0.028 * rng.normal(size=(width, width))
    covariance = seed_factor @ seed_factor.T + 0.35 * np.eye(width)
    mean = rng.normal(scale=0.18, size=width)
    for _ in range(depth):
        weight = rng.normal(scale=np.sqrt(2.0 / width), size=(width, width))
        activation_mean, activation_covariance = analytic_relu_gaussian_moments(mean, covariance)
        mean = activation_mean @ weight
        covariance = weight.T @ activation_covariance @ weight
        covariance = 0.5 * (covariance + covariance.T)
        # The generated closure can carry tiny negative roundoff at high
        # depth.  A fixed 1e-10 ridge is a numerical floor, not fitting.
        covariance += 1.0e-10 * np.eye(width)
    return covariance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--depth", type=int, default=8)
    args = parser.parse_args()
    covariance = generated_chain_covariance(args.width, args.depth, 135_900)
    ranks = sorted({rank for rank in (2, 4, 8, 16, 32, 64, 128, 234, args.width - 1) if 0 <= rank < args.width})
    spectrum = np.linalg.eigvalsh(covariance)[::-1]
    rows = []
    for rank in ranks:
        approximation = isotropic_diagonal_eigen_approximation(covariance, rank)
        rows.append({
            "rank": rank,
            "residual_trace_fraction": approximation.residual_trace_fraction,
            "residual_frobenius_fraction": approximation.residual_frobenius_fraction,
            "residual_psd_min_eigenvalue": float(np.linalg.eigvalsh(approximation.residual)[0]),
            "exact_density_ratio_log_second_moment": gaussian_bridge_log_second_moment(
                approximation.base.covariance(), covariance
            ),
        })
    print(json.dumps({
        "contract": {
            "generated_only": True,
            "fresh_dense_gaussian_closure_chain": True,
            "not_a_contest_state": True,
            "width": args.width,
            "depth": args.depth,
        },
        "generic_dimension_lower_bound_for_factor_rank": generic_factor_rank_dimension_lower_bound(args.width),
        "condition_number": float(spectrum[0] / spectrum[-1]),
        "top_eigenvalue_trace_fractions": [float(value / spectrum.sum()) for value in spectrum[:min(8, args.width)]],
        "isotropic_diagonal_plus_eigenfactor_diagnostics": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
