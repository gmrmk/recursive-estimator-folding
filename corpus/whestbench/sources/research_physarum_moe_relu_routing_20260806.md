# Research excursion: Physarum routing, mixture-of-experts, and ReLU cubature

Date: 2026-08-06

Search scope: arXiv, primary journal/conference pages, PubMed, and a direct
Google Scholar domain query. The Scholar query returned noisy author-profile
matches rather than a reliable paper set, so claims below are grounded in the
primary papers themselves. This note motivates a falsifiable estimator
operator; it does not claim competition performance.

## Primary sources

1. A. Tero et al., *Rules for biologically inspired adaptive network design*,
   Science 327 (2010), 439--442. DOI:
   https://doi.org/10.1126/science.1177894 ; PubMed:
   https://pubmed.ncbi.nlm.nih.gov/20093467/

   Physarum adapts transport-tube conductance through local flow feedback,
   producing networks that trade transport efficiency, cost, and robustness.

2. V. Bonifaci, K. Mehlhorn, G. Varma, *Physarum Can Compute Shortest Paths*,
   https://arxiv.org/abs/1106.0423

   For the standard dynamics, conductance mass converges to a shortest path
   independently of initial mass. This makes the biological metaphor an actual
   graph algorithm rather than a visual analogy.

3. D. Straszak, N. K. Vishnoi, *On a Natural Dynamics for Linear Programming*,
   https://arxiv.org/abs/1511.07020

   Physarum dynamics are interpreted as steepest descent on a Riemannian
   manifold and as a path of entropy-barrier-regularized convex optimizers.
   This supplies a principled attenuation term and a route to min-cost flow.

4. D. Straszak, N. K. Vishnoi, *Natural Algorithms for Flow Problems*, SODA
   2016. DOI: https://doi.org/10.1137/1.9781611974331.ch131

   Discrete Physarum dynamics extend beyond shortest paths to directed and
   undirected uncapacitated min-cost flow.

5. N. Shazeer et al., *Outrageously Large Neural Networks: The Sparsely-Gated
   Mixture-of-Experts Layer*, https://arxiv.org/abs/1701.06538

   A learned sparse gate activates a small expert subset, illustrating
   conditional computation but also requiring load-balancing controls.

6. W. Fedus, B. Zoph, N. Shazeer, *Switch Transformers*,
   https://arxiv.org/abs/2101.03961

   Top-one routing keeps activated compute roughly constant, but routing
   stability and balancing remain central engineering constraints.

7. A. Vaswani et al., *Attention Is All You Need*,
   https://arxiv.org/abs/1706.03762

   Scaled dot-product attention supplies the query/key compatibility form. A
   full trained transformer is not justified here; the useful translation is a
   small invariant attention score combined with Physarum conductance dynamics.

## Concrete WHestBench translation

The safe translation is a **Physarum-routed cubature expert graph**, not a
biological simulation and not a language transformer.

### Graph

- Demand nodes: layer/output-group ReLU boundary observables, represented only
  by permutation/gauge-invariant quantities such as `alpha=mu/sigma`, boundary
  mass `phi(alpha)`, covariance participation, and downstream weight norms.
- Expert nodes: complete moment-safe rules, e.g. Haar+chi2 radial cubature,
  analytic full covariance, residual-cumulant correction, and a direct random
  probe family. An expert is a whole rule, not an individual point, so its
  internal mean/covariance identities remain intact.
- Edge length `ell_de`: conservative charged arithmetic plus a budget-tail
  barrier and a structural mismatch penalty.
- Edge conductance `D_de`: nonnegative compute allocation.

Given deterministic demand `b`, solve the electrical-flow subproblem

```text
q_de = (D_de / ell_de) (p_d - p_e),
B q = b,
```

then update conductance by a damped Physarum rule

```text
D_de <- (1-eta) D_de + eta |q_de|^gamma.
```

Use entropy-barrier attenuation, equivalently a tiny transformer-style
compatibility prior,

```text
s_de = <query(d), key(e)> / sqrt(h),
D_de(0) proportional to exp(s_de / tau).
```

No learned transformer weights are needed in the first premise. Queries and
keys are fixed invariant feature maps; Physarum flow enforces cost/load
constraints. Top-k pruning happens only after the flow converges and must keep
whole moment-safe experts.

## Critical constraints from the existing campaign

1. The mediant law means mixing two independent estimators cannot beat the
   more efficient pure family unless efficiency genuinely varies by instance
   and the router predicts that variation.
2. Fresh-rotation selection from noisy estimates is a coin flip under the
   existing symmetry proof. The router may not best-pick Haar seeds.
3. H1/H2 show that current weight-only features do not predict arbitrary
   residual or sampler-noise signs. The first premise must route using a
   target-free one-step oracle or deterministic structural loss, never public
   truth.
4. A trained transformer is likely too costly and too easy to overfit. Start
   with parameter-free query/key maps and at most top-1/top-2 routing.
5. Every routed expert must retain exact normalization/moment constraints and
   the final rule must be costed under actual charged shapes, not abstract FLOPs.

## Exploratory series

### P0: target-free routing premise

On frozen synthetic intermediate states, compare each expert against an
uncompressed one-step reference. Physarum/top-k routing must reduce aggregate
one-step mean+covariance error by at least 20% relative to always using the
Haar+chi2 expert, win at least 75% of states, and never exceed the same static
cost. This establishes predictable specialization without truth.

### P1: attenuation ablation

Freeze experts and compare: uniform allocation, softmax attention only,
Physarum conductance only, and attention-initialized Physarum. Report route
entropy, load, cost, and error. No fitted temperature/gamma; use a predeclared
small grid only as a premise family, with a held-out synthetic graph.

### P2: estimator interaction

Only after P0/P1 pass, test routed experts end to end against the frozen
Haar+chi2 parent. Report covariance between expert errors. If errors are merely
independent and one expert is uniformly worse, the mediant theorem kills the
mixture. Promotion needs complementary, weight-predictable regimes.

### P3: production boundary

Require exact symmetry, zero failures, conservative target cost below 80B for
the analytic branch (or explicit score headroom for a sampler branch), bounded
router call/allocation count, and no use of private/public truth for routing.

## Verdict before experiments

The idea is mathematically viable as a **routing and compression mechanism**.
It is not yet evidence for a better estimator. Its best near-term use is to
route among complete non-Gaussian cubature/compression experts on a one-step
synthetic oracle, not to train a large transformer or mutate individual node
weights without moment repair.
