# Rank-5 k4 tensor-sketch premise report

## Decision: hard kill

The rank-5 factor-column sketch is not a viable k4 closure.  The implemented
CountSketch fails the predeclared 30% selected-k4-contraction error gate by a
wide margin.  More decisively, even the locally optimal, unimplementable
pair-eigen rank-5 ceiling fails the downstream stability gate: a deterministic
public-index-0 transition has correction cosine `-0.999999996` and relative
correction error `25.8799`.

No estimator should be built, promoted, packaged, or officially scored from
this branch.

## Scope and protocol

- Public dataset index: `0` only.
- Network information used: weights only.  Target activation means were never
  read by the runner.
- Small deterministic crops: widths `8`, `12`, and `16`; depth `4`.
- Tested rank: `5` only.
- Transitions: 3 per width, 9 total.
- Random repetitions: 8 deterministic seeds per transition for CountSketch and
  randomized range finding, 72 trials per randomized method.
- Dense oracle: trusted NumPy BASE-k4 propagation with `use_pK=False`.
- Official scorer: not invoked.
- Holdout/private data: not used.

Command:

```powershell
..\..\whest-v014\Scripts\python.exe run_premise.py `
  --dataset ..\..\whest-full `
  --output premise_rank5_results.json `
  --widths 8 12 16 --depth 4 --ranks 5 --seeds 8
```

Elapsed premise time was 26.05 seconds after the one-time partition setup.  The
dense quartic-form cross-check passed at every transition.

## Predeclared gate

The branch had to satisfy all of:

1. selected k4 contraction relative error no greater than 30%;
2. stable downstream correction signs and positive cosine across cases/seeds;
3. projected optimistic rank-5 cost no greater than 50B FLOPs.

The projected transport plus mandatory `(2,1,1)` work is `40.936407040B`
FLOPs.  This is only a lower bound: it excludes sketch construction, factor
generation, Wick work, and the existing k3 parent.

## Aggregate results

| Method | Trials | Mean k4 error | Worst k4 error | Worst k4 sign agreement | Worst correction cosine | Worst correction sign agreement | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| Optimal pair eigen | 9 | 16.83% | 29.80% | 91.67% | -1.0000 | 87.50% | Fail: downstream stability |
| CountSketch | 72 | 49.83% | 115.82% | 62.50% | -1.0000 | 66.67% | Fail: k4 error and stability |
| Randomized pair range | 72 | 16.92% | 32.43% | 91.67% | -1.0000 | 87.50% | Fail: k4 error and stability |

Optimal pair eigen is a favorable local oracle because it minimizes pair-space
Frobenius error after dense materialization.  It is not full-width feasible.
CountSketch is the actual cheap seeded factor-column mutation tested here.
Randomized range finding is an additional small-shape quality oracle whose
naive construction is not cost-feasible.

## Exact ceiling failure

The raw optimal rank-5 k4 contraction only barely clears the numerical cap:
its worst case is `0.298032464` at width 16, transition 0 to 1.  That leaves no
robust error margin as width grows: the exact pair ranks already rise from 36
at width 8, to 78 at width 12, to 136 at width 16.  At width 16, the first two
transitions require ranks 11 and 8 merely to retain 90% of pair spectral energy.

More importantly, raw quartic contraction accuracy is insufficient for the
Edgeworth/ReLU mean.  At width 16, transition 2 to 3, optimal rank 5 has:

- k4 contraction error: `0.150159164`;
- k4 contraction cosine: `0.988816054`;
- downstream correction error: `25.879851917`;
- downstream correction cosine: `-0.999999996`.

The nonlinear `k4`, `k3*k4`, `k4^2`, and `k4^3` polynomial amplifies a modest
contraction perturbation into a direction reversal in the actual correction.
Because this happens for the best rank-5 pair approximation, changing the hash
or sketch seed cannot repair the rank-5 closure premise.

## Implemented sketch failure

CountSketch is not close to the optimistic ceiling.  Across the 72 seeded
trials, selected-k4 error is 49.83% on average and 115.82% in the worst case.
Every width has at least one transition whose mean error exceeds the 30% cap
except width 8 transition 1 to 2, and even that transition has a worst seeded
error of 81.72%.  The worst k4 sign agreement drops to 62.5%.

This is consistent with collision cross terms: signing makes the factor sum
unbiased over hashes, but a rank-5 table is far too small for source pair ranks
36--136.  Averaging more hashes would multiply both storage and contraction
cost and immediately consume the narrow 9.064B lower-bound headroom.

## Reproducibility

- Full result: `premise_rank5_results.json`
- Machine-readable decision: `gate_summary.json`
- SHA-256 of full result:
  `01B90B67B39C5E51B902EDF8E9E4718AA33A8794321DC80F73FEEA8A6863D81C`
- Static/algebraic test suite: 6 tests passed after the premise run.

The hard kill applies specifically to fixed-rank-5 pair-factor k4 closure and
its tested CountSketch/randomized-range mutations.  It does not falsify other
uses of k3 propagation or terminal corrections that avoid recurrent k4 state.
