"""Frozen generated-only variance screen for M133.

The comparison is deliberately favorable to HT: it grants exact per-triple
feature norms at no charge and matches only the arithmetic cost of eight M129
hollow Rademacher probes.  The deployable HT catalog has only a cheap upper
bound and must additionally pay catalog construction, sorting, and wall time.
"""

from __future__ import annotations

import json
import math

import numpy as np

from m133_ht_hidden_edge import (
    collision211_conductance_catalog,
    collision211_exact_from_catalog,
    collision211_factored_proposal,
    collision211_hh_batched,
    collision211_hollow_probe,
    collision211_ht_sample,
    systematic_pps_sample,
    waterfill_inclusion_probabilities,
)


CONFIG = {
    "widths": [12, 16, 24, 32],
    "seeds": [1338101, 1338102, 1338103, 1338104],
    "replicates": 128,
    "rademacher_probes": 8,
    "bridge_offdiagonal_sd": 0.11,
    "weight_sd_rule": "1/sqrt(width)",
    "collision_rule": "quadratic_jet_1_over_4pi",
    "ht_order": "fresh_uniform_permutation_then_systematic_phase",
    "factored_uniform_mixture": 0.05,
    "metric": "relative_frobenius_squared_on_aaab_plus_aabb",
}


def bridge(width: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(scale=CONFIG["bridge_offdiagonal_sd"], size=(width, width))
    q = 0.5 * (raw + raw.T)
    np.fill_diagonal(q, 1.0)
    return q


def quadratic_defect(q: np.ndarray) -> np.ndarray:
    width = q.shape[0]
    answer = np.zeros((width, width, width), dtype=np.float64)
    coefficient = 1.0 / (4.0 * math.pi)
    for i in range(width):
        for j in range(width):
            for k in range(j + 1, width):
                if len({i, j, k}) != 3:
                    continue
                value = coefficient * (
                    q[i, j] * q[i, k]
                    + q[i, j] * q[j, k]
                    + q[i, k] * q[j, k]
                )
                answer[i, j, k] = value
                answer[i, k, j] = value
    return answer


def squared_error(sample: dict[str, np.ndarray], exact: dict[str, np.ndarray]) -> float:
    return float(
        np.sum((sample["k4_aaab"] - exact["k4_aaab"]) ** 2)
        + np.sum((sample["k4_aabb"] - exact["k4_aabb"]) ** 2)
    )


def aggregate_probes(
    defect: np.ndarray, weight: np.ndarray, rng: np.random.Generator, probes: int
) -> dict[str, np.ndarray]:
    outputs = weight.shape[1]
    answer = {
        "k4_aaaa": np.zeros(outputs),
        "k4_aaab": np.zeros((outputs, outputs)),
        "k4_aabb": np.zeros((outputs, outputs)),
    }
    for _ in range(probes):
        z = rng.choice(np.asarray((-1.0, 1.0)), size=defect.shape[0])
        sample = collision211_hollow_probe(defect, weight, z)
        for key in answer:
            answer[key] += sample[key] / probes
    return answer


def sample_size_at_equal_probe_arithmetic(width: int, probes: int) -> dict[str, int]:
    square = 2 * width**3 - width**2
    packed_pairs = math.comb(width, 2)
    packed_reduction = 2 * width * packed_pairs - width
    gemv = 2 * width**2 - width
    probe_cost = square + packed_reduction + gemv
    tuple_cost = 10 * width**2
    return {
        "single_hollow_probe_f32": probe_cost,
        "all_hollow_probes_f32": probes * probe_cost,
        "single_ht_tuple_f32": tuple_cost,
        "ht_sample_size": (probes * probe_cost) // tuple_cost,
    }


def summarize(values: list[float]) -> dict[str, float]:
    array = np.asarray(values)
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.90)),
        "maximum": float(np.max(array)),
    }


def run() -> dict[str, object]:
    cells: list[dict[str, object]] = []
    pooled = {
        "ht_exact_norm": [],
        "ht_upper_norm": [],
        "hh_factored": [],
        "hh_factored_k4n": [],
        "rademacher_p8": [],
    }
    for width in CONFIG["widths"]:
        cost = sample_size_at_equal_probe_arithmetic(
            width, CONFIG["rademacher_probes"]
        )
        for seed in CONFIG["seeds"]:
            q = bridge(width, seed)
            defect = quadratic_defect(q)
            rng_weight = np.random.default_rng(seed + 100_000)
            weight = rng_weight.normal(
                scale=1.0 / math.sqrt(width), size=(width, width)
            )
            exact_catalog = collision211_conductance_catalog(
                defect, weight, norm_mode="exact_generated_only"
            )
            upper_catalog = collision211_conductance_catalog(
                defect, weight, norm_mode="upper"
            )
            factored = collision211_factored_proposal(
                q, weight, uniform_mixture=CONFIG["factored_uniform_mixture"]
            )
            exact = collision211_exact_from_catalog(exact_catalog)
            energy = float(
                np.sum(exact["k4_aaab"] ** 2)
                + np.sum(exact["k4_aabb"] ** 2)
            )
            sample_size = min(cost["ht_sample_size"], exact_catalog.units.shape[0])
            p_exact = waterfill_inclusion_probabilities(
                exact_catalog.scores, sample_size
            )
            p_upper = waterfill_inclusion_probabilities(
                upper_catalog.scores, sample_size
            )
            errors = {
                "ht_exact_norm": [],
                "ht_upper_norm": [],
                "hh_factored": [],
                "hh_factored_k4n": [],
                "rademacher_p8": [],
            }
            rng = np.random.default_rng(seed + 200_000)
            for _ in range(CONFIG["replicates"]):
                phase_exact = float(rng.random())
                phase_upper = float(rng.random())
                order_exact = rng.permutation(p_exact.size)
                order_upper = rng.permutation(p_upper.size)
                mask_exact = systematic_pps_sample(
                    p_exact, phase=phase_exact, order=order_exact
                )
                mask_upper = systematic_pps_sample(
                    p_upper, phase=phase_upper, order=order_upper
                )
                ht_exact = collision211_ht_sample(
                    exact_catalog, p_exact, mask_exact
                )
                ht_upper = collision211_ht_sample(
                    upper_catalog, p_upper, mask_upper
                )
                factored_draws = factored.sample(rng, sample_size)
                hh_factored = collision211_hh_batched(
                    weight,
                    factored,
                    factored_draws,
                    lambda i, j, k: float(defect[i, j, k]),
                )
                factored_k4n_draws = factored.sample(rng, 4 * width)
                hh_factored_k4n = collision211_hh_batched(
                    weight,
                    factored,
                    factored_k4n_draws,
                    lambda i, j, k: float(defect[i, j, k]),
                )
                probe = aggregate_probes(
                    defect, weight, rng, CONFIG["rademacher_probes"]
                )
                errors["ht_exact_norm"].append(squared_error(ht_exact, exact) / energy)
                errors["ht_upper_norm"].append(squared_error(ht_upper, exact) / energy)
                errors["hh_factored"].append(squared_error(hh_factored, exact) / energy)
                errors["hh_factored_k4n"].append(
                    squared_error(hh_factored_k4n, exact) / energy
                )
                errors["rademacher_p8"].append(squared_error(probe, exact) / energy)
            for key in pooled:
                pooled[key].extend(errors[key])
            effective_support = float(
                np.sum(exact_catalog.scores) ** 2
                / np.sum(exact_catalog.scores**2)
            )
            top_mass = float(
                np.sum(np.sort(exact_catalog.scores)[-sample_size:])
                / np.sum(exact_catalog.scores)
            )
            cells.append(
                {
                    "width": width,
                    "seed": seed,
                    "population": int(exact_catalog.units.shape[0]),
                    "sample_size": sample_size,
                    "inclusion_fraction": sample_size / exact_catalog.units.shape[0],
                    "effective_support": effective_support,
                    "top_sample_size_score_mass": top_mass,
                    "cost": cost,
                    "relative_mse": {key: summarize(value) for key, value in errors.items()},
                    "mean_ratio_exact_ht_over_p8": (
                        float(np.mean(errors["ht_exact_norm"]))
                        / float(np.mean(errors["rademacher_p8"]))
                    ),
                    "mean_ratio_upper_ht_over_p8": (
                        float(np.mean(errors["ht_upper_norm"]))
                        / float(np.mean(errors["rademacher_p8"]))
                    ),
                }
            )
    return {
        "config": CONFIG,
        "cells": cells,
        "pooled": {key: summarize(value) for key, value in pooled.items()},
        "pooled_mean_ratio_exact_ht_over_p8": (
            float(np.mean(pooled["ht_exact_norm"]))
            / float(np.mean(pooled["rademacher_p8"]))
        ),
        "pooled_mean_ratio_upper_ht_over_p8": (
            float(np.mean(pooled["ht_upper_norm"]))
            / float(np.mean(pooled["rademacher_p8"]))
        ),
        "pooled_mean_ratio_factored_hh_over_p8": (
            float(np.mean(pooled["hh_factored"]))
            / float(np.mean(pooled["rademacher_p8"]))
        ),
        "pooled_mean_ratio_factored_k4n_over_p8": (
            float(np.mean(pooled["hh_factored_k4n"]))
            / float(np.mean(pooled["rademacher_p8"]))
        ),
        "contest_data_accessed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["pooled"], indent=2, sort_keys=True))
    print("pooled exact-HT / P8", result["pooled_mean_ratio_exact_ht_over_p8"])
    print("pooled upper-HT / P8", result["pooled_mean_ratio_upper_ht_over_p8"])
    print("pooled factored-HH / P8", result["pooled_mean_ratio_factored_hh_over_p8"])
    print("pooled factored-HH-k4n / P8", result["pooled_mean_ratio_factored_k4n_over_p8"])
    for width in CONFIG["widths"]:
        cells = [cell for cell in result["cells"] if cell["width"] == width]
        exact_ht = np.mean(
            [cell["relative_mse"]["ht_exact_norm"]["mean"] for cell in cells]
        )
        upper_ht = np.mean(
            [cell["relative_mse"]["ht_upper_norm"]["mean"] for cell in cells]
        )
        factored_hh = np.mean(
            [cell["relative_mse"]["hh_factored"]["mean"] for cell in cells]
        )
        factored_hh_k4n = np.mean(
            [cell["relative_mse"]["hh_factored_k4n"]["mean"] for cell in cells]
        )
        p8 = np.mean(
            [cell["relative_mse"]["rademacher_p8"]["mean"] for cell in cells]
        )
        population = cells[0]["population"]
        sample_size = cells[0]["sample_size"]
        effective_support = np.mean([cell["effective_support"] for cell in cells])
        top_mass = np.mean([cell["top_sample_size_score_mass"] for cell in cells])
        print(
            "width",
            width,
            "K/M",
            sample_size / population,
            "effective_support/M",
            effective_support / population,
            "top_mass",
            top_mass,
            "exactHT/P8",
            exact_ht / p8,
            "upperHT/P8",
            upper_ht / p8,
            "factoredHH/P8",
            factored_hh / p8,
            "factoredHH-k4n/P8",
            factored_hh_k4n / p8,
        )
