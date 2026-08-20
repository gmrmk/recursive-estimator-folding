"""m207b: what the owner's floor-semantics change actually buys the spine.

Owner ruling 2026-08-18: M198 floor semantics change from ABSOLUTE to RELATIVE
is authorized (the gm_m179_m199 reopening premise). m207 established the wall
is intermittent stochastic near-singularity with a stable trace, so a relative
floor can only help if the near-singular visits stay above the relative bar.
This cell measures the per-network floor-crossing probability under BOTH
semantics at real sample size, and converts each to the quantity the campaign
actually cares about: the probability a full 24-network production sweep hits
the fail-closed guard at least once.

Control arm (mechanism isolation): the identical congruence chain WITHOUT the
ReLU covariance map. If the ReLU map is the restorer (m207's revised
mechanism), the control arm's conditioning must spread without recovery and
its crossing rate must exceed the main arm's.

Diagnostic only; zero charge against H; synthetic seeded He nets of the
challenge family at production width.
"""

from __future__ import annotations

import json
import math
import os
import time

import numpy as np

D = 256
WIDTH = 256
DEPTH = 32
FLOOR = 1e-12                       # same numeric bar under both semantics
SWEEP_NETS = 24
SMOKE = os.environ.get("M207B_SMOKE") == "1"
BASE_SEEDS = (777000999,) if SMOKE else (20260825,)
N_REPS = 10 if SMOKE else 200
N_CTRL = 5 if SMOKE else 40
METRIC_NAME = "relative_floor_crossing_fraction_w256"


def r6(x: float) -> float:
    return float(np.round(float(x), 6))


def relu_cov_map(C: np.ndarray) -> np.ndarray:
    diag = np.diag(C)
    s = np.sqrt(diag)
    outer = np.outer(s, s)
    rho = np.clip(C / outer, -1.0, 1.0)
    k = (np.sqrt(np.maximum(1.0 - rho * rho, 0.0))
         + (math.pi - np.arccos(rho)) * rho) / (2.0 * math.pi)
    V = outer * k
    return 0.5 * (V + V.T)


def run_rep(rng: np.random.Generator, use_relu: bool) -> dict:
    """One recurrence pass; returns per-rep extremes and crossing flags."""
    V = np.eye(D)
    w_in = D
    max_log_kappa = 0.0
    crossed_rel = crossed_abs = False
    argmax_layer = 0
    for l in range(1, DEPTH + 1):
        W = rng.normal(0.0, math.sqrt(2.0 / w_in), size=(WIDTH, w_in))
        w_in = WIDTH
        C = W @ V @ W.T
        C = 0.5 * (C + C.T)
        eig = np.linalg.eigvalsh(C)
        lo, hi = float(eig[0]), float(eig[-1])
        rel = lo / hi if hi > 0.0 else 0.0
        if rel < FLOOR or lo <= 0.0:
            crossed_rel = True
        if lo < FLOOR:
            crossed_abs = True
        lk = math.log10(hi / lo) if lo > 0.0 else 30.0
        if lk > max_log_kappa:
            max_log_kappa, argmax_layer = lk, l
        if use_relu:
            if float(np.min(np.diag(C))) <= 0.0:
                return {"max_log_kappa": 30.0, "argmax_layer": l,
                        "crossed_rel": True, "crossed_abs": True,
                        "died": True}
            V = relu_cov_map(C)
        else:
            V = C
    return {"max_log_kappa": r6(max_log_kappa), "argmax_layer": argmax_layer,
            "crossed_rel": crossed_rel, "crossed_abs": crossed_abs,
            "died": False}


def wilson_ci(k: int, n: int) -> tuple[float, float]:
    """95% Wilson interval for a binomial fraction."""
    if n == 0:
        return (0.0, 1.0)
    z = 1.959963984540054
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def sweep_risk(p: float) -> float:
    return 1.0 - (1.0 - p) ** SWEEP_NETS


def summarize(reps: list[dict]) -> dict:
    n = len(reps)
    k_rel = sum(r["crossed_rel"] for r in reps)
    k_abs = sum(r["crossed_abs"] for r in reps)
    lo_r, hi_r = wilson_ci(k_rel, n)
    lo_a, hi_a = wilson_ci(k_abs, n)
    kappas = sorted(r["max_log_kappa"] for r in reps)
    q = lambda f: r6(kappas[min(n - 1, int(f * n))])
    return {
        "n": n,
        "crossed_relative": k_rel,
        "crossed_absolute": k_abs,
        "p_relative": r6(k_rel / n),
        "p_relative_ci95": [r6(lo_r), r6(hi_r)],
        "p_absolute": r6(k_abs / n),
        "p_absolute_ci95": [r6(lo_a), r6(hi_a)],
        "sweep24_risk_relative": r6(sweep_risk(k_rel / n)),
        "sweep24_risk_relative_ci95": [r6(sweep_risk(lo_r)), r6(sweep_risk(hi_r))],
        "sweep24_risk_absolute": r6(sweep_risk(k_abs / n)),
        "max_log10_kappa_quantiles": {"q50": q(0.50), "q90": q(0.90),
                                      "q99": q(0.99), "max": kappas[-1]},
        "argmax_layer_histogram_octiles": [
            sum(1 for r in reps if (r["argmax_layer"] - 1) // 4 == b)
            for b in range(8)],
    }


def main() -> None:
    started = time.perf_counter()
    base = BASE_SEEDS[0]
    main_reps, ctrl_reps = [], []
    for i in range(N_REPS):
        rng = np.random.Generator(np.random.PCG64DXSM((base << 8) ^ i))
        main_reps.append(run_rep(rng, use_relu=True))
    for i in range(N_CTRL):
        rng = np.random.Generator(np.random.PCG64DXSM((base << 8) ^ (0xC0000 + i)))
        ctrl_reps.append(run_rep(rng, use_relu=False))

    main_sum = summarize(main_reps)
    ctrl_sum = summarize(ctrl_reps)

    print(json.dumps({
        "cell": "m207b_semantics",
        "smoke": SMOKE,
        METRIC_NAME: main_sum["p_relative"],
        "metric_semantics": "fraction of independent production-width networks whose zero-order covariance recurrence has, at ANY of the 32 layers, min_eig/max_eig below 1e-12 (or a nonpositive spectrum) -- the relative-semantics guard-fire probability per network",
        "main_arm_relu": main_sum,
        "control_arm_pure_congruence": ctrl_sum,
        "relu_map_is_restorer": bool(
            ctrl_sum["p_relative"] > main_sum["p_relative"]
            or ctrl_sum["max_log10_kappa_quantiles"]["q50"]
            > main_sum["max_log10_kappa_quantiles"]["q50"]),
        "floor": FLOOR,
        "sweep_nets": SWEEP_NETS,
        "config": {"d": D, "width": WIDTH, "depth": DEPTH,
                   "n_reps": N_REPS, "n_ctrl": N_CTRL,
                   "seeds": list(BASE_SEEDS)},
        "wall_seconds": r6(time.perf_counter() - started),
    }))


if __name__ == "__main__":
    main()
