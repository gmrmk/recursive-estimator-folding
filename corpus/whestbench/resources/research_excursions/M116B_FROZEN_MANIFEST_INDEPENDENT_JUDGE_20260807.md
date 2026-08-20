# M116B frozen-manifest independent judge — 2026-08-07

## Verdict: PASS_TO_EXECUTE

The frozen harness is internally consistent and is authorized for exactly one
later generated-only campaign invocation. This is a pass of the **harness
freeze**, not an assertion that the unexecuted full numerical, trace, peak,
wall, or residual gates will pass.

I did not execute the campaign, call its owner-token entry point, or create
the canonical root. It was absent before and after this review:

```text
work/scorefloor_generation/m116b_inplace_l3_draft/
M116B_B2048_GENERATED_CAMPAIGN
```

## Frozen identity reconciliation

The manifest SHA-256 is exactly the requested value:

```text
8464f4e6d6a6a47ba5af7f3ee599c9e8aae0866a8d4ce88bdc9333abba829019
```

Every manifest-bound source byte matches:

| File | SHA-256 |
|---|---|
| `campaign_contract.json` | `3c8e362177959a91f16d352eaaf3336e0f85af8985b986a7997f91a06457b734` |
| `campaign_runner.py` | `099ee36fd21d15ea2255828784cce606a4aa125710365f239cd8e18e39ad6775` |
| `campaign_worker.py` | `19497a13551592725c8329b01e74fe9c4dc92ffc6b86ae18467b26cff21cefe1` |
| `cost_model.py` | `c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed` |
| `inplace_l3.py` | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| `test_campaign_harness.py` | `dd7729722b47cbef9cd0a5239568bb9f594d42ae91436eaf353392d0f2863c57` |
| `test_inplace_l3.py` | `25bf60c70e33fc4f0419f31dabe8f92d3154387c9a0893744ccbb8a851a98d0e` |

The runner's normalized self-seal recomputes to
`05d516630d7e70b3c077e5ebe17d0542cdb4e0a2f80ed10766200d287370d21d`.
The runner's literal contract hash, contract's expected runner seal, and
manifest's two self-seal fields all agree. The runner verifies source and
runtime identity before claiming the root; the worker repeats both checks and
authenticates itself from the just-created claim hash.

## Contract, scope, and gate reconciliation

The manifest and contract exactly agree on run ID, geometry, seeds, all shared
numeric gates, runtime values, thread environment, canonical root, and
no-retry scope:

```text
tile=256; block_rows=2048; full_rows=64512; shallow_rows=3072
depth_rows=512; depth=32; dtype=float32

micro seeds=116762,118298; shallow=116207; depth32=116320
full_prediction=11664512
```

The full trace is mechanically derived as 32 hooks at
`5,912,804,352` billed flops and 32 matmul calls each, plus 32 in-place ReLUs:

```text
32 * 5,912,804,352 + 32 * 64,512 * 256 = 189,738,221,568
matmul calls = 32 * 32 = 1,024
```

The policy value `absolute_l3_only_no_direct_or_l2_comparator` is the sole
schema placement difference: it is a manifest `gates` annotation and contract
`protocol` field. It matches exactly; it is not a discrepancy. The manifest
also correctly prohibits retries, submission/upload, and champion replacement.

## Runtime reconciliation

Under the frozen four-variable one-thread environment, the runner's live
runtime verifier passed against the contract:

- Python: `work/whest-v014/Scripts/python.exe`, version `3.14.4`, executable
  SHA-256 `4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262`.
- NumPy `2.4.6`, initializer SHA-256
  `65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4`,
  build fingerprint
  `fb5905933699a015e02a1e6254a9fc5aadc4a81f4ed03878632d09370684d1e0`.
- FlopScope `0.10.0+np2.4.6`, initializer SHA-256
  `f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06`.
- `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, and
  `NUMEXPR_NUM_THREADS` all equal `1`.

## Audit-evidence reconciliation

All six manifest-bound reports exist and hash exactly to the frozen values.
Their sequence is coherent: the early build pass is limited to a campaign
build; the original harness report is explicitly superseded; the first hostile
campaign audit records the two defects; the repair report addresses them; and
the second independent audit returns `PASS_TO_FREEZE` while reserving full
observation for the one shot.

| Report | SHA-256 |
|---|---|
| `M116B_INPLACE_STREAMED_L3_IMPLEMENTATION_20260807.md` | `396302c171622e89ed5b0bd9a57fcd46a2daea04bd07f786f598a90324634c23` |
| `M116B_INDEPENDENT_PREEXEC_AUDIT_20260807.md` | `c3f09fc493ab4884d75c6d0908757154f78688a9c8e02459ce7a420eb905db0d` |
| `M116B_B2048_GENERATED_CAMPAIGN_HARNESS_20260807.md` | `5bb834a7ef0471532f36756c24c60303e453a28b49762f28e757a2ec2c5f407a` |
| `M116B_CAMPAIGN_INDEPENDENT_PREEXEC_AUDIT_20260807.md` | `862cf09d6d1d5e72ea23a2b3cfdf30c8bafb054835fd4fa641481cccdf2d93e2` |
| `M116B_B2048_GENERATED_CAMPAIGN_HARNESS_REPAIR_20260807.md` | `f4f1734e5df2c96582cb9797e6319ccfdc3e3f020d3790eabaf0f1283296782b` |
| `M116B_SECOND_INDEPENDENT_PREEXEC_AUDIT_20260807.md` | `818896e50ebf16870998f0cfaf50997be26cb9f98f99b5ef42b81069e0353741` |

## Source/static validation

Only noncanonical target-free checks ran:

```text
test_inplace_l3:       11 passed
test_campaign_harness: 15 passed
```

They must run separately by design. The operator suite begins with an
un-pinned trace and asserts fail-closed behavior before locally injecting the
thread pins; the harness suite validates the live pinned runtime. Harness
lifecycle tests use temporary roots and mocked/bounded workers. The real
canonical root remained absent.

## What remains unobserved

No claim is that the following gates pass. They can be observed only during
the authorized one shot and must be written to its terminal result/failure
ledger:

- actual full 64,512-row/depth-32 FlopScope trace (`189,738,221,568` bill and
  `1,024` calls);
- generated micro, shallow, and depth-32 numerical/relu-mismatch gates;
- parent/child lifetime peak working set `<=464 MiB`;
- full prediction wall `<20 s` and absolute L3 residual `<=0.170 s`.

Failure of any of these gates is terminal for this run ID. It neither authorizes
a retry nor any submission, upload, target access, or champion action.

## Exact single authorized invocation — not executed here

Only after a user-authorized final preflight again confirms the root is absent,
the above manifest/source/audit hashes still match, the frozen runtime and all
four thread pins are present, and the scope remains generated-only/no-retry,
the single executable call is:

```powershell
Push-Location 'work\scorefloor_generation\m116b_inplace_l3_draft'
$env:OPENBLAS_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'; $env:NUMEXPR_NUM_THREADS='1'
& 'C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\whest-v014\Scripts\python.exe' -c "import campaign_runner as r; r.run_authorized_generated_campaign(r.EXECUTION_TOKEN)"
Pop-Location
```

`campaign_runner.py` has no runnable CLI; this owner-token call is the sole
path able to claim the fixed root. It was **not** invoked in this audit.

