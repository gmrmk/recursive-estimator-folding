"""gm_a4_constraint step 0 -- stage (a) breach arithmetic + regime-coherence gates.

Runs the CHEAPEST falsifier exactly as mined (PREDECLARATION.md sections 4 and 6).
Zero estimator compute. Read-only everywhere except this directory.

Signal 1: every ratio recomputed in THIS process from the primary committed JSON
          (a4_results.json, u2_findings.json, fold_ledger.json) -- never from the
          prose numbers in the mining record.
Signal 2: mechanical source reachability -- token counts in the exact frozen-v3
          source tree A4 invoked (proved by a4_results.json's own traceback paths)
          and in capped_fold3.py, plus the cap constant read from source.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]                      # .../recursive-estimator-folding
SHARE = REPO.parent.parent                  # .../https-chatgpt-com-share-...
WORK = SHARE / "work"

A4 = REPO / "corpus/whestbench/experiments/a_series_granular_adversarial/a4_results.json"
U2 = REPO / "corpus/whestbench/experiments/u2_fold3cap_bound/u2_findings.json"
LEDGER = REPO / "corpus/whestbench/headroom/fold_ledger.json"
CAPPED = REPO / "corpus/whestbench/experiments/t3_fold3_deterministic_cap/capped_fold3.py"
FROZEN_V3 = WORK / "scorefloor_generation/kerdock_l1_owned_buffer/candidate_source_validator_v3"

out = {"experiment": "gm_a4_constraint", "stage": "a (step 0)", "signals": {}}

# ---------------------------------------------------------------- signal 1 ---
a4 = json.loads(A4.read_text(encoding="utf-8"))
u2 = json.loads(U2.read_text(encoding="utf-8"))
ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

B = float(u2["budget_B"])
LAM = float(u2["lambda_flops_per_second"])

# B cross-checked against the ledger invariant text (independent source).
m = re.search(r"C\s*<=\s*(\d+)", ledger["invariants"]["resource_ceiling"])
B_ledger = float(m.group(1))

rows = a4["rows"] + [a4["baseline"]]
worst = max(rows, key=lambda r: r["billed_flops"])
F_worst = int(worst["billed_flops"])

R_up = float(u2["inflation_upper_flops"])          # 3.0e10 FLOP-equiv
R_band = [float(x) for x in u2["inflation_upper_flops_band"]]
R_low = float(u2["inflation_lower_flops"])

S = F_worst + R_up

sig1 = {
    "B_from_u2_findings": B,
    "B_from_ledger_invariant": B_ledger,
    "B_sources_agree": B == B_ledger,
    "lambda_flops_per_s": LAM,
    "worst_hostile_net": worst["net"],
    "worst_hostile_mlp_seed": worst["mlp_seed"],
    "F_worst_billed_flops": F_worst,
    "F_worst_over_B": F_worst / B,
    "a4_recorded_budget_breach": worst["budget_breach"],
    "a4_recorded_headroom_flops": int(B) - F_worst,
    "a4_recorded_headroom_frac": (B - F_worst) / B,
    "u2_residual_upper_flop_equiv": R_up,
    "u2_residual_upper_band": R_band,
    "u2_residual_lower_flop_equiv": R_low,
    "u2_residual_upper_seconds": R_up / LAM,
    "SUM_S": S,
    "SUM_S_over_B": S / B,
    "a4_rows_record_residual_seconds": any(
        "residual" in k for r in rows for k in r
    ),
    "a4_regime_walls_s_cold_subprocess": a4["determinism"]["subprocess_walls_s"],
}
out["signals"]["s1_arithmetic_from_primary_json"] = sig1

# ---------------------------------------------------------------- signal 2 ---
def count_tokens(paths, tokens):
    tot = {t: 0 for t in tokens}
    files = []
    for p in sorted(paths):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        files.append(p.name)
        for t in tokens:
            tot[t] += txt.count(t)
    return tot, files

TOKENS = ["budget_summary_dict", "_tally", "summary_dict", "get_data("]
v3_counts, v3_files = count_tokens(FROZEN_V3.glob("*.py"), TOKENS)
cap_counts, _ = count_tokens([CAPPED], TOKENS + ["get_active_budget"])

cap_src = CAPPED.read_text(encoding="utf-8")
cap_const = re.search(r"cap_billed_flops\s*=\s*([0-9.eE+]+)", cap_src)
# The source literal is a plain float literal ("244.8e9"); float() parses it directly.
CAP = float(cap_const.group(1))
fix_applied = "get_active_budget().flops_used" in cap_src

sig2 = {
    "frozen_v3_dir": str(FROZEN_V3),
    "frozen_v3_py_files": v3_files,
    "frozen_v3_token_counts": v3_counts,
    "capped_fold3_token_counts": cap_counts,
    "CAP_from_source": CAP,
    "CAP_over_B": CAP / B,
    "u2_one_line_fix_already_on_disk": fix_applied,
}
out["signals"]["s2_source_reachability"] = sig2

# ------------------------------------------------------------------- gates ---
G0A_alive = S > B
B1 = v3_counts["budget_summary_dict"] > 0          # residual source reachable from F-producing path
B2 = F_worst <= CAP                                # F reachable in the residual-producing regime
G0B_alive = B1 or B2

S_coh = CAP + R_up                                 # the only coherent variant
G0C_alive = not fix_applied                        # coherent variant already committed+fixed => re-litigation

gates = {
    "G0A_arithmetic": {
        "computed_sum": S,
        "B": B,
        "sum_over_B": S / B,
        "alive": bool(G0A_alive),
        "note": "sum > B, so the arithmetic alone does not kill; it is not the discriminator",
    },
    "G0B_co_occurrence": {
        "B1_residual_source_reachable_from_frozen_v3": bool(B1),
        "B1_evidence_count_budget_summary_dict_in_frozen_v3": v3_counts["budget_summary_dict"],
        "B2_F_worst_reachable_under_cap": bool(B2),
        "B2_evidence": f"F_worst {F_worst} vs CAP {CAP:.0f}; excess {F_worst - CAP:.0f}",
        "alive": bool(G0B_alive),
    },
    "G0C_novelty": {
        "only_coherent_variant_CAP_plus_residual": S_coh,
        "coherent_variant_over_B": S_coh / B,
        "already_committed_in_U2_section4": u2["adjusted_delta"]["catastrophic_tail"],
        "u2_fix_already_on_disk": bool(fix_applied),
        "alive": bool(G0C_alive),
    },
}
out["gates"] = gates

alive = G0A_alive and G0B_alive and G0C_alive
out["step0_verdict"] = "ALIVE -> run stage (b)" if alive else "KILLED_AT_STEP0"
out["stage_b_run"] = bool(alive)

(HERE / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

print(json.dumps(out, indent=2))
