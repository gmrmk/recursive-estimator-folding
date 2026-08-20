"""U-F1 eligibility attack, stage 3: the two remaining questions.

  E. How often does the headline shape (64512x256)@(256x256) actually occur?
  F. Isolate the direct-baseline double count: the published translation
     applies (1 - r(d)) to a lane that is ALREADY charged at Winograd depth 1.
  G. Best case for the claim: adaptive per-hook depth with lawful ragged
     splitting / padding.  This is the ceiling the mechanism could reach.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PKG = REPO / "corpus" / "whestbench" / "experiments" / "v31_guards" / "package_source"
UF1 = REPO / "corpus" / "whestbench" / "experiments" / "uf1_strassen_flop_accounting"
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(UF1))

from cost_model import owned_batched_candidate_bill  # noqa: E402
from uf1_derive_and_verify import matmul_charge, strassen_charge  # noqa: E402

VARIANT = "V1_winograd15_floor"
C_CHAMP, CB, ADJUSTED = 1.7683e11, 0.650, 1.832e-7
B_BUDGET = C_CHAMP / CB
RAW_MSE = ADJUSTED / max(0.1, CB)
PUB_LANE = 145.138e9


def ci95(xs):
    n = len(xs)
    m = statistics.fmean(xs)
    if n < 2:
        return m, m, m
    s = statistics.stdev(xs)
    t = {4: 2.776}.get(n - 1, 1.96)
    h = t * s / math.sqrt(n)
    return m, m - h, m + h


def translate(saving_rel: float) -> dict:
    saved = saving_rel * PUB_LANE
    c_new = C_CHAMP - saved
    return {"C_new": c_new, "C_over_B_new": c_new / B_BUDGET,
            "adjusted_score_new": RAW_MSE * max(0.1, c_new / B_BUDGET),
            "score_improvement_x":
                ADJUSTED / (RAW_MSE * max(0.1, c_new / B_BUDGET))}


def split_cost(m, k, n, d):
    step = 1 << d
    if d == 0:
        return matmul_charge(m, k, n)
    kc, nc = k - k % step, n - n % step
    if m % step or kc == 0 or nc == 0:
        return None
    cost = strassen_charge(m, kc, nc, d, VARIANT)["total"]
    if k - kc:
        cost += matmul_charge(m, k - kc, nc) + m * nc
    if n - nc:
        cost += matmul_charge(m, k, n - nc)
    return cost


def pad_cost(m, k, n, d):
    step = 1 << d
    if d == 0:
        return matmul_charge(m, k, n)
    if m % step:
        return None
    kp = ((k + step - 1) // step) * step
    np_ = ((n + step - 1) // step) * step
    return strassen_charge(m, kp, np_, d, VARIANT)["total"]


def main() -> None:
    raw = json.loads((HERE / "attack_eligibility_raw.json").read_text("utf-8"))
    tapes = raw["tapes"]
    runs = {str(r["seed"]): r for r in raw["runs"]}
    out: dict[str, object] = {}

    # ---- E. headline-shape frequency --------------------------------------
    e_rows = []
    for seed, tape in tapes.items():
        deep = [t for t in tape if t["kind"] == "deep_hook"]
        direct = sum(matmul_charge(t["m"], t["k"], t["n"]) for t in deep)
        full = [t for t in deep if t["k"] == 256 and t["n"] == 256]
        e_rows.append({
            "seed": seed, "deep_hooks": len(deep),
            "hooks_with_k256_n256": len(full),
            "share_of_direct_hook_bill":
                sum(matmul_charge(t["m"], t["k"], t["n"]) for t in full)
                / direct,
            "k_widths": [t["k"] for t in deep],
            "n_widths": [t["n"] for t in deep],
            "odd_k_hooks": sum(1 for t in deep if t["k"] % 2),
            "k_div16_hooks": sum(1 for t in deep if t["k"] % 16 == 0),
            "n_div16_hooks": sum(1 for t in deep if t["n"] % 16 == 0),
        })
    m, lo, hi = ci95([r["share_of_direct_hook_bill"] for r in e_rows])
    out["E_headline_shape_frequency"] = {
        "per_seed": e_rows,
        "mean_share_of_direct_hook_bill": m, "ci95": [lo, hi],
        "mean_hooks_with_k256_n256":
            statistics.fmean([r["hooks_with_k256_n256"] for r in e_rows]),
    }

    # ---- F. direct-baseline double count, on the IDEAL clean shape --------
    M, K, N = 64512, 256, 256
    direct = matmul_charge(M, K, N)
    current = int(owned_batched_candidate_bill(M, K, N).total)
    f = {"shape": f"({M}x{K})@({K}x{N})",
         "direct_charge": direct,
         "champion_current_charge_frozen_operator": current,
         "r_current": current / direct,
         "rows": {}}
    for d in range(1, 6):
        r_d = strassen_charge(M, K, N, d, VARIANT)["total"] / direct
        published_saving = 1.0 - r_d
        honest_saving = 1.0 - (r_d * direct) / current
        f["rows"][f"d{d}"] = {
            "r_d_vs_direct": r_d,
            "published_saving_fraction_of_lane": published_saving,
            "honest_saving_fraction_of_already_winograd_lane": honest_saving,
            "overstatement_x": published_saving / honest_saving,
        }
    out["F_direct_baseline_double_count"] = f

    # ---- G. adaptive per-hook depth ceiling --------------------------------
    g_rows = []
    for seed, tape in tapes.items():
        deep = [t for t in tape if t["kind"] == "deep_hook"]
        run = runs[seed]
        lane, cur = run["matmul_lane_charged"], run["deep_hook_charged"]
        best = {"split": 0, "pad": 0, "strict": 0}
        chosen = {"split": [], "pad": []}
        for t in deep:
            m_, k_, n_ = t["m"], t["k"], t["n"]
            for tag, fn in (("split", split_cost), ("pad", pad_cost)):
                costs = {0: t["charged"]}
                for d in range(1, 6):
                    c = fn(m_, k_, n_, d)
                    if c is not None:
                        costs[d] = c
                bd = min(costs, key=costs.get)
                best[tag] += costs[bd]
                chosen[tag].append(bd)
            cs = {0: t["charged"]}
            for d in range(1, 6):
                step = 1 << d
                if all(v % step == 0 for v in (m_, k_, n_)):
                    cs[d] = strassen_charge(m_, k_, n_, d, VARIANT)["total"]
            best["strict"] += min(cs.values())
        g_rows.append({
            "seed": seed,
            "saving_rel_adaptive_split": (cur - best["split"]) / lane,
            "saving_rel_adaptive_pad": (cur - best["pad"]) / lane,
            "saving_rel_adaptive_strict": (cur - best["strict"]) / lane,
            "depths_chosen_split": chosen["split"],
            "depths_chosen_pad": chosen["pad"],
        })
    g_agg = {}
    for key in ("saving_rel_adaptive_split", "saving_rel_adaptive_pad",
                "saving_rel_adaptive_strict"):
        mm, ll, hh = ci95([r[key] for r in g_rows])
        g_agg[key] = {"mean": mm, "ci95": [ll, hh],
                      "translated": translate(mm),
                      "translated_ci_low": translate(ll),
                      "translated_ci_high": translate(hh)}
    out["G_adaptive_depth_ceiling"] = {"per_seed": g_rows, "aggregate": g_agg}

    (HERE / "attack_stage3.json").write_text(json.dumps(out, indent=2),
                                             encoding="utf-8")
    print("E. headline (rows x256)@(256x256) hooks per net: %.1f of 28; "
          "%.4f%% of the direct hook bill [%.4f%%, %.4f%%]"
          % (out["E_headline_shape_frequency"]["mean_hooks_with_k256_n256"],
             100 * m, 100 * lo, 100 * hi))
    for r in e_rows:
        print("   seed %s: k256n256=%d  odd-k hooks=%d  k%%16==0: %d  "
              "n%%16==0: %d" % (r["seed"], r["hooks_with_k256_n256"],
                                r["odd_k_hooks"], r["k_div16_hooks"],
                                r["n_div16_hooks"]))
    print()
    print("F. clean 64512x256x256: direct=%d  champion-current=%d  r_cur=%.6f"
          % (direct, current, current / direct))
    for d in range(1, 6):
        row = f["rows"][f"d{d}"]
        print("   d=%d published saving %.6f vs honest %.6f  -> %.4fx over"
              % (d, row["published_saving_fraction_of_lane"],
                 row["honest_saving_fraction_of_already_winograd_lane"],
                 row["overstatement_x"]))
    print()
    for key, lab in (("saving_rel_adaptive_strict", "adaptive strict"),
                     ("saving_rel_adaptive_split", "adaptive split"),
                     ("saving_rel_adaptive_pad", "adaptive pad")):
        a = g_agg[key]
        print("G. %-16s saving %.6f  score %.4e  gain %.4fx  "
              "[%.4fx, %.4fx]"
              % (lab, a["mean"], a["translated"]["adjusted_score_new"],
                 a["translated"]["score_improvement_x"],
                 a["translated_ci_low"]["score_improvement_x"],
                 a["translated_ci_high"]["score_improvement_x"]))
    print("wrote attack_stage3.json")


if __name__ == "__main__":
    main()
