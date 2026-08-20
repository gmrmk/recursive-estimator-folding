# M170: tensor-rank audit of M166's oriented all-collision-null compiler

## Disposition

**KILLED STATIC: no exact `<=5` dense-product-family compiler exists in the
audited M166 compiler model.** The lower bound is seven dense product
families: two independent node-axis projection channels and five terminal
source contractions.  Thus six f64 square families alone cost
`15,572,336,640`, already above the `14,019,121,200` slot before any
pointwise, orientation, allocation, or copy work.

This is response-free algebra only.  It did not access a response, source
variance outcome, target, scorer, contest/model data, leaderboard,
submission, champion, native trace, or estimator state.  M166's orientation,
tie rule, dtype contract, complete-domain add/subtract identity, and M167's
physical-owner rule are unchanged.

## Prediction and kill condition

The mechanism tested was narrowly predeclared:

```text
Try to replace M166's seven product families by an exact <=5-family compiler
for c_ijk = -(A_ij B_ik + B_ij A_ik), B=A^T,
using only C_aaab and C_aabb, polarizations, common subexpressions, and
lawful M167 owner retirement.
```

The kill condition was a nonzero-rank symbolic flattening on an *admissible*
M166 orientation cell, not an arbitrary unconstrained `A,A^T` example.  It
must show two independent initial channels, rank three in the ordered
`aaab` output, and symmetric-pair rank two in `aabb`.  That condition passed.

## Exact normal form and symbolic monomials

This is a lower bound for the relevant dense-product-family normal form:

1. dense products acting on the node axis;
2. rowwise pointwise expressions, copies, and reshapes;
3. output-axis Gram products, whose transpose can be reused only for the
   symmetric `aabb` output;
4. free linear recombination of already formed output matrices.

A rectangular/block call is charged by scalar product volume,
`2mkn-mn` in f32 (twice for f64). Concatenating two channels therefore does
not turn their work into one family.  This excludes neither a future
structured-kernel proof nor a different arithmetic-circuit class; it prevents
renaming a wider product or a pair of blocks as a product-rank reduction.

Put, for fixed hidden row `i`,

```text
x = W[i,:],       p = (A W)[i,:],       q = (A^T W)[i,:].
```

The exact M166 source, ignoring the common nonzero scalar factors, is

```text
C_aaab:  2 (xpq)^T x + (x^2p)^T q + (x^2q)^T p,

C_aabb:  (x^2)^T(pq) + (pq)^T(x^2)
          + 2[(xp)^T(xq) + (xq)^T(xp)].
```

The ordered `aaab` coefficient flattening in bases
`(xpq, x^2p, x^2q)` and `(x,q,p)` is

```text
diag(2, 1, 1),
```

so it has rank three and needs three output products.  `aabb` is symmetric:
one product can supply a term and its transpose.  Its two unordered feature
pairs are

```text
{x^2, pq},  {xp, xq},
```

with symmetric-pair flattening `diag(1,2)`, hence rank two and two output
products.  These two source blocks have separate output tags and different
output multidegrees (`3+1` versus `2+2`), so one terminal product cannot be
reused in both blocks: doing so would inject the same nonzero polynomial into
both output coordinates, where the other target is identically zero.

Before them, the coefficient has two independent node-axis forms, `p=AW` and
`q=A^T W`; their projection flattening is `I_2`.  Consequently the exact
lower bound in this model is

```text
2 projection families + 3 ordered aaab families + 2 symmetric aabb families
= 7 dense product families.
```

Pointwise operations, copies, and reshapes have no node-axis reduction and
cannot lower any of these flattening ranks.

## Admissible specialization / rank certificate

The certificate uses `C=N/100`, where

```text
N = [[100,45, 7, 6, 4, 3], [45,100, 8, 5, 5, 4],
     [ 7, 8,100,30, 6, 5], [ 6, 5,30,100, 7, 6],
     [ 4, 5, 6, 7,100,15], [ 3, 4, 5, 6,15,100]].
```

`C` is strictly diagonally dominant, hence SPD.  Its exact row-score tiers,
scaled by `10^4`, are `(2025,2025,900,900,225,225)`.  M166 therefore assigns
the cross-tier entries to the strict upper triangle and gives neither member
of a tied pair an edge.  This is a lawful tied-score orientation cell; it is
not a relaxation to arbitrary `A`.

At middle-tier row `i=2`, using the integer 6-by-7 weight fixture recorded in
the source, the following exact minors are nonzero (the actual `p,q` each
carry an irrelevant common `/100` factor):

| witness | numerator determinant | implication |
|---|---:|---|
| `det[p,q]_(0,1)` | `-114` | two independent projection channels |
| `det[xpq,x^2p,x^2q]_(0,1,2)` | `-1,297,824` | left `aaab` basis has rank 3 |
| `det[x,q,p]_(0,1,2)` | `686` | right `aaab` basis has rank 3 |
| `det[x^2,pq,xp,xq]_(0,1,2,3)` | `1,505,876` | four `aabb` features are independent |

This rank-flattening certificate is exact integer arithmetic in the frozen
test, rather than a numerical-rank inference.

## Exhaustive source parity

An independent ordered-triple expansion was compared with the seven-product
formula on generated widths 2 through 7.  Width 2 is included deliberately:
with only one off-diagonal partner the two M166 scores tie, so the lawful
control is zero.  The maximum source discrepancies were:

| width | max absolute source difference |
|---:|---:|
| 2 | `0.0` |
| 3 | `0.0` |
| 4 | `1.39e-17` |
| 5 | `8.88e-16` |
| 6 | `2.26e-16` |
| 7 | `1.05e-15` |

The same sweep verifies `iii`, `iik`, `iji`, and `ijj` collision coefficients
are zero without a collision mask.  This preserves M166's existing identity;
it does not create a replacement compiler.

## Cost and ownership implications

At width 256, 31 source layers, and the inherited 1.25 protection:

| item | protected f64 bill |
|---|---:|
| one square product family | `2,595,389,440` |
| six families, before any pointwise/copy work | `15,572,336,640` |
| seven families | `18,167,726,080` |
| seven plus charged pointwise/copy allowance | `18,492,784,640` |

The conservative f64 pointwise/copy allowance is `325,058,560` (correlation,
scores, orientation, compiler pointwise maps, casts, copies, and shared
storage).  A block product is not credited merely because it makes fewer API
calls: its full rectangular scalar-product bill is required.

M167 ownership remains exactly as frozen.  M166's collision-null control
cannot lawfully absorb physical `[4]`, `[3,1]`, or `[2,2]` owners merely by
being zero on those entries.  In particular, M167 already disproved the
generic `K22=-4 A^2` identification.  No owner retirement, residual change,
or estimator alteration is authorized by this rank audit.

## Preserved salvage, deliberately not merged

Sorting by the scalar score makes `A` strictly triangular and `B=A^T` the
opposite strict triangle.  Their *combined nonzero scalar multiply count* for
the two initial maps is `n(n-1)m`, equal to one dense off-diagonal action.
This is a separate structured triangular-kernel hypothesis, **not** a tensor
rank reduction: it leaves the two independent channels and the seven-family
lower bound intact.

It receives no current cost, exactness, or dispatch credit.  A descendant
would need an exact f64 triangular implementation, complete permutation /
gather / allocation / copy accounting, and a native trace.  Only after that
independent validation may it be factorial-tested with separately validated
L2 Strassen or cross-layer batching.  No such test was opened here.

## Recursive salvage map

- **Killed implementation:** any claimed exact `<=5` dense-product-family
  compiler in the audited M166 normal form.
- **Preserved component:** M166's seven-product exact real-arithmetic
  compiler and its all-collision-null orientation.
- **Preserved constraint:** a genuine replacement must escape the proved
  normal form with a new exact factorization and full scalar-work proof; a
  block/rectangular repackaging is insufficient.
- **Unresolved separate family:** exact triangular structured kernels for the
  two initial projections, with no presently claimed effect or cost credit.

