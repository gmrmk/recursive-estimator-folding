# Sacred geometry, phyllotaxis, and “folded pi”: an honest shortcut audit

**Scope and boundary.**  This is a literature-and-mechanism excursion only.
It does not run WHestBench, generate a contest network, alter a packet,
champion, or ledger, or make a leaderboard claim.  “Campaign evidence” below
means the already-recorded local evidence cited by relative path; it is not
new experimental evidence.

## Bottom line

There is no known identity by which sacred geometry, sunflower repetition, or
a fast formula for the scalar \(\pi\) computes a weight-conditioned deep-ReLU
expectation.  The relevant target is

\[
 \mu(W)=\mathbb E_{X\sim N(0,I_{256})}f_W(X),
\]

where every layer's independently drawn dense \(W_\ell\), and the resulting
input-dependent ReLU gates, are part of the instance.  A legitimate shortcut
must either (i) change the sampling law while retaining a stated bias/unbiased
law, or (ii) reuse an *exact* repeated linear operator with a charged,
shape-aware implementation.  A visually regular point pattern or a fast way
to compute a universal constant establishes neither.

The only two mechanisms below that are both (a) not already directly falsified
as the exact combined operator and (b) honest enough to screen are deliberately
low-prior sampling mutations.  They are not recommendations to replace the
current estimator.  All purported \(\pi\)-arithmetic and generic
tensor/FFT/WHT “folding” shortcuts have no connection to the required
weight-specific integral beyond ordinary implementation details.

## First, disambiguate “newly folded Pi calculation”

Searches of web and arXiv for the exact phrases **“folded Pi calculation,”**
**“folded \(\pi\) algorithm,”** and spelling variants (2026-08-07) found no
recognizable mathematical result bearing that name.  The hits are paper
folding, folded \(\pi\)-electron molecules, or unrelated folded Fourier/
cryptographic objects.  It would be an invention to cite a named “folded pi”
method or infer an associated complexity result.

The closest established, but different, families are:

| Possible intended phrase | Actual classical operator | What it accelerates | Why it is not this integral |
|---|---|---|---|
| Fast \(\pi\) iteration | Gauss--Legendre/AGM and Borwein iterations | A *scalar* constant using arithmetic/geometric means and roots | It knows no \(W\), gate pattern, or 256-dimensional measure. |
| Fast \(\pi\) series | Ramanujan--Chudnovsky hypergeometric series plus binary splitting | High-precision summation of a scalar series | Divide-and-conquer applies when summands have a proven product recurrence, not to changing ReLU regions. |
| Digit extraction | Bailey--Borwein--Plouffe (BBP) base-16 series | Selected hexadecimal digits of \(\pi\) | Random-network expectation is not a digit-extraction problem. |
| “Folded” QMC | dyadic/\(b\)-adic tent (baker) transform | Smooth, non-periodic QMC integrands after a digital-net transform | This is an actual sampling operator, but its higher-order theory has smoothness assumptions strained by inverse-normal tails and ReLU kinks. |
| Folded matrix computation | tensor/Kronecker recursion, FFT/WHT, Strassen-like divide-and-conquer | A repeated transform or specially shaped multiplication | The \(W_\ell\) are heterogeneous and ReLU gates differ per sample and layer; there is no common transform to factor. |

Primary anchors: Chudnovsky & Chudnovsky, *The computation of classical
constants* (PNAS 1989), [doi:10.1073/pnas.86.21.8178](https://doi.org/10.1073/pnas.86.21.8178);
Bailey, Borwein & Plouffe, *On the rapid computation of various polylogarithmic
constants* (Math. Comp. 1997),
[doi:10.1090/S0025-5718-97-00856-9](https://doi.org/10.1090/S0025-5718-97-00856-9);
and Brent, *The Borwein brothers, Pi and the AGM*,
[author copy](https://maths-people.anu.edu.au/~brent/pd/rpb269.pdf).  These
are genuine fast-constant algorithms, not neural expectation algorithms.

## Translate the imagery into the real mathematical objects

### Sunflower/phyllotaxis

The familiar golden-angle point rule is a **two-sphere** construction, e.g.

\[
 z_k=1-\frac{2(k+1/2)}N,\quad
 \theta_k=2\pi k/\varphi^2,\quad
 u_k=(\sqrt{1-z_k^2}\cos\theta_k,
       \sqrt{1-z_k^2}\sin\theta_k,z_k)\in S^2.
\]

It is a useful near-uniform construction on \(S^2\), not a canonical
low-discrepancy design on \(S^{255}\), and it is not a spherical \(t\)-design
merely because it looks uniform.  The relevant primary computer-graphics
reference is Keinert, Innmann, S\u00e4nger & Stamminger, *Spherical Fibonacci
Mapping*, ACM TOG 2015, [doi:10.1145/2816795.2818131](https://doi.org/10.1145/2816795.2818131).
The dimension mismatch is decisive: repeating a 2-D golden spiral in 128
coordinate planes creates a low-dimensional torus orbit, not a 255-dimensional
sphere design.

### “Sacred geometry”

The testable mathematical translations are finite group orbits, Coxeter/root
systems, spherical designs, mutually unbiased bases (MUBs), and code-derived
Kerdock sets.  A spherical \(t\)-design \(D\subset S^{d-1}\) satisfies

\[
 |D|^{-1}\sum_{u\in D}p(u)=\int_{S^{d-1}}p(u)d\sigma(u)
 \quad\text{for every polynomial }p\text{ of degree}\le t.
\]

It does **not** integrate a generic piecewise-linear deep network exactly.
This definition and its cardinality constraints are due to Delsarte, Goethals
& Seidel, *Spherical codes and designs* (1977),
[doi:10.1007/BF03187604](https://doi.org/10.1007/BF03187604).

In this campaign the non-metaphorical version has already been used: the
maximal real MUB/Kerdock construction at \(d=256\) gives 129 bases; after
antipodal closure it is degree-5 exact (the complete MUB union is degree-4
exact and antipodality removes odd terms).  Its 128 non-coordinate bases are
phased Hadamard bases, so their first multiplication admits a WHT.  The
construction is documented from Fuchs et al., *Sketching with Kerdock's
crayons*, Proposition 7, [arXiv:2105.05879](https://arxiv.org/abs/2105.05879),
and locally reconstructed in
[`design8_reconstruction/REPORT.md`](../design8_reconstruction/REPORT.md).
Thus “try a beautiful symmetric design” is not an untested new idea here.

### Exact radial reduction

For bias-free ReLU networks, positive homogeneity gives \(f_W(ru)=r f_W(u)\)
for \(r\ge0\).  Write \(X=RU\), \(U\sim\sigma_{255}\), and
\(R\sim\chi_{256}\) independently.  Then

\[
 \mu(W)=\mathbb E[R]\,\mathbb E_U[f_W(U)].
\]

Fixing the radius to \(\rho_{256}=\mathbb E\chi_{256}\) is therefore an
exact angular Rao--Blackwellization for this target, not a mystical radial
approximation.  It removes only radial noise; it supplies no angular
high-degree information.  This exact reduction, constant-radius construction,
and the \(d=256\) value are already used in the documented Kerdock work
([`design8_reconstruction/REPORT.md`](../design8_reconstruction/REPORT.md)).

### QMC and the real meaning of tent/tau folding

For a randomized digital net, a digital scramble/shift gives each point a
uniform marginal; applying a measure-preserving tent map retains that marginal.
For binary digits, one \(b=2\) form is the digit transformation
\(\eta_i=\xi_{i+1}\mathbin{\mathrm{XOR}}\xi_1\).  Goda, Suzuki & Yoshiki,
*The \(b\)-adic tent transformation for QMC integration using digital nets*,
[arXiv:1312.5850](https://arxiv.org/abs/1312.5850), prove useful rates in
specified smooth Sobolev/RKHS settings.  They do not prove a rate for
\(f_W(\Phi^{-1}(u))\) after 256 inverse-CDF coordinates and many moving ReLU
kink hyperplanes.

Owen's randomized-scrambling result is still useful: a properly scrambled net
is an unbiased randomized rule and has a broad \(L^2\) asymptotic variance
guarantee, but it is not a finite-\(N\), high-dimensional win guarantee:
Owen, *Monte Carlo variance of scrambled net quadrature* (1997),
[doi:10.1137/S0036142994277468](https://doi.org/10.1137/S0036142994277468).

## What the campaign has already paid for or falsified

The following constraints are binding evidence, not invitations to repeat the
same proposal under a poetic name.

1. **The geometry is already a \(d=256\) sphere problem.**  The current family
   uses randomized spherical lines / exact radialization, and Kerdock/MUB
   degree-5 geometry was reconstructed and tested.  The full-129 design was
   not automatically better; the 126-base fold-3 realization exceeded budget.
   See [`design8_reconstruction/REPORT.md`](../design8_reconstruction/REPORT.md).

2. **Kerdock symmetry and a WHT were already exploited.**  Its first layer can
   be formed by phase multiplication plus WHT, without materializing a
   32,256-by-256 direction matrix.  That is exactly the repeated-operator
   opportunity sacred-geometry rhetoric commonly gestures toward.  The
   faithful L2 path nevertheless measured 415.521B analytic FLOPs plus 3.922s
   residual (807.727B effective), so it is not a free algebraic compression.
   Same source.

3. **The remaining angular error is not a low-degree design defect with an
   easy fixed axis.**  A degree-6/8 JSpace-Gram control had small features but
   only 0.0506 design-error correlation and 21.0923x cost-adjusted variance;
   it failed every fresh case.  See
   [`jspace_gram_aligned_control/REPORT.md`](../jspace_gram_aligned_control/REPORT.md).
   The current targeted, weights-only degree-4/6/8 harmonic-control premise is
   properly a separate, cross-fitted proposal, not evidence that more geometry
   itself is a solution; see
   [`M107_SPHERICAL_CONTROL_THEORY_20260807.md`](M107_SPHERICAL_CONTROL_THEORY_20260807.md).

4. **Effective dimension stays high where it matters.**  The campaign's
   Jacobian diagnostics report gate-dependent active subspaces that tumble
   across inputs rather than one reusable global active subspace
   ([`cleanroom_whitebox_redteam/README.md`](../cleanroom_whitebox_redteam/README.md)).
   Even an 89.5%-energy matrix SVD flipped 15--19% of gates and left 58--95%
   of final correction variance in one audited route
   ([`DEFINITIVE_SOLVE_20260806.md`](../DEFINITIVE_SOLVE_20260806.md)).
   That is adverse to a one-dimensional golden orbit or a low-rank repeated
   operator explanation.

5. **QMC/tent regularity is especially strained.**  Existing notes already
   identify inverse-normal endpoint behavior and deep-ReLU kink hyperplanes as
   violations or stresses of the smoothness assumptions behind the strongest
   folded-net rates ([`sources/fringe-physics-biology-research.md`](../../../sources/fringe-physics-biology-research.md)).
   Public QMC disclosures were useful but modest (about 1.4x lattice gain on
   one reported pipeline), and neither proves a new asymptotic rate here;
   see [`sources/research_top_method_forensics_20260803.md`](../../../sources/research_top_method_forensics_20260803.md).

6. **Multiplication has a billed shape, not a symbolic FLOP count.**  The
   exact structural-compression audit found that extra sum/stack/concatenate
   and multiple visible matmul calls made recursive products lose once
   residual time was charged.  One representative direct product carried a
   12.205B effective proxy; no shape in the measured \(k,n\le256\) grid was
   improved by the dispatched alternative.  See
   [`exact_sampler_compression/REPORT.md`](../exact_sampler_compression/REPORT.md).
   Tensor/FFT/WHT recurrences are therefore candidates only when they preserve
   an exact operator *and* beat the fully billed direct operand shape.

7. **Weights and gates destroy naive repeated-operator compression.**  The
   dense \(W_\ell\) are heterogeneous.  After each ReLU the sample-specific
   diagonal gate changes the next effective map.  Except for a demonstrated
   first-layer Kerdock/Hadamard factorization, a proposed shared transform
   must show exact equivalence through those changing diagonals, then pay all
   packing, transforms, temporaries, and residual time.  “The sunflower is
   self-similar” is not such a proof.

## Two still-honest, generated-only falsifiers

These are the **only** new operators retained by this excursion.  They are
sampling hypotheses, not analytic closures or cost-compression claims.  Each
must use predeclared seeds and a fresh generated-only cleanroom gate before
any target-scale work.  No fitting to contest outputs is permitted.

### A. Scrambled Sobol + dyadic tent + exact spherical radialization

**Exact operator.**  Let \(P=2^m\), draw an Owen-scrambled Sobol net
\(\{U_i\}_{i=1}^P\subset[0,1)^{256}\), and use the coordinatewise tent map
\(T(u)=1-|2u-1|\) (or the precisely implemented digitwise \(b\)-adic map,
not both ambiguously).  Put

\[
 Z_i=\Phi^{-1}(T(U_i)),\quad
 V_i=Z_i/\|Z_i\|_2,\quad
 \widehat\mu_A(W)=\rho_{256}\frac1P\sum_{i=1}^P f_W(V_i),
 \qquad \rho_{256}=\mathbb E\chi_{256}.
\]

Add antipodes by evaluating \(\pm V_i\) and averaging if the path budget is
counted as \(2P\).  The all-zero event has probability zero under the
continuous randomized construction; a finite-precision implementation must
document an endpoint/midpoint convention rather than silently clip.

**Law and bias class.**  Conditional on \(W\), each scrambled point is
uniform on the cube.  A measure-preserving tent map remains uniform; hence
\(Z_i\sim N(0,I)\), \(V_i\sim\sigma_{255}\) marginally, and exact radialization
gives an **unbiased randomized estimator**.  Dependence between points is
intentional.  The claim is unbiasedness, *not* an \(o(P^{-1})\) finite-sample
variance promise.  This combined spherical/tent mapping has not been given a
direct local falsifier, but Sobol/lattice QMC and radial/spherical designs have
each been separately explored, so its prior is low.

**Billed complexity.**  Sampling/normalization costs \(O(Pd)\), plus an
inverse-normal implementation; propagation remains \(O(P\sum_\ell n_{\ell-1}
n_\ell)\) elementwise and \(O(P\sum_\ell n_{\ell-1}n_\ell)\) dense work.  It
does not create a WHT factorization.  Charge net generation/asset loading,
tent, inverse CDF, norms, antipodal paths, all matrix products, and residual
time.  It can only win if its variance reduction at *equal complete cost*
beats more paths of the current sampler.

**Predicted signature.**  If the mechanism is real, the tented rule has a
stable below-one variance-times-cost ratio versus equally budgeted scrambled
Sobol *and* randomized spherical-frame baselines, across independent
scrambles and generated networks.  It should not appear only after a chosen
scramble or only on smooth first-layer observables.

**Cheapest generated-only falsifier.**  Before a depth-32 run, use fixed
independent scrambles at \(d=256\) to estimate the known spherical moments
\(\mathbb E(a^TU)^{2r}\), \(r=1,2,3,4\), for predeclared random axes, then
compare block variance with equal-cost scrambled Sobol and spherical frames.
Next, on eight fresh generated width-64/depth-8 bias-free ReLU networks,
compare antithetic \(2P\)-path estimates against a streamed high-precision
reference, with network as the resampling unit and no coefficient tuning.

**Hard kill.**  Kill this exact operator if it has a nonfinite/endpoint or
moment-law defect; or if the paired one-sided 95% upper confidence bound for
its geometric mean variance-times-cost ratio is \(\ge1\), or fewer than six
of eight networks improve, or any network exceeds 1.10.  Do not rescue it by
changing net, tent convention, inverse-CDF approximation, or dimension after
the gate.

### B. Haar-shifted phyllotactic torus orbit on \(S^{255}\)

This is the most charitable rigorous reading of “sunflower repetition.”  It
is intentionally presented as a falsifier, not as an expected improvement.

**Exact operator.**  Split \(\mathbb R^{256}\) into 128 coordinate planes.
Choose fixed \(u\in S^{255}\) with \(\|u_{2j-1:2j}\|_2^2=1/128\).  Let
\(R(\theta)\) be a planar rotation, choose frozen irrational frequencies
\(\omega_j=\{j/\varphi\}\), and define

\[
 D(t)=\operatorname{diag}\bigl(R(2\pi t\omega_1),\ldots,
 R(2\pi t\omega_{128})\bigr),\quad
 V_k=Q_0D(k/\varphi)u,
\]

where \(Q_0\sim\mathrm{Haar}(O(256))\) is drawn independently per replicate.
Estimate with \(\rho_{256}[f_W(V_k)+f_W(-V_k)]/2\), averaged over \(k=0,
\ldots,P-1\).

**Law and bias class.**  For every fixed \(k\), Haar left invariance makes
\(V_k\) uniform on \(S^{255}\); therefore the rule is **unbiased over the
Haar seed** after exact radialization.  The \(P\) directions are *not*
independent and occupy a one-parameter orbit of a 128-torus before the common
rotation.  There is no claim of spherical-design strength, low discrepancy on
\(S^{255}\), or QMC convergence rate.

**Billed complexity.**  A naive formation costs \(O(d^3)\) for Haar QR plus
\(O(Pd)\) phase generation and \(O(Pd^2)\) first-layer propagation (or one
charged rotation of \(W_1\) plus the same dense products).  Later layers are
unchanged.  Unlike Kerdock phases, these directions do not turn the first
product into a Walsh transform; trigonometric generation, QR, and any cached
rotation must be included in the cost trace.

**Predicted signature.**  Its only plausible signature is lower frame-block
variance for a genuinely low-dimensional rotational Fourier component of
\(f_W\), consistently across independently Haar-shifted replicates.  Given
the observed tumbling gate subspaces and degree-6+ residual, the stronger
prediction is excess variance, anisotropic degree-6 moments, and no
equal-cost gain.

**Cheapest generated-only falsifier.**  Do not begin with an MLP.  At
\(d=256\), compare the orbit's replicate variance on the known harmonics
\(P_4(a^Tv),P_6(a^Tv),P_8(a^Tv)\) against equal-count Haar frames, random
spherical lines, and Kerdock blocks, across eight predeclared \(Q_0\)'s and
axes.  Then, only if it is not dominated, perform the same eight-network
width-64/depth-8 equal-cost screen as A.

**Hard kill.**  Kill if any required marginal/moment check fails; or if the
median degree-6 harmonic variance is no lower than the randomized-frame
baseline, or the equal-cost ReLU variance gate is not passed.  A single
visually attractive orbit, selected frequencies, or a lucky Haar rotation is
not evidence and cannot be retained.

## Explicitly rejected translations

- **AGM/Borwein/BBP/binary splitting:** retain only as possible ways to
  evaluate a scalar special function already required by a proved estimator.
  They cannot reduce the number of weight-specific gate regions or matrix
  products.  No experiment is warranted absent an actual scalar bottleneck.

- **Coxeter/root-system/MUB/Kerdock substitution:** already represented by
  the Kerdock/MUB construction.  A new root system must first prove its
  spherical moments and then beat Kerdock/random frames at the same sample
  count and fully billed cost; symmetry alone is no novelty.

- **Higher-strength deterministic spherical design:** a degree-6/7 ambition
  is not a cheap patch.  Design cardinality constraints grow rapidly with
  dimension (Delsarte--Goethals--Seidel); even if a construction exists, it
  must confront the present degree-6+ residual, path cost, and absent WHT
  factorization.  The prior JSpace control failure also says that merely
  observing a high-degree geometric feature did not correlate with the actual
  design error.

- **Tensor-product/FFT/WHT recursion:** WHT is already used where its
  Kerdock/Hadamard hypothesis is exact.  A tensor product across layers would
  require repeated compatible factors across heterogeneous \(W_\ell\) and
  gate matrices \(\operatorname{diag}(1_{h_\ell>0})\); those factors are not
  present.  Recursive matrix multiplication was specifically falsified under
  the actual operand shapes and residual billing.

## Decision

The honest answer is **no discovered sacred-geometry or folded-\(\pi\)
shortcut** for deep ReLU expectation/weight calculations.  The campaign has
already exhausted the literal geometric symmetry/WHT avenue far more deeply
than the metaphors suggest.  Candidate A is a narrowly specified, unbiased
QMC mutation whose smoothness rationale is weak but testable.  Candidate B is
the most faithful mathematical version of phyllotaxis and is more valuable as
a fast rejection test than as a contender.  Neither supplies an analytic
closure, avoids the 256-dimensional angular problem, or makes heterogeneous
gated dense products disappear.

### Primary-source links

1. Delsarte, Goethals & Seidel (1977), *Spherical codes and designs*:
   [doi:10.1007/BF03187604](https://doi.org/10.1007/BF03187604).
2. Fuchs, Gross, Krahmer, Kueng & Mixon (2021), *Sketching with Kerdock's
   crayons*: [arXiv:2105.05879](https://arxiv.org/abs/2105.05879).
3. Owen (1997), *Monte Carlo variance of scrambled net quadrature*:
   [doi:10.1137/S0036142994277468](https://doi.org/10.1137/S0036142994277468).
4. Goda, Suzuki & Yoshiki (2014), *The \(b\)-adic tent transformation for
   quasi-Monte Carlo integration using digital nets*:
   [arXiv:1312.5850](https://arxiv.org/abs/1312.5850).
5. Keinert, Innmann, S\u00e4nger & Stamminger (2015), *Spherical Fibonacci
   mapping*: [doi:10.1145/2816795.2818131](https://doi.org/10.1145/2816795.2818131).
6. Chudnovsky & Chudnovsky (1989), *The computation of classical constants*:
   [doi:10.1073/pnas.86.21.8178](https://doi.org/10.1073/pnas.86.21.8178).
7. Bailey, Borwein & Plouffe (1997), *On the rapid computation of various
   polylogarithmic constants*:
   [doi:10.1090/S0025-5718-97-00856-9](https://doi.org/10.1090/S0025-5718-97-00856-9).

