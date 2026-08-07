"""Unit checks for M137's frozen terminal-law closures."""

from __future__ import annotations

import numpy as np

from m137_terminal_law_resummation import (
    Moments4,
    certified_relu_interval,
    closures_from_moments,
    edgeworth_polynomial_minimum,
    gaussian_relu_mean,
    moments4_from_raw,
    symmetric_gaussian_moment_counterexample,
    two_gaussian_mixture_relu_mean,
)


def test_raw_cumulant_round_trip() -> None:
    m = moments4_from_raw([2.0, 7.0, 32.0, 181.0])
    assert np.isclose(m.mean, 2.0)
    assert np.isclose(m.variance, 3.0)
    assert np.isclose(m.raw2, 7.0)
    assert np.isclose(m.raw3, 32.0)
    assert np.isclose(m.raw4, 181.0)


def test_gaussian_and_edgeworth_reduce_to_exact_gaussian() -> None:
    m = Moments4(0.0, 1.0, 0.0, 0.0)
    values, diagnostics = closures_from_moments(m)
    assert np.isclose(gaussian_relu_mean(m), 1.0 / np.sqrt(2.0 * np.pi))
    assert np.isclose(values["edgeworth_k4_second"], values["gaussian"])
    assert diagnostics["saddlepoint_status"] == "gaussian_only"
    assert diagnostics["edgeworth_density_minimum"] >= 1.0 - 1e-12


def test_certified_interval_contains_normal_and_counterexample() -> None:
    m = Moments4(0.0, 1.0, 0.0, 0.0)
    lo, hi = certified_relu_interval(m)
    witness = symmetric_gaussian_moment_counterexample()
    assert np.isclose(lo, witness["three_atom_relu"])
    assert np.isclose(hi, 0.5)
    assert lo <= witness["normal_relu"] <= hi
    assert lo <= witness["three_atom_relu"] <= hi


def test_edgeworth_positivity_detects_bad_kurtosis() -> None:
    assert edgeworth_polynomial_minimum(0.0, -0.2) == float("-inf")
    assert edgeworth_polynomial_minimum(0.2, 0.0) < 0.0


def test_symmetric_two_gaussian_matches_negative_kurtosis() -> None:
    # A 50/50 mixture with separation variance r=0.5 has g2=-2r^2=-0.5.
    m = Moments4(0.0, 1.0, 0.0, -0.5)
    _value, ok, info = two_gaussian_mixture_relu_mean(m)
    assert ok
    assert np.isclose(info["r"], 0.5)


def test_nonzero_cumulant_saddlepoint_is_not_a_global_law() -> None:
    m = Moments4(0.0, 1.0, 0.1, 0.0)
    _values, diagnostics = closures_from_moments(m)
    assert diagnostics["saddlepoint_status"] == "invalid_as_global_law_marcinkiewicz"


def test_dead_coordinate_is_an_exact_point_mass_not_a_holder_overflow() -> None:
    m = moments4_from_raw([0.0, 0.0, 0.0, 0.0])
    values, diagnostics = closures_from_moments(m)
    assert all(value == 0.0 for value in values.values())
    assert diagnostics["certified_interval"] == [0.0, 0.0]
