"""Generated-only M135 source/output variance and allocation audit.

No contest model, score, public instance, or target is loaded.  The only
states are fresh exact diagonal-plus-rank-two Gaussian factor models.  The
audit compares equal-count full Gaussian normal ordering against the
Rao--Blackwellized common-factor source, then prints the protected target-width
allocation that would be required to retain the exact reference algorithm.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in ("m129_source_frechet_tangent", "m131_trivariate_boundary_stream"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)
sys.path.insert(0, str(HERE))

from m129_source_frechet import build_state_frechet  # noqa: E402
from m131_trivariate_boundary_stream import one_delay_edgeworth_source, sampled_normal_ordered_source  # noqa: E402
from m135_conditional_lowrank_source import (  # noqa: E402
    conditional_lowrank_repeated_source,
    conditional_reference_cost_envelope,
    exact_diagonal_factor_state,
    gaussian_factor_samples,
)


def factor_rule_2d(order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = np.sqrt(2.0) * nodes
    weights = weights / np.sqrt(np.pi)
    left, right = np.meshgrid(nodes, nodes, indexing="ij")
    qleft, qright = np.meshgrid(weights, weights, indexing="ij")
    return np.column_stack((left.ravel(), right.ravel())), (qleft * qright).ravel()


def generated_problem(width: int, seed: int):
    rng = np.random.default_rng(seed)
    d = 0.65 + rng.random(width)
    loadings = rng.normal(scale=0.19, size=(width, 2))
    factor = exact_diagonal_factor_state(d, loadings)
    mean = rng.normal(scale=0.18, size=width)
    tangent = build_state_frechet(mean, factor.covariance(), np.zeros(width), np.zeros((width, width)))
    weight = rng.normal(scale=0.37, size=(width, width))
    # An independently generated well-conditioned next Gaussian state lets us
    # measure the complete M121 one-delay output functional, rather than only
    # a source-table norm.
    auxiliary = np.eye(width) + 0.03 * rng.normal(size=(width, width))
    next_covariance = auxiliary @ auxiliary.T + 0.5 * np.eye(width)
    next_mean = rng.normal(scale=0.20, size=width)
    probe_mean = rng.normal(size=width)
    probe_covariance = rng.normal(size=(width, width))
    probe_covariance = 0.5 * (probe_covariance + probe_covariance.T)
    return factor, tangent, weight, next_mean, next_covariance, probe_mean, probe_covariance


def functional(repeated, next_mean, next_covariance, probe_mean, probe_covariance) -> float:
    source = one_delay_edgeworth_source(repeated, next_mean, next_covariance)
    return float(probe_mean @ source.mean + np.sum(probe_covariance * source.covariance))


def sample_variance(values: np.ndarray, reference: float) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "variance": float(np.var(values, ddof=1)),
        "squared_bias_vs_quadrature": float((np.mean(values) - reference) ** 2),
        "mse_vs_quadrature": float(np.mean((values - reference) ** 2)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=8)
    parser.add_argument("--common-samples", type=int, default=12)
    parser.add_argument("--repetitions", type=int, default=160)
    args = parser.parse_args()
    if args.width < 4 or args.common_samples < 2:
        raise ValueError("small generated audit requires width>=4 and at least two samples")
    factor, tangent, weight, next_mean, next_covariance, probe_mean, probe_covariance = generated_problem(args.width, 135_700)
    qnodes, qweights = factor_rule_2d(30)
    reference = functional(
        conditional_lowrank_repeated_source(tangent, weight, qnodes, factor, sample_weights=qweights).repeated,
        next_mean, next_covariance, probe_mean, probe_covariance,
    )
    conditional_values = []
    iid_values = []
    for repetition in range(args.repetitions):
        h = gaussian_factor_samples(args.common_samples, 2, 135_800 + repetition)
        conditional_values.append(functional(
            conditional_lowrank_repeated_source(tangent, weight, h, factor).repeated,
            next_mean, next_covariance, probe_mean, probe_covariance,
        ))
        standard = np.random.default_rng(136_000 + repetition).standard_normal((args.common_samples, args.width))
        # M131 transforms standard rows internally by Cholesky; the local
        # state is identical, hence this is an equal-row source comparison.
        iid_values.append(functional(
            sampled_normal_ordered_source(tangent, weight, standard, bank_count=1).repeated,
            next_mean, next_covariance, probe_mean, probe_covariance,
        ))
    conditional_values = np.asarray(conditional_values)
    iid_values = np.asarray(iid_values)
    conditional_summary = sample_variance(conditional_values, reference)
    iid_summary = sample_variance(iid_values, reference)
    result = {
        "contract": {
            "generated_only": True,
            "exact_factor_model": "C=diag(d)+UU^T",
            "factor_rank": 2,
            "common_factor_samples": args.common_samples,
            "repetitions": args.repetitions,
            "complete_repeated_k3_k4": True,
            "complete_m121_output_functional": True,
            "second_order_k3_squared": False,
            "not_a_contest_measurement": True,
        },
        "reference": "30x30 Gauss-Hermite common-factor quadrature; deterministic approximation only",
        "conditional": conditional_summary,
        "m131_iid_equal_rows": iid_summary,
        "variance_ratio_conditional_over_iid": conditional_summary["variance"] / iid_summary["variance"],
        "target_width_exact_reference_cost": {
            "two_samples_per_bank": conditional_reference_cost_envelope(2),
            "three_samples_per_bank": conditional_reference_cost_envelope(3),
            "four_samples_per_bank": conditional_reference_cost_envelope(4),
            "hypothetical_float32_three_samples_per_bank": conditional_reference_cost_envelope(3, dense_dtype="float32"),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
