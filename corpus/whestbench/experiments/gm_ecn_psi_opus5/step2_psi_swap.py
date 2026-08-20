"""Step 2 of the gm_ecn_psi cheapest falsifier.

The identical ECN no-ladder cell at K=48 / d=6 on the same 32 frozen states,
with ONLY psi swapped: the SPD surrogate metric is replaced by the exact ReLU
observable Jacobian pullback in theta = (alpha, ell = log sigma) coordinates,
using the judge's prescribed symmetric local pullback (G_i + G_j)/2.

tau (entropic_transport), phi (decode_total_moments), the generator, the q3
comparator and the 32 seeds are the frozen originals, imported not edited.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

FROZEN_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\ecn_jacobian_maxent_compressor"
)
sys.path.insert(0, str(FROZEN_DIR))
import experiment as frozen  # noqa: E402

HERE = Path(__file__).resolve().parent
BOOTSTRAP_SEED = 20260810
BOOTSTRAP_DRAWS = 10000

CACHED_GENERIC_RMS = 0.014398754762932663
CACHED_NOLADDER_RATIO = 0.9114717897200765
CACHED_NOLADDER_RMS = 0.01312405877351071


def exact_theta(instance):
    alpha = np.asarray(instance.alpha_trajectory[-1], dtype=np.float64)
    var = np.diagonal(instance.covariances, axis1=1, axis2=2)
    ell = 0.5 * np.log(var)
    return alpha, ell


def exact_geometry(instance):
    """Distances under the exact observable-Jacobian local pullback metric."""
    alpha, ell = exact_theta(instance)
    sigma = np.exp(ell)
    Phi = frozen.normal_cdf(alpha)
    pdf = frozen.normal_pdf(alpha)
    h = alpha * Phi + pdf
    a = sigma * Phi          # d o / d alpha,  [K, d]
    b = sigma * h            # d o / d ell,    [K, d]

    raw = np.concatenate([alpha, ell], axis=1)
    standardized, _, scale = frozen.robust_standardize(raw)
    s_alpha = scale[: frozen.DIM]
    s_ell = scale[frozen.DIM :]

    # ridge, mirroring the frozen convention trace(S G S) / (100 * p_dim)
    p_dim = 2 * frozen.DIM
    trace_k = np.sum(a * a * (s_alpha**2)[None, :], axis=1) + np.sum(
        b * b * (s_ell**2)[None, :], axis=1
    )
    delta = float(np.mean(trace_k)) / (100.0 * p_dim)

    d_alpha = alpha[:, None, :] - alpha[None, :, :]
    d_ell = ell[:, None, :] - ell[None, :, :]
    # Q_i(Delta_ij) = sum_c (a_ic dalpha_ijc + b_ic dell_ijc)^2
    proj_i = a[:, None, :] * d_alpha + b[:, None, :] * d_ell
    q_i = np.sum(proj_i * proj_i, axis=2)
    pullback = 0.5 * (q_i + q_i.T)

    d_std = standardized[:, None, :] - standardized[None, :, :]
    ridge_term = delta * np.sum(d_std * d_std, axis=2)

    dist = pullback + ridge_term
    dist = np.maximum(0.0, 0.5 * (dist + dist.T))
    np.fill_diagonal(dist, 0.0)
    stats = {
        "jacobian_regularizer": delta,
        "mean_component_metric_trace": float(np.mean(trace_k)),
    }
    return dist, stats


def evaluate_exact(instance):
    distance, stats = exact_geometry(instance)
    transport = frozen.entropic_transport(distance, instance.weights)
    decoded = frozen.decode_total_moments(
        instance.means, instance.covariances, instance.weights, transport.assignment
    )
    error = decoded.observable - instance.exact_observable
    rms = math.sqrt(float(np.mean(error * error)))
    return frozen.MethodResult(
        method="jacobian_exact_psi",
        prediction=decoded.observable,
        rms_error=rms,
        transport=transport,
        decode=decoded,
        extras=stats,
    )


ARMS = ("generic_q3", "jacobian_maxent", "jacobian_exact_psi")


def evaluate(instance, arm):
    if arm == "jacobian_exact_psi":
        return evaluate_exact(instance)
    return frozen.evaluate_method(instance, arm)


def pooled_ratio(sq_by_arm, idx, num, den):
    a = math.sqrt(float(np.mean(np.stack([sq_by_arm[num][i] for i in idx]))))
    b = math.sqrt(float(np.mean(np.stack([sq_by_arm[den][i] for i in idx]))))
    return a / b


def main() -> int:
    seeds = list(frozen.VALIDATION_SEEDS)
    sq = {arm: [] for arm in ARMS}
    unit_rms = {arm: [] for arm in ARMS}
    per_unit = []
    maxima = {
        "mean_residual": 0.0,
        "covariance_residual": 0.0,
        "negative_eigenvalue_magnitude": 0.0,
        "repair_magnitude": 0.0,
        "transport_marginal_residual": 0.0,
        "bin_mass_residual": 0.0,
    }
    min_hard_rank = math.inf
    all_unambiguous = True
    all_finite = True
    sinkhorn_iterations = []
    first_instance = None

    for seed in seeds:
        inst = frozen.make_instance(seed)
        if first_instance is None:
            first_instance = inst
        rec = {"seed": seed}
        for arm in ARMS:
            res = evaluate(inst, arm)
            err = res.prediction - inst.exact_observable
            sq[arm].append(err * err)
            unit_rms[arm].append(res.rms_error)
            rec[arm] = res.rms_error
            if arm == "jacobian_exact_psi":
                maxima["mean_residual"] = max(
                    maxima["mean_residual"], res.decode.global_mean_residual
                )
                maxima["covariance_residual"] = max(
                    maxima["covariance_residual"], res.decode.global_covariance_residual
                )
                maxima["negative_eigenvalue_magnitude"] = max(
                    maxima["negative_eigenvalue_magnitude"],
                    max(0.0, -res.decode.minimum_bin_covariance_eigenvalue),
                )
                maxima["repair_magnitude"] = max(
                    maxima["repair_magnitude"], res.decode.repair_magnitude
                )
                maxima["transport_marginal_residual"] = max(
                    maxima["transport_marginal_residual"],
                    res.transport.marginal_residual,
                )
                maxima["bin_mass_residual"] = max(
                    maxima["bin_mass_residual"],
                    float(np.max(np.abs(res.decode.bin_masses - 1.0 / 3.0))),
                )
                min_hard_rank = min(min_hard_rank, res.transport.hard_rank_effective)
                all_unambiguous = all_unambiguous and res.transport.medoids.unambiguous
                all_finite = all_finite and bool(
                    np.all(np.isfinite(res.prediction)) and np.isfinite(res.rms_error)
                )
                sinkhorn_iterations.append(int(res.transport.iterations))
                rec["exact_psi_regularizer"] = res.extras["jacobian_regularizer"]
        per_unit.append(rec)

    agg_rms = {
        arm: math.sqrt(float(np.mean(np.stack(sq[arm])))) for arm in ARMS
    }
    ratios = {arm: agg_rms[arm] / agg_rms["generic_q3"] for arm in ARMS}
    u = {arm: np.asarray(unit_rms[arm], dtype=np.float64) for arm in ARMS}
    wins = {
        "exact_psi_vs_generic": int(np.sum(u["jacobian_exact_psi"] < u["generic_q3"])),
        "exact_psi_vs_surrogate_noladder": int(
            np.sum(u["jacobian_exact_psi"] < u["jacobian_maxent"])
        ),
        "surrogate_noladder_vs_generic": int(
            np.sum(u["jacobian_maxent"] < u["generic_q3"])
        ),
    }

    # ---- equivariance / structural symmetry for the new arm ----
    rng = np.random.default_rng(77182026)
    comp_order = rng.permutation(frozen.K_COMPONENTS)
    coord_order = np.array([2, 5, 1, 4, 0, 3], dtype=np.int64)
    base = evaluate_exact(first_instance)
    comp = evaluate_exact(frozen.permute_components(first_instance, comp_order))
    coord = evaluate_exact(frozen.permute_coordinates(first_instance, coord_order))
    comp_resid = float(np.max(np.abs(base.prediction - comp.prediction)))
    coord_resid = float(np.max(np.abs(base.prediction[coord_order] - coord.prediction)))

    # positive coordinate-gauge covariance is not claimed here (the judge's own
    # independent test); only the permutation gauge from the frozen gate is run.

    # ---- bootstrap and sign test ----
    boot = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(seeds)
    ratio_exact_draws = np.empty(BOOTSTRAP_DRAWS)
    ratio_surr_draws = np.empty(BOOTSTRAP_DRAWS)
    diff_draws = np.empty(BOOTSTRAP_DRAWS)
    for t in range(BOOTSTRAP_DRAWS):
        idx = boot.integers(0, n, size=n)
        re_ = pooled_ratio(sq, idx, "jacobian_exact_psi", "generic_q3")
        rs_ = pooled_ratio(sq, idx, "jacobian_maxent", "generic_q3")
        ratio_exact_draws[t] = re_
        ratio_surr_draws[t] = rs_
        diff_draws[t] = re_ - rs_
    ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

    k_exact_better = wins["exact_psi_vs_surrogate_noladder"]
    # exact two-sided binomial sign test, p = 0.5
    from math import comb

    tail = sum(comb(n, i) for i in range(0, min(k_exact_better, n - k_exact_better) + 1))
    sign_p_two_sided = min(1.0, 2.0 * tail / (2.0**n))

    repro = {
        "generic_rms_cached": CACHED_GENERIC_RMS,
        "generic_rms_recomputed": agg_rms["generic_q3"],
        "generic_rel_diff": abs(agg_rms["generic_q3"] - CACHED_GENERIC_RMS)
        / CACHED_GENERIC_RMS,
        "noladder_ratio_cached": CACHED_NOLADDER_RATIO,
        "noladder_ratio_recomputed": ratios["jacobian_maxent"],
        "noladder_ratio_rel_diff": abs(ratios["jacobian_maxent"] - CACHED_NOLADDER_RATIO)
        / CACHED_NOLADDER_RATIO,
        "noladder_rms_cached": CACHED_NOLADDER_RMS,
        "noladder_rms_recomputed": agg_rms["jacobian_maxent"],
        "noladder_wins_cached": 32,
        "noladder_wins_recomputed": wins["surrogate_noladder_vs_generic"],
    }

    gates = {
        "G2_REPRO": bool(
            repro["generic_rel_diff"] <= 1e-12
            and repro["noladder_ratio_rel_diff"] <= 1e-12
            and repro["noladder_wins_recomputed"] == 32
        ),
        "G2_PRIMARY_ratio_le_0_80": bool(ratios["jacobian_exact_psi"] <= 0.80),
        "G2_PRIMARY_wins_ge_24_of_32": bool(wins["exact_psi_vs_generic"] >= 24),
        "G2_MATERIALITY_ratio_lt_0_8942": bool(ratios["jacobian_exact_psi"] < 0.8942),
        "G2_STRUCT_mean_moment_exact": bool(maxima["mean_residual"] <= 2e-10),
        "G2_STRUCT_covariance_moment_exact": bool(maxima["covariance_residual"] <= 2e-10),
        "G2_STRUCT_psd": bool(maxima["negative_eigenvalue_magnitude"] <= 2e-10),
        "G2_STRUCT_transport_marginals": bool(
            maxima["transport_marginal_residual"] <= 2e-10
        ),
        "G2_STRUCT_balanced_bin_masses": bool(maxima["bin_mass_residual"] <= 2e-8),
        "G2_STRUCT_assignment_noncollapse": bool(min_hard_rank >= 2.5),
        "G2_STRUCT_medoids_unambiguous": bool(all_unambiguous),
        "G2_STRUCT_component_permutation": bool(comp_resid <= 2e-10),
        "G2_STRUCT_coordinate_gauge": bool(coord_resid <= 2e-10),
        "G2_STRUCT_all_finite": bool(all_finite),
    }
    primary = gates["G2_PRIMARY_ratio_le_0_80"] and gates["G2_PRIMARY_wins_ge_24_of_32"]
    structural = all(v for k, v in gates.items() if k.startswith("G2_STRUCT"))
    if not gates["G2_REPRO"]:
        verdict = "INCONCLUSIVE"
    elif primary and gates["G2_MATERIALITY_ratio_lt_0_8942"] and structural:
        verdict = "REVIVED_PASS"
    elif gates["G2_MATERIALITY_ratio_lt_0_8942"] and not primary:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "KILL_CONFIRMED"

    out = {
        "schema": "gm-ecn-psi-step2-exact-psi-swap-v1",
        "arms": list(ARMS),
        "seeds": seeds,
        "aggregate_rms": agg_rms,
        "aggregate_ratio_vs_generic": ratios,
        "wins": wins,
        "bootstrap": {
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "exact_psi_ratio_ci95": ci(ratio_exact_draws),
            "surrogate_noladder_ratio_ci95": ci(ratio_surr_draws),
            "paired_ratio_difference_ci95": ci(diff_draws),
            "paired_ratio_difference_point": ratios["jacobian_exact_psi"]
            - ratios["jacobian_maxent"],
        },
        "paired_sign_test_exact_vs_surrogate": {
            "exact_better_on_units": k_exact_better,
            "n_units": n,
            "two_sided_p": sign_p_two_sided,
        },
        "unit_ratio_summaries": {
            arm: {
                "mean_unit_ratio": float(np.mean(u[arm] / u["generic_q3"])),
                "median_unit_ratio": float(np.median(u[arm] / u["generic_q3"])),
            }
            for arm in ARMS
        },
        "maxima_exact_psi": maxima,
        "minimum_hard_assignment_rank_effective_exact_psi": min_hard_rank,
        "equivariance_exact_psi": {
            "component_permutation_residual": comp_resid,
            "coordinate_gauge_residual": coord_resid,
        },
        "sinkhorn_iterations_exact_psi": {
            "min": int(min(sinkhorn_iterations)),
            "max": int(max(sinkhorn_iterations)),
        },
        "reproduction_of_frozen_cache": repro,
        "gates": gates,
        "verdict": verdict,
        "per_unit_rms": per_unit,
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__},
    }
    (HERE / "step2_results.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = {
        k: out[k]
        for k in (
            "aggregate_ratio_vs_generic",
            "wins",
            "bootstrap",
            "paired_sign_test_exact_vs_surrogate",
            "reproduction_of_frozen_cache",
            "gates",
            "verdict",
        )
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
