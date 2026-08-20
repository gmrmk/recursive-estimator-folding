"""S10 -- ledger id s10_mlmc_depth_increment_variance.

QUESTION: does multilevel Monte Carlo (MLMC) over DEPTH give a real
variance-per-FLOP gain for estimating E[f_L] (L=32, final-layer
neuron-averaged post-ReLU output), when the champion is single-level
sampling of the full net?

Firewall: synthetic self-generated He nets + own MC only.  We IMPORT (never
edit) the frozen constructor + Kerdock directions from the sibling n8a
runner (load_kerdock_directions, haar_rotation, he_mlp_weights, WIDTH,
DEPTH, MEAN_CHI_256, radial_condition, N_BASE).  No dataset/truth/scorer/
submission access.  Writes confined to this directory.

------------------------------------------------------------------ TARGET
Champion target: E[f_L], f_L(u) = neuron-average of the layer-32 post-ReLU
activation for input direction u, averaged over u (antipodally doubled
Kerdock design).  This is EXACTLY the double average (over u and over the
256 output neurons) that the champion's antipodal_forward_mean produces,
so the depth telescope estimates the champion's target with NO gap.

------------------------------------------------------ DEPTH LADDER / SCALAR
Level scalar g_l(u) = neuron-average of the post-ReLU activation after
applying the first l weight matrices (weights[0..l-1], ReLU after each),
starting from direction u.  The first matmul carries the per-net Haar
rotation exactly as the champion does (first_eff = rotation.T @ weights[0]),
and antipodal doubling happens right after it, again exactly as the champion.

  g_1(u)  = mean_neurons ReLU(u @ W0_eff)                    1 layer-matmul
  g_2(u)  = mean_neurons ReLU(ReLU(u @ W0_eff) @ W1)         2 layer-matmuls
  ...
  g_32(u) = mean_neurons (full net output)                  32 layer-matmuls

g_l and g_{l+1} share the SAME u -> the increment g_{l+1}-g_l is a COUPLED
(common-random-number) quantity, which is the whole point of MLMC.

LIMITATION (documented): the scalar is the neuron-mean at each depth; this
is a directly comparable scalar across levels and g_32 IS the champion's
target (final-layer neuron-mean).  The telescope therefore has no target
gap.  The one modelling choice is that per-draw variances are measured as
the EMPIRICAL variance of g across the structured (Kerdock / antipodal)
design points; for a fixed-radius well-spread design this empirical second
moment estimates the population Var_u under the intended sphere ensemble
(cross-checked against an independent iid-Gaussian resample below).

--------------------------------------------------------------- FLOP MODEL
One "layer-matmul" = one WIDTH x WIDTH matmul applied to a batch of
directions = WIDTH^2 = 65,536 MACs per direction (ReLU + neuron-mean are
O(WIDTH), negligible).  Billed cost to evaluate g_l = l layer-matmuls.
The MLMC increment estimator Y_l = g_{l+1}-g_l is evaluated by a single
forward to depth l+1 (g_l is the byproduct at depth l), so its billed cost
is (l+1) layer-matmuls.  Base level E[g_1] costs 1.  Single-level E[g_32]
costs 32.  (The proportionality constant WIDTH^2 cancels in every ratio.)

------------------------------------------------------------- MLMC CLOSED FORM
Estimator levels:
  base : V_0 = Var_u[g_1],                 c_0 = 1
  l=1..31 : V_l = Var_u[g_{l+1}-g_l],      c_l = l+1
Optimal allocation N_l  proportional to  sqrt(V_l / c_l).
MLMC work-normalized variance (variance x total FLOPs) at the optimum:
  W_mlmc  = ( sum_levels sqrt(V_l * c_l) )^2
Single-level:
  W_single = V_full * c_32,  V_full = Var_u[g_32], c_32 = 32
GAIN (variance-per-FLOP, MLMC vs single-level) = W_single / W_mlmc.
  >1 => MLMC wins.  Gate: >=1.3x live ; <1.1x dead ; 1.1-1.3x inconclusive.

Rhee-Glynn randomized single-term estimator (unbiased, cross-check): its
work-normalized variance uses the level SECOND MOMENTS,
  W_rg = ( sum_levels sqrt(E[Delta_l^2] * c_l) )^2 ,
with Delta_0 = g_1, Delta_l = g_{l+1}-g_l.  gain_rg = W_single / W_rg.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N8A_DIR = (
    HERE.parent / "n8a_rqmc_kerdock"
)
sys.path.insert(0, str(N8A_DIR))

# Frozen, imported (never edited) constructor + directions.
import run_n8a_gates as n8a  # noqa: E402

WIDTH = n8a.WIDTH          # 256
DEPTH = n8a.DEPTH          # 32
N_BASE = n8a.N_BASE        # 126*256 = 32,256 (antipodally doubled -> 64,512)
MEAN_CHI_256 = n8a.MEAN_CHI_256
NET_SEEDS = (101, 202, 303)


def forward_ladder(
    weights: list[np.ndarray], first_eff: np.ndarray, points: np.ndarray
) -> np.ndarray:
    """Return g of shape (2*n, DEPTH): column k = g_{k+1}(u) for every
    antipodally-doubled sample u.  Mirrors the champion's forward exactly
    (antipodal doubling right after the rotated first matmul) but records
    the neuron-mean at every depth."""
    n2 = 2 * points.shape[0]
    g = np.empty((n2, DEPTH), dtype=np.float64)
    first = points @ first_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)),
         np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    g[:, 0] = act.mean(axis=1, dtype=np.float64)   # g_1, cost 1
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
        g[:, layer] = act.mean(axis=1, dtype=np.float64)  # g_{layer+1}
    return g


def ladder_stats(g: np.ndarray) -> dict:
    """All per-level quantities from a g matrix (samples x DEPTH)."""
    # Per-level means E_u[g_l], l=1..32
    level_mean = g.mean(axis=0)                       # len 32
    # Increment means E_u[g_{l+1}-g_l], l=1..31  (column diffs 1..31)
    diffs = g[:, 1:] - g[:, :-1]                      # (samples, 31)
    inc_mean = diffs.mean(axis=0)                     # len 31
    # Coupled increment variances V_l = Var_u[g_{l+1}-g_l]
    inc_var = diffs.var(axis=0, ddof=1)               # len 31
    inc_sec = (diffs * diffs).mean(axis=0)            # E[Delta^2], len 31
    # Base level
    v_base = float(g[:, 0].var(ddof=1))
    sec_base = float((g[:, 0] * g[:, 0]).mean())
    # Single-level full net
    v_full = float(g[:, 31].var(ddof=1))
    return {
        "level_mean": level_mean,
        "inc_mean": inc_mean,
        "inc_var": inc_var,
        "inc_sec": inc_sec,
        "v_base": v_base,
        "sec_base": sec_base,
        "v_full": v_full,
        "grand_mean_g32": float(level_mean[31]),
    }


def mlmc_gain(stats: dict) -> dict:
    """Closed-form MLMC allocation + gain vs single-level, matched FLOPs."""
    # Cost model: base cost 1; increment l (l=1..31) cost (l+1).
    inc_c = np.arange(2, DEPTH + 1, dtype=np.float64)   # 2..32, len 31
    v_levels = np.concatenate(([stats["v_base"]], stats["inc_var"]))
    c_levels = np.concatenate(([1.0], inc_c))
    sec_levels = np.concatenate(([stats["sec_base"]], stats["inc_sec"]))

    # MLMC work-normalized variance (variance x FLOPs at optimal allocation).
    root_vc = np.sqrt(v_levels * c_levels)
    w_mlmc = float(root_vc.sum() ** 2)
    w_single = float(stats["v_full"] * DEPTH)          # c_32 = 32
    gain = w_single / w_mlmc

    # Optimal allocation fractions N_l propto sqrt(V_l/c_l).
    alloc = np.sqrt(v_levels / c_levels)
    alloc = alloc / alloc.sum()

    # Rhee-Glynn randomized single-term: uses second moments.
    root_sc = np.sqrt(sec_levels * c_levels)
    w_rg = float(root_sc.sum() ** 2)
    gain_rg = w_single / w_rg

    return {
        "w_mlmc": w_mlmc,
        "w_single": w_single,
        "gain_mlmc_over_single": gain,
        "w_rhee_glynn": w_rg,
        "gain_rhee_glynn": gain_rg,
        "alloc_fractions": alloc.tolist(),
        "level_costs": c_levels.tolist(),
        "level_vars": v_levels.tolist(),
    }


def fit_decay(y: np.ndarray, l_index: np.ndarray) -> dict:
    """Geometric decay fit y_l ~ A * rho^l on strictly-positive y."""
    mask = y > 0
    if mask.sum() < 3:
        return {"rho_per_layer": None, "r2": None, "n_points": int(mask.sum())}
    x = l_index[mask].astype(np.float64)
    ly = np.log(y[mask])
    slope, intercept = np.polyfit(x, ly, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((ly - pred) ** 2))
    ss_tot = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return {
        "rho_per_layer": float(math.exp(slope)),
        "intercept": float(intercept),
        "r2": r2,
        "n_points": int(mask.sum()),
    }


def iid_directions(seed: int) -> np.ndarray:
    """Independent-signal resample: iid Gaussian directions radially
    conditioned to the same fixed radius mean_chi (own MC, firewall-clean)."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((N_BASE, WIDTH)).astype(np.float32)
    return n8a.radial_condition(z)


def main() -> None:
    t_start = time.perf_counter()
    print("S10 MLMC-over-depth increment-variance experiment", flush=True)

    # mean_chi self-check (same formula the frozen runner uses).
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    assert abs(mean_chi_check - MEAN_CHI_256) < 1e-9, "mean_chi mismatch"

    kerdock = n8a.load_kerdock_directions()   # (32,256, 256), radius mean_chi
    print(f"Kerdock directions {kerdock.shape}, antipodal-doubled "
          f"to {2 * N_BASE} samples per net", flush=True)

    results = {
        "ledger_id": "s10_mlmc_depth_increment_variance",
        "date": "2026-08-09",
        "firewall": (
            "synthetic He nets (seeds 101/202/303); frozen n8a constructor + "
            "Kerdock directions imported read-only; own MC only; no dataset/"
            "truth/scorer/submission; writes confined to s10_mlmc_depth/"
        ),
        "width": WIDTH,
        "depth": DEPTH,
        "n_base": N_BASE,
        "n_samples_doubled": 2 * N_BASE,
        "target": (
            "E_u[g_32], g_32(u)=neuron-mean of layer-32 post-ReLU output; "
            "equals champion target E[f_L] (final-layer neuron-mean), NO gap"
        ),
        "flop_model": (
            "1 layer-matmul = WIDTH^2 MACs per direction; cost(g_l)=l; "
            "increment Y_l cost=(l+1) (forward to depth l+1, g_l is byproduct);"
            " base cost=1; single-level cost c_32=32; constant cancels in ratios"
        ),
        "gates": {"live>=1.3": None, "dead<1.1": None, "inconclusive": "1.1-1.3"},
        "nets": [],
        "cross_check": {},
    }

    gains, gains_rg = [], []
    per_net_v_full = {}
    per_net_v_inc1 = {}
    for net in NET_SEEDS:
        t0 = time.perf_counter()
        weights = n8a.he_mlp_weights(net)
        rotation = n8a.haar_rotation(900_000 + net * 1_000 + 0)
        first_eff = (rotation.T @ weights[0]).astype(np.float32)
        g = forward_ladder(weights, first_eff, kerdock)
        st = ladder_stats(g)
        gn = mlmc_gain(st)
        wall = time.perf_counter() - t0

        # Decay fits: variance ladder and |mean-defect| ladder (l=1..31).
        l_idx = np.arange(1, DEPTH)                    # 1..31
        var_fit = fit_decay(st["inc_var"], l_idx)
        mean_fit = fit_decay(np.abs(st["inc_mean"]), l_idx)

        per_net_v_full[net] = st["v_full"]
        per_net_v_inc1[net] = float(st["inc_var"][0])
        gains.append(gn["gain_mlmc_over_single"])
        gains_rg.append(gn["gain_rhee_glynn"])

        row = {
            "net_seed": net,
            "rotation_seed": 900_000 + net * 1_000 + 0,
            "grand_mean_g32": st["grand_mean_g32"],
            "level_mean_g_l": st["level_mean"].tolist(),   # g_1..g_32
            "increment_mean_l_1_to_31": st["inc_mean"].tolist(),
            "increment_var_V_l_1_to_31": st["inc_var"].tolist(),
            "v_base_g1": st["v_base"],
            "v_full_g32": st["v_full"],
            "mlmc": gn,
            "var_decay_fit": var_fit,
            "mean_defect_decay_fit": mean_fit,
            "wall_s": round(wall, 1),
        }
        results["nets"].append(row)
        print(
            f"net {net}: E[g32]={st['grand_mean_g32']:.5f}  "
            f"V_full={st['v_full']:.4e}  V_1={st['inc_var'][0]:.4e}  "
            f"V_31={st['inc_var'][-1]:.4e}  "
            f"gain(MLMC)={gn['gain_mlmc_over_single']:.4f}  "
            f"gain(RG)={gn['gain_rhee_glynn']:.4f}  "
            f"var_rho={var_fit['rho_per_layer']:.4f}  "
            f"mean_rho={mean_fit['rho_per_layer']:.4f}  ({wall:.0f}s)",
            flush=True,
        )

    agg_gain = float(np.exp(np.mean(np.log(gains))))
    agg_gain_rg = float(np.exp(np.mean(np.log(gains_rg))))
    mean_var_rho = float(np.mean(
        [r["var_decay_fit"]["rho_per_layer"] for r in results["nets"]]))
    mean_defect_rho = float(np.mean(
        [r["mean_defect_decay_fit"]["rho_per_layer"] for r in results["nets"]]))

    results["aggregate"] = {
        "gain_mlmc_geomean": agg_gain,
        "gain_rhee_glynn_geomean": agg_gain_rg,
        "per_net_gain_mlmc": gains,
        "per_net_gain_rhee_glynn": gains_rg,
        "var_decay_rho_mean": mean_var_rho,
        "mean_defect_decay_rho_mean": mean_defect_rho,
        "compare_to_0_87_law": {
            "prior_defect_decay": 0.87,
            "measured_mean_defect_rho": mean_defect_rho,
            "measured_var_rho": mean_var_rho,
        },
    }

    # ------- TWO-SIGNAL: independent iid-Gaussian resample of V_full & V_1 ---
    # Population Var_u[g] is a second moment; a well-spread fixed-radius design
    # and an iid draw at the same radius must estimate the SAME value.
    cc = {"note": (
        "independent iid-Gaussian directions (radius mean_chi, own seed) vs "
        "the Kerdock design; both estimate the same population Var_u")}
    for net in NET_SEEDS:
        weights = n8a.he_mlp_weights(net)
        rotation = n8a.haar_rotation(900_000 + net * 1_000 + 0)
        first_eff = (rotation.T @ weights[0]).astype(np.float32)
        pts = iid_directions(424_242 + net)
        g_iid = forward_ladder(weights, first_eff, pts)
        st_iid = ladder_stats(g_iid)
        v_full_iid = st_iid["v_full"]
        v_inc1_iid = float(st_iid["inc_var"][0])
        cc[str(net)] = {
            "v_full_kerdock": per_net_v_full[net],
            "v_full_iid": v_full_iid,
            "v_full_ratio_iid_over_kerdock": v_full_iid / per_net_v_full[net],
            "v_inc1_kerdock": per_net_v_inc1[net],
            "v_inc1_iid": v_inc1_iid,
            "v_inc1_ratio_iid_over_kerdock": v_inc1_iid / per_net_v_inc1[net],
        }
        print(
            f"cross-check net {net}: V_full ker={per_net_v_full[net]:.4e} "
            f"iid={v_full_iid:.4e} (ratio {v_full_iid/per_net_v_full[net]:.3f}) "
            f"| V_1 ker={per_net_v_inc1[net]:.4e} iid={v_inc1_iid:.4e} "
            f"(ratio {v_inc1_iid/per_net_v_inc1[net]:.3f})",
            flush=True,
        )
    results["cross_check"] = cc

    # ---------------------------------------------------------------- verdict
    if agg_gain >= 1.3:
        verdict = (
            f"LIVE: closed-form MLMC-over-depth gain {agg_gain:.3f}x >= 1.3x "
            f"at matched billed FLOPs -> full-arm proposal warranted."
        )
    elif agg_gain < 1.1:
        verdict = (
            f"DEAD: closed-form MLMC-over-depth gain {agg_gain:.3f}x < 1.1x -> "
            f"the depth-fidelity family is fully dead; the champion "
            f"(single-level full-net sampling) is not beaten by a depth "
            f"telescope."
        )
    else:
        verdict = (
            f"INCONCLUSIVE: closed-form MLMC-over-depth gain {agg_gain:.3f}x "
            f"in [1.1, 1.3) -> no promotion, no full kill."
        )
    results["verdict"] = verdict
    results["wall_s_total"] = round(time.perf_counter() - t_start, 1)

    out = HERE / "s10_results.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nAGGREGATE gain(MLMC) geomean = {agg_gain:.4f}x  "
          f"gain(RG) = {agg_gain_rg:.4f}x  "
          f"var_rho={mean_var_rho:.4f}  defect_rho={mean_defect_rho:.4f}")
    print(f"VERDICT: {verdict}")
    print(f"results -> {out}  (total {results['wall_s_total']}s)")


if __name__ == "__main__":
    main()
