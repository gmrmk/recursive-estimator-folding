# M220 predeclaration — bivariate positive-part fourth owners

Status: **predeclared formula/TDD candidate; not promoted and not a source
compiler.**  This folder deliberately contains no truth, scorer, weights,
response, leaderboard, target model, or variance-efficacy route.

## One changed mechanism

For a single SPD bivariate Gaussian preactivation
`(X,Y) ~ N((mu_x,mu_y), [[v_x,c],[c,v_y]])`, compute the raw moments
`E[X_+^3 Y_+]` and `E[X_+^2 Y_+^2]` from **one** M178 `Phi2` value/first-jet
call, plus certified univariate/boundary evaluations.  It replaces neither a
Source211 slot nor a collision residual proposal.  It is an on-demand pair
primitive only.

The physical connected owners returned by the primitive are

```
kappa31 = central31 - 3 Var(X_+) Cov(X_+,Y_+)
kappa22 = central22 - Var(X_+) Var(Y_+) - 2 Cov(X_+,Y_+)^2.
```

Thus `kappa31(i,j)` is directed and `kappa22(i,j)` is symmetric.  A downstream
owner still needs an explicitly compatible tree convention before it may call
either value a `K31` or `K22` *defect*.

## Exact recurrence and normalized ABI

Put `sx=sqrt(v_x)`, `sy=sqrt(v_y)`, `a=mu_x/sx`, `b=mu_y/sy`,
`rho=c/(sx sy)`, `s2=(1-rho)(1+rho)`, and
`M_pq=E[X_+^p Y_+^q]`.  M178 supplies `P=M00`, `Da=dP/da`, `Db=dP/db`,
and `Dr=dP/drho`.  The boundary terms needed by density integration by parts
are retained rather than silently discarded:

```
BX0 = Da/sx                         BY0 = Db/sy
BX1 = sy/sx * ((b-rho*a)*Da + s2*Dr)
BX2 = sy^2/sx * (((b-rho*a)^2+s2)*Da + (b-rho*a)*s2*Dr)
BY1 = sx/sy * ((a-rho*b)*Db + s2*Dr)
```

The base row and column remain *joint* orthant moments (they are not unary
marginals):

```
M01 = mu_y*P + c*BX0 + vy*BY0       M10 = mu_x*P + vx*BX0 + c*BY0
M02 = mu_y*M01 + c*BX1 + vy*P       M20 = mu_x*M10 + vx*P + c*BY1.
```

Then

```
M11 = mu_x*M01 + vx*BX1 + c*P
M21 = mu_x*M11 + vx*M01 + c*M10
M31 = mu_x*M21 + 2*vx*M11 + c*M20
M12 = mu_x*M02 + vx*BX2 + 2*c*M01
M22 = mu_x*M12 + vx*M02 + 2*c*M11.
```

This is the corrected boundary-indicator recurrence: the `B` terms are joint
boundary integrals, and the base row/column retain the other orthant
indicator.  Unary moments are used only after this recurrence, in the central
cumulant conversion.  It is algebraically exact on the SPD stratum.  The
cheapest falsifier is a Hermite-series comparison of raw and connected
`(3,1)/(2,2)` values on fixed nonzero-mean SPD cells.

## Domain, symmetry, and fail-closed policy

* SPD: require finite inputs, `v_x,v_y>0`, and `abs(rho)<=1-2^-52`; otherwise
  M178's rank-one/non-SPD chart is refused.
* Exact variance-zero strata are handled separately only when the corresponding
  covariance is exactly zero.  A fourth connected cumulant with a deterministic
  endpoint is exactly zero.  Nonzero covariance with zero variance is refused.
* Swapping endpoints maps `M31(x,y)`/`kappa31(x,y)` to the reverse directed
  `(1,3)` owner and leaves `M22`/`kappa22` unchanged.  Positive diagonal gauge
  scaling has degrees `(3,1)` and `(2,2)` respectively.
* Any nonfinite intermediate, an M178 refusal, or a negative/nonfinite
  numerical enclosure is a typed refusal.  No clipping, retry, or rank-one
  continuation.  Exact deterministic limits have zero enclosure width.

## Numerical and cost gates

M178's certified value/derivative widths and M178's certified unary `Phi/phi`
subroutines are propagated into a deliberately conservative formula-level
radius.  This is **not yet a target-FlopScope certificate**: promotion requires
the frozen high-precision containment suite and the width gate in the tests.

The static inclusive scalar budget is predeclared as **8,192 charged FLOPs per
SPD pair event**, comprising M178's inclusive 4,048 maximum and a 4,144
allowance for both unary charts, normalization, recurrence, cumulant algebra,
and radius bookkeeping.  This bill includes no producer-side `a,C` extraction,
no collision proposal, no tree, no storage, and no M198 work.  It is a ceiling,
not a claim that an all-pairs physical tensor fits a layer budget.  If queried
for all ordered pairs of a 31 x 256 layer, this ceiling alone is
`31*256*255/2*8192 = 8,288,993,280` FLOPs, so such materialization is rejected
as a cost premise.

Promotion gates: one M178 call per SPD event; frozen Hermite reference
containment; raw/connected permutation and gauge checks; no refusal on the
declared SPD reference cells; finite radius with `radius <= 3e-3*(1+|value|)`;
and a target-path inclusive FlopScope receipt no greater than 8,192.

## Non-claims / prior-failure firewall

This does not reopen M151/M206's strict-distinct control, M167/M205's missing
physical-owner producer, M212/M213's collision-provider failure, M214's
budget failure, or M178's rank-one refusal.  In particular, it does not prove
that physical `a,C` arrays live at a target layer, does not subtract a tree,
and does not claim variance reduction.
