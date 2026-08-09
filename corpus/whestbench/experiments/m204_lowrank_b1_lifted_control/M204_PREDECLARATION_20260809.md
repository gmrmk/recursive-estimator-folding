# M204 predeclaration -- lifted rank-one B=1 Rademacher control

Date: 2026-08-09.  This artifact is written before any M204 source-variance,
MSE, score, response, contest, truth, scorer, leaderboard, submission, or
champion evaluation.

## One changed mechanism

M204 is a narrow M151/M155 child.  It fixes one B=1, 49-node canonical state
whose two active nodes are the rank-one Rademacher pair.  It lifts the
resulting control to the complete ordered triple domain and puts the collision
add/subtract terms in the exact full-support residual, using M156's already
established conservation pattern.  The rank is frozen to **r=1**.  No
rank-2/3/4 fallback, factor tuning, adaptive proposal, residual tuning, or
response-side mutation is permitted.

The proposed state is formed only from the live M179 `BackgroundState(mu,V)`:
for positive diagonal entries set `s_i=sqrt(V_ii)`, let
`q_i=1/sqrt(n_active)` on the positive-variance coordinates and zero
otherwise, set `u_i=s_i q_i`, and set `d_i=V_ii-u_i^2`.  The two nonzero nodes
have weights `(1/2,1/2)`, conditional means `mu+u` and `mu-u`, and identical
conditional variance `d`; the remaining 47 nodes have zero weight.  This
uses no truth, target, score, source coefficient, or outcome input.

For every distinct `(i,j,k)`, the prescribed coefficient is

```text
dtilde_ijk = -2 u_i^2 u_j u_k.
```

On the complete ordered domain let `c_ijk=dtilde_ijk`, let the physical M151
target be `Delta^o_ijk = Delta_ijk * 1{i,j,k distinct}`, and use the M156
complete-domain mixture: the distinct stratum has mass `1-eta` under the
frozen M133 `q0`, the collision stratum has mass `eta`, and
`eta=n(3n-2)/n^3`.  With `F` denoting M151's original coefficient-free feature,

```text
C = (1/2) sum_all c_e F_e
Rhat = (1/K) sum_t (Delta^o_Et-c_Et) F_Et / [2 q(Et)].
```

This is an exact add/subtract identity.  It supplies no variance or efficacy
claim.

## Frozen algebra and source compiler

For `W` with labelled rows, define

```text
p = W^T u
rho = (W^2)^T u^2
B = W^T diag(u^2) W.
```

The lifted source slots are frozen as

```text
C_aaab = -6 [ diag(p^2) B + (rho*p) p^T ]
C_aabb = -2 [ rho (p^2)^T + (p^2) rho^T + 4 diag(p) B diag(p) ]
C_aaaa = diag(C_aaab).
```

There is exactly one f64 square output contraction `B` per source layer.  No
ordered-cubic label loop, Khatri--Rao buffer, all-output dual, reverse
covariance pullback, second carrier, or B>1 state is permitted in a target
compiler.  Small-width exhaustive sums are parity oracles only.

## Strict cost-premise gate

One f64 `256x256` product across 31 layers costs `2.076311552B` before the
frozen 1.25 reserve and `2.595389440B` protected.  M151 already books exactly
one protected dense forward source-emission family.  M204 may treat its single
`B` family as that booked family **only** if a native integrated trace proves
same operands, dtype, result, lifetime, and billed call.  Otherwise it is an
additional nonnegative cost and fails the strict composed premise.

Even with that replacement proof, all M204-new state formation, complete-
domain proposal/collision bookkeeping, source glue, M198/M172/terminal work,
copies, allocations, and residual wall time must fit

```text
1.986871472 B FLOPs
```

under one integrated target-shaped trace.  M199's `9.723621632B` replacement
sensitivity is not cost credit and cannot open this gate.  Until this strict
trace exists and passes, M204 is `BLOCKED_COST_PREMISE`; source-variance and
all response/MSE work are forbidden.

## Required response-free checks

The implementation may run generated-only algebra checks at widths 3, 4, 5,
and 8 with fixed Philox fixtures.  It must verify: the rank-factor Schur
identity; the Rademacher `dtilde` identity; lifted `aaaa/aaab/aabb` source-slot
parity with a brute complete ordered-triple sum; positive-gauge and hidden
permutation covariance; complete-domain conservation for an arbitrary
symmetric distinct-only synthetic target; full proposal support and unit mass;
and the recorded strict cost arithmetic.

Any algebra, invariance, conservation, or cost-arithmetic failure kills this
rank-one configuration.  Passing these checks gives only an exact
response-free component and does not waive the native strict-cost gate.

## Stop rule

No source-variance runner is created or executed in M204.  No contest/model
input, truth, scorer, leaderboard, submission, or champion artifact is read
or changed.  The only lawful next action after algebra is a separate,
integrated native replacement/cost trace; only a passing trace could authorize
a separately predeclared generated source-variance gate.
