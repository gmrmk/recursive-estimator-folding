# Latent-factor rank-3 recursive mutation

## Decision

**Hard kill at the predeclared synthetic accuracy gate.**

This was a bounded one-knob child of the screened latent-factor closure. The
retained component count, Gaussian--Hermite order, component compressor,
fallbacks, reference generators, random seeds, and seven synthetic networks
were frozen. The only algorithmic mutation was

```text
q=3, factor rank r=2  ->  q=3, factor rank r=3.
```

Before results, survival required all of:

1. aggregate summed-MSE ratio to full covariance strictly below `0.035`
   (headroom below the `0.04158` target-score floor ratio);
2. rank-three sign-gauge and layerwise neuron-permutation invariance;
3. plausible width-256/depth-32 arithmetic below `40B` operations.

The child produced ratio **0.0602767**, versus **0.0473808** for q3/r2. It is
27.22% worse than its parent and 72.2% above the survival threshold. Exact
invariance and the cost premise pass, but the conjunction fails. No WHest data,
official scorer, holdout, API, or new synthetic network was used.

## Matched seven-case result

The q3/r2 predictions were reproduced bit-for-bit (`max_abs = 0`) against the
stored parent artifact before comparison.

| reference | n | L | seed | q3/r2 MSE | q3/r3 MSE | r3/r2 |
|---|---:|---:|---:|---:|---:|---:|
| tensor GH17 | 4 | 8 | 101 | 5.2308e-5 | 1.4637e-3 | 27.982 |
| tensor GH17 | 4 | 16 | 202 | 1.0585e-4 | 1.4634e-3 | 13.824 |
| tensor GH17 | 4 | 32 | 303 | 6.0368e-13 | 9.6484e-12 | 15.983 |
| exact-forward antithetic MC | 8 | 16 | 401 | 1.6071e-5 | 7.7923e-5 | 4.849 |
| exact-forward antithetic MC | 8 | 32 | 402 | 7.9794e-5 | 5.2093e-5 | 0.653 |
| exact-forward antithetic MC | 16 | 16 | 501 | 2.4235e-3 | 3.0703e-4 | 0.127 |
| exact-forward antithetic MC | 16 | 32 | 502 | 2.2814e-5 | 7.1128e-5 | 3.118 |

Rank three beats full covariance on 7/7 cases but beats q3/r2 on only 2/7.
Those two local wins do not rescue the prespecified aggregate loss.

## Structural result

The rank-three tensor rule has 27 children per parent. The existing
`n=16,L=16,seed=501` case uses all 27 nodes at every component and produces 81
steady children before deterministic reduction back to three components.

The invariance audit reuses two frozen suite members:

- mixed eigenvector-sign gauge: maximum first-two-moment discrepancy
  `4.44e-16`;
- distinct neuron permutations at every layer: maximum output discrepancy
  `7.22e-16`.

All four unit tests pass. The degeneracy/tie fallback remains unchanged from
the parent and therefore preserves the same mathematical equivariance rule.

## Cost accounting

At `n=256,L=32`, q3/r3 has 81 steady children. Using the parent report's dense
eigensolver convention and explicitly charging covariance sandwiches, four
`n^2` moment passes per child, factor shifts, and analytic rectification gives:

| term | arithmetic |
|---|---:|
| covariance sandwiches | 6.442B |
| dense eigensolvers | 19.327B |
| child moment outer products | 0.679B |
| factor shifts + rectification | 0.011B |
| subtotal | 26.460B |
| with 25% contingency | **33.075B** |

This clears the predeclared `<40B` plausibility gate. It is not a FlopScope
bill, so it would not by itself authorize an official screen even if accuracy
had passed.

## Failure interpretation

The evidence rejects the simple monotone hypothesis “retaining one more local
covariance factor improves this q=3 closure.” A likely mechanism is a
resolution/compression mismatch: rank three triples children per parent from 9
to 27, but all 81 steady children are still projected onto one compressor
direction and reduced to only three Gaussian components. The heterogeneous
2/7 wins and 5/7 losses are consistent with additional factor resolution being
aliased differently by that unchanged bottleneck. This is a diagnosis, not a
proof.

Per the recursive-fold rule, do not continue r=4 or retune this child. A future
mutation is justified only if it directly changes the diagnosed compression
bottleneck while preserving a one-mechanism comparison against the surviving
q3/r2 parent.

## Files

- `run_rank3_premise.py`: frozen seven-case comparison and predeclared gate.
- `rank3_results.json`: predictions and per-case/aggregate metrics.
- `test_rank3.py`: rank-three grid, gauge, permutation, and cost guards.
- `structural_audit_rank3.py` / `structural_audit_rank3.json`: machine-readable
  invariance, component-growth, and cost evidence.
- `finalize_decision.py` / `decision.json`: conjunction gate and artifact
  hashes.
