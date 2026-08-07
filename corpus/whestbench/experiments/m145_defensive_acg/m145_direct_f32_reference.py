"""Direct target-semantics reference primitive for the M145 cross-risk descendant.

This is deliberately independent of the estimator's folding, pruning, and
transport paths.  It is not an efficacy runner and does not create reference
vectors by itself; callers must supply a frozen antipodal float32 design.
"""

from __future__ import annotations

import flopscope.numpy as fnp


def direct_relu_mean_f32(weights, antipodal_radius_scaled_points):
    """Return the direct float32 forward mean used by the reference protocol.

    Every matrix multiply and ReLU is explicitly float32 FlopScope arithmetic.
    Accumulation is a deterministic float32 reduction, matching the evaluator
    target semantics rather than silently changing the estimand to float64.
    """

    x = fnp.asarray(antipodal_radius_scaled_points, dtype=fnp.float32)
    if x.ndim != 2:
        raise ValueError("points must have shape [paths,width]")
    for weight in weights:
        w = fnp.asarray(weight, dtype=fnp.float32)
        if w.ndim != 2 or int(w.shape[0]) != int(x.shape[1]):
            raise ValueError("incompatible float32 weight matrix")
        x = fnp.matmul(x, w).astype(fnp.float32)
        x = fnp.maximum(x, fnp.float32(0.0)).astype(fnp.float32)
    return fnp.mean(x, axis=0, dtype=fnp.float32).astype(fnp.float32)


def direct_relu_mean_f32_chunked(weights, antipodal_radius_scaled_points, chunk_rows):
    """Exact-order-safe streaming variant with an explicit no-outcome contract.

    It returns a sum and count rather than a mean so the protocol can freeze a
    reduction tree.  The equivalence test must compare this to the unchunked
    primitive using identical chunks before any reference campaign is allowed.
    """

    points = fnp.asarray(antipodal_radius_scaled_points, dtype=fnp.float32)
    if int(chunk_rows) <= 0:
        raise ValueError("chunk_rows must be positive")
    total = fnp.zeros((int(points.shape[1]),), dtype=fnp.float32)
    count = 0
    for start in range(0, int(points.shape[0]), int(chunk_rows)):
        stop = min(start + int(chunk_rows), int(points.shape[0]))
        x = points[start:stop]
        for weight in weights:
            x = fnp.matmul(x, fnp.asarray(weight, dtype=fnp.float32)).astype(
                fnp.float32
            )
            x = fnp.maximum(x, fnp.float32(0.0)).astype(fnp.float32)
        total = fnp.add(total, fnp.sum(x, axis=0, dtype=fnp.float32)).astype(
            fnp.float32
        )
        count += int(stop - start)
    return total, count
