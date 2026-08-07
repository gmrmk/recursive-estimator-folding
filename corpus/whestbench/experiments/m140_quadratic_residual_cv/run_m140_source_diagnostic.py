"""Predeclared target-free M140 coefficient/influence diagnostic.

This script deliberately stops at local source tables.  It does not invoke
M121 conversion, M125 propagation, a contest model, a scorer, an outcome, or
an efficacy comparison.  It measures only whether subtracting the exact
dimensionless quadratic jet changes the local coefficient and fixed-proposal
source-influence distribution on frozen generated Gaussian states.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m129_source_frechet_tangent",
    "m131_trivariate_boundary_stream",
    "m126_repeated_output_source_contraction",
    "m133_ht_hidden_edge",
    "m140_quadratic_residual_cv",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m129_source_frechet import build_state_frechet  # noqa: E402
from m131_trivariate_boundary_stream import conditional_collision211_defect_dot  # noqa: E402
from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m133_ht_hidden_edge import collision211_factored_proposal, collision211_feature  # noqa: E402
from m140_quadratic_residual_cv import quadratic_211_tensor, standardize_211_tensor  # noqa: E402


CONFIG = {
    "scope": "target-free local coefficient/influence diagnostic only",
    "cells": [{"width": 5, "seed": 140711}, {"width": 6, "seed": 140712}],
    "oracle": "M131 independent conditional 32/48-node rule, 24 series terms",
    "proposal": "M133 fixed three-bank plus 5% uniform rescue, used only to compute fixed-q influence moments",
    "forbidden": ["M121", "M125", "contest target", "scorer", "outcome screen", "leaderboard", "submission"],
}


def generated_state(width: int, seed: int):
    rng = np.random.default_rng(seed)
    factor = np.eye(width) + 0.018 * rng.normal(size=(width, width))
    covariance = factor @ factor.T + 0.55 * np.eye(width)
    sigma = np.sqrt(np.diag(covariance))
    mean = rng.normal(scale=0.13, size=width) * sigma
    weight = 0.82 * np.eye(width) + rng.normal(scale=0.035, size=(width, width))
    tangent = build_state_frechet(mean, covariance, np.zeros(width), np.zeros((width, width)))
    return tangent, weight


def exact_physical_table(tangent: object) -> tuple[np.ndarray, float]:
    n = tangent.state.mean.size
    result = np.zeros((n, n, n), dtype=np.float64)
    worst = 0.0
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                if len({i, j, k}) != 3:
                    continue
                value, _dot, certificate = conditional_collision211_defect_dot(
                    tangent, i, j, k, coarse_order=32, fine_order=48, series_terms=24
                )
                worst = max(worst, float(certificate.value_disagreement))
                if certificate.value_disagreement > 4e-5:
                    raise ArithmeticError("paired M131 quadrature certification failed")
                result[i, j, k] = result[i, k, j] = value
    return result, worst


def table_norm_sq(table: dict[str, np.ndarray]) -> float:
    return float(sum(np.sum(np.asarray(table[key]) ** 2) for key in ("k4_aaab", "k4_aabb")))


def influence_second_moment(coefficient: np.ndarray, weight: np.ndarray, proposal: object) -> tuple[float, float]:
    """Return E_q||Z||^2 and trace-variance for one fixed-q HH draw."""

    source = collision211_repeated_exact(coefficient, weight)
    mean_norm_sq = table_norm_sq(source)
    second = 0.0
    n = coefficient.shape[0]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) != 3:
                    continue
                q = float(proposal.probability(i, j, k))
                feature = collision211_feature(weight, i, j, k)
                feature_norm_sq = float(np.sum(feature["k4_aaab"] ** 2) + np.sum(feature["k4_aabb"] ** 2))
                second += coefficient[i, j, k] ** 2 * feature_norm_sq / (4.0 * q)
    return second, max(0.0, second - mean_norm_sq)


def run_cell(width: int, seed: int) -> dict[str, float | int]:
    tangent, weight = generated_state(width, seed)
    physical, disagreement = exact_physical_table(tangent)
    standardized = standardize_211_tensor(physical, tangent.state.relu_scale)
    jet = quadratic_211_tensor(tangent.state.bridge)
    residual = standardized - jet
    effective_weight = tangent.state.relu_scale[:, None] * weight
    proposal = collision211_factored_proposal(tangent.state.bridge, effective_weight, uniform_mixture=0.05)
    full_second, full_variance = influence_second_moment(standardized, effective_weight, proposal)
    residual_second, residual_variance = influence_second_moment(residual, effective_weight, proposal)
    full_table = collision211_repeated_exact(standardized, effective_weight)
    residual_table = collision211_repeated_exact(residual, effective_weight)
    coefficient_norm = float(np.sum(standardized**2))
    jet_norm = float(np.sum(jet**2))
    residual_norm = float(np.sum(residual**2))
    cross = float(np.sum(jet * residual))
    return {
        "width": width,
        "seed": seed,
        "certificate_max_disagreement": disagreement,
        "coefficient_l2_sq": coefficient_norm,
        "jet_l2_sq": jet_norm,
        "residual_l2_sq": residual_norm,
        "jet_residual_inner_product": cross,
        "residual_l2_fraction": residual_norm / coefficient_norm if coefficient_norm else math.nan,
        "full_source_table_l2_sq": table_norm_sq(full_table),
        "residual_source_table_l2_sq": table_norm_sq(residual_table),
        "full_hh_influence_second_moment": full_second,
        "residual_hh_influence_second_moment": residual_second,
        "full_hh_influence_variance_trace": full_variance,
        "residual_hh_influence_variance_trace": residual_variance,
        "residual_to_full_influence_variance_ratio": residual_variance / full_variance if full_variance else math.nan,
    }


def main() -> None:
    result = {
        "config": CONFIG,
        "contest_data_accessed": False,
        "outcome_screen_run": False,
        "cells": [run_cell(**cell) for cell in CONFIG["cells"]],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
