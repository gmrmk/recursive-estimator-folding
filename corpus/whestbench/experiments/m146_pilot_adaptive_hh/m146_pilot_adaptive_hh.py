"""Algebra-only M146 pilot-adaptive Hansen--Hurwitz source machinery.

This module deliberately contains no generated-state constructor, M131 endpoint
workaround, response runner, contest evaluator, authorization path, or outcome
code.  A future endpoint provider must satisfy ``EndpointSafe211Provider`` and
receive an independent audit before any generated premise can execute.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Mapping, Protocol, Sequence, runtime_checkable

import numpy as np


Array = np.ndarray


class M146ContractError(ValueError):
    """A frozen M146 algebra or protocol contract was violated."""


class EndpointProviderUnavailable(RuntimeError):
    """No independently audited endpoint-safe generated provider is bound."""


class UnresolvedBaselineVariance(ArithmeticError):
    """The exact base variance is zero or unresolved at floating precision."""


@dataclass(frozen=True)
class CertifiedCoefficient:
    value: float
    coarse_value: float
    fine_value: float
    certificate_digest: str

    def __post_init__(self) -> None:
        values = (self.value, self.coarse_value, self.fine_value)
        if not all(math.isfinite(float(value)) for value in values):
            raise M146ContractError("certified coefficient values must be finite")
        if not isinstance(self.certificate_digest, str) or len(self.certificate_digest) != 64:
            raise M146ContractError("certificate_digest must be one SHA-256 hex digest")
        try:
            int(self.certificate_digest, 16)
        except ValueError as exc:
            raise M146ContractError("certificate_digest is not hexadecimal") from exc


@dataclass(frozen=True)
class CertifiedGeneratedCell:
    family: str
    width: int
    cell_seed: int
    layer: int
    mean: Array
    covariance: Array
    source_scale: Array
    state_digest: str
    provider_id: str


@runtime_checkable
class EndpointSafe211Provider(Protocol):
    """Typed boundary owned by the independent M147 endpoint investigation."""

    provider_id: str
    endpoint_safe: bool
    arithmetic_dtype: str

    def build_cell(
        self, *, family: str, width: int, cell_seed: int, layer: int
    ) -> CertifiedGeneratedCell:
        ...

    def coefficient(
        self, cell: CertifiedGeneratedCell, repeated: int, left: int, right: int
    ) -> CertifiedCoefficient:
        ...


def require_endpoint_provider(
    provider: EndpointSafe211Provider | None,
) -> EndpointSafe211Provider:
    """Fail closed until a separately audited M147 provider is explicitly bound."""

    if provider is None:
        raise EndpointProviderUnavailable(
            "M146 has no generated coefficient/state constructor; await audited M147"
        )
    if not isinstance(provider, EndpointSafe211Provider):
        raise EndpointProviderUnavailable("provider does not satisfy EndpointSafe211Provider")
    if provider.endpoint_safe is not True:
        raise EndpointProviderUnavailable("provider is not certified endpoint-safe")
    if provider.arithmetic_dtype not in {"float64", "longdouble"}:
        raise EndpointProviderUnavailable("endpoint provider arithmetic dtype is not frozen")
    if not isinstance(provider.provider_id, str) or not provider.provider_id:
        raise EndpointProviderUnavailable("endpoint provider id is empty")
    return provider


def _finite_array(name: str, value: Array, *, ndim: int | None = None) -> Array:
    answer = np.asarray(value)
    if ndim is not None and answer.ndim != ndim:
        raise M146ContractError(f"{name} must have ndim={ndim}")
    if not np.issubdtype(answer.dtype, np.number) or not np.all(np.isfinite(answer)):
        raise M146ContractError(f"{name} must be finite numeric data")
    return answer


def _readonly_float64(name: str, value: Array, *, ndim: int) -> Array:
    answer = np.array(_finite_array(name, value, ndim=ndim), dtype=np.float64, copy=True)
    answer.setflags(write=False)
    return answer


def _readonly_int64(name: str, value: Array, *, width: int | None = None) -> Array:
    raw = np.asarray(value)
    if raw.ndim != 2 or raw.shape[1] != 3 or not np.issubdtype(raw.dtype, np.integer):
        raise M146ContractError(f"{name} must be one integer array with shape (count,3)")
    answer = np.array(raw, dtype=np.int64, copy=True)
    if width is not None:
        if np.any(answer < 0) or np.any(answer >= width):
            raise M146ContractError(f"{name} contains an out-of-range label")
        if np.any(
            (answer[:, 0] == answer[:, 1])
            | (answer[:, 0] == answer[:, 2])
            | (answer[:, 1] == answer[:, 2])
        ):
            raise M146ContractError(f"{name} must contain distinct labels in every row")
    answer.setflags(write=False)
    return answer


def _symmetric_hollow(name: str, value: Array, width: int) -> Array:
    answer = _readonly_float64(name, value, ndim=2)
    if answer.shape != (width, width):
        raise M146ContractError(f"{name} must have shape ({width},{width})")
    if np.any(answer < 0.0):
        raise M146ContractError(f"{name} must be nonnegative")
    if not np.allclose(answer, answer.T, rtol=0.0, atol=2e-12):
        raise M146ContractError(f"{name} must be symmetric")
    if np.any(np.diag(answer) != 0.0):
        raise M146ContractError(f"{name} must have an exactly zero diagonal")
    return answer


def _symmetric_hollow_signed(name: str, value: Array, width: int) -> Array:
    answer = _readonly_float64(name, value, ndim=2)
    if answer.shape != (width, width):
        raise M146ContractError(f"{name} must have shape ({width},{width})")
    if not np.allclose(answer, answer.T, rtol=0.0, atol=2e-12):
        raise M146ContractError(f"{name} must be symmetric")
    if np.any(np.diag(answer) != 0.0):
        raise M146ContractError(f"{name} must have an exactly zero diagonal")
    if np.any(np.abs(answer) > 1.0 + 2e-15):
        raise M146ContractError(f"{name} must lie in [-1,1]")
    return answer


def _vector(name: str, value: Array, width: int, *, nonnegative: bool = False) -> Array:
    answer = _readonly_float64(name, value, ndim=1)
    if answer.shape != (width,):
        raise M146ContractError(f"{name} must have length {width}")
    if nonnegative and np.any(answer < 0.0):
        raise M146ContractError(f"{name} must be nonnegative")
    return answer


@dataclass(frozen=True)
class RoleAware211Proposal:
    """Exact three-bank ordered-triple proposal with role-specific factors."""

    repeated_strength: Array
    singleton_strength: Array
    repeated_singleton_edge: Array
    singleton_singleton_edge: Array
    uniform_mixture: float = 0.05

    def __post_init__(self) -> None:
        repeated = _readonly_float64("repeated_strength", self.repeated_strength, ndim=1)
        width = int(repeated.size)
        if width < 3:
            raise M146ContractError("a [2,1,1] proposal needs width at least three")
        if np.any(repeated < 0.0):
            raise M146ContractError("repeated_strength must be nonnegative")
        singleton = _vector(
            "singleton_strength", self.singleton_strength, width, nonnegative=True
        )
        edge_rs = _symmetric_hollow(
            "repeated_singleton_edge", self.repeated_singleton_edge, width
        )
        edge_ss = _symmetric_hollow(
            "singleton_singleton_edge", self.singleton_singleton_edge, width
        )
        epsilon = float(self.uniform_mixture)
        if not math.isfinite(epsilon) or not (0.05 <= epsilon <= 1.0):
            raise M146ContractError("uniform_mixture must be finite and in [.05,1]")

        endpoint_a = edge_rs * singleton[None, :]
        endpoint_sum = np.sum(endpoint_a, axis=1, dtype=np.float64)
        distinct_a = endpoint_sum * endpoint_sum - np.sum(
            endpoint_a * endpoint_a, axis=1, dtype=np.float64
        )
        center_a = repeated * repeated * np.maximum(distinct_a, 0.0)

        left = edge_rs * (repeated * repeated)[:, None]
        right = edge_ss * singleton[:, None]
        left_sum = np.sum(left, axis=0, dtype=np.float64)
        right_sum = np.sum(right, axis=0, dtype=np.float64)
        distinct_b = left_sum * right_sum - np.sum(left * right, axis=0, dtype=np.float64)
        center_b = singleton * np.maximum(distinct_b, 0.0)
        center_c = center_b.copy()

        for name, value in (
            ("repeated_strength", repeated),
            ("singleton_strength", singleton),
            ("repeated_singleton_edge", edge_rs),
            ("singleton_singleton_edge", edge_ss),
            ("center_a", center_a),
            ("center_b", center_b),
            ("center_c", center_c),
        ):
            frozen = np.array(value, dtype=np.float64, copy=True)
            if not np.all(np.isfinite(frozen)) or np.any(frozen < 0.0):
                raise M146ContractError(f"{name} became nonfinite or negative")
            frozen.setflags(write=False)
            object.__setattr__(self, name, frozen)
        object.__setattr__(self, "uniform_mixture", epsilon)

    @property
    def width(self) -> int:
        return int(self.repeated_strength.size)

    @property
    def ordered_population(self) -> int:
        return self.width * (self.width - 1) * (self.width - 2)

    @property
    def z_a(self) -> float:
        return float(np.sum(self.center_a, dtype=np.float64))

    @property
    def z_b(self) -> float:
        return float(np.sum(self.center_b, dtype=np.float64))

    @property
    def z_c(self) -> float:
        return float(np.sum(self.center_c, dtype=np.float64))

    @property
    def structured_normalizer(self) -> float:
        return self.z_a + self.z_b + self.z_c

    @property
    def effective_uniform_weight(self) -> float:
        return 1.0 if self.structured_normalizer <= 0.0 else self.uniform_mixture

    def structured_mass(self, repeated: int, left: int, right: int) -> float:
        if not all(0 <= item < self.width for item in (repeated, left, right)):
            raise IndexError("triple label is outside the proposal width")
        if len({repeated, left, right}) != 3:
            return 0.0
        r = self.repeated_strength
        u = self.singleton_strength
        x = self.repeated_singleton_edge
        y = self.singleton_singleton_edge
        answer = r[repeated] ** 2 * u[left] * u[right] * (
            x[repeated, left] * x[repeated, right]
            + x[repeated, left] * y[left, right]
            + x[repeated, right] * y[left, right]
        )
        return float(answer)

    def probability(self, repeated: int, left: int, right: int) -> float:
        if not all(0 <= item < self.width for item in (repeated, left, right)):
            raise IndexError("triple label is outside the proposal width")
        if len({repeated, left, right}) != 3:
            return 0.0
        normalizer = self.structured_normalizer
        uniform = 1.0 / self.ordered_population
        if normalizer <= 0.0:
            return uniform
        answer = self.uniform_mixture * uniform + (
            1.0 - self.uniform_mixture
        ) * self.structured_mass(repeated, left, right) / normalizer
        if not math.isfinite(answer) or answer < self.uniform_mixture * uniform:
            raise ArithmeticError("proposal probability lost its rescue lower bound")
        return float(answer)

    @staticmethod
    def _categorical(weights: Array, rng: np.random.Generator) -> int:
        weights = np.asarray(weights, dtype=np.float64)
        if weights.ndim != 1 or not np.all(np.isfinite(weights)) or np.any(weights < 0.0):
            raise M146ContractError("categorical weights must be finite and nonnegative")
        cumulative = np.cumsum(weights, dtype=np.float64)
        total = float(cumulative[-1]) if cumulative.size else 0.0
        if total <= 0.0:
            raise ArithmeticError("cannot draw from a zero-mass categorical law")
        target = float(rng.random()) * total
        return min(int(np.searchsorted(cumulative, target, side="right")), weights.size - 1)

    def _draw_uniform(self, rng: np.random.Generator) -> tuple[int, int, int]:
        # Three sequential exact integer draws, with deterministic skip maps and
        # no rejection loop.
        i = int(rng.integers(self.width))
        raw_j = int(rng.integers(self.width - 1))
        j = raw_j + int(raw_j >= i)
        low, high = sorted((i, j))
        raw_k = int(rng.integers(self.width - 2))
        k = raw_k + int(raw_k >= low)
        k += int(k >= high)
        return i, j, k

    def _draw_a(self, rng: np.random.Generator) -> tuple[int, int, int]:
        i = self._categorical(self.center_a, rng)
        endpoint = self.singleton_strength * self.repeated_singleton_edge[i]
        total = float(np.sum(endpoint, dtype=np.float64))
        j = self._categorical(endpoint * (total - endpoint), rng)
        last = endpoint.copy()
        last[j] = 0.0
        k = self._categorical(last, rng)
        return i, j, k

    def _draw_b(self, rng: np.random.Generator) -> tuple[int, int, int]:
        j = self._categorical(self.center_b, rng)
        left = self.repeated_strength**2 * self.repeated_singleton_edge[:, j]
        right = self.singleton_strength * self.singleton_singleton_edge[:, j]
        total = float(np.sum(right, dtype=np.float64))
        i = self._categorical(left * (total - right), rng)
        last = right.copy()
        last[i] = 0.0
        k = self._categorical(last, rng)
        return i, j, k

    def _draw_c(self, rng: np.random.Generator) -> tuple[int, int, int]:
        k = self._categorical(self.center_c, rng)
        left = self.repeated_strength**2 * self.repeated_singleton_edge[:, k]
        right = self.singleton_strength * self.singleton_singleton_edge[:, k]
        total = float(np.sum(right, dtype=np.float64))
        i = self._categorical(left * (total - right), rng)
        last = right.copy()
        last[i] = 0.0
        j = self._categorical(last, rng)
        return i, j, k

    def sample(self, rng: np.random.Generator, count: int) -> Array:
        if type(count) is not int or count < 0:
            raise M146ContractError("count must be a nonnegative integer")
        answer = np.empty((count, 3), dtype=np.int64)
        normalizer = self.structured_normalizer
        banks = np.asarray((self.z_a, self.z_b, self.z_c), dtype=np.float64)
        for position in range(count):
            if normalizer <= 0.0 or float(rng.random()) < self.uniform_mixture:
                answer[position] = self._draw_uniform(rng)
                continue
            bank = self._categorical(banks, rng)
            if bank == 0:
                answer[position] = self._draw_a(rng)
            elif bank == 1:
                answer[position] = self._draw_b(rng)
            else:
                answer[position] = self._draw_c(rng)
        return answer


@dataclass(frozen=True)
class Defensive211Mixture:
    base: RoleAware211Proposal
    adaptive: RoleAware211Proposal
    base_mixture: float = 0.25

    def __post_init__(self) -> None:
        if self.base.width != self.adaptive.width:
            raise M146ContractError("defensive components have different widths")
        beta = float(self.base_mixture)
        if not math.isfinite(beta) or not (0.0 < beta < 1.0):
            raise M146ContractError("base_mixture must lie strictly between zero and one")
        object.__setattr__(self, "base_mixture", beta)

    @property
    def width(self) -> int:
        return self.base.width

    @property
    def ordered_population(self) -> int:
        return self.base.ordered_population

    @property
    def effective_uniform_weight(self) -> float:
        beta = self.base_mixture
        return beta * self.base.effective_uniform_weight + (
            1.0 - beta
        ) * self.adaptive.effective_uniform_weight

    @property
    def guaranteed_uniform_weight(self) -> float:
        return min(self.base.uniform_mixture, self.adaptive.uniform_mixture)

    def probability(self, repeated: int, left: int, right: int) -> float:
        beta = self.base_mixture
        answer = beta * self.base.probability(repeated, left, right) + (
            1.0 - beta
        ) * self.adaptive.probability(repeated, left, right)
        if len({repeated, left, right}) == 3:
            lower = self.guaranteed_uniform_weight / self.ordered_population
            if not math.isfinite(answer) or answer < lower:
                raise ArithmeticError("defensive mixture lost full support")
        return float(answer)

    def sample(self, rng: np.random.Generator, count: int) -> Array:
        if type(count) is not int or count < 0:
            raise M146ContractError("count must be a nonnegative integer")
        answer = np.empty((count, 3), dtype=np.int64)
        for position in range(count):
            component = self.base if float(rng.random()) < self.base_mixture else self.adaptive
            answer[position] = component.sample(rng, 1)[0]
        return answer


def make_base_proposal(
    bridge: Array,
    source_scale: Array,
    weight: Array,
    *,
    uniform_mixture: float = 0.05,
) -> RoleAware211Proposal:
    bridge = np.asarray(_finite_array("bridge", bridge, ndim=2), dtype=np.float64)
    if bridge.shape[0] != bridge.shape[1] or bridge.shape[0] < 3:
        raise M146ContractError("bridge must be square with width at least three")
    width = bridge.shape[0]
    if not np.allclose(bridge, bridge.T, rtol=0.0, atol=2e-12):
        raise M146ContractError("bridge must be symmetric")
    if not np.allclose(np.diag(bridge), 1.0, rtol=0.0, atol=2e-12):
        raise M146ContractError("bridge must have unit diagonal")
    scale = np.asarray(_finite_array("source_scale", source_scale, ndim=1), dtype=np.float64)
    if scale.shape != (width,) or np.any(scale < 0.0):
        raise M146ContractError("source_scale must be one nonnegative width-vector")
    weight = np.asarray(_finite_array("weight", weight, ndim=2), dtype=np.float64)
    if weight.shape[0] != width:
        raise M146ContractError("weight row count must equal bridge width")
    strength = scale * np.linalg.norm(weight, axis=1)
    residual = np.abs(bridge.copy())
    np.fill_diagonal(residual, 0.0)
    return RoleAware211Proposal(
        strength,
        strength,
        residual,
        residual,
        uniform_mixture=uniform_mixture,
    )


@dataclass(frozen=True)
class PilotScores:
    age_weights: Array
    centered_scores: Array
    all_zero: bool


@dataclass(frozen=True)
class FadingFields:
    repeated_node: Array
    singleton_node: Array
    repeated_singleton_edge: Array
    singleton_singleton_edge: Array


def pilot_scores(
    magnitudes: Array,
    base_probabilities: Array,
    *,
    rho: float = 31.0 / 32.0,
    relative_floor: float = 2.0**-24,
) -> PilotScores:
    magnitude = np.asarray(_finite_array("magnitudes", magnitudes, ndim=1), dtype=np.float64)
    probability = np.asarray(
        _finite_array("base_probabilities", base_probabilities, ndim=1), dtype=np.float64
    )
    if magnitude.size == 0 or magnitude.shape != probability.shape:
        raise M146ContractError("pilot arrays must have one equal positive length")
    if np.any(magnitude < 0.0) or np.any(probability <= 0.0):
        raise M146ContractError("pilot magnitudes must be nonnegative and probabilities positive")
    if not math.isfinite(rho) or not (0.0 < rho <= 1.0):
        raise M146ContractError("rho must lie in (0,1]")
    if not math.isfinite(relative_floor) or not (0.0 < relative_floor < 1.0):
        raise M146ContractError("relative_floor must lie in (0,1)")

    count = magnitude.size
    # Frozen indexing: pilot t=1 has exponent P-1; pilot t=P has exponent 0.
    age = np.power(rho, np.arange(count - 1, -1, -1, dtype=np.float64))
    maximum = float(np.max(magnitude))
    if maximum == 0.0:
        centered = np.zeros(count, dtype=np.float64)
        all_zero = True
    else:
        floor = relative_floor * maximum
        log_correction = np.log(np.maximum(magnitude, floor) / probability)
        centre = float(np.sum(age * log_correction) / np.sum(age))
        centered = np.clip((log_correction - centre) / math.log(16.0), -1.0, 1.0)
        all_zero = False
    age.setflags(write=False)
    centered.setflags(write=False)
    return PilotScores(age, centered, all_zero)


def _edge_ids(left: Array, right: Array, width: int) -> Array:
    low = np.minimum(left, right)
    high = np.maximum(left, right)
    return low * width + high


def fit_fading_fields(
    draws: Array,
    scores: PilotScores,
    *,
    width: int,
    pseudocount: float = 1.0,
    score_permutation: Array | None = None,
) -> FadingFields:
    draws = _readonly_int64("draws", draws, width=width)
    if draws.shape[0] != scores.centered_scores.size:
        raise M146ContractError("draw count and pilot score count disagree")
    if not math.isfinite(pseudocount) or pseudocount <= 0.0:
        raise M146ContractError("pseudocount must be finite and positive")
    score = np.asarray(scores.centered_scores, dtype=np.float64)
    if score_permutation is not None:
        permutation = np.asarray(score_permutation)
        if (
            permutation.shape != (score.size,)
            or not np.issubdtype(permutation.dtype, np.integer)
            or not np.array_equal(np.sort(permutation), np.arange(score.size))
        ):
            raise M146ContractError("score_permutation must be one exact permutation")
        score = score[permutation]
    age = np.asarray(scores.age_weights, dtype=np.float64)
    signed = age * score
    i, j, k = draws[:, 0], draws[:, 1], draws[:, 2]

    def state(ids: Array, numerator_weight: Array, denominator_weight: Array, size: int) -> Array:
        numerator = np.bincount(ids, weights=numerator_weight, minlength=size).astype(
            np.float64, copy=False
        )
        denominator = np.bincount(ids, weights=denominator_weight, minlength=size).astype(
            np.float64, copy=False
        )
        return numerator / (pseudocount + denominator)

    g_r = state(i, signed, age, width)
    singleton_ids = np.concatenate((j, k))
    g_s = state(
        singleton_ids,
        np.concatenate((signed, signed)),
        np.concatenate((age, age)),
        width,
    )

    rs_ids = np.concatenate((_edge_ids(i, j, width), _edge_ids(i, k, width)))
    rs_flat = state(
        rs_ids,
        np.concatenate((signed, signed)),
        np.concatenate((age, age)),
        width * width,
    ).reshape(width, width)
    ss_ids = _edge_ids(j, k, width)
    ss_flat = state(ss_ids, signed, age, width * width).reshape(width, width)
    g_rs = rs_flat + rs_flat.T
    g_ss = ss_flat + ss_flat.T
    np.fill_diagonal(g_rs, 0.0)
    np.fill_diagonal(g_ss, 0.0)

    fields: list[Array] = []
    for value in (g_r, g_s, g_rs, g_ss):
        value = np.array(value, dtype=np.float64, copy=True)
        if not np.all(np.isfinite(value)) or np.any(np.abs(value) > 1.0 + 2e-15):
            raise ArithmeticError("fading field escaped its [-1,1] bound")
        value.setflags(write=False)
        fields.append(value)
    return FadingFields(*fields)


def make_adapted_proposal(
    base: RoleAware211Proposal,
    fields: FadingFields,
) -> RoleAware211Proposal:
    width = base.width
    g_r = _vector("repeated_node", fields.repeated_node, width)
    g_s = _vector("singleton_node", fields.singleton_node, width)
    g_rs = _symmetric_hollow_signed(
        "repeated_singleton_edge field", fields.repeated_singleton_edge, width
    )
    g_ss = _symmetric_hollow_signed(
        "singleton_singleton_edge field", fields.singleton_singleton_edge, width
    )
    cap = math.log(2.0)
    return RoleAware211Proposal(
        base.repeated_strength * np.exp(cap * g_r),
        base.singleton_strength * np.exp(cap * g_s),
        base.repeated_singleton_edge * np.exp(cap * g_rs),
        base.singleton_singleton_edge * np.exp(cap * g_ss),
        uniform_mixture=base.uniform_mixture,
    )


def fit_defensive_mixture(
    base: RoleAware211Proposal,
    pilot_draws: Array,
    pilot_magnitudes: Array,
    *,
    rho: float = 31.0 / 32.0,
    pseudocount: float = 1.0,
    base_mixture: float = 0.25,
    score_permutation: Array | None = None,
) -> tuple[Defensive211Mixture, PilotScores, FadingFields]:
    draws = _readonly_int64("pilot_draws", pilot_draws, width=base.width)
    probabilities = np.asarray(
        [base.probability(*(int(item) for item in row)) for row in draws],
        dtype=np.float64,
    )
    scores = pilot_scores(pilot_magnitudes, probabilities, rho=rho)
    fields = fit_fading_fields(
        draws,
        scores,
        width=base.width,
        pseudocount=pseudocount,
        score_permutation=score_permutation,
    )
    adaptive = make_adapted_proposal(base, fields)
    return Defensive211Mixture(base, adaptive, base_mixture), scores, fields


def feature_norm_211_gram_batch(
    weight: Array,
    draws: Array,
    *,
    arithmetic_dtype: np.dtype | type = np.float64,
) -> Array:
    """Exact `(F31,F22)` Frobenius norm via a frozen batched Gram association.

    Association order is: construct rank-one left/right terms, reduce the last
    coordinate for every ordered term pair, multiply the two Gram tables, then
    reduce term-row followed by term-column.  Float32 is the target trace mode;
    float64 is the generated algebra/test mode.
    """

    dtype = np.dtype(arithmetic_dtype)
    if dtype not in {np.dtype(np.float32), np.dtype(np.float64)}:
        raise M146ContractError("arithmetic_dtype must be float32 or float64")
    weight = np.asarray(_finite_array("weight", weight, ndim=2), dtype=dtype)
    draws = _readonly_int64("draws", draws, width=weight.shape[0])
    if draws.shape[0] == 0:
        return np.empty(0, dtype=dtype)
    x = weight[draws[:, 0]]
    y = weight[draws[:, 1]]
    z = weight[draws[:, 2]]

    u31 = np.stack((dtype.type(6) * x * y * z, dtype.type(3) * x * x * z, dtype.type(3) * x * x * y), axis=1)
    v31 = np.stack((x, y, z), axis=1)
    u22 = np.stack((dtype.type(2) * x * x, dtype.type(2) * y * z, dtype.type(4) * x * y, dtype.type(4) * x * z), axis=1)
    v22 = np.stack((y * z, x * x, x * z, x * y), axis=1)

    def rank_sum_norm_sq(left: Array, right: Array) -> Array:
        gram_left = np.sum(
            left[:, :, None, :] * left[:, None, :, :], axis=-1, dtype=dtype
        )
        gram_right = np.sum(
            right[:, :, None, :] * right[:, None, :, :], axis=-1, dtype=dtype
        )
        row_sum = np.sum(gram_left * gram_right, axis=2, dtype=dtype)
        return np.sum(row_sum, axis=1, dtype=dtype)

    norm_sq = rank_sum_norm_sq(u31, v31) + rank_sum_norm_sq(u22, v22)
    tolerance = dtype.type(256) * np.finfo(dtype).eps * np.maximum(dtype.type(1), np.abs(norm_sq))
    if np.any(norm_sq < -tolerance):
        raise ArithmeticError("Gram feature norm became materially negative")
    return np.sqrt(np.maximum(norm_sq, dtype.type(0)), dtype=dtype)


def feature_norm_211_gram(
    weight: Array,
    repeated: int,
    left: int,
    right: int,
    *,
    arithmetic_dtype: np.dtype | type = np.float64,
) -> float:
    draw = np.asarray(((repeated, left, right),), dtype=np.int64)
    return float(feature_norm_211_gram_batch(weight, draw, arithmetic_dtype=arithmetic_dtype)[0])


def heterogeneous_phase_scales(
    coefficients: Array,
    probabilities: Array,
    *,
    total_count: int,
) -> Array:
    coefficient = np.asarray(_finite_array("coefficients", coefficients, ndim=1), dtype=np.float64)
    probability = np.asarray(_finite_array("probabilities", probabilities, ndim=1), dtype=np.float64)
    if coefficient.shape != probability.shape or coefficient.size == 0:
        raise M146ContractError("coefficient/probability vectors must have equal positive length")
    if type(total_count) is not int or total_count <= 0 or coefficient.size > total_count:
        raise M146ContractError("total_count must own every phase row")
    if np.any(probability <= 0.0):
        raise M146ContractError("phase probabilities must be strictly positive")
    scale = coefficient / (2.0 * float(total_count) * probability)
    if not np.all(np.isfinite(scale)):
        raise ArithmeticError("heterogeneous HH scale became nonfinite")
    return scale


def concatenate_phase_batch(
    base: RoleAware211Proposal,
    adaptive: Defensive211Mixture,
    pilot_draws: Array,
    pilot_coefficients: Array,
    main_draws: Array,
    main_coefficients: Array,
) -> tuple[Array, Array]:
    pilot = _readonly_int64("pilot_draws", pilot_draws, width=base.width)
    main = _readonly_int64("main_draws", main_draws, width=base.width)
    total = int(pilot.shape[0] + main.shape[0])
    if pilot.shape[0] == 0 or main.shape[0] == 0:
        raise M146ContractError("both pilot and main phases must be nonempty")
    p0 = np.asarray([base.probability(*map(int, row)) for row in pilot], dtype=np.float64)
    p1 = np.asarray([adaptive.probability(*map(int, row)) for row in main], dtype=np.float64)
    pilot_scale = heterogeneous_phase_scales(
        pilot_coefficients, p0, total_count=total
    )
    main_scale = heterogeneous_phase_scales(main_coefficients, p1, total_count=total)
    draws = np.concatenate((pilot, main), axis=0)
    scales = np.concatenate((pilot_scale, main_scale))
    draws.setflags(write=False)
    scales.setflags(write=False)
    return draws, scales


def heterogeneous_collision211_batched(
    weight: Array, draws: Array, scales: Array
) -> dict[str, Array]:
    """Five products for one concatenated batch with arbitrary per-row scales."""

    weight = np.asarray(_finite_array("weight", weight, ndim=2), dtype=np.float64)
    draws = _readonly_int64("draws", draws, width=weight.shape[0])
    scales = np.asarray(_finite_array("scales", scales, ndim=1), dtype=np.float64)
    if scales.shape != (draws.shape[0],) or draws.shape[0] == 0:
        raise M146ContractError("one finite scale is required for every nonempty row")
    x = weight[draws[:, 0]]
    y = weight[draws[:, 1]]
    z = weight[draws[:, 2]]
    aaab = (
        ((6.0 * scales)[:, None] * x * y * z).T @ x
        + ((3.0 * scales)[:, None] * x * x * z).T @ y
        + ((3.0 * scales)[:, None] * x * x * y).T @ z
    )
    first = ((2.0 * scales)[:, None] * x * x).T @ (y * z)
    second = ((4.0 * scales)[:, None] * x * y).T @ (x * z)
    aabb = first + first.T + second + second.T
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def heterogeneous_collision211_direct(
    weight: Array, draws: Array, scales: Array
) -> dict[str, Array]:
    weight = np.asarray(_finite_array("weight", weight, ndim=2), dtype=np.float64)
    draws = _readonly_int64("draws", draws, width=weight.shape[0])
    scales = np.asarray(_finite_array("scales", scales, ndim=1), dtype=np.float64)
    if scales.shape != (draws.shape[0],) or draws.shape[0] == 0:
        raise M146ContractError("one finite scale is required for every nonempty row")
    outputs = weight.shape[1]
    aaab = np.zeros((outputs, outputs), dtype=np.float64)
    aabb = np.zeros((outputs, outputs), dtype=np.float64)
    for row, scale in zip(draws, scales, strict=True):
        i, j, k = (int(item) for item in row)
        x, y, z = weight[i], weight[j], weight[k]
        aaab += scale * (
            6.0 * np.outer(x * y * z, x)
            + 3.0 * np.outer(x * x * z, y)
            + 3.0 * np.outer(x * x * y, z)
        )
        aabb += scale * (
            2.0 * np.outer(x * x, y * z)
            + 2.0 * np.outer(y * z, x * x)
            + 4.0 * np.outer(x * y, x * z)
            + 4.0 * np.outer(x * z, x * y)
        )
    return {"k4_aaaa": np.diag(aaab).copy(), "k4_aaab": aaab, "k4_aabb": aabb}


def proposal_probabilities(
    proposal: RoleAware211Proposal | Defensive211Mixture, units: Array
) -> Array:
    units = _readonly_int64("units", units, width=proposal.width)
    answer = np.asarray(
        [proposal.probability(*(int(item) for item in row)) for row in units],
        dtype=np.float64,
    )
    if not np.all(np.isfinite(answer)) or np.any(answer <= 0.0):
        raise ArithmeticError("proposal population contains nonpositive probability")
    return answer


def exact_trace_variance(
    contribution_norm_sq: Array,
    target_norm_sq: float,
    probabilities: Array,
) -> tuple[float, float]:
    norm_sq = np.asarray(
        _finite_array("contribution_norm_sq", contribution_norm_sq, ndim=1), dtype=np.float64
    )
    probability = np.asarray(
        _finite_array("probabilities", probabilities, ndim=1), dtype=np.float64
    )
    target = float(target_norm_sq)
    if norm_sq.shape != probability.shape or norm_sq.size == 0:
        raise M146ContractError("population arrays must have equal positive length")
    if np.any(norm_sq < 0.0) or np.any(probability <= 0.0) or not math.isfinite(target) or target < 0.0:
        raise M146ContractError("invalid variance population")
    if not math.isclose(float(np.sum(probability)), 1.0, rel_tol=0.0, abs_tol=5e-11):
        raise M146ContractError("population probabilities do not sum to one")
    second = float(np.sum(norm_sq / (4.0 * probability), dtype=np.float64))
    variance = second - target
    tolerance = 64.0 * np.finfo(np.float64).eps * max(abs(second), abs(target), np.finfo(np.float64).tiny)
    if variance < -tolerance:
        raise ArithmeticError("trace variance is materially negative")
    return max(0.0, variance), tolerance


def exact_rmain(
    contribution_norm_sq: Array,
    target_norm_sq: float,
    base_probabilities: Array,
    adaptive_probabilities: Array,
) -> dict[str, float]:
    base_variance, tolerance = exact_trace_variance(
        contribution_norm_sq, target_norm_sq, base_probabilities
    )
    if base_variance <= tolerance:
        raise UnresolvedBaselineVariance(
            "V(q0) is zero or unresolved; Rmain is undefined and the screen must fail closed"
        )
    adaptive_variance, _ = exact_trace_variance(
        contribution_norm_sq, target_norm_sq, adaptive_probabilities
    )
    return {
        "base_variance": base_variance,
        "adaptive_variance": adaptive_variance,
        "ratio": adaptive_variance / base_variance,
        "resolution": tolerance,
    }


@dataclass(frozen=True)
class WeightedTailPopulation:
    values: Array
    weights: Array


def complete_phase_tail_population(
    contribution_norm_sq: Array,
    base_probabilities: Array,
    adaptive_probabilities: Array,
    *,
    pilot_fraction: float = 0.125,
) -> tuple[WeightedTailPopulation, WeightedTailPopulation]:
    norm_sq = np.asarray(
        _finite_array("contribution_norm_sq", contribution_norm_sq, ndim=1), dtype=np.float64
    )
    q0 = np.asarray(_finite_array("base_probabilities", base_probabilities, ndim=1), dtype=np.float64)
    q1 = np.asarray(
        _finite_array("adaptive_probabilities", adaptive_probabilities, ndim=1), dtype=np.float64
    )
    if not (norm_sq.shape == q0.shape == q1.shape) or np.any(norm_sq < 0.0) or np.any(q0 <= 0.0) or np.any(q1 <= 0.0):
        raise M146ContractError("invalid tail population")
    f = float(pilot_fraction)
    if not math.isfinite(f) or not (0.0 < f < 1.0):
        raise M146ContractError("pilot_fraction must lie strictly between zero and one")
    for probability in (q0, q1):
        if not math.isclose(float(np.sum(probability)), 1.0, rel_tol=0.0, abs_tol=5e-11):
            raise M146ContractError("tail probabilities do not sum to one")
    h0_sq = norm_sq / (4.0 * q0 * q0)
    h1_sq = norm_sq / (4.0 * q1 * q1)
    candidate = WeightedTailPopulation(
        np.concatenate((h0_sq, h1_sq)), np.concatenate((f * q0, (1.0 - f) * q1))
    )
    baseline = WeightedTailPopulation(h0_sq.copy(), q0.copy())
    return candidate, baseline


def weighted_quantile_lower_cdf(
    values: Array, weights: Array, quantile: float
) -> float:
    value = np.asarray(_finite_array("values", values, ndim=1), dtype=np.float64)
    weight = np.asarray(_finite_array("weights", weights, ndim=1), dtype=np.float64)
    q = float(quantile)
    if value.shape != weight.shape or value.size == 0 or np.any(weight < 0.0):
        raise M146ContractError("weighted quantile arrays are invalid")
    if not math.isfinite(q) or not (0.0 <= q <= 1.0):
        raise M146ContractError("quantile must lie in [0,1]")
    total = float(np.sum(weight, dtype=np.float64))
    if total <= 0.0:
        raise M146ContractError("weighted quantile has zero total weight")
    order = np.argsort(value, kind="stable")
    cumulative = np.cumsum(weight[order], dtype=np.float64)
    threshold = q * total
    index = min(int(np.searchsorted(cumulative, threshold, side="left")), value.size - 1)
    return float(value[order[index]])


def pooled_complete_phase_p99_ratio(
    candidate_records: Sequence[WeightedTailPopulation],
    baseline_records: Sequence[WeightedTailPopulation],
) -> float:
    if len(candidate_records) == 0 or len(candidate_records) != len(baseline_records):
        raise M146ContractError("tail scopes need equal nonempty record lists")

    def pool(records: Sequence[WeightedTailPopulation]) -> tuple[Array, Array]:
        values: list[Array] = []
        weights: list[Array] = []
        record_weight = 1.0 / len(records)
        for record in records:
            value = np.asarray(_finite_array("tail values", record.values, ndim=1), dtype=np.float64)
            weight = np.asarray(_finite_array("tail weights", record.weights, ndim=1), dtype=np.float64)
            if value.shape != weight.shape or value.size == 0 or np.any(weight < 0.0):
                raise M146ContractError("invalid tail record")
            total = float(np.sum(weight, dtype=np.float64))
            if total <= 0.0:
                raise M146ContractError("tail record has zero mass")
            values.append(value)
            weights.append(record_weight * weight / total)
        return np.concatenate(values), np.concatenate(weights)

    candidate_value, candidate_weight = pool(candidate_records)
    baseline_value, baseline_weight = pool(baseline_records)
    numerator = weighted_quantile_lower_cdf(candidate_value, candidate_weight, 0.99)
    denominator = weighted_quantile_lower_cdf(baseline_value, baseline_weight, 0.99)
    if denominator <= 0.0:
        raise UnresolvedBaselineVariance("base p99 squared contribution is zero")
    return numerator / denominator


@dataclass(frozen=True)
class PremiseRecord:
    family: str
    width: int
    cell_seed: int
    repetition: int
    error_q0: float
    error_m133: float
    error_m146: float
    error_shuffle: float
    main_variance_base: float
    main_variance_adaptive: float

    def __post_init__(self) -> None:
        if not self.family or min(self.width, self.repetition + 1) <= 0:
            raise M146ContractError("invalid premise record key")
        values = (
            self.error_q0,
            self.error_m133,
            self.error_m146,
            self.error_shuffle,
            self.main_variance_base,
            self.main_variance_adaptive,
        )
        if not all(math.isfinite(float(value)) and float(value) >= 0.0 for value in values):
            raise M146ContractError("premise metrics must be finite and nonnegative")

    @property
    def key(self) -> tuple[str, int, int, int]:
        return self.family, self.width, self.cell_seed, self.repetition


@dataclass(frozen=True)
class FrozenGateThresholds:
    primary_ratio_max: float = 0.75
    primary_upper90_strict_max: float = 0.90
    rmain_max: float = 5.0 / 7.0
    attribution_ratio_max: float = 0.90
    attribution_upper90_strict_max: float = 1.00
    p99_ratio_max: float = 1.25


def validate_protocol_completeness(
    records: Sequence[PremiseRecord],
    *,
    families: Sequence[str],
    widths: Sequence[int],
    cell_seeds: Sequence[int],
    repetitions: int,
) -> None:
    if repetitions <= 0 or not families or not widths or not cell_seeds:
        raise M146ContractError("expected protocol grid is empty")
    expected = {
        (family, width, seed, repetition)
        for family in families
        for width in widths
        for seed in cell_seeds
        for repetition in range(repetitions)
    }
    actual = [record.key for record in records]
    if len(actual) != len(set(actual)):
        raise M146ContractError("duplicate premise record key")
    missing = expected - set(actual)
    extra = set(actual) - expected
    if missing or extra:
        raise M146ContractError(
            f"incomplete premise protocol: missing={len(missing)}, extra={len(extra)}"
        )


def _ratio_of_sums(numerator: Array, denominator: Array, name: str) -> float:
    top = float(np.sum(numerator, dtype=np.float64))
    bottom = float(np.sum(denominator, dtype=np.float64))
    if not math.isfinite(top) or not math.isfinite(bottom) or bottom <= 0.0:
        raise UnresolvedBaselineVariance(f"{name} denominator is zero or nonfinite")
    return top / bottom


def _bootstrap_ratio_upper90(
    numerator: Array,
    denominator: Array,
    *,
    seed_words: Sequence[int],
    resamples: int = 10_000,
) -> float:
    numerator = np.asarray(numerator, dtype=np.float64)
    denominator = np.asarray(denominator, dtype=np.float64)
    if numerator.shape != denominator.shape or numerator.size == 0 or resamples <= 0:
        raise M146ContractError("invalid bootstrap arrays")
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(seed_words)))
    ratios = np.empty(resamples, dtype=np.float64)
    for position in range(resamples):
        index = rng.integers(0, numerator.size, size=numerator.size)
        ratios[position] = _ratio_of_sums(
            numerator[index], denominator[index], "bootstrap ratio"
        )
    return float(np.quantile(ratios, 0.9, method="higher"))


def evaluate_scope_gates(
    records: Sequence[PremiseRecord],
    *,
    p99_ratio: float,
    scope_code: int,
    thresholds: FrozenGateThresholds = FrozenGateThresholds(),
) -> dict[str, float | bool]:
    if not records:
        raise M146ContractError("gate scope is empty")
    ordered = sorted(records, key=lambda record: record.key)
    e0 = np.asarray([record.error_q0 for record in ordered], dtype=np.float64)
    e146 = np.asarray([record.error_m146 for record in ordered], dtype=np.float64)
    eshuffle = np.asarray([record.error_shuffle for record in ordered], dtype=np.float64)
    v0 = np.asarray([record.main_variance_base for record in ordered], dtype=np.float64)
    v1 = np.asarray([record.main_variance_adaptive for record in ordered], dtype=np.float64)
    primary = _ratio_of_sums(e146, e0, "primary")
    attribution = _ratio_of_sums(e146, eshuffle, "attribution")
    rmain = _ratio_of_sums(v1, v0, "Rmain")
    primary_upper = _bootstrap_ratio_upper90(
        e146, e0, seed_words=(146000007, 0x14604, scope_code, 1)
    )
    attribution_upper = _bootstrap_ratio_upper90(
        e146, eshuffle, seed_words=(146000007, 0x14604, scope_code, 2)
    )
    widths = sorted({record.width for record in ordered})
    if len(widths) < 2:
        raise M146ContractError("width-trend gate needs at least two widths")
    by_width: dict[int, float] = {}
    for width in widths:
        selected = [record for record in ordered if record.width == width]
        by_width[width] = _ratio_of_sums(
            np.asarray([record.error_m146 for record in selected]),
            np.asarray([record.error_q0 for record in selected]),
            f"width-{width} primary",
        )
    width_pass = by_width[widths[-1]] <= by_width[widths[0]]
    p99 = float(p99_ratio)
    if not math.isfinite(p99) or p99 < 0.0:
        raise M146ContractError("p99 ratio must be finite and nonnegative")
    result: dict[str, float | bool] = {
        "primary_ratio": primary,
        "primary_upper90": primary_upper,
        "rmain_ratio_of_summed_exact_variances": rmain,
        "attribution_ratio": attribution,
        "attribution_upper90": attribution_upper,
        "smallest_width_ratio": by_width[widths[0]],
        "largest_width_ratio": by_width[widths[-1]],
        "width_pass": width_pass,
        "p99_ratio_of_pooled_complete_phase_quantiles": p99,
    }
    result["primary_pass"] = (
        primary <= thresholds.primary_ratio_max
        and primary_upper < thresholds.primary_upper90_strict_max
        and rmain <= thresholds.rmain_max
        and width_pass
        and p99 <= thresholds.p99_ratio_max
    )
    result["attribution_pass"] = (
        attribution <= thresholds.attribution_ratio_max
        and attribution_upper < thresholds.attribution_upper90_strict_max
        and width_pass
    )
    result["all_pass"] = bool(result["primary_pass"] and result["attribution_pass"])
    return result


def evaluate_all_family_gates(
    records: Sequence[PremiseRecord],
    *,
    families: Sequence[str],
    widths: Sequence[int],
    cell_seeds: Sequence[int],
    repetitions: int,
    p99_ratios: Mapping[str, float],
) -> dict[str, object]:
    validate_protocol_completeness(
        records,
        families=families,
        widths=widths,
        cell_seeds=cell_seeds,
        repetitions=repetitions,
    )
    if set(p99_ratios) != {"pooled", *families}:
        raise M146ContractError("p99 ratios must contain exactly pooled and every family")
    result: dict[str, object] = {}
    result["pooled"] = evaluate_scope_gates(
        records, p99_ratio=p99_ratios["pooled"], scope_code=0xA11
    )
    family_results: dict[str, object] = {}
    for position, family in enumerate(families):
        selected = [record for record in records if record.family == family]
        family_results[family] = evaluate_scope_gates(
            selected, p99_ratio=p99_ratios[family], scope_code=0xF00 + position
        )
    result["families"] = family_results
    result["all_pass"] = bool(
        result["pooled"]["all_pass"]
        and all(value["all_pass"] for value in family_results.values())
    )
    return result


def proposal_snapshot_digest(
    proposal: RoleAware211Proposal | Defensive211Mixture,
) -> str:
    digest = hashlib.sha256()
    components = (
        (proposal.base, proposal.adaptive)
        if isinstance(proposal, Defensive211Mixture)
        else (proposal,)
    )
    for component in components:
        for value in (
            component.repeated_strength,
            component.singleton_strength,
            component.repeated_singleton_edge,
            component.singleton_singleton_edge,
            component.center_a,
            component.center_b,
            component.center_c,
        ):
            digest.update(np.asarray(value, dtype=np.float64).tobytes(order="C"))
        digest.update(np.float64(component.uniform_mixture).tobytes())
    if isinstance(proposal, Defensive211Mixture):
        digest.update(np.float64(proposal.base_mixture).tobytes())
    return digest.hexdigest()
