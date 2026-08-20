"""Step 1 of the gm_ecn_psi cheapest falsifier.

Central-difference validation of the EXACT ReLU observable Jacobian in
theta = (alpha, ell = log sigma) coordinates, on every (alpha, ell) present in
the 32 frozen ECN synthetic states.  Gates G1A/G1B/G1C/G1D of PREDECLARATION.md.

The frozen ECN implementation is imported read-only and never modified.
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
import experiment as frozen  # noqa: E402  (frozen source, imported not edited)

HERE = Path(__file__).resolve().parent
REL_FLOOR = 1e-12
GATE_DERIV = 1e-6
GATE_OBS = 1e-10


def analytic_blocks(alpha: np.ndarray, ell: np.ndarray):
    sigma = np.exp(ell)
    Phi = frozen.normal_cdf(alpha)
    pdf = frozen.normal_pdf(alpha)
    h = alpha * Phi + pdf
    return sigma * Phi, sigma * h


def frozen_observable(alpha: np.ndarray, ell: np.ndarray) -> np.ndarray:
    sigma = np.exp(ell)
    return frozen.gaussian_relu_mean(sigma * alpha, sigma * sigma)


def gl_observable(alpha: np.ndarray, ell: np.ndarray, nodes: int = 800) -> np.ndarray:
    """E[relu(z)] by Gauss-Legendre quadrature: erf-free, independent of Phi."""
    x, w = np.polynomial.legendre.leggauss(nodes)
    sigma = np.exp(ell)
    mu = sigma * alpha
    upper = np.maximum(mu + 16.0 * sigma, 1e-300)
    flat_mu = mu.ravel()
    flat_s = sigma.ravel()
    flat_u = upper.ravel()
    half = 0.5 * flat_u
    z = half[:, None] * (x[None, :] + 1.0)
    t = (z - flat_mu[:, None]) / flat_s[:, None]
    dens = np.exp(-0.5 * t * t) / (flat_s[:, None] * math.sqrt(2.0 * math.pi))
    out = half * np.einsum("nj,j->n", z * dens, w)
    return out.reshape(alpha.shape)


def central_diff(fun, alpha, ell, axis, h):
    if axis == "alpha":
        return (fun(alpha + h, ell) - fun(alpha - h, ell)) / (2.0 * h)
    return (fun(alpha, ell + h) - fun(alpha, ell - h)) / (2.0 * h)


def relerr(num, exact):
    return float(np.max(np.abs(num - exact) / (np.abs(exact) + REL_FLOOR)))


def main() -> int:
    alphas, ells = [], []
    for seed in frozen.VALIDATION_SEEDS:
        inst = frozen.make_instance(seed)
        alphas.append(inst.alpha_trajectory[-1])
        var = np.diagonal(inst.covariances, axis1=1, axis2=2)
        ells.append(0.5 * np.log(var))
    alpha = np.concatenate(alphas, axis=0)
    ell = np.concatenate(ells, axis=0)
    n_points = int(alpha.size)

    j_alpha, j_ell = analytic_blocks(alpha, ell)

    cd_a_h1 = central_diff(frozen_observable, alpha, ell, "alpha", 1e-5)
    cd_l_h1 = central_diff(frozen_observable, alpha, ell, "ell", 1e-5)
    cd_a_h2 = central_diff(frozen_observable, alpha, ell, "alpha", 5e-6)
    cd_l_h2 = central_diff(frozen_observable, alpha, ell, "ell", 5e-6)

    g1a = relerr(cd_a_h1, j_alpha)
    g1b = relerr(cd_l_h1, j_ell)
    g1d_a = relerr(cd_a_h2, j_alpha)
    g1d_b = relerr(cd_l_h2, j_ell)

    obs_frozen = frozen_observable(alpha, ell)
    obs_gl = gl_observable(alpha, ell)
    g1c_obs = relerr(obs_gl, obs_frozen)
    gl_cd_a = central_diff(gl_observable, alpha, ell, "alpha", 1e-5)
    gl_cd_l = central_diff(gl_observable, alpha, ell, "ell", 1e-5)
    g1c_a = relerr(gl_cd_a, j_alpha)
    g1c_b = relerr(gl_cd_l, j_ell)

    # third, purely algebraic cross-check: h'(alpha) == Phi(alpha)
    h_of = lambda a: a * frozen.normal_cdf(a) + frozen.normal_pdf(a)
    hp = (h_of(alpha + 1e-5) - h_of(alpha - 1e-5)) / 2e-5
    g1e = relerr(hp, frozen.normal_cdf(alpha))

    gates = {
        "G1A_alpha_block_cd_h1e-5": g1a <= GATE_DERIV,
        "G1B_ell_block_cd_h1e-5": g1b <= GATE_DERIV,
        "G1C_gl_observable_matches_frozen": g1c_obs <= GATE_OBS,
        "G1C_gl_cd_alpha_block": g1c_a <= GATE_DERIV,
        "G1C_gl_cd_ell_block": g1c_b <= GATE_DERIV,
        "G1D_step_halving_alpha": g1d_a <= GATE_DERIV,
        "G1D_step_halving_ell": g1d_b <= GATE_DERIV,
    }
    out = {
        "schema": "gm-ecn-psi-step1-jacobian-cd-v1",
        "n_theta_points": n_points,
        "n_derivative_entries": 2 * n_points,
        "alpha_range": [float(alpha.min()), float(alpha.max())],
        "ell_range": [float(ell.min()), float(ell.max())],
        "sigma_range": [float(np.exp(ell).min()), float(np.exp(ell).max())],
        "max_rel_err": {
            "G1A_alpha_block_h1e-5": g1a,
            "G1B_ell_block_h1e-5": g1b,
            "G1D_alpha_block_h5e-6": g1d_a,
            "G1D_ell_block_h5e-6": g1d_b,
            "G1C_gl_vs_frozen_observable": g1c_obs,
            "G1C_gl_cd_alpha_block": g1c_a,
            "G1C_gl_cd_ell_block": g1c_b,
            "identity_hprime_equals_Phi": g1e,
        },
        "gate_thresholds": {"derivative_rel": GATE_DERIV, "observable_rel": GATE_OBS},
        "gates": gates,
        "step1_pass": bool(all(gates.values())),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
        },
    }
    (HERE / "step1_results.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
