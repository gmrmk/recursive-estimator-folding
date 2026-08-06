# Frontier audit: honest routes beyond design8

**Date:** 2026-08-06  
**Scope:** mathematical and empirical audit only. No estimator or submission files were changed.

## Executive verdict

Design8 is a strong measured incumbent, but the dossier does **not** establish a universal sampling floor or prove that weight-analytic third- and fourth-cumulant propagation is the only remaining route. The strongest brick in the dossier is empirical: several direct terminal Gaussian/Edgeworth closures do not help. The weakest bricks are the claimed average-case lower bound and the use of the proposed \((L/n)^K\) law as a hardness theorem.

There is also a concrete ledger error in the harmonic argument. Writing the normalized Gegenbauer polynomial as \(Q_\ell(1)=1\), the recurrence is

\[
(\ell+d-2)Q_{\ell+1}(t)=(2\ell+d-2)tQ_\ell(t)-\ell Q_{\ell-1}(t),
\qquad Q_0=1,\ Q_1=t.
\]

With \(d=256\), summing the resulting pair spectrum using the trimmed-126 multiplicities \(\{m_{+1}=m_{-1}=1,m_0=510,m_{+1/16}=m_{-1/16}=32000\}\) gives

\[
A_4=0.04742218,\quad A_6=2.06057070,\quad
A_8=1.99809410,\quad A_{10}=2.00006589.
\]

They do not give \(A_4=0\), and the values from degree eight onward are close to, but not exactly, two. The full-129 multiplicities use 32768 at each of \(\pm1/16\) and instead give \(A_4=0\), \(A_6=2.06203521\), and \(A_8=1.99804807\). Thus the dossier's second brick conflates the full and trimmed constructions and rounds an asymptotic-to-two ledger into an exact identity. Any spectral floor or cancellation claim using that brick must be recomputed with the actual trimmed spectrum.

The defensible statement is narrower:

> Among the tested fixed, nonadaptive linear spherical rules and the tested plug-in terminal closures, design8 appears near a local frontier. It has not been proved optimal among allowed algorithms that use the observed weights nonlinearly, condition exactly on part of the Gaussian input, or resum finite-width corrections.

At \(L=32,n=256\), \(L/n=0.125\). ARC's paper states

\[
\operatorname{MSE}(\widehat I_K)\lesssim c_K(L/n)^K
\]

as a **conjecture** about depth dependence, not a lower bound. Its rigorous theorems assume fixed depth and polynomial activations; ReLU and depth growing with width are outside that proof. The experiments supporting the depth heuristic go only to substantially smaller depths. Therefore failure of one layerwise \(K\)-cumulant implementation is not evidence that every exact-conditioning, tensor-network, cavity, or nonlinear method must fail.

The adjusted-score arithmetic also matters. From raw \(2.686\times10^{-7}\) and adjusted \(2.0467\times10^{-7}\), design8 appears to use about \(0.76199B=2.0726\times10^{11}\) operations, leaving about \(6.474\times10^{10}\). If a candidate adds \(10^{10}\) operations, it must lower raw MSE by about 4.60%; adding \(5\times10^{10}\) requires about 19.44%; spending the entire budget requires raw MSE below \(2.0467\times10^{-7}\), a 23.80% reduction. Cheap nonlinear post-processing therefore deserves priority over an expensive mechanistic solver.

## Claims under audit

| Dossier claim | Status | What is actually supported |
|---|---|---|
| Design8 raw \(2.686\times10^{-7}\), adjusted \(2.0467\times10^{-7}\) | Empirical, conditionally valid | Valid if obtained on untouched development instances with the competition's exact cost/score accounting. It is not by itself evidence of global optimality. |
| Trimmed-126 has \(A_4=0\), \(A_6\approx2.062\), and exact \(A_\ell=2\) for all \(\ell\ge8\) | **False arithmetic claim** | Those values mix full-129 and trimmed-126 multiplicities. Trimmed-126 has \(A_4=0.04742218\), \(A_6=2.06057070\), \(A_8=1.99809410\), \(A_{10}=2.00006589\). Near-two is not exact-two. |
| Sampling floor \(2.42\text{--}2.55\times10^{-7}\) | **Restricted empirical floor only** | Plausible for the tested fixed linear frame/quadrature family. No proof supplied covers all weight-aware nonlinear or adaptive estimators. |
| Gaussian weight prior makes linear rules average-case optimal | **Scope mismatch** | Classical Gaussian-measure theorems establish linear/nonadaptive optimality only for particular Gaussian priors on the unknown function and specified linear information classes. ReLU networks induce a non-Gaussian finite-width function law, and the full network weights are observed. |
| Exact final \((\mu,\sigma)\) closure caps gain at \(8.76\times10^{-7}\) | Useful negative oracle result | It says a two-moment terminal Gaussian approximation is insufficient. It does not lower-bound nonlinear conditioning or higher-order estimators. |
| Exact \(\kappa_3,\kappa_4\) Gram--Charlier oracle reaches \(4.7\times10^{-8}\) | Strong sufficiency clue, not an algorithm | It shows that accurate relevant higher moments could be valuable. It does not show those moments are computable within \(B\), nor that a truncated Gram--Charlier density is uniformly stable. |
| Layerwise cumulant propagation fails because errors scale as \((L/n)^K\) | **Unproven brick** | The scaling is proposed by ARC as a conjecture/heuristic, with unknown constants, not a no-go theorem. Failure of one closure may come from omitted contractions, ReLU nonanalyticity, re-Gaussianization, or numerical instability. |
| Only weight-analytic \(\kappa_3/\kappa_4\) remains | **Unproved completeness claim** | It is a promising untested mechanistic family, but exact conditional integration, nonlinear shrinkage, and resummed low-rank corrections are logically distinct routes. |

## Why the Gaussian-prior floor does not apply as stated

The target is a quenched integral

\[
I(W)=\mathbb E_{X\sim N(0,I_d)}[f_W(X)],
\]

where the realized \(W\) is given to the algorithm. Evaluation may average \((\widehat I(W)-I(W))^2\) over random networks, but after observing \(W\) the algorithm is free to use arbitrary nonlinear functions of it. This is different from recovering a linear functional of an unobserved function drawn from an exact Gaussian process using only a prescribed set of point evaluations.

Even with Gaussian entries in \(W\), the finite-width map \(W\mapsto f_W\) contains repeated products and ReLU gates. Consequently the induced law of \(f_W\) is not exactly Gaussian. Infinite-width GP limits concern an annealed distribution over weights at finitely many inputs; they do not turn the fixed-weight, input-averaged problem into a Gaussian Bayesian integration problem. The large oracle gain from \(\kappa_3,\kappa_4\) is itself evidence that non-Gaussian structure is material at the required precision.

There is also a constructive counterpoint to any blanket linear-optimality claim. Suppose a linear rule gives a noisy vector \(y=\mu+\varepsilon\) with approximately Gaussian covariance \(\Sigma\). For a weight-derived anchor \(a(W)\), whiten and shrink:

\[
z=\Sigma^{-1/2}(y-a),\qquad
\widetilde\mu=a+\Sigma^{1/2}
\left(1-\frac{p-2}{\|z\|^2}\right)_+z.
\]

Under the classical spherical Gaussian sequence model \(\Sigma=\sigma^2I\), positive-part James--Stein shrinkage dominates the unshrunk estimator in ordinary total squared error for \(p\ge3\). Whitening a general known \(\Sigma\) gives the analogous statement for Mahalanobis loss; it does **not** automatically give dominance for the competition's unweighted loss. That theorem therefore does not prove this particular shrinker will win here, but it does prove that Gaussian observation noise alone cannot justify a universal linear-estimator floor.

### Consequence of the Gegenbauer-ledger mismatch

Let \(A_\ell\) denote the normalized degree-\(\ell\) pair-spectrum coefficient used by the floor calculation. Whatever normalization convention is chosen, one construction's multiplicity table must be used consistently throughout its recurrence and pair sum. Replacing 32000 by 32768 changes more than a label: it changes the degree-four cancellation and all subsequent coefficients. Conversely, treating \(1.99809410\) or \(2.00006589\) as the exact integer two deletes small but systematic residual harmonics. Those residuals may or may not be practically important, but their contribution must be bounded against the required \(10^{-7}\)-scale MSE rather than assumed away.

This inconsistency does **not** prove design8 is poor—the measured score already includes its real behavior. It does invalidate any proof of its floor that requires exact degree-four annihilation by trimmed-126 or exact flatness at all higher even degrees. The repair is cheap: recompute the spectral variance ledger from the actual 126-point weights/multiplicities in extended precision and compare the predicted residual with measured rule-to-rule differences.

## Ranked hypothesis slate

### 1. Cross-fitted nonlinear shrinkage/fusion of design8 replicates

**Idea.** Treat independent Haar/frame replicates as repeated noisy observations, estimate only the covariance structure supported by the number of replicates, and shrink design8 toward a cheap weight-derived anchor or fuse two rule families using coefficients learned without targets. Use leave-one-frame-out or seed-disjoint cross-fitting so the estimated covariance and shrinkage coefficient do not reuse the residual being corrected.

**Equation.** A conservative scalar form is

\[
\widehat I_\lambda=a(W)+\lambda(W)\,[\widehat I_{\rm d8}-a(W)],
\]

with \(\lambda\) selected by cross-fitted SURE or an analytic noise estimate. The vector James--Stein form above is the richer version when the output dimension is large enough and \(\Sigma\) is estimable.

**Complexity.** \(O(md)\) for diagonal/scalar variance estimation from \(m\) existing replicates; \(O(md^2+d^3)\) for a full covariance, which should be avoided unless \(m\gg d\). No additional network forward passes are required if replicate outputs are retained.

**Predicted signature.** A stable shrink factor below one on held-out seeds; gain should be largest for networks where the standardized disagreement between replicate families is small. Estimated gain should persist when folds are swapped.

**Cheapest premise test.** Re-score existing per-frame/per-seed outputs with strictly cross-fitted scalar and diagonal shrinkage. Report raw MSE, tail quantiles, and coefficient stability separately.

**Hard kill.** Shrinkage collapses to \(\lambda\approx1\), covariance estimates change materially across folds, or seed-disjoint gain is below 5% with any tail worsening. A nondeployable oracle mean is not an admissible anchor.

### 2. Terminal-only, cross-fitted Hermite/cumulant control

**Idea.** Avoid layerwise cumulant propagation. Sample the true prefix distribution with the existing design, then estimate only the output-relevant projected moments of each final preactivation. For final weights \(w_j\) and prefix activation \(H\),

\[
\kappa_r(z_j)=K_r(H)[w_j^{\otimes r}],
\]

but the scalar contractions can be accumulated directly from \(z_j=H w_j\) in \(O(Sd)\), without materializing a \(d^r\) tensor. Cross-fit the moment estimate and the residual/control coefficient.

For a marginal with \(\alpha=\mu/\sigma\), the fourth-order terminal approximation used in the prior experiment was

\[
E[Z_+]\approx \mu\Phi(\alpha)+\sigma\phi(\alpha)
+\sigma\phi(\alpha)\left[-\frac{\gamma_1\alpha}{6}
+\frac{\gamma_2(\alpha^2-1)}{24}
+\frac{\gamma_1^2(\alpha^4-6\alpha^2+3)}{72}\right].
\]

**Important distinction.** A terminal contraction is genuinely distinct from layerwise \(K\)-propagation because it conditions on the actual sampled prefix and introduces no repeated re-Gaussianization. It is also distinct from the already-tested plug-in formula only if it is used as a cross-fitted control/U-statistic or an analytically computed weight-conditioned contraction.

**Complexity.** \(O(Sd)\) time and \(O(d)\) memory for direct projected third/fourth moments, plus negligible cross-fitting. A fully weight-analytic upstream tensor is a different and potentially \(d^K\)-scale object.

**Predicted signature.** The Hermite statistic must correlate with design8's signed error on held-out seeds, and its fitted coefficient must remain stable across networks. Gain should concentrate in outputs with reproducible skewness/kurtosis rather than high sample noise.

**Cheapest premise test.** Compute independent-half terminal moment controls from already available samples, fit on one half, apply to the other, then swap.

**Hard kill.** The local dossier already supplies a severe warning: direct terminal Edgeworth made results worse, while the best target-fitted four-term fold oracle improved only about 2.62%. Kill this route if the cross-fitted statistic has near-zero error correlation or fails to deliver at least 5% seed-disjoint raw-MSE gain. Do not count a same-sample plug-in rerun as a new hypothesis.

### 3. Exact one-dimensional Gaussian conditioning

**Idea.** Choose a unit vector \(u\) and decompose

\[
X=Y+Tu,\qquad T\sim N(0,1),\quad Y\sim N(0,I-uu^\top).
\]

For fixed \(Y\), a ReLU network restricted to the line \(Y+tu\) is piecewise affine:

\[
f_W(Y+tu)=a_r t+b_r,qquad t\in[\tau_r,\tau_{r+1}].
\]

Therefore the conditional expectation is exact:

\[
g_W(Y)=\sum_r \left{
a_r[\phi(\tau_r)-\phi(\tau_{r+1})]
+b_r[\Phi(\tau_{r+1})-\Phi(\tau_r)]
\right}.
\]

Estimating \(E_Y[g_W(Y)]\) is Rao--Blackwellization, so its variance cannot exceed direct sampling variance at equal outer samples. This route evades the cumulant hierarchy rather than climbing it.

**Complexity.** If a traced line has \(R\) regions, a naive retrace is \(O(RLd^2)\) per outer sample; an event-driven incremental implementation may be much cheaper. Worst-case \(R\) is exponential. Random-initialization theory reports average line-region growth roughly linear in the total number of neurons under its assumptions, but those assumptions do not exactly match every conditional slice here.

**Predicted signature.** With \(\rho=\operatorname{Var}(E[f(X)\mid Y])/\operatorname{Var}(f(X))\), the rough efficiency gate is

\[
\rho\,\frac{C_{\rm line}}{C_{\rm forward}}<1.
\]

Observed region counts should have a controlled upper tail and exact line integration should sharply reduce replicate variance.

**Cheapest premise test.** On a handful of untouched networks, trace 32--128 random conditional lines; measure median/q95 region count, exact-line cost, and the empirical variance ratio. No full solver is needed for this gate.

**Hard kill.** Kill if \(\rho C_{\rm line}/C_{\rm forward}\ge0.8\text{--}1\) before implementation overhead, if q95 region counts explode with depth, or if projected budget cannot clear the adjusted-score gate.

### 4. Low-rank cavity/Dyson resummation of the dominant finite-width mode

**Idea.** Do not enumerate every order-\(K\) diagram independently. If the layer map admits

\[
q_{\ell+1}=T_0(q_\ell)+n^{-1}G(q_\ell)+O(n^{-2}),
\]

then repeatedly inserting the same dominant correction produces secular powers of \(L/n\). Propagating the corrected map, or an effective resolvent/exponential such as

\[
(I-J/n)^{-1}\quad\text{or}\quad \exp[(L/n)G],
\]

resums a cactus/rainbow subclass to all depths. This can remove a bad truncated \(L^K\) series if one coherent mode dominates, but it is not an exact theorem for quenched ReLU networks.

**Complexity.** About \(O(Ld^3)\) for a full dense state update (roughly \(5.37\times10^8\) scalar kernel operations before diagram constants at \(L=32,d=256\)), or \(O(Ld^2r)\) for rank \(r\). This is plausibly within headroom only if ranks and constants stay small.

**Predicted signature.** One-step closure residuals exhibit a stable low-rank singular spectrum, the leading modes align across layers/networks, and fitted correction coefficients do not flip sign with depth.

**Cheapest premise test.** Measure one-layer moment-map residuals against high-sample references for several widths/depths, perform an SVD, and test whether a rank-1--8 recurrent correction predicts later-layer residuals without refitting.

**Hard kill.** Diffuse residual spectrum, mode rotation across layers, coefficient drift/sign changes, or less than 10% held-out improvement after the cost penalty. A tensor-network contraction order that computes the same truncated diagrams faster is not a resummation and cannot change truncation error.

## Tensor-network, cavity, and exact-conditioning boundary

The symbolic ARC implementation already notes that a cumulant calculation can be represented as a tensor network and that choosing a better contraction path can reduce runtime. For a fixed retained diagram set, however, contraction order changes cost, not the estimator's mathematical output. It therefore cannot by itself evade the \(L/n\) truncation behavior.

A tensor method becomes mathematically new only if it does one of the following:

1. sums an infinite or depth-complete diagram family by a transfer matrix/resolvent;
2. exactly conditions on activation regions and contracts their Gaussian probabilities; or
3. exploits a proved low-rank/separable structure not present in the original truncation.

The corresponding obstruction is then bond dimension/treewidth, activation-region count, or loss of low rank. Those quantities should be measured before a large implementation. Claims of an “exact tensor-network solve” without a bound on one of them are presently unproved.

Analytic Gaussian activation formulas are also not an exact deep-network solution. They may compute a ReLU mean/covariance exactly **conditional on a Gaussian layer input**, but feeding the resulting moments into the next layer re-Gaussianizes a non-Gaussian finite-width law. That is precisely where missing higher contractions can accumulate.

## Recommended order of attack

1. Run the zero/near-zero-compute cross-fitted shrinkage audit. It directly probes the unsupported linear-floor assumption and has the easiest adjusted-score gate.
2. Reuse existing samples for a strictly cross-fitted terminal Hermite control. Stop immediately if it reproduces the prior Edgeworth negative result.
3. Run the small exact-line profiling experiment. Proceed only if measured region-count and variance-cost products are favorable.
4. Only then build a low-rank cavity residual prototype. Require cross-width and cross-depth transfer before spending the remaining headroom.

None of these routes is currently a demonstrated winning entry. The first two are cheap falsification tests; exact line conditioning is the cleanest mathematical escape from the cumulant hierarchy; the cavity route has the largest theory risk. The honest claim today is that design8 is a strong incumbent with exploitable logical gaps around nonlinear weight-aware estimation, not that a winner has already been proved.

## Primary sources

- W. Wu et al., *Estimating the expected output of wide random MLPs more efficiently than sampling* (2026): fixed-depth polynomial-activation theorems, the conjectured \((L/n)^K\) depth law, empirical depth evidence, and open questions on ReLU/non-Gaussian settings. [Paper](https://arxiv.org/pdf/2605.05179) and [official implementation](https://github.com/alignment-research-center/mlp_cumulant_propagation).
- D. Lee and G. W. Wasilkowski, *Approximation of linear functionals on a Banach space with a Gaussian measure* (Journal of Complexity, 1986): scope of Gaussian average-case linear/nonadaptive optimality. [Publisher page](https://www.sciencedirect.com/science/article/pii/0885064X8690021X).
- B. Hanin and D. Rolnick, *Complexity of Linear Regions in Deep Networks* (ICML 2019): average linear-region counts along one-dimensional subspaces at random initialization. [PMLR](https://proceedings.mlr.press/v97/hanin19a.html).
- O. Wright, Y. Nakahira, and J. M. F. Moura, *An Analytic Solution to Covariance Propagation in Neural Networks* (AISTATS 2024): an exact covariance formula for nonlinear activations with Gaussian inputs, embedded in a layerwise method that assumes Gaussian activation inputs. [PMLR PDF](https://proceedings.mlr.press/v238/wright24a/wright24a.pdf).
- K. Fischer et al., *Decomposing neural networks as mappings of correlation functions* (Physical Review Research, 2022): how nonlinear layers transfer information among correlation orders. [arXiv](https://arxiv.org/abs/2202.04925).

## Local falsification evidence consulted

- `work/scorefloor_generation/terminal_edgeworth/RESULTS.md`: direct Gaussian, skew, skew+kurtosis, and fourth-order Edgeworth terminal closures; naive analytic corrections are strongly negative, while even target-fitted four-term fold improvement is only about 2.62%.
- `work/mlp_cumulant_propagation/src/mlp_kprop/symb/README.md`: tensor-network formulation and contraction-path remarks.
- `outputs/WHestBench-Quantization-Excursion.md`, `work/swarm/scorefloor_theory.md`, and `sources/research_phase1_top_arc_repo_20260803.md`: incumbent/floor context and prior route eliminations.
