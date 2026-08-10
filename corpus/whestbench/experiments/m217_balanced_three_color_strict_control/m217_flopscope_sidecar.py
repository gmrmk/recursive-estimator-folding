"""FlopScope 0.10 sidecar for M217's frozen colored self-Gram circuit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import flopscope.numpy as fnp


LAYERS = 31
WIDTH = 256
COLORS = 3
DEPTH = 3
DTYPE = fnp.float64


@dataclass(frozen=True)
class ColoredLayerInput:
    layer: int
    weight: object
    factor: object
    colors: object
    producer_epoch: int


@dataclass
class StagedInputs:
    weight: object
    factor: object
    permutation: object
    class_sizes: tuple[int, int, int]
    sorted_weight: object | None = None
    sorted_factor: object | None = None
    layer_ids: tuple[int, ...] | None = None
    producer_epoch: int | None = None
    color_packets: tuple[tuple[int, ...], ...] | None = None


@dataclass
class Workspace:
    scaled: object
    gram: object
    first: object
    rho: object
    pb: object
    pc: object
    singleton_product: object
    vector: object
    color_scratch: object
    color_scratch2: object
    plane_scratch: object
    aaab: object
    aabb: object
    aaaa: object
    level_products: tuple[object, ...]


def _sizes(width: int) -> tuple[int, int, int]:
    quotient, remainder = divmod(int(width), COLORS)
    return tuple(quotient + int(color < remainder) for color in range(COLORS))


def allocate_staged_inputs(layers: int = LAYERS, width: int = WIDTH) -> StagedInputs:
    sizes = _sizes(width)
    return StagedInputs(
        weight=fnp.empty((layers, width, width), dtype=DTYPE),
        factor=fnp.empty((layers, width), dtype=DTYPE),
        permutation=fnp.empty((layers, width), dtype=fnp.int64),
        class_sizes=sizes,
    )


def allocate_workspace(
    layers: int = LAYERS, width: int = WIDTH, depth: int = DEPTH
) -> Workspace:
    if depth < 0 or width % (2**depth):
        raise ValueError("width must be divisible by the recursive leaf count")
    block = max(_sizes(width))
    color_plane = lambda: fnp.empty((layers, COLORS, width, width), dtype=DTYPE)
    plane = lambda: fnp.empty((layers, width, width), dtype=DTYPE)
    color_vector = lambda: fnp.empty((layers, COLORS, width), dtype=DTYPE)
    vector = lambda: fnp.empty((layers, width), dtype=DTYPE)
    products = []
    for level in range(depth):
        nodes = 2**level
        half = width // (2 ** (level + 1))
        products.append(
            fnp.empty((layers, COLORS, nodes, half, half), dtype=DTYPE)
        )
    leaves = 2**depth
    leaf = width // leaves
    products.append(fnp.empty((layers, COLORS, leaves, leaf, leaf), dtype=DTYPE))
    return Workspace(
        scaled=fnp.empty((layers, COLORS, block, width), dtype=DTYPE),
        gram=color_plane(),
        first=color_vector(),
        rho=color_vector(),
        pb=color_vector(),
        pc=color_vector(),
        singleton_product=color_vector(),
        vector=color_vector(),
        color_scratch=color_plane(),
        color_scratch2=color_plane(),
        plane_scratch=plane(),
        aaab=plane(),
        aabb=plane(),
        aaaa=vector(),
        level_products=tuple(products),
    )


def stage_inputs(
    records: Sequence[ColoredLayerInput],
    staged: StagedInputs,
    *,
    expected_epoch: int,
) -> None:
    layers = int(staged.weight.shape[0])
    width = int(staged.weight.shape[-1])
    if len(records) != layers:
        raise ValueError("exactly one colored packet per source layer is required")
    expected_layers = tuple(range(1, layers + 1))
    if tuple(int(record.layer) for record in records) != expected_layers:
        raise ValueError("colored packets must be unique and canonically ordered")
    if any(int(record.producer_epoch) != int(expected_epoch) for record in records):
        raise ValueError("producer epoch mismatch")
    if len({id(record.weight) for record in records}) != layers:
        raise ValueError("weight objects must be layer-unique")
    if len({id(record.factor) for record in records}) != layers:
        raise ValueError("factor objects must be layer-unique")

    packets = []
    orders = []
    for record in records:
        if tuple(record.weight.shape) != (width, width):
            raise ValueError("weight shape mismatch")
        if tuple(record.factor.shape) != (width,):
            raise ValueError("factor shape mismatch")
        if str(record.weight.dtype) != "float64" or str(record.factor.dtype) != "float64":
            raise ValueError("M217 accepts float64 weight/factor inputs only")
        colors = tuple(int(value) for value in record.colors)
        if len(colors) != width or any(value not in (0, 1, 2) for value in colors):
            raise ValueError("invalid color packet")
        if tuple(colors.count(color) for color in range(COLORS)) != staged.class_sizes:
            raise ValueError("unbalanced color packet")
        packets.append(colors)
        orders.append(
            tuple(
                index
                for color in range(COLORS)
                for index, value in enumerate(colors)
                if value == color
            )
        )
    fnp.stack([record.weight for record in records], axis=0, out=staged.weight)
    fnp.stack([record.factor for record in records], axis=0, out=staged.factor)
    fnp.stack(orders, axis=0, out=staged.permutation)
    staged.sorted_weight = fnp.take_along_axis(
        staged.weight, staged.permutation[:, :, None], axis=1
    )
    staged.sorted_factor = fnp.take_along_axis(
        staged.factor, staged.permutation, axis=1
    )
    staged.layer_ids = expected_layers
    staged.producer_epoch = int(expected_epoch)
    staged.color_packets = tuple(packets)


def _level_fused_class_grams(staged: StagedInputs, x: Workspace, depth: int) -> None:
    u, gram = x.scaled, x.gram
    layers, _colors, rows, width = map(int, u.shape)
    if depth < 0 or width % (2**depth):
        raise ValueError("invalid recursion depth")
    for level in range(depth):
        nodes = 2**level
        block_width = width // nodes
        half = block_width // 2
        blocks = fnp.reshape(u, (layers, COLORS, rows, nodes, block_width))
        left = fnp.transpose(blocks[:, :, :, :, :half], (0, 1, 3, 4, 2))
        right = fnp.transpose(blocks[:, :, :, :, half:], (0, 1, 3, 2, 4))
        products = x.level_products[level]
        fnp.matmul(left, right, out=products)
        for node in range(nodes):
            start = node * block_width
            middle = start + half
            stop = start + block_width
            fnp.copyto(gram[:, :, start:middle, middle:stop], products[:, :, node])
            fnp.copyto(
                gram[:, :, middle:stop, start:middle],
                fnp.swapaxes(products[:, :, node], 2, 3),
            )
    leaves = 2**depth
    leaf = width // leaves
    blocks = fnp.reshape(u, (layers, COLORS, rows, leaves, leaf))
    left = fnp.transpose(blocks, (0, 1, 3, 4, 2))
    right = fnp.transpose(blocks, (0, 1, 3, 2, 4))
    products = x.level_products[depth]
    fnp.matmul(left, right, out=products)
    for node in range(leaves):
        start = node * leaf
        stop = start + leaf
        fnp.copyto(gram[:, :, start:stop, start:stop], products[:, :, node])


def compile_staged_stack(staged: StagedInputs, x: Workspace, depth: int = DEPTH):
    layers = int(staged.weight.shape[0])
    width = int(staged.weight.shape[-1])
    if staged.layer_ids != tuple(range(1, layers + 1)):
        raise ValueError("compile requires a complete canonical layer trace")
    if staged.producer_epoch is None or staged.color_packets is None:
        raise ValueError("compile requires bound color packets")
    if staged.sorted_weight is None or staged.sorted_factor is None:
        raise ValueError("compile requires materialized color-sorted inputs")
    start = 0
    block_rows = int(x.scaled.shape[2])
    for color, count in enumerate(staged.class_sizes):
        stop = start + count
        fnp.multiply(
            staged.sorted_factor[:, start:stop, None],
            staged.sorted_weight[:, start:stop],
            out=x.scaled[:, color, :count],
        )
        if count < block_rows:
            fnp.copyto(x.scaled[:, color, count:], fnp.float64(0.0))
        start = stop
    fnp.sum(x.scaled, axis=2, out=x.first)
    _level_fused_class_grams(staged, x, depth)
    fnp.copyto(x.rho, fnp.diagonal(x.gram, axis1=2, axis2=3))
    n0, n1, n2 = staged.class_sizes
    probability = fnp.float64(
        (6.0 * n0 * n1 * n2) / (width * (width - 1) * (width - 2))
    )
    aaab_scale = fnp.float64(-6.0) / probability
    aabb_scale = fnp.float64(-4.0) / probability
    fnp.take(x.first, (1, 0, 0), axis=1, out=x.pb)
    fnp.take(x.first, (2, 2, 1), axis=1, out=x.pc)
    fnp.multiply(x.pb, x.pc, out=x.singleton_product)

    # Vectorize the three repeated-role colors as one batch axis.
    fnp.multiply(
        x.singleton_product[:, :, :, None], x.gram, out=x.color_scratch
    )
    fnp.multiply(x.color_scratch, fnp.float64(2.0), out=x.color_scratch)
    fnp.multiply(x.rho, x.pc, out=x.vector)
    fnp.multiply(
        x.vector[:, :, :, None], x.pb[:, :, None, :], out=x.color_scratch2
    )
    fnp.add(x.color_scratch, x.color_scratch2, out=x.color_scratch)
    fnp.multiply(x.rho, x.pb, out=x.vector)
    fnp.multiply(
        x.vector[:, :, :, None], x.pc[:, :, None, :], out=x.color_scratch2
    )
    fnp.add(x.color_scratch, x.color_scratch2, out=x.color_scratch)
    fnp.sum(x.color_scratch, axis=1, out=x.aaab)
    fnp.multiply(x.aaab, aaab_scale, out=x.aaab)

    fnp.multiply(
        x.rho[:, :, :, None],
        x.singleton_product[:, :, None, :],
        out=x.color_scratch,
    )
    fnp.multiply(
        x.singleton_product[:, :, :, None],
        x.rho[:, :, None, :],
        out=x.color_scratch2,
    )
    fnp.add(x.color_scratch, x.color_scratch2, out=x.color_scratch)
    fnp.multiply(x.pb[:, :, :, None], x.gram, out=x.color_scratch2)
    fnp.multiply(
        x.color_scratch2, x.pc[:, :, None, :], out=x.color_scratch2
    )
    fnp.multiply(x.color_scratch2, fnp.float64(2.0), out=x.color_scratch2)
    fnp.add(x.color_scratch, x.color_scratch2, out=x.color_scratch)
    fnp.multiply(x.pc[:, :, :, None], x.gram, out=x.color_scratch2)
    fnp.multiply(
        x.color_scratch2, x.pb[:, :, None, :], out=x.color_scratch2
    )
    fnp.multiply(x.color_scratch2, fnp.float64(2.0), out=x.color_scratch2)
    fnp.add(x.color_scratch, x.color_scratch2, out=x.color_scratch)
    fnp.sum(x.color_scratch, axis=1, out=x.aabb)
    fnp.multiply(x.aabb, aabb_scale, out=x.aabb)

    fnp.copyto(x.plane_scratch, fnp.swapaxes(x.aabb, 1, 2))
    fnp.add(x.aabb, x.plane_scratch, out=x.aabb)
    fnp.multiply(x.aabb, fnp.float64(0.5), out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab, axis1=1, axis2=2))
    return x.aaaa, x.aaab, x.aabb, x.gram, x.first


def allocation_ledger(staged: StagedInputs, x: Workspace) -> dict[str, object]:
    named = {
        "staged_weight": staged.weight,
        "staged_factor": staged.factor,
        "staged_permutation": staged.permutation,
        "scaled": x.scaled,
        "gram": x.gram,
        "first": x.first,
        "rho": x.rho,
        "pb": x.pb,
        "pc": x.pc,
        "singleton_product": x.singleton_product,
        "vector": x.vector,
        "color_scratch": x.color_scratch,
        "color_scratch2": x.color_scratch2,
        "plane_scratch": x.plane_scratch,
        "aaab": x.aaab,
        "aabb": x.aabb,
        "aaaa": x.aaaa,
    }
    if staged.sorted_weight is not None:
        named["sorted_weight"] = staged.sorted_weight
    if staged.sorted_factor is not None:
        named["sorted_factor"] = staged.sorted_factor
    for index, value in enumerate(x.level_products):
        named[f"level_product_{index}"] = value
    items = {
        name: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "bytes": int(value.nbytes),
        }
        for name, value in named.items()
    }
    total = sum(item["bytes"] for item in items.values())
    return {
        "arrays": items,
        "persistent_bytes": total,
        "persistent_mib": total / (1024.0 * 1024.0),
        "rank3_coefficient_arrays": 0,
        "color_packet_count": 0 if staged.color_packets is None else len(staged.color_packets),
    }


__all__ = [
    "ColoredLayerInput",
    "allocate_staged_inputs",
    "allocate_workspace",
    "stage_inputs",
    "compile_staged_stack",
    "allocation_ledger",
]
