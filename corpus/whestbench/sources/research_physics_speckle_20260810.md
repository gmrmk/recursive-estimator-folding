# Research brief: finite-width NN fields as speckle; speckle averaging theory; mean estimation for correlated fields on spheres

Filed: 2026-08-09 (filename per task spec). Scope: ~20-minute web sweep (arXiv, publisher pages, standard references via web search).
Evidence levels: paper-content statements below are REPORTED (from abstracts/search extracts, not full-text reads unless noted); formulas tagged [standard] are textbook results; anything tagged [derived here] is our own algebra and should be spot-checked before load-bearing use.

Context (our measured facts, given): width-256 depth-32 He-init bias-free ReLU MLPs on the input sphere; neuron-averaged output fluctuation field behaves as REAL-amplitude speckle — per-direction energies chi^2_1 (KS 0.007-0.016, n=64,512), statistically homogeneous (near/far ReLU-boundary energy ratio 1.00 vs 850x sensitivity), angular correlation length 36-46 deg vs 21 deg from the infinite-width arccos kernel. Design min angle 86 deg, so spacing/xi ~ 2.

---

## Q1 — Finite-width random NN functions as Gaussian random fields / speckle on the sphere

### Key papers

1. **Non-Gaussian processes and neural networks at finite widths** — S. Yaida, MSML 2020, arXiv:1910.00019. First systematic 1/n perturbative expansion of the finite-width prior in function space; the four-point (connected) correlation is the leading non-Gaussian correction and kernels "propagate finite-size corrections forward through the network" rather than concentrating layerwise.
2. **Finite size corrections for neural network Gaussian processes** — J. Antognini, 2019, arXiv:1908.10030. One-hidden-layer output density = Gaussian perturbed by the 4th Hermite polynomial with amplitude ~ 1/n; direct evidence that per-direction marginals stay near-Gaussian at large width (consistent with our chi^2_1 energies).
3. **Random fully connected neural networks as perturbatively solvable hierarchies** — B. Hanin, JMLR 2024, arXiv:2204.01058. Sharp cumulant hierarchy in powers of 1/n for deep ReLU-class nets; the depth-to-width ratio L/n is the effective expansion parameter controlling both single-neuron fluctuation scale and inter-neuron correlations. Our L/n = 32/256 = 0.125, i.e. NOT negligible — a candidate mechanism for the measured correlation-length broadening (36-46 vs 21 deg); unproven for our setup until the O(L/n) correction is computed from the paper's recursions (settling check named in Verdict Q1b).
4. **The Neural Covariance SDE: shaped infinite depth-and-width networks at initialization** — M. B. Li, M. Nica, D. Roy, NeurIPS 2022, arXiv:2206.02768. In the joint depth-width limit the covariance (kernel) itself becomes a stochastic process; quantifies kernel fluctuation/broadening at fixed L/n — second supporting frame for the xi discrepancy.
5. **Gaussian random field approximation via Stein's method with applications to wide random neural networks** — K. Balasubramanian, L. Goldstein, N. Ross, A. Salim, Appl. Comput. Harmon. Anal. 2024, arXiv:2306.16308. The closest formal statement of "random NN = Gaussian random field on the input domain": Wasserstein-type bounds on the whole field (not just finite-dimensional marginals), with sphere-domain results.
6. **Rate of convergence of polynomial / ReLU networks to Gaussian processes** — A. Klukowski, COLT 2022, arXiv:2111.03175. W2 rates for one-layer nets with inputs on the sphere via spherical harmonics + Stein kernels; power-law rate in n for ReLU. The spherical-harmonic decomposition of the arccos kernel here is the reference for the infinite-width angular correlation we compare against.
7. **Quantitative Gaussian approximation of randomly initialized deep neural networks** — A. Basteri, D. Trevisan, Machine Learning 2024, arXiv:2203.07379. W2 distance of a deep finite net to its NNGP scales like the sum over layers of width^{-1/2}-type terms — depth accumulates finite-width error, again pointing at depth-accumulated kernel distortion.
8. **Exponential expressivity in deep neural networks through transient chaos** — B. Poole, S. Lahiri, M. Raghu, J. Sohl-Dickstein, S. Ganguli, NeurIPS 2016, arXiv:1606.05340. The infinite-width layer-by-layer angle map c_{l+1} = f(c_l); the canonical account of how depth reshapes the angular correlation function of the composed arccos kernel — the baseline our 21-deg prediction comes from.
9. (Adjacent, newer) **Fractal and regular geometry of deep neural networks** (arXiv:2504.06250) and **Phase transitions in the fluctuations of functionals of random neural networks** (arXiv:2604.19738) — geometry/functional-fluctuation statistics of NN-GP fields on spheres; nearest current literature to "landscape statistics of random ReLU fields."

### Extracted content

- Finite-width function-space priors are Gaussian + O(1/n) Edgeworth-type corrections; connected 4-point function is the leading correction (Yaida; Antognini). [reported]
- The controlling small parameter for deep nets is L/n, not 1/n (Hanin; Li-Nica-Roy). At L/n = 0.125 the kernel itself has O(10%) random distortion per realization. [reported; magnitude is our reading]
- Quantitative field-level (not marginal-level) GP approximation exists with explicit rates on the sphere (Balasubramanian et al.; Klukowski; Basteri-Trevisan; Eldan-Mikulincer-Schramm arXiv:2102.08668). [reported]

### Verdicts

- VERDICT Q1a: The GRF framing of random finite-width networks on the sphere EXISTS and is quantitative (Stein's-method field bounds, cumulant hierarchies). Nobody in the swept literature phrases it as SPECKLE or tests chi^2_1 per-direction energies / homogeneity across ReLU activation boundaries — that framing and those two measurements appear novel.
- VERDICT Q1b: The measured xi (36-46 deg) exceeding the infinite-width prediction (21 deg) has a ready-made candidate mechanism: O(L/n) kernel fluctuation/broadening (Hanin 2204.01058 recursions; covariance-SDE picture). A quantitative check is computable from the published recursions — worth one offline derivation. [hypothesis, upgrade path named]
- VERDICT Q1c: No prior derivation of an angular correlation function for the neuron-averaged fluctuation field specifically was found; the closest objects are kernel fluctuation statistics.

---

## Q2 — Speckle averaging and integration theory (optics)

### Key papers

1. **Some fundamental properties of speckle** — J. W. Goodman, J. Opt. Soc. Am. 66(11):1145, 1976. The canonical source for first/second-order speckle statistics and aperture-integrated speckle.
2. **Speckle Phenomena in Optics: Theory and Applications** — J. W. Goodman, 2007 (book, 2nd ed. 2020). Chapter-level treatment of degrees-of-freedom M, integrated speckle, and all diversity mechanisms.
3. **Speckle contrast reduction in laser projection displays** — J. I. Trisnadi, Proc. SPIE 4657, 2002. The engineering diversity-budget formulation: total M multiplies over independent channels; polarization contributes at most a factor 2 in M (sqrt(2) in contrast).
4. **Effect of incidence/observation angles and angular diversity on speckle reduction by wavelength diversity in laser projection systems** — Tran, Svensen, Chen, Akram, Opt. Express 2017 (PubMed 29245877). Measured NON-independence of wavelength and angle diversity: channels only multiply when independent; the cross-coupling reduces the joint gain.
5. **Diffusing wave spectroscopy: a unified treatment on temporal sampling and speckle ensemble methods** — arXiv:2010.13979. Explicit N_independent (number-of-speckle-grains) estimator-variance accounting on detector arrays: error ~ sqrt(Var/N_independent).
6. **Imaging with nature: compressive imaging using a multiply scattering medium** — Liutkus et al., Sci. Rep. 4:5552, 2014, arXiv:1309.0425. Speckle field as a random compressive measurement operator (transmission matrix) — the "measure random projections instead of points" paradigm.
7. **Characterization of the angular memory effect of scattered light in biological tissues** — arXiv:1502.00270. Angular decorrelation range = the angular coherence cell; sets when two illumination angles give independent speckle.

### Extracted formulas [standard]

- Point statistics: fully developed COMPLEX (polarized) speckle intensity is exponential, contrast C = sigma_I/<I> = 1. A REAL-amplitude Gaussian field has per-point energy ~ chi^2_1 and C = sqrt(2). Our chi^2_1 finding is exactly the real-field case.
- Aperture-integrated speckle: for W = (1/A) int_A I, Var(W) = <I>^2 / M with
  **1/M = (1/A^2) ∬_A |mu(r1 - r2)|^2 d r1 d r2**, and for A >> A_c: **M ≈ A / A_c**, coherence area **A_c = ∫ |mu(Δ)|^2 d^2Δ** (mu = complex coherence factor). This is the N_eff = area / coherence-cell law.
- Real-field version: replace |mu|^2 by rho^2 (field correlation squared) and Var(W) = 2<E>^2 / M (chi^2 with M effective DOF).
- Discrete design version [derived here, one line]: for n sample energies e_i at angles theta_ij,
  **Var(mean e) = (2<E>^2/n) [1 + (1/n) Σ_{i≠j} rho^2(theta_ij)]**, i.e. **N_eff = n / (1 + (n-1) · mean rho^2)**.
  KEY POINT: for ENERGY averaging the relevant correlation is rho^2, not rho. At design spacing 86 deg with xi(field) 36-46 deg, rho(86) is already small and rho^2(86) is second-order small — the current design is within ~1-2% of fully independent averaging. [derived here from measured numbers; check against measured rho(86)]
- Diversity budget: **M_total = M_space × M_polarization × M_wavelength × M_angle** when channels are mutually independent; contrast falls as 1/sqrt(M_total). Polarization: M ≤ 2. Wavelength channels independent when separation exceeds the spectral decorrelation width (path-spread-limited); angle channels independent when separation exceeds the angular memory-effect range. Tran 2017: wavelength × angle are NOT independent in general — budget multiplication must be verified channel-pair by channel-pair.

### Verdicts

- VERDICT Q2a: The standard machinery transfers cleanly: N_eff = area/coherence-cell; on the sphere, N_eff = (total design "area") / (coherence cap of radius ~xi), with the rho^2 refinement above for energies.
- VERDICT Q2b: Our design (86-deg spacing, xi 36-46) is in the SPARSE regime — samples already near-independent; independent-averaging theory says the remaining slack from decorrelation is ~1%, so denser angle packing down to ~xi adds samples at essentially full 1/n value, and below ~xi it saturates.
- VERDICT Q2c: The speckle-metrology lever beyond independent averaging is DIVERSITY — adding independent channels, not more samples of one channel. Mapping: multiple rotations = angle diversity (we already do); multiple radii = wavelength diversity (helps iff the radial correlation decays — measure the radial decorrelation length first); fresh weight draws = changing the diffuser (helps only if the estimand averages over initializations). Tran 2017's warning transfers: radius × rotation diversity may not multiply — verify joint decorrelation empirically.

---

## Q3 — Mean estimation / quadrature for isotropic random fields; kriging vs equal weights

### Key papers

1. **Designs for regression problems with correlated errors** — J. Sacks, D. Ylvisaker, Ann. Math. Statist. 37:66-89 (1966) and sequel (1968). The founding asymptotic theory of optimal observation points under correlated errors; regular design sequences as quantiles of a density.
2. **Multivariate integration and approximation for random fields satisfying Sacks-Ylvisaker conditions** — K. Ritter, G. Wasilkowski, H. Wozniakowski, Ann. Appl. Prob. 5(2), 1995. Sharp minimal-error bounds for integrating random fields; the dense-regime (spacing << xi) theory.
3. **On large-sample estimation for the mean of a stationary random sequence** — R. K. Adenstedt, Ann. Statist. 2:1095-1107, 1974. BLUE of the mean vs sample mean; generalizes Grenander-Szego: the SAMPLE MEAN IS ASYMPTOTICALLY EFFICIENT whenever the spectral density is positive and continuous at frequency zero (short-range dependence); inefficiency appears only for long-memory spectra f(l) ~ l^nu, where Var(BLUE) ~ n^{-nu-1}.
4. **Asymptotic behavior of the variance of the BLUE for the mean of stationary processes** — arXiv:2604.17705 (2026). Current sharp statement of the same program.
5. **Optimal designs in regression with correlated errors** — H. Dette, A. Pepelyshev, A. Zhigljavsky, Ann. Statist. 44(1), 2016 (+ JASA companion). Modern exact/asymptotic optimal design + weighting theory with correlated observations.
6. **QMC designs: optimal-order quasi Monte Carlo integration schemes on the sphere** — J. Brauchart, E. Saff, I. Sloan, R. Womersley, Math. Comp. 83:2821, 2014, arXiv:1208.3267. EQUAL-WEIGHT rules on S^d achieve the optimal worst-case rate O(N^{-s/d}) in Sobolev spaces — equal weights are rate-optimal on the sphere; later work allows positive weights with no rate improvement.
7. (Bayesian-quadrature form of kriging for integrals) **Bayes-Hermite quadrature** — A. O'Hagan, J. Stat. Plann. Inf. 29:245, 1991; survey: Briol, Oates, Girolami, Osborne, Sejdinovic, "Probabilistic integration," Statist. Sci. 34(1), 2019. Optimal weights w = K^{-1} k-bar minimize posterior variance of the integral given a known covariance.

### Extracted formulas [standard unless tagged]

- BLUE of a constant mean from y ~ (mu·1, Sigma): **mu_hat = (1' Sigma^{-1} 1)^{-1} 1' Sigma^{-1} y**, **Var_BLUE = (1' Sigma^{-1} 1)^{-1}**. Equal weights: **Var_eq = 1' Sigma 1 / n^2**.
- Exactness condition: **equal weights ARE the BLUE iff Sigma 1 = c 1** (the all-ones vector is an eigenvector, i.e. all row sums of Sigma equal). For an isotropic covariance and a design invariant under a symmetry group acting transitively on the points (orbits, spherical designs), row sums are automatically equal — kriging weights give EXACTLY ZERO gain.
- Perturbative gain [derived here; verify]: write Sigma = sigma^2 (I + R), r_i = (R 1)_i = Σ_{j≠i} rho(theta_ij). Then to second order in R:
  **Var_eq − Var_BLUE ≈ (sigma^2/n^2) Σ_i (r_i − r_bar)^2**, i.e. **relative gain ≈ empirical variance of the row sums {r_i}**.
  The gain is controlled entirely by the HETEROGENEITY of total correlation seen by each point, not by the correlation level itself.
- Bayesian-quadrature note: for estimating the full-sphere average of f under an isotropic kernel, k-bar_i = const for every design point, so optimal weights ∝ K^{-1} 1 — same structure, same conclusion as the BLUE-of-mean case.
- Sacks-Ylvisaker: superefficient rates from known covariance arise in the DENSE regime (spacing << xi), via regular sequences with density tuned to the covariance's mean-square smoothness. Not our regime.

### Verdicts

- VERDICT Q3a (the standard answer): kriging/BLUE with known covariance beats equal weights ONLY through row-sum heterogeneity. When spacing > xi (correlations at design distances small) AND the design is near-symmetric, the gain is second-order small; for exactly group-invariant designs it is exactly zero. Adenstedt/Grenander: for short-range correlation the plain mean is asymptotically efficient anyway.
- VERDICT Q3b (our numbers): at spacing/xi ~ 2 (rho(86 deg) roughly 0.1-0.25 depending on correlation shape), predicted relative gain ≈ Var_i(r_i) — for a near-uniform rotation design this is well under 1%. Decisive one-evening test: from the measured covariance compute both (1' Sigma^{-1} 1)^{-1} and 1' Sigma 1 / n^2 and compare. No simulation needed.
- VERDICT Q3c: equal-weight designs are rate-optimal for sphere integration in the deterministic worst-case frame too (Brauchart et al.) — there is no hidden asymptotic win from weighting on the sphere.

---

## MECHANISM-GENERATOR (outside the closed list: Gaussian closures, design perturbation, rotation selection/weighting, RQMC/lattices, harmonic CVs, mid-layer exactness, offline correctors, terminal smoothing)

1. **Kriging-weights / BLUE with the measured covariance.** Distinctness: it is the OPTIMAL COMPLETION of the "rotation selection/weighting" family, not a new mechanism — same decision variables (weights on sample points), optimality now certified by the covariance. Predicted gain at spacing/xi ~ 2: ≈ empirical variance of correlation row sums; ~0 for symmetric designs, sub-1% for near-symmetric ones (formula above). Recommendation: run the two-formula comparison from the measured Sigma as a cheap kill-test, then close the family with a proof-grade number instead of a verdict-by-analogy.
2. **Diversity channels (genuinely outside the list).** Speckle metrology's only beyond-averaging lever is adding INDEPENDENT physical channels and multiplying M. Analogs: (a) radius diversity — sample several radii; value contingent on measured radial decorrelation (measure first; the arccos kernel is homogeneous of known degree in radius for bias-free ReLU, so radial correlation may be near 1 — if so this channel is dead and that is worth knowing); (b) initialization/seed diversity — only if the estimand averages over draws; (c) the independence warning (Tran 2017): joint channels need not multiply — verify rho_joint = rho_angle × rho_radius empirically before budgeting.
3. **Negative-correlation pairing.** Real-amplitude fields (unlike speckle intensity, whose correlations are nonnegative) admit rho(theta) < 0; if the MEASURED angular correlation has a negative lobe, placing sample pairs at that angle cancels variance beyond 1/n — a mechanism speckle optics cannot use and none of the closed families exploits explicitly. One empirical check of the measured rho(theta) near its tail decides. (The infinite-width arccos-1 kernel is nonnegative with k(pi) = 0, so the prior expectation is NO negative lobe — but the measured finite-width field is the object that matters.)
4. **Design-density headroom from the N_eff law.** The rho^2-for-energies fact means the design is currently UNDER-dense by the speckle criterion: additional rotations remain ~fully independent until pairwise angles approach ~xi (36-46 deg), i.e. roughly the 86 deg spacing could be halved before decorrelation losses bite. This is a sizing rule, not a new estimator, but it bounds what any weighting scheme can recover: at most the 1-2% currently lost to residual correlation.
5. **Cap-averaging / finite-aperture probes.** Replacing point evaluations with small-cap averages is the optics analog of a finite detector aperture (each probe gains its own M = A_cap/A_c). Flag: this is adjacent to "terminal smoothing" in the closed list — include only if their kill of terminal smoothing was about output smoothing rather than input-domain aperture integration.
6. **Known-covariance superefficiency (Sacks-Ylvisaker regime).** Real gains from a known covariance exist only when sampling DENSER than xi (regular sequences tuned to kernel smoothness). If the budget ever allows spacing << 40 deg, the S-Y/Ritter theory gives the rate schedule; until then it is inapplicable.
7. **L/n kernel-fluctuation derivation (understanding, feeds items 1-3).** Hanin's arXiv:2204.01058 recursions permit computing the finite-width correction to the angular correlation at L/n = 0.125 — potentially explaining 36-46 vs 21 deg and yielding a PREDICTED covariance model (shape + negative-lobe question) instead of a purely measured one, tightening any weighting/pairing analysis.

## Sources (primary URLs used)

- arXiv:1910.00019, arXiv:1908.10030 (via Semantic Scholar), arXiv:2204.01058, arXiv:2206.02768, arXiv:2306.16308, arXiv:2111.03175, arXiv:2203.07379 (Springer ML 2024), arXiv:2102.08668, arXiv:1606.05340, arXiv:2504.06250, arXiv:2604.19738
- Goodman JOSA 66:1145 (opg.optica.org/abstract.cfm?URI=josa-66-11-1145); Goodman, Speckle Phenomena in Optics (book); Trisnadi SPIE 2002 (siliconlight.com PDF); Tran et al. Opt. Express 2017 (PubMed 29245877); arXiv:2010.13979; Liutkus et al. Sci. Rep. 4:5552 / arXiv:1309.0425; arXiv:1502.00270
- Sacks-Ylvisaker 1966/1968 (via projecteuclid); Ritter-Wasilkowski-Wozniakowski AAP 1995 (projecteuclid aoap/1177004776); Adenstedt QAM 1974 (ams.org/journals/qam/1974-32-03); arXiv:2604.17705; Dette-Pepelyshev-Zhigljavsky Ann. Statist. 44(1) 2016 (projecteuclid 15-AOS1361); Brauchart-Saff-Sloan-Womersley Math. Comp. 83:2821 / arXiv:1208.3267; O'Hagan 1991; Briol et al. Statist. Sci. 2019
