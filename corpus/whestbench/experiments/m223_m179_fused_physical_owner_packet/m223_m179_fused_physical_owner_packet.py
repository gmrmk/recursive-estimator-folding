"""M223 seam prototype: one M178 jet shared by M179 fields and fourth owners.

This module deliberately does not call M179's opaque ``pair_moments`` as a
source of reuse: that function owns and discards its jet.  It exposes the
small seam a native M179 caller would have to supply, with object-identity and
one-use streaming guards.  No source coefficient, tree, response, or variance
logic is present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _sibling in ("m178_certified_phi2_owent",):
    _path = str(EXPERIMENTS / _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import m178_certified_phi2_owent as m178  # noqa: E402


MUTATION = "M223"
M178_CALLS_PER_SPD_PACKET = 1
OWNER_INCREMENTAL_FLOP_CEILING_PER_PAIR = 512
N_TARGET = 256
LAYERS_TARGET = 31
ALL_LAYER_OWNER_CEILING = (
    LAYERS_TARGET * N_TARGET * (N_TARGET - 1) // 2
    * OWNER_INCREMENTAL_FLOP_CEILING_PER_PAIR
)


class M223Refusal(RuntimeError):
    """Typed fail-closed refusal for an invalid seam, chart, or lifecycle."""


@dataclass(frozen=True)
class EndpointUnary:
    """One endpoint's M179 marginal and M223 raw positive-part cache."""

    mean: float
    sigma: float
    alpha: float
    probability: float
    density: float
    raw1: float
    raw2: float
    raw3: float
    raw4: float

    @property
    def variance(self) -> float:
        return self.raw2 - self.raw1 * self.raw1

    @property
    def kappa4(self) -> float:
        central4 = (
            self.raw4 - 4.0 * self.raw1 * self.raw3
            + 6.0 * self.raw1 * self.raw1 * self.raw2 - 3.0 * self.raw1 ** 4
        )
        return central4 - 3.0 * self.variance * self.variance


@dataclass(frozen=True)
class M179CompatiblePair:
    """The off-diagonal fields produced by the M179 G1 pair assembly."""

    e_relu_relu: float
    cov: float
    K: float
    Hmu_ij: float
    Hmu_ji: float
    Hv_ij: float
    Hv_ji: float


@dataclass(frozen=True)
class BoundaryCache:
    """All endpoint boundary moments needed by both directed owner orders."""

    s2: float
    bx0: float
    bx1: float
    bx2: float
    by0: float
    by1: float
    by2: float


@dataclass(frozen=True)
class PhysicalOwners:
    """Connected physical values; no tree subtraction or source semantics."""

    k4_i: float
    k4_j: float
    k31_ij: float
    k31_ji: float
    k22_ij: float
    raw_m31_ij: float
    raw_m31_ji: float
    raw_m22: float


@dataclass
class LayerPrecontext:
    """Reference-bound live pre-ReLU context with one packet in flight."""

    layer: int
    epoch: int
    a: np.ndarray
    C: np.ndarray
    provenance: str
    _closed: bool = field(default=False, init=False, repr=False)
    _in_flight: object | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.layer, int) or self.layer < 1 or not isinstance(self.epoch, int):
            raise M223Refusal("INVALID_LAYER_OR_EPOCH")
        if (not isinstance(self.a, np.ndarray) or not isinstance(self.C, np.ndarray)
                or self.a.dtype != np.float64 or self.C.dtype != np.float64):
            raise M223Refusal("LIVE_F64_ARRAYS_REQUIRED")
        if self.a.ndim != 1 or self.C.shape != (self.a.size, self.a.size):
            raise M223Refusal("PRECONTEXT_SHAPE")
        if not np.array_equal(self.C, self.C.T):
            raise M223Refusal("PRECONTEXT_NOT_BITWISE_SYMMETRIC")
        if not np.all(np.isfinite(self.a)) or not np.all(np.isfinite(self.C)):
            raise M223Refusal("PRECONTEXT_NONFINITE")

    @property
    def a_identity(self) -> int:
        return id(self.a)

    @property
    def C_identity(self) -> int:
        return id(self.C)

    def close(self) -> None:
        if self._in_flight is not None:
            raise M223Refusal("PACKET_MUST_BE_CONSUMED_BEFORE_CLOSE")
        self._closed = True


@dataclass(frozen=True)
class FrozenOwnerSelection:
    """Pre-loop, context-bound selection only; it has no proposal mechanism."""

    layer: int
    epoch: int
    a_identity: int
    C_identity: int
    pair_indices: tuple[tuple[int, int], ...]
    k4_indices: tuple[int, ...]

    @classmethod
    def from_context(cls, context: LayerPrecontext,
                     pair_indices: tuple[tuple[int, int], ...],
                     k4_indices: tuple[int, ...]) -> "FrozenOwnerSelection":
        if context._closed or context._in_flight is not None:
            raise M223Refusal("SELECTION_REQUIRES_IDLE_LIVE_PRECONTEXT")
        pairs = tuple(pair_indices)
        nodes = tuple(k4_indices)
        if pairs != tuple(sorted(set(pairs))) or nodes != tuple(sorted(set(nodes))):
            raise M223Refusal("SELECTION_MUST_BE_SORTED_UNIQUE_AND_FROZEN")
        if any(not (0 <= i < j < context.a.size) for i, j in pairs):
            raise M223Refusal("SELECTION_PAIR_RANGE_OR_ORIENTATION")
        if any(not (0 <= index < context.a.size) for index in nodes):
            raise M223Refusal("SELECTION_K4_RANGE")
        return cls(context.layer, context.epoch, id(context.a), id(context.C), pairs, nodes)

    def _check_context(self, context: LayerPrecontext) -> None:
        if (context.layer != self.layer or context.epoch != self.epoch
                or id(context.a) != self.a_identity or id(context.C) != self.C_identity):
            raise M223Refusal("SELECTION_PRECONTEXT_SUBSTITUTION")
        if context._closed:
            raise M223Refusal("PRECONTEXT_CLOSED")

    def selects_pair(self, context: LayerPrecontext, i: int, j: int) -> bool:
        self._check_context(context)
        return (i, j) in self.pair_indices

    def selects_k4(self, context: LayerPrecontext, index: int) -> bool:
        self._check_context(context)
        return index in self.k4_indices


@dataclass(frozen=True)
class K4Emission:
    """A diagonal-owner handoff from M179's already-created unary cache."""

    layer: int
    epoch: int
    index: int
    kappa4: float
    a_identity: int
    C_identity: int
    additional_special_function_calls: int = 0


@dataclass
class FusedOwnerPacket:
    """A single streaming pair packet. It cannot be copied into an owner cache."""

    context: LayerPrecontext
    i: int
    j: int
    pair: M179CompatiblePair
    owners: PhysicalOwners
    jet: m178.M178Result
    boundaries: BoundaryCache
    m179_jet_identity: int
    owner_jet_identity: int
    owner_boundary_identity: int
    endpoint_unary_calls: int
    conditional_unary_calls: int
    owner_special_function_calls: int
    m178_calls: int
    _consumed: bool = field(default=False, init=False, repr=False)

    @property
    def layer(self) -> int:
        return self.context.layer

    @property
    def epoch(self) -> int:
        return self.context.epoch

    @property
    def a_identity(self) -> int:
        return self.context.a_identity

    @property
    def C_identity(self) -> int:
        return self.context.C_identity

    def consume(self, context: LayerPrecontext) -> PhysicalOwners:
        if context is not self.context:
            raise M223Refusal("FOREIGN_PRECONTEXT")
        if self._consumed or context._in_flight is not self:
            raise M223Refusal("PACKET_ALREADY_RETIRED")
        if context._closed:
            raise M223Refusal("PRECONTEXT_CLOSED")
        if self.layer != context.layer or self.epoch != context.epoch:
            raise M223Refusal("LAYER_EPOCH_SUBSTITUTION")
        if self.a_identity != id(context.a) or self.C_identity != id(context.C):
            raise M223Refusal("PRECONTEXT_IDENTITY_SUBSTITUTION")
        self._consumed = True
        context._in_flight = None
        return self.owners


def _endpoint_unary(mean: float, sigma: float) -> EndpointUnary:
    """M179's endpoint backbone, extended algebraically through raw order four.

    Exactly one M178 Phi and one M178 phi chart are called for this endpoint.
    M223 owners consume the returned object; they make no special-function call.
    """
    if not math.isfinite(mean) or not math.isfinite(sigma) or sigma <= 0.0:
        raise M223Refusal("INVALID_SPD_ENDPOINT")
    alpha = mean / sigma
    bk = m178.Backend()
    probability, _ = m178._Phi_cert(bk, alpha)
    density, _ = m178._phi_cert(bk, alpha)
    p, q = float(probability), float(density)
    raw1 = sigma * (alpha * p + q)
    raw2 = sigma * sigma * ((alpha * alpha + 1.0) * p + alpha * q)
    raw3 = sigma ** 3 * ((alpha ** 3 + 3.0 * alpha) * p + (alpha * alpha + 2.0) * q)
    raw4 = sigma ** 4 * ((alpha ** 4 + 6.0 * alpha * alpha + 3.0) * p
                           + (alpha ** 3 + 5.0 * alpha) * q)
    if not all(math.isfinite(value) for value in (p, q, raw1, raw2, raw3, raw4)):
        raise M223Refusal("NONFINITE_UNARY_CACHE")
    return EndpointUnary(mean, sigma, alpha, p, q, raw1, raw2, raw3, raw4)


def _m179_pair_from_shared_jet(left: EndpointUnary, right: EndpointUnary,
                               rho: float, jet: m178.M178Result) -> tuple[M179CompatiblePair, int]:
    """M179 G1 equations, consuming the provided M178Result by object identity."""
    if jet.refused:
        raise M223Refusal("M178_" + jet.reason)
    s2 = (1.0 - rho) * (1.0 + rho)
    if s2 <= 0.0:
        raise M223Refusal("NON_SPD_OR_RANK_ONE_CHART")
    s = math.sqrt(s2)
    K, da, db, dr = jet.value, jet.d_a, jet.d_b, jet.d_rho
    ez_i = da + rho * db
    ez_j = db + rho * da
    ez_ij = rho * K - rho * (left.alpha * da + right.alpha * db) + s2 * dr
    e_relu_relu = (
        left.mean * right.mean * K
        + left.mean * right.sigma * ez_j
        + right.mean * left.sigma * ez_i
        + left.sigma * right.sigma * ez_ij
    )
    hmu_ij = right.mean * K + right.sigma * ez_j - left.probability * right.raw1
    hmu_ji = left.mean * K + left.sigma * ez_i - right.probability * left.raw1

    # These two conditional endpoint charts are M179 work.  The owner path
    # below uses only left/right and therefore contributes zero such calls.
    cond_j = _endpoint_unary(right.mean - rho * left.alpha * right.sigma, right.sigma * s)
    cond_i = _endpoint_unary(left.mean - rho * right.alpha * left.sigma, left.sigma * s)
    r_i = left.density / (2.0 * left.sigma)
    r_j = right.density / (2.0 * right.sigma)
    f_i0, f_j0 = left.density / left.sigma, right.density / right.sigma
    hv_ij = 0.5 * f_i0 * cond_j.raw1 - r_i * right.raw1
    hv_ji = 0.5 * f_j0 * cond_i.raw1 - r_j * left.raw1
    result = M179CompatiblePair(
        e_relu_relu=e_relu_relu,
        cov=e_relu_relu - left.raw1 * right.raw1,
        K=K,
        Hmu_ij=hmu_ij,
        Hmu_ji=hmu_ji,
        Hv_ij=hv_ij,
        Hv_ji=hv_ji,
    )
    if not all(math.isfinite(value) for value in result.__dict__.values()):
        raise M223Refusal("NONFINITE_M179_FIELDS")
    return result, 4  # Phi/phi once at each of M179's two conditional charts


def _boundary_cache(left: EndpointUnary, right: EndpointUnary, rho: float,
                    jet: m178.M178Result) -> BoundaryCache:
    """Derive both orientations' boundary moments once from the shared jet."""
    sx, sy, s2 = left.sigma, right.sigma, (1.0 - rho) * (1.0 + rho)
    tx, ty = left.alpha - rho * right.alpha, right.alpha - rho * left.alpha
    bx0, by0 = jet.d_a / sx, jet.d_b / sy
    bx1 = sy / sx * (ty * jet.d_a + s2 * jet.d_rho)
    bx2 = sy * sy / sx * ((ty * ty + s2) * jet.d_a + ty * s2 * jet.d_rho)
    by1 = sx / sy * (tx * jet.d_b + s2 * jet.d_rho)
    by2 = sx * sx / sy * ((tx * tx + s2) * jet.d_b + tx * s2 * jet.d_rho)
    values = (s2, bx0, bx1, bx2, by0, by1, by2)
    if s2 <= 0.0 or not all(math.isfinite(value) for value in values):
        raise M223Refusal("NONFINITE_OR_NONSPD_BOUNDARY_CACHE")
    return BoundaryCache(*values)


def _central31(left: EndpointUnary, right: EndpointUnary, m11: float, m21: float, m31: float) -> float:
    u, v = left.raw1, right.raw1
    return (
        m31 - v * left.raw3 - 3.0 * u * m21 + 3.0 * u * v * left.raw2
        + 3.0 * u * u * m11 - 3.0 * u ** 3 * v
    )


def _central22(left: EndpointUnary, right: EndpointUnary, m11: float, m12: float, m21: float, m22: float) -> float:
    u, v = left.raw1, right.raw1
    return (
        m22 - 2.0 * v * m21 + v * v * left.raw2 - 2.0 * u * m12
        + 4.0 * u * v * m11 - 2.0 * u * u * v * v
        + u * u * right.raw2 - u * u * v * v
    )


def _owner_direction(left: EndpointUnary, right: EndpointUnary, rho: float,
                     jet: m178.M178Result, boundaries: BoundaryCache,
                     *, reverse: bool = False) -> tuple[float, float, float, float]:
    """M220's corrected joint-base recurrence for ordered (left^3,right)."""
    mx, my, sx, sy = left.mean, right.mean, left.sigma, right.sigma
    vx, vy, cov = sx * sx, sy * sy, rho * sx * sy
    if reverse:
        bx0, bx1, bx2 = boundaries.by0, boundaries.by1, boundaries.by2
        by0, by1 = boundaries.bx0, boundaries.bx1
    else:
        bx0, bx1, bx2 = boundaries.bx0, boundaries.bx1, boundaries.bx2
        by0, by1 = boundaries.by0, boundaries.by1

    # These base/column moments are joint over both positive half-lines.
    j01 = my * jet.value + cov * bx0 + vy * by0
    j02 = my * j01 + cov * bx1 + vy * jet.value
    j10 = mx * jet.value + vx * bx0 + cov * by0
    j20 = mx * j10 + vx * jet.value + cov * by1
    m11 = mx * j01 + vx * bx1 + cov * jet.value
    m21 = mx * m11 + vx * j01 + cov * j10
    m31 = mx * m21 + 2.0 * vx * m11 + cov * j20
    m12 = mx * j02 + vx * bx2 + 2.0 * cov * j01
    m22 = mx * m12 + vx * j02 + 2.0 * cov * m11
    central31 = _central31(left, right, m11, m21, m31)
    central22 = _central22(left, right, m11, m12, m21, m22)
    covariance = m11 - left.raw1 * right.raw1
    k31 = central31 - 3.0 * left.variance * covariance
    k22 = central22 - left.variance * right.variance - 2.0 * covariance * covariance
    if not all(math.isfinite(value) for value in (m31, m22, k31, k22)):
        raise M223Refusal("NONFINITE_OWNER")
    return m31, m22, k31, k22


def _owners_from_shared_jet(left: EndpointUnary, right: EndpointUnary,
                            rho: float, jet: m178.M178Result,
                            boundaries: BoundaryCache) -> PhysicalOwners:
    """Use exactly the supplied jet.  The reverse direction swaps derivative roles."""
    raw31, raw_m22, k31, k22 = _owner_direction(left, right, rho, jet, boundaries)
    raw13, _raw_m22_reverse, k13, _k22_reverse = _owner_direction(
        right, left, rho, jet, boundaries, reverse=True)
    return PhysicalOwners(left.kappa4, right.kappa4, k31, k13, k22, raw31, raw13, raw_m22)


def fuse_next_pair(context: LayerPrecontext, i: int, j: int) -> FusedOwnerPacket:
    """Emit one packet and retain it until the identical context consumes it."""
    if context._closed:
        raise M223Refusal("PRECONTEXT_CLOSED")
    if context._in_flight is not None:
        raise M223Refusal("PREVIOUS_PACKET_NOT_RETIRED")
    if not (0 <= i < j < context.a.size):
        raise M223Refusal("PAIR_INDEX_ORIENTATION")
    vx, vy = float(context.C[i, i]), float(context.C[j, j])
    if vx <= 0.0 or vy <= 0.0:
        raise M223Refusal("ZERO_VARIANCE_OUTSIDE_FUSED_SPD")
    sx, sy = math.sqrt(vx), math.sqrt(vy)
    rho = float(context.C[i, j]) / (sx * sy)
    if not math.isfinite(rho) or abs(rho) > m178.RHO_MAX:
        raise M223Refusal("NON_SPD_OR_RANK_ONE_CHART")
    left, right = _endpoint_unary(float(context.a[i]), sx), _endpoint_unary(float(context.a[j]), sy)
    # The only production jet source is the M178 provider. Test-time hostile
    # substitutions patch this symbol around the call; callers cannot inject a
    # look-alike object through this ABI.
    jet = m178.evaluate(left.alpha, right.alpha, rho)
    if not isinstance(jet, m178.M178Result):
        raise M223Refusal("HOSTILE_JET_TYPE_SUBSTITUTION")
    if jet.refused:
        raise M223Refusal("M178_" + jet.reason)
    boundaries = _boundary_cache(left, right, rho, jet)
    pair, conditional_calls = _m179_pair_from_shared_jet(left, right, rho, jet)
    owners = _owners_from_shared_jet(left, right, rho, jet, boundaries)
    packet = FusedOwnerPacket(
        context=context, i=i, j=j, pair=pair, owners=owners, jet=jet, boundaries=boundaries,
        m179_jet_identity=id(jet), owner_jet_identity=id(jet),
        owner_boundary_identity=id(boundaries),
        endpoint_unary_calls=4, conditional_unary_calls=conditional_calls,
        owner_special_function_calls=0, m178_calls=1,
    )
    context._in_flight = packet
    return packet


def maybe_fuse_selected_pair(selection: FrozenOwnerSelection, context: LayerPrecontext,
                              i: int, j: int) -> FusedOwnerPacket | None:
    """M179-loop hook: no packet and no M178 call for an unselected pair."""
    if not selection.selects_pair(context, i, j):
        return None
    return fuse_next_pair(context, i, j)


def emit_selected_k4(selection: FrozenOwnerSelection, context: LayerPrecontext,
                     index: int, m179_unary: EndpointUnary) -> K4Emission | None:
    """Emit K4 from a supplied M179 diagonal cache; never evaluates Phi/phi."""
    if not selection.selects_k4(context, index):
        return None
    variance = float(context.C[index, index])
    if variance <= 0.0 or not math.isclose(m179_unary.mean, float(context.a[index]), rel_tol=0.0, abs_tol=0.0):
        raise M223Refusal("HOSTILE_DIAGONAL_UNARY_SUBSTITUTION")
    expected_sigma = math.sqrt(variance)
    if not math.isclose(m179_unary.sigma, expected_sigma, rel_tol=0.0, abs_tol=0.0):
        raise M223Refusal("HOSTILE_DIAGONAL_UNARY_SUBSTITUTION")
    return K4Emission(context.layer, context.epoch, index, m179_unary.kappa4,
                      id(context.a), id(context.C))
