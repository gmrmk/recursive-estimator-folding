# M243 preimplementation erratum

Date: 2026-08-09

This file was written after three read-only preimplementation audits and
before any M243 test, module, runner, result, or evidence-generating command.
It preserves the original predeclaration and manifest byte-for-byte.  Where
this erratum conflicts with either, this erratum and the V2 manifest govern.

## E1. Inherited invariants

The official objective is

```text
S = MSE * max(0.1,C/B)
B = 2.72e11
C = billed FlopScope FLOPs + 1e11 * residual seconds.
```

The total candidate ceiling is 100B.  The currently unallocated strict
no-replacement composition headroom `1.986871472B` is a warning, not a G0
allowance.  No M243 component receives sharing, replacement, or score credit.

The exact frozen v3.1 GUARDS tar SHA-256 is
`8382e269c9b32e0935492734ddf8182560120f7e9331621aa18839d5d1f4ea06`.
M243 does not modify or read its outputs.

The frozen G0 interpreter is

```text
C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe
Python 3.14.4
NumPy 2.4.6
mpmath 1.3.0
WhestBench 0.14.0
FlopScope 0.10.0+np2.4.6
```

Any dependency or version mismatch fails closed.  Installation during the
experiment is forbidden.

## E2. Bias classes and the lifted centered function

Freeze two different claims:

```text
mathematical_identity_bias_class =
  exact-unbiased for exact b and every deterministic c in real arithmetic

runtime_m178_bias_class =
  deterministic certified numerical approximation, not literally unbiased
```

Let `L(x)=x Phi(x)+phi(x)`, `la=L(a)`, and `lb=L(b)`.  Define

```text
Raw(x,y;rho) = (xy+rho)Phi2(x,y;rho)
               + y d_xPhi2 + x d_yPhi2
               + (1-rho^2)d_rhoPhi2

Htilde(s,t) = Raw(a+s,b+t;rho)
              - la L(b+t) - lb L(a+s) + la lb.
```

Every `Ha`, `Hab`, ..., `Hbbbb` in the original predeclaration means the
corresponding partial derivative of `Htilde` at `(s,t)=(0,0)`.  This fixed-base
center convention is binding and makes `Hab=P`.  Ordinary differentiation of
the abbreviated baseline scalar `Raw(a,b)-la*lb` is not the intended object.

The exact beta values are the ordinary L2 Hermite projection of `b`.  They are
not claimed to minimize the variance of the `r`-weighted antithetic event.
Their variance efficiency is an empirical G0B premise.

## E3. Exact G0A census and invariance actions

Both generated events are evaluated at every generated width, including
width 3.  They are not duplicates.  The exact eight-event census is

```text
A0: (0,1,2)
A1: (0,1,2)
w3: (0,1,2), (2,0,1)
w5: (0,1,2), (4,0,1)
w7: (0,1,2), (6,0,1).
```

For a width `n`, freeze the nonidentity cyclic permutation
`perm[a]=(a+1) mod n` with action

```text
mu_prime[perm[a]] = mu[a]
C_prime[perm[a],perm[b]] = C[a,b]
event_prime = (perm[i],perm[j],perm[k]).
```

Freeze the positive gauge

```text
lambda[a] = 2^(((a mod 5)-2)/4)
mu_prime = lambda * mu
C_prime = outer(lambda,lambda) * C.
```

For `s=lambda_i^2 lambda_j lambda_k`, compare every tail-node `b`, `r`, beta,
`R`, and folded `Z` at the transformed cell against its expected physical
degree.  The binding defect is

```text
abs(lhs-s*rhs)/(1+abs(s*rhs)).
```

The beta object alone scales `lambda_j lambda_k`; the R object alone scales
`lambda_i^2`; `b` and `r` use those respective degrees; `Z` uses `s`.  Apply
the same frozen tail-g list from the original predeclaration.  Singleton swap
is the exact map `(i,j,k)->(i,k,j)`.

## E4. Independent oracle and numerical enclosures

The high-precision oracle may not import M243 formulas.  It constructs

```text
Phi2(a,b,rho) = Phi(a)Phi(b)
                + integral_0^rho phi2(a,b;t) dt,
A = phi(a) Phi((b-rho a)/sqrt((1-rho)(1+rho))),
B = phi(b) Phi((a-rho b)/sqrt((1-rho)(1+rho))),
D = phi2(a,b;rho),
```

then uses the standard positive-part formula for `E[Y_jY_k]`, exact unary
positive-part means, and Gaussian conditioning to build centered `b(g)`.

For the rho integral, split `[0,rho]` into 16 equal directed panels.  For the
outer integral, use `[-inf,-16,-10,-8,-5,-2.5,-1,-.25,0,.25,1,2.5,5,8,10,16,
+inf]` plus the repeated kink `-alpha_i`, sorted and deduplicated.  Use
mpmath tanh-sinh quadrature with `maxdegree=12` on every panel at both 80 and
100 digits.  Any exception, cap hit, or 80/100 disagreement fails; there is no
retry with a different partition or precision.

G0A has one process launch, a 2700-second wall cap, and a 2048-MiB peak-RSS
cap.  Partial completion is failure.

Two numerical paths are tested separately:

1. the analytic derivative formulas using independent high-precision
   `P,A,B,D`;
2. the actual M178-backed beta using `M178Result` values and
   `w_value,w_da,w_db,w_drho`.

Because each beta is affine in the four M178 jet components, propagate its
radius by the absolute linear coefficient sum, add
`64*eps*(1+abs(center))`, and expand both endpoints with `math.nextafter`
toward infinity.  The independent reference must lie inside every resulting
interval.  The actual conditional `b(g)` similarly propagates the M178 value
radius through its positive-part scale and then through `r(g)`.  An
"enclosure miss" means the independent value lies outside this explicitly
constructed interval.

## E5. Atom and tree safety

Candidate code must construct the centered conditional pair `b(g)` first.
It is forbidden to use M213/M216 `OwnerEvent.value`, `plus.value`, or
`minus.value` as `b`, because those values already contain Wick and tree
subtractions.

For G0A and G0B, bind the exact target coefficient/tree reference to
M147 `conditional_collision211_endpoint_dot` and its M122/M126 tree
convention.  M243 then multiplies `r*b` and subtracts `ViiVjk`, `2VijVik`,
and `Tree` exactly once.

## E6. G0B state, proposal, feature, and duplicate handling

For `S=raw raw^T`, define

```text
d = sqrt(diag(S))
Rbase = S / outer(d,d)
R = (1-mix)I + mix Rbase
```

followed by exact symmetrization and diagonal overwrite to one.  `corrcoef`
semantics are forbidden.

At width 12, use M147 `build_endpoint_state_frechet` with zero tangents as the
bound generated-reference bridge constructor.  M213 `build_local_state` is
forbidden because it rejects width 12.  Bind

```text
q_e = collision211_factored_proposal(
        state.bridge,W,uniform_mixture=.05).probability(i,j,k)
F_e = source_feature_211(W,i,j,k)
f_e = concatenate(F_e.aaaa.ravel(), F_e.aaab.ravel(), F_e.aabb.ravel())
||f_e||^2 = sum of squares over all three slots.
```

The 128 proposal draws per cell are paired statistical units.  Duplicate
ordered events are evaluated once in an oracle cache keyed by `(cell,i,j,k)`
and mapped back to every sampled occurrence.  Report unique and total counts.
This cache earns no production-cost or native-sharing credit.  The
unconditional M178 jet is cached once per unique `(cell,j,k)` and its reverse
orientation uses the same certified receipt.

## E7. Exact G0B estimator and bootstrap definitions

For each sampled event `t`, set

```text
x_t = Delta_e f_e/(2q_e)
w_t = ||f_e/(2q_e)||^2
mu_Q(e) = direct integral E_G[Z_Q(G)]
n_Q(e) = direct integral E_G[(Z_Q(G)-mu_Q(e))^2]
h_Q(e) = w_t n_Q(e)
bias_Q(e) = mu_Q(e)-Delta_e.
```

The centered variance integral is evaluated directly.  Computing
`E[Z^2]-E[Z]^2`, clipping a negative result, or replacing the actual mean by
Delta is forbidden.

For one cell with `K=128`, define

```text
Nhat_Q = mean_t h_Q(e_t)
Vhat_Delta = sum_t ||x_t-xbar||^2/(K-1).
```

Pooled numerators and denominators are equal-weight averages of the two
cellwise values.  Concatenating vectors across cells and including
between-cell mean variance is forbidden.

Use `Generator(Philox(2430002))` for exactly 20,000 bootstrap replicates.
Within each replicate, resample 128 paired event indices with replacement
inside each cell, independently between cells; recompute each cell ratio and
the equal-cell pooled ratio.  The one-sided upper 90 bound is
`np.quantile(ratios,.90,method='linear')`.  A zero, negative, or nonfinite
denominator fails closed.  The empirical p99 is
`np.quantile(h_Q,.99,method='linear')`; the frozen p99 ratio is Q4 over ANTI.
All original ratio and p99 gates apply separately to P0, P1, and pooled.

The actual M178-backed path, not the ideal beta path, is binding G0B evidence.
The ideal path is an oracle comparator only.  For every sampled event require

```text
abs(bias_Q4(e)) <= 2e-7*(1+abs(Delta_e))
```

and require, per cell and pooled,

```text
|| mean_t [bias_Q4(e_t) f_e/(2q_e)] ||^2 / Vhat_Delta <= 1e-8.
```

The integrated M178 enclosure must contain the ideal mean.  The ideal path
must satisfy the original `5e-8*(1+abs(reference))` expectation gate.

G0B has one process launch, a 14,400-second wall cap, and a 2048-MiB peak-RSS
cap.  A timeout, cap hit, exception, missing event, or partial artifact is a
frozen failure; no rerun is authorized.

## E8. Comparator definitions and accounting

Let `Zraw(g)=r(g)b(g)-ViiVjk-2VijVik-Tree`.

```text
RAW1   = Zraw(G)
RAW2   = .5[Zraw(G1)+Zraw(G2)], G1,G2 independent
ANTI   = .5[Zraw(G)+Zraw(-G)]
Q2     = the universal add-back formula with beta0..beta2 at +/-G
Q4     = the universal add-back formula with beta0..beta4 at +/-G
STRAT2 = .5[Zraw(Phi^-1(U1/2)) + Zraw(Phi^-1(.5+U2/2))],
         U1,U2 independent Uniform(0,1)
GH2    = .5[Zraw(-1)+Zraw(+1)]
EXACT  = the adaptive high-precision outer integral.
```

RAW2, ANTI, Q2, Q4, STRAT2, and GH2 each use two conditional pair
evaluations.  Q2/Q4 additionally use an unconditional M178 jet and algebra;
that work, call count, wall, and RSS are reported separately.  `GH2` is a
biased deterministic diagnostic.  `STRAT2` is the honest randomized
equal-two-call comparator.  No comparator earns cost-normalized, native, or
promotion credit in G0B.

## E9. Strengthened M196 firewall and stop rule

G0B must not construct, import, or read `B1CanonicalState`, `dtilde`, `H`,
`V_H`, or any of M196's frozen 24 cells/seeds.  Generated `V_Delta` is allowed
only as a scale for coefficient-provider noise.  The later identity
`V_total=V_H+N_Q4` remains sealed behind all four M196 prerequisites and a
new predeclaration.

Any repair changes the authority hashes and requires a fresh no-code audit.
After the authority hash receipt is committed, no cell, statistic, tolerance,
comparator, resource cap, or estimator definition may change.  G0A failure
closes G0B.  G0B failure closes atlas/native work.  Partial completion is a
failure, not partial evidence.

