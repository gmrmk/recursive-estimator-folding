# M155 — hostile audit of the M151 native B=1 compiler

## Disposition

**KILL THE CURRENT M151 FULL-CONTROL COMPILER PREMISE; PRESERVE THE B=1
CONTROL/RESIDUAL IDENTITY.**  No truth, response, scorer, network outcome,
leaderboard datum, submission, or champion state was accessed.

## Forced term

M151's coefficient on distinct labels contains

```text
d_star(i,j,k) = -2 V_ij V_ik.
```

Let `x_i` be row `i` of the source weight matrix, set the diagonal of `V` to
zero, and define `Z=V_off W`, `G=V_off o V_off`.  The split-pair part of the
`aabb` source is exactly

```text
-8 [ (W o Z)^T (W o Z) - E ],
E_pq = (W_:p o W_:q)^T G (W_:p o W_:q).                 (1)
```

The first term is one ordinary square Gram.  `E` is the masked `j=k`
subtraction required by M151's pairwise-distinct ownership.  It is a generic
Khatri--Rao quadratic action with one column for every symmetric output pair.
The response-free code verifies (1) against the exhaustive ordered source for
widths 3, 4, and 5.

This is not canceled by the canonical raw-node term.  An admissible 49-node B=1
state with weights `(1/2,1/2,0,...,0)`, conditional means `(+a,-a,0,...,0)`,
and zero conditional variance has `T_si=V_ii` on every nonzero-weight node.
Its CP term is identically zero while
`dtilde_ijk=-2 V_ij V_ik` remains on every distinct triple.  The test fixture
verifies this exact witness.

## Frozen current-interface cost

At width 256 the symmetric Khatri matrix has

```text
M = 256*257/2 = 32,896 columns.
```

The only installed generic dense realization forms `G @ K`.  Under the contest
matmul bill `2mkn-mn`, one f32 action costs `4.303323136B` per source layer;
float64 is billed twice, or `8.606646272B`.  Across 31 source layers the f64
action alone costs

```text
266.806034432B FLOPs.
```

That is 25.93 times M151's complete `10.291363760B` allowance before the CP
raw-node contribution, the other `aaab/aabb` contractions, state construction,
the coefficient provider, allocations, copies, or residual wall time.  Adding
it to M151's known `89.708636240B` subtotal already gives `356.514670672B`.

One f64 symmetric Khatri buffer is 64.25 MiB and its product is another 64.25
MiB.  Both exceed the 37.141 MiB exposure left by the hash-bound Formal-L1
reference peak.  Streaming can reduce peak memory only by increasing call
count; it does not change the forced arithmetic.

The 266.806B figure is the exact bill of the current generic contraction, not a
claim of an unconditional arithmetic-circuit lower bound.  A future descendant
would need a genuinely new factorization and native trace.  M151's frozen gate
explicitly rejects a missing compiler, and therefore its current configuration
cannot progress to the residual-variance screen.

## Unexpected escape retained for recursion

M148's conservation identity does **not** require the deterministic control to
equal the full canonical coefficient.  A child may move collision exclusions
or a compiler-hostile component into the exact sampled residual, provided the
same extended-domain control is added and subtracted once and the proposal has
full support there.  In particular, lifting a compiler-closed covariance-star
control to all ordered triples removes the deterministic `j=k` subtraction in
(1).  This is a new ownership/domain mechanism and must receive its own
variance, collision, cost, symmetry, and tail gates; it is not permission to
alter M151 after failure.

Preserve: B=1 state algebra, exact control/residual conservation, equation (1),
the star-only admissible witness, and the extended-domain-control opening.
