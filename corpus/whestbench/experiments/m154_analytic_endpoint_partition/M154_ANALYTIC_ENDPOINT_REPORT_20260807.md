# M154 analytic moving-kink endpoint partition

Date: 2026-08-07  
Status: **KILL — a correct rank-one stratum kernel was retained, but no generic rank-two/rank-three provider was derived within the one-mechanism constraint.**

## Scope and firewall

This investigation read only the local generated-mathematics components M122,
M131, M147, M149, M151, and M129.  It created a response-free rank-one
`[2,1,1]` component and small-dimensional tests.  It did not read a network
truth, efficacy result, scorer, leaderboard, model response, submission, or
champion artifact.

## The attempted replacement

Write the rank-one local state as `X_l = mu_l + a_l Z`, with `Z ~ N(0,1)`.
For a raw ReLU monomial with powers `p`, its only moving kinks are
`tau_l=-mu_l/a_l`.  M154 sorts the finite `tau_l` and, on each open interval,
integrates the active polynomial exactly:

```text
E product_l (X_l)_+^p_l
  = sum_cells sum_q c_cell,q I_q(left_cell, right_cell),
I_0(u,v)=Phi(v)-Phi(u),
I_1(u,v)=phi(u)-phi(v),
I_q(u,v)=u^(q-1)phi(u)-v^(q-1)phi(v)+(q-1)I_(q-2)(u,v).
```

There is no fixed outer rule, adaptive split, retry, ridge, correlation clip,
or special-function call.  The raw moments are expanded exactly into the
centered `E[(Y_0-m_0)^2(Y_1-m_1)(Y_2-m_2)]`; pair covariances and the M129
tree continuation are formed from the same raw cache.

For a covariance direction `D` and mean direction `m_dot`, the tangent uses
the Price identity in its symmetric-covariance convention:

```text
dM = sum_r m_dot_r E[d_r f]
   + 1/2 sum_r D_rr E[d_rr f]
   +     sum_r<s D_rs E[d_rs f].
```

Here `d(x_+)/dx = 1[x>0]` and `d^2(x_+)/dx^2 = delta(x)` supply exactly the
moving-boundary term.  On a rank-one line, a delta term is an endpoint density
`phi(tau_r)/abs(a_r)` times the remaining active factors.  This supplies an
ordinary tangent in the rank-one stratum and a one-sided PSD-feasible tangent
when null directions open.  It is deliberately not called an ambient Frechet
derivative at the PSD boundary.

The use of Price differentiation follows [Price (1958)](https://doi.org/10.1109/TIT.1958.1057444).  The bivariate truncated-moment part is consistent with [Rosenbaum (1961)](https://doi.org/10.1111/j.2517-6161.1961.tb00422.x).  The broader truncated-multinormal generating-function reduction is due to [Tallis (1961)](https://doi.org/10.1111/j.2517-6161.1961.tb00408.x), and the permitted bivariate normal primitive context is [Owen (1956)](https://doi.org/10.1214/aoms/1177728074).

## Strata and continuity contract

| Local covariance stratum | M154 action | Tangent/continuity statement |
|---|---|---|
| Rank one, all marginal variances positive | Supported exactly by the moving-kink interval partition | Continuous across kink crossings; moving-boundary terms vanish in value and are represented by Price delta terms in the tangent. |
| Rank one, PSD-feasible opening direction | Supported | One-sided tangent only; outward null-space direction fails closed. |
| Rank two, all marginal variances positive | Refused | Three ReLU half-planes form a generic Gaussian triangle/wedge in the factor plane.  No finite Owen-T/Rosenbaum reduction and certified tangent were derived here. |
| Rank three SPD | Refused | Tallis tilting leaves a noncentral trivariate orthant probability.  Its derivatives give the desired moments, but the base trivariate probability remains an unpriced numerical primitive under the no-grid/no-retry rule. |
| Non-PSD, nonfinite, zero marginal variance, or uncertified rank-one factor | Refused | No projection, ridge, clipping, or substitution. |

The rank-one value is the exact lower-rank limit of the Gaussian moment, but
M154 intentionally exposes no rank-two/rank-three continuation API.  Thus it
does **not** establish a continuous generic provider across strata; claiming
otherwise would hide the remaining primitive.

The blocking identity can be seen directly from the exponential tilt:

```text
E[exp(t^T X) 1{X>0}]
 = exp(t^T mu + t^T Sigma t / 2)
   P[N(mu + Sigma t, Sigma) > 0].
```

Differentiating four times produces the `[2,1,1]` raw moment.  Tallis and
Rosenbaum reduce derivatives to lower-dimensional boundary terms, but the
generic base probability is still a noncentral 3D orthant probability.  Owen
T handles bivariate normal integrals, not that remaining generic primitive.
Replacing it by a numerical one-dimensional rule would recreate the M149
outer-integral family, contrary to this mutation's constraint.

## Response-free verification

`test_m154_analytic_endpoint_partition.py` contains seven Philox-free,
small-dimensional generated-state checks:

1. Exact common-factor zero-mean fourth central moment and cumulant.
2. Rank-preserving centered finite-difference tangent parity.
3. One-sided null-space-opening tangent parity against M147 only as a
   response-free high-accuracy oracle; M154 invokes no such rule.
4. Singleton permutation and positive-ReLU-gauge covariance.
5. Rank-two and rank-three adversarial refusals.
6. Outward PSD tangent and nonfinite input refusals.
7. Structural cost bound.

The test command passed all seven tests with the declared bundled interpreter.

## Cost result

For the only supported rank-one stratum, the structural cap is 480 normal
interval cells and 36 delta-boundary evaluations per coefficient, with no
quadrature or special-function call.  A deliberately conservative
250,000-operation cap per coefficient gives:

```text
3,968 calls * 250,000 = 992,000,000 ops = 0.992 B ops
M151 inclusive untraced allowance = 10,291,363,760 ops = 10.291363760 B
```

So the rank-one kernel alone fits the arithmetic allowance.  This is **not a
credit** against M151: M151 needs a provider over ordinary full-rank local
states, and M154 refuses those states before any coefficient is emitted.

## Disposition

**KILL M154 as an M149 replacement / M151 provider.**  The required generic
endpoint-safe nonzero-mean `[2,1,1]` coefficient and tangent cannot be
honestly claimed without adding a certified noncentral trivariate/triangle
Gaussian primitive.  That would be a new mechanism and must carry a separate
accuracy, endpoint, derivative, native-call, allocation, and inclusive-cost
proof.

Preserved identities:

- exact rank-one moving-kink partition and Price/delta tangent;
- rank-one tree continuation from exact raw moments, avoiding artificial
  correlation clipping after positive gauge;
- explicit rank-two and rank-three obstruction classification;
- a hard rank-one cost envelope that is below M151's 3,968-call allowance.
