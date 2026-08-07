"""Clean-room falsifier for terminal mean/second-moment control variates.

This uses no WHestBench data.  It fixes one width-8, depth-32 He-Gaussian
ReLU network (seed 4) and one final coordinate.  The network is deliberately
small enough to reproduce quickly, but has the target depth: an independent
penultimate pilot costs at least 31/32 of a full path before sidecar work.

The point is not that this one network is representative.  The exact split
formula below is distribution-free for a fixed feature vector U.  The generated
network is a compact regression test that catches two illegal conclusions:

* treating sample/cross-fit estimates of E[U] as known expectations; and
* claiming an independent-pilot win after omitting its 31/32-depth cost.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np


WIDTH = 8
DEPTH = 32
NETWORK_SEED = 4
TRUTH_SAMPLES = 2_000_000
TRUTH_CHUNK = 100_000
TRIALS = 5_000
EVAL_PATHS = 128
PILOT_PATHS = 128
# A penultimate pilot omits only the final dense/ReLU layer at target depth.
PILOT_COST_RATIO = (DEPTH - 1) / DEPTH


@dataclass(frozen=True)
class Population:
    mean_f: float
    variance_f: float
    mean_u: np.ndarray
    covariance_u: np.ndarray
    covariance_uf: np.ndarray
    positive_fraction: float
    negative_fraction: float


def make_network() -> list[np.ndarray]:
    rng = np.random.default_rng(NETWORK_SEED)
    scale = np.sqrt(2.0 / WIDTH)
    return [rng.normal(0.0, scale, size=(WIDTH, WIDTH)) for _ in range(DEPTH)]


def terminal_preactivation(x: np.ndarray, weights: list[np.ndarray]) -> np.ndarray:
    hidden = x
    for weight in weights[:-1]:
        hidden = np.maximum(hidden @ weight, 0.0)
    return hidden @ weights[-1][:, 0]


def population_moments(weights: list[np.ndarray]) -> Population:
    rng = np.random.default_rng(1_000_004)
    sum_f = 0.0
    sum_f2 = 0.0
    sum_u = np.zeros(2)
    sum_uu = np.zeros((2, 2))
    sum_uf = np.zeros(2)
    positive = 0
    negative = 0
    for _ in range(TRUTH_SAMPLES // TRUTH_CHUNK):
        z = terminal_preactivation(
            rng.standard_normal((TRUTH_CHUNK, WIDTH)), weights
        )
        f = np.maximum(z, 0.0)
        u = np.column_stack((z, z * z))
        sum_f += float(np.sum(f))
        sum_f2 += float(np.sum(f * f))
        sum_u += np.sum(u, axis=0)
        sum_uu += u.T @ u
        sum_uf += u.T @ f
        positive += int(np.count_nonzero(z > 0.0))
        negative += int(np.count_nonzero(z < 0.0))

    n = float(TRUTH_SAMPLES)
    mean_f = sum_f / n
    mean_u = sum_u / n
    variance_f = sum_f2 / n - mean_f * mean_f
    covariance_u = sum_uu / n - np.outer(mean_u, mean_u)
    covariance_uf = sum_uf / n - mean_u * mean_f
    return Population(
        mean_f=mean_f,
        variance_f=variance_f,
        mean_u=mean_u,
        covariance_u=covariance_u,
        covariance_uf=covariance_uf,
        positive_fraction=positive / n,
        negative_fraction=negative / n,
    )


def explained_fraction(population: Population, controls: int) -> float:
    sigma = population.covariance_u[:controls, :controls]
    c = population.covariance_uf[:controls]
    return float(c @ np.linalg.solve(sigma, c) / population.variance_f)


def optimal_cost_ratio(r_squared: float, pilot_to_eval_cost: float) -> tuple[float, float]:
    """Return (optimal p/n, minimum variance-times-cost ratio).

    With n evaluation paths, p independent pilot paths, feature U, and the
    optimal split coefficient,

      V_split / V_direct_equal_cost
        = (1+a t) (1+(1-R^2)t)/(1+t),

    where a is pilot/evaluation path cost and t=p/n.  Its minimum is one at
    t=0 whenever R^2 <= a.  This does not assume Gaussian projections.
    """
    if r_squared <= pilot_to_eval_cost:
        return 0.0, 1.0
    t = np.sqrt(
        r_squared * (1.0 - pilot_to_eval_cost)
        / (pilot_to_eval_cost * (1.0 - r_squared))
    ) - 1.0
    ratio = (
        (1.0 + pilot_to_eval_cost * t)
        * (1.0 + (1.0 - r_squared) * t)
        / (1.0 + t)
    )
    return float(t), float(ratio)


def simulation_check(weights: list[np.ndarray], population: Population) -> dict[str, float]:
    """Monte Carlo check at a fixed nonzero pilot split, not a fit."""
    m_direct = round(EVAL_PATHS + PILOT_COST_RATIO * PILOT_PATHS)
    rng = np.random.default_rng(2_000_004)
    direct_errors = []
    split_errors = []
    same_path_defects = []
    crossfit_defects = []

    # The split coefficient is population-oracle optimal.  Giving the proposed
    # method this advantage can only make the falsifier more favorable to it.
    beta_oracle = np.linalg.solve(
        population.covariance_u, population.covariance_uf
    )
    beta_split = (PILOT_PATHS / (EVAL_PATHS + PILOT_PATHS)) * beta_oracle

    for _ in range(TRIALS):
        z = terminal_preactivation(
            rng.standard_normal((EVAL_PATHS + PILOT_PATHS, WIDTH)), weights
        )
        f = np.maximum(z, 0.0)
        u = np.column_stack((z, z * z))
        f_eval = f[:EVAL_PATHS]
        u_eval = u[:EVAL_PATHS]
        u_pilot = u[EVAL_PATHS:]
        split = np.mean(f_eval) - beta_split @ (
            np.mean(u_eval, axis=0) - np.mean(u_pilot, axis=0)
        )
        direct = np.mean(f[:m_direct])
        split_errors.append((split - population.mean_f) ** 2)
        direct_errors.append((direct - population.mean_f) ** 2)

        # Same-path centering is the direct mean identically.  This also
        # includes the stated positive-part identity for the first feature.
        same_identity = 0.5 * (np.mean(z[:EVAL_PATHS]) + np.mean(np.abs(z[:EVAL_PATHS])))
        same_path = np.mean(f_eval) - beta_oracle @ (
            np.mean(u_eval, axis=0) - np.mean(u_eval, axis=0)
        )
        same_path_defects.append(abs(same_identity - np.mean(f_eval)))
        same_path_defects.append(abs(same_path - np.mean(f_eval)))

        # A two-fold common-coefficient cross-fit cancels algebraically too.
        a = slice(0, EVAL_PATHS // 2)
        b = slice(EVAL_PATHS // 2, EVAL_PATHS)
        crossfit = 0.5 * (
            np.mean(f_eval[a]) - beta_oracle @ (np.mean(u_eval[a], axis=0) - np.mean(u_eval[b], axis=0))
            + np.mean(f_eval[b]) - beta_oracle @ (np.mean(u_eval[b], axis=0) - np.mean(u_eval[a], axis=0))
        )
        crossfit_defects.append(abs(crossfit - np.mean(f_eval)))

    return {
        "direct_mse": float(np.mean(direct_errors)),
        "independent_pilot_mse": float(np.mean(split_errors)),
        "independent_pilot_over_direct": float(np.mean(split_errors) / np.mean(direct_errors)),
        "max_same_path_defect": float(np.max(same_path_defects)),
        "max_common_beta_crossfit_defect": float(np.max(crossfit_defects)),
        "direct_path_count_at_equal_cost": float(m_direct),
    }


def main() -> None:
    weights = make_network()
    population = population_moments(weights)
    results: dict[str, object] = {
        "network": {
            "width": WIDTH,
            "depth": DEPTH,
            "seed": NETWORK_SEED,
            "truth_samples": TRUTH_SAMPLES,
        },
        "population": {
            "mean_relu": population.mean_f,
            "mean_z": float(population.mean_u[0]),
            "second_moment_z": float(population.mean_u[1]),
            "variance_relu": population.variance_f,
            "positive_fraction": population.positive_fraction,
            "negative_fraction": population.negative_fraction,
        },
        "pilot_cost_ratio": PILOT_COST_RATIO,
        "controls": {},
    }
    for name, controls in (("mean_only", 1), ("mean_and_second_moment", 2)):
        r_squared = explained_fraction(population, controls)
        t_star, ratio_star = optimal_cost_ratio(r_squared, PILOT_COST_RATIO)
        t_one = 1.0
        ratio_one = (
            (1.0 + PILOT_COST_RATIO * t_one)
            * (1.0 + (1.0 - r_squared) * t_one)
            / (1.0 + t_one)
        )
        results["controls"][name] = {
            "population_R_squared": r_squared,
            "known_moment_oracle_variance_gain": 1.0 / (1.0 - r_squared),
            "optimal_independent_pilot_to_eval_paths": t_star,
            "best_independent_pilot_cost_adjusted_ratio": ratio_star,
            "equal_path_split_cost_adjusted_ratio": ratio_one,
        }

    results["simulation"] = simulation_check(weights, population)
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
