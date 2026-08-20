# M216 predeclaration -- antithetic strict-distinct conditional provider

Date: 2026-08-09.  Status: `PREDECLARED_BEFORE_IMPLEMENTATION`.

M216 is a separately named child of M213.  It preserves only M213's proved
tower-property identity on the pairwise-distinct `[2,1,1]` domain and changes
the failed outer mechanism.  It does not repair, estimate, or numerically zero
the `[4]`, `[3,1]`, `[2,2]`, or `[1,1,1,1]` strata.  Those requests must raise
a typed refusal.  It emits no complete Source211 table and claims no M198,
carrier, terminal, response, MSE, score, rank, or submission result.

## Frozen invariants

The competition objective is the official adjusted MSE under the 100B-like
protected branch accounting used by this campaign.  This experiment can only
establish a response-free coefficient-provider component.  The legality
boundary is FlopScope 0.10.0 with NumPy 2.4.6: every runtime operation and
allocation must be exposed, and the residual-wall conversion is
`lambda = 1e11 charged FLOPs/s`.  The component resource ceiling is the
currently unclaimed M214 replacement-DAG allowance `6.824272176B`; consuming
all of it would still not license integration because the other M214 unknowns
remain unpriced.  Bias class is exact-in-expectation in real arithmetic, with
certified finite-precision enclosures.  All inputs are generated Gaussian
cells.  No challenge model, weights, truth, scorer, leaderboard, response,
champion output, or submission artifact may be read.

## Changed mechanism

For three distinct labels `(i,j,k)`, let `Z_i;jk(g)` be M213's valid event:

```text
(ReLU(mu_i + sigma_i g) - m_i)^2
 * E[(Y_j-m_j)(Y_k-m_k) | G_i=g]
- V_ii V_jk - 2 V_ij V_ik - Tree_iijk.
```

`m`, `V`, and `Tree` are deterministic local quantities, and the conditional
pair is evaluated with M178.  M216 returns the coupled event

```text
A_i;jk(g) = (Z_i;jk(g) + Z_i;jk(-g))/2,   G ~ N(0,1).
```

Normal symmetry proves `E[A(G)] = E[Z(G)]` without a quadrature rule or fitted
coefficient.  One coupled event makes exactly two M178 calls.  The singleton
swap `j <-> k` must be invariant.  Positive diagonal gauge with scales `s`
must multiply the event by `s_i^2 s_j s_k`, while a label permutation merely
reindexes it.

## Frozen generated identity census and independent oracle

- Widths: `3,4,5,6,7`.
- State seeds paired by width: `216700003..216700007`.
- At each width, identity events are `(0,1,2)` and `(width-1,0,1)`; duplicate
  physical events at width 3 are retained as different repeated-label tests.
- The reference is an independent mpmath 1.3.0 adaptive one-dimensional outer
  integral, not Gauss--Hermite and not M213's GH64/96 gate.  It uses 60 decimal
  digits, splits at the repeated-ReLU boundary, and uses an independently
  assembled high-precision bivariate positive-part formula.  A second 80-digit
  run must agree within `2e-11 * (1+abs(reference))`.
- The adaptive oracle and the adaptive integral of the M216 antithetic kernel
  must agree within `5e-8 * (1+abs(reference))` on every frozen identity event.
  Any oracle exception, nonfinite value, or failed self-check kills M216.

This validates the expectation, not a finite-sample mean.  Floating PRNG draws
are never called literally unbiased.

## Frozen invariance and numerical gates

Gauge/permutation cell: width 5, seed `216700005`, permutation
`(3,0,4,1,2)`, positive gauge
`exp((-0.4,-0.1,0.0,0.2,0.5))`, outer probes
`(-2.0,-0.5,0.0,0.75,2.5)`.  Test every strict physical owner
`i;{j,k}`.  Covariance tolerance is
`5e-8 * (1+abs(expected))`; singleton-swap tolerance is `2e-12`.

Numerical census: every strict physical owner at every frozen width and
`g in (0,+-2^-8,+-0.25,+-1,+-2.5,+-5,+-8)`.  Both M178 calls must be contained
and finite.  The propagated antithetic coefficient radius must satisfy

```text
radius <= 2e-7 * (1 + abs(midpoint)).
```

There is no clipping, ridge, retry, or fallback value.  An invalid SPD chart
is a refusal and a gate failure.

## Frozen static and native resource gates

Static event ceiling:

```text
2 * 4,048 M178 worst-inclusive + 4,096 local charged FLOPs = 12,192/event.
31 * 128 = 3,968 events -> 48,377,856 charged FLOPs.
```

The implementation must publish a counted local-DAG census no larger than the
4,096 allowance and verify two billed M178 calls on native FlopScope.  The
static count does not hide Python wall time.

Native seeds are `216720001..216720005`.  Each trace warms 256 coupled events,
then times exactly 3,968 coupled events, cycling through frozen strict owners;
setup and the archived local context are outside the hot interval, while event
dispatch, both conditional evaluations, and antithetic assembly are inside.
Peak RSS must stay below 512 MiB.  Every trace must satisfy the hostile gate

```text
48,377,856 + 5 * 1e11 * elapsed_seconds <= 6,824,272,176.
```

The interpreter/reference implementation is the implementation under test.
A future compiled or batch-stratified provider would be a new mutation and
must receive its own native gate; it cannot inherit M216's algebraic result.

## Ordered gates and variance firewall

Run, in order:

1. response-free adaptive-oracle identity;
2. singleton symmetry, permutation, and positive-gauge covariance;
3. numerical enclosure census;
4. static count and five native hostile resource traces.

Only if **all four** pass may a second document be written that predeclares a
generated source-level matched-variance experiment.  That future gate must use
the full frozen `q0` domain and the actual source vector
`A_i;jk(G) F_i;jk/(2 q0(i,j,k))`, including the provider's outer randomness.
Coefficient-only or fixed-G variance is forbidden.  Its frozen primary gates
must be paired-bootstrap one-sided `upper90 < .25` and
`p99(candidate squared contribution)/p99(raw squared contribution) <= 1.25`.
No such runner or result may exist if any preceding gate fails.

Failure kills this fully specified antithetic implementation only.  It
preserves the exact symmetry identity, strict-domain refusal ABI, independent
adaptive oracle, and any passing numerical component as salvage.
