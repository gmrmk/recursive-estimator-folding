# M122 — bridge-tree Tucker factor construction audit

## Decision

**REPAIR, not IMPLEMENT_COMPONENT.**

Two useful exact operators survive:

1. the zero-mean M85 `k3` tree has a non-materialising mode-1 Gram in
   `O(n^3)`; and
2. once a factor is genuinely supplied, the `k4` tree core is exactly
   obtainable by path contractions without an `n^4` tensor.

The requested target-valid rank-4 `k4` HOSVD factor does **not** yet follow.
The full mode-1 Gram contains a generic Khatri--Rao quadratic subnetwork.  It
has an `O(n^3)` *matvec* but no fixed, target-costed finite procedure here for
its top four eigenspace.  Explicit Gram construction exposes an `n^4` shaped
matmul; direct tensor HOSVD is far over budget.  Thus M122 preserves an
implicit spectral-operator repair, while killing the claim that M85's reported
`0.580B` already includes a target rank-4 factor construction.

This is generated algebra only.  It does not read any contest model, labels,
scorer, public/private evaluation, submission, or champion artifact.

## 1. Standardised source and the exact `k3` Gram

Work in the standardised hidden coordinates.  Let `Q=Q^T` be the M85 signed
pair bridge, and suppress the common `gamma_2` factor.  The all-index tree
polynomial is

```
S3_ijk = Q_ij Q_ik + Q_ij Q_jk + Q_ik Q_jk.
```

The actual M85 source replaces entries with one or two distinct coordinates
by its deterministic univariate/bivariate rule.  That is a sparse correction:
only `O(n^2)` ordered entries total, hence it can be added to the following
mode-Gram contractions in `O(n^3)` without materialising `S3`.

Put

```
R = Q Q                         H = Q circ Q
r = H 1                         F = (Q circ R) Q
K = Q H Q.
```

For `G3_ab = sum_jk S3_ajk S3_bjk`, direct expansion of the nine pairings is

```
G3 = R circ R + 2 Q diag(r) Q + 2 K + 2(F + F^T).                 (1)
```

For example, the `A_a=Q_aj Q_ak` with `B_b=Q_bj Q_jk` pairing is
`F_ab`; the `B_a` with `C_b=Q_jk Q_bk` pairing is `K_ab`.  Equation (1)
uses five ordinary dense `n` by `n` products and elementwise operations, so
it is an exact `O(n^3)` source-factor primitive.  It has been checked against
dense tensors for every generated width `2,...,8`.

## 2. `k4` as a path tensor network

Let `P4` be the 12 labelled undirected paths on the four slots.  The all-index
tree polynomial is

```
S4_ijkl = sum_(p in P4) Q_{p0,p1} Q_{p1,p2} Q_{p2,p3}.            (2)
```

Again, M85's one/two-coordinate source rule is a sparse correction to (2),
not a reason to materialise it.  If `U` is an already-valid `n by r` factor,
the projected core is exact from (2):

```
C_pqrs = sum_(path in P4) a^T Q diag(b) Q diag(c) Q d,            (3)
```

where `(a,b,c,d)` are the four selected columns of `U` ordered by that path.
For rank four, there are `C(7,4)=35` symmetric entries, each with twelve paths
and three `Q` matvecs.  The generated small-width equality between (3) and a
dense four-way projection is at most `6.83e-13` over widths `2,...,8`.
The exact one/two-coordinate M85 addendum has only `n + 7n(n-1)` ordered
entries for order four.  Its core can therefore be added directly in
`O(n^2 r^4)`; generated widths `2,...,6` verify the complete tree-plus-sparse
core to `1e-10`.  It is not a hidden dense tensor.

The mode-1 Gram is itself an exact sum of 144 tensor networks:

```
G4_ab = sum_(p,q in P4) sum_jkl
        [path_p(a,j,k,l)] [path_q(b,j,k,l)].                      (4)
```

This is the correct non-materialising definition; it is not an assertion that
the 144 networks may be omitted or treated as a free HOSVD.

## 3. The exposed obstruction, and the useful escape hatch

Choose the two paths

```
j-a-k-l       and       k-b-j-l.
```

Their contribution to (4) is

```
H_ab = sum_jk Q_aj Q_bj (Q^2)_jk Q_ak Q_bk.                       (5)
```

Equivalently, with `B_(j,k),a = Q_aj Q_ak`,

```
H = B^T diag(vec(Q)) B,
```

an `n^2 by n` Khatri--Rao factor on both sides.  For arbitrary dense bridge
`Q`, it is not a low-rank M90 factor: M90 has already measured the bridge's
broad, Wishart-like off-diagonal bulk rather than a stable low-rank spike.
Building all `H_ab` by the visible shaped matmul is therefore
`(n by n^2) (n^2 by n)`, i.e. an `n^4` operator under FlopScope's per-call
shape accounting.

There is nevertheless a real non-materialising *matvec* identity.  For a
given `x`, define

```
C = Q diag(x) Q
Hx = diag( Q [ (Q^2) circ C ] Q ).                                (6)
```

The last diagonal is a rowwise inner product after one dense product, so (6)
is `O(n^3)` rather than `O(n^4)`.  Widths `2,...,8` verify both (5) and (6)
against the explicit path tensors to `3.56e-15`.

More generally, contract `b` against an input vector in any one of the 144
path-pair networks in (4).  The `b` vertex has degree at most two, so this
creates only a unary or pair factor.  The remaining graph is the union of a
path containing `a` and a path/edge on the other three labels.  Exhaustive
enumeration of all 144 labelled pairs finds post-`b` induced width at most two
(minimum one, maximum two).  Hence every *individual Gram matvec term* has a
matrix/Hadamard `O(n^3)` contraction.  This is the legitimate repair clue:
an implicit block-Krylov source factor is mathematically possible.

It is not yet a target component.  A rank-four HOSVD is defined by the four
leading eigenvectors of the **full** `G4`.  A finite Krylov run only gives Ritz
vectors.  To make it legal and reproducible it must fix the start block, max
iterations, reorthogonalisation, residual/gap certificate, tie handling,
fallback, actual contraction fusion, allocation schedule, and a complete
FlopScope bill.  None is present in M85 or M122.  Treating asymptotic
`O(n^3)` notation as a priced target implementation would repeat the M121
error.

## 4. Target ledger (`n=256`)

All figures below use FlopScope's matrix-multiply shape bill
`2mkn-mn`; the float64 multiplier and 25% contingency are explicitly shown.

| operation | shape / storage | f32 bill | float64 x2 + 25% |
|---|---:|---:|---:|
| Direct `S4` storage | `256^4` values | — | 32 GiB before workspace |
| Direct mode-1 Gram | `(256, 16,777,216) @ (16,777,216, 256)` | 2,199,023,190,016 | 5,497,557,975,040 |
| One exposed (5) Gram term | `(256, 65,536) @ (65,536, 256)` | 8,589,869,056 | 21,474,672,640 |
| Exact (1), conservative five dense products | five `256 by 256` products | 167,444,480 | 418,611,200 |
| Rank-4 tree core (3) | 1,260 `Q` matvecs | 164,828,160 | 412,070,400 |

The direct mode Gram is about `21.3x` the full `258.4B` candidate ceiling by
itself.  Even the **single exposed term** in (5), if paid independently at
each of 31 proposed source layers, is `665.715B` charged, before M120's
already-audited Gaussian/adjoint work and before the other 143 terms.  An
uncertified `0.779` L2-Strassen discount would still leave about `518.6B` for
that one repeated term.  Strassen can reduce an accepted matrix-product bill;
it does not turn a generic `n^2 by n` Khatri--Rao factor into rank four.

The implicit-matvec route avoids this *storage/explicit-Gram* price but has no
fixed constant or convergence certificate yet, so it deliberately receives no
optimistic target ledger.  This is the principal non-working link, not an
excuse to hide the cost.

## 5. Permutations, positive gauges, and degeneracies

Do the factorisation in standardised coordinates.  Under a hidden permutation
`P`, `Q' = P^T Q P`, so equations (1)--(6) are conjugated by `P`; the spectral
projector is equivariant.  Individual signed eigenvectors need not be: their
signs and any rotation within a repeated eigenspace are arbitrary, while the
reconstructed Tucker tensor is unchanged if the core receives the matching
orthogonal coordinate change.

For a positive ReLU gauge `D`, use physical scales `s` and a standardised
factor `U`:

```
V = diag(s) U,       V' = diag(Ds) U = D V.
```

With `h'=D h, W'=D^-1 W`, `W'^T V'=W^T V`.  Thus standardise first, restore
scales only in the physical factor, and never take an Euclidean HOSVD of the
unstandardised source.  The original M85 `hosvd_shared` did the latter, so it
did not supply this gauge guarantee.

A future fixed-rank component must fail closed if the fourth/fifth Ritz gap is
not certified.  Choosing one vector from a tied eigenspace by coordinate order
is not permutation covariant.

## 6. Exact boundary and next fold

This audit does **not** revive 31 M85 sources: present M85 is zero-mean only,
whereas later Gaussian background layers have nonzero means.  The valid next
mutation is narrower:

1. implement a standardised, deterministic block-Krylov `G4` operator using
   all 144 path-pair contractions (with fusion demonstrated, not assumed);
2. predeclare a residual/gap fail-closed criterion and a maximum priced
   iteration count;
3. add the exact sparse one/two-coordinate correction to both the Gram action
   and core;
4. compare its rank-4 reconstruction with dense M85 HOSVD at widths 8, 12,
   and 16, including simultaneous permutation/gauge transforms; and
5. only then produce a non-overlapping one-source cost ledger.  A nonzero-mean
   source and a diagram-incidence subtraction remain separate M121 gates.

Until that changed mechanism exists, do not promote it into M120/M121, charge
it as `0.580B`, or combine it with terminal Born diagrams.

## Reproduction

```powershell
& '..\\..\\headroom-recursion\\.venv\\Scripts\\python.exe' -m unittest -v test_m122_tree_factor.py
& '..\\..\\headroom-recursion\\.venv\\Scripts\\python.exe' run_m122.py
```

The runner writes `results.json`, whose source-free checks are all at or below
`1e-10`.
