# M115 hostile theory audit: Projective Arc-Cosine Nystrom Control

**Disposition: REPAIR.** The proposed feature has an exact conditional-zero identity and is legal in principle. It is not yet safe to implement as stated, because (i) ordinary training centering of the controls breaks that identity on held frames, (ii) the advertised `40 frames x 256 lines` fit optimizes the wrong loss for a complete-frame estimator, and (iii) the initial cost sketch omitted the second landmark projection needed by the antipodal feature. The repaired, frame-level, no-intercept version below is eligible for one *generated-only* premise implementation. It is not a champion mutation and it has no claimed efficacy result.

This is a classical first-layer random-feature control. "Projective" means that the same feature is evaluated at a line and its antipode; "Nystrom" is a mnemonic for a landmark dictionary in the finite first-layer ReLU feature space, not a claim that a standard kernel-Nystrom error theorem applies to a deep finite-width ReLU network.

## 0. Frozen boundary

The target is the radialized directional mean of a fixed, bias-free, positive-homogeneous depth-32 ReLU network at `d=n=256`. Let

\[
 F_o(u)=\operatorname{ReLU}(z^{(L)}_o(u)),\qquad
 G_o(u)=\tfrac12\{F_o(u)+F_o(-u)\},\qquad
 I_o=\rho_d\,E[G_o(U)],
\]

where \(U\sim\operatorname{Unif}(S^{d-1})\) and \(\rho_d=E\chi_d\). The only permissible sample unit for this mutation is a **whole independent Haar frame**. A shared rotation of Kerdock/MUB bases is excluded: its held bases are not independent of the training bases, so the cross-fit proof below does not apply.

The deployment parent is therefore the independent-Haar L1 sampler, not the single-rotation structured design. All landmark work, special functions, QR/RNG, conversions, copies, ridge solves, and wall time must be billed in the same submitted process. No public truth, leaderboard value, or network output at a landmark is allowed.

## 1. The exact control

Write the nonzero first-layer gate axes as

\[
 a_i=\frac{w_{1,i}}{\lVert w_{1,i}\rVert_2},\qquad
 H(u)=([a_1^Tu]_+,\ldots,[a_n^Tu]_+)^T.
\]

Here \(w_{1,i}\) denotes the input vector feeding hidden unit \(i\); an implementation must state its array convention and normalize that axis, not a row/column chosen accidentally by layout. Zero first-layer vectors are a hard precheck failure for this exact candidate.

Take `m=128` *oriented* landmark directions \(z_1,\ldots,z_m\) from a dedicated random Haar frame, independent of every evaluation frame, and set \(c_\ell=H(z_\ell)\). Conditional on the weights,

\[
 M_{ik}=E[H_i(U)H_k(U)]
   =\frac{\kappa(a_i^Ta_k)}{2d},\tag{1}
\]

\[
 \kappa(t)=\frac{\sqrt{1-t^2}+t(\pi-\arccos t)}{\pi}.
\]

Equation (1) follows by writing a standard Gaussian as \(RU\): the Gaussian ReLU product is \(\kappa(t)/2\), while \(E R^2=d\). It is the degree-one arc-cosine kernel in the spherical normalization. In particular, \(M\) is positive semidefinite. Define

\[
 D_\ell=c_\ell^T M c_\ell,\quad
 \phi_\ell(u)=\frac{(H(u)^Tc_\ell)^2}{D_\ell}-1,\quad
 \psi_\ell(u)=\tfrac12\{\phi_\ell(u)+\phi_\ell(-u)\}.\tag{2}
\]

For every fixed weights and every fixed admissible landmark set,

\[
 E[\phi_\ell(U)\mid W_1,Z]
 =\frac{c_\ell^T M c_\ell}{D_\ell}-1=0,
 \qquad E[\psi_\ell(U)\mid W_1,Z]=0.\tag{3}
\]

This is an exact conditional identity, rather than a learned approximation. The antipodal average makes the feature even and shares the target's parity.

### Denominator and tail facts

Let

\[
 \mu_d=E[U_1^+]
 =\frac{\Gamma(d/2)}{2\sqrt\pi\,\Gamma((d+1)/2)}.
\]

Since \(c_\ell\ge0\), \(H_i(u)\in[0,1]\), and \(E[c_\ell^T H(U)]=\mu_d\,\mathbf 1^Tc_\ell\), Jensen gives

\[
 D_\ell\ge \mu_d^2(\mathbf1^Tc_\ell)^2,
 \qquad -1\le\phi_\ell(u)\le\mu_d^{-2}-1.\tag{4}
\]

Thus a nonzero \(c_\ell\) has a strictly positive denominator in exact arithmetic. At `d=256`, \(\mu_d=0.024958253860802991\) and the upper bound is `1604.3569199232961`. This bound is loose but important: these are not automatically light-tailed controls. If a landmark happens to have \(c_\ell=0\), (2) is undefined. The frozen implementation must fail closed before any output forward, rather than floor the denominator or resample a landmark after inspecting an outcome.

## 2. Frame estimator and exact cross-fit rule

For independent Haar frames \(Q_r=(q_{r1},\ldots,q_{rd})\), let

\[
 Y_{r,o}=\frac{\rho_d}{d}\sum_{b=1}^dG_o(q_{rb}),\qquad
 P_r=\frac1d\sum_{b=1}^d\psi(q_{rb})\in\mathbb R^m.\tag{5}
\]

Each individual frame column is uniform, so (3) implies

\[
 E[P_r\mid W_1,Z]=0.\tag{6}
\]

Partition `R=50` independent frames into five fixed folds of ten frames. For held fold \(f\), write \(T_f\) for its forty training frames. The following is the safe frozen regression rule; it uses frame blocks, not the 10240 individual directions as independent observations.

\[
 s_{f\ell}=\left(\frac1{|T_f|}\sum_{r\in T_f}P_{r\ell}^2\right)^{1/2},
 \quad S_f=\operatorname{diag}(s_{f\ell}),
 \quad X_{r,f}=P_rS_f^{\dagger},\tag{7}
\]

where a literally zero `s` has pseudoinverse entry zero. This is RMS scaling **without centering**. With

\[
 \lambda_f=10^{-3}\frac{\operatorname{tr}(X_{T_f,f}^TX_{T_f,f})}{m},
\]

define, separately for each output but with the shared factorization,

\[
 \widehat\gamma_{f,o}=
 (X_{T_f,f}^TX_{T_f,f}+\lambda_f I)^{-1}
 X_{T_f,f}^T(Y_{T_f,o}-\bar Y_{T_f,o}\mathbf1),\tag{8}
\]

and make the held correction

\[
 C_{h,o}=X_{h,f}^T\widehat\gamma_{f,o},\qquad
 \widehat I_o=\frac1R\sum_f\sum_{h\in f}(Y_{h,o}-C_{h,o}).\tag{9}
\]

If the training trace is zero, (8) is defined to produce an all-zero coefficient. There is no fitted intercept and no added training mean in (9).

Let \(\mathcal F_f\) contain all weights, landmarks, and training frames and their output blocks. Conditional on \(\mathcal F_f\), both \(S_f\) and \(\widehat\gamma_f\) are fixed, while an independent held frame has mean-zero \(P_h\) by (6). Therefore

\[
 E[C_{h,o}\mid\mathcal F_f]=0,
 \qquad E[Y_{h,o}-C_{h,o}\mid\mathcal F_f]=I_o.\tag{10}
\]

Summing proves \(E[\widehat I_o\mid W,Z]=I_o\). Fold training sets overlap, so this proves exact mean-unbiasedness, not an iid standard-error formula or a guarantee of lower variance.

### The centering trap

The usual ML standardization is invalid here. If instead deployment uses

\[
 \widetilde X_{h,f}=(P_h-\bar P_{T_f})S_f^{-1},
\]

then

\[
 E[\widetilde X_{h,f}\mid\mathcal F_f]
 =-\bar P_{T_f}S_f^{-1},
\]

which is generally nonzero. A fitted slope then creates a genuine bias. The same failure occurs with `Ridge(fit_intercept=True)`, kernel double centering, a held-row cosine normalization, batch normalization using held rows, or subtracting a training prediction intercept.

Safe operations are only linear maps of the held raw \(P_h\), whose matrix may depend on training data. Thus it is safe to center **training responses** in (8), to choose a training-only RMS scaling or PCA/whitening matrix, and then apply that matrix to the *uncentered* held \(P_h\). The simple rule (7)--(9) is preferred because it makes the invariant visible in code.

## 3. Symmetry and independence audit

| Transformation | Result |
|---|---|
| Positive first-layer gauge | Exact: axes \(a_i\), hence \(M,c,\psi\), are unchanged; compensating downstream gauge leaves \(Y\) unchanged. |
| Later positive ReLU gauges | Exact: features use no later weights and the network output is gauge invariant. |
| First-hidden permutation | Exact: \(H,c\) permute together and \(M\mapsto P^TMP\); all inner products in (2) are unchanged. |
| Input orthogonal rotation, with directions rotated too | Exact pointwise covariance: all axis-direction dot products are preserved. |
| Input rotation when random landmarks/frames are redrawn from the same Haar law | Distributional, not pointwise, invariance. A fixed coordinate-seeded landmark frame must not be described as pointwise rotation invariant. |
| Antipodal input line | Exact: \(\psi(-u)=\psi(u)\). |
| Output permutation | Equivariant: response columns and fitted coefficient columns permute together. |

The landmark frame must be in an independent seed namespace. Conditional zero in (3) itself allows fixed landmarks, but the held-frame proof needs the held frame independent of landmarks. Reusing a held frame column as a landmark violates that condition: conditional on the landmark, other columns of that frame are constrained to an orthogonal complement, and (6) is no longer the asserted spherical identity.

## 4. What complete frames remove, and what this does not evade

Every \(\psi_\ell\) is even and mean-zero. Its spherical harmonic expansion may contain degrees \(2,4,6,\ldots\), but a complete orthonormal frame integrates every degree-two harmonic exactly. Hence the frame feature \(P_r\) in (5) contains only the degree-four-and-higher component. That is useful alignment with the L1 residual, but it is also an information loss: M115 cannot exploit a correlation that lives only in degree two.

This exposes the central issue with a line-level fit. Regressing the 10240 individual values \(\rho_dG(q_{rb})\) on \(\psi(q_{rb})\) estimates a pointwise covariance containing degree-two energy. The submitted estimator uses the *frame averages* \((Y_r,P_r)\), for which that energy is exactly annihilated. The 10240 directions are not 10240 independent units for the objective. A line fit remains mean-unbiased under cross-fitting, but can select a slope that strictly increases the frame-level variance. It cannot be called an efficacy test or a 10240-sample regression result. The repair is the block loss (8), with at most forty training rows per fold.

The fixed Bayesian-quadrature/reweighting certificate for the antipodally closed MUB rule is not contradicted. M115 is an additive, known-zero function control whose coefficient is learned from different actual-output frames. It is neither a fixed set of weights on the MUB evaluations nor usable on shared MUB rotations under the independence proof. Its only possible advantage is the new output-coupling edge learned out of fold; it does not create a hidden point-placement or fixed-reweighting loophole.

## 5. Causal hypothesis, rank, and variance attack

The candidate dictionary may be written

\[
 H(u)^Tc_\ell=\sum_i [a_i^Tu]_+[a_i^Tz_\ell]_+.
\]

It is a finite first-layer arc-cosine similarity to a landmark. Squaring it creates a fourth-order gate-amplitude observable. Unlike M111's ungated transport, its coefficient is fitted to actual deep outputs, so it does not claim that \((W_1,M)\) determines the downstream connected tensor. The proposal is consequently a legitimate *test* of a causal edge, not a theorem that the edge is present.

The attack is severe:

1. With forty training frame blocks, \(\operatorname{rank}(X_{T_f})\le40\) despite `m=128`. The landmark dictionary is richer before frame averaging, but the learned held correction still lies in an at-most-40-dimensional empirical frame span. It has no 10240-observation generalization guarantee.
2. Ridge prevents a singular solve, not variance inflation. Under a null relation between \(Y_r\) and \(P_r\), training slopes are nonzero from chance covariance while the held correction has exactly zero mean and positive variance.
3. The downstream-refactorization counterexample from M111 survives. One can keep the first-layer axes, all M115 features, and their denominators fixed while changing deeper gating and hence their covariance with the output. Cross-fitting learns that covariance only if forty frames contain enough signal.
4. If all axes are equal or antipodal, the dictionary has rank at most one; a landmark can also have \(c=0\). The network can retain nonconstant downstream output variation, so first-layer feature richness is not guaranteed by network width.
5. A constant-plus-degree-two paired output is a sharp test. The complete frame makes \(Y_r\) constant, whereas a pointwise fit can see degree-two correlations and inject held-frame noise. Correct frame-level training sets the population slope to zero.
6. The bound (4) allows rare values near `1604`, so a small number of high-leverage frame blocks can dominate a 40-row ridge fit even when all denominators are mathematically valid.

These attacks rule out any efficiency claim from feature count, kernel terminology, or in-sample regression. They do not rule out a strong, out-of-fold frame-level correlation; that is what the one-shot gate tests.

## 6. Fully billed cost and memory

The following is incremental cost for the exact reference implementation. It assumes the base L1 evaluator exposes its first unrectified preactivation \(A^TU\) (with a row scaling to normalize axes), so it can be reused. The two landmark products remain necessary: one for \(H(u)\) and one for \(H(-u)\). They must not be collapsed into one product.

For \(N=Rd\), one product of shape \((N\times n)(n\times m)\) is billed as \(2Nnm-Nm\). The table uses the stated double charge for float64 matmuls.

| Item | `R=50` | `R=126` |
|---|---:|---:|
| Evaluated directions \(N\) | 12,800 | 32,256 |
| `A^T U` if not reused, float32 | 1,674,444,800 | 4,219,600,896 |
| Two `H_+ C`, `H_- C`, float32 | 1,674,444,800 | 4,219,600,896 |
| Two `H_+ C`, `H_- C`, float64 | 3,348,889,600 | 8,439,201,792 |
| Increment if no first-preactivation reuse, all three feature matmuls float64 | 6,697,779,200 | 16,878,403,584 |

One-time f64 matmuls for `d=n=256,m=128` are: build the normalized-axis Gram `A^T A`, 66,977,792 billed operations; form landmark activations, 33,488,896; and form `M C`, 33,488,896. Their subtotal is 133,955,584 before arccos/square-root/division, norms, copies/casts, and the random orthogonal landmark frame. A full Haar QR plus explicit-Q construction must be charged rather than treated as setup magic; a conservative dense f64 allowance is about 0.09 billion operations, subject to the actual `flopscope` trace.

Frame-level ridge is small but nonzero: five f64 `128 x 40` Gram builds, five shared `128 x 128` factorizations, and 256 right-hand sides per fold should be charged. It is below 0.1 billion dense-operation equivalent, but the implementation must include it in the trace. The line-level regression that this audit rejects would cost materially more and store far more data.

For comparison, the stated L1 mean bill is about 189.85 billion. At 126 frames, the reuse-aware f64 arithmetic lower bound adds about 8.57 billion including the listed setup/QR allowance, leaving apparent FLOP headroom but not a wall-time guarantee. The all-float64/no-reuse version adds about 17.0 billion before scalar and wall costs. These figures are **not** a deployment approval: measured call shapes, allocations, and the residual wall term are binding under the official scorer.

Stream by frame and immediately accumulate \(P_r\). Then persistent M115 state is modest: `M` is 0.5 MiB f64, `C` is 0.25 MiB f64, one `A`/Gram workspace is about 0.5 MiB each, `P` at 126 frames is 0.123 MiB f64, `Y` is 0.246 MiB f64, and one `128 x 256` coefficient matrix is 0.25 MiB f64. A per-frame f64 activation/projection scratch is about 1--2 MiB in addition to the base evaluator. Storing all line features instead would cost 63.0 MiB at 126 frames alone, offers no valid sample-size benefit, and is disallowed by this repaired design.

An f32 production shortcut is a different candidate: it must separately bound the numerical mean error introduced by approximate `M`, denominators, and contractions. The first implementation should retain f64 for the control calculation and f32 only where the base evaluator already requires it.

## 7. Leakage firewall and prechecks

Before an output evaluator is callable, a frozen implementation must verify:

* landmark frame seed namespace is disjoint from every evaluation-frame seed;
* all first-layer norms are positive; `M` is symmetric/PSD to f64 tolerance, its diagonal is set to the analytic `1/(2d)`, and input Gram values are only clamped to `[-1,1]` for documented roundoff excursions;
* all landmark denominators are positive/finite with no floor, all control values finite, and the numerical version of (4) holds to a fixed tolerance;
* row/column layout, hidden permutation, positive gauge, simultaneous input rotation, antipodal parity, and rerun determinism tests pass;
* no landmark is passed through layers 2--L, no held response appears in a training fold, and no fit uses a held row for centering, scaling, feature selection, rank selection, or hyperparameter choice;
* the complete f64/f32 operation and allocation trace, including failed branches, stays below a predeclared safety ceiling.

The only allowed adaptivity in (7)--(9) is a training-measurable *linear map* of raw held frame features. Feature selection by a training-only zero column is safe, but selecting landmarks, folds, ridge, rank, or an output subset by OOF score is a new mutation and invalidates the one-shot result.

## 8. Strict one-shot admission gate

This gate is deliberately a high bar because M107/M110/M111 already showed that exact controls can add held variance.

1. Freeze the repaired equations (1)--(9), `m=128`, `R=50`, five ten-frame folds, \(\lambda=10^{-3}\operatorname{tr}(X^TX)/128\), f64 control arithmetic, and four fresh generated He networks with seeds `115001..115004`. Use one dedicated landmark Haar frame per network and fifty independent Haar evaluation frames. All seeds, source hashes, and call shapes go in the manifest before output generation.
2. Complete every precheck in section 7 for all four networks before any deep forward. A failure is `KILL_M115_REPAIRED_IMPLEMENTATION_NO_RETRY`.
3. For each network, compute the OOF frame-block covariance-trace ratio \(r_i=V_{\rm corrected}/V_{\rm base}\). Record raw and fully billed equal-cost ratios. Define the charged ratio using the actual total bill/wall trace against the frozen equal-cost L1 comparator; no favorable call or frame allocation may be omitted.
4. Continue only if every raw \(r_i<1\), the charged geometric mean and charged pooled ratio are both `< 0.90`, and the exact four-network bootstrap 90th percentile of the charged aggregate is `< 0.90`. Any failure kills this exact repaired implementation without a seed, landmark, ridge, fold, precision, rank, or normalization retry.
5. A pass is labelled `OOF-RISK-ONLY`. It authorizes repeated independent outer superblocks on fresh generated networks, using whole networks as units. It does not authorize a private submission, a champion replacement, or a claim to have beaten the structured sampler.

The comparison must use the same actual cost; adding more L1 frames to the baseline is mandatory if the mutation consumes extra budget. The gate tests one causal mechanism only: actual-output coupling to an exact projective first-layer control.

## 9. Literature anchor

The analytic ReLU/arc-cosine product in (1) is the standard degree-one arc-cosine kernel; see Cho and Saul, *Kernel Methods for Deep Learning*, NeurIPS 2009 ([primary paper](https://proceedings.neurips.cc/paper/2009/hash/5751ec3e9a4feab575962e78e006250d-Abstract.html)). Cross-fitting is cited only as an organizational precedent, not as a substitute for (10), which is a direct conditional-expectation proof: Chernozhukov et al., *Double/debiased machine learning for treatment and structural parameters*, Econometrics Journal 2018 ([primary article](https://academic.oup.com/ectj/article/21/1/C1/5056401)).

## Final judgement

M115 has passed the exact-mean, symmetry, and legality **theory** checks after the repairs above. It has not passed the causal-coupling or variance test. The mechanism is worth one target-free, manifest-gated frame-level screen because it repairs M111's missing downstream information by learning only from actual independent frame outputs while preserving an exact known mean. It must be killed, rather than parameter-tuned, if the strict gate fails.
