"""Target-shaped FlopScope sidecar for M156's five-product compiler.

The sidecar owns no response, truth, scorer, or contest instance.  All hot
buffers are supplied by setup and every billed operation is performed through
``flopscope.numpy``.  The implementation deliberately emits all three M133
source slots, including the diagonal ``aaaa`` slot.
"""

from __future__ import annotations

from dataclasses import dataclass

import flopscope.numpy as fnp


@dataclass
class Workspace:
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
    return Workspace(
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
        aaaa=fnp.empty((n,), dtype=fnp.float64),
    )


def compile_layer(weight, covariance, workspace: Workspace):
    """Emit the complete-domain star source using exactly five GEMMs."""

    w = weight
    v = covariance
    x = workspace

    fnp.matmul(v, w, out=x.z)
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
    return x.aaaa, x.aaab, x.aabb

