"""Target-shaped native FlopScope trace for M143 proposal structure only.

Fresh synthetic float32 arrays are created before the budget context.  The
measured region replaces M133's proposal setup: sign-scrambled row energy,
physical-scale strength, three factored banks, fixed-count categorical scan
work, and exact sampled-q gathers.  It deliberately excludes M133's unchanged
five products, exact coefficient builder, carrier, hard-edge sampler, and its
already reserved 100 ms whole-estimator wall allowance.

This is a structural trace, not a response/outcome experiment and not a
submission estimator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite an existing trace")

    n = 256
    layers = 31
    samples = 512
    dtype = np.float32
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(143_014_300)))
    weights_np = [rng.normal(scale=0.06, size=(n, n)).astype(dtype) for _ in range(layers)]
    probabilities_np = [rng.uniform(.15, .85, size=n).astype(dtype) for _ in range(layers)]
    scales_np = [rng.uniform(.2, 1.4, size=n).astype(dtype) for _ in range(layers)]
    bridges_np = []
    for _ in range(layers):
        raw = rng.normal(scale=.08, size=(n, n)).astype(dtype)
        bridge = .5 * (raw + raw.T)
        np.fill_diagonal(bridge, 1.0)
        bridges_np.append(bridge)
    centre_index_np = [rng.integers(0, n, size=samples, dtype=np.int64) for _ in range(layers)]
    left_index_np = [rng.integers(0, n, size=samples, dtype=np.int64) for _ in range(layers)]
    right_index_np = [rng.integers(0, n, size=samples, dtype=np.int64) for _ in range(layers)]
    exclusion_mask_np = []
    for layer in range(layers):
        mask = np.zeros((samples, n), dtype=dtype)
        mask[np.arange(samples), left_index_np[layer]] = 1.0
        exclusion_mask_np.append(mask)

    weights = [fnp.asarray(value, dtype=fnp.float32) for value in weights_np]
    probabilities = [fnp.asarray(value, dtype=fnp.float32) for value in probabilities_np]
    scales = [fnp.asarray(value, dtype=fnp.float32) for value in scales_np]
    bridges = [fnp.asarray(value, dtype=fnp.float32) for value in bridges_np]
    centre_index = [fnp.asarray(value) for value in centre_index_np]
    left_index = [fnp.asarray(value) for value in left_index_np]
    right_index = [fnp.asarray(value) for value in right_index_np]
    exclusion_mask = [fnp.asarray(value, dtype=fnp.float32) for value in exclusion_mask_np]
    identity = fnp.eye(n, dtype=fnp.float32)

    ctx = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
    started = time.perf_counter()
    with ctx:
        energy = fnp.ones(n, dtype=fnp.float32)
        row_energy = [None] * layers
        for layer in range(layers - 1, -1, -1):
            gated = probabilities[layer] * probabilities[layer] * energy
            energy = (weights[layer] * weights[layer]) @ gated
            row_energy[layer] = energy

        live = fnp.asarray(0.0, dtype=fnp.float32)
        for layer in range(layers):
            strength = scales[layer] * fnp.sqrt(row_energy[layer])
            strength2 = strength * strength
            residual = fnp.abs(bridges[layer] - identity)

            # Centre-i bank.
            endpoint = residual * strength[None, :]
            endpoint_sum = fnp.sum(endpoint, axis=1)
            centre_a = strength2 * (
                endpoint_sum * endpoint_sum - fnp.sum(endpoint * endpoint, axis=1)
            )

            # Singleton-centre banks B/C in one vectorized table construction.
            left = residual * strength2[:, None]
            right = residual * strength[:, None]
            left_sum = fnp.sum(left, axis=0)
            right_sum = fnp.sum(right, axis=0)
            centre_b = strength * (
                left_sum * right_sum - fnp.sum(left * right, axis=0)
            )
            centre_c = centre_b + fnp.zeros(n, dtype=fnp.float32)

            # One centre CDF and two K-by-n endpoint categorical scans.  The
            # fixed synthetic indices stand in for independent uniforms; the
            # measured scan/gather shapes are exactly target-sized.
            centre_cdf = fnp.cumsum(centre_a + centre_b + centre_c)
            chosen_endpoint = endpoint[centre_index[layer]]
            first_cdf = fnp.cumsum(chosen_endpoint, axis=1)
            exclusion = fnp.ones((samples, n), dtype=fnp.float32) - exclusion_mask[layer]
            second_cdf = fnp.cumsum(chosen_endpoint * exclusion, axis=1)

            # Exact q ingredients for K sampled ordered triples.  The full HH
            # coefficient and five-product work are inherited and excluded.
            i = centre_index[layer]
            j = left_index[layer]
            k = right_index[layer]
            sampled_mass = strength2[i] * strength[j] * strength[k] * (
                residual[i, j] * residual[i, k]
                + residual[i, j] * residual[j, k]
                + residual[i, k] * residual[j, k]
            )
            normalizer = fnp.sum(centre_a) + fnp.sum(centre_b) + fnp.sum(centre_c)
            sampled_q = .05 / float(n * (n - 1) * (n - 2)) + .95 * sampled_mass / normalizer
            live = live + centre_cdf[-1] + fnp.sum(first_cdf[:, -1]) + fnp.sum(second_cdf[:, -1]) + fnp.sum(sampled_q)
        _ = live + fnp.asarray(0.0, dtype=fnp.float32)
    elapsed = time.perf_counter() - started

    result = {
        "firewall": "fresh target-shaped synthetic proposal structure only; no network outcome/data/scorer/submission",
        "shape": {"width": n, "layers": layers, "samples_per_layer": samples},
        "dtype": "float32",
        "scope": [
            "p^2-gated sign-scrambled path-energy recursion",
            "physical source-scale strength",
            "three factored proposal banks and normalizers",
            "fixed-count centre/two-endpoint categorical scan shapes",
            "exact sampled-q gathers",
        ],
        "excluded_as_inherited": [
            "M133 five rectangular products",
            "M131 exact sampled coefficient builder",
            "M125b carrier/background",
            "M133 hard path and [2,2] edge sampler",
            "M133 100ms whole-estimator wall reserve",
        ],
        "flopscope": getattr(flops, "__version__", "unknown"),
        "numpy": np.__version__,
        "billed_flops": int(ctx.flops_used),
        "backend_s": float(ctx.flopscope_backend_time_s),
        "overhead_s": float(ctx.flopscope_overhead_time_s),
        "residual_s": float(ctx.residual_wall_time_s or 0.0),
        "effective_compute": int(ctx.flops_used) + 1.0e11 * float(ctx.residual_wall_time_s or 0.0),
        "outer_wall_s": elapsed,
        "native_trace": True,
        "response_outcome_run": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
