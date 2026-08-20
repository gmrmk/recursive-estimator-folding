# M120 exploratory generated-only findings

Status: mechanism evidence only.  These observations preceded the independent
complete-theory audit and are not a frozen promotion experiment.

## Exact algebra being probed

For a Gaussian preactivation vector `Z`, let

`p_i = P(Z_i > 0)` and `K_ij = P(Z_i > 0, Z_j > 0)`.

Then

`K = p p^T + diag(p-p^2) + E`

exactly, with `diag(E)=0`.  The first term is the independent-gate/separable
piece; the second is the Bernoulli self-collision variance; `E` is the
connected cross-gate covariance.  M119's `R=I` counterexample is represented
exactly by the first two pieces, rather than spectrally truncated.

For a joint all-output symmetric CP adjoint

`A_ijo = sum_s U_is U_js G_os`,

the `p p^T` Schur action scales rows of `U` and preserves rank.  If
`D_io=(p_i-p_i^2) A_iio`, then an affine pull through weight `W` maps the
diagonal reset to

`sum_i W_ai W_bi D_io`,

which is exactly `n` shared CP atoms.  With `E=0`, rank therefore grows by at
most `n` per hidden layer, not by a kernel-rank product.

## Exploratory measurements

Fresh generated He networks only; no contest/public/private weights, truths,
scorer, or champion artifact were read.

1. `probe_price_split.py`, width 256, depth 32, seeds 120001 and 120002:

   - 62 hidden-layer records;
   - mean `||E||_F/||K||_F = 0.019570031557779807`;
   - 90th percentile `0.025498001949127387`, maximum
     `0.03960089728411157`;
   - on terminal rank-one weight adjoints, mean omitted/exact Schur-action
     ratio `0.019436686819615526`, 90th percentile layer aggregate
     `0.02537218200247636`, maximum `0.03897091578231573`.

2. `probe_repeated_pullback.py`, width 256, depth 32, seed 120101, output 0,
   connected rank 0:

   - exact dense `K` pullback versus exact dense separable-plus-diagonal
     pullback through every hidden layer;
   - terminal-to-first-ReLU relative Frobenius error
     `0.03143572710945089`;
   - cosine `0.9995927343984596`.

A width-32/depth-8 sanity probe showed that naively retaining the largest
absolute eigenmodes of indefinite `E` can be worse than omitting `E`: ranks 4
and 8 had mean relative errors `0.53867` and `0.34592`, versus `0.10232` for
rank 0.  This is an early warning against reviving M119 by ordinary spectral
truncation.

## What remains unproved

- the complete coupled mean/covariance Gaussian-closure reverse Jacobian;
- a nonduplicated local non-Gaussian source contraction;
- whether diagonal-reset atoms coincide with the dominant fixed-instance
  repeated-index diagrams rather than only an ensemble analogy;
- signed contraction error after all nonnormal pulls for all outputs;
- complete FlopScope cost, memory, conditioning, and residual wall time; and
- a predeclared one-shot generated-only efficacy falsifier.

No estimator, correction oracle, manifest, package, upload, or submission is
authorized by these exploratory results.
