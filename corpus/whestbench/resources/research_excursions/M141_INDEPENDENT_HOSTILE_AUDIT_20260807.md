# M141 independent hostile audit -- 2026-08-07

## Decision

**REPAIR the local mathematical observation; KILL M141 as a deployable
replacement for M131 in its present form.**  The local three-by-three
factorization is exact.  The claimed executable coefficient engine, boundary
tangent, fixed-realization symmetry, and `93.74849288B` target worksheet are
not yet established together.

This audit read only generated-theory/code artifacts M131, M133, M135, and the
local FlopScope starter-kit implementation.  It did not read a contest model,
truth, scorer outcome, submission, or champion.

## Verdict ledger

| Claim | Verdict | Why |
|---|---|---|
| `C = lambda I + U U^T`, `rank(U) <= 2`, for a PSD 3x3 block | **PASS (algebra)** | Spectral decomposition with `lambda=lambda_min(C)` proves it, including eigenvalue ties and semidefinite matrices. |
| Nine-cell random factor rule is unbiased for the raw `[2,1,1]` moment | **PASS (ideal real arithmetic)** | It is ordinary independently jittered stratification of the factor integral. |
| It is an exact, deployed M131 coefficient replacement | **REPAIR** | The lower primitives and degenerate cases invoked by M141 are not implemented by M131; the displayed HH identity also omits the sum over `K` draws. |
| Uniform finite variance at the singular edge, including tangent | **REPAIR** | A primal finite-variance result is plausible on a compact, positive-marginal state set; M141 proves neither the stated uniform bound nor the required degenerate bivariate/delta implementation. |
| Fixed-q Price tangent | **REPAIR** | The Price algebra is right at an SPD base when all boundary primitives exist, but current M131 rejects the claimed boundary and the estimator is not pathwise differentiable through its eigengauge. |
| Deterministic permutation/positive-ReLU-gauge covariance | **KILL** | A finite jittered grid depends on eigenvector signs/rotations and on the isotropic-residual spectral gauge.  Equal covariances can give different realized estimates under the same random stream. |
| `93.74849288B` is a safe complete bill | **REPAIR** | The arithmetic is internally consistent as a reserve worksheet, but it is not a native FlopScope trace and the inherited M133 ledger flags both exact coefficients and residual time as uncharged. |
| No hidden ambient `O(n^3)` eigendecomposition | **PASS (asymptotic only)** | A batched 3x3 factorization per selected triple is `O(KL)`, not a 256x256 eigendecomposition.  Its actual vectorized client implementation is still absent. |

## 1. Exact local factorization: pass, with a representation caveat

For a symmetric PSD `C=V diag(lambda_1,lambda_2,lambda_3)V^T` with ordered
eigenvalues, set `lambda=lambda_1` and retain columns
`sqrt(lambda_s-lambda_1)v_s`, `s=2,3`.  Then exactly

```text
C = lambda I + U U^T.
```

If eigenvalues are tied, a zero column can be removed; if `C=lambda I`, the
factor is empty.  Thus the **law** used by M141 is exact for every PSD 3x3
block.  This is genuinely different from M135's failed global low-rank claim.

However, `U` is not a function of `C` without a gauge choice: every `UO` for
orthogonal `O` represents the same block, and individual eigenvector signs are
already enough to cause a problem for a finite non-rotation-invariant cubature.
This is not a harmless implementation detail when the rule is intended to be
deterministic from `mlp.seed`.

## 2. What is unbiased -- and what is not yet

For a *fixed* `U`, `lambda`, and `mu`, equation (5) is unbiased for

```text
R_ijk = E[(X_i)_+^2 (X_j)_+ (X_k)_+].
```

Consequently `Rhat - lower_terms` is unbiased for `Delta_ijk` only if all
lower terms are supplied as exact mathematical primitives.  The HH estimator
then needs the sum over its fixed number of draws:

```text
DeltaHat_total = sum_{s=1}^K Deltahat_{e_s} F_{e_s}/(2 K q_{e_s}).
E[DeltaHat_total] = sum_{i,j<k} Delta_ijk F_ijk.
```

M141 equation (7) writes the right-hand equality for a single quantity with
`1/(2Kq_e)` and no `sum_s`; literally it is smaller by `K`.  This is repairable
notation, but it must be made exact before an implementation is trusted.

More importantly, the referenced M131 engine is not an exact degenerate
bivariate primitive.  `m131_trivariate_boundary_stream.py`,
`bivariate_relu_raw_dot`, raises if either diagonal variance is at most
`1e-12`, the determinant is at most `1e-14`, or
`abs(rho) >= 1-1e-10`.  Direct check:

```text
rho = 0.975         -> succeeds (raw moment 0.48809387986844055)
rho = 1 - 1e-11     -> ValueError: bivariate correlation is too close to singular
```

Its `[2,1,1]` raw moment is also a paired 32/48-node numerical quadrature,
not an algebraically exact evaluator.  Therefore the current code cannot
support M141's phrases “including its degenerate bivariate limit” or “exact
unbiasedness” as an executable claim.  The random cells are exact only for the
mathematical integral, not for the present finite-precision lower-term path.

## 3. Boundary variance and the tangent

For the primal raw moment, the rational normal map is sensible: normal tails
dominate its polynomial/secant Jacobian, and `M_1`, `M_2` are Lipschitz or
smooth enough in their mean argument.  With bounded means and bounded marginal
scales, an `H^1`-style finite-variance proof can be completed even as the
spectral residual `lambda` goes to zero.

That is not the uniform assertion M141 makes.  Its own proof permits an
unbounded constant as means/scales grow; over all PSD matrices no uniform
variance statement is true.  It also leaves `M_0` unspecified at `v=0,m=0`,
which matters for the derivative.  A ReLU expectation is generally not
Frechet-differentiable at a deterministic zero under arbitrary variance
directions (`E[(sqrt(t)Z)_+]` is proportional to `sqrt(t)`).  So the tangent
cannot be claimed for every semidefinite block.

At an SPD base with positive marginal variances, equation (11) has the correct
Price factors: off-diagonal directions appear once, diagonal directions have
the one-half second-derivative factor, and the ReLU singleton deltas should be
Rao--Blackwellized.  But (12) still requires a robust bivariate `[2,1]`
primitive when its conditional covariance becomes singular.  Current M131
explicitly rejects that case.  The correct scope is therefore:

```text
primal:   candidate finite-variance operator on a predeclared compact SPD gate;
tangent: candidate only after a separately implemented, tested degenerate
         bivariate/delta primitive; never claim pathwise eigenfactor derivative.
```

Freezing `q` correctly removes `qdot`; it does not cure eigengauge discontinuity
or a missing boundary primitive.

## 4. Deterministic gauge/permutation failure: explicit counterexamples

Take

```text
C = diag(1,2,3),  mu = (0.3,-0.4,0.1), lambda=1,
U = [[0,0],[1,0],[0,sqrt(2)]].
```

Using the same fixed 3x3 jitter array in M141 equation (5), changing only the
allowed eigenfactor sign `U[:,1] -> -U[:,1]` leaves `C` unchanged but produces

```text
Rhat(U)       = 0.3722537753741205
Rhat(U sign-flipped) = 0.2734919388196706
difference    = 0.09876183655444992.
```

The expectation is the same; the seeded realized estimator is not.  At a tied
eigenvalue the arbitrary `O(2)` rotation gives a continuum of such outcomes.

Positive ReLU gauge fails as well.  For `D=diag(2,3,4)`, exact covariance and
mean transformation is `C'=D C D`, `mu'=D mu`, and the raw `[2,1,1]` moment
must scale by `2^2*3*4=48`.  M141's new minimum-eigenvalue factorization with
the same grid gives

```text
Rhat(C',mu')           = 17.30915945199722
48 Rhat(C,mu)          = 17.868181217957783
difference             = -0.5590217659605621.
```

The source is structural: `lambda I` is not carried to `D lambda I D` by a
non-scalar positive diagonal gauge.  Sorting/jittering by array labels also
does not supply per-realization permutation covariance.  Distributional
unbiasedness is insufficient for this stricter invariant.

### Repair that actually addresses the invariant

For an SPD block, use the full three-factor Cholesky representation
`C=LL^T`, with residual zero.  It has exact positive-diagonal gauge covariance:
`chol(D C D)=D chol(C)`, and each conditional ReLU factor scales pointwise.
To make it permutation covariant at fixed seed, average the same jittered rule
over all six coordinate orders, carrying the exponent roles with the coordinate
permutation.  Use the same underlying jitter array in all six terms so the
finite set is closed under re-labelling.

That repair has an important cost: `m=3` in three dimensions is 27 cells; six
coordinate orders make **162** cell evaluations/triple, rather than M141's
9.  It only covers SPD blocks unless a separate deterministic semidefinite
Cholesky and derivative convention is designed and tested.

## 5. Cost and runtime audit

The M141 arithmetic itself checks out:

```text
M133 common work excluding its coefficient engine       93.31564744B
M141 nine-cell inherited scalar reserve                    0.18284544B
M141 local-factor/scalar/delta reserve                      0.25000000B
claimed total                                               93.74849288B.
```

It is nevertheless not a verified complete FlopScope accounting.  M133's
`flopscope_batched_hh_ledger(..., K=512)` returns
`sampled_exact_coefficients_charged=False` and
`residual_wall_time_charged=False`; M141 replaces those flags with an untraced
manual reserve.  The 100-ms wall reserve inherited in the common term does not
measure Python loops, batched gathers, jitter generation, `tan`, normal
CDF/PDF, `eigh`, branch/padding, or the extra delta path for this implementation.

Useful non-target instrumentation: local FlopScope accepts batched 3x3
`fnp.linalg.eigh`; 512 SPD blocks cost 124,416 f32 billed FLOPs (243/block).
Thus there is no hidden 256x256 eigendecomposition and no ambient `O(n^3)`
factorization.  But no M141 code batches all selected triples, pins dtype,
pads rank-dependent work to its maximum, or measures residual time on the
grader-compatible client.

For the symmetry repair, merely scaling the inherited 512-per-cell reserve
gives

```text
node reserve = 1.6252928B * 162/80 = 3.29121792B.
```

Holding the unexplained `0.25B` reserve fixed yields an optimistic
`96.85686536B`.  Scaling that reserve with the eighteen-fold cell increase
yields `101.10686536B`.  Since M141 does not split the reserve into fixed and
per-cell components, a safe repaired allocation cannot be certified below the
cliff.  This is before a native residual trace.

The original rank-drop (`r=0,1,2`) also makes actual work data-dependent.
That is not an adaptive proposal or a hidden `O(n^3)` operation, but a
hard-cliff implementation should pad every selected triple to the declared
maximum or account the full branch cost.

## Required gates before any child is permitted

1. Implement a vectorized client-compatible coefficient operator; specify the
   finite-precision lower primitives and the `M_0`/semidefinite behavior.
2. Fix the HH sum in the proof and test raw-moment, defect, and frozen-q
   tangent identities against independent small dense Gaussian references.
3. Add exact generated tests for eigen-sign, tied-eigenspace rotation,
   permutation, and positive diagonal ReLU-gauge covariance using the same
   `mlp.seed` substreams.
4. Either adopt the Cholesky-plus-six-order repair and re-open the complete
   cost gate, or explicitly drop the deterministic symmetry claim.  Do not
   silently call expectation-level invariance the stronger property.
5. Require a FlopScope client trace showing `F`, operation calls/dtypes, peak
   arrays, and residual wall time with the maximum fixed cell count.
6. Only then run M141's predeclared G1/G2 output-MSE screens.  It may not be
   composed with an unvalidated triple-allocation mutation.

## Final disposition

Preserve the local PSD factor identity and ideal randomized raw-moment
estimator.  Do **not** call M141 an exact, gauge-safe, fixed-cost M131
replacement, do not attach its tangent to M133, and do not alter the champion.
The next lawful child must repair one concrete link: executable degenerate
primitive plus deterministic symmetry, followed by a complete recost; otherwise
M141 remains a mathematical component only.
