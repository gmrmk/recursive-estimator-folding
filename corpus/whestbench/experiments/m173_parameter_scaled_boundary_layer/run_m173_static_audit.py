"""Verify M173's frozen response-free static audit without writing outputs."""

from __future__ import annotations

import json
from pathlib import Path

from m173_parameter_scaled_boundary_layer import ETA_MAX, audit_record, layer_enclosure, predicted_cost


ROOT = Path(__file__).resolve().parent


def main() -> None:
    frozen = json.loads((ROOT / "M173_STATIC_AUDIT_20260807.json").read_text(encoding="utf-8"))
    endpoint = layer_enclosure(ETA_MAX)
    expected_value = f"{endpoint.value_total.numerator}/{endpoint.value_total.denominator}"
    expected_tangent = f"{endpoint.tangent_total.numerator}/{endpoint.tangent_total.denominator}"
    if frozen["uniform_enclosure_at_eta_max"]["value_total"] != expected_value:
        raise SystemExit("frozen M173 value enclosure changed")
    if frozen["uniform_enclosure_at_eta_max"]["tangent_total"] != expected_tangent:
        raise SystemExit("frozen M173 tangent enclosure changed")
    if frozen["cost_prediction"]["predicted_ops"] != predicted_cost().predicted_ops:
        raise SystemExit("frozen M173 cost prediction changed")
    print(json.dumps(audit_record(), sort_keys=True))


if __name__ == "__main__":
    main()
