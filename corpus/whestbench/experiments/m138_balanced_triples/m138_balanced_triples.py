"""Balanced fixed-count draws for the M133 factored ``[2,1,1]`` proposal.

This is deliberately a *sampling-design-only* mutation.  It retains M133's
three-bank O(n^2) factored proposal, its fixed 5% uniform rescue, its ordered
three-label support, and the five-product Hansen--Hurwitz contraction.  The
only change is to couple the K draws:

* systematic sampling balances the mixture-bank and centre incidences; and
* conditional neighbour uniforms form two independent randomized Latin
  hypercubes within each bank.

The output is still a sequence of ordered distinct triples.  Each labelled
position has exactly M133's probability ``q(i,j,k)`` marginally, so the
existing Hansen--Hurwitz scale and frozen-q Frechet tangent remain valid.

No full O(n^3) triple table is created.  The module contains no challenge
loader, outcome, scorer, submission, or leaderboard access.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

import numpy as np


_ROOT = Path(__file__).resolve().parents[1]
_M133 = str(_ROOT / "m133_ht_hidden_edge")
if _M133 not in sys.path:
    sys.path.insert(0, _M133)

from m133_ht_hidden_edge import Factored211Proposal  # noqa: E402


Array = np.ndarray


@dataclass(frozen=True)
class BalancedDrawAudit:
    """Non-secret diagnostics for one fixed-count balanced draw design."""

    component: Array
    centres: Array
    neighbour_uniforms: Array
    global_permutation: Array


def _probabilities(proposal: Factored211Proposal) -> Array:
    """The four mixture-bank probabilities, including the unchanged rescue."""

    if proposal.quadratic_normalizer <= 0.0:
        return np.asarray((1.0, 0.0, 0.0, 0.0), dtype=np.float64)
    rest = 1.0 - proposal.uniform_mixture
    banks = rest * np.asarray(
        (proposal.z_a, proposal.z_b, proposal.z_c), dtype=np.float64
    ) / proposal.quadratic_normalizer
    answer = np.concatenate((np.asarray((proposal.uniform_mixture,)), banks))
    if not np.all(np.isfinite(answer)) or np.any(answer < 0.0):
        raise ArithmeticError("invalid factored proposal mixture")
    answer[-1] += 1.0 - float(np.sum(answer))
    return answer


def _inverse_cdf(weights: Array, uniform: float) -> int:
    """Deterministic inverse CDF with zero-mass labels and ties killed.

    ``searchsorted(..., side='right')`` puts an exact CDF boundary in the next
    positive interval.  Thus no zero-mass or excluded label can re-enter due
    to an ambiguous floating point tie.
    """

    weights = np.asarray(weights, dtype=np.float64)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights < 0):
        raise ValueError("CDF weights must be one finite nonnegative vector")
    total = float(np.sum(weights))
    if not total > 0.0 or not (0.0 <= uniform < 1.0):
        raise ValueError("invalid inverse-CDF request")
    cdf = np.cumsum(weights / total)
    # Protect a true u=0 boundary and roundoff in the final CDF entry.
    index = int(np.searchsorted(cdf, uniform, side="right"))
    if index >= weights.size:
        index = weights.size - 1
    while index < weights.size and weights[index] == 0.0:
        index += 1
    if index >= weights.size:
        # This can only occur after an exact terminal boundary, so choose the
        # last positive mass deterministically rather than resurrect a tie.
        index = int(np.flatnonzero(weights > 0.0)[-1])
    return index


def _systematic_labels(weights: Array, count: int, rng: np.random.Generator) -> Array:
    """Randomized systematic sample with an unbiased centre-incidence law."""

    if type(count) is not int or count < 0:
        raise ValueError("count must be a nonnegative integer")
    if count == 0:
        return np.empty(0, dtype=np.int64)
    weights = np.asarray(weights, dtype=np.float64)
    if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights < 0):
        raise ValueError("systematic weights must be finite nonnegative")
    total = float(np.sum(weights))
    if total <= 0.0:
        raise ValueError("cannot systematically sample an empty support")
    cumulative = np.cumsum(weights / total)
    # u is uniform on [0,1/K); each label's expected count is K p_i.
    thresholds = (float(rng.random()) + np.arange(count, dtype=np.float64)) / count
    labels = np.searchsorted(cumulative, thresholds, side="right")
    labels = np.minimum(labels, weights.size - 1).astype(np.int64, copy=False)
    # A numerical exact boundary may select a zero-mass next bin.  Resolve it
    # deterministically without changing any positive-mass interval.
    for position, label in enumerate(labels):
        if weights[label] == 0.0:
            labels[position] = _inverse_cdf(weights, float(thresholds[position]))
    return labels


def _latin_uniforms(count: int, rng: np.random.Generator, dimensions: int) -> Array:
    """Independent randomized Latin-hypercube coordinates in ``[0,1)``.

    For a random position each coordinate is exactly uniform.  Independent
    permutations and jitters make the two conditional neighbour coordinates
    independent for that position, while reducing aggregate CDF discrepancy.
    """

    if type(count) is not int or count < 0 or dimensions <= 0:
        raise ValueError("invalid Latin-hypercube dimensions")
    if count == 0:
        return np.empty((0, dimensions), dtype=np.float64)
    answer = np.empty((count, dimensions), dtype=np.float64)
    for dimension in range(dimensions):
        answer[:, dimension] = (
            rng.permutation(count).astype(np.float64) + rng.random(count)
        ) / count
    return answer


def _radical_inverse_base2(index: int) -> float:
    """Base-two radical inverse, used only for a randomized OA-like pairing."""

    value = 0.0
    scale = 0.5
    while index:
        value += scale * (index & 1)
        index >>= 1
        scale *= 0.5
    return value


def _orthogonal_latin_uniforms(count: int, rng: np.random.Generator, dimensions: int) -> Array:
    """Random-shifted, permuted Hammersley Latin hypercube.

    The first coordinate is one-per-stratum.  Every other coordinate is a
    radical-inverse sequence with an independent uniform torus shift.  Hence a
    fixed labelled row is jointly uniform in ``[0,1)^d`` (the shifts provide
    exact randomization), while the complete set has a two-dimensional
    space-filling coupling absent from independent Latin permutations.
    """

    if type(count) is not int or count < 0 or dimensions <= 0:
        raise ValueError("invalid orthogonal-Latin dimensions")
    if count == 0:
        return np.empty((0, dimensions), dtype=np.float64)
    base = np.arange(count, dtype=np.int64)
    answer = np.empty((count, dimensions), dtype=np.float64)
    answer[:, 0] = (base.astype(np.float64) + rng.random(count)) / count
    for dimension in range(1, dimensions):
        values = np.asarray([_radical_inverse_base2(int(item)) for item in base])
        answer[:, dimension] = (values + float(rng.random())) % 1.0
    # Random row labels preserve the systematic centre draw but avoid granting
    # a particular centre a fixed low-discrepancy coordinate.
    return answer[rng.permutation(count)]


def _antithetic_orthogonal_latin_uniforms(
    count: int, rng: np.random.Generator, dimensions: int
) -> Array:
    """A pairwise antithetic randomized OA/LH coupling.

    For each low-discrepancy conditional vector ``u`` this emits ``1-u`` as
    well.  Both rows are jointly uniform under the randomized shifts, so the
    proposal marginal is unchanged; their negative CDF displacement targets
    the remaining centre-balanced variance without another product call.
    """

    if type(count) is not int or count < 0 or dimensions <= 0:
        raise ValueError("invalid antithetic orthogonal-Latin dimensions")
    if count == 0:
        return np.empty((0, dimensions), dtype=np.float64)
    pairs = count // 2
    base = _orthogonal_latin_uniforms(pairs, rng, dimensions)
    answer = np.concatenate((base, (1.0 - base) % 1.0), axis=0)
    if count % 2:
        answer = np.concatenate((answer, rng.random((1, dimensions))), axis=0)
    return answer[rng.permutation(count)]


def _uniform_ordered_triple(width: int, uniforms: Array) -> tuple[int, int, int]:
    """Exact inverse-CDF draw from the ordered, distinct uniform population."""

    if uniforms.shape != (3,):
        raise ValueError("uniform rescue needs three uniforms")
    i = min(int(math.floor(float(uniforms[0]) * width)), width - 1)
    j_short = min(int(math.floor(float(uniforms[1]) * (width - 1))), width - 2)
    j = j_short if j_short < i else j_short + 1
    k_short = min(int(math.floor(float(uniforms[2]) * (width - 2))), width - 3)
    remaining = [label for label in range(width) if label != i and label != j]
    return i, j, int(remaining[k_short])


def _factored_triple(
    proposal: Factored211Proposal,
    component: int,
    centre: int,
    uniforms: Array,
) -> tuple[int, int, int]:
    """One exact conditional draw from factored bank A, B, or C."""

    if component not in (1, 2, 3) or uniforms.shape != (2,):
        raise ValueError("invalid factored conditional request")
    s, r = proposal.absolute_residual, proposal.node_norm
    if component == 1:  # A: i is the repeated-node centre.
        i = centre
        a = s[i] * r
        row_sum = float(np.sum(a))
        j = _inverse_cdf(a * (row_sum - a), float(uniforms[0]))
        conditional = a.copy()
        conditional[j] = 0.0
        k = _inverse_cdf(conditional, float(uniforms[1]))
        return i, j, k
    if component == 2:  # B: j is the path centre.
        j = centre
        s_column = s[:, j]
        left = r**2 * s_column
        right = r * s_column
        i = _inverse_cdf(left * (float(np.sum(right)) - right), float(uniforms[0]))
        conditional = right.copy()
        conditional[i] = 0.0
        k = _inverse_cdf(conditional, float(uniforms[1]))
        return i, j, k
    # C: k is the labelled path centre; this is not folded into B because it
    # would silently change the ordered-slot gauge.
    k = centre
    s_column = s[:, k]
    left = r**2 * s_column
    right = r * s_column
    i = _inverse_cdf(left * (float(np.sum(right)) - right), float(uniforms[0]))
    conditional = right.copy()
    conditional[i] = 0.0
    j = _inverse_cdf(conditional, float(uniforms[1]))
    return i, j, k


def balanced_factored_draws(
    proposal: Factored211Proposal,
    rng: np.random.Generator,
    count: int,
    *,
    neighbour_design: str = "orthogonal_latin",
    return_audit: bool = False,
) -> Array | tuple[Array, BalancedDrawAudit]:
    """Return K dependent draws with M133's one-draw marginal exactly.

    First draw a randomized systematic allocation among the unchanged uniform
    rescue and the A/B/C banks.  Within each nonempty stratum use systematic
    centres and randomized-Latin conditional CDF coordinates, then uniformly
    permute all K labelled slots.  Exchangeability after the final permutation
    gives every returned row exactly proposal ``q`` marginally; dependence is
    intentional and is the only new variance-reduction mechanism.
    """

    if type(count) is not int or count <= 0:
        raise ValueError("balanced sampling needs a positive integer count")
    mixture = _probabilities(proposal)
    if neighbour_design not in ("latin", "orthogonal_latin", "antithetic_orthogonal_latin"):
        raise ValueError("unknown balanced neighbour design")
    draw_uniforms = {
        "latin": _latin_uniforms,
        "orthogonal_latin": _orthogonal_latin_uniforms,
        "antithetic_orthogonal_latin": _antithetic_orthogonal_latin_uniforms,
    }[neighbour_design]
    components = _systematic_labels(mixture, count, rng)
    draws = np.empty((count, 3), dtype=np.int64)
    centres = np.full(count, -1, dtype=np.int64)
    neighbour_uniforms = np.full((count, 3), np.nan, dtype=np.float64)
    centre_weights = (None, proposal.center_a, proposal.center_b, proposal.center_c)

    for component in range(4):
        positions = np.flatnonzero(components == component)
        local_count = int(positions.size)
        if local_count == 0:
            continue
        if component == 0:
            uniforms = draw_uniforms(local_count, rng, 3)
            for local, position in enumerate(positions):
                draws[position] = _uniform_ordered_triple(proposal.width, uniforms[local])
                neighbour_uniforms[position] = uniforms[local]
            continue
        selected_centres = _systematic_labels(centre_weights[component], local_count, rng)
        uniforms = draw_uniforms(local_count, rng, 2)
        for local, position in enumerate(positions):
            centre = int(selected_centres[local])
            draws[position] = _factored_triple(
                proposal, component, centre, uniforms[local]
            )
            centres[position] = centre
            neighbour_uniforms[position, :2] = uniforms[local]

    # The shuffle makes every *labelled output position* exchangeable.  It is
    # required for the standard HH 1/(K q) scale, not merely cosmetic.
    permutation = rng.permutation(count)
    draws = draws[permutation]
    components = components[permutation]
    centres = centres[permutation]
    neighbour_uniforms = neighbour_uniforms[permutation]
    if np.any(draws < 0) or any(len(set(row.tolist())) != 3 for row in draws):
        raise ArithmeticError("balanced conditional sampler emitted a collision")
    if return_audit:
        return draws, BalancedDrawAudit(
            components, centres, neighbour_uniforms, permutation
        )
    return draws


def balanced_sampling_bill(
    *, width: int = 256, count: int = 512, layers: int = 31, safety_factor: float = 1.25
) -> dict[str, int | float]:
    """Conservative scalar/copy/gather/sort bill for the balancing operator.

    It charges all K-by-n conditional vectors, four systematic CDF passes,
    Latin permutations/sorts, gathers, and fresh temporary buffers.  It has no
    dense product and no O(n^3) catalogue.  The 100ms residual reserve remains
    owned by M133's full first-order worksheet and is not spent twice here.
    """

    if min(width, count, layers) <= 0 or safety_factor < 1.0:
        raise ValueError("invalid balanced-sampling bill")
    # Four mixture/centre CDF scans and K conditional O(n) vectors.  Sorting
    # and gather rates follow the stated flopscope 4-per-element convention;
    # fill/copy/scalar vector operations are deliberately rounded upward.
    cdf_build = 8 * width * width + 8 * count * width
    conditional_exclusion = 20 * count * width
    latin_permute_sort_gather = 4 * (12 * count + 8 * width)
    buffer_fill_copy = 18 * count * width + 12 * width * width
    raw_per_layer = (
        cdf_build + conditional_exclusion + latin_permute_sort_gather + buffer_fill_copy
    )
    raw = layers * raw_per_layer
    return {
        "width": width,
        "count": count,
        "layers": layers,
        "raw_scalar_copy_gather_sort_bill": int(raw),
        "protected_increment": int(math.ceil(safety_factor * raw)),
        "full_triple_catalog_entries": 0,
        "additional_rectangular_products": 0,
        "unchanged_uniform_rescue": 0.05,
    }
