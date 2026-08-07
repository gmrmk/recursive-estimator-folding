# M147 endpoint-safe Gaussian bridge / Frechet audit -- 2026-08-07

## Decision first

M147 splits cleanly into two dispositions.

1. **Endpoint-safe bivariate ReLU bridge: STATIC SURVIVOR.**  The artificial
   M122 guard `abs(rho) <= 0.80` is removable.  The user-supplied
   Rosenbaum/Owen positive-part formula, evaluated in an angular Plackett
   coordinate and joined to exact rank-one limits, returns the value and
   interior Frechet derivative for every `-1 < rho < 1`.  At `rho=+-1` it
   returns the exact value and only a PSD-feasible one-sided directional
   derivative; it never calls that boundary object an ambient Frechet
   derivative.

2. **Direct central `[2,1,1]` conditional oracle: CORRECTNESS SURVIVOR, LITERAL
   TARGET IMPLEMENTATION COST-KILLED.**  It eliminates the M129 trivariate
   Hermite series, accepts exact conditional `rho=+-1`, and agrees with the
   independent M129 moment-partition oracle to `2.99e-14` in value and
   `2.92e-14` in tangent.  However, its frozen 48/64 outer rule composed with
   the 16/32 angular rule costs at least 108,480 billed operations per ordinary
   high-correlation coefficient under an intentionally favorable lower bound,
   already above the frozen 102,400-operation reserve.  A conditional
   `rho=.999` adversary costs at least 606,720.  Batching changes wall time, not
   those billed element operations.

No response cell, benchmark, truth, scorer, model, champion, or submission was
opened.  Nothing here authorizes a retry of M143's consumed token.

## 1. Failure-local recursive mutation

M143 failed before its proposal law was evaluated because its inherited call
chain was

```text
M143 build_cell
  -> M129 build_state_frechet
  -> M122 build_state
  -> refuse if any abs(rho) > .80.
```

That guard certifies convergence of one truncated Hermite series; it is not a
singularity of the bivariate Gaussian law.  The legitimate mutation is
therefore to replace only that numerical representation while preserving:

- the Gaussian mean/covariance state;
- exact ReLU marginal moments;
- the normalized bridge definition;
- M129's tree and collision ownership; and
- fail-closed PSD and tangent semantics.

Merely catching `RuntimeError`, clipping `rho`, adding a ridge, changing the
generated seed, or reissuing M143's token would not repair the failed
mathematical link and remains prohibited.

## 2. Endpoint-safe bivariate value

Let

```text
X = sx (a + G1),    Y = sy (b + G2),
Corr(G1,G2) = r,    sx,sy > 0,
F(a,b,r) = E[(a+G1)_+ (b+G2)_+],
Q(a,b,r) = P(G1>-a, G2>-b).
```

The Rosenbaum-type formula supplied in the mathematics brick is equivalent to

```text
Ba = phi(a) Phi((b-r a)/q),
Bb = phi(b) Phi((a-r b)/q),
J  = exp(-[(1+r)(a-b)^2 + (1-r)(a+b)^2] / [4(1-r^2)]),
q  = sqrt((1-|r|)(1+|r|)),

F = b Ba + a Bb + q J/(2 pi) + (a b + r) Q.              (1)
```

The physical raw moment is `sx sy F`.  Equation (1) is exactly the user's
Rosenbaum/Owen candidate, but three apparently harmless operations are unsafe
near an endpoint:

- `1-r*r` loses relative precision;
- `a*a+b*b-2*r*a*b` cancels when the thresholds coalesce; and
- near `r=-1`, the four terms in (1) can cancel down from `O(sqrt(1+r))` to
  `O((1+r)^(3/2))`.

M147 uses the factored square root, the displayed nonnegative rotated
quadratic, and `math.fsum`.  It independently certifies (1) against an endpoint
Price enclosure.  If the closed form falls outside that enclosure by more
than a termwise roundoff allowance, it evaluates the small nonnegative Price
remainder rather than accepting the cancellation.

### 2.1 Angular Plackett/Owen coordinate

Plackett's identity becomes nonsingular after `r=sin(theta)`:

```text
Q(a,b,r) = Phi(a)Phi(b)
 + (1/(2 pi)) int_0^asin(r)
     exp[-(a-b)^2/(4(1-sin(theta)))
         -(a+b)^2/(4(1+sin(theta)))] dtheta.              (2)
```

The Jacobian cancels the `1/sqrt(1-r^2)` density pole.  The remaining
integrand is in `[0,1/(2 pi)]`, including its endpoint limit.  M147 evaluates
it with a globally adaptive 16/32 paired Gauss-Legendre rule.  The paired
disagreement is correctly labeled an a-posteriori numerical indicator, not a
rigorous interval.

There is also an independent rigorous enclosure.  If `s=sign(r)` and `Qs` is
the exact rank-one probability, monotonicity and the bounded angular integrand
give

```text
r >= 0: max(0, Q+ - acos(r)/(2 pi)) <= Q(r) <= Q+,
r <  0: Q- <= Q(r) <= min(1, Q- + acos(|r|)/(2 pi)).      (3)
```

This is why the implementation can hostile-check the numerical quadrature
without pretending that coarse/fine agreement alone is proof.

The change of variable follows the reduction identity of R. L. Plackett,
*Biometrika* 41 (1954), 351-360,
https://doi.org/10.1093/biomet/41.3-4.351.  Owen's bivariate-normal tables and
`T` representation are D. B. Owen, *Annals of Mathematical Statistics* 27
(1956), 1075-1090, https://doi.org/10.1214/aoms/1177728074.

### 2.2 Exact rank-one limits

At `r=s in {+1,-1}`, write `G2=s G1= s Z`.  For arbitrary positive integer
powers,

```text
E[(a+Z)_+^p (b+sZ)_+^q]
```

is a finite polynomial combination of truncated univariate normal moments.
M147 evaluates those moments recursively, over

```text
s=+1: Z in [max(-a,-b), infinity),
s=-1: Z in [-a,b] if -a<b, otherwise the moment is zero.  (4)
```

In particular,

```text
Q+ = Phi(min(a,b)),
Q- = max(0, Phi(a)+Phi(b)-1).                             (5)
```

The standardized mean derivatives at the endpoint are

```text
r=+1:
  Fa = b Q+ + phi(min(a,b)),
  Fb = a Q+ + phi(min(a,b));

r=-1, a+b>0:
  Fa = b Q- - phi(a) + phi(b),
  Fb = a Q- + phi(a) - phi(b),

r=-1, a+b<=0: Fa=Fb=0.                                  (6)
```

The inward covariance derivative is the one-sided Price limit `Fr=Qs`.

### 2.3 Rigorous singularity-subtracted value enclosure

Price's theorem gives `dF/dr=Q`.  Since Plackett gives `dQ/dr=phi_2>0`, the
endpoint-linear expansion has a nonnegative remainder:

```text
r >= 0: F(r) = F(+1) - (1-r)Q+ + R,
r <  0: F(r) = F(-1) + (1+r)Q- + R.                      (7)
```

Changing to the angle coordinate and bounding its exponential by one proves

```text
0 <= R <= B(r),
B(r) = [sqrt(1-r^2) - |r| acos(|r|)]/(2 pi).             (8)
```

Near an endpoint, direct subtraction in `B` loses the `O(delta^(3/2))` term;
M147 evaluates `sin(theta)-theta cos(theta)` by its series beginning
`theta^3/3-theta^5/30+theta^7/840`.

The most adversarial zero-threshold negative-endpoint test uses
`r=-1+1e-12`.  The naive arc-cosine expression loses the tiny result; M147's
nonnegative remainder gives `1.50049e-19` and stays inside (8).

The covariance differentiation used here is an instance of Price's theorem
for distributional nonlinearities.  A rigorous modern statement is F.
Voigtlaender, *A General Version of Price's Theorem*, Journal of Theoretical
Probability (2021), https://doi.org/10.1007/s10959-020-01017-w.

## 3. Frechet and PSD-boundary semantics

For `|r|<1`, Price/Bonnet gives the standardized derivatives without
differentiating a bivariate CDF:

```text
Fa = b Q + r Ba + Bb,
Fb = a Q + r Bb + Ba,
Fr = Q.                                                  (9)
```

With `M=sx sy F`, M147 applies the ordinary chain rule through `sx`, `sy`,
`a=mx/sx`, `b=my/sy`, and `r=Cxy/(sx sy)`.  The test grid through
`r=+/-0.999999` agrees with centered finite differences.  On the old
`|r|<=.75` domain, value and tangent agree with M129's 96-term Hermite oracle
to `9.72e-17` and `1.05e-17` absolute respectively.

At `|r|=1`, the covariance lies on the boundary of the PSD cone.  There is no
ambient two-sided Frechet derivative.  For a `t -> 0+` path, feasibility
requires

```text
-sign(r) rdot >= 0,                                     (10)
```

equivalently `det'(0+)>=0`.  M147 accepts only that one-sided direction and
labels it `one-sided-PSD-directional`; an outward tangent fails explicitly.

For a rank-deficient 3x3 local state, the corresponding tangent-cone check is

```text
V0^T Cdot V0 >= 0,                                      (11)
```

where `V0` spans the nullspace of `C`.  Zero marginal variance is still
refused: at a zero-variance variable whose mean is at the ReLU kink, the
ordinary derivative can be singular and this implementation has no valid
certificate for it.

## 4. Width-independent connected `[2,1,1]` rule

Let `A=ReLU(X_i)`, `B=ReLU(X_j)`, `C=ReLU(X_k)` and use lower-case letters for
their centered versions.  Translation invariance of cumulants gives the much
smaller identity

```text
kappa(A,A,B,C)
 = E[a^2 b c] - Var(A) Cov(B,C) - 2 Cov(A,B) Cov(A,C).   (12)
```

Condition on the standardized repeated preactivation `Z_i=z`.  The
conditional `(X_j,X_k)` law has affine mean and constant 2x2 Schur covariance.
At each `z`, M147 evaluates

```text
h(z) = E[(B-mB)(C-mC) | z]
     = E[BC|z] - mB E[C|z] - mC E[B|z] + mB mC.          (13)
```

Then

```text
E[a^2bc] = int phi(z) (ReLU(mi+si z)-mA)^2 h(z) dz.      (14)
```

The line is split exactly at `z=-mi/si`; both tails use
`radial=t/(1-t)`.  The integrand is continuous at the ReLU boundary, so the
two moving-boundary terms cancel.  The tangent differentiates the same fixed
nodes, conditional Schur complement, pair raw moment, univariate means, and
global centering.  A frozen 48/64 pair must meet absolute disagreements

```text
abs(delta coefficient) <= 2e-8,
abs(delta tangent)     <= 2e-7.                          (15)
```

Finally, the M129 tree value/tangent is subtracted to return the exact
collision defect consumed by M133-style sampling.

### Width-256 contract versus the reference state constructor

`collision211_local_state_dot` is the relevant deployment-shaped API.  A
width-256 caller gathers exactly three mean entries and the corresponding 3x3
covariance and tangent minors.  All subsequent work is independent of ambient
width and does not materialize an `n^3` or `n^4` tensor.  An exact rank-deficient
local state is accepted with (11); the test suite exercises an exact
conditional `rho=+1` and an inward tangent without an endpoint abort.

`build_endpoint_state_frechet` has an `n<=16` guard because it is a small
reference constructor.  That guard is not a mathematical limit of the local
per-triple API.  Conversely, the existence of a three-variable API does not
provide a target-width all-pairs bridge builder or a free `O(n^3)` coefficient
table.

The central-moment route is consistent with the classical truncated-normal
moment program of G. M. Tallis, *JRSS B* 23 (1961), 223-229,
https://doi.org/10.1111/j.2517-6161.1961.tb00408.x, but equations (12)-(14) are
implemented directly rather than importing a black-box multivariate CDF.

## 5. Hostile evidence

Ten response-free tests pass under bundled NumPy 2.3.5:

1. angular quadrant probability and rigorous endpoint enclosures;
2. exact positive and negative rank-one values and one-sided Price derivative;
3. cancellation-safe `r=-1+1e-12` value;
4. agreement with M129 throughout its certified pair domain;
5. finite-difference Frechet checks near both endpoints plus permutation;
6. positive-gauge covariance and outward tangent refusal;
7. high-correlation state acceptance while old M122 refuses;
8. moderate `[2,1,1]` agreement with independent moment partitions;
9. conditional `rho=.999` tangent finite difference and cost exposure; and
10. width-independent local API at exact conditional `rho=+1`, including
    outward full-PSD tangent refusal.

Measured static defects are in
`m147_endpoint_safe_bridge/M147_STATIC_AUDIT_20260807.json`:

| check | result |
|---|---:|
| legacy pair maximum value defect | `9.7145e-17` |
| legacy pair maximum tangent defect | `1.0408e-17` |
| moderate 211 cumulant defect | `2.9844e-14` |
| moderate 211 tangent defect | `2.9187e-14` |
| conditional-rho=.999 value 48/64 disagreement | `9.1674e-10` |
| conditional-rho=.999 tangent disagreement | `5.5020e-11` |

Positive-gauge scaling multiplies a raw pair by the product of the two gauges
and leaves its normalized bridge invariant.  Permuting the variables permutes
the state, and swapping the two singleton labels leaves the `[2,1,1]` defect
unchanged.  These are algebraic covariance properties, not fitted tests.

## 6. Target cost boundary

The frozen M133/M143 worksheet reserves

```text
1,625,292,800 / (31*512) = 102,400 billed operations
```

per sampled exact coefficient.  The literal M147 rule uses two mapped tails,
48+64 outer nodes, and 16+32 nonnested angular nodes:

```text
2*(48+64)*(16+32) = 10,752 angular evaluations           (16)
```

before any adaptive split.  The measured high-correlation state used 10,848;
the conditional `rho=.999` adversary used 60,672.

Even granting that angle geometry is precomputed, one evaluation needs at
least two multiplications, one addition, one exponential, and one final
multiplication.  The scorer bills float64 at 2x, so the favorable lower bound
is ten billed operations/evaluation:

```text
ordinary: 10,848*10 = 108,480 > 102,400,
endpoint: 60,672*10 = 606,720 > 102,400.                 (17)
```

Equation (17) omits CDFs, outer density, ReLU moments, derivatives,
accumulations, the Schur complement, gathers, and call/allocation residual.
It is therefore a kill, not merely an imprecise estimate.  Vectorization can
repair the observed ~0.03-0.07 scalar seconds per coefficient but cannot
repair billed element counts.

## 7. Frozen repair map -- not yet an implementation

The ordinary lower bound misses reserve by only 5.9%, so one structurally new
quadrature layout remains worth preserving.  It does not change the current
cost-killed verdict.

### R1: nested rules rather than two disjoint Gaussian rules

The current 16/32 and 48/64 Gauss-Legendre pairs share no nodes.  A nested
Gauss-Kronrod layout can return a coarse and fine estimate from one node bank:

```text
inner angular rule: embedded 15 / 31, 31 unique nodes;
outer split-tail rule: embedded 31 / 63, 63 unique nodes per side.

fixed unsplit count = 2*63*31 = 3,906 angular evaluations;
favorable f64 core lower bound = 39,060 billed operations.              (18)
```

Even one bisection of every inner panel would give 7,812 evaluations and a
78,120-operation core lower bound, leaving 24,280 operations for the rest of
the coefficient.  The hard proposed cap is 8,000 angular evaluations per
coefficient; beyond it the candidate fails closed in response-free preflight.

The embedded rules must preserve the absolute gates (15), and a native
FlopScope trace must prove the complete coefficient -- not just the exponent
kernel -- below 102,400 with margin.  Gauss-Kronrod construction and positive
nested weights are described by Calvetti, Golub, Gragg and Reichel,
*Mathematics of Computation* 69 (2000), 1035-1052,
https://doi.org/10.1090/S0025-5718-00-01174-1.

### R2: certified endpoint asymptotic bypass

For a near-endpoint pair, equations (3) and (8) permit an integration-free
approximation `Fendpoint +/- delta*Qendpoint`.  Its physical value error is

```text
Ev <= sx sy B(r).                                        (19)
```

If the cheap interior boundary terms in (9) are retained and only `Q` is
replaced by `Qs`, a conservative physical tangent error is

```text
Et <= |(sx sy)dot| B(r)
    + sx sy A(r) (|b adot| + |a bdot| + |rdot|),
A(r)=acos(|r|)/(2 pi).                                   (20)
```

For the complete coefficient, accumulate (19)-(20) with the signed quadrature
weights and local sensitivity factors.  The endpoint bypass is allowed only
when its aggregate bounds consume at most half the frozen budgets:

```text
aggregate Ev <= 1e-8,
aggregate Et <= 1e-7,                                   (21)
```

leaving the other half for embedded outer/inner disagreement.  Worst-case
tangent sensitivity makes (21) useful only extremely near the endpoint
(often `delta~1e-12`), so it repairs the singular adversary but does not by
itself remove the ordinary 5.9% excess.

### What does and does not cross the boundary

- **Common-node geometry reuse:** required, and already assumed by the lower
  bound.  It saves `sin/cos/denominator` work and wall time but cannot alone
  cross (17).
- **Batching:** required for residual wall time, but billed operations remain
  unchanged; it cannot alone cross.
- **Singleton symmetry:** already owned by the canonical unordered singleton
  pair; the two mapped tails are not symmetric for nonzero means or tangents
  and cannot be deleted.
- **Endpoint subtraction:** certifiably removes endpoint cancellations and can
  delete inner nodes under (21), but only in a narrow endpoint region.
- **Nested 15/31 and 31/63 rules:** the only preserved operator that crosses
  the arithmetic lower bound on paper.  It remains unproven until the absolute
  gates, adversarial grid, and complete native trace pass.

## 8. What M147 unlocks and what it cannot

### It unlocks

- response-free domain preflight for a genuine M143 descendant without the
  arbitrary `abs(rho)<=.80` abort;
- exact pair bridge values/tangents for high-correlation generated states;
- a width-independent, exact-endpoint per-triple `[2,1,1]` correctness oracle;
- an independent check of future Owen/Plackett, nested-quadrature, or
  singularity-subtracted target kernels; and
- possible reuse of already-computed global quadrant probabilities and local
  kernels in pair-state construction.

### It does not unlock

- a retry, family deletion, or result inference from M143's consumed token;
- a target-ready 512-coefficient/layer implementation under the current cost
  reserve;
- a width-256 all-pairs constructor, native f32 parity, residual-time proof,
  or zero-failure target trace;
- any efficacy or variance-reduction conclusion about suffix energy; or
- an ambient Frechet derivative at the PSD boundary.

## 9. Recursive disposition

**Promote to salvage bank:** angular Plackett coordinate, exact endpoint power
moments, Price remainder enclosure, tangent-cone semantics, direct central
identity (12), local width-independent API, and the nested-rule repair map.

**Kill implementation:** literal 48/64 by 16/32 conditional coefficient as a
target kernel under the 102,400-operation reserve.

**Unresolved family:** nested embedded quadrature plus endpoint bypass under
the absolute `(2e-8,2e-7)` coefficient/tangent gates.  Reopen only with a new
module, response-free hostile grid, complete native cost trace, and independent
audit.  Do not alter or rerun M143.

