# M128: second-order cumulant response theory

Date: 2026-08-07  
Status: generated-only theory audit; no contest/public/private outcomes  
Verdict: **REPAIR**

## 1. Executive result

There is a real nonincremental mechanism here, but it is not yet a complete
candidate.

1. The complete Edgeworth-order-two response is closed by the existing
   repeated-output `k3/k4` tables.  It needs linear `k4` and the disconnected
   `k3^2` diagram; it does **not** need an ambient `k6` tensor.
2. The exact `k3^2` coefficient is `1/[2 (3!)^2] = 1/72`.  For a bivariate
   response, its seven derivative channels are an explicit binomial
   convolution of `jjj, ijj, iij, iii`.
3. A second inhomogeneous tangent can coalesce all downstream source--source
   meetings in `O(L n^3)`, rather than explicitly propagating `O(L^2)` source
   pairs.  The extra unavoidable float64 affine cost is about `4.019B` for 30
   stages (`4.153B` for 31).
4. M126-style direct/Hutchinson contractions already contain the minimal
   cumulant tables.  The `k3^2` response itself adds only `O(L n^2)` scalar
   work.  However, a *complete* second-order recurrence also needs the
   directional derivative of the first-order source, including the derivative
   of M126's state-dependent cumulant construction.  That differentiated call
   graph is not yet derived or priced.
5. Plain second-order Edgeworth is a signed, oscillatory expansion and need not
   preserve covariance positivity.  Deterministic positivity-preserving
   reorganizations exist, but none is free and none is authorized by the
   literature as an accuracy theorem for this fixed-weight problem.

Accordingly, implement the exact response kernels and Hessian-vector carrier as
a generated small-width component, but do not freeze an efficacy grid until the
`D source` call graph, probe-product unbiasedness, and a complete `<100B` ledger
exist.

## 2. What the primary literature does and does not prove

Celli's 2026 paper defines an order-`4m-1` multivariate Edgeworth signed measure
for **centered conditionally Gaussian** neural-network outputs.  Its expansion
has `k` covariance-fluctuation insertions with coefficient `1/(k! 2^k)` and
Hermite degree `2k`; it proves `O(n^-m)` total-variation upper and matching lower
rates under an invertible Gaussian limit and moment assumptions.  This is a
clean diagram-ownership precedent: identical insertions receive the factorial
automorphism divisor.  The paper also explicitly reports that higher Hermite
orders oscillate badly at small width, and leaves simultaneous depth/width
growth open.  See [Celli, arXiv:2605.24072](https://arxiv.org/abs/2605.24072),
especially definition (2.7), Remark 8, and Remark 9.

That theorem is **not** an accuracy certificate here.  Celli averages over a
randomly initialized ensemble evaluated at finitely many inputs and exploits a
conditional Gaussian covariance mixture.  WhestBench fixes every weight and
integrates over a Gaussian input through a deep deterministic ReLU map.  The
fixed-instance activation law has nonzero skewness, depth is 32 at `L/n=1/8`,
and the relevant conditioning is different.  We may reuse the exact formal
Edgeworth combinatorics and the oscillation warning, but not the paper's TV
rate.

Voigtlaender proves that Gaussian expectations of tempered distributions are
smooth in covariance and gives exact derivatives in terms of distributional
derivatives, with a `1/2` for each diagonal-variance derivative and no such
factor for an off-diagonal covariance coordinate.  ReLU, gates, deltas, and
their derivatives fit this framework.  This legitimizes the nonsmooth local
Jacobian/Hessian kernels used below; it does not validate a non-Gaussian
truncation.  See [Voigtlaender, arXiv:1710.03576](https://arxiv.org/abs/1710.03576),
Theorem 1.

## 3. Formal cumulant operator and the two meanings of “second order”

Let `G ~ N(mu,C)` match the first two cumulants of `X`, and let

```text
F_f(mu,C) = E[f(G)]
D3 = (1/3!) kappa3_abc d_a d_b d_c
D4 = (1/4!) kappa4_abcd d_a d_b d_c d_d,
```

with repeated indices summed and `d_a = partial/partial mu_a`.  Formally,

```text
E[f(X)] = exp(D3 + D4 + D5 + ...) F_f(mu,C).
```

The sign is positive in the expectation operator.  For example,
`d_mu^3 E[G_+] = -mu phi(mu/sigma)/sigma^3`, reproducing the signed first-Born
skew correction.

There are two distinct truncations which must never be conflated:

### 3.1 Classical Edgeworth power counting

Introduce `epsilon` with `kappa3=O(epsilon)` and
`kappa4=O(epsilon^2)`.  Through `epsilon^2`,

```text
F + epsilon D3 F
  + epsilon^2 (D4 F + (1/2) D3^2 F).
```

This is the recommended M128 child.  It adds `k3^2` to linear `k3/k4` and does
not assert that `k3*k4` or `k4^2` is of the same asymptotic order.

### 3.2 Quadratic Gram--Charlier truncation in retained `(k3,k4)`

If both retained tensors are declared `O(eta)`, then through `eta^2`,

```text
F + (D3+D4)F
  + (1/2)D3^2 F + D3 D4 F + (1/2)D4^2 F.
```

The scalar coefficients are

```text
k3^2 : 1/[2(3!)^2] = 1/72
k3k4 : 1/[3!4!]    = 1/144
k4^2 : 1/[2(4!)^2] = 1/1152.
```

This is algebraically complete for a model retaining only `k3,k4`, but it is
not a complete asymptotic description of an arbitrary fixed law unless the
sizes of `k5,k6,...` are also controlled.  It is retained below as a formula
and falsifier, not the preferred deployment.

## 4. Exact univariate final-mean and variance response

Let `sigma^2=v`, `alpha=mu/sigma`, `phi=standard-normal pdf`, and `He_r` be the
probabilists' Hermite polynomial.  Define

```text
m(mu,v) = E[G_+].
```

For every `r>=2`,

```text
m_r := d_mu^r m
     = (-1)^(r-2) He_(r-2)(alpha) phi(alpha) / sigma^(r-1).
```

Therefore the full retained quadratic response of the final mean is

```text
delta1 m = k3 m_3/6 + k4 m_4/24
delta2 m = k3^2 m_6/72 + k3 k4 m_7/144 + k4^2 m_8/1152.
```

Under classical Edgeworth grading, instead use

```text
m^[1] = k3 m_3/6
m^[2] = k4 m_4/24 + k3^2 m_6/72.
```

In particular,

```text
m_6 = (alpha^4 - 6 alpha^2 + 3) phi(alpha) / sigma^5.
```

Only `kappa3_iii` and `kappa4_iiii` are required for neuron `i`.

For the raw second moment `q(mu,v)=E[G_+^2]`, translation gives the exact
identity

```text
q_r := d_mu^r q = 2 m_(r-1), r>=1.
```

Apply the same coefficients to `q_r`.  If `m=m0+epsilon m1+epsilon^2 m2`
and `q=q0+epsilon q1+epsilon^2 q2`, central variance ownership is

```text
V1 = q1 - 2 m0 m1
V2 = q2 - 2 m0 m2 - m1^2.
```

The `-m1^2` term is mandatory.  Omitting it counts the disconnected mean
diagram in the raw moment but fails to remove it from the central covariance.

## 5. Exact bivariate response and the complete `k3^2` coefficients

For distinct outputs `i,j`, define the Gaussian raw ReLU pair moment

```text
R_ij = E[G_i+ G_j+]
R_pq = d_mu_i^p d_mu_j^q R_ij.
```

All `R_pq` needed below are exact boundary derivatives, not finite differences.
For example:

```text
R_11 = P(G_i>0,G_j>0),

R_pq = (-1)^(p+q-4)
       [d_x^(p-2) d_y^(q-2) density_(G_i,G_j)(x,y)]_(0,0), p,q>=2.
```

When `p>=2,q=1`, take `(-1)^(p-2)` times the `(p-2)` derivative of
`density_i(x) P(G_j>0 | G_i=x)` at `x=0`; when `p>=2,q=0`, replace the
conditional probability by `E[G_j+ | G_i=x]` with the same sign.  The
remaining cases follow by symmetry.  These one- and two-dimensional Gaussian boundary jets extend the
analytic M124 collision jet to total degree eight.  Voigtlaender's theorem
justifies the delta derivatives distributionally.

For a symmetric order-`r` cumulant restricted to the pair, write

```text
K^(r)_p = kappa[ i repeated p times, j repeated (r-p) times ], 0<=p<=r.
```

The linear pair responses are

```text
R3 = (1/6)  sum_(p=0)^3 C(3,p) K^(3)_p R_(p,3-p)
R4 = (1/24) sum_(p=0)^4 C(4,p) K^(4)_p R_(p,4-p).
```

For `k3^2`, define the convolution

```text
A_q = sum_(p+r=q) C(3,p) C(3,r) K^(3)_p K^(3)_r.
```

Explicitly,

```text
A0 = K0^2
A1 = 6 K0 K1
A2 = 6 K0 K2 + 9 K1^2
A3 = 2 K0 K3 + 18 K1 K2
A4 = 6 K1 K3 + 9 K2^2
A5 = 6 K2 K3
A6 = K3^2.
```

Then

```text
R33 = (1/72) sum_(q=0)^6 A_q R_(q,6-q).
```

This formula includes every ordered slot assignment and divides the exchange
of the two identical connected cubic vertices by `2!` exactly once.

For the full retained quadratic truncation, additionally define

```text
B_q = sum_(p+r=q) C(3,p) C(4,r) K^(3)_p K^(4)_r
C_q = sum_(p+r=q) C(4,p) C(4,r) K^(4)_p K^(4)_r,

R34 = (1/144)  sum_(q=0)^7 B_q R_(q,7-q)
R44 = (1/1152) sum_(q=0)^8 C_q R_(q,8-q).
```

No new width-order tensor appears: these are scalar products of already
contracted repeated-output cumulants.

Under Edgeworth grading, write marginal corrections `m_i^[1]` and `m_i^[2]`
as in Section 4 and set

```text
C_ij^[1] = R3 - m_i0 m_j^[1] - m_j0 m_i^[1]

C_ij^[2] = R4 + R33
           - m_i0 m_j^[2] - m_j0 m_i^[2]
           - m_i^[1] m_j^[1].
```

For the full retained quadratic grading, replace `R3` by `R3+R4`, replace the
second raw term by `R33+R34+R44`, and use the correspondingly graded marginal
means.  Diagonal covariance is always computed by the univariate `q` formula;
never take a singular `rho->1` bivariate limit.

## 6. Minimal repeated-output cumulant tables

At width `n`, the complete mean/covariance response needs only:

```text
k3:
  iii                              n
  iij, directed repeated label     n(n-1)
  total                            n^2

k4:
  iiii                             n
  iiij, directed repeated label    n(n-1)
  iijj, unordered pair             n(n-1)/2
  total                            (3n^2-n)/2.
```

At `n=256` this is `65,536 + 98,176 = 163,712` float64 values, about
`1.31 MB` per layer.  The tables can be streamed, so all-layer storage is not
required.

Classical second order adds **zero** cumulant-table entries: `k3^2` uses products
of `iii/iij/ijj/jjj`.  The full retained quadratic model also adds no entries,
but any noisy `k4^2` product needs separate probe-product ownership.

## 7. Collision and diagram ownership

The following partition is mandatory.

1. `k3` and `k4` are connected cumulants, not central moments.  Gaussian Wick
   pairs have already been removed from `k4`; do not subtract or reinsert them
   in the response operator.
2. The local same-layer disconnected two-cubic diagram belongs to
   `(1/2)D3^2`.  It must not also be hidden inside a sixth central moment.  If a
   measured sixth moment is introduced later, first convert it to connected
   `k6` by the full set-partition formula.
3. Each symmetric repeated-output orbit is stored once.  The binomial factors
   in Sections 5--6 own all slot permutations; materializing permutations and
   then multiplying by the same binomial factor double-counts them.
4. Diagonal output variance belongs to the univariate `G_+^2` response.
   Off-diagonal covariance belongs to the nonsingular bivariate response.
5. Centralization owns `-m1_i m1_j` exactly once at second order.
6. At depth, a local second-order source owns two cumulant vertices born at the
   same conversion layer.  The Gaussian-map Hessian owns meetings of sources
   born earlier.  The derivative of a first-order source owns one earlier
   background perturbation meeting one current cumulant insertion.  These
   families are disjoint.
7. Celli's random-covariance `Q`-edge diagrams and the present connected
   cumulant diagrams are alternative parameterizations only after an explicit
   log-cumulant conversion.  Adding both descriptions directly double-counts
   covariance-mixture diagrams.

## 8. The exact second inhomogeneous tangent

Let `theta_l=(mu_l,C_l)` be the Gaussian background state and let one stage be

```text
theta_(l+1)(epsilon)
 = F_l(theta_l(epsilon))
 + epsilon S_l(theta_l(epsilon))
 + epsilon^2 T_l(theta_l(epsilon)) + O(epsilon^3),
```

where `S_l` is the first-order source and `T_l` contains `k4+k3^2` under
Edgeworth grading.  Expand

```text
theta_l(epsilon) = theta_l0 + epsilon a_l + epsilon^2 b_l + O(epsilon^3).
```

With `J_l=DF_l` and Hessian `H_l=D^2F_l`, exact coefficient matching gives

```text
a_(l+1) = J_l a_l + S_l

b_(l+1) = J_l b_l
          + (1/2) H_l[a_l,a_l]
          + DS_l[a_l]
          + T_l.
```

This is the second-order analogue of M125b.  If
`a_l=sum_s a_l^(s)`, then

```text
(1/2)H[a_l,a_l]
 = (1/2)sum_s H[a_s,a_s] + sum_(s<t) H[a_s,a_t].
```

Thus every unordered earlier-source pair appears exactly once without storing
or propagating the pairs separately.

The affine part of `F_l` is linear and has zero Hessian.  For the Gaussian ReLU
mean `m(mu,v)`, the required Hessian entries are

```text
m_mumu = phi(alpha)/sigma
m_muv  = -alpha phi(alpha)/(2 sigma^2)
m_vv   = (alpha^2-1) phi(alpha)/(4 sigma^3).
```

For each raw pair moment, the state has only five local coordinates
`(mu_i,mu_j,v_i,v_j,c_ij)`, so a directional Hessian uses 15 scalar second
partials per pair, not a width-four Hessian.  Price's theorem produces them as
Gaussian boundary expectations.  For central covariance,

```text
D2 C[a,a] = D2 R[a,a]
             - D2m[a,a] m0^T - m0 D2m[a,a]^T
             - 2 Dm[a] Dm[a]^T.
```

Therefore a Hessian-vector application is `O(n^2)` scalar work.  Each first or
second tangent still needs one affine covariance congruence
`W^T deltaC W`, which is `O(n^3)`.  The coalesced two-tangent carrier is
`O(L n^3)`.

### Completeness caveat

`DS_l[a_l]` differentiates both the Gaussian response kernel and the cumulant
source:

```text
DS[a] = (D_background response)[a ; kappa]
        + response[D kappa[a]].
```

Freezing M126's cumulant table while the background moves drops the second
term and is not a complete second-order method.  Differentiating its exact easy
matrix identities remains `O(L n^3)`.  Differentiating the hard Hutchinson
`ABAB/iijj` estimator may require product-rule matrix calls for `A`, `g`, and
`E`; this constant and its probe covariance are currently unresolved.  An
explicit `O(L^2 n^3)` source-pair implementation is unnecessary for the
response, but may be used as a small-width oracle.

## 9. Can M126 supply the tables below 100B?

For one target `256x256` float32-shaped matrix multiplication, FlopScope bills

```text
2 n^3 - n^2 = 33,488,896.
```

Float64 doubles this to `66,977,792`.  A covariance congruence uses two calls,
or `133,955,584` billed operations.  Hence one additional second tangent costs
at least

```text
30 stages: 4,018,667,520
31 stages: 4,152,623,104,
```

before local kernels, source derivatives, copies, or contingency.  This lower
bound is unavoidable for a dense complete covariance state.

M126's hard residual uses two dense products per probe per layer, the same
`4.019--4.153B` across the depth **per probe**.  Counting the M125 first tangent
and M128 second tangent, but optimistically charging no easy source work, gives

```text
C_lower(P) = (P + 2) * 4.153B     [31-stage conservative form].
```

Thus `P<=22` is necessary for a strict `<100B` implementation even before the
exact stars, adjacent paths, collision corrections, scalar kernels,
`D source`, allocations, and safety margin.  At `P=16`, this lower bound is
about `74.75B`, leaving only `25.25B` for everything else.

Consequences:

- The Edgeworth-grade `k3^2` term itself is affordable and needs no new
  Hutchinson probes.
- Linear noisy `k4` remains unbiased if M126's estimator is unbiased.
- A naive square of a noisy cumulant estimate is biased.  If the full retained
  `k4^2` branch is ever tested, use independent probe banks or an exactly
  derived order-two U-statistic over distinct probes.  Random orthogonal probes
  are not automatically independent; their cross-probe correction must be
  proved.
- If differentiating the hard source doubles its two-product probe cost, even
  moderate probe counts threaten the `100B` ceiling.  No under-100 claim is
  valid until the differentiated call graph is enumerated.
- M124 cannot satisfy this particular `100B` moonshot: its protected
  source-only cost is already `98.8342976B` before the second tangent.

The correct current answer is therefore: **M126 can plausibly provide the
first-order tables under 100B, and `k3^2` adds almost no source cost, but a
complete differentiated-source M128 is not yet certified under 100B.**

## 10. Stability, positivity, and permitted reorganizations

Celli's examples require much larger width before an order-eight Hermite term
stops dominating, and the paper attributes small-width deterioration to
oscillation.  Our width 256 and fixed-weight regime provide no automatic small
parameter.  The following distinctions are mandatory.

### Plain polynomial Edgeworth

This is the canonical, coefficient-free falsifier.  It is a signed expansion:
the implied density may be negative, the corrected variance may be negative,
and a corrected covariance may be indefinite.  Do not repair these failures by
elementwise clipping.  Predeclare fail-closed gates on correction size,
finite values, minimum covariance eigenvalue, and order-two/order-one norm
ratio.

### Exponential moment coordinates

For a positive scalar mean series `m0+epsilon m1+epsilon^2 m2`,

```text
m_exp = m0 exp(epsilon m1/m0
               + epsilon^2 [m2/m0 - (m1/m0)^2/2])
```

matches through second order and remains positive.  For a positive-definite
covariance, whiten corrections

```text
A1=C0^(-1/2) C1 C0^(-1/2),
A2=C0^(-1/2) C2 C0^(-1/2)
```

and use

```text
C_exp=C0^(1/2) exp(epsilon A1
                   + epsilon^2[A2-A1^2/2]) C0^(1/2).
```

This is permutation/gauge covariant and PSD, and matches the series through
second order.  It introduces higher orders and an eigendecomposition/matrix
exponential, so it must be a separately frozen branch with its own cost and
cannot be chosen after seeing efficacy.

Exponentiating the **truncated cumulant differential operator** does not by
itself define a positive probability law; a truncated characteristic exponent
need not be positive definite.

### Padé

A scalar `[1/1]` approximant is uniquely determined by the first three series
coefficients when `m1 != 0`: its denominator is
`1-(m2/m1) epsilon`.  It must fail closed near a denominator zero.  There is no
canonical entrywise matrix Padé that preserves covariance PSD, and any fitted
damping coefficient is forbidden.  Padé is at most a predeclared scalar-mean
falsifier.

### Cornish--Fisher

Cornish--Fisher approximates quantiles, not the required mean/covariance source.
It does not close the bivariate covariance recurrence and is rejected here.

### Mystical or geometric damping

Tau folds, sacred ratios, cymatic phases, and hand-selected damping constants
supply no cumulant asymptotic, invariance proof, or error bound.  They are not
mechanisms and are excluded.

## 11. Required generated-only repair ladder

1. Implement `R_pq` analytic jets through total degree eight and verify them
   against independent one-dimensional conditional integration, including
   nonsingular endpoint guards.
2. Verify every coefficient above by symbolic convolution and by applying the
   response to generated polynomial test functions whose expectations are
   known exactly.
3. Implement the local Gaussian ReLU Hessian-vector product and prove dense
   finite-difference convergence only as a test, never as deployment code.
4. Prove the second inhomogeneous recurrence equals explicit propagation of
   all generated source pairs at widths `4--8`, including `DS[a]` and same-layer
   `k3^2` ownership.
5. Derive tangent versions of every M126 exact and Hutchinson contraction.
   For noisy products, prove unbiased cross-probe/U-statistic ownership.
6. Enumerate every float64 call, copy, symmetry restore, scalar jet, probe, and
   allocation.  Require complete protected cost `<100B`; no “plausible” range.
7. Only after 1--6 pass, freeze generated widths/depths/seeds and compare plain
   first versus second order.  Require improvement in every stratum, a bounded
   second/first correction ratio, finite outputs, covariance positivity, and no
   retry.  Do not touch contest/public/private outcomes.

## 12. Final verdict

**REPAIR.**

The mathematical response is implementable: the complete Edgeworth-order-two
formulas close on `O(n^2)` repeated-output tables, `k3^2` has exact ownership,
and a coalesced Hessian recurrence reduces source--source propagation to
`O(L n^3)`.  This is substantially stronger than first Born.

The mechanism is not yet promotable because `DS[a]` requires a differentiated
M126 source, the hard probe-product estimator has no completed second-order
unbiasedness/cost proof, and high-order Hermite stability is not guaranteed in
the fixed-weight width-256 regime.  Kill only if the exact differentiated call
graph breaches `100B`, if explicit-pair parity fails, or if the eventual frozen
generated second-order correction is uniformly worse.  Until one of those
events, preserve the formulas and repair the missing source derivative.
