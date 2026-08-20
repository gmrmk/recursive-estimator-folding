"""N5 (predeclared): does the multilevel control have headroom beyond the
champion's first-layer control? The cheapest falsifier of the VISION
(multilevel Doob control variate).

MECHANISM: the champion already corrects the LAYER-1 sampling residual by
propagating it through the analytic mean-tangent (base_estimator delta loop).
The vision claims correcting EVERY layer's residual (multilevel) cuts variance
further. Test: on a small generated net, for M batches record the per-layer
sampled residual r_l = (batch post-ReLU mean at l) - (analytic diagonal mu_l),
propagate each r_l through the analytic mean-tangent from l to the output to get
a predictor p_l of the final error, and regress the true final error on the
predictors. R2 using p_1 alone = the champion's layer-1 capture; R2 using all
{p_l} = the multilevel upper bound. Their gap = the headroom.

PREDICTION: if the v-lever is TAPPED (ultrathink-2), R2_all ~= R2_layer1 (later
residuals are just propagated layer-1 noise). If the VISION is right, R2_all >>
R2_layer1. The oracle "4x v-cut" corresponds to
(1-R2_all)/(1-R2_layer1) <= 0.25.

KILL/DISPOSITION: this is a first-order (mean-tangent, diagonal) upper bound; a
positive result is necessary-not-sufficient (the real control is gated at M172),
a null result strongly caps the multilevel headroom. Report R2 with the caveat.

Response-free: generated net, own MC truth. No challenge data.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N, DEPTH = 24, 8
INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def gen(seed):
    rng = np.random.default_rng(seed)
    g = math.sqrt(2.0 / N)
    return [rng.standard_normal((N, N)) * g for _ in range(DEPTH)]


def phi(x):
    return INV_SQRT_2PI * np.exp(-0.5 * x * x)


def Phi(x):
    from math import erf
    vf = np.vectorize(lambda t: 0.5 * (1.0 + erf(t / math.sqrt(2.0))))
    return vf(x)


def diagonal_pass(weights):
    """Analytic diagonal Gaussian moments: returns per-layer (mu_l, sigma_l,
    firing_l = Phi(alpha_l)) for the mean-tangent."""
    mu = np.zeros(N)
    var = np.ones(N)
    mus, sigmas, firings = [], [], []
    for W in weights:
        mu_pre = mu @ W
        var_pre = var @ (W * W)
        sigma = np.sqrt(np.maximum(var_pre, 1e-12))
        alpha = mu_pre / sigma
        f = Phi(alpha)
        mu = mu_pre * f + sigma * phi(alpha)
        second = (var_pre + mu_pre * mu_pre) * f + mu_pre * sigma * phi(alpha)
        var = np.maximum(second - mu * mu, 0.0)
        mus.append(mu.copy()); sigmas.append(sigma.copy()); firings.append(f.copy())
    return mus, sigmas, firings


def forward_layer_means(weights, X):
    """Return per-layer post-ReLU sample means for a batch X (rows = samples)."""
    x = X
    means = []
    for W in weights:
        x = np.maximum(x @ W, 0.0)
        means.append(x.mean(axis=0))
    return means


def propagate_tangent(weights, firings, r_l, l):
    """Propagate a mean-perturbation r_l injected at layer l forward to the
    output via the analytic mean-tangent d E[ReLU]/d mu = firing."""
    delta = r_l.copy()
    for k in range(l, DEPTH - 1):
        delta = firings[k + 1] * (delta @ weights[k + 1])
    return delta  # contribution to the final (layer DEPTH-1) mean


def main():
    weights = gen(20260807)
    mus, sigmas, firings = diagonal_pass(weights)

    rng = np.random.default_rng(1)
    truth = forward_layer_means(weights, rng.standard_normal((4_000_000, N)))[-1]

    M, Nb = 600, 1024
    # predictors P[batch, layer, neuron], target E[batch, neuron]
    P = np.zeros((M, DEPTH, N))
    E = np.zeros((M, N))
    for b in range(M):
        Xb = np.random.default_rng(1000 + b).standard_normal((Nb, N))
        layer_means = forward_layer_means(weights, Xb)
        E[b] = layer_means[-1] - truth
        for l in range(DEPTH):
            r_l = layer_means[l] - mus[l]
            P[b, l] = propagate_tangent(weights, firings, r_l, l)

    # pooled regression across neurons: rows = M*N, cols = DEPTH predictors
    y = E.reshape(-1)
    def r2(cols):
        Xr = P[:, cols, :].transpose(0, 2, 1).reshape(-1, len(cols))
        beta, *_ = np.linalg.lstsq(Xr, y, rcond=None)
        resid = y - Xr @ beta
        return 1.0 - float(resid @ resid) / float(y @ y), beta.tolist()

    r2_l1, beta_l1 = r2([0])
    r2_l12, _ = r2([0, 1])
    r2_all, beta_all = r2(list(range(DEPTH)))
    var_ratio = (1 - r2_all) / max(1e-12, (1 - r2_l1))  # multilevel resid / layer1 resid

    out = {
        "net": {"width": N, "depth": DEPTH}, "batches": M, "batch_N": Nb,
        "R2_layer1_only": r2_l1,
        "R2_layers_1_2": r2_l12,
        "R2_all_layers": r2_all,
        "resid_var_ratio_multilevel_over_layer1": var_ratio,
        "implied_v_cut_factor": (1.0 / var_ratio) if var_ratio > 0 else None,
        "beta_layer1": beta_l1, "beta_all": beta_all,
        "caveat": ("first-order mean-tangent, diagonal closure, small net; a "
                   "positive result is necessary-not-sufficient (real control "
                   "gated at M172); a null strongly caps multilevel headroom"),
    }
    (HERE / "N5_RESULTS.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in (
        "R2_layer1_only", "R2_layers_1_2", "R2_all_layers",
        "resid_var_ratio_multilevel_over_layer1", "implied_v_cut_factor")}, indent=1))


if __name__ == "__main__":
    main()
