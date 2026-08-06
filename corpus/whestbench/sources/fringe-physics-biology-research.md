# Fringe-operator research for ARC WHestBench

Research date: 2026-08-02. This note records the primary sources, classical mathematical translations, assumptions, and falsifiers used by the recursive estimator-folding program. It deliberately distinguishes an analogy from a proof.

## Competition constraints and prize strategy

- Challenge and score prizes: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
- Algorithmic-prize instructions: https://discourse.aicrowd.com/t/algorithmic-contribution-prize-guidelines-how-arc-judges-these-prizes-discretion-technical-writeups-llm-usage/18041
- Townhall/private-rerun clarification: https://discourse.aicrowd.com/t/townhall-summary-recording/18078
- Current grader releases: https://github.com/AIcrowd/whestbench/releases
- Accounting-boundary question: https://discourse.aicrowd.com/t/rules-clarification-are-operations-on-the-numpy-backed-arrays-reachable-through-flopscope-numpy-inside-the-intended-accounting-boundary/18122

Phase II awards $50,000/$20,000/$10,000 by a fresh private rerun of one designated submission. The separate $20,000 algorithmic-contribution award requires a PDF and exactly one successfully graded Phase-II submission ID. The clean strategy is to use the same mechanistic estimator for both. Receipt of both by one team is not explicitly guaranteed; obtain written organizer confirmation. Prize eligibility requires an OSI-approved source release, and LLM assistance must be disclosed.

## QMC, fractal series, and tau folding

### Randomized QMC

- Art Owen, scrambled-net variance: https://doi.org/10.1137/S0036142994277468
- Takashi Goda, digital nets with antithetics: https://arxiv.org/abs/1509.08570

Nested scrambled nets admit a multiresolution interpretation. If `Q_m` is a randomized prefix estimator, then `D_m = Q_m - Q_(m-1)` has expectation zero. A fixed, development-trained `Q_L + beta*D_L` is therefore an unbiased control. The “fractal” content is an honest Haar-scale series, not a claim of self-similar physics. The falsifier is an unstable or zero held-out coefficient.

### b-adic tent or tau fold

- Goda, Suzuki, and Yoshiki, b-adic tent transform: https://arxiv.org/abs/1312.5850
- Folded digital nets with infinite digit expansions: https://arxiv.org/abs/1407.6086

For binary digits `x=.xi_1 xi_2 ...`, the dyadic fold is `eta_i = xi_(i+1) XOR xi_1`. The 32-bit implementation shifts left and XORs a mask derived from the high bit; it is a finite-grid permutation and preserves discrete-uniform marginals. The strongest rates require smooth Sobolev integrands and suitable higher-order nets. Box-Muller endpoint behavior and deep ReLU kink hyperplanes violate or strain those assumptions, so WHestBench use is exploratory.

Premise result under WHestBench 0.14, matched first five mini networks: raw MSE rose from `4.6903e-7` to `8.0346e-7` (+71%). The branch is killed before any holdout-scale tuning.

## Exact spherical and Hermite physics

### Spherical-radial conditioning

- Spherical-radial integration background: https://doi.org/10.1080/01621459.1997.10474018
- Spherical QMC designs: https://arxiv.org/abs/1208.3267

For a bias-free ReLU network, positive homogeneity gives `F(RU)=R F(U)`. A standard Gaussian decomposes into independent `R~chi_d` and uniform direction `U`, hence `E F(X) = E[R] E[F(U)]`. Rescaling every Gaussianized QMC point to `E[R]` is an exact Rao-Blackwellization for the target distribution. QMC variance improvement is not guaranteed and must be measured.

Premise result on five mini networks: raw MSE changed from `4.6903e-7` to `4.6831e-7` (about 0.15% better), effectively neutral at this rung.

### Gaussian response/Hermite controls

- Price's theorem: https://doi.org/10.1109/TIT.1958.1057444
- Control functionals: https://arxiv.org/abs/1410.2392
- Zero-variance principle: https://arxiv.org/abs/cond-mat/9911396

For deterministic basis `V`, let `S=V^T X` and center `SS^T` by `V^T V`. Gaussian response identities give `nabla_a^2 E[f(X+Va)]|_0 = E[f(X)(SS^T-V^TV)]`. Under the ideal continuous Gaussian law, subtracting any deterministic coefficient contracted with this sample score is exactly unbiased; a poor mean-field response coefficient can increase variance but cannot change the expectation. Antithetic sampling removes odd Hermite components, making degree two a particularly relevant next target. The trace-free version cancels the leading isotropic finite-grid discrepancy of 32-bit midpoint Box-Muller, but floating-point implementation still requires an “ideal-law” qualification. Remove the isotropic direction already handled by radial controls before composition.

## Biological patterning and retinal computation

### Reaction-diffusion and lateral inhibition

- Turing's morphogenesis paper: https://doi.org/10.1098/rstb.1952.0012
- Kondo and Asai, angelfish pattern rearrangement: https://doi.org/10.1038/376765a0
- Delta-Notch lateral-inhibition model: https://doi.org/10.1006/jtbi.1996.0233

Classical translation: local activation plus longer-range inhibition can maintain separated search niches on a graph of estimator mutations. A graph-Laplacian activator/inhibitor scheduler is an offline diversity heuristic, not an accuracy theorem. It survives only if retrospective replay selects full-split winners more reliably than successive halving under equal pilot cost.

### Retinal mosaics, opponent channels, and efficient coding

- MEGF10/11 retinal mosaics and exclusion zones: https://doi.org/10.1038/nature10877
- Decorrelation and efficient retinal coding: https://www.nature.com/articles/nn.3064
- ON/OFF mosaic arrangement from scene statistics and noise: https://doi.org/10.1073/pnas.2105115118

Classical translations:

- opponent channels -> antithetic `x,-x` pairs;
- center-surround -> known-expectation control variates;
- same-type exclusion zones -> select nonredundant control directions in correlation space;
- receptor mosaics -> randomized space-filling directions with preserved marginals.

The strongest proposed biological operator is a cross-fitted “retinal mosaic” selector over first-layer controls that are zero-mean in the continuous-Gaussian ideal. Coefficients and selected controls must be independent of the corrected fold. The 32-bit midpoint Box-Muller implementation has a microscopic finite-grid centering discrepancy, so implementation-level claims must include that qualification.

### Developmental pruning, rescue, and homeostasis

- Complement-dependent synapse elimination: https://pubmed.ncbi.nlm.nih.gov/18083105/
- Microglial activity-dependent pruning: https://pubmed.ncbi.nlm.nih.gov/22632727/
- Homeostatic synaptic scaling: https://www.nature.com/articles/36103

Classical translations:

- developmental overproduction -> generate a broad candidate set;
- activity-dependent pruning -> remove analytically cold neurons only after a pilot test;
- rescue -> reinstate any cold candidate that fires in the independent pilot;
- homeostasis -> fixed variance-per-FLOP allocation with a no-starvation floor.

Pilot-rescued pruning is already the best surviving structural mutation. It is deliberately biased: a truly active intermediate neuron may evade the pilot, and the analytic final-layer fill does not restore omitted upstream paths. Its bias and tails must be evaluated on whole networks. Same-pilot rescue also creates selection dependence; an opposite-scramble mask/evaluation cross-fit can remove that extra selection bias but cannot make the sparsification exact.

## Memristive principles

- Chua's memristor: https://doi.org/10.1109/TCT.1971.1083337
- Physical memristive device: https://www.nature.com/articles/nature06932
- Computing review: https://www.nature.com/articles/nnano.2012.240
- Randomized unbiased continuation: https://web.stanford.edu/~glynn/papers/2015/RheeG15.pdf

A raw cross-sample hysteretic state is rejected because it creates order dependence. The defensible translation is a bounded, fading state used only to choose predictable continuation probabilities in an exact Russian-roulette telescoping estimator. This remains low priority until a coupled approximation hierarchy demonstrates rapidly decaying correction energy.

## Statistical mechanics, renormalization, and response rigor

- Wilson's renormalization review: https://doi.org/10.1103/RevModPhys.47.773
- Deep-information propagation/mean-field correlation maps: https://arxiv.org/abs/1606.05340 and https://arxiv.org/abs/1611.01232
- Multilevel Monte Carlo: https://arxiv.org/abs/1304.5472
- Multifidelity control variates: https://doi.org/10.1137/16M1082469

Legitimate translations are:

- renormalization -> measure residual laws over nested sample and layer scales;
- response theory -> deterministic tangent coefficients multiplying controls that are zero-mean under the stated ideal law;
- order parameters -> gate occupancy, covariance rank, kink proximity, and perturbation susceptibility;
- coarse graining -> an explicitly coupled multilevel estimator, never an uncorrected replacement.

Every physical analogy must identify the ensemble, symmetry or conserved quantity, scale, approximation, measurable signature, rival explanation, and falsifier. A mean-field closure may supply a control coefficient; it cannot replace the fixed finite network without bias.

## Quantum/photopigment boundary

- Rhodopsin vibrational coherence: https://www.nature.com/articles/nchem.2398

Photon absorption in pigment is quantum; image construction downstream is classical biological computation. Useful inspirations are conditioning away nuisance amplitude, opponent pairs, population coding, and explicit noise models. No quantum speedup is claimed because there is no quantum hardware, oracle, or quantum estimator in the submitted method.

## Promotion policy

1. Static legality and worst-case compute check.
2. Two-to-five-network mechanism falsification only.
3. Matched 20-network screen.
4. Whole-network cross-validation on full1000.
5. One frozen evaluation on untouched mini100.
6. Fresh private rerun; no post-holdout mutation.

Report every tested branch, pairwise residual covariance, bootstrap or fold uncertainty, failures, package/version hashes, and all negative results. A small-screen win is not a competition win.
