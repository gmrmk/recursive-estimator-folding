# Cymatic/physics harmonic mutations for WHestBench

**Date:** 2026-08-07  
**Status:** theory and generated-only gate design; nothing executed  
**Protected artifacts:** M107, champions, packets, and ledgers are unchanged

## Decision

Cymatics has one rigorous translation here: a Chladni figure is a nodal pattern
of a normal mode, and normal modes on the post-radialization sphere are
spherical harmonics.  Heat, Helmholtz, and wave equations supply fixed
spectral multipliers of those modes.  They do not create a new recurrence
through heterogeneous ReLU layers.

Three descendants are mathematically lawful enough to falsify:

1. a fixed even heat-difference bandpass centered at degree 18;
2. an output-specific, positive-gauge-invariant signed mean-Jacobian weighting
   of first-layer bandpass zonals, retained in its rank-\(K\) Hutchinson form;
3. a centered squared band-energy control, the closest exact analogue of
   Chladni antinode intensity.

The third is the only **truly new god-edge candidate** found in this
excursion: if \(B_a\) is a unit-variance, zero-mean spherical band mode, then
\(B_a^2-1\) is another exact-zero control.  It can reveal a magnitude/energy
link even when the signed mode cancels, and costs only a square and reduction
once the band mode exists.  This is an identity, not evidence of useful
correlation.  Its prior remains low because the earlier needlet proposal had
no demonstrated spatial localization and every JSpace-aligned high-degree
control was adverse.

The requested “residual median near degree 18” was supplied as a premise for
this mutation.  No provenance-linked degree-spectrum artifact with that
median was found in the searched campaign files.  Degree 18 is therefore a
**frozen hypothesis to test**, not a restated campaign measurement.  It must
not be moved after generated outcomes.

## Boundary inherited from M107

For \(d=256\), write \(X=RU\), where \(U\) is uniform on
\(S^{255}\), \(R\sim\chi_{256}\), and \(R\perp U\).  A bias-free ReLU
network is positively homogeneous, so for fixed weights \(W\),

\[
  \mu(W)=\mathbb E_X f_W(X)
        =\rho_{256}\,\mathbb E_U f_W(U),
  \qquad \rho_{256}=\mathbb E\chi_{256}.
\]

All controls below are angular and have known zero surface mean.  An
output-fitted coefficient is unbiased only when fitted from frames independent
of the frame on which it is applied.  Formal L1 has independent Haar frames,
so frame-block cross-fitting is available.  M71's Kerdock bases share one Haar
rotation; holding out a basis is not an independent fold.  None of the
following borrows an M71 cross-fit proof.

[`M107_SPHERICAL_CONTROL_THEORY_20260807.md`](M107_SPHERICAL_CONTROL_THEORY_20260807.md)
remains immutable.  Its corrected first-layer convention is used:
the forward map is \(xW_1\), the gate normals are the nonzero columns
\(w_j=W_1[:,j]\), and

\[
  a_j=w_j/\lVert w_j\rVert_2,
  \qquad t_{sj}=a_j^Tu_s
       ={\texttt{first\_pre}_{sj}\over \rho_{256}\lVert w_j\rVert_2}.
\]

Thus a formal-L1 implementation can reuse the already formed first-layer
preactivation.  No candidate may bill a fictitious extra \(U W_1\), and no
other sampler may claim this reuse without the same identity.

## What the physics actually says

### Laplace--Beltrami, Helmholtz, heat, and wave modes

The degree-\(\ell\) spherical-harmonic space \(\mathcal H_\ell\) is an
eigenspace of the round-sphere Laplace--Beltrami operator:

\[
  -\Delta_{S^{d-1}}Y_{\ell m}
   =\lambda_\ell Y_{\ell m},
  \qquad \lambda_\ell=\ell(\ell+d-2).
\]

The Helmholtz equation selects one eigenspace.  Heat evolution multiplies it
by \(e^{-t\lambda_\ell}\); wave evolution multiplies it by sinusoidal
functions of \(\sqrt{\lambda_\ell}\).  Zhao and Song give the exact
hyperspherical heat kernel as an absolutely convergent Gegenbauer/eigenmode
series: [doi:10.3389/fams.2018.00001](https://doi.org/10.3389/fams.2018.00001),
[arXiv:1702.01373](https://arxiv.org/abs/1702.01373).

Those are diagonal spectral operators on functions of \(u\).  They are not a
claim that the deep network itself obeys a heat or wave equation.

The three relevant fixed degree multipliers can be written without analogy.
Let \(\lambda_{18}=4896\).  Before normalization or restriction to the frozen
even band, they are:

| operator | channel multiplier \(m_\ell\) | degree-18 calibration |
|---|---|---|
| heat difference | \(e^{-t_1\lambda_\ell}-e^{-2t_1\lambda_\ell}\) | \(t_1=\log 2/\lambda_{18}\), so its continuous-\(\lambda\) peak is \(\lambda_{18}\) |
| Poisson/Laplace extension difference | \(r_1^\ell-r_1^{2\ell}\) | \(r_1=2^{-1/18}\), so its continuous-degree peak is \(\ell=18\) |
| Helmholtz shell | \(\mathbf1_{\ell=18}\) | \((-\Delta_{S^{255}}-\lambda_{18})q_{18}(a^T\cdot)=0\) |

For the Poisson row, a degree-\(\ell\) boundary harmonic extends into the unit
ball with factor \(r^\ell\); the point-source Poisson kernel therefore has a
Gegenbauer series with those multipliers.  Iglewska-Nowak derives the
hyperspherical Poisson-kernel expansion and its differentiated wavelets:
[doi:10.1007/s00041-014-9366-x](https://doi.org/10.1007/s00041-014-9366-x),
[preprint](https://arxiv.org/abs/1803.03118).  Each displayed multiplier has
zero degree-0 multiplier.  Consequently, restricting it to positive even
degrees, expanding in \(q_\ell\), and normalizing its coefficient vector gives
an exact-zero unit-variance zonal by the addition theorem.  Candidate A freezes
the heat row only.  The Poisson and exact Helmholtz rows are recorded controls,
not post-failure replacements or extra multiple-comparison cells.

### Chladni patterns

A vibrating plate has domain- and boundary-dependent flexural normal modes;
the visible sand pattern follows their nodal sets.  Bardell's analytical
study, for example, computes plate eigensolutions by a Ritz/Legendre method and
compares their nodal patterns with experiments:
[doi:10.1006/jsvi.1994.1300](https://doi.org/10.1006/jsvi.1994.1300).
The transferable idea is therefore **mode amplitude or mode energy**, not the
shape of a literal metal plate.  WHestBench's angular domain is \(S^{255}\),
not a two-dimensional plate with a biharmonic boundary-value problem.

### Needlets and wavelets

Narcowich, Petrushev, and Ward construct localized tight frames on spheres
from smooth spectral cutoffs and positive spherical quadrature:
[doi:10.1137/040614359](https://doi.org/10.1137/040614359).  This licenses the
mathematical idea “compact harmonic band + spatial center.”  It does not make
the 256 first-layer normals a needlet quadrature grid.  The candidates below
are therefore called **needlet-style zonal wavepackets**, not certified tight
frames.

### Transfer matrices and normal modes

For a fixed linear oscillator \(M\ddot q+Kq=0\), normal modes diagonalize one
fixed generalized eigenproblem.  A transfer matrix can propagate the same
linear state repeatedly.  A ReLU chain instead has effective sample-dependent
maps

\[
  W_1D_1(u)W_2D_2(u)\cdots,
\]

with unrelated dense \(W_\ell\) and changing gates \(D_\ell(u)\).  There is
no fixed normal-mode basis or repeated transfer matrix across depth.  The only
exact transfer recurrence used here is the scalar Gegenbauer recurrence for
evaluating a spherical control.  Quantum Hamiltonians, partition functions,
and phonon language add no further operator, so they are omitted.

## A stable exact recurrence through degree 32

Let

\[
 P_\ell(t)={C_\ell^{(d-2)/2}(t)\over
 C_\ell^{(d-2)/2}(1)},\qquad
 N_\ell={ (2\ell+d-2)(\ell+d-3)!\over
                \ell!(d-2)!}.
\]

M107 uses the normalized recurrence

\[
 P_{\ell+1}(t)=A_\ell tP_\ell(t)-B_\ell P_{\ell-1}(t),\quad
 A_\ell={2\ell+d-2\over \ell+d-2},\quad
 B_\ell={\ell\over \ell+d-2}.
\]

At degree 18 in \(d=256\), \(N_{18}=6.2233387287131023033645308\times
10^{27}\).  Typical raw \(P_{18}\) values are consequently tiny.  Blindly
multiplying by \(\sqrt{N_{18}}\) after a cancellation-prone float32 recurrence
is not acceptable.

Instead propagate the orthonormal-scaled zonal

\[
 q_\ell(t)=\sqrt{N_\ell}\,P_\ell(t),\qquad
 q_0=1,\quad q_1=\sqrt d\,t.
\]

With

\[
 r_\ell={N_{\ell+1}\over N_\ell}
 = {2\ell+d\over2\ell+d-2}{\ell+d-2\over\ell+1},
\]

the exact recurrence, for \(\ell\geq1\), is

\[
 \boxed{q_{\ell+1}
 =A_\ell\sqrt{r_\ell}\,tq_\ell
 -B_\ell\sqrt{r_\ell r_{\ell-1}}\,q_{\ell-1}.}
\]

It can be written as a degree-dependent \(2\times2\) transfer matrix, but the
matrix changes with \(\ell\), so exponentiation or FFT rhetoric does not
shorten it.  A Clenshaw evaluation of a fixed linear combination has the same
\(O(L_{\max})\) arithmetic and two live recurrence states.

The addition theorem gives, for fixed unit axes \(a,b\),

\[
 \mathbb E_U q_\ell(a^TU)=0\quad(\ell>0),\qquad
 \mathbb E_U[q_\ell(a^TU)q_{\ell'}(b^TU)]
 =\mathbf1_{\ell=\ell'}P_\ell(a^Tb).
\]

In particular, \(q_\ell(a^TU)\) has variance one.  These identities supply
the exact-zero laws below.  The recurrence coefficients are grounded in the
standard Gegenbauer recurrence (NIST DLMF
[§18.9](https://dlmf.nist.gov/18.9)); the spherical addition theorem and
harmonic normalization are the same identities used in M107.

Numerical certification is still mandatory: float64 recurrence versus a
100-bit reference for a fixed grid of \(t\), forward/backward recurrence
agreement, parity, Haar moments, and a material-excursion rather than silent
clipping policy.

## Campaign evidence that constrains all three candidates

- Formal L1 averages independent Haar frames; complete frames kill degree 2
  but not degree 4.  M107 therefore correctly froze degrees 4/6/8, uniform and
  squared-path-energy mixtures, and independent frame folds.  This excursion
  is a later alternative, not a mutation of that gate.
- The complete real MUB/Kerdock union with antipodes is a spherical 5-design,
  and its phased Hadamard structure already uses a WHT.  The remaining error
  begins at degree 6 for that design, but formal L1 and M71 are distinct
  samplers.  See
  [`design8_reconstruction/REPORT.md`](../design8_reconstruction/REPORT.md).
- The JSpace branch is severe negative evidence.  On its fresh bank,
  \(\|EJ\|_F^2/E\|J\|_F^2\) had median 0.1028, showing signed cancellation.
  The later exact-mean degree-6/8 control had design-error correlations 0.0172
  for signed mean-J and 0.0506 for the second-moment Gram; every control lost
  on every network.  See
  [`jspace_workspace_adapter/REPORT.md`](../jspace_workspace_adapter/REPORT.md)
  and
  [`jspace_gram_aligned_control/REPORT.md`](../jspace_gram_aligned_control/REPORT.md).
  Candidate B changes the edge—gate normals are retained as centers and the
  signed Jacobian becomes output weights—but it does not erase this prior.
- The earlier M25 generic needlet proposal was judged redundant absent
  demonstrated spatial localization; see
  [`terra_moonshot_judge2/REPORT.md`](../terra_moonshot_judge2/REPORT.md).
  Candidate C's squared band energy is the new observable that avoids merely
  renaming that proposal.
- A candidate is judged by measured variance times **complete billed cost**.
  The current formal champion's public-100 mean effective compute is 189.853B;
  its observed worst case leaves 35.995B below the conservative safety line; see
  [`CHAMPION_20260806.md`](../CHAMPION_20260806.md).  No analytic scalar count
  can spend that headroom before a FlopScope/resource trace.

## Candidate A — fixed degree-18 heat-difference bandpass

### Exact operator and law

For \(d=256\), \(\lambda_{18}=18(18+254)=4896\).  Freeze

\[
 t_1={\log 2\over4896}=1.41574179035937\times10^{-4},\qquad
 t_2=2t_1,
\]

and the even band \(\mathcal L=\{8,10,\ldots,32\}\).  The heat-difference
spectral multiplier

\[
 b_\ell=e^{-t_1\lambda_\ell}-e^{-t_2\lambda_\ell}
\]

peaks as a function of continuous \(\lambda\) at \(\lambda_{18}\).  Define
\(c_\ell=b_\ell/(\sum_{r\in\mathcal L}b_r^2)^{1/2}\) and

\[
 B_a(u)=\sum_{\ell\in\mathcal L}c_\ell q_\ell(a^Tu),qquad
 H_A(u;W)=|\mathcal J|^{-1/2}\sum_{j\in\mathcal J}B_{a_j}(u).
\]

This is a **truncated, orthonormal-channel heat-difference bandpass**, not the
literal point-source heat kernel, whose coefficients also contain harmonic
multiplicities.  The distinction prevents a false “exact heat kernel” label.

Because no degree-zero term is present,

\[
 E_U B_a(U)=E_UH_A(U;W)=0,
 \qquad E_UB_a(U)^2=\sum c_\ell^2=1.
\]

Thus a fixed coefficient, a weights-only coefficient, or an independently
cross-fitted output coefficient preserves conditional unbiasedness.  The
finite truncation introduces no integration bias; it only changes which
zero-mean control is offered.

### Invariance

The uniform sum is invariant to a first-hidden-neuron permutation.  Under an
orthogonal input change, \(a_j\) and \(u\) rotate together and every dot
product is unchanged.  Even degrees make each axis an unoriented line and
match antipodal sampling.  Positive rescaling of a first hidden unit leaves
\(a_j\) unchanged.  Exact zero columns are excluded; an empty set is a hard
failure.

### Billed recurrence and cost

Reuse each block's first preactivation to obtain all \(t_{sj}\).  Stream the
scaled recurrence to degree 32 with two recurrence buffers and accumulate only
the 13 even band terms.  After \(t,q_0,q_1\) are formed, and counting one
scalar multiply or add as one operation,
each recurrence update has three multiplies and one subtraction, and each
selected degree has one multiply and one accumulation.  For \(S=32,256\)
spherical lines and \(|\mathcal J|=256\), the recurrence-plus-band arithmetic is

\[
 4S|\mathcal J|(31) + 2S|\mathcal J|(13)
 =1{,}238{,}630{,}400\text{ scalar operations},
\]

plus norms, divisions, validation, and reductions.  This is not a FlopScope
bill: dispatch granularity, block temporaries, float64 support, and residual
time must be measured.  A row-block implementation needs only the current
first-pre block, two recurrence blocks, and one accumulator; retaining a full
\(S\times256\times32\) tensor is forbidden.

### Predicted signature

If the supplied degree-18 prior is causal, the band feature's **frame-block
error** should correlate more strongly with the output integration error than
M107's individual degrees 4/6/8, and the same frozen filter should help across
networks.  A pointwise fit with no held-frame gain is not the signature.

### Failure localization and reasons it may fail

- Held correlation near zero: the degree prior or the first-layer centers are
  unobservable, not a heat-kernel implementation failure.
- Good oracle correlation but no cross-fitted gain: coefficient noise or too
  few independent frames.
- Raw gain but cost-adjusted loss: the recurrence is real but more base paths
  dominate it.
- Degree-18 gain only after moving \(t_1,t_2\), endpoints, or band: spectral
  fishing; invalidate the branch.
- High-precision agreement but float64 failure: numerical cancellation at
  high degree; do not claim a physics failure.

The likely scientific failure is broad/tumbling residual energy rather than a
stationary degree band.  A heat multiplier is isotropic and cannot infer an
instance-specific angular phase.

### Cheapest generated-only gate and hard kill

First use no MLP: verify parity, zero Haar mean, unit single-axis variance,
input covariance, hidden permutation invariance, and recurrence agreement for
predeclared axes and Haar frames in \(d=256\).  Then use eight fresh generated
width-64/depth-8 bias-free networks, independent frame-block coefficient and
held pools, and compare no control, the frozen M107-low-degree feature bank,
and A at equal total measured cost.

Kill A if any law/invariance/numerical check fails; or if median absolute
held-frame error correlation is below 0.25; or if fewer than six of eight
networks improve; or if the one-sided 95% upper bound on the geometric mean
variance-times-cost ratio is at least 0.85; or any network exceeds 1.10.  No
degree/time/band retune follows a failure.

## Candidate B — low-rank output-specific signed mean transfer

### Exact operator and law

Let the final observable be \(f_W(u)\in\mathbb R^p\), and let

\[
 J_1(u)={\partial f_W(u)\over\partial h_1(u)}\in\mathbb R^{p\times n}
\]

be its signed downstream transfer from first-layer preactivations.  On a pilot
\(v_1,\ldots,v_P\) independent of the held frames, use \(K\) Rademacher output
probes \(z_k\in\{\pm1\}^p\).  For the benchmark convention
\(h_\ell=y_{\ell-1}W_\ell\), \(y_\ell=\operatorname{ReLU}(h_\ell)\), set
\(D_\ell(v)=\operatorname{diag}(\mathbf1_{h_\ell(v)>0})\), with zero chosen at
an exact tie.  The exact signed-path reverse recurrence is

\[
 g_L^{(k)}(v)=D_L(v)z_k,\qquad
 g_\ell^{(k)}(v)=D_\ell(v)W_{\ell+1}g_{\ell+1}^{(k)}(v),
 \quad \ell=L-1,\ldots,1,
\]

and \(r_k(v_i)=g_1^{(k)}(v_i)=J_1(v_i)^Tz_k\).  Write
\(\bar J_{1,P}=P^{-1}\sum_iJ_1(v_i)\) and
\(\bar r_k=P^{-1}\sum_i r_k(v_i)=\bar J_{1,P}^Tz_k\).  Then

\[
 \widehat{\bar J}_{1,P}={1\over K}\sum_{k=1}^Kz_k\bar r_k^T,
 \qquad E_z[\widehat{\bar J}_{1,P}\mid v_{1:P}]=\bar J_{1,P},
 \qquad E_{v,z}\widehat{\bar J}_{1,P}=E_UJ_1(U).
\]

Define the hidden-by-output invariant weight matrix

\[
 \Gamma={1\over K}\operatorname{diag}(\lVert w_j\rVert_2)
 [\bar r_1\cdots\bar r_K][z_1\cdots z_K]^T
\]

and, using the same frozen band \(B\) as A,

\[
 \Psi_{sj}=B_{a_j}(u_s),\qquad H_B(U;W)=\Psi(U)\Gamma\in\mathbb R^p.
\]

Conditional on \(W\), probes, and the independent pilot, every column of
\(\Psi\) has zero sphere mean, hence

\[
 E_U[H_B(U;W)\mid W,\text{pilot},z]=0.
\]

The Hutchinson approximation changes the control's variance but **not its
zero-mean law**.  A diagonal output coefficient learned from a second
independent pool and applied to held frames remains unbiased by the same
cross-fit argument as M107.

### Why the norm factor matters: exact positive-gauge invariance

Under the hidden-unit gauge
\(w_j\mapsto c_jw_j\), \(c_j>0\), and the corresponding downstream row
\(W_2[j,:]\mapsto W_2[j,:]/c_j\), the network is unchanged.
Then \(\lVert w_j\rVert\mapsto c_j\lVert w_j\rVert\) while the derivative
with respect to \(h_{1j}\) scales by \(1/c_j\).  Their product in \(\Gamma\)
is invariant.  Omitting the norm would make the alleged “physical coupling”
depend on an arbitrary neuron gauge.

The construction is input-orthogonally covariant and hidden-permutation
invariant because axes, norms, and VJP coordinates transform together.  With
the full, non-Hutchinson \(\bar J_{1,P}\), output permutations are pointwise
covariant.  With finite
iid Rademacher probes, output covariance holds in distribution; a fixed probe
matrix must not be advertised as pointwise output-permutation equivariant.

### Exact low-rank application and billed cost

Do not materialize a dense \(n\times p\) \(\Gamma\).  Retain

\[
 H_B={1\over K}
  [\Psi\operatorname{diag}(\lVert w\rVert)R]Z^T,
 \quad R=[\bar r_1\cdots\bar r_K],\quad Z=[z_1\cdots z_K].
\]

At \(S=32,256\), \(n=p=256\), and \(K=4\), the two-FLOP-MAC count for the
two thin products is about
\(4S\,256\,K=0.132\)B, after the shared band recurrence.  For a constant-width
all-ReLU depth-\(L\) network, one scalar implementation of the displayed VJP
recurrence uses \(n+2(L-1)n^2\) multiply/add operations per pilot state and
probe: each dense matvec uses \(n^2\) multiplies and \(n(n-1)\) additions, and
its gate uses \(n\) multiplications.  Thus \(P=128,K=4,L=32,n=256\) has a
2,080,505,856-operation VJP arithmetic core.  The corresponding pilot forward
core is 535,822,336 multiply/add operations before ReLU comparisons.  These
analytic cores are consistent with, but do not replace, the prior JSpace
target-shape estimate of 2.813B operations: B requires its own first-hidden
streaming, memory, and residual trace.  Charge pilot forwards, gate retention
or replay, every VJP, probe formation, averaging, band recurrence, both thin
products, coefficient fit, and independent held frames.

### Predicted signature

The signed output columns should flip/covary with the corresponding output
path transfer and yield materially higher held-frame error correlation than
uniform or nonnegative squared-path mixtures.  A real win is output-specific:
different outputs favor different signed neuron combinations while the same
band and pilot protocol remain frozen.

### Failure localization and reasons it may fail

- \(\|EJ\|^2/E\|J\|^2\) remains small: gate tumbling cancels the signed
  transfer; this repeats the known JSpace mechanism.
- Stable \(\bar J\), null held error correlation: the transfer describes
  sensitivity but not randomized-integration error, the previously killed
  JSpace link.
- Full-rank oracle works, \(K=4\) fails: Hutchinson rank/noise failure; the
  exact oracle is not deployable evidence and does not authorize \(K\) tuning.
- Feature gain disappears after multiplying by \(\lVert w_j\rVert\): the
  apparent gain was gauge-dependent and inadmissible.
- Thin application wins arithmetically but VJP pilot loses on cost: offline
  diagnostic only.

The strongest reason to expect failure is already measured: signed mean-J
directions had only 0.0172 design-error correlation and 9.1184x raw variance
in the completed JSpace control rung.  B is a changed observable, not a clean
prior.

### Cheapest generated-only gate and hard kill

On eight fresh width-64/depth-8 networks, freeze \(K=4\), a pilot-frame pool,
a coefficient-frame pool, and held independent frames.  Compare, on the
identical A band, uniform weights, M107's normalized squared-path weights, B's
signed mean-transfer weights, and a sign-erased \(|\Gamma|\) causal ablation.
Verify VJP orientation at tiny width, gauge invariance, hidden permutation,
input covariance, output covariance in distribution, zero held mean, and
rank-\(K\) dense/factored equivalence.

Kill B if any exact test fails; if signed-transfer median design-error
correlation is below 0.30; if it does not beat both uniform and sign-erased
cells; if fewer than seven of eight networks improve; or if the one-sided 95%
upper bound on variance-times-complete-cost is at least 0.85.  No probe-count,
layer, rank, band, or normalization mutation is allowed after reading this
gate.

## Candidate C — centered Chladni/needlet band energy

### Exact operator and law

Use the same unit-variance band mode \(B_a\) from A.  Define its centered
energy

\[
 E_a(u)=B_a(u)^2-1,qquad
 H_C(u;W)=|\mathcal J|^{-1/2}
           \sum_{j\in\mathcal J}E_{a_j}(u).
\]

The addition theorem and \(\sum c_\ell^2=1\) give the exact identity

\[
 E_U E_a(U)=E_UB_a(U)^2-1=0,qquad E_UH_C(U;W)=0.
\]

This is the rigorous cymatic move: \(B_a\) is signed displacement, its zero
set is a nodal/Chladni-like pattern, and \(B_a^2\) is modal intensity.  The
network axes are not a needlet quadrature, so \(H_C\) is a network-centered
needlet-style energy bank, not a tight-frame theorem.

### Recurrence, invariance, and bill

Candidate C uses exactly A's scaled recurrence.  If A's band values are
already available in a frozen joint evaluation, let \(m=|\mathcal J|\) and
compute \(H_C=m^{-1/2}(\sum_{j\in\mathcal J}B_{a_j}^2-m)\).  With a
zero-initialized accumulator this adds
\(2Sm+2S=16{,}579{,}584\) scalar operations at \(S=32{,}256,m=256\): one
square and one accumulation per \((s,j)\), then one subtraction and one scale
per row.  Standalone C must pay A's full recurrence.  It needs no VJP, new
network evaluation, FFT, WHT, or dense matrix product.  Stream the energy
reduction; never retain the full axis bank beyond the current row block.

Even degrees make it antipodally even.  Uniform aggregation gives hidden
permutation invariance, input orthogonal covariance, and positive-gauge
invariance exactly as in A.

### Predicted signature

The distinctive signature is

```text
linear band A: weak or cancelling frame-error covariance
energy band C: stable held-frame covariance and variance reduction
```

That pattern would support an antinode/intensity mechanism rather than a
generic high-degree linear control.  If A and C both help identically, the
“cymatic energy” story has not been isolated.

### Failure localization and reasons it may fail

- Empirical mean differs from zero: recurrence/normalization or fold-law bug.
- Unit band variance passes but energy has extreme block kurtosis: the identity
  is correct, but finite-frame regression is unstable.
- Pilot energy correlation vanishes held out: spatial localization is absent;
  repeat of M25.
- C helps only jointly with a selected A coefficient: interaction fishing
  unless the A/C joint cell was frozen in advance.
- Cost-adjusted loss: more base paths beat the feature despite its cheap
  incremental arithmetic.

Squaring is not spectrally innocent.  Products of degrees 8--32 contain even
degrees from zero through 64.  Subtracting one removes the constant exactly,
but the control is a broad harmonic self-convolution, not a pure degree-18
energy projector.  It may reintroduce low-degree variation already handled by
frames and can have high kurtosis.  This is the chief mathematical reason the
god edge may still fail.

### Cheapest generated-only gate and hard kill

The no-network unit gate checks \(E B_a=0\), \(E B_a^2=1\),
\(E(B_a^2-1)=0\), recurrence accuracy, parity, and invariances at \(d=256\).
The generated screen freezes three feature cells—A alone, C alone, and A+C—on
the same eight-network independent-frame protocol.  Fit every coefficient out
of frame and use frame blocks for confidence intervals.

Kill C if any identity fails; if held-frame energy/error correlation is below
0.30; if held block excess kurtosis exceeds the predeclared cap of 50; if
fewer than six of eight networks improve; if any network exceeds 1.10; or if
the one-sided 95% upper bound on variance-times-complete-cost is at least 0.80.
Do not change the square to an absolute value, power, threshold, or selected
axis subset after failure.

## Common execution firewall and failure map

No candidate is authorized to run by this note.  A future gate must use only
fresh generated networks from an immutable seed band; no contest network,
truth, scorer, packet, or champion can enter feature, time, band, coefficient,
or axis selection.  Complete networks—not outputs, neurons, or individual
directions—are the independent unit for the final paired confidence interval.

| Observation | Causal localization | Disposition |
|---|---|---|
| High-precision harmonic laws fail | algebra or normalization | Stop before any network. |
| Float64 differs while high precision passes | recurrence stability | Repair numerics without reading accuracy; otherwise close. |
| Pointwise fit, null frame-error correlation | wrong observable for integration error | Kill that candidate. |
| Held correlation, no variance gain | coefficient/fold noise | Kill frozen implementation; no ridge search. |
| Raw gain, cost-adjusted loss | billed recurrence/pilot dominates | Preserve diagnostic only. |
| A wins, C fails | signed band amplitude is observable; energy story false | Preserve A only. |
| C wins, A fails | genuine antinode/intensity signature | Promote only to a target-shape generated cost audit. |
| B loses to sign-erased | signed transfer is canceling/noisy | Close B. |
| B beats sign-erased but not uniform | output physics real but irrelevant | Diagnostic only. |
| Small width passes, \(d=256\) harmonic variance collapses | high-dimensional dilution | Close; no rank/axis expansion. |
| M71 basis holdout used as an independent fold | invalid conditional law | Invalidate the result. |

## Priority

1. **C is the only novel god edge**, but it should be tested only as the
   predeclared extra observable beside A because it reuses A's recurrence.
2. **A is the cleanest falsifier** of the supplied degree-18 premise.  Its
   operator is fixed, exact zero, and cheap enough to audit; it has no claimed
   asymptotic theorem for the deep ReLU residual.
3. **B has the best invariance engineering and worst empirical prior.**  Its
   gauge-invariant rank-\(K\) factorization is worth recording, but existing
   signed-J cancellation and error-link failures make it last priority.

No physical analogy yields a weight-expectation shortcut by itself.  A future
pass would establish only a generated-network control-variate premise, then
require a separate target-shape FlopScope, residual-time, memory, parity, and
failure-tail audit.

## Primary sources

1. Chenchao Zhao and Jun S. Song, *Exact Heat Kernel on a Hypersphere and Its
   Applications in Kernel SVM*, Frontiers in Applied Mathematics and
   Statistics 4:1 (2018):
   [doi:10.3389/fams.2018.00001](https://doi.org/10.3389/fams.2018.00001),
   [arXiv:1702.01373](https://arxiv.org/abs/1702.01373).
2. F. J. Narcowich, P. Petrushev, and J. D. Ward, *Localized Tight Frames on
   Spheres*, SIAM Journal on Mathematical Analysis 38(2), 574--594 (2006):
   [doi:10.1137/040614359](https://doi.org/10.1137/040614359),
   [author PDF](https://people.math.sc.edu/pencho/Publications/NPW-Sphere-SIMA-2006.pdf).
3. N. S. Bardell, *Chladni Figures for Completely Free Parallelogram Plates:
   An Analytical Study*, Journal of Sound and Vibration 174(5), 655--676
   (1994): [doi:10.1006/jsvi.1994.1300](https://doi.org/10.1006/jsvi.1994.1300).
4. Wes Gurnee et al., *Verbalizable Representations Form a Global Workspace in
   Language Models*, method page, published 2026-07-06:
   [primary method page](https://transformer-circuits.pub/2026/workspace/index.html).
   This supports only the averaged-Jacobian operator; its token/workspace
   interpretation is not transferred.
5. NIST Digital Library of Mathematical Functions, Gegenbauer recurrence
   table: [DLMF §18.9](https://dlmf.nist.gov/18.9).
6. Ilona Iglewska-Nowak, *Poisson Wavelets on n-Dimensional Spheres*, Journal
   of Fourier Analysis and Applications 21, 206--227 (2015):
   [doi:10.1007/s00041-014-9366-x](https://doi.org/10.1007/s00041-014-9366-x),
   [preprint](https://arxiv.org/abs/1803.03118).
