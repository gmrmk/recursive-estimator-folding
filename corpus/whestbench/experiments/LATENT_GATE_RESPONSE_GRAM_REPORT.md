# H15 end-to-end response-Gram gate

## Decision

**Current end-to-end implementation killed on the frozen materiality gate. The
affordable response-factor operator remains a screened survivor.**

Inserting the exact marginal correction and fixed degree-4 response-Gram
covariance at every child/layer produces the correct directional sign: it beats
corrected full covariance on 8/8 cases and beats both H10 and H12 on 7/8.
However, aggregate MSE ratio is **0.997502340**, versus the required `<=0.80`.
The new covariance changes H12 by only `2.14e-8` in relative aggregate MSE.

No WHest data, scorer, API, new truth, coefficient fit, response gain, degree,
quadrature order, rank, or post-result PSD parameter was used. The child uses
only immutable H10 truths/baselines and H12 comparisons.

## Frozen conjunction

| gate | result | pass |
|---|---:|:---:|
| aggregate ratio to corrected fullcov | **0.997502340** (`<=0.8`) | no |
| wins versus corrected fullcov | 8/8 (`>=6`) | yes |
| frozen permutation relative L2 | `2.81e-16` (`<=1e-10`) | yes |
| frozen positive internal gauge relative L2 | `3.76e-16` (`<=1e-10`) | yes |
| minimum audited child covariance eigenvalue/scale | `4.36e-7` (`>=-1e-10`) | yes |
| PSD safety fallbacks | 0 (`=0`) | yes |
| n256/L32 arithmetic with contingency | **71.494B** (`<80B`) | yes |

The materiality conjunction fails and prevents promotion.

## Sole child operator

For each q3 gate-split child, H15 freezes:

- H10's scalar gate direction, bins, GL64 Gaussian ReLU map, and generic
  compressor;
- H12's exact GL64 within-bin ReLU mean and variance;
- H15's degree-4/order-32 response factor `A^T K A`, with no fitted scale.

The raw child covariance is

```text
C_raw = C_parent
      + diag(v_RB - diag(C_parent))
      + hollow(A^T K A).
```

The low-rank term is represented as one signed rank-four factor plus diagonal
compensation. Thus retaining the exact diagonal does not falsely inflate the
factor rank.

## Frozen PSD safety

Positive-coordinate scaling invariance requires repair in correlation rather
than covariance coordinates. Before accuracy metrics the rule was fixed as:

```text
R_safe = (R_raw + 1e-12 I)/(1+1e-12).
```

A Cholesky check is charged for every child. If it fails, that child falls back
to H12's PSD parent-correlation reconstruction, with the same fixed ridge.
There were zero fallbacks over every layer of all eight cases. The smallest
relative child eigenvalue on the audited n64/L16 witness is positive
`4.36e-7`.

## Eight frozen cases

| L | seed | fullcov MSE | H10 MSE | H12 MSE | H15 MSE | H15 vs H12 |
|---:|---:|---:|---:|---:|---:|:---:|
| 16 | 18560 | 3.68836e-4 | 3.68473e-4 | 3.68473e-4 | 3.68473e-4 | win |
| 16 | 18561 | 8.21096e-4 | 8.19316e-4 | 8.19316e-4 | 8.19316e-4 | win |
| 16 | 18562 | 1.44252e-3 | 1.43348e-3 | 1.43348e-3 | 1.43348e-3 | win |
| 16 | 18563 | 2.08471e-4 | 2.06368e-4 | 2.06368e-4 | 2.06368e-4 | win |
| 32 | 18720 | 3.18339e-4 | 3.16427e-4 | 3.16427e-4 | 3.16427e-4 | win |
| 32 | 18721 | 2.80919e-3 | 2.80908e-3 | 2.80908e-3 | 2.80908e-3 | win |
| 32 | 18722 | 3.00407e-4 | 2.99663e-4 | 2.99663e-4 | 2.99663e-4 | loss |
| 32 | 18723 | 5.99216e-4 | 5.98116e-4 | 5.98116e-4 | 5.98116e-4 | win |

Aggregate sums:

```text
corrected fullcov  0.00686807581499806
H10 gate split     0.00685092225857521
H12 marginal only  0.00685092184097252
H15 response Gram  0.00685092169455935
```

H15/H10 ratio is `0.9999999177`; H15/H12 is `0.9999999786`. Maximum final
prediction change from H12 is only `1.41e-8`.

## Compression-versus-source diagnosis

The response factor is not simply deleted by immediate q3 moment matching.
Across 192 layer/case cells:

- maximum absolute change in the response correction's global covariance norm
  across compression is `8.22e-16`;
- non-null pre/post retention ratio ranges from `0.999922` to `1.000036`, with
  median `1.00000000004`; the deviations occur when subtracting nearly null
  corrections;
- median global response correction is only `9.64e-13` of the marginal-state
  covariance norm; maximum is `4.63e-7`;
- median component-level correction is `1.50e-10` of the marginal component
  covariance norm; maximum is `1.76e-5`.

Therefore the dominant failure boundary is already present before reduction:
one scalar gate statistic couples only a minute fraction of each coordinate's
variance at width 64. The validated local rank-four correction accurately
represents that source, but the source is far too small to deliver a 20% MSE
gain. The compressor preserves global first-two moments, although it can still
discard higher conditional label structure over later recursion.

This reconciles the two prior facts rather than dismissing either:

1. H15 recovered 95% of the banked local conditional-covariance defect.
2. That defect is only `O(1/n)`-coupled to individual neurons and becomes
   materially inert end to end.

## Inherited compressor symmetry boundary

The frozen n64/L16/seed18560 permutation and internal-gauge witnesses pass at
machine precision. A pre-accuracy adversarial n16/L8 probe, however, found
positive-gauge relative error `5.45e-5` when a scale change flips the generic
compressor's component grouping. The response split itself is gauge-covariant;
the discontinuity is in the inherited Euclidean leading-eigenvector grouping.

This does not change the failed materiality verdict, but it prevents claiming
global gauge equivariance for the generic compressor. Any later production
descendant must either certify grouping stability or replace that compressor
with a correlation-coordinate/invariant rule and rerun the full ladder.

## Conservative target arithmetic

| term | arithmetic |
|---|---:|
| H12 subtotal | 55.119B |
| response formation/application beyond H12 diagonal | 0.314B |
| one Cholesky safety check per child | 1.611B |
| correlation-coordinate ridge/congruence | 0.151B |
| subtotal | 57.195B |
| with 25% contingency | **71.494B** |

The cost passes with 8.506B headroom under the 80B analytic-family gate. It is
still a shape-arithmetic model rather than a completed FlopScope port.

## Salvage map and next recursion

Preserved components:

- exact scalar conditioning and marginal Rao--Blackwellization;
- affordable degree-4/order-32 response-vector factors;
- rank-four signed covariance representation;
- downstream sign fidelity from the local spectrum audit;
- PSD-safe correlation-coordinate ridge/fallback;
- exact immediate retention of the global covariance correction through q3
  moment matching.

Failed link in this implementation:

- a **single** conditioning direction generates too little source energy;
  improving its representation from H10 to H15 cannot overcome scalar-to-
  coordinate dilution.

The next meaningful mutation must change that failed link, not retune response
degree, quadrature order, or amplitude. A concrete child is a fixed small bank
of orthogonal gate-susceptibility directions whose degree-4 response factors
are superposed additively without a `q^k` component explosion. Predeclare `k`
from cost, measure captured boundary-target energy before any truth comparison,
and require the aggregate pre-compressor correction to grow materially while
remaining below 80B. If source energy still scales only `k/n`, the bank size
needed for a 20% gain is unaffordable and this route's boundary is quantified.

Separately, a correlation-coordinate compressor should be developed to repair
the inherited global-gauge counterexample. That is a correctness mutation, not
an excuse to rerun this failed one-direction accuracy leaf.

## Artifacts

- `PREDECLARED_GATE.md`: frozen operator, PSD rule, cases, and conjunction.
- `latent_gate_response_gram.py`: end-to-end child, trace, and cost model.
- `run_fresh_n64.py` / `fresh_n64_results.json`: immutable-reference results.
- `structural_audit.py` / `structural_audit.json`: symmetry, PSD, compression,
  adversarial compressor boundary, and cost evidence.
- `test_response_closure.py`: six static/machine guards.
