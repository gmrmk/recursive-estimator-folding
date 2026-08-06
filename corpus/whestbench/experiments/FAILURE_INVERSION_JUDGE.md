# Independent judge: failure inversion

Date: 2026-08-06

## Bottom line

“Invert the failure” is mathematically meaningful only when the inversion
changes the estimator's information, function span, coupling, bias class, or
error covariance. Negating a representation that is refit, or subtracting and
adding the same constant, is an exact relabeling.

The two builder reports support the following dispositions:

| Proposed inversion | Mathematical class | Judge disposition |
|---|---|---|
| `v -> -v` for degree 6/8 zonal controls | Identical feature | Exact relabeling |
| `H -> -H` followed by refitting the control | Identical fitted prediction | Exact relabeling |
| Negate a fitted coefficient without refitting | Anti-control in the same span | Different formula, no new information; unjustified here |
| Bottom-four `G0` eigenvectors | New input subspace | Real mechanism; killed implementation |
| Seeded four-space in the top-four orthogonal complement | New conditional-random subspace | Real mechanism; killed implementation |
| `a + mean(f-a)` | Identical sample mean | Exact algebraic collapse |
| `mean(a_i)+mean(f_i-a_i)` | Identical sample mean | Exact algebraic collapse |
| Analytic-anchor/sampler shrinkage | Biased combination in an old information span | Real but cost-dilutive here |
| Mix two ordinary unbiased sampling families | Allocation among existing families | Cannot beat the best cost-variance product by mediant algebra |
| Nonconstant coupled `g(X)` with independently known `E[g]` | New control variate | Genuinely new, unresolved family |
| Cross-fitted predictor of the analytic error from new weight features | New supervised correction | Genuinely new, but faces the 96.11784x residual gate |

Thus the honest result is not “all inversions fail.” Two structural inversions
were real and failed their frozen implementation gate; two broader mechanisms
remain unresolved because they have not yet been specified.

No official row, scorer, private instance, or API was accessed. Builder
artifacts were read but not modified.

## 1. Exact sign-equivalence results

### Even direction sign

The tested homogeneous controls are

```text
h_(v,l)(x) = ||x|| P_l(v.x/||x||),       l in {6,8}.
```

Since normalized Gegenbauer polynomials have parity
`P_l(-t)=(-1)^l P_l(t)`, both tested degrees give

```text
h_(-v,l)(x) = h_(v,l)(x)
```

pointwise. Direction negation does not merely preserve a span; it produces the
same feature array. The builder's maximum measured difference `0.0` is exactly
what the identity predicts.

### Fitted feature sign

The same conclusion holds more generally for a signed change of basis. Let a
centered feature matrix be `H`, a target matrix be `Y`, and use isotropic ridge:

```text
C = (H^T H + lambda I)^(-1) H^T Y.
```

For any diagonal sign matrix `S`, set `H'=H S`. Then

```text
C' = S C,
H' C' = H S S C = H C.
```

Feature means transform by the same `S`, so the final exact-mean control
correction is unchanged. In the scalar all-negative case, `H'=-H`, `C'=-C`.
This proof applies to the builder's centering, RMS scaling, and isotropic ridge.

Negating `C` *after* fitting while leaving `H` fixed is a different anti-control,
but it is not a new observable. If `e` is the baseline design error and `c` the
fitted control error,

```text
Var(e-c) = V_e + V_c - 2 Cov(e,c),
Var(e+c) = V_e + V_c + 2 Cov(e,c).
```

The measured correlations are approximately zero, so either sign retains the
positive `V_c` penalty. Choosing the sign from held-out outcomes would be
post-hoc selection, not inversion.

## 2. Bottom and complement `G0` directions are real mechanisms

Let `G0=V diag(lambda) V^T`, with eigenvalues sorted descending. The tested
projectors were

```text
P_top    = V[:,1:4] V[:,1:4]^T,
P_bottom = V[:,13:16] V[:,13:16]^T,
P_comp   = Q Q^T,  Q = qr((I-P_top)R)[:,1:4].
```

`P_bottom` and `P_comp` are not obtained by changing eigenvector signs.
`P_bottom P_top=0`, and the measured top/complement defect was
`2.87e-15`. For the realized frozen Grams, the relative eigengap at the
bottom-four boundary ranged from about `0.0748` to `0.567`, so this was not
merely a numerically arbitrary rotation of an exactly degenerate boundary.

Input-space orthogonality does not imply that even zonal harmonic features are
orthogonal: their spherical inner product is proportional to
`P_l(v.w)`, which need not vanish at `v.w=0` for even `l`. Nevertheless,
distinct unoriented lines generate distinct zonal functions, so the bottom and
complement cells genuinely changed the control span.

The fresh factorial then killed these implementations decisively:

| Cell | Raw ratio | Cost-adjusted ratio | Wins | Error correlation |
|---|---:|---:|---:|---:|
| Top four `G0` | 6.0549 | 26.8436 | 0/16 | -0.0131 |
| Bottom four `G0` | 4.2461 | 18.8247 | 0/16 | -0.0058 |
| Top-complement four | 4.5629 | 20.2474 | 0/16 | 0.0229 |

Bottom and complement improve on top by 29.87% and 24.64%, respectively. That
is a real relative structural signal, but both remain more than four times
worse than no control before paying the pilot. With correlation near zero, the
control contributes variance without tracking the randomized-design error.
This kills “use the other end/complement of terminal `G0` with the same
degree-6/8 fit,” not every possible complement-conditioned observable.

One audit caveat does not change the negative result: the predeclared gate also
listed hidden/output permutation checks, but `test_inverse_control.py` contains
input-rotation covariance, sign, orthogonality, PSD, determinism, cost, and
freeze checks only. The performance gates fail so strongly that missing those
structural tests cannot rescue either cell. A future, genuinely different
descendant would need to restore them and test subspace stability across
independent K=4 pilots.

## 3. The exact 96.11784x requirement

Let

```text
R = 96.11784
  = (alpha_A M_A) / S_champion,
```

where `M_A` is the failed analytic raw MSE and `alpha_A` its score multiplier.
For a hybrid with raw MSE `M_H` and multiplier `alpha_H`, reaching the champion
reference requires exactly

```text
alpha_H M_H <= alpha_A M_A / R,
M_H/M_A <= alpha_A/(R alpha_H).
```

Define the residual explained fraction relative to the analytic error by

```text
R2_residual = 1 - M_H/M_A.
```

Then the exact gate is

```text
R2_residual >= 1 - alpha_A/(R alpha_H).
```

At equal multipliers this becomes:

```text
1/R                    = 0.0104038958844685
required R2            = 0.989596104115532
remaining RMSE factor  = 1/sqrt(R) = 0.101999489628471
required RMSE reduction= 0.898000510371529.
```

In words: a same-cost residual predictor must explain at least 98.9596% of the
analytic MSE and leave no more than 10.19995% of its RMSE. Added compute makes
`alpha_H>alpha_A` and raises the required explained fraction.

This is exact score algebra, not an exact population claim. The 96.11784 ratio
compares one analytic development-row adjusted result with an aggregate
champion result; the units and raw multipliers are unmatched. It may set a
severity requirement, but it cannot estimate population `R2` or a transferable
blend coefficient.

Also, this 96x requirement applies to correcting the **analytic estimator's
error**. It is not the requirement for a new control variate added to the
already competitive sampler. Such a control only has to beat the sampler after
its own cost multiplier is charged.

## 4. Constant-anchor inversion collapses exactly

For any vector anchor `a`, deterministic or random,

```text
a + (1/N) sum_i (f_i-a) = (1/N) sum_i f_i
```

pathwise. No independence assumption is needed. The same holds for varying
anchors when their external term is their own sample average:

```text
mean(a_i) + mean(f_i-a_i) = mean(f_i).
```

Therefore the frozen randomized-radial network-level mean supplies no residual
variance reduction by itself. Computing it only displaces affordable network
paths or adds billed work. The second builder correctly declined to generate a
synthetic “win” for this identity.

A real residual control instead needs a nonconstant, path-coupled surrogate
`g(X)` and an independently known mean `mu_g`:

```text
T_beta = mean(f) - beta (mean(g)-mu_g).
```

With exact `mu_g`, optimal scalar variance is

```text
Var(T)/Var(mean(f)) = kappa (1-rho^2),
```

where `kappa=N/N'` is path-count inflation from control cost. To beat the
sampler at the raw-variance level requires `kappa(1-rho^2)<1`; adjusted-score
comparison replaces the right-hand side with the appropriate multiplier
allowance. Requiring `rho^2>=1-1/R` is only the stronger hypothetical demand of
a further 96x contraction, not the ordinary deployment gate for this control.

If `mu_g` is approximate by error `delta`, the MSE gains the unavoidable term
`beta^2 delta^2`. The failed approximate network mean cannot be inserted as if
it were exact; its error becomes control bias.

The randomized-radial closure currently returns a deterministic approximate
network mean. It does not expose a coupled `g(X)` with a proven expectation.
Constructing one would be a new mechanism and must begin at a new premise gate.

## 5. Shrinkage and mediant dilution

Shrinkage is not an algebraic identity, but it adds no new information. For an
unbiased sampler error `epsilon` with MSE `B` and deterministic anchor error
`b(W)` with `E[b^2]=rB`, conditional unbiasedness gives

```text
E[b epsilon] = E[b E(epsilon|W)] = 0.
```

For `T_w=(1-w) sampler + w anchor`, therefore

```text
MSE(T_w)/B = (1-w)^2 + r w^2,
w* = 1/(1+r),
minimum ratio = r/(1+r).
```

Conditionally pretending the unmatched severity `R` were `r` gives only a
1.02968% oracle raw-MSE improvement even if the analytic anchor were free. If
the anchor consumes a budget fraction `eta`, sampling variance inflates by
`kappa=1/(1-eta)` and the oracle ratio becomes

```text
kappa r/(kappa+r).
```

It beats pure sampling only if `eta<1/r`. Under `r=R`, the analytic branch may
consume less than 1.04039% of the budget. Its frozen 59.276B billed cost is
21.793% of 272B (and residual-adjusted cost is larger), so the conditional
oracle already loses before estimation error in `w`.

More generally, allocation between ordinary unbiased families cannot beat the
best pure cost-variance efficiency. If family `i` has per-replicate cost `c_i`,
variance `v_i`, and receives `N_i` independent replicates, the optimally
precision-weighted combination satisfies

```text
C_total Var(combination)
 = [sum_i N_i c_i] / [sum_i N_i/v_i]
 = sum_i [(N_i/v_i)/(sum_j N_j/v_j)] (c_i v_i).
```

This is a weighted mediant of the pure efficiencies `c_i v_i`, hence lies
between their minimum and maximum. A mixture beats the best family only if a
new coupling creates covariance cancellation or a residual family has a
strictly better `c*v`. That is exactly why a proven, nonconstant coupled
control is a real mutation while an anchor blend is not.

## 6. Audit of the two builder reports

### `jspace_inverse_complement_control`

- The sign identity and top-complement orthogonality are correct.
- Bottom/complement directions are genuine new subspaces.
- The performance conclusion is robust: 0/16 wins, raw ratios above 4.2, and
  correlations near zero.
- Missing hidden/output permutation checks should be recorded as an incomplete
  structural gate, but cannot change the kill decision.
- Preserve the measured fact that avoiding top sensitivity reduces damage;
  reuse it only if a new observable changes the error-link mechanism.

### `randomized_radial_inverse_residual`

- The constant-anchor and sample-mean-anchor collapse theorems are exact.
- The general multiplier-aware residual requirement and shrinkage algebra are
  correct.
- Its `rho^2>=1-1/R` threshold is correctly labeled as a hypothetical 96x
  contraction. It must not be quoted as the threshold merely to beat the
  deployed sampler.
- No synthetic run was the right decision because no distinct estimator was
  specified.
- Its local `fold_ledger.json` is empty. This does not weaken the proof, but it
  is not a complete recursive-estimator-folding release record; the killed
  forms, preserved operators, and unresolved exact-control family should be
  entered in the campaign ledger by the owning agent.

## 7. Recursive salvage constraint

Do not reopen either failed leaf by changing signs, ranks, degrees, ridge, or
seeds. Reopen only through one of these mechanism changes:

1. Define a nonconstant angular/radial surrogate `g(X)` coupled to the same
   path as `f(X)` and prove `E[g]` exactly before measuring correlation.
2. Define a new cross-fitted weight-analytic predictor of `m-A`; predeclare the
   multiplier-aware `R2` gate above and validate on whole untouched networks.
3. Replace the full-function `G0` link with an observable constructed directly
   from the degree-6+ design residual, then test against isotropic/no-control at
   matched cost.

These are unresolved families. Everything else evaluated here is either a
killed implementation or a relabeling of an existing estimator.
