"""Deterministic contract checks for the frozen M199 cost ledger."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEDGER = HERE / "m199_cost_ledger.json"


def load_and_validate(path: Path = LEDGER) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in payload["operation_ledger"]}
    required_unknowns = {"U_PROVIDER", "U_M172", "U_M198", "U_TERMINAL", "U_RUNTIME"}
    observed_unknowns = {
        row["symbol"] for row in rows.values() if row.get("amount_billions") is None
    }
    if observed_unknowns != required_unknowns:
        raise ValueError("M199 unknown-cost set changed")

    included = sum(
        rows[name]["amount_billions"]
        for name in (
            "m151_common_fixed",
            "m151_k128_residual_products",
            "m151_endpoint_coefficient_lower_bound",
            "m151_b1_known_core",
        )
    )
    if abs(included - 89.70863624) > 1.0e-12:
        raise ValueError("M151 protected subtotal mismatch")
    scenarios = payload["arithmetic_scenarios"]
    if abs(included + 8.304492288 - scenarios["strict_no_replacement_partial"]) > 1.0e-12:
        raise ValueError("strict partial arithmetic mismatch")
    conditional = included - 7.73675016 + 8.304492288
    if abs(conditional - scenarios["conditional_full_legacy_background_replacement"]) > 1.0e-12:
        raise ValueError("conditional replacement arithmetic mismatch")
    if rows["m125b_corrected_standalone_total"]["overlap_class"] != "embedded_do_not_add":
        raise ValueError("standalone M125b was made additive")
    if payload["disposition"] != "BLOCKED_OVERLAP":
        raise ValueError("M199 disposition drift")
    if payload["gate_results"] != {
        "KILL_COST": False,
        "BLOCKED_OVERLAP": True,
        "COST_COHERENT_COMPONENT": False,
    }:
        raise ValueError("M199 gate result drift")
    return payload


if __name__ == "__main__":
    result = load_and_validate()
    print(result["disposition"])
    print(result["symbolic_total_no_credit"])
