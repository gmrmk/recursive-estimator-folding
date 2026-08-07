"""Small pure checks for the M160 structural-audit worker."""

from __future__ import annotations

from m160_cp311_worker import hostile_effective_compute


def test_hostile_effective_compute_scales_only_the_residual() -> None:
    assert hostile_effective_compute(123, 0.0, 5) == 123.0
    assert hostile_effective_compute(123, 0.25, 5) == 125_000_000_123.0


if __name__ == "__main__":
    test_hostile_effective_compute_scales_only_the_residual()
    print("M160 static tests: PASS")
