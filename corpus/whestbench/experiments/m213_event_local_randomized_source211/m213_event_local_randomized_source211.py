"""M213 generated-only event-local randomized Source211 falsifier.

The production-shaped kernel is ``event_local_coefficient``.  It receives a
local post-ReLU context, evaluates one requested owner on demand, and never
builds an all-pairs collision cache.  ``build_local_state`` and
``audit_collision_owners`` are intentionally tiny-width generated audit
oracles; they establish the M167/M205 mapping but are not a cost premise.

The distinct [2,1,1] path has one changed mechanism from M149: it samples one
outer standard normal, conditions on the repeated preactivation, and uses one
M178 value-and-derivative call for the conditional pair.  No deterministic
outer quadrature is used as a provider.  All formulas are local and contain no
model, truth, scorer, response, weight, leaderboard, submission, M198, or
variance-efficacy route.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import json
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _sibling in (
    "m178_certified_phi2_owent",
    "m131_trivariate_boundary_stream",
    "m167_collision_owner_unification",
    "m205_rankone_complete_physical_owner",
):
    _path = str(EXPERIMENTS / _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m178_certified_phi2_owent import evaluate as m178_evaluate  # noqa: E402
from m131_trivariate_boundary_stream import bivariate_relu_raw_dot  # noqa: E402
from m167_collision_owner_unification import (  # noqa: E402
    PhysicalFourthOwners as M167Owners,
    complete_owner_table as m167_complete_owner_table,
)
from m205_rankone_complete_physical_owner import (  # noqa: E402
    PhysicalFourthOwners as M205Owners,
    complete_physical_owner_table as m205_complete_owner_table,
)


MUTATION = "M213"
WIDTHS = (2, 3, 4, 5, 6, 7)
STATE_SEEDS = (213700002, 213700003, 213700004, 213700005, 213700006, 213700007)
OUTER_SEEDS = (213710002, 213710003, 213710004, 213710005, 213710006, 213710007)
CONFIDENCE_BLOCKS = 12
DRAWS_PER_BLOCK = 64
M178_WORST_INCLUSIVE = 4048
LOCAL_RADIUS_FACTOR = 2.0e-7
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_T_99_DF11 = 3.10580651553928


class M213Refusal(RuntimeError):
    """A local state or M178 certified subcall is outside the frozen ABI."""


@dataclass(frozen=True)
class PhysicalOwners:
    """M167 physical owner values, all with connected-minus-tree semantics."""

    k4: np.ndarray
    k31: np.ndarray
    k22: np.ndarray


@dataclass(frozen=True)
class PairMoments:
    """Local bivariate ReLU first-pair moment and M178-local enclosure.

    The one non-elementary base is ``(1,1)``.  Its Tallis reconstruction uses
    M178's Phi2 value and all three derivatives. Higher powered pair moments
    are deliberately unavailable: their first-ReLU-power boundary needs a
    truncated indicator moment that M213 does not provide.
    """

    moments: np.ndarray
    radii: np.ndarray
    m178_calls: int
    contained: bool


@dataclass(frozen=True)
class LocalState:
    """Generated audit context shaped like the M179 local ``(m,V,Tree)`` ABI.

    The dense activation covariance is allowed only because this constructor
    is a width-2--7 audit oracle.  The event kernel consumes it but does not
    populate it; an integrated producer must pass the corresponding archived
    local context directly.
    """

    mean: np.ndarray
    covariance: np.ndarray
    sigma: np.ndarray
    alpha: np.ndarray
    raw_univariate: np.ndarray
    activation_mean: np.ndarray
    activation_covariance: np.ndarray
    activation_covariance_radius: np.ndarray
    relu_scale: np.ndarray
    bridge: np.ndarray
    gamma2: np.ndarray
    gamma3: np.ndarray

    def tree_labels(self, labels: tuple[int, int, int, int]) -> float:
        if len(labels) != 4:
            raise ValueError("tree requires four labels")
        total = 0.0
        for path in _PATHS4:
            a, b, c, d = (labels[position] for position in path)
            total += (
                self.bridge[a, b]
                * self.bridge[b, c]
                * self.bridge[c, d]
                * self.gamma2[b]
                * self.gamma2[c]
            )
        for centre in range(4):
            root = labels[centre]
            product = 1.0
            for position in range(4):
                if position != centre:
                    product *= self.bridge[root, labels[position]]
            total += self.gamma3[root] * product
        scale = math.prod(float(self.relu_scale[label]) for label in labels)
        return float(total * scale)

    def tree_211(self, repeated: int, left: int, right: int) -> float:
        return self.tree_labels((repeated, repeated, left, right))


@dataclass(frozen=True)
class OwnerEvent:
    """One on-demand owner value plus the Source211 orbit denominator."""

    labels: tuple[int, int, int, int]
    stratum: str
    value: float | None
    source211_denominator: int | None
    source211_coefficient: float | None
    m178_radius: float
    m178_contained: bool
    conditional_m178_calls: int
    central_fourth_sample: float | None = None
    conditional_pair_raw: float | None = None
    conditional_mean: np.ndarray | None = None
    conditional_covariance: np.ndarray | None = None
    refused: bool = False


_PATHS4 = tuple(path for path in itertools.permutations(range(4)) if path <= path[::-1])
if len(_PATHS4) != 12:
    raise AssertionError("expected 12 undirected labelled tree paths")


def frozen_manifest() -> dict[str, object]:
    """Return the committed protocol, without reading any external state."""

    return {
        "mutation": MUTATION,
        "widths": WIDTHS,
        "state_seeds": STATE_SEEDS,
        "outer_seeds": OUTER_SEEDS,
        "confidence_blocks": CONFIDENCE_BLOCKS,
        "draws_per_block": DRAWS_PER_BLOCK,
        "conditional_m178_calls_per_distinct_event": 1,
        "m178_worst_case_inclusive": M178_WORST_INCLUSIVE,
        "four_distinct_wedge": False,
        "variance_efficacy_authorized": False,
        "m198_invoked": False,
    }


def _cdf(value: float) -> float:
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def _pdf(value: float) -> float:
    return _INV_SQRT_2PI * math.exp(-0.5 * value * value)


def _univariate_raw(alpha: float, order: int) -> float:
    """Exact real-valued ``E[(G+alpha)_+^order]`` for order <= 4."""

    if order < 0 or order > 4:
        raise ValueError("M213 only needs univariate powers through four")
    if order == 0:
        return 1.0
    cutoff = -alpha
    integrals = [_cdf(alpha), _pdf(alpha)]
    for power in range(2, order + 1):
        integrals.append(cutoff ** (power - 1) * integrals[1] + (power - 1) * integrals[power - 2])
    return float(sum(math.comb(order, power) * alpha ** (order - power) * integrals[power] for power in range(order + 1)))


def _validate_pair(mean: np.ndarray, covariance: np.ndarray) -> tuple[float, float, float, float, float]:
    m = np.asarray(mean, dtype=np.float64)
    v = np.asarray(covariance, dtype=np.float64)
    if (
        m.shape != (2,)
        or v.shape != (2, 2)
        or not np.array_equal(v, v.T)
        or not np.all(np.isfinite(m))
        or not np.all(np.isfinite(v))
        or np.any(np.diag(v) <= 0.0)
    ):
        raise M213Refusal("invalid local bivariate state")
    sigma0, sigma1 = math.sqrt(float(v[0, 0])), math.sqrt(float(v[1, 1]))
    rho = float(v[0, 1] / (sigma0 * sigma1))
    if not math.isfinite(rho) or abs(rho) >= 1.0 - 2.0**-52:
        raise M213Refusal("M178 requires a strict SPD bivariate chart")
    return float(m[0]), float(m[1]), sigma0, sigma1, rho


def _pair_moments(mean: np.ndarray, covariance: np.ndarray) -> PairMoments:
    """Tallis raw pair moments with M178 value/derivative error propagation."""

    mu0, mu1, sigma0, sigma1, rho = _validate_pair(mean, covariance)
    alpha0, alpha1 = mu0 / sigma0, mu1 / sigma1
    result = m178_evaluate(alpha0, alpha1, rho)
    if result.refused or not all(math.isfinite(item) for item in (result.value, result.d_a, result.d_b, result.d_rho)):
        raise M213Refusal(f"M178 refused local pair: {result.reason}")

    standard = np.zeros((5, 5), dtype=np.float64)
    standard_radius = np.zeros((5, 5), dtype=np.float64)
    standard[0, 0] = 1.0
    for power in range(1, 5):
        standard[power, 0] = _univariate_raw(alpha0, power)
        standard[0, power] = _univariate_raw(alpha1, power)

    # M131's pair formula, written in standard coordinates.  This is exactly
    # the M178 Phi2 value + (da, db, drho) Tallis reconstruction.
    standard[1, 1] = (
        alpha1 * result.d_a
        + alpha0 * result.d_b
        + (1.0 - rho * rho) * result.d_rho
        + (alpha0 * alpha1 + rho) * result.value
    )
    standard_radius[1, 1] = (
        abs(alpha1) * result.w_da
        + abs(alpha0) * result.w_db
        + abs(1.0 - rho * rho) * result.w_drho
        + abs(alpha0 * alpha1 + rho) * result.w_value
    )
    moments = np.zeros_like(standard)
    radii = np.zeros_like(standard)
    for p in range(5):
        for q in range(5 - p):
            scale = sigma0**p * sigma1**q
            moments[p, q] = standard[p, q] * scale
            radii[p, q] = standard_radius[p, q] * abs(scale)
    return PairMoments(moments, radii, 1, True)


def _set_partitions(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, ...], ...]]:
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in _set_partitions(rest):
        yield ((first,),) + partition
        for position in range(len(partition)):
            yield partition[:position] + (partition[position] + (first,),) + partition[position + 1 :]


def _cumulant_univariate(raw: np.ndarray) -> float:
    total = 0.0
    for partition in _set_partitions(tuple(range(4))):
        total += math.factorial(len(partition) - 1) * (-1.0) ** (len(partition) - 1) * math.prod(float(raw[len(block)]) for block in partition)
    return float(total)


def generated_spd_cell(width: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic small generated Gaussian cells; no external weights."""

    if width not in WIDTHS:
        raise ValueError("width is outside the frozen M213 audit range")
    rng = np.random.default_rng(seed)
    factor = rng.normal(scale=0.09, size=(width, min(width, 3)))
    diagonal = rng.uniform(0.7, 1.3, size=width)
    covariance = factor @ factor.T + np.diag(diagonal)
    mean = rng.uniform(-0.45, 0.45, size=width)
    return mean.astype(np.float64), covariance.astype(np.float64)


def build_local_state(mean: np.ndarray, covariance: np.ndarray) -> LocalState:
    """Build a small-width audit M179-shaped context from generated arrays."""

    mu = np.asarray(mean, dtype=np.float64)
    cov = np.asarray(covariance, dtype=np.float64)
    if (
        mu.ndim != 1
        or mu.size not in WIDTHS
        or cov.shape != (mu.size, mu.size)
        or not np.allclose(cov, cov.T, rtol=0.0, atol=2.0e-13)
        or not np.all(np.isfinite(mu))
        or not np.all(np.isfinite(cov))
    ):
        raise M213Refusal("invalid audit Gaussian state")
    cov = 0.5 * (cov + cov.T)
    try:
        np.linalg.cholesky(cov)
    except np.linalg.LinAlgError as exc:
        raise M213Refusal("audit Gaussian state is not SPD") from exc
    sigma = np.sqrt(np.diag(cov))
    alpha = mu / sigma
    raw = np.empty((mu.size, 5), dtype=np.float64)
    for i in range(mu.size):
        raw[i] = [sigma[i] ** power * _univariate_raw(float(alpha[i]), power) for power in range(5)]
    activation_mean = raw[:, 1].copy()
    activation_covariance = np.zeros_like(cov)
    activation_radius = np.zeros_like(cov)
    for i in range(mu.size):
        activation_covariance[i, i] = raw[i, 2] - raw[i, 1] ** 2
        for j in range(i + 1, mu.size):
            pair = _pair_moments(mu[[i, j]], cov[np.ix_((i, j), (i, j))])
            value = pair.moments[1, 1] - activation_mean[i] * activation_mean[j]
            activation_covariance[i, j] = activation_covariance[j, i] = value
            activation_radius[i, j] = activation_radius[j, i] = pair.radii[1, 1]
    relu_scale = np.sqrt(np.diag(activation_covariance))
    if np.any(~np.isfinite(relu_scale)) or np.any(relu_scale <= 0.0):
        raise M213Refusal("post-ReLU variance is nonpositive")
    bridge = activation_covariance / np.outer(relu_scale, relu_scale)
    bridge = 0.5 * (bridge + bridge.T)
    np.fill_diagonal(bridge, 1.0)
    probability = np.asarray([_cdf(float(item)) for item in alpha])
    density = np.asarray([_pdf(float(item)) for item in alpha])
    standard_scale = relu_scale / sigma
    if np.any(probability <= 1.0e-12):
        raise M213Refusal("local first Hermite coefficient is too small")
    gamma2 = density * standard_scale / (probability * probability)
    gamma3 = -alpha * density * standard_scale * standard_scale / (probability**3)
    return LocalState(mu, cov, sigma, alpha, raw, activation_mean, activation_covariance, activation_radius, relu_scale, bridge, gamma2, gamma3)


def _condition_on_outer_g(state: LocalState, repeated: int, left: int, right: int, outer_g: float) -> tuple[np.ndarray, np.ndarray]:
    if not math.isfinite(outer_g):
        raise M213Refusal("outer G must be finite")
    selected = np.asarray((left, right), dtype=int)
    repeated_variance = float(state.covariance[repeated, repeated])
    conditional_mean = state.mean[selected] + state.covariance[selected, repeated] * outer_g / state.sigma[repeated]
    conditional_covariance = (
        state.covariance[np.ix_(selected, selected)]
        - np.outer(state.covariance[selected, repeated], state.covariance[selected, repeated]) / repeated_variance
    )
    if np.min(np.linalg.eigvalsh(conditional_covariance)) <= 1.0e-10:
        raise M213Refusal("conditional singleton pair is not comfortably SPD")
    return np.asarray(conditional_mean, dtype=np.float64), np.asarray(conditional_covariance, dtype=np.float64)


def _conditional_mean(mean: float, variance: float) -> float:
    sigma = math.sqrt(variance)
    alpha = mean / sigma
    return sigma * _univariate_raw(alpha, 1)


def _distinct_event(state: LocalState, repeated: int, left: int, right: int, outer_g: float) -> OwnerEvent:
    conditional_mean, conditional_covariance = _condition_on_outer_g(state, repeated, left, right, outer_g)
    pair = _pair_moments(conditional_mean, conditional_covariance)
    left_mean = _conditional_mean(float(conditional_mean[0]), float(conditional_covariance[0, 0]))
    right_mean = _conditional_mean(float(conditional_mean[1]), float(conditional_covariance[1, 1]))
    centered_pair = (
        pair.moments[1, 1]
        - state.activation_mean[left] * right_mean
        - state.activation_mean[right] * left_mean
        + state.activation_mean[left] * state.activation_mean[right]
    )
    preactivation = float(state.mean[repeated] + state.sigma[repeated] * outer_g)
    centered_repeated = max(0.0, preactivation) - state.activation_mean[repeated]
    central_sample = centered_repeated * centered_repeated * centered_pair
    v = state.activation_covariance
    cumulant_sample = central_sample - v[repeated, repeated] * v[left, right] - 2.0 * v[repeated, left] * v[repeated, right]
    value = cumulant_sample - state.tree_211(repeated, left, right)
    radius = (
        centered_repeated * centered_repeated * pair.radii[1, 1]
        + abs(v[repeated, repeated]) * state.activation_covariance_radius[left, right]
        + 2.0 * (
            abs(v[repeated, left]) * state.activation_covariance_radius[repeated, right]
            + abs(v[repeated, right]) * state.activation_covariance_radius[repeated, left]
        )
    )
    return OwnerEvent((repeated, repeated, left, right), "[2,1,1]", float(value), 1, float(value), float(radius), pair.contained, pair.m178_calls, float(central_sample), float(pair.moments[1, 1]), conditional_mean, conditional_covariance)


def event_local_coefficient(local: LocalState, labels: tuple[int, int, int, int], *, outer_g: float | None = None) -> OwnerEvent:
    """Evaluate one physical owner on demand; `[1,1,1,1]` is unsupported."""

    labels = tuple(int(item) for item in labels)
    n = local.mean.size
    if len(labels) != 4 or not all(0 <= item < n for item in labels):
        raise ValueError("labels must name four local coordinates")
    counts = {label: labels.count(label) for label in set(labels)}
    multiplicities = tuple(sorted(counts.values(), reverse=True))
    if multiplicities == (1, 1, 1, 1):
        return OwnerEvent(
            labels, "[1,1,1,1]", None, None, None, float("nan"), False, 0,
            refused=True,
        )
    if multiplicities == (4,):
        index = labels[0]
        value = _cumulant_univariate(local.raw_univariate[index]) - local.tree_labels((index, index, index, index))
        return OwnerEvent((index, index, index, index), "[4]", value, 6, value / 6.0, 0.0, True, 0)
    if multiplicities == (3, 1):
        repeated = next(index for index, count in counts.items() if count == 3)
        singleton = next(index for index, count in counts.items() if count == 1)
        # The tempting recurrence from m11 crosses a p=1 ReLU boundary.  Its
        # missing truncated-indicator moment broke swap/permutation covariance
        # in the frozen generated audit.  Do not turn that unknown into a
        # number: an M213 provider has no valid [3,1] owner.
        return OwnerEvent(
            (repeated, repeated, repeated, singleton), "[3,1]", None, None,
            None, float("nan"), False, 0, refused=True,
        )
    if multiplicities == (2, 2):
        left, right = sorted(counts)
        return OwnerEvent(
            (left, left, right, right), "[2,2]", None, None, None,
            float("nan"), False, 0, refused=True,
        )
    if multiplicities == (2, 1, 1):
        repeated = next(index for index, count in counts.items() if count == 2)
        singleton = tuple(sorted(index for index, count in counts.items() if count == 1))
        if outer_g is None:
            raise ValueError("[2,1,1] requires exactly one supplied outer G")
        return _distinct_event(local, repeated, singleton[0], singleton[1], float(outer_g))
    raise AssertionError("unreachable fourth-order multiplicity")


def distinct_event_from_outer_g(local: LocalState, repeated: int, left: int, right: int, outer_g: float) -> OwnerEvent:
    """Named M131-compatible distinct event helper used by the generated audit."""

    return event_local_coefficient(local, (repeated, repeated, left, right), outer_g=outer_g)


def m131_conditional_pair_crosscheck(event: OwnerEvent) -> float:
    """Independent M131 atom; audit-only and deliberately not a provider path."""

    if event.conditional_mean is None or event.conditional_covariance is None or event.conditional_pair_raw is None:
        raise ValueError("M131 crosscheck applies only to a distinct event")
    raw, _ = bivariate_relu_raw_dot(event.conditional_mean, event.conditional_covariance, np.zeros(2), np.zeros((2, 2)))
    return float(raw - event.conditional_pair_raw)


def audit_collision_owners(local: LocalState) -> PhysicalOwners:
    """Small-width all-owner oracle only; not callable as a production cache."""

    del local
    raise M213Refusal(
        "boundary-indicator high-moment recurrence is unsupported; complete physical K31/K22 owners are unavailable"
    )


def complete_source211_table(distinct_211: np.ndarray, owners: PhysicalOwners) -> np.ndarray:
    """M167 complete ownership, cross-checked with M205 where M205 is total."""

    distinct = np.asarray(distinct_211, dtype=np.float64)
    n = distinct.shape[0]
    m167 = m167_complete_owner_table(distinct, M167Owners(owners.k4, owners.k31, owners.k22))
    if n >= 3:
        m205 = m205_complete_owner_table(distinct, M205Owners(owners.k4, owners.k31, owners.k22))
        if not np.allclose(m167, m205, rtol=0.0, atol=2.0e-10):
            raise M213Refusal("M167/M205 complete owner tables disagree")
    return m167


def _gh_reference(local: LocalState, repeated: int, left: int, right: int, order: int) -> float:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    values = [float(weight) / math.sqrt(math.pi) * distinct_event_from_outer_g(local, repeated, left, right, math.sqrt(2.0) * float(node)).value for node, weight in zip(nodes, weights, strict=True)]
    return float(math.fsum(values))


def _confidence_interval(local: LocalState, repeated: int, left: int, right: int, seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    block_means = np.empty(CONFIDENCE_BLOCKS, dtype=np.float64)
    for block in range(CONFIDENCE_BLOCKS):
        values = [distinct_event_from_outer_g(local, repeated, left, right, float(rng.normal())).value for _ in range(DRAWS_PER_BLOCK)]
        block_means[block] = math.fsum(values) / DRAWS_PER_BLOCK
    center = float(np.mean(block_means))
    standard_error = float(np.std(block_means, ddof=1) / math.sqrt(CONFIDENCE_BLOCKS))
    half_width = _T_99_DF11 * standard_error
    return center - half_width, center + half_width, center


def run_falsifier() -> dict[str, object]:
    """Run only frozen generated identity/numerical gates; never variance efficacy."""

    cells: list[dict[str, object]] = []
    identity_ok = True
    confidence_ok = True
    local_provider_ok = True
    max_radius_ratio = 0.0
    for width, state_seed, outer_seed in zip(WIDTHS, STATE_SEEDS, OUTER_SEEDS, strict=True):
        mean, covariance = generated_spd_cell(width, state_seed)
        local = build_local_state(mean, covariance)
        collision_events = [event_local_coefficient(local, (i, i, i, i)) for i in range(width)]
        events = list(collision_events)
        if width >= 3:
            rng = np.random.default_rng(outer_seed)
            events += [
                event_local_coefficient(local, (i, i, j, k), outer_g=float(rng.normal()))
                for i in range(width)
                for j in range(width)
                for k in range(j + 1, width)
                if i != j and i != k
            ]
        for event in events:
            if event.refused or event.value is None:
                continue
            ratio = event.m178_radius / (1.0 + abs(event.value))
            max_radius_ratio = max(max_radius_ratio, ratio)
            local_provider_ok = local_provider_ok and event.m178_contained and math.isfinite(ratio) and ratio <= LOCAL_RADIUS_FACTOR
        record: dict[str, object] = {
            "width": width,
            "collision_owner_gate": "FAIL_BOUNDARY_INDICATOR_HIGH_MOMENT_RECURRENCE",
            "event_count": len(events),
            "max_m178_radius_ratio": max(event.m178_radius / (1.0 + abs(event.value)) for event in events if not event.refused and event.value is not None),
        }
        if width >= 3:
            reference64 = _gh_reference(local, 0, 1, 2, 64)
            reference96 = _gh_reference(local, 0, 1, 2, 96)
            identity_ok = identity_ok and abs(reference64 - reference96) <= 2.0e-8
            low, high, center = _confidence_interval(local, 0, 1, 2, outer_seed)
            confidence_ok = confidence_ok and low <= reference96 <= high
            record.update({"identity_reference_64": reference64, "identity_reference_96": reference96, "confidence_low": low, "confidence_high": high, "confidence_center": center})
        else:
            record["distinct_identity"] = "VACUOUS_NO_THREE_DISTINCT_LABELS"
        cells.append(record)
    return {
        "mutation": MUTATION,
        "generated_only": True,
        "response_free": True,
        "m178_calls_per_distinct_event": 1,
        "m178_worst_case_inclusive_per_call": M178_WORST_INCLUSIVE,
        "identity_gate_pass": bool(identity_ok),
        "confidence_gate_pass": bool(confidence_ok),
        "m178_local_numerical_gate_pass": bool(local_provider_ok),
        "local_provider_gate_description": "M178 value/derivative envelope propagated through the local event",
        "max_m178_radius_ratio": max_radius_ratio,
        "collision_owner_gate_pass": False,
        "collision_owner_stop_reason": "[3,1]/[2,2] Tallis recurrence crosses a ReLU boundary and lacks a truncated-indicator moment",
        "local_provider_gate_pass": False,
        "whole_source_provider_gate_pass": False,
        "whole_source_stop_reason": "collision owners are unavailable; M213 also does not contract through the next affine W or bind the next pre-ReLU context for M198",
        "source_variance_executed": False,
        "cells": cells,
    }


def main() -> None:
    print(json.dumps(run_falsifier(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
