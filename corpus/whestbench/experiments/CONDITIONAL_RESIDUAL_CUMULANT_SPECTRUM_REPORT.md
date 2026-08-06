# Conditional residual cumulant spectrum

## Outcome

The signed residual-spectrum representation survives every frozen
representation gate. It is not yet a deployable estimator.

Rank-4 conditional residual factors, combined with the previous
rank-4-plus-diagonal conditional covariance, achieve:

| metric | result |
|---|---:|
| standardized k3 fidelity | 0.993974 |
| standardized k4 fidelity | 0.984388 |
| combined standardized fidelity | 0.986618 |
| combined Edgeworth-correction fidelity | 0.995497 |
| material correction signs | 97/97 |
| conditional k3 next-row fidelity | 0.978860 |
| conditional k4 next-row fidelity | 0.893926 |

The frozen thresholds were 0.80 for k3, k4, combined fidelity, and material
signs. Symmetry, coordinate invariance, bank reproduction, and doubled-sample
convergence also pass.

Classification:

- promote the representation and contraction operators;
- retain exact total-cumulance and covariance components;
- withhold deployment because factor formation at n=256 and a multi-layer ReLU
  recurrence remain unresolved.

No WHest network, scorer, holdout, API, or rank tuning was used.

## Construction

The experiment preserves the nine prior cases, input samples, 16
principal-score quantile cells, next-layer weights, exact targets, material
definition, and convergence audit. The only changed link is the prior
Gaussian-within-cell assumption `conditional k3=k4=0`.

For symmetric `A`, use the Frobenius-isometric vectorization

```text
svec(A)_ii = A_ii
svec(A)_ij = sqrt(2) A_ij, i<j,
```

so `svec(A).svec(ww^T)=w^T A w`.

For each cell, conditional k3 is represented by its mode-1/symmetric-pair
unfolding `K3 in R^(n x p)`, `p=n(n+1)/2`. Its SVD gives directional terms

```text
sigma_s (u_s.w) (v_s.svec(ww^T))
= (u_s.w) (w^T V_s w).
```

Conditional k4 becomes the symmetric pair unfolding `K4 in R^(p x p)`. Its
signed eigenspectrum gives

```text
sum_s sign(lambda_s) (w^T A_s w)^2,
A_s = sqrt(abs(lambda_s)) unsvec(a_s).
```

These are not repeated-index approximations. Every tensor index pattern,
including all-distinct cancellations, is retained by the unfoldings and their
signed factors. Exact full-spectrum contraction plus the law of total
cumulance reproduces direct targets to `4.03e-13` maximum absolute error; the
prior exact binned identity remains within `4.25e-13`.

## Spectral ladder

Rank 4 was frozen as the decision gate. Ranks 1, 2, and 8 are diagnostics:

| rank | k3 tensor energy | k4 tensor energy | conditional row k3/k4 | total k3/k4 | combined | signs |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.6575 | 0.6413 | 0.6151 / 0.5299 | 0.9197 / 0.9226 | 0.9220 | 96/97 |
| 2 | 0.8148 | 0.8032 | 0.8780 / 0.7435 | 0.9701 / 0.9545 | 0.9582 | 97/97 |
| 4 | 0.9456 | 0.8974 | 0.9789 / 0.8939 | 0.9940 / 0.9844 | 0.9866 | 97/97 |
| 8 | 0.9927 | 0.9601 | 0.9972 / 0.9821 | 0.9983 / 0.9951 | 0.9959 | 97/97 |

Two conclusions are unusually clear:

1. Rank is not the next bottleneck. Rank 1 already passes the total-cumulant
   gate, and rank 4 leaves little representational error.
2. Total-cumulance structure amplifies the usefulness of the leading modes.
   Rank 1 captures only about 64% of raw tensor energy yet captures more than
   92% of final standardized total-cumulant energy. Conditional mean and
   covariance terms carry the complementary structure.

Using exact conditional covariance instead of the stored rank-4-plus-diagonal
covariance changes rank-4 totals only from `0.9940/0.9844/0.9866` to
`0.9953/0.9877/0.9895`. Covariance compression remains a solved ingredient.

### Per-case rank-4 total fidelity

| n | L | k3 | k4 |
|---:|---:|---:|---:|
| 8 | 2 | 0.9853 | 0.9446 |
| 8 | 3 | 0.9975 | 0.9567 |
| 8 | 4 | 1.0000 | 1.0000 |
| 12 | 2 | 0.9935 | 0.9884 |
| 12 | 3 | 0.9987 | 0.9959 |
| 12 | 4 | 0.9999 | 0.9992 |
| 16 | 2 | 0.9657 | 0.9424 |
| 16 | 3 | 0.9923 | 0.9878 |
| 16 | 4 | 0.9986 | 0.9978 |

Every case is comfortably above the frozen gate.

## Downstream transport

The next-layer preactivation cumulants were transported through the first-order
Edgeworth ReLU correction and compared with the directly sampled ReLU mean.
The rank-4 predicted correction has fidelity `0.941765` to the actual
Gaussian-closure residual and reduces aggregate downstream MSE to `0.058235`
times the Gaussian baseline. Exact empirical k3/k4 reach correction fidelity
`0.947365` and MSE ratio `0.052635`, so rank 4 retains nearly all benefit
available to this correction order.

This is an oracle representation diagnostic on the same synthetic sample, not
an independent estimator-validation result. The doubled-sample audit is the
available stability check; factor cross-fitting remains appropriate before
any claim beyond representation.

## Convergence and structural checks

On the three doubled-sample depth-4 cases, rank 4 gives:

| metric | doubled result |
|---|---:|
| standardized k3 fidelity | 0.999376 |
| standardized k4 fidelity | 0.998699 |
| combined fidelity | 0.998851 |
| correction fidelity | 0.999846 |
| material signs | 30/30 |
| conditional k3/k4 row fidelity | 0.995295 / 0.985043 |

The exact tensor permutation errors are `1.75e-16` for k3 and `2.77e-16` for
k4. Rebuilding all rank-4 factors after a coordinate permutation changes total
contractions by scaled maximum `1.23e-15`. Signed eigenspectrum conventions,
PCA sign, and coordinate ordering therefore do not explain the result.

The small-n oracle reproduces the previous bank within `1.27e-13` standardized
k3, `3.20e-12` standardized k4, and `7.04e-15` correction error.

## n=256 boundary

For `n=256`, symmetric-pair dimension is 32,896. With `B=16,r=4`, residual
factors contain 4,227,136 float64 values. Including conditional
mean/rank-4-plus-diagonal covariance state gives:

```text
4,251,728 float64 values = 34,013,824 bytes.
```

All-output terminal contraction is

```text
2 B r (2 n^3 - n^2) + 3 B r (2 n^2 - n)
= 4,311,695,360 billed-like arithmetic terms.
```

Thus retained factors satisfy the declared `O(B r n^2)` state and
`O(B r n^3)` terminal arithmetic envelope.

Factor formation does not. The exact small-n screen explicitly builds the k4
pair matrix and diagonalizes it. At n=256 that matrix has 1,082,146,816
entries:

```text
8.063 GiB per conditional cell
129.002 GiB across 16 cells,
```

before an infeasible dense `O(p^3)` eigendecomposition. The worst small-n
resource case measured only 140.43 MiB peak working set because `p=136`, but
that does not extrapolate.

No n=256 factor-discovery method and no ReLU recurrence for the signed factors
has been derived. Therefore deployment remains false despite the strong
terminal representation.

## Next rung

The next mutation should target formation, not rank:

- derive a matrix-free k4 cumulant-operator product and use fixed-iteration
  signed Lanczos/randomized subspace iteration without materializing `p x p`;
- or derive the leading one-to-four modes directly as conditional response
  vectors/Hermite-Price factors from the layer state;
- cross-fit small-n factors to distinguish stable modes from empirical tensor
  noise;
- only then attempt and falsify a ReLU factor update.

Rank 1 passing is actionable headroom: an analytic leading-mode recurrence may
be enough even if rank 4 is the robust representation target. A sample-driven
matrix-free oracle alone would not solve the competition; the weights-only
formation and recurrence links remain mandatory.

Artifacts: `PREDECLARED_GATE.md`, `conditional_spectrum.py`, `run_oracle.py`,
`oracle_results.json`, `convergence_audit.json`, `resource_audit.json`,
`structural_audit.json`, `decision.json`, and tests in this directory.
