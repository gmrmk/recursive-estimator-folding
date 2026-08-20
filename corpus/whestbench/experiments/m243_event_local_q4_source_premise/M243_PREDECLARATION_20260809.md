# M243 predeclaration -- event-local Q=4 outer-Hermite source premise

Date: 2026-08-09

Status at creation: `PREDECLARED_G0_ONLY`; no M243 code, test, result,
native trace, response, truth, scorer, challenge-weight, leaderboard, or
submission run existed when this file and its manifest were written.

## 1. One changed mechanism

For one ordered-distinct `[2,1,1]` owner `e=(i,j,k)`, where `i` is repeated,
M243 keeps the exact M216 antithetic outer-normal draw and subtracts a degree-4
probabilists-Hermite polynomial from the conditional singleton-pair function.
It adds the polynomial expectation back analytically.

M243 does not change M133 `q0`, `uniform_mixture=0.05`, M151's mandatory
singleton owner `1/2`, `K=128`, M151 `dtilde`, `F_e`, the M125b carrier,
collision ownership, the four-distinct wedge, or the M122/M126 tree convention.

The candidate is a conditional control variate, not a new information source.
It can lower outer-draw noise only.  It cannot lower the proposal/control floor.

## 2. Firewall and present boundary

All evidence in this experiment is generated-only.  The following are
forbidden: challenge networks or weights, public or private truth, scorer,
leaderboard, champion outputs, response measurements, submissions, clipping,
retry-until-chart, truncation, silent zero fallback, or uncharged work.

The frozen Kerdock v3.1 deployment lane is not modified.

M196's provider-before-variance firewall remains binding.  The composed M151
quantity `(V_H+N4)/V_Delta` may not be run until all four M196 prerequisites
exist and pass:

1. a real 49-node `build_b1_state`;
2. a non-cubic B1 source compiler;
3. a bound exact coefficient provider;
4. an inclusive native trace.

M243 G0 may test formula correctness and provider-only outer noise.  It must
not create a substitute B1 state, call its noise `V_H`, or claim the M196 gate.

## 3. Frozen notation

Let `G=(X_i-mu_i)/sigma_i ~ N(0,1)`, `Y_a=relu(X_a)`, and let `m_a=E[Y_a]`.
For strict `e=(i,j,k)`, define

```text
r(g) = (relu(mu_i + sigma_i g) - m_i)^2,
b(g) = E[(Y_j-m_j)(Y_k-m_k) | G=g].
```

The centers `m_j,m_k`, all covariance data, the tree, `q0`, and `F_e` are
stop-gradient constants.  Only the Cameron-Martin shift of `G` is
differentiated.

Use probabilists' Hermites:

```text
He0 = 1
He1 = g
He2 = g^2 - 1
He3 = g^3 - 3g
He4 = g^4 - 6g^2 + 3
```

## 4. Proposed one-jet coefficients

For the unconditional singleton pair `(j,k)`, set

```text
sj = sqrt(C_jj), sk = sqrt(C_kk)
a = mu_j/sj, b = mu_k/sk
rho = C_jk/(sj sk)
delta = (1-rho)(1+rho)
p = C_ij/(sigma_i sj)
q = C_ik/(sigma_i sk)
```

One M178 call at `(a,b,rho)` returns

```text
P = Phi2(a,b;rho), A = d_a P, B = d_b P, D = d_rho P.
```

Define the fixed centers

```text
la = a Phi(a) + phi(a) = m_j/sj
lb = b Phi(b) + phi(b) = m_k/sk.
```

The proposed dimensionless centered-pair jet is

```text
H    = (a b + rho)P + b A + a B + delta D - la lb
Ha   = b P + rho A + B - lb Phi(a)
Hb   = a P + A + rho B - la Phi(b)
Haa  = (b-rho a)A + delta D - lb phi(a)
Hab  = P
Hbb  = (a-rho b)B + delta D - la phi(b)

Haaa = -(rho + a(b-rho a))A - a delta D + a lb phi(a)
Haab = A
Habb = B
Hbbb = -(rho + b(a-rho b))B - b delta D + b la phi(b)

Haaaa = (a^2(b-rho a)-b+3 rho a)A
        + (delta a^2 + 2 rho^2 - 1)D
        + (1-a^2)lb phi(a)
Haaab  = -a A - rho D
Haabb  = D
Habbb  = -b B - rho D
Hbbbb = (b^2(a-rho b)-a+3 rho b)B
        + (delta b^2 + 2 rho^2 - 1)D
        + (1-b^2)la phi(b).
```

Directional derivatives are

```text
C0 = H
C1 = p Ha + q Hb
C2 = p^2 Haa + 2 p q Hab + q^2 Hbb
C3 = p^3 Haaa + 3 p^2 q Haab + 3 p q^2 Habb + q^3 Hbbb
C4 = p^4 Haaaa + 4 p^3 q Haaab + 6 p^2 q^2 Haabb
     + 4 p q^3 Habbb + q^4 Hbbbb.
```

The proposed physical Hermite coefficients are

```text
beta_r = sj sk C_r / r!,  r=0,...,4.
```

These formulas are hypotheses until G0 passes.  M178's jet is authoritative;
this Q4 reduction is not.

## 5. Proposed repeated-node add-backs

Let `alpha=mu_i/sigma_i`, `pi=Phi(alpha)`, `h=phi(alpha)`, and
`m=sigma_i(alpha pi+h)`.  Freeze

```text
R0 = sigma_i^2 ((alpha^2+1)pi + alpha h) - m^2
R1 = 2 sigma_i m (1-pi)
R2 = 2 sigma_i^2 pi - 2 sigma_i m h
R3 = 2 sigma_i^2 h + 2 sigma_i m alpha h
R4 = -2 sigma_i^2 alpha h - 2 sigma_i m (alpha^2-1)h.
```

The claim is `R_r=E[r(G)He_r(G)]`.  These formulas also remain hypotheses
until G0.

## 6. Bias-safe folded event

For any deterministic state-dependent coefficients `c_0,...,c_Q`, independent
of the current outer draw, define

```text
pc(g) = sum_{r=0}^Q c_r He_r(g)
Z_Q(g) = 0.5 * sum_{s in {+1,-1}} r(sg)[b(sg)-pc(sg)]
         + sum_{r=0}^Q c_r R_r
         - V_ii V_jk - 2 V_ij V_ik - Tree_iijk.
```

Because every `r He_r-R_r` has mean zero,

```text
E_G[Z_Q(G)] = Delta_ijk
```

for every deterministic `c`, not merely the optimal coefficients.  This is
the bias contract used in code.  M243 chooses `c_r=beta_r`.  Exact beta values
are therefore a variance-optimality claim, not an honesty precondition.

The algebraically shorter `(r-R0)(b-Pi_Q b)` form is forbidden in candidate
code unless exact mean-zero residual parity has already been certified.  The
universal add-back form above is the source of truth.

## 7. Ownership

M243 accepts only pairwise-distinct `(i,j,k)`, is symmetric under `j<->k`, and
emits no numeric value on `[4]`, `[3,1]`, `[2,2]`, or `[1,1,1,1]` strata.
Those requests must return a typed refusal.

For later composition only,

```text
X4(e,g) = [Z_4(e,g)-dtilde_e] F_e / [2 q0(e)].
```

The factor `1/2` occurs exactly once.  `F_e` is the complete M151 three-slot
`aaaa/aaab/aabb` feature, flattened with all three slots present.  M133's
two-slot norm shortcut is not the M243 norm.

`beta0 R0=V_jk V_ii` cancels the first Wick term exactly when beta is exact,
but candidate code must not add or subtract that term twice.  `-2V_ijV_ik`
and `-Tree` each occur exactly once.

## 8. G0A formula gate -- frozen before code

Use five Gaussian cells.

```text
A0:
  mu = (-0.4, 0.1, 0.7)
  C = I_3
  event = (0,1,2)

A1:
  mu = (-0.2, 0.45, -0.35)
  scale = (0.7,1.3,1.8)
  correlation = [[1,.75,-.55],[.75,1,-.10],[-.55,-.10,1]]
  C = diag(scale) correlation diag(scale)
  event = (0,1,2)
```

Three generated cells use `(width, Philox seed)`

```text
(3,243700003), (5,243700005), (7,243700007).
```

Their generator is exactly

```text
rng = Generator(Philox(seed))
A = rng.normal(0,.12,size=(width,3))
d = rng.uniform(.65,1.35,size=width)
C = A A^T + diag(d), symmetrized exactly
mu = rng.uniform(-.6,.6,size=width).
```

Events are `(0,1,2)` and `(width-1,0,1)`; duplicate width-3 events are
evaluated once.

The independent reference uses mpmath at 80 and 100 digits, adaptive outer
integration split at `g=-alpha_i`, and an independently assembled conditional
bivariate positive-part formula.  It may not import M243 beta or R formulas.
The two precisions must agree within `2e-12*(1+abs(reference))`.

G0A passes only if all of the following hold:

1. every proposed `R0,...,R4` agrees with direct integration within
   `2e-10*(1+abs(reference))`;
2. every proposed `beta0,...,beta4` agrees with direct
   `E[b He_r]/r!` within the same limit;
3. adaptive expectations of raw antithetic, Q2, and Q4 agree with the
   independent Delta reference within `5e-8*(1+abs(reference))`;
4. singleton swap, co-permutation, and positive diagonal gauge pass with
   maximum scaled defect `2e-10`; the physical degree is `lambda_i^2
   lambda_j lambda_k`;
5. values are finite at `g=0,+/-2^-8,+/-.25,+/-1,+/-2.5,+/-5,+/-8,+/-10,
   +/-16` on every frozen event;
6. source half ownership, collision refusal, and the tree convention match
   M151/M147 exactly;
7. any oracle disagreement, nonfinite value, undeclared refusal, enclosure
   miss, normalization error, or owner mismatch kills the exact-Q4 formulas.

G0A is a formula/component gate.  It grants no total-support, native-cost,
source-variance, response, or score credit.

## 9. G0B provider-only outer-noise gate

G0B may run only after G0A passes.  It still contains no B1 state and is not
the M196 variance gate.

Use two fresh width-12 cells:

```text
cell P0: seed=24312001, correlation_mix=.20
cell P1: seed=24312002, correlation_mix=.52
```

For each cell:

```text
rng = Generator(Philox(seed))
raw = rng.normal(size=(12,12)); R0 = corr(raw raw^T)
R = (1-mix)I + mix R0, exactly symmetrized with diagonal 1
scale = exp(rng.uniform(-.35,.35,size=12))
C = diag(scale) R diag(scale), exactly symmetrized
mu = rng.normal(0,.30,size=12)
W = rng.normal(0,1/sqrt(13),size=(12,13)).
```

Build the exact post-ReLU bridge, M133 `q0` with `uniform_mixture=.05`, and
M151 full three-slot `F_e`.  Draw exactly 128 ordered-distinct events with
replacement from `q0` using `Generator(Philox(seed+100000000))`.  Use the
adaptive 80/100-digit outer oracle for each selected event.

Report separately

```text
N_ANTI = E_q [ ||F_e/(2q_e)||^2 Var_G(Z_ANTI | e) ]
N_Q2   = E_q [ ||F_e/(2q_e)||^2 Var_G(Z_Q2   | e) ]
N_Q4   = E_q [ ||F_e/(2q_e)||^2 Var_G(Z_Q4   | e) ]
V_Delta = Var_q [ Delta_e F_e/(2q_e) ].
```

This is a sampled generated provider premise, not M151 residual efficacy.
Use 20,000 paired bootstrap resamples with seed `2430002`.

G0B passes only if, in each cell and pooled:

```text
upper90(N_Q4/N_ANTI) < 0.50
upper90(N_Q4/V_Delta) < 0.20
p99(Q4 conditional-noise contribution) /
  p99(ANTI conditional-noise contribution) <= 1.25
```

and pooled `N_Q4<N_Q2<N_ANTI`.  Zero denominators, nonfinite values, a
positive-support miss, or an oracle refusal fail closed.  GH2 at nodes `+/-1`
is an equal-two-call deterministic diagnostic; its bias is reported and it
cannot be promoted as an unbiased estimator.  RAW1, RAW2, ANTI, Q2, Q4, GH2,
and exact outer integration share cells and are all reported.

Failure kills this exact Q4 coefficient/provider premise only.  It preserves
the universal arbitrary-coefficient zero-mean-control identity and permits a
separately predeclared shrunk, kink-adapted, or residual-quadrature mutation.

## 10. Gates that remain closed after G0

Even a complete G0 pass does not authorize implementation of a submission
provider.  A later total provider must cover

```text
{e : q0(e)>0} x all finite real g
```

with zero positive-measure refusal.  M224/M226 alone are not total because
their bounded alpha/rho/scale/repeated-coordinate chart excludes Gaussian
tail mass.  A lawful totalizer needs central, generic, saturated-tail,
zero-variance, and rank-boundary charts, with joint antithetic enclosures.

The current strict no-replacement composed headroom is `1.986871472B` before
all unpriced provider/adapter/terminal/runtime terms.  M214's alternate
`6.824272176B` allowance is unavailable without its separate caller-removal
proof.  No reuse credit is granted for the M179/M178 jet until one exact live
object/call/lifetime trace proves it.

Only after the total provider and every M196 prerequisite pass may a new
sealed interaction runner evaluate

```text
upper90((V_H+N_Q4)/V_Delta) < .25,
p99(X4^2)/p99(X_Delta^2) <= 1.25,
and nonpositive width slope at widths 12,16,24.
```

That interaction requires disjoint development, validation, and untouched
holdout manifests.  It is not part of M243 G0.

## 11. Execution order and stop rules

1. Hash this predeclaration and manifest.
2. Obtain an independent preimplementation audit.
3. Create the test before the module and preserve the missing-module RED.
4. Implement G0A only; execute its frozen methods once.
5. If G0A fails, stop.  Do not retune formulas, cells, tolerances, or charts.
6. If G0A passes, authorize the independently implemented long G0B oracle.
7. If G0B fails, stop.  Do not open native or total-support work.
8. If G0B passes, predeclare the total atlas as a new child before code.

No ledger, graph, champion, or deployment status changes are earned by a G0
pass.  Every failure remains useful local evidence and is folded into the
next separately predeclared mutation.

