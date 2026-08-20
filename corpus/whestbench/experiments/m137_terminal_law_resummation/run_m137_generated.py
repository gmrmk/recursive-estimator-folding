"""Frozen generated-only M137 experiment.

This runner never imports WHestBench or reads any repository data.  It creates
small iid-He deep ReLU networks, takes two independent moment banks and a third
independent high-count ReLU-reference bank, then applies *all* frozen terminal
closures to every output.  Whole networks are the bootstrap units.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from m137_terminal_law_resummation import (
    closures_from_moments,
    make_iid_he_network,
    moments4_from_raw,
    raw_moments_and_relu_reference,
    symmetric_gaussian_moment_counterexample,
    target_terminal_cost_interface,
)


# PREDECLARED generated-only configuration.  Do not change after observing the
# output.  No dataset index, scorer target, leaderboard value, or contest MLP
# appears in this file.
WIDTH = 8
DEPTH = 32
NETWORKS = 12
# This is deliberately as large as the independent reference bank: the M137
# question grants terminal moments essentially for free, so closure error must
# not be attributed to a noisy moment estimate.
MOMENT_SAMPLES = 2**20
STABILITY_SAMPLES = 2**17
REFERENCE_SAMPLES = 2**20
CHUNK = 32768
NETWORK_SEED_BASE = 13_700
MOMENT_SEED_BASE = 23_700
STABILITY_SEED_BASE = 33_700
REFERENCE_SEED_BASE = 43_700
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 53_700
METHODS = (
    "gaussian",
    "edgeworth_k4_second",
    "maxent_quartic_or_gaussian",
    "two_gaussian_mixture_or_gaussian",
    "certified_interval_midpoint",
)


def percentile_ci(samples: np.ndarray) -> list[float]:
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def main() -> None:
    started = time.perf_counter()
    per_network: list[dict[str, object]] = []
    network_mses: dict[str, list[float]] = {name: [] for name in METHODS}
    network_maxent_ok: list[float] = []
    network_mixture_ok: list[float] = []
    network_edgeworth_density_ok: list[float] = []
    network_interval_coverage: list[float] = []
    skew_drift: list[float] = []
    kurtosis_drift: list[float] = []

    for network_index in range(NETWORKS):
        weights = make_iid_he_network(WIDTH, DEPTH, NETWORK_SEED_BASE + network_index)
        raw_a, _ = raw_moments_and_relu_reference(
            weights, MOMENT_SAMPLES, CHUNK, MOMENT_SEED_BASE + network_index, reference=False
        )
        raw_b, _ = raw_moments_and_relu_reference(
            weights, STABILITY_SAMPLES, CHUNK, STABILITY_SEED_BASE + network_index, reference=False
        )
        _unused, reference = raw_moments_and_relu_reference(
            weights, REFERENCE_SAMPLES, CHUNK, REFERENCE_SEED_BASE + network_index, reference=True
        )
        moments_a = [moments4_from_raw(raw_a[:, output]) for output in range(WIDTH)]
        moments_b = [moments4_from_raw(raw_b[:, output]) for output in range(WIDTH)]
        predictions = {name: np.empty(WIDTH, dtype=np.float64) for name in METHODS}
        maxent_ok = []
        mixture_ok = []
        edgeworth_ok = []
        coverage = []
        for output, moment in enumerate(moments_a):
            values, diagnostics = closures_from_moments(moment)
            for name in METHODS:
                predictions[name][output] = values[name]
            maxent_ok.append(bool(diagnostics["maxent_feasible"]))
            mixture_ok.append(bool(diagnostics["mixture_feasible"]))
            edgeworth_ok.append(float(diagnostics["edgeworth_density_minimum"]) >= -1e-10)
            lo, hi = diagnostics["certified_interval"]
            coverage.append(bool(float(lo) - 1e-12 <= reference[output] <= float(hi) + 1e-12))
        mses = {name: float(np.mean((predictions[name] - reference) ** 2)) for name in METHODS}
        for name, value in mses.items():
            network_mses[name].append(value)
        network_maxent_ok.append(float(np.mean(maxent_ok)))
        network_mixture_ok.append(float(np.mean(mixture_ok)))
        network_edgeworth_density_ok.append(float(np.mean(edgeworth_ok)))
        network_interval_coverage.append(float(np.mean(coverage)))
        skew_drift.append(float(np.mean(np.abs([a.skewness - b.skewness for a, b in zip(moments_a, moments_b)]))))
        kurtosis_drift.append(float(np.mean(np.abs([a.excess_kurtosis - b.excess_kurtosis for a, b in zip(moments_a, moments_b)]))))
        per_network.append({
            "network_index": network_index,
            "mse": mses,
            "maxent_feasible_fraction": network_maxent_ok[-1],
            "mixture_feasible_fraction": network_mixture_ok[-1],
            "edgeworth_nonnegative_fraction": network_edgeworth_density_ok[-1],
            "certified_interval_reference_coverage": network_interval_coverage[-1],
            "mean_abs_skewness": float(np.mean(np.abs([m.skewness for m in moments_a]))),
            "mean_excess_kurtosis": float(np.mean([m.excess_kurtosis for m in moments_a])),
            "mean_abs_skew_bank_drift": skew_drift[-1],
            "mean_abs_excess_kurtosis_bank_drift": kurtosis_drift[-1],
        })
        elapsed = time.perf_counter() - started
        print(f"network={network_index + 1}/{NETWORKS} seconds={elapsed:.1f}", flush=True)

    mse_array = {name: np.asarray(values, dtype=np.float64) for name, values in network_mses.items()}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bootstrap_indices = rng.integers(0, NETWORKS, size=(BOOTSTRAP_REPS, NETWORKS))
    means = {name: np.mean(mse_array[name][bootstrap_indices], axis=1) for name in METHODS}
    summary: dict[str, object] = {}
    edge = means["edgeworth_k4_second"]
    for name in METHODS:
        ratio = means[name] / edge
        summary[name] = {
            "network_mean_mse": float(np.mean(mse_array[name])),
            "network_median_mse": float(np.median(mse_array[name])),
            "bootstrap_mse_ci95": percentile_ci(means[name]),
            "ratio_to_edgeworth": float(np.mean(mse_array[name]) / np.mean(mse_array["edgeworth_k4_second"])),
            "bootstrap_ratio_ci95": percentile_ci(ratio),
        }

    # Promotion is deliberately harsh: 10x MSE reduction vs the already
    # granted-k3/k4 Edgeworth oracle, and its upper 95% ratio < 0.2.  A
    # candidate must also be a proper law on every coordinate, not fallback.
    promoted: list[str] = []
    for name in ("maxent_quartic_or_gaussian", "two_gaussian_mixture_or_gaussian", "certified_interval_midpoint"):
        upper = float(np.quantile(means[name] / edge, 0.975))
        proper = (
            np.all(np.asarray(network_maxent_ok) == 1.0)
            if name == "maxent_quartic_or_gaussian"
            else (np.all(np.asarray(network_mixture_ok) == 1.0) if name == "two_gaussian_mixture_or_gaussian" else True)
        )
        if upper < 0.2 and proper:
            promoted.append(name)

    elapsed = time.perf_counter() - started
    payload = {
        "generated_only": True,
        "no_contest_data_or_targets": True,
        "exact_moment_interpretation": (
            "The theorem/counterexample concerns exact granted moments.  This "
            "runner does NOT grant them: its A bank estimates moments and its "
            "B bank measures the resulting skew/kurtosis drift.  Therefore its "
            "method ratios are a frozen generated falsifier, not target-shape "
            "or exact-oracle efficacy evidence."
        ),
        "target_shape_extrapolation": (
            "FORBIDDEN: width=8, depth=32 is intentionally a small falsifier "
            "and contains dying-network / zero-output degeneracy.  No efficacy "
            "claim is extrapolated to the target width."
        ),
        "frozen_config": {
            "width": WIDTH, "depth": DEPTH, "networks": NETWORKS,
            "moment_samples_per_network": MOMENT_SAMPLES,
            "stability_samples_per_network": STABILITY_SAMPLES,
            "independent_reference_samples_per_network": REFERENCE_SAMPLES,
            "chunk": CHUNK, "bootstrap_reps": BOOTSTRAP_REPS,
            "seeds": {
                "network_base": NETWORK_SEED_BASE, "moment_base": MOMENT_SEED_BASE,
                "stability_base": STABILITY_SEED_BASE, "reference_base": REFERENCE_SEED_BASE,
                "bootstrap": BOOTSTRAP_SEED,
            },
        },
        "counterexample": symmetric_gaussian_moment_counterexample(),
        "methods": summary,
        "diagnostics": {
            "maxent_feasible_fraction_mean": float(np.mean(network_maxent_ok)),
            "two_gaussian_mixture_feasible_fraction_mean": float(np.mean(network_mixture_ok)),
            "edgeworth_density_nonnegative_fraction_mean": float(np.mean(network_edgeworth_density_ok)),
            "certified_interval_reference_coverage_mean": float(np.mean(network_interval_coverage)),
            "mean_abs_skewness_bank_drift": float(np.mean(skew_drift)),
            "mean_abs_excess_kurtosis_bank_drift": float(np.mean(kurtosis_drift)),
        },
        "saddlepoint": "K(t) truncated at k4 is not a globally valid probability law unless k3=k4=0 (Marcinkiewicz); no saddlepoint closure was admitted.",
        "target_terminal_cost_interface": target_terminal_cost_interface(),
        "promotion_gate": {
            "relative_to_edgeworth": "mean MSE <= 0.1 and upper 95% bootstrap ratio < 0.2",
            "proper_law_required": True,
            "promoted": promoted,
            "status": "PROMOTE" if promoted else "KILL_AS_TERMINAL_LAW_ESCAPE",
        },
        "per_network": per_network,
        "seconds": elapsed,
    }
    out = Path(__file__).with_name("M137_RESULTS_20260807.json")
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["promotion_gate"], indent=2, sort_keys=True), flush=True)
    print(out, flush=True)


if __name__ == "__main__":
    main()
