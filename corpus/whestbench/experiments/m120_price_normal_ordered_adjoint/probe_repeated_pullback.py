"""Generated-only repeated Price-pullback error probe.

For a handful of terminal outputs this computes the exact dense covariance
adjoint and variants that replace the connected gate kernel E by a fixed-rank
spectral truncation at every hidden layer.  It tests whether small one-layer
Schur error stays small under the nonnormal affine/relu reverse product.

This is deliberately a component falsifier: it does not include the other
mean/variance blocks of the full Gaussian-closure Jacobian and cannot promote
an estimator by itself.
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


def _kernel_parts(layer) -> tuple[np.ndarray, np.ndarray]:
    covariance = np.asarray(layer.covariance, dtype=np.float64)
    sigma = np.sqrt(np.maximum(np.diag(covariance), 1e-14))
    alpha = np.asarray(layer.mean, dtype=np.float64) / sigma
    probability = _normal_cdf(alpha)
    correlation = np.clip(
        covariance / np.outer(sigma, sigma), -1.0 + 1e-12, 1.0 - 1e-12
    )
    exact = phi2_gauss10(alpha[:, None], alpha[None, :], correlation)
    np.fill_diagonal(exact, probability)
    exact = 0.5 * (exact + exact.T)
    base = np.outer(probability, probability)
    base += np.diag(probability - probability * probability)
    connected = exact - base
    np.fill_diagonal(connected, 0.0)
    return exact, 0.5 * (connected + connected.T)


def _truncated_kernel(
    exact: np.ndarray,
    connected: np.ndarray,
    rank: int,
) -> np.ndarray:
    base = exact - connected
    if rank <= 0:
        return base
    eigenvalues, eigenvectors = np.linalg.eigh(connected)
    order = np.argsort(np.abs(eigenvalues))[::-1][:rank]
    retained = (eigenvectors[:, order] * eigenvalues[order]) @ eigenvectors[:, order].T
    return base + retained


def _relative(reference: np.ndarray, estimate: np.ndarray) -> tuple[float, float]:
    reference_norm = float(np.linalg.norm(reference, ord="fro"))
    estimate_norm = float(np.linalg.norm(estimate, ord="fro"))
    error = float(np.linalg.norm(estimate - reference, ord="fro"))
    cosine_denominator = reference_norm * estimate_norm
    cosine = (
        1.0
        if cosine_denominator == 0.0 and error == 0.0
        else 0.0
        if cosine_denominator == 0.0
        else float(np.sum(reference * estimate)) / cosine_denominator
    )
    return error / max(reference_norm, 1e-300), cosine


def run(
    width: int,
    depth: int,
    seed: int,
    outputs: tuple[int, ...],
    ranks: tuple[int, ...],
) -> dict[str, object]:
    weights = _he_weights(seed, width, depth)
    layers, _, _ = build_gaussian_background(weights, relu_gaussian_moments)
    parts = [_kernel_parts(layer) for layer in layers]

    records = []
    for output in outputs:
        if output < 0 or output >= width:
            raise ValueError(f"output {output} outside width {width}")
        terminal = weights[-1][:, output]
        exact_adjoint = np.outer(terminal, terminal)
        approximations = {rank: exact_adjoint.copy() for rank in ranks}
        layer_records = []

        for layer_index in range(len(layers) - 1, -1, -1):
            exact_kernel, connected = parts[layer_index]
            exact_adjoint = exact_kernel * exact_adjoint
            for rank in ranks:
                kernel = _truncated_kernel(exact_kernel, connected, rank)
                approximations[rank] = kernel * approximations[rank]

            metrics = {}
            for rank in ranks:
                relative, cosine = _relative(exact_adjoint, approximations[rank])
                metrics[str(rank)] = {
                    "relative_fro_error": relative,
                    "cosine": cosine,
                }
            layer_records.append({"layer": layer_index, "metrics": metrics})

            if layer_index > 0:
                weight = weights[layer_index]
                exact_adjoint = weight @ exact_adjoint @ weight.T
                for rank in ranks:
                    approximations[rank] = (
                        weight @ approximations[rank] @ weight.T
                    )

        records.append(
            {
                "output": output,
                "terminal_to_first_relu": layer_records[-1]["metrics"],
                "layers_reverse": layer_records,
            }
        )

    aggregate = {}
    for rank in ranks:
        relative = np.asarray(
            [
                record["terminal_to_first_relu"][str(rank)]["relative_fro_error"]
                for record in records
            ],
            dtype=np.float64,
        )
        cosine = np.asarray(
            [
                record["terminal_to_first_relu"][str(rank)]["cosine"]
                for record in records
            ],
            dtype=np.float64,
        )
        aggregate[str(rank)] = {
            "relative_mean": float(np.mean(relative)),
            "relative_max": float(np.max(relative)),
            "cosine_mean": float(np.mean(cosine)),
            "cosine_min": float(np.min(cosine)),
        }

    return {
        "provenance": {
            "generated_only": True,
            "width": width,
            "depth": depth,
            "seed": seed,
            "outputs": list(outputs),
            "ranks": list(ranks),
            "numpy": np.__version__,
            "scope": "covariance Price block only",
        },
        "aggregate": aggregate,
        "outputs": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--depth", type=int, default=8)
    parser.add_argument("--seed", type=int, default=120101)
    parser.add_argument("--outputs", type=int, nargs="+", default=[0, 1, 2, 3])
    parser.add_argument("--ranks", type=int, nargs="+", default=[0, 4, 8, 16])
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    result = run(
        args.width,
        args.depth,
        args.seed,
        tuple(args.outputs),
        tuple(args.ranks),
    )
    if args.aggregate_only:
        result.pop("outputs")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
