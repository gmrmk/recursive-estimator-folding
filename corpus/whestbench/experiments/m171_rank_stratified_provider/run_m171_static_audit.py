"""Verify the frozen M171 response-free static audit without writing outputs."""

from __future__ import annotations

import json
from pathlib import Path

from m171_rank_stratified_provider import audit_record, final_disposition, regularity_obstruction
from fractions import Fraction


ROOT = Path(__file__).resolve().parent


def main() -> None:
    frozen = json.loads((ROOT / "M171_STATIC_AUDIT_20260807.json").read_text(encoding="utf-8"))
    obstruction = regularity_obstruction(Fraction(1, 10))
    expected_floor = "675537109375000/323419945960784673"
    if f"{obstruction.gauss_legendre_remainder_floor.numerator}/{obstruction.gauss_legendre_remainder_floor.denominator}" != expected_floor:
        raise SystemExit("M171 exact derivative-envelope floor changed")
    if frozen["uniform_error_enclosure"]["remainder_envelope_floor"] != expected_floor:
        raise SystemExit("frozen M171 audit has a different derivative-envelope floor")
    if frozen["cost"]["bookkeeping_prediction"] != 571_904:
        raise SystemExit("frozen M171 cost prediction changed")
    if final_disposition().action.value != "uniform-remainder-or-native-bill-missing-kill":
        raise SystemExit("M171 must remain killed without a uniform certificate")
    record = audit_record()
    if record["disposition"]["action"] != final_disposition().action.value:
        raise SystemExit("runtime audit and frozen disposition differ")
    print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
