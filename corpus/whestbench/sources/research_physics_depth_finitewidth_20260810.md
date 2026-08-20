# Research brief: depth-decay of layer influence, finite-width kernel corrections, and coherence collapse in critical ReLU nets

Date: 2026-08-09 (filed under requested name _20260810). Read-only literature sweep: arXiv + web search, full-text fetches via ar5iv for the load-bearing formulas. Consensus search tool not used (medicine-focused corpus, no coverage of this literature). Evidence levels: **[obs]** = formula fetched from the paper's full text this session; **[rep]** = abstract/secondary source only; **[der]** = derived here in a few lines from standard Gaussian moments, shown so you can re-derive.

Our measured facts, restated for reference: (F1) per-layer resampling-influence transmission ~0.87/layer, geometric in layer index l, early layers dominate; (F2) angular correlation length 1.7-2.2x the arccos/NNGP prediction; (F3) output coherence plateau c_32(0) = 0.9747, ~1.5-2 effective dof of 256. Aspect ratio D/n = 32/256 = 0.125.

---

## Q1 — Geometric depth-decay of layer-perturbation influence

### Papers

1. **Depth Degeneracy in Neural Networks: Vanishing Angles in Fully Connected ReLU Networks on Initialization** — Jakub & Nica, 2023/2024, arXiv:2302.09712 (JMLR vol. 25, no. 239). The central Q1 reference: exact per-layer angle-contraction recursion at finite width, exponential decay where infinite width predicts polynomial.
2. **Network Degeneracy as an Indicator of Training Performance: Comparing Finite and Infinite Width Angle Predictions** — Jakub & Nica, 2023, arXiv:2306.01513. Companion paper with a practical algorithm predicting degeneracy level for any FC ReLU architecture.
3. **On the Impact of the Activation Function on Deep Neural Networks Training** — Hayou, Doucet, Rousseau, ICML 2019, arXiv:1902.06853. Proves the infinite-width polynomial rate 1 - c_l ~ 9π²/(2l²) for ReLU at the edge of chaos (EOC).
4. **Exponential expressivity in deep neural networks through transient chaos** — Poole, Lahiri, Raghu, Sohl-Dickstein, Ganguli, NeurIPS 2016, arXiv:1606.05340. Source of the correlation map c → f(c) and χ₁ = f'(c*); the origin of the "naive flat" prediction we reject.
5. **Deep Information Propagation** — Schoenholz, Gilmer, Ganguli, Sohl-Dickstein, ICLR 2017, arXiv:1611.01232. Depth scale ξ_c = -1/ln χ₁; χ₁ = 1 at ReLU criticality → ξ_c = ∞ (flat), the prediction our data rejects at 21-31x.
6. **Toward Deeper Understanding of Neural Networks: The Power of Initialization and a Dual View on Expressivity** — Daniely, Frostig, Singer, NeurIPS 2016, arXiv:1602.05897. [rep] Independent derivation of the ReLU angle-contraction ("dual activation") map.
7. **Products of Many Large Random Matrices and Gradients in Deep Neural Networks** — Hanin & Nica, Comm. Math. Phys. 2020, arXiv:1812.05994. Log of the output norm is asymptotically Gaussian with mean/variance set by Σ 1/n_l — the D/n-controlled log-normal machinery behind finite-width departures.
8. **Are All Layers Created Equal?** — Zhang, Bengio, Singer, JMLR 2022, arXiv:1902.01996. [rep] Empirical layer re-initialization/re-randomization robustness (trained nets): layers split into "critical" vs "ambient". Closest published use of the resampling probe itself; no theory for random nets.

### The formulas

**Infinite-width correlation map (Poole/Schoenholz/Daniely; Cho-Saul kernel).** For bias-free He-init ReLU, correlation c = cos θ between two activation vectors evolves as
  f(c) = [sin θ + (π - θ) cos θ] / π,  θ = arccos c.
Exact derivative: **f'(c) = 1 - θ/π** [der: d/dθ of the numerator = -(π-θ)sin θ, times dθ/dc = -1/sin θ]. At the fixed point θ = 0: χ₁ = f'(1) = 1 — the naive flat prediction. Off the fixed point the contraction is strictly < 1: the sqrt-singularity of the kernel near c = 1 makes the approach polynomial, and the local perturbation-transmission factor at ambient angle θ is 1 - θ/π per layer.

**Infinite-width rate (Hayou et al., Prop. 1) [obs]:** on the EOC (σ_b², σ_w²) = (0, 2),
  1 - c_l ~ 9π² / (2 l²)  as l → ∞ (equivalently θ_l ≈ 3π/l).

**Finite-width recursion (Jakub & Nica, Approximation 1) [obs]:**
  ln sin²(θ^(ℓ+1)) ≈ ln sin²(θ^ℓ) - (2/(3π)) θ^ℓ - ρ(n_ℓ),
  ρ(n) := ln((n+5)/(n-1)) - 10n/(n+5)² + 6n/(n-1)² = 2/n + O(n⁻²),
with per-layer fluctuation variance σ²(θ, n) = 8/n + O(θ/n), and the refined mean [obs]
  μ(θ,n) = ln sin²θ - (2/(3π))θ - ρ(n) - 8θ/(15πn) - (2/(9π²) - 68/(45π²n))θ² + O(θ³).
Symbols: θ^ℓ = angle between the two activation vectors at layer ℓ; n_ℓ = width. Consequence [obs]: θ^ℓ ≤ exp(-Σᵢ ρ(nᵢ)) — **exponential (geometric) decay at finite width**, versus θ_l ~ 1/l at infinite width ("qualitatively very different" — their words). Cross-check: dropping ρ and integrating d ln sin²θ/dℓ = -(2/(3π))θ reproduces θ_l ~ 3π/l, i.e., exactly Hayou's law — the two fetched sources agree independently.

### Does it predict 0.87 at width 256?

Two candidate identifications of the measured transmission t = 0.87 = exp(-0.139):

- (a) **Correlation-perturbation transmission** t = f'(c) = 1 - θ/π ⇒ θ_eff ≈ 0.41 rad (23°).
- (b) **Jakub-Nica sin²θ flow** t = exp(-(2/(3π))θ - 2/n); at n = 256 the width term is only 0.0078, so θ_eff ≈ 0.62 rad (36°).

Both require a sustained O(1) ambient angle — which finite width supplies (the angle never sits at the θ = 0 fixed point; fluctuations of size ~ sqrt(8/n) per layer and the O(1) angles injected by resampling keep the system off the singular point). Note a structural point our team should confront: careful infinite-width theory (Hayou rate) predicts resampling-influence 1 - c_out ~ 9π²/(2(D-l)²), i.e., **late layers dominate, power law in distance-to-output** — not flat, and *inverted* in ordering relative to our early-dominant geometric profile. Neither naive nor careful mean-field matches; the finite-width exponential mechanism is the only published candidate with the right shape.

**VERDICT: PARTIAL.** No paper derives the layer-*resampling* influence profile per se. Jakub & Nica derive the finite-width geometric contraction that is its natural generator, with explicit rate formulas; the χ₁ = 1 flat prediction is definitively superseded in the literature.

**Computation to run:** (i) Measure the ambient angle profile θ_ℓ in our width-256 nets (mean angle between activations for input pairs at the measurement separation, plus the resample-injected angle at each ℓ). (ii) Iterate Jakub-Nica Approximation 1 (with the μ(θ,n) refinement) from θ⁰ and compute the predicted influence profile I(l) ∝ sin²θ evaluated along the downstream flow after an O(1) resample at layer l; fit a single geometric rate to the predicted I(l) over l = 0..31 and compare to 0.869/0.879/0.876 and the 95x span. (iii) Discriminate (a) vs (b): check whether the measured per-layer transmission at layer l tracks 1 - θ_l/π or exp(-(2/(3π))θ_l - 2/256) layer-by-layer. If the fitted θ_eff ≈ 0.41-0.62 rad matches the measured mid-network angles, the law is DERIVED by composition of published results.

---

## Q2 — Finite-width (D/n) corrections to the NNGP kernel

### Papers

1. **Non-Gaussian processes and neural networks at finite widths** — Yaida, MSML 2020, arXiv:1910.00019. First systematic 1/n Edgeworth-type corrections to the NNGP for arbitrary depth/nonlinearity; corrections compound with depth.
2. **The Principles of Deep Learning Theory** — Roberts, Yaida, Hanin, CUP 2022, arXiv:2106.10165. The canonical D/n effective theory: near-Gaussian output distributions with the **depth-to-width ratio as the expansion parameter controlling all deviations from NNGP**; four-point vertex grows ~ l/n at criticality.
3. **Finite Depth and Width Corrections to the Neural Tangent Kernel** — Hanin & Nica, ICLR 2020, arXiv:1909.05989. Kernel fluctuations at init are exponential in D/n; NNGP/NTK description fails as D/n grows.
4. **Asymptotics of Wide Networks from Feynman Diagrams** — Dyer & Gur-Ari, ICLR 2020, arXiv:1909.11304. Diagrammatic bookkeeping for 1/n corrections to correlation functions.
5. **The Neural Covariance SDE: Shaped Infinite Depth-and-Width Networks at Initialization** — Li, Nica, Roy, NeurIPS 2022 (oral), arXiv:2206.02768. In the joint limit D, n → ∞ with D/n fixed, the 2-input covariance matrix is a *random* object solving an SDE; unshaped ReLU degenerates — the exact regime our nets live in.
6. **Precise characterization of the prior predictive distribution of deep ReLU networks** — Noci, Bachmann, Roth, Nowozin, Hofmann, NeurIPS 2021, arXiv:2106.06615. [rep] Closed forms (Meijer-G) for finite-width ReLU output law; moments → normal-log-normal mixture at large depth.
7. **Random Fully Connected Neural Networks as Perturbatively Solvable Hierarchies** — Hanin, 2022, arXiv:2204.01058. [rep — full text exceeded fetch limit] Exact solvable moment hierarchies for finite-width ReLU nets; kernel moment recursions to all orders in 1/n.

### The formula and the numerical check

Per-layer kernel fluctuation for He-init ReLU [der, 5 lines]: given layer-l activations, K_{l+1} = (2/n) Σᵢ φ(zᵢ)² with zᵢ iid N(0, K_l); E[φ(z)²] = K/2, E[φ(z)⁴] = 3K²/2 ⇒ Var[φ(z)²] = 5K²/4 ⇒ **Var[K_{l+1}|K_l] = (5/n) K_l²**. Compounding multiplicatively (the Hanin-Nica log-normal structure [rep]):
  E[K_D²]/E[K_D]² ≈ Π (1 + 5/n) ≈ **exp(5D/n)**,  Var[ln K_D] ≈ 5D/n.
At our aspect ratio: exp(5 · 0.125) = exp(0.625) = **1.87** — squarely inside our measured 1.7-2.2x correlation-length inflation. This is suggestive arithmetic, not a published identity: no paper we found states "angular correlation length inflates by exp(5D/n)^(1/2-ish)" — the mapping from quenched kernel fluctuations (plus the collapsed coherent direction) to the *angular correlation length of the output field* is exactly the missing link.

**VERDICT: PARTIAL.** The D/n expansion exists and is quantitative (Yaida, RYH, Hanin-Nica, covariance SDE), the expansion parameter is our 0.125, and the leading ReLU fluctuation constant (5) lands the right magnitude. Nobody computes our specific observable.

**Computation to run:** (i) Simulate/solve the Li-Nica-Roy covariance SDE (or just iterate the 2-input kernel recursion with the per-layer noise Var = 5K²/n and the angle recursion above) for pairs of inputs at angular separation s; compute the ensemble-averaged output correlation C(s) and extract the correlation length; compare the inflation factor to 1.7-2.2x. (ii) Cheaper closed-form attempt: model the finite-width output field as (coherent scalar field g(x)) ⊗ (fixed random direction) + incoherent residual with NNGP statistics, weights (c, 1-c) from F3, and compute the correlation length of the mixture — if it reproduces 1.9x, F2 is a corollary of F3.

---

## Q3 — Near-rank-1 coherence collapse of deep critical ReLU outputs

### Papers

1. **Jakub & Nica**, arXiv:2302.09712 (above). The collapse *is* their depth degeneracy: at finite width the network approaches a constant (rank-1 in function space) exponentially fast, rate ρ(n) + angle term per layer.
2. **On the infinite-depth limit of finite-width neural networks** — Hayou, TMLR 2022, arXiv:2210.00688. [rep] Fixed width, D → ∞: pre-activations converge to activation-dependent non-Gaussian diffusions; the infinite-depth-then-width and width-then-depth limits do not commute — the degenerate finite-width regime is a genuine distinct limit.
3. **Batch Normalization Provably Avoids Rank Collapse for Randomly Initialized Deep Networks** — Daneshmand, Kohler, Bach, Hofmann, Lucchi, NeurIPS 2020, arXiv:2003.01652. Proves unnormalized deep nets suffer rank collapse of representations at init (outputs collinear across inputs — our F3 phenomenon), with BN as the countermeasure.
4. **Li, Nica, Roy**, arXiv:2206.02768 (above). Unshaped ReLU covariance degenerates in the D/n limit; quantifies the onset — the reason "shaping" (φ ≈ identity + s/sqrt(n) kink) was invented.
5. **Rapid training of deep neural networks without skip connections or normalization layers using Deep Kernel Shaping** — Martens, Ballard, Desjardins, Swirszcz, Dalibard, Sohl-Dickstein, Schoenholz, 2021, arXiv:2110.01765. [rep] Diagnoses the degenerate approach of deep kernels to constants (q/c maps) and engineers activations to prevent it.
6. **Signal Propagation in Transformers: Theoretical Perspectives and the Role of Rank Collapse** — Noci et al., NeurIPS 2022, arXiv:2206.03126. [rep] Rank collapse of token representations in transformers — same phenomenon, different architecture; useful for framing generality.

**VERDICT: PARTIAL (phenomenon derived, our specific observable not).** The collapse of deep critical ReLU nets toward a rank-1/constant function is well-established with rates; the specific across-output-neuron coherence c_D(0) and effective-dof count are not computed anywhere we found.

**Computation to run:** iterate the Jakub-Nica recursion to depth 32 at n = 256 from the empirical initial angle and predict 1 - c_32; compare to our 0.0253. Internal consistency check from our own numbers [der]: 0.87^32 = 0.0116, and ~2 × 0.0116 = 0.023 ≈ 1 - 0.9747 — F1's geometric rate compounded over depth lands on F3's plateau, strong evidence F1 and F3 share one mechanism (and that a single fitted rate is self-consistent across observables).

---

## MECHANISM-GENERATOR — published depth-decay exploits outside the closed family

Closed family (excluded): Gaussian closures at any insertion point, design perturbation, rotation selection/weighting, RQMC/lattices, harmonic control variates, mid-layer exact composition, offline correctors, terminal smoothing.

1. **Multilevel Monte Carlo over depth levels** — Giles, *Multilevel Monte Carlo path simulation*, Oper. Res. 56(3), 2008; survey: Giles, Acta Numerica 2015. Treat depth-truncated networks (depth-k head + cheap tail closure) as MLMC levels; the telescoping level-difference variance is exactly our influence tail, decaying like 0.87^k while per-level cost grows only linearly. Geometric variance decay vs linear cost is MLMC's best case: total cost O(ε⁻²) dominated by the coarsest (shallow) level. Our closed list has mid-layer exact composition and offline correctors but no *telescoped multi-resolution ladder with budget allocation across levels* — this is the standout addition.
2. **Randomized truncation / Russian roulette / randomized telescopes** — Rhee & Glynn, *Unbiased estimation with square root convergence for SDE models*, Oper. Res. 63(5), 2015; Beatson & Adams, *Efficient Optimization of Loops and Limits with Randomized Telescoping Sums*, ICML 2019, arXiv:1905.07006 (von Neumann-Ulam ancestry). Unbiased estimators of an infinite/deep telescoping sum by sampling a random truncation depth; optimal truncation distributions are geometric with parameter matched to the decay rate — i.e., our measured 0.87 *is* the tuning constant. Converts any depth-truncated surrogate into an unbiased estimator at O(1) expected cost.
3. **ANOVA/effective-dimension-weighted QMC constructions** — Caflisch, Morokoff, Owen, *Valuation of mortgage-backed securities using Brownian bridges to reduce effective dimension*, J. Comput. Finance 1997; Sloan & Woźniakowski weighted spaces (1998); Kuo-Nuyens fast CBC. RQMC/lattices are closed, but the *weight assignment* is a separate published lever: feed the measured per-layer variance shares (∝ 0.87^l, layers 0-4 = 46%) as product weights γ_l into the CBC lattice construction, and order the integration variables early-layers-first (Brownian-bridge-style reordering by influence). Published theory says the worst-case error constant then depends on Σ γ_l, not dimension — geometric γ makes 8192-dimensional weight space effectively ~15-dimensional.
4. **Feynman-Kac / SMC particle branching across layers** — Del Moral, *Feynman-Kac Formulae*, Springer 2004. Treat layer index as time and run a particle system over weight realizations: branch/replicate particles at early layers (high influence) and share/coalesce randomness at late layers (low influence — their noise self-averages under the 0.87 contraction). The "tree of networks sharing early-layer weights, branching late" gives cheap Rao-Blackwellization of low-influence layers; distinct from design perturbation because the allocation schedule is set by the measured transmission profile.
5. (Half-step, closest to closed territory) **Active-subspace / dominant-block stratification** — Constantine, *Active Subspaces*, SIAM 2015: stratify or importance-sample only the layer-0-4 weight block that carries 46% of variance. Flag: may collide with the closed "design perturbation" item; kept for completeness.

---

## One-line synthesis

The naive χ₁ = 1 flat law is dead in the literature too; the published replacement is the finite-width angle recursion ln sin²θ^(ℓ+1) = ln sin²θ^ℓ - (2/(3π))θ^ℓ - 2/n (Jakub-Nica), whose geometric contraction off the fixed point, the exp(5D/n) ReLU kernel-fluctuation factor (= 1.87 at our D/n = 0.125), and the documented rank-collapse endpoint jointly match the shape and magnitude of all three measured facts — pending the three numbered check computations above.
