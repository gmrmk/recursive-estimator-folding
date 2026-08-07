"""M124 generated-only shared-k3-projector source algebra.

The mechanism is deliberately narrow:

* construct one standardised rank-four projector from the exact cheap k3
  bridge-tree mode Gram, including M85-style one/two-coordinate replacements;
* use that same factor for both k3 and k4;
* form both projected cores exactly, including nonzero-mean path/star weights
  and collision corrections; and
* convert one transported source into the M121 delay-one Edgeworth
  mean/covariance defect.

This file has no challenge loader, scorer, submission path, learned coefficient,
or outcome-grid entry point.
"""

from __future__ import annotations

import itertools
import math
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np


M120_DIR = Path(__file__).resolve().parents[1] / "m120_price_normal_ordered_adjoint"
if str(M120_DIR) not in sys.path:
    sys.path.insert(0, str(M120_DIR))
from m120c_analytic_dense_reference import (  # noqa: E402
    AnalyticReferenceFailClosed,
    analytic_relu_gaussian_moments,
    quadrant_probability,
)


INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
RANK = 4
BOUNDARY_GAP_RELATIVE = 2.0**-36
VARIANCE_FLOOR = 1.0e-12
CORRELATION_MARGIN = 1.0e-10
MAX_COLLISION_ORDER = 4


class M124FailClosed(RuntimeError):
    """A domain, symmetry, rank, or spectral-boundary certificate failed."""


@dataclass(frozen=True)
class LocalVertices:
    alpha: np.ndarray
    relu_mean_standard: np.ndarray
    relu_scale_standard: np.ndarray
    gamma2: np.ndarray
    gamma3: np.ndarray


@dataclass(frozen=True)
class CollisionCorrections:
    """Sparse exact-minus-tree values; no order-three/four dense tensor."""

    diagonal3: np.ndarray
    majority3: np.ndarray
    diagonal4: np.ndarray
    majority4: np.ndarray
    paired4: np.ndarray


@dataclass(frozen=True)
class NonzeroBridgeSource:
    activation_mean: np.ndarray
    activation_covariance: np.ndarray
    activation_scale: np.ndarray
    bridge: np.ndarray
    vertices: LocalVertices
    collisions: CollisionCorrections
    standard_k3: np.ndarray
    standard_k4: np.ndarray
    tree_k3: np.ndarray
    tree_k4: np.ndarray


@dataclass(frozen=True)
class SharedProjector:
    factor_standard: np.ndarray
    eigenvalues: np.ndarray
    boundary_gap: float
    mode_gram: np.ndarray


@dataclass(frozen=True)
class ProjectedSource:
    factor_standard: np.ndarray
    factor_physical: np.ndarray
    core3: np.ndarray
    core4: np.ndarray


@dataclass(frozen=True)
class EdgeworthDefect:
    mean: np.ndarray
    covariance: np.ndarray


def _cdf(x: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(x, dtype=np.float64)
    answer = np.fromiter(
        (0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in values.ravel()),
        dtype=np.float64,
        count=values.size,
    ).reshape(values.shape)
    return float(answer) if answer.ndim == 0 else answer


def _pdf(x: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(x, dtype=np.float64)
    answer = np.exp(-0.5 * values * values) * INV_SQRT_2PI
    return float(answer) if answer.ndim == 0 else answer


def _validate_gaussian(mean: np.ndarray, covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if mean.ndim != 1 or covariance.shape != (mean.size, mean.size):
        raise ValueError("mean/covariance shape mismatch")
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(covariance)):
        raise M124FailClosed("non-finite Gaussian state")
    if not np.array_equal(covariance, covariance.T):
        raise M124FailClosed("covariance must be exactly symmetric")
    variance = np.diag(covariance)
    if np.any(variance <= VARIANCE_FLOOR):
        raise M124FailClosed("variance is at or below fail-closed floor")
    if float(np.min(np.linalg.eigvalsh(covariance))) <= VARIANCE_FLOOR:
        raise M124FailClosed("covariance is not safely positive definite")
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    return mean, covariance, sigma, alpha


def univariate_relu_standard_moments(alpha: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    alpha = np.asarray(alpha, dtype=np.float64)
    probability = np.asarray(_cdf(alpha), dtype=np.float64)
    density = np.asarray(_pdf(alpha), dtype=np.float64)
    mean = density + alpha * probability
    second = (1.0 + alpha * alpha) * probability + alpha * density
    variance = second - mean * mean
    if np.any(~np.isfinite(variance)) or np.any(variance <= VARIANCE_FLOOR):
        raise M124FailClosed("standardised ReLU marginal variance failed")
    return mean, np.sqrt(variance)


def local_vertices(alpha: np.ndarray) -> LocalVertices:
    """Nonzero-mean normal-ordered local vertices in standardised coordinates."""
    alpha = np.asarray(alpha, dtype=np.float64)
    mean, scale = univariate_relu_standard_moments(alpha)
    probability = np.asarray(_cdf(alpha), dtype=np.float64)
    density = np.asarray(_pdf(alpha), dtype=np.float64)
    b1 = probability / scale
    b2 = density / (2.0 * scale)
    b3 = -alpha * density / (6.0 * scale)
    if np.any(np.abs(b1) <= 1.0e-10):
        raise M124FailClosed("first Hermite coefficient is too small")
    gamma2 = 2.0 * b2 / (b1 * b1)
    gamma3 = 6.0 * b3 / (b1 * b1 * b1)
    if not np.all(np.isfinite(gamma2)) or not np.all(np.isfinite(gamma3)):
        raise M124FailClosed("non-finite local tree vertex")
    return LocalVertices(alpha, mean, scale, gamma2, gamma3)


def _canonical_paths4() -> tuple[tuple[int, int, int, int], ...]:
    paths = tuple(path for path in itertools.permutations(range(4)) if path <= path[::-1])
    if len(paths) != 12:
        raise AssertionError("expected twelve undirected labelled paths")
    return paths


PATHS4 = _canonical_paths4()


def weighted_tree3(bridge: np.ndarray, gamma2: np.ndarray) -> np.ndarray:
    q = np.asarray(bridge, dtype=np.float64)
    g = np.asarray(gamma2, dtype=np.float64)
    first = g[:, None, None] * q[:, :, None] * q[:, None, :]
    return first + first.transpose(1, 0, 2) + first.transpose(1, 2, 0)


def weighted_tree4(bridge: np.ndarray, gamma2: np.ndarray, gamma3: np.ndarray) -> np.ndarray:
    q = np.asarray(bridge, dtype=np.float64)
    g2 = np.asarray(gamma2, dtype=np.float64)
    g3 = np.asarray(gamma3, dtype=np.float64)
    n = q.shape[0]
    answer = np.zeros((n, n, n, n), dtype=np.float64)
    path_base = np.einsum("ab,bc,cd,b,c->abcd", q, q, q, g2, g2, optimize=True)
    for path in PATHS4:
        answer += np.transpose(path_base, np.argsort(path))
    star_base = np.einsum("a,ab,ac,ad->abcd", g3, q, q, q, optimize=True)
    # Put the star centre in each of the four canonical slots.
    answer += star_base
    answer += star_base.transpose(1, 0, 2, 3)
    answer += star_base.transpose(1, 2, 0, 3)
    answer += star_base.transpose(1, 2, 3, 0)
    return answer


def _tree3_entry(q: np.ndarray, g: np.ndarray, i: int, j: int, k: int) -> float:
    return float(
        g[i] * q[i, j] * q[i, k]
        + g[j] * q[j, i] * q[j, k]
        + g[k] * q[k, i] * q[k, j]
    )


def _tree4_entry(
    q: np.ndarray, g2: np.ndarray, g3: np.ndarray, indices: tuple[int, int, int, int]
) -> float:
    value = 0.0
    for path in PATHS4:
        a, b, c, d = (indices[position] for position in path)
        value += q[a, b] * q[b, c] * q[c, d] * g2[b] * g2[c]
    for centre in range(4):
        root = indices[centre]
        value += g3[root] * math.prod(q[root, indices[position]] for position in range(4) if position != centre)
    return float(value)


def weighted_tree3_mode_gram(bridge: np.ndarray, gamma2: np.ndarray) -> np.ndarray:
    """Exact O(n^3) mode-1 Gram for the weighted nonzero-mean k3 tree."""
    q = np.asarray(bridge, dtype=np.float64)
    g = np.asarray(gamma2, dtype=np.float64)
    r = q @ q
    h = q * q
    row_sq = h.sum(axis=1)
    f = (q * r) @ (g[:, None] * q)
    dg_f = g[:, None] * f
    qdiagq = (q * (g * g * row_sq)[None, :]) @ q
    hg = (g[:, None] * h) * g[None, :]
    cross_middle = (q @ hg) @ q
    return (
        np.outer(g, g) * (r * r)
        + 2.0 * qdiagq
        + 2.0 * cross_middle
        + 2.0 * (dg_f + dg_f.T)
    )


def _set_partitions(items: tuple[int, ...]):
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in _set_partitions(rest):
        yield ((first,),) + partition
        for position in range(len(partition)):
            yield partition[:position] + (partition[position] + (first,),) + partition[position + 1 :]


def _univariate_raw_positive_moment(alpha: float, order: int) -> float:
    """Exact E[(G+alpha)_+^order] for order<=4 by truncated-normal recurrence."""
    if order == 0:
        return 1.0
    density = float(_pdf(alpha))
    integrals = [float(_cdf(alpha)), density]
    cutoff = -alpha
    for power in range(2, order + 1):
        integrals.append((cutoff ** (power - 1)) * density + (power - 1) * integrals[power - 2])
    return sum(math.comb(order, k) * (alpha ** (order - k)) * integrals[k] for k in range(order + 1))


def univariate_standard_cumulant(alpha: float, order: int) -> float:
    mean, scale = univariate_relu_standard_moments(np.asarray([alpha]))
    raw = [_univariate_raw_positive_moment(alpha, power) for power in range(order + 1)]
    mu = float(mean[0])
    sd = float(scale[0])
    central = sum(math.comb(order, k) * ((-mu) ** (order - k)) * raw[k] for k in range(order + 1))
    standard_moment = central / (sd**order)
    return standard_moment if order == 3 else standard_moment - 3.0


def _hermite_probabilist(order: int, x: float) -> float:
    if order == 0:
        return 1.0
    if order == 1:
        return x
    previous, current = 1.0, x
    for degree in range(1, order):
        previous, current = current, x * current - degree * previous
    return current


def _phi_derivative(order: int, x: float) -> float:
    return ((-1.0) ** order) * _hermite_probabilist(order, x) * float(_pdf(x))


def _cdf_derivative(order: int, x: float) -> float:
    if order == 0:
        return float(_cdf(x))
    return _phi_derivative(order - 1, x)


def _quadrant_argument_derivative(alpha: float, beta: float, rho: float, p: int, q: int) -> float:
    """Closed D_alpha^p D_beta^q Phi2(alpha,beta;rho), p+q<=4."""
    if p == 0 and q == 0:
        try:
            return quadrant_probability(alpha, beta, rho).value
        except AnalyticReferenceFailClosed as exc:
            raise M124FailClosed(str(exc)) from exc
    root = math.sqrt(1.0 - rho * rho)
    if p > 0:
        # One alpha derivative gives phi(alpha) Phi(h); differentiate the
        # remaining affine h=(beta-rho alpha)/root by Leibniz.
        remaining_alpha = p - 1
        h = (beta - rho * alpha) / root
        h_alpha, h_beta = -rho / root, 1.0 / root
        total = 0.0
        for on_density in range(remaining_alpha + 1):
            on_cdf_alpha = remaining_alpha - on_density
            total_order = on_cdf_alpha + q
            total += (
                math.comb(remaining_alpha, on_density)
                * _phi_derivative(on_density, alpha)
                * _cdf_derivative(total_order, h)
                * (h_alpha**on_cdf_alpha)
                * (h_beta**q)
            )
        return total
    # Symmetric beta boundary formula when p=0 and q>0.
    remaining_beta = q - 1
    h = (alpha - rho * beta) / root
    h_beta, h_alpha = -rho / root, 1.0 / root
    total = 0.0
    for on_density in range(remaining_beta + 1):
        on_cdf_beta = remaining_beta - on_density
        total += (
            math.comb(remaining_beta, on_density)
            * _phi_derivative(on_density, beta)
            * _cdf_derivative(on_cdf_beta, h)
            * (h_beta**on_cdf_beta)
            * (h_alpha**p)
        )
    return total


def _poly_add(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left + right


def _poly_mul(left: np.ndarray, right: np.ndarray, degree: int = MAX_COLLISION_ORDER) -> np.ndarray:
    answer = np.zeros_like(left)
    for i in range(degree + 1):
        for j in range(degree + 1 - i):
            if left[i, j] == 0.0:
                continue
            for k in range(degree + 1 - i):
                for ell in range(degree + 1 - i - k):
                    if j + ell > degree - i - k or right[k, ell] == 0.0:
                        continue
                    answer[i + k, j + ell] += left[i, j] * right[k, ell]
    return answer


def _poly_power(base: np.ndarray, exponent: int) -> np.ndarray:
    answer = np.zeros_like(base)
    answer[0, 0] = 1.0
    for _ in range(exponent):
        answer = _poly_mul(answer, base)
    return answer


def _poly_exp_zero_constant(base: np.ndarray) -> np.ndarray:
    answer = np.zeros_like(base)
    answer[0, 0] = 1.0
    power = np.array(answer, copy=True)
    for order in range(1, MAX_COLLISION_ORDER + 1):
        power = _poly_mul(power, base)
        answer += power / math.factorial(order)
    return answer


def bivariate_positive_moments(alpha: float, beta: float, rho: float) -> np.ndarray:
    """All E[(G1+a)_+^p (G2+b)_+^q], p+q<=4, by an analytic jet.

    The sole non-elementary scalar is the already-certified bivariate quadrant
    probability.  All higher derivatives use closed Gaussian boundary terms;
    there is no tensor-product quadrature or hidden O(nodes^2) source cost.
    """
    if abs(rho) >= 1.0 - CORRELATION_MARGIN:
        raise M124FailClosed("pair collision is too close to a singular endpoint")
    shape = (MAX_COLLISION_ORDER + 1, MAX_COLLISION_ORDER + 1)
    da = np.zeros(shape, dtype=np.float64)
    db = np.zeros(shape, dtype=np.float64)
    da[1, 0], da[0, 1] = 1.0, rho
    db[1, 0], db[0, 1] = rho, 1.0
    quadrant_jet = np.zeros(shape, dtype=np.float64)
    for p in range(MAX_COLLISION_ORDER + 1):
        for q in range(MAX_COLLISION_ORDER + 1 - p):
            derivative = _quadrant_argument_derivative(alpha, beta, rho, p, q)
            term = _poly_mul(_poly_power(da, p), _poly_power(db, q))
            quadrant_jet += derivative * term / (math.factorial(p) * math.factorial(q))

    exponent = np.zeros(shape, dtype=np.float64)
    exponent[1, 0] = alpha
    exponent[0, 1] = beta
    exponent[2, 0] = 0.5
    exponent[1, 1] = rho
    exponent[0, 2] = 0.5
    mgf = _poly_mul(_poly_exp_zero_constant(exponent), quadrant_jet)
    moments = np.zeros(shape, dtype=np.float64)
    for p in range(MAX_COLLISION_ORDER + 1):
        for q in range(MAX_COLLISION_ORDER + 1 - p):
            moments[p, q] = mgf[p, q] * math.factorial(p) * math.factorial(q)
    # The quadrant MGF carries the *other* positivity indicator even when one
    # exponent is zero.  Cumulant partitions instead require ordinary
    # one-variable moments for singleton-coordinate blocks, so repair both
    # axes analytically.  Interior entries p,q>=1 remain the joint positive
    # moments generated by the quadrant MGF.
    moments[0, 0] = 1.0
    for p in range(1, MAX_COLLISION_ORDER + 1):
        moments[p, 0] = _univariate_raw_positive_moment(alpha, p)
        moments[0, p] = _univariate_raw_positive_moment(beta, p)
    return moments


def pair_standard_cumulant(alpha_i: float, alpha_j: float, rho: float, labels: tuple[int, ...]) -> float:
    """Analytic standardised bivariate cumulant through total order four."""
    moments = bivariate_positive_moments(alpha_i, alpha_j, rho)
    total = 0.0
    for partition in _set_partitions(tuple(range(len(labels)))):
        coefficient = math.factorial(len(partition) - 1) * ((-1) ** (len(partition) - 1))
        product = 1.0
        for block in partition:
            count_left = sum(labels[index] == 0 for index in block)
            count_right = len(block) - count_left
            product *= moments[count_left, count_right]
        total += coefficient * product
    _, scales = univariate_relu_standard_moments(np.asarray([alpha_i, alpha_j]))
    count_left = labels.count(0)
    count_right = len(labels) - count_left
    answer = total / (float(scales[0]) ** count_left * float(scales[1]) ** count_right)
    if not math.isfinite(answer):
        raise M124FailClosed("non-finite pair collision cumulant")
    return answer


def collision_corrections(
    alpha: np.ndarray,
    input_correlation: np.ndarray,
    bridge: np.ndarray,
    gamma2: np.ndarray,
    gamma3: np.ndarray,
) -> CollisionCorrections:
    """Build the O(n^2) exact collision source used by implicit target algebra."""
    n = alpha.size
    diagonal3 = np.empty(n, dtype=np.float64)
    majority3 = np.zeros((n, n), dtype=np.float64)
    diagonal4 = np.empty(n, dtype=np.float64)
    majority4 = np.zeros((n, n), dtype=np.float64)
    paired4 = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        diagonal3[i] = univariate_standard_cumulant(float(alpha[i]), 3) - _tree3_entry(
            bridge, gamma2, i, i, i
        )
        diagonal4[i] = univariate_standard_cumulant(float(alpha[i]), 4) - _tree4_entry(
            bridge, gamma2, gamma3, (i, i, i, i)
        )
        for j in range(i + 1, n):
            rho = float(input_correlation[i, j])
            exact_iij = pair_standard_cumulant(float(alpha[i]), float(alpha[j]), rho, (0, 0, 1))
            exact_ijj = pair_standard_cumulant(float(alpha[i]), float(alpha[j]), rho, (0, 1, 1))
            majority3[i, j] = exact_iij - _tree3_entry(bridge, gamma2, i, i, j)
            majority3[j, i] = exact_ijj - _tree3_entry(bridge, gamma2, i, j, j)

            exact_iiij = pair_standard_cumulant(float(alpha[i]), float(alpha[j]), rho, (0, 0, 0, 1))
            exact_ijjj = pair_standard_cumulant(float(alpha[i]), float(alpha[j]), rho, (0, 1, 1, 1))
            exact_iijj = pair_standard_cumulant(float(alpha[i]), float(alpha[j]), rho, (0, 0, 1, 1))
            majority4[i, j] = exact_iiij - _tree4_entry(bridge, gamma2, gamma3, (i, i, i, j))
            majority4[j, i] = exact_ijjj - _tree4_entry(bridge, gamma2, gamma3, (i, j, j, j))
            pair_delta = exact_iijj - _tree4_entry(bridge, gamma2, gamma3, (i, i, j, j))
            paired4[i, j] = paired4[j, i] = pair_delta
    return CollisionCorrections(diagonal3, majority3, diagonal4, majority4, paired4)


def collision3_mode_gram_terms(
    bridge: np.ndarray, gamma2: np.ndarray, corrections: CollisionCorrections
) -> tuple[np.ndarray, np.ndarray]:
    """Return T_(1)D_(1)^T and D_(1)D_(1)^T without forming D."""
    q, g = bridge, gamma2
    d, e = corrections.diagonal3, corrections.majority3
    n = q.shape[0]
    cross = np.empty((n, n), dtype=np.float64)
    for a in range(n):
        for b in range(n):
            value = d[b] * _tree3_entry(q, g, a, b, b)
            for t in range(n):
                if t != b:
                    value += 2.0 * e[b, t] * _tree3_entry(q, g, a, b, t)
                    value += e[t, b] * _tree3_entry(q, g, a, t, t)
            cross[a, b] = value

    defect_gram = e.T @ e
    for a in range(n):
        defect_gram[a, a] += d[a] * d[a] + 2.0 * float(e[a] @ e[a])
        for b in range(a + 1, n):
            extra = d[a] * e[a, b] + d[b] * e[b, a] + 2.0 * e[a, b] * e[b, a]
            defect_gram[a, b] += extra
            defect_gram[b, a] += extra
    return cross, defect_gram


def _replace_collisions(tensor: np.ndarray, alpha: np.ndarray, correlation: np.ndarray) -> np.ndarray:
    order = tensor.ndim
    answer = np.array(tensor, copy=True)
    cache: dict[tuple[object, ...], float] = {}
    for index in np.ndindex(*tensor.shape):
        unique = tuple(sorted(set(index)))
        if len(unique) == 1:
            key = ("u", unique[0], order)
            if key not in cache:
                cache[key] = univariate_standard_cumulant(float(alpha[unique[0]]), order)
            answer[index] = cache[key]
        elif len(unique) == 2:
            left, right = unique
            labels = tuple(0 if item == left else 1 for item in index)
            # Cumulants are slot symmetric, so multiplicity is the cache key.
            count_left = labels.count(0)
            key = ("b", left, right, order, count_left)
            if key not in cache:
                canonical = tuple([0] * count_left + [1] * (order - count_left))
                cache[key] = pair_standard_cumulant(
                    float(alpha[left]), float(alpha[right]), float(correlation[left, right]), canonical
                )
            answer[index] = cache[key]
    return answer


def build_nonzero_bridge_source(mean: np.ndarray, covariance: np.ndarray) -> NonzeroBridgeSource:
    mean, covariance, sigma, alpha = _validate_gaussian(mean, covariance)
    vertices = local_vertices(alpha)
    try:
        activation_mean, activation_covariance = analytic_relu_gaussian_moments(mean, covariance)
    except AnalyticReferenceFailClosed as exc:
        raise M124FailClosed(str(exc)) from exc
    activation_covariance = 0.5 * (activation_covariance + activation_covariance.T)
    activation_scale = np.sqrt(np.diag(activation_covariance))
    if np.any(activation_scale <= VARIANCE_FLOOR):
        raise M124FailClosed("activation variance failed")
    bridge = activation_covariance / np.outer(activation_scale, activation_scale)
    np.fill_diagonal(bridge, 1.0)
    correlation = covariance / np.outer(sigma, sigma)
    if np.any(np.abs(correlation - np.eye(mean.size)) >= 1.0 - CORRELATION_MARGIN):
        raise M124FailClosed("input correlation too close to singular endpoint")
    tree3 = weighted_tree3(bridge, vertices.gamma2)
    tree4 = weighted_tree4(bridge, vertices.gamma2, vertices.gamma3)
    collisions = collision_corrections(alpha, correlation, bridge, vertices.gamma2, vertices.gamma3)
    source3 = _replace_collisions(tree3, alpha, correlation)
    source4 = _replace_collisions(tree4, alpha, correlation)
    return NonzeroBridgeSource(
        activation_mean,
        activation_covariance,
        activation_scale,
        bridge,
        vertices,
        collisions,
        source3,
        source4,
        tree3,
        tree4,
    )


def _mode_gram(tensor: np.ndarray) -> np.ndarray:
    unfolding = tensor.reshape(tensor.shape[0], -1)
    return unfolding @ unfolding.T


def shared_projector(source: NonzeroBridgeSource, rank: int = RANK) -> SharedProjector:
    """Rank-four standardised projector from weighted k3 plus exact collisions."""
    n = source.bridge.shape[0]
    if rank != RANK or n <= rank:
        raise ValueError("M124 freezes rank four and needs n>4")
    tree_gram = weighted_tree3_mode_gram(source.bridge, source.vertices.gamma2)
    cross, defect_gram = collision3_mode_gram_terms(
        source.bridge, source.vertices.gamma2, source.collisions
    )
    gram = tree_gram + cross + cross.T + defect_gram
    gram = 0.5 * (gram + gram.T)
    values, vectors = np.linalg.eigh(gram)
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    scale = max(float(values[0]), 1.0)
    gap = float(values[rank - 1] - values[rank])
    if values[rank - 1] <= 0.0 or gap <= BOUNDARY_GAP_RELATIVE * scale:
        raise M124FailClosed("rank-4/5 eigengap is absent or numerically unsafe")
    factor = vectors[:, :rank]
    return SharedProjector(factor, values, gap, gram)


def _project_dense(tensor: np.ndarray, factor: np.ndarray) -> np.ndarray:
    order = tensor.ndim
    if order == 3:
        return np.einsum("ijk,ip,jq,kr->pqr", tensor, factor, factor, factor, optimize=True)
    if order == 4:
        return np.einsum("ijkl,ip,jq,kr,ls->pqrs", tensor, factor, factor, factor, factor, optimize=True)
    raise ValueError("only order three/four")


def _outer_vectors(vectors: list[np.ndarray]) -> np.ndarray:
    answer = np.asarray(vectors[0], dtype=np.float64)
    for vector in vectors[1:]:
        answer = np.multiply.outer(answer, vector)
    return answer


def projected_collision_core3(corrections: CollisionCorrections, factor: np.ndarray) -> np.ndarray:
    """Exact rank-r collision core in O(n^2 r^3), with O(n^2) source storage."""
    u = np.asarray(factor, dtype=np.float64)
    n, r = u.shape
    core = np.zeros((r, r, r), dtype=np.float64)
    for i in range(n):
        core += corrections.diagonal3[i] * _outer_vectors([u[i], u[i], u[i]])
        for j in range(n):
            if i == j:
                continue
            for singleton_slot in range(3):
                vectors = [u[i], u[i], u[i]]
                vectors[singleton_slot] = u[j]
                core += corrections.majority3[i, j] * _outer_vectors(vectors)
    return core


def projected_collision_core4(corrections: CollisionCorrections, factor: np.ndarray) -> np.ndarray:
    """Exact rank-r order-four collision core; no n^4 tensor or G4."""
    u = np.asarray(factor, dtype=np.float64)
    n, r = u.shape
    core = np.zeros((r, r, r, r), dtype=np.float64)
    for i in range(n):
        core += corrections.diagonal4[i] * _outer_vectors([u[i], u[i], u[i], u[i]])
        for j in range(n):
            if i == j:
                continue
            for singleton_slot in range(4):
                vectors = [u[i], u[i], u[i], u[i]]
                vectors[singleton_slot] = u[j]
                core += corrections.majority4[i, j] * _outer_vectors(vectors)
        for j in range(i + 1, n):
            for left_slots in itertools.combinations(range(4), 2):
                vectors = [u[j], u[j], u[j], u[j]]
                for slot in left_slots:
                    vectors[slot] = u[i]
                core += corrections.paired4[i, j] * _outer_vectors(vectors)
    return core


def projected_core3(source: NonzeroBridgeSource, factor: np.ndarray) -> np.ndarray:
    q, g, u = source.bridge, source.vertices.gamma2, np.asarray(factor, dtype=np.float64)
    qu = q @ u
    core = (
        np.einsum("i,ip,iq,ir->pqr", g, u, qu, qu, optimize=True)
        + np.einsum("i,ip,iq,ir->pqr", g, qu, u, qu, optimize=True)
        + np.einsum("i,ip,iq,ir->pqr", g, qu, qu, u, optimize=True)
    )
    return core + projected_collision_core3(source.collisions, u)


def projected_core4(source: NonzeroBridgeSource, factor: np.ndarray) -> np.ndarray:
    q = source.bridge
    g2 = source.vertices.gamma2
    g3 = source.vertices.gamma3
    u = np.asarray(factor, dtype=np.float64)
    r = u.shape[1]
    core = np.zeros((r, r, r, r), dtype=np.float64)
    for output in itertools.product(range(r), repeat=4):
        vectors = [u[:, index] for index in output]
        value = 0.0
        for path in PATHS4:
            a, b, c, d = (vectors[position] for position in path)
            scratch = q @ d
            scratch *= g2 * c
            scratch = q @ scratch
            scratch *= g2 * b
            scratch = q @ scratch
            value += float(a @ scratch)
        core[output] = value
    qu = q @ u
    core += np.einsum("i,ip,iq,ir,is->pqrs", g3, u, qu, qu, qu, optimize=True)
    core += np.einsum("i,ip,iq,ir,is->pqrs", g3, qu, u, qu, qu, optimize=True)
    core += np.einsum("i,ip,iq,ir,is->pqrs", g3, qu, qu, u, qu, optimize=True)
    core += np.einsum("i,ip,iq,ir,is->pqrs", g3, qu, qu, qu, u, optimize=True)
    return core + projected_collision_core4(source.collisions, u)


def project_source(source: NonzeroBridgeSource, projector: SharedProjector) -> ProjectedSource:
    u = projector.factor_standard
    physical = source.activation_scale[:, None] * u
    return ProjectedSource(u, physical, projected_core3(source, u), projected_core4(source, u))


def reconstruct(core: np.ndarray, factor: np.ndarray) -> np.ndarray:
    if core.ndim == 3:
        return np.einsum("pqr,ip,jq,kr->ijk", core, factor, factor, factor, optimize=True)
    if core.ndim == 4:
        return np.einsum("pqrs,ip,jq,kr,ls->ijkl", core, factor, factor, factor, factor, optimize=True)
    raise ValueError("only order three/four")


def transport_dense(tensor: np.ndarray, weight: np.ndarray) -> np.ndarray:
    if tensor.ndim == 3:
        return np.einsum("ijk,ia,jb,kc->abc", tensor, weight, weight, weight, optimize=True)
    if tensor.ndim == 4:
        return np.einsum("ijkl,ia,jb,kc,ld->abcd", tensor, weight, weight, weight, weight, optimize=True)
    raise ValueError("only order three/four")


def transport_projected(projected: ProjectedSource, weight: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = np.asarray(weight, dtype=np.float64).T @ projected.factor_physical
    t3 = np.einsum("pqr,ap,bq,cr->abc", projected.core3, f, f, f, optimize=True)
    t4 = np.einsum("pqrs,ap,bq,cr,ds->abcd", projected.core4, f, f, f, f, optimize=True)
    return t3, t4


def physical_source(source: NonzeroBridgeSource, order: int) -> np.ndarray:
    scale = source.activation_scale
    if order == 3:
        return source.standard_k3 * np.einsum("i,j,k->ijk", scale, scale, scale)
    if order == 4:
        return source.standard_k4 * np.einsum("i,j,k,l->ijkl", scale, scale, scale, scale)
    raise ValueError("only order three/four")


def _relu_mean_vector(mean: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    sigma = np.sqrt(np.diag(covariance))
    alpha = mean / sigma
    return sigma * np.asarray(_pdf(alpha)) + mean * np.asarray(_cdf(alpha))


def edgeworth_delay_one(mean: np.ndarray, covariance: np.ndarray, t3: np.ndarray, t4: np.ndarray) -> EdgeworthDefect:
    """M121 first-order k3/k4 conversion with exact slot multiplicities."""
    mean, covariance, sigma, alpha = _validate_gaussian(mean, covariance)
    n = mean.size
    density_standard = np.asarray(_pdf(alpha), dtype=np.float64)
    density_zero = density_standard / sigma
    variance = sigma * sigma
    density_prime = (mean / variance) * density_zero
    density_second = ((mean * mean / (variance * variance)) - 1.0 / variance) * density_zero
    relu_mean = _relu_mean_vector(mean, covariance)
    delta_mean = np.empty(n, dtype=np.float64)
    delta_raw = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        delta_mean[i] = -(t3[i, i, i] / 6.0) * density_prime[i] + (t4[i, i, i, i] / 24.0) * density_second[i]
        delta_raw[i, i] = (t3[i, i, i] / 3.0) * density_zero[i] - (t4[i, i, i, i] / 12.0) * density_prime[i]
        for j in range(i + 1, n):
            cij = covariance[i, j]
            rho = cij / (sigma[i] * sigma[j])
            if abs(rho) >= 1.0 - CORRELATION_MARGIN:
                raise M124FailClosed("delay-one response reached singular correlation")
            conditional_variance_j = variance[j] - cij * cij / variance[i]
            conditional_mean_j = mean[j] - cij * mean[i] / variance[i]
            conditional_sigma_j = math.sqrt(conditional_variance_j)
            conditional_alpha_j = conditional_mean_j / conditional_sigma_j
            conditional_probability_j = float(_cdf(conditional_alpha_j))
            conditional_relu_j = conditional_sigma_j * float(_pdf(conditional_alpha_j)) + conditional_mean_j * conditional_probability_j
            beta_j = cij / variance[i]

            conditional_variance_i = variance[i] - cij * cij / variance[j]
            conditional_mean_i = mean[i] - cij * mean[j] / variance[j]
            conditional_sigma_i = math.sqrt(conditional_variance_i)
            conditional_alpha_i = conditional_mean_i / conditional_sigma_i
            conditional_probability_i = float(_cdf(conditional_alpha_i))
            conditional_relu_i = conditional_sigma_i * float(_pdf(conditional_alpha_i)) + conditional_mean_i * conditional_probability_i
            beta_i = cij / variance[j]

            d30 = -(density_prime[i] * conditional_relu_j + density_zero[i] * beta_j * conditional_probability_j)
            d21 = density_zero[i] * conditional_probability_j
            d12 = density_zero[j] * conditional_probability_i
            d03 = -(density_prime[j] * conditional_relu_i + density_zero[j] * beta_i * conditional_probability_i)
            d40 = (
                density_second[i] * conditional_relu_j
                + 2.0 * density_prime[i] * beta_j * conditional_probability_j
                + density_zero[i] * beta_j * beta_j * float(_pdf(conditional_alpha_j)) / conditional_sigma_j
            )
            d31 = -(
                density_prime[i] * conditional_probability_j
                + density_zero[i] * beta_j * float(_pdf(conditional_alpha_j)) / conditional_sigma_j
            )
            d04 = (
                density_second[j] * conditional_relu_i
                + 2.0 * density_prime[j] * beta_i * conditional_probability_i
                + density_zero[j] * beta_i * beta_i * float(_pdf(conditional_alpha_i)) / conditional_sigma_i
            )
            d13 = -(
                density_prime[j] * conditional_probability_i
                + density_zero[j] * beta_i * float(_pdf(conditional_alpha_i)) / conditional_sigma_i
            )
            determinant = variance[i] * variance[j] - cij * cij
            exponent = -0.5 * (
                variance[j] * mean[i] * mean[i]
                - 2.0 * cij * mean[i] * mean[j]
                + variance[i] * mean[j] * mean[j]
            ) / determinant
            d22 = math.exp(exponent) / (2.0 * math.pi * math.sqrt(determinant))
            value = (
                t3[i, i, i] * d30
                + 3.0 * t3[i, i, j] * d21
                + 3.0 * t3[i, j, j] * d12
                + t3[j, j, j] * d03
            ) / 6.0
            value += (
                t4[i, i, i, i] * d40
                + 4.0 * t4[i, i, i, j] * d31
                + 6.0 * t4[i, i, j, j] * d22
                + 4.0 * t4[i, j, j, j] * d13
                + t4[j, j, j, j] * d04
            ) / 24.0
            delta_raw[i, j] = delta_raw[j, i] = value
    delta_covariance = delta_raw - np.outer(delta_mean, relu_mean) - np.outer(relu_mean, delta_mean)
    return EdgeworthDefect(delta_mean, 0.5 * (delta_covariance + delta_covariance.T))


def combined_source_fidelity(source: NonzeroBridgeSource, projected: ProjectedSource) -> float:
    approximate3 = reconstruct(projected.core3, projected.factor_standard)
    approximate4 = reconstruct(projected.core4, projected.factor_standard)
    error2 = float(np.sum((source.standard_k3 - approximate3) ** 2) + np.sum((source.standard_k4 - approximate4) ** 2))
    norm2 = float(np.sum(source.standard_k3**2) + np.sum(source.standard_k4**2))
    return 1.0 - math.sqrt(error2 / max(norm2, 1.0e-300))


def source_fidelity(source: NonzeroBridgeSource, projected: ProjectedSource, order: int) -> float:
    if order == 3:
        exact = source.standard_k3
        approximate = reconstruct(projected.core3, projected.factor_standard)
    elif order == 4:
        exact = source.standard_k4
        approximate = reconstruct(projected.core4, projected.factor_standard)
    else:
        raise ValueError("only order three/four")
    error2 = float(np.sum((exact - approximate) ** 2))
    norm2 = float(np.sum(exact * exact))
    return 1.0 - math.sqrt(error2 / max(norm2, 1.0e-300))


def repeated_output_k4_relative(reference: np.ndarray, approximation: np.ndarray) -> float:
    """Relative error on aaaa/aaab/aabb/abbb entries used by pair responses."""
    if reference.ndim != 4 or approximation.shape != reference.shape:
        raise ValueError("order-four tensor shape mismatch")
    n = reference.shape[0]
    error2 = 0.0
    norm2 = 0.0
    for i in range(n):
        error2 += float((reference[i, i, i, i] - approximation[i, i, i, i]) ** 2)
        norm2 += float(reference[i, i, i, i] ** 2)
        for j in range(i + 1, n):
            for index, multiplicity in (((i, i, i, j), 4), ((i, i, j, j), 6), ((i, j, j, j), 4)):
                error2 += multiplicity * float((reference[index] - approximation[index]) ** 2)
                norm2 += multiplicity * float(reference[index] ** 2)
    return math.sqrt(error2 / max(norm2, 1.0e-300))


def correction_ratio(reference: EdgeworthDefect, approximation: EdgeworthDefect) -> float:
    error2 = float(
        np.sum((reference.mean - approximation.mean) ** 2)
        + np.sum((reference.covariance - approximation.covariance) ** 2)
    )
    norm2 = float(np.sum(reference.mean**2) + np.sum(reference.covariance**2))
    return math.sqrt(error2 / max(norm2, 1.0e-300))
