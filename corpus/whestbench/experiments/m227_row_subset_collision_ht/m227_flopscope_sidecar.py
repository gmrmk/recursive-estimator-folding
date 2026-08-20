"""FlopScope 0.10.0 sidecar for frozen M227 row-HT subtraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import flopscope.numpy as fnp
import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
    BASE / "m215_rankone_collision_correction",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m215_flopscope_sidecar import (  # noqa: E402
    FullDomainReceipt,
    issue_full_domain_receipt,
)
from m227_row_subset_collision_ht import (  # noqa: E402
    compile_row_sketch_collision_source_numpy as numpy_row_oracle,
)


WIDTH = 256
LAYERS = 31
SUBSET_ROWS = 32
DTYPE = fnp.float64


@dataclass
class RowWorkspace:
    """Owned selected powers and A/E cross-products; D reuses live B."""

    powers: object
    cross: object
    subset_rows: int
    selected_values: object | None = None
    rank_receipt: object | None = None


@dataclass(frozen=True)
class NativeRowReceipt:
    """The full priority rank packet and selected labelled rows."""

    layer_ids: tuple[int, ...]
    producer_epoch: int
    subset_rows: int
    rank_order: object
    selected: object


def allocate_row_workspace(
    layers: int = LAYERS,
    width: int = WIDTH,
    subset_rows: int = SUBSET_ROWS,
) -> RowWorkspace:
    k = int(subset_rows)
    if layers < 1 or width < 3 or k < 1 or k >= width:
        raise ValueError("invalid M227 workspace dimensions")
    return RowWorkspace(
        powers=fnp.empty((2, layers, k, width), dtype=DTYPE),
        cross=fnp.empty((2, layers, width, width), dtype=DTYPE),
        subset_rows=k,
    )


def allocation_ledger(staged, base_workspace, row_workspace: RowWorkspace) -> dict[str, object]:
    layers, width = int(staged.weight.shape[0]), int(staged.weight.shape[-1])
    k = int(row_workspace.subset_rows)
    if tuple(row_workspace.powers.shape) != (2, layers, k, width):
        raise ValueError("M227 powers workspace shape mismatch")
    if tuple(row_workspace.cross.shape) != (2, layers, width, width):
        raise ValueError("M227 cross workspace shape mismatch")
    arrays = {
        "weight": staged.weight,
        "factor": staged.factor,
        "scaled_S": base_workspace.scaled,
        "live_B_then_Dhat": base_workspace.gram,
        "p": base_workspace.p,
        "p2": base_workspace.p2,
        "rho_then_that": base_workspace.rho,
        "rho_p": base_workspace.rho_p,
        "scratch": base_workspace.scratch,
        "strict_aaab": base_workspace.aaab,
        "strict_aabb": base_workspace.aabb,
        "strict_aaaa": base_workspace.aaaa,
        "selected_powers_S2_S3": row_workspace.powers,
        "cross_Ahat_Ehat": row_workspace.cross,
    }
    for index, value in enumerate(base_workspace.level_products):
        arrays[f"M212_level_product_{index}"] = value
    items = {
        name: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "elements": int(value.size),
            "bytes": int(value.nbytes),
        }
        for name, value in arrays.items()
    }
    m227_owned_names = {"selected_powers_S2_S3", "cross_Ahat_Ehat"}
    visible_bytes = sum(
        item["bytes"] for name, item in items.items() if name not in m227_owned_names
    )
    selected_bytes = layers * k * width * 8
    rank_bytes = layers * width * 8
    incremental_bytes = (
        int(row_workspace.powers.nbytes)
        + int(row_workspace.cross.nbytes)
        + selected_bytes
        + rank_bytes
    )
    return {
        "arrays": items,
        "array_count_before_dynamic_receipt": len(items),
        "selected_values_bytes": selected_bytes,
        "rank_receipt_bytes": rank_bytes,
        "transient_priority_bytes": rank_bytes,
        "incremental_persistent_bytes": incremental_bytes,
        "incremental_persistent_mib": incremental_bytes / (1024.0 * 1024.0),
        "incremental_nominal_peak_mib": (incremental_bytes + rank_bytes)
        / (1024.0 * 1024.0),
        "m212_visible_bytes": visible_bytes,
        "m212_visible_mib": visible_bytes / (1024.0 * 1024.0),
        "m212_m227_persistent_mib": (visible_bytes + incremental_bytes)
        / (1024.0 * 1024.0),
        "rank3_coefficient_arrays": 0,
        "sampled_Bhat_or_rhohat_arrays": 0,
    }


def _validate_live_binding(
    staged,
    workspace,
    row_workspace: RowWorkspace,
    receipt: FullDomainReceipt,
    subset_rows: int,
) -> tuple[int, int, int]:
    layers, width = int(staged.weight.shape[0]), int(staged.weight.shape[-1])
    k = int(subset_rows)
    expected_ids = tuple(range(1, layers + 1))
    if staged.layer_ids != expected_ids or receipt.layer_ids != expected_ids:
        raise ValueError("M227 requires canonical layer order")
    if staged.producer_epoch is None or int(staged.producer_epoch) != int(receipt.producer_epoch):
        raise ValueError("M227 producer epoch mismatch")
    if k != int(row_workspace.subset_rows) or k < 1 or k >= width:
        raise ValueError("M227 subset/workspace mismatch")
    live = (workspace.aaaa, workspace.aaab, workspace.aabb, workspace.gram, workspace.p)
    bound = (receipt.aaaa, receipt.aaab, receipt.aabb, receipt.gram, receipt.p)
    if any(left is not right for left, right in zip(live, bound, strict=True)):
        raise ValueError("M227 receipt no longer owns the live M212 objects")
    if tuple(row_workspace.powers.shape) != (2, layers, k, width):
        raise ValueError("M227 powers workspace shape mismatch")
    if tuple(row_workspace.cross.shape) != (2, layers, width, width):
        raise ValueError("M227 cross workspace shape mismatch")
    values = (
        staged.weight,
        staged.factor,
        workspace.scaled,
        workspace.gram,
        workspace.p,
        workspace.rho,
        workspace.scratch,
        workspace.aaab,
        workspace.aabb,
        workspace.aaaa,
        row_workspace.powers,
        row_workspace.cross,
    )
    if any(str(value.dtype) != "float64" for value in values):
        raise ValueError("M227 requires a fully float64 live stack")
    return layers, width, k


def _reject_priority_ties(priorities) -> None:
    """Fail closed through scalar control flow, charged as residual wall."""

    for row in np.asarray(priorities).tolist():
        if len(set(row)) != len(row):
            raise ValueError("M227 priority ties are forbidden")


def subtract_row_sketch_inplace(
    staged,
    workspace,
    row_workspace: RowWorkspace,
    receipt: FullDomainReceipt,
    *,
    seed: int,
    subset_rows: int = SUBSET_ROWS,
):
    """Subtract one unbiased row-HT collision draw from live M212 slots."""

    layers, width, k = _validate_live_binding(
        staged, workspace, row_workspace, receipt, subset_rows
    )
    x = workspace
    r = row_workspace

    generator = fnp.random.default_rng(int(seed))
    priorities = generator.random((layers, width), dtype=DTYPE)
    rank_order = fnp.argsort(priorities, axis=1, kind="stable")
    _reject_priority_ties(priorities)
    selected_labels = rank_order[:, :k]
    selected = fnp.take_along_axis(
        x.scaled, selected_labels[:, :, None], axis=1
    )
    r.selected_values = selected
    r.rank_receipt = rank_order

    fnp.multiply(selected, selected, out=r.powers[0])
    fnp.multiply(r.powers[0], selected, out=r.powers[1])
    fnp.matmul(fnp.transpose(r.powers, (0, 1, 3, 2)), selected, out=r.cross)

    # Exact live-B terms are integrated, never sketched.
    fnp.multiply(x.rho[:, :, None], x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(12.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)

    fnp.multiply(x.gram, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(8.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)

    fnp.multiply(x.rho[:, :, None], x.rho[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(4.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)

    scale = float(width) / float(k)
    fnp.multiply(x.p[:, :, None], r.cross[0], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(18.0 * scale), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)

    fnp.multiply(r.cross[0], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(12.0 * scale), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.add(x.aabb, fnp.swapaxes(x.scratch, 1, 2), out=x.aabb)

    fnp.sum(r.powers[1], axis=1, out=x.rho)
    fnp.multiply(x.rho[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(6.0 * scale), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(r.cross[1], fnp.float64(-24.0 * scale), out=r.cross[1])
    fnp.add(x.aaab, r.cross[1], out=x.aaab)

    fnp.matmul(
        fnp.transpose(r.powers[0], (0, 2, 1)),
        r.powers[0],
        out=x.gram,
    )
    fnp.multiply(x.gram, fnp.float64(-24.0 * scale), out=x.gram)
    fnp.add(x.aabb, x.gram, out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab, axis1=1, axis2=2))

    row_receipt = NativeRowReceipt(
        layer_ids=tuple(range(1, layers + 1)),
        producer_epoch=int(staged.producer_epoch),
        subset_rows=k,
        rank_order=rank_order,
        selected=selected_labels,
    )
    return (x.aaaa, x.aaab, x.aabb), row_receipt


__all__ = [
    "FullDomainReceipt",
    "NativeRowReceipt",
    "RowWorkspace",
    "allocate_row_workspace",
    "allocation_ledger",
    "issue_full_domain_receipt",
    "numpy_row_oracle",
    "subtract_row_sketch_inplace",
]
