"""Capture a matched sample-count sweep on a sealed WHestBench slice.

This research harness deliberately records only the scored final row.  It is
not part of any submission package and does not attempt to measure FLOPs;
official ``whest run`` invocations are used for that gate.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
from whestbench import SetupContext
from whestbench.dataset import load_dataset
from whestbench.domain import MLP


FLOP_BUDGET = 272_000_000_000


def _load_estimator(path: Path, ordinal: int):
    module_name = f"scorefloor_sweep_{path.stem}_{ordinal}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load estimator module from {path}")
    module = importlib.util.module_from_spec(spec)
    # Variant modules use a sibling fallback import for official-run parity.
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module.Estimator()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--split", default="full")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--n-mlps", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seed-protocol", default="3.0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("estimators", nargs="+", type=Path)
    args = parser.parse_args()

    dataset = load_dataset(args.dataset, split=args.split)
    stop_index = min(args.start_index + args.n_mlps, len(dataset))
    if not 0 <= args.start_index < stop_index:
        raise ValueError("requested slice is outside the dataset")

    estimators = []
    for ordinal, path in enumerate(args.estimators):
        resolved = path.resolve()
        estimator = _load_estimator(resolved, ordinal)
        estimator.setup(
            SetupContext(
                width=256,
                depth=32,
                flop_budget=FLOP_BUDGET,
                api_version="0.14.0",
                submission_dir=str(resolved.parent),
                seed=args.seed,
            )
        )
        estimators.append((resolved, estimator, [], []))

    targets = []
    names = []
    for local_index, index in enumerate(range(args.start_index, stop_index)):
        row = dataset[index]
        target = np.asarray(row["all_layer_means"][-1], dtype=np.float64)
        targets.append(target)
        names.append(str(row.get("mlp_name", "")))
        mlp = MLP.from_row(row, seed_protocol_version=args.seed_protocol)
        for resolved, estimator, predictions, seconds in estimators:
            started = time.perf_counter()
            prediction = estimator.predict(mlp, FLOP_BUDGET)
            seconds.append(time.perf_counter() - started)
            final_row = np.asarray(prediction[-1], dtype=np.float64)
            predictions.append(final_row)
            mse = float(np.mean((final_row - target) ** 2))
            print(
                f"{resolved.stem}: {local_index + 1}/{stop_index - args.start_index} "
                f"index={index} mse={mse:.9e} seconds={seconds[-1]:.3f}",
                flush=True,
            )

    target_array = np.stack(targets)
    payload: dict[str, np.ndarray] = {
        "targets": target_array,
        "names": np.asarray(names),
        "indices": np.arange(args.start_index, stop_index, dtype=np.int32),
    }
    summary = {
        "dataset": str(args.dataset),
        "split": args.split,
        "start_index": args.start_index,
        "stop_index": stop_index,
        "seed": args.seed,
        "estimators": {},
    }
    for resolved, estimator, predictions, seconds in estimators:
        estimator.teardown()
        prediction_array = np.stack(predictions)
        per_network = np.mean((prediction_array - target_array) ** 2, axis=1)
        payload[f"pred_{resolved.stem}"] = prediction_array
        payload[f"mse_{resolved.stem}"] = per_network
        summary["estimators"][resolved.stem] = {
            "mean_raw_mse": float(np.mean(per_network)),
            "median_raw_mse": float(np.median(per_network)),
            "max_raw_mse": float(np.max(per_network)),
            "mean_wall_seconds": float(np.mean(seconds)),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **payload)
    json_path = args.output.with_suffix(".json")
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["estimators"], indent=2), flush=True)
    print(args.output.resolve(), flush=True)


if __name__ == "__main__":
    main()
