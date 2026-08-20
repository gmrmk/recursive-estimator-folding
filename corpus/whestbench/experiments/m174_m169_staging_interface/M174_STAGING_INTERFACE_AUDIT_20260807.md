# M174 — M169 all-layer staging interface audit

## Verdict

**REPAIR / NOT A LAWFUL ACTUAL-CALLER PRECONDITION.**  The two-batch M169
compiler is a valid pure transform *conditional on* 31 already-owned,
float64 `(W_l, V_l)` pairs.  That condition has not been met by an actual
M163/M125b/M129-style caller.  The present repository contains no labelled,
accounted producer-to-M169 ABI.  Therefore M169's generated-stack trace does
not open any downstream gate.

This is an interface/liveness verdict only.  No response, truth, scorer,
leaderboard, submission, champion, or source-efficacy artifact was read or
changed.

## First broken dependency

The production base at `base_estimator.py` has only
`_diagonal_gaussian_pass`: it advances a vector `var`, not a full covariance
matrix `V_l`.  It cannot supply even one M163 input covariance.  The closest
full-covariance experiment, `fullcov_gaussian_mm/estimator.py`, does advance
one `covariance` state sequentially, but it retains only the current state,
returns stacked means, exposes no state archive or source/Jacobian bundle, and
uses a different clipped/floored numerical closure.  It is not the exact
endpoint-aware M125b caller.

The subsequent links remain absent as well:

- M163/M156 accepts one already-made matrix pair and emits source slots
  `(aaaa, aaab, aabb)`.  It does not make a forward-tangent `TangentState`.
- M125b accepts lists of already-made sources, weights, and Jacobians; its
  only structural test is a list-length equality.  It uses ordinary NumPy, so
  it provides neither a FlopScope ledger nor semantic labels `s_1..s_31` /
  `J_2..J_31`.
- M122/M129 is a small-width (`n <= 8`) NumPy algebra oracle.  It cannot be
  the width-256 background/source provider and exports no 31-layer archive.

Thus the first failure is availability/provenance of `V_l`; the lack of a
labelled conversion from M163 source slots into M125b sources is a second,
independent blocker.  Reordering the sequential covariance recurrence to
pretend those states exist would not repair either issue.

## What M169 actually owns

`StagedInputs` has only `weight` and `covariance` fields—no layer labels,
state epoch, immutability guard, or producer identity.  `stage_inputs` copies
both input sequences with two `fnp.stack(..., out=...)` calls.  Its native
runner first creates 31 arbitrary generated matrices, converts them before
the measured budget scope, and then calls this staging function.  It is a
compiler test, not a caller integration test.

The ownership categories must remain distinct:

| object | true owner/lifetime | status in the audited code |
|---|---|---|
| `W_l` | immutable model weight (normally f32); M169 needs an f64 staged copy | source list is synthetic in the M169 runner |
| `V_l` | sequential post-ReLU covariance; must be retained before M169 | no actual 31-state archive exists |
| M163 outputs | `aaaa, aaab, aabb` retained in M169 workspace | not an M125b `TangentState` ABI |
| M125b carrier | one accumulated `(mean,covariance)` plus frozen labelled `J` maps | theory-only NumPy function; producer absent |

The zero-order background may be advanced sequentially before a source is
applied only under the frozen first-Born rule.  It may not be advanced using
the accumulated source carrier.  This distinction prevents a future caller
from treating delayed source compilation as permission to change the
background transition.

## Installed meter semantics and inclusive compiler-side envelope

The pinned `work/whest-v014` FlopScope 0.10.0 source confirms: `empty` bills
zero but allocates real memory; `stack` bills every written element; `copyto`
bills every destination element; float64 has rate 2; `swapaxes` is free; and
`reshape` bills its input size (M169 calls none).  The two preallocated
staging stacks are therefore genuinely billed, but caller-side state retention
and any conversion/Jacobian archive are outside the M169 trace.

At `(L,n)=(31,256)`, M169's own 21 persistent arrays occupy exactly
`42,869,252` f64 elements = **327.0664367675781 MiB**.  Its explicit staging,
RHS packing, and transpose-copy charge is

```text
2 input stacks + 4 RHS planes + 2 materialized transpose copies
= 8 * (2 * 31 * 256^2)
= 32,505,856 billed FLOPs.
```

This is not an inclusive actual-caller peak.  At the stage call, the caller
must additionally keep its covariance archive alive while it is copied.  The
irreducible archive is `31 * 256^2 * 8` = **15.5 MiB**.  If the 31 source
weights are raw f32 model arrays, they add **7.75 MiB**; if they have already
been widened to a separate f64 archive, they add **15.5 MiB** instead.  Hence
the smallest array-only envelope around the existing full-stack compiler is
**350.3164367675781 MiB** (f32 model weights) or **358.0664367675781 MiB**
(separate f64 weight archive), before Python/BLAS overhead, labelled M125
Jacobians, source-slot conversion, and any M129 state.  It is not a proof of
the `<512 MiB` setup/predict limit.  The reported generated-run RSS of
404.23828125 MiB cannot close that gap because it omitted an actual producer,
carrier contract, and full integration liveness measurement.

## Fixed response-free fallback: B=8 consecutive layers

The only evaluated alternative is fixed block size **B=8**, with blocks
`[8, 8, 8, 7]`.  The lawful order, if and only if exact labelled builders are
provided, is:

```text
advance immutable zero-order background through one block
  -> retain that block's labelled (W_l,V_l,J_l)
  -> compile that block's independent M163 sources
  -> convert sources under an explicit ABI and advance M125b through the block
  -> release the block; begin the next zero-order block
```

It never moves a background transition and never feeds a source-carrier state
back into `V`.  Its largest M169 workspace is exactly **85.52151489257812 MiB**;
the block `V` archive is **4 MiB**, and 31 raw f32 immutable weights are
**7.75 MiB**.  The raw M169 packing element count is unchanged across the four
blocks, so the static packing bill remains `32,505,856`; the compiler would
make **8** batched-matmul dispatches rather than 2.  No wall-time, full memory,
or budget certificate follows from that arithmetic.  In particular, B=8 is a
response-free staging design note, not a repaired M169 candidate.

## Required repair contract before re-audit

Define and trace a single labelled, immutable input bundle:

```text
BackgroundArchive[
  l: 1..31,
  W_l: readonly (256,256) f64 view/explicit conversion provenance,
  mu_l: readonly (256,) f64,
  V_l: readonly symmetric (256,256) f64,
  J_{l+1}: exact frozen M125b Jacobian for l<31,
  source_l: explicit M163-slot -> M125b-TangentState conversion ownership
]
```

The producer must preserve the original zero-order operation order and every
cast/rounding point, charge each materialization or prove it is an existing
array, and give an integrated setup/predict liveness trace including the
archive, M169 workspace, source conversion, Jacobian bank, and carrier.  Only
then may the all-31 M169 condition be checked again.  A full new background
pass merely to recreate discarded states is extra billed work and requires a
separate cost certificate; it is not free staging.
