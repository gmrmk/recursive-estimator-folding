# M123 independent theory audit — implicit Krylov bridge source

## Verdict: KILL

The M122 repair edge is real but cannot be promoted in the requested form.
The 144 zero-mean fourth-order path-pair contractions collapse exactly to 16
symmetry orbits.  Thirteen yield explicit dense matrices in 19 shared square
GEMMs per layer, and three generic Khatri--Rao orbits share an exact action of
eight square GEMMs per vector.  Generated widths `2,...,8` match the dense
mode-1 Gram and its action to `3.98e-13`.

The minimal nontrivial rank-four block Krylov factor is
`span{Z,GZ}`.  A fail-closed residual requires the second block action.  Across
31 layers, the necessary zero-mean path subset costs `215.417B` with float64
and one 25% safety factor.  Even applying a favourable but unproved `0.779`
Strassen multiplier to every square call leaves `167.810B`, already above the
entire `152B` incremental allowance.  All nonzero-mean sources, cores,
collisions, response assembly, CP pairing, and memory operations are positive
additional work.

No efficacy outcome, manifest, contest model, public/private datum, scorer,
champion, or submission was used.

## Exact orbit algebra

Let

```
H=Q circ Q,  R=Q^2,  s=H1,
X=QH,        A=Q diag(s)Q,  B=QHQ,
M=Q circ R.
```

For representative orbit matrix `K_o`, the full Gram contribution is `6K_o`
for a size-six orbit and `6(K_o+K_o^T)` for a size-twelve orbit.

| o | size | exact representative matrix |
|---:|---:|---|
| 0 | 6 | `Q diag(Hs) Q` |
| 1 | 6 | `Q diag(diag(B)) Q` |
| 2 | 6 | `Q (H circ R) Q` |
| 3 | 12 | `Q [Q circ X] Q` |
| 4 | 6 | `X X^T` |
| 5 | 12 | `Q [Q circ A]` |
| 6 | 12 | `Q [Q circ B]` |
| 7 | 12 | `X [Q circ R]` |
| 8 | 12 | `Q D^T`, `D_bj=(q_b circ q_j)^T Q(q_b circ q_j)` |
| 9 | 12 | `Q [Q circ (Q M)]^T` |
| 10 | 12 | `Q [Q circ (R H)]^T` |
| 11 | 6 | `R circ A` |
| 12 | 6 | `R circ B` |
| 13 | 6 | `M M` |
| 14 | 12 | `sum_jkl Q_aj Q_ak Q_kl Q_jl Q_bl Q_bk` |
| 15 | 6 | `sum_jk Q_aj Q_bj R_jk Q_ak Q_bk` |

Orbits 8, 14, and 15 are the hard set.  For an input `x`, define

```
C  = Q diag(x) Q
E  = Q circ C
v  = Qx
Cv = Q diag(v) Q.
```

Their exact actions are

```
K8 x    = Q diag(Q E Q)
K8^T x  = diag(Q [Q circ Cv] Q)

K14 x   = rowsum((R E) circ Q)
K14^T x = diag(Q [Q circ (Q C)]^T Q)

K15 x   = diag(Q [R circ C] Q).
```

The common `C` and `E` reduce their combined action to eight
`(256,256)@(256,256)` calls per vector.  `G_easy @ Z` is a further
`(256,256)@(256,4)` call; vector products have shape
`(256,256)@(256,1)`.  These lower-order calls and all elementwise/copy charges
were omitted from the fatal lower bound, so the conclusion is conservative.

The shared 19-GEMM construction is:

- four products for `R`, `X`, `A`, and `B`;
- one each for orbits 0 and 1;
- two each for orbits 2 and 3;
- one each for orbits 4, 5, 6, and 7;
- two each for orbits 9 and 10; and
- one for orbit 13.

Orbits 11 and 12 are Hadamard combinations of shared matrices.

## Why deterministic Krylov theory does not provide a cheaper schedule

Block size four is minimal.  A zero-degree subspace `span Z` needs one Gram
block action to measure its residual but performs no spectral filtering.  The
first nontrivial polynomial subspace `span{Z,GZ}` needs a second action to form
the block-Lanczos residual.  For any fixed rank-four start and absent a proved
overlap/gap, deterministic bounds contain the uncontrolled factors
`tan angle(Z,U4)` and `(lambda5/lambda4)^q`.  They cannot select a finite `q`
from dimensions alone.

The permutation-equivariant start

```
Z=[1,Q1,(Q circ Q)1,Q((Q circ Q)1)]
```

also exposes the exact symmetry obstruction: at `Q=I` it has rank one, and no
deterministic pathwise permutation-equivariant rule can select a distinguished
rank-four subspace from the fully symmetric coordinate representation.  The
only honest behaviour is fail-closed.  Random fixed coordinates would break
the requested pathwise permutation covariance.

A residual `E=GU-U(U^TGU)` is necessary but insufficient to prove the leading
subspace.  A strict certificate additionally needs an upper bound on the
complement spectrum and a positive fourth/fifth separation; a disjoint pair
of Ritz intervals alone does not count the unseen eigenvalues.  M123 therefore
requires a true complement bound and fails closed if it is absent or tied.
Computing that bound cannot reduce the two-action lower bound.

## Nonzero-mean and ownership boundary

For `alpha != 0`, the degree-three local Hermite vertex is
`c3=-sigma alpha phi(alpha)/6`, so fourth-order stars reappear in addition to
the weighted path family.  The sixteen formulas above are a necessary
zero-mean subset only.  Repeated one/two-coordinate entries also require a
new nonzero-mean bivariate source.  M85/M122 supplies neither.  Since the
necessary subset already exceeds compute, the missing terms cannot reverse
the verdict.

M123 must remain separate from terminal Born unless an exact LLQ/LLLC/LLQQ
intersection subtraction is supplied.  No such subtraction or outcome was
introduced.

## Preserved repair edge

The orbit-fused operator is worth keeping.  It changes M122's apparent 144
independent contractions into thirteen reusable matrices plus only three hard
actions.  It may support a genuinely different static Tucker factor,
single-source insertion, or direct response contraction.  It does not make
the all-layer certified rank-four Krylov construction fit.

