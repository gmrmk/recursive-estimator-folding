# Independent COST/LEGALITY judge: FP32 randomized-radial port

## Verdict

**PASS the synthetic production-port cost/legality gate, with a narrow residual-time margin.**

The exact frozen estimator is a valid FlopScope implementation on synthetic weights. It uses FP32 for every floating stage, bills every MLP-dependent numerical operator in `predict`, directly derives its one rotation stream from `mlp.seed` without selection, fits comfortably under the 50 MiB packaging ceiling, and reproduces its exact billed call graph across two target executions.

This verdict does not claim official accuracy or authorize a development/public/locked/prohibited-row run.

## Dtype and call semantics

A separate stage audit found:

| State | Dtype |
|---|---|
| returned `(L,n)` prediction | `float32` |
| final component weights | `float32` |
| final component covariances | `float32` |
| every captured floating internal stage | `float32` |
| sort order | `int64` |

No float64 floating state was observed. Python scalar constants are consumed by FP32 FlopScope arrays without promoting the captured results.

Both target executions billed exactly `59,275,963,417` FLOPs and reported the same required calls:

| Operation | Calls |
|---|---:|
| `random.Generator.standard_normal` | 32 |
| `linalg.qr` | 32 |
| `linalg.eigh` | 64 |
| moment `einsum` | 64 |
| `argsort` | 32 |
| `cumsum` | 32 |

Observed supporting calls include 256 matmuls and 64 reshapes. The first layer uses 1,024 children and the remaining 31 layers use 3,072; the allocation tensors are `(3,1024)` then `(3,3072)`. The overlap values are already probability masses, avoiding accidental squared weights.

The estimator accepts the evaluator's `budget` argument but relies on the enclosing `BudgetContext` for enforcement. The measurement harness used a larger diagnostic ceiling to ensure an over-budget implementation would yield a complete bill; the measured 59.276B is below both the 76B engineering stop and hard 80B target.

## Setup versus billed prediction

`setup` performs only shape-dependent, MLP-independent work:

- derive the two chi-radial constants from `ctx.width`;
- create radial weights and three fixed bin boundaries;
- create the identity covariance for the declared width.

The following all remain inside `predict` under the caller's `BudgetContext`:

- seed-dependent Gaussian draws and all 32 QR factorizations;
- every weight-dependent mean/covariance propagation;
- covariance eigendecompositions and roots;
- child construction and ReLU;
- global and bin moment contractions;
- compressor eigensystems, score sort, cumulative allocation, symmetrization, and returned means.

No weight, Jacobian, route, frame, covariance, prediction, or other MLP-dependent result is moved to `setup`. Python debug dictionaries/lists are also created during `predict`; their time is not hidden—it contributes to residual wall.

## Seed legality

The rotation rule is exactly:

```text
rotation_seed = int(mlp.seed)
one default_rng(rotation_seed)
one sequential Gaussian matrix and QR per layer
```

There is no seed bank, hash-to-bank mapping, retry, score comparison, or best-pick. Repeated predictions for the same network are bitwise identical in the frozen tests. The Haar stream is shared across q components within a layer as declared.

This is legally clean but remains an accuracy-transfer risk: the earlier n=64/n=128 screen averaged four independent frozen rotations, while production uses one network-seeded draw. Haar distributional reasoning supports the change, but official finite-row performance has not been measured.

## Residual-tail reproducibility

| Metric | Frozen guarded run | Independent judge rerun |
|---|---:|---:|
| billed FLOPs | 59,275,963,417 | 59,275,963,417 |
| backend time | 6.81195 s | 4.67461 s |
| FlopScope overhead | 1.05635 s | 0.83261 s |
| residual wall | 0.121467 s | 0.102662 s |
| billed + `100B*residual` | 71.4227B | 69.5422B |
| conservative tail after 70.5901B floor | 71.4227B | 70.5901B |
| estimator wall | 7.98977 s | 5.60989 s |
| process peak working set | 210,595,840 B | 209,375,232 B |

The exact billed graph reproduced. Residual variation was 18.81 ms, equivalent to 1.881B effective FLOPs at the frozen rate. The maximum observed conservative tail is 71.423B, leaving 4.577B—or only 45.77 ms of additional residual time—below the 76B engineering stop. This passes, but it is not abundant headroom. Server load, backend changes, warnings, or extra Python routing could erase it.

The guarded run tracked a nonce-matched worker PID externally and measured 210.6 MB peak working set, 711.5 MB peak private bytes, and 11.37 s end-to-end wall, all below the 2 GB/600 s limits.

## Package constraint

- `estimator.py`: 11,711 bytes.
- Entire current port directory, including reports/results/caches: 188,110 bytes at audit time.
- Limit: 52,428,800 bytes.

The estimator uses only evaluator-provided `flopscope` and `whestbench` plus the Python standard library; it requires no model or frame asset. Packaging is a clear pass even if the full audit directory were mistakenly included, though a real submission should contain only the required estimator files.

## Development-row judgment

A single rule-permitted development/public row is now **scientifically justified as the next rung**, because:

- the mathematical child survived fresh n=64 and n=128 synthetic screens;
- the FP32 port matches an independent NumPy oracle at every named stage;
- the target cost, exact calls, residual tail, RSS, wall, determinism, PSD, and source-legality gates pass;
- no official accuracy datum has yet influenced the implementation.

It is **not currently authorized by this audit**. Before running it, preserve estimator hash `0681179273a21d8a5eae98010927186fce1d48397e497c635179c2441c4b656e`, confirm that the competition permits the chosen development row, and obtain explicit parent authorization. The run should be exactly preregistered and must not trigger seed selection or post-hoc mutation on a locked/holdout result.

Locked, prohibited, private, or untouched holdout rows remain unjustified and forbidden.

## Final judge disposition

`pass_fp32_cost_legality_synthetic_only_development_row_conditionally_justified_not_authorized`
