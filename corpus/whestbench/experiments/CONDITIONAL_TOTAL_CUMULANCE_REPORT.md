# Conditional total-cumulance mutation

## Verdict

Kill only the frozen `B=16`, rank-4-plus-diagonal, Gaussian-within-cell
implementation. Promote two ingredients, not the estimator:

- the exact scalar law-of-total-cumulance contraction, which retains
  all-distinct index effects implicitly;
- the rank-4-plus-diagonal conditional covariance contraction, which is an
  excellent approximation to the corresponding full-covariance closure.

The representation fails because the residual distribution inside a scalar
cell is still non-Gaussian. Full conditional covariance does not repair it.
The missing terms are conditional residual k3/k4, not omitted covariance rank.
No WHest network, scorer, holdout, or API was used.

## Frozen construction

The screen recreated the untouched nine-case bank: `n in {8,12,16}` and
`L in {2,3,4}`, 32,768 Philox base inputs plus their negatives, with the
previous network/input/next-weight seeds. Exact directional targets reproduce
the bank to maximum absolute errors:

| target | maximum error |
|---|---:|
| standardized k3 | 1.2734e-13 |
| standardized k4 | 3.2048e-12 |
| combined Edgeworth correction | 7.0430e-15 |

The conditioning variable is the leading principal score. Its basis is 16
equal-mass quantile cells. Each cell stores probability, mean vector,
covariance diagonal residual, and four leading covariance factors in descending
eigenvalue order. There was no basis/rank/threshold tuning after metrics.

For a directional projection `Y=w.X`, let `delta=E[Y|T]-E[Y]`,
`v=Var(Y|T)`, and `c3,c4` be conditional cumulants. The implemented identities
are

```text
k3 = E[c3] + E[delta^3] + 3 E[delta v]

k4 = E[c4] + E[delta^4] - 3 E[delta^2]^2
     + 4 E[delta c3]
     + 6 (E[delta^2 v] - E[delta^2] E[v])
     + 3 (E[v^2] - E[v]^2).
```

This is the scalar specialization of Brillinger's conditioning formula. The
directional objects are assembled as `m@W`, `d@(W*W)`, and
`sum_r (U_r^T W)^2`; no candidate n3/n4 cumulant tensor is formed. The exact
binned oracle additionally measures conditional directional c3/c4 from
samples. It agrees with direct unconditional cumulants to max absolute errors
`1.10e-13` (k3) and `4.25e-13` (k4).

Research grounding is recorded in
[`sources/research_conditional_response_factorization_20260806.md`](../../../sources/research_conditional_response_factorization_20260806.md).
Brillinger justifies the total-cumulance identity. Price's theorem motivates
future response-vector factorizations but does not establish this candidate's
accuracy or recurrence.

## Frozen results

| representation | k3 fidelity | k4 fidelity | combined fidelity | correction fidelity | material signs |
|---|---:|---:|---:|---:|---:|
| exact binned identity | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 97/97 |
| full-covariance Gaussian cells | 0.7572 | 0.7956 | 0.7867 | 0.8623 | 93/97 |
| rank-4+diagonal Gaussian cells | 0.7560 | 0.7966 | 0.7872 | 0.8637 | 94/97 |

The frozen gate requires k3, k4, and combined fidelities each at least 0.80.
All three candidate energy checks fail. Material-sign accuracy is 0.9691 and
passes its 0.80 gate, but signs cannot override failed energy gates.

The decisive localization is candidate versus full-covariance Gaussian
closure:

| comparison | fidelity |
|---|---:|
| k3 | 0.99814 |
| k4 | 0.99537 |
| combined standardized | 0.99608 |
| combined correction | 0.99864 |

Thus nearly all error is already present before rank-4 compression. A larger
covariance rank is the wrong mutation.

Per-case k3/k4 fidelities also expose no isolated bad seed:

| n | L | full covariance | rank-4+diagonal |
|---:|---:|---:|---:|
| 8 | 2 | 0.8496 / 0.7940 | 0.8279 / 0.7627 |
| 8 | 3 | 0.7495 / 0.7016 | 0.7360 / 0.6729 |
| 8 | 4 | 0.9362 / 0.8907 | 0.9363 / 0.8913 |
| 12 | 2 | 0.6861 / 0.6731 | 0.6752 / 0.6640 |
| 12 | 3 | 0.6395 / 0.8483 | 0.6388 / 0.8525 |
| 12 | 4 | 0.8010 / 0.7684 | 0.7989 / 0.7718 |
| 16 | 2 | 0.5109 / 0.6367 | 0.5183 / 0.6314 |
| 16 | 3 | 0.7581 / 0.7899 | 0.7664 / 0.8154 |
| 16 | 4 | 0.7629 / 0.8374 | 0.7705 / 0.8453 |

## Convergence and invariance

The prior pair-repeated doubled-sample audit is embedded unchanged in the new
convergence artifact. Re-evaluating this candidate on the same three depth-4
cases with 65,536 base inputs gives rank-4 fidelities `0.8405` (k3), `0.8558`
(k4), `0.8524` (combined), correction fidelity `0.9355`, and 29/30 material
signs. Full covariance is nearly identical. This depth-4-only diagnostic passes
the energy gate, but it cannot change the predeclared nine-case verdict. It is
a useful clue that the conditional residual becomes more Gaussian with depth.

A coordinate permutation of a frozen n=8 case, with corresponding next-weight
row permutation, changes contractions by at most `3.20e-14`; scaled maximum
error is `1.18e-15`. Cell reversal is also invariant. PCA sign and covariance
factor gauges therefore do not create the result.

## State, arithmetic, and unresolved recurrence

At `n=256,B=16,r=4`, stored state is exactly 24,592 float64 values (196,736
bytes). Terminal mean/variance contraction is 6,291,456 multiply-like terms per
layer, about 201.3 million over 32 layers.

The predeclared response target counted 3.959 billion scalar operations. The
post-run structural audit found that this outline omitted dense formation of
`W^T diag(d) W` if a full conditional ReLU covariance is constructed. The
corrected explicit envelope is

```text
B * (2 n^3 + (42 + 8 r) n^2) per layer
= 614,465,536 at n=256,B=16,r=4
= 19,662,897,152 over 32 layers.
```

A 2x implementation/transcendental allowance gives 39,325,794,304, narrowly
below the declared 40B research ceiling. This correction is reported rather
than retroactively editing the predeclared gate.

Arithmetic is not the blocking link. Given Gaussian conditional cells, the
affine/ReLU mean-covariance update can be outlined using rectified univariate
and bivariate Gaussian moments followed by factor compression. But the frozen
screen proves that Gaussian cells omit material residual c3/k4. No bounded-error
ReLU recurrence for those residual cumulants has been derived. Consequently
the deployment gate remains false even if the arithmetic envelope is accepted.

The largest one-case resource audit (`n=16,L=4`, 131,072 paths) measured a
134.0 MiB peak working set and 616.0 MiB peak pagefile allocation including the
NumPy runtime. Largest explicit activation/projection arrays are 16 MiB each;
the candidate forms no dense n3/n4 tensor.

## Mutation inherited by the next rung

Do not increase covariance rank. Add signed low-rank conditional residual
cumulant response factors, for example

```text
kappa3(X|cell) ~= sum_s lambda_s a_s^(x3)
kappa4(X|cell) ~= sum_s eta_s b_s^(x4),
```

so directional contractions become sums of `(a_s^T W)^3` and
`(b_s^T W)^4`. This retains all-distinct cancellations with `O(B R n)` state.
The next rung must predeclare rank, factor discovery, signs, and arithmetic,
then separately falsify the ReLU update. A richer two-scalar conditioning basis
is the alternative mutation, but it must be frozen as a new hypothesis rather
than tuned against this failure.

Artifacts: `PREDECLARED_GATE.md`, `conditional_total.py`, `run_oracle.py`,
`oracle_results.json`, `convergence_audit.json`, `resource_audit.json`,
`structural_audit.json`, `decision.json`, and tests in this directory.
