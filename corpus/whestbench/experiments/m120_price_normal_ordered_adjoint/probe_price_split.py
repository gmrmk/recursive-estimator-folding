"""Generated-only spectral probe for the normal-ordered Price gate kernel.

This is a theory probe, not a WHestBench estimator.  It generates fresh He
networks, propagates the existing Gaussian full-covariance background, and
measures the exact decomposition

    K = p p^T + diag(p - p^2) + E,

where K_ij = P(Z_i > 0, Z_j > 0) is the Price covariance pullback and E has
zero diagonal.  The first term preserves a shared CP representation and the
second resets it to at most n shared atoms after an affine pull.  Only E can
cause the generic Schur-rank multiplication used in the old n^4 no-go.

No contest weights, truths, scorer, or prior outcome artifact are read.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
FULLCOV_DIR = HERE.parent / "fullcov_gaussian_mm"
ADJOINT_DIR = HERE.parent / "adjoint_cumulant"
sys.path.insert(0, str(FULLCOV_DIR))
sys.path.insert(0, str(ADJOINT_DIR))

from fullcov import phi2_gauss10, relu_gaussian_moments  # noqa: E402
from adjoint_born import _normal_cdf, build_gaussian_background  # noqa: E402


def _he_weights(seed: int, width: int, depth: int) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(seed)
    scale = math.sqrt(2.0 / width)
    return tuple(
        rng.normal(0.0, scale, size=(width, width)).astype(np.float64)
        for _ in range(depth)
    )


def _best_rank_tail(singular_values: np.ndarray, rank: int) -> float:
    energy = np.square(singular_values)
    denominator = float(np.sum(energy))
    if denominator == 0.0:
        return 0.0
    return math.sqrt(float(np.sum(energy[rank:])) / denominator)


def _layer_record(layer, probe_weight: np.ndarray) -> dict[str, object]:
    covariance = np.asarray(layer.covariance, dtype=np.float64)
    sigma = np.sqrt(np.maximum(np.diag(covariance), 1e-14))
    alpha = np.asarray(layer.mean, dtype=np.float64) / sigma
    probability = _normal_cdf(alpha)
    correlation = np.clip(
        covariance / np.outer(sigma, sigma), -1.0 + 1e-12, 1.0 - 1e-12
    )
    kernel = phi2_gauss10(alpha[:, None], alpha[None, :], correlation)
    np.fill_diagonal(kernel, probability)
    kernel = 0.5 * (kernel + kernel.T)

    separable = np.outer(probability, probability)
    diagonal_reset = np.diag(probability - probability * probability)
    connected = kernel - separable - diagonal_reset
    np.fill_diagonal(connected, 0.0)
    connected = 0.5 * (connected + connected.T)

    singular = np.linalg.svd(connected, compute_uv=False)
    kernel_norm = float(np.linalg.norm(kernel, ord="fro"))
    connected_norm = float(np.linalg.norm(connected, ord="fro"))

    # The actual terminal covariance adjoint begins as w_o w_o^T.  Probe all
    # output columns at once and report the distribution of omitted Schur
    # action relative to the exact Price action.
    ratios = []
    for output in range(probe_weight.shape[1]):
        w = probe_weight[:, output]
        outer = np.outer(w, w)
        exact = kernel * outer
        omitted = connected * outer
        denominator = float(np.linalg.norm(exact, ord="fro"))
        ratios.append(
            0.0
            if denominator == 0.0
            else float(np.linalg.norm(omitted, ord="fro")) / denominator
        )

    eigenvalues = np.linalg.eigvalsh(connected)
    return {
        "alpha_abs_mean": float(np.mean(np.abs(alpha))),
        "offdiag_corr_rms": float(
            np.sqrt(
                np.mean(
                    np.square(correlation[~np.eye(correlation.shape[0], dtype=bool)])
                )
            )
        ),
        "connected_over_kernel_fro": connected_norm / kernel_norm,
        "connected_spectral_over_fro": (
            0.0 if connected_norm == 0.0 else float(singular[0]) / connected_norm
        ),
        "connected_negative_eigen_fraction": float(np.mean(eigenvalues < -1e-12)),
        "best_rank_tail": {
            str(rank): _best_rank_tail(singular, rank)
            for rank in (1, 2, 4, 8, 16, 32, 64, 128)
            if rank < singular.size
        },
        "rank1_adjoint_omission_ratio": {
            "mean": float(np.mean(ratios)),
            "median": float(np.median(ratios)),
            "q90": float(np.quantile(ratios, 0.90)),
            "max": float(np.max(ratios)),
        },
    }


def run(
    width: int,
    depth: int,
    seeds: tuple[int, ...],
    include_layers: bool = True,
) -> dict[str, object]:
    networks = []
    all_records = []
    for seed in seeds:
        weights = _he_weights(seed, width, depth)
        layers, _, _ = build_gaussian_background(weights, relu_gaussian_moments)
        records = [
            _layer_record(layer, weights[-1])
            for layer in layers
        ]
        networks.append({"seed": seed, "layers": records})
        all_records.extend(records)

    def aggregate(path: tuple[str, ...]) -> dict[str, float]:
        values = []
        for record in all_records:
            value: object = record
            for key in path:
                value = value[key]  # type: ignore[index]
            values.append(float(value))
        array = np.asarray(values, dtype=np.float64)
        return {
            "mean": float(np.mean(array)),
            "median": float(np.median(array)),
            "q90": float(np.quantile(array, 0.90)),
            "max": float(np.max(array)),
        }

    aggregate_values = {
        "alpha_abs_mean": aggregate(("alpha_abs_mean",)),
        "offdiag_corr_rms": aggregate(("offdiag_corr_rms",)),
        "connected_over_kernel_fro": aggregate(("connected_over_kernel_fro",)),
        "rank1_omission_mean": aggregate(("rank1_adjoint_omission_ratio", "mean")),
        "rank1_omission_q90": aggregate(("rank1_adjoint_omission_ratio", "q90")),
        "rank1_omission_max": aggregate(("rank1_adjoint_omission_ratio", "max")),
    }
    for rank in (16, 32, 64, 128):
        if rank < width:
            aggregate_values[f"best_rank_tail_{rank}"] = aggregate(
                ("best_rank_tail", str(rank))
            )

    result: dict[str, object] = {
        "provenance": {
            "generated_only": True,
            "width": width,
            "depth": depth,
            "seeds": list(seeds),
            "numpy": np.__version__,
        },
        "aggregate": aggregate_values,
    }
    if include_layers:
        result["networks"] = networks
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--depth", type=int, default=32)
    parser.add_argument("--seeds", type=int, nargs="+", default=[120001, 120002])
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    result = run(
        args.width,
        args.depth,
        tuple(args.seeds),
        include_layers=not args.aggregate_only,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
