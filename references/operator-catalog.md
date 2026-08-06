# Cross-Domain Operator Catalog

Use this catalog to turn evocative language into falsifiable estimator changes. These are hypotheses, not automatic improvements.

## Fractal and multiscale series

Classical translation: nested dyadic sample prefixes, telescoping differences, wavelet/Faber-Schauder decompositions, and multilevel Monte Carlo.

For nested estimates `Y_l` at `N_l = 2^l`, inspect increments `Delta_l = Y_l - Y_(l-1)`. A valid multilevel estimator uses explicit coupling and accounts for every level. A scale-consistency diagnostic may allocate samples, but allocation learned on the current target can bias the result unless separated or symmetrized.

Test: log variance and cost of `Delta_l` versus level, then compare a fixed allocation with equal-cost baseline. Kill when increments do not decay, adaptive allocation overfits, or bookkeeping cost consumes the gain.

## Tau folding

Classical translation: the b-adic tent transform used for folded digital nets, not the circle constant and not a mystical recursion. In base two, apply the exact digit transform defined by the selected construction before mapping uniform points to the target distribution. Preserve random digital shifting/scrambling when required by the unbiasedness argument.

Theory targets smooth nonperiodic integrands in specific Sobolev spaces. ReLU compositions and inverse-normal transforms violate or strain those assumptions, so the transform is exploratory here.

Test: verify uniform marginals and deterministic point hashes; then matched-scramble comparison on held-out problem instances. Kill on bias evidence, tail artifacts near 0/1, or no equal-cost improvement.

## Memristive principles

Classical translation: a bounded state variable with fading memory and hysteresis,

`g_(t+1) = rho*g_t + (1-rho)*e_t`,

with separate enter/exit thresholds. `e_t` can be a pilot firing rate, residual energy, or confidence signal. This can stabilize pruning decisions across dyadic pilot blocks; it does not make a software estimator memristive hardware.

Test: measure false-prune and rescue rates across blocks and networks, with `rho` and thresholds frozen on development data. Kill if state only delays the same decision, adds target-dependent bias, or does not repay its compute.

## Biological patterning

Classical translations:

- local activation / long-range inhibition -> graph-Laplacian or difference-of-kernels contrast on correlated neurons;
- retinal center-surround coding -> subtract a known-expectation local predictor or control variate;
- opponent channels -> antithetic pairing;
- developmental overproduction and pruning -> generous candidate set followed by empirically pilot-rescued removal and mandatory rescue;
- homeostasis -> fixed feedback toward a target active fraction, trained away from holdout data;
- receptor mosaics -> space-filling or blue-noise directions with randomized marginals.

Define a neuron graph from weights or activation correlation without using hidden targets. For a signal `r`, a reaction-diffusion-inspired contrast is `c = r - lambda*L*r`, where `L` is a normalized graph Laplacian. Use `c` only for resource allocation or pruning when the resulting estimator's bias class is explicit.

Test each mechanism separately. Kill when graph construction costs too much, smoothing erases rare active gates, or the pattern is unstable across networks.

## Statistical and theoretical physics

Classical translations:

- renormalization -> coarse-grain dyadic sample/layer scales and study whether residual laws stabilize;
- response theory -> tangent/Jacobian control variates around a tractable reference state;
- fluctuation-dissipation intuition -> estimate sensitivity from matched perturbation/response covariance, without claiming equilibrium identities unless assumptions hold;
- spherical-radial decomposition -> analytically integrate nuisance radius for positively homogeneous networks;
- path/action language -> optimize an explicit variance-plus-cost functional, not an analogy;
- phase transitions -> track gate occupancy, covariance rank, and susceptibility to perturbations near ReLU kinks.

Always state the ensemble, conserved quantity or symmetry, order parameter, and limiting approximation. Dimensional analysis is mandatory when physical units exist; otherwise report normalized scales and computational complexity.

## Quantum and photopigment analogies

Biological phototransduction is quantum at photon absorption, while downstream image estimation is classical neural computation. Defensible translations are conditioning, opponent pairing, population coding, and measurement-noise models. Do not claim quantum speedup without a quantum algorithm, hardware, oracle model, and resource comparison.

## Composition rule

Given survivor errors `e_i`, compute their cross-instance covariance. Combine methods only if they reduce distinct components or an exact algebraic identity justifies the composition. For two binary mutations, run all four factorial cells and estimate the interaction:

`I = score(AB) - score(A) - score(B) + score(base)`.

A pair of individual wins is insufficient when their errors or compute savings overlap.
