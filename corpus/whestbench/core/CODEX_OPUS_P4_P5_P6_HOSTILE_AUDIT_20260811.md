# Hostile audit of Opus P4, P5, and P6

Status: **static mathematical audit; REPAIR required before theorem-level
closure credit**.  No estimator, fixture, cache, scorer, or scientific runner
was executed.  This document grants no execution or submission authority.

Snapshot audited:

- commit `5539e536`;
- `P4_UNIFORM_WEIGHT_OPTIMALITY_20260811.md`, SHA-256
  `C1F3B28C8C121BD5C71B3DA5DB3AAB9F8F4A0057498E17D56FAC53FA8D1C06B3`;
- `P5_DIVERGENCE_FORM_DICHOTOMY_20260811.md`, SHA-256
  `4E8F40F102295EAFEE515F08EFB0E03649E055C4772FDD8F37F013407988D916`;
- `P6_CONSTRAINED_GLS_CROSS_BLOCK_20260811.md`, SHA-256
  `5D7901CCE471D7D95C09B7126BD969C356F005CDE470E09AD975B4A1948BCEB5`.

The papers contain useful mathematics.  This audit separates that tissue from
claims that do not follow.  A paper is not credited as a class closure merely
because its intended conclusion is plausible.

## 1. Outcome first

| paper | verdict | theorem tissue that survives | material repair |
|---|---|---|---|
| P4 | **REPAIR** | PSD plus constant row sums proves that uniform weights are a global minimiser of every fixed-degree zonal quadratic | strictness and uniqueness are false already at degree 2; the doubled-set minimiser dimension is correspondingly wrong |
| P5 | **REPAIR** | the CPWL second distributional derivative is interior-zero and kink-supported; Euler radial conditioning and the spherical jump identity are useful | the admissible regularity does not imply BV, the rigidity lemma drops allowed radial/tangential-gradient terms, the sphere measure has the wrong dimension, and representation does not imply an algorithmic localization or variance lower bound |
| P6 | **REPAIR** | the constrained quadratic splits exactly into `(A,b)` and the positively-ridged solution is correct | one kernel statement contradicts the proof, alternate anchors do not lie on one ray, numerical confirmation is quarantined, and no lawful `b` provider is supplied |

None of the three papers creates submission bytes.  None displaces Kerdock
v3.1 GUARDS.  Their corrected intersection does, however, sharpen the research
frontier:

1. zonal reweighting of the fixed 126-frame point set cannot improve its
   Haar-averaged error;
2. a general divergence-form class closure has **not** been proved;
3. truth-free frame GLS still lacks one non-identifiable cross block;
4. changing the coupling of two marginally valid designs remains outside all
   three results.

The repaired anti-J `M4b` coupling is therefore still the highest-upside open
premise, not a candidate.  Candidate-A exact-residual control remains the
other high-upside route, but its physical source provider and integrated cost
are missing.

## 2. P4: the minimiser proof survives; strictness does not

### 2.1 Correct core theorem

For the base design `X`, let

```text
K_l[i,j] = G_l(<x_i,x_j>),
u = 1/N * 1,
W = {w : 1^T w = 1}.
```

The addition theorem makes `K_l` positive semidefinite.  P4's equal-frame-sum
argument, if its committed aggregate census is transcribed correctly, proves
`K_l 1 = c_l 1`.  Consequently, for `w=u+delta`, `1^T delta=0`,

```text
Q_l(w) = Q_l(u) + delta^T K_l delta >= Q_l(u).
```

This is enough to prove **global, non-strict optimality** of uniform weights at
every degree.  It also proves optimality for any nonnegative zonal mixture of
degrees.  That is the durable P4 result.

### 2.2 Exact degree-2 counterexample to strictness

P4 lines 112--115 claim strictness at every even degree `l>=2`.  At `d=256`,
the normalized degree-2 zonal kernel is

```text
G_2(t) = (256 t^2 - 1) / 255.
```

Therefore

```text
a = G_2(0)    = -1/255,
b = G_2(1/16) = 0.
```

Substitution into P4's own shell formulas gives

```text
lambda_top  = 1 + 255a + 32000b = 0,
lambda_mid  = 1 + 255a - 256b   = 0,
lambda_bulk = 1 - a             = 256/255.
```

Take any nonzero `delta` which is constant `+q` on frame 1, constant `-q`
on frame 2, and zero elsewhere.  Then `1^T delta=0` and
`K_2 delta=0`.  Hence

```text
Q_2(u+delta) = Q_2(u) = 0,
```

contradicting strictness and uniqueness.  This is not numerical: each complete
orthonormal frame integrates degree 2 exactly.

Correct statement:

> Uniform is a minimiser at every degree.  It is unique on the base set for a
> particular zonal target exactly when the positive weighted sum of its
> degree kernels is positive definite on `1^perp`.  P4 proves this condition
> at degree 4 and reports it at degree 6; it does not prove it for every even
> degree.

P4's pointwise target statement must therefore exclude pure degree-2 targets
and any other target whose active kernels share a contrast nullspace.

### 2.3 Doubled-set dimension correction

At even degree, ordering `Y=(X,-X)` gives

```text
K_l^Y = J_2 tensor K_l^X.
```

The antipodally antisymmetric subspace contributes `N=32256` null directions.
At degree 2, `ker K_2^X` additionally contains all 126 frame-constant
directions.  After imposing the sum-zero perturbation constraint, 125 of
those symmetric directions remain.  Thus the feasible minimiser-affine
dimension at degree 2 is

```text
32256 + 125 = 32381,
```

not 32256.  P4's doubled-set dimension is valid only when `K_l^X` has no
additional nullspace on `1^perp`.

### 2.4 What P4 does and does not close

The corrected non-strict theorem still closes any claim that a fixed,
sum-one weight vector can improve a **zonal** Haar-averaged criterion on the
same 126 frames.  It does not close:

- point-set changes;
- coupled rotations or cross-design covariance;
- realized-network non-zonal criteria;
- weight/seed-side predictors;
- adaptive rules whose law requires a separate unbiasedness proof.

Its missing falsifier was equality: a vector with `Q_l(w)=Q_l(u)` can disprove
strictness without beating uniform.

## 3. P5: the proposed dichotomy is not proved as stated

### 3.1 D1 does not imply D3

P5 requires `Phi` to be continuous in `(s,p)` and locally Lipschitz only in
`x`.  Even inside one linear cell, a continuous non-BV function of the affine
scalar `s=f(x)` can make

```text
V_f(x) = Phi(x,f(x),grad f(x))
```

non-BV.  Therefore the decomposition asserted in D3 does not follow from D1.
The exclusion of `x=0` also needs an explicit no-atom/local-integrability
condition for every admitted measure.

Repair: require enough local Lipschitz/Sobolev regularity in all active slots
to make the BV chain rule valid, and state the origin condition separately.

### 3.2 The rigidity lemma constrains only the tangential output

Fix `x!=0`, put `W=x^perp`, and let `P_W` be its projector.  The normal-jump
condition tests only

```text
nu . [Phi(x,s,p+J nu) - Phi(x,s,p)],   nu in W.
```

It can constrain `P_W Phi`; it cannot constrain the component of `Phi`
parallel to `x`.  P5 correctly proves a skew-affine form for the tangential
component, then silently promotes it to a form for the full vector.

An exact missing family is

```text
Phi_a(x,s,p) = x * <a(x), P_W p> / |x|^2,   a(x) in W.
```

Across a conical facet, `[p]=J nu` and `nu.x=0`, so

```text
nu . [Phi_a] = J <a,nu> * nu.x / |x|^2 = 0.
```

It is K-deposit-free but is not P5's A-form because its radial output depends
on the tangential gradient.  Affineness also permits tangential terms
`q_s(x) s`, which are continuous across K and are likewise absent.

On the realizable manifold `x.p=s`, the general affine normal-blind form must
at least include

```text
P_W Phi = A(x) P_W p + q_0(x) + q_s(x) s,   A^T=-A on W,

<x_hat,Phi> = r_0(x) + r_s(x) s + <a(x),P_W p>.
```

This does not prove that such extra terms are useful.  They may still reduce
to point evaluations after a correct tangential integration by parts.  It
does prove that P5's `if and only if` form and its current L4 proof are
incomplete.  Derivatives of the moving projector `P_W(x)` must also be carried
in that repair.

P5 additionally states normal blindness for all `p`, while realizability at
fixed `(x,s)` supplies only gradients satisfying `x.p=s`.  The proof must stay
on that manifold or justify the extension.

### 3.3 The spherical singular measure has the wrong dimension

The Euclidean kink set is generically `(d-1)`-dimensional, but

```text
K cap S^{d-1}
```

is generically `(d-2)`-dimensional.  The spherical identity must use a measure
proportional to

```text
H^{d-2} restricted to K cap S^{d-1},
```

not `H^{d-1}` as written in P5's theorem and one-line avatar.

### 3.4 A representation is not an algorithmic lower bound

Showing that a distributional representation contains a K-supported term
does not prove that every algorithm must enumerate or explicitly locate K.
An analytic transform, coarea sampler, mollified identity, cancellation, or
another implicit representation may compute the same functional.  Such a
method still needs an honest cost and variance analysis, but it is not ruled
out by support alone.

Accordingly, the following P5 consequences are not derived:

- that a class-B variance factor "cannot be engineered away";
- that the theorem removes every hope of avoiding enumeration;
- any target-scale variance or FLOP lower bound.

The committed S9/M86/M202 evidence may empirically or subclass-wise kill
particular implementations.  P5 does not upgrade those results into a
universal algorithmic theorem.

### 3.5 Mean-chi arithmetic correction

The exact high-precision value quoted by the frozen literal is

```text
m_256 = 15.984382666608527477775...
```

The literal `15.98438266660852747` rounds to the corresponding binary64.  P5's
`lgamma` value `15.984382666607859` is about `6.68e-13` low in **absolute**
error and does not round to the same binary64.  The prose currently calls that
relative and same-rounding; both claims are false.  A stable gamma-ratio
evaluation is required.

### 3.6 Correct narrow disposition

P5 preserves three valuable facts:

1. the second distributional derivative of a CPWL function is kink-supported;
2. exact radial conditioning is the Rao--Blackwell optimum in its stated
   radial-weight class;
3. the spherical Laplacian splits into the interior Euler term and the
   correctly dimensioned kink measure.

It does **not** yet prove exhaustive collapse of every K-free affine rewrite,
and it cannot close general estimator classes.  Its omitted tangential family
does expose one exact first-order premise, but not a production candidate.

### 3.7 Exact first-order sphere control: narrow survivor, full design killed

For a fixed direction `v`, a bias-free degree-one homogeneous ReLU network
`f`, and `y(u)=m_d f(u)` on `S^{d-1}`, Gaussian Stein plus the independent
polar decomposition `X=R U` gives, componentwise,

```text
E_U[D y(U)[v]] = d E_U[(v.U) y(U)].
```

Hence

```text
C_v(u) = D y(u)[v] - d (v.u) y(u),
E_U[C_v(U)] = 0.
```

Equivalently, `C_v=div_S(y P_u v)`.  This is a first-order weak identity:
ReLU kinks are Haar-null and no omitted second-derivative facet mass is needed.
It is the rank-one linear member of the already disclosed Q3 multi-output
Stein-control-functional family, not an entirely new family.

Two immediate closures prevent wishful promotion:

1. after antipodal pairing only the odd part of `y` survives this control;
2. for a one-ReLU or first-layer-only reuse, that odd part is linear, so the
   paired control has only degrees 0 and 2 and every complete orthonormal frame
   integrates it exactly to zero.

On the incumbent complete-frame geometry, nonzero signal therefore requires
propagation through deeper gates.  A full 64,512-node JVP sweep is statically
over the current hard budget.  On the
committed worst-cost healthy v3.1 net, `C0=180,098,839,202`.  Even the most
optimistic current installed one-level product bill over the committed active
widths costs at least `85,094,178,120` for the 28 sampled middle layers; the
terminal live branches add `8,032,542,476`.  Their sum,
`93,126,720,596`, puts parent plus tangent at `273,225,559,798`, already
`1,225,559,798` above the hard `272B` budget before masks, additions,
coefficient fitting, control reduction, and residual-time charges.  A new
fusion may challenge that implementation-specific lower envelope only with a
separately frozen physical trace.

A conservative surviving current form is a fixed subset of complete frames,
which preserves the parent's geometry, with a weights-only `v` and a
coefficient fixed in advance or learned on an independent rotation.  The
zero-mean identity itself also permits other predeclared fixed node subsets;
they are separate point-set mutations and do not inherit the complete-frame
annihilation statement.  If incremental cost ratio is `r=DeltaC/C0`, a
necessary optimal-control break-even gate is

```text
R^2 > r/(1+r).
```

It earns no implementation or score credit until a static subset bill and an
independent coefficient topology are frozen.

## 4. P6: correct quadratic interface, no missing-information provider

### 4.1 Correct core algebra

With

```text
u = 1/sqrt(p) * 1,
P = I-u u^T,
C = alpha u u^T + u b^T + b u^T + A,
b = P C u,
A = P C P,
w = 1/p * 1 + v,  v in range(P),
```

the constrained objective is exactly

```text
J(v) = alpha/p + 2/sqrt(p) b^T v + v^T A v.
```

For `A` positive definite on `1^perp`,

```text
v* = -1/sqrt(p) A^{-1} b.
```

For a strictly positive projected ridge, the same formula holds with the
ridged metric.  This is the durable P6 theorem.  It proves that `b=0` returns
uniform weights under the positively-ridged solver.  It does not make `A`
irrelevant: `A` determines how a nonzero `b` is converted into weights.

### 4.2 Internal kernel contradiction

P6 lines 138--140 say that if `A` is singular and nonzero `b` lies in
`ker A`, uniform may still minimise.  That is false.  Along `v=-t b`,

```text
v^T A v = 0,
2/sqrt(p) b^T v = -2t ||b||^2/sqrt(p),
```

so `J(v)` is unbounded below.  P6 lines 211--216 state the correct result.

For `A` positive semidefinite on `1^perp`, the correct singular statement is:

- if `b=0`, uniform is a minimiser, but need not be unique;
- if `b` is in `range A`, pseudoinverse solutions exist;
- if `b` has a nonzero component in `ker A`, no minimiser exists;
- for a PSD **full block matrix** `C`, PSD compatibility itself forces
  `b` orthogonal to `ker A`.

### 4.3 Alternate anchors do not form one rescaled ray

For `a_j=c^T x_j`, `1^T c=1`, P6 derives

```text
b_c proportional to P S (1-pc).
```

As `c` varies, this can sweep `range(P S P)`; it is not generally a rescaling
of one vector.  Thus P6 does not statically kill every nonuniform linear
anchor.  What it proves is narrower: the uniform anchor is the unique linear
unbiased anchor that annihilates the cross block **identically for every
dataset**.

### 4.4 Exact truth non-identifiability from the observed frame matrix

The conclusion that `X` alone does not identify the truth cross block can be
proved without the incorrect ray claim.  Let `X` be `p x n`, let the unknown
truth vector be `mu`, and put

```text
E = X - 1 mu^T,
R = P X.
```

Then

```text
b(mu) = P (E E^T/n) u
      = R (X^T u - sqrt(p) mu) / n.
```

As `mu` varies, `b(mu)` spans an affine translate of `range(R)`.  Therefore
`X` alone cannot identify `b` without a structural model, weight-side
information, or an independent pilot.  This is the exact missing-provider
interface:

```text
A = P X X^T P / n           # observable
b_hat from external source  # missing
w = uniform - 1/sqrt(p) (A+ridge)^+ b_hat.
```

Trace-shrunk M192 additionally lets the common scalar affect the ridge scale;
a projected-ridge child avoids that dependency but still needs `b_hat`.

### 4.5 P6 does not kill the reflected two-arm coupling

For two arms with variances `v_A,v_B` and covariance `c`, the exact
sum-one variance-optimal constant weights, when
`D=v_A+v_B-2c>0`, are

```text
w_A = (v_B-c)/D,
w_B = (v_A-c)/D.
```

If `v_A=v_B`, equal weights are optimal for every `c`, while

```text
Var((Y_A+Y_B)/2) = (v_A+v_B+2c)/4
```

still falls when `c<0`.  P6 controls the weighting; it does not construct a
reflection or determine the covariance.  For the repaired anti-J `D_A/D_B`
arms, equal variances and equal biases remain unproved, so the equation is a
premise gate rather than score credit.

### 4.6 Evidence boundary

The static P6 algebra is admissible.  Its post-charter self-anchor numerical
run is quarantined by `CODEX_ANTI_J_PREMUTATION_LADDER_ERRATUM1_20260811.md`
E8 unless the owner prospectively admits it as common evidence or a fresh
authorized reproduction is performed.  The paper's empirical numbers cannot
carry a current promotion.

## 5. Combined frontier after repair

### 5.1 Closed or bounded

- Fixed-design, sum-one, zonal reweighting: closed by corrected P4
  non-strict optimality.
- Self-anchored sum-one GLS: algebraically returns uniform under the intended
  positive ridge; no gain.
- Truth-free GLS from `X` alone: `b` is non-identifiable without an added
  model or information source.
- Literal diagonal odd/even cumulant "anti-Jacobian": killed; it was not a
  Jacobian construction.
- Class-B kink estimators already tested: retain their empirical/subclass
  kills, but do not inflate P5 into a universal theorem.

### 5.2 Strongest surviving high-upside premise

The reflected two-arm coupling changes the **joint law** while preserving each
arm's Haar marginal.  It is not a fixed-design reweighting (P4), not a
divergence rewrite (P5), and it can reduce common-mode variance with equal
weights even when the GLS cross block is zero (P6).

The missing object must be written at equation level before a proposal is
sealed.  A defensible form is a cross-fitted, gauge-normalized forward
pullback.  For a frozen layer band `L`, let a predeclared weight-only diagonal
recurrence supply a common raw-coordinate reference `Sigma_l^0` and exact
whitener `W_l^0`; call this a gauge chart, not the true deep covariance:

```text
W_l^0 Sigma_l^0 (W_l^0)^T = I,
DeltaS_l^A = empirical_centered_covariance_A - Sigma_l^0,
E_l^A = W_l^0 DeltaS_l^A (W_l^0)^T.
```

The recurrence must transform by congruence under hidden permutations and
positive diagonal ReLU gauges.  Fail if any declared variance is nonpositive;
an `epsilon I` floor is forbidden because it breaks that covariance.  On
independent fold B, let `K_l^B(x)` be the raw **forward** input-to-layer
Jacobian and place it in the same chart:

```text
J_l^B(x) = W_l^0 K_l^B(x).
```

Form

```text
H_AtoB = sum_{l in L} omega_l E_{x in B}[
           J_l^B(x)^T E_l^A J_l^B(x)
         ],
H = sym((H_AtoB + H_BtoA)/2).
```

Define the reverse term analogously with `E_l^B` evaluated through fold-A
Jacobians.  Neither residual may use moments fitted on the opposite fold; any
non-weight-only reference needs an internal same-fold sub-split.  All pilot,
closure, probe, and whitening banks must be independent of the production Haar
rotation.

The operator need not materialize a dense Jacobian.  For each Lanczos vector
`q` and fold-B state, one forward JVP produces all
`t_l=K_l^B q`.  Set the stopped-gradient layer cotangent sources

```text
s_l = omega_l (W_l^0)^T E_l^A W_l^0 t_l.
```

One reverse sweep with all `s_l` injected returns the per-state summand
`sum_l (K_l^B)^T s_l = h_AtoB(x) q`; averaging these results over B returns
`H_AtoB q`.  Thus the carrier is
`O(S K_H L n^2)` work and streaming state, not the prior all-output
`O(n^4)` adjoint.  It becomes the old wall only if the state/probe counts scale
densely or the residual provider itself recreates an all-output covariance
adjoint.

For the full 32-layer band at `n=256`, one cross-direction action has the
static lower bill

```text
[2*32 + 32] * (2*256^2-256) = 12,558,336 operations per pilot state.
```

At `S=128` and four fixed Lanczos actions, both cross directions therefore
cost at least `12,859,736,064` operations after gates are cached, or
`13,931,380,736` after one forward gate pass per fold, before reference,
whitening, residual, Ritz, copying, and residual-time charges.  A narrower
layer band may survive; the full bill must be frozen before choosing it.  The
eigensolver also needs a fixed action cap, Ritz-residual tolerance, and eigengap
certificate.

This chart does not eliminate finite-sample self-deception.  With `S=128`
centered states in width 256, the empirical covariance has rank at most 127,
so `W Sigma_hat W^T-I` has at least 129 exact `-1` eigenvalues even under a
true diagonal null.  Merely observing negative eigenvalues is therefore a
guaranteed false discovery.  Promotion requires a frozen signal-above-null
operator-norm gate and negative-projector transfer across the two directions,
with a random rank-matched null.

Freeze `L`, `omega`, SPD policy, rank `r`, eigengap gate, and all pilot
substreams before observations.  Let `P_AJ` be the spectral projector onto
the `r` most negative eigenvalues of `H`, and

```text
R_AJ = I - 2 P_AJ.
```

This is finally an actual input-space residual operator.  It must pass:

- neuron permutation and positive-ReLU-gauge covariance;
- split stability and an eigengap lower bound;
- signal magnitude above the rank-deficient finite-sample null;
- exact projector/involution identities;
- a noncommuting left-action matrix-contract test;
- random rank-matched and `R=+/-I` controls;
- a static operation/memory bill before a forward;
- the three-arm attribution `W0 -> repaired R=I -> repaired R=R_AJ`;
- clustered whole-network covariance, then separate bias and adjusted-score
  gates.

This equation is a **proposal interface**, not evidence that negative
covariance exists.  A failed static bill kills anti-J without a network
forward.  Split stability requires separately authorized pilot JVP evidence
unless a matching immutable tangent cache exists; it may kill the premise
before any held-out estimator forward.

### 5.3 Secondary route

Candidate-A's exact-residual source architecture remains the only other route
with measured order-of-magnitude oracle upside.  Its next honest step is still
the physical collision provider plus one merged native trace.  P6's `b`
factorization may be tested only as a zero-marginal-cost byproduct after that
provider exists; it cannot justify building Candidate A.

## 6. Next lawful sequence

1. Opus issues append-only errata for P4/P5/P6 or explicitly accepts this
   audit's corrected scopes.  The parent papers stay immutable.
2. No ledger kill is upgraded from those papers until the errata pass an
   independent static audit.
3. Seal one exact anti-J proposal with the operator above, or kill it on its
   static bill before sealing.
4. Under the accepted challenge charter, Opus must seal a proposal too, or the
   owner must approve an append-only canonical-NULL amendment.
5. Both proposals are revealed and rebutted.  Reveals do not authorize
   execution.
6. A separate immutable authority may then permit only the no-forward matrix,
   symmetry, cache-census, and cost gates.
7. New network forwards require their own predeclaration, frozen tests,
   resource witness, and terminal receipt.

Until then, GUARDS remains the only integrated artifact and every new theorem
or premise receives zero contest credit.
