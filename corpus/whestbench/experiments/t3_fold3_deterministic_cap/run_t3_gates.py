"""T3 gate runner: G1 (cost-model calibration), G2 (adversarial worst case),
G3 (regression / bitwise no-op off the tail).  Synthetic nets only, single
process, no dataset/truth/scorer/submission access.  First KILL stops the run
and is written to t3_gate_results.json as the first broken link.
"""

from __future__ import annotations

import gc
import json
import math
import os
import sys
import time
from pathlib import Path

for _v in (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import flopscope as flops           # noqa: E402
import flopscope.numpy as fnp       # noqa: E402
import numpy as np                  # noqa: E402
from whestbench import SetupContext  # noqa: E402
from whestbench.domain import MLP    # noqa: E402

from capped_fold3 import Estimator as CappedEstimator  # noqa: E402
from estimator_n39936 import Estimator as UncappedEstimator  # noqa: E402

CAP = 244.8e9                # 0.9 * B (predeclared)
BUDGET_B = 272e9             # competition per-network budget (context only)
G1_WINDOW = (0.98, 1.06)
G1_SEEDS = (11, 22, 33)
SETUP_SEED_BASE = 2026080810
WIDTH, DEPTH = 256, 32
METER_BUDGET = 10**15        # non-binding; gates compare metered totals to CAP


def he_mlp(seed: int) -> MLP:
    rng = np.random.default_rng(seed)
    gain = math.sqrt(2.0 / WIDTH)
    weights = [
        fnp.asarray(
            (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain)
            .astype(np.float32)
        )
        for _ in range(DEPTH)
    ]
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights, seed=seed,
              name=f"t3-g1-he-{seed}")
    mlp.validate()
    return mlp


_erf = np.vectorize(math.erf, otypes=[np.float64])


def moment_alphas(weights64):
    """Plain-numpy float64 mirror of _diagonal_gaussian_pass (design only)."""
    w = weights64[0].shape[0]
    mu = np.zeros(w)
    var = np.ones(w)
    alphas = []
    mus = []
    for W in weights64:
        mu_pre = mu @ W
        var_pre = var @ (W * W)
        sigma = np.sqrt(np.maximum(var_pre, 1e-12))
        alpha = mu_pre / sigma
        cdf = 0.5 * (1.0 + _erf(alpha / math.sqrt(2.0)))
        phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
        mu = mu_pre * cdf + sigma * phi
        second = (var_pre + mu_pre * mu_pre) * cdf + mu_pre * sigma * phi
        var = np.maximum(second - mu * mu, 0.0)
        alphas.append(alpha)
        mus.append(mu.copy())
    return alphas, mus


def adversarial_mlp(seed: int = 990011):
    """Low-pruning net: He + positive mean offset, per-layer renormalized.

    A uniform positive offset m0 drives every pre-activation mean up, so
    analytic alphas land >= dead_alpha nearly everywhere and structural
    pruning vanishes.  Per-layer rescaling (alphas are scale-invariant per
    layer; ReLU is positively homogeneous) keeps float32 activations bounded.
    """
    rng = np.random.default_rng(seed)
    gain = math.sqrt(2.0 / WIDTH)
    he64 = [
        rng.standard_normal((WIDTH, WIDTH)) * gain for _ in range(DEPTH)
    ]
    chosen = None
    for m0 in (0.002, 0.004, 0.008, 0.016, 0.032, 0.064):
        cand = [W + m0 for W in he64]
        alphas, _ = moment_alphas(cand)
        cold = int(sum(int((a < -2.0).sum()) for a in alphas[1:]))
        print(f"  adversarial design m0={m0}: cold units (layers 1..31) = {cold}")
        if chosen is None or cold < chosen[1]:
            chosen = (m0, cold, cand)
        if cold == 0:
            break
    m0, cold, cand = chosen
    # Normalizing pass: rescale each layer to unit mean-norm growth.
    w = WIDTH
    mu = np.zeros(w)
    var = np.ones(w)
    target = float(np.sqrt(w))
    weights32 = []
    for W in cand:
        mu_pre = mu @ W
        var_pre = var @ (W * W)
        sigma = np.sqrt(np.maximum(var_pre, 1e-12))
        alpha = mu_pre / sigma
        cdf = 0.5 * (1.0 + _erf(alpha / math.sqrt(2.0)))
        phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
        mu_post = mu_pre * cdf + sigma * phi
        second = (var_pre + mu_pre * mu_pre) * cdf + mu_pre * sigma * phi
        var_post = np.maximum(second - mu_post * mu_post, 0.0)
        c = target / max(float(np.linalg.norm(mu_post)), 1e-30)
        weights32.append(fnp.asarray((W * c).astype(np.float32)))
        mu = mu_post * c
        var = var_post * c * c
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights32, seed=seed,
              name="t3-adversarial-low-pruning")
    mlp.validate()
    return mlp, m0, cold


def metered_predict(estimator, mlp):
    started = time.perf_counter()
    failure = None
    prediction = None
    ctx = flops.BudgetContext(METER_BUDGET, quiet=True)
    try:
        with ctx:
            out = estimator.predict(mlp, METER_BUDGET)
        prediction = np.asarray(out).copy()
    except Exception as exc:  # noqa: BLE001 - report verbatim
        failure = f"{type(exc).__name__}: {exc}"
    return {
        "billed_flops": int(ctx.flops_used),
        "wall_s": round(time.perf_counter() - started, 3),
        "failure": failure,
        "prediction": prediction,
    }


def fresh(cls, setup_seed):
    est = cls()
    est.setup(SetupContext(
        width=WIDTH, depth=DEPTH, flop_budget=int(BUDGET_B),
        api_version="synthetic", seed=setup_seed,
    ))
    return est


def main() -> None:
    results = {
        "date": "2026-08-08",
        "firewall": "synthetic nets only; no dataset/truth/scorer/submission",
        "constants": {
            "cap_billed_flops": CAP,
            "budget_B": BUDGET_B,
            "g1_ratio_window": list(G1_WINDOW),
            "n_full": 39_936,
            "meter_budget": METER_BUDGET,
        },
        "gates": {},
        "verdict": None,
    }
    out_path = HERE / "t3_gate_results.json"

    def finish(verdict: str):
        results["verdict"] = verdict
        out_path.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nVERDICT: {verdict}")
        print(f"results written to {out_path}")

    # ------------------------------------------------------------------ G1
    print("G1: cost-model calibration on 3 He-init synthetic nets")
    g1 = {"nets": [], "pass": True}
    g1_predictions = {}
    for seed in G1_SEEDS:
        mlp = he_mlp(seed)
        setup_seed = SETUP_SEED_BASE + seed

        uncapped = fresh(UncappedEstimator, setup_seed)
        um = metered_predict(uncapped, mlp)
        del uncapped
        gc.collect()

        capped = fresh(CappedEstimator, setup_seed)
        cm = metered_predict(capped, mlp)
        report = getattr(capped, "last_cap_report", None)
        del capped
        gc.collect()

        if um["failure"] or cm["failure"] or report is None:
            g1["pass"] = False
            g1["nets"].append({
                "seed": seed,
                "uncapped_failure": um["failure"],
                "capped_failure": cm["failure"],
            })
            print(f"  net {seed}: RUN FAILURE "
                  f"uncapped={um['failure']} capped={cm['failure']}")
            break

        ratio = report["c_pred_full"] / um["billed_flops"]
        net_pass = G1_WINDOW[0] <= ratio <= G1_WINDOW[1]
        g1["nets"].append({
            "seed": seed,
            "c_uncapped_metered": um["billed_flops"],
            "c_pred_full": report["c_pred_full"],
            "ratio": round(ratio, 6),
            "within_window": net_pass,
            "n_eff": report["n_eff"],
            "c_pred_chosen": report["c_pred_chosen"],
            "c_capped_metered": cm["billed_flops"],
            "sim_cost_observed": report["sim_cost_observed"],
            "dp_cost_observed": report["dp_cost_observed"],
            "uncapped_wall_s": um["wall_s"],
            "capped_wall_s": cm["wall_s"],
        })
        g1["pass"] = g1["pass"] and net_pass
        g1_predictions[seed] = {
            "uncapped": um["prediction"],
            "capped": cm["prediction"],
            "c_pred_full": report["c_pred_full"],
            "n_eff": report["n_eff"],
        }
        print(f"  net {seed}: C_uncapped={um['billed_flops']:.4e}  "
              f"C_pred(39936)={report['c_pred_full']:.4e}  "
              f"ratio={ratio:.4f}  n_eff={report['n_eff']}  "
              f"C_capped_metered={cm['billed_flops']:.4e}  "
              f"[{'PASS' if net_pass else 'KILL'}]")
        del mlp
        gc.collect()

    results["gates"]["g1"] = g1
    if not g1["pass"]:
        print("G1: KILL (cost model out of window / run failure)")
        finish("KILL at G1: C_pred(39936) outside [0.98, 1.06] of metered "
               "billed FLOPs (first broken link)")
        return
    print("G1: PASS")

    # ------------------------------------------------------------------ G2
    print("\nG2: adversarial low-pruning worst case")
    adv_mlp, m0, design_cold = adversarial_mlp()
    setup_seed = SETUP_SEED_BASE + 99

    capped = fresh(CappedEstimator, setup_seed)
    cm = metered_predict(capped, adv_mlp)
    report = getattr(capped, "last_cap_report", None)
    del capped
    gc.collect()

    # Diagnostic only (not a gate): what the uncapped estimator would bill.
    uncapped = fresh(UncappedEstimator, setup_seed)
    um = metered_predict(uncapped, adv_mlp)
    del uncapped
    gc.collect()

    completed = cm["failure"] is None and report is not None
    finite = bool(np.isfinite(cm["prediction"]).all()) if completed else False
    n_eff = report["n_eff"] if report else None
    limit = CAP * 1.02
    a_check = completed and n_eff is not None and n_eff < 39_936
    b_check = completed
    c_check = completed and cm["billed_flops"] <= limit
    g2_pass = a_check and b_check and c_check
    realized_active = (
        [dims[3] for dims in report["loop_dims"]] if report else None
    )
    results["gates"]["g2"] = {
        "design_m0": m0,
        "design_cold_units": design_cold,
        "realized_active_counts": realized_active,
        "n_eff": n_eff,
        "a_neff_below_full": a_check,
        "b_run_completed": b_check,
        "capped_failure": cm["failure"],
        "output_finite": finite,
        "c_capped_metered": cm["billed_flops"],
        "c_limit_cap_x1.02": limit,
        "c_within_limit": c_check,
        "c_pred_full": report["c_pred_full"] if report else None,
        "c_pred_chosen": report["c_pred_chosen"] if report else None,
        "capped_wall_s": cm["wall_s"],
        "diagnostic_uncapped_metered": um["billed_flops"],
        "diagnostic_uncapped_would_breach_B": um["billed_flops"] > BUDGET_B,
        "pass": g2_pass,
    }
    print(f"  m0={m0} design_cold={design_cold} "
          f"realized_active={realized_active}")
    print(f"  n_eff={n_eff} (<39936: {a_check})  completed={b_check}  "
          f"finite={finite}")
    print(f"  C_capped={cm['billed_flops']:.4e} <= {limit:.4e}: {c_check}")
    print(f"  diagnostic: uncapped C={um['billed_flops']:.4e} "
          f"(would breach B={BUDGET_B:.3e}: {um['billed_flops'] > BUDGET_B})")
    if not g2_pass:
        print("G2: KILL")
        finish("KILL at G2: adversarial cap behavior failed "
               "(first broken link)")
        return
    print("G2: PASS")

    # ------------------------------------------------------------------ G3
    print("\nG3: bitwise no-op off the tail (G1 nets with C_pred(full) <= CAP)")
    g3 = {"nets": [], "pass": True, "vacuous": True}
    for seed in G1_SEEDS:
        entry = g1_predictions[seed]
        applicable = entry["c_pred_full"] <= CAP
        row = {"seed": seed, "applicable": applicable,
               "c_pred_full": entry["c_pred_full"], "n_eff": entry["n_eff"]}
        if applicable:
            g3["vacuous"] = False
            same = bool(np.array_equal(entry["capped"], entry["uncapped"]))
            row["n_eff_is_full"] = entry["n_eff"] == 39_936
            row["bitwise_equal"] = same
            row["pass"] = row["n_eff_is_full"] and same
            g3["pass"] = g3["pass"] and row["pass"]
            print(f"  net {seed}: applicable, n_eff={entry['n_eff']}, "
                  f"bitwise_equal={same} "
                  f"[{'PASS' if row['pass'] else 'KILL'}]")
        else:
            # Not a gate condition; recorded as data.
            row["bitwise_equal_at_reduced_n"] = bool(
                np.array_equal(entry["capped"], entry["uncapped"])
            )
            print(f"  net {seed}: not applicable "
                  f"(C_pred(full)={entry['c_pred_full']:.4e} > CAP), "
                  f"n_eff={entry['n_eff']}")
        g3["nets"].append(row)
    results["gates"]["g3"] = g3
    if not g3["pass"]:
        print("G3: KILL")
        finish("KILL at G3: cap was not a bitwise no-op off the tail "
               "(first broken link)")
        return
    print(f"G3: PASS{' (vacuous: no G1 net under CAP at full n)' if g3['vacuous'] else ''}")

    finish("PASS: G1, G2, G3 all pass"
           + (" (G3 vacuous)" if g3["vacuous"] else ""))


if __name__ == "__main__":
    main()
