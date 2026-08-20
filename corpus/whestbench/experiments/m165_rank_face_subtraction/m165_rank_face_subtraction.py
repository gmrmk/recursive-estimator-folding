"""Centered M165 rank-face subtraction probe for the [2,1,1] defect.

This is a high-precision, response-free *prototype*, not an endpoint provider.
It studies the centered equicorrelation path

    Sigma(epsilon) = (1-epsilon) 11^T + epsilon I,  0 < epsilon < 1,

whose limit at zero is M154's positive-marginal rank-one common-factor state.
Conditioning on the common factor turns all raw rectified moments into a
one-dimensional integral.  The code combines those moments into the central
cumulant and M129 repeated tree before exposing the defect; it never
differentiates a trivariate orthant probability as an opaque value.

The retained rank-one value and the M154 directional linear coefficient can
then be subtracted.  The nonzero epsilon^(3/2) residual is the endpoint term a
generic rank-aware Plackett implementation would have to enclose analytically.

The prototype deliberately refuses epsilon=0 (rank-one is M154-owned),
epsilon=1 (independence is not a rank-face limit), rank two, and every
zero-variance face.  No ridge, clipping, retry, model, response, truth,
scorer, leaderboard, submission, or champion is involved.
"""

from __future__ import annotations

import itertools

import mpmath as mp


class M165PrototypeDomainError(RuntimeError):
    """The small equicorrelation probe must not be mistaken for a generic ABI."""


_LABELS = (0, 0, 1, 2)


def dispatch_m165_prototype_stratum(
    *, rank: int, positive_marginals: bool, centered_common_factor: bool
) -> str:
    """Fail closed outside the only rank-face anchor actually derived here."""

    if type(rank) is not int or rank < 0 or rank > 3:
        raise ValueError("rank must be a built-in integer between zero and three")
    if not positive_marginals:
        raise M165PrototypeDomainError(
            "zero-marginal PSD face requires M159 deterministic/one-sided dispatch"
        )
    if rank == 2:
        raise M165PrototypeDomainError(
            "rank-two anchor and directional coefficient are not owned by M154"
        )
    if rank != 1 or not centered_common_factor:
        raise M165PrototypeDomainError(
            "prototype supports only the positive-marginal centered rank-one common-factor anchor"
        )
    return "rank1-common-factor-subtraction"


def _require_open_epsilon(epsilon: mp.mpf) -> mp.mpf:
    epsilon = mp.mpf(epsilon)
    if not (mp.mpf("0") < epsilon < mp.mpf("1")):
        raise M165PrototypeDomainError(
            "epsilon must lie strictly between zero and one; rank-one common-factor "
            "and non-rank-face limits use dedicated dispatches"
        )
    return epsilon


def common_factor_rank_one_defect_mp() -> mp.mpf:
    """Exact M154/M158 centered common-factor defect in high precision."""

    pi = mp.pi
    cumulant = (3 * pi * pi - 4 * pi - 6) / (4 * pi * pi)
    tree = 12 * (pi - 1) ** 3 / pi**4
    return cumulant - tree


def _conditional_rectified_moment(
    common_factor: mp.mpf, epsilon: mp.mpf, power: int
) -> mp.mpf:
    """E[(sqrt(1-eps) z + sqrt(eps) E)_+^power | z] for powers 0,1,2."""

    if power == 0:
        return mp.mpf(1)
    noise_scale = mp.sqrt(epsilon)
    conditional_mean = mp.sqrt(1 - epsilon) * common_factor
    alpha = conditional_mean / noise_scale
    pdf = mp.exp(-alpha * alpha / 2) / mp.sqrt(2 * mp.pi)
    cdf = mp.erfc(-alpha / mp.sqrt(2)) / 2
    if power == 1:
        return noise_scale * pdf + conditional_mean * cdf
    if power == 2:
        return (
            (conditional_mean * conditional_mean + epsilon) * cdf
            + conditional_mean * noise_scale * pdf
        )
    raise ValueError("prototype exposes only powers zero, one, and two")


def _raw_moment_mp(epsilon: mp.mpf, powers: tuple[int, int, int]) -> mp.mpf:
    """One-dimensional common-factor integral for a raw ReLU moment."""

    standard_density = lambda z: mp.exp(-z * z / 2) / mp.sqrt(2 * mp.pi)

    def integrand(z: mp.mpf) -> mp.mpf:
        return standard_density(z) * mp.fprod(
            _conditional_rectified_moment(z, epsilon, power) for power in powers
        )

    return mp.quad(integrand, [-mp.inf, mp.mpf(0), mp.inf])


def _repeated_tree_mp(relu_covariance: mp.mpf) -> mp.mpf:
    """M129 repeated tree specialized exactly to centered equal marginals."""

    pi = mp.pi
    relu_variance = mp.mpf("0.5") - 1 / (2 * pi)
    q = relu_covariance / relu_variance
    # h1=1/2, h2=1/sqrt(2*pi), h3=0 in M129's unnormalised convention.
    gamma2 = 2 * mp.sqrt(pi - 1) / pi
    path = mp.mpf(0)
    for permutation in itertools.permutations(range(4)):
        sequence = tuple(_LABELS[position] for position in permutation)
        edge_product = mp.mpf(1)
        for left, right in zip(sequence, sequence[1:]):
            edge_product *= 1 if left == right else q
        path += gamma2 * gamma2 * edge_product
    return relu_variance * relu_variance * path / 2


def centered_equicorrelation_defect_mp(epsilon: mp.mpf, *, dps: int = 60) -> mp.mpf:
    """Combined central-cumulant/tree defect on the open equicorrelation path."""

    if type(dps) is not int or dps < 40:
        raise ValueError("dps must be a built-in integer of at least 40")
    with mp.workdps(dps):
        epsilon = _require_open_epsilon(epsilon)
        mean = 1 / mp.sqrt(2 * mp.pi)
        second = mp.mpf("0.5")
        raw_110 = _raw_moment_mp(epsilon, (1, 1, 0))
        raw_210 = _raw_moment_mp(epsilon, (2, 1, 0))
        raw_111 = _raw_moment_mp(epsilon, (1, 1, 1))
        raw_211 = _raw_moment_mp(epsilon, (2, 1, 1))

        central = (
            raw_211
            - 2 * mean * raw_210
            + mean * mean * second
            - 2 * mean * raw_111
            + 5 * mean * mean * raw_110
            - 3 * mean**4
        )
        relu_variance = second - mean * mean
        relu_covariance = raw_110 - mean * mean
        cumulant = central - relu_variance * relu_covariance - 2 * relu_covariance**2
        defect = cumulant - _repeated_tree_mp(relu_covariance)
        return +defect


def rank_face_subtracted_residual_mp(
    epsilon: mp.mpf, rank_one_directional_coefficient: mp.mpf, *, dps: int = 60
) -> mp.mpf:
    """Subtract the M154 rank-one value and its supplied cone-direction term.

    Along this path, the remaining combined defect has an epsilon^(3/2)
    leading term.  The coefficient is deliberately not hard-coded: a generic
    path must obtain its directional linear term from its rank-one owner.
    """

    with mp.workdps(dps):
        epsilon = _require_open_epsilon(epsilon)
        return +(
            centered_equicorrelation_defect_mp(epsilon, dps=dps)
            - common_factor_rank_one_defect_mp()
            - mp.mpf(rank_one_directional_coefficient) * epsilon
        )
