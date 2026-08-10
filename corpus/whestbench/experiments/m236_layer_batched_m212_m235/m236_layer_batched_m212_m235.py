"""M236: fixed B=8 layer-batched M212 plus M235.

The only changed mechanism from frozen M235 is numerical owner liveness.  All
source layers remain independent and preserve the inherited per-layer
arithmetic.  Setup owns every numerical array and every block alias.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Sequence

import flopscope as flops
import flopscope.numpy as fnp


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m235_setup_shared_philox_row_receipt",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m212_flopscope_sidecar as m212  # noqa: E402
import m235_setup_shared_philox_row_receipt as m235  # noqa: E402


WIDTH = 256
LAYERS = 31
SUBSET_ROWS = 32
DEPTH = 3
PRODUCER_EPOCH = 231
BLOCK_SIZE = 8
BLOCK_SPANS = ((0, 8), (8, 16), (16, 24), (24, 31))
DOMAIN = "M236_SETUP_SHARED_PHILOX_SRSWOR_B8_V1"
DTYPE = fnp.float64


@dataclass
class GlobalOutputs:
    aaaa: object
    aaab: object
    aabb: object


@dataclass
class InternalOwners:
    scaled: object
    gram: object
    p: object
    p2: object
    rho: object
    rho_p: object
    scratch: object
    level_products: tuple[object, ...]


@dataclass
class BlockStaged:
    weight: object
    factor: object
    layer_ids: tuple[int, ...] | None = None
    producer_epoch: int | None = None


@dataclass
class BlockWorkspace:
    scaled: object
    gram: object
    p: object
    p2: object
    rho: object
    rho_p: object
    scratch: object
    aaab: object
    aabb: object
    aaaa: object
    level_products: tuple[object, ...]


@dataclass(frozen=True)
class BlockFullDomain:
    layer_ids: tuple[int, ...]
    producer_epoch: int
    aaaa: object
    aaab: object
    aabb: object
    gram: object
    p: object


@dataclass(frozen=True)
class BlockPlan:
    block_index: int
    start: int
    stop: int
    global_ids: tuple[int, ...]
    local_ids: tuple[int, ...]
    receipt: m235.SetupRowReceipt
    rank_alias: object
    selected_alias: object
    staged: BlockStaged
    base: BlockWorkspace
    row: m235.RowWorkspace
    collision_state: m235.ComponentState
    full: BlockFullDomain
    weight_slots: list[object | None]
    factor_slots: list[object | None]


@dataclass
class ComponentState:
    setup_seed: int
    producer_epoch: int
    domain: str
    layer_ids: tuple[int, ...]
    width: int
    layers: int
    subset_rows: int
    depth: int
    block_size: int
    receipt: m235.SetupRowReceipt
    outputs: GlobalOutputs
    staged_owner: object
    internal_owner: InternalOwners
    row_owner: m235.RowWorkspace
    block_plans: tuple[BlockPlan, ...]
    empty_owners: tuple[object, ...]


def _allocate_outputs(layers: int, width: int) -> GlobalOutputs:
    return GlobalOutputs(
        aaaa=fnp.empty((layers, width), dtype=DTYPE),
        aaab=fnp.empty((layers, width, width), dtype=DTYPE),
        aabb=fnp.empty((layers, width, width), dtype=DTYPE),
    )


def _allocate_internal_owners(capacity: int, width: int, depth: int) -> InternalOwners:
    plane = lambda: fnp.empty((capacity, width, width), dtype=DTYPE)
    vector = lambda: fnp.empty((capacity, width), dtype=DTYPE)
    products = []
    for level in range(depth):
        nodes = 2**level
        half = width // (2 ** (level + 1))
        products.append(fnp.empty((capacity, nodes, half, half), dtype=DTYPE))
    leaves = 2**depth
    leaf_width = width // leaves
    products.append(fnp.empty((capacity, leaves, leaf_width, leaf_width), dtype=DTYPE))
    return InternalOwners(
        scaled=plane(),
        gram=plane(),
        p=vector(),
        p2=vector(),
        rho=vector(),
        rho_p=vector(),
        scratch=plane(),
        level_products=tuple(products),
    )


def _internal_arrays(owner: InternalOwners) -> tuple[object, ...]:
    return (
        owner.scaled,
        owner.gram,
        owner.p,
        owner.p2,
        owner.rho,
        owner.rho_p,
        owner.scratch,
        *owner.level_products,
    )


def _spans(layers: int, block_size: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (start, min(start + block_size, layers))
        for start in range(0, layers, block_size)
    )


def _make_block_plan(
    *,
    block_index: int,
    start: int,
    stop: int,
    receipt: m235.SetupRowReceipt,
    outputs: GlobalOutputs,
    staged_owner: object,
    internal_owner: InternalOwners,
    row_owner: m235.RowWorkspace,
    width: int,
    subset_rows: int,
    producer_epoch: int,
    setup_seed: int,
    depth: int,
) -> BlockPlan:
    count = stop - start
    global_ids = tuple(range(start + 1, stop + 1))
    local_ids = tuple(range(1, count + 1))
    staged = BlockStaged(
        weight=staged_owner.weight[:count],
        factor=staged_owner.factor[:count],
    )
    base = BlockWorkspace(
        scaled=internal_owner.scaled[:count],
        gram=internal_owner.gram[:count],
        p=internal_owner.p[:count],
        p2=internal_owner.p2[:count],
        rho=internal_owner.rho[:count],
        rho_p=internal_owner.rho_p[:count],
        scratch=internal_owner.scratch[:count],
        aaab=outputs.aaab[start:stop],
        aabb=outputs.aabb[start:stop],
        aaaa=outputs.aaaa[start:stop],
        level_products=tuple(value[:count] for value in internal_owner.level_products),
    )
    block_receipt = m235.SetupRowReceipt(
        setup_seed=int(setup_seed),
        producer_epoch=int(producer_epoch),
        domain=m235.DOMAIN,
        layer_ids=local_ids,
        width=int(width),
        subset_rows=int(subset_rows),
        rank_order=receipt.rank_order[start:stop],
        selected=receipt.selected[start:stop],
    )
    row = m235.RowWorkspace(
        powers=row_owner.powers[:, :count],
        cross=row_owner.cross[:, :count],
    )
    collision_plan = m235._build_plan(block_receipt, base, row, width, subset_rows)
    collision_state = m235.ComponentState(
        setup_seed=int(setup_seed),
        producer_epoch=int(producer_epoch),
        domain=m235.DOMAIN,
        layer_ids=local_ids,
        width=int(width),
        layers=count,
        subset_rows=int(subset_rows),
        depth=int(depth),
        receipt_elapsed_s=0.0,
        receipt=block_receipt,
        staged=staged,
        base=base,
        row=row,
        plan=collision_plan,
    )
    full = BlockFullDomain(
        layer_ids=local_ids,
        producer_epoch=int(producer_epoch),
        aaaa=base.aaaa,
        aaab=base.aaab,
        aabb=base.aabb,
        gram=base.gram,
        p=base.p,
    )
    return BlockPlan(
        block_index=int(block_index),
        start=int(start),
        stop=int(stop),
        global_ids=global_ids,
        local_ids=local_ids,
        receipt=block_receipt,
        rank_alias=block_receipt.rank_order,
        selected_alias=block_receipt.selected,
        staged=staged,
        base=base,
        row=row,
        collision_state=collision_state,
        full=full,
        weight_slots=[None] * count,
        factor_slots=[None] * count,
    )


def setup_component(
    *,
    setup_seed: int,
    layers: int = LAYERS,
    width: int = WIDTH,
    subset_rows: int = SUBSET_ROWS,
    producer_epoch: int = PRODUCER_EPOCH,
    depth: int = DEPTH,
    block_size: int = BLOCK_SIZE,
) -> ComponentState:
    """Allocate the exact setup-owned B=8 topology and immutable aliases."""

    layer_count = int(layers)
    row_count = int(width)
    k = int(subset_rows)
    recursion_depth = int(depth)
    capacity = min(int(block_size), layer_count)
    if layer_count < 1 or capacity < 1 or int(block_size) != BLOCK_SIZE:
        raise ValueError("M236 requires positive layers and fixed block size eight")
    if recursion_depth < 0 or row_count % (2**recursion_depth):
        raise ValueError("width must be divisible by the M212 recursion block")
    receipt = m235.issue_setup_receipt(
        setup_seed=int(setup_seed),
        layers=layer_count,
        width=row_count,
        subset_rows=k,
        producer_epoch=int(producer_epoch),
    )
    outputs = _allocate_outputs(layer_count, row_count)
    staged_owner = m212.allocate_staged_inputs(layers=capacity, width=row_count)
    internal_owner = _allocate_internal_owners(capacity, row_count, recursion_depth)
    row_owner = m235._allocate_row_workspace(capacity, row_count, k)
    plans = tuple(
        _make_block_plan(
            block_index=index,
            start=start,
            stop=stop,
            receipt=receipt,
            outputs=outputs,
            staged_owner=staged_owner,
            internal_owner=internal_owner,
            row_owner=row_owner,
            width=row_count,
            subset_rows=k,
            producer_epoch=int(producer_epoch),
            setup_seed=int(setup_seed),
            depth=recursion_depth,
        )
        for index, (start, stop) in enumerate(_spans(layer_count, BLOCK_SIZE))
    )
    empty_owners = (
        outputs.aaaa,
        outputs.aaab,
        outputs.aabb,
        staged_owner.weight,
        staged_owner.factor,
        *_internal_arrays(internal_owner),
        row_owner.powers,
        row_owner.cross,
    )
    expected_empty_owners = 15 + recursion_depth
    if len(empty_owners) != expected_empty_owners:
        raise RuntimeError("M236 setup owner count drift")
    return ComponentState(
        setup_seed=int(setup_seed),
        producer_epoch=int(producer_epoch),
        domain=DOMAIN,
        layer_ids=tuple(range(1, layer_count + 1)),
        width=row_count,
        layers=layer_count,
        subset_rows=k,
        depth=recursion_depth,
        block_size=BLOCK_SIZE,
        receipt=receipt,
        outputs=outputs,
        staged_owner=staged_owner,
        internal_owner=internal_owner,
        row_owner=row_owner,
        block_plans=plans,
        empty_owners=empty_owners,
    )


def validate_records(state: ComponentState, records: Sequence[object]) -> None:
    """Reject every global-binding fault before the first charged write."""

    if state.domain != DOMAIN or state.block_size != BLOCK_SIZE:
        raise ValueError("M236 state domain or block size mismatch")
    if len(records) != state.layers:
        raise ValueError("M236 requires exactly one record per global layer")
    if tuple(int(record.layer) for record in records) != state.layer_ids:
        raise ValueError("M236 global records must be canonical and complete")
    if any(int(record.producer_epoch) != state.producer_epoch for record in records):
        raise ValueError("M236 producer epoch mismatch")
    weights = tuple(record.weight for record in records)
    factors = tuple(record.factor for record in records)
    if len({id(value) for value in weights}) != state.layers:
        raise ValueError("M236 duplicated weight object")
    if len({id(value) for value in factors}) != state.layers:
        raise ValueError("M236 duplicated factor object")
    for weight, factor in zip(weights, factors, strict=True):
        if tuple(weight.shape) != (state.width, state.width):
            raise ValueError("M236 bound weight shape mismatch")
        if tuple(factor.shape) != (state.width,):
            raise ValueError("M236 bound factor shape mismatch")
        if str(weight.dtype) not in {"float32", "float64"}:
            raise ValueError("M236 bound weight dtype mismatch")
        if str(factor.dtype) not in {"float32", "float64"}:
            raise ValueError("M236 bound factor dtype mismatch")
    expected_start = 0
    for plan in state.block_plans:
        if plan.start != expected_start or plan.stop <= plan.start:
            raise ValueError("M236 block span gap or overlap")
        if plan.global_ids != tuple(range(plan.start + 1, plan.stop + 1)):
            raise ValueError("M236 block global binding mismatch")
        if plan.local_ids != tuple(range(1, plan.stop - plan.start + 1)):
            raise ValueError("M236 block local binding mismatch")
        if (
            plan.receipt.rank_order is not plan.rank_alias
            or plan.receipt.selected is not plan.selected_alias
            or plan.collision_state.receipt is not plan.receipt
            or plan.collision_state.plan.receipt is not plan.receipt
        ):
            raise ValueError("M236 receipt global span binding mismatch")
        expected_start = plan.stop
    if expected_start != state.layers:
        raise ValueError("M236 block union is incomplete")


def _clear_slots(plan: BlockPlan) -> None:
    for index in range(len(plan.weight_slots)):
        plan.weight_slots[index] = None
        plan.factor_slots[index] = None


def compile_block_m212(plan: BlockPlan, records: Sequence[object], epoch: int):
    """Stage and compile one already-validated block, then release payload slots."""

    for local, global_index in enumerate(range(plan.start, plan.stop)):
        record = records[global_index]
        plan.weight_slots[local] = record.weight
        plan.factor_slots[local] = record.factor
    try:
        fnp.stack(plan.weight_slots, axis=0, out=plan.staged.weight)
        fnp.stack(plan.factor_slots, axis=0, out=plan.staged.factor)
    finally:
        _clear_slots(plan)
    plan.staged.layer_ids = plan.local_ids
    plan.staged.producer_epoch = int(epoch)
    return m212.compile_staged_stack(plan.staged, plan.base, depth=plan.collision_state.depth)


def subtract_block_m235(plan: BlockPlan):
    """Apply the unchanged M235 partial collision estimator to one block."""

    return m235.subtract_setup_row_sketch_inplace(plan.collision_state, plan.full)


def compile_records_inplace(state: ComponentState, records: Sequence[object]):
    """Compile all global layers directly into the three persistent outputs."""

    validate_records(state, records)
    for plan in state.block_plans:
        with flops.namespace("m212"):
            compile_block_m212(plan, records, state.producer_epoch)
        with flops.namespace("m235"):
            subtract_block_m235(plan)
    return state.outputs.aaaa, state.outputs.aaab, state.outputs.aabb


def staging_slots_clear(state: ComponentState) -> bool:
    return all(
        all(value is None for value in plan.weight_slots)
        and all(value is None for value in plan.factor_slots)
        for plan in state.block_plans
    )


def setup_owner_arrays(state: ComponentState) -> tuple[object, ...]:
    """Hostile-audit inventory; never called by the production compiler."""

    return (*state.empty_owners, state.receipt.rank_order, state.receipt.selected)


def workspace_arrays(state: ComponentState) -> tuple[object, ...]:
    """Current setup owners for same-worker identity/RSS auditing."""

    return state.empty_owners


def allocation_ledger(state: ComponentState) -> dict[str, object]:
    """Exact setup-owner byte ledger outside the timed compiler."""

    output_bytes = sum(
        int(value.nbytes)
        for value in (state.outputs.aaaa, state.outputs.aaab, state.outputs.aabb)
    )
    m212_bytes = int(state.staged_owner.weight.nbytes) + int(
        state.staged_owner.factor.nbytes
    ) + sum(int(value.nbytes) for value in _internal_arrays(state.internal_owner))
    m235_bytes = int(state.row_owner.powers.nbytes) + int(state.row_owner.cross.nbytes)
    rank_bytes = int(state.receipt.rank_order.nbytes)
    gather_bytes = (
        min(state.block_size, state.layers)
        * state.subset_rows
        * state.width
        * 8
    )
    numeric_peak = output_bytes + m212_bytes + m235_bytes + rank_bytes + gather_bytes
    return {
        "setup_empty_owner_count": len(state.empty_owners),
        "global_source_bytes": output_bytes,
        "rank_receipt_bytes": rank_bytes,
        "m212_block_bytes": m212_bytes,
        "m235_block_bytes": m235_bytes,
        "selected_gather_max_bytes": gather_bytes,
        "numeric_peak_bytes": numeric_peak,
        "numeric_peak_mib": numeric_peak / (1024.0 * 1024.0),
    }


__all__ = [
    "BLOCK_SIZE",
    "BLOCK_SPANS",
    "BlockPlan",
    "ComponentState",
    "GlobalOutputs",
    "allocation_ledger",
    "compile_block_m212",
    "compile_records_inplace",
    "setup_component",
    "setup_owner_arrays",
    "staging_slots_clear",
    "subtract_block_m235",
    "validate_records",
    "workspace_arrays",
]
