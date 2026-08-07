# M124 pretheory: one shared k3-selected projector

Status: `SOURCE_COMPONENT PRESERVED / M120 BRANCH KILLED / M125-GATED`

Execution status: the nine-cell generated outcome grid is **UNOPENED**.  The
draft manifest is inert and refuses execution.  No contest, public, private,
scorer, champion, or submission artifact is loaded by this directory.

## Hostile verdict

The M120-linked version of M124 is not a surviving response-bearing estimator.
Its downstream carrier was M120C, whose frozen one-shot result is a kill (648 rows; global
complete error `0.084011 > 0.05`, worst complete cells `0.1395--0.6300 > 0.10`).
That integration must not be revived or described as a route to a leaderboard
result.

One independently useful result survives: exact source-side algebra for a
rank-four projector chosen from the nonzero-mean order-three bridge-tree source,
including exact one/two-coordinate collision replacements, and exact projected
order-three/order-four cores without forming an order-four Gram matrix.  Preserve
that component for a future independently validated carrier.  M125's proposed
source-batched **forward** dense `(dmu,dC)` tangents are not logically killed by
M120's failed reverse response.  If M125 first passes its own frozen dense-source
algebra, accuracy, and cost gates, M124's still-unopened source grid may then be
reviewed, hash-locked, and executed once.

## Frozen candidate definition (not executed)

For standardized ReLU activations, write

```text
b1_i = Phi(alpha_i) / s_i
b2_i = phi(alpha_i) / (2 s_i)
b3_i = -alpha_i phi(alpha_i) / (6 s_i)
g2_i = 2 b2_i / b1_i^2
g3_i = 6 b3_i / b1_i^3
```

where `s_i^2 = Var[(G+alpha_i)_+]`.  If `Q` is the standardized activation
covariance bridge, the distinct-index source ansatz is

```text
T3_ijk = g2_i Q_ij Q_ik + g2_j Q_ji Q_jk + g2_k Q_ki Q_kj.
```

The order-four tree is the sum of the 12 undirected labelled paths, with a
`g2` factor at both internal vertices, plus four labelled stars, with `g3` at
the centre.  Entries containing one or two distinct coordinates are replaced
by their exact standardized bivariate/univariate ReLU cumulants.  “Exact” below
means exact for this declared source family, not exact final-network cumulants.

The rank is fixed at four from M85.  Let `G3 = K3_(1) K3_(1)^T`; the projector
is the leading rank-four eigenspace of `G3`.  If the rank-4/5 relative eigengap
is no larger than `2^-36`, or the fourth eigenvalue is nonpositive, evaluation
fails closed.  The same `U` is used for both sources:

```text
C3 = K3 x1 U^T x2 U^T x3 U^T
C4 = K4 x1 U^T x2 U^T x3 U^T x4 U^T.
```

Physical scales are restored only after projection: `F = diag(s) U`.  A later
linear map `W` transports the source through `W^T F`; this is exactly invariant
to hidden-coordinate permutations and positive diagonal gauges.

## Exact cheap `G3`, including collisions

For the tree part define `R=Q@Q`, `H=Q*Q`, `r=H@1`, `D=diag(g2)`, and
`F=(Q*R)@(D@Q)`.  Direct contraction gives

```text
G_tree = (g2 g2^T) * (R*R)
       + 2 Q diag(g2^2 * r) Q
       + 2 Q (D H D) Q
       + 2 (D F + F^T D).
```

The implementation is algebraically equal to a dense mode unfolding to
`<=1e-10` on generated widths 2 through 8.

Let the sparse collision defect be

```text
d_i   = Delta_iii
E_ij  = Delta_iij, i != j,
```

where `i` is the repeated coordinate in `E_ij`.  No dense `Delta` is needed.
For `C = T_(1) Delta_(1)^T`,

```text
C_ab = d_b T_abb
     + sum_(t != b) [2 E_bt T_abt + E_tb T_att].
```

For `J = Delta_(1) Delta_(1)^T`, start from `E^T E` and add

```text
J_aa += d_a^2 + 2 sum_t E_at^2
J_ab += d_a E_ab + d_b E_ba + 2 E_ab E_ba, a != b.
```

Thus `G3 = G_tree + C + C^T + J` uses `O(n^2)` source storage and `O(n^3)`
arithmetic.  The tests compare this implicit result to the dense same-source
unfolding exactly.

## Exact projected collision cores without `G4`

The order-three collision core is

```text
sum_i d_i u_i^3 + sum_(i != j) E_ij Sym[u_i,u_i,u_j].
```

For order four retain three sparse tables:

```text
d4_i   = Delta_iiii
E31_ij = Delta_iiij, i != j
E22_ij = Delta_iijj, i < j.
```

Then

```text
C4_collision = sum_i d4_i u_i^4
             + sum_(i != j) E31_ij Sym[u_i,u_i,u_i,u_j]
             + sum_(i < j) E22_ij Sym[u_i,u_i,u_j,u_j].
```

The 12 path cores are contracted as length-three matrix chains in rank space;
the four stars use `Q@U`.  This constructs the exact projected order-four core
for the declared source and never constructs `G4` or an `n^4` target tensor.
The dense tensors retained in the test harness exist only at widths 5--8 to
provide an independent algebra oracle and source-fidelity definition.

## Analytic collision source

For correlated standard normals shifted by `(alpha,beta)`, use the positive
quadrant MGF

```text
M(t,s) = exp(alpha t + beta s + (t^2 + 2 rho t s + s^2)/2)
         Phi2(alpha + t + rho s, beta + rho t + s; rho).
```

A total-degree-four Taylor jet yields every joint positive moment needed for
the order-three/four cumulants.  The sole non-elementary scalar is the existing
certified Plackett evaluation of `Phi2`; all higher derivatives are closed
Gaussian boundary terms.  Axis moments are replaced by exact univariate
truncated-normal recurrence values because a quadrant MGF at exponent zero
otherwise retains the unused coordinate's positivity indicator.

Tests cover independence factorization, swap symmetry, and an independent
192-node conditional one-dimensional integration at nonzero correlation to
`2e-11`.  There is no hidden tensor-product quadrature in the target source.

## Inert falsifier and gates

The draft declares generated Gaussian backgrounds only:

```text
widths       = 8, 12, 16
alpha scales = 0.15, 0.35, 0.65
RNG          = predeclared Philox seeds
rank         = 4 (inherited, not selected here)
```

Every cell would have to pass all of:

```text
factor/transport algebra       <= 1e-10
combined k3+k4 source fidelity >= 0.80
separate k3 and k4 fidelity     >= 0.80 each
repeated-output k4 error        <= 0.50
one-delay correction ratio     <= 0.50
permutation invariance         <= 1e-10
positive-gauge invariance      <= 1e-10
finite outputs and no failures
source-only effective cost     < 99e9
source + carrier effective cost < 152e9
```

The response and efficacy gates are deliberately unopened.  The runner requires
a carrier prerequisite with status `PASSED_AND_HASH_LOCKED`; merely changing
the draft status and authorization flags is insufficient.

The repeated-output gate is essential.  Pairwise ReLU responses consume only
`K4_aaaa`, `K4_aaab`, `K4_aabb`, and `K4_abbb` after transport.  High global
Frobenius fidelity does not bound those contractions after an arbitrary weight
map, and choosing `U` from `G3` supplies no k4 subspace theorem.  The metric
weights unique symmetric entries by ordered multiplicities `1,4,6,4` and must
pass independently in every generated cell.

## Complete non-overlap cost certificate

The carrier-independent source component costs `79,067,438,080` raw and
`98,834,297,600` after one global `1.25` protection factor.  It leaves at most
`53,165,702,400` effective operations for a completely non-overlapping M125
carrier inside the `152e9` envelope.  M125 must be killed on cost if its
non-overlap charge exceeds that allowance.

For provenance, the old M120/M121 carrier assumptions made the full raw ledger
`97,308,438,080` and effective ledger `121,635,547,600`; those totals do not
authorize or validate that killed branch.  The ledger separately charges
factor/eigensolve, tree cores, stars, collision cores, analytic collision
scalars, transport, response work, and copies/allocation.

## Tests actually run

Ten target-free tests pass.  They establish:

1. weighted tree `G3` identity;
2. analytic collision moment identities and independent integration;
3. absence of the zero-mean star vertex;
4. exact implicit collision-corrected `G3` and both projected cores;
5. factor transport and delay-one algebra;
6. permutation and positive-gauge covariance;
7. fail-closed rank-boundary ties; and
8. inert manifest plus sub-ceiling static ledger; and
9. mechanical, no-discretion future gate adjudication; and
10. the ordered `1/4/6/4` repeated-output k4 metric.

They do **not** establish source fidelity, repeated-output k4 fidelity,
correction efficacy, final-network accuracy, or contest score.

## Conditional activation rule

The existing generated source grid can be activated only if all of the
following are true before any M124 outcome is observed:

1. M125 passes a frozen, no-retry dense-source validation of its exact forward
   tangent algebra and complete `(dmu,dC)` response;
2. M125 is hash-locked into M124's manifest as `PASSED_AND_HASH_LOCKED`;
3. the audited non-overlap sum is at most `152e9`, so M125's allowance is at
   most `53,165,702,400` with the current source implementation;
4. an independent reviewer freezes the current widths, alpha scales, Philox
   seeds, rank, and all source/repeated-output gates; and
5. the grid is run once, with any cell failure producing `SOURCE_KILL`.

Until those conditions hold, the correct verdict is `PRESERVE / BLOCKED`, not
promotion and not a claim that M125 has already failed.
