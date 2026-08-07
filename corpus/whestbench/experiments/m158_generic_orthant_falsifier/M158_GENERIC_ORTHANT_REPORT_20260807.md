# M158 generic noncentral trivariate-normal endpoint primitive

Date: 2026-08-07  
Status: **KILL — the literal universal float64 absolute-value contract is inconsistent before choosing an orthant algorithm.**

## Scope

This was a source-only mathematical review and generated-state test.  It read
local M122/M129/M131/M147/M149/M151/M154 mathematics and primary literature
metadata only.  No response, network truth, efficacy/oracle result,
leaderboard, scorer, submission, or champion state was read or changed.

## Required contract

M158 asked for one generic noncentral trivariate-normal/triangle primitive
with a hard `2e-8` absolute value certificate, `2e-7` tangent certificate,
all PSD strata, and an inclusive residual allowance of
`2,407,464,960 / 3,968 = 606,720` operations per coefficient.

The existing M147/M149 local-provider ABI accepts and emits binary64 arrays
and scalar floats.  Thus a universal `2e-8` absolute certificate requires at
least one binary64 value to lie within `2e-8` of every admissible exact
coefficient.

## Decisive counterexample

Take the perfectly admissible positive-gauge rank-one state

```text
X = (g Z, g Z, g Z),   Z ~ N(0,1),   mean = 0,
Sigma = g^2 * 11^T,   g = 1024.
```

Every marginal variance is `g^2 > 0`; `Sigma` is exactly PSD with rank one.
This is not a zero-variance, non-PSD, clipping, or ridge corner case.

For the owned `[2,1,1]` coefficient `Delta = cumulant - tree`, direct
univariate truncated-normal algebra gives

```text
kappa_211/g^4 = (3*pi^2 - 4*pi - 6)/(4*pi^2),
tree_211/g^4  = 12*(pi - 1)^3/pi^4,
Delta/g^4     = kappa_211/g^4 - tree_211/g^4.
```

The exact 100-decimal calculation and its nearest binary64 neighbor are:

```text
Delta = -1022887912875.235379148458815624761332076333789665740070687...
nearest float64 = -1022887912875.2354
nearest error   = 0.00002758595881562476133207633379
float64 ULP     = 0.0001220703125
requested value tolerance = 0.00000002
```

No binary64 number lies inside the requested tolerance interval.  This is a
representation lower bound: further Plackett integration, a Genz transform,
Owen-T/S evaluation, rational approximation, interval arithmetic, or more
wall time cannot emit a compliant float64 value for this valid state.  Since
the value conjunct is false, the combined value-plus-tangent provider cannot
pass; a separate tangent impossibility is unnecessary for this disposition.

The M158 test derives the formula independently and checks it against the
retained M154 exact rank-one implementation at `g=1`.

## Literature/reduction audit

The considered identities are real and useful, but none cures the literal
binary64 absolute-error contradiction:

| Route | What it provides | Why it cannot pass the stated M158 contract |
|---|---|---|
| Plackett reduction | Correlation derivatives reduce an MVN probability to lower-dimensional normal boundary terms. [Plackett (1954)](https://doi.org/10.1093/biomet/41.3-4.351) | Recovering a generic noncentral trivariate probability still requires a path integral or a new special primitive; even an exact result is unrepresentable in the counterexample. |
| Tallis tilt/moments | The truncated multinormal MGF supplies the moment derivatives. [Tallis (1961)](https://doi.org/10.1111/j.2517-6161.1961.tb00408.x) | It preserves the base noncentral trivariate truncation probability and does not define a scale-normalized output ABI. |
| Price differentiation | Converts covariance tangent terms to Gaussian expectations of derivatives/distributional boundary terms. [Price (1958)](https://doi.org/10.1109/TIT.1958.1057444) | It is an identity for the tangent, not a finite-precision output enclosure. |
| Owen normal-integral functions | Gives bivariate, trivariate, and multivariate normal integral identities/tables. [Owen (1980)](https://doi.org/10.1080/03610918008812164) | A named integral is not a certified, bounded-cost float64 evaluator, and cannot overcome output spacing. |
| Genz numerical evaluation / interval and rational constructions | Numerical approaches worth considering on a bounded normalized domain. [Genz (1992)](https://doi.org/10.2307/1390838); [Wang &amp; Kennedy (1992)](https://doi.org/10.1016/0167-9473(92)90007-3) | They could only become a new candidate after the contract is narrowed; they cannot satisfy the current universal absolute-float64 requirement. |

This conclusion does **not** assert that generic trivariate probabilities are
mathematically unavailable.  It says the requested combination of unbounded
positive gauge, all PSD strata, a fixed absolute tolerance, and a float64
provider ABI is false.  Treating a successful normalized numerical experiment
as proof of the literal claim would be a scope/generalization error.

## Cost result

The residual budget divides exactly to `606,720` operations per coefficient.
The counterexample is independent of operations and calls, so no call/wall
allocation below that cap can repair it.  M158 receives no cost credit and
does not invoke M149's fixed `43/87`, a higher quadrature order, retry,
correlation clipping, or covariance ridge.

## Tests and frozen result

`test_m158_generic_orthant_falsifier.py` passed four response-free checks:

1. Closed-form common-factor defect agrees with M154 at unit gauge.
2. The nearest binary64 at `g=1024` is outside `2e-8`.
3. The state has positive marginal variances and rank-one PSD covariance.
4. The `2.407464960 B / 3,968 = 606,720` accounting is exact.

## Disposition and preserved result

**KILL M158 under the literal requested ABI/domain.**

Preserve:

- the exact scale/gauge counterexample;
- the distinction between a special-function identity and a hard numerical
  certificate;
- M154's exact rank-one partition as a normalized-stratum identity;
- the exact residual allowance arithmetic.

A future, distinct proposal would first need written authority to narrow the
input/output contract — e.g. a bounded standardized domain plus a
scale-normalized or interval/mantissa-exponent result — and then independently
prove a generic value/tangent enclosure, PSD endpoint behavior, native call
count, allocations, and the full inclusive cost.  It may not inherit a pass
from this literal-domain falsifier.
