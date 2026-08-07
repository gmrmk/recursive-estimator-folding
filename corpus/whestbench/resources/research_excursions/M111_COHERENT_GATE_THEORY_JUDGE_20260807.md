# M111 independent theory judge: coherent binary-gate interferometer

**Date:** 2026-08-07  
**Scope:** theorem, invariance, numerical-risk, and frozen-gate design only.  
**Firewall:** no generated-network forward, contest instance, target, scorer,
submission archive, M110 source, or champion artifact was opened or changed by
this audit.  
**Disposition:** **PASS_TO_A_FROZEN_CONTROL-ONLY_PRECHECK**, after the formula
and implementation corrections below. This is not a measured survivor and is
not a winning-entry claim.

## 1. Verdict in one sentence

M111 is an exact-zero, antipodally even control which measures **connected
pairwise interference among first-layer binary ReLU gates**; it is genuinely
outside the additive one-axis spans tested by M107 and M110, but its normalized
square has no useful universal tail bound and its ungated depth-31 transport is
at serious risk of Oseledets/projective collapse. Those two premises must be
tested without a network forward before spending a single generated output.

The physics translation is ordinary and falsifiable:

```text
cymatic nodes          -> actual first-layer ReLU gate hyperplanes
coherent interference  -> centered products of two binary gate states
intensity              -> a normalized squared signed path sum
underlying harmonic    -> a broad even spherical spectrum, not one frequency
```

## 2. Corrected definition

Use the stated row-forward convention `x @ W1`, with

```text
W1: d x n,       W2,...,W_(L-1): n x n,       W_L: n x n_out.
```

Let `J={i: ||W1[:,i]||_2>0}`. Work only on this active set. Put

\[
 d_i=\|W_1[:,i]\|_2,\qquad D=\operatorname{diag}(d_i),\qquad
 A=W_1[:,J]D^{-1}.
\]

Thus the columns `a_i=A[:,i]`, not the rows, are unit gate normals. For
`u` uniform on `S^(d-1)`, define

\[
 v_i(u)=\mathbf 1\{a_i^T u>0\}-\tfrac12
       =\tfrac12\operatorname{sign}(a_i^Tu)\quad\text{a.e.}
\]

and

\[
 \Sigma_{ik}=\frac{\arcsin(a_i^Ta_k)}{2\pi}.
\]

Here `arcsin` is **entrywise**, not a matrix function. In particular,
`Sigma_ii=1/4`. The downstream signed linear-path transport is

\[
 T=D,W_2W_3\cdots W_L.
\]

For a nondegenerate output column `t_j=T[:,j]`, put

\[
 q_j(u)=v(u)^Tt_j,\qquad
 s_j=t_j^T\Sigma t_j,\qquad
 h_j(u)=\frac{q_j(u)^2}{s_j}-1.                 \tag{M111}
\]

The scale of `t_j` is immaterial. An implementation should replace every
nonzero column by `t_j/||t_j||_2` before computing `s_j`.

If `t_j=0`, or if a weights-only numerical guard declares `s_j` unresolved,
the only safe fallback is the identically zero control for that output. The
fallback retains exact mean zero but must be logged. A generated premise run
does not pass if any such fallback occurs. Silently flooring `s_j`, adding a
ridge to `Sigma`, or projecting `Sigma` to the PSD cone changes the analytic
mean and is forbidden.

## 3. Exact spherical mean

The sign vector depends only on direction, so it has the same orthant law for
a standard Gaussian input and for a uniform spherical input. The bivariate
Gaussian sign identity gives

\[
 E[\operatorname{sign}(a_i^TU)\operatorname{sign}(a_k^TU)]
   =\frac{2}{\pi}\arcsin(a_i^Ta_k).
\]

Consequently,

\[
 E[v_i(U)]=0,\qquad E[v_i(U)v_k(U)]=\Sigma_{ik},
\]

and `Sigma` is a covariance matrix, hence positive semidefinite. Therefore,

\[
 E[q_j(U)^2]=t_j^T\Sigma t_j=s_j,
 \qquad E[h_j(U)]=0                              \tag{1}
\]

for every fixed network with `s_j>0`. This is exact conditional on the
weights; it uses neither a large-`d` approximation nor an ensemble average.
The choice of strict `>0` on a gate boundary is irrelevant because every
nonzero gate hyperplane has spherical measure zero.

If a numerical denominator is `s_hat=s+delta`, the actual mean is

\[
 E[q^2/s_{hat}-1]=-\delta/s_{hat}.
\]

Thus denominator error is directly estimator bias after multiplication by a
fitted slope. A deployment audit needs an explicit relative error bound; a
finite result alone is not enough.

## 4. The stronger connected-pair identity

Because `v_i(u)^2=1/4=Sigma_ii` pointwise, all diagonal energy cancels. The
centered numerator is exactly

\[
 q_j(u)^2-s_j
 =2\sum_{i<k}t_{ij}t_{kj}
   \left[v_i(u)v_k(u)-\frac{\arcsin(a_i^Ta_k)}{2\pi}\right].       \tag{2}
\]

This is the real M111 mechanism. It is not a dressed-up gate count and it is
not a one-neuron feature: every surviving term joins two distinct ReLU gate
hyperplanes and retains the sign of their downstream path product.

Two sanity cases expose the boundary:

* If `t_j` is supported on one gate, `h_j` is identically zero. There is no
  one-gate binary "energy" because one centered binary gate has constant
  square.
* If two gates are identical or opposite, `Sigma` is singular. A transport
  in its nullspace has `q=0` a.e.; a transport on its one effective sign line
  again has constant square. Duplication creates no interference information.

Equation (2) proves non-equivalence to M107/M110 generically. M107 used sums
of single-axis Gegenbauer functions, and M110 uses sums of single-axis nodal
occupancies. Neither additive one-axis dictionary contains the cross products
`v_i v_k` for a generic nonorthogonal gate arrangement. M111 also changes the
specific failed link: nonnegative sign-invariant axis mixtures are replaced by
signed, output-routed pair interactions.

## 5. Parity and full symmetry audit

### Antipodes

`v(-u)=-v(u)` a.e., so `q_j(-u)=-q_j(u)` and

\[
 h_j(-u)=h_j(u).
\]

Antipodal evaluation therefore duplicates the M111 control value. It still
benefits the network estimator, but it supplies no second control observation.

### Input rotations

For a common orthogonal coordinate change `u'=Ru`, `W1'=R W1`, the norms are
unchanged, `A'=RA`, and `A'^T u'=A^Tu`. Thus `v`, `Sigma`, `T`, `s`, and `h`
are unchanged.

### Hidden permutations

A first-hidden permutation `P` gives `A'=AP`, `v'=P^Tv`,
`Sigma'=P^T Sigma P`, and `T'=P^T T`; all contractions are unchanged. A
permutation at any later hidden layer cancels between its two adjacent weight
matrices. An output permutation simply permutes the `h_j` coordinates.

### Every positive ReLU gauge

Let positive diagonal matrices `G_1,...,G_(L-1)` act by

\[
 W_1'=W_1G_1,
 \quad W_k'=G_{k-1}^{-1}W_kG_k\;(2\le k<L),
 \quad W_L'=G_{L-1}^{-1}W_L.
\]

This is the full hidden-neuron positive gauge. Then `D'=DG_1`, `A'=A`, and

\[
 T'=DG_1G_1^{-1}W_2G_2\cdots G_{L-1}G_{L-1}^{-1}W_L=T.
\]

Hence M111 is exactly gauge invariant at every hidden layer. The factor `D`
is essential; omitting it would repeat the gauge defect caught in the first
M109 draft.

If an output column is multiplied by a nonzero scalar, `q_j` scales once and
`s_j` twice, so `h_j` is unchanged. For a positive output rescaling the target
and the independently fitted control slope scale together, making the final
adjustment equivariant. A negative output-weight flip is not a symmetry of a
coordinatewise final ReLU, so no invariance claim is made for it.

## 6. Harmonic content: broad even interference, not a secret tone

Each hemisphere sign `v_i` has an infinite odd spherical-harmonic expansion.
The product `v_i v_k` is antipodally even and has degrees `0,2,4,...` extending
without a finite cutoff. Equation (2) removes the degree-zero mean. A complete
orthonormal frame removes the aggregate degree-two component, while the broad
even tail from degree four upward remains eligible to correlate with the
post-frame network error.

There is therefore an underlying harmonic **structure**, but not one hidden
eigenfrequency. It is the connected even spectrum generated by intersections
of actual gate hyperplanes. Calling this a single resonance would be false.

## 7. Normalization and tail theorem

M111 is finite for fixed nondegenerate weights, but normalization does not
make it safely bounded across networks. Since `|v_i|=1/2`,

\[
 q_j(u)^2\le B_j:=\frac{\|t_j\|_1^2}{4},\qquad
 \kappa_j:=B_j/s_j.
\]

Therefore

\[
 -1\le h_j(u)\le\kappa_j-1,
 \qquad
 \operatorname{Var}(h_j)
   =\frac{E[q_j^4]}{s_j^2}-1\le\kappa_j-1.        \tag{3}
\]

The variance bound uses `q^4 <= B_j q^2`. There is no useful universal bound
on `kappa_j`: nearly duplicate gates can make `Sigma` singular or nearly
singular in a transport direction. Under an approximate Gaussian law for
`q/sqrt(s)`, `h` resembles `chi^2_1-1`; its direction-level standardized
fourth moment is 15, already much heavier than a Gaussian. Frame averaging
may tame this, but it must be measured rather than asserted.

Required control-only diagnostics are therefore `min(s_j)`, all `kappa_j`,
direction and frame-block extrema, pooled block kurtosis, and the discrepancy
between two independent precision/association routes. Tail failure kills this
normalization, not the connected-pair identity in (2).

## 8. Stable deep transport

The literal left-to-right product `D W2 ... W_L` is a poor implementation.
Random depth-31 matrix products can grow, lose subdominant directions, and
become association-sensitive even while their final values remain finite.
M111 is column-scale invariant, so use that symmetry for stability.

For all outputs at once, initialize `R=W_L`. Normalize every nonzero column of
`R`. Then for `k=L-1,...,2`, replace `R <- W_k R` and normalize every nonzero
column again. Finally form `T=D R` and normalize its columns. Every intermediate
normalization is a positive scalar applied independently to an output column;
subsequent left multiplication does not mix columns. Thus the resulting
columns are exactly proportional to those of `D W2 ... W_L` in exact
arithmetic, and M111 is unchanged.

The frozen implementation should use float64 for this premise audit and
compare it with a separately associated or higher-precision reference. It
must also stress the full gauge with diagonal factors spanning at least
`[2^-4,2^4]`. No PSD projection of `Sigma` is allowed. Gram entries may be
clipped to `[-1,1]` only for a recorded roundoff excursion below a frozen
tolerance; the diagonal should be set to the exact value `1/4` after unit-norm
verification.

### Projective-collapse diagnostic

The ungated product may intrinsically align all output columns with one
Oseledets direction. Because M111 squares `q`, columns which differ only by a
sign give the same feature. Define

\[
 r_{jk}=\frac{t_j^T\Sigma t_k}{\sqrt{s_js_k}},\qquad
 R_{\rm line}=\frac{n_{out}^2}{\sum_{j,k}r_{jk}^4}.                \tag{4}
\]

`R_line=1` when all normalized transported random variables are the same up
to sign, and it reaches `n_out` for orthogonal lines in the `Sigma` metric.
This is the correct projective, sign-blind participation diagnostic. A value
near one localizes M111 to a scalar global energy control and falsifies the
claimed output-routing mechanism before any forward evaluation.

## 9. Relation to the prior no-go results

M111 is not eliminated by the existing theorems, but the prior evidence is
hostile.

* **M107:** exact-zero degree-4/6/8 additive zonals reversed from train to held
  on all four generated networks. M111 is outside that additive span because
  of (2), but it inherits the same coefficient-transfer risk.
* **M110:** bounded nodal occupancy is a nonnegative, sign-invariant sum of
  one-gate features. M111 preserves relative gate signs and signed downstream
  path cancellations, directly changing that causal link. It is not a retune
  of the tube width.
* **Frame annihilation:** M111's degree-two component is indeed useless on a
  complete frame, but its gate-product discontinuities have an infinite even
  tail. The theorem does not kill degrees four and above.
* **Euler/Stein:** no network gradient or divergence is used, so the
  Euler-Stein pointwise degeneracy does not apply.
* **Active-subspace tumbling:** `v(u)` observes the full 256-gate sign pattern,
  not a fixed `J`-dimensional linear input projection. The `(J/d)^6` capture
  argument therefore is not a proof against M111. However, (4) can collapse
  the *transported control* to one projective line, recreating a severe scalar
  bottleneck by another route.
* **Layer self-CV cancellation:** `T` is an early-layer observable propagated
  through an ungated linear surrogate, so the measured correlation-versus-
  dilution law is strong negative prior evidence. M111 is not identical to
  that tested class because it inserts a connected quadratic binary-gate
  vertex rather than a propagated mean. Only a fresh held-frame gate can tell
  whether that changed vertex escapes the cancellation.
* **Second-moment closure:** `Sigma` is an exact first-gate second moment, but
  M111 uses the realized centered quadratic fluctuation as a control. It is
  not a final-layer Gaussian closure. Its possible signal would be correlation
  between a connected first-gate pair field and missing higher cumulants.

## 10. Physics backups, compared without outcome selection

These are separate descendants, not extra columns to add after seeing M111.

### 10.1 Smooth scalar Herglotz energy

A real spherical Herglotz-like wave can be written

\[
 q_k(u)=\sum_i c_i\{\cos(k a_i^Tu)-m_d(k)\},
 \quad
 m_d(k)=\Gamma(d/2)(2/k)^{d/2-1}J_{d/2-1}(k).
\]

Its covariance and normalized squared energy have exact spherical means; for
example the cosine-product expectation is

\[
 \tfrac12\{m_d(k\|a_i-a_l\|)+m_d(k\|a_i+a_l\|)\}.
\]

This is legitimate standing-wave mathematics, but `k` is an unmotivated free
wavelength. Small `k` concentrates in low degrees already removed or tested;
large `k` creates high-order Bessel and numerical-cost problems. The binary
M111 wave has no wavelength to tune and puts its nodes exactly on ReLU gate
surfaces, so it is the honest primary.

### 10.2 Nematic quadratic energy

For a weights-only symmetric traceless matrix `Q`,

\[
 q_N(u)=u^TQu,qquad
 E[q_N^2]=\frac{2\operatorname{tr}(Q^2)}{d(d+2)},\qquad
 h_N=q_N^2/E[q_N^2]-1.
\]

This is exact, even, and parameter-free once `Q` is fixed invariantly. But
`q_N` is degree two, so `h_N` contains only degrees `0,2,4`; centering removes
zero and a frame removes degree two. A 5-design integrates it exactly, and the
trimmed MUB design nearly annihilates its remaining degree-four part. A general
`Q` can contain cross-axis degree-four structure not literally tested by M107,
so the family is preserved, but it is a lower-priority L1-only leaf rather
than the broad-spectrum mechanism sought here.

### 10.3 Centered shallow-ReLU/layer-2 linear energy

Let

\[
 r_i(u)=\operatorname{ReLU}(a_i^Tu)-\mu_d,
 \quad
 \mu_d=\frac{\Gamma(d/2)}{2\sqrt\pi\,\Gamma((d+1)/2)}.
\]

Its exact covariance is

\[
 K_{ik}=\frac{\sqrt{1-c^2}+c(\pi-\arccos c)}{2\pi d}-\mu_d^2,
 \quad c=a_i^Ta_k.
\]

Thus `q_R=r^Tt` and `h_R=q_R^2/(t^T Kt)-1` have exact mean zero. This is also
the centered energy of the actual first ReLU layer propagated linearly through
`D W2 ... W_L`, or equivalently a shallow layer-2-preactivation surrogate.
Its antipodal average should be used because `r(-u)` is not `-r(u)`.

This backup is more directly exposed to the already-negative first-layer ReLU
control and linear self-CV evidence. It preserves amplitudes that M111 throws
away, but it does not change the omitted-downstream-gates problem. It should
not be run in the same one-shot or selected after M111 outcomes.

An **actual layer-2 binary-gate** version is not admitted: for a fixed
nonlinear first layer, its gate means and pair covariance are not supplied by
the one-layer arcsine/arc-cosine identities. Estimating those means from the
same frames would forfeit the exact-zero control proof.

## 11. Smallest honest frozen generated-only gate

The gate below changes one causal edge only: additive one-gate geometry becomes
connected signed gate-pair energy. It deliberately mirrors the M107/M110
whole-network protocol so the failure boundary is interpretable.

### 11.1 Freeze and target-free static tests

Before weights or frames are generated, freeze source, config, package
versions, hashes, seeds, all thresholds, and an external manifest. Static
tests must cover:

1. the entrywise arcsine law against an independent bivariate orthant
   calculation, including diagonal, orthogonal, duplicate, and opposite axes;
2. exact-zero examples and the pair expansion (2);
3. antipodal equality, input rotation, hidden permutations, output
   permutations, and positive gauges at the first, middle, and last hidden
   layers;
4. zero/nullspace fallback and a test proving that denominator flooring would
   bias the mean;
5. equivalence of raw and column-renormalized transport on deterministic
   well-conditioned matrices;
6. a deliberately extreme product showing that unnormalized multiplication
   fails while the renormalized route stays finite;
7. analytic bound (3), manifest mismatch, one-shot, no-forward-before-precheck,
   and cost-accounting tests.

### 11.2 Control-only precheck on the frozen fresh weights

Use exactly four fresh He networks with seeds
`111001,111002,111003,111004`, width 256, depth 32, and 32 independently seeded
canonical Haar frames per network. This phase may inspect weights and sign
controls but must make the network evaluator unreachable. Kill before a
forward if any of the following occurs:

* a zero first-layer column, nonfinite value, unrecorded Gram excursion, or
  non-PSD `Sigma` beyond the frozen roundoff allowance;
* any output fallback, or
  `s_j/(||Sigma||_2 ||t_j||_2^2) <= 1e-8`;
* any `kappa_j > 1e6`;
* maximum relative block-control disagreement above `1e-4` between the
  canonical float path and the independent float64/association audit;
* pooled 32-frame block kurtosis above 10, a standardized block magnitude
  above 12, or a nonfinite frame block;
* full-gauge stress over factors `[2^-4,2^4]` changes any normalized block by
  more than `1e-4` relative;
* the projective participation `R_line < 2`, or the 32-by-256 block-control
  matrix has centered numerical rank below 2.

The last condition kills the **output-routed** implementation, while
preserving the scalar connected-energy leaf. These are numerical/mechanistic
guards, not target-derived choices.

### 11.3 One generated forward screen

Only if every precheck passes, evaluate the same four fresh networks once.
For each network use frames 0--15 for coefficient acquisition and frames
16--31 as untouched held frames. A whole generated network is the independent
unit; columns and antipodes are not units.

For each output separately, fit one slope on training-frame block means:
center `Y_train` and `H_train` **for the slope calculation only**, scale the
centered control by its training sample standard deviation, and use a frozen
ridge `lambda=1` in that standardized coordinate. Apply the resulting slope
to the **raw, analytically zero-mean** held control with no intercept and no
held centering. This preserves conditional unbiasedness because the training
frames and held Haar frames are independent conditional on the weights.

Let

\[
 R_i=\frac{\operatorname{tr}\widehat{\operatorname{Cov}}_{held}
       (Y_i-H_i\hat\beta_i)}
      {\operatorname{tr}\widehat{\operatorname{Cov}}_{held}(Y_i)}.
\]

Pooling is `sum_i V_adjusted,i / sum_i V_base,i`; it must not include
between-network mean shifts. Freeze a conservative decision cost factor
`rho_cost=1.08`, which charges the extra direction-by-output multiply, the
float64 arcsine Gram and quadratic forms, the 30 dense setup products, copies,
normalizations, and residual reserve. If an independent bill exceeds 1.08,
kill rather than replace the factor post hoc. Because half the frames acquire
coefficients,

\[
 E_i=2(1.08)R_i,
 \quad E_{geom}=\operatorname{geomean}_i E_i,
 \quad E_{pool}=2(1.08)R_{pool}.
\]

**Kill this implementation** with no seed, ridge, transport, or backup retry
if any law/resource/tail gate fails, any `R_i>=1`, or either
`E_geom>=0.90` or `E_pool>=0.90`.

**Promote only to a larger generated screen** if all four
`R_i < 0.90/(2*1.08) = 5/12`, both efficiency metrics are below 0.90, every
training-to-held covariance sign is reported, zero resource failures occur,
and an independent recomputation from raw immutable arrays agrees. A pass is
only a screened premise. It requires at least 20 new whole networks and then
an equal-cost L1 factorial before any champion mutation.

An outcome in the narrow logical gap between the promote and kill rules is
recorded as ambiguous and is not rerun during this deadline cycle. M111 may
not be combined with M107 or M110 without a four-cell interaction test.

## 12. Failure-localization and salvage

| Observation | Failed link | Preserved component |
|---|---|---|
| arcsine/mean/invariance test fails | formula or implementation | none until repaired under a new manifest |
| `s` or `kappa` gate fails | normalized rank-one energy is numerically unsafe | connected pair field (2) |
| `R_line` collapses | ungated deep transport loses output routing | scalar pair-energy diagnostic |
| control-only tails fail | square/normalization | bounded pair atoms `v_i v_k-Sigma_ik` |
| train improves, held reverses | coefficient transfer repeats M107 | exact pair observable, not its fitted slope |
| raw ratio improves but charged efficiency fails | extra matmul/setup cost | offline diagnostic only |
| all strict gates pass | connected binary pair field is a screened survivor | proceed to >=20 generated networks; no champion claim |

## Final judgment

The original M111 equation is mathematically viable after clarifying active
columns and entrywise arcsine covariance. Its strongest feature is equation
(2): M111 isolates connected cross-gate terms which M107 and M110 could not
represent, so the mutation is causal rather than decorative. Its strongest
liability is equally concrete: a deep ungated matrix product can collapse all
output paths onto one projective line, while the normalized square can amplify
near-null covariance into damaging tails.

That makes M111 worth exactly one frozen, control-first, generated-only premise
gate. It does not justify a sacred-frequency story, a backup sweep, or any
change to the measured champion before those hostile checks pass.

## 13. Pre-data protocol amendment: 50-frame five-fold cross-fitting

**Amendment status:** accepted for a first **out-of-fold risk screen**, subject
to the caveat below. This section supersedes the 32-frame 16/16 schedule and
the factor `2` in section 11.3 if, and only if, every source/config/test file is
changed before freezing. It does not weaken any control-only guard in section
11.2.

Partition 50 independent Haar frames into five fixed folds of exactly ten
frames by `frame_index mod 5`. For fold `k`, fit the one per-output standardized
ridge slope `beta_(-k)` on the other 40 frames and apply it to the raw controls
of the ten held frames. Define

\[
 \widehat\mu_{CF}
 =\frac1{50}\sum_{k=0}^4\sum_{r\in F_k}
   \{Y_r-\beta_{-k}H_r\}.
\]

Conditional on the weights and the other 40 frames, `beta_(-k)` is fixed and
each frame in `F_k` is independent with `E[H_r]=0`. Hence every summand has
mean `mu(W)` and

\[
 E[\widehat\mu_{CF}\mid W]=\mu(W).
\]

All 50 evaluated frames contribute to the final mean, so there is no literal
half-sample or factor-two path penalty. The screen efficiency proxy becomes

\[
 E_i=1.04R_i,
 \quad E_{geom}=\operatorname{geomean}_iE_i,
 \quad E_{pool}=1.04R_{pool}.
\]

The fixed `rho_cost=1.04` is accepted only if an independent call/allocation
ledger, including reverse per-column transport normalization, gives a complete
candidate-core factor at most 1.04. Use `max(1.04, measured_factor)` in the
analysis and kill if the measured factor exceeds the frozen reserve. A
float64 validation shadow which is not deployed must be reported separately;
it cannot be silently counted as free production arithmetic or silently
charged to the proposed deployment core.

### Important variance caveat

The 50 out-of-fold adjusted block values are not mutually independent:
training sets overlap, and an observation held in one fold participates in the
slopes used by other folds. Their ordinary sample trace variance is therefore
an honest **out-of-fold prediction-risk statistic**, but it is not, without a
further covariance argument, exactly `50 Var(mu_hat_CF)`. In particular it
does not measure every covariance contribution from random slope acquisition.

This does not spoil exact mean zero. It changes the interpretation and the
promotion ladder. A first-pass result must be labelled `OOF_risk_ratio`, not
`proved_crossfit_estimator_variance_ratio`. It may authorize repeated outer
50-frame superblocks, which directly estimate the variance of the entire
cross-fitted mean. It may not authorize an L1 or champion mutation by itself.

For the amended premise screen:

* **kill** on any structural/numerical/tail/resource failure, any per-network
  `OOF_R_i>=1`, or either charged geometric/pooled OOF risk at least `0.90`;
* **screen as a survivor to outer-superblock validation only** if all four
  `OOF_R_i < 0.85/1.04 = 85/104`, both charged geometric and pooled risks are
  below `0.85`, and an independent raw-array recomputation agrees;
* record the interval between those boundaries as ambiguous, with no retry or
  backup selection in the same run.

The stricter `0.85` survivor threshold reserves headroom for the unmeasured
cross-fold covariance and small four-network screen. Repeated outer
superblocks must then compare the actual cross-fitted mean against a 50-frame
baseline at equal total cost, with whole networks as units and a prespecified
uncertainty bound, before M111 can be called a validated child.

## 14. Causal-sufficiency correction after independent attack

An independent post-draft causal attack sharpens the negative prior without
changing the exact-control theorem. Let `g(U)` be the antipodally even network
output and define

\[
 \psi_{ik}=v_iv_k-\Sigma_{ik},\qquad
 B_{ik}(g)=E[(g-Eg)\psi_{ik}].
\]

Then the exact output/control covariance is

\[
 \operatorname{Cov}(g,h_j)
 =\frac{2}{s_j}\sum_{i<k}t_{ij}t_{kj}B_{ik}(g).                 \tag{5}
\]

M111 knows `Sigma` and the ungated transport `t`; it does **not** know the
connected output--two-gate tensor `B`. All omitted downstream ReLU masks live
in that missing tensor. Accordingly M111 must not be described as an estimator
of the generic finite-width connected four-point vertex. It is a prospectively
fixed probe whose overlap with that residual remains empirical.

There is a rigorous informational counterexample. At an internal hidden layer,
replace adjacent matrices by

\[
 W_k' = W_k A,\qquad W_{k+1}'=A^T W_{k+1}
\]

for a non-monomial orthogonal `A`. The ungated product, `W1`, `Sigma`, `T`, and
the pointwise M111 field are unchanged. The real network generally changes
because ReLU does not commute with `A`. For iid Gaussian He matrices this
transformation also preserves the ensemble law. Therefore the output and its
M111 covariance are not determined by `(W1,Sigma,T)`, even under the stated
ensemble.

The same independent attack's annealed independent-mask reference gives a
leading ungated-versus-gated path correlation of order
`2^(-(L-2)/2)/sqrt(pi)` and a two-leg energy overlap of order
`2^(-(L-2))/pi`, about `2.96e-10` at `L=32` before the Haar frame removes
degree two. This is a reference calculation, not a finite-network upper bound,
but ordinary relative `L/n=1/8` corrections do not naturally repair an
exponential gate mismatch.

This correction substantially lowers the mechanism prior. It does not make a
forward test dishonest: exact-zero controls can be useful without being
sufficient statistics. It does mean that a positive held effect would be
evidence for a genuinely connected, factorization-aware departure from the
annealed reference, while a null result should be localized to the ungated
transport rather than to all pair-gate observables. The full derivation and
counterexample are recorded in `M111_CAUSAL_LINK_ATTACK_20260807.md`.

## 15. Independent pre-freeze source audit

**Verdict: `PASS_TO_MANIFEST_CREATION_ONLY`.** This is not permission to run,
promote, deploy, or touch a champion. It releases only the current source
bytes for external hashing into a pre-execution manifest, followed by a
separate manifest/freeze check before the single generated-only run.

The final source audit found the theorem implemented with the required row
convention and without a denominator floor or fallback:

* `Ahat` is formed from normalized columns of `W1`; the arcsine is entrywise;
  candidate float32 and reference float64 sign-covariance matrices have
  separately frozen PSD gates.
* `T` is folded from selected `WL` columns backwards through `W_(L-1),...,W2`,
  with an independent positive normalization for every output column after
  every multiply, followed by the `D` row scale and one final column
  normalization. The retained `Sigma@T` product is reused for both `s` and
  `R_line`; no uncharged duplicate dense product remains.
* The hot control path performs one `v@T` product per frame. It squares before
  reduction, uses the exact normalized denominator, checks the deterministic
  tail certificate, and evaluates plus directions only because the control is
  exactly antipodally even.
* The full positive ReLU gauge stress spans every hidden layer over
  `2^-4..2^4`. The reference path uses the fixed output subset
  `0,17,...,255`. On fixed frames 0 and 25 it independently recomputes
  `(rho*frame64)^T W1_64`, audits gate-sign disagreement, and recomputes the
  subset controls. Denominator disagreement is genuinely relative;
  block/gauge disagreement is explicitly labelled as the mixed-scale metric
  `|a-b|/max(1,|b|)`.
* All four networks and all 50 control frames per network must clear the
  structural, PSD, denominator, tail, rank, projective-line, precision, gauge,
  and resource gates before the evaluator phase is reachable. The persisted
  event ledger has four precheck completions, one all-network barrier, then
  evaluator events and per-network evaluator timings.
* The five folds are fixed by `frame_index mod 5`, with exactly 40 training and
  10 held frames per fold. Held adjustments use the raw exact-zero control and
  no fitted intercept. The output calls the resulting statistic an OOF
  prediction-risk proxy, not the variance of the final cross-fit mean.
* The durable owner wrapper is the sole ordinary execution path. Direct worker
  entry is refused before generation; any failure after owner release creates
  `m111_failure.json`, and every subsequent invocation refuses the artifact.

The independent shape ledger evaluates to an enumerated candidate/base factor
of `1.0356616341030196`, below the frozen `rho_cost=1.04`, leaving
`1,888,845,824` scalar-equivalent operations of reserve under that proxy. It
explicitly charges both fixed float64 `W1` products, float64 subset controls,
full-gauge transforms/copies, candidate/reference covariance eigenaudits,
reverse per-column normalizations, `Sigma@T`, one `v@T` per frame, and OOF
regression. This is still not an official FlopScope or residual-wall trace;
therefore a surviving premise result cannot authorize deployment without the
later measured-headroom factorial already required above.

I independently replayed the inert, target-free suite on the final bytes:

```text
M111 target-free tests: passed=39 failed=0
```

The replay uses mock weights/prechecks/evaluators for orchestration tests and
runs no generated-network forward. At judgment time
`FROZEN_SOURCE_MANIFEST.json`, raw/result/failure artifacts, contest data,
scorer hooks, and submission hooks were absent. The causal prior remains
hostile for the reasons in section 14; the pass says only that the one-shot can
honestly falsify this exact operator without adaptive rescue.

## 16. Freeze-boundary correction and fresh verdict

The section-15 pass exposed one final lifecycle contradiction before any
manifest was created: two target-free tests and several status sentences
treated manifest absence as permanent, although manifest creation was the
approved next step. Frozen source must remain self-consistent on both sides of
that boundary. The affected bytes were repaired and re-audited.

The candidate and runner statuses are now phase-neutral `source_manifest_gated`
states. Before freeze, absence fails closed. After freeze, the same code only
accepts a manifest with passing theorem/cost releases and matching hashes for
the complete required source surface. The manifest-sensitive tests now have
two safe branches:

* pre-freeze: verify that the missing manifest fails before generation;
* post-freeze: perform read-only manifest/hash verification and never call the
  authorized wrapper with a valid token.

An explicit nonexistent temporary manifest path preserves the fail-closed test
even after the real manifest exists. Inventory and protocol language now
describe the same pre/post-freeze lifecycle. No estimator formula, seed,
threshold, disposition boundary, cost term, or evaluator path changed.

Fresh checks on the resulting bytes give:

```text
M111 target-free tests: passed=39 failed=0
CONFIG_GUARDS_OK
enumerated_total_to_base_factor = 1.0356616341030196
unmodeled_reserve_equivalents   = 1888845824
FROZEN_SOURCE_MANIFEST.json     = absent
generated result/failure files = absent
```

**Fresh verdict: `PASS_TO_MANIFEST_CREATION_ONLY`.** This verdict supersedes
the section-15 source-byte release. It still does not authorize a generated
forward. Hash these current bytes, create the external manifest, then run the
target-free suite once in its post-freeze branch and obtain the separate
manifest/freeze-judge release before the one-shot owner may be invoked.
