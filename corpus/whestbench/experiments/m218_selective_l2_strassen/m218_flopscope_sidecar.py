"""FlopScope 0.10.0 implementation of M218's selective L2 Strassen fold."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import flopscope.numpy as fnp


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for path in (BASE / "m215_rankone_collision_correction",):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from m215_flopscope_sidecar import (  # noqa: E402
    _symmetric_gram_from_power,
    _validate_live_binding,
)


WIDTH = 256
LAYERS = 31
STRASSEN_DEPTH = 2
D_DEPTH = 3
DTYPE = fnp.float64


@dataclass
class StrassenCollisionWorkspace:
    powers: object
    cross: object
    level: object
    leaf_left: object
    leaf_right: object
    leaf_product: object


def allocate_strassen_collision_workspace(
    layers: int = LAYERS, width: int = WIDTH
) -> StrassenCollisionWorkspace:
    if width < 4 or width % 4:
        raise ValueError("M218 width must be divisible by four")
    half, quarter = width // 2, width // 4
    return StrassenCollisionWorkspace(
        powers=fnp.empty((2, layers, width, width), dtype=DTYPE),
        cross=fnp.empty((2, layers, width, width), dtype=DTYPE),
        level=fnp.empty((7, layers, half, half), dtype=DTYPE),
        leaf_left=fnp.empty((7, 7, layers, quarter, quarter), dtype=DTYPE),
        leaf_right=fnp.empty((7, 7, layers, quarter, quarter), dtype=DTYPE),
        leaf_product=fnp.empty((7, 7, layers, quarter, quarter), dtype=DTYPE),
    )


def allocation_ledger(staged, base, workspace: StrassenCollisionWorkspace) -> dict[str, object]:
    arrays = {
        "weight": staged.weight,
        "factor": staged.factor,
        "scaled_S": base.scaled,
        "live_B_then_D": base.gram,
        "p": base.p,
        "p2": base.p2,
        "rho_then_t": base.rho,
        "rho_p": base.rho_p,
        "scratch": base.scratch,
        "strict_aaab": base.aaab,
        "strict_aabb": base.aabb,
        "strict_aaaa": base.aaaa,
        "powers_S2_S3": workspace.powers,
        "cross_A_E": workspace.cross,
        "strassen_level": workspace.level,
        "strassen_leaf_left": workspace.leaf_left,
        "strassen_leaf_right": workspace.leaf_right,
        "strassen_leaf_product": workspace.leaf_product,
    }
    for index, value in enumerate(base.level_products):
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
    incremental = sum(
        value.nbytes
        for value in (
            workspace.powers,
            workspace.cross,
            workspace.level,
            workspace.leaf_left,
            workspace.leaf_right,
            workspace.leaf_product,
        )
    )
    return {
        "arrays": items,
        "array_count": len(items),
        "persistent_bytes_visible_to_m218": int(total),
        "persistent_mib_visible_to_m218": total / (1024.0 * 1024.0),
        "incremental_m218_bytes": int(incremental),
        "incremental_m218_mib": incremental / (1024.0 * 1024.0),
        "rank3_coefficient_arrays": 0,
        "strassen_depth": STRASSEN_DEPTH,
    }


def _left_transforms(source, output) -> None:
    """Build the seven classic left operands, vectorized over batch axes."""

    half = int(source.shape[-1]) // 2
    a11, a12 = source[..., :half, :half], source[..., :half, half:]
    a21, a22 = source[..., half:, :half], source[..., half:, half:]
    fnp.copyto(output[0], a11)
    fnp.add(output[0], a22, out=output[0])
    fnp.copyto(output[1], a21)
    fnp.add(output[1], a22, out=output[1])
    fnp.copyto(output[2], a11)
    fnp.copyto(output[3], a22)
    fnp.copyto(output[4], a11)
    fnp.add(output[4], a12, out=output[4])
    fnp.copyto(output[5], a21)
    fnp.subtract(output[5], a11, out=output[5])
    fnp.copyto(output[6], a12)
    fnp.subtract(output[6], a22, out=output[6])


def _right_transforms(source, output) -> None:
    """Build the seven classic right operands, vectorized over batch axes."""

    half = int(source.shape[-1]) // 2
    b11, b12 = source[..., :half, :half], source[..., :half, half:]
    b21, b22 = source[..., half:, :half], source[..., half:, half:]
    fnp.copyto(output[0], b11)
    fnp.add(output[0], b22, out=output[0])
    fnp.copyto(output[1], b11)
    fnp.copyto(output[2], b12)
    fnp.subtract(output[2], b22, out=output[2])
    fnp.copyto(output[3], b21)
    fnp.subtract(output[3], b11, out=output[3])
    fnp.copyto(output[4], b22)
    fnp.copyto(output[5], b11)
    fnp.add(output[5], b12, out=output[5])
    fnp.copyto(output[6], b21)
    fnp.add(output[6], b22, out=output[6])


def _combine_seven(products, output) -> None:
    """Recombine seven products into four quadrants without temporaries."""

    half = int(output.shape[-1]) // 2
    c11 = output[..., :half, :half]
    c12 = output[..., :half, half:]
    c21 = output[..., half:, :half]
    c22 = output[..., half:, half:]
    fnp.copyto(c11, products[0])
    fnp.add(c11, products[3], out=c11)
    fnp.subtract(c11, products[4], out=c11)
    fnp.add(c11, products[6], out=c11)
    fnp.copyto(c12, products[2])
    fnp.add(c12, products[4], out=c12)
    fnp.copyto(c21, products[1])
    fnp.add(c21, products[3], out=c21)
    fnp.copyto(c22, products[0])
    fnp.subtract(c22, products[1], out=c22)
    fnp.add(c22, products[2], out=c22)
    fnp.add(c22, products[5], out=c22)


def _build_right_leaf(source, workspace: StrassenCollisionWorkspace) -> None:
    _right_transforms(source, workspace.level)
    _right_transforms(workspace.level, workspace.leaf_right)


def _strassen_l2_product(left, output, workspace: StrassenCollisionWorkspace) -> None:
    _left_transforms(left, workspace.level)
    _left_transforms(workspace.level, workspace.leaf_left)
    fnp.matmul(workspace.leaf_left, workspace.leaf_right, out=workspace.leaf_product)
    _combine_seven(workspace.leaf_product, workspace.level)
    _combine_seven(workspace.level, output)


def _validate_strassen_workspace(staged, workspace: StrassenCollisionWorkspace) -> None:
    layers, width = int(staged.weight.shape[0]), int(staged.weight.shape[-1])
    half, quarter = width // 2, width // 4
    expected = {
        "powers": (2, layers, width, width),
        "cross": (2, layers, width, width),
        "level": (7, layers, half, half),
        "leaf_left": (7, 7, layers, quarter, quarter),
        "leaf_right": (7, 7, layers, quarter, quarter),
        "leaf_product": (7, 7, layers, quarter, quarter),
    }
    for name, shape in expected.items():
        value = getattr(workspace, name)
        if tuple(value.shape) != shape or str(value.dtype) != "float64":
            raise ValueError(f"M218 {name} workspace contract mismatch")


def subtract_collisions_strassen_inplace(
    staged,
    base,
    workspace: StrassenCollisionWorkspace,
    receipt,
    *,
    d_depth: int = D_DEPTH,
):
    """M215 subtraction with only A/E replaced by frozen L2 Strassen."""

    _validate_live_binding(staged, base, workspace, receipt, d_depth)
    _validate_strassen_workspace(staged, workspace)
    x, c = base, workspace
    fnp.multiply(x.scaled, x.scaled, out=c.powers[0])
    fnp.multiply(c.powers[0], x.scaled, out=c.powers[1])

    _build_right_leaf(x.scaled, c)
    _strassen_l2_product(fnp.swapaxes(c.powers[0], 1, 2), c.cross[0], c)
    _strassen_l2_product(fnp.swapaxes(c.powers[1], 1, 2), c.cross[1], c)

    # Every term below is byte-for-byte the M215 schedule after A/E exist.
    fnp.multiply(x.rho[:, :, None], x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(12.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(x.gram, x.gram, out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(8.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.multiply(x.rho[:, :, None], x.rho[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(4.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.multiply(x.p[:, :, None], c.cross[0], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(18.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(c.cross[0], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(12.0), out=x.scratch)
    fnp.add(x.aabb, x.scratch, out=x.aabb)
    fnp.add(x.aabb, fnp.swapaxes(x.scratch, 1, 2), out=x.aabb)
    fnp.sum(c.powers[1], axis=1, out=x.rho)
    fnp.multiply(x.rho[:, :, None], x.p[:, None, :], out=x.scratch)
    fnp.multiply(x.scratch, fnp.float64(6.0), out=x.scratch)
    fnp.add(x.aaab, x.scratch, out=x.aaab)
    fnp.multiply(c.cross[1], fnp.float64(-24.0), out=c.cross[1])
    fnp.add(x.aaab, c.cross[1], out=x.aaab)
    _symmetric_gram_from_power(c.powers[0], x.gram, x.level_products, d_depth)
    fnp.multiply(x.gram, fnp.float64(-24.0), out=x.gram)
    fnp.add(x.aabb, x.gram, out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab, axis1=1, axis2=2))
    return x.aaaa, x.aaab, x.aabb


__all__ = [
    "StrassenCollisionWorkspace",
    "allocate_strassen_collision_workspace",
    "allocation_ledger",
    "subtract_collisions_strassen_inplace",
]
