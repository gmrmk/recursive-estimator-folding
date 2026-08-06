# ECN-style constrained projection, Jacobian routing, and MaxEnt priors

Date: 2026-08-06

Question: can the known weights of the WHestBench ReLU network be used to
reverse-engineer influence paths in Jacobian space, then route a compressed
estimator with flatworm-like attenuation and maximum-entropy priors?

## Source separation

Three distinct literatures are relevant and must not be conflated.

### 1. Elliptic Cortical Networks (ECN)

Jiao (2025) proposes a six-layer architecture whose state variables are points
on elliptic curves over finite fields. Its transferable computational pattern
is an inter-curve projection

```text
Pi(P) = phi_target( tau( psi_source(P) ) ).
```

`psi` extracts real-valued features from a valid source point, `tau` performs a
conventional neural transformation, and `phi` maps the result onto a valid
target-curve point. The paper reports curve-constraint satisfaction, XOR, and a
small predictive-learning experiment.

Important limits for this project:

- The ECN paper does not propose Jacobian-space routing or maximum-entropy
  optimization.
- A state satisfying a finite-field curve equation is mathematically valid but
  is not thereby semantically true. The paper's phrase "hallucination
  prevention" should not be imported as a correctness guarantee.
- Literal finite-field elliptic arithmetic is a poor fit for continuous
  Gaussian moments: modular wrapping and quantization can destroy radial,
  covariance, and rotation identities and would add unsupported billed work.
- We therefore borrow only `extract -> transform -> constraint-preserving
  remap`, then test it in the actual estimator geometry.

Primary source: Dian Jiao, **Elliptic cortical networks: A mathematically
constrained architecture for biologically-inspired intelligence**,
*Neurocomputing* 658 (2025), 131802.
https://doi.org/10.1016/j.neucom.2025.131802

Open full text:
https://www.sciencedirect.com/science/article/pii/S0925231225024749

### 2. Cortical neurogeometry and hypoelliptic diffusion

The Citti--Petitot--Sarti line models V1 by lifting image locations into an
orientation bundle and diffusing along a constrained sub-Riemannian geometry.
This is a different use of "elliptic": the governing operator is
hypoelliptic, not an elliptic curve. Its useful lesson is that transport should
follow a feature geometry rather than Euclidean proximity alone.

Primary source: Boscain et al., **Anthropomorphic image reconstruction via
hypoelliptic diffusion** (2010), arXiv:1006.3735.
https://arxiv.org/abs/1006.3735

### 3. Maximum entropy network models

Maximum-entropy models choose the least-committal distribution satisfying
specified expectation constraints. Exponential random graph models use
`P(G) proportional to exp(theta . x(G))`; their parameters and graph
statistics must be specified carefully, and degenerate models are a known
risk. This motivates a KL-regularized routing posterior but does not prove that
such a posterior improves an estimator.

Review: **Statistical models of complex brain networks: a maximum entropy
approach**, arXiv:2209.05829.
https://arxiv.org/abs/2209.05829

Related functional-connectivity study:
https://www.nature.com/articles/s41598-022-13674-4

## What is exactly available from the WHest weights

For a fixed input/gate pattern, a bias-free ReLU network has pointwise input
Jacobian

```text
J_x = W_L D_(L-1) W_(L-1) ... D_1 W_1,
D_l = diag(1[z_l > 0]).
```

This factorization exposes active paths exactly. However, the prior campaign
already measured that the leading pointwise subspace tumbles with the input:
the local Jacobian has low effective rank but its averaged sensitivity is
nearly isotropic. Consequently, a single global input active subspace is not a
valid descendant.

The usable alternative is an **observable Jacobian** of a one-layer or
downstream moment map. Let the state be `s_l=(mu_l,C_l)` and the target
observable be `o`. For a perturbation `delta s_l`, use analytic Jacobian-vector
and vector-Jacobian actions rather than materializing the enormous matrix:

```text
delta o = J_(l->o) delta s_l,
G_l = J_(l->o)^T Q J_(l->o).
```

`G_l` is a pullback metric: two mixture components are close only when their
difference has similar effect on the target observable. Low-rank Lanczos or a
fixed bank of response probes can approximate its action in `O(r L n^2)` or
`O(r L n^3)` depending on whether the state action is vector or covariance
valued. Full Jacobians, per-particle backward passes, and output-specific dense
covariance adjoints are rejected by the existing cost evidence.

## Proposed constrained compressor

Apply ECN's three-stage pattern to the randomized Haar-plus-two-radius mixture.

### psi: invariant response extraction

For source component `c` at layer `l`, form a small feature vector from the
already-derived response channels:

```text
h_lc = [gate-boundary response, active-pair covariance response].
```

Normalize using weighted source moments and the observable pullback metric.
Features must be invariant to neuron permutation, covariance-factor gauge, and
the deterministic Haar construction; no reference error or truth enters.

### tau: MaxEnt/entropic transport into q=3 bins

For three target prototypes `z_k`, solve a fixed regularized transport problem

```text
T* = argmin_(T>=0) <T,C_G> + eps KL(T || w outer a)
subject to T 1 = w,  T^T 1 = a,
C_G(c,k) = ||h_lc-z_k||^2_(G_l).
```

The base prior is the maximum-entropy distribution allowed by the frozen mass
and capacity constraints. Any biological role prior changes support or graph
coupling only; it must not inject truth-fitted numerical preferences. Use a
fixed iteration count and dimensionless standardization before freezing
`eps`.

### phi: exact remap to the feasible estimator manifold

Each transport column aggregates source component raw moments. Reconstruct its
mean and covariance with the law of total covariance, then retain the three
weighted Gaussian components. Globally,

```text
sum_k a_k mu_k                 = source mean,
sum_k a_k (C_k+mu_k mu_k^T)   = source raw second moment.
```

Thus `phi` preserves total mass, mean, covariance, and PSD by construction.
This is the estimator analogue of ECN's target-valid remap and is far more
relevant than a finite-field curve.

## Flatworm tandem operator

Retain gate and active response as two semantic lanes. Across depth,

```text
m_l = .5 m_(l-1) + .5 u_l,
mtilde_l = [[.75,.25],[.25,.75]] m_l.
```

The ladder state regularizes the MaxEnt transport metric, not the estimator
output. Because the channels were observed to become nearly orthogonal late in
depth, the implementation must keep the two-dimensional embedding; it may use
commissural consensus as a control signal but may not collapse the lanes to one
scalar. The flatworm source note documents the biological boundary:
`sources/research_flatworm_ladder_attenuation_20260806.md`.

## Aggressive falsification plan

Four frozen ablations:

1. generic q3 compressor;
2. scalar dual-observable q3 (the diagnosed failed link);
3. Jacobian-MaxEnt project/route/remap;
4. Jacobian-MaxEnt plus flatworm depth ladder.

Promotion premise: observable RMS ratio at most 0.80 against generic, at least
75% matched wins, exact mass/mean/covariance/PSD, permutation and gauge tests,
no route collapse, conservative target arithmetic below 80B, and no
truth-fitted coefficient or depth threshold. An independent judge must audit:

- whether the Jacobian target leaks the reference;
- whether MaxEnt is doing more than soft k-means with a decorative name;
- whether `phi` really preserves raw second moments;
- whether the pullback metric is computable inside FlopScope;
- whether the claimed gain survives fresh states and width scaling;
- whether the flatworm recurrence improves a causal link rather than merely
  smoothing reported metrics.

Failure must be localized to `psi`, `tau`, `phi`, the ladder, or the resource
model. Passing operators remain reusable even if the complete child misses its
effect-size gate.
