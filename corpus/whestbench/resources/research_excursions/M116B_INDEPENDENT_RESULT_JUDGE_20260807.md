# M116B independent consumed-result judge — 2026-08-07

## Verdict: KILL — `M116B_B2048_GENERATED_20260807`

The consumed B=2,048 identity failed its frozen absolute L3 residual gate.
This is a clean gate failure, not a harness, source-identity, numerical,
memory, trace, or lifecycle discrepancy. The existing claim permanently
consumes this run ID: **no retry is allowed or recommended**.

## Read-only scope and terminal lifecycle

I read only the frozen manifest/judge, current frozen source/contract, and the
permanent claim/failure/terminal artifacts. I did not invoke a runner or
worker, write or alter a campaign artifact, or create a retry path.

The permanent root contains exactly the expected terminal failure lifecycle:

```text
M116B_B2048_CLAIM.json
M116B_B2048_FAILURE.json
M116B_B2048_TERMINAL.json  -> {"status":"fail"}
```

There is no success result and no pending failure/terminal publication file.
The claim is present, the failure references that exact canonical claim path,
and `retry_allowed` is false in both claim-derived result evidence and frozen
contract. This is the correct no-overwrite/no-retry terminal state.

## Identity and artifact hashes

| Artifact | SHA-256 |
|---|---|
| frozen manifest | `8464f4e6d6a6a47ba5af7f3ee599c9e8aae0866a8d4ce88bdc9333abba829019` |
| campaign contract | `3c8e362177959a91f16d352eaaf3336e0f85af8985b986a7997f91a06457b734` |
| campaign runner | `099ee36fd21d15ea2255828784cce606a4aa125710365f239cd8e18e39ad6775` |
| campaign worker | `19497a13551592725c8329b01e74fe9c4dc92ffc6b86ae18467b26cff21cefe1` |
| cost model | `c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed` |
| in-place L3 operator | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| permanent claim | `dc28bcccd71822e8760bb2168aac9340bcf4b04bceea48071232077e9c5436b1` |
| permanent failure result | `a299f73e8880ae5b52d71d5403b97618aedaed76a988416b4bd4c5e7dc858e3b` |
| permanent terminal | `e7fa2cbc9d5b74a4cae1d748c87ddc7ea4857a8cd1095ad8046e10b1f1267fb1` |

The claim and failure agree on run ID, contract hash, five source hashes, and
the complete pinned runtime identity: Python 3.14.4, NumPy 2.4.6 and frozen
build/initializer hashes, FlopScope `0.10.0+np2.4.6` and initializer hash, and
all four thread variables equal to one. The recorded source hashes equal the
current manifest-bound bytes. There is no source/runtime coherence defect to
repair.

## Independent gate recomputation

I recomputed the gate map directly from `M116B_B2048_FAILURE.json` and the
frozen contract. It exactly equals the persisted map:

| Gate | Result | Evidence |
|---|---|---|
| worker zero failure / finite | pass | worker failure `null`; finite true |
| full prediction trace | pass | 189,738,221,568 bill; 1,024 calls |
| generated microchecks | pass | 512: 47,588,352; 2,048: 188,353,536; one call each |
| shallow parity/alias/suffix/right | pass | relative Frobenius `1.994912574e-6 <= 3e-6` |
| depth-32 parity | pass | relative Frobenius `6.329318763e-6 <= 2e-5`; ReLU mismatch `1.430511475e-6 <= 2e-4` |
| parent/child peak | pass | 186.58203125 MiB `<= 464` MiB |
| prediction wall | pass | 17.7161278001 s `< 20` s |
| **residual** | **fail** | **0.6105131132062525 s `> 0.170` s** |

The full bill also independently recomputes:

```text
32 * 5,912,804,352 hook bill = 189,209,739,264
32 * 64,512 * 256 ReLU bill =     528,482,304
full FlopScope bill           = 189,738,221,568
```

Thus no numerical, trace, peak, or wall gate masks the result: residual is the
one and only failed boolean.

## Meaning of the residual under lambda = 1e11

The frozen policy is absolute L3-only; it contains no direct or L2 timing
comparison and licenses no comparative timing claim. Given the stated wall
exchange `lambda=1e11` flop-equivalents per second:

```text
allowed residual charge  = 1e11 * 0.1700000000000000
                         = 17,000,000,000 flop-equivalents
observed residual charge = 1e11 * 0.6105131132062525
                         = 61,051,311,320.625 flop-equivalents
excess                    = 44,051,311,320.625 flop-equivalents
ratio                     = 3.5912536071x the frozen limit
```

The effective charge is therefore approximately
`189.738221568B + 61.051311321B = 250.789532889B`, versus a residual-gate
ceiling of `206.738221568B` for the same billed work. The B=2,048 operator's
analytical FLOP bill and its 17.716-second prediction wall do not waive this
separately frozen residual constraint.

## Transferable atoms

The result preserves these facts for future, separately audited work:

- capture-before-overwrite in-place L3 operator/liveness discipline;
- generated-only firewall, atomic claim/terminal/no-retry harness pattern;
- exact B=2,048 full trace arithmetic: 32 hooks per layer, 1,024 visible
  hook calls over depth 32, and 189,738,221,568 billed operations including
  in-place ReLUs;
- demonstrated generated numerical parity, finite behavior, and 186.58-MiB
  measured parent/child peak for this exact B=2,048 configuration; and
- the finding that its absolute FlopScope residual is not acceptable.

These are engineering facts only. They do not promote an estimator,
submission, upload, champion replacement, target claim, direct/L2 superiority
claim, or a cost-effective M116 result.

## Descendant boundary

The prior independent M116b audit predeclared one narrow conditional branch:
a **separately named B=4,096 mutation** may be investigated only if B=2,048
later fails its frozen call/residual gate. That condition is now met at the
gate level. It does not prove that call count caused the residual—the campaign
has no per-call decomposition or direct/L2 comparator—but it is sufficient to
open only the stated research branch.

No B=4,096 execution is authorized by this result. A descendant must use a new
run ID, source/contract/manifest/self-seal, generated-only preflight, and
independent audit. It must first obtain a **fresh whole-process peak proof**
under its own geometry and retain the `<=464 MiB` limit; the old static
same-base estimate (445.65625 MiB) is not proof. It must also seal its own
residual/wall/numerical/trace gates. Changing B, a dispatcher, ownership,
thresholds, runtime, or source is a new child, never a retry or amendment of
the consumed B=2,048 campaign.

## Forbidden claims and actions

- Do not retry or rerun `M116B_B2048_GENERATED_20260807`.
- Do not replace its failure terminal ledger, delete its claim, or reuse its
  canonical root.
- Do not call the B=2,048 run cost-effective because its static bill, full
  prediction wall, numerical parity, or peak passed.
- Do not infer direct/L2 timing superiority or causal call-count attribution
  from this absolute-L3-only observation.
- Do not treat B=4,096 as calibrated, peak-cleared, or execution-authorized.
