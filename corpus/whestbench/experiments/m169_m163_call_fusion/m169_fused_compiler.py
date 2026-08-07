"""M169: response-free two-axis call fusion for the frozen M163 compiler.

The M163 coefficient is unchanged: ``A = V * (1 - R**2)`` and the five
M156/M163 products are evaluated in their original float64 operation order.
M169 changes only the legal scheduling of those products.  Given the already
owned stack of 31 independent ``(W_l, V_l)`` states, it first performs the 31
``A_l @ W_l`` products as one batched matmul.  It then lays out the four
post-Z operands in a leading product axis and evaluates them in one batched
matmul.  Matmul batch axes keep every product independent: they do *not*
create the cross blocks a 4N-by-4N block product would bill and compute.

This module does not inspect a model response, target, truth, scorer,
leaderboard, submission, or champion.  It is a compiler scheduling artifact
only.  The caller contract is deliberately strict: all layer ``W`` and ``V``
states must already be owned before calling :func:`compile_staged_stack`.
M169 neither derives a covariance nor moves a sequential state transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import flopscope.numpy as fnp


WIDTH = 256
LAYERS = 31
DTYPE = fnp.float64
INHERITED_K128_ENDPOINT_SUBTOTAL = 85_980_878_800
COMPILER_SLOT = 14_019_121_200
COMBINED_CAP = 100_000_000_000
M164_OBSERVED_COMPILER_BILL = 10_444_656_904
M164_OBSERVED_MATMUL_CALLS = 155
COLLISION_MASS = 0.011688232421875


@dataclass
class StagedInputs:
    """Counted owned storage for the caller-provided layer stacks."""

    weight: object
    covariance: object


@dataclass
class Workspace:
    """All counted scratch storage; no implicit temporary is required."""

    diagonal: object
    sigma: object
    inverse_sigma: object
    scale: object
    correlation: object
    exterior: object
    edge: object
    sampler_mass: object
    sampler_probe: object
    z: object
    w2: object
    z2: object
    wz: object
    lhs: object
    rhs: object
    product: object
    aaab: object
    aabb: object
    aaaa: object


def allocate_staged_inputs(layers: int = LAYERS, width: int = WIDTH) -> StagedInputs:
    """Allocate the two explicitly charged 3-D input materializations."""

    shape = (int(layers), int(width), int(width))
    return StagedInputs(
        weight=fnp.empty(shape, dtype=DTYPE),
        covariance=fnp.empty(shape, dtype=DTYPE),
    )


def allocate_workspace(layers: int = LAYERS, width: int = WIDTH) -> Workspace:
    """Allocate persistent arrays used by the two batched contractions."""

    l, n = int(layers), int(width)
    plane = lambda: fnp.empty((l, n, n), dtype=DTYPE)
    # The frozen M164 exterior construction is sequential and reuses these
    # exact 1-D/2-D scratch buffers.  Only the resulting edge needs to live
    # through the batched Z product, so keeping correlation/exterior stacked
    # would add neither information nor a legal algebraic benefit.
    matrix = lambda: fnp.empty((n, n), dtype=DTYPE)
    vector = lambda: fnp.empty((n,), dtype=DTYPE)
    stacked_vector = lambda: fnp.empty((l, n), dtype=DTYPE)
    product_plane = lambda: fnp.empty((l, 4, n, n), dtype=DTYPE)
    return Workspace(
        diagonal=vector(),
        sigma=vector(),
        inverse_sigma=vector(),
        scale=matrix(),
        correlation=matrix(),
        exterior=matrix(),
        edge=plane(),
        sampler_mass=fnp.empty((2,), dtype=DTYPE),
        sampler_probe=fnp.empty((2,), dtype=DTYPE),
        z=plane(),
        w2=plane(),
        z2=plane(),
        wz=plane(),
        lhs=product_plane(),
        rhs=product_plane(),
        product=product_plane(),
        aaab=plane(),
        aabb=plane(),
        aaaa=stacked_vector(),
    )


def stage_inputs(
    weights: Sequence[object], covariances: Sequence[object], staged: StagedInputs
) -> None:
    """Materialize all caller-owned layers and charge both copies.

    ``stack(..., out=...)`` is deliberately used rather than a raw assignment:
    its full data movement appears in the FlopScope ledger.  This is the only
    legal staging step; it has no dependence on values from a later compiler
    operation.
    """

    if len(weights) != staged.weight.shape[0] or len(covariances) != staged.covariance.shape[0]:
        raise ValueError("the staged layer count must equal both input sequences")
    fnp.stack(weights, axis=0, out=staged.weight)
    fnp.stack(covariances, axis=0, out=staged.covariance)


def initialize_target_q0(workspace: Workspace, frozen_masses) -> None:
    """Retain M164's fixed two-stratum bookkeeping and its charge exactly."""

    fnp.copyto(workspace.sampler_mass, frozen_masses)
    fnp.multiply(workspace.sampler_mass, workspace.sampler_mass, out=workspace.sampler_probe)


def _exterior_edges(covariance, workspace: Workspace) -> tuple[object, object, object]:
    """Execute M163's exterior-edge arithmetic in its frozen per-layer order."""

    x = workspace
    layers = covariance.shape[0]
    for layer in range(layers):
        # This is the M164 sequence verbatim on every layer.  In particular,
        # ``outer`` (rather than a broadcast multiply) preserves its existing
        # charge and its exact diagonal-normalization arithmetic.
        fnp.copyto(x.diagonal, fnp.diagonal(covariance[layer]))
        fnp.sqrt(x.diagonal, out=x.sigma)
        fnp.divide(fnp.float64(1.0), x.sigma, out=x.inverse_sigma)
        fnp.outer(x.inverse_sigma, x.inverse_sigma, out=x.scale)
        fnp.multiply(covariance[layer], x.scale, out=x.correlation)
        fnp.fill_diagonal(x.correlation, fnp.float64(1.0))
        fnp.multiply(x.correlation, x.correlation, out=x.exterior)
        fnp.subtract(fnp.float64(1.0), x.exterior, out=x.exterior)
        fnp.fill_diagonal(x.exterior, fnp.float64(0.0))
        fnp.multiply(covariance[layer], x.exterior, out=x.edge[layer])
        fnp.fill_diagonal(x.edge[layer], fnp.float64(0.0))
    return x.edge, x.correlation, x.exterior


def compile_staged_stack(staged: StagedInputs, workspace: Workspace):
    """Return frozen M163 sources for every staged layer using two matmuls.

    The original per-layer post-Z product definitions are retained exactly::

        P = (W * Z**2).T @ W
        Q = (W**2 * Z).T @ Z
        R = (W**2).T @ Z**2
        S = (W * Z).T @ (W * Z)

    ``lhs[:, q] @ rhs[:, q]`` is merely a batched spelling of the q-th
    expression.  ``q`` is a batch index, so the four contractions are neither
    summed nor allowed to form cross terms.
    """

    w, covariance, x = staged.weight, staged.covariance, workspace
    edge, correlation, exterior = _exterior_edges(covariance, x)

    # First of the frozen five products, now batched over all known layers.
    fnp.matmul(edge, w, out=x.z)
    fnp.multiply(w, w, out=x.w2)
    fnp.multiply(x.z, x.z, out=x.z2)
    fnp.multiply(w, x.z, out=x.wz)

    # Explicit packing is fully billed.  Two transposed operands must be
    # materialized for a single homogeneous 4-D batched matmul.
    # P and Q, like R and S, have a transposed left operand.  Directly
    # writing the elementwise product in transposed layout avoids an
    # intermediate without changing either multiplication's operands.
    fnp.multiply(fnp.swapaxes(w, 1, 2), fnp.swapaxes(x.z2, 1, 2), out=x.lhs[:, 0])
    fnp.multiply(fnp.swapaxes(x.w2, 1, 2), fnp.swapaxes(x.z, 1, 2), out=x.lhs[:, 1])
    fnp.copyto(x.lhs[:, 2], fnp.swapaxes(x.w2, 1, 2))
    fnp.copyto(x.lhs[:, 3], fnp.swapaxes(x.wz, 1, 2))
    fnp.stack((w, x.z, x.z2, x.wz), axis=1, out=x.rhs)

    # The four final dense products, batched over (layer, product).
    fnp.matmul(x.lhs, x.rhs, out=x.product)

    fnp.add(x.product[:, 0], x.product[:, 1], out=x.aaab)
    fnp.multiply(x.aaab, fnp.float64(-6.0), out=x.aaab)
    fnp.add(x.product[:, 2], fnp.swapaxes(x.product[:, 2], 1, 2), out=x.aabb)
    fnp.multiply(x.product[:, 3], fnp.float64(4.0), out=x.lhs[:, 0])
    fnp.add(x.aabb, x.lhs[:, 0], out=x.aabb)
    fnp.multiply(x.aabb, fnp.float64(-2.0), out=x.aabb)
    for layer in range(x.aaab.shape[0]):
        fnp.copyto(x.aaaa[layer], fnp.diagonal(x.aaab[layer]))
    return x.aaaa, x.aaab, x.aabb, correlation, exterior, edge


def static_prediction(width: int = WIDTH, layers: int = LAYERS) -> dict[str, int | float | bool | str]:
    """Predeclared target-size accounting, including every packing operation.

    The number is exact for FlopScope 0.10.0 / NumPy 2.4.6 and float64.  It
    starts with the frozen M164 inclusive bill, then adds two stacks of layer
    inputs, one four-product RHS stack, and two materialized transposes.  No
    reshape occurs; a reshape charge is therefore exactly zero.
    """

    n, l = int(width), int(layers)
    if (n, l) != (WIDTH, LAYERS):
        # This ledger is a target-shape freeze, rather than an invitation to
        # extrapolate a different compute contract.
        raise ValueError("M169 static prediction is frozen for width=256, layers=31")
    f64_pack_cost = 2 * l * n * n
    staging_stack_cost = 2 * f64_pack_cost
    rhs_stack_cost = 4 * f64_pack_cost
    transpose_copy_cost = 2 * f64_pack_cost
    packed_total = staging_stack_cost + rhs_stack_cost + transpose_copy_cost
    predicted = M164_OBSERVED_COMPILER_BILL + packed_total
    residual_limit_s = (COMBINED_CAP - INHERITED_K128_ENDPOINT_SUBTOTAL - predicted) / (5.0e11)
    return {
        "candidate": "M169 frozen M163 two-axis batched call fusion",
        "width": n,
        "layers": l,
        "baseline_m164_bill": M164_OBSERVED_COMPILER_BILL,
        "baseline_m164_matmul_calls": M164_OBSERVED_MATMUL_CALLS,
        "predicted_total_matmul_calls": 2,
        "predicted_post_z_matmul_calls": 1,
        "predicted_call_reduction": M164_OBSERVED_MATMUL_CALLS - 2,
        "predicted_dense_matmul_bill": 10_381_557_760,
        "predicted_staging_stack_bill": staging_stack_cost,
        "predicted_rhs_stack_bill": rhs_stack_cost,
        "predicted_transpose_copy_bill": transpose_copy_cost,
        "predicted_reshape_bill": 0,
        "predicted_extra_packing_bill": packed_total,
        "predicted_total_bill": predicted,
        "compiler_slot": COMPILER_SLOT,
        "predicted_bill_fits_slot": predicted <= COMPILER_SLOT,
        "inherited_endpoint_subtotal": INHERITED_K128_ENDPOINT_SUBTOTAL,
        "combined_cap": COMBINED_CAP,
        "max_residual_s_each_for_hostile_5x": residual_limit_s,
        "max_residual_ms_each_for_hostile_5x": residual_limit_s * 1.0e3,
        "no_block_cross_terms": True,
        "all_layer_staging_required": True,
    }


def workspace_allocation_ledger(workspace: Workspace, staged: StagedInputs) -> dict[str, int | float]:
    """Report owned arrays and bytes without relying on allocator heuristics."""

    arrays = [*workspace.__dict__.values(), *staged.__dict__.values()]
    byte_count = int(sum(int(value.nbytes) for value in arrays))
    element_count = int(sum(int(value.size) for value in arrays))
    return {
        "persistent_array_count": len(arrays),
        "persistent_elements": element_count,
        "persistent_bytes": byte_count,
        "persistent_mib": byte_count / (1024.0 * 1024.0),
    }
