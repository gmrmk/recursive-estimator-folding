"""Reuse M145's response-free trace harness with the M153 candidate class."""

from __future__ import annotations

import run_m145_deployable_structural_trace as harness

from m153_deployable_prefix_reuse import PrefixReuseEstimator


harness.Estimator = PrefixReuseEstimator


if __name__ == "__main__":
    harness.main()
