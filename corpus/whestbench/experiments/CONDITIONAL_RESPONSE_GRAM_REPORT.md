# Degree-4 conditional response-Gram formation

## Decision

**Screened survivor at the frozen representation and cost gate. This is not an
estimator promotion.**

The response-Gram child replaces the parent's unaffordable dense pairwise
conditional-covariance formation with a fixed rank-at-most-four operator built
only from coordinatewise univariate ReLU responses. On the 27 banked exact
cells it achieves:

- **95.0349%** direct aggregate off-diagonal reconstruction;
- Frobenius cosine **0.974878**;
- proxy/target Frobenius norm ratio **0.968654**;
- **95.9161%** material downstream signs, 869/906;
- mean downstream correction cosine **0.933613**;
- positive reconstructed covariance margin, minimum relative eigenvalue
  `1.93e-5`;
- conservative `n=256,L=32,q=3` incremental arithmetic **0.5103B** with 25%
  contingency, including the inherited exact diagonal Rao--Blackwellization.

Both predeclared 80% gates pass. The exact parent cases are reproduced
bit-for-summary: 27/27 identifiers match and the regenerated target's
off-diagonal Frobenius norms differ from the banked values by exactly zero.
The GL96-to-GL128 convergence maximum remains `1.24345e-14`.

No WHest data, scorer, truth, holdout, API, dense target fitting, scalar gain,
or result-dependent basis/rank choice was used.

## Frozen operator

Within one gate-split bin,

```text
Z_i | T=t ~ N(mu_i + c_i t, s_i^2),
g_i(t) = E[relu(Z_i) | T=t].
```

The exact covariance decomposition is

```text
Cov(Y) = E_T[Cov(Y|T)] + Cov_T(E[Y|T]).
```

The child targets the second, Gram-structured term. For standardized
`x=(t-m_bin)/sqrt(v_bin)`, each response is represented in the basis

```text
(1, x, x^2, x^3, x^4).
```

The coefficients are fixed deterministic weighted least squares under an
equal mixture of the exact truncated law and its moment-matched Gaussian, both
at order 32. With `A` the four nonconstant response coefficients and

```text
K = Cov_truncated(x,x^2,x^3,x^4)
  - Cov_gaussian(x,x^2,x^3,x^4),
```

the proposed signed correction is

```text
L = A^T K A.
```

`K` is only 4x4, so `L` has rank at most four and its factors come from a 4x4
eigendecomposition. No n-dimensional eigensolve and no conditional bivariate
ReLU calculation is needed. The deployed representation is

```text
exact residual diagonal + L - diag(L),
```

which is implemented as one signed rank-four factor plus a diagonal
compensation; hollowing the matrix is not falsely counted as rank preserving.

This construction is consistent with the rigorous multivariate form of
[Price's theorem](https://arxiv.org/abs/1710.03576): covariance derivatives of
Gaussian tensor-product nonlinearities can be represented through response
derivatives, including ReLU via distributional derivatives. Price's theorem
motivates the factor basis; it does not establish the empirical 80% claim,
which is supplied only by the frozen synthetic audit. The exact conditioning
identity and research boundary are recorded in
`sources/research_conditional_response_factorization_20260806.md`.

## Aggregate and worst-case audit

| quantity | result | gate |
|---|---:|---:|
| direct off-diagonal reconstruction | **95.0349%** | >=80% |
| factor-space oracle capture | 91.8001% | diagnostic |
| Frobenius cosine | 0.974878 | diagnostic |
| material downstream signs | **95.9161%** | >=80% |
| mean downstream cosine | 0.933613 | diagnostic |
| reconstructed covariance min eigenvalue/scale | `1.93e-5` | >=`-1e-9` |
| arithmetic with contingency | **0.5103B** | <5B |

By width:

| width | direct reconstruction | material signs |
|---:|---:|---:|
| 12 | 91.0467% | 93.0876% |
| 16 | 96.3531% | 96.2838% |
| 24 | 98.9451% | 97.2010% |

By depth snapshot:

| layer | direct reconstruction | material signs |
|---:|---:|---:|
| 1 | 98.5512% | 98.0769% |
| 3 | 96.3630% | 93.1034% |
| 5 | 90.0698% | 96.3816% |

The worst individual direct fraction is 73.04% at `n=24, layer=5, middle
bin`, but that cell's target energy is only `2.69e-25`. The middle bin carries
only `9.18e-8` of total target energy and still achieves 81.25% as an
energy-weighted group. The two material tail bins achieve 94.85% and 95.19%
direct reconstruction.

The global minimum downstream cosine is 0.237 in another nearly null middle-
bin correction (`||delta||_2=5.57e-13`). Across tail bins the minimum cosine is
0.870 and the minimum material sign fraction is 85.7%. Thus the aggregate pass
is not hiding a large-energy reversed correction, while the null middle cells
remain explicitly recorded.

All 27 proxies have numerical factor rank four. The degree-4 response fit has
median relative weighted MSE `1.33e-25` and maximum `1.90e-17`. Therefore the
remaining ~5% covariance energy is not explained by polynomial response-fit
error; it principally marks the omitted difference in
`E_T[Cov(ReLU(Z)|T)]`.

## Symmetry and stability

On the frozen `n=16, seed=27116, layer=3, upper-bin` witness:

- permutation relative Frobenius error: exactly `0`;
- positive-coordinate-scaling relative error: `9.99e-13`;
- factor rank: 4;
- hollow proxy diagonal maximum: exactly `0`.

The common monomial Gram condition number is `1.36e3`. This is not ideal, but
the response fits, symmetry audit, and deterministic quadrature are stable at
float64 in the frozen sweep. A future production implementation may use an
analytically orthogonalized equivalent basis, but changing basis is not needed
to claim this result and must not be outcome-tuned.

## Static target arithmetic

| term | arithmetic |
|---|---:|
| two-law univariate response evaluation | 0.0944B |
| inherited exact GL64 diagonal RB moments | 0.0944B |
| degree-4 polynomial projection | 0.0472B |
| 4x4 factor formation | 0.0024B |
| signed factor reconstruction/application | 0.1699B |
| subtotal | 0.4082B |
| with 25% contingency | **0.5103B** |

This is more than 3,600 times below the parent's literal 1.855T nested
reference formation. It is an arithmetic target, not a completed FlopScope
port; special-function billing and allocation/call overhead remain deployment
work.

## Salvage map and next recursion

Preserved and now operational:

- scalar gate-boundary conditioning;
- exact diagonal marginal Rao--Blackwellization;
- the signed rank-four conditional-correlation target;
- cheap univariate response-vector formation;
- downstream sign transport across two to four layers;
- permutation and positive-gauge covariance.

Residual non-working links:

1. The original gate split's end-to-end effect was only 0.2498% under generic
   Gaussianization and recompression. Passing factor formation does not prove
   that inserting this correction survives the full recursive compressor.
2. About 4.97% aggregate off-diagonal energy remains in the conditional
   covariance expectation rather than the response Gram.
3. The arithmetic model has not been translated to actual billed FlopScope
   calls or wall-time tails.

The next causal child should insert **this frozen response-Gram covariance and
exact diagonal** into the synthetic `latent_gate_split` recursion, retaining
the same q=3 compressor, and compare end-to-end n64 predictions on the already
frozen synthetic cases. Its kill condition should be material improvement over
both the parent gate split and the marginal-only child, with invariance and
actual billed cost checked before any WHest screen. If that recursion washes
out the factors, retain this pass and change only the compressor/label memory;
do not retune degree, order, or gain.

A separate optional child may target the missing 4.97% using a low-order Price-
derivative representation of `E_T[conditional covariance]`, but it should not
delay the end-to-end test because the current representation already clears
both declared gates.

## Artifacts

- `PREDECLARED_GATE.md`: frozen basis, orders, inheritance, and gates.
- `response_gram.py`: univariate response factors, symmetry-preserving proxy,
  subspace diagnostic, and cost model.
- `run_response_gram.py`: exact-target regeneration and downstream comparison.
- `results.json`: all 27 cells, 81 horizon probes, aggregate metrics, hashes.
- `structural_audit.py` / `structural_audit.json`: symmetry/rank/cost witness.
- `test_response_gram.py`: six static and machine-result guards.
