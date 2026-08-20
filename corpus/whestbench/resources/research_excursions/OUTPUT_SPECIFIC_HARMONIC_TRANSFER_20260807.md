# Output-specific signed harmonic transfer: adversarial audit

## Verdict

**Do not promote this as a new physics or transfer mechanism.** For a fixed
bias-free ReLU network, an even spherical-zonal mixture with any finite,
deterministic weights-only *signed* coefficient vector is an exact zero-mean
control. That narrow fact makes a fixed-coefficient estimator unbiased. It
does **not** make a product with a 1/2 gate factor an exact deep response, a
conditional moment, or a useful control.

The proposed mean-gate product fails as an exact identity after the first
gate; its uniform 1/2 factors disappear entirely after usual control
normalization. The nonnegative squared-path product is a legitimate
sign-insensitive path-energy proxy, but is also not the gated conditional
second moment. The only exact deep transfer is an unevaluated expectation
over the same deep gate geometry that the estimator is trying to integrate.
For all 256 outputs, applying output-specific controls at the
64,512-direction scale costs dense N x 256 by 256 x 256 products and is not a
cheap sidecar.

Thus retain the elementary exact-zero lemma only. Kill the claims that
"cymatic" signed propagation gives an exact gate transfer, avoids the known
self-control cancellation law, or supplies a cheap all-output control. No
M107 artifact, champion, package, experiment, or contest data was changed or
run for this audit.

## Fixed-network convention and proposed controls

Use column-vector notation only in this note:

\[
h_0=x\in\mathbb R^n,\qquad
h_\ell=\operatorname{ReLU}(W_\ell^\mathsf T h_{\ell-1}),\quad
\ell=1,\ldots,L-1,\qquad
y=W_L^\mathsf T h_{L-1}.
\]

The first-layer gate normals are the nonzero columns
\(w_j=W_1[:,j]\), with \(a_j=w_j/\lVert w_j\rVert_2\). After exact
radialization, the remaining law is \(U\sim\operatorname{Unif}(S^{n-1})\).
For an even degree \(l>0\), let

\[
 Z_{l,j}(u)=P_l(a_j^\mathsf T u),
\]

where \(P_l\) is the normalized Gegenbauer zonal harmonic. It has
\(\mathbb E_U Z_{l,j}(U)=0\) exactly, conditional on every fixed \(W\).

For a selected output coordinate \(o\), each candidate is a scalar control

\[
 H_l^o(u;W)=\sum_{j\in\mathcal J}\eta_j^o(W)Z_{l,j}(u).
\]

| Product | Coefficient before harmless normalization | What it actually represents |
|---|---|---|
| Signed mean-gate product | \(q^{o}_{1,\mathrm{mg}}=2^{-(L-2)}W_2W_3\cdots W_Le_o\) | An annealed independent-gate surrogate for a signed downstream response from \(h_1\) to output \(o\). |
| Squared path energy | \(s^o_{L-1}=W_L^{\circ2}e_o,\quad s^o_{\ell-1}=W_\ell^{\circ2}s^o_\ell\) for \(\ell=L-1,\ldots,2\) | Sum of squared *ungated linear* path products from first hidden unit \(j\) to output \(o\). |
| Exact response/moment | \(m_1^o(W)=\mathbb E_X[r_1^o(X)\mid W]\), \(k_{j,o}(W)=\mathbb E_X[(r_{1,j}^o(X))^2\mid W]\) | A weights-only mathematical function, but evaluating it is the deep gate integral rather than a cheap transfer. |

The actual input-conditioned signed downstream response is

\[
r_1^o(x)=W_2D_2(x)W_3D_3(x)\cdots W_{L-1}D_{L-1}(x)W_Le_o,\qquad
D_\ell(x)=\operatorname{diag}\{W_\ell^\mathsf T h_{\ell-1}(x)>0\}.
\]

The convention starts at \(h_1\). Including the first gate only changes the
number of displayed 1/2 factors; it does not cure the failures below.

## What is exact, and what is not

### Exact zero mean and conditional unbiasedness

If \(\eta^o(W)\) is finite and weights-only, including a signed vector, then

\[
 \mathbb E_U[H_l^o(U;W)\mid W]
 =\sum_j\eta_j^o(W)\mathbb E_U[Z_{l,j}(U)\mid W]=0.
\]

Signs do not alter this proof. A normalized signed product may use
\(\eta=q/\lVert q\rVert_1\) or \(q/\lVert q\rVert_2\); if \(q=0\), its only
legal fallback is the logged zero control. A squared-energy mixture can use
\(\eta=s/(\mathbf1^\mathsf Ts)\) when nonzero. No zero denominator may be
repaired with sampled output information.

Consequently, with a weights-only fixed \(\beta_o\),

\[
 \widehat\mu_o=\operatorname{mean}_u\{g_{W,o}(u)-\beta_oH_l^o(u;W)\}
\]

has the same conditional mean as the parent angular estimator. This is the
whole unbiasedness theorem. It says nothing about covariance with frame-block
error, numerical conditioning, cost, MSE, or score. If \(\beta_o\), a degree,
a normalization, or a transfer family is fitted from function values, it must
be frozen before evaluation or fit on genuinely independent Haar-frame folds.
Dependent MUB/Kerdock bases under one common Haar rotation are not independent
cross-fit folds.

### The 1/2 gate product is not an exact transfer

For centrally symmetric input, the *individual first-layer* gate has
\(\mathbb E[D_{1,jj}\mid W]=1/2\). No corresponding factorization holds for
the deep gate product:

\[
 \mathbb E[D_2W_3D_3\cdots D_{L-1}\mid W]
 \ne \mathbb E[D_2\mid W]W_3\mathbb E[D_3\mid W]\cdots.
\]

Nor is \(\mathbb E[D_\ell\mid W]=\tfrac12I\) generally true for
\(\ell\ge2\). The first ReLU produces a nonnegative, nonsymmetric hidden
state, and all later gates are correlated with earlier gate events and with
every path through their shared activation.

The smallest counterexample has no numerical uncertainty. With scalar input,
two ReLU gates, and positive weights,

\[
h_1=\operatorname{ReLU}(X),\qquad h_2=\operatorname{ReLU}(h_1),\qquad
X\sim N(0,1),
\]

both gate indicators equal \(\mathbf1\{X>0\}\). Hence
\(\mathbb E[D_1D_2]=1/2\), not \(1/4\). If the second weight is negative,
then \(h_2=0\) almost surely and its gate mean is zero, not 1/2. This
disproves the proposed mean-gate identity before any high-dimensional or
statistical question arises.

There is a further degeneracy: \(2^{-(L-2)}\) is common to all first-layer
coordinates for one output. It cancels from either
\(q/\lVert q\rVert_1\) or \(q/\lVert q\rVert_2\). A normalized "mean-gated"
signed mixture has exactly the same axes and relative signed weights as the
raw signed dense product; it conveys no gate information.

### Squared path energy is bookkeeping, not the missing moment

The recurrence with \(W_\ell^{\circ2}\) is exact for the sum over paths of the
products of squared *weights*. A uniform per-gate mean factor would be
\(2^{-(L-2)}s^o\), which again vanishes under mixture normalization. This
makes the construction nonnegative, sign-insensitive, and trace-like. It
does not make it equal to \(k_{j,o}(W)\).

Expanding the actual moment shows the missing terms:

\[
 k_{j,o}(W)=\sum_{p,p':j\to o}
    \Bigl(\prod_{e\in p}W_e\Bigr)
    \Bigl(\prod_{e'\in p'}W_{e'}\Bigr)
    \mathbb E_X\!\left[\prod_{v\in p\cup p'}D_v(X)\mid W\right].
\]

The squared-path recurrence keeps diagonal path weights and no gate joint
moments. The omitted cross-path terms can be signed and gates are not
independent. Treating \(s\) as an exact second moment is an unjustified
diagonal mean-field approximation.

### Exact weights-only moment boundary

There is one limited exact moment step. For Gaussian input, first-layer
preactivations are jointly Gaussian, and both
\(\mathbb E[D_1]=\tfrac12I\) and

\[
 \mathbb E[\operatorname{ReLU}(w_i^\mathsf TX)
             \operatorname{ReLU}(w_j^\mathsf TX)]
 =\frac{\lVert w_i\rVert\lVert w_j\rVert}{2\pi}
   \{\sin\theta+(\pi-\theta)\cos\theta\}
\]

are exact, where \(\theta\) is the angle between \(w_i\) and \(w_j\). This
gives exact first-layer means and covariance, then exact first two moments of
the *linear* next preactivation. That preactivation is not generally
Gaussian. Applying the same ReLU kernel to its first two moments is a closure
approximation, not an exact fixed-weight conditional transfer.

The exact deep quantities \(m_1^o(W)\) and \(k_{j,o}(W)\) are technically
weights-only because the input law is fixed. Computing them exactly requires
integrating the full arrangement of deep ReLU gate regions, or an equivalent
state carrying its full distribution. Calling this expectation a "transfer"
merely renames the original integration problem; no finite recurrence of the
proposed size follows from it.

## Symmetry, cancellation, and stability audit

### Representation symmetries pass, with explicit fallbacks

Both \(q^o\) and \(s^o\) transform by the same reindexing as the first hidden
units. Simultaneously permuting first-layer units and the adjacent downstream
rows/columns permutes \((a_j,\eta_j^o)\) and leaves \(H_l^o\) unchanged.
Under an input rotation \(R\), use \(x'=Rx\) and \(W'_1=RW_1\). Then
\(a'_j=Ra_j\), \(u'=Ru\), and
\((a'_j)^\mathsf Tu'=a_j^\mathsf Tu\); the downstream transfer is unchanged.
The controls are hidden-permutation invariant and input-covariant.

The family is equivariant under a final-output permutation if the label \(o\)
follows that permutation. It is not supposed to be invariant to arbitrary
output-space rotations, because it explicitly names output coordinates.

For even \(l\), \(Z_{l,a}=Z_{l,-a}\). A signed mixture therefore collapses
antipodal first-layer axes by the signed sum of their coefficients. This is
consistent with an even control, but creates an additional cancellation route.
A coefficient vector with nontrivial Euclidean norm can still have almost-zero
control variance,

\[
 \operatorname{Var}(H_l^o\mid W)=
 \frac1{N(n,l)}\sum_{j,k}\eta_j^o\eta_k^oP_l(a_j^\mathsf Ta_k),
\]

and must fail a small Gram/variance condition test rather than be repaired
with a data-chosen basis change.

### Oseledets language is heuristic here, not a proof

For He-scaled square matrices,
\(\mathbb E\lVert Wv\rVert_2^2=2\lVert v\rVert_2^2\). Replacing thirty
downstream ReLU gates by 1/2 therefore makes the expected squared norm of the
signed surrogate contract by about \(2^{-30}\) before final normalization.
Renormalizing each backward step avoids underflow but cannot make its direction
a true gated response.

Products of random signed matrices can align with a leading
Lyapunov/Oseledets direction when a stationary ergodic product with a spectral
gap is specified. Products of nonnegative squared matrices can analogously
concentrate in a positive Perron direction. Either behavior would tend to
make ostensibly output-specific mixtures nearly collinear at depth. It is not
a theorem for one fixed 32-layer network: the required stationary, ergodic,
asymptotic model is absent, and real ReLU gates are input-dependent. It is a
numerical risk to measure, not a mechanism predicting useful harmonic
covariance.

Signed products additionally risk destructive cancellation and a near-zero
normalization denominator. Squared products avoid signs but can concentrate or
overflow. Per-layer positive rescaling is safe only because the final energy
mixture is renormalized; clipping, coordinate tie breaks, output-derived sign
changes, or data-chosen rescaling define a different rule and need a new
unbiasedness audit.

## Cost at n=256, L=32, and 256 outputs

Let \(m=256\) outputs and use \(N=64,512\) antipodal directions
(\(126\mathbin{*}256\mathbin{*}2\)) only to price the all-output surface.
With the convention above, transfer from the first hidden layer crosses thirty
downstream hidden matrices. A dense matrix-vector product is \(n^2\) MACs and
a dense matrix-matrix product is \(n^3\) MACs.

| Work item | MACs | FLOPs if one MAC is two operations | Consequence |
|---|---:|---:|---|
| One output's signed or squared transfer | \(30n^2=1,966,080\) | 3.93M | Cheap only for a selected output. |
| Transfers for all outputs | \(30n^3=503,316,480\) | 1.01B | Material, but not the dominant charge. |
| One degree, all-output control readout | \(Nnm=4,227,858,432\) | 8.46B | Dense feature-by-output multiplication; scalar reductions no longer suffice. |
| Degrees 4, 6, 8, signed only | \(3Nnm=12,683,575,296\) | 25.37B | Before regression, memory traffic, and any pilot. |
| Degrees 4, 6, 8, signed and energy | \(6Nnm=25,367,150,592\) | 50.73B | Exceeds roughly 35.995B sidecar headroom before parent work. |

The first-layer projections can be reused only when the exact sampler has
already formed them. The all-output readout cannot: it changes scalar weighted
reductions into dense \(N\mathbin{x}n\) by \(n\mathbin{x}m\) products. A
streaming implementation can avoid materializing an \(N\mathbin{x}m\) control
array (one such float32 array is about 64 MiB), but cannot remove arithmetic
or bandwidth. For one output and three degrees the readout is only \(3Nn\)
MACs; that is a generated diagnostic, not a fair replacement for a parent
that gets all 256 outputs from each deep forward pass.

## Interaction with the known self-CV cancellation law

This proposal has two sharply different regimes.

1. **Fixed weights-only transfer and fixed coefficient.** The zonal control
   has a known exact zero mean. It is not an unknown-anchor self-CV, so the
   algebraic cancellation theorem does not apply merely because the control is
   evaluated on the same paths as the integrand. It remains a valid but
   unproven variance-reduction attempt.

2. **Sample-estimated gate transfer, same-fold fitting, or a common
   cross-fitted coefficient.** This re-enters the self-CV obstruction. For
   two equally sized folds and a common \(\beta\),

\[
 \tfrac12\{\bar f_A-\beta(\bar H_A-\bar H_B)
          +\bar f_B-\beta(\bar H_B-\bar H_A)\}
 =\tfrac12(\bar f_A+\bar f_B).
\]

   The correction cancels exactly to direct Monte Carlo. Different learned
   coefficients add estimation noise; they do not create a known expectation.
   Estimating gates from the same paths also makes the control random in the
   held sample, so the fixed weights-only zero-mean proof no longer applies
   without a separate independence proof.

The signed product therefore does not evade the existing 1.155x self-CV
ceiling or the exact common-coefficient cancellation law. It either stays a
fixed known-mean harmonic control, whose frame-block covariance must be
measured under fully charged cost, or becomes an unknown-anchor construction
with the same obstruction.

## Cheapest falsifier (generated networks only; not executed)

The asserted *exact* mean-gate law is already falsified by the scalar
positive/negative-weight construction above. No benchmark can repair that. If
the claim is softened to a heuristic direction rule, the cheapest useful
screen is deliberately much smaller than a target-shape run:

1. Freeze one He-generated bias-free network with n=8, width 8, L=4, one
   output, and one immutable seed. Do not select the seed after seeing a
   result.
2. Use B=32 independent Haar frames, each with antipodes. Bias-free
   homogeneity gives exact radialization for this screen:
   \(g_W(u)=\mathbb E[\chi_8]f_W(u)\), so it needs no sampled radial pilot.
3. Form only degree-4 controls, one from normalized signed mean-gate product
   and one from normalized squared energy. Do not fit a coefficient, degree,
   regularizer, or sign from these frames.
4. At the **frame-block** level, record the correlation of each control mean
   with the output frame mean, its control variance/Gram, the signed-product
   norm, and the actual average gated response \(r_1^o(x)\). Compare the
   latter with the 1/2 product only as an identity check, not as a score.

This screen falsifies the heuristic on its cheapest terms if the signed rule
has negligible frame-block correlation (for example, absolute correlation
below .25), is no better than squared energy, has a degenerate control Gram,
or the actual gated response disagrees with the claimed mean-gate transfer.
It cannot confirm a target-scale variance or score gain: a single output,
small width, and only 32 frame blocks have no such authority. A failure
retains the exact-zero atom lemma but retires the signed-transfer story;
neither result authorizes a change to M107 or a champion.

## Final disposition

The valid object is simply a deterministic, signed, output-labelled
zero-mean spherical harmonic control. Its exactness comes from harmonic
orthogonality, not from physics language, mean gates, path energy, or an
Oseledets argument. The advertised transfer interpretation fails at the
second gate; the exact moment alternative is computationally circular; and
the all-output cost removes the claimed sidecar advantage. Treat this as a
closed mechanism unless a new proposal supplies both a genuine cheap exact
deep conditional moment and a preregistered, all-output, equal-cost
generated-only frame-block result.

