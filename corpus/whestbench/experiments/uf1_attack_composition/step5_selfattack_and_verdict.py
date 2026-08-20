"""STEP 5 -- attack my own kill, then consolidate.

Strongest counter-hypotheses against the kill, each tested:

  CH1  "145.138e9 was measured on a pre-Winograd champion, so U-F1's
        classical divisor is correct."
       -> tested by Route 2, which never touches 145.138e9 and uses the
          committed 29-hook trace instead.
  CH2  "The V1 floor (4,4,7) IS the reachable numerator, so r(d) really is
        0.629184 at d=4."
       -> granted here as the numerator while keeping the METERED production
          denominator.  If the kill survives even this, it is schedule-proof.
  CH3  "r_prod = 0.880151 is the wrong divisor because eligible hooks have
        other shapes."
       -> tested by reproducing the committed 11.037909953e9 trace saving
          from the eligible-mass model.
  CH4  "Residual is not charged / is machine-specific."
       -> the FLOP-only kill is recomputed with residual excluded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FROZEN = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
    r"\corpus\whestbench\experiments\v31_guards\package_source"
)
sys.path.insert(0, str(FROZEN))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cost_model import direct_cost  # noqa: E402
from step1_production_baseline import VARIANTS, strassen_charge  # noqa: E402

M, K, N = 64512, 256, 256
CHAMPION_C, CHAMPION_CB, CHAMPION_ADJ = 176.830e9, 0.650, 1.832e-7
B = CHAMPION_C / CHAMPION_CB
RAW_MSE = CHAMPION_ADJ / CHAMPION_CB
MATMUL_LANE = 145.138e9
ELIG = 0.574164
PROD_BILL = 7_427_768_320          # metered, step 1
RATE = 1.0e11


def score(c):
    return RAW_MSE * max(0.1, c / B)


def main():
    classical = direct_cost(M, K, N)
    res = {"DEVIATIONS": [
        "U-F1's V2 'batched' variant is (6,6,7); the frozen production kernel "
        "writes SEVEN blocks on each side (3 copies + 4 arithmetic, "
        "row_blocked_winograd.py lines 110-116 and 137-143), i.e. (7,7,7). "
        "A fifth variant V5=(7,7,7) was added and metered; it is the "
        "production schedule bit-exactly.",
        "flopscope v0.10.0 bills numpy.reshape at 1/element even when it "
        "returns a view. The frozen kernel pays none because its stacks are "
        "preallocated with a leading 7 axis. The depth-d kernel was rewritten "
        "reshape-free (all reshapes hoisted to construction) so the "
        "comparison is not contaminated by an implementation artifact.",
        "Eligibility is held at the depth-1 measured 57.4164% at every depth. "
        "U-F1 itself notes depth 4-5 needs k,n = 0 mod 16/32 so raw "
        "eligibility that deep is worse. Every honest gain below is therefore "
        "an UPPER bound.",
        "Residual wall was measured on this machine, not the graded host. "
        "The FLOP-only kill (CH4 row) does not depend on it.",
    ]}

    # ---- CH2: grant the V1 floor numerator, keep the metered denominator ---
    rows = []
    for d in range(1, 6):
        v1 = strassen_charge(M, K, N, d, VARIANTS["V1_winograd15_floor"])
        v5 = strassen_charge(M, K, N, d, VARIANTS["V5_production_batched_ACTUAL"])
        for label, bill in (("V1_floor_granted", v1),
                            ("V5_production_reachable", v5)):
            f = bill / PROD_BILL
            E = MATMUL_LANE * ELIG
            c = CHAMPION_C - E * (1 - f)
            rows.append({
                "d": d, "numerator_schedule": label, "bill": bill,
                "r_vs_classical": bill / classical,
                "marginal_factor_vs_metered_production": f,
                "C": c, "C_over_B": c / B, "score": score(c),
                "gain_vs_champion": CHAMPION_ADJ / score(c),
            })
    res["CH2_grant_V1_floor_numerator"] = rows
    res["UF1_claimed_gain_d4_at_measured_eligibility"] = 1.2118

    # ---- CH4: FLOP-only, no residual, both numerators, both eligibilities --
    flop_only = {}
    for elabel, e in (("whole_lane", 1.0), ("measured_57.4164pct", ELIG)):
        for label in ("V1_floor_granted", "V5_production_reachable"):
            key = f"{elabel}|{label}"
            flop_only[key] = []
            for d in range(1, 6):
                bill = strassen_charge(
                    M, K, N, d,
                    VARIANTS["V1_winograd15_floor" if label.startswith("V1")
                             else "V5_production_batched_ACTUAL"])
                f = bill / PROD_BILL
                c = CHAMPION_C - MATMUL_LANE * e * (1 - f)
                flop_only[key].append(
                    {"d": d, "gain": CHAMPION_ADJ / score(c)})
    res["CH4_flop_only_no_residual"] = flop_only

    # ---- residual-inclusive trace-level net, from step 4 ------------------
    s4 = json.loads((HERE / "step4_residual_stability.json").read_text())
    equivalents = (161.964214272e9 * ELIG) / classical   # production-products
    net_rows = []
    for name, arm in s4["arms"].items():
        for lo_hi, val in (("mean", arm["NET_effective_saving_mean"]),
                           ("ci_lo", arm["NET_effective_saving_ci95"][0]),
                           ("ci_hi", arm["NET_effective_saving_ci95"][1])):
            c = CHAMPION_C - val * equivalents
            net_rows.append({"arm": name, "bound": lo_hi,
                             "trace_net_effective_saving": val * equivalents,
                             "C": c, "score": score(c),
                             "gain": CHAMPION_ADJ / score(c)})
    res["residual_inclusive_trace_level"] = {
        "production_product_equivalents_in_eligible_mass": equivalents,
        "rows": net_rows,
    }

    # ---- CH3 reproduction check ------------------------------------------
    E_direct = 161.964214272e9 * ELIG
    implied = E_direct * (1 - PROD_BILL / classical)
    res["CH3_divisor_check"] = {
        "model_implied_d1_trace_saving": implied,
        "recorded_d1_trace_saving": 11.037909953e9,
        "relative_agreement": abs(implied - 11.037909953e9) / 11.037909953e9,
    }

    (HERE / "step5_selfattack_and_verdict.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")

    print("CH2/CH4 -- gain vs champion at measured 57.4164% eligibility, "
          "FLOP-only (no residual):")
    for label in ("V1_floor_granted", "V5_production_reachable"):
        g = [r["gain_vs_champion"] for r in rows if r["numerator_schedule"] == label]
        print(f"  {label:26s} d1..d5 = " + " ".join(f"{x:.4f}" for x in g))
    print("  UF1 claimed d=4 = 1.2118")
    print()
    print("residual-inclusive, trace-level "
          f"({equivalents:.3f} production-product equivalents):")
    for r in net_rows:
        if r["bound"] == "mean":
            print(f"  {r['arm']:20s} net {r['trace_net_effective_saving']/1e9:+.2f}e9"
                  f"  gain {r['gain']:.4f}")
    print()
    print("CH3:", res["CH3_divisor_check"])


if __name__ == "__main__":
    main()
