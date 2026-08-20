"""STEP 0: re-derive M160's resource verdict at k=1 from the CACHED 2026-08-07
audit. Zero compute. If this kills, gm_residual_k1 stops here."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHED = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c"
    r"\work\scorefloor_generation\terra_m160_hostile_deploy"
    r"\M160_HOSTILE_AUDIT_20260807.json"
)
GATE = 258.4e9
LAMBDA = 1e11


def charge(billed: int, residual_s: float, k: float) -> float:
    return float(billed) + LAMBDA * float(k) * float(residual_s)


def main() -> None:
    audit = json.loads(CACHED.read_text(encoding="utf-8"))
    rows = []
    for index, target in enumerate(audit["targets"], start=1):
        first = target["first_predict"]
        billed = int(first["billed_flops"])
        residual = float(first["residual_s"])
        k1 = charge(billed, residual, 1)
        k5 = charge(billed, residual, 5)
        rows.append(
            {
                "worker": index,
                "seeds": target["seeds"],
                "billed_flops": billed,
                "residual_s": residual,
                "C_k1": k1,
                "C_k5": k5,
                "cached_effective_compute_field": first["effective_compute"],
                "cached_hostile_5x_field": first["hostile_effective_compute_5x_residual"],
                "recompute_matches_field_k1": abs(k1 - first["effective_compute"]) <= 1e-6 * k1,
                "recompute_matches_field_k5": abs(
                    k5 - first["hostile_effective_compute_5x_residual"]
                )
                <= 1e-6 * k5,
                "k1_margin_to_gate": GATE - k1,
                "k1_margin_pct": 100.0 * (GATE - k1) / GATE,
                "break_even_k": (GATE - billed) / (LAMBDA * residual),
                "residual_ceiling_s_at_k1": (GATE - billed) / LAMBDA,
                "passes_k1": k1 < GATE,
                "passes_k5": k5 < GATE,
            }
        )
    worst_k1 = max(row["C_k1"] for row in rows)
    worst_k5 = max(row["C_k5"] for row in rows)
    result = {
        "arm": "STEP0_CACHED_ARITHMETIC_ONLY",
        "source": str(CACHED),
        "gate": GATE,
        "lambda": LAMBDA,
        "rows": rows,
        "max_C_k1": worst_k1,
        "max_C_k5": worst_k5,
        "k1_pass_count": sum(row["passes_k1"] for row in rows),
        "k5_pass_count": sum(row["passes_k5"] for row in rows),
        "recompute_all_match": all(
            row["recompute_matches_field_k1"] and row["recompute_matches_field_k5"]
            for row in rows
        ),
        "step0_verdict": "PASS_PROCEED_TO_ARM_A" if worst_k1 < GATE else "KILLED_AT_STEP0",
    }
    (HERE / "step0_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for row in rows:
        print(
            f"w{row['worker']} billed={row['billed_flops']/1e9:.9f}B "
            f"resid={row['residual_s']:.6f}s C_k1={row['C_k1']/1e9:.9f}B "
            f"C_k5={row['C_k5']/1e9:.9f}B k*={row['break_even_k']:.4f} "
            f"k1={'PASS' if row['passes_k1'] else 'FAIL'} "
            f"k5={'PASS' if row['passes_k5'] else 'FAIL'}"
        )
    print(
        json.dumps(
            {
                "max_C_k1": worst_k1,
                "max_C_k5": worst_k5,
                "k1_pass_count": result["k1_pass_count"],
                "k5_pass_count": result["k5_pass_count"],
                "recompute_all_match": result["recompute_all_match"],
                "step0_verdict": result["step0_verdict"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
