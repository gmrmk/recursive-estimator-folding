# M156 native compiler audit

## Decision

**PASS for the isolated five-product compiler; no efficacy credit.**

The collision-mask obstruction in M155 is not fundamental.  Moving the mask
from the deterministic control into the full-support residual domain converts
the masked Khatri--Rao action into five ordinary dense products.  Seven
small-width tests prove algebraic parity, conservation, collision ownership,
proposal mass, permutation covariance, and positive-gauge covariance.

## Fresh-process trace

All inputs were generated matrices.  No response, truth, scorer, competition
row, network API, leaderboard, submission, or champion state was read.

| run | bill | residual seconds | combined effective | 5x hostile | hostile margin |
|---:|---:|---:|---:|---:|---:|
| 0 | 10,426,269,184 | 0.005956504 | 97.002798340B | 99.385399765B | 0.614600235B |
| 1 | 10,426,269,184 | 0.006383699 | 97.045517920B | 99.598997666B | 0.401002334B |
| 2 | 10,426,269,184 | 0.005618798 | 96.969027746B | 99.216546792B | 0.783453208B |
| 3 | 10,426,269,184 | 0.006120397 | 97.019187708B | 99.467346606B | 0.532653394B |
| 4 | 10,426,269,184 | 0.005724094 | 96.979557348B | 99.269194806B | 0.730805194B |

Every run made exactly `5 * 31 = 155` matmul calls, had no exception, and
returned finite `aaaa`, `aaab`, and `aabb` slots.  Hot arrays were allocated
outside the billed region and reused through `out=`.

## Scope boundary

The trace establishes only that the complete-domain covariance-star compiler
fits.  The following remain closed:

1. bind `V` to a covariance already owned by the base analytic state, or trace
   any new provider inside the smallest 5x margin of 0.401002334B;
2. include complete-domain proposal bookkeeping without changing K=128;
3. bind the generic exact distinct-label endpoint provider;
4. run the frozen response-free source variance and p99 gate.

The K=128 residual already owns 128 feature evaluations per layer.  Replacing
its distinct-only draw by a complete-domain draw does not increase that count,
and collision rows skip the trivariate coefficient call.  This sharing remains
a logical upper bound until an integrated trace proves it.

## Recursive disposition

Promote the **domain-lift identity and compiler** as reusable mechanisms.
Do not promote an estimator.  If residual variance fails, preserve the domain
lift and mutate only the control coefficient or covariance provenance.

