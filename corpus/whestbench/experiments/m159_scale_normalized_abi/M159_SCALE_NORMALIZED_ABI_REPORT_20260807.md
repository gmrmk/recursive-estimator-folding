# M159 scale-normalized [2,1,1] endpoint ABI — response-free audit

## Decision

**REPAIR ONLY — retain the generic trivariate endpoint family, but replace the
literal physical-float64 absolute-value ABI.**  M158 is a localized output
representation failure: it does not falsify Plackett/Tallis/Price-style
trivariate reductions, a rank-deficient PSD state, or an exponent-carried
endpoint.  It does permanently kill the statement that *every* admissible PSD
state returns one physical binary64 `Delta_211` with absolute error at most
`2e-8`.

M159 does not claim that a generic noncentral trivariate primitive exists
within the residual operation allowance.  It supplies the scale-aware ABI and
the certificate that such a primitive must satisfy before a compiler audit can
credit it.  No coefficient evaluator, quadrature, retry, ridge, clipping, or
response data is introduced here.

## 1. Homogeneity factorization

For local labels `(i,i,j,k)=(0,0,1,2)`, coordinatewise positive ReLU gauges
give the exact covariance law

\[
 \Delta_{211}(D\mu,D\Sigma D)
   =d_i^2d_jd_k\,\Delta_{211}(\mu,\Sigma),\qquad D=\operatorname{diag}(d)>0.
\]

On the positive-marginal stratum, set

\[
 \sigma_a=\sqrt{\Sigma_{aa}},\quad
 \alpha_a=\mu_a/\sigma_a,\quad
 R=\operatorname{diag}(\sigma)^{-1}\Sigma\operatorname{diag}(\sigma)^{-1},
 \quad S=\sigma_0^2\sigma_1\sigma_2.
\]

Then `Delta_211 = S delta_211(alpha,R)`.  The optional correlation chart is
therefore gauge invariant.  Its directional identities are

\[
 \dot\sigma_a={\dot\Sigma_{aa}\over2\sigma_a},\quad
 \dot\alpha_a={\dot\mu_a\over\sigma_a}
                 -\alpha_a{\dot\sigma_a\over\sigma_a},
\]

\[
 \dot R_{ab}={\dot\Sigma_{ab}\over\sigma_a\sigma_b}
 -R_{ab}\left({\dot\sigma_a\over\sigma_a}+{\dot\sigma_b\over\sigma_b}\right),
 \qquad {\dot S\over S}=2{\dot\sigma_0\over\sigma_0}
 +{\dot\sigma_1\over\sigma_1}+{\dot\sigma_2\over\sigma_2},
\]

\[
 \dot\Delta_{211}=S\dot\delta_{211}+\dot S\delta_{211}.
\]

That chart is useful for a future correlation-based primitive, but it is not
the primary ABI: dividing by `sigma` loses its coordinate chart at a marginal
zero face.

### Primary ABI: exact uniform dyadic carrier

Choose a primal-only integer `e` from finite `mu` and covariance diagonals,
and put `r=2^e`.  The packet uses the largest binary exponent needed by a mean
or a standard deviation.  Call the generic primitive on

\[
 \bar\mu=2^{-e}\mu,\qquad\bar\Sigma=2^{-2e}\Sigma,
 \qquad d=\Delta_{211}(\bar\mu,\bar\Sigma).
\]

It returns the scale-carried endpoint

\[
 \Delta_{211}=2^{4e}d,\qquad
 \dot\Delta_{211}=2^{4e}\dot d.
\]

`4e` is integer metadata, not a float64 multiplication.  The carrier is held
fixed when taking a JVP/VJP at the primal; it is reselected only for a new
primal state.  This is the necessary tangent convention for a discontinuous
power-of-two representation choice.

The uniform map is a nonsingular scalar congruence.  It preserves PSD,
rank, and every zero marginal exactly; no ridge is needed.  If a f64-only
normalization would underflow a nonzero state component, the packet fails
closed and requires exponent-coded state entries rather than silently erasing
it.  This is a representation boundary, not a request to truncate the domain.

## 2. Zero and low-rank semantics

If `Sigma_aa=0` in a PSD matrix, its row and column at that **state** are zero,
and `X_a=mu_a` is deterministic.  The primary dyadic ABI retains that state
unchanged apart from a common power-of-two carrier.  An endpoint can then use
an exact deterministic dimensional reduction where applicable.

The correlation chart must instead return `ZERO_VARIANCE_PSD_FACE`.  It must
not divide, ridge, or define a generic two-sided derivative there.  In
particular, a smooth PSD curve can have an off-diagonal first derivative at
such a face (for example `[[t^2,t],[t,1]]`); `Sigma_aa=0` at the base point
does not make correlation coordinates differentiable.  A future provider must
use an explicit pathwise/one-sided conic tangent rule for that route.

For positive diagonals with rank one or two, `R` remains singular but defined.
The packet retains those strata exactly.  It neither declares them full rank
nor invokes an inverse covariance.

## 3. The tight useful float64 certificate

Let the dimensionless evaluator produce a float `d_hat` with a mixed
certificate

\[
 |\hat d-d|\le a_d+r_d|d|,\qquad 0\le r_d<1.
\]

It can export the computable absolute enclosure

\[
 \epsilon_d={a_d+r_d|\hat d|\over1-r_d}.
\]

The recommended result is therefore the triple

\[
 (\hat d,\;4e,\;\epsilon_d+\tfrac12\operatorname{ulp}(\hat d)),
\]

meaning `2^(4e) * (d_hat +/- radius)`.  The exponent is exact, and the radius
is in dimensionless mantissa units.  This is the tightest useful form for a
float64 primitive: it captures its ordinary absolute-plus-relative numerical
error without demanding a physical absolute error that must shrink as the
state gauge grows.

If a caller insists on materializing a physical binary64 `y`, the mandatory
state-specific bound is

\[
 |y-\Delta_{211}|
 \le 2^{4e}\left(\epsilon_d+\tfrac12\operatorname{ulp}(\hat d)\right)
      +\tfrac12\operatorname{ulp}(y). \tag{1}
\]

The last term is irreducible.  It is not a property of the normal-probability
algorithm.  The optional correlation chart has a mantissa `m` with
`S=2^(4e)m`; if that chart is used, it must additionally certify `m_hat` by
`epsilon_m`, and replace the inner radius in (1) by

\[
 |\hat m|\epsilon_d+|\hat d|\epsilon_m+\epsilon_m\epsilon_d
 +\tfrac12\operatorname{ulp}(\hat m\hat d).
\]

Thus a chart conversion cannot be treated as free numerical algebra.

A coarse universal necessary range check follows from binary64 spacing.  For
values with magnitude below `2^28`, the largest half-ulp is `2^-26`, about
`1.490116119e-8`; that leaves only about `5.09883881e-9` for every other term
in a `2e-8` certificate.  At and above `2^28`, a universal correct-rounding
bound already exceeds `2e-8`.  Consequently the old physical contract can be
used only as a **state-specific materialization check** using (1), never as a
generic all-PSD provider promise.

## 4. M158 survives ideal normalization at the old boundary

The retained rank-one positive-gauge probe is

\[
 \Delta_{211}(g)=g^4\left[{3\pi^2-4\pi-6\over4\pi^2}
 -{12(\pi-1)^3\over\pi^4}\right].
\]

For `g=1024`, the dyadic ABI chooses `e=11`, so its exact output carrier is
`2^44` and the ideal normalized mantissa is approximately
`-0.05814444607922470022165605403`.  Granting an impossible best case—exact
dimensionless arithmetic before the sole final conversion—still produces

| quantity | value |
|---|---:|
| exact physical coefficient | `-1022887912875.235379148458815624...` |
| nearest binary64 | `-1022887912875.2354` |
| exact nearest-float error | `0.00002758595881562476133207633379` |
| binary64 ULP | `0.0001220703125` |

The nearest error is over one thousand times `2e-8`.  Exact exponent scaling
therefore **does not recover the old physical-output contract**.  It preserves
the result as a scale-carried value for an ABI willing to accept that form.

## 5. Replacement gate compatible with the source variance audit

Source normalization is safe only when it is a common nonzero factor `L`
within the same generated source population (and bootstrap replicate).  If
both raw and residual source values are carried as `x/L`, then variance and
the associated RMS numerical envelope scale by `L^-2` and `L^-1`,
respectively; their ratio is unchanged.  Per-event normalization is not safe:
it changes the sampling distribution and thus the residual-variance target.

Let `H_hat,D_hat` be the computed residual and raw source contributions, and
let `b_H,b_D` be certified centered-L2 numerical error envelopes over one
source draw.  A sufficient robust replacement for each bootstrap replicate is

\[
 U_V=\left({\sqrt{V(\hat H)}+b_H\over
                 \sqrt{V(\hat D)}-b_D}\right)^2,
 \qquad \sqrt{V(\hat D)}>b_D. \tag{2}
\]

The 90% bootstrap upper quantile of `U_V` must be strictly below `.25`.
For the p99 guard, with pointwise envelopes `c_H,c_D`, require

\[
 U_{99}={Q_{.99}(|\hat H|)+c_H\over
                 Q_{.99}(|\hat D|)-c_D}\le1.25,
 \qquad Q_{.99}(|\hat D|)>c_D. \tag{3}
\]

The endpoint carrier feeds these envelopes through its coefficient radius
times the corresponding source feature, plus the source reduction's own
certified rounding.  Equations (2) and (3) are scale invariant under a common
power-of-two `L`, and are sufficient to preserve the downstream **numerical
variance gate**, rather than merely reporting an optimistic ratio of rounded
values.  They do not establish response efficacy or exact unbiasedness.

To adopt this path, the source ABI must be explicitly changed to consume
scale-carried coefficients through its accumulation and apply at most one
common source normalization.  That is outside M159.  Materializing each
coefficient first leaves M158 unchanged.

## 6. Falsification packet

`m159_scale_normalized_abi.py` and its five response-free tests establish:

1. diagonal-gauge factorization and retention of a positive-marginal rank-one
   correlation stratum;
2. frozen-carrier tangent reconstruction under uniform homogeneity;
3. explicit zero-variance face dispatch for the optional correlation chart,
   while the primary dyadic ABI preserves the face;
4. failure of `2e-8` after ideal normalization and physical binary64 export;
5. invariance of the robust variance and p99 gates under a common power-of-two
   source scale.

The packet contains no endpoint quadrature and earns no operation or variance
credit.  Its role is to prevent a future generic primitive from being rejected
for M158's localized ABI reason, while also preventing it from silently
claiming the impossible old certificate.

## 7. Literature retained for a future primitive

- R. L. Plackett, “A Reduction Formula for Normal Multivariate Integrals,”
  *Biometrika* 41 (1954), DOI: 10.1093/biomet/41.3-4.351.
- G. R. Price, “A Useful Theorem for Non-Linear Devices Having Gaussian
  Inputs,” *IEEE Transactions on Information Theory* 4 (1958), DOI:
  10.1109/TIT.1958.1057444.
- G. M. Tallis, “The Moment Generating Function of the Truncated
  Multi-normal Distribution,” *JRSS B* 23 (1961), DOI:
  10.1111/j.2517-6161.1961.tb00408.x.
- A. Genz, “Numerical Computation of Multivariate Normal Probabilities,”
  *JCGS* 1 (1992), DOI: 10.2307/1390838.
- S. Wang and W. J. Kennedy, “A Self-Validating Method for the Computation of
  Multivariate Normal Probabilities,” *Computational Statistics & Data
  Analysis* 13 (1992), DOI: 10.1016/0167-9473(92)90007-3.

## Firewall and disposition

- Response cells, model predictions, labels, truth, scorers, leaderboards,
  submissions, and champion selection were not read or changed.
- No M149 outer rule, higher fixed order, ridge, clipping, retry, or
  conditional quadrature was used.
- **Disposition:** `REPAIR_ABI_ONLY; KEEP_GENERIC_ENDPOINT_FAMILY_OPEN;
  KILL_LITERAL_ALL_PSD_PHYSICAL_FLOAT64_2E-8_CONTRACT`.
