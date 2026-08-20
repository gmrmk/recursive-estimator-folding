# M120 primary-source boundary

These sources motivate the finite-width/resummation interpretation only.  They
do not prove the fixed-weight WHestBench estimator, its source ownership, or
its resource law.

- Sho Yaida, *Non-Gaussian processes and neural networks at finite widths*,
  MSML/PMLR 107 (2020):
  https://proceedings.mlr.press/v107/yaida20a.html
  Develops a perturbative finite-width non-Gaussian flow by progressively
  integrating layers.  Relevant to the hierarchy and renormalization analogy;
  it is an ensemble statement, not a certificate for the present fixed-weight
  adjoint.

- Kevin T. Grosvenor and Ro Jefferson, *The edge of chaos: quantum field
  theory and deep neural networks* (2021):
  https://arxiv.org/abs/2109.13247
  Organizes loop corrections in depth/width and explicitly sums infinite
  cactus and mushroom families.  It also notes that shared neuron indices in
  petal diagrams preserve their perturbative order.  This is the closest
  literature analogy to an exact diagonal-reset/repeated-index recurrence, but
  its field theory and network observable differ from WHestBench.

- Boris Hanin and Mihai Nica, *Finite Depth and Width Corrections to the Neural
  Tangent Kernel* (2019):
  https://arxiv.org/abs/1909.05989
  Gives rigorous depth/width scaling for finite ReLU networks.  It supports the
  campaign's refusal to treat `1/n` independently of depth; it does not provide
  the missing fixed-instance cumulant operator.

- Max Guillen, Philipp Misof, and Jan E. Gerken, *Finite-Width Neural Tangent
  Kernels from Feynman Diagrams* (2025):
  https://arxiv.org/abs/2508.11522
  Gives a modern diagrammatic finite-width recursion and a ReLU diagonal
  cancellation result for a different NTK statistic.  Its diagonal result must
  not be transplanted to the Price covariance adjoint without a derivation.

## Inference used here

The literature makes a repeated-index resummation scientifically plausible.
The exact M120 identity is instead elementary and self-contained:

`K = p p^T + diag(p-p^2) + E`.

Only a complete fixed-weight derivation, strict generated-only falsifier, and
installed-cost audit can promote the resulting shared-CP recurrence.
