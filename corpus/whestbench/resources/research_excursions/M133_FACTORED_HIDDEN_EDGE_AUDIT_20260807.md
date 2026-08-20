# M133 factored hidden-edge audit -- 2026-08-07

## Decision

**REPAIR COMPONENT / DO NOT PROMOTE / DO NOT RUN AN EFFICACY OR CONTEST
CELL.**  This mutation produced two real operators:

1. fixed-count conductance sampling owns the hard central `ABBA/ABAB` edge
   and the hard `[2,2]` edge without a FLOP-tail risk; and
2. an exact three-bank proposal samples the full `[2,1,1]` collision support
   from an `O(n^2)` setup, evaluates only sampled exact defects, and assembles
   all repeated-output slices with five rectangular products.

The algebra, inclusion law, collision ownership, batching, and frozen-proposal
tangent all pass generated tests.  The complete target envelope does not have
an allocation that passes both the frozen variance gate and the protected cost
gate.  With the minimum-safe edge allocation `k_Q=k_22=640`, `kappa=2` triple
sampling fits at `94.941B` but scales to `1.223x` P8 MSE at width 32.
`kappa=3` repairs that screen to `0.815x` but costs `102.255B` once the exact
sampled-coefficient reserve, new buffers, and a 100 ms wall reserve are
included.  `kappa=4` costs `109.569B`.  The second-order mutation is farther
over budget.

This is generated algebra only.  No challenge model, truth, scorer,
leaderboard row, submission, private/public evaluation, or champion artifact
was read or used.

## 1. Frozen contract and bias class

The exact source contract is M122, including all collision partitions.  The
deterministic M126 source owns every cubic tree term, the identity part of the
hard paths, and the non-hard one/two-label collision contractions.  M133 owns
only three disjoint linear populations:

* one off-diagonal central residual edge of `E=Q-I` in the complete hard AABB
  path orbit;
* one off-diagonal `[2,2]` defect edge; and
* one canonical three-label `[2,1,1]` unit `(i; j<k)`.

The estimators are exactly unbiased in real arithmetic.  Float32 matrix
products estimate the rounded float32 algebra and still require the M126
mixed-precision parity gates.  Seeds, sample counts, the uniform rescue mass,
proposal state, dtype, and association order must be fixed before any outcome.

Independent Bernoulli Horvitz--Thompson sampling was rejected for deployment:
it controls expected work but can select every edge.  Capping its realized
count biases the result.  The audited implementations are:

* fixed-size systematic PPS/HT for the full-catalog reference; and
* fixed-count with-replacement Hansen--Hurwitz (HH) for the deployable
  factored proposal.

Calling the second object HT would be imprecise.  Both are unbiased, but only
HH gives the five-product factored implementation without an `n^3` table.

## 2. Hard path and `[2,2]` edge ownership

Let `A=QW`, and define the symmetric output matrix

```text
D_i[a,b] = gamma2_i (A_ia W_ib + W_ia A_ib).
```

Since `E` is symmetric and hollow, the complete hard path residual is

```text
T_path = 2 D^T E D = sum_(i<j) E_ij F^path_ij,
F^path_ij = 4 (D_i o D_j).
```

Each `F^path_ij` is four rank-one output products.  The `[2,2]` obstruction is

```text
T_22 = sum_(i<j) E22_ij F^22_ij,
F^22_ij = 4 (W_i o W_j)(W_i o W_j)^T,
```

one rank-one product.  These identities match M126's dense small-width oracle
through width seven.

Exact path feature norms do not require output-matrix materialization.  The
four left vectors are

```text
A_i A_j,  A_i W_j,  W_i A_j,  W_i W_j,
```

and the right vectors are their reversal.  Six source-row Grams of `A^2`,
`A*W`, and `W^2` assemble every `4x4` pair Gram.  That is an exact six-GEMM
catalog, but the cheaper independently screened proposal is

```text
q^path_ij proportional |E_ij| ||D_i||_F ||D_j||_F,
q^22_ij   proportional |E22_ij| ||W_i||_2^2 ||W_j||_2^2.
```

For fixed `k`, drawing with replacement and returning

```text
(1/k) sum_s coefficient(e_s) F(e_s) / q(e_s)
```

is unbiased and cliff-safe.  The four path families and one collision family
are batched as five rectangular products, so the hot call count is constant
rather than `5k`.

The independent M126 judge screened this proxy at generated width 64 over 12
seeds.  At equal hard-edge arithmetic (`k=410` per family), source-table MSE
ratios versus Rademacher P8 were `.169--.364`, median `.216`.  This is a
mechanism clue, not output-response evidence.  To keep its worst generated
cell below parity after inverse-cost scaling, the balanced envelope uses
`k_Q=k_22=640` at width 256: `640/1638=.3907` of matched P8 arithmetic, giving
the extrapolated worst ratio about `.364/.3907=.932`.

## 3. Factored `[2,1,1]` proposal

Let `S=abs(Q-I)` and `r_i=||W_i||_2`.  Every coefficient-free repeated-output
feature satisfies the separable bound

```text
||F31_ijk||_F <= 12 r_i^2 r_j r_k,
||F22_ijk||_F <= 12 r_i^2 r_j r_k.
```

The quadratic collision jet has the three connected tree banks.  M133 uses
their absolute conductance envelope on ordered distinct triples:

```text
h_ijk = r_i^2 r_j r_k (
          S_ij S_ik + S_ij S_jk + S_ik S_jk).
```

This distribution is sampled without forming `n^3` probabilities.

### Bank A: repeated label is the centre

Put `a_ij=S_ij r_j` and

```text
D_i = (sum_j a_ij)^2 - sum_j a_ij^2.
```

Choose `i` proportional to `r_i^2 D_i`; choose `j` proportional to
`a_ij(sum a_i-a_ij)`; then choose `k != j` proportional to `a_ik`.  The
resulting ordered probability is exactly proportional to
`r_i^2 r_j r_k S_ij S_ik`.

### Banks B and C: a singleton is the centre

For centre `j`, put

```text
L_i=r_i^2 S_ij,  R_k=r_k S_jk,
D_j=(sum_i L_i)(sum_k R_k)-sum_i L_i R_i.
```

Choose `j` proportional to `r_j D_j`, then `i` proportional to
`L_i(sum R-R_i)`, then `k != i` proportional to `R_k`.  This samples the
`S_ij S_jk` bank exactly.  Exchanging the named centre supplies the third
bank.  Choosing the bank proportional to its analytic normalizer makes the
mixture probability exactly `h_ijk/sum h`.

A frozen `epsilon=.05` uniform ordered-triple mixture gives every distinct
triple positive support, including exact higher-order defects missed by the
quadratic envelope:

```text
q_ijk = .95 h_ijk/Z + .05/[n(n-1)(n-2)].
```

No rejection normalizer is estimated; all collision removal is analytic.
The setup is `O(n^2)`.

## 4. Exact collision coefficient and five-product scatter

For a sampled ordered triple, evaluate the exact M122 defect

```text
Delta_ijk = cumulant(Y_i,Y_i,Y_j,Y_k) - tree(i,i,j,k).
```

The independent M131 conditional-boundary route supplies the unique
trivariate raw moment with paired 32/48-node one-dimensional quadrature; all
remaining partition moments are univariate or bivariate.  M133's protected
worksheet allows 512 float64-billed scalar operations per node, both orders,
and the partition arithmetic.  This is a conservative static reserve, not a
native target trace.

For rows `x=W_i`, `y=W_j`, `z=W_k`, one canonical collision contributes

```text
F31 = 6(x*y*z)x^T + 3(x^2*z)y^T + 3(x^2*y)z^T,

F22 = 2[x^2(y*z)^T + (y*z)(x^2)^T]
    + 4[(x*y)(x*z)^T + (x*z)(x*y)^T].
```

The proposal samples ordered `(j,k)`, so a fixed `K` HH estimate uses weight

```text
Delta_ijk / [2 K q_ijk].
```

The factor two owns every canonical `j<k` unit exactly once in expectation.
The three `F31` outer products and the two symmetric `F22` pairs are five
rectangular matrix products.  Generated tests show bitwise shape ownership
and agreement with direct scatter to `2e-10`.

## 5. Conditional unbiasedness and frozen-proposal tangent

Condition on the complete Gaussian background, full bridge, weights, and
proposal.  For any ordered distinct triple `e`, `q_e>0`, hence

```text
E_q[Delta_e F_e/(2q_e)]
  = (1/2) sum_ordered Delta_e F_e
  = sum_(i,j<k) Delta_ijk F_ijk.
```

The path and `[2,2]` arguments are identical without the ordered-singleton
factor.  Linearity of the one-delay response preserves expectation.  Sampling
the bridge before forming `A=QW` would violate this proof because the same
random edge would enter several factors; M133 never does that.

For second order, freeze `q=q(theta0)` at the unperturbed background and reuse
the same sampled units.  Then

```text
d/dtheta E_q[F_e(theta)/q_e] = E_q[Fdot_e(theta)/q_e].
```

There is no score-function or `qdot` term.  Generated central differences pass
at `3e-8`.  With fixed network weights, `[2,1,1]` needs five additional
rectangular products for `Delta_dot`; the hard path needs eight additional
product-rule families and `[2,2]` needs one.

## 6. Frozen generated variance screen

The screen used four fixed generated seeds at each width, 128 replicates per
cell, Gaussian rows scaled by `1/sqrt(n)`, and the full quadratic collision
jet.  It never accessed challenge data.  The metric was source-table relative
Frobenius MSE on `(aaab,aabb)`.

| width | equal-arithmetic factored HH / P8 | factored HH `K=4n` / P8 |
|---:|---:|---:|
| 12 | .675 | .387 |
| 16 | .674 | .392 |
| 24 | .891 | .523 |
| 32 | 1.047 | .611 |

The pooled `K=4n` ratio is `.533`, but the adverse width trend is binding.
For iid with-replacement averages, MSE scales exactly as `1/K`.  Therefore the
same frozen width-32 cell predicts:

| triple allocation | scaled width-32 ratio |
|---:|---:|
| `K=2n` | 1.223 |
| `K=3n` | .815 |
| `K=4n` | .611 |

The test is favorable to M133: it uses the quadratic jet that defines the
proposal.  Exact cubic-and-higher collision content can only make proposal
misspecification a new uncertainty.  No target-width or output-response claim
is inferred from these values.  M126 already observed that naive source-entry
variance can misstate response variance by factors `.209--5.415`.

## 7. Complete first-order protected envelope

FlopScope's f32 rectangular product bill is

```text
R(K)=2 n K n - n^2.
```

The common base is the protected M126 P0 source `40.144673280B` plus the
independently corrected exact M125b carrier/background `12.819202000B`, or
`52.963875280B`.  Edge samples use `K_Q=K_22=640`.  Proposal setup is charged
at `0.121896960B`.  The sampled-coefficient reserve uses both 32/48-node rules.
New gathers, explicit symmetry, and allocations receive `1.0B`.  A 100 ms
residual-wall reserve costs `10.0B` at `lambda=1e11 FLOP/s`.

| triple kappa | K/layer | edge products | triple products | coefficient reserve | buffers | wall | protected total | gate |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 512 | 16.240B | 12.990B | 1.625B | 1.000B | 10.000B | **94.941B** | cost pass; variance fail |
| 3 | 768 | 16.240B | 19.491B | 2.438B | 1.000B | 10.000B | **102.255B** | cost fail |
| 4 | 1024 | 16.240B | 25.992B | 3.251B | 1.000B | 10.000B | **109.569B** | cost fail |

Reducing the wall reserve to 60 ms would place kappa 3 at about `98.255B`, but
that leaves only `1.745B` margin without a native trace.  The official runner
has previously inflated local residual timings by about fivefold; accepting
this worksheet would violate the over-budget-cliff invariant.

Thus no first-order allocation passes both gates:

```text
kappa 2: affordable, insufficient variance;
kappa 3: variance screen survives, protected cost fails;
kappa 4: stronger variance, larger cost failure.
```

No efficacy run was performed after this preexecution intersection became
empty.

## 8. Second-order cost kill

At `K_Q=K_22=640`, the frozen-proposal edge tangent alone adds
`29.232414720B` protected.  The triple tangent adds the same five-product bill
as the triple primal: `12.990B`, `19.491B`, or `25.992B`.  Exact
`Delta_dot` needs another conditional-boundary reserve, before the M128 second
response and any additional state work.

Consequently kappa 4 is statically over budget even before the complete edge
tangent is attached.  Kappa 3 also fails after all edge/source costs; it does
not fit merely because its isolated 211 primal+tangent table is below 100B.
The frozen-proposal derivative is mathematically preserved, but the present
second-order implementation is killed by complete cost.

## 9. Tests and evidence boundary

Thirteen generated tests pass.  They verify:

1. path-edge sum against the M126 dense hard residual;
2. exact six-Gram feature norms;
3. `[2,2]` edge ownership;
4. all twelve `[2,1,1]` slots against the dense collision oracle;
5. the separable norm bound;
6. water-filled first-order inclusion probabilities;
7. exact systematic-PPS inclusion by phase partition;
8. exact HT expectation for all three disjoint populations;
9. exhaustive hollow-Rademacher expectation;
10. factored proposal normalization and full support;
11. empirical sampler agreement with its declared law;
12. direct-versus-five-product HH equality; and
13. frozen-proposal tangent finite differences.

They do not prove target-width runtime, float32 parity, response-level
variance, exact-collision proposal quality beyond the quadratic jet, or final
network efficacy.

## 10. Relation to prior randomized algebra

The hierarchical construction is consistent with known work showing that
enormous row-product distributions can sometimes be sampled without
materializing the product: Bharadwaj et al., *Fast Exact Leverage Score
Sampling from Khatri--Rao Products*, arXiv:2301.12584, and Larsen--Kolda,
*Practical Leverage-Based Sampling for Low-Rank Tensor Decomposition*,
arXiv:2006.16438.  Those papers do not prove M133; this report derives and
tests its exact proposal directly.  The five-product estimator is also in the
classical lineage of unbiased sampled outer-product/Gram approximations;
Holodnak--Ipsen, arXiv:1310.1502 / DOI 10.1137/130940116, provides relevant
analysis, not a contest-specific guarantee.

## Final disposition and salvage map

Preserve:

* the disjoint collision-ownership proof;
* fixed-count batched conductance edges;
* the exact `O(n^2)` three-bank proposal with uniform rescue;
* five-product `[2,1,1]` assembly;
* frozen-proposal pathwise differentiation; and
* the full protected envelope and adverse width scaling.

The killed implementation is the **balanced M133 allocation under the current
source and carrier**, not the whole importance-sampling family.  Reopen only
if a new mechanism changes a failed link: a stronger exact-defect proposal
without `n^3` work, a measured fused trace that safely supports kappa 3 with
margin, a source/carrier call reduction of at least several billion protected
operations, or an output-response variance proof showing fewer triple samples
are sufficient.  Parameter drift, seed retry, reducing the wall reserve after
seeing an outcome, or dropping the exact higher-order collision tail does not
count as a repair.
