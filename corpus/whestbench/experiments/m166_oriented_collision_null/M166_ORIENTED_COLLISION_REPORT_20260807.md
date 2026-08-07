# M166 oriented all-collision-null covariance-star control -- 2026-08-07

## Disposition

**The exact f64 compiler is static-cost killed; preserve the orientation and
seven-product compiler.** This is generated-array theory/static work only. No
response, source-variance outcome, truth, error, scorer, competition row,
leaderboard, submission, champion, or M145 state was opened or changed.

M166 changes one mechanism: the covariance-star coefficient. It does not
alter the complete-domain add/subtract identity inherited from M156. The
control is valid on every ordered triple and therefore its residual has the
same full support. No explicit collision-label mask appears in the control or
the deployed compiler.

## Canonical score and orientation

For a finite symmetric covariance `V` with positive diagonal, form

```text
R_ij = V_ij / sqrt(V_ii V_jj),
s_i  = max_{ell != i} R_iell^2.
```

`s_i` is a scalar of correlation row `i`. The off-diagonal maximum is a
multiset operation, so under a simultaneous label permutation it simply
permutes with the labels. Under a positive diagonal gauge `V' = D V D`,
`R'=R` and the scores are unchanged in exact arithmetic.

For `i != j`, set

```text
A_ij = V_ij              if s_i > s_j, otherwise 0,
B    = A^T,
A_ii = B_ii = 0.
```

Thus every non-tied covariance edge is assigned one orientation. An exact
working-representation score tie assigns neither orientation: `A_ij=B_ij=0`.
There is no index-based secondary ordering. This is the certified
tie-to-zero rule, including the fully tied equicorrelation/isotropic case.
Because `B=A^T`, `A_ij B_ij=0` exactly at every ordered location.

The control is

```text
c_ijk = -(A_ij B_ik + B_ij A_ik) = c_ikj.
```

## Collision proof

No collision predicate is needed in the formula.

```text
c_iik = -(A_ii B_ik + B_ii A_ik) = 0,
c_iji = -(A_ij B_ii + B_ij A_ii) = 0,
c_ijj = -(A_ij B_ij + B_ij A_ij) = 0,
c_iii = 0.
```

The first two use the exact zero diagonal; the third uses disjoint supports.
IEEE signed zero may carry a negative sign after the outer negation, but it is
exactly numerically equal to zero and no collision entry is repaired with a
mask. The generated width-6 trace reports collision maximum absolute value
`0.0`; the unit suite exhausts all four patterns.

For positive `D`, orientation is unchanged and
`A'=DAD`, `B'=DBD`. Hence
`c'_ijk=d_i^2 d_j d_k c_ijk`. With `W'_i=W_i/d_i`, every degree-four source
feature cancels that factor. This proves positive-gauge covariance of the
real-arithmetic source. The same permutation argument gives permutation
covariance. The generated f64 trace has source discrepancies `2.27e-13`
(permutation) and `3.41e-13` (positive gauge).

## Exact full-domain compiler

Let `ZA=AW`, `ZB=BW`, `U=ZA o ZB`, and define

```text
P   = (W o U)^T W,
QAB = (W^2 o ZA)^T ZB,
QBA = (W^2 o ZB)^T ZA,
R   = (W^2)^T U,
S   = (W o ZA)^T (W o ZB).
```

Direct expansion of the half-owned M156 feature gives

```text
C_aaab = -3 (2P + QAB + QBA),
C_aabb = -2(R + R^T) - 4(S + S^T),
C_aaaa = diag(C_aaab).
```

The seven dense products are `ZA`, `ZB`, `P`, `QAB`, `QBA`, `R`, and `S`.
`oriented_star_table` exists only as a small-width test oracle; the compiler
uses neither a cubic coefficient table nor a Khatri--Rao/Kronecker action.
The generated exhaustive width-6 comparison is `4.55e-13` maximum absolute
source difference.

## Cost audit against the 14.0191212B compiler slot

At `n=256`, 31 source layers, and inherited 1.25 protection, one f32 square
product family is `1,297,694,720` and f64 is twice that. M166 needs seven,
not five, dense product families.

| variant | seven dense products | correlation/orientation/compiler-pointwise/copy allowance | total | margin to 14.0191212B |
|---|---:|---:|---:|---:|
| exact f64 | 18,167,726,080 | 325,058,560 | 18,492,784,640 | **-4,473,663,440** |
| shared-control f32 | 9,083,863,040 | 162,529,280 | 9,246,392,320 | +4,772,728,880 |

The allowance is charged as `64*n^2` per layer before the 1.25 protection:
10 for covariance/correlation/score, 10 for orientation, 28 for compiler
pointwise transformations, and 16 for casts, copies, and storage shared with
the residual arm. It intentionally does not claim an omitted operation,
copy, or orientation for free.

Therefore the exact f64 implementation is killed at the static budget gate.
No native trace was run or implied.

## Float32 semantics (not a promotion)

The f32 accounting is retained only as a separate numerical candidate. One
stored f32 `OrientedEdges(A,B)` object is passed to the deterministic compiler
and used again to subtract the sampled residual control; it is never
recomputed by a different orientation path. In the generated probe,
`c + (target-c)` had maximum coefficient discrepancy `9.23871994e-7` and was
not bitwise equal to `target`. Positive-gauge covariance is likewise a
real-arithmetic theorem, not a bitwise f32 guarantee near score ties.

Consequently f32 has no exact-conservation, numerical-stability, native-cost,
or source-variance credit. A future descendant would need to lock its dtype
contract, use the exact same stored A/B in both arms, pass a numerical
conservation/gauge gate, and pass a complete native resource trace before any
source-variance premise could open.

## Recursive salvage map

- **Preserved component:** all-collision-null orientation with tie-to-zero.
- **Preserved component:** exact real-arithmetic seven-product compiler and
  permutation/positive-gauge theorem.
- **Killed implementation:** exact f64 target compiler (`18.493B > 14.019B`).
- **Unresolved family:** shared f32 numerical implementation; no outcome or
  native evidence exists, and no parameter/score retuning is authorized.
