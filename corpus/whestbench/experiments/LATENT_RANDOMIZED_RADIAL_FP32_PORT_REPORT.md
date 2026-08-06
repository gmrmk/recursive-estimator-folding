# FP32 FlopScope port: SURVIVE synthetic production rung

The frozen FP32 FlopScope port survives every preregistered synthetic-only gate. It is executable, deterministic per network, stage-matched to an independent NumPy oracle, under the billed and residual-adjusted cost ceilings, and externally guarded below the resource limits.

This is a validated production-port candidate, not a competition-winning claim. No WHest data, targets, scorer, public row, locked/prohibited row, holdout, or API was touched.

## Frozen operator

- q=3 full-covariance assumed-density closure.
- Two positive chi-radial nodes matching moments zero through three.
- Antipodal points along one Haar frame shared by all components in a layer.
- Exactly one Gaussian `(n,n)` draw and one billed QR per layer.
- Rotation seed is exactly `int(mlp.seed)`. There is no seed bank, seed selection, retry, comparison, hashing, or best-pick.
- Vectorized three-bin cumulative-overlap compressor with no progress loop.
- FP32 state and computation throughout, with scale-relative numerical-rank truncation and explicit billed symmetrization.
- Output shape `(L,n)`; target output `(32,256)`.

The final estimator hash is `0681179273a21d8a5eae98010927186fce1d48397e497c635179c2441c4b656e`. Its final pre-metric freeze is `freeze_manifest_v6.json`, hash `6b25a71230bd56b22bea70ae99a95cf29e5ff8bf56c03591d5e32c5efa954bd8`.

## Parity and correctness

Six unit-test groups pass with zero current failures or errors. Four frozen synthetic networks exercised 200 named internal-stage comparisons against the independent NumPy FP32 oracle. Every comparison passed the frozen `rtol=5e-5`, `atol=5e-6` condition; maximum absolute stage difference was `6.4373e-6`. Large relative errors occurred only where the oracle value was numerically near zero and were covered by the frozen absolute term.

The test matrix verifies:

- direct per-network seed identity and bitwise repeated-run determinism;
- radial moments zero through three;
- pre-means, pre-covariances, eigenvalues, roots, raw/frame Haar matrices, oriented roots, child weights/means, global moments, compressor eigensystem, scores/order, allocation, bin masses, component moments, and final layer means;
- finite, nonnegative `(L,n)` output;
- positive bin masses and no reducer zero-progress path;
- final covariance symmetry and PSD tolerance;
- absence of dataset/scorer imports or disk-load calls.

## Shape and allocation audit

At n=256, layer 1 maps q=1 to 1,024 children; layers 2-32 map q=3 to 3,072 children. The steady tensors are:

| Tensor | Shape |
|---|---:|
| child weights | `(3072,)` |
| child means | `(3072,256)` |
| cumulative-overlap allocation | `(3,3072)` |
| component means | `(3,256)` |
| component covariances | `(3,256,256)` |
| returned layer means | `(32,256)` |

The target run passed every runtime shape assertion. FlopScope observed 64 reshape calls (two per layer), billing 24,737,792 FLOPs; 35 stack calls; and 256 matmul calls. Allocation entries are probability masses, not fractions multiplied by probability again. Target bin masses ranged from `0.33331096` to `0.33333337`.

## Exact billed call audit

| Operation | Required | Observed |
|---|---:|---:|
| `random.Generator.standard_normal` | 32 | 32 |
| `linalg.qr` | 32 | 32 |
| `linalg.eigh` | 64 | 64 |
| moment `einsum` | 64 | 64 |
| `argsort` | 32 | 32 |
| `cumsum` | 32 | 32 |

The dominant billed operations were:

| Operation | Billed FLOPs |
|---|---:|
| `einsum` | 25,425,854,464 |
| `linalg.eigh` | 19,025,362,944 |
| `matmul` | 12,850,407,936 |
| `linalg.qr` | 1,431,655,808 |
| `as_symmetric` | 189,005,664 |

Total billed work was **59,275,963,417 FLOPs**.

## Cost tail and resources

| Quantity | Observed | Gate/margin |
|---|---:|---:|
| billed FLOPs | 59,275,963,417 | 16,724,036,583 below 76B engineering stop |
| backend time | 6.81195 s | reported |
| FlopScope overhead | 1.05635 s | reported |
| residual wall | 0.121467 s | charged at 100B FLOP/s |
| residual-adjusted effective compute | 71,422,682,170.50 | 4,577,317,829.50 below 76B |
| conservative combined tail | 71,422,682,170.50 | 8,577,317,829.50 below hard 80B |
| estimator wall | 7.98977 s | below 600 s |
| guarded end-to-end wall | 11.3723 s | below 600 s |
| external peak working set | 210,595,840 bytes | below 2 GB |
| external peak private bytes | 711,479,296 bytes | reported |

The combined tail is `max(predeclared 70,590,136,320, billed + 100B*residual_seconds)`. The residual-adjusted term dominates but retains 6.02% engineering headroom relative to 76B.

The final covariance minimum eigenvalue divided by its trace scale was `-1.66e-15`, comfortably above the `-2e-5` tolerance. Output was finite and nonnegative.

## Localized failure history

Four failed links were preserved rather than hidden:

1. Implementation 001 amplified a near-null eigenspace beyond stage tolerance. Scale-relative float32 numerical-rank truncation fixed that mechanism.
2. Implementation 002 relied on algebraic symmetry and exceeded FlopScope's tag-validation tolerance by `1.91e-6`. Explicit billed symmetrization fixed it.
3. One PowerShell controller revision failed before launch due duplicate `Path`/`PATH` handling when redirecting output. The estimator was unaffected.
4. The first complete target computation lost its artifact in an invalid Windows memory FFI call; nonce-bound external PID tracking and typed `K32GetProcessMemoryInfo` fixed measurement.
5. The first complete metric artifact had 96 rather than 64 `einsum` calls because a noncontracting outer product used `einsum`. Broadcast multiplication restored the exact declared call graph without changing the mathematical tensor.

The final implementation has zero current failures and retains all previously passing components.

## Decision and boundary

Decision: `survive_fp32_port_synthetic_only`.

This authorizes preserving the FP32 port as the reference implementation for a later mixed-precision mutation. It does not authorize official-row evaluation or claim leaderboard performance. Any next quantization rung must freeze a new mutation and compare against this exact FP32 hash on synthetic units first.
