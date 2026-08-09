"""M198 generated-only Source211 -> delay-one TangentState semantics.

This module is a response-free algebra component.  It does not construct a
physical Source211 coefficient, run a benchmark network, or claim native cost.
The G0 ABI is deliberately fail-closed: arrays are copied/read-only, a source
is bound to one exact pre-ReLU context, ownership conservation is explicit,
and source labels survive the M125b carrier.  Its in-process SHA-256 receipt
registries are cooperative integrity checks, not signatures, capabilities, or
a hostile-code authority boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import math
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for directory in (
    EXPERIMENTS / "m125_source_batched_forward_tangent",
    EXPERIMENTS / "m178_certified_phi2_owent",
    EXPERIMENTS / "m179_background_archive_producer",
    EXPERIMENTS / "m172_selective_22_owner_fusion",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from m125_forward_tangent import (  # noqa: E402
    LocalReluJacobian,
    TangentState,
    tangent_stage,
)


INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
CORRELATION_MARGIN = 1.0e-10
VARIANCE_FLOOR = 1.0e-12
HEX_DIGEST_LENGTH = 64
_CONTEXT_RECEIPTS: dict[str, tuple[object, ...]] = {}
_OWNERSHIP_RECEIPTS: dict[str, tuple[object, ...]] = {}
_SOURCE_RECEIPTS: dict[str, tuple[object, ...]] = {}
_CONVERSION_RECEIPTS: dict[str, tuple[object, ...]] = {}
_MAP_RECEIPTS: dict[str, tuple[object, ...]] = {}


def _frozen_array(value: np.ndarray, *, ndim: int | None = None) -> np.ndarray:
    """Own one canonical float64 bytes buffer that cannot be thawed."""

    canonical = np.array(value, dtype="<f8", copy=True, order="C")
    result = np.frombuffer(canonical.tobytes(order="C"), dtype="<f8").reshape(
        canonical.shape
    )
    if ndim is not None and result.ndim != ndim:
        raise ValueError(f"expected a rank-{ndim} array")
    if result.flags.writeable:
        raise AssertionError("bytes-backed frozen array unexpectedly writeable")
    return result


def _array_digest(*named_arrays: tuple[str, np.ndarray]) -> str:
    digest = hashlib.sha256()
    digest.update(b"m198-array-digest-v1\0")
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


def _validate_hex_digest(name: str, value: str) -> None:
    if len(value) != HEX_DIGEST_LENGTH or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ValueError(f"{name} must be a lowercase sha256 digest")


def _frozen_tangent(state: TangentState) -> TangentState:
    return TangentState(
        _frozen_array(state.mean, ndim=1),
        _frozen_array(state.covariance, ndim=2),
    )


def _frozen_jacobian(jacobian: LocalReluJacobian) -> LocalReluJacobian:
    return LocalReluJacobian(
        probability=_frozen_array(jacobian.probability, ndim=1),
        mean_variance_derivative=_frozen_array(
            jacobian.mean_variance_derivative, ndim=1
        ),
        price_kernel=_frozen_array(jacobian.price_kernel, ndim=2),
        h_mu=_frozen_array(jacobian.h_mu, ndim=2),
        h_variance=_frozen_array(jacobian.h_variance, ndim=2),
    )


@dataclass(frozen=True)
class ContextProvenance:
    """Exact identity of one archived pre-ReLU Gaussian state."""

    network_digest: str
    weight_trace_digest: str
    relu_layer: int
    producer_epoch: int
    cast_provenance: str
    pre_state_digest: str
    issuer_family: str
    issuer_receipt: str

    def __post_init__(self) -> None:
        _validate_hex_digest("network_digest", self.network_digest)
        _validate_hex_digest("weight_trace_digest", self.weight_trace_digest)
        _validate_hex_digest("pre_state_digest", self.pre_state_digest)
        _validate_hex_digest("issuer_receipt", self.issuer_receipt)
        if self.relu_layer < 1 or self.producer_epoch < 0:
            raise ValueError("invalid context provenance label")
        if not self.cast_provenance or "f64" not in self.cast_provenance.lower():
            raise ValueError("cast provenance must explicitly record float64")
        if self.issuer_family not in {
            "m179_background_archive",
            "m198_generated_reference",
        }:
            raise ValueError("unrecognized context issuer family")

    @property
    def digest(self) -> str:
        return _record_digest(
            "m198-context-provenance-v1",
            self.network_digest,
            self.weight_trace_digest,
            self.relu_layer,
            self.producer_epoch,
            self.cast_provenance,
            self.pre_state_digest,
            self.issuer_family,
            self.issuer_receipt,
        )


def _context_record(
    *,
    network_digest: str,
    weight_trace_digest: str,
    relu_layer: int,
    producer_epoch: int,
    cast_provenance: str,
    pre_state_digest: str,
    issuer_family: str,
) -> tuple[object, ...]:
    return (
        network_digest,
        weight_trace_digest,
        int(relu_layer),
        int(producer_epoch),
        cast_provenance,
        pre_state_digest,
        issuer_family,
    )


def _issue_context_provenance(
    pre_mean: np.ndarray,
    pre_covariance: np.ndarray,
    *,
    network_digest: str,
    weight_trace_digest: str,
    relu_layer: int,
    producer_epoch: int,
    cast_provenance: str = "generated-f64 (no f32 source in this trace)",
    issuer_family: str,
) -> ContextProvenance:
    pre_state_digest = _array_digest(
        ("pre_mean", pre_mean), ("pre_covariance", pre_covariance)
    )
    record = _context_record(
        network_digest=network_digest,
        weight_trace_digest=weight_trace_digest,
        relu_layer=relu_layer,
        producer_epoch=producer_epoch,
        cast_provenance=cast_provenance,
        pre_state_digest=pre_state_digest,
        issuer_family=issuer_family,
    )
    receipt = _record_digest("m198-context-receipt-v1", *record)
    _CONTEXT_RECEIPTS[receipt] = record
    return ContextProvenance(
        network_digest=network_digest,
        weight_trace_digest=weight_trace_digest,
        relu_layer=relu_layer,
        producer_epoch=producer_epoch,
        cast_provenance=cast_provenance,
        pre_state_digest=pre_state_digest,
        issuer_family=issuer_family,
        issuer_receipt=receipt,
    )


def make_context_provenance(
    pre_mean: np.ndarray,
    pre_covariance: np.ndarray,
    *,
    network_digest: str,
    weight_trace_digest: str,
    relu_layer: int,
    producer_epoch: int,
    cast_provenance: str = "generated-f64 (no f32 source in this trace)",
) -> ContextProvenance:
    """Issue a generated mathematical-reference context, never production."""

    return _issue_context_provenance(
        pre_mean,
        pre_covariance,
        network_digest=network_digest,
        weight_trace_digest=weight_trace_digest,
        relu_layer=relu_layer,
        producer_epoch=producer_epoch,
        cast_provenance=cast_provenance,
        issuer_family="m198_generated_reference",
    )


def _verify_context_provenance(
    provenance: ContextProvenance,
    pre_mean: np.ndarray,
    pre_covariance: np.ndarray,
    *,
    required_family: str | None = None,
) -> None:
    state_digest = _array_digest(
        ("pre_mean", pre_mean), ("pre_covariance", pre_covariance)
    )
    if provenance.pre_state_digest != state_digest:
        raise ValueError("context provenance/pre-state digest mismatch")
    _verify_context_receipt(provenance, required_family=required_family)


def _verify_context_receipt(
    provenance: ContextProvenance, *, required_family: str | None = None
) -> None:
    record = _context_record(
        network_digest=provenance.network_digest,
        weight_trace_digest=provenance.weight_trace_digest,
        relu_layer=provenance.relu_layer,
        producer_epoch=provenance.producer_epoch,
        cast_provenance=provenance.cast_provenance,
        pre_state_digest=provenance.pre_state_digest,
        issuer_family=provenance.issuer_family,
    )
    if _CONTEXT_RECEIPTS.get(provenance.issuer_receipt) != record:
        raise ValueError("unregistered or stale context issuer receipt")
    if required_family is not None and provenance.issuer_family != required_family:
        raise ValueError(f"context was not issued by {required_family}")


@dataclass(frozen=True)
class SourceOwnerPolicy:
    """Descriptive owner family; authorization comes from the witness."""

    family: str = "m172_selective_22"

    def __post_init__(self) -> None:
        if self.family not in {"m172_selective_22", "dense_reference_t4"}:
            raise ValueError("unsupported Source211 owner family")


M163_M172_OWNER = SourceOwnerPolicy()
DENSE_REFERENCE_OWNER = SourceOwnerPolicy("dense_reference_t4")


@dataclass(frozen=True)
class Source211Slots:
    """Immutable repeated-output fourth-order source slots."""

    aaaa: np.ndarray
    aaab: np.ndarray
    aabb: np.ndarray
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        aaaa = _frozen_array(self.aaaa, ndim=1)
        aaab = _frozen_array(self.aaab, ndim=2)
        aabb = _frozen_array(self.aabb, ndim=2)
        n = aaaa.size
        if aaab.shape != (n, n) or aabb.shape != (n, n):
            raise ValueError("Source211 slot shape mismatch")
        if not all(np.all(np.isfinite(value)) for value in (aaaa, aaab, aabb)):
            raise ValueError("non-finite Source211 slot")
        if not np.array_equal(aaaa, np.diag(aaab)):
            raise ValueError("Source211 invariant aaaa == diag(aaab) failed")
        if not np.array_equal(aabb, aabb.T):
            raise ValueError("Source211 aabb must be exactly symmetric")
        digest = _array_digest(("aaaa", aaaa), ("aaab", aaab), ("aabb", aabb))
        object.__setattr__(self, "aaaa", aaaa)
        object.__setattr__(self, "aaab", aaab)
        object.__setattr__(self, "aabb", aabb)
        object.__setattr__(self, "digest", digest)

    @property
    def width(self) -> int:
        return self.aaaa.size


def zero_source_slots(width: int) -> Source211Slots:
    return Source211Slots(
        np.zeros(width, dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
    )


def _slots_max_abs_difference(left: Source211Slots, right: Source211Slots) -> float:
    return float(
        max(
            np.max(np.abs(left.aaaa - right.aaaa)),
            np.max(np.abs(left.aaab - right.aaab)),
            np.max(np.abs(left.aabb - right.aabb)),
        )
    )


def _verify_slots(slots: Source211Slots) -> None:
    rebuilt = Source211Slots(slots.aaaa, slots.aaab, slots.aabb)
    if rebuilt.digest != slots.digest:
        raise ValueError("Source211 slots were tampered after issuance")


def _add_slots(*values: Source211Slots) -> Source211Slots:
    if not values or len({value.width for value in values}) != 1:
        raise ValueError("cannot add empty or width-mismatched Source211 slots")
    return Source211Slots(
        sum((value.aaaa for value in values), np.zeros(values[0].width)),
        sum((value.aaab for value in values), np.zeros_like(values[0].aaab)),
        sum((value.aabb for value in values), np.zeros_like(values[0].aabb)),
    )


def _scale_slots(scale: float, value: Source211Slots) -> Source211Slots:
    return Source211Slots(scale * value.aaaa, scale * value.aaab, scale * value.aabb)


@dataclass(frozen=True)
class OwnershipConservationWitness:
    """Issuer-backed M172 ownership and source-contribution conservation."""

    scope: str
    physical_k22_half: np.ndarray
    control_ijj: np.ndarray
    residual_ijj: np.ndarray
    prior_owned_slots: Source211Slots
    emitted_source_slots: Source211Slots
    transferred_target_slots: Source211Slots
    control_source_slots: Source211Slots
    residual_source_slots: Source211Slots
    retained_k4_source_slots: Source211Slots
    retained_k31_source_slots: Source211Slots
    retired_legacy_k22_slots: Source211Slots
    complete_residual_interface: str = "M167.complete_residual_table"
    issuer_receipt: str = ""
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        physical = _frozen_array(self.physical_k22_half, ndim=2)
        control = _frozen_array(self.control_ijj, ndim=2)
        residual = _frozen_array(self.residual_ijj, ndim=2)
        if physical.shape[0] != physical.shape[1] or not (
            control.shape == residual.shape == physical.shape
        ):
            raise ValueError("ownership witness shape mismatch")
        if not all(np.all(np.isfinite(x)) for x in (physical, control, residual)):
            raise ValueError("non-finite ownership witness")
        if not all(np.array_equal(x, x.T) for x in (physical, control, residual)):
            raise ValueError("ownership witness must be exactly symmetric")
        if not all(np.array_equal(np.diag(x), np.zeros(physical.shape[0])) for x in (physical, control, residual)):
            raise ValueError("ownership collision diagonal must be exactly zero")
        _validate_hex_digest("ownership issuer_receipt", self.issuer_receipt)
        slot_values = (
            self.prior_owned_slots,
            self.emitted_source_slots,
            self.transferred_target_slots,
            self.control_source_slots,
            self.residual_source_slots,
            self.retained_k4_source_slots,
            self.retained_k31_source_slots,
            self.retired_legacy_k22_slots,
        )
        if any(value.width != physical.shape[0] for value in slot_values):
            raise ValueError("ownership witness/source width mismatch")
        for value in slot_values:
            _verify_slots(value)
        if self.scope == "m172_selective_22":
            if not np.array_equal(physical - control, residual):
                raise ValueError("ownership conservation physical-control=residual failed")
            reconstructed_transfer = _add_slots(
                self.control_source_slots, self.residual_source_slots
            )
            if _slots_max_abs_difference(
                self.transferred_target_slots, reconstructed_transfer
            ) > 5.0e-10:
                raise ValueError("control plus residual does not reconstruct transferred source")
            reconstructed_emitted = _add_slots(
                self.transferred_target_slots,
                self.retained_k4_source_slots,
                self.retained_k31_source_slots,
            )
            if _slots_max_abs_difference(
                self.emitted_source_slots, reconstructed_emitted
            ) > 5.0e-10:
                raise ValueError("emitted source omits or double-counts an owner contribution")
            if _slots_max_abs_difference(
                self.prior_owned_slots, self.emitted_source_slots
            ) > 5.0e-10:
                raise ValueError("ownership transfer changed or double-counted the owned source")
            if _slots_max_abs_difference(
                self.retired_legacy_k22_slots, zero_source_slots(physical.shape[0])
            ) != 0.0:
                raise ValueError("legacy K22 source was not retired exactly")
            if self.complete_residual_interface != "M167.complete_residual_table":
                raise ValueError("wrong collision residual interface")
        elif self.scope == "dense_reference_t4":
            zero_matrix = np.zeros_like(physical)
            if not all(
                np.array_equal(value, zero_matrix)
                for value in (physical, control, residual)
            ):
                raise ValueError("reference ownership cannot carry physical coefficients")
            if _slots_max_abs_difference(
                self.prior_owned_slots, self.emitted_source_slots
            ) != 0.0:
                raise ValueError("reference ownership/source mismatch")
        else:
            raise ValueError("unsupported ownership witness scope")
        witness_digest = _record_digest(
            "m198-ownership-witness-v2",
            self.scope,
            _array_digest(
                ("physical_k22_half", physical),
                ("control_ijj", control),
                ("residual_ijj", residual),
            ),
            self.prior_owned_slots.digest,
            self.emitted_source_slots.digest,
            self.transferred_target_slots.digest,
            self.control_source_slots.digest,
            self.residual_source_slots.digest,
            self.retained_k4_source_slots.digest,
            self.retained_k31_source_slots.digest,
            self.retired_legacy_k22_slots.digest,
            self.complete_residual_interface,
            self.issuer_receipt,
        )
        object.__setattr__(self, "physical_k22_half", physical)
        object.__setattr__(self, "control_ijj", control)
        object.__setattr__(self, "residual_ijj", residual)
        object.__setattr__(self, "digest", witness_digest)


def _ownership_record(witness: OwnershipConservationWitness) -> tuple[object, ...]:
    return (
        witness.scope,
        _array_digest(
            ("physical_k22_half", witness.physical_k22_half),
            ("control_ijj", witness.control_ijj),
            ("residual_ijj", witness.residual_ijj),
        ),
        witness.prior_owned_slots.digest,
        witness.emitted_source_slots.digest,
        witness.transferred_target_slots.digest,
        witness.control_source_slots.digest,
        witness.residual_source_slots.digest,
        witness.retained_k4_source_slots.digest,
        witness.retained_k31_source_slots.digest,
        witness.retired_legacy_k22_slots.digest,
        witness.complete_residual_interface,
    )


def _issue_ownership(**values: object) -> OwnershipConservationWitness:
    provisional = dict(values)
    provisional["issuer_receipt"] = "0" * 64
    unsigned = OwnershipConservationWitness(**provisional)
    record = _ownership_record(unsigned)
    receipt = _record_digest("m198-ownership-receipt-v2", *record)
    _OWNERSHIP_RECEIPTS[receipt] = record
    provisional["issuer_receipt"] = receipt
    return OwnershipConservationWitness(**provisional)


def _verify_ownership(witness: OwnershipConservationWitness) -> None:
    # Reconstructing catches object.__setattr__ tampering of any nested field.
    record = _ownership_record(witness)
    if _OWNERSHIP_RECEIPTS.get(witness.issuer_receipt) != record:
        raise ValueError("unregistered, forged, or tampered ownership receipt")
    expected = OwnershipConservationWitness(
        scope=witness.scope,
        physical_k22_half=witness.physical_k22_half,
        control_ijj=witness.control_ijj,
        residual_ijj=witness.residual_ijj,
        prior_owned_slots=witness.prior_owned_slots,
        emitted_source_slots=witness.emitted_source_slots,
        transferred_target_slots=witness.transferred_target_slots,
        control_source_slots=witness.control_source_slots,
        residual_source_slots=witness.residual_source_slots,
        retained_k4_source_slots=witness.retained_k4_source_slots,
        retained_k31_source_slots=witness.retained_k31_source_slots,
        retired_legacy_k22_slots=witness.retired_legacy_k22_slots,
        complete_residual_interface=witness.complete_residual_interface,
        issuer_receipt=witness.issuer_receipt,
    )
    if expected.digest != witness.digest:
        raise ValueError("ownership witness digest was tampered")


def _issue_reference_ownership(slots: Source211Slots) -> OwnershipConservationWitness:
    zero_slots = zero_source_slots(slots.width)
    zero_matrix = np.zeros((slots.width, slots.width), dtype=np.float64)
    return _issue_ownership(
        scope="dense_reference_t4",
        physical_k22_half=zero_matrix,
        control_ijj=zero_matrix,
        residual_ijj=zero_matrix,
        prior_owned_slots=slots,
        emitted_source_slots=slots,
        transferred_target_slots=zero_slots,
        control_source_slots=zero_slots,
        residual_source_slots=zero_slots,
        retained_k4_source_slots=zero_slots,
        retained_k31_source_slots=zero_slots,
        retired_legacy_k22_slots=zero_slots,
    )


@dataclass(frozen=True)
class LabelledSource211:
    provenance: ContextProvenance
    owner: SourceOwnerPolicy
    ownership: OwnershipConservationWitness
    slots: Source211Slots
    source_receipt: str
    source_id: str = field(init=False)

    def __post_init__(self) -> None:
        _validate_hex_digest("source_receipt", self.source_receipt)
        _verify_context_receipt(self.provenance)
        _verify_slots(self.slots)
        _verify_ownership(self.ownership)
        n = self.slots.width
        if self.ownership.physical_k22_half.shape != (n, n):
            raise ValueError("Source211/ownership width mismatch")
        if self.ownership.emitted_source_slots.digest != self.slots.digest:
            raise ValueError("ownership witness is not bound to emitted Source211 slots")
        if self.owner.family != self.ownership.scope:
            raise ValueError("source owner family/ownership scope mismatch")
        source_id = _record_digest(
            "m198-source211-v2",
            self.provenance.digest,
            self.owner.family,
            self.ownership.digest,
            self.slots.digest,
            self.source_receipt,
        )
        record = (
            self.provenance.digest,
            self.owner.family,
            self.ownership.digest,
            self.slots.digest,
        )
        if _SOURCE_RECEIPTS.get(self.source_receipt) != record:
            raise ValueError("unregistered, forged, or stale Source211 receipt")
        object.__setattr__(self, "source_id", source_id)

    @property
    def aaaa(self) -> np.ndarray:
        return self.slots.aaaa

    @property
    def aaab(self) -> np.ndarray:
        return self.slots.aaab

    @property
    def aabb(self) -> np.ndarray:
        return self.slots.aabb

    @property
    def relu_layer(self) -> int:
        return self.provenance.relu_layer

    @property
    def producer_epoch(self) -> int:
        return self.provenance.producer_epoch


def _issue_labelled_source(
    *,
    provenance: ContextProvenance,
    owner: SourceOwnerPolicy,
    ownership: OwnershipConservationWitness,
    slots: Source211Slots,
) -> LabelledSource211:
    _verify_ownership(ownership)
    record = (provenance.digest, owner.family, ownership.digest, slots.digest)
    receipt = _record_digest("m198-source-receipt-v2", *record)
    _SOURCE_RECEIPTS[receipt] = record
    return LabelledSource211(
        provenance=provenance,
        owner=owner,
        ownership=ownership,
        slots=slots,
        source_receipt=receipt,
    )


def _verify_labelled_source(
    source: LabelledSource211, *, required_family: str | None = None
) -> None:
    _verify_context_receipt(source.provenance)
    _verify_slots(source.slots)
    _verify_ownership(source.ownership)
    record = (
        source.provenance.digest,
        source.owner.family,
        source.ownership.digest,
        source.slots.digest,
    )
    if _SOURCE_RECEIPTS.get(source.source_receipt) != record:
        raise ValueError("unregistered, forged, or tampered Source211 receipt")
    expected_source_id = _record_digest(
        "m198-source211-v2",
        source.provenance.digest,
        source.owner.family,
        source.ownership.digest,
        source.slots.digest,
        source.source_receipt,
    )
    if source.source_id != expected_source_id:
        raise ValueError("Source211 identity was tampered")
    if source.ownership.emitted_source_slots.digest != source.slots.digest:
        raise ValueError("ownership witness/source binding was tampered")
    if source.owner.family != source.ownership.scope:
        raise ValueError("source owner family/ownership scope mismatch")
    if required_family is not None and source.owner.family != required_family:
        raise ValueError(f"source was not issued by {required_family}")


@dataclass(frozen=True)
class DelayOneContext:
    provenance: ContextProvenance
    pre_mean: np.ndarray
    pre_covariance: np.ndarray
    post_mean: np.ndarray

    def __post_init__(self) -> None:
        mean = _frozen_array(self.pre_mean, ndim=1)
        covariance = _frozen_array(self.pre_covariance, ndim=2)
        post_mean = _frozen_array(self.post_mean, ndim=1)
        if covariance.shape != (mean.size, mean.size):
            raise ValueError("delay-one Gaussian shape mismatch")
        if post_mean.shape != mean.shape:
            raise ValueError("post-mean shape mismatch")
        if not all(np.all(np.isfinite(value)) for value in (mean, covariance, post_mean)):
            raise ValueError("non-finite delay-one context")
        if not np.array_equal(covariance, covariance.T):
            raise ValueError("pre-ReLU covariance must be exactly symmetric")
        _verify_context_provenance(self.provenance, mean, covariance)
        variance = np.diag(covariance)
        if np.any(variance <= VARIANCE_FLOOR):
            raise ValueError("unsafe pre-ReLU marginal variance")
        if float(np.min(np.linalg.eigvalsh(covariance))) <= VARIANCE_FLOOR:
            raise ValueError("pre-ReLU covariance is not safely SPD")
        object.__setattr__(self, "pre_mean", mean)
        object.__setattr__(self, "pre_covariance", covariance)
        object.__setattr__(self, "post_mean", post_mean)

    @property
    def relu_layer(self) -> int:
        return self.provenance.relu_layer

    @property
    def producer_epoch(self) -> int:
        return self.provenance.producer_epoch


@dataclass(frozen=True)
class LabelledTangent:
    source: LabelledSource211
    context: DelayOneContext
    state: TangentState
    conversion_receipt: str

    def __post_init__(self) -> None:
        _validate_hex_digest("conversion_receipt", self.conversion_receipt)
        object.__setattr__(self, "state", _frozen_tangent(self.state))
        _verify_labelled_tangent(self)

    @property
    def provenance(self) -> ContextProvenance:
        return self.source.provenance

    @property
    def owner(self) -> SourceOwnerPolicy:
        return self.source.owner

    @property
    def ownership_digest(self) -> str:
        return self.source.ownership.digest

    @property
    def source_id(self) -> str:
        return self.source.source_id

    @property
    def relu_layer(self) -> int:
        return self.provenance.relu_layer

    @property
    def producer_epoch(self) -> int:
        return self.provenance.producer_epoch


@dataclass(frozen=True)
class ExtendedBackgroundEntry:
    """M179-compatible entry retaining the already-computed pre-ReLU state."""

    provenance: ContextProvenance
    pre_mean: np.ndarray
    pre_covariance: np.ndarray
    mu: np.ndarray
    V: np.ndarray
    jacobian: LocalReluJacobian
    strata: Mapping[str, int]

    def __post_init__(self) -> None:
        pre_mean = _frozen_array(self.pre_mean, ndim=1)
        pre_covariance = _frozen_array(self.pre_covariance, ndim=2)
        mu = _frozen_array(self.mu, ndim=1)
        covariance = _frozen_array(self.V, ndim=2)
        _verify_context_provenance(
            self.provenance,
            pre_mean,
            pre_covariance,
            required_family="m179_background_archive",
        )
        object.__setattr__(self, "pre_mean", pre_mean)
        object.__setattr__(self, "pre_covariance", pre_covariance)
        object.__setattr__(self, "mu", mu)
        object.__setattr__(self, "V", covariance)
        object.__setattr__(self, "jacobian", _frozen_jacobian(self.jacobian))
        object.__setattr__(self, "strata", MappingProxyType(dict(self.strata)))

    @property
    def layer(self) -> int:
        return self.provenance.relu_layer

    @property
    def producer_epoch(self) -> int:
        return self.provenance.producer_epoch

    @property
    def delay_one_context(self) -> DelayOneContext:
        return DelayOneContext(
            provenance=self.provenance,
            pre_mean=self.pre_mean,
            pre_covariance=self.pre_covariance,
            post_mean=self.mu,
        )


def _cdf(value: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(value, dtype=np.float64)
    answer = np.fromiter(
        (0.5 * math.erfc(-float(item) / math.sqrt(2.0)) for item in values.ravel()),
        dtype=np.float64,
        count=values.size,
    ).reshape(values.shape)
    return float(answer) if answer.ndim == 0 else answer


def _pdf(value: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(value, dtype=np.float64)
    answer = np.exp(-0.5 * values * values) * INV_SQRT_2PI
    return float(answer) if answer.ndim == 0 else answer


def relu_gaussian_mean(mean: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    variance = np.diag(covariance)
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    return sigma * np.asarray(_pdf(alpha)) + mean * np.asarray(_cdf(alpha))


def _source211_delay_one_state(
    source: LabelledSource211,
    context: DelayOneContext,
) -> TangentState:
    """Convert fourth-order repeated slots under their exact bound context."""

    _verify_labelled_source(source)
    _verify_context_provenance(
        context.provenance, context.pre_mean, context.pre_covariance
    )
    if source.provenance != context.provenance:
        raise ValueError("Source211/context provenance mismatch")
    if source.aaaa.size != context.pre_mean.size:
        raise ValueError("Source211/context width mismatch")

    mean = context.pre_mean
    covariance = context.pre_covariance
    n = mean.size
    variance = np.diag(covariance)
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    density_standard = np.asarray(_pdf(alpha), dtype=np.float64)
    density_zero = density_standard / sigma
    density_prime = (mean / variance) * density_zero
    density_second = (
        mean * mean / (variance * variance) - 1.0 / variance
    ) * density_zero
    relu_mean = relu_gaussian_mean(mean, covariance)
    if not np.allclose(relu_mean, context.post_mean, rtol=2.0e-13, atol=2.0e-13):
        raise ValueError("context post-mean does not match its pre-ReLU Gaussian state")

    delta_mean = (source.aaaa / 24.0) * density_second
    delta_raw = np.empty((n, n), dtype=np.float64)
    indices = np.arange(n)
    delta_raw[indices, indices] = -(source.aaaa / 12.0) * density_prime

    for i in range(n):
        for j in range(i + 1, n):
            cij = covariance[i, j]
            rho = cij / (sigma[i] * sigma[j])
            if abs(rho) >= 1.0 - CORRELATION_MARGIN:
                raise ValueError("delay-one response reached singular correlation")

            conditional_variance_j = variance[j] - cij * cij / variance[i]
            conditional_mean_j = mean[j] - cij * mean[i] / variance[i]
            conditional_sigma_j = math.sqrt(conditional_variance_j)
            conditional_alpha_j = conditional_mean_j / conditional_sigma_j
            probability_j = float(_cdf(conditional_alpha_j))
            conditional_density_j = float(_pdf(conditional_alpha_j))
            relu_j = conditional_sigma_j * conditional_density_j + conditional_mean_j * probability_j
            beta_j = cij / variance[i]

            conditional_variance_i = variance[i] - cij * cij / variance[j]
            conditional_mean_i = mean[i] - cij * mean[j] / variance[j]
            conditional_sigma_i = math.sqrt(conditional_variance_i)
            conditional_alpha_i = conditional_mean_i / conditional_sigma_i
            probability_i = float(_cdf(conditional_alpha_i))
            conditional_density_i = float(_pdf(conditional_alpha_i))
            relu_i = conditional_sigma_i * conditional_density_i + conditional_mean_i * probability_i
            beta_i = cij / variance[j]

            d40 = (
                density_second[i] * relu_j
                + 2.0 * density_prime[i] * beta_j * probability_j
                + density_zero[i] * beta_j * beta_j * conditional_density_j / conditional_sigma_j
            )
            d31 = -(
                density_prime[i] * probability_j
                + density_zero[i] * beta_j * conditional_density_j / conditional_sigma_j
            )
            d04 = (
                density_second[j] * relu_i
                + 2.0 * density_prime[j] * beta_i * probability_i
                + density_zero[j] * beta_i * beta_i * conditional_density_i / conditional_sigma_i
            )
            d13 = -(
                density_prime[j] * probability_i
                + density_zero[j] * beta_i * conditional_density_i / conditional_sigma_i
            )
            determinant = variance[i] * variance[j] - cij * cij
            exponent = -0.5 * (
                variance[j] * mean[i] * mean[i]
                - 2.0 * cij * mean[i] * mean[j]
                + variance[i] * mean[j] * mean[j]
            ) / determinant
            d22 = math.exp(exponent) / (2.0 * math.pi * math.sqrt(determinant))
            value = (
                source.aaaa[i] * d40
                + 4.0 * source.aaab[i, j] * d31
                + 6.0 * source.aabb[i, j] * d22
                + 4.0 * source.aaab[j, i] * d13
                + source.aaaa[j] * d04
            ) / 24.0
            delta_raw[i, j] = delta_raw[j, i] = value

    delta_covariance = delta_raw - np.outer(delta_mean, relu_mean) - np.outer(relu_mean, delta_mean)
    delta_covariance = 0.5 * (delta_covariance + delta_covariance.T)
    return _frozen_tangent(TangentState(delta_mean, delta_covariance))


def _tangent_state_digest(state: TangentState) -> str:
    return _array_digest(("tangent_mean", state.mean), ("tangent_covariance", state.covariance))


def reference_source211_delay_one(
    source: LabelledSource211, context: DelayOneContext
) -> TangentState:
    """Generated mathematical oracle; its state has no carrier receipt."""

    _verify_labelled_source(source, required_family="dense_reference_t4")
    _verify_context_provenance(
        context.provenance,
        context.pre_mean,
        context.pre_covariance,
        required_family="m198_generated_reference",
    )
    return _source211_delay_one_state(source, context)


def source211_delay_one(
    source: LabelledSource211, context: DelayOneContext
) -> LabelledTangent:
    """Production conversion: only M172 source + M179 context receipts."""

    _verify_labelled_source(source, required_family="m172_selective_22")
    _verify_context_provenance(
        context.provenance,
        context.pre_mean,
        context.pre_covariance,
        required_family="m179_background_archive",
    )
    state = _source211_delay_one_state(source, context)
    record = (source.source_id, context.provenance.digest, _tangent_state_digest(state))
    receipt = _record_digest("m198-conversion-receipt-v1", *record)
    _CONVERSION_RECEIPTS[receipt] = record
    return LabelledTangent(
        source=source,
        context=context,
        state=state,
        conversion_receipt=receipt,
    )


def _verify_labelled_tangent(tangent: LabelledTangent) -> None:
    _verify_labelled_source(tangent.source, required_family="m172_selective_22")
    _verify_context_provenance(
        tangent.context.provenance,
        tangent.context.pre_mean,
        tangent.context.pre_covariance,
        required_family="m179_background_archive",
    )
    if tangent.source.provenance != tangent.context.provenance:
        raise ValueError("tangent source/context provenance mismatch")
    expected_state = _source211_delay_one_state(tangent.source, tangent.context)
    if not np.array_equal(expected_state.mean, tangent.state.mean) or not np.array_equal(
        expected_state.covariance, tangent.state.covariance
    ):
        raise ValueError("tangent state does not match its verified delay-one conversion")
    record = (
        tangent.source.source_id,
        tangent.context.provenance.digest,
        _tangent_state_digest(tangent.state),
    )
    if _CONVERSION_RECEIPTS.get(tangent.conversion_receipt) != record:
        raise ValueError("unregistered, forged, or stale conversion receipt")


def build_extended_background(
    weights: Sequence[np.ndarray],
    epoch: int = 0,
    *,
    network_digest: str | None = None,
    cast_provenance: str = "generated-f64 (no f32 source in this trace)",
) -> list[ExtendedBackgroundEntry]:
    """One-pass M179 recurrence retaining `(a,C)` without recomputation."""

    import m179_background_producer as producer
    import m179_jacobian_archive as archive

    matrices = [np.array(weight, dtype=np.float64, copy=True, order="C") for weight in weights]
    if not matrices:
        raise ValueError("at least one weight matrix is required")
    weight_trace_digest = _array_digest(
        *((f"weight_{index}", weight) for index, weight in enumerate(matrices, start=1))
    )
    if network_digest is None:
        network_digest = _record_digest("m198-generated-network-v1", weight_trace_digest)
    _validate_hex_digest("network_digest", network_digest)
    n = matrices[0].shape[0]
    mu = np.zeros(n, dtype=np.float64)
    covariance = np.eye(n, dtype=np.float64)
    entries: list[ExtendedBackgroundEntry] = []
    for layer, weight in enumerate(matrices, start=1):
        if weight.shape != (n, n):
            raise ValueError("constant-width square weights assumed")
        pre_mean = mu @ weight
        pre_covariance = weight.T @ (covariance @ weight)
        pre_covariance = 0.5 * (pre_covariance + pre_covariance.T)
        provenance = _issue_context_provenance(
            pre_mean,
            pre_covariance,
            network_digest=network_digest,
            weight_trace_digest=weight_trace_digest,
            relu_layer=layer,
            producer_epoch=epoch,
            cast_provenance=cast_provenance,
            issuer_family="m179_background_archive",
        )
        jacobian, jacobian_mean, strata = archive.build_jacobian(pre_mean, pre_covariance)
        state = producer.relu_moments(pre_mean, pre_covariance)
        if not np.allclose(jacobian_mean, state.mu, rtol=2.0e-13, atol=2.0e-13):
            raise AssertionError("M179 producer/Jacobian mean disagreement")
        mu, covariance = state.mu, state.V
        entries.append(
            ExtendedBackgroundEntry(
                provenance=provenance,
                pre_mean=pre_mean,
                pre_covariance=pre_covariance,
                mu=mu,
                V=covariance,
                jacobian=jacobian,
                strata=strata,
            )
        )
    return entries


def slots_from_dense_t4(
    tensor: np.ndarray,
    provenance: ContextProvenance,
) -> LabelledSource211:
    """Reference-only extraction of repeated slots from a dense symmetric T4."""

    _verify_context_receipt(
        provenance, required_family="m198_generated_reference"
    )
    tensor = np.asarray(tensor, dtype=np.float64)
    if tensor.ndim != 4 or len(set(tensor.shape)) != 1:
        raise ValueError("dense T4 must be n-by-n-by-n-by-n")
    n = tensor.shape[0]
    aaaa = np.asarray([tensor[i, i, i, i] for i in range(n)])
    aaab = np.asarray([[tensor[i, i, i, j] for j in range(n)] for i in range(n)])
    aabb = np.asarray([[tensor[i, i, j, j] for j in range(n)] for i in range(n)])
    aabb = 0.5 * (aabb + aabb.T)
    aaab[np.arange(n), np.arange(n)] = aaaa
    slots = Source211Slots(aaaa=aaaa, aaab=aaab, aabb=aabb)
    ownership = _issue_reference_ownership(slots)
    return _issue_labelled_source(
        provenance=provenance,
        owner=DENSE_REFERENCE_OWNER,
        ownership=ownership,
        slots=slots,
    )


def _external_source_slots(value: object) -> Source211Slots:
    aaaa = np.asarray(getattr(value, "aaaa"), dtype=np.float64).copy()
    aaab = np.asarray(getattr(value, "aaab"), dtype=np.float64).copy()
    aabb = np.asarray(getattr(value, "aabb"), dtype=np.float64)
    aaab[np.arange(aaaa.size), np.arange(aaaa.size)] = aaaa
    aabb = 0.5 * (aabb + aabb.T)
    return Source211Slots(
        aaaa,
        aaab,
        aabb,
    )


def issue_m172_source(
    *,
    provenance: ContextProvenance,
    weight: np.ndarray,
    distinct_211: np.ndarray,
    owners: object,
    covariance: np.ndarray,
) -> LabelledSource211:
    """Recompute and issue the exact M172 owner-transfer artifact.

    This is a small/generated algebra issuer, not an affordable target-width
    physical cumulant provider.  The caller supplies physical owner values;
    M172/M167 recompute every coefficient/source contribution and conservation
    identity before a production receipt is minted.
    """

    _verify_context_receipt(provenance, required_family="m179_background_archive")
    import m172_selective_22_owner_fusion as m172
    from m167_collision_owner_unification import (
        PhysicalFourthOwners,
        complete_source_reference,
        direct_physical_owner_source,
    )

    matrix = np.asarray(weight, dtype=np.float64)
    n = matrix.shape[0]
    if matrix.shape != (n, n):
        raise ValueError("M198 production issuer requires a square source weight")
    if n <= 0:
        raise ValueError("empty source weight")
    # M172 validates owners, distinct table, and covariance through these calls.
    target, control_table, residual_table = m172.selective_22_residual(
        distinct_211, owners, covariance
    )
    transferred_target = _external_source_slots(
        complete_source_reference(matrix, target)
    )
    control_source = _external_source_slots(
        m172.m163_control_source(matrix, covariance)
    )
    residual_source = _external_source_slots(
        complete_source_reference(matrix, residual_table)
    )
    checked_k4 = np.asarray(getattr(owners, "k4"), dtype=np.float64)
    checked_k31 = np.asarray(getattr(owners, "k31"), dtype=np.float64)
    zero_matrix = np.zeros((n, n), dtype=np.float64)
    retained_k4 = _external_source_slots(
        direct_physical_owner_source(
            matrix, PhysicalFourthOwners(checked_k4, zero_matrix, zero_matrix)
        )
    )
    retained_k31 = _external_source_slots(
        direct_physical_owner_source(
            matrix, PhysicalFourthOwners(np.zeros(n), checked_k31, zero_matrix)
        )
    )
    emitted = _add_slots(
        control_source, residual_source, retained_k4, retained_k31
    )
    prior = _external_source_slots(
        m172.old_separate_source(matrix, distinct_211, owners)
    )
    retired = _external_source_slots(m172.retired_22_source(matrix, owners))
    physical = np.empty((n, n), dtype=np.float64)
    control_ijj = np.empty((n, n), dtype=np.float64)
    residual_ijj = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            physical[i, j] = target[i, j, j] if i != j else 0.0
            control_ijj[i, j] = control_table[i, j, j] if i != j else 0.0
            residual_ijj[i, j] = residual_table[i, j, j] if i != j else 0.0
    # K22 is symmetric, and the exterior ijj control is symmetric.  Preserve
    # exact represented symmetry to make the witness ABI bitwise deterministic.
    physical = 0.5 * (physical + physical.T)
    control_ijj = 0.5 * (control_ijj + control_ijj.T)
    residual_ijj = physical - control_ijj
    witness = _issue_ownership(
        scope="m172_selective_22",
        physical_k22_half=physical,
        control_ijj=control_ijj,
        residual_ijj=residual_ijj,
        prior_owned_slots=prior,
        emitted_source_slots=emitted,
        transferred_target_slots=transferred_target,
        control_source_slots=control_source,
        residual_source_slots=residual_source,
        retained_k4_source_slots=retained_k4,
        retained_k31_source_slots=retained_k31,
        retired_legacy_k22_slots=retired,
    )
    return _issue_labelled_source(
        provenance=provenance,
        owner=M163_M172_OWNER,
        ownership=witness,
        slots=emitted,
    )


def scale_source(source: LabelledSource211, scale: float) -> LabelledSource211:
    _verify_labelled_source(source, required_family="dense_reference_t4")
    slots = _scale_slots(scale, source.slots)
    return _issue_labelled_source(
        provenance=source.provenance,
        owner=DENSE_REFERENCE_OWNER,
        ownership=_issue_reference_ownership(slots),
        slots=slots,
    )


def add_sources(left: LabelledSource211, right: LabelledSource211) -> LabelledSource211:
    _verify_labelled_source(left, required_family="dense_reference_t4")
    _verify_labelled_source(right, required_family="dense_reference_t4")
    if left.provenance != right.provenance or left.owner != right.owner:
        raise ValueError("cannot add differently labelled Source211 values")
    if left.source_id == right.source_id:
        raise ValueError("cannot add a Source211 value to the same owned source twice")
    slots = _add_slots(left.slots, right.slots)
    return _issue_labelled_source(
        provenance=left.provenance,
        owner=DENSE_REFERENCE_OWNER,
        ownership=_issue_reference_ownership(slots),
        slots=slots,
    )


@dataclass(frozen=True)
class LabelledCarrierMap:
    """One exact post-layer-k -> post-layer-(k+1) M125 map."""

    from_provenance: ContextProvenance
    to_provenance: ContextProvenance
    weight: np.ndarray
    jacobian: LocalReluJacobian
    map_receipt: str
    map_id: str = field(init=False)

    def __post_init__(self) -> None:
        _validate_hex_digest("map_receipt", self.map_receipt)
        _verify_context_receipt(
            self.from_provenance, required_family="m179_background_archive"
        )
        _verify_context_receipt(
            self.to_provenance, required_family="m179_background_archive"
        )
        if self.to_provenance.relu_layer != self.from_provenance.relu_layer + 1:
            raise ValueError("carrier map layers are not consecutive")
        for field_name in ("network_digest", "weight_trace_digest", "producer_epoch"):
            if getattr(self.from_provenance, field_name) != getattr(self.to_provenance, field_name):
                raise ValueError(f"carrier map {field_name} mismatch")
        weight = _frozen_array(self.weight, ndim=2)
        n = weight.shape[0]
        if weight.shape != (n, n):
            raise ValueError("carrier map weight must be square")
        jacobian = _frozen_jacobian(self.jacobian)
        if jacobian.probability.size != n:
            raise ValueError("carrier map weight/Jacobian width mismatch")
        record = (
            self.from_provenance.digest,
            self.to_provenance.digest,
            _array_digest(("weight", weight)),
            _array_digest(
                ("p", jacobian.probability),
                ("r", jacobian.mean_variance_derivative),
                ("K", jacobian.price_kernel),
                ("Hmu", jacobian.h_mu),
                ("Hv", jacobian.h_variance),
            ),
        )
        if _MAP_RECEIPTS.get(self.map_receipt) != record:
            raise ValueError("unregistered, forged, or stale carrier-map receipt")
        map_id = _record_digest(
            "m198-labelled-carrier-map-v2", *record, self.map_receipt
        )
        object.__setattr__(self, "weight", weight)
        object.__setattr__(self, "jacobian", jacobian)
        object.__setattr__(self, "map_id", map_id)


def _carrier_map_record(
    from_provenance: ContextProvenance,
    to_provenance: ContextProvenance,
    weight: np.ndarray,
    jacobian: LocalReluJacobian,
) -> tuple[object, ...]:
    return (
        from_provenance.digest,
        to_provenance.digest,
        _array_digest(("weight", weight)),
        _array_digest(
            ("p", jacobian.probability),
            ("r", jacobian.mean_variance_derivative),
            ("K", jacobian.price_kernel),
            ("Hmu", jacobian.h_mu),
            ("Hv", jacobian.h_variance),
        ),
    )


def _issue_carrier_map(
    *,
    from_provenance: ContextProvenance,
    to_provenance: ContextProvenance,
    weight: np.ndarray,
    jacobian: LocalReluJacobian,
) -> LabelledCarrierMap:
    frozen_weight = _frozen_array(weight, ndim=2)
    frozen_jacobian = _frozen_jacobian(jacobian)
    record = _carrier_map_record(
        from_provenance, to_provenance, frozen_weight, frozen_jacobian
    )
    receipt = _record_digest("m198-carrier-map-receipt-v1", *record)
    _MAP_RECEIPTS[receipt] = record
    return LabelledCarrierMap(
        from_provenance=from_provenance,
        to_provenance=to_provenance,
        weight=frozen_weight,
        jacobian=frozen_jacobian,
        map_receipt=receipt,
    )


def _verify_carrier_map(mapping: LabelledCarrierMap) -> None:
    record = _carrier_map_record(
        mapping.from_provenance,
        mapping.to_provenance,
        mapping.weight,
        mapping.jacobian,
    )
    if _MAP_RECEIPTS.get(mapping.map_receipt) != record:
        raise ValueError("unregistered, forged, or tampered carrier-map receipt")
    expected_id = _record_digest(
        "m198-labelled-carrier-map-v2", *record, mapping.map_receipt
    )
    if mapping.map_id != expected_id:
        raise ValueError("carrier-map identity was tampered")


@dataclass(frozen=True)
class LabelledCarrierResult:
    terminal_provenance: ContextProvenance
    consumed_source_ids: tuple[str, ...]
    consumed_map_ids: tuple[str, ...]
    state: TangentState

    def __post_init__(self) -> None:
        if len(set(self.consumed_source_ids)) != len(self.consumed_source_ids):
            raise ValueError("duplicate source identity in carrier result")
        object.__setattr__(self, "state", _frozen_tangent(self.state))


def build_labelled_carrier_maps(
    entries: Sequence[ExtendedBackgroundEntry],
    weights: Sequence[np.ndarray],
) -> list[LabelledCarrierMap]:
    if len(entries) != len(weights) or not entries:
        raise ValueError("background/weight trace length mismatch")
    maps = []
    for index in range(len(entries) - 1):
        maps.append(
            _issue_carrier_map(
                from_provenance=entries[index].provenance,
                to_provenance=entries[index + 1].provenance,
                weight=weights[index + 1],
                jacobian=entries[index + 1].jacobian,
            )
        )
    return maps


def _validate_labelled_chain(
    sources: Sequence[LabelledTangent], maps: Sequence[LabelledCarrierMap]
) -> None:
    if not sources or len(sources) != len(maps) + 1:
        raise ValueError("labelled source/map indexing mismatch")
    source_ids = [source.source_id for source in sources]
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("duplicate source identity or terminal reinjection")
    for source in sources:
        _verify_labelled_tangent(source)
    for index, mapping in enumerate(maps):
        _verify_carrier_map(mapping)
        if sources[index].provenance != mapping.from_provenance:
            raise ValueError("carrier source/from-context mismatch or reorder")
        if sources[index + 1].provenance != mapping.to_provenance:
            raise ValueError("carrier next-source/to-context mismatch or reorder")


def labelled_inhomogeneous_source_recurrence(
    sources: Sequence[LabelledTangent], maps: Sequence[LabelledCarrierMap]
) -> LabelledCarrierResult:
    """M125b with provenance retained and checked at every injection."""

    _validate_labelled_chain(sources, maps)
    state = sources[0].state
    for next_source, mapping in zip(sources[1:], maps):
        propagated = tangent_stage(state, mapping.weight, mapping.jacobian)
        state = TangentState(
            propagated.mean + next_source.state.mean,
            propagated.covariance + next_source.state.covariance,
        )
    return LabelledCarrierResult(
        terminal_provenance=sources[-1].provenance,
        consumed_source_ids=tuple(source.source_id for source in sources),
        consumed_map_ids=tuple(mapping.map_id for mapping in maps),
        state=state,
    )


def labelled_explicit_source_superposition(
    sources: Sequence[LabelledTangent], maps: Sequence[LabelledCarrierMap]
) -> LabelledCarrierResult:
    """Labelled reference: propagate each source through its entire suffix."""

    _validate_labelled_chain(sources, maps)
    final_mean = np.zeros_like(sources[0].state.mean)
    final_covariance = np.zeros_like(sources[0].state.covariance)
    for source_index, source in enumerate(sources):
        state = source.state
        for mapping in maps[source_index:]:
            state = tangent_stage(state, mapping.weight, mapping.jacobian)
        final_mean += state.mean
        final_covariance += state.covariance
    return LabelledCarrierResult(
        terminal_provenance=sources[-1].provenance,
        consumed_source_ids=tuple(source.source_id for source in sources),
        consumed_map_ids=tuple(mapping.map_id for mapping in maps),
        state=TangentState(final_mean, final_covariance),
    )
