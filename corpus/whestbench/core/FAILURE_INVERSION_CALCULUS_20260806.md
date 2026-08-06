# Failure-inversion calculus

Date: 2026-08-06

This note converts failed rungs into new calculations without pretending that
negating a number reverses a mechanism. Each inversion must change the failed
causal link and must be tested on fresh cleanroom seeds.

## 1. Sign inversion of a fitted control is exactly redundant

For an exact-zero-mean control matrix `H` and fitted coefficient matrix `B`,

`m_hat = mean(f - H B)`.

Replacing `H` by `-H` replaces the least-squares optimum by `-B`; the product
`H B` and the estimator are unchanged. More generally any nonsingular change
of coordinates `H -> H A` leaves `span(H)` unchanged. Therefore the adverse
JSpace results cannot be inverted by flipping signs, coefficients, or feature
normalizations. A valid inversion must change the subspace.

## 2. JSpace structural inversion

Observed fresh factorial ratios relative to no control:

| control span | raw variance ratio | cost-adjusted ratio | wins | median error correlation |
|---|---:|---:|---:|---:|
| isotropic | 4.28796 | 7.48336 | 0/16 | 0.01949 |
| signed terminal `J` top modes | 9.11840 | 40.4253 | 0/16 | 0.01719 |
| terminal `E[J^T J]` top modes | 4.75763 | 21.0923 | 0/16 | 0.05057 |

The Gram cell is 1.10953 times worse than isotropic raw. Its RMS error is
`sqrt(4.75763)=2.18120` times the no-control RMS. Conditioning is benign
(median 8.25), so the result says that high local-sensitivity directions are
not observable directions for the even spherical degree-`>=6` integration
residual.

The distinct inversion now under test is:

- bottom four eigenvectors of `G_0`;
- four fresh directions in the orthogonal complement of the top-four space;
- the original top-four, isotropic, and no-control cells as frozen controls.

This is a new subspace, not a sign relabeling. If bottom/complement cells also
lose, terminate the JSpace estimator family and retain `G_0` only as an offline
sensitivity diagnostic.

## 3. Randomized-radial residual inversion

The one-shot development result is:

`S_closure / S_champion = 96.1178366555`.

As a same-multiplier severity calculation, an added residual mechanism would
have to leave at most

`1 / 96.1178366555 = 0.01040389625`

of the closure MSE, equivalently contract RMSE to

`1 / sqrt(96.1178366555) = 0.1019994914`.

An ideal linear residual model would need

`R^2 >= 1 - 1/96.1178366555 = 0.9895961038`.

More generally, if `alpha_A` is the analytic multiplier, `alpha_H` the hybrid
multiplier, and `R=(alpha_A V_A)/(alpha_target V_target)` is computed on
matched units, then

`R^2 > 1 - alpha_A/(R alpha_H)`.

The observed `96.1178` compares one development-row analytic score with an
aggregate champion score, so `0.989596` is a conservative severity/falsifier,
not an exact population requirement. A real residual child must be judged by
paired, matched-unit residual variance per total cost on fresh networks.

The strongest prior symmetry-safe residual model reached only `R^2=0.662672`.
Thus a generic learned bias inversion is not remotely on the required route.

For any constant analytic estimate `a(W)` and ordinary samples `f(X_i)`,

`a + mean_i(f(X_i)-a) = mean_i f(X_i)`.

This “sample the analytic residual” inversion collapses exactly to the pure
sampler: it contributes no control-variate variance reduction. Shrinking the
sampled residual merely interpolates between the biased closure and sampler;
the approximate-mean and mediant constraints apply. A real survivor requires
a coupled per-sample surrogate `g(X;W)` with a more accurate exact mean and
high correlation specifically after the 5-design projection. No such function
is supplied by the current q3 component state.

## 4. Consequence for resource allocation

The inversion calculations reinforce the current allocation rule:

- use the random32,256 sampler as the immutable deployment parent;
- do not spend points on terminal sensitivity controls or a constant analytic
  residual correction;
- reuse Haar/chi-radial/q3 machinery only if a new hybrid exposes a coupled
  zero-mean observable rather than replacing the sampler;
- treat `R^2=.9896` as a conservative same-multiplier severity gate and require
  the exact paired residual-variance/total-cost inequality on grouped fresh
  cleanroom networks before any official-row budget.

These thresholds are now part of the recursive ledger and graph falsifiers.
