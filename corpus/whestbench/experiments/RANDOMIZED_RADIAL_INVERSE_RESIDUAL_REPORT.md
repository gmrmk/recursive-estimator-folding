# Randomized-radial failure inversion: proof-backed no-go

## Outcome

There is no genuinely distinct residual estimator in the proposed constant-anchor inversion. For any vector anchor `a`,

```text
a + mean(f_i - a) = mean(f_i)
```

pathwise and exactly. It is the deployed sample mean with extra arithmetic and, if `a` must be computed, fewer affordable paths. Approximate-mean shrinkage cannot rescue the branch at equal compute without a new nonconstant control whose expectation is known independently. No such control is defined by the current angular/radial closure.

Disposition: **kill the constant-anchor/approximate-mean inversion; preserve the angular, radial, covariance, and compressor operators.** No synthetic estimator test was run because no distinct mechanism survived the algebraic premise gate.

## What the 96.11784x miss does and does not imply

Let `R=96.11784` denote the already-recorded adjusted-score severity ratio. Numerically,

| Quantity | Value |
|---|---:|
| reciprocal `1/R` | `0.0104038958845` |
| RMSE contraction `1/sqrt(R)` | `0.101999489628` |
| same-multiplier explained residual fraction `1-1/R` | `0.989596104116` |
| severity RMSE factor `sqrt(R)` | `9.80397062419` |

These are severity calculations, not population estimates. The numerator is one development-row analytic adjusted result and the denominator is an aggregate champion result. They are not matched raw MSEs.

Let the failed analytic raw loss be `M_A`, a proposed hybrid raw loss be `M_H`, and their compute/score multipliers be `alpha_A` and `alpha_H`. Since the recorded adjusted severity is

```text
R = alpha_A * M_A / champion_adjusted,
```

the exact hybrid requirement to reach that champion reference is

```text
alpha_H * M_H < alpha_A * M_A / R,
M_H / M_A < alpha_A / (R * alpha_H).
```

If an error corrector explains a fraction

```text
R2_residual = 1 - M_H/M_A,
```

then it must satisfy

```text
R2_residual > 1 - alpha_A/(R*alpha_H).
```

Only under the diagnostic assumption `alpha_H=alpha_A` does this reduce to `R2_residual>0.989596104116` and residual RMSE below `10.19995%` of the analytic error. Any added hybrid compute makes `alpha_H>alpha_A` and pushes the required explained fraction closer to one.

The real future gate is therefore a matched-unit comparison of residual variance, bias, and measured multiplier--not the number `0.989596` by itself.

## The constant-anchor collapse theorem

Let `f_1,...,f_N` be vector-valued path outputs and let `a` be any vector. It may be exact, approximate, random, biased, or computed from the same network. If the same `a` appears outside and inside every residual, then

```text
T = a + (1/N) * sum_i (f_i - a)
  = a + (1/N) * sum_i f_i - (1/N) * N*a
  = (1/N) * sum_i f_i.
```

This is a pathwise identity; it needs no independence or expectation. Consequently:

- prediction, bias, variance, MSE, and random seed behavior are exactly those of pure sampling with the same paths;
- the analytic approximation's quality is irrelevant because it cancels;
- computing `a` adds cost but no statistical information;
- under a fixed budget, any paths displaced by computing `a` strictly increase sampling variance unless the sampler itself has zero variance.

The same result holds for coordinatewise/vector anchors and for a shared random anchor. It also holds for varying `a_i` when the external anchor is their sample average:

```text
mean(a_i) + mean(f_i-a_i) = mean(f_i).
```

Therefore "analytic mean plus residuals around that same mean" is not a control variate.

## When a residual becomes a real control variate

A distinct estimator requires a nonconstant random surrogate `g(X)` and an externally known mean `mu_g`:

```text
T_beta = mean(f_i) - beta * (mean(g_i) - mu_g).
```

For a scalar output with exact `mu_g`, the variance-minimizing coefficient is

```text
beta* = Cov(f,g)/Var(g),
Var(T_beta*) = Var(f)/N' * (1-rho^2),
```

where `rho` is the pathwise correlation and `N'` is the number of paths affordable after control costs. The vector result replaces scalar covariance by the corresponding Hilbert-space or multivariate projection.

If the controlled path costs a factor `kappa=N/N'` relative to the deployed sampler's path count, the matched raw-MSE ratio, before control-mean error, is

```text
MSE_control / MSE_sampler = kappa * (1-rho^2).
```

To attain the same-multiplier severity contraction `1/R`, even a zero-cost control requires

```text
rho^2 >= 1 - 1/R = 0.989596104116.
```

With overhead,

```text
rho^2 >= 1 - 1/(kappa*R),
```

which is stricter. To merely beat the deployed sampler on matched units requires `rho^2 > 1-1/kappa`, followed by the actual multiplier comparison.

The randomized-radial closure currently returns one deterministic approximate mean per network. It does not define a per-path `g(X)` with a known exact expectation, so it supplies neither `rho` nor `mu_g` for this theorem.

## Approximate control-mean constraint

Suppose `m_g=mu_g+delta` is only an approximate control mean. Then

```text
T_beta = mean(f_i) - beta*(mean(g_i)-m_g)
```

has bias `beta*delta` and

```text
MSE(T_beta)
 = [Var(f)-2*beta*Cov(f,g)+beta^2*Var(g)]/N'
   + beta^2*delta^2.
```

At the exact-mean optimal coefficient, normalized against the original sampler MSE `B`, the necessary matched-unit gate is

```text
kappa*(1-rho^2) + beta*^2*delta^2/B
  < adjusted_multiplier_allowance.
```

Under the same-multiplier severity diagnostic, the right side is `1/R`. Thus an approximate mean consumes rather than creates the tiny residual allowance. In the impossible best case `rho^2=1` and `kappa=1`, it still requires

```text
abs(beta*delta) < sqrt(B/R) = 0.10199949*sqrt(B).
```

Estimating `mu_g` with additional samples introduces another variance/cost term. Using the failed analytic mean as `m_g` does not remove this requirement; its unknown error becomes bias.

## Shrinkage and mediant constraint

For a matched unit only, let an unbiased sampler have MSE `B`, let a deterministic analytic anchor have squared error `rB`, and blend them:

```text
T_w = (1-w)*sampler + w*anchor.
```

Sampling expectation removes the cross term, giving

```text
MSE(T_w)/B = (1-w)^2 + r*w^2.
```

The oracle choice is

```text
w* = 1/(1+r),
min MSE/B = r/(1+r).
```

If one conditionally substitutes the severity number `r=R`, while acknowledging that it is not a matched estimate, the oracle gives:

- analytic weight: `0.0102967693680`;
- MSE ratio: `0.989703230632`;
- improvement: only `1.02968%` before charging analytic compute.

This is the best possible independent-error shrinkage "mediant." An equal arithmetic blend would be drastically worse. Negative covariance could do better, but a deterministic anchor and unbiased sampling error have zero cross term in sampling expectation; one row cannot establish a transferable anticorrelation.

## Equal-compute comparison

Let the analytic computation consume fraction `eta` of the sampler's fixed budget, leaving `N'=(1-eta)N` paths. Then `kappa=1/(1-eta)` and the oracle shrinkage bound becomes

```text
min MSE/B = kappa*r/(kappa+r).
```

It beats pure sampling only if

```text
kappa < r/(r-1),
eta < 1/r.
```

Under the conditional diagnostic `r=R`, analytic overhead must be less than `1.0403896%` of the entire budget. The frozen closure bills `59.276B` FLOPs before residual-time charging:

| Total comparison budget | Closure fraction | Path variance inflation `kappa` | Conditional oracle blend ratio |
|---:|---:|---:|---:|
| 80B | 74.095% | 3.8603 | 3.7112 |
| 272B | 21.793% | 1.2787 | 1.2619 |

Even granting the conditional matched interpretation and an oracle blend weight, both equal-compute scenarios lose to pure sampling. Using the closure's residual-adjusted cost makes the conclusion stronger.

If `a` were somehow free because another required estimator stage already computed it, the exact recentering identity still yields no variance change. If it is not free, it reduces path count and loses.

## Exact compression break-even law

Let matched raw MSE be `V`, effective compute be `C`, the budget be `B`, and the score multiplier floor be `f`. The adjusted score has the form

```text
S = V * alpha(C),
alpha(C) = max(f, C/B).
```

For a candidate relative to its parent, define

```text
r_V = V_candidate/V_parent,
r_alpha = alpha(C_candidate)/alpha(C_parent).
```

The exact win condition is

```text
S_candidate/S_parent = r_V*r_alpha < 1.
```

When both systems are above the multiplier floor, `r_alpha=C_candidate/C_parent=:r_C`, so the requested break-even law is exactly

```text
r_C*r_V < 1.
```

For an additive mechanism costing `Delta C`, this becomes

```text
r_V < C_parent/(C_parent + Delta C).
```

Crossing or sitting on the floor requires the general `r_alpha` expression; replacing it by `r_C` there would be wrong. Below the floor, reducing FLOPs without changing `alpha` cannot improve adjusted score. Above the floor, a 10% compute reduction can tolerate at most a reciprocal MSE increase, not an arbitrary one.

### Why FP16 or int8 alone do not buy score headroom

FlopScope bills the captured primitive and its tensor geometry. Changing the storage dtype while retaining the same matrix multiplies, eigendecompositions, contractions, sorts, and elementwise calls does not change those operation counts. FP16 or int8 may reduce memory traffic, wall time, package size, or hardware energy, but it does not by itself reduce billed FLOPs. Quantize/dequantize scales, zero-points, saturation guards, and repair casts can add captured work and numerical bias.

Therefore a precision-only port has `r_C` approximately one in billed units and wins only if its numerical perturbation happens to reduce matched MSE--not a credible predeclared mechanism. A score-relevant quantization must change the algorithmic dimension, rank, sparsity, number of paths, or number of captured primitives while preserving enough accuracy.

## The distinct surviving structural compression target

The one causal compression target is not the failed analytic mean and not an unported Jacobian. It is the signed conditional `k3/k4` correction already shown on clean synthetic states to live largely in a covariance-generated algebra of at most 12 matrix directions and rank-4 small cores:

```text
C3 = Q_L^T K3 Q_M,   dim(Q_L) <= 7, dim(Q_M) <= 12,
C4 = Q_M^T K4 Q_M,   dim(Q_M) <= 12,
rank(C3), rank(C4) <= 4 for the frozen representation.
```

This is structural quantization: replace a dense higher-cumulant object by signed low-rank factors generated from the conditional mean, diagonal covariance residual, and four covariance factors. The frozen synthetic representation retained `0.9835` standardized next-row k3 fidelity, `0.9695` k4 fidelity, `0.9882` correction fidelity, and all `97/97` material correction signs. Those figures establish representation headroom only. They do not establish a score gain, an exact coefficient generator, or a legal recurrence.

The current causal opening is narrow but real: derive matrix-free, weights-only coefficient formation for the small `7x12` and `12x12` cores, then a signed ReLU recurrence. The current oracle obtains those cores by projecting exact empirical tensors, so deploying it now would be outcome leakage and unaffordable formation disguised as compression. The branch remains `screened`, not `validated` or `promoted`.

### Conservative added-cost envelope

Known target-shape arithmetic for the 12-direction terminal contraction is `6.444519424B` billed-like operations. Applying a known rank-4 correction and transporting its factors have separate conservative figures of `0.2124B` and `0.3536B`. Charging 25% contingency to the large contraction and then adding both smaller allowances gives

```text
Delta C_known
  = 1.25*6.444519424B + 0.2124B + 0.3536B
  = 8.621649280B.
```

This is a planning envelope, not a cost certificate: coefficient formation and multi-layer recurrence are still missing and must fit inside a separately frozen allowance.

Atop the `59.275963417B` billed FP32 port, the known-envelope total is `67.897612697B`, so the above-floor score gate requires

```text
r_C = 1.145449332,
r_V < 0.873019847,
```

or more than `12.698%` matched raw-MSE reduction. It leaves `12.102B` under an `80B` billed ceiling. Against the port's measured `71.422682171B` residual-adjusted tail, however, the same envelope totals `80.044331451B`, exceeding `80B` by `0.044331451B`; wall/residual or operator savings are required before claiming that envelope.

For a random-32 parent with compute `C_R`, the exact requirements are

```text
C_total = C_R + 8.621649280B,
r_V < C_R/(C_R + 8.621649280B),
C_R <= 263.378350720B   for the 272B hard ceiling,
C_R <= 249.778350720B   for a 258.4B safety ceiling.
```

Using the already-recorded aggregate parent maximum `C_R=250.488783B` solely for compute planning, without reading any row, gives `C_total=259.110432280B`, `r_C=1.034419303`, and the break-even requirement `r_V<0.966725966`: more than `3.327%` matched raw-MSE reduction. It remains `12.890B` below the hard ceiling but misses the `258.4B` safety line by `0.710B`. Thus an honest random-parent rung must either cap added measured cost below `7.911217B`, reduce the parent work, or use a weaker safety policy explicitly approved in advance.

This opens exactly one causal next rung: a frozen synthetic, weights-only small-core formation test with no stored outcome fitting, followed by complete FlopScope integration and the `r_C*r_V<1` gate on untouched matched units. It does not reopen constant-anchor recentering, analytic-mean replacement, or the Jacobian projection.

## Why there is no synthetic test in this rung

A synthetic test would be legitimate for a specified nonconstant `g(X)` with:

1. a proven exact expectation under the path law;
2. explicit coupling to the same sampled paths as `f`;
3. fixed coefficient or cross-fitted coefficient estimation;
4. complete added FLOP/residual accounting;
5. a frozen correlation and equal-compute kill gate.

The current analytic closure provides only a network-level approximate mean. Turning its angular/radial nodes into a pathwise surrogate with known expectation would require a new coupling operator; none exists in the frozen implementation. Testing the constant identity or selecting a coefficient from synthetic noise would create the appearance of a mutation without a distinct mechanism.

Accordingly, no synthetic estimator result was generated.

## Preserved components and next constraint

Preserved:

- Haar angular orientation;
- positive two-node chi-radial moment rule;
- q=3 full-covariance propagation and guarded equal-mass compressor;
- FP32 FlopScope call graph, structural tests, and cost measurements.

Killed implementation class:

- `a + mean(f-a)` for any shared analytic/approximate anchor;
- same-sample varying anchors whose external anchor is their sample mean;
- post-hoc shrinkage fitted from development row 100;
- equal-compute sampler/anchor blending at the conditional severity level.

Unresolved broader family:

- exact zero-mean pathwise controls, Rao-Blackwellizations, or coupled multifidelity residuals with analytically known expectations.

Any next mutation must introduce one such observable explicitly. It may use angular/radial structure to design the control, but it must prove the control expectation before measuring correlation. The real gate is matched residual MSE times measured compute multiplier versus the deployed sampler at equal compute.
