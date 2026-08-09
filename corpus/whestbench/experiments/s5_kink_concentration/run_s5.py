"""S5 -- Landau kink-concentration premise probe (ledger id
s5_landau_kink_concentration_premise).

QUESTION: does the champion estimator's per-direction residual energy
concentrate near the ReLU kink set (activation boundaries) on the sphere?

DESIGN (predeclared by the S5 task):
  * 3 He nets (seeds 101, 202, 303), depth 32, width 256, one rotation each
    (r=0, rotation seed = 900000 + net_seed*1000 + 0, the P2 lineage formula).
  * Direction set: the frozen Kerdock v3 base set (126 phased-Hadamard frames
    x 256 rows = 32,256 directions at exact radius mean_chi(256)), rotated by
    the per-net Haar rotation and antipodally doubled -> 64,512 directions.
  * Residual proxy r(u) = ybar(u) - m, where ybar(u) is the neuron-averaged
    post-ReLU final-layer output and m is the design mean of ybar (global
    version); frame version subtracts each direction's 512-member frame mean.
  * Kink-distance observables d1, dmin, kcount (exact definitions below).
  * Deciles of each observable; mean |r|^2 per decile; near/far ratios;
    Spearman rho of |r|^2 vs each observable; per net and pooled.

PREDECLARED GATES (verbatim from the task):
  PASS  = nearest/farthest decile ratio >= 3x with monotone decile trend on
          >= 2 of 3 nets (either residual version, either of d1/dmin).
  KILL  = pooled ratio < 1.5x or non-monotone/sign-inconsistent across nets.
  else  = INCONCLUSIVE (ledger holds unresolved, no reopen license).

EXACT NORMALIZATIONS (documented per the task; also in S5_VERDICT.md):
  * Effective first layer after rotation: W1_eff = R.T @ W[0]; layer-1
    preactivation pre1 = kerdock_base @ W1_eff (the n8a/estimator
    association).  The rotated direction u_i is row i of kerdock_base @ R.T.
  * d1(u)   = min_j |pre1(u)_j| / ||W1_eff[:, j]||_2 / mean_chi(256).
    All directions share radius mean_chi, so this is the (sine of the)
    angular margin to the nearest FIRST-layer activation boundary.
  * layer-l margin (l >= 2, input activation a = post-ReLU output of l-1):
    m_l(u) = min_j |pre_l(u)_j| / ||W[l][:, j]||_2 / ||a(u)||_2
    i.e. the Euclidean point-to-hyperplane distance in layer l's own input
    space, scaled by the incoming activation norm (relative margin).
  * dmin(u) = min over layers l = 1..32 of m_l(u)  (layer-1 term == d1).
  * kcount(u): within u's Kerdock frame all 510 non-antipodal frame-mates
    (256 rows x both signs, minus u and -u) are EXACTLY equidistant from u
    (phased-Hadamard rows are mutually orthogonal), so "nearest design
    neighbor" is a 510-way tie.  Operationalization (recorded as a
    deviation-level decision): kcount(u) = min over all non-antipodal
    frame-mates v of the Hamming distance between the layer-1 activation
    sign patterns of u and v (number of first-layer boundaries separating
    u from an equidistant 90-degree neighbor; sign(0) counted as +).
    kcount is a density (higher = more kinks nearby): its "near" decile is
    the HIGHEST-kcount decile.  kcount is diagnostic-only for the gates
    (the gates name d1/dmin).
  * Deciles: equal-count rank bins (bin = rank*10 // n, ascending
    observable).  "Near" = decile 0 for d1/dmin (smallest distance),
    decile 9 for kcount.  Ratio = mean|r|^2(near) / mean|r|^2(far).
  * Monotone decile trend (gate-bearing operationalization): the 10 decile
    mean energies are STRICTLY decreasing from the near decile to the far
    decile (all 9 successive differences).  Violation counts and the decile-
    level trend are also reported as diagnostics.
  * Pooled: each net's |r|^2 is normalized by its own net-mean energy;
    deciles assigned within net; pooled decile mean = mean over nets of the
    per-net normalized decile means; pooled ratio from that table.  Pooled
    rho = Spearman on the concatenated (observable, normalized energy).
  * Sign-inconsistent across nets = the per-net direction-level Spearman
    rhos do not share one sign across the 3 nets.

FIREWALL: synthetic He nets only; n8a machinery imported read-only (its own
module loads the frozen v3 sampling asset kerdock_phases.npz read-only); no
dataset/truth/scorer/submission access; no git; writes confined to this
directory (s5_kink_concentration).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # firewall: no .pyc into other directories

import numpy as np

HERE = Path(__file__).resolve().parent
N8A = HERE.parent / "n8a_rqmc_kerdock" / "run_n8a_gates.py"

_spec = importlib.util.spec_from_file_location("run_n8a_gates", N8A)
n8a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(n8a)  # module main() is __main__-guarded: safe

WIDTH = n8a.WIDTH            # 256
DEPTH = n8a.DEPTH            # 32
MEAN_CHI = n8a.MEAN_CHI_256  # 15.98438266660852747
NET_SEEDS = (101, 202, 303)
N_BASE = n8a.N_BASE          # 32,256
N_FULL = 2 * N_BASE          # 64,512
N_FRAMES = 126
ROWS_PER_FRAME = 256

PASS_RATIO = 3.0
KILL_POOLED_RATIO = 1.5
GATE_OBS = ("d1", "dmin")            # gate-bearing observables
ALL_OBS = ("d1", "dmin", "kcount")   # kcount = diagnostic only
RESIDS = ("global", "frame")


def rot_seed(net_seed: int) -> int:
    return 900_000 + net_seed * 1_000 + 0  # r = 0 (predeclared)


# --------------------------------------------------------------- forward pass
def forward_with_margins(weights: list[np.ndarray], first_eff: np.ndarray,
                         kerdock: np.ndarray):
    """One antipodally-doubled forward pass recording margin observables.

    Returns dict with d1, dmin (N_FULL,), ybar (N_FULL,) float64,
    y (N_FULL, WIDTH) float32 final post-ReLU, plus degeneracy counters.
    """
    pre1 = kerdock @ first_eff                      # (N_BASE, WIDTH) f32
    col1 = np.linalg.norm(first_eff.astype(np.float64), axis=0)
    m1 = (np.abs(pre1.astype(np.float64)) / col1[None, :]).min(axis=1) / MEAN_CHI
    d1 = np.concatenate([m1, m1])                   # pre1(-u) = -pre1(u)

    act = np.concatenate([np.maximum(pre1, np.float32(0.0)),
                          np.maximum(-pre1, np.float32(0.0))], axis=0)
    dmin = d1.copy()
    dead_rows_seen = 0
    zero_pre1 = int((pre1 == 0.0).sum())
    for layer in range(1, DEPTH):
        w = weights[layer]
        coln = np.linalg.norm(w.astype(np.float64), axis=0)
        anorm = np.linalg.norm(act.astype(np.float64), axis=1)
        pre = act @ w
        q = (np.abs(pre.astype(np.float64)) / coln[None, :]).min(axis=1)
        ml = q / np.maximum(anorm, 1e-300)          # anorm==0 -> q==0 -> ml==0
        dead_rows_seen += int((anorm == 0.0).sum())
        np.minimum(dmin, ml, out=dmin)
        act = np.maximum(pre, np.float32(0.0))
    ybar = act.astype(np.float64).mean(axis=1)
    return {"pre1": pre1, "d1": d1, "dmin": dmin, "ybar": ybar, "y": act,
            "dead_rows_seen": dead_rows_seen, "zero_pre1": zero_pre1}


def kcount_from_pre1(pre1: np.ndarray) -> np.ndarray:
    """Min layer-1 sign-pattern Hamming distance to any non-antipodal
    frame-mate (both signs), per base direction; antipodally duplicated."""
    signs = np.where(pre1 >= 0.0, np.float32(1.0), np.float32(-1.0))
    kc = np.empty(N_BASE, dtype=np.float64)
    for f in range(N_FRAMES):
        rows = slice(f * ROWS_PER_FRAME, (f + 1) * ROWS_PER_FRAME)
        s = signs[rows]
        gram = s @ s.T                              # 256 - 2*flips
        flips = (ROWS_PER_FRAME - gram) / 2.0
        cand = np.minimum(flips, ROWS_PER_FRAME - flips)
        np.fill_diagonal(cand, np.inf)              # exclude u and -u
        kc[rows] = cand.min(axis=1)
    return np.concatenate([kc, kc])


# ------------------------------------------------------------------ statistics
def rankdata_avg(x: np.ndarray) -> np.ndarray:
    """Average-rank rankdata (ties -> mean rank), 1-based."""
    order = np.argsort(x, kind="stable")
    ranks = np.empty(len(x), dtype=np.float64)
    ranks[order] = np.arange(1, len(x) + 1, dtype=np.float64)
    # average ranks over ties
    xs = x[order]
    uniq, inv, counts = np.unique(xs, return_inverse=True, return_counts=True)
    if len(uniq) != len(xs):
        csum = np.concatenate([[0], np.cumsum(counts)])
        avg = (csum[:-1] + csum[1:] + 1) / 2.0      # mean of 1-based positions
        ranks[order] = avg[inv]
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = rankdata_avg(x), rankdata_avg(y)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / denom)


def decile_bins(x: np.ndarray) -> np.ndarray:
    """Equal-count rank deciles 0..9 (ascending x; ties split by stable sort)."""
    order = np.argsort(x, kind="stable")
    bins = np.empty(len(x), dtype=np.int64)
    bins[order] = (np.arange(len(x)) * 10) // len(x)
    return bins


def decile_table(obs: np.ndarray, energy: np.ndarray, obs_name: str) -> dict:
    bins = decile_bins(obs)
    means = np.array([energy[bins == b].mean() for b in range(10)])
    edges = [float(np.quantile(obs, q)) for q in np.linspace(0, 1, 11)]
    if obs_name == "kcount":                        # density: near = decile 9
        near, far = means[9], means[0]
        ordered = means[::-1]                       # near -> far
    else:                                           # distance: near = decile 0
        near, far = means[0], means[9]
        ordered = means
    diffs = np.diff(ordered)
    return {
        "decile_mean_energy": [float(v) for v in means],
        "decile_edges": edges,
        "ratio_near_over_far": float(near / far),
        "strict_monotone": bool((diffs < 0).all()),
        "n_monotone_violations": int((diffs >= 0).sum()),
        "rho_spearman": spearman(obs, energy),
    }


# ------------------------------------------------------------------------ main
def main() -> None:
    t_start = time.perf_counter()
    print("S5 kink-concentration probe: loading Kerdock base set...", flush=True)
    kerdock = n8a.load_kerdock_directions()         # (32256, 256) f32

    results: dict = {
        "ledger_id": "s5_landau_kink_concentration_premise",
        "date": "2026-08-09",
        "config": {
            "net_seeds": list(NET_SEEDS), "depth": DEPTH, "width": WIDTH,
            "rotation_seed_formula": "900000 + net_seed*1000 + 0 (r=0)",
            "n_directions": N_FULL, "n_base": N_BASE,
            "radius": MEAN_CHI,
            "gates": {
                "pass": "near/far decile ratio >= 3 AND strict monotone decile"
                        " trend, on >= 2 of 3 nets, same (observable, residual)"
                        " combo, observable in {d1, dmin}",
                "kill": "every gate combo has pooled ratio < 1.5, OR every gate"
                        " combo is sign-inconsistent across nets (per-net rho"
                        " signs disagree)",
                "else": "INCONCLUSIVE",
            },
            "normalizations": "see module docstring / S5_VERDICT.md",
        },
        "nets": {},
        "pooled": {},
        "cross_checks": {},
        "verdict": None,
    }

    per_net = {}
    for seed in NET_SEEDS:
        t0 = time.perf_counter()
        weights = n8a.he_mlp_weights(seed)
        rot = n8a.haar_rotation(rot_seed(seed))
        first_eff = (rot.T @ weights[0]).astype(np.float32)

        # Rotated direction set (explicit, for the radius check + cross-check).
        u_rot = (kerdock @ rot.T).astype(np.float32)
        radii = np.linalg.norm(u_rot.astype(np.float64), axis=1)
        max_rad_dev = float(np.abs(radii - MEAN_CHI).max() / MEAN_CHI)
        if max_rad_dev > 1e-4:
            raise RuntimeError(f"net {seed}: rotated radius off by {max_rad_dev}")

        fw = forward_with_margins(weights, first_eff, kerdock)
        kcount = kcount_from_pre1(fw["pre1"])

        ybar = fw["ybar"]
        m = float(ybar.mean())
        r_global = ybar - m
        frames = np.tile(np.repeat(np.arange(N_FRAMES), ROWS_PER_FRAME), 2)
        frame_means = np.bincount(frames, weights=ybar) / np.bincount(frames)
        r_frame = ybar - frame_means[frames]
        energies = {"global": r_global ** 2, "frame": r_frame ** 2}
        # diagnostic: full-256-vector residual energy about the design mean vec
        ymean_vec = fw["y"].astype(np.float64).mean(axis=0)
        e_vec = ((fw["y"].astype(np.float64) - ymean_vec[None, :]) ** 2).mean(axis=1)

        obs = {"d1": fw["d1"], "dmin": fw["dmin"], "kcount": kcount}

        # Cross-check 1 (two-path design mean): n8a's own antipodal_forward_mean
        # with the OTHER matmul association (points = rotated U, first = W[0]).
        ref = n8a.antipodal_forward_mean(weights, weights[0], u_rot)
        m_ref = float(ref.mean())
        m_rel_diff = abs(m - m_ref) / max(abs(m_ref), 1e-300)

        net_row: dict = {
            "design_mean_m": m,
            "design_mean_ref_other_association": m_ref,
            "design_mean_rel_diff": m_rel_diff,
            "max_radius_rel_dev": max_rad_dev,
            "dead_rows_seen": fw["dead_rows_seen"],
            "zero_pre1_entries": fw["zero_pre1"],
            "energy_mean": {k: float(v.mean()) for k, v in energies.items()},
            "kcount_min_max": [float(kcount.min()), float(kcount.max())],
            "tables": {},
            "vector_residual_diagnostic": {},
        }
        for on in ALL_OBS:
            for rv in RESIDS:
                net_row["tables"][f"{on}__{rv}"] = decile_table(
                    obs[on], energies[rv], on)
            net_row["vector_residual_diagnostic"][on] = decile_table(
                obs[on], e_vec, on)
        # Harness-validation positive control (diagnostic, NOT gate-bearing,
        # circular by construction): bin |r_global|^2 by deciles of |r_global|
        # itself.  A huge strictly-monotone ratio proves the decile machinery
        # detects real structure when present, so a null on the kink
        # observables cannot be a broken-binning artifact.
        pc_bins = decile_bins(np.abs(r_global))
        pc = np.array([energies["global"][pc_bins == b].mean()
                       for b in range(10)])
        net_row["positive_control_binning"] = {
            "ratio_decile10_over_1": float(pc[9] / pc[0]),
            "strict_monotone_increasing": bool((np.diff(pc) > 0).all()),
        }
        net_row["wall_s"] = round(time.perf_counter() - t0, 1)
        results["nets"][str(seed)] = net_row
        per_net[seed] = {"obs": obs, "energies": energies}

        np.savez_compressed(
            HERE / f"s5_net{seed}_arrays.npz",
            d1=fw["d1"].astype(np.float64), dmin=fw["dmin"].astype(np.float64),
            kcount=kcount, ybar=ybar, frames=frames,
            r_global=r_global, r_frame=r_frame, e_vec=e_vec)

        for on in GATE_OBS:
            for rv in RESIDS:
                t = net_row["tables"][f"{on}__{rv}"]
                print(f"  net {seed} {on:5s}/{rv:6s}: "
                      f"ratio={t['ratio_near_over_far']:.3f} "
                      f"monotone={t['strict_monotone']} "
                      f"viol={t['n_monotone_violations']} "
                      f"rho={t['rho_spearman']:+.4f}", flush=True)
        print(f"  net {seed}: m={m:.6e} ref={m_ref:.6e} "
              f"rel_diff={m_rel_diff:.2e}  wall={net_row['wall_s']}s", flush=True)

    # ------------------------------------------------------------------ pooled
    for on in ALL_OBS:
        for rv in RESIDS:
            per_net_norm_means = []
            cat_obs, cat_en = [], []
            for seed in NET_SEEDS:
                o = per_net[seed]["obs"][on]
                e = per_net[seed]["energies"][rv]
                en = e / e.mean()
                bins = decile_bins(o)
                per_net_norm_means.append(
                    np.array([en[bins == b].mean() for b in range(10)]))
                cat_obs.append(o)
                cat_en.append(en)
            pooled_means = np.mean(per_net_norm_means, axis=0)
            if on == "kcount":
                near, far = pooled_means[9], pooled_means[0]
                ordered = pooled_means[::-1]
            else:
                near, far = pooled_means[0], pooled_means[9]
                ordered = pooled_means
            diffs = np.diff(ordered)
            per_net_rhos = [results["nets"][str(s)]["tables"][f"{on}__{rv}"]
                            ["rho_spearman"] for s in NET_SEEDS]
            results["pooled"][f"{on}__{rv}"] = {
                "decile_mean_energy_normalized": [float(v) for v in pooled_means],
                "ratio_near_over_far": float(near / far),
                "strict_monotone": bool((diffs < 0).all()),
                "n_monotone_violations": int((diffs >= 0).sum()),
                "rho_spearman_pooled": spearman(
                    np.concatenate(cat_obs), np.concatenate(cat_en)),
                "per_net_rhos": per_net_rhos,
                "rho_signs_consistent": bool(
                    all(r > 0 for r in per_net_rhos)
                    or all(r < 0 for r in per_net_rhos)),
            }

    # ------------------------------------------------------- cross-checks 2, 3
    # 2: Spearman two-way -- my implementation vs scipy, plus the no-ties
    #    classical formula on d1 (continuous; verify tie count first).
    from scipy.stats import spearmanr
    xc = {}
    s0 = NET_SEEDS[0]
    for on in ALL_OBS:
        o = per_net[s0]["obs"][on]
        e = per_net[s0]["energies"]["global"]
        mine = spearman(o, e)
        sci = float(spearmanr(o, e).statistic)
        xc[f"rho_{on}_global_net{s0}"] = {
            "mine": mine, "scipy": sci, "abs_diff": abs(mine - sci)}
    d1_ties = int(len(per_net[s0]["obs"]["d1"])
                  - len(np.unique(per_net[s0]["obs"]["d1"])))
    if d1_ties == 0:
        rx = rankdata_avg(per_net[s0]["obs"]["d1"])
        ry = rankdata_avg(per_net[s0]["energies"]["global"])
        n = len(rx)
        rho_formula = 1.0 - 6.0 * float(((rx - ry) ** 2).sum()) / (n * (n * n - 1))
        xc["rho_d1_noties_formula"] = {
            "value": rho_formula,
            "abs_diff_vs_mine": abs(rho_formula
                                    - xc[f"rho_d1_global_net{s0}"]["mine"]),
        }
    xc["d1_tie_count_net101"] = d1_ties
    results["cross_checks"]["spearman_two_way"] = xc

    # 3: bitwise repeat of the d1/global decile table from the saved arrays.
    repeat_ok = True
    for seed in NET_SEEDS:
        d = np.load(HERE / f"s5_net{seed}_arrays.npz")
        t2 = decile_table(d["d1"], d["r_global"] ** 2, "d1")
        t1 = results["nets"][str(seed)]["tables"]["d1__global"]
        same = (t2["decile_mean_energy"] == t1["decile_mean_energy"]
                and t2["ratio_near_over_far"] == t1["ratio_near_over_far"])
        repeat_ok = repeat_ok and same
        d.close()
    results["cross_checks"]["decile_table_bitwise_repeat_from_npz"] = repeat_ok
    results["cross_checks"]["design_mean_two_path_max_rel_diff"] = max(
        results["nets"][str(s)]["design_mean_rel_diff"] for s in NET_SEEDS)

    # ------------------------------------------------------------------- gates
    gate_eval = {"pass_combos": [], "combo_status": {}}
    for on in GATE_OBS:
        for rv in RESIDS:
            key = f"{on}__{rv}"
            n_pass_nets = sum(
                1 for s in NET_SEEDS
                if (results["nets"][str(s)]["tables"][key]["ratio_near_over_far"]
                    >= PASS_RATIO
                    and results["nets"][str(s)]["tables"][key]["strict_monotone"]))
            pooled = results["pooled"][key]
            status = {
                "n_nets_ratio_ge_3_and_monotone": n_pass_nets,
                "pooled_ratio": pooled["ratio_near_over_far"],
                "pooled_ratio_ge_1p5": pooled["ratio_near_over_far"]
                                       >= KILL_POOLED_RATIO,
                "rho_signs_consistent": pooled["rho_signs_consistent"],
            }
            gate_eval["combo_status"][key] = status
            if n_pass_nets >= 2:
                gate_eval["pass_combos"].append(key)

    if gate_eval["pass_combos"]:
        verdict = ("PASS: " + ", ".join(gate_eval["pass_combos"])
                   + " reached ratio >= 3 with strict monotone deciles on >= 2"
                     " of 3 nets")
    else:
        all_pooled_dead = all(
            not s["pooled_ratio_ge_1p5"]
            for s in gate_eval["combo_status"].values())
        all_inconsistent = all(
            not s["rho_signs_consistent"]
            for s in gate_eval["combo_status"].values())
        if all_pooled_dead or all_inconsistent:
            reason = []
            if all_pooled_dead:
                reason.append("pooled near/far ratio < 1.5 on every gate combo")
            if all_inconsistent:
                reason.append("per-net rho signs inconsistent on every combo")
            verdict = "KILL: " + " and ".join(reason)
        else:
            verdict = ("INCONCLUSIVE: no combo met the 3x+monotone PASS bar on"
                       " >= 2 nets, but not every combo fell below the pooled"
                       " 1.5x / consistency KILL bar")
    results["gate_evaluation"] = gate_eval
    results["verdict"] = verdict
    results["total_wall_s"] = round(time.perf_counter() - t_start, 1)

    out = HERE / "s5_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"\nVERDICT: {verdict}")
    print(f"results -> {out}  (wall {results['total_wall_s']}s)", flush=True)


if __name__ == "__main__":
    main()
