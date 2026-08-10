"""M212: M210 level fusion with caller-owned symmetry scratch."""

from __future__ import annotations

from pathlib import Path
import sys

import flopscope.numpy as fnp


HERE = Path(__file__).resolve().parent
M210 = HERE.parent / "m210_level_fused_recursive_gram"
if str(M210) not in sys.path:
    sys.path.insert(0, str(M210))

from m210_flopscope_sidecar import (  # noqa: E402
    LayerInput,
    Workspace,
    _level_fused_gram,
    allocate_staged_inputs,
    allocate_workspace,
    allocation_ledger as _m210_allocation_ledger,
    stage_inputs,
)


def allocation_ledger(staged, workspace: Workspace) -> dict[str, object]:
    ledger = _m210_allocation_ledger(staged, workspace)
    ledger["user_full_plane_temporaries"] = 0
    ledger["symmetry_scratch_owner"] = "scratch"
    ledger["matmul_pack_owner"] = (
        "supported flopscope matmul backend; analytically billed from operand shapes"
    )
    return ledger


def compile_staged_stack(staged, workspace: Workspace, depth: int = 3):
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
    fnp.copyto(x.scratch, fnp.swapaxes(x.aabb, 1, 2))
    fnp.add(x.aabb, x.scratch, out=x.aabb)
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
