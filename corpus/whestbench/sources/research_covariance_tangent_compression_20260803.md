# Source log: compressing a signed covariance tangent

Accessed 2026-08-03. This log preserves the public primary sources used for
`work/swarm/covariance_tangent_compression.md`. No competitor-private source or
code was consulted.

## Problem-specific sources

- Hilton, Wu, Robinson, Winer, Lecomte, and Christiano (2026), *Estimating the
  expected output of wide random MLPs more efficiently than sampling*:
  https://arxiv.org/abs/2605.05179
- ARC public explanation and public reference implementation:
  https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/
  and https://github.com/alignment-research-center/mlp_cumulant_propagation
- Cho and Saul (2009), *Kernel Methods for Deep Learning*. The degree-one
  arc-cosine kernel gives the centered bivariate-Gaussian ReLU raw moment used
  by the full-covariance tangent:
  https://proceedings.neurips.cc/paper/2009/file/5751ec3e9a4feab575962e78e006250d-Paper.pdf

## Randomized low-rank approximation and sketches

- Halko, Martinsson, and Tropp (2011), *Finding Structure with Randomness*:
  https://arxiv.org/abs/0909.4061
- Tropp, Yurtsever, Udell, and Cevher (2017), *Practical Sketching Algorithms
  for Low-Rank Matrix Approximation*: https://arxiv.org/abs/1609.00048
- Meyer, Musco, Musco, and Woodruff (2021), *Hutch++: Optimal Stochastic Trace
  Estimation*: https://arxiv.org/abs/2010.09649
- Dharangutte and Musco (2023), *A Tight Analysis of Hutchinson's Diagonal
  Estimator*: https://arxiv.org/abs/2208.03268 and
  https://doi.org/10.1137/1.9781611977585.ch32

The Hutch++ relative-error theorem is for traces of positive-semidefinite
matrices. The tangent discrepancy in this project is signed/indefinite, so that
theorem is not transferred to the proposed approximation. The diagonal result
does apply to a general square matrix and bounds error by the off-diagonal
Frobenius norm, but it estimates only `diag(A)` and does not close the tangent's
covariance recursion.

## Response-informed subspaces and control variates

- Constantine and Gleich (2015), *Computing Active Subspaces with Monte
  Carlo*: https://arxiv.org/abs/1408.0545
- Liu and Owen (2023), *Pre-integration via Active Subspaces*:
  https://arxiv.org/abs/2202.02682
- Oates, Girolami, and Chopin (2017), *Control Functionals for Monte Carlo
  Integration*: https://arxiv.org/abs/1410.2392
- Oates and Girolami (2016), *Control Functionals for Quasi-Monte Carlo
  Integration*: https://proceedings.mlr.press/v51/oates16.html

These sources support gradient-informed dimension reduction and Stein-derived
zero-mean controls in their stated settings. They do not establish that a
downstream-response sketch preserves this particular depth-32 signed tangent;
that is a new, explicitly falsifiable proposal.

## Structured orthogonal designs

- Lin, Chen, Zhang, Laroche, and Choromanski (2020), *Demystifying Orthogonal
  Monte Carlo and Beyond*: https://arxiv.org/abs/2005.13590 and
  https://proceedings.neurips.cc/paper/2020/hash/5bce843dd76db8c939d5323dd3e54ec9-Abstract.html

Orthogonal Monte Carlo supplies negative-dependence/concentration motivation.
It is not a theorem that partial Hadamard probes improve an arbitrary fixed,
signed covariance sketch, so Gaussian, Rademacher, and randomized-Hadamard
probes must be compared at identical billed shapes.

## Local primary evidence and accounting formulas

- `work/scorefloor_generation/covariance_control/RESULTS.md`: the current
  full-covariance tangent's 20-network premise, exact state definition, and
  official cost delta.
- `work/scorefloor_generation/covariance_control/estimator.py`: exact
  recurrence and counted operations.
- FlopScope 0.10 local source:
  `work/whest-v014/Lib/site-packages/flopscope/_flops.py` and
  `work/whest-v014/Lib/site-packages/flopscope/numpy/linalg/_decompositions.py`.
  Relevant leading bills are `(m,k)@(k,n): m*n*(2k-1)`, thin rank-`r` SVD
  bounded by `4*m*n*r`, reduced QR
  `2*(2*m*n*k - 2*k^3/3)`, and symmetric eigendecomposition `9*n^3`.
  Repeated-operand `X.T@X` receives the validated symmetric-output bill
  `1,842,143,104` at shape `X=(28000,256)`, rather than the dense
  `3,669,950,464`; a symmetric `W.T@C@W` costs `50,298,752` before the
  float64 dtype rate of 2.0. These values were checked directly against the
  official local cost engine.

[03:00:00] SAVED: Nine public primary research sources, three public
problem-specific artifacts, and the official local FlopScope cost formulas.
