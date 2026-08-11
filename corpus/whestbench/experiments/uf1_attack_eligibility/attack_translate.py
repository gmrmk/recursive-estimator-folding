"""U-F1 eligibility attack, stage 2.

Consumes attack_eligibility_raw.json (measured per-hook logical shapes and
charges from the frozen v3.1 GUARDS predict path) and:

  A. VERIFIES the tape: each measured per-hook charge must equal the frozen
     cost_model.owned_batched_candidate_bill total for that shape, exactly.
     (Second, independent signal that the tape is the real dispatch bill.)
  B. Reproduces the CONSTRUCTION of the published 57.4164% figure under the
     frozen depth-1 dispatcher rule, on our nets.
  C. Computes honest depth-d eligibility three ways and re-runs the published
     score translation with the corrected number.
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

# Published champion constants (UF1_ACCOUNTING.md section "Adjusted-score
# translation").  Used unchanged so the correction is attributable to the
# eligibility term alone.
C_CHAMP = 1.7683e11
CB = 0.650
ADJUSTED = 1.832e-7
B_BUDGET = C_CHAMP / CB
RAW_MSE = ADJUSTED / max(0.1, CB)
PUB_LANE = 145.138e9
PUB_ELIG = 0.574164


def ci95(xs):
    n = len(xs)
    m = statistics.fmean(xs)
    if n < 2:
        return m, m, m
    s = statistics.stdev(xs)
    t = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}.get(n - 1, 1.96)
    h = t * s / math.sqrt(n)
    return m, m - h, m + h


def translate(saving_rel: float, lane: float = PUB_LANE) -> dict:
    saved = saving_rel * lane
    c_new = C_CHAMP - saved
    cb_new = c_new / B_BUDGET
    mult = max(0.1, cb_new)
    score = RAW_MSE * mult
    return {"lane_saving_fraction": saving_rel, "flops_saved": saved,
            "C_new": c_new, "C_over_B_new": cb_new,
            "adjusted_score_new": score,
            "score_improvement_x": ADJUSTED / score}


def main() -> None:
    raw = json.loads((HERE / "attack_eligibility_raw.json").read_text("utf-8"))
    tapes = raw["tapes"]
    runs = {str(r["seed"]): r for r in raw["runs"]}
    out: dict[str, object] = {}

    # ---- A. tape verification against the frozen cost model ---------------
    ver = {"checked": 0, "exact": 0, "mismatches": []}
    for seed, tape in tapes.items():
        for t in tape:
            if t["kind"] != "deep_hook":
                continue
            bill = owned_batched_candidate_bill(t["m"], t["k"], t["n"])
            ver["checked"] += 1
            if int(bill.total) == int(t["charged"]):
                ver["exact"] += 1
            else:
                ver["mismatches"].append(
                    {"seed": seed, "m": t["m"], "k": t["k"], "n": t["n"],
                     "measured": t["charged"], "cost_model": int(bill.total),
                     "strategy": bill.strategy})
    ver["all_exact"] = ver["checked"] == ver["exact"]
    out["A_tape_verification_vs_frozen_cost_model"] = ver

    # ---- B. reproduce the published 57.4164% construction -----------------
    # "16 of 29 hooks dispatched Winograd ... those eligible calls represented
    # 57.4164% of the direct hook bill."  Dispatcher rule (cost_model): m even
    # AND k even; an odd n is served by a 1-column direct tail, so odd n is
    # still 'eligible'.  That is a DEPTH-1 rule.
    b_rows = []
    for seed, tape in tapes.items():
        deep = [t for t in tape if t["kind"] == "deep_hook"]
        direct = sum(matmul_charge(t["m"], t["k"], t["n"]) for t in deep)
        sel = [t for t in deep
               if owned_batched_candidate_bill(
                   t["m"], t["k"], t["n"]).strategy.startswith("winograd")]
        sel_direct = sum(matmul_charge(t["m"], t["k"], t["n"]) for t in sel)
        b_rows.append({
            "seed": seed, "hooks": len(deep), "winograd_selected": len(sel),
            "call_fraction": len(sel) / len(deep),
            "eligible_share_of_direct_hook_bill": sel_direct / direct,
        })
    b_mean, b_lo, b_hi = ci95([r["eligible_share_of_direct_hook_bill"]
                               for r in b_rows])
    out["B_depth1_dispatcher_eligibility"] = {
        "per_seed": b_rows,
        "mean": b_mean, "ci95": [b_lo, b_hi],
        "published_figure": PUB_ELIG,
        "note": "depth-1 rule (k even; odd n served by a direct tail); this is "
                "the quantity the published 0.574164 measures.",
    }

    # ---- C. honest depth-d eligibility + corrected translation ------------
    depths = list(range(1, 6))
    c_out: dict[str, object] = {}
    for d in depths:
        step = 1 << d
        per_seed = []
        for seed, tape in tapes.items():
            deep = [t for t in tape if t["kind"] == "deep_hook"]
            run = runs[seed]
            lane = run["matmul_lane_charged"]
            cur_hook = run["deep_hook_charged"]
            direct_hook = sum(matmul_charge(t["m"], t["k"], t["n"])
                              for t in deep)

            # C1 STRICT: only hooks whose m,k,n are all divisible by 2^d
            # recurse; every other hook keeps its CURRENT measured charge.
            new_strict = 0
            elig_direct = 0
            n_elig = 0
            for t in deep:
                if all(v % step == 0 for v in (t["m"], t["k"], t["n"])):
                    s = strassen_charge(t["m"], t["k"], t["n"], d,
                                        VARIANT)["total"]
                    new_strict += min(s, t["charged"])
                    elig_direct += matmul_charge(t["m"], t["k"], t["n"])
                    n_elig += 1
                else:
                    new_strict += t["charged"]

            # C2 SPLIT: lawful ragged decomposition.  Recurse on the largest
            # 2^d-divisible core (kc x nc), charge the k-slab and n-tail direct,
            # plus the m*nc combining add for the k-split.
            new_split = 0
            for t in deep:
                m, k, n = t["m"], t["k"], t["n"]
                kc, nc = k - k % step, n - n % step
                if m % step or kc == 0 or nc == 0:
                    new_split += t["charged"]
                    continue
                cost = strassen_charge(m, kc, nc, d, VARIANT)["total"]
                if k - kc:
                    cost += matmul_charge(m, k - kc, nc) + m * nc
                if n - nc:
                    cost += matmul_charge(m, k, n - nc)
                new_split += min(cost, t["charged"])

            # C3 PAD: pad k,n up to the next multiple of 2^d and pay the full
            # padded volume (the published envelope's rule).
            new_pad = 0
            for t in deep:
                m, k, n = t["m"], t["k"], t["n"]
                kp = ((k + step - 1) // step) * step
                np_ = ((n + step - 1) // step) * step
                if m % step:
                    new_pad += t["charged"]
                    continue
                cost = strassen_charge(m, kp, np_, d, VARIANT)["total"]
                new_pad += min(cost, t["charged"])

            # published-shape counterfactual: whole hook lane treated as
            # direct and 57.4164% of it eligible at depth d.
            r_d = (strassen_charge(64512, 256, 256, d, VARIANT)["total"]
                   / matmul_charge(64512, 256, 256))

            per_seed.append({
                "seed": seed,
                "eligible_calls_strict": n_elig,
                "strict_eligible_share_of_direct_hook_bill":
                    elig_direct / direct_hook,
                "saving_rel_strict": (cur_hook - new_strict) / lane,
                "saving_rel_split": (cur_hook - new_split) / lane,
                "saving_rel_pad": (cur_hook - new_pad) / lane,
                "published_saving_rel": (1.0 - r_d) * PUB_ELIG,
                "effective_eligibility_strict":
                    ((cur_hook - new_strict) / lane) / (1.0 - r_d),
                "effective_eligibility_split":
                    ((cur_hook - new_split) / lane) / (1.0 - r_d),
                "effective_eligibility_pad":
                    ((cur_hook - new_pad) / lane) / (1.0 - r_d),
                "r_d_reference_shape": r_d,
            })
        agg = {}
        for key in ("saving_rel_strict", "saving_rel_split", "saving_rel_pad",
                    "strict_eligible_share_of_direct_hook_bill",
                    "effective_eligibility_strict",
                    "effective_eligibility_split",
                    "effective_eligibility_pad"):
            m, lo, hi = ci95([p[key] for p in per_seed])
            agg[key] = {"mean": m, "ci95": [lo, hi]}
        r_d = per_seed[0]["r_d_reference_shape"]
        agg["r_d_reference_shape"] = r_d
        agg["published"] = translate((1.0 - r_d) * PUB_ELIG)
        agg["published"]["assumed_eligibility"] = PUB_ELIG
        agg["corrected_strict"] = translate(agg["saving_rel_strict"]["mean"])
        agg["corrected_strict_ci_low"] = translate(
            agg["saving_rel_strict"]["ci95"][0])
        agg["corrected_strict_ci_high"] = translate(
            agg["saving_rel_strict"]["ci95"][1])
        agg["corrected_split"] = translate(agg["saving_rel_split"]["mean"])
        agg["corrected_pad"] = translate(agg["saving_rel_pad"]["mean"])
        c_out[f"d{d}"] = {"per_seed": per_seed, "aggregate": agg}
    out["C_corrected_translation"] = c_out

    # ---- D. lane structure ------------------------------------------------
    lane_rows = []
    for seed, run in runs.items():
        lane_rows.append({
            "seed": seed,
            "total_charged": run["total_charged"],
            "matmul_lane": run["matmul_lane_charged"],
            "matmul_share_of_total":
                run["matmul_lane_charged"] / run["total_charged"],
            "deep_hook_charged": run["deep_hook_charged"],
            "hook_share_of_matmul_lane":
                run["deep_hook_charged"] / run["matmul_lane_charged"],
            "first_product_charged_WHT_not_matmul":
                run["first_product_charged"],
        })
    m1, lo1, hi1 = ci95([r["matmul_share_of_total"] for r in lane_rows])
    m2, lo2, hi2 = ci95([r["hook_share_of_matmul_lane"] for r in lane_rows])
    m3, lo3, hi3 = ci95([r["total_charged"] for r in lane_rows])
    out["D_lane_structure"] = {
        "per_seed": lane_rows,
        "matmul_share_of_total": {"mean": m1, "ci95": [lo1, hi1]},
        "deep_hook_share_of_matmul_lane": {"mean": m2, "ci95": [lo2, hi2]},
        "total_charged_predict": {"mean": m3, "ci95": [lo3, hi3]},
    }

    (HERE / "attack_translation.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    # ---- console summary --------------------------------------------------
    print("A. tape vs frozen cost model: %d/%d exact"
          % (ver["exact"], ver["checked"]))
    print("B. depth-1 dispatcher eligibility (our nets): %.4f%% "
          "[%.4f%%, %.4f%%]  vs published %.4f%%"
          % (100 * b_mean, 100 * b_lo, 100 * b_hi, 100 * PUB_ELIG))
    for r in b_rows:
        print("   seed %s: %2d/%2d winograd, %.4f%% of direct hook bill"
              % (r["seed"], r["winograd_selected"], r["hooks"],
                 100 * r["eligible_share_of_direct_hook_bill"]))
    print()
    hdr = ("  d  r(d)     strict elig   eff.elig(strict)  gain(strict)  "
           "gain(split)  gain(pad)  published gain")
    print(hdr)
    for d in depths:
        a = c_out[f"d{d}"]["aggregate"]
        print("  %d  %.6f  %6.3f%%      %6.3f%%          %.4fx      %.4fx     "
              "%.4fx    %.4fx"
              % (d, a["r_d_reference_shape"],
                 100 * a["strict_eligible_share_of_direct_hook_bill"]["mean"],
                 100 * a["effective_eligibility_strict"]["mean"],
                 a["corrected_strict"]["score_improvement_x"],
                 a["corrected_split"]["score_improvement_x"],
                 a["corrected_pad"]["score_improvement_x"],
                 a["published"]["score_improvement_x"]))
    a4 = c_out["d4"]["aggregate"]
    print()
    print("d=4 corrected adjusted score (strict): %.4e  [%.4e, %.4e]  "
          "gain %.4fx  (published %.4e / %.4fx)"
          % (a4["corrected_strict"]["adjusted_score_new"],
             a4["corrected_strict_ci_high"]["adjusted_score_new"],
             a4["corrected_strict_ci_low"]["adjusted_score_new"],
             a4["corrected_strict"]["score_improvement_x"],
             a4["published"]["adjusted_score_new"],
             a4["published"]["score_improvement_x"]))
    print("wrote attack_translation.json")


if __name__ == "__main__":
    main()
