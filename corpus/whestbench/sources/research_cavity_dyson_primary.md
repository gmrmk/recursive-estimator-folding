# Primary-source ledger: cavity, Dyson, and TAP closures

Date: 2026-08-06

## Scope and method

Question: can a leave-one-neuron, Dyson, or TAP-style self-consistency turn the
fixed-weight Gaussian-input ReLU mean problem into an `O(L n^3)` recurrence that
resums errors beyond a finite `k2`/`k3` cumulant truncation?

The preferred `parallel-cli` research path was unavailable in this workspace.
The fallback was direct retrieval of primary papers and their official/arXiv
records. No benchmark target, public truth, scorer response, or forward-pass
experiment was used in this branch.

## Primary papers

### Finite-width diagrammatics

1. Sho Yaida, **Non-Gaussian Processes and Neural Networks at Finite Widths**,
   PMLR 107 (2020).
   [PMLR record](https://proceedings.mlr.press/v107/yaida20a.html),
   [paper](https://proceedings.mlr.press/v107/yaida20a/yaida20a.pdf).

   - Observable: correlations of preactivations after averaging over an ensemble
     of independent, zero-mean Gaussian weights and biases.
   - Leading finite-width state: the infinite-width kernel plus a two-point
     self-energy and a connected four-point vertex. The recursion for the
     self-energy is not closed without the four-point vertex.
   - The paper's vanishing odd moments and neuron-index delta structures come
     from weight averaging. They are not identities for a realized network with
     expectation taken only over its Gaussian input.

2. Ethan Dyer and Guy Gur-Ari, **Asymptotics of Wide Networks from Feynman
   Diagrams**, ICLR 2020, arXiv:1909.11304.
   [arXiv record](https://arxiv.org/abs/1909.11304),
   [paper](https://arxiv.org/pdf/1909.11304).

   - Develops Feynman-diagram power counting for correlation functions of wide
     random networks and training dynamics.
   - Its contractions are Gaussian integrals over random parameters. This is
     useful for identifying which vertices occur, but it does not itself supply
     a quenched estimator for `E_X[f_W(X) | W]`.

3. Max Guillen, Philipp Misof, and Jan E. Gerken, **Finite-Width Neural Tangent
   Kernels from Feynman Diagrams**, arXiv:2508.11522 (2025).
   [arXiv record](https://arxiv.org/abs/2508.11522),
   [paper](https://arxiv.org/pdf/2508.11522).

   - Gives layerwise order-`1/n` corrections and all-order diagram rules for
     finite-width NTK statistics.
   - Even at rank four, the closed description uses several vertex tensors, not
     a covariance-only Dyson scalar. Numerical checks average over many network
     initializations.
   - The reported ReLU cancellations concern ensemble NTK observables and do not
     transfer to the fixed-network Gaussian-input mean.

4. Boris Hanin and Mihai Nica, **Finite Depth and Width Corrections to the
   Neural Tangent Kernel**, arXiv:1909.05989.
   [arXiv record](https://arxiv.org/abs/1909.05989),
   [paper](https://arxiv.org/pdf/1909.05989).

   - Quantifies finite-depth/finite-width mean and variance for random ReLU NTKs.
   - Again, the random-weight NTK is an annealed parameter-ensemble observable,
     not a conditional input integral for one weight realization.

### TAP / Onsager mechanisms

5. Peter J. Shamir and Haim Sompolinsky, **TAP equations for neural networks**,
   Physical Review E 61, 1839 (2000), DOI 10.1103/PhysRevE.61.1839.
   [PubMed record](https://pubmed.ncbi.nlm.nih.gov/11046469/),
   [DOI](https://doi.org/10.1103/PhysRevE.61.1839).

   - TAP corrections are developed for recurrent/Hopfield-type networks, where
     a unit's field feeds back through the network and creates a self-reaction.
   - A strictly feed-forward layer has no such same-edge feedback.

6. Alyson K. Fletcher and Sundeep Rangan, **Inference in Deep Networks in High
   Dimensions**, arXiv:1706.06549.
   [arXiv record](https://arxiv.org/abs/1706.06549),
   [paper](https://arxiv.org/pdf/1706.06549).

   - ML-VAMP/expectation-propagation uses Onsager-style corrections for iterative
     inverse inference under high-dimensional random-matrix assumptions.
   - It is not a one-pass evaluation of a deterministic feed-forward network;
     the algorithmic iteration and matrix reuse are essential to its reaction
     terms.

### Comparator: finite cumulant propagation

7. W. Wu et al., **Estimating the expected output of wide random MLPs more
   efficiently than sampling**, arXiv:2605.05179 (2026).
   [arXiv record](https://arxiv.org/abs/2605.05179),
   [paper](https://arxiv.org/pdf/2605.05179),
   [official code](https://github.com/alignment-research-center/mlp_cumulant_propagation).

   - Supplies the finite-order cumulant/Hermite comparator and the proposed
     `(L/n)^K` depth scaling.
   - The depth law is a conjecture/heuristic outside the paper's rigorous
     fixed-depth polynomial-activation regime. Therefore the report below does
     not use it as a lower bound.

## Translation rule used in the audit

An ensemble identity was admitted into the fixed-instance analysis only if its
conditioning was made explicit. In particular,

`E_W E_X[f_W(X)]` and correlation functions averaged over `W`

are not substitutes for

`E_X[f_W(X) | W = W_realized]`.

Weight averaging can erase odd cumulants and collapse neuron-index tensors by
exchangeability. Those simplifications are unavailable after conditioning on a
generic dense `W_realized`.
