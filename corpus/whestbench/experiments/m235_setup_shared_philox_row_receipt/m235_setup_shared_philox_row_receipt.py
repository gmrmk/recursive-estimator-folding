"""Setup-shared exact SRSWOR receipt and M231 row-collision circuit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import time

import flopscope.numpy as fnp


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    BASE / "m212_backend_packed_explicit_symmetry",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m212_flopscope_sidecar as m212  # noqa: E402


WIDTH = 256
LAYERS = 31
SUBSET_ROWS = 32
DEPTH = 3
PRODUCER_EPOCH = 231
DOMAIN = "M235_SETUP_SHARED_PHILOX_SRSWOR_V1"
DTYPE = fnp.float64


@dataclass(frozen=True)
class SetupRowReceipt:
    setup_seed: int
    producer_epoch: int
    domain: str
    layer_ids: tuple[int, ...]
    width: int
    subset_rows: int
    rank_order: object
    selected: object


@dataclass
class RowWorkspace:
    powers: object
    cross: object


@dataclass(frozen=True)
class ProductionPlan:
    receipt: SetupRowReceipt
    row_owner: RowWorkspace
    selected_index3: object
    powers2: object
    powers3: object
    powers_t: object
    powers2_t: object
    cross_a: object
    cross_e: object
    rho_col: object
    rho_row: object
    p_col: object
    p_row: object
    scratch_t: object
    aaab_diag: object
    c12: object
    c8: object
    c4: object
    c18g: object
    c12g: object
    c6g: object
    cm24g: object


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
    receipt_elapsed_s: float
    receipt: SetupRowReceipt
    staged: object
    base: object
    row: RowWorkspace
    plan: ProductionPlan


def issue_setup_receipt(
    *,
    setup_seed: int,
    layers: int,
    width: int,
    subset_rows: int,
    producer_epoch: int,
) -> SetupRowReceipt:
    """Issue one immutable independent-slice setup receipt from ctx.seed."""

    layer_count = int(layers)
    row_count = int(width)
    k = int(subset_rows)
    seed = int(setup_seed)
    if seed < 0:
        raise ValueError("setup seed must be nonnegative")
    if layer_count < 1 or row_count < 3 or k < 1 or k >= row_count:
        raise ValueError("invalid M235 receipt dimensions")
    generator = fnp.random.Generator(fnp.random.Philox(int(setup_seed)))
    label_base = fnp.arange(row_count, dtype=fnp.int64)
    label_bank = fnp.broadcast_to(label_base, (layer_count, row_count))
    rank_order = generator.permuted(label_bank, axis=1)
    selected = rank_order[:, :k]
    selected.flags.writeable = False
    rank_order.flags.writeable = False
    return SetupRowReceipt(
        setup_seed=seed,
        producer_epoch=int(producer_epoch),
        domain=DOMAIN,
        layer_ids=tuple(range(1, layer_count + 1)),
        width=row_count,
        subset_rows=k,
        rank_order=rank_order,
        selected=selected,
    )


def _allocate_row_workspace(layers: int, width: int, subset_rows: int) -> RowWorkspace:
    return RowWorkspace(
        powers=fnp.empty((2, layers, subset_rows, width), dtype=DTYPE),
        cross=fnp.empty((2, layers, width, width), dtype=DTYPE),
    )


def _build_plan(
    receipt: SetupRowReceipt,
    base,
    row: RowWorkspace,
    width: int,
    subset_rows: int,
) -> ProductionPlan:
    scale = float(width) / float(subset_rows)
    powers2 = row.powers[0]
    powers3 = row.powers[1]
    return ProductionPlan(
        receipt=receipt,
        row_owner=row,
        selected_index3=receipt.selected[:, :, None],
        powers2=powers2,
        powers3=powers3,
        powers_t=fnp.transpose(row.powers, (0, 1, 3, 2)),
        powers2_t=fnp.transpose(powers2, (0, 2, 1)),
        cross_a=row.cross[0],
        cross_e=row.cross[1],
        rho_col=base.rho[:, :, None],
        rho_row=base.rho[:, None, :],
        p_col=base.p[:, :, None],
        p_row=base.p[:, None, :],
        scratch_t=fnp.swapaxes(base.scratch, 1, 2),
        aaab_diag=fnp.diagonal(base.aaab, axis1=1, axis2=2),
        c12=fnp.float64(12.0),
        c8=fnp.float64(8.0),
        c4=fnp.float64(4.0),
        c18g=fnp.float64(18.0 * scale),
        c12g=fnp.float64(12.0 * scale),
        c6g=fnp.float64(6.0 * scale),
        cm24g=fnp.float64(-24.0 * scale),
    )


def setup_component(
    *,
    setup_seed: int,
    layers: int = LAYERS,
    width: int = WIDTH,
    subset_rows: int = SUBSET_ROWS,
    producer_epoch: int = PRODUCER_EPOCH,
    depth: int = DEPTH,
) -> ComponentState:
    """Perform the MLP-independent M235 setup transaction."""

    layer_count = int(layers)
    row_count = int(width)
    k = int(subset_rows)
    recursion_depth = int(depth)
    if recursion_depth < 0 or row_count % (2**recursion_depth):
        raise ValueError("width must be divisible by the M212 recursion block")
    receipt_started = time.perf_counter()
    receipt = issue_setup_receipt(
        setup_seed=int(setup_seed),
        layers=layer_count,
        width=row_count,
        subset_rows=k,
        producer_epoch=int(producer_epoch),
    )
    receipt_elapsed = time.perf_counter() - receipt_started
    staged = m212.allocate_staged_inputs(layers=layer_count, width=row_count)
    base = m212.allocate_workspace(
        layers=layer_count, width=row_count, depth=recursion_depth
    )
    row = _allocate_row_workspace(layer_count, row_count, k)
    plan = _build_plan(receipt, base, row, row_count, k)
    return ComponentState(
        setup_seed=int(setup_seed),
        producer_epoch=int(producer_epoch),
        domain=DOMAIN,
        layer_ids=receipt.layer_ids,
        width=row_count,
        layers=layer_count,
        subset_rows=k,
        depth=recursion_depth,
        receipt_elapsed_s=receipt_elapsed,
        receipt=receipt,
        staged=staged,
        base=base,
        row=row,
        plan=plan,
    )


def _check_binding(state: ComponentState, full: object) -> None:
    plan = state.plan
    receipt = state.receipt
    if plan.receipt is not receipt or plan.row_owner is not state.row:
        raise ValueError("M235 setup plan ownership mismatch")
    if state.domain != DOMAIN or receipt.domain != DOMAIN:
        raise ValueError("M235 setup domain mismatch")
    if receipt.setup_seed != state.setup_seed:
        raise ValueError("M235 setup seed mismatch")
    if receipt.width != state.width or receipt.subset_rows != state.subset_rows:
        raise ValueError("M235 receipt integer metadata mismatch")
    if receipt.layer_ids != state.layer_ids or full.layer_ids != state.layer_ids:
        raise ValueError("M235 canonical layer binding mismatch")
    if state.staged.layer_ids != state.layer_ids:
        raise ValueError("M235 staged layer binding mismatch")
    if state.staged.producer_epoch != state.producer_epoch:
        raise ValueError("M235 staged epoch mismatch")
    if full.producer_epoch != state.producer_epoch:
        raise ValueError("M235 full-domain epoch mismatch")
    live = (
        state.base.aaaa,
        state.base.aaab,
        state.base.aabb,
        state.base.gram,
        state.base.p,
    )
    owned = (full.aaaa, full.aaab, full.aabb, full.gram, full.p)
    if any(left is not right for left, right in zip(live, owned, strict=True)):
        raise ValueError("M235 full-domain live object mismatch")


def subtract_setup_row_sketch_inplace(
    state: ComponentState,
    full: object,
):
    _check_binding(state, full)
    x = state.base
    q = state.plan
    selected = fnp.take_along_axis(x.scaled, q.selected_index3, axis=1)

    fnp.multiply(selected, selected, out=q.powers2)
    fnp.multiply(q.powers2, selected, out=q.powers3)
    fnp.matmul(q.powers_t, selected, out=state.row.cross)

    fnp.multiply(q.rho_col, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, q.c12, out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(x.gram, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, q.c8, out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.multiply(q.rho_col, q.rho_row, out=x.scratch)
    fnp.multiply(x.scratch, q.c4, out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)

    fnp.multiply(q.p_col, q.cross_a, out=x.scratch)
    fnp.multiply(x.scratch, q.c18g, out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(q.cross_a, q.p_row, out=x.scratch)
    fnp.multiply(x.scratch, q.c12g, out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.add(x.aabb, q.scratch_t, out=x.aabb)

    fnp.sum(q.powers3, axis=1, out=x.rho)
    fnp.multiply(q.rho_col, q.p_row, out=x.scratch)
    fnp.multiply(x.scratch, q.c6g, out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(q.cross_e, q.cm24g, out=q.cross_e)
    fnp.add(x.aaab, q.cross_e, out=x.aaab)

    fnp.matmul(q.powers2_t, q.powers2, out=x.gram)
    fnp.multiply(x.gram, q.cm24g, out=x.gram)
    fnp.add(x.aabb, x.gram, out=x.aabb)
    fnp.copyto(x.aaaa, q.aaab_diag)
    return x.aaaa, x.aaab, x.aabb


def workspace_arrays(state: ComponentState) -> tuple[object, ...]:
    """Hostile-audit inventory outside the timed correction."""

    return (
        state.staged.weight,
        state.staged.factor,
        state.base.scaled,
        state.base.gram,
        state.base.p,
        state.base.p2,
        state.base.rho,
        state.base.rho_p,
        state.base.scratch,
        state.base.aaab,
        state.base.aabb,
        state.base.aaaa,
        *state.base.level_products,
        state.row.powers,
        state.row.cross,
    )


__all__ = [
    "ComponentState",
    "DOMAIN",
    "ProductionPlan",
    "RowWorkspace",
    "SetupRowReceipt",
    "issue_setup_receipt",
    "setup_component",
    "subtract_setup_row_sketch_inplace",
    "workspace_arrays",
]
