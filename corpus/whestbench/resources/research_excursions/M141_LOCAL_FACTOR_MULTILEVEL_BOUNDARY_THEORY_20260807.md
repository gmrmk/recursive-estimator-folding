# M141: local-factor randomized boundary coefficient

Date: 2026-08-07  
Scope: generated mathematics and static accounting only.  This note read no
contest model, truth, scorer, leaderboard, public/private instance, submission,
or champion artifact.  It performs no outcome run.

## Decision

**Preserve one exact local operator; do not promote or compose it yet.**

The useful observation is local rather than global.  Every *three-coordinate*
Gaussian block has an exact independent-residual plus at-most-two-factor
representation.  Thus the surviving M131 trivariate boundary coefficient has
an exactly unbiased, fixed-cost, two-dimensional randomized-stratification
estimator.  It needs neither a trivariate CDF nor an infinite Hermite/Russian-
roulette tail.

This is a genuine change of the coefficient-information class:

```text
M131:  one factor + exact bivariate rectified primitive at 80 outer nodes
M141:  two factors + three independent univariate rectified primitives at
       nine fixed jittered cells
```

It does **not** cancel the M131 `Q3` term, and its additional coefficient noise
can only add to the M133 Horvitz--Thompson variance at fixed triple count.  It
therefore cannot by itself reopen M133's failed `K=512` variance gate.  Its
only honest role is a cheap, finite-variance exact coefficient engine for an
independently successful triple-allocation mechanism (for example a future
balanced-design child).  A fixed `3 x 3` version fits the protected `K=512`,
five-product envelope with substantial arithmetic margin; no target efficacy,
native trace, or coefficient-noise screen has yet been performed.

The tempting infinite-level alternatives are ruled out for this deployment:
unbounded Russian roulette has no deterministic per-MLP cost cap, while a
partial-correlation path adds an integration dimension and does not remove the
irreducible orthant term.

## 1. Frozen contract

The parent is M133's canonical, distinct `[2,1,1]` unit `(i;j<k)`.  Its exact
coefficient is a fourth-cumulant defect

```text
Delta_ijk = E[(X_i)_+^2 (X_j)_+ (X_k)_+] - lower Wick/tree terms,
X ~ N(mu,C).
```

The proposal `q_ijk` is M133's already-built, full-support three-bank proposal
with its five-percent uniform rescue.  It is frozen before any coefficient
jitter is drawn.  The five M133 batched outer products, collision ownership,
and all other source populations are unchanged.

Invariants retained from the recursive ledger:

* bias class: exact unbiasedness in real arithmetic, conditional on the frozen
  proposal;
* no change to the legal/billed envelope or to the M126/M125b carrier;
* a fixed maximum of nine factor cells per selected triple (no stochastic FLOP
  tail);
* no claim about float32 parity, residual wall time, or target efficacy.

## 2. Exact local factorization -- why M135's global obstruction does not apply

For one sampled triple, write the SPD `3 x 3` covariance as

```text
C = V diag(lambda_1,lambda_2,lambda_3) V^T,
lambda_1 <= lambda_2 <= lambda_3,
lambda = lambda_1,
U = [ sqrt(lambda_2-lambda_1) v_2,
      sqrt(lambda_3-lambda_1) v_3 ].
```

Zero columns are removed.  Hence, with `r <= 2`,

```text
C = lambda I_3 + U U^T,
X_a = mu_a + u_a.H + sqrt(lambda) epsilon_a,
H ~ N(0,I_r),       epsilon_a iid N(0,1).              (1)
```

Conditionally on `H`, the three coordinates are independent.  Let

```text
M_p(m,v) = E[(m + sqrt(v) Z)_+^p],  Z ~ N(0,1),
M_0(m,v) = Phi(m/sqrt(v)).
```

For `v>0`, the only needed primal expressions are

```text
M_1 = m Phi(alpha) + sqrt(v) phi(alpha),
M_2 = (m^2+v) Phi(alpha) + m sqrt(v) phi(alpha),
alpha = m/sqrt(v),                                      (2)
```

with their continuous `v=0` limits `m_+` and `m_+^2`.  Thus the only hard raw
moment is exactly

```text
R_ijk = E_H[ M_2(mu_i+u_i.H,lambda)
             M_1(mu_j+u_j.H,lambda)
             M_1(mu_k+u_k.H,lambda) ].                 (3)
```

All lower terms in `Delta_ijk` remain the exact univariate/bivariate
primitives already owned by M131/M133.

This does not contradict M135.  M135 required a *single global* `256 x 256`
law `D+UU^T` with small `r`, which generically needs `r >= 234`.  Equation (1)
is rebuilt for one selected `3 x 3` block, where rank two is an identity rather
than an approximation.

The Tallis/truncated-normal lineage supports the moment representation, but
the factorization and estimator here are derived directly:
[Manjunath--Wilhelm (2012)](https://arxiv.org/abs/1206.5387),
[Mamis (2022)](https://arxiv.org/abs/2202.00189).

## 3. Fixed-cost unbiased two-factor stratification

Use a separable rational normal-coordinate map

```text
h(t) = tan(pi(t-1/2)),       J(t) = pi sec^2(pi(t-1/2)),
0 < t < 1.
```

For `r=2`, define the ordinary square-integrable integrand

```text
f(t_1,t_2) = phi(h(t_1)) phi(h(t_2)) J(t_1)J(t_2)
             M_2(m_i(t),lambda) M_1(m_j(t),lambda) M_1(m_k(t),lambda).
                                                               (4)
```

For fixed `m`, draw independent `U_ab,V_ab ~ Unif(0,1)` for every cell and
return

```text
Rhat_m = m^-2 sum_(a,b=0)^(m-1)
  f((a+U_ab)/m, (b+V_ab)/m).                              (5)
```

For `r=1`, remove the second coordinate and use `m` one-dimensional cells.
For `r=0`, equation (3) is deterministic.  A predeclared implementation uses
`m=3` in every `r=2` case and does not adapt the cell count to the sampled
values.

### Exactness

Each cell point in (5) is uniform on its cell.  Summing the cell integrals
gives the integral of (4), so

```text
E_U[Rhat_m | mu,C] = R_ijk.                               (6)
```

Therefore `Deltahat = Rhat_m - lower_terms` is unbiased.  If `e=(i,j,k)` is a
M133 ordered triple and `F_e` its five-product feature contribution, then

```text
E_(e,U)[ Deltahat_e F_e / (2 K q_e) ]
  = sum_(i,j<k) Delta_ijk F_ijk.                          (7)
```

The M133 factor `1/2` still owns the ordered-singleton convention exactly.
No fitted coefficient and no public/target information enters this identity.

## 4. Finite variance, including the high-correlation edge

This section is the important gate: it proves finite variance without claiming
that the variance is small enough for the full estimator.

### 4.1 Primal coefficient

`M_p` is polynomially bounded in `m`, and its first mean derivative is

```text
d_m M_p = p M_(p-1)  (p=1,2),
```

where `d_m M_1=M_0` is bounded by one.  Differentiating (4) once thus produces
a polynomial in `|h_1|+|h_2|` times
`phi(h_1)phi(h_2)J(t_1)J(t_2)` and at most the same tail factors.  The
super-exponential normal factors dominate the rational Jacobians at all four
faces of `[0,1]^2`.  Consequently

```text
f in H^1([0,1]^2),       integral ||grad f||^2 dt < infinity.       (8)
```

Crucially this uses only first derivatives of `M_1,M_2`; it contains no
`1/sqrt(1-rho^2)` bivariate-density term.  It remains valid as a conditional
correlation tends to `+/-1`, and also at `lambda -> 0` after the continuous
limits in (2).  Pair correlations such as `.975` are therefore well inside the
finite-variance domain.  The bound's *constant* can be large when means or
scales are large, so this is a finiteness certificate, not a quality claim.

On a square cell of side `1/m`, the Poincare inequality gives

```text
Var(Rhat_m | mu,C)
 <= ||grad f||_L2^2 / (pi^2 m^4)
 =  ||grad f||_L2^2 / (pi^2 K_q^2),     K_q=m^2.          (9)
```

The independent jitter in (5) is essential for the elementary unbiasedness
proof.  The `r=1` analogue has `O(K_q^-3)` under the corresponding `H^1`
condition.  Equation (9) is a direct proof, not an extrapolation from a QMC
paper.

### 4.2 What the bound does *not* buy

For the complete HT source, independent coefficient jitter adds the nonnegative
term

```text
(1/(4K)) sum_e ||F_e||_F^2 Var(Rhat_e)/q_e                (10)
```

to the usual exact-coefficient HT second moment (up to the common centering
term).  Thus randomized coefficient integration cannot reduce M133's
fixed-`K` triple variance.  It can only exchange the 80-node deterministic
coefficient cost for a small, certified random error.  This is the decisive
anti-hype result.

Before any generated efficacy screen, the child must pass both:

```text
G1: measured complete-output MSE(m=3) / MSE(exact coefficient) <= 1.05;
G2: no width has an upper paired 90% confidence bound above 1.10.
```

Those gates are deliberately prospective; no values have been measured here.

## 5. Frozen-proposal Frechet tangent without differentiating eigenvectors

Directly differentiating `U` in (1) is a trap: eigenvectors are not a stable
Frechet chart at repeated eigenvalues.  Use the Gaussian Price identity at the
base state instead.  Set

```text
g_i(x)=x_+^2,   g_j(x)=g_k(x)=x_+,
g_i'=2x_+, g_i''=2 1{x>0},
g_j'=g_k'=1{x>0}, g_j''=g_k''=delta_0.
```

For a state direction `(mudot,Cdot)`, the raw-moment tangent is

```text
Rdot = sum_a mudot_a E[g_a' product_(b!=a) g_b]
     + sum_(a<b) Cdot_ab E[g_a'g_b' product_(c!=a,b) g_c]
     + .5 sum_a Cdot_aa E[g_a'' product_(b!=a) g_b].     (11)
```

Every expectation in (11) without a delta uses precisely the same conditional
factor rule as (3), with `M_0`, `M_1`, or `M_2` substituted.  These retain the
finite-variance argument in Section 4.

Do **not** sample the two delta terms conditionally; their conditional density
has a `lambda^-1/2` spike as `lambda -> 0`.  Rao--Blackwellize each exactly:

```text
E[(X_i)_+^2 delta_0(X_j) (X_k)_+]
 = p_Xj(0) E[(X_i)_+^2 (X_k)_+ | X_j=0],                  (12)
```

and symmetrically for `k`.  The right-hand side is a deterministic bivariate
rectified normal `[2,1]` primitive, evaluated by M131's certified conditional
one-dimensional oracle (including its degenerate bivariate limit).  This
removes, rather than merely tolerates, the near-singular tangent variance.

Differentiate each lower Wick/tree term with the same univariate/bivariate
Price primitives.  This defines `Deltadot` exactly at the base state.  With
the M133 proposal and all selected triples fixed at that state,

```text
d/dtheta E_(q0,U)[ Deltahat_theta F_theta / q0 ]|theta0
 = E_(q0,U)[ (Deltahatdot F + Deltahat Fdot)/q0 ].        (13)
```

There is no `qdot` or eigenvector derivative.  Equation (13) is the requested
frozen-`q` Frechet tangent.  It is exact in real arithmetic and has finite
coefficient-jitter variance for positive marginal variances; the delta pieces
are deterministic.  Price/Stein differentiation under Gaussian law is also
the framework used in [Mamis (2022)](https://arxiv.org/abs/2202.00189).

This establishes a tangent operator, not a viable second-order contest
allocation: M133's five extra `[2,1,1]` products and 29.232B edge-tangent
increment still statically exceed the envelope.

## 6. Conservative fixed-cost worksheet

M133 charged 80 `(32+48)` conditional-boundary nodes at 512 float64-equivalent
operations per node, including its 1.25 protection.  Retain that *same* highly
conservative scalar charge per M141 cell even though a cell needs only three
univariate expressions from (2).  This avoids claiming an untraced special-
function discount.

For `K=512` selected triples/layer, M133's exact coefficient reserve was
`1.6252928B`.  Replacing 80 nodes by nine cells gives

```text
node reserve:       1.6252928 * 9/80 = 0.18284544B.
local 3x3 factor, jitter, scalar and bivariate-delta reserve: 0.25000000B.
M141 coefficient engine ceiling:                         0.43284544B.

M133 common K=512 work excluding coefficient engine:    93.31564744B.
M141 protected complete K=512 worksheet:                93.74849288B.
```

The `0.25B` is deliberately a reserve, not a measured bill.  The result is
below both the requested `5B` incremental ceiling and `100B` complete ceiling,
with `6.252B` arithmetic headroom before a native residual-time trace.  It is
therefore a well-defined candidate *component* for a `K=512` successor.

It cannot honestly rescue M133's `K=768` allocation.  There the M133 total
excluding its coefficient engine is `99.81681864B`; even an unrealistically
free M141 engine leaves too little protected margin.  With the above reserve it
is `100.24966408B`.  So the proposed repair is not a disguised parameter
change to the killed M133 allocation.

## 7. Falsification of the other apparent escapes

### Unbounded Rhee--Glynn / Borel / conformal tails -- killed for this envelope

If an exact deterministic quadrature limit is written as
`T_0 + sum_l Delta_l`, a Russian-roulette estimator needs positive survival
probability at every level carrying a nonzero remainder.  Since level cost
grows with resolution, it has positive probability of exceeding any fixed
finite cost.  No deterministic per-MLP bill cap exists.  Capping the level
introduces truncation bias unless a separately exact closed remainder is
provided--which returns to the unresolved trivariate primitive.

Rhee--Glynn correctly gives finite-variance/finite-expected-cost conditions
for suitable strong convergence, but those are expected-cost statements, not a
hard worst-case contest budget guarantee:
[Rhee--Glynn (2012)](https://arxiv.org/abs/1207.2452),
[Cui--Fu--Peng--Zhu (2018)](https://arxiv.org/abs/1804.04215).

### Partial-correlation telescoping -- preserved algebra, killed as an escape

For a bivariate conditional block, Price gives

```text
B(r)-B(0) = s_j s_k integral_0^r P_r(X_j>0,X_k>0) dr.    (14)
```

The integrand is bounded, so (14) is numerically harmless.  But the base term
is still a one-factor integral and the new path variable adds a dimension.
More importantly, M131 proves the `G_iijk Q3` coefficient is generically
nonzero after all tree/Wick subtractions.  Equation (14) reparametrizes that
term; it cannot turn it into a finite collection of univariate/bivariate
constants.  Preserve it as a diagnostic identity only.

### Global factor compression -- already killed, not reopened

The local rank-two identity has no implication that a full layer is low rank.
M135's dimension and density-ratio `L2` gates remain binding for a global
source.  Treating the local construction as evidence for a global factor law
would be precisely the invalid inference M135 was built to catch.

## 8. Recursive disposition and next gate

### Preserved

* exact local `lambda I + UU^T`, `r<=2` conditioning;
* fixed-count, unbiased `3 x 3` jittered factor cubature;
* the `H^1` finite-variance certificate, including the `.975`/singular primal
  boundary;
* Price-form frozen-proposal tangent with deterministic delta
  Rao--Blackwellization;
* explicit HT coefficient-noise accounting; and
* the protected `K=512` static worksheet.

### Killed in this generation

* using infinite Russian roulette in a hard-cliff budget;
* claiming a partial-correlation path removes the trivariate orthant term;
* using M141 to make M133 `K=768` fit;
* claiming an efficacy or leaderboard improvement without the predeclared G1/G2
  screen and a native accounting trace.

### Single lawful child

Only if an independently changed triple-allocation mechanism clears its own
generated output-level variance gate at `K=512`, test this coefficient engine
against M131's exact conditional oracle on matched generated states, then run
the complete M133/M125b influence harness with G1/G2.  Keep the factor cell
count, reserve, proposal, source populations, and holdout firewall frozen.
Do not combine it with another unvalidated variance mutation and call the
result a win.

