"""Judge check J3: honest FLOP-only score translation.

Corrects two defects in U-F1's published translation, using U-F1's OWN
constants (C, B, raw MSE, lane) so the only thing that changes is the
eligibility/baseline treatment:

  defect 1  baseline: U-F1 charges the saving as (1 - r(d)) x lane, i.e. against
            CLASSICAL direct.  The champion's deep-layer lane already runs the
            one-level Winograd (metered J1: 7,427,768,320 / 8,439,201,792 =
            0.88015).  The honest saving is (shipped - strassen_d).
  defect 2  eligibility: 57.4164% is the DEPTH-1 dispatcher share (J2 reproduces
            it at 0.5708 on fresh seeds).  Depth-d strict eligibility is
            measured per depth from the same traces.

Per-hook counterfactual on the J2 traces, then scaled onto U-F1's headline C.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PKG = REPO / "corpus" / "whestbench" / "experiments" / "v31_guards" / "package_source"
UF1 = REPO / "corpus" / "whestbench" / "experiments" / "uf1_strassen_flop_accounting"
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(UF1))

from cost_model import direct_cost, owned_batched_candidate_bill
from uf1_derive_and_verify import strassen_charge

VARIANT = "V1_winograd15_floor"
C_CHAMP = 1.7683e11
B = C_CHAMP / 0.650
RAW_MSE = 1.832e-7 / 0.650
LANE = 145.138e9            # U-F1's own matmul-lane figure
ADJ_CHAMP = 1.832e-7

traces = json.loads((HERE / "j2_eligibility.json").read_text(encoding="utf-8"))

per_seed = []
for row in traces["rows"]:
    shapes = list(zip([64512] * row["n_deep_hooks"] if False else [],
                      [], []))
    ks = row["k_sequence"]
    ns = row["n_sequence"]
    m = 2 * 126 * 256   # 64512 sampled rows, constant across hooks
    shapes = [(m, k, n) for k, n in zip(ks, ns)]

    direct_b = sum(direct_cost(a, b_, c) for a, b_, c in shapes)
    shipped_b = sum(owned_batched_candidate_bill(a, b_, c).total
                    for a, b_, c in shapes)
    rec = {"seed": row["seed"], "direct": direct_b, "shipped": shipped_b,
           "shipped_over_direct": shipped_b / direct_b,
           "matmul_lane_charged": row["matmul_lane_charged"],
           "deep_hook_share_of_matmul_lane": shipped_b / row["matmul_lane_charged"]}
    for d in range(1, 6):
        step = 1 << d
        new = 0
        for a, b_, c in shapes:
            if all(v % step == 0 for v in (a, b_, c)):
                new += strassen_charge(a, b_, c, d, VARIANT)["total"]
            else:
                new += owned_batched_candidate_bill(a, b_, c).total
        rec[f"counterfactual_bill_d{d}"] = new
        rec[f"saving_fraction_of_shipped_d{d}"] = (shipped_b - new) / shipped_b
        # U-F1's (wrong) law for comparison: (1-r(d)) * f_d1 * direct
        rec[f"uf1_law_saving_fraction_of_shipped_d{d}"] = (
            (1 - strassen_charge(m, 256, 256, d, VARIANT)["total"]
             / direct_cost(m, 256, 256)) * 0.574164 * direct_b / shipped_b)
    per_seed.append(rec)

hook_share = float(np.mean([r["deep_hook_share_of_matmul_lane"] for r in per_seed]))
out = {"per_seed": per_seed,
       "mean_deep_hook_share_of_matmul_lane": hook_share,
       "mean_shipped_over_direct":
           float(np.mean([r["shipped_over_direct"] for r in per_seed]))}


def score(c):
    return RAW_MSE * max(0.1, c / B)


table = {}
for d in range(1, 6):
    frac = float(np.mean([r[f"saving_fraction_of_shipped_d{d}"] for r in per_seed]))
    lo = float(np.min([r[f"saving_fraction_of_shipped_d{d}"] for r in per_seed]))
    hi = float(np.max([r[f"saving_fraction_of_shipped_d{d}"] for r in per_seed]))
    # deep-hook lane in absolute terms = LANE * hook_share
    deep_lane = LANE * hook_share
    dC = frac * deep_lane
    c_new = C_CHAMP - dC
    uf1frac = float(np.mean([r[f"uf1_law_saving_fraction_of_shipped_d{d}"]
                             for r in per_seed]))
    table[f"d{d}"] = {
        "honest_saving_fraction_of_deep_lane_mean": frac,
        "honest_saving_fraction_range": [lo, hi],
        "uf1_implied_saving_fraction_of_deep_lane": uf1frac,
        "overstatement_x": uf1frac / frac if frac > 0 else None,
        "deep_lane_flops": deep_lane,
        "delta_C": dC,
        "C_new": c_new,
        "C_over_B": c_new / B,
        "score": score(c_new),
        "gain_vs_champion": ADJ_CHAMP / score(c_new),
        "gain_at_range_lo": ADJ_CHAMP / score(C_CHAMP - lo * deep_lane),
        "gain_at_range_hi": ADJ_CHAMP / score(C_CHAMP - hi * deep_lane),
    }
out["honest_table"] = table
out["constants"] = {"C": C_CHAMP, "B": B, "raw_MSE": RAW_MSE, "lane": LANE,
                    "adjusted_champion": ADJ_CHAMP}
print(json.dumps({"mean_deep_hook_share_of_matmul_lane": hook_share,
                  "mean_shipped_over_direct": out["mean_shipped_over_direct"],
                  "honest_table": table}, indent=2))
(HERE / "j3_score.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
