# Dipole–Fourier Rotational Stein Ladders for White-Box Estimation in ReLU Networks

*A theoretical construction and prospective falsification protocol*

**Status:** companion theory note with `PASS_SYNTHETIC_MATH_ONLY`; no estimator-efficacy result<br>
**Date:** 2026-08-11<br>
**Implementation status:** deterministic math harness only; provider source absent and cost/resource bounds open<br>
**Incumbent:** Kerdock v3.1 GUARDS remains the only integrated estimator

## Abstract

We introduce a sparse control-variate family for Haar-randomized spherical quadrature of bias-free ReLU networks. The construction begins with a two-dimensional input plane and its skew rotation generator $J$. A single directional derivative $D y(u)[Ju]$ is then reused by two complementary classes of scalar modulators: linear dipoles and fixed-frequency cosine modes derived from pilot-selected deep gate directions. Each resulting vector control is a surface divergence on the fixed input sphere and therefore has exactly zero spherical mean in the ideal real-arithmetic model. When its geometry and coefficient vector are frozen independently of the production Haar rotation, subtracting the sampled control preserves the conditional mean of the base estimator.

The central computational idea is a shared-$J$ ladder. The expensive network Jacobian–vector product is evaluated once per selected node, while all dipole and Fourier readouts are formed by inexpensive scalar modulation. The separate rungs are retained during development to measure interaction and incremental value, but linearity would permit a future provider to fuse them into one scalar field after coefficients have been frozen.

This paper proves the mean-zero identity and specifies a falsification program.
Its deterministic synthetic harness passes 20 of 20 manifest-bound mathematical
contract tests. It reports no variance reduction, score improvement, cost pass,
provider implementation, or generated-network result. The construction is a
fixed-sphere control rather than a moving-boundary estimator; it neither
reconstructs a boundary integral nor implies zero variance.

## Relationship to the Phase-1 writeup

This note is designed to be read alongside the
[Phase-1 algorithm writeup](../core/PHASE1_WRITEUP_DRAFT_20260808.md). The
Phase-1 paper documents the Kerdock, radial-conditioning, pruning, folding, and
guarded estimator that was actually built and evaluated. This companion begins
where that account stops: it asks whether a new, analytically centered control
can remove a reproducible component of the remaining rotation error.

The separation is strict. DGFL was not part of the Phase-1 submission, and no
Phase-1 score, ablation, or hosted result is evidence for it. Conversely, this
note does not revise the Phase-1 algorithm or its empirical claims. Its role is
to make the next mechanism mathematically precise and cheaply falsifiable.

## Synthetic F0 result

The first testable slice of the proposal is now implemented as a deterministic
float64 mathematical harness. Its exact
[pre-execution manifest](../experiments/dgfl1_f0_synthetic/PREEXECUTION_MANIFEST.json)
has SHA-256
`85CA3CCF5F6BE7E1E3DBF7F417E5CF1138F55B737F22B5A3F47BA9F5E7F4821B`.
The bound run passed 20 of 20 tests; the exact
[result](../experiments/dgfl1_f0_synthetic/F0_RESULTS.json) has SHA-256
`251931A4F6B1EDC27593276248D213793CAB3EB730CBEB46F0A9AC9EC3250780`.

The tests cover skew-plane geometry, the shared JVP against finite-difference
and independent full-Jacobian references, physical-radius transport,
WHest-style row weights and absorbed-$Q$ coordinates, both dipole signs, the
Fourier Lie term, fusion, antipodal parity, a weak full-orbit identity across a
hand-built ReLU kink, and canonical reduction under adversarial shard emission.
The [notes](../experiments/dgfl1_f0_synthetic/F0_NOTES.md) preserve the exact
scope and test-driven chronology.

This is a synthetic mathematical-contract result, not a complete source F0.
It does not test a generated network, production $Q$, W0 guard paths, real
multiprocessing, cost, variance reduction, MSE, or score. This result section
was finalized only after the sealed run and did not alter its source or tests.

## 1. Problem and scope

Let a known bias-free ReLU network map an input $x\in\mathbb R^d$ to a vector $f_W(x)\in\mathbb R^p$. The white-box estimation problem is to approximate

\[
\mu(W)=\mathbb E_{G\sim\mathcal N(0,I_d)} f_W(G)
\]

under a fixed computational budget. Because the network is positively homogeneous, $f_W(r u)=r f_W(u)$ for $r\ge 0$. With $U$ uniform on the unit sphere and

\[
\bar r=\mathbb E\|G\|_2,
\]

the Gaussian expectation can therefore be written as

\[
\mu(W)=\mathbb E_U y_W(U),
\qquad
y_W(u)=f_W(\bar r u).
\]

The argument is componentwise, but this companion fixes $p=32\times256$ for
the all-layer stack returned by the incumbent provider. Every control has the
same codomain. The eventual score inner product may emphasize only part of that
stack, but a final-vector-only sidecar would be a different family and requires
its own source and evidence contract.

The base estimator rotates a fixed structured direction set by a production matrix $Q$. We write $Y_0(Q)$ for its output. DGFL does not replace this estimator. It constructs sampled functions with known spherical mean zero and subtracts a frozen linear combination from $Y_0$. The goal is variance reduction at acceptable inclusive cost, not a new analytic approximation to $\mu(W)$.

This distinction is essential. The theorem below preserves the conditional mean of the base provider. It does not remove bias already present in the implemented provider from finite-precision rotations, guard branches, or approximate completion paths. Finite design size contributes quadrature variance rather than conditional Haar bias by itself.

## 2. From slices to Fourier controls

A bias-free ReLU network is a continuous piecewise-linear function of its input. Its linear regions form a polyhedral fan, and changes of gradient occur on gate facets. Along a generic affine line $x(t)$ crossing those facets, a scalar network output has a distributional second derivative of the form

\[
\frac{d^2}{dt^2} f_W(x(t))
=\sum_j \Delta s_j\,\delta(t-t_j),
\]

whose Fourier transform is

\[
\mathcal D(\omega)=\sum_j \Delta s_j e^{-i\omega t_j}.
\]

This is the precise content of the slice-and-diffraction metaphor: a high-dimensional piecewise-linear object is observed through lower-dimensional probes, and Fourier phases encode the relative positions of gradient changes along those probes. It does **not** make the independent random weights a periodic crystal or turn the network output into a transported density.

Literal enumeration of all ReLU facets is computationally inappropriate here. The local [S9 Crofton screen](../experiments/s9_crofton_transect/S9_VERDICT.md) found complete boundary estimation many orders of magnitude less efficient on its tested network, while the [S6 spectrum audit](../experiments/s6_bragg_spectrum/S6_VERDICT.md) found a broad degree-four shelf rather than a small collection of dominant Bragg modes. The present construction consequently uses only a few pilot-frozen directions as control features. Missing or inaccurate directions can destroy efficacy, but cannot change their analytically known mean.

## 3. A rotational Stein identity on the sphere

Let $J\in\mathbb R^{d\times d}$ be constant and skew-symmetric, $J^\top=-J$. The vector field

\[
X_J(u)=Ju
\]

is tangent to $S^{d-1}$, because $u^\top Ju=0$, and it is divergence-free on the sphere. Assume, componentwise,

\[
y_W\in W^{1,1}(S^{d-1};\mathbb R^p),
\qquad
h\in W^{1,\infty}(S^{d-1}),
\]

with normalized surface probability measure. Then $y_WhX_J\in W^{1,1}$.
Define the control componentwise by

\[
C_h[y_W](u)
=\operatorname{div}_S\!\left(y_W(u)h(u)X_J(u)\right).
\]

The weak product rule gives

\[
C_h[y_W](u)
=h(u)D y_W(u)[Ju]
+\bigl(Dh(u)[Ju]\bigr)y_W(u).
\tag{1}
\]

Continuous piecewise-linear network outputs are Lipschitz on the compact sphere, so these assumptions hold. The weak product rule and integration by parts on the closed sphere yield

\[
\mathbb E_U C_h[y_W](U)=0.
\tag{2}
\]

Equation (2) is the exact mathematical foundation of the method. It is a fixed-domain rotational Stein, Ward, or integration-by-parts identity. The two terms in (1) cancel in expectation. They are not an exact “bulk estimate” and a stochastic “boundary residual,” and there is no moving integration domain. Because $y_W$ is continuous, its first weak derivative has no facet delta measure; the facet measure appears one derivative later.

For a physical input $x=\bar r u$, the tangent propagated through the network must begin at

\[
\delta x=Jx=\bar r Ju.
\]

Starting the physical Jacobian–vector product with bare $Ju$ would introduce a scale error.

### Proposition 1: conditional mean preservation

Let

\[
\mathcal F_{\mathrm{pre}}
=\sigma\!\left(W,S_{\mathrm{rows}},\text{pilot streams and values},J,
\{h_r\},\beta,\text{source rules, route, and schedule}\right),
\]

where $S_{\mathrm{rows}}$ is a fixed multiset of unit vectors. Require
$Q\mid\mathcal F_{\mathrm{pre}}\sim\operatorname{Haar}(O(d))$. Define

\[
Z_r(Q)=\frac{1}{|S_{\mathrm{rows}}|}
\sum_{v\in S_{\mathrm{rows}}} C_{h_r}[y_W](Qv)
\]

and

\[
Y_{\mathrm{DGFL}}(Q)
=Y_0(Q)-\sum_{r=1}^{R}\beta_r Z_r(Q),
\]

where every finite $\beta_r$ is frozen before production $Q$. Then

\[
\mathbb E_Q[Z_r(Q)\mid\mathcal F_{\mathrm{pre}}]=0,
\qquad
\mathbb E_Q[Y_{\mathrm{DGFL}}(Q)\mid\mathcal F_{\mathrm{pre}}]
=\mathbb E_Q[Y_0(Q)\mid\mathcal F_{\mathrm{pre}}].
\]

The proof is immediate: for each fixed unit $v$, $Qv$ is uniform on the sphere, so (2) applies row by row. This argument requires complete production totality. A post-$Q$ exception followed by zero substitution or a value-dependent fallback is generally biased.

## 4. The dipole plane

An independent pilot selects an oriented two-dimensional input plane with orthonormal basis $m,b$. Its generator is

\[
J=bm^\top-mb^\top.
\tag{3}
\]

It obeys

\[
J^\top=-J,\qquad Jm=b,\qquad Jb=-m,
\qquad J^2=-P_{\operatorname{span}(m,b)}.
\]

This is a rank-two infinitesimal rotation. A symmetric Householder reflection is not interchangeable with $J$. The pilot must freeze the plane, orientation, tie rules, eigengap, dtype, and failure behavior before the production rotation is drawn.

The two linear dipoles are

\[
h_m(u)=m^\top u,
\qquad
h_b(u)=b^\top u.
\]

Substitution into (1) yields

\[
C_m(u)
=(m^\top u)D y_W(u)[Ju]-(b^\top u)y_W(u),
\tag{4}
\]

and

\[
C_b(u)
=(b^\top u)D y_W(u)[Ju]+(m^\top u)y_W(u).
\tag{5}
\]

Both controls reuse the same directional derivative. Their value is not guaranteed by the mean-zero theorem; their usefulness depends on covariance with the rotation error of the base design.

## 5. The Fourier ladder

The pilot may additionally freeze a small set of unit directions $a_g\in\mathbb R^d$. A deep direction must be expressed in physical input coordinates—for example, as a normalized pullback gradient of a selected deep preactivation inside a frozen pilot cell. A hidden-layer weight row is not a valid substitute merely because it has the same numerical length.

For a prospectively fixed frequency $k$, define

\[
h_{g,k}(u)=\cos(k a_g^\top u).
\]

Its derivative along the rotational field is

\[
D h_{g,k}(u)[Ju]
=-k\sin(k a_g^\top u)(a_g^\top Ju),
\]

and its exact control is

\[
C_{g,k}(u)
=\cos(k a_g^\top u)D y_W(u)[Ju]
-k\sin(k a_g^\top u)(a_g^\top Ju)y_W(u).
\tag{6}
\]

The second product-rule term in (6) is mandatory unless the implementation proves $Ja_g=0$. Omitting it converts an exactly centered divergence into an uncontrolled feature.

The theory permits any finite bank. The prospective F1 ladder requires exactly
four valid pilot axes and the two frequencies

\[
k\in\{\sqrt d,\,2\sqrt d\}.
\]

Failure to produce four valid axes follows the sealed pre-$Q$ W0-only route and
fails the mechanism premise rather than shrinking the dictionary. The
frequencies are hypotheses, not a learned spectrum. They may not be tuned on
production outputs, and attention or nonlinear mixing driven by the same
production rotation would invalidate Proposition 1.

The dipole and cosine rungs are not algebraic duplicates. The dipoles are odd scalar modulators, whereas the cosine modes are even. With an antipodally paired row set, they interrogate complementary odd and even parts of the network response. That complementarity is a motivation for a factorial test, not evidence of positive interaction.

## 6. One derivative chain, many readouts

The decisive engineering feature is that equations (4)–(6) share the single quantity

\[
v_J(u)=D y_W(u)[Ju].
\]

A network Jacobian–vector product is therefore propagated once per selected node. Every dipole and Fourier rung then combines $v_J(u)$, $y_W(u)$, and inexpensive scalar factors. Assigning a separate skew generator to each gate direction would multiply the dominant derivative cost and is outside this family.

The control operator is linear in its modulator:

\[
\sum_r \beta_r C_{h_r}[y_W]
=C_H[y_W],
\qquad
H=\sum_r\beta_r h_r.
\tag{7}
\]

For the prospective ten-rung F1 bank, the fused field is explicitly

\[
H_\beta(u)=\beta_m m^\top u+\beta_b b^\top u
+\sum_{g=1}^{4}\sum_{k\in\{\sqrt d,2\sqrt d\}}
\beta_{g,k}\cos(k a_g^\top u),
\]

with

\[
D H_\beta(u)[Ju]
=-\beta_m b^\top u+\beta_b m^\top u
-\sum_{g,k}\beta_{g,k}k\sin(k a_g^\top u)(a_g^\top Ju).
\]

Development code should retain separate $Z_r$ values so the dipole and Fourier blocks can be fitted and audited. After the coefficients are frozen, a provider may use (7) to accumulate only $H$ and $D H[Ju]$ per row, subject to a source-derived bill and a bitwise-equivalence test.

Linearity also exposes a limitation. For $u_t=e^{tJ}u$, every field satisfies,
almost everywhere and weakly,

\[
C_H[y_W](u_t)=\frac{d}{dt}\bigl(H(u_t)y_W(u_t)\bigr).
\]

The rank-two flow closes after a full rotation, so

\[
\int_0^{2\pi} C_H[y_W](e^{tJ}u)\,dt=0.
\]

At the design level define

\[
A_H(Q)=\frac{1}{|S_{\mathrm{rows}}|}\sum_v H(Qv)y_W(Qv).
\]

Then

\[
Z_H(e^{tJ}Q)=\frac{d}{dt}A_H(e^{tJ}Q),
\qquad
\int_0^{2\pi}Z_H(e^{tJ}Q)\,dt=0.
\]

Thus an error function $e(Q)$ that equals $Z_H(Q)$ for every $Q$ must have
zero mean on every left-$J$ orbit. This is necessary, not sufficient, and it
does not constrain one isolated realized error vector. The construction is a
restricted control family, not a universal or zero-variance representation.

## 7. Frozen coefficients and factorial interaction test

Coefficients must be learned from development rotations independent of the final production rotations. The prospective F1 coefficient law is a fixed ridge regression on centered whole-rotation outputs. For development networks $w$, fit rotations $q$, and score inner product $\langle\cdot,\cdot\rangle_s$, define

\[
\widetilde Y_{wq}=Y_{0,wq}-\overline Y_w,
\qquad
\widetilde Z_{wqr}=Z_{wqr}-\overline Z_{wr},
\]

\[
G_{rs}=\operatorname{mean}_{w,q}
\langle\widetilde Z_{wqr},\widetilde Z_{wqs}\rangle_s,
\qquad
g_r=\operatorname{mean}_{w,q}
\langle\widetilde Z_{wqr},\widetilde Y_{wq}\rangle_s,
\]

and

\[
\beta=\operatorname{solve}(G+\lambda I,g),
\qquad
\lambda=2^{-20}\frac{\operatorname{tr}G}{R}.
\tag{8}
\]

The solve uses one fixed float64 Cholesky order. Nonfinite or nonpositive
$\operatorname{tr}G$, factorization failure, or failure of a frozen
high-precision residual check kills F1. Coefficient clipping or caps,
pseudoinverse retry, changed ridge, same-$Q$ fitting, frequency search, sign
selection, row dropping, and post-result shrinkage are forbidden. In a future
provider, the fitted vector would be a global constant rather than a
per-network pilot regression.

The bounded F1 premise panel is a $2\times2$ factorial comparison reconstructed from common base and control records:

\[
00=Y_0,\quad
10=Y_0-\text{dipole},\quad
01=Y_0-\text{Fourier},\quad
11=Y_0-\text{dipole}-\text{Fourier}.
\]

The single-arm coefficients are obtained by zeroing the other block of one globally fitted joint vector; they are not refitted. If $V_{ij}$ denotes held whole-rotation trace variance, the incremental diagnostics are

\[
R^2_{\mathrm{joint}}=1-\frac{V_{11}}{V_{00}},
\quad
R^2_{F\mid D}=1-\frac{V_{11}}{V_{10}},
\quad
R^2_{D\mid F}=1-\frac{V_{11}}{V_{01}}.
\tag{9}
\]

All denominators must be finite and strictly positive. Let $C_{00}$, $C_{10}$,
$C_{01}$, and $C_{11}$ be complete isolated effective-compute scalars under a
manifest-bound linear cost law. The necessary cost-weighted variance gate is

\[
C_{11}V_{11}<\min(C_{00}V_{00},C_{10}V_{10},C_{01}V_{01}).
\tag{10}
\]

Wall time and RSS require isolated-arm receipts or conservative charging at
the joint maximum. Both partial values in (9) must also be positive. Four
development networks provide a kill screen for conditional rotation transfer,
not population evidence. Without independently authorized truth, F1 cannot
make an official-score claim because the shared unknown W0 bias is multiplied
by differing arm costs and nonlinear score branches may apply; the eventual
manifest must replace (10) if the bound score law is not a single linear
cost-times-variance branch.

## 8. Serial and parallel execution

The normative schedule is serial. After a pre-production pilot and route
certificate, a future child must either retain the exact production $Q$ or
regenerate it byte-identically with the full duplicate bill. It then runs the
immutable base estimator, reaches a source-proved quiescent state, and replays
only the fixed selected rows. For each row it propagates one primal state and
one $J$-tangent state, forms every scalar readout immediately, and releases the
row state. Accumulation follows a frozen row order and binary merge tree. No
$N\times R\times p$ tensor is materialized. If the base source has absorbed
$Q$ into its first-layer coordinates, the child must transport $J$ and every
$a_g$ into exactly the same convention; applying an untransformed
physical-space operator to rotated states is invalid. Every complete post-$Q$
base guard or completion branch must receive the complete frozen correction;
returning uncorrected W0 after observing $Q$ is forbidden.

A conditional two-worker implementation can divide the selected rows into immutable shards. Each worker must compute the primal, shared JVP, dipole terms, and all Fourier terms for its assigned rows. Dividing workers by control family is forbidden because it duplicates the JVP or requires an unsealed derivative cache. Worker completion order may not affect the reduction; serial and parallel modes must use the same leaves and central merge tree and return bitwise-identical outputs.

Parallelism changes the critical path, not the mathematical work. Its accounting must include all workers and the parent:

\[
F_{\mathrm{wave}}=\sum_w F_w+F_{\mathrm{serialization}}
+F_{\mathrm{IPC\_copy}}+F_{\mathrm{hash}}+F_{\mathrm{setup}}
+F_{\mathrm{merge}}+F_{\mathrm{join}}+F_{\mathrm{cleanup}},
\]

\[
T_{\mathrm{wave}}=T_{\mathrm{spawn}}+\max_w T_w
+T_{\mathrm{barrier}}+T_{\mathrm{merge}}+T_{\mathrm{teardown}},
\]

with

\[
F_{\mathrm{total}}=F_{W0}+F_{\mathrm{pilot}}+F_{\mathrm{wave}},
\qquad
T_{\mathrm{total}}=T_{W0}+T_{\mathrm{pilot}}+T_{\mathrm{wave}},
\]

and

\[
RSS_{\mathrm{wave}}=RSS_{\mathrm{parent,quiet}}
+\sum_w RSS_w+RSS_{\mathrm{IPC}}+RSS_{\mathrm{shards}}.
\]

Peak memory is the simultaneous process-tree footprint, not the largest worker
alone. Until the official subprocess and residual-time rules are bound and a
paired receipt demonstrates a strict inclusive gain, $P=1$ remains the only
normative schedule.

## 9. Feasibility boundary

The current work is not a provider implementation and does not complete the
source-contract portion of F0. A source audit found no theorem-level cost kill
for a sparse 64-row sidecar, but it also found no complete upper bound. One
candidate source seam is a descendant estimator that preserves the base files,
retains the exact first production rotation, executes the base provider, and
then performs a serial selected-row primal/JVP replay.

The bound technical proposal records only a rough 0.27–0.54 billion-operation
orientation for the 64-row tangent path, depending on whether primal replay is
required. It excludes Pilot A, production-$Q$ retention or regeneration,
trigonometry, reduction, guards, cleanup, residual time, and RSS. It is neither
a bill nor a budget pass, and the true cost may exceed it.

The provisional inherited ledger leaves a numerical witness margin of about 12.3 billion operations, but the inherited total is not a complete worst-case upper bound and the governing Phase-2 policy is not yet bound. A prior unfused full-node JVP worksheet exceeded the provisional budget even before omitted work. The present family therefore fixes a sparse row subset and must be rejected before execution if its complete success and failure paths, wall time, or aggregate memory lack strict margin.

## 10. Prospective falsification ladder

The first gate is symbolic and synthetic only. It must verify the skew identities in (3), the signs in (4)–(6), the physical-input scale, the weak divergence identity on hand-built continuous piecewise-linear networks, the independence of every pilot object from production $Q$, exact row coverage, one JVP per row, deterministic reduction, and typed accounting for every path. Boundary fixtures must compare one-sided derivatives and an integrated weak identity rather than treating one library's ReLU subgradient at zero as canonical.

Only after that gate survives should the smallest premise panel be considered.
A future F1 manifest must freeze four development networks, one
domain-separated Pilot-A rotation per network, sixteen independent base/control
rotations per network, eight rotations for the coefficient fit, and eight
untouched rotations for evaluation. It must also freeze two dipoles, exactly
four deep axes, the two frequencies above, a 64-row antipodal subset, the
factorial reconstruction, the interval method, and all cost and resource
accounting before values are observed.

The family is killed if the joint arm fails its inclusive cost-weighted variance condition, if either block has nonpositive held partial value, if any source/mean-zero/finite/resource guard fails, if efficacy depends on same-$Q$ adaptation, or if performance reverses beyond a predeclared network-level tail bound. Survival would authorize only a larger paired validation study. It would not itself authorize packaging or submission.

## 11. Limitations and prior evidence

The exact mean-zero identity does not imply useful covariance. The local
[S5 kink](../experiments/s5_kink_concentration/S5_VERDICT.md),
[S15 stratification](../experiments/s15_stratification/S15_VERDICT.md), and
[S18 cell](../experiments/s18_cell_membership_probe/S18_VERDICT.md) screens did
not expose a stable held first-layer geometric signal. The
[M112 connected-gate control](../resources/research_excursions/M112_INDEPENDENT_RESULT_JUDGE_20260807.md)
was killed with a charged pooled variance ratio of about 1.1575. The
[M191 harmonic control](../experiments/pb1_premise_battery/M191_G0B_NOTES.md)
produced a 0.83% reduction with a confidence interval crossing zero against a
10% gate. Complete facet/Crofton estimation was also prohibitively expensive
on its bounded screen. First-layer-only dipole signal is annihilated at low
degree by antipodal complete orthonormal bases. These are strong, family-local
adverse priors for DGFL.

They are not a theorem against the present deep shared-$J$ construction. The narrow hypothesis is that pilot-selected deep input pullbacks identify a low-dimensional rotational error correlated with the structured design, and that odd dipole and even Fourier readouts remove complementary parts of that error while sharing one derivative chain. That hypothesis is currently unmeasured.

Finite implementation introduces further limitations. A seeded float32 QR is not literally Haar distributed; finite-precision divergence evaluations need a numerical bias bound; all post-rotation paths must be total; and guard or fallback behavior can preserve neither exact centering nor the base mean unless explicitly proved. The honest deployed statement is therefore conditional mean preservation in an ideal Haar/real-arithmetic model, followed by numerical and source-level gates for the actual provider.

## 12. Discussion

The useful part of the wave picture is not a claim that weights form a crystal. It is a way to choose structured, differentiable readouts of a piecewise-linear response. The dipole plane supplies an oriented local rotation. Deep gate pullbacks supply candidate phase directions in the physical input space. Fixed cosine modes provide a small Fourier ladder. The rotational Stein identity converts each modulated directional derivative into a known-zero-mean control. Sharing one JVP makes the combined family computationally plausible, and the factorial design tests whether either block contributes after the other at inclusive cost.

This formulation is intentionally modest. It contains one exact identity, one constrained operator family, one implementation hypothesis, and a sequence of tests capable of killing it cheaply. It contains no boundary reconstruction theorem, no transport model, no claim of machine precision, and no result from a generated, held-out, hosted, or contest evaluation.

## 13. Conclusion

The Phase-1 writeup explains the estimator that was built. This companion
isolates one possible successor: a finite bank of rotational-divergence controls
whose dipole and Fourier modulators share one deep JVP. Under an independent
ideal Haar rotation, the correction preserves the base provider's conditional
expectation. Whether it purchases enough held covariance to justify its full
cost is deliberately unresolved. The synthetic mathematical slice has now
passed, but it is not a complete F0. The next legitimate contribution is a
source-only F0 contract; only if that survives should a prospectively frozen F1
premise panel be considered.

## Reproducibility and provenance

The normative incomplete technical proposal is
[`CODEX_DGFL1_DIPOLE_FOURIER_LADDER_PROPOSAL_20260811.md`](../core/CODEX_DGFL1_DIPOLE_FOURIER_LADDER_PROPOSAL_20260811.md), SHA-256
`47F9BD3EF003833900ACCAB8EFD00C85B869553D14A02C46996534CDF6D099BA`.
The incumbent archive and exact source anchors are bound there. The present paper is an explanatory theory manuscript, not an execution manifest; if it conflicts with that proposal, the proposal governs the prospective experiment.

Within the local corpus, first-order sphere-divergence controls and Herglotz/cosine controls have disclosed ancestors. The proposed local differentiator is the factorization of a pilot-frozen deep skew direction with complementary dipole and Fourier readouts sharing one network JVP. No external prior-art search or publication-level novelty claim is made here.
