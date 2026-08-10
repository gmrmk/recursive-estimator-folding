"""FlopScope 0.10.0 sidecar for the frozen M209 target-shape schedule."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import flopscope.numpy as fnp


WIDTH = 256
LAYERS = 31
DEPTH = 3
DTYPE = fnp.float64


@dataclass
class StagedInputs:
    weight: object
    factor: object
    layer_ids: tuple[int, ...] | None = None
    producer_epoch: int | None = None


@dataclass(frozen=True)
class LayerInput:
    """One M179-derived factor bound to its actual source-layer weight."""

    layer: int
    weight: object
    factor: object
    producer_epoch: int


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


def allocate_staged_inputs(layers: int = LAYERS, width: int = WIDTH) -> StagedInputs:
    return StagedInputs(
        weight=fnp.empty((layers, width, width), dtype=DTYPE),
        factor=fnp.empty((layers, width), dtype=DTYPE),
    )


def allocate_workspace(layers: int = LAYERS, width: int = WIDTH) -> Workspace:
    plane = lambda: fnp.empty((layers, width, width), dtype=DTYPE)
    vector = lambda: fnp.empty((layers, width), dtype=DTYPE)
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
    )


def allocation_ledger(staged: StagedInputs, workspace: Workspace) -> dict[str, object]:
    arrays = {
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
    items = {
        name: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "elements": int(value.size),
            "bytes": int(value.nbytes),
        }
        for name, value in arrays.items()
    }
    total_bytes = sum(item["bytes"] for item in items.values())
    return {
        "arrays": items,
        "array_count": len(items),
        "persistent_bytes": total_bytes,
        "persistent_mib": total_bytes / (1024.0 * 1024.0),
        "rank3_coefficient_arrays": 0,
    }


def stage_inputs(
    records: Sequence[LayerInput],
    staged: StagedInputs,
    *,
    expected_epoch: int,
) -> None:
    """Validate and materialize a complete ordered layer trace.

    Validation deliberately happens before the charged copies: a refused
    layer binding cannot mutate the staged buffers and then masquerade as a
    valid trace.
    """

    layers, width = staged.weight.shape[0], staged.weight.shape[1]
    if len(records) != layers:
        raise ValueError("exactly one bound record per staged layer is required")
    expected_ids = tuple(range(1, layers + 1))
    if tuple(int(record.layer) for record in records) != expected_ids:
        raise ValueError("layer records must be unique and in canonical order")
    if any(int(record.producer_epoch) != int(expected_epoch) for record in records):
        raise ValueError("producer epoch mismatch")
    weights = [record.weight for record in records]
    factors = [record.factor for record in records]
    if len({id(value) for value in weights}) != layers or len({id(value) for value in factors}) != layers:
        raise ValueError("duplicated weight/factor object across layer records")
    for weight, factor in zip(weights, factors, strict=True):
        if tuple(weight.shape) != (width, width) or tuple(factor.shape) != (width,):
            raise ValueError("bound weight/factor shape mismatch")
        if str(weight.dtype) != "float64" or str(factor.dtype) != "float64":
            raise ValueError("M209 accepts float64 layer inputs only")
    fnp.stack(weights, axis=0, out=staged.weight)
    fnp.stack(factors, axis=0, out=staged.factor)
    staged.layer_ids = expected_ids
    staged.producer_epoch = int(expected_epoch)


def _recursive_gram(staged: StagedInputs, workspace: Workspace, depth: int) -> None:
    width = int(staged.weight.shape[-1])
    if depth < 0 or width % (2**depth):
        raise ValueError("width must be divisible by 2**depth")
    u = workspace.scaled
    b = workspace.gram

    def visit(start: int, stop: int, remaining: int) -> None:
        if remaining == 0:
            block = u[:, :, start:stop]
            fnp.matmul(
                fnp.swapaxes(block, 1, 2),
                block,
                out=b[:, start:stop, start:stop],
            )
            return
        middle = (start + stop) // 2
        left = u[:, :, start:middle]
        right = u[:, :, middle:stop]
        fnp.matmul(
            fnp.swapaxes(left, 1, 2),
            right,
            out=b[:, start:middle, middle:stop],
        )
        fnp.copyto(
            b[:, middle:stop, start:middle],
            fnp.swapaxes(b[:, start:middle, middle:stop], 1, 2),
        )
        visit(start, middle, remaining - 1)
        visit(middle, stop, remaining - 1)

    visit(0, width, depth)


def compile_staged_stack(
    staged: StagedInputs, workspace: Workspace, depth: int = DEPTH
):
    """Compile all unchanged M205 control slots, fully billed and preallocated."""

    if staged.layer_ids != tuple(range(1, staged.weight.shape[0] + 1)):
        raise ValueError("compile requires a completely bound canonical layer trace")
    if staged.producer_epoch is None:
        raise ValueError("compile requires a bound producer epoch")
    x = workspace
    fnp.multiply(staged.factor[:, :, None], staged.weight, out=x.scaled)
    fnp.sum(x.scaled, axis=1, out=x.p)
    _recursive_gram(staged, x, depth)
    fnp.copyto(x.rho, fnp.diagonal(x.gram, axis1=1, axis2=2))
    fnp.multiply(x.p, x.p, out=x.p2)

    # aaab = -6 * [diag(p^2) B + (rho*p) p^T]
    fnp.multiply(x.p2[:, :, None], x.gram, out=x.aaab)
    fnp.multiply(x.rho, x.p, out=x.rho_p)
    fnp.multiply(x.rho_p[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(x.aaab, fnp.float64(-6.0), out=x.aaab)

    # aabb = -2 * [rho p2^T + p2 rho^T + 4 diag(p) B diag(p)]
    fnp.multiply(x.rho[:, :, None], x.p2[:, None, :], out=x.aabb)
    fnp.add(x.aabb, fnp.swapaxes(x.aabb, 1, 2), out=x.aabb)
    fnp.multiply(x.p[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(4.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.multiply(x.aabb, fnp.float64(-2.0), out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab, axis1=1, axis2=2))
    return x.aaaa, x.aaab, x.aabb, x.gram, x.p
