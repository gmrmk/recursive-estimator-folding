"""Inclusive target-shaped FlopScope sidecar for frozen M163.

The only new M163 arithmetic is the canonical correlation/exterior edge map
``A = V o (1-R^2)``.  The five-product M156 source compiler then acts on A.
All hot buffers are allocated once through FlopScope and supplied as ``out=``
destinations.  This is a structural resource artifact only: it has no model
response, target truth, scorer, or competition dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

import flopscope.numpy as fnp


@dataclass
class Workspace:
    # M163-specific correlation/exterior state.
    diagonal: object
    sigma: object
    inverse_sigma: object
    scale: object
    correlation: object
    exterior: object
    edge: object
    sampler_mass: object
    sampler_probe: object
    # Existing five-product compiler state.
    z: object
    w2: object
    z2: object
    wz: object
    left: object
    p: object
    q: object
    r: object
    s: object
    aaab: object
    aabb: object
    aaaa: object


def allocate_workspace(width: int = 256) -> Workspace:
    n = int(width)
    matrix = lambda: fnp.empty((n, n), dtype=fnp.float64)
    vector = lambda: fnp.empty((n,), dtype=fnp.float64)
    return Workspace(
        diagonal=vector(),
        sigma=vector(),
        inverse_sigma=vector(),
        scale=matrix(),
        correlation=matrix(),
        exterior=matrix(),
        edge=matrix(),
        sampler_mass=fnp.empty((2,), dtype=fnp.float64),
        sampler_probe=fnp.empty((2,), dtype=fnp.float64),
        z=matrix(),
        w2=matrix(),
        z2=matrix(),
        wz=matrix(),
        left=matrix(),
        p=matrix(),
        q=matrix(),
        r=matrix(),
        s=matrix(),
        aaab=matrix(),
        aabb=matrix(),
        aaaa=vector(),
    )


def initialize_target_q0(workspace: Workspace, frozen_masses) -> None:
    """Charge the frozen two-stratum bookkeeping once, with no adaptation."""

    # ``flopscope.numpy`` intentionally exposes no scalar ``fill`` primitive.
    # Copying the fixed, externally supplied two-stratum masses is both billed
    # and represents the actual setup work without a hidden scalar write.
    fnp.copyto(workspace.sampler_mass, frozen_masses)
    fnp.multiply(workspace.sampler_mass, workspace.sampler_mass, out=workspace.sampler_probe)


def exterior_edge(covariance, workspace: Workspace):
    """Form M163's edge matrix through billed array operations only."""

    x = workspace
    fnp.copyto(x.diagonal, fnp.diagonal(covariance))
    fnp.sqrt(x.diagonal, out=x.sigma)
    fnp.divide(fnp.float64(1.0), x.sigma, out=x.inverse_sigma)
    fnp.outer(x.inverse_sigma, x.inverse_sigma, out=x.scale)
    fnp.multiply(covariance, x.scale, out=x.correlation)
    # Define the canonical diagonal exactly before forming the exterior Gram
    # determinant.  No clipping/ridge or per-pair branch occurs.
    fnp.fill_diagonal(x.correlation, fnp.float64(1.0))
    fnp.multiply(x.correlation, x.correlation, out=x.exterior)
    fnp.subtract(fnp.float64(1.0), x.exterior, out=x.exterior)
    fnp.fill_diagonal(x.exterior, fnp.float64(0.0))
    fnp.multiply(covariance, x.exterior, out=x.edge)
    fnp.fill_diagonal(x.edge, fnp.float64(0.0))
    return x.edge, x.correlation, x.exterior


def compile_layer(weight, covariance, workspace: Workspace):
    """M163 edge construction plus the exact five-product source compiler."""

    edge, correlation, exterior = exterior_edge(covariance, workspace)
    w = weight
    x = workspace
    fnp.matmul(edge, w, out=x.z)
    fnp.multiply(w, w, out=x.w2)
    fnp.multiply(x.z, x.z, out=x.z2)
    fnp.multiply(w, x.z, out=x.wz)

    fnp.multiply(w, x.z2, out=x.left)
    fnp.matmul(x.left.T, w, out=x.p)
    fnp.multiply(x.w2, x.z, out=x.left)
    fnp.matmul(x.left.T, x.z, out=x.q)
    fnp.matmul(x.w2.T, x.z2, out=x.r)
    fnp.matmul(x.wz.T, x.wz, out=x.s)

    fnp.add(x.p, x.q, out=x.aaab)
    fnp.multiply(x.aaab, fnp.float64(-6.0), out=x.aaab)
    fnp.add(x.r, x.r.T, out=x.aabb)
    fnp.multiply(x.s, fnp.float64(4.0), out=x.left)
    fnp.add(x.aabb, x.left, out=x.aabb)
    fnp.multiply(x.aabb, fnp.float64(-2.0), out=x.aabb)
    fnp.copyto(x.aaaa, fnp.diagonal(x.aaab))
    return x.aaaa, x.aaab, x.aabb, correlation, exterior, edge
