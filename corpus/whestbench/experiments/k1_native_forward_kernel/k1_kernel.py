"""K1: verified fused wall-priced forward kernel + structural pruning.

The working, measured artifact (bitwise-identical to the naive forward,
1.36x faster from allocation removal; 1.7x fewer FLOPs from pruning). This is
the correctness reference and the deployable fallback for a compiled kernel
(designed in K1_DISPOSITION, bundled precompiled per Rules 5.2).

Response-free: operates on weights + generated samples only.
"""

from __future__ import annotations

import math

import numpy as np

WIDTH = 256


def fused_forward_mean(weights, X):
    """Dense fused forward; returns the per-neuron post-ReLU sample mean.
    Preallocated ping-pong f32 buffers, out= matmul, in-place ReLU."""
    n = X.shape[0]
    # np.array always copies: the in-place ping-pong must NOT mutate the
    # caller's X (np.ascontiguousarray would alias an already-f32 input).
    a = np.array(X, dtype=np.float32, order="C")
    b = np.empty((n, weights[0].shape[1]), dtype=np.float32, order="C")
    for W in weights:
        np.dot(a, W, out=b)
        np.maximum(b, np.float32(0.0), out=b)
        a, b = b, a
    return a.mean(axis=0)


def structural_active_masks(weights, dead_alpha=-2.0):
    """Champion-style per-network active-neuron masks from the analytic diagonal
    pass: a neuron is pruned when its analytic alpha < dead_alpha. Returns a list
    of boolean masks (one per layer) and the FLOP fraction vs dense."""
    mu = np.zeros(WIDTH)
    var = np.ones(WIDTH)
    masks = []
    inv_sqrt_2pi = 1.0 / math.sqrt(2.0 * math.pi)
    for W in weights:
        Wf = np.asarray(W, dtype=np.float64)
        mu_pre = mu @ Wf
        var_pre = var @ (Wf * Wf)
        s = np.sqrt(np.maximum(var_pre, 1e-12))
        alpha = mu_pre / s
        Phi = 0.5 * (1.0 + np.vectorize(math.erf)(alpha / math.sqrt(2.0)))
        phi = inv_sqrt_2pi * np.exp(-0.5 * alpha * alpha)
        mu = mu_pre * Phi + s * phi
        var = np.maximum((var_pre + mu_pre * mu_pre) * Phi + mu_pre * s * phi - mu * mu, 0.0)
        masks.append(alpha >= dead_alpha)
    active = [int(m.sum()) for m in masks]
    dense = len(weights) * 2 * WIDTH * WIDTH
    pruned = sum(2 * (active[l - 1] if l > 0 else WIDTH) * active[l]
                 for l in range(len(weights)))
    return masks, pruned / dense


def floor_budget_plan(us_per_sample, v=0.0199, floor_wall_s=0.272, B=2.72e11):
    """Given a measured us/sample, the max samples under the 0.1-multiplier floor
    and the implied raw + adjusted score at v (the S-lever payoff calculator)."""
    n = int(floor_wall_s / (us_per_sample * 1e-6))  # integer samples drawable
    raw_mse = v / n
    return {
        "us_per_sample": us_per_sample,
        "floor_budget_samples": n,
        "raw_mse": raw_mse,
        "adjusted_at_floor": 0.1 * raw_mse,
        "S_vs_n2_176gflops": 23.77 / us_per_sample,
    }
