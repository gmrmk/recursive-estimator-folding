# Centered Hermite-association bridge: a lawful control, not a moment closure

**Question.** Can the exact learned-carrier association

\[
 C_{\ell,r,q}=K_{\ell,r}^{\mathsf T}
 \operatorname{diag}(\gamma_{\ell,q}-\bar\gamma_{\ell,q})S_\ell,
 \qquad K_{\ell,r}\in\{W_\ell,|W_\ell|,W_\ell^2\},\quad q=1,\ldots,4,
\]

be turned into a cheap analytic/control-variate or low-rank moment correction
for the fixed, bias-free, width-256/depth-32 ReLU MLP?  Here
\(\bar\gamma_{\ell,q}=n^{-1}\sum_i\gamma_{\ell,q,i}\).  This is a
theory/source audit only: no contest target, estimator packet, or champion was
run or modified.

## Bottom line

**Do not promote a deterministic `C -> analytic mean/moment` bridge.**  It is
an approximate-mean estimator unless it supplies an independently proved
fixed-network expectation.  The exact association identity does not provide
that expectation and cannot evade the finite-width cumulant hierarchy.

There is exactly one narrow, lawful conversion worth a cheap *generated-net*
falsifier: use a frozen, weights-only readout of compressed \(C\) to choose
coefficients of **input-Gaussian, frame-surviving Hermite controls with known
zero mean**.  This is unbiased conditional on the frozen MLP weights.  The
association merely chooses coefficients; it does not claim to be a propagated
cumulant.  It is viable only if it gives a very large held-network
variance-times-cost reduction.  Existing design/frame results make that
unlikely, but this construction has a different bias class and a cheap
decisive test.

```mermaid
flowchart LR
  C[Centered association C(W)] --> B[Frozen weights-only readout B(W)]
  B --> CV[Input Hermite controls h(X;W), E[h|W]=0]
  X --> F[Exact sampled MLP output f(X;W)]
  X --> CV
  F --> EST[mean of f - B h]
  CV --> EST
  C -. deterministic only .-> BAD[Deterministic mean/moment correction]
  BAD -. no exact E[g|W] .-> REJECT[Approximate-mean bias class]
```

## Established facts (not extrapolations)

1. **The decomposition is exact but deterministic.**  For every layer/kernel
   pair,

   \[
   K_r^{\mathsf T}\operatorname{diag}(\gamma_q)S
   =\bar\gamma_q K_r^{\mathsf T}S+C_{r,q}.
   \]

   Thus \(C\) retains source-node/edge/state pairing which the raw transport
   loses.  It is not four independent sources: the four \(\gamma_q\) are
   functions of one local \(\alpha\).  This is an algebraic property of the
   local carrier, not a theorem that \(C\) estimates the MLP integral.

2. **Gaussian covariance propagation has a real, limited theorem.**  Wright,
   Nakahira, and Moura give an analytic covariance map for nonlinearities,
   including ReLU, *when the preactivation is Gaussian*.  It is a
   mean/covariance propagation result, not a proof that a fixed deep ReLU MLP
   remains Gaussian after a layer.  [Primary source](https://arxiv.org/abs/2403.16163).

3. **Finite-width higher cumulants are not optional in the ensemble theory.**
   Hanin proves, for random fully-connected networks, a perturbative cumulant
   hierarchy and specifically identifies \(L/n\) as the effective depth:
   nominal \(n^{-k}\) terms can grow as \(L^k\).  At the requested geometry,
   \(L/n=32/256=1/8\), so this is not a small-parameter certificate for an
   arbitrary finite truncation.  The theorem concerns an ensemble of random
   networks (with its stated assumptions), **not** the input law of one fixed
   realized MLP; it is nevertheless a direct warning against the proposed
   `fixed rank beats all cumulants` inference.  [Primary source](https://arxiv.org/abs/2204.01058).

4. **Edgeworth expansions establish controlled finite-width corrections only
   in their stated random-network regimes.**  Antognini derives a leading
   fourth-Hermite correction for a one-hidden-layer random ensemble.  Celli
   (2026) gives an arbitrary-order multivariate Edgeworth result for
   Gaussian-initialized FC ensembles evaluated on a finite set of inputs; the
   order must increase to achieve the stated \(n^{-m}\) total-variation rate.
   Neither result creates a fixed-width, fixed-weight, fixed-rank recursion
   for \(E_X[f_W(X)]\).  [Antognini, 2019](https://arxiv.org/abs/1908.10030);
   [Celli, 2026](https://arxiv.org/abs/2605.24072).

5. **Tensor-program/GP results do not supply the missing correction.**  They
   give infinite-width deterministic limits (and, in newer work, quantitative
   proximity under their assumptions); they do not identify a frozen
   transformer feature with the all-order conditional law of a single fixed
   MLP.  [Yang, 2020](https://arxiv.org/abs/2006.14548);
   [Agazzi--Mosig García--Trevisan, 2026](https://arxiv.org/abs/2607.06290).

6. **A mean/covariance-only state is therefore capped at second order.**  This
   follows directly from item 2's Gaussian-input premise and the fact that
   ReLU of a nondegenerate Gaussian is rectified, hence non-Gaussian.  Calling
   a second-moment propagation a “Gaussian closure” is an approximation after
   the first nontrivial layer, not an exact fixed-network law.

7. **Local established project constraints.**  The current random-frame plus
   antipodal sampler kills odd spherical harmonics and integrates the degree-2
   component exactly framewise; prior local tests also found near-orthogonal
   polynomial/frame controls unhelpful.  These are campaign measurements, not
   external theorems, but they determine which exact-mean controls are not
   worth retesting.

No directly relevant primary source was found that turns a TAP/EP/Laplace
fixed point into an exact conditional expectation for a deterministic deep
ReLU MLP.  Those methods would still need an exact normalizer/expectation to
be an unbiased control, so they do not change the conclusion here.

## Candidate A — association-selected exact-mean Hermite control

### Exact construction

Freeze every learned quantity before the sampled paths for a network.  Let
\(v_j(W)\in\mathbb R^{256}\), \(j=1,\ldots,d\), be deterministic unit
directions derived from the first-layer columns (with a deterministic
fallback for a zero column).  For an input \(X\sim N(0,I)\), define

\[
 h_{j,p}(X;W)=\operatorname{He}_{2p}(v_j(W)^{\mathsf T}X),\qquad
 p\in\{3,4\}.
\]

Then exactly \(E_X[h_{j,p}(X;W)\mid W]=0\).  Use only even degrees 6 and 8:
antithetic averaging removes odd degrees, and the existing complete frame
already kills degree 2.  Let \(\operatorname{vec}\widetilde C(W)\) be a
low-rank, canonicalized compression of all association matrices, for example

\[
 \widetilde C_{\ell,r,q}=K_{\ell,r}^{\mathsf T}
 \operatorname{diag}(\gamma_{\ell,q}-\bar\gamma_{\ell,q})S_\ell P_\ell,
 \qquad P_\ell\in\mathbb R^{15\times a},\ a=4,
\]

where \(P_\ell\) and the subsequent readout are frozen after offline
training on generated networks.  A fixed readout produces
\(B(W)\in\mathbb R^{256\times 2d}\), preferably clipped solely by a
predeclared deterministic rule.  The sample estimator is

\[
 \widehat\mu(W)=\frac1N\sum_{t=1}^N\left[f_W(X_t)-B(W)h(X_t;W)\right].
\]

It is conditionally unbiased for every frozen \(W\), regardless of whether
the learned \(B\) is accurate:

\[
 E_X[\widehat\mu(W)\mid W]=E_X[f_W(X)\mid W].
\]

For the actual spherical/radial implementation, define the controls with the
same radial factor and use their **analytic Gaussian mean**, or prove the
matched angular mean is zero under exactly the sampled design.  Do not assume
Gaussian Hermite zero-mean after changing the sampling law.

### What is inference, not established

The hypothesis is only that \(C(W)\) predicts useful coefficients \(B(W)\)
for residual harmonic content of the sampled deep MLP.  The exact identity
proves neither correlation nor low-rank compressibility of that mapping.

### Complexity at \(n=256,L=32\)

The association-formation lower bound, retaining 3 kernels, 4 masks, and
rank \(a=4\), is

\[
 (L-1)\,3\,4\,[2n^2a+2n(15)a]
 =31\cdot12\cdot(524{,}288+30{,}720)
 \approx 206.5\text{M FLOPs}.
\]

This deliberately excludes the existing learned-carrier/attention forward,
the readout, and control evaluation.  With \(d=8\), two degrees add only
\(2d\cdot256=4096\) dot-product FLOPs per Monte-Carlo input plus scalar
Hermite recurrences; that is negligible beside a 32x256 MLP forward.  The
complete carrier must be charged end-to-end, not inferred from this lower
bound.  The local sidecar headroom is about 35B, so cost is plausibly
testable; accuracy is the binding issue.

### Bias class, measurable signature, and cheapest falsifier

* **Bias class:** exact conditional mean if (i) `B` is frozen without held
  paths and (ii) the exact mean of the matched sampling-law controls is used.
  Cross-fitting coefficients is permitted but unnecessary for conditional
  unbiasedness when coefficients are weights-only.
* **Signature:** on wholly held generated MLPs, the paired residual
  \(f-Bh\) must show a stable reduction in **frame-block variance**, with
  degree-6/8 residual covariance nonzero after all existing degree-0/2 and
  antipodal annihilations.  The improvement must persist after a coherent
  whole-\(\gamma\)-row permutation that destroys source association while
  leaving the controls and feature marginals available.
* **Cheapest falsifier:** before any full evaluation, generate 16 fresh
  width-256/depth-32 He MLPs and use 8 independent Haar-frame blocks per net.
  Compute the population-oracle ridge coefficient from seven blocks and score
  it on the held eighth block; compare equal total FLOPs to extra base paths.
  If oracle `Var(residual)/Var(base) * cost_ratio >= 1` on the aggregate, the
  learned control cannot help.  The prospective promotion bar should be much
  stronger (e.g. upper-95% ratio < 0.5), but `>=1` is the cheap hard stop.
* **Hard kill condition:** either (a) its association-informed oracle fails
  the above held-frame equal-cost inequality, or (b) its benefit is unchanged
  by coherent gamma-row permutation / is matched by an association-free
  readout.  In case (b), `C` is not the causal information source; retire this
  bridge rather than retune degrees, directions, or rank.

## Candidate B — deterministic low-rank cumulant/moment correction

### Proposed form

One might read \(\widetilde C\) as factors for an order-3/4 tensor, e.g.

\[
 \kappa_{3,\ell}\stackrel{?}{\approx}
 \sum_{a=1}^{r}\lambda_{\ell a}u_{\ell a}^{\otimes3},\qquad
 \kappa_{4,\ell}\stackrel{?}{\approx}
 \sum_{a=1}^{r}\eta_{\ell a}v_{\ell a}^{\otimes4},
\]

then push the factors through affine maps and a ReLU Edgeworth map, and emit a
deterministic correction \(\Delta(W)\) to a Gaussian mean/covariance anchor.
At \(r=4\), forming the compressed association costs the same 206.5M-FLOP
lower bound above; propagating rank-4 factors through each dense layer is
only \(O(Ln^2r)\), about 16.3M multiply-add FLOPs.  This arithmetic is cheap.

### Why it is rejected now

* **Bias class:** a deterministic approximate mean.  It is not a control
  variate: substituting it as a constant anchor gives
  \(\Delta+\operatorname{mean}(f-\Delta)=\operatorname{mean}(f)\), and any
  nontrivial blend inherits approximation bias unless separately debiased.
* **Source failure:** \(C\) contains four local Hermite-weighted transports,
  not the actual third/fourth joint cumulant tensors of the fixed input law.
  Inferring them is a learned regression, not an identity.
* **Closure failure:** the ReLU Hermite expansion has infinitely many nonzero
  orders.  A fixed rank/order 3--4 state has no exact closure through 31
  nonlinear layers.  Hanin's \(L/n\) hierarchy directly defeats the claim that
  a finite first correction is uniformly negligible here.
* **Known local cap:** a terminal order-2 analytic Hermite contraction was
  already observed to retain only about 0.5% of its matched Gaussian-closure
  baseline improvement even while an expensive true-terminal-moment oracle
  had large signal.  This is not an external theorem, but it is the correct
  empirical prior for a new deterministic compression.

**Hard kill condition:** do not implement/evaluate this as a score candidate
unless it first provides (1) an explicit fixed-weight source identity for the
claimed factors, (2) a residual/certificate bounding every omitted
Hermite/cumulant contribution below the required error scale at \(L/n=1/8\),
and (3) an exact-mean debiasing identity.  A low reconstruction error of
\(C\) or a good in-sample learned mean is not evidence for any of the three.

## Reconciliation with the documented objections

| Objection | Effect on the bridge |
|---|---|
| Gaussian second-moment cap | Kills Candidate B as an exact law; does not affect Candidate A's input-Hermite zero-mean proof. |
| `L/n` cumulant hierarchy | Kills the assertion that a fixed rank-4/low-order closure avoids accumulated diagrams. |
| Near-orthogonal truncation error | Candidate A must use held frame blocks and equal-cost comparison; basis orthogonality is not a variance proof. |
| Frame/design annihilation | Excludes odd and degree-2 controls; motivates degree 6/8 only, but also makes success less likely. |
| Approximate-mean theorem | Forbids treating deterministic `C -> Δ(W)` as a control.  Candidate A survives only because `h(X;W)` is nonconstant with a proved mean. |

## Decision

**Status: Candidate A is a single cheap falsifier, not a promoted estimator.
Candidate B is hard-killed at the source/closure/bias boundary.**  The
centered association is worth preserving as a coefficient-selection feature
only; the literature and existing constraints do not support interpreting it
as a finite-dimensional analytic moment law for the fixed deep MLP.

## Primary-source record

1. Boris Hanin, *Random Fully Connected Neural Networks as Perturbatively
   Solvable Hierarchies*, JMLR 25 (2024); [author arXiv version](https://arxiv.org/abs/2204.01058).
2. Lucia Celli, *Optimal Non-Asymptotic Edgeworth Expansions for Multivariate
   Neural Network Outputs* (2026); [arXiv](https://arxiv.org/abs/2605.24072).
3. Joseph M. Antognini, *Finite Size Corrections for Neural Network Gaussian
   Processes* (2019); [arXiv](https://arxiv.org/abs/1908.10030).
4. Oren Wright, Yorie Nakahira, and José M. F. Moura, *An Analytic Solution to
   Covariance Propagation in Neural Networks* (2024); [arXiv](https://arxiv.org/abs/2403.16163).
5. Greg Yang, *Tensor Programs II: Neural Tangent Kernel for Any Architecture*
   (2020); [arXiv](https://arxiv.org/abs/2006.14548).
6. Andrea Agazzi, Eloy Mosig García, and Dario Trevisan, *Quantitative
   Gaussian-Process Limits of Tensor Programs* (2026); [arXiv](https://arxiv.org/abs/2607.06290).

All external claims above are limited to these primary papers.  Statements
about frame designs, existing terminal-Hermite measurements, and the
approximate-mean/control constraint are explicitly labeled as local algebra or
campaign evidence rather than attributed to the papers.
