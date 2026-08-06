# JSpace source audit for a bias-free ReLU workspace adapter

Date: 2026-08-06

Upstream: https://github.com/kameshkanna/jspace

Pinned repository state:

```text
commit: 54089367f887dde0b076d99bba71d053b67d70ac
author date: 2026-07-11T06:51:40+05:30
subject: feat: rich metadata in .pt files, add MIT LICENSE
package version: 0.1.0
license: MIT, copyright 2026 Kamesh Kanna
```

The source was cloned directly from GitHub into the cleanroom adapter directory
with a partial, no-checkout clone. Code was inspected with `git show` at the
pinned commit; the adapter below does not import or vendor upstream code.

## Upstream dependencies

`pyproject.toml` requires Python >=3.10 and:

```text
torch>=2.3.0
transformers>=4.43.0
accelerate>=0.31.0
numpy>=1.26.0
tqdm>=4.66.0
rich>=13.7.0
matplotlib>=3.9.0
seaborn>=0.13.2
huggingface-hub>=0.24.0
safetensors>=0.4.3
```

The local adaptation uses only NumPy and Python's standard library.

## What the upstream source actually implements

`src/jspace/jlens.py`:

- observes in-graph residual-stream activations at every requested transformer
  layer;
- defines an averaged signed Jacobian from an intermediate hidden state to the
  final residual stream;
- uses Rademacher output probes and fused reverse-mode VJPs;
- accumulates the matrix estimator `outer(v, J^T v)`, whose expectation is the
  signed Jacobian;
- projects corpus hidden states through the averaged Jacobian and stores
  normalized `J h` vectors.

Important weighting discrepancy: `_process_all_layers_fused` sets
`tgt_start=seq_len//2`, averages only final positions in the second half, then
averages gradients over every source position. Causality makes some invalid
source/target derivatives zero, but this is still not the literal uniform
`E_{t,t'>=t}` over all advertised position pairs. The fused all-layer VJP is
correct for the scalar actually constructed; the source does not establish
that its position weighting is "paper-exact."

`src/jspace/workspace.py`:

- implements nonnegative matching/gradient pursuit on those corpus vectors;
- chooses the highest positive residual dot product, clips coefficients at
  zero, and stops at 95% norm-squared coverage or 30 atoms;
- combines capacity with next-token accuracy, positional autocorrelation, and
  an entropy-valley signal in a majority-vote workspace detector.

The README claims an open replication of Lindsey et al. (2026), says the
implementation is paper-exact, and reports language-model workspace findings.
Those are upstream claims, not independently established by this audit. The
README references a results text file that is not present in the pinned Git
tree. No model checkpoints or result artifacts were executed here.

## Transferable mechanisms

1. A Rademacher VJP estimator can estimate the signed mean Jacobian without
   materializing a Jacobian for each state.
2. The same VJP `g=J^T v` gives the PSD second-moment workspace estimator
   `E[g g^T]=E[J^T J]`. This is distinct from `(E J)^T(E J)` and avoids signed
   cancellation.
3. Corpus pursuit is a falsifiable capacity diagnostic, but bias-free ReLU
   gradients are signed. The upstream nonnegative-coefficient restriction must
   be compared with a signed matching-pursuit control.

## Non-transferable mechanisms

- token unembedding, next-token accuracy, prompt position, language pivot,
  entropy valleys, and transformer phase voting have no analogue in the
  Gaussian-input bias-free MLP estimand;
- an averaged signed Jacobian is not automatically a sensitivity covariance;
- upstream defaults (16/32 probes, 95% coverage, cap 30) are empirical choices,
  not theorems or a WHest cost argument;
- `J h` has a special residual-stream interpretation upstream. For the ReLU
  cleanroom, the audited object is the input VJP workspace and is labeled as a
  new adaptation.

## Files inspected

```text
LICENSE
README.md
pyproject.toml
src/jspace/jlens.py
src/jspace/workspace.py
src/jspace/model.py
scripts/compute_jlens.py
scripts/run_workspace.py
src/jspace/__init__.py
```
