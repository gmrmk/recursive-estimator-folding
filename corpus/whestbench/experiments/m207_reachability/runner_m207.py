"""m207: closure certificate on the M198 reachability wall.

The exact-control spine is blocked twice: (A) the missing layer-bound
fourth-order provider (M205), and (B) gm_m179_m199 KILL_REACHABILITY -- at
width 256 the zero-order pre-ReLU covariance recurrence crosses the M198
variance floor at layer ~12/32 and goes strictly negative shortly after, so a
perfect provider still cannot run past layer 12. B is upstream of A. This
cell settles B: is the wall CONDITIONING (trace-normalized spectrum collapses;
structural; spine closure certified) or SCALE (absolute trace decays under an
absolute floor while the normalized spectrum stays healthy; repairable by an
exact gauge)?

The discriminator is lawful by exactness, not tolerance: the recurrence
C_l = W_l V_{l-1} W_l^T, V_l = R(C_l) is positively homogeneous (R(sC) = sR(C)
for s > 0 because relu is degree-1 homogeneous, and the congruence is linear
in V), so a per-layer scalar trace gauge with the factor carried in the log is
EXACTLY value-preserving -- a gauge, not a clip/floor/ridge (which m179's
kill_condition bans). Both passes are run: absolute (reproducing the wall as
recorded) and gauge-rescaled (roundoff can never manufacture negatives from
scale decay).

Second signals, both computed in-run: (1) Cholesky success/failure on the
normalized covariance, independent of eigvalsh; (2) the width-scaling
fingerprint -- Lyapunov spread of repeated Gaussian congruence grows with
width, so the floor-crossing layer must move LATER as width drops 256 -> 128
-> 64; a floating-point artifact has no reason to track that law.

Diagnostic only: nothing is added to the champion; zero charge against H.
Synthetic seeded He nets of the challenge family (the wall is claimed as a
family property, not a property of one archived net).
"""

from __future__ import annotations

import json
import math
import os
import time

import numpy as np

D = 256
DEPTH = 32
WIDTHS = (64, 128, 256)
FLOOR = 1e-12                       # M198 VARIANCE_FLOOR, absolute
SMOKE = os.environ.get("M207_SMOKE") == "1"
SEEDS = (555000111,) if SMOKE else (20260823, 20260824)
METRIC_NAME = "log10_kappa12_norm_w256_rep0"
METRIC_CAP = 30.0                   # rescaled recursion dead or lambda_min <= 0


def r6(x: float) -> float:
    return float(np.round(float(x), 6))


def make_net(rng: np.random.Generator, width: int) -> list[np.ndarray]:
    ws = [rng.normal(0.0, math.sqrt(2.0 / D), size=(width, D))]
    for _ in range(DEPTH - 1):
        ws.append(rng.normal(0.0, math.sqrt(2.0 / width), size=(width, width)))
    return ws


def relu_cov_map(C: np.ndarray) -> np.ndarray:
    """Post-ReLU covariance of N(0, C) -- the first-order arc-cosine map.

    V_ij = s_i s_j * (sqrt(1-rho^2) + (pi - arccos(rho)) rho) / (2 pi),
    rho = C_ij / (s_i s_j). Diagonal check: rho=1 -> V_ii = C_ii / 2 exactly.
    Requires strictly positive diagonal; the caller handles death.
    """
    diag = np.diag(C).copy()
    s = np.sqrt(diag)
    outer = np.outer(s, s)
    rho = np.clip(C / outer, -1.0, 1.0)
    k = (np.sqrt(np.maximum(1.0 - rho * rho, 0.0))
         + (math.pi - np.arccos(rho)) * rho) / (2.0 * math.pi)
    V = outer * k
    return 0.5 * (V + V.T)


def run_pass(weights: list[np.ndarray], rescale: bool) -> dict:
    """The zero-order covariance recurrence, absolute or trace-gauge-rescaled."""
    width = weights[0].shape[0]
    V = np.eye(D)
    log_gauge = 0.0
    layers = []
    death = None
    for l, W in enumerate(weights, start=1):
        C = W @ V @ W.T
        C = 0.5 * (C + C.T)
        if rescale:
            tr = float(np.trace(C))
            if not math.isfinite(tr) or tr <= 0.0:
                death = {"layer": l, "reason": "nonpositive trace in rescaled pass"}
                break
            log_gauge += math.log10(tr / width)
            C = C * (width / tr)
        eig = np.linalg.eigvalsh(C)
        lo, hi = float(eig[0]), float(eig[-1])
        tr = float(np.trace(C))
        try:
            np.linalg.cholesky(C)
            chol_ok = True
        except np.linalg.LinAlgError:
            chol_ok = False
        layers.append({"layer": l, "min_eig": lo, "max_eig": hi,
                       "trace": tr, "log10_gauge": r6(log_gauge),
                       "cholesky_ok": chol_ok})
        if float(np.min(np.diag(C))) <= 0.0:
            death = {"layer": l, "reason": "nonpositive diagonal entering relu map"}
            break
        V = relu_cov_map(C)
    first_floor = next((e["layer"] for e in layers if e["min_eig"] < FLOOR), None)
    first_neg = next((e["layer"] for e in layers if e["min_eig"] < 0.0), None)
    return {"layers": layers, "death": death,
            "first_floor_layer": first_floor, "first_neg_layer": first_neg}


def kappa_log10(entry: dict | None) -> float:
    if entry is None or entry["min_eig"] <= 0.0:
        return METRIC_CAP
    return min(math.log10(entry["max_eig"] / entry["min_eig"]), METRIC_CAP)


def main() -> None:
    started = time.perf_counter()
    out_widths = {}
    metric = None
    for width in WIDTHS:
        reps = []
        for rep, seed in enumerate(SEEDS):
            rng = np.random.Generator(np.random.PCG64DXSM(seed ^ (width * 2654435761)))
            weights = make_net(rng, width)
            absolute = run_pass(weights, rescale=False)
            rescaled = run_pass(weights, rescale=True)
            l12 = next((e for e in rescaled["layers"] if e["layer"] == 12), None)
            l32 = next((e for e in rescaled["layers"] if e["layer"] == DEPTH), None)
            rep_out = {
                "rep": rep, "seed": seed,
                "abs_first_floor_layer": absolute["first_floor_layer"],
                "abs_first_neg_layer": absolute["first_neg_layer"],
                "abs_death": absolute["death"],
                "abs_trace_by_8": [r6(e["trace"]) for e in absolute["layers"][:8]],
                "resc_death": rescaled["death"],
                "resc_log10_kappa12": r6(kappa_log10(l12)),
                "resc_log10_kappa32": r6(kappa_log10(l32)),
                "resc_min_eig12": (l12 and l12["min_eig"]),
                "resc_first_neg_layer": rescaled["first_neg_layer"],
                "resc_cholesky12_ok": (l12 and l12["cholesky_ok"]),
                "resc_gauge_log10_at_end": (rescaled["layers"]
                                            and rescaled["layers"][-1]["log10_gauge"]),
                "resc_kappa_profile": [r6(kappa_log10(e)) for e in rescaled["layers"]],
            }
            reps.append(rep_out)
            if width == 256 and rep == 0:
                metric = r6(kappa_log10(l12))
        out_widths[str(width)] = reps

    fingerprint = {str(w): [r["abs_first_floor_layer"] for r in out_widths[str(w)]]
                   for w in WIDTHS}
    f0 = [fingerprint[str(w)][0] for w in WIDTHS if fingerprint[str(w)][0]]
    fingerprint_monotone = bool(len(f0) == len(WIDTHS)
                                and all(a >= b for a, b in zip(f0, f0[1:])))
    # width-scaling law on conditioning itself (works even when no rep crosses
    # the absolute floor): Lyapunov spread grows with width, so kappa12 must
    # rise 64 -> 128 -> 256 in every rep.
    kappa_by_width = {str(w): [r["resc_log10_kappa12"] for r in out_widths[str(w)]]
                      for w in WIDTHS}
    kappa_monotone = bool(all(
        kappa_by_width[str(a)][i] < kappa_by_width[str(b)][i]
        for a, b in zip(WIDTHS, WIDTHS[1:]) for i in range(len(SEEDS))))

    print(json.dumps({
        "cell": "m207_reachability",
        "smoke": SMOKE,
        METRIC_NAME: metric,
        "metric_semantics": "log10 condition number of the trace-gauge-rescaled pre-ReLU covariance at layer 12, width 256, rep 0; capped when the spectrum is nonpositive or the rescaled recursion dies",
        "branch_view": ("A_CLOSURE_CONDITIONING" if metric is not None and metric >= 12.0
                        else "B_REPAIRABLE_SCALE" if metric is not None and metric <= 10.0
                        else "C_AMBIGUOUS"),
        "widths": out_widths,
        "width_fingerprint_first_floor_layers": fingerprint,
        "fingerprint_monotone_later_as_width_drops": fingerprint_monotone,
        "kappa12_by_width": kappa_by_width,
        "kappa12_monotone_rising_with_width": kappa_monotone,
        "floor": FLOOR,
        "config": {"d": D, "depth": DEPTH, "widths": list(WIDTHS),
                   "seeds": list(SEEDS)},
        "wall_seconds": r6(time.perf_counter() - started),
    }))


if __name__ == "__main__":
    main()
