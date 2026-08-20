"""Deprecated M120B entry point; intentionally inert after the M120C freeze."""

from __future__ import annotations

from run_m120c_protocol import freeze_ready_description


def main() -> None:
    raise SystemExit(
        "Deprecated M120B runner is inert.  M120C has no CLI execution path before authorization."
    )


if __name__ == "__main__":
    main()
