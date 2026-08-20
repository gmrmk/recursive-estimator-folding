"""STEP 0 of gm_m179_m199: the mined falsifier's arithmetic/metering gate (b).

Re-meters the M179 per-layer matmul bill live through flopscope 0.10.0 and
evaluates the 32-layer inclusive bill against 9.723621632e9.

Response-free: generated shapes only. Reads no truth/scorer/holdout.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
sys.path.insert(0, str(EXPERIMENTS / "m179_background_archive_producer"))

import m179_metering as met  # noqa: E402  (frozen module, imported read-only)

# --- M199 ledger anchors (verbatim from m199_cost_ledger.json) ---------------
M151_SUBTOTAL = Fraction("89.70863624")
LEGACY_ROW = Fraction("7.73675016")
STRICT_PARTIAL = Fraction("98.013128528")
STRICT_HEADROOM = Fraction("1.986871472")
COND_REPL_HEADROOM = Fraction("9.723621632")
COND_REPL_TOTAL = Fraction("90.276378368")
M179_31_TOTAL = Fraction("8.304492288")
ENDPOINT = Fraction(100)
RESERVE = Fraction(5, 4)

GATE_B_THRESHOLD = 9.723621632e9


def main() -> None:
    # --- live re-metering ---------------------------------------------------
    mm_metered = met.metered_layer_matmul_flops()
    pairs = met.N * (met.N - 1) // 2
    per_pair = met.F_M178 + met.F_ASSEMBLY_PER_PAIR
    pair_layer = pairs * per_pair
    diag_layer = met.N * met.F_DIAG_PER_NEURON
    per_layer = pair_layer + diag_layer + mm_metered

    # second signal on the frozen 31-layer ledger: reproduce it exactly
    ledger31 = met.inclusive_ledger()
    frozen31 = json.loads(
        (EXPERIMENTS / "m179_background_archive_producer"
         / "M179_RESULTS_20260807.json").read_text(encoding="utf-8")
    )["inclusive_flop_ledger"]

    b31 = per_layer * 31
    b32 = per_layer * 32
    marginal = per_layer

    # --- ledger identity cross-checks --------------------------------------
    id1 = (LEGACY_ROW + STRICT_HEADROOM) == COND_REPL_HEADROOM
    id2 = (ENDPOINT - COND_REPL_TOTAL) == COND_REPL_HEADROOM
    id3 = (STRICT_PARTIAL - LEGACY_ROW) == COND_REPL_TOTAL
    id4 = (M151_SUBTOTAL + M179_31_TOTAL) == STRICT_PARTIAL
    id5 = Fraction(b31, 10 ** 9) == M179_31_TOTAL

    b32_frac = Fraction(b32, 10 ** 9)
    t_a = M151_SUBTOTAL + b32_frac - LEGACY_ROW
    t_b = M151_SUBTOTAL + RESERVE * b32_frac - LEGACY_ROW
    strict_conv_b = M151_SUBTOTAL + RESERVE * Fraction(b31, 10 ** 9)

    gate0_pass = float(b32) <= GATE_B_THRESHOLD
    gate0x_pass = t_a <= ENDPOINT

    out = {
        "step": "STEP 0 metering / arithmetic gate",
        "metered": {
            "matmul_flops_per_layer_METERED_live": int(mm_metered),
            "matmul_flops_per_layer_frozen_2026_08_07": int(
                frozen31["matmul_flops_per_layer_metered"]),
            "matmul_reproduces_frozen": int(mm_metered) == int(
                frozen31["matmul_flops_per_layer_metered"]),
            "pairs_per_layer": int(pairs),
            "per_pair_flops": int(per_pair),
            "pair_flops_per_layer": int(pair_layer),
            "diag_flops_per_layer": int(diag_layer),
            "per_layer_flops": int(per_layer),
            "frozen_per_layer_flops": int(frozen31["per_layer_flops"]),
            "per_layer_reproduces_frozen": int(per_layer) == int(
                frozen31["per_layer_flops"]),
            "frozen_module_inclusive_ledger_31": {
                k: int(v) if isinstance(v, int) else v
                for k, v in ledger31.items()},
        },
        "bills": {
            "B31_31_layer_inclusive": int(b31),
            "B31_frozen_total_producer_flops": int(
                frozen31["total_producer_flops"]),
            "B31_reproduces_frozen": int(b31) == int(
                frozen31["total_producer_flops"]),
            "marginal_layer_32_flops": int(marginal),
            "B32_32_layer_inclusive": int(b32),
            "B32_billions": float(b32) / 1e9,
        },
        "ledger_identities": {
            "legacy_row + strict_headroom == cond_repl_headroom": id1,
            "100 - cond_repl_total == cond_repl_headroom": id2,
            "strict_partial - legacy_row == cond_repl_total": id3,
            "m151_subtotal + m179_31 == strict_partial": id4,
            "metered_B31 == ledger m179_standalone_total": id5,
        },
        "GATE_0": {
            "quantity": "B32 (32-layer inclusive metered bill), FLOPs",
            "value": int(b32),
            "value_billions": float(b32) / 1e9,
            "threshold_billions": GATE_B_THRESHOLD / 1e9,
            "margin_billions": (GATE_B_THRESHOLD - float(b32)) / 1e9,
            "verdict": "PASS" if gate0_pass else "KILL_COST",
        },
        "GATE_0X_convention_crosscheck": {
            "T_A_post_replacement_total_convA_billions": float(t_a),
            "T_A_headroom_billions": float(ENDPOINT - t_a),
            "T_A_matches_mined_expected_90_544": abs(float(t_a) - 90.544265216) < 1e-9,
            "T_B_post_replacement_total_convB_1p25_billions": float(t_b),
            "T_B_headroom_billions": float(ENDPOINT - t_b),
            "strict_no_replacement_convB_billions": float(strict_conv_b),
            "strict_no_replacement_convB_matches_ledger_100_0892516":
                abs(float(strict_conv_b) - 100.0892516) < 1e-9,
            "verdict": "PASS" if gate0x_pass else "KILL_COST",
        },
    }
    (HERE / "step0_results.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
