"""M200 response-free streaming overlap fixture.

This is deliberately a *semantic and liveness* harness, not a target runner.
It streams one M179 state at a time into M198 and M125b.  The nonzero
Source211 packets are deterministic generated fixtures: their mathematical
provider and all native target costs remain unknown.  In particular this file
does not load contest inputs, scores, responses, or a submission artifact.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for directory in (
    EXPERIMENTS / "m125_source_batched_forward_tangent",
    EXPERIMENTS / "m167_collision_owner_unification",
    EXPERIMENTS / "m172_selective_22_owner_fusion",
    EXPERIMENTS / "m178_certified_phi2_owent",
    EXPERIMENTS / "m179_background_archive_producer",
    EXPERIMENTS / "m198_source211_delay_one_adapter",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from m125_forward_tangent import TangentState, tangent_stage  # noqa: E402
from m167_collision_owner_unification import PhysicalFourthOwners  # noqa: E402
import m179_background_producer as m179_producer  # noqa: E402
import m179_jacobian_archive as m179_archive  # noqa: E402
import m198_source211_delay_one_adapter as m198  # noqa: E402


PARITY_MAX_ABS = 2.0e-12
FROZEN_WIDTHS = (2, 3, 4, 5, 6, 7)
FROZEN_DEPTHS = (3, 4, 5, 6)
FROZEN_REPLICATES = (0, 1)
FIXTURE_EPOCH = 200


def _array_digest(*named_arrays: tuple[str, np.ndarray]) -> str:
    """A local, public byte digest; it is an integrity convention, not a MAC."""

    digest = hashlib.sha256()
    digest.update(b"m200-array-digest-v1\0")
    for name, value in named_arrays:
        array = np.ascontiguousarray(np.asarray(value, dtype="<f8"))
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(array.shape).encode("ascii"))
        digest.update(b"\0<f8\0")
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _record_digest(kind: str, *parts: object) -> str:
    digest = hashlib.sha256()
    digest.update(kind.encode("utf-8"))
    digest.update(b"\0")
    for part in parts:
        payload = part if isinstance(part, bytes) else str(part).encode("utf-8")
        digest.update(len(payload).to_bytes(8, byteorder="big", signed=False))
        digest.update(payload)
    return digest.hexdigest()


def _canonical_symmetric(value: np.ndarray) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    return 0.5 * (array + array.T)


def _nonzero_max(*arrays: np.ndarray) -> float:
    return float(max(np.max(np.abs(np.asarray(value))) for value in arrays))


def frozen_seed(width: int, depth: int, replicate: int) -> int:
    """The two predeclared Philox seeds for one frozen grid cell."""

    if width not in FROZEN_WIDTHS or depth not in FROZEN_DEPTHS:
        raise ValueError("M200 frozen grid is width 2..7 and depth 3..6")
    if replicate not in FROZEN_REPLICATES:
        raise ValueError("M200 has exactly two fixed seeds per grid cell")
    return 200_000_000 + 10_000 * width + 100 * depth + replicate


def generated_weights(width: int, depth: int, seed: int) -> tuple[np.ndarray, ...]:
    """Generated He-scale square weights; no benchmark model is involved."""

    rng = np.random.Generator(np.random.Philox(seed))
    scale = float(np.sqrt(2.0 / width))
    return tuple(
        np.array(rng.normal(scale=scale, size=(width, width)), dtype=np.float64)
        for _ in range(depth)
    )


def _weight_trace_digest(weights: Sequence[np.ndarray]) -> str:
    return _array_digest(
        *((f"weight_{index}", value) for index, value in enumerate(weights, start=1))
    )


def _network_digest(weight_trace_digest: str) -> str:
    return _record_digest("m200-generated-network-v1", weight_trace_digest)


@dataclass
class EventRecord:
    operation: str
    dtype: str
    shape: tuple[int, ...]
    logical_buffer_id: str
    digest: str
    birth_order: int
    death_order: int | None
    alias_class: str
    native_cost_status: str
    metadata: dict[str, Any] = field(default_factory=dict)


class EventLedger:
    """Explicit logical-buffer birth/death ledger for the M200 streaming path."""

    def __init__(self) -> None:
        self._clock = 0
        self.records: list[EventRecord] = []
        self._open: dict[str, EventRecord] = {}

    def birth(
        self,
        operation: str,
        value: np.ndarray,
        *,
        logical_buffer_id: str,
        alias_class: str,
        native_cost_status: str = "UNKNOWN_NOT_TARGET_METERED",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if logical_buffer_id in self._open:
            raise AssertionError(f"duplicate live logical buffer: {logical_buffer_id}")
        array = np.asarray(value)
        self._clock += 1
        record = EventRecord(
            operation=operation,
            dtype=str(array.dtype),
            shape=tuple(int(x) for x in array.shape),
            logical_buffer_id=logical_buffer_id,
            digest=_array_digest((logical_buffer_id, array)),
            birth_order=self._clock,
            death_order=None,
            alias_class=alias_class,
            native_cost_status=native_cost_status,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records.append(record)
        self._open[logical_buffer_id] = record
        return logical_buffer_id

    def marker(
        self,
        operation: str,
        *,
        logical_buffer_id: str,
        metadata: dict[str, Any] | None = None,
        native_cost_status: str = "UNKNOWN_NOT_TARGET_METERED",
    ) -> str:
        """Record a non-array semantic event as a scalar float64 logical buffer."""

        return self.birth(
            operation,
            np.zeros((), dtype=np.float64),
            logical_buffer_id=logical_buffer_id,
            alias_class="semantic_event_no_alias",
            native_cost_status=native_cost_status,
            metadata=metadata,
        )

    def release(self, logical_buffer_id: str) -> None:
        record = self._open.pop(logical_buffer_id, None)
        if record is None:
            raise AssertionError(f"release of absent/already-dead buffer: {logical_buffer_id}")
        self._clock += 1
        record.death_order = self._clock

    def release_many(self, buffer_ids: Iterable[str]) -> None:
        for buffer_id in buffer_ids:
            self.release(buffer_id)

    def assert_complete(self) -> None:
        if self._open:
            raise AssertionError(f"live buffers leaked: {sorted(self._open)}")
        for record in self.records:
            if record.death_order is None or record.death_order <= record.birth_order:
                raise AssertionError(f"bad event lifetime: {record.logical_buffer_id}")
            if record.dtype != "float64":
                raise AssertionError(f"non-float64 event: {record.logical_buffer_id}")
            if record.native_cost_status not in {
                "UNKNOWN_NOT_TARGET_METERED",
                "EXPLICIT_FIXTURE_PROVIDER_UNKNOWN",
            }:
                raise AssertionError("event omitted native-cost disposition")

    def jsonable(self) -> list[dict[str, Any]]:
        return [asdict(record) for record in self.records]


@dataclass(frozen=True)
class FixtureSpec:
    """Compact fixture description. It deliberately stores no dense rank-3 data."""

    network_seed: int
    layer: int

    @property
    def digest(self) -> str:
        return _record_digest("m200-fixture-spec-v1", self.network_seed, self.layer)


_LAYER_RECEIPTS: dict[str, tuple[object, ...]] = {}
_PACKET_RECEIPTS: dict[str, tuple[object, ...]] = {}


@dataclass(frozen=True)
class BoundArchiveLayer:
    """A live M179 output plus its exact upstream W_k/V_(k-1) causal inputs.

    The receipt is a cooperative integrity receipt, not an in-process security
    capability.  It specifically prevents accidental or ordinary wrapper-level
    laundering of a Source211 issued from a different ``W``/``Vprev``.
    """

    generation: int
    entry: m198.ExtendedBackgroundEntry
    upstream_mu: np.ndarray
    upstream_covariance: np.ndarray
    weight: np.ndarray
    receipt: str

    def __post_init__(self) -> None:
        if self.generation < 1 or self.entry.layer != self.generation:
            raise ValueError("bound layer generation/layer mismatch")
        record = _layer_record(
            self.generation,
            self.entry,
            self.upstream_mu,
            self.upstream_covariance,
            self.weight,
        )
        if _LAYER_RECEIPTS.get(self.receipt) != record:
            raise ValueError("unregistered or stale M200 bound-layer receipt")
        expected_a = np.asarray(self.upstream_mu, dtype=np.float64) @ self.weight
        expected_c = self.weight.T @ (np.asarray(self.upstream_covariance, dtype=np.float64) @ self.weight)
        expected_c = _canonical_symmetric(expected_c)
        if not np.array_equal(expected_a, self.entry.pre_mean):
            raise ValueError("bound layer a_k was not emitted from its W_k/mu_(k-1)")
        if not np.array_equal(expected_c, self.entry.pre_covariance):
            raise ValueError("bound layer C_k was not emitted from its W_k/V_(k-1)")

    @property
    def token(self) -> str:
        return _record_digest("m200-bound-layer-token-v1", self.receipt)


def _layer_record(
    generation: int,
    entry: m198.ExtendedBackgroundEntry,
    upstream_mu: np.ndarray,
    upstream_covariance: np.ndarray,
    weight: np.ndarray,
) -> tuple[object, ...]:
    return (
        int(generation),
        entry.provenance.digest,
        id(entry),
        id(upstream_mu),
        _array_digest(("upstream_mu", upstream_mu)),
        id(upstream_covariance),
        _array_digest(("upstream_covariance", upstream_covariance)),
        id(weight),
        _array_digest(("weight", weight)),
        id(entry.pre_mean),
        _array_digest(("pre_mean", entry.pre_mean)),
        id(entry.pre_covariance),
        _array_digest(("pre_covariance", entry.pre_covariance)),
        id(entry.mu),
        _array_digest(("post_mean", entry.mu)),
    )


def bind_archive_layer(
    entry: m198.ExtendedBackgroundEntry,
    upstream_mu: np.ndarray,
    upstream_covariance: np.ndarray,
    weight: np.ndarray,
    *,
    generation: int,
) -> BoundArchiveLayer:
    """Mint a monotonically generated causal binding after re-deriving a_k/C_k."""

    record = _layer_record(generation, entry, upstream_mu, upstream_covariance, weight)
    receipt = _record_digest("m200-bound-layer-receipt-v1", *record)
    _LAYER_RECEIPTS[receipt] = record
    return BoundArchiveLayer(
        generation=generation,
        entry=entry,
        upstream_mu=upstream_mu,
        upstream_covariance=upstream_covariance,
        weight=weight,
        receipt=receipt,
    )


@dataclass(frozen=True)
class SourcePacket:
    """One consumed M172-labelled Source211 fixture bound to one live M179 step."""

    spec: FixtureSpec
    source: m198.LabelledSource211
    layer: int
    network_digest: str
    weight_trace_digest: str
    weight_object: np.ndarray
    weight_object_id: int
    weight_digest: str
    input_covariance_object: np.ndarray
    input_covariance_object_id: int
    input_covariance_digest: str
    pre_mean_object: np.ndarray
    pre_mean_object_id: int
    pre_mean_digest: str
    pre_covariance_object: np.ndarray
    pre_covariance_object_id: int
    pre_covariance_digest: str
    post_mean_object: np.ndarray
    post_mean_object_id: int
    post_mean_digest: str
    bound_layer: BoundArchiveLayer
    issuance_receipt: str

    def __post_init__(self) -> None:
        if self.layer != self.spec.layer:
            raise ValueError("fixture layer/spec mismatch")
        if self.source.provenance.relu_layer != self.layer:
            raise ValueError("fixture source/context layer mismatch")
        if self.source.provenance.network_digest != self.network_digest:
            raise ValueError("fixture source/network mismatch")
        if self.source.provenance.weight_trace_digest != self.weight_trace_digest:
            raise ValueError("fixture source/weight-trace mismatch")
        if self.weight_object_id != id(self.weight_object):
            raise ValueError("fixture weight object identity was substituted")
        if self.input_covariance_object_id != id(self.input_covariance_object):
            raise ValueError("fixture covariance object identity was substituted")
        if self.weight_digest != _array_digest(("weight", self.weight_object)):
            raise ValueError("fixture weight digest was substituted")
        if self.input_covariance_digest != _array_digest(
            ("input_covariance", self.input_covariance_object)
        ):
            raise ValueError("fixture covariance digest was substituted")
        for name, value, object_id, digest in (
            ("pre-mean", self.pre_mean_object, self.pre_mean_object_id, self.pre_mean_digest),
            ("pre-covariance", self.pre_covariance_object, self.pre_covariance_object_id, self.pre_covariance_digest),
            ("post-mean", self.post_mean_object, self.post_mean_object_id, self.post_mean_digest),
        ):
            if object_id != id(value):
                raise ValueError(f"fixture {name} object identity was substituted")
            if digest != _array_digest(((name, value))):
                raise ValueError(f"fixture {name} digest was substituted")
        if _nonzero_max(
            self.source.slots.aaaa, self.source.slots.aaab, self.source.slots.aabb
        ) <= 0.0:
            raise ValueError("M200 fixture source must be nonzero")
        if self.bound_layer.entry is not self._entry_from_fields():
            raise ValueError("packet fields do not name its live bound archive layer")
        if self.bound_layer.generation != self.layer:
            raise ValueError("packet/bound-layer generation mismatch")
        record = _packet_record(self.bound_layer, self.source, self.spec)
        if _PACKET_RECEIPTS.get(self.issuance_receipt) != record:
            raise ValueError("unregistered or stale integrated M200 source issuance")

    def _entry_from_fields(self) -> m198.ExtendedBackgroundEntry:
        """Return the exact bound entry only when every stored field names it."""

        entry = self.bound_layer.entry
        if not (
            self.weight_object is self.bound_layer.weight
            and self.input_covariance_object is self.bound_layer.upstream_covariance
            and self.pre_mean_object is entry.pre_mean
            and self.pre_covariance_object is entry.pre_covariance
            and self.post_mean_object is entry.mu
        ):
            raise ValueError("packet field/object identity differs from bound layer")
        return entry

    @property
    def packet_id(self) -> str:
        return _record_digest(
            "m200-source-packet-v1",
            self.spec.digest,
            self.source.source_id,
            self.weight_digest,
            self.input_covariance_digest,
        )

    @property
    def binding_token(self) -> str:
        """M200 layer token: W_k, V_(k-1), a_k, C_k, mu_k, and k are all bound."""

        return _record_digest(
            "m200-layer-bound-packet-v1",
            self.bound_layer.token,
            self.source.source_id,
            self.issuance_receipt,
        )


def _packet_record(
    bound_layer: BoundArchiveLayer,
    source: m198.LabelledSource211,
    spec: FixtureSpec,
) -> tuple[object, ...]:
    return (
        bound_layer.receipt,
        spec.digest,
        source.source_id,
        source.slots.digest,
        source.provenance.digest,
    )


def _fixture_rng(spec: FixtureSpec) -> np.random.Generator:
    seed = int(spec.network_seed) * 8191 + int(spec.layer) * 131 + 17
    return np.random.Generator(np.random.Philox(seed))


def _fixture_source(
    entry: m198.ExtendedBackgroundEntry,
    weight: np.ndarray,
    input_covariance: np.ndarray,
    spec: FixtureSpec,
) -> m198.LabelledSource211:
    """Build a generated M172 source, retaining only its compact Source211 slots.

    ``distinct`` and owner arrays are ephemeral construction scratch.  They are
    intentionally not returned or captured by a packet/liveness object.
    """

    n = int(entry.mu.size)
    rng = _fixture_rng(spec)
    distinct = rng.normal(scale=0.025, size=(n, n, n))
    distinct = 0.5 * (distinct + distinct.swapaxes(1, 2))
    k4 = rng.normal(scale=0.020, size=n)
    k31 = rng.normal(scale=0.020, size=(n, n))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(scale=0.020, size=(n, n))
    k22 = _canonical_symmetric(k22)
    np.fill_diagonal(k22, 0.0)
    owners = PhysicalFourthOwners(k4, k31, k22)
    source = m198.issue_m172_source(
        provenance=entry.provenance,
        weight=weight,
        distinct_211=distinct,
        owners=owners,
        covariance=input_covariance,
    )
    # An explicit compactness invariant: no third-order table survives this
    # factory boundary. `Source211Slots` carries O(n^2), not O(n^3), storage.
    if source.slots.aaab.ndim != 2 or source.slots.aabb.ndim != 2:
        raise AssertionError("M200 fixture accidentally retained a dense rank-3 source")
    return source


def fixture_source_bound_to(
    bound_layer: BoundArchiveLayer,
    spec: FixtureSpec,
) -> SourcePacket:
    """Integrated issuer for a nonzero, provider-unknown M172 fixture packet.

    There is intentionally no API that accepts an externally issued source:
    that would allow an ordinary ``W/Vprev`` laundering mistake to be wrapped
    in the current layer labels.  The M172 source is minted here from the live
    bound M179 layer and a receipt records all causal identity/digest inputs.
    """

    entry = bound_layer.entry
    weight = bound_layer.weight
    input_covariance = bound_layer.upstream_covariance
    source = _fixture_source(entry, weight, input_covariance, spec)
    record = _packet_record(bound_layer, source, spec)
    issuance_receipt = _record_digest("m200-integrated-source-issuance-v1", *record)
    _PACKET_RECEIPTS[issuance_receipt] = record
    return SourcePacket(
        spec=spec,
        source=source,
        layer=entry.layer,
        network_digest=entry.provenance.network_digest,
        weight_trace_digest=entry.provenance.weight_trace_digest,
        weight_object=weight,
        weight_object_id=id(weight),
        weight_digest=_array_digest(("weight", weight)),
        input_covariance_object=input_covariance,
        input_covariance_object_id=id(input_covariance),
        input_covariance_digest=_array_digest(("input_covariance", input_covariance)),
        pre_mean_object=entry.pre_mean,
        pre_mean_object_id=id(entry.pre_mean),
        pre_mean_digest=_array_digest((("pre-mean", entry.pre_mean))),
        pre_covariance_object=entry.pre_covariance,
        pre_covariance_object_id=id(entry.pre_covariance),
        pre_covariance_digest=_array_digest((("pre-covariance", entry.pre_covariance))),
        post_mean_object=entry.mu,
        post_mean_object_id=id(entry.mu),
        post_mean_digest=_array_digest((("post-mean", entry.mu))),
        bound_layer=bound_layer,
        issuance_receipt=issuance_receipt,
    )


def validate_packet_binding(
    packet: SourcePacket,
    bound_layer: BoundArchiveLayer,
    *,
    consumed_packet_ids: set[str] | None = None,
    terminal_sealed: bool = False,
) -> None:
    """Fail closed on every M200 packet substitution/reorder/reinjection class."""

    if terminal_sealed:
        raise ValueError("terminal record sealed: Source211 terminal reinjection refused")
    entry = bound_layer.entry
    weight = bound_layer.weight
    input_covariance = bound_layer.upstream_covariance
    if packet.bound_layer is not bound_layer:
        raise ValueError("packet did not originate from the live bound layer object")
    if packet.layer != entry.layer or packet.spec.layer != entry.layer:
        raise ValueError("cross-layer packet substitution or reorder refused")
    if packet.source.provenance != entry.provenance:
        raise ValueError("packet/source context does not equal the current M179 layer")
    if packet.network_digest != entry.provenance.network_digest:
        raise ValueError("packet/network substitution refused")
    if packet.weight_trace_digest != entry.provenance.weight_trace_digest:
        raise ValueError("packet/weight-trace substitution refused")
    if packet.weight_object is not weight or packet.weight_object_id != id(weight):
        raise ValueError("packet weight-object substitution refused")
    if packet.weight_digest != _array_digest(("weight", weight)):
        raise ValueError("packet weight digest substitution refused")
    if (
        packet.input_covariance_object is not input_covariance
        or packet.input_covariance_object_id != id(input_covariance)
    ):
        raise ValueError("packet input-covariance object substitution refused")
    if packet.input_covariance_digest != _array_digest(
        ("input_covariance", input_covariance)
    ):
        raise ValueError("packet input-covariance digest substitution refused")
    for name, packet_value, packet_id, packet_digest, entry_value in (
        ("pre-mean", packet.pre_mean_object, packet.pre_mean_object_id, packet.pre_mean_digest, entry.pre_mean),
        ("pre-covariance", packet.pre_covariance_object, packet.pre_covariance_object_id, packet.pre_covariance_digest, entry.pre_covariance),
        ("post-mean", packet.post_mean_object, packet.post_mean_object_id, packet.post_mean_digest, entry.mu),
    ):
        if packet_value is not entry_value or packet_id != id(entry_value):
            raise ValueError(f"packet {name} object substitution refused")
        if packet_digest != _array_digest(((name, entry_value))):
            raise ValueError(f"packet {name} digest substitution refused")
    expected_token = _record_digest(
        "m200-layer-bound-packet-v1",
        bound_layer.token,
        packet.source.source_id,
        packet.issuance_receipt,
    )
    if packet.binding_token != expected_token:
        raise ValueError("layer-bound packet token mismatch")
    if consumed_packet_ids is not None and packet.packet_id in consumed_packet_ids:
        raise ValueError("duplicate Source211 packet/reinjection refused")


@dataclass
class StreamInjectionGuard:
    """One-way packet consumer used by the streamed recurrence and its negative tests."""

    consumed_packet_ids: set[str] = field(default_factory=set)
    terminal_sealed: bool = False

    def consume(
        self,
        packet: SourcePacket,
        bound_layer: BoundArchiveLayer,
    ) -> None:
        validate_packet_binding(
            packet,
            bound_layer,
            consumed_packet_ids=self.consumed_packet_ids,
            terminal_sealed=self.terminal_sealed,
        )
        self.consumed_packet_ids.add(packet.packet_id)

    def seal_terminal(self) -> None:
        if self.terminal_sealed:
            raise ValueError("terminal record already sealed")
        self.terminal_sealed = True


@dataclass(frozen=True)
class LivenessAudit:
    """Structural, not RSS-based, audit of retained state at stream completion."""

    retained_previous_background: int
    retained_current_background: int
    retained_tangent: int
    retained_fixture_packet: int
    retained_scratch: int
    retained_full_archive: int
    retained_dense_rank3: int
    retained_suffix_states: int
    max_live_named_objects: int

    def assert_gate(self) -> None:
        if (
            self.retained_full_archive != 0
            or self.retained_dense_rank3 != 0
            or self.retained_suffix_states != 0
        ):
            raise AssertionError("M200 retained forbidden archive/rank3/suffix state")
        if any(
            value != 0
            for value in (
                self.retained_previous_background,
                self.retained_current_background,
                self.retained_tangent,
                self.retained_fixture_packet,
                self.retained_scratch,
            )
        ):
            raise AssertionError("M200 failed to release stream-local live state")
        if self.max_live_named_objects > 5:
            raise AssertionError("M200 live set exceeded previous/current/tangent/packet/scratch")


@dataclass(frozen=True)
class StreamingResult:
    source_terminal_state: TangentState
    terminal_state: TangentState
    network_digest: str
    weight_trace_digest: str
    background_steps: int
    source_packets: int
    conversions: int
    injections: int
    transports: int
    terminal_responses: int
    background_rebuilds_inside_stream: int
    event_ledger: tuple[EventRecord, ...]
    liveness: LivenessAudit
    transport_jacobian_identity_pass: bool
    conversion_copy_integrity_pass: bool

    transport_call_log: tuple[tuple[int, int, int], ...]

    def assert_semantic_gates(self, source_relu_layers_h: int) -> None:
        if (
            self.background_steps,
            self.source_packets,
            self.conversions,
            self.injections,
            self.transports,
            self.terminal_responses,
            self.background_rebuilds_inside_stream,
        ) != (
            source_relu_layers_h,
            source_relu_layers_h,
            source_relu_layers_h,
            source_relu_layers_h,
            source_relu_layers_h - 1,
            1,
            0,
        ):
            raise AssertionError("M200 frozen streaming operation count gate failed")
        if not self.transport_jacobian_identity_pass:
            raise AssertionError("M125b did not receive M179's exact Jacobian object")
        if not self.conversion_copy_integrity_pass:
            raise AssertionError("M198 did not receive exact-copy M179 a/C/mu arrays")
        self.liveness.assert_gate()


def _m179_stream_step(
    previous_mu: np.ndarray,
    previous_covariance: np.ndarray,
    weight: np.ndarray,
    *,
    layer: int,
    network_digest: str,
    weight_trace_digest: str,
) -> m198.ExtendedBackgroundEntry:
    """One M179 update emitted as an M198-compatible *current* layer only."""

    pre_mean = previous_mu @ weight
    pre_covariance = weight.T @ (previous_covariance @ weight)
    pre_covariance = _canonical_symmetric(pre_covariance)
    provenance = m198._issue_context_provenance(  # integrity convention from M198
        pre_mean,
        pre_covariance,
        network_digest=network_digest,
        weight_trace_digest=weight_trace_digest,
        relu_layer=layer,
        producer_epoch=FIXTURE_EPOCH,
        cast_provenance="generated-f64 (M200 response-free streaming fixture)",
        issuer_family="m179_background_archive",
    )
    jacobian, jacobian_mean, strata = m179_archive.build_jacobian(
        pre_mean, pre_covariance
    )
    state = m179_producer.relu_moments(pre_mean, pre_covariance)
    if float(np.max(np.abs(jacobian_mean - state.mu))) > 2.0e-12:
        raise AssertionError("M179 Jacobian/producer mean disagreement")
    return m198.ExtendedBackgroundEntry(
        provenance=provenance,
        pre_mean=pre_mean,
        pre_covariance=pre_covariance,
        mu=state.mu,
        V=state.V,
        jacobian=jacobian,
        strata=strata,
    )


def _record_entry_births(
    ledger: EventLedger, entry: m198.ExtendedBackgroundEntry, layer: int
) -> tuple[str, str, str, str, tuple[str, ...]]:
    prefix = f"l{layer}"
    core = (
        ledger.birth(
            "m179.exact_step.pre_mean",
            entry.pre_mean,
            logical_buffer_id=f"{prefix}.pre_mean",
            alias_class="fresh_m179_output",
        ),
        ledger.birth(
            "m179.exact_step.pre_covariance",
            entry.pre_covariance,
            logical_buffer_id=f"{prefix}.pre_covariance",
            alias_class="fresh_m179_output",
        ),
        ledger.birth(
            "m179.exact_step.post_mean",
            entry.mu,
            logical_buffer_id=f"{prefix}.post_mean",
            alias_class="frozen_copy_of_m179_output",
        ),
        ledger.birth(
            "m179.exact_step.post_covariance",
            entry.V,
            logical_buffer_id=f"{prefix}.post_covariance",
            alias_class="frozen_copy_of_m179_output",
        ),
    )
    jacobian_ids = (
        ledger.birth(
            "m179.exact_step.jacobian.probability", entry.jacobian.probability,
            logical_buffer_id=f"{prefix}.jacobian_probability",
            alias_class="frozen_m179_jacobian_component",
        ),
        ledger.birth(
            "m179.exact_step.jacobian.mean_variance_derivative", entry.jacobian.mean_variance_derivative,
            logical_buffer_id=f"{prefix}.jacobian_mean_variance_derivative",
            alias_class="frozen_m179_jacobian_component",
        ),
        ledger.birth(
            "m179.exact_step.jacobian.price_kernel", entry.jacobian.price_kernel,
            logical_buffer_id=f"{prefix}.jacobian_price_kernel",
            alias_class="frozen_m179_jacobian_component",
        ),
        ledger.birth(
            "m179.exact_step.jacobian.h_mu", entry.jacobian.h_mu,
            logical_buffer_id=f"{prefix}.jacobian_h_mu",
            alias_class="frozen_m179_jacobian_component",
        ),
        ledger.birth(
            "m179.exact_step.jacobian.h_variance", entry.jacobian.h_variance,
            logical_buffer_id=f"{prefix}.jacobian_h_variance",
            alias_class="frozen_m179_jacobian_component",
        ),
    )
    return (*core, jacobian_ids)


def run_streaming_overlap(
    weights: Sequence[np.ndarray],
    *,
    network_seed: int,
) -> StreamingResult:
    """The M200 measured stream. It never calls ``build_extended_background``.

    The phrase “measured stream” means this path is isolated from the full
    archive reference.  Native cost is *not* measured by a target meter here.
    """

    matrices = tuple(weights)
    if len(matrices) < 4:
        raise ValueError("M200 requires H>=3 source layers plus a terminal matrix")
    if any(not isinstance(matrix, np.ndarray) or matrix.dtype != np.float64 for matrix in matrices):
        raise ValueError("M200 is float64-only; implicit casts are forbidden")
    n = matrices[0].shape[0]
    if n < 2 or any(matrix.shape != (n, n) for matrix in matrices):
        raise ValueError("M200 requires constant-width square generated weights")
    source_relu_layers_h = len(matrices) - 1
    source_weights = matrices[:source_relu_layers_h]
    terminal_weight = matrices[-1]

    trace_digest = _weight_trace_digest(matrices)
    network = _network_digest(trace_digest)
    ledger = EventLedger()
    guard = StreamInjectionGuard()
    previous_mu = np.zeros(n, dtype=np.float64)
    previous_covariance = np.eye(n, dtype=np.float64)
    previous_mu_buffer = ledger.birth(
        "m200.initial_background.mean", previous_mu,
        logical_buffer_id="l0.post_mean", alias_class="initial_live_background",
    )
    previous_covariance_buffer = ledger.birth(
        "m200.initial_background.covariance", previous_covariance,
        logical_buffer_id="l0.post_covariance", alias_class="initial_live_background",
    )
    accumulated: TangentState | None = None
    tangent_buffers: tuple[str, str] | None = None
    max_live_named_objects = 0
    counts = {
        "background_steps": 0,
        "source_packets": 0,
        "conversions": 0,
        "injections": 0,
        "transports": 0,
        "terminal_responses": 0,
        "background_rebuilds_inside_stream": 0,
    }
    transport_jacobian_identity_pass = True
    conversion_copy_integrity_pass = True
    transport_call_log: list[tuple[int, int, int]] = []

    for index, weight in enumerate(source_weights, start=1):
        weight_buffer = ledger.birth(
            "m200.borrowed_weight_w_k", weight,
            logical_buffer_id=f"l{index}.borrowed_weight",
            alias_class="borrowed_exact_weight_object",
            metadata={"weight_object_id": id(weight), "generation": index},
        )
        # Exactly one M179 state is born. There is no archive list in this path.
        entry = _m179_stream_step(
            previous_mu,
            previous_covariance,
            weight,
            layer=index,
            network_digest=network,
            weight_trace_digest=trace_digest,
        )
        counts["background_steps"] += 1
        pre_mean_buffer, pre_covariance_buffer, post_mean_buffer, post_covariance_buffer, jacobian_buffers = _record_entry_births(ledger, entry, index)
        bound_layer = bind_archive_layer(
            entry,
            previous_mu,
            previous_covariance,
            weight,
            generation=index,
        )

        # The current input covariance is the exact live object consumed by this
        # layer. It is intentionally not copied for the packet binding contract.
        input_covariance = previous_covariance
        max_live_named_objects = max(max_live_named_objects, 2 + int(accumulated is not None))

        transport_buffers: tuple[str, str] | None = None
        if accumulated is not None:
            # The transport consumes *this* entry's emitted LocalReluJacobian.
            supplied_weight = bound_layer.weight
            supplied_jacobian = bound_layer.entry.jacobian
            transport_jacobian_identity_pass &= (
                supplied_weight is weight and supplied_jacobian is entry.jacobian
            )
            transport_call_log.append((id(supplied_weight), id(supplied_jacobian), index))
            transported = tangent_stage(accumulated, supplied_weight, supplied_jacobian)
            transport_mean_buffer = ledger.birth(
                "m125b.transport.current_m179_jacobian",
                transported.mean,
                logical_buffer_id=f"l{index}.transport_mean",
                alias_class="fresh_transport_output",
                metadata={
                    "jacobian_object_id": id(entry.jacobian),
                    "emitting_layer": entry.layer,
                    "weight_object_id": id(weight),
                },
            )
            transport_covariance_buffer = ledger.birth(
                "m125b.transport.current_m179_jacobian",
                transported.covariance,
                logical_buffer_id=f"l{index}.transport_covariance",
                alias_class="fresh_transport_output",
                metadata={
                    "jacobian_object_id": id(entry.jacobian),
                    "emitting_layer": entry.layer,
                    "weight_object_id": id(weight),
                },
            )
            counts["transports"] += 1
            accumulated = transported
            transport_buffers = (transport_mean_buffer, transport_covariance_buffer)

        spec = FixtureSpec(network_seed=network_seed, layer=index)
        packet = fixture_source_bound_to(bound_layer, spec)
        max_live_named_objects = max(max_live_named_objects, 4 + int(accumulated is not None))
        packet_mean_id = ledger.birth(
            "fixture_source_bound_to",
            packet.source.slots.aaaa,
            logical_buffer_id=f"l{index}.fixture_aaaa",
            alias_class="compact_owned_source_slots",
            native_cost_status="EXPLICIT_FIXTURE_PROVIDER_UNKNOWN",
            metadata={
                "packet_id": packet.packet_id,
                "weight_object_id": id(weight),
                "input_covariance_object_id": id(input_covariance),
                "no_dense_rank3_retained": True,
            },
        )
        packet_aaab_id = ledger.birth(
            "fixture_source_bound_to",
            packet.source.slots.aaab,
            logical_buffer_id=f"l{index}.fixture_aaab",
            alias_class="compact_owned_source_slots",
            native_cost_status="EXPLICIT_FIXTURE_PROVIDER_UNKNOWN",
            metadata={"packet_id": packet.packet_id, "no_dense_rank3_retained": True},
        )
        packet_aabb_id = ledger.birth(
            "fixture_source_bound_to",
            packet.source.slots.aabb,
            logical_buffer_id=f"l{index}.fixture_aabb",
            alias_class="compact_owned_source_slots",
            native_cost_status="EXPLICIT_FIXTURE_PROVIDER_UNKNOWN",
            metadata={"packet_id": packet.packet_id, "no_dense_rank3_retained": True},
        )
        counts["source_packets"] += 1

        guard.consume(packet, bound_layer)
        context = entry.delay_one_context
        # M198 constructs its own frozen copies. Value/digest equality and strict
        # non-aliasing are both required; aliases would be a ledger violation.
        conversion_copy_integrity_pass &= (
            context.provenance == entry.provenance
            and np.array_equal(context.pre_mean, entry.pre_mean)
            and np.array_equal(context.pre_covariance, entry.pre_covariance)
            and np.array_equal(context.post_mean, entry.mu)
            and context.pre_mean is not entry.pre_mean
            and context.pre_covariance is not entry.pre_covariance
            and context.post_mean is not entry.mu
        )
        context_buffers = (
            ledger.birth(
                "m198.context_copy.pre_mean", context.pre_mean,
                logical_buffer_id=f"l{index}.context_pre_mean",
                alias_class="explicit_immutable_copy_of_m179_pre_mean",
                metadata={"parent_object_id": id(entry.pre_mean), "child_object_id": id(context.pre_mean)},
            ),
            ledger.birth(
                "m198.context_copy.pre_covariance", context.pre_covariance,
                logical_buffer_id=f"l{index}.context_pre_covariance",
                alias_class="explicit_immutable_copy_of_m179_pre_covariance",
                metadata={"parent_object_id": id(entry.pre_covariance), "child_object_id": id(context.pre_covariance)},
            ),
            ledger.birth(
                "m198.context_copy.post_mean", context.post_mean,
                logical_buffer_id=f"l{index}.context_post_mean",
                alias_class="explicit_immutable_copy_of_m179_post_mean",
                metadata={"parent_object_id": id(entry.mu), "child_object_id": id(context.post_mean)},
            ),
        )
        injected = m198.source211_delay_one(packet.source, context)
        counts["conversions"] += 1
        injected_mean_id = ledger.birth(
            "m198.delay_one.convert_exact_m179_context_copy",
            injected.state.mean,
            logical_buffer_id=f"l{index}.injected_mean",
            alias_class="fresh_m198_conversion_output",
            native_cost_status="EXPLICIT_FIXTURE_PROVIDER_UNKNOWN",
            metadata={
                "entry_pre_mean_object_id": id(entry.pre_mean),
                "context_pre_mean_object_id": id(context.pre_mean),
                "entry_pre_covariance_object_id": id(entry.pre_covariance),
                "context_pre_covariance_object_id": id(context.pre_covariance),
                "entry_post_mean_object_id": id(entry.mu),
                "context_post_mean_object_id": id(context.post_mean),
                "copy_not_alias": True,
            },
        )
        injected_cov_id = ledger.birth(
            "m198.delay_one.convert_exact_m179_context_copy",
            injected.state.covariance,
            logical_buffer_id=f"l{index}.injected_covariance",
            alias_class="fresh_m198_conversion_output",
            native_cost_status="EXPLICIT_FIXTURE_PROVIDER_UNKNOWN",
            metadata={"source_id": injected.source_id, "copy_not_alias": True},
        )
        if accumulated is None:
            accumulated = TangentState(injected.state.mean.copy(), injected.state.covariance.copy())
        else:
            accumulated = TangentState(
                accumulated.mean + injected.state.mean,
                accumulated.covariance + injected.state.covariance,
            )
        accumulator_buffers = (
            ledger.birth(
                "m125b.accumulator_after_source_injection", accumulated.mean,
                logical_buffer_id=f"l{index}.accumulator_mean",
                alias_class="fresh_stream_accumulator",
            ),
            ledger.birth(
                "m125b.accumulator_after_source_injection", accumulated.covariance,
                logical_buffer_id=f"l{index}.accumulator_covariance",
                alias_class="fresh_stream_accumulator",
            ),
        )
        counts["injections"] += 1
        if tangent_buffers is not None:
            ledger.release_many(tangent_buffers)
        ledger.release_many(
            (
                injected_mean_id,
                injected_cov_id,
                packet_mean_id,
                packet_aaab_id,
                packet_aabb_id,
                *context_buffers,
                pre_mean_buffer,
                pre_covariance_buffer,
                *jacobian_buffers,
                weight_buffer,
                previous_mu_buffer,
                previous_covariance_buffer,
                *(transport_buffers or ()),
            )
        )
        # Only scalar references survive between iterations: current output becomes
        # the next input, and the current entry replaces the previous entry.
        previous_mu = entry.mu
        previous_covariance = entry.V
        previous_mu_buffer = post_mean_buffer
        previous_covariance_buffer = post_covariance_buffer
        tangent_buffers = accumulator_buffers
        del packet, context, injected, bound_layer

    if accumulated is None:
        raise AssertionError("M200 produced no terminal tangent")
    guard.seal_terminal()
    terminal_weight_buffer = ledger.birth(
        "m200.borrowed_terminal_weight_w_h_plus_1", terminal_weight,
        logical_buffer_id="terminal.borrowed_weight",
        alias_class="borrowed_exact_weight_object",
        metadata={"weight_object_id": id(terminal_weight), "source_injection": False},
    )
    terminal_entry = _m179_stream_step(
        previous_mu,
        previous_covariance,
        terminal_weight,
        layer=source_relu_layers_h + 1,
        network_digest=network,
        weight_trace_digest=trace_digest,
    )
    terminal_bound = bind_archive_layer(
        terminal_entry,
        previous_mu,
        previous_covariance,
        terminal_weight,
        generation=source_relu_layers_h + 1,
    )
    terminal_buffers = _record_entry_births(ledger, terminal_entry, source_relu_layers_h + 1)
    # The final W_(H+1),J_(H+1) stage is a response only: no Source211 packet
    # exists at this layer.
    terminal_supplied_weight = terminal_bound.weight
    terminal_supplied_jacobian = terminal_bound.entry.jacobian
    transport_jacobian_identity_pass &= (
        terminal_supplied_weight is terminal_weight
        and terminal_supplied_jacobian is terminal_entry.jacobian
    )
    terminal_state = tangent_stage(accumulated, terminal_supplied_weight, terminal_supplied_jacobian)
    terminal_mean_id = ledger.birth(
        "m200.terminal_w_h_plus_1_response",
        terminal_state.mean,
        logical_buffer_id="terminal.response_mean",
        alias_class="fresh_terminal_response",
        metadata={
            "weight_object_id": id(terminal_bound.weight),
            "jacobian_object_id": id(terminal_bound.entry.jacobian),
            "source_injection": False,
        },
    )
    terminal_cov_id = ledger.birth(
        "m200.terminal_w_h_plus_1_response",
        terminal_state.covariance,
        logical_buffer_id="terminal.response_covariance",
        alias_class="fresh_terminal_response",
        metadata={"source_injection": False},
    )
    counts["terminal_responses"] += 1
    ledger.release_many(
        (
            *terminal_buffers[:4],
            *terminal_buffers[4],
            terminal_weight_buffer,
            terminal_mean_id,
            terminal_cov_id,
            previous_mu_buffer,
            previous_covariance_buffer,
            *(tangent_buffers or ()),
        )
    )
    ledger.assert_complete()

    result = StreamingResult(
        source_terminal_state=accumulated,
        terminal_state=terminal_state,
        network_digest=network,
        weight_trace_digest=trace_digest,
        event_ledger=tuple(ledger.records),
        liveness=LivenessAudit(
            retained_previous_background=0,
            retained_current_background=0,
            retained_tangent=0,
            retained_fixture_packet=0,
            retained_scratch=0,
            retained_full_archive=0,
            retained_dense_rank3=0,
            retained_suffix_states=0,
            max_live_named_objects=max_live_named_objects,
        ),
        transport_jacobian_identity_pass=transport_jacobian_identity_pass,
        conversion_copy_integrity_pass=conversion_copy_integrity_pass,
        transport_call_log=tuple(transport_call_log),
        **counts,
    )
    result.assert_semantic_gates(source_relu_layers_h)
    return result


@dataclass(frozen=True)
class FullArchiveReference:
    source_terminal_state: TangentState
    terminal_state: TangentState
    per_layer_impulse_max_abs: float


def full_archive_reference(
    weights: Sequence[np.ndarray],
    *,
    network_seed: int,
) -> FullArchiveReference:
    """Slow explicit M125b superposition, isolated from ``run_streaming_overlap``."""

    matrices = tuple(weights)
    if len(matrices) < 4 or any(
        not isinstance(matrix, np.ndarray) or matrix.dtype != np.float64
        for matrix in matrices
    ):
        raise ValueError("M200 reference is float64-only with H>=3 plus terminal")
    source_relu_layers_h = len(matrices) - 1
    source_weights = matrices[:source_relu_layers_h]
    terminal_weight = matrices[-1]
    trace_digest = _weight_trace_digest(matrices)
    network = _network_digest(trace_digest)
    # This list is the *separate reference archive*, never retained or created
    # by run_streaming_overlap.
    entries: list[m198.ExtendedBackgroundEntry] = []
    sources = []
    previous_mu = np.zeros(matrices[0].shape[0], dtype=np.float64)
    previous_covariance = np.eye(matrices[0].shape[0], dtype=np.float64)
    for index, weight in enumerate(source_weights, start=1):
        entry = _m179_stream_step(
            previous_mu, previous_covariance, weight, layer=index,
            network_digest=network, weight_trace_digest=trace_digest,
        )
        bound = bind_archive_layer(
            entry, previous_mu, previous_covariance, weight, generation=index
        )
        entries.append(entry)
        packet = fixture_source_bound_to(bound, FixtureSpec(network_seed=network_seed, layer=index))
        sources.append(m198.source211_delay_one(packet.source, entry.delay_one_context))
        previous_mu = entry.mu
        previous_covariance = entry.V
    terminal_entry = _m179_stream_step(
        previous_mu, previous_covariance, terminal_weight,
        layer=source_relu_layers_h + 1,
        network_digest=network, weight_trace_digest=trace_digest,
    )
    # Manual full-archive explicit suffix reference. There are H sources and H
    # maps when the unsourced terminal map W_(H+1),J_(H+1) is included, so we
    # must not fabricate a terminal source to force it through M198's H-1-map
    # carrier helper.
    source_terminal_mean = np.zeros_like(sources[0].state.mean)
    source_terminal_covariance = np.zeros_like(sources[0].state.covariance)
    terminal_mean = np.zeros_like(sources[0].state.mean)
    terminal_covariance = np.zeros_like(sources[0].state.covariance)
    impulse_max = 0.0
    for source_index, source in enumerate(sources):
        explicit = source.state
        for next_index in range(source_index + 1, source_relu_layers_h):
            explicit = tangent_stage(
                explicit, source_weights[next_index], entries[next_index].jacobian
            )
        source_terminal_mean += explicit.mean
        source_terminal_covariance += explicit.covariance
        terminal_impulse = tangent_stage(explicit, terminal_weight, terminal_entry.jacobian)
        terminal_mean += terminal_impulse.mean
        terminal_covariance += terminal_impulse.covariance
        # Independently reconstruct the same one-source path by consuming its
        # concrete archive entries, rather than a labelled carrier-map helper.
        recurrence = source.state
        for next_index in range(source_index + 1, source_relu_layers_h):
            current_entry = entries[next_index]
            recurrence = tangent_stage(
                recurrence, source_weights[next_index], current_entry.jacobian
            )
        recurrence = tangent_stage(recurrence, terminal_weight, terminal_entry.jacobian)
        impulse_max = max(
            impulse_max,
            float(np.max(np.abs(terminal_impulse.mean - recurrence.mean))),
            float(np.max(np.abs(terminal_impulse.covariance - recurrence.covariance))),
        )
    if impulse_max > PARITY_MAX_ABS:
        raise AssertionError("M200 per-layer impulse parity failed")
    return FullArchiveReference(
        TangentState(source_terminal_mean, source_terminal_covariance),
        TangentState(terminal_mean, terminal_covariance),
        impulse_max,
    )


@dataclass(frozen=True)
class ScreenCaseResult:
    width: int
    depth: int
    replicate: int
    seed: int
    max_abs_error: float
    per_layer_impulse_max_abs: float
    stream_counts: dict[str, int]
    event_count: int
    liveness: LivenessAudit

    def jsonable(self) -> dict[str, Any]:
        value = asdict(self)
        value["liveness"] = asdict(self.liveness)
        return value


def run_screen_case(width: int, depth: int, replicate: int) -> ScreenCaseResult:
    """One frozen M200 case: stream first, construct archive reference second."""

    seed = frozen_seed(width, depth, replicate)
    weights = generated_weights(width, depth + 1, seed)
    streamed = run_streaming_overlap(weights, network_seed=seed)
    reference = full_archive_reference(weights, network_seed=seed)
    max_abs_error = max(
        float(np.max(np.abs(streamed.source_terminal_state.mean - reference.source_terminal_state.mean))),
        float(np.max(np.abs(streamed.source_terminal_state.covariance - reference.source_terminal_state.covariance))),
        float(np.max(np.abs(streamed.terminal_state.mean - reference.terminal_state.mean))),
        float(np.max(np.abs(streamed.terminal_state.covariance - reference.terminal_state.covariance))),
    )
    if max_abs_error > PARITY_MAX_ABS:
        raise AssertionError(
            f"M200 stream/reference parity {max_abs_error:.3e} exceeds {PARITY_MAX_ABS:.3e}"
        )
    return ScreenCaseResult(
        width=width,
        depth=depth,
        replicate=replicate,
        seed=seed,
        max_abs_error=max_abs_error,
        per_layer_impulse_max_abs=reference.per_layer_impulse_max_abs,
        stream_counts={
            "background_steps": streamed.background_steps,
            "source_packets": streamed.source_packets,
            "conversions": streamed.conversions,
            "injections": streamed.injections,
            "transports": streamed.transports,
            "terminal_responses": streamed.terminal_responses,
            "background_rebuilds_inside_stream": streamed.background_rebuilds_inside_stream,
        },
        event_count=len(streamed.event_ledger),
        liveness=streamed.liveness,
    )


def run_frozen_screen() -> list[ScreenCaseResult]:
    """Execute the predeclared 6 x 4 x 2 generated-only screen once."""

    return [
        run_screen_case(width, depth, replicate)
        for width in FROZEN_WIDTHS
        for depth in FROZEN_DEPTHS
        for replicate in FROZEN_REPLICATES
    ]


def results_payload(cases: Sequence[ScreenCaseResult]) -> dict[str, Any]:
    if len(cases) != len(FROZEN_WIDTHS) * len(FROZEN_DEPTHS) * len(FROZEN_REPLICATES):
        raise ValueError("M200 results must cover the entire frozen screen")
    return {
        "candidate": "M200 streaming M179 -> M198 -> M125b overlap fixture",
        "status": "STREAMING_SEMANTIC_PASS_NATIVE_COST_BLOCKED",
        "scope": "generated-only response-free ABI/liveness fixture",
        "parity_max_abs_threshold": PARITY_MAX_ABS,
        "max_abs_error": max(case.max_abs_error for case in cases),
        "case_count": len(cases),
        "fixture_provider_cost": "UNKNOWN",
        "m198_native_cost": "UNKNOWN",
        "native_target_cost": "NOT_MEASURED",
        "no_claims": [
            "physical Source211 provider",
            "target cost or overlap replacement",
            "variance, MSE, score, promotion, or winning-entry result",
        ],
        "cases": [case.jsonable() for case in cases],
    }


def write_results(path: Path, cases: Sequence[ScreenCaseResult]) -> None:
    path.write_text(json.dumps(results_payload(cases), indent=2) + "\n", encoding="utf-8")
