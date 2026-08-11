# DGFL-1 — fused dipole–Fourier gate-diffraction ladder

**Status:** `ZERO_EVIDENCE_STATIC_PROPOSAL / SOURCE_ABSENT / COST_OPEN / DO_NOT_EXECUTE`  
**Date:** 2026-08-11  
**Incumbent:** Kerdock v3.1 GUARDS (`W0`) remains the sole integrated artifact.  
**Mutation:** add a sparse, pilot-frozen, exactly centered sphere-divergence
control bank to W0. One skew-direction JVP is shared by the dipole and every
Fourier rung.  
**Normative execution:** serial `P=1`. A deterministic `P=2` schedule is a
separate conditional implementation and receives no credit until the official
Phase-2 process, meter, residual-time, and aggregate-RSS rules are bound.

This record translates the owner's higher-dimensional-slice / gate-boundary
diffraction idea into one falsifiable estimator. It is not an implementation,
experiment authorization, candidate, promotion, package, launch, or submission.
No generated network, truth, scorer, holdout, hosted system, or selection state
may be touched under this record.

## 1. Frozen anchors and epistemic boundary

Repository base at construction:

- Git commit: `ab5de3e8e9c0ef0329a2abdaffd1e9b712584e10`.
- W0 archive:
  `corpus/whestbench/experiments/v31_guards/submission_kerdock_v31_guards_20260808.tar.gz`,
  SHA-256
  `8382E269C9B32E0935492734DDF8182560120F7E9331621AA18839D5D1F4EA06`.
- W0 phased-design source:
  `kerdock_v3_estimator.py`, SHA-256
  `076D0A5D81891DDCBB4509DC6E2BFF5459D935B5556490A85D98DAC60759AACF`.
- W0 row-blocked source:
  `row_blocked_winograd.py`, SHA-256
  `A3BF5C8014198E33037D6AEAFC3F4138A98908754BB82BFCF5ACDD92B1D9FCCA`.
- W0 fold source:
  `fold3_estimator.py`, SHA-256
  `68449E3EFE3B82A860B884A2BD05C9260E1EFBD138A343257CDC51AD38A63F6F`.
- W0 guard wrapper:
  `estimator.py`, SHA-256
  `5E7D52156B330BF63AC4FF0E0F38D864B32677F82BC8ED4D1382787A27D3E0C9`.
- Exact kink-surface/Crofton record:
  `s9_crofton_transect/S9_VERDICT.md`, SHA-256
  `33BD2E712F43CD7FD59BBD6716354968F94B00A6AE0A8FEC0C023C0A30711BCA`.
- S9 result receipt: SHA-256
  `9EC8894F6C05F983A01D9CB832D7883FB90F52CA88D2587F8F96DB26411FA720`.
- Bragg-spectrum record:
  `s6_bragg_spectrum/S6_VERDICT.md`, SHA-256
  `413E9C87BAD340453D1A8CB5A324F19EB4B04171A45699FB5E70C16801AF2DC9`.

The only numerical resource orientation available here is the provisional
Phase-1 ledger:

```text
B                         = 272,000,000,000
W0 witness                = 259,700,821,492
arithmetic witness margin =  12,299,178,508
```

These are not Phase-2 rules and the W0 witness is not a complete worst-case
upper bound. Therefore DGFL-1 has no budget PASS. The implementation must be
static-killed if the later official rules or a source-derived complete path
ledger do not fit strictly with wall and process-tree RSS margin.

## 2. Ordinary mathematical translation of the metaphor

For a bias-free ReLU MLP, each output is continuous and piecewise linear in the
input. Its distributional Hessian and Laplacian are measures supported on gate
facets. Along a generic affine probe line `x(t)` transverse to the facets, the
distributional second derivative is a signed spike train,

```text
d^2 f(x(t))/dt^2 = sum_k Delta_s_k delta(t-t_k),
```

and its Fourier transform is

```text
D(omega) = sum_k Delta_s_k exp(-i omega t_k).
```

Thus the high-dimensional piecewise-linear fan is the latent object; gates are
tomographic slices; the measured rotation-to-rotation fluctuation is an
interference observable. This is a mathematical analogy, not a claim that the
random weights form a periodic crystal. S6 found that the fixed Kerdock
degree-4 deviation-operator spectrum was a flat shelf rather than a sparse
low-rank spectrum.

S9 proved that the target can be replaced by a Gaussian-weighted integral over
all kink facets, but on its width-64, depth-8 screen its exact Crofton
implementation was roughly `4e4`–`1.77e5` times worse per FLOP. DGFL-1 does not
estimate that surface integral. It uses a few pilot-local directions only as
known-mean controls; missing or inaccurate facets can reduce efficacy but
cannot change the control mean.

## 3. Ensemble, target, and filtration

Let `d=256`, let `U` be uniform on `S^(d-1)`, and let

```text
y_W(u) = full 32 x 256 layer-output stack at input rbar*u,
rbar   = E ||G||,  G ~ N(0,I_d).
```

The incumbent provider has the same codomain: its fold source returns
`stack((*analytic_means[:-1], final_mean), axis=0)` at
`fold3_estimator.py:294`, so `Y_W0(Q)` and every `Z_r(Q)` below are elements of
`R^(32 x 256)`. The official score may select or weight only part of that stack;
that weighting belongs to the frozen score inner product, not to an implicit
change of codomain.

Positive homogeneity gives `E_U y_W(U) = E_G H_W(G)` in ideal real
arithmetic. Let `D` be the fixed Kerdock direction multiset and `Q` the
production Haar rotation. `Q_D[h;Q]` denotes the fixed ordered mean of `h` over
the selected rotated design rows.

Throughout, `d sigma` denotes normalized surface probability measure on
`S^(d-1)`.

Define the complete pre-production sigma-field

```text
F_pre = sigma(W, rules, source hashes, pilot-A streams and values,
              selected subset, m, b, J, gate axes, frequencies,
              globally frozen development coefficients, shard map, P).
```

Production `Q` and every production-only stream must be independent of
`F_pre`. Frames sharing one `Q` are one statistical unit and may never be split
between fitting and validation.

DGFL-1 preserves the bias class of the base provider. In the ideal guard-quiet
Haar model the control addition is exactly conditionally unbiased. It does not
upgrade W0's deployed M186/M187 completion branches into an exact-unbiasedness
theorem.

## 4. One frozen dipole plane

Pilot A must emit orthonormal `m,b` and one real skew generator

```text
J = b m^T - m b^T,
J^T = -J,
Jm = b,
Jb = -m,
J^2 = -P_span(m,b).
```

The exact construction, gauge/sign convention, gap test, dtype, and source
bill must be sealed before any premise execution. A symmetric Householder is
not `J` and cannot be substituted. A separate `J_g` for each facet is forbidden
because it multiplies the dominant JVP cost.

If the plane is learned from pilot-local gate axes, a permissible prospective
construction is the top two simple eigenvectors of

```text
M = sum_g s_g^2 a_g a_g^T,
```

with invariant nonnegative strengths `s_g`, a frozen eigengap, and canonical
sign rules. This paragraph is not a source seal: the eventual manifest must
choose one exact construction or static-kill the family.

## 5. Fused sphere-divergence ladder

Here `S` is the fixed input sphere, `y_W` is the vector-valued network-output
stack rather than a probability density, `h` is a scalar modulator rather than
the estimated observable, and `J` is a frozen skew generator of input rotations
rather than the network Jacobian or a weight-transport velocity. The identity
below is fixed-sphere integration by parts (a rotational Stein/Ward identity),
not Reynolds transport across moving ReLU boundaries. Its two product-rule
terms cancel in expectation; neither term is an independently exact "bulk" or
"boundary residual" estimate of the target.

Assume componentwise `y_W in W^(1,1)(S^(d-1))`, scalar
`h in W^(1,infinity)(S^(d-1))`, and constant `J^T=-J`. Continuous CPWL network
outputs satisfy the first condition. Define, almost everywhere and weakly,

```text
C_h(u) = div_S [ y_W(u) h(u) X_J(u) ]
       = h(u) Dy_W(u)[X_J(u)] + (L_(X_J) h)(u) y_W(u),

X_J(u) = Ju,
L_(X_J) h(u) = Dh(u)[Ju].
```

Because `Ju` is tangent and divergence-free on the sphere, the weak product
rule gives

```text
integral_(S^(d-1)) div_S[y_W h X_J] d sigma = E_U C_h(U) = 0
```

componentwise for the complete `32 x 256` output stack. There is no
first-derivative facet delta because `y_W` is continuous. One physical-input
JVP starts with `delta x = Jx = rbar*Ju`; using bare `Ju` in physical
coordinates is a scale error.

The ladder uses one shared `Dy_W(u)[Ju]` per selected node.

### 5.1 Dipole rungs

```text
h_m(u) = m^T u,
h_b(u) = b^T u.
```

Both readouts share the same JVP. For example,

```text
C_m(u) = (m^T u) Dy_W(u)[Ju] - (b^T u) y_W(u).
```

Pure `h=1` is excluded from the premise; this record makes no covariance claim
for it against guarded W0.

### 5.2 Fourier gate rungs

Pilot A may freeze at most four deep local unit axes `a_g`. Each `a_g` must be a
unit vector in the physical input-sphere coordinates: specifically, the
normalized pullback gradient of a selected deep preactivation with respect to
the physical input inside one frozen pilot cell. A hidden-layer weight row lives
in activation coordinates and is forbidden even when its shape is also 256.
The manifest must bind the pullback order, cell, dtype, normalization, and
nonzero threshold. The premise family uses the fixed frequency set

```text
k in {sqrt(d), 2*sqrt(d)}.
```

For each `(g,k)`, set

```text
h_(g,k)(u)        = cos(k a_g^T u),
L_(X_J) h_(g,k)  = -k sin(k a_g^T u) (a_g^T J u),

C_(g,k)(u)   = h_(g,k)(u) Dy_W(u)[Ju]
             + (L_(X_J) h_(g,k))(u) y_W(u).
```

Every Fourier rung therefore reuses the dipole JVP. The complete product-rule
pair is required in general. If `J a_g=0`, the second term is identically zero;
an implementation must prove that special case rather than silently omit a
nonzero term.

### 5.3 Out-of-family cheap polarized plane-wave identity

The following no-JVP identity is recorded only to delimit the nearby theory. It
is **not** a DGFL-1 rung, F0 option, F1 flag, surrogate fallback, or post-result
backup. Any use requires a separately named, prospectively sealed child. Let

```text
Phi_d(xi) = E exp(i xi^T U) = phi_d(||xi||),
phi_d(k)  = Gamma(d/2) (2/k)^(d/2-1) J_(d/2-1)(k).
```

For `||a||=1`,

```text
D_(a,m,k)(u) = (m^T u) sin(k a^T u) + (m^T a) phi_d'(k).
```

In ideal real arithmetic this atom is antipodally even and exactly centered.
Sphere centering uses `phi_d`, never the Gaussian shortcut `exp(-k^2/2)`.
Nothing about its identity, Bessel evaluation, cast, efficacy, or bill transfers
to DGFL-1.

## 6. Child estimator and coefficient law

Let `S_rows` be a fixed pre-Q multiset of unit-normalized design rows in
`S^(d-1)`. For the premise, freeze 32 base directions and both antipodes
(`|S_rows|=64`). Define streamed means

```text
Z_r(Q) = |S_rows|^-1 sum_(v in S_rows) C_r(Qv).
```

For a finite linear coefficient vector measurable in `F_pre`,

```text
Y_DGFL(Q) = Y_W0(Q) - sum_(r=1)^R beta_r Z_r(Q),
beta_r in R finite.
```

The premise uses exactly one scalar coefficient per rung, shared across the
complete output stack. A per-layer, per-coordinate, diagonal, or full
output-matrix coefficient is forbidden in the premise because its estimation
and covariance burden are different families.

Linearity gives `sum_r beta_r C_(h_r)[y_W] = C_H[y_W]` for
`H=sum_r beta_r h_r`. F1 retains separate `Z_r` values only to fit and audit the
factorial blocks. A later provider may evaluate `H` and `L_(X_J) H` once per row and
stream one output-vector correction, but only after a source bill and bitwise
equivalence fixture. This does not imply universal or zero variance: for rank-2
`J`, every `C_H` is a derivative along closed rotation orbits and has zero
integral on each such orbit. Therefore not every quadrature error can lie in
this control span; any representable error must have zero mean on every closed
`J`-orbit.

The F1 coefficient law is global and offline. On exactly four predeclared
development networks and eight fit rotations per network, form

```text
Y_tilde_(w,q)   = Y_W0_(w,q) - mean_q Y_W0_(w,q),
Z_tilde_(w,q,r) = Z_(w,q,r)  - mean_q Z_(w,q,r).
```

Let `<.,.>_score` be the exact predeclared official score-weighted inner
product, with equal network weights, and set

```text
G_(r,s) = mean_w mean_q <Z_tilde_(w,q,r), Z_tilde_(w,q,s)>_score,
g_r     = mean_w mean_q <Z_tilde_(w,q,r), Y_tilde_(w,q)>_score,
lambda  = 2^-20 * trace(G)/R,
beta    = solve(G + lambda I, g).
```

The fit uses one fixed float64 Cholesky order. Nonfinite or nonpositive
`trace(G)`, factorization failure, or failure of a frozen high-precision
residual check kills F1; there is no pseudoinverse, retry, changed ridge,
intercept, clipping, sign choice, mode choice, stopping, thresholding, or row
dropping. The resulting finite `beta` values are global constants embedded in
any later provider. No per-network or production-time pilot-B exists, and the
development fitting bill is experimental rather than a provider-path cost.
Same-production-Q fitting and every nonlinear or adaptive coefficient map are
forbidden. No coefficient rule may be changed after an F1 value is seen.

### Bias-preservation theorem

Conditional on `F_pre`, every fixed `Qv` is uniform on the sphere and each
`C_r` is a spherical divergence. Therefore

```text
E_Q[Z(Q) | F_pre] = 0,
E_Q[Y_DGFL(Q) | F_pre] = E_Q[Y_W0(Q) | F_pre].
```

The theorem requires no claim that a pilot-local `a_g` is a globally owned
facet. Wrong axes affect variance only. It does require production totality:
post-Q failure followed by zero substitution or a value-dependent fallback is
not an unbiased estimator.

## 7. Exact interaction gate

One receipt must reconstruct all four factorial cells from the same frozen
base and control records:

```text
00 = W0
10 = W0 + dipole block only
01 = W0 + Fourier block only
11 = W0 + joint dipole/Fourier block
```

The coefficient law is component ablation of the one globally fitted joint
vector: arm 11 applies every frozen coefficient, arm 10 sets every Fourier
coefficient to zero, arm 01 sets both dipole coefficients to zero, and arm 00
sets all coefficients to zero. The single-arm coefficients are not refitted.
Refitting nested submodels would answer a different question and is a separately
sealed family.

The joint family survives only if it beats the better single family after
inclusive cost and the Fourier block has positive held incremental value after
residualizing against both dipole rungs. A joint win caused entirely by one
block does not authorize the other.

Let `V_00`, `V_10`, `V_01`, and `V_11` be the predeclared score-weighted trace
variances of W0, dipole-only, Fourier-only, and joint outputs over whole held
rotations, with all coefficients frozen before those rotations. Define

```text
R2_joint = 1 - V_11/V_00,
R2_F_given_D = 1 - V_11/V_10,
R2_D_given_F = 1 - V_11/V_01.
```

The ratio domain requires finite `V_00>0`, `V_10>0`, and `V_01>0`; otherwise
the premise fails closed without a variance floor or substituted denominator.

Let `C_00`, `C_10`, `C_01`, and `C_11` be the corresponding complete isolated
effective-compute scalars under the manifest-bound official law, including all
scalarized FLOP/residual/setup/return/cleanup terms. Wall and RSS remain separate
legality constraints and receipts unless the official law explicitly
scalarizes them. A joint arithmetic receipt may reconstruct all four values,
but it cannot infer counterfactual wall or RSS; those resources must be measured
in isolated arms or conservatively charged at the joint maximum. If independent
truth authority exists, the direct held official-score gate is that arm 11
beats `min(00,10,01)` with the predeclared paired uncertainty procedure. Without
truth, F1 may establish only rotation-variance/cost necessary conditions because
the shared unknown W0 bias and differing compute multipliers prevent an official
score claim. Under a single linear `cost * variance` branch, the necessary
condition specializes to

```text
C_11 * V_11 < min(C_00*V_00, C_10*V_10, C_01*V_01).
```

If the comparison objective is proportional to `cost * variance` and the
controlled cost is exactly `C_W0*(1+r)`, where `r=DeltaC/C_W0`, the necessary
held joint gate is

```text
R2_joint > r/(1+r),
equivalently (1+r)(1-R2_joint) < 1.
```

If the official score law, cost floor, bias term, or per-network weighting
differs, the manifest must derive and use the direct complete-score inequality;
the displayed variance gate is not portable by assertion.

Use whole independent rotations as units. The premise is truth-free for the
covariance question: within each network, center independent rotation
replicates and evaluate held trace variance. Truth may be used only if an
independent authority later permits the already-cached development receipt;
it is not needed to decide whether the control tracks rotation error.

## 8. Streaming implementation constraint

Never materialize an `N x modes x outputs` tensor. At
`N=64,512`, `modes=32`, `outputs=256`, float32 alone would be about 1.97 GiB.
Process fixed row shards and stream into small `modes x 256` float64
accumulators.

The current W0 phased transform can evaluate projections of several frozen
axes by applying the phased WHT to `Q^T A`. That observation grants no source
reuse by itself. A new child must prove exact row order, scale, dtype, and bill,
and must not alter W0's primal bytes.

Current W0 does not expose a general deep JVP sidecar or the selected primal
states/gates. The child must either:

1. retain exactly the fixed subset state with a complete lifetime/RSS bill; or
2. replay the complete selected-row primal path and charge it.

Silent cache reuse is forbidden.

Current W0 also constructs and discards its production `Q` internally in
`kerdock_v3_estimator.py:139-159`. A child must either retain that exact object
without changing W0 arithmetic, or regenerate it from the same `mlp.seed` path
and prove byte identity before any network experiment. The complete bill must
include RNG, QR, sign handling, casts/copies, selected-row construction, and
retained-`Q` lifetime/RSS. A merely distributionally equivalent second `Q`
invalidates the paired control.

## 9. Deterministic serial and conditional parallel schedules

### 9.1 Normative `P=1`

1. Complete the pre-Q pilot, source certificate, and route decision.
2. Construct production Q.
3. Run immutable W0 without overlap.
4. Enter a source-proved parent-quiescent state whose persistent WHT/Winograd
   buffers and allocator behavior are explicitly measured. Run fixed row
   shards. For each row, compute one primal/JVP state and immediately form every
   dipole and fused Fourier rung before releasing that state.
5. Reduce every shard in ascending
   `(family, level, frame, row, axis, output)` order through one frozen binary
   merge tree.
6. Apply coefficients once, run one whole-output guard, and return.

No new approximate child fallback is permitted. Before Pilot A, reserve the
maximum of the W0-only reject path, every spent-pilot-plus-cleanup-plus-W0 path,
every inherited W0 completion/guard branch plus the complete control, and the
full success path. A pre-pilot reserve rejection returns W0. A Pilot-A failure
before Q may return W0 only when its spent work, cleanup, and W0 were reserved.
Once Q exists, every inherited W0 branch that returns a complete stack must
receive the complete frozen control; otherwise that Q-dependent branch gates
the correction. Inherited M186/M187 behavior is not relabeled a new child
fallback. A W0 exception or post-Q child failure is a provider failure and may
not return a partial correction or silently fall back.

### 9.2 Conditional `P=2`

Only after W0 has completed and a measured parent-quiescent state is reached may
a separately sealed implementation split the fixed selected-row shards into two
immutable row partitions. Each worker computes one primal/JVP per assigned row
and every dipole/Fourier rung for that row. Splitting workers by control family is
forbidden because it would duplicate the dominant JVP or require an unsealed
JVP-value IPC/cache. There is no work stealing, early cancellation,
network-dependent `P`, cross-worker cache, or reduction by completion order.
Native libraries use one thread per worker. `P=1` uses the identical row shards
and merge tree; outputs, guards, and receipts must be bitwise identical.

Inclusive accounting is

```text
F_wave = sum_t F_t + F_serialization + F_IPC_copy + F_hash
       + F_setup + F_merge + F_join + F_cleanup,

T_wave = T_spawn + max_w sum_(t assigned w) T_t
       + T_barrier + T_merge + T_teardown,

RSS_wave = RSS_parent_quiescent + sum_w RSS_worker_w
         + RSS_IPC + RSS_shards.
```

The shard leaves and central binary merge tree are identical at `P=1` and
`P=2`; worker-local regrouping is forbidden. Parallelism never discounts FLOPs.
Under the provisional `C=F+1e11*R` law, lawful aggregate subprocess metering,
bitwise-identical predictions, and the same unfloored linear score branch, it
can improve score only if the reduction in charged residual time strictly
exceeds its extra FLOP-equivalent charge:

```text
1e11 * (R_serial - R_parallel) > F_parallel - F_serial.
```

If the official law, floor/cap, process accounting, or score branch differs,
the manifest must derive the direct inequality; the display is not portable by
assertion. Until the official Phase-2 rules and a paired resource receipt prove
the applicable inequality with strict RSS margin, `P=2` is descriptive only and
`P=1` remains normative.

## 10. Complete cost paths required before any generated execution

The implementation manifest must bind typed, source-derived prefix maxima for
all paths:

```text
F_child = F_W0 + F_pilot + F_axes + F_JVP + F_primal_replay_or_retention
        + F_Q_generation_or_retention + F_modulators + F_QtA + F_WHT
        + F_trig + F_center
        + F_reduce + F_coefficients + F_guards + F_return + F_cleanup.
```

Parallel bills use the sums in section 9, never the largest worker alone.
Wall uses the critical path including spawn/join/teardown. RSS uses the maximum
simultaneous process-tree footprint, not `max(worker)` and not copy-on-write
credit.

A rough per-invocation premise orientation, not a bill, is 0.27–0.54B for 64
tangent rows depending on whether primal replay is required, before axis
construction, Q regeneration/retention, Fourier evaluation, reduction, guards,
and residual time. The inherited AJ2 worksheet supplies the
`259,700,821,492` W0 witness; no independent machine receipt for that exact
total is claimed here. The prior unfused full-node JVP worksheet reached exactly
`273,225,559,798` before omitted work and is over the provisional Phase-1
budget, as corrected in
`CODEX_OPUS_P4_P5_P6_HOSTILE_AUDIT_ERRATUM1_20260811.md:31-42`. That erratum
prevents treating the worksheet as a theorem-level lower bound. Full-node DGFL
is nevertheless excluded from the premise.

For scale only, F1 contains 64 inherited W0 receipts across four networks and
16 base/control rotations per network. Their inherited witness total is
`16,620,852,575,488` FLOPs. The 4,096 selected rows contribute a dense tangent
core of `17,146,314,752` FLOPs if primal state is retained, or
`34,292,629,504` with a primal replay, before Pilot A and every positive extra.
These are panel-level experimental orientations, not per-invocation submission
bills.

## 11. Cheapest falsification ladder

No step authorizes itself. Every step needs a pre-evidence manifest and an
independent authority decision.

### F0 — symbolic and synthetic only

- Construct `J` from exact paired assignments with an exactly zero diagonal so
  `J^T=-J` is bitwise. Check `J^2=-P`, `Jm=b`, `Jb=-m`, norms, and
  orthogonality against a high-precision reference with manifest-sealed absolute
  and relative tolerances; library-default `allclose` is forbidden.
- Verify each divergence formula by directional finite-difference and AD away
  from gates on deterministic hand-built CPWL networks. At frozen boundary
  fixtures, test the two one-sided derivatives and the weak/integrated
  divergence identity; do not equate the theorem with one arbitrary ReLU AD
  subgradient.
- Verify both Fourier terms are present and have the correct sign.
- Verify the no-main-Q dependency by source graph. For antipodal behavior, let
  `A f(u)=(f(u)+f(-u))/2` and verify
  `A C_h[y]=C_h[y_even]` for even `h`, and
  `A C_h[y]=C_h[y_odd]` for odd `h`. Do not assign one parity to a generic
  fused rung. The out-of-family plane-wave identity receives no F0 credit.
- Verify serial/parallel shard coverage, one JVP per row, deterministic merge,
  failure semantics, and complete bills without generated networks.

Any mismatch kills the exact source family.

### F1 — smallest premise panel

Freeze before values:

- four fresh generated development networks;
- one additional domain-separated 64-row Pilot-A rotation per network;
- sixteen independent base/control Haar rotations per network;
- eight rotations for coefficient fitting and eight untouched rotations for
  evaluation;
- Pilot-A's exact stream tuple, direction count, eligible layers/gates, jump
  strength, axis-ranking rule, zero/nonfinite handling, duplicate threshold,
  tie order, eigengap, sign convention, and coefficient-stability/tail statistic;
- one skew J, the two dipole modulators, and exactly four deep pilot axes; failure
  to obtain four valid axes takes the W0-only pre-Q route and fails the mechanism
  premise rather than shrinking the dictionary;
- frequencies `{sqrt(d),2*sqrt(d)}`;
- one fixed 64-row antipodal subset;
- four factorial arms reconstructed from one base/control receipt;
- source-derived incremental FLOP/wall/RSS bill;
- paired trace-variance statistic, interval method, alpha, and multiplicity.

Kill if any of the following occurs:

1. the necessary cost-weighted variance gate fails; or, if independent truth
   authority exists, the direct held official-score gate fails;
2. either block's held partial `R2 <= 0`;
3. under the assumptions of section 7, the held joint `R2` does not strictly
   exceed `r/(1+r)` with the predeclared uncertainty margin; otherwise the
   direct manifest-bound score inequality fails;
4. any network reverses beyond the predeclared tail bound;
5. coefficient signs/subspaces are unstable across whole-network sensitivity;
6. efficacy requires same-Q fitting, frequency tuning, row dropping, retry, or
   value-dependent parallel routing;
7. any mean-zero, finite, source-hash, bill, wall, or aggregate-RSS guard fails.

### F2 and later

A surviving premise earns only a >=20-network paired screen against immutable
W0, followed by a distinct validation panel and untouched final gate. Promotion
requires zero failures, direct bias noninferiority, raw MSE improvement,
complete adjusted-score improvement, resource margin, subprocess stability,
and a hostile source/package audit. No F1 value may tune the sealed family.

## 12. Prior negative evidence and precise novelty boundary

- S6: in the fixed Kerdock degree-4 deviation operator, the top 100 eigenvalues
  carry 0.32% of `tr(D^2)`; this does not characterize all frequencies or the
  network-residual spectrum.
- S9: on its width-64, depth-8 screen, exact complete boundary/Crofton
  estimation was `4e4`–`1.77e5` times worse per FLOP and exhibited signed
  cancellation.
- S5/S15/S18: first-layer kink distance, cheap first-layer covariates, and cell
  identity did not expose a useful held signal.
- M111/M112: pair-gate/interference controls worsened held variance.
- M191: fixed harmonic controls produced only a small gain.
- `CODEX_OPUS_P4_P5_P6_HOSTILE_AUDIT_20260811.md`, section 3.7, already records
  the first-order sphere-divergence `C_v` ancestor.
- `corpus/whestbench/resources/research_excursions/`
  `M111_COHERENT_GATE_THEORY_JUDGE_20260807.md`, section 10.1, already records
  Bessel/Herglotz cosine controls.
- First-layer-only paired dipole signal is annihilated by antipodes and complete
  orthonormal bases at low degree.

These are severe priors. They do not theorem-kill a deep, pilot-frozen,
shared-J divergence ladder. Within this corpus, divergence controls and cosine
atoms have disclosed ancestors. The proposed differentiator of DGFL-1 within
this corpus is the following factorization: a pilot-frozen deep skew-J direction
and complementary dipole/Fourier readouts share one deep JVP while remaining
separately centered, so a truth-free factorial panel can test whether they
remove complementary rotation error. The fixed frequencies were chosen after
observing prior-family outcomes and inherit no evidence. No external prior-art
search or publication-level novelty claim is made. Until the new panel passes,
there is no variance, cost, score, novelty, or ranking credit.

## 13. Stop conditions and disposition

Static-kill DGFL-1 without execution if:

- official Phase-2 rules forbid the required numerical path or leave no strict
  complete-path margin;
- a source cannot prove production Q independence and totality;
- one shared JVP cannot serve every rung;
- current W0 bytes or guards cannot remain immutable;
- selected state retention/replay or aggregate RSS cannot fit;
- the exact centered formulas cannot be implemented under the meter;
- the full source-derived cost threshold makes the required held `R2`
  unattainable or scientifically implausible;
- the planned parallel path cannot beat serial inclusively.

Otherwise preserve DGFL-1 as an unresolved proposal and run only the next
authorized falsifier. GUARDS remains the incumbent throughout.
