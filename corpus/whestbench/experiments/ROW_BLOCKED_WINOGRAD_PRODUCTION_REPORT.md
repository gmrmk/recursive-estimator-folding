# Production 8192-row Winograd fold: validated public-100 child

Date: 2026-08-06

## Decision

**Promote `random32256_rowwinograd8192` as the validated local child of
`random32256`.**  It passes every frozen no-truth engineering/package gate and
every frozen paired public-100 score gate.  It is packaged but unsubmitted.
This establishes a stronger local candidate, not a guaranteed private-suite or
competition win.

The causal result is unusually clean: the estimator's sample geometry and
mathematics are unchanged, float32 reassociation changes raw MSE by only
`-0.001704%` in aggregate, and exact billed-compute compression reduces the
official adjusted score by `5.99524%`.

## Official public-100 result

The child was run once by WHestBench 0.14's subprocess runner on the only
authorized score units: already-touched public full-split indices 0..99, seed
0, budget 272B.  It was compared to the immutable cached official parent
artifact for the same 100 MLPs.  Source hashes were checked before and after
the run and remained identical.

| measurement | parent `random32256` | child | child/parent |
|---|---:|---:|---:|
| raw final MSE | `3.089512726e-7` | `3.089460087e-7` | `0.999982962` |
| adjusted score | `2.257079776e-7` | `2.121762464e-7` | `0.940047616` |
| mean effective C | `202.281790B` | `189.852556B` | `0.938554853` |
| mean analytical FLOPs | `185.406853B` | `173.794058B` | `0.937365882` |
| max effective C | `250.488783B` | `222.405357B` | -- |
| mean residual | `0.168749 s` | `0.160585 s` | `0.951618` |
| mean whole predict wall | `2.246593 s` | `2.867496 s` | `1.276375` |
| failures | `0/100` | `0/100` | -- |

The score law was reconstructed from every per-network record as
`MSE * max(0.1, C/272B)` with exactly zero numerical discrepancy for both
branches.  This is a true paired score comparison, not a product of aggregate
ratios.

## Paired inference and tails

The child wins all `100/100` networks.  A frozen one-million-resample paired
network-cluster bootstrap (seed 20260806) gives:

```text
mean child-parent score       -1.353173126e-8
95% CI for mean difference   [-1.562576754e-8, -1.166233571e-8]
95% CI for ratio of means     [0.936501313, 0.943475999]
P(bootstrap mean diff < 0)     1.0
```

Per-network score ratios have minimum/median/maximum
`0.862199 / 0.941218 / 0.982518`; even the weakest observed network improves
by 1.75%.  Effective-compute ratios are
`0.862226 / 0.941166 / 0.982458`.  MSE ratios are tightly centered at one:
minimum/median/maximum `0.999723 / 0.999976 / 1.000251`.

Every child network remains below the 258.4B safety gate; its worst observed C
is 222.405B, leaving 49.595B below the official 272B cliff.  Every paired child
C is lower than its parent's by 3.445B to 34.511B.

## Mechanism

The immutable parent's two sample-path products are routed through a
shape-only dispatcher.  Eligible even products use exact one-level Batched-B
Winograd arithmetic.  Seven right operands are packed once; consecutive even
row blocks of at most 8192 use bounded seven-left/seven-product scratch; results
are reconstructed directly into the full output.  Odd contracted widths stay
direct and odd output widths use one direct tail.

The arithmetic bill is linear in row count except for the right pack, which is
performed once.  Row blocking therefore preserves the unsplit reduced bill.
At representative full geometry the production port reproduced:

```text
parent analytical FLOPs       170.530655499B
child analytical FLOPs        159.492745546B
exact saving                   11.037909953B
operator workspace             91.4375 MiB
process peak                  474.8594 MiB
```

The public suite's exact mean analytical saving is 11.612795B.  Whole predict
wall time is 27.6% higher because row streaming fragments large products into
more backend calls.  WHest's score excludes backend time and FlopScope overhead
from residual time, and actual residual C still declined.  The slower backend
wall remains the principal deployment-stability risk; it is disclosed rather
than treated as universally free.

## Gate A: no truth

Before opening any score, the production source passed:

- four inherited modules byte-identical to the parent package;
- exactly seven declared runtime modules and no network/subprocess imports;
- 131,072 exhaustive shape-bill checks and 96,768 row-partition checks, with
  zero mismatch and no selected bill above direct;
- full synthetic relative parity `4.28216e-8`, maximum delta `1.49812e-6`;
- depth-32 relative error `2.48581e-6` and one gate mismatch in 4,194,304;
- synthetic effective-C ratio `0.937363`;
- setup `0.632 s`, predict `4.198 s`, peak working set `474.859 MiB`;
- WHest estimator validation, five operator unit tests, and final package
  validation.

The original 667.328 MiB full-height implementation's failed liveness link is
therefore repaired by fixed row blocking without discarding the exact
Winograd, dispatcher, or bill-proof components.

## Preserved negative evidence

Two infrastructure failures were localized and retained:

1. Pointing the WHest folder packager at a single file generated a manifest
   lacking sibling imports.  Repointing the same packager at the frozen source
   directory fixed packaging without changing estimator code.
2. The first tool wrapper used a 10-second outer timeout for the multi-minute
   score harness and terminated before any JSON or stderr byte was produced.
   The corrected wrapper changed only its outer timeout; the same hash-frozen
   scorer run then completed once in 540.0 seconds.

Neither failure was silently retuned into the estimator, and neither generated
a score used for selection.

## Artifact and firewall

Validated archive:
`submission_random32256_rowwinograd8192_20260806.tar.gz`

SHA-256:
`bc2ec39558c76a67b12b587ca4ee70bb1e8921489643d83707e052d086e8ae36`

Archive contents are exactly seven Python runtime modules plus the generated
manifest.  No dataset, truth, result, credential, binary payload, external
asset, network dependency, API call, login, upload, or submission is present.
No locked row 600..799 or prohibited row >=800 was accessed.

## Recursive-fold disposition

- **Promoted mechanism:** exact row-blocked Winograd sample products.
- **Preserved parent components:** random32,256 geometry, Haar frames,
  antipodes, pilot rescue, fold3, moment tangent, seeds, and float32 path.
- **Resolved link:** full-height temporary liveness/memory.
- **Remaining risk:** backend call fragmentation and private-run timing drift.
- **Next legal test:** independent package/runtime audit and, if the campaign
  policy permits, an untouched validation split.  Do not tune from public
  0..99 again and do not claim a guaranteed private winner from this result.
