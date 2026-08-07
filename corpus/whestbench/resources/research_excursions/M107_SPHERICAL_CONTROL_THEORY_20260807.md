# M107: even spherical Gegenbauer controls after exact radialization

## Decision

M107 is a **target-free, generated-network premise only**, not an estimator
promotion.  Once the Gaussian radius has been integrated exactly, the
remaining probability law is uniform surface measure on \(S^{255}\).  The
matched exact-zero controls are therefore spherical harmonics, not raw
one-dimensional Gaussian Hermites.  The narrowly defensible candidate is an
even, degree-6/8 zonal-harmonic control whose axes and coefficients are made
from weights only, evaluated on independent antipodal Haar frames, and fitted
out of fold.  It remains conditionally unbiased even if the fitted
coefficients are poor.  It should be abandoned immediately unless it clears
the strict generated-only, equal-total-cost gate below.

This note makes no target calls and changes no champion, ledger, or estimator
packet.  Statements marked **local premise** use the campaign description
provided to this analysis; all other mathematical statements below are derived
in the text.  No web sources were used.

## Probability space and the correct controls

Let \(d=256\), let \(X\sim N(0,I_d)\), and write \(X=RU\), where
\(U\sim\sigma_{d-1}\) is uniform on \(S^{d-1}=S^{255}\), \(R\) has the
chi distribution with \(d\) degrees of freedom, and \(R\perp U\).  For a
fixed submitted network \(W\), exact radialization replaces its integrand by

\[
  g_W(u)=E_R[f_W(Ru)\mid W],\qquad
  \mu(W)=E_U[g_W(U)\mid W].
\]

The word “exact” is important: any finite radial quadrature, clipping, or
reuse of a radius is a separate approximation and must not borrow the
unbiasedness claim below.  M107 concerns only the angular integral after that
exact transformation.

A raw Gaussian control \(\operatorname{He}_{2p}(a^\mathsf TX)\) is matched
to the *joint* \((R,U)\) law.  It is not a direction-only function.  Replacing
\(X\) by \(U\), by a fixed radius, or by an independently chosen radial rule
does not preserve its Gaussian zero-mean identity: even powers have nonzero
spherical means.  If it is itself radialized exactly, the result is a mixture
of spherical degrees up to \(2p\), rather than a pure degree-\(2p\) control;
in particular it can put mass back into degrees already annihilated by the
integration design.  Thus Gaussian Hermites are not intrinsically illegal,
but raw input-Gaussian Hermites are the wrong basis for an estimator whose
randomness is solely \(U\).  Spherical harmonics have exactly the sampled law,
a degree label with the intended meaning, and a known angular mean.

For a unit axis \(a\in S^{d-1}\), use the normalized zonal harmonic

\[
  P_l(t) = \frac{C_l^{\alpha}(t)}{C_l^{\alpha}(1)},\qquad
  \alpha=\frac{d-2}{2}=127,\qquad Z_{l,a}(u)=P_l(a^\mathsf Tu).
\]

Here \(C_l^\alpha\) is the Gegenbauer polynomial and \(P_l(1)=1\).  The
normalization is useful because all controls take the same bounded reference
value at their axis, independently of degree.

## Exact recurrence, parity, and mean-zero proof

The standard Gegenbauer recurrence is

\[
 (l+1)C_{l+1}^\alpha(t)=2(l+\alpha)tC_l^\alpha(t)
 -(l+2\alpha-1)C_{l-1}^\alpha(t),
\]

and \(C_l^\alpha(1)=(2\alpha)_l/l!\).  Dividing the recurrence by
\(C_{l+1}^\alpha(1)\) gives the normalized recurrence

\[
 \boxed{\quad
 P_0(t)=1,\quad P_1(t)=t,\quad
 P_{l+1}(t)=\frac{2(l+\alpha)}{l+2\alpha}tP_l(t)
             -\frac{l}{l+2\alpha}P_{l-1}(t).\quad}
\]

On \(S^{255}\), this is equivalently

\[
 P_{l+1}(t)=\frac{2l+254}{l+254}tP_l(t)
             -\frac{l}{l+254}P_{l-1}(t).
\]

For example, \(P_2(t)=(256t^2-1)/255\).  The recurrence also proves parity
by induction: \(P_l(-t)=(-1)^lP_l(t)\).

The function \(Z_{l,a}\) is a degree-\(l\) spherical harmonic (the zonal
member pointing at \(a\)).  Constants are precisely the degree-zero harmonic
space, while the spherical-harmonic spaces of distinct degrees are orthogonal
under normalized surface measure.  Consequently, for every fixed \(a\) and
every \(l\geq1\),

\[
 E_U[Z_{l,a}(U)]=\int_{S^{255}}P_l(a^\mathsf Tu)\,d\sigma(u)=0.
\]

This is an exact identity, not an asymptotic approximation.  It continues to
hold conditionally when \(a=a(W)\) is any measurable weights-only unit vector.

The addition theorem supplies the optional orthonormal scaling.  If
\(N(d,l)\) is the dimension of degree-\(l\) spherical harmonics,

\[
 N(d,l)=\frac{(2l+d-2)(l+d-3)!}{l!(d-2)!},\qquad
 E[Z_{l,a}(U)Z_{l,b}(U)]=\frac{P_l(a^\mathsf Tb)}{N(d,l)}.
\]

Thus \(\widetilde Z_{l,a}=\sqrt{N(256,l)}Z_{l,a}\) has unit variance.  The
two relevant dimensions are \(N(256,6)=414,173,091,136\) and
\(N(256,8)=509,436,238,615,200\).  Scaling is mathematically optional and
numerically nontrivial: the multipliers are about \(6.44\times10^5\) and
\(2.26\times10^7\), respectively.  Raw zonals with a regression
preconditioner, or analytic Gram whitening in float64, are preferable to
blindly materializing these large multipliers in low precision.

## What antipodes and frames already remove

For an antipodal pair, \([h(v)+h(-v)]/2\), every odd harmonic vanishes
pointwise.  This includes degrees 1, 3, 5, 7, and all other odd degrees; it
does not remove an even degree.  For an orthonormal frame
\(Q=(q_1,\ldots,q_d)\), the exact identity
\(d^{-1}\sum_i(a^\mathsf Tq_i)^2=1/d\), together with the displayed formula
for \(P_2\), gives

\[
 \frac1d\sum_{i=1}^d P_2(a^\mathsf Tq_i)=0
\]

for every frame and every axis.  A random Haar frame therefore gives no
degree-2 Monte Carlo error at all.  The degree-zero component is the target,
not a control.  **Local premise:** the current sampler already uses both
antipodes and complete Haar frames, so odd and degree-2 controls are known
nonstarters.

Neither fact kills degree 6 or degree 8: a generic complete orthonormal frame
does not make \(d^{-1}\sum_iP_l(a^\mathsf Tq_i)\) vanish for \(l=6,8\).
Haar averaging makes their expectation zero, but each finite frame retains a
random residual.  This is exactly the residual M107 can correlate with.  It
also means that adding controls without measuring their *frame-block*
covariance is not evidence of a variance reduction.

## A permutation-invariant, input-covariant weights-only construction

Write the first layer as rows \(w_i^\mathsf T\), \(i=1,\ldots,n\), and set
\(a_i=w_i/\|w_i\|_2\) when nonzero.  Assign a nonnegative, downstream
sensitivity weight using absolute weights only.  One concrete choice (with
the evident transpose changes for another layer convention) is the vector

\[
 s(W)=|W_2|^\mathsf T|W_3|^\mathsf T\cdots |W_L|^\mathsf T|w_{\rm out}|.
\]

It measures a pathwise upper-envelope influence, not a target-derived
gradient.  Let \(r=0,1\) denote two predeclared powers or clipped transforms
of \(s_i\), and form just four scalar controls

\[
 H_{l,r}(u;W)=\sum_{i:w_i\ne0} \omega_{i,r}(W)P_l(a_i^\mathsf Tu),
 \quad l\in\{6,8\},\quad
 \omega_{i,r}=\frac{\phi_r(s_i)}{\sum_j\phi_r(s_j)}.
\]

The zero-denominator fallback is the identically zero control and must be
logged, not repaired using targets.  Every \(H_{l,r}\) has exact conditional
mean zero.  A hidden-neuron permutation reorders \((w_i,s_i)\) and leaves
the sum unchanged.  Under an orthogonal input coordinate change \(R\),
\(w_i\mapsto Rw_i\), \(u\mapsto Ru\), and each dot product is unchanged;
the construction is input-covariant.  It uses weights, not labels or sampled
network outputs, to choose its axes.

An eigendirection alternative is possible but needs a sharper audit.  Define
\(A(W)=\sum_i s_iw_iw_i^\mathsf T\).  With a simple, predeclared separated
eigenvalue, its eigenline is hidden-permutation invariant and input-covariant;
the sign ambiguity is harmless for even \(l\).  At a repeated or nearly
repeated eigenvalue, selecting individual eigenvectors is basis-dependent and
is **not** a deterministic fully covariant rule.  The construction must then
drop that axis, or use a predeclared invariant tensor of the spectral
projector; it must not use coordinate-order tie breaking.  The weighted-column
sum above avoids this degeneracy entirely and is the recommended first test.

These are candidate directions, not a proof of usefulness.  Direction choice
is an inference: downstream sensitivity might be badly aligned with the
unintegrated degree-6/8 content of \(g_W\).

## Cross-fitted coefficient theorem

Let \(\mathcal F_k\) be the sigma-field generated by \(W\) and all Haar
frames and their antipodal directions except fold \(k\).  Let
\(\beta_{-k}\) be any finite, \(\mathcal F_k\)-measurable coefficient vector:
ridge, clipped ridge, or a deterministic weights-only coefficient are all
allowed.  It may use all function values in the other folds.  Fold \(k\)
uses an independent Haar frame \(Q_k\), and its anchors/control directions
are functions of \(W\) alone.  With \(H\) made from the degree-6/8 controls,
set

\[
 \widehat\mu_k=\frac1{m_k}\sum_{u\in Q_k^{\pm}}
      \bigl[g_W(u)-\beta_{-k}^\mathsf TH(u;W)\bigr],\qquad
 \widehat\mu_{\rm CF}=K^{-1}\sum_{k=1}^K\widehat\mu_k.
\]

Conditional on \(\mathcal F_k\), \(\beta_{-k}\) is fixed and the Haar
distribution of fold \(k\) is untouched.  Each marginal direction is uniform
on the sphere, so the exact mean-zero result gives

\[
 E[\widehat\mu_k\mid\mathcal F_k]
 =\mu(W)-\beta_{-k}^\mathsf T E[H(U;W)\mid W]=\mu(W).
\]

Taking another expectation proves \(E[\widehat\mu_{\rm CF}\mid W]=\mu(W)\).
Within-frame directions are dependent, which changes variance estimation but
not this expectation proof.  Independence of folds is the sufficient
condition that permits output-fitted coefficients.  A coefficient fitted on
the same frame, a direction picked after viewing the same fold's outputs, a
coefficient selected after target performance, or a shared pseudo-random
stream that makes folds dependent invalidates this short proof.  Weights-only
directions may be reused in every fold; weights-only *coefficients* need no
cross-fitting, but output-fitted ones do.

## Stable implementation and fully charged cost

Evaluate \(P_6\) and \(P_8\) by the normalized three-term recurrence above
in float64, never by expanding high-degree Gegenbauer coefficients.  Normalize
each nonzero \(w_i\) in float64; clamp a dot product only to correct a
documented roundoff excursion beyond \([-1,1]\), and record every clamp.
Use a numerically stable Haar QR with an explicitly fixed diagonal-sign
convention.  Keep the controls raw and whiten their tiny \(4\times4\) Gram
matrix analytically or by a training-fold Cholesky/SVD.  Reject, rather than
silently pseudo-invert, a rank-deficient or ill-conditioned design under its
predeclared threshold.  Ridge \(\lambda\), clipping rule, feature set, and
whether an intercept is fitted must be frozen before generated evaluation.
The intercept does not replace the known zero mean; it only stabilizes a
finite training-fold regression and must be fitted out of fold as part of
\(\beta_{-k}\).

The target-scale charge is the complete wall-clock/resource trace, not merely
the two scalar recurrences.  It includes the absolute-weight sensitivity
backward pass (roughly one dense matrix-vector pass per downstream layer),
row normalization and weighted aggregation, Haar-frame generation/QR,
radialization at every direction, all MLP evaluations, control dot products,
Gram/ridge solves, stored fold outputs, and any pilot used to choose a
coefficient, ridge, or rank.  If the implementation chooses eigenaxes, it
also charges formation of \(A\) and its eigendecomposition.  Baseline work
that cannot be demonstrably shared with the submitted path must be charged
again.  Cross-fitting avoids bias; it does not make training-frame function
evaluations free.  Equal-cost comparison must instead grant baseline the
additional complete paths that fit in M107's total measured cost.

## Strict cheap premise gate (generated networks only)

The gate has a deliberately narrow scope.  It is run on fresh generated
width-256/depth-32 networks only, with immutable seeds and no contest inputs,
targets, champion mutation, or coefficient transfer from this test.  First,
unit and property tests must verify the normalized recurrence through degree
8; empirical Haar means of every control; antipodal parity; the exact
framewise degree-2 identity; hidden-unit permutation invariance; and input
orthogonal covariance.  The numerical design must also show no zero fallback,
no eigen-gap violation if eigenaxes are used, and a predeclared training-fold
Gram condition number at most \(10^6\) after the selected regularization.
Failure of any item is an immediate non-promotion.

Second, on eight fresh generated networks use \(K=4\) independent Haar-frame
folds, with frame blocks (not individual correlated columns) as the resampling
unit.  Fit only the four \(H_{6,0},H_{6,1},H_{8,0},H_{8,1}\) coefficients from
the other three folds and score the held fold; every model choice is frozen.
Repeat the whole four-fold estimator over a predeclared number of independent
superblocks sufficient to form paired network-level variance estimates.  The
comparison is the actually measured variance-times-total-cost ratio against
the base sampler, after granting the base all paths purchasable at M107's
measured cost.  Pass only if the paired one-sided 95% upper confidence bound
of the geometric mean ratio is below \(0.85\), at least seven of eight
networks improve, and no network exceeds a ratio of \(1.10\).  This is a
strict premise threshold, not a score prediction.  Any gate failure kills the
M107 control family as specified; it does not authorize degree, rank, or
regularization fishing.

## Failure-localization map

| Observation | Localized failure | Required disposition |
|---|---|---|
| A control's analytic/empirical Haar mean disagrees with zero | radialization/control-law or recurrence implementation | Stop; repair proof/code before any variance claim. |
| Permuting hidden neurons or rotating input coordinates changes the control | direction construction is not invariant/covariant | Reject that construction; do not use coordinate tie breaks. |
| Frame-block control variance is negligible | frame/design has effectively annihilated the proposed mode | Stop M107; there is no usable lever. |
| Gram matrix is singular or badly conditioned | redundant axes/scaling, not a discovered signal | Stop under the frozen gate; no target-tuned feature surgery. |
| Training-fold reduction is large but held-fold reduction disappears | coefficient overfit or fold leakage | Reject output-fitted coefficients; audit seeds and data flow. |
| Held-fold reduction survives, but equal-cost ratio is at least one | variance reduction is smaller than full overhead | Stop; more base frames dominate. |
| Sensitivity-weighted axes do not beat uniform/weight-norm axes under the same frozen test | downstream-sensitivity direction inference is unsupported | Retire the sensitivity story; do not call it mechanism. |
| Generated pass, target-shape resource trace fails | cost/memory implementation failure | Reject deployment while retaining the target-free result. |
| Any selection used contest outputs, same-fold outputs, or adaptive folds | unbiasedness premise is broken | Invalidate the result and rerun only from a clean frozen protocol. |

## Hostile conclusion

The mathematical guarantee is limited but real: degree-6/8 zonal controls
have known zero mean under the exact post-radialization law, and independent
folds preserve that guarantee after coefficient fitting.  Neither the
Gegenbauer recurrence, downstream sensitivity, harmonic orthogonality, nor
cross-fitting says that the controls correlate with the residual.  Antipodes,
complete frames, and prior **local premise** results have already removed the
most obvious low-degree opportunities; this makes M107 less likely to help,
not more compelling.  The sole rational next action is the predeclared cheap
generated-only gate.  A pass would establish an efficiency premise needing a
separate fully charged target-scale audit; a failure closes M107 rather than
inviting basis expansion.

## CORRECTION — 2026-08-07: restore degree 4; distinguish L1 and M71; correct W1 orientation

The preceding degree selection was too aggressive.  **Local correction:** L1
is an average over 126 *independent Haar frames*, not a spherical 5-design.
The exact complete-frame calculation eliminates degree 2 only.  It does not
eliminate degree 4: for a generic axis \(a\),
\(d^{-1}\sum_iP_4(a^\mathsf Tq_i)\) varies with the frame.  Moreover, the
measured Kerdock/MUB advantage is direct local evidence that degree-4 angular
leakage is material.  M107's first and only frozen premise test must therefore
use \(l\in\{4,6,8\}\), not \(\{6,8\}\).  This is a correction to the
candidate set, not permission to search over additional degrees after the
gate.

The same normalized recurrence remains the stable implementation for degree
4:

\[
 P_{l+1}(t)=\frac{2l+254}{l+254}tP_l(t)
             -\frac{l}{l+254}P_{l-1}(t),\qquad P_0=1,\ P_1=t.
\]

Run it forward through \(P_4\), \(P_6\), and \(P_8\) in float64; do not
form monomial or unnormalized Gegenbauer coefficients.  The additional
orthonormal-scaling constant is

\[
 N(256,4)=\frac{(2\cdot4+256-2)(4+256-3)!}{4!(256-2)!}
 =\frac{262\cdot255\cdot256\cdot257}{24}
 =183,148,480,\qquad
 \sqrt{N(256,4)}\mathrel{\approx}13,533.2361.
\]

Thus it is much smaller than the degree-6/8 scalings, but the same stability
rule applies: retain raw controls and whiten the small coefficient Gram
matrix, or apply an analytic float64 scaling.  The fact that \(P_4\) has
zero Haar mean is still exact; the correction concerns what a *finite frame*
annihilates, not the population control identity.

The first-layer convention also requires a correction.  The forward map is
\(x\mathbin{@}W_1\), so the input gate normals are the **columns**
\(w_j=W_1[:,j]\), not rows.  Let \(\mathcal J=\{j:\|w_j\|_2>0\}\),
\(a_j=w_j/\|w_j\|_2\), and choose the weights-only path sensitivity in the
same forward convention, for example

\[
 s=|W_2|\,|W_3|\cdots |W_{\rm out}|,\qquad s_j\geq0.
\]

The rightmost factor denotes the fixed nonnegative output sensitivity with
the dimensions implied by the implementation; equivalently, this is the
absolute-value dense backward product from the output to the first hidden
layer.  Under a first-hidden-layer permutation, the columns of \(W_1\) and
the entries of \(s\) are permuted together.  Define, with no targets and no
sampled outputs,

\[
 \omega_{j,0}=|\mathcal J|^{-1},\qquad
 \omega_{j,1}=s_j/\sum_{i\in\mathcal J}s_i,\qquad
 H_{l,r}(u;W)=\sum_{j\in\mathcal J}\omega_{j,r}P_l(a_j^\mathsf Tu),
\]

for \(l\in\{4,6,8\}\) and \(r\in\{0,1\}\).  If the sensitivity
denominator is zero, \(H_{l,1}\) is the logged identically-zero fallback.
These are the **six** predeclared mixture controls
\((H_{4,0},H_{4,1},H_{6,0},H_{6,1},H_{8,0},H_{8,1})\).  They are invariant to
hidden-neuron permutations because each is a symmetric sum, and input
covariant because an orthogonal input change rotates both \(a_j\) and \(u\)
without changing their dot product.  Each has conditional spherical mean zero
by linearity.  This column-mixture construction supersedes the row-based
formula above.

The cross-fitting statement also has a sampler-specific boundary.  For L1,
make folds from disjoint subsets of its 126 independent Haar frames.  A
coefficient fitted using the other-frame folds is independent of the held
frame conditional on \(W\), so the displayed conditional-unbiasedness proof
applies unchanged (with a full frame as the dependent-within-fold block).
M71 instead uses MUB/Kerdock bases generated from one Haar rotation; its bases
are dependent through that shared rotation.  Holding out one such basis after
fitting coefficients on the others does **not** supply the frame-independence
step in the proof.  It may still be a useful quadrature design, but it is not
automatically a valid output-fitted cross-fit design.  For M71, retain only
weights-only fixed coefficients, or introduce genuinely independent Haar
rotations as cross-fit folds and charge them; otherwise no conditional
unbiasedness claim for output-fitted coefficients is available.

Accordingly, the strict gate's frozen feature vector is now six-dimensional,
its Gram/ridge test is \(6\times6\), and all earlier references to four
degree-6/8 controls should be read as replaced by these six degree-4/6/8
controls.  The fold construction must be L1-safe independent Haar frames;
the gate must not treat correlated M71 MUB bases as independent folds.

**Sensitivity addendum (2026-08-07).**  The frozen \(r=1\) choice is the
normalized backward *squared-weight path energy*, not the absolute-weight
envelope written earlier.  In the forward convention \(h_{\ell}=h_{\ell-1}
\mathbin{@}W_{\ell}\), seed the scalar-output trace with
\(s_{\rm out}=1\) (or an all-ones output-trace seed) and recurse backward

\[
 s_{\ell-1}=(W_{\ell}^{\circ2})s_{\ell},
\]

where the square is elementwise; normalizing a positive \(s\) after each
step is permitted because the final mixture renormalizes it again.  This is a
nonnegative, target-free, hidden-permutation-equivariant path-energy proxy.
For a linear downstream map it sums products of squared weights over paths,
which is the natural sign-insensitive quantity for a trace/variance objective.
ReLU gates mean it is not the actual input-conditioned Jacobian energy, and
it is not a pointwise upper bound; neither property is needed for the
exact-zero-control or cross-fit-unbiasedness proofs.  The absolute-weight
product is a defensible amplitude envelope but is not mandatory and is less
directly aligned with frame-block variance.  Hence squared path energy is the
single predeclared \(r=1\) rule; it must not be compared or swapped against
the absolute envelope using generated or contest outcomes.

There is one important L1 cost correction.  For an L1 direction matrix \(Q\)
and a positive radial value \(\rho\), the existing first-layer forward
preactivation is \(\operatorname{first\_pre}=(\rho Q)\mathbin{@}W_1\).
For every retained column \(w_j\), its zonal argument is already available as

\[
 t_{ij}=\frac{\operatorname{first\_pre}_{ij}}
                 {\rho\,\|w_j\|_2}=q_i^\mathsf Tw_j/\|w_j\|_2.
\]

Therefore the six M107 controls add **no new \(QW_1\) matrix
multiplication** to L1.  Their properly charged incremental work is column
norm computation and validation, degree-4-to-8 recurrences, six weighted
reductions, the weights-only absolute-value sensitivity matrix-vector chain,
and the small regression/Gram operations.  This reuse is L1-specific and may
not be assumed for a different sampler or execution order.

The reuse has two non-negotiable numerical guards.  A column with exactly zero
float64 norm is excluded from \(\mathcal J\), never divided by; an empty
\(\mathcal J\) makes all six controls logged zero controls and fails the
premise gate.  The sensitivity-zero fallback remains as specified above.  The
reuse identity requires every radial node used for this path to be strictly
positive and representable in the denominator.  If a radial implementation
contains \(\rho=0\), it must provide a separately cached unscaled projection
with an audited identity, or M107 cannot claim this reuse.  Finally compute
\(t\) in float64.  If \(|t|\leq1+\tau\), where \(\tau\) is a frozen small
roundoff tolerance, clip only to \([-1,1]\) and count the event; if
\(|t|>1+\tau\), reject the block as an inconsistent frame/preactivation/norm
calculation.  Clamping a material excursion is not a numerical-stability fix.
