"""Print one M216 gate family; callers persist stdout only after inspection."""

from __future__ import annotations

import argparse
import json

import m216_antithetic_distinct_provider as m216


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "gate",
        choices=("response", "native"),
        help="response uses local mpmath/scipy; native uses the pinned FlopScope venv",
    )
    args = parser.parse_args()
    if args.gate == "native":
        payload = m216.run_native_gate()
    else:
        identity = m216.run_identity_gate()
        invariance = m216.run_invariance_gate()
        numerical_static = m216.run_numerical_and_static_gates()
        payload = {
            "mutation": m216.MUTATION,
            "generated_only": True,
            "response_free": True,
            "identity": identity,
            "invariance": invariance,
            "numerical_static": numerical_static,
            "response_gate_pass": bool(
                identity["identity_gate_pass"]
                and invariance["invariance_gate_pass"]
                and numerical_static["numerical_gate_pass"]
                and numerical_static["static_gate_pass"]
            ),
            "variance_gate_authorized": False,
        }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
