"""FlopScope implementation of M210's fixed same-level Gram fusion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import flopscope.numpy as fnp


HERE = Path(__file__).resolve().parent
M209 = HERE.parent / "m209_batched_recursive_gram_control"
if str(M209) not in sys.path:
    sys.path.insert(0, str(M209))

from m209_flopscope_sidecar import (  # noqa: E402
    LayerInput,
    StagedInputs,
    allocate_staged_inputs,
    stage_inputs,
)


WIDTH = 256
LAYERS = 31
DEPTH = 3
DTYPE = fnp.float64


@dataclass
class Workspace:
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


def allocate_workspace(
    layers: int = LAYERS, width: int = WIDTH, depth: int = DEPTH
) -> Workspace:
    if depth < 0 or width % (2**depth):
        raise ValueError("width must be divisible by 2**depth")
    plane = lambda: fnp.empty((layers, width, width), dtype=DTYPE)
    vector = lambda: fnp.empty((layers, width), dtype=DTYPE)
    products = []
    for level in range(depth):
        nodes = 2**level
        half = width // (2 ** (level + 1))
        products.append(fnp.empty((layers, nodes, half, half), dtype=DTYPE))
    leaves = 2**depth
    leaf_width = width // leaves
    products.append(fnp.empty((layers, leaves, leaf_width, leaf_width), dtype=DTYPE))
    return Workspace(
        scaled=plane(),
        gram=plane(),
        p=vector(),
        p2=vector(),
        rho=vector(),
        rho_p=vector(),
        scratch=plane(),
        aaab=plane(),
        aabb=plane(),
        aaaa=vector(),
        level_products=tuple(products),
    )


def allocation_ledger(staged: StagedInputs, workspace: Workspace) -> dict[str, object]:
    named = {
        "weight": staged.weight,
        "factor": staged.factor,
        "scaled": workspace.scaled,
        "gram": workspace.gram,
        "p": workspace.p,
        "p2": workspace.p2,
        "rho": workspace.rho,
        "rho_p": workspace.rho_p,
        "scratch": workspace.scratch,
        "aaab": workspace.aaab,
        "aabb": workspace.aabb,
        "aaaa": workspace.aaaa,
    }
    for index, value in enumerate(workspace.level_products):
        named[f"level_product_{index}"] = value
    items = {
        name: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "elements": int(value.size),
            "bytes": int(value.nbytes),
        }
        for name, value in named.items()
    }
    total = sum(item["bytes"] for item in items.values())
    return {
        "arrays": items,
        "array_count": len(items),
        "persistent_bytes": total,
        "persistent_mib": total / (1024.0 * 1024.0),
        "rank3_coefficient_arrays": 0,
    }


def _level_fused_gram(staged: StagedInputs, workspace: Workspace, depth: int) -> None:
    u, b = workspace.scaled, workspace.gram
    layers, width = int(u.shape[0]), int(u.shape[-1])
    if depth < 0 or width % (2**depth):
        raise ValueError("invalid M210 depth")

    for level in range(depth):
        nodes = 2**level
        block_width = width // nodes
        half = block_width // 2
        blocks = fnp.reshape(u, (layers, width, nodes, block_width))
        left = fnp.transpose(blocks[:, :, :, :half], (0, 2, 3, 1))
        right = fnp.transpose(blocks[:, :, :, half:], (0, 2, 1, 3))
        products = workspace.level_products[level]
        fnp.matmul(left, right, out=products)
        for node in range(nodes):
            start = node * block_width
            middle = start + half
            stop = start + block_width
            fnp.copyto(b[:, start:middle, middle:stop], products[:, node])
            fnp.copyto(
                b[:, middle:stop, start:middle],
                fnp.swapaxes(products[:, node], 1, 2),
            )

    leaves = 2**depth
    leaf_width = width // leaves
    blocks = fnp.reshape(u, (layers, width, leaves, leaf_width))
    left = fnp.transpose(blocks, (0, 2, 3, 1))
    right = fnp.transpose(blocks, (0, 2, 1, 3))
    products = workspace.level_products[depth]
    fnp.matmul(left, right, out=products)
    for node in range(leaves):
        start = node * leaf_width
        stop = start + leaf_width
        fnp.copyto(b[:, start:stop, start:stop], products[:, node])


def compile_staged_stack(
    staged: StagedInputs, workspace: Workspace, depth: int = DEPTH
):
    if staged.layer_ids != tuple(range(1, staged.weight.shape[0] + 1)):
        raise ValueError("compile requires canonical bound layers")
    if staged.producer_epoch is None:
        raise ValueError("compile requires producer epoch")
    x = workspace
    fnp.multiply(staged.factor[:, :, None], staged.weight, out=x.scaled)
    fnp.sum(x.scaled, axis=1, out=x.p)
    _level_fused_gram(staged, x, depth)
    fnp.copyto(x.rho, fnp.diagonal(x.gram, axis1=1, axis2=2))
    fnp.multiply(x.p, x.p, out=x.p2)
    fnp.multiply(x.p2[:, :, None], x.gram, out=x.aaab)
    fnp.multiply(x.rho, x.p, out=x.rho_p)
    fnp.multiply(x.rho_p[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(x.aaab, fnp.float64(-6.0), out=x.aaab)
    fnp.multiply(x.rho[:, :, None], x.p2[:, None, :], out=x.aabb)
    fnp.add(x.aabb, fnp.swapaxes(x.aabb, 1, 2), out=x.aabb)
    fnp.multiply(x.p[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(4.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.multiply(x.aabb, fnp.float64(-2.0), out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab, axis1=1, axis2=2))
    return x.aaaa, x.aaab, x.aabb, x.gram, x.p


__all__ = [
    "LayerInput",
    "allocate_staged_inputs",
    "allocate_workspace",
    "allocation_ledger",
    "stage_inputs",
    "compile_staged_stack",
]
