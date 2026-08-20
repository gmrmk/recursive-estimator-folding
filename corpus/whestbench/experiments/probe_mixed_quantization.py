"""Research-only accuracy probe for separable activation/weight quantization.

The probe dequantizes before BLAS so it does *not* claim a compute saving.  It
answers the prerequisite question for a later counted bit-serial kernel: can
the depth-32 trajectory tolerate per-row activation and per-column weight
codes at the proposed bit widths?
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from whestbench import SetupContext
from whestbench.dataset import load_dataset
from whestbench.domain import MLP


FLOP_BUDGET = 272_000_000_000


def quantize_rows_unsigned(x: np.ndarray, bits: int) -> np.ndarray:
    qmax = float((1 << bits) - 1)
    scale = np.maximum(np.max(x, axis=1, keepdims=True) / qmax, 1e-12)
    codes = np.clip(np.rint(x / scale), 0.0, qmax)
    return (codes * scale).astype(np.float32)


def quantize_columns_signed(weight: np.ndarray, bits: int) -> np.ndarray:
    qmax = float((1 << (bits - 1)) - 1)
    scale = np.maximum(np.max(np.abs(weight), axis=0, keepdims=True) / qmax, 1e-12)
    codes = np.clip(np.rint(weight / scale), -qmax, qmax)
    return (codes * scale).astype(np.float32)


def propagate(
    gaussian: np.ndarray,
    weights: list[np.ndarray],
    *,
    activation_bits: int | None,
    weight_bits: int | None,
    quantize_start: int,
    quantize_stop: int,
) -> np.ndarray:
    first = gaussian @ weights[0]
    x = np.concatenate((np.maximum(first, 0.0), np.maximum(-first, 0.0)), axis=0)
    for layer in range(1, len(weights)):
        use_quantized = quantize_start <= layer < quantize_stop
        if use_quantized:
            qx = quantize_rows_unsigned(x, int(activation_bits))
            qw = quantize_columns_signed(weights[layer], int(weight_bits))
            x = np.maximum(qx @ qw, 0.0)
        else:
            x = np.maximum(x @ weights[layer], 0.0)
    return np.mean(x, axis=0, dtype=np.float64)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--split", default="full")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--n-base", type=int, default=512)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    from base_estimator import Estimator

    estimator = Estimator()
    estimator.n_base = args.n_base
    estimator.setup(
        SetupContext(
            width=256,
            depth=32,
            flop_budget=FLOP_BUDGET,
            api_version="0.14.0",
            submission_dir=str(root),
            seed=args.seed,
        )
    )
    gaussian = np.asarray(estimator._gaussian, dtype=np.float32)
    estimator.teardown()

    row = load_dataset(args.dataset, split=args.split)[args.index]
    mlp = MLP.from_row(row, seed_protocol_version="3.0")
    weights = [np.asarray(weight, dtype=np.float32) for weight in mlp.weights]
    target = np.asarray(row["all_layer_means"][-1], dtype=np.float64)
    reference = propagate(
        gaussian,
        weights,
        activation_bits=None,
        weight_bits=None,
        quantize_start=32,
        quantize_stop=32,
    )

    configurations = []
    for bits in (8, 6, 5, 4, 3, 2):
        configurations.append((f"a{bits}w{bits}_layers2_30", bits, bits, 1, 30))
    configurations.extend(
        (
            ("a4w4_layers17_30", 4, 4, 16, 30),
            ("a3w3_layers17_30", 3, 3, 16, 30),
            ("a4w4_layers2_16", 4, 4, 1, 16),
            ("a3w3_layers2_16", 3, 3, 1, 16),
        )
    )

    result = {
        "dataset_index": args.index,
        "n_base": args.n_base,
        "reference_target_mse": float(np.mean((reference - target) ** 2)),
        "configurations": {},
    }
    for name, abits, wbits, start, stop in configurations:
        prediction = propagate(
            gaussian,
            weights,
            activation_bits=abits,
            weight_bits=wbits,
            quantize_start=start,
            quantize_stop=stop,
        )
        result["configurations"][name] = {
            "mse_vs_reference": float(np.mean((prediction - reference) ** 2)),
            "mse_vs_target": float(np.mean((prediction - target) ** 2)),
            "mean_signed_delta": float(np.mean(prediction - reference)),
            "max_abs_delta": float(np.max(np.abs(prediction - reference))),
        }
        print(name, result["configurations"][name], flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
