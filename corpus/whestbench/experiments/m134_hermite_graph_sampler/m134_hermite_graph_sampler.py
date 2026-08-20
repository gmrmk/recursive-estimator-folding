"""Generated-only oracle for M134's Hermite graph-degree sampler.

The module never reads contest data.  It exposes the exact finite Hermite
graph algebra for the three-label ``[2,1,1]`` collision, its finite tree
control, the one-GEMM masked-triangle contraction, and the corresponding
Rademacher repeated-output probe.

The finite ``terms`` parameter is a correctness oracle.  It is deliberately
not presented as an exact target algorithm: the trivariate graph series can
diverge in the high-correlation regime.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from pathlib import Path
import sys
from typing import Iterable, Sequence

import numpy as np


_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "m122_nonzero_bridge_theory"))
sys.path.insert(0, str(_ROOT / "m129_source_frechet_tangent"))

from m122_nonzero_bridge import (  # noqa: E402
    NonzeroMeanBridgeState,
    power_hermite_coefficient,
    tree_tensor_continuation,
)
from m129_source_frechet import (  # noqa: E402
    BridgeStateFrechet,
    power_hermite_coefficient_dot,
)


@dataclass(frozen=True)
class GraphFactor:
    """One oriented triangle factor.

    Its dense value is

    ``row[i] left[j] right[k] H_r[i,j] H_s[i,k] H_t[j,k]``

    with every ``H`` hollow.  Summing the oriented Hermite factors restores
    singleton symmetry.  Tree factors carry a negative row and therefore
    implement exact-minus-tree ownership without a separate subtraction.
    """

    name: str
    edge: np.ndarray
    powers: tuple[int, int, int]
    row: np.ndarray
    left: np.ndarray
    right: np.ndarray


@dataclass(frozen=True)
class GraphFactorDual:
    value: GraphFactor
    edge_dot: np.ndarray
    row_dot: np.ndarray
    left_dot: np.ndarray
    right_dot: np.ndarray


def _hollow_power(edge: np.ndarray, degree: int) -> np.ndarray:
    if degree < 0:
        raise ValueError("edge degree must be nonnegative")
    edge = np.asarray(edge, dtype=np.float64)
    answer = np.ones_like(edge) if degree == 0 else edge**degree
    answer = answer.copy()
    np.fill_diagonal(answer, 0.0)
    return answer


def _hollow_power_dot(edge: np.ndarray, edge_dot: np.ndarray, degree: int) -> np.ndarray:
    edge = np.asarray(edge, dtype=np.float64)
    edge_dot = np.asarray(edge_dot, dtype=np.float64)
    if degree == 0:
        answer = np.zeros_like(edge)
    else:
        answer = degree * edge ** (degree - 1) * edge_dot
    answer = answer.copy()
    np.fill_diagonal(answer, 0.0)
    return answer


def local_centered_coefficients(
    alpha: np.ndarray, sigma: np.ndarray, terms: int
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``c[d]=E[(Y-EY)He_d]`` and ``b[d]=E[(Y-EY)^2 He_d]``."""

    alpha = np.asarray(alpha, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    if alpha.shape != sigma.shape or terms < 2 or np.any(sigma <= 0.0):
        raise ValueError("invalid local coefficient request")
    n = alpha.size
    raw1 = np.empty((terms, n), dtype=np.float64)
    raw2 = np.empty((terms, n), dtype=np.float64)
    for degree in range(terms):
        for node in range(n):
            raw1[degree, node] = power_hermite_coefficient(
                float(alpha[node]), float(sigma[node]), 1, degree
            )
            raw2[degree, node] = power_hermite_coefficient(
                float(alpha[node]), float(sigma[node]), 2, degree
            )
    mean = raw1[0]
    centered = raw1.copy()
    centered[0] = 0.0
    squared = raw2 - 2.0 * mean[None, :] * raw1
    squared[0] += mean**2
    return centered, squared


def local_centered_coefficients_dual(
    alpha: np.ndarray,
    sigma: np.ndarray,
    alpha_dot: np.ndarray,
    sigma_dot: np.ndarray,
    terms: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Value/tangent counterpart of :func:`local_centered_coefficients`."""

    alpha = np.asarray(alpha, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    alpha_dot = np.asarray(alpha_dot, dtype=np.float64)
    sigma_dot = np.asarray(sigma_dot, dtype=np.float64)
    if not (alpha.shape == sigma.shape == alpha_dot.shape == sigma_dot.shape):
        raise ValueError("dual local coefficient shape mismatch")
    n = alpha.size
    raw1 = np.empty((terms, n), dtype=np.float64)
    raw2 = np.empty((terms, n), dtype=np.float64)
    raw1_dot = np.empty((terms, n), dtype=np.float64)
    raw2_dot = np.empty((terms, n), dtype=np.float64)
    for degree in range(terms):
        for node in range(n):
            raw1[degree, node], raw1_dot[degree, node] = power_hermite_coefficient_dot(
                float(alpha[node]),
                float(sigma[node]),
                1,
                degree,
                float(alpha_dot[node]),
                float(sigma_dot[node]),
            )
            raw2[degree, node], raw2_dot[degree, node] = power_hermite_coefficient_dot(
                float(alpha[node]),
                float(sigma[node]),
                2,
                degree,
                float(alpha_dot[node]),
                float(sigma_dot[node]),
            )
    mean, mean_dot = raw1[0], raw1_dot[0]
    centered, centered_dot = raw1.copy(), raw1_dot.copy()
    centered[0] = 0.0
    centered_dot[0] = 0.0
    squared = raw2 - 2.0 * mean[None, :] * raw1
    squared[0] += mean**2
    squared_dot = raw2_dot - 2.0 * (
        mean_dot[None, :] * raw1 + mean[None, :] * raw1_dot
    )
    squared_dot[0] += 2.0 * mean * mean_dot
    return centered, squared, centered_dot, squared_dot


def admissible_configurations(terms: int) -> list[tuple[int, int, int]]:
    """All M122 tripartite configurations with three local degrees < terms.

    The ``r=s=0`` bank cancels exactly against ``Var_i Cov_jk`` and is removed.
    At ``terms=24`` this returns 3654 configurations; adding the cancelled 24
    gives M129's 3678 raw configurations.
    """

    if terms < 2:
        raise ValueError("terms must be at least two")
    return [
        (r, s, t)
        for r in range(terms)
        for s in range(terms)
        for t in range(terms)
        if r + s < terms
        and r + t < terms
        and s + t < terms
        and not (r == 0 and s == 0)
    ]


def hermite_factors(
    alpha: np.ndarray, sigma: np.ndarray, correlation: np.ndarray, terms: int
) -> list[GraphFactor]:
    """Finite connected-cumulant graph factors for ``kappa(Y_i,Y_i,Y_j,Y_k)``.

    Centralization gives

    ``E[X_i^2 X_j X_k] - Var(X_i)Cov(X_j,X_k) - 2Cov(X_i,X_j)Cov(X_i,X_k)``.

    The first subtraction deletes ``r=s=0``.  For ``t=0`` the second changes
    the repeated-node coefficient from ``b[r+s]`` to
    ``b[r+s]-2*c[r]*c[s]``.  This is exact diagram ownership, not a fitted
    correction.
    """

    correlation = np.asarray(correlation, dtype=np.float64)
    c, b = local_centered_coefficients(alpha, sigma, terms)
    if correlation.shape != (c.shape[1], c.shape[1]):
        raise ValueError("correlation shape mismatch")
    result: list[GraphFactor] = []
    for r, s, t in admissible_configurations(terms):
        row = b[r + s].copy()
        if t == 0:
            row -= 2.0 * c[r] * c[s]
        row /= math.factorial(r) * math.factorial(s) * math.factorial(t)
        left = c[r + t].copy()
        right = c[s + t].copy()
        if not (np.any(row) and np.any(left) and np.any(right)):
            continue
        result.append(
            GraphFactor(
                f"H({r},{s},{t})",
                correlation,
                (r, s, t),
                row,
                left,
                right,
            )
        )
    return result


def hermite_factors_dual(
    alpha: np.ndarray,
    sigma: np.ndarray,
    correlation: np.ndarray,
    alpha_dot: np.ndarray,
    sigma_dot: np.ndarray,
    correlation_dot: np.ndarray,
    terms: int,
) -> list[GraphFactorDual]:
    c, b, cdot, bdot = local_centered_coefficients_dual(
        alpha, sigma, alpha_dot, sigma_dot, terms
    )
    result: list[GraphFactorDual] = []
    for r, s, t in admissible_configurations(terms):
        denominator = math.factorial(r) * math.factorial(s) * math.factorial(t)
        row = b[r + s].copy()
        row_dot = bdot[r + s].copy()
        if t == 0:
            row -= 2.0 * c[r] * c[s]
            row_dot -= 2.0 * (cdot[r] * c[s] + c[r] * cdot[s])
        row /= denominator
        row_dot /= denominator
        left, right = c[r + t].copy(), c[s + t].copy()
        left_dot, right_dot = cdot[r + t].copy(), cdot[s + t].copy()
        if not (np.any(row) and np.any(left) and np.any(right)):
            continue
        factor = GraphFactor(
            f"H({r},{s},{t})",
            np.asarray(correlation, dtype=np.float64),
            (r, s, t),
            row,
            left,
            right,
        )
        result.append(
            GraphFactorDual(
                factor,
                np.asarray(correlation_dot, dtype=np.float64),
                row_dot,
                left_dot,
                right_dot,
            )
        )
    return result


def _tree_factor_specs(
    scale: np.ndarray, gamma2: np.ndarray, gamma3: np.ndarray
) -> list[tuple[str, tuple[int, int, int], np.ndarray, np.ndarray, np.ndarray]]:
    """The three star and six path factors of the continued ``(i,i,j,k)`` tree."""

    s2 = scale**2
    return [
        ("S_i", (1, 1, 0), 2.0 * s2 * gamma3, scale, scale),
        ("S_j", (2, 0, 1), s2, scale * gamma3, scale),
        ("S_k", (0, 2, 1), s2, scale, scale * gamma3),
        ("P_ik_011", (0, 1, 1), 2.0 * s2 * gamma2, scale, scale * gamma2),
        ("P_ij_101", (1, 0, 1), 2.0 * s2 * gamma2, scale * gamma2, scale),
        ("P_ii_110", (1, 1, 0), 2.0 * s2 * gamma2**2, scale, scale),
        ("P_jk_111", (1, 1, 1), 2.0 * s2, scale * gamma2, scale * gamma2),
        ("P_ik_120", (1, 2, 0), 2.0 * s2 * gamma2, scale, scale * gamma2),
        ("P_ij_210", (2, 1, 0), 2.0 * s2 * gamma2, scale * gamma2, scale),
    ]


def negative_tree_factors(state: NonzeroMeanBridgeState) -> list[GraphFactor]:
    """Nine factors whose sum is minus the M122 tree on ``[2,1,1]``."""

    return [
        GraphFactor(name, state.bridge, powers, -row, left, right)
        for name, powers, row, left, right in _tree_factor_specs(
            state.relu_scale, state.gamma2, state.gamma3
        )
    ]


def negative_tree_factors_dual(
    tangent: BridgeStateFrechet,
) -> list[GraphFactorDual]:
    """Frechet tangents of all nine negative tree-control factors."""

    state = tangent.state
    s, sd = state.relu_scale, tangent.relu_scale_dot
    g2, g2d = state.gamma2, tangent.gamma2_dot
    g3, g3d = state.gamma3, tangent.gamma3_dot
    s2, s2d = s**2, 2.0 * s * sd

    def product(x: np.ndarray, xd: np.ndarray, y: np.ndarray, yd: np.ndarray):
        return x * y, xd * y + x * yd

    sg2, sg2d = product(s, sd, g2, g2d)
    sg3, sg3d = product(s, sd, g3, g3d)
    s2g2, s2g2d = product(s2, s2d, g2, g2d)
    s2g3, s2g3d = product(s2, s2d, g3, g3d)
    g2sq, g2sqd = g2**2, 2.0 * g2 * g2d
    s2g2sq, s2g2sqd = product(s2, s2d, g2sq, g2sqd)
    specs = [
        ("S_i", (1, 1, 0), 2 * s2g3, 2 * s2g3d, s, sd, s, sd),
        ("S_j", (2, 0, 1), s2, s2d, sg3, sg3d, s, sd),
        ("S_k", (0, 2, 1), s2, s2d, s, sd, sg3, sg3d),
        ("P_ik_011", (0, 1, 1), 2 * s2g2, 2 * s2g2d, s, sd, sg2, sg2d),
        ("P_ij_101", (1, 0, 1), 2 * s2g2, 2 * s2g2d, sg2, sg2d, s, sd),
        ("P_ii_110", (1, 1, 0), 2 * s2g2sq, 2 * s2g2sqd, s, sd, s, sd),
        ("P_jk_111", (1, 1, 1), 2 * s2, 2 * s2d, sg2, sg2d, sg2, sg2d),
        ("P_ik_120", (1, 2, 0), 2 * s2g2, 2 * s2g2d, s, sd, sg2, sg2d),
        ("P_ij_210", (2, 1, 0), 2 * s2g2, 2 * s2g2d, sg2, sg2d, s, sd),
    ]
    result: list[GraphFactorDual] = []
    for name, powers, row, rowd, left, leftd, right, rightd in specs:
        base = GraphFactor(name, state.bridge, powers, -row, left, right)
        result.append(
            GraphFactorDual(
                base,
                tangent.bridge_dot,
                -rowd,
                leftd,
                rightd,
            )
        )
    return result


def factor_tensor(factor: GraphFactor) -> np.ndarray:
    r, s, t = factor.powers
    hr = _hollow_power(factor.edge, r)
    hs = _hollow_power(factor.edge, s)
    ht = _hollow_power(factor.edge, t)
    value = (
        factor.row[:, None, None]
        * factor.left[None, :, None]
        * factor.right[None, None, :]
        * hr[:, :, None]
        * hs[:, None, :]
        * ht[None, :, :]
    )
    return value


def sum_factor_tensor(factors: Sequence[GraphFactor]) -> np.ndarray:
    if not factors:
        raise ValueError("at least one factor is required")
    answer = np.zeros((factors[0].row.size,) * 3, dtype=np.float64)
    for factor in factors:
        answer += factor_tensor(factor)
    return 0.5 * (answer + answer.swapaxes(1, 2))


def factor_probe_t(factor: GraphFactor, sign: np.ndarray) -> np.ndarray:
    """Contract one factor with ``z_j z_k`` using one square GEMM.

    Algebraically this is ``row * rowsum((U @ H_t) * V)`` with
    ``U=H_r*left*z`` and ``V=H_s*right*z``.  Hollow powers own every
    ``i=j``, ``i=k``, and ``j=k`` exclusion exactly.
    """

    sign = np.asarray(sign, dtype=np.float64)
    r, s, t = factor.powers
    hr = _hollow_power(factor.edge, r)
    hs = _hollow_power(factor.edge, s)
    ht = _hollow_power(factor.edge, t)
    u = hr * (factor.left * sign)[None, :]
    v = hs * (factor.right * sign)[None, :]
    return factor.row * np.sum((u @ ht) * v, axis=1)


def factor_probe_t_dual(
    factor: GraphFactorDual, sign: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Primal/Frechet triangle probe; exactly three hidden GEMMs total."""

    base = factor.value
    sign = np.asarray(sign, dtype=np.float64)
    r, s, t = base.powers
    hr = _hollow_power(base.edge, r)
    hs = _hollow_power(base.edge, s)
    ht = _hollow_power(base.edge, t)
    hrdot = _hollow_power_dot(base.edge, factor.edge_dot, r)
    hsdot = _hollow_power_dot(base.edge, factor.edge_dot, s)
    htdot = _hollow_power_dot(base.edge, factor.edge_dot, t)
    u = hr * (base.left * sign)[None, :]
    v = hs * (base.right * sign)[None, :]
    udot = hrdot * (base.left * sign)[None, :] + hr * (
        factor.left_dot * sign
    )[None, :]
    vdot = hsdot * (base.right * sign)[None, :] + hs * (
        factor.right_dot * sign
    )[None, :]
    um = u @ ht
    core = np.sum(um * v, axis=1)
    core_dot = np.sum(((udot @ ht) + (u @ htdot)) * v + um * vdot, axis=1)
    value = base.row * core
    tangent = factor.row_dot * core + base.row * core_dot
    return value, tangent


def repeated_output_probe(
    t: np.ndarray, sign: np.ndarray, weight: np.ndarray
) -> dict[str, np.ndarray]:
    """M129's exact-in-expectation repeated-output transport."""

    t = np.asarray(t, dtype=np.float64)
    sign = np.asarray(sign, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    projection = sign @ weight
    gram = weight.T @ (t[:, None] * weight)
    diagonal = np.diag(gram).copy()
    pair = projection[:, None] * projection[None, :]
    aaab = 1.5 * (
        gram * projection[:, None] ** 2 + diagonal[:, None] * pair
    )
    aabb = 0.5 * (
        diagonal[:, None] * projection[None, :] ** 2
        + diagonal[None, :] * projection[:, None] ** 2
    ) + 2.0 * gram * pair
    return {
        "k4_aaaa": np.diag(aaab).copy(),
        "k4_aaab": aaab,
        "k4_aabb": aabb,
    }


def repeated_output_probe_dual(
    t: np.ndarray, t_dot: np.ndarray, sign: np.ndarray, weight: np.ndarray
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    primal = repeated_output_probe(t, sign, weight)
    tangent = repeated_output_probe(t_dot, sign, weight)
    return {key: (primal[key], tangent[key]) for key in primal}


def factor_proxy(factor: GraphFactor) -> float:
    """Cheap weights-only importance proxy; no output or outcome is used."""

    r, s, t = factor.powers
    pieces = (
        np.linalg.norm(factor.row),
        np.linalg.norm(factor.left),
        np.linalg.norm(factor.right),
        np.linalg.norm(_hollow_power(factor.edge, r)),
        np.linalg.norm(_hollow_power(factor.edge, s)),
        np.linalg.norm(_hollow_power(factor.edge, t)),
    )
    value = float(math.prod(float(item) for item in pieces))
    return value if math.isfinite(value) else math.inf


def importance_probabilities(factors: Sequence[GraphFactor]) -> np.ndarray:
    proxies = np.asarray([factor_proxy(factor) for factor in factors], dtype=np.float64)
    active = proxies > 0.0
    if not np.any(active) or not np.all(np.isfinite(proxies[active])):
        raise ValueError("importance proxy is not normalizable")
    probabilities = np.zeros_like(proxies)
    probabilities[active] = proxies[active] / np.sum(proxies[active])
    return probabilities


def all_rademacher_signs(width: int) -> Iterable[np.ndarray]:
    for bits in itertools.product((-1.0, 1.0), repeat=width):
        yield np.asarray(bits, dtype=np.float64)


def response_scalar(
    tables: dict[str, np.ndarray], response31: np.ndarray, response22: np.ndarray
) -> float:
    return float(
        np.sum(np.asarray(response31) * tables["k4_aaab"])
        + np.sum(np.asarray(response22) * tables["k4_aabb"])
    )


def exact_joint_response_variance(
    factors: Sequence[GraphFactor],
    weight: np.ndarray,
    response31: np.ndarray,
    response22: np.ndarray,
    probabilities: np.ndarray,
) -> dict[str, float]:
    """Enumerate degree and hidden-sign randomness at generated width <= 6."""

    probabilities = np.asarray(probabilities, dtype=np.float64)
    signs = list(all_rademacher_signs(weight.shape[0]))
    contributions = np.empty((len(factors), len(signs)), dtype=np.float64)
    for factor_index, factor in enumerate(factors):
        for sign_index, sign in enumerate(signs):
            tables = repeated_output_probe(factor_probe_t(factor, sign), sign, weight)
            contributions[factor_index, sign_index] = response_scalar(
                tables, response31, response22
            )
    sign_mean = np.mean(contributions, axis=1)
    target = float(np.sum(sign_mean))
    hidden_samples = np.sum(contributions, axis=0)
    hidden_variance = float(np.mean(hidden_samples**2) - target**2)
    joint_second = 0.0
    for index, probability in enumerate(probabilities):
        if probability > 0.0:
            joint_second += float(np.mean(contributions[index] ** 2)) / probability
    joint_variance = joint_second - target**2
    return {
        "target": target,
        "hidden_variance_one_probe": max(0.0, hidden_variance),
        "joint_variance_one_probe": max(0.0, joint_variance),
        "joint_over_hidden": joint_variance / hidden_variance
        if hidden_variance > 0.0
        else math.inf,
        "joint_over_m129_p2": joint_variance / (hidden_variance / 2.0)
        if hidden_variance > 0.0
        else math.inf,
    }


def cost_envelope(samples: int, *, second_order: bool) -> dict[str, float | int]:
    """Static WhestBench square-call comparison at width 256, 31 sources.

    First-order attaches to M126 P8.  Second-order replaces M129's prebuilt
    hollow-211 probes by an on-the-fly joint factor/sign sample.  The latter
    uses three hidden and two output GEMMs per sample for primal+tangent.
    Coefficient/proxy construction and the published M129 reserves are shown
    separately; they are not hidden inside the lower bound.
    """

    if type(samples) is not int or samples < 1:
        raise ValueError("samples must be a positive integer")
    width, layers = 256, 31
    square = 2 * width**3 - width**2
    if second_order:
        carrier = 16_971_970_384
        lower_calls = 66 + 5 * samples
        upper_calls = 78 + 5 * samples
        reserves = 16_800_000_000
        lower = layers * lower_calls * square + carrier
        protected_upper = int(
            math.ceil(1.25 * (layers * upper_calls * square + reserves))
        ) + carrier
        return {
            "samples": samples,
            "square_bill": square,
            "calls_per_layer_lower": lower_calls,
            "calls_per_layer_upper": upper_calls,
            "lower_total": lower,
            "protected_upper": protected_upper,
            "unpriced_coefficient_proxy_builder": True,
        }
    protected_m126_p8 = 94_490_251_600
    increment = int(math.ceil(1.25 * layers * 2 * samples * square))
    return {
        "samples": samples,
        "square_bill": square,
        "protected_m126_p8": protected_m126_p8,
        "protected_increment": increment,
        "protected_total_before_builder": protected_m126_p8 + increment,
        "unpriced_coefficient_proxy_builder": True,
    }


def equicorrelation_partial_sums(
    alpha: Sequence[float], sigma: Sequence[float], rho: float, horizons: Sequence[int]
) -> list[float]:
    """Raw ``E[Y_0^2Y_1Y_2]`` graph partial sums for a divergence diagnostic."""

    alpha = np.asarray(alpha, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    if alpha.shape != (3,) or sigma.shape != (3,):
        raise ValueError("equicorrelation diagnostic needs exactly three nodes")
    edge = np.full((3, 3), float(rho), dtype=np.float64)
    np.fill_diagonal(edge, 1.0)
    answers: list[float] = []
    for terms in horizons:
        total = 0.0
        coefficients = [
            [
                power_hermite_coefficient(
                    float(alpha[node]), float(sigma[node]), (2, 1, 1)[node], degree
                )
                for degree in range(terms)
            ]
            for node in range(3)
        ]
        for r in range(terms):
            for s in range(terms):
                for t in range(terms):
                    if r + s >= terms or r + t >= terms or s + t >= terms:
                        continue
                    total += (
                        coefficients[0][r + s]
                        * coefficients[1][r + t]
                        * coefficients[2][s + t]
                        * rho ** (r + s + t)
                        / (math.factorial(r) * math.factorial(s) * math.factorial(t))
                    )
        answers.append(total)
    return answers


def tree_211_tensor_oracle(state: NonzeroMeanBridgeState) -> np.ndarray:
    """Dense generated-only extraction of the continued M122 tree."""

    dense = tree_tensor_continuation(state, 4)
    n = state.mean.size
    answer = np.zeros((n, n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    answer[i, j, k] = dense[i, i, j, k]
    return answer
