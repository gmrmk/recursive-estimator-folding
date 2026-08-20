# M140 -- quadratic `[2,1,1]` residual-control audit

Date: 2026-08-07.  This pass uses generated arrays and the already-installed
M131 conditional-boundary coefficient oracle only.  It did **not** access a
challenge model, truth, scorer, leaderboard, submission, champion archive,
M121 response conversion, or M125 propagation.

## Decision

**KILLED IMPLEMENTATION BEFORE AN OUTCOME SCREEN.**

The source-level decomposition is exact, has a correct frozen-proposal
tangent, and exposes one useful units correction.  It nevertheless cannot be
deployed under the requested contract:

1. the complete quadratic jet has an unresolved masked `aabb` split-pair
   contraction, so there is no verified deterministic `O(n^3)` implementation
   of *all* M121 repeated tables; and
2. even an unrealistically optimistic partial deterministic contraction costs
   `5.190778880B` protected f32 operations, above the `5B` incremental cap,
   before its remaining `aabb` term, scalar work, allocations, or residual HH
   estimate are charged.

The two predeclared target-free coefficient cells also give an adverse local
signature: residual fixed-proposal influence variance is `1.2216x` and
`1.2662x` that of the full exact coefficient.  That is a source diagnostic,
not a network-outcome result; it reinforces the pre-execution kill but is not
used to make a competition-performance claim.

## 1. Exact partition and its units

For distinct standardized bridge labels `(i,j,k)`, define

```text
J_ijk = [Q_ij Q_ik + Q_ij Q_jk + Q_ik Q_jk] / (4 pi),
R_ijk = D_ijk - J_ijk,
```

where `D_ijk` is the exact connected-minus-tree `[2,1,1]` coefficient.  Thus
on the existing canonical source support,

```text
P_[211] D = P_[211] J + P_[211] R.                     (M140.1)
```

M131 returns a *physical* ReLU cumulant.  This pass corrects a crucial
comparison-of-units issue: before subtracting the dimensionless bridge jet,
the physical coefficient must be standardized as

```text
D_ijk = Dphys_ijk / (s_i^2 s_j s_k),
```

where `s` is the ReLU scale.  Transport then uses
`U = diag(s) W`; hence the physical source is restored exactly without a
fitted coefficient.  Under a positive ReLU gauge
`s -> s*g, W -> W/g`, `U` is unchanged.

No artificial diagonal extension is permitted.  If the polynomial were
unmasked, then `j=k` creates `c S_ij^2` on `[2,2]`, while `j=i` or `k=i`
creates `c S_ik^2` on `[3,1]`.  Hiding those new populations inside the
control would move collision ownership and require a new exhaustive residual
estimator.  M140 keeps `[4]`, `[3,1]`, `[2,2]`, and all-distinct populations
with their previous owners.

## 2. Repeated-output table boundary

The M121 interface needs `k4_aaaa`, `k4_aaab`, and `k4_aabb`.

* M130's cubic identity supplies `k4_aaab` exactly; by fourth-tensor
  symmetry, `k4_aaaa = diag(k4_aaab)` exactly.
* The repeated-pair part of `k4_aabb` is also cubic and exact.
* The remaining split-pair part is nonzero on generated width six and contains
  the masked diagonal term

```text
C_ab = (W_:a o W_:b)^T (S o S) (W_:a o W_:b).           (M140.2)
```

For all output pairs `(a,b)`, (M140.2) is a Khatri--Rao quadratic action with
`n^2` column-pair features.  M130's exact construction removes it with a
Rademacher estimator; it is not an `n x n` matrix product.  No exact cubic
contraction for this fully masked term was constructed or certified here.
This is a boundary of the implementation, not a general lower-bound theorem
about every conceivable algebraic algorithm.

Consequently a scheme that deterministically adds only the `aaab` and
repeated-pair pieces while HH sampling `R` is incomplete: it has omitted the
jet's own split-pair source.  Sampling that leftover would no longer be
"sample only the exact residual" and does not meet this M140 contract.

## 3. Unbiasedness, tangent, and symmetries -- passed algebra gates

Let a frozen full-support ordered-triple law be `q0(i,j,k)>0`; M133/M139's
five-percent uniform rescue satisfies this.  With the same `U` above,

```text
E_q0[ R_ijk F_ijk / (2 q0(i,j,k)) ]
    = sum_(i,j<k) R_ijk F_ijk.
```

The factor two accounts for the two singleton orders.  Adding the complete
deterministic transport of `J` gives the exact `P_[211]D` transport by
(M140.1), with no overlap with other collision strata.

For a direction `theta`, freeze `q0` before differentiating.  The coefficient
and source product rules are

```text
Jdot = [a_dot(b+c) + b_dot(a+c) + c_dot(a+b)]/(4 pi),
Rdot = Ddot - Jdot,
d E_q0[R F/q0] = E_q0[(Rdot F + R Fdot)/q0].            (M140.3)
```

Scale-standardization contributes the exact logarithmic derivative
`2 sdot_i/s_i + sdot_j/s_j + sdot_k/s_k`; no scale term is dropped.  There is
no `qdot` score term.  Permuting the source labels conjugates `Q` and permutes
the rows of `U`, leaving every output table unchanged.  Positive-gauge and
permutation tests pass.

## 4. Protected cost gate -- failed before execution

Granting reuse of `Q@W` and every existing M133/M126 intermediate, the
verified M130 `aaab`/repeated-pair formula still introduces at least these four
new f32 square products per source layer:

```text
(S o S)@W,  (S o S)@(W o W),  S@(W o (Q@W)),
S@((W o W) o (Q@W)).
```

At width 256, 31 source layers, a f32 square call costs `33,488,896`:

| worksheet | protected bill | result |
|---|---:|---|
| four-call optimistic f32 lower worksheet | `5.190778880B` | fails 5B |
| same f64 worksheet | `10.381557760B` | fails 5B |
| M130 f32 exact partial implementation (15 calls/layer) | `19.541606400B` | incomplete `aabb` |
| M130 f32 partial plus two unbiased hard probes | `40.304721920B` | full jet stochastic, not M140 contract |

The four-call value excludes the unresolved split pair, all residual samples,
buffers, scalar/copy bill, and runtime reserve.  It is therefore already a
fail-closed lower worksheet, not a debatable full bill.

## 5. Frozen target-free source diagnostic

Predeclared cells were widths 5/6 with seeds `140711/140712`, diagonal-
dominant generated Gaussian states, M131 paired 32/48-node quadrature, and
the fixed M133 three-bank proposal plus 5% uniform rescue.  The diagnostic
standardized the physical M131 coefficient, formed `R=D-J`, and measured
coefficient `L2` and one-draw HH source-influence moments only.

| width | max quadrature disagreement | `||R||²/||D||²` | residual/full HH variance trace |
|---:|---:|---:|---:|
| 5 | `6.61e-8` | `1.2142` | `1.2216` |
| 6 | `6.70e-8` | `1.2690` | `1.2662` |

The quadratic jet is anti-correlated with the exact coefficient in both cells
(`sum J*R < 0`), so blindly subtracting it increases residual norm.  This is
not surprising for a zero-mean local jet applied to a nonzero-mean exact
vertex; it is a falsifier of this unweighted control construction, not a
rejection of exact trivariate source algebra.

## 6. Artifacts and tested scope

* `m140_quadratic_residual_cv/m140_quadratic_residual_cv.py`
* `m140_quadratic_residual_cv/test_m140_quadratic_residual_cv.py`
* `m140_quadratic_residual_cv/run_m140_source_diagnostic.py`
* `m140_quadratic_residual_cv/MANIFEST.json`

Seven generated tests pass: support ownership, exact partition, central
finite-difference jet tangent, physical scale/tangent standardization,
`aaab/aaaa` exactness, nonzero `aabb` remainder, ordered-HH identity,
permutation/gauge covariance, and the static gate.  The separate coefficient
diagnostic is predeclared and does not run a response or outcome screen.

## Salvage map

Preserve the physical-scale standardization, the exact residual/tangent
identity, canonical collision ownership, and the Khatri--Rao obstruction as
constraints.  A child may reopen only with a new exact deterministic
split-pair contraction that passes the protected 5B envelope, or with a
different control whose *complete* M121 transport and residual population are
specified before a screen.  Reusing an artificial unmasked diagonal extension,
dropping `aabb`, or calling a randomized jet remainder a deterministic control
does not repair M140.
