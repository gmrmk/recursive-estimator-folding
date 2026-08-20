"""Exact rational witness for the M202 signed-facet SMC no-go."""

from __future__ import annotations

from fractions import Fraction


def signed_mass(epsilon: Fraction) -> Fraction:
    if not Fraction(0) < epsilon < Fraction(1):
        raise ValueError("epsilon must lie strictly between zero and one")
    return 2 * epsilon


def absolute_mass(epsilon: Fraction) -> Fraction:
    if not Fraction(0) < epsilon < Fraction(1):
        raise ValueError("epsilon must lie strictly between zero and one")
    return 2 * (2 - epsilon)


def sign_ratio(epsilon: Fraction) -> Fraction:
    return signed_mass(epsilon) / absolute_mass(epsilon)


def optimal_relative_variance(epsilon: Fraction) -> Fraction:
    rho = sign_ratio(epsilon)
    return Fraction(1, 1) / (rho * rho) - 1


def raw_gate_to_owned_mass_factor() -> int:
    """Both nested ReLU layers label each one true output boundary."""

    return 2


def generic_first_layer_candidate_facets(dimension: int) -> int:
    if dimension < 1:
        raise ValueError("dimension must be positive")
    return dimension * (2 ** (dimension - 1))


def exact_result() -> dict[str, object]:
    epsilon = Fraction(1, 1024)
    return {
        "candidate": "M202 signed-facet SMC no-go",
        "epsilon": str(epsilon),
        "signed_mass": str(signed_mass(epsilon)),
        "absolute_mass": str(absolute_mass(epsilon)),
        "sign_ratio": str(sign_ratio(epsilon)),
        "raw_gate_to_owned_mass_factor": raw_gate_to_owned_mass_factor(),
        "target_first_layer_candidate_facets": generic_first_layer_candidate_facets(256),
        "status": "KILLED_UNNORMALIZED_SIGNED_FACET_SMC_WITHOUT_OWNED_GENERATOR_AND_ESS_CERTIFICATE",
    }
