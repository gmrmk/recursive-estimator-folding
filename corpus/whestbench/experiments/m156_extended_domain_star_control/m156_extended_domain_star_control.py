"""Response-free algebra for M156's extended-domain covariance-star control.

The target [2,1,1] coefficient is zero outside pairwise-distinct labels.  M156
deliberately defines a cheap control on *all* ordered triples and samples the
negative control on collision strata.  Therefore collisions cancel in
expectation and never overlap the separately owned physical collision source.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray
ORDERED_OWNER = 0.5


@dataclass(frozen=True)
class Source211:
    aaaa: Array
    aaab: Array
    aabb: Array


def _weight(weight: Array) -> Array:
    value = np.asarray(weight, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] < 3 or not np.all(np.isfinite(value)):
        raise ValueError("weight must be a finite labelled matrix")
    return value


def _covariance(covariance: Array, labels: int) -> Array:
    value = np.asarray(covariance, dtype=np.float64)
    if value.shape != (labels, labels) or not np.all(np.isfinite(value)):
        raise ValueError("covariance has incompatible shape or values")
    if not np.allclose(value, value.T, rtol=0.0, atol=2e-13):
        raise ValueError("covariance must be symmetric")
    return value


def extended_feature(weight: Array, i: int, j: int, k: int) -> Source211:
    """The same half-owned polynomial feature, extended to repeated labels."""

    w = _weight(weight)
    if not all(0 <= index < w.shape[0] for index in (i, j, k)):
        raise ValueError("label outside source width")
    x, y, z = w[i], w[j], w[k]
    aaab = 3.0 * (
        np.outer(x * y * z, x) + np.outer(x * x * z, y)
    )
    first = np.outer(x * x, y * z)
    split = 2.0 * np.outer(x * y, x * z)
    aabb = first + first.T + split + split.T
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def source_add(left: Source211, right: Source211) -> Source211:
    return Source211(
        left.aaaa + right.aaaa,
        left.aaab + right.aaab,
        left.aabb + right.aabb,
    )


def source_scale(scale: float, source: Source211) -> Source211:
    if not math.isfinite(scale):
        raise ValueError("source scale must be finite")
    return Source211(
        scale * source.aaaa, scale * source.aaab, scale * source.aabb
    )


def zero_source(output_width: int) -> Source211:
    return Source211(
        np.zeros(output_width, dtype=np.float64),
        np.zeros((output_width, output_width), dtype=np.float64),
        np.zeros((output_width, output_width), dtype=np.float64),
    )


def dense_extended_source(weight: Array, coefficient: Array) -> Source211:
    """Small-width reference: half-owned sum over every ordered triple."""

    w = _weight(weight)
    coefficient = np.asarray(coefficient, dtype=np.float64)
    n = w.shape[0]
    if coefficient.shape != (n, n, n) or not np.all(np.isfinite(coefficient)):
        raise ValueError("coefficient must be a finite cubic table")
    if not np.allclose(coefficient, coefficient.swapaxes(1, 2), rtol=0.0, atol=2e-13):
        raise ValueError("coefficient must be singleton-symmetric")
    answer = zero_source(w.shape[1])
    for i in range(n):
        for j in range(n):
            for k in range(n):
                answer = source_add(
                    answer,
                    source_scale(
                        float(coefficient[i, j, k]),
                        extended_feature(w, i, j, k),
                    ),
                )
    return answer


def extended_star_table(covariance: Array) -> Array:
    covariance = np.asarray(covariance, dtype=np.float64)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    covariance = _covariance(covariance, covariance.shape[0])
    # c_ijk=-2 V_ij V_ik on the complete ordered domain.
    return -2.0 * covariance[:, :, None] * covariance[:, None, :]


def compiled_extended_star_control(weight: Array, covariance: Array) -> Source211:
    """Exact five-GEMM compiler for the all-triple covariance-star control."""

    w = _weight(weight)
    v = _covariance(covariance, w.shape[0])
    z = v @ w
    w2 = w * w
    z2 = z * z
    wz = w * z

    p = (w * z2).T @ w
    q = (w2 * z).T @ z
    r = w2.T @ z2
    s = wz.T @ wz

    aaab = -6.0 * (p + q)
    aabb = -2.0 * (r + r.T + 4.0 * s)
    return Source211(np.diag(aaab).copy(), aaab, aabb)


def distinct_target_extension(coefficient: Array) -> Array:
    """Set every collision label to zero without changing distinct entries."""

    value = np.asarray(coefficient, dtype=np.float64).copy()
    if value.ndim != 3 or value.shape[0] != value.shape[1] or value.shape[1] != value.shape[2]:
        raise ValueError("target coefficient must be cubic")
    n = value.shape[0]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) != 3:
                    value[i, j, k] = 0.0
    return value


def residual_table(target_distinct: Array, control_all: Array) -> Array:
    target = distinct_target_extension(target_distinct)
    control = np.asarray(control_all, dtype=np.float64)
    if control.shape != target.shape:
        raise ValueError("target/control table shape mismatch")
    return target - control


def collision_count(width: int) -> int:
    n = int(width)
    if n < 3:
        raise ValueError("width must be at least three")
    return n * (3 * n - 2)


def distinct_count(width: int) -> int:
    n = int(width)
    if n < 3:
        raise ValueError("width must be at least three")
    return n * (n - 1) * (n - 2)


def collision_strata(width: int) -> list[tuple[int, int, int]]:
    """Reference enumeration of the four disjoint collision patterns."""

    n = int(width)
    triples: list[tuple[int, int, int]] = []
    triples.extend((i, i, i) for i in range(n))
    triples.extend((i, i, k) for i in range(n) for k in range(n) if k != i)
    triples.extend((i, j, i) for i in range(n) for j in range(n) if j != i)
    triples.extend((i, j, j) for j in range(n) for i in range(n) if i != j)
    return triples


def mixture_probability(
    unit: tuple[int, int, int],
    width: int,
    distinct_probability,
) -> float:
    """Full-support two-stratum proposal used by the conservation proof.

    ``distinct_probability`` is the frozen M133 q0 callable on distinct
    labels.  The collision stratum receives its natural uniform-domain mass
    eta=n(3n-2)/n^3; no rejection sampler is required.
    """

    n = int(width)
    eta = collision_count(n) / float(n**3)
    if len(set(unit)) == 3:
        q0 = float(distinct_probability(unit))
        if not math.isfinite(q0) or q0 <= 0.0:
            raise ValueError("distinct proposal must have full support")
        return (1.0 - eta) * q0
    return eta / float(collision_count(n))


def source_max_abs_difference(left: Source211, right: Source211) -> float:
    return float(
        max(
            np.max(np.abs(left.aaaa - right.aaaa)),
            np.max(np.abs(left.aaab - right.aaab)),
            np.max(np.abs(left.aabb - right.aabb)),
        )
    )


def static_cost_ledger(width: int = 256, layers: int = 31) -> dict[str, float | int | str | bool]:
    n = int(width)
    layer_count = int(layers)
    f64_square = 2 * (2 * n**3 - n**2)
    protection = 1.25
    protected_one = int(math.ceil(protection * layer_count * f64_square))
    protected_five = 5 * protected_one
    inherited_endpoint = 85_980_878_800
    total = inherited_endpoint + protected_five
    return {
        "width": n,
        "layers": layer_count,
        "dense_f64_products_per_layer": 5,
        "protected_one_product_all_layers": protected_one,
        "protected_five_products_all_layers": protected_five,
        "inherited_k128_endpoint_subtotal": inherited_endpoint,
        "known_total_before_pointwise_wall": total,
        "known_total_before_pointwise_wall_billions": total / 1e9,
        "remaining_to_100b": 100_000_000_000 - total,
        "remaining_to_100b_billions": (100_000_000_000 - total) / 1e9,
        "arithmetic_floor_below_100b": total < 100_000_000_000,
        "native_trace_required": True,
        "status": "CONDITIONAL_STATIC_SURVIVOR_BEFORE_POINTWISE_AND_WALL",
    }

