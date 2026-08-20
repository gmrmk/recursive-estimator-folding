"""Generated-only M139 positive proposal for the exact M122 ``[2,1,1]`` term.

This module changes *only* the Hansen--Hurwitz sampling law used for the
already audited M133 five-product estimator.  A sampled contribution is still
evaluated by M131's conditional one-dimensional oracle (or the same exact
coefficient in a deployment implementation).  Consequently a poor surrogate
can increase variance, but cannot create approximation bias.

The proposal has two parts.

* M133's three positive tree banks supply the quadratic bridge component.
* A fixed-rank, positive Nyström envelope supplies a finite proxy for the
  partial-correlation boundary mode.  It is deliberately an envelope for a
  sampling law, not an assertion that the connected cumulant is low rank.

The only dense objects are ``O(R n^2)`` nonnegative edge tables.  There is no
``n^3`` tensor, no model loader, no scorer, and no benchmark access.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

import numpy as np


Array = np.ndarray

ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "m131_trivariate_boundary_stream",
    "m133_ht_hidden_edge",
    "m129_source_frechet_tangent",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)


@dataclass(frozen=True)
class TreeComponent:
    """One positive separable star on an ordered distinct triple.

    ``root_slot`` names which of ``(repeated, singleton_left,
    singleton_right)`` is the graph centre.  For a fixed centre ``r`` the
    unnormalised mass is ``anchor[r] * left[r,p] * right[r,q]`` with
    ``r,p,q`` distinct.  Its exact distinct-label normalizer is available in
    O(n), after an O(n^2) table setup.
    """

    root_slot: int
    anchor: Array
    left: Array
    right: Array
    root_mass: Array
    normalizer: float


@dataclass(frozen=True)
class PositivePartialProposal:
    """A finite mixture of exact-normalized positive tree components."""

    components: tuple[TreeComponent, ...]
    uniform_mixture: float
    rank_used: int
    source_scale: Array
    node_strength: Array

    @property
    def width(self) -> int:
        return int(self.source_scale.size)

    @property
    def ordered_population(self) -> int:
        n = self.width
        return n * (n - 1) * (n - 2)

    @property
    def structured_normalizer(self) -> float:
        return float(math.fsum(component.normalizer for component in self.components))

    @staticmethod
    def _draw(weights: Array, rng: np.random.Generator) -> int:
        total = float(np.sum(weights))
        if not math.isfinite(total) or total <= 0.0:
            raise ArithmeticError("attempted to sample an empty positive table")
        return int(rng.choice(weights.size, p=weights / total))

    def _component_weight(self, component: TreeComponent, i: int, j: int, k: int) -> float:
        labels = (i, j, k)
        root = labels[component.root_slot]
        endpoints = tuple(labels[position] for position in range(3) if position != component.root_slot)
        return float(component.anchor[root] * component.left[root, endpoints[0]] * component.right[root, endpoints[1]])

    def probability(self, repeated: int, left: int, right: int) -> float:
        if not (0 <= repeated < self.width and 0 <= left < self.width and 0 <= right < self.width):
            raise IndexError("ordered triple label is out of range")
        if len({repeated, left, right}) != 3:
            return 0.0
        uniform = self.uniform_mixture / self.ordered_population
        normalizer = self.structured_normalizer
        if normalizer <= 0.0:
            return 1.0 / self.ordered_population
        structured = math.fsum(
            self._component_weight(component, repeated, left, right)
            for component in self.components
        ) / normalizer
        return uniform + (1.0 - self.uniform_mixture) * structured

    def _draw_uniform(self, rng: np.random.Generator) -> tuple[int, int, int]:
        draw = rng.choice(self.width, size=3, replace=False)
        return int(draw[0]), int(draw[1]), int(draw[2])

    def _draw_component(self, component: TreeComponent, rng: np.random.Generator) -> tuple[int, int, int]:
        root = self._draw(component.root_mass, rng)
        row_left = component.left[root]
        row_right = component.right[root]
        right_total = float(np.sum(row_right))
        first_weights = row_left * (right_total - row_right)
        first = self._draw(first_weights, rng)
        second_weights = row_right.copy()
        second_weights[root] = 0.0
        second_weights[first] = 0.0
        second = self._draw(second_weights, rng)
        labels = [0, 0, 0]
        labels[component.root_slot] = root
        slots = [slot for slot in range(3) if slot != component.root_slot]
        labels[slots[0]] = first
        labels[slots[1]] = second
        return int(labels[0]), int(labels[1]), int(labels[2])

    def sample(self, rng: np.random.Generator, count: int) -> Array:
        if type(count) is not int or count < 0:
            raise ValueError("count must be a nonnegative integer")
        answer = np.empty((count, 3), dtype=np.int64)
        normalizer = self.structured_normalizer
        component_weights = np.asarray([item.normalizer for item in self.components])
        for row in range(count):
            if normalizer <= 0.0 or float(rng.random()) < self.uniform_mixture:
                answer[row] = self._draw_uniform(rng)
            else:
                component = self.components[self._draw(component_weights, rng)]
                answer[row] = self._draw_component(component, rng)
        return answer


def _validate_bridge(bridge: Array) -> Array:
    bridge = np.asarray(bridge, dtype=np.float64)
    if bridge.ndim != 2 or bridge.shape[0] != bridge.shape[1]:
        raise ValueError("bridge must be square")
    if not np.all(np.isfinite(bridge)) or not np.array_equal(bridge, bridge.T):
        raise ValueError("bridge must be finite and exactly symmetric")
    if not np.allclose(np.diag(bridge), 1.0, rtol=0.0, atol=2e-12):
        raise ValueError("bridge must have unit diagonal")
    return bridge


def _vector(name: str, value: Array, size: int, *, positive: bool = False) -> Array:
    value = np.asarray(value, dtype=np.float64)
    if value.shape != (size,) or not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be one finite vector")
    if positive and np.any(value <= 0.0):
        raise ValueError(f"{name} must be strictly positive")
    return value


def _component(root_slot: int, anchor: Array, left: Array, right: Array) -> TreeComponent:
    if root_slot not in (0, 1, 2):
        raise ValueError("root slot must be 0, 1, or 2")
    n = anchor.size
    if left.shape != (n, n) or right.shape != (n, n):
        raise ValueError("tree component table shape mismatch")
    if np.any(anchor < 0.0) or np.any(left < 0.0) or np.any(right < 0.0):
        raise ValueError("tree component must be nonnegative")
    left = np.array(left, dtype=np.float64, copy=True)
    right = np.array(right, dtype=np.float64, copy=True)
    np.fill_diagonal(left, 0.0)
    np.fill_diagonal(right, 0.0)
    left_sum = np.sum(left, axis=1)
    right_sum = np.sum(right, axis=1)
    distinct = left_sum * right_sum - np.sum(left * right, axis=1)
    # Roundoff can make an exact zero slightly negative after cancellation.
    distinct = np.maximum(distinct, 0.0)
    root_mass = anchor * distinct
    normalizer = float(np.sum(root_mass))
    if not math.isfinite(normalizer):
        raise ArithmeticError("tree normalizer is non-finite")
    return TreeComponent(root_slot, anchor, left, right, root_mass, normalizer)


def partial_correlation(bridge: Array, repeated: int, left: int, right: int) -> float:
    """Return the stable conditional correlation ``rho(left,right | repeated)``.

    This is only a diagnostic/calibration coordinate.  The sampler uses the
    finite positive separation built below; it never relies on an unbounded
    conditional-density value.
    """

    bridge = _validate_bridge(bridge)
    if len({repeated, left, right}) != 3:
        raise ValueError("partial correlation needs three distinct labels")
    a = float(bridge[repeated, left])
    b = float(bridge[repeated, right])
    c = float(bridge[left, right])
    denom = math.sqrt(max((1.0 - a * a) * (1.0 - b * b), 0.0))
    if denom <= 1e-14:
        return math.copysign(1.0, c - a * b) if c != a * b else 0.0
    return float(np.clip((c - a * b) / denom, -1.0, 1.0))


def quadratic_211_term(bridge: Array, repeated: int, left: int, right: int) -> float:
    """The analytically-owned zero-mean quadratic bridge jet.

    Exact M122 evaluation subtracts the tree/pair pieces first.  This term is
    then removed for the surrogate diagnostic, not from the estimator.
    """

    bridge = _validate_bridge(bridge)
    return float(
        (
            bridge[repeated, left] * bridge[repeated, right]
            + bridge[repeated, left] * bridge[left, right]
            + bridge[repeated, right] * bridge[left, right]
        )
        / (4.0 * math.pi)
    )


def _strict_top_pivots(degree: Array, rank: int, *, tie_tolerance: float) -> Array:
    """Permutation-covariant pivot set, with a fail-closed tie boundary.

    Sorting by an array index would silently break permutation covariance.
    When the rank boundary is tied, we deliberately return no latent factors;
    the remaining M133 tree proposal is still fully covariant.
    """

    n = degree.size
    if rank <= 0 or rank >= n:
        return np.empty(0, dtype=np.int64)
    order = np.argsort(-degree, kind="stable")
    boundary_hi = float(degree[order[rank - 1]])
    boundary_lo = float(degree[order[rank]])
    if abs(boundary_hi - boundary_lo) <= tie_tolerance * max(1.0, abs(boundary_hi)):
        return np.empty(0, dtype=np.int64)
    return np.sort(order[:rank]).astype(np.int64)


def make_positive_partial_proposal(
    bridge: Array,
    weight: Array,
    alpha: Array,
    source_scale: Array,
    *,
    rank: int = 4,
    uniform_mixture: float = 0.05,
    partial_ridge: float = 2.0**-12,
    partial_cap: float = 8.0,
    latent_strength: float = 0.70,
    tie_tolerance: float = 2e-13,
) -> PositivePartialProposal:
    """Construct the frozen M139 positive-envelope mixture.

    Let ``S=abs(B-I)`` and ``u_r(j)=S[j,p_r]/sqrt(sum S[:,p_r])`` for the
    `rank` largest strict-degree pivots.  The products ``u_r(j)u_r(k)`` are a
    nonnegative Nyström separation of the residual correlation path.  The
    conditional-coordinate multiplier

    ``[ridge + 1 - min(u_r(i)^2, 1)]^(-1/2)``

    is a bounded surrogate for the partial-correlation boundary left after
    conditioning on the repeated label.  It is *not* used as a cumulant
    approximation.  Each such rank-one endpoint mode multiplies one of the
    three M133 tree banks, so its normalization and sampler remain O(n^2).

    ``source_scale[i] * ||weight_i||`` is used instead of an unscaled row
    norm.  It is invariant under the positive ReLU gauge
    ``source_scale -> d source_scale, weight_i -> weight_i/d_i``.
    """

    bridge = _validate_bridge(bridge)
    n = bridge.shape[0]
    weight = np.asarray(weight, dtype=np.float64)
    if weight.ndim != 2 or weight.shape[0] != n or not np.all(np.isfinite(weight)):
        raise ValueError("weight must be a finite matrix with matching rows")
    alpha = _vector("alpha", alpha, n)
    source_scale = _vector("source_scale", source_scale, n, positive=True)
    if type(rank) is not int or rank < 0:
        raise ValueError("rank must be a nonnegative integer")
    if not (0.0 < uniform_mixture <= 1.0):
        raise ValueError("uniform mixture must lie in (0,1]")
    if not (partial_ridge > 0.0 and partial_cap >= 1.0 and latent_strength >= 0.0):
        raise ValueError("invalid finite partial-envelope parameters")

    residual = np.abs(bridge.copy())
    np.fill_diagonal(residual, 0.0)
    # This static rational gate is a positive Chebyshev-compatible envelope in
    # alpha^2/(1+alpha^2): no fitted coefficient or outcome is consulted.
    alpha_gate = 1.0 + 0.35 * (alpha * alpha / (1.0 + alpha * alpha))
    strength = source_scale * np.linalg.norm(weight, axis=1) * alpha_gate
    if np.any(strength <= 0.0):
        # A zero row contributes no output feature.  Give it a harmless tiny
        # positive score so the uniform rescue, not a division by zero, owns
        # the mathematical support.
        strength = np.maximum(strength, np.finfo(np.float64).tiny)

    components: list[TreeComponent] = []

    def append_three_banks(endpoint_left: Array, endpoint_right: Array, root_factor: Array) -> None:
        # root = repeated i
        components.append(_component(0, strength * strength * root_factor, endpoint_left * strength[None, :], endpoint_right * strength[None, :]))
        # root = singleton j; its first endpoint is the repeated i.
        components.append(_component(1, strength * root_factor, endpoint_left * (strength * strength)[None, :], endpoint_right * strength[None, :]))
        # root = singleton k; the endpoint roles are intentionally exchanged.
        components.append(_component(2, strength * root_factor, endpoint_left * (strength * strength)[None, :], endpoint_right * strength[None, :]))

    # Exact M133 quadratic tree geometry, with only source-scale/gate weights
    # added.  At alpha=0 and source_scale=1 this is exactly M133's structure.
    append_three_banks(residual, residual, np.ones(n))

    degree = np.sum(residual, axis=1)
    pivots = _strict_top_pivots(degree, min(rank, max(0, n - 1)), tie_tolerance=tie_tolerance)
    # Pair endpoint factors remain finite even as a pair correlation approaches
    # one.  The cap is a proposal safety device; uniform rescue protects bias.
    pair_endpoint = np.minimum(
        partial_cap,
        np.power(np.maximum(1.0 - bridge * bridge + partial_ridge, partial_ridge), -0.25),
    )
    np.fill_diagonal(pair_endpoint, 0.0)

    for pivot in pivots:
        feature = residual[:, pivot] / math.sqrt(max(float(degree[pivot]), partial_ridge))
        feature = np.maximum(feature, 0.0)
        # ``feature[i]`` is the low-rank latent coordinate explained by label
        # i.  Conditioning creates a finite residual mode instead of an
        # unbounded partial-correlation density.
        conditional = np.minimum(
            partial_cap,
            1.0 / np.sqrt(partial_ridge + np.maximum(0.0, 1.0 - feature * feature)),
        )
        endpoint = residual * pair_endpoint * feature[None, :]
        append_three_banks(endpoint, endpoint, latent_strength * conditional)

    return PositivePartialProposal(
        tuple(component for component in components if component.normalizer > 0.0),
        float(uniform_mixture),
        int(pivots.size),
        source_scale.copy(),
        strength.copy(),
    )


def singularity_subtracted_defect(
    tangent, repeated: int, left: int, right: int, *, coarse_order: int = 32, fine_order: int = 48) -> tuple[float, float, float]:
    """Return exact M131 defect, owned quadratic jet, and residual diagnostic."""

    from m131_trivariate_boundary_stream import conditional_collision211_defect_dot

    exact, _, _ = conditional_collision211_defect_dot(
        tangent,
        repeated,
        left,
        right,
        coarse_order=coarse_order,
        fine_order=fine_order,
    )
    quadratic = quadratic_211_term(tangent.state.bridge, repeated, left, right)
    return float(exact), float(quadratic), float(exact - quadratic)


def m139_incremental_cost_envelope(
    *, width: int = 256, layers: int = 31, samples_per_layer: int = 512, rank: int = 4, safety_factor: float = 1.25
) -> dict[str, float | int | bool]:
    """Conservative static, non-overlapping overhead bound in billed units.

    The existing five rectangular products and exact sampled coefficient
    quadrature are inherited from M133 and intentionally excluded.  This
    bound covers the new O(R n^2) positive tables, exact-mixture probability
    evaluation, and fixed-count sampling.  It is not a native runner trace.
    """

    if min(width, layers, samples_per_layer) <= 0 or rank < 0 or safety_factor < 1.0:
        raise ValueError("invalid M139 cost dimensions")
    component_count = 3 * (1 + rank)
    # Table setup performs conservative 20 scalar/fill-equivalent operations
    # per component entry.  A draw has three O(n) categorical scans plus all
    # component masses for its exact HH probability.
    table_scalar = 20 * layers * component_count * width * width
    draw_scalar = layers * samples_per_layer * (3 * width + 4 * component_count)
    pivot_scalar = 12 * layers * width * width
    allocation_and_symmetry = layers * component_count * width * width
    raw = table_scalar + draw_scalar + pivot_scalar + allocation_and_symmetry
    protected = int(math.ceil(raw * safety_factor))
    return {
        "width": width,
        "layers": layers,
        "samples_per_layer": samples_per_layer,
        "rank": rank,
        "component_count": component_count,
        "raw_incremental": int(raw),
        "protected_incremental": protected,
        "protected_billions": protected / 1.0e9,
        "under_five_billion": protected <= 5_000_000_000,
        "inherits_same_five_m133_products": True,
        "inherits_exact_sampled_coefficient": True,
        "native_trace_completed": False,
    }
