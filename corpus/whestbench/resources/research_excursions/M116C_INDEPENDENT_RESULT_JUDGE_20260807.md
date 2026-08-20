# M116c independent consumed-result judge — 2026-08-07

## Verdict: KILL — `M116C_B4096_GENERATED_20260807`

The consumed M116c identity failed its frozen absolute L3 residual gate. This is a clean terminal gate failure: all eight other recorded gates independently recompute as passes. It is not a source, runtime, trace, numerical, peak, wall, or lifecycle discrepancy. This report grants no submission, retry, mutation, B=8192, or other successor-execution authority.

## Read-only scope and permanent lifecycle

I did not invoke the runner or worker, write a campaign artifact, modify a source/release, or create a retry path. The fixed canonical root is a direct path (not a symlink) and contains exactly:

```text
M116C_B4096_CLAIM.json
M116C_B4096_FAILURE.json
M116C_B4096_TERMINAL.json  -> {"status":"fail"}
```

There is no result-success artifact or pending terminal artifact. The failure references the exact canonical claim path, claim/failure/contract agree on run ID `M116C_B4096_GENERATED_20260807`, and the claim's execution-release hash equals the failure's release hash. The frozen contract and failure record both declare `retry_allowed: false`. The runner's lifecycle source also opens a claim with `O_CREAT|O_EXCL` and rejects an existing claim or terminal file. The root is therefore permanently consumed; it must not be reused or amended.

## Identity and artifact hashes

| Artifact | SHA-256 |
|---|---|
| execution release | `ec1431ac6669c9ede19486a13eec139bd9598e1535dbca4f9dc5c83b5c584a6d` |
| campaign contract | `f289cd0ca1e81273cd45398e3b6d827d946197db989a8db638318665ede09ebf` |
| campaign runner (raw installed source) | `27f3d59b24f7d21918a2b3a85a0ec879a0d89bb80b9d3fbbe021dbd66efe8d4a` |
| campaign worker | `bdc6d2a6666c65a370d68f43a743458e8a811ac8cd0ec57a3a3f7704571e6d56` |
| cost model | `ee1d0dc3f9f15239cc7561c6437545c5c316f8148d9b70060217488428c6a2e3` |
| in-place L3 operator | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| permanent claim | `4dd867f7bd339d2a360f60c2afd94c287cb1568d78df2c6b0a203517d8c5f1e9` |
| permanent failure result | `5cb46ff45e9f4c28576261f1c76419385c88b054e444c742e1f48f224eca40f8` |
| permanent terminal | `e7fa2cbc9d5b74a4cae1d748c87ddc7ea4857a8cd1095ad8046e10b1f1267fb1` |

The failure record embeds the actual contract/release/source hashes above and the exact pinned runtime identity. The installed release also binds normalized runner hash `66bbda5c7d5fe69551dc897e730e3ee4fc3e2dd677d314888387a27181737c2c`, protocol identity `c2fa4f35bacf4b8f37f9755d62b0eb927eb2d7aa09eaa76f5082d6f8bfff1246`, and runtime identity `c7ee40a1ea4556b3dfc8617a91dbc176955bd03b9abcb9b4216e9533495214f7`.

## Independent gate and bill recomputation

I recomputed each predicate directly from the current failure record and current sealed contract. The resulting map exactly equals the persisted map.

| Gate | Result | Independent evidence |
|---|---|---|
| zero failure and finiteness | pass | worker `failure: null`; worker, shallow, depth-32, and both microchecks finite |
| full prediction trace | pass | 512 visible hook calls; 189,738,221,568 billed FLOPs |
| generated microchecks | pass | 512 and 4,096 rows; one core/matmul call each; preservation checks true |
| shallow parity/alias/suffix/right | pass | relative Frobenius `1.9988572976e-6 <= 3e-6` |
| depth-32 parity | pass | relative Frobenius `6.9171657064e-6 <= 2e-5`; ReLU mismatch `1.6689300537e-6 <= 2e-4` |
| parent/child peak | pass | 205.109375 MiB (215,072,768 bytes) `<= 464` MiB; parent and child reported the same peak |
| prediction wall | pass | 17.2983878001 s `< 20` s |
| **residual** | **fail** | **0.3284645767416805 s `> 0.170` s** |

The full bill recomputes from the sealed values:

```text
32 * 5,912,804,352 hook bill = 189,209,739,264
32 * 64,512 * 256 ReLU bill =     528,482,304
full FlopScope bill          = 189,738,221,568
```

With the frozen `lambda = 1e11` flop-equivalents/second wall exchange:

```text
allowed residual charge  = 17,000,000,000.000 flop-equivalents
observed residual charge = 32,846,457,674.168 flop-equivalents
excess                   = 15,846,457,674.168 flop-equivalents
ratio                    = 1.9321445691x the frozen limit
effective observed bill  = 222.584679242B
effective gate ceiling   = 206.738221568B
```

The absolute L3-only residual gate is separately binding; passing the arithmetic bill, numerical trace, peak, and prediction wall cannot waive it.

## Comparison with consumed M116b: descriptive only

The two permanently recorded campaigns have the same full billed FLOPs but different visible full-prediction call counts and residuals:

| Campaign | Calls | Residual seconds |
|---|---:|---:|
| M116b B=2,048 | 1,024 | `0.6105131132062525` |
| M116c B=4,096 | 512 | `0.3284645767416805` |

M116c is lower by `0.2820485364645720` s: `0.5380139585x` M116b's residual (a 46.19860415% reduction). A two-point affine description, `residual_s = 0.04641604027710855 + 0.0005508760477823671 * calls`, interpolates those two observations. At 256 calls it would predict `0.18744030850939453` s, still above the 0.170-s gate; the line crosses the gate at approximately 224.34 calls.

This is not a causal attribution to call count and not a calibration rule: the data comprise only two separately sealed campaigns and have no per-call residual decomposition or direct/L2 comparator. In particular, it does **not** authorize B=8192, a different block geometry, a threshold change, further tuning, or any execution.

## Transferable atoms

The following are preserved engineering evidence only, for future separately specified and independently authorized research:

- generated-only, fixed-runtime, atomic claim/failure/terminal harness pattern;
- capture-before-overwrite in-place L3 operator and its source identity;
- exact M116c depth-32 finite/parity trace and full bill of 189,738,221,568 FLOPs with 512 visible hooks;
- measured 205.109375-MiB parent/child peak and 17.2983878001-s prediction wall for this exact consumed configuration; and
- the empirical two-point observation that halving visible hooks coincided with lower residual while still failing the frozen absolute residual gate.

These facts do not promote an estimator, submission, upload, champion, replacement, cost-effective result, direct/L2 comparison, or successor run.

## Forbidden descendants and actions

- Do not retry, rerun, overwrite, delete, or reuse `M116C_B4096_GENERATED_20260807` or its canonical root.
- Do not claim M116c passed, was cost-effective, or can be rescued by its successful numerical/trace/peak/wall gates.
- Do not infer that call count caused the improvement or that the affine line predicts a real configuration.
- Do not launch or pre-authorize B=8192, an alternate B, a runtime/source change, a dispatcher change, a residual-threshold change, or more tuning as a descendant of this consumed identity.
- Any future research proposal must start as a new, separately reviewed specification and must earn independent execution authority; this report supplies none.

