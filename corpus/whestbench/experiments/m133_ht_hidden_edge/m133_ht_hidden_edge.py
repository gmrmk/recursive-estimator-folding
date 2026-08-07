"""Generated-only fixed-size HT estimators for M126's hidden edge terms.

The module owns exactly three disjoint linear populations:

* the off-diagonal central ``Q-I`` edge in the hard AABB path orbit;
* the off-diagonal ``[2,2]`` collision-defect edge; and
* one canonical ``[2,1,1]`` unit ``(i; j<k)``.

Every other bridge factor is deterministic and uses the full supplied bridge.
This detail is essential: inserting one random bridge into multiple factors
would create products of inclusion indicators and would not be HT-unbiased.

The code contains no challenge loader, truth, scorer, model repository, board,
submission, or champion access.  It is a small/generated algebra audit only.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np


Array = np.ndarray


def _finite_matrix(name: str, value: Array) -> Array:
    answer = np.asarray(value, dtype=np.float64)
    if answer.ndim != 2 or not np.all(np.isfinite(answer)):
        raise ValueError(f"{name} must be one finite matrix")
    return answer


def _bridge(value: Array) -> Array:
    q = _finite_matrix("q", value)
    if q.shape[0] != q.shape[1]:
        raise ValueError("q must be square")
    if not np.allclose(q, q.T, rtol=0.0, atol=2e-12):
        raise ValueError("q must be symmetric")
    if not np.allclose(np.diag(q), 1.0, rtol=0.0, atol=2e-12):
        raise ValueError("q must have unit diagonal")
    return q


def _weight(value: Array, rows: int) -> Array:
    weight = _finite_matrix("weight", value)
    if weight.shape[0] != rows:
        raise ValueError("weight row count must match the source width")
    return weight


def _vector(name: str, value: Array, size: int) -> Array:
    answer = np.asarray(value, dtype=np.float64)
    if answer.shape != (size,) or not np.all(np.isfinite(answer)):
        raise ValueError(f"{name} must be one finite length-{size} vector")
    return answer


@dataclass(frozen=True)
class EdgeCatalog:
    units: Array
    coefficients: Array
    feature_norm: Array
    scores: Array
    weight: Array
    propagated: Array | None = None
    gamma2: Array | None = None


@dataclass(frozen=True)
class Collision211Catalog:
    units: Array
    coefficients: Array
    feature_norm_upper: Array
    scores: Array
    weight: Array
    norm_mode: str


@dataclass(frozen=True)
class Factored211Proposal:
    """O(n^2)-constructed ordered-triple proposal with uniform rescue mass."""

    absolute_residual: Array
    node_norm: Array
    z_a: float
    z_b: float
    z_c: float
    center_a: Array
    center_b: Array
    center_c: Array
    uniform_mixture: float

    @property
    def width(self) -> int:
        return int(self.node_norm.size)

    @property
    def quadratic_normalizer(self) -> float:
        return self.z_a + self.z_b + self.z_c

    @property
    def ordered_population(self) -> int:
        return self.width * (self.width - 1) * (self.width - 2)

    def _quadratic_weight(self, repeated: int, left: int, right: int) -> float:
        s = self.absolute_residual
        r = self.node_norm
        common = r[repeated] ** 2 * r[left] * r[right]
        return float(
            common
            * (
                s[repeated, left] * s[repeated, right]
                + s[repeated, left] * s[left, right]
                + s[repeated, right] * s[left, right]
            )
        )

    def probability(self, repeated: int, left: int, right: int) -> float:
        if not (0 <= repeated < self.width and 0 <= left < self.width and 0 <= right < self.width):
            raise IndexError("ordered triple label is out of range")
        if len({repeated, left, right}) != 3:
            return 0.0
        uniform = self.uniform_mixture / self.ordered_population
        normalizer = self.quadratic_normalizer
        if normalizer <= 0.0:
            return 1.0 / self.ordered_population
        return uniform + (1.0 - self.uniform_mixture) * self._quadratic_weight(
            repeated, left, right
        ) / normalizer

    @staticmethod
    def _draw(weights: Array, rng: np.random.Generator) -> int:
        total = float(np.sum(weights))
        if total <= 0.0:
            raise ArithmeticError("attempted to draw from an empty proposal bank")
        return int(rng.choice(weights.size, p=weights / total))

    def _draw_uniform(self, rng: np.random.Generator) -> tuple[int, int, int]:
        labels = rng.choice(self.width, size=3, replace=False)
        return int(labels[0]), int(labels[1]), int(labels[2])

    def _draw_a(self, rng: np.random.Generator) -> tuple[int, int, int]:
        i = self._draw(self.center_a, rng)
        a = self.absolute_residual[i] * self.node_norm
        row_sum = float(np.sum(a))
        j = self._draw(a * (row_sum - a), rng)
        conditional = a.copy()
        conditional[j] = 0.0
        k = self._draw(conditional, rng)
        return i, j, k

    def _draw_b(self, rng: np.random.Generator) -> tuple[int, int, int]:
        j = self._draw(self.center_b, rng)
        s = self.absolute_residual[:, j]
        left_weight = self.node_norm**2 * s
        right_weight = self.node_norm * s
        right_sum = float(np.sum(right_weight))
        i = self._draw(left_weight * (right_sum - right_weight), rng)
        conditional = right_weight.copy()
        conditional[i] = 0.0
        k = self._draw(conditional, rng)
        return i, j, k

    def _draw_c(self, rng: np.random.Generator) -> tuple[int, int, int]:
        k = self._draw(self.center_c, rng)
        s = self.absolute_residual[:, k]
        left_weight = self.node_norm**2 * s
        right_weight = self.node_norm * s
        right_sum = float(np.sum(right_weight))
        i = self._draw(left_weight * (right_sum - right_weight), rng)
        conditional = right_weight.copy()
        conditional[i] = 0.0
        j = self._draw(conditional, rng)
        return i, j, k

    def sample(self, rng: np.random.Generator, count: int) -> Array:
        if type(count) is not int or count < 0:
            raise ValueError("count must be a nonnegative integer")
        answer = np.empty((count, 3), dtype=np.int64)
        normalizer = self.quadratic_normalizer
        bank_weights = np.asarray((self.z_a, self.z_b, self.z_c), dtype=np.float64)
        for position in range(count):
            if normalizer <= 0.0 or float(rng.random()) < self.uniform_mixture:
                answer[position] = self._draw_uniform(rng)
                continue
            bank = self._draw(bank_weights, rng)
            if bank == 0:
                answer[position] = self._draw_a(rng)
            elif bank == 1:
                answer[position] = self._draw_b(rng)
            else:
                answer[position] = self._draw_c(rng)
        return answer


def _edge_units(size: int) -> Array:
    left, right = np.triu_indices(size, k=1)
    return np.column_stack((left, right)).astype(np.int64, copy=False)


def path_feature(
    propagated: Array, gamma2: Array, weight: Array, left: int, right: int
) -> Array:
    """Coefficient-free orbit matrix for one central residual edge.

    Put ``D_i[a,b]=g_i(A_ia W_ib+W_ia A_ib)``.  Because the residual is
    symmetric and hollow, ``2 D_ab.T E D_ab`` contributes
    ``E_ij * 4(D_i o D_j)`` for the canonical undirected edge ``i<j``.
    """

    a_i = propagated[left]
    a_j = propagated[right]
    w_i = weight[left]
    w_j = weight[right]
    d_i = gamma2[left] * (np.outer(a_i, w_i) + np.outer(w_i, a_i))
    d_j = gamma2[right] * (np.outer(a_j, w_j) + np.outer(w_j, a_j))
    return 4.0 * d_i * d_j


def _path_pair_gram(
    propagated: Array, weight: Array, left: int, right: int
) -> Array:
    a_i = propagated[left]
    a_j = propagated[right]
    w_i = weight[left]
    w_j = weight[right]
    vectors = np.stack(
        (a_i * a_j, a_i * w_j, w_i * a_j, w_i * w_j), axis=1
    )
    return vectors.T @ vectors


def path_feature_norm_fast(
    propagated: Array, gamma2: Array, weight: Array, left: int, right: int
) -> float:
    """Exact O(outputs) norm, without materialising an output matrix."""

    gram = _path_pair_gram(propagated, weight, left, right)
    reverse = np.asarray((3, 2, 1, 0))
    right_gram = gram[np.ix_(reverse, reverse)]
    base_squared = max(0.0, float(np.sum(gram * right_gram)))
    return 4.0 * abs(float(gamma2[left] * gamma2[right])) * math.sqrt(
        base_squared
    )


def _all_path_feature_norms_six_grams(
    propagated: Array, gamma2: Array, weight: Array, units: Array
) -> Array:
    """All exact path norms after six n-by-output Gram products.

    The four left vectors are ``AA, AW, WA, WW`` and the right vectors are
    their reversal.  Their 4x4 Gram for every source pair is assembled from
    the six pairwise Grams of ``A^2, A*W, W^2``.
    """

    a2 = propagated * propagated
    aw = propagated * weight
    w2 = weight * weight
    aa = a2 @ a2.T
    ab = a2 @ aw.T
    ac = a2 @ w2.T
    bb = aw @ aw.T
    bc = aw @ w2.T
    cc = w2 @ w2.T
    answer = np.empty(units.shape[0], dtype=np.float64)
    reverse = np.asarray((3, 2, 1, 0))
    for position, (i, j) in enumerate(units):
        gram = np.asarray(
            (
                (aa[i, j], ab[i, j], ab[j, i], bb[i, j]),
                (ab[i, j], ac[i, j], bb[i, j], bc[i, j]),
                (ab[j, i], bb[i, j], ac[j, i], bc[j, i]),
                (bb[i, j], bc[i, j], bc[j, i], cc[i, j]),
            ),
            dtype=np.float64,
        )
        base_squared = max(
            0.0, float(np.sum(gram * gram[np.ix_(reverse, reverse)]))
        )
        answer[position] = (
            4.0 * abs(float(gamma2[i] * gamma2[j])) * math.sqrt(base_squared)
        )
    return answer


def path_conductance_catalog(q: Array, gamma2: Array, weight: Array) -> EdgeCatalog:
    q = _bridge(q)
    n = q.shape[0]
    gamma2 = _vector("gamma2", gamma2, n)
    weight = _weight(weight, n)
    propagated = q @ weight
    units = _edge_units(n)
    residual = q.copy()
    np.fill_diagonal(residual, 0.0)
    coefficients = residual[units[:, 0], units[:, 1]]
    norms = _all_path_feature_norms_six_grams(
        propagated, gamma2, weight, units
    )
    return EdgeCatalog(
        units=units,
        coefficients=coefficients,
        feature_norm=norms,
        scores=np.abs(coefficients) * norms,
        weight=weight,
        propagated=propagated,
        gamma2=gamma2,
    )


def collision22_feature(weight: Array, left: int, right: int) -> Array:
    vector = weight[left] * weight[right]
    return 4.0 * np.outer(vector, vector)


def collision22_conductance_catalog(paired4: Array, weight: Array) -> EdgeCatalog:
    paired4 = _finite_matrix("paired4", paired4)
    if paired4.shape[0] != paired4.shape[1]:
        raise ValueError("paired4 must be square")
    n = paired4.shape[0]
    weight = _weight(weight, n)
    if not np.allclose(paired4, paired4.T, rtol=0.0, atol=2e-12):
        raise ValueError("paired4 must be symmetric")
    if not np.allclose(np.diag(paired4), 0.0, rtol=0.0, atol=2e-12):
        raise ValueError("paired4 must be hollow")
    units = _edge_units(n)
    coefficients = paired4[units[:, 0], units[:, 1]]
    squared_gram = (weight * weight) @ (weight * weight).T
    norms = 4.0 * squared_gram[units[:, 0], units[:, 1]]
    return EdgeCatalog(
        units=units,
        coefficients=coefficients,
        feature_norm=norms,
        scores=np.abs(coefficients) * norms,
        weight=weight,
    )


def _validate_211(defect211: Array, weight: Array) -> tuple[Array, Array]:
    defect = np.asarray(defect211, dtype=np.float64)
    if defect.ndim != 3 or len(set(defect.shape)) != 1:
        raise ValueError("defect211 must be one cubic tensor")
    if not np.all(np.isfinite(defect)):
        raise ValueError("defect211 must be finite")
    n = defect.shape[0]
    weight = _weight(weight, n)
    if not np.allclose(defect, defect.swapaxes(1, 2), rtol=0.0, atol=2e-12):
        raise ValueError("singleton labels must be symmetric")
    for i in range(n):
        if (
            np.any(defect[i, i, :] != 0.0)
            or np.any(defect[i, :, i] != 0.0)
            or np.any(np.diag(defect[i]) != 0.0)
        ):
            raise ValueError("defect211 must be hollow on every label collision")
    return defect, weight


def collision211_feature(weight: Array, repeated: int, left: int, right: int) -> dict[str, Array]:
    """Coefficient-free twelve-slot repeated-output contribution."""

    x = weight[repeated]
    y = weight[left]
    z = weight[right]
    aaab = (
        6.0 * np.outer(x * y * z, x)
        + 3.0 * np.outer(x * x * z, y)
        + 3.0 * np.outer(x * x * y, z)
    )
    aabb = (
        2.0 * np.outer(x * x, y * z)
        + 2.0 * np.outer(y * z, x * x)
        + 4.0 * np.outer(x * y, x * z)
        + 4.0 * np.outer(x * z, x * y)
    )
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def _hadamard_norm_bound(left: Array, right: Array) -> float:
    return min(
        float(np.max(np.abs(left))) * float(np.linalg.norm(right)),
        float(np.max(np.abs(right))) * float(np.linalg.norm(left)),
    )


def collision211_feature_norm_upper_bound(
    weight: Array, repeated: int, left: int, right: int
) -> float:
    """O(outputs) triangle bound used when exact triple norms are unaffordable."""

    x = weight[repeated]
    y = weight[left]
    z = weight[right]
    nx = float(np.linalg.norm(x))
    ny = float(np.linalg.norm(y))
    nz = float(np.linalg.norm(z))
    ix = float(np.max(np.abs(x)))
    iy = float(np.max(np.abs(y)))
    iz = float(np.max(np.abs(z)))
    nxyz = min(ix * iy * nz, ix * iz * ny, iy * iz * nx)
    nx2z = min(ix * ix * nz, ix * iz * nx)
    nx2y = min(ix * ix * ny, ix * iy * nx)
    bound31 = 6.0 * nxyz * nx + 3.0 * nx2z * ny + 3.0 * nx2y * nz
    nx2 = ix * nx
    nyz = _hadamard_norm_bound(y, z)
    nxy = _hadamard_norm_bound(x, y)
    nxz = _hadamard_norm_bound(x, z)
    bound22 = 4.0 * nx2 * nyz + 8.0 * nxy * nxz
    return math.hypot(bound31, bound22)


def collision211_conductance_catalog(
    defect211: Array, weight: Array, *, norm_mode: str = "upper"
) -> Collision211Catalog:
    defect, weight = _validate_211(defect211, weight)
    if norm_mode not in {"upper", "exact_generated_only"}:
        raise ValueError("norm_mode must be upper or exact_generated_only")
    n = defect.shape[0]
    units: list[tuple[int, int, int]] = []
    coefficients: list[float] = []
    norms: list[float] = []
    for repeated in range(n):
        for left in range(n):
            for right in range(left + 1, n):
                if len({repeated, left, right}) != 3:
                    continue
                coefficient = float(defect[repeated, left, right])
                if coefficient == 0.0:
                    continue
                units.append((repeated, left, right))
                coefficients.append(coefficient)
                if norm_mode == "upper":
                    norms.append(
                        collision211_feature_norm_upper_bound(
                            weight, repeated, left, right
                        )
                    )
                else:
                    feature = collision211_feature(weight, repeated, left, right)
                    norms.append(
                        math.sqrt(
                            float(np.sum(feature["k4_aaab"] ** 2))
                            + float(np.sum(feature["k4_aabb"] ** 2))
                        )
                    )
    unit_array = np.asarray(units, dtype=np.int64).reshape(-1, 3)
    coefficient_array = np.asarray(coefficients, dtype=np.float64)
    norm_array = np.asarray(norms, dtype=np.float64)
    return Collision211Catalog(
        units=unit_array,
        coefficients=coefficient_array,
        feature_norm_upper=norm_array,
        scores=np.abs(coefficient_array) * norm_array,
        weight=weight,
        norm_mode=norm_mode,
    )


def collision211_factored_proposal(
    q: Array, weight: Array, *, uniform_mixture: float = 0.05
) -> Factored211Proposal:
    """Build a three-tree-bank proposal without an ``n^3`` probability table.

    With ``S=abs(Q-I)`` and ``r_i=||W_i||_2``, the quadratic-jet conductance
    envelope is proportional to

    ``r_i^2 r_j r_k (S_ij S_ik + S_ij S_jk + S_ik S_jk)``.

    Each summand is sampled exactly by choosing its graph centre and then two
    distinct neighbours.  A fixed uniform mixture gives every ordered
    distinct triple positive support, including higher-order exact defects
    not represented by the quadratic envelope.
    """

    q = _bridge(q)
    n = q.shape[0]
    if n < 3:
        raise ValueError("the [2,1,1] proposal needs width at least three")
    weight = _weight(weight, n)
    if not math.isfinite(uniform_mixture) or not (0.0 < uniform_mixture <= 1.0):
        raise ValueError("uniform_mixture must lie in (0,1]")
    residual = np.abs(q.copy())
    np.fill_diagonal(residual, 0.0)
    node_norm = np.linalg.norm(weight, axis=1)

    # A bank: i is the repeated-label centre, j and k are distinct neighbours.
    a = residual * node_norm[None, :]
    a_sum = np.sum(a, axis=1)
    a_distinct = a_sum * a_sum - np.sum(a * a, axis=1)
    center_a = node_norm**2 * np.maximum(a_distinct, 0.0)

    # B bank: j is the path centre i-j-k.  C has the same local normalizer but
    # names k as the centre; retaining both banks preserves labelled slots.
    center_b = np.zeros(n, dtype=np.float64)
    center_c = np.zeros(n, dtype=np.float64)
    for centre in range(n):
        s = residual[:, centre]
        left = node_norm**2 * s
        right = node_norm * s
        distinct = float(np.sum(left) * np.sum(right) - left @ right)
        center_b[centre] = node_norm[centre] * max(0.0, distinct)
        center_c[centre] = center_b[centre]

    return Factored211Proposal(
        absolute_residual=residual,
        node_norm=node_norm,
        z_a=float(np.sum(center_a)),
        z_b=float(np.sum(center_b)),
        z_c=float(np.sum(center_c)),
        center_a=center_a,
        center_b=center_b,
        center_c=center_c,
        uniform_mixture=float(uniform_mixture),
    )


def _validate_ordered_draws(weight: Array, proposal: Factored211Proposal, draws: Array) -> Array:
    draws = np.asarray(draws, dtype=np.int64)
    if draws.ndim != 2 or draws.shape[1] != 3:
        raise ValueError("draws must have shape (count,3)")
    if weight.shape[0] != proposal.width:
        raise ValueError("proposal and weight widths disagree")
    if np.any(draws < 0) or np.any(draws >= proposal.width):
        raise ValueError("a sampled label is out of range")
    if any(len(set(int(item) for item in row)) != 3 for row in draws):
        raise ValueError("every sampled ordered triple must have distinct labels")
    if draws.shape[0] == 0:
        raise ValueError("the HH estimator needs at least one draw")
    return draws


def _hh_scales(
    proposal: Factored211Proposal,
    draws: Array,
    coefficient: Callable[[int, int, int], float],
) -> Array:
    count = draws.shape[0]
    scales = np.empty(count, dtype=np.float64)
    for position, row in enumerate(draws):
        i, j, k = (int(item) for item in row)
        probability = proposal.probability(i, j, k)
        value = float(coefficient(i, j, k))
        if not math.isfinite(value) or probability <= 0.0:
            raise ValueError("non-finite coefficient or zero proposal support")
        # Ordered singletons represent every canonical j<k unit twice.
        scales[position] = value / (2.0 * count * probability)
    return scales


def collision211_hh_direct(
    weight: Array,
    proposal: Factored211Proposal,
    draws: Array,
    coefficient: Callable[[int, int, int], float],
) -> dict[str, Array]:
    """Direct reference for fixed-count with-replacement importance sampling.

    This is Hansen--Hurwitz, not without-replacement Horvitz--Thompson.  The
    distinction matters; both are unbiased, but this form has a strict count
    and admits five batched rectangular products.
    """

    weight = _weight(weight, proposal.width)
    draws = _validate_ordered_draws(weight, proposal, draws)
    scales = _hh_scales(proposal, draws, coefficient)
    outputs = weight.shape[1]
    result = {
        "k4_aaaa": np.zeros(outputs, dtype=np.float64),
        "k4_aaab": np.zeros((outputs, outputs), dtype=np.float64),
        "k4_aabb": np.zeros((outputs, outputs), dtype=np.float64),
    }
    for row, scale in zip(draws, scales):
        feature = collision211_feature(weight, *(int(item) for item in row))
        for key in result:
            result[key] += scale * feature[key]
    return result


def collision211_hh_batched(
    weight: Array,
    proposal: Factored211Proposal,
    draws: Array,
    coefficient: Callable[[int, int, int], float],
) -> dict[str, Array]:
    """The same HH estimate using exactly five rectangular matrix products."""

    weight = _weight(weight, proposal.width)
    draws = _validate_ordered_draws(weight, proposal, draws)
    scales = _hh_scales(proposal, draws, coefficient)
    x = weight[draws[:, 0]]
    y = weight[draws[:, 1]]
    z = weight[draws[:, 2]]

    aaab = (
        ((6.0 * scales)[:, None] * x * y * z).T @ x
        + ((3.0 * scales)[:, None] * x * x * z).T @ y
        + ((3.0 * scales)[:, None] * x * x * y).T @ z
    )
    first = ((2.0 * scales)[:, None] * x * x).T @ (y * z)
    second = ((4.0 * scales)[:, None] * x * y).T @ (x * z)
    aabb = first + first.T + second + second.T
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def collision211_hh_batched_tangent(
    weight: Array,
    proposal: Factored211Proposal,
    draws: Array,
    coefficient_dual: Callable[[int, int, int], tuple[float, float]],
) -> tuple[dict[str, Array], dict[str, Array]]:
    """Primal and pathwise tangent with the proposal frozen at background.

    For fixed ``q0(e)>0``, differentiating
    ``E_q0[F_e(theta)/q0(e)]`` needs ``Fdot/q0`` and no score-function or
    ``qdot`` term.  The two outputs each use the same five rectangular product
    families and the exact same sampled triples.
    """

    draws = np.asarray(draws, dtype=np.int64)
    cache: dict[tuple[int, int, int], tuple[float, float]] = {}
    for row in draws:
        unit = tuple(int(item) for item in row)
        if unit not in cache:
            value, tangent = coefficient_dual(*unit)
            if not math.isfinite(value) or not math.isfinite(tangent):
                raise ValueError("dual coefficient must be finite")
            cache[unit] = (float(value), float(tangent))
    primal = collision211_hh_batched(
        weight, proposal, draws, lambda i, j, k: cache[(i, j, k)][0]
    )
    tangent = collision211_hh_batched(
        weight, proposal, draws, lambda i, j, k: cache[(i, j, k)][1]
    )
    return primal, tangent


def waterfill_inclusion_probabilities(scores: Array, sample_size: int) -> Array:
    """Return ``pi=min(1,c*score)`` with integer ``sum(pi)=sample_size``."""

    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 1 or not np.all(np.isfinite(scores)) or np.any(scores < 0.0):
        raise ValueError("scores must be one finite nonnegative vector")
    if type(sample_size) is not int or sample_size < 0:
        raise ValueError("sample_size must be a nonnegative integer")
    positive = scores > 0.0
    count = int(np.sum(positive))
    if sample_size > count:
        raise ValueError("sample size exceeds the number of nonzero contributions")
    probabilities = np.zeros_like(scores)
    if sample_size == 0:
        return probabilities
    if sample_size == count:
        probabilities[positive] = 1.0
        return probabilities
    active = positive.copy()
    remaining = sample_size
    while True:
        scale = remaining / float(np.sum(scores[active]))
        saturated = active & (scale * scores >= 1.0)
        if not np.any(saturated):
            probabilities[active] = scale * scores[active]
            break
        probabilities[saturated] = 1.0
        remaining -= int(np.sum(saturated))
        active[saturated] = False
    discrepancy = float(sample_size - np.sum(probabilities))
    if abs(discrepancy) > 2e-12:
        fractional = np.flatnonzero((probabilities > 0.0) & (probabilities < 1.0))
        if fractional.size == 0:
            raise ArithmeticError("could not close inclusion probability sum")
        probabilities[fractional[-1]] += discrepancy
    if np.any(probabilities < -2e-13) or np.any(probabilities > 1.0 + 2e-13):
        raise ArithmeticError("water filling left the probability interval")
    probabilities = np.clip(probabilities, 0.0, 1.0)
    return probabilities


def systematic_pps_sample(
    probabilities: Array, *, phase: float, order: Array | None = None
) -> Array:
    """One fixed-size systematic PPS sample with exact first-order ``pi``.

    Conditional on any fixed order, unit ``i`` occupies an interval of length
    ``pi_i`` on the unit circle.  A uniform phase therefore includes it with
    probability ``pi_i``.  The returned work count is exactly ``sum(pi)``.
    """

    probabilities = np.asarray(probabilities, dtype=np.float64)
    if probabilities.ndim != 1 or np.any(probabilities < 0.0) or np.any(probabilities > 1.0):
        raise ValueError("probabilities must lie in [0,1]")
    if not math.isfinite(phase) or not (0.0 <= phase < 1.0):
        raise ValueError("phase must lie in [0,1)")
    total = float(np.sum(probabilities))
    sample_size = int(round(total))
    if abs(total - sample_size) > 3e-10:
        raise ValueError("systematic PPS requires an integer probability sum")
    if order is None:
        order = np.arange(probabilities.size, dtype=np.int64)
    else:
        order = np.asarray(order, dtype=np.int64)
        if order.shape != probabilities.shape or not np.array_equal(
            np.sort(order), np.arange(probabilities.size)
        ):
            raise ValueError("order must be a permutation")
    selected = np.zeros(probabilities.size, dtype=bool)
    if sample_size == 0:
        return selected
    cumulative = np.cumsum(probabilities[order])
    cumulative[-1] = float(sample_size)
    thresholds = phase + np.arange(sample_size, dtype=np.float64)
    positions = np.searchsorted(cumulative, thresholds, side="right")
    chosen = order[positions]
    if np.unique(chosen).size != sample_size:
        raise ArithmeticError("systematic PPS selected a unit twice")
    selected[chosen] = True
    return selected


def _check_ht(probabilities: Array, selected: Array, catalog_size: int) -> tuple[Array, Array]:
    probabilities = np.asarray(probabilities, dtype=np.float64)
    selected = np.asarray(selected, dtype=bool)
    if probabilities.shape != (catalog_size,) or selected.shape != (catalog_size,):
        raise ValueError("HT probability/mask shape mismatch")
    if np.any(selected & (probabilities <= 0.0)):
        raise ValueError("a selected HT unit has zero inclusion probability")
    return probabilities, selected


def _edge_sum(
    catalog: EdgeCatalog,
    coefficient_scale: Callable[[int], float],
    feature: Callable[[int, int], Array],
) -> Array:
    outputs = catalog.weight.shape[1]
    result = np.zeros((outputs, outputs), dtype=np.float64)
    for position, (left, right) in enumerate(catalog.units):
        result += coefficient_scale(position) * feature(int(left), int(right))
    return result


def path_exact_from_catalog(catalog: EdgeCatalog) -> Array:
    assert catalog.propagated is not None and catalog.gamma2 is not None
    return _edge_sum(
        catalog,
        lambda position: float(catalog.coefficients[position]),
        lambda left, right: path_feature(
            catalog.propagated, catalog.gamma2, catalog.weight, left, right
        ),
    )


def path_ht_sample(catalog: EdgeCatalog, probabilities: Array, selected: Array) -> Array:
    probabilities, selected = _check_ht(probabilities, selected, catalog.units.shape[0])
    assert catalog.propagated is not None and catalog.gamma2 is not None
    outputs = catalog.weight.shape[1]
    result = np.zeros((outputs, outputs), dtype=np.float64)
    for position in np.flatnonzero(selected):
        left, right = catalog.units[position]
        result += (
            catalog.coefficients[position]
            / probabilities[position]
            * path_feature(
                catalog.propagated,
                catalog.gamma2,
                catalog.weight,
                int(left),
                int(right),
            )
        )
    return result


def collision22_exact_from_catalog(catalog: EdgeCatalog) -> Array:
    return _edge_sum(
        catalog,
        lambda position: float(catalog.coefficients[position]),
        lambda left, right: collision22_feature(catalog.weight, left, right),
    )


def collision22_ht_sample(catalog: EdgeCatalog, probabilities: Array, selected: Array) -> Array:
    probabilities, selected = _check_ht(probabilities, selected, catalog.units.shape[0])
    outputs = catalog.weight.shape[1]
    result = np.zeros((outputs, outputs), dtype=np.float64)
    for position in np.flatnonzero(selected):
        left, right = catalog.units[position]
        result += (
            catalog.coefficients[position]
            / probabilities[position]
            * collision22_feature(catalog.weight, int(left), int(right))
        )
    return result


def collision211_exact_from_catalog(catalog: Collision211Catalog) -> dict[str, Array]:
    outputs = catalog.weight.shape[1]
    result = {
        "k4_aaaa": np.zeros(outputs, dtype=np.float64),
        "k4_aaab": np.zeros((outputs, outputs), dtype=np.float64),
        "k4_aabb": np.zeros((outputs, outputs), dtype=np.float64),
    }
    for position, unit in enumerate(catalog.units):
        feature = collision211_feature(catalog.weight, *(int(item) for item in unit))
        for key in result:
            result[key] += catalog.coefficients[position] * feature[key]
    return result


def collision211_ht_sample(
    catalog: Collision211Catalog, probabilities: Array, selected: Array
) -> dict[str, Array]:
    probabilities, selected = _check_ht(probabilities, selected, catalog.units.shape[0])
    outputs = catalog.weight.shape[1]
    result = {
        "k4_aaaa": np.zeros(outputs, dtype=np.float64),
        "k4_aaab": np.zeros((outputs, outputs), dtype=np.float64),
        "k4_aabb": np.zeros((outputs, outputs), dtype=np.float64),
    }
    for position in np.flatnonzero(selected):
        unit = catalog.units[position]
        feature = collision211_feature(catalog.weight, *(int(item) for item in unit))
        scale = catalog.coefficients[position] / probabilities[position]
        for key in result:
            result[key] += scale * feature[key]
    return result


def collision211_hollow_probe(defect211: Array, weight: Array, probe: Array) -> dict[str, Array]:
    """One M129 hollow-quadratic Rademacher sample for comparison."""

    defect, weight = _validate_211(defect211, weight)
    n = defect.shape[0]
    probe = _vector("probe", probe, n)
    t = np.einsum("ijk,j,k->i", defect, probe, probe, optimize=True)
    projection = probe @ weight
    gram = weight.T @ (t[:, None] * weight)
    diagonal = np.diag(gram).copy()
    uaub = np.outer(projection, projection)
    aaab = 1.5 * (
        gram * projection[:, None] ** 2 + diagonal[:, None] * uaub
    )
    aabb = (
        0.5
        * (
            diagonal[:, None] * projection[None, :] ** 2
            + diagonal[None, :] * projection[:, None] ** 2
        )
        + 2.0 * gram * uaub
    )
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def flopscope_ht_ledger(
    *,
    path_samples: int,
    collision22_samples: int,
    collision211_samples: int,
    width: int = 256,
    layers: int = 31,
    safety_factor: float = 1.25,
) -> dict[str, int | float | bool]:
    """Conservative f32 target worksheet for the fixed-size HT component.

    The inherited P=0 M126 source plus protected M125b carrier is fixed at
    52.964020560B.  Six dense Grams build exact ABAB/[2,2] conductances.  The
    [2,1,1] score plumbing deliberately charges twenty scalar/copy/sort-rate
    operations per canonical triple, but *not* the still-separate exact
    trivariate coefficient builder or measured residual wall time.
    """

    for name, value in (
        ("path_samples", path_samples),
        ("collision22_samples", collision22_samples),
        ("collision211_samples", collision211_samples),
    ):
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    if width <= 0 or layers <= 0 or safety_factor < 1.0:
        raise ValueError("invalid target ledger parameters")
    edges = math.comb(width, 2)
    triples = width * math.comb(width - 1, 2)
    if path_samples > edges or collision22_samples > edges or collision211_samples > triples:
        raise ValueError("sample count exceeds its canonical population")
    square = 2 * width**3 - width**2
    conductance_grams = layers * 6 * square
    edge_probability_plumbing = layers * edges * 16
    collision211_probability_plumbing = layers * triples * 20
    selected_outer_updates = (
        layers
        * 2
        * width**2
        * (
            4 * path_samples
            + collision22_samples
            + 5 * collision211_samples
        )
    )
    raw_ht_extra = (
        conductance_grams
        + edge_probability_plumbing
        + collision211_probability_plumbing
        + selected_outer_updates
    )
    protected_ht_extra = int(math.ceil(safety_factor * raw_ht_extra))
    inherited_p0_source_plus_m125b = 52_964_020_560
    total = inherited_p0_source_plus_m125b + protected_ht_extra
    return {
        "width": width,
        "layers": layers,
        "edge_population": edges,
        "collision211_population": triples,
        "path_samples": path_samples,
        "collision22_samples": collision22_samples,
        "collision211_samples": collision211_samples,
        "collision211_inclusion_fraction": collision211_samples / triples,
        "conductance_gram_raw_flops": conductance_grams,
        "probability_plumbing_raw_flops": (
            edge_probability_plumbing + collision211_probability_plumbing
        ),
        "selected_updates_raw_flops": selected_outer_updates,
        "raw_ht_extra": raw_ht_extra,
        "protected_ht_extra": protected_ht_extra,
        "protected_total_with_m125b": total,
        "fixed_size_hard_cap": True,
        "exact_211_owned": True,
        "exact_211_coefficient_builder_charged": False,
        "residual_wall_time_charged": False,
    }


def flopscope_batched_hh_ledger(
    *,
    path_samples: int,
    collision22_samples: int,
    collision211_samples: int,
    include_tangent: bool,
    width: int = 256,
    layers: int = 31,
    safety_factor: float = 1.25,
) -> dict[str, int | float | bool]:
    """Rectangular-product bill for fixed-count HH primal and frozen-q tangent.

    Four product families own the hard path edge, one owns ``[2,2]``, and five
    own ``[2,1,1]``.  With fixed network weights, their pathwise tangent needs
    respectively eight, one, and five *additional* products.  Exact sampled
    collision coefficients and their derivatives are deliberately flagged but
    uncharged because the current M122 Hermite-series oracle has not received a
    native target trace.
    """

    for name, value in (
        ("path_samples", path_samples),
        ("collision22_samples", collision22_samples),
        ("collision211_samples", collision211_samples),
    ):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if type(include_tangent) is not bool:
        raise ValueError("include_tangent must be boolean")
    if width <= 0 or layers <= 0 or safety_factor < 1.0:
        raise ValueError("invalid target ledger parameters")

    def rectangular(samples: int) -> int:
        return 2 * width * samples * width - width**2

    path_rect = rectangular(path_samples)
    collision22_rect = rectangular(collision22_samples)
    collision211_rect = rectangular(collision211_samples)
    primal_per_layer = 4 * path_rect + collision22_rect + 5 * collision211_rect
    tangent_increment_per_layer = (
        8 * path_rect + collision22_rect + 5 * collision211_rect
    )
    primal_raw = layers * primal_per_layer
    tangent_raw = layers * tangent_increment_per_layer if include_tangent else 0
    proposal_raw = layers * 48 * width**2
    protected_primal = int(math.ceil(safety_factor * (primal_raw + proposal_raw)))
    protected_tangent_increment = int(math.ceil(safety_factor * tangent_raw))
    inherited_p0_source_plus_m125b = 52_964_020_560
    return {
        "width": width,
        "layers": layers,
        "path_samples": path_samples,
        "collision22_samples": collision22_samples,
        "collision211_samples": collision211_samples,
        "path_rectangular_f32_bill": path_rect,
        "collision22_rectangular_f32_bill": collision22_rect,
        "collision211_rectangular_f32_bill": collision211_rect,
        "primal_raw_flops": primal_raw,
        "proposal_raw_flops": proposal_raw,
        "protected_primal_extra": protected_primal,
        "protected_tangent_increment": protected_tangent_increment,
        "protected_total_with_m125b": (
            inherited_p0_source_plus_m125b
            + protected_primal
            + protected_tangent_increment
        ),
        "fixed_count_hard_cap": True,
        "proposal_frozen_for_tangent": include_tangent,
        "sampled_exact_coefficients_charged": False,
        "sampled_exact_coefficient_tangents_charged": False,
        "residual_wall_time_charged": False,
    }
