"""Exact static ledger for M214's new complete-domain architecture."""

from __future__ import annotations

from decimal import Decimal as D
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUDGET = D("100")


def _s(value: D) -> str:
    return f"{value:.9f}"


def build_ledger() -> dict[str, object]:
    common = D("80.326002640")
    products = D("3.247411200")
    old_endpoint = D("2.407464960")
    old_b1 = D("3.727757440")
    source_total = common + products + old_endpoint + old_b1
    m179 = D("8.304492288")
    m212 = D("1.249253376")
    m213 = D("0.048568320")
    terminal_floor = D("0.134217216")
    known = common + products + m179 + m212 + m213
    remaining = BUDGET - known
    with_terminal = known + terminal_floor
    rows = [
        {
            "id": "m151_common_fixed",
            "amount_billions": _s(common),
            "disposition": "retained_fully_charged",
            "note": "old collision outputs must be retired semantically even if their cost remains",
        },
        {
            "id": "m151_k128_residual_products",
            "amount_billions": _s(products),
            "disposition": "retained_fully_charged",
        },
        {
            "id": "m151_endpoint_provider",
            "amount_billions": _s(old_endpoint),
            "disposition": "removed_by_new_dag",
        },
        {
            "id": "m151_b1_core",
            "amount_billions": _s(old_b1),
            "disposition": "removed_by_new_dag",
        },
        {
            "id": "m179",
            "amount_billions": _s(m179),
            "disposition": "fully_additive",
            "note": "no legacy-background replacement credit",
        },
        {
            "id": "m212",
            "amount_billions": _s(m212),
            "disposition": "fully_additive_new_call",
            "note": "not arithmetic-identical to M151 distinct-only source emission",
        },
        {
            "id": "m213",
            "amount_billions": _s(m213),
            "disposition": "conditional_new_call_unearned",
            "note": "provider-only projection pending independent identity and native cost gates",
        },
    ]
    return {
        "candidate": "M214 complete-domain replacement DAG ledger",
        "status": "BLOCKED_COMPLETE_DOMAIN_REPLACEMENT_DAG",
        "source_m151_total": _s(source_total),
        "known_replacement_subtotal": _s(known),
        "remaining_before_unknowns": _s(remaining),
        "terminal_floor_sensitivity_total": _s(with_terminal),
        "after_terminal_floor_sensitivity": _s(BUDGET - with_terminal),
        "rows": rows,
        "legacy_background_replacement_credit": False,
        "provider_pass_assumed": False,
        "cost_coherent": False,
        "variance_or_efficacy_authorized": False,
        "unknowns": [
            "complete-owner issuer and old-collision output retirement",
            "M179-bound M212 all-layer factor lifecycle",
            "M213 inclusive event/provider RNG and local unary arithmetic",
            "M198 conversion under the next pre-ReLU context",
            "terminal response beyond the explicit floor",
            "copies, allocations, provenance, and integrated residual wall",
        ],
        "gate": (
            "sum(all unknown effective costs) <= 6.824272176B, M213 passes, "
            "and one native caller proves exact M205 conservation"
        ),
        "firewall": "response-free static ledger; no contest or efficacy data",
    }


if __name__ == "__main__":
    result = build_ledger()
    output = HERE / "M214_RESULTS_20260809.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "status": result["status"]}, sort_keys=True))
