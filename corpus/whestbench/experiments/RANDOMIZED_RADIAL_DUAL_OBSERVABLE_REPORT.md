# Dual-observable randomized-radial q3 compressor

## Decision

**The parameter-free trace-equal dual-observable implementation is killed at
the frozen one-step materiality gate.  Both response channels, their invariant
pullback, and the repaired deep-layer signatures are preserved.**

The runner read no H18 result, truth vector, prediction array, WHest row,
scorer, holdout, API, or leaderboard value.  The randomized-radial parent and
frozen n128 branch were not modified.  The parent hash remains
`150657841fb72b3150e32fe465fb4c24d12c4d11e90df2ce9f1dc22b306215cf`.

## Fixed mutation

H18 isolated a failure of the gate-only geometry on deep covariance.  This
pass kept the 24 parent states, uncompressed one-step oracle, downstream `W`,
signed equal-mass q3 compressor, exact within-bin moments, metrics, and gates.
It changed only the direction metric:

```text
R        = diag(1/sigma) Sigma diag(1/sigma),
F_gate   = diag(phi(alpha)) R diag(phi(alpha)),
F_active = diag(Phi(alpha)) R diag(Phi(alpha)),
F_dual   = F_gate/tr(F_gate) + F_active/tr(F_active).
```

No coefficient was learned or selected.  The unique top eigenvector `v` was
mapped to the variance-one standardized score

```text
T(x) = v^T diag(1/sigma)(xW-mu) / sqrt(v^T R v).
```

The separate even tail score `T(x)^2` was not evaluated or combined.

## Frozen result

| quantity | result | gate |
|---|---:|:---:|
| dual/generic aggregate RMS error | **0.965944** | `<=0.80`, fail |
| relative improvement | **3.406%** | `>=20%`, fail |
| state wins | **17/24** | `>=18/24`, fail |
| mean RMS ratio | `0.941359` | diagnostic |
| covariance RMS ratio | `0.966103` | diagnostic |
| generic covariance energy fraction | `99.348%` | diagnostic |
| maximum source moment relative error | `3.80e-15` | pass |
| minimum normalized covariance eigenvalue | `-3.36e-16` | pass |
| maximum permutation error | `2.90e-13` | pass |
| maximum positive-gauge error | `9.78e-16` | pass |
| spectral ambiguities / collapses | `0 / 0` | pass |
| conservative n256/L32 cost | `71.964B` | `<80B`, pass |

The implementation passes all three unit tests: exact source moments and PSD,
combined monomial input/output covariance, and conservative cost.

The win-count miss is only one state, but it cannot rescue a materiality ratio
that misses its bound by `0.165944`.  No coefficient, channel weight, cutoff,
or case selection was reopened.

## Mean/covariance and layer decomposition

| group | wins | joint ratio | mean ratio | covariance ratio | generic energy share |
|---|---:|---:|---:|---:|---:|
| L16 layer 0 | 4/4 | 0.9591 | 0.9621 | 0.9591 | 47.96% |
| L16 layer 8 | 2/4 | 1.2668 | 1.2361 | 1.2670 | 1.17% |
| L16 layer 14 | 2/4 | 0.9844 | 0.7618 | 0.9862 | 1.23% |
| L32 layer 0 | 4/4 | 0.9636 | 0.9141 | 0.9639 | 48.99% |
| L32 layer 16 | 3/4 | 0.8753 | 0.9056 | 0.8749 | 0.31% |
| L32 layer 30 | 2/4 | 1.0788 | 1.1996 | 1.0775 | 0.33% |

The new active channel changes the failure pattern in the intended direction.
Relative to the preceding gate-only implementation, the dual rule raises wins
from 11 to 17 and moves:

- L16 late from `1.214` to `0.984`;
- L32 middle from `1.181` to `0.875`;
- L32 late from `1.203` to `1.079`.

So the active covariance-response mechanism is real.  It is simply not large
enough when compressed into one trace-averaged scalar direction.

## New causal boundary

The Frobenius cosine between the two response Grams falls strongly with depth:

| group | mean channel cosine | range |
|---|---:|---:|
| L16 layer 0 | 0.751 | 0.667--0.807 |
| L16 layer 8 | 0.338 | 0.200--0.461 |
| L16 layer 14 | 0.246 | 0.167--0.399 |
| L32 layer 0 | 0.721 | 0.657--0.826 |
| L32 layer 16 | 0.187 | 0.069--0.240 |
| L32 layer 30 | 0.147 | 0.052--0.248 |

Early in the network the channels are largely aligned, so their averaged top
direction behaves coherently and wins 8/8.  In the middle and late network the
channels become nearly orthogonal.  A top eigenvector of their trace-equal sum
then forces a one-dimensional compromise:

```text
two distinct deep response geometries
    -> one averaged scalar score
    -> exact global moments but insufficient non-Gaussian partition capacity.
```

This is a narrower failure than "susceptibility does not work."  The response
channels work and repair predicted states; the killed link is their collapse
to one signed scalar q3 geometry.

## Salvage and continuation

Preserved components:

- `F_gate` and `F_active` as separate gauge-invariant response metrics;
- trace normalization as a parameter-free dimensional equalizer;
- the variance-one standardized downstream pullback;
- exact q3 moment conservation, PSD, and unordered sign symmetry;
- channel-cosine and layer-response diagnostics;
- the direct non-Gaussian one-step oracle.

Killed implementation:

- the top eigenvector of the trace-equal sum as the sole signed binning score.

The next recursion must add a mechanism that retains distinct channel
geometry; changing the `1:1` coefficient after seeing this result would not
qualify.  Two clean leaves remain separate:

1. a fixed rank-two response-subspace compressor, but only after a
   permutation/gauge/sign-invariant balanced q3 partition is derived and
   costed; and
2. the already isolated even `T^2` tail partition, tested alone as a
   covariance-amplitude operator on a fresh frozen premise.

They must not be composed until each has its own gate and an interaction test.
An active-only endpoint is also untested, but selecting it on these same 24
states would be post-result channel tuning; any such test needs a fresh
predeclared synthetic split.

## Artifacts

- `PREDECLARED_GATE.md` and `gate_contract.json`: frozen gate.
- `dual_observable_compressor.py`: fixed dual geometry and cost.
- `run_one_step_gate.py`: truth-free runner with mean/covariance and group
  ledgers.
- `one_step_results.json`: authoritative result, SHA256
  `24375ec8355f3609b69b5bf689fb9d9a66f9f959b9c04669b2863d0cad80f2fc`.
- `test_dual_observable_compressor.py`: structural tests.
