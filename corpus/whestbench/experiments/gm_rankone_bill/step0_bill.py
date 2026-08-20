"""Step-0 arithmetic gate for gm_rankone_bill.

Re-prices the M203/M204/M205/M206 static bills at dtype_multiplier = 1.0
(float32) using the FROZEN modules' own cost functions where they exist.
No frozen file is modified; m203's constants are re-applied, not rewritten.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(EXP / "m205_rankone_complete_physical_owner"))
sys.path.insert(0, str(EXP / "m203_terminal_contraction_circuit_no_go"))

import m203_terminal_contraction_circuit_no_go as M203  # noqa: E402
from m205_rankone_complete_physical_owner import (  # noqa: E402
    SOURCE_LAYERS,
    STRICT_COMPOSED_HEADROOM,
    WIDTH,
    PROTECTION,
    source_cost_and_blockers,
)

H = STRICT_COMPOSED_HEADROOM
N = WIDTH
L = SOURCE_LAYERS

square_f32 = 2 * N**3 - N**2
a_term_f32 = 2 * N * N - N  # M204/M206 a = u^T W, per source layer

# ---- frozen f64 record (independent recomputation signal #1) ----
frozen = source_cost_and_blockers()

# ---- f32 re-pricing (dtype_multiplier = 1.0) ----
m205_raw_f32 = L * square_f32
m205_prot_f32 = int(math.ceil(PROTECTION * m205_raw_f32))
m204_raw_f32 = L * square_f32 + L * a_term_f32
m204_prot_f32 = int(math.ceil(PROTECTION * m204_raw_f32))

# ---- M203 at F64_RATE -> 1, using the frozen bill functions verbatim ----
def m203_protected_terminal_f32(depth: int) -> int:
    raw = M203.recursive_winograd_bill(N, 3 * N, N, depth)
    raw += M203.recursive_winograd_bill(N, 2 * N, N, depth)
    return raw * L * 1 * M203.PROTECTION_NUMERATOR // M203.PROTECTION_DENOMINATOR


def m203_protected_projection_f32() -> int:
    raw = 2 * N * (N - 1) ** 2
    return raw * L * 1 * M203.PROTECTION_NUMERATOR // M203.PROTECTION_DENOMINATOR


m203_rows = []
for depth in range(3, 7):
    t64 = M203.protected_terminal_bill(depth)
    t32 = m203_protected_terminal_f32(depth)
    p64 = M203.protected_ideal_projection_bill()
    p32 = m203_protected_projection_f32()
    m203_rows.append(
        {
            "depth": depth,
            "terminal_f64": t64,
            "terminal_f32": t32,
            "projection_f64": p64,
            "projection_f32": p32,
            "combined_f64": t64 + p64,
            "combined_f32": t32 + p32,
            "vs_m151_slot_f32": (t32 + p32) - M203.M151_SLOT,
            "vs_strict_headroom_f32": (t32 + p32) - H,
        }
    )
m203_best = min(m203_rows, key=lambda r: r["combined_f32"])

result = {
    "strict_composed_headroom": H,
    "m151_slot": M203.M151_SLOT,
    "square_f32": square_f32,
    "a_term_per_layer_f32": a_term_f32,
    "frozen_f64_record": {
        "m205_one_f64_square_raw": frozen["one_f64_square_raw"],
        "m205_one_f64_square_protected": frozen["one_f64_square_protected"],
    },
    "f32_repricing": {
        "m205_raw": m205_raw_f32,
        "m205_protected": m205_prot_f32,
        "m205_slack_vs_headroom": H - m205_prot_f32,
        "m205_pct_under": 100.0 * (H - m205_prot_f32) / H,
        "m204_m206_raw": m204_raw_f32,
        "m204_m206_protected": m204_prot_f32,
        "m204_m206_slack_vs_headroom": H - m204_prot_f32,
        "m204_m206_pct_under": 100.0 * (H - m204_prot_f32) / H,
    },
    "m203_rows": m203_rows,
    "m203_best_depth": m203_best["depth"],
    "m203_best_combined_f32": m203_best["combined_f32"],
    "m203_pct_under_m151_slot": 100.0
    * (M203.M151_SLOT - m203_best["combined_f32"])
    / M203.M151_SLOT,
    "m203_over_strict_headroom": m203_best["combined_f32"] > H,
}

# ---- predeclared expectations (PREDECLARATION.md section 3) ----
expect = {
    "m205_raw": 1_038_155_776,
    "m205_protected": 1_297_694_720,
    "m205_slack_vs_headroom": 689_176_752,
    "m204_m206_raw": 1_042_211_072,
    "m204_m206_protected": 1_302_763_840,
    "m204_m206_slack_vs_headroom": 684_107_632,
}
result["predeclared_match"] = {
    k: (result["f32_repricing"][k] == v) for k, v in expect.items()
}
result["predeclared_all_match"] = all(result["predeclared_match"].values())
result["m203_combined_f32_matches_mined_5_271_889_760"] = (
    m203_best["combined_f32"] == 5_271_889_760
)

# ---- frozen f64 record reproduction ----
result["frozen_f64_reproduced"] = (
    frozen["one_f64_square_raw"] == 2_076_311_552
    and frozen["one_f64_square_protected"] == 2_595_389_440
    and M203.protected_terminal_bill(5) == 7_963_587_520
    and M203.protected_ideal_projection_bill() == 2_580_192_000
    and M203.protected_terminal_bill(5) + M203.protected_ideal_projection_bill()
    == 10_543_779_520
)

step0_kill = (m205_prot_f32 >= H) or (m204_prot_f32 >= H)
result["step0_gate"] = "KILL" if step0_kill else "PASS"

out = HERE / "step0_bill.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
