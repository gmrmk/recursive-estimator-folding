# Multi-direction susceptibility response bank

## Decision

**Current finite-k additive bank killed before truth. The invariant direction
construction and response/cancellation measurements are preserved.**

This pass produced an important false positive and then resolved it without
touching truth:

1. Summing only the degree-4 response factors appeared to amplify H15's source
   by tens of thousands of times at affordable cost.
2. Exact conditioning theory shows that factor is only one side of a
   cancellation. A Gaussian split into exact truncated conditional laws,
   passed through ReLU, and recombined must reproduce the unsplit Gaussian
   ReLU moments.
3. Once every direction includes its Gaussianized q3 split, exact marginal
   correction, response factor, and recombination, each additional direction
   costs 29.664B before contingency. Only k=1 remains under 80B.
4. The admissible top-susceptibility replacement triggers five frozen PSD
   fallbacks in 24 states, violating the predeclared zero-fallback gate.

No truth, prediction array, WHest data, scorer, API, fitted gain, or best-
direction selection was read or used.

## Invariant direction construction

For a Gaussian closure state `(mu,C)`, define

```text
sigma_i = sqrt(C_ii)
alpha_i = mu_i/sigma_i
g_i     = phi(alpha_i)/sigma_i
F       = diag(g) C diag(g).
```

If coordinates are positively rescaled by `D`, `g -> D^-1 g` and
`C -> D C D`, hence `F` is invariant. Under a permutation, it transforms by
similarity. From `F v_s=lambda_s v_s`, define

```text
a_s = diag(g) v_s / sqrt(lambda_s),
T_s = a_s^T (Z-mu).
```

Then `a_s^T C a_t=delta_st`; the coefficients transform contravariantly and
the covariance loadings transform covariantly. Direction sign is harmless
because the three equal-probability bins are summed.

Across the frozen cells, maximum C-orthogonality error is `1.27e-10`, minimum
selected relative eigengap is `1.64e-7`, and there are zero spectral
ambiguities. The k16 factor-only source has permutation and positive-gauge
relative errors `1.95e-14` and `2.41e-14`.

## The factor-only false positive

The initially frozen additive object was

```text
P_s = sum_b p_b hollow(A_sb^T K_b A_sb).
```

All factor-only k values fit the naive arithmetic envelope:

| k | arithmetic with 25% contingency |
|---:|---:|
| 1 | 71.494B |
| 2 | 71.886B |
| 4 | 72.671B |
| 8 | 74.240B |
| 16 | 77.379B |

Against H15's original factor source, the aggregate factor-only results were:

| k | Frobenius RMS amplification | nuclear amplification | PSD fallbacks |
|---:|---:|---:|---:|
| 1 | 25,741x | 75,611x | 0 |
| 2 | 33,374x | 122,526x | 0 |
| 4 | 41,401x | 178,330x | 1 |
| 8 | 53,225x | 240,923x | 1 |
| 16 | 66,949x | 291,820x | 1 |

Those numbers are numerically reproducible but causally incomplete. `P_s`
corrects the moment-matched Gaussian bin approximation; without including that
same direction's bin approximation, adding `P_s` to the unsplit parent injects
the cancellation term as if it were signal.

The raw factor-only file `premise_results.json` is retained as negative
evidence about cancellation scale. It is not a surviving estimator premise.

## Complete partition audit

The corrected source is

```text
S_s = Cov(corrected q3 children for direction s)
    - Cov(unsplit Gaussian ReLU state).
```

It includes the GL64 bivariate child maps, exact GL64 marginals, degree-4
response factor, fixed correlation ridge, PSD fallback, and mixture
recombination. Exact integration would give `S_s=0`; measured `S_s` is an
explicit biased closure residual.

### Cost

| k | complete arithmetic with 25% contingency | admissible |
|---:|---:|:---:|
| 1 | **71.494B** | yes |
| 2 | 108.573B | no |
| 4 | 182.732B | no |
| 8 | 331.049B | no |
| 16 | 627.684B | no |

Each additional complete direction costs 29.664B before contingency. Growth is
linear rather than `q^k`, but the three bivariate GL64 maps per direction are
already fatal.

### Frozen k1 replacement

Only the top susceptibility direction is complete-cost admissible:

| quantity | result | gate |
|---|---:|:---:|
| Frobenius RMS amplification over original direction | 35,404x | pass |
| nuclear amplification | 50,598x | pass |
| spectral ambiguities | 0 | pass |
| permutation relative error | `9.85e-13` | pass |
| positive-gauge relative error | `1.55e-12` | pass |
| PSD fallbacks | **5/24 states** | **fail** |

The original-direction net source has median Frobenius norm `8.73e-12`; the
top-susceptibility closure residual has median `3.43e-3`. Five fallbacks occur
at `(L,seed,layer)` equal to `(16,18560,15)`, `(32,18720,31)`,
`(32,18721,16)`, `(32,18721,31)`, and `(32,18723,31)`.

The corrected net/raw response-factor norm ratio has median `0.143`, range
`0.0685` to `1.136`: typically about 86% of the apparently huge response factor
is canceled by the rest of its own partition. Mean recombination residual is at
most `4.97e-15`, independently confirming the exact mean identity.

The remaining large covariance residual is not a certified network cumulant.
It is the approximation error left by omitting part of the exact conditional
bivariate covariance, and its PSD failures are consistent with that diagnosis.
The frozen conjunction therefore prevents a tempting but unsupported truth
screen.

## What failed and what survives

Killed implementation:

- finite-k additive response factors without their partition terms are
  causally incomplete;
- complete k>=2 partitions exceed budget;
- the only admissible complete replacement direction fails PSD stability in
  five states.

Preserved components:

- the permutation/positive-gauge invariant susceptibility Gram;
- C-orthonormal bank construction and spectral-gap checks;
- degree-4 univariate response factors;
- exact factor/source overlap, eigenvalue coverage, and interaction ledgers;
- the Gaussian partition cancellation identity as a new design constraint;
- fixed correlation-coordinate PSD safety.

The next viable mutation must replace the 29.664B-per-direction missing term:
derive a cheap, PSD-guaranteed low-rank representation of

```text
E_T[Cov(ReLU(Z)|T)]_truncated
- E_S[Cov(ReLU(Z)|S)]_matched-Gaussian.
```

Price-derivative or separable pair-kernel factors are appropriate candidates.
They must be tested against exact small-width conditional bivariate quadrature,
including cancellation, before the large factor-only magnitudes can be treated
as source. If such a term costs below roughly 0.5B per added direction, k16 can
re-enter the 80B envelope; otherwise this bank remains structurally correct but
computationally closed.

The inherited generic compressor's n16 gauge-grouping error `5.45e-5` remains
documented and unchanged. It neither caused nor rescues this kill.

## Artifacts

- `PREDECLARED_GATE.md`: original factor-bank premise.
- `premise_results.json`: factor-only magnitude/overlap diagnostic; explicitly
  not authoritative for survival.
- `NET_SOURCE_GATE.md`: corrected complete-source premise, frozen before its
  metrics.
- `multidirection_gate_response.py`: invariant bank, factor source, complete
  partition identity, PSD audit, overlap, and both cost models.
- `run_source_premise.py`: factor-only truth-free audit.
- `run_net_source_premise.py` / `net_source_results.json`: authoritative
  complete-source verdict.
- `test_multidirection.py`: seven algebra, symmetry, identity, cost, and
  decision guards.
