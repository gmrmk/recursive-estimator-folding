# M156 — extended-domain covariance-star control

## Status

**COMPILER RESOURCE GATE PASSED; FULL-BRANCH AND SOURCE-VARIANCE GATES CLOSED.**
No truth, response, scorer, network outcome, leaderboard datum, submission, or
champion state was accessed.

## One mechanism: lift the control domain

The physical `[2,1,1]` target is

```text
T = (1/2) sum_{i,j,k pairwise distinct} Delta_ijk F_ijk.
```

Extend its coefficient by zero to every collision triple and choose the
covariance-star control

```text
c_ijk = -2 V_ij V_ik
```

on **all** ordered triples.  With any full-support proposal on that complete
domain,

```text
C = (1/2) sum_all c_e F_e,
Rhat = mean [(Delta*_E-c_E)F_E/(2q(E))],
E[C+Rhat] = T.
```

On collision rows `Delta*=0`, so the sampled residual is exactly `-cF`.
Consequently the artificial collision source cancels in expectation and does
not overlap the separately owned physical collision classes.  The change is an
exact control-domain lift, not a claim that collisions have `[2,1,1]` physics.

Use a two-stratum proposal: retain the frozen full-support M133 `q0` on
distinct labels with mass `1-eta`, and sample uniformly from the four disjoint
collision patterns with mass

```text
eta = n(3n-2)/n^3.
```

At n=256, `eta=0.011688232421875`; only about 1.50 of K=128 draws per layer
are collisions in expectation.  The collision sampler needs no rejection.

## Five-product deterministic compiler

Let `Z=VW`.  The complete-domain star control has the exact source slots

```text
P = (W o Z^2)^T W
Q = (W^2 o Z)^T Z
R = (W^2)^T Z^2
S = (W o Z)^T(W o Z)

C_aaab = -6(P+Q)
C_aabb = -2(R+R^T+4S)
C_aaaa = diag(C_aaab).
```

These are five square products per source layer, including `Z=VW`.  There is
no cubic coefficient table and no masked Khatri--Rao action.  Small-width
exhaustive tests cover repeated labels and reproduce all three source slots.

## Static cost

At width 256, float64 rate, 31 layers, and the inherited 1.25 protection,
each square-product family costs 2.595389440B.  Five cost 12.976947200B.
Adding M148's frozen K=128 endpoint subtotal gives

```text
85.980878800B + 12.976947200B = 98.957826000B.
```

Only 1.042174000B remains for pointwise operations, collision sampling,
extended repeated-row features, copies/allocations, and all incremental
residual wall time.  This is not a deployment certificate.  A native target
trace must include every one of those terms and stay below 100B with peak
memory at most 512 MiB.  No f32 credit, sharing credit, or omitted call is
allowed.

## Response-free gates before a source premise

1. Root/independent exhaustive parity of all source slots, extended-domain
   conservation, collision partition, permutation, positive gauge, and exact
   one-owner cancellation.
2. Native target-shaped FlopScope compiler plus sampler trace below 100B and
   512 MiB, including the incremental residual-time charge.  The five control
   maps must be exactly 155 calls across 31 layers.
3. Bind a generic exact value provider for distinct `Delta`.  Collision rows
   call no trivariate provider because their true target is zero.
4. Only then run M148's frozen source-level gate, modified solely to measure
   the complete-domain residual: upper-90 variance ratio below .25, collision
   contribution p99 within the same 1.25 tail gate, and no adverse width trend.
5. Any failure preserves the domain-lift identity and kills this star-control
   configuration.  No eta, K, control coefficient, or proposal retune follows
   an opened source result.

## Risk forecast

M140 found a different zero-mean quadratic control anticorrelated with the
nonzero-mean vertex.  Therefore M156 has no variance credit.  Its only claim is
that exact conservation removes M155's deterministic collision obstruction.
The source gate, especially its collision and p99 components, is decisive.

## Native compiler addendum

The frozen target-shaped implementation was run in five fresh CPython 3.11
processes against FlopScope 0.10.0.  Every run made exactly 155 matmul calls,
returned finite source slots, and billed 10,426,269,184 operations.  Local
incremental residual time ranged from 0.005619 to 0.006384 seconds.

Combining the literal measured compiler bill with the inherited K=128 endpoint
subtotal gives 96.407147984B before incremental wall.  At the measured wall it
gives 96.9690--97.0455B effective compute.  Even multiplying only the new
compiler residual by the hostile factor 5 gives 99.2165--99.5990B, leaving
0.4010--0.7835B.

This passes the compiler-only resource gate.  It is not a full branch pass:
the collision-mixture bookkeeping and the provenance of `V` must be bound to
already-owned work or traced inside the remaining hostile margin.  In
particular, silently constructing a new B=1 covariance provider is forbidden.
The most economical legal descendant uses a covariance already emitted by the
base analytic state; because the exact-control identity permits any frozen
deterministic `V`, accuracy of that covariance affects variance but not bias.
