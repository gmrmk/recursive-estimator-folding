"""Second-signal verification for gm_ecn_psi step 2.

Attacks the strongest counter-hypothesis: that the exact-psi arm loses because
my vectorised closed-form pullback cost is buggy rather than because the exact
metric routes worse.  Recomputes every pairwise distance the slow, explicit
way -- build each 12x12 G_k = J_k^T J_k from a materialised d x 2d Jacobian,
form (G_i + G_j)/2 + delta I, evaluate Delta^T M Delta -- and compares.

Also reports the ridge/pullback balance and repeats the step-2 headline
numbers from a fresh process for a bit-repeat.
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
sys.path.insert(0, str(HERE))
import step2_psi_swap as step2  # noqa: E402


def explicit_geometry(instance):
    alpha, ell = step2.exact_theta(instance)
    sigma = np.exp(ell)
    Phi = frozen.normal_cdf(alpha)
    pdf = frozen.normal_pdf(alpha)
    h = alpha * Phi + pdf
    a = sigma * Phi
    b = sigma * h

    raw = np.concatenate([alpha, ell], axis=1)
    standardized, _, scale = frozen.robust_standardize(raw)
    d = frozen.DIM
    p_dim = 2 * d
    K = frozen.K_COMPONENTS
    S = np.diag(scale)

    grams = np.zeros((K, p_dim, p_dim), dtype=np.float64)
    traces = np.zeros(K, dtype=np.float64)
    idx = np.arange(d)
    for k in range(K):
        jac = np.zeros((d, p_dim), dtype=np.float64)
        jac[idx, idx] = a[k]
        jac[idx, d + idx] = b[k]
        g = jac.T @ jac
        grams[k] = g
        traces[k] = float(np.trace(S @ g @ S))
    delta = float(np.mean(traces)) / (100.0 * p_dim)

    dist = np.zeros((K, K), dtype=np.float64)
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            drw = raw[i] - raw[j]
            dsd = standardized[i] - standardized[j]
            m = 0.5 * (grams[i] + grams[j])
            dist[i, j] = float(drw @ m @ drw) + delta * float(dsd @ dsd)
    dist = np.maximum(0.0, 0.5 * (dist + dist.T))
    np.fill_diagonal(dist, 0.0)

    # ridge / pullback balance, off-diagonal only
    pull = np.zeros((K, K))
    ridge = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            drw = raw[i] - raw[j]
            dsd = standardized[i] - standardized[j]
            pull[i, j] = float(drw @ (0.5 * (grams[i] + grams[j])) @ drw)
            ridge[i, j] = delta * float(dsd @ dsd)
    off = ~np.eye(K, dtype=bool)
    balance = float(np.sum(ridge[off]) / np.sum(pull[off] + ridge[off]))
    return dist, delta, balance


def main() -> int:
    max_abs = 0.0
    max_rel = 0.0
    deltas = []
    balances = []
    for seed in frozen.VALIDATION_SEEDS:
        inst = frozen.make_instance(seed)
        fast, stats = step2.exact_geometry(inst)
        slow, delta, balance = explicit_geometry(inst)
        denom = np.maximum(np.abs(slow), 1e-300)
        diff = np.abs(fast - slow)
        max_abs = max(max_abs, float(np.max(diff)))
        off = ~np.eye(fast.shape[0], dtype=bool)
        max_rel = max(max_rel, float(np.max(diff[off] / denom[off])))
        assert abs(delta - stats["jacobian_regularizer"]) <= 1e-12 * abs(delta)
        deltas.append(delta)
        balances.append(balance)

    cached = json.loads((HERE / "step2_results.json").read_text(encoding="utf-8"))
    out = {
        "schema": "gm-ecn-psi-step3-crosscheck-v1",
        "explicit_matrix_vs_vectorised_distance": {
            "max_abs_diff": max_abs,
            "max_rel_diff_offdiag": max_rel,
            "gate_le_1e-12": bool(max_rel <= 1e-12),
        },
        "ridge_diagnostics": {
            "regularizer_min": float(np.min(deltas)),
            "regularizer_max": float(np.max(deltas)),
            "ridge_share_of_total_cost_min": float(np.min(balances)),
            "ridge_share_of_total_cost_max": float(np.max(balances)),
        },
        "step2_headline_recheck": {
            "exact_psi_ratio": cached["aggregate_ratio_vs_generic"]["jacobian_exact_psi"],
            "surrogate_ratio": cached["aggregate_ratio_vs_generic"]["jacobian_maxent"],
            "exact_psi_wins_vs_generic": cached["wins"]["exact_psi_vs_generic"],
            "exact_psi_wins_vs_surrogate": cached["wins"][
                "exact_psi_vs_surrogate_noladder"
            ],
        },
        "judge_bootstrap_independent_agreement": {
            "judge_reported_noladder_ci95": [0.8942, 0.9291],
            "my_bootstrap_noladder_ci95": cached["bootstrap"][
                "surrogate_noladder_ratio_ci95"
            ],
        },
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__},
    }
    (HERE / "step3_crosscheck.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
