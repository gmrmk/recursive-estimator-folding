# M145 f32 cross-reference descendant -- target-semantics repair

Status: **protocol repair only; execution is forbidden.**  This is a new
descendant of the immutable float64-oriented cross-risk protocol.  It does not
replace, edit, or interpret any prior reference result (none exists).

## Target

For each randomized, antipodally closed radius-scaled spherical design, the
reference is now defined by `direct_relu_mean_f32` in
`m145_direct_f32_reference.py`: every supplied point and weight is converted to
`flopscope.numpy.float32`; each of the 32 layers is `fnp.matmul` followed by
`fnp.maximum(..., 0)`; the output uses the declared float32 reduction.  Thus
the reference targets the same float32 forward arithmetic class as the contest
scorer, rather than the mathematical float64 surrogate.

## Pre-execution numerical-equivalence gate

Before a reference vector may be generated, an independently written local
official-semantics fixture must run on three frozen synthetic (not contest)
networks and three frozen antipodal point blocks per network.  It must use the
starter-kit/official local direct-forward primitive at its installed version,
with exactly the same f32 points and f32 weights.  The result must be bitwise
equal to `direct_relu_mean_f32` *or*, if the official primitive documents a
different reduction association, agree to maximum absolute `<= 2^-20` and
relative RMS `<= 2^-22`; every vector and digest used for that fixture stays
inside the fixture report and is not a generated campaign reference.

The streamed implementation is separately compared with the unchunked
primitive using the protocol's frozen 256-row blocks.  Its reduction tree is
accepted only if it meets the same predeclared tolerance.  Any failure means
the cross-reference campaign remains locked; no tolerance may be relaxed after
inspection.

## Why the estimate remains unbiased

The stochastic argument is unchanged: a fresh sign-correct Gaussian QR
rotation maps each fixed spherical design line to a uniform direction, and
antipodal equal weighting plus exact radial scaling estimates the float32
implementation's own deterministic spherical integral.  The guarantee is for
the declared computation, not a claim that it equals ideal real arithmetic.
Independent `R1,R2` then retain

`E[(A-R1) dot (A-R2)/256 | W,A] = ||A-I_f32||^2/256`.

No f64 surrogate is used for a promotion decision in this descendant.
