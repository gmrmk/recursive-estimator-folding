"""FlopScope 0.10.0 sidecar for M215's frozen collision subtraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import flopscope.numpy as fnp


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (
    HERE,
    BASE / "m210_level_fused_recursive_gram",
    BASE / "m212_backend_packed_explicit_symmetry",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m215_rankone_collision_correction import (  # noqa: E402
    compile_rank_one_collision_source_numpy as numpy_collision_oracle,
)


WIDTH = 256
LAYERS = 31
DEPTH = 3
DTYPE = fnp.float64


@dataclass
class CollisionWorkspace:
    """Four declared planes: `[S^2,S^3]` and `[A,E]`."""

    powers: object
    cross: object


@dataclass(frozen=True)
class FullDomainReceipt:
    layer_ids: tuple[int, ...]
    producer_epoch: int
    aaaa: object
    aaab: object
    aabb: object
    gram: object
    p: object


def allocate_collision_workspace(
    layers: int = LAYERS, width: int = WIDTH
) -> CollisionWorkspace:
    shape = (2, layers, width, width)
    return CollisionWorkspace(
        powers=fnp.empty(shape, dtype=DTYPE),
        cross=fnp.empty(shape, dtype=DTYPE),
    )


def allocation_ledger(staged, base_workspace, collision_workspace) -> dict[str, object]:
    arrays = {
        "weight": staged.weight,
        "factor": staged.factor,
        "scaled_S": base_workspace.scaled,
        "live_B_then_D": base_workspace.gram,
        "p": base_workspace.p,
        "p2": base_workspace.p2,
        "rho_then_t": base_workspace.rho,
        "rho_p": base_workspace.rho_p,
        "scratch": base_workspace.scratch,
        "strict_aaab": base_workspace.aaab,
        "strict_aabb": base_workspace.aabb,
        "strict_aaaa": base_workspace.aaaa,
        "powers_S2_S3": collision_workspace.powers,
        "cross_A_E": collision_workspace.cross,
    }
    for index, value in enumerate(base_workspace.level_products):
        arrays[f"D_level_product_{index}"] = value
    items = {
        name: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "elements": int(value.size),
            "bytes": int(value.nbytes),
        }
        for name, value in arrays.items()
    }
    total = sum(item["bytes"] for item in items.values())
    correction_bytes = int(collision_workspace.powers.nbytes + collision_workspace.cross.nbytes)
    return {
        "arrays": items,
        "array_count": len(items),
        "persistent_bytes_visible_to_m215": total,
        "persistent_mib_visible_to_m215": total / (1024.0 * 1024.0),
        "incremental_collision_bytes": correction_bytes,
        "incremental_collision_mib": correction_bytes / (1024.0 * 1024.0),
        "rank3_coefficient_arrays": 0,
    }


def issue_full_domain_receipt(staged, workspace, outputs) -> FullDomainReceipt:
    expected_ids = tuple(range(1, int(staged.weight.shape[0]) + 1))
    if staged.layer_ids != expected_ids or staged.producer_epoch is None:
        raise ValueError("M215 receipt requires a canonical bound M212 stack")
    if len(outputs) < 5:
        raise ValueError("M212 output tuple is incomplete")
    expected = (workspace.aaaa, workspace.aaab, workspace.aabb, workspace.gram, workspace.p)
    if any(got is not want for got, want in zip(outputs[:5], expected, strict=True)):
        raise ValueError("receipt outputs are not the live M212 workspace")
    return FullDomainReceipt(
        layer_ids=expected_ids,
        producer_epoch=int(staged.producer_epoch),
        aaaa=workspace.aaaa,
        aaab=workspace.aaab,
        aabb=workspace.aabb,
        gram=workspace.gram,
        p=workspace.p,
    )


def _validate_live_binding(staged, workspace, collision_workspace, receipt, depth: int) -> None:
    layers, width = int(staged.weight.shape[0]), int(staged.weight.shape[-1])
    expected_ids = tuple(range(1, layers + 1))
    if staged.layer_ids != expected_ids or receipt.layer_ids != expected_ids:
        raise ValueError("M215 requires canonical layer order")
    if staged.producer_epoch is None or int(staged.producer_epoch) != int(receipt.producer_epoch):
        raise ValueError("M215 producer epoch mismatch")
    if depth < 0 or width % (2**depth):
        raise ValueError("M215 width must be divisible by 2**depth")
    live = (workspace.aaaa, workspace.aaab, workspace.aabb, workspace.gram, workspace.p)
    bound = (receipt.aaaa, receipt.aaab, receipt.aabb, receipt.gram, receipt.p)
    if any(left is not right for left, right in zip(live, bound, strict=True)):
        raise ValueError("M215 receipt no longer owns the live M212 objects")
    expected_planes = (2, layers, width, width)
    if tuple(collision_workspace.powers.shape) != expected_planes or tuple(collision_workspace.cross.shape) != expected_planes:
        raise ValueError("M215 collision workspace shape mismatch")
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
        collision_workspace.powers,
        collision_workspace.cross,
    )
    if any(str(value.dtype) != "float64" for value in values):
        raise ValueError("M215 requires a fully float64 live stack")


def _symmetric_gram_from_power(source, output, level_products, depth: int) -> None:
    """M212's same-level recursion applied to the live `S^2` plane."""

    layers, width = int(source.shape[0]), int(source.shape[-1])
    for level in range(depth):
        nodes = 2**level
        block_width = width // nodes
        half = block_width // 2
        blocks = fnp.reshape(source, (layers, width, nodes, block_width))
        left = fnp.transpose(blocks[:, :, :, :half], (0, 2, 3, 1))
        right = fnp.transpose(blocks[:, :, :, half:], (0, 2, 1, 3))
        products = level_products[level]
        fnp.matmul(left, right, out=products)
        for node in range(nodes):
            start = node * block_width
            middle = start + half
            stop = start + block_width
            fnp.copyto(output[:, start:middle, middle:stop], products[:, node])
            fnp.copyto(
                output[:, middle:stop, start:middle],
                fnp.swapaxes(products[:, node], 1, 2),
            )

    leaves = 2**depth
    leaf_width = width // leaves
    blocks = fnp.reshape(source, (layers, width, leaves, leaf_width))
    left = fnp.transpose(blocks, (0, 2, 3, 1))
    right = fnp.transpose(blocks, (0, 2, 1, 3))
    products = level_products[depth]
    fnp.matmul(left, right, out=products)
    for node in range(leaves):
        start = node * leaf_width
        stop = start + leaf_width
        fnp.copyto(output[:, start:stop, start:stop], products[:, node])


def subtract_collisions_inplace(
    staged,
    workspace,
    collision_workspace: CollisionWorkspace,
    receipt: FullDomainReceipt,
    *,
    depth: int = DEPTH,
):
    """Convert live complete-domain M212 slots to strict-distinct slots."""

    _validate_live_binding(staged, workspace, collision_workspace, receipt, depth)
    x = workspace
    c = collision_workspace

    # Preserve both left operands, then compute A=(S^2)^T S and E=(S^3)^T S
    # in one shape-billed broadcast-batched matmul.
    fnp.multiply(x.scaled, x.scaled, out=c.powers[0])
    fnp.multiply(c.powers[0], x.scaled, out=c.powers[1])
    fnp.matmul(fnp.transpose(c.powers, (0, 1, 3, 2)), x.scaled, out=c.cross)

    # Subtract Ccol's live-B terms: +12 diag(rho)B, +8 B hadamard B,
    # and +4 rho rho^T in the strict source.
    fnp.multiply(x.rho[:, :, None], x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(12.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)

    fnp.multiply(x.gram, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(8.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)

    fnp.multiply(x.rho[:, :, None], x.rho[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(4.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)

    # A terms: +18 diag(p)A and +12[A diag(p)+diag(p)A^T].
    fnp.multiply(x.p[:, :, None], c.cross[0], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(18.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)

    fnp.multiply(c.cross[0], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(12.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.add(x.aabb, fnp.swapaxes(x.scratch, 1, 2), out=x.aabb)

    # E/t terms: +6 t p^T -24E.
    fnp.sum(c.powers[1], axis=1, out=x.rho)
    fnp.multiply(x.rho[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(6.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(c.cross[1], fnp.float64(-24.0), out=c.cross[1])
    fnp.add(x.aaab, c.cross[1], out=x.aaab)

    # D term: compute the fourth-power Gram after B is dead, then add -24D.
    _symmetric_gram_from_power(c.powers[0], x.gram, x.level_products, depth)
    fnp.multiply(x.gram, fnp.float64(-24.0), out=x.gram)
    fnp.add(x.aabb, x.gram, out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab, axis1=1, axis2=2))
    return x.aaaa, x.aaab, x.aabb


__all__ = [
    "CollisionWorkspace",
    "FullDomainReceipt",
    "allocate_collision_workspace",
    "allocation_ledger",
    "issue_full_domain_receipt",
    "numpy_collision_oracle",
    "subtract_collisions_inplace",
]
